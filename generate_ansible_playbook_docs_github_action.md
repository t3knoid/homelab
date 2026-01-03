---
title: "️ GitHub Action: Generate Playbook Docs"
---

# ⚙️ GitHub Action: Generate Playbook Docs

## 📖 Purpose

This workflow ensures that documentation for all Ansible roles is **automatically generated and kept up to date**. Whenever code is pushed or a pull request is opened, the workflow runs the [Generate Playbook Documentation Script](generate_playbook_documentation_script.md) script, which regenerates per‑playbook markdown files, builds folder‑level summaries, maintains a global index of playbooks, and commits the changes back to the repository.


## 🛠 Workflow File
Located at: `.github/workflows/generate-playbook-docs.yml`

{% raw %}
```yaml
name: Generate Ansible Playbook Docs

on:
  push:
    branches:
      - main
  pull_request:

jobs:
  generate-playbook-docs:
    # Only run the job logic when the branch is main
    if: github.ref == 'refs/heads/main'
    
    runs-on: ubuntu-latest

    steps:
      # Checkout the repo
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # needed for committing back

      # Set up Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # Install dependencies (if any)
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # Run the documentation generator
      - name: Generate playbook docs
        run: |
          python ./scripts/generate_playbook_docs.py

      - name: Commit and push changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git pull origin main
          git add playbooks/README.md docs/playbooks/README.md docs/playbooks/*.md

          if ! git diff --cached --quiet; then
            git commit -m "chore(docs): auto-generate playbook documentation"
            git push origin main
          else
            echo "No documentation changes to commit."
          fi
```
{% endraw %}

---

## 🔹 Workflow Details

### Trigger

* **push**: Any push to the `main` branch.
* **pull_request**: Any new pull request.

### Jobs

#### `generate-inventory-docs`

* **Runs on**: `ubuntu-latest`
* **Steps**:

  1. **Checkout repository**
     Uses `actions/checkout@v4` with `fetch-depth: 0` to ensure the repository history is fully available for commits.
  2. **Set up Python**
     Installs Python 3.11 using `actions/setup-python@v5`.
  3. **Install dependencies**
     Upgrades `pip` and installs Python dependencies from `requirements.txt`.
  4. **Generate inventory docs**
     Runs the Python script `scripts/generate_inventory_docs.py` to produce markdown documentation for all inventories.
  5. **Commit and push changes**
     Configures git user, stages updated markdown files, commits only if there are changes, and pushes back to the branch.

---

## 📝 Summary

* **Trigger:** Runs on every push to `main` and on pull requests.  
* **Checkout:** Uses `actions/checkout@v4` with `fetch-depth: 0` so commits can be pushed back.  
* **Python Setup:** Uses Python 3.11 (adjustable).  
* **Dependencies:** Installs from `requirements.txt` (currently only PyYAML).  
* **Script Execution:** Runs `scripts/generate_playbook_docs.py` to regenerate playbook documentation.
* **Generated Documentation:** The following markdown files are created by the Python script:
  * `playbooks/README.md`
  * `docs/playbooks/README.md`
  * `docs/playbooks/<playbook name>.md`
* **Commit Logic:**  
  * Stages only playbook markdowns and the central index.  
  * Commits only if changes exist (`git diff --cached --quiet` prevents empty commits).  
  * Pushes back to the branch that triggered the workflow.  
* **Permissions:** Requires repository **Actions → Workflow permissions** set to **Read and write** so the built‑in `GITHUB_TOKEN` can push commits.