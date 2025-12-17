---
title: "Docker Deployment (Calibre-Web) - Role Overview"
---

# Docker Deployment (Calibre-Web) - Role Overview

This page documents the **Calibre-Web Docker deployment using Ansible**, illustrating the workflow, architecture, and best practices for deploying this containerized application with version control, persistent storage, and optional network-mounted backups.

---

## **1. Overview**

Calibre-Web is deployed in a Docker container using Ansible. The workflow is consistent with other containerized applications in the lab:

* **Stop existing container** safely
* **Prepare persistent configuration and backup directories**
* **Deploy templated Docker Compose files** using Ansible
* **Pin the Docker image version** to ensure reproducibility
* **Start the container**

This ensures predictable deployments, persistent storage, and automated provisioning.

---

## **2. Persistent Configuration and Backups**

A host directory is mounted inside the container to hold:

* Application configuration files (`/config/calibreweb`)
* Backup files (`/nfs/backups/calibre`)

Example variables from the role:

{% raw %}
```yaml
calibreweb_setup_config_dir: "/config/calibreweb"
calibreweb_setup_backups_dir: "/nfs/backups/calibre"
calibreweb_setup_backup_filename: "{{ calibreweb_setup_backup_prefix }}{{ ansible_date_time.date }}.sqlc"
```
{% endraw %}

* Directories are **created and owned** by a dedicated system user
* Ensures the container can read/write configuration and backup files
* Supports network-mounted storage for centralizing backups

---

## **3. Docker Image Version Control**

The deployment uses a **specific Docker image version**, avoiding automatic `latest` pulls:

{% raw %}
```yaml
calibreweb_setup_version: 0.6.25
calibreweb_setup_docker_image_name: "calibre-web:{{ calibreweb_setup_version }}"
```
{% endraw %}

> This ensures reproducible deployments and prevents unexpected changes from upstream image updates.

---

## **4. Deployment Workflow**

The sequence for deploying Calibre-Web is:

1. **Stop and remove existing container**

   ```bash
   docker stop calibreweb
   docker rm calibreweb
   docker network prune -f
   ```

2. **Ensure persistent directories exist**

   ```bash
   mkdir -p {{ calibreweb_setup_config_dir }}
   mkdir -p {{ calibreweb_setup_backups_dir }}
   chown <user>:<group> {{ calibreweb_setup_config_dir }}
   ```

3. **Copy templated Docker Compose file**

   ```yaml
   docker-compose.yml
   ```

4. **Prune unused images** (optional)

   ```bash
   docker image prune -f
   ```

5. **Start the container**

   ```bash
   docker-compose -f {{ calibreweb_setup_config_dir }}/docker-compose.yml up -d
   ```

---

## **5. Architecture Diagram**

{% raw %}
```
           ┌───────────────────────────┐
           │ Host / Docker Environment │
           │                           │
           │ ┌──────────────────────┐  │
           │ │ Calibre-Web Container│  │
           │ │ - Pinned Image       │  │
           │ │ - Config & Backup    │  │
           │ │ - Exposed Port 8083  │  │
           │ └──────────────────────┘  │
           │                           │
           └─────────────▲─────────────┘
                         │ Access
           ┌─────────────┴─────────────┐
           │ Users / Clients           │
           │ Web Browser / API         │
           └───────────────────────────┘
```
{% endraw %}

* Config directory is mounted as `/config`
* Backup folder can optionally reside on NFS for centralized storage
* The container exposes **port 8083** for web access

---

## **6. Key Features**

* Fully automated deployment via **Ansible**
* Persistent configuration and backups
* **Version-controlled Docker image**
* Easy integration with other home lab services
* Reusable workflow applicable to other containerized applications

---

## **7. Best Practices**

* **Pin Docker image versions** for reproducibility
* **Mount host directories** for configuration and backup persistence
* **Prune unused Docker images** periodically to conserve disk space
* **Use templated Docker Compose files** for consistency
* **Automate deployment** using Ansible for repeatability

---

## **8. Summary**

This role demonstrates a **robust approach to deploying Calibre-Web using Docker and Ansible**, ensuring:

* Predictable, reproducible deployments
* Persistent storage for configs and backups
* Minimal manual intervention
* A workflow easily adaptable for other home lab applications

> The workflow mirrors the general Docker deployment strategy used in other roles, making it a cornerstone of home lab container management.

## **9. Related Pages**

* [Calibre Deployment (Docker) - Role Overview](calibre_deployment_(docker)_-_role_overview.md)
* [Docker Command Cheat Sheet](docker_command_cheat_sheet.md)
* [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md)
* [LazyLibrarian Deployment (Docker) - Role Overview](lazylibrarian_deployment_(docker)_-_role_overview.md)
* [Lidarr Deployment (Docker) - Role Overview](lidarr_deployment_(docker)_-_role_overview.md)
* [Radarr Deployment (Docker) - Role Overview](radarr_deployment_(docker)_-_role_overview.md)
* [SABnzbd Deployment (Docker) - Role Overview](sabnzbd_deployment_(docker)_-_role_overview.md)
* [Sonarr Deployment (Docker) - Role Overview](sonarr_deployment_(docker)_-_role_overview.md)
