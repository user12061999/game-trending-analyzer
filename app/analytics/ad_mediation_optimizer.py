"""Ad Mediation Waterfall & eCPM Floor Yield Optimizer.

Provides regional eCPM floor benchmarks for Rewarded Video, Interstitial, and Banner,
simulates AppLovin MAX / AdMob waterfall architectures, and models frequency capping vs retention churn.
"""

from typing import Dict, Any, List, Optional

class AdMediationOptimizer:
    """Mediation yield optimizer and ad fatigue churn simulator."""

    def __init__(self):
        # Regional eCPM Floor Benchmarks (Median across AppLovin MAX / AdMob / LevelPlay)
        self.ecpm_benchmarks = [
            {"region": "US (United States)", "tier": "Tier 1", "rewarded_ecpm": 38.50, "interstitial_ecpm": 24.00, "banner_ecpm": 1.20, "notes": "Thị trường quảng cáo có giá trị cao nhất thế giới"},
            {"region": "JP (Japan)", "tier": "Tier 1", "rewarded_ecpm": 32.00, "interstitial_ecpm": 19.50, "banner_ecpm": 0.95, "notes": "Tỷ lệ xem hết Rewarded Video cực kỳ cao"},
            {"region": "KR (South Korea)", "tier": "Tier 1", "rewarded_ecpm": 26.50, "interstitial_ecpm": 16.00, "banner_ecpm": 0.85, "notes": "Cạnh tranh đấu thầu mạnh từ game MMORPG nội địa"},
            {"region": "DE / UK (Europe)", "tier": "Tier 1", "rewarded_ecpm": 22.00, "interstitial_ecpm": 14.20, "banner_ecpm": 0.70, "notes": "Tuân thủ chặt chẽ GDPR consent form"},
            {"region": "TW / HK (Taiwan/HK)", "tier": "Tier 2", "rewarded_ecpm": 16.50, "interstitial_ecpm": 10.50, "banner_ecpm": 0.55, "notes": "Cầu nối văn hóa Đông Á, sức mua khá"},
            {"region": "VN (Vietnam)", "tier": "Tier 3", "rewarded_ecpm": 4.50, "interstitial_ecpm": 2.80, "banner_ecpm": 0.18, "notes": "Lượng impression rất lớn, cần đặt giá sàn để tránh rác"},
            {"region": "BR (Brazil)", "tier": "Tier 3", "rewarded_ecpm": 3.80, "interstitial_ecpm": 2.40, "banner_ecpm": 0.15, "notes": "Thị trường volume lớn, fill rate cao"},
            {"region": "ID / IN (SEA/India)", "tier": "Tier 3", "rewarded_ecpm": 2.20, "interstitial_ecpm": 1.40, "banner_ecpm": 0.08, "notes": "Tập trung tối ưu rewarded video để cứu eCPM"}
        ]

        # Standard Mediation Waterfall Architecture
        self.waterfall_templates = [
            {"level": "Top Priority (High Floor)", "target_floor": "$40.00+", "fill_expectation": "12 - 18%", "network_allocation": "AppLovin Bidding, Google Bidding, Unity Ads High Price Floor"},
            {"level": "Second Priority (Mid Floor)", "target_floor": "$20.00 - $35.00", "fill_expectation": "25 - 35%", "network_allocation": "Mintegral Bidding, Vungle/Liftoff, InMobi"},
            {"level": "Standard Liquidity (Low Floor)", "target_floor": "$8.00 - $15.00", "fill_expectation": "30 - 40%", "network_allocation": "Pangle (TikTok), IronSource, Chartboost"},
            {"level": "Backfill Floor ($0 Base)", "target_floor": "$0.50 Auto-Bid", "fill_expectation": "99% Fill Rate", "network_allocation": "AdMob Backfill, AppLovin Network Backfill"}
        ]

    def get_benchmarks(self) -> Dict[str, Any]:
        """Returns regional eCPM benchmarks and waterfall architecture."""
        return {
            "ecpm_benchmarks": self.ecpm_benchmarks,
            "waterfall_templates": self.waterfall_templates
        }

    def simulate_mediation_yield(
        self,
        dau: int = 50000,
        avg_session_mins: int = 15,
        interstitial_cooldown_secs: int = 60,
        rewarded_watches_per_user: float = 2.5,
        region_tier: str = "us"
    ) -> Dict[str, Any]:
        """Simulates 30-day Ad revenue and evaluates player retention churn penalty from ad fatigue."""
        # Find regional eCPM
        geo = next((g for g in self.ecpm_benchmarks if region_tier.lower() in g["region"].lower()), self.ecpm_benchmarks[0])

        rewarded_ecpm = geo["rewarded_ecpm"]
        interstitial_ecpm = geo["interstitial_ecpm"]

        # Number of interstitials per session
        session_seconds = avg_session_mins * 60
        # If cooldown is too short, more ads, but heavier churn
        interstitials_per_session = max(0, int(session_seconds / max(30, interstitial_cooldown_secs)))
        daily_interstitials = dau * interstitials_per_session
        daily_rewarded = int(dau * rewarded_watches_per_user)

        # Monthly gross ad revenue
        monthly_interstitial_rev = (daily_interstitials * 30 * interstitial_ecpm) / 1000.0
        monthly_rewarded_rev = (daily_rewarded * 30 * rewarded_ecpm) / 1000.0
        total_monthly_ad_rev = round(monthly_interstitial_rev + monthly_rewarded_rev, 2)

        # Retention Churn Penalty from Frequency Capping
        # Ideal cooldown: 75s - 90s (0% penalty)
        # Danger: < 45s (-22% retention penalty), 45-60s (-10% penalty)
        if interstitial_cooldown_secs < 45:
            churn_risk = "CỰC KỲ NGUY HIỂM: BÃO QUẢNG CÁO GÂY GỠ GAME"
            retention_impact_pct = -22.5
            badge_color = "rose"
            advisory = "Khoảng cách < 45 giây khiến người chơi cảm giác bị 'ép xem rác'. D1 retention sẽ sụt giảm trên 20%."
        elif interstitial_cooldown_secs < 60:
            churn_risk = "CẢNH BÁO: TẦN SUẤT QUẢNG CÁO DÀY ĐẶC"
            retention_impact_pct = -10.0
            badge_color = "amber"
            advisory = "Doanh thu tăng trong 3 ngày đầu nhưng sẽ làm tăng churn rate người chơi vào D7."
        elif interstitial_cooldown_secs <= 90:
            churn_risk = "ĐIỂM CÂN BẰNG VÀNG (Golden Sweet Spot)"
            retention_impact_pct = 0.0
            badge_color = "emerald"
            advisory = "Khoảng cách 75-90 giây là tiêu chuẩn vàng của ngành game mobile. Tối ưu doanh thu mà không gây ức chế."
        else:
            churn_risk = "QUÁ THƯA THỚT: THẤT THOÁT DOANH THU ADS"
            retention_impact_pct = 0.0
            badge_color = "indigo"
            advisory = "Người chơi rất thoải mái nhưng studio đang bỏ lỡ khoảng 25-35% doanh thu quảng cáo tiềm năng."

        return {
            "inputs": {
                "dau": dau,
                "region_selected": geo["region"],
                "interstitial_cooldown_secs": interstitial_cooldown_secs,
                "rewarded_watches_per_user": rewarded_watches_per_user
            },
            "revenue_forecast": {
                "total_monthly_ad_revenue_usd": total_monthly_ad_rev,
                "monthly_rewarded_rev_usd": round(monthly_rewarded_rev, 2),
                "monthly_interstitial_rev_usd": round(monthly_interstitial_rev, 2),
                "daily_interstitial_impressions": daily_interstitials,
                "daily_rewarded_impressions": daily_rewarded,
                "effective_ad_arpdau_usd": round(total_monthly_ad_rev / (max(1, dau) * 30), 4)
            },
            "ad_fatigue_churn_analysis": {
                "churn_risk_level": churn_risk,
                "badge_color": badge_color,
                "projected_d1_retention_penalty": f"{retention_impact_pct}%",
                "strategic_recommendation": advisory
            }
        }
