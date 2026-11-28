# AI hỗ trợ phần nào, đội tự kiểm và sửa phần nào

Tác giả xác nhận ngày 28/11/2026: "Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào." và "Cổng mô hình ngoài AIBOX là dịch vụ bên thứ ba."

Mỗi dòng có cột *Bằng chứng* là mã commit hoặc tệp có thật; `tests/test_minh_chung_trich_commit.py` kiểm từng mục. Tài liệu này không ghi tỷ lệ phần trăm mã do AI viết, vì chưa có phép đo nào cho con số đó. Công cụ của từng commit cũ được liệt kê ở `docs/minh-bach/truy-nguon-commit.md`; commit không ghi công cụ được để `chua_xac_dinh`, không đoán.

## Bảng 1. Từng phần của dự án

| Phần | AI hỗ trợ | Đội làm | Công cụ | Bằng chứng |
|---|---|---|---|---|
| Dữ liệu mô phỏng | Viết mã sinh hội thoại theo khuôn, biến thể câu, phương ngữ | Chọn cách sinh bằng luật thay vì nhờ mô hình lớn viết hội thoại; đặt khuôn bệnh; chia tập theo khuôn để mô hình không thấy trước bài kiểm tra | Claude Code; Antigravity (mở rộng phương ngữ 27/11) | `src/bo_du_lieu/sinh_hoi_thoai_viet.py`, `src/bo_du_lieu/chia_tap_theo_khuon.py`, `bffaa3c` |
| Huấn luyện | Viết mã huấn luyện QLoRA, DPO, hàm mất mát tiết kiệm bộ nhớ | Chạy trên máy của đội, đọc kết quả, quyết định không dùng bản DPO | Claude Code | `src/huan_luyen/huan_luyen_sft.py`, `src/huan_luyen/huan_luyen_dpo.py`, `docs/ket-qua/dpo-v3.md` |
| Luật K1–K7 (kiểm căn cứ) | Viết mã luật theo yêu cầu | Đặt luật, đăng ký trước cách đo, chỉ chạy tập giữ kín một lần | Claude Code | `src/duong_ong/b4_kiem_can_cu.py`, `docs/dang-ky-truoc-bo-luat.md` |
| Cảnh báo | Viết mã phát hiện lỗi, các vòng vá điểm mù | Đo trên tập điều chỉnh 400 ca trước khi nhận một vòng vá | Claude Code; Antigravity (một số chốt 27/11) | `src/canh_bao/phat_hien.py`, `397ddbb`, `8120ce4` |
| Đo lường | Viết công cụ đo, chấm điểm | Chạy lại phép đo, ghi số thật kể cả khi chưa đạt mục tiêu | Claude Code | `src/do_luong/do_canh_bao.py`, `docs/ket-qua/bo-sot-v3-v1.md`, `a4fb3d6` |
| Giao diện | Viết mã React và máy chủ web | Thử trên giao diện thật, chụp ảnh các trạng thái, yêu cầu bớt nút và bớt chữ | Claude Code; Antigravity (một số commit 25–26/11) | `web/src/components/NoteEditorView.tsx`, `ac254bb`, `eef14d2` |
| Mô-đun âm thanh | Viết một mô-đun âm thanh (README ghi Codex) | Mô-đun cụ thể chờ tác giả xác nhận; không đoán | Codex | `src/audio/README.md` |
| Sắp xếp mã nguồn | Chia `src/` thành 6 gói | Chạy lại toàn bộ test sau khi chia | Antigravity | `1878711` |
| Tài liệu | Soạn README, sổ tay, báo cáo | Đối chiếu từng con số với tệp kết quả; rút hoặc đánh dấu số không có lần đo | Claude Code; Antigravity | `docs/doi-chieu-so-lieu-bao-cao.md`, `7b3a635` |
| Ảnh | Ảnh minh họa | Ảnh chụp giao diện trong `docs/minh-bach/anh/` là ảnh đội chụp từ phần mềm thật, không phải ảnh AI vẽ | ChatGPT (ảnh minh họa) | `f111b14`, `docs/minh-bach/anh/khoa-truoc-ky-1.jpg` |

## Bảng 2. Những lần đội bác bỏ hoặc sửa đầu ra của AI

| Lần đội bác bỏ hoặc sửa đầu ra AI | Lỗi | Cách phát hiện | Bằng chứng |
|---|---|---|---|
| Sửa 3 lỗi trong mã Antigravity viết ở `8120ce4` | Chữ "mi" (mí mắt) bị đổi thành "mày"; số không phải liều thuốc vẫn bật cảnh báo DOSE_MISMATCH; chữ viết tắt in hoa như "DIA" bị coi là nhiễu nhận dạng tiếng nói | Đội rà lại mã sau commit của Antigravity và chạy lại phép đo | `2fc4eba`, `8120ce4` |
| Kiểm toán tầng Python do Antigravity viết | Lỗi ở khử định danh, BHYT, FHIR, cận lâm sàng | Rà soát từng mô-đun và viết thêm phép thử | `e9a1866` |
| Rà soát độc lập 26/11, hai lượt (Python và web) | 9 lỗi nghiêm trọng, ví dụ khóa kiểm liều coi "5 mg" khớp "2.5 mg", thiếu tuổi thì ngầm lấy 50 | Một lượt rà soát riêng; mỗi lỗi có phép thử hồi quy; chạy lại số đo cảnh báo sau khi sửa | `2286ee0`, `7d00a2a`, `docs/ket-qua/canh-bao-moc-0.md` |
| Vòng 6 vá 4 điểm mù của lớp cảnh báo | Bỏ qua lỗi đổi bên, đổi mức độ, nhầm quá khứ/hiện tại, đính chính ngược | Đo trên tập điều chỉnh 400 ca, không chạy lại tập giữ kín | `397ddbb`, `docs/ket-qua/cay-loi.md` |
| Bảng thuốc cũ ghi sintrom là biệt dược của warfarin | Sintrom là acenocoumarol, không phải warfarin; bảng cũ còn ghi trần liều warfarin cố định | Đọc lại từng mục bảng thuốc khi gom về một nguồn | `docs/tri-thuc-thuoc-can-duyet.md`, `data/tri_thuc_thuoc.json`, `e9a1866` |
| Bảng so sánh GPT-4o / Gemini / Claude / Llama trong tài liệu | Có số liệu nhưng không có tệp kết quả, lệnh gọi hay mã nào chạy các mô hình đó | Đối chiếu từng con số với `src/`, `tools/`, `docs/ket-qua/`; bảng bị đánh dấu "chưa có bằng chứng" | `docs/doi-chieu-so-lieu-bao-cao.md`, `docs/tai-lieu/BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md` |
| Con số "78,3% đa dạng" trong tài liệu cũ | Không có phép đo tương ứng trong mã; đo lại không ra con số đó | Đo lại bộ dữ liệu bằng mã | `docs/BAN-GIAO-CONG-VIEC-DANG-DO.md`, `docs/do-lap-lai-bo-du-lieu.md` |
| Con số bỏ sót 11,8% được ghi như số đo chung | Số này đo trên tập phát triển dùng để viết luật | Đọc lại nguồn của con số | `2fc4eba` |
| Hackathon 28/11, Task 4: danh sách lối ra mạng | Test quét lối ra bắt được chính chú thích có chữ `fetch(` trong tệp danh sách | Chạy test; đội sửa chú thích, giữ test nghiêm | `054c8b3`, `web/may-chu/loi-ra-mang.test.ts` |
| Hackathon 28/11, Task 5: đường ra bên thứ ba mặc định tắt | Luật mới để biến môi trường bật đè lên việc quản trị bấm tắt | Test cũ của dự án báo lỗi; đội đổi thứ tự để quản trị tắt luôn thắng | `8b752da`, `web/may-chu/tro-ly/cai-dat-tro-ly.test.ts` |
| Hackathon 28/11, Task 2–3: bộ che định danh | Trên tập kiểm tra chưa đạt 0,95 (TS 0,940, Python 0,938) | Đo tập kiểm tra đúng hai lần; đội giữ số thật, không vá thêm theo tập kiểm tra | `a4fb3d6`, `docs/ket-qua/an-danh-phoner.md` |
| Rà soát độc lập cuối buổi hackathon (một agent riêng đọc toàn bộ nhánh) | 4 nút BHYT/XML, đơn thuốc TT26, cam đoan, đi buồng vẫn xuất được khi chưa ký; vài dòng log còn thô; bộ che Python bỏ sót họ tên viết thường và hai bộ che che nhầm "sốt từ thứ 2", "viêm gan B."; từ khóa tra cứu có thể mang tên thật; hook không chạy trên macOS/Linux | Đội viết test tái hiện từng lỗi (đỏ trước), sửa, chạy lại toàn bộ; test quét lối xuất còn bắt thêm một lối mở thứ hai mà rà soát chưa nêu | `web/src/lib/loiRaHoSo.test.ts`, `web/may-chu/log-da-che.test.ts`, `web/may-chu/tra-cuu/loc-tu-khoa.test.ts` |
| Hackathon 28/11, Task 8: truy nguồn commit | Agent không được sửa README | Đội chạy lại test, thử hook chặn commit thiếu dòng công cụ, tự sửa mục Công cụ AI | `9f290d2`, `tools/kiem_trailer_commit.py` |
