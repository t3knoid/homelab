# Active Directory

Active directory is provided using Windows Server 2022. Windows Server 2022 is installed without a GUI.

## Virtual Machine

### Properties

- Operating system: Windows Server 2022
- OS Disk: 32GB
- Memory: 4GB
- CPU: 3 sockets, 1 core
- Hostname: ad0
- IP address: 192.168.2.252
- DNS 1: 192.168.2.254
- DNS 2: 8.8.8.8

### Configuration

Windows Server 2022 Active Directory has been configured to work with Pi-Hole as the primary DNS server. In order to make this work, the following must be configured:

#### Enable NTP S

1. Open Registry Editor(regedit.exe)
Navigate to the following registry key: HKLM\System\CurrentControlSet\Services\W32Time\Parameters. To use a specific NTP source, modify the Type value to NTP.
2. Modify the NtpServervalue to contain the NTP server to synchronize time with followed by 0x8, for example 131.107.13.100,0x8. Multiple NTP servers must be space-delimited, for example 131.107.13.100,0x8 24.56.178.140,0x8
3. Open an administrative Command prompt and execute the following command: w32tm /config /update

1. https://learn.microsoft.com/en-us/services-hub/unified/health/remediation-steps-ad/configure-the-root-pdc-with-an-authoritative-time-source-and-avoid-widespread-time-skewEnable 
2. 
## Installing Active Directory

Installation and Configuration of Active Directory on Windows Server 2022 core requires using Powershell commands.

### Install Active Directory Services Role

Use the following powershell command to install the Active Directory services role.

```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
 ```

### Import the AD DS Deployment Module

```powershell
Import-Module ADDSDeployment
```

### Create the Domain Forest

```powershell
Install-ADDSForest -DomainName "refol.us" -InstallDNS:$False
```

Set the Safe Mode Administrator Password when prompted and confirm that the server will be a domain controller.

>PS C:\Users\Administrator> Install-ADDSForest -DomainName "refol.us"
SafeModeAdministratorPassword: **********
Confirm SafeModeAdministratorPassword: **********
>
>The target server will be configured as a domain controller and restarted when this operation is complete.
>Do you want to continue with this operation?
[Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "Y"):

The server will reboot.

### Enable NTP Server

```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\w32time\TimeProviders\NtpServer" -Name "Enabled" -Value 1 
```

Restart the NTP server
```powershell
Restart-Service w32Time 
```

### Configure Firewall to Allow NTP 

```powershell
New-NetFirewallRule `
-Name "NTP Server Port" `
-DisplayName "NTP Server Port" `
-Description 'Allow NTP Server Port' `
-Profile Any `
-Direction Inbound `
-Action Allow `
-Protocol UDP `
-Program Any `
-LocalAddress Any `
-LocalPort 123 
```

## Windows Admin Center

https://www.microsoft.com/en-us/evalcenter/download-windows-admin-center


## References

- [Windows 2022 guest best practices](https://pve.proxmox.com/wiki/Windows_2022_guest_best_practices)
- [Configure the Root PDC with an Authoritative Time Source and Avoid a Widespread Time Skew](https://learn.microsoft.com/en-us/services-hub/unified/health/remediation-steps-ad/configure-the-root-pdc-with-an-authoritative-time-source-and-avoid-widespread-time-skew)
- [Pi-Hole as Primary DNS with Active Directory](https://discourse.pi-hole.net/t/pihole-as-primary-dns-with-active-directory/58800/12)
- [Administer a Server Core server](https://learn.microsoft.com/en-us/windows-server/administration/server-core/server-core-administer)
  