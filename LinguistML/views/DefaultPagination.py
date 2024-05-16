from chat.serializers import MessageSerializer
from utils.http_utils import generate_success_response
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DefaultPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'pageSize'
    page_query_param = 'page'
    max_page_size = 10

    def get_paginated_response(self, data):

        first = not self.page.has_previous()
        last = not self.page.has_next()
        number = self.page.number
        total_pages = self.page.paginator.num_pages
        total_elements = self.page.paginator.count
        size = self.get_page_size(self.request)
        number_of_elements = len(data)
        empty = number_of_elements == 0

        return generate_success_response("Data retrieved successfully", {
            'content': data,
            'pageable': {
                'sort': {
                    'sorted': self.request.query_params.get('ordering', None) is not None,
                    'unsorted': self.request.query_params.get('ordering', None) is None,
                    'empty': self.request.query_params.get('ordering', None) is None,
                },
                'offset': self.page.start_index(),
                'pageNumber': number,
                'pageSize': size,
                'paged': True,
                'unpaged': False,
            },
            'last': last,
            'totalPages': total_pages,
            'totalElements': total_elements,
            'size': size,
            'number': number,
            'sort': {
                'sorted': self.request.query_params.get('ordering', None) is not None,
                'unsorted': self.request.query_params.get('ordering', None) is None,
                'empty': self.request.query_params.get('ordering', None) is None,
            },
            'first': first,
            'numberOfElements': number_of_elements,
            'empty': empty
        })
