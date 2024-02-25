import json
import time
from rest_framework.decorators import api_view
from constants.header_constants import HEADER_USER_EMAIL
from mcq.prompts.create_mcq_prompt import create_mcq_prompt

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utils.gemini_utils import gemini_model


# Create Django Rest Endpoint that returns a list of messages for a given conversation
@swagger_auto_schema(
    method='post',
    operation_description="Create a multiple choice question",
    operation_id="Create a multiple choice question",
    operation_summary="Create a multiple choice question",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["word"],
        properties={
            "word": openapi.Schema(type=openapi.TYPE_STRING, description="Word to generate a multiple choice question for")
        },
    ),
    responses={
        "200": openapi.Response(
            description="Multiple choice question generated successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Multiple choice question generated successfully",
                    "data": {
                        "question": "Plants convert sunlight into energy through the process of _______.",
                        "options": [
                            "Respiration",
                            "Fermentation",
                            "Transpiration"
                        ],
                        "answer": "Photosynthesis"
                    }
                }
            }
        ),
        "400": openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 400,
                    "msg": "Word is required"
                }
            }
        )
    }
)
@api_view(['POST'])
def create_mcq_question(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")
    
    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")
    
    # Check request data for message
    if not request.data or "word" not in request.data:
        return generate_error_response(400, "Word is required")

    # Get message from request body
    word = request.data.get("word")
    if not word:
        return generate_error_response(400, "Word is required")
    
    prompt = create_mcq_prompt(word)
    
    # Log gemini response time
    start_time = time.time()
    response = gemini_model.generate_content(prompt)
    end_time = time.time()
    
    # TODO: Add better logging
    print(f"Time taken to generate Gemini response: {end_time - start_time}")
    
    print("Gemini response: ", response.text)
    print("Prompt feedback: ", response.prompt_feedback)
    
    json_response = json.loads(response.text)
    
    return generate_success_response("Multiple choice question generated successfully", json_response)
    