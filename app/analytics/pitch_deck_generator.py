"""Executive Pitch Deck & Strategic Report Generator.

Compiles comprehensive studio strategy, ASO benchmarks, CPI-LTV forecast,
in-game economy, and publisher pitch into an interactive, printable executive slide deck.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

class PitchDeckGenerator:
    """Generates standalone printable HTML pitch decks for executives and publishers."""

    def __init__(self):
        pass

    def generate_deck_html(
        self,
        game_title: str = "Project Valkyrie",
        genre: str = "Mid-Core Action RPG",
        target_regions: str = "Global (Tier 1 US/JP & SEA)",
        target_cpi: float = 1.80,
        projected_d1: float = 42.0,
        projected_d7: float = 16.5,
        target_break_even_day: int = 45,
        whale_cap: str = "$1,500+",
        publisher_fit: str = "Habby / Miniclip (Tier 1 Mid-Core)"
    ) -> str:
        """Generates a complete standalone interactive slide deck in HTML/CSS."""
        generated_date = datetime.now().strftime("%B %d, %Y")

        html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{game_title} - Executive Studio Pitch Deck</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @media print {{
      .no-print {{ display: none !important; }}
      .slide {{ page-break-after: always; height: 100vh; }}
      body {{ background: #0f172a !important; -webkit-print-color-adjust: exact; }}
    }}
    .slide-gradient {{
      background: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15) 0%, rgba(15, 23, 42, 0.95) 75%);
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans antialiased min-h-screen">
  <!-- Top Presentation Toolbar (Hidden when printing) -->
  <div class="no-print fixed top-0 left-0 right-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 py-3 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
      <span class="text-xs font-bold text-white uppercase tracking-wider">{game_title} • Executive Pitch Deck</span>
    </div>
    <div class="flex items-center gap-3 text-xs">
      <button onclick="window.print()" class="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-all shadow-md">
        🖨️ In / Xuất PDF
      </button>
      <button onclick="window.close()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300">
        Đóng
      </button>
    </div>
  </div>

  <div class="pt-14 max-w-5xl mx-auto p-6 space-y-12">
    <!-- SLIDE 1: COVER & EXECUTIVE SUMMARY -->
    <div class="slide p-10 rounded-3xl border border-indigo-500/30 slide-gradient shadow-2xl space-y-8">
      <div class="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <span class="px-3 py-1 rounded-full text-xs font-black bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            EXECUTIVE CONFIDENTIAL BRIEF
          </span>
          <h1 class="text-4xl font-black text-white mt-3 tracking-tight">{game_title}</h1>
          <p class="text-sm text-slate-400 mt-1">Chiến Lược Sản Xuất, Tối Ưu Monetization & Kế Hoạch Phát Hành Toàn Cầu</p>
        </div>
        <div class="text-right text-xs text-slate-400">
          <div>Ngày lập: <strong class="text-slate-200">{generated_date}</strong></div>
          <div>Bản thảo: <strong class="text-emerald-400 font-mono">v1.0 Final</strong></div>
        </div>
      </div>

      <!-- 4 Core Executive Highlights -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <span class="text-[11px] text-slate-400">Thể Loại Mục Tiêu</span>
          <div class="text-base font-bold text-white mt-1">{genre}</div>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <span class="text-[11px] text-slate-400">Thị Trường Phát Hành</span>
          <div class="text-base font-bold text-sky-400 mt-1">{target_regions}</div>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <span class="text-[11px] text-slate-400">Target CPI Blended</span>
          <div class="text-base font-bold text-emerald-400 mt-1 font-mono">${target_cpi}</div>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <span class="text-[11px] text-slate-400">Dự Báo Hòa Vốn (Break-even)</span>
          <div class="text-base font-bold text-amber-400 mt-1 font-mono">Ngày thứ {target_break_even_day}</div>
        </div>
      </div>

      <div class="p-5 rounded-2xl bg-slate-900/60 border border-indigo-500/20 text-xs text-slate-300 leading-relaxed space-y-2">
        <h4 class="font-bold text-indigo-300 uppercase tracking-wider text-[11px]">Tóm Tắt Chiến Lược Điều Hành:</h4>
        <p>Dự án khai thác khoảng trống thị trường giữa game hành động đồ họa cao và cơ chế điều khiển tối giản một ngón tay (One-thumb control). Với chiến lược UA tối ưu kết hợp giữa Creative Video Ads dạng Hook và mạng lưới Micro-Creators TikTok, dự án hướng tới mục tiêu đạt điểm hòa vốn trong 45 ngày và duy trì LTV 180 ngày vượt trội nhờ hệ thống Battle Pass và Gacha cân bằng.</p>
      </div>
    </div>

    <!-- SLIDE 2: FINANCIAL FORECAST & CPI VS LTV SIMULATION -->
    <div class="slide p-10 rounded-3xl border border-slate-800 slide-gradient shadow-2xl space-y-6">
      <div class="border-b border-slate-800 pb-4">
        <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider">PHẦN 1: MÔ HÌNH DÒNG TIỀN & ĐỘ GIỮ CHÂN</span>
        <h2 class="text-2xl font-black text-white mt-1">Dự Báo Chỉ Số UA (CPI vs LTV) & Retention Trajectory</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div class="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <span class="text-xs text-slate-400">Hệ Số Giữ Chân Dự Kiến</span>
          <div class="flex items-center justify-between text-sm pt-1">
            <span>D1 Retention:</span>
            <strong class="text-emerald-400 font-mono">{projected_d1}%</strong>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span>D7 Retention:</span>
            <strong class="text-indigo-400 font-mono">{projected_d7}%</strong>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span>D30 Retention:</span>
            <strong class="text-purple-400 font-mono">7.2%</strong>
          </div>
        </div>

        <div class="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <span class="text-xs text-slate-400">Cột Mốc Hoàn Vốn (ROAS Milestones)</span>
          <div class="flex items-center justify-between text-sm pt-1">
            <span>ROAS D30:</span>
            <strong class="text-amber-400 font-mono">82%</strong>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span>ROAS D60:</span>
            <strong class="text-emerald-400 font-mono">118% (Lãi Ròng)</strong>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span>ROAS D180:</span>
            <strong class="text-emerald-400 font-mono">165%</strong>
          </div>
        </div>

        <div class="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <span class="text-xs text-slate-400">Cơ Cấu Người Nạp (Monetization Cap)</span>
          <div class="flex items-center justify-between text-sm pt-1">
            <span>Whale Cap Trần:</span>
            <strong class="text-purple-400 font-mono">{whale_cap}</strong>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span>Gói Mồi Đầu Tiên:</span>
            <strong class="text-amber-400 font-mono">$0.99</strong>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span>Chu Kỳ Battle Pass:</span>
            <strong class="text-sky-400 font-mono">28 Ngày ($9.99)</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- SLIDE 3: PUBLISHER FIT & GO-TO-MARKET READINESS -->
    <div class="slide p-10 rounded-3xl border border-slate-800 slide-gradient shadow-2xl space-y-6">
      <div class="border-b border-slate-800 pb-4">
        <span class="text-xs font-bold text-indigo-400 uppercase tracking-wider">PHẦN 2: CHIẾN LƯỢC GO-TO-MARKET & ĐỐI TÁC</span>
        <h2 class="text-2xl font-black text-white mt-1">Đánh Giá Tiềm Năng Hợp Tác Publisher Quốc Tế</h2>
      </div>

      <div class="p-5 rounded-2xl bg-slate-900 border border-indigo-500/30 flex items-center justify-between">
        <div>
          <span class="text-xs text-slate-400">Nhóm Đối Tác Khuyến Nghị Phù Hợp Nhất</span>
          <div class="text-lg font-black text-white mt-1">{publisher_fit}</div>
        </div>
        <span class="px-3 py-1.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          ĐỦ ĐIỀU KIỆN KÝ HỢP ĐỒNG (92/100)
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs text-slate-300">
        <div class="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <h4 class="font-bold text-white uppercase text-[11px]">Điều Khoản Thương Thảo Dự Kiến:</h4>
          <p>• <strong>RevShare:</strong> Đề xuất 40% Studio / 60% Publisher sau khi hoàn vốn UA.</p>
          <p>• <strong>Minimum Guarantee (MG):</strong> Yêu cầu tạm ứng tối thiểu $50,000 để bảo vệ dòng tiền studio.</p>
          <p>• <strong>UA Scaling:</strong> Publisher cam kết đẩy ngân sách tối thiểu $200,000/tháng nếu KPI D7 đạt chuẩn.</p>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <h4 class="font-bold text-white uppercase text-[11px]">Cam Kết Chất Lượng Kỹ Thuật (QA/C10n):</h4>
          <p>• Sẵn sàng bản build độc lập tuân thủ quy chuẩn kiểm duyệt Trung Quốc và Trung Đông.</p>
          <p>• Tích hợp sẵn hệ thống Analytics (Adjust/AppsFlyer) và phân tầng Ad Mediation thông minh.</p>
          <p>• Vòng lặp LiveOps 28 ngày chuẩn bị sẵn nội dung cập nhật cho 6 tháng đầu tiên.</p>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""
        return html_template
