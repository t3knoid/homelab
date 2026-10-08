---
title: "Request Web Certificates for a Specific Domain Runbook"
---

# 🏃Request Web Certificates for a Specific Domain Runbook

This runbook provides **step‑by‑step instructions to request and stage TLS certificates** for a specific hostname in the homelab. 

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=set this to the inventory containing the host
```
{% endraw %}

> ⚡ Important: Always start on the control node so all subsequent commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local repository is up to date:

{% raw %}
```shell
git pull origin main
```
{% endraw %}

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent version.

---

## 3️⃣ Request Certificates

Run the Ansible playbook that requests Let’s Encrypt certificates for all configured hostnames:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/certs/generate_certs.yml -u ansible
```
{% endraw %}

> ⚡ Note: The `‑k` option prompts for SSH password if needed.

After this completes successfully, new certificates should be available on the reverse proxy host (rproxy-0) in hostname-specific folders under:

* `/data/letsencrypt/archive/`

---

## 4️⃣ Stage Certificates

Once the certificates have been generated, stage (copy and prepare) them for use:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/certs/stage_certs.yml
```
{% endraw %}

After staging, the certificates will be available on the host in hostname-specific folders under:

* `/data/certs/`


---

## 5️⃣ Verify Certificates Installed

After staging the certificates:

1. Open a web browser and navigate to the hosted site.
2. Verify that each hosted site loads securely via HTTPS.
3. Confirm the certificate details (e.g., expiration date and domain names) are correct in the browser’s security panel.

---

### ✅ Notes

* Ensure DNS for all domains points to the correct host before requesting certificates.
* Let’s Encrypt rate limits certificate issuance—if you encounter errors, check for duplicate requests.
* If staging fails, verify permissions on the target directories.

