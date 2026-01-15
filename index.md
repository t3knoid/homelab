---
title: "Home Lab Platform Overview"
---

# 🏠 Home Lab Platform Overview

This home lab is a **self-hosted internal platform** designed to model production-grade infrastructure and SRE practices. It provides standardized compute, networking, storage, identity, and automation primitives used to deploy and operate services in a controlled environment.

The platform emphasizes **reproducibility, automation, observability, and operational discipline**, mirroring modern platform engineering principles.

---

## 🎯 Platform Goals

* Design and operate a production-like infrastructure platform
* Practice Infrastructure-as-Code and automated change management
* Implement identity-first, modern authentication workflows
* Operate observable, recoverable, and well-documented services
* Provide a safe environment for experimentation and failure analysis

---

## 🧱 Platform Foundation

The **Platform Foundation** defines the lowest architectural layer of the homelab. These components provide the execution environment upon which all platform capabilities and workloads depend.

---

### 🖥 Compute & Virtualization

A clustered **Proxmox Virtual Environment** provides the compute substrate for all workloads.

* Multi-node **[Proxmox](proxmox.md)** VE cluster
* Standardized Ubuntu 24.04 VM templates via **[cloud-init](cloud-init.md)**
* Automated VM provisioning with **[Ansible](ansible.md)**
* **[Docker](docker.md)**-based container workloads
* **[WSL2](wsl2.md)** used as an Ansible control node

---

### 🌐 Networking

Networking is designed for availability, segmentation, and secure ingress.

* Nginx **[reverse-proxy](reverse-proxy.md)** cluster for routing and TLS termination
* Automated certificate lifecycle via **[Certbot](certbot.md)**
* Redundant **[Pi-hole DNS](pi-hole_dns.md)** instances
* Dedicated DMZ VLAN documented in **[DMZ Network Design and Implementation](dmz_network_design_and_implementation.md)**

---

### 💾 Storage & Data Protection

Storage services simulate enterprise data architectures.

* **[Ceph](ceph.md)** distributed storage cluster
* **[iSCSI](iscsi.md)** volumes hosted on **[Synology NAS](synology_nas.md)**
* **[NFS](nfs.md) / Samba** exports from **[TrueNAS](truenas.md)**
* **[PostgreSQL](postgresql.md)** — standardized backend database for supported applications
* Centralized backup and recovery via **[Proxmox Backup Server](proxmox_backup_server.md)**

---

## 🔐 Identity & Access Management

Identity is centralized and treated as a first-class platform service.

* Windows Server 2022 **[Domain Controller](domain_controller.md)**
* **[LDAP](ldap.md)** integration for Linux and compatible services
* OAuth2-based access via **[Microsoft Entra ID](microsoft_entra_id.md)**

This enables testing of federation, authorization, and modern authentication flows.

---

## 🧩 Application Workloads

Application workloads are user-facing services deployed on top of the platform.  
They consume core services such as identity, storage, networking, and monitoring.

### 🎬 Media Services

- [Plex](plex.md)
- [Tautulli](tautulli.md)
- [Radarr](radarr.md)
- [Sonarr](sonarr.md)
- [Lidarr](lidarr.md)
- [Sabnzbd](sabnzbd.md)
- [Ombi](ombi.md)

### 📚 Library & Content Management

- [Calibre](calibre.md)
- [Calibre-Web](calibre-web.md)
- [Lazy Librarian](lazy_librarian.md)

### 🎮 Game Servers

- [Minecraft Server](minecraft_server.md)

### 🤖 Home Automation

- [Home Assistant](home_assistant.md) 

---

## 📈 Observability & Monitoring

The platform is observable by design.

* **[Prometheus](prometheus.md)** for metrics collection
* **[Grafana](grafana.md)** for dashboards and visualization
* Exporters deployed across compute, storage, and services

For detailed architecture, 
👉 see **[Monitoring & Observability](monitoring_&_observability.md)**.

---

## ⚙️ Automation & Platform Operations

Platform changes are automated, auditable, and repeatable.

* **[Ansible](ansible.md)** for provisioning and configuration management
* **[Semaphore](semaphore.md)** for controlled playbook execution
* **[Terraform](terraform.md)** (orchestrated via Ansible) for declarative infrastructure
* **[Jenkins](jenkins.md)** for CI/CD pipelines
* **[GitHub](github.md) Actions** for cloud-based workflows

---

## 💻 Infrastructure-as-Code

All platform configuration is managed as Infrastructure-as-Code.

* Source-controlled in **[GitHub](github.md)**
* Developed and tested using **[Visual Studio Code](visual_studio_code.md)** and **[Code Server](code_server.md)**
* Git-based change history provides auditability and rollback
* Enforces consistency across environments

---

## 📚 Operational Runbooks

Operational runbooks define **how the platform is operated**.

* VM lifecycle management
* Service deployment workflows
* Backup and recovery procedures
* Identity and networking operations

For all procedures,
👉 See **[Runbooks](runbooks.md)**.

---

## 🧱 Platform Dependency Model

The homelab follows a layered dependency model consistent with platform engineering and SRE practices.

{% raw %}
```text
+--------------------------------------------------+
|                  Applications                    |
|   Media services, test workloads, experiments    |
+--------------------------------------------------+
|           Platform Capabilities & Ops            |
|   CI/CD, Automation, IaC, Runbooks               |
+--------------------------------------------------+
|              Core Platform Services              |
|   Identity, Databases, Backup, Monitoring        |
+--------------------------------------------------+
|              Platform Foundation                 |
|   Compute, Networking, Storage                   |
+--------------------------------------------------+
|               Physical Infrastructure            |
|   Hosts, disks, network hardware                 |
+--------------------------------------------------+
```
{% endraw %}

Each layer depends only on the layer below it. Failures in lower layers propagate upward, informing monitoring priorities, recovery planning, and operational response.

---

## 📘 Platform Governance & Documentation

* **[Redmine](redmine.md)** serves as the system of record for issues and documentation
* This wiki is mirrored as a static site at
  [https://homelab.refol.us](https://homelab.refol.us)
* Mirroring workflow documented in **[Home Lab Wiki Mirror to a Static Website Workflow](home_lab_wiki_mirror_to_a_static_website_workflow.md)**

---

## 📌 Summary

This homelab functions as a **personal internal platform**, enabling standardized service delivery, reliable automation, secure access, and observable operations while supporting continuous learning aligned with real-world SRE and platform engineering practices.