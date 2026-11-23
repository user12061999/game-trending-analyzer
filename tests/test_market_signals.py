from datetime import datetime, timedelta

from app.analytics.market_signals import MarketSignals
from app.database.db import log_crawl
from tests.conftest import make_record, days_ago


def test_sustained_breakout_detected(insert):
    recs = []
    for i, rank in enumerate([40, 35, 30, 22, 18]):
        recs.append(make_record("steady", rank, days_ago(4 - i)))
    for i, rank in enumerate([40, 40, 40, 40, 10]):
        recs.append(make_record("spike", rank, days_ago(4 - i)))
    for i, rank in enumerate([10, 30, 5, 25, 4]):
        recs.append(make_record("noisy", rank, days_ago(4 - i)))
    insert(recs)
    res = {r["game_id"]: r for r in MarketSignals.get_sustained_breakouts(window_days=7)}
    assert "steady" in res and res["steady"]["net_gain"] == 22
    assert res["steady"]["consistency_pct"] == 100.0
    assert res["spike"]["is_single_spike"] is True
    assert res["steady"]["momentum_score"] > res["spike"]["momentum_score"]
    assert "noisy" not in res  # only 50% of steps were non-drops


def test_breakout_needs_min_observations(insert):
    insert([make_record("two", 50, days_ago(1)), make_record("two", 10, days_ago(0))])
    assert MarketSignals.get_sustained_breakouts(window_days=7) == []


def test_genre_trends_week_over_week(insert):
    recs = []
    # previous week: Puzzle dominates; this week: RPG dominates
    for d in (8, 9):
        recs += [make_record("p1", 1, days_ago(d), genre="Puzzle"), make_record("r1", 9, days_ago(d), genre="RPG")]
    for d in (0, 1):
        recs += [make_record("p1", 9, days_ago(d), genre="Puzzle"), make_record("r1", 1, days_ago(d), genre="Role Playing, RPG")]
    insert(recs)
    t = MarketSignals.get_genre_trends()
    assert t["has_comparison"] is True
    g = {x["genre"]: x for x in t["genres"]}
    assert g["Puzzle"]["direction"] == "down"
    assert "Role Playing" in g and g["Role Playing"]["direction"] == "up"
    for x in t["genres"]:
        assert 0 <= x["share_pct"] <= 100


def test_data_health_statuses(temp_db):
    log_crawl("pc_steam", "global", "most_played", 50, "success")
    log_crawl("mobile_appstore", "us", "top_free", 0, "failed", "Crawler returned 0 records")
    h = MarketSignals.get_data_health()
    st = {(s["platform"], s["ranking_type"]): s["status"] for s in h["sources"]}
    assert st[("pc_steam", "most_played")] == "ok"
    assert st[("mobile_appstore", "top_free")] == "failing"
    assert h["overall_status"] == "degraded"

    later = datetime.now() + timedelta(hours=48)
    h2 = MarketSignals.get_data_health(now=later)
    st2 = {(s["platform"], s["ranking_type"]): s["status"] for s in h2["sources"]}
    assert st2[("pc_steam", "most_played")] == "stale"
