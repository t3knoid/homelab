---
title: "Generate Ansible Inventory Docs GitHub Action"
---

# Generate Ansible Inventory Docs GitHub Action

This GitHub Action automatically generates documentation for the Ansible inventories whenever changes are pushed to the `main` branch or a pull request is created. It uses a Python script to generate markdown files for each inventory and commits the changes back to the repository.

---

## 📄 Workflow File

{% raw %}
```yaml
name: Generate Ansible Inventory Docs

on:
  push:
    branches:
      - main
  pull_request:

jobs:
  generate-inventory-docs:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Generate inventory docs
        run: |
          python ./scripts/generate_inventory_docs.py

      - name: Commit and push changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git pull
          git add inventory/README.md docs/inventories/README.md docs/inventories/*.md
          if ! git diff --cached --quiet; then
            git commit -m "chore(docs): auto-generate inventory documentation"
            git push origin HEAD:${{ github.ref }}
          else
            echo "No documentation changes to commit."
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

## ⚡ Notes

* The workflow only commits changes if there are actual documentation updates.
* `fetch-depth: 0` is necessary to ensure git history is available for committing.
* Python dependencies must be declared in `requirements.txt`.
* Generated documentation is saved in:

  * `inventory/README.md`
  * `docs/inventories/README.md`
  * `docs/inventories/*.md`

