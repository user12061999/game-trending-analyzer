"""Mobile UA / creative / ads tools."""

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
    creative_spy,
    cpi_simulator,
    ua_optimizer,
    kfactor_forecaster,
    bot_service,
    pitch_generator,
    ab_calculator,
    playable_generator,
    voiceover_studio,
    ad_fraud_scanner,
    ad_mediation_engine,
)

router = APIRouter()

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


# --- Mobile Strategy Lab Endpoints (Creative Spy, CPI Simulator, Blue Ocean) ---
@router.get("/api/mobile/creatives")
async def get_creative_archetypes_api(genre: Optional[str] = Query(None), network: Optional[str] = Query(None)):
    """Returns top winning video ad archetypes and storyboards."""
    return {"archetypes": creative_spy.get_all_archetypes(genre=genre, network=network)}

@router.post("/api/mobile/creatives/generate")
async def generate_creative_script_api(request: Request):
    """Generates a custom 20-second video ad script for studio production."""
    payload = await request.json()
    title = payload.get("game_title", "")
    genre = payload.get("genre", "RPG")
    network = payload.get("target_network", "TikTok")
    script = creative_spy.generate_custom_ad_script(game_title=title, genre=genre, target_network=network)
    return script

@router.get("/api/mobile/simulator/cpi")
async def get_cpi_benchmark_api(country: str = Query("vn"), genre: str = Query("rpg"), platform: str = Query("all")):
    """Returns estimated CPI cost for given country and genre."""
    cpi = cpi_simulator.get_cpi_benchmark(country=country, genre=genre, platform=platform)
    return {"country": country.upper(), "genre": genre.title(), "platform": platform.upper(), "estimated_cpi": cpi}

@router.post("/api/mobile/simulator/run")
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

# --- TikTok & Meta UA Campaign Optimizer & ROAS Pacing Endpoints ---
@router.get("/api/mobile/campaign/dayparting-benchmarks")
async def get_ua_dayparting_benchmarks_api():
    """Returns 24-hour behavioral curves, network mechanics, and kill-switch rules."""
    return ua_optimizer.get_benchmarks()

@router.post("/api/mobile/campaign/optimize-pacing")
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

# --- TikTok Creator & Viral K-Factor Endpoints ---
@router.post("/api/mobile/viral/k-factor")
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

@router.post("/api/mobile/viral/tiktok-forecast")
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
@router.get("/api/mobile/webhook/config")
async def get_webhook_config_api():
    """Returns saved webhook bot configuration."""
    return bot_service.get_config()

@router.post("/api/mobile/webhook/config")
async def save_webhook_config_api(request: Request):
    """Saves Discord and Telegram webhook credentials and preferences."""
    payload = await request.json()
    return bot_service.save_config(payload)

@router.post("/api/mobile/webhook/test")
async def test_webhook_api():
    """Sends an instant test alert to enabled webhook channels."""
    return bot_service.trigger_test_alert()

@router.post("/api/mobile/webhook/trigger-digest")
async def trigger_morning_digest_api():
    """Triggers immediate broadcast of morning market digest."""
    return bot_service.trigger_morning_digest()

# --- Executive Pitch Deck Generator Endpoints ---
@router.post("/api/mobile/deck/generate")
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
@router.post("/api/mobile/ab-test/sample-size")
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

@router.post("/api/mobile/ab-test/evaluate")
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
@router.get("/api/mobile/mediation/benchmarks")
async def get_mediation_benchmarks_api():
    """Returns regional eCPM benchmarks and standard waterfall templates."""
    return ad_mediation_engine.get_benchmarks()

@router.post("/api/mobile/mediation/simulate")
async def simulate_mediation_api(request: Request):
    """Simulates ad revenue yield, blended ARPDAU, and full LTV/ROAS break-even curve."""
    payload = await request.json()
    dau = int(payload.get("dau", 50000))
    session_mins = int(payload.get("session_mins", 15))
    sessions_per_day = float(payload.get("sessions_per_day", 2.4))
    cooldown = int(payload.get("cooldown_secs", 75))
    rewarded = float(payload.get("rewarded_watches", 2.8))
    banner_enabled = bool(payload.get("banner_enabled", True))
    aoa_enabled = bool(payload.get("aoa_enabled", True))
    tier1_pct = float(payload.get("tier1_pct", 30.0))
    tier2_pct = float(payload.get("tier2_pct", 25.0))
    tier3_pct = float(payload.get("tier3_pct", 45.0))
    iap_share_pct = float(payload.get("iap_share_pct", 30.0))
    target_cpi = float(payload.get("target_cpi", 0.65))

    return ad_mediation_engine.simulate(
        dau=dau,
        avg_session_mins=session_mins,
        sessions_per_day=sessions_per_day,
        interstitial_cooldown_secs=cooldown,
        rewarded_watches_per_user=rewarded,
        banner_enabled=banner_enabled,
        aoa_enabled=aoa_enabled,
        tier1_pct=tier1_pct,
        tier2_pct=tier2_pct,
        tier3_pct=tier3_pct,
        iap_share_pct=iap_share_pct,
        target_cpi=target_cpi
    )

# --- Playable Ad Canvas Sandbox & MRAID Exporter Endpoints ---
@router.get("/api/mobile/playable/templates")
async def get_playable_templates_api():
    """Returns high-converting playable ad templates."""
    return playable_generator.get_templates()

@router.post("/api/mobile/playable/export-mraid")
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
@router.get("/api/mobile/voiceover/meta")
async def get_voiceover_meta_api():
    """Returns supported localization markets and emotion tones."""
    return {
        "markets": voiceover_studio.get_supported_markets(),
        "emotions": voiceover_studio.get_supported_emotions()
    }

@router.post("/api/mobile/voiceover/generate")
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

# --- UA Ad Fraud & Click Injection Diagnostic Scanner Endpoints ---
@router.get("/api/mobile/fraud/samples")
async def get_fraud_samples_api():
    """Returns preset benchmark networks for fraud comparison."""
    return ad_fraud_scanner.get_sample_networks()

@router.post("/api/mobile/fraud/audit")
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
