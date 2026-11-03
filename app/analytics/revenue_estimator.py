"""Revenue and Download Estimation Engine based on Power-Law / Pareto Distributions."""

import re
from typing import Dict, Any, Optional

# Base benchmark for Daily Revenue for Rank #1 on Top Grossing (in USD)
TIER_GROSSING_BENCHMARK = {
    "us": 1500000,       # ~$1.5M / day for #1 in US
    "global": 1600000,   # ~$1.6M / day worldwide benchmark
    "jp": 1000000,       # ~$1.0M / day for #1 in Japan (FGO, Monster Strike)
    "kr": 600000,        # ~$600K / day for #1 in Korea (Lineage, Odin)
    "gb": 280000,        # ~$280K / day for #1 in UK
    "de": 320000,        # ~$320K / day for #1 in Germany
    "vn": 120000,        # ~$120K / day for #1 in Vietnam (Liên Quân, Free Fire)
    "br": 140000,        # ~$140K / day for #1 in Brazil
    "id": 90000,         # ~$90K / day for #1 in Indonesia
    "th": 85000,         # ~$85K / day for #1 in Thailand
    "ph": 55000,         # ~$55K / day for #1 in Philippines
    "default": 100000
}

# Base benchmark for Daily Downloads for Rank #1 on Top Free
TIER_DOWNLOADS_BENCHMARK = {
    "us": 220000,       # ~220K downloads / day for #1 in US
    "global": 350000,
    "br": 180000,
    "id": 160000,
    "in": 250000,
    "vn": 50000,        # ~50K downloads / day for #1 in Vietnam
    "kr": 40000,
    "jp": 55000,
    "gb": 35000,
    "de": 40000,
    "default": 45000
}

class RevenueEstimator:
    @staticmethod
    def estimate_mobile_revenue(rank: int, country: str = "us", ranking_type: str = "top_grossing") -> Dict[str, Any]:
        """
        Estimates daily and monthly gross revenue for a mobile game.
        Formula: Revenue(rank) = R_1 * (rank ^ -0.84)
        """
        if rank <= 0:
            rank = 1

        country_key = country.lower() if country else "us"
        r1 = TIER_GROSSING_BENCHMARK.get(country_key, TIER_GROSSING_BENCHMARK["default"])

        # If not on top grossing (e.g. top free), scale down revenue based on ad-monetization/casual baseline
        if ranking_type == "top_free":
            # Free games make revenue mostly from ads & small IAPs
            daily_rev = int(r1 * 0.12 * (rank ** -0.75))
        else:
            # Top Grossing power-law
            daily_rev = int(r1 * (rank ** -0.84))

        # Add reasonable confidence interval range (-15% to +20%)
        low_daily = int(daily_rev * 0.85)
        high_daily = int(daily_rev * 1.20)

        monthly_est = daily_rev * 30
        low_monthly = low_daily * 30
        high_monthly = high_daily * 30

        return {
            "daily_revenue": daily_rev,
            "daily_revenue_formatted": RevenueEstimator._format_currency_range(low_daily, high_daily),
            "monthly_revenue": monthly_est,
            "monthly_revenue_formatted": RevenueEstimator._format_currency_range(low_monthly, high_monthly),
        }

    @staticmethod
    def estimate_mobile_downloads(rank: int, country: str = "us", ranking_type: str = "top_free") -> Dict[str, Any]:
        """
        Estimates daily and monthly downloads for a mobile game.
        Formula: Downloads(rank) = D_1 * (rank ^ -0.88)
        """
        if rank <= 0:
            rank = 1

        country_key = country.lower() if country else "us"
        d1 = TIER_DOWNLOADS_BENCHMARK.get(country_key, TIER_DOWNLOADS_BENCHMARK["default"])

        if ranking_type == "top_grossing":
            # Grossing games still get sustained organic installs
            daily_installs = int(d1 * 0.25 * (rank ** -0.80))
        else:
            daily_installs = int(d1 * (rank ** -0.88))

        low_d = int(daily_installs * 0.85)
        high_d = int(daily_installs * 1.20)

        monthly_installs = daily_installs * 30
        low_m = low_d * 30
        high_m = high_d * 30

        return {
            "daily_downloads": daily_installs,
            "daily_downloads_formatted": f"{RevenueEstimator._format_number(low_d)} - {RevenueEstimator._format_number(high_d)}/ngày",
            "monthly_downloads": monthly_installs,
            "monthly_downloads_formatted": f"{RevenueEstimator._format_number(low_m)} - {RevenueEstimator._format_number(high_m)}/tháng"
        }

    @staticmethod
    def estimate_pc_revenue(price_str: str, estimated_downloads_str: str, player_count: int = 0, rank: int = 1) -> Dict[str, Any]:
        """
        Estimates lifetime revenue and daily cash flow for a PC Steam game.
        Uses Owners count from SteamSpy and price (with ~0.65 realization rate for discounts/Steam cut).
        """
        # Parse price
        price = 0.0
        if price_str and price_str.lower() != "free" and "$" in price_str:
            clean = re.sub(r"[^\d\.]", "", price_str)
            try:
                price = float(clean)
            except ValueError:
                price = 0.0

        # Parse owners count (e.g. "10,000,000 .. 20,000,000 owners")
        owners_mid = 0
        if estimated_downloads_str and "owners" in estimated_downloads_str.lower():
            numbers = [int(s.replace(",", "")) for s in re.findall(r"[\d,]+", estimated_downloads_str)]
            if len(numbers) >= 2:
                owners_mid = (numbers[0] + numbers[1]) // 2
            elif len(numbers) == 1:
                owners_mid = numbers[0]

        # Calculate estimated lifetime gross
        if price > 0 and owners_mid > 0:
            # Net publisher realization factor after regional pricing & discounts ~ 65%
            lifetime_gross = int(owners_mid * price * 0.65)
            lifetime_formatted = f"~${RevenueEstimator._format_number(lifetime_gross)} (Gross)"
        elif price == 0 and owners_mid > 0:
            # Free to play: estimated average revenue per owner ~ $1.8 - $3.5
            lifetime_gross = int(owners_mid * 2.2)
            lifetime_formatted = f"~${RevenueEstimator._format_number(lifetime_gross)} (IAP Est.)"
        else:
            lifetime_gross = 0
            lifetime_formatted = "Đang ước tính"

        # Daily cash flow estimation based on CCU velocity and rank
        ccu = player_count or 0
        if ccu > 0:
            daily_rev = int(ccu * (0.85 if price > 0 else 0.45) * max(1.0, price * 0.1))
        else:
            daily_rev = int(800000 * (rank ** -0.92))

        low_d = int(daily_rev * 0.85)
        high_d = int(daily_rev * 1.25)

        return {
            "daily_revenue": daily_rev,
            "daily_revenue_formatted": RevenueEstimator._format_currency_range(low_d, high_d),
            "monthly_revenue": daily_rev * 30,
            "monthly_revenue_formatted": RevenueEstimator._format_currency_range(low_d * 30, high_d * 30),
            "lifetime_gross": lifetime_gross,
            "lifetime_formatted": lifetime_formatted
        }

    @staticmethod
    def _format_currency_range(low: int, high: int) -> str:
        return f"${RevenueEstimator._format_number(low)} - ${RevenueEstimator._format_number(high)}"

    @staticmethod
    def _format_number(n: int) -> str:
        if n >= 1000000:
            return f"{n / 1000000:.1f}M"
        elif n >= 1000:
            return f"{n / 1000:.0f}K"
        return f"{n:,}"
