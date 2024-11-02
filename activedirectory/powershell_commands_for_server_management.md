# Powershell Commands for Server Management

- [Powershell Commands for Server Management](#powershell-commands-for-server-management)
  - [Change Administrator Password](#change-administrator-password)
  - [Show the available cmdlets in the ADDSDeployment module](#show-the-available-cmdlets-in-the-addsdeployment-module)
  - [Add a Domain User](#add-a-domain-user)
  - [Add User to Domain Admins Group](#add-user-to-domain-admins-group)
  - [List all Domain Administrators](#list-all-domain-administrators)
  - [Show Windows Features Installed](#show-windows-features-installed)
  - [Get specific computer that shows all properties](#get-specific-computer-that-shows-all-properties)
  - [Get all computer accounts using a filter](#get-all-computer-accounts-using-a-filter)
  - [Get Network Address](#get-network-address)
    - [Set Static IP Network Address](#set-static-ip-network-address)
    - [Set DNS](#set-dns)
  - [References](#references)


The following is a [list of PowerShell commands](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2022-ps) useful in administering Active Directory.

## Change Administrator Password
```powershell
net user administrator *
```

## Show the available cmdlets in the ADDSDeployment module

```powershell
Get-Command -Module ADDSDeployment
```

## Add a Domain User

**Prompt for a Password**

```powershell
New-ADUser -Name "Frank Refol" -GivenName "Frank" -Surname "Refol" -SamAccountName "frank" -UserPrincipalName "frank@refol.us" -AccountPassword(Read-Host -AsSecureString "Input Password") -Enabled $true
```

**Enter Password on Command-Line**

```powershell
New-ADUser -Name "Frank Refol" -GivenName "Frank" -Surname "Refol" -SamAccountName "frank" -UserPrincipalName "frank@refol.us" -AccountPassword (ConvertTo-SecureString "MySecurePassword123" -AsPlainText -Force) -Enabled $true
```

Enter a password when prompted.

## Add User to Domain Admins Group

```powershell
Add-ADGroupMember -Identity "Domain Admins" -Members frank
```

## Enable or Disable a User Account

```powershell
Enable-ADAccount -Identity "jdoe"
```

```powershell
Disable-ADAccount -Identity "jdoe"
```

## Set User Password to Never Expire

```powershell
Set-ADUser -Identity "username" -PasswordNeverExpires $true
```

## Verify PasswordNeverExpires Property

```powershell
Get-ADUser -Identity "username" | Select-Object PasswordNeverExpires
```

## Change a User Password

**Prompt for Password**

```powershell
Set-ADAccountPassword -Identity "jdoe" -NewPassword (Read-Host -AsSecureString "Input Password") -Reset
```

**Enter Password on Command-line**

```powershell
Set-ADAccountPassword -Identity "jdoe" -NewPassword (ConvertTo-SecureString "NewPassword123" -AsPlainText -Force) -Reset
```

## Get User Information

```powershell
Get-ADUser -Identity "jdoe" -Properties * | Select-Object Name, UserPrincipalName, SamAccountName, Enabled
```

## Delete a User Account

```powershell
Remove-ADUser -Identity "jdoe" -Confirm:$false
```

## List all Domain Administrators

```powershell
Get-ADGroupMember -Identity Administrators -Recursive
```

## Show Windows Features Installed

```powershell
get-windowsfeature
```

## Get specific computer that shows all properties

```powershell
 Get-ADComputer -Identity "ansible-0" -Properties *
 ```

 ## Get all computer accounts using a filter

 ```powershell
 Get-ADComputer -Filter *
 ```

## Get Network Address

```powershell
Get-NetIPInterface
```

### Set Static IP Network Address

If there is an existing static IP address set, remove it first with the following command.

```powershell
Remove-NetIPAddress
```
If DHCP is enabled, disable it first,

```powershell
Set-NetIPInterface
```

Use the following to set the new static IP address.

```powershell
New-NetIPaddress -InterfaceIndex 6 -IPAddress 192.168.2.251 -PrefixLength 24 -DefaultGateway 192.168.2.1
```

### Set DNS 

```bash
Set-DNSClientServerAddress –InterfaceIndex 12 -ServerAddresses 192.168.2.252,192.168.2.253
```

## References

- https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2022-ps