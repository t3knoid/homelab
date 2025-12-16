# Docker Deployment Commands vs Ansible Workflow

This page illustrates the **equivalence between manual Docker commands and the automated Ansible tasks** used in the homelab roles for containerized applications. It serves as a reference to understand how Ansible simplifies and standardizes container deployment.

---

## **1. Stop & Remove Container**

| Docker Command                        | Equivalent Ansible Task                                                               |
| ------------------------------------- | ------------------------------------------------------------------------------------- |
| `docker ps --filter name=<container>` | `Check if container is running` (sets a fact)                                         |
| `docker stop <container>`             | `ansible.builtin.command: docker stop <container>` (conditional on container running) |
| `docker rm <container>`               | `ansible.builtin.command: docker rm <container>` (conditional on container running)   |
| `docker network prune -f`             | `ansible.builtin.command: docker network prune -f`                                    |

**Notes:**

* Ansible tasks automatically check whether the container exists before stopping/removing it.
* Manual steps require conditional checks to avoid errors.

---

## **2. Prepare Persistent Directories**

| Docker/Manual Step                     | Equivalent Ansible Task                                                     |
| -------------------------------------- | --------------------------------------------------------------------------- |
| `mkdir -p /config/appname`             | `ansible.builtin.file: path=/config/appname state=directory mode=0755`      |
| `mkdir -p /nfs/backups/appname`        | `ansible.builtin.file: path=/nfs/backups/appname state=directory mode=0777` |
| `chown <user>:<group> /config/appname` | `ansible.builtin.file: owner=<user> group=<group> recurse=true`             |

**Notes:**

* Ensures the container has read/write access to configuration and backup folders.
* Automatically handles NFS-mounted volumes in Ansible roles.

---

## **3. Deploy Configuration & Docker Compose**

| Manual Step                                            | Equivalent Ansible Task                                                                       |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Copy `docker-compose.yml` to config dir                | `ansible.builtin.template: src=docker-compose.yml.j2 dest=/config/appname/docker-compose.yml` |
| Copy app-specific config (`config.xml`, `sabnzbd.ini`) | `ansible.builtin.template: src=config_file.j2 dest=/config/appname/config_file`               |

**Notes:**

* Ansible uses **Jinja2 templates** for consistency and version control.
* Supports dynamic configuration based on role variables.

---

## **4. Prune Unused Docker Images**

| Docker Command                         | Equivalent Ansible Task                                                                    |
| -------------------------------------- | ------------------------------------------------------------------------------------------ |
| `docker image prune -f`                | `ansible.builtin.command: docker image prune -f`                                           |
| `docker rmi -f $(docker images -a -q)` | `ansible.builtin.shell: docker rmi -f $(docker images -a -q)` (ignore errors if no images) |

---

## **5. Pull Pinned Docker Image**

| Docker Command                                              | Equivalent Ansible Task                                                              |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `docker-compose -f /config/appname/docker-compose.yml pull` | `ansible.builtin.command: docker-compose -f /config/appname/docker-compose.yml pull` |

**Notes:**

* Version pinning is controlled in the role variable: `app_setup_version`.
* Ensures reproducible deployments.

---

## **6. Start Container**

| Docker Command                                               | Equivalent Ansible Task                                                               |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `docker-compose -f /config/appname/docker-compose.yml up -d` | `ansible.builtin.command: docker-compose -f /config/appname/docker-compose.yml up -d` |

**Notes:**

* Roles like Radarr, Sonarr, Lidarr, SABnzbd, and LazyLibrarian all follow this pattern.
* Optional pre-checks ensure directories and configs are ready before starting the container.

---

## **7. Summary**

Using Ansible roles for Docker deployments provides:

* **Automation**: Manual commands are replaced by reproducible tasks.
* **Consistency**: Template-driven configs ensure all containers follow the same structure.
* **Safety**: Conditional checks prevent errors when stopping/removing containers.
* **Scalability**: New applications can be deployed using the same workflow.

> The workflow illustrated here is applied across all homelab containerized applications, including Radarr, Sonarr, Lidarr, SABnzbd, and LazyLibrarian.

---

## **8. Related Pages**

* **[[Docker Deployment - Home Lab Overview]]**
* **[[Radarr Deployment (Docker) - Role Overview]]**
* **[[Sonarr Deployment (Docker) - Role Overview]]**
* **[[Lidarr Deployment (Docker) - Role Overview]]**
* **[[SABnzbd Deployment (Docker) - Role Overview]]**
* **[[LazyLibrarian Deployment (Docker) - Role Overview]]**

