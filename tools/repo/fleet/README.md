# `repo-fleet`

`repo-fleet` renders and plans DevHub's shared repository files against the inventory. The central fleet workflow also uses it to preflight and deliver one combined template/APM PR per changed active repository. See the [repository fleet guide](../README.md) for design, inventory, authentication, and Terraform operations.

From this directory, install the locked dependencies and run the offline validation:

```bash
uv sync --locked
uv run repo-fleet check
```

Normal `plan` and `apply` commands manage shared templates. APM changes are explicitly opt-in for local content-only operations:

```bash
uv run repo-fleet plan --apm
uv run repo-fleet apply --apm
```

APM mode requires authenticated GitHub access and the pinned APM CLI 0.35.0. It prepares all selected active repositories before any PR writes, creates or updates pull requests on `devhub/apm-sync`, and skips archived repositories. Exit codes are 0 for no changes or success, 2 for planned changes, and 1 for an error or declined confirmation. The one central workflow uses staged `repo-fleet sync` commands to validate adopted Terraform state, prepare all combined content, apply the exact saved settings plan, and deliver prepared pull requests. Its triggers, token boundaries, bootstrap, and recovery are documented in the [central fleet sync guide](../../../docs/github-actions/workflows/apm-sync.md).
