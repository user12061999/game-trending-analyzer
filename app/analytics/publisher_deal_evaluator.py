"""Global Publisher Pitch Scorecard & Deal Evaluator.

Evaluates game metrics against Tier 1 & Tier 2 global publisher benchmarks,
calculates contract publishing deal financial splits, and determines self-publishing readiness.
"""

from typing import Dict, Any, List, Optional

class PublisherDealEvaluator:
    """Publishing readiness evaluator and deal economics simulator."""

    def __init__(self):
        # Global Publisher Benchmark Standards
        self.publisher_archetypes = [
            {
                "id": "tier1_hyper_hybrid",
                "tier": "Tier 1 Hyper/Hybrid Casual",
                "examples": ["Voodoo", "SayGames", "Kwalee", "Lion Studios"],
                "target_genre": "Hyper-Casual / Arcade Idle",
                "req_d1_retention": 45.0,
                "req_d7_retention": 18.0,
                "max_cpi_us": 0.55,
                "min_playtime_minutes": 25,
                "typical_revshare_studio": 50.0,  # 50% after UA deduction
                "typical_mg_usd": 15000,
                "notes": "Đòi hỏi D1 cực cao (>45%) và CPI US phải dưới $0.55. Publisher tài trợ 100% ngân sách UA."
            },
            {
                "id": "tier1_midcore_roguelike",
                "tier": "Tier 1 Mid-Core & Roguelike",
                "examples": ["Habby (Archero/Survivor.io)", "Miniclip", "Playgendary"],
                "target_genre": "Action Roguelike / Hybrid-Midcore",
                "req_d1_retention": 42.0,
                "req_d7_retention": 16.0,
                "max_cpi_us": 1.20,
                "min_playtime_minutes": 35,
                "typical_revshare_studio": 40.0,
                "typical_mg_usd": 50000,
                "notes": "Đặc biệt chú trọng D30 (>7%) và chiều sâu IAP. Khả năng scale doanh thu lên $10M+/tháng nếu pass prototype test."
            },
            {
                "id": "tier1_hardcore_rpg",
                "tier": "Tier 1 RPG & Strategy",
                "examples": ["Netmarble", "Garena", "Level Infinite", "Com2uS"],
                "target_genre": "Action RPG / 4X / Turn-Based",
                "req_d1_retention": 38.0,
                "req_d7_retention": 15.0,
                "max_cpi_us": 4.50,
                "min_playtime_minutes": 45,
                "typical_revshare_studio": 30.0,
                "typical_mg_usd": 150000,
                "notes": "Đòi hỏi đồ họa cao, cộng đồng bang hội mạnh. Publisher đầu tư mạnh vào marketing thương hiệu và influencer."
            }
        ]

    def evaluate_game_readiness(
        self,
        d1_retention: float = 40.0,
        d7_retention: float = 15.0,
        tested_cpi_us: float = 0.85,
        avg_playtime_mins: int = 28,
        game_genre: str = "Hybrid-Casual"
    ) -> Dict[str, Any]:
        """Calculates scorecard and readiness grade against publisher benchmarks."""
        evaluations = []

        for pub in self.publisher_archetypes:
            # Score D1
            d1_score = min(100, (d1_retention / pub["req_d1_retention"]) * 100)
            # Score D7
            d7_score = min(100, (d7_retention / pub["req_d7_retention"]) * 100)
            # Score CPI (lower is better)
            cpi_score = min(100, (pub["max_cpi_us"] / max(0.1, tested_cpi_us)) * 100)
            # Score Playtime
            play_score = min(100, (avg_playtime_mins / pub["min_playtime_minutes"]) * 100)

            total_weighted_score = round(d1_score * 0.35 + d7_score * 0.25 + cpi_score * 0.25 + play_score * 0.15, 1)

            if total_weighted_score >= 95:
                readiness_grade = "Sẵn Sàng Ký Hợp Đồng (Ready to Sign)"
                badge = "emerald"
            elif total_weighted_score >= 80:
                readiness_grade = "Tiềm Năng Cao (Needs Minor Polish)"
                badge = "indigo"
            elif total_weighted_score >= 65:
                readiness_grade = "Cần Tối Ưu Thêm (Prototype Stage)"
                badge = "amber"
            else:
                readiness_grade = "Chưa Đạt Chuẩn (Underperforming)"
                badge = "rose"

            evaluations.append({
                "publisher_archetype": pub["tier"],
                "examples": pub["examples"],
                "target_genre": pub["target_genre"],
                "weighted_score": total_weighted_score,
                "readiness_grade": readiness_grade,
                "badge_color": badge,
                "benchmark_comparison": {
                    "d1": {"actual": d1_retention, "target": pub["req_d1_retention"], "passed": d1_retention >= pub["req_d1_retention"]},
                    "d7": {"actual": d7_retention, "target": pub["req_d7_retention"], "passed": d7_retention >= pub["req_d7_retention"]},
                    "cpi": {"actual": tested_cpi_us, "target": pub["max_cpi_us"], "passed": tested_cpi_us <= pub["max_cpi_us"]},
                    "playtime": {"actual": avg_playtime_mins, "target": pub["min_playtime_minutes"], "passed": avg_playtime_mins >= pub["min_playtime_minutes"]}
                },
                "deal_terms_preview": {
                    "revshare": f"{pub['typical_revshare_studio']}% Studio / {100 - pub['typical_revshare_studio']}% Publisher",
                    "minimum_guarantee": f"${pub['typical_mg_usd']:,}",
                    "advisory": pub["notes"]
                }
            })

        # Overall verdict
        top_match = max(evaluations, key=lambda x: x["weighted_score"])
        if top_match["weighted_score"] >= 85:
            strategic_verdict = f"Game của bạn có chỉ số xuất sắc, đặc biệt phù hợp để gửi pitch deck tới các đối tác thuộc nhóm {top_match['publisher_archetype']} ({', '.join(top_match['examples'])})."
        else:
            strategic_verdict = "Chỉ số hiện tại nên tập trung tối ưu thêm D1/D7 qua ASO và onboarding tutorial trước khi gửi bản build cho Publisher để không bị mất lợi thế thương lượng."

        return {
            "evaluations": evaluations,
            "strategic_verdict": strategic_verdict,
            "top_match": top_match
        }

    def simulate_publishing_deal_cashflow(
        self,
        projected_gross_revenue: float = 500000.0,
        ua_marketing_budget: float = 300000.0,
        studio_revshare_pct: float = 40.0,
        minimum_guarantee: float = 50000.0,
        store_fee_pct: float = 30.0
    ) -> Dict[str, Any]:
        """Simulates net studio earnings under standard post-UA recoupment publishing contract."""
        net_after_store = projected_gross_revenue * (1.0 - (store_fee_pct / 100.0))
        net_profit_pool = max(0.0, net_after_store - ua_marketing_budget)

        # Standard post-UA revshare
        studio_share_from_pool = net_profit_pool * (studio_revshare_pct / 100.0)
        # Studio gets at least Minimum Guarantee (MG acts as advance)
        actual_studio_earnings = max(minimum_guarantee, studio_share_from_pool)
        publisher_net = max(0.0, net_after_store - actual_studio_earnings - ua_marketing_budget)

        # Comparison with Self-Publishing (Studio pays own UA)
        self_publish_net = max(0.0, net_after_store - ua_marketing_budget)

        return {
            "financial_breakdown": {
                "projected_gross_usd": projected_gross_revenue,
                "app_store_fee_usd": round(projected_gross_revenue * 0.30, 2),
                "ua_ad_spend_usd": ua_marketing_budget,
                "net_profit_pool_usd": round(net_profit_pool, 2),
                "studio_net_earnings_usd": round(actual_studio_earnings, 2),
                "publisher_net_profit_usd": round(publisher_net, 2),
                "minimum_guarantee_paid_usd": minimum_guarantee
            },
            "deal_comparison": {
                "publishing_route_studio_gain": round(actual_studio_earnings, 2),
                "self_publishing_studio_gain": round(self_publish_net, 2),
                "risk_profile": "Publisher chịu 100% rủi ro tiền ad spend UA. Nếu game flop, Studio vẫn giữ nguyên tiền Minimum Guarantee ($" + f"{minimum_guarantee:,})."
            }
        }
