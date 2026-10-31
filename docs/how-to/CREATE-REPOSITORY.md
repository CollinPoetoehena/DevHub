# Create a Repository in the DevHub Ecosystem

Use this when adding a personal project repository. DevHub manages the GitHub inventory and policy; the project owns its source, files, and operational documentation.

1. Confirm that a separate repository is appropriate using the [repository-boundary guidelines](../GUIDELINES.md#choosing-a-repository-boundary), and choose a name using the [naming conventions](../GUIDELINES.md#naming-conventions).
2. Follow the repository tool's [authentication](../../tools/repo/README.md#github-app-authentication), [state-management prerequisites](../../tools/repo/README.md#state-management), and [add and roll out a repository](../../tools/repo/README.md#add-and-roll-out-a-repository) procedure. That README owns inventory edits, validation, imports for existing repositories, plan review, apply, and rollout verification; they are intentionally not repeated here.
3. Initialize the project content manually. Add its README, native build/package files, and only the workflows it actually needs. Copy the appropriate APM manifest declaration using the [AI customization setup guide](../USAGE.md#ai-customizations), then install the common package as documented there. Repository management does not scaffold or synchronize these files.
4. Link to the [shared guidelines](../GUIDELINES.md), record project-specific decisions in the owning README, and use the [central task-tracking workflow](TASK-TRACKING.md).

After rollout, use the common profile's pull-request workflow. The [solo-review limitation and administrator bypass](../../tools/repo/README.md#protection-and-solo-reviews) apply; author self-approval is not supported by GitHub.
