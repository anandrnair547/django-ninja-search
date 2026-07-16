[![PyPI version](https://img.shields.io/pypi/v/django-ninja-search.svg)](https://pypi.org/project/django-ninja-search/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-search.svg)](https://pypi.org/project/django-ninja-search/)
[![Build](https://github.com/anandrnair547/django-ninja-search/actions/workflows/test.yml/badge.svg)](https://github.com/anandrnair547/django-ninja-search/actions)
[![codecov](https://codecov.io/gh/anandrnair547/django-ninja-search/branch/main/graph/badge.svg)](https://codecov.io/gh/anandrnair547/django-ninja-search)
[![License](https://img.shields.io/github/license/anandrnair547/django-ninja-search.svg)](https://github.com/anandrnair547/django-ninja-search/blob/main/LICENSE)

# django-ninja-search

A lightweight decorator to add filtering, searching, and sorting support to Django Ninja view functions.

---

## ✨ Features

* Multi-term substring search (`?search=`) with a decorator — each term must match (AND, default) or any term may match (`search_mode="or"`), across any of the configured fields (OR, `icontains`)
* Safe, allowlisted ordering (`?ordering=`) with comma-separated multi-field and `-` descending support
* Optional filtering via `ninja.FilterSchema`
* `search`, `ordering`, and `filters` show up in the OpenAPI schema / interactive docs
* Works seamlessly with Django ORM and Django Ninja

---

## 📦 Installation

```bash
pip install django-ninja-search
```

Or with Poetry:

```bash
poetry add django-ninja-search
```

---

## 🚀 Usage

### 1. Define your model (example)

```python
# models.py
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
```

### 2. Add the decorator to your view

```python
# views.py
from ninja import FilterSchema
from ninja_search import searching


class ItemFilterSchema(FilterSchema):
    name: str | None = None  # exact-match filter, e.g. /?name=Banana


@api.get("/items", response=list[ItemSchema])
@searching(
    filter_schema=ItemFilterSchema,  # optional
    search_fields=["name", "description"],
    sort_fields=["name", "description"],
)
def list_items(request):
    return Item.objects.all()
```

This enables:

* `/?search=yellow banana` → rows where **every** term matches `name` or `description` (case-insensitive substring)
* `/?ordering=name` or `/?ordering=-name,description` → sorts results (only fields in `sort_fields` are accepted; anything else falls back to the default ordering)
* `/?name=Banana` → filtering via your `FilterSchema`

Notes:

* The decorated view must return a `QuerySet` (or a `(status, QuerySet)` tuple).
* `filter_schema` must subclass `ninja.FilterSchema` — a plain `ninja.Schema` has no `.filter()` and is rejected with a `TypeError` at import time.
* When no `?ordering=` is given (or the value is invalid), results are ordered by `sort_fields` as declared, so pagination stays stable.
* Related fields work with dot notation (`"author.name"`); searches across to-many relations are de-duplicated automatically.
* At most 10 search terms are applied per request (`ninja_search.MAX_SEARCH_TERMS`).
* Pass `search_mode="or"` to match rows containing *any* term instead of all terms (the 0.1.x behavior).

### Upgrading from 0.1.x / 0.2.0 (breaking changes in 0.3.0)

See the [Migration Guide](MIGRATION.md) for before/after examples. Summary:

* `filterSchema=` is deprecated — use `filter_schema=`. It must now be a `ninja.FilterSchema` subclass; with plain `Schema` classes filtering silently did nothing.
* Multi-term search now ANDs terms (`?search=red apple` no longer matches rows that only contain "red").
* Single-character search terms are no longer ignored.
* Views no longer need to declare a `filters` parameter — the decorator adds it (plus `search` and `ordering`) to the endpoint signature automatically.

---

## 🧪 Running Tests

```bash
poetry install
poetry run pytest --cov=ninja_search --cov-report=html
```

Open the coverage report in your browser:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 📤 Publishing

### ✅ Publish to Test PyPI

```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish --build -r testpypi
```

### 🚀 Publish to PyPI

```bash
poetry config repositories.pypi https://upload.pypi.org/legacy/
poetry config pypi-token.pypi <your-token-here>
poetry publish --build -r pypi
```

---

## 🔁 Versioning and Release

Before releasing a new version:

```bash
poetry version patch  # or minor / major
poetry build
# Publish using one of the methods above

# Tag and push
NEW_VERSION=$(poetry version -s)
git tag v$NEW_VERSION
git push origin v$NEW_VERSION
git push origin main
```

---

## 📚 Metadata & Compatibility

**Python Versions:** 3.10, 3.11, 3.12, 3.13, 3.14
**Django Versions:** >=5.1, <7.0
**Django Ninja Versions:** >=1.4.3, <2.0
**License:** MIT
**Project URL:** [https://github.com/anandrnair547/django-ninja-search](https://github.com/anandrnair547/django-ninja-search)
**PyPI:** [https://pypi.org/project/django-ninja-search/](https://pypi.org/project/django-ninja-search/)

---

## 🤝 Contributing

We welcome contributions! See the [Contributing Guide](https://github.com/anandrnair547/django-ninja-search/blob/main/CONTRIBUTING.md) for setup instructions, test coverage tips, release workflow, and versioning guidance.

---

## 🧾 License

MIT © [Anand R Nair](https://github.com/anandrnair547)


## AI Development Setup (Optional)

This repo uses an `agent-setup` submodule — a shared AI agent framework with agents, workflows, and skills for Claude Code, Cursor, Copilot, and other AI tools.

After cloning, initialize it if you use AI-assisted development:

```bash
git submodule update --init --recursive
```

This is **optional** — the submodule is only needed for AI tooling. The app runs fine without it.

To pull the latest agent framework updates:

```bash
git submodule update --remote agent-setup
```
