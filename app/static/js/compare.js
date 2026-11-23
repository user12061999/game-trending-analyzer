/* Head-to-head game comparison */
// --- COMPARE OPPONENTS ---
async function searchGameAutocomplete(target) {
  const input = document.getElementById(`compareSearch${target}`);
  const dropdown = document.getElementById(`compareDropdown${target}`);
  const q = input.value.trim();
  if (!q) {
    dropdown.classList.add('hidden');
    return;
  }

  try {
    const res = await fetch(`/api/games/search?q=${encodeURIComponent(q)}&limit=10`);
    const games = await res.json();
    if (games.length === 0) {
      dropdown.innerHTML = '<div class="p-2 text-slate-500">Không tìm thấy tựa game nào</div>';
      dropdown.classList.remove('hidden');
      return;
    }

    dropdown.innerHTML = games.map(g => `
      <div onclick="selectCompareGame('${target}', '${g.game_id}', '${escape(g.title)}')" class="p-2 hover:bg-slate-800 cursor-pointer flex items-center justify-between border-b border-slate-800 last:border-none">
        <div class="flex items-center gap-2 truncate">
          <img src="${g.icon_url}" class="w-6 h-6 rounded object-cover bg-slate-700" onerror="this.src='https://placehold.co/24x24/1e293b/white?text=G'">
          <span class="text-white font-medium truncate">${g.title}</span>
        </div>
        <span class="text-[10px] text-slate-400">#${g.rank}</span>
      </div>
    `).join('');
    dropdown.classList.remove('hidden');
  } catch (err) {
    console.error(err);
  }
}

function selectCompareGame(target, gameId, encodedTitle) {
  const title = unescape(encodedTitle);
  document.getElementById(`compareGameId${target}`).value = gameId;
  document.getElementById(`compareSearch${target}`).value = title;
  document.getElementById(`compareSelectedTitle${target}`).innerHTML = `
    <span class="w-2 h-2 rounded-full ${target === 'A' ? 'bg-indigo-500' : 'bg-amber-400'}"></span> Đã chọn: ${title}
  `;
  document.getElementById(`compareDropdown${target}`).classList.add('hidden');
}

function setComparePreset(idA, idB) {
  switchTab('compare');
  document.getElementById('compareGameIdA').value = idA;
  document.getElementById('compareGameIdB').value = idB;
  executeComparison();
}

async function executeComparison() {
  const idA = document.getElementById('compareGameIdA').value;
  const idB = document.getElementById('compareGameIdB').value;
  const container = document.getElementById('compareResultContainer');
  container.innerHTML = '<div class="glass-card p-6 rounded-2xl text-center text-slate-400">Đang nạp dữ liệu so sánh...</div>';

  try {
    const res = await fetch(`/api/compare?game_a=${encodeURIComponent(idA)}&game_b=${encodeURIComponent(idB)}`);
    const data = await res.json();
    if (data.error) {
      container.innerHTML = `<div class="glass-card p-6 rounded-2xl text-center text-rose-400">${data.error}</div>`;
      return;
    }

    const ga = data.game_a;
    const gb = data.game_b;
    const sa = data.stats_a || {};
    const sb = data.stats_b || {};
    const timeline = data.timeline || [];

    container.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="glass-card p-5 rounded-2xl border-l-4 border-indigo-500 space-y-4">
          <div class="flex items-center gap-3">
            <img src="${ga.icon_url}" class="w-14 h-14 rounded-xl object-cover bg-slate-800 shadow" onerror="this.src='https://placehold.co/60x60/1e293b/white?text=A'">
            <div>
              <h3 class="font-bold text-white text-base">${ga.title}</h3>
              <p class="text-xs text-slate-400">${ga.developer} • ${ga.genre}</p>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 font-semibold mt-1 inline-block">${ga.platform.toUpperCase()}</span>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <span class="text-slate-400 text-[10px] block">Rank Hiện Tại</span>
              <span class="font-bold text-indigo-400 text-sm">#${ga.rank}</span>
            </div>
            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <span class="text-slate-400 text-[10px] block">Doanh Thu/Ngày</span>
              <span class="font-bold text-emerald-400 text-xs">${ga.estimated_revenue_daily_formatted || 'N/A'}</span>
            </div>
            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <span class="text-slate-400 text-[10px] block">Đánh Giá</span>
              <span class="font-bold text-amber-400 text-sm">⭐ ${ga.score || '4.5'}</span>
            </div>
          </div>
        </div>

        <div class="glass-card p-5 rounded-2xl border-l-4 border-amber-400 space-y-4">
          <div class="flex items-center gap-3">
            <img src="${gb.icon_url}" class="w-14 h-14 rounded-xl object-cover bg-slate-800 shadow" onerror="this.src='https://placehold.co/60x60/1e293b/white?text=B'">
            <div>
              <h3 class="font-bold text-white text-base">${gb.title}</h3>
              <p class="text-xs text-slate-400">${gb.developer} • ${gb.genre}</p>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-400 font-semibold mt-1 inline-block">${gb.platform.toUpperCase()}</span>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <span class="text-slate-400 text-[10px] block">Rank Hiện Tại</span>
              <span class="font-bold text-amber-400 text-sm">#${gb.rank}</span>
            </div>
            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <span class="text-slate-400 text-[10px] block">Doanh Thu/Ngày</span>
              <span class="font-bold text-emerald-400 text-xs">${gb.estimated_revenue_daily_formatted || 'N/A'}</span>
            </div>
            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <span class="text-slate-400 text-[10px] block">Đánh Giá</span>
              <span class="font-bold text-amber-400 text-sm">⭐ ${gb.score || '4.5'}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="glass-card p-5 rounded-2xl border border-slate-800 space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i data-lucide="line-chart" class="w-4 h-4 text-amber-400"></i>
            So Sánh Quỹ Đạo Thứ Hạng Theo Dòng Thời Gian
          </h3>
          <span class="text-[10px] text-slate-400">*Trục Y đảo ngược (#1 ở trên đỉnh)</span>
        </div>
        <div class="h-72 bg-slate-950/80 p-3 rounded-xl border border-slate-800">
          <canvas id="compareLineChart"></canvas>
        </div>
      </div>
    `;

    renderCompareChart(timeline, ga.title, gb.title);
    lucide.createIcons();
  } catch (err) {
    console.error("Comparison error:", err);
  }
}

function renderCompareChart(timeline, titleA, titleB) {
  const ctx = document.getElementById('compareLineChart').getContext('2d');
  if (compareChartInstance) compareChartInstance.destroy();

  const labels = timeline.map(t => t.date);
  const dataA = timeline.map(t => t.game_a_rank);
  const dataB = timeline.map(t => t.game_b_rank);

  compareChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: titleA,
          data: dataA,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderWidth: 2.5,
          tension: 0.35,
          fill: false
        },
        {
          label: titleB,
          data: dataB,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.2)',
          borderWidth: 2.5,
          tension: 0.35,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8', font: { size: 10 } }
        },
        y: {
          reverse: true,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#cbd5e1', font: { size: 10 } }
        }
      },
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { size: 11 } } }
      }
    }
  });
}
