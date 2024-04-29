import requests
import logging
from constants.service_constants import USER_SERVICE_DECREASE_ITEM_QUANTITY_PATH

logger = logging.getLogger(__name__)


def request_decrease_item_quantity(user_email: str, item_type: str):
    if not user_email:
        logger.error("Error while decreasing item quantity for user. User email is required")
        return False, "User email is required"

    if not item_type:
        logger.error("Error while decreasing item quantity for user {}. Item type is required".format(user_email))
        return False, "Item type is required"

    headers = {
        "UserEmail": user_email
    }

    params = {
        "type": item_type,
    }
    response = requests.post(USER_SERVICE_DECREASE_ITEM_QUANTITY_PATH,
                             headers=headers,
                             params=params)

    if response is None:
        error_msg = "Error while decreasing item quantity for user {}, item of type {}. Request failed: {}".format(user_email, item_type, response.text if response else "No response")
        logger.error(error_msg)
        return False, error_msg

    try:
        response_data = response.json()
        status = response_data.get("status")
        if status != 200:
            msg = response_data.get("msg", "Unknown error occurred")
            error_msg = "Error while decreasing item quantity for user {}, item of type {}: {}".format(user_email, item_type, msg)
            logger.error(error_msg)
            return False, error_msg
    except Exception as e:
        logger.error("Error while processing response: {}".format(e))
        return False, "Error while processing response: {}".format(e)

    logger.info("Item quantity decreased for item of type {} successfully".format(item_type))
    return True, "Item quantity decreased successfully"
