#!/usr/bin/env bash

# Ensure AI tool state/config is always writable by the devcontainer user.
# The ai-config volume can accumulate root-owned files after elevated commands.
_ai_config_dir="$HOME/ai-config"
if [[ -d "$_ai_config_dir" ]]; then
    if command -v sudo >/dev/null 2>&1; then
        sudo chown -R "$USER:$USER" "$_ai_config_dir"
    else
        chown -R "$USER:$USER" "$_ai_config_dir"
    fi

    find "$_ai_config_dir" -type d -exec chmod 700 {} +
    find "$_ai_config_dir" -type f -exec chmod 600 {} +
fi
unset _ai_config_dir
