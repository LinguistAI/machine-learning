import json
import time
from mcq.prompts.create_mcq_prompt import create_mcq_prompt

from utils.gemini_utils import gemini_model
import logging

logger = logging.getLogger(__name__)

def create_mcq_question(word: str):
    
    prompt = create_mcq_prompt(word)
    
    # Log gemini response time
    start_time = time.time()
    response = gemini_model.generate_content(prompt)
    end_time = time.time()
    
    logger.info(f"Time taken to generate Gemini response for MCQ: {end_time - start_time}")
    
    json_response = json.loads(response.text)
    
    return json_response
    