

from concurrent.futures import ThreadPoolExecutor
from math import floor
from chat.models import UnknownWord
from constants.unknown_word_constants import CONFIDENCE_LEVEL_SCALING_FACTOR, DECREASE_CONFIDENCE_ON_WRONG_MCQ_ANSWER
from mcq.tasks.request_decrease_confidence_backend import request_decrease_confidence_backend
from mcq.tasks.request_increase_confidence_backend import request_increase_confidence_backend


def increase_word_confidence(email: str, 
                             unknown_word: UnknownWord,
                             increase_amount: float):
    
    previous_confidence = unknown_word.confidenceLevel
    next_confidence = previous_confidence + increase_amount
    
    previous_confidence_category = floor(previous_confidence / CONFIDENCE_LEVEL_SCALING_FACTOR)
    next_confidence_category = floor(next_confidence / CONFIDENCE_LEVEL_SCALING_FACTOR)
    # Increase confidence in current db
    unknown_word.increase_confidence(increase_amount)
    
    if previous_confidence_category != next_confidence_category:
        # Update user service to increase confidence async
        executor = ThreadPoolExecutor()
        executor.submit(request_increase_confidence_backend, email, unknown_word)
    
def decrease_word_confidence(email: str, 
                             unknown_word: UnknownWord,
                             decrease_amount: float):
    
    previous_confidence = unknown_word.confidenceLevel
    next_confidence = previous_confidence - decrease_amount
    
    previous_confidence_category = floor(previous_confidence / CONFIDENCE_LEVEL_SCALING_FACTOR)
    next_confidence_category = floor(next_confidence / CONFIDENCE_LEVEL_SCALING_FACTOR)
    # Increase confidence in current db
    unknown_word.decrease_confidence(decrease_amount)
    
    if previous_confidence_category != next_confidence_category:
        # Update user service to increase confidence async
        executor = ThreadPoolExecutor()
        executor.submit(request_decrease_confidence_backend, email, unknown_word)