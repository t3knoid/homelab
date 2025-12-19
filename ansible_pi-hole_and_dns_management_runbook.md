---
title: "Ansible Pi-hole and DNS Management Runbook"
---

# 🧑‍🔧 Ansible Pi-hole and DNS Management Runbook

This runbook documents all **Ansible playbooks** used to manage Pi-hole and DNS in the homelab. It provides a quick reference for **purpose, target inventory groups, and special notes**. All Pi-hole API–based operations require the `pihole_password` secret stored in **Ansible Vault**.

---

## 📁 Playbooks Overview

| Purpose                                    | Playbook                                         |  Target Inventory Group | Notes                                                                                                                   |
| ------------------------------------------ | ------------------------------------------------ | ----------------------: | ----------------------------------------------------------------------------------------------------------------------- |
| Install Pi-hole (unattended)               | [deploy_pihole.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/deploy_pihole.yml)           |                     dns | Uses `roles: [global, pihole]`. Requires review before running installer; ensure `pihole_password` available via vault. |
| Add/update local host entries in Pi-hole   | [add_dns_entry.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/add_dns_entry.yml)           | vms, synology, pvenodes | Invokes `pihole` task `add_to_local_dns.yml`; API calls delegated to control node.                                      |
| Remove host entries from Pi-hole           | [delete_dns_entry.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/delete_dns_entry.yml)     | vms, synology, pvenodes | Invokes `pihole` task `delete_from_local_dns.yml`.                                                                      |
| Add one or more CNAME records              | [add_cname_entry.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/add_cname_entry.yml)       |                   cname | Requires `pihole_cname_entries` to be defined; invokes `add_cname_record.yml`.                                          |
| Delete CNAME records                       | [delete_cname_entry.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/delete_cname_entry.yml) |                   cname | Requires `pihole_cname_entries`; invokes `delete_cname_record.yml`.                                                     |
| Display current CNAME records              | [show_cname_records.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/show_cname_records.yml) |             primary_dns | Invokes `get_cname_records.yml` (fetches via Pi-hole API).                                                              |
| Display host entries configured in Pi-hole | [show_hosts.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/show_hosts.yml)                 |             primary_dns | Invokes `get_hosts.yml`.                                                                                                |
| Retrieve Pi-hole configuration             | [show_config.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/show_config.yml)               |             primary_dns | Invokes `get_config.yml`; authenticates with `pihole_password` and deletes session.                                     |
| Trigger Pi-hole DNS restart via API        | [restart_dns.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/restart_dns.yml)               |                     dns | Invokes `restartdns.yml`; API call delegated to control node.                                                           |
| Update Pi-hole software (`pihole -up`)     | [update_pihole_dns.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/update_pihole_dns.yml)   |                     dns | Invokes `update_pihole.yml`; runs `pihole -up` with `become: true`.                                                     |
| Deploy Nebula Sync on primary DNS host     | [deploy_nebulasync.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/deploy_nebulasync.yml)   |             primary_dns | Uses `nebulasync_setup` role (not part of `pihole`); included because it targets DNS hosts.                             |

---

## ⚠️ Common Notes

* **Secrets** – Any playbook that interacts with the Pi-hole API requires the `pihole_password` stored in **Ansible Vault**.
* **CNAME Operations** – The `pihole_cname_entries` variable must be defined as a list of `{domain, target}` dictionaries.
* **Global Variables** – Many tasks rely on global variables such as `global_domain_name` and `global_ip_addresses`, which are supplied by the `roles/global` role or inventory.
* **Delegation** – API calls are delegated to the **control node** to avoid direct API calls from Pi-hole hosts.
* **Ansible Source of Truth** – Never manually update Pi-hole hosts; always run the appropriate playbook to ensure configuration consistency.

---

## 🛠️ Typical Usage Patterns

### 1️⃣ Deploy New Pi-hole Node

1. Add host to `dns` inventory group.
2. Run `deploy_pihole.yml` to install Pi-hole.
3. If deploying HA, run `deploy_nebulasync.yml` to configure Nebula Sync.

### 2️⃣ Add or Update DNS Entries

{% raw %}
```bash
ansible-playbook playbooks/dns/add_dns_entry.yml -i inventory/hosts.yml
```
{% endraw %}

### 3️⃣ Remove DNS Entries

{% raw %}
```bash
ansible-playbook playbooks/dns/delete_dns_entry.yml -i inventory/hosts.yml
```
{% endraw %}

### 4️⃣ Manage CNAME Records

{% raw %}
```bash
ansible-playbook playbooks/dns/add_cname_entry.yml -i inventory/hosts.yml
ansible-playbook playbooks/dns/delete_cname_entry.yml -i inventory/hosts.yml
```
{% endraw %}

### 5️⃣ Retrieve Pi-hole Configuration or Logs

{% raw %}
```bash
ansible-playbook playbooks/dns/show_config.yml -i inventory/dns/inventory.ini
ansible-playbook playbooks/dns/show_hosts.yml -i inventory/dns/inventory.ini
ansible-playbook playbooks/dns/show_cname_records.yml -i inventory/dns/inventory.ini
```
{% endraw %}

### 6️⃣ Restart or Update Pi-hole DNS

{% raw %}
```bash
ansible-playbook playbooks/dns/restart_dns.yml -i inventory/dns/inventory.ini
ansible-playbook playbooks/dns/update_pihole_dns.yml -i inventory/dns/inventory.ini
```
{% endraw %}

---

## 📌 Runbook Best Practices

* **Always check variables** in inventory/group_vars/host_vars before running a playbook.
* **Validate credentials** (`pihole_password`) in Ansible Vault.
* **Use tags** for partial runs when supported.
* **Monitor Nebula Sync** after any configuration changes to ensure all nodes remain consistent.

---
