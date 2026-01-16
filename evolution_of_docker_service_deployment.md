---
title: "Evolution of Docker Service Deployment"
---

# 🐳 Evolution of Docker Service Deployment  

This page documents the journey that led to the creation of the **docker_service_deploy** role. It explains how Docker service deployment began in this homelab, how the process evolved over time, and why a shared, DRY‑compliant solution became necessary.

This is both a historical record and a guide for contributors who want to understand *why* this role exists and *what problems it solves*.

---

## 1. The Early Days: Simple Playbooks  
When Docker services were first introduced into the homelab, deployments were straightforward:

- Copy a few configuration files  
- Pull the Docker image  
- Start the container  

A typical playbook looked something like:

- Create a directory  
- Copy a config file  
- Run `docker pull`  
- Run `docker run`  

It was simple, direct, and easy to reason about.

At this stage, each service had its own small playbook, and duplication wasn’t yet a concern.

---

## 2. Growing Complexity: Templates and Orchestration  
As more services were added, the deployment process naturally became more sophisticated:

- Configuration files moved from static files to **Jinja2 templates**  
- Docker commands were replaced with **docker‑compose**  
- Permissions and ownership needed to be enforced  
- Backup directories were added  
- Services required pre‑configuration logic  
- Some services needed post‑configuration steps  
- Image pruning and cleanup became part of the workflow  

Each new service role copied the same pattern:

1. Stop the container  
2. Create config and backup directories  
3. Template config files  
4. Template docker‑compose  
5. Fix permissions  
6. Prune images  
7. Pull the latest image  
8. Start the container  

This pattern repeated across Sonarr, Radarr, Sabnzbd, Lidarr, Tautulli, and others.

---

## 3. The Problem: Copy‑and‑Paste Infrastructure  
As the number of services grew, so did the maintenance burden.

Every new service role required:

- Copying the same tasks  
- Renaming variables  
- Adjusting paths  
- Repeating the same logic  

This created several issues:

### **Duplication**
The same 20–30 lines of YAML appeared in every service role.

### **Inconsistency**
Small differences crept in over time — different permissions, missing tasks, outdated logic.

### **Maintenance Overhead**
Fixing a bug or improving a workflow meant updating *every* service role manually.

### **Contributor Confusion**
New contributors had to understand and maintain a large amount of boilerplate before they could focus on service‑specific logic.

It became clear that this approach wasn’t sustainable.

---

## 4. The Turning Point: Recognizing the Pattern  
Despite differences between services, the core workflow was identical:

{% raw %}
```
stop → pre_config → config → post_config → prune → pull → start
```
{% endraw %}

Only the **inputs** changed:

- Container name  
- Config directory  
- Backup directory  
- Template filenames  
- Optional pre/post hooks  

The orchestration itself was universal.

This realization made the path forward obvious:  
**extract the shared workflow into a reusable role.**

---

## 5. The Solution: `docker_service_deploy`  
The `docker_service_deploy` role was created to centralize the entire deployment workflow into a single, reusable module.

It provides:

### ✔ A shared deployment pipeline  
Stop → configure → prune → pull → start

### ✔ Optional hooks  
For services that need custom logic (e.g., Sabnzbd domain lookup).

### ✔ Parameterized variables  
Each service supplies only what it needs:

- `docker_service_deploy_container_name`  
- `docker_service_deploy_config_dir`  
- `docker_service_deploy_backups_dir`  
- `docker_service_deploy_compose_template`  
- Optional config template + filename  
- Optional pre/post hooks  

### ✔ DRY compliance  
No more copy‑and‑paste.  
No more duplicated logic.  
No more inconsistencies.

### ✔ Contributor‑friendly structure  
Service roles become thin, declarative, and easy to understand.

---

## 6. The Result: A Clean, Maintainable Ecosystem  
With `docker_service_deploy` in place:

- Adding a new service is trivial  
- Updating the deployment workflow happens in one place  
- Contributors focus on service‑specific logic, not boilerplate  
- The homelab gains consistency, reliability, and clarity  
- The entire Docker ecosystem becomes easier to maintain and evolve  

This role represents the natural maturation of the homelab’s automation — from simple scripts to a modular, scalable, DRY‑compliant deployment framework.

---

## 7. Summary  
The `docker_service_deploy` role exists because:

- Docker service deployment became increasingly complex  
- The same workflow was repeated across many roles  
- Copy‑and‑paste maintenance became unsustainable  
- A shared, parameterized, hook‑friendly role was the logical evolution  

It is now the foundation for all Docker service deployments in the homelab.

