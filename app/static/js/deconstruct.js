/* Game modal: AI gameplay deconstruction, prototype canvas, moodboard, video script, GDD engine */
// ==========================================
// MODAL AUTOMATIC GAMEPLAY DECONSTRUCTION & GDD ENGINE
// ==========================================
let modalDeconstructCache = {};
let modalGddCache = {};
let currentModalDeconstructData = null;
let currentModalGddData = null;

let currentSelectedUnityScript = 'PlayerController.cs';

async function loadModalDeconstruct(forceReload = false, useAiLlm = false, customKey = null) {
  const container = document.getElementById('modalDeconstructContainer');
  if (!container) return;
  const gameId = currentActiveModalGameId;
  const title = currentActiveModalGameTitle || 'Game';

  if (!forceReload && !useAiLlm && modalDeconstructCache[gameId]) {
    currentModalDeconstructData = modalDeconstructCache[gameId];
    renderModalDeconstructResults(currentModalDeconstructData);
    return;
  }

  if (useAiLlm) {
    showToast(`✨ Đang kích hoạt AI phân tích sâu gameplay & cốt truyện cho "${title}"...`, 'sparkles');
  }

  container.innerHTML = `
    <div class="p-12 text-center space-y-4 rounded-2xl bg-slate-950/90 border border-slate-800 shadow-2xl">
      <div class="inline-block p-4 rounded-2xl ${useAiLlm ? 'bg-amber-500/20 border border-amber-500/40 text-amber-300' : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'} animate-pulse">
        <i data-lucide="${useAiLlm ? 'sparkles' : 'cpu'}" class="w-10 h-10 ${useAiLlm ? 'animate-bounce' : 'animate-spin'}"></i>
      </div>
      <div class="space-y-1">
        <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${useAiLlm ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'}">
          ${useAiLlm ? '✨ ĐANG PHÂN TÍCH SÂU BẰNG AI (GEMINI ENGINE)' : '⚙️ ĐANG BÓC TÁCH BLUEPRINT 1:1'}
        </span>
        <h4 class="text-base font-bold text-white">${useAiLlm ? 'AI Đang Bóc Tách Kịch Bản, Cơ Chế & Vật Lý Riêng Cho' : 'Đang Bóc Tách Gameplay Chuẩn Hoá Cho'} "${title}"...</h4>
      </div>
      <p class="text-xs text-slate-400 max-w-lg mx-auto leading-relaxed">
        Hệ thống đang trích xuất: Động học Kinematics 1:1, Ma trận Combo kỹ năng, Kịch bản Pacing 10 giai đoạn kèm Tension Score, Cốt truyện 3 hồi và 5 bộ mã nguồn Unity C#...
      </p>
      <div class="w-48 h-1.5 mx-auto bg-slate-800 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full animate-pulse" style="width: 85%"></div>
      </div>
    </div>
  `;
  lucide.createIcons();

  try {
    const storedKey = customKey || localStorage.getItem('gemini_api_key') || '';
    
    // Add a slight minimum visible delay when using AI so the user clearly feels the processing
    const startTime = Date.now();
    const res = await fetch('/api/deconstruct/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_title: title,
        platform: currentActiveModalGamePlatform || 'PC / Mobile',
        genre_hint: currentActiveModalGameGenre || 'Action',
        store_url: currentActiveModalGameStoreUrl || '',
        raw_description: currentActiveModalGameDesc || '',
        use_ai_llm: useAiLlm,
        custom_api_key: storedKey
      })
    });

    if (useAiLlm) {
      const elapsed = Date.now() - startTime;
      if (elapsed < 800) {
        await new Promise(r => setTimeout(r, 800 - elapsed));
      }
    }

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    modalDeconstructCache[gameId] = data;
    currentModalDeconstructData = data;
    renderModalDeconstructResults(data);
    if (useAiLlm) {
      showToast(`Đã hoàn tất phân tích sâu bằng AI cho "${title}"!`, 'check-circle');
    }
  } catch (err) {
    container.innerHTML = `
      <div class="p-8 text-center text-rose-400 space-y-2 rounded-2xl bg-slate-950 border border-slate-800">
        <i data-lucide="alert-circle" class="w-8 h-8 mx-auto"></i>
        <p class="font-bold text-xs">Lỗi khi phân tích bóc tách: ${err.message}</p>
        <button onclick="loadModalDeconstruct(true)" class="px-4 py-2 rounded-lg bg-slate-800 text-white text-xs hover:bg-slate-700 cursor-pointer">Thử Lại</button>
      </div>
    `;
    lucide.createIcons();
  }
}

async function saveAndRunGeminiAiAnalysis() {
  const input = document.getElementById('modalGeminiApiKeyInput');
  const key = input ? input.value.trim() : '';
  if (!key) {
    showToast('Vui lòng nhập khóa Gemini API Key trước khi áp dụng.', 'alert-circle');
    return;
  }
  localStorage.setItem('gemini_api_key', key);
  try {
    await fetch('/api/ai/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gemini_api_key: key })
    });
  } catch (e) {
    console.warn('Failed to save to server config:', e);
  }
  showToast('Đã lưu API Key! Đang gửi yêu cầu phân tích trực tiếp tới Google Gemini...', 'sparkles');
  loadModalDeconstruct(true, true, key);
}

function reloadModalDeconstruct() {
  loadModalDeconstruct(true);
}

function selectUnityScriptTab(fileName) {
  currentSelectedUnityScript = fileName;
  if (!currentModalDeconstructData) return;
  const scripts = currentModalDeconstructData.unity_scripts || {
    'PlayerController.cs': currentModalDeconstructData.unity_starter_code || '// Code'
  };
  const code = scripts[fileName] || '// Không tìm thấy mã nguồn file này';
  const display = document.getElementById('modalUnityCodeDisplay');
  if (display) {
    display.innerHTML = `<code>${code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code>`;
  }

  const tabs = ['PlayerController.cs', 'WeaponSystem.cs', 'EnemyAI.cs', 'WaveDirector.cs', 'GameEconomyManager.cs'];
  tabs.forEach(t => {
    const btn = document.getElementById(`scriptTabBtn-${t.replace('.', '_')}`);
    if (btn) {
      if (t === fileName) {
        btn.className = "px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white shadow-md shadow-emerald-600/30 cursor-pointer border border-emerald-500";
      } else {
        btn.className = "px-3 py-1 rounded-lg text-xs font-medium bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 cursor-pointer";
      }
    }
  });
}

function copyCurrentUnityScript() {
  if (!currentModalDeconstructData) return;
  const scripts = currentModalDeconstructData.unity_scripts || {
    'PlayerController.cs': currentModalDeconstructData.unity_starter_code || ''
  };
  const code = scripts[currentSelectedUnityScript] || currentModalDeconstructData.unity_starter_code || '';
  navigator.clipboard.writeText(code).then(() => {
    showToast(`Đã sao chép mã nguồn ${currentSelectedUnityScript}!`);
  });
}

function copyAllUnityScripts() {
  if (!currentModalDeconstructData) return;
  const scripts = currentModalDeconstructData.unity_scripts || {};
  let allCode = `// TRỌN BỘ 5 FILE C# UNITY STARTER - ${currentModalDeconstructData.title}\n// Xuất bởi Game Trending Analyzer 2.0\n\n`;
  for (const [fname, fcode] of Object.entries(scripts)) {
    allCode += `// ==========================================\n// FILE: ${fname}\n// ==========================================\n${fcode}\n\n`;
  }
  navigator.clipboard.writeText(allCode).then(() => {
    showToast('Đã sao chép trọn bộ 5 file C# Unity vào clipboard!');
  });
}

function renderModalDeconstructResults(data) {
  const container = document.getElementById('modalDeconstructContainer');
  if (!container) return;

  const pAndM = data.physics_and_movement || {};
  const fsm = data.core_state_machine || {};
  const pacing = data.pacing_script || [];
  const narrative = data.narrative_and_quest_script || {};
  const assets = data.asset_checklist || {};
  const twists = data.clone_with_a_twist || [];
  const unityScripts = data.unity_scripts || {
    'PlayerController.cs': data.unity_starter_code || '// Code'
  };

  const playerFsm = fsm.player_fsm || (Array.isArray(fsm) ? fsm : []);
  const enemyFsm = fsm.enemy_director_fsm || [];
  const charProfiles = narrative.character_profiles || {};
  const dialogues = narrative.scripted_dialogues || {};
  const quests = narrative.quest_hierarchy || {};

  currentSelectedUnityScript = 'PlayerController.cs';
  const initialCode = (unityScripts['PlayerController.cs'] || data.unity_starter_code || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  container.innerHTML = `
    <!-- Header Archetype & Badge Banner -->
    <div class="glass-card p-4 rounded-xl border ${data.is_ai_enhanced ? 'border-amber-500/50 bg-gradient-to-r from-amber-950/30 via-slate-950 to-slate-950' : 'border-slate-800 bg-slate-950/70'} flex items-center justify-between flex-wrap gap-2">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="px-3 py-1 rounded-full text-xs font-black bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 text-emerald-300 border border-emerald-500/40 uppercase tracking-wider flex items-center gap-1.5">
          <i data-lucide="tag" class="w-3.5 h-3.5"></i> ${data.archetype_name || data.genre || 'Gameplay Archetype'}
        </span>
        ${data.is_ai_enhanced ? `
          <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1.5 shadow-md shadow-amber-500/20 animate-pulse">
            <i data-lucide="sparkles" class="w-3.5 h-3.5 text-yellow-300"></i> ${data.is_ai_enhanced ? 'AI ENHANCED' : 'KHÔNG DÙNG LLM'}: ${data.ai_source || 'Gemini'}
          </span>
        ` : ''}
      </div>
      <div class="flex items-center gap-2 flex-wrap text-xs">
        <div class="flex items-center gap-1.5 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
          <i data-lucide="key" class="w-3 h-3 text-amber-400"></i>
          <input type="password" id="modalGeminiApiKeyInput" placeholder="Google Gemini API Key..." value="${localStorage.getItem('gemini_api_key') || ''}" class="bg-transparent text-[11px] text-white focus:outline-none w-36">
          <button onclick="saveAndRunGeminiAiAnalysis()" class="px-2 py-0.5 rounded bg-amber-600 hover:bg-amber-500 text-white text-[10px] font-bold cursor-pointer">
            Lưu & Gọi Gemini
          </button>
        </div>
        <span class="text-xs text-slate-400 font-medium">Bản thiết kế kỹ thuật phục vụ Clone & Nâng Cấp Gameplay 1:1</span>
      </div>
    </div>

    <!-- 1. Core Mechanics, 1:1 Physics & Game Feel Spec -->
    <div class="space-y-3">
      <h4 class="text-xs font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
        <i data-lucide="crosshair" class="w-4 h-4 text-emerald-400"></i>
        1. Cơ Chế Điều Khiển, Vật Lý 1:1 & Game Feel (Kinematics & Tuning)
      </h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
          <span class="text-slate-400 font-semibold block text-[11px] flex items-center gap-1">
            <i data-lucide="video" class="w-3.5 h-3.5 text-indigo-400"></i> Góc Nhìn Camera:
          </span>
          <p class="text-slate-200 font-medium text-[11px] leading-relaxed">${data.camera_perspective || 'N/A'}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
          <span class="text-slate-400 font-semibold block text-[11px] flex items-center gap-1">
            <i data-lucide="gamepad" class="w-3.5 h-3.5 text-teal-400"></i> Phương Thức Điều Khiển:
          </span>
          <p class="text-slate-200 font-medium text-[11px] leading-relaxed">${data.control_scheme || 'N/A'}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
          <span class="text-slate-400 font-semibold block text-[11px] flex items-center gap-1">
            <i data-lucide="zap" class="w-3.5 h-3.5 text-amber-400"></i> Tốc Độ & Gia Tốc:
          </span>
          <p class="text-slate-200 font-medium text-[11px] leading-relaxed">${pAndM.movement_speed || 'N/A'}</p>
          <p class="text-slate-400 text-[10px]">${pAndM.acceleration_and_deceleration || ''}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
          <span class="text-slate-400 font-semibold block text-[11px] flex items-center gap-1">
            <i data-lucide="shield" class="w-3.5 h-3.5 text-emerald-400"></i> Va Chạm & Hitbox:
          </span>
          <p class="text-slate-200 font-medium text-[11px] leading-relaxed">${pAndM.collision_and_hitbox || pAndM.hitbox_rules || 'N/A'}</p>
          <p class="text-slate-400 text-[10px]">${pAndM.coyote_and_buffering || ''}</p>
        </div>
      </div>

      <!-- Game Feel & Damage Formula Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
          <span class="text-amber-400 font-bold block text-[11px] flex items-center gap-1.5">
            <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i> Độ Khựng Đòn Đánh & Game Feel (Hit-Stop & Shake):
          </span>
          <p class="text-slate-200 text-[11px] leading-relaxed">${pAndM.game_feel_juice || 'Hit-stop 45ms, camera shake trauma 0.15s'}</p>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
          <span class="text-cyan-400 font-bold block text-[11px] flex items-center gap-1.5">
            <i data-lucide="calculator" class="w-3.5 h-3.5 text-cyan-400"></i> Công Thức Tính Sát Thương Thực Tế:
          </span>
          <p class="text-cyan-200 font-mono text-[11px] leading-relaxed p-1.5 rounded bg-slate-900 border border-slate-800">${pAndM.damage_formula || 'Damage = (Attack * SkillMult - Defense * 0.3) * Crit'}</p>
        </div>
      </div>

      <!-- Synergies Matrix -->
      ${(pAndM.combat_synergies && pAndM.combat_synergies.length > 0) ? `
        <div class="p-3.5 rounded-xl bg-gradient-to-r from-purple-950/30 via-slate-950 to-slate-950 border border-purple-500/30 space-y-2">
          <span class="text-xs font-bold text-purple-300 flex items-center gap-1.5">
            <i data-lucide="layers" class="w-4 h-4 text-purple-400"></i> Tổ Hợp Kỹ Năng & Công Thức Tiến Hóa Vũ Khí (Combat Synergies):
          </span>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px]">
            ${pAndM.combat_synergies.map(syn => `
              <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 text-slate-200 space-y-1">
                <span class="text-purple-300 font-bold block flex items-center gap-1">⚡ Combo</span>
                <p class="text-slate-300 leading-relaxed">${syn}</p>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}
    </div>

    <!-- 2. Dual Finite State Machine (FSM) -->
    <div class="space-y-3">
      <h4 class="text-xs font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
        <i data-lucide="git-branch" class="w-4 h-4 text-cyan-400"></i>
        2. Hệ Thống Máy Trạng Thái FSM Kép (Player FSM & Enemy Director FSM)
      </h4>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Player FSM Table -->
        <div class="space-y-2">
          <span class="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
            <i data-lucide="user" class="w-3.5 h-3.5"></i> FSM Nhân Vật Chính (Player State Machine):
          </span>
          <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider font-bold">
                <tr>
                  <th class="px-3 py-2">Trạng Thái</th>
                  <th class="px-3 py-2">Kích Hoạt (Trigger)</th>
                  <th class="px-3 py-2">Hành Vi & Thoát</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/80 text-slate-300">
                ${playerFsm.map(s => `
                  <tr class="hover:bg-slate-900/40">
                    <td class="px-3 py-2 font-bold text-emerald-400 font-mono text-[11px] whitespace-nowrap">${s.state}</td>
                    <td class="px-3 py-2 text-slate-300 text-[11px]">${s.trigger}</td>
                    <td class="px-3 py-2 text-slate-200 text-[11px]">
                      ${s.action}
                      ${s.exit_condition ? `<div class="text-[10px] text-slate-400 italic mt-0.5">Thoát: ${s.exit_condition}</div>` : ''}
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <!-- Enemy FSM Table -->
        <div class="space-y-2">
          <span class="text-[11px] font-bold text-rose-400 flex items-center gap-1">
            <i data-lucide="skull" class="w-3.5 h-3.5"></i> FSM Đạo Diễn AI Quái Vật (Enemy Director FSM):
          </span>
          <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider font-bold">
                <tr>
                  <th class="px-3 py-2">Trạng Thái</th>
                  <th class="px-3 py-2">Điều Kiện (Trigger)</th>
                  <th class="px-3 py-2">Hành Động Của Quái</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/80 text-slate-300">
                ${(enemyFsm.length > 0 ? enemyFsm : [
                  { state: 'SPAWN_OUT_OF_BOUNDS', trigger: 'Timer đếm ngược', action: 'Sinh quái ngoài viền camera' },
                  { state: 'FLOCKING_CHASE', trigger: 'Quái còn sống', action: 'Đuổi theo Player và tách bầy' },
                  { state: 'DEATH_DROP', trigger: 'HP về 0', action: 'Rớt ngọc và cộng điểm tiến trình' }
                ]).map(s => `
                  <tr class="hover:bg-slate-900/40">
                    <td class="px-3 py-2 font-bold text-rose-400 font-mono text-[11px] whitespace-nowrap">${s.state}</td>
                    <td class="px-3 py-2 text-slate-300 text-[11px]">${s.trigger}</td>
                    <td class="px-3 py-2 text-slate-200 text-[11px]">${s.action}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Minute-by-Minute Wave Pacing Script & Tension Arc -->
    <div class="space-y-3">
      <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-800 pb-2">
        <h4 class="text-xs font-bold text-white flex items-center gap-2">
          <i data-lucide="timer" class="w-4 h-4 text-amber-400"></i>
          3. Kịch Bản Nhịp Độ Màn Chơi 8-10 Giai Đoạn (Level Pacing & Tension Curve)
        </h4>
        <span class="text-[11px] text-amber-400/90 font-medium">Đoạn cong cảm xúc: Nghỉ ngơi ➔ Áp lực ➔ Cao trào Boss ➔ Thỏa mãn</span>
      </div>
      <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider font-bold">
            <tr>
              <th class="px-3 py-2">Thời Gian</th>
              <th class="px-3 py-2">Giai Đoạn / Wave</th>
              <th class="px-3 py-2">Căng Thẳng (Tension)</th>
              <th class="px-3 py-2">Mật Độ</th>
              <th class="px-3 py-2">Mục Tiêu & Tâm Lý Người Chơi</th>
              <th class="px-3 py-2">Cơ Chế Rủi Ro & Monetization</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-300">
            ${pacing.map(p => {
              const score = p.tension_score || 5;
              let barColor = 'bg-emerald-500';
              if (score >= 9) barColor = 'bg-rose-500';
              else if (score >= 7) barColor = 'bg-orange-500';
              else if (score >= 4) barColor = 'bg-amber-500';

              return `
                <tr class="hover:bg-slate-900/50">
                  <td class="px-3 py-2.5 font-bold text-amber-400 whitespace-nowrap text-[11px]">${p.timestamp}</td>
                  <td class="px-3 py-2.5 text-white font-semibold text-[11px] whitespace-nowrap">${p.wave_name}</td>
                  <td class="px-3 py-2.5 whitespace-nowrap">
                    <div class="flex items-center gap-1.5">
                      <div class="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div class="h-full ${barColor}" style="width: ${score * 10}%;"></div>
                      </div>
                      <span class="font-bold text-[10px] ${score >= 8 ? 'text-rose-400' : 'text-slate-300'}">${score}/10</span>
                    </div>
                  </td>
                  <td class="px-3 py-2.5 text-slate-300 text-[11px] whitespace-nowrap">${p.density}</td>
                  <td class="px-3 py-2.5 text-slate-200 text-[11px]">
                    <div>${p.objective}</div>
                    ${p.player_emotion ? `<div class="text-[10px] text-cyan-400/80 italic mt-0.5">Tâm lý: ${p.player_emotion}</div>` : ''}
                  </td>
                  <td class="px-3 py-2.5 text-slate-300 text-[11px]">${p.risk_and_monetization || p.difficulty || 'Bình thường'}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>

    <!-- 4. Deep Narrative, 3-Act Dialogues & Quest Architecture -->
    <div class="space-y-3">
      <h4 class="text-xs font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
        <i data-lucide="book-open" class="w-4 h-4 text-purple-400"></i>
        4. Kịch Bản Cốt Truyện, Hồ Sơ Nhân Vật & Cây Nhiệm Vụ 3 Tầng
      </h4>

      <!-- World Premise -->
      <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
        <span class="text-purple-400 font-bold block text-[11px] flex items-center gap-1">
          <i data-lucide="globe" class="w-3.5 h-3.5"></i> Bối Cảnh & Xung Đột Thế Giới:
        </span>
        <p class="text-slate-200 leading-relaxed text-[11px]">${narrative.premise || 'N/A'}</p>
      </div>

      <!-- Character Profiles Grid -->
      ${Object.keys(charProfiles).length > 0 ? `
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          ${Object.entries(charProfiles).map(([key, prof]) => `
            <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-white">${prof.name}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  ${prof.role}
                </span>
              </div>
              <p class="text-[11px] text-slate-400">${prof.archetype || ''}</p>
              <blockquote class="italic text-slate-300 border-l-2 border-purple-500 pl-2 text-[11px]">
                "${prof.battle_cry || prof.villain_philosophy || prof.guidance_tone || 'Sẵn sàng chiến đấu!'}"
              </blockquote>
            </div>
          `).join('')}
        </div>
      ` : ''}

      <!-- Scripted Dialogues 3-Acts -->
      ${Object.keys(dialogues).length > 0 ? `
        <div class="space-y-2 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
          <span class="text-emerald-400 font-bold block text-[11px] flex items-center gap-1.5">
            <i data-lucide="message-square" class="w-3.5 h-3.5 text-emerald-400"></i> Kịch Bản Thoại Chi Tiết 3 Hồi (Scripted Dialogue):
          </span>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">
            ${Object.entries(dialogues).map(([actKey, dial]) => `
              <div class="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                <span class="font-bold text-emerald-300 block text-[10px] uppercase tracking-wider">${actKey.replace('_', ' ')}</span>
                <pre class="font-sans text-slate-300 text-[11px] whitespace-pre-wrap leading-relaxed">${dial}</pre>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- 3-Tier Quest Architecture -->
      ${Object.keys(quests).length > 0 ? `
        <div class="space-y-2 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
          <span class="text-amber-400 font-bold block text-[11px] flex items-center gap-1.5">
            <i data-lucide="target" class="w-3.5 h-3.5 text-amber-400"></i> Hệ Thống Nhiệm Vụ 3 Tầng Giữ Chân Người Chơi (Quest Architecture):
          </span>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
            ${Object.entries(quests).map(([qType, qList]) => `
              <div class="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1.5">
                <span class="font-bold text-amber-300 block text-[10px] uppercase tracking-wider">${qType.replace('_', ' ')}</span>
                <div class="space-y-1.5">
                  ${(qList || []).map(q => `
                    <div class="border-b border-slate-800/60 pb-1 text-[11px]">
                      <strong class="text-slate-200 block">${q.title}</strong>
                      <span class="text-slate-400 block text-[10px]">${q.desc}</span>
                      <span class="text-emerald-400 text-[10px] font-semibold">🎁 Thưởng: ${q.reward}</span>
                    </div>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Audio Choreography -->
      <div class="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
        <i data-lucide="volume-2" class="w-4 h-4 text-cyan-400 shrink-0"></i>
        <div>
          <strong class="text-cyan-400 text-[11px]">Chỉ Dẫn m Thanh & Nhạc Nền:</strong>
          <span class="text-slate-300 text-[11px] ml-1">${narrative.gameplay_audio_cues || 'm thanh hit-stop, âm báo lên cấp và BGM cao trào.'}</span>
        </div>
      </div>
    </div>

    <!-- 5. Multi-Script Unity Starter Code Suite -->
    <div class="space-y-2.5">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2 flex-wrap gap-2">
        <div class="space-y-0.5">
          <h4 class="text-xs font-bold text-white flex items-center gap-2">
            <i data-lucide="code" class="w-4 h-4 text-emerald-400"></i>
            5. Trọn Bộ 5 File Mã Nguồn C# Unity Starter Suite (Architecture Studio)
          </h4>
          <p class="text-[10px] text-slate-400">Kiến trúc Component-Based sạch sẽ, phân tách rõ ràng Controllers, Weapons, AI, Wave Director & Economy</p>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button onclick="copyCurrentUnityScript()" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold border border-slate-700 flex items-center gap-1 cursor-pointer">
            <i data-lucide="copy" class="w-3 h-3 text-emerald-400"></i> Sao Chép File Này
          </button>
          <button onclick="copyAllUnityScripts()" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold border border-slate-700 flex items-center gap-1 cursor-pointer">
            <i data-lucide="copy-check" class="w-3 h-3 text-cyan-400"></i> Sao Chép Cả 5 File
          </button>
          <button onclick="downloadUnityZipPackage()" class="px-2.5 py-1 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-[11px] font-bold flex items-center gap-1 shadow-md shadow-purple-600/30 cursor-pointer">
            <i data-lucide="package" class="w-3.5 h-3.5"></i> Tải Full Project (.zip)
          </button>
        </div>
      </div>

      <!-- Script Tabs Navigation -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
        ${Object.keys(unityScripts).map(fname => `
          <button id="scriptTabBtn-${fname.replace('.', '_')}" onclick="selectUnityScriptTab('${fname}')" class="px-3 py-1 rounded-lg text-xs font-semibold cursor-pointer transition-all ${fname === 'PlayerController.cs' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30 border border-emerald-500 font-bold' : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'}">
            ${fname}
          </button>
        `).join('')}
      </div>

      <!-- Code Display Container -->
      <div class="relative rounded-xl overflow-hidden border border-slate-800 bg-slate-950 p-4">
        <pre id="modalUnityCodeDisplay" class="font-mono text-[11px] text-emerald-300 leading-relaxed overflow-x-auto max-h-80 scrollbar-thin"><code>${initialCode}</code></pre>
      </div>
    </div>

    <!-- 6. Asset Checklist & Clone With A Twist -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
      <div class="space-y-2.5 p-3.5 rounded-xl bg-slate-950/70 border border-slate-800">
        <h4 class="text-xs font-bold text-white flex items-center gap-1.5 border-b border-slate-800 pb-1.5">
          <i data-lucide="layers" class="w-3.5 h-3.5 text-blue-400"></i>
          6. Danh Mục Tài Nguyên Sản Xuất (Asset Checklist)
        </h4>
        <div class="space-y-2 text-xs text-slate-300">
          <div>
            <span class="text-slate-400 font-semibold block text-[11px] mb-1">Sprites & 3D Models:</span>
            <ul class="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
              ${(assets.sprites || []).map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
          <div>
            <span class="text-slate-400 font-semibold block text-[11px] mb-1 mt-1.5">UI Canvas & HUD:</span>
            <ul class="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
              ${(assets.ui_canvas || []).map(u => `<li>${u}</li>`).join('')}
            </ul>
          </div>
          <div>
            <span class="text-slate-400 font-semibold block text-[11px] mb-1 mt-1.5">SFX & BGM:</span>
            <ul class="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
              ${(assets.sfx_list || []).map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
        </div>
      </div>

      <div class="space-y-2.5 p-3.5 rounded-xl bg-slate-950/70 border border-slate-800">
        <h4 class="text-xs font-bold text-white flex items-center gap-1.5 border-b border-slate-800 pb-1.5">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i>
          7. Công Thức "Clone With A Twist" (Cải Tiến Vượt Trội Bản Gốc)
        </h4>
        <div class="space-y-2 text-xs">
          ${twists.map(t => `
            <div class="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 space-y-0.5">
              <span class="font-bold text-amber-300 flex items-center gap-1 text-[11px]">
                <i data-lucide="zap" class="w-3 h-3"></i> ${t.idea}
              </span>
              <p class="text-slate-300 text-[11px] leading-relaxed">${t.why}</p>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- 8. REA (Reverse Engineer Anything - morluto/rea) Binary & Decompilation Dossier -->
    ${data.rea_dossier ? `
      <div class="p-4 rounded-xl bg-gradient-to-b from-indigo-950/30 via-slate-950 to-slate-950 border border-indigo-500/30 space-y-3.5">
        <div class="flex items-center justify-between flex-wrap gap-2 border-b border-indigo-900/40 pb-2.5">
          <div class="flex items-center gap-2">
            <span class="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/40">
              <i data-lucide="cpu" class="w-4 h-4"></i>
            </span>
            <div>
              <h4 class="text-xs font-bold text-white flex items-center gap-1.5">
                8. Báo Cáo Reverse Engineering Binary & Mã Máy (Tích hợp morluto/rea)
              </h4>
              <p class="text-[10px] text-slate-400">
                Bóc tách sâu .NET Assemblies, Android APK Dex & Ký hiệu bộ nhớ với <a href="https://github.com/morluto/rea" target="_blank" class="text-indigo-400 underline hover:text-indigo-300">morluto/rea v6.8.0</a>
              </p>
            </div>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
              <i data-lucide="check-circle" class="w-3 h-3 text-emerald-400"></i> REA Engine Sẵn Sàng (175 Tools)
            </span>
            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-purple-500/10 text-purple-300 border border-purple-500/30">
              ${data.rea_dossier.engine_fingerprint || 'Unity Engine IL2CPP'}
            </span>
          </div>
        </div>

        <!-- REA 4-Card Analysis Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-3 text-xs">
          <!-- Card A: Decompiled Classes & Methods -->
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span class="text-xs font-bold text-indigo-300 flex items-center gap-1.5">
              <i data-lucide="code-2" class="w-3.5 h-3.5 text-indigo-400"></i> Ký Hiệu Lớp & Hàm Trích Xuất (Assembly Classes):
            </span>
            <div class="space-y-2 max-h-56 overflow-y-auto pr-1 scrollbar-thin">
              ${(data.rea_dossier.decompiled_classes || []).map(cls => `
                <div class="p-2 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
                  <div class="flex items-center justify-between">
                    <span class="font-mono font-bold text-white text-[11px]">${cls.class_name}</span>
                    <span class="text-[9px] text-slate-500 font-mono">${cls.namespace}</span>
                  </div>
                  <div class="space-y-0.5 text-[10px] font-mono text-slate-300">
                    ${cls.methods.map(m => `
                      <div class="text-slate-400">
                        <span class="text-indigo-400">${m.visibility}</span> <span class="text-emerald-400">${m.return_type}</span> <span class="text-slate-200">${m.name}</span>
                        ${m.desc ? `<span class="text-[9px] text-slate-500 italic block font-sans">${m.desc}</span>` : ''}
                      </div>
                    `).join('')}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Card B: SDKs & Engine Footprint -->
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span class="text-xs font-bold text-teal-300 flex items-center gap-1.5">
              <i data-lucide="layers" class="w-3.5 h-3.5 text-teal-400"></i> Thư Viện SDK & Công Nghệ Ngầm (Footprint):
            </span>
            <div class="space-y-1.5 max-h-56 overflow-y-auto pr-1 scrollbar-thin">
              ${(data.rea_dossier.detected_sdks || []).map(sdk => `
                <div class="p-2 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between text-[11px]">
                  <div>
                    <span class="font-bold text-white block">${sdk.name}</span>
                    <span class="text-[10px] text-slate-400">${sdk.purpose}</span>
                  </div>
                  <span class="px-2 py-0.5 rounded text-[9px] font-semibold bg-slate-800 text-slate-300 border border-slate-700 whitespace-nowrap">
                    ${sdk.category}
                  </span>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Card C: Internal Constants & Balancing Floats -->
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span class="text-xs font-bold text-amber-300 flex items-center gap-1.5">
              <i data-lucide="hash" class="w-3.5 h-3.5 text-amber-400"></i> Hằng Số Cân Bằng Gameplay Nhúng Trong Binary:
            </span>
            <div class="space-y-1 text-[11px]">
              ${(data.rea_dossier.internal_constants || []).map(c => `
                <div class="p-1.5 rounded bg-slate-900/80 border border-slate-800/80 flex items-center justify-between gap-2">
                  <span class="font-mono text-amber-300 text-[10px]">${c.name}</span>
                  <span class="font-mono font-bold text-white text-[10px]">${c.value}</span>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Card D: Network Telemetry & REA Commands -->
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span class="text-xs font-bold text-pink-300 flex items-center gap-1.5">
              <i data-lucide="terminal" class="w-3.5 h-3.5 text-pink-400"></i> Lệnh REA CLI Trích Xuất Trên Máy Của Bạn:
            </span>
            <div class="space-y-1.5 text-[10px] font-mono">
              ${(data.rea_dossier.rea_cli_commands || []).map(cmd => `
                <div class="p-2 rounded bg-slate-900 border border-slate-800 text-slate-300 flex items-center justify-between gap-2">
                  <span class="truncate text-pink-300">${cmd}</span>
                  <button onclick="copyTextToClipboard('${cmd.replace(/'/g, "\\'")}', 'Đã sao chép lệnh REA!')" class="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 cursor-pointer text-[9px] whitespace-nowrap">
                    Copy
                  </button>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>
    ` : ''}

  `;

  lucide.createIcons();
}

function copyModalDeconstructMarkdown() {
  if (!currentModalDeconstructData || !currentModalDeconstructData.markdown_blueprint) {
    showToast('Chưa có dữ liệu Blueprint để sao chép.');
    return;
  }
  navigator.clipboard.writeText(currentModalDeconstructData.markdown_blueprint).then(() => {
    showToast('Đã sao chép Blueprint Clone (.md) vào clipboard!');
  }).catch(err => {
    showToast('Lỗi khi sao chép: ' + err);
  });
}

function downloadModalDeconstructMarkdown() {
  if (!currentModalDeconstructData || !currentModalDeconstructData.markdown_blueprint) {
    showToast('Chưa có dữ liệu Blueprint để tải về.');
    return;
  }
  const title = (currentModalDeconstructData.title || currentActiveModalGameTitle || 'Game').replace(/[^a-zA-Z0-9_-]/g, '_');
  const blob = new Blob([currentModalDeconstructData.markdown_blueprint], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title}_Clone_Blueprint.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Đã tải file Blueprint (.md) về máy thành công!');
}

function copyModalDeconstructCode() {
  if (!currentModalDeconstructData || !currentModalDeconstructData.unity_starter_code) {
    showToast('Chưa có mã nguồn C# để sao chép.');
    return;
  }
  navigator.clipboard.writeText(currentModalDeconstructData.unity_starter_code).then(() => {
    showToast('Đã sao chép mã nguồn C# Unity vào clipboard!');
  }).catch(err => {
    showToast('Lỗi khi sao chép: ' + err);
  });
}

function downloadUnityZipPackage() {
  const title = currentActiveModalGameTitle || 'Game';
  const platform = currentActiveModalGamePlatform || 'PC / Mobile';
  const genre = currentActiveModalGameGenre || 'Action';
  const storeUrl = currentActiveModalGameStoreUrl || '';
  const desc = currentActiveModalGameDesc || '';
  showToast(`Đang đóng gói Starter Project Unity (.zip) cho ${title}...`);
  const url = `/api/deconstruct/export-unity-zip?title=${encodeURIComponent(title)}&platform=${encodeURIComponent(platform)}&genre=${encodeURIComponent(genre)}&store_url=${encodeURIComponent(storeUrl)}&desc=${encodeURIComponent(desc)}`;
  window.location.href = url;
}

function copyTextToClipboard(text, msg) {
  navigator.clipboard.writeText(text).then(() => {
    showToast(msg || 'Đã sao chép vào clipboard!');
  }).catch(err => {
    showToast('Lỗi khi sao chép: ' + err);
  });
}

// --- HTML5 CANVAS 60 FPS PROTOTYPE SIMULATOR ---
let protoCanvas = null;
let protoCtx = null;
let isProtoRunning = false;
let protoAnimId = null;
let protoSpeed = 1;
let protoAutopilot = false;
let protoAudioEnabled = true;
let protoAudioCtx = null;
let protoLastTime = 0;
let protoKeys = { w: false, a: false, s: false, d: false, ArrowUp: false, ArrowDown: false, ArrowLeft: false, ArrowRight: false };
let protoTouch = { active: false, x: 0, y: 0 };
let protoEventsBound = false;

let protoState = {
  player: {
    x: 450, y: 210, radius: 14,
    hp: 100, maxHp: 100,
    speed: 3.8,
    fireInterval: 320,
    lastFire: 0,
    bulletSpeed: 8,
    damage: 30,
    multishot: 1,
    magnet: 130,
    level: 1,
    exp: 0,
    expNext: 60,
    kills: 0,
    facingAngle: 0
  },
  enemies: [],
  bullets: [],
  gems: [],
  particles: [],
  floatingTexts: [],
  wave: 1,
  startTime: 0,
  elapsedTime: 0,
  spawnTimer: 0,
  spawnInterval: 1100,
  isGameOver: false,
  isLevelingUp: false
};

function playProtoSound(type) {
  if (!protoAudioEnabled) return;
  try {
    if (!protoAudioCtx) {
      protoAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (protoAudioCtx.state === 'suspended') {
      protoAudioCtx.resume();
    }
    const osc = protoAudioCtx.createOscillator();
    const gain = protoAudioCtx.createGain();
    osc.connect(gain);
    gain.connect(protoAudioCtx.destination);
    const now = protoAudioCtx.currentTime;

    if (type === 'shoot') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.07);
      gain.gain.setValueAtTime(0.06, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.07);
      osc.start(now);
      osc.stop(now + 0.07);
    } else if (type === 'hit') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(160, now);
      osc.frequency.exponentialRampToValueAtTime(40, now + 0.09);
      gain.gain.setValueAtTime(0.09, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.09);
      osc.start(now);
      osc.stop(now + 0.09);
    } else if (type === 'gem') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(659, now);
      osc.frequency.setValueAtTime(987, now + 0.05);
      gain.gain.setValueAtTime(0.07, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.12);
      osc.start(now);
      osc.stop(now + 0.12);
    } else if (type === 'levelup') {
      osc.type = 'square';
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.setValueAtTime(554, now + 0.08);
      osc.frequency.setValueAtTime(659, now + 0.16);
      osc.frequency.setValueAtTime(880, now + 0.24);
      gain.gain.setValueAtTime(0.09, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    } else if (type === 'gameover') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(55, now + 0.35);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    }
  } catch (e) {}
}

function initPrototypeGame() {
  protoCanvas = document.getElementById('prototypeCanvas');
  if (!protoCanvas) return;
  protoCtx = protoCanvas.getContext('2d');

  const rect = protoCanvas.getBoundingClientRect();
  if (rect.width > 0) {
    protoCanvas.width = rect.width;
    protoCanvas.height = 420;
  }

  if (!protoEventsBound) {
    window.addEventListener('keydown', (e) => {
      if (['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        protoKeys[e.key] = true;
      }
    });
    window.addEventListener('keyup', (e) => {
      if (['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        protoKeys[e.key] = false;
      }
    });

    const handlePointer = (clientX, clientY, active) => {
      if (!protoCanvas) return;
      const r = protoCanvas.getBoundingClientRect();
      protoTouch.active = active;
      protoTouch.x = clientX - r.left;
      protoTouch.y = clientY - r.top;
    };

    protoCanvas.addEventListener('mousedown', (e) => handlePointer(e.clientX, e.clientY, true));
    window.addEventListener('mousemove', (e) => {
      if (protoTouch.active) handlePointer(e.clientX, e.clientY, true);
    });
    window.addEventListener('mouseup', () => { protoTouch.active = false; });

    protoCanvas.addEventListener('touchstart', (e) => {
      if (e.touches && e.touches.length > 0) handlePointer(e.touches[0].clientX, e.touches[0].clientY, true);
    }, { passive: true });
    protoCanvas.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches.length > 0) handlePointer(e.touches[0].clientX, e.touches[0].clientY, true);
    }, { passive: true });
    protoCanvas.addEventListener('touchend', () => { protoTouch.active = false; });

    protoEventsBound = true;
  }

  resetPrototypeGame(false);
}

function resetPrototypeGame(autoStart = false) {
  const w = (protoCanvas && protoCanvas.width) || 900;
  const h = (protoCanvas && protoCanvas.height) || 420;

  protoState = {
    player: {
      x: w / 2, y: h / 2, radius: 14,
      hp: 100, maxHp: 100,
      speed: 3.8,
      fireInterval: 320,
      lastFire: 0,
      bulletSpeed: 8,
      damage: 30,
      multishot: 1,
      magnet: 130,
      level: 1,
      exp: 0,
      expNext: 60,
      kills: 0,
      facingAngle: 0
    },
    enemies: [],
    bullets: [],
    gems: [],
    particles: [],
    floatingTexts: [],
    wave: 1,
    startTime: Date.now(),
    elapsedTime: 0,
    spawnTimer: 0,
    spawnInterval: 1000,
    isGameOver: false,
    isLevelingUp: false
  };

  const upOverlay = document.getElementById('protoUpgradeOverlay');
  if (upOverlay) { upOverlay.classList.add('hidden'); upOverlay.classList.remove('flex'); }
  const goOverlay = document.getElementById('protoGameOverOverlay');
  if (goOverlay) { goOverlay.classList.add('hidden'); goOverlay.classList.remove('flex'); }

  updatePrototypeHUD();

  if (autoStart) {
    startPrototypeGame();
  } else {
    renderPrototypeStaticFrame();
  }
}

function togglePrototypePlay() {
  if (isProtoRunning) {
    pausePrototypeGame();
  } else {
    startPrototypeGame();
  }
}

function startPrototypeGame() {
  if (!protoCanvas) initPrototypeGame();
  if (protoState.isGameOver) {
    resetPrototypeGame(true);
    return;
  }
  isProtoRunning = true;
  protoLastTime = performance.now();
  const btn = document.getElementById('protoPlayBtn');
  if (btn) {
    btn.className = "px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-amber-600/30 cursor-pointer";
    const txt = document.getElementById('protoPlayText');
    if (txt) txt.innerText = "Tạm Dừng";
    const icon = document.getElementById('protoPlayIcon');
    if (icon) icon.setAttribute('data-lucide', 'pause');
    lucide.createIcons();
  }
  cancelAnimationFrame(protoAnimId);
  protoAnimId = requestAnimationFrame(prototypeGameLoop);
}

function pausePrototypeGame() {
  isProtoRunning = false;
  cancelAnimationFrame(protoAnimId);
  const btn = document.getElementById('protoPlayBtn');
  if (btn) {
    btn.className = "px-3.5 py-1.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-violet-600/30 cursor-pointer";
    const txt = document.getElementById('protoPlayText');
    if (txt) txt.innerText = "Tiếp Tục Chơi";
    const icon = document.getElementById('protoPlayIcon');
    if (icon) icon.setAttribute('data-lucide', 'play');
    lucide.createIcons();
  }
}

function togglePrototypeSpeed() {
  protoSpeed = (protoSpeed === 1) ? 2 : 1;
  const text = document.getElementById('protoSpeedText');
  if (text) text.innerText = `Tốc độ x${protoSpeed}`;
  const btn = document.getElementById('protoSpeedBtn');
  if (btn) {
    if (protoSpeed === 2) {
      btn.className = "px-3.5 py-1.5 rounded-xl bg-amber-600 text-white text-xs font-bold border border-amber-500 flex items-center gap-1 cursor-pointer";
    } else {
      btn.className = "px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 flex items-center gap-1 cursor-pointer";
    }
  }
}

function togglePrototypeAutopilot() {
  protoAutopilot = !protoAutopilot;
  const text = document.getElementById('protoAutopilotText');
  if (text) text.innerText = `Auto-Pilot: ${protoAutopilot ? 'ON 🤖' : 'OFF'}`;
  const btn = document.getElementById('protoAutopilotBtn');
  if (btn) {
    if (protoAutopilot) {
      btn.className = "px-3.5 py-1.5 rounded-xl bg-cyan-600 text-white text-xs font-bold border border-cyan-400 flex items-center gap-1 cursor-pointer shadow-lg shadow-cyan-600/30";
    } else {
      btn.className = "px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 flex items-center gap-1 cursor-pointer";
    }
  }
}

function togglePrototypeAudio() {
  protoAudioEnabled = !protoAudioEnabled;
  const text = document.getElementById('protoAudioText');
  if (text) text.innerText = `SFX: ${protoAudioEnabled ? 'Bật' : 'Tắt'}`;
  const btn = document.getElementById('protoAudioBtn');
  if (btn) {
    if (protoAudioEnabled) {
      btn.className = "px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 flex items-center gap-1 cursor-pointer";
    } else {
      btn.className = "px-3.5 py-1.5 rounded-xl bg-slate-800 text-slate-500 text-xs font-semibold border border-slate-800 flex items-center gap-1 cursor-pointer";
    }
  }
}

function updatePrototypeHUD() {
  const p = protoState.player;
  const lvl = document.getElementById('protoHudLevel');
  if (lvl) lvl.innerText = p.level;

  const hpTxt = document.getElementById('protoHudHp');
  if (hpTxt) hpTxt.innerText = `${Math.max(0, Math.round(p.hp))}/${p.maxHp}`;

  const hpBar = document.getElementById('protoHpBar');
  if (hpBar) {
    const pct = Math.max(0, Math.min(100, (p.hp / p.maxHp) * 100));
    hpBar.style.width = `${pct}%`;
    if (pct > 50) hpBar.className = "h-full bg-emerald-500 rounded-full transition-all duration-150";
    else if (pct > 25) hpBar.className = "h-full bg-amber-500 rounded-full transition-all duration-150";
    else hpBar.className = "h-full bg-rose-500 rounded-full transition-all duration-150";
  }

  const waveTxt = document.getElementById('protoHudWave');
  if (waveTxt) waveTxt.innerText = `Wave ${protoState.wave}`;

  const killsTxt = document.getElementById('protoHudKills');
  if (killsTxt) killsTxt.innerText = p.kills;

  const timerTxt = document.getElementById('protoHudTimer');
  if (timerTxt) {
    const s = Math.floor(protoState.elapsedTime / 1000);
    const mm = String(Math.floor(s / 60)).padStart(2, '0');
    const ss = String(s % 60).padStart(2, '0');
    timerTxt.innerText = `${mm}:${ss}`;
  }
}

function prototypeGameLoop(timestamp) {
  if (!isProtoRunning) return;
  const rawDelta = Math.min(timestamp - protoLastTime, 100);
  protoLastTime = timestamp;
  const dt = (rawDelta / 16.666) * protoSpeed;

  protoState.elapsedTime += rawDelta * protoSpeed;
  const w = protoCanvas.width;
  const h = protoCanvas.height;
  const p = protoState.player;

  // 1. Move Player
  let dx = 0;
  let dy = 0;
  if (protoAutopilot) {
    let threat = null;
    let threatDist = 120;
    protoState.enemies.forEach(e => {
      const d = Math.hypot(e.x - p.x, e.y - p.y);
      if (d < threatDist) {
        threat = e;
        threatDist = d;
      }
    });

    if (threat) {
      dx = p.x - threat.x;
      dy = p.y - threat.y;
    } else if (protoState.gems.length > 0) {
      let closestGem = protoState.gems[0];
      let minDist = 9999;
      protoState.gems.forEach(g => {
        const d = Math.hypot(g.x - p.x, g.y - p.y);
        if (d < minDist) {
          minDist = d;
          closestGem = g;
        }
      });
      dx = closestGem.x - p.x;
      dy = closestGem.y - p.y;
    } else if (protoState.enemies.length > 0) {
      const target = protoState.enemies[0];
      const dist = Math.hypot(target.x - p.x, target.y - p.y);
      if (dist > 180) {
        dx = target.x - p.x;
        dy = target.y - p.y;
      } else if (dist < 130) {
        dx = p.x - target.x;
        dy = p.y - target.y;
      }
    }
  } else if (protoTouch.active) {
    dx = protoTouch.x - p.x;
    dy = protoTouch.y - p.y;
    if (Math.hypot(dx, dy) < 10) { dx = 0; dy = 0; }
  } else {
    if (protoKeys.w || protoKeys.ArrowUp) dy -= 1;
    if (protoKeys.s || protoKeys.ArrowDown) dy += 1;
    if (protoKeys.a || protoKeys.ArrowLeft) dx -= 1;
    if (protoKeys.d || protoKeys.ArrowRight) dx += 1;
  }

  if (dx !== 0 || dy !== 0) {
    const len = Math.hypot(dx, dy);
    p.x += (dx / len) * p.speed * dt;
    p.y += (dy / len) * p.speed * dt;
    p.facingAngle = Math.atan2(dy, dx);
  }

  p.x = Math.max(p.radius + 5, Math.min(w - p.radius - 5, p.x));
  p.y = Math.max(p.radius + 5, Math.min(h - p.radius - 5, p.y));

  // 2. Auto-Target Weapon
  if (timestamp - p.lastFire > p.fireInterval) {
    let nearestEnemy = null;
    let minRange = 400;
    protoState.enemies.forEach(e => {
      const dist = Math.hypot(e.x - p.x, e.y - p.y);
      if (dist < minRange) {
        minRange = dist;
        nearestEnemy = e;
      }
    });

    if (nearestEnemy) {
      p.lastFire = timestamp;
      const baseAngle = Math.atan2(nearestEnemy.y - p.y, nearestEnemy.x - p.x);
      p.facingAngle = baseAngle;

      const shots = p.multishot;
      const spread = 0.22;
      for (let i = 0; i < shots; i++) {
        const offset = (shots > 1) ? (i - (shots - 1) / 2) * spread : 0;
        const angle = baseAngle + offset;
        protoState.bullets.push({
          x: p.x + Math.cos(angle) * (p.radius + 4),
          y: p.y + Math.sin(angle) * (p.radius + 4),
          vx: Math.cos(angle) * p.bulletSpeed,
          vy: Math.sin(angle) * p.bulletSpeed,
          radius: 4.5,
          damage: p.damage,
          life: 55
        });
      }
      playProtoSound('shoot');
    }
  }

  // 3. Update Bullets
  for (let i = protoState.bullets.length - 1; i >= 0; i--) {
    const b = protoState.bullets[i];
    b.x += b.vx * dt;
    b.y += b.vy * dt;
    b.life -= dt;

    let hit = false;
    for (let j = protoState.enemies.length - 1; j >= 0; j--) {
      const e = protoState.enemies[j];
      const dist = Math.hypot(e.x - b.x, e.y - b.y);
      if (dist < e.radius + b.radius) {
        hit = true;
        const isCrit = Math.random() < 0.25;
        const dmg = isCrit ? Math.round(b.damage * 1.8) : b.damage;
        e.hp -= dmg;

        protoState.floatingTexts.push({
          x: e.x + (Math.random() - 0.5) * 16,
          y: e.y - 12,
          text: isCrit ? `CRIT! ${dmg}` : `${dmg}`,
          color: isCrit ? '#f59e0b' : '#38bdf8',
          life: 30,
          size: isCrit ? 13 : 11
        });

        for (let k = 0; k < 4; k++) {
          protoState.particles.push({
            x: b.x, y: b.y,
            vx: (Math.random() - 0.5) * 5,
            vy: (Math.random() - 0.5) * 5,
            color: isCrit ? '#f59e0b' : '#38bdf8',
            radius: Math.random() * 2.5 + 1,
            life: 15, maxLife: 15
          });
        }

        playProtoSound('hit');

        if (e.hp <= 0) {
          p.kills++;
          protoState.gems.push({
            x: e.x, y: e.y,
            value: e.expVal,
            radius: 5
          });
          for (let k = 0; k < 8; k++) {
            protoState.particles.push({
              x: e.x, y: e.y,
              vx: (Math.random() - 0.5) * 6,
              vy: (Math.random() - 0.5) * 6,
              color: e.color,
              radius: Math.random() * 3.5 + 1.5,
              life: 22, maxLife: 22
            });
          }
          protoState.enemies.splice(j, 1);
        }
        break;
      }
    }

    if (hit || b.life <= 0 || b.x < 0 || b.x > w || b.y < 0 || b.y > h) {
      protoState.bullets.splice(i, 1);
    }
  }

  // 4. Enemy Spawner & Waves
  protoState.spawnTimer += rawDelta * protoSpeed;
  const currentSeconds = Math.floor(protoState.elapsedTime / 1000);
  protoState.wave = Math.floor(currentSeconds / 20) + 1;
  protoState.spawnInterval = Math.max(380, 1050 - (protoState.wave * 80));

  if (protoState.spawnTimer > protoState.spawnInterval && protoState.enemies.length < 50) {
    protoState.spawnTimer = 0;
    let sx, sy;
    const side = Math.floor(Math.random() * 4);
    if (side === 0) { sx = Math.random() * w; sy = -15; }
    else if (side === 1) { sx = w + 15; sy = Math.random() * h; }
    else if (side === 2) { sx = Math.random() * w; sy = h + 15; }
    else { sx = -15; sy = Math.random() * h; }

    const rType = Math.random();
    let eType = { radius: 11, hp: 45 + protoState.wave * 12, maxHp: 45 + protoState.wave * 12, speed: 1.7 + (protoState.wave * 0.1), color: '#ef4444', expVal: 15 };
    if (rType > 0.8) {
      eType = { radius: 18, hp: 140 + protoState.wave * 35, maxHp: 140 + protoState.wave * 35, speed: 1.1, color: '#a855f7', expVal: 35 };
    } else if (rType > 0.6) {
      eType = { radius: 9, hp: 30 + protoState.wave * 8, maxHp: 30 + protoState.wave * 8, speed: 2.8, color: '#f97316', expVal: 20 };
    }

    protoState.enemies.push({
      x: sx, y: sy,
      radius: eType.radius,
      hp: eType.hp,
      maxHp: eType.maxHp,
      speed: eType.speed,
      color: eType.color,
      expVal: eType.expVal
    });
  }

  // 5. Update Enemies
  for (let i = protoState.enemies.length - 1; i >= 0; i--) {
    const e = protoState.enemies[i];
    const angle = Math.atan2(p.y - e.y, p.x - e.x);
    e.x += Math.cos(angle) * e.speed * dt;
    e.y += Math.sin(angle) * e.speed * dt;

    const dist = Math.hypot(p.x - e.x, p.y - e.y);
    if (dist < p.radius + e.radius) {
      p.hp -= 0.35 * dt;
      if (Math.random() < 0.15) {
        playProtoSound('hit');
      }
      if (p.hp <= 0) {
        p.hp = 0;
        triggerPrototypeGameOver();
        return;
      }
    }
  }

  // 6. Update Gems & Vacuum Attraction
  for (let i = protoState.gems.length - 1; i >= 0; i--) {
    const g = protoState.gems[i];
    const dist = Math.hypot(p.x - g.x, p.y - g.y);
    if (dist < p.magnet) {
      const pullSpeed = Math.max(5, (p.magnet - dist) * 0.15);
      const angle = Math.atan2(p.y - g.y, p.x - g.x);
      g.x += Math.cos(angle) * pullSpeed * dt;
      g.y += Math.sin(angle) * pullSpeed * dt;
    }

    if (dist < p.radius + g.radius + 3) {
      p.exp += g.value;
      playProtoSound('gem');
      protoState.gems.splice(i, 1);

      if (p.exp >= p.expNext) {
        triggerPrototypeLevelUp();
        return;
      }
    }
  }

  // 7. Update Particles
  for (let i = protoState.particles.length - 1; i >= 0; i--) {
    const pt = protoState.particles[i];
    pt.x += pt.vx * dt;
    pt.y += pt.vy * dt;
    pt.life -= dt;
    if (pt.life <= 0) protoState.particles.splice(i, 1);
  }

  // 8. Update Floating Texts
  for (let i = protoState.floatingTexts.length - 1; i >= 0; i--) {
    const ft = protoState.floatingTexts[i];
    ft.y -= 0.6 * dt;
    ft.life -= dt;
    if (ft.life <= 0) protoState.floatingTexts.splice(i, 1);
  }

  // 9. Render Frame
  renderPrototypeFrame();
  updatePrototypeHUD();

  protoAnimId = requestAnimationFrame(prototypeGameLoop);
}

function renderPrototypeFrame() {
  if (!protoCtx || !protoCanvas) return;
  const ctx = protoCtx;
  const w = protoCanvas.width;
  const h = protoCanvas.height;
  const p = protoState.player;

  ctx.fillStyle = '#060913';
  ctx.fillRect(0, 0, w, h);

  ctx.strokeStyle = 'rgba(30, 41, 59, 0.4)';
  ctx.lineWidth = 1;
  const gridSize = 40;
  for (let x = 0; x < w; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = 0; y < h; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // Magnet vacuum aura
  ctx.beginPath();
  ctx.arc(p.x, p.y, p.magnet, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(56, 189, 248, 0.03)';
  ctx.fill();
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.12)';
  ctx.setLineDash([4, 6]);
  ctx.stroke();
  ctx.setLineDash([]);

  // Gems
  protoState.gems.forEach(g => {
    ctx.save();
    ctx.translate(g.x, g.y);
    ctx.fillStyle = '#10b981';
    ctx.shadowColor = '#10b981';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.moveTo(0, -g.radius);
    ctx.lineTo(g.radius, 0);
    ctx.lineTo(0, g.radius);
    ctx.lineTo(-g.radius, 0);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  });

  // Enemies
  protoState.enemies.forEach(e => {
    ctx.save();
    ctx.beginPath();
    ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
    ctx.fillStyle = e.color;
    ctx.shadowColor = e.color;
    ctx.shadowBlur = 10;
    ctx.fill();

    ctx.beginPath();
    ctx.arc(e.x, e.y, e.radius * 0.5, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.fill();

    if (e.hp < e.maxHp) {
      const barW = e.radius * 2.2;
      const barH = 3;
      const pct = Math.max(0, e.hp / e.maxHp);
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.fillRect(e.x - barW / 2, e.y - e.radius - 7, barW, barH);
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(e.x - barW / 2, e.y - e.radius - 7, barW * pct, barH);
    }
    ctx.restore();
  });

  // Bullets
  protoState.bullets.forEach(b => {
    ctx.save();
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
    ctx.fillStyle = '#38bdf8';
    ctx.shadowColor = '#38bdf8';
    ctx.shadowBlur = 12;
    ctx.fill();
    ctx.restore();
  });

  // Particles
  protoState.particles.forEach(pt => {
    const alpha = Math.max(0, pt.life / pt.maxLife);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, pt.radius, 0, Math.PI * 2);
    ctx.fillStyle = pt.color;
    ctx.fill();
    ctx.restore();
  });

  // Player
  ctx.save();
  ctx.shadowColor = '#8b5cf6';
  ctx.shadowBlur = 16;
  ctx.beginPath();
  ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
  ctx.fillStyle = '#8b5cf6';
  ctx.fill();
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = '#c4b5fd';
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(p.x, p.y);
  ctx.lineTo(p.x + Math.cos(p.facingAngle) * (p.radius + 7), p.y + Math.sin(p.facingAngle) * (p.radius + 7));
  ctx.lineWidth = 4;
  ctx.strokeStyle = '#f8fafc';
  ctx.lineCap = 'round';
  ctx.stroke();
  ctx.restore();

  // Floating Texts
  protoState.floatingTexts.forEach(ft => {
    ctx.save();
    ctx.font = `bold ${ft.size || 11}px sans-serif`;
    ctx.fillStyle = ft.color;
    ctx.shadowColor = '#000';
    ctx.shadowBlur = 4;
    ctx.textAlign = 'center';
    ctx.fillText(ft.text, ft.x, ft.y);
    ctx.restore();
  });
}

function renderPrototypeStaticFrame() {
  if (!protoCanvas) initPrototypeGame();
  renderPrototypeFrame();
}

function triggerPrototypeLevelUp() {
  pausePrototypeGame();
  protoState.isLevelingUp = true;
  const p = protoState.player;
  p.level++;
  p.exp -= p.expNext;
  p.expNext = Math.round(p.expNext * 1.45);
  playProtoSound('levelup');

  const pool = [
    { id: 'firerate', title: '⚡ Bắn Cực Nhanh', desc: 'Tăng 30% tốc độ xả đạn của vũ khí.' },
    { id: 'damage', title: '💥 Đạn Công Phá', desc: 'Tăng 40% sát thương cơ bản mỗi phát bắn.' },
    { id: 'multishot', title: '🌟 Bắn Phân Thân', desc: 'Bắn thêm +1 viên đạn nan quạt.' },
    { id: 'speed', title: '👟 Gia Tốc Lướt', desc: 'Tăng 25% tốc độ di chuyển né đòn.' },
    { id: 'magnet', title: '🧲 Siêu Nam Châm', desc: 'Tăng 60% bán kính hút ngọc EXP.' },
    { id: 'heal', title: '💖 Trị Liệu & Tăng Máu', desc: 'Hồi phục +50 HP và tăng +30 Max HP vĩnh viễn.' }
  ];

  const shuffled = pool.sort(() => 0.5 - Math.random()).slice(0, 3);
  const container = document.getElementById('protoUpgradeCards');
  if (container) {
    container.innerHTML = shuffled.map(up => `
      <button onclick="applyPrototypeUpgrade('${up.id}')" class="p-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-violet-500/30 hover:border-violet-400 text-left transition-all hover:scale-105 cursor-pointer shadow-lg space-y-1 group">
        <div class="flex items-center gap-2">
          <span class="w-6 h-6 rounded-lg bg-violet-500/20 text-violet-300 font-bold flex items-center justify-center text-xs group-hover:bg-violet-500 group-hover:text-white transition-colors">
            ★
          </span>
          <h4 class="text-xs font-bold text-white">${up.title}</h4>
        </div>
        <p class="text-[11px] text-slate-300">${up.desc}</p>
      </button>
    `).join('');
  }

  const overlay = document.getElementById('protoUpgradeOverlay');
  if (overlay) {
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
  }
  lucide.createIcons();
}

function applyPrototypeUpgrade(type) {
  const p = protoState.player;
  if (type === 'firerate') p.fireInterval = Math.max(100, Math.round(p.fireInterval * 0.72));
  else if (type === 'damage') p.damage = Math.round(p.damage * 1.4);
  else if (type === 'multishot') p.multishot += 1;
  else if (type === 'speed') p.speed *= 1.25;
  else if (type === 'magnet') p.magnet *= 1.6;
  else if (type === 'heal') {
    p.maxHp += 30;
    p.hp = Math.min(p.maxHp, p.hp + 50);
  }

  protoState.isLevelingUp = false;
  const overlay = document.getElementById('protoUpgradeOverlay');
  if (overlay) {
    overlay.classList.add('hidden');
    overlay.classList.remove('flex');
  }
  startPrototypeGame();
}

function triggerPrototypeGameOver() {
  pausePrototypeGame();
  protoState.isGameOver = true;
  playProtoSound('gameover');

  const s = Math.floor(protoState.elapsedTime / 1000);
  const mm = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  const sum = document.getElementById('protoGameOverSummary');
  if (sum) {
    sum.innerText = `Sống sót được ${mm}:${ss} (Wave ${protoState.wave}) và tiêu diệt ${protoState.player.kills} quái.`;
  }

  const overlay = document.getElementById('protoGameOverOverlay');
  if (overlay) {
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
  }
  lucide.createIcons();
}

function initOrResumePrototype() {
  if (!protoCanvas) {
    setTimeout(initPrototypeGame, 50);
  } else {
    renderPrototypeStaticFrame();
  }
}

// --- AI VISUAL ASSET PROMPT GENERATOR & MOODBOARD STUDIO ---
let modalArtPromptsCache = {};
let currentModalArtPromptsData = null;

async function loadModalArtPrompts(forceReload = false) {
  const container = document.getElementById('modalArtPromptsContainer');
  if (!container) return;
  const title = currentActiveModalGameTitle || 'Game';
  const style = document.getElementById('modalArtStyleSelect')?.value || 'Stylized 3D Anime (Genshin / Honkai Style)';
  const cacheKey = `${currentActiveModalGameId}_${style}`;

  if (!forceReload && modalArtPromptsCache[cacheKey]) {
    currentModalArtPromptsData = modalArtPromptsCache[cacheKey];
    renderModalArtPrompts(currentModalArtPromptsData);
    return;
  }

  container.innerHTML = `
    <div class="p-10 text-center space-y-4 rounded-2xl bg-slate-950/80 border border-slate-800">
      <div class="inline-block p-4 rounded-2xl bg-fuchsia-500/10 border border-fuchsia-500/20 text-fuchsia-400 animate-pulse">
        <i data-lucide="palette" class="w-10 h-10 animate-spin"></i>
      </div>
      <h4 class="text-base font-bold text-white">Đang Khởi Tạo Bộ Prompt AI Assets Cho "${title}"...</h4>
      <p class="text-xs text-slate-400 max-w-md mx-auto">
        Hệ thống đang chuyển hóa danh mục Asset Checklist thành Prompt Midjourney / Stable Diffusion theo phong cách "${style}"...
      </p>
    </div>
  `;
  lucide.createIcons();

  try {
    const res = await fetch('/api/deconstruct/art-prompts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_title: title,
        platform: currentActiveModalGamePlatform || 'PC / Mobile',
        genre: currentActiveModalGameGenre || 'Action',
        art_style: style,
        asset_checklist: (currentModalDeconstructData && currentModalDeconstructData.asset_checklist) || {}
      })
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    modalArtPromptsCache[cacheKey] = data;
    currentModalArtPromptsData = data;
    renderModalArtPrompts(data);
  } catch (err) {
    container.innerHTML = `
      <div class="p-8 text-center text-rose-400 space-y-2 rounded-2xl bg-slate-950 border border-slate-800">
        <i data-lucide="alert-circle" class="w-8 h-8 mx-auto"></i>
        <p class="font-bold text-xs">Lỗi khi tạo prompt visual: ${err.message}</p>
        <button onclick="loadModalArtPrompts(true)" class="px-4 py-2 rounded-lg bg-slate-800 text-white text-xs hover:bg-slate-700 cursor-pointer">Thử Lại</button>
      </div>
    `;
    lucide.createIcons();
  }
}

function reloadModalArtPrompts() {
  loadModalArtPrompts(true);
}

function onArtStyleChanged() {
  loadModalArtPrompts(true);
}

function renderModalArtPrompts(data) {
  const container = document.getElementById('modalArtPromptsContainer');
  if (!container) return;

  const palette = data.moodboard_palette || ['#6366f1', '#a855f7', '#ec4899', '#f43f5e', '#3b82f6'];
  const prompts = data.prompts || [];

  container.innerHTML = `
    <!-- Moodboard Color Palette -->
    <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-2.5">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-slate-200 flex items-center gap-1.5">
          <i data-lucide="swatch-book" class="w-4 h-4 text-fuchsia-400"></i>
          Bảng Màu Chủ Đạo Moodboard (Color Palette):
        </span>
        <span class="text-[11px] text-slate-400 font-medium">Bấm vào mã màu để sao chép Hex</span>
      </div>
      <div class="flex items-center gap-2.5 flex-wrap">
        ${palette.map(color => `
          <div onclick="copyTextToClipboard('${color}', 'Đã sao chép mã màu ${color}!')" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700/80 hover:border-slate-500 cursor-pointer transition-all hover:scale-105">
            <span class="w-4 h-4 rounded-lg shadow-inner" style="background-color: ${color};"></span>
            <span class="font-mono text-xs font-semibold text-slate-200">${color}</span>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Prompts Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      ${prompts.map((p, idx) => `
        <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-3 flex flex-col justify-between hover:border-fuchsia-500/40 transition-all">
          <div class="space-y-2">
            <div class="flex items-center justify-between gap-2">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/30 uppercase tracking-wider">
                ${p.category || 'Asset'}
              </span>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                --ar ${p.aspect_ratio || '1:1'}
              </span>
            </div>
            <h4 class="text-xs font-bold text-white flex items-center gap-1.5">
              <i data-lucide="sparkles" class="w-3.5 h-3.5 text-fuchsia-400"></i>
              ${p.subject || 'Visual Subject'}
            </h4>
            <div class="p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs font-mono text-fuchsia-200 leading-relaxed select-all">
              ${p.prompt}
            </div>
            ${p.negative_prompt ? `
              <div class="p-2 rounded-lg bg-rose-950/20 border border-rose-900/30 text-[11px] text-rose-300">
                <span class="font-semibold text-rose-400 block text-[10px]">Negative Prompt:</span>
                ${p.negative_prompt}
              </div>
            ` : ''}
          </div>
          <button onclick="copyTextToClipboard('${p.prompt.replace(/'/g, "\\'")}', 'Đã sao chép prompt Midjourney!')" class="w-full mt-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1.5 cursor-pointer">
            <i data-lucide="copy" class="w-3.5 h-3.5 text-fuchsia-400"></i> Sao Chép Prompt Này
          </button>
        </div>
      `).join('')}
    </div>
  `;
  lucide.createIcons();
}

function copyAllArtPrompts() {
  if (!currentModalArtPromptsData || !currentModalArtPromptsData.prompts) {
    showToast('Chưa có dữ liệu prompt để sao chép.');
    return;
  }
  const lines = currentModalArtPromptsData.prompts.map(p => `### [${p.category}] ${p.subject}\nPrompt:\n${p.prompt}\n\nNegative:\n${p.negative_prompt || 'None'}\n-----------------------------------\n`).join('\n');
  navigator.clipboard.writeText(lines).then(() => {
    showToast('Đã sao chép toàn bộ bộ prompt vào clipboard!');
  });
}

function downloadAllArtPromptsText() {
  if (!currentModalArtPromptsData || !currentModalArtPromptsData.prompts) {
    showToast('Chưa có dữ liệu prompt để tải.');
    return;
  }
  const title = (currentActiveModalGameTitle || 'Game').replace(/[^a-zA-Z0-9_-]/g, '_');
  const lines = currentModalArtPromptsData.prompts.map(p => `### [${p.category}] ${p.subject}\nPrompt:\n${p.prompt}\n\nNegative:\n${p.negative_prompt || 'None'}\n-----------------------------------\n`).join('\n');
  const blob = new Blob([lines], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title}_AI_Art_Prompts.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Đã tải file Prompts (.txt) thành công!');
}

// --- AI COMPETITOR AD CREATIVE VIDEO SCRIPT & STORYBOARD ---
let modalAdScriptCache = {};
let currentModalAdScriptData = null;

async function loadModalAdScript(forceReload = false) {
  const container = document.getElementById('modalAdScriptContainer');
  if (!container) return;
  const gameId = currentActiveModalGameId;
  const title = currentActiveModalGameTitle || 'Game';

  if (!forceReload && modalAdScriptCache[gameId]) {
    currentModalAdScriptData = modalAdScriptCache[gameId];
    renderModalAdScript(currentModalAdScriptData);
    return;
  }

  container.innerHTML = `
    <div class="p-10 text-center space-y-4 rounded-2xl bg-slate-950/80 border border-slate-800">
      <div class="inline-block p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 animate-pulse">
        <i data-lucide="clapperboard" class="w-10 h-10 animate-spin"></i>
      </div>
      <h4 class="text-base font-bold text-white">Đang Biên Soạn Kịch Bản Video Quảng Cáo UA 30s Cho "${title}"...</h4>
      <p class="text-xs text-slate-400 max-w-md mx-auto">
        Hệ thống phân tích cơ chế gây nghiện, xây dựng kịch bản 4 hồi: Hook 3s, Nỗi đau Noob fail, Thỏa mãn Pro wipeout & Kêu gọi CTA...
      </p>
    </div>
  `;
  lucide.createIcons();

  try {
    const res = await fetch('/api/deconstruct/video-ad-script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_title: title,
        platform: currentActiveModalGamePlatform || 'PC / Mobile',
        genre: currentActiveModalGameGenre || 'Action',
        core_hook: (currentModalDeconstructData && currentModalDeconstructData.physics_and_movement && currentModalDeconstructData.physics_and_movement.movement_type) || '',
        target_audience: 'Mobile Gamers aged 18-35',
        pacing_script: (currentModalDeconstructData && currentModalDeconstructData.pacing_script) || []
      })
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    modalAdScriptCache[gameId] = data;
    currentModalAdScriptData = data;
    renderModalAdScript(data);
  } catch (err) {
    container.innerHTML = `
      <div class="p-8 text-center text-rose-400 space-y-2 rounded-2xl bg-slate-950 border border-slate-800">
        <i data-lucide="alert-circle" class="w-8 h-8 mx-auto"></i>
        <p class="font-bold text-xs">Lỗi khi biên soạn video ad script: ${err.message}</p>
        <button onclick="loadModalAdScript(true)" class="px-4 py-2 rounded-lg bg-slate-800 text-white text-xs hover:bg-slate-700 cursor-pointer">Thử Lại</button>
      </div>
    `;
    lucide.createIcons();
  }
}

function reloadModalAdScript() {
  loadModalAdScript(true);
}

function renderModalAdScript(data) {
  const container = document.getElementById('modalAdScriptContainer');
  if (!container) return;

  const scenes = data.scenes || [];
  const bgm = data.bgm_recommendation || {};

  container.innerHTML = `
    <!-- Metadata Header -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
        <span class="text-[10px] text-slate-400 font-semibold uppercase">Định Dạng Video:</span>
        <p class="text-xs font-bold text-white flex items-center gap-1.5">
          <i data-lucide="smartphone" class="w-3.5 h-3.5 text-rose-400"></i> ${data.aspect_ratio || '9:16 Vertical (TikTok/Reels)'}
        </p>
      </div>
      <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
        <span class="text-[10px] text-slate-400 font-semibold uppercase">Thời Lượng Chuẩn:</span>
        <p class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
          <i data-lucide="clock" class="w-3.5 h-3.5"></i> ${data.target_duration || '30 Giây Tối Ưu'}
        </p>
      </div>
      <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
        <span class="text-[10px] text-slate-400 font-semibold uppercase">Góc Tiếp Cận Hook:</span>
        <p class="text-xs font-bold text-emerald-400 flex items-center gap-1.5 truncate">
          <i data-lucide="target" class="w-3.5 h-3.5"></i> ${data.hook_angle || 'Challenge / Skill Test'}
        </p>
      </div>
    </div>

    <!-- 4-Phase Storyboard Timeline -->
    <div class="space-y-3.5">
      <h4 class="text-xs font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
        <i data-lucide="film" class="w-4 h-4 text-rose-400"></i>
        Phân Cảnh Chi Tiết Kịch Bản 4 Hồi (Storyboard 4-Phases)
      </h4>

      <div class="space-y-3">
        ${scenes.map((s, idx) => `
          <div class="glass-card p-4 rounded-xl border border-slate-800/80 hover:border-rose-500/30 transition-all space-y-3">
            <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-800/60 pb-2">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-lg bg-rose-500/20 text-rose-400 text-xs font-black flex items-center justify-center">
                  ${idx + 1}
                </span>
                <h5 class="text-xs font-bold text-white">${s.phase}</h5>
              </div>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
                ⏱️ ${s.timecode}
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div class="space-y-1 p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <span class="text-[11px] font-bold text-rose-400 flex items-center gap-1">
                  <i data-lucide="video" class="w-3.5 h-3.5"></i> Hành Động Thị Giác (Visual Cue):
                </span>
                <p class="text-slate-200 leading-relaxed text-[11px]">${s.visual_action}</p>
              </div>

              <div class="space-y-1 p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <span class="text-[11px] font-bold text-cyan-400 flex items-center gap-1">
                  <i data-lucide="type" class="w-3.5 h-3.5"></i> Chữ Đè Màn Hình (On-Screen Text):
                </span>
                <p class="text-slate-100 font-semibold text-[11px]">${s.on_screen_text}</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div class="space-y-1 p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <span class="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
                  <i data-lucide="mic" class="w-3.5 h-3.5"></i> Lời Bình Tiếng Việt (Voiceover VI):
                </span>
                <p class="text-slate-200 italic leading-relaxed text-[11px]">"${s.voiceover_vi}"</p>
              </div>

              <div class="space-y-1 p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <span class="text-[11px] font-bold text-indigo-400 flex items-center gap-1">
                  <i data-lucide="globe" class="w-3.5 h-3.5"></i> Voiceover Tiếng Anh (EN Global):
                </span>
                <p class="text-slate-200 italic leading-relaxed text-[11px]">"${s.voiceover_en}"</p>
              </div>
            </div>

            <div class="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between text-[11px] text-slate-300 flex-wrap gap-2">
              <span class="flex items-center gap-1 text-slate-400 font-medium">
                <i data-lucide="volume-2" class="w-3.5 h-3.5 text-amber-400"></i> SFX: <strong class="text-slate-200">${s.sfx || 'Game audio'}</strong>
              </span>
              <span class="text-slate-400 font-medium">
                Nhạc nền: <strong class="text-slate-200">${s.bgm_cue || 'Upbeat'}</strong>
              </span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- BGM Recommendations -->
    <div class="p-4 rounded-xl bg-gradient-to-r from-amber-950/30 via-slate-900 to-slate-900 border border-amber-500/30 space-y-2">
      <h4 class="text-xs font-bold text-amber-300 flex items-center gap-1.5">
        <i data-lucide="music" class="w-4 h-4 text-amber-400"></i>
        Khuyến Nghị Nhạc Nền (BGM & Viral Audio Cue):
      </h4>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
        <div><span class="text-slate-400 text-[11px]">Thể Loại:</span> <strong class="text-slate-200 block">${bgm.genre || 'Phonk / Electronic'}</strong></div>
        <div><span class="text-slate-400 text-[11px]">Nhịp Độ (BPM):</span> <strong class="text-amber-400 block">${bgm.tempo_bpm || '135-145 BPM'}</strong></div>
        <div><span class="text-slate-400 text-[11px]">Âm Hưởng Tương Tự:</span> <strong class="text-slate-200 block">${bgm.sound_similar_to || 'Trending TikTok Viral Sound'}</strong></div>
      </div>
    </div>
  `;
  lucide.createIcons();
}

function copyAdScriptText() {
  if (!currentModalAdScriptData || !currentModalAdScriptData.scenes) {
    showToast('Chưa có dữ liệu kịch bản để sao chép.');
    return;
  }
  const data = currentModalAdScriptData;
  let md = `# KỊCH BẢN VIDEO QUẢNG CÁO 30S - ${data.title || currentActiveModalGameTitle}\n`;
  md += `Thời lượng: ${data.target_duration} | Khung hình: ${data.aspect_ratio}\n\n`;
  data.scenes.forEach(s => {
    md += `## [${s.timecode}] ${s.phase}\n`;
    md += `- Visual: ${s.visual_action}\n`;
    md += `- Text Overlay: ${s.on_screen_text}\n`;
    md += `- Voiceover VI: "${s.voiceover_vi}"\n`;
    md += `- Voiceover EN: "${s.voiceover_en}"\n`;
    md += `- SFX: ${s.sfx}\n\n`;
  });
  navigator.clipboard.writeText(md).then(() => {
    showToast('Đã sao chép kịch bản video ad vào clipboard!');
  });
}

function downloadAdScriptMarkdown() {
  if (!currentModalAdScriptData || !currentModalAdScriptData.scenes) {
    showToast('Chưa có dữ liệu kịch bản để tải.');
    return;
  }
  const title = (currentActiveModalGameTitle || 'Game').replace(/[^a-zA-Z0-9_-]/g, '_');
  const data = currentModalAdScriptData;
  let md = `# KỊCH BẢN VIDEO QUẢNG CÁO 30S - ${data.title || currentActiveModalGameTitle}\n`;
  md += `Thời lượng: ${data.target_duration} | Khung hình: ${data.aspect_ratio}\n\n`;
  data.scenes.forEach(s => {
    md += `## [${s.timecode}] ${s.phase}\n`;
    md += `- Visual: ${s.visual_action}\n`;
    md += `- Text Overlay: ${s.on_screen_text}\n`;
    md += `- Voiceover VI: "${s.voiceover_vi}"\n`;
    md += `- Voiceover EN: "${s.voiceover_en}"\n`;
    md += `- SFX: ${s.sfx}\n\n`;
  });
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title}_Video_UA_Ads_Script.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Đã tải file kịch bản (.md) thành công!');
}

// --- AUTOMATIC GDD (GAME DESIGN DOCUMENT) ENGINE ---
async function loadModalGDD(forceReload = false) {
  const container = document.getElementById('modalGddContainer');
  if (!container) return;
  const gameId = currentActiveModalGameId;
  const title = currentActiveModalGameTitle || 'Game';

  if (!forceReload && modalGddCache[gameId]) {
    currentModalGddData = modalGddCache[gameId];
    renderModalGddResults(currentModalGddData);
    return;
  }

  container.innerHTML = `
    <div class="p-10 text-center space-y-4 rounded-2xl bg-slate-950/80 border border-slate-800">
      <div class="inline-block p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 animate-pulse">
        <i data-lucide="file-text" class="w-10 h-10 animate-bounce"></i>
      </div>
      <h4 class="text-base font-bold text-white">Đang Tự Động Biên Soạn Game Design Document (GDD) Cho "${title}"...</h4>
      <p class="text-xs text-slate-400 max-w-md mx-auto">
        Cấu trúc hóa High Concept, Core Loop, D1-D30 Retention, Economy Sinks & Sources, Tech Stack và KPI Benchmarks...
      </p>
    </div>
  `;
  lucide.createIcons();

  try {
    const res = await fetch('/api/gdd/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        genre: currentActiveModalGameGenre || 'Action Roguelike',
        platform: currentActiveModalGamePlatform || 'Cross-Platform',
        target_audience: 'Mid-Core & Casual Players',
        art_style: 'Stylized 3D / 2D High Production',
        monetization_model: 'Hybrid Free-to-Play'
      })
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    modalGddCache[gameId] = data;
    currentModalGddData = data;
    renderModalGddResults(data);
  } catch (err) {
    container.innerHTML = `
      <div class="p-8 text-center text-rose-400 space-y-2 rounded-2xl bg-slate-950 border border-slate-800">
        <i data-lucide="alert-circle" class="w-8 h-8 mx-auto"></i>
        <p class="font-bold text-xs">Lỗi khi biên soạn GDD: ${err.message}</p>
        <button onclick="loadModalGDD(true)" class="px-4 py-2 rounded-lg bg-slate-800 text-white text-xs hover:bg-slate-700 cursor-pointer">Thử Lại</button>
      </div>
    `;
    lucide.createIcons();
  }
}

function reloadModalGDD() {
  loadModalGDD(true);
}

function renderModalGddResults(data) {
  const container = document.getElementById('modalGddContainer');
  if (!container) return;

  const meta = data.metadata || {};
  const ep = data.elevator_pitch || {};
  const cgl = data.core_gameplay_loops || {};
  const usps = data.key_usps || [];
  const ma = data.monetization_architecture || {};
  const liveops = data.liveops_cadence || [];
  const kpi = data.kpi_benchmarks || {};

  container.innerHTML = `
    <!-- High Concept & USPs -->
    <div class="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
      <span class="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
        <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Elevator Pitch & Định Vị Dự Án
      </span>
      <p class="text-xs text-white font-semibold italic">"${ep.logline || ''}"</p>
      <p class="text-[11px] text-slate-300"><strong class="text-emerald-400">Core Hook:</strong> ${ep.core_hook || ''}</p>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-2 pt-1 text-xs">
        ${usps.map(u => `
          <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-[11px]">
            <span class="text-cyan-300 font-bold">✔</span> ${u}
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Core Loops & Monetization -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
      <!-- Core Loops -->
      <div class="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
        <span class="font-bold text-emerald-400 flex items-center gap-1.5">
          <i data-lucide="repeat" class="w-3.5 h-3.5"></i> Vòng Lặp Trải Nghiệm (Core Gameplay Loops)
        </span>
        <div class="space-y-1.5 text-[11px] text-slate-300">
          <p><strong class="text-white">Primary Action Loop:</strong> ${cgl.primary_loop || ''}</p>
          <p><strong class="text-white">Secondary Retention:</strong> ${cgl.secondary_retention_loop || ''}</p>
          <p><strong class="text-white">Tertiary Meta:</strong> ${cgl.tertiary_meta_progression || ''}</p>
        </div>
      </div>

      <!-- Monetization Architecture -->
      <div class="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
        <span class="font-bold text-amber-400 flex items-center gap-1.5">
          <i data-lucide="coins" class="w-3.5 h-3.5"></i> Kiến Trúc Kiếm Tiền (Monetization Spec)
        </span>
        <div class="space-y-1 text-[11px] text-slate-300">
          <p><strong class="text-white">Model:</strong> ${ma.monetization_model || 'Hybrid F2P'}</p>
          <p><strong class="text-white">Revenue Drivers:</strong> ${(ma.primary_revenue_drivers || []).join(', ')}</p>
          <p><strong class="text-white">Battle Pass:</strong> ${ma.battle_pass_structure || ''}</p>
        </div>
      </div>
    </div>

    <!-- KPI Benchmarks -->
    <div class="p-4 rounded-xl bg-gradient-to-r from-cyan-950/30 via-slate-950 to-indigo-950/30 border border-cyan-500/30">
      <span class="text-xs font-bold text-cyan-400 block mb-2.5 flex items-center gap-1.5">
        <i data-lucide="target" class="w-3.5 h-3.5"></i> Mục Tiêu Chỉ Số Hiệu Suất Chuẩn (KPI Benchmarks)
      </span>
      <div class="grid grid-cols-2 sm:grid-cols-6 gap-2 text-center text-xs">
        <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">Target CPI</span>
          <strong class="text-emerald-300 text-sm">${kpi.target_cpi || '$0.45'}</strong>
        </div>
        <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">D1 Retention</span>
          <strong class="text-indigo-300 text-sm">${kpi.d1_retention || '42%'}</strong>
        </div>
        <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">D7 Retention</span>
          <strong class="text-cyan-300 text-sm">${kpi.d7_retention || '18%'}</strong>
        </div>
        <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">D30 Retention</span>
          <strong class="text-purple-300 text-sm">${kpi.d30_retention || '7.5%'}</strong>
        </div>
        <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">D30 LTV</span>
          <strong class="text-amber-300 text-sm">${kpi.d30_ltv || '$1.85'}</strong>
        </div>
        <div class="p-2 rounded-lg bg-slate-900 border border-slate-800">
          <span class="text-[10px] text-slate-400 block">Expected ARPDAU</span>
          <strong class="text-rose-300 text-sm">${kpi.expected_arpdau || kpi.target_arpdau || '$0.35'}</strong>
        </div>
      </div>
    </div>
  `;

  lucide.createIcons();
}

function copyModalGddMarkdown() {
  const md = currentModalGddData?.markdown_export || currentModalGddData?.markdown_gdd;
  if (!md) {
    showToast('Chưa có dữ liệu GDD để sao chép.');
    return;
  }
  navigator.clipboard.writeText(md).then(() => {
    showToast('Đã sao chép tài liệu GDD (.md) vào clipboard!');
  }).catch(err => {
    showToast('Lỗi khi sao chép: ' + err);
  });
}

function downloadModalGddMarkdown() {
  const md = currentModalGddData?.markdown_export || currentModalGddData?.markdown_gdd;
  if (!md) {
    showToast('Chưa có dữ liệu GDD để tải về.');
    return;
  }
  const title = (currentModalGddData?.metadata?.game_title || currentActiveModalGameTitle || 'Game').replace(/[^a-zA-Z0-9_-]/g, '_');
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title}_Game_Design_Document.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Đã tải file GDD (.md) về máy thành công!');
}
