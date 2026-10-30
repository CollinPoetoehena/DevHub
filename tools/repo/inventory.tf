# Explicit repository inventory; all active repositories share the common profile.
locals {
  profiles = {
    common = {
      main_branch                     = "main"
      protect_main_deletion           = true
      block_main_force_push           = true
      required_approving_review_count = 1
      allow_merge_commit              = false
      allow_squash_merge              = true
      allow_rebase_merge              = false
    }
  }

  repositories = tomap({
    DevHub = {
      profile    = "common"
      visibility = "public"
      archived   = false
    }
    devhub-homelab = {
      profile    = "common"
      visibility = "public"
      archived   = false
    }
    devhub-homelab-private = {
      profile    = "common"
      visibility = "private"
      archived   = false
    }
    devhub-ansible-users = {
      profile    = "common"
      visibility = "public"
      archived   = false
    }
    devhub-ansible-proxmox = {
      profile    = "common"
      visibility = "public"
      archived   = true
    }
    devhub-ansible-mgmtvm = {
      profile    = "common"
      visibility = "public"
      archived   = false
    }
    devhub-ansible-jumphost = {
      profile    = "common"
      visibility = "public"
      archived   = true
    }
    devhub-ansible-router-custom = {
      profile    = "common"
      visibility = "public"
      archived   = true
    }
    devhub-terraform-azurerm-network = {
      profile    = "common"
      visibility = "public"
      archived   = false
    }
    devhub-terraform-azurerm-compute = {
      profile    = "common"
      visibility = "public"
      archived   = false
    }
    homelab-energy-exporter = {
      profile    = "common"
      visibility = "public"
      archived   = false
    }
  })

  active_repositories = {
    for name, repository in local.repositories : name => merge(repository, {
      settings = local.profiles[repository.profile]
    }) if !repository.archived
  }

  archived_repositories = {
    for name, repository in local.repositories : name => repository if repository.archived
  }
}
