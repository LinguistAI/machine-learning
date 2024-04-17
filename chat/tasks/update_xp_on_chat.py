import requests
from constants.service_constants import USER_SERVICE_XP_MESSAGE_PATH

def update_xp_on_chat(user_email: str):
    
    if not user_email:
        print("Error while updating XP for user. User email is required")
    
    headers = {
        "UserEmail": user_email
    }
    
    response = requests.post(USER_SERVICE_XP_MESSAGE_PATH, headers=headers)
    
    if not response or response.status_code != 200:
        return False
    
    response = response.json()
    
    if "status" not in response or response["status"] != 200:
        return False
    
    print("XP updated successfully", response)
    
    return True