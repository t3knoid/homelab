function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name) || "";
}

async function loadIndex() {
  const response = await fetch("/search-index.json");
  const docs = await response.json();

  const idx = lunr(function () {
    this.ref("id");
    this.field("title", { boost: 10 });
    this.field("content");

    docs.forEach(doc => this.add(doc));
  });

  return { idx, docs };
}

async function runSearch() {
  const query = getQueryParam("q");
  if (!query) return;

  const { idx, docs } = await loadIndex();
  const resultsContainer = document.getElementById("search-results");

  const matches = idx.search(query);

  if (matches.length === 0) {
    resultsContainer.innerHTML = `<p>No results found for <strong>${query}</strong>.</p>`;
    return;
  }

  matches.forEach(match => {
    const doc = docs.find(d => d.id === match.ref);

    const item = document.createElement("div");
    item.className = "search-result";
    item.innerHTML = `
      <a href="${doc.url}">${doc.title}</a>
      <p>${doc.content.substring(0, 180)}...</p>
    `;
    resultsContainer.appendChild(item);
  });
}

document.addEventListener("DOMContentLoaded", runSearch);
