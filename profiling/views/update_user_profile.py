from rest_framework.decorators import api_view
from chat.models import Conversation, Message
from chat.serializers import MessageSerializer
from constants.header_constants import HEADER_USER_EMAIL
from profiling.models import Hobby, Profile
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
    
    valid_fields = {"birthDate", "englishLevel", "hobbies", "name"}
    if not set(profile_data.keys()).issubset(valid_fields):
        return generate_error_response(400, "Invalid fields in request")
    
    hobby_objects = []
    
    if "hobbies" in profile_data:
        hobbies = profile_data.pop("hobbies")
        if not isinstance(hobbies, list):
            return generate_error_response(400, "Hobbies must be a list")
        
        for hobby in hobbies:
            if not isinstance(hobby, str):
                return generate_error_response(400, "Hobbies must be a list of strings")
        
        for hobby in hobbies:
            hobby_result: tuple[Hobby, bool]= Hobby.objects.get_or_create(name=hobby.lower())
            hobby_obj = hobby_result[0]
            hobby_objects.append(hobby_obj)
            
    profile_result: tuple[Profile, bool] = Profile.objects.update_or_create(email=email, defaults=profile_data)
    profile = profile_result[0]
    
    if len(hobby_objects) > 0:
        profile.hobbies.add(*hobby_objects)
        
    profile.save()
        
    serializer = ProfileSerializer(profile)
    
    return generate_success_response("Profile updated successfully", serializer.data)