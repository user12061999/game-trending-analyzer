"""Revenue model calibration from known (real) revenue figures.

The user records games whose real monthly revenue is known (earnings reports,
publisher statements, etc.) together with the chart rank at that time. For each
(platform, country) the model's estimate is compared with the real figure and the
median ratio becomes a multiplier applied to all future estimates.
"""

import statistics
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app import config
from app.database.db import get_db_connection

# Safety bounds so a single bad data point can't blow up every estimate
MIN_FACTOR = 0.1
MAX_FACTOR = 10.0
# Points needed before a country-specific factor is trusted; otherwise fall back to the platform-wide factor
MIN_POINTS_PER_COUNTRY = 1
MIN_POINTS_PLATFORM_WIDE = 2

_cache_lock = threading.Lock()
_cache: Dict[str, Any] = {"db": None, "factors": None}


def _clamp(v: float) -> float:
    return max(MIN_FACTOR, min(MAX_FACTOR, v))


def invalidate_cache() -> None:
    with _cache_lock:
        _cache["db"] = None
        _cache["factors"] = None


def _model_monthly(point: Dict[str, Any]) -> int:
    """Uncalibrated model estimate (monthly) for a calibration point."""
    from app.analytics.revenue_estimator import RevenueEstimator
    if point["platform"] == "pc":
        est = RevenueEstimator.estimate_pc_revenue(
            point.get("price") or "", "", point.get("player_count") or 0, point["rank"], calibrated=False
        )
    else:
        est = RevenueEstimator.estimate_mobile_revenue(
            point["rank"], country=point["country"], ranking_type=point.get("ranking_type") or "top_grossing",
            calibrated=False,
        )
    return est["monthly_revenue"]


def list_points() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM revenue_calibration ORDER BY created_at DESC, id DESC").fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
    finally:
        conn.close()


def add_point(data: Dict[str, Any]) -> Dict[str, Any]:
    platform = (data.get("platform") or "mobile").lower()
    if platform not in ("mobile", "pc"):
        raise ValueError("platform phải là 'mobile' hoặc 'pc'")
    rank = int(data.get("rank") or 0)
    actual = float(data.get("actual_monthly_revenue") or 0)
    title = (data.get("game_title") or "").strip()
    if rank < 1 or actual <= 0 or not title:
        raise ValueError("Cần game_title, rank >= 1 và actual_monthly_revenue > 0")
    country = (data.get("country") or ("global" if platform == "pc" else "us")).lower()
    conn = get_db_connection()
    try:
        cur = conn.execute("""
            INSERT INTO revenue_calibration
                (game_title, platform, country, ranking_type, rank, player_count, price,
                 actual_monthly_revenue, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, platform, country, data.get("ranking_type") or "top_grossing", rank,
            int(data.get("player_count") or 0), data.get("price") or "",
            actual, (data.get("source") or "").strip(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        new_id = cur.lastrowid
    finally:
        conn.close()
    invalidate_cache()
    return {"id": new_id}


def delete_point(point_id: int) -> bool:
    conn = get_db_connection()
    try:
        cur = conn.execute("DELETE FROM revenue_calibration WHERE id = ?", (point_id,))
        conn.commit()
        deleted = cur.rowcount > 0
    finally:
        conn.close()
    invalidate_cache()
    return deleted


def _compute_factors(points: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_key: Dict[Tuple[str, str], List[float]] = {}
    by_platform: Dict[str, List[float]] = {}
    for p in points:
        model = _model_monthly(p)
        if model <= 0:
            continue
        ratio = p["actual_monthly_revenue"] / model
        by_key.setdefault((p["platform"], p["country"]), []).append(ratio)
        by_platform.setdefault(p["platform"], []).append(ratio)
    return {
        "country": {k: _clamp(statistics.median(v)) for k, v in by_key.items() if len(v) >= MIN_POINTS_PER_COUNTRY},
        "platform": {k: _clamp(statistics.median(v)) for k, v in by_platform.items() if len(v) >= MIN_POINTS_PLATFORM_WIDE},
        "counts": {f"{k[0]}:{k[1]}": len(v) for k, v in by_key.items()},
    }


def _factors() -> Dict[str, Any]:
    db = str(config.DB_PATH)
    with _cache_lock:
        if _cache["db"] == db and _cache["factors"] is not None:
            return _cache["factors"]
    factors = _compute_factors(list_points())
    with _cache_lock:
        _cache["db"] = db
        _cache["factors"] = factors
    return factors


def get_factor(platform: str, country: Optional[str]) -> float:
    """Multiplier for (platform, country); 1.0 when there is no calibration data."""
    platform = "pc" if platform and ("pc" in platform or "steam" in platform) else "mobile"
    f = _factors()
    country = (country or "").lower()
    if (platform, country) in f["country"]:
        return f["country"][(platform, country)]
    return f["platform"].get(platform, 1.0)


def get_report() -> Dict[str, Any]:
    """All points with model vs actual error, plus the factors currently in effect."""
    points = list_points()
    f = _factors()
    rows = []
    for p in points:
        raw = _model_monthly(p)
        factor = get_factor(p["platform"], p["country"])
        calibrated = int(raw * factor)
        actual = p["actual_monthly_revenue"]
        rows.append({
            **p,
            "model_monthly_raw": raw,
            "model_monthly_calibrated": calibrated,
            "raw_error_pct": round((raw - actual) / actual * 100, 1) if actual else None,
            "calibrated_error_pct": round((calibrated - actual) / actual * 100, 1) if actual else None,
        })
    return {
        "points": rows,
        "factors": [
            {"platform": k[0], "country": k[1], "factor": round(v, 3), "points": f["counts"].get(f"{k[0]}:{k[1]}", 0)}
            for k, v in sorted(f["country"].items())
        ],
        "platform_factors": {k: round(v, 3) for k, v in f["platform"].items()},
        "bounds": [MIN_FACTOR, MAX_FACTOR],
    }
