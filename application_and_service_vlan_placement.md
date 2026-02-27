---
title: "Application and Service VLAN Placement"
---

# Application and Service VLAN Placement

*Applies to: All Proxmox‑hosted VMs and containers*  
*Purpose: Define the correct VLAN for each service based on security, exposure, and function.*

The VLAN design establishes three core roles:

- **VLAN 20 – Infrastructure**  
  Internal services, automation, monitoring, storage, hypervisors, DNS, databases, orchestration.

- **VLAN 30 – DMZ**  
  Public‑facing or internet‑exposed services (reverse proxies, externally reachable apps).

- **VLAN 10 – Client LAN**  
  End‑user devices (Windows 11 desktops, laptops, phones).

Below is the authoritative placement for each resource.

---

# **1. Infrastructure Services (VLAN 20)**  
These systems must remain internal, trusted, and reachable by hypervisors, storage, and automation tools.

### **Automation & Orchestration**
- **ansible‑0, ansible‑1** → VLAN 20  
- **semaphore‑0** → VLAN 20  
- **jenkins‑0** → VLAN 20  

### **Directory, DNS, and Core Services**
- **ad‑0 (Active Directory)** → VLAN 20  
- **dns‑0, dns‑1 (Pi‑hole / Unbound)** → VLAN 20  

### **Monitoring & Observability**
- **prometheus‑0** → VLAN 20  
- **grafana‑0** → VLAN 20  

### **Databases**
- **pg‑0, pg‑1, pg‑2, pg‑3, pg‑4** → VLAN 20  
  (Postgres clusters should never live in DMZ or client networks.)

### **Home Automation**
- **ha‑0 (Home Assistant)** → VLAN 20  
  (Internal automation, API integrations, MQTT, etc.)

### **Media Automation Stack**
These apps are *not* externally exposed and should remain internal:

- **sonarr‑0** → VLAN 20  
- **radarr‑0** → VLAN 20  
- **lidarr‑0** → VLAN 20  
- **tautulli‑0** → VLAN 20  
- **ombi‑0** → VLAN 20  
  (Ombi *can* be exposed externally, but in your setup it is not. If that changes, it moves to VLAN 30.)

### **Internal Applications**
- **redmine‑0** → VLAN 20  

---

# **2. DMZ Services (VLAN 30)**  
These services are externally reachable or sit in front of public‑facing applications.

### **Reverse Proxies**
- **rproxy‑0, rproxy‑1, rproxy‑2** → VLAN 30  
  (These terminate external traffic and forward internally.)

### **Externally Accessible Applications**
- **plex‑0** → VLAN 30  
  (Required because WAN:32400 is forwarded to plex‑0.)
- **minecraft‑1** → VLAN 30  
  (Required because WAN:19132 is forwarded to minecraft-1.)

---

# **3. Client Systems (VLAN 10)**  
These behave like end‑user devices.

- **win11‑0** → VLAN 10  
  (Your Windows 11 VM is a client workload, not infrastructure.)

If you spin up additional desktop OS VMs for testing, they also belong here.

---

# **4. Summary Table**

| Service / VM | VLAN | Reason |
|--------------|-------|--------|
| ansible‑0 / ansible‑1 | 20 | Automation, internal orchestration |
| rproxy‑0 / rproxy‑1 / rproxy‑2 | 30 | Public‑facing reverse proxies |
| ad‑0 | 20 | Directory services must remain internal |
| lidarr‑0 | 20 | Internal media automation |
| sonarr‑0 | 20 | Internal media automation |
| radarr‑0 | 20 | Internal media automation |
| tautulli‑0 | 20 | Internal monitoring |
| ombi‑0 | 20 | Internal request portal (not externally exposed) |
| dns‑0 / dns‑1 | 20 | Internal DNS / Pi‑hole |
| pg‑0 … pg‑4 | 20 | Databases must remain internal |
| semaphore‑0 | 20 | CI/CD orchestration |
| prometheus‑0 | 20 | Monitoring |
| grafana‑0 | 20 | Dashboards |
| minecraft‑1 | 30 | Externally exposed game server |
| jenkins‑0 | 20 | CI/CD |
| redmine‑0 | 20 | Internal project management |
| ha‑0 | 20 | Home automation |
| plex‑0 | 30 | Externally accessible via port‑forward |
| win11‑0 | 10 | Client OS |

---

# **5. Why This Layout Works**

- **Infrastructure (VLAN 20)** stays protected and reachable only by trusted systems.  
- **DMZ (VLAN 30)** isolates anything exposed to the internet.  
- **Clients (VLAN 10)** remain separate from servers and automation.  
- **Proxmox VMs tag their own VLANs**, keeping switch configuration simple and consistent.
