---
title: "️ Homelab-Wide Metrics Architecture"
---

# 🛰️ Homelab-Wide Metrics Architecture

The homelab uses a unified observability stack built around **[Prometheus](prometheus.md)** and **[Grafana](grafana.md)**. This architecture collects metrics from compute, storage, networking, and application services, providing a consistent, scalable foundation for monitoring, alerting, and long‑term analysis.

This page documents the full metrics architecture, including the data flow, exporters, and the role of each layer in the system.

---

## 🗺️ Architecture Overview

At a high level, the monitoring pipeline follows this flow:

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

---

## 📊 Homelab‑Wide Metrics Architecture Diagram

{% raw %}
```
                                      +-----------------------+
                                      |       Grafana         |
                                      | Dashboards & Queries  |
                                      +-----------+-----------+
                                                  |
                                                  |
                                          +-------v--------+
                                          |   Prometheus   |
                                          |  Scrape Engine |
                                          +-------+--------+
                                                  |
     ---------------------------------------------------------------------------------------------------------
     |                 |                 |                 |                 |                 |             |
     |                 |                 |                 |                 |                 |             |
+----v-----+     +-----v------+    +-----v------+    +-----v------+    +-----v------+    +-----v------+  +--v-----+
| nginx    |     | node_export|    | docker_exp |    | plex_exp   |    | ceph_exp   |    | snmp_export |  | black- |
| exporter |     |  Proxmox   |    |  Media Apps|    | Plex Media |    | Ceph Mons  |    | switches/AP |  | box_exp|
+----+-----+     +-----+------+    +-----+------+    +-----+------+    +-----+------+    +-----+------+  +--+-----+
     |                 |                 |                 |                 |                 |             |
     |                 |                 |                 |                 |                 |             |
+----v-----+     +-----v------+    +-----v------+    +-----v------+    +-----v------+    +-----v------+  +--v-----+
| Nginx RP |     | Proxmox VE |    | Docker Host|    | Plex Media |    | Ceph OSDs  |    | Network Gear|  | External|
| (OAuth2) |     | Cluster    |    | (Lidarr,   |    | Server     |    | Ceph Mgr   |    | (Switches)  |  | Services|
+----------+     +------------+    | Radarr,    |    +------------+    +------------+    +------------+  +---------+
                                   | Sonarr,    |
                                   | Sabnzbd,   |
                                   | Calibre,   |
                                   | CalibreWeb |
                                   | LazyLib)   |
                                   +------------+

     --------------------------------------------------------------------------------------------------------------------------------
     |                 |                 |                 |                 |                 |                 |                  |
     |                 |                 |                 |                 |                 |                 |                  |
+----v-----+     +-----v------+    +-----v------+    +-----v------+    +-----v------+    +-----v------+    +-----v------+    +----v-----+
| synology |     | truenas    |    | smb/nfs    |    | iscsi      |    | ceph rbd   |    | cephfs     |    | pbs_export |    | pihole_exp|
| exporter |     | exporter   |    | exporter   |    | exporter   |    | exporter   |    | exporter   |    | PBS Backup |    | Pi-hole   |
+----------+     +------------+    +------------+    +------------+    +------------+    +------------+    +------------+    +----------+
     |                 |                 |                 |                 |                 |                 |                  |
+----v-----+     +-----v------+    +-----v------+    +-----v------+    +-----v------+    +-----v------+    +-----v------+    +----v-----+
| Synology |     | TrueNAS    |    | NFS/SMB    |    | iSCSI LUNs |    | Ceph RBD   |    | CephFS     |    | PBS Server |    | Pi-hole  |
| NAS      |     | Core/Scale |    | Shares     |    |            |    | Pools      |    |            |    |            |    | DNS/Ad   |
+----------+     +------------+    +------------+    +------------+    +------------+    +------------+    +------------+    +----------+
```
{% endraw %}

---

## 🧱 Layer‑by‑Layer Breakdown

This section explains each layer of the architecture and the role it plays.

---

### 🧩 1. Reverse Proxy Layer (Nginx + OAuth2 Proxy)

**Monitored components:**

- Nginx reverse proxy  
- OAuth2 Proxy authentication layer  
- Backend service health checks  

**Exporters:**

- `nginx-prometheus-exporter`  
- OAuth2 Proxy’s built‑in metrics  
- `blackbox_exporter` for HTTP checks  

**Services behind the proxy:**

- CalibreWeb  
- LazyLibrarian  
- Radarr / Sonarr / Lidarr  
- Sabnzbd  
- Internal dashboards  
- Admin UIs (Proxmox, TrueNAS, Synology)

---

### 🐳 2. Docker Media Stack Layer

**Applications:**

- Radarr  
- Sonarr  
- Lidarr  
- Sabnzbd  
- Calibre  
- CalibreWeb  
- LazyLibrarian  

**Exporters:**

- `docker_exporter` or `cAdvisor`  
- App‑specific `/metrics` endpoints where available  
- `blackbox_exporter` for apps without native metrics  

---

### 🎬 3. Plex Media Server Layer

**Metrics include:**

- Playback sessions  
- Transcode activity  
- Library scans  
- Resource usage  

**Exporters:**

- `plex-media-server-exporter`  
- Or Tautulli → Prometheus exporter  

---

### 🖥️ 4. Proxmox Cluster Layer

**Metrics include:**

- Node CPU/memory/disk  
- VM resource usage  
- Cluster health  
- Storage pools  
- Ceph integration  

**Exporters:**

- `pve_exporter`  
- `node_exporter`  
- `smartctl_exporter`  
- `ceph_exporter` (if Ceph integrated)

---

### 🗄️ 5. Storage Layer

#### **Ceph**
- OSDs, MONs, MGR  
- RBD pools  
- CephFS  
- Cluster health  

**Exporter:** Ceph MGR Prometheus module

#### **Synology**
- CPU/memory  
- Disk SMART  
- RAID health  
- Shares  

**Exporter:** `synology_exporter`

#### **TrueNAS**
- ZFS pools  
- ARC stats  
- Disk health  
- Shares  

**Exporter:** `truenas_exporter` or ZFS exporter

---

### 🌐 6. Network Layer

**Devices:**

- Switches  
- Routers  
- Access points  

**Exporter:** `snmp_exporter`

---

### 🧩 7. DNS & Network Services Layer

#### **Pi‑hole**
- Query counts  
- Blocked domains  
- Upstream latency  
- Cache hit rate  

**Exporter:** `pihole_exporter`

---

## 📡 Prometheus Scrape Topology

Prometheus scrapes metrics from all exporters using jobs such as:

- `nginx`  
- `proxmox`  
- `docker`  
- `media_apps`  
- `plex`  
- `ceph`  
- `synology`  
- `truenas`  
- `pihole`  
- `network`  
- `blackbox`  

Each job defines targets, labels, and scrape intervals.


