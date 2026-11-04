---
title: "SABnzbd"
---

# 📥 SABnzbd

SABnzbd is a Usenet download client. It accepts NZB download jobs from applications such as [Sonarr](sonarr.md), [Radarr](radarr.md), and [Lidarr](lidarr.md), retrieves the requested files from Usenet, and processes them before making the completed files available to those applications. SABnzbd handles downloading and post-processing; it does not search for releases itself or act as a media player.

## 🐳 Deployment

SABnzbd runs in a LinuxServer [Docker](docker.md) container on the `sabnzbd-0` VM.

## 💾 Storage & Downloads

SABnzbd uses NAS-backed folders for downloads. Incomplete downloads are mounted at `/incomplete-downloads`, and completed downloads are mounted at `/downloads`. The media applications use the shared completed-download location to import files into their libraries.

The container also has NAS-backed media folders mounted for music, books, TV, and movies.

## 📡 Usenet & Integrations

SABnzbd is configured as the shared download client for the homelab’s media automation services. It is configured to connect to Easynews, NewsDemon, and Giganews using encrypted connections. The media applications submit download jobs to SABnzbd with service-specific categories.

## 🗄️ Configuration & Backups

SABnzbd’s application configuration is stored in `/config`. It does not use a separate PostgreSQL database or a database restore playbook.

SABnzbd’s built-in backup directory is `/backups`, mounted from NAS storage at `/mnt/Data/backups_ex/sabnzbd`. Its configuration includes a scheduled `create_backup` task.

## 🌐 Web Access & Authentication

The web interface is available at https://sabnzbd.refol.us through the homelab reverse proxy, with [Microsoft Entra ID](microsoft_entra_id.md) authentication configured.

## 🤖 Automation

Deployment and configuration are managed through [Ansible](ansible.md).

👉 See: [Deploy SABnzbd Runbook](deploy_sabnzbd_runbook.md)