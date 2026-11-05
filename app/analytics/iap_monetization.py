"""IAP Monetization & Battle Pass Pricing Benchmarking Engine.

Provides price ladder standards by genre, global Purchasing Power Parity (PPP)
conversion tables, and player spender segmentation simulation (Whales vs Dolphins vs Minnows).
"""

from typing import Dict, Any, List, Optional

class IAPMonetizationAnalyzer:
    """IAP & Monetization Strategy Analyzer for Mobile Games."""

    def __init__(self):
        # Standard Price Ladders by Genre
        self.genre_monetization_benchmarks = {
            "hybrid_casual": {
                "genre_name": "Hybrid-Casual / Arcade Idle",
                "ad_vs_iap_split": {"ad_share": 65, "iap_share": 35},
                "median_arpu_d30": 0.45,
                "median_paying_conversion": 2.2,  # % of DAU who ever pay
                "price_ladder": [
                    {"tier": "No-Ads Bait", "price_usd": 2.99, "conversion_share": "55%", "description": "Gói xóa quảng cáo bắt buộc (interstitial) + tặng kèm 200 gem khởi đầu"},
                    {"tier": "Starter Bundle", "price_usd": 0.99, "conversion_share": "25%", "description": "Mở khóa nhân vật tốc độ + x2 tài nguyên trong 24h"},
                    {"tier": "Weekly VIP Pass", "price_usd": 1.99, "conversion_share": "12%", "description": "Tự động nhặt đồ + skip ads nhận thưởng 7 ngày"},
                    {"tier": "Season Quest Pass", "price_usd": 4.99, "conversion_share": "8%", "description": "Battle pass 14 ngày mở khóa skin độc quyền"}
                ],
                "whale_cap": "Low ($15 - $50 total LTV)",
                "recommended_mechanics": ["Forced Ads Removal", "Piggy Bank (Break for $1.99)", "Speedup Boosters"]
            },
            "midcore_rpg": {
                "genre_name": "Mid-Core Action / Idle RPG",
                "ad_vs_iap_split": {"ad_share": 15, "iap_share": 85},
                "median_arpu_d30": 2.80,
                "median_paying_conversion": 4.8,
                "price_ladder": [
                    {"tier": "First Purchase Bait", "price_usd": 0.99, "conversion_share": "40%", "description": "Nạp bất kỳ nhận tướng SSR 5 sao + 10 vé quay gacha (x1000% value)"},
                    {"tier": "Monthly Gem Card", "price_usd": 4.99, "conversion_share": "30%", "description": "Nhận ngay 300 Gem + 100 Gem mỗi ngày đăng nhập liên tục 30 ngày"},
                    {"tier": "Battle Pass (Season)", "price_usd": 9.99, "conversion_share": "18%", "description": "Chu kỳ 28 ngày, mở khóa tài nguyên nâng cấp gấp 10 lần bản miễn phí"},
                    {"tier": "Piggy Bank (Hũ heo đất)", "price_usd": 2.99, "conversion_share": "8%", "description": "Tích lũy kim cương qua màn chơi, mở khóa khi đầy hũ"},
                    {"tier": "Whale Pack Milestone", "price_usd": 49.99, "conversion_share": "3%", "description": "Gói nguyên liệu nâng sao tướng độc quyền giới hạn theo tuần"},
                    {"tier": "Super Whale Vault", "price_usd": 99.99, "conversion_share": "1%", "description": "Gói kim cương tối thượng tặng kèm VIP EXP lớn"}
                ],
                "whale_cap": "High ($500 - $10,000+ LTV)",
                "recommended_mechanics": ["First-purchase 1000% ROI", "Monthly Card Drip", "Tiered Battle Pass", "Pity Gacha"]
            },
            "strategy_4x": {
                "genre_name": "4X Strategy & Hardcore War",
                "ad_vs_iap_split": {"ad_share": 0, "iap_share": 100},
                "median_arpu_d30": 7.50,
                "median_paying_conversion": 3.5,
                "price_ladder": [
                    {"tier": "Builder Extra Queue", "price_usd": 4.99, "conversion_share": "35%", "description": "Mở vĩnh viễn thợ xây thứ 2 + tăng 20% tốc độ nghiên cứu quân sự"},
                    {"tier": "Alliance War Pass", "price_usd": 19.99, "conversion_share": "25%", "description": "Cả bang hội nhận rương thưởng khi thành viên thăng cấp chiến tích"},
                    {"tier": "Kingdom Resource Drip", "price_usd": 9.99, "conversion_share": "20%", "description": "Bảo vệ mỏ tài nguyên + cung cấp lúa/gỗ hàng ngày"},
                    {"tier": "Troop Speedup Pack", "price_usd": 49.99, "conversion_share": "12%", "description": "Gia tốc 7 ngày huấn luyện lính cấp T4/T5 khẩn cấp"},
                    {"tier": "Dominion Sovereign Bundle", "price_usd": 99.99, "conversion_share": "8%", "description": "Gói nạp lặp vô hạn cho Top Clan Leader trong các cuộc chiến Server vs Server (KvK)"}
                ],
                "whale_cap": "Massive ($2,000 - $100,000+ LTV)",
                "recommended_mechanics": ["Alliance Shared Gifting", "Peace Shield Monetization", "Infinite $99.99 Stacking Bundles"]
            },
            "gacha_anime": {
                "genre_name": "Anime Hero Collector / Turn-Based Gacha",
                "ad_vs_iap_split": {"ad_share": 5, "iap_share": 95},
                "median_arpu_d30": 4.20,
                "median_paying_conversion": 6.2,
                "price_ladder": [
                    {"tier": "Blessing of the Welkin Moon", "price_usd": 4.99, "conversion_share": "45%", "description": "Thẻ tháng đăng nhập nhận 90 đá mỗi ngày (x30 ngày)"},
                    {"tier": "Standard Battle Pass", "price_usd": 9.99, "conversion_share": "28%", "description": "Mở khóa vũ khí 4 sao độc quyền + 4 vé quay đặc biệt"},
                    {"tier": "Collector Deluxe Pass", "price_usd": 19.99, "conversion_share": "12%", "description": "Battle Pass + khung avatar động + nhảy sẵn 10 cấp"},
                    {"tier": "Character Banner Pack", "price_usd": 29.99, "conversion_share": "9%", "description": "Gói vé quay giới hạn nhân vật Rate-up trong 14 ngày"},
                    {"tier": "Genesis Crystal Cache", "price_usd": 99.99, "conversion_share": "6%", "description": "Gói đá quý cao nhất (x2 lần đầu nạp lại sau mỗi đợt Reset sinh nhật game)"}
                ],
                "whale_cap": "Ultra High ($1,000 - $30,000+ LTV)",
                "recommended_mechanics": ["Pity Counter (Hard pity at 80-90 pulls)", "Annual First-Purchase Bonus Reset", "Cosmetic Skins"]
            },
            "casual_match3": {
                "genre_name": "Casual Match-3 & Tile Decoration",
                "ad_vs_iap_split": {"ad_share": 40, "iap_share": 60},
                "median_arpu_d30": 1.60,
                "median_paying_conversion": 3.8,
                "price_ladder": [
                    {"tier": "Extra Lives & Coins Bait", "price_usd": 0.99, "conversion_share": "42%", "description": "5 lượt hồi sinh tức thì khi sắp hết lượt đi (Out-of-moves trigger)"},
                    {"tier": "Piggy Bank Gold Bank", "price_usd": 2.99, "conversion_share": "32%", "description": "Mở hũ vàng tích lũy qua mỗi chuỗi combo màn chơi"},
                    {"tier": "Golden Ticket Season Pass", "price_usd": 4.99, "conversion_share": "18%", "description": "Nhận trái tim vô hạn, tăng sức chứa tim từ 5 lên 8 trong 21 ngày"},
                    {"tier": "Super Booster Vault", "price_usd": 9.99, "conversion_share": "8%", "description": "Bộ combo búa, bom màu, hoán đổi vị trí"}
                ],
                "whale_cap": "Moderate ($50 - $400 LTV)",
                "recommended_mechanics": ["Choke-point Out-of-moves Prompts", "Unlimited Lives Timers", "Room Decorating Events"]
            }
        }

        # Purchasing Power Parity (PPP) Pricing Multipliers & Local Currencies
        self.ppp_matrix = [
            {"region": "US (United States)", "tier": "Tier 1", "currency": "USD", "symbol": "$", "fx_rate": 1.0, "ppp_ratio": 1.00, "starter_local": "$0.99", "pass_local": "$9.99", "whale_local": "$99.99", "cvr_impact": "Baseline"},
            {"region": "JP (Japan)", "tier": "Tier 1", "currency": "JPY", "symbol": "¥", "fx_rate": 150.0, "ppp_ratio": 0.95, "starter_local": "¥160", "pass_local": "¥1,500", "whale_local": "¥15,800", "cvr_impact": "+15% High Gacha Willingness"},
            {"region": "KR (South Korea)", "tier": "Tier 1", "currency": "KRW", "symbol": "₩", "fx_rate": 1350.0, "ppp_ratio": 0.90, "starter_local": "₩1,500", "pass_local": "₩14,000", "whale_local": "₩149,000", "cvr_impact": "+20% High PvP Spending"},
            {"region": "DE / EU (Europe)", "tier": "Tier 1", "currency": "EUR", "symbol": "€", "fx_rate": 0.92, "ppp_ratio": 1.05, "starter_local": "€1.19", "pass_local": "€11.99", "whale_local": "€119.99", "cvr_impact": "-5% (VAT included)"},
            {"region": "VN (Vietnam)", "tier": "Tier 3", "currency": "VND", "symbol": "₫", "fx_rate": 25000.0, "ppp_ratio": 0.40, "starter_local": "25,000 ₫", "pass_local": "129,000 ₫ (~$5.1)", "whale_local": "1,299,000 ₫ (~$52)", "cvr_impact": "+65% Paying Conversion when localized"},
            {"region": "BR (Brazil)", "tier": "Tier 3", "currency": "BRL", "symbol": "R$", "fx_rate": 5.5, "ppp_ratio": 0.45, "starter_local": "R$ 4.90", "pass_local": "R$ 27.90", "whale_local": "R$ 279.90", "cvr_impact": "+55% Paying Conversion"},
            {"region": "ID (Indonesia)", "tier": "Tier 3", "currency": "IDR", "symbol": "Rp", "fx_rate": 15800.0, "ppp_ratio": 0.38, "starter_local": "Rp 16,000", "pass_local": "Rp 79,000", "whale_local": "Rp 799,000", "cvr_impact": "+60% Paying Conversion"}
        ]

    def get_benchmarks(self, genre_key: Optional[str] = None) -> Dict[str, Any]:
        """Returns standard monetization ladders and PPP benchmarks."""
        if genre_key and genre_key in self.genre_monetization_benchmarks:
            genre_data = self.genre_monetization_benchmarks[genre_key]
        else:
            genre_data = self.genre_monetization_benchmarks

        return {
            "genres": self.genre_monetization_benchmarks,
            "ppp_matrix": self.ppp_matrix
        }

    def simulate_economy(
        self,
        dau: int = 50000,
        genre_key: str = "midcore_rpg",
        region_tier: str = "global",
        battle_pass_price: float = 9.99,
        monthly_card_price: float = 4.99
    ) -> Dict[str, Any]:
        """Simulates 30-day player spender distribution, revenue breakdown, and ARPPU."""
        benchmark = self.genre_monetization_benchmarks.get(genre_key, self.genre_monetization_benchmarks["midcore_rpg"])
        
        # Base paying conversion %
        base_conversion = benchmark["median_paying_conversion"] / 100.0
        
        # Region adjustments
        if region_tier == "tier3_sea":
            base_conversion *= 1.35  # Higher volume if micro-priced
            spending_power = 0.45
        elif region_tier == "tier1_us":
            spending_power = 1.00
        elif region_tier == "tier1_east_asia":
            spending_power = 1.25
            base_conversion *= 1.2
        else:
            spending_power = 0.85

        total_paying_users = int(dau * base_conversion)
        non_paying_dau = max(0, dau - total_paying_users)

        # Spender segmentation
        # Whales: 3% of payers
        # Dolphins: 22% of payers
        # Minnows: 75% of payers
        whale_count = max(1, int(total_paying_users * 0.03))
        dolphin_count = int(total_paying_users * 0.22)
        minnow_count = max(0, total_paying_users - whale_count - dolphin_count)

        # Average spend per tier per month
        avg_whale_spend = 350.0 * spending_power
        avg_dolphin_spend = (battle_pass_price + monthly_card_price + 15.0) * spending_power
        avg_minnow_spend = (0.99 + monthly_card_price * 0.5) * spending_power

        # Monthly Revenue breakdown
        whale_rev = whale_count * avg_whale_spend
        dolphin_rev = dolphin_count * avg_dolphin_spend
        minnow_rev = minnow_count * avg_minnow_spend
        total_iap_rev = whale_rev + dolphin_rev + minnow_rev

        # Ad revenue calculation
        ad_share_pct = benchmark["ad_vs_iap_split"]["ad_share"] / 100.0
        if ad_share_pct > 0:
            # Estimate ad revenue based on impressions & eCPM
            avg_ecpm = 8.5 * spending_power
            daily_impressions_per_dau = 3.2
            monthly_ad_rev = (dau * daily_impressions_per_dau * 30 * avg_ecpm) / 1000.0
        else:
            monthly_ad_rev = 0.0

        total_gross_rev = total_iap_rev + monthly_ad_rev
        arpu = round(total_gross_rev / max(1, dau), 2)
        arppu = round(total_iap_rev / max(1, total_paying_users), 2)
        arpdau = round(total_gross_rev / (max(1, dau) * 30), 4)

        whale_share_pct = round((whale_rev / max(1, total_iap_rev)) * 100, 1)
        dolphin_share_pct = round((dolphin_rev / max(1, total_iap_rev)) * 100, 1)
        minnow_share_pct = round((minnow_rev / max(1, total_iap_rev)) * 100, 1)

        return {
            "inputs": {
                "dau": dau,
                "genre": benchmark["genre_name"],
                "region_tier": region_tier,
                "battle_pass_price": battle_pass_price,
                "monthly_card_price": monthly_card_price
            },
            "financial_summary": {
                "total_monthly_gross_usd": round(total_gross_rev, 2),
                "monthly_iap_usd": round(total_iap_rev, 2),
                "monthly_ad_usd": round(monthly_ad_rev, 2),
                "monthly_arpu_usd": arpu,
                "monthly_arppu_usd": arppu,
                "daily_arpdau_usd": arpdau,
                "payer_conversion_rate": round(base_conversion * 100, 2)
            },
            "spender_distribution": {
                "whales": {
                    "count": whale_count,
                    "pct_of_payers": 3.0,
                    "avg_monthly_spend": round(avg_whale_spend, 2),
                    "total_revenue": round(whale_rev, 2),
                    "revenue_contribution_pct": whale_share_pct
                },
                "dolphins": {
                    "count": dolphin_count,
                    "pct_of_payers": 22.0,
                    "avg_monthly_spend": round(avg_dolphin_spend, 2),
                    "total_revenue": round(dolphin_rev, 2),
                    "revenue_contribution_pct": dolphin_share_pct
                },
                "minnows": {
                    "count": minnow_count,
                    "pct_of_payers": 75.0,
                    "avg_monthly_spend": round(avg_minnow_spend, 2),
                    "total_revenue": round(minnow_rev, 2),
                    "revenue_contribution_pct": minnow_share_pct
                },
                "f2p_users": {
                    "count": non_paying_dau,
                    "pct_of_dau": round((non_paying_dau / max(1, dau)) * 100, 1),
                    "ad_value_generated": round(monthly_ad_rev, 2)
                }
            },
            "revenue_split": {
                "iap_pct": round((total_iap_rev / max(1, total_gross_rev)) * 100, 1),
                "ad_pct": round((monthly_ad_rev / max(1, total_gross_rev)) * 100, 1)
            }
        }
