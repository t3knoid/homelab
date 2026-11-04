---
title: "Lidarr"
---

# 🎵 Lidarr

Lidarr is a music library manager and automation service, similar to [Sonarr](sonarr.md) for TV or [Radarr](radarr.md) for movies. It tracks artists and albums, uses metadata to organize the library, and can search configured indexers for releases. When it finds a match, it sends the download to a configured download client and imports the completed files into the music library.

Lidarr manages and organizes music; it is not a music player or streaming service.

## 🐳 Deployment

In this homelab, Lidarr runs in a LinuxServer [Docker](docker.md) container on the `lidarr-0` VM.

## 💾 Storage & Library

Its library is stored on the [TrueNAS](truenas.md) and mounted at `/music`; completed and incomplete downloads are also NAS-mounted for the download and import workflow.

The configured root folder is `/music`, with a Lossless quality profile.

## 📥 Download Client & Indexers

Lidarr is configured to use [SABnzbd](sabnzbd.md) as its download client and two Newznab-compatible Usenet indexers for RSS, automatic, and interactive searches.


## 🗄️ Database & Backups

Its application database is hosted on the homelab PostgreSQL server, with scheduled database backups written to NAS storage. The database backup is part of [Semaphore Scheduled Tasks](semaphore_scheduled_tasks.md) that are executed regularly.

The database is restored using the following playbook:

{% raw %}
```
ansible-playbook -k -i inventory/services/inventory.ini playbooks/services/restore_lidarr_db.yml \
  -e lidarr_setup_restore_path=/nfs/backups/lidarr/lidarr_<timestamp>.sqlc
```
{% endraw %}

The playbook stops the Lidarr container, drops and recreates its PostgreSQL database, restores the selected backup with pg_restore, then starts Lidarr again. This replaces the current Lidarr database, so verify the selected backup before restoring.

## 🌐 Web Access & Authentication

The web interface is available through https://lidarr.refol.us via the homelab reverse proxy, with [Microsoft Entra ID](microsoft_entra_id.md) authentication configured.

## 🤖 Automation

Deployment and configuration are managed through [Ansible](ansible.md). 

👉 See: [Deploy Lidarr Runbook](deploy_lidarr_runbook.md)