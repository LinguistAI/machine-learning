# helpers.py
import os
import shutil
import subprocess
from flask import jsonify
from werkzeug.utils import secure_filename
from constants import PERSIST_DIRECTORY, DEVICE_TYPE
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Chroma
from run_localGPT import load_model
from prompt_template_utils import get_prompt_template
from langchain.chains import RetrievalQA

def prompt():
    global QA
    user_prompt = request.form.get("user_prompt")
    if user_prompt:
        res = QA(user_prompt)
        answer, docs = res["result"]

        prompt_response_dict = {
            "Prompt": user_prompt,
            "Answer": answer,
        }
        return jsonify(prompt_response_dict), 200
    else:
        return "No user prompt received", 400
