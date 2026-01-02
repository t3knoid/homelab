# 🏠 homelab — Wiki Mirror

⚠️ Important: other than this `README.md`, the Markdown files in this repository must NOT be edited by hand.

## Summary

  ⚙️ These Markdown files are automatically generated from an Ansible playbook. Any manual edits to the generated Markdown will be overwritten the next time the playbook runs.
  
  ⤴️ To (re)generate the Markdown files locally, run from a local [Ansible](https://github.com/t3knoid/ansible) source folder:

```bash
ansible-playbook -i inventory/redmine/inventory.ini -k playbooks/redmine/mirror_wiki.yml
```

---

📡 **This repository serves as a one‑way mirror of my internal Redmine wiki.** All page content is automatically exported and transformed by the **[redmine wiki mirror Ansible module](https://github.com/t3knoid/refol.general/blob/main/docs/redmine_wiki_mirror.md)**, which handles the full conversion pipeline from Redmine wiki syntax to the Markdown files stored here. Manual edits to mirrored content are intentionally overwritten on each sync to ensure the public mirror always reflects the authoritative internal source.

---

🚀 Finally, GitHub Actions builds the Markdown into static HTML and publishes the site automatically through GitHub Pages.


	 https://lab.refol.us/projects/home-lab/wiki ➡️ https://homelab.refol.us/

---

## 🧱 Tech Stack Overview (Static Site Generation)

This site is built using a **fully automated static‑site toolchain** that combines Jekyll, GitHub Actions, Lunr.js, and a post‑deploy validation pipeline. The result is a reproducible, dependency‑pinned workflow that produces a fast, privacy‑preserving static HTML site with built‑in search and continuous link integrity checks.

### 🔧 Core Components

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Static Site Generator** | **Jekyll** | Converts Markdown → HTML, processes Liquid templates, applies layouts, and builds the final `_site/` directory. |
| **Theme** | **Minima** | Provides base styling, typography, and layout structure. |
| **Templating** | **Liquid** | Powers includes, layouts, and dynamic path resolution (`relative_url`). |
| **Search Engine** | **Lunr.js** | Client‑side full‑text search with no backend dependencies. |
| **Index Builder** | **Python + BeautifulSoup4** | Extracts content from generated HTML and produces `search-index.json`. |
| **Deployment** | **GitHub Pages** | Hosts the final static site from the `_site/` artifact. |
| **Automation** | **GitHub Actions** | Orchestrates the entire build → index → deploy → link‑check pipeline. |
| **Post‑Deploy Validation** | **Python crawler** | Scans the live site for broken links, orphaned pages, and link integrity issues. |

---

### 🛠️ Build Pipeline Summary

The static HTML is produced and validated through the following automated stages:

1. **Jekyll Build**
   - Ruby + Bundler install dependencies  
   - Jekyll renders Markdown and Liquid templates  
   - Output written to `_site/`

2. **Search Index Generation**
   - Python script parses generated HTML  
   - Extracts `<main>` content, titles, and URLs  
   - Produces `search-index.json`  
   - Copied into `_site/` for publishing

3. **Deployment**
   - `_site/` uploaded as a GitHub Pages artifact  
   - GitHub Pages serves the static HTML

4. **Post‑Deploy Link Checking**
   - Python crawler scans the **live deployed site**  
   - Follows internal HTTP/HTTPS links  
   - Detects:
     - Broken internal links  
     - Orphaned pages  
     - External links (marked `"external"`)  
     - Special schemes (`mailto:`, `tel:`, `javascript:`)  
   - Generates:
     - `link-summary.md` (human‑readable summary)  
     - `link-report.html` (full report)  
   - Uploads both as workflow artifacts  
   - Adds a summary block to the GitHub Actions UI

---

### 📦 Languages & Tools Used

- **Ruby 3.3.x** — Jekyll + Bundler  
- **Python 3.x** — Lunr index generation + link checker  
- **HTML/CSS/JS** — Final static site  
- **Liquid** — Template includes, layouts, and path helpers  
- **GitHub Actions** — CI/CD automation  
- **GitHub Pages** — Hosting  

---

### 🎯 Why This Stack Works Well

- **Zero backend** — everything is static and CDN‑served  
- **Deterministic builds** — Jekyll + pinned Ruby gems  
- **Search without servers** — Lunr.js runs entirely in the browser  
- **Continuous validation** — link checker ensures site integrity after every deploy  
- **Contributor‑friendly** — Markdown is generated automatically, HTML is built automatically  
- **Privacy‑preserving** — no analytics, no external search services  
- **Fast** — GitHub Pages + static assets = instant load times  

---

## 🔍 Full‑Text Search (Lunr.js)

This site includes a **client‑side full‑text search** powered by **Lunr.js**.  
The search system is fully static and requires **no backend**, making it ideal for GitHub Pages.

### How Search Works

#### 1. **Index Generation (GitHub Actions)**
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

#### 2. **Search Page (`search.html`)**
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

#### 3. **Search Bar (in the header)**
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

## ⚙️ GitHub Actions Workflow

The GitHub Actions workflow that builds and deploys the site is at  
[.github/workflows/static.yml](.github/workflows/static.yml).

### Workflow Triggers
- 🔁 **Run on**:
  - Pushes to the `main` branch
  - Manual dispatch (`workflow_dispatch`)

---

### 🧱 Workflow Steps

#### 1. ✅ Checkout Repository
Pulls the repository contents.

#### 2. 💎 Setup Ruby & Dependencies
- Installs Ruby
- Installs Jekyll and Bundler dependencies

#### 3. 🛠️ Build Site
Builds the Jekyll site into `./_site`:

```bash
bundle exec jekyll build
```

#### 4. 🔍 Generate Lunr Search Index
- Python script parses generated HTML
- Produces `search-index.json` into `_site/` directory

#### 5. 📤 Deploy to GitHub Pages
Deploys the `_site` directory using `actions/deploy-pages`.

#### 6. 🔗 Crawl Deployed Site
After deployment, a [Python crawler](.github/scripts/linkcheck.py):

- Scans all internal links
- Detects broken links
- Detects orphaned pages
- Marks external links as `"external"`
- Marks special schemes (`mailto:`, `tel:`, `javascript:`)

#### 7. 📤 Upload Reports
Uploads:

- `link-summary.md`
- `link-report.html`

as workflow artifacts.

---

## 🔍 Post‑Deploy Link Checking

After the static site is deployed to GitHub Pages, a dedicated **post‑deploy validation stage** to ensure the published site is structurally sound and free of broken internal links.

---

### 🔎 What the Link Checker Does

Once GitHub Pages finishes deploying the `_site` artifact, the workflow:

1. Crawls the **live** site (not the build output)
2. Follows internal HTTP/HTTPS links
3. Marks:
   - **Broken internal links** (non‑200/301/302)
   - **External links** as `"external"`
   - **Special schemes** (`mailto:`, `tel:`, `javascript:`)
4. Detects **orphaned pages** not linked from anywhere
5. Generates:
   - A human‑readable Markdown summary (`link-summary.md`)
   - A full HTML report (`link-report.html`)
6. Uploads both as workflow artifacts
7. Adds a summary block to the GitHub Actions UI

This ensures the deployed site is always internally consistent and that regressions are caught immediately.

---

### 🔗 Viewing Post‑Deploy Link Check Results

To inspect the link checker output after a deployment:

1. Open the repository on GitHub.
2. Go to **Actions** → select the latest **static site** workflow run.
3. In the left sidebar, click the **linkcheck** job.
4. At the top of the job, read the **Link Checker Results** summary.
5. Scroll to the bottom of the job to download the artifacts:
   - `link-summary.md` (quick overview)
   - `link-report.html` (full detailed report)

These results reflect the **live deployed site**, not the build output, ensuring accurate link validation.

## 🎨 Minima Configuration

- **Theme:** `minima` (set in `_config.yml`)
- **Defaults:** `layout: default` applied to generated pages
- **Layout:** `_layouts/default.html` includes the custom header
- **Header:** `_includes/custom-header.html` contains:
  - Navigation
  - Responsive hamburger menu
  - Global search bar

---

## 🧪 Testing Locally

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

## 📝 Notes

- Only **internal HTTP/HTTPS links** count as broken.
- External links and special schemes appear in reports but do not affect the broken link count.
- Crawling happens **after deployment** for accuracy.
- The canonical source of truth for content is the **Ansible playbook**, not this repository.