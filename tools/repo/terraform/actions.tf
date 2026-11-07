resource "github_workflow_repository_permissions" "active" {
  for_each = local.active

  repository                       = github_repository.active[each.key].name
  default_workflow_permissions     = each.value.settings.default_workflow_permissions
  can_approve_pull_request_reviews = each.value.settings.can_approve_pull_request_reviews
}
