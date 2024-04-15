
# GET PROJECT_MODE from environment variable
import os

USER_SERVICE_BASE_PATH = os.getenv('USER_SERVICE_BASE_PATH', None)
USER_SERVICE_SELECT_WORD_PATH = USER_SERVICE_BASE_PATH + "/wordbank/select"