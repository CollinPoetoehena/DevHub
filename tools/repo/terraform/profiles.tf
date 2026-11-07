locals {
  # Later profiles override earlier ones; every repository starts with common.
  profiles = {
    common = {
      allow_merge_commit               = false
      allow_squash_merge               = true
      allow_rebase_merge               = false
      delete_branch_on_merge           = true
      required_approving_review_count  = 1
      bypass_repository_role_id        = 5
      default_workflow_permissions     = "read"
      can_approve_pull_request_reviews = true
    }
  }

  repositories = {
    for name, repository in var.inventory.repositories : name => merge(repository, {
      settings = merge([for profile in repository.profiles : local.profiles[profile]]...)
    })
  }

  active = {
    for name, repository in local.repositories : name => repository if !repository.archived
  }

  archived = {
    for name, repository in local.repositories : name => repository if repository.archived
  }
}
