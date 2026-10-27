# DevHub Generic Instructions

These instructions apply for all code and documentation in DevHub repositories.

TODO NOTE: This is done already, I added first setup and from the TODO.md, etc.

---

## Documentation Guidelines

### General Principles
- **Terse and Succinct**: Essential details only, no verbose explanations
  - **Focus on decisions**: Record significant project-specific choices, constraints, alternatives, and consequences that cannot be inferred from the code; avoid documenting general theory or routine implementation details
  - **Link to authoritative sources**: For general knowledge like language, framework, or API details, link to the relevant official documentation instead of duplicating it; explain the project's specific usage or rationale where needed
- **Code is Truth**: Documentation must match code implementation exactly
- **Fact-check Required**: Always verify documentation against actual code (including documentation that is not affected by the changes to ensure documentation always remains accurate and up-to-date)
- **Describe behavior, not edits**: Document what the code does; avoid change narration such as "I changed X, so it now does Y" or "This change now..."

### Formatting Rules
- **No "Reading time" headers**: Never include estimated reading times
- **Minimal Emoji Usage**: Use only ✅ ❌ ⚠️ for status indicators in code/examples, avoid decorative or unrelated emojis
- **Plain Bullet Points**: No emoji bullets in feature lists or documentation sections, use standard markdown bullet points (`-` or `*`) instead
- **Headings & Splitting**: Use consistent heading levels and descriptive titles for sections and subsections; use `---` to separate major (level 2: `##`) sections
- **Table of Contents**: Include a table of contents for longer documentation files to improve navigation. List headings from levels `##` through `####` only; do not include headings below level `####`. Skip the table of contents for very short documentation files and for Copilot instruction files like `copilot-instructions.md`.

---

## Generic Code Standards

Coding standards that apply to all code (e.g. Python, Go, Shell, Docker, etc.):
- **Readability & Maintainability**: Write code that is easy to read and maintain, with clear structure and logical flow
- **Documentation & Comments**: Code must be self-documenting with clear variable names, add inline comments only where necessary to explain non-obvious logic; avoid redundant or obvious comments
- **DRY Principle**: Avoid duplication, abstract common logic into reusable constructs (e.g. functions, classes, modules, etc.)
- **YAGNI Principle**: Do not add functionality or abstractions that are not currently required; prefer the simplest solution that meets the task
- **KISS Principle**: Keep It Simple, Stupid; prefer straightforward solutions over complex ones
- **Single Responsibility & Separation of Concerns**: Each function/module should have one clear responsibility and different concerns should be separated into distinct modules or layers
- **Error Handling**: Clear error messages with actionable solutions
- **Validation & Fail-fast**: Early validation of inputs with descriptive failures
- **Consistency**: Maintain consistent coding style, naming conventions, and patterns throughout the codebase where applicable (e.g., indentation, spacing, naming schemes); avoid blindly following conventions without understanding their purpose

---

## Testing & CI
- Python tests in containerized environments
- All test results stored in `test-results/` directory
- Run relevant existing tests for the changed code. If no meaningful tests exist, treat their absence as intentional: do not add test scaffolding or run tests by default, and state in the final response that tests were skipped and why. Continue applicable non-test validation; follow explicit user requests or project requirements for tests.
- When tests are required or the project has an established test suite, add or update meaningful tests for changed behavior and relevant edge cases; avoid superficial assertions or scaffolding that does not verify expected outcomes.

---

## Container Guidelines

- Default registry: `TODO`
- **Use official images**: Prefer official images from trusted sources to ensure security and reliability

### Package Management
- **Prefer minimal base images**: Start with the smallest image that meets your requirements to reduce attack surface and image size
  - **Prefer Alpine variants**: Minimal attack surface, smaller images
  - **Pin minor versions**: Use `python:3.14-alpine` (not `python:3-alpine`) to allow patch updates only
- **Separate build and runtime dependencies**:
  - Install build deps, use them, remove them in same RUN command
  - Only runtime dependencies remain in final image
  - Reduces image size and attack surface
- **Example pattern**:
  ```dockerfile
  # Build deps: gcc musl-dev python3-dev (removed after install)
  # Runtime deps: openldap supercronic
  RUN set -o errexit -o nounset && \
    apk add --no-cache \
      gcc musl-dev python3-dev \
      openldap supercronic \
      && pip install -r requirements.txt \
    && apk del gcc musl-dev python3-dev
  ```
- **Use `--no-cache`**: Prevents package cache from inflating image size

### RUN Directives
- **Shell Options**: Always start RUN commands with `set -o errexit -o nounset && \`
  - `errexit`: Exit immediately if any command fails
  - `nounset`: Treat unset variables as errors
- **Command Chaining**: Use `&&` to chain commands, never `;`
  - Ensures build fails on first error in chain
  - Example: `RUN set -o errexit -o nounset && cmd1 && cmd2 && cmd3`

### Layer Caching Optimization
- **COPY dependency manifests before install**: Improves rebuild speed, such as:
  ```dockerfile
  COPY requirements.txt /tmp/
  RUN set -o errexit -o nounset && \
      pip install -r /tmp/requirements.txt
  COPY . /app/
  ```
- **Order layers by change frequency**: Least changing (dependencies) → most changing (source code)

### Security
- **User ID**: Default to UID 1001 (matches GitHub Actions dind runner); create the Alpine runtime user with `adduser -D -u 1001 -G root app` in a RUN command and set `USER 1001`
- **Minimize Privileges**: Avoid running containers as root; grant only necessary permissions to the runtime user