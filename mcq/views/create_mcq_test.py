import json
import time
from django.utils import timezone
from rest_framework.decorators import api_view
from chat.models import Conversation, UnknownWord
from constants.header_constants import HEADER_USER_EMAIL
from constants.unknown_word_constants import ACTIVE_WORD_LIST_SIZE, MCQ_TEST_QUESTION_PER_WORD
from mcq.models import MCTQuestion, MCTTest

from mcq.serializers import MCTTestHiddenAnswerSerializer
from mcq.tasks.create_mcq_question import create_mcq_question
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi


# Create Django Rest Endpoint that returns a list of messages for a given conversation
@swagger_auto_schema(
    method='post',
    operation_description="Create a multiple choice question test",
    operation_id="create_mcq_test",
    operation_summary="Create a multiple choice question test",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'conversationId': openapi.Schema(type=openapi.TYPE_STRING, description="Conversation ID")
        }
    ),
    responses={
        "200": openapi.Response(
            description="Multiple choice question test generated successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Multiple choice question test generated successfully",
                    "data": {
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
                        "isCompleted": False,
                        "correctPercentage": 0.0,
                        "startedAt": "2021-08-30 14:00:00",
                        "completedAt": None,
                        "elapsedSeconds": 0.0
                    }
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
                    "msg": "Conversation not found"
                }
            }
        )
    }
    
)
@api_view(['POST'])
def create_mcq_test(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Check request data for message
    if not request.data or "conversationId" not in request.data:
        return generate_error_response(400, "Conversation ID is required")

    # Get message from request body
    conversationId = request.data.get("conversationId")
    if not conversationId:
        return generate_error_response(400, "Conversation ID is required")

    conversation_exists = Conversation.objects.filter(id=conversationId).exists()
    
    if not conversation_exists:
        return generate_error_response(404, "Conversation not found")
    
    conversation = Conversation.objects.get(id=conversationId)
    
    unknown_words: list[UnknownWord] = conversation.unknownWords.all()

    
    if not unknown_words or unknown_words.count() < ACTIVE_WORD_LIST_SIZE:
        return generate_error_response(404, "You need to chat a bit more before starting a multiple choice test")
    
    
    test = MCTTest.objects.create(
        conversation=conversation,
        email=email
    )
    
    for unknown_word_obj in unknown_words:
        for _ in range(MCQ_TEST_QUESTION_PER_WORD):
            json_response = create_mcq_question(unknown_word_obj.word)
            
            # JSON Response is as follows
    #         {
    # "question": "Write the sentence with the blank, indicating where the input word should fit."
    # "options": [
    # "Incorrect Option 1",
    # "Incorrect Option 2",
    # "Incorrect Option 3"
    # ],
    # "answer": "Correct Answer (Input Word)"
    # }
            # Create MCTQuestion object
            # Add the answer to options while creating question object
            question = MCTQuestion.objects.create(
                email=email,
                word=unknown_word_obj.word,
                question=json_response["question"],
                answer=json_response["answer"].lower(),
                option1={"label": json_response["options"][0].lower(), "isEliminated": False},
                option2={"label": json_response["options"][1].lower(), "isEliminated": False},
                option3={"label": json_response["options"][2].lower(), "isEliminated": False},
                option4={"label": json_response["answer"].lower(), "isEliminated": False},
            )
            question.randomize_options()
            test.questions.add(question)
            question.save()
    
    
    test.unknownWords.set(unknown_words)
    test.startedAt = timezone.now()
    test.save()
    
    test_serializer = MCTTestHiddenAnswerSerializer(test)
    
    return generate_success_response("Multiple choice question test generated successfully", test_serializer.data)
    