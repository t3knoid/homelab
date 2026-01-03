---
title: "Home Lab Wiki Mirror to a Static Website Workflow"
---

# 📚 Home Lab Wiki Mirror to a Static Website Workflow

This page documents the process of **mirroring the home lab Redmine wiki to GitHub as Markdown** and converting it into a **static HTML website** available at [https://homelab.refol.us](https://homelab.refol.us).

---

## 1. Overview

This workflow automates the lifecycle of mirroring the lab wiki to a static website:

1. **Redmine Wiki**: Original source of content.
2. **Ansible Playbook**: Uses the `redmine_wiki_mirror` module to export pages as Markdown and commit to GitHub.
3. **GitHub Repository**: Stores Markdown pages at [https://github.com/t3knoid/homelab](https://github.com/t3knoid/homelab).
4. **GitHub Actions**: Converts Markdown to static HTML.
5. **GitHub Pages**: Hosts the static HTML site at [https://homelab.refol.us](https://homelab.refol.us).

**Key Benefits:**

* Version-controlled documentation.
* Easy integration with CI/CD workflows.
* Consistent static website for easy browsing.

---

## 2. Redmine Wiki to GitHub Markdown

### Ansible Module: `redmine_wiki_mirror`

* Located in: [refol.general/plugins/modules/redmine_wiki_mirror.py](https://github.com/t3knoid/refol.general/blob/main/plugins/modules/redmine_wiki_mirror.py)
* Documentation: [redmine_wiki_mirror.md](https://github.com/t3knoid/refol.general/blob/main/docs/redmine_wiki_mirror.md)
* Purpose:

  * Fetch wiki pages from Redmine.
  * Convert to Markdown.
  * Commit changes to a GitHub repository.

### Example Usage

{% raw %}
```yaml
- name: Mirror Redmine Wiki to GitHub
  hosts: localhost
  connection: local
  gather_facts: no
  tasks:
    - name: Export Redmine wiki and commit to GitHub
      refol.general.redmine_wiki_mirror:
        redmine_url: "https://redmine.example.com"
        project: "homelab"
        github_repo: "t3knoid/homelab"
        github_branch: "main"
        github_token: "{{ lookup('env', 'GITHUB_TOKEN') }}"
```
{% endraw %}

**Notes:**

* All Markdown files in the repository root are **replaced** with the mirrored content on each run.
* The `README.md` file is **protected** and is **not deleted**, as it documents the repository itself.
* Only wiki pages from Redmine are mirrored; repository documentation files remain intact.

---

## 3. GitHub Repository Structure

The mirrored Markdown files are stored **flat in the root folder**:

{% raw %}
```
/README.md          # Repository documentation, protected
/index.md
/dc.md
/pihole.md
/playbooks.md
/roles.md
...
```
{% endraw %}

* Only the wiki content files are replaced during a mirror.
* The repository README provides details of the GitHub workflow converting Markdown → HTML.

---

## 4. GitHub Actions: Markdown → Static HTML

The repository includes a GitHub Actions workflow that:

1. Watches for commits to the Markdown files.
2. Converts Markdown to a static HTML site.
3. Pushes the site to the `gh-pages` branch.
4. Serves the website at [https://homelab.refol.us](https://homelab.refol.us).

**Workflow highlights (from README):**

* Uses a static site generator (details in the workflow README).
* Automatically deploys updates whenever the Redmine wiki is mirrored.
* Ensures the live site is always in sync with Redmine.

---

## 5. Running the Wiki Sync

To mirror the Redmine wiki to GitHub:

1. Set the inventory variable:

{% raw %}
```bash
INV=inventory/redmine/inventory.ini
```
{% endraw %}

2. Run the Ansible playbook:

{% raw %}
```bash
ansible-playbook -k -i $INV playbooks/redmine/mirror_wiki.yml
```
{% endraw %}

**Notes:**

* The `-k` option prompts for the SSH password if needed.
* This playbook uses the `redmine_wiki_mirror` module to fetch wiki pages, convert them to Markdown, and commit them to the GitHub repository.
* All Markdown files in the root of the repository are replaced during the sync, except `README.md` which is protected.

After the playbook completes, the **GitHub Actions workflow** will automatically convert the Markdown files to HTML and deploy the static site at [https://homelab.refol.us](https://homelab.refol.us).

---

## 6. Static Site Generation & Theme

* The repository uses **Jekyll** to convert Markdown pages into HTML.
* The **Minima theme** is applied, with some customizations such as:

  * A **hamburger menu** for navigation on small screens.
  * Minor CSS tweaks to match the home lab branding and improve usability.

All Markdown content in the root folder is processed by Jekyll during the GitHub Actions workflow to generate the static HTML site served at [https://homelab.refol.us](https://homelab.refol.us).

---

## 7. ASCII Diagram of the Workflow

{% raw %}
```
   ┌────────────────┐
   │  Redmine Wiki  │
   └───────┬────────┘
           │ Mirror
           ▼
   ┌───────────────────────────────┐
   │ Ansible Playbook +            │
   │ redmine_wiki_mirror module    │
   │                               │
   │ - Fetch wiki pages            │
   │ - Convert to Markdown         │
   │ - Commit to GitHub            │
   └───────┬───────────────────────┘
           │ Push
           ▼
   ┌───────────────────────────────┐
   │ GitHub Repository (homelab)   │
   │ Root folder contains Markdown │
   │ README.md is protected        │
   └───────┬───────────────────────┘
           │ Trigger
           ▼
   ┌───────────────────────────────┐
   │ GitHub Actions Workflow       │
   │                               │
   │ - Converts Markdown → HTML    │
   │ - Pushes HTML to gh-pages     │
   └───────┬───────────────────────┘
           │ Serve
           ▼
   ┌───────────────────────────────┐
   │ GitHub Pages                  │
   │ https://homelab.refol.us      │
   └───────────────────────────────┘
```
{% endraw %}