
# GET PROJECT_MODE from environment variable
import os

USER_SERVICE_BASE_PATH = os.getenv('USER_SERVICE_BASE_PATH', None)

# Remove the last '/' character if exists
if USER_SERVICE_BASE_PATH.endswith('/'):
    USER_SERVICE_BASE_PATH = USER_SERVICE_BASE_PATH[:-1]

USER_SERVICE_SELECT_WORD_PATH = USER_SERVICE_BASE_PATH + "/wordbank/select"
USER_SERVICE_INCREASE_CONFIDENCE_PATH = USER_SERVICE_BASE_PATH + "/wordbank/increase-confidence"
USER_SERVICE_DECREASE_CONFIDENCE_PATH = USER_SERVICE_BASE_PATH + "/wordbank/decrease-confidence"
USER_SERVICE_XP_MESSAGE_PATH = USER_SERVICE_BASE_PATH + "/user-xp/message"
