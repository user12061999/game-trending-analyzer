from datetime import date, timedelta

import pytest

from app.database.db import log_crawl
from app.notifications import notifier as notifier_mod
from app.notifications.alert_engine import AlertEngine
from app.notifications.notifier import AlertNotifier
from tests.conftest import make_record, days_ago


@pytest.fixture()
def notif(temp_db, tmp_path, monkeypatch):
    """AlertNotifier with a temp config file and captured (not sent) messages."""
    monkeypatch.setattr(notifier_mod, "CONFIG_PATH", tmp_path / "alerts_config.json")
    n = AlertNotifier()
    n.save_config({"telegram_bot_token": "t", "telegram_chat_id": "c"})
    sent = []
    monkeypatch.setattr(n, "send_telegram_message", lambda bot_token, chat_id, text: sent.append(text) or True)
    monkeypatch.setattr(n, "send_discord_message", lambda **kw: sent.append(kw["title"]) or True)
    n.sent = sent
    return n


def test_save_config_keeps_other_keys(notif):
    notif.save_config({"gemini_api_key": "KEY"})
    notif.save_config({"breakout_threshold": 20})  # alert form doesn't include the gemini key
    cfg = notif.get_config()
    assert cfg["gemini_api_key"] == "KEY"
    assert cfg["breakout_threshold"] == 20


def test_no_channel_sends_nothing(temp_db, tmp_path, monkeypatch):
    monkeypatch.setattr(notifier_mod, "CONFIG_PATH", tmp_path / "empty.json")
    res = AlertEngine(AlertNotifier()).run_after_crawl()
    assert "skipped" in res


def test_breakout_alert_has_cooldown(notif, insert):
    rec = make_record("hot", 2, days_ago(0), title="Hot <Game> & Co")
    rec["rank_change_day"] = 30
    insert([rec])
    eng = AlertEngine(notif)
    cfg = notif.get_config()
    assert eng.send_breakout_alerts(cfg)["sent"] == 1
    assert eng.send_breakout_alerts(cfg)["sent"] == 0  # within cooldown
    tg = [m for m in notif.sent if "CẢNH BÁO HIỆN TƯỢNG" in m][0]
    assert "Hot &lt;Game&gt; &amp; Co" in tg  # escaped for Telegram HTML


def test_daily_digest_once_per_day(notif, insert):
    insert([make_record("g", 1, days_ago(0))])
    eng = AlertEngine(notif)
    cfg = notif.get_config()
    assert eng.send_daily_digest(cfg)["sent"] is True
    assert eng.send_daily_digest(cfg)["sent"] is False
    assert eng.send_daily_digest(cfg, force=True)["sent"] is True


def test_sustained_alert_once_per_window(notif, insert):
    insert([make_record("steady", r, days_ago(4 - i)) for i, r in enumerate([40, 34, 28, 22, 15])])
    eng = AlertEngine(notif)
    cfg = notif.get_config()
    assert eng.send_sustained_alerts(cfg)["sent"] == 1
    assert eng.send_sustained_alerts(cfg)["sent"] == 0
    assert any("BỨT PHÁ BỀN VỮNG" in m for m in notif.sent)


def test_health_alert_once_per_day_per_problem(notif):
    log_crawl("mobile_appstore", "us", "top_free", 0, "failed", "boom")
    eng = AlertEngine(notif)
    cfg = notif.get_config()
    assert eng.check_health(cfg)["sent"] is True
    assert eng.check_health(cfg)["sent"] is False
    log_crawl("pc_steam", "global", "most_played", 0, "failed", "down")  # new problem -> new alert
    assert eng.check_health(cfg)["sent"] is True


def test_weekly_digest_rules(notif, insert):
    recs = []
    for d in (8, 9):
        recs += [make_record("p", 1, days_ago(d), genre="Puzzle"), make_record("r", 9, days_ago(d), genre="RPG")]
    for d in (0, 1):
        recs += [make_record("p", 9, days_ago(d), genre="Puzzle"), make_record("r", 1, days_ago(d), genre="RPG")]
    insert(recs)
    eng = AlertEngine(notif)
    today = date.today()
    cfg = {**notif.get_config(), "weekly_digest_weekday": 6}
    if today.weekday() < 6:
        assert "skipped" in eng.send_weekly_digest(cfg, today=today)
    cfg["weekly_digest_weekday"] = 0  # Monday: any day of the week is "on/after"
    assert eng.send_weekly_digest(cfg, today=today)["sent"] is True
    assert eng.send_weekly_digest(cfg, today=today)["sent"] is False  # once per ISO week


def test_failed_crawl_only_runs_health(notif, insert):
    rec = make_record("hot", 2, days_ago(0))
    rec["rank_change_day"] = 30
    insert([rec])
    res = AlertEngine(notif).run_after_crawl(crawl_ok=False)
    assert set(res) == {"health"}
