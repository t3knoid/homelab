---
title: "Entra ID OAuth2 Provisioning Ansible Role"
---

# 🔐 **Entra ID OAuth2 Provisioning Ansible Role**

This role automates the creation and management of Microsoft Entra ID (Azure AD) OAuth2 application credentials for sites protected by SSO in the reverse‑proxy environment.

It discovers which sites require OAuth2, provisions or updates the necessary identity resources in Entra ID, generates client secrets, and injects those secrets back into the site definitions so that the [`oauth2_proxy_setup`](https://github.com/t3knoid/ansible/blob/main/roles/oauth2_proxy_setup/README.md) downstream role can complete OAuth2 Proxy and Nginx SSO configuration.

This role acts as the **identity provisioning layer** in the SSO pipeline.

---

## 🎯 **Role Purpose and Responsibilities**

This role manages all Azure‑side identity operations required for OAuth2‑enabled sites, including:

* Identifying which reverse‑proxy sites use OAuth2  
* Creating or validating the Entra ID application for each site  
* Generating client secrets with a controlled expiry  
* Logging into Azure using a service principal  
* Returning a complete site definition list that includes generated secrets  
* Preparing the data needed by the `oauth2_proxy_setup` role to finalize SSO configuration  

It abstracts away the complexities of Azure application registration and ensures consistent, repeatable identity provisioning.

---

## 🧭 **High‑Level Workflow**

Below is the end‑to‑end flow of the role, from site discovery to generating usable OAuth2 credentials for downstream roles.

{% raw %}
```
                     +--------------------------------+
                     |  rproxy_setup_sites (input)    |
                     |  list of reverse-proxy sites   |
                     +-----------------+--------------+
                                       |
                                       v
                    +------------------+------------------+
                    | Filter sites requiring OAuth2       |
                    | use_oauth2: true                    |
                    +------------------+------------------+
                                       |
                                       v
                 +---------------------+----------------------+
                 | Create/validate Entra ID app for each site |
                 |   - Uses azure.azcollection                |
                 +---------------------+----------------------+
                                       |
                                       v
                 +---------------------+----------------------+
                 | Login to Azure using service principal     |
                 |   - Stores token under ~/.azure            |
                 +---------------------+----------------------+
                                       |
                                       v
                 +---------------------+----------------------+
                 | Generate client secrets for each site      |
                 |   - Uses Azure CLI                         |
                 +---------------------+----------------------+
                                       |
                                       v
         +------------------------------+-------------------------------+
         | Append generated secrets into site definitions               |
         | Produces: entra_id_oauth2_updated_sites                      |
         +------------------------------+-------------------------------+
                                       |
                                       v
           +---------------------------+-----------------------------+
           | Downstream role: oauth2_proxy_setup                      |
           | Uses updated site list to configure OAuth2 Proxy + Nginx |
           +---------------------------------------------------------+
```
{% endraw %}

---

## 🧩 **Required Variables (Per‑Site)**

Each site that needs OAuth2 must define the following fields inside the master variable:  
**`rproxy_setup_sites`**

These values describe how the site integrates with Entra ID via OAuth2 Proxy.

### 📘 **Example Entry**

{% raw %}
```yaml
rproxy_setup_sites:
  - server_name: code.refol.us
    port: 8000
    proxy_pass: "http://{{ global_ip_addresses[groups['code_server'][0]] }}"
    allow_list:
      - 192.168.0.0/24
      - 192.168.2.0/24
      - 24.105.250.200
      - 70.107.117.124
    restricted: false
    enable: true

    # OAuth2 integration
    use_oauth2: true
    oauth2_provider: "entra-id"
    oauth2_scope: "openid profile email"
    oauth2_cookie_secret: "base64-random-32-bytes"
    oauth2_client_id: "uuid-for-site"
    oauth2_callback_url: "https://code.refol.us/oauth2/callback"
    oauth2_client_secret: ""
    oauth2_email_domains: "*"
```
{% endraw %}

### 📋 **Required Values**

| Field                  | Purpose                                                    |
| ---------------------- | ---------------------------------------------------------- |
| `use_oauth2`           | Marks the site as requiring OAuth2 SSO                     |
| `oauth2_client_id`     | Pre‑created application ID (e.g., via `uuidgen`)           |
| `oauth2_callback_url`  | Must match Entra ID’s redirect URI                         |
| `oauth2_scope`         | Requested scopes                                           |
| `oauth2_email_domains` | Allowed login domains                                      |
| `oauth2_cookie_secret` | Base64‑encoded 32‑byte random string                       |
| `oauth2_client_secret` | **Left blank** → filled in by this role                    |

Only sites with `use_oauth2: true` are processed.

---

## 🧱 **Prerequisites**

This role interacts directly with Azure and therefore requires the following components.

### 🔑 **Azure Service Principal**

A dedicated service principal with permissions to:

* Create and manage Azure AD applications  
* Generate client secrets  

👉 See the **[Service Principal](service_principal.md)** page for details.

---

### 🌍 **Global Role Variables**

Defined in the global role vault:

{% raw %}
```yaml
global_azure_sp_client_id: "<service_principal_client_id>"
global_azure_sp_secret: "<service_principal_secret>"
global_azure_tenant: "<tenant_id>"
```
{% endraw %}

---

### 📦 **Azure Ansible Collection**

Used to create or update Entra ID applications:

{% raw %}
```bash
ansible-galaxy collection install azure.azcollection
```
{% endraw %}

The role installs Python dependencies into the virtual environment automatically.

---

### 🖥️ **Azure CLI (`azure-cli`)**

Used for:

* Service principal login  
* Secret generation  

Installed via the `azure_cli_setup` role.

{% raw %}
```bash
az login --service-principal \
  --username <client_id> \
  --password <client_secret> \
  --tenant <tenant_id>
```
{% endraw %}

> **Note:**  
> `azure_rm_adapplication` was tested but did not reliably generate secrets.  
> The `az` CLI is used instead.

---

### 🐍 **Python 3 Virtual Environment**

Azure modules are installed into a dedicated venv defined by:

{% raw %}
```
python3_venv_folder
python3_version
```
{% endraw %}

This ensures dependency isolation.

---

## 📤 **Output of the Role**

### 🔄 **`entra_id_oauth2_updated_sites`**

This is the **final updated version of `rproxy_setup_sites`**, containing newly generated client secrets for each OAuth2‑enabled site.

Each entry includes:

* Client ID  
* Client secret  
* Scopes  
* Cookie secret  
* Callback URL  

This list is the **primary output** of the role.

---

## 🔗 **Downstream Integration (OAuth2 Proxy Setup)**

The output variable `entra_id_oauth2_updated_sites` is consumed by the  
**`oauth2_proxy_setup` role**, which uses it to:

* Render OAuth2 Proxy configuration  
* Insert client secrets and provider settings  
* Configure Nginx integration  
* Finalize the SSO flow  

➡️ **This role provisions identity; the next role activates it.**  
Together, they form a fully automated, consistent, and secure OAuth2 SSO deployment pipeline across the homelab reverse‑proxy cluster.