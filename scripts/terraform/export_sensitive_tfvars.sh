#!/bin/bash
# =============================================================================
# Generate terraform.tfvars
# =============================================================================
# Generic script that exports a terraform.tfvars file populated with sensitive
# or environment-specific values that should not be committed to source control.
# Terraform automatically loads terraform.tfvars when running plan/apply.
#
# The exported variables are intentionally generic and reusable across projects:
#   - Cloud authentication details (e.g. Azure subscription ID, resource group)
#   - Your current public IP address (e.g. for firewall / NSG inbound rules)
#   - Infrastructure access credentials (e.g. SSH public key)
#   - Identity references (e.g. Azure AD user object ID for Key Vault policies)
#
# Prerequisites:
#   - Azure CLI installed and authenticated (az login)
#   - SSH key pair already generated at the path passed via --ssh-key
#
# Usage: see the show_usage function below or run with -h/--help for details and examples.
#
# Design:
#   - File exporting: This script exports a file with the generated variables that Terraform reads
#   - Alternative (this was used earlier): load script via "source" or "eval" commands, however, this was aborted
#       because it caused issues with shell session persistence and error handling. For example, the "log" functions like
#       log_info write to stdout, which can interfere with "eval" or "source" when trying to capture variable output, 
#       and also caused issues with error handling (e.g. if a command failed, it could exit the entire shell session 
#       (e.g. tab completion caused it to crash before) because the "set -e" is loaded in the shell session by sourcing this script.)
# =============================================================================

# Dir of this specific script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the shared configurations and utilities
source "$SCRIPT_DIR/../load_config.sh"
source "$SCRIPT_DIR/lib.sh"

# show_usage prints usage information
show_usage() {
    cat <<EOF
Usage: $0 --ssh-key PATH --output-dir DIR [OPTIONS]

Required:
  --ssh-key PATH           Path to SSH public key (e.g. ~/.ssh/id_k8slab.pub)
  -o, --output-dir DIR     Directory to write terraform.tfvars into (e.g. ~/projects/personal/k8s-lab/terraform)

Options:
  --resource-group NAME    Azure resource group name (default: first available)
  --relogin                Force re-authentication to Azure (default: false)
  -h, --help               Show this help message

Example:
  $0 --ssh-key ~/.ssh/id_k8slab.pub --output-dir ~/projects/personal/k8s-lab/terraform
  $0 --ssh-key ~/.ssh/id_k8slab.pub -o ~/projects/personal/k8s-lab/terraform --resource-group my-rg
EOF
}

SSH_KEY_PATH=""
RESOURCE_GROUP=""
RELOGIN=false
OUTPUT_DIR=""

## Parse command line arguments
# Each 'shift 2' advances the positional parameters by two (while the number of args ($#) is greater than 0), 
# effectively consuming the option and its value, so the next option becomes $1 in the next iteration:
#   - 'shift 2' removes $1 and $2 from the argument list (the option and its value),
#     so $3 becomes the new $1, $4 becomes $2, etc.
#   - This ensures that after handling an option and its value, the next unprocessed argument is always $1.
#   - Internally, 'shift' modifies the shell's argument list ($@ and $*) by discarding the specified number of leading arguments.
#   - Example: If the script is called with '--image foo --version 1.0', after processing '--image foo' and 'shift 2',
#     the next $1 is '--version' and $2 is '1.0'.
while [[ $# -gt 0 ]]; do
    case $1 in
        --ssh-key) SSH_KEY_PATH="$2"; shift 2 ;;
        -o|--output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --resource-group) RESOURCE_GROUP="$2"; shift 2 ;;
        --relogin) RELOGIN=true; shift ;;
        -h|--help) show_usage; exit 0 ;;
        *) log_error "Unknown option: $1"; show_usage; exit 1 ;;
    esac
done

if [ -z "$SSH_KEY_PATH" ]; then
    log_error "--ssh-key is required"
    show_usage
    exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
    log_error "--output-dir is required"
    show_usage
    exit 1
fi

##################################################################################################################
# TODO: for my homelab I will also use different providers like Proxmox for creating VMs there, etc.
# TODO: so add in lib the handling function of creating the file, etc., and then based on the used provider
# TODO: such as Azure or Proxmox, etc., call the corresponding function to export the variables needed for that provider, and then
# TODO: add the generic vars always (e.g. my IP, etc.), etc.
##################################################################################################################



# Check Azure config dir for safety to ensure the correct Azure environment is targeted (see: Azure Account Isolation in DevHub/scripts/terraform/lib.sh)
check_azure_config_dir "${HOME}/.azure-${PROJECT_NAME}"

log_header_1 "Terraform tfvars Generator"

# Check if Azure CLI is installed
log_info "Checking prerequisites..."
if ! command -v az &> /dev/null; then
    log_error "Azure CLI is not installed. Please install it first:"
    echo "  https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi
log_success "Azure CLI found"

# If RELOGIN is true, or if not logged in, run 'az login' to authenticate to Azure (can be used when you want to override current login for example)
# NOTE: Currently only Azure authentication is supported. To add support for other cloud providers (e.g. AWS, GCP),
#       extend this section with the corresponding CLI login commands and update the variable exports below accordingly.
log_info "Checking Azure authentication..."
if [ "$RELOGIN" = true ]; then
    log_info "--relogin flag set, forcing re-authentication..."
    # Use device code login for better compatibility in scripts and CI environments
    az login --use-device-code
# Check if logged in to Azure by running 'az account show' and checking for errors. This is a common way to verify if the user is authenticated, as it will return an error if not logged in.
elif ! az account show &> /dev/null; then
    log_error "Not logged in to Azure. Running 'az login'..."
    az login --use-device-code
fi
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
log_success "Logged in to Azure (Subscription: $SUBSCRIPTION_NAME)"

# Get resource group — use provided value or fall back to the first one in the subscription
log_info "Getting resource group..."
if [ -z "$RESOURCE_GROUP" ]; then
    RESOURCE_GROUP=$(az group list --query "[0].name" -o tsv 2>/dev/null)
    if [ -z "$RESOURCE_GROUP" ]; then
        log_error "No resource groups found. Create one first, or pass --resource-group."
        exit 1
    fi
    log_info "Found resource group, using: $RESOURCE_GROUP"
fi

# Get location from resource group
LOCATION=$(az group show --name "$RESOURCE_GROUP" --query location -o tsv)
log_success "Using location: $LOCATION"

# Load SSH public key
log_info "Getting SSH public key..."
if [ ! -f "$SSH_KEY_PATH" ]; then
    log_error "SSH public key not found at: $SSH_KEY_PATH"
    echo "Generate a key pair (without passphrase) with:"
    # Command explanation:
    #   - ssh-keygen: the command to generate SSH keys
    #   - -t rsa: specifies the type of key to create (RSA)
    #   - -b 4096: specifies the number of bits in the key (4096 bits for stronger security)
    #   - -f "${SSH_KEY_PATH%.pub}": specifies the output file for the private key (removing the .pub extension from the provided path)
    #   - -C "azure-k8slab": adds a comment to the key (useful for identifying the key later)
    #   - -N "": specifies an empty passphrase (no password) for the private key, which is common for automated use cases like this
    echo "  ssh-keygen -t rsa -b 4096 -f \"${SSH_KEY_PATH%.pub}\" -C \"azure-k8slab\" -N \"\""
    exit 1
fi
SSH_PUBLIC_KEY=$(cat "$SSH_KEY_PATH")
log_success "SSH public key loaded from: $SSH_KEY_PATH"

# Get user object ID (used for Key Vault access policies)
log_info "Getting Azure AD user object ID..."
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv 2>/dev/null)
if [ -n "$USER_OBJECT_ID" ]; then
    log_success "User object ID found (not logged for security reasons)"
else
    log_info "Could not retrieve user object ID — skipping (optional, used for Key Vault access)"
fi

# Get current public IP — used to restrict SSH inbound to the jump host from the internet (my_ip variable)
# Tries two well-known services; if both fail the script exits rather than writing a permissive wildcard.
log_info "Detecting your current public IP..."
MY_IP=$(curl -s --max-time 5 https://ifconfig.me 2>/dev/null || curl -s --max-time 5 https://checkip.amazonaws.com 2>/dev/null)
if [ -z "$MY_IP" ]; then
    log_error "Could not detect your public IP. Check your internet connection, or set my_ip manually in terraform.tfvars."
    exit 1
fi
# Validate that the result looks like an IPv4 address before using it.
# The regex breakdown:
#   ^           - start of string (no leading characters allowed)
#   [0-9]+      - one or more digits (one octet)
#   \.          - literal dot separator (escaped because '.' means "any char" in regex)
#   (repeated 4 times for the four octets of an IPv4 address: e.g. 93.184.216.34)
#   $           - end of string (no trailing characters, e.g. newlines, allowed)
# '!' negates the match, so the block runs (and exits) when the value does NOT look like an IP.
# This guards against injecting arbitrary content into terraform.tfvars via a compromised curl response.
if ! [[ "$MY_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_error "Unexpected value returned for public IP (not logged for security reasons). Set my_ip manually in terraform.tfvars."
    exit 1
else
    log_success "Public IP detected (not logged for security reasons)"
fi
# Append /32 CIDR suffix to specify a single IP address in the Terraform variable (which expects CIDR notation for network rules)
# CIDR: https://aws.amazon.com/what-is/cidr/ and https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing
MY_IP_CIDR="${MY_IP}/32"

# Write terraform.tfvars to the Terraform root directory.
# Terraform automatically loads this file when running plan/apply — no extra flags needed.
# See: https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files
TFVARS_FILE="$OUTPUT_DIR/terraform.tfvars"
log_info "Writing $TFVARS_FILE..."

cat > "$TFVARS_FILE" <<EOF
# Auto-generated by $0 — do not edit manually
# Re-run the script to refresh these values
subscription_id      = "$SUBSCRIPTION_ID"
resource_group_name  = "$RESOURCE_GROUP"
location             = "$LOCATION"
ssh_public_key       = "$SSH_PUBLIC_KEY"
user_object_id       = "$USER_OBJECT_ID"
my_ip                = "$MY_IP_CIDR"
EOF

log_success "terraform.tfvars written to: $TFVARS_FILE"

# NOTE: these variables are sensitive and therefore NOT added in Git (via .gitignore terraform.tfvars), and also
# NOT logged, such as your Azure credentials and your IP address should not be publicly visible (e.g. in CI logs, etc.)
echo ""
log_success "Done!"
echo ""
echo "Next steps (see /docs/development/README.md):"
echo "  1. cd $OUTPUT_DIR"
echo "  2. Execute Terraform commands, such as \"terraform plan\" or \"terraform apply\", which will automatically load the generated terraform.tfvars"
echo ""
log_info "Note: terraform.tfvars contains sensitive values — it is gitignored."
