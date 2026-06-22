#!/bin/bash

# Shared configuration variables for all scripts, such as utility functions, constants, etc.
# Source this file to load configuration: source "$(dirname "$0")/path/to/load_config.sh"

# Exit immediately if a command exits with a non-zero status (error)
set -e

# Check if configuration is already loaded (avoids loading config multiple times)
# :- means "use default value if variable is not set" to prevent unbound variable error when CONFIG_LOADED is not set
# Add check in this script to avoid having to add this check in all sub-scripts that source this file
if [ -n "${CONFIG_LOADED:-}" ]; then # Use default value of empty string if CONFIG_LOADED is not set to avoid unbound variable error
    echo "Configuration already loaded, skipping..."
    # Return (0 means success) from sourcing this file without executing the rest of the script, 
    # allowing the calling script to continue execution after sourcing the config
    return 0
else
    echo "Configuration not yet loaded, loading configuration now..."
fi

# Determine the root project directory
# This checks if PROJECT_ROOT is already set (to allow override), and if not:
# 1. ${BASH_SOURCE[0]} gets the path to this script file (load_config.sh)
# 2. cd .. navigates to the parent directory of the script (assuming this script is in a subdirectory of the project root)
# 3. dirname extracts the directory containing this script
# 4. pwd gets the absolute path, which is the project root
# Result: PROJECT_ROOT will be set to the absolute path of the project root directory
# :- to use default value of empty string if PROJECT_ROOT is not set to avoid unbound variable error
if [ -z "${PROJECT_ROOT:-}" ]; then
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

# Script directory
SCRIPTS_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Name of the calling project, derived from the current working directory so this shared
# script works correctly when invoked from any project (e.g. k8s-lab, dev-hub, etc.).
# Using $PWD rather than PROJECT_ROOT because PROJECT_ROOT always resolves to the directory
# where this script lives (dev-hub), not the project the caller is operating on.
PROJECT_NAME="$(basename "$PWD")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Display loaded configuration
echo "Loaded configuration:"
echo "  PROJECT_ROOT: $PROJECT_ROOT"
echo "  PROJECT_NAME: $PROJECT_NAME"
echo "  SCRIPTS_ROOT_DIR: $SCRIPTS_ROOT_DIR"
echo 

# Functions to display colored messages
log_debug() {
    echo -e "${CYAN}[DEBUG] ${NC}$1"
}

log_info() {
    echo -e "${BLUE}[INFO] ${NC}$1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] ${NC}$1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] ${NC}$1"
}

log_error() {
    echo -e "${RED}[ERROR] ${NC}$1"
}

log_header_1() {
    echo ""
    echo -e "${GREEN}===========================================================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}===========================================================================${NC}"
    echo ""
}

log_header_2() {
    echo ""
    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    echo ""
}

log_header_3() {
    echo ""
    echo -e "${YELLOW}[INFO]  --- $1 ---${NC}"
    echo ""
}

# Add clarifying message to display config is loaded and the specific script can continue (e.g. version upgrade script)
echo "Configuration loaded successfully, continue with specific script execution..."
echo "" # Add newline for better readability in the terminal when multiple scripts are executed sequentially
# Mark configuration as loaded
CONFIG_LOADED=1