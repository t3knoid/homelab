---
title: "Mirror wiki pages to HTML static page runbook"
---

# 🏃 Mirror wiki pages to HTML static page runbook

These runbook provides **step-by-step instructions to mirror the homelab wiki pages to an HTML static page**. It references the corresponding Ansible playbook and ensures consistency, verification, and version control.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/redmine/inventory.ini
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

## 3️⃣ Deploy Using Ansible Playbook

Run the corresponding playbook:

{% raw %}
```shell
ansible-playbook -k -i $INV playbooks/redmine/mirror_wiki.yml 
```
{% endraw %}

---

## 6️⃣ Verify Deployment

After deployment:

1. Open https://github.com/t3knoid/homelab/actions. The workflow named **Mirror Redmine wiki** should be in progress
2. Click on the **Mirror Redmine wiki** workflow run.
3. At the end of the run, scan the Link Checker Results for any 404 error.
4. Fix 404 errors any and redeploy.

---

### ✅ Notes

* Always double-check the version or configuration before deploying.
* Use this workflow for both **updates and new deployments**.
* Make sure the control node has network access to the service.
* Pulling, committing, and deploying in this order prevents repository conflicts and ensures a consistent deployment state.

