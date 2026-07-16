import functools
import inspect
import operator
import warnings
from collections.abc import Callable, Sequence
from typing import Any, Literal

from django.db.models import Q, QuerySet
from ninja import FilterSchema, Query

# Hard cap on the number of whitespace-separated search terms applied per
# request, so a crafted ?search= value cannot grow the WHERE clause unbounded.
MAX_SEARCH_TERMS = 10

View = Callable[..., Any]


def _normalize(fields: Sequence[str]) -> list[str]:
    """Convert dot-notation to Django's double-underscore."""
    return [f.replace(".", "__") for f in fields]


def searching(
    *,
    filter_schema: type[FilterSchema] | None = None,
    search_fields: Sequence[str] | None = None,
    sort_fields: Sequence[str] | None = None,
    search_mode: Literal["and", "or"] = "and",
    filterSchema: type[FilterSchema] | None = None,  # noqa: N803
) -> Callable[[View], View]:
    """Add ``?search=``, ``?ordering=`` and FilterSchema filtering to a view.

    The decorated view must return a ``QuerySet`` or a ``(status, QuerySet)``
    tuple. ``search`` matches every whitespace-separated term (AND, or any
    term with ``search_mode="or"``) against any of ``search_fields`` (OR,
    ``__icontains``). ``ordering`` accepts a
    comma-separated list of ``sort_fields`` entries, each optionally prefixed
    with ``-``; invalid values fall back to the default ordering
    (``sort_fields`` as declared). ``filter_schema`` must be a
    ``ninja.FilterSchema`` subclass; if the view does not declare a
    ``filters`` parameter itself, one is added to its exposed signature so
    Django Ninja parses and documents it.
    """
    if search_mode not in ("and", "or"):
        raise ValueError(f'search_mode must be "and" or "or", got {search_mode!r}')
    if filterSchema is not None:
        warnings.warn(
            "searching(filterSchema=...) is deprecated; use filter_schema=...",
            DeprecationWarning,
            stacklevel=2,
        )
        if filter_schema is None:
            filter_schema = filterSchema

    search_fields = _normalize(search_fields or [])
    default_order = tuple(_normalize(sort_fields or []))
    allowed_sort = {f.removeprefix("-") for f in default_order}
    needs_distinct = any("__" in f for f in search_fields)

    def decorator(func: View) -> View:
        if filter_schema is not None and not (
            isinstance(filter_schema, type) and issubclass(filter_schema, FilterSchema)
        ):
            raise TypeError(
                f"@searching on view '{func.__name__}': filter_schema must be a "
                "ninja.FilterSchema subclass; plain ninja.Schema has no "
                ".filter() and cannot filter querysets"
            )

        sig = inspect.signature(func)
        own_params = set(sig.parameters)

        @functools.wraps(func)
        def wrapper(request: Any, *args: Any, **kwargs: Any) -> Any:
            # Params we appended to __signature__ are ours to consume; params
            # the view declared itself are read but left for the view. Direct
            # calls (plain Django, tests) fall back to request.GET.
            def param(name: str) -> str:
                value = (
                    kwargs.get(name) if name in own_params else kwargs.pop(name, None)
                )
                return value or request.GET.get(name, "")

            search_term = param("search")
            sort_term = param("ordering")
            if "filters" in own_params:
                filters = kwargs.get("filters")
            else:
                filters = kwargs.pop("filters", None)

            result = func(request, *args, **kwargs)
            if isinstance(result, QuerySet):
                has_status, status, queryset = False, None, result
            elif (
                isinstance(result, tuple)
                and len(result) == 2
                and isinstance(result[1], QuerySet)
            ):
                has_status, (status, queryset) = True, result
            else:
                raise TypeError(
                    f"@searching view '{func.__name__}' must return a QuerySet "
                    f"or a (status, QuerySet) tuple, got {type(result).__name__}"
                )

            # --- search: AND (default) or OR across terms, OR across fields ---
            # AND uses one .filter() call per term: a single combined filter
            # would reuse one JOIN for to-many relations, wrongly requiring
            # every term to match the same related row.
            terms = search_term.split()[:MAX_SEARCH_TERMS]
            if terms and search_fields:
                term_qs = []
                for term in terms:
                    term_q = Q()
                    for field in search_fields:
                        term_q |= Q(**{f"{field}__icontains": term})
                    term_qs.append(term_q)
                if search_mode == "or":
                    queryset = queryset.filter(functools.reduce(operator.or_, term_qs))
                else:
                    for term_q in term_qs:
                        queryset = queryset.filter(term_q)
                if needs_distinct:
                    queryset = queryset.distinct()

            # --- ordering: allowlisted, comma-separated, else default ---
            order = default_order
            if sort_term:
                parts = tuple(
                    p.replace(".", "__")
                    for p in (s.strip() for s in sort_term.split(","))
                    if p
                )
                if parts and all(p.removeprefix("-") in allowed_sort for p in parts):
                    order = parts
            if order:
                queryset = queryset.order_by(*order)

            # --- filtering ---
            if isinstance(filters, FilterSchema):
                queryset = filters.filter(queryset)

            return (status, queryset) if has_status else queryset

        # functools.wraps sets __wrapped__, and both Django Ninja and
        # inspect.signature() resolve the ORIGINAL view signature through it —
        # so search/ordering/filters must be spliced into an explicit
        # __signature__ (which takes precedence) to be parsed and documented.
        extra = []
        if "search" not in own_params:
            extra.append(
                inspect.Parameter(
                    "search",
                    inspect.Parameter.KEYWORD_ONLY,
                    default=Query(""),
                    annotation=str,
                )
            )
        if "ordering" not in own_params:
            extra.append(
                inspect.Parameter(
                    "ordering",
                    inspect.Parameter.KEYWORD_ONLY,
                    default=Query(""),
                    annotation=str,
                )
            )
        if filter_schema is not None and "filters" not in own_params:
            extra.append(
                inspect.Parameter(
                    "filters",
                    inspect.Parameter.KEYWORD_ONLY,
                    default=Query(...),
                    annotation=filter_schema,
                )
            )
        if extra:
            params = list(sig.parameters.values())
            var_kw = [p for p in params if p.kind is inspect.Parameter.VAR_KEYWORD]
            rest = [p for p in params if p.kind is not inspect.Parameter.VAR_KEYWORD]
            wrapper.__signature__ = sig.replace(parameters=rest + extra + var_kw)

        return wrapper

    return decorator
