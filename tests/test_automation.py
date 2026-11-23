import sqlite3

from app import config
from app.services import crawl_lock
from app.services.crawl_service import CrawlService
from tests.conftest import make_record, days_ago


class FakeOrchestrator:
    def __init__(self):
        self.calls = 0

    def run_full_crawl(self, countries=None):
        self.calls += 1
        return {"total_items": 7}


class FakeAnalyzer:
    def get_market_overview(self):
        return {"rising_games": []}


def _service(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    orch = FakeOrchestrator()
    return CrawlService(orch, FakeAnalyzer(), notifier=None), orch


def test_lock_blocks_second_process(temp_db, tmp_path, monkeypatch):
    service, orch = _service(tmp_path, monkeypatch)
    assert crawl_lock.acquire("other-process")
    assert service.is_crawling is True
    assert service.run_crawl(reason="test") is None
    assert orch.calls == 0
    crawl_lock.release()
    assert service.run_crawl(reason="test")["total_items"] == 7
    assert not crawl_lock.lock_path().exists()  # released after the run


def test_stale_lock_is_ignored(temp_db, tmp_path, monkeypatch):
    import os, time
    service, orch = _service(tmp_path, monkeypatch)
    crawl_lock.lock_path().write_text("{}", encoding="utf-8")
    old = time.time() - crawl_lock.STALE_AFTER_SECONDS - 60
    os.utime(crawl_lock.lock_path(), (old, old))
    assert service.run_crawl(reason="test") is not None
    assert orch.calls == 1


def test_skip_if_already_crawled_today(temp_db, insert, tmp_path, monkeypatch):
    service, orch = _service(tmp_path, monkeypatch)
    assert service.run_crawl(reason="auto", skip_if_done_today=True) is not None  # no data yet -> crawls
    insert([make_record("g", 1, days_ago(0))])
    assert service.run_crawl(reason="auto", skip_if_done_today=True) is None
    assert service.last_run["skipped"]
    assert orch.calls == 1
    assert service.run_crawl(reason="manual") is not None  # manual crawl still allowed
    assert orch.calls == 2


def test_crawl_once_script_exit_codes(temp_db, insert, tmp_path, monkeypatch):
    import scripts.crawl_once as co
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    import app.crawlers.orchestrator as orch_mod
    monkeypatch.setattr(orch_mod.CrawlerOrchestrator, "run_full_crawl", lambda self, countries=None: {"total_items": 3})
    assert co.main([]) == 0
    insert([make_record("g", 1, days_ago(0))])
    assert co.main([]) == 0  # skipped
    assert crawl_lock.acquire("someone-else")
    assert co.main(["--force"]) == 2
    crawl_lock.release()
    assert (tmp_path / "logs").exists()


def test_backup_keeps_newest(temp_db, insert, tmp_path):
    import scripts.backup_db as b
    insert([make_record("g", 1, days_ago(0))])
    out_dir = tmp_path / "bk"
    out_dir.mkdir()
    stem = config.DB_PATH.stem
    for d in ("2026-01-01_000000", "2026-01-08_000000", "2026-01-15_000000"):
        (out_dir / f"{stem}_{d}.db").write_bytes(b"old")
    new = b.backup(keep=2, backup_dir=out_dir)
    remaining = sorted(p.name for p in out_dir.glob("*.db"))
    assert remaining == [f"{stem}_2026-01-15_000000.db", new.name]
    n = sqlite3.connect(new).execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    assert n == 1
