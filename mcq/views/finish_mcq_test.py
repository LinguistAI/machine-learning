from concurrent.futures import ThreadPoolExecutor
from rest_framework.decorators import api_view
from chat.models import Conversation, UnknownWord
from constants.header_constants import HEADER_USER_EMAIL
from constants.unknown_word_constants import CONFIDENCE_LEVEL_SCALING_FACTOR, DECREASE_CONFIDENCE_ON_WRONG_MCQ_ANSWER, INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER
from mcq.models import MCTQuestion, MCTTest

from mcq.serializers import MCTTestSerializer
from mcq.tasks.alter_word_confidence import decrease_word_confidence, increase_word_confidence
from mcq.tasks.request_decrease_confidence_backend import request_decrease_confidence_backend
from mcq.tasks.request_increase_confidence_backend import request_increase_confidence_backend
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema
from math import floor
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Finish a multiple choice question test",
    operation_id="finish_mcq_test",
    operation_summary="Finish a multiple choice question test",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'testId': openapi.Schema(type=openapi.TYPE_STRING, description="Test ID")
        }
    ),
    responses={
        "200": openapi.Response(
            description="Test completed successfully",
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
                    }
                }
            }
        ),
        "400": openapi.Response(
            description="Bad request",
            extra="All questions must be answered before completing the test",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 400,
                    "msg": "All questions must be answered before completing the test"
                }
            }
        ),
        "404": openapi.Response(
            description="Not found",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 404,
                    "msg": "Test not found"
                }
            }
        )
    }
    
)
@api_view(['POST'])
def finish_mcq_test(request):
    
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Check request data for message
    if not request.data or "testId" not in request.data:
        return generate_error_response(400, "Test ID is required")

    # Get message from request body
    testId = request.data.get("testId")
    if not testId:
        return generate_error_response(400, "Test ID is required")
    
    test_exists = MCTTest.objects.filter(id=testId).exists()
    
    if not test_exists:
        return generate_error_response(404, "Test not found")
    
    test = MCTTest.objects.get(id=testId)
    
    
    # Check if all questions have been answered
    total_questions = test.questions.count()
    answered_questions = test.questions.filter(hasUserAnswered=True).count()
    
    if total_questions != answered_questions:
        return generate_error_response(400, "All questions must be answered before completing the test")

    questions: list[MCTQuestion] = test.questions.all()

    # Update UnknownWord confidence levels based on answers
    for question in questions:
        unknown_word = UnknownWord.objects.filter(word=question.word, email=email).first()
        if question.isUserCorrect:
            increase_word_confidence(email, unknown_word, INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER)
            
        else:
            decrease_word_confidence(email, unknown_word, DECREASE_CONFIDENCE_ON_WRONG_MCQ_ANSWER)
    
    correct_answers = test.questions.filter(isUserCorrect=True).count()
    correctness_percentage = (float(correct_answers) / float(total_questions)) * 100
    test.correctPercentage = correctness_percentage
    test.isCompleted = True
    test.save()
    
    # Update conversation to update words
    conversation: Conversation = test.conversation
    conversation.update_words = True
    conversation.save()
    
    test_serializer = MCTTestSerializer(test)
    
    return generate_success_response("Test completed successfully", test_serializer.data)

