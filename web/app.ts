const resultsList = document.getElementById("results") as HTMLUListElement;
const form = document.getElementById("searchForm") as HTMLFormElement;
const queryInput = document.getElementById("queryInput") as HTMLInputElement;
const seedButton = document.getElementById("seedButton") as HTMLButtonElement;

type SearchResult = { title: string; score: number };

function renderResults(results: SearchResult[]): void {
  resultsList.innerHTML = "";
  if (!results.length) {
    resultsList.innerHTML = "<li>No matches yet.</li>";
    return;
  }
  results.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${item.title}</span><span class="score">${item.score}</span>`;
    resultsList.appendChild(li);
  });
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: queryInput.value, top_k: 5 }),
  })
    .then((res) => res.json())
    .then((data) => renderResults(data.results || []));
});

seedButton.addEventListener("click", () => {
  fetch("/api/seed", { method: "POST" })
    .then((res) => res.json())
    .then(() => alert("Sample docs loaded."));
});
