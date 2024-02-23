from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_prompt import get_chat_prompt
from profiling.models import Profile

from utils.http_utils import generate_error_response, generate_success_response
from utils.gemini_utils import gemini_model
from utils.utils import parse_gemini_json
from drf_yasg.utils import swagger_auto_schema
import time

from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Generate a response to a chat message",
    operation_id="Generate a response to a chat message",
    operation_summary="Generate a response to a chat message",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description="User message")
        }
    ),
    responses={
        "200": openapi.Response(
            description="Chat response generated successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Chat response generated successfully",
                    "data": "Bot response here..."
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
        "400": openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 400,
                    "msg": "Message is required"
                }
            }
        )
    }
)
@api_view(['POST'])
def generate_chat_response(request):
    
    # Check the request header for email
    email = request.headers.get("email")
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Check the request body for message
    message = request.data.get("message")
    if not message:
        return generate_error_response(400, "Message is required")
    
    # Get the conversation id that matches the email
    conversation = Conversation.objects.filter(user_email=email).first()
    
    # Now get the last five messages from the conversation
    previous_messages = Message.objects.filter(conversation=conversation).order_by('-timestamp')[:5]
    
    # Get user profile
    profile = Profile.objects.get(email=email)
    
    chat_prompt = get_chat_prompt(previous_messages, profile, message)
    
    # Log gemini response time
    start_time = time.time()
    response = gemini_model.generate_content(chat_prompt)
    end_time = time.time()
    
    # TODO: Add better logging
    print(f"Time taken to generate Gemini response: {end_time - start_time}")

    data = parse_gemini_json(response.text)
    
    return generate_success_response("Chat response generated successfully", data)