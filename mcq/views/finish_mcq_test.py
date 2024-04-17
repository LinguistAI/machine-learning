from concurrent.futures import ThreadPoolExecutor
from rest_framework.decorators import api_view
from chat.models import Conversation, UnknownWord
from constants.header_constants import HEADER_USER_EMAIL
from constants.unknown_word_constants import DECREASE_CONFIDENCE_ON_WRONG_MCQ_ANSWER, INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER
from mcq.models import MCTQuestion, MCTTest

from mcq.serializers import MCTTestSerializer
from mcq.tasks.decrease_confidence_mcq import decrease_confidence_mcq
from mcq.tasks.increase_confidence_mcq import increase_confidence_mcq
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema

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
                                "option1": "Randomized Option 1",
                                "option2": "Randomized Option 2",
                                "option3": "Randomized Option 3",
                                "option4": "Randomized Option 4",
                                "createdAt": "2021-08-30 14:00:00",
                                "updatedAt": "2021-08-30 14:00:00",
                                "isUserCorrect": False,
                                "hasUserAnswered": False
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
            # Increase confidence in current db
            unknown_word.increase_confidence(INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER)
            # Update user service to increase confidence async
            executor = ThreadPoolExecutor()
            executor.submit(increase_confidence_mcq, email, unknown_word)
            
        else:
            # Decrease confidence in current db
            unknown_word.decrease_confidence(DECREASE_CONFIDENCE_ON_WRONG_MCQ_ANSWER)
            # Update user service to decrease confidence async
            executor = ThreadPoolExecutor()
            executor.submit(decrease_confidence_mcq, email, unknown_word)
    
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

