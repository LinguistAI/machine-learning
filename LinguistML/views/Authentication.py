from rest_framework import permissions

from constants.header_constants import HEADER_USER_EMAIL

class IsAuthenticatedByHeader(permissions.BasePermission):
    """
    Custom permission to check for user email in the headers.
    """
    def has_permission(self, request, view):
        return request.headers.get(HEADER_USER_EMAIL) is not None
