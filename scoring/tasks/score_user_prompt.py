
import logging
import time
from chat.models import UnknownWord
from scoring.models import WordScore
from utils.gemini_utils import gemini_model
import re
import nltk
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer
import json

from scoring.prompts.score_prompt import get_score_prompt

logger = logging.getLogger(__name__)

# Ensure that you have the required nltk resources downloaded
nltk.download('words')
nltk.download('wordnet')

def find_words_in_list(message: str, word_list: list[str]):
    # Normalize the message and split into words
    words_in_message = re.findall(r'\b\w+\b', message.lower())
    
    # Normalize the list of words for checking
    normalized_word_list = set(word.lower() for word in word_list)
    
    # Check and collect words that are in the list
    found_words = [word for word in words_in_message if word in normalized_word_list]
    
    return found_words

def find_unknown_words(message:str):
    word_list = set(words.words())
    lemmatizer = WordNetLemmatizer()
    
    # Split and normalize the message
    words_in_message = re.findall(r'\b\w+\b', message.lower())
    
    # Find unknown words considering their base forms
    unknown_words = []
    for word in words_in_message:
        lemmas = {lemmatizer.lemmatize(word), lemmatizer.lemmatize(word, pos='v')}
        if not lemmas & word_list:
            unknown_words.append(word)
    
    return unknown_words

def score_user_prompt(email: str, unknownWords: list[UnknownWord], message: str):
    
    if not email:
        logger.error("Error while scoring user prompt. User email is required")
    
    if not message:
        logger.error(f"Error while scoring user prompt. Message is required for {email}")
    
    if not unknownWords:
        logger.error(f"Error while scoring user prompt. Unknown words are required for {email}")
        
    # Check if message contains any unknown words, store them in a list
    # Use nltk to for checking if the message contains any unknown words
    # As the word may be used with a paragogic or a suffix
    unknown_words_list = [word.word for word in unknownWords]
    logger.info(f"Unknown words list for user {email}: {unknown_words_list}")
    
    unknown_words_in_sentence = find_words_in_list(message, unknown_words_list)
    
    logger.info(f"Unknown words in user prompt for user {email}: {unknown_words_in_sentence}")
    
    # if unknown_words_in_sentence is empty, then return
    if not unknown_words_in_sentence:
        logger.info(f"No unknown words found in user prompt for user {email}")
        return
    
    score_prompt = get_score_prompt(message, unknown_words_in_sentence)
    
    start_time = time.time()
    response = gemini_model.generate_content(score_prompt)
    end_time = time.time()
    
    logger.info(f"Time taken to generate Gemini response for scoring user prompt {email}: {end_time - start_time}")
    
    
    # Remove ``` from the beginning and ``` at the end of the response text
    # if they exist
    response_text = response.text
    
    if response_text.startswith('```'):
        response_text = response.text[3:]
    
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    
    # Parse response as json
    json_response = json.loads(response_text)
    
    word_scores = []
    
    for word_score in json_response:
        word = word_score['word']
        properties = word_score['properties']
        reasoning = word_score['reasoning']
        
        gramatical_correctness = properties['gramatical_correctness']
        spelling = properties['spelling']
        punctuation = properties['punctuation']
        capitalization = properties['capitalization']
        word_choice = properties['word_choice']
        sentence_structure = properties['sentence_structure']
        rest_of_sentence = properties['rest_of_sentence']
        
        # Convert the results to integer, with default value of 1
        gramatical_correctness = int(gramatical_correctness) if int(gramatical_correctness) in range(1, 6) else 1
        spelling = int(spelling) if int(spelling) in range(1, 6) else 1
        punctuation = int(punctuation) if int(punctuation) in range(1, 6) else 1
        capitalization = int(capitalization) if int(capitalization) in range(1, 6) else 1
        word_choice = int(word_choice) if int(word_choice) in range(1, 6) else 1
        sentence_structure = int(sentence_structure) if int(sentence_structure) in range(1, 6) else 1
        rest_of_sentence = int(rest_of_sentence) if int(rest_of_sentence) in range(1, 6) else 1
        
        unknown_word = unknownWords.filter(word=word).first()
        
        word_score = WordScore.objects.create(
            word=word,
            gramatical_correctness=gramatical_correctness,
            spelling=spelling,
            punctuation=punctuation,
            capitalization=capitalization,
            word_choice=word_choice,
            sentence_structure=sentence_structure,
            rest_of_sentence=rest_of_sentence,
            reasoning=reasoning,
            unknownWord=unknown_word
        )
        word_score.save()
        word_scores.append(word_score)
        
        logger.info(f"Word score saved for word {word} for user {email}")
    
    return word_scores
    
    
    
    