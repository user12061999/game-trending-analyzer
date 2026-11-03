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
        """
        if not records:
            return records

        conn = get_db_connection()
        cursor = conn.cursor()

        today = date.today()
        yesterday_str = (today - timedelta(days=1)).isoformat()
        last_week_str = (today - timedelta(days=7)).isoformat()

        for rec in records:
            platform = rec["platform"]
            country = rec["country"]
            ranking_type = rec["ranking_type"]
            game_id = rec["game_id"]
            current_rank = rec["rank"]

            # 1. Day-over-Day delta
            cursor.execute("""
            SELECT rank FROM snapshots
            WHERE snapshot_date = ? AND platform = ? AND country = ? AND ranking_type = ? AND game_id = ?
            LIMIT 1
            """, (yesterday_str, platform, country, ranking_type, game_id))
            row_yesterday = cursor.fetchone()

            if row_yesterday:
                old_rank = row_yesterday["rank"]
                rec["rank_change_day"] = old_rank - current_rank
                rec["is_new_entry"] = 0
            else:
                # Check if it ever existed before
                cursor.execute("""
                SELECT 1 FROM snapshots
                WHERE platform = ? AND country = ? AND ranking_type = ? AND game_id = ?
                LIMIT 1
                """, (platform, country, ranking_type, game_id))
                ever_existed = cursor.fetchone()
                rec["rank_change_day"] = 0
                rec["is_new_entry"] = 0 if ever_existed else 1

            # 2. Week-over-Week delta
            cursor.execute("""
            SELECT rank FROM snapshots
            WHERE snapshot_date = ? AND platform = ? AND country = ? AND ranking_type = ? AND game_id = ?
            LIMIT 1
            """, (last_week_str, platform, country, ranking_type, game_id))
            row_last_week = cursor.fetchone()

            if row_last_week:
                old_rank_week = row_last_week["rank"]
                rec["rank_change_week"] = old_rank_week - current_rank
            else:
                rec["rank_change_week"] = 0

        conn.close()
        return records

    def crawl_steam(self) -> int:
        """Crawls Steam PC most played and top sellers."""
        total = 0
        try:
            most_played = self.steam_crawler.fetch_most_played(limit=50)
            if most_played:
                processed = self.calculate_deltas(most_played)
                save_snapshot_batch(processed)
                log_crawl("pc_steam", "global", "most_played", len(processed), "success")
                total += len(processed)

            top_sellers = self.steam_crawler.fetch_top_sellers(limit=50)
            if top_sellers:
                processed = self.calculate_deltas(top_sellers)
                save_snapshot_batch(processed)
                log_crawl("pc_steam", "global", "top_sellers", len(processed), "success")
                total += len(processed)
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
            # 1. App Store
            for r_type in ["top_grossing", "top_free"]:
                try:
                    records = self.app_store_crawler.fetch_rankings(country=country, ranking_type=r_type, limit=50)
                    if records:
                        processed = self.calculate_deltas(records)
                        save_snapshot_batch(processed)
                        log_crawl("mobile_appstore", country, r_type, len(processed), "success")
                        total += len(processed)
                except Exception as e:
                    logger.error(f"Error crawling App Store for {country} {r_type}: {e}")
                    log_crawl("mobile_appstore", country, r_type, 0, "failed", str(e))

            # 2. Google Play
            for r_type in ["top_free", "top_grossing"]:
                try:
                    records = self.google_play_crawler.fetch_rankings(country=country, ranking_type=r_type, limit=30)
                    if records:
                        processed = self.calculate_deltas(records)
                        save_snapshot_batch(processed)
                        log_crawl("mobile_googleplay", country, r_type, len(processed), "success")
                        total += len(processed)
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
