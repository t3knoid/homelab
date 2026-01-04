#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import unicodedata
import html
import re


# ------------------------------------------------------------
# Normalization helpers
# ------------------------------------------------------------

def normalize_ascii(text):
    """Normalize Unicode to ASCII, collapse whitespace, decode HTML entities."""
    text = html.unescape(text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return " ".join(text.split())

def normalize_filename(name):
    if not name:
        return None

    # Decode percent-encoding (%E2%80%91 → U+2011)
    name = unquote(name)

    # Replace all Unicode hyphens/dashes with ASCII hyphen
    name = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015]", "-", name)

    # Normalize Unicode to ASCII
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    return name

# ------------------------------------------------------------
# Link extraction
# ------------------------------------------------------------

def is_internal_link(href):
    if not href:
        return False
    parsed = urlparse(href)
    return parsed.scheme == "" and parsed.netloc == ""


def normalize_link(base, href):
    """Resolve relative links and strip anchors/query params."""
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None
    resolved = urljoin(base, href)
    parsed = urlparse(resolved)
    return parsed.path.lstrip("/")


def extract_links(html_path, root):
    """Extract internal .html links from the <main> content only."""
    full_path = root / html_path
    if not full_path.exists():
        return []

    soup = BeautifulSoup(full_path.read_text(encoding="utf-8"), "html.parser")

    # Only parse inside <main>
    main = soup.find("main")
    if not main:
        return []  # no main content, skip

    links = []

    for a in main.find_all("a", href=True):
        href = a["href"]
        if not is_internal_link(href):
            continue

        normalized = normalize_link("/" + html_path, href)
        normalized = normalize_filename(normalized)
        if normalized and normalized.endswith(".html"):
            links.append(normalized)

    return sorted(set(links))

# ------------------------------------------------------------
# H1 extraction
# ------------------------------------------------------------

def extract_h1_label(html_path, root):
    """Extract <h1> text and normalize it."""
    full_path = root / html_path
    if not full_path.exists():
        return None

    soup = BeautifulSoup(full_path.read_text(encoding="utf-8"), "html.parser")
    h1 = soup.find("h1")
    if not h1:
        return None

    text = h1.get_text(strip=True)
    return normalize_ascii(text)


def build_label_map(root):
    """Build a map of normalized_filename → H1 label."""
    label_map = {}

    for path in root.rglob("*.html"):
        real_rel = str(path.relative_to(root))          # actual filename on disk
        norm_rel = normalize_filename(real_rel)         # normalized key

        label = extract_h1_label(real_rel, root)        # MUST use real filename
        if label:
            label_map[norm_rel] = label                 # store under normalized key

    return label_map

# ------------------------------------------------------------
# Link-relationship tree builder
# ------------------------------------------------------------

def build_link_tree(root, start="index.html"):
    visited = set()

    def walk(page):
        if page in visited:
            return {}
        visited.add(page)

        children = extract_links(page, root)
        subtree = {}

        for child in children:
            subtree[child] = walk(child)

        return subtree

    return {start: walk(start)}


# ------------------------------------------------------------
# Renderer (collapsible, top-level open)
# ------------------------------------------------------------

def render_tree(tree, label_map, level=0):
    html_parts = ["<ul>"]

    for page, children in tree.items():
        safe_page = normalize_filename(page)
        label = label_map.get(safe_page, safe_page)
        open_attr = " open" if level == 0 else ""

        if children:
            html_parts.append(f"<li><details{open_attr}>")
            html_parts.append(
                f"<summary><a href='/{escape(page)}'>{escape(label)}</a></summary>"
            )
            html_parts.append(render_tree(children, label_map, level + 1))
            html_parts.append("</details></li>")
        else:
            html_parts.append(
                f"<li><a href='/{escape(page)}'>{escape(label)}</a></li>"
            )

    html_parts.append("</ul>")
    return "\n".join(html_parts)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a link-relationship HTML sitemap starting from index.html."
    )
    parser.add_argument(
        "--root",
        default="_site",
        help="Root folder of the built site (default: _site)"
    )
    parser.add_argument(
        "--output",
        default="_includes/sitemap-content.html",
        help="Output HTML file (default: _includes/sitemap-content.html)"
    )

    args = parser.parse_args()
    root = Path(args.root)

    if not root.exists():
        raise SystemExit(f"Error: root folder '{root}' does not exist")

    # Build link graph
    tree = build_link_tree(root)

    # Extract H1 labels
    label_map = build_label_map(root)

    # Render final HTML
    html_body = render_tree(tree, label_map)

    output_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Site Map</title>
    <style>
        body {{ font-family: sans-serif; padding: 2rem; }}
        ul {{ list-style-type: none; padding-left: 1rem; }}
        li {{ margin: 4px 0; }}
        summary a {{ text-decoration: none; }}
        summary a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
<h1>Site Map</h1>
{html_body}
</body>
</html>
"""

    Path(args.output).write_text(output_html, encoding="utf-8")
    print(f"Link-based sitemap written to {args.output}")


if __name__ == "__main__":
    main()
