---
title: "Minecraft Server"
---

# 🧱 Minecraft Server

This page documents the deployment, management, and version‑tracking workflows for **Minecraft servers** running in the environment. Both **Bedrock Edition** and **Java Edition** are supported through dedicated Ansible roles, with automated version‑scraping powered by Playwright.

---

## 🟩 **Minecraft Bedrock Edition Server**  
Documentation for the active Bedrock server deployment, including version pinning, Ansible role usage, and automated version checks.

➡️ see: **[Minecraft Bedrock Edition Server](minecraft_bedrock_edition_server.md)**

---

## 🟧 **Minecraft Java Edition Server**  
Documentation for the Java Edition role, versioning model, manual version checks, and deployment workflow.

➡️ see: **[Minecraft Java Edition Server](minecraft_java_edition_server.md)**

---

## 🔍 Version Detection Using Playwright

Minecraft does not provide a public API for server version discovery. To automate version tracking, the homelab uses **Playwright** to scrape the official download pages for both editions.

> ℹ️ **NOTE**
> The **[Playwright role](https://github.com/t3knoid/ansible/tree/main/roles/playwright)** which installs and configures Playwright is included in the version check playbooks.

### 🟩 Bedrock Edition Version Scraping

The Bedrock download page hides the Linux server link behind JavaScript‑rendered elements.  
Playwright is required because:

- The download button is dynamically injected  
- The ZIP filename contains the version number  
- The version can be extracted directly from the URL

Workflow:

1. Playwright loads the Bedrock server download page  
2. Waits for the Linux download button to appear  
3. Extracts the `.zip` URL  
4. Parses the version from the filename  
5. Outputs the version for Ansible to consume

This is used by the **[get_bedrock_version.py](https://github.com/t3knoid/ansible/blob/main/roles/bedrock_setup/files/get_bedrock_version.py)** helper script inside the `bedrock_setup` role.

---

### 🟧 Java Edition Version Scraping

The Java Edition page displays the version number in **page text**, not in the download URL. However, the version text is injected by client‑side JavaScript, so Playwright is still required.

Workflow:

1. Playwright loads the Java server download page  
2. Waits for the version text (`minecraft_server.X.Y.Z.jar`) to appear  
3. Extracts the version using regex  
4. Outputs the version for Ansible

This is used by the **[get_minecraft_version.py](https://github.com/t3knoid/ansible/blob/main/roles/minecraft_setup/files/get_minecraft_version.py)** helper script inside the `minecraft_setup` role.

---

## ⚙️ Configuring the Playwright Environment

Playwright must be installed and configured on the Ansible control node (or wherever the version‑check scripts run).

### 1. Install Python Dependencies

Inside your virtual environment:

{% raw %}
```
pip install playwright
pip install requests
```
{% endraw %}

### 2. Install Playwright Browsers

Playwright requires browser binaries (Firefox is recommended for headless scraping):

{% raw %}
```
playwright install firefox
```
{% endraw %}

This installs:

- Firefox browser engine  
- Required Playwright drivers  
- Supporting libraries  

### 3. Verify Installation

Run:

{% raw %}
```
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```
{% endraw %}

Then test a simple script:

{% raw %}
```
playwright install
```
{% endraw %}

### 4. Running Version‑Check Scripts

Bedrock:

{% raw %}
```
python3 roles/bedrock_setup/files/get_bedrock_version.py
```
{% endraw %}

Java:

{% raw %}
```
python3 roles/minecraft_setup/files/get_minecraft_version.py
```
{% endraw %}

Both scripts output **only the version number**, making them easy to integrate into Ansible workflows.

---

## 🧩 How Version Checks Integrate With Ansible

### Bedrock Edition

- `check_bedrock_version.yml` runs the Playwright script  
- The script prints the latest version  
- You update `bedrock_setup_version` in inventory  
- Deployment playbook installs the correct ZIP

### Java Edition

- The helper script scrapes the version text  
- You update:
  - `minecraft_setup_version` (metadata)
  - `minecraft_setup_download_url` (actual JAR source)
- Deployment playbook installs the new JAR

---