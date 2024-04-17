import requests
from chat.models import UnknownWord
from constants.service_constants import USER_SERVICE_INCREASE_CONFIDENCE_PATH

def increase_confidence_mcq(user_email: str, unknown_word: UnknownWord):

    if not user_email:
        print("Error while increasing confidence for user. User email is required")
        
    if not unknown_word:
        print("Error while increasing confidence for user {}. Unknown word is required".format(user_email))

    headers = {
        "UserEmail": user_email
    }
    
    request_body = {
        "word": unknown_word.word,
        "listId": unknown_word.listId
    }

    response = requests.post(USER_SERVICE_INCREASE_CONFIDENCE_PATH, 
                             json=request_body,
                             headers=headers)

    if not response or response.status_code != 200:
        return False

    response = response.json()

    if "status" not in response or response["status"] != 200:
        return False

    print("Confidence increased for word {} successfully".format(unknown_word.word), response)

    return True