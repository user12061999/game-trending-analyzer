"""TikTok Creator & Organic K-Factor Viral Forecaster.

Calculates mathematical viral coefficient (K-Factor = i * c), simulates organic viral loops,
and projects Micro-Creator TikTok/YouTube Shorts campaign ROI and blended CPI reduction.
"""

from typing import Dict, Any, List, Optional
import math

class ViralKFactorForecaster:
    """Viral coefficient modeling & TikTok UGC campaign ROI forecasting engine."""

    def __init__(self):
        pass

    def calculate_k_factor_loop(
        self,
        paid_installs: int = 10000,
        paid_cpi: float = 2.00,
        invites_per_user: float = 2.5,
        invitee_conversion_rate: float = 0.24,
        simulation_cycles: int = 5
    ) -> Dict[str, Any]:
        """Calculates viral K-Factor and models total user acquisition with viral expansion."""
        k_factor = round(invites_per_user * invitee_conversion_rate, 3)

        # Classification
        if k_factor >= 1.0:
            classification = "BÙNG NỔ VIRAL TỰ NHIÊN (Exponential Viral Loop)"
            badge_color = "emerald"
            verdict = "Game đạt ngưỡng tự sinh trưởng không giới hạn! Mỗi người chơi kéo theo hơn 1 người chơi mới."
        elif k_factor >= 0.6:
            classification = "KHUẾCH ĐẠI TỰ NHIÊN MẠNH (Strong Organic Amplifier)"
            badge_color = "indigo"
            verdict = "Hệ thống lan truyền xuất sắc, giúp giảm một nửa gánh nặng ngân sách quảng cáo trả phí (UA)."
        elif k_factor >= 0.3:
            classification = "LAN TRUYỀN VỪA PHẢI (Moderate Virality)"
            badge_color = "amber"
            verdict = "Có hiệu ứng chia sẻ nhưng chủ yếu vẫn phụ thuộc vào nguồn tiền mua quảng cáo paid ads."
        else:
            classification = "LAN TRUYỀN THẤP (Low Virality)"
            badge_color = "rose"
            verdict = "Người chơi ít có động lực chia sẻ game với bạn bè. Cần bổ sung cơ chế quà mời bạn (Referral bonus) hoặc Guild."

        # Model cycles
        cycles_data = []
        current_cohort = paid_installs
        total_users = paid_installs

        for cycle in range(1, simulation_cycles + 1):
            organic_new = int(current_cohort * k_factor)
            total_users += organic_new
            cycles_data.append({
                "cycle": cycle,
                "incoming_viral_users": organic_new,
                "cumulative_total_users": total_users
            })
            current_cohort = organic_new
            if organic_new == 0:
                break

        total_paid_spend = paid_installs * paid_cpi
        blended_cpi = round(total_paid_spend / max(1, total_users), 2)
        cpi_savings_pct = round(((paid_cpi - blended_cpi) / paid_cpi) * 100, 1)

        return {
            "k_factor_metrics": {
                "k_factor_value": k_factor,
                "invites_per_user": invites_per_user,
                "conversion_rate_pct": round(invitee_conversion_rate * 100, 1),
                "classification": classification,
                "badge_color": badge_color,
                "verdict": verdict
            },
            "acquisition_impact": {
                "initial_paid_installs": paid_installs,
                "organic_viral_installs_gained": total_users - paid_installs,
                "total_users_acquired": total_users,
                "initial_paid_cpi_usd": paid_cpi,
                "blended_cpi_usd": blended_cpi,
                "cpi_reduction_pct": cpi_savings_pct,
                "total_marketing_spend_usd": total_paid_spend
            },
            "cycles_progression": cycles_data
        }

    def forecast_tiktok_creator_campaign(
        self,
        creator_budget_usd: float = 5000.0,
        creator_count: int = 25,
        avg_views_per_creator: int = 40000,
        target_network: str = "TikTok"
    ) -> Dict[str, Any]:
        """Projects ROI and organic store search lift from a TikTok/Shorts Micro-Creator campaign."""
        total_views = creator_count * avg_views_per_creator
        cpm_effective = round((creator_budget_usd / max(1, total_views)) * 1000.0, 2)

        # Typical CTR on TikTok bio link / sound page is 1.5%
        bio_clicks = int(total_views * 0.015)
        # Store conversion on click is ~22%
        direct_installs = int(bio_clicks * 0.22)

        # Organic Store Search Lift (people who see video and search game title directly on App Store)
        # Typically 1.8x - 2.5x of direct bio installs
        organic_search_lift = int(direct_installs * 2.2)
        total_campaign_installs = direct_installs + organic_search_lift

        effective_cpi_ugc = round(creator_budget_usd / max(1, total_campaign_installs), 2)

        return {
            "campaign_inputs": {
                "budget_usd": creator_budget_usd,
                "creator_count": creator_count,
                "avg_views_per_creator": avg_views_per_creator,
                "target_network": target_network
            },
            "performance_forecast": {
                "total_projected_views": total_views,
                "effective_cpm_usd": cpm_effective,
                "direct_bio_installs": direct_installs,
                "organic_search_lift_installs": organic_search_lift,
                "total_campaign_installs": total_campaign_installs,
                "effective_cpi_usd": effective_cpi_ugc
            },
            "strategic_takeaway": (
                f"Với ngân sách ${creator_budget_usd:,} tài trợ cho {creator_count} creator, chiến dịch dự kiến tạo ra {total_views:,} lượt xem "
                f"và mang về {total_campaign_installs:,} lượt cài đặt chất lượng cao (CPI thực tế ~${effective_cpi_ugc}). "
                "Lưu lượng người chơi đến từ Creator có retention D7 cao hơn 25% so với quảng cáo banner truyền thống."
            )
        }
