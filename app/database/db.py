"""Database access layer and SQLite schema definition."""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables and indexes if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Snapshots table stores ranking items at a point in time
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_date TEXT NOT NULL,
        snapshot_time TEXT NOT NULL,
        period_type TEXT NOT NULL,
        week_number TEXT NOT NULL,
        platform TEXT NOT NULL,
        country TEXT NOT NULL,
        ranking_type TEXT NOT NULL,
        rank INTEGER NOT NULL,
        game_id TEXT NOT NULL,
        title TEXT NOT NULL,
        developer TEXT,
        genre TEXT,
        score REAL,
        price TEXT,
        player_count INTEGER DEFAULT 0,
        estimated_downloads TEXT,
        icon_url TEXT,
        store_url TEXT,
        rank_change_day INTEGER DEFAULT 0,
        rank_change_week INTEGER DEFAULT 0,
        is_new_entry INTEGER DEFAULT 0,
        UNIQUE(snapshot_date, platform, country, ranking_type, game_id)
    );
    """)

    # Index for fast querying by date, platform, ranking_type, country
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_snapshots_lookup 
    ON snapshots(snapshot_date, platform, country, ranking_type);
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_snapshots_game
    ON snapshots(game_id, platform);
    """)

    # Crawl logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crawled_at TEXT NOT NULL,
        platform TEXT NOT NULL,
        country TEXT NOT NULL,
        ranking_type TEXT NOT NULL,
        items_count INTEGER NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT
    );
    """)

    # AI / Market Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        period TEXT NOT NULL,
        target_date TEXT NOT NULL,
        title TEXT NOT NULL,
        summary_markdown TEXT NOT NULL,
        highlights_json TEXT
    );
    """)

    conn.commit()
    conn.close()

def save_snapshot_batch(records: List[Dict[str, Any]]):
    """Saves or updates a batch of snapshot ranking records."""
    if not records:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO snapshots (
        snapshot_date, snapshot_time, period_type, week_number,
        platform, country, ranking_type, rank,
        game_id, title, developer, genre,
        score, price, player_count, estimated_downloads,
        icon_url, store_url, rank_change_day, rank_change_week, is_new_entry
    ) VALUES (
        :snapshot_date, :snapshot_time, :period_type, :week_number,
        :platform, :country, :ranking_type, :rank,
        :game_id, :title, :developer, :genre,
        :score, :price, :player_count, :estimated_downloads,
        :icon_url, :store_url, :rank_change_day, :rank_change_week, :is_new_entry
    )
    ON CONFLICT(snapshot_date, platform, country, ranking_type, game_id) DO UPDATE SET
        rank = excluded.rank,
        title = excluded.title,
        developer = excluded.developer,
        genre = excluded.genre,
        score = excluded.score,
        price = excluded.price,
        player_count = excluded.player_count,
        estimated_downloads = excluded.estimated_downloads,
        icon_url = excluded.icon_url,
        store_url = excluded.store_url,
        rank_change_day = excluded.rank_change_day,
        rank_change_week = excluded.rank_change_week,
        is_new_entry = excluded.is_new_entry;
    """

    cursor.executemany(query, records)
    conn.commit()
    conn.close()

def log_crawl(platform: str, country: str, ranking_type: str, items_count: int, status: str, error_message: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO crawl_history (crawled_at, platform, country, ranking_type, items_count, status, error_message)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), platform, country, ranking_type, items_count, status, error_message))
    conn.commit()
    conn.close()
