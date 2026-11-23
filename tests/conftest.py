import sqlite3
from datetime import date, timedelta

import pytest

from app import config


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    """Points the app at an empty temporary SQLite database."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", db_file)
    from app.database.db import init_db
    init_db()
    from app.analytics import calibration
    calibration.invalidate_cache()
    yield db_file
    calibration.invalidate_cache()


def make_record(game_id, rank, snapshot_date, platform="mobile_appstore", country="us",
                ranking_type="top_grossing", title=None, genre="Puzzle"):
    d = snapshot_date if isinstance(snapshot_date, str) else snapshot_date.isoformat()
    return {
        "snapshot_date": d,
        "snapshot_time": f"{d} 06:00:00",
        "period_type": "daily",
        "week_number": "2026-W47",
        "platform": platform,
        "country": country,
        "ranking_type": ranking_type,
        "rank": rank,
        "game_id": game_id,
        "title": title or f"Game {game_id}",
        "developer": "Dev",
        "genre": genre,
        "score": 4.5,
        "price": "Free",
        "player_count": 0,
        "estimated_downloads": "",
        "icon_url": "",
        "store_url": "",
        "rank_change_day": 0,
        "rank_change_week": 0,
        "is_new_entry": 0,
    }


@pytest.fixture()
def insert(temp_db):
    from app.database.db import save_snapshot_batch

    def _insert(records):
        save_snapshot_batch(records)
    return _insert


@pytest.fixture()
def today():
    return date.today()


def days_ago(n):
    return date.today() - timedelta(days=n)
