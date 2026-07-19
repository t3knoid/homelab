---
title: "Prometheus"
---

# 🔥 **Prometheus**

Prometheus is the primary metrics collection and storage engine used in this homelab. It provides a unified, scalable way to gather telemetry from compute, storage, networking, and application services. Prometheus scrapes metrics from exporters running across the environment and stores them in a time‑series database optimized for high‑cardinality operational data. This data is visualized using **[Grafana](grafana.md)**.

Prometheus is deployed and managed using **[Ansible](ansible.md)**, ensuring consistent configuration, reproducible deployments, and version‑controlled infrastructure changes.

---

## 🎯 **Purpose**

Prometheus acts as the central observability backbone for the homelab. It enables:

- Cluster‑wide visibility into system health  
- Early detection of failures (disk issues, container crashes, network saturation)  
- Long‑term performance and capacity analysis  
- Unified monitoring across Proxmox, Ceph, Docker, Plex, Pi‑hole, Synology, TrueNAS, and the Nginx reverse proxy  
- A consistent, scalable monitoring model as new services are added  

Prometheus integrates directly with Grafana, which provides dashboards, visualizations, and alerting.

---

## 🔄 **How Prometheus Works**

Prometheus uses a pull‑based model:

{% raw %}
```
Services → Exporters → Prometheus → Grafana → Alerts
```
{% endraw %}

- **Services** expose metrics directly or via exporters  
- **Exporters** convert service‑specific metrics into Prometheus format  
- **Prometheus** scrapes these endpoints on a defined interval  
- **Grafana** queries Prometheus for dashboards and alert rules  

This architecture ensures reliability, simplicity, and clear data flow.

---

## 🧩 **Key Components**

### 🏛️ **1. Prometheus Server**
- Scrapes metrics from exporters  
- Stores time‑series data  
- Exposes a query interface (PromQL)  
- Provides service discovery and scrape scheduling

### 📦 **2. Exporters**
Prometheus relies on exporters to expose metrics from services that do not natively support Prometheus format.

Common exporters in this homelab include:

- **[nginx-prometheus-exporter](nginx-prometheus-exporter.md)** (reverse proxy)  
- **[node_exporter](node_exporter.md)** (Linux hosts, Proxmox nodes)  
- **[pve_exporter](pve_exporter.md)** (Proxmox API metrics)  
- **[ceph-mgr Prometheus module](ceph-mgr_prometheus_module.md)** (Ceph cluster)  
- **[synology_exporter](synology_exporter.md)** (Synology NAS)  
- **[truenas_exporter](truenas_exporter.md)** (TrueNAS)  
- **[docker/cAdvisor exporters](docker/cadvisor_exporters.md)** (media stack containers)  
- **[pihole_exporter](pihole_exporter.md)** (Pi‑hole DNS)  
- **[snmp_exporter](snmp_exporter.md)** (network gear)  
- **[blackbox_exporter](blackbox_exporter.md)** (HTTP/ICMP/TCP checks)

### 📐 **3. PromQL**
Prometheus Query Language (PromQL) is used to build dashboards, alerts, and diagnostic queries.

---

## ⚙️ **Deployment**

Prometheus is deployed using **Ansible**, which manages:

- Installation  
- Configuration (`prometheus.yml`)  
- Scrape jobs  
- Exporter deployment  
- Service management  
- Updates and version pinning  

This ensures the monitoring stack is reproducible, consistent, and easy to extend.

---

## 📡 **Scrape Configuration Overview**

A typical `prometheus.yml` includes jobs for:

- Reverse proxy (Nginx)  
- Proxmox nodes  
- Docker media stack (Radarr, Sonarr, Lidarr, Sabnzbd, CalibreWeb, etc.)  
- Plex Media Server  
- Ceph cluster  
- Synology and TrueNAS storage  
- Pi‑hole DNS  
- Network switches and routers  
- Blackbox health checks for internal services  

Each job defines targets, labels, and scrape intervals.

---

## 🔗 **Relevant Links**

### 📘 **Official Documentation**
- Prometheus: https://prometheus.io  
- Prometheus Docs: https://prometheus.io/docs/introduction/overview  
- PromQL: https://prometheus.io/docs/prometheus/latest/querying/basics  
- Exporters List: https://prometheus.io/docs/instrumenting/exporters  

### 🧰 **Common Exporters**
- Nginx Exporter: https://github.com/nginxinc/nginx-prometheus-exporter  
- Node Exporter: https://github.com/prometheus/node_exporter  
- Blackbox Exporter: https://github.com/prometheus/blackbox_exporter  
- SNMP Exporter: https://github.com/prometheus/snmp_exporter  
- Ceph Prometheus Module: https://docs.ceph.com/en/latest/mgr/prometheus  

### 🌐 **Ecosystem**
- Grafana: https://grafana.com  
- Alertmanager: https://prometheus.io/docs/alerting/latest/alertmanager  

---

## 🚀 **Next Steps**

- Configure Grafana dashboards for each major service  
- Add alerting rules for disk health, container failures, and cluster issues  
- Document per‑service monitoring pages (Proxmox, Ceph, Docker, Reverse Proxy, etc.)  
- Add a homelab‑wide metrics architecture diagram