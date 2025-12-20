---
title: "Nebula Sync – Pi‑hole Synchronization"
---

# 🌐 Nebula Sync – Pi‑hole Synchronization

**Nebula Sync** is used to **synchronize multiple Pi‑hole instances** in this homelab, ensuring consistent blocklists, local DNS records, and configuration settings across all nodes.

> ⚠️ This is not a true high-availability cluster — it copies state on a scheduled or manual basis. Changes should always be made on the **primary Pi‑hole**.

---

## ⚙️ Purpose

Nebula Sync helps in environments where:

* You have **multiple Pi‑hole servers** for redundancy.
* You want **consistent ad-blocking and DNS configurations** across nodes.
* You need to **automate syncing** without manual export/import of Teleporter backups.

---

## 📦 Installation & Deployment

Nebula Sync is installed and configured using **Ansible**:

* **Role:** [nebulasync_setup](https://github.com/t3knoid/ansible/blob/main/roles/nebulasync_setup/tasks/main.yml)
* **Deployment Playbook:** [deploy_nebulasync.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/deploy_nebulasync.yml)

### 🔹 Steps (Conceptual)

1. Configure **primary and replica Pi‑hole instances** in the inventory.
2. Apply the `nebulasync_setup` role using Ansible.
3. Verify sync configuration and schedules.
4. Monitor logs and health checks to ensure successful propagation.

> 💡 Recommended to schedule syncs during off-peak hours to avoid DNS resolution delays.

---

## 🖥️ Configuration Overview

**Primary → Replica model:**

* **Primary:** Central source of truth; all changes made here.
* **Replica:** Receives configuration updates automatically via Nebula Sync.

**What is synced:**

* Gravity blocklists
* Whitelists and blacklists
* Local DNS entries
* Pi‑hole configuration files

**What is NOT synced:**

* DHCP leases
* UI-specific settings (themes, passwords if different)
* Custom scripts or plugins not installed on replicas

---

## 📡 Usage Notes

* **Multiple replicas supported:** Each replica points to a single primary.
* **Sync verification:** Check logs on both primary and replica after sync runs.
* **Conflict avoidance:** Avoid manual changes on replica nodes.

{% raw %}
```bash
# Example: check Nebula Sync status
journalctl -u nebulasync.service
```
{% endraw %}

---

## 📌 Best Practices

1. **Always edit primary Pi‑hole only.**
2. **Enable logging** for sync verification.
3. **Test sync** after major updates or adding new blocklists.
4. **Monitor network connectivity** between primary and replicas.
5. **Schedule regular sync intervals** appropriate for the environment (e.g., hourly, daily).

---

## 🔗 References

* [Nebula Sync GitHub Repository](https://github.com/lovelaze/nebula-sync)
* [Pi‑hole Documentation](https://docs.pi-hole.net/)
* [Ansible Role: nebulasync_setup](https://github.com/t3knoid/ansible/blob/main/roles/nebulasync_setup/tasks/main.yml)
* [Deployment Playbook: deploy_nebulasync.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/dns/deploy_nebulasync.yml)

