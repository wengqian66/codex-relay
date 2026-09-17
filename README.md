# codex-relay

在 WSL 中管理 Codex CLI 中转服务的轻量 Python 命令行工具。它会切换中转 URL 和 API Key，写入 Codex 所需配置，并从中转服务刷新可用模型目录。

## 特性

- 以 `codex-relay` 命令管理多个中转配置。
- 切换中转时同步更新 `~/.codex/config.toml`、`~/.codex/auth.json` 和模型目录。
- 中转数据保存在 `~/.codex/relays.json`，新建文件权限为 `600`。
- `current` 仅显示 API Key 的前 8 位和后 4 位，便于识别且避免完整回显。
- `quota` 通过当前中转的 `GET /v1/usage` 查询可用状态与剩余额度，且不会回显 API Key。
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

## 用 Codex Skill 安装

仓库内提供可复用的 Skill：[`skills/codex-relay-install`](skills/codex-relay-install)。其他 Linux/WSL 用户可让自己的 Codex 智能体安装该 Skill，再让它完成 `codex-relay` 的安装、更新和验证。

如果目标环境包含 Codex 的 `skill-installer`，可执行：

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo wengqian66/codex-relay \
  --path skills/codex-relay-install
```

安装 Skill 后，在下一轮对话中直接让智能体“安装或更新 codex-relay”。Skill 不会要求把 API Key 发到聊天中；配置中转时会提供本地终端命令模板，由用户自行输入密钥。

## 使用

```sh
codex-relay list                          列出所有中转（* 为当前）
codex-relay current                       显示当前中转详情
codex-relay use <名字>                    切换到该中转，并拉取模型列表
codex-relay sync                          刷新当前中转的模型列表
codex-relay quota [名字]                   查询当前或指定中转的剩余额度
codex-relay add <名字> <url> <key> [显示名]  新增一套中转
codex-relay rename <旧名> <新名>          重命名中转（可用 mv）
codex-relay rm <名字>                     删除中转（不能删当前）
codex-relay help                          显示本帮助
```

`quota` 会向 `<URL>/v1/usage` 发送带 Bearer API Key 的只读请求，并兼容下列响应字段：

- 剩余额度：`remaining`、`quota.remaining` 或 `balance`
- 单位：`unit`、`quota.unit`，缺失时显示 `USD`
- 有效状态：`is_active` 或 `isValid`，缺失时默认显示为有效

若中转未实现 `/v1/usage` 或返回非 JSON，命令会输出请求失败原因；不会在输出中显示 API Key。
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
python3 -m unittest discover -s tests -v
command -v codex-relay
codex-relay help
codex-relay quota
```
