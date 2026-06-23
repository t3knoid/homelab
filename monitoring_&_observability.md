---
title: "Monitoring & Observability"
---

# 📈 Monitoring & Observability

The homelab uses a unified monitoring stack built around **[Prometheus](prometheus.md)** and **[Grafana](grafana.md)**, providing full visibility into compute, storage, networking, and application services. This observability layer acts as the telemetry backbone of the environment, enabling early failure detection, performance analysis, and long‑term capacity planning.

This page serves as the central hub for all monitoring‑related documentation.

---

## 📡 Overview

The monitoring pipeline follows a simple, reliable flow:

{% raw %}
```
Services → Exporters → Prometheus → Grafana → Alerts
```
{% endraw %}

- **Services** expose metrics directly or through exporters  
- **Exporters** convert service‑specific data into Prometheus format  
- **Prometheus** scrapes and stores metrics  
- **Grafana** visualizes dashboards and alerts  
- **Alerting** notifies when thresholds or anomalies occur  

Prometheus and Grafana are both deployed and managed using **Ansible**, ensuring consistent, reproducible configuration across the homelab.

---

## 🗺️ Homelab-Wide Metrics Architecture

A complete breakdown of how metrics flow across the environment, including exporters, storage systems, Proxmox, Docker media stack, Plex, Pi‑hole, and network devices.

👉 **See the full architecture:**  **[Homelab-Wide Metrics Architecture](homelab-wide_metrics_architecture.md)**

---

## 🔥 Prometheus

Prometheus is the metrics collection and storage engine for the homelab. It scrapes exporters across compute, storage, networking, and application layers, storing data in a high‑performance time‑series database.

Prometheus documentation includes:

- How Prometheus works  
- Exporters used across the homelab  
- Scrape configuration  
- Deployment via Ansible  
- Integration with Grafana  

To read further details,
👉 See the **[Prometheus](prometheus.md)** page.

---

## 📊 Grafana

Grafana provides dashboards, visualizations, and alerting for all Prometheus metrics. It serves as the primary interface for exploring system health, performance trends, and service‑level insights.

Grafana documentation includes:

- Datasource configuration  
- Dashboard provisioning  
- Alerting setup  
- Authentication and reverse proxy integration  
- Deployment via Ansible  

To read further details,
👉 See the **[Grafana](grafana.md)** page.

---

## 🧰 Exporters

Exporters expose metrics from services that do not natively support Prometheus format. The homelab uses a wide range of exporters, including:

- `node_exporter` — Linux hosts, Proxmox nodes  
- `pve_exporter` — Proxmox API metrics  
- `nginx-prometheus-exporter` — reverse proxy  
- `ceph-mgr` Prometheus module — Ceph cluster  
- `synology_exporter` — Synology NAS  
- `truenas_exporter` — TrueNAS  
- `docker_exporter` / `cAdvisor` — Docker containers  
- `pihole_exporter` — Pi‑hole DNS  
- `snmp_exporter` — network switches and routers  
- `blackbox_exporter` — HTTP/ICMP/TCP checks  

👉 **See exporter details inside each service’s monitoring page.**

---

## 🖥️ Per‑Service Monitoring

Each major subsystem in the homelab has its own monitoring page:

- **Compute**
  - [Proxmox Monitoring](proxmox_monitoring.md)
  - [Node Monitoring](node_monitoring.md)
  - [Docker Monitoring](docker_monitoring.md)

- **Storage**
  - [Ceph Monitoring](ceph_monitoring.md)
  - [Synology Monitoring](synology_monitoring.md)
  - [TrueNAS Monitoring](truenas_monitoring.md)

- **Applications**
  - [Plex Monitoring](plex_monitoring.md)
  - [Media Stack Monitoring](media_stack_monitoring.md) (Radarr, Sonarr, Lidarr, Sabnzbd, CalibreWeb, LazyLibrarian)

- **Networking**
  - [Pi-hole Monitoring](pi-hole_monitoring.md)
  - [Network Device Monitoring](network_device_monitoring.md)

- **Reverse Proxy**
  - [Nginx Reverse Proxy Monitoring](nginx_reverse_proxy_monitoring.md) 

These pages document exporters, dashboards, alerts, and troubleshooting workflows.

---

## 🚨 Alerting

Alerting is handled through:

- Grafana Unified Alerting  
- Optional Prometheus Alertmanager integration  

Alerts cover:

- Disk failures  
- Container crashes  
- Ceph health  
- Proxmox node issues  
- Network saturation  
- DNS failures  
- Reverse proxy errors  

👉 See: **[Alerting](alerting.md)**