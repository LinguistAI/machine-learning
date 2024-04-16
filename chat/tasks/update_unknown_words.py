import requests
from chat.models import Conversation, UnknownWord
from constants.unknown_word_constants import ACTIVE_WORD_LIST_SIZE, CONFIDENCE_LEVELS
from constants.service_constants import USER_SERVICE_SELECT_WORD_PATH

def update_unknown_words(conversation_id: str, user_email: str):
    
    conversation_exists = Conversation.objects.filter(id=conversation_id).exists()
    
    if not conversation_exists:
        print("Error while getting unknown words for {} conversation. Conversation does not exist".format(conversation_id))
        return None

    conversation = Conversation.objects.filter(id=conversation_id).first()
    conversation.unknownWords.update(isActive=False)
    
    request_body = {
        "conversationId": conversation_id,
        "size": ACTIVE_WORD_LIST_SIZE,
        "preservedWords": [],
    }
    
    headers = {
        "UserEmail": user_email
    }
    
    response = requests.post(USER_SERVICE_SELECT_WORD_PATH, json=request_body, headers=headers)
    
    if not response or response.status_code != 200:
        return None
    
    response = response.json()
    
    if "status" not in response or response["status"] != 200:
        return None
    
    data = response.get("data", [])
    unknown_words = []
    
    for word_obj in data:
        conversation_id = word_obj.get("conversationId")
        word_key = word_obj.get("word")
        confidence = word_key.get("confidence")
        word = word_key.get("word")
        
        confidence_level = 0
        
        # Give confidence an integer value according to the index in the CONFIDENCE_LEVELS list:
        if confidence in CONFIDENCE_LEVELS:
            confidence_level = CONFIDENCE_LEVELS.index(confidence)
        
        # Check if the word already exists in the database
        word_exists = conversation.unknownWords.filter(word=word).exists()
        
        if word_exists:
            unknown_word: UnknownWord = conversation.unknownWords.filter(word=word).first()
            unknown_word.confidenceLevel = confidence_level
            unknown_word.isActive = True
            unknown_word.save()
            
        else:        
            # Store the unknown word to the database
            unknown_word = UnknownWord.objects.create(
                word=word,
                confidenceLevel=confidence_level,
                isActive=True
            )
            unknown_word.save()
            conversation.unknownWords.add(unknown_word)
            conversation.save()
        
        unknown_words.append(unknown_word)
        
    conversation.update_words = False

    print("Unknown words for conversation {} are: {}".format(conversation_id, unknown_words))    

    return unknown_words