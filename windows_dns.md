---
title: "Windows DNS"
---

# 🧩 Windows DNS  

Windows DNS (running on the Domain Controller) is the authoritative internal DNS service for the Active Directory domain. It provides the DNS infrastructure required for domain‑joined systems, authentication, service discovery, and reverse lookups.

---

## 🟦 Windows DNS Responsibilities

Windows DNS hosts and maintains all DNS zones required for Active Directory:

### **Forward Lookup Zones**
- `refol.us` — primary AD domain zone  
- `_msdcs.refol.us` — forest‑wide service location zone  

These zones contain:
- A/AAAA records for domain‑joined hosts  
- SRV records for LDAP, Kerberos, GC, and DC discovery  
- CNAMEs and other service records  
- Dynamically updated records from DHCP and domain‑joined clients  

### **Reverse Lookup Zones**
Windows DNS also manages reverse lookup zones such as:

{% raw %}
```
20.168.192.in-addr.arpa
```
{% endraw %}

These zones provide:
- PTR records for IP → hostname mapping  
- Reverse lookups used by AD, logging systems, and management tools  

### **Delegated Subzones**

When a subdomain is hosted outside the Domain Controller’s DNS—for example, on Cloudflare—Windows DNS must be told to hand off authority for that subzone. This is done through **DNS delegation**. Without a delegation, the DC assumes full ownership of the entire parent zone and returns NXDOMAIN for valid external records. Delegation ensures queries for the external subdomain are routed to the correct nameservers while the DC remains authoritative only for the parent zone.

👉 See: **[Windows DNS Delegation](windows_dns_delegation.md)**

### **Dynamic DNS Integration**
Windows DNS supports:
- Secure dynamic updates from domain‑joined machines  
- DHCP‑triggered DNS updates  
- Automatic registration of DC service records  

This functionality is essential for:
- Kerberos authentication  
- Group Policy processing  
- Domain controller location  
- AD replication  

---

## 🟩 Why Windows DNS Must Remain Authoritative

Active Directory depends on DNS for nearly every operation.  
Windows DNS is the **only** service that:

- Understands AD SRV record requirements  
- Supports secure dynamic updates  
- Maintains authoritative AD zones  
- Integrates with domain controllers  
- Provides correct reverse lookup behavior  
- Hosts `_msdcs` and other AD‑critical subzones  

No external DNS resolver (public or local) can replace these functions.

---

## 🟧 Relationship With Pi‑hole

Pi‑hole acts as the **first‑hop DNS resolver** for clients on the network, but it is **not** authoritative for the AD domain and does not maintain internal DNS records.

Because Windows DNS is authoritative for `refol.us` and its subzones, Pi‑hole must forward all queries for the internal domain to the Domain Controller.

This ensures:

- Internal hostnames resolve correctly  
- AD service records are reachable  
- Kerberos and LDAP discovery works  
- Reverse lookups return the correct PTRs  
- DHCP dynamic DNS updates remain functional  

Pi‑hole handles filtering and upstream resolution for public domains, while Windows DNS handles authoritative resolution for internal domains.

👉 See: **[Pi-hole Active Directory Integration](pi-hole_active_directory_integration.md)**

---

## 🟨 Conditional Forwarding Requirement

To maintain proper AD functionality, Pi‑hole must be configured to **conditionally forward** the internal domain:

{% raw %}
```
refol.us → <Domain Controller IP>
```
{% endraw %}

This preserves the correct DNS flow:

{% raw %}
```
Clients → Pi‑hole → Windows DNS (authoritative for refol.us)
```
{% endraw %}

Windows DNS then provides the authoritative internal answer, while Pi‑hole continues to manage all external DNS traffic.