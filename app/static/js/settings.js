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
    document.getElementById('alertCooldownDays').value = data.breakout_cooldown_days || 3;
    document.getElementById('alertEnableSustained').checked = data.enable_sustained_alerts !== false;
    document.getElementById('alertSustainedGain').value = data.sustained_min_gain || 10;
    document.getElementById('alertSustainedWindow').value = data.sustained_window_days || 7;
    document.getElementById('alertEnableHealth').checked = data.enable_health_alerts !== false;
    document.getElementById('alertEnableWeekly').checked = data.enable_weekly_digest !== false;
    document.getElementById('alertWeeklyDay').value = String(data.weekly_digest_weekday ?? 0);
    loadAlertHistory();

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
    breakout_threshold: parseInt(document.getElementById('alertThreshold').value) || 15,
    breakout_cooldown_days: parseInt(document.getElementById('alertCooldownDays').value) || 3,
    enable_sustained_alerts: document.getElementById('alertEnableSustained').checked,
    sustained_min_gain: parseInt(document.getElementById('alertSustainedGain').value) || 10,
    sustained_window_days: parseInt(document.getElementById('alertSustainedWindow').value) || 7,
    enable_health_alerts: document.getElementById('alertEnableHealth').checked,
    enable_weekly_digest: document.getElementById('alertEnableWeekly').checked,
    weekly_digest_weekday: parseInt(document.getElementById('alertWeeklyDay').value) || 0
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

const ALERT_TYPE_LABELS = {
  daily_digest: '📊 Bản tin ngày', weekly_digest: '🗓️ Bản tin tuần', breakout: '🚀 Breakout',
  sustained: '📈 Bứt phá bền vững', health: '⚠️ Crawl lỗi'
};

async function loadAlertHistory() {
  const el = document.getElementById('alertHistoryList');
  if (!el) return;
  try {
    const items = await fetch('/api/alerts/history?limit=30').then(r => r.json());
    el.innerHTML = items.map(a => `
      <li class="flex gap-2 text-slate-300">
        <span class="text-slate-500 shrink-0">${escHtml(a.sent_at)}</span>
        <span class="shrink-0 font-semibold">${ALERT_TYPE_LABELS[a.alert_type] || escHtml(a.alert_type)}</span>
        <span class="truncate" title="${escHtml(a.summary || '')}">${escHtml(a.summary || '')}</span>
      </li>`).join('') || '<li class="text-slate-500">Chưa gửi cảnh báo nào.</li>';
  } catch (e) {
    console.error('Error loading alert history:', e);
  }
}

async function runAlertChecksNow() {
  await saveAlertSettings();
  const res = await fetch('/api/alerts/run-checks', { method: 'POST' }).then(r => r.json());
  showToast(res.skipped ? 'Chưa cấu hình Discord/Telegram' : 'Đã kiểm tra xong (cảnh báo đã gửi trước đó sẽ không gửi lại)');
  loadAlertHistory();
}

async function sendWeeklyDigestNow() {
  await saveAlertSettings();
  const res = await fetch('/api/alerts/weekly', { method: 'POST' }).then(r => r.json());
  showToast(res.sent ? 'Đã gửi bản tin tuần' : `Chưa gửi: ${res.reason || res.skipped || 'không có kênh nào nhận'}`);
  loadAlertHistory();
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
