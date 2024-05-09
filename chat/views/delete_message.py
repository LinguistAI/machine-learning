from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
from chat.prompts.chat_gpt_system_prompt import get_gpt_chat_system_prompt
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
    method="delete",
    operation_description="Delete a message from a conversation",
    operation_id="Delete a message from a conversation",
    operation_summary="Delete a message from a conversation",
    manual_parameters=[
        openapi.Parameter(
            name='message_id', in_=openapi.IN_PATH,
            description='Unique identifier for the message',
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        "200": openapi.Response(
            description="Message deleted successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Message deleted successfully",
                    "data": "Message ID here..."
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
@api_view(['DELETE'])
def delete_message(request, message_id: str):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    if not message_id:
        return generate_error_response(400, "Message ID is required")
    
    message_exists = Message.objects.filter(id=message_id).exists()
    
    # Now get the last five messages from the conversations
    if not message_exists:
        return generate_error_response(404, "Message does not exist")
    
    message = Message.objects.get(id=message_id)
    
    conversation: Conversation = message.conversation
        
    message.delete()
    
    conversation.lastMessage = Message.objects.filter(conversation=conversation).last().messageText
    conversation.save()
    
    return generate_success_response("Message deleted successfully", message_id)
