# 🏠 Home Lab Overview

My home lab is a fully featured technical environment designed to sharpen skills in systems engineering, automation, DevOps, and modern infrastructure management. It simulates a production-grade ecosystem using industry-standard tools, allowing me to design, test, and refine solutions across virtualization, orchestration, authentication, and CI/CD.

Built on a clustered **[Proxmox](proxmox.md)** environment, the lab integrates automated provisioning, centralized identity, infrastructure-as-code, high-availability services, and modern authentication. It mirrors enterprise technologies while serving as a personal platform for continuous learning.

---

## 🖥 Virtualization & Infrastructure

A multi-node **[Proxmox Virtual Environment](Proxmox)** cluster hosts both Linux and Windows workloads. Key features include:

* Standardized Ubuntu 24.04 VM templates via **[cloud-init](cloud-init.md)**
* Automated provisioning with **[Ansible](ansible.md)**
* Docker-based application deployment where containerization is appropriate
* Seamless integration with the home network for reliability

This foundation enables production-like services and experimentation with new technologies.

---

## 🔐 Identity & Authentication

Identity and access management is modeled on enterprise practices:

* Windows Server 2022 **Active Directory Domain Controller**
* **[LDAP](ldap.md)** integration for compatible services
* Migration toward unified Single Sign-On using **[Microsoft Entra ID](microsoft_entra_id.md)** as an **[OAuth2](oauth2.md)** identity provider

This setup supports testing of authentication workflows, identity federation, and authorization patterns.

---

## 💾 Storage & Backup

Multiple storage backends simulate real-world architectures:

* Local SSDs for performance-critical workloads
* **[Ceph](ceph.md)** distributed storage cluster
* **[iSCSI](iscsi.md)** volumes hosted on Synology NAS
* **NFS/Samba** shares from TrueNAS

Backups are handled by **[Proxmox Backup Server](proxmox_backup_server.md)**, providing VM snapshotting, deduplication, and disaster recovery experience.

---

## ⚙️ Automation & Orchestration

Automation and reproducibility are central to the lab:

* **[Ansible](ansible.md)** for provisioning, configuration, and deployment
* **[Semaphore](semaphore.md)** as a web interface for playbook execution
* **Terraform** (driven through Ansible) for declarative infrastructure
* **Jenkins** for CI/CD pipelines and automation workflows
* **GitHub Actions** for cloud-based CI/CD and artifact automation

Together, these tools create a fully Infrastructure-as-Code environment aligned with modern DevOps practices.

---

## 💻 Infrastructure-as-Code (IaC)

The home lab is managed as **Infrastructure-as-Code** to ensure reproducibility, versioning, and maintainability:

* **Source Control:** All [Ansible code](https://github.com/t3knoid/ansible) and configuration templates are stored in **[GitHub](github.md)**, enabling history tracking, code reviews, and collaboration.
* **Development Best Practices:** Use tools such as **[Visual Studio Code](visual_studio_code.md)** and **[Code Server](code_server.md)** for editing and testing IaC locally or remotely. These tools support syntax highlighting, linting, and integrated terminal workflows.
* **Automated Provisioning:** Ansible playbooks define VM templates, service deployments, and container orchestration in a consistent, repeatable manner.
* **Change Management:** Any updates to playbooks or templates are committed to GitHub, providing an audit trail and rollback capability.

This approach ensures that every configuration change is **trackable, testable, and reproducible**, mirroring modern DevOps workflows.

---

## 🌐 Networking & Services

Networking is designed for high availability and resilience:

* **[Nginx reverse proxy cluster](Reverse-proxy)** for failover load balancing, centralized routing, and automated TLS via Let’s Encrypt
* Redundant **[Pi-hole](pi-hole.md)** instances for DNS resolution, ad/telemetry filtering, and local service discovery

This mirrors production-style ingress, routing, and DNS management patterns.

---

## 📘 Project Management

Redmine serves as the central platform for organizing and documenting all aspects of the homelab.
Because this wiki is hosted directly inside **Redmine**, it benefits from:

* Full project and task tracking across infrastructure components
* Issue management for lab improvements, troubleshooting, and feature requests
* Integrated documentation (this wiki) for architecture, configuration, and procedures
* A local Git repository mirror for viewing Ansible code changes directly within Redmine

Explore the details here:

* **[Redmine Configuration](redmine_configuration.md)** – How authentication, repositories, and system integration are configured within the homelab.

Redmine ties everything together—issues, documentation, and source code—providing a unified project management layer over the entire environment.

---

## 🎯 Why This Lab Matters

The home lab is more than an experiment—it’s a platform for continuous learning and hands-on practice with:

* Clustered virtualization and systems administration
* Identity and access management
* Automation and Infrastructure-as-Code
* CI/CD pipelines and DevOps tooling
* Distributed storage and backup
* Reverse proxying and certificate management
* DNS and network services

It enables prototyping, troubleshooting, and staying current with modern infrastructure technologies.