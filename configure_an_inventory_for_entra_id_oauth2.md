---
title: "Configure An Inventory For Entra ID OAuth2"
---

# Configure An Inventory For Entra ID OAuth2

This runbook explains how to update an inventory so a site behind rproxy uses oauth2-proxy with Microsoft Entra ID.

## Scope

This runbook covers required updates in:

- inventory/<inventory_name>/group_vars/all/main.yml
- roles/global/vars/main.yml

It also includes the required host group update in inventory/<inventory_name>/inventory.ini.

## Prerequisites

- The site is already defined in rproxy_setup_sites.
- A reverse proxy host exists in the inventory (commonly rproxy-0 in rproxy_main).
- Azure service principal and tenant values used by Entra playbooks are already configured in global vars/vault.

## 1) Update Inventory Host Groups

Edit inventory/<inventory_name>/inventory.ini and add the oauth2_proxy group that defines where oauth2-proxy is installed. This entry is required.

Example:

{% raw %}
```ini
[oauth2_proxy]
rproxy-0
```
{% endraw %}

## 2) Update The Inventory Main Vars File

Edit inventory/<inventory_name>/group_vars/all/main.yml in rproxy_setup_sites for the domain you want to protect.

Required fields:

{% raw %}
```yaml
rproxy_setup_sites:
  - server_name: prometheus.refol.us
    port: 9090
    proxy_pass: "http://{{ global_ip_addresses['prometheus-0'] }}"
    allow_list:
      - 192.168.0.0/24
      - 192.168.2.0/24
    restricted: false
    use_oauth2: true
    oauth2_provider: "entra-id"
    oauth2_scope: "openid profile email"
    oauth2_cookie_secret: ""
    oauth2_client_id: ""
    oauth2_callback_url: "https://prometheus.refol.us/oauth2/callback"
    oauth2_client_secret: ""
    oauth2_email_domains: "*"
```
{% endraw %}

Notes:

- redirect_url in oauth2-proxy is populated from oauth2_callback_url.
- For apps that need an application redirect URL different from callback, add app_redirect_url.
- oauth2_cookie_secret can be generated with:

{% raw %}
```bash
python -c 'import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'
```
{% endraw %}

- oauth2_client_id and oauth2_client_secret are automatically injected when the entra_id_oauth2 role runs.

## 3) Update Global OAuth2 Port Maps

Edit roles/global/vars/main.yml and add the domain to both maps:

- global_oauth2_proxy_ports
- global_oauth2_proxy_metrics_ports

Example:

{% raw %}
```yaml
global_oauth2_proxy_ports:
  prometheus.refol.us: 4187

global_oauth2_proxy_metrics_ports:
  prometheus.refol.us: 9107
```
{% endraw %}

Rules:

- Keys must match server_name exactly.
- Ports must be unique across all entries in each map.
- Keep proxy and metrics ports aligned with local conventions.

## 4) Deploy Changes

Run the reverse proxy and oauth2-proxy playbooks with the target inventory:

{% raw %}
```bash
ansible-playbook -i inventory/<inventory_name>/inventory.ini playbooks/rproxy/deploy_rproxy.yml
ansible-playbook -i inventory/<inventory_name>/inventory.ini playbooks/oauth2_proxy/deploy_oauth2_proxy.yml
```
{% endraw %}

## 5) Validate

Inventory and group checks:

{% raw %}
```bash
ansible-inventory -i inventory/<inventory_name>/inventory.ini --graph oauth2_proxy
```
{% endraw %}

Behavior checks:

- Accessing https://<server_name> redirects to Entra login.
- After login, oauth2-proxy returns to oauth2_callback_url.
- nginx auth_request locations are present for the protected site.
- oauth2-proxy service is running on the oauth2_proxy host for that domain.

## Troubleshooting

- 404/502 after enabling oauth2: verify global_oauth2_proxy_ports entry exists for the exact server_name.
- OAuth callback mismatch: verify oauth2_callback_url matches Entra app redirect URI exactly.
- Authentication loop: check oauth2_cookie_secret is valid and consistent, and clock skew is minimal.
- Empty client_id/client_secret: run the Entra registration playbook or populate values from vault.
