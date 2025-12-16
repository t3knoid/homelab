# 🏃 Deploy Sabnzbd Runbook

This runbook provides **step‑by‑step instructions to deploy or update Sabnzbd** in the Home Lab using Ansible. It follows the same pattern you use for other service deployments.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/services/inventory.ini
```

> ⚡ Important: Always begin on the control node so all subsequent commands run in the correct environment.

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
inventory/services/group_vars/sabnzbd/main.yml
```

Locate and update the version variable:

```yaml
sabnzbd_setup_version: <desired_version>
```

### Where to Find the Latest Version

* Visit Sabnzbd’s GitHub Versions page and look for the **latest** tagged release to determine the correct version to deploy. ([Home Lab][1])

---

## 4️⃣ Commit Version Change

After updating the version, commit the change:

```shell
git add inventory/services/group_vars/sabnzbd/main.yml
git commit -m "Update Sabnzbd version to <version_number>"
git push origin main
```

> ⚡ Important: Replace `<version_number>` with the actual version you want to deploy.

---

## 5️⃣ Deploy Sabnzbd

Run the Ansible playbook to deploy the specified version:

```shell
ansible-playbook -i $INV -k playbooks/services/deploy_sabnzbd.yml
```

> ⚡ Note: The `-k` option will prompt for SSH password if required.

---

## 6️⃣ Verify Installed Version

After the playbook completes:

1. Open a web browser and navigate to:
   [https://sabnzbd.refol.us](https://sabnzbd.refol.us)
2. Click the **gear (settings) icon**.
3. Confirm that the **version number shown matches the version you deployed**. ([Home Lab][1])

---

### ✅ Notes

* Always pull and commit changes before deploying.
* Confirm the inventory variable (`INV`) points at the correct service hosts.
* If deployment fails, review the Ansible output for errors, then retry.

