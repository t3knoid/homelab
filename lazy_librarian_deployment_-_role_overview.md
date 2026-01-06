---
title: "Lazy Librarian Deployment - Role Overview"
---

# Lazy Librarian Deployment - Role Overview

This page documents the **Lazy Librarian Docker deployment using Ansible**, illustrating the workflow, architecture, and best practices for deploying this containerized application with version control, persistent storage, and templated configuration.

---

## **1. Overview**

Lazy Librarian is deployed in a Docker container using Ansible. Key steps include:

* **Stop existing container** safely
* **Prepare persistent configuration and backup directories**
* **Deploy templated Docker Compose file**
* **Version control the Docker image** to prevent accidental upgrades
* **Start the container**

Lazy Librarian manages its own internal configuration and does **not require an external database**, simplifying deployment while maintaining persistent storage for e-books, download history, and settings.

---

## **2. Persistent Configuration and Backups**

Persistent storage ensures application data is preserved across container restarts:

* Configuration directory: `/config/lazylibrarian`
* Backup directory: `/nfs/backups/lazy`

Example variables from the role:

{% raw %}
```yaml
lazylibrarian_setup_config_dir: "/config/lazylibrarian"
lazylibrarian_setup_backups_dir: "{{ lazylibrarian_setup_mount_point }}/lazy"
lazylibrarian_setup_backup_filename: "{{ lazylibrarian_setup_backup_prefix }}{{ ansible_date_time.date }}.sqlc"
```
{% endraw %}

* Directories are **created and owned** by a dedicated system user
* Supports NFS-mounted storage for centralized backups
* Ensures container can read/write configuration, ebook libraries, and backup files

---

## **3. Docker Image Version Control**

The role pins a specific Docker image version:

{% raw %}
```yaml
lazylibrarian_setup_version: 0c862d0f
lazylibrarian_setup_docker_image_name: "lazylibrarian:version-{{ lazylibrarian_setup_version }}"
```
{% endraw %}

* Avoids pulling `latest` automatically
* Guarantees reproducible deployments
* Allows testing and validation of known working versions

---

## **4. Deployment Workflow**

The sequence for deploying Lazy Librarian is:

1. **Stop and remove existing container**

{% raw %}
```bash
docker stop lazylibrarian
docker rm lazylibrarian
docker network prune -f
```
{% endraw %}

2. **Ensure persistent directories exist**

{% raw %}
```bash
mkdir -p {{ lazylibrarian_setup_config_dir }}
mkdir -p {{ lazylibrarian_setup_backups_dir }}
chown <user>:<group> {{ lazylibrarian_setup_config_dir }}
```
{% endraw %}

3. **Deploy Docker Compose file**

* `docker-compose.yml` (templated in the role)

4. **Prune unused Docker images** (optional)

{% raw %}
```bash
docker image prune -f
```
{% endraw %}

5. **Pull the pinned Docker image**

{% raw %}
```bash
docker-compose -f {{ lazylibrarian_setup_config_dir }}/docker-compose.yml pull
```
{% endraw %}

6. **Start the container**

{% raw %}
```bash
docker-compose -f {{ lazylibrarian_setup_config_dir }}/docker-compose.yml up -d
```
{% endraw %}

---

## **5. Architecture Diagram**

{% raw %}
```
                 ┌──────────────────────────────┐
                 │  Host / Docker Environment   │
                 │                              │
                 │ ┌──────────────────────────┐ │
                 │ │ Lazy Librarian Container │ │
                 │ │ - Pinned Image           │ │
                 │ │ - Config & Backup Volumes│ │
                 │ │ - Exposed Port 5299      │ │
                 │ └──────────────────────────┘ │
                 │                              │
                 └────────────────▲─────────────┘
                                 │ Access
                 ┌───────────────┴─────────────┐
                 │ Users / Clients             │
                 │ Web Browser / API           │
                 └─────────────────────────────┘
```
{% endraw %}

* Config directory is mounted inside the container
* Backups can reside on NFS for centralized storage
* Container manages its own internal data for ebooks and download management

---

## **6. Key Features**

* Automated deployment via **Ansible**
* Persistent configuration and backup support
* Pinned Docker image version for reproducibility
* Optional NFS storage for backups
* Template-driven Docker Compose for flexible setup
* No external database dependencies, self-contained configuration

---

## **7. Summary**

The Lazy Librarian deployment role demonstrates a **simple, containerized workflow**:

* Safe, repeatable container start/stop sequences
* Version-controlled Docker images to prevent accidental updates
* Persistent storage and automated backups for configuration and ebook libraries
* Template-driven Docker Compose to allow scalable and consistent deployments

> This workflow can be adapted for other containerized applications in the home lab, ensuring maintainability, reliability, and consistent infrastructure-as-code practices.
---


## **8. Related Pages**

* [Calibre Deployment (Docker) - Role Overview](calibre_deployment_(docker)_-_role_overview.md)
* [Calibre-Web Deployment (Docker) - Role Overview](calibre-web_deployment_(docker)_-_role_overview.md)
* [Docker Command Cheat Sheet](docker_command_cheat_sheet.md)
* [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md)
* [Lidarr Deployment (Docker) - Role Overview](lidarr_deployment_(docker)_-_role_overview.md)
* [Radarr Deployment (Docker) - Role Overview](radarr_deployment_(docker)_-_role_overview.md)
* [SABnzbd Deployment (Docker) - Role Overview](sabnzbd_deployment_(docker)_-_role_overview.md)
* [Sonarr Deployment (Docker) - Role Overview](sonarr_deployment_(docker)_-_role_overview.md)

