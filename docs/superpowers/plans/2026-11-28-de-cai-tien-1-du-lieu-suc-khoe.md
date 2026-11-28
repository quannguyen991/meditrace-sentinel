# Đề cải tiến 1 (BTC, 28/11/2026): Làm chủ và bảo vệ dữ liệu sức khỏe — Kế hoạch

> **Cho người/agent thực thi:** superpowers:executing-plans. Đây là **Pha 0** của [kịch bản v2](2026-11-28-kich-ban-nang-cap-v2.md): làm trước mọi pha khác vì BTC đã giao đề chính thức.

**Đề của BTC (nguyên văn ý chính):**
- *Vấn đề:* quá trình dùng AI để phát triển sản phẩm và phạm vi xử lý thông tin bệnh nhân cần minh bạch hơn.
- *Yêu cầu:* trình bày quyết định thiết kế, những nội dung AI hỗ trợ và đội tự đánh giá/sửa; không đưa dữ liệu bệnh nhân nhận dạng được vào dịch vụ/log trái phép.
- *Minh chứng:* lịch sử sửa đổi, sơ đồ dữ liệu, quy trình bác sĩ phê duyệt trước khi dùng hồ sơ.

**Mục tiêu:** Có ba bộ minh chứng kiểm chứng được bằng mã và test (không chỉ bằng lời), và đóng các chỗ hở đã tìm thấy khi rà ngày 28/11.

---

## 1. Kết quả rà soát 28/11 (đọc mã thật)

### Đã làm tốt — dùng làm minh chứng

| Điểm | Chỗ trong mã |
|---|---|
| Chép lời (PhoWhisper) và trích mệnh đề (Qwen3-4B) chạy **tại chỗ**, không gửi âm thanh hay lời thoại ra ngoài | `src/audio/`, `src/he_thong/dich_vu_http.py` |
| **Một lối ra duy nhất** tới mô hình ngoài: `goiNgoai()`. Phải qua 2 công tắc (quản trị + bác sĩ bật cho từng lần), giới hạn lượt, che định danh, và **từ chối gửi** nếu còn sót định danh (422 `con_danh_tinh`) | `web/may-chu/routes/llm-ngoai.ts`, `web/may-chu/an-danh-ngoai.ts` |
| Nhật ký hoạt động chỉ ghi siêu dữ liệu (hành động, mã phiên, số đếm), không ghi nội dung ca khám; trợ lý có ràng buộc "không ghi chuỗi đã gửi ra ngoài" | `web/may-chu/csdl.ts` `ghiNhatKy`, `web/may-chu/tro-ly/chay-viec.ts` |
| Ký duyệt bị **chặn cứng** khi còn mục "Cần bác sĩ xác nhận" chưa xử lý hoặc mệnh đề thiếu lượt căn cứ; ký ghi vào sổ WORM có băm SHA-256 và HMAC; sửa sau khi ký thì phải ký lại | `web/src/lib/compileEffectiveNote.ts` `kiemTraDieuKienKyDuyet`, `web/may-chu/worm.ts`, `NoteEditorView.tsx` (`daSuaSauKy`) |
| Kho GitHub không chứa CSDL, âm thanh hay khóa bí mật; dữ liệu trong kho là dữ liệu mô phỏng | `git ls-files` |
| Đã có nhật ký lời nhắc AI gắn với commit, có che thông tin nhạy cảm | `src/he_thong/nhat_ky_loi_nhac.py`, `NHAT_KY_LOI_NHAC_VA_KHAI_MA_NGUON.md` |
| Worker Cloudflare chỉ chuyển tiếp, mã không lưu hay đọc nội dung | `trien-khai/cloudflare/src/index.js` |

### Chỗ hở — phải sửa (xếp theo mức nặng)

| # | Chỗ hở | Bằng chứng | Hệ quả |
|---|---|---|---|
| H1 | **Hồ sơ dùng được trước khi bác sĩ ký.** Nút *Chép HIS*, *Tải FHIR & BHYT (.json)*, *Tải Markdown*, *Tờ dặn dò người bệnh* không kiểm trạng thái ký; chỉ nút *Ký* bị chặn | `NoteEditorView.tsx` dòng ~1516 (Chép HIS), ~1660 (FHIR), ~1529 (dặn dò) | Trái trực tiếp minh chứng "bác sĩ phê duyệt trước khi dùng hồ sơ" |
| H2 | **Che định danh chưa được đo trên dữ liệu ngoài.** Bộ che tiếng Việt của Python chỉ che được 1,2% (10/847) tên/mã bệnh nhân trên PhoNER (`docs/ket-qua/da-nguon-doc-lap.json`); bộ che ở cổng ra (TypeScript) chưa đo lần nào. Dạng "bệnh nhân 416", "bà H.T.P" có thể lọt | `an-danh-ngoai.ts`, `src/he_thong/khu_dinh_danh.py` | Cổng ra dựa vào bộ che; không có số thì không chứng minh được "không đưa dữ liệu nhận dạng ra ngoài" |
| H3 | **Tra PubMed gửi thẳng từ khóa ra NCBI**, không qua bộ che và không cần bật công tắc | `web/may-chu/routes/tra-cuu.ts` `/api/pubmed-search` | Nếu bác sĩ gõ tên bệnh nhân vào ô tìm, tên đi ra ngoài |
| H4 | **Log máy chủ có thể chứa nội dung ca khám khi lỗi:** in 200 ký tự đầu đầu ra Python khi JSON hỏng, 2.000 ký tự cuối stderr, và toàn bộ stack lỗi bản nháp | `routes/dung-chung.ts:175,181`, `routes/asr.ts:175` | "Log trái phép" theo đúng chữ của đề |
| H5 | **Công tắc quản trị mặc định là BẬT** (chỉ tắt khi đặt `tat`) | `tro-ly/cai-dat-tro-ly.ts` `ngoaiBat` | Nên là chọn tham gia (mặc định tắt) ở cả hai lớp |
| H6 | **Lịch sử sửa đổi không ghi đủ công cụ AI.** 33/78 commit không có dòng ghi công cụ (các commit của Antigravity ngày 27/11 cũng vậy). README chỉ kể Claude Code và Codex; chưa kể Antigravity và ChatGPT (ảnh) | `git log`, README mục "Công cụ AI đã dùng" | Đề hỏi đúng "những nội dung AI hỗ trợ" |
| H7 | **Tài liệu khai cũ và có câu nói quá:** `BANG_KE_KHAI…` ghi "1.330 test", "8 chốt", và "Đội ngũ Nghiên cứu Lâm sàng" | các tệp `*.md` gốc repo | Giám khảo đối chiếu sẽ thấy lệch |
| H8 | Phông Google tải từ `fonts.googleapis.com` | `web/index.html` | Không lộ dữ liệu bệnh nhân (chỉ địa chỉ IP), nhưng phòng khám ngoại tuyến sẽ thiếu phông. Mức nhẹ |

---

## 2. Các việc

Thứ tự: P1 → P2 → P3 → P4 (mã, có test) rồi P5 → P6 → P7 (minh chứng), P8 cuối. P5 và P6 làm song song với mã được.

### P1. Khóa dùng hồ sơ trước khi ký (H1)

**Files:** Create `web/src/lib/choPhepDungHoSo.ts` + `choPhepDungHoSo.test.ts`; Modify `web/src/components/NoteEditorView.tsx`.
**Interface:** `choPhepDungHoSo(daKy: boolean, daSuaSauKy: boolean): { duoc: boolean; lyDo: string | null }`.

- [ ] **Test:** `chưa ký → duoc=false, lyDo chứa "chưa ký"`; `đã ký, chưa sửa → duoc=true`; `đã ký rồi sửa → duoc=false, lyDo chứa "ký lại"`.
- [ ] Chạy `cd web; npx tsx --test src/lib/choPhepDungHoSo.test.ts` → FAIL, cài đặt, PASS.
- [ ] Nối vào bốn nút: Chép HIS, Tải FHIR & BHYT, Tải Markdown, Tờ dặn dò (và SBAR nếu xuất ra ngoài). Khi `!duoc`: nút mờ, `title` = `lyDo`, bấm không làm gì. **Xem trên màn hình vẫn được**; chỉ chặn đưa ra khỏi phần mềm.
- [ ] Kiểm trong trình duyệt bằng ca mẫu: trước khi ký thì bốn nút bị khóa; ký xong thì mở; sửa một dòng thì khóa lại. Chụp màn hình làm minh chứng.
- [ ] `npm run lint; npm test` xanh. Commit `feat(web): khoa chep HIS/xuat FHIR/to dan do truoc khi bac si ky duyet`.

### P2. Đo và vá bộ che định danh ở cổng ra (H2)

**Files:** Create `web/may-chu/do-an-danh-phoner.ts` (script đo), `docs/ket-qua/an-danh-cong-ra.md`; Modify `web/may-chu/an-danh-ngoai.ts`, `an-danh-ngoai.test.ts`.

- [ ] **Đo trước khi sửa (mốc 0):** chạy `anDanhChoNgoai` trên 1.000 câu PhoNER test (`data/ngoai/PhoNER_COVID19/.../test_syllable.json`), nhãn vàng `NAME` + `PATIENT_ID`. Ghi: tỷ lệ nhãn bị che, và **tỷ lệ câu bị từ chối gửi** (fail-closed cũng là bảo vệ). Đo thêm tỷ lệ che nhầm trên 300 câu y khoa không có định danh (ViMedAQA) để biết bộ che có làm hỏng nội dung lâm sàng không.
- [ ] **Test hồi quy viết trước:** `"bệnh nhân 416"`, `"BN 416"`, `"bà H.T.P"`, `"ông N.V.A, 67 tuổi"` → không còn chuỗi gốc sau khi che **hoặc** bị từ chối gửi. Và `"đau ngực 3 ngày"`, `"uống paracetamol 500 mg"` → giữ nguyên.
- [ ] Vá luật cho đến khi test xanh. **Ngưỡng:** che hoặc từ chối ≥ 95% nhãn `NAME`/`PATIENT_ID`; che nhầm câu y khoa ≤ 5%. PhoNER là văn bản tin tức, không phải hội thoại khám: báo cáo ghi rõ giới hạn này.
- [ ] Bộ che Python (`khu_dinh_danh.py`, 1,2%): kiểm nó được dùng ở đâu. Nếu chỉ để đo thì ghi rõ trong sơ đồ dữ liệu; nếu nằm trên đường dữ liệu thật thì áp cùng luật hoặc gọi chung một bộ.
- [ ] Commit kết quả đo trước/sau.

### P3. Bịt PubMed và log (H3, H4)

**Files:** Modify `routes/tra-cuu.ts`, `routes/dung-chung.ts`, `routes/asr.ts`; Create `web/may-chu/che-log.ts` + test.
**Interface:** `cheLog(s: string, toiDa = 300): string` cắt ngắn, chạy `anDanhChoNgoai`. Nếu còn định danh thì chỉ trả `"[đã ẩn n ký tự]"`.

- [ ] **Test:** `cheLog("Bệnh nhân Nguyễn Văn An 0912345678 ...")` không chứa "Nguyễn Văn An" và "0912345678"; chuỗi dài 5.000 ký tự → kết quả ≤ 300 ký tự.
- [ ] `/api/pubmed-search`: chạy `anDanhChoNgoai(q)`. Còn định danh → 422 kèm câu "Ô tìm tài liệu không nhận tên/mã bệnh nhân". Test route: `q="Nguyễn Văn An đau ngực"` → 422; `q="chest pain troponin"` → 200 (giả lập fetch).
- [ ] Ba chỗ log ở H4 đổi sang `cheLog(...)`. Đầu ra Python khi JSON hỏng chỉ log độ dài và 12 ký tự băm, không log nội dung.
- [ ] **Test quét lối ra mạng** `web/may-chu/loi-ra-mang.test.ts`: đọc mọi tệp `.ts` trong `web/may-chu` (trừ test), tìm `fetch(`, và FAIL nếu xuất hiện lối ra mới ngoài danh sách cho phép (dịch vụ Python nội bộ `API`, `NGOAI.base`, nguồn tra cứu trong `tra-cuu/nguon-ngoai.ts`). Từ đây, thêm một lối ra mới bắt buộc phải sửa danh sách, và danh sách chính là phụ lục của sơ đồ dữ liệu.
- [ ] Commit.

### P4. Công tắc quản trị mặc định tắt (H5)

- [ ] **Test:** `ngoaiBat(db_trong, {})` → `false`; sau `ghiNgoaiBat(db, true)` → `true`; `MEDITRACE_TRO_LY_NGOAI=tat` luôn `false`.
- [ ] Đổi `ngoaiBat` thành `docKhoa(...) === "bat"`. Cập nhật README mục biến môi trường. Trên máy demo, quản trị bật lại bằng giao diện (có ghi nhật ký `tro_ly_cong_tac_ngoai`).
- [ ] Commit.

### P5. Sổ quyết định thiết kế và vai của AI (minh chứng "quyết định thiết kế / AI hỗ trợ / đội tự sửa")

**Files:** Create `docs/minh-bach/so-quyet-dinh-thiet-ke.md`, `docs/minh-bach/ai-ho-tro-va-doi-tu-sua.md`.

- [ ] **Sổ quyết định:** 10–15 quyết định, mỗi quyết định gồm *vấn đề → các phương án → chọn gì → vì sao → ai quyết (đội) → commit/tài liệu*. Ứng viên đã có bằng chứng trong lịch sử:
  - chỉ Bước 1 dùng AI, các bước sau là luật đọc được;
  - chạy tại chỗ, không gửi lời thoại ra ngoài;
  - mô hình thương mại chỉ để đo, không nằm trong sản phẩm;
  - không tự đặt `da_duyet=true` cho bảng thuốc;
  - chính sách C là mặc định, D chỉ là tùy chọn;
  - không nhận DPO và mô hình v3 vì số không tốt hơn;
  - niêm phong tập kiểm tra cuối;
  - không hứa "giảm thời gian làm hồ sơ" sau khi hỏi bác sĩ;
  - bỏ XGrammar vì đã có cơ chế ép JSON;
  - ghi nhãn "tập phát triển" cho con số 11,8%.
- [ ] **AI hỗ trợ gì, đội làm gì:** bảng theo từng phần (dữ liệu, mô hình, luật, đo lường, giao diện, tài liệu, hình ảnh):

  | Phần | AI làm | Đội làm | Công cụ |
  |---|---|---|---|

  Kèm danh sách **các lần đội bác bỏ hoặc sửa đầu ra của AI**, mỗi dòng có commit. Ví dụ:
  - `2fc4eba` sửa 3 lỗi trong mã Antigravity viết (đổi "mi" thành "mày", cảnh báo liều nhầm, viết tắt DIA);
  - rà soát 26/11 tìm ra 9 lỗi nặng;
  - bảng thuốc cũ ghi sai sintrom = warfarin;
  - bảng so sánh GPT-4o/Gemini/Claude không có lần chạy nào nên bị rút (`docs/doi-chieu-so-lieu-bao-cao.md`);
  - con số "78,3%" chưa đo nên bị bỏ.
- [ ] **Chỉ ghi điều có bằng chứng.** Dòng nào không tìm được commit hoặc tài liệu thì để trống và hỏi tác giả, không tự điền.

### P6. Lịch sử sửa đổi có truy nguồn (H6, H7)

**Files:** Create `tools/truy_nguon_commit.py`, `tests/test_truy_nguon_commit.py`, `docs/minh-bach/truy-nguon-commit.md`.
**Interface:** `phan_loai_commit(thong_diep: str, tac_gia: str) -> str` trả `"claude_code"` (có `Co-Authored-By: Claude`), `"chua_ro"` (không có dòng ghi công cụ), hoặc nhãn do tác giả ghi đè trong `docs/minh-bach/truy-nguon-ghi-de.json`.

- [ ] **Test:** thông điệp có `Co-Authored-By: Claude Opus 5.5` → `claude_code`; không có → `chua_ro`; mã commit có trong tệp ghi đè → nhãn ghi đè.
- [ ] Tool sinh bảng 78 commit: ngày, tóm tắt, công cụ, tệp chạm tới, có test kèm không. Commit `chua_ro` để **tác giả xác nhận** (Antigravity, tự viết, hay công cụ khác). Không đoán.
- [ ] Từ nay mọi commit ghi công cụ ở dòng cuối thông điệp. Ghi luật này vào README mục đóng góp, và nhắc trong lời nhắc bàn giao cho Antigravity.
- [ ] README mục "Công cụ AI đã dùng": thêm Antigravity và ChatGPT (ảnh), mỗi công cụ một câu nói đã làm gì, trỏ tới `ai-ho-tro-va-doi-tu-sua.md`.
- [ ] Sửa các tài liệu khai cũ: số test và số chốt theo số đo mới. (Câu "Đội ngũ Nghiên cứu Lâm sàng" đã bỏ ngày 28/11 theo xác nhận của tác giả.)
- [ ] Commit.

### P7. Sơ đồ dữ liệu và quy trình phê duyệt (minh chứng 2, 3)

**Files:** Create `docs/minh-bach/so-do-du-lieu.md`, `docs/minh-bach/quy-trinh-phe-duyet.md`; ảnh chụp trong `docs/minh-bach/anh/`.

- [ ] **Sơ đồ dữ liệu** (Mermaid, kèm bảng):
  - Luồng chính: micro → trình duyệt → máy chủ web (HoaiĐức) → dịch vụ Python tại chỗ (ASR, Qwen3-4B, luật) → SQLite tại chỗ.
  - Lối ra mô hình ngoài: chỉ qua `goiNgoai`, đi qua 2 công tắc, bộ che và bước từ chối.
  - Tra cứu tài liệu: chỉ từ khóa đã che.
  - Phông chữ: chỉ địa chỉ IP.
  - Bản demo: đi qua Cloudflare Worker và đường hầm. Cloudflare có thấy lưu lượng đã giải mã TLS, nên bản demo **chỉ dùng dữ liệu mô phỏng**; cần ghi điều này lên màn hình đăng nhập.
  - Bảng *mọi nơi lưu dữ liệu* (CSDL ca khám, bản sao, sổ WORM, nhật ký hoạt động, tệp âm thanh, log tiến trình): lưu gì, có định danh không, ai đọc được, giữ bao lâu.
  - Bảng *mọi lối ra mạng*, khớp với test quét lối ra ở P3.
- [ ] **Quy trình phê duyệt:** sơ đồ trạng thái *nháp → cần xác nhận → duyệt từng mục (Giữ/Sửa/Bỏ) → ký WORM → mới được chép/xuất → sửa sau ký thì khóa lại và ký lại*. Mỗi bước kèm: ảnh chụp từ ca mẫu, test chứng minh (`kiemTraDieuKienKyDuyet`, `choPhepDungHoSo`, `worm.test.ts`), và lệnh kiểm chuỗi WORM.
- [ ] **Dữ liệu dùng khi phát triển:** toàn bộ là dữ liệu mô phỏng và bộ dữ liệu công khai (liệt kê, kèm giấy phép từ `docs/nguon-va-giay-phep.md`). Không có hồ sơ bệnh nhân thật nào được đưa vào công cụ AI lập trình. Chỉ ghi câu này nếu tác giả xác nhận đúng.

### P8. Tổng hợp nộp BTC

- [ ] Một tài liệu ngắn `docs/minh-bach/TRA_LOI_DE_CAI_TIEN_1.md` (2–3 trang): mỗi ý của đề → câu trả lời → đường dẫn minh chứng → test/lệnh kiểm. Có mục *"Chỗ hở đã tìm và đã sửa"* (H1–H8 kèm commit), vì tự tìm ra lỗi của chính mình là minh chứng mạnh nhất cho "đội tự đánh giá/sửa".
- [ ] Xuất bản Word/PDF. Không dùng phông Be Vietnam Pro.
- [ ] Toàn bộ `pytest -q`, `cd web; npm run lint; npm test; npm run build` xanh; 3 ca demo BGK không đổi.
- [ ] Push và triển khai chỉ khi người dùng đồng ý (triển khai theo quy trình HoaiĐức, không khởi động lại máy).

---

## 3. Cần tác giả xác nhận (máy không tự điền)

**Đã trả lời (28/11/2026):**
- Câu "Đội ngũ Nghiên cứu Lâm sàng": **bỏ**. Đã xóa khỏi 2 tài liệu khai và 3 công cụ sinh tài liệu.
- **Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào** (tác giả xác nhận). P7 được ghi câu này.
- Cổng mô hình ngoài AIBOX là **dịch vụ của bên thứ ba**. Hệ quả cho sơ đồ dữ liệu và câu trả lời BTC:
  - Ghi rõ "bên thứ ba, ngoài sự kiểm soát của đội; không có thỏa thuận xử lý dữ liệu".
  - Vì vậy đường này **mặc định tắt ở cả hai lớp** (P4 trở thành bắt buộc, không còn tùy chọn).
  - Chỉ gửi văn bản đã che; còn định danh thì từ chối.
  - Bản dành cho phòng khám nên tắt hẳn đường này (`MEDITRACE_TRO_LY_NGOAI=tat`).

**Còn chờ:**
1. Nhãn công cụ của 33 commit không có dòng ghi công cụ (P6).
2. Hạn nộp minh chứng (hackathon 6 tiếng, xem `docs/hackathon-6-tieng-de-cai-tien-1.md`).

## 4. Đường ngắn (nếu hạn gấp, khoảng 1 ngày)

P1 (khóa xuất trước ký) → P3 (PubMed + log + test lối ra) → P7 (sơ đồ + quy trình) → P5 (sổ quyết định, chỉ những mục có bằng chứng) → P8. Hoãn P2, P4, P6 và ghi chúng thành *"việc tiếp theo"* trong tài liệu nộp.
