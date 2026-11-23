/* Shared globals, helpers (debounce, toast) and 2-tier navigation */
let genreChartInstance = null;
let modalChartInstance = null;
let compareChartInstance = null;
let currentRawReport = "";
let currentActiveModalGameId = null;
let isCurrentModalInWatchlist = false;

// Escape text before inserting into innerHTML (store reviews, titles... are untrusted)
function escHtml(v) {
  return String(v ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
}

// Debounce helper
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Toast helper
function showToast(msg, icon = 'check-circle') {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toastMsg');
  toastMsg.innerText = msg;
  toast.classList.remove('translate-y-20', 'opacity-0');
  lucide.createIcons();
  setTimeout(() => {
    toast.classList.add('translate-y-20', 'opacity-0');
  }, 3500);
}


// ==========================================
// 2-TIER STREAMLINED NAVIGATION SYSTEM
// ==========================================
const CATEGORIES = {
  market: {
    key: 'market',
    name: '📊 Thị Trường & Game Top',
    activeClass: 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-lg shadow-indigo-900/40',
    tabs: [
      { id: 'overview', name: 'Tổng Quan Thị Trường', icon: 'layout-grid' },
      { id: 'signals', name: 'Tín Hiệu Thị Trường', icon: 'radar', badge: 'MỚI' },
      { id: 'pc', name: 'PC Steam Rankings', icon: 'monitor' },
      { id: 'mobile', name: 'Mobile App Store', icon: 'smartphone' },
      { id: 'radar', name: 'Radar Sắp Ra Mắt', icon: 'compass' },
      { id: 'breakouts', name: 'Bứt Phá (Breakouts)', icon: 'flame' },
      { id: 'watchlist', name: 'Theo Dõi (Watchlist)', icon: 'bookmark' },
      { id: 'compare', name: 'So Sánh 2 Game', icon: 'arrow-left-right' },
      { id: 'hybridlab', name: '🧬 Lai Ghép Cơ Chế', icon: 'dna', badge: 'AI LAB' },
      { id: 'blueocean', name: 'Thị Trường Ngách (Blue Ocean)', icon: 'anchor' }
    ]
  },
  growth: {
    key: 'growth',
    name: '🚀 Creative & UA Studio',
    activeClass: 'bg-gradient-to-r from-purple-600 to-violet-600 text-white shadow-lg shadow-purple-900/40',
    tabs: [
      { id: 'creatives', name: 'Creative Spy & Trend', icon: 'video' },
      { id: 'playable', name: 'Playable Ad Studio', icon: 'play' },
      { id: 'voiceover', name: 'AI Voiceover & Script', icon: 'mic' },
      { id: 'mediation', name: 'Ad Mediation & LTV', icon: 'layers', badge: 'ROAS' },
      { id: 'uapacing', name: 'UA Budget & ROAS Pacing', icon: 'line-chart' },
      { id: 'fraud', name: 'Ad Fraud Scanner', icon: 'shield-alert' },
      { id: 'mmpstream', name: 'MMP Stream Simulation', icon: 'activity' }
    ]
  },
  economy: {
    key: 'economy',
    name: '💰 Kinh Tế & LiveOps',
    activeClass: 'bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-lg shadow-amber-900/40',
    tabs: [
      { id: 'iapmatrix', name: 'IAP & Economy Matrix', icon: 'shopping-cart' },
      { id: 'gachaecon', name: 'Gacha Pity & Drop Rate', icon: 'sparkles' },
      { id: 'liveopsradar', name: 'LiveOps & Battle Pass', icon: 'calendar' },
      { id: 'chokepoint', name: 'Choke Point & Drop-off', icon: 'alert-triangle' },
      { id: 'viralkfactor', name: 'K-Factor & Viral Loop', icon: 'share-2' },
      { id: 'asolab', name: 'ASO Visual Lab', icon: 'eye' }
    ]
  },
  producer: {
    key: 'producer',
    name: '📋 Producer & Chiến Lược',
    activeClass: 'bg-gradient-to-r from-cyan-600 to-teal-600 text-white shadow-lg shadow-cyan-900/40',
    tabs: [
      { id: 'gdd', name: 'AI GDD Generator', icon: 'file-text' },
      { id: 'rice', name: 'RICE Feature Matrix', icon: 'check-square' },
      { id: 'simulator', name: 'Simulator Doanh Thu', icon: 'calculator' },
      { id: 'pubpitch', name: 'Publisher Pitch Kit', icon: 'briefcase' },
      { id: 'abtesting', name: 'A/B Test Calculator', icon: 'percent' },
      { id: 'prereg', name: 'Pre-Registration Tracker', icon: 'bell' },
      { id: 'steamapi', name: 'Steam API Direct Sync', icon: 'refresh-cw' },
      { id: 'pitchdeck', name: 'Pitch Deck Generator', icon: 'presentation' },
      { id: 'c10nscan', name: 'Localization & Cultural Scan', icon: 'globe' }
    ]
  },
  settings: {
    key: 'settings',
    name: '⚙️ Cài Đặt & Logs',
    activeClass: 'bg-gradient-to-r from-pink-600 to-rose-600 text-white shadow-lg shadow-pink-900/40',
    tabs: [
      { id: 'report', name: 'Báo Cáo Toàn Diện', icon: 'file-bar-chart' },
      { id: 'alerts', name: 'Cấu Hình Cảnh Báo', icon: 'bell-ring' },
      { id: 'calibration', name: 'Hiệu Chỉnh Mô Hình', icon: 'sliders-horizontal', badge: 'MỚI' },
      { id: 'botcenter', name: 'Bot Center & Telegram/Discord', icon: 'bot' },
      { id: 'logs', name: 'Nhật Ký Hệ Thống', icon: 'terminal' }
    ]
  }
};

let currentCategoryKey = 'market';
let currentTabId = 'overview';

function renderSubnav(catKey, activeTabId) {
  const container = document.getElementById('subnavContainer');
  if (!container) return;
  const cat = CATEGORIES[catKey] || CATEGORIES.market;
  container.innerHTML = cat.tabs.map(tab => {
    const isActive = tab.id === activeTabId;
    const activeClass = isActive 
      ? 'bg-slate-800 text-white border border-slate-700 shadow-md font-bold'
      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent font-medium';
    const iconColor = isActive ? 'text-indigo-400' : 'text-slate-400';
    const badge = tab.badge ? `<span class="ml-1 px-1.5 py-0.5 rounded text-[9px] font-black bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider">${tab.badge}</span>` : '';
    return `
      <button onclick="switchTab('${tab.id}')" id="tabBtn-${tab.id}" class="tab-btn flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap text-xs ${activeClass}">
        <i data-lucide="${tab.icon}" class="w-3.5 h-3.5 ${iconColor}"></i>
        <span>${tab.name}</span>
        ${badge}
      </button>
    `;
  }).join('');
  lucide.createIcons();
}

function switchCategory(catKey, targetTabId = null) {
  if (!CATEGORIES[catKey]) catKey = 'market';
  currentCategoryKey = catKey;

  // Update Tier 1 Category buttons styling
  Object.keys(CATEGORIES).forEach(k => {
    const btn = document.getElementById(`catBtn-${k}`);
    if (!btn) return;
    if (k === catKey) {
      btn.className = `cat-btn flex items-center gap-2 px-4 py-2.5 rounded-xl ${CATEGORIES[k].activeClass} transition-all cursor-pointer font-bold`;
    } else {
      btn.className = `cat-btn flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all cursor-pointer font-medium`;
    }
  });

  // Target tab
  const cat = CATEGORIES[catKey];
  const tabToOpen = targetTabId || cat.tabs[0].id;
  renderSubnav(catKey, tabToOpen);
  switchTab(tabToOpen, false);
}

// Tabs whose numbers are NOT live market data. A banner is shown at the top of each so
// hard-coded benchmarks / templates are never mistaken for measured data.
const DATA_NOTES = {
  creatives:    ['static', 'Danh sách mẫu quảng cáo viết sẵn. Các chỉ số CTR / CVR / CPI chỉ là ước lượng minh họa, không đo từ chiến dịch thật.'],
  blueocean:    ['static', 'Danh sách thị trường ngách viết sẵn. Điểm cạnh tranh, tiềm năng doanh thu và các tỷ lệ tăng trưởng là nhận định biên soạn sẵn, không tính từ dữ liệu crawl.'],
  liveopsradar: ['static', 'Lịch cập nhật đối thủ và mẫu sự kiện là dữ liệu viết sẵn; hệ số tăng doanh thu là giả định.'],
  asolab:       ['static', 'Các kiểu ảnh store và điểm "clickability" là benchmark viết sẵn, không đo từ A/B test thật.'],
  c10nscan:     ['static', 'Quy định & lưu ý văn hóa là ghi chú biên soạn sẵn, có thể đã cũ. Luôn kiểm tra lại với văn bản pháp lý / guideline hiện hành.'],
  simulator:    ['model', 'Mô phỏng: CPI, retention và LTV dùng benchmark giả định. Thay bằng số liệu thật của bạn để có kết quả tin cậy.'],
  iapmatrix:    ['model', 'Mô phỏng: bảng giá theo thể loại, hệ số PPP và tỷ lệ Whale/Dolphin là benchmark giả định.'],
  uapacing:     ['model', 'Mô phỏng: phân bổ ngân sách theo giờ dựa trên benchmark giả định, không lấy từ tài khoản quảng cáo của bạn.'],
  gachaecon:    ['model', 'Mô phỏng Monte Carlo theo tham số bạn nhập: kết quả chính xác về mặt xác suất cho đúng các tham số đó.'],
  chokepoint:   ['model', 'Mô phỏng: phễu rời bỏ và ngưỡng chuẩn là benchmark giả định, không lấy từ analytics của game.'],
  viralkfactor: ['model', 'Mô phỏng: công thức K-Factor chuẩn, nhưng các tỷ lệ mặc định là giả định.'],
  mediation:    ['model', 'Mô phỏng: eCPM theo khu vực và waterfall là benchmark giả định, không lấy từ ad network thật.'],
  pubpitch:     ['model', 'Mô phỏng: benchmark nhà phát hành và điều khoản hợp đồng là giả định tham khảo.'],
  prereg:       ['model', 'Mô phỏng: tỷ lệ chuyển đổi wishlist / pre-reg là hệ số giả định.'],
  fraud:        ['model', 'Kiểm tra theo luật CTIT chuẩn trên dữ liệu mẫu hoặc dữ liệu bạn nhập; mạng quảng cáo mẫu là giả lập.'],
  hybridlab:    ['generated', 'Nội dung sinh tự động (Gemini nếu có key, nếu không là template nội bộ). Đây là ý tưởng thiết kế, không phải dữ liệu thị trường.'],
  gdd:          ['generated', 'Tài liệu sinh tự động từ template, dùng làm khung bắt đầu.'],
  pitchdeck:    ['generated', 'Slide sinh tự động; các con số trong slide lấy từ mô phỏng / ước tính, cần thay bằng số liệu thật trước khi trình bày.'],
  voiceover:    ['generated', 'Kịch bản sinh tự động từ template.'],
  playable:     ['generated', 'Playable ad sinh từ template mẫu.'],
};

function renderDataNote(tabId) {
  const note = DATA_NOTES[tabId];
  const content = document.getElementById(`tabContent-${tabId}`);
  if (!note || !content || document.getElementById(`dataNote-${tabId}`)) return;
  const [kind, text] = note;
  const style = {
    static: ['📚 THAM KHẢO TĨNH — KHÔNG PHẢI DỮ LIỆU LIVE', 'border-amber-500/40 bg-amber-500/10 text-amber-200'],
    model: ['🧮 MÔ PHỎNG — SỐ LIỆU GIẢ ĐỊNH', 'border-sky-500/40 bg-sky-500/10 text-sky-200'],
    generated: ['✨ NỘI DUNG SINH TỰ ĐỘNG', 'border-purple-500/40 bg-purple-500/10 text-purple-200'],
  }[kind];
  const div = document.createElement('div');
  div.id = `dataNote-${tabId}`;
  div.className = `px-3 py-2 rounded-xl border text-[11px] leading-relaxed ${style[1]}`;
  div.innerHTML = `<b>${style[0]}</b> · ${escHtml(text)}`;
  content.prepend(div);
}

function switchTab(tabId, syncCategory = true) {
  currentTabId = tabId;

  // Find which category owns this tab
  if (syncCategory) {
    let foundCat = 'market';
    for (const [k, v] of Object.entries(CATEGORIES)) {
      if (v.tabs.some(t => t.id === tabId)) {
        foundCat = k;
        break;
      }
    }
    if (foundCat !== currentCategoryKey) {
      currentCategoryKey = foundCat;
      // Sync Tier 1 buttons
      Object.keys(CATEGORIES).forEach(k => {
        const btn = document.getElementById(`catBtn-${k}`);
        if (!btn) return;
        if (k === currentCategoryKey) {
          btn.className = `cat-btn flex items-center gap-2 px-4 py-2.5 rounded-xl ${CATEGORIES[k].activeClass} transition-all cursor-pointer font-bold`;
        } else {
          btn.className = `cat-btn flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all cursor-pointer font-medium`;
        }
      });
      renderSubnav(currentCategoryKey, tabId);
    } else {
      // Just update subnav active button styling
      const cat = CATEGORIES[currentCategoryKey];
      if (cat && cat.tabs) {
        cat.tabs.forEach(t => {
          const btn = document.getElementById(`tabBtn-${t.id}`);
          if (!btn) return;
          if (t.id === tabId) {
            btn.className = "tab-btn flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap text-xs bg-slate-800 text-white border border-slate-700 shadow-md font-bold";
          } else {
            btn.className = "tab-btn flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all cursor-pointer whitespace-nowrap text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent font-medium";
          }
        });
      }
    }
  }

  // Hide all tab contents, show only target tab (list derived from CATEGORIES)
  const allTabs = Object.values(CATEGORIES).flatMap(c => c.tabs.map(t => t.id));

  allTabs.forEach(t => {
    const content = document.getElementById(`tabContent-${t}`);
    if (!content) return;
    if (t === tabId) {
      content.classList.remove('hidden');
      renderDataNote(t);
    } else {
      content.classList.add('hidden');
    }
  });

  // Trigger data loaders
  if (tabId === 'overview') loadOverview();
  if (tabId === 'pc') loadPCRankings();
  if (tabId === 'mobile') loadMobileRankings();
  if (tabId === 'radar') loadRadarUpcoming();
  if (tabId === 'creatives') loadCreativeSpy();
  if (tabId === 'simulator') initSimulatorTab();
  if (tabId === 'blueocean') loadBlueOceanRadar();
  if (tabId === 'asolab') loadAsoVisualLab();
  if (tabId === 'iapmatrix') initIapMatrixTab();
  if (tabId === 'liveopsradar') initLiveOpsRadarTab();
  if (tabId === 'uapacing') initUaPacingTab();
  if (tabId === 'gachaecon') initGachaEconTab();
  if (tabId === 'pubpitch') initPublisherPitchTab();
  if (tabId === 'c10nscan') initC10nTab();
  if (tabId === 'chokepoint') initChokePointTab();
  if (tabId === 'viralkfactor') initViralKFactorTab();
  if (tabId === 'botcenter') initBotCenterTab();
  if (tabId === 'pitchdeck') initPitchDeckTab();
  if (tabId === 'abtesting') initAbTestingTab();
  if (tabId === 'mediation') initMediationTab();
  if (tabId === 'playable') initPlayableTab();
  if (tabId === 'voiceover') initVoiceoverTab();
  if (tabId === 'rice') initRiceTab();
  if (tabId === 'fraud') initFraudTab();
  if (tabId === 'mmpstream') initMmpStreamTab();
  if (tabId === 'gdd') initGddTab();
  if (tabId === 'prereg') initPreRegTab();
  if (tabId === 'steamapi') initSteamApiTab();
  if (tabId === 'breakouts') loadBreakoutRadar();
  if (tabId === 'signals') loadMarketSignals();
  if (tabId === 'calibration') loadCalibration();
  if (tabId === 'watchlist') loadWatchlist();
  if (tabId === 'compare') executeComparison();
  if (tabId === 'hybridlab') initHybridLabTab();
  if (tabId === 'alerts') loadAlertSettings();
  if (tabId === 'report') loadMarketReport();
  if (tabId === 'logs') loadCrawlLogs();
}
