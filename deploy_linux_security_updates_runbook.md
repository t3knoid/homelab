# 🏃 Deploy Linux Security Updates Runbook

This runbook provides **step-by-step instructions to apply Linux security updates** on one or more hosts in your Home Lab using an Ansible playbook. Note that this process **may reboot target systems** if required by the updates.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
```

> ⚡ Important: All subsequent steps must be run in this Ansible environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local repository is up to date:

```shell
git pull origin main
```

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent playbook and inventory definitions.

---

## 3️⃣ Set Inventory

Before running the playbook, set the inventory of the target nodes you want to update:

```shell
INV=<set this to the inventory of target nodes to update>
```

For example, to update all Ubuntu servers:

```shell
INV=inventory/linux/inventory.ini
```

> ⚡ Tip: Adjust this to the specific inventory group you want to patch (e.g., `inventory/servers/inventory.ini`, `inventory/web/inventory.ini`, etc.).

---

## 4️⃣ Deploy Security Updates

Run the Ansible playbook to apply Linux security updates:

```shell
ansible-playbook -i $INV -k playbooks/linux/deploy_updates.yml
```

> ⚡ Note: The `-k` option will prompt for SSH password if needed.
> ⚠ If updates require a reboot, the target host may restart during this process.

---

## 5️⃣ Verify Successful Updates

After the playbook completes:

1. SSH into each updated host.
2. Check that the system is running and reachable.
3. Optionally, verify that critical packages have been updated:

```shell
sudo apt list --upgradable
```

It should return **no upgradable packages** if updates were applied successfully.

---

### ✅ Notes

* Always pull the latest code before deploying.
* Make sure the inventory variable (`INV`) points to the correct hosts you intend to update.
* Some security updates may trigger a reboot; plan accordingly if target hosts provide production-like services.
* If the update playbook fails, review the Ansible output and logs on the target systems to diagnose the error.
