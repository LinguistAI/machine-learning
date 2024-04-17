import json
import time
from rest_framework.decorators import api_view
from chat.models import Conversation, UnknownWord
from constants.header_constants import HEADER_USER_EMAIL
from constants.unknown_word_constants import ACTIVE_WORD_LIST_SIZE, MCQ_TEST_QUESTION_PER_WORD
from mcq.models import MCTQuestion, MCTTest

from mcq.serializers import MCTQuestionSerializer, MCTTestSerializer
from mcq.tasks.create_mcq_question import create_mcq_question
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
