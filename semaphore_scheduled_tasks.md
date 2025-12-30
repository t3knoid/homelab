---
title: "️ Semaphore Scheduled Tasks"
---

# 🗓️ Semaphore Scheduled Tasks

This page documents the scheduled tasks configured for the **Home Lab** project in Semaphore.  All schedules are defined in [inventory/semaphore/group_vars/semaphore/schedules.yml](https://github.com/t3knoid/ansible/blob/main/inventory/semaphore/group_vars/semaphore/schedules.yml).

For instructions on adding or modifying schedules, 

👉 See: **[Configure Semaphore UI Projects Runbook](configure_semaphore_ui_projects_runbook.md)**.

---

## 📘 Overview

Semaphore executes recurring automation across several categories:

- **Backups** – database dumps, application backups, configuration snapshots  
- **Certificate Rotation** – renewing and distributing certificates  
- **Maintenance Tasks** – cleanup, pruning, or other recurring system operations  
- **Service‑Specific Automation** – tasks tied to individual applications or services  

Each category is documented below.

---

### 💾 Backup Tasks

These tasks perform recurring backups of application data and databases.

| Name | Template | Cron | Human time |
|---|---|---|---:|
| Semaphore Database Nightly Backup | Backup Semaphore Database | `0 3 * * *` | daily at 03:00 |
| Ombi Database Weekly Backup | Backup Ombi Database | `0 2 * * 0` | Sunday 02:00 |
| Lidarr Database Weekly Backup | Backup Lidarr Database | `15 2 * * 0` | Sunday 02:15 |
| Radarr Database Weekly Backup | Backup Radarr Database | `30 2 * * 0` | Sunday 02:30 |
| Sonarr Database Weekly Backup | Backup Sonarr Database | `45 2 * * 0` | Sunday 02:45 |
| Tautulli Database Weekly Backup | Backup Tautulli Database | `0 3 * * 0` | Sunday 03:00 |
| Grafana Database Weekly Backup | Backup Grafana Database | `15 3 * * 0` | Sunday 03:15 |
| Plex Weekly Backup | Backup Plex | `30 3 * * 0` | Sunday 03:30 |
| Prometheus Database Weekly Backup | Backup Prometheus Database | `45 3 * * 0` | Sunday 03:45 |
| Redmine Database Nightly Backup | Backup Redmine Database | `0 3 * * *` | daily at 03:00 |

**Note:** Weekly backups are staggered in 15‑minute increments to reduce load on shared resources.

---

### 🔐 Certificate & Key Rotation

| Name | Template | Cron | Human time |
|---|---|---|---:|
| Monthly Cert Rotation | Request Certificates for all hosts | `0 4 1 * *` | 04:00 on day 1 of each month |

---

### 🧹 Maintenance Tasks

*(No maintenance tasks currently defined.)*

This section will expand as cleanup, pruning, or housekeeping jobs are added.

---

### 🔧 Service‑Specific Automation

*(No service‑specific tasks beyond backups at this time.)*

This section is reserved for future tasks such as:

---

## 🔍 Verification

To confirm schedules are applied:

1. Open **Semaphore UI → Projects → Home Lab → Schedules**  
2. Verify next run times  
3. Inspect job history to confirm successful execution  
4. Validate outputs (e.g., backup files, renewed certificates, cleanup results)

---

## 🛠️ Troubleshooting

If a scheduled task does not run as expected:

- Check the job logs in Semaphore  
- Confirm the referenced template exists and is functional  
- Verify inventories, repositories, and keystores used by the template  
- Ensure cron syntax is valid in `schedules.yml`  
- Adjust timing if tasks overlap or cause resource contention  

---

## 📎 Related Documentation

- [Configure Semaphore UI Projects Runbook](configure_semaphore_ui_projects_runbook.md) 
- [Semaphore](semaphore.md)