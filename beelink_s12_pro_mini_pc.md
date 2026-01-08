---
title: "️ Beelink S12 Pro Mini PC"
---

# 🖥️ Beelink S12 Pro Mini PC

The *Beelink S12 Pro* is a compact mini PC that serves as a dedicated hardware host in the homelab. Its small form factor, modern CPU with hardware transcoding support, and solid connectivity make it ideal for always‑on media workloads.

**Purchase Link:**
[https://www.amazon.com/Beelink-Pro-Desktop-Computer-1000Mbps/dp/B0G62PNXZB](https://www.amazon.com/Beelink-Pro-Desktop-Computer-1000Mbps/dp/B0G62PNXZB)

---

## 📦 Overview

The Beelink S12 Pro is a turnkey mini desktop computer designed for space-constrained environments requiring reliable performance. In the homelab, it functions as a **bare-metal Plex Media Server**.

For Plex-specific deployment, configuration, and operational details, 
👉 see the [Plex](plex.md) page.

---

## 🧠 Hardware Specifications

| Component     | Specification                                  |
| ------------- | ---------------------------------------------- |
| Model         | Beelink S12 Pro Mini PC                        |
| CPU           | Intel 12th Gen Alder Lake‑N100 (Up to 3.4 GHz) |
| Cores/Threads | 4 / 4                                          |
| RAM           | 16 GB DDR4                                     |
| Storage       | 500 GB PCIe SSD                                |
| Graphics      | Integrated Intel UHD Graphics with QuickSync   |
| Networking    | 1× Gigabit Ethernet, Wi‑Fi 6                   |
| USB           | Multiple USB‑A & USB‑C ports                   |
| Display       | HDMI / DisplayPort capable                     |
| Form Factor   | Mini PC (small desktop)                        |

---

## 🏷️ Key Features

### 🔧 Performance

* Intel 12th Gen Alder Lake‑N100 — efficient, low-power CPU capable of media workloads
* 16 GB DDR4 RAM — sufficient for Plex and other lightweight services
* 500 GB PCIe SSD — fast local storage for system and cache

### 🎥 Media Acceleration

* **Intel QuickSync support** — enables hardware-accelerated video transcoding for Plex and other media applications

### 🌐 Connectivity

* Gigabit Ethernet for reliable streaming
* Wi‑Fi 6 for optional wireless connectivity
* Multiple USB ports for expansion (external drives, peripherals)

### 📏 Compact Design

* Small footprint suitable for rack shelf, media cabinet, or desktop
* Quiet operation for home environments

---

## 🛠 Integration in the Homelab

* Hosts **[Plex](plex.md)** for media streaming (see Plex page for details)
* NFS shares mounted via [Autofs](autofs.md) from [TrueNAS](truenas.md)
* SSH/system login authenticated via [LDAP](ldap.md) / [Microsoft Active Directory](microsoft_active_directory.md)
* Fully monitored through [Prometheus](prometheus.md) and [Grafana](grafana.md) dashboards

---

## ⚙️ Notes & Best Practices

* Keep system and firmware updated regularly
* Monitor hardware metrics during peak media usage
* Leverage Intel QuickSync for efficient transcoding
* Minimize CPU-intensive workloads outside Plex to maintain streaming performance

---

## 🔗 Related Pages

* [Plex](plex.md) – Plex Media Server deployment and usage
* [Autofs](autofs.md) – NFS mount automation
* [Prometheus](prometheus.md) / [Grafana](grafana.md) – Monitoring stack
* [Ansible](ansible.md) – Deployment automation