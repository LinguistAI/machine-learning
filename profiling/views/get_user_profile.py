from rest_framework.decorators import api_view
from chat.models import Conversation, Message
from chat.serializers import MessageSerializer
from constants.header_constants import HEADER_USER_EMAIL
from profiling.models import Profile
from profiling.serializers import ProfileSerializer

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create Django Rest Endpoint that returns a list of messages for a given conversation

@swagger_auto_schema(
    method='get',
    operation_description="Get user profile",
    operation_id="Get user profile",
    operation_summary="Get user profile",
    responses={
        "200": openapi.Response(
            description="Profile retrieved successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Profile retrieved successfully",
                    "data": {
                        "loves": [],
                        "likes": [],
                        "dislikes": [
                            "running"
                        ],
                        "hates": [],
                        "profileInfo": {},
                        "id": "67dc6128-6ecf-49d9-aaca-731f3670eb12",
                        "createdDate": "2024-04-18T09:29:50.705974Z",
                        "updatedDate": "2024-04-22T10:50:34.858758Z"
                     }
                }
            }
        ),
    }
)
@api_view(['GET'])
def get_user_profile(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    profile = Profile.objects.filter(email=email).first()
    
    if not profile:
        profile = Profile.objects.create(email=email)
        
    serializer = ProfileSerializer(profile)
    
    return generate_success_response("Profile retrieved successfully", serializer.data)
    