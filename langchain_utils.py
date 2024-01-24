# langchain_utils.py
from operator import itemgetter
import torch
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_experimental.chat_models import Llama2Chat
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain_community.llms import LlamaCpp
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
import logging
import os

from dotenv import load_dotenv

from constants import MODELS_PATH

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

model_path = f"{MODELS_PATH}/mistral-7b-v0.1.Q4_0.gguf"

# Check if path exists
print(f"Model path: {model_path}. Model is found?: {os.path.exists(model_path)}")

llm = LlamaCpp(
    model_path=model_path,
    streaming=False,
    n_ctx=4096,
    n_batch=10,
)
model = Llama2Chat(llm=llm, MAX_NEW_TOKENS=4096)

# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt = ChatPromptTemplate.from_template(prompt_template)
chain = LLMChain(
    llm=model,
    prompt=prompt)

score_prompt_template = """
Task:
Evaluate how well the word "{word}" is used in the user's message, assigning a score between 0 and 10 based on English language rules. 
Consider context, grammar, and appropriateness.

User Message:
"{user_prompt}"

Scoring Guidelines:

10: Outstanding usage; the word seamlessly blends into the sentence, showcasing a profound understanding of its context.
8-9: Excellent usage; the word harmonizes well with the sentence, with only minor room for enhancement.
6-7: Good usage; the word is generally fitting, but there might be some potential for clarification or improvement.
4-5: Adequate usage; the word is used, but there are notable issues with context, grammar, or appropriateness.
2-3: Insufficient usage; there are significant problems with how the word is integrated into the sentence.
0-1: Poor usage; the word is either entirely out of place or used in a confusing or incorrect manner.

"""

"""
# Output parser: (needs {format_instructions} in the prompt
class Score(BaseModel):
    score: str = Field(description="score given to the word")
    reason: str = Field(description="the reasoning for the given score")


parser = PydanticOutputParser(pydantic_object=Score)

score_prompt = PromptTemplate(
    template=score_prompt_template,
    input_variables=["user_prompt", "word"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

score_chain = score_prompt | model | parser
"""

score_prompt = ChatPromptTemplate.from_template(score_prompt_template)
score_chain = score_prompt | model | StrOutputParser()
