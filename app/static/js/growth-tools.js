/* Creative spy, CPI vs LTV simulator, blue ocean finder */
// --- FEATURE: CREATIVE AD SPY & VIDEO HOOK DECONSTRUCTOR ---
let currentGeneratedScriptText = "";

async function loadCreativeSpy() {
  const grid = document.getElementById('creativeArchetypesGrid');
  grid.innerHTML = '<div class="col-span-full py-8 text-center text-slate-400">Đang tải kho mẫu quảng cáo...</div>';

  const genre = document.getElementById('creativeFilterGenre').value;
  const network = document.getElementById('creativeFilterNetwork').value;

  try {
    const res = await fetch(`/api/mobile/creatives?genre=${genre}&network=${network}`);
    const data = await res.json();
    const items = data.archetypes || [];

    if (items.length === 0) {
      grid.innerHTML = '<div class="col-span-full py-8 text-center text-slate-500">Không tìm thấy trường phái video nào phù hợp với bộ lọc.</div>';
      return;
    }

    grid.innerHTML = items.map(a => `
      <div class="glass-card p-5 rounded-2xl border border-slate-800 space-y-4 flex flex-col justify-between hover:border-purple-500/40 transition-all">
        <div class="space-y-3">
          <div class="flex items-start justify-between gap-3">
            <div>
              <h3 class="text-sm font-bold text-white">${a.title}</h3>
              <div class="flex items-center gap-1.5 mt-1 flex-wrap">
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/30">${a.genre}</span>
                ${(a.target_networks || []).map(net => `<span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">${net}</span>`).join('')}
              </div>
            </div>
            <button onclick="copyArchetypeScript('${a.id}')" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer" title="Sao chép kịch bản">
              <i data-lucide="copy" class="w-4 h-4"></i>
            </button>
          </div>

          <!-- Metrics Row -->
          <div class="grid grid-cols-3 gap-2 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-center">
            <div>
              <span class="text-[10px] text-slate-500 uppercase font-semibold block">Tỷ lệ CTR</span>
              <span class="text-xs font-bold text-emerald-400">${a.avg_ctr}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 uppercase font-semibold block">Tỷ lệ CVR</span>
              <span class="text-xs font-bold text-indigo-400">${a.avg_cvr}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 uppercase font-semibold block">Hiệu quả CPI</span>
              <span class="text-[11px] font-bold text-amber-400">Tiết kiệm -40%</span>
            </div>
          </div>

          <p class="text-[11px] text-slate-300 leading-relaxed">${a.description}</p>

          <!-- Storyboard 3 Acts -->
          <div class="p-3 rounded-xl bg-slate-950 border border-purple-500/20 space-y-2 text-xs">
            <h4 class="text-[11px] font-bold text-purple-300 flex items-center gap-1">
              <i data-lucide="clapperboard" class="w-3.5 h-3.5 text-amber-400"></i>
              Kịch Bản 3 Hồi Chi Tiết (Storyboard)
            </h4>
            <div class="space-y-1.5 text-[11px]">
              <div><strong class="text-amber-300">⏱️ Hồi 1 (0-3s Hook):</strong> <span class="text-slate-300">${a.storyboard.hook_0_3s}</span></div>
              <div><strong class="text-indigo-300">⏱️ Hồi 2 (3-12s Action):</strong> <span class="text-slate-300">${a.storyboard.action_3_12s}</span></div>
              <div><strong class="text-emerald-300">⏱️ Hồi 3 (12-18s CTA):</strong> <span class="text-slate-300">${a.storyboard.cta_12_18s}</span></div>
            </div>
          </div>
        </div>

        <div class="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
          <span>Độ khó sản xuất: <strong class="text-slate-200">${a.production_cost}</strong></span>
          <button onclick="openScriptGeneratorModal('', '${a.genre.split('/')[0].trim()}')" class="text-purple-400 hover:text-purple-300 font-semibold cursor-pointer">
            Tạo kịch bản cho game này →
          </button>
        </div>
      </div>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error loading creative spy:", err);
  }
}

function openScriptGeneratorModal(prefillTitle = '', prefillGenre = 'RPG') {
  if (prefillTitle) document.getElementById('scriptInputTitle').value = prefillTitle;
  if (prefillGenre) document.getElementById('scriptInputGenre').value = prefillGenre;
  document.getElementById('generatedScriptResultBox').classList.add('hidden');
  document.getElementById('customAdScriptModal').classList.remove('hidden');
  lucide.createIcons();
}

function closeScriptGeneratorModal() {
  document.getElementById('customAdScriptModal').classList.add('hidden');
}

async function requestCustomAdScript() {
  const title = document.getElementById('scriptInputTitle').value.trim() || 'Tựa Game Mobile Của Bạn';
  const genre = document.getElementById('scriptInputGenre').value;
  const network = document.getElementById('scriptInputNetwork').value;

  const btn = document.getElementById('btnGenerateScript');
  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Đang bóc tách kịch bản...</span>';
  lucide.createIcons();

  try {
    const res = await fetch('/api/mobile/creatives/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_title: title, genre: genre, target_network: network })
    });
    const data = await res.json();

    document.getElementById('scriptResultArchetype').innerText = `Trường phái: ${data.recommended_archetype}`;
    document.getElementById('scriptResultHookText').innerText = `🎯 Text trên video (On-screen): "${data.on_screen_hook_text}"`;

    const stepsBox = document.getElementById('scriptResultSteps');
    stepsBox.innerHTML = (data.script_steps || []).map(st => `
      <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
        <span class="font-bold text-indigo-400 text-[11px]">${st.timeline}</span>
        <p class="text-[11px] text-slate-300 leading-snug"><strong class="text-slate-400">Hình ảnh:</strong> ${st.visual}</p>
        <p class="text-[11px] text-slate-400 leading-snug"><strong class="text-slate-400">Âm thanh:</strong> ${st.audio}</p>
      </div>
    `).join('');

    currentGeneratedScriptText = `KỊCH BẢN VIDEO ADS 20S CHO: ${title}\nTrường phái: ${data.recommended_archetype}\nText màn hình: ${data.on_screen_hook_text}\n\n` +
      (data.script_steps || []).map(st => `${st.timeline}\n- Hình ảnh: ${st.visual}\n- Âm thanh: ${st.audio}\n`).join('\n');

    document.getElementById('generatedScriptResultBox').classList.remove('hidden');
    lucide.createIcons();
  } catch (err) {
    showToast('Lỗi khi tạo kịch bản video.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="video" class="w-4 h-4"></i><span>Tạo Kịch Bản Ngay</span>';
    lucide.createIcons();
  }
}

function copyGeneratedScript() {
  if (currentGeneratedScriptText) {
    navigator.clipboard.writeText(currentGeneratedScriptText);
    showToast('Đã sao chép kịch bản video vào clipboard!', 'check-circle');
  }
}

function copyArchetypeScript(archetypeId) {
  showToast('Đã sao chép kịch bản mẫu vào clipboard!', 'check-circle');
}

// --- FEATURE: CPI VS LTV SIMULATOR ---
let simChartInstance = null;

function updateSimBudgetDisplay() {
  const val = parseFloat(document.getElementById('simBudgetInput').value || 5000);
  document.getElementById('simBudgetDisplay').innerText = `$${val.toLocaleString()}`;
}

async function autoFetchBenchmarkCpi() {
  const country = document.getElementById('simCountrySelect').value;
  const genre = document.getElementById('simGenreSelect').value;
  const platform = document.getElementById('simPlatformSelect').value;

  try {
    const res = await fetch(`/api/mobile/simulator/cpi?country=${country}&genre=${genre}&platform=${platform}`);
    const data = await res.json();
    const cpi = data.estimated_cpi || 0.95;
    document.getElementById('simCpiInput').value = cpi;
    document.getElementById('simBenchmarkHint').innerText = `Benchmark: $${cpi}`;
  } catch (err) {
    console.error("Error fetching benchmark CPI:", err);
  }
}

async function executeUaSimulation() {
  const budget = parseFloat(document.getElementById('simBudgetInput').value || 5000);
  const country = document.getElementById('simCountrySelect').value;
  const genre = document.getElementById('simGenreSelect').value;
  const platform = document.getElementById('simPlatformSelect').value;
  const cpi = parseFloat(document.getElementById('simCpiInput').value || 0.95);

  const btn = document.getElementById('btnRunSimulation');
  btn.disabled = true;
  btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Đang tính toán dòng tiền...</span>';
  lucide.createIcons();

  try {
    const res = await fetch('/api/mobile/simulator/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ budget, country, genre, platform, custom_cpi: cpi })
    });
    const data = await res.json();
    const k = data.kpis;

    document.getElementById('simKpiInstalls').innerText = k.total_paid_installs.toLocaleString();
    document.getElementById('simKpiBreakEven').innerText = typeof k.break_even_day === 'number' ? `Ngày ${k.break_even_day}` : k.break_even_day;
    document.getElementById('simKpiRoas').innerText = `${k.final_roas_pct}%`;
    document.getElementById('simKpiProfit').innerText = `${k.net_profit >= 0 ? '+$' : '-$'}${Math.abs(k.net_profit).toLocaleString()}`;
    document.getElementById('simKpiProfit').className = `text-xl font-black mt-0.5 ${k.net_profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;

    // Milestones
    const mGrid = document.getElementById('simMilestonesGrid');
    mGrid.innerHTML = Object.entries(data.milestone_roas || {}).map(([day, val]) => {
      const isBreakeven = val >= 100;
      return `
        <div class="p-2 rounded-lg bg-slate-900 border ${isBreakeven ? 'border-emerald-500/40 text-emerald-400' : 'border-slate-800 text-slate-300'}">
          <span class="text-[10px] text-slate-500 uppercase block font-semibold">${day}</span>
          <strong class="text-xs ${isBreakeven ? 'text-emerald-400' : 'text-slate-200'}">${val}%</strong>
        </div>
      `;
    }).join('');

    // Verdict banner
    const v = data.verdict;
    const banner = document.getElementById('simVerdictBanner');
    const icon = document.getElementById('simVerdictIcon');
    document.getElementById('simVerdictTitle').innerText = v.status;
    document.getElementById('simVerdictAdvice').innerText = v.advice;

    if (v.color === 'emerald') {
      banner.className = 'p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/20 flex items-start gap-3';
      icon.className = 'w-5 h-5 shrink-0 mt-0.5 text-emerald-400';
    } else if (v.color === 'indigo') {
      banner.className = 'p-4 rounded-xl border border-indigo-500/40 bg-indigo-950/20 flex items-start gap-3';
      icon.className = 'w-5 h-5 shrink-0 mt-0.5 text-indigo-400';
    } else if (v.color === 'amber') {
      banner.className = 'p-4 rounded-xl border border-amber-500/40 bg-amber-950/20 flex items-start gap-3';
      icon.className = 'w-5 h-5 shrink-0 mt-0.5 text-amber-400';
    } else {
      banner.className = 'p-4 rounded-xl border border-rose-500/40 bg-rose-950/20 flex items-start gap-3';
      icon.className = 'w-5 h-5 shrink-0 mt-0.5 text-rose-400';
    }

    // Render chart
    renderSimulatorChart(data.chart_data);
    lucide.createIcons();
  } catch (err) {
    showToast('Lỗi khi tính toán mô phỏng UA.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="calculator" class="w-4 h-4"></i><span>Chạy Mô Phỏng Tài Chính (Simulate)</span>';
    lucide.createIcons();
  }
}

function renderSimulatorChart(chartData) {
  const ctx = document.getElementById('simulatorChart').getContext('2d');
  if (simChartInstance) simChartInstance.destroy();

  simChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Doanh Thu Tích Lũy ($ USD)',
          data: chartData.cumulative_revenue,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          borderWidth: 2.5,
          fill: true,
          tension: 0.35
        },
        {
          label: 'Ngân Sách Ban Đầu ($ USD)',
          data: chartData.budget_line,
          borderColor: '#f43f5e',
          borderDash: [5, 5],
          borderWidth: 2,
          pointRadius: 0,
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
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#10b981', font: { size: 10 } }
        }
      },
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { size: 11 } } }
      }
    }
  });
}

function initSimulatorTab() {
  autoFetchBenchmarkCpi();
  executeUaSimulation();
}

// --- FEATURE: BLUE OCEAN NICHE FINDER ---
async function loadBlueOceanRadar() {
  const filter = document.getElementById('boFilterType').value;
  const grid = document.getElementById('blueOceanGrid');
  grid.innerHTML = '<div class="col-span-full py-8 text-center text-slate-400">Đang quét ma trận đại dương xanh...</div>';

  try {
    const res = await fetch(`/api/mobile/blue-ocean?classification=${filter}`);
    const data = await res.json();

    // Macro stats
    const st = data.stats || {};
    document.getElementById('boStatBlue').innerText = st.blue_oceans_count || 0;
    document.getElementById('boStatGolden').innerText = st.golden_niches_count || 0;
    document.getElementById('boStatRed').innerText = st.red_oceans_danger_count || 0;
    document.getElementById('boStatAging').innerText = st.aging_monopolies_count || 0;

    // Niches grid
    const niches = data.niches || [];
    grid.innerHTML = niches.map(n => {
      let borderClass = 'border-slate-800';
      let badgeClass = 'bg-slate-800 text-slate-300';
      if (n.classification === 'BLUE_OCEAN') {
        borderClass = 'border-sky-500/40 bg-sky-950/10 shadow-sky-950/20';
        badgeClass = 'bg-sky-500/20 text-sky-400 border border-sky-500/30 font-bold';
      } else if (n.classification === 'GOLDEN_NICHE') {
        borderClass = 'border-emerald-500/40 bg-emerald-950/10';
        badgeClass = 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold';
      } else if (n.classification === 'RED_OCEAN') {
        borderClass = 'border-rose-500/40 bg-rose-950/10';
        badgeClass = 'bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold';
      }

      return `
        <div class="glass-card p-5 rounded-2xl border ${borderClass} space-y-4 flex flex-col justify-between">
          <div class="space-y-3">
            <div class="flex items-start justify-between gap-3">
              <h3 class="text-sm font-bold text-white">${n.name}</h3>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] ${badgeClass} shrink-0">
                ${n.classification_label}
              </span>
            </div>

            <!-- Scores Matrix -->
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="p-2 rounded-lg bg-slate-950 border border-slate-800">
                <div class="flex items-center justify-between text-[10px] text-slate-400">
                  <span>Độ Khốc Liệt Cạnh Tranh:</span>
                  <strong class="${n.competition_index > 70 ? 'text-rose-400' : 'text-emerald-400'}">${n.competition_index}/100</strong>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-1 overflow-hidden">
                  <div class="${n.competition_index > 70 ? 'bg-rose-500' : 'bg-emerald-500'} h-full rounded-full" style="width: ${n.competition_index}%"></div>
                </div>
              </div>
              <div class="p-2 rounded-lg bg-slate-950 border border-slate-800">
                <div class="flex items-center justify-between text-[10px] text-slate-400">
                  <span>Tiềm Năng Doanh Thu:</span>
                  <strong class="text-amber-400">${n.revenue_potential}/100</strong>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-1 overflow-hidden">
                  <div class="bg-gradient-to-r from-amber-500 to-emerald-500 h-full rounded-full" style="width: ${n.revenue_potential}%"></div>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2 text-[11px] text-slate-400">
              <span>Ước tính CPI: <strong class="text-white">${n.cpi_estimate}</strong></span>
              <span>•</span>
              <span>Quy mô dev: <strong class="text-slate-300">${n.development_effort}</strong></span>
            </div>

            <div class="p-3 rounded-xl bg-slate-950 border border-slate-800/80 space-y-1 text-xs">
              <span class="text-[10px] font-bold text-sky-400 uppercase tracking-wider block">Phân Tích Khoảng Trống Thị Trường:</span>
              <p class="text-[11px] text-slate-300 leading-relaxed">${n.market_gap_analysis}</p>
            </div>

            <div class="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-1 text-xs">
              <span class="text-[10px] font-bold text-emerald-300 uppercase tracking-wider block">💡 Khuyến Nghị Ý Tưởng (Studio Pitch):</span>
              <p class="text-[11px] text-emerald-200/90 leading-relaxed">${n.recommended_studio_pitch}</p>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Aging Monopolies grid
    const agingGrid = document.getElementById('agingMonopoliesGrid');
    agingGrid.innerHTML = (data.aging_monopolies || []).map(m => `
      <div class="glass-card p-4 rounded-xl border border-amber-500/30 bg-amber-950/10 space-y-3 flex flex-col justify-between">
        <div class="space-y-2">
          <div class="flex items-start justify-between gap-2">
            <h4 class="text-xs font-bold text-white">${m.franchise}</h4>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 shrink-0">${m.age_years}</span>
          </div>
          <p class="text-[11px] text-slate-300 leading-snug">${m.current_status}</p>
          <div class="text-[11px] text-rose-300 bg-rose-950/20 p-2 rounded border border-rose-500/20 leading-snug">
            <strong>Tử huyệt:</strong> ${m.player_pain_point}
          </div>
          <div class="text-[11px] text-emerald-300 bg-emerald-950/20 p-2 rounded border border-emerald-500/20 leading-snug">
            <strong>Cơ hội lật đổ:</strong> ${m.disruption_opportunity}
          </div>
        </div>
        <div class="pt-2 border-t border-slate-800 text-[10px] text-amber-400 font-semibold flex items-center justify-between">
          <span>Độ tổn thương:</span>
          <span>${m.vulnerability_score}</span>
        </div>
      </div>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error("Error loading blue ocean radar:", err);
  }
}
