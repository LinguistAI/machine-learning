from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message, UnknownWord
from chat.prompts.chat_gpt_system_prompt import get_gpt_chat_system_prompt
from chat.prompts.spanish_chat_gpt_system_prompt import get_spanish_gpt_chat_system_prompt
from chat.prompts.turkish_chat_gpt_system_prompt import get_turkish_gpt_chat_system_prompt
from chat.prompts.german_chat_gpt_system_prompt import get_german_gpt_chat_system_prompt
from chat.prompts.italian_chat_gpt_system_prompt import get_italian_gpt_chat_system_prompt
from chat.prompts.french_chat_gpt_system_prompt import get_french_gpt_chat_system_prompt
from chat.prompts.korean_chat_gpt_system_prompt import get_korean_gpt_chat_system_prompt
from chat.tasks.update_quest_on_chat import update_quest_on_chat
from chat.tasks.update_unknown_words import update_unknown_words
from chat.tasks.update_xp_on_chat import update_xp_on_chat
from constants.header_constants import HEADER_USER_EMAIL
from feature_flags.models import FeatureCategory, UserFeature
from profiling.models import Profile
from profiling.tasks.update_profile import update_profile_async

from scoring.tasks.score_user_prompt import score_user_prompt
from utils.http_utils import generate_error_response, generate_success_response
from utils.gemini_utils import chat_model
from drf_yasg.utils import swagger_auto_schema
import time
from constants.profile_constants import MAX_NO_OF_MESSAGE_CONTEXT
from concurrent.futures import ThreadPoolExecutor
from utils.chatgpt_utils import generate_gpt_chat_response


from drf_yasg import openapi

import logging

logger = logging.getLogger(__name__)



def handle_future_exception(future, future_name: str):
    try:
        future.result()  # This will re-raise any exception that was caught during the execution of the task.
    except Exception as e:
        logger.error(f"An error occurred during future {future_name}")
        logger.error(future.exception())



# Create a global _executor
_executor = ThreadPoolExecutor(max_workers=5)

def handle_profile_future_exception(future):
    handle_future_exception(future, "profile")

def handle_xp_future_exception(future):
    handle_future_exception(future, "xp")

def handle_quest_future_exception(future):
    handle_future_exception(future, "quest")

def handle_unknown_words_future_exception(future):
    handle_future_exception(future, "unknown_words")

def handle_scoring_future_exception(future):
    handle_future_exception(future, "scoring")

@swagger_auto_schema(
    method='post',
    operation_description="Generate a response to a chat message",
    operation_id="Generate a response to a chat message",
    operation_summary="Generate a response to a chat message",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description="User message")
        }
    ),
    # ADd url parameter

    manual_parameters=[
        openapi.Parameter(
            name='conversation_id', in_=openapi.IN_PATH,
            description='Unique identifier for the chat session',
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        "200": openapi.Response(
            description="Chat response generated successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Chat response generated successfully",
                    "data": "Bot response here..."
                }
            }
        ),
        "400": openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 400,
                    "msg": "Authentication is required"
                }
            }
        ),
        "400": openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 400,
                    "msg": "Message is required"
                }
            }
        )
    }
)
@api_view(['POST'])
def generate_chat_response(request, conversation_id: str):

    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")

    # Check the request body for message
    if not request.data or "message" not in request.data:
        return generate_error_response(400, "Message is required")

    # Check the request body for message
    message = request.data.get("message")
    if not message:
        return generate_error_response(400, "Message is required")

    if not conversation_id:
        return generate_error_response(400, "Conversation ID is required")

    logger.info(f"Generating chat response for {email} in conversation {conversation_id}")

    # Get the conversation id that matches the email if exists
    conversation_exists = Conversation.objects.filter(id=conversation_id).exists()

    # Now get the last five messages from the conversations
    if not conversation_exists:
        logger.error(f"Conversation does not exist for {conversation_id}")
        return generate_error_response(400, "Conversation does not exist")

    conversation = Conversation.objects.filter(id=conversation_id).first()
    message_count = Message.objects.filter(conversation=conversation).count()
    previous_messages = Message.objects.filter(conversation=conversation).order_by('-createdDate')[:MAX_NO_OF_MESSAGE_CONTEXT]

    # Reverse the previous messages
    previous_messages = previous_messages[::-1]

    # Get conversation unknown words
    unknown_words: list[UnknownWord] = conversation.unknownWords.all()

    unknown_words_list = [word.word for word in unknown_words]

    # If unknown words do not exist, update them by sending a async request to the unknown words endpoint
    if conversation.update_words:
        unknown_words_list = None
        logger.info("Attempting to update words for {} conversation".format(conversation_id))
        future_unknown_words = _executor.submit(update_unknown_words, conversation_id, email)
        future_unknown_words.add_done_callback(handle_unknown_words_future_exception)
    else:
        logger.info("Unknown words exist for {} conversation".format(conversation_id))

    # Get user profile if exists
    profile_exists = Profile.objects.filter(email=email).exists()

    if profile_exists:
        profile = Profile.objects.filter(email=email).first()
    else:
        profile = Profile.objects.create(email=email)
        profile.save()

    previous_messages_str = [str(message) for message in previous_messages]
    previous_messages_str = "\n".join(previous_messages_str)

    conversation_bot = conversation.bot
    bot_profile = conversation_bot.prompt
    bot_difficulty = conversation_bot.difficultyLevel
    system_prompt = ''

    if conversation_bot.language == 'ENG':
        system_prompt = get_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)
    elif conversation_bot.language == 'ESP':
        system_prompt = get_spanish_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)
    elif conversation_bot.language == 'TUR':
        system_prompt = get_turkish_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)
    elif conversation_bot.language == 'GER':
        system_prompt = get_german_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)
    elif conversation_bot.language == 'ITA':
        system_prompt = get_italian_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)
    elif conversation_bot.language == 'FRA':
        system_prompt = get_french_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)
    elif conversation_bot.language == 'KOR':
        system_prompt = get_korean_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)
    else:
        system_prompt = get_gpt_chat_system_prompt(bot_profile, bot_difficulty, profile, unknown_words_list)

    # logger.info(f"Chat prompt generated for conversation {conversation_id}: {chat_prompt}")
    chat_model_feature_exists = FeatureCategory.objects.filter(name="ChatModel").exists()
    user_features = UserFeature.objects.filter(email=email)
    
    chat_model = "gpt-4o"
    
    # Get UserFeature object for ChatModel
    if chat_model_feature_exists:
        for user_feature in user_features:
            if user_feature.feature.category.name == "ChatModel":
                chat_model = user_feature.feature.name
                break
        
    # Log gemini response time
    start_time = time.time()
    response = generate_gpt_chat_response(system_prompt, previous_messages, chat_model, message)
    end_time = time.time()

    logger.info(f"Time taken to generate ChatGPT response for conversation {conversation_id}: {end_time - start_time}")

    logger.info("ChatGPT Chat response is " + response)

    data = response

    if data:
        conversation.lastMessage = data
        conversation.save()

    # Add message to conversation
    user_message = Message.objects.create(conversation=conversation, messageText=message, senderEmail=email, senderType="user")
    user_message.save()

    bot_message = Message.objects.create(conversation=conversation, messageText=data, senderEmail="bot", senderType="bot")
    bot_message.save()

    # Update profile if needed
    if message_count % MAX_NO_OF_MESSAGE_CONTEXT == 0:
        last_user_messages = Message.objects.filter(conversation=conversation, senderType="user").order_by('-createdDate')[:MAX_NO_OF_MESSAGE_CONTEXT]
        last_user_messages = last_user_messages[::-1]
        last_user_messages_str = [str(message) for message in last_user_messages]
        last_user_messages_str = "\n".join(last_user_messages_str)
        logger.info("Profile _executor for conversation {} executing".format(conversation_id))
        future_profile = _executor.submit(update_profile_async, profile, last_user_messages_str, data)
        future_profile.add_done_callback(handle_profile_future_exception)
        logger.info("Profile _executor for conversation {} executed".format(conversation_id))

    logger.info("XP _executor for conversation {} executing".format(conversation_id))
    future_xp = _executor.submit(update_xp_on_chat, email)
    future_xp.add_done_callback(handle_xp_future_exception)
    logger.info("XP _executor for conversation {} executed".format(conversation_id))

    logger.info("Quest _executor for conversation {} executing".format(conversation_id))
    future_quest = _executor.submit(update_quest_on_chat, email, message)
    future_quest.add_done_callback(handle_quest_future_exception)
    logger.info("Quest _executor for conversation {} executed".format(conversation_id))

    logger.info("Scoring _executor for conversation {} executing".format(conversation_id))
    future_scoring = _executor.submit(score_user_prompt, email, unknown_words, message)
    future_scoring.add_done_callback(handle_scoring_future_exception)
    logger.info("Scoring _executor for conversation {} executed".format(conversation_id))


    return generate_success_response("Chat response generated successfully", data)

