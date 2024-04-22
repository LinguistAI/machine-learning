from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_prompt import get_chat_prompt
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

@swagger_auto_schema(
    method="post",
    operation_description="Clear all messages from a conversation",
    operation_id="Clear all messages from a conversation",
    operation_summary="Clear all messages from a conversation",
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
            description="Conversation messages cleared successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Conversation messages cleared successfully",
                    "data": [
                        {
                            "id": "6ca7f806-a054-4b78-848b-0bf9da1885e2",
                            "createdDate": "2024-04-18T09:29:36.556201Z",
                            "updatedDate": "2024-04-18T09:42:47.071779Z",
                            "userEmail": "mehmet_dogu123@hotmail.com",
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
        ),
        "404": openapi.Response(
            description="Not found",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 404,
                    "msg": "Conversation does not exist"
                }
            }
        ),
    }
)
@api_view(['POST'])
def clear_conversation(request, conversation_id: str):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    if not conversation_id:
        return generate_error_response(400, "Conversation ID is required")
    
    # Get the conversation id that matches the email if exists
    conversation_exists = Conversation.objects.filter(id=conversation_id).exists()
    
    # Now get the last five messages from the conversations
    if not conversation_exists:
        return generate_error_response(404, "Conversation does not exist")
    
    conversation = Conversation.objects.filter(id=conversation_id).first()
    
    messages = Message.objects.filter(conversation=conversation).all()
    
    messages.delete()
    
    conversation = Conversation.objects.filter(id=conversation_id).first()
    
    serializer = ConversationSerializer(conversation)
    
    return generate_success_response("Conversation messages cleared successfully", serializer.data)
