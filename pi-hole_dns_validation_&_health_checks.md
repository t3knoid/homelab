---
title: "Pi-hole DNS Validation & Health Checks"
---

# 🧪 Pi-hole DNS Validation & Health Checks

This page defines the **standard validation and health check procedures** for Pi-hole DNS servers in this environment.
It is used after:

* Initial deployment
* Configuration changes
* Updates or upgrades
* Failover or recovery events
* Suspected DNS or directory-related issues

> 📌 **Scope**
>
> This page focuses on *verification and health assessment*.
> Update procedures and failure remediation are documented separately.

---

## 🎯 Validation Objectives

Successful validation confirms that:

* Pi-hole is reachable and responding to DNS queries
* Clients resolve both **external** and **internal (AD)** records correctly
* Configuration is consistent across Pi-hole instances
* Nebula Sync is functioning as expected
* No DNS loops or forwarding issues exist

---

## 🧭 When to Run These Checks

Run this validation:

* After running `deploy_pihole.yml`
* After executing the **Update Pi-hole DNS Servers Runbook**
* After modifying DNS, AD, or Nebula Sync configuration
* When adding or rebuilding a Pi-hole instance
* When users report intermittent connectivity or authentication issues

---

## 🔍 DNS Resolution Validation

### External DNS Resolution

From a client or management host:

{% raw %}
```bash
nslookup google.com 192.168.2.253
```
{% endraw %}

**Expected result**

* Query resolves quickly
* Response is returned by Pi-hole
* No timeout or SERVFAIL

---

### Internal (Active Directory) Resolution

Verify AD SRV records resolve correctly through Pi-hole:

{% raw %}
```bash
nslookup _ldap._tcp.refol.us 192.168.2.253
```
{% endraw %}

**Expected result**

* SRV records are returned
* Responses originate from the AD DNS server
* No NXDOMAIN or timeout errors

> ⚠️ Failure here typically indicates a Conditional Forwarding or upstream DNS issue.

---

## 🧠 Conditional Forwarding Verification

Confirm that Pi-hole is forwarding AD queries correctly.

In the **Pi-hole Admin UI**:

* Navigate to **Settings → DNS**
* Verify **Conditional Forwarding** is enabled
* Confirm values:

  * Local network: `192.168.2.0/24`
  * DHCP server: `192.168.2.253`
  * Domain: `refol.us`

---

## 🖥️ Pi-hole Service Health

### Web Interface Accessibility

Access the Admin UI:

* `http://pi.hole/admin`
* `http://192.168.2.253/admin`

**Expected**

* UI loads without error
* Statistics populate
* Query log updates in real time

---

### FTL Service Status (Optional)

On the Pi-hole host:

{% raw %}
```bash
systemctl status pihole-FTL
```
{% endraw %}

**Expected**

* Service is active and running
* No crash loops or repeated restarts

---

## 🔁 Nebula Sync Validation

Configuration synchronization is handled automatically by **Nebula Sync**.

### Sync Consistency Checks

On replica Pi-hole instances:

* Verify blocklists, local DNS records, and groups match the primary
* Confirm recent changes made on the primary appear after the sync interval

### Drift Indicators

* Settings differ between nodes
* Changes revert unexpectedly
* Replica behavior differs from primary

> 📌 If drift is detected, **do not fix manually**.
> Refer to the **Nebula Sync** wiki page for validation and resync procedures.

👉 See: **[Nebula Sync](nebula_sync.md)**

---

## 📡 Client Path Validation

Verify that clients are actually using Pi-hole for DNS.

On a client system:

{% raw %}
```bash
nslookup pi.hole
```
{% endraw %}

Or check the client’s DNS settings to confirm:

* Primary DNS points to a Pi-hole instance
* Secondary DNS is expected and documented

**Expected**

* Client queries appear in the Pi-hole query log
* Client hostname resolves correctly (if Conditional Forwarding is configured)

---

## 🔄 Multi-Instance Validation

When multiple Pi-hole instances are deployed:

* Validate DNS resolution against **each** Pi-hole IP
* Ensure both respond consistently
* Confirm Omada (or other network infrastructure) advertises all expected DNS servers

Example:

{% raw %}
```bash
nslookup google.com 192.168.2.254
```
{% endraw %}

---

## 📊 Indicators of Healthy Operation

A healthy Pi-hole environment typically shows:

* Stable query volume
* Low or predictable block rate
* No spikes in SERVFAIL or REFUSED responses
* Consistent behavior across all Pi-hole nodes
* No AD authentication or GPO-related errors reported by users

---

## 🚨 When Validation Fails

If any validation step fails:

* **Do not make ad-hoc configuration changes**
* Identify which validation stage failed (external, AD, sync, client path)
* Proceed to the troubleshooting guide

👉 See: **[Pi-hole Troubleshooting Runbook](pi-hole_troubleshooting_runbook.md)**

---

## 🔗 Related Pages

* **[Pi-hole DNS](pi-hole_dns.md)** – Service overview and architecture
* **[Update Pi-hole DNS Servers Runbook](update_pi-hole_dns_servers_runbook.md)** – Update procedures
* **[Nebula Sync](nebula_sync.md)** – Configuration sync
* **[Pi-hole Troubleshooting Runbook](pi-hole_troubleshooting_runbook.md)** – Failure scenarios and remediation