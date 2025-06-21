# django-ninja-search

`django-ninja-search` provides a simple decorator to enable full-text searching and sorting in Django Ninja API views. It’s designed to make your filtering logic easier to reuse and maintain, with zero boilerplate.

---

## 🚀 Features

* 🔍 Adds `search` query parameter filtering to Django Ninja views
* ↕️ Supports `ordering` query parameter for sorting by specified fields
* 🧩 Pluggable: Works with your existing Pydantic filter schemas
* 🪶 Lightweight and dependency-free (beyond Django + Ninja)

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

## 🧑‍💻 Usage

```python
from ninja import Router, Query
from pydantic import BaseModel
from ninja_search import searching

router = Router()

class ItemFilter(BaseModel):
    pass  # your custom filters can go here

@router.get("/items")
@searching(
    filterSchema=ItemFilter,
    search_fields=["name", "description"],
    sort_fields=["name", "price"]
)
def list_items(request, filters: ItemFilter = Query(...)):
    return Item.objects.all()
```

This will automatically:

* Filter by `search=<term>` across `name` and `description`
* Sort by `ordering=name` or `ordering=-price`

---

## 🧪 Running Tests

```bash
poetry install
PYTHONPATH=. poetry run pytest -v
```

---

## 📂 Project Structure

```
django-ninja-search/
├── ninja_search/           # Core package code
├── tests/                  # Test project & unit tests
│   ├── test_project/       # Minimal Django project config
│   ├── unit/               # Tests for searching decorator
```

---

## 📝 License

MIT License

---

## 👤 Author

Built with ❤️ by [Anand R Nair](mailto:anand547@outlook.com)

---

## 🌐 Links

* 📘 [Django Ninja Documentation](https://django-ninja.dev)
* 🐍 [Django](https://www.djangoproject.com/)
* 🐙 [GitHub Repository](https://github.com/anandrnair/django-ninja-search)

---

Enjoying the project? Consider starring it ⭐ to support the maintainer!
