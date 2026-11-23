"""Market signals built only from real crawl data: data health, sustained breakouts, genre trends."""

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from app.database.db import get_db_connection

# A chart is "stale" if its last successful crawl is older than this many hours
STALE_AFTER_HOURS = 36
# Sources not attempted for this long are considered retired and hidden from data health
RETIRED_AFTER_DAYS = 7


class MarketSignals:
    # ------------------------------------------------------------------ data health
    @staticmethod
    def get_data_health(now: Optional[datetime] = None) -> Dict[str, Any]:
        """Per-source crawl freshness, recent failures and snapshot coverage."""
        now = now or datetime.now()
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT platform, country, ranking_type,
                       MAX(CASE WHEN status = 'success' THEN crawled_at END) AS last_success,
                       MAX(crawled_at) AS last_attempt
                FROM crawl_history
                GROUP BY platform, country, ranking_type
                ORDER BY platform, country, ranking_type
            """)
            groups = [dict(r) for r in cur.fetchall()]

            retired_before = (now - timedelta(days=RETIRED_AFTER_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
            groups = [g for g in groups if g["last_attempt"] and g["last_attempt"] >= retired_before]

            sources = []
            for g in groups:
                cur.execute("""
                    SELECT status, items_count, error_message FROM crawl_history
                    WHERE platform = ? AND country = ? AND ranking_type = ?
                    ORDER BY id DESC LIMIT 1
                """, (g["platform"], g["country"], g["ranking_type"]))
                last = dict(cur.fetchone())
                cur.execute("""
                    SELECT COUNT(*) AS n FROM crawl_history
                    WHERE platform = ? AND country = ? AND ranking_type = ? AND status != 'success'
                      AND crawled_at >= ?
                """, (g["platform"], g["country"], g["ranking_type"],
                      (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")))
                failures_7d = cur.fetchone()["n"]

                age_h = None
                if g["last_success"]:
                    age_h = round((now - datetime.strptime(g["last_success"], "%Y-%m-%d %H:%M:%S")).total_seconds() / 3600, 1)

                if last["status"] != "success":
                    status = "failing"
                elif age_h is None or age_h > STALE_AFTER_HOURS:
                    status = "stale"
                else:
                    status = "ok"

                sources.append({
                    "platform": g["platform"],
                    "country": g["country"],
                    "ranking_type": g["ranking_type"],
                    "status": status,
                    "last_success": g["last_success"],
                    "last_attempt": g["last_attempt"],
                    "hours_since_success": age_h,
                    "last_items_count": last["items_count"],
                    "last_error": last["error_message"] if last["status"] != "success" else None,
                    "failures_7d": failures_7d,
                })

            cur.execute("""
                SELECT snapshot_date, COUNT(*) AS n FROM snapshots
                WHERE snapshot_date >= ?
                GROUP BY snapshot_date ORDER BY snapshot_date
            """, ((now.date() - timedelta(days=29)).isoformat(),))
            per_day = {r["snapshot_date"]: r["n"] for r in cur.fetchall()}
        finally:
            conn.close()

        coverage = []
        for i in range(29, -1, -1):
            d = (now.date() - timedelta(days=i)).isoformat()
            coverage.append({"date": d, "records": per_day.get(d, 0)})
        days_with_data = sum(1 for c in coverage if c["records"] > 0)

        counts = defaultdict(int)
        for s in sources:
            counts[s["status"]] += 1
        if not sources:
            overall = "no_data"
        elif counts["failing"] or counts["stale"]:
            overall = "degraded" if counts["ok"] else "down"
        else:
            overall = "healthy"

        return {
            "overall_status": overall,
            "sources_ok": counts["ok"],
            "sources_stale": counts["stale"],
            "sources_failing": counts["failing"],
            "days_with_data_30d": days_with_data,
            "missing_days_30d": [c["date"] for c in coverage if c["records"] == 0],
            "daily_coverage": coverage,
            "sources": sources,
            "generated_at": now.isoformat(timespec="seconds"),
        }

    # ------------------------------------------------------------ sustained breakouts
    @staticmethod
    def get_sustained_breakouts(
        window_days: int = 7,
        min_observations: int = 3,
        min_net_gain: int = 5,
        min_consistency: float = 0.6,
        platform: Optional[str] = None,
        country: Optional[str] = None,
        limit: int = 20,
        today: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """Games that climbed steadily over several snapshots, not just one lucky jump.

        consistency = share of day-to-day steps that were not drops.
        momentum score = net rank gain x consistency, penalised when one jump
        accounts for most of the gain.
        """
        today = today or date.today()
        start = (today - timedelta(days=window_days - 1)).isoformat()
        conditions = ["snapshot_date >= ?", "snapshot_date <= ?"]
        params: List[Any] = [start, today.isoformat()]
        if platform and platform != "all":
            if platform in ("pc", "mobile"):
                conditions.append("platform LIKE ?")
                params.append(f"{platform}%")
            else:
                conditions.append("platform = ?")
                params.append(platform)
        if country and country != "all":
            conditions.append("country = ?")
            params.append(country.lower())

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT snapshot_date, platform, country, ranking_type, game_id, rank,
                       title, developer, genre, icon_url, store_url
                FROM snapshots
                WHERE {' AND '.join(conditions)}
                ORDER BY snapshot_date ASC
            """, params)
            rows = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        series: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
        for r in rows:
            series[(r["platform"], r["country"], r["ranking_type"], r["game_id"])].append(r)

        results = []
        for (plat, ctry, rtype, gid), pts in series.items():
            if len(pts) < min_observations:
                continue
            ranks = [p["rank"] for p in pts]
            steps = [ranks[i - 1] - ranks[i] for i in range(1, len(ranks))]  # + = climbed
            net_gain = ranks[0] - ranks[-1]
            if net_gain < min_net_gain:
                continue
            consistency = sum(1 for s in steps if s >= 0) / len(steps)
            if consistency < min_consistency:
                continue
            biggest_jump = max(steps)
            jump_share = biggest_jump / net_gain if net_gain else 1
            spike_penalty = 0.5 if jump_share > 0.8 and len(steps) > 1 else 1.0
            score = round(net_gain * consistency * spike_penalty, 1)
            latest = pts[-1]
            results.append({
                "game_id": gid,
                "title": latest["title"],
                "developer": latest["developer"],
                "genre": latest["genre"],
                "icon_url": latest["icon_url"],
                "store_url": latest["store_url"],
                "platform": plat,
                "country": ctry,
                "ranking_type": rtype,
                "start_rank": ranks[0],
                "current_rank": ranks[-1],
                "net_gain": net_gain,
                "observations": len(pts),
                "first_date": pts[0]["snapshot_date"],
                "last_date": latest["snapshot_date"],
                "consistency_pct": round(consistency * 100, 1),
                "biggest_single_jump": biggest_jump,
                "is_single_spike": spike_penalty < 1.0,
                "momentum_score": score,
                "rank_series": [{"date": p["snapshot_date"], "rank": p["rank"]} for p in pts],
            })

        results.sort(key=lambda x: (-x["momentum_score"], x["current_rank"]))
        return results[:limit]

    # ----------------------------------------------------------------- genre trends
    @staticmethod
    def _week_window(end: date) -> tuple:
        return (end - timedelta(days=6)).isoformat(), end.isoformat()

    @staticmethod
    def get_genre_trends(
        platform: Optional[str] = None,
        country: Optional[str] = None,
        top_n_rank: int = 50,
        today: Optional[date] = None,
        limit: int = 15,
    ) -> Dict[str, Any]:
        """Week-over-week change in each genre's weighted share of the charts.

        Each chart entry contributes weight 1/sqrt(rank), so a #1 game counts more
        than a #50 game. Shares are averaged per snapshot day so weeks with more
        crawl days are not over-counted.
        """
        today = today or date.today()
        this_start, this_end = MarketSignals._week_window(today)
        prev_start, prev_end = MarketSignals._week_window(today - timedelta(days=7))

        conditions = ["snapshot_date >= ?", "snapshot_date <= ?", "rank <= ?",
                      "genre IS NOT NULL", "genre != ''"]
        params: List[Any] = [prev_start, this_end, top_n_rank]
        if platform and platform != "all":
            if platform in ("pc", "mobile"):
                conditions.append("platform LIKE ?")
                params.append(f"{platform}%")
            else:
                conditions.append("platform = ?")
                params.append(platform)
        if country and country != "all":
            conditions.append("country = ?")
            params.append(country.lower())

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT snapshot_date, genre, rank, title FROM snapshots
                WHERE {' AND '.join(conditions)}
            """, params)
            rows = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        def shares(start: str, end: str):
            per_day: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
            titles: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
            for r in rows:
                if start <= r["snapshot_date"] <= end:
                    g = MarketSignals._normalize_genre(r["genre"])
                    w = 1.0 / (max(1, r["rank"]) ** 0.5)
                    per_day[r["snapshot_date"]][g] += w
                    titles[g][r["title"]] += w
            if not per_day:
                return {}, 0, titles
            acc: Dict[str, float] = defaultdict(float)
            for day_weights in per_day.values():
                total = sum(day_weights.values()) or 1
                for g, w in day_weights.items():
                    acc[g] += w / total
            n_days = len(per_day)
            return {g: v / n_days * 100 for g, v in acc.items()}, n_days, titles

        this_share, this_days, this_titles = shares(this_start, this_end)
        prev_share, prev_days, _ = shares(prev_start, prev_end)

        genres = set(this_share) | set(prev_share)
        trends = []
        for g in genres:
            cur_s = round(this_share.get(g, 0.0), 2)
            prev_s = round(prev_share.get(g, 0.0), 2)
            delta = round(cur_s - prev_s, 2)
            top_titles = sorted(this_titles.get(g, {}).items(), key=lambda kv: -kv[1])[:3]
            trends.append({
                "genre": g,
                "share_pct": cur_s,
                "prev_share_pct": prev_s,
                "delta_pp": delta,
                "direction": "up" if delta > 0.5 else ("down" if delta < -0.5 else "flat"),
                "top_titles": [t for t, _ in top_titles],
            })
        trends.sort(key=lambda t: -t["share_pct"])

        return {
            "this_week": {"start": this_start, "end": this_end, "snapshot_days": this_days},
            "prev_week": {"start": prev_start, "end": prev_end, "snapshot_days": prev_days},
            "has_comparison": this_days > 0 and prev_days > 0,
            "genres": trends[:limit],
            "rising": sorted([t for t in trends if t["direction"] == "up"], key=lambda t: -t["delta_pp"])[:5],
            "falling": sorted([t for t in trends if t["direction"] == "down"], key=lambda t: t["delta_pp"])[:5],
        }

    @staticmethod
    def _normalize_genre(genre: str) -> str:
        """Takes the first genre of comma / slash separated lists ("Action, RPG" -> "Action")."""
        g = (genre or "").strip()
        for sep in (",", "/", "|", ";"):
            if sep in g:
                g = g.split(sep)[0].strip()
        return g or "Unknown"
