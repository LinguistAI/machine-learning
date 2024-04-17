from rest_framework.decorators import api_view
from chat.models import Conversation, UnknownWord
from constants.header_constants import HEADER_USER_EMAIL
from constants.unknown_word_constants import INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER
from mcq.models import MCTQuestion, MCTTest

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

    questions: list[MCTQuestion] = test.questions.all()

    # Update UnknownWord confidence levels based on answers
    for question in questions:
        if question.isUserCorrect:
            UnknownWord.objects.filter(word=question.word, email=email).first().increase_confidence(INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER)
        else:
            UnknownWord.objects.filter(word=question.word, email=email).first().decrease_confidence(INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER)
    
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

