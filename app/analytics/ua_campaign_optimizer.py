"""UA Campaign Budget Optimizer & ROAS Dayparting Engine.

Calculates hourly spend allocation (dayparting) across TikTok, Meta, and Unity Ads,
generates algorithmic ROAS pacing kill-switches, and models mobile gamer spending hours.
"""

from typing import Dict, Any, List, Optional
import math

class UACampaignOptimizer:
    """Mobile UA Budget Pacing & Dayparting Optimization Engine."""

    def __init__(self):
        # 24-Hour Mobile Gaming Behavioral Benchmark Matrix (00:00 to 23:00)
        # Hour: (Traffic Index 0-100, IAP Propensity 0-100, Recommended Bid Multiplier)
        self.hourly_behavior_profile = [
            {"hour": 0, "label": "00:00 - 01:00", "traffic": 25, "iap_intent": 15, "bid_mult": 0.45, "phase": "Late Night Churn", "advisory": "Giảm bid 55%, chỉ giữ lại ad set retargeting"},
            {"hour": 1, "label": "01:00 - 02:00", "traffic": 18, "iap_intent": 10, "bid_mult": 0.35, "phase": "Sleeping Dead Zone", "advisory": "Giảm bid tối đa để tránh ghost clicks"},
            {"hour": 2, "label": "02:00 - 03:00", "traffic": 12, "iap_intent": 8, "bid_mult": 0.30, "phase": "Sleeping Dead Zone", "advisory": "Chi phí bid rẻ nhưng tỷ lệ nạp tiền gần bằng 0"},
            {"hour": 3, "label": "03:00 - 04:00", "traffic": 10, "iap_intent": 5, "bid_mult": 0.30, "phase": "Sleeping Dead Zone", "advisory": "Khung giờ tĩnh, khuyến nghị pause campaign VO"},
            {"hour": 4, "label": "04:00 - 05:00", "traffic": 12, "iap_intent": 8, "bid_mult": 0.30, "phase": "Early Dawn", "advisory": "Chưa có lưu lượng người chơi trả tiền"},
            {"hour": 5, "label": "05:00 - 06:00", "traffic": 20, "iap_intent": 12, "bid_mult": 0.40, "phase": "Early Dawn", "advisory": "Bắt đầu có traffic lướt mạng xã hội"},
            {"hour": 6, "label": "06:00 - 07:00", "traffic": 40, "iap_intent": 25, "bid_mult": 0.70, "phase": "Morning Wakeup", "advisory": "Người chơi bắt đầu dậy, kiểm tra game"},
            {"hour": 7, "label": "07:00 - 08:00", "traffic": 65, "iap_intent": 35, "bid_mult": 0.85, "phase": "Morning Commute", "advisory": "Lưu lượng TikTok/Meta tăng vọt, thích hợp cho chiến dịch MAI"},
            {"hour": 8, "label": "08:00 - 09:00", "traffic": 55, "iap_intent": 30, "bid_mult": 0.80, "phase": "Work Start", "advisory": "Bắt đầu giờ làm việc/học tập, traffic chững lại"},
            {"hour": 9, "label": "09:00 - 10:00", "traffic": 50, "iap_intent": 32, "bid_mult": 0.80, "phase": "Mid-morning", "advisory": "Duy trì bid tiêu chuẩn"},
            {"hour": 10, "label": "10:00 - 11:00", "traffic": 55, "iap_intent": 40, "bid_mult": 0.90, "phase": "Mid-morning Break", "advisory": "Tăng nhẹ bid cho các gói nạp thẻ tháng"},
            {"hour": 11, "label": "11:00 - 12:00", "traffic": 75, "iap_intent": 60, "bid_mult": 1.15, "phase": "Lunch Rush Warmup", "advisory": "Chuẩn bị bước vào khung giờ vàng buổi trưa"},
            {"hour": 12, "label": "12:00 - 13:00", "traffic": 90, "iap_intent": 78, "bid_mult": 1.35, "phase": "Lunch Break Peak", "advisory": "Đỉnh điểm chơi game ngắn & xem Rewarded Video Ads"},
            {"hour": 13, "label": "13:00 - 14:00", "traffic": 70, "iap_intent": 55, "bid_mult": 1.05, "phase": "Post-Lunch Rest", "advisory": "Hạ dần bid về mức trung bình"},
            {"hour": 14, "label": "14:00 - 15:00", "traffic": 52, "iap_intent": 38, "bid_mult": 0.85, "phase": "Afternoon Work", "advisory": "Khung giờ tĩnh, kiểm tra kill-switch các ad set kém"},
            {"hour": 15, "label": "15:00 - 16:00", "traffic": 58, "iap_intent": 42, "bid_mult": 0.88, "phase": "Tea Break", "advisory": "Duy trì ổn định"},
            {"hour": 16, "label": "16:00 - 17:00", "traffic": 65, "iap_intent": 50, "bid_mult": 0.95, "phase": "Late Afternoon", "advisory": "Học sinh/sinh viên tan trường, traffic casual tăng"},
            {"hour": 17, "label": "17:00 - 18:00", "traffic": 78, "iap_intent": 62, "bid_mult": 1.10, "phase": "Evening Commute", "advisory": "Bắt đầu giai đoạn leo rank và hoàn thành daily quest"},
            {"hour": 18, "label": "18:00 - 19:00", "traffic": 85, "iap_intent": 75, "bid_mult": 1.25, "phase": "Dinner / Chill", "advisory": "Tăng tốc ngân sách cho các chiến dịch AEO & VO"},
            {"hour": 19, "label": "19:00 - 20:00", "traffic": 96, "iap_intent": 92, "bid_mult": 1.50, "phase": "Golden Whale Prime", "advisory": "GIỜ VÀNG CÁ VOI: Bơm 150% bid, tập trung nạp IAP"},
            {"hour": 20, "label": "20:00 - 21:00", "traffic": 100, "iap_intent": 100, "bid_mult": 1.65, "phase": "Peak Prime Time", "advisory": "ĐỈNH ĐIỂM DOANH THU TOÀN NGÀY: Khung giờ gacha & chiến bang hội"},
            {"hour": 21, "label": "21:00 - 22:00", "traffic": 95, "iap_intent": 95, "bid_mult": 1.55, "phase": "Peak Prime Time", "advisory": "Duy trì bid tối đa, thời điểm mua Battle Pass cao nhất"},
            {"hour": 22, "label": "22:00 - 23:00", "traffic": 80, "iap_intent": 75, "bid_mult": 1.25, "phase": "Late Night Gamers", "advisory": "Nhóm hardcore tiếp tục cày đêm, chuyển dần sang remarketing"},
            {"hour": 23, "label": "23:00 - 24:00", "traffic": 50, "iap_intent": 40, "bid_mult": 0.80, "phase": "Bedtime Cooldown", "advisory": "Hạ ngân sách chuẩn bị cho chu kỳ ngày hôm sau"}
        ]

        # Network Specific Mechanics & Ad Formats
        self.network_archetypes = {
            "tiktok": {
                "name": "TikTok Ads Manager",
                "core_objective": "Spark Ads + High-Velocity Creative Testing",
                "recommended_formats": ["Spark Ads (Ủy quyền kênh TikToker)", "Interactive Card Add-on", "Playable Endcards"],
                "pacing_algorithm": "Accelerated (Fast Burn) trong 3 giờ đầu, sau đó Standard",
                "best_optimization_goal": "AEO (In-App Purchase / Tutorial Complete)",
                "cpi_sensitivity": "Rất nhạy cảm với Creative Fatigue (quảng cáo tụt CVR sau 5-7 ngày)",
                "min_adset_budget_rule": "$50/ngày/ad set để hệ thống máy học vượt qua ngưỡng 50 conversions"
            },
            "meta": {
                "name": "Meta Ads (Facebook & Instagram)",
                "core_objective": "Advantage+ App Campaigns (A+AC) + Value Optimization (VO)",
                "recommended_formats": ["Video Reel 9:16", "Carousel Showcase nhân vật", "Static Endcard with High Contrast"],
                "pacing_algorithm": "Smoothed Daily Pacing với Bid Cap / Cost Cap",
                "best_optimization_goal": "VO (Target ROAS - Tối ưu người nạp nhiều)",
                "cpi_sensitivity": "Hệ thống AI phân phối cực kỳ thông minh vào nhóm tuổi 25-45 có thẻ visa/momo",
                "min_adset_budget_rule": "Ngân sách tối thiểu = 5x Target CPA sự kiện nạp tiền"
            },
            "unity_applovin": {
                "name": "Unity Ads / AppLovin MAX (In-App Ad Networks)",
                "core_objective": "Playable Ads + Rewarded Video Inventory",
                "recommended_formats": ["Full-Screen Rewarded Video 15-30s", "Playable HTML5 MRAID", "Interactive Endcard"],
                "pacing_algorithm": "Dynamic eCPM Waterflow & Real-time Bidding",
                "best_optimization_goal": "ROAS D7 Campaign",
                "cpi_sensitivity": "Ổn định cao, vòng đời creative có thể kéo dài 3-6 tuần",
                "min_adset_budget_rule": "Thử nghiệm theo Geo Tier (Tier 3 trước, Tier 1 sau)"
            }
        }

        # ROAS Automation Rules / Kill-Switch Protocols
        self.kill_switch_rules = [
            {
                "rule_id": "rule_no_install_morning",
                "name": "Morning Ghost Click Kill-Switch (11:00 AM Check)",
                "trigger_condition": "Chi tiêu > $25 VÀ Lượt Cài Đặt (Installs) = 0",
                "action": "TẮT AD SET NGAY LẬP TỨC",
                "severity": "CRITICAL",
                "logic": "Lỗi tracking Adjust/AppsFlyer hoặc Creative bị Click-bait ảo, không phát sinh người dùng thực."
            },
            {
                "rule_id": "rule_cpi_bleed_afternoon",
                "name": "CPI Bleed Protector (14:00 PM Check)",
                "trigger_condition": "CPI thực tế > 1.8x Target CPI VÀ Chi tiêu đạt > $50",
                "action": "GIẢM 40% NGÂN SÁCH HOẶC TẮT",
                "severity": "HIGH",
                "logic": "Ad set không tìm được tệp người dùng giá rẻ trong phiên trưa. Tránh đốt tiền vô ích vào buổi chiều."
            },
            {
                "rule_id": "rule_prime_time_scaler",
                "name": "Golden Hour ROAS Scale-Up (19:00 PM Check)",
                "trigger_condition": "D0 ROAS > 25% VÀ Tỷ lệ CVR > 3.5%",
                "action": "TĂNG NGÂN SÁCH THÊM +25%",
                "severity": "POSITIVE_SCALE",
                "logic": "Ad set đang hút đúng nhóm cá voi nạp tiền lúc bắt đầu giờ vàng. Tăng ngân sách 20-25% không làm reset learning phase."
            },
            {
                "rule_id": "rule_creative_fatigue_alert",
                "name": "Creative Fatigue Frequency Guard",
                "trigger_condition": "Frequency > 2.8 VÀ CTR giảm > 35% trong 3 ngày liên tục",
                "action": "THAY CREATIVE MỚI (CREATIVE REFRESH)",
                "severity": "WARNING",
                "logic": "Khán giả đã thấy video quảng cáo này quá nhiều lần. Cần bơm video hook mới từ Creative Spy."
            }
        ]

    def get_benchmarks(self) -> Dict[str, Any]:
        """Returns hourly dayparting profiles, network mechanics, and kill-switch rules."""
        return {
            "hourly_profile": self.hourly_behavior_profile,
            "networks": self.network_archetypes,
            "kill_switch_rules": self.kill_switch_rules
        }

    def optimize_campaign_pacing(
        self,
        daily_budget: float = 1000.0,
        network_id: str = "tiktok",
        optimization_goal: str = "aeo_purchase",
        target_cpi: float = 1.80,
        target_roas_d0: float = 20.0
    ) -> Dict[str, Any]:
        """Calculates precise hourly budget allocation, dayparting bids, and projected ROI curve."""
        network = self.network_archetypes.get(network_id, self.network_archetypes["tiktok"])

        # Calculate sum of bid multipliers to distribute budget proportionally
        total_mult = sum(h["bid_mult"] for h in self.hourly_behavior_profile)

        hourly_schedule = []
        allocated_sum = 0.0

        for h in self.hourly_behavior_profile:
            # Baseline proportional spend
            proportional_share = h["bid_mult"] / total_mult
            hour_budget = round(daily_budget * proportional_share, 2)
            allocated_sum += hour_budget

            # Estimated installs & payer acquisitions
            # Peak hours have higher conversion to paying users
            cpi_factor = target_cpi * (1.15 if h["bid_mult"] > 1.3 else (0.85 if h["bid_mult"] < 0.6 else 1.0))
            est_installs = max(1, int(hour_budget / max(0.1, cpi_factor)))
            
            # Paying conversion % based on IAP intent
            base_payer_rate = 0.045 if optimization_goal == "aeo_purchase" else (0.015 if optimization_goal == "mai_install" else 0.08)
            hour_payer_rate = base_payer_rate * (h["iap_intent"] / 50.0)
            est_payers = round(est_installs * hour_payer_rate, 1)

            # Revenue estimation for hour
            avg_order_val = 6.50
            est_revenue = round(est_payers * avg_order_val, 2)
            hour_roas = round((est_revenue / max(0.1, hour_budget)) * 100, 1)

            hourly_schedule.append({
                "hour": h["hour"],
                "time_slot": h["label"],
                "phase": h["phase"],
                "bid_multiplier": h["bid_mult"],
                "allocated_budget_usd": hour_budget,
                "pct_of_day_budget": round(proportional_share * 100, 1),
                "estimated_installs": est_installs,
                "estimated_paying_users": est_payers,
                "projected_revenue_usd": est_revenue,
                "projected_d0_roas_pct": hour_roas,
                "strategy_advisory": h["advisory"]
            })

        # Summary KPIs
        total_est_installs = sum(item["estimated_installs"] for item in hourly_schedule)
        total_est_revenue = round(sum(item["projected_revenue_usd"] for item in hourly_schedule), 2)
        total_est_payers = round(sum(item["estimated_paying_users"] for item in hourly_schedule), 1)
        blended_d0_roas = round((total_est_revenue / max(1.0, daily_budget)) * 100, 1)

        # Budget phase breakdown
        prime_time_budget = round(sum(h["allocated_budget_usd"] for h in hourly_schedule if h["hour"] in [19, 20, 21, 22]), 2)
        lunch_budget = round(sum(h["allocated_budget_usd"] for h in hourly_schedule if h["hour"] in [11, 12, 13]), 2)
        dead_zone_budget = round(sum(h["allocated_budget_usd"] for h in hourly_schedule if h["hour"] in [1, 2, 3, 4, 5]), 2)

        return {
            "campaign_inputs": {
                "daily_budget_usd": daily_budget,
                "network_name": network["name"],
                "network_id": network_id,
                "optimization_goal": optimization_goal,
                "target_cpi": target_cpi,
                "target_roas_d0": target_roas_d0
            },
            "pacing_summary": {
                "total_daily_budget_usd": daily_budget,
                "projected_daily_revenue_usd": total_est_revenue,
                "projected_blended_d0_roas": blended_d0_roas,
                "total_estimated_installs": total_est_installs,
                "total_estimated_paying_users": total_est_payers,
                "blended_effective_cpi": round(daily_budget / max(1, total_est_installs), 2)
            },
            "phase_distribution": {
                "golden_prime_hours_usd": prime_time_budget,
                "golden_prime_hours_pct": round((prime_time_budget / daily_budget) * 100, 1),
                "lunch_rush_usd": lunch_budget,
                "lunch_rush_pct": round((lunch_budget / daily_budget) * 100, 1),
                "dead_zone_saved_usd": dead_zone_budget,
                "dead_zone_pct": round((dead_zone_budget / daily_budget) * 100, 1)
            },
            "network_best_practices": {
                "core_objective": network["core_objective"],
                "pacing_rule": network["pacing_algorithm"],
                "recommended_formats": network["recommended_formats"],
                "min_budget_rule": network["min_adset_budget_rule"]
            },
            "hourly_schedule": hourly_schedule,
            "automated_rules": self.kill_switch_rules
        }
