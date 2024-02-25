from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_prompt import get_chat_prompt
from constants.header_constants import HEADER_USER_EMAIL
from profiling.models import Profile
from profiling.tasks.update_profile import update_profile_async

from utils.http_utils import generate_error_response, generate_success_response
from utils.gemini_utils import gemini_model
from drf_yasg.utils import swagger_auto_schema
import time
from constants.profile_constants import MAX_NO_OF_MESSAGE_CONTEXT
from concurrent.futures import ThreadPoolExecutor


from drf_yasg import openapi

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
    
    print(f"User message: {message}")
    
    # Get the conversation id that matches the email if exists
    conversation_exists = Conversation.objects.filter(id=conversation_id).exists()
    
    print(f"Conversation exists: {conversation_exists}")
        
    # Now get the last five messages from the conversations
    if not conversation_exists:
        return generate_error_response(400, "Conversation does not exist")
    
    conversation = Conversation.objects.filter(user_email=email).first()
    message_count = Message.objects.filter(conversation=conversation).count()
    previous_messages = Message.objects.filter(conversation=conversation).order_by('+created_date')[:MAX_NO_OF_MESSAGE_CONTEXT]
    
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
    
    chat_prompt = get_chat_prompt(bot_profile, previous_messages_str, profile, message)
    
    print(chat_prompt)
    
    # Log gemini response time
    start_time = time.time()
    response = gemini_model.generate_content(chat_prompt)
    end_time = time.time()
    
    # TODO: Add better logging
    print(f"Time taken to generate Gemini response: {end_time - start_time}")
    
    print("Gemini response: ", response)
    print("Prompt feedback: ", response.prompt_feedback)
    data = response.text

    # Add message to conversation
    user_message = Message.objects.create(conversation=conversation, message_text=message, sender_email=email, sender_type="user")
    user_message.save()
    
    bot_message = Message.objects.create(conversation=conversation, message_text=data, sender_email="bot", sender_type="bot")
    bot_message.save()
    
    # async call to update profile
    if message_count > MAX_NO_OF_MESSAGE_CONTEXT:
        executor = ThreadPoolExecutor()
        executor.submit(update_profile_async, profile, previous_messages_str, data)
    
    return generate_success_response("Chat response generated successfully", data)