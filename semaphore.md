---
title: "🚦 Semaphore UI"
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

```json
"postgres": {
  "host": "192.168.2.102",
  "name": "semaphoreui",
  "user": "semaphoreui",
  "pass": "*****"
},
"dialect": "postgres"
```

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
Semaphore also supports OAuth2 authentication. In this setup, **Microsoft Entra ID** (formerly Azure AD) acts as the Identity Provider (IdP).  
- Provides single sign‑on (SSO) with Microsoft accounts.  
- Users are redirected to Entra ID for login, and Semaphore grants access based on identity claims.  
- Requires registering Semaphore as an application in Entra ID, configuring redirect URIs, and creating client credentials.

---

## 🖥️ Systemd Service

Semaphore UI runs automatically via a systemd unit file (`/etc/systemd/system/semaphore.service`):

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

> **Note:** The service runs as user `semaphore` and group `ansible`, using a Python virtual environment.

---

## 👤 Service Account

A dedicated Active Directory account must be created to run the Semaphore UI service. Example PowerShell command:

```powershell
New-ADUser -Name "Semaphore" -GivenName "Semaphore" -Surname "User" `
  -SamAccountName "semaphore" -UserPrincipalName "semaphore@refol.us" `
  -AccountPassword (Read-Host -AsSecureString "Input Password") -Enabled $true
```

---

## 🌐 Web Host

Semaphore UI is accessible at: **https://semaphore.refol.us**  
- **Reverse proxy:** Nginx  
- **TLS certificates:** Generated via [Certbot](../certbot/README.md)

---

## 🛠️ Troubleshooting

Semaphore does not maintain its own log file. All output is sent to system messages.  
View logs with:

```shell
sudo journalctl -u semaphore -f
```

---

## 📦 Deployment with Ansible

Semaphore UI can be provisioned and deployed using Ansible playbooks.

### 1. Provision Ubuntu VM
```shell
ansible-playbook -u ansible -k -i inventory/ansible/inventory.ini playbooks/provision_vm.yml -l ansible-1
```

### 2. Deploy Semaphore UI
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/deploy_semaphoreui.yml
```
> Uses the `postgresql_setup` role plus Python/Ansible modules.

### 3. Configure Reverse Proxy
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/rproxy/config_rproxy.yml
```

### 4. Generate Certificates
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/certs/generate_certs.yml
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/certs/stage_certs.yml
```

### 5. Backup Database
```shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/semaphoreui/backup_db.yml
```
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

