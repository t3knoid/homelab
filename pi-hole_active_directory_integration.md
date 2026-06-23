---
title: "Pi-hole Active Directory Integration"
---

# 🌐 Pi-hole Active Directory Integration

This guide explains how to integrate **Pi-hole as the primary DNS resolver** with **Windows Active Directory (AD)**. It covers **Pi-hole configuration** and the **AD server-side steps** required for headless Windows environments.

---

## 1️⃣ Pi-hole Conditional Forwarding

| Setting           | Value            |
| ----------------- | ---------------- |
| Local network     | `192.168.20.0/24` |
| DHCP server IP    | `192.168.20.253`  |
| Local domain name | `refol.us`       |

> ✅ Ensures queries like `_ldap._tcp.refol.us` are resolved by the domain controller at `192.168.20.251`.

---

## 2️⃣ AD Server Configuration (Using PowerShell)

### a. Configure DNS Zones

{% raw %}
```powershell
Add-DnsServerPrimaryZone -Name "refol.us" -ZoneFile "refol.us.dns"
Add-DnsServerPrimaryZone -NetworkId "192.168.20.0/24" -ZoneFile "20.168.192.in-addr.arpa.dns" -ZoneType Primary
```
{% endraw %}

### b. Validate DNS Zones

{% raw %}
```powershell
Get-DnsServerZone | Where-Object {$_.ZoneType -eq "Primary"}
Get-DnsServerZone -Name "refol.us" | Format-List *
```
{% endraw %}

### c. Configure Forwarders

{% raw %}
```powershell
Add-DnsServerForwarder -IPAddress "8.8.8.8"
Add-DnsServerForwarder -IPAddress "1.1.1.1"
```
{% endraw %}

### d. Validate Forwarding

{% raw %}
```powershell
Get-DnsServerForwarder
Resolve-DnsName google.com -Server 127.0.0.1
Test-NetConnection -ComputerName 8.8.8.8 -Port 53
Get-WinEvent -LogName "DNS Server" -MaxEvents 50 | Format-Table TimeCreated, Id, Message -AutoSize
```
{% endraw %}

### e. Ensure Required SRV & A Records

{% raw %}
```powershell
Get-DnsServerResourceRecord -ZoneName "refol.us" -RRType "SRV"
Get-DnsServerResourceRecord -ZoneName "refol.us" -Name "dc01"
```
{% endraw %}

### f. Enable NTP Synchronization

{% raw %}
```powershell
w32tm /config /manualpeerlist:"time.windows.com,0x9" /syncfromflags:manual /reliable:YES /update
w32tm /resync /nowait
```
{% endraw %}

### g. Configure Firewall Rules

{% raw %}
```powershell
New-NetFirewallRule -DisplayName "Allow DNS TCP" -Direction Inbound -Protocol TCP -LocalPort 53 -Action Allow
New-NetFirewallRule -DisplayName "Allow DNS UDP" -Direction Inbound -Protocol UDP -LocalPort 53 -Action Allow
```
{% endraw %}

---

## 3️⃣ Additional Recommendations

* Whitelist AD domain in Pi-hole (`refol.us`, `dc01.refol.us`).
* Validate Pi-hole conditional forwarding:

{% raw %}
```bash
nslookup _ldap._tcp.refol.us 192.168.2.253
dig @192.168.20.253 _kerberos._tcp.refol.us SRV
```
{% endraw %}

* Monitor hostname resolution in Pi-hole logs.
* Backup Pi-hole configuration via Teleporter or Nebula Sync.

---

## 4️⃣ References

* [Pi-hole + Active Directory Discussion](https://discourse.pi-hole.net/t/pihole-as-primary-dns-with-active-directory/58800)
* [Active Directory DNS PowerShell Reference](https://learn.microsoft.com/en-us/powershell/module/dnsserver/)
* [Windows AD DNS Quick Reference Commands](windows_ad_dns_quick_reference_commands.md) 