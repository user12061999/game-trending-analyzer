from app.analytics.revenue_estimator import RevenueEstimator
from app.analytics.revenue_history_engine import RevenueHistoryEngine
from tests.conftest import make_record, days_ago


def test_mobile_revenue_power_law_monotonic(temp_db):
    revs = [RevenueEstimator.estimate_mobile_revenue(r, country="us")["daily_revenue"] for r in (1, 5, 20, 100)]
    assert revs == sorted(revs, reverse=True)
    assert revs[0] == 1500000


def test_country_benchmark_fallback(temp_db):
    assert RevenueEstimator.estimate_mobile_revenue(1, country="zz")["daily_revenue"] == 100000


def test_steam_revenue_helper_exists_and_is_sane(temp_db):
    est = RevenueEstimator.estimate_steam_revenue(3, player_count=50000, price_str="$29.99")
    assert est["daily_revenue"] > 0
    assert est["estimated_units_sold_daily"] > 0


def test_history_is_deterministic_and_labels_sources(insert):
    insert([
        make_record("g1", 20, days_ago(10)),
        make_record("g1", 10, days_ago(6)),
        make_record("g1", 10, days_ago(0)),
    ])
    a = RevenueHistoryEngine.get_game_revenue_history("g1", days=14)
    b = RevenueHistoryEngine.get_game_revenue_history("g1", days=14)
    assert a["timeline"] == b["timeline"]  # no randomness

    by_date = {d["date"]: d for d in a["timeline"]}
    assert by_date[days_ago(10).isoformat()]["data_source"] == "snapshot"
    assert by_date[days_ago(8).isoformat()]["data_source"] == "interpolated"
    assert by_date[days_ago(8).isoformat()]["rank"] == 15  # halfway between 20 and 10
    assert by_date[days_ago(13).isoformat()]["data_source"] == "carried"
    assert a["data_quality"]["actual_snapshot_days"] == 3
    assert a["data_quality"]["is_model_estimate"] is True


def test_history_ignores_other_charts(insert):
    insert([
        make_record("g2", 50, days_ago(1), country="vn"),
        make_record("g2", 2, days_ago(0), country="us"),
    ])
    h = RevenueHistoryEngine.get_game_revenue_history("g2", days=7)
    assert h["data_quality"]["actual_snapshot_days"] == 1  # vn snapshot excluded


def test_insufficient_data_lifecycle(insert):
    insert([make_record("g3", 5, days_ago(0))])
    h = RevenueHistoryEngine.get_game_revenue_history("g3", days=30)
    assert h["data_quality"]["has_reliable_wow"] is False
    assert "Insufficient" in h["lifecycle"]["phase"]


def test_pc_history_does_not_crash(insert):
    insert([make_record("730", 1, days_ago(0), platform="pc_steam", country="global", ranking_type="most_played")])
    h = RevenueHistoryEngine.get_game_revenue_history("730", days=7)
    assert len(h["timeline"]) == 7
