# Calibre Deployment (Docker) - Role Overview

This page documents the **Calibre Docker deployment using Ansible**, illustrating the workflow, architecture, and best practices for deploying this containerized ebook management application with version control, persistent storage, and optional integration with external resources.

---

## **1. Overview**

Calibre is deployed in a Docker container using Ansible. Key steps include:

* **Stop existing container** safely
* **Prepare persistent configuration and library directories**
* **Deploy templated Docker Compose and application configuration files**
* **Version control the Docker image** to prevent accidental upgrades
* **Start the container**

Additionally, Calibre can integrate with **network-mounted libraries** or external storage for ebook management.

---

## **2. Persistent Configuration and Library Storage**

Persistent storage ensures application data is preserved across container restarts:

* Configuration directory: `/config/calibre`
* Library directory: `/books` or network-mounted paths

Example variables from the role:

```yaml
calibre_setup_config_dir: "/config/calibre"
calibre_setup_library_dir: "/books"
calibre_setup_backup_dir: "/nfs/backups/calibre"
```

* Directories are **created and owned** by a dedicated system user
* Supports **NFS or other network storage** for centralized ebook libraries
* Ensures container can read/write configs and library files

---

## **3. Docker Image Version Control**

The role pins a specific Docker image version:

```yaml
calibre_setup_version: "6.23.0"
calibre_setup_docker_image_name: "ghcr.io/linuxserver/calibre:version-{{ calibre_setup_version }}"
```

* Avoids pulling `latest` automatically
* Guarantees reproducible deployments
* Allows testing and validation of known working versions

---

## **4. Deployment Workflow**

The sequence for deploying Calibre is:

1. **Stop and remove existing container**

   ```bash
   docker stop calibre
   docker rm calibre
   docker network prune -f
   ```

2. **Ensure persistent directories exist**

   ```bash
   mkdir -p {{ calibre_setup_config_dir }}
   mkdir -p {{ calibre_setup_library_dir }}
   mkdir -p {{ calibre_setup_backup_dir }}
   chown <user>:<group> {{ calibre_setup_config_dir }}
   ```

3. **Deploy configuration files and Docker Compose**

   * `docker-compose.yml`
   * Optional `calibre-server.conf` or other application-specific configs

4. **Prune unused Docker images** (optional)

   ```bash
   docker image prune -f
   ```

5. **Pull the pinned Docker image**

   ```bash
   docker-compose -f {{ calibre_setup_config_dir }}/docker-compose.yml pull
   ```

6. **Start the container**

   ```bash
   docker-compose -f {{ calibre_setup_config_dir }}/docker-compose.yml up -d
   ```

All of these steps are **automated in the Ansible role**.

---

## **5. Architecture Diagram**

```
                 ┌───────────────────────────────┐
                 │   Host / Docker Environment   │
                 │                               │
                 │ ┌───────────────────────────┐ │
                 │ │ Calibre Container         │ │
                 │ │ - Pinned Image            │ │
                 │ │ - Config & Library Volumes│ │
                 │ │ - Exposed Port 8080       │ │
                 │ └───────────────────────────┘ │
                 │                               │
                 └───────────────▲───────────────┘
                                 │ Access
                 ┌───────────────┴───────────────┐
                 │ Users / Clients               │
                 │ Web Browser / Calibre Apps    │
                 └───────────────▲───────────────┘
                                 │ Library Storage
                 ┌───────────────┴──────────────┐
                 │ External / Network Storage   │
                 │ - /books                     │
                 │ - /nfs/backups/calibre       │
                 └──────────────────────────────┘
```

* Config directory and library volumes are mounted inside the container
* Optional NFS storage allows centralized library and backup management

---

## **6. Key Features**

* Automated deployment via **Ansible**
* Persistent configuration and library storage
* Pinned Docker image for reproducibility
* Optional NFS or network storage for centralized libraries
* Template-driven configuration for **consistent, scalable deployments**

---

## **7. Summary**

The Calibre deployment role demonstrates a **robust, production-like container workflow**:

* Safe, repeatable container start/stop sequences
* Version-controlled Docker images to prevent accidental updates
* Persistent configuration and library storage
* Optional integration with external network storage for scalability
* Template-driven deployment allowing easy replication in the homelab

> This workflow can be adapted to other containerized home lab applications with similar persistent storage and configuration requirements.

---

## **8. Related Pages**

* [Calibre-Web Deployment (Docker) - Role Overview](calibre-web_deployment_(docker)_-_role_overview.md)
* [Docker Command Cheat Sheet](docker_command_cheat_sheet.md)
* [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md)
* [LazyLibrarian Deployment (Docker) - Role Overview](lazylibrarian_deployment_(docker)_-_role_overview.md)
* [Lidarr Deployment (Docker) - Role Overview](lidarr_deployment_(docker)_-_role_overview.md)
* [Radarr Deployment (Docker) - Role Overview](radarr_deployment_(docker)_-_role_overview.md)
* [SABnzbd Deployment (Docker) - Role Overview](sabnzbd_deployment_(docker)_-_role_overview.md)
* [Sonarr Deployment (Docker) - Role Overview](sonarr_deployment_(docker)_-_role_overview.md)

