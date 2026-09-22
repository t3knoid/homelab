---
title: "Deploying PVE Exporter to Proxmox Nodes"
---

# 📈 Deploying PVE Exporter to Proxmox Nodes

## 📖 Purpose

This runbook explains how to:

1. add Proxmox nodes to PVE exporter monitoring
2. configure the Proxmox API credentials required by the exporter
3. deploy PVE exporter to the Proxmox nodes
4. refresh the Prometheus scrape configuration

In this repository, PVE exporter targets come from the `pve_exporter` inventory group. Prometheus does not maintain a separate manual list of PVE exporter targets.

---

## 🧭 How PVE Exporter Targeting Works Here

The PVE exporter is deployed to the `pvenodes` group by:

{% raw %}
```text
playbooks/proxmox/deploy_pve_monitoring.yml
```
{% endraw %}

Prometheus scraping is driven separately by the `pve_exporter` group. The PVE inventory uses a group-of-groups pattern:

{% raw %}
```ini
[pvenodes]
pve-0
pve-1
pve-2

[pve_exporter:children]
pvenodes
```
{% endraw %}

Each exporter runs on its Proxmox node and queries that node's local API. Prometheus scrapes the exporter's `/pve` endpoint with `target=localhost` and the `local` module.

---

## 🛠 Add a Proxmox Node to PVE Exporter Monitoring

### 1. Open the PVE inventory

{% raw %}
```text
inventory/pve/inventory.ini
```
{% endraw %}

### 2. Add the node to the Proxmox node group

Add the host to `pvenodes`:

{% raw %}
```ini
[pvenodes]
pve-0
pve-1
pve-2
```
{% endraw %}

Because `pve_exporter` includes `pvenodes` as a child group, every host in `pvenodes` becomes a PVE exporter target.

Guidelines:

* Keep Proxmox hosts in `pvenodes`.
* Keep the existing `[pve_exporter:children]` pattern.
* Do not also add the same hosts directly to `pve_exporter`.
* Ensure each host has a matching entry in `global_ip_addresses` in `roles/global/vars/main.yml`.

### 3. Configure the exporter port and API user

Open:

{% raw %}
```text
inventory/pve/group_vars/all.yml
```
{% endraw %}

Ensure it defines:

{% raw %}
```yaml
pve_exporter_setup_port: 9221
pve_exporter_setup_api_user: "prometheus@pve"
```
{% endraw %}

The role defaults use the API token name `monitoring`. The resulting Proxmox token identifier is:

{% raw %}
```text
prometheus@pve!monitoring
```
{% endraw %}

### 4. Supply the API token securely

Set `pve_exporter_setup_api_token_value` through Ansible Vault or the repository's secure runtime variable flow:

{% raw %}
```yaml
pve_exporter_setup_api_token_value: <Proxmox API token secret>
```
{% endraw %}

Do not place the token value in unencrypted inventory variables or in this runbook. The deployment role stops before making changes if this value is missing.

The Proxmox API user and token must already exist and have permission to read the cluster metrics exposed by the Proxmox API. Use the **PVEAuditor** role for this user and token.

---

## 🚀 Deploy PVE Exporter

Run the Proxmox monitoring playbook against the PVE inventory:

{% raw %}
```bash
ansible-playbook -i inventory/pve/inventory.ini playbooks/proxmox/deploy_pve_monitoring.yml
```
{% endraw %}

What this does on every `pvenodes` host:

* installs or updates node exporter
* installs `prometheus-pve-exporter` in `/opt/pve_exporter`
* renders `/etc/pve_exporter/pve.yml`
* installs and starts the `pve_exporter` systemd service
* listens on port `9221` by default

The playbook deploys both node exporter and PVE exporter. It does not update the Prometheus scrape configuration by itself.

Alternatively, each exporter can be deployed separately using two distinct playbooks. 

To deploy node exporter, execute

{% raw %}
```bash
ansible-playbook -i inventory/pve/inventory.ini playbooks/prometheus/deploy_node_exporter.yml
```
{% endraw %}

To deploy pve exporter, execute

{% raw %}
```bash
ansible-playbook -i inventory/pve/inventory.ini playbooks/prometheus/deploy_pve_exporter.yml
```
{% endraw %}

---

## 🔄 Deploy the Updated Targets to Prometheus

Refresh the Prometheus exporter scrape configuration using the repository's combined default inventory:

{% raw %}
```bash
ansible-playbook -i inventory/pve/inventory.ini playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

What this does:

* reads the `pve_exporter` group from the combined inventory
* merges its hosts into the existing PVE exporter targets
* renders the Prometheus `pve_exporter` scrape job
* points each target at the host's `pve_exporter_setup_port`

---

## ✅ Validate Before Deploying

If Ansible is installed in the repository Python environment:

{% raw %}
```bash
source /opt/python_3.12/bin/activate
ansible-inventory -i inventory/pve/inventory.ini --graph
ansible-playbook -i inventory/pve/inventory.ini playbooks/proxmox/deploy_pve_monitoring.yml --syntax-check
ansible-playbook playbooks/prometheus/deploy_prometheus_exporters.yml --syntax-check
```
{% endraw %}

Confirm that the inventory graph places the intended nodes under both `pvenodes` and `pve_exporter`.

---

## 🔍 Verify After Deployment

### On each Proxmox node

Check the service:

{% raw %}
```bash
systemctl status pve_exporter
```
{% endraw %}

Check the local exporter endpoint:

{% raw %}
```bash
curl --fail 'http://localhost:9221/pve?module=local&target=localhost'
```
{% endraw %}

The response should contain Prometheus metrics and should not report an authentication or permission error.

### In Prometheus

Run:

{% raw %}
```promql
up{job="pve_exporter"}
```
{% endraw %}

Expected behavior:

* every monitored Proxmox node appears in the `pve_exporter` job
* the `instance` label matches the inventory host name
* the value is `1` when the exporter and Proxmox API are reachable

You can also check a PVE metric:

{% raw %}
```promql
pve_up{job="pve_exporter"}
```
{% endraw %}

### In Grafana

Open the Proxmox VE status dashboard and confirm that the cluster and nodes report current data.

---

## ⚠️ Common Mistakes

* Adding a host outside `pvenodes`, so the deployment playbook does not target it
* Removing `pvenodes` from the `pve_exporter` children group
* Forgetting the host's `global_ip_addresses` entry
* Leaving `pve_exporter_setup_api_token_value` undefined
* Using an API token without sufficient Proxmox read permissions
* Deploying PVE exporter but forgetting to refresh Prometheus exporters
* Passing only the PVE inventory to `deploy_prometheus_exporters.yml`
* Testing `/metrics` instead of the configured `/pve` probe endpoint

---

## ✅ Summary

To deploy PVE exporter to the Proxmox nodes:

1. Add each node to `pvenodes` in `inventory/pve/inventory.ini`.
2. Keep `pvenodes` under `[pve_exporter:children]`.
3. Define the port and API user in `inventory/pve/group_vars/all.yml`.
4. Supply `pve_exporter_setup_api_token_value` securely.
5. Deploy `playbooks/proxmox/deploy_pve_monitoring.yml` with the PVE inventory.
6. Deploy `playbooks/prometheus/deploy_prometheus_exporters.yml` with the combined default inventory.
7. Verify the `pve_exporter` job in Prometheus and the Proxmox VE dashboard in Grafana.

The inventory is the source of truth for which Proxmox nodes are deployed and scraped.
