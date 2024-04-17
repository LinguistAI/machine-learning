from rest_framework.decorators import api_view
from constants.header_constants import HEADER_USER_EMAIL
from mcq.models import MCTTest

from mcq.serializers import MCTTestSerializer
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method='post',
)
@api_view(['POST'])
def submit_answer(request, question_id: str):
    
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
    
    correct_answers = test.questions.filter(isUserCorrect=True).count()
    correctness_percentage = (float(correct_answers) / float(total_questions)) * 100
    test.correctPercentage = correctness_percentage
    test.isCompleted = True
    test.save()
    
    test_serializer = MCTTestSerializer(test)
    
    return generate_success_response("Test completed successfully", test_serializer.data)

