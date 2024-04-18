

from profiling.models import Profile
from profiling.prompts.profile_prompt import get_profile_prompt
import time
from utils.gemini_utils import gemini_model, parse_gemini_json

import logging

logger = logging.getLogger(__name__)

def update_profile_async(profile: Profile, last_messages: str, last_message: str):
    logger.info("Updating profile async for user: %s", profile.email)
    
    context = last_messages + "\n" + last_message

    profile_prompt = get_profile_prompt(str(profile), context)  
    
    # Log gemini response time
    start_time = time.time()
    response = gemini_model.generate_content(profile_prompt)
    end_time = time.time()
    
    # TODO: Add better logging
    logger.info(f"Time taken to generate Gemini response for profile update: {end_time - start_time}")
    
    data = parse_gemini_json(response.text)
    
    profile.likes = data['likes']
    profile.dislikes = data['dislikes']
    profile.loves = data['loves']
    profile.hates = data['hates']
    profile.profileInfo = data['profile-info']
    
    profile.save()
    
    logger.info("Profile updated successfully for user: %s", profile.email)
    return
    
    