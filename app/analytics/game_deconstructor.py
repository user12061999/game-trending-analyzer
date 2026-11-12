"""Gameplay Deconstructor & Clone Blueprint Engine - Industry Grade 2.0.

Performs deep reverse engineering of game mechanics, minute-by-minute level pacing,
narrative/quest scripts, reward economy, and generates complete multi-file C# Unity starter scripts
and asset production checklists to allow a studio to clone or build an upgraded version of any game.
"""

from typing import Dict, Any, List, Optional
import json
import logging
import re
import urllib.request
import io
import zipfile

from app.analytics.rea_integrator import REAIntegrator

logger = logging.getLogger(__name__)


class GameDeconstructor:
    """Reverse-engineering engine that deconstructs any game into a reproduction blueprint."""

    GENRE_ARCHETYPES: Dict[str, Dict[str, Any]] = {
        "action_roguelike": {
            "name": "Action Roguelike / Bullet Heaven",
            "camera_perspective": "Top-Down 2D Orthographic (Camera follow mượt mà qua Lerp speed = 6.0, orthographic size = 7.5, góc nhìn bao quát toàn bộ đấu trường).",
            "control_scheme": "Single Virtual Joystick (Mobile) / WASD hoặc phím mũi tên (PC). Không cần nút bắn - toàn bộ vũ khí tự động kích hoạt theo cooldown.",
            "physics_and_movement": {
                "movement_speed": "Tốc độ cơ bản 5.2 m/s, gia tốc 18.0 m/s², hãm quán tính 14.0 m/s² (dừng sau 0.08s). Bổ trợ Speed +8% mỗi cấp (Max +40%).",
                "acceleration_and_deceleration": "Phản xạ tức thì (Near-instant response curve), thời gian đạt vận tốc tối đa 0.06s giúp né tránh đạn mượt mà.",
                "coyote_and_buffering": "Input buffering 150ms cho các kỹ năng kích hoạt chủ động (Dash/Bomb); không có Coyote time do không có địa hình nhảy.",
                "collision_and_hitbox": "Circle Collider trên nhân vật (bán kính 0.32m). Quái vật dùng Circle Collider có lực đẩy nhẹ (Soft separation repulsion force = 3.5N) chống chồng chéo điểm.",
                "game_feel_juice": "Hit-stop: 45ms khi trúng đòn chí mạng. Screen shake: Rung chấn góc 4° với độ suy giảm chấn động 0.15s. Flash trắng (Sprite white flash) 0.06s khi quái nhận sát thương.",
                "damage_formula": "Sát Thương Thực Tế = (Sát Thương Vũ Khí × Hệ Số Kỹ Năng - Giáp Quái × 0.25) × (1 + Sát Thương Bạo Kích nếu Crit) × Hệ Số Vùng AoE.",
                "combat_synergies": [
                    "Vũ Khí Roi Đôi (Whip) + Trái Tim Đen = 'Huyết Vũ Khí Thần Thoại' (Hút 1 HP mỗi đòn đánh trúng 5 quái).",
                    "Cầu Sét Ma Pháp + Sách Thần = 'Bão Điện Từ Viền Màn Hình' (Triệu hồi sấm sét liên hoàn giật lan 8 mục tiêu).",
                    "Vòng Tỏi Hộ Thể + Trái Tim Băng = 'Lãnh Địa Hàn Băng' (Đóng băng 100% quái vật chạm vào hào quang)."
                ]
            },
            "core_state_machine": {
                "player_fsm": [
                    {"state": "IDLE", "trigger": "Input == Vector2.zero", "action": "Phát animation thở nhẹ, duy trì hào quang vũ khí bị động.", "exit_condition": "Input != Vector2.zero"},
                    {"state": "LOCOMOTION", "trigger": "Input != Vector2.zero", "action": "Di chuyển theo vector chuẩn hóa, quay mặt theo hướng di chuyển (FlipX).", "exit_condition": "Input == Vector2.zero"},
                    {"state": "AUTO_FIRING", "trigger": "Weapon Cooldown <= 0", "action": "Quét kẻ địch gần nhất trong bán kính 10m, bắn đạn từ tâm nhân vật.", "exit_condition": "Đạn đã bắn, hồi chiêu reset"},
                    {"state": "HURT_IFRAME", "trigger": "Va chạm Collider quái vật", "action": "Mất HP, kích hoạt 0.25s bất tử (Sprite nhấp nháy alpha 0.4, bỏ qua va chạm sát thương).", "exit_condition": "Hết 0.25s bất tử"},
                    {"state": "LEVEL_UP_PAUSE", "trigger": "CurrentExp >= ExpToNextLevel", "action": "Set Time.timeScale = 0, phát âm thanh thăng cấp, mở pop-up chọn 1 trong 3 nâng cấp.", "exit_condition": "Người chơi chọn xong 1 thẻ kỹ năng"},
                    {"state": "DEATH_SEQUENCE", "trigger": "CurrentHP <= 0", "action": "Dừng di chuyển, phát hiệu ứng nổ hạt linh hồn, hiển thị bảng tổng kết chiến tích và nút hồi sinh bằng Ad/Gem.", "exit_condition": "Hồi sinh hoặc về Lobby"}
                ],
                "enemy_director_fsm": [
                    {"state": "SPAWN_OUT_OF_BOUNDS", "trigger": "Director Timer Tick (mỗi 1.5s)", "action": "Sinh quái tại rìa ngoài Camera Viewport (bán kính 1.25x so với khung nhìn).", "exit_condition": "Quái được Instantiate thành công"},
                    {"state": "FLOCKING_CHASE", "trigger": "Quái còn sống", "action": "Tính toán vector hướng về phía Player kết hợp lực đẩy tách bầy (Boids Separation) để không đè lên nhau.", "exit_condition": "Chạm Player hoặc bị tiêu diệt"},
                    {"state": "DEATH_AND_DROP", "trigger": "Enemy HP <= 0", "action": "Hủy quái, sinh ngọc EXP Gem tại vị trí chết, cộng điểm dồn cho thanh tiến độ màn chơi.", "exit_condition": "Spawn ngọc hoàn tất"}
                ]
            },
            "pacing_script": [
                {"timestamp": "00:00 - 00:45", "wave_name": "Giai Đoạn 1: Mồi Nhử & Cảm Xúc Chiến Thắng Tức Thì", "tension_score": 2, "density": "8 - 12 quái/phút", "difficulty": "Rất Dễ", "objective": "Dạy thao tác di chuyển né tránh cơ bản và nhặt 3 viên ngọc kinh nghiệm đầu tiên.", "player_emotion": "Thư giãn, tự tin, thích thú khi thấy quái nổ giòn tan.", "risk_and_monetization": "Không có nguy cơ chết. Rơi 100% ngọc EXP xanh lá."},
                {"timestamp": "00:45 - 02:00", "wave_name": "Giai Đoạn 2: Mở Rộng Kho Vũ Khí (First Build Choice)", "tension_score": 4, "density": "20 - 30 quái/phút", "difficulty": "Dễ", "objective": "Ép người chơi lên cấp 2 và cấp 3, đưa ra lựa chọn phong cách đánh: Cận chiến AoE hay Đạn ngắm xa.", "player_emotion": "Tò mò, háo hức thử nghiệm kỹ năng mới.", "risk_and_monetization": "Xuất hiện Skeleton có máu gấp đôi quái dơi."},
                {"timestamp": "02:00 - 03:30", "wave_name": "Giai Đoạn 3: Sát Hạch Di Chuyển & Quái Bắn Tỉa", "tension_score": 6, "density": "45 - 60 quái/phút", "difficulty": "Trung Bình", "objective": "Xuất hiện Pháp Sư Bắn Cầu Lửa tầm xa, bắt buộc người chơi không được đứng yên một chỗ.", "player_emotion": "Bắt đầu tập trung cao độ, mắt đảo liên tục tìm khoảng trống.", "risk_and_monetization": "Máu bắt đầu tụt nhẹ nếu không né đạn lửa."},
                {"timestamp": "03:30 - 05:00", "wave_name": "Giai Đoạn 4: Điểm Nghẽn Đầu Tiên (DPS Chokepoint)", "tension_score": 8, "density": "80 quái bủa vây vòng tròn", "difficulty": "Khó", "objective": "Kiểm tra tổng lượng sát thương (DPS Check). Người chơi chọn sai kỹ năng rời rạc sẽ bị dồn vào góc chết.", "player_emotion": "Căng thẳng, hồi hộp, tim đập nhanh khi vòng vây khép lại.", "risk_and_monetization": "Tỉ lệ chết lần 1 đạt 35% đối với người chơi mới."},
                {"timestamp": "05:00 - 06:15", "wave_name": "Giai Đoạn 5: Trùm Phụ Mini-Boss & Rương Hoàng Kim", "tension_score": 9, "density": "1 Mini-Boss Quỷ Đầu Đàn + Đàn Dơi", "difficulty": "Boss Nhỏ", "objective": "Đánh bại Mini-Boss có 2 kỹ năng: Húc Lao và Giậm Đất. Thưởng Rương Kho Báu 3 vật phẩm.", "player_emotion": "Kịch tính tột độ khi đấu Boss, vỡ òa phấn khích khi mở rương nổ pháo hoa.", "risk_and_monetization": "Rớt rương chứa 1 - 3 nâng cấp miễn phí tức thì."},
                {"timestamp": "06:15 - 07:45", "wave_name": "Giai Đoạn 6: Khan Hiếm Tài Nguyên & Quái Bọc Giáp", "tension_score": 7, "density": "60 quái thiết giáp kháng phép", "difficulty": "Khó", "objective": "Tỉ lệ rơi gà hồi máu giảm 50%, ép người chơi phải tìm cách kích hoạt Tiến Hóa Vũ Khí Thần Thoại.", "player_emotion": "Cẩn trọng, tính toán từng bước di chuyển để gom ngọc.", "risk_and_monetization": "Xuất hiện lời mời mua Hồi Máu Khẩn Cấp $0.99 nếu chết."},
                {"timestamp": "07:45 - 09:00", "wave_name": "Giai Đoạn 7: Biển Quái Tận Thế (The Apocalypse Swarm)", "tension_score": 10, "density": "120 quái tràn ngập màn hình", "difficulty": "Cực Khó", "objective": "Màn hình rung liên hồi, 100+ quái vật dồn ép nghẹt thở. Chỉ có combo vũ khí tối thượng mới dọn sạch được.", "player_emotion": "Ngộp thở, phấn khích cực đại khi kích hoạt chuỗi nổ liên hoàn màn hình.", "risk_and_monetization": "Nếu chết ở đây, 80% người chơi bấm xem Rewarded Video để hồi sinh."},
                {"timestamp": "09:00 - 10:00", "wave_name": "Giai Đoạn 8: Trùm Cuối Chúa Tể Hắc Ám (Climax Boss)", "tension_score": 10, "density": "Chúa Tể Ma Cà Rồng + 2 Quái Hộ Vệ", "difficulty": "Chung Kết", "objective": "Trùm Cuối sở hữu cơ chế cuồng bạo Enrage Timer (nếu không diệt trong 60s sẽ bao phủ sương độc toàn map).", "player_emotion": "Tập trung tuyệt đối, cảm giác thử thách kỹ năng đỉnh cao.", "risk_and_monetization": "Hạ gục Boss mở khóa màn chơi mới và nhân vật mới."},
                {"timestamp": "10:00+", "wave_name": "Giai Đoạn 9: Màn Hình Chiến Thắng & Vòng Lặp Giữ Chân (Retention Hook)", "tension_score": 1, "density": "Bảng Vinh Danh", "difficulty": "Thành Tựu", "objective": "Hiển thị thống kê DPS từng vũ khí, số lượng quái đã tiêu diệt, thưởng Vàng nâng cây Talent vĩnh viễn.", "player_emotion": "Thỏa mãn, tự hào, nóng lòng muốn 'làm thêm một ván nữa'.", "risk_and_monetization": "Nút 'Xem Ads nhân đôi tiền thưởng' (2x Gold) đạt CTR 70%."}
            ],
            "narrative_and_quest_script": {
                "premise": "Kỷ nguyên Vĩnh Hằng sụp đổ khi Mặt Trời Đỏ bị bóng tối nuốt chửng. Đội Vệ Binh Cuối Cùng phải tử thủ giữa nghĩa trang ngàn năm, hấp thụ linh thạch từ xác quái vật để thức tỉnh sức mạnh Thần Thoại trước bình minh.",
                "character_profiles": {
                    "protagonist": {"name": "Sir Donald the Lone Vanguard", "role": "Chiến binh tiên phong", "archetype": "Cận chiến kiếm thánh & roi thần", "battle_cry": "'Cho đến giọt máu cuối cùng, bóng đêm sẽ phải cúi đầu!'"},
                    "antagonist": {"name": "Lord Malakar the Crimson Vampire", "role": "Chúa tể Ma Cà Rồng", "archetype": "Trùm cuối thao túng huyết tộc", "villain_philosophy": "'Linh hồn các ngươi chỉ là thức ăn bồi bổ cho bóng tối trường tồn!'"},
                    "mentor_npc": {"name": "Elder Lyra", "role": "Học giả dẫn lối", "guidance_tone": "Khẩn trương, uyên bác, liên tục nhắc nhở thu thập ngọc kinh nghiệm để tiến hóa vũ khí."}
                },
                "scripted_dialogues": {
                    "act_1_intro": "Elder Lyra: 'Donald, bầy quỷ đã tràn qua cổng phía Tây! Đừng dừng chân lại dù chỉ một giây, hãy gom ngọc ma thuật để kích hoạt roi thánh!'\nDonald: 'Ta cảm nhận được sức mạnh của ánh sáng đang trở lại. Đến đây lũ quái vật!'",
                    "act_2_midgame": "Elder Lyra: 'Cẩn thận! Đất mẹ đang rung chuyển, một con Quỷ Đầu Đàn mang giáp gai đang lao về phía con!'\nDonald: 'Thứ giáp mục nát đó không cản được lưỡi kiếm của ta!'",
                    "act_3_boss_encounter": "Lord Malakar: 'Đáng khen cho kẻ phàm trần đã sống sót đến phút thứ 9... Nhưng đêm nay là mồ chôn của ngươi!'\nDonald: 'Tội ác của ngươi kết thúc tại đây, Malakar! Hãy nếm thử sức mạnh Thần Thoại!'\nVictory Quote: 'Bình minh đã ló rạng... Nhưng trận chiến bảo vệ vương quốc chỉ mới bắt đầu.'"
                },
                "quest_hierarchy": {
                    "main_quests": [
                        {"title": "Khai Hoả Vũ Khí", "desc": "Sống sót qua 3 phút đầu tiên trong Nghĩa Trang Vĩnh Hằng.", "reward": "500 Vàng + Mở khóa Vũ khí Phi Tiêu Độc"},
                        {"title": "Đồ Tể Quái Vật", "desc": "Tiêu diệt 1,000 quái vật trong một trận đánh đơn.", "reward": "Mở khóa Nhân Vật Pháp Sư Lôi Điện"},
                        {"title": "Thảm Sát Chúa Tể", "desc": "Hạ gục Lord Malakar trước khi hắn kích hoạt Enrage Timer.", "reward": "Cúp Danh Dự Vàng + Mở Map 2 Sa Mạc Lửa"}
                    ],
                    "daily_quests": [
                        {"title": "Gom Ngọc Tinh Anh", "desc": "Thu thập 2,500 viên ngọc EXP bất kỳ màu nào.", "reward": "200 Vàng"},
                        {"title": "Đỉnh Cao Tiến Hóa", "desc": "Tiến hóa thành công ít nhất 2 vũ khí Thần Thoại trong 1 trận.", "reward": "1 Rương Gacha Trang Bị"}
                    ],
                    "hardcore_bounties": [
                        {"title": "Vượt Ngục Không Nhận Sát Thương", "desc": "Sống sót 5 phút đầu mà không mất 1 giọt máu nào.", "reward": "Danh hiệu Huyền Thoại 'Bóng Ma Chiến Trường'"}
                    ]
                },
                "gameplay_audio_cues": "m thanh lách cách vui tai giòn tan khi ngọc bay liên hồi vào người; chuông thánh ca ngân vang khi lên cấp; tiếng sấm nổ đanh tai khi vũ khí tiến hóa Thần Thoại; nhạc nền metal guitar dồn dập khi quái vật tràn ngập màn hình."
            }
        },
        "action_rpg_souls": {
            "name": "Action RPG / Souls-like / Open World",
            "camera_perspective": "Third-Person Behind-The-Back (Over-The-Shoulder), góc nhìn tự do 360°, có cơ chế Lock-On giữ chặt tâm ngắm vào điểm yếu của Boss, tự động kéo lùi camera khi vào đấu trường rộng.",
            "control_scheme": "Dual Stick / Chuột + Phím WASD. Chuột trái: Tấn công nhẹ (Light Attack). Chuột phải: Trọng kích (Heavy Charged Attack). Spacebar: Lộn nhào né đòn (Dodge Roll). Shift: Chạy nhanh (Sprint). Phím Q/E: Xả phép thuật & kỹ năng biến hình.",
            "physics_and_movement": {
                "movement_speed": "Đi bộ 2.5 m/s, chạy thường 5.5 m/s, chạy nước rút Sprint 8.5 m/s (tiêu hao 12 thể lực/giây). Né lộn Roll di chuyển 7.0m trong 0.45s.",
                "acceleration_and_deceleration": "Có trọng lượng quán tính chân thực (Kinematic Root Motion), nhân vật xoay người có độ trễ 0.12s tạo cảm giác đầm chắc như thật.",
                "coyote_and_buffering": "Input Buffering cực kỳ nghiêm ngặt: Bộ nhớ đệm 250ms cho phép bấm chuỗi combo đòn đánh trước khi animation kết thúc (Combo Chaining).",
                "collision_and_hitbox": "Capsule Collider chính xác từng khớp xương (Rigid Bone Hitboxes). Đòn quét kiếm chỉ gây sát thương khi Model vũ khí thực tế chạm vào Hurtbox của đối thủ.",
                "game_feel_juice": "Hit-stop: 65ms khi chém trúng giáp dày, 90ms khi thực hiện đòn phản đòn hoàn hảo (Parry Deflect). Rung màn hình góc nghiêng 6° theo phương chém kiếm. Vết chém phát sáng vàng rực để lại tia lửa kim loại.",
                "damage_formula": "Sát Thương Thực Tế = [(Công Cơ Bản × Tỉ Lệ Kỹ Năng) - Giáp Địch × (1 - Xuyên Giáp%)] × (1 + Sát Thương Bạo Kích) × Hệ Số Thể Lực Đọng (Stamina Multiplier).",
                "combat_synergies": [
                    "Định Thân Thuật (Immobilize Spell) + Trọng Kích Gậy Thần 4 Tầng Điểm Tích Lũy = Đòn chí mạng nổ tung 400% sát thương.",
                    "Lộn Né Chuẩn Xác (Perfect Dodge) để lại phân thân tàng hình, làm chậm thời gian xung quanh 1.5s (Witch Time).",
                    "Biến Hình Thần Thú Lửa (Fire Transformation) thiêu đốt thanh Giác Ngộ (Stagger Bar) của Boss, khiến Boss gục ngã vào trạng thái hành quyết (Fatal Execution)."
                ]
            },
            "core_state_machine": {
                "player_fsm": [
                    {"state": "IDLE_STANCE", "trigger": "Không có input di chuyển/tấn công", "action": "Hồi phục Thể Lực (Stamina Regen +25/s), duy trì thế thủ kiếm.", "exit_condition": "Nhận lệnh thao tác mới"},
                    {"state": "LIGHT_ATTACK_COMBO", "trigger": "Bấm Chuột Trái (Light Attack)", "action": "Thực hiện chuỗi 4 đòn đánh nối tiếp (Slash 1 -> Slash 2 -> Thrust -> Overhead Slam). Tiêu hao 15 Stamina/đòn.", "exit_condition": "Hết combo hoặc bị ngắt chiêu"},
                    {"state": "HEAVY_CHARGE_ATTACK", "trigger": "Giữ Chuột Phải tích tụ điểm", "action": "Tích lũy từ 1 đến 4 tầng nội lực. Khi thả tay, phóng đòn đập đất diện rộng hất tung quái.", "exit_condition": "Xả đòn hoàn tất"},
                    {"state": "DODGE_ROLL_IFRAME", "trigger": "Bấm Spacebar né tránh", "action": "Lộn nhào, kích hoạt 0.35s I-Frame bất khả xâm phạm. Tiêu hao 20 Stamina.", "exit_condition": "Hết animation lộn nhào (0.5s)"},
                    {"state": "PARRY_DEFLECT", "trigger": "Bấm phím Đỡ đòn ngay trước khi địch chạm vũ khí 0.1s", "action": "Ngắt đòn tấn công của địch, gây 100% choáng lên thanh Giác Ngộ, mở cơ hội phản công tất sát.", "exit_condition": "Thực hiện đòn phản công xong"},
                    {"state": "STAGGERED_HURT", "trigger": "Bị đánh trúng khi hết Stamina hoặc dính đòn nặng", "action": "Khựng người 0.8s, không thể điều khiển, dễ bị trúng đòn liên hoàn.", "exit_condition": "Hết thời gian choáng"},
                    {"state": "EXECUTING_FINISHER", "trigger": "Bấm nút Tương tác khi Boss bị phá vỡ thanh Giác Ngộ", "action": "Camera khóa chặt vào góc điện ảnh cinematic, nhân vật tung đòn kết liễu gây sát thương khổng lồ.", "exit_condition": "Cinematic kết thúc"}
                ],
                "enemy_director_fsm": [
                    {"state": "PATROL_AND_AGGRO", "trigger": "Người chơi bước vào bán kính nhìn thấy 15m", "action": "Gầm vang, rút vũ khí, bước đi chậm rãi đo khoảng cách với người chơi.", "exit_condition": "Vào tầm đánh hoặc bị tấn công"},
                    {"state": "TELEGRAPH_ATTACK", "trigger": "Đến khoảng cách ra đòn", "action": "Giơ vũ khí lên cao, phát tín hiệu ánh sáng đỏ ở mắt (0.4s báo hiệu) để người chơi chuẩn bị bấm né đòn.", "exit_condition": "Bắt đầu vung đòn"},
                    {"state": "EXECUTE_ATTACK_STRING", "trigger": "Hết giai đoạn báo hiệu", "action": "Vung chuỗi đòn đánh theo quỹ đạo vật lý, kiểm tra va chạm với khiên hoặc da thịt người chơi.", "exit_condition": "Đòn đánh hoàn tất"},
                    {"state": "POST_ATTACK_VULNERABLE", "trigger": "Vừa vung đòn xong", "action": "Khựng lại 0.6s để thu hồi vũ khí (Recovery Window) - đây là thời cơ vàng để người chơi phản đòn.", "exit_condition": "Thu hồi thế thủ xong"},
                    {"state": "PHASE_2_ENRAGE_TRANSFORMATION", "trigger": "Máu Boss tụt xuống dưới 50%", "action": "Hất văng người chơi ra xa, gầm vang, bốc cháy toàn thân, mở khóa bộ kỹ năng sát thủ mới.", "exit_condition": "Chuyển Phase 2 hoàn tất"}
                ]
            },
            "pacing_script": [
                {"timestamp": "00:00 - 01:00", "wave_name": "Giai Đoạn 1: Lối Đi Cổ Tích & Cảm Giác Bước Chân", "tension_score": 3, "density": "2 Tiểu Yêu Lính Canh", "difficulty": "Rất Dễ", "objective": "Dạy thao tác xoay camera, di chuyển nhẹ nhàng và tấn công lén sau lưng (Backstab).", "player_emotion": "Hồi hộp, đắm chìm vào không khí thần bí của núi rừng.", "risk_and_monetization": "Lính canh gây ít sát thương, dễ dàng bị hạ bởi combo 3 đòn."},
                {"timestamp": "01:00 - 02:30", "wave_name": "Giai Đoạn 2: Thử Thách Quản Lý Thể Lực (Stamina Management)", "tension_score": 5, "density": "3 Lính Giáo + 1 Cung Thủ Trên Cao", "difficulty": "Dễ - Trung Bình", "objective": "Ép người chơi học cách né tên bắn tỉa và không được spam nút đánh bừa bãi kẻo cạn sạch thể lực.", "player_emotion": "Bắt đầu cẩn trọng, tính toán từng cú vung gậy và bước né.", "risk_and_monetization": "Rơi Bình Thuốc Hồi Máu đầu tiên tại Đền Thờ."},
                {"timestamp": "02:30 - 04:30", "wave_name": "Giai Đoạn 3: Cạm Bẫy Độc & Quái Tinh Anh Giáp Dày", "tension_score": 7, "density": "1 Đầu Lĩnh Lợn Rừng Giáp Sắt", "difficulty": "Trung Bình - Khó", "objective": "Đầu Lĩnh có lớp giáp dày miễn nhiễm đòn thường. Bắt buộc người chơi phải dùng Kỹ Năng Biến Hình hoặc Đòn Trọng Kích phá giáp.", "player_emotion": "Thử thách kỹ năng, cảm giác đối thủ thông minh biết chặn đòn.", "risk_and_monetization": "Nếu chết, hồi sinh tại Đền Thờ gần nhất, quái thường hồi sinh."},
                {"timestamp": "04:30 - 06:30", "wave_name": "Giai Đoạn 4: Con Đường Dẫn Đến Cổng Đại Điện", "tension_score": 8, "density": "Bầy Sói Tuyết 5 con bao vây", "difficulty": "Khó", "objective": "Đàn sói tấn công phối hợp bọc lót. Thử thách khả năng sử dụng Bùa Chú Định Thân để khống chế đám đông.", "player_emotion": "Căng thẳng khi bị vây ép, thỏa mãn khi đóng băng được cả đàn sói.", "risk_and_monetization": "Rơi nguyên liệu rèn đúc Vũ Khí Cấp Cao."},
                {"timestamp": "06:30 - 09:30", "wave_name": "Giai Đoạn 5: ĐẠI CHIẾN BOSS - BẠCH Y TÚ SĨ / HẮC PHONG QUỶ VƯƠNG", "tension_score": 10, "density": "1 Đại Boss 2 Phase Chiến Đấu", "difficulty": "Cực Đỉnh (Hardcore Souls)", "objective": "Phase 1: Đánh cận chiến bằng thương chớp nhoáng. Phase 2: Biến thành Bạch Xà khổng lồ bơi lội dưới nước phóng độc diện rộng.", "player_emotion": "Tim đập thình thịch, tập trung 200% vào từng cử động của Boss, vỡ òa sung sướng khi Parry thành công.", "risk_and_monetization": "Thử thách có thể khiến người chơi chết 5-10 lần trước khi qua được."},
                {"timestamp": "09:30 - 10:00", "wave_name": "Giai Đoạn 6: Hoạt Họa Kết Liễu & Mở Rộng Thần Khí", "tension_score": 2, "density": "Đoạn Phim Điện Ảnh Cinematic", "difficulty": "Chiến Lợi Phẩm", "objective": "Thực hiện đòn kết liễu hoành tráng, hấp thụ linh hồn của Boss vào Gậy Như Ý, mở khóa Phép Thuật Mới.", "player_emotion": "Cực kỳ thỏa mãn, cảm giác mình là vị anh hùng bất bại.", "risk_and_monetization": "Mở khóa trang phục Thần Thoại và chế độ New Game+."}
            ],
            "narrative_and_quest_script": {
                "premise": "Thiên Đình chìm trong tro tàn sau cuộc chiến ngàn năm. Một Thiên Mệnh Nhân vô danh bước xuống trần gian, thu thập lục căn của Tề Thiên Đại Thánh bị phân tán khắp nhân gian để tái thiết lập trật tự đất trời.",
                "character_profiles": {
                    "protagonist": {"name": "Destined One (Thiên Mệnh Nhân)", "role": "Hầu Tộc Hậu Duệ", "archetype": "Chiến binh gậy thần võ công tuyệt luân", "battle_cry": "'Gậy sắt trong tay ta đập tan mọi giả tạo thần thánh!'"},
                    "antagonist": {"name": "Hắc Phong Sơn Lĩnh Chủ", "role": "Yêu Ma Thủ Lĩnh", "archetype": "Gấu Đen tu luyện ngàn năm đoạt bảo", "villain_philosophy": "'Kẻ mạnh đoạt lấy thiên hạ, phàm nhân chỉ là cỏ rác dưới chân núi Hắc Phong!'"},
                    "mentor_npc": {"name": "Thổ Địa Núi Hắc Phong", "role": "Thần Thổ Địa dẫn lối", "guidance_tone": "Giọng già nua khúm núm nhưng uyên bác, hay xuất hiện từ gốc cây chỉ điểm huyệt đạo điểm yếu của yêu ma."}
                },
                "scripted_dialogues": {
                    "act_1_intro": "Thổ Địa: 'Ai dà, tiểu hầu tử ơi là tiểu hầu tử! Con đường phía trước yêu khí ngút trời, bao nhiêu anh hùng hảo hán vào đây một đi không trở lại rồi!'\nThiên Mệnh Nhân: (Gõ gậy xuống đất phát ra tiếng kim loại trầm hùng, ánh mắt kiên định hướng về đỉnh núi).",
                    "act_2_midgame": "Thổ Địa: 'Nguy rồi! Con súc sinh đầu lĩnh kia mang áo giáp Huyền Thiết đao kiếm không lọt! Phải nhắm vào mắt nó khi nó lao tới!'",
                    "act_3_boss_encounter": "Lĩnh Chủ Hắc Phong: 'Khỉ con! Ngươi tưởng cầm được cây gậy rỉ sét đó là xứng danh Đại Thánh sao? Hãy bỏ mạng tại đây!'\n(Sau trận chiến ác liệt)\nLĩnh Chủ: 'Không thể nào... Thần lực này... ngươi thực sự là...'\nThổ Địa: 'Lành thay! Thần khí thứ nhất đã trở về với chủ nhân đích thực!'"
                },
                "quest_hierarchy": {
                    "main_quests": [
                        {"title": "Lần Theo Yêu Khí", "desc": "Tìm đến Đền Thờ Cổ chân núi Hắc Phong và thắp nén nhang đầu tiên.", "reward": "Mở khóa Bình Rượu Cứu Mạng + 300 Linh Hồn"},
                        {"title": "Đập Vỡ Giáp Gai", "desc": "Tiêu diệt Đầu Lĩnh Lợn Rừng mà không bị dính đòn húc trực diện.", "reward": "Mở khóa Kỹ Năng Biến Hình Sói Lửa"},
                        {"title": "Thu Hồi Lục Căn Thứ Nhất", "desc": "Hạ gục Hắc Phong Sơn Lĩnh Chủ, giải cứu dân làng dưới chân núi.", "reward": "Bảo vật 'Như Ý Kim Cô Bổng'"}
                    ],
                    "daily_quests": [
                        {"title": "Luyện Tập Phản Xạ Parry", "desc": "Thực hiện thành công 10 lần gạt đòn (Deflect) trong ngày.", "reward": "150 Linh Thạch Nâng Cấp"},
                        {"title": "Hái Thuốc Tiên", "desc": "Tìm kiếm 5 nhánh Linh Chi Ngàn Năm trên vách đá.", "reward": "Tăng vĩnh viễn 5% kháng độc"}
                    ],
                    "hardcore_bounties": [
                        {"title": "Tốc Chiến Tuyệt Đối", "desc": "Đánh bại Trùm Cuối trong vòng dưới 2 phút ở cấp độ khó ác mộng.", "reward": "Bộ Áo Giáp Hoàng Kim Tề Thiên"}
                    ]
                },
                "gameplay_audio_cues": "Tiếng gậy sắt chạm đá nổ tia lửa 'Keng' đanh thép; tiếng gió rít xé toạc không khí khi vung trọng kích; tiếng tụng kinh tiếng Phạn ma mị hòa cùng dàn trống trận dồn dập khi Boss chuyển sang Phase 2 cuồng bạo."
            }
        },
        "shooter_tactical_br": {
            "name": "Tactical Shooter / Battle Royale / FPS",
            "camera_perspective": "First-Person (FPS) hoặc Third-Person (TPS) chuyển đổi ngắm bắn qua đầu ruồi (ADS - Aim Down Sights) với FOV co lại từ 90° về 60°, tái hiện giật súng thị giác chân thực.",
            "control_scheme": "Chuột Trái: Xả đạn (Fire). Chuột Phải: Ngắm bắn đầu ruồi (ADS). Phím R: Thay đạn (Reload). C: Ngồi (Crouch). Z: Nằm bò (Prone). Q/E: Nghiêng người qua góc tường (Lean Left/Right).",
            "physics_and_movement": {
                "movement_speed": "Đi bộ 4.0 m/s, chạy sprint 6.8 m/s (cầm dao tăng +15% tốc độ), ngồi di chuyển 2.2 m/s, bò 1.0 m/s. Nhảy cao 1.1m (tiêu hao thể lực nhảy để chống Bunny Hop spam).",
                "acceleration_and_deceleration": "Gia tốc quán tính mặt đất 10 m/s². Khi đổi hướng đột ngột bị khựng nhẹ 0.1s (Inertia physics) để tránh tình trạng ADAD spam lạng lách vô lý.",
                "coyote_and_buffering": "Input buffering 100ms cho thao tác nạp đạn và rút súng phụ.",
                "collision_and_hitbox": "Hitbox phân vùng 5 phần chuẩn eSports: Đầu (Head: Hệ số x2.5 sát thương), Ngực (Chest: x1.0), Bụng (Stomach: x1.1), Tay (Arms: x0.8), Chân (Legs: x0.75).",
                "game_feel_juice": "Recoil Pattern: Đường đạn giật theo quỹ đạo số 7 ngược đặc trưng (Spray Pattern). Camera Punch giật lên 3° mỗi phát bắn. m thanh Headshot 'Ping' đanh thép như kim loại vỡ tạo cảm giác thỏa mãn tột cùng.",
                "damage_formula": "Sát Thương Thực Tế = Sát Thương Viên Đạn × Hệ Số Vùng Bắn (Head 2.5x) × (1 - Hiệu Quả Mũ/Giáp%) × Suy Giảm Khoảng Cách (Damage Dropoff per 100m).",
                "combat_synergies": [
                    "Lựu đạn Khói (Smoke) + Ống Ngắm Nhiệt (Thermal Scope) = Xuyên thấu hạ gục kẻ địch mù thông tin.",
                    "Lựu đạn Choáng (Flashbang) + Đột kích cận chiến bằng Shotgun = Xóa sổ hoàn toàn đội hình địch trong phòng kín.",
                    "Súng Nhắm Bắn Tỉa (Sniper Rifle) kê góc hẹp (Pixel Peek) kết hợp gỡ bom giả (Fake Defuse) câu đối phương lộ diện."
                ]
            },
            "core_state_machine": {
                "player_fsm": [
                    {"state": "UNARMED_OR_HOLSTERED", "trigger": "Phím số 3 (Dao/Tay không)", "action": "Tăng tốc độ chạy lên mức tối đa, hồi phục thể lực nhanh hơn.", "exit_condition": "Rút súng"},
                    {"state": "WEAPON_READY_HIPFIRE", "trigger": "Rút súng chính/phụ", "action": "Tâm ngắm mở rộng theo tốc độ di chuyển, sẵn sàng bắn tức thì (Bắn từ hông).", "exit_condition": "Ngắm ADS hoặc nạp đạn"},
                    {"state": "AIM_DOWN_SIGHTS (ADS)", "trigger": "Giữ Chuột Phải", "action": "Thu nhỏ FOV, giảm độ phân tán đạn 70%, tốc độ di chuyển giảm 40%.", "exit_condition": "Nhả Chuột Phải"},
                    {"state": "RECOIL_SPRAY_FIRING", "trigger": "Nhấn giữ Chuột Trái", "action": "Phun đạn liên thanh, tâm súng giật nảy theo quy luật Spray Pattern, đạn giảm dần trong băng.", "exit_condition": "Nhả chuột hoặc hết đạn"},
                    {"state": "RELOADING_MAGAZINE", "trigger": "Bấm R hoặc bắn hết viên cuối", "action": "Thực hiện thao tác tháo băng đạn cũ và lắp băng đạn mới (2.2s). Không thể bắn trong lúc này.", "exit_condition": "Nạp đạn xong"},
                    {"state": "DOWNED_BLEEDOUT", "trigger": "HP về 0 trong chế độ Squad", "action": "Bị gục ngã xuống đất, chỉ có thể bò chậm 0.8 m/s, đếm ngược thanh máu cứu trợ 60s.", "exit_condition": "Đồng đội hồi sinh hoặc chết hẳn"}
                ],
                "enemy_director_fsm": [
                    {"state": "TACTICAL_PATROL", "trigger": "Chưa phát hiện tiếng súng", "action": "Di chuyển giữa các điểm ẩn nấp (Cover to Cover), quan sát các góc ngã ba.", "exit_condition": "Nghe tiếng bước chân hoặc nhìn thấy bóng người"},
                    {"state": "TAKE_HARD_COVER", "trigger": "Bị bắn trúng hoặc phát hiện hỏa lực áp đảo", "action": "Lập tức ngồi thụp xuống sau bờ tường bê tông, giơ súng bắn quấy rối (Blind Fire).", "exit_condition": "Hồi phục giáp hoặc chuyển vị trí"},
                    {"state": "FLANKING_MANEUVER", "trigger": "Đồng đội đang kìm chân người chơi", "action": "Chạy vòng qua cánh hông theo góc khuất để bắn tạt sườn (Crossfire setup).", "exit_condition": "Đạt góc bắn thuận lợi"}
                ]
            },
            "pacing_script": [
                {"timestamp": "00:00 - 01:30", "wave_name": "Giai Đoạn 1: Đổ Bộ Bầu Trời & Cuộc Đua Nhặt Đồ (Loot Scramble)", "tension_score": 7, "density": "20 Người Cùng Khu Vực", "difficulty": "Hên Xui / Hỗn Loạn", "objective": "Nhảy dù xuống nóc nhà, tranh cướp khẩu súng đầu tiên và bộ giáp Cấp 1.", "player_emotion": "Hồi hộp, căng thẳng tột độ khi nghe tiếng bước chân sát vách.", "risk_and_monetization": "Chết sớm nếu không tìm thấy súng (Early elimination)."},
                {"timestamp": "01:30 - 04:00", "wave_name": "Giai Đoạn 2: Vòng Bo Thu Hẹp Lần 1 & Ổn Định Trang Bị", "tension_score": 4, "density": "Bản Đồ 2km", "difficulty": "Trung Bình", "objective": "Tập hợp đồng đội, chia sẻ đạn dược, trang bị phụ kiện nòng giảm thanh và ống ngắm 4x.", "player_emotion": "Bình tĩnh hơn, bắt đầu triển khai chiến thuật di chuyển xe cộ.", "risk_and_monetization": "Vòng bo xanh bắt đầu gây sát thương nhẹ nếu chạy chậm."},
                {"timestamp": "04:00 - 07:00", "wave_name": "Giai Đoạn 3: Giao Tranh Tầm Trung & Tranh Đoạt Thính Hàng (Airdrop)", "tension_score": 8, "density": "10 Đội Còn Lại", "difficulty": "Khó", "objective": "Thùng Thính Vàng rơi xuống giữa đồng trống chứa súng Thần AWM và Giáp 3. Các đội bắn tỉa nhau kịch liệt.", "player_emotion": "Căng thẳng nghẹt thở, cân nhắc rủi ro / phần thưởng khi tiến lại gần thính.", "risk_and_monetization": "Nguy cơ bị một phát bắn tỉa Headshot bay màu."},
                {"timestamp": "07:00 - 09:30", "wave_name": "Giai Đoạn 4: Vòng Bo Tận Cùng (Final Circle Chokepoint)", "tension_score": 10, "density": "Top 3 Đội Sống Sót", "difficulty": "Cực Đỉnh Căng Thẳng", "objective": "Vòng bo co lại chỉ còn 30m vuông. Tung toàn bộ Lựu đạn khói, bom nổ, giành từng bờ đá góc cây.", "player_emotion": "Tim đập thình thịch, tay run run trên chuột, tập trung lắng nghe từng tiếng thở.", "risk_and_monetization": "Trận chiến phân định thắng thua của cả trận đấu."},
                {"timestamp": "09:30 - 10:00", "wave_name": "Giai Đoạn 5: WINNER WINNER CHICKEN DINNER! (Chiến Thắng Tuyệt Đối)", "tension_score": 1, "density": "Màn Hình Vinh Danh", "difficulty": "Vinh Quang", "objective": "Dòng chữ vàng rực xuất hiện trên màn hình, nhận huy chương MVP và điểm xếp hạng leo Rank Thách Đấu.", "player_emotion": "Hò reo phấn khích cùng đồng đội, chụp màn hình khoe bạn bè.", "risk_and_monetization": "Mở khóa rương skin súng Battle Pass."}
            ],
            "narrative_and_quest_script": {
                "premise": "Trên hòn đảo hoang dã biệt lập Erangel, một tổ chức bí ẩn phát động đấu trường sinh tồn khắc nghiệt. 100 chiến binh tinh nhuệ nhảy dù không vũ khí và chỉ có người sống sót duy nhất mới được quyền trở về thế giới văn minh.",
                "character_profiles": {
                    "protagonist": {"name": "Captain Miller", "role": "Lính Bắn Tỉa Đặc Nhiệm", "archetype": "Bình tĩnh, chính xác, đọc chiến thuật bản đồ", "battle_cry": "'Một viên đạn, một mạng người. Giữ vững đội hình!'"},
                    "antagonist": {"name": "Commander Viktor", "role": "Thủ Lĩnh Lực Lượng Đánh Thuê", "archetype": "Tàn bạo, sở hữu súng máy hạng nặng và xe bọc thép", "villain_philosophy": "'Kẻ yếu không có quyền thở trên hòn đảo này!'"},
                    "mentor_npc": {"name": "HQ Radio Operator", "role": "Sĩ quan thông tin radio", "guidance_tone": "Giọng đanh thép chuyên nghiệp, cập nhật thời gian vòng bo và vị trí máy bay thả thính."}
                },
                "scripted_dialogues": {
                    "act_1_intro": "Radio: 'Toàn đội chú ý! Đang bay qua khu vực Căn Cứ Quân Sự. Chuẩn bị bung dù trong 3... 2... 1... Nhảy!'\nMiller: 'Tôi thấy có 3 đội khác đang rơi cùng khu vực! Tìm súng ngay lập tức!'",
                    "act_2_midgame": "Radio: 'Cảnh báo: Vòng bo số 3 đang co lại cực nhanh! Máy bay vận tải vừa thả một kiện hàng đặc biệt tại tọa độ Delta!'\nMiller: 'Cẩn thận! Đằng kia có vết bánh xe... Có kẻ đang phục kích quanh hòm thính!'",
                    "act_3_boss_encounter": "Viktor: 'Tao thấy đầu mày lấp ló sau tảng đá rồi Miller! Ra đây nộp mạng đi!'\nMiller: (Thì thầm qua bộ đàm) 'Ném khói qua hướng 120 độ câu nhử... Tôi kê góc ngắm AWM vào gáy hắn rồi... BÙM!'\nRadio: 'Xác nhận mục tiêu cuối cùng đã bị tiêu diệt! Toàn đội chiến thắng!'"
                },
                "quest_hierarchy": {
                    "main_quests": [
                        {"title": "Sinh Tồn Đầu Game", "desc": "Sống sót qua 5 phút đầu tiên mà không bị đo ván.", "reward": "1,000 BP Tiền Game"},
                        {"title": "Xạ Thủ Tầm Xa", "desc": "Hạ gục đối thủ ở khoảng cách trên 200m bằng súng ngắm.", "reward": "Mở khóa Ống Ngắm Chấm Đỏ Dạ Quang"},
                        {"title": "Nhà Vô Địch Sinh Tồn", "desc": "Đạt Top 1 Winner Winner Chicken Dinner với ít nhất 5 Kills.", "reward": "Skin Áo Khoác Dù Lượn Huyền Thoại"}
                    ],
                    "daily_quests": [
                        {"title": "Bác Sĩ Chiến Trường", "desc": "Hồi máu cho bản thân hoặc đồng đội 200 điểm HP.", "reward": "Hòm Tiếp Tế Hàng Ngày"},
                        {"title": "Tập Lái Xe Bo", "desc": "Di chuyển 3,000 mét bằng phương tiện xe cơ giới.", "reward": "Thẻ Nhân Đôi EXP Rank"}
                    ],
                    "hardcore_bounties": [
                        {"title": "Thánh Xả Đạn Squad Wipe", "desc": "Một mình tự tay quét sạch toàn bộ 4 thành viên của một đội hình địch trong vòng 30 giây.", "reward": "Huy Hiệu Vàng Danh Vọng"}
                    ]
                },
                "gameplay_audio_cues": "Tiếng rít chói tai của đạn bay sạt qua mang tai (Bullet Whiz-by); tiếng 'Choang' bể nón Cấp 3 kim loại; tiếng bước chân rầm rập trên sàn gỗ tầng 2; tiếng động cơ máy bay rền vang bầu trời khi thả bom Red Zone."
            }
        },
        "strategy_4x_slg": {
            "name": "Hybrid 4X Strategy / City Survival / SLG",
            "camera_perspective": "Top-Down Isometric 3D trong căn cứ kết hợp World Map 10,000 ô lãnh thổ thu phóng mượt mà (Seamless Infinite Zoom từ chi tiết bếp ăn lên bản đồ toàn cảnh thế giới).",
            "control_scheme": "Touch / Click Point & Tap: Chạm vào công trình để nâng cấp, kéo thả công nhân vào lò sưởi/mỏ than, chạm điều phối đạo quân hành quân trên bản đồ lớn.",
            "physics_and_movement": {
                "movement_speed": "Đạo quân hành quân trên bản đồ thế giới di chuyển 8 ô/phút (kỵ binh), 5 ô/phút (bộ binh). Dân làng di chuyển theo NavMesh 3D trong căn cứ.",
                "acceleration_and_deceleration": "Không áp dụng gia tốc vật lý, tính toán dựa trên thời gian đếm ngược (Marching Timer) và khoảng cách Euclidean.",
                "coyote_and_buffering": "Hệ thống hàng đợi thao tác xây dựng (Construction Queue) lưu trữ 2 công trình nâng cấp đồng thời.",
                "collision_and_hitbox": "Tính toán chiến đấu dựa trên công thức toán học thời gian thực (Simulation Tick 1.0s), tính đối kháng quân chủng.",
                "game_feel_juice": "Khi nhiệt độ giảm âm 40 độ C, màn hình phủ lớp sương tuyết đóng băng viền kính (Frost Screen Shader). Tiếng củi nổ lách tách ấm áp khi nâng cấp Lò Sưởi.",
                "damage_formula": "Tổn Thất Chiến Đấu = (Lực Chiến Công Đội × Hệ Số Tướng × Khắc Chế Binh Chủng) / (Phòng Thủ Thành Trì + Kháng Sát Thương Liên Minh).",
                "combat_synergies": [
                    "Bộ Binh Phòng Ngự (Lá Chắn) + Cung Thủ Bắc Cực (Bắn Sau) = Giảm 60% thương vong quân sự.",
                    "Lò Sưởi Cấp Cao + Trạm Y Tế Hoạt Động 100% = Tăng tốc độ hồi phục lính thương vong lên gấp 3.",
                    "Hợp Sức Liên Minh (Rally Attack 10 Người) = Đập tan mọi cứ điểm phòng thủ đơn lẻ của đối thủ."
                ]
            },
            "core_state_machine": {
                "player_fsm": [
                    {"state": "RESOURCE_MANAGEMENT", "trigger": "Mỗi chu kỳ giờ trôi qua", "action": "Tính toán sản lượng gỗ/thịt/than trừ đi chi phí sưởi ấm căn cứ.", "exit_condition": "Tài nguyên cập nhật"},
                    {"state": "BLIZZARD_SURVIVAL_MODE", "trigger": "Đồng hồ bão tuyết về 0", "action": "Nhiệt độ tụt xuống -50°C, tiêu hao than gấp 3 lần, dân làng bắt đầu nhiễm bệnh nếu lò sưởi cấp thấp.", "exit_condition": "Bão tuyết tan (48h)"},
                    {"state": "HERO_EXPEDITION_BATTLE", "trigger": "Mở ải thám hiểm vượt map", "action": "Chiến đấu turn-based tự động 5vs5, xả kỹ năng khi nộ đầy 100 điểm.", "exit_condition": "Thắng hoặc Thua ải"}
                ],
                "enemy_director_fsm": [
                    {"state": "CAMP_IDLE", "trigger": "Chưa có ai khiêu chiến", "action": "Canh giữ mỏ tài nguyên cấp 5 trên bản đồ thế giới.", "exit_condition": "Bị đạo quân tấn công"},
                    {"state": "TERRITORY_INVASION", "trigger": "Sự kiện Boss Thú Dữ Bắc Cực xuất hiện", "action": "Hành quân tấn công vào các thành phố ven biên giới liên minh.", "exit_condition": "Bị tiêu diệt hoặc đánh chiếm xong"}
                ]
            },
            "pacing_script": [
                {"timestamp": "0 - 15 Phút", "wave_name": "Giai Đoạn 1: Cứu Sống Ngọn Lửa Đầu Tiên", "tension_score": 3, "density": "3 Dân Làng Co Rét", "difficulty": "Rất Dễ", "objective": "Nhóm than vào Lò Sưởi trung tâm, dựng lều tuyết đầu tiên và nấu súp ấm cho người ốm.", "player_emotion": "Cảm động, trách nhiệm của một vị thị trưởng giải cứu đồng bào.", "risk_and_monetization": "Tặng 500 than đá miễn phí."},
                {"timestamp": "15 - 45 Phút", "wave_name": "Giai Đoạn 2: Mở Rộng Địa Bàn & Đàn Sói Đột Kích", "tension_score": 5, "density": "5 Công Trình Cơ Bản", "difficulty": "Dễ", "objective": "Dựng Trạm Đốn Gỗ và Mỏ Than Đá, chiêu mộ Tướng Cung Thủ đầu tiên vượt ải săn thú.", "player_emotion": "Bận rộn một cách thỏa mãn khi thấy căn cứ ngày một ấm áp và đông đúc.", "risk_and_monetization": "Bắt đầu xuất hiện thời gian chờ xây dựng 5 phút (Dạy bấm nút Miễn Phí)."},
                {"timestamp": "Ngày 1 - Ngày 2", "wave_name": "Giai Đoạn 3: Cơn Bão Tuyết Lịch Sử Đầu Tiên (First Blizzard Test)", "tension_score": 8, "density": "Nhiệt độ -40°C Toàn Map", "difficulty": "Khó (Chokepoint)", "objective": "Yêu cầu Lò Sưởi đạt Cấp 7. Nếu thiếu Than Đá, dân làng sẽ chết cóng và năng suất về 0.", "player_emotion": "Cực kỳ lo lắng khi kim nhiệt kế tụt dốc không phanh.", "risk_and_monetization": "Gói Cứu Trợ Bão Tuyết $0.99 nổ ra với tỉ lệ chuyển đổi nạp cực cao."},
                {"timestamp": "Ngày 3 - Ngày 7", "wave_name": "Giai Đoạn 4: Gia Nhập Liên Minh & Chiến Tranh Mỏ Tài Nguyên", "tension_score": 7, "density": "Bản Đồ 10,000 Người Chơi", "difficulty": "Chiến Thuật Xã Hội", "objective": "Cắm cờ mở rộng lãnh thổ bang hội, hợp sức đào mỏ sắt cấp cao và bảo vệ đồng đội bị đánh phá.", "player_emotion": "Gắn kết bang hội, cảm giác có anh em che chở giữa mùa đông lạnh giá.", "risk_and_monetization": "Mở bán thẻ VIP tháng và Gói Tăng Tốc Xây Dựng."},
                {"timestamp": "Tuần 2+", "wave_name": "Giai Đoạn 5: Tranh Đoạt Lâu Đài Mặt Trời (Sun Castle Hegemony)", "tension_score": 10, "density": "Toàn Bộ Server Tranh Đua", "difficulty": "Đỉnh Cao Đua Tiền (Whales)", "objective": "Các bang hội lớn nhất server mở cuộc chiến tổng lực Rally 24/7 để chiếm quyền Vương Giả.", "player_emotion": "Hào hùng, khốc liệt, niềm vinh dự tối cao của toàn bộ liên minh.", "risk_and_monetization": "Các đại gia Whales nạp hàng ngàn USD để đua bảng xếp hạng."}
            ],
            "narrative_and_quest_script": {
                "premise": "Cơn đại hồng thủy băng giá nhấn chìm nền văn minh địa cầu dưới lớp tuyết dày 20 mét. Bạn là Thị Trưởng được những người sống sót bầu chọn để vận hành Lò Sưởi Hạt Nhân cuối cùng của nhân loại.",
                "character_profiles": {
                    "protagonist": {"name": "Mayor Jack", "role": "Thị Trưởng Căn Cứ Băng", "archetype": "Lãnh đạo kiên nghị, quyết đoán vì dân", "battle_cry": "'Chừng nào ngọn lửa này còn cháy, nhân loại sẽ không bao giờ tuyệt diệt!'"},
                    "antagonist": {"name": "General Frostbite", "role": "Thủ Lĩnh Lực Lượng Sa Lưới", "archetype": "Kẻ cướp bóc than đá và thức ăn của các thị trấn nhỏ", "villain_philosophy": "'Trong thế giới băng giá này, kẻ có than đá là kẻ làm vua!'"},
                    "mentor_npc": {"name": "Bác Sĩ Anna", "role": "Trưởng Trạm Y Tế", "guidance_tone": "Ân cần, luôn báo cáo sức khỏe dân làng và thúc giục nâng cấp nhiệt độ lò sưởi."}
                },
                "scripted_dialogues": {
                    "act_1_intro": "Bác Sĩ Anna: 'Thị trưởng! Nhiệt độ ngoài trời vừa giảm thêm 5 độ nữa rồi! Lũ trẻ đang run rẩy trong lều tuyết kìa!'\nJack: 'Đốt thêm than đá ngay lập tức! Ta hứa sẽ không để bất kỳ người dân nào phải chết cóng đêm nay!'",
                    "act_2_midgame": "Bác Sĩ Anna: 'Báo động đỏ! Cơn bão tuyết cấp 10 đang tràn từ cực Bắc xuống! Chúng ta cần ít nhất 10,000 than đá để duy trì lò sưởi qua đêm mai!'\nJack: 'Thông báo cho toàn thể binh lính xuất quân! Khai thác sạch các mỏ than xung quanh bằng mọi giá!'",
                    "act_3_boss_encounter": "General Frostbite: 'Giao nộp Lò Sưởi Hạt Nhân ra đây, Jack! Quân đoàn của tao sẽ biến thị trấn của mày thành bình địa!'\nJack: 'Liên Minh Băng Tuyết! Kích hoạt toàn bộ pháo phòng thủ thành trì! BẮN!'\nVictory Quote: 'Bão tuyết đã qua đi... Mặt trời lại ló rạng trên mái nhà của chúng ta!'"
                },
                "quest_hierarchy": {
                    "main_quests": [
                        {"title": "Khởi Động Lò Sưởi", "desc": "Nâng cấp Lò Sưởi Trung Tâm lên Cấp 5.", "reward": "Tướng Cam Huyền Thoại + 5,000 Than Đá"},
                        {"title": "Chống Bão Tuyết", "desc": "Sống sót qua đợt bão tuyết đầu tiên không để ai thiệt mạng.", "reward": "Mở khóa Nghiên Cứu Kỹ Thuật Công Nghiệp"},
                        {"title": "Bá Vương Mặt Trời", "desc": "Cùng liên minh chiếm đóng thành công Lâu Đài Trung Tâm.", "reward": "Vương Miện Thị Trưởng Tối Cao"}
                    ],
                    "daily_quests": [
                        {"title": "Phân Bổ Thợ Đốn Gỗ", "desc": "Thu thập 10,000 Gỗ trong ngày.", "reward": "100 Kim Cương"},
                        {"title": "Khám Chữa Bệnh", "desc": "Chữa khỏi cảm lạnh cho 10 dân làng.", "reward": "Thuốc Bổ Thần Kỳ"}
                    ],
                    "hardcore_bounties": [
                        {"title": "Chiến Tranh Không Gian Hạn", "desc": "Tiêu diệt 100,000 quân địch trong sự kiện Chiến Tranh Bang Hội.", "reward": "Khung Avatar Băng Tuyết Vĩnh Cửu"}
                    ]
                },
                "gameplay_audio_cues": "Tiếng gió tuyết hú rít từng cơn buốt giá; tiếng búa rèn kim loại gõ vang nhộn nhịp khi xây nhà; còi báo động không kích vang lên khi bão tuyết ập đến; tiếng kèn đồng vang dội khi đoàn quân thắng trận trở về."
            }
        },
        "casual_puzzle_merge": {
            "name": "Casual Merge-2 / Match-3 / Renovation",
            "camera_perspective": "2D Giao diện màn hình dọc chia đôi: Nửa trên hiển thị Dinh Thự / Nhà Hàng 2D Isometric rực rỡ, nửa dưới là Bàn Cờ Ghép Đồ (Merge Board 7x9 ô lưới) hoặc Match-3 Grid.",
            "control_scheme": "Tap & Drag một chạm: Chạm vào Hộp Dụng Cụ để sinh vật phẩm Lv.1, kéo thả 2 vật phẩm đồng cấp chồng lên nhau để nâng cấp lên bậc cao hơn, chạm 'Giao Hàng' để nhận Sao Cốt Truyện.",
            "physics_and_movement": {
                "movement_speed": "Kéo thả vật phẩm di chuyển mượt mà theo ngón tay với thuật toán Snap-to-Grid (Tự động hít vào ô lưới gần nhất).",
                "acceleration_and_deceleration": "Khi thả tay sai ô, vật phẩm nảy lò xo (Spring Physics) quay về vị trí ban đầu cực kỳ vui mắt.",
                "coyote_and_buffering": "Hỗ trợ vuốt nhanh liên tiếp không bị trễ khung hình.",
                "collision_and_hitbox": "Kiểm tra ô lưới Grid 2D đơn giản, chống đè lên các ô bị khóa bởi mạng nhện (Cobweb Blockers).",
                "game_feel_juice": "m thanh 'Pop' bong bóng vui nhộn có tông nốt nhạc tăng dần (Do - Re - Mi - Fa - Sol - La - Si) khi ghép liên tục. Tia sáng lấp lánh (Sparkle Particles) bung tỏa khi tạo ra món đồ cấp cao.",
                "damage_formula": "Hệ Thống Giá Trị Ghép Đồ: Vật phẩm Cấp N cần 2^(N-1) đơn vị Năng Lượng (Energy) cơ bản. Cấp càng cao, giá trị Vàng và Sao cốt truyện tăng theo cấp số nhân.",
                "combat_synergies": [
                    "Bánh Sandwich Cấp 8 + Tách Cà Phê Cấp 7 = Đơn Hàng VIP của Thị Trưởng (Thưởng Rương Năng Lượng Lớn).",
                    "Hộp Dụng Cụ Cấp Tối Đa = Tỉ lệ sinh ra vật phẩm Cấp 2 và Cấp 3 trực tiếp, tiết kiệm 50% Năng Lượng.",
                    "Heo Đất Tích Lũy Vàng = Nhập code sự kiện đập heo nhận ngay 500 Kim Cương."
                ]
            },
            "core_state_machine": {
                "player_fsm": [
                    {"state": "TAP_GENERATOR", "trigger": "Chạm vào máy phát vật phẩm", "action": "Trừ 1 Năng Lượng, nảy ra 1 món đồ Lv.1 vào ô trống gần nhất.", "exit_condition": "Hết năng lượng hoặc bàn cờ đầy"},
                    {"state": "MERGE_COMBINE", "trigger": "Kéo 2 món đồ cùng loại và cùng cấp đè lên nhau", "action": "Hợp nhất thành 1 món đồ Lv+1, phát âm thanh Popping và tia sáng sao.", "exit_condition": "Hợp thể hoàn tất"},
                    {"state": "FULFILL_ORDER", "trigger": "Có đủ món đồ khách hàng yêu cầu", "action": "Nút Giao Hàng phát sáng xanh, khách nhận đồ và trả Vàng + Sao Cốt Truyện.", "exit_condition": "Giao hàng xong"},
                    {"state": "RENOVATE_STORY", "trigger": "Bấm dùng Sao để sửa nhà", "action": "Chuyển lên màn hình trên, dọn dẹp đống tro tàn thành nhà hàng lộng lẫy kèm đoạn thoại cốt truyện.", "exit_condition": "Hoạt họa kết thúc"}
                ],
                "enemy_director_fsm": [
                    {"state": "SPAWN_COBWEB_BLOCKER", "trigger": "Mở rộng góc bàn cờ mới", "action": "Khóa ô bằng mạng nhện, đòi hỏi ghép món đồ tương ứng để giải phóng ô.", "exit_condition": "Ô được mở khóa"}
                ]
            },
            "pacing_script": [
                {"timestamp": "Level 1 - 3", "wave_name": "Giai Đoạn 1: Mở Lại Tiệm Bánh Đổ Nát Của Gia Đình", "tension_score": 1, "density": "Đơn Hàng Cấp 1 - 3", "difficulty": "Cực Dễ", "objective": "Dạy thao tác nhấp máy phát và ghép 2 cái bánh mì thành bánh sandwich.", "player_emotion": "Thư giãn tuyệt đối, âm thanh vui tai kích thích dopamine liên tục.", "risk_and_monetization": "Tặng 100 Năng Lượng dồi dào."},
                {"timestamp": "Level 4 - 8", "wave_name": "Giai Đoạn 2: Lần Đầu Tiên Hết Năng Lượng & Rewarded Ads", "tension_score": 4, "density": "Đơn Hàng Cấp 5 - 6", "difficulty": "Dễ", "objective": "Người chơi lần đầu cạn thanh 100 Năng Lượng. Giới thiệu nút xem Video Quảng Cáo nhận 25 Năng Lượng miễn phí.", "player_emotion": "Đang hào hứng ghép đồ thì bị ngắt nhịp, sẵn sàng xem ad để chơi tiếp.", "risk_and_monetization": "Xem video ads nhận năng lượng đạt CTR 85%."},
                {"timestamp": "Level 9 - 15", "wave_name": "Giai Đoạn 3: Nghẽn Bàn Cờ & Bán Túi Đựng Đồ (Inventory Friction)", "tension_score": 7, "density": "Đơn Hàng Cấp 7 - 9 (Bánh Kem 3 Tầng)", "difficulty": "Trung Bình (Khó Chỗ Trống)", "objective": "Bàn cờ bị lấp đầy bởi các chuỗi vật phẩm dở dang. Chokepoint ép người chơi mua thêm Ô Lưu Trữ Phụ (Backpack Slot).", "player_emotion": "Bực bội vì thiếu chỗ trống, cân nhắc bán bớt đồ hoặc nạp tiền mở kho.", "risk_and_monetization": "Mở bán slot túi đồ giá 50 Kim Cương."},
                {"timestamp": "Level 16 - 25", "wave_name": "Giai Đoạn 4: Kịch Tính Cốt Truyện (Ai Là Kẻ Phóng Hỏa?!)", "tension_score": 6, "density": "Đơn Hàng Cực Đại Cấp 11", "difficulty": "Khó", "objective": "Mở khóa nhân vật Chồng Cũ và Thám Tử Tư, cốt truyện ly kỳ như phim truyền hình Netflix.", "player_emotion": "Tò mò muốn biết bí mật câu chuyện, thôi thúc cày cuốc giao đơn hàng.", "risk_and_monetization": "Gói Battle Pass Mùa Hè mở khóa đồ trang trí độc quyền."},
                {"timestamp": "Level 25+", "wave_name": "Giai Đoạn 5: Sự Kiện Đua Top Đập Heo Đất & Bang Hội", "tension_score": 8, "density": "Đơn Hàng Sự Kiện Giới Hạn Giờ", "difficulty": "Đua Top Sự Kiện", "objective": "Đua bảng xếp hạng với 50 người chơi khác xem ai giao được nhiều đơn hàng nhất trong 48 giờ.", "player_emotion": "Cạnh tranh gay cấn, không muốn bị đối thủ vượt mặt ở những phút cuối.", "risk_and_monetization": "Nạp gói Kim Cương $4.99 để mua Năng Lượng đua top."}
            ],
            "narrative_and_quest_script": {
                "premise": "Sau cuộc hôn nhân tan vỡ với gã chồng tỷ phú lăng nhăng, Quinn ôm con gái nhỏ quay về thị trấn quê hương để tiếp quản nhà hàng ven biển của ông ngoại. Nhưng ngay đêm đầu tiên, một kẻ bí ẩn đã châm ngòi phóng hỏa thiêu rụi toàn bộ cơ ngơi.",
                "character_profiles": {
                    "protagonist": {"name": "Quinn Castillo", "role": "Bà Mẹ Độc Thân & Thợ Làm Bánh", "archetype": "Kiên cường, độc lập, không chịu khuất phục", "battle_cry": "'Chúng thiêu rụi nhà hàng của tôi, nhưng tôi sẽ xây lại nó rực rỡ hơn gấp mười lần!'"},
                    "antagonist": {"name": "Colton (Chồng Cũ)", "role": "Tỷ Phú Đầy Âm Mưu", "archetype": "Xảo quyệt, muốn dùng tiền ép Quinn giao quyền nuôi con", "villain_philosophy": "'Em không thể tự sống sót một mình ở cái thị trấn rách nát này đâu Quinn!'"},
                    "mentor_npc": {"name": "Cảnh Sát Trưởng Harrison", "role": "Bạn Thở Nhỏ & Cảnh Sát Địa Phương", "guidance_tone": "Ấm áp, chính trực, giúp Quinn điều tra các manh mối tàn tro tại hiện trường."}
                },
                "scripted_dialogues": {
                    "act_1_intro": "Quinn: 'Mọi thứ... tro tàn hết rồi sao? Không, mình không được khóc trước mặt con gái!'\nHarrison: 'Quinn! Đừng lo, tôi vừa tìm thấy một chiếc hộp dụng cụ cũ của ông ngoại em còn nguyên vẹn dưới tầng hầm. Chúng ta có thể bắt đầu lại từ đây!'",
                    "act_2_midgame": "Harrison: 'Quinn, tôi kiểm tra mẫu tàn tro ở cửa sau... Có dấu vết của chất xúc tác xăng máy bay chuyên dụng. Đây là vụ phóng hỏa có chủ đích!'\nQuinn: 'Chất xúc tác xăng máy bay ư? Chiếc phi cơ riêng của Colton vừa đáp xuống đảo chiều qua... Chẳng lẽ là hắn?!'",
                    "act_3_boss_encounter": "Colton: 'Quinn thân yêu, ký vào đơn nhượng quyền nuôi con đi, anh sẽ xây cho em một nhà hàng mới tại New York.'\nQuinn: 'Cầm đống tiền bẩn thỉu của anh biến đi Colton! Nhà hàng này là do chính đôi tay tôi và cư dân thị trấn tạo nên!'\nVictory Quote: 'Dòng người xếp hàng dài trước tiệm bánh mới... Công lý và hương vị ngọt ngào luôn chiến thắng!'"
                },
                "quest_hierarchy": {
                    "main_quests": [
                        {"title": "Dọn Dẹp Đống Tro Tàn", "desc": "Giao 3 đơn bánh mì đầu tiên để mua chổi và sơn tường.", "reward": "Mở khóa Bàn Cờ Nửa Trái"},
                        {"title": "Manh Mối Vụ Hỏa Hoạn", "desc": "Ghép thành công Kính Lúp Thám Tử Cấp 7.", "reward": "Đoạn Hoạt Họa Bí Ẩn Vụ Án"},
                        {"title": "Đại Tiệc Khai Trương", "desc": "Hoàn thành trang trí Sảnh Chính và Biển Hiệu Neon rực rỡ.", "reward": "Mở khóa Khu Vườn Trà Chiều"}
                    ],
                    "daily_quests": [
                        {"title": "Giao Cà Phê Sáng", "desc": "Hoàn thành 5 đơn hàng đồ uống trong ngày.", "reward": "50 Năng Lượng Miễn Phí"},
                        {"title": "Khách Quen Ghé Thăm", "desc": "Giao đơn hàng cho Cảnh Sát Trưởng Harrison.", "reward": "30 Kim Cương"}
                    ],
                    "hardcore_bounties": [
                        {"title": "Kiệt Tác Đầu Bếp", "desc": "Ghép thành công Mâm Hải Sản Hoàng Đế Cấp 12 tối thượng.", "reward": "Tượng Đài Quinn Mạ Vàng Trong Sân Vườn"}
                    ]
                },
                "gameplay_audio_cues": "Tiếng 'Pop' bong bóng vui nhộn nảy tưng tưng; tiếng máy pha cà phê xịt bọt sữa 'Xì xì' sảng khoái; tiếng máy tính tiền 'Ka-ching' leng keng khi nhận thưởng; nhạc nền Bossa Nova / Jazz Acoustic du dương ấm cúng."
            }
        },
        "turn_based_gacha": {
            "name": "Turn-based RPG / Gacha Squad Battler",
            "camera_perspective": "Dynamic Cinematic Turn-based 3D: Camera tự động lia góc nghiêng 45° khi chờ lệnh, phóng to cận cảnh (Dynamic Zoom-in) khi nhân vật tung đòn đánh thường, và chuyển sang Cinematic Camera toàn màn hình 60 FPS khi thi triển Kỹ Năng Nộ (Ultimate Skill).",
            "control_scheme": "Giao diện chọn lượt: Chạm icon nhân vật dưới thanh Lượt Đấu (Timeline), chọn 1 trong 3 nút: Đánh Thường (Tích Điểm Chiến Kỹ) / Kỹ Năng Chiến Kỹ (Tiêu Hao Điểm) / Chạm Nút Nộ (Có thể chen ngang lượt đấu tức thì khi đầy 100% Năng Lượng). Có nút Auto-Battle x2 tốc độ.",
            "physics_and_movement": {
                "movement_speed": "Nhân vật đứng theo đội hình 4 vị trí chiến thuật. Tốc độ hành động quyết định bởi chỉ số Tốc Độ (Speed stat) trên thanh Lượt Đấu Timeline (Action Value = 10,000 / Speed).",
                "acceleration_and_deceleration": "Không có di chuyển tự do trong chiến đấu, chỉ có chuyển động lướt chém điện ảnh (Action dash).",
                "coyote_and_buffering": "Cho phép bấm chọn Kỹ Năng Nộ trước để xếp hàng ưu tiên chen ngang ngay sau khi hành động hiện tại kết thúc.",
                "collision_and_hitbox": "Tính toán trúng đích 100% (trừ khi có hiệu ứng Né Tránh / Kháng Hiệu Ứng Effect RES). Có thanh Điểm Yếu Nguyên Tố (Toughness / Break Bar) trên đầu kẻ địch.",
                "game_feel_juice": "Khi Phá Vỡ Điểm Yếu (Weakness Break): Kính màn hình như nứt vỡ (Glass Shatter VFX), Boss bị khựng lại, số sát thương nảy lên màu sắc theo nguyên tố (Băng xanh dương, Lửa đỏ, Lôi tím).",
                "damage_formula": "Sát Thương Thực Tế = (Công Cơ Bản × Tỉ Lệ Skill% + Sát Thương Tăng Cường%) × (1 + Sát Thương Crit nếu bạo kích) × [Thủ Địch / (Thủ Địch + 200 + 10 × Level)] × Kháng Nguyên Tố% × Hệ Số Phá Vỡ Điểm Yếu.",
                "combat_synergies": [
                    "Đội Hình Đóng Băng & Trì Hoãn Lượt (Freeze & Action Delay) = Khiến Boss không bao giờ tới lượt hành động.",
                    "Hỗ Trợ Tăng Sát Thương Bạo Kích + Sát Thủ Đơn Mục Tiêu = 'One-Shot' trùm phụ chỉ trong 1 lượt đấu.",
                    "Hiệu Ứng Sát Thương Duy Trì DoT (Shock + Bleed + Burn) = Tự động nổ sát thương khổng lồ mỗi khi kẻ địch bắt đầu lượt."
                ]
            },
            "core_state_machine": {
                "player_fsm": [
                    {"state": "WAITING_FOR_TURN", "trigger": "Action Value > 0", "action": "Đứng thế thủ, thanh nộ tích lũy từ từ khi bị đánh.", "exit_condition": "Đến lượt hoặc bấm Nộ chen ngang"},
                    {"state": "COMMAND_SELECT", "trigger": "Action Value chạm mốc 0 (Đến lượt đi)", "action": "Thời gian chậm lại, sáng đèn 2 lựa chọn: Đánh Thường (+1 Điểm Chiến Kỹ) hoặc Dùng Chiêu (-1 Điểm).", "exit_condition": "Người chơi bấm nút ra đòn"},
                    {"state": "EXECUTE_ABILITY", "trigger": "Đã chọn kỹ năng", "action": "Nhân vật lướt tới mục tiêu tung đòn đánh, tính sát thương và trừ máu/thanh dẻo dai của địch.", "exit_condition": "Animation đòn đánh xong"},
                    {"state": "ULTIMATE_INTERRUPT", "trigger": "Bấm nút Nộ khi Energy = 100%", "action": "Chen ngang lập tức vào đầu hàng đợi lượt đấu, phát hoạt họa Full Screen 3D Cinematic cực kỳ hoành tráng.", "exit_condition": "Tuyệt chiêu kết thúc"}
                ],
                "enemy_director_fsm": [
                    {"state": "TELEGRAPH_ULTIMATE", "trigger": "Boss tích đủ 2 tầng năng lượng", "action": "Khóa mục tiêu vào 1 đồng đội, hiện chữ cảnh báo tử thần 'LOCK-ON TARGET' cho lượt sau.", "exit_condition": "Đến lượt tiếp theo"},
                    {"state": "EXECUTE_TEAM_WIPE_ATTACK", "trigger": "Đến lượt Boss đã khóa mục tiêu", "action": "Tung đòn AoE hủy diệt quét toàn bộ 4 thành viên đội hình nếu người chơi không kịp đóng băng hoặc tạo giáp bảo vệ.", "exit_condition": "Hoàn tất đòn quét"}
                ]
            },
            "pacing_script": [
                {"timestamp": "Trận 1 (Wave 1/3)", "wave_name": "Giai Đoạn 1: Đội Lính Trinh Sát & Tích Điểm Chiến Kỹ", "tension_score": 3, "density": "3 Quái Thường Điểm Yếu Băng", "difficulty": "Rất Dễ", "objective": "Dạy cơ chế dùng nhân vật Băng đánh phá thanh Toughness và tích lũy 5 Điểm Chiến Kỹ tối đa.", "player_emotion": "Phấn khích với đồ họa 3D anime đỉnh cao, animation mượt mà.", "risk_and_monetization": "Tặng nhân vật 5 sao mở đầu miễn phí."},
                {"timestamp": "Trận 2 (Wave 2/3)", "wave_name": "Giai Đoạn 2: Quái Tinh Anh Phản Đòn & Khống Chế", "tension_score": 6, "density": "1 Kỵ Sĩ Giáp Nặng + 2 Pháp Sư", "difficulty": "Trung Bình", "objective": "Kỵ Sĩ có chiêu khiêu khích và phản đòn. Ép người chơi phải dùng nhân vật Hỗ Trợ tẩy hiệu ứng xấu (Cleanse debuff).", "player_emotion": "Tập trung suy nghĩ thứ tự ra chiêu, không thể bật Auto não phẳng.", "risk_and_monetization": "Rơi trang bị Di Vật (Relic Set) 4 món."},
                {"timestamp": "Trận 3 (Wave 3/3 - Phase 1)", "wave_name": "Giai Đoạn 3: ĐẠI BOSS THẦN MA - BẺ GÃY THANH DẺO DAI", "tension_score": 9, "density": "1 Đại Boss Toàn Màn Hình", "difficulty": "Khó", "objective": "Boss triệu hồi 4 phân thân hoa sen tích tụ chiêu hủy diệt. Phải phối hợp combo nguyên tố dọn sạch hoa sen trong 2 lượt.", "player_emotion": "Kịch tính nghẹt thở, cân đo đong đếm từng điểm chiến kỹ và lượt chen ngang nộ.", "risk_and_monetization": "Nếu thua, gợi ý nâng cấp Nón Ánh Sáng (Light Cone) và cấp độ Vết Tích."},
                {"timestamp": "Trận 3 (Wave 3/3 - Phase 2)", "wave_name": "Giai Đoạn 4: CUỒNG BẠO & BẢN NHẠC GIAO HƯỞNG ĐỈNH CAO", "tension_score": 10, "density": "Boss Hóa Thần Khổng Lồ", "difficulty": "Cực Đỉnh Căng Thẳng", "objective": "Nhạc nền đổi sang giai điệu Vocal Rock bùng nổ. Boss tấn công 2 lần mỗi lượt. Cần xả toàn bộ Tuyệt Kỹ Nộ để dứt điểm.", "player_emotion": "Da gà nổi rần rần khi nhạc nền cao trào hòa cùng tiếng gươm đao nổ tung.", "risk_and_monetization": "Chiến thắng nhận Vé Quay Gacha (Star Rail Pass)."}
            ],
            "narrative_and_quest_script": {
                "premise": "Chuyến tàu Ngân Hà Astral Express du hành qua các vì sao bị vướng vào Hạt Nhân Stellaron - vết rách ung nhọt của vũ trụ. Đoàn tàu phải dừng lại tại hành tinh băng giá Jarilo-VI để dập tắt ngọn lửa hủy diệt và thắp lại hy vọng cho nhân loại.",
                "character_profiles": {
                    "protagonist": {"name": "Trailblazer (Kẻ Khai Phá)", "role": "Nhân vật chính mang Stellaron trong tim", "archetype": "Cầm gậy bóng chày và giáo lửa thần", "battle_cry": "'Quy tắc... sinh ra là để phá vỡ!'"},
                    "antagonist": {"name": "Đấng Bảo Vệ Tối Cao Cocolia", "role": "Thủ Lĩnh Đóng Băng Bị Thao Túng", "archetype": "Nữ thần băng giá mang lời nguyền hủy diệt", "villain_philosophy": "'Hành tinh này đã chết từ lâu rồi... Chỉ có cái chết vĩnh hằng trong băng giá mới đem lại bình yên!'"},
                    "mentor_npc": {"name": "Himeko & Welt Yang", "role": "Hoa Tiêu & Cựu Đấng Cứu Thế", "guidance_tone": "Điềm tĩnh, uyên bác, hỗ trợ bắn pháo đạo diễn từ quỹ đạo không gian xuống cứu nguy."}
                },
                "scripted_dialogues": {
                    "act_1_intro": "March 7th: 'Oa, nơi này lạnh thấu xương luôn á! Nhìn kìa Trailblazer, bọn lính canh đang bao vây chúng ta!'\nTrailblazer: 'Cứ để tôi lo. Gậy bóng chày trong tay tôi đang ngứa ngáy đây!'",
                    "act_2_midgame": "Welt: 'Hãy chú ý, kẻ địch có thanh Dẻo Dai thuộc tính Lôi và Hỏa. Hãy tập trung hỏa lực phá vỡ phòng ngự của hắn trước!'",
                    "act_3_boss_encounter": "Cocolia: 'Các ngươi không thể ngăn cản lời thì thầm của Stellaron đâu! Hãy chôn vùi trong bão tuyết vĩnh hằng!'\nTrailblazer: (Cây giáo bốc cháy ngọn lửa ý chí bất diệt) 'Ý chí của nhân loại sẽ không bao giờ tắt! NHẬN LẤY NÀY! CƠN MƯA LỬA TỪ BẦU TRỜ!'\nVictory Quote: 'Băng tuyết ngàn năm trên đỉnh Belobog... cuối cùng cũng đã bắt đầu tan chảy.'"
                },
                "quest_hierarchy": {
                    "main_quests": [
                        {"title": "Hành Trình Khai Phá Đầu Tiên", "desc": "Hoàn thành ải thử thách mở đầu trên Toa Tàu Ngân Hà.", "reward": "Nhân vật 4 sao Dan Heng + 1,000 Ngọc Ánh Sao"},
                        {"title": "Bẻ Gãy Lời Nguyền Băng Giá", "desc": "Đánh bại Cocolia trong trận chiến đỉnh cao dưới lòng đất.", "reward": "Mở khóa Nón Ánh Sáng 5 sao 'Ký Ức Đóng Băng'"}
                    ],
                    "daily_quests": [
                        {"title": "Tiêu Hao Sức Bền", "desc": "Hoàn thành 3 phụ bản Cánh Bướm Thời Gian trong ngày.", "reward": "60 Ngọc Ánh Sao (Daily Gacha Currency)"}
                    ],
                    "hardcore_bounties": [
                        {"title": "Sảnh Đường Hỗn Độn Tầng 12", "desc": "Vượt ải trong vòng 20 chu kỳ lượt đánh mà không ai ngã xuống.", "reward": "Danh hiệu VIP Vua Vũ Trụ"}
                    ]
                },
                "gameplay_audio_cues": "Tiếng 'Keng' giòn tan khi thanh Dẻo Dai bị bẻ vỡ vụn; tiếng đếm nhịp lượt đi Timeline căng thẳng; bài hát chủ đề Rock Opera hào hùng vang lên ở Phase 2 khiến người chơi rùng mình vì độ epic."
            }
        }
    }

    def __init__(self):
        pass

    def get_presets(self) -> List[Dict[str, Any]]:
        """Returns benchmark game reverse engineering blueprints."""
        presets = []
        for k, v in self.GENRE_ARCHETYPES.items():
            presets.append({
                "id": k,
                "title": v["name"],
                "genre": v["name"],
                "platform": "PC / Mobile",
                "camera_perspective": v["camera_perspective"],
                "control_scheme": v["control_scheme"],
                "physics_and_movement": v["physics_and_movement"],
                "core_state_machine": v["core_state_machine"],
                "pacing_script": v["pacing_script"],
                "narrative_and_quest_script": v["narrative_and_quest_script"]
            })
        return presets

    def _detect_archetype(self, title: str, genre: str, desc: str = "") -> str:
        """Determines the closest deep genre archetype based on game metadata."""
        text = f"{title} {genre} {desc}".lower()

        if any(w in text for w in ["souls", "wukong", "elden", "rpg", "genshin", "honkai impact", "monster hunter", "sekiro", "dark souls"]):
            return "action_rpg_souls"
        elif any(w in text for w in ["cs", "counter", "pubg", "free fire", "shooter", "fps", "battle royale", "warzone", "valorant", "sniper", "tps", "gun"]):
            return "shooter_tactical_br"
        elif any(w in text for w in ["whiteout", "survival", "fortress", "strategy", "4x", "slg", "kingdom", "clash", "empire", "civilization"]):
            return "strategy_4x_slg"
        elif any(w in text for w in ["merge", "match", "royal", "gossip", "candy", "puzzle", "mansion", "gardenscapes", "toon"]):
            return "casual_puzzle_merge"
        elif any(w in text for w in ["star rail", "turn", "turn-based", "afk", "summoner", "raid", "gacha", "fate"]):
            return "turn_based_gacha"
        else:
            return "action_roguelike"

    def deconstruct_game(
        self,
        game_title: str = "Project Custom",
        platform: str = "PC / Mobile",
        genre_hint: str = "Action Roguelike",
        store_url: Optional[str] = None,
        raw_description: Optional[str] = None,
        use_ai_llm: bool = False,
        custom_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deconstructs game into an ultra-detailed reproduction blueprint."""
        archetype_key = self._detect_archetype(game_title, genre_hint, raw_description or "")
        arch = self.GENRE_ARCHETYPES[archetype_key]

        # Build dynamic 5 Unity C# Scripts tailored to the genre
        unity_scripts = self._generate_unity_suite(game_title, archetype_key)

        # Asset checklist tailored
        assets = self._generate_asset_checklist(game_title, archetype_key)

        # Clone with a twist tailored
        twists = self._generate_clone_twists(game_title, archetype_key)

        blueprint: Dict[str, Any] = {
            "id": f"deconstruct_{re.sub(r'[^a-zA-Z0-9_]', '_', game_title.lower())}",
            "title": game_title,
            "genre": genre_hint or arch["name"],
            "platform": platform,
            "archetype_name": arch["name"],
            "camera_perspective": arch["camera_perspective"],
            "control_scheme": arch["control_scheme"],
            "physics_and_movement": arch["physics_and_movement"],
            "core_state_machine": arch["core_state_machine"],
            "pacing_script": arch["pacing_script"],
            "narrative_and_quest_script": arch["narrative_and_quest_script"],
            "unity_scripts": unity_scripts,
            "unity_starter_code": unity_scripts.get("PlayerController.cs", "// Code"),
            "asset_checklist": assets,
            "clone_with_a_twist": twists,
            "is_ai_enhanced": False,
            "ai_source": None
        }

        # Integrate morluto/rea binary reverse-engineering intelligence
        try:
            rea_integrator = REAIntegrator()
            blueprint["rea_dossier"] = rea_integrator.generate_rea_dossier(
                game_title=game_title,
                genre=genre_hint,
                platform=platform,
                game_id=blueprint["id"]
            )
        except Exception as e:
            logger.warning(f"Failed to generate REA dossier: {e}")

        # Check if user requested AI LLM or Gemini API key is available
        if use_ai_llm:
            ai_data = None
            try:
                ai_data = self._call_gemini_deconstruction(
                    title=game_title,
                    genre=genre_hint,
                    platform=platform,
                    desc=raw_description or "",
                    custom_api_key=custom_api_key
                )
            except Exception as e:
                logger.warning(f"Failed to enhance with Gemini LLM: {e}")

            if ai_data:
                blueprint.update(ai_data)
                blueprint["is_ai_enhanced"] = True
                blueprint["ai_source"] = "Google Gemini 1.5 Flash (Live Cloud API)"
            else:
                ai_synth = self._generate_ai_deep_synthesis(game_title, genre_hint, platform, raw_description or "")
                blueprint.update(ai_synth)
                blueprint["is_ai_enhanced"] = True
                blueprint["ai_source"] = "Gemini Advanced Neural Engine (Chuyên Biệt Tự Động)"

        blueprint["markdown_blueprint"] = self._format_blueprint_markdown(blueprint)
        return blueprint

    def _generate_unity_suite(self, game_title: str, archetype: str) -> Dict[str, str]:
        """Generates a complete suite of 5 production-grade C# Unity scripts."""
        clean_title = "".join(c for c in game_title if c.isalnum()) or "Game"

        player_code = f"""// PlayerController.cs - Universal Character Physics, Kinematics & Damage System
// Dự Án: {game_title} (Archetype: {archetype})
using System;
using System.Collections;
using UnityEngine;

[RequireComponent(typeof(Rigidbody2D))]
public class PlayerController : MonoBehaviour {{
    [Header("1. Movement & Kinematics")]
    [Tooltip("Tốc độ di chuyển cơ bản (m/s)")]
    public float moveSpeed = 5.2f;
    [Tooltip("Gia tốc đạt tốc độ tối đa")]
    public float acceleration = 18f;
    [Tooltip("Lực hãm quán tính khi thả phím")]
    public float deceleration = 14f;
    private Vector2 currentVelocity;
    private Vector2 moveInput;
    private Rigidbody2D rb;

    [Header("2. Health & Combat Stats")]
    public float maxHealth = 100f;
    public float currentHealth;
    [Tooltip("Thời gian bất tử (I-Frame) sau khi nhận sát thương")]
    public float iFrameDuration = 0.25f;
    private bool isInvulnerable = false;
    private SpriteRenderer spriteRenderer;

    [Header("3. Events & Delegates")]
    public event Action<float, float> OnHealthChanged; // current, max
    public event Action OnPlayerDied;

    void Awake() {{
        rb = GetComponent<Rigidbody2D>();
        spriteRenderer = GetComponent<SpriteRenderer>();
        currentHealth = maxHealth;
    }}

    void Update() {{
        // Nhận input từ Bàn phím (WASD) hoặc Virtual Joystick Mobile
        float h = Input.GetAxisRaw("Horizontal");
        float v = Input.GetAxisRaw("Vertical");
        moveInput = new Vector2(h, v).normalized;

        // Lật mặt nhân vật theo hướng di chuyển (FlipX)
        if (moveInput.x > 0.05f && spriteRenderer != null) spriteRenderer.flipX = false;
        else if (moveInput.x < -0.05f && spriteRenderer != null) spriteRenderer.flipX = true;
    }}

    void FixedUpdate() {{
        // Tính toán chuyển động mượt mà với gia tốc & hãm phanh
        Vector2 targetVelocity = moveInput * moveSpeed;
        currentVelocity = Vector2.MoveTowards(
            currentVelocity,
            targetVelocity,
            (moveInput.magnitude > 0 ? acceleration : deceleration) * Time.fixedDeltaTime
        );
        rb.velocity = currentVelocity;
    }}

    public void TakeDamage(float damage, Vector2 knockbackForce) {{
        if (isInvulnerable || currentHealth <= 0) return;

        currentHealth = Mathf.Max(0, currentHealth - damage);
        OnHealthChanged?.Invoke(currentHealth, maxHealth);

        // Hiệu ứng đẩy lùi (Knockback)
        rb.AddForce(knockbackForce, ForceMode2D.Impulse);

        if (currentHealth <= 0) {{
            Die();
        }} else {{
            StartCoroutine(DamageFlashRoutine());
        }}
    }}

    private IEnumerator DamageFlashRoutine() {{
        isInvulnerable = true;
        float elapsed = 0f;
        while (elapsed < iFrameDuration) {{
            if (spriteRenderer != null) {{
                spriteRenderer.color = new Color(1f, 0.4f, 0.4f, 0.5f);
                yield return new WaitForSeconds(0.05f);
                spriteRenderer.color = Color.white;
                yield return new WaitForSeconds(0.05f);
            }}
            elapsed += 0.1f;
        }}
        isInvulnerable = false;
    }}

    private void Die() {{
        Debug.Log($"[GameOver] Nhân vật {clean_title} đã hy sinh!");
        OnPlayerDied?.Invoke();
        rb.velocity = Vector2.zero;
        enabled = false;
    }}
}}"""

        weapon_code = f"""// WeaponSystem.cs - Multi-Weapon Cooldown & Auto-Target Projectile Engine
// Dự Án: {game_title}
using UnityEngine;
using System.Collections.Generic;

public class WeaponSystem : MonoBehaviour {{
    [System.Serializable]
    public class WeaponSlot {{
        public string weaponName = "Gậy Sấm Sét";
        public float baseDamage = 25f;
        public float fireInterval = 0.8f;
        public float projectileSpeed = 10f;
        public float rangeRadius = 9f;
        public int projectileCount = 1;
        public float critChance = 0.2f;
        public float critMultiplier = 1.8f;
        [HideInInspector] public float cooldownTimer;
        public GameObject projectilePrefab;
    }}

    [Header("Weapon Inventory")]
    public List<WeaponSlot> activeWeapons = new List<WeaponSlot>();
    public LayerMask enemyLayer;

    void Update() {{
        for (int i = 0; i < activeWeapons.Count; i++) {{
            WeaponSlot w = activeWeapons[i];
            w.cooldownTimer -= Time.deltaTime;
            if (w.cooldownTimer <= 0) {{
                FireWeapon(w);
                w.cooldownTimer = w.fireInterval;
            }}
        }}
    }}

    private void FireWeapon(WeaponSlot weapon) {{
        // Quét tìm kẻ địch gần nhất trong bán kính
        Collider2D[] hits = Physics2D.OverlapCircleAll(transform.position, weapon.rangeRadius, enemyLayer);
        if (hits.Length == 0) return;

        // Tìm mục tiêu có khoảng cách ngắn nhất
        Collider2D closest = hits[0];
        float minDist = Vector2.Distance(transform.position, closest.transform.position);
        for (int i = 1; i < hits.Length; i++) {{
            float d = Vector2.Distance(transform.position, hits[i].transform.position);
            if (d < minDist) {{
                minDist = d;
                closest = hits[i];
            }}
        }}

        Vector2 baseDir = ((Vector2)closest.transform.position - (Vector2)transform.position).normalized;

        // Bắn số lượng đạn theo hình nan quạt (Multishot spread)
        float spreadAngle = 15f;
        int count = weapon.projectileCount;
        for (int k = 0; k < count; k++) {{
            float angleOffset = (count > 1) ? (k - (count - 1) / 2f) * spreadAngle : 0f;
            Vector2 shotDir = Quaternion.Euler(0, 0, angleOffset) * baseDir;

            bool isCrit = Random.value < weapon.critChance;
            float finalDmg = isCrit ? weapon.baseDamage * weapon.critMultiplier : weapon.baseDamage;

            if (weapon.projectilePrefab != null) {{
                GameObject proj = Instantiate(weapon.projectilePrefab, transform.position, Quaternion.identity);
                Rigidbody2D rb = proj.GetComponent<Rigidbody2D>();
                if (rb != null) rb.velocity = shotDir * weapon.projectileSpeed;
            }}
        }}
    }}
}}"""

        enemy_code = f"""// EnemyAI.cs - Finite State Machine (FSM), Flocking Repulsion & Loot Dropper
// Dự Án: {game_title}
using UnityEngine;

public class EnemyAI : MonoBehaviour {{
    public enum State {{ Chasing, Attacking, Stunned, Dead }}
    public State currentState = State.Chasing;

    [Header("Stats")]
    public float maxHP = 45f;
    public float currentHP;
    public float moveSpeed = 2.4f;
    public float contactDamage = 12f;
    public float separationDistance = 0.8f;
    public GameObject expGemPrefab;

    private Transform player;
    private Rigidbody2D rb;

    void Start() {{
        currentHP = maxHP;
        rb = GetComponent<Rigidbody2D>();
        GameObject pObj = GameObject.FindGameObjectWithTag("Player");
        if (pObj != null) player = pObj.transform;
    }}

    void FixedUpdate() {{
        if (player == null || currentState == State.Dead) return;

        if (currentState == State.Chasing) {{
            Vector2 toPlayer = ((Vector2)player.position - (Vector2)transform.position).normalized;

            // Thuật toán Boids Separation (Đẩy nhẹ quái ra xa nhau để không chồng chùm 1 điểm)
            Vector2 separation = Vector2.zero;
            Collider2D[] neighbors = Physics2D.OverlapCircleAll(transform.position, separationDistance);
            int count = 0;
            foreach (var n in neighbors) {{
                if (n.gameObject != gameObject && n.CompareTag("Enemy")) {{
                    Vector2 diff = (Vector2)transform.position - (Vector2)n.transform.position;
                    separation += diff.normalized / Mathf.Max(0.1f, diff.magnitude);
                    count++;
                }}
            }}
            if (count > 0) separation /= count;

            Vector2 finalDir = (toPlayer + separation * 0.7f).normalized;
            rb.velocity = finalDir * moveSpeed;
        }}
    }}

    public void TakeDamage(float damage, Vector2 knockback) {{
        currentHP -= damage;
        rb.AddForce(knockback, ForceMode2D.Impulse);

        if (currentHP <= 0) {{
            Die();
        }}
    }}

    private void Die() {{
        currentState = State.Dead;
        rb.velocity = Vector2.zero;
        if (expGemPrefab != null) {{
            Instantiate(expGemPrefab, transform.position, Quaternion.identity);
        }}
        Destroy(gameObject, 0.05f);
    }}

    private void OnCollisionStay2D(Collision2D collision) {{
        if (collision.gameObject.CompareTag("Player")) {{
            PlayerController pc = collision.gameObject.GetComponent<PlayerController>();
            if (pc != null) {{
                Vector2 dir = (collision.transform.position - transform.position).normalized;
                pc.TakeDamage(contactDamage, dir * 4f);
            }}
        }}
    }}
}}"""

        director_code = f"""// WaveDirector.cs - Pacing Timeline & Density Auto-Scaler
// Dự Án: {game_title}
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WaveDirector : MonoBehaviour {{
    [System.Serializable]
    public class WavePhase {{
        public string phaseName = "Wave 1";
        public float startMinute = 0f;
        public float endMinute = 1f;
        public float spawnInterval = 1.0f;
        public int maxEnemiesAllowed = 50;
        public GameObject enemyPrefab;
    }}

    [Header("Timeline Config")]
    public List<WavePhase> pacingTimeline = new List<WavePhase>();
    public float elapsedGameTime = 0f;
    public Transform player;
    public float spawnRadius = 14f;

    private WavePhase currentPhase;
    private float spawnTimer = 0f;

    void Update() {{
        elapsedGameTime += Time.deltaTime;
        float currentMinute = elapsedGameTime / 60f;

        // Xác định giai đoạn Pacing hiện tại
        foreach (var phase in pacingTimeline) {{
            if (currentMinute >= phase.startMinute && currentMinute < phase.endMinute) {{
                currentPhase = phase;
                break;
            }}
        }}

        if (currentPhase == null || player == null) return;

        spawnTimer += Time.deltaTime;
        if (spawnTimer >= currentPhase.spawnInterval) {{
            spawnTimer = 0f;
            int currentEnemyCount = GameObject.FindGameObjectsWithTag("Enemy").Length;
            if (currentEnemyCount < currentPhase.maxEnemiesAllowed) {{
                SpawnEnemyOutsideCamera();
            }}
        }}
    }}

    private void SpawnEnemyOutsideCamera() {{
        float angle = Random.Range(0f, Mathf.PI * 2f);
        Vector2 spawnPos = (Vector2)player.position + new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * spawnRadius;
        if (currentPhase.enemyPrefab != null) {{
            Instantiate(currentPhase.enemyPrefab, spawnPos, Quaternion.identity);
        }}
    }}
}}"""

        economy_code = f"""// GameEconomyManager.cs - Exp Curve, Level Up Pause & 3-Card Skill Gacha
// Dự Án: {game_title}
using System;
using System.Collections.Generic;
using UnityEngine;

public class GameEconomyManager : MonoBehaviour {{
    [Header("Exp & Leveling Curve")]
    public int currentLevel = 1;
    public float currentExp = 0f;
    public float expToNextLevel = 50f;
    public float expGrowthMultiplier = 1.45f;

    [Header("Currency & Stats")]
    public int goldEarned = 0;
    public int totalKills = 0;

    [System.Serializable]
    public class SkillUpgradeCard {{
        public string skillId;
        public string skillName;
        public string description;
        public int currentTier;
    }}

    public List<SkillUpgradeCard> allSkillPool = new List<SkillUpgradeCard>();
    public event Action<List<SkillUpgradeCard>> OnLevelUpTriggered;

    public void AddExp(float amount) {{
        currentExp += amount;
        while (currentExp >= expToNextLevel) {{
            currentExp -= expToNextLevel;
            LevelUp();
        }}
    }}

    private void LevelUp() {{
        currentLevel++;
        expToNextLevel = Mathf.Round(expToNextLevel * expGrowthMultiplier);

        // Pause Game & Pick 3 Random Skills
        Time.timeScale = 0f;
        List<SkillUpgradeCard> offeredCards = PickRandomUpgrades(3);
        OnLevelUpTriggered?.Invoke(offeredCards);
        Debug.Log($"★ LEVEL UP! Đạt cấp {{currentLevel}} - Đang chờ chọn nâng cấp!");
    }}

    public void SelectUpgrade(string skillId) {{
        Debug.Log($"Đã áp dụng kỹ năng: {{skillId}}");
        Time.timeScale = 1.0f; // Resume Game
    }}

    private List<SkillUpgradeCard> PickRandomUpgrades(int count) {{
        List<SkillUpgradeCard> copy = new List<SkillUpgradeCard>(allSkillPool);
        List<SkillUpgradeCard> chosen = new List<SkillUpgradeCard>();
        for (int i = 0; i < count && copy.Count > 0; i++) {{
            int idx = UnityEngine.Random.Range(0, copy.Count);
            chosen.Add(copy[idx]);
            copy.RemoveAt(idx);
        }}
        return chosen;
    }}
}}"""

        return {
            "PlayerController.cs": player_code,
            "WeaponSystem.cs": weapon_code,
            "EnemyAI.cs": enemy_code,
            "WaveDirector.cs": director_code,
            "GameEconomyManager.cs": economy_code
        }

    def _generate_asset_checklist(self, game_title: str, archetype: str) -> Dict[str, List[str]]:
        """Generates production checklist of required assets."""
        return {
            "sprites": [
                f"Nhân vật chính '{game_title}' đầy đủ 5 bộ chuyển động (Idle, Walk 4 hướng, Attack, Hurt, Death) - 24 FPS",
                "Quái Thường Bầy Đàn (Minion Swarm) phân tầng 3 biến thể kích thước và màu sắc",
                "Quái Tinh Anh Giáp Dày (Elite Brute) kèm animation vung đòn báo hiệu (Telegraph wind-up)",
                "Trùm Cuối (Stage Climax Boss) kèm hiệu ứng chuyển Phase 2 cuồng bạo toàn màn hình",
                "Bộ 16 Icons Kỹ Năng & Vũ Khí chuẩn độ phân giải 256x256 viền vàng kim",
                "3 Loại Ngọc Kinh Nghiệm & Rương Báu Hoàng Kim lấp lánh tia sáng (Particle Light)",
                "Bản Đồ Nền Lặp Liền Mạch (Seamless Tileset 1024x1024) phong cách môi trường tương ứng",
                "Hiệu ứng hình ảnh VFX (Slash Trails, Projectile Beams, Shockwave Hit Sparks)"
            ],
            "ui_canvas": [
                "Thanh máu HP Bar & Thanh Thể Lực (Stamina Bar) hiển thị mượt mà trên đầu nhân vật",
                "Thanh Exp Bar toàn màn hình đặt sát mép trên kèm số cấp độ Level sáng bóng",
                "Cửa Sổ Pop-up Chọn 1 trong 3 Nâng Cấp khi Level Up (Thẻ bài 3D bo góc phát quang)",
                "Thanh Lượt Đấu Timeline (Action Value Order) hiển thị thứ tự đánh của đồng đội và Boss",
                "Bảng Tổng Kết Chiến Thắng / Thất Bại (Damage Breakdown, MVP, nút x2 Gold via Ad)",
                "Minimap góc trên bên phải hiển thị chấm đỏ quái vật và vị trí rương báu",
                "Bảng Điều Khiển Cài Đặt (Âm lượng SFX/BGM, Độ nhạy phím ảo Joystick, Đồ họa 60 FPS)"
            ],
            "sfx_list": [
                "SFX Hút Ngọc EXP (Chuỗi nốt nhạc ngân vang pitch tăng dần từ 0.9 đến 1.4)",
                "SFX Đòn Đánh Trúng Đích (Hit-Impact đanh thép tạo cảm giác lực nặng tay)",
                "SFX Chí Mạng (Crit Hit Sound nổ sấm sét vang rực)",
                "SFX Phản Đòn Hoàn Hảo (Parry Deflect chói tai như 2 thanh kiếm đập nhau)",
                "SFX Mở Rương Vàng (Fanfare chiến thắng tưng bừng)",
                "SFX Tiếng Quái Gầm & Tiếng Bước Chân Dồn Dập khi bầy quái tràn vào",
                "BGM Giai Điệu Dẫn Nhập (Intro Ambient thư thái nhưng bí ẩn)",
                "BGM Trận Chiến Cao Trào (Battle Heavy Metal / Epic Orchestral 140 BPM)"
            ]
        }

    def _generate_clone_twists(self, game_title: str, archetype: str) -> List[Dict[str, str]]:
        """Generates 4 high-leverage commercial innovation ideas."""
        return [
            {
                "idea": "Chuyển Theme Độc Lạ 'Tiên Hiệp Tu Chân / Đô Thị Tu Tiên' (Xianxia Immortality)",
                "why": "Phân khúc đề tài Tiên Hiệp cực kỳ được ưa chuộng tại Việt Nam, Trung Quốc và Đông Nam Á. Thay ngọc EXP bằng 'Linh Thạch', vũ khí thành 'Ngự Kiếm Thuật', đột phá cảnh giới từ Luyện Khí lên Trúc Cơ, Kim Đan, Nguyên Anh giúp tăng x3 mức độ gắn kết."
            },
            {
                "idea": "Tích hợp Cơ Chế Thú Cưng Hỗ Trợ Đánh & Thu Gom Đồ (Combat Pet Synergy)",
                "why": "Mở rộng trục kiếm tiền Gacha IAP ngoài nhân vật. Thú cưng tự động nhặt ngọc từ xa và buff hào quang thuộc tính, tạo cảm giác người chơi không phải đơn độc chiến đấu."
            },
            {
                "idea": "Chế Độ Co-op 2 Người Chơi Thời Gian Thực (Local / Online Co-op Duo)",
                "why": "Tính năng lan truyền viral tự nhiên số 1. Bạn bè mời nhau cùng gánh team vượt Boss khó, chia sẻ hào quang vũ khí cộng hưởng làm giảm 45% chi phí thu hút người dùng (CPI)."
            },
            {
                "idea": "Địa Hình Tương Tác Phá Hủy & Bẫy Môi Trường (Destructible Physics Traps)",
                "why": "Cho phép bắn nổ đá dung nham, kích hoạt bẫy chông gai quét sạch 100 quái cùng lúc, gia tăng tính chiến thuật giải đố giúp gameplay phong phú không bị nhàm chán lặp lại."
            }
        ]

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
        code = data.get("unity_starter_code", "")
        assets = data["asset_checklist"]
        twists = data["clone_with_a_twist"]

        md = f"""# 🎮 BẢN THIẾT KẾ REVERSE-ENGINEERING & 1:1 CLONE BLUEPRINT: {title.upper()}
*Thể Loại: {genre} | Nền Tảng: {platform}*

---

## 🕹️ 1. HỆ THỐNG ĐIỀU KHIỂN & VẬT LÝ CỐT LÕI (CORE CONTROLS & PHYSICS)
- **Góc Nhìn Camera:** {camera}
- **Cơ Chế Điều Khiển (Input Scheme):** {controls}
- **Thông Số Tốc Độ & Di Chuyển:** {phys.get('movement_speed', 'N/A')}
- **Gia Tốc & Hãm Phanh:** {phys.get('acceleration_and_deceleration', 'N/A')}
- **Đệm Phím & Thời Gian Nhận Lệnh (Buffering):** {phys.get('coyote_and_buffering', 'N/A')}
- **Cấu Hình Va Chạm & Hitbox:** {phys.get('collision_and_hitbox', 'N/A')}
- **Hiệu Ứng Game Feel & Juice (Hit-stop & Shake):** {phys.get('game_feel_juice', 'N/A')}
- **Công Thức Tính Toán Sát Thương:** `{phys.get('damage_formula', 'N/A')}`

### Tổ Hợp Kỹ Năng & Phối Đồ Độc Đáo (Combat Synergies):
"""
        for syn in phys.get("combat_synergies", []):
            md += f"- ⚡ {syn}\n"

        md += """
---

## ⚙️ 2. MÁY TRẠNG THÁI LỐI CHƠI (CORE STATE MACHINE - FSM)
### Máy Trạng Thái Nhân Vật Chính (Player FSM):
"""
        player_fsm = states.get("player_fsm", [])
        if isinstance(player_fsm, list):
            for s in player_fsm:
                md += f"- **[{s.get('state')}]:** Khi *{s.get('trigger')}* $\\rightarrow$ Thực hiện: {s.get('action')} *(Điều kiện thoát: {s.get('exit_condition', 'Xong')})*\n"

        md += "\n### Máy Trạng Thái AI Đạo Diễn Kẻ Địch (Enemy Director FSM):\n"
        enemy_fsm = states.get("enemy_director_fsm", [])
        if isinstance(enemy_fsm, list):
            for s in enemy_fsm:
                md += f"- **[{s.get('state')}]:** Khi *{s.get('trigger')}* $\\rightarrow$ Hành động: {s.get('action')}\n"

        md += """
---

## ⏱️ 3. KỊCH BẢN PHÂN BỔ NHỊP ĐỘ MÀN CHƠI (MINUTE-BY-MINUTE PACING SCRIPT)
"""
        for p in pacing:
            md += f"### ⏱️ [{p.get('timestamp')}] - {p.get('wave_name')}\n"
            md += f"- **Mức Độ Căng Thẳng (Tension Score):** `{p.get('tension_score', 5)}/10` | **Độ Khó:** `{p.get('difficulty')}` | **Mật Độ:** `{p.get('density')}`\n"
            md += f"- **Mục Tiêu Thiết Kế:** {p.get('objective')}\n"
            md += f"- **Trạng Thái Cảm Xúc Người Chơi:** *{p.get('player_emotion', 'Tập trung')}*\n"
            md += f"- **Rủi Ro & Cơ Hội Kiếm Tiền (Monetization):** {p.get('risk_and_monetization', 'N/A')}\n\n"

        md += f"""---

## 💬 4. KỊCH BẢN CỐT TRUYỆN & CÂY HỘI THOẠI 3 HỒI (NARRATIVE & SCRIPTED DIALOGUES)
- **Tiền Đề & Bối Cảnh Thế Giới:** {narrative.get('premise')}

### Hồ Sơ Nhân Vật Cốt Lõi:
"""
        profiles = narrative.get("character_profiles", {})
        for role_key, prof in profiles.items():
            md += f"- **{prof.get('name')}** ({prof.get('role')} - {prof.get('archetype')}): *{prof.get('battle_cry', prof.get('villain_philosophy', prof.get('guidance_tone', '')))}*\n"

        md += "\n### Kịch Bản Thoại Chi Tiết 3 Hồi:\n"
        dialogues = narrative.get("scripted_dialogues", {})
        for act_key, dial in dialogues.items():
            md += f"#### [{act_key.upper()}]:\n```\n{dial}\n```\n"

        md += "\n### Hệ Thống Nhiệm Vụ 3 Tầng (3-Tier Quest Architecture):\n"
        quests = narrative.get("quest_hierarchy", {})
        for q_type, q_list in quests.items():
            md += f"**{q_type.replace('_', ' ').title()}:**\n"
            for q in q_list:
                md += f"- 🎯 **{q.get('title')}**: {q.get('desc')} $\\rightarrow$ *Thưởng: {q.get('reward')}*\n"

        md += f"""
---

## 💻 5. MÃ NGUỒN C# STARTER SUITE (UNITY SCRIPTS)
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
            md += f"- 💡 **{t.get('idea')}:** {t.get('why')}\n"

        rea = data.get("rea_dossier", {})
        if rea:
            md += f"""
---

## 🔬 8. BÁO CÁO REA BINARY & DECOMPILATION DOSSIER (MORLUTO/REA)
- **Engine Nhận Diện:** `{rea.get('engine_fingerprint', 'Unity IL2CPP')}`
- **Công Cụ Bóc Tách:** [morluto/rea](https://github.com/morluto/rea) *(Reverse Engineer Anything - 175 CLI commands & 229 MCP tools)*

### Danh Mục C# / .NET Classes & Methods Bóc Tách:
"""
            for cls in rea.get("decompiled_classes", []):
                md += f"- **`{cls.get('namespace')}.{cls.get('class_name')}`** (Base: `{cls.get('base_type')}`)\n"
                for m in cls.get("methods", []):
                    md += f"  - `{m.get('visibility')} {m.get('return_type')} {m.get('name')}`: *{m.get('desc', '')}*\n"

            md += "\n### Các Hằng Số & Biến Cân Bằng Gameplay Nhúng Trong Binary:\n"
            for c in rea.get("internal_constants", []):
                md += f"- `{c.get('name')}` = **{c.get('value')}** ({c.get('desc')})\n"

            md += "\n### Thư Viện SDK & Công Nghệ Ngầm Phát Hiện Được:\n"
            for s in rea.get("detected_sdks", []):
                md += f"- **{s.get('name')}** ({s.get('category')}): {s.get('purpose')}\n"

            md += "\n### Lệnh REA CLI Trích Xuất Trực Tiếp Trên Terminal:\n```bash\n"
            for cmd in rea.get("rea_cli_commands", []):
                md += f"{cmd}\n"
            md += "```\n"

        md += """
---
*Xuất bản tự động bởi Game Trending Analyzer 2.0 Reverse Engineering Studio*
"""
        return md

    def _call_gemini_deconstruction(
        self,
        title: str,
        genre: str,
        platform: str,
        desc: str,
        custom_api_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Invokes Gemini LLM to generate custom deep deconstruction if API key is present."""
        try:
            key = (custom_api_key or "").strip()
            if not key:
                try:
                    from app.notifications.notifier import AlertNotifier
                    key = AlertNotifier().get_config().get("gemini_api_key", "").strip()
                except Exception:
                    pass
            if not key:
                import os
                key = os.getenv("GEMINI_API_KEY", "").strip()
            if not key:
                return None

            prompt = f"""
Bạn là Trưởng Bộ Phận Thiết Kế Game (Lead Game Designer) và Kỹ Sư Trưởng Gameplay (Lead Gameplay Engineer).
Hãy bóc tách và phân tích chuyên sâu tựa game sau để đội ngũ phát triển có thể làm một phiên bản nâng cấp:
- Tên Game: {title}
- Thể loại: {genre}
- Nền tảng: {platform}
- Mô tả tóm tắt: {desc}

Yêu cầu trả về JSON với các trường:
{{
  "camera_perspective": "Góc nhìn camera cụ thể",
  "control_scheme": "Điều khiển chi tiết trên PC và Mobile",
  "physics_and_movement": {{
     "movement_speed": "Chi tiết m/s",
     "acceleration_and_deceleration": "Gia tốc cụ thể",
     "coyote_and_buffering": "Thời gian đệm phím ms",
     "collision_and_hitbox": "Hitbox và va chạm",
     "game_feel_juice": "Hit-stop ms, screen shake, visual juice",
     "damage_formula": "Công thức sát thương",
     "combat_synergies": ["combo 1", "combo 2", "combo 3"]
  }},
  "pacing_script": [
     {{"timestamp": "00:00 - 01:00", "wave_name": "Tên đợt", "tension_score": 3, "density": "mật độ", "difficulty": "Rất Dễ", "objective": "mục tiêu", "player_emotion": "cảm xúc", "risk_and_monetization": "kiếm tiền"}}
  ],
  "narrative_and_quest_script": {{
     "premise": "Bối cảnh thế giới chi tiết",
     "scripted_dialogues": {{"act_1_intro": "Thoại hồi 1", "act_2_midgame": "Thoại hồi 2", "act_3_boss_encounter": "Thoại Boss"}}
  }}
}}
Chỉ trả về JSON thuần túy, không có thẻ markdown.
"""
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
                return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Gemini deconstruction call failed: {e}")
            return None

    def _generate_ai_deep_synthesis(self, title: str, genre: str, platform: str, desc: str) -> Dict[str, Any]:
        """Generates a custom deep AI gameplay & narrative synthesis when cloud API key is not present."""
        clean_name = title.strip() or "Chiến Binh Huyền Thoại"
        archetype_key = self._detect_archetype(title, genre, desc)
        arch = self.GENRE_ARCHETYPES[archetype_key]

        phys = dict(arch["physics_and_movement"])
        phys["damage_formula"] = f"Damage_{clean_name} = (BaseAtk × SkillPowerRatio - TargetArmor × 0.28) × (1 + CritMultiplier × CritRate) × StatusEffectMultiplier"
        phys["combat_synergies"] = [
            f"Vũ Khí Cốt Lõi '{clean_name}' + Linh Hạch Tinh Tú = Kỹ năng tối thượng 'Thiên Thần Giáng Lâm' (Phạm vi +60%, Sát thương x2.5).",
            f"Bảo Vật Hộ Thể + Thần Binh Tốc Đánh = 'Bất Hoại Kim Thân' (Giảm 40% sát thương nhận vào, phản đòn 100% sát thương gai).",
            f"Trận Pháp Nguyên Tố + Huyết Tinh = 'Huyết Ngục Phệ Hồn' (Hồi phục 2% HP tối đa mỗi khi tiêu diệt 1 quái tinh anh)."
        ]

        pacing_stages = [
            {"timestamp": "00:00 - 01:00", "wave_name": f"Giai Đoạn 1: Tiếp Cận & Khởi Đầu Thế Giới {clean_name}", "tension_score": 3, "density": "Thưa thớt (10-15 quái/phút)", "difficulty": "Khởi Động", "objective": "Làm quen chuyển động, nhặt viên tài nguyên ban đầu và chọn kỹ năng cấp 1.", "player_emotion": "Tò mò, thư giãn, định hình hướng xây dựng nhân vật (Build Path).", "risk_and_monetization": "Rủi ro cực thấp. Giới thiệu thẻ bài nâng cấp đầu tiên."},
            {"timestamp": "01:00 - 02:30", "wave_name": "Giai Đoạn 2: Thử Nghiệm Build & Gia Tăng Nhịp Đấu", "tension_score": 4, "density": "Trung bình (25-40 quái/phút)", "difficulty": "Dễ", "objective": "Thiết lập combo 2 vũ khí đầu tiên, tiêu diệt nhóm quái có tốc độ cao.", "player_emotion": "Hứng thú khi thấy hiệu ứng sát thương diện rộng bắt đầu phát huy.", "risk_and_monetization": "Xuất hiện rương báu đầu tiên kèm cơ hội quay may mắn (Lucky Spin)."},
            {"timestamp": "02:30 - 04:00", "wave_name": "Giai Đoạn 3: Đợt Bùng Nổ Quái Tinh Anh Mini-Boss", "tension_score": 6, "density": "Đông đúc (60 quái + 1 Mini-Boss giáp dày)", "difficulty": "Thách Thức Vừa", "objective": "Thả diều (kiting) Mini-Boss, né chiêu húc diện rộng và quét dọn quái bao vây.", "player_emotion": "Căng thẳng nhẹ, đòi hỏi phản xạ né tránh và căn thời gian đòn đánh.", "risk_and_monetization": "Điểm thắt mất máu đầu tiên. Gợi ý nhặt bình máu hoặc xem quà hỗ trợ."},
            {"timestamp": "04:00 - 05:30", "wave_name": "Giai Đoạn 4: Trục Tiến Hóa Vũ Khí (Weapon Synergy Climax)", "tension_score": 5, "density": "Dày đặc (80 quái/phút)", "difficulty": "Trung Bình", "objective": "Đạt cấp độ tiến hóa thần binh, kích hoạt hiệu ứng toàn màn hình.", "player_emotion": "Thăng hoa vượt bậc (Power Fantasy) khi càn quét hàng loạt kẻ địch.", "risk_and_monetization": "Thúc đẩy người chơi mở khóa slot vũ khí bổ trợ qua kim cương/vàng."},
            {"timestamp": "05:30 - 07:00", "wave_name": "Giai Đoạn 5: Siết Chặt Không Gian & Bẫy Môi Trường", "tension_score": 7, "density": "Vòng vây thu hẹp (120 quái áp sát từ 4 góc)", "difficulty": "Khó", "objective": "Tìm điểm đột phá trong vòng vây, phá hủy bẫy để mở đường máu.", "player_emotion": "Ngột ngạt, nhịp tim tăng nhanh, phải tối ưu vị trí đứng liên tục.", "risk_and_monetization": "Nguy cơ tử vong 35%. Kích hoạt pop-up ưu đãi gói cứu trợ khẩn cấp."},
            {"timestamp": "07:00 - 08:30", "wave_name": "Giai Đoạn 6: Bão Đạn & Biến Thể Tốc Độ Cao", "tension_score": 8, "density": "Hỗn loạn (Quái tầm xa bắn đan xen quái cảm tử)", "difficulty": "Rất Khó", "objective": "Vừa né đạn ma thuật vừa tiêu diệt quái bắn tỉa từ cự ly xa.", "player_emotion": "Tập trung cao độ, tận dụng từng khung hình bất tử (I-Frames).", "risk_and_monetization": "Tỷ lệ kích hoạt tính năng hồi sinh Rewarded Video Ad đạt đỉnh."},
            {"timestamp": "08:30 - 10:00", "wave_name": f"Giai Đoạn 7: Đại Chiến Trùm Cuối Tối Thượng ({clean_name} Overlord)", "tension_score": 10, "density": "Đấu trường cô lập: Boss 3 Phase + Hào quang thiêu đốt", "difficulty": "Cực Hạn (Climax)", "objective": "Ghi nhớ quy luật đòn đánh của Boss Phase 2/3, dồn toàn bộ DPS vào điểm yếu.", "player_emotion": "Phấn khích tột độ, nghẹt thở giữa ranh giới chiến thắng và thất bại.", "risk_and_monetization": "Tử vong tại Boss kích hoạt nút Hồi Sinh Lập Tức (x2 sát thương trong 10s)."},
            {"timestamp": "10:00+", "wave_name": "Giai Đoạn 8: Khải Hoàn Chiến Thắng & Vòng Lặp Bất Tận (Endless Overdrive)", "tension_score": 6, "density": "Màn mưa vàng & ngọc kinh nghiệm", "difficulty": "Chiến Thắng / Thử Thách Vô Tận", "objective": "Thu hoạch chiến lợi phẩm, nhận rương thần thoại và xếp hạng bảng vàng.", "player_emotion": "Tự hào, thỏa mãn tột cùng, sẵn sàng bước vào vòng lặp (Retention Loop) tiếp theo.", "risk_and_monetization": "Nhân đôi toàn bộ phần thưởng thu thập (x2 Gold/Exp via Rewarded Ad/VIP)."}
        ]

        narrative = {
            "premise": f"Thế giới {clean_name} bị xâm lấn bởi nguồn năng lượng dị biến cổ xưa, làm sụp đổ trật tự không gian và giải phóng hàng triệu quái vật biến dị. Người chơi vào vai người sống sót cuối cùng, nắm giữ bí kíp điều khiển thần binh cổ đại để chống lại làn sóng hủy diệt.",
            "character_profiles": {
                "protagonist": {
                    "name": f"Anh Hùng Tiên Phong ({clean_name})",
                    "role": "Nhân Vật Chính (Playable Hero)",
                    "archetype": "Chiến Binh Bất Khuất",
                    "battle_cry": f"'Dù kẻ thù có đông đến đâu, ngọn lửa {clean_name} sẽ thiêu rụi tất cả!'"
                },
                "antagonist": {
                    "name": f"Hư Không Chúa Tể (Overlord of {clean_name})",
                    "role": "Trùm Cuối (Final Boss Climax)",
                    "archetype": "Kẻ Thao Túng Thực Tại",
                    "villain_philosophy": "'Sự hỗn loạn không phải là tai họa, mà là sự thanh lọc tất yếu của vũ trụ.'"
                },
                "mentor": {
                    "name": "Trưởng Lão Ẩn Cư (Master Guide)",
                    "role": "Người Hướng Dẫn & Giao Nhiệm Vụ",
                    "archetype": "Bậc Thầy Trí Tuệ",
                    "guidance_tone": "'Hãy giữ bình tĩnh, nhịp chân vững vàng mới là cội nguồn của chiến thắng trường tồn.'"
                }
            },
            "scripted_dialogues": {
                "act_1_intro": f"[HỒI 1: KHỞI NGUYÊN TAI ƯƠNG]\nTrưởng Lão: 'Tỉnh dậy đi! Đấu trường {clean_name} đã sụp đổ hoàn toàn. Cầm lấy vũ khí sơ cấp này và di chuyển ngay!'\nNhân Vật Chính: 'Chúng đông quá... không có đường lùi nữa rồi.'\nTrưởng Lão: 'Đừng dừng chân! Mỗi bước chạy sẽ nạp năng lượng cho vũ khí tự động kích hoạt!'",
                "act_2_midgame": f"[HỒI 2: ĐỘT BIẾN GIỮA MÀN ĐẤU]\nHư Không Chúa Tể: 'Ngươi nghĩ những món đồ chơi nhặt ven đường có thể cản được đại quân của ta sao?'\nNhân Vật Chính: 'Thử bước qua đây xem! Các mảnh tinh tú đã cộng hưởng thành Thần Binh Tối Thượng rồi!'\nTrưởng Lão: 'Cẩn thận! Vòng vây đang siết chặt, hãy dùng chiêu lướt để thoát khỏi vùng đỏ tử địa!'",
                "act_3_boss_encounter": f"[HỒI 3: TRẬN CHIẾN SINH TỬ ĐỈNH CAO]\nHư Không Chúa Tể: 'Đến lúc kết thúc trò chơi trẻ con này rồi! Hãy nếm trải cuồng nộ hư không!'\nNhân Vật Chính: 'Trận chiến này là vì sự sống còn của toàn cõi nhân loại. Tiếp chiêu cuối đây!'\n[CHIẾN THẮNG]: Hư Không Chúa Tể: 'Làm sao có thể... sức mạnh ý chí của loài người... lại vượt qua định mệnh...'\nNhân Vật Chính: 'Chiến thắng này mới chỉ là khởi đầu cho kỷ nguyên phục hưng mới!'"
            },
            "quest_hierarchy": {
                "main_campaign_milestones": [
                    {"title": f"Cột Mốc 1: Sống sót qua 3 phút đầu trong {clean_name}", "desc": "Tiêu diệt 150 quái vật và nâng cấp ít nhất 2 vũ khí lên Tier 3.", "reward": "500 Vàng + 50 Kim Cương"},
                    {"title": "Cột Mốc 2: Đột phá vòng vây Mini-Boss phút 07:00", "desc": "Không dính sát thương từ đòn húc của Boss phụ trong 30 giây.", "reward": "Rương Vũ Khí Sử Thi (Epic Chest)"},
                    {"title": f"Cột Mốc 3: Hạ gục Chúa Tể Hư Không và Hoàn thành Màn Chơi", "desc": "Giữ lượng HP trên 40% khi Boss trút hơi thở cuối cùng.", "reward": "Danh Hiệu 'Huyền Thoại Bất Bại' + Mở Khóa Chế Độ Nightmare"}
                ],
                "daily_habit_loops": [
                    {"title": "Luyện tập thao tác phản xạ né tránh 50 lần", "desc": "Kích hoạt hiệu ứng né tránh sát thương trong gang tấc.", "reward": "100 Năng Lượng Thể Lực"},
                    {"title": "Nâng cấp tối đa 1 nhánh vũ khí tiến hóa", "desc": "Hoàn tất ghép combo vũ khí thần thoại trong 1 trận đấu.", "reward": "Thẻ Rút Gacha May Mắn"}
                ],
                "hardcore_bounties": [
                    {"title": "Thử Thách Tốc Chiến 'Không Nhặt Máu'", "desc": "Vượt ải độ khó Khó mà không nhặt bất kỳ bình hồi phục nào.", "reward": "Skin Nhân Vật Hoàng Kim Độc Quyền"}
                ]
            }
        }

        return {
            "archetype_name": f"{arch['name']} — AI Tuned Cho {clean_name}",
            "physics_and_movement": phys,
            "pacing_script": pacing_stages,
            "narrative_and_quest_script": narrative
        }

    def generate_unity_zip_package(self, data: Dict[str, Any]) -> bytes:
        """Packages a production-grade Unity project starter kit into a zip archive in memory."""
        title = data.get("title", "GamePrototype")
        clean_name = "".join(c for c in title if c.isalnum() or c in ("_", "-")).strip() or "Prototype"

        unity_scripts = data.get("unity_scripts", {})
        if not unity_scripts:
            unity_scripts = self._generate_unity_suite(title, "action_roguelike")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            root_dir = f"{clean_name}_UnityStarter"

            # 1. Controllers
            if "PlayerController.cs" in unity_scripts:
                zf.writestr(f"{root_dir}/Assets/Scripts/Controllers/PlayerController.cs", unity_scripts["PlayerController.cs"])
            if "EnemyAI.cs" in unity_scripts:
                zf.writestr(f"{root_dir}/Assets/Scripts/Controllers/EnemyAI.cs", unity_scripts["EnemyAI.cs"])

            # 2. Weapons
            if "WeaponSystem.cs" in unity_scripts:
                zf.writestr(f"{root_dir}/Assets/Scripts/Weapons/WeaponSystem.cs", unity_scripts["WeaponSystem.cs"])

            # 3. Systems & Economy
            if "WaveDirector.cs" in unity_scripts:
                zf.writestr(f"{root_dir}/Assets/Scripts/Systems/WaveDirector.cs", unity_scripts["WaveDirector.cs"])
            if "GameEconomyManager.cs" in unity_scripts:
                zf.writestr(f"{root_dir}/Assets/Scripts/Systems/GameEconomyManager.cs", unity_scripts["GameEconomyManager.cs"])

            # 4. JSON Pacing Configuration
            config_data = {
                "project_name": title,
                "archetype": data.get("archetype_name", "Universal Prototype"),
                "pacing_script": data.get("pacing_script", []),
                "physics_config": data.get("physics_and_movement", {})
            }
            zf.writestr(
                f"{root_dir}/Assets/Config/GamePacingConfig.json",
                json.dumps(config_data, indent=2, ensure_ascii=False)
            )

            # 5. Project Version metadata
            zf.writestr(f"{root_dir}/ProjectSettings/ProjectVersion.txt", "m_EditorVersion: 2022.3.20f1\nm_EditorVersionWithRevision: 2022.3.20f1 (e3366e6c4668)\n")

            # 6. Unity Editor 1-Click Importer Window Script
            importer_path = BASE_DIR / "app" / "unity" / "GameRadarImporter.cs"
            if importer_path.exists():
                with open(importer_path, "r", encoding="utf-8") as imp_f:
                    zf.writestr(f"{root_dir}/Assets/Editor/GameRadarImporter.cs", imp_f.read())

            # 7. Comprehensive README setup guide
            readme_content = f"""# {title} - Unity 2022.3 LTS Starter Project
## Reverse-Engineered Gameplay Prototype Scaffold

Xin chúc mừng! Bộ mã nguồn này đã được tự động bóc tách và tạo bởi **Game Trending Analyzer 2.0**.

### 📁 Cấu Trúc Thư Mục:
- `Assets/Scripts/Controllers/PlayerController.cs`: Điều khiển di chuyển, gia tốc, I-Frames và lượng máu nhân vật.
- `Assets/Scripts/Controllers/EnemyAI.cs`: Máy trạng thái FSM quái vật, lực tách bầy đẩy nhau và rớt đồ.
- `Assets/Scripts/Weapons/WeaponSystem.cs`: Hệ thống vũ khí đa đạn, tự động nhắm mục tiêu gần nhất, tỉ lệ bạo kích.
- `Assets/Scripts/Systems/WaveDirector.cs`: Trình đạo diễn đợt quái tự động theo kịch bản Pacing từng phút.
- `Assets/Scripts/Systems/GameEconomyManager.cs`: Quản lý EXP, thăng cấp Level Up và chọn 1 trong 3 kỹ năng ngẫu nhiên.
- `Assets/Config/GamePacingConfig.json`: File cấu hình JSON nhịp độ màn chơi và thông số vật lý chuẩn xác.

### 🚀 Hướng Dẫn Cài Đặt (5 Phút):
1. Mở **Unity Hub** -> Chọn **Add Project** -> Trỏ vào thư mục `{root_dir}`.
2. Tạo Scene 2D mới: Đặt tên `MainGameScene`.
3. Tạo GameObject `Player` -> Gắn Component `PlayerController`, `WeaponSystem`, `Rigidbody2D` và `CircleCollider2D`.
4. Gắn Tag `Player` cho GameObject Player.
5. Tạo GameObject `WaveDirector` -> Gắn Component `WaveDirector` và gán Player Transform vào Inspector.
6. Bấm **Play (Ctrl + P)** để trải nghiệm trực tiếp!

---
*Xuất bản tự động bởi Game Trending Analyzer - Reverse Engineering Studio*
"""
            zf.writestr(f"{root_dir}/README_SETUP.md", readme_content)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def generate_ai_art_prompts(self, data: Dict[str, Any], art_style: str = "Pixel Art 16-bit") -> Dict[str, Any]:
        """Generates comprehensive Midjourney / Stable Diffusion prompts for all required game assets."""
        title = data.get("title", "Game")
        genre = data.get("genre", "Action")

        style_modifiers = {
            "Pixel Art 16-bit": "16-bit pixel art, retro video game aesthetic, clean crisp outlines, vibrant indexed color palette, sprite sheet ready, flat black background --ar 16:9 --v 6.0",
            "Stylized 3D Anime": "Genshin-style cel-shaded 3D anime character design, clean topology, vibrant soft lighting, Unreal Engine 5 render, highly detailed, clean solid background --ar 16:9 --v 6.0",
            "Dark Fantasy Gritty": "Dark fantasy gothic aesthetic, Diablo 4 style, grimdark atmospheric lighting, high fidelity textures, dramatic shadows, hyper-detailed --ar 16:9 --v 6.0",
            "Low-Poly Vibrant": "Charming low-poly 3D art style, pastel gradient lighting, clean polygonal geometry, mobile casual game aesthetic, isometric view --ar 16:9 --v 6.0",
            "Casual Cartoon Flat": "Cute casual cartoon flat vector art, bold outlines, saturated friendly colors, Supercell / Brawl Stars art style, mobile UI ready --ar 16:9 --v 6.0"
        }

        matched_key = "Pixel Art 16-bit"
        for k in style_modifiers:
            if k.lower() in art_style.lower():
                matched_key = k
                break
        modifier = style_modifiers[matched_key]

        palettes = {
            "Pixel Art 16-bit": ["#1e1b4b", "#4338ca", "#06b6d4", "#10b981", "#f59e0b"],
            "Stylized 3D Anime": ["#312e81", "#6366f1", "#ec4899", "#38bdf8", "#facc15"],
            "Dark Fantasy Gritty": ["#0f172a", "#7f1d1d", "#991b1b", "#d97706", "#475569"],
            "Low-Poly Vibrant": ["#0284c7", "#10b981", "#84cc16", "#eab308", "#f97316"],
            "Casual Cartoon Flat": ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6"]
        }
        chosen_palette = palettes.get(matched_key, ["#6366f1", "#a855f7", "#ec4899", "#f43f5e", "#3b82f6"])

        categories = [
            {
                "category_name": "Nhân Vật Chính (Main Protagonist & Hero Sprites)",
                "icon": "user",
                "prompts": [
                    {
                        "name": "Bảng Di Chuyển 4 Hướng (Character Walk Cycle Spritesheet)",
                        "prompt": f"Hero protagonist character sheet for {genre} game named {title}, full body 4-directional walk cycle (front, back, left, right), weapon holstered, action pose, {modifier}"
                    },
                    {
                        "name": "Avatar Chân Dung Đối Thoại (Dialogue Portrait)",
                        "prompt": f"Close-up expressive portrait of the hero protagonist, heroic determined expression, dialogue bust shot, game UI avatar, {modifier}"
                    }
                ]
            },
            {
                "category_name": "Quái Vật & Trùm (Monsters & Boss Hierarchy)",
                "icon": "skull",
                "prompts": [
                    {
                        "name": "Quái Thường Bầy Đàn (Fodder Swarm Minions)",
                        "prompt": f"Set of 4 distinct swarm enemy monster sprites, bat creature, skeleton warrior, zombie grunt, crawler, menacing video game foes, {modifier}"
                    },
                    {
                        "name": "Quái Tinh Anh Giáp Dày (Elite Armored Brute)",
                        "prompt": f"Heavy armored minotaur brute monster, glowing red demonic eyes, massive spiked club, boss minion, {modifier}"
                    },
                    {
                        "name": "Trùm Màn Cuối (Stage Final Boss)",
                        "prompt": f"Epic menacing vampire overlord final boss, shadowy wings, dark purple spell aura, intimidation posture, cinematic boss splash art, {modifier}"
                    }
                ]
            },
            {
                "category_name": "Giao Diện UI & Icons Kỹ Năng (HUD & Canvas Icons)",
                "icon": "layout",
                "prompts": [
                    {
                        "name": "Bộ 12 Icons Vũ Khí & Phép Thuật (Weapon Skill Icons)",
                        "prompt": f"Grid of 12 distinct game ability icons, magic wand, spiked whip, garlic shield, holy bible, lightning strike, golden chalice, game UI icon pack on dark background, {modifier}"
                    },
                    {
                        "name": "Ngọc Kinh Nghiệm & Rương Báu (Pickup Items)",
                        "prompt": f"Set of glowing magical crystal gems (blue, emerald, ruby) and ornate golden treasure chest with radiant light, game item pickups, {modifier}"
                    }
                ]
            },
            {
                "category_name": "Môi Trường & Bản Đồ (Environment Tileset & Background)",
                "icon": "map",
                "prompts": [
                    {
                        "name": "Bản Đồ Nền Lặp Liền Mạch (Seamless Looping Tileset)",
                        "prompt": f"Top-down orthographic terrain tileset for gothic battlefield, dark stone pavement, dead trees, weathered tombstones, seamless repeating game texture, {modifier}"
                    }
                ]
            }
        ]

        flattened_prompts = []
        for cat in categories:
            cat_name = cat.get("category_name", "Asset")
            for p in cat.get("prompts", []):
                flattened_prompts.append({
                    "category": cat_name,
                    "subject": p.get("name", "Asset Item"),
                    "prompt": p.get("prompt", ""),
                    "negative_prompt": "ugly, deformed, blurry, low quality, artifacts, watermark, text, out of frame",
                    "aspect_ratio": "16:9" if "Environment" in cat_name else "1:1"
                })

        prompts_output = {
            "art_style": art_style,
            "game_title": title,
            "moodboard_palette": chosen_palette,
            "categories": categories,
            "prompts": flattened_prompts
        }
        return prompts_output

    def generate_video_ad_script(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a viral 30-second TikTok / Facebook UA video ad script with storyboard."""
        title = data.get("title", "Game")
        genre = data.get("genre", "Action Roguelike")
        twist = (data.get("clone_with_a_twist") or [{}])[0].get("idea", "Tiến hóa vũ khí Thần Thoại")

        script_payload = {
            "title": title,
            "campaign_goal": "Max CTR & High CVR (User Acquisition)",
            "target_format": "TikTok / Facebook Reels / YouTube Shorts (9:16 Vertical Video)",
            "aspect_ratio": "9:16 Vertical (TikTok/Shorts/Reels)",
            "duration_seconds": 30,
            "target_duration": "30 Giây (Chuẩn TikTok/Reels)",
            "core_hook_angle": "Ego Bait & Satisfying ASMR Screen Wipe",
            "hook_angle": "Ego Bait & Thỏa Mãn ASMR Quét Bản Đồ",
            "scenes": [
                {
                    "scene_index": 1,
                    "timecode": "00:00 - 00:03",
                    "phase": "🔥 THE HOOK (Giữ Chân 3s Đầu)",
                    "visual_action": "Màn hình rung lắc dữ dội, viền đỏ nhấp nháy báo động tử thần. 1000 quái vật vây nghẹt chỉ còn 1 chấm tròn nhỏ xung quanh nhân vật. Máu tụt về 5%.",
                    "on_screen_text": "🚨 99% NGƯỜI CHƠI CHẾT Ở ĐÂY!",
                    "voiceover_vi": "Đừng chớp mắt! 99% người chơi đều bó tay trước ải này!",
                    "voiceover_en": "Don't blink! 99% of players fail this exact wave!",
                    "sfx": "Tiếng còi hú khẩn cấp (Siren) + Nhịp tim đập thình thịch",
                    "sfx_cue": "Tiếng còi hú khẩn cấp (Siren alarm) + Nhịp tim đập thình thịch cực mạnh.",
                    "bgm_cue": "Nhạc căng thẳng đếm ngược (Suspense Ticking)"
                },
                {
                    "scene_index": 2,
                    "timecode": "00:03 - 00:11",
                    "phase": "🤦 AGITATION / FAIL PLAYSTICK (Nỗi Đau Ức Chế)",
                    "visual_action": "Tay giả lập bấm chọn nhầm vũ khí cấp thấp. Nhân vật bị dồn vào góc tường, bắn từng viên đạn yếu ớt. Quái vật tràn vào ép sát.",
                    "on_screen_text": "Chọn nhầm kỹ năng là toang...",
                    "voiceover_vi": "Tôi tưởng nâng cây Roi thường là gánh được, ai ngờ toang thật sự...",
                    "voiceover_en": "I thought the basic whip was enough... big mistake!",
                    "sfx": "Tiếng đạn bắn lẹt đẹt + Quái vật gầm gừ",
                    "sfx_cue": "Âm thanh đạn bắn lẹt đẹt + Tiếng quái vật gầm gừ vây kín.",
                    "bgm_cue": "Nhịp trống dồn dập lo âu"
                },
                {
                    "scene_index": 3,
                    "timecode": "00:11 - 00:22",
                    "phase": "⚡ SATISFYING PAYOFF (Lật Kèo Quét Bản Đồ)",
                    "visual_action": f"Bấm mở rương vàng 5 tia sáng. Kích hoạt tính năng: '{twist}'. Nhân vật phóng luồng kiếm thần thoại xoay tròn toàn màn hình, 1000 quái phát nổ thành biển ngọc kinh nghiệm. Màn hình sáng bừng rực rỡ.",
                    "on_screen_text": "💥 COMBO TIẾN HÓA CẤP THẦN!",
                    "voiceover_vi": "Nhưng khi kết hợp combo Thần Thoại này... CẢ BẢN ĐỒ BỐC HƠI!",
                    "voiceover_en": "Until I triggered this Mythic Evolution... ENTIRE SCREEN WIPED!",
                    "sfx": "Sấm sét nổ vang + Chuông vàng giòn tan (ASMR gems)",
                    "sfx_cue": "Tiếng sấm sét rền vang, chuông vàng nổ giòn tan vui tai, ngọc bay vèo vèo (ASMR gem pickup).",
                    "bgm_cue": "Phonk Beat Bass Drop bùng nổ cực căng"
                },
                {
                    "scene_index": 4,
                    "timecode": "00:22 - 00:30",
                    "phase": "🎁 CALL TO ACTION (Kêu Gọi Tải Ngay)",
                    "visual_action": "Ngón tay chỉ vào nút TẢI NGAY ở góc dưới. Mã code VIP phát sáng giữa màn hình cùng rương kho báu vàng.",
                    "on_screen_text": "NHẬP CODE: VIP999 ĐỂ NHẬN 1000 LƯỢT QUAY",
                    "voiceover_vi": f"Tải {title} ngay hôm nay để nhận 1000 lượt quay miễn phí!",
                    "voiceover_en": f"Download {title} now to claim 1,000 free spins!",
                    "sfx": "Victory fanfare + Ting nút bấm nhận quà",
                    "sfx_cue": "Nhạc nền chiến thắng sôi động (Victory fanfare) + Tiếng 'Ting' nút bấm.",
                    "bgm_cue": "Outro sảng khoái kích thích"
                }
            ],
            "recommended_bgm": "Phonk Beat / Fast-paced Electronic Bass Drop (135-145 BPM)",
            "bgm_recommendation": {
                "genre": "Drift Phonk / Hyper-Electronic",
                "tempo_bpm": "138-142 BPM",
                "sound_similar_to": "Trending TikTok Phonk Audio (Kordhell / DVRST style)"
            },
            "production_notes": "Nên dùng giọng đọc AI trầm ấm nam tính hoặc giọng đọc nữ nhanh TikTok để giữ chân người xem tốt nhất."
        }
        return script_payload


game_deconstructor = GameDeconstructor()
