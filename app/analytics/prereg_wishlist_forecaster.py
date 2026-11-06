"""Steam Wishlist & Mobile Pre-Registration Velocity Forecaster.

Models wishlist accumulation velocity, Steam Next Fest demo conversion lifts,
and projects Day 1 - Day 7 launch revenue, peak concurrent players (CCU), and Year 1 sales.
"""

from typing import Dict, Any, List, Optional
import math

class PreRegWishlistForecaster:
    """Forecasting engine for Steam Wishlists and Mobile Pre-Registrations."""

    BENCHMARK_PRESETS = [
        {
            "id": "steam_indie_breakout",
            "platform": "Steam",
            "name": "Steam Indie Action Breakout (Hades / Dead Cells Tier)",
            "current_wishlists": 65000,
            "days_to_launch": 45,
            "retail_price_usd": 19.99,
            "next_fest_demo_downloads": 18000,
            "expected_review_score_pct": 92.0,
            "description": "Game Indie đồ họa pixel/2.5D độc đáo, có demo tham gia Steam Next Fest và nhận phản hồi tích cực từ streamer."
        },
        {
            "id": "steam_solo_dev_niche",
            "platform": "Steam",
            "name": "Steam Solo Developer Niche (Thẻ Bài / Xây Dựng)",
            "current_wishlists": 14000,
            "days_to_launch": 30,
            "retail_price_usd": 12.99,
            "next_fest_demo_downloads": 4000,
            "expected_review_score_pct": 84.0,
            "description": "Dự án quy mô nhỏ, tập trung vào gameplay chiến thuật chiều sâu, tệp fan trung thành nhưng thiếu ngân sách marketing lớn."
        },
        {
            "id": "mobile_midcore_rpg",
            "platform": "Mobile",
            "name": "Mobile Mid-Core Gacha RPG (Quy Mô Vừa - Lớn)",
            "current_prereg": 420000,
            "days_to_launch": 20,
            "projected_d1_retention": 44.0,
            "projected_d30_ltv_usd": 3.40,
            "description": "Chiến dịch đặt trước trên App Store & Google Play kéo dài 2 tháng kèm quà tặng mốc 100k, 300k, 500k lượt đăng ký."
        },
        {
            "id": "mobile_casual_puzzle",
            "platform": "Mobile",
            "name": "Mobile Casual Puzzle / Runner (Tập Trung Ad & IAP Nhẹ)",
            "current_prereg": 95000,
            "days_to_launch": 15,
            "projected_d1_retention": 38.0,
            "projected_d30_ltv_usd": 0.85,
            "description": "Tựa game casual giải đố dễ tiếp cận, organic store impression chiếm 60% tổng lượng đăng ký."
        }
    ]

    def get_presets(self) -> List[Dict[str, Any]]:
        """Returns benchmark presets for quick simulation."""
        return self.BENCHMARK_PRESETS

    def forecast_steam_launch(
        self,
        current_wishlists: int = 50000,
        days_to_launch: int = 30,
        retail_price_usd: float = 19.99,
        next_fest_demo_downloads: int = 10000,
        expected_review_score_pct: float = 88.0
    ) -> Dict[str, Any]:
        """Calculates Steam launch velocity, conversion, and revenue projections."""
        if current_wishlists <= 0:
            current_wishlists = 1000
        if retail_price_usd <= 0:
            retail_price_usd = 9.99

        # 1. Next Fest demo to wishlist lift (industry avg 28% - 42% demo players wishlist)
        next_fest_wishlist_gain = int(next_fest_demo_downloads * 0.35)

        # 2. Organic acceleration velocity leading up to launch (exponential curve)
        # Typically adds 8% to 18% in the final 30 days
        velocity_gain = int(current_wishlists * min(0.35, (days_to_launch / 30.0) * 0.14))
        projected_wishlists_at_launch = current_wishlists + next_fest_wishlist_gain + velocity_gain

        # 3. Wishlist-to-Sales Multiplier on Week 1 based on Review Sentiment
        # Positive review sentiment strongly impacts algorithm recommendation (More Like This & Discover Queue)
        if expected_review_score_pct >= 90.0:
            w1_multiplier = 0.38   # High conversion (Overwhelmingly Positive)
            y1_multiplier = 4.8
            tier_badge = "TIER S (Siêu Phẩm Tiềm Năng)"
            algorithm_status = "Được Steam thuật toán đẩy Discover Queue & Top New Releases tối đa"
        elif expected_review_score_pct >= 80.0:
            w1_multiplier = 0.28   # Solid conversion (Very Positive)
            y1_multiplier = 3.8
            tier_badge = "TIER A (Thành Công Thương Mại)"
            algorithm_status = "Được đẩy vào trang chủ mục New & Trending trong 48 giờ đầu"
        elif expected_review_score_pct >= 70.0:
            w1_multiplier = 0.18   # Average (Mostly Positive)
            y1_multiplier = 2.8
            tier_badge = "TIER B (Phân Khúc Ngách An Toàn)"
            algorithm_status = "Phụ thuộc chủ yếu vào traffic tự thân của cộng đồng và streamer"
        else:
            w1_multiplier = 0.10   # Low (Mixed reviews)
            y1_multiplier = 1.8
            tier_badge = "TIER C (Rủi Ro Hoàn Tiền Cao)"
            algorithm_status = "Nguy cơ tụt khỏi bảng xếp hạng sau 24 giờ do tỷ lệ Refund cao"

        # 4. Units & Financials
        w1_units_sold = int(projected_wishlists_at_launch * w1_multiplier)
        y1_units_sold = int(w1_units_sold * y1_multiplier)

        w1_gross_rev = round(w1_units_sold * retail_price_usd, 2)
        w1_net_rev = round(w1_gross_rev * 0.70, 2) # Steam 30% platform cut

        y1_gross_rev = round(y1_units_sold * retail_price_usd, 2)
        y1_net_rev = round(y1_gross_rev * 0.70, 2)

        # 5. Day 1 Peak CCU estimation (formula: ~15% to 22% of Day 1 buyers play concurrently)
        day1_buyers = int(w1_units_sold * 0.42)
        day1_peak_ccu = max(10, int((day1_buyers * 0.20) / 1.0))

        return {
            "platform": "Steam",
            "inputs": {
                "current_wishlists": current_wishlists,
                "days_to_launch": days_to_launch,
                "retail_price_usd": retail_price_usd,
                "next_fest_demo_downloads": next_fest_demo_downloads,
                "expected_review_score_pct": expected_review_score_pct
            },
            "wishlist_growth": {
                "base_wishlists": current_wishlists,
                "next_fest_lift": next_fest_wishlist_gain,
                "velocity_boost": velocity_gain,
                "total_launch_wishlists": projected_wishlists_at_launch,
                "tier_classification": tier_badge,
                "algorithm_recommendation": algorithm_status
            },
            "sales_projections": {
                "week_1_units": w1_units_sold,
                "week_1_gross_usd": w1_gross_rev,
                "week_1_net_steam_usd": w1_net_rev,
                "year_1_units": y1_units_sold,
                "year_1_gross_usd": y1_gross_rev,
                "year_1_net_steam_usd": y1_net_rev,
                "day_1_peak_ccu": day1_peak_ccu
            },
            "strategic_advice": (
                "🎯 Hãy gửi Key Review cho ít nhất 50 streamer/content creator trước ngày ra mắt 7 ngày. "
                "Nếu đạt trên 50,000 Wishlist, game sẽ được Steam xếp vào tab 'Popular Upcoming', "
                "tạo cú hích đẩy thẳng vào Top 10 Global Top Sellers ngay trong đêm ra mắt!"
            )
        }

    def forecast_mobile_prereg(
        self,
        current_prereg: int = 250000,
        days_to_launch: int = 25,
        projected_d1_retention: float = 40.0,
        projected_d30_ltv_usd: float = 2.50
    ) -> Dict[str, Any]:
        """Calculates Mobile Pre-registration auto-install velocity and Day 1 - Day 30 revenue."""
        if current_prereg <= 0:
            current_prereg = 5000
        if projected_d30_ltv_usd <= 0:
            projected_d30_ltv_usd = 1.0

        # Organic velocity gain leading up to release
        organic_boost = int(current_prereg * min(0.40, (days_to_launch / 30.0) * 0.18))
        total_prereg_at_launch = current_prereg + organic_boost

        # Store auto-install conversion rate (Apple & Google auto-download on WiFi: ~32% - 40%)
        d1_auto_installs = int(total_prereg_at_launch * 0.36)

        # Store featuring & Chart climbing organic multiplier (Top 5 Free chart lift)
        chart_multiplier = 1.65 if total_prereg_at_launch > 200000 else 1.25
        m1_total_installs = int(d1_auto_installs * chart_multiplier * 2.8)

        # Revenue Projections
        d1_active_users = int(d1_auto_installs * (projected_d1_retention / 100.0))
        m1_projected_revenue_usd = round(m1_total_installs * projected_d30_ltv_usd, 2)
        net_store_revenue_usd = round(m1_projected_revenue_usd * 0.70, 2) # After 30% store commission

        status_tier = (
            "🚀 SIÊU TỰA GAME TOP CHART (Khả năng leo Top 1 Free)" if total_prereg_at_launch >= 300000
            else ("⭐ TỰA GAME TIỀM NĂNG CAO (Lọt Top 10 Game Mới)" if total_prereg_at_launch >= 100000
            else "📦 PHÁT HÀNH TIÊU CHUẨN (Cần đẩy mạnh UA trả phí)")
        )

        return {
            "platform": "Mobile",
            "inputs": {
                "current_prereg": current_prereg,
                "days_to_launch": days_to_launch,
                "projected_d1_retention": projected_d1_retention,
                "projected_d30_ltv_usd": projected_d30_ltv_usd
            },
            "prereg_growth": {
                "base_prereg": current_prereg,
                "velocity_boost": organic_boost,
                "total_launch_prereg": total_prereg_at_launch,
                "tier_classification": status_tier
            },
            "install_and_revenue": {
                "day_1_auto_installs": d1_auto_installs,
                "day_1_active_users_d1": d1_active_users,
                "month_1_total_installs": m1_total_installs,
                "month_1_gross_revenue_usd": m1_projected_revenue_usd,
                "month_1_net_revenue_usd": net_store_revenue_usd
            },
            "strategic_advice": (
                "📱 Ngày đầu tiên phát hành (Day 1) là thời điểm vàng để mua thêm 30% Paid UA nhằm cộng hưởng "
                "với lượng tải tự động từ Pre-registration. Cú hích kép này sẽ đẩy game lọt Top 1 Bảng Xếp Hạng Miễn Phí, "
                "mang về thêm 40% - 60% lượt tải hoàn toàn miễn phí từ Organic Discovery!"
            )
        }
