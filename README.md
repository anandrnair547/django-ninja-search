# django-ninja-search

[![PyPI version](https://img.shields.io/pypi/v/django-ninja-search.svg)](https://pypi.org/project/django-ninja-search/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-search.svg)](https://pypi.org/project/django-ninja-search/)
[![Build](https://github.com/anandrnair547/django-ninja-search/actions/workflows/test.yml/badge.svg)](https://github.com/anandrnair547/django-ninja-search/actions)
[![codecov](https://codecov.io/gh/anandrnair547/django-ninja-search/branch/main/graph/badge.svg)](https://codecov.io/gh/anandrnair547/django-ninja-search)
[![License](https://img.shields.io/github/license/anandrnair547/django-ninja-search.svg)](https://github.com/anandrnair547/django-ninja-search/blob/main/LICENSE)

A lightweight decorator to add filtering, searching, and sorting support to Django Ninja view functions.

---

## ✨ Features

* Add full-text search and ordering with a decorator
* Optional schema-based filtering
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
from ninja import Query
from ninja_schema import Schema
from django_ninja_search import searching

class ItemFilterSchema(Schema):
    pass  # You can define extra filters here if needed

@searching(
    filterSchema=ItemFilterSchema,
    search_fields=["name", "description"],
    sort_fields=["name", "description"],
)
def list_items(request, filters: ItemFilterSchema = Query(...)):
    return Item.objects.all()
```

This enables:

* `/?search=banana` → filters by search text
* `/?ordering=name` → sorts results

---

## 🧪 Running Tests

```bash
poetry install
poetry run pytest --cov=django_ninja_search
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

## 📚 Metadata & Compatibility

**Python Versions:** 3.10, 3.11, 3.12, 3.13
**Django Versions:** >=5.1.0
**License:** MIT
**Project URL:** [https://github.com/anandrnair547/django-ninja-search](https://github.com/anandrnair547/django-ninja-search)
**PyPI:** [https://pypi.org/project/django-ninja-search/](https://pypi.org/project/django-ninja-search/)

---

## 🧾 License

MIT © [Anand R Nair](https://github.com/anandrnair547)
