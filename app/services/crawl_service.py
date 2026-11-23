"""Crawl coordination: single-run lock, fixed-time daily schedule and startup catch-up."""

import logging
import threading
from datetime import date, datetime
from typing import List, Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import DAILY_CRAWL_HOUR, DAILY_CRAWL_MINUTE, DEFAULT_CRAWL_COUNTRIES
from app.database.db import get_db_connection
from app.services import crawl_lock

logger = logging.getLogger(__name__)


class CrawlService:
    def __init__(self, orchestrator, analyzer, notifier):
        self.orchestrator = orchestrator
        self.analyzer = analyzer
        self.notifier = notifier
        self._lock = threading.Lock()
        self.last_run: Optional[dict] = None
        self.last_alerts: Optional[dict] = None
        self.scheduler = BackgroundScheduler()

    @property
    def is_crawling(self) -> bool:
        # True if this process is crawling, or another process (e.g. the scheduled task) holds the lock
        return self._lock.locked() or crawl_lock.is_locked()

    def run_crawl(self, countries: Optional[List[str]] = None, reason: str = "manual",
                  skip_if_done_today: bool = False) -> Optional[dict]:
        """Runs a full crawl unless one is already running (in any process). Returns None if skipped.

        skip_if_done_today: used by automatic runs (scheduler, catch-up, Windows task) so the
        server and the scheduled task don't crawl the same day twice.
        """
        if not self._lock.acquire(blocking=False):
            logger.info("Crawl (%s) skipped: another crawl is running", reason)
            return None
        if not crawl_lock.acquire(owner=reason):
            self._lock.release()
            logger.info("Crawl (%s) skipped: another process holds the crawl lock (%s)", reason, crawl_lock.holder())
            return None
        started = datetime.now()
        try:
            if skip_if_done_today and self.has_snapshot_for(date.today()):
                logger.info("Crawl (%s) skipped: today's snapshot already exists", reason)
                self.last_run = {"reason": reason, "started_at": started.isoformat(timespec="seconds"),
                                 "skipped": "already crawled today"}
                return None
            logger.info("Starting crawl (%s)", reason)
            result = self.orchestrator.run_full_crawl(countries=countries or DEFAULT_CRAWL_COUNTRIES)
            self.last_alerts = self._run_alerts(crawl_ok=result.get("total_items", 0) > 0)
            self.last_run = {
                "reason": reason,
                "started_at": started.isoformat(timespec="seconds"),
                "finished_at": datetime.now().isoformat(timespec="seconds"),
                "total_items": result.get("total_items", 0),
            }
            return result
        except Exception as e:
            logger.error("Crawl (%s) failed: %s", reason, e)
            self.last_alerts = self._run_alerts(crawl_ok=False)
            self.last_run = {
                "reason": reason,
                "started_at": started.isoformat(timespec="seconds"),
                "finished_at": datetime.now().isoformat(timespec="seconds"),
                "error": str(e),
            }
            return None
        finally:
            crawl_lock.release()
            self._lock.release()

    def _run_alerts(self, crawl_ok: bool) -> Optional[dict]:
        """Digest / breakout / sustained / health / weekly alerts, each deduplicated via alert_log."""
        if self.notifier is None:
            return None
        try:
            from app.notifications.alert_engine import AlertEngine
            summary = AlertEngine(self.notifier, self.analyzer).run_after_crawl(crawl_ok=crawl_ok)
            logger.info("Alerts after crawl: %s", summary)
            return summary
        except Exception as e:
            logger.warning("Alert dispatch failed: %s", e)
            return {"error": str(e)}

    def send_daily_digest_if_needed(self) -> Optional[dict]:
        """08:00 safety net: sends today's digest only if no crawl has sent it yet."""
        if self.notifier is None:
            return None
        from app.notifications.alert_engine import AlertEngine
        config = self.notifier.get_config()
        if not self.notifier.has_channel(config):
            return {"skipped": "no channel"}
        return AlertEngine(self.notifier, self.analyzer).send_daily_digest(config)

    def run_crawl_async(self, countries: Optional[List[str]] = None, reason: str = "manual",
                        skip_if_done_today: bool = False) -> bool:
        """Starts a crawl in a background thread. Returns False if one is already running."""
        if self.is_crawling:
            return False
        threading.Thread(target=self.run_crawl, args=(countries, reason, skip_if_done_today), daemon=True).start()
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
        return self.run_crawl_async(reason="startup-catch-up", skip_if_done_today=True)

    def start_schedule(self, digest_job) -> None:
        self.scheduler.add_job(
            lambda: self.run_crawl(reason="scheduled", skip_if_done_today=True),
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
