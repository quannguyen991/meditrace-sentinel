# Nhật ký hackathon — Đề cải tiến 1 (28/11/2026)

Bắt đầu: 07:50, nhánh `hackathon-de-1`. Đường cơ sở: pytest 1.960 passed / 27 skipped; web 96/96 pass.

Mỗi dòng: giờ · task · commit · công cụ AI · đội đã sửa/bác bỏ gì ở đầu ra AI.

| Giờ | Task | Commit | Công cụ AI | Đội kiểm / sửa |
|---|---|---|---|---|
| 08:00 | 1 Khóa chép/in/xuất trước khi ký | (commit này) | claude_code | Đội kiểm trên giao diện thật 3 trạng thái (chưa ký / đã ký / sửa sau ký), chụp 3 ảnh; phát hiện menu Công cụ có SBAR/HIS/Tờ dặn dò nằm trong menu xổ xuống, đã khóa cả ở đó |
| 08:01 | 8 Truy nguồn commit + hook | (commit này) | claude_code (agent) | Agent viết tool + 13 test; đội chạy lại test, thử hook chặn commit thiếu trailer (exit 1), tự sửa README mục Công cụ AI (agent bị cấm sửa README) |
| 08:08 | 4 Che log, chặn PubMed, danh sách lối ra | (commit này) | claude_code | Test quét lối ra tự bắt được chính chú thích chứa chữ fetch( trong tệp danh sách — đội sửa chú thích, giữ test nghiêm; ghi rõ hàm layChu (NCBI/IRIS/openFDA) khác layWeb khi đọc lại mã |
