# django-ninja-search — Project Configuration

## Overview
- **Project**: django-ninja-search — A lightweight decorator to add filtering, searching, and sorting support to Django Ninja view functions
- **Type**: Python/Django library package (published on PyPI)
- **Repo**: /Users/anandrnair/Documents/Projects/Personal/ninja-search/django-ninja-search
- **PyPI**: https://pypi.org/project/django-ninja-search/

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Framework | Django 5.0+ + Django Ninja 1.0+ |
| Test | pytest + pytest-django + pytest-cov |
| Lint | ruff |
| Package | pyproject.toml (Poetry backend) |
| CI | GitHub Actions |

## Key Commands
- **Test**: `pytest`
- **Test with coverage**: `pytest --cov=ninja_search --cov-report=term-missing`
- **Test (HTML report)**: `pytest --cov=ninja_search --cov-report=html`
- **Lint**: `ruff check .`
- **Format**: `ruff format .`
- **Install dev**: `poetry install`

## Directory Structure
```
django-ninja-search/
├── ninja_search/           # Library source
│   ├── __init__.py         # Package exports
│   ├── searching.py        # Core decorator implementation
│   └── py.typed            # PEP 561 marker
├── tests/
│   ├── conftest.py         # Shared fixtures
│   ├── manage.py           # Test project manage.py
│   ├── test_project/       # Django settings for tests
│   └── unit/               # Unit tests
├── pyproject.toml          # Package metadata + dependencies
├── pytest.ini              # Pytest configuration
├── agent-setup -> ...      # Symlink to central agent framework
├── .claude/agents/         # Project-specific agent wrappers
└── .agents/                # Project config + memory
```

## Library Architecture
- **Core**: `ninja_search/searching.py` — the `@searching` decorator
- **How it works**: Wraps Django Ninja view functions to intercept `search`, `ordering` query params and apply them to the returned QuerySet
- **Public API**: `@searching(filterSchema=..., search_fields=[...], sort_fields=[...])`
- **Design**: Zero config beyond the decorator — no middleware, no settings, no models

## Agent Framework
- Base: `agent-setup/` (symlink to central framework)
- Key skills: python-best-practices, django-patterns, testing-expert, tdd-mastery
- Protocols: universal, quality-gates, output-format

## Git
- Remote: `git@github.com:anandrnair547/django-ninja-search.git`
- Branch: main
- CI: GitHub Actions (test.yml)
