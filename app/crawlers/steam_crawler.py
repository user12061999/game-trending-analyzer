"""Steam Data Crawler for PC Market Analytics."""

import logging
from typing import List, Dict, Any
from datetime import datetime, date
import httpx

logger = logging.getLogger(__name__)

STEAM_CHARTS_URL = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
STEAM_SPY_TOP_2WEEKS = "https://steamspy.com/api.php?request=top100in2weeks"
STEAM_SPY_APPDETAILS = "https://steamspy.com/api.php?request=appdetails&appid="

# Pre-populated dictionary for popular titles to minimize API requests and ensure zero delay
KNOWN_STEAM_GAMES = {
    "730": {"title": "Counter-Strike 2", "developer": "Valve", "genre": "FPS / Action", "price": "Free"},
    "570": {"title": "Dota 2", "developer": "Valve", "genre": "MOBA / Strategy", "price": "Free"},
    "578080": {"title": "PUBG: BATTLEGROUNDS", "developer": "KRAFTON", "genre": "Battle Royale", "price": "Free"},
    "1172470": {"title": "Apex Legends", "developer": "Respawn Entertainment", "genre": "Hero Shooter", "price": "Free"},
    "271590": {"title": "Grand Theft Auto V", "developer": "Rockstar North", "genre": "Open World / Action", "price": "$29.99"},
    "252490": {"title": "Rust", "developer": "Facepunch Studios", "genre": "Survival", "price": "$39.99"},
    "1086940": {"title": "Baldur's Gate 3", "developer": "Larian Studios", "genre": "RPG", "price": "$59.99"},
    "1245620": {"title": "ELDEN RING", "developer": "FromSoftware Inc.", "genre": "Souls-like / Action RPG", "price": "$59.99"},
    "2358720": {"title": "Black Myth: Wukong", "developer": "Game Science", "genre": "Action RPG", "price": "$59.99"},
    "1623730": {"title": "Palworld", "developer": "Pocketpair", "genre": "Open World / Survival", "price": "$29.99"},
    "440": {"title": "Team Fortress 2", "developer": "Valve", "genre": "FPS", "price": "Free"},
    "105600": {"title": "Terraria", "developer": "Re-Logic", "genre": "Sandbox / Survival", "price": "$9.99"},
    "230410": {"title": "Warframe", "developer": "Digital Extremes", "genre": "Action / RPG", "price": "Free"},
    "1938090": {"title": "Call of Duty: Warzone", "developer": "Infinity Ward", "genre": "Action / FPS", "price": "Free"},
    "2195250": {"title": "EA SPORTS FC™ 25", "developer": "EA Canada", "genre": "Sports", "price": "$69.99"},
    "221100": {"title": "DayZ", "developer": "Bohemia Interactive", "genre": "Survival", "price": "$44.99"},
    "359550": {"title": "Tom Clancy's Rainbow Six Siege", "developer": "Ubisoft", "genre": "Tactical Shooter", "price": "$19.99"},
    "892970": {"title": "Valheim", "developer": "Iron Gate AB", "genre": "Survival RPG", "price": "$19.99"},
    "553850": {"title": "HELLDIVERS™ 2", "developer": "Arrowhead Game Studios", "genre": "Co-op Shooter", "price": "$39.99"},
    "289070": {"title": "Sid Meier's Civilization VI", "developer": "Firaxis Games", "genre": "Strategy / 4X", "price": "$59.99"},
    "1091500": {"title": "Cyberpunk 2077", "developer": "CD PROJEKT RED", "genre": "Open World RPG", "price": "$59.99"},
    "292030": {"title": "The Witcher 3: Wild Hunt", "developer": "CD PROJEKT RED", "genre": "RPG", "price": "$39.99"},
}

class SteamCrawler:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_steamspy_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Fetches top games metadata from SteamSpy for lookup of titles and tags."""
        lookup = dict(KNOWN_STEAM_GAMES)
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                resp = client.get(STEAM_SPY_TOP_2WEEKS)
                if resp.status_code == 200:
                    data = resp.json()
                    for appid, item in data.items():
                        lookup[str(appid)] = {
                            "title": item.get("name"),
                            "developer": item.get("developer"),
                            "genre": item.get("genre", "Action / PC Game"),
                            "price": f"${int(item.get('price', 0)) / 100:.2f}" if item.get("price") else "Free",
                            "score": round(float(item.get("positive", 0)) / max(1, item.get("positive", 0) + item.get("negative", 0)) * 5.0, 1),
                            "estimated_downloads": f"{item.get('owners', 'Unknown')} owners",
                            "ccu": item.get("ccu", 0)
                        }
        except Exception as e:
            logger.warning(f"Error fetching SteamSpy metadata: {e}")
        return lookup

    def fetch_most_played(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches top PC games by concurrent players (CCU) from Steam official charts."""
        records = []
        today_str = date.today().isoformat()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        week_str = datetime.now().strftime("%Y-W%W")

        # Fetch steamspy metadata for titles / developer info
        metadata_map = self.fetch_steamspy_metadata()

        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                resp = client.get(STEAM_CHARTS_URL)
                if resp.status_code == 200:
                    data = resp.json().get("response", {})
                    ranks = data.get("ranks", [])[:limit]
                    
                    for item in ranks:
                        rank = item.get("rank")
                        appid = str(item.get("appid"))
                        ccu = item.get("concurrent_in_game", 0)
                        peak = item.get("peak_in_game", 0)

                        meta = metadata_map.get(appid, {})
                        title = meta.get("title") or KNKNOWN_NAME(appid) or f"Steam App {appid}"
                        developer = meta.get("developer") or "Steam Creator"
                        genre = meta.get("genre") or "PC Game"
                        price = meta.get("price") or "Free to Play"
                        score = meta.get("score") or 4.5
                        downloads = meta.get("estimated_downloads") or f"{peak:,} peak CCU"

                        icon_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
                        store_url = f"https://store.steampowered.com/app/{appid}"

                        records.append({
                            "snapshot_date": today_str,
                            "snapshot_time": now_str,
                            "period_type": "daily",
                            "week_number": week_str,
                            "platform": "pc_steam",
                            "country": "global",
                            "ranking_type": "most_played",
                            "rank": rank,
                            "game_id": appid,
                            "title": title,
                            "developer": developer,
                            "genre": genre,
                            "score": score,
                            "price": price,
                            "player_count": ccu,
                            "estimated_downloads": downloads,
                            "icon_url": icon_url,
                            "store_url": store_url,
                            "rank_change_day": 0,
                            "rank_change_week": 0,
                            "is_new_entry": 0
                        })
        except Exception as e:
            logger.error(f"Error fetching Steam Most Played: {e}")

        return records

    def fetch_top_sellers(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches top PC games by player activity and trending popularity."""
        records = []
        today_str = date.today().isoformat()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        week_str = datetime.now().strftime("%Y-W%W")

        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                resp = client.get(STEAM_SPY_TOP_2WEEKS)
                if resp.status_code == 200:
                    data = resp.json()
                    items = list(data.values())[:limit]
                    for rank, item in enumerate(items, start=1):
                        appid = str(item.get("appid"))
                        title = item.get("name", f"Game {appid}")
                        developer = item.get("developer", "PC Studio")
                        genre = item.get("genre", "Action / Strategy")
                        price = f"${int(item.get('price', 0)) / 100:.2f}" if item.get("price") else "Free"
                        score = round(float(item.get("positive", 0)) / max(1, item.get("positive", 0) + item.get("negative", 0)) * 5.0, 1)

                        records.append({
                            "snapshot_date": today_str,
                            "snapshot_time": now_str,
                            "period_type": "daily",
                            "week_number": week_str,
                            "platform": "pc_steam",
                            "country": "global",
                            "ranking_type": "top_sellers",
                            "rank": rank,
                            "game_id": appid,
                            "title": title,
                            "developer": developer,
                            "genre": genre,
                            "score": score,
                            "price": price,
                            "player_count": item.get("ccu", 0),
                            "estimated_downloads": f"{item.get('owners', 'Unknown')} owners",
                            "icon_url": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
                            "store_url": f"https://store.steampowered.com/app/{appid}",
                            "rank_change_day": 0,
                            "rank_change_week": 0,
                            "is_new_entry": 0
                        })
        except Exception as e:
            logger.error(f"Error fetching Steam Top Sellers: {e}")

        return records

def KNKNOWN_NAME(appid: str) -> str:
    return KNOWN_STEAM_GAMES.get(appid, {}).get("title", "")
