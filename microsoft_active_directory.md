# 🗂️ Microsoft Active Directory

**Active Directory (AD)** is hosted on the domain controller and provides centralized authentication, authorization, and directory services.  
For applications requiring Lightweight Directory Access Protocol (**LDAP**), **Active Directory Lightweight Directory Services (AD LDS)** is installed to expose LDAP endpoints.

---

## ⚙️ Installing Active Directory

Active Directory is deployed on **Windows Server 2022 Core**. Installation and configuration are performed using PowerShell commands.

### 1. Install AD Domain Services Role
```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
```

### 2. Import the AD DS Deployment Module
```powershell
Import-Module ADDSDeployment
```

### 3. Create the Domain Forest
```powershell
Install-ADDSForest -DomainName "refol.us" -InstallDNS:$False
```

During installation:
- You will be prompted to set the **Safe Mode Administrator Password**.  
- Confirm that the server will act as a domain controller.  
- The server will reboot automatically after configuration.

Example prompt:
```
SafeModeAdministratorPassword: **********
ConfirmSafeModeAdministratorPassword: **********
The target server will be configured as a domain controller and restarted when this operation is complete.
Do you want to continue with this operation?
[Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "Y"):
```

---

Here’s a rewritten **Configuration section** with a clear **Purpose & Impact** explanation, so it reads more like professional documentation and explains *why* each step matters, not just *how*:

---

## 🛠️ Configuration

After installing Active Directory, additional configuration ensures the domain controller operates reliably as the **authoritative source for time and DNS** within the environment. These steps are critical because **Kerberos authentication and domain replication depend on synchronized clocks and consistent name resolution**.

### ⏱️ Enable NTP Server  
**Purpose:**  
Active Directory relies on Kerberos, which enforces strict time tolerances (typically 5 minutes). If domain members drift out of sync, authentication failures and replication errors occur. Configuring the **Primary Domain Controller (PDC)** as an NTP server ensures all domain members share a consistent, trusted time source.  

**Impact:**  
- Prevents logon failures due to time skew.  
- Ensures replication and group policy updates occur smoothly.  
- Provides a single authoritative time source for both Windows and Linux hosts.  

**Implementation:**  
- Registry changes set the PDC to use external NTP servers.  
- PowerShell commands enable the NTP service and restart it.  
- Firewall rules allow inbound UDP 123 traffic so clients can query the domain controller for time.

---

### 🌐 DNS Integration with Pi‑Hole  
**Purpose:**  
Active Directory requires reliable DNS resolution for service records (SRV) and domain lookups. In this environment, **Pi‑Hole** is configured as the primary DNS server to provide ad‑blocking and enhanced visibility.  

**Impact:**  
- Domain members resolve AD services correctly while benefiting from Pi‑Hole’s filtering.  
- Ensures AD queries (e.g., `_ldap._tcp.refol.us`) are properly resolved.  
- Provides a balance between enterprise directory requirements and homelab network customization.  

---

### 🔥 Firewall Configuration for NTP  
**Purpose:**  
By default, Windows Firewall may block inbound NTP traffic. Opening UDP port 123 ensures that the domain controller can serve time to all clients.  

**Impact:**  
- Guarantees Linux and Windows hosts can synchronize against the domain controller.  
- Prevents authentication issues caused by blocked NTP queries.  

---

✅ **Summary:**  
The configuration section ensures the domain controller is not just installed, but hardened and reliable. By enabling NTP, integrating DNS with Pi‑Hole, and adjusting firewall rules, the AD environment gains stability, security, and interoperability across platforms.

---

## 🐧 Authenticate Linux Hosts

Linux systems can be joined to the Active Directory domain for centralized authentication.  
See: [Join an Ubuntu 24.04 Host to Active Directory Domain](join_an_ubuntu_2404_host_to_active_directory_domain.md).

---

## 📚 References

- [Windows 2022 guest best practices](https://pve.proxmox.com/wiki/Windows_2022_guest_best_practices)  
- [Configure the Root PDC with an Authoritative Time Source](https://learn.microsoft.com/en-us/services-hub/unified/health/remediation-steps-ad/configure-the-root-pdc-with-an-authoritative-time-source-and-avoid-widespread-time-skew)  
- [Pi‑Hole as Primary DNS with Active Directory](https://discourse.pi-hole.net/t/pihole-as-primary-dns-with-active-directory/58800/12)  
- [Administer a Server Core server](https://learn.microsoft.com/en-us/windows-server/administration/server-core/server-core-administer)  
- [Manage DNS Zones with PowerShell](https://learn.microsoft.com/en-us/windows-server/networking/dns/manage-dns-zones?tabs=powershell)  
