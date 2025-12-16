---
title: "Azure PowerShell (Az) Reference Guide"
---

# Azure PowerShell (Az) Reference Guide

This guide provides **documentation on using Azure PowerShell (Az module)** in your Home Lab. It includes installation, common commands, authentication, and uninstallation procedures.

---

## 1️⃣ Installation

The Az module can be installed using an Ansible playbook:

```shell
ansible-playbook -i inventory/ansible/inventory.ini -k playbooks/azure/deploy_azure_ps.yml
```

**Notes:**

* The playbook installs **PowerShell first**, then the Az module.
* Installation is **user-specific**: each user gets their own PowerShell environment.
* After installation, launch PowerShell using:

```shell
pwsh
```

---

## 2️⃣ Authentication

Interactive login is **not supported**. Device authentication must be used:

```powershell
Connect-AzAccount -UseDeviceAuthentication
```

**Instructions:**

1. You will receive an authentication code in PowerShell.
2. Open [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin) in a browser.
3. Enter the provided code.
4. After successful login, Azure will display your **Subscription Name** and **Tenant**.

---

## 3️⃣ Common Azure PowerShell Commands

| Task                          | Command                                                                                        | Notes                                               |
| ----------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **List all resource groups**  | `Get-AzResourceGroup`                                                                          | Useful to see your existing resource groups         |
| **List all virtual machines** | `Get-AzVM`                                                                                     | Can be filtered by resource group                   |
| **Create a Key Vault**        | `New-AzKeyVault -Name "<unique-name>" -ResourceGroupName "myResourceGroup" -Location "EastUS"` | Replace `<unique-name>` with a globally unique name |
| **Find VM-related cmdlets**   | `Get-Command -Verb Get -Noun AzVM* -Module Az.Compute`                                         | Helps discover compute-related commands             |
| **Help for any cmdlet**       | `Get-Help <cmdlet>`                                                                            | Displays usage examples and parameters              |

> ⚡ Tip: Most Az cmdlets follow the `Verb-AzNoun` pattern (e.g., `Get-AzVM`, `Remove-AzStorageAccount`).

---

## 4️⃣ Uninstallation

To remove the Az module and all dependencies:

1. Enumerate installed Az modules:

```powershell
($AzVersions |
  ForEach-Object {
    Import-Clixml -Path (Join-Path -Path $_.InstalledLocation -ChildPath PSGetModuleInfo.xml)
  }).Dependencies.Name | Sort-Object -Descending -Unique -OutVariable AzModules
```

2. Uninstall all modules:

```powershell
$AzModules |
  ForEach-Object {
    Remove-Module -Name $_ -ErrorAction SilentlyContinue
    Write-Output "Attempting to uninstall module: $_"
    Uninstall-Module -Name $_ -AllVersions
  }
```

3. Remove the Az module itself:

```powershell
Remove-Module -Name Az -ErrorAction SilentlyContinue
Uninstall-Module -Name Az -AllVersions
```

> ⚡ Caution: Only uninstall if no scripts rely on Az modules.

---

## 5️⃣ References

* [Get started with Azure PowerShell](https://learn.microsoft.com/en-us/powershell/azure/get-started-azureps?view=azps-14.1.0)
* [Azure PowerShell Key Vault Documentation](https://learn.microsoft.com/en-us/powershell/azure/get-started-azureps?view=azps-14.1.0#find-commands)
* [Uninstall Azure PowerShell](https://learn.microsoft.com/en-us/powershell/azure/uninstall-az-ps?view=azps-14.1.0)

