from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_prompt import get_chat_prompt
from profiling.models import Profile

from utils.http_utils import generate_error_response
from utils.gemini_utils import gemini_model
from utils.utils import parse_gemini_json
import time

@api_view(['POST'])
def generate_chat_response(request):
    
    # Check the request header for email
    email = request.headers.get("email")
    if not email:
        return generate_error_response(400, "Email is required")
    
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
    
    prompt_response_dict = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 200,
        "msg": "Success",
        "data": data
    }
    return Response(prompt_response_dict, status=200)