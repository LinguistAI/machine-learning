from django.http import HttpRequest
from rest_framework.decorators import api_view
from chat.serializers import  UnknownWordSerializer
from chat.tasks.update_unknown_words import update_unknown_words
from constants.header_constants import HEADER_USER_EMAIL

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(
    method='post',
)            
@api_view(['POST'])
def test_unknown_words(request: HttpRequest):
    
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL, None)
    if not email:
        return generate_error_response(400, "Authentication is required")
        
    if not request.data or "conversationId" not in request.data:
        return generate_error_response(400, "Conversation ID is required")
        
    conversation_id = request.data.get("conversationId")
    if not conversation_id:
        return generate_error_response(400, "Conversation ID is required")
    
    unknown_words = update_unknown_words(conversation_id, email)    
    
    serializer = UnknownWordSerializer(unknown_words, many=True)
    
    return generate_success_response("Unknown words retrieved successfully", serializer.data)