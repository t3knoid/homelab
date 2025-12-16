# 🏃 Deploy Lazy Librarian Runbook

This runbook provides **step‑by‑step instructions to deploy or update Lazy Librarian** in the Home Lab using Ansible.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

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

Edit the following file:

```
inventory/services/group_vars/lazylibrarian/main.yml
```

Locate and update the version variable:

```yaml
lazylibrarian_setup_version: <desired_version>
```

### Where to Find the Latest Version

* Visit Lazy Librarian’s GitHub Versions page and look for the **latest** tagged release to determine the version you want to deploy. ([Home Lab][1])

---

## 4️⃣ Commit Version Change

After updating the version value, commit the change:

```shell
git add inventory/services/group_vars/lazylibrarian/main.yml
git commit -m "Update Lazy Librarian version to <version_number>"
git push origin main
```

> ⚡ Important: Replace `<version_number>` with the actual version you set.

---

## 5️⃣ Deploy Lazy Librarian

Run the Ansible playbook to deploy the specified version:

```shell
ansible-playbook -i $INV -k playbooks/services/deploy_lazylibrarian.yml
```

> ⚡ Note: The `‑k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Installed Version

After the playbook completes:

1. Open a web browser and navigate to:
   [https://lazy.refol.us](https://lazy.refol.us)
2. In the Lazy Librarian web interface, go to **Help > Version**.
3. Confirm that the **first part of the version shown** matches the version you deployed. ([Home Lab][1])

---

### ✅ Notes

* Always pull and commit changes before deploying.
* Make sure the inventory variable (`INV`) points to the correct hosts.
* If the deployment fails, review the Ansible output for errors before retrying.
