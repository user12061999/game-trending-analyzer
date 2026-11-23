"""Decides which alerts to send after a crawl, and makes sure each one is sent only once.

Runs from both the web server and the scheduled Windows task (scripts/crawl_once.py),
so every alert is deduplicated through the alert_log table:

- daily digest        : once per day (first successful crawl of the day, or the 08:00 job)
- weekly genre digest : once per ISO week, on the first crawl on/after the configured weekday
- breakout (1-day)    : per game/chart, with a cooldown of N days
- sustained breakout  : per game/chart, at most once per window
- crawl health        : once per day per distinct set of failing/stale sources
"""

import hashlib
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from app.analytics.market_signals import MarketSignals
from app.database.db import get_db_connection
from app.notifications.notifier import DASHBOARD_URL, _e

logger = logging.getLogger(__name__)

MAX_ITEMS_PER_MESSAGE = 5


class AlertEngine:
    def __init__(self, notifier, analyzer=None):
        self.notifier = notifier
        self.analyzer = analyzer

    # ------------------------------------------------------------------ alert log
    @staticmethod
    def was_sent(key: str, within_days: Optional[float] = None) -> bool:
        conn = get_db_connection()
        try:
            if within_days is None:
                row = conn.execute("SELECT 1 FROM alert_log WHERE alert_key = ? LIMIT 1", (key,)).fetchone()
            else:
                since = (datetime.now() - timedelta(days=within_days)).strftime("%Y-%m-%d %H:%M:%S")
                row = conn.execute(
                    "SELECT 1 FROM alert_log WHERE alert_key = ? AND sent_at >= ? LIMIT 1", (key, since)
                ).fetchone()
            return row is not None
        finally:
            conn.close()

    @staticmethod
    def mark_sent(key: str, alert_type: str, summary: str = "") -> None:
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO alert_log (alert_key, alert_type, sent_at, summary) VALUES (?, ?, ?, ?)",
                (key, alert_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), summary[:500]),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def recent_alerts(limit: int = 30) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            rows = conn.execute("SELECT * FROM alert_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def _sent_ok(result: Dict[str, bool]) -> bool:
        return bool(result.get("discord") or result.get("telegram"))

    # ------------------------------------------------------------------ entry points
    def run_after_crawl(self, crawl_ok: bool = True, today: Optional[date] = None) -> Dict[str, Any]:
        """Called after every crawl attempt (successful or not)."""
        config = self.notifier.get_config()
        summary: Dict[str, Any] = {}
        if not self.notifier.has_channel(config):
            return {"skipped": "no Discord/Telegram channel configured"}

        steps = [("health", self.check_health)]
        if crawl_ok:
            steps += [
                ("daily_digest", self.send_daily_digest),
                ("breakouts", self.send_breakout_alerts),
                ("sustained", self.send_sustained_alerts),
                ("weekly_digest", self.send_weekly_digest),
            ]
        for name, fn in steps:
            try:
                summary[name] = fn(config, today=today)
            except Exception as e:  # one failing alert type must not block the others
                logger.warning("Alert step %s failed: %s", name, e)
                summary[name] = {"error": str(e)}
        return summary

    # ------------------------------------------------------------------ health
    def check_health(self, config: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
        if not config.get("enable_health_alerts", True):
            return {"skipped": "disabled"}
        health = MarketSignals.get_data_health()
        bad = [s for s in health["sources"] if s["status"] in ("failing", "stale")]
        if not bad:
            return {"sent": False, "reason": "all sources ok"}

        today = today or date.today()
        ids = sorted(f"{s['platform']}:{s['country']}:{s['ranking_type']}:{s['status']}" for s in bad)
        # stable across processes (built-in hash() of str is randomized per process)
        digest = hashlib.sha1("|".join(ids).encode("utf-8")).hexdigest()[:10]
        key = f"health:{today.isoformat()}:{digest}"
        if self.was_sent(key):
            return {"sent": False, "reason": "already alerted today"}

        lines_d, lines_t = [], []
        for s in bad[:10]:
            label = "LỖI" if s["status"] == "failing" else "CŨ"
            when = f"{s['hours_since_success']}h trước" if s["hours_since_success"] is not None else "chưa từng thành công"
            err = f" — {s['last_error']}" if s.get("last_error") else ""
            lines_d.append(f"• **{label}** `{s['platform']} / {s['country']} / {s['ranking_type']}` (lần OK cuối: {when}){err}")
            lines_t.append(f"• <b>{label}</b> <code>{_e(s['platform'])} / {_e(s['country'])} / {_e(s['ranking_type'])}</code> "
                           f"(lần OK cuối: {_e(when)}){_e(err)}")
        more = f"\n… và {len(bad) - 10} nguồn khác" if len(bad) > 10 else ""
        title = f"⚠️ CRAWL CÓ VẤN ĐỀ: {len(bad)} nguồn dữ liệu lỗi hoặc cũ"
        res = self.notifier.broadcast(
            title=title,
            discord_description="\n".join(lines_d) + more + f"\n\nXem tab **Tín Hiệu Thị Trường → Sức Khỏe Dữ Liệu**.",
            telegram_html=f"<b>{_e(title)}</b>\n\n" + "\n".join(lines_t) + _e(more)
                          + f"\n\n👉 <a href='{DASHBOARD_URL}'>Mở Dashboard</a>",
            color=0xF59E0B,
        )
        if self._sent_ok(res):
            self.mark_sent(key, "health", title)
        return {"sent": self._sent_ok(res), "sources": len(bad)}

    # ------------------------------------------------------------------ daily digest
    def send_daily_digest(self, config: Dict[str, Any], today: Optional[date] = None,
                          force: bool = False) -> Dict[str, Any]:
        if not config.get("enable_daily_digest", True) and not force:
            return {"skipped": "disabled"}
        today = today or date.today()
        key = f"digest:{today.isoformat()}"
        if not force and self.was_sent(key):
            return {"sent": False, "reason": "already sent today"}
        res = self.notifier.dispatch_daily_digest()
        ok = self._sent_ok(res)
        if ok:
            self.mark_sent(key, "daily_digest")
        return {"sent": ok}

    # ------------------------------------------------------------------ 1-day breakouts
    def send_breakout_alerts(self, config: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
        if not config.get("enable_breakout_alerts", True):
            return {"skipped": "disabled"}
        threshold = int(config.get("breakout_threshold", 15))
        cooldown = float(config.get("breakout_cooldown_days", 3))
        analyzer = self.analyzer or self.notifier.analyzer
        target_date = analyzer.get_latest_snapshot_date()
        conn = get_db_connection()
        try:
            rows = [dict(r) for r in conn.execute("""
                SELECT game_id, title, developer, platform, country, ranking_type, rank,
                       rank_change_day, icon_url, genre, store_url
                FROM snapshots
                WHERE snapshot_date = ? AND rank_change_day >= ?
                ORDER BY rank_change_day DESC
            """, (target_date, threshold)).fetchall()]
        finally:
            conn.close()

        sent = 0
        for g in rows:
            key = f"breakout:{g['platform']}:{g['country']}:{g['ranking_type']}:{g['game_id']}"
            if self.was_sent(key, within_days=cooldown):
                continue
            if sent >= MAX_ITEMS_PER_MESSAGE:
                break
            if self.notifier.dispatch_breakout_alert(g):
                self.mark_sent(key, "breakout", f"{g['title']} +{g['rank_change_day']}")
                sent += 1
        return {"sent": sent, "candidates": len(rows)}

    # ------------------------------------------------------------------ sustained breakouts
    def send_sustained_alerts(self, config: Dict[str, Any], today: Optional[date] = None) -> Dict[str, Any]:
        if not config.get("enable_sustained_alerts", True):
            return {"skipped": "disabled"}
        window = int(config.get("sustained_window_days", 7))
        min_gain = int(config.get("sustained_min_gain", 10))
        found = MarketSignals.get_sustained_breakouts(window_days=window, min_net_gain=min_gain, limit=50, today=today)
        found = [g for g in found if not g["is_single_spike"]]
        fresh = []
        for g in found:
            key = f"sustained:{g['platform']}:{g['country']}:{g['ranking_type']}:{g['game_id']}"
            if not self.was_sent(key, within_days=window):
                fresh.append((key, g))
        if not fresh:
            return {"sent": 0, "candidates": len(found)}

        fresh = fresh[:MAX_ITEMS_PER_MESSAGE]
        title = f"📈 BỨT PHÁ BỀN VỮNG: {len(fresh)} game tăng hạng đều trong {window} ngày"
        lines_d, lines_t = [], []
        for _, g in fresh:
            path = " → ".join(f"#{p['rank']}" for p in g["rank_series"][-6:])
            lines_d.append(f"• **{g['title']}** (+{g['net_gain']} bậc, ổn định {g['consistency_pct']}%) — "
                           f"`{g['platform']} / {g['country']} / {g['ranking_type']}`\n  {path}")
            lines_t.append(f"• <b>{_e(g['title'])}</b> (+{g['net_gain']} bậc, ổn định {g['consistency_pct']}%)\n"
                           f"  <code>{_e(g['platform'])} / {_e(g['country'])} / {_e(g['ranking_type'])}</code>  {_e(path)}")
        res = self.notifier.broadcast(
            title=title,
            discord_description="\n".join(lines_d),
            telegram_html=f"<b>{_e(title)}</b>\n\n" + "\n".join(lines_t) + f"\n\n👉 <a href='{DASHBOARD_URL}'>Mở Dashboard</a>",
            color=0x10B981,
            thumbnail_url=fresh[0][1].get("icon_url") or None,
        )
        if self._sent_ok(res):
            for key, g in fresh:
                self.mark_sent(key, "sustained", f"{g['title']} +{g['net_gain']}")
        return {"sent": len(fresh) if self._sent_ok(res) else 0, "candidates": len(found)}

    # ------------------------------------------------------------------ weekly genre digest
    def send_weekly_digest(self, config: Dict[str, Any], today: Optional[date] = None,
                           force: bool = False) -> Dict[str, Any]:
        if not config.get("enable_weekly_digest", True) and not force:
            return {"skipped": "disabled"}
        today = today or date.today()
        # Send on the first crawl on/after the configured weekday, so a week isn't lost
        # just because the PC was off on that exact day. The ISO-week key keeps it to once a week.
        if not force and today.weekday() < int(config.get("weekly_digest_weekday", 0)):
            return {"skipped": "before the configured weekday"}
        iso = today.isocalendar()
        key = f"weekly:{iso[0]}-W{iso[1]:02d}"
        if not force and self.was_sent(key):
            return {"sent": False, "reason": "already sent this week"}

        t = MarketSignals.get_genre_trends(today=today)
        if not t["has_comparison"]:
            return {"sent": False, "reason": "not enough data for two weeks"}

        def fmt(items, sign_ok):
            d, tg = [], []
            for g in items:
                titles = ", ".join(g["top_titles"][:2])
                d.append(f"• **{g['genre']}** {g['delta_pp']:+.1f} điểm % (nay {g['share_pct']:.1f}%)" + (f" — {titles}" if titles else ""))
                tg.append(f"• <b>{_e(g['genre'])}</b> {g['delta_pp']:+.1f} điểm % (nay {g['share_pct']:.1f}%)" + (f" — {_e(titles)}" if titles else ""))
            return d or ["• —"], tg or ["• —"]

        up_d, up_t = fmt(t["rising"], True)
        down_d, down_t = fmt(t["falling"], False)
        title = f"🗓️ XU HƯỚNG THỂ LOẠI TUẦN {iso[1]} ({t['this_week']['start']} → {t['this_week']['end']})"
        res = self.notifier.broadcast(
            title=title,
            discord_description="So với tuần trước, tỷ trọng có trọng số theo thứ hạng Top 50.",
            fields=[
                {"name": "▲ Đang lên", "value": "\n".join(up_d)[:1000], "inline": False},
                {"name": "▼ Đang xuống", "value": "\n".join(down_d)[:1000], "inline": False},
            ],
            telegram_html=f"<b>{_e(title)}</b>\n<i>So với tuần trước, tỷ trọng theo thứ hạng Top 50</i>\n\n"
                          f"<b>▲ Đang lên</b>\n" + "\n".join(up_t) + "\n\n<b>▼ Đang xuống</b>\n" + "\n".join(down_t)
                          + f"\n\n👉 <a href='{DASHBOARD_URL}'>Mở Dashboard</a>",
            color=0x6366F1,
        )
        ok = self._sent_ok(res)
        if ok:
            self.mark_sent(key, "weekly_digest", title)
        return {"sent": ok}
