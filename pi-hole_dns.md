---
title: "Pi-hole DNS"
---

# 🌐 Pi-hole DNS

[Pi-hole](https://pi-hole.net/) is a lightweight DNS solution that provides **network-wide ad blocking** and centralized DNS management. It is particularly useful in homelab environments where visibility, redundancy, and integration with directory services are important.

In this environment, Pi-hole is deployed with [**multiple instances**](https://github.com/t3knoid/ansible/blob/main/inventory/dns/inventory.ini) to provide resilient DNS resolution and consistent filtering across the network.

---

## 🧠 Architecture Overview

* Pi-hole operates as the **primary DNS resolver** for LAN clients
* Multiple Pi-hole instances are deployed for **high availability**
* Configuration is synchronized automatically using **Nebula Sync**
* Windows Active Directory remains authoritative for AD-specific DNS records

{% raw %}
```plaintext
           +------------------+
           |   LAN Client     |---------Failover----------+
           +------------------+                           |
                     |                                    |
                     | DNS Query                          |
                     v                                    v
           +------------------+                 +------------------+
           | Primary Pi-hole  | <-------------> | Secondary Pi-hole|
           |  (Filtering +    |   Nebula-sync   |  (HA Node)       |
           |   Gravity)       |                 +------------------+
           +------------------+
                    |
                    |
               AD-specific?
                |      |
               Yes     No
       +-------------+-------------+
       |                           |
       v                           v
+--------------------+   +-----------------+
|  AD DNS Server     |   | Upstream DNS    |
| (Domain Controller)|   | (e.g., 8.8.8.8) |
+--------------------+   +-----------------+
       |
       v
+------------------+
| Pi-hole Logs / UI|
+------------------+
```
{% endraw %}

This design provides:

* DNS redundancy and failover
* Centralized filtering policy
* Minimal manual configuration
* Predictable rebuild and recovery behavior

---

## ⚙️ Installation & Deployment

Pi-hole is **installed and configured exclusively using Ansible**.

### Ansible Deployment

* **Playbook:**
  [playbooks/dns/deploy_pihole.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/deploy_pihole.yml)
 

* **Deployment responsibilities include:**

  * Pi-hole installation
  * Base configuration and networking
  * Gravity and blocklist initialization
  * Environment-specific DNS configuration
  * Idempotent rebuild support

> ⚠️ **Do not install or reconfigure Pi-hole manually**
> All Pi-hole nodes must be deployed or rebuilt through Ansible to avoid configuration drift.

---

## 🏢 Integration with Active Directory

Pi-hole must forward AD-specific queries to the domain controller.  
Detailed configuration, validation, and AD server steps are documented on a separate page:

👉 See: **[Pi-hole – Active Directory Integration](pi-hole_–_active_directory_integration.md)**

Here’s a clear explanation of **how DNS failover works in a multi-Pi-hole setup** and how clients handle the primary Pi-hole being down:

---

## DNS Failover in Multi-Pi-hole Setup

### 1️⃣ Client Configuration

Clients on the LAN are typically configured with **two DNS servers** in order of preference:

{% raw %}
```
Primary DNS:   192.168.2.253  (Primary Pi-hole)
Secondary DNS: 192.168.2.252  (Secondary Pi-hole)
```
{% endraw %}

* The **primary Pi-hole** handles most queries.
* The **secondary Pi-hole** acts as a **backup** if the primary becomes unreachable.

---

### 2️⃣ Failover Behavior

1. A client sends a DNS query to the **primary Pi-hole**.
2. If the primary responds normally, the query is resolved and logged.
3. If the primary **fails to respond** (offline, network issue, service crash):

   * The client automatically retries the query using the **secondary Pi-hole**.
   * This is controlled by the client’s OS DNS resolver (Windows, Linux, macOS, etc.).
4. The secondary Pi-hole resolves the query, applies the same blocklists and rules (thanks to **Nebula Sync**), and returns the result to the client.

> ⚠️ There may be a small delay (typically milliseconds) while the client switches to the secondary server.

---

### 3️⃣ Considerations

* **Nebula Sync** ensures both Pi-hole nodes have identical configurations, so blocking and local DNS resolution remain consistent during failover.
* Clients do **not automatically fail back** to the primary until the next DNS query is sent to it; most OS resolvers try the primary again periodically.
* Logging on the secondary Pi-hole captures queries that occurred during the primary outage, preserving visibility.

---

## 🖥️ Admin Web Interface

The Pi-hole Admin UI provides visibility into DNS queries, filtering statistics, and configuration state.

**Access URLs**

* `http://pi.hole/admin`
* `http://192.168.2.253/admin`

> 🔒 Access should be restricted to trusted networks and protected with HTTPS, reverse proxy rules, or IP allow-listing where appropriate.

---

## 📡 Usage with TP-Link Omada

Pi-hole is integrated with **TP-Link Omada** to enforce centralized DNS usage across the LAN.

### Configuration Summary

* **DNS Mode:** Manual
* **Configured DNS servers:**

  * `192.168.2.253` (Primary Pi-hole)
  * `192.168.2.252` (Secondary Pi-hole)

> 📊 This configuration ensures clients prefer Pi-hole for DNS resolution while maintaining redundancy.

---

## 🔁 Pi-hole Configuration Synchronization

To prevent configuration drift between Pi-hole instances, **[Nebula Sync](nebula_sync.md)** is used to synchronize Pi-hole configuration automatically.

> ⚠️ **Important**
>
> Pi-hole configuration changes **must only be made on the designated primary Pi-hole instance**.
> Changes made directly on replica nodes may be overwritten during the next synchronization cycle.

---

### 📌 Nebula Sync

Nebula Sync is **installed, configured, and maintained via Ansible**, not through the Pi-hole UI.

To keep this page focused on **Pi-hole behavior and integration**, Nebula Sync is documented on a **separate dedicated wiki page**, which covers:

* Primary → replica architecture
* Ansible role and playbook usage
* Synchronization scope and exclusions
* Scheduling and execution model
* Failure handling and recovery procedures

👉 See: **[Nebula Sync](nebula_sync.md)**

---

## 🧠 Unbound Recursive DNS Resolver

Unbound provides a local, validating, recursive DNS resolver for Pi-hole. It replaces external upstream DNS providers and keeps all DNS resolution inside the homelab. Pi-hole **must be installed first**, as Unbound is configured to serve as its upstream resolver.

### Pi-hole Integration

Each Pi-hole instance is configured to use its local Unbound service:

{% raw %}
```
127.0.0.1#5335
```
{% endraw %}

👉 See: **[Unbound](unbound.md)**

---

## 🧭 Making Pi‑hole Authoritative for a Domain

Pi‑hole only applies **Local CNAME Records** to domains it is authoritative for.  If the domain isn’t authoritative, Pi‑hole forwards the query to Unbound, which returns **NXDOMAIN**, and the CNAME never resolves.

### ✔️ Why this is needed
Local CNAMEs for custom domains (e.g., `homelab.refol.us`) only work when Pi‑hole owns the zone.

### ✔️ How to enable authority
Add a Local DNS Record for the zone apex:

{% raw %}
```
refol.us → 0.0.0.0
```
{% endraw %}

This establishes Pi‑hole as authoritative for the domain.  
After that, CNAMEs resolve normally:

{% raw %}
```
homelab.refol.us → t3knoid.github.io
```
{% endraw %}

### ✔️ Verify
{% raw %}
```
dig homelab.refol.us
dig homelab.refol.us CNAME
```
{% endraw %}

Expected:

{% raw %}
```
homelab.refol.us.  CNAME  t3knoid.github.io.
```
{% endraw %}

> [!TIP]
> If CNAMEs that are pointing to external domains continue to fail to resolve,
> add an A record for the domain that is pointed by the CNAME entry in Pi-hole.
>
> In the above example, add an A record for `t3knoid.github.com` > `185.199.109.153`

---

## 🔄 Updates & Maintenance

Pi-hole updates are **not performed manually or ad hoc** and are **not handled by Nebula Sync**.

All update procedures are documented in the following runbook:

👉 **[Update Pi-hole DNS Servers Runbook](update_pi-hole_dns_servers_runbook.md)**

This runbook defines:

* Update prerequisites
* Execution order
* Validation requirements
* Rollback considerations

All Pi-hole maintenance tasks, including updates, restarts, and configuration changes, are defined in playbooks. See:

👉 **[Ansible Pi-hole and DNS Management Runbook](ansible_pi-hole_and_dns_management_runbook.md)**

---

## 🧪 Validation & Health Checks

Routine validation and health verification are documented separately to keep operational procedures isolated from service design.

👉 See: **[Pi-hole DNS – Validation & Health Checks](pi-hole_dns_–_validation_&_health_checks.md)**

This page covers:

* Post-deployment validation
* DNS and AD resolution checks
* Sync verification
* Ongoing health monitoring

---

## 🛠️ Troubleshooting

Operational issues, failure scenarios, and recovery procedures are documented on a dedicated troubleshooting page.

👉 See: **[Pi‑hole Troubleshooting Runbook](pi‑hole_troubleshooting_runbook.md)**

---

## 🚨 Operational Notes

* **Do not configure Pi-hole, Nebula Sync, or Unbound manually**

* All configuration is managed via Ansible
* All rebuilds should be performed using the Ansible deployment playbook
* Configuration drift should be resolved through automation, not UI changes
* Always consult the appropriate runbook before making changes

---

## 📚 References

* [Pi-hole Basic Install Guide](https://docs.pi-hole.net/main/basic-install/)
* [Pi-hole FTL DNS Configuration](https://docs.pi-hole.net/ftldns/configfile/)
* [Pi-hole + Active Directory Discussion](https://discourse.pi-hole.net/t/pihole-as-primary-dns-with-active-directory/58800)