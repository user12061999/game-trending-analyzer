"""Market data: dashboard page, rankings, game details, reports, exports, market signals."""

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
    analyzer,
    report_generator,
)

from app.analytics.market_signals import MarketSignals
from app.analytics.revenue_history_engine import RevenueHistoryEngine

router = APIRouter()

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


# --- Web UI Route ---
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    latest_date = analyzer.get_latest_snapshot_date()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "latest_date": latest_date,
        "supported_countries": SUPPORTED_COUNTRIES,
        "platforms": PLATFORMS,
        "ranking_types": RANKING_TYPES
    })

# --- API Endpoints ---
@router.get("/api/overview")
async def get_overview(target_date: Optional[str] = None):
    return analyzer.get_market_overview(target_date=target_date)

@router.get("/api/rankings")
async def get_rankings(
    platform: Optional[str] = "all",
    country: Optional[str] = "all",
    ranking_type: Optional[str] = "all",
    genre: Optional[str] = "all",
    search: Optional[str] = None,
    target_date: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    return analyzer.get_rankings(
        platform=platform,
        country=country,
        ranking_type=ranking_type,
        genre=genre,
        search_query=search,
        target_date=target_date,
        limit=limit,
        offset=offset
    )

@router.get("/api/genres")
async def get_genres(platform: Optional[str] = "all", country: Optional[str] = "all", target_date: Optional[str] = None):
    return analyzer.get_genre_distribution(platform=platform, country=country, target_date=target_date)

@router.get("/api/report")
async def get_report(target_date: Optional[str] = None, period: str = "daily"):
    return report_generator.generate_market_report(target_date=target_date, period=period)

@router.get("/api/export/excel")
async def export_excel(target_date: Optional[str] = None):
    if not target_date:
        target_date = analyzer.get_latest_snapshot_date()
    content = report_generator.export_to_excel(target_date=target_date)
    filename = f"game_market_report_{target_date}.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/api/export/csv")
async def export_csv(target_date: Optional[str] = None):
    if not target_date:
        target_date = analyzer.get_latest_snapshot_date()
    content = report_generator.export_to_csv(target_date=target_date)
    filename = f"game_market_report_{target_date}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/api/games/search")
async def search_games_api(q: str = Query("", min_length=1), limit: int = Query(15, ge=1, le=50)):
    return analyzer.search_games(query=q, limit=limit)

@router.get("/api/compare")
async def compare_games_api(game_a: str = Query(...), game_b: str = Query(...)):
    return analyzer.compare_games(game_id_a=game_a, game_id_b=game_b)

@router.get("/api/meta")
async def get_metadata():
    return {
        "supported_countries": SUPPORTED_COUNTRIES,
        "platforms": PLATFORMS,
        "ranking_types": RANKING_TYPES,
        "latest_date": analyzer.get_latest_snapshot_date()
    }

@router.get("/api/game/{game_id}/history")
async def get_game_history(game_id: str, days: int = 30):
    return analyzer.get_game_history(game_id=game_id, limit_days=days)

@router.get("/api/game/{game_id}")
async def get_game_details_api(game_id: str):
    details = analyzer.get_game_details(game_id)
    if not details:
        return {"error": "Game not found"}
    return details

# --- Estimated Revenue & Download History (rank-based model) ---
@router.get("/api/game/{game_id}/revenue-history")
async def get_game_revenue_history_api(game_id: str, days: int = Query(30, ge=7, le=90)):
    """Returns 30-day historical revenue, download curves, ARPU and lifecycle phase."""
    return RevenueHistoryEngine.get_game_revenue_history(game_id=game_id, days=days)


# --- Market signals (built only from real crawl data) ---
@router.get("/api/signals/data-health")
async def get_data_health_api():
    return MarketSignals.get_data_health()


@router.get("/api/signals/sustained-breakouts")
async def get_sustained_breakouts_api(
    window_days: int = Query(7, ge=3, le=60),
    platform: Optional[str] = "all",
    country: Optional[str] = "all",
    min_net_gain: int = Query(5, ge=1, le=100),
    limit: int = Query(20, ge=1, le=100),
):
    return MarketSignals.get_sustained_breakouts(
        window_days=window_days, platform=platform, country=country,
        min_net_gain=min_net_gain, limit=limit,
    )


@router.get("/api/signals/genre-trends")
async def get_genre_trends_api(
    platform: Optional[str] = "all",
    country: Optional[str] = "all",
    top_n_rank: int = Query(50, ge=5, le=200),
):
    return MarketSignals.get_genre_trends(platform=platform, country=country, top_n_rank=top_n_rank)
