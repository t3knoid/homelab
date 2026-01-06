---
title: "Sonarr Deployment - Role Overview"
---

# Sonarr Deployment - Role Overview

This page documents the **Sonarr Docker deployment using Ansible**, illustrating the workflow, architecture, and best practices for deploying this containerized application with version control, persistent storage, and integration with an external PostgreSQL database.

---

## **1. Overview**

Sonarr is deployed in a Docker container using Ansible. Key steps include:

* **Stop existing container** safely
* **Prepare persistent configuration and backup directories**
* **Deploy templated Docker Compose and application configuration files**
* **Version control the Docker image** to prevent accidental upgrades
* **Start the container**

Additionally, Sonarr connects to an **external PostgreSQL database**, separating storage from the application for improved reliability and scalability.

---

## **2. Persistent Configuration and Backups**

Persistent storage ensures application data is preserved across container restarts:

* Configuration directory: `/config`
* Backup directory: `/nfs/backups/sonarr`

Example variables from the role:

{% raw %}
```yaml
sonarr_setup_config_dir: "/config"
sonarr_setup_backups_dir: "/nfs/backups/sonarr"
sonarr_setup_backup_filename: "{{ sonarr_setup_backup_prefix }}{{ ansible_date_time.date }}.sqlc"
```
{% endraw %}

* Directories are **created and owned** by a dedicated system user
* Supports NFS-mounted storage for centralized backups
* Ensures container can read/write configs and backup files

---

## **3. Docker Image Version Control**

The role pins a specific Docker image version:

{% raw %}
```yaml
sonarr_setup_version: 4.0.15.2941
sonarr_setup_docker_image_name: "sonarr:{{ sonarr_setup_version }}"
```
{% endraw %}

* Avoids pulling `latest` automatically
* Guarantees reproducible deployments
* Allows testing and validation of known working versions

---

## **4. Deployment Workflow**

The sequence for deploying Sonarr is:

1. **Stop and remove existing container**

{% raw %}
```bash
docker stop sonarr
docker rm sonarr
docker network prune -f
```
{% endraw %}

2. **Ensure persistent directories exist**

{% raw %}
```bash
mkdir -p {{ sonarr_setup_config_dir }}
mkdir -p {{ sonarr_setup_backups_dir }}
chown <user>:<group> {{ sonarr_setup_config_dir }}
```
{% endraw %}

3. **Deploy configuration files and Docker Compose**

* `docker-compose.yml`
* `config.xml` (application-specific configuration)

4. **Prune unused Docker images** (optional)

{% raw %}
```bash
docker image prune -f
```
{% endraw %}

5. **Pull the pinned Docker image**

{% raw %}
```bash
docker-compose -f {{ sonarr_setup_config_dir }}/docker-compose.yml pull
```
{% endraw %}

6. **Start the container**

{% raw %}
```bash
docker-compose -f {{ sonarr_setup_config_dir }}/docker-compose.yml up -d
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
                 │ │ Sonarr Container         │ │
                 │ │ - Pinned Image           │ │
                 │ │ - Config & Backup Volumes│ │
                 │ │ - Exposed Ports 8989/9898│ │
                 │ └──────────────────────────┘ │
                 │                              │
                 └────────────────▲─────────────┘
                                 │ Access
                 ┌───────────────┴─────────────┐
                 │ Users / Clients             │
                 │ Web Browser / API           │
                 └───────────────▲─────────────┘
                                 │ Database Connection
                 ┌───────────────┴─────────────┐
                 │ External PostgreSQL Server  │
                 │ - Database: sonarr-main     │
                 │ - User: sonarr              │
                 │ - Port: 5432                │
                 └─────────────────────────────┘
```
{% endraw %}

* Config directory is mounted inside the container
* Backups can reside on NFS for centralized storage
* Container connects to **external PostgreSQL** for data persistence

---

## **6. Key Features**

* Automated deployment via **Ansible**
* Persistent configuration and backups
* Pinned Docker image version for reproducibility
* Optional NFS storage for backups
* Integration with **external PostgreSQL** for database separation
* Reusable workflow applicable to other home lab containerized apps

---

## **7. Summary**

The Sonarr deployment role demonstrates a **robust, production-like container workflow**:

* Safe, repeatable container start/stop sequences
* Version-controlled Docker images to prevent accidental updates
* Persistent storage and automated backups for configuration and data
* Separation of application and database layers using PostgreSQL
* Template-driven configuration to allow scalable and consistent deployments

> This workflow can be adapted for other containerized applications in the home lab, ensuring maintainability, reliability, and consistent infrastructure-as-code practices.

---

## **8. Related Pages**

* [Calibre Deployment (Docker) - Role Overview](calibre_deployment_(docker)_-_role_overview.md)
* [Calibre-Web Deployment (Docker) - Role Overview](calibre-web_deployment_(docker)_-_role_overview.md)
* [Docker Command Cheat Sheet](docker_command_cheat_sheet.md)
* [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md)
* [LazyLibrarian Deployment (Docker) - Role Overview](lazylibrarian_deployment_(docker)_-_role_overview.md)
* [Lidarr Deployment (Docker) - Role Overview](lidarr_deployment_(docker)_-_role_overview.md)
* [Radarr Deployment (Docker) - Role Overview](radarr_deployment_(docker)_-_role_overview.md)
* [SABnzbd Deployment (Docker) - Role Overview](sabnzbd_deployment_(docker)_-_role_overview.md)
