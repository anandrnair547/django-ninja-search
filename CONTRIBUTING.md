# Contributing to django-ninja-search

Thank you for considering contributing to `django-ninja-search`! 🎉

This guide will help you get started.

---

## 🚧 Requirements

* Python 3.10+
* Django >=5.1.0
* [Django Ninja](https://django-ninja.dev)
* Poetry (for dependency management)

---

## 📦 Setup

1. **Clone the repository:**

```bash
git clone https://github.com/anandrnair547/django-ninja-search.git
cd django-ninja-search
```

2. **Install dependencies:**

```bash
poetry install
```

---

## 🧪 Running Tests

Install dev‑dependencies first (they include **pytest-cov** for coverage reports):

```bash
poetry install  # pulls dev group too
```

Run the full test suite with coverage (targeting the `ninja_search` module) and generate an HTML report:

```bash
poetry run pytest --cov=ninja_search --cov-report=html
```

This creates `htmlcov/index.html` — open it to view detailed coverage:

```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

---

## ✅ Guidelines

* Follow PEP8 and Black formatting.
* Write clear commit messages.
* Cover new functionality with tests.
* If your feature is Ninja-specific (e.g. depends on `Schema` or `Query`), document that in your PR.

---

## 🧠 Tips

* The decorator is meant for Django Ninja views using `Schema` and `Query`.
* Refer to existing usage in `tests/unit/test_searching.py` for patterns.

---

## 📦 Versioning & Release

Before publishing a release:

1. **Bump the version using Poetry:**

```bash
poetry version patch   # or minor / major as appropriate
```

2. **Build the package:**

```bash
poetry build
```

3. **Publish to Test PyPI:**

```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish --build -r testpypi
```

4. **Publish to PyPI:**

```bash
poetry config repositories.pypi https://upload.pypi.org/legacy/
poetry config pypi-token.pypi <your-token-here>
poetry publish --build -r pypi
```

5. **Tag the version and push to GitHub:**

```bash
NEW_VERSION=$(poetry version -s)
git tag v$NEW_VERSION
git push origin v$NEW_VERSION
git push origin main
```

---

## 🚥 Continuous Integration

GitHub Actions runs the test suite on every push to `main`. Check the [Actions tab](https://github.com/anandrnair547/django-ninja-search/actions) for results.

---

## 📬 Questions?

Open an issue or drop a discussion at:
[https://github.com/anandrnair547/django-ninja-search/issues](https://github.com/anandrnair547/django-ninja-search/issues)

---

Thanks for your interest in improving the project! 🚀
