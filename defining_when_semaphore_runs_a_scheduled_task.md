---
title: "⏱️ Defining When Semaphore Runs a Scheduled Task"
---

# ⏱️ Defining When Semaphore Runs a Scheduled Task

Each entry under `semaphoreui_setup_projects_schedules` defines an automated task that Semaphore will run on a recurring schedule.  

The `cron` field specifies **when** the task should execute, using a standard 5‑field UNIX cron expression.

## 📌 Example
{% raw %}
```yaml
semaphoreui_setup_projects_schedules:
  "Home Lab":
    - name: "Nightly Semaphore Backup"
      template: "Backup Semaphore Database"
      cron: "0 3 * * *"
      enabled: true

    - name: "Weekly Cert Rotation"
      template: "Request Certificates for all hosts"
      cron: "0 4 * * 0"
      enabled: true
```
{% endraw %}

---

## 🧩 What the `cron` Field Represents

The `cron` variable defines the schedule using this format:

| Field | Meaning | Example |
|-------|---------|---------|
| `minute` | 0–59 | `0` |
| `hour` | 0–23 | `3` |
| `day of month` | 1–31 | `*` |
| `month` | 1–12 | `*` |
| `day of week` | 0–6 (0 = Sunday) | `0` |

Semaphore accepts standard cron syntax, and the role passes this value directly to the Semaphore API when creating the schedule.

---

## 🕒 Interpreting Your Examples

### **Nightly Semaphore Backup**
{% raw %}
```
cron: "0 3 * * *"
```
{% endraw %}
Runs **every day at 03:00**.

### **Weekly Cert Rotation**
{% raw %}
```
cron: "0 4 * * 0"
```
{% endraw %}
Runs **every Sunday at 04:00**.

---

## 🛠️ How the Role Uses `cron`

When the playbook runs:

- The role reads each schedule entry from `schedules.yml`.
- It resolves the referenced template name to a `template_id`.
- It sends a POST request to `/project/{id}/schedules` with:
  - `name`
  - `template_id`
  - `cron`
  - `enabled`
- Semaphore stores the cron expression and triggers the task accordingly.

No additional transformation or validation is performed by the role—your cron string must be valid UNIX cron syntax.


Absolutely — here’s a **clean, scannable Cron Cheat Sheet** that matches the tone and structure of your existing Runbook page. It drops in neatly right after the explanation of the `cron` field.

---

## 🧭 Cron Cheat Sheet

A quick reference for contributors defining schedules under `semaphoreui_setup_projects_schedules`.

### ⭐ Common Patterns

| Schedule | Cron Expression | Meaning |
|---------|-----------------|---------|
| Every minute | `* * * * *` | Runs once per minute |
| Every 5 minutes | `*/5 * * * *` | Runs every 5 minutes |
| Hourly | `0 * * * *` | At minute 0 of every hour |
| Daily at 03:00 | `0 3 * * *` | Runs every day at 03:00 |
| Daily at midnight | `0 0 * * *` | Runs every day at 00:00 |
| Weekly (Sunday) at 04:00 | `0 4 * * 0` | Runs every Sunday at 04:00 |
| Monthly (1st) at 02:00 | `0 2 1 * *` | Runs on the 1st of each month |
| Yearly (Jan 1) at 00:00 | `0 0 1 1 *` | Runs once per year |

---

### 🔢 Field Reference

| Field | Allowed Values | Notes |
|-------|----------------|-------|
| Minute | `0–59` | `*/N` for intervals |
| Hour | `0–23` | 24‑hour format |
| Day of Month | `1–31` | `*` for any day |
| Month | `1–12` | Or names: `JAN`, `FEB`, etc. |
| Day of Week | `0–6` | `0 = Sunday` |

---

### 🧪 Useful Tricks

- **Intervals:**  
  `*/15 * * * *` → every 15 minutes  
  `0 */6 * * *` → every 6 hours

- **Multiple values:**  
  `0 9,17 * * *` → at 09:00 and 17:00  
  `0 4 * * 1,3,5` → Mon/Wed/Fri at 04:00

- **Ranges:**  
  `0 8-18 * * 1-5` → hourly from 08:00–18:00 on weekdays
