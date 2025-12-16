# 🔧 Fix GitHub Actions Workflow Permission Errors

If one of your GitHub Actions workflows keeps failing with a permission error — such as not being able to push code, commit changes, or create pull requests — this guide shows exactly how to fix it. These errors happen when GitHub hasn’t given the workflow the right access. We’ll walk through how to give it what it needs safely and easily.

**Related GitHub official documentation:**
👉 [https://docs.github.com/en/actions/tutorials/authenticate-with-github_token](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token) — This tutorial explains how `GITHUB_TOKEN` works and how to change its permissions in workflows. ([GitHub Docs][1])

---

## 🔹 What This Fixes

This guide resolves common workflow issues such as:

* Workflows **failing due to lack of permission to read or write repository content**
* Workflows that need to **create or approve pull requests**
* Workflows that use the built‑in **`GITHUB_TOKEN`** and get authentication or access denied errors

In GitHub Actions, each workflow gets an automatically generated `GITHUB_TOKEN` which lets the workflow authenticate API calls and interact with the repository. But by default, that token may have limited permissions — especially on repositories with tighter security settings. ([GitHub Docs][2])

---

## ➤ Solution 1: Update Repository Settings (Recommended for Most Cases)

This method gives all workflows in your repository read and write permissions by default so they won’t fail due to permission issues.

1. Go to your repository on GitHub.
2. Click the **Settings** tab.
3. In the left sidebar, choose **Actions**, then click **General**.
4. Scroll down to the **Workflow permissions** section.
5. Select **Read and write permissions**.
6. If your workflow needs to **create and approve pull requests**, check that box too.
7. Click **Save**.
8. Re‑run your failed workflow — it should now succeed.

📌 **This works because GitHub allows configuring the default `GITHUB_TOKEN` permissions at the repository level.** Without this, the token might only have read access to contents and packages, which isn’t enough for write operations. ([GitHub Docs][2])

---

## ➤ Solution 2: Specify Permissions in the Workflow File (Fine‑Grained Control)

This method is more secure because you only give the workflow only the permissions it actually needs.

1. Open your workflow YAML file (e.g., `.github/workflows/your‑workflow.yml`).
2. Add a `permissions` block at the top to grant the minimum required access:

```yaml
# Gives permission to read and write repo contents
permissions:
  contents: write

jobs:
  your_job_name:
    runs-on: ubuntu-latest
    steps:
      # ... your steps here ...
```

3. If a step needs the token explicitly (such as `actions/checkout`), include it:

```yaml
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
```

🔐 **Tip:** You can list many permissions (e.g., `issues: write`, `pull‑requests: write`) depending on what actions your workflow performs. This works because GitHub lets you define exactly what scopes `GITHUB_TOKEN` has for a workflow or job. ([GitHub Docs][2])

---

## ⚡ Quick Recap

| Method                        | How It Works                                        | Best Use Case           |
| ----------------------------- | --------------------------------------------------- | ----------------------- |
| **Repository Settings**       | Sets default permissions for all workflows          | Easy fix for most cases |
| **Workflow File Permissions** | Only grants needed permissions to specific workflow | Safer & more precise    |

---

## 🎉 After These Steps

Your workflows should now be able to:

* Read and write repository contents
* Push commits
* Create pull requests
* Use the GitHub API without permission errors

---

## 📘 Related Official Guide

Learn more from GitHub’s own tutorial on how `GITHUB_TOKEN` works and how to modify its permissions in workflows:
👉 [https://docs.github.com/en/actions/tutorials/authenticate-with-github_token](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token) ([GitHub Docs][1])


