/* Steam Web API direct sync */
// --- 8. STEAM LIVE API & STOREFRONT CONNECTOR ---
let steamPresets = [];

async function initSteamApiTab() {
  try {
    if (!steamPresets || steamPresets.length === 0) {
      const res = await fetch('/api/steam/presets');
      if (res.ok) {
        steamPresets = await res.json();
        renderSteamPresets(steamPresets);
      }
    }
    fetchSteamLiveData(730); // Default CS2
  } catch (e) {
    console.error("Error initializing Steam API tab:", e);
  }
}

function renderSteamPresets(presets) {
  const container = document.getElementById('steamPresetBtnGroup');
  if (!container) return;

  container.innerHTML = presets.map(p => `
    <button onclick="fetchSteamLiveData(${p.app_id})" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 cursor-pointer">
      <span>${p.title}</span>
      <span class="text-[10px] text-sky-400 font-mono">(${p.app_id})</span>
    </button>
  `).join('');
}

async function fetchSteamLiveData(appId) {
  const id = appId || parseInt(document.getElementById('customSteamAppId').value, 10) || 730;
  document.getElementById('customSteamAppId').value = id;

  const container = document.getElementById('steamLiveResultContainer');
  if (container) {
    container.innerHTML = `<div class="p-8 text-center text-slate-400 text-xs"><i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-sky-400"></i>Đang kết nối Steam Web API & Storefront...</div>`;
    lucide.createIcons();
  }

  try {
    const res = await fetch(`/api/steam/app/${id}`);
    if (res.ok) {
      const data = await res.json();
      renderSteamLiveCard(data);
    }
  } catch (e) {
    console.error("Error fetching live steam data:", e);
  }
}

function renderSteamLiveCard(data) {
  const container = document.getElementById('steamLiveResultContainer');
  if (!container) return;

  const d = data.details;
  const c = data.ccu;
  const r = data.reviews;
  const fmt = v => (v === null || v === undefined) ? 'N/A' : Number(v).toLocaleString();
  const isOffline = [d, c, r].some(x => x && x.status === 'OFFLINE');

  container.innerHTML = `
    <div class="glass-card rounded-2xl overflow-hidden border border-slate-800 bg-slate-900/90">
      ${isOffline ? `<div class="px-4 py-2 text-xs font-bold bg-amber-500/15 text-amber-300 border-b border-amber-500/30">⚠️ Không kết nối được Steam API — một số chỉ số hiển thị N/A (không phải số liệu thật).</div>` : ''}
      <div class="relative h-48 md:h-64 overflow-hidden bg-slate-950">
        ${d.header_image ? `<img src="${d.header_image}" class="w-full h-full object-cover opacity-60">` : ''}
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
        <div class="absolute bottom-4 left-6 right-6 flex items-end justify-between flex-wrap gap-4">
          <div>
            <span class="text-[11px] font-mono text-sky-400">Steam AppID: ${data.app_id}</span>
            <h3 class="text-2xl md:text-3xl font-black text-white">${d.title}</h3>
            <p class="text-xs text-slate-300 mt-1">${(d.developers || []).join(', ')} • ${(d.publishers || []).join(', ')}</p>
          </div>
          <div class="flex items-center gap-2">
            <a href="https://store.steampowered.com/app/${data.app_id}" target="_blank" class="px-4 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-sky-600/30">
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i> Mở Trang Steam Store
            </a>
          </div>
        </div>
      </div>

      <div class="p-6 space-y-5">
        <!-- CCU & Sentiment Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Live CCU Counter -->
          <div class="p-4 rounded-xl bg-sky-950/30 border border-sky-500/30 space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs text-sky-300 font-bold uppercase tracking-wider flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
                Người Chơi Online (Live CCU)
              </span>
              <span class="text-[10px] text-slate-400 font-mono">${c.status}</span>
            </div>
            <div class="text-3xl font-black text-white font-mono mt-1">
              ${fmt(c.live_player_count)}
            </div>
            <span class="text-[10px] text-slate-400">Đang ingame trực tiếp tại thời điểm này</span>
          </div>

          <!-- Reviews Sentiment -->
          <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="text-xs text-slate-400 font-semibold block uppercase tracking-wider">Đánh Giá Người Dùng (Steam Sentiment)</span>
            <div class="text-xl font-bold ${r.positive_percent >= 80 ? 'text-emerald-400' : 'text-amber-400'}">
              ${r.review_score_desc}${r.positive_percent != null ? ` (${r.positive_percent}%)` : ''}
            </div>
            <span class="text-[10px] text-slate-400">${fmt(r.total_reviews)} đánh giá (${fmt(r.total_positive)} tích cực)</span>
          </div>

          <!-- Price & Release -->
          <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="text-xs text-slate-400 font-semibold block uppercase tracking-wider">Giá Niêm Yết & Ngày Phát Hành</span>
            <div class="text-xl font-black text-amber-300 font-mono">${d.price}</div>
            <span class="text-[10px] text-slate-400">Phát hành: ${d.release_date}</span>
          </div>
        </div>

        <!-- Description & Genres -->
        <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
          <span class="font-bold text-slate-300 block">Mô Tả Cửa Hàng:</span>
          <p class="text-slate-400 leading-relaxed">${d.short_description}</p>
          <div class="flex items-center gap-1.5 flex-wrap pt-2 border-t border-slate-800">
            <span class="text-slate-500 font-semibold text-[11px]">Thể Loại:</span>
            ${(d.genres || []).map(g => `<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-medium border border-slate-700">${g}</span>`).join('')}
          </div>
        </div>
      </div>
    </div>
  `;

  lucide.createIcons();
}

function toggleSteamApiKeyModal() {
  const modal = document.getElementById('steamApiKeyModal');
  if (modal) modal.classList.toggle('hidden');
}

async function saveSteamApiKey() {
  const key = document.getElementById('inputSteamApiKey').value.trim();
  try {
    const res = await fetch('/api/steam/configure-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ steam_api_key: key })
    });
    if (res.ok) {
      showToast('Đã lưu Steam Web API Key thành công!');
      toggleSteamApiKeyModal();
    }
  } catch (e) {
    console.error("Error saving Steam API key:", e);
  }
}
