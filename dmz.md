---
title: "DMZ"
---

# DMZ

A **DMZ (Demilitarized Zone)** is a network segment that sits between the internet and your internal LAN. It provides a layer of security by **isolating public-facing services** from sensitive internal systems.

In the home lab, the DMZ is used to host **NGINX reverse proxy VMs**. These proxies handle all external traffic and forward requests to backend servers on the LAN in a controlled, secure way.

For full details, configurations, and implementation steps, see the detailed page: [DMZ Network Design and Implementation](dmz_network_design_and_implementation.md).

---

## Simplified Network Overview

{% raw %}
```
      Internet
          |
  +----------------+
  | Omada Router   |
  | Firewall + DHCP|
  +----------------+
          |
      VLAN 10 (DMZ)
   192.168.10.0/24
          |
  +----------------+
  | NGINX Proxy VM |
  | 192.168.10.10  |
  +----------------+
          |
 Explicitly allowed DMZ → LAN traffic
          |
      VLAN 1 (LAN)
   192.168.2.0/24
          |
  +----------------+ 
  |   Backend VM   | 
  |   HTTP / 80    | 
  +----------------+ 
```
{% endraw %}

---

## Key Points

- **External traffic** flows only to the DMZ.
- **Reverse proxy** controls which internal servers can be reached.
- **Direct WAN → LAN** access is blocked.
- Internal traffic between the DMZ and LAN is **explicitly allowed by firewall rules**.
