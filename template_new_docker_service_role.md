---
title: "Template: New Docker Service Role"
---

# 🧩 Template: New Docker Service Role

This template shows the recommended structure and minimal tasks needed to onboard a new Dockerized service using the shared `docker_service_deploy` role.

It includes:

- Folder structure  
- Required variables  
- Optional hooks  
- Example templates  
- A ready‑to‑use `tasks/main.yml`  

Everything is intentionally minimal so contributors focus only on service‑specific details.

---

## 📁 **Folder Structure**

{% raw %}
```
roles/<service_name>/
├── defaults/
│   └── main.yml
├── tasks/
│   ├── main.yml
│   ├── pre_config.yml        # optional
│   └── post_config.yml       # optional
└── templates/
    ├── docker-compose.yml.j2
    └── <service_config>.j2   # optional
```
{% endraw %}

---

## 📄 **defaults/main.yml**

This file defines service‑specific variables and paths.  
Only the required variables must be set; optional ones can be omitted.

{% raw %}
```yaml
# Required
<service_name>_container_name: "<service_name>"
<service_name>_config_dir: "/opt/<service_name>"
<service_name>_backups_dir: "/nfs/backups/<service_name>"

# Required: docker-compose template
<service_name>_compose_template: "docker-compose.yml.j2"

# Optional: single config template (legacy)
<service_name>_config_template: null
<service_name>_config_filename: null

# Optional: multi-config templates (preferred)
<service_name>_config_templates: []

# Optional hooks (paths set at runtime via set_fact)
<service_name>_pre_config: null
<service_name>_post_config: null
```
{% endraw %}

Contributors only need to adjust these values.

---

## 📄 **tasks/main.yml**

This is the core of the service role.  
It prepares hook paths (if present) and imports the shared deployment workflow.

{% raw %}
```yaml
# Optional: compute pre-config hook path
- name: Set pre-config hook path
  ansible.builtin.set_fact:
    <service_name>_pre_config: "{{ role_path }}/tasks/pre_config.yml"
  when: <service_name>_pre_config is not defined or <service_name>_pre_config != ""

# Optional: compute post-config hook path
- name: Set post-config hook path
  ansible.builtin.set_fact:
    <service_name>_post_config: "{{ role_path }}/tasks/post_config.yml"
  when: <service_name>_post_config is not defined or <service_name>_post_config != ""

- name: Deploy <service_name> using docker_service_deploy
  import_role:
    name: docker_service_deploy
  vars:
    docker_service_deploy_container_name: "{{ <service_name>_container_name }}"
    docker_service_deploy_config_dir: "{{ <service_name>_config_dir }}"
    docker_service_deploy_backups_dir: "{{ <service_name>_backups_dir }}"
    docker_service_deploy_compose_template: "{{ <service_name>_compose_template }}"

    # Optional list of config templates
    docker_service_deploy_config_templates: "{{ <service_name>_config_templates }}"

    # Optional hooks (full paths computed above)
    docker_service_deploy_pre_config: "{{ <service_name>_pre_config }}"
    docker_service_deploy_post_config: "{{ <service_name>_post_config }}"
```
{% endraw %}

This keeps the service role thin, declarative, and easy to maintain.

---

## 🧩 **Optional: tasks/pre_config.yml**

Only create this file if the service needs custom logic before configuration.

Example:

{% raw %}
```yaml
- name: Perform pre-configuration for <service_name>
  debug:
    msg: "Running pre-config hook for <service_name>"
```
{% endraw %}

Enable it in `defaults/main.yml`:

{% raw %}
```yaml
<service_name>_pre_config: true
```
{% endraw %}

---

## 🧩 **Optional: tasks/post_config.yml**

Runs after configuration templating.

{% raw %}
```yaml
- name: Perform post-configuration for <service_name>
  debug:
    msg: "Running post-config hook for <service_name>"
```
{% endraw %}

Enable it in `defaults/main.yml`:

{% raw %}
```yaml
<service_name>_post_config: true
```
{% endraw %}

---

## 🧩 **templates/docker-compose.yml.j2**

A minimal example contributors can expand:

{% raw %}
```yaml
version: "3.9"

services:
  {{ <service_name>_container_name }}:
    image: <image>:latest
    container_name: {{ <service_name>_container_name }}
    restart: unless-stopped
    volumes:
      - "{{ <service_name>_config_dir }}:/config"
    ports:
      - "8080:8080"
```
{% endraw %}

---

## 🧩 **Optional: templates/<service_config>.j2**

Only needed if the service has one or more standalone config files.

Example:

{% raw %}
```ini
# Example config for <service_name>
setting1 = value1
setting2 = value2
```
{% endraw %}

Add it to the list:

{% raw %}
```yaml
<service_name>_config_templates:
  - src: "<service_config>.j2"
    dest: "<service_config>"
    mode: "0640"
```
{% endraw %}

---

## 🎯 **Contributor Workflow Summary**

To add a new service:

1. Create `roles/<service_name>/`
2. Add `defaults/main.yml` with service‑specific paths and filenames
3. Add `templates/docker-compose.yml.j2`
4. (Optional) Add one or more config templates  
5. (Optional) Add pre/post config hooks  
6. Use the shared `docker_service_deploy` role in `tasks/main.yml`

