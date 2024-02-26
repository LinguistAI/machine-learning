from django.http import HttpRequest
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import ChatBot, Conversation, Message
from chat.prompts.chat_prompt import get_chat_prompt
from chat.serializers import ConversationSerializer
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

from utils.utils import is_valid_uuid

@swagger_auto_schema(
    method='post',
    operation_description="Create a conversation",
    operation_id="Create a conversation",
    operation_summary="Create a conversation",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'botId': openapi.Schema(type=openapi.TYPE_STRING, description="Bot ID")
        }
    ),
    responses={
        "200": openapi.Response(
            description="Conversation generated successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Conversation generated successfully",
                    "data": {}
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
def create_conversation(request: HttpRequest):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
        
    if not request.data or "botId" not in request.data:
        return generate_error_response(400, "Bot selection is required")
        
    bot_id = request.data.get("botId")
    if not bot_id:
        return generate_error_response(400, "Bot selection is required")
    
    # Check if bot_id is valid uuid4
    is_valid_uuid4 = is_valid_uuid(bot_id, version=4)
    
    if not is_valid_uuid4:
        return generate_error_response(400, "Invalid bot ID")
    
    bot_exists = ChatBot.objects.filter(id=bot_id).exists()
    
    if not bot_exists:
        return generate_error_response(400, "Bot not found")
    
    bot = ChatBot.objects.filter(id=bot_id).first()
    
    user_conversations_exists = Conversation.objects.filter(userEmail=email, bot=bot).exists()
    
    if user_conversations_exists:
        return generate_error_response(400, "A conversation already exists with this bot")
    
    bot = ChatBot.objects.filter(id=bot_id).first()
     
    title = bot.name
    
    conversation = Conversation.objects.create(userEmail=email, bot=bot, title=title)
    serializer = ConversationSerializer(conversation)
    
    return generate_success_response("Conversation created successfully", serializer.data)