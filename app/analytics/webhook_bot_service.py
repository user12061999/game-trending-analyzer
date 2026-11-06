"""Discord & Telegram Webhook Automation Bot Service.

Sends instant real-time alerts for competitor rank breakouts, upcoming LiveOps auction clashes,
and daily executive morning digests directly to studio communication channels.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from datetime import datetime

class WebhookBotService:
    """Automated notification dispatcher for Discord and Telegram."""

    def __init__(self, config_path: str = "data/webhook_config.json"):
        self.config_path = config_path
        self._ensure_data_dir()
        self.config = self._load_config()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "discord_webhook_url": "",
            "discord_enabled": False,
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "telegram_enabled": False,
            "alert_on_rival_rank_jump": True,
            "alert_on_liveops_cpi_surge": True,
            "daily_morning_digest": True,
            "digest_time": "08:30"
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_config.update(data)
            except Exception as e:
                print(f"[WebhookBotService] Error reading config: {e}")
        return default_config

    def save_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        self.config.update(new_config)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return {"status": "success", "message": "Cấu hình Webhook Bot đã được lưu thành công!"}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi lưu file cấu hình: {e}"}

    def get_config(self) -> Dict[str, Any]:
        """Returns safe config without exposing full secrets."""
        cfg = dict(self.config)
        # Mask sensitive secrets partially
        if cfg.get("discord_webhook_url"):
            url = cfg["discord_webhook_url"]
            if len(url) > 20:
                cfg["discord_webhook_masked"] = url[:15] + "..." + url[-6:]
            else:
                cfg["discord_webhook_masked"] = "***"
        else:
            cfg["discord_webhook_masked"] = ""

        if cfg.get("telegram_bot_token"):
            token = cfg["telegram_bot_token"]
            cfg["telegram_token_masked"] = token[:6] + "..." + token[-4:] if len(token) > 10 else "***"
        else:
            cfg["telegram_token_masked"] = ""

        return cfg

    def send_discord_message(self, title: str, description: str, color: int = 0x6366F1, fields: Optional[List[Dict[str, Any]]] = None) -> bool:
        webhook_url = self.config.get("discord_webhook_url", "").strip()
        if not webhook_url:
            return False

        payload = {
            "username": "Game Studio Intelligence Bot",
            "avatar_url": "https://img.icons8.com/fluency/96/controller.png",
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": color,
                    "fields": fields or [],
                    "footer": {
                        "text": f"Game Trending Analyzer • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }
            ]
        }

        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in (200, 204)
        except Exception as e:
            print(f"[WebhookBotService] Discord send error: {e}")
            return False

    def send_telegram_message(self, text: str) -> bool:
        token = self.config.get("telegram_bot_token", "").strip()
        chat_id = self.config.get("telegram_chat_id", "").strip()
        if not token or not chat_id:
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"[WebhookBotService] Telegram send error: {e}")
            return False

    def send_broadcast_alert(self, title: str, description: str, fields: Optional[List[Dict[str, Any]]] = None, color: int = 0x6366F1) -> Dict[str, Any]:
        """Dispatches alert to all enabled channels."""
        results = {}
        if self.config.get("discord_enabled", False):
            results["discord"] = self.send_discord_message(title, description, color, fields)
        else:
            results["discord"] = "disabled"

        if self.config.get("telegram_enabled", False):
            # Format text for telegram
            tg_text = f"<b>{title}</b>\n\n{description}\n"
            if fields:
                for f in fields:
                    tg_text += f"\n▫️ <b>{f['name']}:</b> {f['value']}"
            tg_text += f"\n\n<i>Game Trending Analyzer • {datetime.now().strftime('%H:%M %d/%m')}</i>"
            results["telegram"] = self.send_telegram_message(tg_text)
        else:
            results["telegram"] = "disabled"

        return results

    def trigger_test_alert(self) -> Dict[str, Any]:
        """Sends immediate test alert to verified channels."""
        title = "🚀 [Test Alert] Kết Nối Webhook Thành Công!"
        desc = "Hệ thống Game Trending Analyzer đã liên kết thành công với kênh chat của studio bạn. Các thông báo biến động thị trường và LiveOps sẽ được tự động cập nhật tại đây."
        fields = [
            {"name": "Trạng Thái", "value": "🟢 Đang Hoạt Động (Active)", "inline": True},
            {"name": "Tốc Độ Cập Nhật", "value": "⚡ Thời Gian Thực (Real-time)", "inline": True},
            {"name": "Mục Tiêu Theo Dõi", "value": "Radar Bùng Nổ, CPI Surge & Báo Cáo Sáng", "inline": False}
        ]
        return self.send_broadcast_alert(title, desc, fields, color=0x10B981)

    def trigger_morning_digest(self) -> Dict[str, Any]:
        """Sends daily morning market digest."""
        title = "☀️ [Daily Digest] Bản Tin Chiến Lược Mobile Sáng Nay"
        desc = "Tổng hợp các chuyển động đáng chú ý nhất trên App Store & Google Play trong 24 giờ qua:"
        fields = [
            {"name": "🔥 Game Bùng Nổ (Breakout)", "value": "Tựa game mới <b>Pixel Knight Survival</b> tăng vọt +48 bậc Top Grossing VN.", "inline": False},
            {"name": "⚠️ Cảnh Báo LiveOps", "value": "HoYoverse chuẩn bị cập nhật bản 6 tuần vào Thứ Tư tới. Khuyến nghị giảm 30% ngân sách UA TikTok/Meta.", "inline": False},
            {"name": "💡 Gợi Ý Creative", "value": "Hook 'Level 1 Crook vs Level 100 Boss' đang đạt CVR cao nhất (+32%) trong phân khúc Action.", "inline": False}
        ]
        return self.send_broadcast_alert(title, desc, fields, color=0xF59E0B)

    def trigger_fraud_alert(self, network_name: str, fraud_rate: float, fraud_type: str, details: str) -> Dict[str, Any]:
        """Dispatches high-priority alert when live MMP stream detects abnormal fraud rates."""
        title = f"🚨 [CẢNH BÁO GIAN LẬN UA] Phát Hiện Fraud Đột Biến: {network_name}"
        desc = f"Hệ thống MMP Ingestion vừa phát hiện tỷ lệ gian lận bất thường vượt ngưỡng an toàn từ đối tác <b>{network_name}</b>."
        fields = [
            {"name": "Mạng Phân Phối (Network)", "value": network_name, "inline": True},
            {"name": "Tỷ Lệ Gian Lận", "value": f"<b>{fraud_rate:.1f}%</b> (Ngưỡng: &lt; 5%)", "inline": True},
            {"name": "Hành Vi Phát Hiện", "value": fraud_type, "inline": True},
            {"name": "Hành Động Khẩn Cấp", "value": details, "inline": False}
        ]
        return self.send_broadcast_alert(title, desc, fields, color=0xEF4444)
