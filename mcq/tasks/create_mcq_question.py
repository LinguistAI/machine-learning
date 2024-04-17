import json
import time
from mcq.prompts.create_mcq_prompt import create_mcq_prompt

from utils.gemini_utils import gemini_model


def create_mcq_question(word: str):
    
    prompt = create_mcq_prompt(word)
    
    # Log gemini response time
    start_time = time.time()
    response = gemini_model.generate_content(prompt)
    end_time = time.time()
    
    # TODO: Add better logging
    print(f"Time taken to generate Gemini response: {end_time - start_time}")
    
    print("Gemini response: ", response.text)
    print("Prompt feedback: ", response.prompt_feedback)
    
    json_response = json.loads(response.text)
    
    return json_response
    