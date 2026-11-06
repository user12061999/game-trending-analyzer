"""Game Feature RICE Scorer & Production Roadmap Planner.

Prioritizes mobile game roadmap backlog using the industry standard RICE framework:
RICE Score = (Reach * Impact * Confidence) / Effort.
Provides 10 classic mobile liveops feature presets, ROI / Retention lift projections,
and automated sprint Gantt roadmap scheduling.
"""

from typing import Dict, Any, List, Optional
import math

class FeatureRICEScorer:
    """Evaluates game feature priorities and plans production sprints."""

    # 10 Classic mobile game feature presets
    DEFAULT_PRESETS = [
        {
            "id": "first_recharge",
            "name": "Gói Nạp Lần Đầu $0.99 Kèm Tướng SSR (First Recharge Bait)",
            "category": "Monetization",
            "reach": 85000,
            "impact": 3.0,       # 3.0 = Massive
            "confidence": 0.95,   # 95%
            "effort": 1.5,        # 1.5 person-weeks
            "description": "Trigger pop-up sau khi hoàn thành Tutorial, bán gói $0.99 kèm vũ khí tím và nhân vật SSR để phá vỡ rào cản chi tiêu lần đầu (Zero-to-One spender conversion).",
            "expected_kpi": "Tăng tỷ lệ Spender Conversion từ 1.8% lên 4.5%."
        },
        {
            "id": "piggy_bank",
            "name": "Heo Đất Tích Lũy Kim Cương (Piggy Bank IAP Vault)",
            "category": "Monetization",
            "reach": 70000,
            "impact": 2.5,
            "confidence": 0.90,
            "effort": 2.0,
            "description": "Mỗi trận thắng tích lũy kim cương vào heo đất. Khi heo đầy (500 gem), người chơi có thể đập heo chỉ với $1.99 (giảm 70% so với giá shop thường). Khai thác tâm lý sợ mất mát (loss aversion).",
            "expected_kpi": "Tăng ARPPU thêm 22%, tăng tần suất mở app mỗi ngày."
        },
        {
            "id": "offline_idle_rewards",
            "name": "Rương Treo Máy Tích Lũy Offline 24h (AFK Patrol Chest)",
            "category": "Retention",
            "reach": 95000,
            "impact": 2.0,
            "confidence": 0.90,
            "effort": 2.0,
            "description": "Người chơi offline vẫn tự động thu thập exp, vàng và trang bị cơ bản trong tối đa 12-24 giờ. Đăng nhập lại nhận ngay một chạm kèm tùy chọn xem rewarded ad x2 phần thưởng.",
            "expected_kpi": "Tăng D1 Retention +5.2%, D7 Retention +3.8%."
        },
        {
            "id": "battle_pass_season",
            "name": "Battle Pass Mùa Giải Mới (30-Day Seasonal Battle Pass)",
            "category": "Monetization & Retention",
            "reach": 80000,
            "impact": 2.5,
            "confidence": 0.85,
            "effort": 3.5,
            "description": "Hệ thống 50 cấp độ phần thưởng: Cột Free cho đại chúng và Cột Premium ($9.99) cho người nạp kèm skin độc quyền cuối mùa.",
            "expected_kpi": "Tăng Recurring Monthly Revenue +28%, kéo dài Session Duration."
        },
        {
            "id": "vip_subscription",
            "name": "Thẻ Tháng VIP Tích Hợp Tắt Quảng Cáo (VIP Monthly Privilege)",
            "category": "Monetization",
            "reach": 60000,
            "impact": 2.0,
            "confidence": 0.85,
            "effort": 2.0,
            "description": "Giá $4.99/tháng: Nhận 100 kim cương mỗi ngày, tắt banner quảng cáo xen kẽ, tăng 20% tốc độ di chuyển hoặc càn quét ải tức thì.",
            "expected_kpi": "Tạo dòng doanh thu định kỳ ổn định, tăng LTV D60 lên 30%."
        },
        {
            "id": "clan_guild_war",
            "name": "Bang Hội Chiến Liên Server (Cross-Server Guild GvG War)",
            "category": "Social & Engagement",
            "reach": 50000,
            "impact": 3.0,
            "confidence": 0.80,
            "effort": 6.0,
            "description": "Hệ thống chiến tranh lãnh địa vào tối Thứ Bảy hàng tuần. Thành viên bang phối hợp phòng thủ và tấn công thành lũy đối phương để nhận danh hiệu và buff toàn server.",
            "expected_kpi": "Tăng D30 Retention +6.5%, kích thích Whales đua top lực chiến."
        },
        {
            "id": "guild_boss_raid",
            "name": "Săn Boss Bang Hội Hàng Ngày (Co-op Daily Guild Boss)",
            "category": "Social & Retention",
            "reach": 55000,
            "impact": 1.8,
            "confidence": 0.85,
            "effort": 3.0,
            "description": "Mỗi ngày thành viên có 3 lượt đánh Boss tích điểm sát thương chung. Đạt mốc sát thương toàn bang nhận rương báu.",
            "expected_kpi": "Tăng DAU Stickiness (DAU/MAU) thêm 4%, tăng tương tác chat bang."
        },
        {
            "id": "pet_companion_system",
            "name": "Hệ Thống Thú Cưng Đồng Hành (Pet Breeding & Synergy)",
            "category": "Engagement & Gacha",
            "reach": 65000,
            "impact": 2.0,
            "confidence": 0.75,
            "effort": 4.5,
            "description": "Thú cưng đi theo hỗ trợ nhặt đồ, tăng chỉ số và kỹ năng chủ động riêng. Gacha trứng thú cưng và hệ thống ấp trứng tiến hóa 3 bậc.",
            "expected_kpi": "Mở rộng chiều sâu gameplay (meta progression), tăng spending sinks."
        },
        {
            "id": "skin_gacha_wardrobe",
            "name": "Tủ Đồ Thời Trang & Vòng Quay Ngoại Trang (Skin Gacha Wardrobe)",
            "category": "Monetization",
            "reach": 75000,
            "impact": 2.2,
            "confidence": 0.80,
            "effort": 3.5,
            "description": "Hệ thống trang phục đổi diện mạo kỹ năng, hiệu ứng biến về đặc biệt. Không ảnh hưởng cân bằng pay-to-win nhưng cực hấp dẫn với tệp casual/anime.",
            "expected_kpi": "Tăng IAP từ tệp Dolphin và Whales không thích mua sức mạnh thuần."
        },
        {
            "id": "roguelike_side_mode",
            "name": "Chế Độ Phụ Roguelike Vô Hạn (Infinite Roguelike Tower)",
            "category": "Engagement",
            "reach": 40000,
            "impact": 1.8,
            "confidence": 0.70,
            "effort": 5.0,
            "description": "Tháp vô tận tạo ngẫu nhiên bản đồ và quái vật mỗi tuần. Người chơi chọn 1 trong 3 kỹ năng sau mỗi tầng, không tiêu hao thể lực chính.",
            "expected_kpi": "Cứu vãn churn cho tệp End-game players đã hết nhiệm vụ chính."
        }
    ]

    def get_presets(self) -> List[Dict[str, Any]]:
        """Returns the benchmark preset features list."""
        return self.DEFAULT_PRESETS

    def evaluate_features(self, features: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculates RICE scores, projected ROI / Retention impact, and assigns sprint quarters."""
        input_list = features if features and len(features) > 0 else self.DEFAULT_PRESETS

        scored_features = []
        for feat in input_list:
            reach = float(feat.get("reach", 10000))
            impact = float(feat.get("impact", 1.0))
            confidence = float(feat.get("confidence", 0.8))
            effort = float(feat.get("effort", 2.0))
            if effort <= 0:
                effort = 0.5

            # RICE Formula
            raw_rice = (reach * impact * confidence) / effort
            normalized_rice = round(raw_rice / 1000.0, 1)

            # Impact Projections
            category = feat.get("category", "Monetization")
            projected_rev_lift_pct = 0.0
            projected_retention_lift_pct = 0.0

            if "Monetization" in category:
                projected_rev_lift_pct = round(impact * 4.5 * (confidence / 0.8), 1)
                projected_retention_lift_pct = round(impact * 0.8 * (reach / 70000.0), 1)
            elif "Retention" in category:
                projected_rev_lift_pct = round(impact * 2.0, 1)
                projected_retention_lift_pct = round(impact * 2.4 * (confidence / 0.8), 1)
            elif "Social" in category or "Engagement" in category:
                projected_rev_lift_pct = round(impact * 2.8, 1)
                projected_retention_lift_pct = round(impact * 2.0 * (confidence / 0.8), 1)
            else:
                projected_rev_lift_pct = round(impact * 2.0, 1)
                projected_retention_lift_pct = round(impact * 1.5, 1)

            scored_features.append({
                "id": feat.get("id", f"feat_{len(scored_features)}"),
                "name": feat.get("name", "Unnamed Feature"),
                "category": category,
                "reach": int(reach),
                "impact": impact,
                "confidence": confidence,
                "effort": effort,
                "description": feat.get("description", ""),
                "expected_kpi": feat.get("expected_kpi", ""),
                "rice_score": normalized_rice,
                "projected_revenue_lift_pct": projected_rev_lift_pct,
                "projected_d30_retention_lift_pct": projected_retention_lift_pct
            })

        # Sort descending by RICE Score
        scored_features.sort(key=lambda x: x["rice_score"], reverse=True)

        # Distribute into 6 Sprints (Quarterly Roadmap: 2 weeks per sprint, 12 weeks total)
        # Capacity per sprint ~ 4 to 6 person-weeks
        sprint_buckets = {
            "Sprint 1 (Tuần 1-2: Quick-Wins & High RICE)": [],
            "Sprint 2 (Tuần 3-4: Core Conversion & Hook)": [],
            "Sprint 3 (Tuần 5-6: Economy & Retention Loops)": [],
            "Sprint 4 (Tuần 7-8: Social & Guild Mechanics)": [],
            "Sprint 5 (Tuần 9-10: Deep Progression Systems)": [],
            "Sprint 6 (Tuần 11-12: End-Game & Polish)": []
        }
        sprint_keys = list(sprint_buckets.keys())

        # Distribute based on priority and effort
        current_sprint_idx = 0
        current_sprint_effort = 0.0
        max_effort_per_sprint = 4.5

        for rank, item in enumerate(scored_features):
            effort = item["effort"]
            # If current sprint is overloaded, move to next sprint unless already at last
            if current_sprint_effort + effort > max_effort_per_sprint and current_sprint_idx < len(sprint_keys) - 1:
                current_sprint_idx += 1
                current_sprint_effort = 0.0

            item["priority_tier"] = "P0 - Critical Quick-Win" if rank < 3 else ("P1 - High Value" if rank < 6 else "P2 - Strategic Expansion")
            item["assigned_sprint"] = sprint_keys[current_sprint_idx]
            sprint_buckets[sprint_keys[current_sprint_idx]].append(item)
            current_sprint_effort += effort

        # Calculate portfolio totals
        total_effort = sum(f["effort"] for f in scored_features)
        total_potential_rev_lift = min(150.0, sum(f["projected_revenue_lift_pct"] for f in scored_features[:5]))
        total_potential_d30_lift = min(25.0, sum(f["projected_d30_retention_lift_pct"] for f in scored_features[:5]))

        return {
            "summary": {
                "total_features_evaluated": len(scored_features),
                "total_engineering_weeks": round(total_effort, 1),
                "cumulative_top5_rev_lift_pct": round(total_potential_rev_lift, 1),
                "cumulative_top5_d30_lift_pct": round(total_potential_d30_lift, 1),
                "highest_roi_feature": scored_features[0]["name"] if scored_features else "None"
            },
            "ranked_features": scored_features,
            "quarterly_roadmap": sprint_buckets
        }
