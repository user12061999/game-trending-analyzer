/* Revenue model calibration tab */

function fmtUsd(v) {
  if (v == null) return '--';
  if (v >= 1e6) return '$' + (v / 1e6).toFixed(2) + 'M';
  if (v >= 1e3) return '$' + (v / 1e3).toFixed(1) + 'K';
  return '$' + Math.round(v);
}

function errBadge(pct) {
  if (pct == null) return '';
  const abs = Math.abs(pct);
  const cls = abs <= 25 ? 'text-emerald-400' : (abs <= 60 ? 'text-amber-400' : 'text-rose-400');
  return `<span class="${cls}">(${pct > 0 ? '+' : ''}${pct}%)</span>`;
}

function toggleCalibPcFields() {
  const isPc = document.getElementById('calibPlatform')?.value === 'pc';
  document.getElementById('calibPcFields')?.classList.toggle('hidden', !isPc);
}

async function loadCalibration() {
  try {
    const data = await fetch('/api/calibration').then(r => r.json());
    renderCalibration(data);
  } catch (e) {
    console.error('Error loading calibration:', e);
  }
}

function renderCalibration(data) {
  if (data.bounds) document.getElementById('calibBounds').textContent = `${data.bounds[0]}–${data.bounds[1]}`;
  const chips = (data.factors || []).map(f =>
    `<span class="px-2 py-1 rounded-lg bg-slate-900 border border-slate-700"><b>${escHtml(f.platform)}:${escHtml(f.country)}</b> ×${f.factor} <span class="text-slate-500">(${f.points} điểm)</span></span>`);
  for (const [p, v] of Object.entries(data.platform_factors || {})) {
    chips.push(`<span class="px-2 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-200"><b>${escHtml(p)}: các QG khác</b> ×${v}</span>`);
  }
  document.getElementById('calibFactors').innerHTML = chips.join('') ||
    '<span class="text-slate-500">Chưa có điểm dữ liệu — mô hình đang dùng hệ số mặc định ×1.0.</span>';

  document.getElementById('calibTable').innerHTML = (data.points || []).map(p => `
    <tr>
      <td class="py-1.5 px-2 text-slate-200">${escHtml(p.game_title)}<div class="text-[10px] text-slate-500">${escHtml(p.source || '')}</div></td>
      <td class="px-2 text-slate-300">${escHtml(p.platform)} / ${escHtml(p.country)} · ${escHtml(p.ranking_type || '')}</td>
      <td class="px-2 text-right text-slate-300">#${p.rank}</td>
      <td class="px-2 text-right font-bold text-white">${fmtUsd(p.actual_monthly_revenue)}</td>
      <td class="px-2 text-right text-slate-300">${fmtUsd(p.model_monthly_raw)} ${errBadge(p.raw_error_pct)}</td>
      <td class="px-2 text-right text-slate-300">${fmtUsd(p.model_monthly_calibrated)} ${errBadge(p.calibrated_error_pct)}</td>
      <td class="px-2 text-right"><button onclick="deleteCalibrationPoint(${p.id})" class="text-rose-400 hover:text-rose-300" title="Xóa">✕</button></td>
    </tr>`).join('') || '<tr><td colspan="7" class="py-3 text-center text-slate-500">Chưa có dữ liệu</td></tr>';
}

async function submitCalibrationPoint(ev) {
  ev.preventDefault();
  const form = ev.target;
  const payload = Object.fromEntries(new FormData(form).entries());
  const res = await fetch('/api/calibration', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    showToast(data.message || 'Dữ liệu không hợp lệ', 'alert-triangle');
    return;
  }
  form.reset();
  toggleCalibPcFields();
  renderCalibration(data.report);
  showToast('Đã lưu và cập nhật hệ số hiệu chỉnh');
}

async function deleteCalibrationPoint(id) {
  if (!confirm('Xóa điểm dữ liệu này?')) return;
  const data = await fetch(`/api/calibration/${id}`, { method: 'DELETE' }).then(r => r.json());
  renderCalibration(data.report);
}
