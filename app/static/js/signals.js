/* Market signals tab: data health, sustained breakouts, genre trends */
// ==========================================
// MARKET SIGNALS: data health, sustained breakouts, genre trends
// ==========================================
let genreTrendsChartInstance = null;

function escHtml(v) {
  return String(v ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
}

async function loadMarketSignals() {
  const platform = document.getElementById('signalsPlatform')?.value || 'all';
  const country = document.getElementById('signalsCountry')?.value || 'all';
  const windowDays = document.getElementById('signalsWindow')?.value || '7';
  const qs = `platform=${encodeURIComponent(platform)}&country=${encodeURIComponent(country)}`;
  try {
    const [health, breakouts, genres] = await Promise.all([
      fetch('/api/signals/data-health').then(r => r.json()),
      fetch(`/api/signals/sustained-breakouts?${qs}&window_days=${windowDays}`).then(r => r.json()),
      fetch(`/api/signals/genre-trends?${qs}`).then(r => r.json())
    ]);
    renderDataHealth(health);
    renderSustainedBreakouts(breakouts);
    renderGenreTrends(genres);
  } catch (e) {
    console.error('Error loading market signals:', e);
    showToast('Không tải được tín hiệu thị trường');
  }
  lucide.createIcons();
}

function renderDataHealth(h) {
  const badge = document.getElementById('dataHealthBadge');
  const map = {
    healthy: ['✅ Ổn định', 'bg-emerald-500/20 text-emerald-300'],
    degraded: ['⚠️ Một số nguồn lỗi / cũ', 'bg-amber-500/20 text-amber-300'],
    down: ['🚨 Tất cả nguồn lỗi', 'bg-rose-500/20 text-rose-300'],
    no_data: ['Chưa có lần crawl nào', 'bg-slate-800 text-slate-300']
  };
  const [label, cls] = map[h.overall_status] || map.no_data;
  if (badge) { badge.textContent = label; badge.className = `px-2 py-0.5 rounded text-[11px] font-bold ${cls}`; }

  const kpis = [
    ['Nguồn OK', h.sources_ok, 'text-emerald-400'],
    ['Nguồn cũ (>36h)', h.sources_stale, 'text-amber-400'],
    ['Nguồn đang lỗi', h.sources_failing, 'text-rose-400'],
    ['Ngày có dữ liệu / 30', h.days_with_data_30d, 'text-sky-400']
  ];
  document.getElementById('dataHealthKpis').innerHTML = kpis.map(([k, v, c]) => `
    <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
      <p class="text-[10px] text-slate-400 uppercase">${k}</p>
      <p class="text-xl font-black ${c}">${v ?? 0}</p>
    </div>`).join('');

  const cov = h.daily_coverage || [];
  const maxN = Math.max(1, ...cov.map(c => c.records));
  document.getElementById('dataHealthCoverage').innerHTML = cov.map(c => {
    const pct = c.records ? Math.max(15, Math.round(c.records / maxN * 100)) : 100;
    const color = c.records ? 'bg-emerald-500/70' : 'bg-slate-700/60';
    return `<div title="${c.date}: ${c.records} bản ghi" class="flex-1 rounded-sm ${color}" style="height:${pct}%"></div>`;
  }).join('');

  const statusCls = { ok: 'text-emerald-400', stale: 'text-amber-400', failing: 'text-rose-400' };
  const statusTxt = { ok: 'OK', stale: 'Cũ', failing: 'Lỗi' };
  document.getElementById('dataHealthTable').innerHTML = (h.sources || []).map(s => `
    <tr>
      <td class="py-1.5 px-2 text-slate-200">${escHtml(s.platform)}</td>
      <td class="px-2 text-slate-300">${escHtml(s.country)}</td>
      <td class="px-2 text-slate-300">${escHtml(s.ranking_type)}</td>
      <td class="px-2 font-bold ${statusCls[s.status] || ''}" title="${escHtml(s.last_error || '')}">${statusTxt[s.status] || s.status}</td>
      <td class="px-2 text-slate-400">${s.last_success ? `${escHtml(s.last_success)} (${s.hours_since_success}h trước)` : 'Chưa từng'}</td>
      <td class="px-2 text-right text-slate-300">${s.last_items_count ?? 0}</td>
      <td class="px-2 text-right ${s.failures_7d ? 'text-rose-400 font-bold' : 'text-slate-500'}">${s.failures_7d}</td>
    </tr>`).join('') || '<tr><td colspan="7" class="py-3 text-center text-slate-500">Chưa có nhật ký crawl</td></tr>';
}

function renderSustainedBreakouts(list) {
  const el = document.getElementById('sustainedBreakoutList');
  if (!list || !list.length) {
    el.innerHTML = '<p class="text-xs text-slate-500 py-4 text-center">Chưa có game nào tăng hạng bền vững trong cửa sổ này (cần ít nhất 3 ngày crawl).</p>';
    return;
  }
  el.innerHTML = list.map(g => {
    const spark = (g.rank_series || []).map(p => `#${p.rank}`).join(' → ');
    return `
    <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center gap-3">
      ${g.icon_url ? `<img src="${escHtml(g.icon_url)}" class="w-10 h-10 rounded-lg object-cover" onerror="this.style.display='none'">` : ''}
      <div class="flex-1 min-w-0">
        <p class="text-sm font-bold text-white truncate">${escHtml(g.title)}</p>
        <p class="text-[10px] text-slate-400 truncate">${escHtml(g.platform)} · ${escHtml(g.country)} · ${escHtml(g.ranking_type)} · ${escHtml(g.genre || '')}</p>
        <p class="text-[10px] text-slate-500 truncate" title="${escHtml(spark)}">${escHtml(spark)}</p>
      </div>
      <div class="text-right shrink-0">
        <p class="text-sm font-black text-emerald-400">+${g.net_gain} bậc</p>
        <p class="text-[10px] text-slate-400">${g.observations} lần crawl · ổn định ${g.consistency_pct}%</p>
        ${g.is_single_spike ? '<p class="text-[10px] text-amber-400">chủ yếu 1 cú nhảy</p>' : ''}
      </div>
    </div>`;
  }).join('');
}

function renderGenreTrends(data) {
  const meta = document.getElementById('genreTrendsMeta');
  const tw = data.this_week || {}, pw = data.prev_week || {};
  if (meta) {
    meta.textContent = `Tuần này ${tw.start} → ${tw.end} (${tw.snapshot_days || 0} ngày crawl) so với tuần trước ${pw.start} → ${pw.end} (${pw.snapshot_days || 0} ngày crawl). Tỷ trọng có trọng số theo thứ hạng (Top 50).`
      + (data.has_comparison ? '' : ' ⚠️ Chưa đủ dữ liệu 2 tuần để so sánh.');
  }
  const genres = data.genres || [];
  const canvas = document.getElementById('genreTrendsChart');
  if (canvas) {
    if (genreTrendsChartInstance) genreTrendsChartInstance.destroy();
    genreTrendsChartInstance = new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: genres.map(g => g.genre),
        datasets: [
          { label: 'Tuần trước (%)', data: genres.map(g => g.prev_share_pct), backgroundColor: 'rgba(100,116,139,0.5)', borderRadius: 3 },
          { label: 'Tuần này (%)', data: genres.map(g => g.share_pct), backgroundColor: genres.map(g => g.direction === 'up' ? 'rgba(16,185,129,0.8)' : (g.direction === 'down' ? 'rgba(244,63,94,0.8)' : 'rgba(99,102,241,0.8)')), borderRadius: 3 }
        ]
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        scales: { x: { ticks: { color: '#94a3b8', callback: v => v + '%' }, grid: { color: 'rgba(255,255,255,0.05)' } }, y: { ticks: { color: '#cbd5e1', font: { size: 10 } }, grid: { display: false } } },
        plugins: { legend: { labels: { color: '#cbd5e1', font: { size: 11 } } } }
      }
    });
  }
  const li = g => `<li><span class="font-semibold">${escHtml(g.genre)}</span> <span class="${g.delta_pp >= 0 ? 'text-emerald-400' : 'text-rose-400'}">${g.delta_pp >= 0 ? '+' : ''}${g.delta_pp} điểm %</span>${g.top_titles?.length ? `<br><span class="text-[10px] text-slate-500">${escHtml(g.top_titles.join(', '))}</span>` : ''}</li>`;
  document.getElementById('genreRisingList').innerHTML = (data.rising || []).map(li).join('') || '<li class="text-slate-500">—</li>';
  document.getElementById('genreFallingList').innerHTML = (data.falling || []).map(li).join('') || '<li class="text-slate-500">—</li>';
}
