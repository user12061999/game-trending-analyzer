"""Creative Ad Spy & Video Hook Deconstructor for Mobile Games.

Analyzes winning mobile UA video ad archetypes across TikTok, Facebook, Unity, AppLovin.
Provides detailed second-by-second storyboards and custom ad script generation for game studios.
"""

import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Winning Mobile Ad Creative Archetypes Database
CREATIVE_ARCHETYPES: List[Dict[str, Any]] = [
    {
        "id": "rage_bait_fail",
        "title": "Fail-Ad / Rage-Bait (Chơi Ngớ Ngẩn Gây Ức Chế)",
        "genre": "Casual / Puzzle / Strategy",
        "target_networks": ["TikTok", "Meta (Facebook/Instagram)", "Unity Ads"],
        "avg_ctr": "4.8%",
        "avg_cvr": "34.2%",
        "cpi_impact": "Giảm -40% CPI nhờ lượng click tò mò cực cao",
        "primary_hook_type": "Kích thích sự tự ái và lòng kiêu hãnh của người xem",
        "description": "Video mô phỏng một 'tay mơ' liên tục đưa ra những lựa chọn ngớ ngẩn trước bài toán đơn giản (ví dụ: kéo chốt nhầm chỗ khiến dung nham đổ vào người, hoặc chọn cửa chia đôi quân lính). Kết thúc bằng màn thua tức tưởi khiến người xem muốn nhảy vào tự tay chơi để chứng minh mình thông minh hơn.",
        "storyboard": {
            "hook_0_3s": "Hiển thị câu đố cực kỳ rõ ràng kèm dòng chữ: 'Chỉ 1% người chơi IQ trên 120 mới qua được màn này!' Ngón tay ảo bắt đầu do dự.",
            "action_3_12s": "Ngón tay chọn phương án sai hiển nhiên (ví dụ: kéo chốt nhốt quái vật nhưng lại thả quái vật vào căn phòng nhân vật chính). Nhân vật chính kêu thét hài hước.",
            "cta_12_18s": "Màn hình rung lắc hiện chữ 'DEFEAT' màu đỏ to đùng. Mũi tên chỉ vào nút tải về kèm thông điệp: 'Bạn có thông minh hơn tên ngốc này không? Tải ngay để thử sức!'"
        },
        "production_cost": "Thấp (Dựng 2D/3D đơn giản trong 1-2 ngày)",
        "recommended_for": ["Puzzle", "Tower Defense", "Hyper-casual", "Hybrid-casual"]
    },
    {
        "id": "mob_runner_multiplier",
        "title": "Mob Runner / Door Multiplier (Gom Quân Cửa Nhân Số Lượng)",
        "genre": "Action / Casual / SLG",
        "target_networks": ["TikTok", "AppLovin", "Unity Ads"],
        "avg_ctr": "5.2%",
        "avg_cvr": "38.5%",
        "cpi_impact": "Giảm -45% CPI, cực kỳ hiệu quả kéo tệp Gen Z",
        "primary_hook_type": "Thỏa mãn cảm giác đám đông và cấp số nhân (Oddly Satisfying)",
        "description": "Nhân vật xuất phát với 1 xạ thủ nhỏ bé, chạy qua các cánh cổng có phép tính (+10, x2, x5). Đội quân nhân bản ào ạt như thác lũ, quét sạch quái vật trên đường đi. Cảm giác nhìn con số nhảy vọt tạo khoái cảm thị giác cực mạnh (Dopamine rush).",
        "storyboard": {
            "hook_0_3s": "Nhân vật bắn súng 1 mình bị đám đông thây ma truy đuổi gắt gao. Phía trước xuất hiện 2 cánh cổng: 'x5 Quân' và '-50 Quân'.",
            "action_3_14s": "Nhân vật chạy vào cổng 'x5', ngay lập tức nhân bản thành 500 binh lính xả đạn như bão lửa. Đám đông càn quét xuyên qua pháo đài kẻ địch.",
            "cta_14_20s": "Trước mặt xuất hiện cánh cổng 'x100 Binh Đoàn'. Nút bấm 'CHẠY NGAY' nhấp nháy: 'Chỉ huy quân đội của bạn ngay hôm nay - Miễn phí trên iOS & Android!'"
        },
        "production_cost": "Trung bình (Yêu cầu asset nhân vật 3D chạy mượt)",
        "recommended_for": ["Action Runner", "SLG Chiến Thuật", "Sinh Tồn Zombie", "Casual"]
    },
    {
        "id": "gacha_flex_giftcode",
        "title": "Gacha Flex & Giftcode Bomb (Mở Rương Nổ Hũ & Tặng Mã Code)",
        "genre": "RPG / Anime Gacha / Thẻ Tướng",
        "target_networks": ["TikTok", "Meta (Facebook)", "YouTube Shorts"],
        "avg_ctr": "4.1%",
        "avg_cvr": "31.0%",
        "cpi_impact": "Thu hút tệp người chơi chịu chi (Whales & Dolphins) với LTV cao",
        "primary_hook_type": "Kích thích lòng tham phần thưởng tân thủ và cảm giác mở thưởng (Unboxing)",
        "description": "Video tập trung hoàn toàn vào hoạt cảnh quay tướng gacha hào nhoáng. Hiệu ứng ánh sáng vàng kim/cầu vồng bùng nổ, liên tục nổ ra các tướng cấp SSR/UR hiếm nhất game, kèm mã code tân thủ nhấp nháy trên màn hình.",
        "storyboard": {
            "hook_0_3s": "Âm thanh tiếng chuông nổ hũ vang lên. Màn hình tối sầm lại rồi bùng sáng hiệu ứng cầu vồng rực rỡ với dòng chữ: 'NỔ TƯỚNG 5 SAO HUYỀN THOẠI!'.",
            "action_3_13s": "Xuất hiện nhân vật nữ/nam thần thoại với hiệu ứng chiêu thức mãn nhãn. Kèm dòng chữ nổi bật: 'Đăng nhập hôm nay tặng ngay 100 lượt quay vé vàng và Rương Tự Chọn Tướng'.",
            "cta_13_20s": "Hiển thị khung nhập giftcode to rõ ràng: 'VIP999'. Hướng dẫn người xem: 'Tải game qua link dưới, nhập mã VIP999 để nhận ngay 10.000 Kim Cương!'"
        },
        "production_cost": "Thấp (Cắt ghép trực tiếp từ cutscene/cinematic trong game)",
        "recommended_for": ["Anime RPG", "Thẻ Tướng Tam Quốc", "Turn-based JRPG", "MMORPG"]
    },
    {
        "id": "zero_to_hero_level",
        "title": "Level 1 Crook vs Level 100 Boss (Tiến Hóa Cấp Độ Thần Tốc)",
        "genre": "RPG / Survival / Action / MMORPG",
        "target_networks": ["Meta (Facebook)", "TikTok", "AppLovin"],
        "avg_ctr": "4.5%",
        "avg_cvr": "32.8%",
        "cpi_impact": "Giảm -35% CPI, kích thích khao khát thăng tiến (Progression Fantasy)",
        "primary_hook_type": "Tâm lý muốn trở nên hùng mạnh và đánh bại kẻ bắt nạt",
        "description": "Chia đôi màn hình hoặc dòng thời gian: Bên trái/Ban đầu là Level 1 mặc áo rách bị quái vật đánh bay; Bên phải/Sau 10 phút là Level 99 mặc giáp vàng cưỡi rồng lửa, tung một đòn quét sạch bản đồ.",
        "storyboard": {
            "hook_0_3s": "Nhân vật Level 1 cầm que củi bị boss chê cười và hất văng xuống vực sâu. Dòng chữ: 'Bạn nghĩ tôi sẽ bỏ cuộc?'",
            "action_3_12s": "Nhân vật nhặt được thanh thần kiếm phát sáng, cấp độ nhảy số liên tục: Lv1 -> Lv20 -> Lv60 -> Lv99. Giáp biến hình lộng lẫy, cánh lửa mọc ra sau lưng.",
            "cta_12_18s": "Quay trở lại gặp con boss đầu game. Nhân vật vung kiếm 1 hit hạ gục boss rơi đầy vàng bạc. Dòng chữ: 'Bắt đầu hành trình báo thù của bạn ngay!'"
        },
        "production_cost": "Trung bình (Ghép animation biến hình nhân vật)",
        "recommended_for": ["MMORPG", "Action RPG", "Idle RPG", "Survival Roguelike"]
    },
    {
        "id": "ugc_dramatic_challenge",
        "title": "UGC Skit & Real-Life Drama (Tình Huống Hài Kịch TikTok Đời Thực)",
        "genre": "Casual / Party / PvP / Strategy",
        "target_networks": ["TikTok", "YouTube Shorts", "Instagram Reels"],
        "avg_ctr": "5.6%",
        "avg_cvr": "41.0%",
        "cpi_impact": "Tỷ lệ giữ chân người xem (Watch Time) cao nhất nhờ cảm giác đời thực",
        "primary_hook_type": "Tò mò về câu chuyện đời thực của người khác (Storytelling)",
        "description": "Diễn viên quay camera trước theo phong cách TikTok chân thực. Ví dụ: Bạn gái giận dỗi vì người yêu chơi game quá giỏi, hoặc sếp cá cược với nhân viên bằng một trận solo PvP nếu thua sẽ được tăng lương.",
        "storyboard": {
            "hook_0_3s": "Góc quay điện thoại rung lắc, cô gái tức giận nói trước ống kính: 'Người yêu em bảo nếu em thắng được ải này trong game của anh ấy thì tuần này đi du lịch Paris!'",
            "action_3_14s": "Camera quay cận cảnh màn hình điện thoại đang chơi game. Cô gái bấm nút và vô tình kích hoạt combo huyền thoại, màn hình hiện chiến thắng rực rỡ. Chàng trai ôm đầu thảng thốt.",
            "cta_14_20s": "Cô gái cười rạng rỡ chỉ tay xuống phần mô tả: 'Link tải game em để ở dưới nhé, ai muốn đi Paris thì tải về solo với người yêu ngay!'"
        },
        "production_cost": "Thấp đến Trung bình (Chỉ cần 1-2 diễn viên và 1 chiếc smartphone)",
        "recommended_for": ["Party Game", "PvP Đối Kháng", "Casual", "Board / Card Game"]
    }
]

class CreativeSpy:
    """Provides mobile ad intelligence, archetype benchmarking, and script generator."""

    def __init__(self):
        self.archetypes = CREATIVE_ARCHETYPES

    def get_all_archetypes(self, genre: Optional[str] = None, network: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filters creative archetypes by target genre or ad network."""
        results = self.archetypes
        if genre and genre.lower() != "all":
            results = [a for a in results if genre.lower() in a["genre"].lower()]
        if network and network.lower() != "all":
            results = [a for a in results if any(network.lower() in net.lower() for net in a["target_networks"])]
        return results

    def get_archetype_by_id(self, archetype_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single archetype details."""
        for a in self.archetypes:
            if a["id"] == archetype_id:
                return a
        return None

    def generate_custom_ad_script(self, game_title: str, genre: str = "RPG", target_network: str = "TikTok") -> Dict[str, Any]:
        """Generates a tailored 20-second high-conversion video ad script for a specific mobile game."""
        clean_title = game_title or "Tựa Game Mobile Của Bạn"
        clean_genre = genre or "RPG"

        if "puzzle" in clean_genre.lower() or "casual" in clean_genre.lower():
            chosen_archetype = "Rage-Bait Fail Ad (Chơi ngớ ngẩn gây ức chế)"
            hook = f"Hiển thị câu đố sinh tồn hóc búa với dòng chữ giật gân: 'Chỉ 2% người chơi qua được màn 5 của {clean_title}!'."
            action = "Bàn tay ảo chọn sai phương án, nhân vật bị rơi xuống bẫy nước hài hước. Nhạc nền giật gân dừng đột ngột."
            cta = f"Màn hình hiện 'BẠN CÓ DÁM THỬ?'. Tải {clean_title} ngay trên App Store & Google Play!"
            hook_text = "99% Người Chơi Đều Bị Đánh Lừa Ở Màn Này!"
        elif "shoot" in clean_genre.lower() or "action" in clean_genre.lower():
            chosen_archetype = "Mob Multiplier / Survival Bullet Storm"
            hook = f"Nhân vật chính trong {clean_title} bị vây ráp bởi 10.000 quái vật zombie bủa vây."
            action = "Lao qua cổng 'x10 Hỏa Lực', súng nâng cấp thành bão plasma quét sạch toàn bộ bản đồ trong 5 giây mãn nhãn."
            cta = f"Tải {clean_title} ngay để nhận Gói Tiếp Tế Bão Lửa miễn phí!"
            hook_text = "Sống Sót Qua 10.000 Con Quái Vật Trong 20 Giây!"
        else: # Default RPG / Strategy
            chosen_archetype = "Gacha Flex & Giftcode Explosion"
            hook = f"Hiệu ứng ánh sáng hoàng kim rực rỡ bùng nổ trên nền nhạc bass drop: '{clean_title} KHAI MỞ SERVER MỚI!'."
            action = "Chuỗi quay 10 vé nổ liền 3 Tướng Thần Thoại SSR 5 sao với đồ họa chiêu thức 3D đỉnh cao. Mã code 'TANTHU888' hiện sáng rực rỡ."
            cta = f"Nhập code 'TANTHU888' nhận ngay 100 Vé Quay & 10.000 Kim Cương khi tải {clean_title} hôm nay!"
            hook_text = "Tặng Miễn Phí 100 Lượt Quay Tướng SSR Cho Tân Thủ!"

        return {
            "game_title": clean_title,
            "genre": clean_genre,
            "target_network": target_network,
            "recommended_archetype": chosen_archetype,
            "duration": "20 giây (Chuẩn TikTok & Reels)",
            "on_screen_hook_text": hook_text,
            "script_steps": [
                {
                    "timeline": "00:00 - 00:03 (The 3-Second Hook)",
                    "visual": hook,
                    "audio": "Âm thanh tiếng chuông nổ hũ / báo động kịch tính kích thích sự chú ý tức thì.",
                    "overlay_text": hook_text
                },
                {
                    "timeline": "00:03 - 00:14 (Core Action & Escalation)",
                    "visual": action,
                    "audio": "Nhạc nền tiết tấu nhanh, âm thanh chiêu thức dồn dập, tạo cảm giác thỏa mãn thị giác.",
                    "overlay_text": "Combo Kỹ Năng Đỉnh Cao • Tốc Độ Bắn Cực Nhanh"
                },
                {
                    "timeline": "00:14 - 00:20 (Call To Action - CTA)",
                    "visual": cta,
                    "audio": "Giọng lồng tiếng (Voiceover) hào hứng: 'Tải ngay hôm nay để nhận trọn bộ quà tân thủ!', tiếng click tải về vang lên.",
                    "overlay_text": f"👉 Bấm Link Dưới Để Tải {clean_title} Miễn Phí!"
                }
            ],
            "estimated_kpis": {
                "expected_ctr": "4.5% - 5.5%",
                "expected_cvr": "32% - 38%",
                "cpi_saving": "Tiết kiệm ~35% ngân sách marketing so với video thông thường"
            }
        }
