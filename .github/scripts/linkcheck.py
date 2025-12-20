import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import html

BASE_URL = "https://homelab.refol.us"

visited = set()
report = {}
broken_links = []

def is_internal(url):
    return urlparse(url).netloc in ("", urlparse(BASE_URL).netloc)

def fetch(url):
    try:
        r = requests.get(url, timeout=10)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

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
            link_status, _ = fetch(full)

            page_entry["links"].append({
                "raw": raw,
                "resolved": full,
                "status": link_status
            })

            if link_status not in (200, 301, 302):
                broken_links.append((page, full, link_status))

            if is_internal(full) and full not in visited:
                queue.append(full)

        report[page] = page_entry

crawl(BASE_URL)

# -----------------------------
# Generate Markdown summary
#