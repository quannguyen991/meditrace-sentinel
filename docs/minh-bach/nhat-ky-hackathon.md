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
| 08:23 | 9 Sổ quyết định + bảng AI hỗ trợ / đội sửa | `867a783` | claude_code (agent) | Agent viết 11 quyết định + 2 bảng, test kiểm mọi commit trích là có thật; đội rà và sửa 2 dòng: dòng Codex ghi chi tiết chưa kiểm được → đổi thành chờ tác giả xác nhận; một dòng ghi Task 1 "bỏ sót" không đúng sự thật → xóa |
| 08:28 | 10 Tổng hợp trả lời BTC + hồi quy toàn bộ | `93ad035` | claude_code | Đội tự rà số liệu trong tài liệu khớp tệp kết quả (94,0%/93,8% chưa đạt ngưỡng ghi thẳng); hồi quy toàn bộ xanh |

## Sửa sau rà soát độc lập

Một agent riêng (mô hình mạnh nhất, không thấy quá trình làm) đọc toàn bộ nhánh và báo 1 lỗi nặng, 6 lỗi quan trọng, 6 lỗi nhỏ. Đội sửa lỗi nặng, lỗi quan trọng và 2 lỗi nhỏ có dính tới rò dữ liệu; mỗi lỗi có test tái hiện chạy đỏ trước khi sửa.

| Phát hiện | Test đỏ trước khi sửa | Ghi chú của đội |
|---|---|---|
| #1 BHYT/XML, TT26, cam đoan, đi buồng xuất được khi chưa ký | `web/src/lib/loiRaHoSo.test.ts` | Test còn bắt thêm lối mở TT26 thứ hai (từ bảng an toàn lâm sàng) mà rà soát chưa nêu; kiểm lại trên giao diện thật: 8/8 nút xuất khóa |
| #2 Log lỗi còn thô (ca-kham, tro-ly, tai-khoan, dung-chung) | `web/may-chu/log-da-che.test.ts` | |
| #10 Cắt chuỗi trước khi che (chặt đôi số điện thoại) | `che-log.test.ts`, `tests/test_che_log.py` | Rà soát xếp "nhỏ"; đội nâng lên vì đúng là rò |
| #3 Python bỏ sót họ tên viết thường | `tests/test_che_log.py`, bộ ca dùng chung | |
| #4 #5 Che nhầm "thứ 2", "viêm gan B.", "nhóm máu A.", "Thái Lan", "Lý Do Khám" | bộ ca dùng chung (8 ca mới) | Không đo tập test lần ba; dev giữ nguyên 97,5% / 97,3% |
| #8 Từ khóa tra cứu do mô hình đặt có thể mang tên thật | `web/may-chu/tra-cuu/loc-tu-khoa.test.ts` | Rà soát xếp "nhỏ"; đội nâng lên |
| #7 Hook không chạy trên macOS/Linux | `tests/test_kiem_trailer_commit.py` | Thêm quyền chạy, `python3`, `.gitattributes` giữ LF |
| #6 #9 Tài liệu nói quá ("bật cho từng lần", "tắt cả hai lớp", khóa ở máy chủ) | — | Sửa lời cho khớp mã |

## Gia cố bổ sung (vòng rà soát thứ hai, 28/11)

Sau lượt sửa đầu, đội tiếp tục rà soát và đóng các khoảng trống còn nêu trong mục hạn chế:

| Hạng mục | Kiểm chứng tự động | Ghi chú thực hiện |
|---|---|---|
| Chốt bản chụp lúc ký trên máy chủ (`ban_ky_duyet`, `layBanKyDeXuat`) và khóa đủ 6 route xuất (`tao-ma`, `bhyt/precheck`, `bhyt/recompile`, `fhir/recompile`, `informed-consent`, `ward-round-diff`) | `web/may-chu/kiem-ky-may-chu.test.ts`, `web/may-chu/routes/boost-lam-sang.test.ts`, `web/may-chu/routes/bhyt-ocr.test.ts`, `web/may-chu/routes/benh-nhan-portal.test.ts` | Gắn kiểm IDOR `403` trước `409` ở cam đoan PTTT; đồng bộ `CamDoanThuThuatModal.tsx` không fallback đóng dấu offline khi bị `409` |
| Che `procedureName` trước khi ghi vào bảng `nhat_ky` (`cheLog`) | `web/may-chu/routes/boost-lam-sang.test.ts` | Xác nhận tên/SĐT trong tên thủ thuật không lọt vào CSDL nhật ký |
| Tự xóa tệp ghi âm: 30 ngày sau duyệt & 7 ngày cho phiên chưa duyệt bị bỏ dở; kích hoạt `don_dinh_ky()` trong `dich_vu_http.py` | `tests/test_audio_xoa_qua_han.py`, `tests/test_dich_vu.py` | Giữ `session.json` + `audit.jsonl`, ghi sự kiện `am_thanh_da_xoa` |
| Gỡ Google Fonts khỏi `web/index.html`, dùng font hệ thống tiếng Việt | `web/src/lib/khongTaiNguonNgoai.test.ts` | Chặn tuyệt đối kết nối ngoài từ thẻ `<link>` / `<script>` |
