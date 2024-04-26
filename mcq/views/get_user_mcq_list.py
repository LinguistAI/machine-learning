from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_prompt import get_chat_prompt
from chat.serializers import ConversationSerializer
from constants.header_constants import HEADER_USER_EMAIL
from mcq.models import MCTTest
from mcq.serializers import MCTTestHiddenAnswerSerializer, MCTTestSerializer
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
                            "id": "Test ID",
                            "email": "User's email",
                            "conversation": {
                                "id": "Conversation ID",
                                "createdAt": "2021-08-30 14:00:00",
                                "updatedAt": "2021-08-30 14:00:00",
                                "...": "..."
                            },
                            "questions": [
                                {
                                    "id": "Question ID",
                                    "email": "User's email",
                                    "word": "Word",
                                    "question": "Question",
                                    "answer": "Correct answer",
                                    "options": [
                                        "Randomized Option 1", 
                                        "Randomized Option 2", 
                                        "Randomized Option 3", 
                                        "Randomized Option 4",
                                    ],
                                    "createdAt": "2021-08-30 14:00:00",
                                    "updatedAt": "2021-08-30 14:00:00",
                                    "isUserCorrect": False,
                                    "hasUserAnswered": False
                                }
                            ],
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
                            ],
                            "createdAt": "2021-08-30 14:00:00",
                            "updatedAt": "2021-08-30 14:00:00",
                            "isCompleted": True,
                            "correctPercentage": 80.00,
                            "startedAt": "2021-08-30 14:00:00",
                            "completedAt": "2021-08-30 14:02:32",
                            "elapsedSeconds": 120.31413
                        }
                    ]
                }
            }
        )
    }
)
@api_view(['GET'])
def get_user_mcq_list(request):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Get all conversations for the user
    completed_tests = MCTTest.objects.filter(email=email, isCompleted=True).order_by('-createdAt')
    
    completed_serializer = MCTTestSerializer(completed_tests, many=True)
    
    non_completed_tests = MCTTest.objects.filter(email=email, isCompleted=False).order_by('-createdAt')
    
    non_completed_serializer = MCTTestHiddenAnswerSerializer(non_completed_tests, many=True)
    
    # Get the union
    all_data = completed_serializer.data + non_completed_serializer.data
    
    logger.info("MCQ Tests gathered successfully for user: %s", email)
    
    return generate_success_response("Tests gathered successfully", all_data)