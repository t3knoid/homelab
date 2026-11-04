---
title: "Sonarr"
---

# 📺 Sonarr

Sonarr is a TV library manager and automation service, similar to [Radarr](radarr.md) for movies or [Lidarr](lidarr.md) for music. It tracks series and episodes, uses metadata to organize the library, and watches configured indexers for new and missing episodes. When it finds a match, it sends the download to a configured download client and imports the completed files into the TV library.

Sonarr manages and organizes TV shows; it is not a media player or streaming service.

## 🐳 Deployment

In this homelab, Sonarr runs in a LinuxServer [Docker](docker.md) container on the `sonarr-0` VM.

## 💾 Storage & Library

Its library is stored on the [TrueNAS](truenas.md) and mounted at `/tv`. Completed and incomplete downloads are also mounted from the NAS for the download and import workflow.

The configured root folder is `/tv`.

## 📥 Download Client & Indexers

Sonarr uses [SABnzbd](sabnzbd.md) as its download client and two Newznab-compatible Usenet indexers for RSS, automatic, and interactive searches.

## 🗄️ Database & Backups

Its application database is hosted on the homelab PostgreSQL server, and scheduled database backups are written to NAS storage. The database backup is one of the [Semaphore Scheduled Tasks](semaphore_scheduled_tasks.md) that run regularly.

The database is restored using the following playbook:

{% raw %}
```
ansible-playbook -k -i inventory/services/inventory.ini playbooks/services/restore_sonarr_db.yml \
  -e sonarr_setup_restore_path=/nfs/backups/sonarr/sonarr_<timestamp>.sqlc
```
{% endraw %}

The playbook stops the Sonarr container, drops and recreates its PostgreSQL database, restores the selected backup with pg_restore, then starts Sonarr again. This replaces the current Sonarr database, so verify the selected backup before restoring.

## 🌐 Web Access & Authentication

The web interface is available at https://sonarr.refol.us through the homelab reverse proxy, with [Microsoft Entra ID](microsoft_entra_id.md) authentication configured.

## 🤖 Automation

Deployment and configuration are managed through [Ansible](ansible.md).

👉 See: [Deploy Sonarr Runbook](deploy_sonarr_runbook.md)