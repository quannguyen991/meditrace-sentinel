# Nhật ký hackathon — Đề cải tiến 1 (28/11/2026)

Bắt đầu: 07:50, nhánh `hackathon-de-1`. Đường cơ sở: pytest 1.960 passed / 27 skipped; web 96/96 pass.

Mỗi dòng: giờ · task · commit · công cụ AI · đội đã sửa/bác bỏ gì ở đầu ra AI.

| Giờ | Task | Commit | Công cụ AI | Đội kiểm / sửa |
|---|---|---|---|---|
| 08:00 | 1 Khóa chép/in/xuất trước khi ký | `f111b14` | claude_code | Đội kiểm trên giao diện thật 3 trạng thái (chưa ký / đã ký / sửa sau ký), chụp 3 ảnh; mở cả menu Công cụ xổ xuống để kiểm SBAR, Chép HIS, Tờ dặn dò cũng khóa |
| 08:01 | 8 Truy nguồn commit + hook | `9f290d2` | claude_code (agent) | Agent viết tool + 13 test; đội chạy lại test, thử hook chặn commit thiếu trailer (exit 1), tự sửa README mục Công cụ AI (agent bị cấm sửa README) |
| 08:08 | 4 Che log, chặn PubMed, danh sách lối ra | `054c8b3` | claude_code | Test quét lối ra tự bắt được chính chú thích chứa chữ fetch( trong tệp danh sách — đội sửa chú thích, giữ test nghiêm; ghi rõ hàm layChu (NCBI/IRIS/openFDA) khác layWeb khi đọc lại mã |
| 08:10 | 5 Đường ra bên thứ ba mặc định tắt + cảnh báo bản demo | `8b752da` | claude_code | Test cũ của dự án bắt được lỗi trong luật mới (env bat đè quản trị bấm tắt) — đội đổi thứ tự ưu tiên để quản trị tắt luôn thắng |
| 08:11 | 2–3 Bộ ca rò rỉ dùng chung, đo và vá hai bộ che | `a4fb3d6` | claude_code (agent) | Agent vá trên dev, đo test đúng 2 lần; test chưa đạt 0,95 (TS 0,940, Python 0,938) — đội giữ nguyên số thật, không vá thêm theo test để tránh học tủ |
| 08:14 | 6 Sơ đồ dữ liệu sinh từ mã | `586e066` | claude_code | Khi đọc lại mã để điền nơi lưu, đội phát hiện trình duyệt cũng giữ bản sao danh sách ca khám có tên bệnh nhân (localStorage) — ghi thẳng vào bảng thay vì bỏ qua |
| 08:15 | 7 Quy trình phê duyệt | `6bd6377` | claude_code | Đội tự kiểm thêm trường hợp đổi quyết định duyệt sau ký (giữ → bỏ) cũng phải khóa lại; ghi rõ 2 giới hạn không chặn được (bôi đen Ctrl+C, Ctrl+P) |
| 08:23 | 9 Sổ quyết định + bảng AI hỗ trợ / đội sửa | (commit này) | claude_code (agent) | Agent viết 11 quyết định + 2 bảng, test kiểm mọi commit trích là có thật; đội rà và sửa 2 dòng: dòng Codex ghi chi tiết chưa kiểm được → đổi thành chờ tác giả xác nhận; một dòng ghi Task 1 "bỏ sót" không đúng sự thật → xóa |
