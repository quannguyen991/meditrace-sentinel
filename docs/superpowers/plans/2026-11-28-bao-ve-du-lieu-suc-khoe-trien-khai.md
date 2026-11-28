# Bảo vệ dữ liệu sức khỏe và minh bạch dùng AI (Đề cải tiến 1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Biến ba lời hứa của MediTrace — "dữ liệu nhận dạng không ra ngoài", "hồ sơ chỉ được dùng sau khi bác sĩ ký", "đội làm chủ phần AI viết" — thành mã có test giữ, số đo, và tài liệu tự sinh từ mã. Làm trong hackathon 6 tiếng.

**Architecture:** Ba lớp. (1) **Chặn**: khóa mọi lối đưa hồ sơ ra khỏi phần mềm trước khi ký; mọi lối ra mạng nằm trong một danh sách duy nhất có test quét; log đi qua bộ che. (2) **Đo**: một bộ ca rò rỉ dùng chung cho cả bộ che TypeScript (cổng ra mô hình ngoài) và Python (cổng ra máy xa), cộng phép đo trên PhoNER. (3) **Chứng minh**: sơ đồ dữ liệu sinh từ danh sách lối ra và nơi lưu; sổ quyết định có test kiểm từng commit được trích là có thật; lịch sử commit gắn công cụ AI bằng trailer bắt buộc.

**Tech Stack:** TypeScript (Node, Express, React, `tsx --test`, `node:test`), Python 3.11 (pytest), SQLite (`node:sqlite`), git hooks.

**Spec:** Đề cải tiến 1 của BTC (28/11/2026), chép nguyên văn ở `docs/superpowers/plans/2026-11-28-de-cai-tien-1-du-lieu-suc-khoe.md` đầu tệp. Bảng chỗ hở H1–H8 ở mục 1 của tệp đó là đầu vào của kế hoạch này. Lịch theo giờ: `docs/hackathon-6-tieng-de-cai-tien-1.md`.

Đề, nguyên văn ý:
- **Vấn đề:** quá trình sử dụng AI để phát triển sản phẩm và phạm vi xử lý thông tin bệnh nhân cần minh bạch hơn.
- **Yêu cầu:** trình bày quyết định thiết kế, những nội dung AI hỗ trợ và đội tự đánh giá/sửa; không đưa dữ liệu bệnh nhân nhận dạng được vào dịch vụ/log trái phép.
- **Minh chứng:** lịch sử sửa đổi, sơ đồ dữ liệu và quy trình bác sĩ phê duyệt trước khi dùng hồ sơ.

## Global Constraints

- Tác giả xác nhận ngày 28/11/2026, các câu này được ghi đúng nguyên văn vào tài liệu:
  - Cổng mô hình ngoài AIBOX là **dịch vụ bên thứ ba**.
  - **Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào.**
  - Không dùng cụm "Đội ngũ Nghiên cứu Lâm sàng".
- Mọi commit trong buổi hackathon kết thúc bằng trailer `Cong-cu-AI: <claude_code|antigravity|codex|chatgpt|khong>` (Task 8 bắt buộc từ lúc cài hook). Commit có Claude viết thì thêm cả `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Chỉ `git add` tệp của task. Có phiên khác đang sửa `BAO_CAO_CAI_TIEN_CHANG_1.md`, `docs/tai-lieu/Bao_Cao_Nghien_Cuu_Khoa_Hoc_MediTrace_Sentinel.md`, `docs/tai-lieu/Báo cáo dự án.md`, `tools/bo_sung_nckh_thang_10.py`, `tools/nang_cap_bao_cao_chuan.py`: **không đụng các tệp này**. Chạy `git status` trước khi sửa tệp dùng chung.
- Không push, không triển khai khi chưa có đồng ý của tác giả. Không khởi động lại máy HoaiĐức. Không in khóa bí mật.
- PhoNER: **vá luật trên `dev_syllable.json`, chỉ đo cuối trên `test_syllable.json`** (đo test lần đầu ở Task 2 là mốc 0, lần hai ở cuối Task 3, không lần nào khác).
- Đường cơ sở test: `pytest -q` → 1.960 passed, 27 skipped. `cd web; npm test` xanh. Ba ca demo BGK (`demo_bs_nguoi_nha_nhi`, `demo_hai_benh_nhan`, `demo_lao_khoa_con_gai`) không đổi.
- Giao diện: chữ tiếng Việt, cỡ chữ tối thiểu 13px, không dùng phông Be Vietnam Pro.
- Không viết câu nào vào tài liệu minh chứng mà không có commit, tệp hoặc lệnh kiểm kèm theo.

## Review Focus

1. **In bằng trình duyệt (Ctrl+P) khi chưa ký.** Không chặn được phím in của trình duyệt, nên bản in phải tự mang dòng "BẢN NHÁP — CHƯA KÝ DUYỆT". → test `nhan_in_khi_chua_ky` ở Task 1.
2. **Cổng ngoài trả lỗi có lặp lại nội dung đã gửi.** `llm-ngoai.ts` đang log thẳng `data?.error?.message`. Cổng bên thứ ba có thể dội lại lời thoại, nên log phải qua bộ che. → test `log_loi_cong_ngoai_da_che` ở Task 4.
3. **Ngoại lệ Python mang nội dung ca khám trong thông điệp** (ví dụ `ValueError(f"... {hoi_thoai}")`), rồi bị `traceback.print_exc()` in ra. → test `in_loi_an_toan_khong_in_ten` ở Task 4.
4. **Từ khóa tra cứu viết thường không dấu hoa**, ví dụ "nguyễn văn an đau ngực". → test `pubmed_tu_choi_ten_chu_thuong` ở Task 4.
5. **Người xem bản demo công khai nhập dữ liệu thật**, mà bản demo đi qua Cloudflare. → test `thong_bao_ban_demo_co_tren_man_dang_nhap` ở Task 5.

---

## Chuẩn bị (10 phút, trước Task 1)

- [ ] `git status`; ghi lại các tệp đang sửa dở của phiên khác (xem Global Constraints).
- [ ] `git switch -c hackathon-de-1`
- [ ] `pytest -q > tmp/goc-pytest.txt; cd web; npm test > ../tmp/goc-web.txt` → ghi số passed vào đầu `docs/minh-bach/nhat-ky-hackathon.md` cùng giờ bắt đầu.
- [ ] Mỗi task xong: thêm một dòng vào `docs/minh-bach/nhat-ky-hackathon.md`, gồm giờ, task, commit, công cụ AI đã dùng, và chỗ đội đã sửa hay bác bỏ đầu ra của AI. Tệp này là minh chứng sống của "đội tự đánh giá/sửa".

---

### Task 1: Khóa dùng hồ sơ trước khi bác sĩ ký (H1)

**Files:**
- Create: `web/src/lib/choPhepDungHoSo.ts`
- Test: `web/src/lib/choPhepDungHoSo.test.ts`
- Modify: `web/src/components/NoteEditorView.tsx` (`handleCopy` ~615, `handleDownloadTxt` ~622, `handleDownloadMd` ~634, `handleDownloadFhirBhytJson` ~646, nút SBAR ~1505, Chép HIS ~1516, Tờ dặn dò ~1529, hai chỗ `window.print()` ~1638 và ~1669)
- Modify: `web/src/index.css` (quy tắc `@media print`)

**Interfaces:**
- Consumes: `isSignOffStale(signOff, currentContentHash): boolean` trong `web/src/lib/compileEffectiveNote.ts`; biến `signOff`, `daSuaSauKy` có sẵn trong `NoteEditorView.tsx`.
- Produces:
  - `choPhepDungHoSo(t: { daKy: boolean; daSuaSauKy: boolean }): { duoc: boolean; lyDo: string | null }`
  - `nhanInHoSo(duoc: boolean): string | null`
  - hằng `LY_DO_CHUA_KY`, `LY_DO_SUA_SAU_KY`, `NHAN_BAN_NHAP`

- [ ] **Step 1: Viết test**

```ts
import assert from "node:assert/strict";
import test from "node:test";
import { choPhepDungHoSo, nhanInHoSo, LY_DO_CHUA_KY, LY_DO_SUA_SAU_KY, NHAN_BAN_NHAP } from "./choPhepDungHoSo";

test("chua_ky_thi_khoa", () => {
  assert.deepEqual(choPhepDungHoSo({ daKy: false, daSuaSauKy: false }), { duoc: false, lyDo: LY_DO_CHUA_KY });
});
test("da_ky_thi_mo", () => {
  assert.deepEqual(choPhepDungHoSo({ daKy: true, daSuaSauKy: false }), { duoc: true, lyDo: null });
});
test("sua_sau_ky_thi_khoa_lai", () => {
  assert.deepEqual(choPhepDungHoSo({ daKy: true, daSuaSauKy: true }), { duoc: false, lyDo: LY_DO_SUA_SAU_KY });
});
test("nhan_in_khi_chua_ky", () => {
  assert.equal(nhanInHoSo(false), NHAN_BAN_NHAP);
  assert.equal(nhanInHoSo(true), null);
});
```

Giá trị hằng (chép đúng):
- `LY_DO_CHUA_KY = "Bác sĩ chưa ký duyệt — hồ sơ chỉ được xem, chưa được chép, in hay xuất."`
- `LY_DO_SUA_SAU_KY = "Hồ sơ đã sửa sau lần ký — cần ký lại trước khi chép, in hay xuất."`
- `NHAN_BAN_NHAP = "BẢN NHÁP — CHƯA KÝ DUYỆT"`

- [ ] **Step 2: Chạy, phải FAIL**

Run: `cd web; npx tsx --test src/lib/choPhepDungHoSo.test.ts`
Expected: FAIL, không tìm thấy module `./choPhepDungHoSo`

- [ ] **Step 3: Cài đặt `choPhepDungHoSo` và `nhanInHoSo`** trong `web/src/lib/choPhepDungHoSo.ts`.

- [ ] **Step 4: Chạy, phải PASS** (cùng lệnh). Expected: 4 pass.

- [ ] **Step 5: Nối vào `NoteEditorView.tsx`**
  - Tính `const dungHoSo = useMemo(() => choPhepDungHoSo({ daKy: Boolean(signOff), daSuaSauKy }), [signOff, daSuaSauKy]);`
  - Bốn hàm `handleCopy`, `handleDownloadTxt`, `handleDownloadMd`, `handleDownloadFhirBhytJson` thoát ngay khi `!dungHoSo.duoc`.
  - Các nút SBAR, Chép HIS, Tờ dặn dò, In, và mục trong menu Xuất: `disabled={!dungHoSo.duoc}`, `title={dungHoSo.lyDo ?? <title cũ>}`.
  - Thêm một `div` chỉ hiện khi in (lớp `chi-hien-khi-in`) chứa `nhanInHoSo(dungHoSo.duoc)` ở đầu vùng nội dung bản nháp.
  - Trong `index.css`: `.chi-hien-khi-in{display:none}` và `@media print{.chi-hien-khi-in{display:block;font-size:16px;font-weight:700;border:2px solid #B91C1C;padding:6px}}`.
  - Xem trên màn hình vẫn được; chỉ khóa việc đưa hồ sơ ra khỏi phần mềm.

- [ ] **Step 6: Kiểm trong trình duyệt** (`preview_start` dev server, mở "Xem thử với ca mẫu"):
  - Chưa ký: 4 nút mờ, rê chuột hiện `LY_DO_CHUA_KY`.
  - Xử lý hết mục *Cần bác sĩ xác nhận* rồi ký: các nút mở.
  - Sửa một dòng: các nút khóa lại, hiện `LY_DO_SUA_SAU_KY`.
  - Lưu 3 ảnh chụp vào `docs/minh-bach/anh/khoa-truoc-ky-{1,2,3}.png`.

- [ ] **Step 7: Kiểm toàn bộ**

Run: `cd web; npm run lint; npm test`
Expected: 0 lỗi kiểu, toàn bộ test pass.

- [ ] **Step 8: Commit**

```bash
git add web/src/lib/choPhepDungHoSo.ts web/src/lib/choPhepDungHoSo.test.ts web/src/components/NoteEditorView.tsx web/src/index.css docs/minh-bach/anh/khoa-truoc-ky-*.png docs/minh-bach/nhat-ky-hackathon.md
git commit -m "feat(web): khoa chep/in/xuat ho so truoc khi bac si ky duyet" -m "Cong-cu-AI: <cong cu>"
```

---

### Task 2: Bộ ca rò rỉ dùng chung và mốc 0 của hai bộ che (H2, phần đo)

**Files:**
- Create: `tests/fixtures/ro_ri_dinh_danh.json`
- Create: `tests/test_ro_ri_dinh_danh_chung.py` (bộ che Python)
- Create: `web/may-chu/an-danh-chung.test.ts` (bộ che TypeScript)
- Create: `web/may-chu/do-an-danh-phoner.ts`, `tools/do_an_danh_phoner.py`
- Create: `docs/ket-qua/an-danh-phoner.md`, `docs/ket-qua/an-danh-phoner.json`

**Interfaces:**
- Consumes:
  - TypeScript: `anDanhChoNgoai(van): KetQuaAnDanh` trong `web/may-chu/an-danh-ngoai.ts`.
  - Python: `ClinicalDeidentifier.an_danh_van_ban(van, ten_benh_nhan=None)` và `ClinicalDeidentifier.kiem_tra_con_sot(van) -> list` trong `src/he_thong/khu_dinh_danh.py`.
- Produces:
  - Định dạng fixture: `[{"van": str, "cam": [str], "giu": [str]}]`.
    - `cam`: chuỗi không được còn sau khi che (trừ khi cả câu bị từ chối gửi).
    - `giu`: chuỗi lâm sàng phải còn nguyên.
  - Định nghĩa đo `bao_ve(nhãn) = nhãn không còn trong văn bản đã che HOẶC câu bị từ chối gửi`, dùng chung cho cả hai bộ đo.

- [ ] **Step 1: Viết fixture** với ít nhất 24 ca, gồm ba nhóm:
  - **Dạng đang lọt:** `"bệnh nhân 416"`, `"BN416"`, `"bệnh nhân số 91 đã xuất viện"`, `"bà H.T.P, 67 tuổi"`, `"ông N.V.A"`, `"anh Q. bị sốt"`.
  - **Dạng đã che được** (lấy 8 ca từ `RO_RI` trong `web/may-chu/an-danh-ngoai.test.ts`).
  - **Ca phải giữ nguyên:** `"đau ngực 3 ngày"`, `"uống paracetamol 500 mg ngày 2 lần"`, `"huyết áp 140/90"`, `"tiểu đường type 2 từ năm 2019"`, `"dị ứng penicillin"`, `"mẹ bệnh nhân bị hen"`, mỗi ca có `giu` bằng chính câu đó và `cam: []`.

- [ ] **Step 2: Viết hai test đọc cùng fixture**
  - Python `test_bo_che_python_theo_bo_ca_chung`, tham số hóa theo từng ca: hoặc `kiem_tra_con_sot(da_che)` khác rỗng (từ chối), hoặc mọi chuỗi `cam` vắng mặt; mọi chuỗi `giu` có mặt.
  - TypeScript `bo_che_cong_ra_theo_bo_ca_chung`: với từng ca, hoặc `kq.ok === false`, hoặc mọi `cam` vắng trong `kq.van`; mọi `giu` có trong `kq.van` khi `kq.ok`.

- [ ] **Step 3: Chạy, ghi lại các ca FAIL** (đây là danh sách việc của Task 3, không sửa ở đây)

Run: `pytest tests/test_ro_ri_dinh_danh_chung.py -q; cd web; npx tsx --test may-chu/an-danh-chung.test.ts`
Expected: một số ca nhóm "đang lọt" FAIL, nhóm "phải giữ" PASS. Đánh dấu tạm các ca FAIL bằng `pytest.mark.xfail(strict=True)` / `test.todo` để bộ test chính vẫn xanh. Task 3 gỡ các dấu này.

- [ ] **Step 4: Viết hai bộ đo PhoNER** (cùng định nghĩa)
  - Đầu vào: `data/ngoai/PhoNER_COVID19/data/syllable/{dev|test}_syllable.json`, mỗi dòng một JSON `{"words": [...], "tags": [...]}`, lấy nhãn `NAME` và `PATIENT_ID` (gộp B-/I-).
  - Che nhầm: 300 câu hỏi đầu của `data/ngoai/ViMedAQA/test_sample_500.json`. Một câu tính là "che nhầm" khi văn bản sau che khác văn bản gốc **hoặc** câu bị từ chối.
  - Tham số `--tap dev|test`, `--toi-da 1000`. In và ghi JSON: `{tap, so_nhan, bao_ve, ty_le_bao_ve, so_cau_tu_choi, che_nham, ty_le_che_nham}`.
  - Chạy TypeScript bằng `cd web; npx tsx may-chu/do-an-danh-phoner.ts --tap test`, Python bằng `python -m tools.do_an_danh_phoner --tap test`.

- [ ] **Step 5: Đo mốc 0 trên `test`** (lần đo test thứ nhất trong hai lần được phép). Ghi vào `docs/ket-qua/an-danh-phoner.md` bảng *Bộ che | Tập | Bảo vệ NAME+PATIENT_ID | Từ chối | Che nhầm ViMedAQA*, có cột "mốc 0, trước khi vá". Nhắc lại số cũ 10/847 (1,2%) của `docs/ket-qua/da-nguon-doc-lap.json` cho bộ Python để đối chiếu, và ghi chú vì sao hai cách đo khác nhau (bản cũ không tính câu bị từ chối).

- [ ] **Step 6: Chạy toàn bộ test**

Run: `pytest -q; cd web; npm test`
Expected: xanh (các ca đang lọt mang dấu xfail/todo).

- [ ] **Step 7: Commit** (fixture, 2 test, 2 bộ đo, kết quả mốc 0) — `test: bo ca ro ri dinh danh dung chung va moc 0 tren PhoNER`

---

### Task 3: Vá hai bộ che cho tới ngưỡng (H2, phần sửa)

**Files:**
- Modify: `web/may-chu/an-danh-ngoai.ts` (mảng `LUAT`)
- Modify: `src/he_thong/khu_dinh_danh.py` (`ClinicalDeidentifier.an_danh_van_ban`, `kiem_tra_con_sot`)
- Modify: `tests/test_ro_ri_dinh_danh_chung.py`, `web/may-chu/an-danh-chung.test.ts` (gỡ dấu xfail/todo)
- Modify: `docs/ket-qua/an-danh-phoner.md`, `.json`

**Interfaces:**
- Consumes: fixture và hai bộ đo của Task 2.
- Produces: hai luật mới tên giống nhau ở cả hai bộ che:
  - `MA_CA_BENH`: "bệnh nhân" / "BN" / "ca bệnh", có thể có "số", rồi 1–6 chữ số, kể cả viết liền `BN416`.
  - `TEN_VIET_TAT`: xưng hô (ông, bà, anh, chị, cô, chú, bác, cháu, em, bé, cụ) + 1–4 chữ hoa có dấu chấm, ví dụ "H.T.P", "N.V.A", "Q.".

- [ ] **Step 1: Thêm hai luật vào bộ che TypeScript.** Đặt `MA_CA_BENH` trước luật "chuỗi 8 chữ số"; đặt `TEN_VIET_TAT` trước luật "xưng hô + tên viết hoa". Giữ ranh giới từ bằng `KHONG_CHU_TRUOC`/`KHONG_CHU_SAU`; không dùng `\b`.
- [ ] **Step 2: Gỡ dấu `test.todo` của các ca tương ứng. Chạy** `cd web; npx tsx --test may-chu/an-danh-chung.test.ts may-chu/an-danh-ngoai.test.ts`. Expected: PASS (bộ ca cũ `RO_RI` vẫn xanh).
- [ ] **Step 3: Thêm hai luật vào bộ che Python**, che bằng token cùng kiểu bộ đang dùng. `kiem_tra_con_sot` phải nhận ra hai dạng này nếu còn sót.
- [ ] **Step 4: Gỡ dấu `xfail`. Chạy** `pytest tests/test_ro_ri_dinh_danh_chung.py tests -q -k "dinh_danh or khu_dinh"`. Expected: PASS.
- [ ] **Step 5: Lặp vá trên `--tap dev`** cho tới khi **cả hai** bộ che đạt `ty_le_bao_ve ≥ 0,95` và `ty_le_che_nham ≤ 0,05`.
  - **Luật dừng:** sau 45 phút mà chưa đạt thì dừng, giữ bản tốt nhất.
  - Mỗi lần vá phải thêm ít nhất một ca vào fixture.
- [ ] **Step 6: Đo lần hai (cuối cùng) trên `--tap test`**, ghi cột "sau khi vá", kèm câu: "PhoNER là văn bản tin tức về COVID-19, không phải hội thoại khám; ngưỡng đặt trên tập dev, số test đo đúng hai lần (trước và sau)". Không đạt ngưỡng thì ghi đúng số và lý do.
- [ ] **Step 7: Chạy toàn bộ test** `pytest -q; cd web; npm test`, rồi kiểm 3 ca demo BGK không đổi bằng `pytest -q tests/test_dich_vu.py tests/test_a1_a2_a3.py tests/test_nguoi_khac_khong_vao_tien_su_gia_dinh.py` (các test đang dùng ca mẫu BGK). Expected: xanh.
- [ ] **Step 8: Commit** — `fix: bo che dinh danh nhan ma ca benh va ten viet tat (TS + Python), do lai PhoNER`

---

### Task 4: Chặn lối ra ở tra cứu và log; danh sách lối ra duy nhất có test quét (H3, H4)

**Files:**
- Create: `web/may-chu/che-log.ts`, `web/may-chu/che-log.test.ts`
- Create: `web/may-chu/loi-ra-mang.ts`, `web/may-chu/loi-ra-mang.test.ts`
- Create: `src/he_thong/che_log.py`, `tests/test_che_log.py`, `tests/test_loi_ra_mang_python.py`
- Modify:
  - `web/may-chu/routes/dung-chung.ts` (dòng ~75, ~175, ~181)
  - `web/may-chu/routes/asr.ts` (~175)
  - `web/may-chu/routes/llm-ngoai.ts` (~154, ~159, ~197)
  - `web/may-chu/routes/tra-cuu.ts` (route `/api/pubmed-search`)
  - `src/he_thong/dich_vu_http.py` (6 chỗ `traceback.print_exc()` ở ~306, ~378, ~927, ~963, ~991, ~1062)
- Test: `web/may-chu/routes/tra-cuu.test.ts` (tạo nếu chưa có)

**Interfaces:**
- Consumes: `anDanhChoNgoai` (TypeScript), `ClinicalDeidentifier` (Python), đã vá ở Task 3.
- Produces:
  - `cheLog(giaTri: unknown, toiDa?: number): string`, với `toiDa` mặc định 300:
    - Chuỗi hóa giá trị, cắt còn `toiDa` ký tự, rồi che.
    - Nếu bộ che từ chối thì trả `"[đã ẩn <n> ký tự: còn định danh]"`.
  - `LOI_RA_DUOC_PHEP: ReadonlyArray<{ tep: string; dich: string; mucDich: string; duLieu: string; macDinh: "bat" | "tat" }>`. Task 6 sinh sơ đồ từ danh sách này.
  - Python:
    - `che_log(gia_tri, toi_da=300) -> str`, cùng hành vi với `cheLog`.
    - `in_loi_an_toan(exc: BaseException) -> None`: in tên lớp ngoại lệ, các khung `tệp:dòng`, và `che_log(str(exc))`. Không in giá trị biến cục bộ.

- [ ] **Step 1: Viết test `che-log.test.ts`**
  - `cheLog("Bệnh nhân Nguyễn Văn An, sđt 0912345678, đau ngực")` không chứa `"Nguyễn Văn An"`, không chứa `"0912345678"`, vẫn chứa `"đau ngực"`.
  - `cheLog("x".repeat(5000)).length <= 300`.
  - `cheLog({ a: 1 })` trả chuỗi chứa `"a"`.
- [ ] **Step 2: Viết test log cổng ngoài `log_loi_cong_ngoai_da_che`** trong `web/may-chu/routes/llm-ngoai.test.ts`.
  - Cho cổng giả trả mã 400 kèm `{"error":{"message":"bad input: Bệnh nhân Nguyễn Văn An"}}`.
  - Thay `console.error` bằng hàm thu chuỗi (`t.mock.method(console, "error", ...)`).
  - Assert không chuỗi log nào chứa `"Nguyễn Văn An"`.
- [ ] **Step 3: Viết test PubMed** trong `routes/tra-cuu.test.ts` (dựng app như `llm-ngoai.test.ts`; giả lập `fetch` bằng `t.mock.method(globalThis, "fetch", ...)` trả `{esearchresult:{idlist:[]}}`).
  - `pubmed_tu_choi_ten`: `GET /api/pubmed-search?q=Nguyễn Văn An đau ngực` → 422, `code === "tu_khoa_co_danh_tinh"`, `fetch` **không** được gọi.
  - `pubmed_tu_choi_ten_chu_thuong`: `q=nguyễn văn an đau ngực` → 422.
  - `pubmed_cho_qua_tu_khoa_y_khoa`: `q=chest pain troponin` → 200.
- [ ] **Step 4: Viết test quét lối ra `loi-ra-mang.test.ts`**
  - Đọc đệ quy mọi `.ts` trong `web/may-chu` (bỏ `*.test.ts`) cùng `web/server.ts`.
  - Đếm số lần xuất hiện `fetch(` theo từng tệp.
  - Assert bằng đúng số mục của tệp đó trong `LOI_RA_DUOC_PHEP`.
  - Hiện có 6 lời gọi: `routes/dung-chung.ts` 1 (dịch vụ Python nội bộ), `routes/llm-ngoai.ts` 2 (AIBOX bên thứ ba: chat và models), `tra-cuu/nguon-ngoai.ts` 3 (PubMed/NCBI, trang tài liệu, AAFP).
  - Test thêm `muc_nao_cung_co_mo_ta`: mọi mục có `mucDich`, `duLieu` khác rỗng.
- [ ] **Step 5: Viết test Python**
  - `tests/test_che_log.py`:
    - `test_in_loi_an_toan_khong_in_ten`: ném `ValueError("lỗi ở hội thoại: Bệnh nhân Nguyễn Văn An 0912345678")`, gọi `in_loi_an_toan`, dùng `capsys` bắt stderr. Assert không có `"Nguyễn Văn An"`, không có `"0912345678"`, có `"ValueError"`.
    - `test_che_log_cat_ngan`: chuỗi 5.000 ký tự cho ra kết quả ≤ 300 ký tự.
  - `tests/test_loi_ra_mang_python.py`: quét `src/**/*.py` tìm `urlopen(`, `requests.`, `httpx.`, `http.client`. Chỉ được có `src/he_thong/dich_vu_http.py` với đúng 1 `urlopen` (máy xa của đội, mặc định tắt, bật bằng `--mo-hinh-xa`).
- [ ] **Step 6: Chạy, phải FAIL**

Run: `cd web; npx tsx --test may-chu/che-log.test.ts may-chu/loi-ra-mang.test.ts may-chu/routes/tra-cuu.test.ts may-chu/routes/llm-ngoai.test.ts; cd ..; pytest tests/test_che_log.py tests/test_loi_ra_mang_python.py -q`
Expected: FAIL (thiếu module, PubMed trả 200, log còn tên).

- [ ] **Step 7: Cài đặt**
  - Viết `cheLog`, `LOI_RA_DUOC_PHEP`, `che_log`, `in_loi_an_toan`.
  - `/api/pubmed-search`: nếu `anDanhChoNgoai(q)` trả `ok:false` **hoặc** `van !== q` thì trả 422, kèm `{ error: "Ô tìm tài liệu không nhận tên, mã hay số liên lạc của bệnh nhân. Hãy chỉ gõ từ khóa y khoa.", code: "tu_khoa_co_danh_tinh" }`.
  - Mọi `console.error(..., err?.stack || err?.message || err)` trong các tệp ở mục Files đổi sang `cheLog(...)`. Riêng đầu ra Python khi JSON hỏng chỉ log `do_dai=<n> bam=<12 ký tự sha256>`.
  - Sáu chỗ `traceback.print_exc()` đổi thành `in_loi_an_toan(exc)` (bắt `except Exception as exc`).
- [ ] **Step 8: Chạy lại cùng lệnh.** Expected: PASS.
- [ ] **Step 9: Toàn bộ** `pytest -q; cd web; npm run lint; npm test`. Expected: xanh.
- [ ] **Step 10: Commit** — `fix: che log, chan tu khoa PubMed co danh tinh, danh sach loi ra mang co test quet`

---

### Task 5: Hai lớp chọn tham gia cho đường ra bên thứ ba, và cảnh báo bản demo (H5)

**Files:**
- Modify: `web/may-chu/tro-ly/cai-dat-tro-ly.ts` (`ngoaiBat`)
- Modify: `web/may-chu/tro-ly/cai-dat-tro-ly.test.ts`
- Create: `web/src/lib/thongBaoBanDemo.ts`, `web/src/lib/thongBaoBanDemo.test.ts`
- Modify: `web/src/components/ManDangNhap.tsx`, `README.md` (bảng biến môi trường)

**Interfaces:**
- Produces:
  - `ngoaiBat(db, env): boolean` theo luật mới:
    - `env.MEDITRACE_TRO_LY_NGOAI === "tat"` thì `false`.
    - `=== "bat"` thì `true`.
    - Còn lại thì `docKhoa(db,"tro_ly_ngoai") === "bat"`.
  - `THONG_BAO_BAN_DEMO: string`.

- [ ] **Step 1: Test trong `cai-dat-tro-ly.test.ts`** (thay khẳng định mặc định cũ):
  - `ngoaiBat(moi(), {}) === false`.
  - Sau `ghiNgoaiBat(db, true)` thì `ngoaiBat(db, {}) === true`.
  - `ngoaiBat(db, { MEDITRACE_TRO_LY_NGOAI: "tat" }) === false`, kể cả khi CSDL ghi bật.
  - `ngoaiBat(moi(), { MEDITRACE_TRO_LY_NGOAI: "bat" }) === true`.
- [ ] **Step 2: Test `thong_bao_ban_demo_co_tren_man_dang_nhap`** trong `thongBaoBanDemo.test.ts`:
  - `THONG_BAO_BAN_DEMO` chứa `"dữ liệu mô phỏng"`.
  - Đọc tệp `web/src/components/ManDangNhap.tsx` và assert có import `THONG_BAO_BAN_DEMO`.
  - Giá trị: `"Bản chạy thử công khai: chỉ nhập dữ liệu mô phỏng. Không nhập tên, mã hồ sơ hay thông tin của người bệnh thật."`
- [ ] **Step 3: Chạy, phải FAIL**: `cd web; npx tsx may-chu/tro-ly/cai-dat-tro-ly.test.ts; npx tsx --test src/lib/thongBaoBanDemo.test.ts`
- [ ] **Step 4: Cài đặt**
  - Đổi `ngoaiBat`; tạo hằng; hiện thông báo dưới nút đăng nhập, cỡ chữ ≥ 13px.
  - README ghi: "Đường ra mô hình ngoài (AIBOX, dịch vụ bên thứ ba) mặc định TẮT; quản trị bật trong giao diện, bác sĩ bật cho từng lần gửi."
  - Kiểm `llm-ngoai.test.ts` vẫn xanh (đang đặt env `bat`).
- [ ] **Step 5: Chạy lại, PASS; toàn bộ** `cd web; npm run lint; npm test`.
- [ ] **Step 6: Commit** — `fix: duong ra mo hinh ben thu ba mac dinh tat ca hai lop; canh bao ban demo`

---

### Task 6: Sơ đồ dữ liệu sinh từ mã (minh chứng 2)

**Files:**
- Create: `web/may-chu/noi-luu-du-lieu.ts`
- Create: `web/may-chu/sinh-so-do-du-lieu.ts` (vừa là hàm vừa chạy được bằng `npx tsx`)
- Create: `web/may-chu/sinh-so-do-du-lieu.test.ts`
- Create (sinh ra): `docs/minh-bach/so-do-du-lieu.md`

**Interfaces:**
- Consumes: `LOI_RA_DUOC_PHEP` (Task 4).
- Produces:
  - `NOI_LUU_DU_LIEU: ReadonlyArray<{ noi: string; tep: string; noiDung: string; coDinhDanh: "co" | "khong" | "da_che"; aiDoc: string; giu: string }>`.
  - `sinhSoDoDuLieu(): string`, trả toàn văn Markdown.

- [ ] **Step 1: Test**
  - `so_do_khop_tep`: `sinhSoDoDuLieu()` bằng đúng nội dung `docs/minh-bach/so-do-du-lieu.md` (bỏ khác biệt `\r\n`). Sửa danh sách mà quên sinh lại thì test đỏ.
  - `so_do_du_loi_ra`: Markdown chứa `dich` của mọi mục trong `LOI_RA_DUOC_PHEP`.
  - `so_do_ghi_ben_thu_ba`: chứa `"AIBOX"` và `"bên thứ ba"`.
- [ ] **Step 2: Chạy, FAIL.** `cd web; npx tsx --test may-chu/sinh-so-do-du-lieu.test.ts`
- [ ] **Step 3: Điền `NOI_LUU_DU_LIEU`**, mỗi mục ghi đúng nội dung đọc từ mã:
  - `ca_kham` (`web/may-chu/csdl.ts`: lời thoại, bản nháp, **tên bệnh nhân**, có định danh, tại chỗ).
  - `ban_sao`.
  - `muc_kho`.
  - `nhat_ky` (chỉ siêu dữ liệu, không định danh).
  - `worm_signoff` (băm và số đếm, không nội dung).
  - `phien_asr`.
  - Thư mục phiên âm thanh của `src/audio/storage.py` (**giọng nói**, có định danh, chưa có hạn xóa; ghi trung thực "chưa có hạn giữ, xem Task 11").
  - `data/audit_log_worm.db` của Python.
  - Log tiến trình (đã che từ Task 4).
- [ ] **Step 4: Cài đặt `sinhSoDoDuLieu()`**, trả về:
  1. Sơ đồ Mermaid `flowchart LR` gồm:
     - Micro, rồi Trình duyệt.
     - Máy chủ web (HoaiĐức).
     - Dịch vụ Python tại chỗ (ASR PhoWhisper, Qwen3-4B, luật K1–K7).
     - SQLite tại chỗ.
     - Mỗi mục `LOI_RA_DUOC_PHEP` là một mũi tên ra ngoài, ghi nhãn `duLieu` và `macDinh`.
     - Nhánh Cloudflare Worker và đường hầm: "chỉ chuyển tiếp; Cloudflare thấy lưu lượng đã giải mã TLS; bản demo chỉ dùng dữ liệu mô phỏng".
  2. Bảng *Lối ra mạng*.
  3. Bảng *Nơi lưu dữ liệu*.
  4. Mục *Dữ liệu dùng khi phát triển*: "Chỉ dữ liệu mô phỏng và bộ dữ liệu công khai (xem `docs/nguon-va-giay-phep.md`). Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào (tác giả xác nhận 28/11/2026)."
  5. Dòng cuối: "Tệp này sinh từ `web/may-chu/sinh-so-do-du-lieu.ts`; sửa danh sách rồi chạy lại, không sửa tay."
- [ ] **Step 5: Sinh tệp** `cd web; npx tsx may-chu/sinh-so-do-du-lieu.ts > ../docs/minh-bach/so-do-du-lieu.md`, chạy test, PASS.
- [ ] **Step 6: Commit** — `docs: so do du lieu sinh tu danh sach loi ra va noi luu (co test khop)`

---

### Task 7: Quy trình bác sĩ phê duyệt, chứng minh bằng một test xuyên suốt (minh chứng 3)

**Files:**
- Create: `web/src/lib/quyTrinhPheDuyet.test.ts`
- Create: `docs/minh-bach/quy-trinh-phe-duyet.md`

**Interfaces:**
- Consumes:
  - `kiemTraDieuKienKyDuyet(propositions, quyetDuyet, banSuaDuyet)`, `isSignOffStale(signOff, hash)`, `computeNoteSignOffHashSync(...)` và `sha256HexSync(input: string): string` trong `web/src/lib/compileEffectiveNote.ts`.
  - `choPhepDungHoSo` (Task 1).

- [ ] **Step 1: Viết test `quy_trinh_phe_duyet_tu_dau_den_cuoi`**: 3 mệnh đề, trong đó mệnh đề 2 ở trạng thái cần xác nhận (dạng `canXacNhan` đọc được, xem cách test hiện có trong `web/src/lib/kyDuyet.test.ts`). Kiểm lần lượt:
  1. Chưa quyết định gì: `kiemTraDieuKienKyDuyet(...).duDieuKien === false`, `maLoi === "con_muc_can_xac_nhan"`, và `choPhepDungHoSo({daKy:false,daSuaSauKy:false}).duoc === false`.
  2. Quyết định `{2:"sua"}` với bản sửa rỗng: vẫn `false`.
  3. `{2:"giu"}`: `duDieuKien === true`.
  4. Giả lập ký (`signOff = { contentHash: h }` với `h = sha256HexSync(noiDung)`): `isSignOffStale(signOff, h) === false` và `choPhepDungHoSo({daKy:true,daSuaSauKy:false}).duoc === true`.
  5. Nội dung đổi (băm mới `h2`): `isSignOffStale(signOff, h2) === true` và `choPhepDungHoSo({daKy:true,daSuaSauKy:true}).duoc === false`.
- [ ] **Step 2: Chạy** `cd web; npx tsx --test src/lib/quyTrinhPheDuyet.test.ts`, PASS (dùng hàm có sẵn và Task 1). Nếu FAIL là có lỗi thật trong luồng ký: dùng superpowers:systematic-debugging, không sửa test cho xanh.
- [ ] **Step 3: Viết `quy-trinh-phe-duyet.md`**:
  - Sơ đồ trạng thái Mermaid: *Bản nháp → Cần xác nhận → Duyệt từng mục (Giữ/Sửa/Bỏ) → Ký (sổ WORM, băm SHA-256 + HMAC) → Được chép/in/xuất → Sửa sau ký → Khóa lại, ký lại*.
  - Mỗi bước kèm ảnh chụp ở Task 1 và test chứng minh: `quyTrinhPheDuyet.test.ts`, `choPhepDungHoSo.test.ts`, `web/may-chu/worm.test.ts`, `kyDuyet.test.ts`.
  - Ghi lệnh kiểm chuỗi WORM có sẵn của dự án (tìm trong `web/may-chu/worm.ts` hàm xác minh chuỗi và route tương ứng).
  - Ghi rõ giới hạn: không chặn được việc bôi đen rồi Ctrl+C; bản in khi chưa ký mang nhãn `NHAN_BAN_NHAP`.
- [ ] **Step 4: Commit** — `test+docs: quy trinh bac si phe duyet truoc khi dung ho so`

---

### Task 8: Lịch sử sửa đổi truy nguồn được công cụ AI (minh chứng 1a, H6)

**Files:**
- Create: `tools/truy_nguon_commit.py`, `tests/test_truy_nguon_commit.py`
- Create: `docs/minh-bach/truy-nguon-ghi-de.json` (rỗng `{}` lúc đầu)
- Create (sinh ra): `docs/minh-bach/truy-nguon-commit.md`
- Create: `.githooks/commit-msg`, `tools/kiem_trailer_commit.py`, `tests/test_kiem_trailer_commit.py`

**Interfaces:**
- Produces:
  - `phan_loai_commit(thong_diep: str, ghi_de: dict[str, str], ma: str) -> str`, trả theo thứ tự ưu tiên:
    1. `ghi_de[ma]` nếu có.
    2. Giá trị trailer `Cong-cu-AI:`.
    3. `"claude_code"` nếu có `Co-Authored-By: Claude`.
    4. Nếu không thì `"chua_xac_dinh"`.
  - `trailer_hop_le(thong_diep: str) -> bool`: `True` khi có dòng `Cong-cu-AI:` với giá trị thuộc `{"claude_code","antigravity","codex","chatgpt","khong"}`. Bỏ qua commit merge (dòng đầu bắt đầu bằng `Merge `).

- [ ] **Step 1: Test**
  - `phan_loai_commit("fix: x\n\nCong-cu-AI: antigravity", {}, "a1") == "antigravity"`.
  - `phan_loai_commit("fix\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", {}, "a2") == "claude_code"`.
  - `phan_loai_commit("fix", {}, "a3") == "chua_xac_dinh"`.
  - `phan_loai_commit("fix", {"a4": "khong"}, "a4") == "khong"`.
  - `trailer_hop_le("x\n\nCong-cu-AI: claude_code") is True`.
  - `trailer_hop_le("x\n\nCong-cu-AI: gpt5") is False`.
  - `trailer_hop_le("x") is False`.
  - `trailer_hop_le("Merge branch 'a'") is True`.
- [ ] **Step 2: FAIL** `pytest tests/test_truy_nguon_commit.py tests/test_kiem_trailer_commit.py -q`
- [ ] **Step 3: Cài đặt**
  - `truy_nguon_commit.py` đọc `git log --format=%H%x1f%ad%x1f%s%x1f%B%x1e --date=short --numstat`. Sinh bảng *Ngày | Commit (7 ký tự) | Tóm tắt | Công cụ | Số tệp | Có chạm test không*, cộng bảng đếm theo công cụ.
  - Câu đầu tệp sinh ra: "Commit `chua_xac_dinh` là commit không ghi công cụ; không đoán. Tác giả xác nhận dần vào `truy-nguon-ghi-de.json`."
  - `.githooks/commit-msg` gọi `python tools/kiem_trailer_commit.py "$1"`; sai thì in hướng dẫn và thoát mã 1.
- [ ] **Step 4: PASS**, rồi `git config core.hooksPath .githooks`. Thử commit không có trailer, phải bị chặn.
- [ ] **Step 5: Sinh** `python -m tools.truy_nguon_commit > docs/minh-bach/truy-nguon-commit.md`.
- [ ] **Step 6: README** mục "Công cụ AI đã dùng" thêm Antigravity (một số commit 25–27/11, gồm sắp xếp lại `src/` và mở rộng phương ngữ) và ChatGPT (ảnh minh họa). Thêm luật trailer `Cong-cu-AI:` và lệnh `git config core.hooksPath .githooks`.
- [ ] **Step 7: Commit** — `feat: truy nguon commit theo cong cu AI va hook bat buoc trailer`

---

### Task 9: Sổ quyết định thiết kế và "AI làm gì / đội sửa gì", mọi dòng có commit kiểm được (minh chứng 1b)

**Files:**
- Create: `docs/minh-bach/so-quyet-dinh-thiet-ke.md`
- Create: `docs/minh-bach/ai-ho-tro-va-doi-tu-sua.md`
- Create: `tests/test_minh_chung_trich_commit.py`

**Interfaces:**
- Produces: quy ước bảng Markdown, mỗi dòng có cột `Bằng chứng` chứa ít nhất một mã commit 7 ký tự trong dấu `` ` `` **hoặc** một đường dẫn tệp có thật.

- [ ] **Step 1: Test `test_moi_dong_co_bang_chung_that`**:
  - Với mỗi tệp `docs/minh-bach/so-quyet-dinh-thiet-ke.md` và `ai-ho-tro-va-doi-tu-sua.md`: đọc các dòng bảng (bắt đầu bằng `| ` và không phải dòng tiêu đề hay dòng `---`).
  - Mỗi dòng phải có ít nhất một bằng chứng.
  - Mỗi mã commit phải qua `git cat-file -e <ma>^{commit}`.
  - Mỗi đường dẫn có dạng `src/…`, `web/…`, `tools/…`, `docs/…`, `tests/…` phải tồn tại.
- [ ] **Step 2: FAIL** (chưa có tệp).
- [ ] **Step 3: Viết sổ quyết định** với các cột *Vấn đề | Phương án đã cân nhắc | Chọn | Vì sao | Người quyết | Bằng chứng*. Chỉ dùng mục có bằng chứng; mục nào không tìm được commit thì bỏ. Ứng viên:
  - Chỉ Bước 1 dùng AI, các bước sau là luật đọc được.
  - Chạy tại chỗ.
  - Mô hình thương mại chỉ để đo.
  - Đường ra bên thứ ba mặc định tắt (Task 5).
  - Không tự đặt `da_duyet=true` (`docs/tri-thuc-thuoc-can-duyet.md`).
  - Chính sách C là mặc định.
  - Không dùng DPO hay v3 (`docs/ket-qua/dpo-v3.md`).
  - Niêm phong tập kiểm tra cuối.
  - Không hứa giảm thời gian làm hồ sơ (README "Giới hạn đã biết").
  - Ghi nhãn "tập phát triển" cho 11,8% (`2fc4eba`).
  - Khóa xuất trước khi ký (commit Task 1).
- [ ] **Step 4: Viết `ai-ho-tro-va-doi-tu-sua.md`**
  - Bảng 1 *Phần | AI hỗ trợ | Đội làm | Công cụ | Bằng chứng*, cho các phần: dữ liệu mô phỏng, huấn luyện, luật K1–K7, cảnh báo, đo lường, giao diện, tài liệu, ảnh.
  - Bảng 2 *Lần đội bác bỏ hoặc sửa đầu ra AI | Lỗi | Cách phát hiện | Bằng chứng*:
    - `2fc4eba`: sửa 3 lỗi trong mã do Antigravity viết ở `8120ce4`.
    - Rà soát độc lập 25–26/11 ra 9 lỗi nặng, vòng 6 vá 4 điểm mù (`397ddbb`).
    - Bảng thuốc cũ ghi sai sintrom = warfarin.
    - Bảng so sánh GPT-4o/Gemini/Claude không có lần chạy nên bị rút (`docs/doi-chieu-so-lieu-bao-cao.md`).
    - Con số 78,3% chưa đo nên bị bỏ (`docs/BAN-GIAO-CONG-VIEC-DANG-DO.md`).
    - Các dòng trong `docs/minh-bach/nhat-ky-hackathon.md` của chính buổi thi.
  - Không ghi phần trăm "AI viết bao nhiêu mã" nếu không đo.
- [ ] **Step 5: PASS** `pytest tests/test_minh_chung_trich_commit.py -q`
- [ ] **Step 6: Commit** — `docs: so quyet dinh thiet ke va bang AI ho tro/doi tu sua (moi dong co commit kiem duoc)`

---

### Task 10: Tổng hợp trả lời BTC, hồi quy toàn bộ

**Files:**
- Create: `docs/minh-bach/TRA_LOI_DE_CAI_TIEN_1.md` (2–3 trang)
- Modify: `docs/minh-bach/nhat-ky-hackathon.md` (dòng kết thúc)

- [ ] **Step 1: Viết tài liệu**, mỗi ý của đề là một mục: *Đề hỏi → Chúng tôi làm gì → Minh chứng (đường dẫn) → Kiểm bằng lệnh nào*.
  - Có mục *Chỗ hở tự tìm và đã sửa* (H1–H5, kèm commit của Task 1–5).
  - Có mục *Còn hạn chế*: H2 nếu chưa đạt ngưỡng, âm thanh chưa có hạn giữ, 33 commit cũ `chua_xac_dinh`, phông Google.
  - Ghi đúng nguyên văn hai xác nhận của tác giả.
- [ ] **Step 2: Hồi quy toàn bộ**

Run: `pytest -q; cd web; npm run lint; npm test; npm run build`
Expected:
- pytest ≥ 1.960 passed cộng số test mới, 0 failed.
- web 0 lỗi kiểu, toàn bộ test pass, build xong.
- Ghi số thật vào tài liệu.

- [ ] **Step 3:** Kiểm 3 ca demo BGK không đổi (cách ở Task 3 Step 7).
- [ ] **Step 4:** Xuất Word/PDF của `TRA_LOI_DE_CAI_TIEN_1.md` (dùng công cụ xuất có sẵn của dự án; không dùng phông Be Vietnam Pro).
- [ ] **Step 5: Commit**, rồi **hỏi tác giả** trước khi push hoặc triển khai.

---

## Ngoài 6 tiếng (làm sau, đặc tả sẵn)

### Task 11: Hạn giữ và xóa âm thanh (giọng nói là dữ liệu nhận dạng)

- `src/audio/storage.py`: thêm `xoa_am_thanh_qua_han(so_ngay: int, bay: float | None = None) -> list[str]`.
  - Xóa tệp âm thanh gốc và bản 16 kHz của phiên đã ký quá `so_ngay` ngày, **giữ** lời thoại đã duyệt và nhật ký sự kiện.
  - Ghi sự kiện `am_thanh_da_xoa`.
  - Mặc định 30 ngày qua `MEDITRACE_GIU_AM_THANH_NGAY`.
- Test: phiên 31 ngày đã ký thì bị xóa; phiên 31 ngày chưa ký thì giữ; phiên 29 ngày thì giữ; sau khi xóa, `load()` vẫn đọc được lời thoại.
- Cập nhật `NOI_LUU_DU_LIEU` (Task 6) và sinh lại sơ đồ.

### Task 12: Tự lưu phông chữ, bỏ `fonts.googleapis.com` (H8)

- Chép tệp phông Newsreader và Plus Jakarta Sans vào `web/public/fonts/` (giấy phép OFL, kiểm trước), đổi `web/index.html` sang `@font-face` tại chỗ.
- Test quét `web/index.html` không còn `googleapis`.

### Task 13: Gán nhãn công cụ cho 33 commit cũ

- Tác giả điền `docs/minh-bach/truy-nguon-ghi-de.json`. Máy không đoán. Sinh lại `truy-nguon-commit.md`.

---

## Phân bổ thời gian và luật cắt

| Task | Phút | Cắt khi trễ |
|---|---|---|
| Chuẩn bị | 10 | — |
| 1 Khóa trước ký | 55 | không cắt |
| 4 Lối ra + log | 60 | bỏ phần Python của Step 5/7 nếu trễ > 15 phút, ghi vào *Còn hạn chế* |
| 5 Chọn tham gia + demo | 20 | không cắt (AIBOX là bên thứ ba) |
| 2 Bộ ca + mốc 0 | 35 | bỏ bộ đo Python, chỉ đo TypeScript |
| 3 Vá bộ che | 45 | dừng theo luật dừng ở Step 5 |
| 6 Sơ đồ dữ liệu | 35 | không cắt |
| 7 Quy trình phê duyệt | 25 | không cắt |
| 8 Truy nguồn commit | 25 | bỏ hook, giữ bảng |
| 9 Sổ quyết định | 30 | giảm còn 6 quyết định |
| 10 Tổng hợp | 20 | không cắt |
| **Tổng** | **360** | |

Thứ tự chạy: Chuẩn bị → 1 → 4 → 5 → 2 → 3 → 6 → 7 → 8 → 9 → 10. Task 6 cần `LOI_RA_DUOC_PHEP` của Task 4; Task 7 cần Task 1; Task 3 cần Task 2.

## Self-review

- **Phủ đề:**
  - "Quyết định thiết kế": Task 9.
  - "Nội dung AI hỗ trợ, đội tự đánh giá/sửa": Task 8, Task 9, nhật ký hackathon.
  - "Không đưa dữ liệu nhận dạng vào dịch vụ": Task 2, 3, 4, 5.
  - "Không đưa vào log": Task 4.
  - "Lịch sử sửa đổi": Task 8.
  - "Sơ đồ dữ liệu": Task 6.
  - "Quy trình bác sĩ phê duyệt trước khi dùng hồ sơ": Task 1, Task 7.
- **Nhất quán tên:**
  - Dùng chung một tên ở mọi chỗ: `choPhepDungHoSo`, `LOI_RA_DUOC_PHEP`, `cheLog`/`che_log`, `in_loi_an_toan`, `NOI_LUU_DU_LIEU`, `sinhSoDoDuLieu`, `phan_loai_commit`, `trailer_hop_le`.
  - Hai luật `MA_CA_BENH`, `TEN_VIET_TAT` mang cùng tên ở cả TypeScript và Python.
- **Đã kiểm khi viết:** 6 lời gọi `fetch(` trong `web/may-chu`; 6 chỗ `traceback.print_exc()`; 1 `urlopen` Python duy nhất; commit `397ddbb` có thật; `sha256HexSync` có trong `compileEffectiveNote.ts`.
- **Chưa kiểm khi viết kế hoạch:**
  - Lệnh xác minh chuỗi WORM (Task 7 Step 3 dặn tra trong `worm.ts`).
  - Cách `kyDuyet.test.ts` dựng mệnh đề cần xác nhận (Task 7 Step 1 dặn bắt chước).
