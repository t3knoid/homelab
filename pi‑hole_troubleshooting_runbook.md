---
title: "️ Pi‑hole Troubleshooting Runbook"
---

# 🛠️ Pi‑hole Troubleshooting Runbook

This page provides **common troubleshooting scenarios and resolutions** for Pi‑hole in a homelab environment. For installation and configuration, see the [Pi‑hole DNS Wiki Page](pi-hole_dns.md).

---

## ⚠️ General Troubleshooting Guidelines

1. **Check Logs**

   ```bash
   sudo journalctl -u pihole-FTL
   tail -f /var/log/pihole-FTL.log
   tail -f /var/log/pihole.log
   ```
2. **Verify DNS Resolution**

   ```bash
   nslookup pi.hole 192.168.2.253
   dig @192.168.2.253 google.com
   ```
3. **Check Service Status**

   ```bash
   sudo systemctl status pihole-FTL
   sudo systemctl status lighttpd
   ```

> 💡 Always start with logs and service status before attempting configuration changes.

---

## 🔍 Common Issues

### 1. Domain Join Failures (Windows AD)

* **Symptom:** Windows clients cannot join the AD domain.
* **Cause:** Pi‑hole is not forwarding SRV records correctly.
* **Resolution:**

  * Verify Conditional Forwarding is set to the AD DNS (`192.168.2.251`).

  ```bash
  nslookup _ldap._tcp.refol.us 192.168.2.253
  ```

### 2. Kerberos Authentication Errors

* **Symptom:** Logon failures, GPOs not applying.
* **Cause:** Time skew or blocked SRV records.
* **Resolution:**

  * Ensure NTP is configured on both Pi‑hole and domain controller.
  * Verify Conditional Forwarding is correctly pointing to the AD DNS.

### 3. DNS Loops

* **Symptom:** Queries fail or time out.
* **Cause:** Pi‑hole forwards to AD, but AD forwards back to Pi‑hole.
* **Resolution:**

  * Reconfigure AD DNS forwarders to upstream servers (e.g., `1.1.1.1`, `8.8.8.8`) instead of Pi‑hole.

### 4. Missing Client Hostnames in Pi‑hole Logs

* **Symptom:** Only IPs shown, not hostnames.
* **Cause:** Conditional Forwarding not configured with DHCP server IP.
* **Resolution:**

  * Confirm DHCP server IP (`192.168.2.252`) is entered in Pi‑hole’s Conditional Forwarding settings.

### 5. Pi‑hole Blocking AD Queries

* **Symptom:** AD services intermittently fail.
* **Resolution:**

  * Whitelist AD domain (`refol.us`) and domain controller hostnames in Pi‑hole.

---

## 📌 Notes on Nebula Sync Integration

* If using [Nebula Sync](nebula_sync.md) to synchronize multiple Pi‑hole instances, ensure:

  * Syncs are running on schedule.
  * Primary → replica configuration is consistent.
  * Replica Pi‑hole instances are not manually modified.

---

## 🔗 References

* [Pi‑hole Admin Manual](https://docs.pi-hole.net/)
* [Pi‑hole + Active Directory Discussion](https://discourse.pi-hole.net/t/pihole-as-primary-dns-with-active-directory/58800)
* [Nebula Sync Wiki Page](nebula_sync.md)


