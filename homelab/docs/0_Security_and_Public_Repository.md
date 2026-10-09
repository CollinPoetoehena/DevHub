# Security and Public Repository

The homelab is documented in the public DevHub repository so others can learn from and reuse it, and so it can serve as a portfolio of the design and automation work. Public visibility is intentional; exposing information that could identify or provide access to the real network is not.

This document is the central reference for homelab security in this public repository. It defines what information may be documented, how secrets must be managed, and how to review content before publishing. Use it as the baseline when creating or updating homelab documentation, configuration, automation, and other repository content.

## Table of Contents

- [Security Principles](#security-principles)
- [Information That Must Not Be Published](#information-that-must-not-be-published)
- [Information That Is Usually Safe to Document](#information-that-is-usually-safe-to-document)
- [Secrets Management Rules](#secrets-management-rules)
  - [Ansible](#ansible)
  - [CI/CD](#cicd)
  - [GitOps and Workloads](#gitops-and-workloads)
  - [Terraform and Infrastructure State](#terraform-and-infrastructure-state)
- [Review Before Publishing](#review-before-publishing)
- [If Sensitive Information Is Exposed](#if-sensitive-information-is-exposed)
- [Related Documentation](#related-documentation)

---

## Security Principles

Assume that everything committed or uploaded here is permanently public, even if it is later deleted. Apply least privilege to accounts, credentials, firewall rules, and ACLs, and keep access limited to only the sources and services that need it. Good network controls reduce risk but do not make disclosure of a credential or real internet-facing endpoint safe.

When uncertain, do not publish the real value. Replace it with a safe example or placeholder, and ask for a security review (e.g. with AI) before sharing anything whose impact is unclear.

---

## Information That Must Not Be Published

Do not commit, upload, or include in screenshots, logs, examples, issue reports, or generated artifacts anything that could provide access to the real environment or help an attacker target it. This includes information embedded in metadata and values that seem harmless when considered individually but become identifying when combined.

- Real public IPv4 addresses, globally routable IPv6 addresses or prefixes, public DNS records, hostnames, and domain names used by the homelab.
- Passwords, API tokens, session cookies, access keys, recovery codes, private keys, certificates, pre-shared keys, vault passwords, and other credentials.
- VPN configuration that reveals a real endpoint, peer identity, routes, keys, certificates, or credentials.
- Unredacted router, firewall, switch, hypervisor, cloud, or service configuration exports that reveal sensitive values or access paths.
- Terraform state, saved plans, state backups, crash logs, or generated files that may contain credentials or infrastructure details.
- Logs, terminal output, screenshots, diagrams, backups, inventory files, or support bundles containing any of the above.
- Personal information or metadata that unnecessarily identifies household members, physical location, accounts, device identifiers, or routines.

Never use a real secret, endpoint, or domain in an example, even temporarily. Use nonfunctional placeholders such as `<REDACTED>` or `<YOUR_SECRET>`, reserved example domains such as `example.com`, and documentation-only IP ranges such as `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, and `2001:db8::/32`.

---

## Information That Is Usually Safe to Document

Documenting the design and security controls is useful and generally appropriate, provided the content does not expose real access details or allow the actual environment to be identified. Review each case in context rather than treating this list as an unconditional approval.

- Private IPv4 ranges such as RFC 1918 subnets, subnet plans, VLAN IDs, and network topology.
- Firewall and ACL intent, example rules, and descriptions of which sources or services should be allowed.
- Software, protocol, and package versions; architecture decisions; and reproducible setup instructions.
- Sanitized examples using reserved addresses and placeholder names instead of values taken from the live environment.

Private addressing and a VLAN number are not secrets by themselves, but do not assume every detail is safe simply because it is private. Remove real public endpoints, unique identifiers, credentials, and unnecessary clues about the physical location or operating schedule. Use example values consistently so readers do not mistake them for live configuration.

---

## Secrets Management Rules

Secrets must not be stored in plaintext in tracked files, source code, documentation, commit messages, or command examples. Use a secrets mechanism appropriate to the tool, protect its decryption credentials separately, and ensure secrets are injected only where and when they are needed.

### Ansible

Use Ansible Vault for Ansible secrets that need to be versioned with this repository. An encrypted vault file is safe to commit only while its password and all unencrypted copies remain outside Git and are securely stored.

- The local setup creates `ansible/group_vars/all/vault.yml` as an encrypted vault file; verify it is encrypted before committing.
- Keep the vault password file outside the repository, restrict its filesystem permissions, and do not share or commit it.
- Keep private keys themselves outside the repository. Store only encrypted secret values in the vault when automation truly needs them.
- Do not print decrypted values in task output, debugging logs, diffs, or CI logs; use Ansible's `no_log` for tasks that handle secrets.
- If the vault password or plaintext vault contents may have been exposed, rotate affected credentials and re-encrypt the vault with a new password.

### CI/CD

Store CI credentials in the CI platform's protected secret store or an approved external vault, scope them to the required repository, environment, and job, and provide them at runtime. A CI secret store does not make a credential safe if it is also present in source, logs, artifacts, or a previously published commit.

- Prefer short-lived credentials and narrowly scoped permissions; use environment protections and approval gates for sensitive deployment jobs.
- Do not hard-code credentials in workflow YAML, scripts, container build arguments, or test fixtures.
- Prevent secrets from being printed, uploaded as artifacts, or exposed to untrusted pull-request code.
- Rotate credentials if their visibility or use is uncertain, including after accidental logging.

### GitOps and Workloads

Follow the selected secrets-management design for repository-managed workloads. The software design documents SOPS with age for encrypted secrets in Git; encrypt before committing, protect the age private key separately, and verify that plaintext files and decryption keys are not staged.

- Do not treat Kubernetes Secret objects as encrypted merely because their values are base64-encoded; secure encryption at rest and access control must be configured independently.
- Do not commit rendered manifests, Helm values, or generated artifacts containing decrypted secrets.
- Use HashiCorp Vault or another external vault only when its access, availability, backup, recovery, and operational responsibilities are understood and deliberately configured.
- Do not store decryption keys alongside the encrypted files they unlock.

### Terraform and Infrastructure State

Treat Terraform state, plans, and backups as sensitive because they can contain secret values and detailed infrastructure data. A `sensitive` variable or output only redacts display in some contexts; it does not encrypt the value or remove it from state.

- Do not commit state files, state backups, saved plans, crash logs, or `.tfvars` files containing real secrets.
- Use a secured remote backend with encryption, strict access controls, and appropriate locking and backup protections.
- Keep credentials out of configuration and source-controlled variable files; provide them through an approved runtime secret mechanism.
- Add local state and secret-bearing files to `.gitignore`, and confirm they are not already tracked before relying on the ignore rule.

---

## Review Before Publishing

Review the staged diff and every file being uploaded, not only the source code. Search for credentials, public addresses and domains, VPN details, real hostnames, identifiers, metadata, and generated state; inspect screenshots, command output, diagrams, logs, and artifacts as carefully as configuration files.

- Use reserved examples such as `example.com`, `192.0.2.10`, `198.51.100.10`, `203.0.113.10`, and `2001:db8::10`; use clearly nonfunctional placeholders such as `<REDACTED>` for secret values.
- Check the full change with tools such as a secret scanner where available, but do not treat automated scanning as a substitute for manual review.
- Use `.gitignore` for local secret files and generated state, while remembering that ignore rules do not remove files already tracked or prevent secrets from being included through other paths.
- Check commits, branches, release assets, CI logs, and uploaded artifacts, not just the current working tree.

---

## If Sensitive Information Is Exposed

Assume an exposed credential or access-enabling detail has been copied and may be used, even if it was visible only briefly or has already been deleted. Prioritize containing access and notifying the appropriate account or system owners; repository history cleanup alone does not remediate a compromised secret.

- Revoke or rotate exposed passwords, tokens, keys, certificates, and vault credentials; invalidate active sessions where relevant.
- Update affected systems and dependent automation with the replacement credentials, then verify that the old credentials no longer work.
- Review relevant account, network, and service logs for unexpected access.
- Remove the exposed content from the current files and prevent it from recurring; assess whether Git history, forks, caches, or artifacts also need remediation.
- Report the exposure through the appropriate project or platform security process if other people or systems may be affected.

---

## Related Documentation

See [Local Environment Setup](./2_Setup/1_Setup_Local_Environment.md) for this repository's Ansible Vault workflow, [Network Setup](./2_Setup/2_Setup_Network.md) for network-specific guidance, [Software Prerequisites](./1_Design/2_Design_Software_Prerequisites.md#secrets-management) for the homelab's secrets-management design, and the [homelab project skill](../../.github/skills/homelab-project/SKILL.md) for AI assistants working in this repository.
