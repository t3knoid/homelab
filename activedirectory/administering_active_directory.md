# Administering Active Directory

The following provides different ways of managing Windows Server Core.

- [Server Manager](#server-manager)
- [MMC](#mmc)
- [Powershell](#powershell)
- [References](#references)

> [!IMPORTANT] 
> Execute the following powershell command to configure the Windows server firewall to allow remote management.

```powershell
Enable-NetFirewallRule -DisplayGroup "Windows Remote Management"
```
## Server Manager

Server Manager must be installed separately. In Windows 11, for example, open settings and navigate to the **Add an optional feature** window. Click the **View features** button and enable  the **RSAT: Server Manager** feature.

## MMC

Open the MMC application and navigate to **File > Add/Remove Snap-ins." Choose **Computer Management** from the Add or Remove Snap-ins window. Enter the server IP or host to manage.

## Powershell 

The [Powershell Commands for Server Management](powershell_commands_for_server_management.md) is a active list of Powershell commands to help with managing a Window Server Core from a Powershell command-line.

 ## References

 - https://learn.microsoft.com/en-us/windows-server/administration/server-core/server-core-administer
 - 