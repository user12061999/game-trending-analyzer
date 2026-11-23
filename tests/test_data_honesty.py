from datetime import date, timedelta

from app.analytics.review_miner import ReviewMiner
from app.crawlers import mobile_radar_crawler as radar_mod
from app.database import db


def _miner(monkeypatch, apple=None, gp=None, steam=None):
    m = ReviewMiner.__new__(ReviewMiner)
    monkeypatch.setattr(m, "fetch_apple_reviews", lambda *a, **k: list(apple or []), raising=False)
    monkeypatch.setattr(m, "fetch_google_play_reviews", lambda *a, **k: list(gp or []), raising=False)
    monkeypatch.setattr(m, "fetch_steam_reviews", lambda *a, **k: list(steam or []), raising=False)
    return m


def test_no_reviews_means_no_fake_reviews(monkeypatch):
    res = _miner(monkeypatch).analyze_reviews("ios_123", "Some Game")
    assert res["status"] == "no_reviews"
    assert res["sample_reviews"] == []
    assert res["churn_drivers"] == [] and res["studio_attack_playbook"] is None
    assert "App Store" in res["message"]


def test_categories_come_from_review_text(monkeypatch):
    reviews = [
        {"rating": 1, "title": "", "content": "Game keeps crashing after update"},
        {"rating": 1, "title": "", "content": "too many ads, every level"},
        {"rating": 2, "title": "", "content": "crash on start"},
        {"rating": 2, "title": "", "content": "boring"},
        {"rating": 5, "title": "", "content": "Beautiful graphics and fun"},
    ]
    res = _miner(monkeypatch, gp=reviews).analyze_reviews("gp_com.example.game", "Ex")
    assert res["status"] == "ok" and res["review_source"].startswith("Google Play")
    churn = {c["category"]: c for c in res["churn_drivers"]}
    tech = next(c for k, c in churn.items() if "Kỹ Thuật" in k)
    assert tech["mentions"] == 2 and tech["frequency_pct"] == 50.0  # 2 of 4 negative reviews
    assert "crash" in tech["sample_quote"].lower()
    assert not any("Gacha" in k for k in churn)  # nobody complained about gacha
    assert res["studio_attack_playbook"]["actionable_steps"][0]["evidence"].startswith("2 đánh giá")
    assert len(res["retention_hooks"]) >= 1


def test_store_is_picked_from_game_id(monkeypatch):
    m = _miner(monkeypatch, steam=[{"rating": 5, "content": "fun"}])
    assert m.analyze_reviews("730", platform="pc_steam")["review_source"] == "Steam"


def test_radar_marks_sources_and_skips_past_curated(temp_db, monkeypatch):
    future = (date.today() + timedelta(days=40)).isoformat()
    past = (date.today() - timedelta(days=5)).isoformat()
    curated = [
        {"title": "Future Curated", "platform": "iOS / Android", "expected_release_date": future, "threat_level": "HIGH"},
        {"title": "Old Curated", "platform": "iOS / Android", "expected_release_date": past, "threat_level": "CRITICAL"},
    ]
    live = [{"title": "Live Preorder", "platform": "iOS", "expected_release_date": future, "hype_score": None,
             "threat_level": "MEDIUM", "data_source": "app_store_live"}]
    crawler = radar_mod.MobileRadarCrawler()
    crawler.curated_games = curated
    monkeypatch.setattr(crawler, "crawl_app_store_preorders", lambda countries=None: live)
    res = crawler.run_radar_update()
    assert res["curated_count"] == 1 and res["live_count"] == 1 and res["curated_skipped_released"] == 1

    games = {g["title"]: g for g in db.get_upcoming_mobile_games()}
    assert set(games) == {"Future Curated", "Live Preorder"}
    assert games["Future Curated"]["is_verified"] is False
    assert games["Live Preorder"]["is_verified"] is True
    assert games["Live Preorder"]["hype_score"] is None
    assert games["Future Curated"]["countdown_days"] == 40
    assert db.get_radar_threat_stats()["curated_count"] == 1


def test_released_games_hidden_from_radar(temp_db):
    past = (date.today() - timedelta(days=1)).isoformat()
    db.save_upcoming_games([{"title": "Already Out", "expected_release_date": past, "data_source": "app_store_live"}])
    assert db.get_upcoming_mobile_games() == []
    assert db.get_radar_threat_stats()["total_tracked"] == 0
