"""Ad Mediation & IAA Revenue Simulator Engine (AppLovin MAX / Google AdMob / Unity LevelPlay).

Provides comprehensive regional eCPM waterfall modeling, ad format revenue attribution
(Rewarded Video, Interstitial, Banner, App Open Ads), retention fatigue churn modeling,
and full LTV / ROAS Break-Even forecasting for mobile game studios.
"""

import math
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AdMediationEngine:
    """Simulates ad mediation waterfall yield, blended ARPDAU, and LTV/ROAS break-even timelines."""

    # Regional eCPM benchmarks (Blended medians across MAX / AdMob / LevelPlay)
    REGIONAL_BENCHMARKS = {
        "us": {
            "name": "United States (Tier 1 Premium)",
            "tier": "Tier 1",
            "rewarded_ecpm": 42.50,
            "interstitial_ecpm": 26.80,
            "banner_ecpm": 1.45,
            "aoa_ecpm": 22.00,
            "fill_rate": 0.98,
            "notes": "Thị trường quảng cáo có giá trị cao nhất thế giới, sức mua IAP cực mạnh."
        },
        "jp": {
            "name": "Japan (Tier 1 East Asia)",
            "tier": "Tier 1",
            "rewarded_ecpm": 34.00,
            "interstitial_ecpm": 21.50,
            "banner_ecpm": 1.10,
            "aoa_ecpm": 18.50,
            "fill_rate": 0.97,
            "notes": "Tỷ lệ xem trọn vẹn Rewarded Video cao, người chơi trung thành."
        },
        "kr": {
            "name": "South Korea (Tier 1 Hardcore)",
            "tier": "Tier 1",
            "rewarded_ecpm": 28.50,
            "interstitial_ecpm": 18.00,
            "banner_ecpm": 0.95,
            "aoa_ecpm": 15.00,
            "fill_rate": 0.96,
            "notes": "Cạnh tranh đấu thầu quyết liệt từ các tựa game MMORPG lớn."
        },
        "de_uk": {
            "name": "Western Europe (Tier 1 EU: DE, UK, FR)",
            "tier": "Tier 1",
            "rewarded_ecpm": 24.50,
            "interstitial_ecpm": 15.80,
            "banner_ecpm": 0.85,
            "aoa_ecpm": 13.50,
            "fill_rate": 0.95,
            "notes": "Tuân thủ nghiêm ngặt GDPR CMP consent, eCPM ổn định quanh năm."
        },
        "tier_2": {
            "name": "Tier 2 Mid-Market (TW, CA, AU, IT)",
            "tier": "Tier 2",
            "rewarded_ecpm": 17.50,
            "interstitial_ecpm": 11.20,
            "banner_ecpm": 0.58,
            "aoa_ecpm": 9.50,
            "fill_rate": 0.94,
            "notes": "Cân bằng tốt giữa volume tải về và sức chi trả."
        },
        "vn": {
            "name": "Vietnam (Tier 3 Southeast Asia)",
            "tier": "Tier 3",
            "rewarded_ecpm": 4.80,
            "interstitial_ecpm": 3.10,
            "banner_ecpm": 0.22,
            "aoa_ecpm": 2.60,
            "fill_rate": 0.96,
            "notes": "Lượng impression cực lớn, cần đặt giá sàn thông minh để tránh rác."
        },
        "br": {
            "name": "Brazil & LATAM (Tier 3 Volume)",
            "tier": "Tier 3",
            "rewarded_ecpm": 4.10,
            "interstitial_ecpm": 2.65,
            "banner_ecpm": 0.18,
            "aoa_ecpm": 2.20,
            "fill_rate": 0.95,
            "notes": "Thị trường volume khổng lồ cho game hành động / thể thao."
        },
        "sea_in": {
            "name": "India & Rest of SEA (Tier 3 Emerging)",
            "tier": "Tier 3",
            "rewarded_ecpm": 2.50,
            "interstitial_ecpm": 1.60,
            "banner_ecpm": 0.10,
            "aoa_ecpm": 1.40,
            "fill_rate": 0.92,
            "notes": "Tập trung tối đa vào Rewarded Video và tối ưu nén tài nguyên game."
        }
    }

    # Mediation Waterfall Architecture
    WATERFALL_TIERS = [
        {
            "priority": "Tầng 1: In-App Bidding Top Floor",
            "price_floor": "$35.00 - $55.00",
            "fill_share": "15 - 22%",
            "networks": "AppLovin Bidding, Google Bidding (AdMob), Meta Audience Network",
            "role": "Hớt váng những phiên đấu giá giá trị cao nhất từ các nhà quảng cáo lớn"
        },
        {
            "priority": "Tầng 2: Direct Line Items (High-Mid)",
            "price_floor": "$18.00 - $32.00",
            "fill_share": "28 - 35%",
            "networks": "Unity LevelPlay, Mintegral Bidding, Liftoff/Vungle",
            "role": "Đảm bảo lấp đầy doanh thu cốt lõi cho nhóm người chơi nạp và tương tác sâu"
        },
        {
            "priority": "Tầng 3: Secondary Liquidity (Mid-Low)",
            "price_floor": "$6.00 - $15.00",
            "fill_share": "30 - 40%",
            "networks": "Pangle (TikTok Ads), InMobi, IronSource Exchange",
            "role": "Duy trì thanh khoản impression cho các thị trường Tier 2 & Tier 3"
        },
        {
            "priority": "Tầng 4: Backfill Auto-Refresh Floor",
            "price_floor": "$0.50 Base Auto-Bid",
            "fill_share": "99.2% Fill Rate",
            "networks": "AdMob Backfill, AppLovin Network Backfill",
            "role": "Bảo đảm không bao giờ bị lãng phí impression trắng (No-Fill)"
        }
    ]

    def __init__(self):
        pass

    def get_benchmarks(self) -> Dict[str, Any]:
        """Returns standard regional benchmarks and waterfall architecture."""
        return {
            "regional_benchmarks": list(self.REGIONAL_BENCHMARKS.values()),
            "waterfall_tiers": self.WATERFALL_TIERS
        }

    def simulate(
        self,
        dau: int = 50000,
        avg_session_mins: int = 15,
        sessions_per_day: float = 2.4,
        interstitial_cooldown_secs: int = 75,
        rewarded_watches_per_user: float = 2.8,
        banner_enabled: bool = True,
        aoa_enabled: bool = True,
        tier1_pct: float = 30.0,
        tier2_pct: float = 25.0,
        tier3_pct: float = 45.0,
        iap_share_pct: float = 30.0,
        target_cpi: float = 0.65
    ) -> Dict[str, Any]:
        """Performs full end-to-end mediation yield, ARPDAU, LTV, and ROAS break-even simulation."""
        safe_dau = max(100, int(dau))
        safe_cooldown = max(20, int(interstitial_cooldown_secs))
        safe_session_mins = max(3, int(avg_session_mins))
        safe_cpi = max(0.05, float(target_cpi))

        # Normalize region weights
        total_weight = tier1_pct + tier2_pct + tier3_pct
        if total_weight <= 0:
            w_t1, w_t2, w_t3 = 0.3, 0.25, 0.45
        else:
            w_t1 = tier1_pct / total_weight
            w_t2 = tier2_pct / total_weight
            w_t3 = tier3_pct / total_weight

        # Blended Regional eCPMs
        # T1 weighted: US 60%, DE_UK 40%
        t1_rv = self.REGIONAL_BENCHMARKS["us"]["rewarded_ecpm"] * 0.6 + self.REGIONAL_BENCHMARKS["de_uk"]["rewarded_ecpm"] * 0.4
        t1_fs = self.REGIONAL_BENCHMARKS["us"]["interstitial_ecpm"] * 0.6 + self.REGIONAL_BENCHMARKS["de_uk"]["interstitial_ecpm"] * 0.4
        t1_bn = self.REGIONAL_BENCHMARKS["us"]["banner_ecpm"] * 0.6 + self.REGIONAL_BENCHMARKS["de_uk"]["banner_ecpm"] * 0.4
        t1_aoa = self.REGIONAL_BENCHMARKS["us"]["aoa_ecpm"] * 0.6 + self.REGIONAL_BENCHMARKS["de_uk"]["aoa_ecpm"] * 0.4

        # T2
        t2_rv = self.REGIONAL_BENCHMARKS["tier_2"]["rewarded_ecpm"]
        t2_fs = self.REGIONAL_BENCHMARKS["tier_2"]["interstitial_ecpm"]
        t2_bn = self.REGIONAL_BENCHMARKS["tier_2"]["banner_ecpm"]
        t2_aoa = self.REGIONAL_BENCHMARKS["tier_2"]["aoa_ecpm"]

        # T3 weighted: VN 50%, BR 50%
        t3_rv = self.REGIONAL_BENCHMARKS["vn"]["rewarded_ecpm"] * 0.5 + self.REGIONAL_BENCHMARKS["br"]["rewarded_ecpm"] * 0.5
        t3_fs = self.REGIONAL_BENCHMARKS["vn"]["interstitial_ecpm"] * 0.5 + self.REGIONAL_BENCHMARKS["br"]["interstitial_ecpm"] * 0.5
        t3_bn = self.REGIONAL_BENCHMARKS["vn"]["banner_ecpm"] * 0.5 + self.REGIONAL_BENCHMARKS["br"]["banner_ecpm"] * 0.5
        t3_aoa = self.REGIONAL_BENCHMARKS["vn"]["aoa_ecpm"] * 0.5 + self.REGIONAL_BENCHMARKS["br"]["aoa_ecpm"] * 0.5

        blended_rv_ecpm = round(w_t1 * t1_rv + w_t2 * t2_rv + w_t3 * t3_rv, 2)
        blended_fs_ecpm = round(w_t1 * t1_fs + w_t2 * t2_fs + w_t3 * t3_fs, 2)
        blended_bn_ecpm = round(w_t1 * t1_bn + w_t2 * t2_bn + w_t3 * t3_bn, 2)
        blended_aoa_ecpm = round(w_t1 * t1_aoa + w_t2 * t2_aoa + w_t3 * t3_aoa, 2)

        # 1. Interstitial Impressions Calculation
        # Number of interstitials per session = session_seconds / cooldown
        session_seconds = safe_session_mins * 60
        fs_per_session = max(0.5, session_seconds / safe_cooldown)
        daily_fs_impressions = int(safe_dau * sessions_per_day * fs_per_session)

        # 2. Rewarded Video Impressions
        daily_rv_impressions = int(safe_dau * rewarded_watches_per_user)

        # 3. Banner Impressions (Refreshed every 30 seconds)
        banner_refresh_rate = 30 # seconds
        banners_per_session = (session_seconds / banner_refresh_rate) if banner_enabled else 0
        daily_bn_impressions = int(safe_dau * sessions_per_day * banners_per_session) if banner_enabled else 0

        # 4. App Open Ads (Shown on cold starts and app resumes)
        aoa_per_day = min(3.0, sessions_per_day * 0.8) if aoa_enabled else 0
        daily_aoa_impressions = int(safe_dau * aoa_per_day) if aoa_enabled else 0

        # Daily Revenue by Format
        daily_rv_rev = (daily_rv_impressions * blended_rv_ecpm) / 1000.0
        daily_fs_rev = (daily_fs_impressions * blended_fs_ecpm) / 1000.0
        daily_bn_rev = (daily_bn_impressions * blended_bn_ecpm) / 1000.0
        daily_aoa_rev = (daily_aoa_impressions * blended_aoa_ecpm) / 1000.0

        daily_total_ad_rev = daily_rv_rev + daily_fs_rev + daily_bn_rev + daily_aoa_rev
        monthly_total_ad_rev = daily_total_ad_rev * 30.0

        # Ad ARPDAU (USD)
        ad_arpdau = round(daily_total_ad_rev / safe_dau, 4)

        # Blended IAP Calculation
        # iap_share_pct of total revenue: Ad_Rev = (1 - iap_share) * Total_Rev
        iap_ratio = max(0.0, min(0.8, iap_share_pct / 100.0))
        if iap_ratio < 1.0:
            total_daily_rev = daily_total_ad_rev / (1.0 - iap_ratio)
            daily_iap_rev = total_daily_rev - daily_total_ad_rev
        else:
            daily_iap_rev = daily_total_ad_rev
            total_daily_rev = daily_total_ad_rev * 2

        iap_arpdau = round(daily_iap_rev / safe_dau, 4)
        blended_arpdau = round(ad_arpdau + iap_arpdau, 4)
        monthly_gross_total = round(total_daily_rev * 30.0, 2)

        # Ad Fatigue Churn Penalty
        # Sweet spot is 75s - 90s
        if safe_cooldown < 40:
            churn_risk_level = "CRITICAL"
            churn_risk_title = "🚨 BÃO QUẢNG CÁO CỰC ĐOAN (Nguy Cơ Gỡ Game Hàng Loạt)"
            retention_penalty_pct = -25.0
            churn_advice = "Khoảng cách < 40s tạo cảm giác bị 'tra tấn quảng cáo'. D1 Retention sẽ giảm trên 25% và điểm đánh giá Store sẽ rơi xuống dưới 3.5 sao."
            badge_color = "rose"
        elif safe_cooldown < 60:
            churn_risk_level = "WARNING"
            churn_risk_title = "⚠️ TẦN SUẤT DÀY ĐẶC (Nguy Cơ Sụt Churn D7)"
            retention_penalty_pct = -12.0
            churn_advice = "Doanh thu ngày có thể tăng ngắn hạn, nhưng người chơi sẽ bỏ rơi game sau 3-5 ngày. Cân nhắc nâng lên 75s."
            badge_color = "amber"
        elif safe_cooldown <= 95:
            churn_risk_level = "OPTIMAL"
            churn_risk_title = "✅ ĐIỂM CÂN BẰNG VÀNG (Golden Sweet Spot)"
            retention_penalty_pct = 0.0
            churn_advice = "Tần suất 75s - 95s là tiêu chuẩn vàng của ngành Hybrid-Casual. Tối đa hóa doanh thu mà vẫn bảo vệ trải nghiệm người chơi."
            badge_color = "emerald"
        else:
            churn_risk_level = "PASSIVE"
            churn_risk_title = "ℹ️ QUÁ THƯA THỚT (Bỏ Lỡ Doanh Thu Ads)"
            retention_penalty_pct = 0.0
            churn_advice = "Người chơi rất thoải mái nhưng studio đang thất thoát khoảng 20% - 30% doanh thu tiềm năng từ interstitial."
            badge_color = "indigo"

        # Baseline Hybrid-Casual Retention Profile (D0, D1, D3, D7, D14, D30, D60)
        base_retention = {
            1: 0.38,
            3: 0.24,
            7: 0.16,
            14: 0.10,
            30: 0.055,
            60: 0.025
        }

        # Apply fatigue churn penalty to retention
        penalty_factor = 1.0 + (retention_penalty_pct / 100.0)
        retention_curve = {d: round(max(0.01, base_retention[d] * penalty_factor), 3) for d in base_retention}

        # Cumulative LTV Modeling (D1 to D60)
        # LTV(D_n) = ARPDAU * sum(Retention(i) for i in 1..n)
        ltv_timeline = []
        running_ltv = blended_arpdau # Day 0 install day
        break_even_day = None

        for day in range(1, 61):
            # Interpolated retention for day
            if day == 1:
                r_day = retention_curve[1]
            elif day <= 3:
                r_day = retention_curve[1] + (retention_curve[3] - retention_curve[1]) * ((day - 1) / 2.0)
            elif day <= 7:
                r_day = retention_curve[3] + (retention_curve[7] - retention_curve[3]) * ((day - 3) / 4.0)
            elif day <= 14:
                r_day = retention_curve[7] + (retention_curve[14] - retention_curve[7]) * ((day - 7) / 7.0)
            elif day <= 30:
                r_day = retention_curve[14] + (retention_curve[30] - retention_curve[14]) * ((day - 14) / 16.0)
            else:
                r_day = retention_curve[30] + (retention_curve[60] - retention_curve[30]) * ((day - 30) / 30.0)

            running_ltv += blended_arpdau * r_day
            curr_ltv_val = round(running_ltv, 3)

            # Check break-even against target CPI
            if break_even_day is None and curr_ltv_val >= safe_cpi:
                break_even_day = day

            ltv_timeline.append({
                "day": day,
                "label": f"D{day}",
                "retention": round(r_day * 100, 1),
                "cumulative_ltv": curr_ltv_val,
                "target_cpi": safe_cpi,
                "roas_pct": round((curr_ltv_val / safe_cpi) * 100, 1)
            })

        # Key LTV milestones
        ltv_d1 = ltv_timeline[0]["cumulative_ltv"]
        ltv_d7 = ltv_timeline[6]["cumulative_ltv"]
        ltv_d14 = ltv_timeline[13]["cumulative_ltv"]
        ltv_d30 = ltv_timeline[29]["cumulative_ltv"]
        ltv_d60 = ltv_timeline[59]["cumulative_ltv"]

        roas_d7 = ltv_timeline[6]["roas_pct"]
        roas_d30 = ltv_timeline[29]["roas_pct"]
        roas_d60 = ltv_timeline[59]["roas_pct"]

        # Unit Economics & Monthly Profitability Projection
        # Monthly new users acquired
        monthly_installs = int((safe_dau * 0.08) * 30) # Estimated healthy churn replacement
        monthly_ua_spend = round(monthly_installs * safe_cpi, 2)
        monthly_net_profit = round(monthly_gross_total - monthly_ua_spend, 2)
        net_profit_margin_pct = round((monthly_net_profit / max(1.0, monthly_gross_total)) * 100, 1)

        return {
            "inputs": {
                "dau": safe_dau,
                "avg_session_mins": safe_session_mins,
                "sessions_per_day": sessions_per_day,
                "interstitial_cooldown_secs": safe_cooldown,
                "rewarded_watches_per_user": rewarded_watches_per_user,
                "banner_enabled": banner_enabled,
                "aoa_enabled": aoa_enabled,
                "region_weights": {"tier_1": round(w_t1 * 100, 1), "tier_2": round(w_t2 * 100, 1), "tier_3": round(w_t3 * 100, 1)},
                "iap_share_pct": iap_share_pct,
                "target_cpi": safe_cpi
            },
            "blended_ecpms": {
                "rewarded_video": blended_rv_ecpm,
                "interstitial": blended_fs_ecpm,
                "banner": blended_bn_ecpm,
                "app_open_ads": blended_aoa_ecpm
            },
            "daily_revenue_breakdown": {
                "rewarded_video_usd": round(daily_rv_rev, 2),
                "interstitial_usd": round(daily_fs_rev, 2),
                "banner_usd": round(daily_bn_rev, 2),
                "app_open_ads_usd": round(daily_aoa_rev, 2),
                "total_ad_revenue_usd": round(daily_total_ad_rev, 2),
                "total_iap_revenue_usd": round(daily_iap_rev, 2),
                "gross_daily_total_usd": round(total_daily_rev, 2)
            },
            "monthly_projection": {
                "gross_ad_revenue_usd": round(monthly_total_ad_rev, 2),
                "gross_iap_revenue_usd": round(daily_iap_rev * 30.0, 2),
                "gross_total_revenue_usd": monthly_gross_total,
                "estimated_ua_spend_usd": monthly_ua_spend,
                "net_profit_usd": monthly_net_profit,
                "profit_margin_pct": net_profit_margin_pct
            },
            "arpdau_metrics": {
                "ad_arpdau": ad_arpdau,
                "iap_arpdau": iap_arpdau,
                "blended_arpdau": blended_arpdau
            },
            "ad_fatigue_diagnostic": {
                "risk_level": churn_risk_level,
                "title": churn_risk_title,
                "penalty_pct": retention_penalty_pct,
                "advice": churn_advice,
                "badge_color": badge_color
            },
            "ltv_milestones": {
                "d1_ltv": ltv_d1,
                "d7_ltv": ltv_d7,
                "d14_ltv": ltv_d14,
                "d30_ltv": ltv_d30,
                "d60_ltv": ltv_d60,
                "target_cpi": safe_cpi,
                "payback_day": break_even_day or "Chưa đạt (sau D60)",
                "roas_d7_pct": roas_d7,
                "roas_d30_pct": roas_d30,
                "roas_d60_pct": roas_d60
            },
            "ltv_curve_points": ltv_timeline[:30], # First 30 days for primary chart
            "waterfall_setup_guide": self.WATERFALL_TIERS
        }
