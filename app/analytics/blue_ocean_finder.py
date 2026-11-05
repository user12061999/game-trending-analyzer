"""Blue Ocean Niche Finder & Market Saturation Radar for Mobile Games.

Identifies untapped market opportunities (Blue Oceans), warns against hyper-competitive Red Oceans,
and detects Aging Monopolies ripe for disruption by innovative mobile game studios.
"""

import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Market Sub-genres & Saturation Opportunity Matrix
MARKET_NICHES_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "cozy_farming_roguelike",
        "name": "Cozy Farming Sim x Roguelike (Nông Trại Thư Giãn kết hợp Hầm Ngục)",
        "classification": "BLUE_OCEAN",
        "classification_label": "🟦 Đại Dương Xanh (Cơ Hội Vàng)",
        "competition_index": 28,     # 1-100 (Low competition)
        "revenue_potential": 84,     # 1-100 (High revenue potential)
        "cpi_estimate": "$0.65 - $1.40",
        "development_effort": "Trung bình (Đội ngũ 6 - 12 người trong 6-9 tháng)",
        "target_audience": "Nữ giới & thế hệ Gen Z yêu thích thư giãn, kết hợp tệp game thủ cày cuốc nhẹ nhàng (Stardew Valley, Moonlighter style).",
        "market_gap_analysis": "Người chơi mobile đang quá mệt mỏi với các game cày cuốc PvP đao kiếm căng thẳng. Nhu cầu tìm kiếm game 'chữa lành' (Cozy games) tăng vọt +240% trên TikTok, nhưng 90% game hiện tại chỉ là xếp hình casual hoặc nông trại 2D lỗi thời. Kết hợp trồng trọt ban ngày và phiêu lưu thám hiểm ban đêm là công thức triệu đô chưa có đối thủ thống trị trên mobile.",
        "recommended_studio_pitch": "Tựa game nông trại 3D phong cách Isometric: Ban ngày trồng rau nuôi thú kỳ ảo, ban đêm vào hầm ngục thu thập hạt giống quý. Không có quảng cáo chèn ép, bán skin thời trang và gói mở rộng nông trang."
    },
    {
        "id": "southeast_asia_myth_rpg",
        "name": "Southeast Asian Myth RPG (Nhập Vai Thần Thoại Bản Địa Đông Nam Á)",
        "classification": "GOLDEN_NICHE",
        "classification_label": "🟩 Thị Trường Ngách Vàng",
        "competition_index": 34,
        "revenue_potential": 78,
        "cpi_estimate": "$0.55 - $1.10",
        "development_effort": "Trung bình (Đội ngũ 8 - 15 người)",
        "target_audience": "Game thủ Việt Nam, Indonesia, Thái Lan, Philippines khao khát nội dung văn hóa dân gian gần gũi thay vì Tam Quốc/Kiếm Hiệp nhàm chán.",
        "market_gap_analysis": "Thị trường ngập tràn đề tài Tam Quốc và Tiên Hiệp Trung Quốc suốt 15 năm qua. Tệp game thủ trẻ khao khát được thấy các truyền thuyết dân gian (Sơn Tinh Thủy Tinh, Thần thoại Garuda, Nữ thần Lúa) được tái hiện bằng đồ họa 3D hiện đại.",
        "recommended_studio_pitch": "Game nhập vai theo lượt (Turn-based RPG) mang phong cách Dark Fantasy Thần Thoại Đông Nam Á: Tướng truyền thuyết, bùa chú cổ truyền, lồng tiếng thuần Việt và âm nhạc nhạc cụ dân tộc phối hiện đại."
    },
    {
        "id": "casual_party_pvp_1min",
        "name": "Casual 1-Minute Party PvP (Đấu Trường Tiệc Tùng 1 Phút)",
        "classification": "BLUE_OCEAN",
        "classification_label": "🟦 Đại Dương Xanh (Viral Cực Nhanh)",
        "competition_index": 38,
        "revenue_potential": 82,
        "cpi_estimate": "$0.40 - $0.85",
        "development_effort": "Nhẹ (Đội ngũ 4 - 8 người trong 4-6 tháng)",
        "target_audience": "Nhóm bạn bè học sinh, sinh viên, dân văn phòng cần giải trí nhanh trong giờ nghỉ trưa.",
        "market_gap_analysis": "Các tựa game PvP hiện nay (Liên Quân, Tốc Chiến, Free Fire) đòi hỏi mỗi trận kéo dài 15-20 phút và quá căng thẳng. Thị trường thiếu hụt trầm trọng các game đối kháng vui nhộn, chơi cùng bạn bè với thời lượng đúng 60 giây/trận để lan tỏa tự nhiên trên TikTok/Reels.",
        "recommended_studio_pitch": "Game Party brawler màn hình dọc: 4 người cùng vào một sàn đấu thu nhỏ, dùng các chiêu thức đẩy nhau lọt hố hoặc né bẫy. Trận đấu 60 giây kết thúc, dễ dàng mời bạn bè qua link chia sẻ Zalo/Messenger."
    },
    {
        "id": "idle_merge_tower_defense",
        "name": "Idle Merge Tower Defense (Tháp Phòng Kết Hợp Hợp Nhất Vật Phẩm)",
        "classification": "EMERGING",
        "classification_label": "🟨 Cân Bằng Tiềm Năng (Mới Nổi)",
        "competition_index": 52,
        "revenue_potential": 76,
        "cpi_estimate": "$0.70 - $1.35",
        "development_effort": "Nhẹ đến Trung bình",
        "target_audience": "Người chơi thích tính toán chiến lược nhưng không có thời gian cắm máy (Hybrid-casual gamer).",
        "market_gap_analysis": "Dòng game thủ thành truyền thống quá phức tạp, còn game ghép đồ (Merge) thuần túy lại thiếu chiều sâu chiến thuật. Kết hợp cơ chế ghép 2 trụ giống nhau để thăng cấp tự động bắn quái mang lại tỷ lệ giữ chân D7 vượt trội (>18%).",
        "recommended_studio_pitch": "Cơ chế: Kéo thả ghép trụ lính bảo vệ vương quốc. Tích hợp mô hình Hybrid Monetization: 70% IAP mua tướng thần thoại, 30% xem quảng cáo tự nguyện nhận x2 tốc độ trận đấu."
    },
    {
        "id": "three_kingdoms_slg_4x",
        "name": "Tam Quốc SLG 4X Cổ Điển (Chiến Thuật Xây Thành Điều Binh)",
        "classification": "RED_OCEAN",
        "classification_label": "🟥 Đại Dương Đỏ (Cực Kỳ Đẫm Máu - Tránh Xa)",
        "competition_index": 96,     # Extremely high competition
        "revenue_potential": 92,     # High revenue, but controlled by top publishers
        "cpi_estimate": "$6.50 - $12.00",
        "development_effort": "Rất lớn (Ngân sách > 1.5 triệu USD, đội ngũ 40+ người)",
        "target_audience": "Whales trung niên chịu chi, fan Tam Quốc cứng tuổi.",
        "market_gap_analysis": "CẢNH BÁO NGUY HIỂM: Phân khúc này đã bị các tập đoàn khổng lồ (Koei Tecmo, Efun, VNG, NetEase) độc chiếm hoàn toàn. Chi phí mua 1 lượt tải (CPI) bị đẩy lên tới $10-$15. Studio nhỏ lao vào đây chắc chắn sẽ cạn kiệt ngân sách marketing trước khi kịp thu hồi vốn.",
        "recommended_studio_pitch": "KHUYẾN NGHỊ: Không nên phát triển thể loại này trừ khi bạn có ngân sách marketing trên 10 tỷ VNĐ và bản quyền IP chính chủ nổi tiếng."
    },
    {
        "id": "anime_open_world_gacha",
        "name": "Anime Open-World Gacha AAA (Thế Giới Mở Anime Bom Tấn)",
        "classification": "RED_OCEAN",
        "classification_label": "🟥 Đại Dương Đỏ (Chi Phí Sản Xuất Khổng Lồ)",
        "competition_index": 92,
        "revenue_potential": 98,
        "cpi_estimate": "$4.50 - $9.00",
        "development_effort": "Cực khủng (Hàng chục triệu USD, 100+ kỹ sư)",
        "target_audience": "Otaku toàn cầu yêu thích đồ họa chuẩn Console.",
        "market_gap_analysis": "Thống trị bởi các gã khổng lồ HoYoverse (Genshin, Star Rail), Kuro Games (Wuthering Waves) và Tencent. Tiêu chuẩn đồ họa và kỳ vọng của người chơi đã bị đẩy lên quá cao, studio vừa và nhỏ không có cơ hội cạnh tranh trực diện.",
        "recommended_studio_pitch": "Né tránh làm game 3D thế giới mở quy mô lớn; thay vào đó nên khai thác lối chơi màn hình dọc (Vertical Anime Gacha) hoặc 2D Stylized với chi phí sản xuất thấp hơn 90%."
    }
]

# Aging Monopolies (Top-grossing games that are > 4-5 years old with outdated tech)
AGING_MONOPOLIES_DATABASE: List[Dict[str, Any]] = [
    {
        "franchise": "Các Game Nông Trại Truyền Thống (Hay Day, Township...)",
        "age_years": "9 - 12 năm",
        "current_status": "Vẫn lọt Top Doanh thu nhưng đồ họa 2D cũ kỹ, cơ chế thời gian chờ (timer) tạo cảm giác ức chế, thiếu tính năng tương tác xã hội thời gian thực.",
        "player_pain_point": "Người chơi phàn nàn thời gian đợi sản xuất nông sản quá lâu (4-8 tiếng) ép nạp tiền, thiếu tính năng nuôi pet đồng hành và thời trang nhân vật cá nhân hóa.",
        "disruption_opportunity": "Tung game Nông trại 3D đồ họa Chibi dễ thương, bổ sung cơ chế Co-op làm nông cùng người yêu/bạn bè và mini-game khám phá hòn đảo bí ẩn không giới hạn thời gian chờ.",
        "vulnerability_score": "88/100 (Cực kỳ dễ bị lật đổ bởi game thế hệ mới)"
    },
    {
        "franchise": "Dòng Game Chiến Thuật Thẻ Tướng Màn Ngang 2D Kiểu Cũ",
        "age_years": "6 - 8 năm",
        "current_status": "Lối chơi auto bấm kỹ năng nhàm chán, phụ thuộc 100% vào chỉ số lực chiến P2W, hoạt ảnh nhân vật cứng nhắc.",
        "player_pain_point": "Người chơi chán ngấy các giải đấu chỉ cần nạp tiền nhiều hơn là thắng 100% không cần tư duy, thiếu yếu tố địa hình và khắc chế chiến thuật sâu.",
        "disruption_opportunity": "Thay thế bằng cơ chế Auto-battler bàn cờ (TFT mobile style) kết hợp thẻ bài: thắng bại phụ thuộc vào cách sắp xếp trận đồ và kích hoạt hệ tộc, cho phép người cày chay dùng đầu óc lật kèo đại gia.",
        "vulnerability_score": "82/100 (Rất dễ thu hút người chơi thất vọng chuyển sang)"
    },
    {
        "franchise": "Game Bắn Cá Đổi Thưởng Cổ Điển",
        "age_years": "7 - 10 năm",
        "current_status": "Giao diện lòe loẹt, âm thanh ồn ào, cơ chế hút máu quá rõ ràng khiến người chơi trẻ tuổi quay lưng.",
        "player_pain_point": "Thế hệ Gen Z coi bắn cá truyền thống là trò chơi cờ bạc lỗi thời, không có cốt truyện hay yếu tố phiêu lưu nhập vai.",
        "disruption_opportunity": "Hiện đại hóa thành thể loại Thám Hiểm Đại Dương Đáy Biển (Deep Sea Rogue Hunting): vừa săn cá quái vật biển sâu, vừa nâng cấp tàu ngầm và mở khóa bí mật Atlantis.",
        "vulnerability_score": "75/100 (Cơ hội khai phá phân khúc đại dương mới)"
    }
]

class BlueOceanFinder:
    """Provides market saturation radar and discovers untapped mobile sub-genres."""

    def __init__(self):
        self.niches = MARKET_NICHES_DATABASE
        self.aging_monopolies = AGING_MONOPOLIES_DATABASE

    def get_market_niches(self, classification: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns market niches filtered by ocean type (BLUE_OCEAN, GOLDEN_NICHE, RED_OCEAN)."""
        if classification and classification.lower() != "all":
            return [n for n in self.niches if n["classification"].lower() == classification.lower()]
        return self.niches

    def get_aging_monopolies(self) -> List[Dict[str, Any]]:
        """Returns franchises vulnerable to disruption by new studios."""
        return self.aging_monopolies

    def get_market_overview_stats(self) -> Dict[str, Any]:
        """Calculates macro metrics for market opportunities."""
        blue_count = sum(1 for n in self.niches if n["classification"] == "BLUE_OCEAN")
        niche_count = sum(1 for n in self.niches if n["classification"] == "GOLDEN_NICHE")
        red_count = sum(1 for n in self.niches if n["classification"] == "RED_OCEAN")

        return {
            "total_niches_analyzed": len(self.niches),
            "blue_oceans_count": blue_count,
            "golden_niches_count": niche_count,
            "red_oceans_danger_count": red_count,
            "aging_monopolies_count": len(self.aging_monopolies),
            "top_recommended_niche": self.niches[0]["name"] if self.niches else "Cozy Farming Roguelike"
        }
