resource "github_repository_ruleset" "default_branch_safety" {
  for_each = local.active

  name        = "default-branch-safety"
  repository  = github_repository.active[each.key].name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  rules {
    deletion         = true
    non_fast_forward = true
  }
}

resource "github_repository_ruleset" "default_branch_pull_request" {
  for_each = local.active

  name        = "default-branch-pull-request"
  repository  = github_repository.active[each.key].name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  # The bypass lets the role merge its own pull requests; it does not allow direct pushes.
  bypass_actors {
    actor_id    = each.value.settings.bypass_repository_role_id
    actor_type  = "RepositoryRole"
    bypass_mode = "pull_request"
  }

  rules {
    pull_request {
      required_approving_review_count = each.value.settings.required_approving_review_count
      allowed_merge_methods = [
        for method, enabled in {
          merge  = each.value.settings.allow_merge_commit
          squash = each.value.settings.allow_squash_merge
          rebase = each.value.settings.allow_rebase_merge
        } : method if enabled
      ]
    }
  }
}
