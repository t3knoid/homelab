---
title: "Alerting"
---

# 🚨 **Alerting**

Alerting provides early warnings when something in the homelab requires attention — disk failures, container crashes, service outages, storage issues, or unusual resource usage. Alerts are generated from metrics collected by **[Prometheus](prometheus.md)** and evaluated through **[Grafana](grafana.md)**’s Unified Alerting system (with optional integration to Prometheus Alertmanager).

This page serves as the central reference for alerting strategy, alert definitions, and notification routing.

---

## 🧭 **Overview**

The alerting pipeline follows the same observability flow:

{% raw %}
```
Services → Exporters → Prometheus → Grafana → Notifications
```
{% endraw %}

- **Prometheus** evaluates alert rules based on metric thresholds or conditions  
- **Grafana** handles alerting logic, grouping, silencing, and routing  
- **Notification channels** deliver alerts to your preferred destinations  

Both Prometheus and Grafana are deployed and configured using **[Ansible](ansible.md)**, ensuring alert rules remain version‑controlled and reproducible.

---

## 📌 **Alerting Philosophy**

The goal of alerting in the homelab is:

- Notify only when action is required  
- Avoid noisy or low‑value alerts  
- Focus on service health, data integrity, and cluster stability  
- Keep alert definitions simple, modular, and easy to maintain  

This page will grow as you define which conditions matter most for your environment.

---

## 📐 **Alert Template**

Use this template for each alert to be added. It keeps documentation consistent and makes it easy for contributors to understand what each alert does.

{% raw %}
``` text
# **Alert Name**
A short, descriptive name (e.g., *Proxmox Node Down*, *Ceph OSD Failure*, *Plex Transcode Saturation*).

## **Purpose**
Why this alert exists and what problem it detects.

## **Trigger Condition**
Describe the metric and threshold that triggers the alert.

Example:
- `node_exporter` reports CPU > 90% for 5 minutes  
- Ceph OSD marked `down`  
- Nginx 5xx error rate exceeds 2%  

## **Severity**
- `info` — useful but not urgent  
- `warning` — needs attention soon  
- `critical` — immediate action required  

## **PromQL Expression**
Add the PromQL rule once defined.

```
{% endraw %}# PromQL goes here```

## **Recommended Response**
What to check, where to look, and typical remediation steps.

## **Notes**
Any additional context, links to dashboards, or troubleshooting pages.

```

---

## 🧱 **Planned Alert Categories**

### **Compute (Proxmox / VMs)**
- Node down  
- High CPU or memory usage  
- VM unresponsive  
- SMART disk failures  

### **Storage (Ceph / Synology / TrueNAS)**
- Ceph OSD down  
- Ceph cluster in `HEALTH_WARN` or `HEALTH_ERR`  
- ZFS pool degradation  
- RAID rebuild or failure  

### **Applications (Docker Media Stack / Plex)**
- Container down  
- Plex transcode saturation  
- Radarr/Sonarr queue stuck  

### **Networking**
- Pi‑hole DNS failure  
- High DNS latency  
- Switch or AP unreachable (SNMP)  

### **Reverse Proxy**
- Nginx 5xx error spikes  
- Backend service unreachable  


