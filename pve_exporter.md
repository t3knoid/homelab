---
title: "Pve exporter"
---

# Pve exporter

## 🎯 Purpose

`pve_exporter` exposes Proxmox VE metrics for Prometheus and Grafana. In this environment, it provides:

* Node, storage, and virtual machine metrics from the Proxmox API
* VM snapshot timestamps and a snapshot collection health metric
* A per-node view of Proxmox, alongside host-level metrics from Node Exporter

---

## ⚙️ How It Works

* `pve_exporter` runs on each Proxmox node and listens on port `9221`
* Prometheus scrapes `/pve` every 30 seconds, passing `module=local` and `target=localhost`
* Each exporter reads its local Proxmox API; the same cluster-wide API token is used on every node
* Grafana uses the resulting metrics for Proxmox dashboards

---

## 🧩 Key Concepts

### 📊 Proxmox Metrics

The exporter reports metrics for Proxmox nodes, guests, and storage. Common metric families used by the dashboards include:

* `pve_up` — resource availability
* `pve_cpu_usage_ratio`
* `pve_memory_usage_bytes` and `pve_memory_size_bytes`
* `pve_disk_usage_bytes` and `pve_disk_size_bytes`
* `pve_guest_info`
* `pve_disk_read_bytes_total` and `pve_disk_written_bytes_total`
* `pve_network_receive_bytes_total` and `pve_network_transmit_bytes_total`

The `id` label identifies a resource, such as `node/<name>`, `qemu/<vmid>`, or `lxc/<vmid>`.

### 📸 VM Snapshot Metrics

The local snapshot collector adds:

* `pve_vm_snapshot_created_timestamp_seconds` — creation time for collected QEMU VM snapshots
* `pve_vm_snapshot_collection_success` — whether the local snapshot collection completed successfully

Templates and the `current` snapshot entry are excluded. Snapshot collection requires the Proxmox API token to have the necessary access, including `VM.Audit`.

---

## 📁 Configuration & Service

**Configuration file:**
`/etc/pve_exporter/pve.yml`

**Service:**
`pve_exporter` (systemd)

**Listener:**
`0.0.0.0:9221`

The service runs as the `pve-exporter` system user. The API token value is supplied through Ansible vault; do not put it in this page, metric labels, or other public configuration.

---

## 🚀 Deployment

The `pve_exporter` inventory group contains the Proxmox nodes. Deploy the exporter with:

{% raw %}
```bash
source /opt/python_3.12/bin/activate
ansible-playbook -i inventory/pve/inventory.ini playbooks/prometheus/deploy_pve_exporter.yml
```
{% endraw %}

To deploy Node Exporter and PVE Exporter together, use:

{% raw %}
```bash
ansible-playbook -i inventory/pve/inventory.ini playbooks/proxmox/deploy_pve_monitoring.yml
```
{% endraw %}

Refresh Prometheus scrape targets after inventory changes:

{% raw %}
```bash
ansible-playbook playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

This refresh command uses the repository's full combined inventory (`inventory/`); do not limit it to `inventory/pve/`, or exporter groups from other inventories will be omitted from that run.

Syntax-check the deployment playbook before applying changes:

{% raw %}
```bash
ansible-playbook -i inventory/pve/inventory.ini --syntax-check playbooks/prometheus/deploy_pve_exporter.yml
```
{% endraw %}

The **[Deploy PVE_Exporter to Proxmox Nodes](deploy_pve_exporter_to_proxmox_nodes.md)** runbook provides detailed stops on deploying the PVE Exporter using Ansible.

---

## 🔍 Common Prometheus Queries

* Check that each exporter endpoint is reachable:
  `up{job="pve_exporter"}`
* Check Proxmox node availability:
  `pve_up{id=~"node/.+"}`
* Check unavailable guests:
  `pve_up{id=~"(qemu|lxc)/.+"} == 0`
* Check snapshot collector health:
  `pve_vm_snapshot_collection_success`
* Find VM snapshot creation times:
  `pve_vm_snapshot_created_timestamp_seconds`

---

## 📊 Grafana Usage Notes

The Proxmox dashboards use the `pve_exporter` job for node, storage, guest, and snapshot panels. Node Exporter is a separate job and provides operating-system metrics for the same hosts.

---

## 🛠️ Troubleshooting

### ❌ Exporter Target Is Down

Check:

* The `pve_exporter` systemd service is active on the Proxmox node
* Port `9221` is reachable from Prometheus
* The Prometheus target uses `/pve`, `module=local`, and `target=localhost`
* The API token is configured through vault and can access the Proxmox API

### 📸 Snapshot Metrics Are Missing

Check:

* `pve_vm_snapshot_collection_success` is `1`
* The token has `VM.Audit` access for the local node's VMs
* The service logs for API access errors

### 🛠️ Quick Verification Commands

{% raw %}
```bash
systemctl status pve_exporter
journalctl -u pve_exporter -n 50 --no-pager
curl -G 'http://localhost:9221/pve' \
  --data-urlencode 'module=local' \
  --data-urlencode 'target=localhost'
```
{% endraw %}

---

## 🔐 Security & Operational Guidance

* Keep the API token in Ansible vault; never put it in source-controlled plaintext
* Restrict access to port `9221` to Prometheus and trusted administration hosts
* Use a dedicated API user and token with only the permissions needed for collection
* Protect the exporter configuration file because it contains API credentials

---

## 🧾 Summary

`pve_exporter` exposes Proxmox API metrics from each node for Prometheus to scrape. Its additional snapshot collector makes VM snapshot age visible in Grafana, while Node Exporter separately reports host-level health.