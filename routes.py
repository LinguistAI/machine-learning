# routes.py
from flask import jsonify, request
from app import app
from langchain_utils import QA

@app.route("/api/prompt_route", methods=["GET", "POST"])
def prompt_route():
    pass
