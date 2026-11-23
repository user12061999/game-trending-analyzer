"""Run one daily crawl without starting the web server, then exit.

Used by the Windows scheduled task (see scripts/install_scheduled_tasks.ps1).
Skips automatically if today's snapshot already exists (e.g. the web server
already crawled), unless --force is given.

Exit codes: 0 = crawled or skipped, 1 = crawl failed, 2 = another crawl is running.
"""

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import config  # noqa: E402


def setup_logging() -> Path:
    log_dir = Path(config.DATA_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"crawl_{date.today():%Y-%m}.log"
    handlers = [logging.FileHandler(log_file, encoding="utf-8")]
    if sys.stdout is not None:  # pythonw.exe has no console
        handlers.append(logging.StreamHandler(sys.stdout))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        handlers=handlers, force=True)
    return log_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run one market crawl and exit.")
    parser.add_argument("--force", action="store_true", help="Crawl even if today's snapshot already exists")
    parser.add_argument("--countries", help="Comma-separated country codes (default: CRAWL_COUNTRIES from .env)")
    args = parser.parse_args(argv)

    log_file = setup_logging()
    log = logging.getLogger("crawl_once")

    from app.database.db import init_db
    from app.crawlers.orchestrator import CrawlerOrchestrator
    from app.analytics.trend_analyzer import TrendAnalyzer
    from app.notifications.notifier import AlertNotifier
    from app.services.crawl_service import CrawlService
    from app.services import crawl_lock

    init_db()
    service = CrawlService(CrawlerOrchestrator(), TrendAnalyzer(), AlertNotifier())
    countries = [c.strip() for c in args.countries.split(",") if c.strip()] if args.countries else None

    if crawl_lock.is_locked():
        log.info("Another crawl is running (%s) - exiting", crawl_lock.holder())
        return 2

    result = service.run_crawl(countries=countries, reason="windows-task",
                               skip_if_done_today=not args.force)
    last = service.last_run or {}
    if result is not None:
        log.info("Crawl finished: %s items (log: %s)", result.get("total_items", 0), log_file)
        return 0
    if last.get("skipped"):
        log.info("Skipped: %s", last["skipped"])
        return 0
    if last.get("error"):
        log.error("Crawl failed: %s", last["error"])
        return 1
    log.info("Another crawl is running - exiting")
    return 2


if __name__ == "__main__":
    sys.exit(main())
