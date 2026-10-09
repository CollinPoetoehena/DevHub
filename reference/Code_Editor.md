# Code Editor

This guide describes my code editor setup and the account and Git configuration I use across personal and work projects. Keeping it maintained gives me repeatable setup steps when I get a new device, reinstall my environment, or need to recreate the same setup later.

> **Note:** This is my personal guide for setting up and using a code editor. It describes the approach that works for me; adapt it to your own accounts, devices, and employer policies.

## Contents

- [Scope](#scope)
- [Editor](#editor)
- [VS Code Settings and Extensions](#vs-code-settings-and-extensions)
    - [File Associations and Language Modes](#file-associations-and-language-modes)
    - [Main Extensions](#main-extensions)
    - [Windows and WSL](#windows-and-wsl)
    - [List Installed Extensions](#list-installed-extensions)
- [Backup and Settings Sync](#backup-and-settings-sync)
    - [Personal VS Code Account and Extensions](#personal-vs-code-account-and-extensions)
    - [Separate Work and Personal Profiles](#separate-work-and-personal-profiles)
- [Subscriptions and Work Accounts](#subscriptions-and-work-accounts)
- [Git](#git)
    - [Git with Personal and Work Accounts](#git-with-personal-and-work-accounts)
        - [Use Different Identities for Work Platforms](#use-different-identities-for-work-platforms)
        - [Verify the Git Identity](#verify-the-git-identity)
    - [Git Authentication with SSH](#git-authentication-with-ssh)
        - [Configure Multiple Work Git Platforms](#configure-multiple-work-git-platforms)
        - [Load Keys into an SSH Agent](#load-keys-into-an-ssh-agent)
        - [Clone or Update a Repository](#clone-or-update-a-repository)

---

## Scope

This setup is intended for both work devices, such as a company laptop, and personal devices, such as a personal laptop. Using the same editor preferences and tools across them makes it easier to move between work and personal projects and to set up a replacement device. Settings, profiles, and extensions are editor preferences; using a personal account to sync them can keep them available independently of a work account.

> **Scope note:** This guide is for local workstations where you run a code editor, such as a work laptop or personal laptop. It is not intended for servers or protected environments where you do not run VS Code; access and Git operations there should follow that environment's separate procedures and policies.

Do not sync secrets, company data, or confidential work configuration to a personal account, and use separate VS Code Profiles when work and personal tools or preferences need separation. This is safe because the settings in VS Code do not contain secrets and company data; only personal preferences/settings and non-sensitive configuration, so they can safely be synced to a personal account.

---

## Editor

I use [Visual Studio Code (VS Code)](https://code.visualstudio.com/) as my code editor. It is a lightweight, extensible editor with a large ecosystem of language tools and extensions, and it works well across personal projects and work repositories.

---

## VS Code Settings and Extensions

**These are some important settings and preferences for myself (preference example updated on 2026-06-18). Settings not listed here can generally stay at their defaults; this section only highlights specific customizations I like, such as `files.associations`.**

My supported user settings and local extension selection are backed up and synced through my personal account as explained in [Backup and Settings Sync](#backup-and-settings-sync). This is a short explanation, not a complete copy of my configuration. Run **Settings Sync: Show Synced Data** in the Command Palette to see the full data synced to my account. Remote extension installations, including WSL, are an exception; see [Windows and WSL](#windows-and-wsl).

### File Associations and Language Modes

I use these associations because plain YAML highlighting can look wrong around Helm or Jinja template expressions. Selecting the matching language mode makes those expressions readable while keeping ordinary YAML in its normal mode.

Open **Preferences: Open User Settings (JSON)** from the Command Palette and merge the following example into your existing settings. VS Code settings use JSON with Comments (JSONC). Keep other settings unchanged, and merge entries into an existing `files.associations` object rather than adding a duplicate one.

```jsonc
{
    // Settings not listed here can generally stay at their defaults.
    "files.associations": {
        // Plain YAML by default; not every YAML file contains templating.
        "*.yaml": "yaml",

        // Helm templates: YAML with Go template expressions.
        "**/charts/**/*.yaml": "helm",
        "**/templates/**/*.yaml": "helm",

        // Personal overrides for files containing Jinja in my workflows.
        "**kustomization.yaml": "jinja-yaml",
        "**deployment.yaml": "jinja-yaml",
        "**values.yaml": "jinja-yaml",
        "**/base/**/*.yaml": "jinja-yaml",
        "**/config/**/*.yaml": "jinja-yaml"
    }
}
```

The [main extensions below](#main-extensions) provide these modes: YAML for plain YAML, Kubernetes for `helm`, and Better Jinja for `jinja-yaml`. Jinja adds template highlighting and snippets but is not required alongside Better Jinja for this example. Syntax highlighting is not the same as automatic document formatting.

These are personal overrides, not universal rules: Kustomize manifests, Kubernetes deployments, and Helm values are normally plain YAML unless a separate templating workflow adds Jinja. Helm templates use Go templates, not Jinja. The broad `charts`, `templates`, `base`, and `config` patterns can also match files that do not use the selected templating language. Narrow them to the relevant project paths, or use workspace settings for project-specific rules. Changing the language mode can affect YAML validation, formatting, and Kubernetes tooling, not just colors.

Check a representative file's language mode in the bottom-right status bar after applying the settings, especially where patterns overlap. Use **Change Language Mode** to select YAML, Helm, or Jinja YAML manually when needed. Add corresponding `.yml` patterns if your projects use that extension; the example targets `.yaml`. Extend the associations with other languages or more specific overrides as needed.

### Main Extensions

These are my most important extensions currently. A full list and further explanation of the others are not necessary here; use the [terminal command below](#list-installed-extensions) or the Extensions view in VS Code to see everything installed. See [Backup and Settings Sync](#backup-and-settings-sync) for my synced local selection.

| Extension | Why I use it |
| --- | --- |
| [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) | YAML validation, completion, and formatting. |
| [Kubernetes](https://marketplace.visualstudio.com/items?itemName=ms-kubernetes-tools.vscode-kubernetes-tools) | Kubernetes tooling and Helm template highlighting and previews. |
| [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) | Jinja2 highlighting, especially Jinja YAML. |
| [Jinja](https://marketplace.visualstudio.com/items?itemName=wholroyd.jinja) | Jinja highlighting and snippets. |
| [Ansible](https://marketplace.visualstudio.com/items?itemName=redhat.ansible) | Ansible playbook and role editing. |
| [HashiCorp Terraform](https://marketplace.visualstudio.com/items?itemName=hashicorp.terraform) | Terraform/HCL tooling and formatting. |
| [Bicep](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-bicep) | Azure Bicep infrastructure editing. |
| [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Python development and debugging. |
| [Go](https://marketplace.visualstudio.com/items?itemName=golang.go) | Go development, testing, and debugging. |
| [Extension Pack for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-pack) | Java language, debugging, and testing tools. |
| [Rainbow CSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv) | Color-coded CSV columns. |
| [Todo Tree](https://marketplace.visualstudio.com/items?itemName=gruntfuggly.todo-tree) | Find TODO/FIXME comments across a project. |
| [TODO Highlight](https://marketplace.visualstudio.com/items?itemName=wayou.vscode-todo-highlight) | Highlight TODO/FIXME comments in the editor. |
| [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack), [WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl), [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh), and [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) | Work in WSL, SSH hosts, and development containers. |
| [Remote Explorer](https://marketplace.visualstudio.com/items?itemName=ms-vscode.remote-explorer) and [Remote - Tunnels](https://marketplace.visualstudio.com/items?itemName=ms-vscode.remote-server) | Browse remote environments and connect through tunnels. |

### Windows and WSL

The Windows and WSL extension lists represent different installation locations, not two incompatible sets of preferences. In my setup, VS Code runs on Windows and connects to VS Code Server in WSL. UI extensions can run locally on Windows, while language tools and debuggers often run in WSL alongside the project and its toolchain. An extension appearing only in the Windows list does not mean it is unsupported on Linux or unavailable while editing in WSL.

In a WSL-connected window, open the Extensions view and check **Local - Installed** and **WSL: Ubuntu - Installed**. Use **Install in WSL: Ubuntu** for a workspace extension that is installed locally but needs to run in WSL. Local user settings are reused in WSL; **Preferences: Open Remote Settings (JSON)** lets you add WSL-specific overrides. See the official [WSL extension management guide](https://code.visualstudio.com/docs/remote/wsl#_managing-extensions).

> **Sync limitation:** [Settings Sync](#backup-and-settings-sync) backs up supported user preferences and local extension selections, but VS Code does **not** sync extensions to or from remote windows such as WSL, SSH, or Dev Containers. Install the needed extensions in each remote environment separately. Workspace files, remote settings, and external toolchains are not restored by syncing local user settings. See the [official Settings Sync documentation](https://code.visualstudio.com/docs/configure/settings-sync#_configure-synced-data).

### List Installed Extensions

Run this in a Windows Command Prompt or PowerShell terminal for the local Windows installation:

```powershell
code --list-extensions
```

Run the same command in a WSL terminal, preferably the integrated terminal of a WSL-connected VS Code window, for that WSL installation. My supplied output begins with `Extensions installed on WSL: Ubuntu:`:

```bash
code --list-extensions
```

To include installed versions, use `code --list-extensions --show-versions`. These commands list installed extension IDs, not whether every extension is enabled for the current workspace. If using multiple profiles, add `--profile "Work"` (replace `Work` with the relevant profile name). The Extensions view remains useful for confirming the local/remote installation location.

---

## Backup and Settings Sync

Use [VS Code Settings Sync](https://code.visualstudio.com/docs/configure/settings-sync) with your **personal GitHub account** (or another personal account supported by VS Code); I prefer GitHub because it is currently my main development account where I also maintain this `DevHub` project, etc. Editor settings are personal preferences, and using a personal account always keeps them available if you change jobs, lose access to a work account, or do not have a work account that can sync the settings at all. The same setup can support work with different tools like Kubernetes and Ansible as well as personal projects such as a homelab.

Settings Sync keeps the supported parts of your coding environment consistent across machines and profiles, including preferences, extensions, keybindings, snippets, and prompts. This avoids manually recreating or maintaining the same setup in every environment.

**To enable it:**

1. In VS Code, open **Manage** (the gear menu) and choose **Backup and Sync Settings...**. You can also open the Accounts menu and choose the Settings Sync option.
2. Sign in with your personal account and turn on Settings Sync.
3. Select the data types you want to sync, including **Settings**, **Extensions**, **Profiles**, and **Prompts and Instructions** when those options are available in your VS Code version. Include prompts you create in your user profile so they are available in your other synced environments.
4. On another machine, sign in to Settings Sync with the same personal account, enable sync, and choose whether to merge or replace local settings if VS Code asks.

The Settings Sync feature backs up supported settings, but it is not a substitute for version control or a separate backup of important files. Keep secrets and employer-confidential configuration out of synced settings, and follow company policy for work-related data.

### Personal VS Code Account and Extensions

It is fine to use your personal account as the main signed-in VS Code account and for Settings Sync. This account keeps your editor setup portable and is separate from subscriptions such as work-provided GitHub Copilot, which can use your work account as described below (see [Separate Work and Personal Profiles](#separate-work-and-personal-profiles)).

I rarely use extensions that require GitHub sign-in (I mainly just use SSH; see [Git with Personal and Work Accounts](#git-with-personal-and-work-accounts)). If an extension needs access to work resources, sign in to that extension with your work account when it supports its own account connection; this does not require changing the account used for Settings Sync. Some extensions use VS Code's shared GitHub authentication instead, so check the extension's sign-in behavior and confirm which account it uses. If it is not possible to sign in with separate accounts, consider using different VS Code profiles for work and personal use. If that is also not possible just use the SSH key for authentication and/or another alternative such as the GUI, etc.

### Separate Work and Personal Profiles

If you need different editor settings or extensions for work and personal projects, create separate VS Code Profiles instead of maintaining two unrelated editor installations or accounts. For example, keep a Personal profile for your own projects and a Work profile with the extensions and preferences you need for work. Switch profiles from **Manage > Profiles**.

Enable **Profiles** in Settings Sync to sync both profiles using your personal account. This keeps the configurations separate while making them available across your environments; the work profile does not require using your work account for Settings Sync. Keep employer-confidential settings and secrets out of personal sync, and follow company policy.

---

## Subscriptions and Work Accounts

Use the account that owns each subscription. In particular, use your **work account for GitHub Copilot in VS Code** when your employer provides the license. The subscription is granted to that account, so it does not need to be tied to the personal account used for Settings Sync (see [Backup and Settings Sync](#backup-and-settings-sync)). For the current product-specific steps, see [Set up GitHub Copilot in VS Code](https://code.visualstudio.com/docs/setup/copilot#_use-a-different-github-account-per-workspace-or-profile).

**To set it up:**

1. Open the Command Palette (`Ctrl+Shift+P` on Windows/Linux or `Cmd+Shift+P` on macOS).
2. Run **Manage Extension Account Preference**.
3. Select **GitHub Copilot** and choose your **work GitHub account** as its preferred account. Complete your organization's SSO or authorization steps if prompted.

> **Account picker note (2026-10-09):** In the **Manage Extension Account Preference** flow, **Add a new account** appears after selecting **GitHub Copilot**. It does not appear when selecting **GitHub** itself.

**Verify the accounts and Copilot access:**

1. Click on the account avatar in the lower-left corner of VS Code and verify it shows 2 GitHub accounts: your personal and work accounts.
2. Confirm [Settings Sync](https://code.visualstudio.com/docs/configure/settings-sync) still shows your **personal GitHub account**.
3. Run **Manage Extension Account Preference** again, select **GitHub Copilot**, and confirm it shows your **work GitHub account**.
4. Check the Copilot icon in the lower-right status bar. It should show the Copilot plan associated with your work account.
5. Open Copilot Chat, send a simple prompt, and confirm Copilot responds using the work account. For example, ask it to explain a small piece of code in the current editor.
6. If your employer has not assigned a Copilot license to your work account, request access from your administrator.

> **Note:** It is fine for Settings Sync and Copilot to use different accounts: Settings Sync uses the account chosen for syncing your editor configuration, while Copilot authenticates the account that owns the subscription. These are separate services, so using your personal account for sync and your work account for Copilot does not change the sync account or interfere with your synced settings. The labels and available account options can vary with VS Code versions and organization policies.

This separation is intentional: personal account for portable editor settings, work account for employer-provided tools and subscriptions. The exact sign-in flow can depend on the VS Code and extension versions, so verify both Settings Sync and the subscription are using the intended accounts.

---

## Git

### Git with Personal and Work Accounts

Keep personal and work repositories in separate parent directories, for example `~/projs/personal/` and `~/projs/work/`. Git's conditional includes can then select the correct author identity automatically for every repository below each directory, without configuring each repository by hand.

In `~/.gitconfig` (see [Git Configuration Files Docs](https://git-scm.com/docs/git-config#FILES)):

```gitconfig
[includeIf "gitdir:~/projs/personal/"]
    path = ~/.gitconfig-personal
[includeIf "gitdir:~/projs/work/"]
    path = ~/.gitconfig-work
```

In `~/.gitconfig-personal`:

```gitconfig
[user]
    name = Your Name
    email = you@example.com
```

In `~/.gitconfig-work`:

```gitconfig
[user]
    name = Your Name
    email = you@company.example
```

#### Use Different Identities for Work Platforms

If you use different Git identities on multiple work platforms, Git can select them by repository directory. For example, keep GitHub repositories under `~/projs/work/github/` and Bitbucket repositories under `~/projs/work/bitbucket/`. Add these more-specific conditions to `~/.gitconfig` after the general `~/projs/work/` condition so these identities override the default work identity for repositories in those directories:

```gitconfig
[includeIf "gitdir:~/projs/work/github/"]
    path = ~/.gitconfig-work-github
[includeIf "gitdir:~/projs/work/bitbucket/"]
    path = ~/.gitconfig-work-bitbucket
```

In `~/.gitconfig-work-github`:

```gitconfig
[user]
    name = Your Name
    email = you@github-company.example
```

In `~/.gitconfig-work-bitbucket`:

```gitconfig
[user]
    name = Your Name
    email = you@bitbucket-company.example
```

The platform is not detected from the remote URL; the repository's location determines which identity is included. Use the matching directory when cloning, and add another condition and config file for each additional platform if needed. Verify from a repository under each directory with `git config --show-origin --get user.email`; the output should name the corresponding `.gitconfig-work-*` file.

> If the Git author name and email are the same across your work platforms, you do not need separate platform-specific identity files; use the general `~/.gitconfig-work` identity above. You may still need separate SSH aliases or keys to authenticate to different platforms or accounts; see [Configure Multiple Work Git Platforms](#configure-multiple-work-git-platforms).

#### Verify the Git Identity

Run this from inside a personal repository to see which configuration file supplies the identity (after cloning the repository as explained in the [Clone or Update a Repository](#clone-or-update-a-repository) section):

```bash
cd ~/projs/personal/repo
git config --show-origin --get user.name
git config --show-origin --get user.email
```

The output should identify `.gitconfig-personal` as the source of both values. Repeat from a work repository under `~/projs/work/`; it should identify `.gitconfig-work`. If another file such as the repository's `.git/config` appears, a more specific setting may be overriding the included identity. For example:

```bash
...:~/projs/personal/DevHub$ git config --show-origin --get user.name
file:/home/poetoec/.gitconfig-personal  CollinPoetoehena
```

### Git Authentication with SSH

> **Note:** The examples use GitHub, but the SSH setup is a Git workflow, not a GitHub-specific one. GitLab, Bitbucket, and other Git platforms use the same SSH keys, agent, and client configuration pattern. The host aliases below (`git-personal` and `git-work`) are local names and do not identify a platform; keep them when changing providers, and update `HostName` and the repository path in remote URLs to match the provider. This lets you switch platforms without renaming the aliases or changing the rest of your SSH workflow. See the platform's documentation for its exact host and repository URL format.

SSH is useful when you use personal and work accounts on a Git platform because separate keys and host aliases make each repository select the intended account, without repeatedly switching HTTPS credentials or managing personal access tokens. HTTPS is also a valid choice; use it if it better fits your tools or organization. For GitHub-specific details, see [Connecting to GitHub with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) and [Contributing to multiple accounts using SSH and multiple keys](https://docs.github.com/en/account-and-profile/how-tos/account-management/managing-multiple-accounts#contributing-to-multiple-accounts-using-ssh-and-multiple-keys).

> **Protected environments:** In this setup, I do interactive development on a local workstation (e.g. a company laptop): VS Code runs there as my editor, and that workstation performs my routine Git operations. Management servers and protected workloads are for administering or running services, not for my personal development workflow, so I do not run VS Code, use personal repositories, or need to switch between personal and work Git accounts there. SSH being blocked from those servers therefore does not prevent the workflow described here. If a server-side job needs repository access, use the authentication method and network route approved for that environment, such as HTTPS with an organization-managed token, deploy token, or service account. Such a job normally needs one organization-controlled identity, not my personal account on a Git platform. Do not copy personal SSH keys or use personal credentials there. If your setup requires running VS Code remotely, treat that as a separate workflow and follow the environment's access policies.

If you do not already have keys, create one for each account:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_personal -C "you@example.com"
ssh-keygen -t ed25519 -f ~/.ssh/id_work -C "you@company.example"
```

Set a passphrase when prompted, then add each corresponding `.pub` public key to the matching account on your Git platform. Keep the private key files private. If your work Git platform uses a separate host, use that host name in the work SSH configuration instead of `github.com`.

In `~/.ssh/config` (see [SSH Config Docs](https://www.ssh.com/academy/ssh/config)):

```sshconfig
# Git configs for personal and work accounts
Host git-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_personal
    IdentitiesOnly yes

Host git-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_work
    IdentitiesOnly yes
```

Test authentication with each SSH key to ensure it is correctly configured:

```bash
ssh -T git@git-personal
ssh -T git@git-work
```

The response depends on the Git platform and its SSH setup. Look for confirmation that the key was accepted; interactive shell access is usually disabled for Git SSH connections. For example, GitHub may respond `Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.` Bitbucket Server may instead report `shell request failed on channel 0`. This can be correct if it appears after the SSH key is accepted: `ssh -T` makes an SSH connection without running a Git command, so the server may reject the requested shell even though it allows Git operations over SSH. The shell-request message alone does not prove authentication succeeded; check for a preceding authentication failure, and verify access with an operation on a repository you are allowed to use, such as `git ls-remote <ssh-repository-url>`. Check your platform's documentation if the response is unclear.

#### Configure Multiple Work Git Platforms

If your work uses more than one Git platform, add a separate `Host` entry for each platform/account in `~/.ssh/config`. Give each entry a distinct local alias, and set `HostName` to that platform's SSH host. For example:

```sshconfig
# Work GitHub
Host git-work-github
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_work
    IdentitiesOnly yes

# Work Bitbucket (example with a custom Git server and a specific port)
Host git-work-bitbucket
    HostName git.<company>.org
    User git
    Port 7999
    IdentityFile ~/.ssh/id_work
    IdentitiesOnly yes

# Work Azure DevOps
Host git-work-azure
    HostName ssh.dev.azure.com
    User git
    IdentityFile ~/.ssh/id_work
    IdentitiesOnly yes
```

These aliases are examples; use each provider's SSH host, repository URL format, and account requirements. The key setup and authentication checks are otherwise the same: add the public key to the relevant platform account, then test each alias with `ssh -T git@<alias>` (for example, `ssh -T git@git-work-bitbucket`). For clarity, the main walkthrough above keeps just one personal and one work alias, but the same pattern extends to as many platforms or accounts as you need. Use the selected alias in the repository's SSH remote URL, such as `git@git-work-bitbucket:workspace/repo.git`.

#### Load Keys into an SSH Agent

An SSH agent keeps unlocked keys available so you do not have to enter each passphrase for every Git operation. To start an agent and load the keys manually in a terminal:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_personal
ssh-add ~/.ssh/id_work
```

The agent asks for each key's passphrase when it is added. To avoid repeating this in every terminal, use your operating system's SSH agent or keyring and add the keys once per login/session. On systems where you want the shell to start or reuse an agent, install `keychain`; it can manage the agent and reuse it across terminal sessions.

To add the command to your shell startup file (recommended; ensures the SSH agent is available in every terminal session and avoids repeatedly entering passphrases):

1. Check your shell with `echo "$SHELL"`. For Bash, the interactive startup file is usually `~/.bashrc`; for Zsh, it is usually `~/.zshrc`.
2. Open the appropriate file in a text editor, add the following line, and save it:
```bash
# Git setup (work and personal)
eval "$(keychain --eval --quiet ~/.ssh/id_personal ~/.ssh/id_work)"
ssh-add -l
# Or alternatively, you can add each key separately if keychain is not possible:
# ssh-add ~/.ssh/id_personal
# ssh-add ~/.ssh/id_work
```
3. Apply the change by opening a new terminal, or run `source ~/.bashrc` for Bash or `source ~/.zshrc` for Zsh in the current terminal.

Keychain may ask you to unlock each key the first time it starts or when its agent needs to be reloaded. It reuses the agent for later terminals, and the passphrases are not stored in the startup file. These file names apply to Bash and Zsh; other shells use different startup files and syntax. Follow your employer's requirements for protecting work keys.

To remove keys from the running agent (e.g. if you no longer need them in the current session or want to test without keys already loaded), remove one identity at a time or clear all loaded identities:

```bash
ssh-add -d ~/.ssh/id_personal
ssh-add -d ~/.ssh/id_work
# Remove every identity currently loaded in the agent instead:
ssh-add -D
```

These commands unload identities from the current SSH agent; they do not delete private-key files. This also applies when Keychain manages the agent: Keychain starts or reuses an SSH agent rather than storing a separate copy of your keys.

#### Clone or Update a Repository

Clone each repository into the matching directory and use the SSH host alias for the account that owns it, such as:

```bash
git clone git@git-personal:you/repo.git ~/projs/personal/repo
git clone git@git-work:company/repo.git ~/projs/work/repo
```

For a repository that is already cloned, check its current remote and replace it with the matching SSH URL. If the remote has a different name, use that name instead of `origin`:

```bash
git remote -v
git remote set-url origin git@git-work:company/repo.git
```

Use the personal alias instead for a personal repository. If the existing repository is outside the matching `~/projs/personal/` or `~/projs/work/` directory, move it under the appropriate directory so Git's conditional include selects the right author identity. After this one-time setup, the repository path selects the commit name and email, and the remote's SSH alias selects the account on the Git platform. When using another provider, update its `HostName` and the repository path format as needed. Protect private keys and follow your employer's rules for work credentials and repositories.