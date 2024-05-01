from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from LinguistML.views.Authentication import IsAuthenticatedByHeader
from chat.models import Conversation, Message
from chat.serializers import MessageSerializer
from chat.views.MessageListView import MessageListView
from constants.header_constants import HEADER_USER_EMAIL

from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from constants.profile_constants import MAX_NO_OF_MESSAGE_CONTEXT
import logging
import rest_framework.request

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method="GET",
    operation_description="Get paginated messages for a conversation",
    operation_summary="Get paginated messages",
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY,
                          description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('pageSize', openapi.IN_QUERY,
                          description="Number of messages per page", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: openapi.Response(
            description="Paginated response",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Data retrieved successfully",
                    "data": {
                        # Example of serialized data
                        "content": [MessageSerializer().data],
                        "pageable": {
                            "sort": {"sorted": True, "unsorted": False, "empty": False},
                            "offset": 0,
                            "pageNumber": 1,
                            "pageSize": 5,
                            "paged": True,
                            "unpaged": False
                        },
                        "last": True,
                        "totalPages": 1,
                        "totalElements": 0,
                        "size": 5,
                        "number": 1,
                        "sort": {"sorted": True, "unsorted": False, "empty": False},
                        "first": True,
                        "numberOfElements": 0,
                        "empty": True
                    }
                }
            }
        ),
        400: openapi.Response(description="Bad request"),
        404: openapi.Response(description="Not found")
    }
)
@api_view(['GET'])
def get_conversation_messages(request: rest_framework.request.Request, conversation_id: str):
    # In order to have custom Swagger documentation, we needed this view.
    # however, this view uses rest_framework.request.Request instead of the standard Django request object
    # Convert REST request to Django request by accessing the Django _request object
    return MessageListView.as_view()(request._request, conversation_id=conversation_id)
