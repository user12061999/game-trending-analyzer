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

    # Watchlist table for user tracked games & rivals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        developer TEXT,
        platform TEXT,
        country TEXT,
        genre TEXT,
        icon_url TEXT,
        store_url TEXT,
        added_at TEXT NOT NULL,
        notes TEXT,
        is_rival INTEGER DEFAULT 0
    );
    """)

    # Upcoming Mobile Games Radar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS upcoming_mobile_games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        developer TEXT,
        publisher TEXT,
        platform TEXT DEFAULT 'iOS / Android',
        regions TEXT DEFAULT 'Global',
        genre TEXT,
        expected_release_date TEXT,
        countdown_days INTEGER DEFAULT 0,
        hype_score INTEGER DEFAULT 80,
        pre_reg_count TEXT,
        threat_level TEXT DEFAULT 'MEDIUM',
        target_audience TEXT,
        threat_analysis TEXT,
        tactical_advice TEXT,
        icon_url TEXT,
        banner_url TEXT,
        store_url TEXT,
        is_tracked INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PRE_REGISTRATION',
        updated_at TEXT,
        UNIQUE(title, platform)
    );
    """)

    # MMP Live Webhook Postbacks & Fraud Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mmp_postbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        received_at TEXT NOT NULL,
        mmp_provider TEXT NOT NULL,
        network_name TEXT NOT NULL,
        campaign_name TEXT,
        advertising_id TEXT,
        ip_address TEXT,
        click_time TEXT,
        install_time TEXT,
        ctit_seconds REAL,
        country TEXT,
        device_model TEXT,
        fraud_verdict TEXT,
        fraud_score REAL,
        is_rejected INTEGER DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_mmp_postbacks_time
    ON mmp_postbacks(received_at, network_name);
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

def add_to_watchlist(game_id: str, title: str, developer: str = "", platform: str = "", country: str = "", genre: str = "", icon_url: str = "", store_url: str = "", notes: str = "", is_rival: int = 0) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO watchlist (game_id, title, developer, platform, country, genre, icon_url, store_url, added_at, notes, is_rival)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(game_id) DO UPDATE SET
        notes = excluded.notes,
        is_rival = excluded.is_rival
    """, (game_id, title, developer, platform, country, genre, icon_url, store_url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), notes, is_rival))
    conn.commit()
    conn.close()
    return True

def remove_from_watchlist(game_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE game_id = ?", (game_id,))
    conn.commit()
    conn.close()
    return True

def get_watchlist_items() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM watchlist ORDER BY is_rival ASC, added_at DESC")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def is_game_in_watchlist(game_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM watchlist WHERE game_id = ? LIMIT 1", (game_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row)

# --- Upcoming Mobile Games Radar DB Helpers ---

def save_upcoming_games(games: List[Dict[str, Any]]):
    """Saves or updates upcoming mobile games."""
    if not games:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    INSERT INTO upcoming_mobile_games (
        title, developer, publisher, platform, regions, genre,
        expected_release_date, countdown_days, hype_score, pre_reg_count,
        threat_level, target_audience, threat_analysis, tactical_advice,
        icon_url, banner_url, store_url, is_tracked, status, updated_at
    ) VALUES (
        :title, :developer, :publisher, :platform, :regions, :genre,
        :expected_release_date, :countdown_days, :hype_score, :pre_reg_count,
        :threat_level, :target_audience, :threat_analysis, :tactical_advice,
        :icon_url, :banner_url, :store_url, :is_tracked, :status, :updated_at
    )
    ON CONFLICT(title, platform) DO UPDATE SET
        developer = excluded.developer,
        publisher = excluded.publisher,
        regions = excluded.regions,
        genre = excluded.genre,
        expected_release_date = excluded.expected_release_date,
        countdown_days = excluded.countdown_days,
        hype_score = excluded.hype_score,
        pre_reg_count = excluded.pre_reg_count,
        threat_level = excluded.threat_level,
        target_audience = excluded.target_audience,
        threat_analysis = excluded.threat_analysis,
        tactical_advice = excluded.tactical_advice,
        icon_url = excluded.icon_url,
        banner_url = excluded.banner_url,
        store_url = excluded.store_url,
        status = excluded.status,
        updated_at = excluded.updated_at;
    """

    records = []
    for g in games:
        rec = dict(g)
        rec.setdefault("developer", "")
        rec.setdefault("publisher", "")
        rec.setdefault("platform", "iOS / Android")
        rec.setdefault("regions", "Global")
        rec.setdefault("genre", "Game")
        rec.setdefault("expected_release_date", "")
        rec.setdefault("countdown_days", 0)
        rec.setdefault("hype_score", 80)
        rec.setdefault("pre_reg_count", "")
        rec.setdefault("threat_level", "MEDIUM")
        rec.setdefault("target_audience", "")
        rec.setdefault("threat_analysis", "")
        rec.setdefault("tactical_advice", "")
        rec.setdefault("icon_url", "")
        rec.setdefault("banner_url", "")
        rec.setdefault("store_url", "")
        rec.setdefault("is_tracked", 0)
        rec.setdefault("status", "PRE_REGISTRATION")
        rec["updated_at"] = now_str
        records.append(rec)

    cursor.executemany(query, records)
    conn.commit()
    conn.close()

def get_upcoming_mobile_games(
    region: Optional[str] = None,
    genre: Optional[str] = None,
    threat_level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Retrieves filtered list of upcoming mobile games sorted by threat level and countdown days."""
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if region and region.lower() != "all":
        conditions.append("regions LIKE ?")
        params.append(f"%{region}%")

    if genre and genre.lower() != "all":
        conditions.append("genre LIKE ?")
        params.append(f"%{genre}%")

    if threat_level and threat_level.lower() != "all":
        conditions.append("threat_level = ?")
        params.append(threat_level.upper())

    if search:
        conditions.append("(title LIKE ? OR developer LIKE ? OR publisher LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Sort order: CRITICAL > HIGH > MEDIUM > LOW, then by countdown_days ascending
    query = f"""
    SELECT *,
        CASE threat_level
            WHEN 'CRITICAL' THEN 1
            WHEN 'HIGH' THEN 2
            WHEN 'MEDIUM' THEN 3
            ELSE 4
        END as threat_rank
    FROM upcoming_mobile_games
    {where_clause}
    ORDER BY threat_rank ASC, countdown_days ASC
    LIMIT ?
    """
    params.append(limit)

    cursor.execute(query, params)
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def get_upcoming_game_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Fetches full details of a specific upcoming mobile game."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM upcoming_mobile_games WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def toggle_track_upcoming_game(item_id: int) -> bool:
    """Toggles tracked status for an upcoming game."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE upcoming_mobile_games 
    SET is_tracked = CASE WHEN is_tracked = 1 THEN 0 ELSE 1 END 
    WHERE id = ?
    """, (item_id,))
    cursor.execute("SELECT is_tracked FROM upcoming_mobile_games WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return bool(row["is_tracked"]) if row else False

def get_radar_threat_stats() -> Dict[str, Any]:
    """Computes summary KPI statistics for Mobile Radar."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM upcoming_mobile_games")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as cnt FROM upcoming_mobile_games WHERE threat_level = 'CRITICAL'")
    critical = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM upcoming_mobile_games WHERE threat_level = 'HIGH'")
    high = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM upcoming_mobile_games WHERE countdown_days <= 30 AND countdown_days > 0")
    imminent_30d = cursor.fetchone()["cnt"]

    cursor.execute("""
    SELECT genre, COUNT(*) as count 
    FROM upcoming_mobile_games 
    GROUP BY genre 
    ORDER BY count DESC 
    LIMIT 3
    """)
    top_threatened_genres = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "total_tracked": total,
        "critical_threats": critical,
        "high_threats": high,
        "imminent_30d": imminent_30d,
        "top_threatened_genres": top_threatened_genres
    }
