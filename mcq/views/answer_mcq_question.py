from rest_framework.decorators import api_view
from constants.header_constants import HEADER_USER_EMAIL
from mcq.models import MCTQuestion

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Submit answer to a multiple choice question",
    operation_id="submit_answer",
    operation_summary="Submit answer to a multiple choice question",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'questionId': openapi.Schema(type=openapi.TYPE_STRING, description="Question ID"),
            'answer': openapi.Schema(type=openapi.TYPE_STRING, description="User's answer (case-insensitive)")
        }
    ),
    responses={
        
        "200": openapi.Response(
            description="Answer submitted successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Answer submitted successfully",
                    "data": {
                        "id": "Question ID",
                        "email": "User's email",
                        "word": "Word",
                        "answer": "Correct answer",
                        "option1": "Randomized Option 1",
                        "option2": "Randomized Option 2",
                        "option3": "Randomized Option 3",
                        "option4": "Randomized Option 4",
                        "createdAt": "2021-08-30 14:00:00",
                        "updatedAt": "2021-08-30 14:00:00",
                        "isUserCorrect": True,
                        "hasUserAnswered": True
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
                    "msg": "Question not found"
                }
            }
        )
    }
)            
@api_view(['POST'])
def answer_mcq_question(request):
    
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Check request data for message
    if not request.data or "questionId" not in request.data:
        return generate_error_response(400, "Question ID is required")

    # Get message from request body
    questionId = request.data.get("questionId")
    if not questionId:
        return generate_error_response(400, "Question ID is required")
    
    if "answer" not in request.data:
        return generate_error_response(400, "Answer is required")
    
    user_answer = request.data.get("answer")
    if not user_answer:
        return generate_error_response(400, "Answer is required")

    question_exists = MCTQuestion.objects.filter(id=questionId).exists()
    
    if not question_exists:
        return generate_error_response(404, "Question not found")
    
    question = MCTQuestion.objects.get(id=questionId)

    # Update the question with user's answer
    # compare the user's answer with the correct answer as string
    question.isUserCorrect = (str(user_answer).lower() == question.answer.lower())
    question.hasUserAnswered = True
    question.save()

    question_serializer = MCTQuestionSerializer(question)
    
    return generate_success_response("Answer submitted successfully", question_serializer.data)
