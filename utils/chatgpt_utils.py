
import logging
from openai import OpenAI
import openai
import time
import os
from chat.models import Message

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def convert_senderType_to_role(senderType: str) -> str:
    if senderType == "bot":
        return "assistant"
    elif senderType == "user":
        return "user"
    else:
        logger.error(f"Invalid senderType: {senderType}")
        return "user"

def generate_gpt_chat_response(system_prompt, chat_history: list[Message], json=False):
    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            for message in chat_history:
                messages.append({
                    "role": convert_senderType_to_role(message.senderType), 
                    "content": message.messageText
                    })
            
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.7, 
            max_tokens=150,
            n=1,
        )
        print("Response1", response)
        end_time = time.time()
        print("Response2", response.choices[0].message.content)
        logger.info(f"Time taken to generate response: {end_time - start_time}")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Failed to generate response: {str(e)}")
        logger.error(e)
        return None


def generate_text_response(system_prompt):
    
    pass