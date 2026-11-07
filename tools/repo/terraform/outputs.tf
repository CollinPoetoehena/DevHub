output "active_repositories" {
  description = "Names of the managed active repositories."
  value       = sort(keys(github_repository.active))
}

output "archived_repositories" {
  description = "Names of the preserved archived repositories."
  value       = sort(keys(github_repository.archived))
}
