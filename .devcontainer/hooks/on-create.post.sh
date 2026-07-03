#!/bin/bash
#
# .devcontainer/hooks/on-create.post.sh - Personal on-create hook
#
# Runs after the main on-create setup (volume ownership fix). This file is
# protected from template sync (.devcontainer/hooks/ is in .templatesyncignore).
#

set -euo pipefail

_ai_config_dir="$HOME/ai-config"

# Fix ownership of the ai-config volume mount point (Docker creates it as root:root).
sudo chown vscode:vscode "$_ai_config_dir"

# Symlink AI tool paths into the shared ai-config volume so they persist
# across container rebuilds.
mkdir -p "$_ai_config_dir/.claude"
ln -sfn "$_ai_config_dir/.claude" "$HOME/.claude"

unset _ai_config_dir
