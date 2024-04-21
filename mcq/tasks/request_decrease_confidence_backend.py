import requests
from chat.models import UnknownWord
from constants.service_constants import USER_SERVICE_DECREASE_CONFIDENCE_PATH

import logging

logger = logging.getLogger(__name__)

def request_decrease_confidence_backend(user_email: str, unknown_word: UnknownWord):

    if not user_email:
        logger.error("Error while decreasing confidence for user. User email is required")
        
    if not unknown_word:
        logger.error("Error while decreasing confidence for user {}. Unknown word is required".format(user_email))

    headers = {
        "UserEmail": user_email
    }
    
    request_body = {
        "word": unknown_word.word,
        "listId": unknown_word.listId
    }

    response = requests.post(USER_SERVICE_DECREASE_CONFIDENCE_PATH, 
                             json=request_body,
                             headers=headers)

    if not response or response.status_code != 200:
        logger.error("Error while decreasing confidence for word {}. Request failed: %s".format(unknown_word.word), response.text)
        return False

    response = response.json()

    if "status" not in response or response["status"] != 200:
        logger.error("Error while decreasing confidence for word {}. Request failed: %s".format(unknown_word.word), response)
        return False

    logger.info("Confidence decreased for word {} successfully".format(unknown_word.word), response)

    return True