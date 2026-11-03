"""AI Game Deconstructor & Market Analyst integrating Google Gemini and Expert Knowledge."""

import json
import logging
from typing import Dict, Any, Optional
import httpx

from app.notifications.notifier import AlertNotifier

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

class AIAnalyst:
    def __init__(self):
        self.notifier = AlertNotifier()

    def get_api_key(self) -> str:
        """Retrieves Gemini API Key from config if set."""
        cfg = self.notifier.get_config()
        return cfg.get("gemini_api_key", "").strip()

    def save_api_key(self, api_key: str) -> bool:
        """Saves Gemini API Key to config."""
        cfg = self.notifier.get_config()
        cfg["gemini_api_key"] = api_key.strip()
        self.notifier.save_config(cfg)
        return True

    def analyze_game(self, game_data: Dict[str, Any], custom_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Deconstructs a game's design, monetization, and market positioning.
        Uses Gemini API if key is present; otherwise falls back to the Expert Heuristic Engine.
        """
        api_key = custom_api_key or self.get_api_key()

        if api_key:
            try:
                gemini_result = self._call_gemini_api(game_data, api_key)
                if gemini_result:
                    return {
                        "source": "gemini-1.5-flash",
                        "status": "success",
                        "analysis": gemini_result
                    }
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to heuristic analyst: {e}")

        # Fallback to Expert Heuristic Engine
        heuristic_result = self._generate_heuristic_deconstruction(game_data)
        return {
            "source": "expert-heuristic-engine",
            "status": "success",
            "note": "Phân tích tự động bằng Hệ tri thức Game Market Radar (Nhập Gemini API Key trong Cài đặt để kích hoạt phân tích LLM sâu hơn).",
            "analysis": heuristic_result
        }

    def _call_gemini_api(self, game_data: Dict[str, Any], api_key: str) -> Optional[Dict[str, Any]]:
        """Calls Google Gemini API for custom deep game analysis."""
        title = game_data.get("title", "Game")
        developer = game_data.get("developer", "Studio")
        genre = game_data.get("genre", "Game")
        platform = game_data.get("platform", "Mobile / PC")
        rank = game_data.get("rank", 1)
        price = game_data.get("price", "Free")
        est_rev = game_data.get("estimated_revenue_monthly_formatted", "N/A")
        downloads = game_data.get("estimated_downloads_formatted", game_data.get("estimated_downloads", "N/A"))

        prompt = f"""
Bạn là một Giám Đốc Sản Phẩm Game (Game Product Director) và Chuyên Gia Phân Tích Kinh Tế Game (Game Monetization Expert) dày dạn kinh nghiệm.
Hãy bóc tách và phân tích chuyên sâu tựa game sau:
- Tên Game: {title}
- Nhà phát triển: {developer}
- Thể loại: {genre}
- Nền tảng: {platform}
- Thứ hạng hiện tại: #{rank}
- Giá bán / Mô hình: {price}
- Doanh thu tháng ước tính: {est_rev}
- Lượt tải / Người chơi: {downloads}

Hãy trả về kết quả dưới định dạng JSON với các trường sau (viết bằng Tiếng Việt súc tích, chuyên nghiệp):
{{
  "core_loop": "Mô tả vòng lặp trải nghiệm cốt lõi (Core Gameplay Loop: Hành động -> Phần thưởng -> Nâng cấp -> Thử thách mới) và cơ chế Retention giữ chân người chơi.",
  "monetization": "Bóc tách chi tiết mô hình kinh doanh & cơ chế kiếm tiền (Gacha, Battle Pass, IAP gói nạp giới hạn giờ, Rewarded Ads, Cosmetic skins, hoặc Pity system).",
  "player_persona": "Chân dung người chơi mục tiêu (Target Audience, độ tuổi, tâm lý: Thích tranh đấu Hardcore, Casual thư giãn hay Thích sưu tập).",
  "competitive_edge": "Điểm khác biệt cốt lõi hoặc cải tiến giúp tựa game này vượt trội hơn các đối thủ cùng phân khúc.",
  "actionable_takeaways": "3 bài học đắt giá nhất dành cho Game Developer / Studio Việt Nam hoặc Indie Dev có thể học hỏi và áp dụng vào game của mình."
}}
Chỉ trả về JSON thuần túy, không kèm markdown code block (không cần ```json).
"""
        url = f"{GEMINI_API_URL}?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "response_mime_type": "application/json"
            }
        }

        with httpx.Client(timeout=20) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
            else:
                logger.error(f"Gemini API returned code {resp.status_code}: {resp.text}")
                return None

    def _generate_heuristic_deconstruction(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates domain-expert teardown based on genre, platform and economics."""
        title = game_data.get("title", "Game")
        genre = (game_data.get("genre") or "").lower()
        platform = (game_data.get("platform") or "").lower()
        is_pc = "pc" in platform
        price = game_data.get("price", "Free")
        is_f2p = price.lower() == "free"

        # 1. Core loop breakdown
        if "rpg" in genre or "role playing" in genre:
            core_loop = (
                "Vòng lặp cốt lõi: Vượt ải / Hoàn thành nhiệm vụ cốt truyện ➔ Thu thập tài nguyên & phôi tướng ➔ "
                "Cường hóa chỉ số (Trang bị, Thức tỉnh, Tẩy luyện) ➔ Thử thách Boss hầm ngục và leo Top PvP xếp hạng. "
                "Cơ chế giữ chân dựa trên FOMO (sự kiện giới hạn ngày), phần thưởng tích lũy AFK và bang hội guild chiến."
            )
            monetization = (
                "Hệ thống Kiếm tiền: Mô hình Gacha kết hợp Gói nạp định kỳ. Doanh thu chính đến từ Banner tướng giới hạn (Limited Banner) "
                "với cơ chế bảo hiểm (Pity System), Thẻ tháng (Monthly Card với ROI cao), Battle Pass theo mùa và gói nạp tăng tốc tiến trình."
            )
            player_persona = "Người chơi Mid-core đến Hardcore, độ tuổi 18-35. Thích cảm giác thăng tiến sức mạnh, sưu tập nhân vật và ganh đua thứ hạng PvP."
        elif "strategy" in genre or "chiến thuật" in genre:
            core_loop = (
                "Vòng lặp cốt lõi: Khai thác tài nguyên nội thành ➔ Chiêu mộ quân đội & Nghiên cứu công nghệ ➔ "
                "Mở rộng bản đồ thế giới (Map Control) ➔ Tham gia Liên minh liên chiến giành lãnh thổ trung tâm. "
                "Tính năng mạng xã hội và tình anh em bang hội là động lực giữ chân mạnh mẽ nhất."
            )
            monetization = (
                "Hệ thống Kiếm tiền: Doanh thu dựa vào nhóm người chơi bạo chi (Whales). Bán gói nạp tăng tốc xây dựng/huấn luyện lính, "
                "bảo hiểm hòa bình (Peace Shield), tài nguyên khẩn cấp và các sự kiện đua top liên server với giải thưởng độc quyền."
            )
            player_persona = "Người chơi từ 22-45 tuổi, có thu nhập ổn định và thời gian online rải rác. Thích tư duy lãnh đạo, quản trị tài nguyên và sức mạnh chính trị liên minh."
        elif "action" in genre or "shooter" in genre or "moba" in genre or "battle royale" in genre:
            core_loop = (
                "Vòng lặp cốt lõi: Tham gia trận đấu đối kháng (10-25 phút) ➔ Thể hiện kỹ năng cá nhân & phối hợp đồng đội ➔ "
                "Nhận điểm xếp hạng Rank & Tiền tệ sự kiện ➔ Mở khóa ngoại trang biểu cảm và nâng bậc mùa giải."
            )
            monetization = (
                "Hệ thống Kiếm tiền: Công bằng tuyệt đối (Fair-play F2P), không bán chỉ số sức mạnh (Pay-to-Win). Doanh thu bùng nổ từ Battle Pass mùa, "
                "Trang phục nhân vật/vũ khí độ hiếm cao (Legendary/Mythic skins) kết hợp vòng quay may mắn (Lucky Wheel/Gacha skins)."
            )
            player_persona = "Thế hệ Gen Z & Millennials (15-28 tuổi). Đòi hỏi tính cạnh tranh cao, thích thể hiện phong cách cá nhân và chơi cùng bạn bè."
        elif "casual" in genre or "puzzle" in genre:
            core_loop = (
                "Vòng lặp cốt lõi: Giải đố màn chơi ngắn (1-3 phút) ➔ Tích lũy sao/điểm tiến trình ➔ "
                "Trang trí không gian / Nâng cấp cốt truyện phụ ➔ Nhận chuỗi thắng (Win Streak) và leo bảng xếp hạng bạn bè."
            )
            monetization = (
                "Hệ thống Kiếm tiền: Hybrid-Monetization (Kết hợp IAP và Quảng cáo). Bán thêm lượt đi (+5 Moves) khi suýt thua, "
                "Bình máu/Lượt chơi (Lives), và Quảng cáo nhận thưởng (Rewarded Video) để nhận trợ giúp."
            )
            player_persona = "Đại chúng (Casual Gamers), tỷ lệ nữ giới cao (25-50 tuổi). Chơi để giải tỏa căng thẳng trong các khoảng thời gian trống."
        else:
            core_loop = (
                f"Vòng lặp cốt lõi của {title}: Khởi động thử thách ➔ Thu thập kinh nghiệm & mở khóa vật phẩm ➔ Tùy biến lối chơi ➔ Đạt thành tựu mới. "
                "Game tạo nhịp độ cuốn hút nhờ cơ chế khen thưởng vi mô (micro-rewards) liên tục."
            )
            monetization = (
                "Hệ thống Kiếm tiền: " + ("Bán bản quyền một lần (Buy-to-Play) kèm DLC/Gói nội dung mở rộng." if not is_f2p else "Mô hình Free-to-Play hỗ trợ IAP vật phẩm tiện ích và trang phục làm đẹp.")
            )
            player_persona = "Cộng đồng đam mê trải nghiệm sáng tạo, thích khám phá cơ chế gameplay mới lạ và lối chơi giàu chiều sâu."

        competitive_edge = (
            f"Lợi thế cạnh tranh: {title} thành công nhờ tối ưu hóa trải nghiệm người dùng (UX) mượt mà, "
            f"tần suất cập nhật Live-Ops sự kiện đều đặn và cân bằng tốt giữa trải nghiệm người chơi miễn phí với người nạp tiền."
        )

        actionable_takeaways = [
            "1. Tối ưu First-Time User Experience (FTUE): Đưa người chơi vào 'vùng khoái cảm' (Flow State) ngay trong 60 giây đầu tiên.",
            "2. Thiết kế Battle Pass có giá trị cảm nhận cao: Tạo lộ trình nhận quà liên tục để biến người chơi F2P thành người nạp gói đầu tiên (First-time Conversion).",
            "3. Live-Ops linh hoạt: Duy trì chu kỳ sự kiện hàng tuần với các nhiệm vụ gắn liền cộng đồng để chống tụt giảm Retention D7 và D30."
        ]

        return {
            "core_loop": core_loop,
            "monetization": monetization,
            "player_persona": player_persona,
            "competitive_edge": competitive_edge,
            "actionable_takeaways": "\n".join(actionable_takeaways)
        }
