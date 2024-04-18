import google.generativeai as genai
import os 
import json

import logging

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY, transport="rest")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

gemini_model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def parse_gemini_json(data: str):
    # Find the index of the first opening brace
    start_index = data.find('{')
    # Find the index of the last closing brace
    end_index = data.rfind('}')
    
    # Extract and return the substring between the first { and the last }
    # Includes the braces themselves in the extracted substring
    if start_index != -1 and end_index != -1 and end_index > start_index:
        json_data = data[start_index:end_index+1]
        return json.loads(json_data)
    else:
        # Return an error message or None if the required characters are not found
        # return empty json
        return json.loads("{}")

# TODO: Sometimes Gemini Model rejects input due to safety settings, handle that
logger.info("Gemini model is ready to use")


