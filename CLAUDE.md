# django-ninja-search — Agent Configuration

## Agent Framework

Base framework: `agent-setup/` (symlink to central framework at `/Users/anandrnair/Documents/Projects/Personal/claude/agent-setup/`)

**Before any task**:
1. Load `agent-setup/protocols/universal.md`
2. Route via `agent-setup/agents/orchestrator.md`
3. Load `.agents/project-config.md` for project context
4. Always active skills:
   - `agent-setup/skills/domain/python-best-practices/SKILL.md`
   - `agent-setup/skills/domain/django-patterns/SKILL.md`
5. For test work: `agent-setup/skills/testing-expert/SKILL.md`

---

## Project Overview

django-ninja-search is a lightweight decorator library that adds filtering, searching, and sorting support to Django Ninja view functions. Published on PyPI.

## Tech Stack

- Python 3.10+
- Django 5.0+ / Django Ninja 1.0+
- pytest + pytest-django + pytest-cov
- Poetry (build backend)
- ruff (lint + format)
- GitHub Actions (CI)

## Key Commands

- **Test**: `pytest`
- **Coverage**: `pytest --cov=ninja_search --cov-report=term-missing`
- **Lint**: `ruff check .`
- **Format**: `ruff format .`
- **Install**: `poetry install`

## Testing Requirements

- Tests must pass before every push
- New features need tests
- Maintain high coverage (CI reports to Codecov)
- Test settings: `tests.test_project.settings`

## Library Public API

```python
from ninja_search.searching import searching

@searching(
    filterSchema=MyFilterSchema,
    search_fields=["name", "description"],
    sort_fields=["name", "created_at"],
)
def my_view(request, filters=Query(...)):
    return MyModel.objects.all()
```

## Git

- Remote: `git@github.com:anandrnair547/django-ninja-search.git`
- Branch: `main`
