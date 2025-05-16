document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('dest-list');
  let current = window.destConfig.page;
  const pages = window.destConfig.pages;

  async function loadPage(p) {
    const params = new URLSearchParams({
      page: p,
      visa: window.destConfig.visaFilter,
      in_budget: window.destConfig.inBudget,
      available_to_passport: window.destConfig.passportOk,
      sort_by: window.destConfig.sortBy,
      search: window.destConfig.search
    });
    const resp = await fetch(`/destinations/api?${params.toString()}`);
    const data = await resp.json();
    data.items.forEach(it => {
      const div = document.createElement('div');
      div.className = 'list-group-item mb-3 p-3 rounded';
      div.innerHTML = `
        <h4>${it.city} <span class="text-success">${it.score}% Match</span></h4>
        <small class="text-muted">${it.country}</small>
      `;
      list.appendChild(div);
    });
  }

  document.getElementById('next-page').addEventListener('click', async e => {
    e.preventDefault();
    if (current < pages) {
      await loadPage(++current);
    }
  });

  document.getElementById('prev-page').addEventListener('click', async e => {
    e.preventDefault();
    if (current > 1) {
      current--;
      list.innerHTML = '';
      await loadPage(current);
    }
  });

  // preload all pages in background
  for (let p = 2; p <= pages; p++) {
    loadPage(p);
  }
});
