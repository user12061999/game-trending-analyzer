"""Configuration and constants for Game Market Trending Analyzer."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "game_trends.db"


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (KEY=VALUE per line). Real environment variables win."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(BASE_DIR / ".env")

# Secrets / AI settings (set in .env — see .env.example)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
STEAM_API_KEY = os.getenv("STEAM_API_KEY", "").strip()

# Scheduler settings
DAILY_CRAWL_HOUR = int(os.getenv("DAILY_CRAWL_HOUR", "6"))
DAILY_CRAWL_MINUTE = int(os.getenv("DAILY_CRAWL_MINUTE", "0"))
DEFAULT_CRAWL_COUNTRIES = [
    c.strip() for c in os.getenv("CRAWL_COUNTRIES", "us,vn,kr,jp,global").split(",") if c.strip()
]

# Server Network Settings
PORT = int(os.getenv("PORT", "8888"))
HOST = os.getenv("HOST", "127.0.0.1")

# Supported target countries for mobile markets
SUPPORTED_COUNTRIES = [
    {"code": "global", "name": "Global / Worldwide", "flag": "🌐"},
    {"code": "us", "name": "United States", "flag": "🇺🇸"},
    {"code": "vn", "name": "Vietnam", "flag": "🇻🇳"},
    {"code": "kr", "name": "South Korea", "flag": "🇰🇷"},
    {"code": "jp", "name": "Japan", "flag": "🇯🇵"},
    {"code": "gb", "name": "United Kingdom", "flag": "🇬🇧"},
    {"code": "de", "name": "Germany", "flag": "🇩🇪"},
    {"code": "br", "name": "Brazil", "flag": "🇧🇷"},
    {"code": "in", "name": "India", "flag": "🇮🇳"},
    {"code": "id", "name": "Indonesia", "flag": "🇮🇩"},
    {"code": "ph", "name": "Philippines", "flag": "🇵🇭"},
    {"code": "th", "name": "Thailand", "flag": "🇹🇭"},
    {"code": "tw", "name": "Taiwan", "flag": "🇹🇼"},
    {"code": "fr", "name": "France", "flag": "🇫🇷"},
]

# Supported platform choices
PLATFORMS = [
    {"id": "all", "name": "All Platforms"},
    {"id": "pc", "name": "PC (Steam)"},
    {"id": "mobile", "name": "Mobile (Google Play & App Store)"},
]

# Rankings types
RANKING_TYPES = [
    {"id": "top_grossing", "name": "Top Grossing (Doanh thu)"},
    {"id": "top_free", "name": "Top Free (Lượt tải)"},
    {"id": "most_played", "name": "Most Played (CCU - Số người chơi)"},
    {"id": "top_sellers", "name": "Top Sellers (PC)"},
    {"id": "breakouts", "name": "Breakout / Rising (Tăng vọt)"},
]
