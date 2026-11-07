variable "inventory" {
  description = "Repository inventory: the owning account and each repository's visibility, ordered profiles, and archive state."
  type = object({
    owner = string
    repositories = map(object({
      visibility = string
      profiles   = list(string)
      archived   = bool
    }))
  })
  nullable = false

  validation {
    condition     = trimspace(var.inventory.owner) != ""
    error_message = "inventory.owner must not be empty."
  }

  validation {
    condition     = alltrue([for name in keys(var.inventory.repositories) : can(regex("^[A-Za-z0-9._-]+$", name))])
    error_message = "Repository names may contain only letters, digits, '.', '_', and '-'."
  }

  validation {
    condition     = alltrue([for repository in values(var.inventory.repositories) : contains(["public", "private"], repository.visibility)])
    error_message = "Repository visibility must be 'public' or 'private'."
  }

  validation {
    condition     = alltrue([for repository in values(var.inventory.repositories) : length(repository.profiles) > 0])
    error_message = "Every repository needs at least one profile."
  }

  validation {
    condition     = alltrue([for repository in values(var.inventory.repositories) : try(repository.profiles[0], "") == "common"])
    error_message = "The first profile of every repository must be 'common'."
  }

  validation {
    condition     = alltrue([for repository in values(var.inventory.repositories) : length(distinct(repository.profiles)) == length(repository.profiles)])
    error_message = "Repository profiles must be unique."
  }

  validation {
    condition = alltrue(flatten([
      for repository in values(var.inventory.repositories) : [
        for profile in repository.profiles : contains(keys(local.profiles), profile)
      ]
    ]))
    error_message = "Every repository profile must be defined in local.profiles."
  }
}
