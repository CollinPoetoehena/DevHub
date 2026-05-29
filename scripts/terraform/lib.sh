#!/bin/bash
# =============================================================================
# Terraform utility functions
# =============================================================================
# Shared helper functions for Terraform-related scripts. Source this file after
# load_config.sh to make these utilities available.
#
# Azure Account Isolation
# -----------------------
# This project uses AZURE_CONFIG_DIR=~/.azure-<project> to keep its Azure
# credentials completely separate from any other Azure environment you use
# (e.g. a work subscription) to avoid accidentally modifying resources in the wrong environment.
#
# How it works:
#   - 'az login' and all 'az' commands in this project read/write ~/.azure-<project>
#     instead of ~/.azure. Azure CLI normally reads/writes credentials, subscriptions
#     and tokens to ~/.azure by default, unless AZURE_CONFIG_DIR is set. Setting
#     AZURE_CONFIG_DIR redirects ALL az CLI operations to a different directory, so
#     'az login' here writes to ~/.azure-<project> and never touches ~/.azure.
#   - The Terraform 'azurerm' provider (CLI auth) also reads AZURE_CONFIG_DIR, so
#     'terraform plan/apply' automatically uses the credentials from the project
#     config set above.
#   - Because 'export' is used, the variable is inherited by all child processes in
#     the same terminal session (az, terraform, ansible, etc.) spawned from scripts
#     that source this file.
#   - The isolation is session-scoped — only the current terminal and its child
#     processes are affected. Any new terminal window defaults back to ~/.azure
#     (your work config for example) automatically, since it does not have
#     AZURE_CONFIG_DIR set and will use ~/.azure as normal.
#
# Switching back to your work Azure account:
#
#   # Option 1: Just open a new terminal — AZURE_CONFIG_DIR won't be set there.
#
#   # Option 2: Unset the variable in the current session to restore the default
#   #           (only needed if you are using the same terminal session).
#   unset AZURE_CONFIG_DIR
#
#   # Verify which account is active at any time:
#   echo "Config dir: ${AZURE_CONFIG_DIR:-~/.azure (default)}"
#   az account show --query name -o tsv
# =============================================================================

# Utility function:
# Validate AZURE_CONFIG_DIR is set to the expected specific path.
#
# Usage:
#   check_azure_config_dir <expected_path>
#
# Example:
#   check_azure_config_dir "${HOME}/.azure-${PROJECT_NAME}"
#
# NOTE: AZURE_CONFIG_DIR must also be set in the calling shell session before running any
# script that interacts with Azure (az CLI, Terraform). Setting it only inside load_config.sh
# is not sufficient for commands run directly in the terminal — exported variables in a child
# process do not propagate back to the parent shell. For scripts that source load_config.sh
# the variable IS available, but the explicit check below guards against accidental overrides.
# Therefore, it is defined here in lib.sh and can be called by any Terraform script that
# sources it to ensure the correct Azure environment is targeted.
#
# This isolation is critical: if AZURE_CONFIG_DIR is wrong (or unset, falling back to ~/.azure),
# any az or Terraform call could authenticate against a different subscription — e.g. a work
# environment — and accidentally create, modify or destroy resources there.
check_azure_config_dir() {
    local expected="$1"
    if [ -z "$expected" ]; then
        log_error "check_azure_config_dir: expected path argument not provided."
        exit 1
    fi
    if [ -z "${AZURE_CONFIG_DIR:-}" ]; then
        log_error "AZURE_CONFIG_DIR is not set. Export it before running this script:"
        echo "  export AZURE_CONFIG_DIR=\"${expected}\""
        exit 1
    fi
    if [ "$AZURE_CONFIG_DIR" != "$expected" ]; then
        log_error "AZURE_CONFIG_DIR is set to '$AZURE_CONFIG_DIR', but expected '$expected'."
        log_error "This may cause Azure CLI and Terraform to authenticate against the wrong subscription and modify resources there. Please set AZURE_CONFIG_DIR to the expected path before running this script:"
        echo "  export AZURE_CONFIG_DIR=\"${expected}\""
        exit 1
    fi
    log_success "AZURE_CONFIG_DIR: ${AZURE_CONFIG_DIR}"
}
