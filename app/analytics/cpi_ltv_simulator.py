"""CPI vs LTV Forecaster & UA Profitability Simulator for Mobile Games.

Simulates User Acquisition (UA) campaign economics, calculates real-world Cost Per Install (CPI),
projects retention curves, cumulative Lifetime Value (LTV), and forecasts Break-Even Days and ROAS.
"""

import math
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Real-world CPI Benchmarks by Country and Genre (USD)
CPI_BENCHMARKS = {
    "vn": {"rpg": 0.95, "strategy": 1.25, "action": 0.80, "casual": 0.35, "simulation": 0.60, "default": 0.75},
    "us": {"rpg": 5.60, "strategy": 6.90, "action": 4.40, "casual": 1.95, "simulation": 2.90, "default": 4.50},
    "jp": {"rpg": 6.80, "strategy": 7.90, "action": 5.20, "casual": 2.30, "simulation": 3.60, "default": 5.20},
    "kr": {"rpg": 4.90, "strategy": 5.95, "action": 3.90, "casual": 1.60, "simulation": 2.50, "default": 3.80},
    "global": {"rpg": 2.10, "strategy": 2.60, "action": 1.65, "casual": 0.75, "simulation": 1.15, "default": 1.65}
}

# Standard Retention Curve Benchmarks (D1, D7, D14, D30, D60, D90, D180)
RETENTION_BENCHMARKS = {
    "rpg": [0.42, 0.18, 0.12, 0.075, 0.042, 0.026, 0.015],
    "strategy": [0.38, 0.20, 0.14, 0.092, 0.058, 0.042, 0.028],
    "action": [0.40, 0.17, 0.11, 0.065, 0.038, 0.022, 0.012],
    "casual": [0.35, 0.14, 0.08, 0.045, 0.022, 0.012, 0.005],
    "simulation": [0.37, 0.16, 0.10, 0.060, 0.032, 0.018, 0.009],
    "default": [0.38, 0.16, 0.10, 0.065, 0.035, 0.020, 0.010]
}

# Daily Active User ARPU Benchmarks by Country and Genre (USD per DAU per day)
DAU_ARPU_BENCHMARKS = {
    "vn": {"rpg": 0.12, "strategy": 0.16, "action": 0.09, "casual": 0.035, "simulation": 0.06, "default": 0.08},
    "us": {"rpg": 0.58, "strategy": 0.72, "action": 0.45, "casual": 0.18, "simulation": 0.32, "default": 0.42},
    "jp": {"rpg": 0.75, "strategy": 0.88, "action": 0.55, "casual": 0.22, "simulation": 0.38, "default": 0.55},
    "kr": {"rpg": 0.52, "strategy": 0.65, "action": 0.40, "casual": 0.15, "simulation": 0.28, "default": 0.38},
    "global": {"rpg": 0.25, "strategy": 0.32, "action": 0.18, "casual": 0.08, "simulation": 0.14, "default": 0.18}
}

class CPILTVForecaster:
    """Simulates mobile campaign unit economics and forecasts break-even timelines."""

    def __init__(self):
        pass

    def get_cpi_benchmark(self, country: str, genre: str, platform: str = "all") -> float:
        """Determines estimated CPI based on region, genre, and platform."""
        c_key = country.lower() if country.lower() in CPI_BENCHMARKS else "global"
        g_key = "default"
        for k in ["rpg", "strategy", "action", "casual", "simulation"]:
            if k in genre.lower():
                g_key = k
                break

        base_cpi = CPI_BENCHMARKS[c_key].get(g_key, CPI_BENCHMARKS[c_key]["default"])

        # Platform modifier: iOS has higher CPI, Android has lower CPI
        if platform.lower() == "ios":
            base_cpi *= 1.30
        elif platform.lower() == "android":
            base_cpi *= 0.88

        return round(base_cpi, 2)

    def simulate_ua_campaign(
        self,
        budget: float = 5000.0,
        country: str = "vn",
        genre: str = "rpg",
        platform: str = "all",
        custom_cpi: Optional[float] = None
    ) -> Dict[str, Any]:
        """Performs day-by-day 180-day simulation of installs, retention, revenue, and ROAS."""
        effective_budget = max(100.0, float(budget))
        cpi = float(custom_cpi) if custom_cpi and custom_cpi > 0 else self.get_cpi_benchmark(country, genre, platform)
        total_installs = int(effective_budget / cpi)

        # Retrieve region & genre ARPU
        c_key = country.lower() if country.lower() in DAU_ARPU_BENCHMARKS else "global"
        g_key = "default"
        for k in ["rpg", "strategy", "action", "casual", "simulation"]:
            if k in genre.lower():
                g_key = k
                break

        daily_arpu = DAU_ARPU_BENCHMARKS[c_key].get(g_key, DAU_ARPU_BENCHMARKS[c_key]["default"])
        if platform.lower() == "ios":
            daily_arpu *= 1.45  # Higher spending propensity on iOS

        # Interpolate 180 days retention power-law curve R(t) = R1 * t^(-alpha)
        # Using calibrated alpha from D1 and D30 benchmarks
        ret_bench = RETENTION_BENCHMARKS.get(g_key, RETENTION_BENCHMARKS["default"])
        r1 = ret_bench[0]   # D1 retention
        r30 = ret_bench[3]  # D30 retention
        alpha = -math.log(r30 / r1) / math.log(30.0) if r30 > 0 and r1 > 0 else 0.55

        # Simulate 180 days
        cumulative_rev = 0.0
        break_even_day = None
        milestone_roas = {}
        chart_labels = []
        chart_revenue = []
        chart_spend = []

        # Day 0: Install day (All users active, D0 IAP/Ad monetization)
        day_0_rev = total_installs * daily_arpu * 1.2
        cumulative_rev += day_0_rev

        for day in range(1, 181):
            retention_rate = r1 * (day ** (-alpha))
            active_users = total_installs * retention_rate
            day_rev = active_users * daily_arpu
            cumulative_rev += day_rev

            if break_even_day is None and cumulative_rev >= effective_budget:
                break_even_day = day

            if day in [7, 30, 60, 90, 180]:
                roas = round((cumulative_rev / effective_budget) * 100, 1)
                milestone_roas[f"D{day}"] = roas

            # Sample every 10 days for chart
            if day in [1, 7, 14, 30, 45, 60, 90, 120, 150, 180]:
                chart_labels.append(f"Ngày {day}")
                chart_revenue.append(round(cumulative_rev, 1))
                chart_spend.append(round(effective_budget, 1))

        # Financial summaries
        total_revenue_180d = round(cumulative_rev, 2)
        net_profit = round(total_revenue_180d - effective_budget, 2)
        final_roas = round((total_revenue_180d / effective_budget) * 100, 1)
        ltv_180d = round(total_revenue_180d / total_installs, 2)

        # Verdict classification
        if break_even_day and break_even_day <= 45:
            verdict = "SIÊU LỢI NHUẬN (HIGHLY PROFITABLE)"
            verdict_color = "emerald"
            verdict_advice = f"Chiến dịch hòa vốn sớm ở Ngày {break_even_day}. Bạn có thể tự tin tăng ngân sách UA (Scale-up) thêm +200% để chiếm lĩnh thị trường."
        elif break_even_day and break_even_day <= 90:
            verdict = "HÒA VỐN TỐT (VIABLE & SCALABLE)"
            verdict_color = "indigo"
            verdict_advice = f"Chiến dịch đạt điểm hòa vốn ở Ngày {break_even_day}. Tỷ suất ROAS 180 ngày đạt {final_roas}%. Nên tối ưu thêm LiveOps và Banner gacha tuần 2 để rút ngắn thời gian hoàn vốn về dưới 60 ngày."
        elif break_even_day:
            verdict = "HÒA VỐN CHẬM (EXTENDED BREAK-EVEN)"
            verdict_color = "amber"
            verdict_advice = f"Chiến dịch hòa vốn ở Ngày {break_even_day}. Cần nâng cao tỷ lệ giữ chân D7 và bổ sung thêm gói nạp Battle Pass để đẩy nhanh tốc độ thu hồi dòng tiền."
        else:
            verdict = "RỦI RO LỖ VỐN (HIGH LOSS RISK)"
            verdict_color = "rose"
            verdict_advice = "Chiến dịch chưa thể hòa vốn trong vòng 180 ngày. Tuyệt đối không scale ngân sách lớn! Hãy hạ CPI bằng video creative mới hoặc tăng Monetization/Ad eCPM trước."

        return {
            "inputs": {
                "budget": effective_budget,
                "country": country.upper(),
                "genre": genre.title(),
                "platform": platform.upper(),
                "cpi": cpi
            },
            "kpis": {
                "total_paid_installs": total_installs,
                "cpi_cost": cpi,
                "ltv_180d": ltv_180d,
                "break_even_day": break_even_day if break_even_day else "Chưa hòa vốn (>180 ngày)",
                "total_revenue_180d": total_revenue_180d,
                "net_profit": net_profit,
                "final_roas_pct": final_roas
            },
            "milestone_roas": milestone_roas,
            "verdict": {
                "status": verdict,
                "color": verdict_color,
                "advice": verdict_advice
            },
            "chart_data": {
                "labels": chart_labels,
                "cumulative_revenue": chart_revenue,
                "budget_line": chart_spend
            }
        }
