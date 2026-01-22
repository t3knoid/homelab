---
title: "VLAN Creation Procedure"
---

# VLAN Creation Procedure

**Applies to:** ER605 Gateway, TL‑SG2428P, SG2008  
**Source Reference:** TP‑Link “How to configure VLAN on Omada Gateway”

---

# **1. VLAN Definitions (Use These Values)**

| VLAN | Name | Subnet | Gateway | DHCP Range | DNS |
|------|------|---------|----------|-------------|------|
| **10** | Client LAN | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.50–199 | 192.168.20.10 (Pi‑hole) |
| **20** | Infrastructure | 192.168.20.0/24 | 192.168.20.1 | 192.168.20.50–199 | 192.168.20.10 |
| **30** | DMZ | 192.168.30.0/24 | 192.168.30.1 | 192.168.30.50–199 | 192.168.20.10 |
| **99** | Legacy LAN | 192.168.2.0/24 | 192.168.2.1 | 192.168.2.50–199 | 192.168.20.10 |

---

# **2. Create Each VLAN in Omada**

## **2.1 Create the VLAN as a LAN Network**  
*(Matches Step 1 on the TP‑Link page: “Create a LAN with VLAN ID”)*

For each VLAN:

1. Navigate to:  
   **Settings → Wired Networks → LAN → Networks → Create New LAN**

2. Fill in the fields using the table above:  
   - **Name** (e.g., “Client LAN”)  
   - **VLAN ID** (10, 20, 30, 99)  
   - **Gateway/Subnet** (e.g., 192.168.10.1 / 24)  
   - **DHCP Server**  
     - Start: e.g., 192.168.10.50  
     - End: e.g., 192.168.10.199  
   - **DNS**  
     - Primary: **192.168.20.10 (Pi‑hole)**  
     - Secondary: 1.1.1.1  

3. Under **Port Assignment**, select the ports that should carry this VLAN.  
   - Omada will add the VLAN **tagged** by default.

4. Save.

Repeat for VLANs **10, 20, 30, 99**.

---

# **3. Configure Access Ports (Set PVID)**  
*(Matches Step 2 on the TP‑Link page: “Set PVID for ports”)*

Omada behavior from the page:

- Adding a VLAN to a port = **tagged** by default  
- Setting the **PVID** = makes that VLAN **untagged**  
- Default LAN is always untagged and cannot be changed

### **Procedure**
1. Go to:  
   **Devices → Gateway → Ports**  
   or  
   **Devices → Switch → Ports**

2. For each port that should be an **access port**:
   - Set **PVID = VLAN ID**  
   - Example:  
     - Client port → PVID 10  
     - AP port → PVID 20  
     - DMZ port → PVID 30  
     - Migration ports → PVID 99  

This converts the port from tagged to untagged for that VLAN.

---

# **4. Configure Trunk Ports (Uplinks)**  
*(Based on the page’s explanation of tagged VLAN behavior)*

For uplinks:

- ER605 → TL‑SG2428P  
- TL‑SG2428P → SG2008  

### **Procedure**
1. Add VLANs **10, 20, 30, 99** to the port  
2. Leave the **PVID unchanged**  
3. This keeps all VLANs **tagged**, which is correct for trunk links

---

# **5. WAN VLAN Tagging (If Required by ISP)**  
*(Matches “WAN VLAN Tagging” section on the page)*

Only needed if your ISP requires it.

1. Go to:  
   **Settings → Wired Networks → Internet → Advanced Settings**

2. Enable **802.1Q Tag**  
3. Enter the ISP‑provided VLAN ID  

If your ISP does not require tagging, leave this disabled.

---

# **6. Summary of Required Port Roles**

### **Access Ports (Untagged via PVID)**
- **VLAN 10:** Client devices  
- **VLAN 20:** Servers, hypervisors, NAS, APs  
- **VLAN 30:** DMZ hosts  
- **VLAN 99:** Temporary migration ports  

### **Trunk Ports (Tagged)**
- ER605 → TL‑SG2428P  
- TL‑SG2428P → SG2008  

All VLANs tagged on these ports.

---

# **7. Migration Notes**
- Start by placing all ports in **VLAN 99** (Legacy LAN)  
- Migrate APs first (to VLAN 20)  
- Migrate servers next (to VLAN 20)  
- Migrate DMZ services (to VLAN 30)  
- Migrate clients last (to VLAN 10)  
- Remove VLAN 99 when migration is complete  
