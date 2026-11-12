"""Revenue & Download Historical Intelligence Engine (Sensor Tower / AppMagic Style).

Calculates multi-day historical revenue, download curves, country tier revenue attribution,
blended ARPU, and lifecycle phase diagnostics for any tracked PC or Mobile game.
"""

import math
import random
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional

from app.database.db import get_db_connection
from app.analytics.revenue_estimator import RevenueEstimator


class RevenueHistoryEngine:
    """Calculates 30-day revenue/download trends, ARPU, and lifecycle diagnostics."""

    @staticmethod
    def get_game_revenue_history(game_id: str, days: int = 30) -> Dict[str, Any]:
        """Returns 30-day historical revenue, downloads, ARPU and lifecycle intelligence."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query recorded snapshots for this game ordered by date ASC
        cursor.execute("""
            SELECT snapshot_date, rank, player_count, price, platform, country, ranking_type, title, developer, genre, icon_url
            FROM snapshots
            WHERE game_id = ?
            ORDER BY snapshot_date ASC
        """, (game_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        # If no direct match by game_id, try finding by title substring
        if not rows:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT snapshot_date, rank, player_count, price, platform, country, ranking_type, title, developer, genre, icon_url, game_id
                FROM snapshots
                WHERE title LIKE ? OR game_id LIKE ?
                ORDER BY snapshot_date ASC
            """, (f"%{game_id}%", f"%{game_id}%"))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()

        # Baseline info
        if rows:
            latest_record = rows[-1]
            title = latest_record.get("title") or game_id
            platform = latest_record.get("platform", "mobile_appstore")
            genre = latest_record.get("genre", "Action")
            country = latest_record.get("country", "global")
            base_rank = latest_record.get("rank") or 15
            player_count = latest_record.get("player_count") or 0
            price_str = latest_record.get("price") or "$0.00"
            icon_url = latest_record.get("icon_url", "")
        else:
            title = game_id.replace("_", " ").title()
            platform = "mobile_appstore"
            genre = "Action"
            country = "global"
            base_rank = 18
            player_count = 0
            price_str = "$0.00"
            icon_url = ""

        is_pc = "pc" in platform.lower() or "steam" in platform.lower()

        # Calculate baseline daily revenue & downloads using Pareto Power-law
        if is_pc:
            base_est = RevenueEstimator.estimate_steam_revenue(base_rank, player_count, price_str)
            base_daily_rev = base_est.get("daily_revenue", 45000)
            base_daily_dl = base_est.get("estimated_units_sold_daily", 1800)
        else:
            base_est = RevenueEstimator.estimate_mobile_revenue(base_rank, country=country)
            base_dl_est = RevenueEstimator.estimate_mobile_downloads(base_rank, country=country)
            base_daily_rev = base_est.get("daily_revenue", 38000)
            base_daily_dl = base_dl_est.get("daily_downloads", 14000)

        # Build snapshot date lookup map
        snapshot_map = {}
        for r in rows:
            d_str = r.get("snapshot_date")
            if d_str:
                snapshot_map[d_str] = r

        # Generate continuous 30-day timeline ending at today
        today = date.today()
        timeline: List[Dict[str, Any]] = []
        running_cum_rev = 0
        running_cum_dl = 0

        # Pseudo-random seed deterministic on game title
        seed_val = sum(ord(c) for c in title)
        rng = random.Random(seed_val)

        for i in range(days - 1, -1, -1):
            cur_date = today - timedelta(days=i)
            cur_date_str = cur_date.isoformat()

            # If snapshot exists for this exact date, use real rank
            if cur_date_str in snapshot_map:
                snap = snapshot_map[cur_date_str]
                day_rank = snap.get("rank") or base_rank
                if is_pc:
                    p_cnt = snap.get("player_count") or player_count
                    day_est = RevenueEstimator.estimate_steam_revenue(day_rank, p_cnt, price_str)
                    d_rev = day_est.get("daily_revenue", base_daily_rev)
                    d_dl = day_est.get("estimated_units_sold_daily", base_daily_dl)
                else:
                    d_rev = RevenueEstimator.estimate_mobile_revenue(day_rank, country=country).get("daily_revenue", base_daily_rev)
                    d_dl = RevenueEstimator.estimate_mobile_downloads(day_rank, country=country).get("daily_downloads", base_daily_dl)
            else:
                # Organic market curve with weekend spikes (Saturdays/Sundays +18-25%)
                weekday = cur_date.weekday()
                weekend_multiplier = 1.22 if weekday in (5, 6) else 1.0

                # Slight progressive slope or drift based on day index
                drift = 1.0 + (days - i - 1) * 0.004 + rng.uniform(-0.06, 0.07)
                d_rev = int(base_daily_rev * drift * weekend_multiplier)
                d_dl = int(base_daily_dl * drift * (1.15 if weekday in (5, 6) else 0.98))
                day_rank = max(1, int(base_rank + rng.randint(-3, 3)))

            running_cum_rev += d_rev
            running_cum_dl += d_dl

            # Day ARPU
            day_arpu = round(d_rev / max(1, d_dl), 2)

            timeline.append({
                "date": cur_date_str,
                "display_date": cur_date.strftime("%d/%m"),
                "daily_revenue": d_rev,
                "daily_downloads": d_dl,
                "cumulative_revenue": running_cum_rev,
                "cumulative_downloads": running_cum_dl,
                "rank": day_rank,
                "arpu": day_arpu,
                "is_weekend": cur_date.weekday() in (5, 6)
            })

        # Calculate aggregate summary metrics
        total_30d_rev = sum(d["daily_revenue"] for d in timeline)
        total_30d_dl = sum(d["daily_downloads"] for d in timeline)
        avg_daily_rev = int(total_30d_rev / days)
        avg_daily_dl = int(total_30d_dl / days)
        blended_arpu = round(total_30d_rev / max(1, total_30d_dl), 2)

        # WoW Velocity (Compare last 7 days vs previous 7 days)
        last_7d_rev = sum(d["daily_revenue"] for d in timeline[-7:])
        prev_7d_rev = sum(d["daily_revenue"] for d in timeline[-14:-7]) if len(timeline) >= 14 else last_7d_rev
        wow_growth_pct = round(((last_7d_rev - prev_7d_rev) / max(1, prev_7d_rev)) * 100, 1)

        # Lifecycle Phase Determination
        if wow_growth_pct >= 12.0:
            lifecycle_phase = "🚀 Tăng Trưởng Nóng (Hyper Growth)"
            lifecycle_desc = f"Doanh thu tuần qua tăng trưởng vượt bậc +{wow_growth_pct}%. Lượng người chơi mới gia tăng nhanh chóng, cơ hội tối ưu chuyển đổi nạp lần đầu (FTUE IAP)."
            badge_color = "emerald"
        elif wow_growth_pct >= -4.0:
            lifecycle_phase = "⚖️ Bão Hòa / Trưởng Thành (Maturity)"
            lifecycle_desc = f"Doanh thu duy trì ổn định (biến động {wow_growth_pct}% WoW). Game đã xây dựng được tập người chơi nạp ổn định (Whales & Dolphins), cần đẩy mạnh chuỗi sự kiện LiveOps định kỳ."
            badge_color = "indigo"
        elif wow_growth_pct >= -15.0:
            lifecycle_phase = "📉 Hạ Nhiệt Nhẹ (Early Fatigue)"
            lifecycle_desc = f"Hiệu suất doanh thu giảm {wow_growth_pct}% WoW. Cần cập nhật nội dung mới, tung Battle Pass Season mới để tái kích hoạt người chơi cũ (Re-engagement)."
            badge_color = "amber"
        else:
            lifecycle_phase = "⚠️ Thoái Trào Cần Can Thiệp (Decline)"
            lifecycle_desc = f"Doanh thu sụt giảm mạnh {wow_growth_pct}% so với tuần trước. Cần điều chỉnh lại phễu D7-D30 retention và xem xét chính sách giá hoặc chế độ chơi đột phá."
            badge_color = "rose"

        # Monetization Efficiency Score (1 - 100)
        # Based on ARPU benchmark ($1.50 = 70pts, $3.00+ = 90pts) and growth
        base_score = min(85, int(blended_arpu * 26))
        growth_bonus = max(-15, min(15, int(wow_growth_pct * 0.6)))
        monetization_score = max(20, min(98, base_score + growth_bonus + 10))

        # Country Tier Breakdown (Tier 1 US/JP/KR vs Tier 2 vs Tier 3 SEA)
        tier_breakdown = {
            "tier_1": {
                "name": "Tier 1 (US, JP, KR, UK, DE)",
                "share_pct": 64.5,
                "revenue": int(total_30d_rev * 0.645),
                "revenue_formatted": RevenueHistoryEngine._format_currency(int(total_30d_rev * 0.645)),
                "downloads": int(total_30d_dl * 0.28),
                "downloads_formatted": RevenueHistoryEngine._format_number(int(total_30d_dl * 0.28)),
                "arpu": round((total_30d_rev * 0.645) / max(1, total_30d_dl * 0.28), 2),
                "countries": ["Mỹ 🇺🇸", "Nhật Bản 🇯🇵", "Hàn Quốc 🇰🇷", "Đức 🇩🇪", "Anh 🇬🇧"]
            },
            "tier_2": {
                "name": "Tier 2 (FR, CA, TW, AU, IT)",
                "share_pct": 21.5,
                "revenue": int(total_30d_rev * 0.215),
                "revenue_formatted": RevenueHistoryEngine._format_currency(int(total_30d_rev * 0.215)),
                "downloads": int(total_30d_dl * 0.22),
                "downloads_formatted": RevenueHistoryEngine._format_number(int(total_30d_dl * 0.22)),
                "arpu": round((total_30d_rev * 0.215) / max(1, total_30d_dl * 0.22), 2),
                "countries": ["Đài Loan 🇹🇼", "Pháp 🇫🇷", "Canada 🇨🇦", "Úc 🇦🇺"]
            },
            "tier_3": {
                "name": "Tier 3 (VN, BR, ID, IN, PH, TH)",
                "share_pct": 14.0,
                "revenue": int(total_30d_rev * 0.14),
                "revenue_formatted": RevenueHistoryEngine._format_currency(int(total_30d_rev * 0.14)),
                "downloads": int(total_30d_dl * 0.50),
                "downloads_formatted": RevenueHistoryEngine._format_number(int(total_30d_dl * 0.50)),
                "arpu": round((total_30d_rev * 0.14) / max(1, total_30d_dl * 0.50), 2),
                "countries": ["Việt Nam 🇻🇳", "Brazil 🇧🇷", "Indonesia 🇮🇩", "Thái Lan 🇹🇭", "Philippines 🇵🇭"]
            }
        }

        return {
            "game_id": game_id,
            "title": title,
            "platform": platform,
            "genre": genre,
            "country": country,
            "icon_url": icon_url,
            "days_requested": days,
            "timeline": timeline,
            "metrics_summary": {
                "total_revenue": total_30d_rev,
                "total_revenue_formatted": RevenueHistoryEngine._format_currency(total_30d_rev),
                "total_downloads": total_30d_dl,
                "total_downloads_formatted": RevenueHistoryEngine._format_number(total_30d_dl),
                "average_daily_revenue": avg_daily_rev,
                "average_daily_revenue_formatted": RevenueHistoryEngine._format_currency(avg_daily_rev),
                "average_daily_downloads": avg_daily_dl,
                "average_daily_downloads_formatted": RevenueHistoryEngine._format_number(avg_daily_dl),
                "blended_arpu": blended_arpu,
                "blended_arpu_formatted": f"${blended_arpu:.2f}",
                "monetization_score": monetization_score,
                "wow_growth_pct": wow_growth_pct
            },
            "lifecycle": {
                "phase": lifecycle_phase,
                "description": lifecycle_desc,
                "wow_growth_pct": wow_growth_pct,
                "badge_color": badge_color
            },
            "tier_breakdown": tier_breakdown
        }

    @staticmethod
    def _format_currency(val: int) -> str:
        if val >= 1_000_000:
            return f"${val / 1_000_000:.2f}M"
        elif val >= 1_000:
            return f"${val / 1_000:.1f}K"
        return f"${val:,}"

    @staticmethod
    def _format_number(val: int) -> str:
        if val >= 1_000_000:
            return f"{val / 1_000_000:.2f}M"
        elif val >= 1_000:
            return f"{val / 1_000:.1f}K"
        return f"{val:,}"
