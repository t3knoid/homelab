# LDAP

The following provides an overview on installing LDAP in Windows 2022 Core.

## Install Active Directory Lightweight Directory Services

```powershell
Install-WindowsFeature -Name ADLDS -IncludeAllSubFeature -IncludeManagementTools
```

## Creating an unattended install of a new AD LDS instance 

The following uses the adaminstall.exe tool to install an unattended install of a new AD LDS instance.

### Create an Answer File
The first step is to create an answer file.

```ini
[ADAMInstall]
; The following line specifies to install a unique ADAM instance.
InstallType=Unique
; The following line specifies the name to be assigned to the new instance.
InstanceName=MyFirstInstance
; The following line specifies the communications port to use for LDAP.
LocalLDAPPortToListenOn=389
; The following line specifies an application partition to create
NewApplicationPartitionToCreate="o=microsoft,c=us"
; The following line specifies the directory to use for ADAM data files.
DataFilesPath=C:\Program Files\Microsoft ADAM\instance1\data
; The following line specifies the directory to use for ADAM log files.
LogFilesPath=C:\Program Files\Microsoft ADAM\instance1\data
; The following line specifies the .ldf files to import into the ADAM schema.
ImportLDIFFiles="ms-inetorgperson.ldf" "ms-user.ldf"
```

```powershell
Start-Process -FilePath "$env:SystemRoot\ADAM\adaminstall.exe" -ArgumentList
"/answer:C:\install_adam_example.txt" -WindowStyle Hidden 
```



## References

- https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc816778(v=ws.10)?redirectedfrom=MSDN
- https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature?view=windowsserver2022-ps
- https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc816774(v=ws.10)?redirectedfrom=MSDN
- 