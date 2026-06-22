# Packages

TODO: short intro here and TOC

---

## Repositories

| Component | Index | Description |
|-----------|-------|-------------|
| Terraform | [Terraform.md](Terraform.md) | Reusable Terraform modules (IaC) |
| Ansible | [Ansible.md](Ansible.md) | Reusable Ansible roles and playbooks |
| Helm | [Helm.md](Helm.md) | Reusable Helm charts |
| _(future)_ | | Add more here as needed |

---

## Versioning

All packages and images follow [Semantic Versioning](https://semver.org/): **`MAJOR.MINOR.PATCH`**.

| Part | When to increment |
|---|---|
| `MAJOR` | Breaking / incompatible changes (e.g. removing or changing existing public API, changing function signatures, removing deprecated code, etc.) |
| `MINOR` | New backwards-compatible functionality (e.g. adding new public API, adding optional parameters, adding a new module or feature, etc.) |
| `PATCH` | Backwards-compatible bug fixes **and** internal changes that don't affect the public API (e.g. refactors, performance improvements, dependency bumps, documentation fixes, CI changes, test improvements, etc.) |

**Rule of thumb:** if users can't tell anything changed → `PATCH`. If users can do something new → `MINOR`. If users must change their code → `MAJOR`.

> **Note:** the `v` prefix is not used in this project, but is commonly used in many ecosystems (e.g. `v1.0.0` instead of `1.0.0`). The important part is the `MAJOR.MINOR.PATCH` format, not the presence of a `v` prefix. So, version the packages without the `v` prefix (e.g. `1.0.0`, `2.1.3`, etc.) to follow the standard SemVer format. 

## Qualifiers (pre-releases)

Append an optional **qualifier** to the version to publish a **pre-release** build without consuming a real version number. This is especially useful during development or testing, where you want to iterate freely before committing to the next stable version.

**Why this matters:** Once you publish `1.0.1` and something still needs to change (e.g. after testing you still find a bug or incomplete change), you are forced to jump to `1.0.2`. Using a qualifier lets you publish test builds (e.g. `1.0.1a`, `1.0.1b`, `1.0.1rc1`, etc.) and only cut the real `1.0.1` when the build is confirmed stable.

**Format:** `MAJOR.MINOR.PATCH<qualifier>` — the qualifier follows immediately after `PATCH` (optionally with a separator `-`). For example:
| Qualifier style | Examples | Typical use |
|---|---|---|
| Letters (`a`, `b`, `c`, …) | `1.0.1a`, `1.0.1b` | Quick iteration during development |
| Alpha | `1.0.1alpha`, `1.0.1-alpha` | Early / unstable builds |
| Beta | `1.0.1beta`, `1.0.1-beta` | Feature-complete but still being validated |
| Preview | `1.0.1preview`, `1.0.1-preview` | Preview build |
| Snapshot | `1.0.1SNAPSHOT`, `1.0.1-SNAPSHOT` | Automated builds reflecting the latest codebase changes at that specific point in time.  |
| Release candidate (rc) | `1.0.1rc`, `1.0.1-rc` | Final testing before the stable release. If no critical bugs are found, this qualifier is typically dropped for the official, stable release. |

**Workflow example (using pseudo code, no specific tooling (publishing logic is already explained elsewhere in this documentation)):**

```sh
# Iterate freely with qualifiers as needed — these do not block the real 1.0.1 release, so you can publish as many as you want while testing and fixing issues until the build is confirmed stable
publish 1.0.1a
publish 1.0.1b
publish 1.0.1alpha
publish 1.0.1beta
publish 1.0.1rc
...

# Publish the stable release only when confirmed good
publish 1.0.1
```

### Creating a release

The releases are created by creating a Git tag with the version number. This serves as the source of truth for the release, and is what consumers will reference when pinning to a specific version. The Git tag can be created manually via the command line, or automatically via CI/CD pipelines. The important part is that the tag follows the format specified above. For example:
```bash
# List commits (used to find the commit hash for the tag)
git log --oneline
# Create an annotated tag with a message (recommended for releases)
git tag -a <tagname> <commit-hash> -m "<release message>"
git push origin <tagname>

# Example:
git tag -a 1.0.0 abc123 -m "Initial release"
git push origin 1.0.0
```

Pin to a tag to get a stable, reproducible reference. Each ecosystem uses the Git tag slightly differently, see the specific instructions for each type below.

### Deleting a release

Deleting a release means deleting the Git tag (locally and remotely). You may also need to delete a published package or image from its registry — see the specific instructions for each component type.

**When you might need to delete a release:**
- You tagged the wrong commit (e.g. the tag points to an unrelated commit).
- You published a broken or incomplete build and want to retract it before consumers pick it up.
- You accidentally tagged with the wrong version number (e.g. `1.1.0` instead of `1.0.1`).
- You need to re-cut the same version against a different commit (e.g. after a hotfix was missed).
- Etc...

> **Warning:** Deleting a tag that has already been consumed by others is a breaking change — their pinned references will no longer resolve. Only delete a release if you are certain no one has pinned to it yet, or if you have coordinated with all affected consumers. Prefer publishing a corrected version over retracting an existing one.

```bash
# Getting current tags and show details (used to find the tag name for deletion)
git tag
git show-ref --tags
git show <tagname>
# Delete the tag locally
git tag -d <tagname>
# Delete the tag on the remote
git push origin -d <tagname>

# Example:
git tag -d 1.0.0
git push origin -d 1.0.0
```