import httpx

from app.analytics.mmp_webhook_engine import MMPWebhookEngine
from app.crawlers import http_utils


def test_ctit_never_invented():
    eng = MMPWebhookEngine()
    assert eng._calculate_ctit("", "") is None
    assert eng._calculate_ctit("garbage", "also garbage") is None
    assert eng._calculate_ctit("100", "105") == 5.0
    assert eng._evaluate_fraud(None, "1.1.1.1", "iPhone", "net")[0] == "CTIT_UNKNOWN"
    assert eng._evaluate_fraud(3.0, "1.1.1.1", "iPhone", "net")[0] == "CLICK_INJECTION"


def test_simulated_postbacks_are_flagged(temp_db):
    eng = MMPWebhookEngine()
    eng.generate_mock_batch(count=5)
    eng.ingest_postback({"network_name": "Real", "click_time": "100", "install_time": "160"})
    stats = eng.get_mmp_stats()
    assert stats["total_postbacks"] == 6
    assert stats["simulated_count"] == 5


def test_get_with_retry_recovers(monkeypatch):
    monkeypatch.setattr(http_utils.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(503 if calls["n"] < 3 else 200, json={"ok": True})

    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        r = http_utils.get_with_retry(c, "https://example.test/x")
    assert r.status_code == 200 and calls["n"] == 3


def test_dotenv_loader(tmp_path, monkeypatch):
    from app import config
    env = tmp_path / ".env"
    env.write_text("FOO_TEST_KEY='abc'\n# comment\nBAR_TEST_KEY=1\n", encoding="utf-8")
    monkeypatch.delenv("FOO_TEST_KEY", raising=False)
    monkeypatch.setenv("BAR_TEST_KEY", "keep")
    config._load_dotenv(env)
    import os
    assert os.environ["FOO_TEST_KEY"] == "abc"
    assert os.environ["BAR_TEST_KEY"] == "keep"
