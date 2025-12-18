---
title: "Contributor Guide: Adding a New Ansible Inventory"
---

# 👩‍💻 Contributor Guide: Adding a New Ansible Inventory

## 📖 Purpose

This guide explains how to add a new Ansible inventory to the repository and ensure its documentation is **automatically generated and indexed** by the inventory documentation workflow.

The system treats inventories as **source-of-truth artifacts**. Documentation is derived entirely from inventory files and updated automatically by CI.

---

## 🛠 Steps to Add a New Inventory

### 1. **Create the inventory folder**

Each inventory lives in its own directory under `inventory/`.

Create a new folder using a short, descriptive name:

{% raw %}
```
inventory/myservice/
```
{% endraw %}

Naming guidelines:

* Lowercase
* Hyphenated if needed
* Represents a logical service, role, or domain
* Avoid environment-specific names unless required

---

### 2. **Create `inventory.ini`**

Inside the new folder, create an `inventory.ini` file:

{% raw %}
```
inventory/myservice/inventory.ini
```
{% endraw %}

This file must use standard **INI-style Ansible inventory syntax**.

Example:

{% raw %}
```ini
[myservice]
myservice-0 ansible_host=10.0.10.50

[linux:children]
myservice
```
{% endraw %}

This file is the **only required input** for documentation generation.

---

### 3. **Define hosts correctly**

Hosts may include inline variables:

{% raw %}
```ini
myservice-0 vms_proxmox_node=pve-1 ansible_host=10.0.10.50
```
{% endraw %}

Guidelines:

* The **first token** on the line must be the hostname
* All variables must be key=value pairs
* Quoted values and JSON-like strings are supported

✅ These are treated as **one host**, not multiple entries.

---

### 4. **Use groups intentionally**

Groups help drive both playbook targeting and documentation clarity.

Supported group types:

{% raw %}
```ini
[group]
[group:vars]
[group:children]
```
{% endraw %}

Example:

{% raw %}
```ini
[db]
pg-0
pg-1

[db:vars]
postgres_port=5432

[services:children]
db
```
{% endraw %}

All group relationships are reflected in generated documentation.

---

## ⚠️ Duplicate Host Awareness

The documentation generator tracks **all hosts across all inventories**.

If a host is defined in more than one inventory:

* A warning is logged
* The host appears once in the Global Host Index
* All owning inventories are listed

### 📌 Note — Duplicate Hosts

> Defining the same host in multiple inventories can lead to:
>
> * Conflicting variables
> * Unexpected group membership
> * Non-deterministic playbook behavior
>
> Contributors should strongly prefer **one authoritative inventory per host** and refactor shared concerns into groups or variables instead.

If CI is run in `--strict` mode, duplicate hosts will **fail the workflow**.

---

## 5. **Commit your changes**

Once your inventory is added:

{% raw %}
```bash
git add inventory/myservice/
git commit -m "feat(inventory): add myservice inventory"
git push
```
{% endraw %}

No documentation files should be edited manually.

---

## ⚙️ What Happens Next (Automation)

On push or pull request, the **Generate Inventory Docs** GitHub Action runs automatically.

It executes:

{% raw %}
```
scripts/generate_inventory_docs.py
```
{% endraw %}

The script will:

✅ Parse the new inventory
✅ Generate per-inventory documentation at:

{% raw %}
```
docs/inventory/myservice.md
```
{% endraw %}

✅ Update the global inventory index at:

{% raw %}
```
docs/inventory/README.md
inventory/README.md
```
{% endraw %}

✅ Highlight multi-host inventories with 📌
✅ Detect and warn about duplicate hosts

All documentation updates are committed automatically.

---

## 📂 Example

After adding:

{% raw %}
```
inventory/redis/inventory.ini
```
{% endraw %}

With:

{% raw %}
```ini
[redis]
redis-0 vms_proxmox_node=pve-2

[services:children]
redis
```
{% endraw %}

The workflow generates:

* `docs/inventory/redis.md`
* Updated `docs/inventory/README.md`
* Updated `inventory/README.md`

No manual documentation required.

---

## ✅ Contributor Expectations

* Use valid INI syntax
* Place exactly one inventory per folder
* Name inventories clearly and consistently
* Avoid duplicate host definitions across inventories
* Review PR diffs — you should see:

  * New or updated files under `docs/inventory/`
  * Updated inventory indexes

---

## 🧭 Summary

Adding a new inventory is straightforward:

1. Create a folder under `inventory/`
2. Add `inventory.ini`
3. Define hosts and groups cleanly
4. Commit and push

The automation handles everything else — parsing, documentation, indexing, and validation.

