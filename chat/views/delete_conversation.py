from rest_framework.decorators import api_view
from chat.models import Conversation, Message
from constants.header_constants import HEADER_USER_EMAIL

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema


from drf_yasg import openapi

@swagger_auto_schema(
    method="delete",
    operation_description="Delete a conversation",
    operation_id="Delete a conversation",
    operation_summary="Delete a conversation",
    manual_parameters=[
        openapi.Parameter(
            name='conversation_id', in_=openapi.IN_PATH,
            description='Unique identifier for the conversation',
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        "200": openapi.Response(
            description="Conversation deleted successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Conversation deleted successfully",
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
        ),
        "404": openapi.Response(
            description="Not found",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 404,
                    "msg": "Conversation does not exist"
                }
            }
        )
    }
)
@api_view(['DELETE'])
def delete_conversation(request, conversation_id: str):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    if not conversation_id:
        return generate_error_response(400, "Conversation ID is required")
    
    conversation_exists = Conversation.objects.filter(id=conversation_id).exists()
    
    # Now get the last five messages from the conversations
    if not conversation_exists:
        return generate_error_response(404, "Conversation does not exist")
    
    conversation = Conversation.objects.get(id=conversation_id)
    
    messages = Message.objects.filter(conversation=conversation).all()
    
    messages.delete()
    
    conversation.delete()
    
    return generate_success_response("Conversation deleted successfully", conversation_id)
