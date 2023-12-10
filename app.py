# app.py
import logging
from flask import Flask
from routes import *
import argparse

app = Flask(__name__)

@app.route("/api/prompt_route2", methods=["GET", "POST"])
def prompt_route2():
    user_prompt = request.form.get("user_prompt")
    if user_prompt:
        # Get the answer from the chain
        res = chain.run(user_prompt)
        answer = res

        prompt_response_dict = {
            "Prompt": user_prompt,
            "Answer": answer,
        }

        return jsonify(prompt_response_dict), 200
    else:
        return "No user prompt received", 400

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5110, help="Port to run the API on. Defaults to 5110.")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the UI on. Defaults to 127.0.0.1. "
        "Set to 0.0.0.0 to make the UI externally "
        "accessible from other devices.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    app.run(debug=False, host=args.host, port=args.port)

