---
title: "Unbound"
---

# 🧠 Unbound

Unbound provides a **local, validating, recursive DNS resolver** that replaces external upstream DNS providers. Instead of sending DNS queries to Cloudflare, Google, or your ISP, Unbound resolves everything directly from the root servers — inside your homelab.

Using Unbound gives you **privacy, independence, and full control** over DNS resolution. It eliminates reliance on third‑party DNS services and ensures that every DNS query is validated, logged, and resolved on your own hardware.

Unbound is deployed only after Pi-hole is installed, and each DNS node runs its own local Unbound instance.

---

## ⭐ Why Use Unbound?

Unbound is the natural upstream for Pi-hole because it provides:

### **1. Privacy**
No external DNS provider sees your queries.  
All resolution happens locally, from root → TLD → authoritative servers.

### **2. Independence**
Your DNS no longer depends on Cloudflare, Google, Quad9, or your ISP.  
Even if the internet is degraded, recursive resolution continues to function.

### **3. DNSSEC Validation**
Unbound performs DNSSEC validation locally, ensuring authenticity of DNS responses without trusting upstream resolvers.

### **4. Reliability**
Each DNS node runs its own Unbound instance.  
If one node goes down, the other continues resolving queries without interruption.

### **5. Consistency**
Every Pi-hole uses the same local upstream resolver, eliminating differences in behavior between nodes or clients.

### **6. Zero External Dependencies**
No third‑party DNS outages, no rate limits, no filtering surprises, no logging by external providers.

In short: **Unbound gives you a self‑contained, trustworthy DNS stack.**

---

## 🏗️ Architecture Overview

Pi-hole handles filtering and client‑facing DNS.  
Unbound handles recursive resolution and DNSSEC.

{% raw %}
```
+------------------+        +------------------+
|   Pi-hole        | -----> |    Unbound       |
| (Filtering + UI) |        | (Recursive DNS)  |
+------------------+        +------------------+
           |                         |
           v                         v
      LAN Clients               Root → TLD → Authoritative
```
{% endraw %}

Both DNS servers run Pi-hole + Unbound, providing full redundancy.

---

## ⚙️ Installation & Deployment

Unbound is deployed exclusively via Ansible.

### Ansible Role  
<https://github.com/t3knoid/ansible/tree/main/roles/unbound>

The role provides:

- Hardened configuration  
- Local recursive resolution  
- DNSSEC validation  
- Systemd service management  
- Safe reload behavior  

### Deploying Unbound

{% raw %}
``` bash
ansible-playbook -k -i inventory/dns/inventory playbooks/dns/deploy_unbound.yml
```
{% endraw %}

This playbook installs Unbound, applies the hardened configuration, and ensures the service is enabled and running.

> All configuration must be applied through Ansible to avoid drift.

---

## 🔗 Integration with Pi-hole

Each Pi-hole instance uses its **local** Unbound resolver:

{% raw %}
```
127.0.0.1#5335
```
{% endraw %}

This ensures:

- All DNS stays inside the homelab  
- DNSSEC validation is performed locally  
- Both DNS nodes behave identically  

---

## 🧪 Validation

The Unbound playbook performs basic resolver validation automatically.  
No manual steps are required.

Here’s a **tight, minimal troubleshooting section** that matches the tone of your Pi-hole DNS page and fits cleanly into the new Unbound page. It focuses only on actionable checks, avoids noise, and assumes everything is deployed via Ansible.

---

## 🛠️ Troubleshooting

Unbound is generally hands‑off once deployed, but the following checks cover the most common issues:

### Unbound Not Responding
- Ensure the service is running:  
  `systemctl status unbound`
- Restart if needed:  
  `systemctl restart unbound`

### Pi-hole Not Resolving Through Unbound
- Confirm Pi-hole is using the correct upstream:  
  `127.0.0.1#5335`
- Verify Unbound is listening on port 5335:  
  `ss -tulpn | grep 5335`

### DNS Resolution Fails
- Test direct Unbound resolution:  
  `dig @127.0.0.1 -p 5335 example.com`
- If this fails, re-run the deployment playbook to restore configuration.

### Configuration Drift
All configuration must come from Ansible.  
If anything looks off, redeploy:

{% raw %}
```
ansible-playbook playbooks/dns/deploy_unbound.yml
```
{% endraw %}
