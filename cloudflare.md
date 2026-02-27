---
title: "Cloudflare"
---

# 🌐 Cloudflare

[Cloudflare](https://www.cloudflare.com/) serves as the **public-facing ingress layer** for the homelab, acting as a secure, globally distributed reverse‑proxy that fully obfuscates the homelab’s residential WAN IP. All external traffic terminates at Cloudflare’s edge network before being forwarded to the homelab’s frontend Nginx server.

This design ensures that the homelab is never directly exposed to the internet, significantly reducing the attack surface while providing enterprise‑grade performance and security at zero cost. Cloudflare becomes **Layer 0** of the ingress path, with the existing **[Reverse-Proxy](reverse-proxy.md)**  cluster continuing to handle routing, authentication, and backend failover.

---

## 🔒 Why Cloudflare?

### **1. Complete WAN IP Obfuscation**

Cloudflare’s Anycast IPs become the only publicly visible addresses.  
Your home IP is never exposed in:

- DNS records  
- HTTP headers  
- Server logs  
- Port scans  
- Security crawlers  

### **2. Free TLS, WAF, and DDoS Protection**

Cloudflare provides:

- Automatic TLS certificates  
- Global caching  
- Bot mitigation  
- Layer‑7 DDoS protection  
- HTTP/2 and HTTP/3 support  

All at zero cost.

### **3. Reduced Attack Surface**

Only Cloudflare is reachable from the internet.  
Your router/firewall can safely block:

- All inbound traffic except Cloudflare IP ranges  
- All direct access to the frontend Nginx server  

### **4. Seamless Integration With Existing Architecture**

Cloudflare simply becomes the new public edge.  The Nginx **[Reverse-Proxy](reverse-proxy.md)** continues to handle:

- Internal TLS termination  
- OAuth2 Proxy integration  
- Routing to backend nodes  

No architectural changes required.

---

# 🛠️ Cloudflare Configuration Guide

This section provides a step‑by‑step guide on how Cloudflare was set up.

---

## 1. Add Your Domain to Cloudflare

1. Create a free Cloudflare account  
2. Add your domain  
3. Cloudflare scans existing DNS records  
4. Update your registrar’s nameservers to Cloudflare’s  

Propagation typically completes within minutes.

---

## 2. Configure DNS Records

For each public service:

1. Create an **A record** pointing to your home WAN IP  
2. **Enable the orange cloud** (proxy mode)  
3. Do *not* create any gray‑cloud (DNS‑only) records pointing to your home IP  

Cloudflare now becomes the public endpoint.

---

## 3. Set SSL/TLS Mode

Navigate to:

**SSL/TLS → Overview → Mode**

Set to:

### **Full (Strict)**  

Cloudflare validates the certificate presented by your frontend Nginx server.

This ensures:

- End‑to‑end encryption  
- No downgrade attacks  
- No plaintext traffic between Cloudflare and the homelab  

---

## 4. Configure Firewall Rules (Highly Recommended)

Configure the following inbound rules on the router,:

- Allow inbound traffic **only** from Cloudflare IP ranges 

{% raw %}
```text
173.245.48.0/20
103.21.244.0/22
103.22.200.0/22
103.31.4.0/22
141.101.64.0/18
108.162.192.0/18
190.93.240.0/20
188.114.96.0/20
197.234.240.0/22
198.41.128.0/17
162.158.0.0/15
104.16.0.0/13
104.24.0.0/14
172.64.0.0/13
131.0.72.0/22
```
{% endraw %}

Cloudflare maintains an updated list here, https://www.cloudflare.com/ips/.

- Block all other inbound traffic  
- Prevent direct access to the frontend Nginx server  

This ensures the homelab is reachable *only* through Cloudflare.

---

## 5. Optional Enhancements

### **WAF Rules**

Enable:

- “Managed Rules”  
- “Bot Fight Mode”  
- “Browser Integrity Check”  

### **Rate Limiting**

Protect sensitive endpoints:

- `/login`  
- `/oauth2/`  
- `/admin`  

### **Caching**

Enable caching for static assets or entire sites if appropriate.

## 6. Automation & Ops

Cloudflare provides an API to update the DNS A record with the current WAN IP address. The **[Automated Cloudflare DNS Updates](automated_cloudflare_dns_updates.md)** details the use of a simple batch script that can be used to automatically keep the network WAN IP address up to date.

---

# 🧩 Troubleshooting & Best Practices

### **Avoid IP Leaks**

- Never expose gray‑cloud DNS records  
- Never publish your WAN IP in logs or documentation  
- Avoid direct port forwarding except for Cloudflare‑validated traffic  

### **Verify Cloudflare Is Working**
Use:

{% raw %}
```
curl -I https://yourdomain.com
```
{% endraw %}

Look for headers like:

{% raw %}
```
server: cloudflare
cf-ray: ...
```
{% endraw %}

### **Check Origin Reachability**

Ensure the Reverse-Proxy Nginx server:

- Responds on port 443  
- Presents a valid certificate  
- Is reachable from Cloudflare IPs  
