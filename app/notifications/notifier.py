"""Notification system for Discord Webhook and Telegram Bot alerts."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, date
import httpx

from app.config import DATA_DIR

logger = logging.getLogger(__name__)

CONFIG_PATH = DATA_DIR / "alerts_config.json"

DEFAULT_CONFIG = {
    "discord_webhook_url": "",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "enable_daily_digest": True,
    "enable_breakout_alerts": True,
    "digest_time": "08:00",
    "breakout_threshold": 15
}

class AlertNotifier:
    def __init__(self):
        self._analyzer = None

    @property
    def analyzer(self):
        if self._analyzer is None:
            from app.analytics.trend_analyzer import TrendAnalyzer
            self._analyzer = TrendAnalyzer()
        return self._analyzer

    def get_config(self) -> Dict[str, Any]:
        """Loads alerts configuration or returns defaults."""
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {**DEFAULT_CONFIG, **data}
            except Exception as e:
                logger.error(f"Error reading alerts config: {e}")
        return DEFAULT_CONFIG.copy()

    def save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Persists alerts configuration."""
        merged = {**DEFAULT_CONFIG, **config}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        return merged

    def send_discord_message(self, webhook_url: str, title: str, description: str, fields: list = None, color: int = 0x6366F1, thumbnail_url: str = None) -> bool:
        """Dispatches a rich embed to Discord Webhook."""
        if not webhook_url:
            return False

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "🎮 Game Market Radar Intelligence"}
        }

        if fields:
            embed["fields"] = fields
        if thumbnail_url:
            embed["thumbnail"] = {"url": thumbnail_url}

        payload = {
            "username": "Game Market Radar",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/686/686589.png",
            "embeds": [embed]
        }

        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(webhook_url, json=payload)
                return resp.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error sending Discord webhook: {e}")
            return False

    def send_telegram_message(self, bot_token: str, chat_id: str, text: str) -> bool:
        """Sends a markdown-formatted message via Telegram Bot API."""
        if not bot_token or not chat_id:
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(url, json=payload)
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def send_test_alert(self) -> Dict[str, Any]:
        """Sends a verification test alert to all configured channels."""
        config = self.get_config()
        results = {}

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Discord Test
        if config.get("discord_webhook_url"):
            success = self.send_discord_message(
                webhook_url=config["discord_webhook_url"],
                title="✅ KẾT NỐI THÀNH CÔNG: Game Market Radar",
                description=f"Hệ thống cảnh báo thị trường game đã được kích hoạt thành công lúc `{now_str}`.\nBạn sẽ nhận được các thông báo đột biến thị trường và tổng kết hàng ngày tại kênh này.",
                color=0x10B981,
                fields=[
                    {"name": "Trạng thái", "value": "🟢 Hoạt động tốt", "inline": True},
                    {"name": "Tần suất", "value": "Mỗi 8:00 AM & Cảnh báo tức thì", "inline": True}
                ]
            )
            results["discord"] = "Thành công" if success else "Thất bại (Vui lòng kiểm tra lại Webhook URL)"
        else:
            results["discord"] = "Chưa cấu hình Webhook URL"

        # 2. Telegram Test
        if config.get("telegram_bot_token") and config.get("telegram_chat_id"):
            text = (
                f"<b>🎮 GAME MARKET RADAR - KẾT NỐI THÀNH CÔNG</b>\n\n"
                f"Hệ thống cảnh báo thị trường game đã kết nối thành công lúc <code>{now_str}</code>!\n\n"
                f"• <b>Trạng thái:</b> 🟢 Hoạt động bình thường\n"
                f"• <b>Báo cáo:</b> Tự động cập nhật mỗi ngày"
            )
            success = self.send_telegram_message(
                bot_token=config["telegram_bot_token"],
                chat_id=config["telegram_chat_id"],
                text=text
            )
            results["telegram"] = "Thành công" if success else "Thất bại (Vui lòng kiểm tra lại Bot Token hoặc Chat ID)"
        else:
            results["telegram"] = "Chưa cấu hình Bot Token / Chat ID"

        return results

    def dispatch_daily_digest(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Gathers market highlights and dispatches the morning executive summary."""
        config = self.get_config()
        if not config.get("enable_daily_digest"):
            return {"status": "skipped", "message": "Daily digest disabled in settings"}

        if not target_date:
            target_date = self.analyzer.get_latest_snapshot_date()

        overview = self.analyzer.get_market_overview(target_date)

        # Discord formatting
        discord_fields = []
        if overview.get("top_steam_ccu"):
            top_pc = overview["top_steam_ccu"][0]
            discord_fields.append({
                "name": "🖥️ Đỉnh Bảng PC (Steam CCU)",
                "value": f"**{top_pc.get('title')}**\n`{top_pc.get('player_count', 0):,} CCU` | Thể loại: {top_pc.get('genre', 'PC')}",
                "inline": False
            })

        if overview.get("rising_games"):
            top_riser = overview["rising_games"][0]
            discord_fields.append({
                "name": "🔥 Tăng Trưởng Nóng Nhất (Breakout)",
                "value": f"**{top_riser.get('title')}** (+{top_riser.get('rank_change_day')} bậc)\nRank hiện tại: `#{top_riser.get('rank')}` trên {top_riser.get('platform')}",
                "inline": False
            })

        if overview.get("top_mobile_grossing"):
            top_m = overview["top_mobile_grossing"][0]
            discord_fields.append({
                "name": "📱 Đỉnh Bảng Mobile Grossing",
                "value": f"**{top_m.get('title')}** (Rank #1 {top_m.get('country', '').upper()})\nStudio: {top_m.get('developer', 'N/A')}",
                "inline": False
            })

        discord_sent = False
        if config.get("discord_webhook_url"):
            discord_sent = self.send_discord_message(
                webhook_url=config["discord_webhook_url"],
                title=f"📊 BẢN TIN THỊ TRƯỜNG GAME NGÀY {target_date}",
                description=f"Tổng số game theo dõi hôm nay: **{overview.get('total_tracked', 0):,}** tựa game.",
                fields=discord_fields,
                color=0x6366F1
            )

        # Telegram formatting
        telegram_sent = False
        if config.get("telegram_bot_token") and config.get("telegram_chat_id"):
            tg_text = [
                f"<b>📊 BẢN TIN THỊ TRƯỜNG GAME - {target_date}</b>",
                f"<i>Tổng số game theo dõi: {overview.get('total_tracked', 0):,} tựa game</i>\n"
            ]
            if overview.get("top_steam_ccu"):
                top_pc = overview["top_steam_ccu"][0]
                tg_text.append(f"🖥️ <b>PC Đỉnh CCU:</b> {top_pc.get('title')} (<code>{top_pc.get('player_count', 0):,} CCU</code>)")
            if overview.get("rising_games"):
                top_riser = overview["rising_games"][0]
                tg_text.append(f"🔥 <b>Bứt Phá:</b> {top_riser.get('title')} (<b>+{top_riser.get('rank_change_day')}</b> bậc)")
            if overview.get("top_mobile_grossing"):
                top_m = overview["top_mobile_grossing"][0]
                tg_text.append(f"📱 <b>Mobile Top Doanh Thu:</b> {top_m.get('title')}")

            tg_text.append("\n👉 <a href='http://127.0.0.1:8000'>Xem chi tiết trên Web Dashboard</a>")
            telegram_sent = self.send_telegram_message(
                bot_token=config["telegram_bot_token"],
                chat_id=config["telegram_chat_id"],
                text="\n".join(tg_text)
            )

        return {
            "status": "completed",
            "discord": discord_sent,
            "telegram": telegram_sent
        }

    def dispatch_breakout_alert(self, game: Dict[str, Any]) -> bool:
        """Sends an immediate alert when a game makes a sudden massive rank climb."""
        config = self.get_config()
        if not config.get("enable_breakout_alerts"):
            return False

        threshold = config.get("breakout_threshold", 15)
        delta = game.get("rank_change_day", 0)
        if delta < threshold:
            return False

        title = f"🚀 CẢNH BÁO BREAKOUT: {game.get('title')} (+{delta} bậc!)"
        desc = (
            f"Tựa game **{game.get('title')}** vừa có bước nhảy vọt thứ hạng dữ dội trên **{game.get('platform')}**!\n"
            f"• Rank mới: **#{game.get('rank')}** (Tăng +{delta} bậc so với hôm qua)\n"
            f"• Thể loại: **{game.get('genre', 'N/A')}**\n"
            f"• Studio: **{game.get('developer', 'N/A')}**"
        )

        discord_ok = False
        if config.get("discord_webhook_url"):
            discord_ok = self.send_discord_message(
                webhook_url=config["discord_webhook_url"],
                title=title,
                description=desc,
                color=0xEC4899,
                thumbnail_url=game.get("icon_url")
            )

        telegram_ok = False
        if config.get("telegram_bot_token") and config.get("telegram_chat_id"):
            tg_text = (
                f"🚀 <b>CẢNH BÁO HIỆN TƯỢNG BÙNG NỔ</b>\n\n"
                f"Tựa game <b>{game.get('title')}</b> vừa tăng vọt <b>+{delta}</b> bậc trên bảng xếp hạng!\n"
                f"• Rank hiện tại: <b>#{game.get('rank')}</b>\n"
                f"• Nền tảng: <code>{game.get('platform')}</code>\n"
                f"• Thể loại: {game.get('genre', 'N/A')}\n\n"
                f"👉 <a href='{game.get('store_url', 'http://127.0.0.1:8000')}'>Mở trang Game</a>"
            )
            telegram_ok = self.send_telegram_message(
                bot_token=config["telegram_bot_token"],
                chat_id=config["telegram_chat_id"],
                text=tg_text
            )

        return discord_ok or telegram_ok

    def dispatch_radar_threat_alert(self, game: Dict[str, Any]) -> bool:
        """Sends an immediate alert when a high-threat mobile game is entering pre-registration / launch window."""
        config = self.get_config()
        threat = game.get("threat_level", "MEDIUM")
        if threat not in ["CRITICAL", "HIGH"]:
            return False

        color = 0xEF4444 if threat == "CRITICAL" else 0xF59E0B
        threat_emoji = "🔴 CỰC KỲ NGUY HIỂM" if threat == "CRITICAL" else "🟠 NGUY HIỂM CAO"

        title = f"🎯 RADAR MOBILE: {game.get('title')} [{threat_emoji}]"
        desc = (
            f"**Cảnh báo đối thủ Mobile sắp ra mắt:**\n"
            f"• Tựa game: **{game.get('title')}**\n"
            f"• NPH / Studio: **{game.get('publisher', game.get('developer', 'N/A'))}**\n"
            f"• Thể loại: **{game.get('genre', 'N/A')}**\n"
            f"• Dự kiến phát hành: **{game.get('expected_release_date')}** (Còn {game.get('countdown_days')} ngày)\n"
            f"• Đăng ký trước: **{game.get('pre_reg_count')}**\n\n"
            f"⚠️ **Khuyến nghị cho Studio:** {game.get('tactical_advice')}"
        )

        discord_ok = False
        if config.get("discord_webhook_url"):
            discord_ok = self.send_discord_message(
                webhook_url=config["discord_webhook_url"],
                title=title,
                description=desc,
                color=color,
                thumbnail_url=game.get("icon_url")
            )

        telegram_ok = False
        if config.get("telegram_bot_token") and config.get("telegram_chat_id"):
            tg_text = (
                f"🎯 <b>RADAR MOBILE: CẢNH BÁO BOM TẤN SẮP RA MẮT</b>\n\n"
                f"Tựa game: <b>{game.get('title')}</b> [{threat_emoji}]\n"
                f"• NPH / Studio: <b>{game.get('publisher', game.get('developer', 'N/A'))}</b>\n"
                f"• Thể loại: <code>{game.get('genre', 'N/A')}</code>\n"
                f"• Ngày ra mắt: <b>{game.get('expected_release_date')}</b> (Còn {game.get('countdown_days')} ngày)\n"
                f"• Lượng Đăng Ký Trước: <b>{game.get('pre_reg_count')}</b>\n\n"
                f"💡 <i>Khuyến nghị: {game.get('tactical_advice')}</i>\n\n"
                f"👉 <a href='http://127.0.0.1:8000'>Xem chi tiết trên Radar Dashboard</a>"
            )
            telegram_ok = self.send_telegram_message(
                bot_token=config["telegram_bot_token"],
                chat_id=config["telegram_chat_id"],
                text=tg_text
            )

        return discord_ok or telegram_ok
