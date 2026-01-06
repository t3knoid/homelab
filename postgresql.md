---
title: "PostgreSQL"
---

# 🐘 PostgreSQL

PostgreSQL is the standardized database engine used across the homelab whenever an application supports it. Services such as Radarr, Sonarr, and Lidarr all use PostgreSQL for their backend storage. The entire lifecycle—installation, configuration, database creation, access control, and backups—is automated using Ansible.

If you're looking to integrate PostgreSQL into a new service,

👉 see the **[Adding PostgreSQL to a Service Contributor Guide](adding_postgresql_to_a_service_contributor_guide.md)** for a step‑by‑step workflow.

---

## 🏗️ Architecture Overview

| Component | Description |
|----------|-------------|
| **pg-1** | Dedicated PostgreSQL VM (inventory group: `pgdb`) |
| **Ansible Role** | `postgresql_setup` installs and configures PostgreSQL |
| **Application DB Roles** | Each service (Radarr, Sonarr, etc.) has a role that creates its DB + user |
| **Backups** | Per‑service backup tasks using `pg_dump` |
| **Storage** | Backups stored on NFS share hosted by TrueNAS |

---

## 🚀 Deployment via Ansible

PostgreSQL is deployed using the `postgresql_setup` role. This role:

- Installs PostgreSQL from the official PGDG repository  
- Creates a custom data directory  
- Initializes the database cluster  
- Configures authentication (`pg_hba.conf`)  
- Enables remote access (`listen_addresses = '*'`)  
- Ensures the service is enabled and running  

### Key Features of the Role

- Uses the upstream PostgreSQL APT repository  
- Moves the data directory to a custom path  
- Enforces MD5 authentication  
- Supports both local and remote access rules  
- Idempotent initialization using `creates: PG_VERSION`  
- Automatically restarts PostgreSQL when configuration changes  

---

## 🗂️ Inventory Layout

Applications that use PostgreSQL reference the `pgdb` group:

{% raw %}
```
[pgdb]
pg-1
```
{% endraw %}

This ensures all database‑related tasks run on the correct host.

---

## 🛠️ Creating Databases for Applications

Each application has a dedicated Ansible role that:

- Installs required PostgreSQL client libraries  
- Creates the application’s database user  
- Creates one or more databases  
- Updates `pg_hba.conf` to allow access from the application host  
- Manages `.pgpass` for passwordless automation  

### Example: Radarr

The Radarr role:

- Creates the main Radarr DB  
- Creates a log DB  
- Adds host‑based access rules  
- Ensures `.pgpass` is present for the `postgres` user  
- Notifies PostgreSQL to restart when needed  

This pattern is reused for Sonarr, Lidarr, and any future services.

---

## 💾 Backups

Backups are performed using a dedicated task file that:

1. Runs `pg_dump` in custom format (`-Fc`)  
2. Stores the backup on an NFS mount provided by TrueNAS  
3. Keeps only the latest 3 backups per service  

### Backup Workflow

- Each service has its own backup directory  
- Backups are named using a prefix and timestamp  
- Cleanup is handled automatically using `ls -1t | tail -n +4`  

This ensures backups remain lightweight and manageable.

---

## 🧩 Adding a New PostgreSQL‑Backed Service

To add a new service:

1. Add the service host to inventory  
2. Create a role with a `database.yml` task file  
3. Use `community.postgresql` modules to create user + DB  
4. Add `pg_hba.conf` entries for the service host  
5. Add `.pgpass` entries for automation  
6. Add a backup task file using the standard pattern  

A **[full contributor guide](adding_postgresql_to_a_service_contributor_guide.md)** is provided.
