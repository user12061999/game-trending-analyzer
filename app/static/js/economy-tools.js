/* ASO lab, IAP, LiveOps, UA pacing, gacha, publisher, culturalization, churn, K-factor */
// ==========================================
// MODULE: ASO VISUAL OPTIMIZER & CVR LAB
// ==========================================
async function loadAsoVisualLab() {
  const grid = document.getElementById('asoArchetypesGrid');
  grid.innerHTML = '<div class="col-span-full py-6 text-center text-slate-400">Đang tải các trường phái thiết kế Icon...</div>';

  try {
    const res = await fetch('/api/mobile/aso/visual-archetypes');
    const data = await res.json();
    const items = data.archetypes || [];

    grid.innerHTML = items.map(a => `
      <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-3 flex flex-col justify-between hover:border-pink-500/40 transition-all">
        <div class="space-y-2">
          <div class="flex items-start justify-between gap-1">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-pink-500/20 text-pink-400 border border-pink-500/30">${a.cvr_lift} CVR</span>
            <span class="text-[10px] text-slate-400 font-mono">Avg ${a.avg_cvr}%</span>
          </div>
          <h4 class="text-xs font-bold text-white leading-tight">${a.name}</h4>
          <p class="text-[11px] text-slate-300 leading-snug">${a.psychology}</p>
          
          <div class="space-y-1 text-[10px] text-slate-400">
            <div><strong class="text-slate-300">Thể loại tốt nhất:</strong> ${(a.best_genres || []).slice(0, 3).join(', ')}</div>
            <div><strong class="text-slate-300">Tone màu:</strong> ${(a.color_palette || []).slice(0, 2).join(', ')}</div>
          </div>
        </div>

        <div class="pt-2 border-t border-slate-800 text-[10px] text-pink-300">
          💡 ${a.dos_and_donts.dos[0] || ''}
        </div>
      </div>
    `).join('');

    onAsoInputChanged();
    runAsoAudit();
    lucide.createIcons();
  } catch (err) {
    console.error("Error loading ASO visual archetypes:", err);
  }
}

function updateAsoCharLimits() {
  const store = document.getElementById('asoAuditStore').value;
  const subLabel = document.getElementById('asoSubtitleLabel');
  if (store === 'app_store') {
    subLabel.innerText = "Phụ Đề (Subtitle - Tối đa 30 ký tự)";
  } else {
    subLabel.innerText = "Mô Tả Ngắn (Short Description - Tối đa 80 ký tự)";
  }
  onAsoInputChanged();
}

function onAsoInputChanged() {
  const store = document.getElementById('asoAuditStore').value;
  const title = document.getElementById('asoAuditTitle').value || '';
  const subtitle = document.getElementById('asoAuditSubtitle').value || '';
  const titleLimit = 30;
  const subtitleLimit = store === 'app_store' ? 30 : 80;

  const titleCountElem = document.getElementById('asoTitleCount');
  const subtitleCountElem = document.getElementById('asoSubtitleCount');

  titleCountElem.innerText = `${title.length} / ${titleLimit}`;
  titleCountElem.className = title.length > titleLimit ? "text-[11px] font-mono text-rose-400 font-bold" : "text-[11px] font-mono text-slate-400";

  subtitleCountElem.innerText = `${subtitle.length} / ${subtitleLimit}`;
  subtitleCountElem.className = subtitle.length > subtitleLimit ? "text-[11px] font-mono text-rose-400 font-bold" : "text-[11px] font-mono text-slate-400";
}

async function runAsoAudit() {
  const title = document.getElementById('asoAuditTitle').value;
  const subtitle = document.getElementById('asoAuditSubtitle').value;
  const keywords = document.getElementById('asoAuditKeywords').value;
  const genre = document.getElementById('asoAuditGenre').value;
  const icon_style = document.getElementById('asoAuditIconStyle').value;
  const target_store = document.getElementById('asoAuditStore').value;

  try {
    const res = await fetch('/api/mobile/aso/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        subtitle: subtitle,
        keywords: keywords,
        genre: genre,
        icon_archetype_id: icon_style,
        target_store: target_store
      })
    });

    const data = await res.json();

    // Update scores
    document.getElementById('asoEstimatedCvr').innerText = `${data.estimated_cvr}%`;
    document.getElementById('asoHealthScore').innerText = `${data.overall_score} / 100`;

    const gradeBadge = document.getElementById('asoHealthGradeBadge');
    gradeBadge.innerText = data.health_grade;
    if (data.badge_color === 'emerald') {
      gradeBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    } else if (data.badge_color === 'indigo') {
      gradeBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30";
    } else if (data.badge_color === 'amber') {
      gradeBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-amber-500/20 text-amber-400 border border-amber-500/30";
    } else {
      gradeBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-rose-500/20 text-rose-400 border border-rose-500/30";
    }

    // Render matched keywords
    const kwList = document.getElementById('asoMatchedKeywordsList');
    document.getElementById('asoKwCount').innerText = `${data.matched_keywords.length} từ khóa`;
    if (data.matched_keywords.length === 0) {
      kwList.innerHTML = '<div class="text-[11px] text-slate-500 py-2">Không phát hiện từ khóa gaming phổ biến trong listing.</div>';
    } else {
      kwList.innerHTML = data.matched_keywords.map(kw => `
        <div class="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800 text-xs">
          <div class="flex items-center gap-2">
            <span class="font-bold text-pink-400 capitalize">${kw.keyword}</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">${kw.found_in}</span>
          </div>
          <div class="flex items-center gap-3 text-[11px] font-mono">
            <span class="text-emerald-400">Vol: ${kw.volume}</span>
            <span class="text-amber-400">Diff: ${kw.difficulty}</span>
          </div>
        </div>
      `).join('');
    }

    // Render recommendations
    const recList = document.getElementById('asoRecommendationsList');
    recList.innerHTML = data.recommendations.map(r => `
      <div class="flex items-start gap-2 p-1.5 rounded bg-slate-900/60 border border-slate-800/80">
        <i data-lucide="arrow-right-circle" class="w-3.5 h-3.5 text-pink-400 shrink-0 mt-0.5"></i>
        <span>${r}</span>
      </div>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error running ASO audit:", err);
  }
}

// ==========================================
// MODULE: IAP MONETIZATION & PRICING MATRIX
// ==========================================
let cachedIapBenchmarks = null;

async function initIapMatrixTab() {
  try {
    const res = await fetch('/api/mobile/iap/benchmarks');
    cachedIapBenchmarks = await res.json();

    // Render default genre ladder
    selectIapGenre('midcore_rpg');

    // Render PPP table
    const pppBody = document.getElementById('iapPppTableBody');
    pppBody.innerHTML = (cachedIapBenchmarks.ppp_matrix || []).map(p => `
      <tr class="hover:bg-slate-900/60 transition-colors">
        <td class="px-4 py-3 font-semibold text-white">${p.region}</td>
        <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${p.tier === 'Tier 1' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'}">${p.tier}</span></td>
        <td class="px-4 py-3 text-emerald-400 font-bold">${p.starter_local}</td>
        <td class="px-4 py-3 text-amber-400 font-bold">${p.pass_local}</td>
        <td class="px-4 py-3 text-purple-400 font-bold">${p.whale_local}</td>
        <td class="px-4 py-3 text-slate-300 font-sans">${p.cvr_impact}</td>
      </tr>
    `).join('');

    runIapSimulation();
    lucide.createIcons();
  } catch (err) {
    console.error("Error initializing IAP matrix tab:", err);
  }
}

function selectIapGenre(genreKey) {
  if (!cachedIapBenchmarks || !cachedIapBenchmarks.genres) return;
  const genres = ['midcore_rpg', 'hybrid_casual', 'strategy_4x', 'gacha_anime', 'casual_match3'];
  genres.forEach(g => {
    const btn = document.getElementById(`iapGenreBtn-${g}`);
    if (!btn) return;
    if (g === genreKey) {
      btn.className = "px-3 py-1.5 rounded-lg bg-amber-600 text-white font-semibold cursor-pointer";
    } else {
      btn.className = "px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 cursor-pointer";
    }
  });

  const gData = cachedIapBenchmarks.genres[genreKey];
  if (!gData) return;

  const display = document.getElementById('iapLadderDisplay');
  display.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-950 border border-amber-500/20">
      <div>
        <span class="text-xs text-slate-400">Thể Loại</span>
        <div class="text-sm font-bold text-white mt-0.5">${gData.genre_name}</div>
      </div>
      <div>
        <span class="text-xs text-slate-400">Cơ Cấu Doanh Thu</span>
        <div class="text-sm font-bold text-amber-400 mt-0.5">${gData.ad_vs_iap_split.iap_share}% IAP / ${gData.ad_vs_iap_split.ad_share}% Ads</div>
      </div>
      <div>
        <span class="text-xs text-slate-400">Tỷ Lệ Trả Tiền Chuẩn</span>
        <div class="text-sm font-bold text-emerald-400 mt-0.5">~${gData.median_paying_conversion}% Paying DAU</div>
      </div>
      <div>
        <span class="text-xs text-slate-400">Trần Chi Tiêu Của Whale</span>
        <div class="text-sm font-bold text-purple-400 mt-0.5">${gData.whale_cap}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      ${gData.price_ladder.map(tier => `
        <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 hover:border-amber-500/40 transition-colors">
          <div class="flex items-center justify-between">
            <span class="font-bold text-white text-xs">${tier.tier}</span>
            <span class="px-2 py-0.5 rounded text-xs font-black bg-amber-500/20 text-amber-400 border border-amber-500/30 font-mono">$${tier.price_usd}</span>
          </div>
          <p class="text-[11px] text-slate-300 leading-snug">${tier.description}</p>
          <div class="text-[10px] text-slate-400 pt-1 border-t border-slate-800/80 flex items-center justify-between">
            <span>Tỷ trọng đơn hàng:</span>
            <strong class="text-amber-300 font-mono">${tier.conversion_share}</strong>
          </div>
        </div>
      `).join('')}
    </div>

    <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-2 flex-wrap text-xs">
      <span class="text-slate-400 font-semibold">Cơ chế monetization khuyến nghị:</span>
      ${(gData.recommended_mechanics || []).map(m => `<span class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[11px]">${m}</span>`).join('')}
    </div>
  `;

  // Sync simulator genre dropdown
  const simGenreSelect = document.getElementById('iapSimGenre');
  if (simGenreSelect) simGenreSelect.value = genreKey;
  lucide.createIcons();
}

async function runIapSimulation() {
  const dau = document.getElementById('iapSimDau').value;
  const genre = document.getElementById('iapSimGenre').value;
  const region = document.getElementById('iapSimRegion').value;
  const bpPrice = document.getElementById('iapSimBpPrice').value;
  const cardPrice = document.getElementById('iapSimCardPrice').value;

  try {
    const res = await fetch('/api/mobile/iap/simulate-economy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dau: parseInt(dau) || 50000,
        genre_key: genre,
        region_tier: region,
        battle_pass_price: parseFloat(bpPrice) || 9.99,
        monthly_card_price: parseFloat(cardPrice) || 4.99
      })
    });

    const data = await res.json();
    const fin = data.financial_summary;
    const sp = data.spender_distribution;

    // Populate Financial KPIs
    document.getElementById('iapResTotalGross').innerText = `$${Math.round(fin.total_monthly_gross_usd).toLocaleString()}`;
    document.getElementById('iapResIap').innerText = `$${Math.round(fin.monthly_iap_usd).toLocaleString()}`;
    document.getElementById('iapResAds').innerText = `$${Math.round(fin.monthly_ad_usd).toLocaleString()}`;
    document.getElementById('iapResArppu').innerText = `$${fin.monthly_arppu_usd}`;
    document.getElementById('iapResArpdau').innerText = `ARPDAU: $${fin.daily_arpdau_usd}`;
    document.getElementById('iapResConversion').innerText = `${fin.payer_conversion_rate}%`;
    document.getElementById('iapResGrossSplit').innerText = `${data.revenue_split.iap_pct}% IAP / ${data.revenue_split.ad_pct}% Ads`;

    // Render Spender Cards
    const container = document.getElementById('iapSpenderCardsContainer');
    container.innerHTML = `
      <!-- Whales -->
      <div class="glass-card p-4 rounded-xl border border-purple-500/30 bg-purple-950/10 space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-purple-300 flex items-center gap-1">🐋 Whales (Cá Voi)</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 font-mono">${sp.whales.count.toLocaleString()} user</span>
        </div>
        <div class="text-xl font-black text-white font-mono">$${Math.round(sp.whales.total_revenue).toLocaleString()}</div>
        <div class="text-[11px] text-purple-300/80">Chiếm <strong>${sp.whales.revenue_contribution_pct}%</strong> tổng doanh thu IAP</div>
        <div class="text-[10px] text-slate-400">Chi tiêu trung bình: <strong class="text-slate-200 font-mono">$${sp.whales.avg_monthly_spend}/tháng</strong></div>
      </div>

      <!-- Dolphins -->
      <div class="glass-card p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/10 space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-indigo-300 flex items-center gap-1">🐬 Dolphins (Cá Heo)</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 font-mono">${sp.dolphins.count.toLocaleString()} user</span>
        </div>
        <div class="text-xl font-black text-white font-mono">$${Math.round(sp.dolphins.total_revenue).toLocaleString()}</div>
        <div class="text-[11px] text-indigo-300/80">Chiếm <strong>${sp.dolphins.revenue_contribution_pct}%</strong> tổng doanh thu IAP</div>
        <div class="text-[10px] text-slate-400">Mua Battle Pass + Thẻ tháng: <strong class="text-slate-200 font-mono">$${sp.dolphins.avg_monthly_spend}/tháng</strong></div>
      </div>

      <!-- Minnows -->
      <div class="glass-card p-4 rounded-xl border border-sky-500/30 bg-sky-950/10 space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-sky-300 flex items-center gap-1">🐟 Minnows (Cá Con)</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-500/20 text-sky-300 font-mono">${sp.minnows.count.toLocaleString()} user</span>
        </div>
        <div class="text-xl font-black text-white font-mono">$${Math.round(sp.minnows.total_revenue).toLocaleString()}</div>
        <div class="text-[11px] text-sky-300/80">Chiếm <strong>${sp.minnows.revenue_contribution_pct}%</strong> tổng doanh thu IAP</div>
        <div class="text-[10px] text-slate-400">Mua gói $0.99 mồi: <strong class="text-slate-200 font-mono">$${sp.minnows.avg_monthly_spend}/tháng</strong></div>
      </div>

      <!-- F2P Non-payers -->
      <div class="glass-card p-4 rounded-xl border border-slate-700 bg-slate-900/60 space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-slate-300 flex items-center gap-1">👥 F2P (Miễn Phí)</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 font-mono">${sp.f2p_users.pct_of_dau}% DAU</span>
        </div>
        <div class="text-xl font-black text-white font-mono">$${Math.round(sp.f2p_users.ad_value_generated).toLocaleString()}</div>
        <div class="text-[11px] text-slate-400">Đóng góp qua quảng cáo Ads</div>
        <div class="text-[10px] text-slate-500">Giữ chân cộng đồng & thanh khoản matchmaking</div>
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error running IAP simulation:", err);
  }
}

// ==========================================
// MODULE: LIVEOPS CALENDAR & CLASH RADAR
// ==========================================
async function initLiveOpsRadarTab() {
  // Set default start date to next Thursday
  const today = new Date();
  today.setDate(today.getDate() + ((4 + 7 - today.getDay()) % 7 || 7));
  const formattedDate = today.toISOString().split('T')[0];
  const dateInput = document.getElementById('liveopsStartDate');
  if (dateInput && !dateInput.value) dateInput.value = formattedDate;

  try {
    const res = await fetch('/api/mobile/liveops/clash-radar');
    const data = await res.json();

    // Render Competitor Clash Windows
    const clashContainer = document.getElementById('liveopsClashTimeline');
    clashContainer.innerHTML = (data.radar.upcoming_clash_windows || []).map(w => `
      <div class="glass-card p-4 rounded-xl border ${w.risk_level === 'High' ? 'border-rose-500/40 bg-rose-950/10' : 'border-amber-500/30 bg-amber-950/10'} space-y-2.5">
        <div class="flex items-center justify-between">
          <span class="font-bold text-white text-xs">${w.publisher}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${w.risk_level === 'High' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">
            Rủi ro: ${w.risk_level}
          </span>
        </div>
        <div class="text-[11px] text-slate-300 font-semibold">Tựa game: ${(w.titles || []).join(', ')}</div>
        <div class="flex items-center gap-2 text-[11px] font-mono">
          <span class="text-cyan-400 font-bold">${w.estimated_patch_date} (${w.weekday})</span>
        </div>
        <div class="p-2 rounded bg-slate-950 text-[10px] text-slate-300 border border-slate-800">
          ⚡ <strong>Tác động CPI:</strong> ${w.auction_impact}
        </div>
        <p class="text-[10px] text-slate-400 leading-snug">${w.advisory}</p>
      </div>
    `).join('');

    // Render LiveOps Templates
    const templatesContainer = document.getElementById('liveopsTemplatesGrid');
    templatesContainer.innerHTML = (data.templates || []).map(t => `
      <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-3 flex flex-col justify-between hover:border-cyan-500/40 transition-colors">
        <div class="space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="px-2 py-0.5 rounded text-xs font-black bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-mono">${t.revenue_lift} Rev</span>
            <span class="text-[10px] text-slate-400">${t.cadence}</span>
          </div>
          <h4 class="text-xs font-bold text-white">${t.name}</h4>
          <p class="text-[11px] text-slate-300 leading-snug">${t.monetization_impact}</p>
          <div class="text-[10px] text-cyan-300/80">📈 <strong>Dạng sóng:</strong> ${t.revenue_curve}</div>
        </div>
        <div class="pt-2 border-t border-slate-800 text-[10px] text-slate-400 flex items-center justify-between">
          <span>Ngày tối ưu: <strong class="text-slate-200">${t.recommended_day}</strong></span>
          <button onclick="prefillLiveOpsForm('${t.id}', ${t.typical_duration_days})" class="text-cyan-400 hover:text-cyan-300 font-semibold cursor-pointer">Lập lịch →</button>
        </div>
      </div>
    `).join('');

    runLiveOpsPlanning();
    lucide.createIcons();
  } catch (err) {
    console.error("Error initializing liveops radar:", err);
  }
}

function prefillLiveOpsForm(typeId, duration) {
  document.getElementById('liveopsEventType').value = typeId;
  document.getElementById('liveopsDuration').value = duration;
  runLiveOpsPlanning();
}

async function runLiveOpsPlanning() {
  const type = document.getElementById('liveopsEventType').value;
  const date = document.getElementById('liveopsStartDate').value;
  const duration = document.getElementById('liveopsDuration').value;
  const dau = document.getElementById('liveopsBaseDau').value;
  const arpdau = document.getElementById('liveopsBaseArpdau').value;

  try {
    const res = await fetch('/api/mobile/liveops/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type_id: type,
        start_date: date,
        duration_days: parseInt(duration) || 14,
        base_dau: parseInt(dau) || 25000,
        base_arpdau: parseFloat(arpdau) || 0.08
      })
    });

    const data = await res.json();
    const fin = data.financial_forecast;
    const timing = data.timing_advisory;

    document.getElementById('liveopsResultContainer').classList.remove('hidden');

    // Populate KPIs
    document.getElementById('liveopsResTotalRev').innerText = `$${Math.round(fin.total_event_revenue_usd).toLocaleString()}`;
    document.getElementById('liveopsResNetLift').innerText = `+$${Math.round(fin.incremental_revenue_gain_usd).toLocaleString()}`;
    document.getElementById('liveopsResLiftPct').innerText = `Tăng trưởng +${fin.gross_revenue_lift_pct}% so với ngày thường`;
    document.getElementById('liveopsResPeakDay').innerText = `$${Math.round(fin.peak_day_revenue_usd).toLocaleString()}`;
    document.getElementById('liveopsResTimingGrade').innerText = `${timing.start_weekday} - ${timing.timing_grade}`;
    document.getElementById('liveopsResTimingTip').innerText = timing.recommendation;

    // Daily breakdown table
    const tableBody = document.getElementById('liveopsDailyTableBody');
    tableBody.innerHTML = (data.daily_forecast || []).map(d => `
      <tr class="hover:bg-slate-900/60 transition-colors">
        <td class="px-3 py-2 font-bold text-white">Ngày ${d.day}</td>
        <td class="px-3 py-2 text-slate-400">${d.weekday} (${d.date})</td>
        <td class="px-3 py-2 text-cyan-400 font-bold">$${d.projected_revenue.toLocaleString()}</td>
        <td class="px-3 py-2 text-slate-500">$${d.baseline_revenue.toLocaleString()}</td>
        <td class="px-3 py-2 font-semibold ${d.lift_multiplier > 1.4 ? 'text-amber-400' : 'text-emerald-400'}">x${d.lift_multiplier}</td>
      </tr>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error running LiveOps planning:", err);
  }
}

// ==========================================
// MODULE: UA CAMPAIGN PACING & DAYPARTING
// ==========================================
async function initUaPacingTab() {
  try {
    const res = await fetch('/api/mobile/campaign/dayparting-benchmarks');
    const data = await res.json();

    // Render Network Cards
    const netContainer = document.getElementById('uaNetworkCardsContainer');
    const nets = Object.values(data.networks || {});
    netContainer.innerHTML = nets.map(n => `
      <div class="glass-card p-5 rounded-2xl border border-slate-800 space-y-3 flex flex-col justify-between hover:border-violet-500/40 transition-colors">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold text-white flex items-center gap-1.5">
              <i data-lucide="radio" class="w-4 h-4 text-violet-400"></i>
              ${n.name}
            </h4>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-violet-500/20 text-violet-300 font-mono">${n.best_optimization_goal.split(' ')[0]}</span>
          </div>
          <p class="text-[11px] text-slate-300 font-semibold">${n.core_objective}</p>
          <div class="space-y-1 text-[10px] text-slate-400">
            <div>⚡ <strong>Thuật toán pacing:</strong> ${n.pacing_algorithm}</div>
            <div>🎯 <strong>Độ nhạy Creative:</strong> ${n.cpi_sensitivity}</div>
          </div>
          <div class="flex items-center gap-1.5 flex-wrap pt-1">
            ${(n.recommended_formats || []).map(f => `<span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] text-violet-300 font-mono">${f}</span>`).join('')}
          </div>
        </div>
        <div class="pt-2 border-t border-slate-800 text-[10px] text-amber-300/90 font-mono">
          📌 ${n.min_adset_budget_rule}
        </div>
      </div>
    `).join('');

    // Render Kill-Switch Grid
    const killGrid = document.getElementById('uaKillSwitchGrid');
    killGrid.innerHTML = (data.kill_switch_rules || []).map(r => {
      let badgeClass = "bg-rose-500/20 text-rose-400 border-rose-500/30";
      if (r.severity === 'POSITIVE_SCALE') badgeClass = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      if (r.severity === 'WARNING') badgeClass = "bg-amber-500/20 text-amber-400 border-amber-500/30";
      if (r.severity === 'HIGH') badgeClass = "bg-orange-500/20 text-orange-400 border-orange-500/30";

      return `
        <div class="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2.5 flex flex-col justify-between">
          <div class="space-y-2">
            <div class="flex items-start justify-between gap-1">
              <span class="px-2 py-0.5 rounded text-[10px] font-extrabold border ${badgeClass}">${r.severity}</span>
            </div>
            <h4 class="text-xs font-bold text-white leading-snug">${r.name}</h4>
            <div class="p-2 rounded bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
              <span class="text-slate-500 block text-[10px] uppercase font-bold">Điều kiện kích hoạt:</span>
              <span class="font-mono text-amber-300">${r.trigger_condition}</span>
            </div>
            <div class="text-[11px] text-emerald-300 font-bold flex items-center gap-1">
              <span>Hành động:</span>
              <span class="underline">${r.action}</span>
            </div>
          </div>
          <p class="text-[10px] text-slate-400 leading-snug pt-1 border-t border-slate-900">${r.logic}</p>
        </div>
      `;
    }).join('');

    runUaPacingSimulation();
    lucide.createIcons();
  } catch (err) {
    console.error("Error initializing UA pacing tab:", err);
  }
}

async function runUaPacingSimulation() {
  const budget = document.getElementById('uaSimBudget').value;
  const network = document.getElementById('uaSimNetwork').value;
  const goal = document.getElementById('uaSimGoal').value;
  const cpi = document.getElementById('uaSimTargetCpi').value;
  const roas = document.getElementById('uaSimTargetRoas').value;

  try {
    const res = await fetch('/api/mobile/campaign/optimize-pacing', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        daily_budget: parseFloat(budget) || 1000.0,
        network_id: network,
        optimization_goal: goal,
        target_cpi: parseFloat(cpi) || 1.80,
        target_roas_d0: parseFloat(roas) || 20.0
      })
    });

    const data = await res.json();
    const pSum = data.pacing_summary;
    const pDist = data.phase_distribution;

    // KPI cards
    document.getElementById('uaResRevenue').innerText = `$${Math.round(pSum.projected_daily_revenue_usd).toLocaleString()}`;
    document.getElementById('uaResBlendedRoas').innerText = `D0 ROAS: ${pSum.projected_blended_d0_roas}%`;
    document.getElementById('uaResInstalls').innerText = `${pSum.total_estimated_installs.toLocaleString()} installs`;
    document.getElementById('uaResEffectiveCpi').innerText = `CPI hiệu quả: $${pSum.blended_effective_cpi}`;
    document.getElementById('uaResPrimeBudget').innerText = `$${Math.round(pDist.golden_prime_hours_usd).toLocaleString()}`;
    document.getElementById('uaResPrimePct').innerText = `${pDist.golden_prime_hours_pct}% ngân sách ngày`;
    document.getElementById('uaResLunchBudget').innerText = `$${Math.round(pDist.lunch_rush_usd).toLocaleString()}`;
    document.getElementById('uaResLunchPct').innerText = `${pDist.lunch_rush_pct}% ngân sách ngày`;
    document.getElementById('uaResDeadZone').innerText = `$${Math.round(pDist.dead_zone_saved_usd).toLocaleString()}`;

    // 24-Hour Visual Heatmap Bar
    const barContainer = document.getElementById('uaHourlyHeatmapBar');
    barContainer.innerHTML = (data.hourly_schedule || []).map(h => {
      let color = "bg-slate-800 text-slate-400 border-slate-700";
      if (h.hour in {19:1, 20:1, 21:1, 22:1}) {
        color = "bg-amber-500/30 text-amber-300 border-amber-500/50 font-bold";
      } else if (h.hour in {11:1, 12:1, 13:1}) {
        color = "bg-sky-500/30 text-sky-300 border-sky-500/50";
      } else if (h.hour in {1:1, 2:1, 3:1, 4:1, 5:1}) {
        color = "bg-rose-950/40 text-rose-400/60 border-rose-900/40";
      } else {
        color = "bg-violet-950/40 text-violet-300 border-violet-800/40";
      }

      return `
        <div class="p-1.5 rounded-lg border text-center ${color} space-y-0.5">
          <div class="text-[9px] font-mono leading-none">${h.hour}h</div>
          <div class="text-[10px] font-mono font-bold leading-none">${h.bid_multiplier}x</div>
          <div class="text-[8px] opacity-80 leading-none">$${Math.round(h.allocated_budget_usd)}</div>
        </div>
      `;
    }).join('');

    // Full 24-Hour Schedule Table
    const tableBody = document.getElementById('uaHourlyTableBody');
    tableBody.innerHTML = (data.hourly_schedule || []).map(h => {
      let multBadge = "bg-violet-500/20 text-violet-300 border-violet-500/30";
      if (h.bid_multiplier >= 1.5) multBadge = "bg-amber-500/20 text-amber-300 border-amber-500/30 font-bold";
      if (h.bid_multiplier <= 0.4) multBadge = "bg-rose-500/20 text-rose-300 border-rose-500/30";

      return `
        <tr class="hover:bg-slate-900/60 transition-colors">
          <td class="px-3 py-2 font-bold text-white">${h.time_slot}</td>
          <td class="px-3 py-2 text-slate-300 font-sans">${h.phase}</td>
          <td class="px-3 py-2"><span class="px-1.5 py-0.5 rounded text-[10px] border ${multBadge}">${h.bid_multiplier}x</span></td>
          <td class="px-3 py-2 text-emerald-400 font-bold">$${h.allocated_budget_usd.toFixed(2)}</td>
          <td class="px-3 py-2 text-slate-400">${h.pct_of_day_budget}%</td>
          <td class="px-3 py-2 text-sky-400 font-semibold">${h.estimated_installs}</td>
          <td class="px-3 py-2 text-violet-300 font-bold">$${h.projected_revenue_usd.toFixed(2)}</td>
          <td class="px-3 py-2 text-amber-400 font-bold">${h.projected_d0_roas_pct}%</td>
          <td class="px-3 py-2 text-slate-400 font-sans">${h.strategy_advisory}</td>
        </tr>
      `;
    }).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error running UA pacing simulation:", err);
  }
}

// ==========================================
// MODULE 1: GACHA & IN-GAME ECONOMY LAB
// ==========================================
async function initGachaEconTab() {
  runGachaSimulation();
  runFaucetSinkEvaluation();
}

async function runGachaSimulation() {
  const model = document.getElementById('gachaSimModel').value;
  const copies = document.getElementById('gachaSimCopies').value;

  try {
    const res = await fetch('/api/mobile/gacha/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_key: model,
        target_copies: parseInt(copies) || 1
      })
    });

    const data = await res.json();
    const stats = data.monte_carlo_stats;

    document.getElementById('gachaResAvgPulls').innerText = `${stats.average_pulls} vé`;
    document.getElementById('gachaResAvgCost').innerText = `Chi phí: $${stats.avg_cost_usd.toLocaleString()}`;

    document.getElementById('gachaResLuckyPulls').innerText = `${stats.lucky_p10_pulls} vé`;
    document.getElementById('gachaResLuckyCost').innerText = `Chi phí: $${stats.lucky_cost_usd.toLocaleString()}`;

    document.getElementById('gachaResUnluckyPulls').innerText = `${stats.unlucky_p90_pulls} vé`;
    document.getElementById('gachaResUnluckyCost').innerText = `Chi phí: $${stats.unlucky_cost_usd.toLocaleString()}`;

    document.getElementById('gachaResWhaleCost').innerText = `$${stats.whale_full_ascension_cost_usd.toLocaleString()}`;
    document.getElementById('gachaResWorstCase').innerText = `${stats.worst_case_pulls} vé`;

    document.getElementById('gachaPsychologyVerdict').innerHTML = `
      <strong class="text-yellow-400">📊 Đánh Giá Kinh Tế Gacha:</strong> ${data.spending_psychology_verdict}
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error running Gacha simulation:", err);
  }
}

async function runFaucetSinkEvaluation() {
  const dailyF = document.getElementById('faucetDaily').value;
  const weeklyF = document.getElementById('faucetWeekly').value;
  const passF = document.getElementById('faucetMonthlyPass').value;
  const dailyS = document.getElementById('sinkDaily').value;
  const weeklyS = document.getElementById('sinkWeekly').value;
  const pullCost = document.getElementById('gachaPullGemCost').value;

  try {
    const res = await fetch('/api/mobile/gacha/faucet-sink', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        daily_faucet: parseInt(dailyF) || 150,
        weekly_faucet: parseInt(weeklyF) || 500,
        monthly_pass: parseInt(passF) || 3000,
        daily_sink: parseInt(dailyS) || 120,
        weekly_sink: parseInt(weeklyS) || 800,
        pull_cost: parseInt(pullCost) || 160
      })
    });

    const data = await res.json();
    const met = data.monthly_metrics;
    const diag = data.diagnosis;

    const container = document.getElementById('faucetSinkResults');
    container.innerHTML = `
      <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-2">
        <span class="text-xs text-slate-400">Cơ Cấu Tháng (30 Ngày)</span>
        <div class="text-sm font-bold text-white">Tổng Cấp: <span class="text-emerald-400 font-mono">${met.total_faucet_gems.toLocaleString()}</span> Gem</div>
        <div class="text-sm font-bold text-white">Tổng Xả: <span class="text-rose-400 font-mono">${met.total_sink_gems.toLocaleString()}</span> Gem</div>
        <div class="text-[11px] text-slate-400 pt-1 border-t border-slate-800">Tích lũy ròng: <strong class="text-yellow-400 font-mono">+${met.net_monthly_gems_saved.toLocaleString()}</strong> Gem (~${met.free_pulls_per_month} vé free)</div>
      </div>

      <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-2">
        <span class="text-xs text-slate-400">Hệ Số Lạm Phát (Faucet/Sink)</span>
        <div class="text-2xl font-black font-mono ${diag.health_color === 'emerald' ? 'text-emerald-400' : (diag.health_color === 'amber' ? 'text-amber-400' : 'text-rose-400')}">
          ${met.faucet_sink_ratio}x
        </div>
        <div class="text-xs font-bold text-white">${diag.status}</div>
        <div class="text-[10px] text-slate-400 leading-snug">${diag.verdict}</div>
      </div>

      <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-2">
        <span class="text-xs text-slate-400">Chỉ Dẫn Cân Bằng Game Design</span>
        <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-emerald-300 leading-relaxed">
          💡 ${diag.recommended_action}
        </div>
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error evaluating faucet-sink:", err);
  }
}

// ==========================================
// MODULE 2: PUBLISHER PITCH & SCORECARD
// ==========================================
async function initPublisherPitchTab() {
  runPublisherScorecard();
  runPublishingDealSimulation();
}

async function runPublisherScorecard() {
  const d1 = document.getElementById('pubPitchD1').value;
  const d7 = document.getElementById('pubPitchD7').value;
  const cpi = document.getElementById('pubPitchCpi').value;
  const playtime = document.getElementById('pubPitchPlaytime').value;
  const genre = document.getElementById('pubPitchGenre').value;

  try {
    const res = await fetch('/api/mobile/publisher/scorecard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        d1_retention: parseFloat(d1) || 40.0,
        d7_retention: parseFloat(d7) || 15.0,
        cpi_us: parseFloat(cpi) || 0.85,
        playtime_mins: parseInt(playtime) || 28,
        genre: genre
      })
    });

    const data = await res.json();
    const grid = document.getElementById('pubScorecardGrid');

    grid.innerHTML = (data.evaluations || []).map(e => `
      <div class="glass-card p-5 rounded-2xl border ${e.badge_color === 'emerald' ? 'border-emerald-500/40 bg-emerald-950/10' : (e.badge_color === 'indigo' ? 'border-indigo-500/30 bg-indigo-950/10' : 'border-slate-800')} space-y-3 flex flex-col justify-between">
        <div class="space-y-3">
          <div class="flex items-start justify-between gap-2">
            <div>
              <h4 class="text-xs font-bold text-white">${e.publisher_archetype}</h4>
              <div class="text-[10px] text-slate-400 mt-0.5">${e.examples.join(', ')}</div>
            </div>
            <span class="px-2 py-0.5 rounded text-xs font-black font-mono ${e.badge_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-300'}">
              ${e.weighted_score}/100
            </span>
          </div>

          <div class="text-[11px] font-bold ${e.badge_color === 'emerald' ? 'text-emerald-300' : 'text-slate-300'}">
            🎯 ${e.readiness_grade}
          </div>

          <!-- Pass/Fail Matrix -->
          <div class="grid grid-cols-2 gap-2 text-[10px] font-mono">
            <div class="p-1.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
              <span>D1 (${e.benchmark_comparison.d1.actual}%):</span>
              <span class="${e.benchmark_comparison.d1.passed ? 'text-emerald-400' : 'text-rose-400'}">${e.benchmark_comparison.d1.passed ? 'PASSED' : 'MISS'}</span>
            </div>
            <div class="p-1.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
              <span>D7 (${e.benchmark_comparison.d7.actual}%):</span>
              <span class="${e.benchmark_comparison.d7.passed ? 'text-emerald-400' : 'text-rose-400'}">${e.benchmark_comparison.d7.passed ? 'PASSED' : 'MISS'}</span>
            </div>
            <div class="p-1.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
              <span>CPI ($${e.benchmark_comparison.cpi.actual}):</span>
              <span class="${e.benchmark_comparison.cpi.passed ? 'text-emerald-400' : 'text-rose-400'}">${e.benchmark_comparison.cpi.passed ? 'PASSED' : 'MISS'}</span>
            </div>
            <div class="p-1.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
              <span>Play (${e.benchmark_comparison.playtime.actual}m):</span>
              <span class="${e.benchmark_comparison.playtime.passed ? 'text-emerald-400' : 'text-rose-400'}">${e.benchmark_comparison.playtime.passed ? 'PASSED' : 'MISS'}</span>
            </div>
          </div>

          <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[10px] space-y-1 text-slate-300">
            <div><strong>RevShare thông lệ:</strong> <span class="text-amber-300 font-mono">${e.deal_terms_preview.revshare}</span></div>
            <div><strong>Bảo lãnh MG:</strong> <span class="text-emerald-300 font-mono">${e.deal_terms_preview.minimum_guarantee}</span></div>
          </div>
        </div>

        <p class="text-[10px] text-slate-400 leading-snug pt-2 border-t border-slate-800">
          ${e.deal_terms_preview.advisory}
        </p>
      </div>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error running publisher scorecard:", err);
  }
}

async function runPublishingDealSimulation() {
  const gross = document.getElementById('dealSimGross').value;
  const ua = document.getElementById('dealSimUa').value;
  const revshare = document.getElementById('dealSimRevshare').value;
  const mg = document.getElementById('dealSimMg').value;

  try {
    const res = await fetch('/api/mobile/publisher/simulate-deal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        projected_gross: parseFloat(gross) || 500000.0,
        ua_budget: parseFloat(ua) || 300000.0,
        studio_revshare: parseFloat(revshare) || 40.0,
        minimum_guarantee: parseFloat(mg) || 50000.0
      })
    });

    const data = await res.json();
    const fin = data.financial_breakdown;

    const results = document.getElementById('dealSimResults');
    results.innerHTML = `
      <div class="glass-card p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10">
        <span class="text-xs text-slate-400">Studio Thực Nhận (Net)</span>
        <div class="text-xl font-black text-emerald-400 mt-1 font-mono">$${Math.round(fin.studio_net_earnings_usd).toLocaleString()}</div>
        <div class="text-[10px] text-emerald-300/70 mt-0.5">Bảo lãnh tối thiểu: $${fin.minimum_guarantee_paid_usd.toLocaleString()}</div>
      </div>
      <div class="glass-card p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/10">
        <span class="text-xs text-slate-400">Publisher Net Lãi Ròng</span>
        <div class="text-xl font-black text-indigo-400 mt-1 font-mono">$${Math.round(fin.publisher_net_profit_usd).toLocaleString()}</div>
        <div class="text-[10px] text-indigo-300/70 mt-0.5">Sau khi đã thanh toán UA và Studio</div>
      </div>
      <div class="glass-card p-4 rounded-xl border border-slate-700 bg-slate-900/60">
        <span class="text-xs text-slate-400">Phí Store 30% (Apple/Google)</span>
        <div class="text-xl font-black text-slate-300 mt-1 font-mono">$${Math.round(fin.app_store_fee_usd).toLocaleString()}</div>
        <div class="text-[10px] text-slate-500 mt-0.5">Nền tảng trừ trực tiếp</div>
      </div>
      <div class="glass-card p-4 rounded-xl border border-amber-500/30 bg-amber-950/10">
        <span class="text-xs text-slate-400">Ngân Sách UA Marketing</span>
        <div class="text-xl font-black text-amber-400 mt-1 font-mono">$${Math.round(fin.ua_ad_spend_usd).toLocaleString()}</div>
        <div class="text-[10px] text-amber-300/70 mt-0.5">Publisher tài trợ 100%</div>
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error simulating publishing deal:", err);
  }
}

// ==========================================
// MODULE 3: CULTURALIZATION & REGULATORY C10N
// ==========================================
async function initC10nTab() {
  runC10nAudit();
}

async function runC10nAudit() {
  const title = document.getElementById('c10nGameTitle').value;
  const skeletons = document.getElementById('c10nCheckSkeletons').checked;
  const blood = document.getElementById('c10nCheckBlood').checked;
  const gacha = document.getElementById('c10nCheckGacha').checked;
  const costumes = document.getElementById('c10nCheckCostumes').checked;
  const rtl = document.getElementById('c10nCheckRTL').checked;

  const regions = [];
  if (document.getElementById('c10nRegChina').checked) regions.push('china');
  if (document.getElementById('c10nRegJapan').checked) regions.push('japan');
  if (document.getElementById('c10nRegMena').checked) regions.push('mena');
  if (document.getElementById('c10nRegEU').checked) regions.push('eu');

  try {
    const res = await fetch('/api/mobile/culturalization/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_title: title,
        target_regions: regions,
        has_skeletons: skeletons,
        has_red_blood: blood,
        has_gacha_lootbox: gacha,
        has_skimpy_costumes: costumes,
        supports_rtl_arabic: rtl
      })
    });

    const data = await res.json();
    const results = document.getElementById('c10nAuditResults');

    results.innerHTML = `
      <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between flex-wrap gap-3">
        <div>
          <div class="text-xs text-slate-400">Kết Quả Thẩm Định Kiểm Duyệt Toàn Diện</div>
          <div class="text-sm font-bold text-white mt-0.5">${data.executive_summary}</div>
        </div>
        <span class="px-3 py-1 rounded-full text-xs font-black ${data.badge_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : (data.badge_color === 'indigo' ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30')}">
          ${data.overall_status}
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        ${(data.risk_breakdown || []).map(r => `
          <div class="p-4 rounded-xl bg-slate-950 border border-rose-500/30 space-y-3">
            <div class="flex items-center justify-between border-b border-slate-800 pb-2">
              <div class="font-bold text-white text-xs flex items-center gap-1.5">
                <span>${r.flag}</span>
                <span>${r.region_name}</span>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 font-mono">${r.risk_count} Rủi Ro</span>
            </div>
            <div class="space-y-2">
              ${r.issues.map(iss => `
                <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1 text-xs">
                  <div class="flex items-center justify-between">
                    <strong class="text-rose-400 text-[11px]">[${iss.code}] ${iss.category}</strong>
                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-rose-950 text-rose-300">${iss.severity}</span>
                  </div>
                  <p class="text-[11px] text-slate-300 leading-snug">${iss.rule}</p>
                  <div class="text-[10px] text-emerald-300 pt-1 border-t border-slate-800/60 leading-snug">
                    🛠️ <strong>Giải pháp sửa:</strong> ${iss.remediation}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error running C10n audit:", err);
  }
}

// ==========================================
// MODULE 4: CHOKE-POINT & CHURN DIAGNOSTIC
// ==========================================
async function initChokePointTab() {
  runChurnFunnelDiagnostic();
}

async function runChurnFunnelDiagnostic() {
  const installs = document.getElementById('churnSimInstalls').value;
  const patch = document.getElementById('churnSimPatchPass').value;
  const tutorial = document.getElementById('churnSimTutorialPass').value;
  const boss = document.getElementById('churnSimBossWin').value;
  const losses = document.getElementById('churnSimLossesToQuit').value;

  try {
    const res = await fetch('/api/mobile/churn/diagnose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        installs: parseInt(installs) || 10000,
        patch_pass_pct: parseFloat(patch) || 84.0,
        tutorial_pass_pct: parseFloat(tutorial) || 68.0,
        boss_win_pct: parseFloat(boss) || 38.0,
        losses_to_quit: parseInt(losses) || 3
      })
    });

    const data = await res.json();
    const fRes = data.custom_funnel_results;
    const evalRes = data.chokepoint_evaluation;
    const pack = data.dynamic_rescue_pack;

    const container = document.getElementById('churnDiagnosticContainer');
    container.innerHTML = `
      <!-- Funnel Flow KPIs -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <span class="text-xs text-slate-400">Vượt Qua Tải Patch</span>
          <div class="text-xl font-black text-white mt-1 font-mono">${fRes.users_survived_patch.toLocaleString()}</div>
          <div class="text-[10px] text-slate-500">Rơi rụng: ${(fRes.initial_installs - fRes.users_survived_patch).toLocaleString()} user</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <span class="text-xs text-slate-400">Xong Tutorial FTUE</span>
          <div class="text-xl font-black text-white mt-1 font-mono">${fRes.users_completed_tutorial.toLocaleString()}</div>
          <div class="text-[10px] text-slate-500">Người chơi bước vào core loop</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-rose-500/30 bg-rose-950/10">
          <span class="text-xs text-slate-400">Rage-Quit Tại Ải Boss</span>
          <div class="text-xl font-black text-rose-400 mt-1 font-mono">${fRes.users_rage_quit_at_chokepoint.toLocaleString()}</div>
          <div class="text-[10px] text-rose-300/70">Ức chế gỡ game do kẹt độ khó</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10">
          <span class="text-xs text-slate-400">Dự Báo D1 Retention</span>
          <div class="text-xl font-black text-emerald-400 mt-1 font-mono">${fRes.projected_d1_retention_pct}%</div>
          <div class="text-[10px] text-emerald-300/70">D1 sống sót quay lại</div>
        </div>
      </div>

      <!-- Alert & Dynamic Rescue Pack Lifeline -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-5">
        <div class="md:col-span-5 p-4 rounded-xl bg-slate-950 border ${evalRes.badge_color === 'rose' ? 'border-rose-500/40 bg-rose-950/10' : 'border-slate-800'} space-y-2">
          <div class="text-xs font-extrabold ${evalRes.badge_color === 'rose' ? 'text-rose-400' : 'text-emerald-400'}">
            ${evalRes.severity_status}
          </div>
          <p class="text-[11px] text-slate-300 leading-relaxed">${evalRes.diagnosis}</p>
          <div class="pt-2 text-[10px] text-slate-400">
            Tỷ lệ thắng ải Boss hiện tại: <strong class="text-white font-mono">${evalRes.boss_win_rate_pct}%</strong>
          </div>
        </div>

        <!-- Dynamic Rescue Pack Proposal -->
        <div class="md:col-span-7 glass-card p-5 rounded-2xl border border-orange-500/40 bg-orange-950/10 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <span class="px-2 py-0.5 rounded text-[10px] font-black bg-orange-500/20 text-orange-400 border border-orange-500/30 font-mono">${pack.badge_sticker}</span>
              <h4 class="text-sm font-bold text-white mt-1">${pack.pack_title}</h4>
            </div>
            <div class="text-2xl font-black text-orange-400 font-mono">$${pack.price_point_usd}</div>
          </div>

          <div class="text-[11px] text-slate-300">
            ⚡ <strong>Điều kiện kích hoạt tự động:</strong> ${pack.trigger_condition}
          </div>

          <div class="grid grid-cols-2 gap-2 text-[10px]">
            ${pack.contents.map(c => `<div class="p-2 rounded bg-slate-900 border border-slate-800 text-slate-300">🎁 ${c}</div>`).join('')}
          </div>

          <div class="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
            <span class="text-emerald-400 font-semibold">${pack.projected_conversion_boost}</span>
            <span class="text-sky-400 font-semibold">${pack.d1_retention_saved}</span>
          </div>
        </div>
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error diagnosing churn funnel:", err);
  }
}

// ==========================================
// MODULE 5: VIRAL K-FACTOR & TIKTOK FORECASTER
// ==========================================
async function initViralKFactorTab() {
  runKFactorSimulation();
  runTiktokUgcForecast();
}

async function runKFactorSimulation() {
  const paid = document.getElementById('kSimPaidInstalls').value;
  const cpi = document.getElementById('kSimPaidCpi').value;
  const invites = document.getElementById('kSimInvites').value;
  const cvr = document.getElementById('kSimCvr').value;

  try {
    const res = await fetch('/api/mobile/viral/k-factor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        paid_installs: parseInt(paid) || 10000,
        paid_cpi: parseFloat(cpi) || 2.00,
        invites_per_user: parseFloat(invites) || 2.8,
        invitee_cvr: (parseFloat(cvr) || 25.0) / 100.0,
        cycles: 5
      })
    });

    const data = await res.json();
    const met = data.k_factor_metrics;
    const acq = data.acquisition_impact;

    const container = document.getElementById('kFactorResultsContainer');
    container.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border border-pink-500/30 bg-pink-950/10">
          <span class="text-xs text-slate-400">Hệ Số K-Factor</span>
          <div class="text-2xl font-black text-pink-400 mt-1 font-mono">${met.k_factor_value}</div>
          <div class="text-[10px] text-pink-300/70 mt-0.5">${met.classification}</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10">
          <span class="text-xs text-slate-400">Lượt Tải Lan Truyền (Free)</span>
          <div class="text-2xl font-black text-emerald-400 mt-1 font-mono">+${acq.organic_viral_installs_gained.toLocaleString()}</div>
          <div class="text-[10px] text-emerald-300/70 mt-0.5">Kéo theo từ bạn bè</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-purple-500/30 bg-purple-950/10">
          <span class="text-xs text-slate-400">CPI Tổng Hợp (Blended CPI)</span>
          <div class="text-2xl font-black text-purple-400 mt-1 font-mono">$${acq.blended_cpi_usd}</div>
          <div class="text-[10px] text-purple-300/70 mt-0.5">Tiết kiệm -${acq.cpi_reduction_pct}% so với giá gốc $${acq.initial_paid_cpi_usd}</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-sky-500/30 bg-sky-950/10">
          <span class="text-xs text-slate-400">Tổng Người Dùng Thu Về</span>
          <div class="text-2xl font-black text-sky-400 mt-1 font-mono">${acq.total_users_acquired.toLocaleString()}</div>
          <div class="text-[10px] text-sky-300/70 mt-0.5">Sau 5 vòng lặp chia sẻ</div>
        </div>
      </div>

      <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300">
        <strong>💬 Nhận Định Tăng Trưởng:</strong> ${met.verdict}
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error running K-factor simulation:", err);
  }
}

async function runTiktokUgcForecast() {
  const budget = document.getElementById('ugcSimBudget').value;
  const creators = document.getElementById('ugcSimCreators').value;
  const views = document.getElementById('ugcSimViews').value;

  try {
    const res = await fetch('/api/mobile/viral/tiktok-forecast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        budget: parseFloat(budget) || 5000.0,
        creator_count: parseInt(creators) || 25,
        avg_views: parseInt(views) || 40000
      })
    });

    const data = await res.json();
    const p = data.performance_forecast;

    const container = document.getElementById('ugcForecastResults');
    container.innerHTML = `
      <div class="glass-card p-4 rounded-xl border border-purple-500/30 bg-purple-950/10">
        <span class="text-xs text-slate-400">Lượt Xem Video Dự Kiến</span>
        <div class="text-xl font-black text-purple-400 mt-1 font-mono">${p.total_projected_views.toLocaleString()}</div>
        <div class="text-[10px] text-purple-300/70 mt-0.5">CPM: $${p.effective_cpm_usd}</div>
      </div>
      <div class="glass-card p-4 rounded-xl border border-sky-500/30 bg-sky-950/10">
        <span class="text-xs text-slate-400">Lượt Tải Trực Tiếp (Bio)</span>
        <div class="text-xl font-black text-sky-400 mt-1 font-mono">${p.direct_bio_installs.toLocaleString()}</div>
        <div class="text-[10px] text-sky-300/70 mt-0.5">CTR 1.5% từ link</div>
      </div>
      <div class="glass-card p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10">
        <span class="text-xs text-slate-400">Lực Đẩy Tìm Kiếm Store</span>
        <div class="text-xl font-black text-emerald-400 mt-1 font-mono">+${p.organic_search_lift_installs.toLocaleString()}</div>
        <div class="text-[10px] text-emerald-300/70 mt-0.5">Organic Search Lift x2.2</div>
      </div>
      <div class="glass-card p-4 rounded-xl border border-amber-500/30 bg-amber-950/10">
        <span class="text-xs text-slate-400">CPI Thực Tế UGC</span>
        <div class="text-xl font-black text-amber-400 mt-1 font-mono">$${p.effective_cpi_usd}</div>
        <div class="text-[10px] text-amber-300/70 mt-0.5">Tổng: ${p.total_campaign_installs.toLocaleString()} installs</div>
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error forecasting TikTok UGC:", err);
  }
}
