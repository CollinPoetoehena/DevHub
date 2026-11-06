---
description: "Use when writing or reviewing Dockerfiles, Compose files, or container images: DevHub Dockerfile defaults, mandatory rules, and validation commands on top of the common instructions."
applyTo: "**/Dockerfile,**/Dockerfile.*,**/*.Dockerfile,**/dockerfile,**/Containerfile,**/compose.yaml,**/compose.yml,**/docker-compose*.yaml,**/docker-compose*.yml,**/.dockerignore"
---

# Docker Instructions

These rules add container specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `docker` skill for Compose services, networking, volumes, container security, and debugging.

## RUN Directives

- Start RUN commands with `set -o errexit -o nounset && \` to fail on command errors and unset variables.
- Chain commands with `&&`, never `;`, so a failed command fails the build.

## Base Images and Packages

- Default registry: `artifacts.kpn.org`.
- Prefer Alpine variants and pin minor versions, such as `python:3.14-alpine`, to allow patch updates only.
- Install build dependencies, use them, and remove them in the same RUN; retain only runtime dependencies. Use `apk add --no-cache`.

```dockerfile
RUN set -o errexit -o nounset && \
    apk add --no-cache gcc musl-dev python3-dev openldap supercronic \
    && pip install -r requirements.txt \
    && apk del gcc musl-dev python3-dev
```

## Layer Caching

Copy dependency manifests before installing dependencies, then copy application source. Order layers from least to most frequently changing:

```dockerfile
COPY requirements.txt /tmp/
RUN set -o errexit -o nounset && \
    pip install -r /tmp/requirements.txt
COPY . /app/
```

## Runtime Permissions

- Default to UID 1001, matching the GitHub Actions dind runner. Create the Alpine runtime user with `adduser -D -u 1001 -G root app` in a RUN command and set `USER 1001`.
- OpenShift can replace the declared UID with a random UID; the supplementary group is always GID 0. Access must rely on group permissions, not owner or world.
- Use `chown 1001:0` for runtime ownership compatible with standard Docker and OpenShift.
- Read-only paths: `chmod u=rwX,g=rX,o=`.
- Writable paths such as logs and temporary files: `chmod u=rwX,g=rwX,o=`.
- Capital `X` sets execute only on directories and already-executable files.

## Images and Compose

- Pin image tags in Dockerfiles and Compose files; never use `latest`.
- Keep secrets out of images, build arguments, and Compose files; use BuildKit secret mounts at build time and runtime secrets or ignored environment files at run time.
- Keep a `.dockerignore` that excludes version control data, local environment files, and build output.

## Validation

Run from the build context; use the repository's configured commands when they differ:

```sh
docker build --check .
docker compose config --quiet
```

## References

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Build checks](https://docs.docker.com/build/checks/)
- [Compose file reference](https://docs.docker.com/reference/compose-file/)
- [OpenShift (OKD): creating images and supporting arbitrary user IDs](https://docs.okd.io/latest/openshift_images/create-images.html)
