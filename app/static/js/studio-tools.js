/* Playable ads, voiceover, RICE, fraud scanner, MMP stream, GDD studio, pre-reg forecaster */
// --- 1. PLAYABLE AD CANVAS SANDBOX & MRAID EXPORTER ---
let playableTemplates = [];
let sandboxAnimId = null;
let sandboxState = {
  template: 'gate_multiplier',
  playerX: 158,
  playerCount: 10,
  distance: 0,
  gameOver: false,
  won: false,
  gates: [
    { y: 120, leftText: '+10', leftVal: 10, leftType: 'add', rightText: '-5', rightVal: 5, rightType: 'sub' },
    { y: 280, leftText: 'x2', leftVal: 2, leftType: 'mul', rightText: '+5', rightVal: 5, rightType: 'add' },
    { y: 440, leftText: 'x5', leftVal: 5, leftType: 'mul', rightText: '-10', rightVal: 10, rightType: 'sub' }
  ],
  pin1Pulled: false,
  pin2Pulled: false,
  lavaFell: false,
  waterFell: false,
  mergeSlots: [1, 1, 2, 1],
  selectedSlot: null,
  bossHp: 100,
  runnerY: 380,
  runnerVy: 0,
  isJumping: false,
  spikes: [{ x: 260 }, { x: 440 }, { x: 620 }]
};

async function initPlayableTab() {
  try {
    if (!playableTemplates || playableTemplates.length === 0) {
      const res = await fetch('/api/mobile/playable/templates');
      if (res.ok) {
        playableTemplates = await res.json();
      }
    }
    onPlayableTemplateChange();
    setupPlayableCanvasListeners();
    resetPlayableSandbox();
  } catch (e) {
    console.error("Error initializing Playable Studio:", e);
  }
}

function onPlayableTemplateChange() {
  const select = document.getElementById('playableTemplateSelect');
  if (!select) return;
  const tplId = select.value;
  sandboxState.template = tplId;
  const tpl = (playableTemplates && playableTemplates.find(t => t.id === tplId)) || {
    name: select.options[select.selectedIndex].text,
    avg_cvr: '35%',
    description: 'Mô phỏng cơ chế mini-game ad tương tác.',
    hook_mechanic: 'Hook 3s đầu',
    fail_trigger: 'Trigger Endcard'
  };
  const nameEl = document.getElementById('tplCardName');
  const cvrEl = document.getElementById('tplCardCvr');
  const descEl = document.getElementById('tplCardDesc');
  const hookEl = document.getElementById('tplCardHook');
  const trigEl = document.getElementById('tplCardTrigger');
  if (nameEl) nameEl.textContent = tpl.name;
  if (cvrEl) cvrEl.textContent = `Avg CVR: ${tpl.avg_cvr}`;
  if (descEl) descEl.textContent = tpl.description;
  if (hookEl) hookEl.textContent = tpl.hook_mechanic;
  if (trigEl) trigEl.textContent = tpl.fail_trigger;

  resetPlayableSandbox();
}

function setupPlayableCanvasListeners() {
  const canvas = document.getElementById('playableCanvas');
  if (!canvas || canvas.dataset.listening === 'true') return;
  canvas.dataset.listening = 'true';

  const handleMove = (clientX) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const x = (clientX - rect.left) * scaleX;
    sandboxState.playerX = Math.max(30, Math.min(canvas.width - 30, x));
  };

  canvas.addEventListener('mousemove', (e) => {
    if (sandboxState.template === 'gate_multiplier') {
      handleMove(e.clientX);
    }
  });

  canvas.addEventListener('touchmove', (e) => {
    if (e.touches && e.touches[0] && sandboxState.template === 'gate_multiplier') {
      handleMove(e.touches[0].clientX);
    }
  }, { passive: true });

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;

    if (sandboxState.template === 'pull_the_pin') {
      if (clickY > 150 && clickY < 200 && !sandboxState.pin1Pulled) {
        sandboxState.pin1Pulled = true;
        sandboxState.waterFell = true;
      } else if (clickY > 260 && clickY < 310 && !sandboxState.pin2Pulled) {
        sandboxState.pin2Pulled = true;
        sandboxState.lavaFell = true;
      }
    } else if (sandboxState.template === 'merge_weapons') {
      const slotIdx = getMergeSlotUnder(clickX, clickY);
      if (slotIdx !== -1) {
        if (sandboxState.selectedSlot === null) {
          sandboxState.selectedSlot = slotIdx;
        } else if (sandboxState.selectedSlot === slotIdx) {
          sandboxState.selectedSlot = null;
        } else {
          const s1 = sandboxState.selectedSlot;
          const s2 = slotIdx;
          if (sandboxState.mergeSlots[s1] === sandboxState.mergeSlots[s2] && sandboxState.mergeSlots[s1] > 0) {
            sandboxState.mergeSlots[s2] += 1;
            sandboxState.mergeSlots[s1] = 0;
            sandboxState.bossHp = Math.max(0, sandboxState.bossHp - 45);
          }
          sandboxState.selectedSlot = null;
        }
      }
    } else if (sandboxState.template === 'tap_to_dodge') {
      if (!sandboxState.isJumping) {
        sandboxState.isJumping = true;
        sandboxState.runnerVy = -11;
      }
    }
  });
}

function getMergeSlotUnder(x, y) {
  const slots = [
    { x: 50, y: 310, w: 90, h: 70 },
    { x: 176, y: 310, w: 90, h: 70 },
    { x: 50, y: 400, w: 90, h: 70 },
    { x: 176, y: 400, w: 90, h: 70 }
  ];
  for (let i = 0; i < slots.length; i++) {
    const s = slots[i];
    if (x >= s.x && x <= s.x + s.w && y >= s.y && y <= s.y + s.h) return i;
  }
  return -1;
}

function resetPlayableSandbox() {
  if (sandboxAnimId) cancelAnimationFrame(sandboxAnimId);
  const endcard = document.getElementById('canvasEndcardOverlay');
  if (endcard) {
    endcard.classList.add('hidden');
    endcard.classList.remove('flex');
  }

  sandboxState.playerCount = 10;
  sandboxState.playerX = 158;
  sandboxState.distance = 0;
  sandboxState.gameOver = false;
  sandboxState.won = false;
  sandboxState.pin1Pulled = false;
  sandboxState.pin2Pulled = false;
  sandboxState.waterFell = false;
  sandboxState.lavaFell = false;
  sandboxState.mergeSlots = [1, 1, 2, 1];
  sandboxState.selectedSlot = null;
  sandboxState.bossHp = 100;
  sandboxState.runnerY = 380;
  sandboxState.runnerVy = 0;
  sandboxState.isJumping = false;
  sandboxState.spikes = [{ x: 260 }, { x: 440 }, { x: 620 }];
  sandboxState.gates = [
    { y: 120, leftText: '+10', leftVal: 10, leftType: 'add', rightText: '-5', rightVal: 5, rightType: 'sub', passed: false },
    { y: 280, leftText: 'x2', leftVal: 2, leftType: 'mul', rightText: '+5', rightVal: 5, rightType: 'add', passed: false },
    { y: 440, leftText: 'x5', leftVal: 5, leftType: 'mul', rightText: '-10', rightVal: 10, rightType: 'sub', passed: false }
  ];

  startPlayableLoop();
}

function startPlayableLoop() {
  const canvas = document.getElementById('playableCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let lastTime = performance.now();

  function loop(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;

    updateSandbox(dt);
    renderSandbox(ctx, canvas.width, canvas.height);

    if (!sandboxState.gameOver) {
      sandboxAnimId = requestAnimationFrame(loop);
    } else {
      showSandboxEndcard();
    }
  }

  sandboxAnimId = requestAnimationFrame(loop);
}

function updateSandbox(dt) {
  if (sandboxState.gameOver) return;

  if (sandboxState.template === 'gate_multiplier') {
    sandboxState.distance += 75 * dt;
    for (let g of sandboxState.gates) {
      const sy = 460 - (sandboxState.distance * 1.3 - g.y);
      if (sy > 390 && sy < 430 && !g.passed) {
        g.passed = true;
        if (sandboxState.playerX < 158) {
          if (g.leftType === 'add') sandboxState.playerCount += g.leftVal;
          else if (g.leftType === 'mul') sandboxState.playerCount *= g.leftVal;
          else if (g.leftType === 'sub') sandboxState.playerCount -= g.leftVal;
        } else {
          if (g.rightType === 'add') sandboxState.playerCount += g.rightVal;
          else if (g.rightType === 'mul') sandboxState.playerCount *= g.rightVal;
          else if (g.rightType === 'sub') sandboxState.playerCount -= g.rightVal;
        }
      }
    }
    if (sandboxState.playerCount <= 0) {
      sandboxState.gameOver = true;
      sandboxState.won = false;
    } else if (sandboxState.distance > 420) {
      sandboxState.gameOver = true;
      sandboxState.won = true;
    }
  } else if (sandboxState.template === 'pull_the_pin') {
    if (sandboxState.waterFell && sandboxState.lavaFell) {
      sandboxState.gameOver = true;
      sandboxState.won = true;
    } else if (sandboxState.lavaFell && !sandboxState.waterFell) {
      sandboxState.gameOver = true;
      sandboxState.won = false;
    }
  } else if (sandboxState.template === 'merge_weapons') {
    if (sandboxState.bossHp <= 10) {
      sandboxState.gameOver = true;
      sandboxState.won = true;
    }
  } else if (sandboxState.template === 'tap_to_dodge') {
    if (sandboxState.isJumping) {
      sandboxState.runnerVy += 28 * dt;
      sandboxState.runnerY += sandboxState.runnerVy;
      if (sandboxState.runnerY >= 380) {
        sandboxState.runnerY = 380;
        sandboxState.isJumping = false;
        sandboxState.runnerVy = 0;
      }
    }
    for (let s of sandboxState.spikes) {
      s.x -= 160 * dt;
      if (s.x > 50 && s.x < 95 && sandboxState.runnerY > 350) {
        sandboxState.gameOver = true;
        sandboxState.won = false;
      }
    }
    if (sandboxState.spikes[sandboxState.spikes.length - 1].x < 20) {
      sandboxState.gameOver = true;
      sandboxState.won = true;
    }
  }
}

function renderSandbox(ctx, w, h) {
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, w, h);

  if (sandboxState.template === 'gate_multiplier') {
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(20, 0, w - 40, h);
    ctx.strokeStyle = '#334155';
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(w / 2, 0);
    ctx.lineTo(w / 2, h);
    ctx.stroke();
    ctx.setLineDash([]);

    for (let g of sandboxState.gates) {
      const sy = 460 - (sandboxState.distance * 1.3 - g.y);
      if (sy > -50 && sy < h + 50) {
        ctx.fillStyle = g.leftType === 'sub' ? 'rgba(239, 68, 68, 0.85)' : 'rgba(16, 185, 129, 0.85)';
        ctx.fillRect(24, sy - 20, (w - 48) / 2, 36);
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(g.leftText, 24 + (w - 48) / 4, sy + 4);

        ctx.fillStyle = g.rightType === 'sub' ? 'rgba(239, 68, 68, 0.85)' : 'rgba(16, 185, 129, 0.85)';
        ctx.fillRect(w / 2 + 2, sy - 20, (w - 48) / 2 - 2, 36);
        ctx.fillStyle = '#ffffff';
        ctx.fillText(g.rightText, w / 2 + (w - 48) / 4, sy + 4);
      }
    }

    const px = sandboxState.playerX;
    const py = 410;
    ctx.fillStyle = '#38bdf8';
    ctx.beginPath();
    ctx.arc(px, py, 14, 0, Math.PI * 2);
    ctx.fill();

    const displayFollowers = Math.min(20, Math.max(0, sandboxState.playerCount));
    ctx.fillStyle = '#7dd3fc';
    for (let i = 0; i < displayFollowers; i++) {
      const angle = (i / displayFollowers) * Math.PI * 2;
      const rad = 14 + (i % 3) * 6;
      ctx.beginPath();
      ctx.arc(px + Math.cos(angle) * rad, py + Math.sin(angle) * rad + 10, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = '#0284c7';
    ctx.fillRect(px - 28, py - 40, 56, 18);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`LÍNH: ${Math.max(0, sandboxState.playerCount)}`, px, py - 27);

  } else if (sandboxState.template === 'pull_the_pin') {
    ctx.fillStyle = '#1e1b4b';
    ctx.fillRect(40, 40, w - 80, 430);

    ctx.fillStyle = sandboxState.pin1Pulled ? '#0284c7' : '#38bdf8';
    ctx.fillRect(60, 60, w - 120, 80);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('💧 NƯỚC MÁT', w / 2, 105);

    ctx.fillStyle = sandboxState.pin1Pulled ? '#475569' : '#f59e0b';
    ctx.fillRect(sandboxState.pin1Pulled ? 180 : 30, 150, w - 60, 14);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px sans-serif';
    ctx.fillText(sandboxState.pin1Pulled ? 'ĐÃ RÚT CHỐT 1' : '👉 BẤM ĐỂ RÚT CHỐT NƯỚC', w / 2, 145);

    ctx.fillStyle = sandboxState.lavaFell ? (sandboxState.waterFell ? '#64748b' : '#ef4444') : '#f97316';
    ctx.fillRect(60, 175, w - 120, 80);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px sans-serif';
    ctx.fillText(sandboxState.waterFell ? '🪨 ĐÁ NGUỘI' : '🔥 DUNG NHAM NÓNG', w / 2, 220);

    ctx.fillStyle = sandboxState.pin2Pulled ? '#475569' : '#f59e0b';
    ctx.fillRect(sandboxState.pin2Pulled ? 180 : 30, 265, w - 60, 14);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px sans-serif';
    ctx.fillText(sandboxState.pin2Pulled ? 'ĐÃ RÚT CHỐT 2' : '👉 BẤM ĐỂ RÚT CHỐT LỬA', w / 2, 260);

    ctx.fillStyle = '#10b981';
    ctx.fillRect(60, 370, 45, 50);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 11px sans-serif';
    ctx.fillText('🧙 HERO', 82, 400);

    ctx.fillStyle = '#fbbf24';
    ctx.fillRect(w - 110, 380, 45, 40);
    ctx.fillText('💎 KHO BÁU', w - 88, 405);

  } else if (sandboxState.template === 'merge_weapons') {
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(w / 2 - 50, 60, 100, 90);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('👹 WORLD BOSS', w / 2, 105);

    ctx.fillStyle = '#334155';
    ctx.fillRect(w / 2 - 70, 165, 140, 12);
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(w / 2 - 70, 165, 140 * (sandboxState.bossHp / 100), 12);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px sans-serif';
    ctx.fillText(`HP: ${sandboxState.bossHp}%`, w / 2, 160);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px sans-serif';
    ctx.fillText('Chạm 2 thanh kiếm cùng cấp để ghép Level!', w / 2, 260);

    const slots = [
      { x: 50, y: 290, w: 90, h: 70 },
      { x: 176, y: 290, w: 90, h: 70 },
      { x: 50, y: 380, w: 90, h: 70 },
      { x: 176, y: 380, w: 90, h: 70 }
    ];
    for (let i = 0; i < slots.length; i++) {
      const s = slots[i];
      const val = sandboxState.mergeSlots[i];
      const isSel = sandboxState.selectedSlot === i;
      ctx.fillStyle = isSel ? 'rgba(99, 102, 241, 0.4)' : '#1e293b';
      ctx.strokeStyle = isSel ? '#818cf8' : '#334155';
      ctx.lineWidth = 2;
      ctx.fillRect(s.x, s.y, s.w, s.h);
      ctx.strokeRect(s.x, s.y, s.w, s.h);

      if (val > 0) {
        ctx.fillStyle = val === 1 ? '#e2e8f0' : (val === 2 ? '#38bdf8' : '#fbbf24');
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText(`🗡️ KIẾM Lv.${val}`, s.x + s.w / 2, s.y + s.h / 2 + 4);
      }
    }

  } else if (sandboxState.template === 'tap_to_dodge') {
    ctx.fillStyle = '#334155';
    ctx.fillRect(0, 410, w, 110);

    ctx.fillStyle = '#38bdf8';
    ctx.fillRect(70, sandboxState.runnerY, 26, 30);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('RUN', 83, sandboxState.runnerY + 18);

    for (let s of sandboxState.spikes) {
      if (s.x > -20 && s.x < w + 20) {
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.moveTo(s.x, 410);
        ctx.lineTo(s.x + 12, 382);
        ctx.lineTo(s.x + 24, 410);
        ctx.fill();
      }
    }

    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px sans-serif';
    ctx.fillText('Chạm màn hình để nhảy qua chông gai!', w / 2, 200);
  }
}

function showSandboxEndcard() {
  const overlay = document.getElementById('canvasEndcardOverlay');
  const title = document.getElementById('endcardTitle');
  const desc = document.getElementById('endcardDesc');
  const cta = document.getElementById('endcardCtaBtn');
  const customCta = document.getElementById('playableCtaText').value.trim() || 'CHƠI NGAY MIỄN PHÍ';

  if (!overlay) return;
  overlay.classList.remove('hidden');
  overlay.classList.add('flex');

  if (sandboxState.won) {
    title.textContent = 'CHIẾN THẮNG TUYỆT ĐỐI!';
    title.className = 'text-lg font-black text-amber-400 uppercase tracking-wider';
    desc.textContent = 'Bạn đã vượt qua màn chơi xuất sắc! Tải bản full để mở khóa 100+ ải tiếp theo!';
  } else {
    title.textContent = 'THUA RỒI! BẠN CÓ DÁM THỬ LẠI?';
    title.className = 'text-lg font-black text-rose-500 uppercase tracking-wider';
    desc.textContent = '99% người chơi không thể vượt qua cạm bẫy này! Cài đặt game để phục thù ngay!';
  }
  if (cta) cta.textContent = customCta;
  lucide.createIcons();
}

function triggerSandboxCta() {
  const url = document.getElementById('playableStoreUrl').value.trim() || 'https://apps.apple.com';
  showToast(`[MRAID 2.0] Kích hoạt mraid.open("${url}")`);
}

async function exportMraidBundle() {
  const templateId = document.getElementById('playableTemplateSelect').value;
  const gameTitle = document.getElementById('playableGameTitle').value.trim() || 'Stickman War';
  const ctaText = document.getElementById('playableCtaText').value.trim() || 'PLAY NOW';
  const storeUrl = document.getElementById('playableStoreUrl').value.trim() || 'https://apps.apple.com';

  try {
    const res = await fetch('/api/mobile/playable/export-mraid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: templateId,
        game_title: gameTitle,
        call_to_action: ctaText,
        store_url: storeUrl
      })
    });
    if (res.ok) {
      const html = await res.text();
      const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${gameTitle.toLowerCase().replace(/[^a-z0-9]/g, '_')}_playable_ad.html`;
      link.click();
      showToast('Đã xuất và tải file Playable Ad MRAID 2.0 (.html) thành công!');
    }
  } catch (e) {
    console.error("Error exporting MRAID bundle:", e);
    showToast('Có lỗi khi xuất file MRAID bundle.');
  }
}

async function togglePlayableCodeModal() {
  const modal = document.getElementById('playableCodeModal');
  if (!modal) return;
  if (!modal.classList.contains('hidden')) {
    modal.classList.add('hidden');
    return;
  }

  const templateId = document.getElementById('playableTemplateSelect').value;
  const gameTitle = document.getElementById('playableGameTitle').value.trim() || 'Stickman War';
  const ctaText = document.getElementById('playableCtaText').value.trim() || 'PLAY NOW';
  const storeUrl = document.getElementById('playableStoreUrl').value.trim() || 'https://apps.apple.com';

  try {
    const res = await fetch('/api/mobile/playable/export-mraid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: templateId,
        game_title: gameTitle,
        call_to_action: ctaText,
        store_url: storeUrl
      })
    });
    if (res.ok) {
      const html = await res.text();
      document.getElementById('playableCodeArea').value = html;
      modal.classList.remove('hidden');
      lucide.createIcons();
    }
  } catch (e) {
    console.error("Error loading code preview:", e);
  }
}

function copyMraidCode() {
  const area = document.getElementById('playableCodeArea');
  if (area) {
    navigator.clipboard.writeText(area.value);
    showToast('Đã sao chép mã nguồn HTML5 MRAID vào clipboard!');
  }
}

// --- 2. MULTILINGUAL AD VOICEOVER & AUDIO PREVIEW STUDIO ---
let currentVoDuration = 15;
let currentVoiceoverData = null;

function initVoiceoverTab() {
  if (!currentVoiceoverData) {
    generateVoiceoverScript();
  }
}

function setVoDuration(dur) {
  currentVoDuration = dur;
  const btn15 = document.getElementById('voBtnDur15');
  const btn30 = document.getElementById('voBtnDur30');
  if (dur === 15) {
    btn15.className = 'py-2 rounded-lg bg-rose-600 text-white font-bold text-xs border border-rose-500';
    btn30.className = 'py-2 rounded-lg bg-slate-800 text-slate-300 font-bold text-xs border border-slate-700 hover:bg-slate-700';
  } else {
    btn30.className = 'py-2 rounded-lg bg-rose-600 text-white font-bold text-xs border border-rose-500';
    btn15.className = 'py-2 rounded-lg bg-slate-800 text-slate-300 font-bold text-xs border border-slate-700 hover:bg-slate-700';
  }
  generateVoiceoverScript();
}

async function generateVoiceoverScript() {
  const title = document.getElementById('voGameTitle').value.trim() || 'Shadow Legends War';
  const genre = document.getElementById('voGenre').value.trim() || 'Mid-Core RPG';
  const market = document.getElementById('voTargetMarket').value;
  const emotion = document.getElementById('voEmotionTone').value;

  try {
    const res = await fetch('/api/mobile/voiceover/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_title: title,
        genre: genre,
        target_market: market,
        emotion_tone: emotion,
        duration_seconds: currentVoDuration
      })
    });

    if (res.ok) {
      const data = await res.json();
      currentVoiceoverData = data;
      renderVoiceoverScript(data);
    }
  } catch (e) {
    console.error("Error generating voiceover:", e);
  }
}

function renderVoiceoverScript(data) {
  const hookAdvice = document.getElementById('voHookAdvice');
  const bgmAdvice = document.getElementById('voBgmAdvice');
  const castingAdvice = document.getElementById('voCastingAdvice');
  if (hookAdvice) hookAdvice.textContent = data.marketing_tactics.hook_tactic;
  if (bgmAdvice) bgmAdvice.textContent = data.meta.bgm_recommendation;
  if (castingAdvice) castingAdvice.textContent = data.meta.casting_advice;

  const container = document.getElementById('voTimelineContainer');
  if (!container) return;

  container.innerHTML = data.timeline.map(line => `
    <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-2 hover:border-rose-500/30 transition-colors">
      <div class="flex items-center justify-between text-xs">
        <span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold font-mono text-[11px]">
          ⏱️ ${line.time}
        </span>
        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
          ${line.section}
        </span>
      </div>
      <div class="p-3 rounded-lg bg-slate-950 border border-rose-500/20 text-sm font-semibold text-rose-200 leading-relaxed">
        "${line.voice_text}"
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] pt-1">
        <div class="text-slate-400">
          🎬 <b class="text-slate-300 font-medium">Khung Hình:</b> ${line.screen_direction}
        </div>
        <div class="text-amber-400/90 font-mono">
          🔊 <b class="text-amber-300 font-medium">SFX Cue:</b> ${line.sfx_cue}
        </div>
      </div>
    </div>
  `).join('');

  lucide.createIcons();
}

function playVoiceoverSpeech() {
  if (!('speechSynthesis' in window)) {
    showToast('Trình duyệt của bạn không hỗ trợ Web Speech Synthesis.');
    return;
  }

  if (!currentVoiceoverData || !currentVoiceoverData.tts_parameters) return;
  window.speechSynthesis.cancel();

  const tts = currentVoiceoverData.tts_parameters;
  const utterance = new SpeechSynthesisUtterance(tts.full_text);
  utterance.lang = tts.lang;
  utterance.pitch = tts.pitch;
  utterance.rate = tts.rate;

  const indicator = document.getElementById('voSpeakingIndicator');
  if (indicator) indicator.classList.remove('hidden');

  utterance.onend = () => {
    if (indicator) indicator.classList.add('hidden');
  };
  utterance.onerror = () => {
    if (indicator) indicator.classList.add('hidden');
  };

  window.speechSynthesis.speak(utterance);
  showToast(`Đang phát giọng đọc audio (${tts.lang}, tốc độ ${tts.rate}x)`);
}

function stopVoiceoverSpeech() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const indicator = document.getElementById('voSpeakingIndicator');
    if (indicator) indicator.classList.add('hidden');
  }
}

function copyFullVoiceoverScript() {
  if (!currentVoiceoverData) return;
  let text = `=== KỊCH BẢN LỒNG TIẾNG VIDEO ADS: ${currentVoiceoverData.meta.game_title} ===\n`;
  text += `Thị Trường: ${currentVoiceoverData.meta.market_name} (${currentVoiceoverData.meta.lang_code})\n`;
  text += `Tông Cảm Xúc: ${currentVoiceoverData.meta.emotion_name}\n`;
  text += `BGM Đề Xuất: ${currentVoiceoverData.meta.bgm_recommendation}\n\n`;

  currentVoiceoverData.timeline.forEach(item => {
    text += `[${item.time}] (${item.section})\n`;
    text += `Lời Thoại: "${item.voice_text}"\n`;
    text += `Hình Ảnh: ${item.screen_direction}\n`;
    text += `Âm Thanh SFX: ${item.sfx_cue}\n\n`;
  });

  navigator.clipboard.writeText(text);
  showToast('Đã sao chép toàn bộ kịch bản lồng tiếng vào clipboard!');
}

// --- 3. GAME FEATURE RICE SCORER & PRODUCTION ROADMAP ---
let ricePresetsData = [];

async function initRiceTab() {
  try {
    if (!ricePresetsData || ricePresetsData.length === 0) {
      const res = await fetch('/api/mobile/rice/presets');
      if (res.ok) {
        ricePresetsData = await res.json();
      }
    }
    recalculateRiceMatrix();
  } catch (e) {
    console.error("Error initializing RICE Scorer:", e);
  }
}

async function recalculateRiceMatrix() {
  try {
    const res = await fetch('/api/mobile/rice/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        features: ricePresetsData
      })
    });

    if (res.ok) {
      const data = await res.json();
      renderRiceResults(data);
    }
  } catch (e) {
    console.error("Error recalculating RICE:", e);
  }
}

function renderRiceResults(data) {
  const summary = data.summary;
  const topFeatEl = document.getElementById('riceTopFeature');
  const totalFeatEl = document.getElementById('riceTotalFeatures');
  const totalEffortEl = document.getElementById('riceTotalEffort');
  const projRevEl = document.getElementById('riceProjectedRev');
  const projD30El = document.getElementById('riceProjectedD30');

  if (topFeatEl) topFeatEl.textContent = summary.highest_roi_feature;
  if (totalFeatEl) totalFeatEl.textContent = summary.total_features_evaluated;
  if (totalEffortEl) totalEffortEl.textContent = `${summary.total_engineering_weeks} wks`;
  if (projRevEl) projRevEl.textContent = `+${summary.cumulative_top5_rev_lift_pct}%`;
  if (projD30El) projD30El.textContent = `+${summary.cumulative_top5_d30_lift_pct}%`;

  const tbody = document.getElementById('riceTableBody');
  if (tbody) {
    tbody.innerHTML = data.ranked_features.map((feat, idx) => `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="py-3 px-4 font-semibold text-white">
          <div class="flex items-center gap-2">
            <span class="w-5 h-5 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] text-slate-300 font-bold">
              ${idx + 1}
            </span>
            <div>
              <div class="font-bold text-slate-100">${feat.name}</div>
              <div class="text-[10px] text-slate-400 font-normal max-w-sm truncate">${feat.description}</div>
            </div>
          </div>
        </td>
        <td class="py-3 px-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${feat.category.includes('Monetization') ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : (feat.category.includes('Retention') ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'bg-purple-500/20 text-purple-300 border border-purple-500/30')}">
            ${feat.category}
          </span>
        </td>
        <td class="py-3 px-3 font-mono text-slate-300">${feat.reach.toLocaleString()}</td>
        <td class="py-3 px-3 font-mono text-slate-300">${feat.impact}x</td>
        <td class="py-3 px-3 font-mono text-slate-300">${Math.round(feat.confidence * 100)}%</td>
        <td class="py-3 px-3 font-mono text-amber-300">${feat.effort} w</td>
        <td class="py-3 px-3">
          <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-violet-500/20 text-violet-300 border border-violet-500/40">
            ${feat.rice_score}
          </span>
        </td>
        <td class="py-3 px-3 font-bold text-emerald-400 font-mono">+${feat.projected_revenue_lift_pct}%</td>
        <td class="py-3 px-3 font-bold text-cyan-400 font-mono">+${feat.projected_d30_retention_lift_pct}%</td>
        <td class="py-3 px-4">
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${feat.priority_tier.includes('P0') ? 'bg-red-500/20 text-red-400 border border-red-500/30' : (feat.priority_tier.includes('P1') ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-slate-700 text-slate-300')}">
            ${feat.priority_tier}
          </span>
        </td>
      </tr>
    `).join('');
  }

  const roadmapGrid = document.getElementById('riceRoadmapGrid');
  if (roadmapGrid) {
    roadmapGrid.innerHTML = Object.entries(data.quarterly_roadmap).map(([sprintName, items]) => `
      <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-3 bg-slate-900/60">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h5 class="text-xs font-bold text-violet-300 flex items-center gap-1.5">
            <i data-lucide="clock" class="w-3.5 h-3.5"></i>
            ${sprintName}
          </h5>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
            ${items.reduce((acc, i) => acc + i.effort, 0).toFixed(1)} wks
          </span>
        </div>
        <div class="space-y-2">
          ${items.length === 0 ? '<div class="text-[11px] text-slate-400 py-2">Chưa phân bổ tính năng</div>' : items.map(item => `
            <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div class="flex items-center justify-between">
                <span class="font-bold text-white text-[11px] truncate max-w-[190px]">${item.name}</span>
                <span class="text-[10px] font-black text-violet-400 font-mono">RICE: ${item.rice_score}</span>
              </div>
              <div class="flex items-center gap-2 text-[10px] text-slate-400">
                <span class="text-amber-400">${item.effort} tuần</span>
                <span>•</span>
                <span class="text-emerald-400">+${item.projected_revenue_lift_pct}% Rev</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  lucide.createIcons();
}

// --- 4. UA AD FRAUD & CLICK INJECTION SCANNER ---
let fraudSamples = [];

async function initFraudTab() {
  try {
    if (!fraudSamples || fraudSamples.length === 0) {
      const res = await fetch('/api/mobile/fraud/samples');
      if (res.ok) {
        fraudSamples = await res.json();
      }
    }
    auditAdFraud();
  } catch (e) {
    console.error("Error initializing Fraud Scanner:", e);
  }
}

function loadFraudPreset(index) {
  if (!fraudSamples || !fraudSamples[index]) return;
  const s = fraudSamples[index];
  document.getElementById('fraudNetName').value = s.network_name;
  document.getElementById('fraudInstalls').value = s.total_installs;
  document.getElementById('fraudSpend').value = s.ad_spend_usd;
  document.getElementById('fraudMttiUnder10').value = s.mtti_under_10s_pct;
  document.getElementById('fraudMttiOver24').value = s.mtti_over_24h_pct;
  document.getElementById('fraudD1Ret').value = s.d1_retention_pct;

  auditAdFraud();
}

async function auditAdFraud() {
  const netName = document.getElementById('fraudNetName').value.trim() || 'Custom Network';
  const installs = parseInt(document.getElementById('fraudInstalls').value, 10) || 10000;
  const spend = parseFloat(document.getElementById('fraudSpend').value) || 10000;
  const under10 = parseFloat(document.getElementById('fraudMttiUnder10').value) || 0;
  const over24 = parseFloat(document.getElementById('fraudMttiOver24').value) || 0;
  const d1 = parseFloat(document.getElementById('fraudD1Ret').value) || 0;

  try {
    const res = await fetch('/api/mobile/fraud/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        network_name: netName,
        total_installs: installs,
        ad_spend_usd: spend,
        mtti_under_10s_pct: under10,
        mtti_over_24h_pct: over24,
        d1_retention_pct: d1
      })
    });

    if (res.ok) {
      const data = await res.json();
      renderFraudResults(data);
    }
  } catch (e) {
    console.error("Error auditing fraud:", e);
  }
}

function renderFraudResults(data) {
  const verdict = data.audit_verdict;
  const verdictEl = document.getElementById('fraudVerdictText');
  const scoreEl = document.getElementById('fraudRiskScore');
  const clawbackEl = document.getElementById('fraudClawbackUsd');
  const countEl = document.getElementById('fraudInstallCount');
  const pctEl = document.getElementById('fraudInstallPct');
  const safeEl = document.getElementById('fraudSafeSpendUsd');

  if (verdictEl) verdictEl.textContent = verdict.overall_verdict;
  if (scoreEl) {
    scoreEl.textContent = `RỦI RO: ${verdict.fraud_score}/100`;
    scoreEl.className = verdict.fraud_score > 50 ? 'px-3 py-1 rounded-full text-xs font-black bg-red-500/20 text-red-400 border border-red-500/40' : (verdict.fraud_score > 25 ? 'px-3 py-1 rounded-full text-xs font-black bg-amber-500/20 text-amber-400 border border-amber-500/40' : 'px-3 py-1 rounded-full text-xs font-black bg-emerald-500/20 text-emerald-400 border border-emerald-500/40');
  }
  if (clawbackEl) clawbackEl.textContent = `$${verdict.estimated_clawback_usd.toLocaleString()}`;
  if (countEl) countEl.textContent = `${verdict.fraud_installs_count.toLocaleString()} installs`;
  if (pctEl) pctEl.textContent = `Chiếm ${verdict.estimated_fraud_pct}% toàn chiến dịch`;
  if (safeEl) safeEl.textContent = `$${verdict.safe_spend_usd.toLocaleString()}`;

  const barsContainer = document.getElementById('fraudMttiBars');
  if (barsContainer) {
    barsContainer.innerHTML = data.mtti_distribution.map(b => {
      const colorClass = b.status === 'danger' ? 'bg-red-500' : (b.status === 'healthy' ? 'bg-emerald-500' : (b.status === 'warning' ? 'bg-amber-500' : 'bg-slate-600'));
      const textClass = b.status === 'danger' ? 'text-red-400 font-bold' : (b.status === 'healthy' ? 'text-emerald-400 font-bold' : 'text-slate-300');
      return `
        <div class="space-y-1">
          <div class="flex items-center justify-between text-xs">
            <span class="${textClass}">${b.bucket}</span>
            <span class="font-mono ${textClass}">${b.pct}%</span>
          </div>
          <div class="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden">
            <div class="${colorClass} h-2.5 rounded-full" style="width: ${Math.min(100, b.pct * 1.5)}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  const flagsContainer = document.getElementById('fraudFlagsList');
  if (flagsContainer) {
    if (!data.fraud_flags || data.fraud_flags.length === 0) {
      flagsContainer.innerHTML = `
        <div class="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <i data-lucide="check-circle" class="w-5 h-5 text-emerald-400"></i>
          <span>Không phát hiện dấu hiệu gian lận nghiêm trọng. Phân bổ MTTI đạt chuẩn tự nhiên.</span>
        </div>
      `;
    } else {
      flagsContainer.innerHTML = data.fraud_flags.map(f => `
        <div class="p-4 rounded-xl ${f.severity === 'CRITICAL' ? 'bg-red-950/30 border border-red-500/40' : 'bg-amber-950/20 border border-amber-500/30'} space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold ${f.severity === 'CRITICAL' ? 'text-red-400' : 'text-amber-400'} text-xs flex items-center gap-1.5">
              <i data-lucide="alert-triangle" class="w-4 h-4"></i>
              ${f.type}
            </span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded ${f.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-300' : 'bg-amber-500/20 text-amber-300'}">
              ${f.severity}
            </span>
          </div>
          <p class="text-xs text-white font-medium">${f.finding}</p>
          <div class="text-[11px] text-slate-300 pt-1 border-t border-slate-800">
            <b class="text-slate-400">Cơ Chế Gian Lận:</b> ${f.mechanism}
          </div>
          <div class="text-[11px] text-cyan-300">
            <b class="text-cyan-400">Biện Pháp Khắc Phục:</b> ${f.action}
          </div>
        </div>
      `).join('');
    }
  }

  const afList = document.getElementById('afRulesList');
  if (afList && data.rulebook.appsflyer_protect360_rules) {
    afList.innerHTML = data.rulebook.appsflyer_protect360_rules.map(r => `
      <li><b>${r.rule_name}:</b> If ${r.condition} &rarr; <i>${r.action}</i></li>
    `).join('');
  }

  const adjustList = document.getElementById('adjustRulesList');
  if (adjustList && data.rulebook.adjust_fraud_prevention_suite) {
    adjustList.innerHTML = data.rulebook.adjust_fraud_prevention_suite.map(r => `
      <li><b>${r.filter_name}:</b> ${r.threshold} [${r.status}]</li>
    `).join('');
  }

  const letterArea = document.getElementById('clawbackLetterText');
  if (letterArea && data.rulebook.clawback_email_template) {
    letterArea.value = data.rulebook.clawback_email_template;
  }

  lucide.createIcons();
}

function copyClawbackLetter() {
  const area = document.getElementById('clawbackLetterText');
  if (area) {
    navigator.clipboard.writeText(area.value);
    showToast('Đã sao chép thư khiếu nại hoàn tiền Clawback vào clipboard!');
  }
}

// --- 5. MMP LIVE WEBHOOK INGESTION & FRAUD STREAM ---
async function initMmpStreamTab() {
  loadMmpStatsAndRecent();
}

async function loadMmpStatsAndRecent() {
  try {
    const [statsRes, recentRes] = await Promise.all([
      fetch('/api/webhook/mmp/stats'),
      fetch('/api/webhook/mmp/recent?limit=50')
    ]);

    if (statsRes.ok) {
      const stats = await statsRes.json();
      renderMmpStats(stats);
    }

    if (recentRes.ok) {
      const recent = await recentRes.json();
      renderMmpRecentFeed(recent);
    }
  } catch (e) {
    console.error("Error loading MMP stats:", e);
  }
}

function renderMmpStats(stats) {
  const totalEl = document.getElementById('mmpTotalCount');
  const cleanEl = document.getElementById('mmpCleanCount');
  const rejEl = document.getElementById('mmpRejectedCount');
  const rateEl = document.getElementById('mmpFraudRate');
  const ctitEl = document.getElementById('mmpAvgCtit');

  if (totalEl) {
    totalEl.textContent = stats.total_postbacks.toLocaleString();
    let demoBadge = document.getElementById('mmpSimulatedBadge');
    if (!demoBadge) {
      demoBadge = document.createElement('span');
      demoBadge.id = 'mmpSimulatedBadge';
      demoBadge.className = 'ml-2 px-1.5 py-0.5 rounded text-[10px] font-black bg-amber-500/20 text-amber-300 border border-amber-500/30 align-middle';
      totalEl.insertAdjacentElement('afterend', demoBadge);
    }
    const sim = stats.simulated_count || 0;
    demoBadge.textContent = sim > 0 ? `DEMO: ${sim.toLocaleString()} sự kiện giả lập` : '';
    demoBadge.style.display = sim > 0 ? '' : 'none';
  }
  if (cleanEl) cleanEl.textContent = stats.clean_count.toLocaleString();
  if (rejEl) rejEl.textContent = stats.rejected_count.toLocaleString();
  if (rateEl) {
    rateEl.textContent = `${stats.fraud_rate_pct}%`;
    rateEl.className = stats.fraud_rate_pct > 25 ? 'text-2xl font-black text-red-400 mt-1 block' : (stats.fraud_rate_pct > 10 ? 'text-2xl font-black text-amber-400 mt-1 block' : 'text-2xl font-black text-emerald-400 mt-1 block');
  }
  if (ctitEl) ctitEl.textContent = `${stats.avg_ctit_seconds}s`;

  const tbody = document.getElementById('mmpNetworksTableBody');
  if (tbody) {
    if (!stats.networks_breakdown || stats.networks_breakdown.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-slate-500">Chưa có dữ liệu postback. Hãy bấm "Mô Phỏng 15 Postback Mới" để kiểm tra!</td></tr>`;
    } else {
      tbody.innerHTML = stats.networks_breakdown.map(n => `
        <tr class="hover:bg-slate-800/40 transition-colors">
          <td class="py-3 px-4 font-bold text-white">${n.network_name}</td>
          <td class="py-3 px-3 font-mono text-slate-300">${n.total_events.toLocaleString()}</td>
          <td class="py-3 px-3 font-mono font-bold ${n.fraud_events > 0 ? 'text-red-400' : 'text-slate-400'}">${n.fraud_events}</td>
          <td class="py-3 px-3 font-bold font-mono ${n.fraud_rate_pct > 25 ? 'text-red-400' : (n.fraud_rate_pct > 10 ? 'text-amber-400' : 'text-emerald-400')}">${n.fraud_rate_pct}%</td>
          <td class="py-3 px-3 font-mono text-slate-300">${n.avg_ctit}s</td>
          <td class="py-3 px-4 text-center">
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${n.status === 'DANGER' ? 'bg-red-500/20 text-red-300 border border-red-500/40' : (n.status === 'WARNING' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40')}">
              ${n.status === 'DANGER' ? '🚨 NGUY CƠ CAO' : (n.status === 'WARNING' ? '⚠️ THEO DÕI' : '✅ AN TOÀN')}
            </span>
          </td>
        </tr>
      `).join('');
    }
  }
}

function renderMmpRecentFeed(items) {
  const tbody = document.getElementById('mmpFeedTableBody');
  if (!tbody) return;

  if (!items || items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-500 font-sans">Chưa có sự kiện attribution nào.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map(item => {
    let badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">CLEAN</span>';
    if (item.fraud_verdict === 'CLICK_INJECTION') {
      badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/40 animate-pulse">CLICK_INJECTION</span>';
    } else if (item.fraud_verdict === 'CLICK_FLOODING') {
      badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">CLICK_FLOODING</span>';
    } else if (item.fraud_verdict === 'BOT_EMULATOR') {
      badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-400 border border-purple-500/40">BOT_EMULATOR</span>';
    }

    return `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="py-2.5 px-4 text-slate-400">${item.received_at.split(' ')[1] || item.received_at}</td>
        <td class="py-2.5 px-3 text-slate-300">${item.mmp_provider}</td>
        <td class="py-2.5 px-3 font-bold text-white">${item.network_name}</td>
        <td class="py-2.5 px-3 text-slate-400 truncate max-w-[120px]">${item.campaign_name || '--'}</td>
        <td class="py-2.5 px-3 text-slate-400 truncate max-w-[110px]">${item.device_model}</td>
        <td class="py-2.5 px-3 font-bold ${item.ctit_seconds < 10 ? 'text-red-400' : 'text-cyan-400'}">${item.ctit_seconds}s</td>
        <td class="py-2.5 px-3">${badge}</td>
        <td class="py-2.5 px-4 text-center">
          <span class="text-[10px] ${item.is_rejected === 1 ? 'text-red-400 font-bold' : 'text-emerald-400 font-semibold'}">
            ${item.is_rejected === 1 ? 'REJECTED' : 'ATTRIBUTED'}
          </span>
        </td>
      </tr>
    `;
  }).join('');
}

async function simulateMmpBatch() {
  try {
    const res = await fetch('/api/webhook/mmp/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count: 15 })
    });
    if (res.ok) {
      showToast('Đã mô phỏng 15 postback MMP thời gian thực!');
      loadMmpStatsAndRecent();
    }
  } catch (e) {
    console.error("Error simulating MMP batch:", e);
  }
}

async function clearMmpLogs() {
  if (!confirm('Bạn có chắc muốn xóa sạch toàn bộ log MMP postbacks?')) return;
  try {
    const res = await fetch('/api/webhook/mmp/clear', { method: 'DELETE' });
    if (res.ok) {
      showToast('Đã dọn sạch log MMP.');
      loadMmpStatsAndRecent();
    }
  } catch (e) {
    console.error("Error clearing MMP logs:", e);
  }
}

function copyMmpWebhookUrl() {
  const el = document.getElementById('mmpWebhookUrl');
  if (el) {
    navigator.clipboard.writeText(el.textContent.trim());
    showToast('Đã sao chép Webhook Ingestion URL vào clipboard!');
  }
}

// --- 6. AI 1-PAGE GDD STUDIO ---
let currentGddData = null;
let gddPresets = [];

async function initGddTab() {
  try {
    if (!gddPresets || gddPresets.length === 0) {
      const res = await fetch('/api/gdd/presets');
      if (res.ok) {
        gddPresets = await res.json();
      }
    }
    if (!currentGddData) {
      generateGddDocument();
    }
  } catch (e) {
    console.error("Error initializing GDD Tab:", e);
  }
}

function loadGddPreset(idx) {
  if (!gddPresets || !gddPresets[idx]) return;
  const p = gddPresets[idx];
  document.getElementById('gddTitle').value = p.title;
  document.getElementById('gddGenre').value = p.genre;
  document.getElementById('gddPlatform').value = p.platform;
  document.getElementById('gddAudience').value = p.target_audience;
  document.getElementById('gddArtStyle').value = p.art_style;
  document.getElementById('gddMonetModel').value = p.monetization_model;

  generateGddDocument();
}

async function generateGddDocument() {
  const title = document.getElementById('gddTitle').value.trim() || 'Project Valkyrie';
  const genre = document.getElementById('gddGenre').value.trim() || 'Action Roguelike';
  const platform = document.getElementById('gddPlatform').value;
  const audience = document.getElementById('gddAudience').value.trim() || 'Mid-Core Gamers';
  const art = document.getElementById('gddArtStyle').value.trim() || 'Dark Fantasy';
  const monet = document.getElementById('gddMonetModel').value.trim() || 'Hybrid F2P';

  try {
    const res = await fetch('/api/gdd/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        genre: genre,
        platform: platform,
        target_audience: audience,
        art_style: art,
        monetization_model: monet
      })
    });

    if (res.ok) {
      const data = await res.json();
      currentGddData = data;
      renderGddView(data);
    }
  } catch (e) {
    console.error("Error generating GDD:", e);
  }
}

function renderGddView(data) {
  const container = document.getElementById('gddRenderContainer');
  if (!container) return;

  const meta = data.metadata;
  const pitch = data.elevator_pitch;
  const loops = data.core_gameplay_loops;
  const usps = data.key_usps;
  const monet = data.monetization_architecture;
  const kpis = data.kpi_benchmarks;

  container.innerHTML = `
    <!-- Header -->
    <div class="border-b border-slate-800 pb-4 space-y-2">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
          1-PAGE GAME DESIGN DOCUMENT • GREENLIGHT READY
        </span>
        <span class="text-xs text-slate-400 font-mono">${meta.platform}</span>
      </div>
      <h2 class="text-2xl font-black text-white tracking-tight">${meta.game_title.toUpperCase()}</h2>
      <div class="flex items-center gap-2 flex-wrap text-xs text-slate-300">
        <span class="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">${meta.genre}</span>
        <span class="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">${meta.art_style}</span>
        <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">${meta.monetization_model}</span>
      </div>
    </div>

    <!-- High Concept & Hook -->
    <div class="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-2 text-xs">
      <div class="font-bold text-amber-300 flex items-center gap-1.5 text-sm">
        <i data-lucide="zap" class="w-4 h-4"></i> High Concept & 30-Second Hook:
      </div>
      <p class="text-white font-medium leading-relaxed">${pitch.high_concept}</p>
      <p class="text-slate-300 leading-relaxed italic">"${pitch.hook_30s}"</p>
      <div class="text-[11px] text-amber-400/80 pt-1 border-t border-amber-500/20">
        <b>Định Vị Thị Trường:</b> ${pitch.market_positioning}
      </div>
    </div>

    <!-- 3-Layer Core Gameplay Loops -->
    <div class="space-y-3">
      <h4 class="text-sm font-bold text-white flex items-center gap-1.5">
        <i data-lucide="refresh-cw" class="w-4 h-4 text-cyan-400"></i>
        Hệ Thống Vòng Lặp Lối Chơi 3 Tầng (3-Layer Core Gameplay Loops)
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <!-- Minute Loop -->
        <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
          <span class="font-bold text-cyan-300 block text-xs">${loops.minute_loop.title}</span>
          <ul class="space-y-1 text-slate-300 text-[11px] list-none">
            ${loops.minute_loop.steps.map(s => `<li>${s}</li>`).join('')}
          </ul>
          <div class="text-[10px] text-cyan-400/80 pt-1 border-t border-slate-800">
            ⚡ <i>${loops.minute_loop.dopamine_trigger}</i>
          </div>
        </div>

        <!-- Session Loop -->
        <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
          <span class="font-bold text-emerald-300 block text-xs">${loops.session_loop.title}</span>
          <ul class="space-y-1 text-slate-300 text-[11px] list-none">
            ${loops.session_loop.steps.map(s => `<li>${s}</li>`).join('')}
          </ul>
          <div class="text-[10px] text-emerald-400/80 pt-1 border-t border-slate-800">
            💎 <i>${loops.session_loop.dopamine_trigger}</i>
          </div>
        </div>

        <!-- Meta Loop -->
        <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
          <span class="font-bold text-purple-300 block text-xs">${loops.meta_loop.title}</span>
          <ul class="space-y-1 text-slate-300 text-[11px] list-none">
            ${loops.meta_loop.steps.map(s => `<li>${s}</li>`).join('')}
          </ul>
          <div class="text-[10px] text-purple-400/80 pt-1 border-t border-slate-800">
            👑 <i>${loops.meta_loop.dopamine_trigger}</i>
          </div>
        </div>
      </div>
    </div>

    <!-- 3 USPs -->
    <div class="space-y-3">
      <h4 class="text-sm font-bold text-white flex items-center gap-1.5">
        <i data-lucide="award" class="w-4 h-4 text-pink-400"></i>
        3 Điểm Khác Biệt Độc Nhất (Key Unique Selling Points)
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        ${usps.map((u, i) => `
          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span class="font-bold text-pink-300 text-xs">USP #${i + 1}: ${u.usp}</span>
            <p class="text-slate-300 text-[11px] leading-relaxed">${u.description}</p>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Monetization Architecture -->
    <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3 text-xs">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2">
        <span class="font-bold text-emerald-400 flex items-center gap-1.5 text-xs">
          <i data-lucide="dollar-sign" class="w-4 h-4"></i> Kiến Trúc Kinh Tế & Monetization Hooks
        </span>
        <span class="text-[11px] text-slate-400">Conversion Baits & Recurring Passes</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px]">
        <div class="space-y-1.5">
          <span class="text-slate-400 font-semibold block uppercase text-[10px]">Gói Chuyển Đổi Nạp Đầu:</span>
          ${monet.conversion_baits.map(b => `<div class="text-slate-200">💰 <b>${b.name}:</b> ${b.hook}</div>`).join('')}
        </div>
        <div class="space-y-1.5">
          <span class="text-slate-400 font-semibold block uppercase text-[10px]">Doanh Thu Định Kỳ & Thuê Bao:</span>
          ${monet.recurring_subscriptions.map(r => `<div class="text-slate-200">⭐ <b>${r.name}:</b> ${r.hook}</div>`).join('')}
        </div>
      </div>
    </div>

    <!-- KPI Targets -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs pt-1">
      <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-slate-400 block font-medium">Mục Tiêu D1 Retention</span>
        <span class="text-lg font-black text-cyan-400 mt-0.5 block">${kpis.target_d1_retention}</span>
      </div>
      <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-slate-400 block font-medium">Mục Tiêu D7 Retention</span>
        <span class="text-lg font-black text-emerald-400 mt-0.5 block">${kpis.target_d7_retention}</span>
      </div>
      <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-slate-400 block font-medium">Mục Tiêu D30 Retention</span>
        <span class="text-lg font-black text-violet-400 mt-0.5 block">${kpis.target_d30_retention}</span>
      </div>
      <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-slate-400 block font-medium">Dự Kiến ARPDAU (Tier 1)</span>
        <span class="text-lg font-black text-amber-400 mt-0.5 block">${kpis.expected_arpdau}</span>
      </div>
    </div>
  `;

  lucide.createIcons();
}

function copyGddMarkdown() {
  if (!currentGddData || !currentGddData.markdown_export) return;
  navigator.clipboard.writeText(currentGddData.markdown_export);
  showToast('Đã sao chép tài liệu GDD (Markdown) vào clipboard!');
}

function downloadGddMarkdown() {
  if (!currentGddData || !currentGddData.markdown_export) return;
  const title = currentGddData.metadata.game_title.toLowerCase().replace(/[^a-z0-9]/g, '_');
  const blob = new Blob([currentGddData.markdown_export], { type: 'text/markdown;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${title}_gdd_1page.md`;
  link.click();
  showToast('Đã tải file tài liệu GDD (.md) thành công!');
}

// --- 7. STEAM WISHLIST & MOBILE PRE-REG FORECASTER ---
let preregMode = 'steam';
let preregPresets = [];

async function initPreRegTab() {
  try {
    if (!preregPresets || preregPresets.length === 0) {
      const res = await fetch('/api/prereg-wishlist/presets');
      if (res.ok) {
        preregPresets = await res.json();
      }
    }
    if (preregMode === 'steam') {
      runSteamForecast();
    } else {
      runMobileForecast();
    }
  } catch (e) {
    console.error("Error initializing Pre-reg Tab:", e);
  }
}

function setPreregMode(mode) {
  preregMode = mode;
  const btnSteam = document.getElementById('preregModeBtnSteam');
  const btnMobile = document.getElementById('preregModeBtnMobile');
  const steamGroup = document.getElementById('steamInputGroup');
  const mobileGroup = document.getElementById('mobileInputGroup');
  const heading = document.getElementById('preregFormHeading');

  if (mode === 'steam') {
    btnSteam.className = 'px-3 py-1.5 rounded-lg bg-cyan-600 text-white font-bold text-xs flex items-center gap-1.5';
    btnMobile.className = 'px-3 py-1.5 rounded-lg bg-transparent text-slate-400 hover:text-white font-semibold text-xs flex items-center gap-1.5';
    steamGroup.classList.remove('hidden');
    mobileGroup.classList.add('hidden');
    if (heading) heading.innerHTML = '<i data-lucide="monitor" class="w-4 h-4 text-cyan-400"></i> Thông Số Đợt Phát Hành Steam';
    runSteamForecast();
  } else {
    btnMobile.className = 'px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-bold text-xs flex items-center gap-1.5';
    btnSteam.className = 'px-3 py-1.5 rounded-lg bg-transparent text-slate-400 hover:text-white font-semibold text-xs flex items-center gap-1.5';
    mobileGroup.classList.remove('hidden');
    steamGroup.classList.add('hidden');
    if (heading) heading.innerHTML = '<i data-lucide="smartphone" class="w-4 h-4 text-emerald-400"></i> Thông Số Đợt Phát Hành Mobile';
    runMobileForecast();
  }
  lucide.createIcons();
}

function loadPreregPreset(idx) {
  if (!preregPresets || !preregPresets[idx]) return;
  const p = preregPresets[idx];
  if (p.platform === 'Steam') {
    setPreregMode('steam');
    document.getElementById('steamWishlists').value = p.current_wishlists;
    document.getElementById('steamDaysToLaunch').value = p.days_to_launch;
    document.getElementById('steamPrice').value = p.retail_price_usd;
    document.getElementById('steamDemoDownloads').value = p.next_fest_demo_downloads;
    document.getElementById('steamReviewScore').value = p.expected_review_score_pct;
    runSteamForecast();
  } else {
    setPreregMode('mobile');
    document.getElementById('mobilePrereg').value = p.current_prereg;
    document.getElementById('mobileDaysToLaunch').value = p.days_to_launch;
    document.getElementById('mobileD1Ret').value = p.projected_d1_retention;
    document.getElementById('mobileLtv').value = p.projected_d30_ltv_usd;
    runMobileForecast();
  }
}

async function runSteamForecast() {
  const wishlists = parseInt(document.getElementById('steamWishlists').value, 10) || 50000;
  const days = parseInt(document.getElementById('steamDaysToLaunch').value, 10) || 30;
  const price = parseFloat(document.getElementById('steamPrice').value) || 19.99;
  const demo = parseInt(document.getElementById('steamDemoDownloads').value, 10) || 10000;
  const score = parseFloat(document.getElementById('steamReviewScore').value) || 88.0;

  try {
    const res = await fetch('/api/prereg-wishlist/forecast-steam', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_wishlists: wishlists,
        days_to_launch: days,
        retail_price_usd: price,
        next_fest_demo_downloads: demo,
        expected_review_score_pct: score
      })
    });

    if (res.ok) {
      const data = await res.json();
      renderSteamForecastResult(data);
    }
  } catch (e) {
    console.error("Error forecasting Steam launch:", e);
  }
}

function renderSteamForecastResult(data) {
  const container = document.getElementById('preregResultsContainer');
  if (!container) return;

  const g = data.wishlist_growth;
  const s = data.sales_projections;

  container.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
      <div>
        <span class="text-xs text-slate-400">Phân Hạng Tiềm Năng Thương Mại Steam:</span>
        <h4 class="text-lg font-black text-white">${g.tier_classification}</h4>
      </div>
      <span class="px-3 py-1 rounded-full text-xs font-black bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-mono">
        PEAK CCU: ${s.day_1_peak_ccu.toLocaleString()} CCU
      </span>
    </div>

    <!-- Wishlist Accumulation Funnel -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
      <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-slate-400 block font-medium">Wishlist Hiện Tại</span>
        <span class="text-xl font-bold text-white mt-0.5 block font-mono">${g.base_wishlists.toLocaleString()}</span>
      </div>
      <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-cyan-400 block font-medium">Next Fest Demo Lift (+35%)</span>
        <span class="text-xl font-bold text-cyan-400 mt-0.5 block font-mono">+${g.next_fest_lift.toLocaleString()}</span>
      </div>
      <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-emerald-400 block font-medium">Tăng Tốc Trước Launch</span>
        <span class="text-xl font-bold text-emerald-400 mt-0.5 block font-mono">+${g.velocity_boost.toLocaleString()}</span>
      </div>
      <div class="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-500/30">
        <span class="text-[10px] text-cyan-300 font-bold block uppercase tracking-wider">Wishlists Tại Launch</span>
        <span class="text-2xl font-black text-cyan-300 mt-0.5 block font-mono">${g.total_launch_wishlists.toLocaleString()}</span>
      </div>
    </div>

    <!-- Financial Projections Box -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
        <span class="font-bold text-emerald-400 block text-xs uppercase tracking-wider">Doanh Thu Tuần Đầu Phát Hành (Week 1)</span>
        <div class="flex items-baseline justify-between">
          <span class="text-2xl font-black text-white font-mono">$${s.week_1_gross_usd.toLocaleString()}</span>
          <span class="text-xs text-slate-400 font-mono">${s.week_1_units.toLocaleString()} bản bán ra</span>
        </div>
        <div class="text-[11px] text-emerald-300 pt-1 border-t border-slate-800">
          💵 <b>Doanh Thu Ròng Studio (Sau 30% Steam cut):</b> <span class="font-mono font-bold">$${s.week_1_net_steam_usd.toLocaleString()}</span>
        </div>
      </div>

      <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
        <span class="font-bold text-amber-400 block text-xs uppercase tracking-wider">Dự Phóng Doanh Số Năm Đầu (Year 1)</span>
        <div class="flex items-baseline justify-between">
          <span class="text-2xl font-black text-white font-mono">$${s.year_1_gross_usd.toLocaleString()}</span>
          <span class="text-xs text-slate-400 font-mono">${s.year_1_units.toLocaleString()} bản tổng cộng</span>
        </div>
        <div class="text-[11px] text-amber-300 pt-1 border-t border-slate-800">
          💎 <b>Doanh Thu Ròng Dự Kiến Năm 1:</b> <span class="font-mono font-bold">$${s.year_1_net_steam_usd.toLocaleString()}</span>
        </div>
      </div>
    </div>

    <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-1">
      <div class="font-bold text-cyan-400 flex items-center gap-1.5">
        <i data-lucide="cpu" class="w-4 h-4"></i> Phản Ứng Thuật Toán Steam:
      </div>
      <p class="text-[11px]">${g.algorithm_recommendation}</p>
      <div class="text-[11px] text-slate-400 pt-1 border-t border-slate-800/80">
        💡 <b>Khuyến Nghị Chiến Lược:</b> ${data.strategic_advice}
      </div>
    </div>
  `;

  lucide.createIcons();
}

async function runMobileForecast() {
  const prereg = parseInt(document.getElementById('mobilePrereg').value, 10) || 250000;
  const days = parseInt(document.getElementById('mobileDaysToLaunch').value, 10) || 20;
  const ret = parseFloat(document.getElementById('mobileD1Ret').value) || 40.0;
  const ltv = parseFloat(document.getElementById('mobileLtv').value) || 2.50;

  try {
    const res = await fetch('/api/prereg-wishlist/forecast-mobile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_prereg: prereg,
        days_to_launch: days,
        projected_d1_retention: ret,
        projected_d30_ltv_usd: ltv
      })
    });

    if (res.ok) {
      const data = await res.json();
      renderMobileForecastResult(data);
    }
  } catch (e) {
    console.error("Error forecasting Mobile launch:", e);
  }
}

function renderMobileForecastResult(data) {
  const container = document.getElementById('preregResultsContainer');
  if (!container) return;

  const g = data.prereg_growth;
  const s = data.install_and_revenue;

  container.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
      <div>
        <span class="text-xs text-slate-400">Phân Hạng Tiềm Năng Mobile App Store:</span>
        <h4 class="text-lg font-black text-white">${g.tier_classification}</h4>
      </div>
      <span class="px-3 py-1 rounded-full text-xs font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono">
        D1 ACTIVE: ${s.day_1_active_users_d1.toLocaleString()} DAU
      </span>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
      <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-slate-400 block font-medium">Pre-Reg Hiện Tại</span>
        <span class="text-xl font-bold text-white mt-0.5 block font-mono">${g.base_prereg.toLocaleString()}</span>
      </div>
      <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
        <span class="text-[10px] text-emerald-400 block font-medium">Tăng Tốc Trước Launch</span>
        <span class="text-xl font-bold text-emerald-400 mt-0.5 block font-mono">+${g.velocity_boost.toLocaleString()}</span>
      </div>
      <div class="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30">
        <span class="text-[10px] text-emerald-300 font-bold block uppercase tracking-wider">Tổng Pre-Reg Launch</span>
        <span class="text-2xl font-black text-emerald-300 mt-0.5 block font-mono">${g.total_launch_prereg.toLocaleString()}</span>
      </div>
      <div class="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-500/30">
        <span class="text-[10px] text-cyan-300 font-bold block uppercase tracking-wider">Day 1 Auto-Installs (36%)</span>
        <span class="text-2xl font-black text-cyan-300 mt-0.5 block font-mono">${s.day_1_auto_installs.toLocaleString()}</span>
      </div>
    </div>

    <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
      <span class="font-bold text-emerald-400 block text-xs uppercase tracking-wider">Dự Phóng Doanh Thu Tháng Đầu (Month 1 Total)</span>
      <div class="flex items-baseline justify-between">
        <span class="text-2xl font-black text-white font-mono">$${s.month_1_gross_revenue_usd.toLocaleString()}</span>
        <span class="text-xs text-slate-400 font-mono">${s.month_1_total_installs.toLocaleString()} lượt cài đặt (kèm Chart Lift)</span>
      </div>
      <div class="text-[11px] text-emerald-300 pt-1 border-t border-slate-800">
        💵 <b>Doanh Thu Ròng Studio (Sau 30% Store Commission):</b> <span class="font-mono font-bold">$${s.month_1_net_revenue_usd.toLocaleString()}</span>
      </div>
    </div>

    <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300">
      💡 <b>Khuyến Nghị Chiến Lược UA:</b> ${data.strategic_advice}
    </div>
  `;

  lucide.createIcons();
}
