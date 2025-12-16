# 🧰 Configuring Semaphore UI Projects


This page documents how to configure **Semaphore UI** using inventory-based variables.
All project definitions live inside inventory group vars under:

```
inventory/<env>/group_vars/semaphore/
```

The role `semaphoreui_setup` remains generic and only handles *how* to configure Semaphore UI.
Your inventory controls *what* gets created.

All variables follow:

```
semaphoreui_setup_<category>
```

---

## 📁 Inventory Folder Layout

Inside your environment’s inventory:

```
inventory/
└── semaphore/
    └── group_vars/
        └── semaphore/
            ├── projects.yml
            ├── repositories.yml
            ├── keystores.yml
            ├── views.yml
            ├── templates.yml
```

Each file contains one category of Semaphore UI configuration.

---

## 🧩 1. Define Projects

`inventory/semaphore/group_vars/semaphore/projects.yml`:

```yaml
semaphoreui_setup_projects_meta:
  - name: "Home Lab"
    alert_enabled: false
    alert: false
    alert_chat: ""
    max_parallel_tasks: 0

  - name: "Production"
    alert_enabled: true
    alert: true
    alert_chat: "alerts-prod"
    max_parallel_tasks: 3
```

Only per-project metadata belongs here.

---

## 📚 2. Repositories

`inventory/semaphore/group_vars/semaphore/repositories.yml`:

```yaml
semaphoreui_setup_projects_repositories:
  "Home Lab":
    - name: "Ansible"
      git_url: "https://github.com/t3knoid/ansible.git"
      git_branch: "main"

  "Production": []
```

Project names **must match exactly**, including spaces.

---

## 🔑 3. Keystores

`inventory/semaphore/group_vars/semaphore/keystores.yml`:

```yaml
semaphoreui_setup_projects_keystores:
  "Home Lab": []
  "Production": []
```

---

## 👁 4. Views

`inventory/semaphore/group_vars/semaphore/views.yml`:

```yaml
semaphoreui_setup_projects_views:
  "Home Lab": []
  "Production": []
```

---

## 📄 5. Templates

`inventory/semaphore/group_vars/semaphore/templates.yml`:

```yaml
semaphoreui_setup_projects_templates:
  "Home Lab": []
  "Production": []
```

---

## 🔧 6. Role Task Entry Point

Inside your role:

`roles/semaphoreui_setup/tasks/main.yml`:

```yaml
- name: Execute Semaphore UI setup tasks
  ansible.builtin.include_tasks: setup/main.yml
```

This is the **only** task reference required in the role.
All configuration variables come from your inventory.

---

## ▶️ 7. Playbook That Executes the Setup

Your playbook lives at:

```
playbooks/semaphoreui/setup_semaphoreui.yml
```

Example structure:

```yaml
- name: Configure Semaphore UI
  hosts: semaphore
  gather_facts: false

  roles:
    - semaphoreui_setup
```

This playbook loads the inventory vars, passes them to the role, and the role runs `setup/main.yml`.

---

