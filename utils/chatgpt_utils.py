
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
    
AVAILABLE_MODELS = [ 
    "gpt-4o",
    "gpt-4o-2024-05-13",
    "gpt-4-turbo",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-0125-preview",
    "gpt-4-turbo-preview",
    "gpt-4-1106-preview",
    "gpt-4-vision-preview",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-16k-0613",
]

def generate_gpt_chat_response(system_prompt, chat_history: list[Message], model="gpt-4o", last_message=None):
    if model not in AVAILABLE_MODELS:
        logger.error(f"Invalid model: {model}")
        return None
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        if chat_history:
            for message in chat_history:
                messages.append({
                    "role": convert_senderType_to_role(message.senderType), 
                    "content": message.messageText
                    })
            if last_message:
                messages.append({
                    "role": "user",
                    "content": last_message
                })
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7, 
            max_tokens=150,
            n=1,
        )
        end_time = time.time()
        logger.info("ChatGPT response is " +  response.choices[0].message.content)
        logger.info(f"Time taken to generate response: {end_time - start_time}")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Failed to generate response: {str(e)}")
        logger.exception(e)
        return None


def generate_text_response(system_prompt):
    
    pass