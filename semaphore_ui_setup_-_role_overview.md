---
title: "️ Semaphore UI Setup – Role Overview"
---

# 🛠️ Semaphore UI Setup – Role Overview

The semaphoreui_setup role installs and configures Semaphore UI with optional Entra ID OIDC integration.

Primary role metadata:
- [roles/semaphoreui_setup/meta/main.yml](roles/semaphoreui_setup/meta/main.yml)

Main responsibilities:
- Install Semaphore UI binaries and prerequisites
- Render Semaphore runtime config
- Create and persist admin credentials
- Start and enable Semaphore service
- Configure Semaphore objects over API (projects, repos, templates, schedules, etc.)

---

# 💻 Supported Hosts

Primary host group: semaphore

Deployment mode:
- become: true
- gather_facts: true

Main deploy playbook:
- [playbooks/semaphoreui/deploy_semaphoreui.yml](playbooks/semaphoreui/deploy_semaphoreui.yml)

Deployment role chain:
1. global
2. sshpass
3. autofs
4. azure_cli_setup
5. entra_id_oauth2
6. semaphoreui_setup

---

# 🔐 Entra ID / OIDC Integration

Entra app registration and secret generation run before semaphoreui_setup.

Entra registration logic:
- [roles/entra_id_oauth2/tasks/register_app.yml](roles/entra_id_oauth2/tasks/register_app.yml)

Registration process:
1. Resolve redirect URI from site config by priority:
   - app_redirect_url
   - oauth2_callback_url (legacy)
2. Create app if missing
3. Update redirect URIs for existing apps
4. Rotate app secret
5. Inject oauth2_client_id and oauth2_client_secret into rproxy_setup_sites

---

# 📂 Inventory Structure (Semaphore)

Semaphore inventory config:
- [inventory/semaphore/group_vars/all/main.yml](inventory/semaphore/group_vars/all/main.yml)

Site block contains:
- rproxy_setup_sites entry for semaphore.refol.us
- app_redirect_url for Semaphore OIDC callback
- oauth2_callback_url (optional, legacy fallback)

---

# ⚙️ Role Execution Structure

Role entrypoint:
- [roles/semaphoreui_setup/tasks/main.yml](roles/semaphoreui_setup/tasks/main.yml)

Execution flow:
1. install.yml
2. configure.yml
3. runner.yml (when remote runner enabled)

Config rendering:
- [roles/semaphoreui_setup/tasks/configure.yml](roles/semaphoreui_setup/tasks/configure.yml)
- [roles/semaphoreui_setup/templates/config.json.j2](roles/semaphoreui_setup/templates/config.json.j2)

OIDC values sourced from:
- [roles/semaphoreui_setup/defaults/main/main.yml](roles/semaphoreui_setup/defaults/main/main.yml)
- semaphoreui_setup_oidc_redirect_url derives from semaphoreui_setup_oidc_site.app_redirect_url

---

# 📌 Setup API Mode (Project/Template/Schedule Management)

API setup entrypoint:
- [roles/semaphoreui_setup/tasks/setup/main.yml](roles/semaphoreui_setup/tasks/setup/main.yml)

Handles:
- API token creation
- User enumeration
- Dynamic inventory discovery
- Project consolidation
- Setup of views, keystores, repositories, inventories, templates, schedules

Setup tasks:
- [roles/semaphoreui_setup/tasks/setup](roles/semaphoreui_setup/tasks/setup.md)

---

# 🔄 Auth/Data Flow

1. Inventory provides semaphore site entry with app_redirect_url
2. entra_id_oauth2 registers or updates Entra app redirect URI
3. entra_id_oauth2 rotates secret and injects oauth2_client_id/oauth2_client_secret into rproxy_setup_sites
4. semaphoreui_setup reads injected values and renders config.json OIDC provider settings
5. Semaphore sign-in uses configured redirect URI

---

# ✅ Operator Notes

- Native Semaphore OIDC redirect URI: https://semaphore.refol.us/api/auth/oidc/azure/redirect
- app_redirect_url takes priority in redirect URI resolution
- oauth2_callback_url available for legacy compatibility
- Redirect URIs are synchronized with Entra app registration for existing apps