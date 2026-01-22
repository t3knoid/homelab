---
title: "Homelab Network Architecture and Traffic Flows"
---

# 🏡 **Homelab Network Architecture and Traffic Flows**

This page documents the complete network architecture of the homelab, including:

- Physical topology (switching, APs, wiring)
- VLAN segmentation
- DMZ placement
- Ingress and egress paths
- Firewall rule flows
- Forward proxy and VPN chaining
- Service‑to‑service communication
- Proxmox node placement

It serves as the authoritative reference for contributors, troubleshooting, and future expansion.

---

# 📡 **1. Physical Network Topology (TP‑Link Omada)**

This ASCII diagram recreates the physical topology exported from the Omada controller. It shows how the modem, router, switches, APs, cameras, and client/server devices are interconnected.

{% raw %}
```text
                                  ┌──────────────┐
                                  │   INTERNET   │
                                  └──────┬───────┘
                                         │
                                   ┌─────▼────┐
                                   │   xDSL   │
                                   │   Modem  │
                                   └─────┬────┘
                                         │
                          ┌──────────────▼─────────────┐
                          │        Router / Switch     │
                          └────┬─────────┬─────────┬───┘
                               │         │         │
                               │         │         │
                               ▼         ▼         ▼
                         ┌────────┐ ┌────────┐ ┌────────┐
                         │ Access │ │ Access │ │ Access │
                         │ Switch │ │ Switch │ │ Switch │
                         └──┬───┬─┘ └──┬───┬─┘ └──┬───┬─┘
                            │   │      │   │      │   │
                            ▼   ▼      ▼   ▼      ▼   ▼
                          [3] [24]    [4] [21]   [11][10]
                         C/S C/S     C/S C/S     AP  C/S
                          │   │       │   │       │   │
                          ▼   ▼       ▼   ▼       ▼   ▼
                         C/S C/S     C/S C/S     C/S C/S
```
{% endraw %}

### 🔍 Legend

- **C/S** = Client/Server device  
- **AP** = Access Point  
- Numbers in brackets represent the number of devices connected at that node  

This diagram represents the *physical* wiring and switching hierarchy. The logical architecture below overlays VLANs, DMZ boundaries, and traffic flows on top of this structure.

---

# 🧭 **2. VLAN & Security Zone Architecture**

Your homelab uses three primary VLANs:

| VLAN | Purpose | Notes |
|------|---------|-------|
| **10** | DNS / Unbound | Pi‑hole primary/secondary, recursive resolver,workstations, laptops, phones, tablets, home devices actively used |
| **20** | Internal Services | App containers, databases, automation, hypervisors, core services, internal-only apps, management interfaces |
| **30** | DMZ | Reverse proxy, public‑facing services, egress proxy, anything exposed to or tightly coupled with the Internet |

These VLANs are trunked across the access switches shown in the physical topology.

---

# 🔐 **3. DMZ Placement**

The DMZ (VLAN 30) sits between:

- **External Firewall** (Internet → DMZ)
- **Internal Firewall** (DMZ → Internal Services)

This isolates public‑facing or boundary‑facing services from the trusted LAN.

DMZ hosts include:

- Reverse Proxy (Nginx)
- Forward Proxy (Tinyproxy)
- VPN egress gateway (optional)

---

# 🌐 **4. Ingress Architecture (Reverse Proxy)**

Inbound traffic flow:

{% raw %}
```
Internet
  → External Firewall
  → VLAN 30 (DMZ Reverse Proxy)
  → Internal Firewall
  → VLAN 20 (Internal Services)
```
{% endraw %}

The reverse proxy enforces:

- HTTPS termination  
- OAuth2 / SSO  
- Path‑based routing  
- Rate limiting  
- Zero‑trust boundaries  

---

# 📤 **5. Egress Architecture (Forward Proxy + VPN)**

Outbound traffic flow:

{% raw %}
```
VLAN 20 (Internal Services)
  → Internal Firewall
  → VLAN 30 (Forward Proxy)
  → VPN Gateway (optional)
  → External Firewall
  → Internet
```
{% endraw %}

This provides:

- Centralized outbound filtering  
- Logging and auditing  
- Optional country‑specific VPN exit nodes  
- Prevention of direct LAN → Internet access  

---

# 🚧 **6. Firewall Rule Flows**

### External Firewall (WAN ↔ DMZ)

- Allow: `443 → Reverse Proxy`
- Allow: `DMZ → Internet` (forward proxy only)
- Deny: all other inbound

### Internal Firewall (DMZ ↔ LAN)

- Allow: `Reverse Proxy → App Ports`
- Allow: `LAN → Forward Proxy:3128`
- Allow: `DNS VLAN 10 ↔ LAN/DMZ`
- Deny: all other DMZ ↔ LAN traffic

---

# 🔗 **7. Service‑to‑Service Flows**

### User → App

{% raw %}
```
Internet → Reverse Proxy → Internal Service
```
{% endraw %}

### App → Internet

{% raw %}
```
Internal Service → Forward Proxy → Internet
```
{% endraw %}

### App → Database

{% raw %}
```
Internal Service → Database (same VLAN 20)
```
{% endraw %}

### App → DNS

{% raw %}
```
Internal Service → VLAN 10 (Pi‑hole/Unbound)
```
{% endraw %}

---

# 🖥️ **8. Proxmox Node Placement**

{% raw %}
```
Proxmox Node 1
  - DMZ-Proxy-01 (VLAN 30)
  - DNS-01 (VLAN 10)

Proxmox Node 2
  - Apps-01 (VLAN 20)
  - DNS-02 (VLAN 10)
```
{% endraw %}

Both nodes trunk VLANs 10/20/30 from the physical topology.

---

# 🎯 **Purpose of This Page**

This page serves as the authoritative reference for:

- Understanding the homelab’s network architecture  
- Onboarding new contributors  
- Troubleshooting connectivity  
- Planning future expansions  
- Maintaining consistent security boundaries