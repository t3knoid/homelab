---
title: "Lidarr Deployment (Docker) - Role Overview"
---

# Lidarr Deployment (Docker) - Role Overview

This page documents the **Lidarr Docker deployment using Ansible**, illustrating the workflow, architecture, and best practices for deploying this containerized application with version control, persistent storage, and integration with an external PostgreSQL database.

---

## **1. Overview**

Lidarr is deployed in a Docker container using Ansible. Key steps include:

* **Stop existing container** safely
* **Prepare persistent configuration and backup directories**
* **Deploy templated Docker Compose and application configuration files**
* **Version control the Docker image** to prevent accidental upgrades
* **Start the container**

Additionally, Lidarr connects to an **external PostgreSQL database**, separating storage from the application for improved reliability and scalability.

---

## **2. Persistent Configuration and Backups**

Persistent storage ensures application data is preserved across container restarts:

* Configuration directory: `/config`
* Backup directory: `/nfs/backups/lidarr`

Example variables from the role:

```yaml
lidarr_setup_config_dir: "/config"
lidarr_setup_backups_dir: "/nfs/backups/lidarr"
lidarr_setup_backup_filename: "{{ lidarr_setup_backup_prefix }}{{ ansible_date_time.date }}.sqlc"
```

* Directories are **created and owned** by a dedicated system user
* Supports NFS-mounted storage for centralized backups
* Ensures container can read/write configs and backup files

---

## **3. Docker Image Version Control**

The role pins a specific Docker image version:

```yaml
lidarr_setup_version: 2.13.3.4711
lidarr_setup_docker_image_name: "lidarr:{{ lidarr_setup_version }}"
```

* Avoids pulling `latest` automatically
* Guarantees reproducible deployments
* Allows testing and validation of known working versions

---

## **4. Deployment Workflow**

The sequence for deploying Lidarr is:

1. **Stop and remove existing container**

```bash
docker stop lidarr
docker rm lidarr
docker network prune -f
```

2. **Ensure persistent directories exist**

```bash
mkdir -p {{ lidarr_setup_config_dir }}
mkdir -p {{ lidarr_setup_backups_dir }}
chown <user>:<group> {{ lidarr_setup_config_dir }}
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
docker-compose -f {{ lidarr_setup_config_dir }}/docker-compose.yml pull
```

6. **Start the container**

```bash
docker-compose -f {{ lidarr_setup_config_dir }}/docker-compose.yml up -d
```

---

## **5. Architecture Diagram**

```
                 ┌──────────────────────────────┐
                 │  Host / Docker Environment   │
                 │                              │
                 │ ┌──────────────────────────┐ │
                 │ │ Lidarr Container         │ │
                 │ │ - Pinned Image           │ │
                 │ │ - Config & Backup Volumes│ │
                 │ │ - Exposed Ports 8686/6868│ │
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
                 │ - Database: lidarr-main     │
                 │ - User: lidarr              │
                 │ - Port: 5432                │
                 └─────────────────────────────┘
```

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

The Lidarr deployment role demonstrates a **robust, production-like container workflow**:

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
* [Radarr Deployment (Docker) - Role Overview](radarr_deployment_(docker)_-_role_overview.md)
* [SABnzbd Deployment (Docker) - Role Overview](sabnzbd_deployment_(docker)_-_role_overview.md)
* [Sonarr Deployment (Docker) - Role Overview](sonarr_deployment_(docker)_-_role_overview.md)


