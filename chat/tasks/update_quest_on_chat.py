import requests
from constants.service_constants import USER_SERVICE_QUEST_MESSAGE_PATH
import logging

logger = logging.getLogger(__name__)

def update_quest_on_chat(user_email: str, message: str):
    
    if not user_email:
        logger.error("Error while updating Quest message for user. User email is required")
        
    if not message:
        logger.error("Error while updating Quest message for user {}. Message is required".format(user_email))
    
    headers = {
        "UserEmail": user_email
    }
    
    request_body = {
        "message": message
    }
    
    response = requests.post(USER_SERVICE_QUEST_MESSAGE_PATH, json=request_body, headers=headers)
    
    if not response or response.status_code != 200:
        logger.error("Error while updating Quest message for user {}. Request failed: %s".format(user_email), response.text)
        return False
    
    response = response.json()
    
    if "status" not in response or response["status"] != 200:
        logger.error("Error while updating Quest message for user {}. Request failed: %s".format(user_email), response)
        return False
    
    logger.info("Quest message updated successfully for user {}".format(user_email))
    
    return True