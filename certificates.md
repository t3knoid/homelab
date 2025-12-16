---
title: "🔒 Certificates"
---

# 🔒 Certificates

Web certificates are managed using **Certbot**, a widely used tool for obtaining trusted SSL/TLS certificates from **Let’s Encrypt**.  
Certificates are staged inside the reverse proxy server under `/data/certs`, with a dedicated folder for each host.  
Automation is handled via **Ansible playbooks**, ensuring consistency and repeatability across environments.

---

## ⚙️ Certificate Generation

Certificates are generated using the Ansible playbook:

```
playbooks/certs/generate_certs.yml
```

- The **Certbot/Let’s Encrypt** working directory is located at `/data/letsencrypt` on the host defined in the `[certs]` inventory group.  
- This is typically the **main reverse proxy host**.  
- The playbook uses the `rproxy_setup_sites` list variable to determine which hostnames to pass to Certbot.  
- The `server_name` field defines the hostname for certificate generation.  
- Multiple sites can be specified in the inventory when required.

### Example Configuration
```yaml
rproxy_setup_sites:
  - server_name: homelab.refol.us
    port: 80
    proxy_pass: "http://{{ global_ip_addresses['redmine-0'] }}"
    allow_list:
      - 192.168.0.0/24
      - 192.168.2.0/24
      - 24.105.250.200
      - 70.107.117.124
    restricted: false
```

> 💡 This configuration allows Certbot to generate certificates for `homelab.refol.us` while enforcing access controls via the `allow_list`.

---

## 📂 Certificate Staging

Once generated, certificates are staged using:

```
playbooks/certs/stage_certs.yml
```

This playbook copies the following files from the Let’s Encrypt folder into the appropriate host folder under `/data/certs`:

- `privkey.pem` → Private key  
- `fullchain.pem` → Full certificate chain  

These files are then referenced in the NGINX site configuration:

```nginx
ssl_certificate     /data/certs/homelab.refol.us/fullchain.pem;
ssl_certificate_key /data/certs/homelab.refol.us/privkey.pem;
```

> ✅ Staging ensures certificates are consistently deployed and referenced by reverse proxy configurations.

---

## 🧪 Example Workflow

To generate and stage certificates for `homelab.refol.us`:

```bash
INV=inventory/redmine/inventory.ini
ansible-playbook -i $INV playbooks/certs/generate_certs.yml -k
ansible-playbook -i $INV playbooks/certs/stage_certs.yml -k
```

---

## 🛠️ Debugging Certificate Request Errors

If errors occur during certificate generation or renewal:

- Review the Let’s Encrypt log file on the reverse proxy host (`rproxy-0`):  
  ```
  /data/letsencrypt/log/letsencrypt.log
  ```
- Common issues include:  
  - DNS misconfiguration (hostname not resolving correctly).  
  - Firewall restrictions blocking port 80/443.  
  - Incorrect `server_name` values in the playbook.  

---

## ✅ Summary

This workflow provides a **fully automated certificate lifecycle**:  
- **Generation** via Ansible + Certbot.  
- **Staging** into `/data/certs` for each host.  
- **Integration** with NGINX for secure HTTPS delivery.  
- **Debugging** via centralized Let’s Encrypt logs.  

Together, these practices ensure secure, maintainable, and repeatable certificate management across the homelab environment.
