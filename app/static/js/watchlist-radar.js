/* Upcoming games radar and watchlist */
// --- FEATURE: MOBILE RADAR (UPCOMING & PRE-REGISTRATION) ---
let currentActiveRadarGame = null;
const debounceRadarSearch = debounce(() => loadRadarUpcoming(), 350);

async function loadRadarUpcoming() {
  const grid = document.getElementById('radarGamesGrid');
  grid.innerHTML = '<div class="col-span-full py-12 text-center text-slate-400">Đang trinh sát các tựa game Mobile sắp ra mắt...</div>';

  try {
    // 1. Fetch Stats
    fetch('/api/radar/stats')
      .then(res => res.json())
      .then(stats => {
        document.getElementById('radarStatTotal').innerText = stats.total_tracked || 0;
        const totalEl = document.getElementById('radarStatTotal');
        if (totalEl && stats.curated_count) totalEl.title = `${stats.curated_count} game từ danh sách nhập tay (chưa xác minh), còn lại phát hiện tự động từ App Store`;
        document.getElementById('radarStatCritical').innerText = stats.critical_threats || 0;
        document.getElementById('radarStatImminent').innerText = stats.imminent_30d || 0;
        if (stats.top_threatened_genres && stats.top_threatened_genres.length > 0) {
          document.getElementById('radarStatTopGenre').innerText = stats.top_threatened_genres[0].genre;
        } else {
          document.getElementById('radarStatTopGenre').innerText = 'Chưa xác định';
        }
      })
      .catch(err => console.error("Error loading radar stats:", err));

    // 2. Fetch Games
    const region = document.getElementById('radarFilterRegion').value;
    const threat = document.getElementById('radarFilterThreat').value;
    const search = document.getElementById('radarSearchInput').value.trim();

    const params = new URLSearchParams();
    if (region && region !== 'all') params.append('region', region);
    if (threat && threat !== 'all') params.append('threat_level', threat);
    if (search) params.append('search', search);

    const res = await fetch(`/api/radar/upcoming?${params.toString()}`);
    const data = await res.json();
    const games = data.games || [];

    if (games.length === 0) {
      grid.innerHTML = `
        <div class="col-span-full py-12 text-center glass-card rounded-2xl border border-slate-800 space-y-3">
          <i data-lucide="crosshair" class="w-10 h-10 text-slate-500 mx-auto"></i>
          <p class="text-slate-300 font-semibold">Không tìm thấy tựa game nào phù hợp với bộ lọc.</p>
          <p class="text-xs text-slate-500">Hãy thử đổi quốc gia hoặc tìm kiếm bằng từ khóa khác.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    grid.innerHTML = games.map(g => {
      let threatBadgeClass = 'bg-slate-700/30 text-slate-300 border-slate-600/30';
      let threatText = '🟡 Trung Bình';
      let cardBorderClass = 'border-slate-800';

      if (g.threat_level === 'CRITICAL') {
        threatBadgeClass = 'bg-rose-500/20 text-rose-400 border-rose-500/40 font-bold';
        threatText = '🔴 CỰC KỲ NGUY HIỂM';
        cardBorderClass = 'border-rose-500/30 hover:border-rose-500/60 shadow-rose-950/20';
      } else if (g.threat_level === 'HIGH') {
        threatBadgeClass = 'bg-amber-500/20 text-amber-400 border-amber-500/40 font-bold';
        threatText = '🟠 NGUY HIỂM CAO';
        cardBorderClass = 'border-amber-500/30 hover:border-amber-500/60';
      }

      let countdownClass = 'bg-slate-800 text-slate-300 border-slate-700';
      if (g.countdown_days <= 30 && g.countdown_days > 0) {
        countdownClass = 'bg-rose-500/20 text-rose-400 border-rose-500/30 font-bold animate-pulse';
      } else if (g.countdown_days <= 60 && g.countdown_days > 0) {
        countdownClass = 'bg-amber-500/20 text-amber-400 border-amber-500/30 font-bold';
      }

      const countdownLabel = g.countdown_days > 0 ? `Còn ${g.countdown_days} ngày` : 'Sắp ra mắt';
      const sourceBadge = g.is_verified
        ? '<span class="px-2 py-0.5 rounded-full text-[10px] border bg-emerald-500/20 text-emerald-300 border-emerald-500/40" title="Phát hiện tự động từ App Store">✔ App Store</span>'
        : '<span class="px-2 py-0.5 rounded-full text-[10px] border bg-slate-900/80 text-amber-300 border-amber-500/40" title="Danh sách nhập tay trong code: ngày ra mắt, hype, lượt đăng ký và mức đe dọa chưa được xác minh; ảnh là ảnh minh họa">✎ Thủ công · chưa xác minh</span>';
      const hasHype = g.hype_score !== null && g.hype_score !== undefined;
      const isTracked = g.is_tracked === 1;
      const starClass = isTracked ? 'text-amber-400 fill-amber-400' : 'text-slate-400 hover:text-amber-400';

      return `
        <div class="glass-card rounded-2xl border ${cardBorderClass} overflow-hidden flex flex-col justify-between transition-all hover:scale-[1.01] hover:shadow-xl group">
          <div>
            <!-- Card Header Banner & Overlays -->
            <div class="relative h-32 bg-slate-800 overflow-hidden">
              <img src="${escHtml(g.banner_url || g.icon_url)}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onerror="this.src='https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&auto=format&fit=crop&q=80'">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent"></div>
              
              <!-- Badges on Banner -->
              <div class="absolute top-3 left-3 flex items-center gap-1.5 flex-wrap">
                <span class="px-2 py-0.5 rounded-full text-[10px] border ${threatBadgeClass}">
                  ${threatText}
                </span>
                <span class="px-2 py-0.5 rounded-full text-[10px] border ${countdownClass}">
                  ⏳ ${countdownLabel}
                </span>
                ${sourceBadge}
              </div>

              <div class="absolute top-3 right-3 flex items-center gap-1.5">
                <button onclick="toggleRadarTrack(${g.id}, this)" class="p-1.5 rounded-xl bg-slate-900/80 backdrop-blur-sm border border-slate-700/80 transition-colors cursor-pointer" title="Ghim theo dõi">
                  <i data-lucide="star" class="w-4 h-4 ${starClass}"></i>
                </button>
                <button onclick="triggerRadarAlertTest(${g.id})" class="p-1.5 rounded-xl bg-slate-900/80 backdrop-blur-sm border border-slate-700/80 text-slate-400 hover:text-pink-400 transition-colors cursor-pointer" title="Bắn alert thử về Discord/Telegram">
                  <i data-lucide="bell" class="w-4 h-4"></i>
                </button>
              </div>
            </div>

            <!-- Card Content -->
            <div class="p-4 space-y-3">
              <div class="flex items-start gap-3">
                <img src="${escHtml(g.icon_url)}" class="w-12 h-12 rounded-xl object-cover bg-slate-800 border border-slate-700 shadow shrink-0 -mt-7 relative z-10" onerror="this.src='https://placehold.co/48x48/1e293b/white?text=Game'">
                <div class="min-w-0 flex-1">
                  <h3 class="text-sm font-bold text-white group-hover:text-rose-400 transition-colors truncate" title="${escHtml(g.title)}">
                    ${escHtml(g.title)}
                  </h3>
                  <p class="text-[11px] text-slate-400 truncate">
                    ${escHtml(g.publisher || g.developer || 'NPH Chưa công bố')}
                  </p>
                </div>
              </div>

              <!-- Genre & Regions -->
              <div class="flex items-center gap-2 text-[10px] text-slate-300 flex-wrap">
                <span class="px-2 py-0.5 rounded bg-slate-800 border border-slate-700/80">${escHtml(g.genre || 'Game')}</span>
                <span class="px-2 py-0.5 rounded bg-slate-800 text-indigo-400 border border-slate-700/80">${escHtml(g.platform || 'iOS / Android')}</span>
                <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/80">Khu vực: ${escHtml(g.regions || 'Global')}</span>
              </div>

              <!-- Metrics: Pre-reg & Hype -->
              <div class="grid grid-cols-2 gap-2 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs">
                <div>
                  <span class="text-[10px] text-slate-400 uppercase font-semibold block">Đăng ký trước:</span>
                  <span class="font-bold text-emerald-400">${escHtml(g.pre_reg_count || 'Đang mở')}</span>
                </div>
                <div>
                  <div class="flex items-center justify-between text-[10px] text-slate-400 uppercase font-semibold">
                    <span>Hype Nhiệt:</span>
                    <span class="text-amber-400 font-bold">${hasHype ? g.hype_score + '/100' : 'N/A'}</span>
                  </div>
                  <div class="w-full bg-slate-800 h-1.5 rounded-full mt-1 overflow-hidden">
                    <div class="bg-gradient-to-r from-amber-500 to-rose-500 h-full rounded-full" style="width: ${hasHype ? Number(g.hype_score) : 0}%"></div>
                  </div>
                </div>
              </div>

              <!-- Tactical Advice Snippet -->
              <div class="text-[11px] text-slate-300/90 bg-rose-950/10 border border-rose-500/20 p-2.5 rounded-xl leading-relaxed line-clamp-2">
                <span class="text-rose-400 font-bold">⚠️ Khuyến nghị:</span> ${escHtml(g.tactical_advice || g.threat_analysis || '')}
              </div>
            </div>
          </div>

          <!-- Action Footer -->
          <div class="p-4 pt-0">
            <button onclick="openRadarModal(${g.id})" class="w-full py-2 px-3 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-200 hover:text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer">
              <i data-lucide="shield-alert" class="w-3.5 h-3.5"></i>
              <span>Xem Phân Tích Đe Dọa & Chiến Thuật</span>
            </button>
          </div>
        </div>
      `;
    }).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error loading radar games:", err);
    grid.innerHTML = '<div class="col-span-full py-8 text-center text-rose-400">Lỗi tải dữ liệu Radar Mobile. Vui lòng thử lại.</div>';
  }
}

async function openRadarModal(gameId) {
  try {
    const res = await fetch(`/api/radar/game/${gameId}`);
    const game = await res.json();
    if (game.error) {
      showToast(game.error);
      return;
    }

    currentActiveRadarGame = game;

    document.getElementById('radarModalIcon').src = game.icon_url || 'https://placehold.co/64x64/1e293b/white?text=Game';
    document.getElementById('radarModalTitle').innerText = game.title;
    document.getElementById('radarModalDevPub').innerText = `NPH: ${game.publisher || '--'} | Studio phát triển: ${game.developer || '--'}`;
    document.getElementById('radarModalGenre').innerText = game.genre || '--';
    document.getElementById('radarModalPlatform').innerText = game.platform || 'iOS / Android';
    document.getElementById('radarModalRegions').innerText = `Khu vực: ${game.regions || 'Global'}`;

    const threatBadge = document.getElementById('radarModalThreatBadge');
    if (game.threat_level === 'CRITICAL') {
      threatBadge.className = 'text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30';
      threatBadge.innerText = '🔴 CỰC KỲ NGUY HIỂM (CRITICAL)';
    } else if (game.threat_level === 'HIGH') {
      threatBadge.className = 'text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30';
      threatBadge.innerText = '🟠 NGUY HIỂM CAO (HIGH)';
    } else {
      threatBadge.className = 'text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-slate-700/30 text-slate-300 border border-slate-600/30';
      threatBadge.innerText = '🟡 TRUNG BÌNH (MEDIUM)';
    }

    document.getElementById('radarModalDate').innerText = game.expected_release_date || 'Chưa công bố';
    document.getElementById('radarModalDaysLeft').innerText = game.countdown_days > 0 ? `Còn ${game.countdown_days} ngày` : 'Sắp diễn ra';
    document.getElementById('radarModalPreReg').innerText = (game.pre_reg_count || 'Đang mở')
      + (game.is_verified ? '' : '  ⚠️ (nhập tay, chưa xác minh)');
    document.getElementById('radarModalHype').innerText = (game.hype_score === null || game.hype_score === undefined) ? 'N/A' : `${game.hype_score} / 100`;

    document.getElementById('radarModalAudience').innerText = game.target_audience || 'Game thủ dòng game di động.';
    document.getElementById('radarModalThreatAnalysis').innerText = game.threat_analysis || 'Chưa có phân tích chi tiết.';
    document.getElementById('radarModalTacticalAdvice').innerText = game.tactical_advice || 'Theo dõi thêm diễn biến đăng ký trước.';

    const storeLink = document.getElementById('radarModalStoreLink');
    if (game.store_url) {
      storeLink.href = game.store_url;
      storeLink.classList.remove('hidden');
    } else {
      storeLink.classList.add('hidden');
    }

    updateRadarModalTrackBtn(game.is_tracked === 1);

    document.getElementById('radarDetailModal').classList.remove('hidden');
    lucide.createIcons();
  } catch (err) {
    console.error("Error opening radar modal:", err);
  }
}

function updateRadarModalTrackBtn(isTracked) {
  const btn = document.getElementById('radarModalTrackBtn');
  const icon = document.getElementById('radarModalTrackIcon');
  const label = document.getElementById('radarModalTrackLabel');

  if (isTracked) {
    btn.className = 'px-3.5 py-2 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer';
    icon.classList.add('fill-amber-300');
    label.innerText = 'Đang Theo Dõi ⭐';
  } else {
    btn.className = 'px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer';
    icon.classList.remove('fill-amber-300');
    label.innerText = 'Ghim Theo Dõi';
  }
  lucide.createIcons();
}

function closeRadarModal() {
  document.getElementById('radarDetailModal').classList.add('hidden');
}

async function toggleRadarTrack(gameId, btnElement) {
  try {
    const res = await fetch(`/api/radar/track/${gameId}`, { method: 'POST' });
    const data = await res.json();
    const isTracked = data.is_tracked;

    if (btnElement) {
      const icon = btnElement.querySelector('i');
      if (icon) {
        if (isTracked) {
          icon.classList.add('text-amber-400', 'fill-amber-400');
          icon.classList.remove('text-slate-400');
        } else {
          icon.classList.remove('text-amber-400', 'fill-amber-400');
          icon.classList.add('text-slate-400');
        }
      }
    }

    showToast(isTracked ? 'Đã ghim game vào danh sách theo dõi Radar!' : 'Đã hủy theo dõi game này.');
  } catch (err) {
    console.error("Error toggling radar track:", err);
  }
}

async function toggleRadarModalTrack() {
  if (!currentActiveRadarGame) return;
  try {
    const res = await fetch(`/api/radar/track/${currentActiveRadarGame.id}`, { method: 'POST' });
    const data = await res.json();
    currentActiveRadarGame.is_tracked = data.is_tracked ? 1 : 0;
    updateRadarModalTrackBtn(data.is_tracked);
    showToast(data.is_tracked ? 'Đã ghim game vào danh sách theo dõi Radar!' : 'Đã hủy theo dõi game này.');
    loadRadarUpcoming();
  } catch (err) {
    console.error("Error toggling modal track:", err);
  }
}

async function triggerRadarAlertTest(gameId) {
  try {
    showToast('Đang gửi cảnh báo trinh sát Mobile về Discord & Telegram...');
    const res = await fetch(`/api/radar/alert-test/${gameId}`, { method: 'POST' });
    const data = await res.json();
    if (data.alert_dispatched) {
      showToast('Đã bắn cảnh báo thành công qua Webhook / Bot!', 'bell');
    } else {
      showToast('Chưa gửi được: Hãy kiểm tra cấu hình Discord Webhook hoặc Telegram Bot trong tab Cài Đặt.', 'alert-triangle');
    }
  } catch (err) {
    showToast('Lỗi khi gửi cảnh báo.');
  }
}

async function triggerRadarModalAlertTest() {
  if (!currentActiveRadarGame) return;
  await triggerRadarAlertTest(currentActiveRadarGame.id);
}

async function refreshRadarData() {
  const btn = document.getElementById('radarRefreshBtn');
  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4 animate-spin"></i> Đang trinh sát...';
  lucide.createIcons();

  try {
    const res = await fetch('/api/radar/refresh', { method: 'POST' });
    const data = await res.json();
    showToast(`Đã đồng bộ ${data.result.total_games || 0} tựa game mobile sắp ra mắt!`, 'check-circle');
    await loadRadarUpcoming();
  } catch (err) {
    showToast('Lỗi khi làm mới dữ liệu Radar.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4"></i> Cập Nhật Radar';
    lucide.createIcons();
  }
}

// --- FEATURE: WATCHLIST & RIVALS ---
async function loadWatchlist() {
  const tbody = document.getElementById('watchlistTableBody');
  tbody.innerHTML = '<tr><td colspan="8" class="py-6 text-center text-slate-400">Đang tải danh sách quan sát...</td></tr>';

  try {
    const res = await fetch('/api/watchlist');
    const items = await res.json();

    if (items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="py-12 text-center space-y-3">
            <i data-lucide="star" class="w-8 h-8 text-amber-400/40 mx-auto"></i>
            <p class="text-slate-300 font-medium">Danh sách theo dõi đang trống.</p>
            <p class="text-xs text-slate-500 max-w-md mx-auto">Hãy nhấp vào biểu tượng ⭐ trên bất kỳ tựa game nào trong bảng PC, Mobile hoặc Popup để ghim vào danh sách theo dõi riêng.</p>
          </td>
        </tr>
      `;
      lucide.createIcons();
      return;
    }

    tbody.innerHTML = items.map(g => {
      const isRival = g.is_rival === 1;
      const badgeClass = isRival ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30';
      const badgeText = isRival ? '⚔️ Đối Thủ Cạnh Tranh' : '🎮 Game Của Tôi';

      let deltaBadge = '<span class="text-slate-500">-</span>';
      if (g.rank_change_day > 0) {
        deltaBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 flex items-center gap-1 w-fit"><i data-lucide="arrow-up" class="w-3 h-3"></i> +${g.rank_change_day}</span>`;
      } else if (g.rank_change_day < 0) {
        deltaBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 flex items-center gap-1 w-fit"><i data-lucide="arrow-down" class="w-3 h-3"></i> ${g.rank_change_day}</span>`;
      }

      return `
        <tr class="hover:bg-slate-900/60 transition-colors">
          <td class="py-3 px-4">
            <div class="flex items-center gap-3 cursor-pointer group" onclick="openGameModal('${g.game_id}')">
              <img src="${g.icon_url}" class="w-10 h-10 rounded-xl object-cover bg-slate-800 group-hover:scale-105 transition-transform" onerror="this.src='https://placehold.co/40x40/1e293b/white?text=Game'">
              <div>
                <span class="font-semibold text-white group-hover:text-indigo-400 transition-colors">${g.title}</span>
                <p class="text-[10px] text-slate-400">${g.developer || ''}</p>
              </div>
            </div>
          </td>
          <td class="py-3 px-4">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${badgeClass}">
              ${badgeText}
            </span>
          </td>
          <td class="py-3 px-4 text-slate-300 font-medium">${(g.platform || '').toUpperCase()}</td>
          <td class="py-3 px-4 font-bold text-indigo-400">#${g.rank}</td>
          <td class="py-3 px-4">${deltaBadge}</td>
          <td class="py-3 px-4 text-emerald-400 font-semibold">${g.estimated_revenue_daily_formatted || 'N/A'}/ngày</td>
          <td class="py-3 px-4 text-slate-400 max-w-[150px] truncate">${g.notes || '--'}</td>
          <td class="py-3 px-4 text-center">
            <div class="flex items-center justify-center gap-2">
              <button onclick="setComparePreset('${g.game_id}', '730')" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-amber-300 text-[10px] font-semibold border border-slate-700" title="So sánh với game khác">
                ⚔️ So Sánh
              </button>
              <button onclick="removeFromWatchlist('${g.game_id}')" class="p-1 rounded bg-slate-800 hover:bg-rose-600/30 text-rose-400 text-xs" title="Xóa khỏi Watchlist">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error("Error loading watchlist:", err);
  }
  lucide.createIcons();
}

async function quickToggleWatchlist(gameId) {
  try {
    const res = await fetch('/api/watchlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, is_rival: 1, notes: 'Đã thêm từ bảng xếp hạng' })
    });
    const data = await res.json();
    showToast(data.message || 'Đã thêm vào danh sách quan sát!');
  } catch (err) {
    showToast('Lỗi khi thêm vào Watchlist.');
  }
}

async function toggleModalWatchlist() {
  if (!currentActiveModalGameId) return;

  if (isCurrentModalInWatchlist) {
    await removeFromWatchlist(currentActiveModalGameId);
    isCurrentModalInWatchlist = false;
    updateModalWatchlistButton(false);
  } else {
    try {
      const res = await fetch('/api/watchlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: currentActiveModalGameId, is_rival: 0, notes: 'Theo dõi từ Modal' })
      });
      const data = await res.json();
      showToast(data.message);
      isCurrentModalInWatchlist = true;
      updateModalWatchlistButton(true);
    } catch (err) {
      showToast('Lỗi khi thêm vào Watchlist.');
    }
  }
}

async function removeFromWatchlist(gameId) {
  try {
    const res = await fetch(`/api/watchlist/${encodeURIComponent(gameId)}`, { method: 'DELETE' });
    const data = await res.json();
    showToast(data.message);
    loadWatchlist();
  } catch (err) {
    showToast('Lỗi khi xóa khỏi Watchlist.');
  }
}

function updateModalWatchlistButton(inWatchlist) {
  const btn = document.getElementById('modalWatchlistBtn');
  const label = document.getElementById('modalWatchlistLabel');
  const icon = document.getElementById('modalWatchlistIcon');

  if (inWatchlist) {
    btn.className = "bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors";
    label.innerText = "Đang Theo Dõi";
    icon.classList.add("fill-current");
  } else {
    btn.className = "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors";
    label.innerText = "Theo Dõi";
    icon.classList.remove("fill-current");
  }
  lucide.createIcons();
}
