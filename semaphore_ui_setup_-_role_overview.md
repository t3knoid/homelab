# 🛠️ **Semaphore UI Setup – Role Overview**

The `semaphoreui_setup` role configures the [Semaphore UI](https://docs.semaphoreui.com/administration-guide/api/) application on designated hosts.
It automates the creation and management of:

* Projects
* Repositories
* Key stores
* Views
* Inventories
* Task templates (static & dynamic)
* Environments

This role assumes Semaphore UI is already installed and reachable on the target host.

---

# 💻 **Supported Hosts**

**Host group:** `semaphore`
The role uses:

* `become: true`
* fact gathering enabled

---

# 📂 **Inventory Structure**

All project-related configuration is defined **per inventory**, usually under:

```
inventory/semaphore/group_vars/semaphore/
```

Recommended layout (simplified, no redundant prefixes):

```
group_vars/semaphore/
  ├── projects.yml
  ├── repositories.yml
  ├── keystores.yml
  ├── views.yml
  ├── templates.yml
  └── dynamic_templates.yml
```

Each file provides one piece of the full project structure.
`dynamic_templates.yml` contains dynamic template sets assigned **per project**.

---

# 📌 **Variable: `semaphoreui_setup_projects`**

The role assembles this variable dynamically from component files and dynamic template sets.
It becomes the **complete, consolidated list of projects** including everything tied to them.

**Example structure (static + dynamic templates):**

```yaml
semaphoreui_setup_projects:
  - name: "Home Lab"
    alert_enabled: false
    max_parallel_tasks: 0

    repositories:
      - name: "Ansible"
        git_url: "https://github.com/t3knoid/ansible.git"
        git_branch: "main"

    keystores:
      - name: "Semaphore user credentials"
        type: "login_password"
        login_password:
          login: "{{ semaphoreui_setup_semaphore_login }}"
          password: "{{ semaphoreui_setup_semaphore_password }}"

    views:
      - title: "Linux Checks"
      - title: "Security Updates"

    templates:
      # Static templates
      - name: "Backup Semaphore Database"
        playbook: "playbooks/semaphoreui/backup_db.yml"
        inventory: "semaphore"
        credentials:
          - "Ansible vault password"
        view: "Backups"
        environment: "Empty"

      # Dynamic templates
      - name: "Check connection to Plex"
        playbook: "playbooks/linux/check_connection.yml"
        inventory: "plex"
        credentials:
          - "Ansible vault password"
        view: "Linux Checks"
        environment: "Empty"
```

---

# 📌 **Variable: `dynamic_template_sets`**

Dynamic templates are now **grouped by project**:

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

    - name_prefix: "Deploy security updates to"
      playbook: "playbooks/linux/deploy_updates.yml"
      inventories:
        - plex
        - ombi
        - services
      view: "Security Updates"
      credentials:
        - "Ansible vault password"
      repository: "Ansible"
      environment: "Empty"
```

* Each template set applies only to its **specified project**.
* Templates are expanded across all inventories listed in `inventories`.
* Each template automatically combines `name_prefix + inventory` for the task name.

---

# ⚙️ **Role Task Structure**

The role’s entry point:

```
roles/semaphoreui_setup/tasks/main.yml
```

Imports the setup entry point:

```yaml
- import_tasks: setup/main.yml
```

All setup logic resides under:

```
roles/semaphoreui_setup/tasks/setup/
```

### **Task Files and Their Purpose**

| Task File                | Purpose                                                                             |
| ------------------------ | ----------------------------------------------------------------------------------- |
| `create_api_token.yml`   | Logs in as admin, generates API token, logs out.                                    |
| `enum_users.yml`         | Enumerates existing Semaphore users.                                                |
| `setup_projects.yml`     | Creates projects from `semaphoreui_setup_projects`.                                 |
| `setup_project.yml`      | Processes one project and triggers all subcomponents.                               |
| `setup_views.yml`        | Ensures project views exist.                                                        |
| `setup_keystores.yml`    | Creates key stores for the project.                                                 |
| `setup_repositories.yml` | Registers project repositories and attaches keys.                                   |
| `setup_inventories.yml`  | Registers inventories used in templates.                                            |
| `setup_templates.yml`    | Iterates over **both static and dynamic templates**.                                |
| `setup_template.yml`     | Creates a single task template (playbook, inventory, repo, view, env, credentials). |

---

# 🔄 **Execution Workflow**

### **1. Inventory Discovery**

* Finds available Ansible inventory files
* Builds `semaphoreui_setup_inventories`
* Makes this list available for template assignment

### **2. Authentication**

* Reads admin password from disk
* Creates an API token via the Semaphore API
* Stores token for subsequent requests

### **3. User Enumeration**

* Reads the existing list of users
* Avoids re-creating users unless explicitly configured

### **4. Project Creation**

* Reads metadata from `projects_meta.yml`
* Compares with existing projects
* Creates missing projects
* Passes new project IDs to downstream tasks

### **5. Component Setup (Per Project)**

Each project is processed using `setup_project.yml`, which calls:

* `setup_views.yml`
* `setup_keystores.yml`
* `setup_repositories.yml`
* `setup_inventories.yml` → `setup_inventory.yml`
* `setup_templates.yml` → `setup_template.yml` (handles static + dynamic)

---

# 📌 **Dynamic Template Handling**

1. Static templates come directly from `semaphoreui_setup_projects_templates`.
2. Dynamic templates come from `dynamic_template_sets` via the [Ansible_Filter_extract_templates_for_project](ansible_filter_extract_templates_for_project.md).
3. Both sets are **appended and deduplicated** automatically before creating tasks in Semaphore UI.

---

# 🗂️ **Workflow-to-Task Mapping**

| Workflow Action       | Role Task File                                  |
| --------------------- | ----------------------------------------------- |
| Create project views  | `setup_views.yml`                               |
| Add project keystores | `setup_keystores.yml`                           |
| Add repositories      | `setup_repositories.yml`                        |
| Register inventories  | `setup_inventories.yml` → `setup_inventory.yml` |
| Add task templates    | `setup_templates.yml` → `setup_template`        |

---

# 🗺️ **Flowchart Overview**

```
┌──────────────────────────────────────────────┐
│         Project Definition Files             │
│  • projects.yml                              │
│  • repositories.yml                          │
│  • keystores.yml                             │
│  • views.yml                                 │
│  • templates.yml                             │
│  • dynamic_templates.yml                     │
└───────────────────────────────┬──────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────┐
│     Playbook: setup_semaphoreui.yml          │
│     hosts: semaphore                         │
│     roles:                                   │
│       - semaphoreui_setup                    │
└───────────────────────────────┬──────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────┐
│ Role: semaphoreui_setup                      │
│ Entry: tasks/setup/main.yml                  │
│  • Build inventories                         │
│  • Authenticate                              │
│  • Enumerate users                           │
│  • Run setup_projects.yml                    │
└───────────────────────────────┬──────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────┐
│Consolidation into semaphoreui_setup_projects │
│  • Static templates                          │
│  • Dynamic templates                         │
└───────────────────────────────┬──────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────┐
│ setup_projects.yml                           │
│  • Create projects                           │
│  • Loop → setup_project.yml                  │
└───────────────────────────────┬──────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────┐
│ setup_project.yml                            │
│  • Create views                              │
│  • Create keystores                          │
│  • Create repositories                       │
│  • Create inventories                        │
│  • Create templates (static + dynamic)       │
└───────────────────────────────┬──────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────┐
│ setup_template.yml                           │
│  • Resolve inventory/repo/view/env IDs       │
│  • Resolve vault credentials                 │
│  • Create template                           │
└──────────────────────────────────────────────┘
```