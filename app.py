# app.py
from datetime import datetime
import logging
from flask import Flask
from routes import *
import argparse


app = Flask(__name__)

@app.route("/model/api/chat", methods=["GET", "POST"])
def chat_route():
    json_content = request.json
    user_prompt = json_content.get("prompt", None)
    user_email = json_content.get("email", None)
    
    prompt_response_dict = {
        "data": {
            "prompt": user_prompt,
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    if user_prompt and user_email:
        # Get the answer from the chain
        res = chain.run(user_prompt)
        answer = str(res).strip()
        
        # Append the answer to the response dict of data key
        prompt_response_dict["data"]["answer"] = answer
        prompt_response_dict["status"] = 200
        prompt_response_dict["msg"] = "Success"
        return jsonify(prompt_response_dict), 200
    else:
        prompt_response_dict["status"] = 400
        prompt_response_dict["msg"] = "No user prompt received"
        return jsonify(prompt_response_dict), 400
        

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

