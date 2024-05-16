from rest_framework.decorators import api_view
from chat.models import ChatBot, Conversation, Message
from chat.serializers import ChatBotSerializer, MessageSerializer
from constants.header_constants import HEADER_USER_EMAIL

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create Django Rest Endpoint that returns a list of messages for a given conversation

@swagger_auto_schema(
    method='get',
    operation_description="Get all chatbots",
    operation_id="Get all chatbots",
    operation_summary="Get all chatbots",
    manual_parameters=[
        openapi.Parameter(
            'language',
            openapi.IN_QUERY,
            description="Filter chatbots by language",
            type=openapi.TYPE_STRING,
            default='ENG'
        )
    ],
    responses={
        "200": openapi.Response(
            description="Chatbots retrieved successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Chatbots retrieved successfully",
                    "data": []
                }
            }
        )
    }
)
@api_view(['GET'])
def get_all_bots(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Get the language query parameter, default to 'ENG'
    language = request.query_params.get('language', 'ENG')
    
    # Filter ChatBot objects by language
    chatbots = ChatBot.objects.filter(language=language)
    
    serializer = ChatBotSerializer(chatbots, many=True)
    
    return generate_success_response("All chatbots retrieved successfully", serializer.data)
