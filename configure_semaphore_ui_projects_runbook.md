---
title: "Configure Semaphore UI Projects Runbook"
---

# 📘 Configure Semaphore UI Projects Runbook

This section explains how inventory maintainers configure Semaphore UI using the [deploy_semaphoreui.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/semaphoreui/deploy_semaphoreui.yml) playbook.

All configuration lives inside the **inventory**, specifically:

{% raw %}
```
inventory/semaphore/group_vars/all/
```
{% endraw %}

A user does **not** modify the role itself.
They only update the group_vars files to define:

- Projects  
- Repositories  
- Views  
- Keystores  
- Static templates  
- Dynamic template sets  
- Scheduled tasks

Once these variables are defined, running the playbook will fully configure Semaphore UI.

---

# 1. 📁 Where Users Make Changes

Inside your inventory:

{% raw %}
```
inventory/
  semaphore/
    group_vars/
      all/
        projects.yml
        repositories.yml
        views.yml
        keystores.yml
        templates.yml
        dynamic_templates.yml
        schedules.yml
```
{% endraw %}

Each file controls one part of the Semaphore configuration.

| File                    | Purpose                                            |
| ----------------------- | -------------------------------------------------- |
| `projects.yml`          | Define Semaphore projects and metadata             |
| `repositories.yml`      | Define Git repositories for each project           |
| `views.yml`             | Define UI views (tabs) to organize templates       |
| `keystores.yml`         | Define credentials used by templates and schedules |
| `templates.yml`         | Define static task templates                       |
| `dynamic_templates.yml` | Define dynamic template patterns that auto-expand  |
| `schedules.yml`         | Define cron-based scheduled tasks                  |

This structure makes the role **declarative**, **safe**, and **easy to extend**.

---

# 2. 🧩 Required Variables (What Users Must Define)

Below is a breakdown of each file and what the user is expected to configure.

---

## 2.1 `projects.yml` — Define the Projects

Example:

{% raw %}
```yaml
semaphoreui_setup_projects_meta:
  - name: "Home Lab"
    alert_enabled: false
    alert: false
    alert_chat: ""
    max_parallel_tasks: 0
```
{% endraw %}

Each entry defines a **Semaphore project**.

This is the minimal metadata.
Everything else (views, templates, repos, inventories, schedules) is added automatically by the role.

---

## 2.2 `repositories.yml` — Git Repositories for the Project

{% raw %}
```yaml
semaphoreui_setup_projects_repositories:
  "Home Lab":
    - name: "Ansible"
      git_url: "https://github.com/t3knoid/ansible.git"
      git_branch: "main"
```
{% endraw %}

Each repository becomes available to task templates.

---

## 2.3 `views.yml` — UI Views (Tabs) in Semaphore

{% raw %}
```yaml
semaphoreui_setup_projects_views:
  "Home Lab":
    - title: "Linux Checks"
    - title: "Security Updates"
    - title: "Backups"
    - title: "Semaphore"
    - title: "Certs"
    - title: "Deploys"
    - title: "Update Checks"
    - title: "Reboots"
```
{% endraw %}

Views organize templates inside the Semaphore UI.

---

## 2.4 `keystores.yml` — Credentials Used by Templates

{% raw %}
```yaml
semaphoreui_setup_projects_keystores:
  "Home Lab":
    - name: "Semaphore user credentials"
      type: "login_password"
      login_password:
        login: "{{ semaphoreui_setup_semaphore_login }}"
        password: "{{ semaphoreui_setup_semaphore_password }}"
```
{% endraw %}

These credentials are referenced by templates and scheduled tasks.

---

## 2.5 `templates.yml` — Static Task Templates

These are templates explicitly defined by the user.

Example:

{% raw %}
```yaml
semaphoreui_setup_projects_templates:
  "Home Lab":
    - name: "Backup Semaphore Database"
      playbook: "playbooks/semaphoreui/backup_db.yml"
      app: "ansible"
      arguments: "[\"-k\"]"
      inventory: "semaphore"
      credentials:
        - "Ansible vault password"
      repository: "Ansible"
      view: "Backups"
      environment: "Empty"
```
{% endraw %}

Each entry becomes a task template in Semaphore.

---

## 2.6 `dynamic_templates.yml` — Auto‑Generated Templates

Dynamic templates allow you to define a **template pattern** that expands into many templates.

Example:

{% raw %}
```yaml
dynamic_template_sets:
  "Home Lab":
    - name_prefix: "Check connection to"
      playbook: "playbooks/linux/check_connection.yml"
      inventories:
        - redmine
        - ombi
        - plex
      view: "Linux Checks"
      credentials:
        - "Ansible vault password"
      repository: "Ansible"
      environment: "Empty"
```
{% endraw %}

This generates templates like:

- Check connection to redmine  
- Check connection to ombi  
- Check connection to plex  

The role uses your custom filter plugin to expand these.

---

## 2.7 `schedules.yml` — Scheduled Tasks (Cron‑Based Automation)

Scheduled tasks allow Semaphore to automatically run templates on a schedule.

Example:

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

Each schedule:

- References an existing template by **name**
- Defines a **cron expression**
- Can be enabled/disabled

For a list of tasks scheduled to run in Semaphore, see: [Semaphore Scheduled Tasks](semaphore_scheduled_tasks.md)

The role resolves template IDs automatically and creates missing schedules. The [Defining When Semaphore Runs a Scheduled Task](defining_when_semaphore_runs_a_scheduled_task.md) runbook provides further details on how to configure the **cron expression**.

---

# 3. 🚀 Running the Playbook

Once the user updates the group_vars, they run:

{% raw %}
```bash
ansible-playbook -k -i inventory/semaphore/inventory.ini playbooks/semaphoreui/deploy_semaphoreui.yml
```
{% endraw %}

The playbook:

{% raw %}
```yaml
- name: Deploy Semaphore UI
  hosts: semaphore
  gather_facts: true
  become: true
  roles:
    - global
    - sshpass
    - autofs
    - azure_cli_setup
    - entra_id_oauth2
    - semaphoreui_setup
```
{% endraw %}

This triggers the entire automation pipeline:

1. Set up global environment  
2. Install prerequisite tools  
3. Register or update Entra ID application (if OIDC enabled)  
4. Deploy Semaphore UI  
5. Discover inventories  
6. Authenticate to Semaphore  
7. Build the project model  
8. Create/update:
   - Projects  
   - Views  
   - Keystores  
   - Repositories  
   - Inventories  
   - Templates (static + dynamic)  
   - Scheduled tasks  
9. Clean up temporary credentials  

---

# 4. 🧠 What Users Don't Need to Touch

Users **do not** modify:

- The role code  
- The API logic  
- The template expansion logic  
- The inventory discovery logic  
- The schedule creation logic  
- Any files under `roles/semaphoreui_setup/tasks/`  

Everything is driven by group_vars.

---

# 5. 🧑‍💻 Summary for Contributors

To configure Semaphore UI:

1. Edit the group_vars under:

   ```
   inventory/semaphore/group_vars/all/
   ```

2. Define:
   - `projects.yml` → project metadata  
   - `repositories.yml` → Git repos  
   - `views.yml` → UI tabs  
   - `keystores.yml` → credentials  
   - `templates.yml` → static templates  
   - `dynamic_templates.yml` → auto‑generated templates  
   - `schedules.yml` → scheduled tasks

3. Run the playbook.
4. Log into Semaphore UI and verify the results.

This gives contributors a **single, declarative, safe place** to configure everything.
