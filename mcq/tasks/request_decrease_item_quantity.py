import requests
import logging
from constants.service_constants import USER_SERVICE_DECREASE_ITEM_QUANTITY_PATH

logger = logging.getLogger(__name__)


def request_decrease_item_quantity(user_email: str, type: str):
    if not user_email:
        logger.error("Error while decreasing item quantity for user. User email is required")

    if not type:
        logger.error("Error while decreasing item quantity for user {}. String is required".format(user_email))

    headers = {
        "UserEmail": user_email
    }

    params = {
        "type": type,
    }
    response = requests.post(USER_SERVICE_DECREASE_ITEM_QUANTITY_PATH,
                             headers=headers,
                             params=params)

    if not response or response.status_code != 200:
        logger.error("Error while decreasing item quantity for user {}, item of type {}. Request failed: %s".format(user_email, type),
                     response.text)
        return False

    response = response.json()

    if "status" not in response or response["status"] != 200:
        logger.error(
            "Error while decreasing item quantity for user {}, item of type {}. Request failed: %s".format(user_email,
                                                                                                           type),
            response.text)
        return False

    logger.info("Item quantity decreased for item of type {} successfully".format(type), response)

    return True