"""Market Culturalization (C10n) & Regulatory Compliance Scanner.

Audits mobile games for country-specific legal regulations, cultural sensitivities,
and App Store censorship guidelines across China, Japan, MENA, EU, and South Korea.
"""

from typing import Dict, Any, List, Optional

class CulturalizationScanner:
    """Regional compliance & cultural adaptation diagnostic engine."""

    def __init__(self):
        # Database of Regional Regulations & Cultural Sensitivities
        self.regional_standards = {
            "china": {
                "region_name": "Mainland China (Trung Quốc)",
                "flag": "🇨🇳",
                "app_store_gatekeeper": "NPPA (National Press and Publication Administration) & Android Third-party Stores",
                "regulatory_risk": "Cực Kỳ Cao (Extreme Legal Barrier)",
                "mandatory_requirements": [
                    {
                        "code": "CN-01",
                        "category": "Censorship / Art Assets",
                        "rule": "Nghiêm cấm hiển thị xương người (Skulls & Skeletons) và xác chết lộ thiên",
                        "severity": "REJECTION_RISK",
                        "remediation": "Thay thế quái vật bộ xương bằng người bọc giáp sắt kín mít, hoặc xác sống zombie có da thịt hoàn chỉnh."
                    },
                    {
                        "code": "CN-02",
                        "category": "Visual Violence",
                        "rule": "Cấm triệt để hiệu ứng máu đỏ văng tung tóe (Red Blood Splatter)",
                        "severity": "REJECTION_RISK",
                        "remediation": "Chuyển màu máu sang màu xanh lá cây (acid/dịch nhờn), màu tím ma thuật hoặc tắt hoàn toàn hạt particle máu."
                    },
                    {
                        "code": "CN-03",
                        "category": "Legal / Publishing License",
                        "rule": "Bắt buộc có giấy phép phát hành xuất bản số ISBN (Bản Hào)",
                        "severity": "LEGAL_BLOCKER",
                        "remediation": "Studio nước ngoài bắt buộc phải ký hợp đồng phát hành độc quyền thông qua một pháp nhân NPH nội địa Trung Quốc (như Tencent, NetEase, Bilibili)."
                    },
                    {
                        "code": "CN-04",
                        "category": "Minor Protection",
                        "rule": "Hệ thống định danh tên thật (Real-name verification) và giới hạn giờ chơi trẻ vị thành niên",
                        "severity": "MANDATORY_FEATURE",
                        "remediation": "Tích hợp SDK chống nghiện (Anti-addiction SDK) chặn người chơi dưới 18 tuổi, chỉ cho phép chơi 1 tiếng (20h-21h) vào Thứ Sáu, Thứ Bảy và Chủ Nhật."
                    }
                ]
            },
            "japan": {
                "region_name": "Japan (Nhật Bản)",
                "flag": "🇯🇵",
                "app_store_gatekeeper": "Consumer Affairs Agency (CAA) & JOGA Guidelines",
                "regulatory_risk": "Trung Bình Cao (Strict Gacha Laws)",
                "mandatory_requirements": [
                    {
                        "code": "JP-01",
                        "category": "Gacha Law",
                        "rule": "Cấm hoàn toàn cơ chế 'Kompu Gacha' (Complete Gacha)",
                        "severity": "ILLEGAL_CRIMINAL",
                        "remediation": "Nghiêm cấm cơ chế yêu cầu người chơi phải quay trúng đủ 5 món đồ/mảnh ghép khác nhau trong gacha mới được đổi phần thưởng SSR tối thượng."
                    },
                    {
                        "code": "JP-02",
                        "category": "Odds Transparency",
                        "rule": "Minh bạch tỷ lệ quay chi tiết đến 2 chữ số thập phân (Drop Rate Disclosure)",
                        "severity": "MANDATORY_COMPLIANCE",
                        "remediation": "Hiển thị nút 'Tỷ lệ chi tiết' ngay trên giao diện banner (ví dụ: SSR Rate-up 0.60%, SSR Thường 0.12% mỗi nhân vật)."
                    },
                    {
                        "code": "JP-03",
                        "category": "Virtual Currency",
                        "rule": "Luật dịch vụ thanh toán quỹ (Payment Services Act) đối với tiền ảo ingame",
                        "severity": "FINANCIAL_REGULATION",
                        "remediation": "Nếu gem trả phí không có hạn sử dụng quá 6 tháng, studio phải ký quỹ 50% tổng số dư gem chưa tiêu thụ vào ngân sách pháp lý Nhật Bản."
                    }
                ]
            },
            "mena": {
                "region_name": "Middle East / Arab (Ả Rập & Trung Đông)",
                "flag": "🇦🇪 🇸🇦",
                "app_store_gatekeeper": "GCAM (Saudi General Commission for Audiovisual Media)",
                "regulatory_risk": "Cao (Cultural & Religious Sensitivity)",
                "mandatory_requirements": [
                    {
                        "code": "ME-01",
                        "category": "UI / Localization",
                        "rule": "Giao diện và văn bản đọc từ phải sang trái (RTL - Right to Left)",
                        "severity": "USER_EXPERIENCE",
                        "remediation": "Đảo chiều bố cục UI/UX: Nút Back sang góc phải, thanh menu đảo hướng, font chữ Ả Rập hỗ trợ ligature tự nhiên."
                    },
                    {
                        "code": "ME-02",
                        "category": "Character Attire",
                        "rule": "Trang phục nhân vật nữ phải kín đáo, tránh hở ngực/eo/đùi phản cảm",
                        "severity": "CULTURAL_TABOO",
                        "remediation": "Thêm lớp vải bảo hộ (modest skins), kéo dài váy áo nhân vật nữ để phù hợp với văn hóa Hồi giáo truyền thống."
                    },
                    {
                        "code": "ME-03",
                        "category": "Gambling & Religion",
                        "rule": "Tuyệt đối cấm biểu tượng cờ bạc, xúc xắc casino và biểu tượng tôn giáo",
                        "severity": "REJECTION_RISK",
                        "remediation": "Thay hình ảnh máy xèng/xúc xắc thành rương kho báu hoặc phong ấn ma thuật. Loại bỏ biểu tượng thánh giá hay kinh thánh."
                    }
                ]
            },
            "eu": {
                "region_name": "European Union (Châu Âu)",
                "flag": "🇪🇺",
                "app_store_gatekeeper": "European Commission & PEGI Rating Board",
                "regulatory_risk": "Trung Bình (Data & Loot Box Scrutiny)",
                "mandatory_requirements": [
                    {
                        "code": "EU-01",
                        "category": "Gambling / Loot Box",
                        "rule": "Lệnh cấm cơ chế mở hòm trả phí (Paid Loot Box Ban) tại Bỉ và Hà Lan",
                        "severity": "LEGAL_BAN",
                        "remediation": "Tắt tính năng mua rương ngẫu nhiên bằng tiền thật tại khu vực BE/NL; thay bằng bán trực tiếp vật phẩm (Direct Purchase)."
                    },
                    {
                        "code": "EU-02",
                        "category": "Privacy / GDPR",
                        "rule": "Tuân thủ quyền xóa dữ liệu cá nhân (GDPR Right to be Forgotten)",
                        "severity": "LEGAL_PENALTY",
                        "remediation": "Cung cấp nút 'Xóa tài khoản vĩnh viễn' (Delete Account) có thể truy cập dễ dàng trong menu Cài đặt game."
                    }
                ]
            }
        }

    def get_all_standards(self) -> Dict[str, Any]:
        """Returns the complete compliance matrix across all covered regions."""
        return self.regional_standards

    def audit_game_compliance(
        self,
        game_title: str,
        target_regions: List[str],
        has_skeletons: bool = False,
        has_red_blood: bool = False,
        has_gacha_lootbox: bool = True,
        has_skimpy_costumes: bool = False,
        supports_rtl_arabic: bool = False
    ) -> Dict[str, Any]:
        """Audits game configuration against targeted regional standards and generates action checklist."""
        detected_risks = []
        clean_regions = []

        for reg_key in target_regions:
            reg = self.regional_standards.get(reg_key)
            if not reg:
                continue

            region_issues = []
            if reg_key == "china":
                if has_skeletons:
                    region_issues.append(reg["mandatory_requirements"][0])
                if has_red_blood:
                    region_issues.append(reg["mandatory_requirements"][1])
                # China always flags ISBN
                region_issues.append(reg["mandatory_requirements"][2])

            elif reg_key == "japan":
                if has_gacha_lootbox:
                    region_issues.append(reg["mandatory_requirements"][1])

            elif reg_key == "mena":
                if not supports_rtl_arabic:
                    region_issues.append(reg["mandatory_requirements"][0])
                if has_skimpy_costumes:
                    region_issues.append(reg["mandatory_requirements"][1])

            elif reg_key == "eu":
                if has_gacha_lootbox:
                    region_issues.append(reg["mandatory_requirements"][0])

            if region_issues:
                detected_risks.append({
                    "region_key": reg_key,
                    "region_name": reg["region_name"],
                    "flag": reg["flag"],
                    "risk_count": len(region_issues),
                    "issues": region_issues
                })
            else:
                clean_regions.append(reg["region_name"])

        # Health grade
        total_risk_points = sum(r["risk_count"] for r in detected_risks)
        if total_risk_points == 0:
            status_badge = "AN TOÀN TUYỆT ĐỐI (100% Compliant)"
            badge_color = "emerald"
        elif total_risk_points <= 2:
            status_badge = "RỦI RO THẤP - CẦN TINH CHỈNH NHẸ"
            badge_color = "indigo"
        elif total_risk_points <= 4:
            status_badge = "RỦI RO CAO - NGUY CƠ BỊ REJECT APP STORE"
            badge_color = "amber"
        else:
            status_badge = "CẢNH BÁO ĐỎ - RÀO CẢN PHÁP LÝ NẶNG"
            badge_color = "rose"

        return {
            "game_title": game_title,
            "overall_status": status_badge,
            "badge_color": badge_color,
            "total_risk_count": total_risk_points,
            "risk_breakdown": detected_risks,
            "safe_regions": clean_regions,
            "executive_summary": (
                f"Phát hiện {total_risk_points} điểm rủi ro cần xử lý trước khi nộp duyệt App Store / Google Play. "
                "Cần chuẩn bị sẵn bản build riêng (Sub-builds) cho thị trường Trung Quốc và Trung Đông."
            )
        }
