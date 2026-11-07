# Exercises the inventory validation rules with inline inventories.
mock_provider "github" {}

run "valid_minimal_inventory" {
  command = plan

  variables {
    inventory = {
      owner = "example"
      repositories = {
        app = { visibility = "private", profiles = ["common"], archived = false }
        old = { visibility = "public", profiles = ["common"], archived = true }
      }
    }
  }

  assert {
    condition     = keys(github_repository.active) == ["app"] && keys(github_repository.archived) == ["old"]
    error_message = "Archived repositories must be split from active ones."
  }

  assert {
    condition     = github_repository.active["app"].visibility == "private"
    error_message = "Visibility must come from the inventory."
  }
}

run "rejects_empty_owner" {
  command = plan
  variables {
    inventory = {
      owner        = " "
      repositories = { app = { visibility = "public", profiles = ["common"], archived = false } }
    }
  }
  expect_failures = [var.inventory]
}

run "rejects_bad_name" {
  command = plan
  variables {
    inventory = {
      owner        = "example"
      repositories = { "bad name" = { visibility = "public", profiles = ["common"], archived = false } }
    }
  }
  expect_failures = [var.inventory]
}

run "rejects_bad_visibility" {
  command = plan
  variables {
    inventory = {
      owner        = "example"
      repositories = { app = { visibility = "internal", profiles = ["common"], archived = false } }
    }
  }
  expect_failures = [var.inventory]
}

run "rejects_empty_profiles" {
  command = plan
  variables {
    inventory = {
      owner        = "example"
      repositories = { app = { visibility = "public", profiles = [], archived = false } }
    }
  }
  expect_failures = [var.inventory]
}

run "rejects_missing_common_first" {
  command = plan
  variables {
    inventory = {
      owner        = "example"
      repositories = { app = { visibility = "public", profiles = ["other", "common"], archived = false } }
    }
  }
  expect_failures = [var.inventory]
}

run "rejects_duplicate_profiles" {
  command = plan
  variables {
    inventory = {
      owner        = "example"
      repositories = { app = { visibility = "public", profiles = ["common", "common"], archived = false } }
    }
  }
  expect_failures = [var.inventory]
}

run "rejects_unknown_profile" {
  command = plan
  variables {
    inventory = {
      owner        = "example"
      repositories = { app = { visibility = "public", profiles = ["common", "unknown"], archived = false } }
    }
  }
  expect_failures = [var.inventory]
}
