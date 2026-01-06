---
title: "Docker"
---

# 🐳 Docker

This page documents **containerized application deployment using Docker and Ansible** in the homelab. It covers architecture, deployment workflow, version pinning, and integration with external resources like PostgreSQL or NFS.

Think of this as a **generic framework** for all containerized services in the homelab.

---

## 🏗 Architecture Overview

{% raw %}
```
                  ┌───────────────────────────┐
                  │ Host / Docker Environment │
                  │                           │
                  │ ┌───────────────────────┐ │
                  │ │ App Container 1       │ │
                  │ │ - Pinned Image        │ │
                  │ │ - Config & Backup     │ │
                  │ └───────────────────────┘ │
                  │ ┌───────────────────────┐ │
                  │ │ App Container 2       │ │
                  │ │ - Pinned Image        │ │
                  │ │ - Config & Backup     │ │
                  │ └───────────────────────┘ │
                  │                           │
                  └─────────────▲─────────────┘
                                │ Access
                  ┌─────────────┴─────────────┐
                  │ Users / Clients           │
                  │ Web Browser / API         │
                  └─────────────▲─────────────┘
                                │ Database or Shared Storage
                  ┌─────────────┴─────────────┐
                  │ External Services         │
                  │ - PostgreSQL              │
                  │ - NFS / Network Storage   │
                  └───────────────────────────┘
```
{% endraw %}

**Key Notes:**

* Each app runs in an **isolated container**
* Configs and backups stored in **persistent volumes**
* Containers can connect to **external resources** like PostgreSQL or NFS

---


## 📐 **Architecture & Deployment Approach**

* **Docker-Compose Templates:** Use a template `docker-compose.yml` as the primary definition for container services, volumes, ports, and environment variables.
* **Application Configuration Files:** Applications may provide their own configuration files (e.g., `config.xml`, `app.cfg`) that should be mounted into the container.
* **Volumes & Backups:** Persist data via host-mounted volumes or NFS shares for configuration and data storage.
* **Service Lifecycle Tasks:** Typical Ansible tasks include:

  1. Creating configuration directories
  2. Copying template files
  3. Starting, stopping, and updating containers
  4. Cleaning up unused images and networks

**Example Directory Layout:**

{% raw %}
```
/config/
   ├── app1/
   │    ├── docker-compose.yml
   │    └── app1.cfg
   └── app2/
        ├── docker-compose.yml
        └── app2.cfg
/nfs/backups/
   ├── app1/
   └── app2/
```
{% endraw %}

---

## ⚙️ Docker Deployment

**1. Stop & remove existing container**

{% raw %}
```bash
docker stop <container>
docker rm <container>
docker network prune -f
```
{% endraw %}

**2. Ensure persistent directories exist**

{% raw %}
```bash
mkdir -p /config/appname
mkdir -p /nfs/backups/appname
chown <user>:<group> /config/appname
```
{% endraw %}

**3. Deploy templated configuration files**

* `docker-compose.yml`
* App-specific configuration (e.g., `config.xml`, `sabnzbd.ini`)

**4. Prune unused Docker images (optional)**

{% raw %}
```bash
docker image prune -f
```
{% endraw %}

**5. Pull pinned Docker image**

{% raw %}
```bash
docker-compose -f /config/appname/docker-compose.yml pull
```
{% endraw %}

**6. Start container**

{% raw %}
```bash
docker-compose -f /config/appname/docker-compose.yml up -d
```
{% endraw %}

The [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md) page provides a side-by-side equivalence between manual Docker deployment commands and the automated Ansible tasks.

---

## 🔒 Version Pinning & Best Practices

* Always **pin Docker images to a specific version**:

{% raw %}
```yaml
app_setup_version: "1.2.3"
app_setup_docker_image_name: "appname:{{ app_setup_version }}"
```
{% endraw %}

* Avoid `latest` for reproducibility
* Use **templated Docker Compose files**
* Keep **config & data volumes separate**
* Store logs/backups on **persistent network storage**

---

## 🌐 Integrating External Resources

* **Databases**: e.g., Radarr, Sonarr, Lidarr use external PostgreSQL

{% raw %}
```yaml
app_setup_pg_host: "{{ global_ip_addresses[groups['pgdb'][0]] }}"
app_setup_pg_port: 5432
```
{% endraw %}

* **Network Storage**: Configs, downloads, backups mounted from NFS or Ceph
* Containers connect via **environment variables and mounted volumes**

---

## 🎯 Key Features

* Fully automated container deployment via **Ansible**
* Persistent configuration & backup volumes
* Pinned Docker images for reproducibility
* Template-driven, scalable deployments
* Integration with external databases and network storage
* Reusable workflow for all homelab apps

---

## 📚 Related Pages

* [Calibre Deployment (Docker) - Role Overview](calibre_deployment_(docker)_-_role_overview.md)
* [Calibre-Web Deployment (Docker) - Role Overview](calibre-web_deployment_(docker)_-_role_overview.md)
* [Docker Command Cheat Sheet](docker_command_cheat_sheet.md)
* [Docker Deployment Example Commands vs Ansible Tasks](docker_deployment_example_commands_vs_ansible_tasks.md)
* [Lazy Librarian Deployment (Docker) - Role Overview](lazy_librarian_deployment_(docker)_-_role_overview.md)
* [Lidarr Deployment (Docker) - Role Overview](lidarr_deployment_(docker)_-_role_overview.md)
* [Radarr Deployment (Docker) - Role Overview](radarr_deployment_(docker)_-_role_overview.md)
* [SABnzbd Deployment (Docker) - Role Overview](sabnzbd_deployment_(docker)_-_role_overview.md)
* [Sonarr Deployment (Docker) - Role Overview](sonarr_deployment_(docker)_-_role_overview.md)