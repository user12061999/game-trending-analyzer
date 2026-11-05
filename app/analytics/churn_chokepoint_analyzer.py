"""Choke-Point & Churn Diagnostic Lab.

Analyzes player early-journey drop-off funnels (FTUE), identifies difficulty rage-quit walls,
and calculates dynamic Emergency Rescue Pack triggers to rescue D1 retention and convert Minnows.
"""

from typing import Dict, Any, List, Optional

class ChurnChokepointAnalyzer:
    """Diagnostic system for player onboarding drop-offs and rage-quit choke points."""

    def __init__(self):
        # Benchmark Funnel Conversion Rates (Median Top 25% Mobile Games)
        self.benchmark_funnel = [
            {"step": 1, "id": "store_install", "name": "1. Store Page -> App Install", "benchmark_survival_pct": 100.0, "risk_factor": "Dung lượng game > 200MB tải bằng 4G"},
            {"step": 2, "id": "first_launch_patch", "name": "2. Khởi Động & Tải Resource Patch", "benchmark_survival_pct": 88.0, "risk_factor": "Tải data in-app quá chậm hoặc không có mini-game giải trí"},
            {"step": 3, "id": "account_auth", "name": "3. Đăng Nhập / Chơi Ngay (Guest Mode)", "benchmark_survival_pct": 82.0, "risk_factor": "Bắt buộc đăng ký tài khoản phức tạp, không có nút Chơi Nhanh"},
            {"step": 4, "id": "tutorial_ftue", "name": "4. Hoàn Thành Màn Hướng Dẫn (FTUE)", "benchmark_survival_pct": 74.0, "risk_factor": "Tutorial quá dài dòng, cấm người chơi tự do bấm màn hình"},
            {"step": 5, "id": "early_flow_levels", "name": "5. Chuỗi Ải Đầu (Level 1-1 -> 1-3)", "benchmark_survival_pct": 65.0, "risk_factor": "Thiếu dopamine thưởng lớn trong 5 phút đầu tiên"},
            {"step": 6, "id": "boss_chokepoint", "name": "6. Ải Thử Thách Boss Đầu Tiên (Choke-Point)", "benchmark_survival_pct": 52.0, "risk_factor": "TƯỜNG ĐỘ KHÓ (Paywall) - Tỷ lệ thua > 60% gây Rage-Quit"},
            {"step": 7, "id": "d1_retention", "name": "7. Quay Lại Ngày Hôm Sau (D1 Return)", "benchmark_survival_pct": 42.0, "risk_factor": "Hết thể lực (Energy) hoặc không có quà chờ mở hôm sau"}
        ]

    def diagnose_player_funnel(
        self,
        install_count: int = 10000,
        patch_download_pass_pct: float = 85.0,
        tutorial_complete_pct: float = 70.0,
        chokepoint_boss_win_pct: float = 40.0,
        consecutive_losses_to_quit: int = 3
    ) -> Dict[str, Any]:
        """Diagnoses custom studio funnel drop-offs against industry benchmarks."""
        # Calculate actual flow
        users_after_patch = int(install_count * (patch_download_pass_pct / 100.0))
        users_after_tutorial = int(install_count * (tutorial_complete_pct / 100.0))
        users_at_chokepoint = int(users_after_tutorial * 0.85)
        users_beating_chokepoint = int(users_at_chokepoint * (chokepoint_boss_win_pct / 100.0))
        users_rage_quit = users_at_chokepoint - users_beating_chokepoint

        # Projected D1 Retention
        projected_d1_pct = round((users_beating_chokepoint / max(1, install_count)) * 100 * 0.9, 1)

        # Choke-point severity
        if chokepoint_boss_win_pct < 45.0:
            severity = "BÁO ĐỘNG ĐỎ: TƯỜNG ĐỘ KHÓ GÂY GỠ GAME (Rage-Quit Wall)"
            badge_color = "rose"
            diagnosis = "Hơn 55% người chơi bị kẹt và thua cuộc tại ải Boss đầu tiên. Tâm lý ức chế đỉnh điểm khiến họ gỡ cài đặt (Uninstallation) thay vì nạp tiền."
        elif chokepoint_boss_win_pct < 60.0:
            severity = "CẢNH BÁO: ĐỘ KHÓ CAO VỪA PHẢI"
            badge_color = "amber"
            diagnosis = "Có độ thử thách nhưng cần cơ chế hỗ trợ mềm (xem Ads hồi sinh hoặc buff sức mạnh tạm thời)."
        else:
            severity = "AN TOÀN: ĐỘ KHÓ MƯỢT MÀ (Flow State)"
            badge_color = "emerald"
            diagnosis = "Người chơi vượt qua dễ dàng, giữ chân D1 tốt nhưng cần kiểm tra xem họ có cảm thấy quá dễ gây nhàm chán không."

        # Dynamic Rescue Pack Lifeline Proposal
        rescue_pack = {
            "trigger_condition": f"Kích hoạt sau đúng {consecutive_losses_to_quit} lần thua liên tiếp tại ải Choke-Point",
            "pack_title": "Gói Hồi Sinh Cứu Trợ Khẩn Cấp (Emergency Lifeline Pack)",
            "price_point_usd": 0.99,
            "badge_sticker": "GIẢM 400% - CHỈ CÒN 15 PHÚT",
            "contents": [
                "1 lượt Hồi Sinh Miễn Phí (Revive Token) tiếp tục trận đánh",
                "+100% Sức Mạnh & Giáp trong 1 lượt chơi kế tiếp",
                "150 Kim Cương khởi đầu",
                "Mở khóa tính năng Tự Động Chiến Đấu (Auto-Battle x2)"
            ],
            "projected_conversion_boost": "+18% Người chơi thua cuộc sẽ bấm mua gói này để vượt qua ải",
            "d1_retention_saved": f"+4.5% D1 Retention được cứu vãn từ nhóm người chơi định gỡ cài đặt"
        }

        return {
            "funnel_stages": self.benchmark_funnel,
            "custom_funnel_results": {
                "initial_installs": install_count,
                "users_survived_patch": users_after_patch,
                "users_completed_tutorial": users_after_tutorial,
                "users_reached_chokepoint": users_at_chokepoint,
                "users_conquered_chokepoint": users_beating_chokepoint,
                "users_rage_quit_at_chokepoint": users_rage_quit,
                "projected_d1_retention_pct": projected_d1_pct
            },
            "chokepoint_evaluation": {
                "boss_win_rate_pct": chokepoint_boss_win_pct,
                "severity_status": severity,
                "badge_color": badge_color,
                "diagnosis": diagnosis
            },
            "dynamic_rescue_pack": rescue_pack
        }
