---
title: "Home Lab Overview"
---

# 🏠 Home Lab Overview

My home lab is a fully featured technical environment designed to sharpen skills in systems engineering, automation, DevOps, and modern infrastructure management. It simulates a production‑grade ecosystem using industry‑standard tools, allowing me to design, test, and refine solutions across virtualization, orchestration, authentication, and CI/CD.

Built on a clustered Proxmox environment, the lab integrates automated provisioning, centralized identity, infrastructure‑as‑code, high‑availability services, and modern authentication. It mirrors enterprise technologies while serving as a personal platform for continuous learning.

---

# 🖥 Virtualization & Infrastructure

A multi‑node [Proxmox](proxmox.md) Virtual Environment cluster hosts both Linux and Windows workloads. Key features include:

* Standardized Ubuntu 24.04 VM templates via **[cloud-init](cloud-init.md)**
* **[Automated virtual machine provisioning](automated_virtual_machine_provisioning.md)** with **[Ansible](ansible.md)**
* **[Docker](docker.md)**‑based application deployment where containerization is appropriate
* Seamless integration with the home network for reliability
* Use of **[WSL2](wsl2.md)** as an Ansible control node


This foundation enables production‑like services and experimentation with new technologies.

---

# 🔐 Identity & Authentication

Identity and access management is modeled on enterprise practices:

* Windows Server 2022 Microsoft Active Directory **[Domain Controller](domain_controller.md)**
* **[LDAP](ldap.md)** integration for compatible services
* Migration toward unified Single Sign‑On using **[Microsoft Azure](microsoft_azure.md)** Entra ID as an **[Oauth2 Proxy](oauth2_proxy.md)** identity provider


This supports testing of authentication workflows, identity federation, and authorization patterns.

---

# 💾 Storage & Backup

Multiple storage backends simulate real‑world architectures:

* Local SSDs for performance‑critical workloads
* **[Ceph](ceph.md)** distributed storage cluster
* **[iSCSI](iscsi.md)** volumes hosted on **[Synology NAS](synology_nas.md)**
* NFS/Samba shared from a **[TrueNAS](truenas.md)** server


Backups are handled by **[Proxmox Backup Server](proxmox_backup_server.md)** , providing VM snapshotting, deduplication, and disaster recovery experience.

---

# ⚙️ Automation & Orchestration

Automation and reproducibility are central to the lab:

* **[Ansible](ansible.md)** for provisioning, configuration, and deployment
* **[Semaphore](semaphore.md)** as a web interface for playbook execution
* **[Terraform](terraform.md)** (driven through Ansible) for declarative infrastructure
* **[Jenkins](jenkins.md)** for CI/CD pipelines and automation workflows
* **[GitHub](github.md)** Actions for cloud‑based CI/CD and artifact automation


Together, these tools create a fully Infrastructure‑as‑Code environment aligned with modern DevOps practices.

---

# 💻 Infrastructure‑as‑Code (IaC)

The home lab is managed as Infrastructure‑as‑Code to ensure reproducibility, versioning, and maintainability:

* Source Control: All Ansible code and configuration templates are stored in **[GitHub](github.md)**
* Development Best Practices: Editing and testing via **[Visual Studio Code](visual_studio_code.md)** and **[Code Server](code_server.md)**
* Automated Provisioning: Ansible defines VM templates, service deployments, and container orchestration
* Change Management: GitHub commits provide auditability and rollback capability


Every configuration change is trackable, testable, and reproducible, mirroring modern DevOps workflows.

---

# 🌐 Networking

Networking is designed for high availability and resilience:

* Nginx **[reverse-proxy](reverse-proxy.md)** cluster for load balancing, routing, and automated TLS
* **[Certificates](certificates.md)** issued and managed through **[Certbot](certbot.md)**
* Redundant **[Pi-hole DNS](pi-hole_dns.md)** instances for DNS resolution and filtering
* A dedicated DMZ VLAN described in **[DMZ Network Design and Implementation](dmz_network_design_and_implementation.md)**


---

# 🧱 Core Services

Foundational services that power applications across the homelab:

## Databases

* **[PostgreSQL](postgresql.md)** — standardized backend database for supported applications (Radarr, Sonarr, Lidarr, etc.)


## Monitoring Stack

* **[Prometheus](prometheus.md)** — metrics collection
* **[Grafana](grafana.md)** — dashboards and visualization
* Exporters integrated across compute, storage, and applications


## Application Infrastructure

* **Autofs** for NFS‑based backup and media mounts
* **PBS (Proxmox Backup Server)** as a service layer for VM and container backups


This section serves as the service catalog for the homelab.

---

# 📈 Monitoring & Observability

A full monitoring stack built on **[Prometheus](prometheus.md)** and **[Grafana](grafana.md)** provides visibility into system health across compute, storage, networking, and applications.

👉 For the full architecture and exporter breakdown, see **[Monitoring & Observability](monitoring_&_observability.md)**.

Services → Exporters → Prometheus → Grafana → Alerts


---

# 📘 Project Management

Redmine serves as the central platform for organizing and documenting all aspects of the homelab. Because this wiki is hosted directly inside **[Redmine](redmine.md)**, it ties together issues, documentation, and source code into a unified project management layer.

---

# 📚 Runbooks & Operational Procedures

Operational runbooks provide step‑by‑step instructions for managing, troubleshooting, and extending the home lab. They complement the architecture documentation by giving practical guidance for recurring tasks and workflows.

Key runbooks include:

* VM lifecycle management
* Service deployment
* Backup & recovery
* Authentication & networking workflows

All runbooks are consolidated in the **[Runbooks](runbooks.md)** page to ensure operations are repeatable, reliable, and auditable.

---

# 📌 Mirrored Documentation

This wiki is mirrored as a static HTML website at
https://homelab.refol.us

For details on the mirroring workflow, see [Home Lab Wiki Mirror to a Static Website Workflow](home_lab_wiki_mirror_to_a_static_website_workflow.md).

---

# 🎯 Why This Lab Matters

The home lab is a platform for continuous learning and hands‑on practice with:

* Clustered virtualization and systems administration
* Identity and access management
* Automation and Infrastructure‑as‑Code
* CI/CD pipelines and DevOps tooling
* Distributed storage and backup
* Reverse proxying and certificate management
* DNS and network services


It enables prototyping, troubleshooting, and staying current with modern infrastructure technologies.