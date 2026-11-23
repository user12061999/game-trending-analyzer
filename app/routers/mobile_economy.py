"""Mobile economy, LiveOps, ASO and retention tools."""

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
    review_miner,
    aso_analyzer,
    liveops_tracker,
    blue_ocean_finder,
    aso_visual_optimizer,
    iap_analyzer,
    liveops_scheduler,
    gacha_simulator,
    publisher_evaluator,
    c10n_scanner,
    churn_analyzer,
    rice_scorer,
)

router = APIRouter()

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/api/mobile/blue-ocean")
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
@router.get("/api/mobile/aso/visual-archetypes")
async def get_aso_visual_archetypes_api():
    """Returns benchmark visual archetypes for mobile icons and screenshots."""
    return {"archetypes": aso_visual_optimizer.get_visual_archetypes()}

@router.post("/api/mobile/aso/audit")
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
@router.get("/api/mobile/iap/benchmarks")
async def get_iap_benchmarks_api(genre: Optional[str] = Query(None)):
    """Returns standard monetization ladders and PPP benchmarks."""
    return iap_analyzer.get_benchmarks(genre_key=genre)

@router.post("/api/mobile/iap/simulate-economy")
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
@router.get("/api/mobile/liveops/clash-radar")
async def get_liveops_clash_radar_api():
    """Returns competitor update cadence, high-risk auction windows, and LiveOps templates."""
    radar = liveops_scheduler.get_competitor_radar()
    templates = liveops_scheduler.get_event_templates()
    return {
        "radar": radar,
        "templates": templates
    }

@router.post("/api/mobile/liveops/plan")
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

# --- Gacha & In-Game Economy Endpoints ---
@router.get("/api/mobile/gacha/models")
async def get_gacha_models_api():
    """Returns preset gacha system models and mechanics."""
    return {"models": gacha_simulator.preset_models}

@router.post("/api/mobile/gacha/simulate")
async def simulate_gacha_api(request: Request):
    """Runs Monte Carlo gacha probability simulations."""
    payload = await request.json()
    model = payload.get("model_key", "genshin_style")
    copies = int(payload.get("target_copies", 1))
    return gacha_simulator.simulate_gacha_pulls(model_key=model, target_copies=copies)

@router.post("/api/mobile/gacha/faucet-sink")
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
@router.post("/api/mobile/publisher/scorecard")
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

@router.post("/api/mobile/publisher/simulate-deal")
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
@router.get("/api/mobile/culturalization/standards")
async def get_culturalization_standards_api():
    """Returns regional compliance and cultural standards for China, Japan, MENA, EU."""
    return {"regions": c10n_scanner.get_all_standards()}

@router.post("/api/mobile/culturalization/audit")
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
@router.get("/api/mobile/churn/funnel-benchmark")
async def get_churn_benchmark_api():
    """Returns benchmark player onboarding funnel conversion rates."""
    return {"funnel": churn_analyzer.benchmark_funnel}

@router.post("/api/mobile/churn/diagnose")
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

# --- Game Feature RICE Scorer & Production Roadmap Endpoints ---
@router.get("/api/mobile/rice/presets")
async def get_rice_presets_api():
    """Returns 10 classic mobile liveops feature presets."""
    return rice_scorer.get_presets()

@router.post("/api/mobile/rice/evaluate")
async def evaluate_rice_api(request: Request):
    """Calculates RICE priority scores and assigns quarterly sprints."""
    payload = await request.json()
    custom_features = payload.get("features", [])
    return rice_scorer.evaluate_features(custom_features)

# --- Mobile Specialization Intelligence Endpoints (Review/Churn, ASO, LiveOps) ---
@router.get("/api/mobile/reviews/{game_id}")
async def get_mobile_reviews_api(game_id: str, title: Optional[str] = Query(None), platform: Optional[str] = Query("mobile")):
    """Returns Sentiment breakdown, Churn drivers, Retention hooks and Studio Attack Playbook."""
    result = review_miner.analyze_reviews(game_id=game_id, game_title=title or "", platform=platform)
    return result

@router.get("/api/mobile/aso/{game_id}")
async def get_mobile_aso_api(game_id: str, title: Optional[str] = Query(None), genre: Optional[str] = Query("RPG")):
    """Returns Title/Subtitle analysis, keyword density, ASO Health Score and Target Keywords."""
    result = aso_analyzer.analyze_aso(game_id=game_id, game_title=title or "", genre=genre)
    return result

@router.get("/api/mobile/liveops/{game_id}")
async def get_mobile_liveops_api(game_id: str, title: Optional[str] = Query(None)):
    """Returns version changelog, event classification, timeline and revenue impact correlation."""
    result = liveops_tracker.analyze_liveops(game_id=game_id, game_title=title or "")
    return result
