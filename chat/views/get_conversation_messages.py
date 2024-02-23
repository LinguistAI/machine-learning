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

# Create Django Rest Endpoint that returns a list of messages for a given conversation


@api_view(['GET'])
def get_conversation_messages(request):
    # Check the request header for email
    email = request.headers.get("email")
    if not email:
        return generate_error_response(400, "Email is required")
    
    # Get the conversation id that matches the email
    conversation = Conversation.objects.filter(user_email=email).first()
    
    # Now get the last five messages from the conversation
    previous_messages = Message.objects.filter(conversation=conversation).order_by('-timestamp')[:5]
    