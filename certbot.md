---
title: "Certbot"
---

# 🔐 Certbot

Certbot is an open‑source ACME client used to obtain and renew TLS certificates from **Let’s Encrypt**. It is free, widely supported, and integrates cleanly with NGINX to request and manage [certificates](certificates.md) issued by [Let’s Encrypt](https://letsencrypt.org/).

---

## 🚀 Deployment

Certbot is deployed using an [Ansible playbook](https://github.com/t3knoid/ansible/blob/main/docs/playbooks/deploy_certbot.md).  
All Certbot‑specific logic is contained in the dedicated [`certbot_setup`](https://github.com/t3knoid/ansible/blob/main/docs/roles/certbot_setup.md) role.

This role is intentionally minimal: it installs Certbot and the `certbot-nginx` plugin using Python modules, following the general approach outlined in the official [Certbot instructions](https://certbot.eff.org/instructions?ws=nginx&os=pip).

---

## 🔧 Usage

Certificate requests are performed using the [Request TLS Certificates Runbook](request_tls_certificates_runbook.md), which invokes the [Generate Certs](https://github.com/t3knoid/ansible/blob/main/docs/playbooks/generate_certs.md) playbook.

Certbot uses the **nginx plugin** to complete the **HTTP‑01 ACME challenge**.  
This challenge verifies domain ownership by checking for a validation file served at:

{% raw %}
```
http://<domain>/.well-known/acme-challenge/<token>
```
{% endraw %}

The Certbot Nginx plugin automatically creates and serves this file.  
Your Nginx reverse‑proxy configuration includes the required location block:

{% raw %}
```nginx
location /.well-known/acme-challenge/ {
    root /var/www/certbot;
    allow all;
}
```
{% endraw %}

This block is added when configuring each domain’s [Reverse-Proxy](reverse-proxy.md) definition, ensuring Certbot can complete the challenge successfully.
