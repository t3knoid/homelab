---
title: "Radarr"
---

# 🎬 Radarr

Radarr is a movie library manager and automation service, similar to [Sonarr](sonarr.md) for TV or [Lidarr](lidarr.md) for music. It tracks movies, uses metadata to organize the library, and watches configured indexers for releases of wanted and missing movies. When it finds a match, it sends the download to a configured download client and imports the completed files into the movie library.

Radarr manages and organizes movies; it is not a media player or streaming service.

## 🐳 Deployment

In this homelab, Radarr runs in a LinuxServer [Docker](docker.md) container on the `radarr-0` VM.

## 💾 Storage & Library

Its library is stored on the [TrueNAS](truenas.md) and mounted at `/movies`. Completed and incomplete downloads are also mounted from the NAS for the download and import workflow.

The configured root folder is `/movies`.

## 📥 Download Client & Indexers

Radarr uses [SABnzbd](sabnzbd.md) as its download client and two Newznab-compatible Usenet indexers for RSS, automatic, and interactive searches.

## 🗄️ Database & Backups

Its application database is hosted on the homelab PostgreSQL server, and scheduled database backups are written to NAS storage. The database backup is one of the [Semaphore Scheduled Tasks](semaphore_scheduled_tasks.md) that run regularly.

The database is restored using the following playbook:

{% raw %}
```
ansible-playbook -k -i inventory/services/inventory.ini playbooks/services/restore_radarr_db.yml \
  -e radarr_setup_restore_path=/nfs/backups/radarr/radarr_<timestamp>.sqlc
```
{% endraw %}

The playbook stops the Radarr container, drops and recreates its PostgreSQL database, restores the selected backup with pg_restore, then starts Radarr again. This replaces the current Radarr database, so verify the selected backup before restoring.

## 🌐 Web Access & Authentication

The web interface is available at https://radarr.refol.us through the homelab reverse proxy, with [Microsoft Entra ID](microsoft_entra_id.md) authentication configured.

## 🤖 Automation

Deployment and configuration are managed through [Ansible](ansible.md).

👉 See: [Deploy Radarr Runbook](deploy_radarr_runbook.md)
