---
title: "Redmine Configuration"
---

# Redmine Configuration

Redmine plays a central role in the homelab environment—serving as the hub for issue tracking, documentation, project visibility, and integration with infrastructure-as-code workflows. This page details how Redmine is integrated with **Active Directory for authentication** and how it interfaces with a **local Git mirror** of the homelab's Ansible repository.

The goal: a fast, secure, and tightly integrated project management platform.

---

# **🔐 1. LDAP Authentication (Active Directory Integration)**

Redmine authenticates users directly against the **refol.us** Active Directory domain. This provides:

* Unified identity management
* Automatic user provisioning
* Consistent credentials across the homelab

Below are the validated LDAP settings used in the environment:

| Setting                      | Value                                                     |
| ---------------------------- | --------------------------------------------------------- |
| **Name**                     | refol.us                                                  |
| **Host**                     | 192.168.2.251                                             |
| **Port**                     | 389                                                       |
| **Account**                  | [ldap_bind_user@refol.us](mailto:ldap_bind_user@refol.us) |
| **Base DN**                  | CN=Users,DC=refol,DC=us                                   |
| **On-the-fly user creation** | Enabled                                                   |
| **Login attribute**          | sAMAccountName                                            |
| **Firstname attribute**      | givenName                                                 |
| **Lastname attribute**       | sn                                                        |
| **Email attribute**          | mail                                                      |

These values follow Redmine’s recommended LDAP guidelines and are aligned with the homelab’s AD structure.
*Reference:* Redmine LDAP Configuration — [https://www.redmine.org/projects/redmine/wiki/RedmineLDAP](https://www.redmine.org/projects/redmine/wiki/RedmineLDAP)

---

# **📁 2. Repository Integration (Local Git Mirror of the GitHub Ansible Repo)**

Redmine integrates directly with a **local bare Git mirror** of the GitHub-based Ansible repository. This design provides:

* Ultra-fast access to source code
* No dependency on GitHub availability
* An authoritative, locally cached representation of all changes
* Automatic updates via cron

The mirrored repository resides in:

{% raw %}
```
/data/redmine/repos
```
{% endraw %}

This ensures Redmine can render diffs, browse files, and track changesets with minimal latency.

---

## **2.1 Preparing the Repository Directory**

Create the directory and set correct ownership:

{% raw %}
```bash
sudo mkdir -p /data/redmine/repos
sudo chown redmine:redmine /data/redmine/repos
```
{% endraw %}

Switch to the `redmine` user:

{% raw %}
```bash
sudo -u redmine -i
```
{% endraw %}

---

## **2.2 Creating the Bare Repository Mirror**

From within the repository folder:

{% raw %}
```bash
cd /data/redmine/repos
git clone --bare https://github.com/t3knoid/ansible.git
```
{% endraw %}

Once cloned, instruct Redmine to fetch and index the repository’s changesets:

{% raw %}
```bash
cd /data/redmine/redmine-6.0.5/
./bin/rails runner "Repository.fetch_changesets" -e production
```
{% endraw %}

---

## **2.3 Keeping the Mirror Updated**

To sync the bare mirror with GitHub:

{% raw %}
```bash
git fetch origin +refs/heads/*:refs/heads/* && git reset --soft
```
{% endraw %}

Automate this with a cron job that runs every 10 minutes:

{% raw %}
```bash
sudo crontab -u redmine -e
```
{% endraw %}

Add:

{% raw %}
```
*/10 * * * * cd /data/redmine/repos/ansible.git && git fetch origin +refs/heads/*:refs/heads/* && git reset --soft
```
{% endraw %}

This ensures Redmine always displays the latest commits, branches, and diffs without manual intervention.



