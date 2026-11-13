"""Mechanics Hybrid Lab - AI-Powered Game DNA Cross-Breeding & Prototype Generator.

Synthesizes new breakthrough game concepts by fusing the Core Gameplay Loop of Game A
with the Meta-Progression & Monetization DNA of Game B, producing full design specs,
GDD pitch, and executable 60FPS playable HTML5 Canvas prototypes.
"""

import os
import re
import json
import math
import random
import logging
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.database.db import get_db_connection

logger = logging.getLogger(__name__)


class MechanicsHybridLab:
    """Orchestrates mechanic fusion, game DNA synthesis, and prototype generation."""

    PRESET_COMBOS = [
        {
            "id": "vampire_candy",
            "name": "Vampire Matcher: Sweet Survivor",
            "game_a_name": "Vampire Survivors",
            "game_a_genre": "Roguelite / Bullet Hell",
            "game_b_name": "Candy Crush Saga",
            "game_b_genre": "Match-3 Puzzle",
            "fusion_ratio": "50_50",
            "art_style": "Pixel Art 2D Retro",
            "tagline": "Nối kẹo Match-3 để kích hoạt kỹ năng phép thuật hủy diệt hàng ngàn quái vật!",
            "synergy_pitch": "Mỗi combo Match-3 bên dưới màn hình sẽ nạp năng lượng mana và tung ra mưa đạn/kiếm phép tiêu diệt đàn quái vật đang áp sát nhân vật ở nửa trên màn hình."
        },
        {
            "id": "archero_tycoon",
            "name": "Dungeon Factory: Arrow & Assembly",
            "game_a_name": "Archero",
            "game_a_genre": "Action Roguelike",
            "game_b_name": "Idle Egg Factory",
            "game_b_genre": "Idle Tycoon / Automation",
            "fusion_ratio": "70_30",
            "art_style": "Cartoon Low-Poly 3D",
            "tagline": "Bắn quái trong hầm ngục để thu thập nguyên liệu vận hành nhà máy rèn vũ khí tự động!",
            "synergy_pitch": "Càng vượt ải hầm ngục sâu hơn, bạn càng mở khóa thêm các băng chuyền rèn thần khí tự động, sản xuất vũ khí xịn hơn để tiếp tục chinh phục boss khó hơn."
        },
        {
            "id": "flappy_souls",
            "name": "Flappy Knight: Dark Skies",
            "game_a_name": "Flappy Bird",
            "game_a_genre": "Physics Arcade",
            "game_b_name": "Dark Souls",
            "game_b_genre": "Action RPG / Boss Rush",
            "fusion_ratio": "50_50",
            "art_style": "Dark Fantasy Souls-like",
            "tagline": "Nhịp vỗ cánh né bẫy kết hợp căn parry đòn đánh sát thương tử thần của Boss!",
            "synergy_pitch": "Giữ nhịp bay bằng thao tác chạm đơn giản, nhưng mỗi khi bay qua ống khói sẽ có quái vật tung chiêu. Chạm đúng khoảnh khắc để phản đòn (Parry) và tung nhát chém chí mạng."
        },
        {
            "id": "balatro_ninja",
            "name": "Balatro Slice: Poker Slash",
            "game_a_name": "Balatro",
            "game_a_genre": "Roguelike Poker Deckbuilder",
            "game_b_name": "Fruit Ninja",
            "game_b_genre": "Fast-paced Action Arcade",
            "fusion_ratio": "50_50",
            "art_style": "Cyberpunk Neon",
            "tagline": "Chém bay các lá bài tây bay trên màn hình để xếp thành liên hoàn sảnh rồng Poker!",
            "synergy_pitch": "Các quân bài bay vọt lên không trung. Dùng ngón tay vuốt chém thật chuẩn xác để gom thành bài Đôi, Cù Lũ hoặc Thùng Phá Sảnh nhân hệ số điểm sát thương hủy diệt Boss."
        }
    ]

    def __init__(self):
        pass

    def get_preset_combos(self) -> List[Dict[str, Any]]:
        """Returns pre-engineered high-synergy mechanic fusion templates."""
        return self.PRESET_COMBOS

    def _get_game_info(self, game_id_or_title: str) -> Dict[str, Any]:
        """Fetches game details from snapshots table or creates standard representation."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, platform, genre, developer, icon_url, rank, price
            FROM snapshots
            WHERE game_id = ? OR title LIKE ?
            ORDER BY snapshot_date DESC
            LIMIT 1
        """, (game_id_or_title, f"%{game_id_or_title}%"))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)

        # Fallback metadata
        clean_title = game_id_or_title.replace("_", " ").title()
        return {
            "title": clean_title,
            "platform": "mobile_appstore",
            "genre": "Action / Casual",
            "developer": "Top Indie Studio",
            "icon_url": "https://placehold.co/80x80/6366f1/ffffff?text=GAME",
            "rank": 15,
            "price": "Free"
        }

    def fuse_mechanics(
        self,
        game_a_id: str,
        game_b_id: str,
        fusion_ratio: str = "50_50",
        art_style: str = "Pixel Art 2D Retro",
        monetization_model: str = "Hybrid-Casual (IAA + Battle Pass)"
    ) -> Dict[str, Any]:
        """Cross-breeds DNA of Game A and Game B into a breakthrough hybrid game concept."""
        game_a = self._get_game_info(game_a_id)
        game_b = self._get_game_info(game_b_id)

        title_a = game_a.get("title", "Game A")
        genre_a = game_a.get("genre", "Action")
        title_b = game_b.get("title", "Game B")
        genre_b = game_b.get("genre", "Puzzle")

        # Try Gemini LLM first if API key configured
        gemini_result = self._call_gemini_fusion(
            game_a, game_b, fusion_ratio, art_style, monetization_model
        )

        if gemini_result:
            # Attach canvas code and unity starter
            canvas_code = self._generate_hybrid_canvas_code(gemini_result, title_a, title_b)
            gemini_result["playable_canvas_code"] = canvas_code
            gemini_result["unity_starter_code"] = self._generate_unity_starter_code(gemini_result)
            return gemini_result

        # Procedural Deep Synthesis Fallback
        return self._procedural_hybrid_synthesis(
            game_a, game_b, fusion_ratio, art_style, monetization_model
        )

    def _call_gemini_fusion(
        self,
        game_a: Dict[str, Any],
        game_b: Dict[str, Any],
        fusion_ratio: str,
        art_style: str,
        monetization_model: str
    ) -> Optional[Dict[str, Any]]:
        """Invokes Gemini 3.5 Flash Lite to perform creative game design fusion."""
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            try:
                from app.config import GEMINI_API_KEY
                key = GEMINI_API_KEY
            except Exception:
                key = ""

        if not key:
            return None

        prompt = f"""
Bạn là Creative Director và Lead Game Designer hàng đầu thế giới chuyên về Hybrid-Casual và Indie Game Innovation.
Hãy lai ghép DNA của 2 tựa game sau thành một CONCEPT GAME HOÀN TOÀN MỚI, ĐỘT PHÁ VÀ GÂY NGHIỆN:

Game A (Chủ đạo Core Loop):
- Tên: {game_a.get('title')}
- Thể loại: {game_a.get('genre')}
- Nền tảng: {game_a.get('platform')}

Game B (Chủ đạo Meta-Progression & Hook):
- Tên: {game_b.get('title')}
- Thể loại: {game_b.get('genre')}

Tỉ lệ lai ghép: {fusion_ratio}
Phong cách đồ họa: {art_style}
Mô hình kiếm tiền: {monetization_model}

Hãy trả về DUY NHẤT một chuỗi JSON hợp lệ (không kèm markdown ```json hay text bên ngoài) với cấu trúc:
{{
  "concept_title": "Tên game lai ghép cực kêu và cuốn hút",
  "slogan": "Câu slogan đắt giá tóm tắt cơ chế",
  "high_concept_pitch": "1-2 câu pitch thuyết phục nhà phát hành (Publisher)",
  "target_audience": "Đối tượng người chơi mục tiêu và tâm lý học",
  "usp_market_gap": "Điểm độc nhất vô nhị (USP) giúp game thoát khỏi đại dương đỏ",
  "dna_fusion_matrix": {{
    "game_a_inherited": "Những cơ chế điều khiển, nhịp độ được thừa hưởng từ {game_a.get('title')}",
    "game_b_inherited": "Hệ thống nâng cấp, kinh tế, tiến trình lấy từ {game_b.get('title')}",
    "synergy_mechanic": "Cơ chế lai ghép mới nảy sinh khi 2 game va chạm vào nhau (Điểm đột phá)"
  }},
  "core_loop_steps": [
    {{"step": 1, "action": "Hành động đầu vào (Input & Core Action)", "desc": "Mô tả chi tiết"}},
    {{"step": 2, "action": "Phản hồi thử thách (Combat / Puzzle Resolution)", "desc": "Mô tả chi tiết"}},
    {{"step": 3, "action": "Thu hoạch & Tưởng thưởng (Reward Drops)", "desc": "Mô tả chi tiết"}},
    {{"step": 4, "action": "Nâng cấp Meta & Tái đầu tư (Progression & Loop restart)", "desc": "Mô tả chi tiết"}}
  ],
  "ftue_180s": {{
    "phase_1_hook": "0-30s: Cú huých ấn tượng giữ chân người chơi",
    "phase_2_first_win": "30-90s: Cảm giác chiến thắng đầu tiên dễ dàng",
    "phase_3_retention_lock": "90-180s: Mở khóa tính năng tiến trình buộc phải quay lại ngày mai"
  }},
  "monetization_strategy": {{
    "rewarded_video_placements": ["Vị trí 1", "Vị trí 2"],
    "interstitial_pacing": "Chiến lược hiện quảng cáo xen kẽ an toàn",
    "iap_high_value_packs": ["Gói IAP 1", "Gói IAP 2"],
    "battle_pass_concept": "Tên và cấu trúc Battle Pass"
  }},
  "prototype_design": {{
    "player_controls": "Cách điều khiển nhân vật",
    "win_condition": "Điều kiện qua màn",
    "fail_condition": "Điều kiện thua",
    "mechanic_summary": "Tóm tắt cơ chế chính để code"
  }}
}}
"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={key}"
            payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                cleaned = text.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```[a-z]*\n", "", cleaned)
                    cleaned = re.sub(r"\n```$", "", cleaned)
                data = json.loads(cleaned)
                data["source"] = "Gemini 3.5 Flash Lite"
                data["game_a"] = game_a
                data["game_b"] = game_b
                data["fusion_ratio"] = fusion_ratio
                data["art_style"] = art_style
                data["monetization_model"] = monetization_model
                return data
        except Exception as e:
            logger.warning(f"Gemini mechanic fusion call failed: {e}")
            return None

    def _procedural_hybrid_synthesis(
        self,
        game_a: Dict[str, Any],
        game_b: Dict[str, Any],
        fusion_ratio: str,
        art_style: str,
        monetization_model: str
    ) -> Dict[str, Any]:
        """Procedural fall-back synthesis engine when Gemini API is offline."""
        title_a = game_a.get("title", "Game A")
        title_b = game_b.get("title", "Game B")
        genre_a = game_a.get("genre", "Action")
        genre_b = game_b.get("genre", "Casual")

        prefix_words = ["Survivor", "Rogue", "Match", "Idle", "Dungeon", "Cyber", "Mega", "Pocket"]
        suffix_words = ["Fighter", "Tycoon", "Master", "Kingdom", "Clash", "Chronicles", "Rush", "Factory"]
        combo_title = f"{title_a.split()[0]} {title_b.split()[-1]}: {random.choice(prefix_words)} {random.choice(suffix_words)}"

        data = {
            "source": "Procedural Fusion Engine v2.0",
            "concept_title": combo_title,
            "slogan": f"Sự kết hợp bùng nổ giữa nhịp độ chiến đấu của {title_a} và cơ chế tiến trình gây nghiện của {title_b}!",
            "high_concept_pitch": f"{combo_title} giải quyết triệt để sự mệt mỏi của game {genre_a} truyền thống bằng cách tích hợp vòng lặp {genre_b} trực quan, tạo nên một trải nghiệm chơi vừa đã tay vừa có chiều sâu chiến thuật.",
            "target_audience": "Gen-Z & Millennial Mobile Gamers (18-35 tuổi), thích game có tiết tấu nhanh, điều khiển 1 ngón nhưng vẫn muốn xây dựng bộ sưu tập tiến trình lâu dài.",
            "usp_market_gap": f"Thị trường đang tràn ngập các bản sao chép {genre_a} đơn điệu. Bằng cách lồng ghép DNA của {title_b}, game tạo ra trải nghiệm chơi kép (Dual-layer Experience) độc nhất.",
            "dna_fusion_matrix": {
                "game_a_inherited": f"Cơ chế di chuyển né tránh linh hoạt, hệ thống vũ khí tự động kích hoạt và cảm giác giải tỏa căng thẳng (Power Fantasy) từ {title_a}.",
                "game_b_inherited": f"Hệ thống ghép nối tài nguyên, cây tiến trình công trình, và cơ chế tích lũy phần thưởng nhàn rỗi (Offline Progress) từ {title_b}.",
                "synergy_mechanic": f"Mỗi chuỗi combo thành công từ cơ chế của {title_b} sẽ trực tiếp nạp đạn đặc biệt (Ultimate Energy) cho nhân vật trong {title_a}, tạo nên nhịp điệu chơi bùng nổ."
            },
            "core_loop_steps": [
                {"step": 1, "action": "Khởi Đầu & Thao Tác Cơ Bản", "desc": f"Di chuyển nhân vật trong đấu trường, thu thập các viên năng lượng cơ bản xuất hiện ngẫu nhiên."},
                {"step": 2, "action": "Kích Hoạt Phản Ứng Lai Ghép", "desc": f"Khi năng lượng đầy, mở khóa giao diện kết hợp cơ chế {genre_b} để giải phóng chiêu thức hủy diệt diện rộng."},
                {"step": 3, "action": "Thu Thập Hòm Báu & Linh Hạch", "desc": "Tiêu diệt Boss nhỏ nhận được các mảnh nâng cấp vĩnh viễn và chìa khóa mở rương bí mật."},
                {"step": 4, "action": "Nâng Cấp Căn Cứ & Tái Đầu Tư", "desc": "Sử dụng tài nguyên vừa kiếm được để mở khóa vũ khí mới, tăng sát thương cơ bản và tiếp tục vòng lặp."}
            ],
            "ftue_180s": {
                "phase_1_hook": "0-30s: Cho người chơi cầm ngay vũ khí tối thượng quét sạch 50 quái vật đầu tiên để tạo cảm xúc thăng hoa tột đỉnh.",
                "phase_2_first_win": "30-90s: Hướng dẫn cơ chế lai ghép then chốt, người chơi hoàn thành 1 combo và hạ gục Mini-Boss đầu tiên.",
                "phase_3_retention_lock": "90-180s: Nhận trang bị phẩm chất Hiếm (Rare), mở khóa tính năng Điểm Danh 7 Ngày và gợi ý thử thách ngày 2."
            },
            "monetization_strategy": {
                "rewarded_video_placements": [
                    "Hồi sinh khẩn cấp (Revive) giữ nguyên chuỗi combo khi bị hạ gục",
                    "Nhân đôi (x2) phần thưởng vàng và linh hạch sau khi kết thúc trận đấu",
                    "Mở rương báu huyền thoại miễn phí mỗi 6 tiếng"
                ],
                "interstitial_pacing": "Chỉ kích hoạt sau khi hoàn thành ít nhất 2 màn chơi hoặc sau 90 giây nghỉ giữa các trận đấu (Không hiện giữa lúc đang thao tác).",
                "iap_high_value_packs": [
                    "Starter Pack $0.99: Gói Tân Thủ gồm 1 Vũ Khí Độc Quyền + 500 Kim Cương",
                    "Battle Pass Season $4.99: Chuỗi 50 cấp độ nhận Skin độc quyền và x1.5 tốc độ tích lũy tài nguyên"
                ],
                "battle_pass_concept": f"Hành Trình Thợ Săn: Mùa 1 - Thức Tỉnh Linh Hạch ({combo_title})"
            },
            "prototype_design": {
                "player_controls": "Điều khiển di chuyển bằng phím Mũi Tên / WASD hoặc Chuột / Chạm màn hình",
                "win_condition": "Sống sót qua 60 giây và tích lũy đủ 1,000 điểm",
                "fail_condition": "Hết máu (HP = 0) do va chạm quái vật",
                "mechanic_summary": f"Game sinh tồn kết hợp giải đố cơ chế lai ghép {genre_a} + {genre_b}"
            },
            "game_a": game_a,
            "game_b": game_b,
            "fusion_ratio": fusion_ratio,
            "art_style": art_style,
            "monetization_model": monetization_model
        }

        data["playable_canvas_code"] = self._generate_hybrid_canvas_code(data, title_a, title_b)
        data["unity_starter_code"] = self._generate_unity_starter_code(data)
        return data

    def _generate_hybrid_canvas_code(self, data: Dict[str, Any], title_a: str, title_b: str) -> str:
        """Generates self-contained 60FPS playable HTML5 Canvas JavaScript code for the fused game."""
        title = data.get("concept_title", "Hybrid Game").replace("'", "\\'")
        slogan = data.get("slogan", "AI Hybrid Gameplay").replace("'", "\\'")

        return f"""
// --- HYBRID GAME CANVAS ENGINE: {title} ---
(function() {{
  const canvas = document.getElementById('hybridPrototypeCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Game Dimensions
  const W = canvas.width = 640;
  const H = canvas.height = 420;

  // Game State
  let isRunning = true;
  let score = 0;
  let mana = 0;
  let maxMana = 100;
  let gameTime = 0;
  let wave = 1;
  let comboCount = 0;

  // Player Object
  const player = {{
    x: W / 2,
    y: H / 2,
    radius: 16,
    speed: 3.8,
    hp: 100,
    maxHp: 100,
    color: '#10b981',
    keys: {{}}
  }};

  // Collections
  let bullets = [];
  let enemies = [];
  let particles = [];
  let puzzleCores = [];
  let floatTexts = [];

  // Spawn Puzzle Nodes (DNA from Game B)
  function spawnPuzzleNodes() {{
    puzzleCores = [];
    const colors = ['#f43f5e', '#06b6d4', '#eab308', '#a855f7'];
    for (let i = 0; i < 5; i++) {{
      puzzleCores.push({{
        x: 60 + Math.random() * (W - 120),
        y: 60 + Math.random() * (H - 120),
        radius: 12,
        color: colors[i % colors.length],
        active: true,
        pulse: Math.random() * Math.PI
      }});
    }}
  }}
  spawnPuzzleNodes();

  // Input Listeners
  window.addEventListener('keydown', e => {{ player.keys[e.key.toLowerCase()] = true; }});
  window.addEventListener('keyup', e => {{ player.keys[e.key.toLowerCase()] = false; }});

  // Mouse / Touch Aiming
  let mousePos = {{ x: W / 2, y: H / 2 }};
  canvas.addEventListener('mousemove', e => {{
    const rect = canvas.getBoundingClientRect();
    mousePos.x = (e.clientX - rect.left) * (W / rect.width);
    mousePos.y = (e.clientY - rect.top) * (H / rect.height);
  }});

  // Auto-Fire Bullet Logic (Game A Bullet Hell)
  let lastShot = 0;
  function updateBullets(time) {{
    if (time - lastShot > 280) {{
      lastShot = time;
      // Shoot towards mouse or nearest enemy
      let targetX = mousePos.x;
      let targetY = mousePos.y;
      if (enemies.length > 0) {{
        targetX = enemies[0].x;
        targetY = enemies[0].y;
      }}
      const angle = Math.atan2(targetY - player.y, targetX - player.x);
      bullets.push({{
        x: player.x,
        y: player.y,
        vx: Math.cos(angle) * 7.5,
        vy: Math.sin(angle) * 7.5,
        radius: 4.5,
        damage: 25 + Math.floor(mana / 10),
        color: mana >= 80 ? '#f43f5e' : '#38bdf8'
      }});

      // Ultimate Combo Spread Shot
      if (mana >= 100) {{
        for (let offset of [-0.3, 0.3]) {{
          bullets.push({{
            x: player.x,
            y: player.y,
            vx: Math.cos(angle + offset) * 7.5,
            vy: Math.sin(angle + offset) * 7.5,
            radius: 5,
            damage: 35,
            color: '#a855f7'
          }});
        }}
      }}
    }}

    bullets.forEach((b, idx) => {{
      b.x += b.vx;
      b.y += b.vy;
      if (b.x < 0 || b.x > W || b.y < 0 || b.y > H) bullets.splice(idx, 1);
    }});
  }}

  // Spawn Enemy Horde
  let lastSpawn = 0;
  function updateEnemies(time) {{
    const spawnRate = Math.max(400, 1200 - wave * 90);
    if (time - lastSpawn > spawnRate) {{
      lastSpawn = time;
      const side = Math.floor(Math.random() * 4);
      let ex = 0, ey = 0;
      if (side === 0) {{ ex = Math.random() * W; ey = -20; }}
      else if (side === 1) {{ ex = W + 20; ey = Math.random() * H; }}
      else if (side === 2) {{ ex = Math.random() * W; ey = H + 20; }}
      else {{ ex = -20; ey = Math.random() * H; }}

      const isElite = Math.random() < 0.18;
      enemies.push({{
        x: ex,
        y: ey,
        radius: isElite ? 18 : 11,
        hp: isElite ? 90 : 30,
        maxHp: isElite ? 90 : 30,
        speed: isElite ? 1.2 : 2.1,
        color: isElite ? '#e11d48' : '#fb923c',
        isElite
      }});
    }}

    enemies.forEach((en, eIdx) => {{
      const angle = Math.atan2(player.y - en.y, player.x - en.x);
      en.x += Math.cos(angle) * en.speed;
      en.y += Math.sin(angle) * en.speed;

      // Hit Player
      const dist = Math.hypot(player.x - en.x, player.y - en.y);
      if (dist < player.radius + en.radius) {{
        player.hp -= en.isElite ? 0.6 : 0.25;
        if (player.hp <= 0) {{
          player.hp = 0;
          isRunning = false;
        }}
      }}

      // Bullet Collisions
      bullets.forEach((b, bIdx) => {{
        if (Math.hypot(b.x - en.x, b.y - en.y) < b.radius + en.radius) {{
          en.hp -= b.damage;
          bullets.splice(bIdx, 1);

          // Particles
          for (let p = 0; p < 4; p++) {{
            particles.push({{
              x: en.x, y: en.y,
              vx: (Math.random() - 0.5) * 5, vy: (Math.random() - 0.5) * 5,
              alpha: 1, color: en.color
            }});
          }}

          if (en.hp <= 0) {{
            score += en.isElite ? 250 : 50;
            enemies.splice(eIdx, 1);
            if (score > wave * 1000) wave++;
          }}
        }}
      }});
    }});
  }}

  // Player Touch Puzzle Node (Synergy Activation)
  function updatePuzzleNodes() {{
    puzzleCores.forEach((node, idx) => {{
      node.pulse += 0.05;
      const dist = Math.hypot(player.x - node.x, player.y - node.y);
      if (dist < player.radius + node.radius) {{
        // Collected Puzzle Core
        mana = Math.min(maxMana, mana + 25);
        comboCount++;
        score += 150 * comboCount;

        floatTexts.push({{
          x: node.x, y: node.y,
          text: `+MANA COMBO x${{comboCount}}!`,
          alpha: 1
        }});

        // Screen Shake / Particle explosion
        for (let p = 0; p < 12; p++) {{
          particles.push({{
            x: node.x, y: node.y,
            vx: Math.cos(p) * 6, vy: Math.sin(p) * 6,
            alpha: 1, color: node.color
          }});
        }}

        // Relocate
        node.x = 60 + Math.random() * (W - 120);
        node.y = 60 + Math.random() * (H - 120);
      }}
    }});
  }}

  // Game Loop
  function loop(time) {{
    if (!isRunning) {{
      renderGameOver();
      return;
    }}

    // Player Movement
    let dx = 0, dy = 0;
    if (player.keys['arrowup'] || player.keys['w']) dy -= 1;
    if (player.keys['arrowdown'] || player.keys['s']) dy += 1;
    if (player.keys['arrowleft'] || player.keys['a']) dx -= 1;
    if (player.keys['arrowright'] || player.keys['d']) dx += 1;

    if (dx !== 0 && dy !== 0) {{ dx *= 0.7071; dy *= 0.7071; }}
    player.x = Math.max(player.radius, Math.min(W - player.radius, player.x + dx * player.speed));
    player.y = Math.max(player.radius, Math.min(H - player.radius, player.y + dy * player.speed));

    updateBullets(time);
    updateEnemies(time);
    updatePuzzleNodes();

    // Render Stage
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, W, H);

    // Draw Grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 1;
    for (let x = 0; x < W; x += 32) {{ ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }}
    for (let y = 0; y < H; y += 32) {{ ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }}

    // Draw Puzzle Nodes (Game B DNA)
    puzzleCores.forEach(node => {{
      const scale = 1 + Math.sin(node.pulse) * 0.15;
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius * scale, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.shadowColor = node.color;
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;
    }});

    // Draw Bullets
    bullets.forEach(b => {{
      ctx.beginPath();
      ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
      ctx.fillStyle = b.color;
      ctx.fill();
    }});

    // Draw Enemies
    enemies.forEach(en => {{
      ctx.beginPath();
      ctx.arc(en.x, en.y, en.radius, 0, Math.PI * 2);
      ctx.fillStyle = en.color;
      ctx.fill();

      // HP bar
      ctx.fillStyle = 'rgba(0,0,0,0.5)';
      ctx.fillRect(en.x - 12, en.y - en.radius - 6, 24, 3);
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(en.x - 12, en.y - en.radius - 6, (en.hp / en.maxHp) * 24, 3);
    }});

    // Draw Player
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
    ctx.fillStyle = player.color;
    ctx.shadowColor = '#10b981';
    ctx.shadowBlur = 12;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Draw Particles
    particles.forEach((p, idx) => {{
      p.x += p.vx;
      p.y += p.vy;
      p.alpha -= 0.03;
      if (p.alpha <= 0) particles.splice(idx, 1);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = Math.max(0, p.alpha);
      ctx.fillRect(p.x, p.y, 3, 3);
      ctx.globalAlpha = 1;
    }});

    // Float Texts
    floatTexts.forEach((ft, idx) => {{
      ft.y -= 1;
      ft.alpha -= 0.02;
      if (ft.alpha <= 0) floatTexts.splice(idx, 1);
      ctx.font = 'bold 12px Inter, sans-serif';
      ctx.fillStyle = `rgba(234, 179, 8, ${{Math.max(0, ft.alpha)}})`;
      ctx.fillText(ft.text, ft.x - 30, ft.y);
    }});

    // HUD Display
    renderHUD();

    requestAnimationFrame(loop);
  }}

  function renderHUD() {{
    // Top Bar Background
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    ctx.fillRect(10, 10, W - 20, 36);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.strokeRect(10, 10, W - 20, 36);

    // HP Bar
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(20, 20, (player.hp / player.maxHp) * 110, 16);
    ctx.strokeStyle = '#fff';
    ctx.strokeRect(20, 20, 110, 16);
    ctx.font = '10px Inter, sans-serif';
    ctx.fillStyle = '#fff';
    ctx.fillText(`HP: ${{Math.ceil(player.hp)}}/${{player.maxHp}}`, 45, 32);

    // Mana Bar (Game B Synergy)
    ctx.fillStyle = '#38bdf8';
    ctx.fillRect(140, 20, (mana / maxMana) * 110, 16);
    ctx.strokeStyle = '#fff';
    ctx.strokeRect(140, 20, 110, 16);
    ctx.fillStyle = '#fff';
    ctx.fillText(`MANA COMBO: ${{Math.floor(mana)}}%`, 150, 32);

    // Score & Wave
    ctx.font = 'bold 12px Inter, sans-serif';
    ctx.fillStyle = '#e2e8f0';
    ctx.fillText(`ĐIỂM: ${{score.toLocaleString()}}`, 270, 32);
    ctx.fillStyle = '#a855f7';
    ctx.fillText(`WAVE: ${{wave}}`, 430, 32);
  }}

  function renderGameOver() {{
    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
    ctx.fillRect(0, 0, W, H);
    ctx.font = 'bold 26px Inter, sans-serif';
    ctx.fillStyle = '#ef4444';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', W / 2, H / 2 - 20);
    ctx.font = '14px Inter, sans-serif';
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText(`Tổng điểm sinh tồn: ${{score.toLocaleString()}} | Wave ${{wave}}`, W / 2, H / 2 + 10);
    ctx.fillStyle = '#10b981';
    ctx.fillText('Bấm nút "Chơi Lại" bên dưới để thử lại!', W / 2, H / 2 + 40);
    ctx.textAlign = 'start';
  }}

  // Global window controls
  window.restartHybridPrototype = function() {{
    player.x = W / 2;
    player.y = H / 2;
    player.hp = player.maxHp;
    score = 0;
    mana = 0;
    wave = 1;
    comboCount = 0;
    enemies = [];
    bullets = [];
    particles = [];
    isRunning = true;
    requestAnimationFrame(loop);
  }};

  requestAnimationFrame(loop);
}})();
"""

    def _generate_unity_starter_code(self, data: Dict[str, Any]) -> str:
        """Generates a starter C# Unity Monobehaviour script representing the hybrid mechanic."""
        title = data.get("concept_title", "HybridGamePrototype").replace(" ", "").replace(":", "")
        clean_title = re.sub(r"[^a-zA-Z0-9_]", "", title)

        return f"""using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// {clean_title} - Unity Prototype Controller
/// Fused by Game Trending Radar AI Mechanics Hybrid Lab
/// Slogan: {data.get('slogan', '')}
/// </summary>
public class {clean_title}Controller : MonoBehaviour
{{
    [Header("Core Movement (Game A)")]
    public float moveSpeed = 5.0f;
    private Rigidbody2D rb;
    private Vector2 moveInput;

    [Header("Hybrid Synergy (Game B)")]
    public float currentMana = 0f;
    public float maxMana = 100f;
    public int comboCount = 0;

    [Header("Weapon & Auto-Fire")]
    public GameObject bulletPrefab;
    public Transform firePoint;
    public float fireRate = 0.3f;
    private float nextFireTime = 0f;

    void Start()
    {{
        rb = GetComponent<Rigidbody2D>();
        Debug.Log("🚀 [{clean_title}] Initialized successfully with Hybrid DNA!");
    }}

    void Update()
    {{
        // Input Movement
        moveInput.x = Input.GetAxisRaw("Horizontal");
        moveInput.y = Input.GetAxisRaw("Vertical");

        // Auto Attack towards nearest enemy
        if (Time.time >= nextFireTime)
        {{
            AutoFireWeapon();
            nextFireTime = Time.time + fireRate;
        }}
    }}

    void FixedUpdate()
    {{
        if (rb != null)
        {{
            rb.velocity = moveInput.normalized * moveSpeed;
        }}
    }}

    void AutoFireWeapon()
    {{
        // Auto-aiming logic here
        // If currentMana >= 100, trigger Screen-clearing Ultimate Synergy
    }}

    public void CollectPuzzleCore(float manaGain)
    {{
        currentMana = Mathf.Min(maxMana, currentMana + manaGain);
        comboCount++;
        Debug.Log($"💎 Synergy Core Collected! Combo x{{comboCount}}, Mana: {{currentMana}}%");
    }}
}}
"""
