#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_internal_link(href):
    if not href:
        return False
    parsed = urlparse(href)
    return parsed.scheme == "" and parsed.netloc == ""

def normalize_link(base, href):
    # Remove anchors and query params
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None

    # Resolve relative paths
    resolved = urljoin(base, href)

    # Convert absolute file paths to relative
    parsed = urlparse(resolved)
    return parsed.path.lstrip("/")

def extract_links(html_path, root):
    """Extract internal links from a single HTML file."""
    full_path = root / html_path
    if not full_path.exists():
        return []

    soup = BeautifulSoup(full_path.read_text(encoding="utf-8"), "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not is_internal_link(href):
            continue

        normalized = normalize_link("/" + html_path, href)
        if normalized and normalized.endswith(".html"):
            links.append(normalized)

    return sorted(set(links))


def build_link_tree(root, start="index.html"):
    """Build a link-based navigation tree starting from index.html."""
    visited = set()

    def walk(page):
        if page in visited:
            return {}  # avoid cycles
        visited.add(page)

        children = extract_links(page, root)
        subtree = {}

        for child in children:
            subtree[child] = walk(child)

        return subtree

    return {start: walk(start)}


def render_tree(tree, level=0):
    """Render the link tree using <details>/<summary>.
       Top-level is expanded; children collapsed by default.
    """
    html = ["<ul>"]

    for page, children in tree.items():
        # Top-level nodes are open by default
        open_attr = " open" if level == 0 else ""

        if children:
            html.append(f"<li><details{open_attr}>")
            html.append(f"<summary><a href='/{escape(page)}'>{escape(page)}</a></summary>")
            html.append(render_tree(children, level + 1))
            html.append("</details></li>")
        else:
            # Leaf node
            html.append(f"<li><a href='/{escape(page)}'>{escape(page)}</a></li>")

    html.append("</ul>")
    return "\n".join(html)


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

    tree = build_link_tree(root)
    html_body = render_tree(tree)

    output_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Site Map</title>
    <style>
        body {{ font-family: sans-serif; padding: 2rem; }}
        ul {{ list-style-type: none; }}
        li {{ margin: 4px 0; }}
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
