"""Trend Analytics Engine for PC and Mobile Market Intelligence."""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from app.database.db import get_db_connection
from app.analytics.revenue_estimator import RevenueEstimator

class TrendAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def enrich_record_with_estimates(rec: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates estimated revenue and downloads for a game record."""
        platform = (rec.get("platform") or "").lower()
        rank = rec.get("rank") or 1
        country = rec.get("country") or "us"
        ranking_type = rec.get("ranking_type") or "top_grossing"

        if "pc" in platform:
            rev_info = RevenueEstimator.estimate_pc_revenue(
                price_str=rec.get("price", "Free"),
                estimated_downloads_str=rec.get("estimated_downloads", ""),
                player_count=rec.get("player_count", 0),
                rank=rank
            )
            rec["estimated_revenue_daily"] = rev_info["daily_revenue"]
            rec["estimated_revenue_daily_formatted"] = rev_info["daily_revenue_formatted"]
            rec["estimated_revenue_monthly"] = rev_info["monthly_revenue"]
            rec["estimated_revenue_monthly_formatted"] = rev_info["monthly_revenue_formatted"]
            rec["estimated_lifetime_gross"] = rev_info["lifetime_gross"]
            rec["estimated_lifetime_formatted"] = rev_info["lifetime_formatted"]
            rec["estimated_downloads_formatted"] = f"{rec.get('player_count', 0):,} CCU"
        else:
            rev_info = RevenueEstimator.estimate_mobile_revenue(rank=rank, country=country, ranking_type=ranking_type)
            dl_info = RevenueEstimator.estimate_mobile_downloads(rank=rank, country=country, ranking_type=ranking_type)
            rec["estimated_revenue_daily"] = rev_info["daily_revenue"]
            rec["estimated_revenue_daily_formatted"] = rev_info["daily_revenue_formatted"]
            rec["estimated_revenue_monthly"] = rev_info["monthly_revenue"]
            rec["estimated_revenue_monthly_formatted"] = rev_info["monthly_revenue_formatted"]
            rec["estimated_downloads_daily"] = dl_info["daily_downloads"]
            rec["estimated_downloads_formatted"] = dl_info["daily_downloads_formatted"]
        return rec

    def get_latest_snapshot_date(self) -> Optional[str]:
        """Gets the most recent date recorded in snapshots."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(snapshot_date) as max_date FROM snapshots")
        row = cursor.fetchone()
        conn.close()
        return row["max_date"] if row and row["max_date"] else date.today().isoformat()

    def get_market_overview(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Returns high-level metrics for dashboard cards and quick insights."""
        if not target_date:
            target_date = self.get_latest_snapshot_date()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Total games tracked on this date
        cursor.execute("SELECT COUNT(*) as total FROM snapshots WHERE snapshot_date = ?", (target_date,))
        total_tracked = cursor.fetchone()["total"]

        # Platform count breakdown
        cursor.execute("""
        SELECT platform, COUNT(*) as count 
        FROM snapshots 
        WHERE snapshot_date = ? 
        GROUP BY platform
        """, (target_date,))
        platform_counts = {row["platform"]: row["count"] for row in cursor.fetchall()}

        # Top Rising / Breakout Games (Rank surge > 0, sorted by rank_change_day DESC)
        cursor.execute("""
        SELECT title, developer, platform, country, ranking_type, rank, rank_change_day, icon_url, genre
        FROM snapshots
        WHERE snapshot_date = ? AND rank_change_day > 0
        ORDER BY rank_change_day DESC
        LIMIT 6
        """, (target_date,))
        rising_games = [dict(row) for row in cursor.fetchall()]

        # Top New Entries (Games that entered top ranks for the first time)
        cursor.execute("""
        SELECT title, developer, platform, country, ranking_type, rank, icon_url, genre
        FROM snapshots
        WHERE snapshot_date = ? AND is_new_entry = 1
        ORDER BY rank ASC
        LIMIT 6
        """, (target_date,))
        new_entries = [dict(row) for row in cursor.fetchall()]

        # Top Steam CCU (Current Concurrent Users)
        cursor.execute("""
        SELECT title, developer, rank, player_count, estimated_downloads, icon_url, genre, store_url, platform, price, country
        FROM snapshots
        WHERE snapshot_date = ? AND platform = 'pc_steam' AND ranking_type = 'most_played'
        ORDER BY player_count DESC
        LIMIT 5
        """, (target_date,))
        top_steam_ccu = [self.enrich_record_with_estimates(dict(row)) for row in cursor.fetchall()]

        # Top Mobile Grossing Global/US
        cursor.execute("""
        SELECT title, developer, platform, country, rank, score, icon_url, genre, store_url, price, ranking_type
        FROM snapshots
        WHERE snapshot_date = ? AND ranking_type = 'top_grossing'
        ORDER BY rank ASC
        LIMIT 5
        """, (target_date,))
        top_mobile_grossing = [self.enrich_record_with_estimates(dict(row)) for row in cursor.fetchall()]

        conn.close()

        return {
            "target_date": target_date,
            "total_tracked": total_tracked,
            "platform_counts": platform_counts,
            "rising_games": rising_games,
            "new_entries": new_entries,
            "top_steam_ccu": top_steam_ccu,
            "top_mobile_grossing": top_mobile_grossing
        }

    def get_rankings(
        self,
        platform: Optional[str] = None,
        country: Optional[str] = None,
        ranking_type: Optional[str] = None,
        genre: Optional[str] = None,
        search_query: Optional[str] = None,
        target_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Filters and retrieves game rankings based on user selection."""
        if not target_date:
            target_date = self.get_latest_snapshot_date()

        conn = get_db_connection()
        cursor = conn.cursor()

        conditions = ["snapshot_date = ?"]
        params = [target_date]

        if platform and platform != "all":
            if platform == "pc":
                conditions.append("platform LIKE 'pc%'")
            elif platform == "mobile":
                conditions.append("platform LIKE 'mobile%'")
            else:
                conditions.append("platform = ?")
                params.append(platform)

        if country and country != "all":
            conditions.append("country = ?")
            params.append(country.lower())

        if ranking_type and ranking_type != "all":
            conditions.append("ranking_type = ?")
            params.append(ranking_type)

        if genre and genre != "all":
            conditions.append("genre LIKE ?")
            params.append(f"%{genre}%")

        if search_query:
            conditions.append("(title LIKE ? OR developer LIKE ?)")
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT * FROM snapshots
        WHERE {where_clause}
        ORDER BY rank ASC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        cursor.execute(query, params)
        records = [self.enrich_record_with_estimates(dict(row)) for row in cursor.fetchall()]
        conn.close()
        return records

    def get_genre_distribution(self, platform: Optional[str] = None, country: Optional[str] = None, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Aggregates game count by genre for market share charts."""
        if not target_date:
            target_date = self.get_latest_snapshot_date()

        conn = get_db_connection()
        cursor = conn.cursor()

        conditions = ["snapshot_date = ?"]
        params = [target_date]

        if platform and platform != "all":
            if platform == "pc":
                conditions.append("platform LIKE 'pc%'")
            elif platform == "mobile":
                conditions.append("platform LIKE 'mobile%'")
            else:
                conditions.append("platform = ?")
                params.append(platform)

        if country and country != "all":
            conditions.append("country = ?")
            params.append(country.lower())

        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT genre, COUNT(*) as count
        FROM snapshots
        WHERE {where_clause} AND genre IS NOT NULL AND genre != ''
        GROUP BY genre
        ORDER BY count DESC
        LIMIT 10
        """
        cursor.execute(query, params)
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data

    def get_game_history(self, game_id: str, limit_days: int = 30) -> List[Dict[str, Any]]:
        """Returns historical ranking and player counts for a specific game."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT snapshot_date, rank, player_count, rank_change_day, score
        FROM snapshots
        WHERE game_id = ?
        ORDER BY snapshot_date ASC
        LIMIT ?
        """, (game_id, limit_days))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # If we only have 1 data point (first crawl), generate smooth preceding 6-day trend for visualization
        if len(rows) == 1:
            base = rows[0]
            simulated = []
            cur_date = datetime.strptime(base["snapshot_date"], "%Y-%m-%d").date()
            cur_rank = base["rank"]
            delta = base.get("rank_change_day", 0) or 0
            cur_ccu = base.get("player_count", 0) or 0

            # Backfill previous 6 days
            for i in range(6, 0, -1):
                d = (cur_date - timedelta(days=i)).isoformat()
                # Estimate previous rank based on delta trend
                prev_rank = max(1, cur_rank + int(delta * (i / 7.0)) + ((i % 3) - 1))
                prev_ccu = max(0, int(cur_ccu * (0.9 + (i % 3) * 0.05))) if cur_ccu > 0 else 0
                simulated.append({
                    "snapshot_date": d,
                    "rank": prev_rank,
                    "player_count": prev_ccu,
                    "rank_change_day": 0,
                    "score": base.get("score", 4.5),
                    "is_simulated": True
                })
            simulated.append(base)
            return simulated

        return rows

    def get_game_details(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Returns full detailed profile and analytics for a game."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM snapshots 
        WHERE game_id = ? 
        ORDER BY snapshot_date DESC, id DESC 
        LIMIT 1
        """, (game_id,))
        latest = cursor.fetchone()
        if not latest:
            conn.close()
            return None

        latest_dict = self.enrich_record_with_estimates(dict(latest))

        # Get historical stats
        cursor.execute("""
        SELECT 
            MIN(rank) as best_rank,
            MAX(rank) as worst_rank,
            ROUND(AVG(rank), 1) as avg_rank,
            MAX(player_count) as peak_ccu,
            COUNT(DISTINCT snapshot_date) as days_tracked
        FROM snapshots
        WHERE game_id = ?
        """, (game_id,))
        stats = dict(cursor.fetchone())
        conn.close()

        history = self.get_game_history(game_id, limit_days=30)

        return {
            "game": latest_dict,
            "stats": stats,
            "history": history
        }

    def search_games(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Searches distinct games by title or developer for comparison selection."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT DISTINCT game_id, title, developer, platform, genre, icon_url, rank, player_count
        FROM snapshots
        WHERE title LIKE ? OR developer LIKE ?
        ORDER BY rank ASC
        LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def compare_games(self, game_id_a: str, game_id_b: str) -> Dict[str, Any]:
        """Returns side-by-side comparison data and aligned historical charts."""
        detail_a = self.get_game_details(game_id_a)
        detail_b = self.get_game_details(game_id_b)

        if not detail_a or not detail_b:
            return {"error": "Một hoặc cả hai tựa game không tồn tại"}

        # Align history by date
        dates = sorted(list(set(
            [h["snapshot_date"] for h in detail_a["history"]] +
            [h["snapshot_date"] for h in detail_b["history"]]
        )))

        history_map_a = {h["snapshot_date"]: h for h in detail_a["history"]}
        history_map_b = {h["snapshot_date"]: h for h in detail_b["history"]}

        aligned = []
        for d in dates:
            aligned.append({
                "date": d,
                "game_a_rank": history_map_a.get(d, {}).get("rank"),
                "game_a_ccu": history_map_a.get(d, {}).get("player_count", 0),
                "game_b_rank": history_map_b.get(d, {}).get("rank"),
                "game_b_ccu": history_map_b.get(d, {}).get("player_count", 0),
            })

        return {
            "game_a": detail_a["game"],
            "stats_a": detail_a["stats"],
            "game_b": detail_b["game"],
            "stats_b": detail_b["stats"],
            "timeline": aligned
        }
