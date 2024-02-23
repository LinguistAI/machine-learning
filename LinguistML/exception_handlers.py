# your_app/exception_handlers.py

from rest_framework.views import exception_handler
from django.http import JsonResponse
from datetime import datetime

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first, to get the standard error response.
    response = exception_handler(exc, context)

    # Customize the response format.
    if response is not None:
        
        data = response.data
        
        if (response.data["detail"]):
            data = response.data["detail"]
        
        custom_response_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": response.status_code,
            "msg": "Error" if response.status_code != 200 else "Success",
            "data": data
        }
        response.data = custom_response_data

    return response


def custom_404_view(request, exception):
    print("custom_404_view")
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 404,
        "msg": "Not Found",
        "detail": "The requested resource was not found."
    }
    return JsonResponse(data, status=404)

def custom_500_view(request):
    print("custom_500_view")
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 500,
        "msg": "Server Error",
        "detail": "Internal server error."
    }
    return JsonResponse(data, status=500)



