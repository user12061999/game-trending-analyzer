"""UA Ad Fraud & Click Injection Diagnostic Scanner.

Detects mobile UA attribution fraud using Mean Time To Install (MTTI / CTIT) distribution analysis:
- Click Injection (CTIT < 10s install hijacking)
- Click Flooding (Flat >24h click spamming)
- Device Farm / Bot Emulators (0% D1 retention, synthetic installs)
Calculates ad spend clawback refunds and generates custom anti-fraud rulebooks for AppsFlyer and Adjust.
"""

from typing import Dict, Any, List, Optional
import math

class AdFraudScanner:
    """Scanner for detecting attribution hijacking, click spamming, and device farms."""

    # Industry benchmarks for healthy mobile games
    HEALTHY_BENCHMARKS = {
        "mtti_under_10s_max_pct": 5.0,     # Normal healthy wifi/pre-cache < 5%
        "mtti_over_24h_max_pct": 15.0,      # High intent installs usually occur in 1-6 hours
        "d1_retention_min_pct": 28.0,       # Tier 1/2 casual game baseline
        "ctit_sweet_spot_range": "30s - 180s"
    }

    SAMPLE_NETWORKS = [
        {
            "network_name": "Suspicious-AdNet-X (Affiliate / SDK Network)",
            "total_installs": 45000,
            "ad_spend_usd": 67500.0,
            "mtti_under_10s_pct": 58.4,
            "mtti_over_24h_pct": 8.2,
            "d1_retention_pct": 14.2,
            "cpi_usd": 1.50
        },
        {
            "network_name": "SpamTraffic-DSP (Programmatic Display)",
            "total_installs": 32000,
            "ad_spend_usd": 38400.0,
            "mtti_under_10s_pct": 4.1,
            "mtti_over_24h_pct": 46.8,
            "d1_retention_pct": 11.5,
            "cpi_usd": 1.20
        },
        {
            "network_name": "BotFarm-Incentive-Co (Reward Wall Partner)",
            "total_installs": 28000,
            "ad_spend_usd": 22400.0,
            "mtti_under_10s_pct": 12.0,
            "mtti_over_24h_pct": 9.5,
            "d1_retention_pct": 1.4,
            "cpi_usd": 0.80
        },
        {
            "network_name": "Meta Ads / Apple Search Ads (Verified Clean)",
            "total_installs": 50000,
            "ad_spend_usd": 110000.0,
            "mtti_under_10s_pct": 3.2,
            "mtti_over_24h_pct": 11.0,
            "d1_retention_pct": 34.5,
            "cpi_usd": 2.20
        }
    ]

    def get_sample_networks(self) -> List[Dict[str, Any]]:
        """Returns preset benchmark networks for comparison."""
        return self.SAMPLE_NETWORKS

    def audit_network(
        self,
        network_name: str = "Custom Network",
        total_installs: int = 10000,
        mtti_under_10s_pct: float = 35.0,
        mtti_over_24h_pct: float = 20.0,
        d1_retention_pct: float = 12.0,
        ad_spend_usd: float = 15000.0,
        cpi_usd: Optional[float] = None
    ) -> Dict[str, Any]:
        """Performs comprehensive MTTI and cohort fraud diagnostics."""
        if total_installs <= 0:
            total_installs = 1000
        if ad_spend_usd <= 0:
            ad_spend_usd = 1000.0

        effective_cpi = cpi_usd if cpi_usd and cpi_usd > 0 else (ad_spend_usd / total_installs)

        # Flag specific fraud indicators
        fraud_flags = []
        fraud_score = 0.0 # Scale 0 to 100
        estimated_fraud_pct = 0.0

        # 1. Click Injection Check (CTIT < 10s)
        # Impossible to read ad, load store, download 100MB+ APK and install within 10s
        click_injection_severity = "CLEAR"
        if mtti_under_10s_pct > 30.0:
            click_injection_severity = "CRITICAL"
            fraud_score += 45.0
            excess_pct = max(0.0, mtti_under_10s_pct - self.HEALTHY_BENCHMARKS["mtti_under_10s_max_pct"])
            estimated_fraud_pct += excess_pct * 0.95
            fraud_flags.append({
                "type": "Click Injection (Install Hijacking)",
                "severity": "CRITICAL",
                "finding": f"{mtti_under_10s_pct:.1f}% lượt cài đặt có CTIT dưới 10 giây (Ngưỡng chuẩn an toàn < 5%).",
                "mechanism": "Malware hoặc SDK gian lận trên thiết bị Android theo dõi broadcast INSTALL_REFERRER và gửi click ảo ngay trước khi game cài đặt xong để cướp attribution cuối cùng từ Organic traffic.",
                "action": "Kích hoạt CTIT Reject Rule < 12 giây trên AppsFlyer/Adjust và từ chối thanh toán toàn bộ đợt cài đặt này."
            })
        elif mtti_under_10s_pct > 12.0:
            click_injection_severity = "SUSPICIOUS"
            fraud_score += 20.0
            excess_pct = max(0.0, mtti_under_10s_pct - self.HEALTHY_BENCHMARKS["mtti_under_10s_max_pct"])
            estimated_fraud_pct += excess_pct * 0.7
            fraud_flags.append({
                "type": "Click Injection (Dấu hiệu bất thường)",
                "severity": "MEDIUM",
                "finding": f"{mtti_under_10s_pct:.1f}% CTIT < 10s cao hơn mức trung bình ngành.",
                "mechanism": "Có tỷ lệ đáng ngờ các lượt cài đặt diễn ra quá nhanh so với dung lượng tải game trung bình.",
                "action": "Yêu cầu ad network đối soát Sub-Publisher ID và cung cấp log device model chi tiết."
            })

        # 2. Click Flooding / Spamming Check (CTIT > 24h)
        click_flooding_severity = "CLEAR"
        if mtti_over_24h_pct > 35.0:
            click_flooding_severity = "CRITICAL"
            fraud_score += 35.0
            excess_flood_pct = max(0.0, mtti_over_24h_pct - self.HEALTHY_BENCHMARKS["mtti_over_24h_max_pct"])
            estimated_fraud_pct += excess_flood_pct * 0.85
            fraud_flags.append({
                "type": "Click Flooding / Spamming (Bắn click ngầm)",
                "severity": "CRITICAL",
                "finding": f"{mtti_over_24h_pct:.1f}% lượt cài đặt xảy ra sau 24-72 giờ tính từ thời điểm click.",
                "mechanism": "Publisher bắn hàng triệu click ẩn (invisible iframes, background ping) dù người dùng không hề nhìn thấy ad, chực chờ user tự tải tự nhiên để nhận thưởng last-click.",
                "action": "Rút ngắn Attribution Window từ 7 ngày xuống còn 24 giờ cho network này."
            })
        elif mtti_over_24h_pct > 22.0:
            click_flooding_severity = "SUSPICIOUS"
            fraud_score += 15.0
            excess_flood_pct = max(0.0, mtti_over_24h_pct - self.HEALTHY_BENCHMARKS["mtti_over_24h_max_pct"])
            estimated_fraud_pct += excess_flood_pct * 0.5
            fraud_flags.append({
                "type": "Click Flooding (Nghi vấn phân phối chậm)",
                "severity": "MEDIUM",
                "finding": f"{mtti_over_24h_pct:.1f}% CTIT > 24h bất thường.",
                "mechanism": "Tỷ lệ chuyển đổi kéo dài nhiều ngày, dấu hiệu của việc spam click thụ động.",
                "action": "Theo dõi tỷ lệ Click-to-Install Conversion Rate (CVR); nếu CVR < 0.05% thì xác nhận là spam."
            })

        # 3. Device Farm / Emulator Bot Check (Abnormal D1 Retention Drop)
        bot_farm_severity = "CLEAR"
        if d1_retention_pct < 3.0:
            bot_farm_severity = "CRITICAL"
            fraud_score += 30.0
            estimated_fraud_pct = max(estimated_fraud_pct, 65.0)
            fraud_flags.append({
                "type": "Device Farm / Bot Emulator Traffic",
                "severity": "CRITICAL",
                "finding": f"D1 Retention tụt thảm hại chỉ còn {d1_retention_pct:.1f}% (Chuẩn game khỏe > 28%).",
                "mechanism": "Nông trại thiết bị hoặc máy ảo emulator (Nox/BlueStacks/LDPlayer) chạy script tự động cài đặt rồi gỡ app ngay sau khi trigger install event.",
                "action": "Chặn toàn bộ dải IP trung tâm dữ liệu (Datacenter IP) và Blacklist ngay danh sách Sub-site ID."
            })
        elif d1_retention_pct < 10.0:
            bot_farm_severity = "SUSPICIOUS"
            fraud_score += 15.0
            fraud_flags.append({
                "type": "Low Retention / Low Quality Incentive",
                "severity": "MEDIUM",
                "finding": f"D1 Retention {d1_retention_pct:.1f}% thấp hơn chuẩn, người chơi rời bỏ ngay ngày đầu.",
                "mechanism": "Traffic có thể là Incentive trả thưởng tiền mặt hoặc bot nông trại cày coin.",
                "action": "Cắt giảm 50% ngân sách và đặt điều kiện thanh toán theo Cost-Per-Event (CPE)."
            })

        # Cap scores and compute financial impact
        fraud_score = min(100.0, max(0.0, fraud_score))
        estimated_fraud_pct = min(92.0, max(0.0, estimated_fraud_pct))

        fraud_installs_count = int(total_installs * (estimated_fraud_pct / 100.0))
        estimated_clawback_usd = round(fraud_installs_count * effective_cpi, 2)
        safe_spend_usd = round(ad_spend_usd - estimated_clawback_usd, 2)

        overall_verdict = (
            "🚨 FRAUD NGUY HIỂM CAO (Cần Khiếu Nại Hoàn Tiền Ngay)" if fraud_score >= 50
            else ("⚠️ NGUY CƠ TRUNG BÌNH (Cần Audit Chặt & Đặt Rule)" if fraud_score >= 25
            else "✅ AN TOÀN / SẠCH (Traffic Hợp Lệ)")
        )

        # Generate custom anti-fraud rulebook
        rulebook = self._generate_anti_fraud_rulebook(
            network_name,
            mtti_under_10s_pct,
            mtti_over_24h_pct,
            d1_retention_pct
        )

        # MTTI histogram distribution estimation for visualization
        # Estimated buckets: 0-10s, 10-30s, 30-180s (Healthy), 3-12h, 12-24h, >24h
        hist_0_10 = mtti_under_10s_pct
        hist_gt_24 = mtti_over_24h_pct
        remaining = max(0.0, 100.0 - (hist_0_10 + hist_gt_24))
        hist_10_30 = round(remaining * 0.18, 1)
        hist_30_180 = round(remaining * 0.52, 1) # Normal bell peak
        hist_3_12 = round(remaining * 0.20, 1)
        hist_12_24 = round(remaining * 0.10, 1)

        return {
            "network_name": network_name,
            "metrics": {
                "total_installs": total_installs,
                "effective_cpi_usd": round(effective_cpi, 2),
                "ad_spend_usd": ad_spend_usd,
                "mtti_under_10s_pct": mtti_under_10s_pct,
                "mtti_over_24h_pct": mtti_over_24h_pct,
                "d1_retention_pct": d1_retention_pct
            },
            "audit_verdict": {
                "fraud_score": fraud_score,
                "overall_verdict": overall_verdict,
                "estimated_fraud_pct": round(estimated_fraud_pct, 1),
                "fraud_installs_count": fraud_installs_count,
                "estimated_clawback_usd": estimated_clawback_usd,
                "safe_spend_usd": safe_spend_usd
            },
            "fraud_flags": fraud_flags,
            "mtti_distribution": [
                {"bucket": "0s - 10s (Click Injection Risk)", "pct": hist_0_10, "status": "danger" if hist_0_10 > 10 else "normal"},
                {"bucket": "10s - 30s (Fast WiFi/Pre-cache)", "pct": hist_10_30, "status": "normal"},
                {"bucket": "30s - 180s (Healthy Organic Peak)", "pct": hist_30_180, "status": "healthy"},
                {"bucket": "3h - 12h (Delayed Play)", "pct": hist_3_12, "status": "normal"},
                {"bucket": "12h - 24h (Long Consideration)", "pct": hist_12_24, "status": "warning" if hist_12_24 > 15 else "normal"},
                {"bucket": ">24h (Click Flooding Risk)", "pct": hist_gt_24, "status": "danger" if hist_gt_24 > 25 else "normal"}
            ],
            "rulebook": rulebook
        }

    def _generate_anti_fraud_rulebook(
        self,
        network_name: str,
        mtti_under_10s: float,
        mtti_over_24h: float,
        d1_retention: float
    ) -> Dict[str, Any]:
        """Generates ready-to-paste anti-fraud configuration policies for AppsFlyer and Adjust."""
        return {
            "appsflyer_protect360_rules": [
                {
                    "rule_name": f"P360-Block-ClickInjection-{network_name.split()[0]}",
                    "condition": "CTIT < 12 seconds",
                    "action": "Reject attribution & re-attribute to Organic traffic",
                    "reason": "Mean Time To Install below 12s violates physical download limits."
                },
                {
                    "rule_name": f"P360-Attribution-Window-{network_name.split()[0]}",
                    "condition": "Click-Through Attribution Window > 24 Hours",
                    "action": "Shorten window to 12 Hours",
                    "reason": "Prevents passive click spamming attribution theft."
                },
                {
                    "rule_name": "P360-Device-Integrity",
                    "condition": "Google Play Protect / Device Integrity Check == FAILED",
                    "action": "Auto-Reject and flag publisher ID",
                    "reason": "Blocks rooted devices and emulator scripts."
                }
            ],
            "adjust_fraud_prevention_suite": [
                {
                    "filter_name": "Click Injection Filter (Android Broadcast)",
                    "threshold": "Ignore clicks occurring while app installation is already in progress (after INSTALL_REFERRER broadcast).",
                    "status": "ENFORCED"
                },
                {
                    "filter_name": "Click Spamming Outlier Filter",
                    "threshold": "Cap publisher click volume if Click-to-Install Rate drops below 0.08%.",
                    "status": "ENFORCED"
                },
                {
                    "filter_name": "D1 Retention Compliance Threshold",
                    "threshold": f"Auto-pause sub-campaigns if D1 retention falls below 15.0% after 200 installs.",
                    "status": "ACTIVE"
                }
            ],
            "clawback_email_template": f"""Kính gửi Đội ngũ Quản lý Đối tác {network_name},

Qua hệ thống kiểm toán phân bổ (MMP Attribution Audit) cho chiến dịch mobile app của chúng tôi, chúng tôi phát hiện tỷ lệ bất thường nghiêm trọng vi phạm chính sách chống gian lận:
- Tỷ lệ CTIT < 10 giây (Click Injection signature): {mtti_under_10s:.1f}%
- Tỷ lệ CTIT > 24 giờ (Click Flooding signature): {mtti_over_24h:.1f}%
- D1 Retention thực tế: {d1_retention:.1f}%

Theo điều khoản hợp đồng Master Service Agreement (MMP Invalid Traffic Policy), chúng tôi yêu cầu:
1. Loại bỏ toàn bộ các lượt cài đặt gian lận được gắn cờ khỏi hóa đơn thanh toán kỳ này.
2. Hoàn lại số tiền chi tiêu gian lận ước tính (Clawback Refund).
3. Cung cấp danh sách Sub-Publisher ID để đưa vào Blacklist vĩnh viễn.

Trân trọng,
Game Growth & User Acquisition Team"""
        }
