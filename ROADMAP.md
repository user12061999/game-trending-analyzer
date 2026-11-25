# 🗺️ Lộ Trình Phát Triển

Cập nhật: 2026-11-25 · Nhánh: `feat/data-reliability-and-refactor`

Nguyên tắc xuyên suốt: **số liệu nào hiển thị trên dashboard cũng phải cho biết nó là dữ liệu crawl thật, ước tính từ mô hình, mô phỏng giả định hay nội dung sinh tự động.**

---

## ✅ Đã hoàn thành (nhánh hiện tại)

| Commit | Nội dung |
|---|---|
| `218b245` | Bỏ số ngẫu nhiên trong lịch sử doanh thu (nội suy + nhãn nguồn), nhãn DEMO cho MMP, Steam offline hiển thị N/A; `.env` cho API key; cron crawl + crawl bù; retry crawler; tab **Tín Hiệu Thị Trường** (sức khỏe dữ liệu, bứt phá bền vững, xu hướng thể loại); **Hiệu chỉnh mô hình doanh thu** từ số liệu thật; tách `main.py` → routers, tách JS/CSS; bộ test pytest |
| `6f74add` | Crawl tự động bằng Windows Task Scheduler (06:00 + 18:00, chạy bù khi máy bật lại), sao lưu DB hằng tuần, khóa crawl dùng chung giữa server và task |
| `995c588` | Ghim phiên bản CDN (Tailwind 3.4.17, Chart.js 4.6.1 + SRI, Lucide 1.77.0 + SRI) |
| `3fb69bb` | Cảnh báo Discord/Telegram sau mỗi lần crawl, có chống gửi trùng: bản tin ngày, breakout, bứt phá bền vững, crawl lỗi, bản tin thể loại hằng tuần |
| `6b6a802` | Review Miner chỉ dùng review thật (thêm Google Play), radar ghi rõ nguồn, nhãn loại dữ liệu trên 20 tab, vá XSS |

**Trạng thái dữ liệu:** crawl tự động chạy ổn định từ 23/11/2026 (~770 bản ghi/ngày).

---

## 🔜 Việc tiếp theo

### Ưu tiên cao

- [ ] **Cấu hình kênh cảnh báo** *(người dùng)* — điền Discord Webhook hoặc Telegram Bot trong *Cài Đặt → Cấu Hình Cảnh Báo*, bấm "Gửi Thử Nghiệm". Hiện chưa có kênh nào nên chưa có cảnh báo nào được gửi.
- [ ] **Nhập dữ liệu hiệu chỉnh doanh thu** *(người dùng)* — 3–5 game đã biết doanh thu thật cho mỗi thị trường quan tâm (VN, US…) trong *Cài Đặt → Hiệu Chỉnh Mô Hình*.
- [ ] **Chỉnh ngưỡng cảnh báo** — sau ~1 tuần dữ liệu (từ ~30/11/2026), xem tab Tín Hiệu Thị Trường và điều chỉnh ngưỡng breakout / bứt phá bền vững cho phù hợp lượng tin mong muốn.
- [ ] **Làm lại crawl radar game sắp ra mắt** — luồng tìm pre-order qua App Store Search hiện không tìm được game nào, nên 100% radar là danh sách nhập tay chưa xác minh. Hướng: lấy danh sách pre-order từ App Store (trang "Coming Soon"/pre-order theo quốc gia) và Google Play (pre-registration), hoặc cho phép người dùng tự thêm/sửa game trên radar kèm nguồn.
- [ ] **CI trên GitHub Actions** — chạy `pytest` cho mỗi push/PR (bộ test hiện có 44 test, chạy < 10 giây, không cần mạng).

### Ưu tiên trung bình

- [ ] **Bảng xếp hạng Google Play chính thức** — hiện "thứ hạng" Google Play là thứ tự kết quả tìm kiếm theo từ khóa. Cần nguồn top chart thật; rủi ro: phải parse trang web, dễ hỏng khi Google đổi giao diện → cần test parser + cảnh báo khi parser trả 0 kết quả (đã có qua sức khỏe dữ liệu).
- [ ] **Review Steam bị chặn** — endpoint `store.steampowered.com/appreviews` chuyển hướng về trang chủ từ mạng hiện tại (các API Steam khác vẫn chạy). Thử Steam Web API chính thức với API key, hoặc ghi rõ hạn chế.
- [ ] **Tự vendor thư viện front-end** — tải Tailwind/Chart.js/Lucide về `app/static/vendor/` để dashboard chạy được khi không có mạng và không phụ thuộc CDN (Tailwind CDN không hỗ trợ SRI).
- [ ] **Chuyển các tab "tham khảo tĩnh" sang dữ liệu có nguồn** — Creative Spy, Blue Ocean, LiveOps hiện là dữ liệu viết sẵn. Có thể tính "Blue Ocean" từ chính dữ liệu crawl (thể loại có ít game trong Top nhưng doanh thu ước tính cao), và cho phép ghi nguồn cho từng mục.

### Ý tưởng sau này

- [ ] Xuất báo cáo tuần dạng PDF / gửi kèm bản tin.
- [ ] So sánh nhiều thị trường cho cùng một game (rank VN vs US vs JP theo thời gian).
- [ ] Theo dõi đối thủ cụ thể: cảnh báo riêng khi game trong Watchlist đổi hạng mạnh hoặc ra bản cập nhật.
- [ ] Đóng gói chạy nền như Windows service / Docker để không cần đăng nhập Windows.

---

## ⚠️ Hạn chế đã biết

| Hạn chế | Ảnh hưởng | Ghi chú |
|---|---|---|
| Doanh thu & lượt tải là **ước tính** từ thứ hạng | Sai số lớn khi chưa hiệu chỉnh | Dùng tab Hiệu Chỉnh Mô Hình |
| Google Play rank = thứ tự tìm kiếm | Không phải top chart chính thức | Xem mục ưu tiên trung bình |
| App Store không có bảng "global" | Mục global chỉ có Google Play | Đã bỏ qua khi crawl |
| Radar sắp ra mắt chủ yếu là dữ liệu nhập tay | Ngày ra mắt / lượt đăng ký chưa xác minh | Có nhãn "Thủ công · chưa xác minh" |
| Review Steam bị chặn từ mạng hiện tại | Tab review game PC trống | Hiển thị lý do, không dùng review giả |
| Task tự động chỉ chạy khi đã đăng nhập Windows | Máy ở màn hình khóa đăng nhập thì task chờ | Không lưu mật khẩu Windows |
