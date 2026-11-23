"""Player Review Sentiment & Churn Miner for Mobile & PC Games.

Scrapes and analyzes 1-5 star user reviews from Apple App Store, Google Play, and Steam.
Extracts sentiment distribution, churn triggers (why players quit), retention hooks,
and provides an actionable Studio Attack Playbook.
"""

import json
import logging
import re
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

from app.analytics.ai_analyst import AIAnalyst

logger = logging.getLogger(__name__)

# Common stop words for keyword extraction in review analysis
STOP_WORDS = {
    "game", "play", "playing", "played", "the", "and", "this", "that", "with", "for",
    "are", "was", "have", "has", "had", "not", "but", "all", "can", "will", "just",
    "like", "good", "great", "very", "much", "more", "even", "from", "they", "them",
    "game", "choi", "trong", "duoc", "khong", "nhung", "minh", "cung", "nhu", "voi"
}

class ReviewMiner:
    def __init__(self):
        self.ai_analyst = AIAnalyst()

    def fetch_apple_reviews(self, app_id: str, country: str = "us", limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent customer reviews from Apple App Store RSS."""
        # Clean app_id: remove non-numeric prefix if present (e.g. appstore_1517783697 -> 1517783697)
        clean_id = re.sub(r"[^\d]", "", str(app_id))
        if not clean_id:
            return []

        url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={clean_id}/sortBy=mostRecent/json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        
        reviews = []
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                entries = data.get("feed", {}).get("entry", [])
                # The first entry in iTunes RSS is usually app summary info, reviews start from index 1
                for e in entries[1:limit + 1]:
                    try:
                        rating = int(e.get("im:rating", {}).get("label", 3))
                        title = e.get("title", {}).get("label", "")
                        content = e.get("content", {}).get("label", "")
                        author = e.get("author", {}).get("name", {}).get("label", "Anonymous")
                        version = e.get("im:version", {}).get("label", "Current")
                        
                        reviews.append({
                            "rating": rating,
                            "title": title,
                            "content": content,
                            "author": author,
                            "version": version,
                            "source": "Apple App Store",
                            "sentiment": "positive" if rating >= 4 else ("negative" if rating <= 2 else "neutral")
                        })
                    except Exception:
                        continue
        except Exception as e:
            logger.debug(f"Failed to fetch Apple reviews for {clean_id}: {e}")

        return reviews

    def fetch_steam_reviews(self, app_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent player reviews from Steam Web API."""
        clean_id = re.sub(r"[^\d]", "", str(app_id))
        if not clean_id:
            return []

        url = f"https://store.steampowered.com/appreviews/{clean_id}?json=1&language=all&num_per_page={limit}&purchase_type=all"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        reviews = []
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for r in data.get("reviews", []):
                    voted_up = r.get("voted_up", True)
                    rating = 5 if voted_up else 1
                    content = r.get("review", "")
                    author = r.get("author", {}).get("steamid", "Player")
                    
                    reviews.append({
                        "rating": rating,
                        "title": "Positive Review" if voted_up else "Negative Review",
                        "content": content,
                        "author": author,
                        "version": "Steam Live",
                        "source": "Steam",
                        "sentiment": "positive" if voted_up else "negative"
                    })
        except Exception as e:
            logger.debug(f"Failed to fetch Steam reviews for {clean_id}: {e}")

        return reviews

    def fetch_google_play_reviews(self, package_id: str, country: str = "us", limit: int = 100) -> List[Dict[str, Any]]:
        """Fetches recent reviews from Google Play (package id like com.example.game)."""
        if not package_id or "." not in package_id:
            return []
        try:
            from google_play_scraper import reviews as gp_reviews, Sort
            lang = "vi" if country == "vn" else "en"
            items, _ = gp_reviews(package_id, lang=lang, country=country, sort=Sort.NEWEST, count=limit)
        except Exception as e:
            logger.debug(f"Failed to fetch Google Play reviews for {package_id}: {e}")
            return []
        out = []
        for r in items:
            rating = int(r.get("score") or 3)
            out.append({
                "rating": rating,
                "title": "",
                "content": r.get("content") or "",
                "author": r.get("userName") or "Google Play user",
                "version": r.get("reviewCreatedVersion") or "",
                "source": "Google Play",
                "sentiment": "positive" if rating >= 4 else ("negative" if rating <= 2 else "neutral"),
            })
        return out

    def _fetch_for(self, game_id: str, platform: str) -> Dict[str, Any]:
        """Picks the right store from the game_id prefix (ios_ / gp_ / Steam app id)."""
        gid = str(game_id)
        attempts = []
        if gid.startswith("gp_") or "googleplay" in (platform or "").lower():
            pkg = gid[3:] if gid.startswith("gp_") else gid
            for country in ("us", "vn"):
                attempts.append(f"Google Play ({country})")
                reviews = self.fetch_google_play_reviews(pkg, country=country)
                if reviews:
                    return {"reviews": reviews, "source": f"Google Play ({country})"}
        elif (platform or "").lower() in ("steam", "pc", "pc_steam") or gid.isdigit() and not gid.startswith("ios_"):
            attempts.append("Steam")
            reviews = self.fetch_steam_reviews(gid)
            if reviews:
                return {"reviews": reviews, "source": "Steam"}
        else:
            for country in ("us", "vn"):
                attempts.append(f"App Store ({country})")
                reviews = self.fetch_apple_reviews(gid, country=country)
                if reviews:
                    return {"reviews": reviews, "source": f"App Store ({country})"}
        return {"reviews": [], "source": None, "attempted": attempts}

    def analyze_reviews(self, game_id: str, game_title: str = "", platform: str = "mobile",
                        custom_reviews: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Sentiment & churn analysis computed only from real reviews.

        If no review could be fetched, returns status "no_reviews" with empty results —
        never invented sample reviews.
        """
        source = "custom"
        attempted: List[str] = []
        reviews = custom_reviews or []
        if not reviews:
            fetched = self._fetch_for(game_id, platform)
            reviews, source, attempted = fetched["reviews"], fetched["source"], fetched.get("attempted", [])

        base = {"game_id": game_id, "game_title": game_title, "review_source": source}
        if not reviews:
            return {
                **base,
                "status": "no_reviews",
                "message": "Không lấy được đánh giá nào từ store (" + (", ".join(attempted) or "không xác định được store") +
                           "). Store có thể chặn tạm thời hoặc game chưa có đánh giá.",
                "total_reviews_analyzed": 0,
                "average_rating": None,
                "sentiment": {"positive_percentage": 0, "neutral_percentage": 0, "negative_percentage": 0,
                              "positive_count": 0, "neutral_count": 0, "negative_count": 0},
                "churn_drivers": [],
                "retention_hooks": [],
                "studio_attack_playbook": None,
                "sample_reviews": [],
            }

        total = len(reviews)
        pos = [r for r in reviews if r.get("rating", 3) >= 4]
        neu = [r for r in reviews if r.get("rating", 3) == 3]
        neg = [r for r in reviews if r.get("rating", 3) <= 2]
        pct = lambda n: round(n / total * 100, 1)

        churn_drivers = self._match_categories(neg, CHURN_CATEGORIES)
        retention_hooks = self._match_categories(pos, RETENTION_CATEGORIES)

        return {
            **base,
            "status": "ok",
            "total_reviews_analyzed": total,
            "average_rating": round(sum(r.get("rating", 3) for r in reviews) / total, 2),
            "sentiment": {
                "positive_percentage": pct(len(pos)),
                "neutral_percentage": pct(len(neu)),
                "negative_percentage": pct(len(neg)),
                "positive_count": len(pos),
                "neutral_count": len(neu),
                "negative_count": len(neg),
            },
            "churn_drivers": churn_drivers,
            "retention_hooks": retention_hooks,
            "studio_attack_playbook": self._generate_attack_playbook(churn_drivers, game_title),
            "sample_reviews": (neg[:6] + pos[:6])[:12],
        }

    @staticmethod
    def _match_categories(reviews: List[Dict[str, Any]], categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Counts how many of the given reviews mention each category's keywords.

        frequency_pct = share of these reviews (negative or positive) that mention the
        category; sample_quote is an excerpt of a real matching review.
        """
        if not reviews:
            return []
        texts = [(r, f"{r.get('title', '')} {r.get('content', '')}".lower()) for r in reviews]
        out = []
        for cat in categories:
            hits = [r for r, t in texts if any(k in t for k in cat["keywords"])]
            if not hits:
                continue
            freq = round(len(hits) / len(reviews) * 100, 1)
            quote_src = hits[0]
            quote = (quote_src.get("content") or quote_src.get("title") or "").strip()
            item = {
                "category": cat["label"],
                "mentions": len(hits),
                "frequency_pct": freq,
                "description": cat["description"],
                "sample_quote": quote[:220] + ("…" if len(quote) > 220 else ""),
            }
            if "advice" in cat:
                item["severity"] = "CRITICAL" if freq >= 40 else ("HIGH" if freq >= 20 else "MEDIUM")
                item["key"] = cat["key"]
            out.append(item)
        out.sort(key=lambda x: -x["mentions"])
        return out

    def _generate_attack_playbook(self, churn: List[Dict[str, Any]], game_title: str) -> Optional[Dict[str, Any]]:
        """Counter-strategy built only from complaint categories actually found in reviews."""
        if not churn:
            return None
        by_key = {c["key"]: c for c in CHURN_CATEGORIES}
        steps = [{"step": by_key[c["key"]]["advice"][0], "detail": by_key[c["key"]]["advice"][1],
                  "evidence": f"{c['mentions']} đánh giá tiêu cực ({c['frequency_pct']}%) nhắc tới"}
                 for c in churn[:3]]
        top = churn[0]
        return {
            "core_opportunity": f"Điểm yếu lớn nhất của {game_title or 'đối thủ'} theo đánh giá thật: "
                                f"{top['category']} ({top['frequency_pct']}% đánh giá tiêu cực nhắc tới).",
            "actionable_steps": steps,
            "marketing_hook": by_key[top["key"]]["hook"],
        }


# Keyword-based categories (English + Vietnamese, with and without diacritics)
CHURN_CATEGORIES: List[Dict[str, Any]] = [
    {
        "key": "tech",
        "label": "🐛 Lỗi Kỹ Thuật, Nóng Máy & Giật Lag",
        "keywords": ["crash", "bug", "lag", "freeze", "glitch", "battery", "overheat", "black screen", "loading",
                     "văng", "giật", "nóng máy", "đơ", "lỗi", "treo", "van game", "giat", "nong may", "loi game"],
        "description": "Người chơi phàn nàn về crash, giật lag, nóng máy hoặc lỗi.",
        "advice": ("Tối ưu hiệu năng cho máy cấu hình thấp",
                   "Giữ dung lượng nhỏ, 60 FPS ổn định trên máy RAM 3–4GB, test kỹ trước mỗi bản cập nhật."),
        "hook": "Mượt trên mọi máy, không nóng máy, không văng game.",
    },
    {
        "key": "p2w",
        "label": "💸 Gacha & Pay-to-Win",
        "keywords": ["p2w", "pay to win", "pay2win", "gacha", "rates", "drop rate", "greedy", "money", "expensive",
                     "nạp", "hút máu", "tỉ lệ", "tỷ lệ", "đắt", "nap tien", "hut mau", "ti le"],
        "description": "Người chơi cho rằng tỷ lệ gacha thấp, game ép nạp tiền hoặc người nạp áp đảo người không nạp.",
        "advice": ("Gacha thân thiện với người không nạp",
                   "Pity thấp và minh bạch, cho phép cày mảnh nhân vật qua hoạt động hằng ngày."),
        "hook": "Tỷ lệ minh bạch, cày chay vẫn mạnh.",
    },
    {
        "key": "ads",
        "label": "📺 Quảng Cáo Quá Dày",
        "keywords": [" ads", "ads ", "advert", "commercial", "too many ad", "quảng cáo", "quang cao"],
        "description": "Người chơi phàn nàn quảng cáo xuất hiện quá thường xuyên.",
        "advice": ("Chỉ dùng quảng cáo tự nguyện",
                   "Chuyển sang rewarded video, bỏ interstitial ép buộc, có gói IAP xóa quảng cáo."),
        "hook": "Không quảng cáo ép buộc.",
    },
    {
        "key": "difficulty",
        "label": "⚖️ Mất Cân Bằng & Kẹt Màn",
        "keywords": ["too hard", "impossible", "stuck", "unfair", "balance", "matchmaking", "nerf", "op ",
                     "kẹt", "khó quá", "vô lý", "mất cân bằng", "ket man", "kho qua"],
        "description": "Người chơi kẹt ở màn khó, phàn nàn cân bằng hoặc ghép trận không công bằng.",
        "advice": ("Đường cong độ khó mượt",
                   "Theo dõi tỷ lệ bỏ game theo màn, thêm cơ chế hỗ trợ thay vì ép mua vật phẩm."),
        "hook": "Thử thách công bằng, thắng bằng kỹ năng.",
    },
    {
        "key": "server",
        "label": "🌐 Server, Kết Nối & Tài Khoản",
        "keywords": ["server", "connection", "disconnect", "login", "account", "lost progress", "banned",
                     "mất kết nối", "đăng nhập", "tài khoản", "mất acc", "mat ket noi", "dang nhap"],
        "description": "Người chơi gặp lỗi kết nối, đăng nhập hoặc mất tài khoản/tiến trình.",
        "advice": ("Hạ tầng ổn định & bảo vệ tài khoản",
                   "Server khu vực gần người chơi, liên kết tài khoản và sao lưu tiến trình trên cloud."),
        "hook": "Kết nối ổn định, không lo mất tài khoản.",
    },
]

RETENTION_CATEGORIES: List[Dict[str, Any]] = [
    {"label": "🎨 Đồ Họa & Phong Cách Nghệ Thuật",
     "keywords": ["graphic", "beautiful", "art", "visual", "animation", "đồ họa", "đẹp", "do hoa", "hình ảnh"],
     "description": "Người chơi khen đồ họa, phong cách nghệ thuật hoặc hiệu ứng."},
    {"label": "🎮 Lối Chơi Cuốn Hút",
     "keywords": ["fun", "addictive", "gameplay", "addicting", "enjoy", "hay", "cuốn", "vui", "gây nghiện", "cuon"],
     "description": "Người chơi khen lối chơi vui, gây nghiện."},
    {"label": "🎁 Phần Thưởng & Sự Kiện",
     "keywords": ["reward", "free", "event", "generous", "gift", "quà", "sự kiện", "miễn phí", "qua tang", "su kien"],
     "description": "Người chơi khen phần thưởng, quà tặng hoặc sự kiện thường xuyên."},
    {"label": "📖 Cốt Truyện & Nhân Vật",
     "keywords": ["story", "character", "lore", "cốt truyện", "nhân vật", "cot truyen", "nhan vat"],
     "description": "Người chơi khen cốt truyện hoặc thiết kế nhân vật."},
    {"label": "👥 Cộng Đồng & Chơi Cùng Bạn",
     "keywords": ["friend", "guild", "clan", "multiplayer", "community", "bạn bè", "bang hội", "ban be", "cộng đồng"],
     "description": "Người chơi khen tính năng chơi cùng bạn bè, bang hội."},
]
