---
title: "VLAN Architecture and Segmentation"
---

# VLAN Architecture and Segmentation

One of the core design principles of my homelab is intentional network segmentation. VLANs aren’t just organizational tools — they define security boundaries, availability domains, and trust levels across the entire environment.

This homelab runs on the TP-Link Omada networking stack, which provides centralized control of switching, routing, wireless, VLANs, and firewall policies across the environment.

For a deeper look at the hardware, controller model, and design philosophy behind the stack, see:

👉 **[TP-Link Omada Ecosystem](tp-link_omada_ecosystem.md)**

With centralized management in place, VLANs become more than just logical groupings — they define trust boundaries, availability domains, and security zones across the entire network.

---

## 🧩 VLAN Design Model

The homelab uses a structured VLAN model to enforce security boundaries, define trust levels, and simplify traffic flows across the environment.

### **VLAN 1 — Default / Control Plane Network (Legacy Backbone)**

The physical network’s default VLAN.  In this homelab, VLAN 1 is reserved exclusively for **switch management, router uplinks, and foundational control-plane functions** that must remain reachable even during misconfiguration events.  

No clients, servers, hypervisors, or workloads reside here.

This VLAN provides:

- a stable fallback for network hardware management  
- isolation from all user and workload traffic  
- a clean separation between physical control-plane and logical infrastructure services  

### **VLAN 10 — Client LAN**

Trusted user devices and general client workloads.  No direct access to infrastructure services except through approved interfaces.

### **VLAN 20 — Infrastructure**

Core internal services, DNS, databases, monitoring, and automation.  This VLAN forms the **logical control plane** of the homelab, supporting all cluster‑critical communication of infrastructure services.

### **VLAN 30 — DMZ**

Public‑facing and boundary‑facing services such as reverse proxy, VPN egress, and externally accessible applications.  Strict ingress/egress rules isolate the DMZ from the internal network.

### **VLAN 40 — IoT & Embedded Devices**

Low‑trust smart home devices (lights, switches, plugs, thermostats, cameras, ESP modules). This VLAN limits device‑to‑device communication and tightly controls what traffic can leave or enter the network, and it also keeps the high‑volume, chatty traffic typical of IoT devices contained so it doesn’t spill into or degrade other networks.

### **VLAN 50 - Cluster Fabric**

A dedicated, high‑trust network reserved exclusively for **[Proxmox](proxmox.md)** hypervisors and storage systems. This VLAN provides a quiet, low‑latency path for VM disk I/O, migrations, and replication. Isolating this traffic from infrastructure services and workloads ensures predictable cluster performance, reduces contention, and keeps the hypervisor–storage data plane free from noise generated elsewhere in the homelab.

---

## 🏗 Building the Foundation: VLAN Creation & Baseline Configuration

Everything starts with consistency.

Before any service or device is deployed, VLANs are created using standardized naming conventions, structured ID assignments, and repeatable port profiles. This ensures scalability and prevents configuration drift as the network grows.

Switch-level propagation, tagging rules, and Omada controller configuration are all part of this foundational layer.

👉 See: **[VLAN Creation Procedure](vlan_creation_procedure.md)**

---

## 🛡 Designing the DMZ & Enforcing Boundaries

Public-facing services live in the DMZ — intentionally separated from the internal network.

The DMZ architecture enforces:

* Strict ingress rules
* Controlled egress policies
* Minimal access back into trusted VLANs
* Clearly defined service boundaries

By isolating exposure at the perimeter, the internal network remains protected even if a public-facing service is compromised.

👉 See: **[DMZ Network Design and Implementation](dmz_network_design_and_implementation.md)**