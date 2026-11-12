---
title: "Ceph Mgr Prometheus Module"
---

# 🐙 Ceph Mgr Prometheus Module

## 🎯 Purpose

The `ceph-mgr` Prometheus module exposes Ceph cluster metrics for Prometheus and Grafana. In this environment, it provides:

* Cluster health, monitor quorum, and placement group state for the Proxmox Ceph cluster
* OSD status, capacity, and latency metrics
* Pool capacity and usage metrics
* A Ceph view alongside the Proxmox API metrics from `pve_exporter` and host metrics from Node Exporter

---

## ⚙️ How It Works

* The module runs inside the Ceph manager daemon (`ceph-mgr`); there is no separate exporter to install
* Every manager listens on port `9283` and serves `/metrics`
* Only the **active** manager returns Ceph metrics; standby managers answer the scrape with no Ceph samples
* Prometheus scrapes every node in `ceph_nodes` every 30 seconds, so data keeps flowing after a manager failover
* The `ceph` scrape job uses `honor_labels: true` so labels set by `ceph-mgr` are kept
* Grafana uses the resulting metrics for the Ceph panels on the Proxmox dashboard

---

## 🧩 Key Concepts

### 📊 Cluster Metrics

These metric families come from the active manager and describe the whole cluster:

* `ceph_health_status` — `0` = HEALTH_OK, `1` = HEALTH_WARN, `2` = HEALTH_ERR
* `ceph_health_detail` — one series per active health check, labelled by `name`
* `ceph_mon_quorum_status` — `1` when a monitor is in quorum
* `ceph_cluster_total_bytes` and `ceph_cluster_total_used_bytes` — raw cluster capacity
* `ceph_pg_total`, `ceph_pg_active`, and `ceph_pg_clean` — placement group counts per pool

### 💽 OSD and Pool Metrics

* `ceph_osd_up` and `ceph_osd_in` — OSD state
* `ceph_osd_stat_bytes` and `ceph_osd_stat_bytes_used` — per-OSD capacity
* `ceph_osd_apply_latency_ms` and `ceph_osd_commit_latency_ms`
* `ceph_osd_metadata` — maps each OSD to its host and device class
* `ceph_pool_percent_used`, `ceph_pool_stored`, and `ceph_pool_max_avail`
* `ceph_pool_metadata` — maps `pool_id` to the pool name

The `ceph_daemon` label identifies a daemon, such as `osd.0` or `mon.pve-0`. Pool metrics use the `pool_id` label; join with `ceph_pool_metadata` to get the pool name.

### 📈 Per-Daemon Performance Counters

Since Ceph Reef, per-daemon performance counters (such as `ceph_osd_op_r_latency_sum` and `ceph_osd_op_w`) are excluded from the manager module by default. They are expected to come from cephadm's `ceph-exporter` daemon, which Proxmox does not deploy.

This environment sets `mgr/prometheus/exclude_perf_counters` to `false`, so the manager module exports them instead.

---

## 📁 Configuration & Service

**Configuration:**
Stored in the Ceph configuration database, not in a file. View it with `ceph config get mgr mgr/prometheus/<option>`.

**Service:**
`ceph-mgr@<node>` (systemd), for example `ceph-mgr@pve-0`

**Listener:**
`:::9283` by default (all addresses)

**Module settings managed by Ansible:**

* `ceph mgr module enable prometheus`
* `mgr/prometheus/exclude_perf_counters` = `false`

**Prometheus settings** (`roles/prometheus_setup/defaults/main/main.yml`):

* `prometheus_setup_ceph_job_name: "ceph"`
* `prometheus_setup_ceph_port: 9283`
* `prometheus_setup_ceph_alerts_enabled: true`

The module needs no credentials and serves metrics without authentication.

---

## 🚀 Deployment

The `ceph_nodes` inventory group contains the Proxmox Ceph nodes. Enable and configure the module with:

{% raw %}
```bash
source /opt/python_3.12/bin/activate
ansible-playbook -i inventory/pve/inventory.ini playbooks/proxmox/deploy_pve_monitoring.yml
```
{% endraw %}

The Ceph tasks run once, on the first host in `ceph_nodes`, because the module is cluster-wide. The same playbook also deploys Node Exporter and PVE Exporter to the Proxmox nodes.

Refresh Prometheus scrape targets after inventory changes:

{% raw %}
```bash
ansible-playbook playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

This refresh command uses the repository's full combined inventory (`inventory/`); do not limit it to `inventory/pve/`, or exporter groups from other inventories will be omitted from that run.

Deploy the Ceph alert rules with the main Prometheus playbook, then refresh the exporter targets again:

{% raw %}
```bash
ansible-playbook -i inventory/prometheus/inventory.ini playbooks/prometheus/deploy_prometheus.yml
ansible-playbook playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

Syntax-check the deployment playbook before applying changes:

{% raw %}
```bash
ansible-playbook -i inventory/pve/inventory.ini --syntax-check playbooks/proxmox/deploy_pve_monitoring.yml
```
{% endraw %}

**[Deploying the Ceph Mgr Prometheus Module to Proxmox_Nodes](deploying_the_ceph_mgr_prometheus_module_to_proxmox_nodes.md) runbook** provides a comprehensive instruction on deploying Ceph Mgr using Ansible.

---

## 🔔 Alert Rules

The `ceph` group in `prometheus.rules.yml` contains:

* `CephMetricsAbsent` — no Ceph metrics for 5 minutes (critical)
* `CephHealthWarning` — HEALTH_WARN for 15 minutes (warning)
* `CephHealthError` — HEALTH_ERR for 5 minutes (critical)
* `CephMonQuorumLost` — a monitor out of quorum for 5 minutes (warning)
* `CephOSDDown` — an OSD down for 5 minutes (critical)
* `CephOSDOut` — an OSD marked out for 15 minutes (warning)
* `CephOSDNearFull` — an OSD over 80% used for 15 minutes (warning)
* `CephClusterNearFull` — raw capacity over 80% used for 15 minutes (warning)
* `CephClusterCriticallyFull` — raw capacity over 90% used for 5 minutes (critical)
* `CephPGsNotActive` — placement groups not active for 15 minutes (critical)

`prometheus.yml` does not currently have an `alerting:` section, so these alerts appear in Prometheus and Grafana but are not sent to Alertmanager.

* * *

## 🔍 Common Prometheus Queries

* Check that each manager endpoint is reachable:
  `up{job="ceph"}`
* Find which node holds the active manager:
  `count by (instance) (ceph_health_status{job="ceph"})`
* Check cluster health:
  `max(ceph_health_status)`
* List active health checks:
  `ceph_health_detail == 1`
* Find down OSDs:
  `max by (ceph_daemon) (ceph_osd_up) == 0`
* Check raw cluster usage:
  `max(ceph_cluster_total_used_bytes / ceph_cluster_total_bytes)`
* Check pool usage by name:
  `max by (pool_id) (ceph_pool_percent_used) * on (pool_id) group_left (name) max by (pool_id, name) (ceph_pool_metadata)`
* Find OSDs with high commit latency:
  `topk(5, max by (ceph_daemon) (ceph_osd_commit_latency_ms))`

---

## 📊 Grafana Usage Notes

The **Proxmox VE Status** dashboard uses the `ceph` job for its Ceph Health, OSDs Up / Total, Capacity Used, Monitors In Quorum, and Pool Usage panels. The `pve_exporter` and Node Exporter jobs provide the Proxmox API and host-level metrics for the same nodes.

Because the standby managers return no Ceph data, dashboard queries wrap Ceph metrics in `max` or `max by (...)` so a manager failover does not create duplicate or broken series.

---

## 🛠️ Troubleshooting

### ❌ Ceph Target Is Down

Check:

* The node runs a `ceph-mgr` daemon (`ceph mgr stat`)
* Port `9283` is reachable from Prometheus and not blocked by the Proxmox firewall
* The target address matches the host's `global_ip_addresses` entry

### 📭 Targets Are Up but There Is No Ceph Data

Check:

* The module is enabled: `ceph mgr module ls | grep prometheus`
* An active manager exists: `ceph mgr stat`
* `ceph mgr services` lists a `prometheus` URL
* The node with the active manager is in `ceph_nodes`

This is the condition that triggers `CephMetricsAbsent`.

### 📈 Per-OSD Latency or Operation Metrics Are Missing

Check:

* `ceph config get mgr mgr/prometheus/exclude_perf_counters` returns `false`
* Rerun `deploy_pve_monitoring.yml` if it does not

### 🛠️ Quick Verification Commands

{% raw %}
```bash
ceph mgr stat
ceph mgr services
ceph mgr module ls | grep prometheus
systemctl status ceph-mgr@$(hostname)
journalctl -u ceph-mgr@$(hostname) -n 50 --no-pager
curl -s http://localhost:9283/metrics | grep '^ceph_health_status'
```
{% endraw %}

Run the `curl` command on the node with the active manager; on a standby node it returns nothing.

---

## 🔐 Security & Operational Guidance

* The metrics endpoint has no authentication; restrict port `9283` to Prometheus and trusted administration hosts
* Keep at least two managers in the cluster so metrics survive a manager failure
* Keep every manager node in `ceph_nodes` so Prometheus follows the active manager
* Treat a firing `CephMetricsAbsent` alert as a monitoring outage, not a healthy cluster

---

## 🧾 Summary

The `ceph-mgr` Prometheus module exposes Ceph cluster, OSD, and pool metrics from the active manager for Prometheus to scrape. Prometheus scrapes every Ceph node so it follows manager failovers, and the `ceph` alert group and Proxmox dashboard make cluster health and capacity visible alongside the PVE exporter and Node Exporter metrics.
