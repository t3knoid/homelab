---
title: "️ Node Exporter"
---

# 🖥️ Node Exporter

## 🎯 Purpose
Node Exporter provides host‑level metrics for Prometheus, which Grafana uses for dashboards and service visibility. In your environment, it supports:

- CPU, memory, disk, filesystem, and network health  
- Custom textfile metrics from local scripts  
- Failed‑service visibility via systemd metrics

---

## ⚙️ How It Works
- Node Exporter runs on each monitored host  
- Prometheus scrapes the exporter  
- Grafana visualizes the metrics for dashboards and troubleshooting

---

## 🧩 Key Concepts

### 📊 Native Metrics
Examples include:
- `node_cpu_seconds_total`  
- `node_memory_MemAvailable_bytes`  
- `node_filesystem_avail_bytes`  
- `node_network_receive_bytes_total`  
- `up`

### 📝 Textfile Collector Metrics
Allows scripts to publish custom `.prom` metrics.

Flow:
1. Script writes Prometheus‑formatted metrics  
2. File is atomically moved into the collector directory  
3. Node Exporter exposes metrics at scrape time  

Benefits:
- Safe, simple custom checks  
- No custom exporters needed  
- Easy extension for operational signals

---

## 📁 Textfile Collector Paths & Files

**Collector directory**  
`/var/lib/node_exporter/textfile`

**Script paths**  
- `/usr/local/bin/check_updates.sh`  
- `/usr/local/bin/check_failed_services.sh`

**Metrics files**  
- `/var/lib/node_exporter/textfile/linux_updates.prom`  
- `/var/lib/node_exporter/textfile/failed_services.prom`

**Refresh cadence**  
- Updates: `*/30`  
- Failed services: `*/2`

---

## 📈 Current Custom Metrics

### 🔒 Linux Update Metrics
Written to: `linux_updates.prom`  
Metric families:
- `linux_updates_available`  
- `linux_security_updates_available`

### 🚨 Failed Systemd Service Metrics
Written to: `failed_services.prom`  
Metric families:
- `linux_systemd_failed_services`  
- `linux_systemd_failed_services_last_collect_unixtime`  
- `linux_systemd_service_failed`  
- `linux_systemd_service_failed_info`

Labels include:
- `service`  
- `host`  
- `active_state`  
- `sub_state`  
- `result`

---

## 🚀 Deployment

Deployment is managed via Ansible roles and deployed through the Node Exporter playbook.

Operational behavior:
- Binary + service unit managed by role tasks  
- Textfile collector directory created and permissioned  
- Custom scripts installed and scheduled  
- Cron jobs refresh metric files

### 🛠️ Sample Commands
Deploy:
{% raw %}
```
source /opt/python_3.12/bin/activate
ansible-playbook -i inventory/rproxy/inventory.ini playbooks/prometheus/deploy_node_exporter.yml
```
{% endraw %}

Syntax check:
{% raw %}
```
ansible-playbook --syntax-check ...
```
{% endraw %}

Refresh Prometheus exporter targets:
{% raw %}
```
ansible-playbook playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

👉 See also: **[Adding Node Exporter to an Inventory](adding_node_exporter_to_an_inventory.md)**

---

## 🔍 Common Prometheus Queries
- Check scrape health  
  `up{job="node"}`  
- Count failed services  
  `sum(linux_systemd_failed_services{job="node"})`  
- List failed units  
  `linux_systemd_service_failed_info{job="node"}`  
- Filter oauth2‑proxy + nginx  
  `service=~"(oauth2-proxy.*|nginx.*)"`  
- Detect stale collection  
  `time() - max(linux_systemd_failed_services_last_collect_unixtime{job="node"})`

---

## 📊 Grafana Usage Notes
- Use table panels with label expansion  
- Merge frames when needed  
- Keep host + regex variables for drill‑down  
- Default regex: `.*`  
- Focused regex: `(oauth2-proxy.*|nginx.*)`

---

## 🛠️ Troubleshooting

### ❌ No Failed Service Data
Check:
- Node Exporter target is up  
- Metrics file exists and is readable  
- Script output is valid Prometheus format  
- Dashboard queries reference correct metric families  
- Service names parsed correctly

### 🐢 Slow Data Updates
Cause: Cron interval too long  
Fix: Reduce failed‑service collection interval

### 🔎 Quick Verification Commands
{% raw %}
```
ls -l /var/lib/node_exporter/textfile
cat /var/lib/node_exporter/textfile/failed_services.prom
cat /var/lib/node_exporter/textfile/linux_updates.prom
systemctl status node_exporter
```
{% endraw %}

---

## 🔐 Security & Operational Guidance
- Never embed secrets in metric labels  
- Keep script output deterministic  
- Use atomic writes  
- Prefer gauge semantics for current‑state checks

---

## 🧾 Summary

Node Exporter is the foundation of host‑level observability in your stack. The textfile collector extends visibility with operational checks like failed systemd services, enabling clear Grafana dashboards and future alerting.