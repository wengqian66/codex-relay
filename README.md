# codex-relay

在 WSL 中管理 Codex CLI 中转服务的轻量 Python 命令行工具。它会切换中转 URL 和 API Key，写入 Codex 所需配置，并从中转服务刷新可用模型目录。

## 特性

- 以 `codex-relay` 命令管理多个中转配置。
- 切换中转时同步更新 `~/.codex/config.toml`、`~/.codex/auth.json` 和模型目录。
- 中转数据保存在 `~/.codex/relays.json`，新建文件权限为 `600`。
- `current` 仅显示 API Key 的前 8 位和后 4 位，便于识别且避免完整回显。
- 项目不会保存 API Key；`.gitignore` 会忽略常见本地密钥和 Codex 配置文件。

## 前提条件

- Ubuntu（或其他 Linux）WSL 环境。
- `python3`。
- 已安装且可从 `PATH` 访问的 `codex` 命令。

检查环境：

```sh
command -v python3
command -v codex
printf '%s\n' "$HOME"
test -d ~/.codex && echo '~/.codex exists'
test -f ~/.codex/config.toml && echo '~/.codex/config.toml exists'
```

## 安装

在 WSL 中进入此项目目录并执行：

```sh
./install-wsl.sh
```

脚本会执行以下操作：

1. 安装命令到 `~/.local/bin/codex-relay` 并设为 `700`。
2. 保留已有的 `~/.codex/config.toml`；仅在文件不存在时创建最小可用配置。
3. 仅在 `~/.codex/relays.json` 不存在时创建空配置，并设置为 `600`。
4. 在 `~/.bashrc` 中幂等加入 `~/.local/bin` 的 `PATH` 配置。
5. 运行 `python3 -m py_compile`、`command -v codex-relay` 和 `codex-relay help` 验证安装。

安装后请重新打开 WSL 终端。若只想临时在当前 shell 使用：

```sh
export PATH="$HOME/.local/bin:$PATH"
```

## 使用

```sh
codex-relay add <名称> <URL> <API_KEY> [显示名]
codex-relay list
codex-relay use <名称>
codex-relay current
codex-relay sync
```

示例中的 `<API_KEY>` 只应在你的本地终端输入。不要把 API Key 写入脚本、README、提交记录或 Git 仓库。

## WSL 安装踩坑记录

### Windows 路径与 WSL 路径不同

Windows 的 `D:\wengqian\gitlab_project\sd_new` 在 WSL 中对应 `/mnt/d/wengqian/gitlab_project/sd_new`。安装目标必须是 WSL 用户的 Linux HOME，例如 `/home/boshi/.local/bin/codex-relay`，而不是 Windows 用户目录。

### 指定 WSL 发行版更可靠

多发行版环境中建议明确指定 Ubuntu：

```powershell
wsl.exe -d Ubuntu -- /bin/sh -c 'whoami; pwd'
```

本次环境的 Ubuntu 是 WSL 2；使用 `/bin/sh` 成功访问项目挂载目录。

### 不要在自动化中强制 `source ~/.bashrc`

`.bashrc` 可能包含 Conda 初始化、Docker 启动等副作用，导致登录 Bash 变慢或超时。安装脚本只幂等写入 PATH 配置，并提示重新打开终端；需要临时生效时使用前文的 `export PATH=...`。

### 不覆盖已有 Codex 配置

已有 `~/.codex/config.toml` 时保持原样。只有不存在时才写入以下最小配置：

```toml
model_provider = "custom"
model = "placeholder"
model_catalog_json = "cc-switch-model-catalog.json"

[model_providers.custom]
name = "placeholder"
base_url = "https://placeholder.invalid"
wire_api = "responses"
requires_openai_auth = true
```

### 权限与密钥

API Key 存在 `~/.codex/relays.json` 时，该文件应为 `600`。命令本身设为 `700`。不要将 `~/.codex`、`auth.json`、`relays.json` 或任何真实密钥提交到 Git。

## 验证命令

```sh
python3 -m py_compile ~/.local/bin/codex-relay
command -v codex-relay
codex-relay help
```
