# TODOs for now:


## GitHub subscription
TODO: add here stating GitHub Subscription -> Pro (cheapest paid version) to unlock things like protection rules, etc. Otherwise, I do not have access to these features. 


## GitHub Actions & Versioning & Dependabot
### Actions
TODO: add GitHub Actions here, with parts:
- Generic/reusable: Reusable actions and workflows that can be used across multiple repositories and projects -> used specifically for my personal projects repos.
- This repo: Specific actions to automate tasks related to DevHub, such as checking documentation, the reusable actions, etc.

TODO: add a GitHub action that checks the documentation, here can just add in the action itself such as checking that all workflows and actions have been referenced in the corresponding documentation files, the Copilot skills and instructions have their own files, etc.; see my work projects for an example how you can do that.
### Versioning
TODO: add CHANGELOG.md to this DevHub and release 1.0.0 after all the changes in this TODO.md.
TODO: add a GitHub action that does this automatically for DevHub with git tag and also checks that the CHANGELOG.md contains the corresponding version entry (e.g. can check if the current latest git tag is not equal to the latest version in the CHANGELOG.md, because that would indicate that the new version is not in CHANEGLOG.md because the CHANGELOG.md has not been updated yet for the new version in the repository) -> also the CHANGELOG.md is the source of truth for the versioning information (it is present for each version anyway), so the action can release the version based on the CHANGELOG.md entry. This ensures that the versioning is consistent and automated, reducing manual errors and keeping the repository up to date with the latest release information.
### Dependabot
TODO: also add dependabot here, used for the reusable workflow dependencies. See my work projects for an example.
### Homelab updates
TODO: add a TODO for homelab public actions where it checks that each file follows the structure, etc.
### Rollout & Integration
TODO: make a TODO for roll out and integration.

## Tools setup such as packaging & Actions design
TODO: see dns-devhub, use the same setup here with a `devhub-tools` package used for all things like packaging, etc.
TODO: add same reasoning in that README.md as with my work projects such as independently versioned, local usage, not vendor-lockin for GitHub Actions, etc. And also it can be properly tested, etc.
TODO: GitHub Actions are wrappers that use that tooling, etc.
TODO: add the package `devhub-tools` in separate repo and link to it in this DevHub repo.
TODO: make it in Python; add in README.md tool choice Python because it is widely used, has a rich ecosystem for packaging and tooling, and allows for easy integration with GitHub Actions and other automation workflows, etc.

