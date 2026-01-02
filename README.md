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

---

# 🔍 Full‑Text Search (Lunr.js)

This site includes a **client‑side full‑text search** powered by **Lunr.js**.  
The search system is fully static and requires **no backend**, making it ideal for GitHub Pages.

## How Search Works

### 1. **Index Generation (GitHub Actions)**
During the build workflow:

- After Jekyll finishes rendering the site into `_site/`
- A Python script (`.github/scripts/generate_lunr_index.py`) scans the **source Markdown‑generated HTML**
- It extracts:
  - Page title  
  - URL  
  - Main content text (from `<main>`)

The script outputs a JSON index:

```
search-index.json
```

This file is then copied into the final site output:

```
cp search-index.json _site/
```

GitHub Pages publishes it at:

```
/search-index.json
```

### 2. **Search Page (`search.html`)**
The search UI lives at:

```
/search.html
```

This page:

- Uses the site’s default layout (`layout: default`)
- Loads the global header (including the search bar)
- Loads Lunr.js and `search.js`
- Reads the query string (`?q=...`)
- Fetches `/search-index.json`
- Performs a Lunr search in the browser
- Renders results dynamically into:

```html
<div id="search-results"></div>
```

### 3. **Search Bar (in the header)**
The search bar is defined in:

```
_includes/custom-header.html
```

It submits queries to `/search.html`:

```html
<form action="/search.html" method="GET">
  <input type="text" name="q" placeholder="Search…">
</form>
```

This ensures the search bar appears consistently on every page.

---

# ⚙️ GitHub Actions Workflow

The GitHub Actions workflow that builds and deploys the site is at  
[.github/workflows/static.yml](.github/workflows/static.yml).

### Workflow Triggers
- 🔁 **Run on**:
  - Pushes to the `main` branch
  - Manual dispatch (`workflow_dispatch`)

---

## 🧱 Workflow Steps

### 1. ✅ Checkout Repository
Pulls the repository contents.

### 2. 💎 Setup Ruby & Dependencies
- Installs Ruby
- Installs Jekyll and Bundler dependencies

### 3. 🛠️ Build Site
Builds the Jekyll site into `./_site`:

```bash
bundle exec jekyll build
```

### 4. 🔍 Generate Lunr Search Index
- Python script parses generated HTML
- Produces `search-index.json`
- Copies it into `_site/` so GitHub Pages publishes it

### 5. 📤 Deploy to GitHub Pages
Deploys the `_site` directory using `actions/deploy-pages`.

### 6. 🔗 Crawl Deployed Site
After deployment, a Python crawler:

- Scans all internal links
- Detects broken links
- Detects orphaned pages
- Marks external links as `"external"`
- Marks special schemes (`mailto:`, `tel:`, `javascript:`)

### 7. 📤 Upload Reports
Uploads:

- `link-summary.md`
- `link-report.html`

as workflow artifacts.

---

# 📝 Notes

- Only **internal HTTP/HTTPS links** count as broken.
- External links and special schemes appear in reports but do not affect the broken link count.
- Crawling happens **after deployment** for accuracy.
- The canonical source of truth for content is the **Ansible playbook**, not this repository.

---

# 🎨 Minima Configuration

- **Theme:** `minima` (set in `_config.yml`)
- **Defaults:** `layout: default` applied to generated pages
- **Layout:** `_layouts/default.html` includes the custom header
- **Header:** `_includes/custom-header.html` contains:
  - Navigation
  - Responsive hamburger menu
  - Global search bar

---

# 🧪 Testing Locally

To build and preview the site locally:

```bash
ruby -v
gem install bundler
bundle install --jobs 4 --retry 3
bundle exec jekyll serve --host 0.0.0.0 --port 4000
```

To install Ruby using Ansible:

```bash
ansible-playbook -i inventory/ansible/inventory.ini -k playbooks/ruby/deploy_ruby.yml -l ansible-0
```
