from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime

@api_view(['GET'])
def ping(request):
    prompt_response_dict = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": 200,
        "msg": "Success"
    }
    return Response(prompt_response_dict, status=200)
