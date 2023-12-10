# routes.py
from flask import jsonify, request
from app import app
from langchain_utils import chain

@app.route("/api/prompt_route", methods=["GET", "POST"])
def prompt_route():
    user_prompt = request.form.get("user_prompt")
    if user_prompt:
        # print(f'User Prompt: {user_prompt}')
        # Get the answer from the chain
        res = chain.run(user_prompt)
        answer = res["result"]

        prompt_response_dict = {
            "Prompt": user_prompt,
            "Answer": answer,
        }

        return jsonify(prompt_response_dict), 200
    else:
        return "No user prompt received", 400