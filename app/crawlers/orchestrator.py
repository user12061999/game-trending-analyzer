"""Crawler Orchestrator to coordinate multi-platform crawls and calculate DoD / WoW deltas."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from app.database.db import get_db_connection, save_snapshot_batch, log_crawl
from app.crawlers.steam_crawler import SteamCrawler
from app.crawlers.app_store_crawler import AppStoreCrawler
from app.crawlers.google_play_crawler import GooglePlayCrawler
from app.crawlers.mobile_radar_crawler import MobileRadarCrawler
from app.config import SUPPORTED_COUNTRIES

logger = logging.getLogger(__name__)

# iTunes RSS has no worldwide chart: requesting it always returns 0 entries.
APP_STORE_UNSUPPORTED_COUNTRIES = {"global"}

class CrawlerOrchestrator:
    def __init__(self):
        self.steam_crawler = SteamCrawler()
        self.app_store_crawler = AppStoreCrawler()
        self.google_play_crawler = GooglePlayCrawler()
        self.mobile_radar_crawler = MobileRadarCrawler()

    def calculate_deltas(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates DoD (Day-over-Day) and WoW (Week-over-Week) rank changes.
        Positive value (+X): climbed X ranks.
        Negative value (-X): dropped X ranks.

        Runs a fixed number of queries per chart (platform/country/ranking_type)
        instead of 2-3 queries per game.
        """
        if not records:
            return records

        charts: Dict[tuple, List[Dict[str, Any]]] = {}
        for rec in records:
            key = (rec["platform"], rec["country"], rec["ranking_type"], rec.get("snapshot_date") or date.today().isoformat())
            charts.setdefault(key, []).append(rec)

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            for (platform, country, ranking_type, snap_date), chart_recs in charts.items():
                today = date.fromisoformat(snap_date)
                last_week_str = (today - timedelta(days=7)).isoformat()
                chart_args = (platform, country, ranking_type)

                # Most recent earlier snapshot date *for this chart*
                cursor.execute("""
                    SELECT MAX(snapshot_date) AS d FROM snapshots
                    WHERE platform = ? AND country = ? AND ranking_type = ? AND snapshot_date < ?
                """, (*chart_args, snap_date))
                row = cursor.fetchone()
                prev_date_str = row["d"] if row and row["d"] else None

                def ranks_on(day: Optional[str]) -> Dict[str, int]:
                    if not day:
                        return {}
                    cursor.execute("""
                        SELECT game_id, MIN(rank) AS rank FROM snapshots
                        WHERE platform = ? AND country = ? AND ranking_type = ? AND snapshot_date = ?
                        GROUP BY game_id
                    """, (*chart_args, day))
                    return {r["game_id"]: r["rank"] for r in cursor.fetchall()}

                prev_ranks = ranks_on(prev_date_str)
                week_ranks = ranks_on(last_week_str)

                game_ids = [r["game_id"] for r in chart_recs]
                placeholders = ",".join("?" * len(game_ids))
                cursor.execute(f"""
                    SELECT DISTINCT game_id FROM snapshots
                    WHERE platform = ? AND country = ? AND ranking_type = ? AND snapshot_date < ?
                      AND game_id IN ({placeholders})
                """, (*chart_args, snap_date, *game_ids))
                seen_before = {r["game_id"] for r in cursor.fetchall()}

                for rec in chart_recs:
                    gid = rec["game_id"]
                    cur = rec["rank"]
                    if gid in prev_ranks:
                        rec["rank_change_day"] = prev_ranks[gid] - cur
                        rec["is_new_entry"] = 0
                    else:
                        rec["rank_change_day"] = 0
                        rec["is_new_entry"] = 0 if gid in seen_before else 1
                    rec["rank_change_week"] = week_ranks[gid] - cur if gid in week_ranks else 0
        finally:
            conn.close()
        return records

    def _save_batch(self, records: List[Dict[str, Any]], platform: str, country: str, ranking_type: str) -> int:
        """Computes deltas, saves and logs one chart. Empty results are logged as failures
        (crawlers swallow their own errors) so they surface in the data-health view."""
        if not records:
            log_crawl(platform, country, ranking_type, 0, "failed", "Crawler returned 0 records")
            return 0
        processed = self.calculate_deltas(records)
        save_snapshot_batch(processed)
        log_crawl(platform, country, ranking_type, len(processed), "success")
        return len(processed)

    def crawl_steam(self) -> int:
        """Crawls Steam PC most played and top sellers."""
        total = 0
        try:
            total += self._save_batch(self.steam_crawler.fetch_most_played(limit=50), "pc_steam", "global", "most_played")
            total += self._save_batch(self.steam_crawler.fetch_top_sellers(limit=50), "pc_steam", "global", "top_sellers")
        except Exception as e:
            logger.error(f"Error in Steam crawl: {e}")
            log_crawl("pc_steam", "global", "all", 0, "failed", str(e))
        return total

    def crawl_mobile(self, countries: Optional[List[str]] = None) -> int:
        """Crawls App Store and Google Play for specified or top countries."""
        if not countries:
            countries = ["us", "vn", "kr", "jp", "gb", "global"]

        total = 0
        for country in countries:
            # 1. App Store (Apple publishes per-country charts only; there is no "global" feed)
            app_store_types = [] if country.lower() in APP_STORE_UNSUPPORTED_COUNTRIES else ["top_grossing", "top_free"]
            for r_type in app_store_types:
                try:
                    records = self.app_store_crawler.fetch_rankings(country=country, ranking_type=r_type, limit=50)
                    total += self._save_batch(records, "mobile_appstore", country, r_type)
                except Exception as e:
                    logger.error(f"Error crawling App Store for {country} {r_type}: {e}")
                    log_crawl("mobile_appstore", country, r_type, 0, "failed", str(e))

            # 2. Google Play
            for r_type in ["top_free", "top_grossing"]:
                try:
                    records = self.google_play_crawler.fetch_rankings(country=country, ranking_type=r_type, limit=30)
                    total += self._save_batch(records, "mobile_googleplay", country, r_type)
                except Exception as e:
                    logger.error(f"Error crawling Google Play for {country} {r_type}: {e}")
                    log_crawl("mobile_googleplay", country, r_type, 0, "failed", str(e))

        return total

    def run_full_crawl(self, countries: Optional[List[str]] = None) -> Dict[str, Any]:
        """Triggers a full crawl for all platforms, updates mobile radar and saves to DB."""
        steam_count = self.crawl_steam()
        mobile_count = self.crawl_mobile(countries=countries)
        
        radar_result = {}
        try:
            radar_result = self.mobile_radar_crawler.run_radar_update()
        except Exception as e:
            logger.error(f"Error running mobile radar crawl: {e}")

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "steam_items_crawled": steam_count,
            "mobile_items_crawled": mobile_count,
            "upcoming_mobile_radar": radar_result,
            "total_items": steam_count + mobile_count
        }
