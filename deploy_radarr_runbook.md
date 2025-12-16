---
title: "🏃 Deploy Radarr Runbook"
---

# 🏃 Deploy Radarr Runbook

This runbook provides **step‑by‑step instructions to deploy or update Radarr** in the Home Lab. It uses the corresponding Ansible playbook to manage the version and deployment.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/services/inventory.ini
```

> ⚡ Important: Always begin on the control node so all commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local Ansible repository is up to date:

```shell
git pull origin main
```

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent configuration.

---

## 3️⃣ Set Version to Deploy

Edit the file:

```
inventory/services/group_vars/radarr/main.yml
```

Locate and update the version variable:

```yaml
radarr_setup_version: <desired_version>
```

### Where to Find the Latest Version

* Visit Radarr’s GitHub Versions page.
* Look for the release tagged **latest** and use that version. ([Home Lab][1])

---

## 4️⃣ Commit Version Change

After updating the version, commit the change:

```shell
git add inventory/services/group_vars/radarr/main.yml
git commit -m "Update Radarr version to <version_number>"
git push origin main
```

> ⚡ Important: Replace `<version_number>` with the actual version you are deploying.

---

## 5️⃣ Deploy Radarr

Run the Ansible playbook to deploy the version you specified:

```shell
ansible-playbook -i $INV -k playbooks/services/deploy_radarr.yml
```

> ⚡ Note: The `‑k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Installed Version

After deployment:

1. Open a web browser and visit:
   [https://radarr.refol.us](https://radarr.refol.us)
2. Navigate to **System > Status**.
3. Confirm the displayed version matches the version you deployed. ([Home Lab][1])

---

### ✅ Notes

* Always pull and commit changes before deploying.
* Make sure the `INV` inventory variable points to the correct hosts.
* If the deployment fails, review the Ansible output for errors before retrying.

