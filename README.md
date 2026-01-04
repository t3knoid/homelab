# 🏠 homelab — Wiki Mirror

⚠️ **Important**
Other than this `README.md`, the Markdown files in this repository **must NOT be edited by hand**.

---

## 📡 What This Repository Is

This repository is a **one-way public mirror** of my internal **Redmine wiki**.

* Wiki content is authored and maintained **only** in Redmine
* Pages are automatically exported and converted to Markdown by the
  **[redmine wiki mirror Ansible module](https://github.com/t3knoid/refol.general/blob/main/docs/redmine_wiki_mirror.md)**
* Any manual edits to generated Markdown files are intentionally overwritten

The goal is to provide a **read-only, always-up-to-date public mirror** of an authoritative internal knowledge base.

```
https://lab.refol.us/projects/home-lab/wiki
        ⬇
https://homelab.refol.us/
```

---

## ⚙️ Source of Truth & Content Generation

### Authoritative Source

* **Redmine Wiki** (internal)
* Content is written once, in one place

### Markdown Generation

All Markdown files in this repository are generated automatically via Ansible.

To (re)generate the Markdown locally:

```bash
ansible-playbook -i inventory/redmine/inventory.ini -k playbooks/redmine/mirror_wiki.yml
```

> Any manual changes to generated Markdown will be overwritten on the next run.

---

## 🔁 End-to-End Publishing Workflow (At a Glance)

The site is produced through a **fully automated pipeline**, from wiki export to validated public deployment:

1. **Redmine wiki → Markdown** (Ansible)
2. **Markdown → HTML** (Jekyll)
3. **HTML → Search index** (Python + Lunr.js)
4. **Deploy static site** (GitHub Pages)
5. **Crawl live site** (post-deploy link checker)

Everything is reproducible, static, and dependency-pinned.

---

## 🧱 Static Site Toolchain Overview

This site uses a **zero-backend static architecture** with client-side search and continuous validation.

### Core Components

| Layer                 | Technology                  | Purpose                                     |
| --------------------- | --------------------------- | ------------------------------------------- |
| Static Site Generator | **Jekyll**                  | Markdown → HTML, layouts, Liquid processing |
| Theme                 | **Minima**                  | Base styling and layout                     |
| Templating            | **Liquid**                  | Includes, layouts, relative paths           |
| Search Engine         | **Lunr.js**                 | Client-side full-text search                |
| Search Index Builder  | **Python + BeautifulSoup4** | Extracts content from generated HTML        |
| Automation            | **GitHub Actions**          | Build, index, deploy, validate              |
| Hosting               | **GitHub Pages**            | Serves the final static site                |
| Validation            | **Python crawler**          | Post-deploy link integrity checks           |

---

## 🚀 Build, Index, Deploy, Validate

### 1️⃣ Jekyll Build

* Ruby + Bundler install dependencies
* Jekyll renders Markdown + Liquid templates
* Output written to `_site/`

```bash
bundle install
bundle exec jekyll build
```

---

### 2️⃣ Search Index Generation (Lunr.js)

After Jekyll finishes rendering:

* A Python script scans the generated HTML
* Extracts:

  * Page title
  * URL
  * `<main>` content text
* Produces:

```
search-index.json
```

The index is copied into the site output:

```
_site/search-index.json
```

This file is published directly by GitHub Pages and fetched by the browser at runtime.

---

### 🔗 Site Map Generation (HTML)

An automated step generates a human-friendly, link-based HTML site map that is included at `/site-map.html` and is useful for discovery and navigation.

Key points:

- The generator script is `.github/scripts/generate_site_map.py`.
- By default the script writes an include file: `_includes/sitemap-content.html` which is then pulled into the published page `site-map.html`.
- Because the script writes an include, the site is rebuilt so the updated include is rendered into the final HTML (the CI workflow runs a small rebuild step after sitemap generation).

Quick local usage:

```bash
# generate the sitemap include (default output: _includes/sitemap-content.html)
python3 .github/scripts/generate_site_map.py

# rebuild so the generated include is rendered into site-map.html
bundle exec jekyll build
```

The generated page is linked from the site footer and is published as `/site-map.html` on GitHub Pages.

---

### 3️⃣ Deployment (GitHub Pages)

* The `_site/` directory is uploaded as a Pages artifact
* GitHub Pages serves the static HTML, CSS, JS, and search index

---

### 4️⃣ Post-Deploy Link Checking (Live Site)

After deployment completes, a **dedicated validation stage** runs against the **live site**, not the build output.

The Python crawler:

* Crawls all internal HTTP/HTTPS links
* Detects:

  * Broken internal links
  * Orphaned pages
* Marks (but does not fail on):

  * External links
  * `mailto:`, `tel:`, `javascript:` schemes

It generates:

* `link-summary.md` — human-readable overview
* `link-report.html` — full detailed report

Both are uploaded as workflow artifacts, and a summary appears directly in the GitHub Actions UI.

---

## 🔍 Full-Text Search (Client-Side, No Backend)

Search is powered entirely by **Lunr.js**, running in the browser.

### How It Works

#### Search Page

* `/search.html`
* Uses the default site layout
* Loads Lunr.js and `search.js`
* Reads the query string (`?q=...`)
* Fetches `/search-index.json`
* Renders results dynamically into:

```html
<div id="search-results"></div>
```

#### Global Search Bar

Defined in:

```
_includes/custom-header.html
```

```html
<form action="/search.html" method="GET">
  <input type="text" name="q" placeholder="Search…">
</form>
```

This ensures search is available on every page.

---

## ⚙️ GitHub Actions Workflow

Workflow definition:

```
.github/workflows/static.yml
```

### Triggers

* Pushes to `main`
* Manual runs (`workflow_dispatch`)

### Job Stages

1. Checkout repository
2. Setup Ruby & dependencies
3. Build Jekyll site
4. Generate Lunr search index
5. Deploy to GitHub Pages
6. Crawl live site for link integrity
7. Upload validation reports

---

## 🎨 Theme & Layout

* **Theme:** `minima`
* **Default layout:** `_layouts/default.html`
* **Header:** `_includes/custom-header.html`

  * Navigation
  * Responsive menu
  * Global search bar

---

## 🧪 Testing Locally

To preview the site locally, install **Ruby 3.1+** and **Python 3.8+**. These versions match the GitHub Actions environment and ensure compatibility with Jekyll, Requests, and BeautifulSoup4.

### 🔧 Install Dependencies

```bash
# Ruby dependencies
gem install bundler
bundle install --jobs 4 --retry 3

# Python dependencies
python3 -m pip install requests beautifulsoup4
```

### 🛠️ Build & Serve the Site

```bash
# build the Jekyll site
bundle exec jekyll build --destination ./_site

# generate the Lunr search index
python3 .github/scripts/generate_lunr_index.py

# serve the site locally
bundle exec jekyll serve --skip-initial-build --host 0.0.0.0 --port 4000
```

The site will be available at:

```
http://localhost:4000
```

### 🔗 Test the Link Crawler

In a second terminal:

```bash
python3 .github/scripts/linkcheck.py http://localhost:4000
```

This runs the same link‑integrity scan used in the post‑deploy GitHub Actions workflow.

---

## 📝 Notes

- Only **internal HTTP/HTTPS links** count as broken.  
- External links and special schemes appear in reports but do not affect the broken link count.  
- Crawling happens **after deployment** for accuracy.  
- The canonical source of truth for content is the **Ansible playbook**, not this repository.  
- The search index (`search-index.json`) is generated automatically during the workflow and should **not** be committed to the repository.  
- The search page (`search.html`) is the only manually maintained HTML file; all other content is generated from Markdown.  
- Local builds may differ slightly from GitHub Pages due to environment differences; the post‑deploy crawler always reflects the **true deployed state**.  
- The link checker only analyzes **published** pages — drafts or excluded files are not scanned.  
- Any manual edits to generated Markdown will be overwritten on the next sync from Redmine.
