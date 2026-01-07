---
title: "Documenting Ansible"
---

# 📖 Documenting Ansible

This page centralizes all documentation workflows and contributor guides for Ansible. It provides a single reference point for understanding how playbooks, roles, and inventories are documented, and how to contribute new items consistently.

---

## 🗂 Documentation Workflows

Automated [GitHub Actions](https://github.com/t3knoid/ansible/tree/main/.github/workflows) generate Markdown documentation and maintain global indexes for all Ansible artifacts. Each action runs a dedicated script that performs the documentation generation.

* **Playbooks** – generated via the **[Generate Ansible Playbook Docs GitHub Action](generate_ansible_playbook_docs_github_action.md)**, which runs the **[Generate Playbook Documentation Script](generate_playbook_documentation_script.md)**
* **Roles** – generated via the **[Generate Ansible Role Docs GitHub Action](generate_ansible_role_docs_github_action.md)**, which runs the **[Generate Role Documentation Script](generate_role_documentation_script.md)**
* **Inventories** – generated via the **[Generate Ansible Inventory Docs GitHub Action](generate_ansible_inventory_docs_github_action.md)**, which runs the **[Generate Inventory Documentation Script](generate_inventory_documentation_script.md)**

These scripts enforce metadata, comments, and structured READMEs so that all artifacts are **easy to understand and maintain**.

---

## 🏗 Contributor Guides

Guides for adding new items to the Ansible environment:

* **Adding a New Playbook**: [Contributor Guide Adding a New Ansible Playbook](contributor_guide_adding_a_new_ansible_playbook.md)
* **Adding a New Role**: [Contributor Guide Adding a New Ansible Role](contributor_guide_adding_a_new_ansible_role.md)
* **Adding a New Inventory**: [Contributor Guide Adding a New Ansible Inventory](contributor_guide_adding_a_new_ansible_inventory.md)

Following these guides ensures that your contributions **automatically integrate with the GitHub Actions and scripts** to generate documentation and update global indexes.

---

## 🔗 Quick Reference

For related resources and context:

* [Directory Structure & Conventions](ansible_directory_structure_&_conventions.md)
* [Quick-Start Checklist](ansible_quick-start_checklist.md)
