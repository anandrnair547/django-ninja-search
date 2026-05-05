---
name: tester
description: Test generation and execution for django-ninja-search
tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
model: sonnet
---

Load and follow: `agent-setup/agents/tester.md`

## Test Commands
- Run all: `pytest`
- Run with coverage: `pytest --cov=ninja_search --cov-report=term-missing`
- Framework: pytest + pytest-django
- Settings module: tests.test_project.settings
- Load: `agent-setup/skills/domain/tdd-mastery/SKILL.md`
