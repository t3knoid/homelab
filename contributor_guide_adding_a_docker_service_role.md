---
title: "Contributor Guide: Adding a Docker Service Role"
---

# 🐳 Contributor Guide: Adding a Docker Service Role

This guide provides a process of using the shared role `docker_service_deploy` when creating a new Docker-based service role. The `docker_service_deploy` role provides a **shared, reusable deployment workflow** for Docker‑based services in the homelab. It eliminates duplication across service roles by centralizing common tasks such as stopping containers, preparing configuration directories, templating files, pruning images, pulling updates, and starting containers.

Service‑specific roles (e.g., Sonarr, Sabnzbd, Radarr) import this role and supply only the variables and optional hooks they need.

To read on the evolution of this role,
👉 see: the **[Evolution of Docker Service Deployment](evolution_of_docker_service_deployment.md)** page.

---

## 📦 **What This Role Does**

The role implements the following workflow:

1. **Stop the existing container**  
   Uses pure Docker CLI to ensure compatibility even when docker‑compose is not available.

2. **Run optional pre‑config hook**  
   Allows a service to perform custom logic before configuration (e.g., Sabnzbd domain lookup).

3. **Configure the service**  
   - Creates config and backup directories  
   - Optionally templates a service config file  
   - Always templates the docker‑compose file  
   - Ensures correct ownership and permissions  

4. **Run optional post‑config hook**  
   For services that need additional steps after templating.

5. **Prune unused Docker images**  
   Removes dangling images and optionally all images if desired.

6. **Pull the latest image**  
   Uses docker‑compose to fetch updated images.

7. **Start the container**  
   Brings the service up using docker‑compose.

This workflow is consistent across all services, ensuring predictable behavior and reducing maintenance overhead.

To quickly jump into developing a new service role,

👉 see the [Template New Docker Service Role](template_new_docker_service_role.md) page, which provides ready‑to‑use file templates for building a Docker‑based service role using this approach.

---

## 🧩 **Required Variables**

Each service role must define the following:

| Variable | Description |
|---------|-------------|
| `docker_service_deploy_container_name` | Name of the Docker container (e.g., `"sonarr"`) |
| `docker_service_deploy_config_dir` | Path to the service’s config directory |
| `docker_service_deploy_backups_dir` | Path to the service’s backup directory |
| `docker_service_deploy_compose_template` | Jinja2 template for `docker-compose.yml` |

Example:

{% raw %}
```yaml
docker_service_deploy_container_name: "sonarr"
docker_service_deploy_config_dir: "{{ sonarr_setup_config_dir }}"
docker_service_deploy_backups_dir: "{{ sonarr_setup_backups_dir }}"
docker_service_deploy_compose_template: "docker-compose.yml.j2"
```
{% endraw %}

---

## 📝 **Optional Variables**

These allow services to customize behavior without modifying the shared role.

### **Optional config templates**

Some services have one or more standalone configuration files (e.g., `config.xml`, `sabnzbd.ini`, `database.json`). Others rely entirely on environment variables or the docker‑compose file.

To support all cases, the role accepts **a list of config templates**, each with its own source, destination filename, and optional mode.

| Variable | Description |
|----------|-------------|
| `docker_service_deploy_config_templates` | A list of config templates to render into the service’s config directory (optional) |

Each item in the list supports:

- `src` — the Jinja2 template filename  
- `dest` — the output filename  
- `mode` — optional file mode (defaults to `0640`)

Example:

{% raw %}
```yaml
docker_service_deploy_config_templates:
  - src: "database.json.j2"
    dest: "database.json"
    mode: "0600"
  - src: "settings.json.j2"
    dest: "settings.json"
```
{% endraw %}

If the list is omitted or empty, the config‑templating step is skipped.

---

## 🧩 **Optional hooks**

Hooks allow services to inject custom logic before or after configuration.  
They are useful for tasks such as computing dynamic values, preparing files, or performing service‑specific adjustments.

### **How hooks work**

Each service role may provide one or both of the following:

| Variable | Description |
|----------|-------------|
| `docker_service_deploy_pre_config` | Absolute path to a task file to run *before* configuration |
| `docker_service_deploy_post_config` | Absolute path to a task file to run *after* configuration |

Hooks are executed only when the variable is set to a truthy value.

---

## 🧠 **Important: Hooks must provide a full path**

Because the shared `docker_service_deploy` role cannot reliably determine where a service role stores its hook files, **the service role must compute the full path itself**.

This must be done inside a task (not in `defaults/`), so that `role_path` resolves to the *service role’s* directory.

Example inside a service role:

{% raw %}
```yaml
- name: Set pre-config hook path
  ansible.builtin.set_fact:
    <service_name>_pre_config: "{{ role_path }}/tasks/pre_config.yml"
```
{% endraw %}

Then pass it to the shared role:

{% raw %}
```yaml
docker_service_deploy_pre_config: "{{ <service_name>_pre_config }}"
```
{% endraw %}

---

## ✔ Example usage

Inside `roles/sabnzbd_setup/tasks/main.yml`:

{% raw %}
```yaml
- name: Set SABnzbd pre-config hook path
  ansible.builtin.set_fact:
    sabnzbd_setup_pre_config: "{{ role_path }}/tasks/pre_config.yml"

- name: Deploy SABnzbd using docker_service_deploy
  import_role:
    name: docker_service_deploy
  vars:
    docker_service_deploy_pre_config: "{{ sabnzbd_setup_pre_config }}"
```
{% endraw %}

Inside the shared role (`docker_service_deploy`):

{% raw %}
```yaml
- name: Run pre-config hook
  ansible.builtin.include_tasks: "{{ docker_service_deploy_pre_config }}"
  when: docker_service_deploy_pre_config
```
{% endraw %}

---

### **Owner**

Defaults to the first user in `users_list`, but can be overridden:

{% raw %}
```yaml
docker_service_deploy_owner: "media"
```
{% endraw %}

💡 **Tip: `users_list` is typically defined in the inventory vault.**

---

## 🧱 **Role Structure**

{% raw %}
```
roles/docker_service_deploy/
├── defaults/
│   └── main.yml
├── tasks/
│   ├── main.yml
│   ├── stop.yml
│   ├── config.yml
│   ├── prune.yml
│   ├── pull.yml
│   └── start.yml
```
{% endraw %}

Each file is small, focused, and easy to override or extend.

---

## 🚀 **How to Use This Role in a Service Role**

### **Simple service (Sonarr)**

{% raw %}
```yaml
- name: Deploy Sonarr Docker Service
  ansible.builtin.import_role:
    name: docker_service_deploy
  vars:
    docker_service_deploy_container_name: "sonarr"
    docker_service_deploy_config_dir: "{{ sonarr_setup_config_dir }}"
    docker_service_deploy_backups_dir: "{{ sonarr_setup_backups_dir }}"
    docker_service_deploy_config_templates:
      - src: "config.xml.j2"
        dest: "config.xml"
        mode: "0640"
    docker_service_deploy_compose_template: "docker-compose.yml.j2"
```
{% endraw %}

---

### **Service with custom logic (Sabnzbd)**

`tasks/pre_config.yml`:

{% raw %}
```yaml
- name: Get Sabnzbd site hostname
  ansible.builtin.set_fact:
    sabnzbd_setup_domain_name: >-
      {{ rproxy_setup_sites
        | selectattr('server_name', 'defined')
        | selectattr('server_name', 'search', '^sabnzbd')
        | map(attribute='server_name')
        | first
        | default('', true) }}
```
{% endraw %}

`tasks/main.yml`:

{% raw %}
```yaml
- name: Deploy SABnzbd Docker Service
  ansible.builtin.import_role:
    name: docker_service_deploy
  vars:
    docker_service_deploy_container_name: "sabnzbd"
    docker_service_deploy_pre_config: pre_config.yml
    docker_service_deploy_config_dir: "{{ sabnzbd_setup_config_dir }}"
    docker_service_deploy_backups_dir: "{{ sabnzbd_setup_backups_dir }}"
    docker_service_deploy_config_templates:
      - src: "sabnzbd.ini.j2"
        dest: "sabnzbd.ini"
        mode: "0640"
    docker_service_deploy_compose_template: "docker-compose.yml.j2"
```
{% endraw %}

---

## 🧼 **Contributor Expectations**

- Do **not** duplicate logic already provided by this role.  
- Use hooks (`pre_config`, `post_config`) for service‑specific behavior.  
- Keep service roles declarative: set variables, provide templates, and let this role handle the workflow.  
- Avoid modifying this role unless the change benefits *all* services.  
- When adding a new service, follow the examples above for consistency.

---

## 🧭 **Design Philosophy**

This role exists to:

- enforce consistency  
- reduce duplication  
- simplify onboarding  
- make service roles thin and readable  
- centralize Docker deployment logic  
- support optional complexity without clutter  

It reflects the homelab’s broader principles: **modular, predictable, DRY, and contributor‑friendly**.