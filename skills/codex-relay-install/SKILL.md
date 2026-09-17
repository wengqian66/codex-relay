---
name: codex-relay-install
description: Install, update, configure, or verify the codex-relay CLI on Linux or WSL. Use when a user wants Codex relay switching or quota checks set up on their own machine; not for native Windows or macOS.
---

# Codex Relay Install

Install or update the `codex-relay` command from `wengqian66/codex-relay`. It manages locally stored relay endpoints and API keys for Codex, refreshes model catalogs, and can query a relay's remaining quota.

## Safety and scope

- Use only on Linux or WSL. For native Windows or macOS, explain that this repository's installer is Linux/WSL-specific rather than attempting an untested installation.
- Obtain approval before cloning, updating, or running the installer because it writes under `~/.local`, `~/.codex`, and possibly `~/.bashrc`.
- Never ask the user to paste an API key into chat, source code, a commit, or a logged shell command. Provide a command template with `<API_KEY>` and let the user enter the secret locally.
- Do not overwrite an unrelated local clone, force-reset a repository, or replace existing `~/.codex/config.toml` / `relays.json`. The bundled installer preserves existing files.

## Install or update

1. Confirm the OS is Linux/WSL and that `python3` and `git` are available. `codex` itself may be absent during installation, but say that it must be installed before the relay is useful.
2. Use a user-owned source checkout, preferably:

   ```sh
   REPO_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/codex-relay"
   ```

   - If `REPO_DIR/.git` does not exist, clone `https://github.com/wengqian66/codex-relay.git` there.
   - If it is an existing clone of that repository, update it with `git pull --ff-only`.
   - If it points to another repository or has local changes, leave it untouched and ask the user whether to choose another directory or resolve the changes.
3. Run the bundled installer from the checkout:

   ```sh
   sh "$REPO_DIR/install-wsl.sh"
   ```

4. Verify installation without contacting any relay:

   ```sh
   python3 -m py_compile "$HOME/.local/bin/codex-relay"
   "$HOME/.local/bin/codex-relay" help
   ```

Tell the user to open a new shell if `~/.local/bin` was newly added to `PATH`.

## Configure a relay

If the user needs a new relay, show this template and have them enter the key directly in their own terminal:

```sh
codex-relay add <NAME> <BASE_URL> <API_KEY> [DISPLAY_NAME]
codex-relay use <NAME>
```

`use` fetches the relay's models and writes the selected endpoint/key to the user's local Codex configuration. If a relay is already configured, use `codex-relay list` or `codex-relay current` first; `current` masks the key.

## Verify quota

Use the following only after a relay has been configured and the user requests a live check:

```sh
codex-relay quota
# or: codex-relay quota <NAME>
```

The command performs a read-only authenticated `GET <BASE_URL>/v1/usage`. It reports active status and remaining balance without printing the API key. Explain that quota querying requires the relay to implement `/v1/usage`; a 404, authorization error, or non-JSON response means that particular relay does not support this capability or needs different credentials.
