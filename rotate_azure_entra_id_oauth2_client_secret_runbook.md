---
title: "Rotate Azure Entra ID OAuth2 Client Secret Runbook"
---

# 🔐Rotate Azure Entra ID OAuth2 Client Secret Runbook
**Purpose:**  
When the Azure Entra ID application’s **client secret expires**, operators must re‑run the OAuth2 provisioning workflow. This regenerates a new secret and injects it into the reverse proxy’s OAuth2 configuration via the `entra_id_oauth2` role.

**Related Documentation:**  
See **[Configure An Inventory For Entra ID OAuth2](configure_an_inventory_for_entra_id_oauth2.md)** for inventory prerequisites and variable definitions.

---

## 1. Preconditions  

Before executing the rotation workflow, confirm:

- The target site is already defined under `rproxy_setup_sites` in  
  `inventory/<inventory_name>/group_vars/all/main.yml`.
- The inventory contains the required host groups (`[oauth2_proxy]`, etc.).
- Global Azure service principal values (`global_azure_tenant`, `global_azure_sp_client_id`, `global_azure_sp_secret`) are present in `roles/global/vars/main.yml` or vault.
- The reverse proxy host (commonly `rproxy-0`) is reachable via SSH.

If any of these need updating, refer to the **[Configure An Inventory For Entra ID OAuth2](configure_an_inventory_for_entra_id_oauth2.md)** runbook.

---

## 2. Why This Rotation Is Required  
The OAuth2 client secret stored in Entra ID has a fixed lifetime.  
When it expires:

- OAuth2‑Proxy cannot authenticate users.
- The reverse proxy will redirect to Entra but fail to complete the callback.
- Logs show `invalid_client` or `client_secret mismatch`.

The `entra_id_oauth2` role regenerates a **new client secret** using the Azure CLI and injects it into the site’s `rproxy_setup_sites` entry. The updated secret is then consumed by the `oauth2_proxy_setup` role.

---

## 3. Execute the Secret Rotation Workflow  
Run the following command from your automation control node:

{% raw %}
```bash
INV=inventory/services/inventory.ini
ansible-playbook -k -u ansible -i $INV playbooks/oauth2_proxy/deploy_oauth2_proxy.yml
```
{% endraw %}

This playbook:

- Loads the inventory defined by $INV
- Ensures the OAuth2‑Proxy host is targeted via the [oauth2_proxy] group
- Calls the entra_id_oauth2 role to generate a new Azure client secret
- Passes the newly generated secret into oauth2_proxy_setup
- Updates and restarts OAuth2‑Proxy with the new credentials

Refer to the **[Configure An Inventory For Entra ID OAuth2](configure_an_inventory_for_entra_id_oauth2.md)** runbook for inventory structure and variable definitions.

This process ensures the new secret is fully deployed and active.

---

## 4. Post‑Rotation Validation  
Perform the following checks:

### 🔎 Inventory Validation
{% raw %}
```bash
ansible-inventory -i $INV --graph oauth2_proxy
```
{% endraw %}
Confirm the protected site appears under the `oauth2_proxy` group.

### 🌐 Functional Validation
- Visit the protected site (e.g., `https://<server_name>`).  
- You should be redirected to Microsoft Entra ID.  
- After login, OAuth2‑Proxy should return you to the site’s `oauth2_callback_url`.

### 🧩 Service Validation
On the proxy host:

{% raw %}
```bash
systemctl status oauth2-proxy@<server_name>.service
```
{% endraw %}

Confirm the service is running without errors.

---

## 5. Troubleshooting  

If issues occur after rotation, cross‑check the guidance in the **[Configure An Inventory For Entra ID OAuth2](configure_an_inventory_for_entra_id_oauth2.md)** runbook:

- **404/502 errors:** Ensure `global_oauth2_proxy_ports` contains the exact `server_name`.  
- **Callback mismatch:** Verify the Entra App Registration redirect URI matches `oauth2_callback_url`.  
- **Auth loop:** Check `oauth2_cookie_secret` validity and system clock skew.  
- **Empty client_id/client_secret:** Re‑run the playbook — the secret is injected dynamically.

---

## 6. Summary  
This runbook provides the operational steps to rotate an expired Azure Entra ID OAuth2 client secret using your existing Ansible automation. The `deploy_oauth2_proxy.yml` playbook handles secret regeneration, injection, and service reconfiguration end‑to‑end.