/* Game intelligence modal and estimated revenue history */
// --- MODAL SUB-TABS NAVIGATION & MOBILE SPECIALIZATION ---
let currentActiveModalGame = null;
let currentActiveModalGameTitle = "";
let currentActiveModalGamePlatform = "mobile";
let currentActiveModalGameGenre = "RPG";
let currentActiveModalGameStoreUrl = "";
let currentActiveModalGameDesc = "";
let currentActiveModalHistory = [];
let currentModalSubTab = "deconstruct";

function switchModalSubTab(tabName) {
  currentModalSubTab = tabName;
  const subTabs = ['deconstruct', 'playprototype', 'unityplugin', 'overview', 'artprompts', 'adscript', 'gdd', 'reviews', 'aso', 'liveops'];
  subTabs.forEach(t => {
    const btn = document.getElementById(`modalSubTabBtn-${t}`);
    const content = document.getElementById(`modalSubTabContent-${t}`);
    if (!btn || !content) return;
    if (t === tabName) {
      if (t === 'deconstruct') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-lg shadow-emerald-900/40 shrink-0";
      } else if (t === 'playprototype') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-lg shadow-violet-900/40 shrink-0";
      } else if (t === 'unityplugin') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-lg shadow-purple-900/40 shrink-0";
      } else if (t === 'overview') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-lg shadow-emerald-900/40 shrink-0";
      } else if (t === 'artprompts') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-gradient-to-r from-fuchsia-600 to-pink-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-lg shadow-fuchsia-900/40 shrink-0";
      } else if (t === 'adscript') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-gradient-to-r from-rose-600 to-orange-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-lg shadow-rose-900/40 shrink-0";
      } else if (t === 'gdd') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-lg shadow-cyan-900/40 shrink-0";
      } else if (t === 'reviews') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-pink-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-md shrink-0";
      } else if (t === 'aso') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-emerald-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-md shrink-0";
      } else if (t === 'liveops') {
        btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-amber-600 text-white flex items-center gap-1.5 transition-all cursor-pointer font-bold shadow-md shrink-0";
      }
      content.classList.remove('hidden');
    } else {
      btn.className = "modal-subtab-btn px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1.5 transition-all cursor-pointer font-semibold shrink-0";
      content.classList.add('hidden');
    }
  });

  if (tabName !== 'playprototype' && typeof pausePrototypeGame === 'function') {
    pausePrototypeGame();
  }

  if (tabName === 'deconstruct') loadModalDeconstruct();
  if (tabName === 'playprototype') initOrResumePrototype();
  if (tabName === 'unityplugin') loadModalUnityPlugin();
  if (tabName === 'overview') {
    if (currentActiveModalGameId) {
      loadGameRevenueHistory(currentActiveModalGameId, sensorChartDays || 30);
    }
    if (currentActiveModalHistory && currentActiveModalHistory.length > 0) {
      renderModalTrendChart(currentActiveModalHistory, (currentActiveModalGamePlatform || '').includes('pc'));
    }
  }
  if (tabName === 'artprompts') loadModalArtPrompts();
  if (tabName === 'adscript') loadModalAdScript();
  if (tabName === 'gdd') loadModalGDD();
  if (tabName === 'reviews') loadModalReviews(currentActiveModalGameId, currentActiveModalGameTitle, currentActiveModalGamePlatform);
  if (tabName === 'aso') loadModalASO(currentActiveModalGameId, currentActiveModalGameTitle, currentActiveModalGameGenre);
  if (tabName === 'liveops') loadModalLiveOps(currentActiveModalGameId, currentActiveModalGameTitle);
  lucide.createIcons();
}

async function loadModalReviews(gameId, title, platform) {
  const metaSum = document.getElementById('reviewsMetaSummary');
  metaSum.innerText = 'Đang quét và phân tích đánh giá từ người chơi...';
  try {
    const res = await fetch(`/api/mobile/reviews/${encodeURIComponent(gameId)}?title=${encodeURIComponent(title || '')}&platform=${encodeURIComponent(platform || 'mobile')}`);
    const data = await res.json();

    const s = data.sentiment || {};
    const pos = s.positive_percentage || 0;
    const neu = s.neutral_percentage || 0;
    const neg = s.negative_percentage || 0;
    document.getElementById('sentimentBarPos').style.width = `${pos}%`;
    document.getElementById('sentimentBarNeu').style.width = `${neu}%`;
    document.getElementById('sentimentBarNeg').style.width = `${neg}%`;
    document.getElementById('sentimentPosLabel').innerText = `🟢 Tích cực: ${pos}% (${s.positive_count || 0})`;
    document.getElementById('sentimentNeuLabel').innerText = `🟡 Trung lập: ${neu}% (${s.neutral_count || 0})`;
    document.getElementById('sentimentNegLabel').innerText = `🔴 Tiêu cực: ${neg}% (${s.negative_count || 0})`;

    const churnList = document.getElementById('churnDriversList');
    const hooksList = document.getElementById('retentionHooksList');
    const reviewsGrid = document.getElementById('sampleReviewsGrid');

    if (data.status === 'no_reviews') {
      metaSum.innerText = `⚠️ ${data.message}`;
      document.getElementById('reviewsAvgRating').innerText = '--';
      const empty = '<p class="text-[11px] text-slate-500">Không có dữ liệu đánh giá thật để phân tích.</p>';
      churnList.innerHTML = empty;
      hooksList.innerHTML = empty;
      reviewsGrid.innerHTML = '';
      document.getElementById('attackCoreOpportunity').innerText = '--';
      document.getElementById('attackStepsList').innerHTML = '';
      document.getElementById('attackMarketingHook').innerText = '';
      return;
    }

    metaSum.innerText = `Dựa trên ${data.total_reviews_analyzed} đánh giá mới nhất từ ${data.review_source || 'store'}. `
      + 'Tỷ lệ mỗi nhóm = số đánh giá có nhắc tới nhóm đó (theo từ khóa).';
    document.getElementById('reviewsAvgRating').innerText = `${data.average_rating} ⭐`;

    churnList.innerHTML = (data.churn_drivers || []).map(c => {
      let badge = 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      if (c.severity === 'CRITICAL') badge = 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      return `
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white">${escHtml(c.category)}</span>
            <span class="text-[10px] px-2 py-0.5 rounded font-bold border ${badge}">${escHtml(c.severity)} · ${c.mentions} đánh giá (${c.frequency_pct}%)</span>
          </div>
          <p class="text-[11px] text-slate-300 leading-relaxed">${escHtml(c.description)}</p>
          <div class="text-[10px] text-rose-300/80 italic bg-rose-950/20 p-1.5 rounded border border-rose-500/20">"${escHtml(c.sample_quote)}"</div>
        </div>`;
    }).join('') || '<p class="text-[11px] text-slate-500">Không phát hiện nhóm phàn nàn nào trong các đánh giá tiêu cực.</p>';

    hooksList.innerHTML = (data.retention_hooks || []).map(h => `
      <div class="p-3 rounded-xl bg-slate-950 border border-emerald-500/20 space-y-1">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-emerald-300">${escHtml(h.category)}</span>
          <span class="text-[10px] text-amber-400 font-bold">${h.mentions} đánh giá (${h.frequency_pct}%)</span>
        </div>
        <p class="text-[11px] text-slate-400 leading-relaxed">${escHtml(h.description)}</p>
        <p class="text-[10px] text-emerald-300/70 italic">"${escHtml(h.sample_quote)}"</p>
      </div>`).join('') || '<p class="text-[11px] text-slate-500">Không phát hiện nhóm điểm mạnh nào trong các đánh giá tích cực.</p>';

    const pb = data.studio_attack_playbook;
    document.getElementById('attackCoreOpportunity').innerText = pb ? pb.core_opportunity : 'Chưa đủ đánh giá tiêu cực để đề xuất chiến lược.';
    document.getElementById('attackStepsList').innerHTML = (pb?.actionable_steps || []).map(st => `
      <div class="flex items-start gap-2 text-xs">
        <span class="text-emerald-400 font-bold">✔</span>
        <div><strong class="text-white">${escHtml(st.step)}:</strong> <span class="text-slate-300">${escHtml(st.detail)}</span>
        <div class="text-[10px] text-slate-500">${escHtml(st.evidence || '')}</div></div>
      </div>`).join('');
    document.getElementById('attackMarketingHook').innerText = pb ? `📢 Khẩu hiệu đề xuất: "${pb.marketing_hook}"` : '';

    reviewsGrid.innerHTML = (data.sample_reviews || []).map(r => {
      const starColor = r.rating >= 4 ? 'text-amber-400' : 'text-rose-400';
      return `
        <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] space-y-1">
          <div class="flex items-center justify-between">
            <span class="${starColor} font-bold">⭐ ${Number(r.rating)}/5${r.title ? ' - ' + escHtml(r.title) : ''}</span>
            <span class="text-[10px] text-slate-500">${escHtml(r.author || 'User')}${r.version ? ' (' + escHtml(r.version) + ')' : ''}</span>
          </div>
          <p class="text-slate-300 leading-snug line-clamp-3">${escHtml(r.content)}</p>
        </div>`;
    }).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error loading reviews:", err);
  }
}

async function loadModalASO(gameId, title, genre) {
  try {
    const res = await fetch(`/api/mobile/aso/${encodeURIComponent(gameId)}?title=${encodeURIComponent(title || '')}&genre=${encodeURIComponent(genre || 'RPG')}`);
    const data = await res.json();

    document.getElementById('asoHealthScore').innerText = `${data.aso_health_score} / 100`;
    document.getElementById('asoBrandName').innerText = data.brand_name || title;
    document.getElementById('asoTagline').innerText = data.tagline || 'Chưa cài đặt Subtitle phụ';

    const lenBadge = document.getElementById('asoTitleLenBadge');
    lenBadge.innerText = `${data.title_length} / 30 ký tự ${data.title_length <= 30 ? '✅ Chuẩn' : '⚠️ Vượt quá'}`;
    lenBadge.className = data.title_length <= 30 ? 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400' : 'px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400';

    // Keywords Density Table
    const kwBody = document.getElementById('asoKeywordsTableBody');
    kwBody.innerHTML = (data.top_keywords || []).map(k => `
      <tr class="hover:bg-slate-900/60">
        <td class="py-2 px-3 font-semibold text-white">${k.keyword}</td>
        <td class="py-2 px-3">${k.count} lần</td>
        <td class="py-2 px-3 font-bold text-indigo-400">${k.density_percentage}%</td>
        <td class="py-2 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${k.status === 'Tối ưu' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}">${k.status}</span></td>
      </tr>
    `).join('');

    // Target Keyword Opportunities
    const targetList = document.getElementById('asoTargetKeywordsList');
    targetList.innerHTML = (data.recommended_keywords || []).map(k => `
      <span class="px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-xs font-semibold">
        + ${k}
      </span>
    `).join('');

    // Suggested formulas
    const f = data.suggested_formula || {};
    document.getElementById('asoFormulaIos').innerText = f.ios_formula || '--';
    document.getElementById('asoFormulaAndroid').innerText = f.android_formula || '--';

    // Strategic advice
    const advBox = document.getElementById('asoAdviceContainer');
    advBox.innerHTML = (data.aso_advice || []).map(ad => `
      <div class="text-[11px] p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">${ad}</div>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error loading ASO data:", err);
  }
}

async function loadModalLiveOps(gameId, title) {
  try {
    const res = await fetch(`/api/mobile/liveops/${encodeURIComponent(gameId)}?title=${encodeURIComponent(title || '')}`);
    const data = await res.json();

    document.getElementById('liveopsVersion').innerText = data.current_version || 'v1.0';
    document.getElementById('liveopsReleaseDate').innerText = `Ngày ra mắt: ${data.latest_release_date || 'Gần đây'}`;
    document.getElementById('liveopsCadence').innerText = `~ ${data.update_cadence_days} ngày / lần`;
    document.getElementById('liveopsNextUpdate').innerText = data.next_expected_update || 'Đang tính toán';
    document.getElementById('liveopsRevenueSpike').innerText = data.revenue_impact?.estimated_revenue_spike || '+85% IAP';

    const evtBadge = document.getElementById('liveopsEventTypeBadge');
    evtBadge.innerText = data.primary_event_type || 'Bản cập nhật';
    evtBadge.className = `px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-${data.event_color || 'rose'}-500/20 text-${data.event_color || 'rose'}-400 border border-${data.event_color || 'rose'}-500/30`;

    document.getElementById('liveopsReleaseNotes').innerText = data.release_notes || 'Không có mô tả chi tiết.';

    // Timeline
    const tlList = document.getElementById('liveopsTimelineList');
    tlList.innerHTML = (data.event_timeline || []).map(item => `
      <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start justify-between gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-white">${item.version}</span>
            <span class="text-[10px] text-slate-400">(${item.date})</span>
            <span class="text-[10px] px-2 py-0.5 rounded font-semibold bg-indigo-500/20 text-indigo-400">${item.type}</span>
          </div>
          <p class="text-[11px] text-slate-300 mt-1">${item.highlight}</p>
        </div>
        <span class="text-[10px] font-bold px-2 py-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 whitespace-nowrap">${item.revenue_spike}</span>
      </div>
    `).join('');

    document.getElementById('liveopsTacticalAdvice').innerText = data.studio_tactical_takeaway || '--';

    lucide.createIcons();
  } catch (err) {
    console.error("Error loading LiveOps data:", err);
  }
}

// --- GAME INTELLIGENCE MODAL ---
async function openGameModal(gameId) {
  currentActiveModalGameId = gameId;
  const modal = document.getElementById('gameDetailModal');
  modal.classList.remove('hidden');

  document.getElementById('modalAiResultCard').classList.add('hidden');

  try {
    const res = await fetch(`/api/game/${encodeURIComponent(gameId)}`);
    const data = await res.json();
    if (data.error) {
      showToast('Không tìm thấy thông tin tựa game này.');
      closeGameModal();
      return;
    }

    const g = data.game;
    const stats = data.stats || {};
    const history = data.history || [];

    currentActiveModalGame = g;
    currentActiveModalGameTitle = g.title || '';
    currentActiveModalGamePlatform = g.platform || 'mobile';
    currentActiveModalGameGenre = g.genre || 'Action';
    currentActiveModalGameStoreUrl = g.store_url || '';
    currentActiveModalGameDesc = g.description || '';
    currentActiveModalHistory = history;
    switchModalSubTab('deconstruct');

    document.getElementById('modalGameTitle').innerText = g.title;
    document.getElementById('modalGameDeveloper').innerText = `Studio: ${g.developer || 'N/A'}`;
    document.getElementById('modalGameIcon').src = g.icon_url || 'https://placehold.co/80x80/1e293b/white?text=Game';
    document.getElementById('modalGameGenre').innerText = g.genre || 'Game';
    document.getElementById('modalGamePrice').innerText = g.price || 'Free';
    document.getElementById('modalGameScore').innerText = `⭐ ${g.score || '4.5'}`;
    document.getElementById('modalGameStoreLink').href = g.store_url || '#';

    isCurrentModalInWatchlist = !!g.is_in_watchlist;
    updateModalWatchlistButton(isCurrentModalInWatchlist);

    const isPC = (g.platform || '').includes('pc');
    const badge = document.getElementById('modalGamePlatformBadge');
    badge.innerText = isPC ? 'PC Steam' : 'Mobile Store';
    badge.className = isPC 
      ? 'text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400'
      : 'text-[10px] font-semibold px-2 py-0.5 rounded-full bg-pink-500/20 text-pink-400';

    document.getElementById('modalStatCurrentRank').innerText = `#${g.rank}`;
    document.getElementById('modalStatBestRank').innerText = `#${stats.best_rank || g.rank}`;
    document.getElementById('modalStatAvgRank').innerText = `#${stats.avg_rank || g.rank}`;
    document.getElementById('modalStatPeakCCU').innerText = isPC 
      ? `${(stats.peak_ccu || g.player_count || 0).toLocaleString()} CCU`
      : (g.estimated_downloads || 'Top Tier');

    if (document.getElementById('modalStatRevDaily')) document.getElementById('modalStatRevDaily').innerText = g.estimated_revenue_daily_formatted || 'N/A';
    if (document.getElementById('modalStatRevMonthly')) document.getElementById('modalStatRevMonthly').innerText = g.estimated_revenue_monthly_formatted || 'N/A';
    if (document.getElementById('modalStatDownloads')) document.getElementById('modalStatDownloads').innerText = g.estimated_downloads_formatted || g.estimated_downloads || 'N/A';

    // Preload estimated revenue history
    loadGameRevenueHistory(gameId, sensorChartDays || 30);

    renderModalTrendChart(history, isPC);

    const tbody = document.getElementById('modalHistoryTableBody');
    tbody.innerHTML = history.slice().reverse().map(h => {
      let delta = '<span class="text-slate-500">-</span>';
      if (h.rank_change_day > 0) delta = `<span class="text-emerald-400 font-bold">+${h.rank_change_day}</span>`;
      else if (h.rank_change_day < 0) delta = `<span class="text-rose-400 font-bold">${h.rank_change_day}</span>`;

      return `
        <tr>
          <td class="py-2 px-3 text-slate-300 font-medium">${h.snapshot_date}</td>
          <td class="py-2 px-3 font-bold text-indigo-400">#${h.rank}</td>
          <td class="py-2 px-3 text-slate-300">${isPC ? (h.player_count || 0).toLocaleString() : '--'}</td>
          <td class="py-2 px-3">${delta}</td>
        </tr>
      `;
    }).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error opening game modal:", err);
  }
}

function closeGameModal() {
  document.getElementById('gameDetailModal').classList.add('hidden');
  if (typeof pausePrototypeGame === 'function') {
    pausePrototypeGame();
  }
}

function toggleAiCard() {
  document.getElementById('modalAiResultCard').classList.toggle('hidden');
}

// Request AI Deconstruction
async function requestAiDeconstruct() {
  if (!currentActiveModalGameId) return;

  const btn = document.getElementById('btnAiDeconstruct');
  const card = document.getElementById('modalAiResultCard');
  const content = document.getElementById('modalAiContent');
  const badge = document.getElementById('modalAiSourceBadge');

  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin text-amber-300"></i><span>AI Đang Phân Tích & Bóc Tách Gameplay...</span>';
  lucide.createIcons();

  card.classList.remove('hidden');
  content.innerHTML = `
    <div class="py-8 text-center space-y-3">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
      <p class="text-xs text-purple-300">Đang quét cơ chế cốt lõi, mô hình kiếm tiền và chân dung người chơi...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/ai/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: currentActiveModalGameId })
    });
    const data = await res.json();
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="sparkles" class="w-4 h-4 text-amber-300"></i><span>🤖 Bóc Tách & Phân Tích Chuyên Sâu Bằng AI (AI Game Deconstruct)</span>';

    if (data.error) {
      content.innerHTML = `<p class="text-rose-400">${data.error}</p>`;
      return;
    }

    badge.innerText = data.source === 'gemini' ? `✨ Nguồn: Google ${data.model || 'Gemini'}` : '⚡ Nguồn: Hệ tri thức nội bộ (không dùng LLM)';
    const a = data.analysis;

    content.innerHTML = `
      <div class="p-3.5 rounded-xl bg-purple-950/30 border border-purple-500/20">
        <h5 class="font-bold text-purple-300 flex items-center gap-1.5 mb-1">
          <i data-lucide="repeat" class="w-3.5 h-3.5"></i> 1. Vòng Lặp Trải Nghiệm Cốt Lõi (Core Gameplay Loop & Retention)
        </h5>
        <p class="text-slate-300 leading-relaxed">${a.core_loop || 'N/A'}</p>
      </div>

      <div class="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/20">
        <h5 class="font-bold text-emerald-300 flex items-center gap-1.5 mb-1">
          <i data-lucide="credit-card" class="w-3.5 h-3.5"></i> 2. Kiến Trúc Kiếm Tiền (Monetization Architecture)
        </h5>
        <p class="text-slate-300 leading-relaxed">${a.monetization || 'N/A'}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="p-3.5 rounded-xl bg-sky-950/30 border border-sky-500/20">
          <h5 class="font-bold text-sky-300 flex items-center gap-1.5 mb-1">
            <i data-lucide="users" class="w-3.5 h-3.5"></i> 3. Chân Dung Người Chơi (Target Audience)
          </h5>
          <p class="text-slate-300 leading-relaxed">${a.player_persona || 'N/A'}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/20">
          <h5 class="font-bold text-amber-300 flex items-center gap-1.5 mb-1">
            <i data-lucide="zap" class="w-3.5 h-3.5"></i> 4. Lợi Thế Cạnh Tranh (Competitive Edge)
          </h5>
          <p class="text-slate-300 leading-relaxed">${a.competitive_edge || 'N/A'}</p>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-indigo-950/30 border border-indigo-500/20">
        <h5 class="font-bold text-indigo-300 flex items-center gap-1.5 mb-1">
          <i data-lucide="lightbulb" class="w-3.5 h-3.5"></i> 5. Bài Học Đắt Giá Cho Game Dev / Studio Việt Nam
        </h5>
        <div class="text-slate-300 whitespace-pre-line leading-relaxed font-mono text-[11px]">${a.actionable_takeaways || 'N/A'}</div>
      </div>
    `;
    lucide.createIcons();
  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="sparkles" class="w-4 h-4 text-amber-300"></i><span>🤖 Phân Tích Chuyên Sâu Bằng AI (AI Game Deconstruct)</span>';
    content.innerHTML = '<p class="text-rose-400">Lỗi khi gọi phân tích AI.</p>';
  }
}

// --- ESTIMATED REVENUE HISTORY (rank-based model) ---
let currentSensorRevenueHistoryData = null;
let sensorChartMode = 'daily'; // 'daily' or 'cumulative'
let sensorChartDays = 30;
let sensorTowerChartInstance = null;
let currentUnityImporterScriptText = '';

async function loadModalUnityPlugin() {
  const codeDisplay = document.getElementById('unityImporterCodeDisplay');
  if (!codeDisplay) return;
  if (currentUnityImporterScriptText) {
    codeDisplay.textContent = currentUnityImporterScriptText;
    return;
  }
  codeDisplay.textContent = '// Đang tải mã nguồn GameRadarImporter.cs từ máy chủ...';
  try {
    const res = await fetch('/api/unity/importer-script');
    if (!res.ok) throw new Error('Không thể tải script');
    const text = await res.text();
    currentUnityImporterScriptText = text;
    codeDisplay.textContent = text;
  } catch (err) {
    console.error('Error loading Unity importer script:', err);
    codeDisplay.textContent = '// Lỗi khi kết nối API tải GameRadarImporter.cs. Vui lòng thử lại sau.';
  }
}

function copyUnityImporterCode() {
  const codeDisplay = document.getElementById('unityImporterCodeDisplay');
  const code = (codeDisplay && codeDisplay.textContent) ? codeDisplay.textContent : currentUnityImporterScriptText;
  if (!code || code.startsWith('// Lỗi') || code.startsWith('// Đang')) {
    showToast('Chưa tải được mã nguồn script.');
    return;
  }
  navigator.clipboard.writeText(code).then(() => {
    showToast('Đã sao chép mã nguồn GameRadarImporter.cs vào clipboard!');
  }).catch(() => {
    showToast('Không thể truy cập clipboard.');
  });
}

async function loadGameRevenueHistory(gameId, days = 30) {
  if (!gameId) return;
  sensorChartDays = days;
  const loadingEl = document.getElementById('sensorRevenueLoading');
  if (loadingEl) loadingEl.classList.remove('hidden');

  try {
    const res = await fetch(`/api/game/${encodeURIComponent(gameId)}/revenue-history?days=${days}`);
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    currentSensorRevenueHistoryData = data;
    renderSensorTowerDashboard(data);
  } catch (err) {
    console.error('Error loading revenue history:', err);
  } finally {
    if (loadingEl) loadingEl.classList.add('hidden');
  }
}

function setSensorChartMode(mode) {
  sensorChartMode = mode;
  const btnDaily = document.getElementById('btnSensorModeDaily');
  const btnCum = document.getElementById('btnSensorModeCumulative');
  if (btnDaily && btnCum) {
    if (mode === 'daily') {
      btnDaily.className = 'px-2.5 py-1 rounded-lg font-bold bg-emerald-600 text-white transition-all cursor-pointer';
      btnCum.className = 'px-2.5 py-1 rounded-lg font-medium text-slate-400 hover:text-white transition-all cursor-pointer';
    } else {
      btnCum.className = 'px-2.5 py-1 rounded-lg font-bold bg-emerald-600 text-white transition-all cursor-pointer';
      btnDaily.className = 'px-2.5 py-1 rounded-lg font-medium text-slate-400 hover:text-white transition-all cursor-pointer';
    }
  }
  if (currentSensorRevenueHistoryData) {
    renderSensorTowerChart(currentSensorRevenueHistoryData);
  }
}

function changeSensorDays(days) {
  sensorChartDays = days;
  [7, 14, 30].forEach(d => {
    const btn = document.getElementById(`btnSensorDays${d}`);
    if (!btn) return;
    if (d === days) {
      btn.className = 'px-2 py-1 rounded-lg font-bold bg-slate-800 text-emerald-400 border border-emerald-500/30 transition-all cursor-pointer';
    } else {
      btn.className = 'px-2 py-1 rounded-lg font-medium text-slate-400 hover:text-white transition-all cursor-pointer';
    }
  });
  if (currentActiveModalGameId) {
    loadGameRevenueHistory(currentActiveModalGameId, days);
  }
}

function renderSensorTowerDashboard(data) {
  if (!data) return;
  const s = data.metrics_summary || {};
  const l = data.lifecycle || {};
  const t = data.tier_breakdown || {};

  // Metrics
  const elRev30d = document.getElementById('sensorRev30d');
  if (elRev30d) elRev30d.innerText = s.total_revenue_formatted || '--';
  const elRevAvg = document.getElementById('sensorRevDailyAvg');
  if (elRevAvg) elRevAvg.innerText = s.average_daily_revenue_formatted || '--';
  const elDl30d = document.getElementById('sensorDl30d');
  if (elDl30d) elDl30d.innerText = s.total_downloads_formatted || '--';
  const elDlAvg = document.getElementById('sensorDlDailyAvg');
  if (elDlAvg) elDlAvg.innerText = s.average_daily_downloads_formatted || '--';
  const elArpu = document.getElementById('sensorArpu');
  if (elArpu) elArpu.innerText = s.blended_arpu_formatted ? `${s.blended_arpu_formatted} / tải` : '--';
  const elScore = document.getElementById('sensorMonetizationScore');
  if (elScore) elScore.innerText = `${s.monetization_score || 75}/100`;

  // WoW Growth Badge
  const dq = data.data_quality || {};
  const elNote = document.getElementById('sensorDataQualityNote');
  if (elNote && dq.note) elNote.innerText = `⚠️ ${dq.note} (Độ phủ dữ liệu thật: ${dq.coverage_pct}%)`;

  const elGrowth = document.getElementById('sensorRevGrowthBadge');
  if (elGrowth && dq.has_reliable_wow === false) {
    elGrowth.innerText = 'WoW: chưa đủ dữ liệu';
    elGrowth.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-500/10 text-slate-400 border border-slate-500/20';
  } else if (elGrowth) {
    const wow = s.wow_growth_pct || 0;
    const sign = wow >= 0 ? '+' : '';
    elGrowth.innerText = `${sign}${wow}% WoW`;
    if (wow >= 0) {
      elGrowth.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
    } else {
      elGrowth.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20';
    }
  }

  // Lifecycle
  const elLifeBadge = document.getElementById('sensorLifecycleBadge');
  if (elLifeBadge) elLifeBadge.innerText = l.phase || 'Bình thường';
  const elLifeDesc = document.getElementById('sensorLifecycleDesc');
  if (elLifeDesc) elLifeDesc.innerText = l.description || '';

  // Country Tiers
  if (t.tier_1) {
    const t1 = t.tier_1;
    const el = document.getElementById('sensorTier1Rev');
    if (el) el.innerText = t1.revenue_formatted;
    const elDl = document.getElementById('sensorTier1Dl');
    if (elDl) elDl.innerText = t1.downloads_formatted;
    const elArpu = document.getElementById('sensorTier1Arpu');
    if (elArpu) elArpu.innerText = `$${t1.arpu}`;
    const elShare = document.getElementById('sensorTier1Share');
    if (elShare) elShare.innerText = `${t1.share_pct}%`;
  }
  if (t.tier_2) {
    const t2 = t.tier_2;
    const el = document.getElementById('sensorTier2Rev');
    if (el) el.innerText = t2.revenue_formatted;
    const elDl = document.getElementById('sensorTier2Dl');
    if (elDl) elDl.innerText = t2.downloads_formatted;
    const elArpu = document.getElementById('sensorTier2Arpu');
    if (elArpu) elArpu.innerText = `$${t2.arpu}`;
    const elShare = document.getElementById('sensorTier2Share');
    if (elShare) elShare.innerText = `${t2.share_pct}%`;
  }
  if (t.tier_3) {
    const t3 = t.tier_3;
    const el = document.getElementById('sensorTier3Rev');
    if (el) el.innerText = t3.revenue_formatted;
    const elDl = document.getElementById('sensorTier3Dl');
    if (elDl) elDl.innerText = t3.downloads_formatted;
    const elArpu = document.getElementById('sensorTier3Arpu');
    if (elArpu) elArpu.innerText = `$${t3.arpu}`;
    const elShare = document.getElementById('sensorTier3Share');
    if (elShare) elShare.innerText = `${t3.share_pct}%`;
  }

  // Chart
  renderSensorTowerChart(data);
  lucide.createIcons();
}

function renderSensorTowerChart(data) {
  const canvas = document.getElementById('sensorTowerRevenueChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (sensorTowerChartInstance) sensorTowerChartInstance.destroy();

  const timeline = data.timeline || [];
  const labels = timeline.map(d => d.display_date);

  let revData, dlData, revLabel, dlLabel;
  if (sensorChartMode === 'cumulative') {
    revData = timeline.map(d => d.cumulative_revenue);
    dlData = timeline.map(d => d.cumulative_downloads);
    revLabel = 'Doanh Thu Lũy Kế ($)';
    dlLabel = 'Lượt Tải Lũy Kế';
  } else {
    revData = timeline.map(d => d.daily_revenue);
    dlData = timeline.map(d => d.daily_downloads);
    revLabel = 'Doanh Thu Ngày ($)';
    dlLabel = 'Lượt Tải Ngày';
  }

  sensorTowerChartInstance = new Chart(ctx, {
    data: {
      labels: labels,
      datasets: [
        {
          type: 'line',
          label: revLabel,
          data: revData,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          borderWidth: 2.5,
          fill: true,
          tension: 0.35,
          pointRadius: timeline.map(d => d.is_estimated ? 0 : (timeline.length > 20 ? 3 : 4)),
          pointHoverRadius: 6,
          segment: {
            borderDash: c => (timeline[c.p0DataIndex]?.is_estimated || timeline[c.p1DataIndex]?.is_estimated) ? [5, 4] : undefined
          },
          yAxisID: 'yRev'
        },
        {
          type: sensorChartMode === 'cumulative' ? 'line' : 'bar',
          label: dlLabel,
          data: dlData,
          borderColor: '#06b6d4',
          backgroundColor: sensorChartMode === 'cumulative' ? 'rgba(6, 182, 212, 0.1)' : timeline.map(d => d.is_estimated ? 'rgba(6, 182, 212, 0.12)' : 'rgba(6, 182, 212, 0.4)'),
          borderWidth: sensorChartMode === 'cumulative' ? 2 : 1,
          borderRadius: 4,
          fill: sensorChartMode === 'cumulative',
          tension: 0.35,
          pointRadius: sensorChartMode === 'cumulative' ? 2 : 0,
          yAxisID: 'yDl'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: { color: '#94a3b8', font: { size: 10 } }
        },
        yRev: {
          type: 'linear',
          position: 'left',
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#10b981',
            font: { size: 10 },
            callback: function(val) {
              if (val >= 1000000) return '$' + (val / 1000000).toFixed(1) + 'M';
              if (val >= 1000) return '$' + (val / 1000).toFixed(0) + 'K';
              return '$' + val;
            }
          }
        },
        yDl: {
          type: 'linear',
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: {
            color: '#06b6d4',
            font: { size: 10 },
            callback: function(val) {
              if (val >= 1000000) return (val / 1000000).toFixed(1) + 'M';
              if (val >= 1000) return (val / 1000).toFixed(0) + 'K';
              return val;
            }
          }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#cbd5e1', font: { size: 11, weight: 'bold' } }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || '';
              const val = context.parsed.y;
              if (context.dataset.yAxisID === 'yRev') {
                return ` ${label}: $${val.toLocaleString()}`;
              }
              return ` ${label}: ${val.toLocaleString()} lượt`;
            },
            footer: function(items) {
              const d = timeline[items[0]?.dataIndex];
              if (!d) return '';
              const src = {snapshot: 'Thứ hạng crawl thật', interpolated: 'Nội suy giữa 2 lần crawl', carried: 'Giữ thứ hạng gần nhất', assumed: 'Chưa có dữ liệu crawl'}[d.data_source] || d.data_source;
              return `Rank #${d.rank} · ${src}`;
            }
          }
        }
      }
    }
  });
}

function renderModalTrendChart(history, isPC) {
  const ctx = document.getElementById('gameModalChart').getContext('2d');
  if (modalChartInstance) modalChartInstance.destroy();

  const labels = history.map(h => h.snapshot_date);
  const rankData = history.map(h => h.rank);
  const ccuData = history.map(h => h.player_count || 0);

  const datasets = [{
    label: 'Thứ Hạng (Rank)',
    data: rankData,
    borderColor: '#6366f1',
    backgroundColor: 'rgba(99, 102, 241, 0.15)',
    borderWidth: 2.5,
    fill: true,
    tension: 0.35,
    yAxisID: 'y'
  }];

  if (isPC && Math.max(...ccuData) > 0) {
    datasets.push({
      label: 'Người chơi (CCU)',
      data: ccuData,
      borderColor: '#10b981',
      borderDash: [5, 5],
      borderWidth: 2,
      tension: 0.35,
      yAxisID: 'y1'
    });
  }

  modalChartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
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
          type: 'linear',
          display: true,
          position: 'left',
          reverse: true,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#6366f1', font: { size: 10 } }
        },
        y1: {
          type: 'linear',
          display: isPC && Math.max(...ccuData) > 0,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#10b981', font: { size: 10 } }
        }
      },
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { size: 11 } } }
      }
    }
  });
}
