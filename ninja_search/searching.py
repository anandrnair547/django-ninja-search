import functools
import re
from typing import List
from django.db.models import Q, QuerySet
from ninja import Query


def _normalize(fields: List[str]) -> List[str]:
    """Convert dot-notation to Django’s double-underscore."""
    return [f.replace(".", "__") for f in fields]


def searching(
    *,
    filterSchema,
    search_fields: List[str] | None = None,
    sort_fields: List[str] | None = None,
):
    search_fields = _normalize(search_fields or [])
    sort_fields = _normalize(sort_fields or [])

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, filters: filterSchema = Query(None), *args, **kwargs):
            result = func(request, *args, **kwargs)
            queryset = result if isinstance(result, QuerySet) else result[0]

            search_term = request.GET.get("search", "")
            sort_term = request.GET.get("ordering", "")

            # --- full-text search ---
            if search_term:
                terms = [t for t in re.split(r"\\s+", search_term) if len(t) > 1]
                q_obj = functools.reduce(
                    lambda acc, q: acc | q,
                    (
                        Q(**{f + "__icontains": term})
                        for term in terms
                        for f in search_fields
                    ),
                )
                queryset = queryset.filter(q_obj)

            # --- ordering ---
            if sort_term:
                normalized = sort_term.replace(".", "__")
                if normalized.lstrip("-") in sort_fields:
                    queryset = queryset.order_by(normalized)

            # filtering
            if filters:
                queryset = filters.filter(queryset)

            return queryset

        return wrapper

    return decorator
