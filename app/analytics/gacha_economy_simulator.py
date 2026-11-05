"""In-Game Economy & Gacha Monte Carlo Lab.

Provides Monte Carlo gacha probability simulations (Soft & Hard Pity, 50/50 win/loss),
full character ascension whale cost calculators, and in-game resource faucet vs sink balancing.
"""

from typing import Dict, Any, List, Optional
import random

class GachaEconomySimulator:
    """Mathematical simulation engine for Gacha systems and In-Game Resource Economy."""

    def __init__(self):
        # Preset Gacha Systems
        self.preset_models = {
            "genshin_style": {
                "name": "Triple-A Anime Gacha (Genshin / Honkai Style)",
                "base_ssr_rate": 0.006,  # 0.6%
                "soft_pity_start": 74,
                "soft_pity_rate_increase": 0.06,  # +6% per pull after soft pity
                "hard_pity": 90,
                "featured_rate_up": 0.50,  # 50/50
                "guarantee_on_miss": True,  # Next is guaranteed if lost 50/50
                "cost_per_pull_usd": 2.00,
                "max_ascension_copies": 7,  # C0 + 6 duplicates (C6)
                "description": "Tiêu chuẩn vàng của anime RPG toàn cầu: Pity mềm từ lượt 74, Pity cứng tại lượt 90, cơ chế lệch rate 50/50 kèm bảo hiểm lần kế tiếp."
            },
            "idle_rpg_style": {
                "name": "Idle RPG Gacha (AFK Arena / Nikke Style)",
                "base_ssr_rate": 0.04,  # 4.0%
                "soft_pity_start": 30,
                "soft_pity_rate_increase": 0.15,
                "hard_pity": 30,
                "featured_rate_up": 0.50,
                "guarantee_on_miss": False,
                "cost_per_pull_usd": 1.20,
                "max_ascension_copies": 14,  # Multiple copies needed for star upgrades
                "description": "Tỷ lệ cơ bản cao (4%) nhưng đòi hỏi số lượng bản sao rất lớn (14-20 copies) để nâng bậc Kim Cương / Tinh Anh."
            },
            "classic_turnbased": {
                "name": "Classic Turn-Based RPG (Summoners War / FGO Style)",
                "base_ssr_rate": 0.01,  # 1.0%
                "soft_pity_start": 100,
                "soft_pity_rate_increase": 0.02,
                "hard_pity": 200,
                "featured_rate_up": 0.70,
                "guarantee_on_miss": False,
                "cost_per_pull_usd": 2.50,
                "max_ascension_copies": 5,
                "description": "Hệ thống truyền thống ít pity, đề cao độ hiếm cực hạn của tướng 5 sao, kích thích cảm giác sở hữu độc nhất vô nhị."
            }
        }

    def simulate_gacha_pulls(
        self,
        model_key: str = "genshin_style",
        target_copies: int = 1,
        iterations: int = 3000
    ) -> Dict[str, Any]:
        """Runs Monte Carlo simulation for obtaining target copies of the featured SSR."""
        cfg = self.preset_models.get(model_key, self.preset_models["genshin_style"])

        pull_counts = []
        cost_per_pull = cfg["cost_per_pull_usd"]

        # Run empirical simulations
        for _ in range(iterations):
            copies_obtained = 0
            pulls_in_sim = 0
            pity_counter = 0
            is_guaranteed = False

            while copies_obtained < target_copies:
                pulls_in_sim += 1
                pity_counter += 1

                # Calculate current probability with soft/hard pity
                if pity_counter >= cfg["hard_pity"]:
                    current_rate = 1.0
                elif pity_counter >= cfg["soft_pity_start"]:
                    steps = pity_counter - cfg["soft_pity_start"] + 1
                    current_rate = min(1.0, cfg["base_ssr_rate"] + steps * cfg["soft_pity_rate_increase"])
                else:
                    current_rate = cfg["base_ssr_rate"]

                # Roll for SSR
                if random.random() < current_rate:
                    # Reset pity counter
                    pity_counter = 0
                    # Check 50/50
                    if is_guaranteed or (random.random() < cfg["featured_rate_up"]):
                        copies_obtained += 1
                        is_guaranteed = False
                    else:
                        if cfg["guarantee_on_miss"]:
                            is_guaranteed = True

            pull_counts.append(pulls_in_sim)

        pull_counts.sort()
        n = len(pull_counts)

        avg_pulls = round(sum(pull_counts) / n, 1)
        median_pulls = pull_counts[int(n * 0.50)]
        p10_lucky = pull_counts[int(n * 0.10)]
        p90_unlucky = pull_counts[int(n * 0.90)]
        max_worst_case = pull_counts[-1]

        # Cost conversions
        avg_cost_usd = round(avg_pulls * cost_per_pull, 2)
        lucky_cost_usd = round(p10_lucky * cost_per_pull, 2)
        unlucky_cost_usd = round(p90_unlucky * cost_per_pull, 2)

        return {
            "model_info": {
                "name": cfg["name"],
                "base_rate": f"{cfg['base_ssr_rate'] * 100}%",
                "soft_pity": cfg["soft_pity_start"],
                "hard_pity": cfg["hard_pity"],
                "cost_per_pull": f"${cost_per_pull}",
                "target_copies": target_copies,
                "description": cfg["description"]
            },
            "monte_carlo_stats": {
                "simulations_count": iterations,
                "average_pulls": avg_pulls,
                "median_pulls": median_pulls,
                "lucky_p10_pulls": p10_lucky,
                "unlucky_p90_pulls": p90_unlucky,
                "worst_case_pulls": max_worst_case,
                "avg_cost_usd": avg_cost_usd,
                "lucky_cost_usd": lucky_cost_usd,
                "unlucky_cost_usd": unlucky_cost_usd,
                "whale_full_ascension_cost_usd": round(avg_cost_usd * (cfg["max_ascension_copies"] / max(1, target_copies)), 2)
            },
            "spending_psychology_verdict": (
                f"Trung bình người chơi cần {avg_pulls} vé (~${avg_cost_usd}) để sở hữu {target_copies} bản sao. "
                f"90% người chơi sẽ đạt được trong vòng {p90_unlucky} vé. "
                f"Để Max Sao (C6/Thần Thoại), một Whale cần đầu tư khoảng ~${round(avg_cost_usd * (cfg['max_ascension_copies'] / max(1, target_copies)), 2):,}."
            )
        }

    def evaluate_economy_faucet_sink(
        self,
        daily_gem_faucet: int = 150,
        weekly_event_faucet: int = 500,
        monthly_pass_faucet: int = 3000,
        daily_gem_sink: int = 120,
        weekly_gem_sink: int = 800,
        gacha_pull_cost_gems: int = 160
    ) -> Dict[str, Any]:
        """Calculates 30-day resource faucet vs sink ratio and inflation health."""
        # 30-day Faucet calculation
        monthly_faucet = (daily_gem_faucet * 30) + (weekly_event_faucet * 4) + monthly_pass_faucet
        # 30-day Sink calculation
        monthly_sink = (daily_gem_sink * 30) + (weekly_gem_sink * 4)

        net_accumulation = monthly_faucet - monthly_sink
        faucet_sink_ratio = round(monthly_faucet / max(1, monthly_sink), 2)
        free_pulls_per_month = round(monthly_faucet / max(1, gacha_pull_cost_gems), 1)

        # Economic health diagnosis
        if faucet_sink_ratio > 1.6:
            status = "Lạm Phát Tài Nguyên (Hyper-Inflation)"
            health_color = "rose"
            verdict = "Người chơi tích lũy quá nhiều gem miễn phí, làm giảm mạnh động lực nạp gói IAP nạp lần đầu."
            action = "Bổ sung nguồn xả: Thêm skin độc quyền, mở rộng kho đồ, hoặc tăng giá nâng cấp bậc cao."
        elif faucet_sink_ratio < 0.8:
            status = "Nghẽn Kinh Tế (Economy Choke)"
            health_color = "amber"
            verdict = "Lượng gem miễn phí quá ít so với nhu cầu xả, người chơi F2P dễ nản lòng và rời bỏ game sớm."
            action = "Tăng gem thưởng daily quest hoặc quà thành tựu (achievement) giai đoạn đầu để giữ chân D7."
        else:
            status = "Cân Bằng Hoàn Hảo (Golden Equilibrium)"
            health_color = "emerald"
            verdict = "Tỷ lệ tích lũy vừa đủ kích thích người chơi cày cuốc, trong khi vẫn tạo cảm giác thiếu hụt để thúc đẩy nạp vé mùa."
            action = "Duy trì tỷ lệ này. Tập trung tung banner giới hạn đúng chu kỳ."

        return {
            "monthly_metrics": {
                "total_faucet_gems": monthly_faucet,
                "total_sink_gems": monthly_sink,
                "net_monthly_gems_saved": net_accumulation,
                "faucet_sink_ratio": faucet_sink_ratio,
                "free_pulls_per_month": free_pulls_per_month
            },
            "diagnosis": {
                "status": status,
                "health_color": health_color,
                "verdict": verdict,
                "recommended_action": action
            }
        }
