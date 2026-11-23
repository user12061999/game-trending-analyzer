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
   - Tích hợp **Google Gemini** (model cấu hình qua `GEMINI_MODEL` trong `.env`) (hoặc tự động dùng Hệ tri thức Heuristic khi chưa có API key).
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
   - **Bản tin hằng ngày:** Tự động tổng kết Top bứt phá, PC đỉnh CCU, Mobile đỉnh doanh thu sau lần crawl đầu tiên mỗi ngày.
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
File sẽ tự động kích hoạt môi trường ảo và mở trình duyệt tại: `http://127.0.0.1:8888`.

### Cách 2: Chạy bằng dòng lệnh (Terminal / PowerShell)
```powershell
# 1. Kích hoạt môi trường ảo
.\.venv\Scripts\activate

# 2. Khởi động Web Dashboard
python run.py
```

Sau khi chạy, mở trình duyệt web và truy cập: **`http://127.0.0.1:8888`**

---

## ⚙️ Cấu Hình (.env)

Sao chép `.env.example` thành `.env` rồi điền giá trị. File `.env` và `data/*.json` đã được git-ignore để API key không bị commit nhầm.

| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `GEMINI_API_KEY` | Key Google Gemini cho các tính năng AI (để trống → dùng hệ tri thức nội bộ, có ghi rõ "không dùng LLM") | trống |
| `GEMINI_MODEL` | Tên model Gemini dùng cho mọi lời gọi AI | `gemini-3.5-flash-lite` |
| `STEAM_API_KEY` | Steam Web API key (tùy chọn) | trống |
| `HOST` / `PORT` | Địa chỉ web server | `127.0.0.1` / `8888` |
| `DAILY_CRAWL_HOUR` / `DAILY_CRAWL_MINUTE` | Giờ crawl hằng ngày (giờ máy) | `6` / `0` |
| `CRAWL_COUNTRIES` | Quốc gia crawl mặc định | `us,vn,kr,jp,global` |

**Lịch crawl:** crawl chạy theo cron vào giờ cố định mỗi ngày. Nếu máy tắt đúng giờ đó, lần khởi động kế tiếp sẽ tự **crawl bù** khi hôm nay chưa có snapshot. Mọi request mạng của crawler có retry + backoff (429/5xx/lỗi mạng).

### 🕕 Crawl tự động kể cả khi không mở Dashboard

Chạy một lần (không cần quyền admin):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_scheduled_tasks.ps1
```

Lệnh này tạo 2 tác vụ trong Windows Task Scheduler (thư mục `\GameTrendAnalyzer\`):

- **Daily Crawl** — chạy `scripts\crawl_once.py` lúc 06:00 và 18:00 (lần 18:00 là lưới an toàn). Script tự bỏ qua nếu hôm nay đã có dữ liệu, và Windows tự chạy bù khi máy bật lại nếu lỡ giờ. Log ở `data\logs\`.
- **Weekly DB Backup** — Chủ nhật 12:00 sao lưu database vào `dataackups\`, giữ 8 bản mới nhất.

Web server và tác vụ dùng chung khóa `data\crawl.lock` nên không bao giờ crawl trùng nhau. Tùy chọn: `-CrawlTime 07:30` để đổi giờ, `-Uninstall` để gỡ. Crawl thủ công: `.\.venv\Scripts\python scripts\crawl_once.py --force`.

### 🔔 Cảnh báo Discord / Telegram

Điền Webhook Discord hoặc Bot Token + Chat ID Telegram trong tab **Cài Đặt → Cấu Hình Cảnh Báo**. Sau mỗi lần crawl (của web server hoặc tác vụ tự động), hệ thống gửi:

| Cảnh báo | Khi nào | Chống gửi trùng |
|---|---|---|
| 📊 Bản tin ngày | Sau lần crawl thành công đầu tiên trong ngày (08:00 là lưới an toàn nếu Dashboard mở) | 1 lần/ngày |
| 🚀 Breakout | Game tăng ≥ N bậc trong 1 ngày | Không báo lại cùng game trong X ngày |
| 📈 Bứt phá bền vững | Game tăng ≥ N bậc đều đặn trong cửa sổ ngày (bỏ qua cú nhảy đơn lẻ) | 1 lần/cửa sổ |
| ⚠️ Crawl lỗi | Nguồn crawl lỗi hoặc dữ liệu cũ > 36 giờ | 1 lần/ngày cho mỗi nhóm lỗi |
| 🗓️ Bản tin tuần | Xu hướng thể loại, vào lần crawl đầu tiên từ ngày đã chọn trở đi | 1 lần/tuần |

Mọi cảnh báo đã gửi được lưu trong bảng `alert_log` và hiển thị ở mục "Cảnh Báo Đã Gửi Gần Đây".

---

## 🧭 Về Độ Tin Cậy Của Dữ Liệu

- **Dữ liệu thật:** chỉ có **thứ hạng, CCU, giá, điểm đánh giá** lấy từ các lần crawl.
- **Ước tính:** doanh thu & lượt tải được tính từ thứ hạng bằng mô hình Power-law. Biểu đồ doanh thu vẽ **nét đứt** cho những ngày không có snapshot (thứ hạng được nội suy tuyến tính hoặc giữ nguyên thứ hạng gần nhất, không có số ngẫu nhiên). Tỷ trọng theo Tier quốc gia là giả định.
- **Giả lập:** dữ liệu tạo bởi nút "Simulate" trong MMP Stream được gắn nhãn **DEMO** và đếm riêng.
- **Steam offline:** khi không gọi được Steam API, giao diện hiển thị `N/A` kèm cảnh báo thay vì số liệu mẫu.
- **App Store "global":** Apple không có bảng xếp hạng toàn cầu nên mục này chỉ crawl Google Play.
- **Google Play:** thư viện `google-play-scraper` không hỗ trợ bảng xếp hạng chính thức, nên "thứ hạng" Google Play là thứ tự kết quả tìm kiếm theo từ khóa, chỉ mang tính tham khảo.

**Hiệu chỉnh mô hình:** ở tab **Cài Đặt → Hiệu Chỉnh Mô Hình**, nhập các game bạn biết doanh thu thật (kèm thứ hạng lúc đó). Hệ thống lấy trung vị tỷ lệ *thật / ước tính* theo từng (nền tảng, quốc gia) làm hệ số nhân cho mọi ước tính, giới hạn ×0.1–×10. Quốc gia chưa có dữ liệu dùng hệ số chung của nền tảng (khi có ≥2 điểm). Bảng hiển thị sai số trước/sau hiệu chỉnh của từng điểm.

Tab **Thị Trường → Tín Hiệu Thị Trường** hiển thị: sức khỏe từng nguồn crawl (OK / cũ / lỗi), game **bứt phá bền vững** (tăng hạng đều qua nhiều lần crawl) và **xu hướng thể loại** tuần này so với tuần trước.

---

## 🧪 Kiểm Thử

```powershell
.\.venv\Scripts\pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest -q
```

---

## 📁 Cấu Trúc Dự Án

```
d:\game-trending-analyzer\
├── run.py / start.bat           # Khởi động Web Dashboard
├── requirements.txt             # Thư viện chạy app
├── requirements-dev.txt         # Thư viện test (pytest)
├── .env.example                 # Mẫu cấu hình (copy thành .env)
├── data/game_trends.db          # SQLite snapshot lịch sử (git-ignored)
├── scripts/                     # crawl_once.py, backup_db.py, install_scheduled_tasks.ps1
├── tests/                       # Pytest: delta rank, mô hình doanh thu, tín hiệu thị trường, smoke test API
└── app/
    ├── main.py                  # Tạo FastAPI app, lifespan (lịch crawl), mount static, gắn routers
    ├── config.py                # Cấu hình + nạp .env
    ├── routers/                 # API chia theo nhóm: market, crawl, settings, watchlist,
    │                            #   mobile_growth, mobile_economy, mmp, steam, studio
    ├── services/
    │   ├── container.py         # Các service singleton dùng chung
    │   └── crawl_service.py     # Khóa chống crawl trùng, cron hằng ngày, crawl bù khi khởi động
    ├── database/db.py           # SQLite schema và truy vấn
    ├── crawlers/                # Steam, App Store, Google Play, Mobile Radar, retry helper
    ├── analytics/               # Các module phân tích (market_signals, revenue_*, gemini_client, ...)
    ├── static/                  # css/app.css + js/*.js chia theo tính năng (core.js nạp đầu, init.js nạp cuối)
    └── templates/index.html     # Giao diện Web Dashboard (TailwindCSS, Chart.js)
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
- `GET /api/signals/data-health`: Trạng thái từng nguồn crawl, số ngày có dữ liệu trong 30 ngày.
- `GET /api/signals/sustained-breakouts`: Game tăng hạng bền vững (`window_days`, `platform`, `country`, `min_net_gain`).
- `GET /api/signals/genre-trends`: Tỷ trọng thể loại tuần này vs tuần trước (`platform`, `country`, `top_n_rank`).
- `GET /api/calibration` · `POST /api/calibration` · `DELETE /api/calibration/{id}`: Quản lý điểm doanh thu thật & hệ số hiệu chỉnh.
- `GET /api/game/{game_id}/revenue-history`: Doanh thu/lượt tải **ước tính** theo ngày, kèm `data_quality`.
