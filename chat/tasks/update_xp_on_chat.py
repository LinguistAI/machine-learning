import requests
from constants.service_constants import USER_SERVICE_XP_MESSAGE_PATH
import logging

logger = logging.getLogger(__name__)

def update_xp_on_chat(user_email: str):
    
    if not user_email:
        logger.error("Error while updating XP for user. User email is required")
    
    headers = {
        "UserEmail": user_email
    }
    
    response = requests.post(USER_SERVICE_XP_MESSAGE_PATH, headers=headers)
    
    if not response or response.status_code != 200:
        logger.error("Error while updating XP for user {}. Request failed: %s".format(user_email), response.text)
        return False
    
    response = response.json()
    
    if "status" not in response or response["status"] != 200:
        logger.error("Error while updating XP for user {}. Request failed: %s".format(user_email), response)
        return False
    
    logger.info("XP updated successfully", response)
    
    return True