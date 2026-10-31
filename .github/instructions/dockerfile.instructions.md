---
description: "Use when writing Dockerfiles or reviewing container build and OpenShift runtime conventions."
applyTo: "**/Dockerfile,**/Dockerfile.*,**/*.Dockerfile,**/dockerfile"
---

# DevHub Dockerfile Instructions

Developer note (Copilot may ignore this note): these instructions are distributed in the common APM package. See the [Copilot setup guide](https://github.com/CollinPoetoehena/devhub/blob/master/docs/COPILOT-SETUP.md) for installation and maintenance.

## RUN Directives

- Start RUN commands with `set -o errexit -o nounset && \` to fail on command errors and unset variables.
- Chain commands with `&&`, never `;`, so a failed command fails the build.

---

## Base Images and Packages

- Default registry: `artifacts.kpn.org`.
- Prefer Alpine variants and pin minor versions, such as `python:3.14-alpine`, to allow patch updates only.
- Install build dependencies, use them, and remove them in the same RUN; retain only runtime dependencies. Use `apk add --no-cache`.

```dockerfile
# Build dependencies are removed; runtime dependencies remain.
RUN set -o errexit -o nounset && \
    apk add --no-cache gcc musl-dev python3-dev openldap supercronic \
    && pip install -r requirements.txt \
    && apk del gcc musl-dev python3-dev
```

---

## Layer Caching

Copy dependency manifests before installing dependencies, then copy application source. Order layers from least to most frequently changing:

```dockerfile
COPY requirements.txt /tmp/
RUN set -o errexit -o nounset && \
    pip install -r /tmp/requirements.txt
COPY . /app/
```

---

## Runtime Permissions

- Default to UID 1001, matching the GitHub Actions dind runner. Create the Alpine runtime user with `adduser -D -u 1001 -G root app` in a RUN command and set `USER 1001`.
- OpenShift can replace the declared UID with a random UID; the supplementary group is always GID 0. Access must rely on group permissions, not owner or world.
- Use `chown 1001:0` for runtime ownership compatible with standard Docker and OpenShift.
- Read-only paths: `chmod u=rwX,g=rX,o=`.
- Writable paths such as logs/temp: `chmod u=rwX,g=rwX,o=`.
- Capital `X` sets execute only on directories and already-executable files.
