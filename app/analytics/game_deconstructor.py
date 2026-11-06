"""Gameplay Deconstructor & Clone Blueprint Engine.

Performs deep reverse engineering of game mechanics, minute-by-minute level pacing,
narrative/quest scripts, reward economy, and generates complete C# Unity/Godot starter scripts
and asset production checklists to allow a studio to clone or build an upgraded version of any game.
"""

from typing import Dict, Any, List, Optional
import json

class GameDeconstructor:
    """Reverse-engineering engine that deconstructs any game into a reproduction blueprint."""

    PRESET_DECONSTRUCTIONS = [
        {
            "id": "vampire_survivors",
            "title": "Vampire Survivors / Survivor.io",
            "genre": "Action Roguelike / Bullet Heaven",
            "platform": "PC Steam & Mobile",
            "camera_perspective": "Top-Down 2D Orthographic, Camera follows player smoothly (Lerp)",
            "control_scheme": "Single Virtual Joystick (Mobile) / WASD or Arrow Keys (PC). No attack button - all weapons fire automatically on cooldown.",
            "physics_and_movement": {
                "movement_speed": "Standard 5.0 units/sec, affected by Speed passive item (+10% per level).",
                "collision_type": "Circle collider on player (radius 0.35m), Box/Circle on enemies. Soft pushing physics between enemies to prevent stacking into 1 point.",
                "hitbox_rules": "Generous player hurtbox, invulnerability frame (i-frame) of 0.15s upon taking damage."
            },
            "core_state_machine": [
                {"state": "SPAWN_WAVE", "trigger": "Mỗi 15 giây hoặc khi số lượng quái trên màn hình < 50", "action": "Sinh quái vật từ rìa ngoài màn hình (ngoài tầm nhìn camera 1.2x)."},
                {"state": "AUTO_TARGET_ATTACK", "trigger": "Vũ khí hết thời gian hồi chiêu (Cooldown tick)", "action": "Tự động nhắm vào quái gần nhất (Whip/Magic Wand) hoặc bắn ngẫu nhiên theo bán kính (Garlic/Bible)."},
                {"state": "GEM_DROP_VACUUM", "trigger": "Quái chết", "action": "Rớt ngọc kinh nghiệm màu Xanh/Xanh lá/Đỏ. Khi người chơi bước vào bán kính Pick-Up, ngọc bay Lerp tăng tốc về người chơi."},
                {"state": "LEVEL_UP_PAUSE", "trigger": "Thanh Exp đầy", "action": "Dừng thời gian toàn game (Time.timeScale = 0), mở pop-up chọn 1 trong 3 nâng cấp kỹ năng."}
            ],
            "pacing_script": [
                {"timestamp": "00:00 - 01:00", "wave_name": "Wave 1: Fodder Dơi/Dơi nhỏ", "density": "10-20 quái/s", "difficulty": "Rất Dễ", "objective": "Dạy cơ chế nhặt ngọc và nâng cấp vũ khí đầu tiên."},
                {"timestamp": "01:00 - 03:00", "wave_name": "Wave 2: Bộ xương chậm nhưng máu dày", "density": "30-50 quái/s", "difficulty": "Trung Bình", "objective": "Ép người chơi phải chọn vũ khí diện rộng (AoE)."},
                {"timestamp": "03:00 - 05:00", "wave_name": "Wave 3: Đàn đực tốc độ cao (Wall of Bats)", "density": "80 quái bủa vây", "difficulty": "Khó (Chokepoint)", "objective": "Sát hạch DPS. Người chơi thiếu combo sát thương sẽ chết tại đây."},
                {"timestamp": "05:00", "wave_name": "BOSS 1: Quỷ Khổng Lồ Ma Cà Rồng", "density": "1 Boss + 30 quái phụ", "difficulty": "Boss Fight", "objective": "Tiêu diệt Boss rớt Rương Kho Báu Hoàng Kim (Chest 1-3-5 vật phẩm)."}
            ],
            "narrative_and_quest_script": {
                "premise": "Lời nguyền bóng đêm bao trùm vương quốc. Các anh hùng thức tỉnh trong nghĩa trang vô tận chống lại hàng triệu quái vật để giải cứu linh hồn.",
                "tutorial_dialogue": "Người dẫn đường: 'Đừng dừng chân! Chúng ở khắp mọi nơi! Hãy di chuyển và nhặt những viên ngọc ma thuật để tiến hóa sức mạnh!'",
                "gameplay_audio_cues": "Âm thanh lách cách vui tai khi ngọc bay liên hồi vào người; chuông thánh ca vang lên khi chọn nâng cấp; tiếng sấm nổ khi tiến hóa vũ khí Thần Thoại."
            },
            "unity_starter_code": """// CharacterController2D.cs - Vampire Survivors Movement & Auto-Attack
using UnityEngine;
using System.Collections.Generic;

public class SurvivorController : MonoBehaviour {
    [Header("Movement")]
    public float moveSpeed = 5.0f;
    public Rigidbody2D rb;
    private Vector2 inputDirection;

    [Header("Auto Weapon System")]
    public float attackCooldown = 1.0f;
    private float timer = 0f;
    public GameObject projectilePrefab;
    public float weaponRange = 8f;

    void Update() {
        // Simple 8-directional input
        inputDirection = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical")).normalized;

        // Auto Attack Timer
        timer += Time.deltaTime;
        if (timer >= attackCooldown) {
            FireAutoWeapon();
            timer = 0f;
        }
    }

    void FixedUpdate() {
        rb.velocity = inputDirection * moveSpeed;
    }

    void FireAutoWeapon() {
        Collider2D[] hitEnemies = Physics2D.OverlapCircleAll(transform.position, weaponRange, LayerMask.GetMask("Enemy"));
        if (hitEnemies.Length > 0) {
            // Find closest enemy
            Collider2D closest = hitEnemies[0];
            Vector2 dir = (closest.transform.position - transform.position).normalized;
            GameObject proj = Instantiate(projectilePrefab, transform.position, Quaternion.identity);
            proj.GetComponent<Rigidbody2D>().velocity = dir * 12f;
        }
    }
}""",
            "asset_checklist": {
                "sprites": ["Nhân vật chính 4 hướng di chuyển (Walk cycle 4 frames)", "15 loại quái vật phân cấp (Dơi, Skeleton, Zombie, Ghost, Minotaur)", "30 Icons kỹ năng và vũ khí", "3 loại ngọc kinh nghiệm (Xanh, Lục, Đỏ)"],
                "ui_canvas": ["Thanh máu HP Bar (Thanh trượt trên đầu)", "Thanh Exp Bar toàn màn hình ở mép trên", "Bảng chọn 3 kỹ năng Level-Up", "Bảng thống kê DPS cuối trận (End Game Stats)"],
                "sfx_list": ["SFX Gem Pickup (pitched random 0.9 - 1.2)", "SFX Weapon Fire (Whip crack, Magic chime)", "SFX Enemy Death squish", "SFX Level Up Fanfare"]
            },
            "clone_with_a_twist": [
                {"idea": "Chuyển Theme sang Tiên Hiệp Tu Tiên (Cultivation/Xianxia)", "why": "Cực hot tại thị trường Việt Nam & SEA. Ngọc exp thành 'Linh Thạch', vũ khí thành 'Ngự Kiếm Thuật', qua ải phi thăng thành Tiên."},
                {"idea": "Bổ sung cơ chế Thú Cưng Đánh Hỗ Trợ (Pet Synergy)", "why": "Mở rộng hệ thống IAP và Gacha pet, cho phép 2 người chơi co-op đánh boss đôi."},
                {"idea": "Địa hình tương tác phá hủy (Destructible Terrain)", "why": "Bắn nổ đá giải phóng dung nham quét sạch quái, tạo cảm giác giải đố chiến thuật hơn."}
            ]
        },
        {
            "id": "whiteout_survival",
            "title": "Whiteout Survival / Last Fortress",
            "genre": "Hybrid 4X Strategy / City Survival",
            "platform": "Mobile (iOS & Android)",
            "camera_perspective": "Isometric 3D Cố Định trong căn cứ (Base Building) / 2D Vertical Split-Screen khi chiến đấu vượt ải.",
            "control_scheme": "Touch / Tap một chạm: Bấm nhà để nâng cấp lò sưởi, kéo thả công nhân vào lò bánh mì, chạm xả skill tướng khi nộ đầy.",
            "physics_and_movement": {
                "movement_speed": "Nhân vật dân làng di chuyển từ tốn theo NavMesh 3D, ưu tiên sưởi ấm khi nhiệt độ xuống âm 30 độ.",
                "collision_type": "NavMesh Agent obstacle pathfinding, không va chạm phức tạp.",
                "hitbox_rules": "Chiến đấu turn-based theo thời gian thực (ATB / Auto-battle with energy bar)."
            },
            "core_state_machine": [
                {"state": "FROST_FURNACE_DRAIN", "trigger": "Mỗi giây trôi qua", "action": "Lò sưởi tiêu thụ Than đá (Coal). Nếu hết than đá, nhiệt độ giảm -> dân làng bị ốm/chết -> năng suất lao động về 0."},
                {"state": "WORKER_DISPATCH", "trigger": "Người chơi phân bổ dân vào nhà đẵn gỗ/săn bắn", "action": "Tự động tích lũy tài nguyên theo giờ (Hourly Idle Production)."},
                {"state": "BLIZZARD_ALERT", "trigger": "Đếm ngược chu kỳ 48 giờ", "action": "Cơn bão tuyết ập đến, đòi hỏi nâng cấp Lò Sưởi lên Cấp 10 nếu không toàn bộ căn cứ đóng băng."},
                {"state": "RALLY_HERO_EXPEDITION", "trigger": "Bấm đi thám hiểm ngoài bản đồ", "action": "Đội hình 5 tướng xuất trận, tự động đánh creep thu thập rương vàng và than đá."}
            ],
            "pacing_script": [
                {"timestamp": "0-10 phút", "wave_name": "Tutorial Cứu Sống Căn Cứ", "density": "3 Dân làng", "difficulty": "Rất Dễ", "objective": "Nhóm lửa lò sưởi trung tâm, dựng túp lều đầu tiên và chữa cảm lạnh cho đứa trẻ."},
                {"timestamp": "10-30 phút", "wave_name": "Gặp Gỡ Thú Dữ & Mở Khóa Tướng Đầu", "density": "Đàn sói Bắc Cực", "difficulty": "Dễ", "objective": "Tặng tướng tím miễn phí (Marksman), hướng dẫn cơ chế nộ chiêu thức."},
                {"timestamp": "Ngày 1 - Ngày 2", "wave_name": "Sát Hạch Bão Tuyết Lần 1", "density": "Nhiệt độ -40°C", "difficulty": "Chokepoint (Ép nạp)", "objective": "Yêu cầu Lò sưởi Lv.7. Nếu thiếu than đá sẽ xuất hiện gói cứu trợ khẩn cấp $0.99."},
                {"timestamp": "Ngày 3+", "wave_name": "Gia Nhập Liên Minh & Chiến Tranh Lãnh Địa", "density": "Bản đồ 10,000 ô", "difficulty": "Xã hội / PvP", "objective": "Mở rộng lãnh thổ liên minh, chuẩn bị chiếm Lâu Đài Mặt Trời."}
            ],
            "narrative_and_quest_script": {
                "premise": "Thời kỳ băng hà đột ngột ập đến, chôn vùi nền văn minh hiện đại. Bạn là Thị Trưởng dẫn dắt những người sống sót cuối cùng xây dựng lò sưởi ấm áp giữa bão tuyết.",
                "tutorial_dialogue": "Dân làng run rẩy: 'Thị trưởng! Than đá sắp cạn rồi, ngoài kia gió lạnh thấu xương! Chúng ta phải khởi động lại lò sưởi ngay lập tức!'",
                "gameplay_audio_cues": "Tiếng gió tuyết rít gào buốt giá; tiếng củi than nổ lách tách ấm áp khi nâng cấp lò; còi báo động khẩn cấp hú vang khi bão tuyết đổ bộ."
            },
            "unity_starter_code": """// FurnaceManager.cs - Core Temperature & Resource Drain System
using UnityEngine;
using System;

public class FurnaceManager : MonoBehaviour {
    [Header("Furnace Stats")]
    public int furnaceLevel = 1;
    public float currentCoal = 100f;
    public float coalDrainRate = 1.5f; // Coal per second
    public float baseTemperature = -25f; // Outside temp

    public event Action OnFurnaceExtinguished;

    void Update() {
        if (currentCoal > 0) {
            currentCoal -= coalDrainRate * Time.deltaTime;
            if (currentCoal <= 0) {
                currentCoal = 0;
                ExtinguishFurnace();
            }
        }
    }

    public void AddCoal(float amount) {
        currentCoal += amount;
    }

    public void UpgradeFurnace() {
        furnaceLevel++;
        coalDrainRate *= 1.25f; // Higher levels require more fuel
        Debug.Log($"Lò sưởi nâng lên cấp {furnaceLevel}! Bán kính sưởi ấm mở rộng.");
    }

    private void ExtinguishFurnace() {
        Debug.LogWarning("NGUY HIỂM: Lò sưởi đã tắt! Dân làng bắt đầu đóng băng!");
        OnFurnaceExtinguished?.Invoke();
    }
}""",
            "asset_checklist": {
                "sprites": ["Mô hình 3D Lò Sưởi Trung Tâm 10 cấp độ nâng cấp", "Nhà Đốn Gỗ, Bếp Ăn, Trạm Y Tế, Doanh Trại", "Chân dung 2D 10 Tướng Chiến Binh (Bảo an, Bác sĩ, Thợ săn)", "Hiệu ứng tuyết phủ động trên mái nhà"],
                "ui_canvas": ["Đồng hồ nhiệt kế lớn hiển thị độ âm (°C)", "Thanh hiển thị trữ lượng Than Đá / Gỗ / Thịt", "Cửa sổ quản lý phân bổ công nhân (Worker Roster)", "Pop-up gói cứu trợ Bão Tuyết Flash Sale $0.99"],
                "sfx_list": ["SFX Gió Bão Tuyết (Wind Howl Loop)", "SFX Lửa Lò Sưởi Bùng Cháy (Warm Fire Crackle)", "SFX Tiếng Búa Rèn Xây Nhà", "SFX Còi Hú Báo Động (Air Raid Siren)"]
            },
            "clone_with_a_twist": [
                {"idea": "Đổi Theme sang 'Hạn Hán Sa Mạc / Sa Mạc Tử Thần' (Oasis Survival)", "why": "Thay vì lạnh âm độ thì là nắng nóng 55°C, Lò sưởi thay bằng 'Giếng Nước Ngầm Thần Thánh'. Độc lạ, chưa có đối thủ thống trị phân khúc này."},
                {"idea": "Tích hợp Mini-game Tower Defense khi quái thú đột kích", "why": "Tạo gameplay quảng cáo chân thực không treo đầu dê bán thịt chó, tăng đột biến CVR và giảm CPI quảng cáo."},
                {"idea": "Cơ chế Đổi Phe / Ngoại Giao Gián Điệp trong Bang Hội", "why": "Tăng kịch tính cho các Whales đua tranh quyền lực lãnh thổ."}
            ]
        },
        {
            "id": "gossip_harbor",
            "title": "Gossip Harbor / Merge Mansion",
            "genre": "Casual Merge-2 / Mystery Renovation",
            "platform": "Mobile (iOS & Android)",
            "camera_perspective": "2D Giao diện màn hình dọc cố định: Nửa trên là Nhà Hàng/Dinh Thự 2D Isometric, nửa dưới là Bàn cờ Ghép Đồ 7x9 ô.",
            "control_scheme": "Chạm vào máy phát vật phẩm (Item Generator) để tạo ra bánh mì/cà phê Cấp 1, sau đó Kéo & Thả hai vật phẩm cùng cấp đè lên nhau để nâng cấp.",
            "physics_and_movement": {
                "movement_speed": "Kéo thả vật phẩm snapping mượt mà vào từng ô lưới 7x9.",
                "collision_type": "Ô lưới Grid cell detection, tự động nảy lại vị trí cũ nếu kéo vào ô không hợp lệ.",
                "hitbox_rules": "Không có combat."
            },
            "core_state_machine": [
                {"state": "TAP_GENERATOR", "trigger": "Chạm vào Hộp Dụng Cụ / Máy Pha Cà Phê", "action": "Tiêu tốn 1 Thể Lực (Energy), sinh ra 1 vật phẩm Lv.1 vào ô trống gần nhất."},
                {"state": "MERGE_UPGRADE", "trigger": "Kéo đè 2 vật phẩm Lv.X giống nhau", "action": "Ghép thành 1 vật phẩm Lv.X+1 kèm âm thanh nảy giọt nước (Popping) và tia sáng lung linh."},
                {"state": "ORDER_FULFILL", "trigger": "Vật phẩm trên bàn cờ khớp với yêu cầu của Khách Hàng", "action": "Nút 'Giao Hàng' sáng lên. Khách trả Vàng và Tiền Sao để sửa chữa cốt truyện."},
                {"state": "STORY_UNLOCK_CUTSCENE", "trigger": "Dùng Sao để sửa xong 1 hạng mục", "action": "Phát hoạt họa hội thoại kịch tính (Ai đã đốt cháy nhà hàng của Quinn?!)."}
            ],
            "pacing_script": [
                {"timestamp": "Level 1 - 3", "wave_name": "Khởi Đầu Mới Của Quinn", "density": "Đơn hàng Cấp 1 - 3 (Bánh ngọt, Cà phê đen)", "difficulty": "Cực Dễ", "objective": "Dạy thao tác kéo ghép và thưởng 100 năng lượng dồi dào."},
                {"timestamp": "Level 4 - 8", "wave_name": "Gặp Lại Người Yêu Cũ & Kẻ Tình Nghi Số 1", "density": "Đơn hàng Cấp 5 - 6", "difficulty": "Trung Bình", "objective": "Lần đầu tiên cạn thể lực. Dạy cách xem Rewarded Ads nhận 25 thể lực."},
                {"timestamp": "Level 10+", "wave_name": "Bí Ẩn Vụ Cháy & Thử Thách Bàn Cờ Đầy Chỗ", "density": "Đơn hàng Cấp 9 - 10 (Bánh Kem 3 Tầng)", "difficulty": "Chokepoint Bàn Cờ", "objective": "Bàn cờ bị lấp đầy rác và rương khóa. Bán slot ô lưu trữ phụ (Inventory Bag) với giá 50 Kim Cương."}
            ],
            "narrative_and_quest_script": {
                "premise": "Quinn ly hôn người chồng tệ bạc và quay về tiếp quản tiệm bánh ven biển của gia đình, nhưng phát hiện tiệm bánh vừa bị kẻ xấu phóng hỏa thiêu rụi.",
                "tutorial_dialogue": "Quinn: 'Mọi thứ bị thiêu rụi rồi... Nhưng mình không được bỏ cuộc! Hãy dọn dẹp đống tro tàn này và bắt đầu nướng những mẻ bánh đầu tiên nào!'",
                "gameplay_audio_cues": "Tiếng 'Pop' bong bóng vui nhộn khi ghép 2 món đồ; tiếng xào xạc quét sơn khi trang trí nội thất; nhạc nền Jazz Acoustic thư giãn phong cách biển mùa hè."
            },
            "unity_starter_code": """// MergeGridController.cs - Core Merge-2 Drag & Drop Logic
using UnityEngine;

public class MergeItem : MonoBehaviour {
    public int itemLevel = 1;
    public string itemCategory = "Sandwich"; // Coffee, Sandwich, Tool
    private Vector3 originalPosition;

    void OnMouseDown() {
        originalPosition = transform.position;
    }

    void OnMouseDrag() {
        Vector3 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
        mouseWorldPos.z = 0;
        transform.position = mouseWorldPos;
    }

    void OnMouseUp() {
        Collider2D target = Physics2D.OverlapPoint(transform.position);
        if (target != null && target.gameObject != this.gameObject) {
            MergeItem otherItem = target.GetComponent<MergeItem>();
            if (otherItem != null && otherItem.itemCategory == this.itemCategory && otherItem.itemLevel == this.itemLevel) {
                // Success Merge!
                otherItem.UpgradeLevel();
                Destroy(this.gameObject);
                return;
            }
        }
        // Return back if invalid merge
        transform.position = originalPosition;
    }

    public void UpgradeLevel() {
        itemLevel++;
        Debug.Log($"Hợp thể thành công món {itemCategory} lên cấp {itemLevel}!");
        // Update Sprite & play Pop VFX here
    }
}""",
            "asset_checklist": {
                "sprites": ["Bàn cờ 7x9 ô gỗ pastel", "Chuỗi 12 cấp độ Bánh Ngọt (Bột mì -> Bánh quy -> Bánh sừng bò -> Bánh kem 3 tầng)", "Chuỗi 10 cấp độ Đồ Uống (Hạt cà phê -> Espresso -> Latte Art)", "Chân dung 2D Live Emotion nhân vật Quinn, Cảnh sát trưởng, Chồng cũ"],
                "ui_canvas": ["Thanh năng lượng Energy Bar (Tối đa 100 sấm sét)", "Khay chứa 3 Đơn Hàng của cư dân thị trấn", "Giao diện Kho Bọc Đồ Phụ (Backpack Storage)", "Nút Heo Đất Tích Lũy (Piggy Bank Vault)"],
                "sfx_list": ["SFX Pop Giọt Nước (Merge chime pitch tăng dần)", "SFX Xuất Đơn Hàng (Cash Register Ka-ching)", "SFX Đập Heo Đất (Porcelain break)", "Nhạc nền Bossa Nova / Lo-fi Cafe"]
            },
            "clone_with_a_twist": [
                {"idea": "Đổi Theme sang 'Tiệm Trà Sữa & Bói Bài Tarot' (Mystic Boba Cafe)", "why": "Tệp Gen Z cực chuộng bói Tarot và trà sữa trân châu. Mỗi lần ghép ra cốc trà sữa cao cấp sẽ rút được 1 lá bài hé lộ tương lai tình cảm."},
                {"idea": "Cơ chế Thú Cưng Đói Bụng xin ăn trực tiếp trên bàn cờ", "why": "Mèo/Chó đi lại quanh bàn cờ nuốt bớt rác thừa và thưởng kim cương, giải quyết điểm nghẽn ức chế đầy bàn cờ của người chơi."},
                {"idea": "Tính năng Trang Trí Thời Trang cho Nữ Chính", "why": "Mở rộng kênh kiếm tiền IAP từ trang phục, váy dạ hội đi tiệc thị trấn."}
            ]
        }
    ]

    def __init__(self):
        pass

    def get_presets(self) -> List[Dict[str, Any]]:
        """Returns benchmark game reverse engineering blueprints."""
        return self.PRESET_DECONSTRUCTIONS

    def deconstruct_game(
        self,
        game_title: str = "Project Custom",
        platform: str = "PC / Mobile",
        genre_hint: str = "Action Roguelike",
        store_url: Optional[str] = None,
        raw_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deconstructs game into full reproduction blueprint."""
        # Find closest match if matches preset titles
        lower_title = game_title.lower()
        matched = None
        for p in self.PRESET_DECONSTRUCTIONS:
            if p["id"] in lower_title or lower_title in p["title"].lower():
                matched = p
                break

        if matched:
            result = dict(matched)
            result["game_title_input"] = game_title
            result["markdown_blueprint"] = self._format_blueprint_markdown(result)
            return result

        # Dynamic synthesis based on genre
        is_shooter = "shoot" in genre_hint.lower() or "action" in genre_hint.lower()
        is_strategy = "strat" in genre_hint.lower() or "4x" in genre_hint.lower() or "slg" in genre_hint.lower()

        blueprint = {
            "id": "custom_deconstruction",
            "title": game_title,
            "genre": genre_hint,
            "platform": platform,
            "camera_perspective": "Isometric 3D hoặc Top-Down 2.5D với hiệu ứng Camera Shake khi va chạm.",
            "control_scheme": "Hỗ trợ kép: Virtual Joystick cảm ứng trên Mobile và phím WASD + Chuột trên PC. Tự động tìm mục tiêu lân cận.",
            "physics_and_movement": {
                "movement_speed": "Tốc độ cơ bản 4.8m/s, gia tốc 12m/s², hãm phanh tức thì.",
                "collision_type": "Capsule Collider trên người chơi, Raycast kiểm tra chướng ngại vật mặt đất.",
                "hitbox_rules": "Khung bất tử 0.2s sau khi nhận đòn, có hiệu ứng chớp trắng (Sprite Flash White)."
            },
            "core_state_machine": [
                {"state": "SPAWN_CYCLE", "trigger": "Mỗi chu kỳ 10 giây", "action": "Sinh đợt kẻ địch theo hình vòng cung bao vây người chơi."},
                {"state": "ACTION_FEEDBACK", "trigger": "Người chơi tấn công trúng đích", "action": "Dừng hình cực ngắn 0.04s (Hit-stop freeze) + rung màn hình + hiện số sát thương nảy lên."},
                {"state": "PROGRESSION_GATE", "trigger": "Đạt đủ số lượng điểm / vượt ải", "action": "Mở cánh cổng ánh sáng dẫn sang màn tiếp theo kèm phần thưởng ngẫu nhiên."}
            ],
            "pacing_script": [
                {"timestamp": "0 - 2 Phút", "wave_name": "Tutorial & Hook", "density": "15 kẻ địch", "difficulty": "Rất Dễ", "objective": "Làm quen thao tác di chuyển và nhận thưởng kỹ năng đầu tiên."},
                {"timestamp": "2 - 6 Phút", "wave_name": "Escalation & Chokepoint", "density": "50 kẻ địch", "difficulty": "Trung Bình", "objective": "Ép người chơi sử dụng combo kỹ năng diện rộng."},
                {"timestamp": "6 - 10 Phút", "wave_name": "Climax Overlord Boss", "density": "1 Đại Boss", "difficulty": "Cao", "objective": "Trận chiến đỉnh cao, kích thích nạp tiền hoặc xem ads hồi sinh."}
            ],
            "narrative_and_quest_script": {
                "premise": f"Cốt truyện xoay quanh hành trình của nhân vật chính trong thế giới {game_title}, vượt qua các cạm bẫy để mở khóa sức mạnh tối thượng.",
                "tutorial_dialogue": "Người hướng dẫn: 'Hãy cảnh giác! Chạm vào màn hình để điều khiển nhân vật và giải phóng kỹ năng ngay bây giờ!'",
                "gameplay_audio_cues": "Âm thanh va chạm kim loại đanh thép; tiếng bước chân dồn dập; nhạc nền chuyển đổi từ êm dịu sang dồn dập khi quái vật xuất hiện."
            },
            "unity_starter_code": """// GenericCloneController.cs - Universal Character Movement & State Controller
using UnityEngine;

public class GenericCloneController : MonoBehaviour {
    public float moveSpeed = 5.0f;
    public Rigidbody rb;
    private Vector3 movement;

    void Update() {
        movement.x = Input.GetAxisRaw("Horizontal");
        movement.z = Input.GetAxisRaw("Vertical");
    }

    void FixedUpdate() {
        if (movement.magnitude > 0.1f) {
            rb.MovePosition(rb.position + movement.normalized * moveSpeed * Time.fixedDeltaTime);
            transform.rotation = Quaternion.LookRotation(movement);
        }
    }
}""",
            "asset_checklist": {
                "sprites": ["Nhân vật chính kèm 5 bộ animation (Idle, Run, Attack, Hit, Die)", "3 chủng loại quái vật cơ bản", "Bộ UI HUD (Thanh máu, Năng lượng, Điểm số)"],
                "ui_canvas": ["Thanh trạng thái đầu trận", "Menu nâng cấp chỉ số giữa màn", "Bảng tổng kết chiến thắng / thất bại"],
                "sfx_list": ["SFX di chuyển", "SFX tấn công & trúng đòn", "BGM chiến đấu nhịp nhanh"]
            },
            "clone_with_a_twist": [
                {"idea": "Bổ sung cơ chế Chuyển Đổi Vũ Khí Tức Thì (Weapon Swap Combo)", "why": "Tạo chiều sâu kỹ năng vượt trội so với bản gốc."},
                {"idea": "Tối ưu hóa dung lượng game dưới 50MB (Instant Play)", "why": "Giảm 40% chi phí CPI tải game trên Android."},
                {"idea": "Tích hợp Bảng Xếp Hạng Bạn Bè Thời Gian Thực", "why": "Kích hoạt tính cạnh tranh xã hội và lan truyền viral."}
            ]
        }

        blueprint["markdown_blueprint"] = self._format_blueprint_markdown(blueprint)
        return blueprint

    def _format_blueprint_markdown(self, data: Dict[str, Any]) -> str:
        """Formats the reverse engineering analysis as a full markdown blueprint."""
        title = data["title"]
        genre = data["genre"]
        platform = data["platform"]
        camera = data["camera_perspective"]
        controls = data["control_scheme"]
        phys = data["physics_and_movement"]
        states = data["core_state_machine"]
        pacing = data["pacing_script"]
        narrative = data["narrative_and_quest_script"]
        code = data["unity_starter_code"]
        assets = data["asset_checklist"]
        twists = data["clone_with_a_twist"]

        md = f"""# 🎮 BẢN THIẾT KẾ REVERSE-ENGINEERING & CLONE BLUEPRINT: {title.upper()}
*Thể Loại: {genre} | Nền Tảng: {platform}*

---

## 🕹️ 1. HỆ THỐNG ĐIỀU KHIỂN & VẬT LÝ CỐT LÕI (CORE CONTROLS & PHYSICS)
- **Góc Nhìn Camera:** {camera}
- **Cơ Chế Điều Khiển (Input Scheme):** {controls}
- **Thông Số Tốc Độ & Di Chuyển:** {phys['movement_speed']}
- **Cấu Hình Va Chạm (Collision):** {phys['collision_type']}
- **Quy Tắc Hitbox & I-Frame:** {phys['hitbox_rules']}

---

## ⚙️ 2. MÁY TRẠNG THÁI LỐI CHƠI (CORE STATE MACHINE)
"""
        for s in states:
            md += f"- **[{s['state']}]:** Trigger: *{s['trigger']}* $\\rightarrow$ Hành động: {s['action']}\n"

        md += """
---

## ⏱️ 3. KỊCH BẢN PHÂN BỔ NHỊP ĐỘ MÀN CHƠI (LEVEL PACING & WAVE SCRIPT)
"""
        for p in pacing:
            md += f"### {p['timestamp']} - {p['wave_name']}\n"
            md += f"- **Mật độ quái:** `{p['density']}` | **Độ khó:** `{p['difficulty']}`\n"
            md += f"- **Mục tiêu thiết kế:** {p['objective']}\n\n"

        md += f"""---

## 💬 4. KỊCH BẢN CỐT TRUYỆN & LỜI THOẠI HƯỚNG DẪN (NARRATIVE & QUESTS)
- **Tiền Đề Thế Giới:** {narrative['premise']}
- **Lời Thoại Hướng Dẫn Tutorial:** *"{narrative['tutorial_dialogue']}"*
- **Chỉ Dẫn m m Thanh & Cảm Xúc (Audio Cues):** {narrative['gameplay_audio_cues']}

---

## 💻 5. MÃ NGUỒN C# STARTER CODE (UNITY CONTROLLER)
```csharp
{code}
```

---

## 🎨 6. DANH MỤC TÀI NGUYÊN SẢN XUẤT (ASSET PRODUCTION CHECKLIST)
### Hình Ảnh & Animation (Sprites / 3D):
"""
        for a in assets.get("sprites", []):
            md += f"- [ ] {a}\n"

        md += "\n### Giao Diện Canvas (UI Hierarchy):\n"
        for u in assets.get("ui_canvas", []):
            md += f"- [ ] {u}\n"

        md += "\n### Hiệu Ứng m Thanh (SFX & BGM):\n"
        for s in assets.get("sfx_list", []):
            md += f"- [ ] {s}\n"

        md += """
---

## ⚡ 7. CÔNG THỨC "CLONE WITH A TWIST" (CẢI TIẾN ĐỂ VƯỢT MẶT BẢN GỐC)
"""
        for t in twists:
            md += f"- 💡 **{t['idea']}:** {t['why']}\n"

        md += """
---
*Xuất bản tự động bởi Game Trending Analyzer 2.0 Reverse Engineering Studio*
"""
        return md

game_deconstructor = GameDeconstructor()

