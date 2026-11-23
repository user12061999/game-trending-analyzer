/* Mechanics hybrid lab */
// ==========================================
// MODULE: MECHANICS HYBRID LAB (AI GAME DNA FUSION)
// ==========================================
let currentHybridFusionData = null;
let currentHybridPresetsCache = [];

async function initHybridLabTab() {
  try {
    const res = await fetch('/api/hybrid-lab/presets');
    currentHybridPresetsCache = await res.json();
  } catch (err) {
    console.error("Error loading hybrid presets:", err);
  }
  lucide.createIcons();
}

function loadHybridPreset(presetId) {
  const preset = (currentHybridPresetsCache || []).find(p => p.id === presetId);
  if (!preset) return;

  const titleA = document.getElementById('hybridTitleA');
  const genreA = document.getElementById('hybridGenreA');
  const titleB = document.getElementById('hybridTitleB');
  const genreB = document.getElementById('hybridGenreB');

  if (titleA) titleA.innerText = preset.game_a_name;
  if (genreA) genreA.innerText = preset.game_a_genre;
  if (titleB) titleB.innerText = preset.game_b_name;
  if (genreB) genreB.innerText = preset.game_b_genre;

  document.getElementById('hybridGameIdA').value = preset.game_a_name;
  document.getElementById('hybridGameIdB').value = preset.game_b_name;

  if (document.getElementById('hybridArtSelect')) {
    document.getElementById('hybridArtSelect').value = preset.art_style || 'Pixel Art 2D Retro';
  }

  triggerMechanicFusion();
}

async function searchHybridGameAutocomplete(target) {
  const input = document.getElementById(`hybridSearch${target}`);
  const dropdown = document.getElementById(`hybridDropdown${target}`);
  const q = input.value.trim();
  if (!q) {
    dropdown.classList.add('hidden');
    return;
  }

  try {
    const res = await fetch(`/api/games/search?q=${encodeURIComponent(q)}&limit=8`);
    const games = await res.json();
    if (games.length === 0) {
      dropdown.innerHTML = '<div class="p-2 text-slate-500">Không tìm thấy tựa game nào</div>';
      dropdown.classList.remove('hidden');
      return;
    }

    dropdown.innerHTML = games.map(g => `
      <div onclick="selectHybridGame('${target}', '${g.game_id}', '${escape(g.title)}', '${escape(g.genre || 'Action')}', '${g.icon_url || ''}')" class="p-2 hover:bg-slate-800 cursor-pointer flex items-center justify-between border-b border-slate-800 last:border-none">
        <div class="flex items-center gap-2 truncate">
          <img src="${g.icon_url}" class="w-6 h-6 rounded object-cover bg-slate-700" onerror="this.src='https://placehold.co/24x24/1e293b/white?text=G'">
          <span class="font-bold text-white text-xs truncate">${g.title}</span>
        </div>
        <span class="text-[10px] text-slate-400 font-mono">#${g.rank}</span>
      </div>
    `).join('');
    dropdown.classList.remove('hidden');
  } catch (err) {
    console.error("Error searching hybrid games:", err);
  }
}

function selectHybridGame(target, gameId, title, genre, iconUrl) {
  const unescapedTitle = unescape(title);
  const unescapedGenre = unescape(genre);

  document.getElementById(`hybridGameId${target}`).value = gameId;
  document.getElementById(`hybridTitle${target}`).innerText = unescapedTitle;
  document.getElementById(`hybridGenre${target}`).innerText = unescapedGenre;
  if (iconUrl) {
    document.getElementById(`hybridIcon${target}`).src = iconUrl;
  }
  document.getElementById(`hybridDropdown${target}`).classList.add('hidden');
  document.getElementById(`hybridSearch${target}`).value = unescapedTitle;
}

async function triggerMechanicFusion() {
  const gameAId = document.getElementById('hybridGameIdA').value;
  const gameBId = document.getElementById('hybridGameIdB').value;
  const ratio = document.getElementById('hybridRatioSelect').value;
  const art = document.getElementById('hybridArtSelect').value;
  const monetization = document.getElementById('hybridMonetizationSelect').value;

  const btn = document.getElementById('btnTriggerFusion');
  const loading = document.getElementById('hybridLoadingState');
  const container = document.getElementById('hybridResultContainer');

  btn.disabled = true;
  loading.classList.remove('hidden');
  container.classList.add('hidden');

  try {
    const res = await fetch('/api/hybrid-lab/fuse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_a_id: gameAId,
        game_b_id: gameBId,
        fusion_ratio: ratio,
        art_style: art,
        monetization_model: monetization
      })
    });

    const data = await res.json();
    currentHybridFusionData = data;
    renderHybridResult(data);
    container.classList.remove('hidden');
  } catch (err) {
    console.error('Error fusing mechanics:', err);
    showToast('Lỗi khi kích hoạt phản ứng lai ghép DNA.');
  } finally {
    btn.disabled = false;
    loading.classList.add('hidden');
  }
}

function renderHybridResult(data) {
  const container = document.getElementById('hybridResultContainer');
  if (!container) return;

  const m = data.dna_fusion_matrix || {};
  const ftue = data.ftue_180s || {};
  const mon = data.monetization_strategy || {};
  const loop = data.core_loop_steps || [];

  container.innerHTML = `
    <!-- 1. Concept Hero Pitch Banner -->
    <div class="glass-card p-6 rounded-2xl border border-violet-500/40 bg-gradient-to-r from-violet-950/60 via-slate-900 to-indigo-950/60 space-y-3">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <span class="px-3 py-1 rounded-full text-xs font-black bg-violet-500/20 text-violet-300 border border-violet-500/30 uppercase tracking-wider flex items-center gap-1.5">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-300"></i>
          ${data.concept_title || 'Breakthrough Hybrid Game'}
        </span>
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400 font-mono">${data.art_style}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${data.fusion_ratio}</span>
        </div>
      </div>
      <h3 class="text-xl font-extrabold text-white tracking-tight leading-snug">
        "${data.slogan || ''}"
      </h3>
      <p class="text-xs text-slate-300 leading-relaxed max-w-3xl">
        ${data.high_concept_pitch || ''}
      </p>
      <div class="pt-2 flex items-center gap-4 flex-wrap text-xs border-t border-violet-500/20">
        <div>
          <span class="text-slate-400 block text-[10px]">Tập Khách Hàng Mục Tiêu:</span>
          <span class="font-bold text-white">${data.target_audience || 'Gen-Z & Mobile Gamers'}</span>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">Mô Hình Kinh Doanh:</span>
          <span class="font-bold text-emerald-400">${data.monetization_model || 'Hybrid-Casual'}</span>
        </div>
        <div class="flex-1 min-w-[200px]">
          <span class="text-slate-400 block text-[10px]">Đại Dương Xanh (USP):</span>
          <span class="font-medium text-amber-300 text-[11px]">${data.usp_market_gap || ''}</span>
        </div>
      </div>
    </div>

    <!-- 2. DNA Cross-Breeding Matrix Cards (3 Cards) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="p-4 rounded-xl bg-slate-950/80 border border-violet-500/30 space-y-2">
        <span class="text-xs font-bold text-violet-400 flex items-center gap-1.5 uppercase tracking-wider">
          <i data-lucide="crosshair" class="w-3.5 h-3.5"></i> Kế Thừa Từ Game A
        </span>
        <p class="text-xs text-slate-300 leading-relaxed">${m.game_a_inherited || 'N/A'}</p>
      </div>
      <div class="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/30 space-y-2">
        <span class="text-xs font-bold text-indigo-400 flex items-center gap-1.5 uppercase tracking-wider">
          <i data-lucide="layers" class="w-3.5 h-3.5"></i> Kế Thừa Từ Game B
        </span>
        <p class="text-xs text-slate-300 leading-relaxed">${m.game_b_inherited || 'N/A'}</p>
      </div>
      <div class="p-4 rounded-xl bg-gradient-to-br from-violet-950/40 to-amber-950/30 border border-amber-500/40 space-y-2">
        <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5 uppercase tracking-wider">
          <i data-lucide="zap" class="w-3.5 h-3.5"></i> Cơ Chế Đột Phá (Synergy)
        </span>
        <p class="text-xs text-amber-200 leading-relaxed font-semibold">${m.synergy_mechanic || 'N/A'}</p>
      </div>
    </div>

    <!-- 3. Core Gameplay Loop 4-Steps -->
    <div class="glass-card p-5 rounded-2xl border border-slate-800 space-y-3">
      <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
        <i data-lucide="repeat" class="w-4 h-4 text-emerald-400"></i>
        Vòng Lặp Cốt Lõi 4 Bước (Core Game Loop Flow)
      </h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        ${loop.map((st, idx) => `
          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1 relative">
            <span class="text-[10px] font-mono text-emerald-400 font-bold">BƯỚC ${idx + 1}</span>
            <h5 class="text-xs font-bold text-white">${st.action}</h5>
            <p class="text-[11px] text-slate-400 leading-relaxed">${st.desc}</p>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- 4. Interactive 60FPS Playable Canvas Prototype Box -->
    <div class="glass-card p-5 rounded-2xl border border-emerald-500/40 bg-gradient-to-br from-emerald-950/20 via-slate-950 to-slate-900 space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div>
          <span class="px-2 py-0.5 rounded text-[10px] font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider">
            CANVAS 60FPS LIVE ENGINE
          </span>
          <h4 class="text-sm font-bold text-white mt-1 flex items-center gap-2">
            <i data-lucide="gamepad-2" class="w-4 h-4 text-emerald-400"></i>
            Chơi Thử Prototype Live Ngay Trên Web (Playable Prototype)
          </h4>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="if (typeof restartHybridPrototype === 'function') restartHybridPrototype();" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 border border-slate-700 cursor-pointer">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-emerald-400"></i> Chơi Lại Từ Đầu
          </button>
        </div>
      </div>

      <div class="relative rounded-2xl overflow-hidden border border-slate-800 flex justify-center bg-slate-950 p-2">
        <canvas id="hybridPrototypeCanvas" width="640" height="420" class="rounded-xl shadow-2xl max-w-full h-auto"></canvas>
      </div>

      <div class="flex items-center justify-between text-xs text-slate-400 flex-wrap gap-2 pt-1 border-t border-slate-800">
        <span class="flex items-center gap-1.5">
          <i data-lucide="keyboard" class="w-3.5 h-3.5 text-slate-300"></i>
          Điều khiển: <strong>Phím WASD / Mũi Tên</strong> để di chuyển, <strong>Chuột</strong> để ngắm đạn!
        </span>
        <span class="text-amber-300 font-semibold flex items-center gap-1">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i>
          Chạm các khối tròn màu để tích nạp MANA COMBO x2 x3!
        </span>
      </div>
    </div>

    <!-- 5. FTUE 180s & Monetization Breakdown -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- FTUE -->
      <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
        <h5 class="text-xs font-bold text-white flex items-center gap-1.5 uppercase">
          <i data-lucide="clock" class="w-4 h-4 text-cyan-400"></i> Phễu Giữ Chân 180 Giây Đầu (FTUE)
        </h5>
        <div class="space-y-1.5 text-xs">
          <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <span class="text-cyan-400 font-bold block text-[10px]">0-30s Hook:</span>
            <span class="text-slate-300">${ftue.phase_1_hook || ''}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <span class="text-emerald-400 font-bold block text-[10px]">30-90s First Win:</span>
            <span class="text-slate-300">${ftue.phase_2_first_win || ''}</span>
          </div>
          <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <span class="text-purple-400 font-bold block text-[10px]">90-180s Retention Lock:</span>
            <span class="text-slate-300">${ftue.phase_3_retention_lock || ''}</span>
          </div>
        </div>
      </div>

      <!-- Monetization -->
      <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
        <h5 class="text-xs font-bold text-white flex items-center gap-1.5 uppercase">
          <i data-lucide="gem" class="w-4 h-4 text-amber-400"></i> Chiến Lược Khai Thác Doanh Thu (Monetization)
        </h5>
        <div class="space-y-1.5 text-xs text-slate-300">
          <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <span class="text-amber-400 font-bold block text-[10px]">Rewarded Video Điểm Vàng:</span>
            <ul class="list-disc list-inside text-[11px] text-slate-300 space-y-0.5">
              ${(mon.rewarded_video_placements || []).map(p => `<li>${p}</li>`).join('')}
            </ul>
          </div>
          <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <span class="text-emerald-400 font-bold block text-[10px]">Gói Nạp & Battle Pass:</span>
            <span class="text-[11px] text-slate-300 block">${(mon.iap_high_value_packs || []).join(' • ')}</span>
            <span class="text-[10px] text-slate-400 italic block mt-0.5">${mon.battle_pass_concept || ''}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 6. Unity C# Export & GDD Download Row -->
    <div class="glass-card p-4 rounded-xl border border-slate-800 flex items-center justify-between flex-wrap gap-3">
      <div>
        <h5 class="text-xs font-bold text-white">Sẵn Sàng Triển Khai Vào Dự Án Game Thực Tế?</h5>
        <p class="text-[11px] text-slate-400">Tải mã nguồn Unity Controller C# hoặc lưu tài liệu thiết kế GDD hoàn chỉnh</p>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="copyHybridUnityCode()" class="px-3 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-md transition-all cursor-pointer">
          <i data-lucide="copy" class="w-3.5 h-3.5"></i> Sao Chép C# Code
        </button>
        <button onclick="downloadHybridGddMarkdown()" class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 border border-slate-700 transition-all cursor-pointer">
          <i data-lucide="download" class="w-3.5 h-3.5 text-cyan-400"></i> Tải GDD (.md)
        </button>
      </div>
    </div>
  `;

  lucide.createIcons();

  // Dynamically run the executable 60FPS Canvas game script
  if (data.playable_canvas_code) {
    try {
      const oldScript = document.getElementById('dynamicHybridCanvasScript');
      if (oldScript) oldScript.remove();

      const scriptEl = document.createElement('script');
      scriptEl.id = 'dynamicHybridCanvasScript';
      scriptEl.textContent = data.playable_canvas_code;
      document.body.appendChild(scriptEl);
    } catch (e) {
      console.error("Error launching hybrid canvas engine:", e);
    }
  }
}

function copyHybridUnityCode() {
  if (!currentHybridFusionData || !currentHybridFusionData.unity_starter_code) {
    showToast('Chưa có mã nguồn C# để sao chép.');
    return;
  }
  navigator.clipboard.writeText(currentHybridFusionData.unity_starter_code).then(() => {
    showToast('Đã sao chép mã nguồn Unity C# vào clipboard!');
  });
}

function downloadHybridGddMarkdown() {
  if (!currentHybridFusionData) {
    showToast('Chưa có dữ liệu để xuất file.');
    return;
  }
  const title = (currentHybridFusionData.concept_title || 'HybridGame').replace(/[^a-zA-Z0-9_-]/g, '_');
  const lines = [
    `# ${currentHybridFusionData.concept_title}`,
    `> ${currentHybridFusionData.slogan}\n`,
    `## 1. High Concept Pitch`,
    `${currentHybridFusionData.high_concept_pitch}\n`,
    `## 2. Target Audience & USP`,
    `- **Đối tượng**: ${currentHybridFusionData.target_audience}`,
    `- **USP**: ${currentHybridFusionData.usp_market_gap}\n`,
    `## 3. DNA Fusion Matrix`,
    `- **Kế thừa từ Game A**: ${currentHybridFusionData.dna_fusion_matrix?.game_a_inherited}`,
    `- **Kế thừa từ Game B**: ${currentHybridFusionData.dna_fusion_matrix?.game_b_inherited}`,
    `- **Cơ chế đột phá**: ${currentHybridFusionData.dna_fusion_matrix?.synergy_mechanic}\n`,
    `## 4. First-Time User Experience (180s)`,
    `- **0-30s**: ${currentHybridFusionData.ftue_180s?.phase_1_hook}`,
    `- **30-90s**: ${currentHybridFusionData.ftue_180s?.phase_2_first_win}`,
    `- **90-180s**: ${currentHybridFusionData.ftue_180s?.phase_3_retention_lock}\n`,
    `## 5. Unity Starter C# Code`,
    "```csharp",
    currentHybridFusionData.unity_starter_code || "// No C# code",
    "```"
  ].join('\n');

  const blob = new Blob([lines], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title}_GDD.md`;
  document.body.appendChild(a);
  a.click();
  showToast('Đã tải tài liệu GDD lai ghép (.md)!');
}
