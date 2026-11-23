"""Alert channels and AI (Gemini) configuration."""

from typing import Optional, List
from datetime import date, datetime

from fastapi import APIRouter, Query, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse, Response, JSONResponse

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
    analyzer,
    notifier,
    ai_analyst,
)

router = APIRouter()


# --- Notification & Alert Endpoints ---
@router.get("/api/alerts/config")
async def get_alert_config():
    return notifier.get_config()

@router.post("/api/alerts/config")
async def update_alert_config(request: Request):
    payload = await request.json()
    return notifier.save_config(payload)

@router.post("/api/alerts/test")
async def test_alert():
    return notifier.send_test_alert()

@router.post("/api/alerts/digest")
async def send_manual_digest(target_date: Optional[str] = None):
    return notifier.dispatch_daily_digest(target_date=target_date)

@router.get("/api/alerts/history")
async def get_alert_history(limit: int = Query(30, ge=1, le=200)):
    from app.notifications.alert_engine import AlertEngine
    return AlertEngine.recent_alerts(limit=limit)

@router.post("/api/alerts/weekly")
async def send_weekly_digest_now():
    """Sends the weekly genre digest now (ignores weekday / once-a-week rule)."""
    from app.notifications.alert_engine import AlertEngine
    engine = AlertEngine(notifier, analyzer)
    return engine.send_weekly_digest(notifier.get_config(), force=True)

@router.post("/api/alerts/run-checks")
async def run_alert_checks_now():
    """Runs every alert check now, with the normal dedup rules (nothing is re-sent)."""
    from app.notifications.alert_engine import AlertEngine
    return AlertEngine(notifier, analyzer).run_after_crawl(crawl_ok=True)

# --- AI Game Deconstruction Endpoints ---
@router.post("/api/ai/analyze")
async def analyze_game_ai(request: Request):
    payload = await request.json()
    game_id = payload.get("game_id")
    custom_key = payload.get("api_key")
    if not game_id:
        return {"error": "Thiếu game_id"}
    details = analyzer.get_game_details(game_id)
    if not details or not details.get("game"):
        return {"error": "Không tìm thấy dữ liệu tựa game"}
    return ai_analyst.analyze_game(game_data=details["game"], custom_api_key=custom_key)

@router.get("/api/ai/config")
async def get_ai_config():
    key = ai_analyst.get_api_key()
    return {
        "has_gemini_key": bool(key),
        "masked_key": f"{key[:6]}...{key[-4:]}" if len(key) > 10 else ("Configured" if key else "")
    }

@router.post("/api/ai/config")
async def save_ai_config(request: Request):
    payload = await request.json()
    key = payload.get("gemini_api_key", "").strip()
    ai_analyst.save_api_key(key)
    return {"status": "success", "has_gemini_key": bool(key)}


# --- Revenue model calibration (real revenue figures entered by the user) ---
@router.get("/api/calibration")
async def get_calibration_api():
    from app.analytics import calibration
    return calibration.get_report()


@router.post("/api/calibration")
async def add_calibration_point_api(payload: dict):
    from app.analytics import calibration
    try:
        res = calibration.add_point(payload)
    except (ValueError, TypeError) as e:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})
    return {"status": "success", **res, "report": calibration.get_report()}


@router.delete("/api/calibration/{point_id}")
async def delete_calibration_point_api(point_id: int):
    from app.analytics import calibration
    deleted = calibration.delete_point(point_id)
    return {"status": "success" if deleted else "not_found", "report": calibration.get_report()}
