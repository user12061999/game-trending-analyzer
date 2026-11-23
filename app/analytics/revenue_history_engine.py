"""Revenue & Download Historical Estimation Engine (rank-based power-law model).

Calculates multi-day estimated revenue/download curves, country tier attribution,
blended ARPU, and lifecycle phase diagnostics for any tracked PC or Mobile game.

IMPORTANT: every revenue / download number here is a MODEL ESTIMATE derived from
chart rank. Only the rank itself comes from real crawl snapshots, and each timeline
point says whether its rank was observed ("snapshot") or filled in.
"""

from datetime import date, timedelta
from typing import Dict, Any, List, Tuple

from app.database.db import get_db_connection
from app.analytics.revenue_estimator import RevenueEstimator


# Assumed (not measured) split of revenue/downloads across country tiers.
TIER_SPLITS = {
    "tier_1": {
        "name": "Tier 1 (US, JP, KR, UK, DE)",
        "rev_share": 0.645,
        "dl_share": 0.28,
        "countries": ["Mỹ 🇺🇸", "Nhật Bản 🇯🇵", "Hàn Quốc 🇰🇷", "Đức 🇩🇪", "Anh 🇬🇧"],
    },
    "tier_2": {
        "name": "Tier 2 (FR, CA, TW, AU, IT)",
        "rev_share": 0.215,
        "dl_share": 0.22,
        "countries": ["Đài Loan 🇹🇼", "Pháp 🇫🇷", "Canada 🇨🇦", "Úc 🇦🇺"],
    },
    "tier_3": {
        "name": "Tier 3 (VN, BR, ID, IN, PH, TH)",
        "rev_share": 0.14,
        "dl_share": 0.50,
        "countries": ["Việt Nam 🇻🇳", "Brazil 🇧🇷", "Indonesia 🇮🇩", "Thái Lan 🇹🇭", "Philippines 🇵🇭"],
    },
}


class RevenueHistoryEngine:
    """Calculates N-day estimated revenue/download trends, ARPU, and lifecycle diagnostics."""

    @staticmethod
    def _load_rows(game_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT snapshot_date, rank, player_count, price, platform, country, ranking_type,
                       title, developer, genre, icon_url
                FROM snapshots
                WHERE game_id = ?
                ORDER BY snapshot_date ASC
            """, (game_id,))
            rows = [dict(r) for r in cursor.fetchall()]

            # If no direct match by game_id, try finding by title substring
            if not rows:
                cursor.execute("""
                    SELECT snapshot_date, rank, player_count, price, platform, country, ranking_type,
                           title, developer, genre, icon_url, game_id
                    FROM snapshots
                    WHERE title LIKE ? OR game_id LIKE ?
                    ORDER BY snapshot_date ASC
                """, (f"%{game_id}%", f"%{game_id}%"))
                rows = [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()
        return rows

    @staticmethod
    def get_game_revenue_history(game_id: str, days: int = 30) -> Dict[str, Any]:
        """Returns N-day estimated revenue, downloads, ARPU and lifecycle intelligence."""
        rows = RevenueHistoryEngine._load_rows(game_id)

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
            # Only use snapshots from the same chart as the latest record; mixing ranks
            # from different countries / chart types would produce a meaningless series.
            rows = [
                r for r in rows
                if r.get("platform") == latest_record.get("platform")
                and r.get("country") == latest_record.get("country")
                and r.get("ranking_type") == latest_record.get("ranking_type")
            ]
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

        snapshot_map: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            d_str = r.get("snapshot_date")
            if d_str:
                snapshot_map[d_str] = r

        today = date.today()
        window_dates = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
        rank_by_date = RevenueHistoryEngine._fill_rank_series(window_dates, snapshot_map, base_rank)

        timeline: List[Dict[str, Any]] = []
        running_cum_rev = 0
        running_cum_dl = 0

        for cur_date in window_dates:
            cur_date_str = cur_date.isoformat()
            day_rank, data_source = rank_by_date[cur_date_str]
            snap = snapshot_map.get(cur_date_str)

            if is_pc:
                p_cnt = (snap.get("player_count") if snap else None) or player_count
                day_est = RevenueEstimator.estimate_steam_revenue(day_rank, p_cnt, price_str)
                d_rev = day_est.get("daily_revenue", 0)
                d_dl = day_est.get("estimated_units_sold_daily", 0)
            else:
                d_rev = RevenueEstimator.estimate_mobile_revenue(day_rank, country=country).get("daily_revenue", 0)
                d_dl = RevenueEstimator.estimate_mobile_downloads(day_rank, country=country).get("daily_downloads", 0)

            running_cum_rev += d_rev
            running_cum_dl += d_dl

            timeline.append({
                "date": cur_date_str,
                "display_date": cur_date.strftime("%d/%m"),
                "daily_revenue": d_rev,
                "daily_downloads": d_dl,
                "cumulative_revenue": running_cum_rev,
                "cumulative_downloads": running_cum_dl,
                "rank": day_rank,
                "arpu": round(d_rev / max(1, d_dl), 2),
                "is_weekend": cur_date.weekday() in (5, 6),
                # "snapshot"     = rank observed by a crawl that day
                # "interpolated" = gap between two crawls (linear)
                # "carried"      = before first / after last crawl (nearest known rank)
                # "assumed"      = no crawl data at all for this game
                "data_source": data_source,
                "is_estimated": data_source != "snapshot",
            })

        actual_days = sum(1 for d in timeline if d["data_source"] == "snapshot")
        coverage_pct = round(actual_days / max(1, days) * 100, 1)

        # Aggregate summary metrics
        total_rev = sum(d["daily_revenue"] for d in timeline)
        total_dl = sum(d["daily_downloads"] for d in timeline)
        avg_daily_rev = int(total_rev / days)
        avg_daily_dl = int(total_dl / days)
        blended_arpu = round(total_rev / max(1, total_dl), 2)

        # WoW velocity (last 7 days vs previous 7 days)
        last_7 = timeline[-7:]
        prev_7 = timeline[-14:-7] if len(timeline) >= 14 else last_7
        last_7d_rev = sum(d["daily_revenue"] for d in last_7)
        prev_7d_rev = sum(d["daily_revenue"] for d in prev_7)
        wow_growth_pct = round(((last_7d_rev - prev_7d_rev) / max(1, prev_7d_rev)) * 100, 1)

        has_real_wow = (
            len(timeline) >= 14
            and sum(1 for d in last_7 if d["data_source"] == "snapshot") >= 2
            and sum(1 for d in prev_7 if d["data_source"] == "snapshot") >= 2
        )
        lifecycle_phase, lifecycle_desc, badge_color = RevenueHistoryEngine._lifecycle(
            wow_growth_pct, has_real_wow, actual_days, days
        )

        # Monetization Efficiency Score (1 - 100)
        base_score = min(85, int(blended_arpu * 26))
        growth_bonus = max(-15, min(15, int(wow_growth_pct * 0.6))) if has_real_wow else 0
        monetization_score = max(20, min(98, base_score + growth_bonus + 10))

        tier_breakdown = {}
        for key, t in TIER_SPLITS.items():
            rev = int(total_rev * t["rev_share"])
            dl = int(total_dl * t["dl_share"])
            tier_breakdown[key] = {
                "name": t["name"],
                "share_pct": round(t["rev_share"] * 100, 1),
                "revenue": rev,
                "revenue_formatted": RevenueHistoryEngine._format_currency(rev),
                "downloads": dl,
                "downloads_formatted": RevenueHistoryEngine._format_number(dl),
                "arpu": round(rev / max(1, dl), 2),
                "countries": t["countries"],
                "is_assumed_split": True,
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
                "total_revenue": total_rev,
                "total_revenue_formatted": RevenueHistoryEngine._format_currency(total_rev),
                "total_downloads": total_dl,
                "total_downloads_formatted": RevenueHistoryEngine._format_number(total_dl),
                "average_daily_revenue": avg_daily_rev,
                "average_daily_revenue_formatted": RevenueHistoryEngine._format_currency(avg_daily_rev),
                "average_daily_downloads": avg_daily_dl,
                "average_daily_downloads_formatted": RevenueHistoryEngine._format_number(avg_daily_dl),
                "blended_arpu": blended_arpu,
                "blended_arpu_formatted": f"${blended_arpu:.2f}",
                "monetization_score": monetization_score,
                "wow_growth_pct": wow_growth_pct,
            },
            "data_quality": {
                "actual_snapshot_days": actual_days,
                "days_requested": days,
                "coverage_pct": coverage_pct,
                "has_reliable_wow": has_real_wow,
                "is_model_estimate": True,
                "note": (
                    "Doanh thu & lượt tải là ƯỚC TÍNH từ mô hình Power-law theo thứ hạng, không phải số liệu thật. "
                    f"{actual_days}/{days} ngày có thứ hạng crawl thật; các ngày còn lại được nội suy tuyến tính "
                    "hoặc giữ nguyên thứ hạng gần nhất. Tỷ trọng theo Tier quốc gia là giả định."
                ),
            },
            "lifecycle": {
                "phase": lifecycle_phase,
                "description": lifecycle_desc,
                "wow_growth_pct": wow_growth_pct,
                "badge_color": badge_color,
            },
            "tier_breakdown": tier_breakdown,
        }

    @staticmethod
    def _lifecycle(wow: float, reliable: bool, actual_days: int, days: int) -> Tuple[str, str, str]:
        if not reliable:
            return (
                "❔ Chưa Đủ Dữ Liệu (Insufficient Data)",
                f"Chỉ có {actual_days}/{days} ngày có snapshot thật. Cần ít nhất 2 ngày crawl trong mỗi tuần "
                "của 14 ngày gần nhất để đánh giá xu hướng tuần đáng tin cậy.",
                "slate",
            )
        if wow >= 12.0:
            return (
                "🚀 Tăng Trưởng Nóng (Hyper Growth)",
                f"Doanh thu ước tính tuần qua tăng +{wow}%. Lượng người chơi mới gia tăng nhanh, cơ hội tối ưu chuyển đổi nạp lần đầu (FTUE IAP).",
                "emerald",
            )
        if wow >= -4.0:
            return (
                "⚖️ Bão Hòa / Trưởng Thành (Maturity)",
                f"Doanh thu ước tính ổn định (biến động {wow}% WoW). Cần đẩy mạnh chuỗi sự kiện LiveOps định kỳ.",
                "indigo",
            )
        if wow >= -15.0:
            return (
                "📉 Hạ Nhiệt Nhẹ (Early Fatigue)",
                f"Doanh thu ước tính giảm {wow}% WoW. Cần cập nhật nội dung mới, Battle Pass Season mới để tái kích hoạt người chơi cũ.",
                "amber",
            )
        return (
            "⚠️ Thoái Trào Cần Can Thiệp (Decline)",
            f"Doanh thu ước tính sụt mạnh {wow}% so với tuần trước. Cần xem lại phễu D7-D30 retention và chính sách giá.",
            "rose",
        )

    @staticmethod
    def _fill_rank_series(window_dates, snapshot_map, base_rank) -> Dict[str, Tuple[int, str]]:
        """Returns {date_str: (rank, data_source)} for every date in the window.

        Real snapshot ranks are kept as-is. Gaps between two snapshots are linearly
        interpolated; dates outside the observed range carry the nearest known rank.
        No random noise is ever introduced.
        """
        known = sorted(
            (date.fromisoformat(d), int(r.get("rank") or base_rank))
            for d, r in snapshot_map.items()
        )
        result: Dict[str, Tuple[int, str]] = {}
        for cur in window_dates:
            key = cur.isoformat()
            if not known:
                result[key] = (int(base_rank), "assumed")
                continue
            if key in snapshot_map:
                result[key] = (int(snapshot_map[key].get("rank") or base_rank), "snapshot")
                continue
            before = [(d, r) for d, r in known if d < cur]
            after = [(d, r) for d, r in known if d > cur]
            if before and after:
                (d0, r0), (d1, r1) = before[-1], after[0]
                frac = (cur - d0).days / max(1, (d1 - d0).days)
                result[key] = (max(1, round(r0 + (r1 - r0) * frac)), "interpolated")
            elif before:
                result[key] = (before[-1][1], "carried")
            else:
                result[key] = (after[0][1], "carried")
        return result

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
