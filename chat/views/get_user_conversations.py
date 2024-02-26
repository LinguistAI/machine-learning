from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from chat.models import Conversation, Message
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
    
@swagger_auto_schema(
    method='get',
    operation_description="Get all conversations for the current user",
    operation_id="Get all conversations for the current user",
    operation_summary="Get all conversations for the current user",
    responses={
        "200": openapi.Response(
            description="Conversations gathered successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Conversations gathered successfully",
                    "data": []
                }
            }
        )
    }
)
@api_view(['GET'])
def get_user_conversations(request):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Get all conversations for the user
    conversations = Conversation.objects.filter(userEmail=email)
    
    serializer = ConversationSerializer(conversations, many=True)
    
    return generate_success_response("Conversations gathered successfully", serializer.data)