/* Bot center, pitch deck, A/B testing, ad mediation & LTV */
// ==========================================
// MODULE 1: WEBHOOK BOT SERVICE
// ==========================================
async function initBotCenterTab() {
  try {
    const res = await fetch('/api/mobile/webhook/config');
    const cfg = await res.json();

    if (cfg.discord_webhook_url) document.getElementById('botDiscordUrl').value = cfg.discord_webhook_url;
    document.getElementById('botDiscordEnabled').checked = !!cfg.discord_enabled;

    if (cfg.telegram_bot_token) document.getElementById('botTelegramToken').value = cfg.telegram_bot_token;
    if (cfg.telegram_chat_id) document.getElementById('botTelegramChatId').value = cfg.telegram_chat_id;
    document.getElementById('botTelegramEnabled').checked = !!cfg.telegram_enabled;

    document.getElementById('botPrefRivalJump').checked = cfg.alert_on_rival_rank_jump !== false;
    document.getElementById('botPrefLiveopsClash').checked = cfg.alert_on_liveops_cpi_surge !== false;
    document.getElementById('botPrefMorningDigest').checked = cfg.daily_morning_digest !== false;
  } catch (err) {
    console.error("Error loading webhook config:", err);
  }
}

async function saveWebhookConfig() {
  const discordUrl = document.getElementById('botDiscordUrl').value;
  const discordEnabled = document.getElementById('botDiscordEnabled').checked;
  const telegramToken = document.getElementById('botTelegramToken').value;
  const telegramChatId = document.getElementById('botTelegramChatId').value;
  const telegramEnabled = document.getElementById('botTelegramEnabled').checked;

  const prefRival = document.getElementById('botPrefRivalJump').checked;
  const prefLiveops = document.getElementById('botPrefLiveopsClash').checked;
  const prefDigest = document.getElementById('botPrefMorningDigest').checked;

  try {
    const res = await fetch('/api/mobile/webhook/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        discord_webhook_url: discordUrl,
        discord_enabled: discordEnabled,
        telegram_bot_token: telegramToken,
        telegram_chat_id: telegramChatId,
        telegram_enabled: telegramEnabled,
        alert_on_rival_rank_jump: prefRival,
        alert_on_liveops_cpi_surge: prefLiveops,
        daily_morning_digest: prefDigest
      })
    });
    const data = await res.json();
    showToast(data.message || 'Đã lưu cấu hình Webhook Bot!');
  } catch (err) {
    showToast('Lỗi khi lưu cấu hình Webhook Bot');
  }
}

async function triggerWebhookTest() {
  const box = document.getElementById('botDispatchStatusBox');
  box.classList.remove('hidden');
  box.innerHTML = '<span class="text-slate-400">Đang gửi gói tin alert thử nghiệm tới các kênh...</span>';

  try {
    const res = await fetch('/api/mobile/webhook/test', { method: 'POST' });
    const data = await res.json();
    box.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-emerald-400">Kết quả phát tín hiệu:</span>
        <div class="space-x-3 font-mono text-[11px]">
          <span>Discord: <strong class="${data.discord === true ? 'text-emerald-400' : 'text-slate-500'}">${data.discord === true ? 'THÀNH CÔNG' : (data.discord === false ? 'THẤT BẠI' : 'TẮT')}</strong></span>
          <span>Telegram: <strong class="${data.telegram === true ? 'text-emerald-400' : 'text-slate-500'}">${data.telegram === true ? 'THÀNH CÔNG' : (data.telegram === false ? 'THẤT BẠI' : 'TẮT')}</strong></span>
        </div>
      </div>
    `;
    showToast('Đã phát tín hiệu Alert thử nghiệm!');
  } catch (err) {
    box.innerHTML = '<span class="text-rose-400">Lỗi kết nối khi gửi Alert Test</span>';
  }
}

async function triggerMorningDigestManual() {
  const box = document.getElementById('botDispatchStatusBox');
  box.classList.remove('hidden');
  box.innerHTML = '<span class="text-slate-400">Đang tổng hợp và phát bản tin sáng...</span>';

  try {
    const res = await fetch('/api/mobile/webhook/trigger-digest', { method: 'POST' });
    const data = await res.json();
    box.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-amber-400">Bản Tin Chiến Lược Sáng:</span>
        <div class="space-x-3 font-mono text-[11px]">
          <span>Discord: <strong class="${data.discord === true ? 'text-emerald-400' : 'text-slate-500'}">${data.discord === true ? 'ĐÃ GỬI' : 'TẮT'}</strong></span>
          <span>Telegram: <strong class="${data.telegram === true ? 'text-emerald-400' : 'text-slate-500'}">${data.telegram === true ? 'ĐÃ GỬI' : 'TẮT'}</strong></span>
        </div>
      </div>
    `;
    showToast('Đã phát bản tin sáng thành công!');
  } catch (err) {
    box.innerHTML = '<span class="text-rose-400">Lỗi khi phát bản tin sáng</span>';
  }
}

// ==========================================
// MODULE 2: EXECUTIVE PITCH DECK GENERATOR
// ==========================================
function initPitchDeckTab() {
  // Inputs already hold defaults
}

async function launchPitchDeckPresentation() {
  const title = document.getElementById('deckInputTitle').value;
  const genre = document.getElementById('deckInputGenre').value;
  const regions = document.getElementById('deckInputRegions').value;
  const cpi = document.getElementById('deckInputCpi').value;
  const d1 = document.getElementById('deckInputD1').value;
  const d7 = document.getElementById('deckInputD7').value;
  const breakEven = document.getElementById('deckInputBreakEven').value;
  const pub = document.getElementById('deckInputPub').value;

  try {
    showToast('Đang biên dịch Slide Deck PDF...');
    const res = await fetch('/api/mobile/deck/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_title: title,
        genre: genre,
        target_regions: regions,
        target_cpi: parseFloat(cpi) || 1.80,
        projected_d1: parseFloat(d1) || 42.0,
        projected_d7: parseFloat(d7) || 16.5,
        break_even_day: parseInt(breakEven) || 45,
        publisher_fit: pub
      })
    });

    const html = await res.text();
    const win = window.open('', '_blank');
    if (win) {
      win.document.open();
      win.document.write(html);
      win.document.close();
    } else {
      showToast('Vui lòng cho phép Pop-up trên trình duyệt để mở Slide');
    }
  } catch (err) {
    console.error("Error generating pitch deck:", err);
  }
}

// ==========================================
// MODULE 3: SOFT-LAUNCH A/B TESTING
// ==========================================
async function initAbTestingTab() {
  runSampleSizeCalculation();
  runAbSignificanceEvaluation();
}

async function runSampleSizeCalculation() {
  const base = document.getElementById('abPlanBaseRate').value;
  const lift = document.getElementById('abPlanLift').value;
  const conf = document.getElementById('abPlanConfidence').value;
  const country = document.getElementById('abPlanCountry').value;

  try {
    const res = await fetch('/api/mobile/ab-test/sample-size', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        baseline_rate_pct: parseFloat(base) || 40.0,
        expected_lift_pct: parseFloat(lift) || 3.0,
        confidence_level: parseFloat(conf) || 95.0,
        power: 80.0,
        country: country
      })
    });

    const data = await res.json();
    const sRes = data.sample_size_results;

    const container = document.getElementById('sampleSizeResultContainer');
    container.innerHTML = `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border border-cyan-500/30 bg-cyan-950/10">
          <span class="text-xs text-slate-400">Cỡ Mẫu / Mỗi Nhánh</span>
          <div class="text-xl font-black text-cyan-400 mt-1 font-mono">${sRes.sample_per_variant.toLocaleString()} user</div>
          <div class="text-[10px] text-cyan-300/70 mt-0.5">Mỗi nhánh A và B</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/10">
          <span class="text-xs text-slate-400">Tổng Installs Cần Mua</span>
          <div class="text-xl font-black text-indigo-400 mt-1 font-mono">${sRes.total_sample_needed.toLocaleString()} user</div>
          <div class="text-[10px] text-indigo-300/70 mt-0.5">Đạt độ tin cậy 95%</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10">
          <span class="text-xs text-slate-400">Ngân Sách Dự Kiến</span>
          <div class="text-xl font-black text-emerald-400 mt-1 font-mono">$${sRes.estimated_budget_usd.toLocaleString()}</div>
          <div class="text-[10px] text-emerald-300/70 mt-0.5">CPI test: $${sRes.country_cpi_usd}</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-slate-700 bg-slate-900/60">
          <span class="text-xs text-slate-400">Mục Tiêu Thử Nghiệm</span>
          <div class="text-xs font-bold text-white mt-1 leading-snug">${sRes.testing_advisory}</div>
        </div>
      </div>
      <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 mt-3">
        <strong>📋 Khuyến Nghị Khoa Học:</strong> ${data.recommendation}
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error calculating sample size:", err);
  }
}

async function runAbSignificanceEvaluation() {
  const visA = document.getElementById('abTestVisA').value;
  const convA = document.getElementById('abTestConvA').value;
  const visB = document.getElementById('abTestVisB').value;
  const convB = document.getElementById('abTestConvB').value;

  try {
    const res = await fetch('/api/mobile/ab-test/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        visitors_a: parseInt(visA) || 1500,
        conversions_a: parseInt(convA) || 600,
        visitors_b: parseInt(visB) || 1500,
        conversions_b: parseInt(convB) || 665,
        metric_name: "D1 Retention"
      })
    });

    const data = await res.json();
    const cmp = data.comparison;
    const dec = data.decision;

    const results = document.getElementById('abSignificanceResults');
    results.innerHTML = `
      <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between flex-wrap gap-3">
        <div>
          <span class="text-xs text-slate-400">Kết Luận Thẩm Định Z-Test (p-value: ${cmp.p_value})</span>
          <div class="text-sm font-bold text-white mt-0.5">${dec.recommended_action}</div>
        </div>
        <span class="px-3 py-1 rounded-full text-xs font-black ${dec.badge_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : (dec.badge_color === 'rose' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30')}">
          ${dec.verdict}
        </span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <span class="text-xs text-slate-400">Tăng Trưởng Tương Đối</span>
          <div class="text-xl font-black ${cmp.relative_lift_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'} mt-1 font-mono">
            ${cmp.relative_lift_pct >= 0 ? '+' : ''}${cmp.relative_lift_pct}%
          </div>
          <div class="text-[10px] text-slate-500">Chênh lệch: ${cmp.absolute_diff_pct}%</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <span class="text-xs text-slate-400">Hệ Số Z-Score</span>
          <div class="text-xl font-black text-white mt-1 font-mono">${cmp.z_score}</div>
          <div class="text-[10px] text-slate-500">Chuẩn ngưỡng |Z| > 1.96</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <span class="text-xs text-slate-400">Độ Tin Cậy Thống Kê</span>
          <div class="text-xl font-black text-cyan-400 mt-1 font-mono">${cmp.confidence_pct}%</div>
          <div class="text-[10px] text-cyan-300/70">Mức chuẩn 95%</div>
        </div>
        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <span class="text-xs text-slate-400">Tỷ Lệ Nhánh B vs A</span>
          <div class="text-sm font-bold text-white mt-1 font-mono">${data.variant_b_treatment.rate_pct}% vs ${data.variant_a_control.rate_pct}%</div>
          <div class="text-[10px] text-slate-500">Conversion rate</div>
        </div>
      </div>
    `;

    lucide.createIcons();
  } catch (err) {
    console.error("Error evaluating A/B test:", err);
  }
}

// ==========================================
// MODULE 4: AD MEDIATION WATERFALL & LTV SIMULATOR
// ==========================================
let medLtvChartInstance = null;
let medFormatChartInstance = null;

let medCurrentTier1Pct = 30.0;
let medCurrentTier2Pct = 25.0;
let medCurrentTier3Pct = 45.0;

function applyMedRegionPreset() {
  const preset = document.getElementById('medSimRegionPreset').value;
  if (preset === 'us_heavy') {
    medCurrentTier1Pct = 70.0;
    medCurrentTier2Pct = 20.0;
    medCurrentTier3Pct = 10.0;
  } else if (preset === 'sea_heavy') {
    medCurrentTier1Pct = 10.0;
    medCurrentTier2Pct = 15.0;
    medCurrentTier3Pct = 75.0;
  } else {
    medCurrentTier1Pct = 30.0;
    medCurrentTier2Pct = 25.0;
    medCurrentTier3Pct = 45.0;
  }
  runMediationSimulation();
}

async function initMediationTab() {
  try {
    const res = await fetch('/api/mobile/mediation/benchmarks');
    const data = await res.json();

    // 1. Regional Benchmarks Table
    const tbody = document.getElementById('mediationBenchmarkTableBody');
    if (tbody) {
      tbody.innerHTML = (data.regional_benchmarks || []).map(b => `
        <tr class="hover:bg-slate-900/60 transition-colors">
          <td class="px-4 py-3 font-semibold text-white">${b.name}</td>
          <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${b.tier === 'Tier 1' ? 'bg-indigo-500/20 text-indigo-300' : (b.tier === 'Tier 2' ? 'bg-cyan-500/20 text-cyan-300' : 'bg-emerald-500/20 text-emerald-300')}">${b.tier}</span></td>
          <td class="px-4 py-3 text-emerald-400 font-bold font-mono">$${b.rewarded_ecpm.toFixed(2)}</td>
          <td class="px-4 py-3 text-amber-400 font-bold font-mono">$${b.interstitial_ecpm.toFixed(2)}</td>
          <td class="px-4 py-3 text-purple-400 font-bold font-mono">$${(b.aoa_ecpm || 0).toFixed(2)}</td>
          <td class="px-4 py-3 text-sky-400 font-bold font-mono">$${b.banner_ecpm.toFixed(2)}</td>
          <td class="px-4 py-3 text-slate-400 font-sans text-[11px]">${b.notes}</td>
        </tr>
      `).join('');
    }

    // 2. Waterfall Tier Architecture Cards
    const tierCards = document.getElementById('medWaterfallTierCards');
    if (tierCards) {
      tierCards.innerHTML = (data.waterfall_tiers || []).map((w, idx) => `
        <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white flex items-center gap-1.5">
              <span class="w-5 h-5 rounded-md bg-amber-500/20 text-amber-300 flex items-center justify-center text-[10px] font-mono">${idx + 1}</span>
              ${w.priority}
            </span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-amber-300 border border-slate-700">${w.price_floor}</span>
          </div>
          <p class="text-[11px] text-slate-300">${w.role}</p>
          <div class="pt-1 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
            <span class="text-slate-400">Fill Share: <strong class="text-emerald-400">${w.fill_share}</strong></span>
            <span class="text-slate-500 truncate max-w-[200px]">${w.networks}</span>
          </div>
        </div>
      `).join('');
    }

    runMediationSimulation();
    lucide.createIcons();
  } catch (err) {
    console.error("Error initializing mediation tab:", err);
  }
}

async function runMediationSimulation() {
  const dau = document.getElementById('medSimDau') ? parseInt(document.getElementById('medSimDau').value) || 50000 : 50000;
  const sessionMins = document.getElementById('medSimSession') ? parseInt(document.getElementById('medSimSession').value) || 15 : 15;
  const sessionsPerDay = document.getElementById('medSimSessionsPerDay') ? parseFloat(document.getElementById('medSimSessionsPerDay').value) || 2.4 : 2.4;
  const cooldownSecs = document.getElementById('medSimCooldown') ? parseInt(document.getElementById('medSimCooldown').value) || 75 : 75;
  const rewardedWatches = document.getElementById('medSimRewarded') ? parseFloat(document.getElementById('medSimRewarded').value) || 2.8 : 2.8;
  const targetCpi = document.getElementById('medSimCpi') ? parseFloat(document.getElementById('medSimCpi').value) || 0.65 : 0.65;
  const iapSharePct = document.getElementById('medSimIapShare') ? parseFloat(document.getElementById('medSimIapShare').value) || 30.0 : 30.0;
  const bannerEnabled = document.getElementById('medSimBannerCheck') ? document.getElementById('medSimBannerCheck').checked : true;
  const aoaEnabled = document.getElementById('medSimAoaCheck') ? document.getElementById('medSimAoaCheck').checked : true;

  try {
    const res = await fetch('/api/mobile/mediation/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dau: dau,
        session_mins: sessionMins,
        sessions_per_day: sessionsPerDay,
        cooldown_secs: cooldownSecs,
        rewarded_watches: rewardedWatches,
        banner_enabled: bannerEnabled,
        aoa_enabled: aoaEnabled,
        tier1_pct: medCurrentTier1Pct,
        tier2_pct: medCurrentTier2Pct,
        tier3_pct: medCurrentTier3Pct,
        iap_share_pct: iapSharePct,
        target_cpi: targetCpi
      })
    });

    const data = await res.json();
    const m = data.monthly_projection || {};
    const a = data.arpdau_metrics || {};
    const l = data.ltv_milestones || {};
    const f = data.ad_fatigue_diagnostic || {};
    const revDaily = data.daily_revenue_breakdown || {};

    // 1. Update Top KPI Cards
    const elGross = document.getElementById('medStatMonthlyAdRev');
    if (elGross) elGross.innerText = `$${Math.round(m.gross_ad_revenue_usd || 0).toLocaleString()}`;

    const elArpdau = document.getElementById('medStatArpdau');
    if (elArpdau) elArpdau.innerText = `$${(a.blended_arpdau || 0).toFixed(4)}`;

    const elLtv30 = document.getElementById('medStatLtvD30');
    if (elLtv30) elLtv30.innerText = `$${(l.d30_ltv || 0).toFixed(3)}`;

    const elPayback = document.getElementById('medStatPayback');
    if (elPayback) {
      const pb = typeof l.payback_day === 'number' ? `Ngày ${l.payback_day}` : l.payback_day;
      elPayback.innerText = `${pb} • ${l.roas_d30_pct}%`;
    }

    // 2. Update Fatigue Alert
    const badgeEl = document.getElementById('medFatigueBadge');
    if (badgeEl) {
      badgeEl.innerText = f.title || '';
      badgeEl.className = `px-2 py-0.5 rounded text-xs font-bold ${f.badge_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : (f.badge_color === 'amber' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30')}`;
    }
    const adviceEl = document.getElementById('medFatigueAdvice');
    if (adviceEl) adviceEl.innerText = f.advice || '';

    // 3. Render Chart 1: Cumulative LTV Curve vs CPI
    const ltvCanvas = document.getElementById('medLtvChart');
    if (ltvCanvas) {
      const ctxLtv = ltvCanvas.getContext('2d');
      if (medLtvChartInstance) medLtvChartInstance.destroy();

      const pts = data.ltv_curve_points || [];
      const labels = pts.map(p => p.label);
      const ltvData = pts.map(p => p.cumulative_ltv);
      const cpiData = pts.map(p => p.target_cpi);

      medLtvChartInstance = new Chart(ctxLtv, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'LTV Tích Lũy ($)',
              data: ltvData,
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              borderWidth: 2.5,
              fill: true,
              tension: 0.35,
              pointRadius: 2
            },
            {
              label: `Target CPI ($${targetCpi})`,
              data: cpiData,
              borderColor: '#ef4444',
              borderDash: [5, 5],
              borderWidth: 2,
              fill: false,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#10b981', callback: v => '$' + v.toFixed(2) } }
          },
          plugins: { legend: { labels: { color: '#cbd5e1', font: { size: 11 } } } }
        }
      });
    }

    // 4. Render Chart 2: Format Revenue Share
    const formatCanvas = document.getElementById('medFormatChart');
    if (formatCanvas) {
      const ctxFormat = formatCanvas.getContext('2d');
      if (medFormatChartInstance) medFormatChartInstance.destroy();

      medFormatChartInstance = new Chart(ctxFormat, {
        type: 'doughnut',
        data: {
          labels: ['Rewarded Video', 'Interstitial Ads', 'App Open Ads', 'Banner / MREC', 'IAP In-App Purchases'],
          datasets: [{
            data: [
              revDaily.rewarded_video_usd || 100,
              revDaily.interstitial_usd || 80,
              revDaily.app_open_ads_usd || 30,
              revDaily.banner_usd || 15,
              revDaily.total_iap_revenue_usd || 90
            ],
            backgroundColor: ['#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899'],
            borderWidth: 1,
            borderColor: '#0f172a'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'right', labels: { color: '#cbd5e1', font: { size: 10 } } } }
        }
      });
    }

    lucide.createIcons();
  } catch (err) {
    console.error("Error simulating mediation:", err);
  }
}
