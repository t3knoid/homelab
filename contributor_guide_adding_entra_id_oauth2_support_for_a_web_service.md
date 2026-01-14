---
title: "Contributor Guide Adding Entra ID OAuth2 Support for a Web Service"
---

# 🔐 Contributor Guide Adding Entra ID OAuth2 Support for a Web Service

This guide explains how a contributor can add Entra ID OAuth2 authentication to an existing web service that sits behind the repository’s reverse‑proxy setup.

---

## 🧩 Background

The `roles/global/defaults/main/vault.yml` vault file defines the service‑principal credentials used to configure Microsoft Entra ID. This service principal has permissions to create and manage Azure AD applications and generate client secrets:

- `global_azure_tenant`  
- `global_azure_sp_client_id`  
- `global_azure_sp_secret`

The target web service must already have an entry under `rproxy_setup_sites` in `inventory/ansible/group_vars/all/main.yml` for the inventory where the host is defined.

---

## 🛠️ Ansible Requirements

- The `azure.azcollection` collection must be installed  
  (`ansible-galaxy collection install azure.azcollection`).
- The Azure CLI (`azure-cli`) is required for service‑principal login and reliable client‑secret generation. It is installed by the `azure_cli_setup` role.
- Python Azure modules are installed into a dedicated virtual environment using `python3_venv_folder` and `python3_version` to isolate dependencies.

---

## 🔄 High‑Level Flow

- Configure the inventory for the web service host:
  - Define the `[oauth2_rproxy]` group for the reverse‑proxy server.
  - Define Python‑related variables.
  - Update the service’s `rproxy_setup_sites` entry with OAuth2‑specific variables.
- Run the `playbooks/oauth2_proxy/deploy_oauth2_proxy.yml` playbook.

---

## 🧭 Step‑by‑Step Instructions

### 1. Update the Web Service Host Inventory File

#### **① Add the `[oauth2_rproxy]` group**

Define the reverse‑proxy host (e.g., `rproxy-0`).  
The `deploy_oauth2_proxy.yml` playbook runs on this host.

{% raw %}
```ini
[oauth2_rproxy]
rproxy-0
```
{% endraw %}

#### **② Add the `[python]` group**

This group ensures Python is installed on the reverse‑proxy host.

{% raw %}
```ini
[python]
rproxy-0
```
{% endraw %}

#### **③ Update the `rproxy_setup_sites` entry**

Locate the service’s entry in `group_vars/all/main.yml` and ensure it includes the required OAuth2 keys:

{% raw %}
```yaml
rproxy_setup_sites:
  - server_name: code.refol.us

    # OAuth2 integration variables
    use_oauth2: true
    oauth2_provider: "entra-id"
    oauth2_scope: "openid profile email"
    oauth2_cookie_secret: "base64-random-32-bytes"
    oauth2_client_id: ""
    oauth2_callback_url: "https://code.refol.us/oauth2/callback"
    oauth2_client_secret: ""
    oauth2_email_domains: "*"
```
{% endraw %}

**Notes**

- Unless explicitly required, **do not modify**:  
  `oauth2_provider`, `oauth2_scope`, `oauth2_email_domains`
- `use_oauth2: true` enables OAuth2 for the site.
- `oauth2_cookie_secret` can be generated using the following Python snippet, `python -c 'import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'`
- `oauth2_client_id` cannot be set and is generated whenever the application client is created.
- `oauth2_callback_url` must match the redirect URI in the Entra App Registration.
- `oauth2_client_id` and `oauth2_client_secret` are automatically injected when the `entra_id_oauth2` role runs (see [`register_app.yml`](https://github.com/t3knoid/ansible/blob/main/roles/entra_id_oauth2/tasks/register_app.yml)).

---

## ▶️ Running the OAuth2 Deployment Playbook

Execute the playbook:

{% raw %}
```bash
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/oauth2_proxy/deploy_oauth2_proxy.yml
```
{% endraw %}

This playbook:

- Loads the `global` role (Azure service‑principal secrets)
- Loads the `entra_id_oauth2` role (generates and injects the app id and client secret)
- Loads the `redis_setup` role (Redis stores large Azure session data)  
  Reference: https://oauth2-proxy.github.io/oauth2-proxy/7.3.x/configuration/oauth_provider/
- Loads the `oauth2_proxy_setup` role (configures OAuth2 Proxy and service)

---

## 🔑 Notes on Secret Creation and Azure Modules

- Client secrets are generated using the `az` CLI because `azure_rm_adapplication` was found unreliable for this purpose.
- Example service‑principal login:

{% raw %}
```
az login --service-principal \
  --username <client_id> \
  --password <client_secret> \
  --tenant <tenant_id>
```
{% endraw %}

- Azure authentication tokens are stored under `~/.azure` during runs.
- The `entra_id_oauth2` role generates the client secret and passes it to `oauth2_proxy_setup` via the `entra_id_oauth2_updated_sites` variable.
- The client ID and secret are embedded into the web host’s OAuth2 config file during `oauth2_proxy_setup`.
- A **new** client secret is generated each time `deploy_oauth2_proxy.yml` is executed.

---

## 📝 Processing Notes

- Only entries in `rproxy_setup_sites` with `use_oauth2: true` are processed.
- Entries in `rproxy_setup_sites` with `use_oauth2: false` or not defined are skipped. OAuth2 configuration and service for these sites are removed.
- The role filters the list and creates/updates Azure applications only for those sites.