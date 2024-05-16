from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from constants.header_constants import HEADER_USER_EMAIL
from mcq.models import ITEM_TYPE_MAPPING, MCTQuestion
from mcq.serializers import getItemSerializer

from utils.http_utils import generate_error_response, generate_success_response, validate_request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from mcq.tasks.request_decrease_item_quantity import request_decrease_item_quantity


@swagger_auto_schema(
    method='post',
    operation_description="Use a quiz item",
    operation_id="Use a quiz item",
    operation_summary="Use a quiz item",
    responses={
        "200": openapi.Response(
            description="Item used successfully",
            examples={
                "application/json": {
                    "timestamp": "2024-04-28 16:42:58",
                    "status": 200,
                    "msg": "Item used successfully",
                    "data": {
                        "id": "a04ed2ef-0e91-4f5d-878c-8abf6649ebd3",
                        "type": "Double Answer",
                        "maxNumOfUses": 1,
                        "usesSoFar": 1,
                        "question": "52bc3324-400d-4f1b-a5d7-8b446edc9c27"
                    }
                }
            }
        ),
        "400": openapi.Response(
            description="Invalid item type or item of the same type already used for this question",
            examples={
                "application/json": {
                    "timestamp": "2024-04-28 16:43:50",
                    "status": 400,
                    "msg": "There is already an item of type 'Double Answer' used for this question"
                }
            }
        ),
        "500": openapi.Response(
            description="An error occurred",
            examples={
                "application/json": {
                    "timestamp": "2024-04-28 16:43:50",
                    "status": 500,
                    "msg": "An error occurred: {explanation of the error}"
                }
            }
        )
    }
)
@api_view(['POST'])
@transaction.atomic  # So that item creation is rolled back if the user service returns an error
def use_item(request):
    try:
        # Check the request header for email
        validation_error = validate_request(request, required_data=["type", "questionId"])
        if validation_error:
            return validation_error

        email = request.headers.get(HEADER_USER_EMAIL)
        item_type = request.data.get("type")
        question_id = request.data.get("questionId")

        # Validate item type
        if item_type not in ITEM_TYPE_MAPPING:
            return generate_error_response(400, f"Invalid item type: {item_type}")

        # Check if the question has already been answered
        question = get_object_or_404(MCTQuestion, id=question_id)
        if question.hasUserAnswered:
            return generate_error_response(400, "The question has already been answered")

        # Check if there are other items of the same type tied to the same question
        if ITEM_TYPE_MAPPING[item_type].objects.filter(type=item_type, question_id=question_id).exists():
            return generate_error_response(400,
                                           f"There is already an item of type '{item_type}' used for this question")

        # Create a new item object based on the provided item type
        with transaction.atomic():
            # Create a new item object based on the provided item type
            item_class = ITEM_TYPE_MAPPING[item_type]
            item = item_class.objects.create(type=item_type, question_id=question_id)

            item.use()

            # Decrease item quantity from user
            success, msg = request_decrease_item_quantity(email, item_type)
            if not success:
                raise ValueError(msg)

            serializer = getItemSerializer(item)
            return generate_success_response("Item used successfully", serializer.data)
    except Exception as e:
        return generate_error_response(500, f"An error occurred: {str(e)}")