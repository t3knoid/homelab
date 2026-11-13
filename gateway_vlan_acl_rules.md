---
title: "Gateway VLAN ACL Rules"
---

# Gateway VLAN ACL Rules

The following is a list of ACL rules required to control inter-VLAN traffic. It controls what traffic is allowed or disallowed between VLANs.

From the Omada Web UI, navigate Settings > Security > ACL > Gateway ACL.

---

## **Allow** HTTP/s from Frontend to Backend Proxy Servers

Ingress traffic should only go through the frontend reverse proxy server. This rule allows traffic from the frontend to backend reverse proxy servers.

**Create ACL: "Allow https from rproxy-0 to backend proxy servers"**

| Field | Value |
|-------|--------|
| **Policy** | Allow |
| **Source Type** | IP Group |
| **Source IP Subnets** | 192.168.30.210/32 |
| **Source IP Ports** | 443, 80 |
| **Destination Type** | IP-Port Group |
| **Destination IP Subnets** | 192.168.20.211/32, 192.168.20.212/32 |
| **Destination Ports** | 443, 80 |
| **Protocols** | TCP |
| **Binding Type** | Network |
 
---

## **Allow** HTTP/s from Backend Proxy Servers to Infrastructure VLAN (20)

Ingress traffic goes through rproxy-1 or rproxy-2 to the application hosts.

**Create ACL: “Allow HTTP from Backend Proxy Servers to Infrastructure”**

| Field | Value |
|-------|--------|
| **Policy** | Allow |
| **Source Type** | IP-Port Group |
| **Source IP Subnets** | 192.168.29.211/32, 192.168.20.212/32 |
| **Source IP Ports** | 443, 80 |
| **Destination** | VLAN 20 (Infrastructure) |
| **Protocols** | TCP |
| **Binding Type** | Network |

This rule should appear **before** default deny rules.

## **Deny IoT VLAN (40) Access to Internal Networks**

IoT devices are untrusted and should not reach Client, Infrastructure, or DMZ networks.

**Create ACL: “Deny IoT to Internal”**

| Field | Value |
|-------|--------|
| **Policy** | Deny |
| **Source** | VLAN 40 (IoT Devices) |
| **Destination** | VLAN 10 (Client), VLAN 20 (Infrastructure), VLAN 30 (DMZ) |
| **Protocols** | All |
| **Binding Type** | Network |

This rule should appear **after** any IoT exceptions but **before** default allow rules.

---

## **Allow Bi‑Directional Access Between HDHomeRun (VLAN 40) and Client LAN (VLAN 10)**

The HDHomeRun tuner lives in VLAN 40 but must communicate with client devices for discovery and streaming.

Create **two** ACLs above the IoT deny rule:

### **ACL: “Allow Client → HDHomeRun”**

| Field | Value |
|-------|--------|
| **Policy** | Allow |
| **Source** | VLAN 10 (Client LAN) |
| **Destination** | HDHomeRun IP (in VLAN 40) |
| **Protocols** | All |
| **Binding Type** | IP Address |

### **ACL: “Allow HDHomeRun → Client”**

| Field | Value |
|-------|--------|
| **Policy** | Allow |
| **Source** | HDHomeRun IP (VLAN 40) |
| **Destination** | VLAN 10 (Client LAN) |
| **Protocols** | All |
| **Binding Type** | IP Address |

These two rules enable tuner discovery and streaming while keeping the rest of IoT isolated.

---

## **Allow HDHomeRun Access to Plex or Home Assistant**

If required:

### **HDHomeRun → Plex (VLAN 30)**  
Allows Plex to ingest live TV streams.

### **HDHomeRun → Home Assistant (VLAN 20)**  
Allows HA to integrate with the tuner.

Both should be placed **above** the IoT deny rule.

---

## **ACL Rule Order (Critical)**

The ACL list should appear in this order:

1. Allow Client → HDHomeRun  
2. Allow HDHomeRun → Client  
3. *(Optional)* Allow HDHomeRun → Plex  
4. *(Optional)* Allow HDHomeRun → Home Assistant  
5. **Deny IoT → Internal Networks**  
6. Default allow to WAN (implicit)

This ensures exceptions are honored before the global deny.

---

## **Summary of Required Port Roles**

### **Access Ports (Untagged via PVID)**
- **VLAN 10:** Client devices  
- **VLAN 20:** Servers, hypervisors, NAS, APs  
- **VLAN 30:** DMZ hosts
- **VLAN 40:** IoT devices  
- **VLAN 50:** Proxmox Hypervisor and Storage NAS

### **Trunk Ports (Tagged)**

- ER605 → TL‑SG2428P  
- TL‑SG2428P → SG2008  

All VLANs tagged on these ports.

