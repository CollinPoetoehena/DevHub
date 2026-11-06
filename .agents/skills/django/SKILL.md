---
name: django
description: 'Django patterns: project layout and split settings, models and QuerySets, Django REST framework serializers and viewsets, service layer, caching, signals, middleware, and query performance. Use when building, testing, or reviewing Django or Django REST framework applications, models, migrations, or APIs.'
---

# Django

Index for Django work; apply it together with the `python` skill. The Python and common instructions take precedence over the reference.

## When to Use This Skill

- Building or changing Django apps, models, views, or settings
- Designing Django REST framework serializers, viewsets, or permissions
- Optimizing QuerySets, caching, or bulk operations
- Adding signals or middleware

## Steps

1. **Structure the change.** Open [references/patterns.md](references/patterns.md) for project layout, split settings, model and QuerySet patterns, REST framework patterns, the service layer, caching, signals, middleware, and performance.
2. **Change models with migrations.** Create a migration for every model change in the same change, and keep data migrations reversible where possible.
3. **Write tests.** Use the `python` skill's testing reference; with pytest, use `pytest-django`.
4. **Validate.** Run `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and the test suite.

## Gotchas

- **N+1 queries:** use `select_related` for foreign keys and one-to-one relations and `prefetch_related` for many-valued relations; assert query counts in tests with `assertNumQueries`.
- **Applied migrations are history:** never edit a migration that has been applied elsewhere; add a new one.
- **Bulk operations skip hooks:** `bulk_create`, `bulk_update`, and `QuerySet.update()` do not call `save()` or send signals.
- **Signals hide control flow:** prefer explicit service calls; use signals only for decoupled side effects.
- **Production settings:** never run with `DEBUG = True` or a hardcoded `SECRET_KEY`; run `python manage.py check --deploy` for production settings.

## Related Skills

- `python`: language patterns, testing, and tooling.

## References

- [Django documentation](https://docs.djangoproject.com/en/stable/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [Deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
