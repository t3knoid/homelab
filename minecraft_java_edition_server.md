---
title: "Minecraft Java Edition Server"
---

# 🟧 Minecraft Java Edition Server

This page documents the **Minecraft Java Edition** server role available in the homelab’s Ansible ecosystem.  
Although the Java server is **not currently deployed**, the role and playbook are fully prepared for future use.

---

## 📦 Overview

| Component | Description |
|----------|-------------|
| **Edition** | Minecraft **Java Edition** Server |
| **Deployment Method** | Ansible (`minecraft_setup` role) |
| **Playbook** | `playbooks/minecraft/deploy_minecraft.yml` |
| **Inventory** | `inventory/minecraft/` |
| **Version Pin** | Metadata only (`minecraft_setup_version`) |
| **Actual Version Source** | `minecraft_setup_download_url` |
| **Runtime Requirement** | Java (OpenJDK recommended) |
| **Status** | Role exists, but **not in active use** |

---

## 🧩 Architecture

The Java Edition server is deployed as a standalone Linux host managed through Ansible.  The playbook handles installation of Java, deployment of the server JAR, and service management.

### Key Components

- **Ansible Role**  
  [`roles/minecraft_setup`](https://github.com/t3knoid/ansible/tree/main/roles/minecraft_setup)  
  Responsibilities include:
  - Installing Java (OpenJDK)
  - Downloading the server JAR from a provided URL
  - Managing EULA acceptance
  - Creating the server directory structure
  - Generating configuration files
  - Installing a systemd service

- **Deployment Playbook**  
  [`deploy_minecraft.yml`](https://github.com/t3knoid/ansible/blob/main/playbooks/minecraft/deploy_minecraft.yml)  
  Entry point for provisioning or updating a Java Edition server.

- **Inventory**  
  [`inventory/minecraft`](https://github.com/t3knoid/ansible/tree/main/inventory/minecraft)  
  Defines:
  - Host(s) intended for Java Edition deployment  
  - Variables such as Java heap settings, port, version metadata  
  - The authoritative JAR download URL

---

## 🔧 Deployment Workflow

### 1. Configure Java Server Variables

Example inventory variables:

{% raw %}
```
minecraft_setup_version: 1.21.4
minecraft_setup_port: 25565
minecraft_setup_download_url: https://piston-data.mojang.com/v1/objects/4707d00eb834b446575d89a61a11b5d548d8c001/server.jar
minecraft_setup_java_xmx: 2048
minecraft_setup_java_xms: 256
```
{% endraw %}

> [!Important]
> `minecraft_setup_version` is **metadata only**.  
> The **actual server version** is determined by the `minecraft_setup_download_url`.

### 2. Deploy or Update the Server

{% raw %}
```
ansible-playbook playbooks/minecraft/deploy_minecraft.yml
```
{% endraw %}

The playbook ensures:

- Java is installed  
- The correct server JAR is downloaded  
- EULA is accepted (if configured)  
- Systemd service is created or updated  
- Configuration changes are applied safely  

---

## 🔍 Checking for New Minecraft Java Edition Versions

The Minecraft server does **not** provide an API for version discovery.  
To automate this, the homelab uses a Playwright‑based scraper.

### Version Check Playbook

[`check_minecraft_version.yml`](https://github.com/t3knoid/ansible/blob/main/playbooks/minecraft/check_minecraft_version.yml)

This playbook:

1. Launches Playwright in headless mode  
2. Scrapes the official Bedrock server download page  
3. Extracts the latest available version  
4. Prints the version to stdout for easy consumption

### Updating the Inventory Version

When a new version is detected:

1. Update the inventory variable:

   ```
   minecraft_setup_version: <new_version>
   ```

2. Re-run the deployment playbook:

   ```
   ansible-playbook playbooks/minecraft/deploy_minecraft.yml
   ```

This ensures the server is always running the latest official Minecraft Java Edition release.

---

## ▶️ Service Management

The role installs a systemd service:

{% raw %}
```
systemctl status minecraft
systemctl restart minecraft
systemctl enable minecraft
```
{% endraw %}

The service is restarted automatically when:

- The server JAR changes  
- Configuration files are updated  

---

## 🟧 Why This Role Is Not Currently Used

The homelab’s active Minecraft deployment uses **Bedrock Edition**, because:

- The player base uses Bedrock clients (console/mobile/Windows)  
- Bedrock is lighter and easier to maintain  
- Java Edition requires JVM tuning and more memory  

The Java role remains available for future use.
