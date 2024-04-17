import requests
from constants.service_constants import USER_SERVICE_QUEST_MESSAGE_PATH

def update_quest_on_chat(user_email: str, message: str):
    
    if not user_email:
        print("Error while updating Quest message for user. User email is required")
        
    if not message:
        print("Error while updating Quest message for user {}. Message is required".format(user_email))
    
    headers = {
        "UserEmail": user_email
    }
    
    request_body = {
        "message": message
    }
    
    response = requests.post(USER_SERVICE_QUEST_MESSAGE_PATH, json=request_body, headers=headers)
    
    if not response or response.status_code != 200:
        return False
    
    response = response.json()
    
    if "status" not in response or response["status"] != 200:
        return False
    
    print("Quest message sent successfully", response)
    
    return True