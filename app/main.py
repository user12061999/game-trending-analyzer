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
    is_game_in_watchlist,
    get_upcoming_mobile_games,
    get_upcoming_game_by_id,
    toggle_track_upcoming_game,
    get_radar_threat_stats
)
from app.crawlers.orchestrator import CrawlerOrchestrator
from app.analytics.trend_analyzer import TrendAnalyzer
from app.analytics.report_generator import ReportGenerator
from app.analytics.ai_analyst import AIAnalyst
from app.analytics.review_miner import ReviewMiner
from app.analytics.aso_analyzer import ASOAnalyzer
from app.analytics.liveops_tracker import LiveOpsTracker
from app.analytics.creative_spy import CreativeSpy
from app.analytics.cpi_ltv_simulator import CPILTVForecaster
from app.analytics.blue_ocean_finder import BlueOceanFinder
from app.analytics.aso_visual_optimizer import ASOVisualOptimizer
from app.analytics.iap_monetization import IAPMonetizationAnalyzer
from app.analytics.liveops_scheduler import LiveOpsScheduler
from app.notifications.notifier import AlertNotifier

# Scheduler for automatic daily crawl & alerts
scheduler = BackgroundScheduler()
orchestrator = CrawlerOrchestrator()
analyzer = TrendAnalyzer()
report_generator = ReportGenerator()
notifier = AlertNotifier()
ai_analyst = AIAnalyst()
review_miner = ReviewMiner()
aso_analyzer = ASOAnalyzer()
liveops_tracker = LiveOpsTracker()
creative_spy = CreativeSpy()
cpi_simulator = CPILTVForecaster()
blue_ocean_finder = BlueOceanFinder()
aso_visual_optimizer = ASOVisualOptimizer()
iap_analyzer = IAPMonetizationAnalyzer()
liveops_scheduler = LiveOpsScheduler()

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

    # Ensure Mobile Radar has initial upcoming games
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as count FROM upcoming_mobile_games")
        radar_cnt = c.fetchone()["count"]
        conn.close()
        if radar_cnt == 0:
            print("[Startup] Populating Mobile Upcoming Radar intelligence...")
            orchestrator.mobile_radar_crawler.run_radar_update()
    except Exception as e:
        print(f"[Startup] Mobile radar init warning: {e}")

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

# --- Mobile Upcoming & Pre-registration Radar Endpoints ---
@app.get("/api/radar/upcoming")
async def get_upcoming_radar(
    region: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    threat_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    games = get_upcoming_mobile_games(region=region, genre=genre, threat_level=threat_level, search=search)
    return {"games": games, "total": len(games)}

@app.get("/api/radar/stats")
async def get_radar_stats():
    return get_radar_threat_stats()

@app.get("/api/radar/game/{game_id}")
async def get_radar_game(game_id: int):
    game = get_upcoming_game_by_id(game_id)
    if not game:
        return {"error": "Không tìm thấy game trong radar"}
    return game

@app.post("/api/radar/track/{game_id}")
async def track_radar_game(game_id: int):
    is_tracked = toggle_track_upcoming_game(game_id)
    return {"status": "success", "game_id": game_id, "is_tracked": is_tracked}

@app.post("/api/radar/refresh")
async def refresh_radar_data():
    res = orchestrator.mobile_radar_crawler.run_radar_update()
    return {"status": "success", "result": res}

@app.post("/api/radar/alert-test/{game_id}")
async def send_radar_alert_test(game_id: int):
    game = get_upcoming_game_by_id(game_id)
    if not game:
        return {"error": "Không tìm thấy game"}
    sent = notifier.dispatch_radar_threat_alert(game)
    return {"status": "success", "alert_dispatched": sent}

# --- Mobile Specialization Intelligence Endpoints (Review/Churn, ASO, LiveOps) ---
@app.get("/api/mobile/reviews/{game_id}")
async def get_mobile_reviews_api(game_id: str, title: Optional[str] = Query(None), platform: Optional[str] = Query("mobile")):
    """Returns Sentiment breakdown, Churn drivers, Retention hooks and Studio Attack Playbook."""
    result = review_miner.analyze_reviews(game_id=game_id, game_title=title or "", platform=platform)
    return result

@app.get("/api/mobile/aso/{game_id}")
async def get_mobile_aso_api(game_id: str, title: Optional[str] = Query(None), genre: Optional[str] = Query("RPG")):
    """Returns Title/Subtitle analysis, keyword density, ASO Health Score and Target Keywords."""
    result = aso_analyzer.analyze_aso(game_id=game_id, game_title=title or "", genre=genre)
    return result

@app.get("/api/mobile/liveops/{game_id}")
async def get_mobile_liveops_api(game_id: str, title: Optional[str] = Query(None)):
    """Returns version changelog, event classification, timeline and revenue impact correlation."""
    result = liveops_tracker.analyze_liveops(game_id=game_id, game_title=title or "")
    return result

# --- Mobile Strategy Lab Endpoints (Creative Spy, CPI Simulator, Blue Ocean) ---
@app.get("/api/mobile/creatives")
async def get_creative_archetypes_api(genre: Optional[str] = Query(None), network: Optional[str] = Query(None)):
    """Returns top winning video ad archetypes and storyboards."""
    return {"archetypes": creative_spy.get_all_archetypes(genre=genre, network=network)}

@app.post("/api/mobile/creatives/generate")
async def generate_creative_script_api(request: Request):
    """Generates a custom 20-second video ad script for studio production."""
    payload = await request.json()
    title = payload.get("game_title", "")
    genre = payload.get("genre", "RPG")
    network = payload.get("target_network", "TikTok")
    script = creative_spy.generate_custom_ad_script(game_title=title, genre=genre, target_network=network)
    return script

@app.get("/api/mobile/simulator/cpi")
async def get_cpi_benchmark_api(country: str = Query("vn"), genre: str = Query("rpg"), platform: str = Query("all")):
    """Returns estimated CPI cost for given country and genre."""
    cpi = cpi_simulator.get_cpi_benchmark(country=country, genre=genre, platform=platform)
    return {"country": country.upper(), "genre": genre.title(), "platform": platform.upper(), "estimated_cpi": cpi}

@app.post("/api/mobile/simulator/run")
async def run_ua_simulation_api(request: Request):
    """Performs 180-day UA simulation and computes break-even day and ROAS milestones."""
    payload = await request.json()
    budget = float(payload.get("budget", 5000.0))
    country = payload.get("country", "vn")
    genre = payload.get("genre", "rpg")
    platform = payload.get("platform", "all")
    custom_cpi = payload.get("custom_cpi")
    res = cpi_simulator.simulate_ua_campaign(budget=budget, country=country, genre=genre, platform=platform, custom_cpi=custom_cpi)
    return res

@app.get("/api/mobile/blue-ocean")
async def get_blue_ocean_api(classification: Optional[str] = Query(None)):
    """Returns market saturation matrix, blue oceans, and aging monopolies."""
    niches = blue_ocean_finder.get_market_niches(classification=classification)
    aging = blue_ocean_finder.get_aging_monopolies()
    stats = blue_ocean_finder.get_market_overview_stats()
    return {
        "stats": stats,
        "niches": niches,
        "aging_monopolies": aging
    }

# --- ASO Visual Lab & Metadata Audit Endpoints ---
@app.get("/api/mobile/aso/visual-archetypes")
async def get_aso_visual_archetypes_api():
    """Returns benchmark visual archetypes for mobile icons and screenshots."""
    return {"archetypes": aso_visual_optimizer.get_visual_archetypes()}

@app.post("/api/mobile/aso/audit")
async def audit_aso_metadata_api(request: Request):
    """Audits game title, subtitle, keywords and icon archetype for CVR prediction."""
    payload = await request.json()
    title = payload.get("title", "")
    subtitle = payload.get("subtitle", "")
    keywords = payload.get("keywords", "")
    genre = payload.get("genre", "RPG")
    icon_style = payload.get("icon_archetype_id", "screaming_hero")
    target_store = payload.get("target_store", "google_play")
    return aso_visual_optimizer.audit_metadata(
        title=title,
        subtitle=subtitle,
        keywords=keywords,
        genre=genre,
        icon_archetype_id=icon_style,
        target_store=target_store
    )

# --- IAP Monetization & Battle Pass Pricing Endpoints ---
@app.get("/api/mobile/iap/benchmarks")
async def get_iap_benchmarks_api(genre: Optional[str] = Query(None)):
    """Returns standard monetization ladders and PPP benchmarks."""
    return iap_analyzer.get_benchmarks(genre_key=genre)

@app.post("/api/mobile/iap/simulate-economy")
async def simulate_iap_economy_api(request: Request):
    """Simulates 30-day player spender distribution, revenue breakdown, and ARPPU."""
    payload = await request.json()
    dau = int(payload.get("dau", 50000))
    genre_key = payload.get("genre_key", "midcore_rpg")
    region_tier = payload.get("region_tier", "global")
    bp_price = float(payload.get("battle_pass_price", 9.99))
    card_price = float(payload.get("monthly_card_price", 4.99))
    return iap_analyzer.simulate_economy(
        dau=dau,
        genre_key=genre_key,
        region_tier=region_tier,
        battle_pass_price=bp_price,
        monthly_card_price=card_price
    )

# --- LiveOps Calendar & Competitor Clash Radar Endpoints ---
@app.get("/api/mobile/liveops/clash-radar")
async def get_liveops_clash_radar_api():
    """Returns competitor update cadence, high-risk auction windows, and LiveOps templates."""
    radar = liveops_scheduler.get_competitor_radar()
    templates = liveops_scheduler.get_event_templates()
    return {
        "radar": radar,
        "templates": templates
    }

@app.post("/api/mobile/liveops/plan")
async def plan_liveops_event_api(request: Request):
    """Plans a LiveOps event and forecasts daily revenue surge and clash advisory."""
    payload = await request.json()
    event_type = payload.get("event_type_id", "battle_pass_season")
    start_date = payload.get("start_date", "")
    duration_days = int(payload.get("duration_days", 14))
    base_dau = int(payload.get("base_dau", 25000))
    base_arpdau = float(payload.get("base_arpdau", 0.08))
    return liveops_scheduler.plan_liveops_event(
        event_type_id=event_type,
        start_date=start_date,
        duration_days=duration_days,
        base_dau=base_dau,
        base_arpdau=base_arpdau
    )

@app.get("/api/meta")
async def get_metadata():
    return {
        "supported_countries": SUPPORTED_COUNTRIES,
        "platforms": PLATFORMS,
        "ranking_types": RANKING_TYPES,
        "latest_date": analyzer.get_latest_snapshot_date()
    }
