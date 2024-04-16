
# GET PROJECT_MODE from environment variable
import os

USER_SERVICE_BASE_PATH = os.getenv('USER_SERVICE_BASE_PATH', None)

# Remove the last '/' character if exists
if USER_SERVICE_BASE_PATH.endswith('/'):
    USER_SERVICE_BASE_PATH = USER_SERVICE_BASE_PATH[:-1]

USER_SERVICE_SELECT_WORD_PATH = USER_SERVICE_BASE_PATH + "/wordbank/select"