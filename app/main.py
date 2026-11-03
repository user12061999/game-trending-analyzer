"""FastAPI Main Application and API router for Game Market Trending Analyzer."""

import os
from typing import Optional, List
from datetime import date, datetime
from fastapi import FastAPI, Query, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import SUPPORTED_COUNTRIES, PLATFORMS, RANKING_TYPES, BASE_DIR
from app.database.db import (
    init_db,
    get_db_connection,
    add_to_watchlist,
    remove_from_watchlist,
    is_game_in_watchlist
)
from app.crawlers.orchestrator import CrawlerOrchestrator
from app.analytics.trend_analyzer import TrendAnalyzer
from app.analytics.report_generator import ReportGenerator
from app.analytics.ai_analyst import AIAnalyst
from app.notifications.notifier import AlertNotifier

# Scheduler for automatic daily crawl & alerts
scheduler = BackgroundScheduler()
orchestrator = CrawlerOrchestrator()
analyzer = TrendAnalyzer()
report_generator = ReportGenerator()
notifier = AlertNotifier()
ai_analyst = AIAnalyst()

is_crawling = False

def scheduled_crawl_job():
    global is_crawling
    if not is_crawling:
        is_crawling = True
        try:
            print(f"[{datetime.now()}] Running scheduled daily crawl...")
            crawl_res = orchestrator.run_full_crawl()
            # Check for breakout alerts
            overview = analyzer.get_market_overview()
            for game in overview.get("rising_games", []):
                notifier.dispatch_breakout_alert(game)
        finally:
            is_crawling = False

def scheduled_morning_digest_job():
    print(f"[{datetime.now()}] Dispatching morning market digest...")
    notifier.dispatch_daily_digest()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    init_db()
    
    # Check if database has any snapshots; if empty, run an initial quick crawl
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM snapshots")
    count = cursor.fetchone()["count"]
    conn.close()

    if count == 0:
        print("[Startup] Database is empty. Running initial market crawl...")
        try:
            orchestrator.run_full_crawl(countries=["us", "vn", "kr", "jp", "global"])
        except Exception as e:
            print(f"[Startup] Initial crawl warning: {e}")

    # Schedule daily crawl every 24 hours
    scheduler.add_job(scheduled_crawl_job, "interval", hours=24, id="daily_crawl_job", replace_existing=True)
    # Schedule morning digest at 08:00 every day
    scheduler.add_job(scheduled_morning_digest_job, "cron", hour=8, minute=0, id="daily_digest_job", replace_existing=True)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="Game Market Trending Analyzer",
    description="Tool phân tích xu hướng thị trường Game Mobile & PC theo từng ngày, từng tuần",
    version="1.0.0",
    lifespan=lifespan
)

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# --- Web UI Route ---
@app.get("/", response_class=HTMLResponse)
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
@app.get("/api/overview")
async def get_overview(target_date: Optional[str] = None):
    return analyzer.get_market_overview(target_date=target_date)

@app.get("/api/rankings")
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

@app.get("/api/genres")
async def get_genres(platform: Optional[str] = "all", country: Optional[str] = "all", target_date: Optional[str] = None):
    return analyzer.get_genre_distribution(platform=platform, country=country, target_date=target_date)

@app.get("/api/game/{game_id}/history")
async def get_game_history(game_id: str, days: int = 30):
    return analyzer.get_game_history(game_id=game_id, limit_days=days)

@app.post("/api/crawl")
async def trigger_crawl(background_tasks: BackgroundTasks, countries: Optional[str] = None):
    global is_crawling
    if is_crawling:
        return {"status": "busy", "message": "Một tác vụ crawl đang chạy trong nền, vui lòng đợi."}

    country_list = [c.strip() for c in countries.split(",")] if countries else ["us", "vn", "kr", "jp", "global"]
    
    def run_task():
        global is_crawling
        is_crawling = True
        try:
            orchestrator.run_full_crawl(countries=country_list)
            # Check for breakout alerts
            overview = analyzer.get_market_overview()
            for game in overview.get("rising_games", []):
                notifier.dispatch_breakout_alert(game)
        finally:
            is_crawling = False

    background_tasks.add_task(run_task)
    return {"status": "started", "message": f"Đang bắt đầu crawl dữ liệu cho: {', '.join(country_list)}"}

@app.get("/api/crawl/status")
async def get_crawl_status():
    global is_crawling
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crawl_history ORDER BY id DESC LIMIT 15")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "is_crawling": is_crawling,
        "recent_logs": logs
    }

@app.get("/api/report")
async def get_report(target_date: Optional[str] = None, period: str = "daily"):
    return report_generator.generate_market_report(target_date=target_date, period=period)

@app.get("/api/export/excel")
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

@app.get("/api/export/csv")
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

@app.get("/api/game/{game_id}")
async def get_game_details_api(game_id: str):
    details = analyzer.get_game_details(game_id)
    if not details:
        return {"error": "Game not found"}
    return details

@app.get("/api/games/search")
async def search_games_api(q: str = Query("", min_length=1), limit: int = Query(15, ge=1, le=50)):
    return analyzer.search_games(query=q, limit=limit)

@app.get("/api/compare")
async def compare_games_api(game_a: str = Query(...), game_b: str = Query(...)):
    return analyzer.compare_games(game_id_a=game_a, game_id_b=game_b)

# --- Notification & Alert Endpoints ---
@app.get("/api/alerts/config")
async def get_alert_config():
    return notifier.get_config()

@app.post("/api/alerts/config")
async def update_alert_config(request: Request):
    payload = await request.json()
    return notifier.save_config(payload)

@app.post("/api/alerts/test")
async def test_alert():
    return notifier.send_test_alert()

@app.post("/api/alerts/digest")
async def send_manual_digest(target_date: Optional[str] = None):
    return notifier.dispatch_daily_digest(target_date=target_date)

# --- AI Game Deconstruction Endpoints ---
@app.post("/api/ai/analyze")
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

@app.get("/api/ai/config")
async def get_ai_config():
    key = ai_analyst.get_api_key()
    return {
        "has_gemini_key": bool(key),
        "masked_key": f"{key[:6]}...{key[-4:]}" if len(key) > 10 else ("Configured" if key else "")
    }

@app.post("/api/ai/config")
async def save_ai_config(request: Request):
    payload = await request.json()
    key = payload.get("gemini_api_key", "").strip()
    ai_analyst.save_api_key(key)
    return {"status": "success", "has_gemini_key": bool(key)}

# --- Watchlist & Rival Tracker Endpoints ---
@app.get("/api/watchlist")
async def get_watchlist_api():
    return analyzer.get_watchlist_dashboard_data()

@app.post("/api/watchlist")
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

@app.delete("/api/watchlist/{game_id}")
async def remove_watchlist_api(game_id: str):
    remove_from_watchlist(game_id)
    return {"status": "success", "message": "Đã xóa khỏi danh sách theo dõi", "is_in_watchlist": False}

@app.get("/api/watchlist/check/{game_id}")
async def check_watchlist_api(game_id: str):
    return {"game_id": game_id, "in_watchlist": is_game_in_watchlist(game_id)}

@app.get("/api/meta")
async def get_metadata():
    return {
        "supported_countries": SUPPORTED_COUNTRIES,
        "platforms": PLATFORMS,
        "ranking_types": RANKING_TYPES,
        "latest_date": analyzer.get_latest_snapshot_date()
    }
