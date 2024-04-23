from rest_framework.decorators import api_view
from constants.header_constants import HEADER_USER_EMAIL
from profiling.models import Profile
from profiling.serializers import ProfileSerializer

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg.utils import swagger_auto_schema
import json
from drf_yasg import openapi
from rest_framework import status

# Define request and response schemas
request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'profile': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'likes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                'dislikes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                'loves': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                'hates': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
            },
            required=['likes', 'dislikes', 'loves', 'hates']
        ),
    },
    required=['profile']
)

response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'status': openapi.Schema(type=openapi.TYPE_INTEGER),
        'msg': openapi.Schema(type=openapi.TYPE_STRING),
        'data': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'loves': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), nullable=True),
                'likes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                'dislikes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), nullable=True),
                'hates': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                'profileInfo': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                'createdDate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                'updatedDate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
            },
            required=['likes', 'hates', 'id', 'createdDate', 'updatedDate']
        )
    },
    required=['timestamp', 'status', 'msg', 'data']
)

@swagger_auto_schema(
    method='put',
    request_body=request_body,
    responses={
        status.HTTP_200_OK: response_schema,
        status.HTTP_400_BAD_REQUEST: "Invalid request body or Authentication is required",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
    },
)
@api_view(['PUT'])
def update_ml_profile(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")

    if not request.data or "profile" not in request.data:
        return generate_error_response(400, "Profile is required")

    profile_data = request.data.get("profile")

    valid_fields = {"likes", "dislikes", "loves", "hates"}
    if not set(profile_data.keys()).issubset(valid_fields):
        return generate_error_response(400, "Invalid fields in request")

    # Before updating the profile, check if the profile exists
    profile_exists = Profile.objects.filter(email=email).exists()

    if not profile_exists:
        for key, value in profile_data.items():
            if isinstance(value, list):
                profile_data[key] = json.dumps(value)

        Profile.objects.create(email=email, **profile_data).save()
    else:
        for key, value in profile_data.items():
            if isinstance(value, list):
                profile_data[key] = json.dumps(value)

        Profile.objects.filter(email=email).update(**profile_data)

    profile = Profile.objects.filter(email=email).first()
    serializer = ProfileSerializer(profile)

    return generate_success_response("Profile updated successfully", serializer.data)