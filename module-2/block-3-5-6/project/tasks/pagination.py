"""
Custom DRF pagination class for the Task Manager domain.

Produces the exact envelope required by the spec:

    {
        "tasks": [...],
        "pagination": {"page": 1, "limit": 5, "total": 12, "pages": 3}
    }

Uses `page` (default 1) and `limit` (default 5) query params, both integers.
"""
from rest_framework.pagination import BasePagination
from rest_framework.response import Response

from django.core.paginator import Paginator, InvalidPage


class TaskPagination(BasePagination):
    page_query_param = 'page'
    limit_query_param = 'limit'
    page_size = 5
    max_page_size = 100
    default_limit = 5

    def paginate_queryset(self, queryset, request, view=None):
        # Read & validate `page` and `limit` as integers.
        page_num = self._get_int(request, self.page_query_param, 1)
        limit = self._get_int(request, self.limit_query_param, self.default_limit)

        if limit < 1:
            limit = self.default_limit
        if limit > self.max_page_size:
            limit = self.max_page_size

        paginator = Paginator(queryset, limit)
        total = paginator.count
        pages = paginator.num_pages

        # Clamp the requested page into bounds.
        if page_num < 1:
            page_num = 1
        if page_num > pages:
            page_num = pages if pages > 0 else 1

        try:
            page = paginator.page(page_num)
        except InvalidPage:
            page = paginator.page(1) if pages > 0 else paginator.page(1)

        self.page_obj = page
        self.pagination_meta = {
            'page': page_num,
            'limit': limit,
            'total': total,
            'pages': pages,
        }
        return list(page.object_list)

    def get_paginated_response(self, data):
        return Response({'tasks': data, 'pagination': self.pagination_meta})

    def get_paginated_response_schema(self, schema):
        return schema

    def _get_int(self, request, param, default):
        raw = request.query_params.get(param)
        if raw is None or raw == '':
            return default
        try:
            return int(raw)
        except (TypeError, ValueError):
            return default
