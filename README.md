# 🏠 homelab — Markdown Mirror

⚠️ Important: other than this `README.md`, the Markdown files in this repository must NOT be edited by hand.

## Summary
- ⚙️ These Markdown files are automatically generated from an Ansible playbook. Any manual edits to the generated Markdown will be overwritten the next time the playbook runs.
- ⤴️ To (re)generate the Markdown files locally, run from a local [Ansible](https://github.com/t3knoid/ansible) source folder:

```bash
ansible-playbook -i inventory/redmine/inventory.ini -k playbooks/redmine/mirror_wiki.yml
```

- 🌐 This repository is a one-way mirror.

	https://lab.refol.us/projects/home-lab/wiki ➡️ https://homelab.refol.us/


## GitHub Actions Workflow

The GitHub Actions workflow that builds and deploys the site is at
[.github/workflows/static.yml](.github/workflows/static.yml). In short, the workflow:

### Workflow Triggers
- 🔁 **Run on**:
  - Pushes to the `main` branch
  - Manual dispatch (`workflow_dispatch`)

### Steps

1. ✅ **Checkout Repository**
   - Uses `actions/checkout` to pull repository code.

2. 💎 **Setup Ruby & Dependencies**
   - Installs Ruby.
   - Installs Jekyll and Bundler-managed dependencies (`bundle install`).

3. 🛠️ **Build Site**
   - Builds the Jekyll site into `./_site` using:
     ```bash
     bundle exec jekyll build
     ```

4. 📤 **Deploy to GitHub Pages**
   - Deploys `_site` contents to GitHub Pages.
   - Optionally uploads `_site` as a workflow artifact.

5. 🔗 **Crawl Deployed Site**
   - Runs the Python crawler **after deployment**.
   - Crawls **internal HTTP/HTTPS links**.
   - Marks **external links** as `"external"`.
   - Marks **special scheme links** (`mailto:`, `tel:`, `javascript:`) with their scheme.
   - Detects **broken internal links** (status ≠ 200/301/302).
   - Detects **orphaned pages** not linked from any page.
   - Prints a summary in the Actions log:
     - Pages scanned
     - Broken links
     - Orphaned pages

6. 📤 **Upload Reports**
   - Uploads `link-summary.md` and `link-report.html` as workflow artifacts.

### Notes
- Only **internal HTTP/HTTPS links** are counted as broken.
- External and special links appear in the reports but **do not affect the broken link count**.
- Crawling is performed **after the site is live** on GitHub Pages for accurate link checks.

Because the site is rendered from the repository's Markdown, the canonical source of truth for the content is the Ansible playbook that generates the Markdown (see the command above).

## Minima Configuration

- 🎨 **Theme:** set to `minima` in [_config.yml](_config.yml).
- 📐 **Page layout defaults:** added a `defaults` entry in [_config.yml](_config.yml) to assign `layout: default` to generated pages so the theme wrapper (and header) is applied.
- 🧩 **Layout include:** added a minimal layout at [_layouts/default.html](_layouts/default.html) which includes a custom header include so pages render the site header consistently.
- 🍔 **Header/navigation:** created [_includes/custom-header.html](_includes/custom-header.html) with a responsive hamburger menu (CSS-only) and tightened mobile spacing.


## 🧪 Testing Locally

To build and preview the site locally (uses the Gemfile versions):

```bash
# ensure Ruby is available
ruby -v

# install Bundler if missing (system Ruby may require sudo)
gem install bundler

# install gems from Gemfile
bundle install --jobs 4 --retry 3

# serve and preview in the browser (binds to all interfaces)
bundle exec jekyll serve --host 0.0.0.0 --port 4000
```

Ruby can be installed using [Ansible](https://github.com/t3knoid/ansible) with the following command:

```bash
ansible-playbook -i inventory/ansible/inventory.ini -k playbooks/ruby/deploy_ruby.yml -l ansible-0
```
