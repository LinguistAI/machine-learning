import json
import time
from rest_framework.decorators import api_view
from chat.models import Conversation
from constants.header_constants import HEADER_USER_EMAIL
from mcq.prompts.create_mcq_prompt import create_mcq_prompt

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utils.gemini_utils import gemini_model


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
    
    # unknown_words = conversation.unknown_words
    
    
    
    
    
    # # prompt = create_mcq_prompt(word)
    
    # # Log gemini response time
    # start_time = time.time()
    # response = gemini_model.generate_content(prompt)
    # end_time = time.time()
    
    # # TODO: Add better logging
    # print(f"Time taken to generate Gemini response: {end_time - start_time}")
    
    # print("Gemini response: ", response.text)
    # print("Prompt feedback: ", response.prompt_feedback)
    
    # json_response = json.loads(response.text)
    
    return generate_success_response("Multiple choice question generated successfully", None)
    