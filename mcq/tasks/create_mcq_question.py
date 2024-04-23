import json
import time
from mcq.prompts.create_mcq_prompt import create_mcq_prompt

from utils.gemini_utils import gemini_model, parse_gemini_json
import logging

logger = logging.getLogger(__name__)

def create_mcq_question(word: str):
    
    prompt = create_mcq_prompt(word)
    
    # Log gemini response time
    start_time = time.time()
    response = gemini_model.generate_content(prompt)
    end_time = time.time()
    
    logger.info(f"Time taken to generate Gemini response for MCQ: {end_time - start_time}")
    
    data = parse_gemini_json(response.text)
    
    
    return data
    