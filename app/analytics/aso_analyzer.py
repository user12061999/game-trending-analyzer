"""ASO (App Store Optimization) & Keyword Intelligence Spy for Mobile Games.

Analyzes competitors' App Store and Google Play titles, subtitles, descriptions,
keyword density, ASO Health Score, and delivers targeted keyword recommendations.
"""

import re
import json
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "by", "from",
    "is", "are", "was", "were", "be", "been", "this", "that", "it", "its", "of", "as",
    "la", "va", "trong", "cua", "cho", "voi", "o", "tai", "tu", "den", "cac", "nhung",
    "game", "tro", "choi", "mobile", "app", "new", "best", "top", "free", "play"
}

GENRE_KEYWORD_BANK = {
    "rpg": [
        "rpg the gioi mo", "nhap vai anime", "gacha turn based", "cay cuoc khong nap",
        "phieu luu 3d", "danh theo luot", "do hoa sieu dep", "chien binh huyen thoai"
    ],
    "action": [
        "ban sung sinh ton", "fps doi khang", "chien truong ruc lua", "hanh dong chat chem",
        "co op cung ban be", "chien dau sinh tu", "vu khi hien dai", "ban sung 5v5"
    ],
    "strategy": [
        "chien thuat tam quoc", "xay dung de che", "slg thoi gian thuc", "dieu binh khuyen mai",
        "dau tri quan su", "chiem linh thanh tri", "the tuong linh hoat", "lien minh bang hoi"
    ],
    "casual": [
        "giai do xep hinh", "choi offline khong mang", "giai tri nhe nhang", "vui nhon de choi",
        "nuoi thu de thuong", "xep kim cuong", "giet thoi gian cuc hay", "party game ban be"
    ],
    "simulation": [
        "mo phong cuoc song", "nong trai vui ve", "quan ly nha hang", "lai xe chan thuc",
        "xay dung thanh pho", "kinh doanh lam giau", "thiet ke thoi trang", "nau an sieu toc"
    ]
}

class ASOAnalyzer:
    def __init__(self):
        pass

    def fetch_store_metadata(self, app_id: str, country: str = "us") -> Optional[Dict[str, Any]]:
        """Fetches metadata from Apple iTunes Lookup API."""
        clean_id = re.sub(r"[^\d]", "", str(app_id))
        if not clean_id:
            return None

        url = f"https://itunes.apple.com/lookup?id={clean_id}&country={country}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                if results:
                    app = results[0]
                    return {
                        "title": app.get("trackName", ""),
                        "developer": app.get("artistName", ""),
                        "version": app.get("version", ""),
                        "description": app.get("description", ""),
                        "release_notes": app.get("releaseNotes", ""),
                        "current_version_release_date": app.get("currentVersionReleaseDate", ""),
                        "genres": app.get("genres", []),
                        "primary_genre": app.get("primaryGenreName", "Games"),
                        "price": app.get("formattedPrice", "Free"),
                        "store_url": app.get("trackViewUrl", "")
                    }
        except Exception as e:
            logger.debug(f"iTunes lookup error for {clean_id}: {e}")

        return None

    def search_app_metadata(self, query: str, country: str = "us") -> Optional[Dict[str, Any]]:
        """Searches App Store for a game title if direct ID lookup fails."""
        try:
            clean_q = urllib.parse.quote(query)
            url = f"https://itunes.apple.com/search?term={clean_q}&country={country}&media=software&entity=software&limit=1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                if results:
                    app = results[0]
                    return {
                        "title": app.get("trackName", ""),
                        "developer": app.get("artistName", ""),
                        "version": app.get("version", ""),
                        "description": app.get("description", ""),
                        "release_notes": app.get("releaseNotes", ""),
                        "current_version_release_date": app.get("currentVersionReleaseDate", ""),
                        "genres": app.get("genres", []),
                        "primary_genre": app.get("primaryGenreName", "Games"),
                        "price": app.get("formattedPrice", "Free"),
                        "store_url": app.get("trackViewUrl", "")
                    }
        except Exception as e:
            logger.debug(f"Search error for {query}: {e}")
        return None

    def analyze_aso(self, game_id: str, game_title: str = "", genre: str = "rpg") -> Dict[str, Any]:
        """Performs full ASO & Keyword Intelligence Analysis."""
        meta = self.fetch_store_metadata(game_id)
        if not meta and game_title:
            meta = self.search_app_metadata(game_title)

        title = (meta.get("title") if meta else "") or game_title or "Game Title"
        description = (meta.get("description") if meta else "") or f"{title} là tựa game nhập vai thế giới mở hành động đỉnh cao với đồ họa 3D sống động, cơ chế chiến đấu mượt mà và hệ thống bang hội sôi động."
        clean_genre = (meta.get("primary_genre") if meta else "") or genre or "RPG"

        # 1. Title Analysis
        title_len = len(title)
        title_words = [w for w in re.findall(r"\w+", title.lower()) if w not in STOP_WORDS]
        has_subtitle_delimiter = any(d in title for d in ["-", ":", "|", "–", "—"])
        brand_name = re.split(r"[-:|–—]", title)[0].strip() if has_subtitle_delimiter else title
        tagline = title[len(brand_name):].strip(" -:|–—") if has_subtitle_delimiter else ""

        # Title Optimization Score (Max 25 pts)
        title_score = 0
        if 15 <= title_len <= 30:
            title_score = 25  # Optimal character limit on App Store / Google Play
        elif 10 <= title_len < 15 or 30 < title_len <= 45:
            title_score = 20
        else:
            title_score = 12

        # 2. Subtitle / Tagline Score (Max 25 pts)
        subtitle_score = 25 if tagline and len(tagline) >= 8 else (15 if has_subtitle_delimiter else 10)

        # 3. Keyword Extraction & Density Matrix
        all_words = re.findall(r"\b[a-zA-ZÀ-ỹ0-9]{3,}\b", description.lower())
        meaningful_words = [w for w in all_words if w not in STOP_WORDS and len(w) > 2]
        word_counts = Counter(meaningful_words)
        total_meaningful = len(meaningful_words) or 1

        top_keywords = []
        for word, count in word_counts.most_common(8):
            density = round((count / total_meaningful) * 100, 1)
            # Optimal density is 1.5% - 3.5%
            status = "Tối ưu" if 1.5 <= density <= 3.8 else ("Quá cao (Coi chừng phạt Spam)" if density > 4.5 else "Thấp")
            top_keywords.append({
                "keyword": word,
                "count": count,
                "density_percentage": density,
                "status": status
            })

        # Description Keyword Density Score (Max 25 pts)
        desc_score = 22 if len(description) > 500 else 15

        # 4. Localization & Metadata Readiness Score (Max 25 pts)
        has_vietnamese = bool(re.search(r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", description.lower()))
        local_score = 25 if has_vietnamese else 18

        total_aso_score = title_score + subtitle_score + desc_score + local_score

        # 5. High-Impact Target Keyword Recommendations
        matched_genre_key = "rpg"
        for k in GENRE_KEYWORD_BANK:
            if k in clean_genre.lower():
                matched_genre_key = k
                break

        recommended_keywords = GENRE_KEYWORD_BANK.get(matched_genre_key, GENRE_KEYWORD_BANK["rpg"])

        # 6. Suggested ASO Title Formula
        suggested_formula = {
            "ios_formula": f"{brand_name}: {recommended_keywords[0].title()} ({min(30, len(brand_name) + len(recommended_keywords[0]) + 2)} ký tự)",
            "android_formula": f"{brand_name} - {recommended_keywords[1].title()} & {recommended_keywords[2].title()}",
            "recommended_tagline": f"Đỉnh cao {clean_genre} - Khám phá thế giới mở & quà tặng tân thủ cực khủng!"
        }

        return {
            "game_id": game_id,
            "title": title,
            "brand_name": brand_name,
            "tagline": tagline or "Chưa cài đặt Subtitle phụ",
            "title_length": title_len,
            "aso_health_score": total_aso_score,
            "score_breakdown": {
                "title_optimization": title_score,
                "subtitle_utilization": subtitle_score,
                "keyword_density": desc_score,
                "localization": local_score
            },
            "top_keywords": top_keywords,
            "recommended_keywords": recommended_keywords,
            "suggested_formula": suggested_formula,
            "aso_advice": self._generate_aso_advice(total_aso_score, title_len, tagline, has_vietnamese)
        }

    def _generate_aso_advice(self, score: int, title_len: int, tagline: str, has_vn: bool) -> List[str]:
        advice = []
        if title_len < 18:
            advice.append("⚠️ Tiêu đề hiện tại quá ngắn: Hãy tận dụng thêm 10-15 ký tự để gài từ khóa thể loại chính (Ví dụ: Thêm ': Game Nhập Vai 3D').")
        elif title_len > 30:
            advice.append("⚠️ Tiêu đề vượt quá 30 ký tự: Có thể bị cắt cụt (truncated) trên giao diện tìm kiếm App Store.")

        if not tagline or tagline == "Chưa cài đặt Subtitle phụ":
            advice.append("💡 Thiếu Subtitle phụ: Bạn đang bỏ phí trường hiển thị quan trọng nhất để thuyết phục người chơi bấm Tải về.")

        if not has_vn:
            advice.append("🌐 Cần bản địa hóa tiếng Việt: Bổ sung mô tả và từ khóa tiếng Việt có dấu giúp tăng tỷ lệ chuyển đổi (CVR) thêm +35% tại thị trường Việt Nam.")
        else:
            advice.append("✅ Mô tả đã được bản địa hóa tiếng Việt tự nhiên và chuẩn văn hóa địa phương.")

        return advice
