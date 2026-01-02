---
title: "Semaphore UI"
---

# 🚦 Semaphore UI

[Semaphore UI](https://semaphoreui.com/install/) is a lightweight web interface for managing and executing Ansible playbooks. It provides a user‑friendly dashboard to organize inventories, credentials, and playbook runs—ideal for homelab automation and infrastructure orchestration.

---

## 📥 Installation

Semaphore UI is installed on an Ubuntu virtual machine using [Ubuntu’s package manager](https://docs.semaphoreui.com/administration-guide/installation/package-manager/).  
During installation:

- A default **admin** user is created.  
- The initial admin password is written to a file in the configuration folder.  
- The Semaphore UI systemd service is configured to run under an [Active Directory service account](#service-account), which must be created manually.

---

## ⚙️ Configuration

- **Config folder:** `/ansible/semaphore`  
- **Config file:** `/ansible/semaphore/etc/config.json`  

### Python
Semaphore UI runs inside a Python virtual environment.

### Database
PostgreSQL is used as the backend database. It runs on the same host as the Semaphore service.  
Data folder: `/ansible/pgdata`

Example configuration:

{% raw %}
```json
"postgres": {
  "host": "192.168.2.102",
  "name": "semaphoreui",
  "user": "semaphoreui",
  "pass": "*****"
},
"dialect": "postgres"
```
{% endraw %}

---

## 🔐 Logging In & Authentication

Semaphore supports multiple authentication methods to control access:

### Local Admin
- Default **admin** account created during installation.  
- Password stored in `/ansible/semaphore/.admin`.  
- Recommended only for initial setup or emergency access.

### LDAP (Active Directory)
Semaphore can integrate with LDAP/Active Directory for user authentication. This allows domain users to log in with their existing credentials.

Example configuration highlights:
- **Bind DN:** Service account used to query AD.  
- **Search DN:** Base DN for user lookups.  
- **Search filter:** Matches `sAMAccountName` to the login username.  
- **Mappings:** Maps AD attributes to Semaphore fields (e.g., `mail → userPrincipalName`).

### OAuth2 (Entra ID)
Semaphore also supports OAuth2 authentication. In this setup, **[Microsoft Entra ID](microsoft_entra_id.md)** (formerly Azure AD) acts as the Identity Provider (IdP).  
- Provides single sign‑on (SSO) with Microsoft accounts.  
- Users are redirected to Entra ID for login, and Semaphore grants access based on identity claims.  
- Requires registering Semaphore as an application in Entra ID, configuring redirect URIs, and creating client credentials.

---

## 🖥️ Systemd Service

Semaphore UI runs automatically via a systemd unit file (`/etc/systemd/system/semaphore.service`):

{% raw %}
```ini
[Unit]
Description=Semaphore Ansible
Documentation=https://docs.semaphoreui.com
Wants=network-online.target
After=network-online.target
ConditionPathExists=/usr/bin/semaphore
ConditionPathExists=/ansible/semaphore/etc/config.json

[Service]
User=semaphore
Group=ansible
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/bin/bash -c 'source /opt/python_3.12/bin/activate && /usr/bin/semaphore server --config=/ansible/semaphore/etc/config.json'
SyslogIdentifier=semaphore
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```
{% endraw %}

> **Note:** The service runs as user `semaphore` and group `ansible`, using a Python virtual environment.

---

## 👤 Service Account

A dedicated Active Directory account must be created to run the Semaphore UI service. Example PowerShell command:

{% raw %}
```powershell
New-ADUser -Name "Semaphore" -GivenName "Semaphore" -Surname "User" `
  -SamAccountName "semaphore" -UserPrincipalName "semaphore@refol.us" `
  -AccountPassword (Read-Host -AsSecureString "Input Password") -Enabled $true
```
{% endraw %}

---

## 🌐 Web Host

Semaphore UI is accessible at: **https://semaphore.refol.us**  
- **Reverse proxy:** Nginx  
- **TLS [Certificates](certificates.md)** generated via [Certbot](certbot.md)

---

## 🛠️ Troubleshooting

Semaphore does not maintain its own log file. All output is sent to system messages.  
View logs with:

{% raw %}
```shell
sudo journalctl -u semaphore -f
```
{% endraw %}

---

## 📦 Deployment with Ansible

Semaphore UI can be provisioned and deployed using Ansible playbooks.

### 1. Provision Ubuntu VM
{% raw %}
```shell
ansible-playbook -u ansible -k -i inventory/ansible/inventory.ini playbooks/provision_vm.yml -l ansible-1
```
{% endraw %}

### 2. Deploy Semaphore UI
{% raw %}
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/deploy_semaphoreui.yml
```
{% endraw %}
> Uses the `postgresql_setup` role plus Python/Ansible modules.

### 3. Configure Reverse Proxy
{% raw %}
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/rproxy/config_rproxy.yml
```
{% endraw %}

### 4. Generate Certificates
{% raw %}
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/certs/generate_certs.yml
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/certs/stage_certs.yml
```
{% endraw %}

### 5. Backup Database
{% raw %}
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/semaphoreui/backup_db.yml
```
{% endraw %}
> Uses `pg_dump` to `/nfs/backups/` with filenames prefixed `semaphoreui_YYYY-MM-DD`.

---

## 🚀 Using Semaphore

After deployment:

- Login as **admin** at [https://semaphore.refol.us](https://semaphore.refol.us).  
- The generated password is stored in `/ansible/semaphore/.admin`.  
- Create a project to begin.

### Minimum Setup
- **Repository:** Add `https://github.com/t3knoid/ansible.git` (main branch, no access key).  
- **Key Store:** Create two *Login with password* keys:
  - Vault password  
  - Semaphore user credentials  

### Task Templates & Inventory
- **Inventory:**  
  - Name  
  - User Credentials → Semaphore user credentials  
  - Type → File (e.g. `inventory/ansible/inventory.ini`)  
  - Sudo Credentials → none  
  - Repository → leave empty  

- **Task Template:**  
  - Name  
  - Playbook path (e.g. `playbooks/linux/check_connection.yml`)  
  - Inventory → select created inventory  
  - Repository → configured Ansible repo  
  - Variable Group → Empty  
  - CLI args → `-k`  
  - Vaults → vault password from key store

---

Here’s an updated version of your wiki section that cleanly incorporates the new **GitHub Action trigger workflow**, while preserving the tone, structure, and formatting of your existing documentation.

---

## 📘 Set Up using Ansible

For detailed instructions on **configuring Semaphore projects, templates, dynamic templates, views, keystores, and schedules using Ansible**,

👉 See: **[Configure Semaphore UI Projects Runbook](configure_semaphore_ui_projects_runbook.md)**

> This runbook provides step-by-step examples, YAML snippets, and guidance for safely managing your Semaphore UI configuration in a fully declarative way.

### ⚡ Automatic Configuration via GitHub Actions

Semaphore UI configuration is applied **automatically** whenever files under:

{% raw %}
```
inventory/semaphore/group_vars/semaphore/
```
{% endraw %}

are modified.

A dedicated GitHub Action detects these changes and triggers the **Setup Semaphore** task inside the **Home Lab** project in Semaphore UI.

This ensures that any update to your declarative inventory immediately results in a fresh configuration run—no manual playbook execution required.

👉 See: **[Trigger Semaphore Setup Workflow](trigger_semaphore_setup_workflow.md)** for a full breakdown of how the automation works.

### Quick Preview: Manual Execution (Optional)

If you prefer to run the configuration locally—or need to test changes before pushing—you can still execute the playbook manually:

{% raw %}
```bash
ansible-playbook -k -i inventory/semaphore/inventory.ini setup-semaphore.yml
```
{% endraw %}

> Notes:
>
> * `-k` prompts for SSH password; if using SSH keys, it is not needed.
> * Idempotent: safe to run multiple times without duplicating templates or schedules.
> * This playbook **does not install Semaphore UI**; it only configures projects, views, templates, credentials, and schedules using the `semaphoreui_setup` role.  
>   See the [Semaphore UI Setup - Role Overview](semaphore_ui_setup_-_role_overview.md) for a detailed analysis of the setup portion in this role.
