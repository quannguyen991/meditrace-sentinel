# Hackathon 6 tiếng — Đề cải tiến 1: Làm chủ và bảo vệ dữ liệu sức khỏe

Kế hoạch đầy đủ: [docs/superpowers/plans/2026-11-28-de-cai-tien-1-du-lieu-suc-khoe.md](superpowers/plans/2026-11-28-de-cai-tien-1-du-lieu-suc-khoe.md) (mục 1 có bảng chỗ hở H1–H8 kèm dòng mã).

**Nguyên tắc trong 6 tiếng:** mỗi việc xong là commit ngay, dòng cuối thông điệp ghi công cụ AI đã dùng (hoặc "tự viết"). Lịch sử commit của buổi hackathon chính là minh chứng "lịch sử sửa đổi" mà đề yêu cầu.

---

## Trước giờ G (không viết mã, chỉ chuẩn bị)

- [ ] Đọc luật hackathon: có được chuẩn bị mã trước không, được dùng AI tới mức nào, có phải ghi lại không.
- [ ] Máy chạy được: `pytest -q` xanh, `cd web; npm test` xanh, giao diện mở được và "Xem thử với ca mẫu" chạy.
- [ ] Có dữ liệu PhoNER ở `data/ngoai/PhoNER_COVID19/` (dùng cho P2).
- [ ] Mở sẵn các tệp: `web/src/components/NoteEditorView.tsx` (nút Chép HIS ~dòng 1516, Tải FHIR ~1660, Tờ dặn dò ~1529), `web/may-chu/routes/tra-cuu.ts`, `routes/dung-chung.ts` (dòng 175, 181), `routes/asr.ts` (175), `web/may-chu/an-danh-ngoai.ts`, `tro-ly/cai-dat-tro-ly.ts`.
- [ ] Bật công cụ ghi màn hình hoặc giữ cửa sổ chat AI để làm nhật ký lời nhắc.
- [x] Đã trả lời: AIBOX là bên thứ ba; chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI; đã bỏ câu "Đội ngũ Nghiên cứu Lâm sàng".
- [ ] Còn chờ: 33 commit cũ không ghi công cụ là do công cụ nào làm (không biết thì ghi "chưa xác định", không đoán).

---

## Lịch 6 tiếng

| Giờ | Việc | Xong khi | Đề hỏi gì |
|---|---|---|---|
| 0:00–0:15 | Tạo nhánh `hackathon-de-1`, chạy test lấy mốc, ghi giờ bắt đầu | test xanh, có commit mốc | — |
| 0:15–1:15 | **P1. Khóa chép/xuất trước khi ký**: hàm `choPhepDungHoSo(daKy, daSuaSauKy)` + test, nối vào Chép HIS, Tải FHIR, Tải Markdown, Tờ dặn dò | chưa ký thì khóa; ký thì mở; sửa sau ký thì khóa lại; chụp 3 ảnh | quy trình bác sĩ phê duyệt |
| 1:15–2:15 | **P3. Bịt đường ra**: PubMed chạy qua bộ che, còn tên thì trả 422; `cheLog()` cho 3 chỗ log; test quét mọi `fetch(` trong `web/may-chu` theo danh sách cho phép | 3 test mới xanh | không đưa dữ liệu nhận dạng vào dịch vụ/log |
| 2:15–2:30 | Nghỉ, đệm thời gian | — | — |
| 2:30–3:30 | **P2. Đo bộ che ở cổng ra trên PhoNER**: đo trước khi sửa → vá "bệnh nhân 416", "BN 416", "bà H.T.P" → đo sau | có bảng trước/sau | bằng chứng bằng số |
| 3:30–3:50 | **P4. Công tắc quản trị mặc định TẮT** + test | test xanh | chọn tham gia, không mặc định gửi |
| 3:50–4:50 | **P7 + P5. Minh chứng**: sơ đồ dữ liệu (Mermaid + bảng nơi lưu + bảng đường ra); quy trình phê duyệt kèm ảnh P1; sổ 10 quyết định thiết kế; bảng "AI làm gì / đội làm gì / các lần đội sửa AI" | 4 tệp trong `docs/minh-bach/` | quyết định thiết kế, AI hỗ trợ, đội tự sửa, sơ đồ dữ liệu |
| 4:50–5:20 | **P6 rút gọn**: bảng commit của buổi hackathon kèm công cụ; README mục "Công cụ AI" thêm Antigravity và ChatGPT | README sửa xong | lịch sử sửa đổi |
| 5:20–5:45 | **P8**: `TRA_LOI_DE_CAI_TIEN_1.md` 2 trang (ý đề → câu trả lời → minh chứng → lệnh kiểm); chạy toàn bộ test + build | mọi thứ xanh | tổng hợp |
| 5:45–6:00 | Tập demo 3 phút, đóng băng | — | — |

**Luật cắt việc:**
- Đến 3:00 mà chưa xong P3 thì P2 chỉ đo, không vá; ghi số thật vào tài liệu. **P4 không được bỏ** (AIBOX là bên thứ ba, nên đường ra phải mặc định tắt); nó chỉ mất khoảng 20 phút.
- Đến 3:50, dù đang dở việc gì cũng chuyển sang viết minh chứng. Mã đẹp mà không có minh chứng thì không trả lời được đề.
- P6 đầy đủ (truy nguồn 78 commit cũ) để thành "việc tiếp theo".

---

## Demo 3 phút

1. **(40 giây) Phê duyệt trước khi dùng.** Mở ca mẫu: nút Chép HIS và Tải FHIR đang khóa, rê chuột thấy "chưa ký". Xử lý mục *Cần bác sĩ xác nhận* rồi ký: các nút mở. Sửa một dòng: các nút khóa lại và đòi ký lại.
2. **(40 giây) Dữ liệu không ra ngoài.** Gõ "Nguyễn Văn An đau ngực" vào ô tìm PubMed: bị từ chối. Mở sơ đồ dữ liệu: chỉ có một đường ra mô hình ngoài, qua 2 công tắc, bộ che và bước từ chối.
3. **(30 giây) Có test giữ.** Chạy test quét đường ra mạng; thêm thử một `fetch("https://la.example")`: test đỏ.
4. **(40 giây) Đội làm chủ AI.** Mở bảng "các lần đội sửa AI", ví dụ commit `2fc4eba` sửa 3 lỗi do Antigravity viết (đổi "mi" thành "mày", cảnh báo liều nhầm, viết tắt DIA). Mở sổ quyết định: chỉ Bước 1 dùng AI, chạy tại chỗ, không tự duyệt bảng thuốc.
5. **(30 giây) Trung thực.** Bộ che đạt X% trên PhoNER (văn bản tin tức, chưa phải hội thoại khám). Những gì chưa làm được nằm ở mục "việc tiếp theo".

## Câu giám khảo có thể hỏi

- *"AI viết bao nhiêu phần trăm mã?"* → Trỏ bảng "AI làm / đội làm" và lịch sử commit có ghi công cụ. Không đưa ra con số phần trăm nếu không đo được.
- *"Bộ che mà sót thì sao?"* → Che xong vẫn kiểm lại lần cuối; còn dấu hiệu định danh thì **không gửi** (từ chối ngay, 422). Đường ra mặc định tắt ở cả hai lớp.
- *"Mô hình ngoài là của ai?"* → Cổng AIBOX là dịch vụ của bên thứ ba, đội không kiểm soát được việc họ lưu dữ liệu. Vì vậy đường này là tính năng phụ, mặc định tắt, chỉ nhận văn bản đã che. Phần lõi (chép lời, trích mệnh đề, luật, ký duyệt) không cần đường này và chạy hoàn toàn tại chỗ.
- *"Có đưa hồ sơ bệnh nhân thật vào AI khi phát triển không?"* → Không. Khi phát triển chỉ dùng dữ liệu mô phỏng và bộ dữ liệu công khai.
- *"Bản demo trên mạng có an toàn không?"* → Bản demo đi qua Cloudflare nên chỉ dùng dữ liệu mô phỏng. Bản cho phòng khám chạy hoàn toàn tại chỗ.
- *"Bác sĩ bấm duyệt bừa thì sao?"* → Không ký được khi còn mục chưa xử lý. Ký xong được ghi vào sổ không sửa được, sửa sau khi ký thì phải ký lại. Đo mức duyệt bừa là việc tiếp theo (thử người dùng có cấy sẵn lỗi).
