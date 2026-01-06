---
title: "SABnzbd Deployment - Role Overview"
---

# SABnzbd Deployment - Role Overview

This page documents the **SABnzbd Docker deployment using Ansible**, illustrating the workflow, architecture, and best practices for deploying this containerized application with version control, persistent storage, and templated configuration.

---

## **1. Overview**

SABnzbd is deployed in a Docker container using Ansible. Key steps include:

* **Stop existing container** safely
* **Prepare persistent configuration and backup directories**
* **Deploy templated Docker Compose and application configuration files**
* **Version control the Docker image** to prevent accidental upgrades
* **Start the container**

Unlike some other media applications, SABnzbd does **not require an external database**, simplifying deployment while still providing persistent storage for configuration and download management.

---

## **2. Persistent Configuration and Backups**

Persistent storage ensures application data is preserved across container restarts:

* Configuration directory: `/config`
* Backup directory: `/config/sabnzbd` (or `/nfs/backups/sabnzbd`)

Example variables from the role:

{% raw %}
```yaml
sabnzbd_setup_config_dir: "/config"
sabnzbd_setup_backups_dir: "{{ sabnzbd_setup_config_dir }}/sabnzbd"
sabnzbd_setup_backup_filename: "{{ sabnzbd_setup_backup_prefix }}{{ ansible_date_time.date }}.sqlc"
```
{% endraw %}

* Directories are **created and owned** by a dedicated system user
* Supports NFS-mounted storage for centralized backups
* Ensures container can read/write configuration and download management files

---

## **3. Docker Image Version Control**

The role pins a specific Docker image version:

{% raw %}
```yaml
sabnzbd_setup_version: 4.5.3
sabnzbd_setup_docker_image_name: "sabnzbd:{{ sabnzbd_setup_version }}"
```
{% endraw %}

* Avoids pulling `latest` automatically
* Guarantees reproducible deployments
* Allows testing and validation of known working versions

---

## **4. Deployment Workflow**

The sequence for deploying SABnzbd is:

1. **Stop and remove existing container**

{% raw %}
```bash
docker stop sabnzbd
docker rm sabnzbd
docker network prune -f
```
{% endraw %}

2. **Ensure persistent directories exist**

{% raw %}
```bash
mkdir -p {{ sabnzbd_setup_config_dir }}
mkdir -p {{ sabnzbd_setup_backups_dir }}
chown <user>:<group> {{ sabnzbd_setup_config_dir }}
```
{% endraw %}

3. **Deploy configuration files and Docker Compose**

* `docker-compose.yml`
* `sabnzbd.ini` (application-specific configuration)

4. **Prune unused Docker images** (optional)

{% raw %}
```bash
docker image prune -f
```
{% endraw %}

5. **Pull the pinned Docker image**

{% raw %}
```bash
docker-compose -f {{ sabnzbd_setup_config_dir }}/docker-compose.yml pull
```
{% endraw %}

6. **Start the container**

{% raw %}
```bash
docker-compose -f {{ sabnzbd_setup_config_dir }}/docker-compose.yml up -d
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
                 │ │ SABnzbd Container        │ │
                 │ │ - Pinned Image           │ │
                 │ │ - Config & Backup Volumes│ │
                 │ │ - Exposed Port 8080      │ │
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
* Container manages its own internal database (SABnzbd configuration and queue)

---

## **6. Key Features**

* Automated deployment via **Ansible**
* Persistent configuration and backup support
* Pinned Docker image version for reproducibility
* Optional NFS storage for backups
* Templated configuration file for flexible setup
* Simple deployment without external database dependencies

---

## **7. Summary**

The SABnzbd deployment role demonstrates a **straightforward, containerized workflow**:

* Safe, repeatable container start/stop sequences
* Version-controlled Docker images to prevent accidental updates
* Persistent storage and automated backups for configuration and download data
* Template-driven configuration to allow scalable and consistent deployments

> This workflow can be adapted for other containerized applications in the home lab, ensuring maintainability, reliability, and consistent infrastructure-as-code practices.

---

## **8. Related Pages**

* [Docker Command Cheat Sheet](docker_command_cheat_sheet.md)
* [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md)
* [Calibre Deployment - Role Overview](calibre_deployment_-_role_overview.md)
* [Calibre-Web Deployment - Role Overview](calibre-web_deployment_-_role_overview.md)
* [Lazy Librarian Deployment - Role Overview](lazy_librarian_deployment_-_role_overview.md)
* [Lidarr Deployment - Role Overview](lidarr_deployment_-_role_overview.md)
* [Radarr Deployment - Role Overview](radarr_deployment_-_role_overview.md)
* [Sonarr Deployment - Role Overview](sonarr_deployment_-_role_overview.md)