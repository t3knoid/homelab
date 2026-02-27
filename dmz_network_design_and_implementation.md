---
title: "DMZ Network Design and Implementation"
---

# DMZ Network Design and Implementation

## Purpose

This page documents the design and implementation of a **DMZ (Demilitarized Zone)** used to isolate public-facing services from the internal LAN. The DMZ hosts an **NGINX reverse proxy** running as a VM on Proxmox, while backend services remain protected on the internal network.

The design prioritizes:
- Network-level isolation
- Reduced blast radius in the event of compromise
- Clear trust boundaries
- Alignment with production-grade infrastructure patterns

---

## Environment Summary

| Component | Description |
|--------|-------------|
| Router / Firewall | TP-Link Omada Router |
| Switching | Omada-managed switches |
| Virtualization | Proxmox VE |
| Reverse Proxy | NGINX (VM) |
| Backend Services | Proxmox VMs |
| LAN Subnet | `192.168.2.0/24` |
| DMZ Subnet | `192.168.10.0/24` |

DHCP and firewalling are handled by the Omada router.

---

## High-Level Architecture

### Logical Network Layout

{% raw %}
```text
                          Internet
                              |
                              |
                     +------------------+
                     |   Omada Router   |
                     |  Firewall + DHCP |
                     +------------------+
                              |           
                              |          
                 VLAN 10 (DMZ)|
               192.168.10.0/24|
                              |
                              | 
                      +----------------+ 
                      |  NGINX Reverse |
                      |     Proxy VM   |
                      |  192.168.10.10 |
                      +----------------+ 
                              |
          Explicitly allowed  | 
          DMZ → LAN traffic   | 
                              v 
                      +----------------+
                      |  Backend VM A  |
                      | 192.168.20.211 |
                      | HTTPS / 443    |
                      +----------------+
```
{% endraw %}

### Traffic Policy Summary

- **WAN → DMZ:** HTTP/HTTPS only
- **WAN → LAN:** Denied
- **DMZ → LAN:** Denied by default, explicitly allowed per service
- **LAN → DMZ:** Administrative and monitoring access only

---

## Design Principles

- Routing and security boundaries are enforced **outside Proxmox**
- Proxmox does not act as a router
- Public-facing services reside only in the DMZ
- Backend services are never directly Internet-accessible
- Firewall rules are explicit, minimal, and auditable

---

## VLAN & IP Design

| Network | VLAN | Subnet | Gateway |
|--------|------|--------|--------|
| VLAN1 | 1 | 192.168.2.0/24 | 192.168.2.1 |
| VLAN20 | 20 | 192.168.20.0/24 | 192.168.20.1 |
| VLAN30 | 30 | 192.168.30.0/24 | 192.168.30.1 |
| VLAN40 | 40 | 192.168.40.0/24 | 192.168.40.1 |
| VLAN50 | 50 | 192.168.50.0/24 | 192.168.50.1 |
| DMZ | 10 | 192.168.10.0/24 | 192.168.10.1 |

- DHCP enabled on both networks
- DHCP reservations recommended for infrastructure VMs

---

## Omada Switch Configuration

### Proxmox Host Uplink

- Port Mode: **Trunk**
- Allowed VLANs: `1 (LAN), 10 (DMZ)`
- Native VLAN: `1`
- Tagged VLANs: `10`

This ensures VLAN tagging is preserved from the switch through Proxmox to each VM.

---

## Proxmox Network Configuration

### Virtual Bridge Strategy (Recommended)

A single VLAN-aware bridge is used:

{% raw %}
```text

vmbr0
└── Physical NIC (eno1)
└── VLAN aware: Yes

```
{% endraw %}

### VM VLAN Assignment

| VM Type | VLAN | NIC Count |
|------|------|----------|
| NGINX Reverse Proxy | 10 (DMZ) | 1 |
| Backend Services | 20 (LAN) | 1 |

> VMs must not be dual-homed across LAN and DMZ.

---

### Proxmox Placement Diagram

{% raw %}
```text
                Omada Switch (Trunk Port)
 VLAN50 (Physical Control Plane) | VLAN 10 (DMZ)
                                 |
                        +----------------+
                        | Proxmox Host   |
                        | vmbr0 (VLAN50) |
                        +----------------+
                          |            |
                  VLAN 20 |            | VLAN 10
                          |            |
              Backend Service VMs   NGINX Proxy VM
```
{% endraw %}

---

## Reverse Proxy (NGINX) Role

### Network Characteristics

- VLAN: 10 (DMZ)
- IP: `192.168.10.10` (reserved)
- Gateway: `192.168.10.1`
- Single network interface

### Responsibilities

- Terminate inbound HTTP/HTTPS traffic
- Enforce TLS
- Proxy traffic to backend LAN services
- Act as the only public ingress point

### Required Proxy Headers

{% raw %}
```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```
{% endraw %}

---

## Firewall Policy (Omada Router)

### WAN → DMZ

**Allow**

* TCP 80
* TCP 443

**Deny**

* All other inbound traffic

---

### DMZ → LAN

**Default:** Deny all

**Explicit Allow Rules (examples):**

| Source        | Destination  | Port | Protocol |
| ------------- | ------------ | ---- | -------- |
| 192.168.10.10 | 192.168.2.20 | 443  | TCP      |
| 192.168.10.10 | 192.168.2.30 | 8080 | TCP      |

Rules must be narrowly scoped and service-specific.

---

### LAN → DMZ

**Allow**

* SSH
* HTTPS
* Monitoring traffic
* ICMP (optional)

---

## NAT / Port Forwarding

### WAN → DMZ

| WAN Port | Protocol | DMZ IP        | DMZ Port |
| -------- | -------- | ------------- | -------- |
| 80       | TCP      | 192.168.10.10 | 80       |
| 443      | TCP      | 192.168.10.10 | 443      |

No port forwarding to LAN networks is permitted.

---

## Security Hardening

### Router / Network

* Disable UPnP
* Disable consumer-style “DMZ host” features
* Enable logging for DMZ → LAN denies

### NGINX VM

* SSH key-based authentication only
* Fail2ban enabled
* Automatic security updates
* No file-sharing or auxiliary services installed

### Proxmox

* Management interfaces accessible from LAN only
* Optional Proxmox firewall rules for defense-in-depth
* No host-level routing between VLANs

---

## Risk Containment

* A compromised reverse proxy is confined to the DMZ
* Lateral movement into LAN requires firewall rule exploitation
* Backend services remain shielded from direct Internet access
* All trust boundaries are explicit and documented

---

## Implementation Notes

* Firewall rule order is critical (allow rules must precede denies)
* VLAN tagging must be validated end-to-end
* Avoid temporary “any/any” rules during testing
* Document each DMZ → LAN rule with justification

