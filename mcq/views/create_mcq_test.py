import json
import time
from rest_framework.decorators import api_view
from chat.models import Conversation, UnknownWord
from constants.header_constants import HEADER_USER_EMAIL
from constants.unknown_word_constants import ACTIVE_WORD_LIST_SIZE, MCQ_TEST_QUESTION_PER_WORD
from mcq.models import MCTQuestion, MCTTest

from mcq.serializers import MCTTestSerializer
from mcq.tasks.create_mcq_question import create_mcq_question
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema


# Create Django Rest Endpoint that returns a list of messages for a given conversation
@swagger_auto_schema(
    method='post',
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
                answer=json_response["answer"],
                option1=json_response["options"][0],
                option2=json_response["options"][1],
                option3=json_response["options"][2],
                option4=json_response["answer"],
            )
            question.randomize_options()
            test.questions.add(question)
            question.save()
    
    test.save()
    
    test_serializer = MCTTestSerializer(test)
    
    return generate_success_response("Multiple choice question test generated successfully", test_serializer.data)
    