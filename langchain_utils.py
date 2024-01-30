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
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate

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


examples = [
    {
        "question": "What is the score of the word 'are' in 'How are you?'",
        "answer": """
            Are follow up questions needed here: Yes.
            Follow up: How well is the word 'are' used in the given sentence? 
            Intermediate answer: Very well.
            So the final answer is: 10
            """,
    },
    {
        "question": "What is the score of the word 'faith' in 'Get some faith please?'",
        "answer": """
                Are follow up questions needed here: Yes.
                Follow up: How well is the word 'faith' used in the given sentence? 
                Intermediate answer: Not well, meaning can be understood but the usage is not colloquial. 
                So the final answer is: 4
                """,
    },
    {
        "question": "What is the score of the word 'help' in 'My dog eats help'?",
        "answer": """
                Are follow up questions needed here: Yes.
                Follow up: How well is the word 'help' used in the given sentence? 
                Intermediate answer: Not well. The usage is not correct.
                So the final answer is: 0
                """,
    },
]

example_prompt = PromptTemplate(
    input_variables=["question", "answer"], template="Question: {question}\n{answer}"
)

print(example_prompt.format(**examples[0]))

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question: {input}",
    input_variables=["input"],
)

score_prompt_template = """
Task:
Evaluate how well the word "{word}" is used in the user's message, assigning a score between 0 and 10 based on English language rules. 
Consider context, grammar, and appropriateness.

User Message:
"{user_prompt}"

Return only the score and nothing else:

Examples:

Score 0: The use of "{word}" is entirely inappropriate, violating fundamental language rules and hindering comprehension.
Score 1: Incoherent use of "{word}" disrupts the sentence structure, leading to confusion or lack of clarity.
Score 4: "{word}" is used, but there are notable issues in grammar and appropriateness, impacting the overall effectiveness.
Score 7: The use of "{word}" aligns with basic language rules but may have minor issues such as ambiguous context or suboptimal placement.
Score 10: "{word}" is seamlessly integrated, showcasing a deep understanding of language rules, enhancing clarity, and contributing significantly to the message's quality.
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

# score_prompt = ChatPromptTemplate.from_template(score_prompt_template)
score_chain = few_shot_prompt | model | StrOutputParser()
