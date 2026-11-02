"""Configuration and constants for Game Market Trending Analyzer."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "game_trends.db"

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
