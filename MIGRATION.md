# Migration Guide

## 0.1.x / 0.2.0 → 0.3.0

> **Note:** 0.2.0 on PyPI behaves identically to 0.1.9 — the changes below
> all land in 0.3.0. If you are on either, this guide applies.

0.3.0 is a rewrite of the `@searching` decorator. Filtering previously
did nothing (silently) unless you wired it exactly right, ordering could
crash with a 500, and none of the parameters appeared in your OpenAPI
docs. Fixing that required a few breaking changes.

### 1. `filterSchema=` → `filter_schema=`, and it must be a `ninja.FilterSchema`

`filterSchema=` still works but emits a `DeprecationWarning`. The real
change: the class must subclass `ninja.FilterSchema`. Plain `ninja.Schema`
has no `.filter()` method — in 0.1.x/0.2.0 that meant filtering **silently
did nothing**; 0.3.0 raises `TypeError` at import time instead.

**Before**

```python
from ninja import Schema
from ninja_search.searching import searching

class ItemFilterSchema(Schema):
    pass  # filtering never actually worked with this

@searching(
    filterSchema=ItemFilterSchema,
    search_fields=["name", "description"],
    sort_fields=["name"],
)
def list_items(request, filters: ItemFilterSchema = Query(...)):
    return Item.objects.all()
```

**After**

```python
from ninja import FilterSchema
from ninja_search import searching  # top-level import now available

class ItemFilterSchema(FilterSchema):
    name: str | None = None  # /?name=Banana

@searching(
    filter_schema=ItemFilterSchema,
    search_fields=["name", "description"],
    sort_fields=["name"],
)
def list_items(request):
    return Item.objects.all()
```

### 2. Drop the `filters` parameter from your views (optional)

The decorator now injects `filters` (plus `search` and `ordering`) into
the endpoint signature itself, so Django Ninja parses and documents them
without you declaring anything.

Keeping an explicit `filters: MyFilter = Query(...)` parameter still
works — and unlike before, your view body now receives the **parsed
schema instance** (previously it received a useless `Query` FieldInfo
default, and views declaring `filters` without a default raised
`TypeError` on every request).

### 3. Multi-term search is now AND, not OR

`?search=red apple` previously matched rows containing *either* term.
Now every term must match at least one of `search_fields`.

If your clients rely on OR behavior, keep it with one kwarg:

```python
@searching(search_fields=["name", "description"], search_mode="or")
```

Related changes:

- Single-character terms are no longer dropped. `?search=a` used to
  return the **entire unfiltered table**; now it filters like any term.
- At most 10 terms are applied per request
  (`ninja_search.MAX_SEARCH_TERMS`); extra terms are ignored.
- Searches spanning to-many relations (e.g. `search_fields=["tags.label"]`)
  are de-duplicated automatically, and different terms may match
  different related rows.

### 4. Ordering is stricter — and no longer crashes

- `?ordering=--name` returned HTTP 500 in 0.1.x/0.2.0. Now any value not
  in `sort_fields` falls back to the default ordering.
- Invalid ordering used to leave results **unordered** (breaking stable
  pagination); now it falls back to the default ordering
  (`sort_fields` as declared).
- New: comma-separated multi-field ordering — `?ordering=name,-created_at`.
- New: descending defaults — `sort_fields=["-created_at"]` sorts newest
  first when no `?ordering=` is given; clients may still request either
  direction of the bare field name.

### 5. Return-value contract is enforced

Views must return a `QuerySet` or a `(status, QuerySet)` tuple. Anything
else raises `TypeError`.

Previously a `(status, queryset)` return was silently mangled (the
decorator operated on the status code and dropped your queryset); lists
and dicts misbehaved in similar ways. Tuples now work correctly — status
preserved, queryset searched/sorted/filtered.

### 6. OpenAPI

`search`, `ordering`, and your filter fields now appear in the generated
OpenAPI schema and interactive docs. If you post-process your schema,
expect the new parameters.

### Checklist

- [ ] Replace `filterSchema=` with `filter_schema=`
- [ ] Make filter classes subclass `ninja.FilterSchema` and declare fields
- [ ] Remove `filters` params from views that don't use them
- [ ] Verify clients don't depend on OR multi-term search
- [ ] Verify clients don't rely on invalid `?ordering=` leaving results unordered
- [ ] Ensure views return `QuerySet` or `(status, QuerySet)`
