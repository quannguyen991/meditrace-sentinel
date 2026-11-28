# Trả lời Đề cải tiến 1 — Làm chủ và bảo vệ dữ liệu sức khỏe

MediTrace Sentinel · 28/11/2026 · nhánh `main` (đã gộp từ `hackathon-de-1`)

> **Đề:** quá trình sử dụng AI để phát triển sản phẩm và phạm vi xử lý thông tin bệnh nhân cần minh bạch hơn. Trình bày quyết định thiết kế, những nội dung AI hỗ trợ và đội tự đánh giá/sửa; không đưa dữ liệu bệnh nhân nhận dạng được vào dịch vụ/log trái phép. Minh chứng: lịch sử sửa đổi, sơ đồ dữ liệu, quy trình bác sĩ phê duyệt trước khi dùng hồ sơ.

Hai điều tác giả xác nhận ngày 28/11/2026:
- **Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào.** Khi phát triển chỉ dùng dữ liệu mô phỏng và bộ dữ liệu công khai.
- **Cổng mô hình ngoài AIBOX là dịch vụ bên thứ ba.** Vì vậy nó là tính năng phụ, mặc định tắt, và chỉ nhận văn bản đã che.

Mọi ý dưới đây kèm tệp minh chứng và lệnh kiểm. Mọi test chạy được trên máy của giám khảo.

---

## 1. Quyết định thiết kế

**Chúng tôi làm gì.** Sổ quyết định ghi từng quyết định theo dạng: vấn đề → các phương án đã cân nhắc → chọn gì → vì sao → ai quyết → commit hoặc tệp làm bằng chứng. Mọi dòng có bằng chứng kiểm được bằng máy.

**Minh chứng:** [`so-quyet-dinh-thiet-ke.md`](so-quyet-dinh-thiet-ke.md).

**Kiểm:** `python -m pytest tests/test_minh_chung_trich_commit.py`. Test này đỏ nếu một dòng trích commit hay tệp không có thật.

## 2. Nội dung AI hỗ trợ, và đội tự đánh giá/sửa

**Chúng tôi làm gì.**
- Bảng ghi theo từng phần của dự án: AI làm gì, đội làm gì, dùng công cụ nào (Claude Code, Codex, Antigravity, ChatGPT).
- Danh sách các lần đội bác bỏ hoặc sửa đầu ra của AI, mỗi lần có commit. Ví dụ: commit `2fc4eba` sửa 3 lỗi trong mã do Antigravity viết. Chuẩn hóa phương ngữ đổi "mi" (mí mắt) thành "mày"; cảnh báo "sai liều" bắn nhầm khi câu có "ho 3 ngày"; chữ viết tắt "DIA" bị coi là chữ mất dấu.
- Nhật ký buổi hackathon: mỗi việc ghi một dòng, gồm AI làm gì và đội kiểm/sửa gì.

**Minh chứng:**
- [`ai-ho-tro-va-doi-tu-sua.md`](ai-ho-tro-va-doi-tu-sua.md)
- [`nhat-ky-hackathon.md`](nhat-ky-hackathon.md)
- README mục "Công cụ AI đã dùng"

## 3. Lịch sử sửa đổi

**Chúng tôi làm gì.**
- Mọi commit từ 28/11/2026 kết thúc bằng dòng `Cong-cu-AI: <claude_code|antigravity|codex|chatgpt|khong>`.
- Hook git **chặn** commit thiếu dòng này (`.githooks/commit-msg`; bật bằng `git config core.hooksPath .githooks`).
- Bảng truy nguồn sinh từ lịch sử git, xếp mỗi commit theo công cụ. Commit cũ không ghi công cụ được để `chua_xac_dinh`, không đoán.

**Minh chứng:** [`truy-nguon-commit.md`](truy-nguon-commit.md); `tools/truy_nguon_commit.py`; `tools/kiem_trailer_commit.py`.

**Kiểm:**
- `python -m pytest tests/test_truy_nguon_commit.py tests/test_kiem_trailer_commit.py`.
- Thử `git commit -m "x"`: bị chặn.

## 4. Không đưa dữ liệu nhận dạng vào dịch vụ trái phép

**Chúng tôi làm gì.**
- **Lõi chạy tại chỗ:** chép lời (PhoWhisper), trích mệnh đề (Qwen3-4B), kiểm căn cứ và ký duyệt không gửi gì ra ngoài.
- **Mọi lối ra mạng nằm trong một danh sách duy nhất.** Test đếm mọi lời gọi mạng trong mã máy chủ; thêm lối ra mới mà không khai báo thì test đỏ. Bên Python chỉ có một lối ra (máy xa của đội, mặc định không bật), cũng có test giữ.
- **Đường gửi nội dung ca khám ra bên thứ ba (AIBOX) mặc định TẮT.** Quản trị phải bật trong giao diện, rồi bác sĩ bật công tắc “Cho phép gửi ra mô hình ngoài” (trình duyệt nhớ lựa chọn này, không phải bật lại cho từng lần). Quản trị bấm tắt thì luôn tắt. Riêng lời gọi kiểm tình trạng cổng (`/models`) vẫn chạy khi có khóa, nhưng không mang nội dung ca khám.
- **Che định danh trước khi gửi, còn sót thì từ chối gửi.** Hai bộ che (TypeScript ở cổng ra mô hình ngoài, Python ở cổng ra máy xa) được vá thêm cho mã ca bệnh ("bệnh nhân 416", "BN416") và tên viết tắt ("bà H.T.P"). Một bộ ca rò rỉ dùng chung giữ cả hai bộ che.
- **Ô tìm tài liệu PubMed** từ chối từ khóa có tên, mã hay số liên lạc (kể cả tên địa danh viết hoa, nên đôi khi từ chối thừa). Trước đây từ khóa đi thẳng ra NCBI. Từ khóa do mô hình đặt cho tra cứu nhiều nguồn cũng được lọc: từ khóa nào còn dấu hiệu định danh thì bỏ trước khi gửi ra NCBI/MSD/NICE/Bộ Y tế (`locTuKhoaCoDanhTinh`).
- **Bản demo công khai:** màn đăng nhập ghi "chỉ nhập dữ liệu mô phỏng", vì bản demo đi qua Cloudflare.

**Số đo bộ che** trên PhoNER_COVID19, nhãn tên và mã bệnh nhân. Luật được vá trên tập dev; tập test chỉ đo hai lần, trước và sau khi vá:

| Bộ che | Trước khi vá (test) | Sau khi vá (test) | Che nhầm câu y khoa |
|---|---|---|---|
| TypeScript (cổng ra mô hình ngoài) | 7,5% | **94,0%** | 1,3% |
| Python (cổng ra máy xa) | 0,8% | **93,8%** | 0,7% |

Ngưỡng đăng ký trước là 95%. **Trên test chưa đạt** (trên dev đạt 97,5% và 97,3%). Chúng tôi không vá thêm theo tập test, vì như vậy là học tủ. Ngoài ra bước kiểm cuối vẫn từ chối gửi những câu còn dấu hiệu định danh. PhoNER là văn bản tin tức, không phải hội thoại khám.

**Minh chứng:**
- [`so-do-du-lieu.md`](so-do-du-lieu.md)
- `web/may-chu/loi-ra-mang.ts`
- [`../ket-qua/an-danh-phoner.md`](../ket-qua/an-danh-phoner.md)
- `tests/fixtures/ro_ri_dinh_danh.json`

**Kiểm:**
- `cd web; npx tsx --test may-chu/loi-ra-mang.test.ts may-chu/routes/tra-cuu.test.ts may-chu/an-danh-chung.test.ts`
- `python -m pytest tests/test_loi_ra_mang_python.py tests/test_ro_ri_dinh_danh_chung.py`

## 5. Không đưa dữ liệu nhận dạng vào log trái phép

**Chúng tôi làm gì.**
- Log lỗi của máy chủ web và dịch vụ Python đi qua bộ che: cắt ngắn, che tên và số; còn sót thì chỉ ghi độ dài. Chỗ này gồm cả lỗi do cổng bên thứ ba trả về, vì cổng có thể dội lại nội dung đã gửi.
- Đầu ra Python hỏng chỉ ghi độ dài và mã băm.
- `traceback.print_exc()` được thay bằng bản in tên lỗi và vị trí, không in giá trị.
- Nhật ký hoạt động (`nhat_ky`) vốn chỉ ghi siêu dữ liệu; trường tên thủ thuật (`procedureName`) khi đóng dấu cam đoan ở `web/may-chu/routes/boost-lam-sang.ts` cũng được đưa qua `cheLog` trước khi ghi.

**Minh chứng:** `web/may-chu/che-log.ts`, `src/he_thong/che_log.py`. Một test quét (`web/may-chu/log-da-che.test.ts`) đỏ nếu còn dòng `console.error/warn` in biến lỗi mà không qua `cheLog`. Bộ che chạy trước rồi mới cắt ngắn, để không chặt đôi một số điện thoại.

**Kiểm:**
- `cd web; npx tsx --test may-chu/che-log.test.ts may-chu/routes/llm-ngoai.test.ts` (gồm test "cổng ngoài trả lỗi có tên bệnh nhân → log không có tên").
- `python -m pytest tests/test_che_log.py`.

## 6. Sơ đồ dữ liệu

[`so-do-du-lieu.md`](so-do-du-lieu.md) gồm luồng dữ liệu, bảng mọi lối ra mạng và bảng mọi nơi lưu dữ liệu (lưu gì, có định danh không, ai đọc, giữ bao lâu). Tệp **sinh từ mã**; test đỏ khi sơ đồ lệch với mã.

## 7. Quy trình bác sĩ phê duyệt trước khi dùng hồ sơ

**Chúng tôi làm gì.** Trước ngày 28/11, chỉ nút *Ký* bị chặn khi còn mục chưa xác nhận. Các nút *Sao chép*, *In*, *Tải tệp*, *FHIR/BHYT*, *Chép HIS*, *SBAR*, *Tờ dặn dò* vẫn dùng được khi **chưa ký**. Đây là chỗ hở nặng nhất mà đội tự tìm ra khi rà mã. Nay tất cả, cùng các nút *BHYT / ICD-10 (tải gói XML1–XML5)*, *Đơn thuốc TT26*, *Cam đoan PTTT*, *Đi buồng / Trực*, chỉ mở khi đã ký và khóa lại khi sửa sau ký. Bốn nút sau do **rà soát độc lập** tìm ra; một test quét giờ đỏ ngay nếu xuất hiện lối xuất hồ sơ mới chưa khóa (`web/src/lib/loiRaHoSo.test.ts`). Khóa được áp **hai tầng**: giao diện (`web/src/lib/choPhepDungHoSo.ts`) **và máy chủ** (`web/may-chu/kiem-ky-may-chu.ts` lưu bản chụp `ban_ky_duyet` lúc ký và chặn `409 chua_ky_duyet` / `422` cho cả 6 đường xuất: `/api/benh-nhan-portal/tao-ma`, `/api/bhyt/precheck`, `/api/bhyt/recompile`, `/api/fhir/recompile`, `/api/clinical/informed-consent`, `/api/inpatient/ward-round-diff`). Bản in khi chưa ký mang dòng "BẢN NHÁP — CHƯA KÝ DUYỆT".

**Minh chứng:** [`quy-trinh-phe-duyet.md`](quy-trinh-phe-duyet.md), gồm sơ đồ trạng thái, 3 ảnh chụp trên giao diện thật, và lệnh kiểm sổ ký `GET /api/worm/verify`.

**Kiểm:** `cd web; npx tsx --test src/lib/quyTrinhPheDuyet.test.ts src/lib/choPhepDungHoSo.test.ts src/lib/loiRaHoSo.test.ts may-chu/kiem-ky-may-chu.test.ts may-chu/routes/bhyt-ocr.test.ts may-chu/routes/benh-nhan-portal.test.ts may-chu/routes/boost-lam-sang.test.ts`.

---

## Chỗ hở đội tự tìm và đã sửa trong đợt này

| # | Chỗ hở | Commit sửa |
|---|---|---|
| H1 | Chép/in/xuất hồ sơ được khi chưa ký | `f111b14` |
| H2 | Bộ che không nhận mã ca bệnh, tên viết tắt (che được 0,8–7,5% trên PhoNER) | `a4fb3d6` |
| H3 | Từ khóa PubMed đi thẳng ra NCBI, không kiểm định danh | `054c8b3` |
| H4 | Log lỗi có thể in nội dung ca khám | `054c8b3` |
| H5 | Đường ra bên thứ ba mặc định bật | `8b752da` |
| H6 | Lịch sử sửa đổi không ghi công cụ AI | `9f290d2` |
| R1 | (rà soát độc lập) BHYT/XML, đơn thuốc TT26, cam đoan, đi buồng vẫn xuất được khi chưa ký | xem mục "Sửa sau rà soát" trong `nhat-ky-hackathon.md` |
| R2 | (rà soát độc lập) Vài dòng log lỗi còn in thô; cắt chuỗi trước khi che | như trên |
| R3 | (rà soát độc lập) Bộ che Python bỏ sót họ tên viết thường; hai bộ che che nhầm "sốt từ thứ 2", "viêm gan B.", "nhóm máu A.", "Thái Lan" | như trên |
| R4 | (rà soát độc lập) Từ khóa tra cứu do mô hình đặt có thể mang tên thật ra nguồn tài liệu | như trên |
| R5 | (rà soát độc lập) Hook commit không chạy trên macOS/Linux | như trên |
| R6 | (gia cố vòng 2) Khóa máy chủ 6 đường xuất qua bản chụp `ban_ky_duyet` + che `procedureName` trong `nhat_ky` | `98bd5de`, `a555bdc`, `web/may-chu/routes/boost-lam-sang.ts` |
| R7 | (gia cố vòng 2) Tự xóa âm thanh quá hạn: 30 ngày đã duyệt, 7 ngày chưa duyệt; dọn khi `dich_vu_http.py` khởi tạo `AudioPipeline` | `22c61af`, `src/audio/storage.py`, `src/he_thong/dich_vu_http.py` |
| R8 | (gia cố vòng 2) Gỡ Google Fonts khỏi `web/index.html`, dùng font hệ thống tiếng Việt + test chặn tài nguyên ngoài | `web/index.html`, `web/src/lib/khongTaiNguonNgoai.test.ts` |
| R9 | (gia cố vòng 2) Xóa bản sao ca khám ở `localStorage` khi đăng xuất, hết phiên `401`, hoặc đổi người dùng | `22c61af`, `web/src/lib/xoaDuLieuTrinhDuyet.ts` |

## Còn hạn chế (chưa làm, nói thẳng)

- Bộ che đạt 94,0% / 93,8% trên tập test, chưa tới ngưỡng 95%. Phần lọt chủ yếu là tên một tiếng đứng trơ. Sau rà soát độc lập có vá thêm luật; chỉ đo lại trên tập dev (không đổi: 97,5% / 97,3%), **không** đo tập test lần ba.
- Trình duyệt của bác sĩ giữ bản sao danh sách ca khám trong `localStorage` để mở nhanh khi tải lại trang; dữ liệu này tự xóa khi đăng xuất, hết phiên `401` hoặc đổi tài khoản (`web/src/lib/xoaDuLieuTrinhDuyet.ts`), nhưng nếu bác sĩ đóng tab không đăng xuất thì bản sao cục bộ trên máy đó chưa mã hóa.
- 34 commit cũ chưa xác định công cụ (trong đó có các commit Antigravity 25–27/11). Tác giả sẽ xác nhận dần, máy không đoán.
- Chưa thử với bác sĩ thật xem họ có duyệt bừa không, và chưa chặn được thao tác bôi đen Ctrl+C hoặc Ctrl+P trên trình duyệt (bản in khi chưa ký tự mang dòng "BẢN NHÁP — CHƯA KÝ DUYỆT").

## Kết quả kiểm thử toàn bộ

Chạy ngày 28/11/2026 trên nhánh `main` (sau đợt gia cố vòng 2):

| Bộ kiểm | Trước đợt Đề 1 | Sau đợt gia cố vòng 2 |
|---|---|---|
| Python `pytest -q` | 1.960 qua, 27 bỏ qua | **2.106 qua**, 28 bỏ qua (1 ca đo trễ CPU đạt khi chạy riêng) |
| Web `npm test` | 96/96 | **214/214** |
| Kiểu `npm run lint` (tsc) | sạch | sạch |
| Đóng gói `npm run build` | xong | xong |
| 3 ca demo cho BGK | — | không đổi (test dùng ca mẫu xanh) |

Trong lần chạy trọn bộ `pytest` dưới tải cao, test đo độ trễ có sẵn từ trước (`test_tai_kiem_tra_nhanh_do_tre_va_tuong_thich_web_python`, ngưỡng 50 ms) ghi nhận `61,98 ms`; khi chạy lại riêng `tests/test_m1_safety_triage_scores.py` cùng nhóm minh bạch thì qua sạch (`93 passed, 1 skipped`).
