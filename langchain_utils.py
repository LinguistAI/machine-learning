# langchain_utils.py
from operator import itemgetter
import torch
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_experimental.chat_models import Llama2Chat
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.llms import LlamaCpp
import logging
import os

from dotenv import load_dotenv
load_dotenv()

# template_messages = [
#     SystemMessage(content="You are a helpful assistant."),
#     MessagesPlaceholder(variable_name="chat_history"),
#     HumanMessagePromptTemplate.from_template("{text}"),
# ]
# prompt_template = ChatPromptTemplate.from_messages(template_messages)
prompt_template = """
You are an AI language companion designed to assist English language learners at the A2 conversational level or higher. 
Your primary goal is to facilitate writing and speaking practice by engaging users in meaningful conversations. 
Your responses should include asking questions, introducing controversial or opposing ideas, 
and actively listening to users to ensure a smooth and continuous flow of conversation.
Keep the interaction focused on language learning, and adapt your prompts to maximize engagement and practice opportunities for the users.

The chat history is:
{context}

User has said:
{prompt}
"""

if torch.backends.mps.is_available():
    DEVICE_TYPE = "mps"
elif torch.cuda.is_available():
    DEVICE_TYPE = "cuda"
else:
    DEVICE_TYPE = "cpu"

# SHOW_SOURCES = True
logging.info(f"Running on: {DEVICE_TYPE}")
# logging.info(f"Display Source Documents set to: {SHOW_SOURCES}")

# model_path = os.getenv("MODEL_PATH")
# model_path = "./llama-2-7b-chat.Q4_0.gguf"

model_path = "/Users/tolgaozgun/models/llama-2-7b-chat.Q4_0.gguf"
# model_path = "/app/models/llama-2-7b-chat.Q4_0.gguf"

# Check if path exists
print(f"Model path: {model_path}. Model is found?: {os.path.exists(model_path)}")
# print(f'1- {os.listdir("/app/models")}')
# print(f'3- {os.listdir("/app")}')

llm = LlamaCpp(
    model_path=model_path,
    streaming=False,
    n_ctx=4096
)
model = Llama2Chat(llm=llm, MAX_NEW_TOKENS=4096)

# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt = ChatPromptTemplate.from_template(prompt_template)
chain = LLMChain(
    llm=model,
    prompt=prompt)
                 
    
