"""Apple App Store Data Crawler for Mobile Market Analytics."""

import logging
from typing import List, Dict, Any
from datetime import datetime, date
import httpx

logger = logging.getLogger(__name__)

class AppStoreCrawler:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_rankings(self, country: str = "us", ranking_type: str = "top_grossing", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetches mobile game rankings from Apple App Store RSS API.
        ranking_type: 'top_grossing', 'top_free', or 'top_paid'
        country: 2-letter ISO code (e.g., 'us', 'vn', 'kr', 'jp', 'gb')
        """
        # Map internal ranking_type to iTunes RSS path
        type_mapping = {
            "top_grossing": "topgrossingapplications",
            "top_free": "topfreeapplications",
            "top_paid": "toppaidapplications"
        }
        api_type = type_mapping.get(ranking_type, "topgrossingapplications")
        
        # Genre 6014 is Mobile Games in Apple iTunes catalog
        url = f"https://itunes.apple.com/{country.lower()}/rss/{api_type}/limit={limit}/genre=6014/json"
        
        records = []
        today_str = date.today().isoformat()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        week_str = datetime.now().strftime("%Y-W%W")

        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    entries = data.get("feed", {}).get("entry", [])
                    
                    # If only 1 entry is returned, iTunes might return a dict instead of a list
                    if isinstance(entries, dict):
                        entries = [entries]

                    for rank, entry in enumerate(entries, start=1):
                        app_id = entry.get("id", {}).get("attributes", {}).get("im:id", "")
                        title = entry.get("im:name", {}).get("label", "Unknown Game")
                        developer = entry.get("im:artist", {}).get("label", "Unknown Developer")
                        genre = entry.get("category", {}).get("attributes", {}).get("label", "Mobile Game")
                        
                        price_info = entry.get("im:price", {})
                        price_amount = price_info.get("attributes", {}).get("amount", "0") if isinstance(price_info, dict) else "0"
                        currency = price_info.get("attributes", {}).get("currency", "USD") if isinstance(price_info, dict) else "USD"
                        price = "Free" if price_amount in ["0", "0.00000", "0.0"] else f"{price_amount} {currency}"
                        
                        images = entry.get("im:image", [])
                        icon_url = images[-1].get("label") if isinstance(images, list) and images else ""
                        
                        # Fix: link can be a list or a dict
                        link_data = entry.get("link")
                        store_url = ""
                        if isinstance(link_data, list) and link_data:
                            store_url = link_data[0].get("attributes", {}).get("href", "")
                        elif isinstance(link_data, dict):
                            store_url = link_data.get("attributes", {}).get("href", "")
                        
                        if not store_url:
                            store_url = f"https://apps.apple.com/app/id{app_id}"

                        records.append({
                            "snapshot_date": today_str,
                            "snapshot_time": now_str,
                            "period_type": "daily",
                            "week_number": week_str,
                            "platform": "mobile_appstore",
                            "country": country.lower(),
                            "ranking_type": ranking_type,
                            "rank": rank,
                            "game_id": f"ios_{app_id}",
                            "title": title,
                            "developer": developer,
                            "genre": genre,
                            "score": 4.6,  # Default App Store baseline score
                            "price": price,
                            "player_count": 0,
                            "estimated_downloads": f"Rank #{rank} on App Store",
                            "icon_url": icon_url,
                            "store_url": store_url,
                            "rank_change_day": 0,
                            "rank_change_week": 0,
                            "is_new_entry": 0
                        })
                else:
                    logger.warning(f"App Store returned status {resp.status_code} for {country} {ranking_type}")
        except Exception as e:
            logger.error(f"Error fetching App Store rankings for {country}: {e}")

        return records
