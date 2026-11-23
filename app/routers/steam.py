"""Steam Web API direct sync."""

from typing import Optional, List
from datetime import date, datetime

from fastapi import APIRouter, Query, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse, Response

from app.config import SUPPORTED_COUNTRIES, PLATFORMS, RANKING_TYPES, BASE_DIR, DEFAULT_CRAWL_COUNTRIES
from app.database.db import (
    get_db_connection,
    add_to_watchlist,
    remove_from_watchlist,
    is_game_in_watchlist,
    get_upcoming_mobile_games,
    get_upcoming_game_by_id,
    toggle_track_upcoming_game,
    get_radar_threat_stats,
)
from app.services.container import (
    steam_connector,
)

router = APIRouter()


# --- Steam Web API & Storefront Connector Endpoints ---
@router.get("/api/steam/presets")
async def get_steam_presets_api():
    """Returns benchmark popular Steam titles for live lookups."""
    return steam_connector.get_presets()

@router.post("/api/steam/configure-key")
async def configure_steam_key_api(request: Request):
    """Saves user Steam Web API key."""
    payload = await request.json()
    key = payload.get("steam_api_key", "")
    steam_connector.save_api_key(key)
    return {"status": "success", "message": "Steam API Key đã được lưu thành công!"}

@router.get("/api/steam/app/{app_id}")
async def get_steam_live_app_api(app_id: int):
    """Fetches live CCU, Storefront details, and reviews summary from Steam."""
    ccu_data = steam_connector.fetch_live_ccu(app_id)
    details_data = steam_connector.fetch_app_details(app_id)
    reviews_data = steam_connector.fetch_reviews_summary(app_id)
    return {
        "app_id": app_id,
        "ccu": ccu_data,
        "details": details_data,
        "reviews": reviews_data
    }
