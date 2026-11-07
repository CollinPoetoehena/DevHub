resource "github_repository" "active" {
  for_each = local.active

  name       = each.key
  visibility = each.value.visibility

  allow_merge_commit     = each.value.settings.allow_merge_commit
  allow_squash_merge     = each.value.settings.allow_squash_merge
  allow_rebase_merge     = each.value.settings.allow_rebase_merge
  delete_branch_on_merge = each.value.settings.delete_branch_on_merge

  # New repositories get an initial commit so the default branch exists for rulesets.
  auto_init          = true
  archive_on_destroy = true

  lifecycle {
    # Removing a repository from the inventory must never delete it; archive it instead.
    prevent_destroy = true

    ignore_changes = [
      auto_init,
      gitignore_template,
      license_template,
      template,
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
      web_commit_signoff_required,
      squash_merge_commit_title,
      squash_merge_commit_message,
      merge_commit_title,
      merge_commit_message,
      pages,
      security_and_analysis,
      vulnerability_alerts,
    ]
  }
}

# Archived repositories reject settings updates, so all imported metadata is preserved.
resource "github_repository" "archived" {
  for_each = local.archived

  name               = each.key
  visibility         = each.value.visibility
  archived           = true
  archive_on_destroy = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = all
  }
}
