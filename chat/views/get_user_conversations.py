from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_gpt_system_prompt import get_gpt_chat_system_prompt
from chat.serializers import ConversationSerializer
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

import logging

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='get',
    operation_description="Get all conversations for the current user",
    operation_id="Get all conversations for the current user",
    operation_summary="Get all conversations for the current user",
    manual_parameters=[
        openapi.Parameter(
            'language',
            openapi.IN_QUERY,
            description="Filter conversations by the bot's language",
            type=openapi.TYPE_STRING,
            default='ENG'
        )
    ],
    responses={
        "200": openapi.Response(
            description="Conversations gathered successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Conversations gathered successfully",
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
        )
    }
)
@api_view(['GET'])
def get_user_conversations(request):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Get the language query parameter, default to 'ENG'
    language = request.query_params.get('language', 'ENG')

    # Get all conversations for the user
    conversations = Conversation.objects.filter(userEmail=email, bot__language=language).select_related('bot')
    
    serializer = ConversationSerializer(conversations, many=True)
    
    logger.info("Conversations gathered successfully for user: %s", email)
    
    return generate_success_response("Conversations gathered successfully", serializer.data)