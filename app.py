# app.py
from datetime import datetime
import logging
import uuid
from flask import Flask
from routes import *
import argparse
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask import jsonify, request
from langchain_utils import chain, score_chain

load_dotenv()

app = Flask(__name__)

CONVERSATION_DB = os.getenv("CONVERSATION_DB")
CONVERSATION_DB_USER = os.getenv("CONVERSATION_DB_USER")
CONVERSATION_DB_PASSWORD = os.getenv("CONVERSATION_DB_PASSWORD")
CONVERSATION_DB_HOST = os.getenv("CONVERSATION_DB_HOST")
CONVERSATION_DB_PORT = os.getenv("CONVERSATION_DB_PORT")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{CONVERSATION_DB_USER}:{CONVERSATION_DB_PASSWORD}@{CONVERSATION_DB_HOST}:{CONVERSATION_DB_PORT}/{CONVERSATION_DB}"
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    sender_email = db.Column(db.String(255), nullable=False)
    sender_type = db.Column(db.String(10), nullable=False)  # 'bot' or 'human'
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    message_text = db.Column(db.Text, nullable=False)
    conversation_id = db.Column(db.String(255), db.ForeignKey('conversation.id'), nullable=False)

class Conversation(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='conversation', lazy=True)
    
# Create tables if they do not exist
with app.app_context():
    db.create_all()


@app.route("/model/api/chat", methods=["GET", "POST"])
def chat_route():
    json_content = request.json
    user_prompt = json_content.get("prompt", None)
    user_email = json_content.get("email", None)
    
    if user_prompt and user_email:
        # Check if the conversation already exists
        conversation = Conversation.query.filter_by(id=user_email).first()

        if conversation:
            # Retrieve the conversation and pass it to the LLM chain as context
            context = "\n".join([message.sender_type + ": " + message.message_text for message in conversation.messages])
            res = chain.invoke({"prompt": user_prompt, "context": context})

            # Add user message to the conversation
            user_message = Message(id=str(uuid.uuid4()), sender_email=user_email, sender_type="human", message_text=user_prompt, conversation=conversation)
            db.session.add(user_message)

            # Add bot message to the conversation
            bot_answer = str(res).strip()
            bot_message = Message(id=str(uuid.uuid4()), sender_email="bot", sender_type="bot", message_text=bot_answer, conversation=conversation)
            db.session.add(bot_message)

            db.session.commit()
            prompt_response_dict = {
                "data": {
                    "prompt": user_prompt,
                    "answer": bot_answer
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": 200,
                "msg": "Success"
            }
            return jsonify(prompt_response_dict), 200
        else:
            # Create a new conversation and add user and bot messages
            conversation = Conversation(id=user_email)
            db.session.add(conversation)

            # Add user message to the conversation
            user_message = Message(id=str(uuid.uuid4()), sender_email=user_email, sender_type="human", message_text=user_prompt, conversation=conversation)
            print(f'User message id: {user_message.id}')
            db.session.add(user_message)
            print(f'User message id: {user_message.id}')
            
            # Get the answer from the chain
            res = chain.invoke({"prompt": user_prompt, "context": "No previous chat history."})

            # Add bot message to the conversation
            bot_answer = str(res).strip()
            bot_message = Message(id=str(uuid.uuid4()), sender_email="bot", sender_type="bot", message_text=bot_answer, conversation=conversation)
            print(f'Bot message id: {user_message.id}')
            db.session.add(bot_message)
            print(f'User message id: {user_message.id}')

            db.session.commit()
        
            prompt_response_dict = {
                "data": {
                    "prompt": user_prompt,
                    "answer": bot_answer
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": 200,
                "msg": "Success"
            }
            return jsonify(prompt_response_dict), 200
    else:
        if not user_prompt:
            prompt_response_dict = {
                "status": 400,
                "msg": "No user prompt received",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify(prompt_response_dict), 400
        elif not user_email:
            prompt_response_dict = {
                "status": 400,
                "msg": "No user email received",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify(prompt_response_dict), 400
        else:
            prompt_response_dict = {
                "status": 500,
                "msg": "Unknown error occurred. Please report to the administrator.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify(prompt_response_dict), 500


@app.route("/model/api/score", methods=["POST"])
def score_route():
    json_content = request.json
    user_prompt = json_content.get("prompt", None)
    word_to_check = json_content.get("word", None)

    if user_prompt and word_to_check:

        res = score_chain.invoke({"input": user_prompt})

        prompt_response_dict = {
            "data": {
                "prompt": user_prompt,
                "answer": res
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": 200,
            "msg": "Success"
        }
        return jsonify(prompt_response_dict), 200
    else:
        if not user_prompt:
            msg = "No user prompt received"
            status = 400
        elif not word_to_check:
            msg = "No word to be checked received"
            status = 400
        else:
            msg = "Unknown error occurred. Please report to the administrator."
            status = 500

        prompt_response_dict = {
            "status": status,
            "msg": msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return jsonify(prompt_response_dict), status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5110, help="Port to run the API on. Defaults to 5110.")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the UI on. Defaults to 127.0.0.1. "
        "Set to 0.0.0.0 to make the UI externally "
        "accessible from other devices.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    app.run(debug=False, host=args.host, port=args.port)

