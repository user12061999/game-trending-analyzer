"""Mobile ASO Visual Optimizer & Icon/Screenshot CVR Predictor.

Provides visual archetype benchmarks, clickability scoring, and metadata keyword audit
to maximize store conversion rate (CVR) and organic search rankings.
"""

from typing import Dict, Any, List, Optional
import re

class ASOVisualOptimizer:
    """ASO Visual Analysis & Metadata Optimization Engine for Mobile Games."""

    def __init__(self):
        # Benchmark Icon Visual Archetypes
        self.icon_archetypes = [
            {
                "id": "screaming_hero",
                "name": "Screaming Character Hero (Mouth Open / Battle Cry)",
                "tag": "High-Action CTR Driver",
                "cvr_lift": "+28%",
                "avg_cvr": 29.4,
                "best_genres": ["4X Strategy", "Action", "Battle Royale", "RPG", "Tower Defense"],
                "color_palette": ["High-contrast Crimson Red", "Vibrant Gold", "Electric Blue"],
                "visual_elements": [
                    "Main hero angled at 3/4 perspective facing right",
                    "Mouth open roaring with visible teeth and intense eye focus",
                    "Dramatic rim lighting (high contrast background to pop on dark/light store themes)",
                    "Bold character border (1-2px subtle glow to separate from wallpaper)"
                ],
                "psychology": "Kích thích cảm xúc adrenaline, tính cạnh tranh và hành động khẩn cấp. Tăng CTR trong nhóm người chơi mid-core & hardcore.",
                "dos_and_donts": {
                    "dos": ["Dùng nhân vật có biểu cảm khuôn mặt sắc nét, đồng tử rõ ràng", "Test cả nền sáng và nền tối"],
                    "donts": ["Không nhồi nhét quá nhiều chi tiết vụn vặt quanh viền", "Tránh che miệng hoặc biểu cảm vô hồn"]
                }
            },
            {
                "id": "glossy_tactile_object",
                "name": "3D Glossy / Hyper-Tactile Object",
                "tag": "Satisfying Casual Magnet",
                "cvr_lift": "+34%",
                "avg_cvr": 33.8,
                "best_genres": ["Match-3", "Tile Puzzle", "Merge", "Simulation", "Hyper-casual"],
                "color_palette": ["Candy Neon Pink", "Cyan Cyan", "Juicy Lime Green", "Warm Sunshine Yellow"],
                "visual_elements": [
                    "Single oversized 3D object centered (kẹo ngọt, khối ngọc, bình potion ma thuật)",
                    "Hyper-glossy specular reflection (hiệu ứng bóng gương, giọt nước trong suốt)",
                    "Subtle ambient occlusion shadow tạo chiều sâu nổi khối giả lập 3D",
                    "Tương phản màu sắc tươi tắn trên nền gradient pastel"
                ],
                "psychology": "Kích hoạt cảm giác thỏa mãn thị giác (tactile satisfaction) như muốn chạm/bấm ngay vào màn hình.",
                "dos_and_donts": {
                    "dos": ["Tập trung 1 vật phẩm đại diện rõ nét nhất (chỉ chiếm 75% khung hình)", "Gia tăng độ bóng mượt"],
                    "donts": ["Không để quá 3 vật thể nhỏ làm loãng tiêu điểm", "Tránh màu tối xỉn"]
                }
            },
            {
                "id": "anime_waifu_portrait",
                "name": "Anime Waifu / Bishoujo Close-Up",
                "tag": "Tier 1 JP/KR/SEA Heavy Hitter",
                "cvr_lift": "+42%",
                "avg_cvr": 36.2,
                "best_genres": ["Anime RPG", "Gacha", "Visual Novel", "Idle Battler", "Turn-based RPG"],
                "color_palette": ["Soft Sakura Pink", "Twilight Purple", "Ethereal Cyan", "Golden Amber"],
                "visual_elements": [
                    "Cận cảnh khuôn mặt nữ thần (bust portrait) với ánh mắt trực diện (direct eye contact)",
                    "Chi tiết tóc bồng bềnh, phụ kiện đặc trưng (tai thú, vương miện, nơ bướm)",
                    "Đôi mắt to lung linh với hiệu ứng phản chiếu ánh sáng đa lớp",
                    "Nụ cười mỉm bí ẩn hoặc ánh nhìn tình cảm cuốn hút"
                ],
                "psychology": "Khai thác mối quan hệ cảm xúc parasocial (Waifu factor), tạo độ gắn kết cá nhân ngay từ lần đầu nhìn thấy trên Store.",
                "dos_and_donts": {
                    "dos": ["Chọn nhân vật SSR/UR nổi tiếng nhất game làm gương mặt đại diện", "Giữ đường nét anime trong trẻo"],
                    "donts": ["Tránh ảnh vẽ phẳng thiếu bóng đổ", "Không dùng tỷ lệ toàn thân (Full-body) vì thu nhỏ lại không thấy mặt"]
                }
            },
            {
                "id": "level_progression_split",
                "name": "Level 1 vs Level 100 Progression Split",
                "tag": "Dopamine Aspiration Trigger",
                "cvr_lift": "+22%",
                "avg_cvr": 26.5,
                "best_genres": ["Idle Tycoon", "Runner", "Survival Roguelike", "Merge / Evolution"],
                "color_palette": ["Drab Gray/Brown (Trái)", "Radiant Gold/Purple (Phải)"],
                "visual_elements": [
                    "Khung hình chia đôi chéo hoặc dọc (bên trái nghèo nàn, bên phải quyền lực)",
                    "Nhãn 'Lv. 1' nhỏ bé so với 'Lv. 100' trang bị thần thoại lấp lánh",
                    "Mũi tên thăng cấp (Green Upgrade Arrow) tạo cảm giác dễ dàng phát triển"
                ],
                "psychology": "Đánh vào mong muốn thăng tiến nhanh, biến từ 'kẻ vô danh' thành 'bá vương' mà không tốn công sức.",
                "dos_and_donts": {
                    "dos": ["Tạo độ chênh lệch cực đại giữa 2 cấp độ", "Dùng font chữ số to đậm rõ ràng"],
                    "donts": ["Không chia quá 3 nấc làm rối mắt", "Tránh chữ quá nhỏ không đọc được ở kích thước 64x64"]
                }
            },
            {
                "id": "minimalist_emblem",
                "name": "Minimalist Bold Emblem & Logo",
                "tag": "Competitive Brand Authority",
                "cvr_lift": "+15%",
                "avg_cvr": 22.1,
                "best_genres": ["Card Games", "Chess", "Esports MOBA", "Racing Sim", "Tactical Shooter"],
                "color_palette": ["Obsidian Black", "Pure Titanium White", "Vibrant Accent Neon"],
                "visual_elements": [
                    "Biểu tượng vector tối giản (huy hiệu khiên, đầu lâu phong cách, chữ cái cách điệu)",
                    "Flat graphic design với độ tương phản cực hạn",
                    "Độ nhận diện thương hiệu tức thì kể cả ở icon kích thước cực nhỏ 32x32"
                ],
                "psychology": "Tạo cảm giác chuyên nghiệp, gameplay sâu, uy tín và đẳng cấp esport.",
                "dos_and_donts": {
                    "dos": ["Biểu tượng hình học sắc nét, ghi nhớ ngay sau 1 giây", "Dành cho game có cộng đồng hoặc IP mạnh"],
                    "donts": ["Không dùng cho game hyper-casual chưa có thương hiệu", "Tránh màu nền tiệp với icon"]
                }
            }
        ]

        # Common high-value gaming search keywords & traffic weights
        self.keyword_bank = {
            "rpg": {"volume": 94, "difficulty": 88, "intent": "Core Gamers"},
            "action": {"volume": 91, "difficulty": 85, "intent": "High Adrenaline"},
            "pvp": {"volume": 86, "difficulty": 82, "intent": "Competitive"},
            "multiplayer": {"volume": 89, "difficulty": 84, "intent": "Social Gaming"},
            "strategy": {"volume": 82, "difficulty": 79, "intent": "Tactical/Spender"},
            "idle": {"volume": 85, "difficulty": 72, "intent": "Casual Spender"},
            "gacha": {"volume": 78, "difficulty": 75, "intent": "Collector/Whale"},
            "anime": {"volume": 88, "difficulty": 81, "intent": "High LTV Fanbase"},
            "puzzle": {"volume": 92, "difficulty": 86, "intent": "Mass Market Casual"},
            "match 3": {"volume": 87, "difficulty": 90, "intent": "Mature Female Spenders"},
            "3d": {"volume": 79, "difficulty": 68, "intent": "Visual Quality"},
            "survival": {"volume": 84, "difficulty": 76, "intent": "Trending Mid-core"},
            "battle": {"volume": 88, "difficulty": 83, "intent": "Action Focus"},
            "tycoon": {"volume": 76, "difficulty": 65, "intent": "Casual Progression"},
            "offline": {"volume": 89, "difficulty": 70, "intent": "Emerging Markets/Utility"},
            "simulator": {"volume": 83, "difficulty": 74, "intent": "Mass Market Discovery"}
        }

    def get_visual_archetypes(self) -> List[Dict[str, Any]]:
        """Returns the benchmark visual archetypes for mobile icons and screenshots."""
        return self.icon_archetypes

    def audit_metadata(
        self,
        title: str,
        subtitle: str,
        keywords: str,
        genre: str = "RPG",
        icon_archetype_id: str = "screaming_hero",
        target_store: str = "google_play"
    ) -> Dict[str, Any]:
        """Performs a deep ASO metadata and visual synergy audit."""
        title = title.strip()
        subtitle = subtitle.strip()
        keywords_list = [k.strip().lower() for k in keywords.split(",") if k.strip()]

        # Character limits
        title_limit = 30
        subtitle_limit = 30 if target_store == "app_store" else 80

        title_len = len(title)
        subtitle_len = len(subtitle)

        # Keyword density & search intent analysis
        matched_keywords = []
        combined_text = f"{title} {subtitle} {' '.join(keywords_list)}".lower()

        total_volume = 0
        total_difficulty = 0
        for kw, meta in self.keyword_bank.items():
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, combined_text):
                matched_keywords.append({
                    "keyword": kw,
                    "volume": meta["volume"],
                    "difficulty": meta["difficulty"],
                    "intent": meta["intent"],
                    "found_in": "Title" if re.search(pattern, title.lower()) else ("Subtitle" if re.search(pattern, subtitle.lower()) else "Keyword Field")
                })
                total_volume += meta["volume"]
                total_difficulty += meta["difficulty"]

        avg_vol = round(total_volume / max(1, len(matched_keywords)), 1)
        avg_diff = round(total_difficulty / max(1, len(matched_keywords)), 1)

        # Archetype lookup
        archetype = next((a for a in self.icon_archetypes if a["id"] == icon_archetype_id), self.icon_archetypes[0])

        # Calculate CVR Estimate
        base_cvr = archetype["avg_cvr"]
        genre_bonus = 3.5 if genre.lower() in [g.lower() for g in archetype["best_genres"]] else -1.5
        length_penalty = 0.0

        if title_len < 10:
            length_penalty -= 3.0
        elif title_len > title_limit:
            length_penalty -= 5.0

        if subtitle_len < 10:
            length_penalty -= 2.0
        elif subtitle_len > subtitle_limit:
            length_penalty -= 4.0

        kw_bonus = min(len(matched_keywords) * 1.2, 6.0)
        estimated_cvr = round(max(10.0, min(50.0, base_cvr + genre_bonus + kw_bonus + length_penalty)), 1)

        # Health Grade
        total_score = min(100, int((estimated_cvr / 45.0) * 100))
        if total_score >= 85:
            grade = "A+ (Excellent)"
            badge_color = "emerald"
        elif total_score >= 70:
            grade = "A (Strong CVR)"
            badge_color = "indigo"
        elif total_score >= 55:
            grade = "B (Acceptable)"
            badge_color = "amber"
        else:
            grade = "C (Needs Optimization)"
            badge_color = "rose"

        # Actionable recommendations
        recommendations = []
        if title_len > title_limit:
            recommendations.append(f"Tiêu đề vượt quá giới hạn {title_limit} ký tự ({title_len}/{title_limit}). Store có thể cắt bớt hiển thị.")
        elif title_len < 18:
            recommendations.append(f"Tiêu đề còn ngắn ({title_len}/{title_limit} ký tự). Hãy chèn thêm 1 từ khóa cốt lõi (ví dụ: '{title}: 3D Action RPG').")

        if subtitle_len > subtitle_limit:
            recommendations.append(f"Phụ đề/Short description vượt giới hạn {subtitle_limit} ký tự.")
        elif subtitle_len < 20:
            recommendations.append("Mô tả ngắn/Phụ đề chưa nêu bật Hook hoặc tính năng độc quyền (USP).")

        if genre.lower() not in [g.lower() for g in archetype["best_genres"]]:
            recommendations.append(f"Phong cách Icon '{archetype['name']}' thường mang lại CVR cao nhất cho {', '.join(archetype['best_genres'])}. Với thể loại {genre}, cân nhắc A/B test với phong cách khác.")
        else:
            recommendations.append(f"Lựa chọn phong cách Icon '{archetype['name']}' cực kỳ ăn khớp với thể loại {genre} (+{archetype['cvr_lift']} CVR benchmark).")

        if len(matched_keywords) < 2:
            recommendations.append("Chưa phát hiện từ khóa tìm kiếm phổ biến trong Title/Subtitle. Cân nhắc bổ sung: 'PvP', 'Online', 'Idle', hoặc 'Survival'.")

        return {
            "title_analysis": {
                "text": title,
                "length": title_len,
                "limit": title_limit,
                "is_valid": title_len <= title_limit
            },
            "subtitle_analysis": {
                "text": subtitle,
                "length": subtitle_len,
                "limit": subtitle_limit,
                "is_valid": subtitle_len <= subtitle_limit
            },
            "archetype_selected": archetype,
            "estimated_cvr": estimated_cvr,
            "overall_score": total_score,
            "health_grade": grade,
            "badge_color": badge_color,
            "matched_keywords": matched_keywords,
            "keyword_metrics": {
                "detected_count": len(matched_keywords),
                "avg_search_volume": avg_vol,
                "avg_ranking_difficulty": avg_diff
            },
            "recommendations": recommendations
        }
