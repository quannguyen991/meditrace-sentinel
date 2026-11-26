# HỒ SƠ MINH CHỨNG NÂNG CẤP HỆ THỐNG & NHẬT KÝ THỰC THI LỆNH
## (ENGINEERING AUDIT TRAIL, COMMAND EXECUTION LOGS & UPGRADE EVIDENCE)

**Dự án:** MediTrace Sentinel — Hệ thống Hồ sơ Lâm sàng Có căn cứ & Phòng vệ An toàn Y khoa  
**Mã dự án:** `quannguyen991/meditrace-sentinel`  
**Nhánh Git:** `main` | **Thời điểm nghiệm thu cập nhật:** 17/10/2026 – 26/11/2026  
**Môi trường chạy thử (Cloudflare Workers, từ 26/11/2026):** [https://meditrace-sentinel.meditrace.workers.dev](https://meditrace-sentinel.meditrace.workers.dev)  
**Báo cáo cải tiến Chặng 1 (AI 2026):** [`BAO_CAO_CAI_TIEN_CHANG_1.md`](BAO_CAO_CAI_TIEN_CHANG_1.md)  
**Quy chuẩn lưu trữ:** Bản quyền mã nguồn cục bộ và GitHub Public Repository  

---

## 1. TỔNG QUAN MINH CHỨNG NÂNG CẤP TOÀN DIỆN

### 1.1. Thống kê biến động mã nguồn (Git Metrics — cập nhật 26/11/2026)
| Tiêu chí | Trước khi nâng cấp | Sau khi nâng cấp hoàn thiện | Mức tăng trưởng / Thay đổi |
| :--- | :---: | :---: | :---: |
| **Tổng số lượng bài test tự động** | 370 tests | **1.779 tests Pytest + 43 tests TypeScript** | **Tăng 4,9× — PASS 100%** |
| **Kho ngữ liệu hội thoại mô phỏng** | 200 khuôn (lặp câu 76,92%) | **657 khuôn / 21 hệ cơ quan (lặp câu 47,37%)** | **45.835 câu duy nhất (+127%), 0 rò rỉ tập** |
| **Lớp cảnh báo lỗi lâm sàng** | Chưa tách nhóm | **13 nhóm lớn, 56 mã lỗi (2 trục độc lập)** | **Độ nhạy cấy lỗi cơ bản 0,871 (giữ kín 240 ca)** |
| **Chốt chặn ký duyệt & Nhật ký WORM** | Chưa có | **Chặn cứng thiếu căn cứ + WORM SHA-256 `.anchor.json`** | **Không tự hoàn tất hồ sơ khi còn mục Cần xác nhận** |
| **Khóa an toàn dược lý (DDI & Liều trần)** | Chưa có | **3 chốt kiểm soát lâm sàng + Tiền kiểm BHYT** | Hỗ trợ rà soát tương tác & mã ICD-10 4 ký tự |
| **Thang điểm nguy cơ CDSS chuẩn hóa** | 0 thang điểm | **9 thang điểm quốc tế** | Tự động tính toán có căn cứ đối chiếu |
| **Cơ chế cách ly âm vị ASR (Bôi đỏ tên thuốc)** | Chưa có | **Bôi đỏ & Chuyển sang Cần xác nhận + Nghe lại** | Giảm thiểu nhầm lẫn âm vị tên thuốc, có mốc âm thanh |
| **Chuẩn hóa xuất EMR/HIS** | JSON nội bộ | **HL7 FHIR R4 + BHYT XML1–XML5 + SBAR** | Sẵn sàng cấu hình tích hợp bệnh viện |

---

## 2. NHẬT KÝ LỊCH SỬ GIT COMMITS (GIT AUDIT TRAIL)

### Commit 1: Nâng cấp Toàn diện Hạ tầng & Bộ Sơ đồ 7 Flow Master
* **Commit Hash:** `ce886d5`
* **Thời gian:** `Sat Oct 17 18:10:18 2026 +0700`
* **Tác giả:** `quannguyen991 <quannguyen991@users.noreply.github.com>`
* **Thông điệp:** `feat: bo anh 7 master flow diagrams, duong ong 1.330 automated tests, ASR phonetic drug quarantine va ha tang lam sang toan dien`
* **Quy mô thay đổi:** `101 files changed, 13794 insertions(+), 400 deletions(-)`
* **Chi tiết thành phần cốt lõi:**
  * Bổ sung module điều phối hạ tầng lâm sàng `src/dieu_phoi_ha_tang.py` và `src/guardrails.py`.
  * Bổ sung dược lý lâm sàng `src/duoc_ly_lam_sang.py` và hiệu chỉnh liều suy thận `src/hieu_chinh_lieu.py`.
  * Bổ sung cận lâm sàng `src/can_lam_sang.py` và 9 thang điểm nguy cơ `src/thang_diem_lam_sang.py`.
  * Bổ sung tờ dặn dò bệnh nhân 4 khung giờ `src/dan_do_benh_nhan.py`.
  * Bổ sung cơ chế khử định danh tuân thủ Nghị định 13/2023/NĐ-CP `src/khu_dinh_danh.py`.
  * Bổ sung xuất chuẩn HL7 FHIR R4 `src/fhir_exporter.py` và phân tách khuôn ca bệnh `src/kiem_khuon.py`.
  * Bổ sung 13 bộ test suite mới nâng tổng số bài test lên **1.330 automated tests**.
  * Bổ sung công cụ đồ họa sinh 7 sơ đồ Flow 4K `tools/tao_bo_anh_flow_meditrace.py`.
  * Bổ sung cẩm nang Q&A 35 câu hỏi giám khảo và các báo cáo kỹ thuật định dạng Word (`.docx`).

### Commit 2–6: Chuỗi Nâng cấp Chặng 1 AI 2026 & Kiểm toán Kiến trúc Toàn diện (Tháng 11/2026)
* **`3424284`:** Triển khai 8 tính năng lâm sàng, tiền kiểm BHYT/ICD-10 4 ký tự, đọc phiếu xét nghiệm cũ chỉnh liều thận, tách mô-đun `web/server.ts` sang `web/may-chu/routes/*` và hợp đồng kiểu 2 chiều `api_contract`.
* **`e9a1866` (`feat(python)`):** Kiểm toán tầng Python — sửa khử định danh `khu_dinh_danh.py`, tách chủ thể người nhà trong BHYT & FHIR R4, chuẩn hóa `Sintrom → acenocoumarol`, làm sạch `ContextualPrefixTrie600`, tối ưu `GET /api/suc-khoe` khởi động lạnh `< 1s`.
* **`d83d225` (`feat(may-chu)`):** Kiểm toán tầng BFF — gỡ bỏ hoàn toàn wildcard CSRF (`.vercel.app` / `.trycloudflare.com`), chỉ chấp nhận danh sách nguồn HTTPS tường minh `MEDITRACE_NGUON_DUOC_PHEP`; bổ sung nhật ký ký duyệt bất biến SQLite WORM kèm tệp neo `.anchor.json` chống cắt chuỗi/xoá trắng; khóa đồng bộ lạc quan `409 Conflict` cho `PUT /api/ca-kham/:id`; giữ nhãn `[DỊ ỨNG]` trong trợ lý ẩn danh.
* **`eef14d2` (`feat(giao-dien)`):** Kiểm toán giao diện React — thêm 3 lớp `ErrorBoundary`, phát lại âm thanh gốc theo lượt `useTurnAudioPlayer`, biên dịch văn bản hiệu lực `compileEffectiveNote` đồng bộ băm FIPS `SHA-256`, cô lập dữ liệu liên ca/liên người dùng.
* **`fbf987e` & `dad18a4` (`feat/perf(train)`):** Bổ sung huấn luyện DPO trên 1.200 cặp lỗi khó chia đều 14 loại từ adapter v3, gộp lô 2 chuỗi có tự kiểm sai số log-prob.
* **Cập nhật hoàn thiện Chặng 1 (26/11/2026):** Bổ sung chốt chặn cứng 2 tầng không cho hoàn tất/ký duyệt hồ sơ khi thiếu căn cứ hoặc còn mục `Cần xác nhận` chưa xử lý (`kiemTraDieuKienKyDuyet` + `worm.ts`), và tích hợp sẵn **3 ca mẫu đa người nói** chạy ngay không cần GPU (`src/ca_mau_bgk.py`).

---

## 3. NHẬT KÝ THỰC THI CÂU LỆNH KỸ THUẬT (ENGINEERING COMMAND AUDIT LOG)

Dưới đây là trích xuất lịch sử các câu lệnh thực tế được thực thi tuần tự qua các giai đoạn nâng cấp của dự án:

### 3.1. Giai đoạn 1 (05/10 – 06/10/2026): Kiểm thử Khóa bằng chứng K7, Cổng rủi ro & Sinh đồ họa thực nghiệm
```powershell
# 1. Chạy kiểm thử đơn vị cho Cổng rủi ro Tầng 5, Khâu hỏi lại và Bộ âm vị ASR nguy kịch
pytest tests/test_cong_rui_ro.py tests/test_hoi_lai.py tests/test_audio_clinical_tokens.py -v
# Kết quả: 114 passed in 1.45s

# 2. Chạy kiểm thử xác thực Cổng K7 (Khóa bằng chứng chống lỗi nhớ nhầm khi bệnh nhân tự sửa lời)
pytest tests/test_khoa_bang_chung.py -v
# Kết quả: 58 passed in 0.82s

# 3. Thực thi sinh các sơ đồ kiến trúc và bảng số liệu thực nghiệm đối chứng
python tools/ve_bang_doi_chung_thuc_nghiem.py
python tools/ve_so_do_flow_5_tang_meditrace.py
python tools/ve_so_do_so_sanh_nhanh.py
python tools/ve_so_do_tong_the_cac_tang.py
# [+] Đã xuất thành công các sơ đồ phân tích và bảng số liệu thực nghiệm.
```

### 3.2. Giai đoạn 2 (15/10 – 16/10/2026): Kiểm thử Module Dược lý, Đa bệnh lý, Bảo mật & Đo độ đa dạng dữ liệu
```powershell
# 1. Kiểm thử module Dược lý lâm sàng (DDI), Đa bệnh lý, Khử định danh NĐ13 và Từ điển phương ngữ
pytest tests/test_duoc_ly_lam_sang.py tests/test_da_benh_ly.py tests/test_khu_dinh_danh.py tests/test_phuong_ngu_lam_sang.py tests/test_can_lam_sang.py -v
# Kết quả: 346 passed in 4.12s

# 2. Kiểm thử công thức hiệu chỉnh liều theo chức năng gan thận và module sinh tờ dặn dò bình dân
pytest tests/test_hieu_chinh_lieu.py tests/test_dan_do_benh_nhan.py -v
# Kết quả: 201 passed in 2.35s

# 3. Chạy công cụ đo lặp câu và độ đa dạng từ vựng chuẩn hóa bằng toán học
python -m src.do_lap_cau data/hoi_thoai_viet_v2_mo_rong.jsonl
# Kết quả v2 (657 khuôn, 5.000 ca): 45.835 câu duy nhất (+127% so với v1), tỷ lệ lặp giảm xuống 47.37% (câu >= 8 từ: 42.19%), MTLD 145.4, Distinct-2 0.0468 [ĐÃ RÚT: con số 78.3% cũ không có phép đo tương ứng trong mã].
```

### 3.3. Giai đoạn 3 (17/10/2026): Tích hợp 5 chốt Guardrails, Chạy toàn bộ 1.330 bài test & Triển khai Production
```powershell
# 1. Chạy kiểm thử xác nhận module điều phối hạ tầng và 5 tầng Guardrails liên hoàn
pytest tests/test_dieu_phoi_ha_tang.py tests/test_guardrails.py -v
# Kết quả: tests/test_dieu_phoi_ha_tang.py (137 passed), tests/test_guardrails.py (145 passed) in 2.89s

# 2. Chạy toàn bộ đường ống kiểm thử hồi quy toàn diện hệ thống (Full Regression Suite)
pytest tests/
# ============================= test session starts =============================
# platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
# collected 1357 items
# ================= 1330 passed, 27 skipped in 120.35s (0:02:00) =================
# Tỷ lệ thành công: 100% không phát sinh lỗi logic

# 3. Sinh toàn bộ 7 Master Flow Diagrams độ phân giải cao 4K chuẩn y khoa
python tools/tao_bo_anh_flow_meditrace.py
# [+] Đã xuất và đồng bộ thành công bộ 7 sơ đồ Flow 4K UHD.

# 4. Thiết lập tài khoản quản trị hệ thống bằng hàm băm an toàn Scrypt (Sử dụng biến môi trường bảo mật)
$env:ADMIN_PASSWORD = "[REDACTED_SECURE_PASSPHRASE]"
node -e "
const crypto = require('crypto');
const { DatabaseSync } = require('node:sqlite');
const db = new DatabaseSync('web/data/meditrace.db');
const THAM_SO = { N: 16384, r: 8, p: 1 };
function scrypt(pwd, salt) {
  return new Promise((ok, fail) => crypto.scrypt(pwd, salt, 64, THAM_SO, (e, k) => e ? fail(e) : ok(k)));
}
(async () => {
  const salt = crypto.randomBytes(16);
  const hash = await scrypt(process.env.ADMIN_PASSWORD || 'Med!Tr@ce2026', salt);
  const hashStr = 'scrypt$16384$8$1$' + salt.toString('base64') + '$' + hash.toString('base64');
  db.prepare('INSERT OR REPLACE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (2, ?, ?, ?, ?, ?)')
    .run('admin_demo@meditrace.vn', 'BS. Hướng dẫn Lâm sàng', hashStr, 'quan_tri', Date.now());
  console.log('[OK] Cấu hình tài khoản quản trị demo an toàn thành công.');
})();
"

# 5. Triển khai ứng dụng lên môi trường Vercel Production
vercel --prod --yes
# Output:
# ✓ Linked siu6/meditrace-sentinel
# Production: https://meditrace-sentinel.vercel.app
# Deployment Status: ● Ready (Duration: 2s)

# 6. Đẩy mã nguồn nâng cấp lên nhánh chính GitHub
git add -A
git commit -m "feat: bo anh 7 master flow diagrams, duong ong 1.330 automated tests, ASR phonetic drug quarantine va ha tang lam sang toan dien"
git push origin main
```

### 3.4. Giai đoạn 4 (18/10/2026): Nạp Ca mẫu Lâm sàng cho BGK & Hoàn thiện Giao diện Doctor-in-the-Loop
```powershell
# 1. Khởi động dịch vụ hỗ trợ lâm sàng microservice cổng 8765
python src/dich_vu.py --port 8765
# [OK] Dịch vụ hỗ trợ lâm sàng đang lắng nghe tại http://127.0.0.1:8765

# 2. Nạp bộ 3 ca bệnh mẫu có độ khó cao (chứa các bẫy lâm sàng phức tạp) vào tài khoản chấm thi của Ban Giám khảo
node tools/them_3_ca_kho_bgk.js
# [OK] Đã nạp thành công 3 ca khám mẫu tiêu chuẩn vào cơ sở dữ liệu web/data/meditrace.db

# 3. Kiểm tra tính toàn vẹn và đóng gói giao diện Web đối soát (Click-to-Verify & Xuất PDF A4)
bun run build
# [vite] built in 420ms. Sẵn sàng vận hành giao diện Doctor-in-the-loop.
```

---

## 4. CHI TIẾT CÁC ĐOẠN CODE MINH CHỨNG (CORE CODE AUDIT EVIDENCE)

### 4.1. Minh chứng 1: Cơ chế Cách ly Âm vị Tên thuốc & Bôi đỏ (`src/dieu_phoi_ha_tang.py`)
Quy định lâm sàng bắt buộc: Khi tín hiệu thu âm có tạp âm hoặc bệnh nhân nói tên thuốc theo phiên âm dân gian, hệ thống tự động bôi đỏ và cách ly sang danh mục *"Cần bác sĩ xác nhận"* (Zero Silent Normalization).
```python
# Trích từ src/dieu_phoi_ha_tang.py:
def phan_tich_am_vi_thuoc(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Phát hiện các tên thuốc phiên âm dân gian trong lời thoại ASR và bôi đỏ cảnh báo."""
    cac_canh_bao = []
    text_chuan = text
    for dan_gian, chuan in TU_DIEN_THUOC_DAN_GIAN.items():
        pattern = re.compile(rf"\b{re.escape(dan_gian)}\b", re.IGNORECASE)
        if pattern.search(text_chuan):
            canh_bao = {
                "tu_goc": dan_gian,
                "goi_y_chuan": chuan,
                "trang_thai": "CAN_XAC_NHAN",
                "ly_do": "ASR nhận diện tên thuốc dân gian có độ bất định cao",
                "nhan_hien_thi": f"[BÔI ĐỎ - CẦN BÁC SĨ XÁC NHẬN TÊN THUỐC: '{dan_gian}' -> Gợi ý: '{chuan}']"
            }
            cac_canh_bao.append(canh_bao)
            # Đánh dấu trực tiếp thẻ bôi đỏ vào văn bản
            text_chuan = pattern.sub(f"**[BÔI ĐỎ: {dan_gian} (? {chuan})]**", text_chuan)
    return text_chuan, cac_canh_bao
```

### 4.2. Minh chứng 2: Máy trạng thái hữu hạn FSM Bắt đính chính nói nhầm (`src/khoa_bang_chung.py`)
Bắt trọn vẹn ngữ cảnh bệnh nhân nói nhầm rồi sửa lại ngay trong lượt thoại (Ví dụ: *"Uống 3 viên... à nhầm 1 viên thôi"*):
```python
# Trích từ src/khoa_bang_chung.py:
def xu_ly_dinh_chinh_noi_nham(luot_thoai: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """FSM phát hiện từ khóa đính chính (à nhầm, không phải, xin lỗi tôi nhớ nhầm) và gán cờ SUPERSEDED."""
    fsm_state = "NORMAL"
    menh_de_hop_le = []
    for md in luot_thoai:
        if any(tu_dinh_chinh in md["text"].lower() for tu_dinh_chinh in TU_KHOA_DINH_CHINH):
            # Mệnh đề trước đó bị vô hiệu hóa bởi đính chính
            if menh_de_hop_le:
                menh_de_hop_le[-1]["trang_thai_khoa"] = "SUPERSEDED_K7"
                menh_de_hop_le[-1]["ghi_chu"] = "Đã bị bệnh nhân đính chính nói nhầm ở lượt sau"
            md["trang_thai_khoa"] = "ACTIVE_CORRECTED"
        menh_de_hop_le.append(md)
    return menh_de_hop_le
```

### 4.3. Minh chứng 3: Khóa an toàn Dược lý Liều trần & Chống tương tác thuốc (`src/duoc_ly_lam_sang.py`)
Ngăn chặn các thảm họa kê đơn như vượt trần liều Paracetamol (> 4g/ngày) hoặc tương tác chết người (Metformin + Thuốc cản quang):
```python
# Trích từ src/duoc_ly_lam_sang.py:
def kiem_tra_an_toan_duoc_ly(don_thuoc: List[Dict[str, Any]], egfr: float = None) -> List[Dict[str, Any]]:
    canh_bao = []
    # 1. Kiểm tra liều trần Paracetamol
    tong_lieu_para = sum(t["lieu_mg"] for t in don_thuoc if "paracetamol" in t["ten"].lower())
    if tong_lieu_para > 4000:
        canh_bao.append({
            "muc_do": "NGUY_HIEM_DDI_3",
            "loi": f"Tổng liều Paracetamol đạt {tong_lieu_para}mg/24h, vượt trần 4000mg. Nguy cơ ngộ độc hoại tử tế bào gan cấp!",
            "hanh_dong": "CHẶN KÊ ĐƠN & BÔI ĐỎ YÊU CẦU ĐỔI LIỀU"
        })
    # 2. Kiểm tra hiệu chỉnh liều theo eGFR suy thận
    if egfr and egfr < 30:
        for t in don_thuoc:
            if t["ten"].lower() in THUOC_CHONG_CHI_DINH_THAN_NANG:
                canh_bao.append({
                    "muc_do": "CHONG_CHI_DINH_TUYET_DOI",
                    "loi": f"Thuốc {t['ten']} chống chỉ định khi eGFR < 30 mL/phút/1.73m2 (Hiện tại: {egfr})",
                    "hanh_dong": "NGỪNG THUỐC NGAY LẬP TỨC"
                })
    return canh_bao
```

### 4.4. Minh chứng 4: Khóa An ninh CSRF Tường minh Không Wildcard & Chốt chặn Ký duyệt WORM (`web/may-chu/tai-khoan.ts`, `web/may-chu/worm.ts`)
Đã gỡ bỏ toàn bộ mẫu khớp đuôi đại diện (`*.vercel.app`, `*.trycloudflare.com`) và chặn hạ cấp giao thức `http://` đối với tên miền ngoài; chỉ chấp nhận danh sách nguồn cấu hình tường minh qua `MEDITRACE_NGUON_DUOC_PHEP`, đồng thời chặn ký duyệt WORM nếu hồ sơ chưa có mệnh đề có căn cứ hoặc còn mục `Cần xác nhận` chưa được bác sĩ xử lý:
```typescript
// Trích từ web/may-chu/tai-khoan.ts & web/may-chu/worm.ts:
const nguonDuocPhep = new Set(
  (process.env.MEDITRACE_NGUON_DUOC_PHEP || "https://meditrace-sentinel.vercel.app")
    .split(",")
    .map((s) => chuanHoaOrigin(s))
    .filter((s): s is string => Boolean(s)),
);
// Trong worm.ts (kiemTraInputSignOff):
if (input.tongMenhDe < 1) {
  throw loiDauVao("Gia tri khong hop le cho tongMenhDe: 0 (khong duoc hoan tat/ky duyet ho so khi chua co menh de co can cu)");
}
if (input.soChuaXacNhan !== undefined && input.soChuaXacNhan !== 0) {
  throw loiDauVao("Gia tri khong hop le cho soChuaXacNhan: con muc can bac si xac nhan chua xu ly, khong duoc ky duyet");
}
```

---

## 5. DANH MỤC TỆP ĐỒNG BỘ TRÊN MÁY CỤC BỘ

Để phục vụ công tác đối chứng trước Hội đồng Giám khảo, các tệp báo cáo và minh chứng chính nằm tại:

1. **Gốc kho mã nguồn:** [`BAO_CAO_CAI_TIEN_CHANG_1.md`](BAO_CAO_CAI_TIEN_CHANG_1.md), [`README.md`](README.md), [`MINH_CHUNG_NANG_CAP_VA_LICH_SU_LENH.md`](MINH_CHUNG_NANG_CAP_VA_LICH_SU_LENH.md).
2. **Thư mục kết quả đo tự động:** [`docs/ket-qua/cay-loi.md`](docs/ket-qua/cay-loi.md), [`docs/ket-qua/bo-sot-qwen3-4b.md`](docs/ket-qua/bo-sot-qwen3-4b.md), [`docs/ket-qua/canh-bao-moc-0.md`](docs/ket-qua/canh-bao-moc-0.md), [`data/manifest_v2_mo_rong_5000.json`](data/manifest_v2_mo_rong_5000.json).

---

## 6. KẾT LUẬN & CAM KẾT KỸ THUẬT

1. **Tính trung thực & Khả năng tái lập (Reproducibility):** Mọi con số (1.779 bài test `pytest`, 43 bài test TypeScript, độ nhạy lớp cảnh báo 0,871 trên tập giữ kín, tỷ lệ bỏ sót 43,1% → 11,5%, thống kê lặp câu 47,37%) đều do mã nguồn trong kho in ra và tái lập được bằng lệnh thực thi.
2. **An toàn dữ liệu Y khoa:** Hệ thống vận hành theo kiến trúc Neuro-Symbolic chạy tại chỗ (On-premise/Edge), không tự hoàn tất hồ sơ khi thiếu căn cứ, tuân thủ Nghị định 13/2023/NĐ-CP và Luật Khám bệnh, chữa bệnh 2023.
3. **Tính sẵn sàng Production:** Ứng dụng chạy thử tại `https://meditrace-sentinel.meditrace.workers.dev` (có sẵn 3 ca mẫu đa người nói mở ngay không cần GPU).
