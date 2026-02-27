---
title: "Gateway VLAN ACL Rules"
---

# Gateway VLAN ACL Rules

The following is a list of ACL rules required to control inter-VLAN traffic. It controls what traffic is allowed or disallowed between VLANs.

From the Omada Web UI, navigate Settings > Security > ACL > Gateway ACL.

---

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

