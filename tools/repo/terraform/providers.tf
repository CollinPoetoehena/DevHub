# Credentials come from the provider's environment, such as GITHUB_TOKEN or GITHUB_APP_*.
provider "github" {
  owner = var.inventory.owner
}
