---
name: fastapi
description: 'FastAPI application patterns: project layout, app factory and lifespan, pydantic-settings configuration, Pydantic v2 schemas, dependency injection, routers, service layer, and async testing with httpx. Use when building, testing, or reviewing FastAPI routes, dependencies, schemas, or app startup and shutdown.'
---

# FastAPI

Index for FastAPI work; apply it together with the `python` skill. The Python and common instructions take precedence over the reference.

## When to Use This Skill

- Building or changing FastAPI routers, endpoints, or dependencies
- Designing Pydantic request and response schemas or application settings
- Wiring startup and shutdown resources with the lifespan handler
- Testing FastAPI endpoints

## Steps

1. **Structure the change.** Open [references/patterns.md](references/patterns.md) for project structure, app factory and lifespan, configuration, schemas, dependency injection, routers, and the service layer.
2. **Write tests.** Use the reference's testing section, and the `python` skill's testing reference for fixtures and mocking.
3. **Check anti-patterns.** Compare the change with the reference's anti-patterns before reporting.

## Gotchas

- **Blocking calls in `async def`:** blocking I/O in an `async def` endpoint stalls the event loop; use an async client, or a plain `def` endpoint, which FastAPI runs in a thread pool.
- **Lifespan in tests:** `httpx.ASGITransport` does not run lifespan events; wrap the app in `asgi_lifespan.LifespanManager` when startup creates resources.
- **Validate responses:** declare a `response_model` or return annotation so output is validated and filtered; never return ORM objects or secrets directly.
- **Pydantic v2 APIs:** use `model_validate`, `model_dump`, and `model_config = ConfigDict(...)`; the v1 `parse_obj`, `.dict()`, and inner `class Config` are deprecated.
- **Deprecated startup events:** use the `lifespan` handler instead of `@app.on_event("startup")`.

## Related Skills

- `python`: language patterns, testing, and tooling.

## References

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Pydantic documentation](https://docs.pydantic.dev/latest/)
