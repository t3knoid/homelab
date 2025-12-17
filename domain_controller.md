---
title: "️ Domain Controller Overview"
---

# 🖥️ Domain Controller Overview

A **standalone domain controller** provides centralized authentication and directory services for all hosts connected to the **refol.us** domain.  
This controller is deployed as a **Windows Server 2022 virtual machine** hosted in **Proxmox**, ensuring flexibility, scalability, and ease of management in the homelab environment.

---

## ⚙️ Virtual Machine Configuration (Proxmox)

The domain controller VM is provisioned with the following specifications:

- **Memory:** 4 GiB  
- **Processors:** 4 (1 socket, 4 cores) [host]  
- **BIOS:** OVMF (UEFI)  
- **Display:** Default  
- **Machine Type:** `pc-q35-9.0`  
- **SCSI Controller:** VirtIO SCSI single  
- **Hard Disk (ide0):** `local`, size = 32 GB  
- **Network Device (net0):** `e1000e`, bridged to `vmbr0`  
- **EFI Disk:** `local`, size = 4056 KB  
- **TPM State:** `local`, size = 4 MB  

### VM Properties
- **Operating System:** Windows Server 2022  
- **OS Disk:** 32 GB  
- **Memory:** 4 GB  
- **CPU Allocation:** 3 sockets, 1 core  
- **Hostname:** `ad0`  
- **IP Address:** `192.168.2.252`  
- **DNS Servers:**  
  - Primary: `192.168.2.253`  
  - Secondary: `8.8.8.8`  

> 📝 These resources are optimized for a lightweight but reliable domain controller in a homelab setting. For production, scaling memory and CPU would be recommended.

---

## 🏢 Active Directory Services

The domain controller hosts **Microsoft Active Directory (AD)**, providing:

- **Centralized authentication** for Windows and Linux hosts.  
- **Directory services** for user, group, and computer accounts.  
- **Integration with applications** that require domain membership or Kerberos authentication.  

This ensures consistent identity management across the **refol.us** domain.

---

## 🔐 LDAP Integration

To support applications that rely on **Lightweight Directory Access Protocol (LDAP)**, **Active Directory Lightweight Directory Services (AD LDS)** is installed.  

- **Purpose:** Enables non‑Windows applications and services to authenticate against Active Directory.  
- **Benefit:** Provides interoperability between AD and LDAP‑aware applications, ensuring seamless integration across heterogeneous environments.  

---

## ✅ Summary

This domain controller serves as the **authentication backbone** of the refol.us domain.  
- Proxmox provides a flexible virtualization platform.  
- Windows Server 2022 delivers enterprise‑grade Active Directory services.  
- AD LDS ensures LDAP compatibility for cross‑platform applications.  

Together, these components create a robust, scalable, and secure identity infrastructure for the homelab.

---

👉 Frank, would you like me to also add a **“Monitoring & Maintenance” section** (covering event logs, replication health checks, and backup strategies) so this page doubles as an operational guide?
