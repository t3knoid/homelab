---
title: "Visual Studio Code"
---

# 🧩 Visual Studio Code

This page documents my [Visual Studio Code](https://code.visualstudio.com/download) setup (including VS Code Server and code‑server), the extensions I rely on, and recommended settings for development with Ansible, Python, Terraform, .NET, and general web/dev workflows.

---

## 📘 Summary

- **Environment:** VS Code Server (extensions stored under `~/.vscode-server/extensions`).  
- **Focus Areas:** Linting/formatting, source control, cloud/infra (Terraform, Azure), Python/.NET, Ansible/YAML, Markdown authoring.

---

## 🧩 Extensions

These are the extensions I typically install for a complete development environment.

| Extension ID | Name | Purpose / Usage |
|---|---|---|
| `dbaeumer.vscode-eslint` | ESLint | JS/TS linting and auto‑fix on save |
| `eamodio.gitlens` | GitLens | Git history, annotations, authorship |
| `esbenp.prettier-vscode` | Prettier | Opinionated formatter for many languages |
| `github.copilot` | GitHub Copilot | AI‑assisted code suggestions |
| `github.copilot-chat` | Copilot Chat | Chat‑based AI assistance |
| `github.vscode-github-actions` | GitHub Actions | Workflow editing and validation |
| `github.vscode-pull-request-github` | GitHub Pull Requests | PR and issue integration |
| `hashicorp.terraform` | Terraform | HCL language support, formatting, linting |
| `ms-azuretools.vscode-azureterraform` | Azure Terraform | Azure‑specific Terraform helpers |
| `ms-azuretools.vscode-containers` | Containers | Docker/Compose tooling |
| `ms-dotnettools.csdevkit` | C# Dev Kit | Enhanced .NET development |
| `ms-dotnettools.csharp` | C# | C# language support (OmniSharp) |
| `ms-dotnettools.vscode-dotnet-runtime` | .NET Runtime | Manage .NET runtimes |
| `ms-python.debugpy` | debugpy | Python debugging |
| `ms-python.python` | Python | Python language support, testing, envs |
| `ms-python.vscode-pylance` | Pylance | Fast Python language server |
| `ms-python.vscode-python-envs` | Python Envs | Python environment discovery |
| `msjsdiag.vscode-react-native` | React Native | React Native development |
| `redhat.ansible` | Ansible | Playbook syntax, snippets, language features |
| `redhat.vscode-yaml` | YAML | YAML language server with schema support |
| `yzhang.markdown-all-in-one` | Markdown All‑in‑One | Markdown authoring tools |

---

## ⚙️ Recommended Key Settings

These settings can be added to your user `settings.json` or overridden per‑project in `.vscode/settings.json`.

### ✏️ Editor & Formatting
- `"editor.formatOnSave": true` — auto‑format on save  
- `"files.trimTrailingWhitespace": true` — remove trailing whitespace  
- `"editor.codeActionsOnSave": { "source.fixAll": true, "source.fixAll.eslint": true }` — apply ESLint and other fixes  
- Language‑specific formatters:
  - `"[javascript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" }`
  - `"[yaml]": { "editor.defaultFormatter": "redhat.vscode-yaml" }`

### 🐍 Python
- `"python.languageServer": "Pylance"` — preferred for type checking and completions  
- Configure your formatter (`black`, `autopep8`, `ruff`) based on project standards

### 🌍 Terraform
- `"terraform.formatOnSave": true` — or use the HashiCorp extension’s built‑in formatting

### 📄 YAML & Ansible
- `"yaml.validate": true`  
- Add schema mappings if using custom playbook schemas

### 🔧 Git & Source Control
- `"git.autofetch": true`  
- `"git.confirmSync": false"` — optional, speeds up workflow

---

## 🖥️ VS Code Server / code‑server Notes

- VS Code Server extensions live under:  
  - `~/.vscode-server/extensions`  
  - or `~/.local/share/code-server/extensions` (code‑server)
- Keep server‑side extensions updated to avoid client/server mismatches.

---

## 📂 Where `settings.json` Lives

| Context | Path |
|---|---|
| Workspace | `.vscode/settings.json` |
| User (Linux) | `~/.config/Code/User/settings.json` |
| VS Code Server | `~/.vscode-server/data/Machine/settings.json` |
| code‑server | `$XDG_CONFIG_HOME/code-server/User/settings.json` or `~/.local/share/code-server/User/settings.json` |

---

## 🧪 Sample `settings.json`

Use this as a starting point and adjust paths/formatters as needed.

{% raw %}
```json
{
  "ansible.python.interpreterPath": "/opt/python_3.12/bin/python3",
  "editor.formatOnSave": true,
  "files.trimTrailingWhitespace": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true,
    "source.fixAll.eslint": true
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[yaml]": {
    "editor.defaultFormatter": "redhat.vscode-yaml"
  },
  "python.languageServer": "Pylance",
  "terraform.formatOnSave": true,
  "yaml.validate": true,
  "git.autofetch": true,
  "git.confirmSync": false
}
```
{% endraw %}

---

## 🌐 Remote Access

VS Code supports seamless access to remote file systems and development environments.

### 🛜 Accessing This Workspace from a Local VS Code Client

- Install **Remote – SSH** (`ms-vscode-remote.remote-ssh`)  
- Use **Remote Explorer** or **Remote‑SSH: Connect to Host…**  
- Connect to `user@host` — VS Code will launch server components automatically  
- For browser‑based access, tools like **code‑server** expose a web UI (e.g., `https://your-server.example.com`) with most editor features

👉 See: **[Hosting a Visual Code Server](hosting_a_visual_code_server.md)**

### 🌐 Using vscode.dev (Browser Fallback)

When no local VS Code or server is available, https://vscode.dev runs entirely in your browser.  
Limitations: no remote terminal, no server‑side extensions, limited debugging.

---

## 🐧 Accessing Code Inside a WSL Container

- Install the **WSL** extension  
- Open the repo  
- Remote Explorer → **WSL Targets**  
- Select your distro (e.g., `Ubuntu-24.04`)  
- Click **Open Folder**

👉 See: [WSL2](wsl2.md)

---

## ⌨️ Common Keyboard Commands

| Linux | macOS | Description |
|---|---|---|
| `Ctrl+Shift+P` / `F1` | `Cmd+Shift+P` / `F1` | Command Palette |
| `Ctrl+P` | `Cmd+P` | Quick Open |
| `Ctrl+Shift+O` | `Cmd+Shift+O` | Go to Symbol |
| `Ctrl+Shift+M` | `Cmd+Shift+M` | Problems panel |
| `F8` / `Shift+F8` | `F8` / `Shift+F8` | Next / Previous problem |
| `` Ctrl+` `` | `` Cmd+` `` | Toggle Terminal |
| `Ctrl+Shift+` ` | `Cmd+Shift+` ` | New Terminal |
| `Ctrl+B` | `Cmd+B` | Toggle Sidebar |
| `Ctrl+Shift+E` | `Cmd+Shift+E` | Focus Explorer |
| `Ctrl+Shift+F` | `Cmd+Shift+F` | Search files |
| `Ctrl+S` | `Cmd+S` | Save |
| `Ctrl+K Ctrl+S` | `Cmd+K Cmd+S` | Keyboard Shortcuts |
| `Ctrl+/` | `Cmd+/` | Toggle line comment |
| `Alt+Up` / `Alt+Down` | `Option+Up` / `Option+Down` | Move line |
| `Shift+Alt+F` | `Shift+Option+F` | Format document |
| `Ctrl+Shift+D` | `Cmd+Shift+D` | Run & Debug |
| `Ctrl+Shift+I` | `Cmd+Shift+I` | Inline suggestions / Format selection |


