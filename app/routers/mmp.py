"""MMP postback webhook ingestion and fraud stream."""

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
    bot_service,
    mmp_engine,
)

router = APIRouter()


# --- Live MMP Webhook Ingestion Engine & Real-Time Fraud Stream Endpoints ---
@router.post("/api/webhook/mmp/postback")
async def receive_mmp_postback_api(request: Request):
    """Real-time webhook receiver for AppsFlyer, Adjust, Singular, and custom attribution postbacks."""
    payload = await request.json()
    result = mmp_engine.ingest_postback(payload)
    # Check if this single postback or rolling traffic needs instant alert
    if result.get("is_rejected") == 1 and result.get("fraud_score", 0) > 85:
        # Trigger background webhook bot alert if enabled
        bot_service.trigger_fraud_alert(
            network_name=result["network_name"],
            fraud_rate=result["fraud_score"],
            fraud_type=result["fraud_verdict"],
            details=f"IP: {result.get('ip_address')}, Device: {result.get('device_model')}, CTIT: {result.get('ctit_seconds')}s"
        )
    return {"status": "success", "processed_event": result}

@router.get("/api/webhook/mmp/recent")
async def get_recent_mmp_postbacks_api(limit: int = Query(default=50, ge=1, le=200)):
    """Returns most recent incoming attribution postbacks."""
    return mmp_engine.get_recent_postbacks(limit=limit)

@router.get("/api/webhook/mmp/stats")
async def get_mmp_stats_api():
    """Returns aggregated real-time MMP attribution & fraud statistics."""
    return mmp_engine.get_mmp_stats()

@router.post("/api/webhook/mmp/simulate")
async def simulate_mmp_batch_api(request: Request):
    """Simulates realistic incoming MMP stream (Clean vs Fraudulent networks)."""
    payload = await request.json()
    count = int(payload.get("count", 15))
    batch = mmp_engine.generate_mock_batch(count=count)
    return {"status": "success", "generated_count": len(batch), "events": batch}

@router.delete("/api/webhook/mmp/clear")
async def clear_mmp_postbacks_api():
    """Clears MMP postbacks database table for demo reset."""
    deleted = mmp_engine.clear_postbacks()
    return {"status": "success", "deleted_rows": deleted}
