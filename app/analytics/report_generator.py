"""Report Generator for Daily / Weekly Game Market Analysis and File Exports."""

import io
from typing import Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
from app.analytics.trend_analyzer import TrendAnalyzer
from app.database.db import get_db_connection

class ReportGenerator:
    def __init__(self):
        self.analyzer = TrendAnalyzer()

    def generate_market_report(self, target_date: Optional[str] = None, period: str = "daily") -> Dict[str, Any]:
        """Generates a comprehensive market intelligence report in markdown format."""
        if not target_date:
            target_date = self.analyzer.get_latest_snapshot_date()

        overview = self.analyzer.get_market_overview(target_date)
        genre_dist = self.analyzer.get_genre_distribution(target_date=target_date)

        report_title = f"Báo Cáo Xu Hướng Thị Trường Game ({'Hàng Ngày' if period == 'daily' else 'Hàng Tuần'}) - {target_date}"
        
        # Build Markdown Text
        md = []
        md.append(f"# 🎮 {report_title}\n")
        md.append(f"> **Ngày phân tích:** `{target_date}` | **Tổng số game theo dõi:** **{overview.get('total_tracked', 0):,}** tựa game\n")
        
        # 1. Executive Summary
        md.append("## 📌 1. Tóm Tắt Thị Trường (Executive Summary)")
        pc_count = overview.get('platform_counts', {}).get('pc_steam', 0)
        ios_count = overview.get('platform_counts', {}).get('mobile_appstore', 0)
        android_count = overview.get('platform_counts', {}).get('mobile_googleplay', 0)
        md.append(f"- **Phạm vi dữ liệu:** PC Steam ({pc_count}), iOS App Store ({ios_count}), Android Google Play ({android_count}).")
        
        if overview.get("top_steam_ccu"):
            top_pc = overview["top_steam_ccu"][0]
            md.append(f"- **PC Đỉnh Bảng:** Tựa game **{top_pc.get('title')}** dẫn đầu với hơn **{top_pc.get('player_count', 0):,} CCU** (người chơi cùng lúc).")
            
        if overview.get("rising_games"):
            top_riser = overview["rising_games"][0]
            md.append(f"- **Tăng Trưởng Nổi Bật:** **{top_riser.get('title')}** bứt phá nhảy vọt **+{top_riser.get('rank_change_day', 0)} bậc** trên bảng xếp hạng.\n")

        # 2. Breakouts / Rising Stars
        md.append("## 🚀 2. Hiện Tượng Bùng Nổ (Breakout / Rising Stars)")
        md.append("| Game | Thể Loại | Nền Tảng | Rank Hiện Tại | Biến Động Rank (DoD) |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for g in overview.get("rising_games", [])[:5]:
            delta = f"+{g.get('rank_change_day')}" if g.get('rank_change_day', 0) > 0 else g.get('rank_change_day')
            plat_badge = "🖥️ PC Steam" if "pc" in g.get("platform", "") else "📱 Mobile"
            md.append(f"| **{g.get('title')}** | {g.get('genre', 'N/A')} | {plat_badge} | #{g.get('rank')} | 🟢 **{delta}** |")
        md.append("")

        # 3. Top Steam Games
        md.append("## 🖥️ 3. Top PC Games Sôi Động Nhất (Steam CCU)")
        md.append("| Rank | Tựa Game | Nhà Phát Triển | Thể Loại | Người Chơi (CCU) |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for g in overview.get("top_steam_ccu", []):
            md.append(f"| #{g.get('rank')} | **{g.get('title')}** | {g.get('developer', 'N/A')} | {g.get('genre', 'N/A')} | **{g.get('player_count', 0):,}** |")
        md.append("")

        # 4. Top Mobile Grossing
        md.append("## 📱 4. Top Mobile Doanh Thu Cao Nhất (Top Grossing)")
        md.append("| Rank | Tựa Game | Nhà Phát Triển | Quốc Gia | Điểm Đánh Giá |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for g in overview.get("top_mobile_grossing", []):
            md.append(f"| #{g.get('rank')} | **{g.get('title')}** | {g.get('developer', 'N/A')} | {g.get('country', '').upper()} | ⭐ {g.get('score', 'N/A')} |")
        md.append("")

        # 5. Genre Market Share
        md.append("## 📊 5. Phân Bổ Thể Loại Thị Trường (Genre Distribution)")
        md.append("| Thể Loại | Số Lượng Game Trong Top |")
        md.append("| :--- | :--- |")
        for item in genre_dist:
            md.append(f"| **{item.get('genre')}** | {item.get('count')} games |")
        md.append("")

        md_content = "\n".join(md)

        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO market_reports (created_at, period, target_date, title, summary_markdown)
        VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), period, target_date, report_title, md_content))
        conn.commit()
        conn.close()

        return {
            "title": report_title,
            "target_date": target_date,
            "period": period,
            "markdown": md_content
        }

    def export_to_excel(self, target_date: Optional[str] = None) -> bytes:
        """Exports snapshot rankings for the target date to an Excel binary stream."""
        if not target_date:
            target_date = self.analyzer.get_latest_snapshot_date()

        conn = get_db_connection()
        query = "SELECT * FROM snapshots WHERE snapshot_date = ? ORDER BY platform, ranking_type, rank ASC"
        df = pd.read_sql_query(query, conn, params=[target_date])
        conn.close()

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # All data sheet
            df.to_excel(writer, sheet_name="All Rankings", index=False)
            
            # PC sheet
            pc_df = df[df["platform"].str.startswith("pc")]
            if not pc_df.empty:
                pc_df.to_excel(writer, sheet_name="PC Steam", index=False)

            # Mobile sheet
            mobile_df = df[df["platform"].str.startswith("mobile")]
            if not mobile_df.empty:
                mobile_df.to_excel(writer, sheet_name="Mobile Games", index=False)

        output.seek(0)
        return output.getvalue()

    def export_to_csv(self, target_date: Optional[str] = None) -> str:
        """Exports snapshot rankings for the target date as CSV string."""
        if not target_date:
            target_date = self.analyzer.get_latest_snapshot_date()

        conn = get_db_connection()
        query = "SELECT * FROM snapshots WHERE snapshot_date = ? ORDER BY platform, ranking_type, rank ASC"
        df = pd.read_sql_query(query, conn, params=[target_date])
        conn.close()
        return df.to_csv(index=False)
