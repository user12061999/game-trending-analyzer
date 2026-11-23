"""Crawl coordination: single-run lock, fixed-time daily schedule and startup catch-up."""

import logging
import threading
from datetime import date, datetime
from typing import List, Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import DAILY_CRAWL_HOUR, DAILY_CRAWL_MINUTE, DEFAULT_CRAWL_COUNTRIES
from app.database.db import get_db_connection

logger = logging.getLogger(__name__)


class CrawlService:
    def __init__(self, orchestrator, analyzer, notifier):
        self.orchestrator = orchestrator
        self.analyzer = analyzer
        self.notifier = notifier
        self._lock = threading.Lock()
        self.last_run: Optional[dict] = None
        self.scheduler = BackgroundScheduler()

    @property
    def is_crawling(self) -> bool:
        return self._lock.locked()

    def run_crawl(self, countries: Optional[List[str]] = None, reason: str = "manual") -> Optional[dict]:
        """Runs a full crawl unless one is already running. Returns None if busy."""
        if not self._lock.acquire(blocking=False):
            logger.info("Crawl (%s) skipped: another crawl is running", reason)
            return None
        started = datetime.now()
        try:
            logger.info("Starting crawl (%s)", reason)
            result = self.orchestrator.run_full_crawl(countries=countries or DEFAULT_CRAWL_COUNTRIES)
            try:
                overview = self.analyzer.get_market_overview()
                for game in overview.get("rising_games", []):
                    self.notifier.dispatch_breakout_alert(game)
            except Exception as e:
                logger.warning("Breakout alert dispatch failed: %s", e)
            self.last_run = {
                "reason": reason,
                "started_at": started.isoformat(timespec="seconds"),
                "finished_at": datetime.now().isoformat(timespec="seconds"),
                "total_items": result.get("total_items", 0),
            }
            return result
        except Exception as e:
            logger.error("Crawl (%s) failed: %s", reason, e)
            self.last_run = {
                "reason": reason,
                "started_at": started.isoformat(timespec="seconds"),
                "finished_at": datetime.now().isoformat(timespec="seconds"),
                "error": str(e),
            }
            return None
        finally:
            self._lock.release()

    def run_crawl_async(self, countries: Optional[List[str]] = None, reason: str = "manual") -> bool:
        """Starts a crawl in a background thread. Returns False if one is already running."""
        if self.is_crawling:
            return False
        threading.Thread(target=self.run_crawl, args=(countries, reason), daemon=True).start()
        return True

    @staticmethod
    def has_snapshot_for(day: date) -> bool:
        conn = get_db_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM snapshots WHERE snapshot_date = ? LIMIT 1", (day.isoformat(),)
            ).fetchone()
            return row is not None
        finally:
            conn.close()

    def catch_up_if_needed(self) -> bool:
        """If today's snapshot is missing (app was off at schedule time), crawl now in background."""
        if self.has_snapshot_for(date.today()):
            return False
        logger.info("No snapshot for today yet — running catch-up crawl in background")
        return self.run_crawl_async(reason="startup-catch-up")

    def start_schedule(self, digest_job) -> None:
        self.scheduler.add_job(
            lambda: self.run_crawl(reason="scheduled"),
            "cron",
            hour=DAILY_CRAWL_HOUR,
            minute=DAILY_CRAWL_MINUTE,
            id="daily_crawl_job",
            replace_existing=True,
            misfire_grace_time=3600,
            coalesce=True,
        )
        self.scheduler.add_job(
            digest_job, "cron", hour=8, minute=0, id="daily_digest_job",
            replace_existing=True, misfire_grace_time=3600, coalesce=True,
        )
        self.scheduler.start()

    def next_scheduled_run(self) -> Optional[str]:
        job = self.scheduler.get_job("daily_crawl_job") if self.scheduler.running else None
        if job and job.next_run_time:
            return job.next_run_time.isoformat(timespec="seconds")
        return None

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
