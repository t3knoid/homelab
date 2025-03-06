# Powershell Commands for Server Management

- [Change Administrator Password](#change-administrator-password)
- [Show the available cmdlets in the ADDSDeployment module](#show-the-available-cmdlets-in-the-addsdeployment-module)
- [Add a Domain User](#add-a-domain-user)
- [Add User to Domain Admins Group](#add-user-to-domain-admins-group)
- [Enable or Disable a User Account](#enable-or-disable-a-user-account)
- [Set User Password to Never Expire](#set-user-password-to-never-expire)
- [Verify PasswordNeverExpires Property](#verify-passwordneverexpires-property)
- [Change a User Password](#change-a-user-password)
- [Check if a user has been locked out](#check-if-a-user-has-been-locked-out)
  - [Get more information of user lock out](#get-more-information-of-user-lock-out)
- [Get a List of Users and their Respective Password Expiry Dates](#get-a-list-of-users-and-their-respective-password-expiry-dates)
- [Get User Information](#get-user-information)
- [Delete a User Account](#delete-a-user-account)
- [List all Domain Administrators](#list-all-domain-administrators)
- [Show Windows Features Installed](#show-windows-features-installed)
- [Get specific computer that shows all properties](#get-specific-computer-that-shows-all-properties)
- [Get all computer accounts using a filter](#get-all-computer-accounts-using-a-filter)
- [Get Network Address](#get-network-address)
- [Set Static IP Network Address](#set-static-ip-network-address)
- [Set DNS](#set-dns)
- [Get All Groups](#get-all-groups)
- [Add an Active Directory Group](#add-an-active-directory-group)
- [Add Users to a Group](#add-users-to-a-group)
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
Get-ADUser -Identity "username" -Properties PasswordNeverExpires | Select-Object PasswordNeverExpires
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

## Check if a user has been locked out

```powershell
Get-ADUser -Identity <username> -Properties LockedOut | Select-Object LockedOut
```

This will return True if the account is locked, and False if it is not.

### Get more information of user lock out

```powershell
Get-ADUser -Identity <username> -Properties * | Select-Object LockedOut, AccountLockoutTime, BadLogonCount
```

## Get a List of Users and their Respective Password Expiry Dates

The following lists users whose passwords have an expiration.

```powershell
Get-ADUser -filter {Enabled -eq $True -and PasswordNeverExpires -eq $False} –Properties "DisplayName", "msDS-UserPasswordExpiryTimeComputed" |
Select-Object -Property "Displayname",@{Name="ExpiryDate";Expression={[datetime]::FromFileTime($_."msDS-UserPasswordExpiryTimeComputed")}}
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

## Set Static IP Network Address

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

## Set DNS 

```powershell
Set-DNSClientServerAddress –InterfaceIndex 12 -ServerAddresses 192.168.2.252,192.168.2.253
```

## Get All Groups

```powershell
Get-ADGroup -Filter * | Select-Object Name
```

## Add an Active Directory Group

```powershell
New-ADGroup -Name "GroupName" -SamAccountName "GroupName" -GroupScope Global -GroupCategory Security
```

## Add Users to a Group

```powershell
Add-ADGroupMember -Identity SvcAccPSOGroup -Members SQL01, SQL02
```

## References

- https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2022-ps