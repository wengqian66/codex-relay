#!/bin/sh
# Install codex-relay for the current WSL user without modifying credentials.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CODEX_HOME=${CODEX_HOME:-"$HOME/.codex"}
BIN_DIR="$HOME/.local/bin"
TARGET="$BIN_DIR/codex-relay"
CONFIG_PATH="$CODEX_HOME/config.toml"
RELAYS_PATH="$CODEX_HOME/relays.json"
BASHRC="$HOME/.bashrc"

command -v python3 >/dev/null 2>&1 || {
    printf '%s\n' 'python3 is required but was not found in PATH.' >&2
    exit 1
}

if ! command -v codex >/dev/null 2>&1; then
    printf '%s\n' 'warning: codex was not found in PATH; the relay command will install, but Codex itself must be installed separately.' >&2
fi

mkdir -p "$BIN_DIR" "$CODEX_HOME"
install -m 700 "$SCRIPT_DIR/codex-relay" "$TARGET"

if [ ! -e "$CONFIG_PATH" ]; then
    umask 077
    cat >"$CONFIG_PATH" <<'EOF'
model_provider = "custom"
model = "placeholder"
model_catalog_json = "cc-switch-model-catalog.json"

[model_providers.custom]
name = "placeholder"
base_url = "https://placeholder.invalid"
wire_api = "responses"
requires_openai_auth = true
EOF
    printf 'created %s\n' "$CONFIG_PATH"
else
    printf 'kept existing %s unchanged\n' "$CONFIG_PATH"
fi

if [ ! -e "$RELAYS_PATH" ]; then
    umask 077
    cat >"$RELAYS_PATH" <<'EOF'
{
  "current": null,
  "preferred_models": [],
  "relays": {}
}
EOF
    chmod 600 "$RELAYS_PATH"
    printf 'created %s with mode 600\n' "$RELAYS_PATH"
else
    printf 'kept existing %s unchanged\n' "$RELAYS_PATH"
fi

PATH_EXPORT='export PATH="$HOME/.local/bin:$PATH"'
touch "$BASHRC"
if ! grep -Fqx "$PATH_EXPORT" "$BASHRC"; then
    printf '\n%s\n' "$PATH_EXPORT" >>"$BASHRC"
    printf 'added ~/.local/bin to %s\n' "$BASHRC"
else
    printf '~/.local/bin PATH entry already exists in %s\n' "$BASHRC"
fi

python3 -m py_compile "$TARGET"

export PATH="$BIN_DIR:$PATH"
command -v codex-relay
codex-relay help

printf '%s\n' 'Installation complete. Open a new WSL terminal before using codex-relay in other shells.'
