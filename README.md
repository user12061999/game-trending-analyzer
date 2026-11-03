# 🎮 Game Market Trending Analyzer (PC & Mobile)

Hệ thống phân tích xu hướng thị trường game **Mobile (iOS & Android)** và **PC (Steam)** theo chu kỳ **Hàng Ngày (Daily)** và **Hàng Tuần (Weekly)** với Web Dashboard tương tác trực quan.

---

## 🌟 Tính Năng Nổi Bật

1. **Đa nền tảng toàn diện:**
   - **PC (Steam):** Theo dõi Top Most Played (CCU - Số người chơi cùng lúc thời gian thực), Top Sellers (Thịnh hành & Doanh thu), Tags thể loại, giá và studio phát triển.
   - **Mobile (Apple App Store & Google Play):** Theo dõi Top Grossing (Doanh thu), Top Free (Lượt tải về), Điểm đánh giá (Rating), Hãng phát hành.
2. **Mô Hình Ước Tính Doanh Thu & Lượt Tải ($) (Mới):**
   - Ứng dụng phân bổ Pareto / Power Law Curve: Ước tính khoảng doanh thu theo ngày và theo tháng cho từng game Mobile & PC.
   - Ước tính lượt tải về (Downloads) hàng ngày cho game Mobile Top Free.
   - Ước tính tổng doanh thu trọn đời (Lifetime Gross) cho game PC Steam.
3. **Trợ Lý AI Phân Tích Chuyên Sâu Game (AI Game Deconstructor) (Mới):**
   - Nút **"🤖 Phân Tích Chuyên Sâu Bằng AI"** trên từng tựa game.
   - Bóc tách toàn diện 5 trụ cột:
     1. Vòng lặp trải nghiệm cốt lõi (Core Gameplay Loop & Retention)
     2. Kiến trúc kiếm tiền (Monetization Architecture: Gacha, Battle Pass, IAP, Ads)
     3. Chân dung người chơi mục tiêu (Target Audience & Persona)
     4. Lợi thế cạnh tranh (Competitive Edge)
     5. Bài học đắt giá cho Game Dev / Studio Việt Nam
   - Tích hợp **Google Gemini 1.5 Flash** (hoặc tự động dùng Hệ tri thức Heuristic khi chưa có API key).
4. **Biểu Đồ Lịch Sử & Modal Phân Tích Game:**
   - Nhấp vào bất kỳ tựa game nào để mở **Game Intelligence Modal**.
   - Biểu đồ đường **Rank Trendline** (trục Y đảo ngược với vị trí #1 ở đỉnh) và đường cong **CCU** theo thời gian.
   - Bảng thống kê lịch sử: Kỷ lục rank tốt nhất, rank trung bình, ngày theo dõi.
5. **So Sánh Đối Thủ Đối Đầu (Head-to-Head Comparison):**
   - Đặt 2 tựa game cạnh nhau (ví dụ: *CS2* vs *Dota 2*, hoặc *Free Fire* vs *Liên Quân Mobile*).
   - Biểu đồ đường kép (Dual Line Chart) so sánh trực quan quỹ đạo thứ hạng trên cùng trục thời gian.
6. **Hệ Thống Cảnh Báo & Bot Tự Động:**
   - **Discord Webhook:** Gửi thẻ tin nhắn Rich Embed cực đẹp vào kênh Discord của studio.
   - **Telegram Bot:** Gửi tin nhắn định dạng HTML vào nhóm Telegram.
   - **Bản tin 08:00 sáng:** Tự động tổng kết Top bứt phá, PC đỉnh CCU, Mobile đỉnh doanh thu mỗi ngày.
   - **Cảnh báo Breakout khẩn cấp:** Bắn tin nhắn ngay khi có game nhảy vọt $\ge 15$ bậc trong 24 giờ.
7. **Theo dõi tất cả thị trường & Quốc gia:**
   - Hỗ trợ chọn nhanh các thị trường trọng điểm: 🌐 **Toàn cầu (Global)**, 🇻🇳 **Việt Nam**, 🇺🇸 **United States**, 🇰🇷 **Hàn Quốc**, 🇯🇵 **Nhật Bản**, 🇬🇧 **Anh**, 🇩🇪 **Đức**, 🇧🇷 **Brazil**, v.v.
8. **Phân tích Thị phần Thể loại (Genre Analytics):**
   - Biểu đồ tròn (Doughnut Chart) trực quan hóa các dòng game đang chiếm ưu thế.
9. **Báo cáo Thị trường Tự động & Xuất Dữ liệu:**
   - Tự động biên soạn bản tóm tắt thị trường (Executive Summary) theo định dạng Markdown.
   - Xuất dữ liệu ra file **Excel (.xlsx)** hoặc **CSV** chỉ với 1 click.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### Cách 1: Chạy nhanh bằng file Batch (Khuyên dùng trên Windows)
Chỉ cần nhấp đúp chuột vào file:
```
start.bat
```
File sẽ tự động kích hoạt môi trường ảo và mở trình duyệt tại: `http://127.0.0.1:8000`.

### Cách 2: Chạy bằng dòng lệnh (Terminal / PowerShell)
```powershell
# 1. Kích hoạt môi trường ảo
.\.venv\Scripts\activate

# 2. Khởi động Web Dashboard
python run.py
```

Sau khi chạy, mở trình duyệt web và truy cập: **`http://127.0.0.1:8000`**

---

## 📁 Cấu Trúc Dự Án

```
d:\game-trending-analyzer\
│
├── run.py                       # File khởi động ứng dụng Web Dashboard & tự mở trình duyệt
├── start.bat                    # Script 1-click chạy trên Windows
├── requirements.txt             # Danh sách thư viện Python cần thiết
├── README.md                    # Tài liệu hướng dẫn sử dụng
│
├── data/
│   └── game_trends.db           # SQLite database lưu trữ snapshot lịch sử theo ngày/tuần
│
└── app/
    ├── main.py                  # FastAPI server & Scheduler tự động crawl
    ├── config.py                # Cấu hình danh sách quốc gia, nền tảng, loại xếp hạng
    │
    ├── database/
    │   ├── db.py                # Khởi tạo SQLite schema và lưu dữ liệu snapshot
    │
    ├── crawlers/
    │   ├── steam_crawler.py     # Thu thập dữ liệu Steam Charts (CCU) & SteamSpy
    │   ├── app_store_crawler.py # Thu thập Top Grossing & Top Free từ Apple Store RSS
    │   ├── google_play_crawler.py # Thu thập Google Play Store theo từng quốc gia
    │   └── orchestrator.py      # Điều phối crawl, tính delta DoD và WoW
    │
    ├── analytics/
    │   ├── trend_analyzer.py    # Phân tích biến động, breakout radar, thị phần thể loại
    │   └── report_generator.py  # Tạo báo cáo tóm tắt Markdown và xuất file Excel/CSV
    │
    └── templates/
        └── index.html           # Giao diện Web Dashboard hiện đại (TailwindCSS, Chart.js)
```

---

## 📡 REST API Tham Khảo

- `GET /`: Giao diện Web Dashboard.
- `GET /api/overview?target_date=YYYY-MM-DD`: Tổng hợp chỉ số KPI, Top PC, Top Mobile, Rising Games.
- `GET /api/rankings`: Lọc bảng xếp hạng (`platform`, `country`, `ranking_type`, `genre`, `search`, `target_date`, `limit`).
- `GET /api/genres`: Dữ liệu phân bổ thể loại cho biểu đồ.
- `POST /api/crawl`: Kích hoạt crawl dữ liệu mới ngay lập tức.
- `GET /api/crawl/status`: Xem lịch sử và trạng thái crawl gần nhất.
- `GET /api/report`: Bản tóm tắt thị trường dạng bài viết.
- `GET /api/export/excel`: Tải toàn bộ bảng xếp hạng ra file `.xlsx`.
- `GET /api/export/csv`: Tải bảng xếp hạng ra file `.csv`.
