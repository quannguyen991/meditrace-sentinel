# Cải thiện bộ luật kiểm tra MediTrace — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Giảm tỉ lệ lỗi nguy hiểm lọt qua lớp luật và phát hiện được bỏ sót, có số đo trên tập chưa nhìn, thay vì thêm luật theo cảm tính.

**Architecture:** Giữ nguyên ba tầng hiện có (khoá bằng chứng K1–K7 → cổng rủi ro chính sách C → lớp cảnh báo 60+ mã). Đo lại trước, rồi vá theo thứ tự: bỏ sót → lời nói không dấu câu → gộp tri thức thuốc về một nguồn có trích dẫn. Mọi luật mới vào lớp cảnh báo ở mức `THU_NGHIEM` (chỉ hiện) cho tới khi có số đo trên tập mới.

**Tech Stack:** Python 3.11, pytest, regex; không thêm thư viện. GPU (HoaiĐức, RTX 3060) chỉ dùng ở Giai đoạn 5.

**Spec:** cuộc trao đổi 25/11/2026 ("suy nghĩ và lên plan chi tiết để cải thiện bộ luật, phân tích lỗ hổng, bổ sung"); hiện trạng ghi ở Phần A–B dưới đây.

---

## Phần A. Hiện trạng (đọc mã ngày 25/11/2026)

Luồng chạy thật: `web/server.ts` → `src/dich_vu.py` → `nhanh.chay_trung_gian(..., "C_khoa")` → `dich_vu._them_canh_bao` (`src/dich_vu.py:487`).

| Tầng | Mô-đun | Vai trò | Có đổi trạng thái mệnh đề? |
|---|---|---|---|
| 4 — Khoá bằng chứng | `src/khoa_bang_chung.py` (K1–K7, `doan_chua_ghi`) | Mệnh đề có được vào thân bản nháp không | Có (chặn / cảnh báo) |
| 5 — Cổng rủi ro | `src/cong_rui_ro.py` (chính sách `C-2026-09-22`) | Chấm điểm = mức nghiêm trọng × độ thiếu căn cứ | Có |
| 6 — Lớp cảnh báo | `src/canh_bao/` (`loai.py` 60+ mã, `phat_hien.py` 11 bộ phát hiện, `toan_ca.py` bỏ sót/mâu thuẫn/ghi lặp) | Giải thích "sai kiểu gì" | Không với chính sách C; chính sách D chỉ khi gọi rõ |
| "Lâm sàng nâng cao" | `dieu_phoi_ha_tang.py`, `kiem_duyet_bhyt_va_bo_sot.py` (tầng 4.5 khôi phục bỏ sót, BHYT, liều nhi), `guardrails.py`, `duoc_ly_lam_sang.py`, `hieu_chinh_lieu.py`, `aho_corasick_duoc_thu.py` | Kiểm thuốc, liều, ICD-10 | Không. Ghi vào trường riêng `lam_sang_nang_cao` |

Số đo duy nhất có hệ thống: `src/do_canh_bao.py` (24/09/2026) trên 4 bộ thử thách phát triển (300 ca, 2.789 mệnh đề, đầu ra thế hệ 8). Lỗi nguy hiểm lọt: chính sách C 44,7%, D 43,3%. Chặn thừa: C 8,1%, D 6,2%. Nhãn so sánh là **bộ chấm tự động**, không phải nhãn người.

## Phần B. Lỗ hổng (có dẫn chứng)

| Mã | Lỗ hổng | Dẫn chứng | Hậu quả |
|---|---|---|---|
| L1 | **Không có số đo hiện tại.** 44,7% là đầu ra thế hệ 8, tháng 9; luật đã sửa khi nhìn chính các ca đó; dữ liệu đo nằm ở dự án cũ `D:\Claude\khkt-benh-an\kaggle-ra\the-he-8-chinh-sach-C`, `do_canh_bao.THU_MUC` trỏ vào thư mục không tồn tại ở repo này. | `src/do_canh_bao.py:11-14,35` | Không biết luật nào đang có ích; mọi thay đổi không kiểm chứng được |
| L2 | **Hai bộ bỏ sót chạy song song, khác nhau.** `canh_bao/toan_ca.bo_sot` dùng `THUOC_TU_DIEN`; `ActiveOmissionRecoveryEngine` dùng 31 tên thuốc viết cứng. | `src/canh_bao/toan_ca.py:20-56`, `src/kiem_duyet_bhyt_va_bo_sot.py:181-301` | Bác sĩ thấy hai danh sách "có thể bỏ sót" không khớp nhau |
| L3 | **Lỗi trong tầng 4.5:** chỉ cần một mệnh đề bất kỳ chứa chữ "dị ứng" (kể cả "không dị ứng") là bỏ qua mọi dị ứng bị sót; mỗi đoạn chỉ báo một loại (`continue`). | `src/kiem_duyet_bhyt_va_bo_sot.py:225,235` | Bỏ sót dị ứng thật — loại lỗi nặng nhất — bị che |
| L4 | **Bỏ sót câu trả lời ngắn không thấy được.** `doan_chua_ghi` bỏ mọi đoạn kết thúc bằng "?" và mọi đoạn không có từ nội dung. "BS: Chị có dị ứng thuốc gì không? / BN: Dạ có ạ." → cả hai lượt bị bỏ qua. | `src/khoa_bang_chung.py:521,527` | Mất đúng loại thông tin quan trọng nhất trong hỏi bệnh |
| L5 | **Tiêu chí "đã phủ" quá lỏng:** một đoạn coi là đã ghi nếu chung **một** từ nội dung với bất kỳ mệnh đề nào dẫn tới lượt đó. | `src/khoa_bang_chung.py:531` | Lượt dài nhiều ý (v2 có 3.196 lượt > 40 từ) che bỏ sót |
| L6 | **Cảnh báo bỏ sót chung chung vô dụng:** `POSSIBLE_IMPORTANT_OMISSION` 792/887 cảnh báo, chỉ 2,8% trúng. | `src/canh_bao/toan_ca.py:48-50` | Đang bị ẩn; thực chất không có bộ phát hiện bỏ sót tổng quát |
| L7 | **Phụ thuộc dấu câu và nhãn người nói.** `cac_doan`, `cac_cau`, nhận câu hỏi bằng "?", `TRA_LOI_KHONG` neo đầu câu. Văn bản chép từ âm thanh thường không có dấu câu. Không có phép thử nào trên đầu vào không dấu. | `src/canh_bao/phat_hien.py:41,256-258`; `khoa_bang_chung.cac_doan` | Luật yếu đi âm thầm khi gặp lời nói thật |
| L8 | **Tri thức thuốc nằm rải rác.** Liều tối đa paracetamol ở ít nhất 3 nơi; danh sách thuốc ở 4 nơi (`thuc_the.THUOC_TU_DIEN`, `RE_THUOC_PHO_BIEN`, `cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP`, `aho_corasick_duoc_thu`). | `duoc_ly_lam_sang.py:157`, `guardrails.py:296`, `kiem_duyet_bhyt_va_bo_sot.py:143` | Sửa một nơi, nơi khác vẫn cũ; hai kết luận khác nhau cho một đơn |
| L9 | **Ngưỡng y khoa không trích nguồn, không có phép thử.** `hieu_chinh_lieu.py` 0 chỗ ghi nguồn; `quet_an_toan_duoc_ly_v2.py` 0 nguồn, không ai nhập. (Sửa 25/11 sau Task 0.2: cả hai mô-đun này và `aho_corasick_duoc_thu.py` **có** phép thử — nhận định cũ "không phép thử" là sai.) | `docs/kiem-ke-luat.md` | Không bảo vệ được trước hội đồng; có thể sai liều |
| L10 | **Hai hệ cảnh báo song song.** `lam_sang_nang_cao` không đi qua lớp cảnh báo, không có mã, không có mức tin cậy, không đổi trạng thái. | `src/dich_vu.py:505-533` | Bác sĩ không biết tin hệ nào |
| L11 | **Lỗ hổng ngữ nghĩa đã tự khai** (`CHUA_PHAT_HIEN`): đại từ qua nhiều lượt, quan hệ thuốc–chỉ định, tóm tắt mất điều kiện. | `src/canh_bao/loai.py:228-243` | Regex không làm được; cần cách khác |
| L12 | **Từ điển luật xây cho 200 khuôn cũ.** 400 khuôn mới thêm bệnh và thuốc mới; chưa đo độ phủ từ điển. | `khuon_mo_rong.py`, `khuon_lo_*.py` | Thuốc mới không được nhận ra → không báo bỏ sót, không báo bịa |
| L13 | **Số liệu trong tài liệu nói quá.** `docs/tai-lieu/BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md:55-58` ghi "0,0% (K1–K7 ngăn chặn hoàn toàn)", "0,8% lọt đính chính", trái với 44,7% đã đo. | dòng 55-58 | Rủi ro liêm chính khi nộp báo cáo |

## Global Constraints

- Không đổi mặc định `chinh_sach="C"` trong `nhanh.chay_trung_gian`; mọi đổi trạng thái mới đi qua chính sách D hoặc một chính sách mới có tên riêng.
- Luật mới vào `canh_bao/loai.py` với `tin_cay=THU_NGHIEM` cho tới khi có precision ≥ 0,5 trên **tập mới** (Giai đoạn 1); chỉ sau đó mới được đổi sang `ON_DINH`.
- Không thêm ngưỡng liều, tương tác, chống chỉ định nào thiếu trường `nguon` (văn bản, số hiệu, trang) và `da_duyet`. Mục `da_duyet=False` chỉ được sinh cảnh báo mức `can_xem`, không bao giờ chặn.
- Mọi số báo cáo ghi rõ "so với bộ chấm tự động" hoặc "so với nhãn người", và ghi tên tập.
- Tập kiểm tra cuối (`*_kiem_tra*`) không được mở cho tới Giai đoạn 5.
- Suy luận GPU: trần `--phan-vram 0.70`, tổng ≤ 10,8 GiB; không chạy khi HoaiĐức đang huấn luyện.
- Repo có ~243 tệp chưa commit từ các phiên khác: chỉ `git add` đúng tệp của task; không commit khi người dùng chưa đồng ý.

## Review Focus

1. Đầu vào không dấu câu, chữ thường (văn bản chép từ âm thanh) — luật phải cho kết quả gần như đầu vào có dấu (Task 3.2 ghim).
2. Câu trả lời một chữ ("Dạ có", "Không ạ") sau câu hỏi của bác sĩ — phải sinh cảnh báo bỏ sót khi không mệnh đề nào dẫn tới (Task 2.2 ghim).
3. Ca vừa có "không dị ứng thức ăn" vừa có "dị ứng penicillin" — không được che nhau (Task 2.1 ghim).
4. Thuốc chỉ có ở 400 khuôn mới — phải có trong từ điển chung (Task 4.1 ghim bằng phép thử phủ từ điển).
5. Lời người nhà nói về bệnh của chính họ trong lượt dài — luật bỏ sót không được gán sang bệnh nhân (Task 2.3 ghim).

---

## Giai đoạn 0 — Đo lại hiện trạng (CPU, làm ngay)

### Task 0.1: Đưa bộ thử thách vào repo và đo mốc 0

**Files:**
- Create: `data/thach_thuc/` (chép 4 tệp `thach_thuc_*_phat_trien.jsonl` + `ra_C_khoa_*.jsonl` từ `D:\Claude\khkt-benh-an\kaggle-ra\the-he-8-chinh-sach-C`), `data/thach_thuc/MANIFEST.json` (SHA-256 từng tệp)
- Modify: `src/do_canh_bao.py:35-38` (thêm `--thu-muc`, `--nhanh`, `--ra-json`)
- Test: `tests/test_do_canh_bao_tham_so.py`
- Output: `docs/ket-qua/canh-bao-moc-0.md`

**Interfaces:**
- Produces: `do_canh_bao.chay(thu_muc: Path, nhanh: str = "C_khoa") -> dict` trả `{"theo_ma": {ma: {"ban","dung_loai","co_loi","precision"}}, "chinh_sach": {"C": {"lot_nguy_hiem","chan_thua"}, "D": {...}}, "so_menh_de": int}`

- [ ] **Step 1: Viết phép thử** `test_chay_tren_thu_muc_tam` — tạo thư mục tạm với 1 ca + 1 đầu ra 2 mệnh đề; `kq = do_canh_bao.chay(tmp, "C_khoa")`; assert `kq["so_menh_de"] == 2` và `set(kq["chinh_sach"]) == {"C", "D"}`.
- [ ] **Step 2:** `pytest tests/test_do_canh_bao_tham_so.py -v` → FAIL (`chay()` không nhận tham số).
- [ ] **Step 3:** Sửa `chay` nhận `thu_muc`, `nhanh`; `main()` thêm argparse; mặc định `data/thach_thuc`.
- [ ] **Step 4:** Phép thử PASS. Chạy `python -m src.do_canh_bao --ra-json docs/ket-qua/canh-bao-moc-0.json`.
- [ ] **Step 5:** Viết `docs/ket-qua/canh-bao-moc-0.md`: bảng lọt/chặn thừa C và D, 10 mã có precision thấp nhất, 10 mã lỗi bộ chấm thấy mà không cảnh báo nào bắt. So với số 24/09 (44,7% / 8,1%) và giải thích chênh lệch nếu có (luật đã sửa từ đó).

### Task 0.2: Kiểm kê luật

**Files:**
- Create: `tools/kiem_ke_luat.py`, `docs/kiem-ke-luat.md`
- Test: `tests/test_kiem_ke_luat.py`

**Interfaces:**
- Produces: `kiem_ke(thu_muc_src: Path, thu_muc_tests: Path) -> list[dict]` mỗi phần tử `{"mo_dun", "duoc_nhap_boi": list[str], "co_phep_thu": bool, "so_cho_ghi_nguon": int, "nam_tren_luong_chinh": bool}`

- [ ] **Step 1: Phép thử** `test_mo_dun_khong_ai_nhap` — thư mục tạm có `a.py` nhập `b`, và `c.py` không ai nhập; assert phần tử `c` có `duoc_nhap_boi == []`.
- [ ] **Step 2:** FAIL. **Step 3:** cài bằng `ast` (không regex) để đọc `import`/`from src import`. Luồng chính = bao đóng nhập từ `src/dich_vu.py`.
- [ ] **Step 4:** PASS; sinh `docs/kiem-ke-luat.md`. Đánh dấu ứng viên mã chết (dự kiến: `quet_an_toan_duoc_ly_v2.py`, `nhanh_e.py`) — **không xoá**, chỉ liệt kê để người dùng quyết.

### Task 0.3: Đối chiếu số liệu trong tài liệu (L13)

**Files:**
- Create: `docs/doi-chieu-so-lieu-bao-cao.md`

- [ ] **Step 1:** Liệt kê mọi con số về lọt lỗi, sai lệch, bỏ sót trong `docs/tai-lieu/*.md`, `docs/final/*.md` (grep `%`), mỗi số một dòng: tệp:dòng, con số, nguồn đo (lệnh, tệp kết quả) hoặc "không tìm thấy nguồn".
- [ ] **Step 2:** Với số không có nguồn hoặc trái với `canh-bao-moc-0.md`: ghi số đúng thay thế. **Không sửa tài liệu báo cáo** — đưa bảng cho người dùng duyệt.

---

## Giai đoạn 1 — Tập đo mới, chống thiên lệch

### Task 1.1: Sinh bộ thử thách mới từ khuôn chưa nhìn

**Files:**
- Create: `tools/sinh_thach_thuc_v2.py`, `data/thach_thuc_v2/*.jsonl`, `docs/dang-ky-truoc-bo-luat.md`
- Test: `tests/test_sinh_thach_thuc_v2.py`

**Interfaces:**
- Consumes: `kho_khuon.ds_khuon(mo_rong=True)`, `kho_khuon.thanh_vien_dot()`, bộ sinh `sinh_hoi_thoai_viet.sinh_ca`
- Produces: 6 tệp, mỗi tệp 40 ca, chỉ từ khuôn thuộc tập phát triển của đợt 2–3 (khuôn 201–600): `dinh_chinh`, `doi_chu_the`, `phuong_ngu`, `nhieu_asr`, **`tra_loi_ngan`** (mới: câu hỏi có/không + trả lời một chữ, ≥ 3 cặp/ca), **`khong_dau_cau`** (mới: bỏ dấu câu, chữ thường, chèn "ờ", "à", lặp từ).

- [ ] **Step 1: Phép thử** `test_khong_dung_khuon_train` — mọi `khuon` trong tệp sinh ra thuộc `tap_cua_ca(...) == "phat_trien"`; `test_tra_loi_ngan_co_cap` — mỗi ca `tra_loi_ngan` có ≥ 3 lượt bệnh nhân ≤ 3 từ ngay sau lượt bác sĩ là câu hỏi, và đáp án có mệnh đề dẫn tới lượt đó; `test_khong_dau_cau` — `input` không chứa `.,?!`.
- [ ] **Step 2–4:** FAIL → cài → PASS.
- [ ] **Step 5:** Viết `docs/dang-ky-truoc-bo-luat.md` **trước** khi chạy bất kỳ luật nào trên tập này: chỉ số chính (tỉ lệ lỗi nguy hiểm lọt, chặn thừa, precision cảnh báo bỏ sót), ngưỡng thành công (Giai đoạn 5), danh sách tệp + SHA-256.

### Task 1.2: Tập nhãn người nhỏ — **BỎ 25/11/2026** (không có người gán nhãn kịp; xem mục sửa đổi trong `docs/dang-ky-truoc-bo-luat.md`)

**Files:**
- Create: `data/thach_thuc_v2/nhan_nguoi_40.jsonl`, `docs/huong-dan-gan-nhan-loi.md`

- [ ] **Step 1:** Chọn 40 ca (lấy đều 6 tệp) sau khi Giai đoạn 5 đã có đầu ra mô hình. Hướng dẫn gán: với mỗi mệnh đề chọn một mã nhóm trong `canh_bao.loai.NHOM` hoặc "đúng"; với mỗi lượt chưa ghi đánh dấu "bỏ sót quan trọng / không".
- [ ] **Step 2:** Người gán là người dùng hoặc người có chuyên môn y — **không** để máy gán. Ghi tên người gán, ngày. Đây là tập duy nhất dùng để báo precision "so với nhãn người".

---

## Giai đoạn 2 — Bỏ sót (ưu tiên cao nhất)

### Task 2.1: Một bộ bỏ sót duy nhất, sửa lỗi che dị ứng (L2, L3)

**Files:**
- Create: `src/canh_bao/bo_sot.py`
- Modify: `src/canh_bao/toan_ca.py:20-56` (gọi sang `bo_sot.py`), `src/kiem_duyet_bhyt_va_bo_sot.py:181-301` (`ActiveOmissionRecoveryEngine.quet_khoi_phuc` thành lớp bọc gọi `bo_sot.quet`, giữ nguyên kiểu trả `List[MenhDeKhoiPhuc]` cho `dich_vu`)
- Test: `tests/test_bo_sot_thong_nhat.py`

**Interfaces:**
- Produces: `bo_sot.quet(ctx: NguCanh, ps: list[PhatBieu], doan_chua_ghi: list[dict]) -> list[CanhBao]` — một đoạn có thể sinh nhiều mã (không `continue` sau mã đầu); dị ứng chỉ coi là đã ghi khi có mệnh đề **dương tính** dị ứng cùng chất (dùng `toan_ca._sau_di_ung`).

- [ ] **Step 1: Phép thử**
  - `test_khong_di_ung_thuc_an_khong_che_di_ung_thuoc`: mệnh đề "không dị ứng thức ăn" (phu_dinh=True), lượt chưa ghi "em dị ứng penicillin" → có `OMITTED_ALLERGY`.
  - `test_mot_doan_nhieu_loai`: đoạn "dị ứng penicillin, đang uống warfarin" → có cả `OMITTED_ALLERGY` và `OMITTED_MEDICATION`.
  - `test_hai_dau_ra_cung_ket_qua`: trên cùng ca, tập lượt trong `ActiveOmissionRecoveryEngine.quet_khoi_phuc` ⊆ tập lượt trong `bo_sot.quet`.
- [ ] **Step 2:** FAIL (hai phép đầu fail trên mã cũ). **Step 3:** cài. **Step 4:** PASS + `pytest tests/test_canh_bao.py tests/test_kiem_day_du.py -q` không hồi quy.
- [ ] **Step 5:** Chạy lại `do_canh_bao` trên `data/thach_thuc` → ghi chênh lệch vào `canh-bao-moc-0.md` mục "sau 2.1".

### Task 2.2: Bỏ sót trong cặp hỏi–đáp (L4)

**Files:**
- Modify: `src/khoa_bang_chung.py:508-535` (thêm `cap_hoi_dap_chua_ghi`), `src/canh_bao/loai.py` (mã mới `OMITTED_ANSWER`, nhóm `OMISSION`, mức `CAO`, `tin_cay=THU_NGHIEM`), `src/canh_bao/bo_sot.py`
- Test: `tests/test_bo_sot_hoi_dap.py`

**Interfaces:**
- Produces: `khoa_bang_chung.cap_hoi_dap_chua_ghi(ket_qua, ps, cac_luot) -> list[dict]` mỗi phần tử `{"luot_hoi", "luot_dap", "cau_hoi", "tra_loi", "chu_de"}`; `chu_de` ∈ {"di_ung","thuoc","trieu_chung","tien_su","khac"} suy từ câu hỏi.

- [ ] **Step 1: Phép thử**
  - `test_da_co_khong_ghi`: "BS: Chị có dị ứng thuốc gì không?" / "BN: Dạ có ạ." / không mệnh đề nào dẫn lượt 2 → 1 phần tử, `chu_de == "di_ung"`, `tra_loi == "Dạ có ạ."`.
  - `test_da_ghi_thi_im`: có mệnh đề dẫn lượt 2 → rỗng.
  - `test_cau_hoi_khong_dau`: "bs chị có dị ứng thuốc gì không" / "bn dạ không" → vẫn nhận là cặp (dùng `nhan_cau_hoi` của Task 3.1).
- [ ] **Step 2–4:** FAIL → cài → PASS.

### Task 2.3: Tiêu chí "đã phủ" chặt hơn (L5, L6)

**Files:**
- Modify: `src/khoa_bang_chung.py:531`
- Test: `tests/test_doan_chua_ghi_chat.py`

**Interfaces:**
- Produces: `doan_chua_ghi(..., nguong_phu: float = 0.5)` — đoạn coi là đã phủ khi nằm trong khoảng trích dẫn **hoặc** tỉ lệ từ nội dung của đoạn có trong mệnh đề dẫn tới lượt đó ≥ `nguong_phu`, **hoặc** mọi thực thể (thuốc, con số, bộ phận) của đoạn có trong mệnh đề. Mặc định giữ hành vi cũ khi `nguong_phu=None` để không đổi số chính sách C.

- [ ] **Step 1: Phép thử** `test_luot_dai_hai_y`: lượt "ho ba ngày nay, mẹ em bị tiểu đường" + mệnh đề chỉ "ho ba ngày" → với `nguong_phu=0.5` đoạn "mẹ em bị tiểu đường" nằm trong kết quả, `vai` giữ nguyên người nói; với `None` → không (hành vi cũ).
- [ ] **Step 2–4:** FAIL → cài → PASS.
- [ ] **Step 5:** Quét `nguong_phu` ∈ {0,3; 0,5; 0,7} trên `data/thach_thuc` (CPU): báo số cảnh báo bỏ sót và precision từng mức. Chọn mức có precision `POSSIBLE_IMPORTANT_OMISSION` ≥ 0,15 (hiện 0,028); nếu không mức nào đạt → giữ mã này ẩn và ghi kết luận.

---

## Giai đoạn 3 — Chịu được lời nói thật (L7)

### Task 3.1: Một mô-đun chuẩn hoá lời nói

**Files:**
- Create: `src/canh_bao/loi_noi.py`
- Modify: `src/canh_bao/phat_hien.py:41-50,256-258` và `khoa_bang_chung.cac_doan` gọi sang `loi_noi`
- Test: `tests/test_loi_noi.py`

**Interfaces:**
- Produces:
  - `tach_y(van: str) -> list[tuple[int, int]]` — có dấu câu thì tách theo dấu; không có thì tách theo từ nối ("còn", "nhưng", "mà", "rồi", "với lại", "thêm nữa") và độ dài ≤ 25 từ.
  - `nhan_cau_hoi(van: str) -> bool` — "?" **hoặc** tiểu từ cuối (`không`, `chưa`, `à`, `hả`, `chứ`, `nhỉ`, `không ạ`, `chưa ạ`) **hoặc** mẫu "có … không".
  - `bo_tu_dem(van: str) -> str` — bỏ "ờ", "à" đứng riêng, "ừm", lặp liền một từ ("không không" → "không"), nhưng không bỏ "à" cuối câu hỏi.

- [ ] **Step 1: Phép thử** (mỗi dòng một test, có tên):
  - `tach_y("ho ba ngày nay còn sốt thì hôm qua mới bị")` → 2 khoảng.
  - `nhan_cau_hoi("chị có ho không")` True; `nhan_cau_hoi("em không ho")` False; `nhan_cau_hoi("uống thuốc chưa ạ")` True.
  - `bo_tu_dem("ờ thì em không không có sốt")` == `"thì em không có sốt"`.
- [ ] **Step 2–4:** FAIL → cài → PASS; `pytest tests/test_canh_bao.py tests/test_khoa_bang_chung.py -q` không hồi quy.

### Task 3.2: Phép thử bất biến dấu câu

**Files:**
- Create: `tools/do_bat_bien_dau_cau.py`, `tests/test_bat_bien_dau_cau.py`

**Interfaces:**
- Produces: `do(ca_list, ra_list) -> {"ty_le_ma_giu_nguyen": float, "ma_mat": Counter}` — chạy `gop.chay` hai lần: đầu vào gốc và đầu vào bỏ dấu câu + chữ thường (mệnh đề và trích dẫn chuẩn hoá theo cùng cách), so tập (mã, mệnh đề).

- [ ] **Step 1: Phép thử** `test_ca_mau_bat_bien`: 3 ca mẫu viết tay (đính chính, phủ định, người nhà) → `ty_le_ma_giu_nguyen >= 0.9`.
- [ ] **Step 2:** Đo trên `data/thach_thuc` **trước** Task 3.1 và **sau** Task 3.1; ghi cả hai số vào `docs/ket-qua/canh-bao-moc-0.md`. Mục tiêu sau sửa: ≥ 0,85.

---

## Giai đoạn 4 — Tri thức thuốc: một nguồn, có trích dẫn (L8, L9, L10, L12)

### Task 4.1: `tri_thuc_thuoc.py`

**Files:**
- Create: `src/tri_thuc_thuoc.py`, `data/tri_thuc_thuoc.json`
- Modify: `guardrails.py:296`, `duoc_ly_lam_sang.py:157`, `kiem_duyet_bhyt_va_bo_sot.py:141-160,197-202`, `cong_rui_ro.py:25-31`, `thuc_the.THUOC_TU_DIEN` — đọc từ `tri_thuc_thuoc`
- Test: `tests/test_tri_thuc_thuoc.py`

**Interfaces:**
- Produces: `hoat_chat(ten: str) -> str | None` (biệt dược → hoạt chất), `la_nti(hoat_chat) -> bool`, `lieu_toi_da(hoat_chat, doi_tuong: Literal["nguoi_lon","tre_em"]) -> LieuToiDa | None` với `LieuToiDa(gia_tri: float, don_vi: str, nguon: str, da_duyet: bool)`, `regex_ten_thuoc() -> re.Pattern`.
- Mỗi mục JSON bắt buộc `nguon` (ví dụ "Dược thư Quốc gia Việt Nam 2022, tr. …") và `da_duyet` (mặc định `false`).

- [ ] **Step 1: Phép thử**
  - `test_khong_con_lieu_viet_cung`: grep `src/*.py` (trừ `tri_thuc_thuoc.py`, `khuon_*`, `ngu_lieu_viet.py`) không còn literal `4000.0` cạnh tên thuốc.
  - `test_moi_muc_co_nguon`: mọi mục trong JSON có `nguon` không rỗng.
  - `test_phu_thuoc_trong_khuon`: mọi tên thuốc trong trường `ke_hoach` của 600 khuôn (lấy bằng `regex_ten_thuoc` cũ ∪ danh sách hoạt chất) nhận được `hoat_chat(...) is not None` — in danh sách thiếu nếu fail.
- [ ] **Step 2–4:** FAIL → cài (chuyển dữ liệu, chưa thêm số mới) → PASS.
- [ ] **Step 5:** Xuất `docs/tri-thuc-thuoc-can-duyet.md` liệt kê mọi mục `da_duyet=false` cho người có chuyên môn duyệt. **Không** tự đặt `da_duyet=true`.

### Task 4.2: Đưa "lâm sàng nâng cao" vào lớp cảnh báo

**Files:**
- Modify: `src/canh_bao/loai.py` (mã `DOSE_OVER_MAX`, `DRUG_INTERACTION`, `CONTRAINDICATION`, nhóm mới `CLINICAL_KNOWLEDGE`, `tin_cay=THU_NGHIEM`), `src/canh_bao/gop.py`, `src/dich_vu.py:505-533`
- Test: `tests/test_canh_bao_lam_sang.py`

- [ ] **Step 1: Phép thử** `test_lieu_vuot_qua_thanh_canh_bao`: mệnh đề "paracetamol 1000 mg ngày 6 lần" → có `CanhBao(ma="DOSE_OVER_MAX")` trong `gop.chay`, `anh_huong_trang_thai is False`; `test_muc_chua_duyet_chi_can_xem`: khi mục `da_duyet=false` → `ket_luan == CAN_XEM`.
- [ ] **Step 2–4:** FAIL → cài → PASS. Giữ trường `lam_sang_nang_cao` cho giao diện cũ nhưng sinh từ cùng kết quả (một nguồn).

---

## Giai đoạn 5 — Đo trên mô hình mới và quyết định chính sách (GPU)

### Task 5.1: Chạy v3 trên bộ thử thách

- [ ] **Step 1:** Sau khi v3 huấn luyện xong và đo bỏ sót xong: chạy `nhanh C_khoa` với adapter v3 trên `data/thach_thuc_v2` (240 ca) qua `tools/run_capped.py --phan-vram 0.70`. Ước tính 4–10 phút/ca → 16–40 giờ; chạy nền, có bộ đệm để tiếp tục khi đứt.
- [ ] **Step 2:** `python -m src.do_canh_bao --thu-muc data/thach_thuc_v2` cho chính sách C, D, và D' (= D + các mã `THU_NGHIEM` đạt precision ≥ 0,5).
- [ ] **Step 3:** Precision trên `nhan_nguoi_40.jsonl` cho các mã bỏ sót và mã mới.

### Task 5.2: Quyết định (theo đăng ký trước)

- [ ] Ngưỡng thành công đăng ký trong Task 1.1: lọt nguy hiểm giảm ≥ 10 điểm % so với C **và** chặn thừa ≤ 10%. Đạt → đề xuất nâng mã lên `ON_DINH`, cập nhật `CHINH_SACH` mới có tên ngày; không đạt → giữ C, báo cáo trung thực.
- [ ] Cập nhật `docs/tien-do-21-11-2026.md` và bảng đối chiếu Task 0.3.

## Ngoài phạm vi (ghi lại, không làm trong plan này)

- L11 (đại từ qua nhiều lượt, quan hệ thuốc–chỉ định): regex không làm được. Hướng khả thi là cho Qwen3-4B kiểm lại từng mệnh đề với câu trích ("câu này có ủng hộ mệnh đề không: có/không/không rõ"), nhưng tốn thêm một lượt suy luận mỗi mệnh đề. Chỉ cân nhắc sau Giai đoạn 5.
- Thêm luật y khoa mới (tương tác, chống chỉ định): chỉ sau Task 4.1 và khi có người duyệt.

## Thứ tự và thời gian ước tính

| Giai đoạn | Cần GPU | Ước tính | Phụ thuộc |
|---|---|---|---|
| 0 | Không | 0,5 ngày | — |
| 1.1 | Không | 0,5 ngày | 0.1 |
| 2 | Không | 1–1,5 ngày | 0.1 |
| 3 | Không | 1 ngày | 0.1; 2.2 dùng `nhan_cau_hoi` của 3.1 → làm 3.1 trước 2.2 |
| 4 | Không | 1 ngày (+ thời gian người duyệt) | 0.2 |
| 1.2, 5 | Có | 2–3 ngày máy + 40 ca gán tay | v3 xong, 1.1, 2, 3 |
