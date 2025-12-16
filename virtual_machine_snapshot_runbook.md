# 🏃 Virtual Machine Snapshot Runbook

This runbook provides **step-by-step instructions to create and remove virtual machine snapshots** using Ansible. Snapshots can be used as a rollback point before deploying updates or making significant changes.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
```

> ⚡ Important: Always start on the control node so all subsequent commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local Ansible repository is up to date:

```shell
git pull origin main
```

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re using the latest playbooks and inventory.

---

## 3️⃣ Create a VM Snapshot

To create a snapshot for a specific host or VM group:

```shell
ansible-playbook -i $INV -k playbooks/vms/create_vm_snapshot.yml 
```

* The playbook will create a snapshot with a timestamped name.

> ⚡ Tip: Always create a snapshot **before deploying updates or making major changes** to ensure a quick rollback if needed.

---

## 4️⃣ Verify Snapshot Creation

1. Log in to your virtualization management interface (e.g., Proxmox, VMware, or Hyper-V).
2. Confirm that a new snapshot exists for the target VM with the correct timestamp.
3. Optionally, check snapshot metadata to ensure it includes the expected VM state.

---

## 5️⃣ Remove a VM Snapshot

After verifying updates or if the snapshot is no longer needed, remove it:

```shell
ansible-playbook -i $INV -k playbooks/vms/remove_vm_snapshot.yml
```

* Confirm the snapshot has been deleted via your virtualization interface.

---

### ✅ Notes

* Snapshots are **temporary rollback points**, not backups. Keep them only as long as needed.
* Use descriptive naming conventions or timestamps for snapshots to avoid confusion.
* Always verify snapshot creation before making changes to production or critical VMs.
* If snapshot creation or removal fails, check the Ansible logs and the virtualization host for errors.

