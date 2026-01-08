---
title: "Radarr Deployment - Role Overview"
---

# Radarr Deployment - Role Overview

This page documents the **Radarr Docker deployment using Ansible**, illustrating the workflow, architecture, and best practices for deploying this containerized application with version control, persistent storage, and integration with an external [PostgreSQL](postgresql.md) database.

---

## **1. Overview**

[Radarr](radarr.md) is deployed in a [Docker](docker.md) container using Ansible. Key steps include:

* **Stop existing container** safely
* **Prepare persistent configuration and backup directories**
* **Deploy templated Docker Compose and application configuration files**
* **Version control the Docker image** to prevent accidental upgrades
* **Start the container**

Additionally, Radarr connects to an **external PostgreSQL database**, separating storage from the application for improved reliability and scalability.

---

## **2. Persistent Configuration and Backups**

Persistent storage ensures application data is preserved across container restarts:

* Configuration directory: `/config`
* Backup directory: `/nfs/backups/radarr`

Example variables from the role:

{% raw %}
```yaml
radarr_setup_config_dir: "/config"
radarr_setup_backups_dir: "/nfs/backups/radarr"
radarr_setup_backup_filename: "{{ radarr_setup_backup_prefix }}{{ ansible_date_time.date }}.sqlc"
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
radarr_setup_version: "5.27.5.10198"
radarr_setup_docker_image_name: "radarr:{{ radarr_setup_version }}"
```
{% endraw %}

* Avoids pulling `latest` automatically
* Guarantees reproducible deployments
* Allows testing and validation of known working versions

---

## **4. Deployment Workflow**

The sequence for deploying Radarr is:

1. **Stop and remove existing container**

   ```bash
   docker stop radarr
   docker rm radarr
   docker network prune -f
   ```

2. **Ensure persistent directories exist**

   ```bash
   mkdir -p {{ radarr_setup_config_dir }}
   mkdir -p {{ radarr_setup_backups_dir }}
   chown <user>:<group> {{ radarr_setup_config_dir }}
   ```

3. **Deploy configuration files and Docker Compose**

   * `docker-compose.yml`
   * `config.xml` (application-specific configuration)

4. **Prune unused Docker images** (optional)

   ```bash
   docker image prune -f
   ```

5. **Pull the pinned Docker image**

   ```bash
   docker-compose -f {{ radarr_setup_config_dir }}/docker-compose.yml pull
   ```

6. **Start the container**

   ```bash
   docker-compose -f {{ radarr_setup_config_dir }}/docker-compose.yml up -d
   ```

---

## **5. Architecture Diagram**

{% raw %}
```
                 ┌──────────────────────────────┐
                 │  Host / Docker Environment   │
                 │                              │
                 │ ┌──────────────────────────┐ │
                 │ │ Radarr Container         │ │
                 │ │ - Pinned Image           │ │
                 │ │ - Config & Backup Volumes│ │
                 │ │ - Exposed Ports 7878/8787│ │
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
                 │ - Database: radarr-main     │
                 │ - User: radarr              │
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

The Radarr deployment role demonstrates a **robust, production-like container workflow**:

* Safe, repeatable container start/stop sequences
* Version-controlled Docker images to prevent accidental updates
* Persistent storage and automated backups for configuration and data
* Separation of application and database layers using PostgreSQL
* Template-driven configuration to allow scalable and consistent deployments

> This workflow can be adapted for other containerized applications in the home lab, ensuring maintainability, reliability, and consistent infrastructure-as-code practices.

## **8. Related Pages**

* [Docker Command Cheat Sheet](docker_command_cheat_sheet.md)
* [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md)
* [Calibre Deployment - Role Overview](calibre_deployment_-_role_overview.md)
* [Calibre-Web Deployment - Role Overview](calibre-web_deployment_-_role_overview.md)
* [Lazy Librarian Deployment - Role Overview](lazy_librarian_deployment_-_role_overview.md)
* [Lidarr Deployment - Role Overview](lidarr_deployment_-_role_overview.md)
* [SABnzbd Deployment - Role Overview](sabnzbd_deployment_-_role_overview.md)
* [Sonarr Deployment - Role Overview](sonarr_deployment_-_role_overview.md)