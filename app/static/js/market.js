/* Market dashboard: overview, PC/mobile rankings, breakouts, report, crawl trigger, exports */
// Toggle Export Menu
function toggleExportMenu() {
  const menu = document.getElementById('exportMenu');
  menu.classList.toggle('hidden');
}
window.addEventListener('click', (e) => {
  if (!e.target.closest('#exportMenu') && !e.target.closest('button[onclick="toggleExportMenu()"]')) {
    document.getElementById('exportMenu')?.classList.add('hidden');
  }
});

// Load Overview Data
async function loadOverview() {
  const date = document.getElementById('targetDate').value;
  try {
    const res = await fetch(`/api/overview?target_date=${date}`);
    const data = await res.json();

    document.getElementById('statTotalTracked').innerText = (data.total_tracked || 0).toLocaleString();
    const pCounts = data.platform_counts || {};
    document.getElementById('statPlatformSplit').innerText = `PC: ${pCounts.pc_steam || 0} | iOS: ${pCounts.mobile_appstore || 0} | Android: ${pCounts.mobile_googleplay || 0}`;

    if (data.top_steam_ccu && data.top_steam_ccu.length > 0) {
      const topPC = data.top_steam_ccu[0];
      document.getElementById('statPeakGame').innerText = topPC.title;
      document.getElementById('statPeakCCU').innerText = `${(topPC.player_count || 0).toLocaleString()} CCU`;
    }

    if (data.rising_games && data.rising_games.length > 0) {
      const topRiser = data.rising_games[0];
      document.getElementById('statBreakoutGame').innerText = topRiser.title;
      document.getElementById('statBreakoutDelta').innerText = `+${topRiser.rank_change_day} bậc rank`;
    } else {
      document.getElementById('statBreakoutGame').innerText = "Đang tích lũy";
      document.getElementById('statBreakoutDelta').innerText = "Cần ít nhất 2 ngày dữ liệu để so sánh";
    }

    const risingContainer = document.getElementById('overviewRisingContainer');
    if (data.rising_games && data.rising_games.length > 0) {
      risingContainer.innerHTML = data.rising_games.map(g => {
        const isPC = (g.platform || '').includes('pc');
        return `
          <div onclick="openGameModal('${g.game_id}')" class="glass-card p-4 rounded-xl flex items-center justify-between border border-slate-800 hover:border-indigo-500 cursor-pointer transition-all hover:scale-[1.01]">
            <div class="flex items-center gap-3">
              <img src="${g.icon_url || 'https://placehold.co/80x80/1e293b/white?text=Game'}" class="w-12 h-12 rounded-lg object-cover bg-slate-800" onerror="this.src='https://placehold.co/80x80/1e293b/white?text=Game'">
              <div>
                <h4 class="font-bold text-white text-sm line-clamp-1 hover:text-indigo-400">${g.title}</h4>
                <p class="text-xs text-slate-400 line-clamp-1">${g.developer || g.genre || ''}</p>
                <span class="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full ${isPC ? 'bg-indigo-500/10 text-indigo-400' : 'bg-pink-500/10 text-pink-400'} font-medium">
                  ${isPC ? 'PC Steam' : 'Mobile'}
                </span>
              </div>
            </div>
            <div class="text-right">
              <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center gap-1">
                <i data-lucide="arrow-up" class="w-3.5 h-3.5"></i> +${g.rank_change_day}
              </span>
              <p class="text-[10px] text-slate-500 mt-1">Rank #${g.rank}</p>
            </div>
          </div>
        `;
      }).join('');
    } else {
      risingContainer.innerHTML = `
        <div class="glass-card p-4 rounded-xl col-span-3 text-center text-slate-400 text-xs">
          Chưa phát hiện biến động đột biến hoặc mới thu thập ngày đầu tiên. Hãy nhấn <b>Crawl Dữ Liệu Ngay</b> để làm mới.
        </div>
      `;
    }

    const topPCList = document.getElementById('topPCList');
    if (data.top_steam_ccu && data.top_steam_ccu.length > 0) {
      topPCList.innerHTML = data.top_steam_ccu.map(g => `
        <div onclick="openGameModal('${g.game_id}')" class="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 hover:bg-slate-900 cursor-pointer transition-colors">
          <div class="flex items-center gap-2.5">
            <span class="text-xs font-bold text-indigo-400 w-5">#${g.rank}</span>
            <img src="${g.icon_url}" class="w-8 h-8 rounded object-cover bg-slate-800" onerror="this.src='https://placehold.co/40x40/1e293b/white?text=PC'">
            <div class="max-w-[150px]">
              <p class="font-medium text-white text-xs truncate hover:text-indigo-400">${g.title}</p>
              <p class="text-[10px] text-emerald-400 truncate font-semibold">${g.estimated_revenue_daily_formatted || 'N/A'}/ngày</p>
            </div>
          </div>
          <span class="text-xs font-bold text-slate-200">${(g.player_count || 0).toLocaleString()} CCU</span>
        </div>
      `).join('');
    } else {
      topPCList.innerHTML = '<p class="text-xs text-slate-500">Chưa có dữ liệu PC.</p>';
    }

    const topMobileList = document.getElementById('topMobileList');
    if (data.top_mobile_grossing && data.top_mobile_grossing.length > 0) {
      topMobileList.innerHTML = data.top_mobile_grossing.map(g => `
        <div onclick="openGameModal('${g.game_id}')" class="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 hover:bg-slate-900 cursor-pointer transition-colors">
          <div class="flex items-center gap-2.5">
            <span class="text-xs font-bold text-emerald-400 w-5">#${g.rank}</span>
            <img src="${g.icon_url}" class="w-8 h-8 rounded-lg object-cover bg-slate-800" onerror="this.src='https://placehold.co/40x40/1e293b/white?text=App'">
            <div class="max-w-[150px]">
              <p class="font-medium text-white text-xs truncate hover:text-emerald-400">${g.title}</p>
              <p class="text-[10px] text-emerald-400 truncate font-semibold">${g.estimated_revenue_daily_formatted || 'N/A'}/ngày</p>
            </div>
          </div>
          <span class="text-xs font-bold text-amber-400">⭐ ${g.score || '4.5'}</span>
        </div>
      `).join('');
    } else {
      topMobileList.innerHTML = '<p class="text-xs text-slate-500">Chưa có dữ liệu Mobile.</p>';
    }

    loadGenreChart();
  } catch (err) {
    console.error("Error loading overview:", err);
  }
  lucide.createIcons();
}

// Load Genre Distribution Chart
async function loadGenreChart() {
  const date = document.getElementById('targetDate').value;
  try {
    const res = await fetch(`/api/genres?target_date=${date}`);
    const data = await res.json();
    if (data && data.length > 0) {
      document.getElementById('statDominantGenre').innerText = data[0].genre || '--';
      document.getElementById('statGenreShare').innerText = `${data[0].count} games trong Top`;

      const labels = data.map(d => d.genre);
      const counts = data.map(d => d.count);

      const ctx = document.getElementById('genreChart').getContext('2d');
      if (genreChartInstance) genreChartInstance.destroy();

      genreChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: counts,
            backgroundColor: [
              '#6366f1', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6',
              '#06b6d4', '#3b82f6', '#f43f5e', '#14b8a6', '#64748b'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', font: { size: 10 }, boxWidth: 10 }
            }
          },
          cutout: '65%'
        }
      });
    }
  } catch (err) {
    console.error("Error loading genres:", err);
  }
}

// Load PC Rankings Table
async function loadPCRankings() {
  const date = document.getElementById('targetDate').value;
  const rankingType = document.getElementById('pcRankingType').value;
  const genre = document.getElementById('pcGenreFilter').value;
  const search = document.getElementById('pcSearchInput').value;

  const tbody = document.getElementById('pcTableBody');
  tbody.innerHTML = '<tr><td colspan="8" class="py-6 text-center text-slate-400">Đang tải danh sách PC...</td></tr>';

  try {
    const url = `/api/rankings?platform=pc_steam&ranking_type=${rankingType}&genre=${genre}&search=${encodeURIComponent(search)}&target_date=${date}&limit=50`;
    const res = await fetch(url);
    const games = await res.json();

    if (games.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="py-6 text-center text-slate-400">Không tìm thấy tựa game nào phù hợp.</td></tr>';
      return;
    }

    tbody.innerHTML = games.map(g => {
      let deltaBadge = '<span class="text-slate-500">-</span>';
      if (g.is_new_entry) {
        deltaBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-400">NEW</span>';
      } else if (g.rank_change_day > 0) {
        deltaBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 flex items-center gap-1 w-fit"><i data-lucide="arrow-up" class="w-3 h-3"></i> +${g.rank_change_day}</span>`;
      } else if (g.rank_change_day < 0) {
        deltaBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 flex items-center gap-1 w-fit"><i data-lucide="arrow-down" class="w-3 h-3"></i> ${g.rank_change_day}</span>`;
      }

      return `
        <tr class="hover:bg-slate-900/60 transition-colors">
          <td class="py-3 px-4 font-bold text-indigo-400">#${g.rank}</td>
          <td class="py-3 px-4">
            <div class="flex items-center gap-3 cursor-pointer group" onclick="openGameModal('${g.game_id}')">
              <img src="${g.icon_url}" class="w-14 h-8 rounded object-cover bg-slate-800 group-hover:scale-105 transition-transform" onerror="this.src='https://placehold.co/80x40/1e293b/white?text=PC'">
              <div>
                <span class="font-semibold text-white group-hover:text-indigo-400 transition-colors">${g.title}</span>
                <p class="text-[10px] text-slate-400">${g.developer || ''}</p>
              </div>
            </div>
          </td>
          <td class="py-3 px-4 text-slate-300 font-medium">${g.genre || 'Action'}</td>
          <td class="py-3 px-4 text-slate-300">${g.price || 'Free'}</td>
          <td class="py-3 px-4">
            <div class="flex items-center gap-2">
              <span class="font-bold text-white">${(g.player_count || 0).toLocaleString()}</span>
              <span class="text-[10px] text-slate-400">CCU</span>
            </div>
          </td>
          <td class="py-3 px-4">
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              ${g.estimated_revenue_daily_formatted || 'N/A'}/ngày
            </span>
          </td>
          <td class="py-3 px-4">${deltaBadge}</td>
          <td class="py-3 px-4 text-center">
            <div class="flex items-center justify-center gap-1.5">
              <button onclick="quickToggleWatchlist('${g.game_id}')" class="p-1.5 rounded-lg bg-slate-800 hover:bg-amber-600/30 text-amber-300 transition-colors" title="Thêm vào Watchlist">
                <i data-lucide="star" class="w-3.5 h-3.5"></i>
              </button>
              <a href="${g.store_url}" target="_blank" class="p-1.5 rounded-lg bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white transition-colors" title="Xem trên Steam">
                <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
              </a>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error("Error loading PC rankings:", err);
  }
  lucide.createIcons();
}

// Load Mobile Rankings Table
async function loadMobileRankings() {
  const date = document.getElementById('targetDate').value;
  const country = document.getElementById('mobileCountry').value;
  const store = document.getElementById('mobileStore').value;
  const rankingType = document.getElementById('mobileRankingType').value;
  const search = document.getElementById('mobileSearchInput').value;

  const tbody = document.getElementById('mobileTableBody');
  tbody.innerHTML = '<tr><td colspan="8" class="py-6 text-center text-slate-400">Đang tải danh sách Mobile...</td></tr>';

  try {
    const url = `/api/rankings?platform=${store}&country=${country}&ranking_type=${rankingType}&search=${encodeURIComponent(search)}&target_date=${date}&limit=50`;
    const res = await fetch(url);
    const games = await res.json();

    if (games.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="py-6 text-center text-slate-400">Chưa có dữ liệu cho cấu hình này. Bạn có thể nhấn <b>Crawl Dữ Liệu Ngay</b> để kéo dữ liệu về.</td></tr>';
      return;
    }

    tbody.innerHTML = games.map(g => {
      let deltaBadge = '<span class="text-slate-500">-</span>';
      if (g.is_new_entry) {
        deltaBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-400">NEW</span>';
      } else if (g.rank_change_day > 0) {
        deltaBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 flex items-center gap-1 w-fit"><i data-lucide="arrow-up" class="w-3 h-3"></i> +${g.rank_change_day}</span>`;
      } else if (g.rank_change_day < 0) {
        deltaBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 flex items-center gap-1 w-fit"><i data-lucide="arrow-down" class="w-3 h-3"></i> ${g.rank_change_day}</span>`;
      }

      const isIOS = (g.platform || '').includes('appstore');

      return `
        <tr class="hover:bg-slate-900/60 transition-colors">
          <td class="py-3 px-4 font-bold text-emerald-400">#${g.rank}</td>
          <td class="py-3 px-4">
            <div class="flex items-center gap-3 cursor-pointer group" onclick="openGameModal('${g.game_id}')">
              <img src="${g.icon_url}" class="w-10 h-10 rounded-xl object-cover bg-slate-800 group-hover:scale-105 transition-transform" onerror="this.src='https://placehold.co/40x40/1e293b/white?text=App'">
              <div>
                <span class="font-semibold text-white group-hover:text-emerald-400 transition-colors line-clamp-1">${g.title}</span>
                <p class="text-[10px] text-slate-400 line-clamp-1">${g.developer || ''}</p>
              </div>
            </div>
          </td>
          <td class="py-3 px-4 text-slate-300 font-medium">${g.genre || 'Mobile'}</td>
          <td class="py-3 px-4">
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${isIOS ? 'bg-sky-500/10 text-sky-400' : 'bg-emerald-500/10 text-emerald-400'}">
              ${isIOS ? '🍎 iOS' : '🤖 Android'}
            </span>
          </td>
          <td class="py-3 px-4">
            <div class="flex items-center gap-1 text-amber-400 font-medium">
              <i data-lucide="star" class="w-3.5 h-3.5 fill-current"></i> ${g.score || '4.5'}
            </div>
            <p class="text-[10px] text-slate-500">${g.estimated_downloads_formatted || g.estimated_downloads || ''}</p>
          </td>
          <td class="py-3 px-4">
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              ${g.estimated_revenue_daily_formatted || 'N/A'}/ngày
            </span>
          </td>
          <td class="py-3 px-4">${deltaBadge}</td>
          <td class="py-3 px-4 text-center">
            <div class="flex items-center justify-center gap-1.5">
              <button onclick="quickToggleWatchlist('${g.game_id}')" class="p-1.5 rounded-lg bg-slate-800 hover:bg-amber-600/30 text-amber-300 transition-colors" title="Thêm vào Watchlist">
                <i data-lucide="star" class="w-3.5 h-3.5"></i>
              </button>
              <a href="${g.store_url}" target="_blank" class="p-1.5 rounded-lg bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white transition-colors" title="Mở trang Store">
                <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
              </a>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error("Error loading mobile rankings:", err);
  }
  lucide.createIcons();
}

// Load Breakout Radar
async function loadBreakoutRadar() {
  const date = document.getElementById('targetDate').value;
  const grid = document.getElementById('breakoutRadarGrid');
  grid.innerHTML = '<div class="glass-card p-6 rounded-xl col-span-2 text-center text-slate-400">Đang quét radar...</div>';

  try {
    const res = await fetch(`/api/overview?target_date=${date}`);
    const data = await res.json();
    const risers = data.rising_games || [];
    const newEntries = data.new_entries || [];

    let html = '';
    if (risers.length > 0) {
      html += risers.map(g => `
        <div onclick="openGameModal('${g.game_id}')" class="glass-card p-4 rounded-xl border border-emerald-500/30 flex items-center justify-between cursor-pointer hover:border-emerald-400 transition-all">
          <div class="flex items-center gap-3">
            <img src="${g.icon_url}" class="w-12 h-12 rounded-xl object-cover bg-slate-800" onerror="this.src='https://placehold.co/48x48/1e293b/white?text=Game'">
            <div>
              <span class="inline-block text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold mb-1">🔥 TĂNG VỌT</span>
              <h4 class="font-bold text-white text-sm line-clamp-1 hover:text-emerald-300">${g.title}</h4>
              <p class="text-xs text-slate-400">${g.genre} • ${g.platform.toUpperCase()}</p>
            </div>
          </div>
          <div class="text-right">
            <span class="text-base font-extrabold text-emerald-400">+${g.rank_change_day}</span>
            <p class="text-[10px] text-slate-400">Hiện tại: #${g.rank}</p>
          </div>
        </div>
      `).join('');
    }

    if (newEntries.length > 0) {
      html += newEntries.map(g => `
        <div onclick="openGameModal('${g.game_id}')" class="glass-card p-4 rounded-xl border border-indigo-500/30 flex items-center justify-between cursor-pointer hover:border-indigo-400 transition-all">
          <div class="flex items-center gap-3">
            <img src="${g.icon_url}" class="w-12 h-12 rounded-xl object-cover bg-slate-800" onerror="this.src='https://placehold.co/48x48/1e293b/white?text=Game'">
            <div>
              <span class="inline-block text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-bold mb-1">✨ TÂN BINH MỚI</span>
              <h4 class="font-bold text-white text-sm line-clamp-1 hover:text-indigo-300">${g.title}</h4>
              <p class="text-xs text-slate-400">${g.genre} • ${g.platform.toUpperCase()}</p>
            </div>
          </div>
          <div class="text-right">
            <span class="text-xs font-bold text-indigo-400">Rank #${g.rank}</span>
            <p class="text-[10px] text-slate-400">Lần đầu lọt Top</p>
          </div>
        </div>
      `).join('');
    }

    if (!html) {
      html = '<div class="glass-card p-6 rounded-xl col-span-2 text-center text-slate-400">Chưa ghi nhận biến động tăng vọt hoặc tân binh mới hôm nay. Hãy chạy thêm lượt crawl.</div>';
    }
    grid.innerHTML = html;
  } catch (err) {
    console.error("Error loading breakout radar:", err);
  }
}


// --- OTHER DASHBOARD HELPERS ---
async function loadMarketReport() {
  const date = document.getElementById('targetDate').value;
  const container = document.getElementById('reportContent');
  container.innerHTML = 'Đang biên soạn báo cáo thị trường...';

  try {
    const res = await fetch(`/api/report?target_date=${date}`);
    const data = await res.json();
    currentRawReport = data.markdown || '';

    let html = currentRawReport
      .replace(/^# (.*$)/gim, '<h1 class="text-xl font-bold text-white mt-4 mb-2">$1</h1>')
      .replace(/^## (.*$)/gim, '<h2 class="text-base font-bold text-indigo-300 mt-5 mb-2">$1</h2>')
      .replace(/^> (.*$)/gim, '<blockquote class="border-l-4 border-indigo-500 pl-3 py-1 bg-slate-900/60 rounded text-slate-300 my-2">$1</blockquote>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-white font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em class="text-slate-300">$1</em>')
      .replace(/`([^`]+)`/gim, '<code class="bg-slate-800 text-indigo-300 px-1 py-0.5 rounded text-xs">$1</code>')
      .replace(/\n\n/gim, '<br>');

    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = 'Lỗi khi tạo báo cáo.';
  }
}

function copyReportMarkdown() {
  if (currentRawReport) {
    navigator.clipboard.writeText(currentRawReport);
    showToast('Đã sao chép nội dung Markdown vào Clipboard!');
  }
}

async function loadCrawlLogs() {
  const tbody = document.getElementById('logsTableBody');
  tbody.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-slate-400">Đang tải nhật ký...</td></tr>';
  try {
    const res = await fetch('/api/crawl/status');
    const data = await res.json();
    const logs = data.recent_logs || [];
    if (logs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-slate-400">Chưa có lịch sử crawl.</td></tr>';
      return;
    }

    tbody.innerHTML = logs.map(l => `
      <tr class="hover:bg-slate-900/40">
        <td class="py-2.5 px-4 text-slate-400">${l.crawled_at}</td>
        <td class="py-2.5 px-4 font-medium text-white">${l.platform}</td>
        <td class="py-2.5 px-4 uppercase text-slate-300">${l.country}</td>
        <td class="py-2.5 px-4 text-slate-300">${l.ranking_type}</td>
        <td class="py-2.5 px-4 font-bold text-indigo-400">${l.items_count}</td>
        <td class="py-2.5 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${l.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">
            ${l.status.toUpperCase()}
          </span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error("Error loading logs:", err);
  }
}

async function triggerCrawl() {
  const btn = document.getElementById('btnCrawlNow');
  const icon = document.getElementById('crawlIcon');
  btn.disabled = true;
  icon.classList.add('animate-spin');

  showToast('Đang kích hoạt Crawl ngầm cho Steam & Mobile Stores...', 'refresh-cw');

  try {
    const res = await fetch('/api/crawl?countries=us,vn,kr,jp,global', { method: 'POST' });
    const result = await res.json();
    showToast(result.message);

    setTimeout(() => {
      loadOverview();
      loadPCRankings();
      loadMobileRankings();
      loadRadarUpcoming();
      loadWatchlist();
      btn.disabled = false;
      icon.classList.remove('animate-spin');
    }, 5000);
  } catch (err) {
    btn.disabled = false;
    icon.classList.remove('animate-spin');
  }
}


function downloadExcel() {
  const date = document.getElementById('targetDate').value;
  window.location.href = `/api/export/excel?target_date=${date}`;
  showToast('Đang tải file Excel về máy...');
}

function downloadCSV() {
  const date = document.getElementById('targetDate').value;
  window.location.href = `/api/export/csv?target_date=${date}`;
  showToast('Đang tải file CSV về máy...');
}

// Initial Load
