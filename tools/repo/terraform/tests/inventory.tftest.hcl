# Plans the real inventory against a mocked GitHub provider; no credentials or network needed.
mock_provider "github" {}

run "real_inventory_plans" {
  command = plan

  assert {
    condition     = length(github_repository.active) == 8
    error_message = "Expected 8 active repositories in the real inventory."
  }

  assert {
    condition     = length(github_repository.archived) == 3
    error_message = "Expected 3 archived repositories in the real inventory."
  }

  assert {
    condition = (
      length(github_repository_ruleset.default_branch_safety) == length(github_repository.active) &&
      length(github_repository_ruleset.default_branch_pull_request) == length(github_repository.active) &&
      length(github_workflow_repository_permissions.active) == length(github_repository.active)
    )
    error_message = "Every active repository needs both rulesets and workflow permissions."
  }

  assert {
    condition     = github_repository.active["devhub-homelab-private"].visibility == "private"
    error_message = "devhub-homelab-private must stay private."
  }

  assert {
    condition = alltrue([
      for repository in values(var.inventory.repositories) :
      length(repository.apm_stacks) == 0
    ])
    error_message = "Omitted apm_stacks values must default to an empty list."
  }

  assert {
    condition     = alltrue([for name in keys(github_repository.archived) : !contains(keys(github_repository.active), name)])
    error_message = "A repository must not be both active and archived."
  }
}

run "common_profile_policy" {
  command = plan

  assert {
    condition = alltrue([
      for repository in values(github_repository.active) :
      repository.allow_squash_merge && !repository.allow_merge_commit && !repository.allow_rebase_merge && repository.delete_branch_on_merge
    ])
    error_message = "The common profile allows only squash merges and deletes merged branches."
  }

  assert {
    condition     = alltrue([for repository in values(github_repository.active) : repository.archive_on_destroy])
    error_message = "Active repositories must archive instead of delete on destroy."
  }

  assert {
    condition     = alltrue([for repository in values(github_repository.archived) : repository.archived && repository.archive_on_destroy])
    error_message = "Archived repositories must stay archived and archive on destroy."
  }

  assert {
    condition = alltrue([
      for ruleset in values(github_repository_ruleset.default_branch_pull_request) :
      one(ruleset.bypass_actors).actor_id == 5 &&
      one(ruleset.bypass_actors).actor_type == "RepositoryRole" &&
      one(ruleset.bypass_actors).bypass_mode == "pull_request" &&
      ruleset.rules[0].pull_request[0].required_approving_review_count == 1 &&
      ruleset.rules[0].pull_request[0].allowed_merge_methods == tolist(["squash"])
    ])
    error_message = "The pull request ruleset requires one approval, squash only, with an admin pull-request bypass."
  }

  assert {
    condition = alltrue([
      for ruleset in values(github_repository_ruleset.default_branch_safety) :
      length(ruleset.bypass_actors) == 0 &&
      ruleset.rules[0].deletion &&
      ruleset.rules[0].non_fast_forward &&
      ruleset.conditions[0].ref_name[0].include == tolist(["~DEFAULT_BRANCH"])
    ])
    error_message = "The safety ruleset blocks deletion and force pushes on the default branch without bypass."
  }

  assert {
    condition = alltrue([
      for permissions in values(github_workflow_repository_permissions.active) :
      permissions.default_workflow_permissions == "read" && permissions.can_approve_pull_request_reviews
    ])
    error_message = "Workflow tokens default to read and may create pull requests."
  }
}
