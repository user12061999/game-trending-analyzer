"""Watchlist and upcoming-games radar."""

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
    orchestrator,
    analyzer,
    notifier,
)

router = APIRouter()


# --- Watchlist & Rival Tracker Endpoints ---
@router.get("/api/watchlist")
async def get_watchlist_api():
    return analyzer.get_watchlist_dashboard_data()

@router.post("/api/watchlist")
async def add_watchlist_api(request: Request):
    payload = await request.json()
    game_id = payload.get("game_id")
    notes = payload.get("notes", "")
    is_rival = int(payload.get("is_rival", 0))

    if not game_id:
        return {"error": "Thiếu game_id"}

    details = analyzer.get_game_details(game_id)
    if not details or not details.get("game"):
        return {"error": "Không tìm thấy tựa game này"}

    g = details["game"]
    add_to_watchlist(
        game_id=game_id,
        title=g.get("title", ""),
        developer=g.get("developer", ""),
        platform=g.get("platform", ""),
        country=g.get("country", ""),
        genre=g.get("genre", ""),
        icon_url=g.get("icon_url", ""),
        store_url=g.get("store_url", ""),
        notes=notes,
        is_rival=is_rival
    )
    return {"status": "success", "message": f"Đã thêm {g.get('title')} vào danh sách theo dõi", "is_in_watchlist": True}

# --- Mobile Upcoming & Pre-registration Radar Endpoints ---
@router.get("/api/radar/upcoming")
async def get_upcoming_radar(
    region: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    threat_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    games = get_upcoming_mobile_games(region=region, genre=genre, threat_level=threat_level, search=search)
    return {"games": games, "total": len(games)}

@router.get("/api/radar/stats")
async def get_radar_stats():
    return get_radar_threat_stats()

@router.post("/api/radar/refresh")
async def refresh_radar_data():
    res = orchestrator.mobile_radar_crawler.run_radar_update()
    return {"status": "success", "result": res}

@router.delete("/api/watchlist/{game_id}")
async def remove_watchlist_api(game_id: str):
    remove_from_watchlist(game_id)
    return {"status": "success", "message": "Đã xóa khỏi danh sách theo dõi", "is_in_watchlist": False}

@router.get("/api/watchlist/check/{game_id}")
async def check_watchlist_api(game_id: str):
    return {"game_id": game_id, "in_watchlist": is_game_in_watchlist(game_id)}

@router.get("/api/radar/game/{game_id}")
async def get_radar_game(game_id: int):
    game = get_upcoming_game_by_id(game_id)
    if not game:
        return {"error": "Không tìm thấy game trong radar"}
    return game

@router.post("/api/radar/track/{game_id}")
async def track_radar_game(game_id: int):
    is_tracked = toggle_track_upcoming_game(game_id)
    return {"status": "success", "game_id": game_id, "is_tracked": is_tracked}

@router.post("/api/radar/alert-test/{game_id}")
async def send_radar_alert_test(game_id: int):
    game = get_upcoming_game_by_id(game_id)
    if not game:
        return {"error": "Không tìm thấy game"}
    sent = notifier.dispatch_radar_threat_alert(game)
    return {"status": "success", "alert_dispatched": sent}
