"""Calls every parameter-free GET endpoint to catch import/NameError regressions."""
from fastapi.testclient import TestClient

from tests.conftest import make_record, days_ago


def test_get_endpoints_do_not_500(insert, monkeypatch):
    import app.main as main
    # Don't start the scheduler / catch-up crawl during tests
    monkeypatch.setattr(main.crawl_service, "start_schedule", lambda *a, **k: None)
    monkeypatch.setattr(main.crawl_service, "catch_up_if_needed", lambda: False)
    monkeypatch.setattr(main.orchestrator.mobile_radar_crawler, "run_radar_update", lambda: {})
    insert([make_record("g1", 3, days_ago(0)), make_record("730", 1, days_ago(0), platform="pc_steam",
                                                           country="global", ranking_type="most_played")])
    skip_prefixes = ("/api/steam/app", "/api/radar/refresh")
    with TestClient(main.app) as client:
        for route in main.app.routes:
            methods = getattr(route, "methods", set()) or set()
            path = route.path
            if "GET" not in methods or path.startswith(skip_prefixes) or path in ("/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"):
                continue
            if "{" in path:
                path = path.replace("{game_id}", "g1").replace("{app_id}", "730")
                if "{" in path:
                    continue
            resp = client.get(path)
            assert resp.status_code < 500, f"{path} -> {resp.status_code}: {resp.text[:200]}"


def test_all_referenced_static_files_exist():
    import re
    from app.config import BASE_DIR
    html = (BASE_DIR / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    refs = re.findall(r'(?:src|href)="/static/([^"]+)"', html)
    assert refs, "no static references found"
    for ref in refs:
        assert (BASE_DIR / "app" / "static" / ref).exists(), ref


def test_cdn_scripts_are_pinned():
    """Unpinned CDN URLs (no version / @latest) can silently break the dashboard."""
    import re
    from app.config import BASE_DIR
    html = (BASE_DIR / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    urls = re.findall(r'<script[^>]+src="(https?://[^"]+)"', html)
    assert urls
    for u in urls:
        assert "@latest" not in u, u
        assert re.search(r"[@/]\d+\.\d+\.\d+", u), f"CDN URL without pinned version: {u}"
