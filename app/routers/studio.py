"""Studio tools: GDD, pre-registration forecast, deconstructor, REA, hybrid lab, Unity."""

import json
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
    gdd_generator,
    prereg_forecaster,
    game_deconstructor,
    rea_integrator,
    hybrid_lab,
)

router = APIRouter()

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


# --- Mechanics Hybrid Lab (AI Game DNA Fusion Studio) Endpoints ---
@router.get("/api/hybrid-lab/presets")
async def get_hybrid_presets_api():
    """Returns pre-engineered high-synergy mechanic fusion templates."""
    return hybrid_lab.get_preset_combos()

@router.post("/api/hybrid-lab/fuse")
async def fuse_mechanics_api(request: Request):
    """Cross-breeds DNA of Game A and Game B into a breakthrough hybrid game concept."""
    payload = await request.json()
    game_a_id = payload.get("game_a_id", "")
    game_b_id = payload.get("game_b_id", "")
    fusion_ratio = payload.get("fusion_ratio", "50_50")
    art_style = payload.get("art_style", "Pixel Art 2D Retro")
    monetization_model = payload.get("monetization_model", "Hybrid-Casual (IAA + Battle Pass)")

    return hybrid_lab.fuse_mechanics(
        game_a_id=game_a_id,
        game_b_id=game_b_id,
        fusion_ratio=fusion_ratio,
        art_style=art_style,
        monetization_model=monetization_model
    )

# --- AI Game Concept & 1-Page GDD Generator Endpoints ---
@router.get("/api/gdd/presets")
async def get_gdd_presets_api():
    """Returns production GDD genre presets."""
    return gdd_generator.get_presets()

@router.post("/api/gdd/generate")
async def generate_gdd_api(request: Request):
    """Generates structured 1-Page Game Design Document."""
    payload = await request.json()
    return gdd_generator.generate_gdd(
        title=payload.get("title", "Project Apex Horizon"),
        genre=payload.get("genre", "Action Roguelike / Survival"),
        platform=payload.get("platform", "PC Steam & Mobile Cross-Platform"),
        target_audience=payload.get("target_audience", "Mid-Core Gamers, Fast APM enthusiasts"),
        art_style=payload.get("art_style", "Stylized Cyberpunk Anime"),
        monetization_model=payload.get("monetization_model", "Hybrid Free-to-Play")
    )

# --- Steam Wishlist & Mobile Pre-Registration Velocity Forecaster Endpoints ---
@router.get("/api/prereg-wishlist/presets")
async def get_prereg_presets_api():
    """Returns benchmark launch presets."""
    return prereg_forecaster.get_presets()

@router.post("/api/prereg-wishlist/forecast-steam")
async def forecast_steam_api(request: Request):
    """Calculates Steam launch sales and Day 1 peak CCU."""
    payload = await request.json()
    return prereg_forecaster.forecast_steam_launch(
        current_wishlists=int(payload.get("current_wishlists", 50000)),
        days_to_launch=int(payload.get("days_to_launch", 30)),
        retail_price_usd=float(payload.get("retail_price_usd", 19.99)),
        next_fest_demo_downloads=int(payload.get("next_fest_demo_downloads", 10000)),
        expected_review_score_pct=float(payload.get("expected_review_score_pct", 88.0))
    )

@router.post("/api/prereg-wishlist/forecast-mobile")
async def forecast_mobile_api(request: Request):
    """Calculates Mobile Pre-registration auto-installs and Month 1 revenue."""
    payload = await request.json()
    return prereg_forecaster.forecast_mobile_prereg(
        current_prereg=int(payload.get("current_prereg", 250000)),
        days_to_launch=int(payload.get("days_to_launch", 25)),
        projected_d1_retention=float(payload.get("projected_d1_retention", 40.0)),
        projected_d30_ltv_usd=float(payload.get("projected_d30_ltv_usd", 2.50))
    )

# --- Gameplay Deconstructor & Reverse-Engineering Clone Engine Endpoints ---
@router.get("/api/deconstruct/presets")
async def get_deconstruct_presets_api():
    """Returns benchmark reverse-engineered game blueprints."""
    return game_deconstructor.get_presets()

@router.post("/api/deconstruct/analyze")
async def analyze_deconstruct_api(request: Request):
    """Deconstructs game into reproduction blueprint (Core mechanics, physics, pacing, C# script)."""
    try:
        payload = await request.json()
    except Exception:
        body = await request.body()
        try:
            payload = json.loads(body.decode("utf-8", errors="replace"))
        except Exception:
            payload = {}

    return game_deconstructor.deconstruct_game(
        game_title=payload.get("game_title", "Vampire Survivors"),
        platform=payload.get("platform", "PC / Mobile"),
        genre_hint=payload.get("genre_hint", "Action Roguelike"),
        store_url=payload.get("store_url"),
        raw_description=payload.get("raw_description"),
        use_ai_llm=bool(payload.get("use_ai_llm", False)),
        custom_api_key=payload.get("custom_api_key")
    )

@router.get("/api/deconstruct/export-unity-zip")
@router.post("/api/deconstruct/export-unity-zip")
async def export_unity_zip_api(
    request: Request,
    title: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    genre: Optional[str] = Query(None)
):
    """Generates and downloads a complete Unity Starter Prototype Project (.zip)."""
    game_title = title or "GamePrototype"
    plat = platform or "PC / Mobile"
    gen = genre or "Action Roguelike"

    if request.method == "POST":
        try:
            body = await request.json()
            game_title = body.get("game_title") or game_title
            plat = body.get("platform") or plat
            gen = body.get("genre_hint") or body.get("genre") or gen
        except Exception:
            pass

    data = game_deconstructor.deconstruct_game(game_title=game_title, platform=plat, genre_hint=gen)
    zip_bytes = game_deconstructor.generate_unity_zip_package(data)
    clean_title = "".join(c for c in game_title if c.isalnum() or c in ("_", "-")).strip() or "Prototype"
    filename = f"{clean_title}_Unity_Starter.zip"

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.post("/api/deconstruct/art-prompts")
async def get_art_prompts_api(request: Request):
    """Generates comprehensive Midjourney / Stable Diffusion prompts for game assets."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    game_title = payload.get("game_title", "Vampire Survivors")
    art_style = payload.get("art_style", "Pixel Art 16-bit")
    genre = payload.get("genre_hint", "Action Roguelike")

    data = game_deconstructor.deconstruct_game(game_title=game_title, platform="PC / Mobile", genre_hint=genre)
    return game_deconstructor.generate_ai_art_prompts(data, art_style=art_style)

@router.post("/api/deconstruct/video-ad-script")
async def get_video_ad_script_api(request: Request):
    """Generates a viral 30-second TikTok / Facebook UA video ad script with storyboard."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    game_title = payload.get("game_title", "Vampire Survivors")
    genre = payload.get("genre_hint", "Action Roguelike")

    data = game_deconstructor.deconstruct_game(game_title=game_title, platform="PC / Mobile", genre_hint=genre)
    return game_deconstructor.generate_video_ad_script(data)

# --- REA (Reverse Engineer Anything) Endpoints ---
@router.get("/api/rea/status")
async def get_rea_status():
    """Returns engine availability and capabilities of morluto/rea."""
    return rea_integrator.get_status()

@router.post("/api/rea/analyze")
async def analyze_with_rea(request: Request):
    """Generates an in-depth REA reverse-engineering dossier for a game."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    game_title = payload.get("game_title", "Game Project")
    genre = payload.get("genre", "Action Roguelike")
    platform = payload.get("platform", "PC / Mobile")
    game_id = payload.get("game_id", "custom")
    artifact_path = payload.get("artifact_path", None)
    return rea_integrator.generate_rea_dossier(
        game_title=game_title,
        genre=genre,
        platform=platform,
        game_id=game_id,
        artifact_path=artifact_path
    )

# --- Unity Editor Importer Plugin Endpoints ---
@router.get("/api/unity/importer-script")
async def get_unity_importer_script_api():
    """Serves the Unity Editor Window C# script (GameRadarImporter.cs)."""
    script_path = BASE_DIR / "app" / "unity" / "GameRadarImporter.cs"
    if script_path.exists():
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()
        return Response(
            content=code,
            media_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="GameRadarImporter.cs"'}
        )
    return Response(content="// GameRadarImporter.cs not found", media_type="text/plain", status_code=404)
