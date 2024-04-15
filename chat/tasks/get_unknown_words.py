

import requests
from chat.models import Conversation
from constants.service_constants import USER_SERVICE_SELECT_WORD_PATH

def get_unknown_words(conversation: Conversation):
    
    # Send POST request to USER_SERVICE_SELECT_WORD_PATH
    # with body
    request_body = {
        "conversationId": conversation.id,
        "size": 5
    }
    
    response = requests.post(USER_SERVICE_SELECT_WORD_PATH, json=request_body)
    
    print("get_unknown_words response", response)
    
    return 