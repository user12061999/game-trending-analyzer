"""Soft-Launch A/B Testing & Statistical Sample Size Calculator.

Calculates minimum required sample size per variant for soft-launch tests (D1/D7 retention, ASO CVR)
and computes two-proportion Z-test statistical significance (p-value, confidence interval).
"""

from typing import Dict, Any, List, Optional
import math

class ABTestingCalculator:
    """Statistical significance and sample size planner for mobile gaming experiments."""

    def __init__(self):
        # Soft-Launch Country Benchmarks
        self.soft_launch_countries = {
            "philippines": {"name": "Philippines (PH)", "tier": "Tier 3 English", "avg_cpi_usd": 0.28, "best_for": "Test lỗi kỹ thuật, crash rate, và độ hiểu tutorial tiếng Anh"},
            "brazil": {"name": "Brazil (BR)", "tier": "Tier 3 Volume", "avg_cpi_usd": 0.35, "best_for": "Test quy mô lớn matchmaking, PvP guild và cân bằng chỉ số nhân vật"},
            "poland": {"name": "Poland / Czech (PL/CZ)", "tier": "Tier 2 Europe", "avg_cpi_usd": 0.75, "best_for": "Test hành vi tiêu dùng tương đồng với Tây Âu với chi phí rẻ hơn 50%"},
            "canada": {"name": "Canada / Australia (CA/AU)", "tier": "Tier 1 Proxy", "avg_cpi_usd": 2.20, "best_for": "Mô phỏng 1:1 hành vi nạp IAP và Whales của thị trường Mỹ trước khi ra mắt toàn cầu"}
        }

    def calculate_required_sample_size(
        self,
        baseline_rate_pct: float = 40.0,
        expected_lift_pct: float = 3.0,
        confidence_level: float = 95.0,
        power: float = 80.0,
        country_key: str = "philippines"
    ) -> Dict[str, Any]:
        """Calculates minimum sample size per variant needed to detect expected lift."""
        p1 = baseline_rate_pct / 100.0
        p2 = (baseline_rate_pct + expected_lift_pct) / 100.0

        if p1 <= 0 or p1 >= 1 or p2 <= 0 or p2 >= 1 or p1 == p2:
            return {"error": "Tỷ lệ cơ bản hoặc mức tăng trưởng không hợp lệ"}

        # Critical values
        z_alpha = 1.96 if confidence_level == 95.0 else (2.576 if confidence_level == 99.0 else 1.645)
        z_beta = 0.842 if power == 80.0 else (1.282 if power == 90.0 else 0.674)

        p_bar = (p1 + p2) / 2.0
        delta = abs(p2 - p1)

        numerator = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = delta ** 2

        sample_per_variant = int(math.ceil(numerator / denominator))
        total_sample = sample_per_variant * 2

        # Cost estimation
        geo = self.soft_launch_countries.get(country_key, self.soft_launch_countries["philippines"])
        est_cost_usd = round(total_sample * geo["avg_cpi_usd"], 2)

        return {
            "inputs": {
                "baseline_rate_pct": baseline_rate_pct,
                "expected_lift_pct": expected_lift_pct,
                "target_rate_pct": round(p2 * 100, 1),
                "confidence_level": f"{confidence_level}%",
                "statistical_power": f"{power}%",
                "test_country": geo["name"]
            },
            "sample_size_results": {
                "sample_per_variant": sample_per_variant,
                "total_sample_needed": total_sample,
                "estimated_budget_usd": est_cost_usd,
                "country_cpi_usd": geo["avg_cpi_usd"],
                "testing_advisory": geo["best_for"]
            },
            "recommendation": (
                f"Để chứng minh mức tăng +{expected_lift_pct}% đạt độ tin cậy {confidence_level}%, "
                f"bạn cần thu thập tối thiểu {sample_per_variant:,} người chơi cho mỗi nhánh (Tổng: {total_sample:,} installs). "
                f"Nếu chạy tại {geo['name']}, ngân sách dự kiến khoảng ~${est_cost_usd:,}."
            )
        }

    def evaluate_ab_test_significance(
        self,
        visitors_a: int = 1500,
        conversions_a: int = 600,
        visitors_b: int = 1500,
        conversions_b: int = 660,
        metric_name: str = "D1 Retention"
    ) -> Dict[str, Any]:
        """Calculates two-proportion Z-test, p-value, and confidence interval."""
        if visitors_a <= 0 or visitors_b <= 0:
            return {"error": "Số lượng mẫu phải lớn hơn 0"}

        rate_a = conversions_a / visitors_a
        rate_b = conversions_b / visitors_b

        relative_lift_pct = round(((rate_b - rate_a) / max(0.0001, rate_a)) * 100, 2)
        absolute_diff = round((rate_b - rate_a) * 100, 2)

        # Pooled proportion
        pooled_p = (conversions_a + conversions_b) / (visitors_a + visitors_b)
        se = math.sqrt(pooled_p * (1 - pooled_p) * (1 / visitors_a + 1 / visitors_b))

        if se > 0:
            z_score = (rate_b - rate_a) / se
        else:
            z_score = 0.0

        # Approximate two-tailed p-value using complementary error function
        # p-value = 2 * (1 - Phi(|z|))
        abs_z = abs(z_score)
        # Using polynomial approximation for standard normal cumulative distribution
        t = 1.0 / (1.0 + 0.2316419 * abs_z)
        poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        phi = 1.0 - (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * abs_z * abs_z) * poly
        p_value = round(2.0 * (1.0 - phi), 4)

        confidence_pct = round((1.0 - p_value) * 100, 2)

        if p_value < 0.05 and relative_lift_pct > 0:
            verdict = "CHIẾN THẮNG TUYỆT ĐỐI (Statistically Significant Winner)"
            badge_color = "emerald"
            action = "Áp dụng nhánh B (Variant B) ngay lập tức cho toàn bộ người chơi. Khả năng đây là may rủi < 5%."
        elif p_value < 0.05 and relative_lift_pct < 0:
            verdict = "THẤT BẠI RÕ RỆT (Statistically Significant Loss)"
            badge_color = "rose"
            action = "Dừng nhánh B ngay lập tức. Tính năng/Icon mới làm giảm sút chỉ số nghiêm trọng."
        else:
            verdict = "CHƯA ĐỦ BẰNG CHỨNG (Inconclusive / No Significant Difference)"
            badge_color = "amber"
            action = "Chưa thể khẳng định nhánh nào tốt hơn. Cần tiếp tục chạy thêm traffic hoặc giữ nguyên nhánh A."

        return {
            "metric_name": metric_name,
            "variant_a_control": {
                "visitors": visitors_a,
                "conversions": conversions_a,
                "rate_pct": round(rate_a * 100, 2)
            },
            "variant_b_treatment": {
                "visitors": visitors_b,
                "conversions": conversions_b,
                "rate_pct": round(rate_b * 100, 2)
            },
            "comparison": {
                "relative_lift_pct": relative_lift_pct,
                "absolute_diff_pct": absolute_diff,
                "z_score": round(z_score, 3),
                "p_value": p_value,
                "confidence_pct": confidence_pct,
                "is_significant_at_95": p_value < 0.05
            },
            "decision": {
                "verdict": verdict,
                "badge_color": badge_color,
                "recommended_action": action
            }
        }
