---
title: "Adding PostgreSQL to a Service — Contributor Guide"
---

# 🐘 Adding PostgreSQL to a Service — Contributor Guide

This guide explains how to integrate PostgreSQL into a new service using Ansible. All database provisioning is performed on the `pgdb` host group, and each service manages its own database creation tasks.

---

## 🔧 Prerequisites

Before adding PostgreSQL support:

- The service must support PostgreSQL as a backend  
- The PostgreSQL server must already be deployed using the `postgresql_setup` role  
- The service must have an Ansible role (e.g., `myservice_setup`)  

---

## 🗂️ Inventory Requirements

Ensure the PostgreSQL host is defined:

{% raw %}
```
[pgdb]
pg-1
```
{% endraw %}

Your service host should be in its own group (e.g., `myservice`).

---

## 🧱 Role Structure

Inside your service role, create:

{% raw %}
```
roles/
  myservice_setup/
    tasks/
      database.yml
```
{% endraw %}

This file will contain all PostgreSQL provisioning tasks.

---

## 📝 Required Variables

Each service must define:

{% raw %}
```
myservice_db_name: myservice
myservice_db_log: myservice_log
myservice_db_user: myservice
myservice_db_password: "{{ vault_myservice_db_password }}"
myservice_pg_host: pg-1
```
{% endraw %}

---

## 🛠️ Database Provisioning Tasks

Use the same pattern as Radarr/Sonarr/Lidarr.

### 📦 Install prerequisites

{% raw %}
```
- name: Ensure PostgreSQL client library is installed
  ansible.builtin.apt:
    name: python3-psycopg2
    state: present
```
{% endraw %}

### Create user

{% raw %}
```
- name: Create PostgreSQL user
  community.postgresql.postgresql_user:
    name: "{{ myservice_db_user }}"
    password: "{{ myservice_db_password }}"
    state: present
  become: true
  become_user: postgres
```
{% endraw %}

### Create databases

{% raw %}
```
- name: Create main database
  community.postgresql.postgresql_db:
    name: "{{ myservice_db_name }}"
    owner: "{{ myservice_db_user }}"
    state: present
  become: true
  become_user: postgres
```
{% endraw %}

### Add pg_hba rules

{% raw %}
```
- name: Allow service host to connect
  community.postgresql.postgresql_pg_hba:
    dest: "/etc/postgresql/{{ postgresql_setup_version }}/main/pg_hba.conf"
    contype: host
    users: all
    source: "{{ myservice_pg_host }}/32"
    databases: all
    method: md5
  notify: Restart PostgreSQL
```
{% endraw %}

### Add .pgpass entry

{% raw %}
```
- name: Ensure .pgpass entry exists
  ansible.builtin.lineinfile:
    path: ~/.pgpass
    line: "{{ myservice_pg_host }}:5432:{{ myservice_db_name }}:{{ myservice_db_user }}:{{ myservice_db_password }}"
    create: yes
    owner: postgres
    group: postgres
    mode: '0600'
    state: present
  become: true
  become_user: postgres
```
{% endraw %}

---

## 💾 Backups

Each service should include a backup task file:

{% raw %}
```
- name: Backup database
  ansible.builtin.shell: |
    pg_dump -U {{ myservice_db_user }} -h {{ myservice_pg_host }} -Fc \
      --file={{ myservice_backup_path }} {{ myservice_db_name }}
  become_user: postgres
```
{% endraw %}

And a cleanup step:

{% raw %}
```
- name: Keep only latest 3 backups
  ansible.builtin.shell: |
    ls -1t {{ myservice_backup_dir }}/*.sqlc | tail -n +4 | xargs -r rm -f
  become_user: postgres
```
{% endraw %}

Backups must be stored on the NFS share mounted via `autofs`.

---

## 🧪 Testing

After deployment:

1. Verify the DB exists  
2. Verify the user can connect  
3. Verify the service can connect  
4. Run a manual backup  
5. Confirm cleanup works
