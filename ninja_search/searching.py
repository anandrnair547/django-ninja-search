# ninja_search/searching.py

import functools
import re
from typing import List
from django.db.models import Q, QuerySet
from ninja import Query


def searching(
    *, filterSchema, search_fields: List[str] = [], sort_fields: List[str] = []
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, filters: filterSchema = Query(None), *args, **kwargs):
            result = func(request, *args, **kwargs)
            queryset = result if isinstance(result, QuerySet) else result[0]

            search_term = request.GET.get("search", "")
            sort_term = request.GET.get("ordering", "")

            if search_term:
                search_terms = [
                    term for term in re.split(r"\s+", search_term) if len(term) > 1
                ]
                queries = [
                    Q(**{field + "__icontains": term})
                    for term in search_terms
                    for field in search_fields
                ]
                queryset = queryset.filter(
                    functools.reduce(lambda x, y: x | y, queries)
                )

            if sort_term and sort_term in sort_fields:
                queryset = queryset.order_by(sort_term)

            return queryset

        return wrapper

    return decorator
