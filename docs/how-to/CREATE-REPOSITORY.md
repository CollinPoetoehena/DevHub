# Create a Repository in the DevHub Ecosystem

Use this when adding a personal project repository. DevHub manages the GitHub inventory, policy, and shared templates; the project owns its source, files, and operational documentation.

1. Confirm that a separate repository is appropriate using the [monorepo or polyrepo guidance](../GUIDELINES.md#monorepo-or-polyrepo), and choose a name using the [naming conventions](../GUIDELINES.md#naming-conventions).
2. Follow the repository tool's [authentication](../../tools/repo/README.md#authentication), [state](../../tools/repo/README.md#state), and [add a repository](../../tools/repo/README.md#add-a-repository) procedure. Terraform creates the repository with its settings and protection, and `repo-fleet` opens a pull request with the profile templates, including the [APM sync workflow](../github-actions/workflows/apm-sync.md). That README owns the details; they are intentionally not repeated here.
3. Add the project content: its README, native build/package files, and the workflows it needs beyond the templates. Copy the appropriate APM manifest declaration using the [AI customization setup guide](../GETTING-STARTED.md#ai-customizations) and install it once as documented there; afterwards the APM sync keeps it current.
4. Link to the [shared guidelines](../GUIDELINES.md), record project-specific decisions in the owning README, and use the [central task-tracking workflow](TASK-TRACKING.md).

After rollout, use the common profile's pull request workflow. The [solo-review limitation and administrator bypass](../../tools/repo/README.md#protection-and-solo-reviews) apply; author self-approval is not supported by GitHub.
