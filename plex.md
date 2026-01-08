---
title: "Plex"
---

# 🎬 Plex

Plex is a media server platform that organizes video, music, and photo libraries and streams them to client devices. It provides user management, metadata enrichment, transcoding, and remote streaming capabilities.

**Category:**
Media Service

---

## 🧩 Platform Dependencies

* **Compute / Virtualization:** Bare-metal [Beelink S12 Pro Mini PC](beelink_s12_pro_mini_pc.md) (Intel 12th Gen Alder Lake‑N100, 16GB RAM, 500GB PCIe SSD)
  * [Supports Intel QuickSync hardware transcoding](https://support.plex.tv/articles/115002178853-using-hardware-accelerated-streaming/) for efficient video streaming 
* **Storage:** [NFS](nfs.md) shares hosted by [TrueNAS](truenas.md), mounted via [Autofs](autofs.md) under `/nfs/{{mount_point}}`
* **Networking:** [Reverse-Proxy](reverse-proxy.md) for external access, ports 32400 TCP/UDP
* **Host Authentication:** SSH and system login via [LDAP](ldap.md) / [Microsoft Active Directory](microsoft_active_directory.md)
* **Application Authentication:** Standard Plex authentication via Plex accounts
* **Monitoring / Observability:** [Prometheus](prometheus.md) exporter, [Grafana](grafana.md) dashboards for CPU, RAM, disk I/O, and media transcoding metrics

---

## ⚙️ Installation & Deployment

Plex is installed via an **Ansible playbook**:

{% raw %}
```bash
ansible-playbook -k -i inventory/plex/inventory.ini playbooks/plex/deploy_plex.yml
```
{% endraw %}

**Key tasks:**

* Wait for Plex host to come online (`wait_for_connection`)
* Download Plex Media Server package from official source
* Install `.deb` package via `apt`
* Ensure Plex service is started and enabled (`plexmediaserver`)

**Roles included in deployment:**

* `global`, `ad`, `autofs`, `python3`, `users`, `ansible_node`, `plex_setup`

**Notes:**

* Automates standard Plex installation
* Host-level accounts authenticated via [LDAP](ldap.md) / [Microsoft Active Directory](microsoft_active_directory.md)
* Plex itself uses its standard Plex authentication
* Follows same OS configuration as all other Ubuntu 24.04 hosts on the network

---

## 🔐 Access & Authentication

* **Host Access:** SSH and system login via [LDAP](ldap.md) / [Microsoft Active Directory](microsoft_active_directory.md)
* **Plex Application:** Standard Plex accounts for media access and admin control

---

## 💾 Storage & Data Management

* Media libraries mounted via [Autofs](autofs.md) from NFS shares on [TrueNAS](truenas.md)
* Mount points defined in `/etc/auto.nfs` (managed via Ansible):

{% raw %}
```
photos -> /nfs/photos
music -> /nfs/music
books -> /nfs/books
tvshows -> /nfs/tvshows
movies -> /nfs/movies
downloads -> /nfs/downloads/complete
incomplete-downloads -> /nfs/downloads/incomplete
backups -> /nfs/backups_ex
```
{% endraw %}

* Local SSD stores Plex database, metadata, and caching
* Backups performed with `playbooks/plex/backup_plex.yml`

**Backup workflow:**

* Stop Plex service
* Archive Plex data directory into gzipped tarball
* Start Plex service
* Retain only last 7 backups

---

## 📈 Observability

* Prometheus exporter collects CPU, RAM, disk, and Plex transcoding metrics
* [Grafana](grafana.md) dashboards visualize metrics
* Alerts for high CPU load, low storage, or heavy transcoding activity

---

## 📝 Operational Notes

* Restart Plex: `systemctl restart plexmediaserver`
* Update Plex via official repository package
* Logs: `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs`
* Add new media volumes via [Autofs](autofs.md)
* Consider backup/snapshot before major upgrades

---

## 🔗 Related Pages

* [Runbooks](runbooks.md)
* [Tautulli](tautulli.md) (for monitoring Plex usage)

---

## Integrations

* [Tautulli](tautulli.md) for usage tracking
* [Radarr](radarr.md), [Sonarr](sonarr.md), [Lidarr](lidarr.md) for automated media acquisition
* [Ombi](ombi.md) for user media requests

## Performance Notes

* CPU supports 2–3 simultaneous transcodes; direct play recommended for multiple clients
* Monitor CPU, RAM, and I/O with [Prometheus](prometheus.md) / [Grafana](grafana.md)