---
title: "Cloudflare Public Frontend and IP Obfuscation"
---

# 🌐 Cloudflare Public Frontend and IP Obfuscation

Cloudflare serves as the **public-facing ingress layer** for the homelab, acting as a secure, globally distributed reverse‑proxy that fully obfuscates the homelab’s residential WAN IP. All external traffic terminates at Cloudflare’s edge network before being forwarded to the homelab’s frontend Nginx server.

This design ensures that the homelab is never directly exposed to the internet, significantly reducing the attack surface while providing enterprise‑grade performance and security at zero cost. Cloudflare becomes **Layer 0** of the ingress path, with the existing [reverse‑proxy](reverse-proxy.md) cluster continuing to handle routing, authentication, and backend failover.

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
Cloudflare simply becomes the new public edge.  
Your Nginx frontend continues to handle:

- Internal TLS termination  
- OAuth2 Proxy integration  
- Routing to backend nodes  

No architectural changes required.

---

# 🛠️ Cloudflare Configuration Guide (Concise & Practical)

This section provides a step‑by‑step guide for someone who wants to replicate your setup.

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

On your router/firewall:

- Allow inbound traffic **only** from Cloudflare IP ranges  
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
Ensure your frontend Nginx server:

- Responds on port 443  
- Presents a valid certificate  
- Is reachable from Cloudflare IPs  

---

# 🎯 Summary

Cloudflare acts as a **free, secure, globally distributed ingress layer** that:

- Obfuscates your home WAN IP  
- Provides TLS, WAF, and DDoS protection  
- Integrates seamlessly with your existing reverse‑proxy cluster  
- Requires no architectural changes to your backend  

This page documents the complete configuration and rationale for using Cloudflare as the public frontend for the homelab.
