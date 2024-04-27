import requests
from django.db import transaction
from rest_framework.decorators import api_view
from constants.header_constants import HEADER_USER_EMAIL
from mcq.models import ITEM_TYPE_MAPPING
from constants.service_constants import USER_SERVICE_DECREASE_ITEM_QUANTITY_PATH

from utils.http_utils import generate_error_response, generate_success_response, validate_request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema()  #TODO
@api_view(['POST'])
@transaction.atomic  # So that item creation is rolled back if the user service returns an error
def use_item(request):
    try:
        # Add check: if the question was already answered do not allow for item use
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
            headers = {
                "UserEmail": email
            }
            params = {
                "type": item_type,
            }
            response = requests.post(USER_SERVICE_DECREASE_ITEM_QUANTITY_PATH,
                                     headers=headers)

            print(response)
            if response.status_code != 200:
                # If there's an error with the user service, raise an exception to rollback the transaction
                raise ValueError("Error occurred while decreasing item quantity from user")

        return generate_success_response("Item used successfully", "") # TODO add serializer
    except Exception as e:
        return generate_error_response(500, f"An error occurred: {str(e)}")
