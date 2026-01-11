---
title: "️ Terraform"
---

# 🛠️ Terraform

Terraform is an infrastructure‑as‑code tool used to define and manage resources declaratively.  
In this homelab, Terraform is used to provision virtual machines on Proxmox as an alternative to the pure‑Ansible workflow.

The goal is not to replace Ansible, but to support a second provisioning backend that integrates cleanly with the existing automation.

---

## 🔗 Integration with Ansible

Ansible remains the primary interface for provisioning VMs. Terraform is invoked only when the provisioning mode is set to use the hybrid workflow.

A dedicated task file mirrors the behavior of the Ansible‑only provisioning path. It generates the required Terraform configuration, runs the Terraform commands, and hands control back to Ansible for the remainder of the lifecycle (cloud‑init, boot sequencing, cleanup, SSH hardening).

This keeps both provisioning modes aligned while allowing Terraform to manage VM creation and hardware configuration.

👉 See **[Automated Virtual Machine Provisioning](automated_virtual_machine_provisioning.md)** for the full architecture.

---

## 🔐 HashiCorp Vault

Terraform also provides an opportunity to introduce HashiCorp Vault into the homelab.  
Vault can store secrets used during VM provisioning, replacing Ansible Vault over time.  
The long‑term plan is to centralize all sensitive data in Vault and consume it from both Terraform and Ansible.

---

## 📎 Related Documentation

- **[Automated Virtual Machine Provisioning](automated_virtual_machine_provisioning.md)** — Provisioning architecture and workflow  
- **[Proxmox](proxmox.md)** — Cluster layout, storage, and node topology