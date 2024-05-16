from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime

from constants.header_constants import HEADER_USER_EMAIL


def generate_error_response(status_code: int, message: str, data: dict = None):
    """
    Generate a custom error response
    """
    
    custom_response_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status_code,
        "msg": message
    }
    
    if data is not None:
        custom_response_data["data"] = data
    
    return Response(custom_response_data, status=status_code)


def generate_success_response(message: str, data: dict):
    """
    Generate a custom success response
    """
    custom_response_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 200,
        "msg": message
    }
    
    if data is not None:
        custom_response_data["data"] = data
    
    return Response(custom_response_data, status=200)


def validate_request(request, required_data=None):
    """Validate the request for authentication and required data."""
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    if required_data:
        for field in required_data:
            if not request.data or field not in request.data:
                return generate_error_response(400, f"{field.capitalize()} is required")

    return None  # No validation errors