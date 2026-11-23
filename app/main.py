"""FastAPI application entry point for Game Market Trending Analyzer."""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.database.db import init_db, get_db_connection
from app.services.container import orchestrator, notifier, crawl_service
from app.routers import (
    market, crawl, settings, watchlist, mobile_growth, mobile_economy, mmp, steam, studio,
)


def scheduled_morning_digest_job():
    # Normally the digest is sent right after the morning crawl (server or Windows task);
    # this 08:00 job only sends it if that hasn't happened yet today.
    print(f"[{datetime.now()}] Morning digest check: {crawl_service.send_daily_digest_if_needed()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    init_db()

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

    # Daily crawl at a fixed time (DAILY_CRAWL_HOUR) + morning digest at 08:00
    crawl_service.start_schedule(scheduled_morning_digest_job)
    # If the machine was off at the scheduled time (or DB is empty), crawl now in background
    if crawl_service.catch_up_if_needed():
        print("[Startup] No snapshot for today yet - running catch-up crawl in background...")
    yield
    crawl_service.shutdown()


app = FastAPI(
    title="Game Market Trending Analyzer",
    description="Tool phân tích xu hướng thị trường Game Mobile & PC theo từng ngày, từng tuần",
    version="1.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

for module in (market, crawl, settings, watchlist, mobile_growth, mobile_economy, mmp, steam, studio):
    app.include_router(module.router)
