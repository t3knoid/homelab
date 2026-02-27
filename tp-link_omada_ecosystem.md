---
title: "TP-Link Omada Ecosystem"
---

# TP-Link Omada Ecosystem

The homelab network is built on the **TP-Link Omada SDN ecosystem** — a centrally managed stack that unifies routing, switching, wireless access, VLAN segmentation, VPN connectivity, and firewall policy enforcement under a single control plane.

Rather than configuring each device independently, Omada provides controller-based management that ensures consistency, scalability, and clean network architecture. VLANs, SSIDs, port profiles, VPN policies, and firewall rules are defined once and propagated across the environment.

---

## 🧱 Core Network Topology

At a high level, the network follows a structured three-layer model:

Internet
↓
**ER605 Gateway**
↓
**TL-SG2428P Main Switch**
↓
Access Points + Infrastructure Switch
↓
Homelab & Client Devices

Each component has a clearly defined role within the ecosystem.

---

## 🌐 Gateway Layer — ER605 v1.0

**Device:** TP-Link ER605 v1.0
**Role:** Gateway, Router, Firewall, VPN Endpoint

The ER605 sits at the edge of the network and functions as:

* Primary WAN gateway
* Inter-VLAN router
* Firewall policy engine
* VPN server/client endpoint
* Port forwarding controller

### Key Responsibilities

#### 🔐 VLAN Routing & Firewall Enforcement

All VLAN interfaces terminate at the ER605. Inter-VLAN communication is explicitly controlled through firewall rules, enforcing trust boundaries between:

* LAN
* Infrastructure
* IoT
* DMZ
* Management networks

No VLAN communicates implicitly — all traffic is policy-driven.

#### 🌍 Port Forwarding (NAT)

Public-facing services in the DMZ are exposed through controlled port forwarding rules. Each rule maps:

* WAN IP/Port → Internal DMZ Host → Specific Service Port

Ingress access is tightly scoped and monitored to minimize exposure.

#### 🔒 VPN Services

The ER605 provides secure remote access and site connectivity using:

* Client VPN (remote user access)
* Site-to-site VPN (if applicable)
* Policy-bound VPN access to specific VLANs

VPN access is segmented — remote users do not gain unrestricted LAN access.

---

## 🔁 Core Switching Layer — TL-SG2428P v1.0

**Device:** TP-Link TL-SG2428P v1.0
**Role:** Main PoE Switch & VLAN Distribution Core

The TL-SG2428P is the central switching backbone of the homelab.

It connects directly to the ER605 and:

* Carries all VLAN trunks
* Powers access points via PoE
* Distributes VLANs across wired infrastructure
* Enforces port profiles

### Why This Switch Is the Core

* 24 Gigabit ports
* PoE support for APs
* Full VLAN tagging support
* Trunk uplinks to access switches
* Central aggregation point for wireless and wired traffic

All access points connect directly to this switch. It acts as the VLAN distribution layer for the entire network.

---

## 🖧 Infrastructure Access Layer — SG2008 v4.20

**Device:** TP-Link SG2008 v4.20
**Role:** Homelab Infrastructure Switch

The SG2008 connects downstream from the TL-SG2428P and services:

* Homelab servers
* Virtualization hosts
* Storage systems
* Core infrastructure services

This switch carries tagged VLAN trunks from the main switch and breaks them out to infrastructure devices according to port profile configuration.

### Design Intent

Infrastructure services are separated from user and IoT networks via VLANs. This reduces lateral movement risk and ensures predictable traffic flows between:

* Application servers
* Management interfaces
* Storage networks
* Monitoring systems

---

## 📡 Wireless Access Layer

All access points connect directly to the **TL-SG2428P main switch** and are managed through the Omada Controller.

### EAP620 HD v3.0

High-density ceiling-mount AP for primary wireless coverage.

### EAP615-Wall v1.0

In-wall AP providing room-level coverage with integrated switch ports.

### EAP235-Wall v1.0

Compact in-wall AP for targeted coverage zones.

### SSID-to-VLAN Mapping

Each SSID maps directly to a VLAN, including:

* Primary LAN
* Guest network
* IoT network
* Management network (hidden)

Wireless segmentation mirrors wired segmentation. Devices joining an SSID are automatically placed into the appropriate VLAN with corresponding firewall rules applied.

---

## 🧩 VLAN-Centric Architecture

VLANs are the backbone of the design.

They provide:

* Logical segmentation
* Trust boundaries
* Broadcast domain isolation
* Security policy enforcement points
* Clean routing design

Each VLAN is:

* Defined in the Omada Controller
* Propagated across trunk ports
* Assigned to switch port profiles
* Bound to SSIDs where applicable
* Routed and filtered at the ER605

This ensures consistency from the gateway to the access layer.

---

## 🔐 Security & Boundary Enforcement

Security in this ecosystem is not device-based — it is policy-based.

* Inter-VLAN traffic is deny-by-default
* IoT networks cannot reach infrastructure networks
* DMZ services cannot initiate traffic inward
* Management VLAN access is restricted
* VPN access is scoped to specific VLANs

Segmentation is enforced both logically (VLAN) and through firewall policy.

---

## 🌍 DMZ & Public Exposure Model

Public-facing services are isolated into a dedicated DMZ VLAN.

Traffic Flow:

Internet → ER605 (Port Forwarding Rule) → DMZ Host → Restricted Return Path

The DMZ:

* Has no implicit access to internal networks
* Is allowed only specific, tightly scoped flows
* Is monitored through firewall policy and logging

This limits blast radius in the event of compromise.

---

## 🔄 Centralized Management with Omada Controller

The Omada Controller provides:

* Single-pane-of-glass management
* VLAN configuration
* SSID mapping
* Port profile deployment
* Firmware management
* Monitoring & statistics

Changes are consistent across devices, eliminating configuration drift and simplifying scaling.

---

## 🎯 Design Philosophy

This Omada ecosystem is designed around:

* Intentional segmentation
* Explicit trust boundaries
* Centralized policy enforcement
* Scalable infrastructure
* Clean topology design

Rather than building a flat network and layering rules afterward, segmentation is foundational.

VLANs define structure.
Firewall rules enforce boundaries.
VPNs extend access securely.
Port forwarding exposes services intentionally — never implicitly.

The result is a homelab network that is secure, organized, scalable, and easy to reason about.

