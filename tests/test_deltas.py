from app.crawlers.orchestrator import CrawlerOrchestrator
from tests.conftest import make_record, days_ago


def test_day_and_week_deltas(insert):
    insert([
        make_record("a", 10, days_ago(7)),
        make_record("a", 8, days_ago(2)),   # most recent earlier snapshot for this chart
        make_record("b", 3, days_ago(2)),
    ])
    recs = [
        make_record("a", 5, days_ago(0)),   # climbed 3 vs prev, 5 vs last week
        make_record("b", 6, days_ago(0)),   # dropped 3
        make_record("c", 1, days_ago(0)),   # brand new
    ]
    out = {r["game_id"]: r for r in CrawlerOrchestrator.__new__(CrawlerOrchestrator).calculate_deltas(recs)}
    assert out["a"]["rank_change_day"] == 3
    assert out["a"]["rank_change_week"] == 5
    assert out["a"]["is_new_entry"] == 0
    assert out["b"]["rank_change_day"] == -3
    assert out["b"]["rank_change_week"] == 0
    assert out["c"]["is_new_entry"] == 1
    assert out["c"]["rank_change_day"] == 0


def test_previous_date_is_per_chart(insert):
    # Another chart was crawled yesterday, but this chart's last crawl was 3 days ago.
    insert([
        make_record("x", 20, days_ago(3), country="vn"),
        make_record("z", 1, days_ago(1), country="us"),
    ])
    recs = [make_record("x", 15, days_ago(0), country="vn")]
    out = CrawlerOrchestrator.__new__(CrawlerOrchestrator).calculate_deltas(recs)[0]
    assert out["rank_change_day"] == 5
    assert out["is_new_entry"] == 0


def test_returning_game_is_not_new(insert):
    insert([make_record("r", 40, days_ago(20))])
    out = CrawlerOrchestrator.__new__(CrawlerOrchestrator).calculate_deltas([make_record("r", 30, days_ago(0))])[0]
    assert out["is_new_entry"] == 0
