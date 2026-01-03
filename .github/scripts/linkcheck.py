import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
from collections import deque
import html

BASE_URL = "https://homelab.refol.us"

visited = set()
report = {}
broken_links = []

# Track all internal links found
linked_pages = set()
# Cache fetch results to avoid fetching twice
fetch_cache = {}

def is_http_scheme(url):
    scheme = urlparse(url).scheme
    return scheme in ("http", "https")

def is_internal(url):
    return urlparse(url).netloc in ("", urlparse(BASE_URL).netloc)

def fetch(url):
    if url in fetch_cache:
        return fetch_cache[url]
    try:
        r = requests.get(url, timeout=10)
        fetch_cache[url] = (r.status_code, r.text)
        return fetch_cache[url]
    except Exception as e:
        fetch_cache[url] = (None, str(e))
        return fetch_cache[url]

def crawl(start):
    queue = deque([start])

    while queue:
        page = queue.popleft()
        if page in visited:
            continue

        visited.add(page)
        status, content = fetch(page)

        page_entry = {
            "status": status,
            "links": []
        }

        if status != 200 or not content:
            report[page] = page_entry
            continue

        soup = BeautifulSoup(content, "html.parser")
        anchors = soup.find_all("a", href=True)

        for a in anchors:
            raw = a["href"]
            full = urljoin(page, raw)

            # Determine link status safely
            if is_internal(full) and is_http_scheme(full):
                # Only fetch internal HTTP/HTTPS links
                link_status, _ = fetch(full)
                # Only count broken if status is not 200/301/302
                if link_status not in (200, 301, 302):
                    broken_links.append((page, full, link_status))
            elif not is_http_scheme(full):
                # Special schemes like mailto:, tel:, javascript:
                link_status = urlparse(full).scheme
            else:
                # External HTTP/HTTPS links (not counted as broken)
                link_status = "external"

            # Add link info to the page report
            page_entry["links"].append({
                "raw": raw,
                "resolved": full,
                "status": link_status
            })

            # Track linked internal pages and queue unvisited ones
            if is_internal(full) and is_http_scheme(full):
                linked_pages.add(full)
                if full not in visited:
                    queue.append(full)

        report[page] = page_entry

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl a site and report broken/internal links")
    parser.add_argument("base_url", nargs="?", default=BASE_URL,
                        help=f"Base URL to start crawling (default: {BASE_URL})")
    args = parser.parse_args()

    crawl(args.base_url)

# -----------------------------
# Detect orphaned pages
# -----------------------------
orphaned_pages = visited - linked_pages

# -----------------------------
# Generate Markdown summary
# -----------------------------
with open("link-summary.md", "w") as f:
    f.write(f"### Pages scanned: {len(report)}\n")
    f.write(f"### Broken links: {len(broken_links)}\n")
    f.write(f"### Orphaned pages: {len(orphaned_pages)}\n\n")

    if broken_links:
        f.write("#### Broken Links\n")
        for page, link, status in broken_links:
            f.write(f"- **{page}** → {link} (status: {status})\n")
    else:
        f.write("No broken links found.\n")

    if orphaned_pages:
        f.write("\n#### Orphaned Pages\n")
        for page in orphaned_pages:
            f.write(f"- {page}\n")
    else:
        f.write("No orphaned pages found.\n")

# -----------------------------
# Generate HTML report
# -----------------------------
html_output = """
<html>
<head>
<title>Link Report</title>
<style>
body { font-family: sans-serif; padding: 20px; }
table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
th, td { border: 1px solid #ccc; padding: 8px; }
th { background: #f0f0f0; }
.bad { color: red; font-weight: bold; }
.good { color: green; }
</style>
</head>
<body>
<h1>Full Link Report</h1>
"""

for page, data in report.items():
    html_output += f"<h2>{page}</h2>"
    html_output += f"<p>Status: {data['status']}</p>"
    html_output += "<table><tr><th>Raw</th><th>Resolved</th><th>Status</th></tr>"

    for link in data["links"]:
        status = link["status"]
        cls = "good" if status in (200, 301, 302) else "bad"
        html_output += (
            f"<tr>"
            f"<td>{html.escape(link['raw'])}</td>"
            f"<td>{html.escape(link['resolved'])}</td>"
            f"<td class='{cls}'>{status}</td>"
            f"</tr>"
        )

    html_output += "</table>"

if orphaned_pages:
    html_output += "<h2>Orphaned Pages</h2><ul>"
    for page in orphaned_pages:
        html_output += f"<li>{page}</li>"
    html_output += "</ul>"

html_output += "</body></html>"

with open("link-report.html", "w") as f:
    f.write(html_output)

exit(0)
