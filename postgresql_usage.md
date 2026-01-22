---
title: "PostgreSQL Usage"
---

# 🐘 PostgreSQL Usage

PostgreSQL serves as the standardized relational database engine for all applications in the homelab that support it. Each application is provisioned with its own dedicated PostgreSQL server instance, ensuring clean separation of state, predictable performance, and simplified lifecycle management.

This page explains how applications map to PostgreSQL backends, why this pattern is used, and how contributors should think about database placement when adding new services.

## 🎯 Why PostgreSQL Is Standardized

Using PostgreSQL as the default database engine provides several advantages:

* Isolation between applications
* Predictable performance characteristics
* Unified automation and provisioning
* Consistent observability patterns
* Reduced contributor overhead

## 🗺️ Application‑to‑Database Mapping

The diagram below shows how each application connects to its assigned PostgreSQL server over TCP port 5432.

                         +---------------------------------------------+
                         |               PostgreSQL Servers            |
                         |  pg-0  192.168.2.170   (standalone)         |
                         |  pg-1  192.168.2.171   (standalone)         |
                         |  pg-2  192.168.2.172   (standalone)         |
                         |  pg-3  192.168.2.173   (standalone)         |
                         |  pg-4  192.168.2.174   (standalone)         |
                         +--------------------+------------------------+
                                              |
                                              |  TCP 5432 (default)
                                              v

                +---------------------------------------------------------------+
                |                           Applications                        |
                +---------------------------------------------------------------+

                ombi (ombi-0 — 192.168.2.155)
                    |
                    +-------------------------------> pg-0 (192.168.2.170:5432)

                services (all -> pg-1):
                    - sonarr   (sonarr-0   — 192.168.2.150)
                    - lidarr   (lidarr-0   — 192.168.2.151)
                    - radarr   (radarr-0   — 192.168.2.152)
                    - sabnzbd  (sabnzbd-0  — 192.168.2.153)
                    - books    (books-0    — 192.168.2.160)
                    |
                    +-------------------------------> pg-1 (192.168.2.171:5432)

                grafana (grafana-0 — 192.168.2.195)
                    |
                    +-------------------------------> pg-4 (192.168.2.174:5432)

                redmine (redmine-0 — 192.168.2.186)
                    |
                    +-------------------------------> pg-2 (192.168.2.172:5432)

                semaphore (semaphore-0 — 192.168.2.110)
                    |
                    +-------------------------------> pg-3 (192.168.2.173:5432)

