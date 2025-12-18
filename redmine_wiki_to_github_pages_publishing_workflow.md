---
title: "Redmine Wiki to GitHub Pages Publishing Workflow"
---

# 🔄 Redmine Wiki to GitHub Pages Publishing Workflow

This document describes the end‑to‑end workflow used to mirror homelab documentation from **Redmine Wiki** into **GitHub** markdown, and then publish it as a static HTML site to GitHub pages**.

The goal of this setup is:

* ✍️ Keep **Redmine** as the primary authoring source
* 📄 Maintain **Markdown files** in GitHub for version control
* 🌍 Automatically publish clean **HTML docs** using GitHub Pages

---

## 🧩 High‑Level Overview

1. Documentation is authored and maintained in **Redmine Wiki**
2. The Ansible playbook [playbooks/redmine/mirror_wiki.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/redmine/mirror_wiki.yml)
   - converts wiki pages to markdown
   - pushes markdown to GitHub [homelab repo](https://github.com/t3knoid/homelab)
3. A **GitHub Actions** workflow triggers on commit
   - runs **Jekyll** to build static HTML pages from markdown files
   - publishes to **GitHub Pages**
   - pages are available at https://homelab.refol.us/
   
---

## 🗺️ Workflow Diagram

{% raw %}
```text
+------------------+
|  Redmine Wiki    |
|  (Source of      |
|  Truth)          |
+---------+--------+
          |
          | 1. Fetch Wiki Content
          v
+---------+---------+
| Ansible Playbook  |
|                   |
| - mirror_wiki.yml |
|                   |
+---------+---------+
          |
          | 2. Convert to Markdown
          v
+---------+--------+
| Local Git Repo   |
| (Markdown Files) |
+---------+--------+
          |
          | 3. Commit & Push
          v
+---------+--------+
|   GitHub Repo    |
|  (Markdown)      |
+---------+--------+
          |
          | 4. Push Event
          v
+---------+--------+
| GitHub Actions   |
|                  |
| - Jekyll Build   |
| - Pages Deploy   |
+---------+--------+
          |
          | 5. Publish
          v
+------------------+
| GitHub Pages     |
| (Static HTML)    |
+------------------+
```
{% endraw %}

---

## ⚙️ Ansible‑Driven Wiki Mirroring

### Custom Module: [redmine_wiki_mirror.py](https://github.com/t3knoid/refol.general/blob/main/plugins/modules/redmine_wiki_mirror.py)

The heart of the workflow is a custom Ansible module responsible for:

* Authenticating to Redmine
* Fetching one or more wiki pages
* Normalizing Redmine markup
* Converting content to **GitHub‑compatible Markdown**
* Writing Markdown files into the repository workspace
* Part of [refol.general](https://github.com/t3knoid/refol.general/tree/main) Ansible collection.

This module is invoked by a dedicated playbook, making the export process:

* 🔁 Repeatable
* 📦 Automatable

---

## 🚀 GitHub Actions → GitHub Pages

A push to the repository triggers a **GitHub Actions workflow** that:

1. Checks out the repository
2. Runs a Jekyll build using **[_config.ym](https://github.com/t3knoid/homelab/blob/main/_config.yml)**
3. Converts Markdown into static HTML
4. Publishes the site to **[https://homelab.refol.us/](https://homelab.refol.us/)**

Jekyll handles:

* Navigation
* Page layout
* Markdown rendering
* Site structure

---

## 🧱 Jekyll Configuration

The Jekyll configuration (`_config.yml`) defines:

* Site title and metadata
* Markdown processor
* Theme and layout behavior
* GitHub Pages compatibility

This allows the same Markdown files to serve dual purposes:

* 📘 Readable documentation in GitHub
* 🌐 Fully rendered website via Pages

---

## ✅ Benefits of This Approach

* **Single source of truth** (Redmine)
* **Version‑controlled docs** (GitHub)
* **Automated publishing** (GitHub Actions)
* **Portable Markdown** (future‑proof)

---

## 📝 Summary

This workflow cleanly separates concerns:

* ✍️ Authoring → Redmine
* 🔄 Transformation → Ansible
* 📦 Versioning → GitHub
* 🌍 Publishing → GitHub Pages

The result is a robust, auditable, and automation‑friendly documentation pipeline that fits neatly into a homelab ecosystem.
