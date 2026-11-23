/* Alert settings and bot configuration */
// --- SETTINGS & BOT ---
async function loadAlertSettings() {
  try {
    const res = await fetch('/api/alerts/config');
    const data = await res.json();
    document.getElementById('alertDiscordUrl').value = data.discord_webhook_url || '';
    document.getElementById('alertTgToken').value = data.telegram_bot_token || '';
    document.getElementById('alertTgChatId').value = data.telegram_chat_id || '';
    document.getElementById('alertEnableDigest').checked = data.enable_daily_digest !== false;
    document.getElementById('alertEnableBreakout').checked = data.enable_breakout_alerts !== false;
    document.getElementById('alertThreshold').value = data.breakout_threshold || 15;

    const aiRes = await fetch('/api/ai/config');
    const aiData = await aiRes.json();
    const badge = document.getElementById('geminiKeyBadge');
    if (aiData.has_gemini_key) {
      badge.innerText = '🟢 Đã kết nối Gemini';
      badge.className = 'text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold';
      document.getElementById('geminiApiKeyInput').placeholder = 'Đã lưu: ' + aiData.masked_key;
    } else {
      badge.innerText = 'Tự động Heuristic';
      badge.className = 'text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-medium';
    }
  } catch (err) {
    console.error("Error loading alert settings:", err);
  }
}

async function saveAlertSettings() {
  const payload = {
    discord_webhook_url: document.getElementById('alertDiscordUrl').value.trim(),
    telegram_bot_token: document.getElementById('alertTgToken').value.trim(),
    telegram_chat_id: document.getElementById('alertTgChatId').value.trim(),
    enable_daily_digest: document.getElementById('alertEnableDigest').checked,
    enable_breakout_alerts: document.getElementById('alertEnableBreakout').checked,
    breakout_threshold: parseInt(document.getElementById('alertThreshold').value) || 15
  };

  try {
    const res = await fetch('/api/alerts/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    showToast('Đã lưu cấu hình Bot & Cảnh báo thành công!');
  } catch (err) {
    showToast('Lỗi khi lưu cấu hình.');
  }
}

async function saveGeminiKey() {
  const key = document.getElementById('geminiApiKeyInput').value.trim();
  if (!key) {
    showToast('Vui lòng nhập API Key.');
    return;
  }

  try {
    const res = await fetch('/api/ai/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gemini_api_key: key })
    });
    showToast('Đã lưu Gemini API Key thành công!');
    loadAlertSettings();
  } catch (err) {
    showToast('Lỗi khi lưu API Key.');
  }
}

async function testAlertNotification() {
  await saveAlertSettings();
  showToast('Đang gửi tin nhắn thử nghiệm...', 'refresh-cw');
  try {
    const res = await fetch('/api/alerts/test', { method: 'POST' });
    const result = await res.json();
    const msg = `Discord: ${result.discord || 'N/A'} | Telegram: ${result.telegram || 'N/A'}`;
    showToast(msg);
  } catch (err) {
    showToast('Lỗi gửi thử nghiệm.');
  }
}

async function sendManualMorningDigest() {
  const date = document.getElementById('targetDate').value;
  showToast('Đang gửi bản tin tổng kết...', 'refresh-cw');
  try {
    const res = await fetch(`/api/alerts/digest?target_date=${date}`, { method: 'POST' });
    showToast('Đã phát bản tin thành công!');
  } catch (err) {
    showToast('Lỗi khi phát bản tin.');
  }
}
