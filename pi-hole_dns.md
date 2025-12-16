# 🌐 Pi‑hole DNS

[Pi‑hole](https://pi-hole.net/) is a lightweight DNS solution that provides **network‑wide ad blocking** and centralized DNS management. It is particularly useful in homelab environments where visibility, filtering, and integration with existing directory services are important.

---

## ⚙️ Installation

Installation is straightforward and documented in the [Pi‑hole Basic Install Guide](https://docs.pi-hole.net/main/basic-install/).

### Manual Installation
```shell
wget -O basic-install.sh https://install.pi-hole.net
sudo bash basic-install.sh
```

- Recommended to install on a **minimal VM** or container for efficiency.  
- Ensure the VM has a static IP address to avoid DNS resolution issues.  

---

## 🏢 Integration with Active Directory

When Pi‑hole is used as the **primary DNS server** in an environment with **Windows Active Directory (AD)**, it must be configured to forward AD‑specific queries to the domain controller. This is achieved using **Conditional Forwarding**.

### Steps
1. Open the **Pi‑hole Admin UI**.  
2. Navigate to **Settings → DNS**.  
3. Scroll to **Conditional Forwarding** and enable the checkbox.  
4. Configure the following:  
   - **Local network field:** `192.168.2.0/24`  
   - **IP address of DHCP server:** `192.168.2.253`  
   - **Local domain name:** `refol.us`  

> ✅ This ensures Pi‑hole forwards AD domain queries (e.g., `_ldap._tcp.refol.us`) to the domain controller at `192.168.2.251`, while continuing to filter external queries.

---

## 🖥️ Admin Web Interface

The Pi‑hole admin dashboard provides query logs, statistics, and configuration options.  
Access it via:

- `http://pi.hole/admin`  
- `http://192.168.2.253/admin`  

> 🔒 Consider enabling HTTPS or restricting access to trusted subnets for security.

---

## 📡 Usage with TP‑Link Omada

To integrate Pi‑hole with TP‑Link Omada for centralized DNS management:

1. Log in to the [Omada Cloud Controller](https://omada.tplinkcloud.com/).  
2. Navigate to **Settings → Wired Networks → LAN**.  
3. Edit the **Default network**.  
4. Set **DNS Server** to **Manual**.  
5. Enter the following DNS servers:  
   - `192.168.2.253`  
   - `192.168.2.251`  
   - `8.8.8.8`  

> 📊 This ensures all LAN clients use Pi‑hole for DNS resolution, with redundancy across multiple Pi‑hole instances.

---

## 🛠️ Troubleshooting Pi‑hole + AD Integration

Even with Conditional Forwarding enabled, issues can arise. Here are common pitfalls and resolutions:

### 1. Domain Join Failures
- **Symptom:** Windows clients cannot join the AD domain.  
- **Cause:** Pi‑hole is not forwarding SRV records correctly.  
- **Fix:** Verify Conditional Forwarding is set to the AD DNS (`192.168.2.251`).  
  ```bash
  nslookup _ldap._tcp.refol.us 192.168.2.253
  ```

### 2. Kerberos Authentication Errors
- **Symptom:** Logon failures or GPOs not applying.  
- **Cause:** Time skew or blocked SRV records.  
- **Fix:** Ensure NTP is configured on the domain controller and Pi‑hole forwards AD queries.

### 3. DNS Loops
- **Symptom:** Queries fail or time out.  
- **Cause:** Pi‑hole forwards to AD, but AD forwards back to Pi‑hole.  
- **Fix:** Configure AD DNS forwarders to point upstream (e.g., Cloudflare, Google), not back to Pi‑hole.

### 4. Missing Client Hostnames in Pi‑hole Logs
- **Symptom:** Pi‑hole shows only IPs, not hostnames.  
- **Cause:** Conditional Forwarding not configured with the DHCP server IP.  
- **Fix:** Ensure the DHCP server IP (`192.168.2.252`) is entered in Pi‑hole’s Conditional Forwarding settings.

### 5. Pi‑hole Blocking AD Queries
- **Symptom:** AD services intermittently fail.  
- **Fix:** Whitelist AD domain (`refol.us`) and controller hostname in Pi‑hole.

---

## 📚 References

- [Pi‑hole FTL DNS Configuration](https://docs.pi-hole.net/ftldns/configfile/)  
- [Pi‑hole Basic Install Guide](https://docs.pi-hole.net/main/basic-install/)  
- [Pi‑hole + Active Directory Discussion](https://discourse.pi-hole.net/t/pihole-as-primary-dns-with-active-directory/58800)  
