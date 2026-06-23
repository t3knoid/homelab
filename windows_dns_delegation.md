---
title: "Windows DNS Delegation"
---

# **Windows DNS Delegation**

DNS delegation is necessary whenever a **subdomain is hosted outside the authoritative DNS server for the parent zone**. In this environment, the domain controller hosts the internal **refol.us** zone for Active Directory, but certain subdomains are managed externally on Cloudflare. Because Windows DNS is authoritative for the entire parent zone, it will **never forward queries for any name inside refol.us** unless a delegation explicitly tells it to.

A delegation creates a formal handoff inside the DNS hierarchy. It instructs the parent zone that:

> **“I am authoritative for refol.us, but the nameservers for delegated.refol.us are located elsewhere.”**

This ensures that:

- Queries for the external subdomain resolve correctly  
- The domain controller no longer returns NXDOMAIN for valid external records  
- Internal AD DNS remains authoritative only for the zones it actually manages  
- DNS behavior stays consistent with Internet standards and best practices  

Delegation is the required mechanism for cleanly separating **internal AD‑managed DNS** from **externally hosted subdomains**, while preserving correct resolution across the entire namespace.

---

## **Steps**

The following steps shows how to delegate a host inside the refol.us domain named, "delegated."

### **Enumerate Nameserver and IPs**

This example uses Cloudflare as the forwarding DNS.

{% raw %}
```
brenna.ns.cloudflare.com → 108.162.193.11
vick.ns.cloudflare.com   → 172.64.33.11
```
{% endraw %}

### **Delegate the subzone**

Add the delegation for each name server.

{% raw %}
```powershell
Add-DnsServerZoneDelegation `
    -Name "refol.us" `
    -ChildZoneName "delegated" `
    -NameServer "brenna.ns.cloudflare.com" `
    -IPAddress "108.162.193.11"
```
{% endraw %}

{% raw %}
```powershell
Add-DnsServerZoneDelegation `
    -Name "refol.us" `
    -ChildZoneName "delegated" `
    -NameServer "vick.ns.cloudflare.com" `
    -IPAddress "172.64.33.11"
```
{% endraw %}

---

### **Add nameserver records to the parent zone

This is optional but recommended. Again, execute the command for each nameserver.

{% raw %}
```powershell
Add-DnsServerResourceRecord -ZoneName "refol.us" -NS -Name "delegated" -NameServer "brenna.ns.cloudflare.com"
```
{% endraw %}

{% raw %}
```powershell
Add-DnsServerResourceRecord -ZoneName "refol.us" -NS -Name "delegated" -NameServer "vick.ns.cloudflare.com"
```
{% endraw %}

---

### **Add glue A records**

This is required for external nameservers. Again, execute the command for each nameserver.

{% raw %}
```powershell
Add-DnsServerResourceRecordA -ZoneName "refol.us" -Name "brenna.ns.cloudflare.com" -IPv4Address "108.162.193.11"
```
{% endraw %}

{% raw %}
```powershell
Add-DnsServerResourceRecordA -ZoneName "refol.us" -Name "vick.ns.cloudflare.com" -IPv4Address "172.64.33.11"
```
{% endraw %}

---

### **Verify delegation**

{% raw %}
```powershell
Get-DnsServerZoneDelegation -ZoneName "refol.us"
```
{% endraw %}

You should see two entries for the delegated zone.

---

### **Test resolution**

{% raw %}
```powershell
Clear-DnsServerCache -Force
ipconfig /flushdns
nslookup delegated.refol.us 192.168.20.251
```
{% endraw %}

You should now see Cloudflare answering instead of NXDOMAIN.