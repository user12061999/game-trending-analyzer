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
from app.analytics.ua_campaign_optimizer import UACampaignOptimizer
from app.analytics.gacha_economy_simulator import GachaEconomySimulator
from app.analytics.publisher_deal_evaluator import PublisherDealEvaluator
from app.analytics.culturalization_scanner import CulturalizationScanner
from app.analytics.churn_chokepoint_analyzer import ChurnChokepointAnalyzer
from app.analytics.viral_kfactor_forecaster import ViralKFactorForecaster
from app.analytics.webhook_bot_service import WebhookBotService
from app.analytics.pitch_deck_generator import PitchDeckGenerator
from app.analytics.ab_testing_calculator import ABTestingCalculator
from app.analytics.ad_mediation_optimizer import AdMediationOptimizer
from app.analytics.playable_ad_generator import PlayableAdGenerator
from app.analytics.voiceover_studio import VoiceoverStudio
from app.analytics.feature_rice_scorer import FeatureRICEScorer
from app.analytics.ad_fraud_scanner import AdFraudScanner
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
ua_optimizer = UACampaignOptimizer()
gacha_simulator = GachaEconomySimulator()
publisher_evaluator = PublisherDealEvaluator()
c10n_scanner = CulturalizationScanner()
churn_analyzer = ChurnChokepointAnalyzer()
kfactor_forecaster = ViralKFactorForecaster()
bot_service = WebhookBotService()
pitch_generator = PitchDeckGenerator()
ab_calculator = ABTestingCalculator()
mediation_optimizer = AdMediationOptimizer()
playable_generator = PlayableAdGenerator()
voiceover_studio = VoiceoverStudio()
rice_scorer = FeatureRICEScorer()
ad_fraud_scanner = AdFraudScanner()

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

# --- TikTok & Meta UA Campaign Optimizer & ROAS Pacing Endpoints ---
@app.get("/api/mobile/campaign/dayparting-benchmarks")
async def get_ua_dayparting_benchmarks_api():
    """Returns 24-hour behavioral curves, network mechanics, and kill-switch rules."""
    return ua_optimizer.get_benchmarks()

@app.post("/api/mobile/campaign/optimize-pacing")
async def optimize_campaign_pacing_api(request: Request):
    """Calculates hourly budget dayparting schedule, bid multipliers, and ROI forecast."""
    payload = await request.json()
    budget = float(payload.get("daily_budget", 1000.0))
    network = payload.get("network_id", "tiktok")
    goal = payload.get("optimization_goal", "aeo_purchase")
    cpi = float(payload.get("target_cpi", 1.80))
    roas = float(payload.get("target_roas_d0", 20.0))
    return ua_optimizer.optimize_campaign_pacing(
        daily_budget=budget,
        network_id=network,
        optimization_goal=goal,
        target_cpi=cpi,
        target_roas_d0=roas
    )

# --- Gacha & In-Game Economy Endpoints ---
@app.get("/api/mobile/gacha/models")
async def get_gacha_models_api():
    """Returns preset gacha system models and mechanics."""
    return {"models": gacha_simulator.preset_models}

@app.post("/api/mobile/gacha/simulate")
async def simulate_gacha_api(request: Request):
    """Runs Monte Carlo gacha probability simulations."""
    payload = await request.json()
    model = payload.get("model_key", "genshin_style")
    copies = int(payload.get("target_copies", 1))
    return gacha_simulator.simulate_gacha_pulls(model_key=model, target_copies=copies)

@app.post("/api/mobile/gacha/faucet-sink")
async def evaluate_faucet_sink_api(request: Request):
    """Calculates resource faucet vs sink balance and inflation health."""
    payload = await request.json()
    return gacha_simulator.evaluate_economy_faucet_sink(
        daily_gem_faucet=int(payload.get("daily_faucet", 150)),
        weekly_event_faucet=int(payload.get("weekly_faucet", 500)),
        monthly_pass_faucet=int(payload.get("monthly_pass", 3000)),
        daily_gem_sink=int(payload.get("daily_sink", 120)),
        weekly_gem_sink=int(payload.get("weekly_sink", 800)),
        gacha_pull_cost_gems=int(payload.get("pull_cost", 160))
    )

# --- Global Publisher Deal & Scorecard Endpoints ---
@app.post("/api/mobile/publisher/scorecard")
async def get_publisher_scorecard_api(request: Request):
    """Evaluates game metrics against Tier 1 & Tier 2 global publisher benchmarks."""
    payload = await request.json()
    d1 = float(payload.get("d1_retention", 40.0))
    d7 = float(payload.get("d7_retention", 15.0))
    cpi = float(payload.get("cpi_us", 0.85))
    playtime = int(payload.get("playtime_mins", 28))
    genre = payload.get("genre", "Hybrid-Casual")
    return publisher_evaluator.evaluate_game_readiness(
        d1_retention=d1,
        d7_retention=d7,
        tested_cpi_us=cpi,
        avg_playtime_mins=playtime,
        game_genre=genre
    )

@app.post("/api/mobile/publisher/simulate-deal")
async def simulate_publisher_deal_api(request: Request):
    """Simulates net studio earnings under standard post-UA recoupment contract."""
    payload = await request.json()
    gross = float(payload.get("projected_gross", 500000.0))
    ua = float(payload.get("ua_budget", 300000.0))
    revshare = float(payload.get("studio_revshare", 40.0))
    mg = float(payload.get("minimum_guarantee", 50000.0))
    return publisher_evaluator.simulate_publishing_deal_cashflow(
        projected_gross_revenue=gross,
        ua_marketing_budget=ua,
        studio_revshare_pct=revshare,
        minimum_guarantee=mg
    )

# --- Culturalization & Regulatory Scanner Endpoints ---
@app.get("/api/mobile/culturalization/standards")
async def get_culturalization_standards_api():
    """Returns regional compliance and cultural standards for China, Japan, MENA, EU."""
    return {"regions": c10n_scanner.get_all_standards()}

@app.post("/api/mobile/culturalization/audit")
async def audit_culturalization_api(request: Request):
    """Audits game configuration against targeted regional standards."""
    payload = await request.json()
    title = payload.get("game_title", "Mobile Project")
    regions = payload.get("target_regions", ["china", "japan", "mena", "eu"])
    return c10n_scanner.audit_game_compliance(
        game_title=title,
        target_regions=regions,
        has_skeletons=bool(payload.get("has_skeletons", False)),
        has_red_blood=bool(payload.get("has_red_blood", False)),
        has_gacha_lootbox=bool(payload.get("has_gacha_lootbox", True)),
        has_skimpy_costumes=bool(payload.get("has_skimpy_costumes", False)),
        supports_rtl_arabic=bool(payload.get("supports_rtl_arabic", False))
    )

# --- Choke-Point & Churn Diagnostic Endpoints ---
@app.get("/api/mobile/churn/funnel-benchmark")
async def get_churn_benchmark_api():
    """Returns benchmark player onboarding funnel conversion rates."""
    return {"funnel": churn_analyzer.benchmark_funnel}

@app.post("/api/mobile/churn/diagnose")
async def diagnose_churn_api(request: Request):
    """Diagnoses custom studio funnel drop-offs and rage-quit walls."""
    payload = await request.json()
    installs = int(payload.get("installs", 10000))
    patch_pass = float(payload.get("patch_pass_pct", 85.0))
    tutorial_pass = float(payload.get("tutorial_pass_pct", 70.0))
    boss_win = float(payload.get("boss_win_pct", 40.0))
    losses_to_quit = int(payload.get("losses_to_quit", 3))
    return churn_analyzer.diagnose_player_funnel(
        install_count=installs,
        patch_download_pass_pct=patch_pass,
        tutorial_complete_pct=tutorial_pass,
        chokepoint_boss_win_pct=boss_win,
        consecutive_losses_to_quit=losses_to_quit
    )

# --- TikTok Creator & Viral K-Factor Endpoints ---
@app.post("/api/mobile/viral/k-factor")
async def calculate_kfactor_api(request: Request):
    """Calculates viral K-Factor and models viral loop user acquisition."""
    payload = await request.json()
    paid_installs = int(payload.get("paid_installs", 10000))
    cpi = float(payload.get("paid_cpi", 2.00))
    invites = float(payload.get("invites_per_user", 2.5))
    cvr = float(payload.get("invitee_cvr", 0.24))
    cycles = int(payload.get("cycles", 5))
    return kfactor_forecaster.calculate_k_factor_loop(
        paid_installs=paid_installs,
        paid_cpi=cpi,
        invites_per_user=invites,
        invitee_conversion_rate=cvr,
        simulation_cycles=cycles
    )

@app.post("/api/mobile/viral/tiktok-forecast")
async def forecast_tiktok_campaign_api(request: Request):
    """Projects ROI and organic store search lift from a TikTok/Shorts Micro-Creator campaign."""
    payload = await request.json()
    budget = float(payload.get("budget", 5000.0))
    creators = int(payload.get("creator_count", 25))
    views = int(payload.get("avg_views", 40000))
    network = payload.get("network", "TikTok")
    return kfactor_forecaster.forecast_tiktok_creator_campaign(
        creator_budget_usd=budget,
        creator_count=creators,
        avg_views_per_creator=views,
        target_network=network
    )

# --- Discord & Telegram Webhook Bot Endpoints ---
@app.get("/api/mobile/webhook/config")
async def get_webhook_config_api():
    """Returns saved webhook bot configuration."""
    return bot_service.get_config()

@app.post("/api/mobile/webhook/config")
async def save_webhook_config_api(request: Request):
    """Saves Discord and Telegram webhook credentials and preferences."""
    payload = await request.json()
    return bot_service.save_config(payload)

@app.post("/api/mobile/webhook/test")
async def test_webhook_api():
    """Sends an instant test alert to enabled webhook channels."""
    return bot_service.trigger_test_alert()

@app.post("/api/mobile/webhook/trigger-digest")
async def trigger_morning_digest_api():
    """Triggers immediate broadcast of morning market digest."""
    return bot_service.trigger_morning_digest()

# --- Executive Pitch Deck Generator Endpoints ---
@app.post("/api/mobile/deck/generate")
async def generate_pitch_deck_api(request: Request):
    """Generates standalone printable HTML pitch deck presentation."""
    payload = await request.json()
    deck_html = pitch_generator.generate_deck_html(
        game_title=payload.get("game_title", "Project Valkyrie"),
        genre=payload.get("genre", "Mid-Core Action RPG"),
        target_regions=payload.get("target_regions", "Global (Tier 1 US/JP & SEA)"),
        target_cpi=float(payload.get("target_cpi", 1.80)),
        projected_d1=float(payload.get("projected_d1", 42.0)),
        projected_d7=float(payload.get("projected_d7", 16.5)),
        target_break_even_day=int(payload.get("break_even_day", 45)),
        whale_cap=payload.get("whale_cap", "$1,500+"),
        publisher_fit=payload.get("publisher_fit", "Habby / Miniclip (Tier 1 Mid-Core)")
    )
    return HTMLResponse(content=deck_html)

# --- Soft-Launch A/B Testing Calculator Endpoints ---
@app.post("/api/mobile/ab-test/sample-size")
async def calculate_sample_size_api(request: Request):
    """Calculates minimum sample size per variant needed for soft-launch test."""
    payload = await request.json()
    base = float(payload.get("baseline_rate_pct", 40.0))
    lift = float(payload.get("expected_lift_pct", 3.0))
    conf = float(payload.get("confidence_level", 95.0))
    power = float(payload.get("power", 80.0))
    country = payload.get("country", "philippines")
    return ab_calculator.calculate_required_sample_size(
        baseline_rate_pct=base,
        expected_lift_pct=lift,
        confidence_level=conf,
        power=power,
        country_key=country
    )

@app.post("/api/mobile/ab-test/evaluate")
async def evaluate_ab_test_api(request: Request):
    """Evaluates statistical significance of A/B test results (Z-test, p-value)."""
    payload = await request.json()
    return ab_calculator.evaluate_ab_test_significance(
        visitors_a=int(payload.get("visitors_a", 1500)),
        conversions_a=int(payload.get("conversions_a", 600)),
        visitors_b=int(payload.get("visitors_b", 1500)),
        conversions_b=int(payload.get("conversions_b", 660)),
        metric_name=payload.get("metric_name", "D1 Retention")
    )

# --- Ad Mediation Waterfall & eCPM Floor Endpoints ---
@app.get("/api/mobile/mediation/benchmarks")
async def get_mediation_benchmarks_api():
    """Returns regional eCPM benchmarks and standard waterfall templates."""
    return mediation_optimizer.get_benchmarks()

@app.post("/api/mobile/mediation/simulate")
async def simulate_mediation_api(request: Request):
    """Simulates ad revenue yield and ad fatigue retention penalty."""
    payload = await request.json()
    dau = int(payload.get("dau", 50000))
    session_mins = int(payload.get("session_mins", 15))
    cooldown = int(payload.get("cooldown_secs", 60))
    rewarded = float(payload.get("rewarded_watches", 2.5))
    region = payload.get("region", "us")
    return mediation_optimizer.simulate_mediation_yield(
        dau=dau,
        avg_session_mins=session_mins,
        interstitial_cooldown_secs=cooldown,
        rewarded_watches_per_user=rewarded,
        region_tier=region
    )

# --- Playable Ad Canvas Sandbox & MRAID Exporter Endpoints ---
@app.get("/api/mobile/playable/templates")
async def get_playable_templates_api():
    """Returns high-converting playable ad templates."""
    return playable_generator.get_templates()

@app.post("/api/mobile/playable/export-mraid")
async def export_playable_mraid_api(request: Request):
    """Exports a single-file standalone MRAID 2.0 HTML5 playable ad bundle."""
    payload = await request.json()
    template_id = payload.get("template_id", "gate_multiplier")
    game_title = payload.get("game_title", "Stickman Army War")
    call_to_action = payload.get("call_to_action", "PLAY NOW FREE")
    store_url = payload.get("store_url", "https://apps.apple.com")
    html_code = playable_generator.generate_mraid_bundle(
        template_id=template_id,
        game_title=game_title,
        call_to_action=call_to_action,
        store_url=store_url
    )
    return HTMLResponse(content=html_code)

# --- Multilingual Ad Voiceover & Audio Preview Studio Endpoints ---
@app.get("/api/mobile/voiceover/meta")
async def get_voiceover_meta_api():
    """Returns supported localization markets and emotion tones."""
    return {
        "markets": voiceover_studio.get_supported_markets(),
        "emotions": voiceover_studio.get_supported_emotions()
    }

@app.post("/api/mobile/voiceover/generate")
async def generate_voiceover_api(request: Request):
    """Generates localized ad script with audio directions and Web Speech API params."""
    payload = await request.json()
    return voiceover_studio.generate_voiceover_script(
        game_title=payload.get("game_title", "Shadow Legends War"),
        genre=payload.get("genre", "RPG / Strategy"),
        target_market=payload.get("target_market", "US"),
        emotion_tone=payload.get("emotion_tone", "hype"),
        duration_seconds=int(payload.get("duration_seconds", 15))
    )

# --- Game Feature RICE Scorer & Production Roadmap Endpoints ---
@app.get("/api/mobile/rice/presets")
async def get_rice_presets_api():
    """Returns 10 classic mobile liveops feature presets."""
    return rice_scorer.get_presets()

@app.post("/api/mobile/rice/evaluate")
async def evaluate_rice_api(request: Request):
    """Calculates RICE priority scores and assigns quarterly sprints."""
    payload = await request.json()
    custom_features = payload.get("features", [])
    return rice_scorer.evaluate_features(custom_features)

# --- UA Ad Fraud & Click Injection Diagnostic Scanner Endpoints ---
@app.get("/api/mobile/fraud/samples")
async def get_fraud_samples_api():
    """Returns preset benchmark networks for fraud comparison."""
    return ad_fraud_scanner.get_sample_networks()

@app.post("/api/mobile/fraud/audit")
async def audit_fraud_api(request: Request):
    """Audits network MTTI / CTIT distribution and calculates clawback refund claim."""
    payload = await request.json()
    return ad_fraud_scanner.audit_network(
        network_name=payload.get("network_name", "Custom Network"),
        total_installs=int(payload.get("total_installs", 25000)),
        mtti_under_10s_pct=float(payload.get("mtti_under_10s_pct", 35.0)),
        mtti_over_24h_pct=float(payload.get("mtti_over_24h_pct", 20.0)),
        d1_retention_pct=float(payload.get("d1_retention_pct", 12.0)),
        ad_spend_usd=float(payload.get("ad_spend_usd", 37500.0)),
        cpi_usd=float(payload.get("cpi_usd", 1.50)) if payload.get("cpi_usd") else None
    )

@app.get("/api/meta")
async def get_metadata():
    return {
        "supported_countries": SUPPORTED_COUNTRIES,
        "platforms": PLATFORMS,
        "ranking_types": RANKING_TYPES,
        "latest_date": analyzer.get_latest_snapshot_date()
    }
