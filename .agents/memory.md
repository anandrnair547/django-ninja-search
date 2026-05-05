# django-ninja-search — Agent Memory
last_updated: 2026-05-05

## Library Design Decisions
- Decorator-based API: single `@searching` decorator handles search + filter + sort
- Zero runtime configuration — no Django settings required
- Supports optional filter schema via `filterSchema` parameter
- Works with any Django ORM QuerySet returned from the view

## Known Gotchas
- pytest requires `DJANGO_SETTINGS_MODULE = tests.test_project.settings`
- `--nomigrations` flag used in pytest to skip migration checks
- py.typed marker present — library ships type information

## Test Patterns
- Test project lives in `tests/test_project/` with its own settings
- Unit tests in `tests/unit/`
- Uses pytest-django with Django test client
