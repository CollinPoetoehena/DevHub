# Setup & Installation: Local Environment

After preparing your hardware and prerequisites, the next step is to set up the local development environment on your laptop. This is a one-time setup that generates an SSH key, installs dependencies, generates the inventory, and configures the Ansible Vault for secrets management.

## Prerequisites

- **Python 3** — required to run Ansible (comes pre-installed on most Linux distributions and macOS; on Windows use WSL)
- **Git** — to clone this repository

## Step 1: Generate an SSH Key Pair

Ansible connects to remote hosts via SSH. You need an Ed25519 key pair on your laptop — this is used for all homelab hosts (the Pi, future VMs, etc.). Generate it once and reuse it everywhere.

```bash
# Generate a new Ed25519 key (modern, compact, fast; recommended over RSA):
ssh-keygen -t ed25519 -C "your-email@example.com"
# Save with appropriate name (e.g., ~/.ssh/id_homelab).
# NOTE: you cannot use "~" in the path prompt — type the full path, e.g. /home/youruser/.ssh/id_homelab
# Enter a passphrase (strongly recommended — protects the key if your laptop is stolen).
#
# This creates two files:
#   ~/.ssh/id_homelab       — private key (NEVER share this)
#   ~/.ssh/id_homelab.pub   — public key  (safe to share; goes on remote hosts)
#
# Make sure to save these files and the passphrase securely (e.g., in a password manager
# like KeePassXC). If you lose the private key, you lose SSH access to all hosts.
```

This key is referenced in `ansible.cfg` as `private_key_file = ~/.ssh/id_homelab` and stored in the Ansible Vault as `vault_ssh_private_key_src_ansibleremote` so the `users` role can deploy the public key to remote hosts.

## Step 2: Install Python venv with Ansible and Run Setup Playbook

```bash
# Go to the Homelab directory:
cd homelab
# NOTE: The venv should be created in the root of this homelab directory so it can be used for all Python related tasks in this repo (not only Ansible, such as if it would be in the ansible directory).

# Create a Python virtual environment and install Ansible:
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install ansible
ansible --version

# Run the local environment setup playbook. See details in the playbook itself, it describes what it does exactly.
# Safe to re-run — skips steps that are already done.
# --diff: show file changes made on the host
cd ansible # Should run playbooks from this directory because this is where ansible.cfg is located
ansible-playbook setup_local_env.yml --diff
```

After this completes, your environment is ready to run playbooks. See the setup playbook itself (`ansible/setup_local_env.yml`) for full details on what each step does, and `ansible/vars/setup_local_env.yml` for how to add new hosts or vault secrets.