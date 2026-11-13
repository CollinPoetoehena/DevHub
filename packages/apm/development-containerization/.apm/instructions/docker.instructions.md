---
description: "Use when writing or reviewing Dockerfiles, Compose files, or container images: container defaults, essential conventions, and validation commands alongside the common guidelines."
applyTo: "**/Dockerfile,**/Dockerfile.*,**/*.Dockerfile,**/dockerfile,**/Containerfile,**/compose.yaml,**/compose.yml,**/docker-compose*.yaml,**/docker-compose*.yml,**/.dockerignore"
---

# Docker Guidelines

Use general best practices for Docker and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Docker, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

## RUN Directives

- Start RUN commands with `set -o errexit -o nounset && \` to fail on command errors and unset variables.
- Chain commands with `&&`, never `;`, so a failed command fails the build.

## Base Images and Packages

- Use minimal base images from trusted registries. Prefer Alpine variants when compatible and pin versions, such as `python:3.14-alpine`, to allow patch updates only.
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

- Run as a non-root user and choose a UID/GID compatible with the target runtime; do not assume a work-specific fixed UID.
- OpenShift can replace the declared UID with an arbitrary UID; the supplementary group is GID 0. For images targeting OpenShift, access must rely on group permissions, not owner or world.
- Set runtime ownership and group permissions for the identity expected by the target platform. Avoid granting world access.
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

Use the `docker` skill for additional Compose, networking, volume, container-security, and debugging procedures.

## References

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Build checks](https://docs.docker.com/build/checks/)
- [Compose file reference](https://docs.docker.com/reference/compose-file/)
- [OpenShift (OKD): creating images and supporting arbitrary user IDs](https://docs.okd.io/latest/openshift_images/create-images.html)

Use relevant available skills for additional procedures and references.
