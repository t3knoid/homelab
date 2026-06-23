---
title: "Grafana"
---

# 📊 **Grafana**

Grafana is the visualization and dashboarding layer of the homelab’s observability stack. It provides a unified interface for exploring metrics, building dashboards, and defining alert rules based on data collected by **[Prometheus](prometheus.md)**. Grafana transforms raw time-series data into actionable insights for capacity planning, troubleshooting, and long-term analysis.

Grafana is deployed and managed using **[Ansible](ansible.md)**, ensuring consistent configuration, reproducible provisioning, and version-controlled infrastructure changes.

> [!TIP]
> For the dashboard-as-code workflow used in this repository, see **[Configure Grafana Dashboards Process](configure_grafana_dashboards_process.md)**.
> This process page covers how to add JSON dashboards, update role defaults, align provisioning tasks, and deploy safely.

---

## 🎯 **Purpose**

Grafana serves as the primary interface for:

- Visualizing metrics from Prometheus
- Building dashboards for compute, storage, networking, and applications
- Monitoring long-term trends and resource usage
- Creating alert rules for critical events
- Providing a centralized observability portal for the entire homelab

Grafana integrates directly with Prometheus as its main datasource, but can also connect to Loki, InfluxDB, Elasticsearch, and other systems if needed.

---

## 🧰 **Key Features**

### 📊 **1. Dashboards**
Grafana dashboards provide real-time and historical views of:

- Proxmox cluster performance
- Ceph storage health
- Docker media stack (Radarr, Sonarr, Lidarr, Sabnzbd, CalibreWeb, etc.)
- Plex Media Server activity
- Pi-hole DNS statistics
- Synology and TrueNAS storage metrics
- Nginx reverse proxy traffic and errors
- Network device performance via SNMP

Dashboards can be imported from Grafana’s public library or built from scratch.

### 🗄️ **2. Datasources**
The primary datasource in this homelab is:

- **Prometheus** — metrics collection and storage

Additional datasources can be added as the environment grows.

### 🚨 **3. Alerting**
Grafana supports alerting through:

- Unified Alerting (Grafana’s built-in alert engine)
- Prometheus Alertmanager (optional integration)

Alerts can be routed to email, ntfy, Slack, Matrix, or other notification channels.

### 🔐 **4. User Access & Authentication**
Grafana supports:

- Local users
- OAuth2 / OIDC
- Reverse proxy authentication

In this homelab, Grafana is protected behind the Nginx reverse proxy and OAuth2 authentication layer.

---

## ⚙️ **Deployment**

Grafana is deployed using **Ansible**, which manages:

- Installation and version pinning
- Datasource configuration (Prometheus)
- Dashboard provisioning
- Folder structure for dashboards
- Alerting configuration
- Service management
- Plugin installation (if used)

This ensures that Grafana is fully reproducible and can be rebuilt or migrated without manual configuration drift.

---

## 📚 **Dashboards in Use**

The homelab uses a combination of:

- **Official Grafana dashboards**
- **Community dashboards**
- **Custom dashboards** tailored to Proxmox, Ceph, Docker, Plex, Pi-hole, and storage systems

Dashboards are organized by category:

- **Compute** — Proxmox, VMs, node_exporter
- **Storage** — Ceph, Synology, TrueNAS
- **Applications** — Media stack, Plex, CalibreWeb
- **Networking** — SNMP devices, Pi-hole
- **Reverse Proxy** — Nginx metrics and request flow

---

## 🔗 **Relevant Links**

### 📘 **Official Documentation**
- Grafana: https://grafana.com
- Grafana Docs: https://grafana.com/docs
- Dashboard Library: https://grafana.com/grafana/dashboards
- Alerting: https://grafana.com/docs/grafana/latest/alerting

### 🌐 **Ecosystem**
- Prometheus: https://prometheus.io
- Loki (optional logs): https://grafana.com/oss/loki
- Tempo (optional traces): https://grafana.com/oss/tempo
