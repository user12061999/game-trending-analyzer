"""LiveOps Event Calendar & Competitor Clash Radar Engine.

Provides event templates, revenue lift multipliers, competitor update cadence tracking,
and auction clash avoidance scoring for mobile UA & LiveOps synchronization.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class LiveOpsScheduler:
    """LiveOps Lifecycle Planning & Competitor Clash Avoidance System."""

    def __init__(self):
        # Event archetype templates
        self.event_templates = [
            {
                "id": "battle_pass_season",
                "name": "Battle Pass / Season Reset",
                "cadence": "Every 28 - 30 Days",
                "typical_duration_days": 28,
                "revenue_lift": "+75%",
                "dau_lift": "+14%",
                "retention_d7_lift": "+8%",
                "revenue_curve": "Front-loaded (40% of pass sales occur within the first 72 hours)",
                "recommended_day": "Thursday or Friday 10:00 UTC",
                "best_mechanics": ["Free tier vs Premium tier side-by-side", "Instant Tier 1 Hero/Skin unlock", "Bonus currency for final milestones"],
                "monetization_impact": "Drives high recurring volume from Minnows and Dolphins."
            },
            {
                "id": "limited_collab_gacha",
                "name": "Limited IP Collab / Anniversary Gacha Banner",
                "cadence": "Quarterly (Every 60 - 90 Days)",
                "typical_duration_days": 14,
                "revenue_lift": "+180%",
                "dau_lift": "+28%",
                "retention_d7_lift": "+18%",
                "revenue_curve": "Severe Spike (60% revenue concentrated in Day 1-2)",
                "recommended_day": "Wednesday or Thursday",
                "best_mechanics": ["Exclusive character never re-running for 12 months", "Pity system counter carries over", "Special Collab Login Pass"],
                "monetization_impact": "Drives extreme Whale spending and reactivates dormant high-value players."
            },
            {
                "id": "weekend_guild_raid",
                "name": "Weekend Guild War / Server vs Server (KvK)",
                "cadence": "Bi-weekly (Friday 18:00 to Sunday 23:59)",
                "typical_duration_days": 3,
                "revenue_lift": "+38%",
                "dau_lift": "+22%",
                "retention_d7_lift": "+12%",
                "revenue_curve": "Climax curve (Peak spending on Saturday night & Sunday last-minute leaderboard snipes)",
                "recommended_day": "Friday 18:00 Local Server Time",
                "best_mechanics": ["Guild Leader ranking rewards", "Troop speedup emergency bundles", "Alliance gift boxes sent to all members"],
                "monetization_impact": "Fosters peer pressure, social status spending, and alliance rivalry."
            },
            {
                "id": "flash_piggy_smash",
                "name": "Flash Sale & Piggy Bank Vault Break",
                "cadence": "Weekly or Mid-week Churn Choke Point",
                "typical_duration_days": 2,
                "revenue_lift": "+45%",
                "dau_lift": "+6%",
                "retention_d7_lift": "+4%",
                "revenue_curve": "Urgency curve (Spikes at 24h and final 2h countdown)",
                "recommended_day": "Tuesday or Wednesday (Mid-week slump recovery)",
                "best_mechanics": ["Count down timer under 48 hours", "90% off sticker comparison", "Piggy Bank bursting animation"],
                "monetization_impact": "Converts fence-sitting F2P users into first-time paying Minnows."
            },
            {
                "id": "seasonal_holiday_festival",
                "name": "Seasonal Holiday Mega Festival (Lunar New Year, Halloween, Christmas)",
                "cadence": "Annual / Seasonal",
                "typical_duration_days": 21,
                "revenue_lift": "+95%",
                "dau_lift": "+32%",
                "retention_d7_lift": "+15%",
                "revenue_curve": "Sustained high with two distinct peaks (Launch day and Finale climax)",
                "recommended_day": "10-14 days prior to the actual calendar holiday",
                "best_mechanics": ["Red Packet / Lucky Draw mini-games", "Festive UI skin & music overhaul", "Tiered Milestone Community Goals"],
                "monetization_impact": "Captures holiday gift spending and vacation free-time play."
            }
        ]

        # Mobile Gaming Titans Release Cadence & Auction Competition Tracker
        self.competitor_schedules = [
            {
                "publisher": "HoYoverse",
                "titles": ["Genshin Impact", "Honkai: Star Rail", "Zenless Zone Zero"],
                "cadence_days": 42,  # Exactly 6-week cycle
                "update_weekday": "Wednesday",
                "ad_auction_impact": "+45% to +60% Meta/TikTok auction CPI surge for 5 days post-patch",
                "notes": "Tránh launch game mới hoặc đẩy UA lớn vào tuần ra mắt phiên bản mới của HoYoverse vì giá bid CPI bị đẩy kịch trần."
            },
            {
                "publisher": "Supercell",
                "titles": ["Brawl Stars", "Clash of Clans", "Clash Royale"],
                "cadence_days": 30,
                "update_weekday": "Thursday",
                "ad_auction_impact": "+25% to +35% Google Ads & YouTube auction surge",
                "notes": "Reset Brawl Pass vào ngày Thứ Năm đầu tiên mỗi tháng. Lượng user casual và gen Z tập trung cao độ."
            },
            {
                "publisher": "Scopely",
                "titles": ["Monopoly GO", "Stumble Guys"],
                "cadence_days": 7,
                "update_weekday": "Daily & Weekend",
                "ad_auction_impact": "+30% AdMob & Unity Ads rewarded interstitial cost",
                "notes": "Chạy UA bền bỉ $1M+/ngày. Cạnh tranh khốc liệt vị trí Top Grossing trên Store."
            },
            {
                "publisher": "Garena",
                "titles": ["Free Fire", "Arena of Valor / Lien Quan Mobile"],
                "cadence_days": 30,
                "update_weekday": "1st of Month & Friday",
                "ad_auction_impact": "+40% SEA Regional social ads & TikTok influencer saturation",
                "notes": "Đầu tháng reset Booyah Pass/Sổ Sứ Mệnh; cuối tuần có giải đấu eSports ĐTDV/AIC."
            },
            {
                "publisher": "Tencent / Level Infinite",
                "titles": ["PUBG Mobile", "Honor of Kings Global", "NIKKE"],
                "cadence_days": 60,
                "update_weekday": "Tuesday or Thursday",
                "ad_auction_impact": "+50% Global Tier 1 & SEA market share grab",
                "notes": "Thường có các đợt collab Anime/siêu xe quy mô toàn cầu."
            }
        ]

    def get_event_templates(self) -> List[Dict[str, Any]]:
        """Returns standard LiveOps templates with benchmarks."""
        return self.event_templates

    def get_competitor_radar(self) -> Dict[str, Any]:
        """Returns competitor update cadence and upcoming high-risk auction windows."""
        today = datetime.now()
        upcoming_windows = []

        # Generate sample realistic upcoming collision milestones for the current/next month
        for comp in self.competitor_schedules:
            # Estimate next 2 patch windows
            next_patch = today + timedelta(days=((today.day * 3 + hash(comp["publisher"])) % 24) + 2)
            risk_level = "High" if "HoYoverse" in comp["publisher"] or "Garena" in comp["publisher"] else "Medium"
            upcoming_windows.append({
                "publisher": comp["publisher"],
                "titles": comp["titles"],
                "estimated_patch_date": next_patch.strftime("%Y-%m-%d"),
                "weekday": next_patch.strftime("%A"),
                "risk_level": risk_level,
                "auction_impact": comp["ad_auction_impact"],
                "advisory": comp["notes"]
            })

        upcoming_windows.sort(key=lambda x: x["estimated_patch_date"])

        return {
            "competitors": self.competitor_schedules,
            "upcoming_clash_windows": upcoming_windows,
            "best_practices": [
                "Nên tung bản cập nhật/Battle Pass vào Thứ Năm 10:00 UTC để người chơi kịp cập nhật trước đợt cao điểm cuối tuần.",
                "Tránh set ngày chạy chiến dịch UA đỉnh điểm (Burst UA) trùng khớp vào ngày HoYoverse hoặc Supercell tung bản cập nhật lớn.",
                "Tận dụng khoảng trống giữa tuần (Thứ Ba - Thứ Tư) cho các Mini Event/Flash Sale để duy trì DAU không bị tụt dốc."
            ]
        }

    def plan_liveops_event(
        self,
        event_type_id: str,
        start_date: str,
        duration_days: int = 14,
        base_dau: int = 25000,
        base_arpdau: float = 0.08
    ) -> Dict[str, Any]:
        """Plans a LiveOps event, forecasts daily revenue spike, and evaluates competitor clash risks."""
        template = next((t for t in self.event_templates if t["id"] == event_type_id), self.event_templates[0])

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except Exception:
            start_dt = datetime.now() + timedelta(days=7)

        # Baseline revenue
        daily_baseline_rev = base_dau * base_arpdau
        total_baseline_rev = daily_baseline_rev * duration_days

        # Revenue lift multiplier
        lift_str = template["revenue_lift"].replace("+", "").replace("%", "")
        max_lift_pct = float(lift_str) / 100.0

        daily_forecast = []
        total_event_rev = 0.0

        for day_idx in range(1, duration_days + 1):
            cur_dt = start_dt + timedelta(days=day_idx - 1)
            # Modeling curve based on event type
            if template["id"] == "battle_pass_season":
                # Front loaded
                if day_idx <= 3:
                    day_mult = 1.0 + max_lift_pct * (1.2 - (day_idx - 1) * 0.25)
                elif day_idx >= duration_days - 3:
                    day_mult = 1.0 + max_lift_pct * 0.45  # End of season rush
                else:
                    day_mult = 1.0 + max_lift_pct * 0.20
            elif template["id"] == "limited_collab_gacha":
                # Super front-loaded
                if day_idx == 1:
                    day_mult = 1.0 + max_lift_pct * 1.5
                elif day_idx == 2:
                    day_mult = 1.0 + max_lift_pct * 1.1
                elif day_idx == duration_days:
                    day_mult = 1.0 + max_lift_pct * 0.6  # Last chance
                else:
                    day_mult = 1.0 + max_lift_pct * 0.15
            elif template["id"] == "flash_piggy_smash":
                day_mult = 1.0 + max_lift_pct * (0.8 if day_idx == 1 else 1.2)
            else:
                # Normal bell-like or sustained curve
                day_mult = 1.0 + max_lift_pct * 0.5

            day_rev = round(daily_baseline_rev * day_mult, 2)
            total_event_rev += day_rev
            daily_forecast.append({
                "day": day_idx,
                "date": cur_dt.strftime("%Y-%m-%d"),
                "weekday": cur_dt.strftime("%a"),
                "projected_revenue": day_rev,
                "baseline_revenue": round(daily_baseline_rev, 2),
                "lift_multiplier": round(day_mult, 2)
            })

        incremental_revenue = round(total_event_rev - total_baseline_rev, 2)
        total_event_rev = round(total_event_rev, 2)

        # Clash Risk assessment for start_dt
        weekday_name = start_dt.strftime("%A")
        if weekday_name in ["Friday", "Saturday"]:
            timing_grade = "Tốt (Weekend Warmup)"
            timing_tip = "Khởi chạy trước hoặc đúng đầu dịp cuối tuần giúp hấp thụ tối đa thời gian online của game thủ."
        elif weekday_name == "Thursday":
            timing_grade = "Tối Ưu Nhất (Gold Standard)"
            timing_tip = "Thứ Năm là ngày tiêu chuẩn vàng của ngành game mobile (cho phép cập nhật client và warm up server trước thứ 6)."
        else:
            timing_grade = "Trung Bình"
            timing_tip = f"Khởi chạy vào {weekday_name} có thể gặp lượng DAU thấp hơn so với cuối tuần."

        return {
            "event_info": {
                "template_name": template["name"],
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "duration_days": duration_days,
                "cadence": template["cadence"],
                "recommended_mechanics": template["best_mechanics"]
            },
            "financial_forecast": {
                "total_event_revenue_usd": total_event_rev,
                "baseline_revenue_usd": round(total_baseline_rev, 2),
                "incremental_revenue_gain_usd": incremental_revenue,
                "gross_revenue_lift_pct": round((incremental_revenue / max(1, total_baseline_rev)) * 100, 1),
                "peak_day_revenue_usd": max(d["projected_revenue"] for d in daily_forecast)
            },
            "timing_advisory": {
                "start_weekday": weekday_name,
                "timing_grade": timing_grade,
                "recommendation": timing_tip
            },
            "daily_forecast": daily_forecast
        }
