---
title: "Minecraft Bedrock Edition Server"
---

# 🧱 Minecraft Bedrock Edition Server

This page documents the **Minecraft Bedrock Edition** server instance deployed and managed through Ansible.  
The deployment is fully automated, version‑controlled, and reproducible using the `bedrock_setup` role.

---

## 📦 Overview

| Component | Description |
|----------|-------------|
| **Edition** | Minecraft **Bedrock Edition** Server |
| **Deployment Method** | Ansible (`bedrock_setup` role) |
| **Playbook** | [`playbooks/minecraft/deploy_bedrock.yml`](https://github.com/t3knoid/ansible/blob/main/playbooks/minecraft/deploy_bedrock.yml) |
| **Inventory** | [`inventory/minecraft/`](https://github.com/t3knoid/ansible/tree/main/inventory/minecraft) |
| **Version Pin** | `bedrock_setup_version: 1.21.132.3` |
| **Source Download** | Official Bedrock server download page |
| **Version Discovery** | Automated via Playwright (`check_bedrock_version.yml`) |

---

## 🧩 Architecture

The Bedrock server is deployed as a standalone Linux host managed through Ansible.  
All configuration is stored in Git and applied idempotently.

### Key Components

- **Ansible Role:**  
  [`roles/bedrock_setup`](https://github.com/t3knoid/ansible/tree/main/roles/bedrock_setup)  
  Handles:
  - Downloading the Bedrock server package
  - Extracting and installing the server
  - Managing service files
  - Applying configuration templates
  - Ensuring correct permissions and directory layout

- **Deployment Playbook:**  
  [`deploy_bedrock.yml`](https://github.com/t3knoid/ansible/blob/main/playbooks/minecraft/deploy_bedrock.yml)  
  This is the canonical entry point for provisioning or updating the server.

- **Inventory:**  
  [`inventory/minecraft`](https://github.com/t3knoid/ansible/tree/main/inventory/minecraft)  
  Defines:
  - Host(s) running the Bedrock server  
  - Variables such as `bedrock_setup_version`  
  - Any host‑specific overrides

---

## 🔧 Deployment Workflow

### 1. Set the Bedrock Version

The server version is controlled by:

{% raw %}
```
bedrock_setup_version: 1.21.132.3
```
{% endraw %}

This variable lives in the Minecraft inventory and determines which Bedrock server package is downloaded and installed.

### 2. Run the Deployment Playbook

To deploy or update the server:

{% raw %}
```
ansible-playbook playbooks/minecraft/deploy_bedrock.yml
```
{% endraw %}

The role ensures:

- Correct version is installed  
- Service is restarted only when needed  
- Configuration changes are applied safely  
- Deployment is fully idempotent

---

## 🔍 Checking for New Bedrock Versions

The Bedrock server does **not** provide an API for version discovery.  
To automate this, the homelab uses a Playwright‑based scraper.

### Version Check Playbook

[`check_bedrock_version.yml`](https://github.com/t3knoid/ansible/blob/main/playbooks/bedrock/check_bedrock_version.yml)

This playbook:

1. Launches Playwright in headless mode  
2. Scrapes the official Bedrock server download page  
3. Extracts the latest available version  
4. Prints the version to stdout for easy consumption

### Updating the Inventory Version

When a new version is detected:

1. Update the inventory variable:

   ```
   bedrock_setup_version: <new_version>
   ```

2. Re-run the deployment playbook:

   ```
   ansible-playbook playbooks/minecraft/deploy_bedrock.yml
   ```

This ensures the server is always running the latest official Bedrock release.

---

## 🌐 Official Download Source

The Bedrock server package is always retrieved from:

**Minecraft Bedrock Server Download**  
https://www.minecraft.net/en-us/download/server/bedrock

The `bedrock_setup` role handles downloading and verifying the archive.

---

## ▶️ Service Management

The role installs a systemd service:

{% raw %}
```
systemctl status bedrock
systemctl restart bedrock
systemctl enable bedrock
```
{% endraw %}

The service is restarted automatically when:

- A new version is installed  
- Configuration files change