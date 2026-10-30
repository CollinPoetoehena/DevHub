# Existing repositories must be imported before apply; unrelated metadata stays unmanaged.
data "github_repository" "private_adoption" {
  # A missing/inaccessible adoption target must never become a new private repository.
  full_name = "CollinPoetoehena/devhub-homelab-private"
}

resource "github_repository" "active" {
  for_each = local.active_repositories

  name       = each.key
  visibility = each.value.visibility
  archived   = each.value.archived

  # GitHub creates the initial commit; no repository content is managed afterward.
  auto_init = true

  allow_merge_commit = each.value.settings.allow_merge_commit
  allow_squash_merge = each.value.settings.allow_squash_merge
  allow_rebase_merge = each.value.settings.allow_rebase_merge

  lifecycle {
    prevent_destroy = true

    ignore_changes = [
      auto_init,
      gitignore_template,
      license_template,
      template,
      fork,
      source_owner,
      source_repo,
      description,
      homepage_url,
      topics,
      has_issues,
      has_discussions,
      has_projects,
      has_wiki,
      has_downloads,
      is_template,
      allow_auto_merge,
      allow_forking,
      allow_update_branch,
      delete_branch_on_merge,
      web_commit_signoff_required,
      squash_merge_commit_title,
      squash_merge_commit_message,
      merge_commit_title,
      merge_commit_message,
      pages,
      security_and_analysis,
    ]

    precondition {
      condition     = each.key != "devhub-homelab-private" || coalesce(data.github_repository.private_adoption.repo_id, 0) > 0
      error_message = "devhub-homelab-private is adoption-only: restore token access and import the existing repository. Do not create a replacement."
    }

    postcondition {
      condition     = self.default_branch == each.value.settings.main_branch
      error_message = "The repository must already use main as its default branch. For new repositories, set the owner's default branch for new repositories to main before creation; for existing repositories, prepare main and switch the default branch before importing. No branches are created or renamed by this configuration."
    }
  }
}

# Archived repositories reject settings updates, so preserve all imported metadata.
resource "github_repository" "archived" {
  for_each = local.archived_repositories

  name       = each.key
  visibility = each.value.visibility
  archived   = each.value.archived
  auto_init  = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = all
  }
}

# Keep main deletion/force-push safety separate from the administrator PR merge exception.
resource "github_repository_ruleset" "main_safety" {
  for_each = local.active_repositories

  name        = "main-safety"
  repository  = github_repository.active[each.key].name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["refs/heads/${each.value.settings.main_branch}"]
      exclude = []
    }
  }

  rules {
    deletion         = each.value.settings.protect_main_deletion
    non_fast_forward = each.value.settings.block_main_force_push
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "github_repository_ruleset" "main_pull_request" {
  for_each = local.active_repositories

  name        = "main-pull-request"
  repository  = github_repository.active[each.key].name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["refs/heads/${each.value.settings.main_branch}"]
      exclude = []
    }
  }

  # RepositoryRole 5 is admin. This permits PR merges, not self-approval or direct pushes.
  bypass_actors {
    actor_id    = 5
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

  lifecycle {
    prevent_destroy = true
  }
}
