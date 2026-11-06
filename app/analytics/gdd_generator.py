"""AI Game Concept & 1-Page GDD (Game Design Document) Generator.

Synthesizes market trends, core gameplay loops, meta-progression, monetization architecture,
and audience personas into an executive 1-Page GDD ready for greenlight meetings and publisher pitches.
"""

from typing import Dict, Any, List, Optional
import json

class GameDesignDocumentGenerator:
    """Generates structured 1-Page Game Design Documents and pitch sheets."""

    PRESETS = [
        {
            "id": "action_roguelike_survivor",
            "title": "Valkyrie Survivor: Ragnarok",
            "genre": "Action Roguelike / Bullet Heaven",
            "platform": "PC Steam & Mobile Hybrid",
            "target_audience": "Mid-core gamers, Vampire Survivors / Brotato fans, short session players",
            "art_style": "Dark Nordic Fantasy, Stylized High-Contrast 2.5D with Neon VFX",
            "monetization_model": "Premium Buy-to-Play on Steam ($7.99) / Hybrid-Casual on Mobile (Rewarded Ads + Battle Pass)"
        },
        {
            "id": "anime_gacha_rpg",
            "title": "Aether Horizon: Stella Chrono",
            "genre": "Open-World / Turn-based Anime RPG",
            "platform": "Mobile (iOS / Android) & PC Cross-Platform",
            "target_audience": "Gen Z Anime Otaku, Gacha collectors, Honkai Star Rail & Genshin fans",
            "art_style": "Cel-shaded Anime Live2D + High-End 3D Cinematic Burst Ultimates",
            "monetization_model": "F2P Gacha (Character Banners 0.6% SSR rate) + $4.99 Monthly Pass + $9.99 Battle Pass"
        },
        {
            "id": "hybrid_4x_strategy",
            "title": "Frost Fortress: Last Bastion",
            "genre": "Hybrid 4X Strategy / City Survival",
            "platform": "Mobile Exclusive (iOS & Android)",
            "target_audience": "Casual-to-Hardcore Strategy Whales, Whiteout Survival / State of Survival players",
            "art_style": "Isometric Low-Poly 3D, Stylized Blizzard Atmosphere, Warm Firelight VFX",
            "monetization_model": "Aggressive F2P 4X (Speed-ups, Whale VIP 15, Clan War Shield Bundles, $0.99 First Recharge)"
        },
        {
            "id": "cozy_merge_decor",
            "title": "Whispering Bistro: Merge & Mystery",
            "genre": "Casual Merge-2 / Renovation & Drama",
            "platform": "Mobile Exclusive",
            "target_audience": "Female casual audience 25-45, Gossip Harbor / Merge Mansion fans",
            "art_style": "Warm Pastel Toon, Cozy Studio Ghibli inspired cafe illustration",
            "monetization_model": "Energy Sinks, Piggy Bank IAP ($1.99), Narrative Unlock Gate Bundles, Rewarded Ad Spins"
        }
    ]

    def get_presets(self) -> List[Dict[str, Any]]:
        """Returns standard genre concept presets."""
        return self.PRESETS

    def generate_gdd(
        self,
        title: str = "Project Apex Horizon",
        genre: str = "Action Roguelike / Survival",
        platform: str = "PC Steam & Mobile Cross-Platform",
        target_audience: str = "Mid-Core Gamers, Fast APM enthusiasts",
        art_style: str = "Stylized Cyberpunk Anime",
        monetization_model: str = "Hybrid Free-to-Play (Rewarded Ads + Battle Pass + Cosmetic IAP)"
    ) -> Dict[str, Any]:
        """Generates a complete structured 1-Page GDD."""

        # Core loop blueprints tailored per genre
        core_loops = self._build_core_loops(genre)
        monetization_spec = self._build_monetization_architecture(monetization_model, platform)
        usps = self._build_usps(genre, title)
        liveops_calendar = self._build_liveops_calendar(genre)

        gdd_payload = {
            "metadata": {
                "document_version": "1.0 - Production Greenlight Ready",
                "game_title": title,
                "genre": genre,
                "platform": platform,
                "target_audience": target_audience,
                "art_style": art_style,
                "monetization_model": monetization_model
            },
            "elevator_pitch": {
                "high_concept": f"'{title}' là tựa game {genre} kết hợp phong cách đồ họa {art_style}, mang đến nhịp độ chiến đấu kích thích dopamine cao và meta-progression vô tận.",
                "hook_30s": f"Trong vòng 30 giây đầu tiên, người chơi được trải nghiệm ngay cảm giác áp đảo hàng trăm quái vật cùng lúc với hiệu ứng đồ họa bắt mắt, sau đó nâng cấp mở khóa combo kỹ năng mãn nhãn và chinh phục bảng xếp hạng.",
                "market_positioning": f"Đánh vào thị phần ngách đang bùng nổ của {genre}, đón đầu tệp người chơi yêu thích {target_audience} với chi phí CPI dự kiến tối ưu dưới $1.80 (hoặc tỷ lệ Wishlist-to-Sale > 2.5x trên Steam)."
            },
            "core_gameplay_loops": core_loops,
            "key_usps": usps,
            "monetization_architecture": monetization_spec,
            "liveops_cadence": liveops_calendar,
            "kpi_benchmarks": {
                "target_d1_retention": "42.0% - 46.5%",
                "target_d7_retention": "16.0% - 20.0%",
                "target_d30_retention": "6.5% - 9.0%",
                "expected_arpdau": "$0.28 - $0.55 (Tier 1 Global)"
            }
        }

        # Generate markdown and HTML export views
        gdd_payload["markdown_export"] = self._format_as_markdown(gdd_payload)
        return gdd_payload

    def _build_core_loops(self, genre: str) -> Dict[str, Any]:
        """Builds 3-layer gameplay loop."""
        return {
            "minute_loop": {
                "title": "Vòng Lặp Phút (Minute-to-Minute: Action & Feedback)",
                "steps": [
                    "1. Điều khiển nhân vật di chuyển & né tránh chướng ngại vật/quái vật",
                    "2. Kỹ năng tự động thi triển tiêu diệt quái, rớt ngọc kinh nghiệm (Exp Gems / Scrap)",
                    "3. Lên cấp tại chỗ: Chọn 1 trong 3 nâng cấp ngẫu nhiên tạo combo Synergy tức thì"
                ],
                "dopamine_trigger": "Hiệu ứng âm thanh nhặt ngọc liên thanh (slot machine chime) + màn hình nổ pháo hoa VFX khi quét sạch đợt quái."
            },
            "session_loop": {
                "title": "Vòng Lặp Phiên Chơi (12 - 20 Phút: Risk & Extraction)",
                "steps": [
                    "1. Tham gia màn chơi (Run / Dungeon) với tài nguyên thể lực hoặc vé càn quét",
                    "2. Chiến đấu qua 3 mốc thời gian: 5m (Mini-Boss), 10m (Elite Horde), 15m (Final Overlord)",
                    "3. Thu thập vàng vĩnh viễn (Gold) và nguyên liệu hiếm đúc trang bị",
                    "4. Kết thúc Run: Nhận tổng kết điểm số, mở rương kho báu & nâng cấp cây chỉ số vĩnh viễn (Talent Tree)"
                ],
                "dopamine_trigger": "Dù thắng hay thua, người chơi luôn trở nên mạnh hơn ở ván tiếp theo (Sense of Permanent Progression)."
            },
            "meta_loop": {
                "title": "Vòng Lặp Dài Hạn (Days to Weeks: Social & Prestige)",
                "steps": [
                    "1. Cày cuốc cấp độ Battle Pass 30 ngày để mở khóa Trang phục độc quyền",
                    "2. Tham gia Bang Hội Chiến / Leo Tháp Vô Hạn hàng tuần nhận thưởng kim cương",
                    "3. Thu thập trọn bộ sưu tập Nhân vật SSR & Thú cưỡi Huyền thoại",
                    "4. Đua Top Bảng Xếp Hạng Lực Chiến liên server"
                ],
                "dopamine_trigger": "Vị thế xã hội (Social Status) và sự vượt trội trên Leaderboard toàn cầu."
            }
        }

    def _build_monetization_architecture(self, model: str, platform: str) -> Dict[str, Any]:
        """Outlines revenue streams and conversion hooks."""
        return {
            "primary_sinks": [
                {"name": "Gacha / Hero Summon Banner", "desc": "Quay tướng & vũ khí 5 sao với cơ chế Pity bảo hiểm sau 70-80 lượt.", "share": "45%"},
                {"name": "Stamina & Energy Refill", "desc": "Bán lượt hồi thể lực để cày nguyên liệu nâng cấp trang bị nhanh hơn.", "share": "20%"},
                {"name": "Skin Vault & Cosmetics", "desc": "Ngoại trang đổi visual kỹ năng không pay-to-win, hiệu ứng biến về đặc biệt.", "share": "15%"}
            ],
            "conversion_baits": [
                {"name": "First Recharge Bait ($0.99)", "hook": "Tặng ngay Tướng SSR Đỏ + Vũ Khí Tím + 10 Vé Gacha nhằm phá vỡ rào cản chi tiêu lần đầu."},
                {"name": "Piggy Bank Vault ($1.99)", "hook": "Tích lũy kim cương sau mỗi trận thắng. Khi đầy cho phép đập heo với giá rẻ hơn 70% giá shop."}
            ],
            "recurring_subscriptions": [
                {"name": "VIP Monthly Privilege ($4.99/tháng)", "hook": "Nhận 100 kim cương mỗi ngày + Tắt toàn bộ banner ad xen kẽ + Tăng 20% tốc độ di chuyển."},
                {"name": "Seasonal Battle Pass ($9.99/mùa)", "hook": "50 mốc phần thưởng độc quyền trong 30 ngày kèm skin giới hạn."}
            ],
            "ad_placements": [
                {"placement": "Patrol AFK Chest (x2 Rewards)", "type": "Rewarded Video", "ecpm": "$28.00"},
                {"placement": "Revive Once Per Dungeon Run", "type": "Rewarded Video", "ecpm": "$34.00"},
                {"placement": "Daily Lucky Roulette (3 Free Spins)", "type": "Rewarded Video", "ecpm": "$22.00"}
            ]
        }

    def _build_usps(self, genre: str, title: str) -> List[Dict[str, str]]:
        """3 Unique Selling Points differentiating the game."""
        return [
            {
                "usp": "Hệ Thống Phối Hợp Combo Kỹ Năng Đột Phá (Synergy Evolution)",
                "description": "Thay vì chỉ nâng cấp chỉ số đơn thuần, kết hợp 2 vũ khí khác nhau sẽ tiến hóa thành 1 vũ khí thần thoại mới với cơ chế cơ học hoàn toàn khác biệt."
            },
            {
                "usp": "Chế Độ Co-op 2 Người Cùng Máy / Online Tức Thì",
                "description": "Hỗ trợ 2 người chơi cùng sinh tồn trên 1 màn hình điện thoại hoặc ghép đội nhanh 5 giây, tạo tính lan tỏa viral K-Factor cực mạnh trên TikTok."
            },
            {
                "usp": "Engine Vật Lý Phản Ứng Môi Trường (Physics Playground)",
                "description": "Quái vật có thể bị thổi bay vào bẫy gai, rớt xuống vực sâu hoặc kích nổ dây chuyền thùng thuốc súng, đem lại trải nghiệm hài hước và thỏa mãn giác quan."
            }
        ]

    def _build_liveops_calendar(self, genre: str) -> List[Dict[str, str]]:
        """Standard repeatable LiveOps event cadence."""
        return [
            {"frequency": "Thứ 2 - Thứ 4", "event_name": "Rương Cày Cuốc Đầu Tuần", "hook": "Thưởng tăng 50% Exp và Vàng để kích thích người chơi đăng nhập sau cuối tuần."},
            {"frequency": "Thứ 6 - Chủ Nhật", "event_name": "Săn Boss Thế Giới Liên Minh", "hook": "Boss khổng lồ xuất hiện giới hạn 48h, toàn server cùng dồn sát thương nhận rương thần thoại."},
            {"frequency": "Mỗi 30 Ngày", "event_name": "Khởi Tranh Mùa Giải Mới (Season Reset)", "hook": "Reset bảng xếp hạng, cập nhật 2 nhân vật mới, mở bán Battle Pass mùa tiếp theo."}
        ]

    def _format_as_markdown(self, data: Dict[str, Any]) -> str:
        """Formats the GDD into clean GitHub Flavored Markdown."""
        meta = data["metadata"]
        pitch = data["elevator_pitch"]
        loops = data["core_gameplay_loops"]
        usps = data["key_usps"]
        monet = data["monetization_architecture"]

        md = f"""# 🎮 1-PAGE GAME DESIGN DOCUMENT: {meta['game_title'].upper()}
*Document Version: {meta['document_version']}*

---

## 📌 THÔNG TIN TỔNG QUAN (EXECUTIVE SUMMARY)
- **Tựa Game:** {meta['game_title']}
- **Thể Loại:** {meta['genre']}
- **Nền Tảng:** {meta['platform']}
- **Đối Tượng Mục Tiêu:** {meta['target_audience']}
- **Phong Cách Nghệ Thuật:** {meta['art_style']}
- **Mô Hình Kinh Doanh:** {meta['monetization_model']}

### 🎯 High Concept & Elevator Pitch
> **High Concept:** {pitch['high_concept']}

> **30-Second Hook:** {pitch['hook_30s']}

> **Định Vị Thị Trường:** {pitch['market_positioning']}

---

## 🔄 VÒNG LẶP LỐI CHƠI CỐT LÕI (CORE GAMEPLAY LOOPS)

### 1. {loops['minute_loop']['title']}
{chr(10).join(loops['minute_loop']['steps'])}
*Dopamine Trigger:* {loops['minute_loop']['dopamine_trigger']}

### 2. {loops['session_loop']['title']}
{chr(10).join(loops['session_loop']['steps'])}
*Dopamine Trigger:* {loops['session_loop']['dopamine_trigger']}

### 3. {loops['meta_loop']['title']}
{chr(10).join(loops['meta_loop']['steps'])}
*Dopamine Trigger:* {loops['meta_loop']['dopamine_trigger']}

---

## 🌟 3 ĐIỂM KHÁC BIỆT ĐỘC NHẤT (KEY USPs)
"""
        for u in usps:
            md += f"- **{u['usp']}:** {u['description']}\n"

        md += """
---

## 💰 KIẾN TRÚC KINH TẾ & MONETIZATION
### 1. Nguồn Tiêu Tiền Chính (Primary Sinks)
"""
        for s in monet["primary_sinks"]:
            md += f"- **{s['name']} ({s['share']}):** {s['desc']}\n"

        md += "\n### 2. Gói Chuyển Đổi Người Nạp Lần Đầu (Conversion Baits)\n"
        for b in monet["conversion_baits"]:
            md += f"- **{b['name']}:** {b['hook']}\n"

        md += "\n### 3. Doanh Thu Định Kỳ (Subscriptions & Pass)\n"
        for r in monet["recurring_subscriptions"]:
            md += f"- **{r['name']}:** {r['hook']}\n"

        md += "\n### 4. Điểm Chèn Quảng Cáo Rewarded Video (Mobile)\n"
        for ad in monet["ad_placements"]:
            md += f"- **{ad['placement']}** ({ad['type']}) - Dự kiến eCPM: `{ad['ecpm']}`\n"

        md += f"""
---

## 📈 CHỈ SỐ MỤC TIÊU (TARGET METRICS BENCHMARK)
- **D1 Retention:** {data['kpi_benchmarks']['target_d1_retention']}
- **D7 Retention:** {data['kpi_benchmarks']['target_d7_retention']}
- **D30 Retention:** {data['kpi_benchmarks']['target_d30_retention']}
- **Target ARPDAU:** {data['kpi_benchmarks'].get('expected_arpdau', '$0.35')}

---
*Generated by Game Trending Analyzer 2.0 AI Studio*
"""
        return md
