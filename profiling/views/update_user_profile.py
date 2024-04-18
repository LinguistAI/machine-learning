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
    method='put',
)
@api_view(['PUT'])
def update_user_profile(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    if not request.data or "profile" not in request.data:
        return generate_error_response(400, "Profile is required")
    
    profile_data = request.data.get("profile")
    
    # TODO: Support hobbies
    if "hobbies" in profile_data:
        profile_data.pop("hobbies")
        
    
    # Before updating the profile, check if the profile exists
    profile_exists = Profile.objects.filter(email=email).exists()
    
    if not profile_exists:
        profile = Profile.objects.create(email=email, **profile_data).save()
    else: 
        Profile.objects.update(email=email, **profile_data)
        profile = Profile.objects.filter(email=email).first()
        
    serializer = ProfileSerializer(profile)
    
    return generate_success_response("Profile updated successfully", serializer.data)