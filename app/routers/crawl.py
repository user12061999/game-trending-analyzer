"""Crawl trigger and status."""

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
    crawl_service,
)

router = APIRouter()


@router.post("/api/crawl")
async def trigger_crawl(countries: Optional[str] = None):
    country_list = [c.strip() for c in countries.split(",") if c.strip()] if countries else DEFAULT_CRAWL_COUNTRIES
    if not crawl_service.run_crawl_async(countries=country_list, reason="manual"):
        return {"status": "busy", "message": "Một tác vụ crawl đang chạy trong nền, vui lòng đợi."}
    return {"status": "started", "message": f"Đang bắt đầu crawl dữ liệu cho: {', '.join(country_list)}"}

@router.get("/api/crawl/status")
async def get_crawl_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crawl_history ORDER BY id DESC LIMIT 15")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "is_crawling": crawl_service.is_crawling,
        "last_run": crawl_service.last_run,
        "next_scheduled_run": crawl_service.next_scheduled_run(),
        "recent_logs": logs
    }
