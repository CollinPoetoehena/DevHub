---
name: docker
description: 'Docker and Docker Compose patterns: local development stacks, multi-stage builds, override files, networking, volumes, container hardening, secrets, .dockerignore, and debugging. Use when writing, reviewing, or debugging Dockerfiles, Compose services, container networking, or volumes.'
---

# Docker

Index for container work. The DevHub Dockerfile defaults in the Docker instructions and the common instructions take precedence over the reference.

## When to Use This Skill

- Writing or reviewing Dockerfiles or Compose files
- Setting up a local development stack with Compose
- Configuring container networking, volumes, or secrets
- Debugging containers, networks, or builds

## Steps

1. **Write or change a Dockerfile.** Apply the Dockerfile defaults from the Docker instructions, then the hardening and multi-stage patterns in [references/patterns.md](references/patterns.md).
2. **Write or change Compose services.** Open [references/patterns.md](references/patterns.md) for development stacks, override files, networking, volumes, and secrets.
3. **Debug.** Use the debugging commands in [references/patterns.md](references/patterns.md).
4. **Validate.** Run the validation commands from the Docker instructions and report each result.

## Gotchas

- **Later layers do not shrink images:** deleting files in a later `RUN` keeps them in earlier layers; install, use, and remove in the same `RUN`.
- **Build arguments are not secret:** `ARG` and `ENV` values are visible in the image history; use `RUN --mount=type=secret` for build secrets.
- **Shell-form commands swallow signals:** shell-form `CMD` and `ENTRYPOINT` run under `/bin/sh -c`, so the process does not receive `SIGTERM`; use the exec form.
- **`depends_on` does not wait for readiness:** add a `healthcheck` and use `condition: service_healthy`.
- **Published ports listen on all interfaces:** `"8080:80"` is reachable from the network; use `"127.0.0.1:8080:80"` for local-only services.
- **Bind mounts hide image content:** a bind mount over a directory replaces what the image put there, such as installed dependencies.

## Related Skills

- `kubernetes`: running the images on Kubernetes.

## References

- [Docker documentation](https://docs.docker.com/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Compose file reference](https://docs.docker.com/reference/compose-file/)
