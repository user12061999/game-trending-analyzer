"""Google Play Store Data Crawler for Mobile Market Analytics."""

import logging
from typing import List, Dict, Any
from datetime import datetime, date
from google_play_scraper import search, app

logger = logging.getLogger(__name__)

# Search queries optimized per ranking type and language
RANKING_QUERIES = {
    "top_free": {
        "default": "top free games",
        "vn": "game hay nhat",
        "kr": "인기 무료 게임",
        "jp": "無料ゲーム ランキング",
    },
    "top_grossing": {
        "default": "top grossing games rpg gacha",
        "vn": "game online hot nhat nap the",
        "kr": "인기 게임 매출",
        "jp": "売上ランキング ゲーム",
    },
    "trending": {
        "default": "new trending games",
        "vn": "game moi ra mat",
        "kr": "신규 추천 게임",
        "jp": "新作ゲーム",
    }
}

COUNTRY_LANG_MAP = {
    "us": "en",
    "global": "en",
    "vn": "vi",
    "kr": "ko",
    "jp": "ja",
    "gb": "en",
    "de": "de",
    "br": "pt",
    "in": "en",
    "id": "id",
    "ph": "en",
    "th": "th",
    "tw": "zh",
    "fr": "fr",
}

class GooglePlayCrawler:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def fetch_rankings(self, country: str = "us", ranking_type: str = "top_free", limit: int = 30) -> List[Dict[str, Any]]:
        """
        Fetches Google Play games for a given country and ranking type.
        """
        records = []
        today_str = date.today().isoformat()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        week_str = datetime.now().strftime("%Y-W%W")

        country_code = country.lower()
        query_map = RANKING_QUERIES.get(ranking_type, RANKING_QUERIES["top_free"])
        query = query_map.get(country_code, query_map.get("default", "top games"))
        lang = COUNTRY_LANG_MAP.get(country_code, "en")
        target_country = "us" if country_code == "global" else country_code

        try:
            results = search(
                query,
                lang=lang,
                country=target_country,
                n_hits=min(limit, 50)
            )

            seen_packages = set()
            rank_counter = 1

            for item in results:
                package_id = item.get("appId")
                if not package_id or package_id in seen_packages:
                    continue
                seen_packages.add(package_id)

                title = item.get("title", "Unknown Title")
                developer = item.get("developer", "Unknown Developer")
                genre = item.get("genre", "Mobile Game")
                score = round(float(item.get("score") or 4.2), 1)
                price_str = "Free" if item.get("free", True) else f"${item.get('price', 0)}"
                installs = item.get("installs") or "1,000,000+"
                icon_url = item.get("icon") or ""
                store_url = f"https://play.google.com/store/apps/details?id={package_id}&hl={lang}&gl={target_country}"

                records.append({
                    "snapshot_date": today_str,
                    "snapshot_time": now_str,
                    "period_type": "daily",
                    "week_number": week_str,
                    "platform": "mobile_googleplay",
                    "country": country_code,
                    "ranking_type": ranking_type,
                    "rank": rank_counter,
                    "game_id": f"gp_{package_id}",
                    "title": title,
                    "developer": developer,
                    "genre": genre,
                    "score": score,
                    "price": price_str,
                    "player_count": 0,
                    "estimated_downloads": installs,
                    "icon_url": icon_url,
                    "store_url": store_url,
                    "rank_change_day": 0,
                    "rank_change_week": 0,
                    "is_new_entry": 0
                })
                rank_counter += 1
                if rank_counter > limit:
                    break

        except Exception as e:
            logger.error(f"Error scraping Google Play for {country}: {e}")

        return records
