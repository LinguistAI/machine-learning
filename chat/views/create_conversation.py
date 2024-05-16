from django.http import HttpRequest
from rest_framework.decorators import api_view
from chat.models import ChatBot, Conversation
from chat.serializers import ConversationSerializer
from chat.tasks.update_unknown_words import update_unknown_words
from constants.header_constants import HEADER_USER_EMAIL

from feature_flags.check_existing_features import check_existing_features
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema
from concurrent.futures import ThreadPoolExecutor


from drf_yasg import openapi

from utils.utils import is_valid_uuid

import logging

logger = logging.getLogger(__name__)



_executor = ThreadPoolExecutor()


def handle_future_exception(future, future_name: str):
    try:
        # This will re-raise any exception that was caught during the execution of the task.
        future.result()
    except Exception as e:
        logger.error(f"An error occurred during future {future_name}")
        logger.error(future.exception())


def handle_unknown_words_future_exception(future):
    handle_future_exception(future, "unknown_words")
    

def handle_check_existing_features_future_exception(future):
    handle_future_exception(future, "check_existing_features")


@swagger_auto_schema(
    method='post',
    operation_description="Create a conversation",
    operation_id="Create a conversation",
    operation_summary="Create a conversation",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'botId': openapi.Schema(type=openapi.TYPE_STRING, description="Bot ID")
        }
    ),
    responses={
        "200": openapi.Response(
            description="Conversation generated successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Conversation generated successfully",
                    "data": [
                        {
                            "id": "6ca7f806-a054-4b78-848b-0bf9da1885e2",
                            "createdDate": "2024-04-18T09:29:36.556201Z",
                            "updatedDate": "2024-04-18T09:42:47.071779Z",
                            "userEmail": "mehmet_dogu123@hotmail.com",
                            "title": "Albert Einstein",
                            "lastMessage": "Hello, how are you?",
                            "bot": {
                                "id": "37ed45c3-e029-4769-b5de-03ded8a5abdf",
                                "createdDate": "2024-02-26T21:45:49.031000Z",
                                "updatedDate": "2024-02-26T22:00:14.073000Z",
                                "name": "Albert Einstein",
                                "description": "Albert Einstein, the iconic theoretical physicist known for his intelligence and wit, now serves as a mentor in the world of language learning. With his wild hair and kind eyes, he explains complex ideas in simple, relatable terms, inspiring learners to explore the universe of languages with curiosity and perseverance.",
                                "profileImage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Albert_Einstein_1947.jpg/1200px-Albert_Einstein_1947.jpg",
                                "voiceCharacteristics": "istebububu",
                                "difficultyLevel": 50
                            },
                            "unknownWords": [
                                {
                                    "id": "d278ba68-8d01-46a5-8e42-a23b79bfecde",
                                    "listId": "0165ea1d-54f4-4b52-9578-2cdc86b7ec9b",
                                    "email": "mehmet_dogu123@hotmail.com",
                                    "createdDate": "2024-04-18T09:42:46.986405Z",
                                    "updatedDate": "2024-04-18T09:42:46.995996Z",
                                    "word": "clean",
                                    "isActive": True,
                                    "confidenceLevel": 1.0
                                },
                                {
                                    "id": "5d4abaaf-80d7-4aef-88f5-9bbc949785da",
                                    "listId": "0165ea1d-54f4-4b52-9578-2cdc86b7ec9b",
                                    "email": "mehmet_dogu123@hotmail.com",
                                    "createdDate": "2024-04-18T09:42:47.032461Z",
                                    "updatedDate": "2024-04-18T09:42:47.034285Z",
                                    "word": "strategy",
                                    "isActive": True,
                                    "confidenceLevel": 1.0
                                },
                                {
                                    "id": "dc90fb08-9649-4166-98e7-75cd6400a20d",
                                    "listId": "0165ea1d-54f4-4b52-9578-2cdc86b7ec9b",
                                    "email": "mehmet_dogu123@hotmail.com",
                                    "createdDate": "2024-04-18T09:42:47.043687Z",
                                    "updatedDate": "2024-04-18T09:42:47.044963Z",
                                    "word": "application",
                                    "isActive": True,
                                    "confidenceLevel": 1.0
                                },
                                {
                                    "id": "3f4b7fee-ca45-4efc-9bb6-6a7209996b01",
                                    "listId": "0165ea1d-54f4-4b52-9578-2cdc86b7ec9b",
                                    "email": "mehmet_dogu123@hotmail.com",
                                    "createdDate": "2024-04-18T09:42:47.053654Z",
                                    "updatedDate": "2024-04-18T09:42:47.055037Z",
                                    "word": "school",
                                    "isActive": True,
                                    "confidenceLevel": 1.0
                                },
                                {
                                    "id": "45f9e2fc-449c-4acf-9885-5a0c54e00c9a",
                                    "listId": "0165ea1d-54f4-4b52-9578-2cdc86b7ec9b",
                                    "email": "mehmet_dogu123@hotmail.com",
                                    "createdDate": "2024-04-18T09:42:47.063605Z",
                                    "updatedDate": "2024-04-18T09:42:47.064992Z",
                                    "word": "work",
                                    "isActive": True,
                                    "confidenceLevel": 1.0
                                }
                            ]
                        }
                    ]
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
        )
    }
)
@api_view(['POST'])
def create_conversation(request: HttpRequest):

    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")

    if not request.data or "botId" not in request.data:
        return generate_error_response(400, "Bot selection is required")

    bot_id = request.data.get("botId")
    if not bot_id:
        return generate_error_response(400, "Bot selection is required")

    # Check if bot_id is valid uuid4
    is_valid_uuid4 = is_valid_uuid(bot_id, version=4)

    if not is_valid_uuid4:
        return generate_error_response(400, "Invalid bot ID")

    bot_exists = ChatBot.objects.filter(id=bot_id).exists()

    if not bot_exists:
        return generate_error_response(400, "Bot not found")

    bot = ChatBot.objects.filter(id=bot_id).first()

    user_conversations_exists = Conversation.objects.filter(
        userEmail=email, bot=bot).exists()

    if user_conversations_exists:
        return generate_error_response(400, "A conversation already exists with this bot")

    bot = ChatBot.objects.filter(id=bot_id).first()

    title = bot.name

    conversation = Conversation.objects.create(
        userEmail=email, bot=bot, title=title)
    
    # logger.info("Updating unknown words for conversation {}".format(conversation.id))
    # future_unknown_words = _executor.submit(update_unknown_words, conversation.id, email)
    # future_unknown_words.add_done_callback(handle_unknown_words_future_exception)
    # logger.info("Unknown words updated for conversation {}".format(conversation.id))
    
    logger.info("Checking existing features for {}".format(email))
    future_existing_features = _executor.submit(check_existing_features, email)
    future_existing_features.add_done_callback(handle_check_existing_features_future_exception)
    logger.info("Existing features checked for {}".format(email))

    serializer = ConversationSerializer(conversation)

    return generate_success_response("Conversation created successfully", serializer.data)
