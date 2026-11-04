---
title: "Adding Prometheus Support to a VM or Service"
---

# ➕ Adding Prometheus Support to a VM or Service

Choose the monitoring level you need: **node metrics** for a VM’s operating system, a **service exporter** for application-specific metrics, or **Blackbox probes** to monitor whether a service endpoint responds. Inventory membership drives Prometheus scrape targets.

## 1. Add the target to inventory

Add the VM or service to the appropriate inventory and exporter group. For a new host, also add its address to `global_ip_addresses` in `main.yml`. Set exporter ports and required configuration in that inventory’s `group_vars/all/main.yml`; keep secrets in its vault file.

## 2. Use the matching exporter workflow

| Need | Inventory/configuration | Deployment playbook |
|---|---|---|
| Linux host metrics | Add host to `node_exporter`; default port is `9200` | `deploy_node_exporter.yml` |
| NGINX metrics | Add NGINX host to `nginx_exporter`; default port is `9113` | `deploy_nginx_prometheus_exporter.yml` |
| NGINX per-domain traffic | Add configured NGINX host to `nginxlog_exporter` | `deploy_nginxlog_exporter.yml` |
| PostgreSQL metrics | Add database host to `postgres_exporter`; configure port `9187` and credentials | `deploy_postgres_exporter.yml` |
| Proxmox metrics | Use the `pve_exporter` group in the PVE inventory | `deploy_pve_exporter.yml` |
| Plex metrics | Use the `plex_exporter` group in the Plex inventory | `deploy_plex_exporter.yml` |
| HTTP service availability | Add a target under `prometheus_setup_blackbox_targets` in `main.yml` | `deploy_blackbox_exporter.yml` if the exporter needs deploying |

Follow the relevant runbook for exporter-specific settings: [Adding Node Exporter to an Inventory](adding_node_exporter_to_an_inventory.md), [Adding NGINX Exporter to an Inventory](adding_nginx_exporter_to_an_inventory.md), [Adding Postgres Exporter to an Inventory](adding_postgres_exporter_to_an_inventory.md), or [Adding Blackbox Exporter Targets](adding_blackbox_exporter_targets.md).

Ceph uses a Prometheus scrape configuration for the `ceph_nodes` group and its native metrics endpoint; it does not have a separate exporter deployment playbook here.

## 3. Deploy the exporter and refresh Prometheus

Run the selected exporter deployment playbook against the inventory containing its target. After changing exporter group membership or Blackbox targets, refresh Prometheus:

{% raw %}
```shell
ansible-playbook -k playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

**Use the default combined inventory for this refresh.** Do not pass a single inventory with `-i`: the playbook needs the exporter groups across inventories to be visible.

## 4. Verify

In Prometheus, check **Status → Targets** and confirm the target is healthy. For standard exporter jobs, `up{job="<job_name>"}` should be `1`. For Blackbox probes, check `probe_success{job="blackbox_http"}`.

The scrape configuration merges newly discovered targets with existing ones. Removing a host from inventory may not remove a previously rendered target; see `remove_prometheus_targets.yml` for cleanup.