import os
import json
from bs4 import BeautifulSoup

CONTENT_DIR = "./_site"  # root directory
OUTPUT_FILE = "search-index.json"

EXCLUDE_DIRS = {
    ".git",
    ".github",
    "assets",
    "images",
    "scripts",
    "node_modules"
}

def extract_text_from_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else os.path.basename(path)
    text = soup.get_text(separator=" ", strip=True)

    return title, text

def main():
    index = []

    for root, dirs, files in os.walk(CONTENT_DIR):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith(".html"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, CONTENT_DIR)

                # Skip HTML files inside excluded directories
                if any(part in EXCLUDE_DIRS for part in rel_path.split(os.sep)):
                    continue

                title, text = extract_text_from_html(full_path)

                index.append({
                    "id": rel_path,
                    "title": title,
                    "content": text,
                    "url": "/" + rel_path.replace("\\", "/")
                })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

if __name__ == "__main__":
    main()
