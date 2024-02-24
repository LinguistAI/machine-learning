from rest_framework.decorators import api_view
from chat.models import Conversation, Message
from chat.serializers import MessageSerializer
from constants.header_constants import HEADER_USER_EMAIL

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create Django Rest Endpoint that returns a list of messages for a given conversation

@swagger_auto_schema(
    method='get',
    operation_description="Get all messages from current user's conversation",
    operation_id="Get all messages from current user's conversation",
    operation_summary="Get all messages from current user's conversation",
    responses={
        "200": openapi.Response(
            description="Messages retrieved successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Messages retrieved successfully",
                    "data": []
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
@api_view(['GET'])
def get_all_conversation_messages(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Get the conversation id that matches the email
    conversation = Conversation.objects.filter(user_email=email).first()
    
    # Now get the last five messages from the conversation
    previous_messages = Message.objects.filter(conversation=conversation).order_by('-timestamp')
    
    serializer = MessageSerializer(previous_messages, many=True)
    
    return generate_success_response("Messages retrieved successfully", serializer.data)
    