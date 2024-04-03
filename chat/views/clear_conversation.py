from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_prompt import get_chat_prompt
from constants.header_constants import HEADER_USER_EMAIL
from profiling.models import Profile
from profiling.tasks.update_profile import update_profile_async

from utils.http_utils import generate_error_response, generate_success_response
from utils.gemini_utils import gemini_model
from drf_yasg.utils import swagger_auto_schema
import time
from constants.profile_constants import MAX_NO_OF_MESSAGE_CONTEXT
from concurrent.futures import ThreadPoolExecutor


from drf_yasg import openapi

@swagger_auto_schema(
    method="post",
    operation_description="Clear all messages from a conversation",
    operation_id="Clear all messages from a conversation",
    operation_summary="Clear all messages from a conversation",
    manual_parameters=[
        openapi.Parameter(
            name='conversation_id', in_=openapi.IN_PATH,
            description='Unique identifier for the chat session',
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        "200": openapi.Response(
            description="Conversation messages cleared successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Conversation messages cleared successfully",
                    "data": "Conversation ID here..."
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
        )
    }
)
@api_view(['POST'])
def clear_conversation(request, conversation_id: str):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    if not conversation_id:
        return generate_error_response(400, "Conversation ID is required")
    
    # Get the conversation id that matches the email if exists
    conversation_exists = Conversation.objects.filter(id=conversation_id).exists()
    
    # Now get the last five messages from the conversations
    if not conversation_exists:
        return generate_error_response(400, "Conversation does not exist")
    
    conversation = Conversation.objects.filter(id=conversation_id).first()
    
    messages = Message.objects.filter(conversation=conversation).all()
    
    messages.delete()
    
    return generate_success_response("Conversation messages cleared successfully", conversation_id)