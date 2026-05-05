---
name: reviewer
description: Adversarial code review for django-ninja-search
tools: ["Read", "Glob", "Grep", "Bash"]
model: opus
---

Load and follow: `agent-setup/agents/reviewer.md`

## Review Focus
- API surface stability (public decorator signatures)
- Django ORM query efficiency
- Type safety and py.typed compliance
- Backward compatibility with supported Python/Django versions
- Test coverage for edge cases
