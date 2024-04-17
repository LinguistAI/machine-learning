from math import ceil

BACKEND_CONFIDENCE_LEVELS = [
    "LOWEST",
    "LOW",
    "MODERATE",
    "HIGH",
    "HIGHEST"
]

# Do not forget to update MaxValueValidator for UnknownWord.confidenceLevel if this value is changed
ML_CONFIDENCE_LEVEL_MAX = 100

# As the ml service has a bigger range for confidence, add scaling factor
CONFIDENCE_LEVEL_SCALING_FACTOR = ceil(ML_CONFIDENCE_LEVEL_MAX / len(BACKEND_CONFIDENCE_LEVELS))

ACTIVE_WORD_LIST_SIZE = 5

MCQ_TEST_QUESTION_PER_WORD = 1

INCREASE_CONFIDENCE_ON_CORRECT_MCQ_ANSWER = 1
DECREASE_CONFIDENCE_ON_WRONG_MCQ_ANSWER = 1