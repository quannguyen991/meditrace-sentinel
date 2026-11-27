# Nâng cấp toàn diện MediTrace theo chất vấn của Ban Giám khảo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đóng các lỗ hổng mà ban giám khảo đã chỉ ra hoặc sẽ chất vấn: bỏ sót, lỗi lan qua các bước, báo nhầm, gán sai người, đối chứng với AI thương mại, dữ liệu mô phỏng, tốc độ, thời gian duyệt và bảng tri thức chưa duyệt. Mỗi cải tiến phải có số đo đã đăng ký trước.

**Architecture:** Giữ nguyên nguyên tắc "chỉ Bước 1 dùng AI, các bước sau là luật đọc được". Các cải tiến được thêm vào thành chốt mới ở đúng bước của đường ống `src/duong_ong/` (b1 quét lại, b2 hai nguồn chủ thể, b5 cổng ASR) và ở lớp cảnh báo `src/canh_bao/`. Tất cả cùng đi qua khóa căn cứ K1–K6 có sẵn. Phép đo dùng các công cụ đã có trong `tools/` và `src/do_luong/`. Kết quả ghi vào `docs/ket-qua/`, rồi cập nhật README, báo cáo cải tiến và bộ Q&A.

**Tech Stack:** Python 3.11 (pytest), Qwen3-4B + adapter QLoRA (transformers), React/TypeScript (tsx --test, vite), Node/Express BFF, SQLite.

**Spec:** `BAO_CAO_CAI_TIEN_CHANG_1.md` (ba yêu cầu cải tiến của ban giám khảo và số liệu hiện tại) và `Q_AND_A_BAN_GIAM_KHAO.md` (các câu chất vấn). Số liệu hiện tại lấy từ `docs/ket-qua/` và commit `580c84b`.

## Đường cơ sở (đo trước khi sửa, không chạy lại)

| Chỉ số | Hiện tại | Nguồn |
|---|---|---|
| Bỏ sót mệnh đề Tầng 1, 30 ca dev | 11,5% (v1), 14,1% (v3) | `docs/ket-qua/bo-sot-qwen3-4b.md` |
| Cảnh báo bỏ sót toàn ca: độ phủ / độ chính xác | 12,5% / 2,8% | `docs/ket-qua/canh-bao-moc-0.md` |
| Lỗi nguy hiểm lọt vào thân, chính sách D | 24,1% | commit `580c84b`, `docs/ket-qua/truyen-lan-loi-tung-tang.json` |
| Bộ nhiễu ASR: tỷ lệ chặn lỗi nguy hiểm | 53,7% | như trên |
| Cảnh báo trên bản ghi sạch | 7,11 / ca | `docs/ket-qua/cay-loi.md` |
| Gán sai người: dự án / mô hình thương mại | 7,6% / 1,4% | README "Kết quả đo" |
| Thời gian tạo một bản nháp | ~3,5 phút (RTX 3060) | README |

## Global Constraints

- Tập kín `viet_kiem_tra_cuoi*` đang niêm phong, không mở. `thach_thuc_v2` đã chạy một lần, **không chạy lại**. Mọi điều chỉnh làm trên tập phát triển; con số "tập kín" chỉ đo một lần ở Task 12.
- Ngưỡng và mục tiêu phải đăng ký trước (Task 0) và commit trước khi đo. Đo xong phải ghi đúng con số, kể cả khi không đạt.
- GPU: `--phan-vram 0.70`, không vượt.
- Không bao giờ đặt `da_duyet = true` thay người duyệt. Chỉ công cụ duyệt (Task 10) mới ghi được, và phải có `duyet_boi`.
- Chính sách C vẫn là mặc định của sản phẩm. Các chốt mới chỉ đổi mặc định khi Task 12 cho thấy đạt mục tiêu.
- Mô hình thương mại chỉ dùng để đo, không bao giờ nằm trong sản phẩm. Trước khi gọi API: kiểm số dư, ước tính chi phí, hỏi người dùng.
- Chỉ `git add` tệp của chính task. Không viết lại lịch sử, không force-push. Có phiên khác cùng sửa repo, nên chạy `git status` trước khi sửa tệp dùng chung.
- Không in bí mật. Không khởi động lại máy HoaiĐức. Không xóa tệp trên HoaiĐức khi chưa hỏi.
- Giao diện: chữ tiếng Việt, không dùng phông Be Vietnam Pro, cỡ chữ tối thiểu 13px.
- Mọi mệnh đề mới (quét lại, khôi phục) vẫn phải qua K1–K6. Mệnh đề không qua chỉ được vào `CẦN XÁC NHẬN`, không được vào thân.

## Review Focus

1. Hội thoại có một lượt rất dài chứa nhiều vế, trong đó một vế đã được trích. Vế còn lại vẫn phải được quét lại hoặc báo bỏ sót, không bị coi là "lượt đã có mệnh đề" (đây là nguyên nhân của 86% ca sót). → test trong Task 1 và Task 2.
2. Lượt ASR có tên thuốc bị nghe nhầm nhưng câu trích vẫn khớp nguyên văn với bản chép sai. Mệnh đề thuốc/dị ứng từ lượt đó phải vào `CẦN XÁC NHẬN`, không vào thân. → test trong Task 3.
3. Lời của người nhà dùng "con" để tự xưng ("con bị dị ứng tôm") trong khi mô hình gán là bệnh nhân. Phải xếp vào xác nhận, không vào mục DỊ ỨNG. → test trong Task 4.
4. Ca hoàn toàn sạch: theo mặc định, giao diện chỉ hiện cảnh báo trong ngân sách. Các cảnh báo `cao` không bao giờ bị ẩn vì ngân sách. → test trong Task 5.
5. Ghi âm bị cắt giữa chừng (đóng tab khi đang ghi). Các cửa sổ đã trích phải còn nguyên, bản nháp dựng được từ phần đã có. → test trong Task 8.

---

### Task 0: Đăng ký trước mục tiêu và tập đo

**Files:**
- Create: `docs/dang-ky-truoc-nang-cap-27-11.md`
- Test: `tests/test_dang_ky_truoc_27_11.py`

**Interfaces:**
- Produces: bảng mục tiêu mà Task 1–9 và 12 đối chiếu. Mỗi dòng gồm `ma_muc_tieu` (`MT1`..`MT9`), chỉ số, tập đo, đường cơ sở, ngưỡng đạt.

- [ ] **Step 1: Viết test kiểm tài liệu có đủ 9 mục tiêu, mỗi mục có tập đo và ngưỡng**

```python
def test_dang_ky_truoc_du_9_muc_tieu():
    van = Path("docs/dang-ky-truoc-nang-cap-27-11.md").read_text(encoding="utf-8")
    for i in range(1, 10):
        assert f"| MT{i} |" in van
    assert "viet_kiem_tra_cuoi" in van and "chỉ đo một lần" in van
```

- [ ] **Step 2: Chạy test, phải FAIL vì chưa có tệp**

Run: `pytest tests/test_dang_ky_truoc_27_11.py -v`
Expected: FAIL (FileNotFoundError)

- [ ] **Step 3: Viết tài liệu với đúng các ngưỡng sau**

| Mã | Chỉ số | Tập đo | Cơ sở | Ngưỡng đạt |
|---|---|---|---|---|
| MT1 | Bỏ sót mệnh đề sau quét lại | 30 ca đầu `viet_phat_trien_v2` (như cơ sở) | 11,5% | ≤ 8,0%, cận trên Wilson < 11,5% |
| MT2 | Cảnh báo bỏ sót: độ phủ / độ chính xác | 4 bộ `thach_thuc/*_phat_trien` | 12,5% / 2,8% | ≥ 40% / ≥ 10% |
| MT3 | Lỗi nguy hiểm lọt vào thân (chính sách D + cổng ASR) | như trên | 24,1% | ≤ 15%, đồng thời chặn thừa ≤ 8% |
| MT4 | Gán sai người trong thân | bộ "đổi người" + "tự sửa" phát triển | 7,6% | ≤ 4,0% |
| MT5 | Cảnh báo hiển thị mặc định trên bản sạch | 400 ca cấy lỗi tập điều chỉnh | 7,11 / ca | ≤ 2,0 / ca, độ nhạy hiển thị ≥ 0,85 |
| MT6 | Câu trích của mô hình thương mại không qua K1–K6 | 60 ca `thach_thuc` phát triển | chưa đo | chỉ báo cáo, không có ngưỡng |
| MT7 | Độ đồng thuận giữa bộ chấm tự động và nhãn người | 40 ca | chưa đo | Cohen κ ≥ 0,6 thì bộ chấm được coi là đáng tin |
| MT8 | Thời gian từ lúc dừng ghi tới khi có bản nháp | 10 ca dài ≥ 15 lượt | ~210 s | ≤ 45 s |
| MT9 | Trung vị thời gian duyệt của bác sĩ | phiên thử ≥ 5 người dùng | chưa đo | chỉ báo cáo |

Kèm theo: tập kín `viet_kiem_tra_cuoi_v2` **chỉ đo một lần** ở Task 12, sau khi khóa toàn bộ luật.

- [ ] **Step 4: Chạy test, phải PASS**

Run: `pytest tests/test_dang_ky_truoc_27_11.py -v`
Expected: PASS

- [ ] **Step 5: Commit (trước mọi phép đo)**

```bash
git add docs/dang-ky-truoc-nang-cap-27-11.md tests/test_dang_ky_truoc_27_11.py
git commit -m "docs: dang ky truoc muc tieu nang cap 27/11 (MT1-MT9)"
```

---

### Task 1: Quét lại các vế chưa được trích (giảm bỏ sót ở Bước 1)

**Files:**
- Create: `src/duong_ong/b1_quet_lai_ve.py`
- Modify: `src/duong_ong/chay_duong_ong.py` (`chay_trung_gian`: thêm tham số `quet_lai: bool = False`)
- Test: `tests/test_quet_lai_ve.py`

**Interfaces:**
- Consumes: `cac_doan(van) -> List[Tuple[int,int]]` trong `src/duong_ong/b0_cat_doan_van.py`; `tim_trich(trich, van)` trong `src/duong_ong/b4_kiem_can_cu.py`; `_sinh(tok, model, noi_dung, max_token)` trong `chay_duong_ong.py`.
- Produces:
  - `ve_chua_phu(hoi_thoai: str, phat_bieu: list[dict]) -> list[dict]`: mỗi phần tử có dạng `{"luot": int, "dau": int, "cuoi": int, "van": str, "tin_hieu": list[str]}`. Chỉ giữ vế có tín hiệu lâm sàng (`thuoc`, `di_ung`, `so_lieu`, `phu_dinh`, `trieu_chung`) và không trùng với câu trích nào.
  - `loi_nhac_quet_lai(hoi_thoai: str, ve: list[dict]) -> str`
  - `gop_ket_qua_quet_lai(phat_bieu: list[dict], moi: list[dict]) -> list[dict]`: gắn `"nguon": "quet_lai"` cho mỗi mệnh đề mới và bỏ các mệnh đề trùng câu trích với mệnh đề đã có.

- [ ] **Step 1: Viết test**

```python
HT = "[1] Bác sĩ: Cô dùng thuốc gì?\n[2] Bệnh nhân: Tôi uống amlodipin 5mg, còn dị ứng tôm."
def test_ve_chua_phu_tim_ve_thu_hai_cung_luot():
    ps = [{"trich_dan": "Tôi uống amlodipin 5mg", "bang_chung": [2]}]
    ve = ve_chua_phu(HT, ps)
    assert [v["van"] for v in ve] == ["còn dị ứng tôm"]
    assert "di_ung" in ve[0]["tin_hieu"]
def test_ve_xa_giao_khong_quet():
    assert ve_chua_phu("[1] Bệnh nhân: Vâng ạ.", []) == []
def test_gop_bo_trung_trich_va_gan_nguon():
    cu = [{"trich_dan": "dị ứng tôm", "bang_chung": [2]}]
    moi = [{"trich_dan": "dị ứng tôm", "bang_chung": [2]}, {"trich_dan": "5mg", "bang_chung": [2]}]
    ra = gop_ket_qua_quet_lai(cu, moi)
    assert len(ra) == 2 and ra[1]["nguon"] == "quet_lai"
```

- [ ] **Step 2: Chạy test, phải FAIL**

Run: `pytest tests/test_quet_lai_ve.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Cài đặt ba hàm trên.** Tín hiệu lâm sàng tái dùng bộ từ khóa của `src/canh_bao/bo_sot.py` (`_ten_thuoc`, `_chat_di_ung`) và `la_xa_giao`; không viết bảng từ khóa mới. Trong `chay_trung_gian`, khi `quet_lai=True`, sau lượt trích đầu: gọi `ve_chua_phu`; nếu có vế thì sinh thêm một lần với `loi_nhac_quet_lai`, rồi `gop_ket_qua_quet_lai`. Sau đó mới vào Bước 2–5 như cũ.

- [ ] **Step 4: Chạy test, phải PASS; chạy toàn bộ test đường ống**

Run: `pytest tests/test_quet_lai_ve.py tests/ -k "duong_ong or quet_lai" -q`
Expected: PASS

- [ ] **Step 5: Đo MT1 trên GPU (HoaiĐức, `--phan-vram 0.70`)**

Run: chạy `chay_trung_gian(..., quet_lai=True)` trên 30 ca `viet_phat_trien_v2` để ghi `data/trich_viet_phat_trien_3072_hl_quetlai.jsonl`, rồi
`python tools/do_bo_sot_tren_tap.py --ra docs/ket-qua/bo-sot-quet-lai.md "v1=data/trich_viet_phat_trien_3072_hl.jsonl" "v1+quét lại=data/trich_viet_phat_trien_3072_hl_quetlai.jsonl"`
Expected: có bảng hai dòng; ghi đạt/không đạt MT1 và thời gian chạy thêm mỗi ca.

- [ ] **Step 6: Commit**

```bash
git add src/duong_ong/b1_quet_lai_ve.py src/duong_ong/chay_duong_ong.py tests/test_quet_lai_ve.py docs/ket-qua/bo-sot-quet-lai.md
git commit -m "feat(b1): quet lai ve chua duoc trich, do MT1"
```

---

### Task 2: Cảnh báo bỏ sót theo vế thay vì theo lượt

**Files:**
- Modify: `src/canh_bao/bo_sot.py` (`quet`, `quet_chi_tiet`)
- Test: `tests/test_canh_bao_bo_sot_theo_ve.py`

**Interfaces:**
- Consumes: `ve_chua_phu` (Task 1).
- Produces: `quet(ctx, ps, doan_chua_ghi, cap=())`, giữ nguyên chữ ký, nhưng nay báo theo vế. Mỗi `CanhBao` có thêm `chi_tiet["ve"] = {"luot", "dau", "cuoi"}` để giao diện tô đúng vế.

- [ ] **Step 1: Viết test**: lượt có hai vế, một vế đã được trích, vế kia chứa "dị ứng tôm" → có đúng một cảnh báo `OMITTED_ALLERGY` với `chi_tiet["ve"]["luot"] == 2`. Lượt chỉ có "vâng ạ" → không có cảnh báo.
- [ ] **Step 2: Chạy test, phải FAIL** — `pytest tests/test_canh_bao_bo_sot_theo_ve.py -v`
- [ ] **Step 3: Cài đặt**: thay vòng lặp theo lượt trong `quet_chi_tiet` bằng `ve_chua_phu`, giữ `phan_loai` để đặt mã lỗi.
- [ ] **Step 4: Chạy test và toàn bộ `tests/ -k canh_bao`, phải PASS**
- [ ] **Step 5: Đo MT2** — Run: `python tools/do_truyen_lan_loi_tung_tang.py` và công cụ đo cảnh báo mốc 0 (`src/do_luong/do_canh_bao.py`) trên 4 bộ phát triển. Ghi `docs/ket-qua/canh-bao-bo-sot-theo-ve.md` (độ phủ, độ chính xác, so với 12,5% / 2,8%).
- [ ] **Step 6: Commit** — `git add src/canh_bao/bo_sot.py tests/test_canh_bao_bo_sot_theo_ve.py docs/ket-qua/canh-bao-bo-sot-theo-ve.md` rồi `git commit -m "feat(canh_bao): bao bo sot theo ve, do MT2"`

---

### Task 3: Cổng ASR cho thuốc và dị ứng (giảm lỗi nguy hiểm lọt qua)

**Files:**
- Modify: `src/duong_ong/b5_xep_cho_cong_rui_ro.py` (`cham`, `dua_sang_xac_nhan`)
- Create: `src/duong_ong/b5_cong_asr.py`
- Test: `tests/test_cong_asr.py`

**Interfaces:**
- Consumes: `meta_asr` có dạng `{luot: {"tin_cay_tu": [(dau, cuoi, p)], "bat_dong": bool}}`, đúng dạng mà `src/canh_bao/asr.py` đang đọc; `loai_thong_tin(p)`.
- Produces: `can_qua_cong_asr(p: dict, meta_asr: dict | None, nguong: float = 0.6) -> str | None`. Hàm trả về lý do tiếng Việt khi mệnh đề có `loai_thong_tin` ∈ {`di_ung`, `thuoc`, `thuoc_nti`} và vùng câu trích chạm một từ có `p < nguong`, hoặc lượt có `bat_dong=True`, hoặc tên thuốc chỉ khớp mờ với danh mục (`tra_duoc_thu_aho_corasick`). Ngược lại trả `None`. `dua_sang_xac_nhan` gọi hàm này và chuyển mệnh đề sang `CẦN XÁC NHẬN` với lý do *"tên thuốc/dị ứng nằm ở đoạn ghi âm nghe chưa chắc"*.

- [ ] **Step 1: Viết test**

```python
def test_thuoc_o_vung_asr_kem_vao_xac_nhan():
    p = {"noi_dung": "dùng amoxicillin", "trich_dan": "a mốc xi lin", "bang_chung": [3]}
    meta = {3: {"tin_cay_tu": [(0, 11, 0.42)], "bat_dong": False}}
    assert "nghe chưa chắc" in can_qua_cong_asr(p, meta)
def test_trieu_chung_khong_bi_cong_asr():
    p = {"noi_dung": "ho ba ngày", "trich_dan": "ho ba ngày", "bang_chung": [3]}
    assert can_qua_cong_asr(p, {3: {"tin_cay_tu": [(0, 10, 0.3)], "bat_dong": False}}) is None
def test_khong_co_meta_asr_thi_khong_chan():
    assert can_qua_cong_asr({"noi_dung": "dị ứng tôm", "trich_dan": "dị ứng tôm", "bang_chung": [1]}, None) is None
```

- [ ] **Step 2: Chạy test, phải FAIL** — `pytest tests/test_cong_asr.py -v`
- [ ] **Step 3: Cài đặt `can_qua_cong_asr`**, rồi gọi nó trong `dua_sang_xac_nhan` (chỉ ở chính sách D, chính sách C giữ nguyên).
- [ ] **Step 4: Chạy test và `pytest tests/ -k "cong_rui_ro or b5" -q`, phải PASS**
- [ ] **Step 5: Đo MT3** — Run: `python tools/do_truyen_lan_loi_tung_tang.py` (chính sách D). Expected: ghi lỗi nguy hiểm lọt vào thân và chặn thừa vào `docs/ket-qua/truyen-lan-loi-tung-tang.json`; ghi riêng bộ nhiễu ASR (cơ sở 53,7% chặn).
- [ ] **Step 6: Commit** — `git add src/duong_ong/b5_cong_asr.py src/duong_ong/b5_xep_cho_cong_rui_ro.py tests/test_cong_asr.py docs/ket-qua/truyen-lan-loi-tung-tang.json` rồi `git commit -m "feat(b5): cong ASR cho thuoc/di ung, do MT3"`

---

### Task 4: Hai nguồn xác định chủ thể phải đồng thuận (giảm gán sai người)

**Files:**
- Modify: `src/duong_ong/b2_gom_nguoi_thuc_the.py`
- Modify: `src/duong_ong/b5_xep_cho_cong_rui_ro.py` (`dua_sang_xac_nhan`)
- Test: `tests/test_chu_the_hai_nguon.py`

**Interfaces:**
- Consumes: `lien_ket(hoi_thoai)`, `tim_nguoi(doan)` (b4), `kiem_chu_the(la_bn, vai, ng)` (b4).
- Produces: `chu_the_theo_luat(hoi_thoai: str, luot: int, trich_dan: str) -> str | None`. Hàm trả về `"benh_nhan"`, `"nguoi_nha:<quan_he>"`, `"nguoi_khac"` hoặc `None` khi luật không đủ căn cứ. `dua_sang_xac_nhan` chuyển sang xác nhận khi kết quả luật khác `None` và khác chủ thể mô hình gán, với lý do *"mô hình và luật xác định người khác nhau"*. Mệnh đề thuộc loại `di_ung`/`thuoc` có kết quả luật `None` mà người nói không phải bệnh nhân cũng phải vào xác nhận.

- [ ] **Step 1: Viết test**, gồm 3 ca:
  - Mẹ nói "con bị dị ứng tôm", mô hình gán bệnh nhân là trẻ → luật trả `"benh_nhan"`, đồng thuận, không chặn.
  - Mẹ nói "bản thân tôi dị ứng penicillin", mô hình gán bệnh nhân → luật trả `"nguoi_nha:me"` → chuyển vào xác nhận.
  - Người bệnh khác cùng phòng nói "còn tôi thì dị ứng cefuroxim" → luật trả `"nguoi_khac"` → chuyển vào xác nhận.
- [ ] **Step 2: Chạy test, phải FAIL** — `pytest tests/test_chu_the_hai_nguon.py -v`
- [ ] **Step 3: Cài đặt** bằng cách tái dùng `tim_nguoi` và bảng xưng hô có sẵn trong b2; không thêm bảng từ mới.
- [ ] **Step 4: Chạy test, `tests/test_demo_bac_si_nguoi_nha.py` và `pytest tests/ -q`, tất cả phải PASS** (ba ca mẫu cho ban giám khảo không được đổi kết quả).
- [ ] **Step 5: Đo MT4** bằng `src/do_luong/cham_chu_the.py` trên bộ "đổi người" và "tự sửa" phát triển → `docs/ket-qua/chu-the-hai-nguon.md`.
- [ ] **Step 6: Commit** — `git commit -m "feat(b2): chu the hai nguon dong thuan, do MT4"`

---

### Task 5: Ngân sách cảnh báo (giảm báo nhầm mà bác sĩ phải xem)

**Files:**
- Modify: `src/canh_bao/gop.py` (thêm hàm), `src/he_thong/dich_vu_http.py` (trả thêm trường)
- Modify: `web/src/types/api-contract.ts`, `web/src/components/VerificationView.tsx`, `web/src/components/DuyetBenCanh.tsx`
- Test: `tests/test_ngan_sach_canh_bao.py`, `web/src/lib/nganSachCanhBao.test.ts`

**Interfaces:**
- Consumes: `CanhBao` (`muc_do`, `ket_luan`, `uu_tien`) trong `src/canh_bao/loai.py`.
- Produces:
  - `chon_hien_thi(ds: list[CanhBao], ngan_sach: int = 2) -> tuple[list[CanhBao], list[CanhBao]]` trả về `(hien, gap)`. Mọi cảnh báo `muc_do == "cao"` có `ket_luan == "loi_phat_hien"` luôn nằm trong `hien`, kể cả khi vượt ngân sách. Phần còn lại sắp theo `_khoa_sap` và lấy tới khi đủ `ngan_sach`.
  - API trả `canh_bao_hien` và `canh_bao_gap` (khóa của `CanhBao.to_dict()`).
  - Giao diện hiện `canh_bao_hien`; `canh_bao_gap` nằm sau nút "Xem thêm N gợi ý".

- [ ] **Step 1: Viết test Python**

```python
def test_cao_luon_hien_du_vuot_ngan_sach():
    ds = [cb("NEGATION_FLIP", "cao", "loi_phat_hien")] * 3 + [cb("OMITTED_ANSWER", "thap", "can_xem")]
    hien, gap = chon_hien_thi(ds, ngan_sach=2)
    assert len(hien) == 3 and len(gap) == 1
def test_ban_sach_chi_hien_toi_da_ngan_sach():
    ds = [cb("OMITTED_ANSWER", "trung", "nghi_rui_ro")] * 7
    hien, gap = chon_hien_thi(ds, 2)
    assert len(hien) == 2 and len(gap) == 5
```

- [ ] **Step 2: Chạy test, phải FAIL**
- [ ] **Step 3: Cài đặt `chon_hien_thi` và nối vào API.** Ở giao diện, `nganSachCanhBao.test.ts` kiểm rằng component chỉ render `canh_bao_hien` và nút "Xem thêm" mang đúng số lượng.
- [ ] **Step 4: Chạy test** — `pytest tests/test_ngan_sach_canh_bao.py -q` và `cd web && npm run lint && npx tsx --test src/lib/nganSachCanhBao.test.ts`. Expected: PASS.
- [ ] **Step 5: Đo MT5** bằng `tools/cay_loi.py`/`src/do_luong/do_cay_loi.py` trên 400 ca tập điều chỉnh: số cảnh báo hiển thị trên ca sạch, và độ nhạy khi chỉ tính cảnh báo hiển thị → `docs/ket-qua/ngan-sach-canh-bao.md`.
- [ ] **Step 6: Commit** — `git commit -m "feat(canh_bao): ngan sach hien thi canh bao, do MT5"`

---

### Task 6: Đối chứng "dặn AI thương mại ghi nguồn" (trả lời câu hỏi chất vấn số 1)

**Files:**
- Create: `tools/doi_chung_trich_dan_thuong_mai.py`
- Test: `tests/test_doi_chung_trich_dan.py` (chỉ test phần chấm, không gọi mạng)

**Interfaces:**
- Consumes: hạ tầng gọi API, lược đồ JSON và `MEDITRACE_DATA` riêng trong `tools/doi-chung-thuong-mai.py`; `tim_trich`, `kiem_chu_the` (b4); đáp án `dap_an` của bộ thử thách.
- Produces:
  - `cham_mot_ca(hoi_thoai: str, ra_mo_hinh: list[dict], dap_an: list[dict]) -> dict`, gồm các khóa `trich_bia` (câu trích không có nguyên văn trong lượt dẫn), `trich_sai_luot`, `trich_dung_nhung_sai_nguoi`, `dan_thanh_da_lam` (lời dặn có điều kiện bị ghi thành sự việc), `tong`.
  - Báo cáo `docs/ket-qua/doi-chung-trich-dan.md` so sánh "mô hình thương mại + dặn ghi nguồn" với "MediTrace" trên cùng 60 ca.

- [ ] **Step 1: Viết test chấm** với 3 đầu ra giả: một câu trích bịa, một câu trích đúng nhưng gán bệnh nhân cho câu "Bố em bị hen", một câu "Đã chụp phim" từ câu "Nếu mai còn sốt thì chụp phim". Mỗi đầu ra phải được đếm đúng vào khóa của nó.
- [ ] **Step 2: Chạy test, phải FAIL**
- [ ] **Step 3: Cài đặt** phần chấm và lời nhắc: *"viết hồ sơ; mỗi dòng ghi số lượt và câu trích NGUYÊN VĂN"*. Phần gọi API tái dùng `doi-chung-thuong-mai.py`, ghi vào thư mục riêng.
- [ ] **Step 4: Chạy test, phải PASS**
- [ ] **Step 5: DỪNG và hỏi người dùng.** Kiểm số dư API, ước tính chi phí (60 ca × số token), báo con số rồi chờ đồng ý. Chỉ chạy khi có "đồng ý" trong chat.
- [ ] **Step 6: Chạy đo, viết báo cáo MT6, commit** — `git commit -m "feat(tools): doi chung AI thuong mai co dan ghi nguon, do MT6"`

---

### Task 7: Bộ nhãn người 40 ca và kiểm định bộ chấm tự động

**Files:**
- Create: `tools/phieu_gan_nhan_nguoi.py`, `src/do_luong/dong_thuan_nhan.py`
- Test: `tests/test_dong_thuan_nhan.py`

**Interfaces:**
- Produces:
  - `xuat_phieu(tap: str, so_ca: int, ra: Path) -> Path`: tạo tệp HTML tự chứa. Người gán nhãn đánh dấu từng mệnh đề của MediTrace là `dung` / `sai_nguoi` / `sai_noi_dung` / `khong_co_can_cu`, và ghi thêm các thông tin bị bỏ sót. Kết quả xuất ra JSON. Chọn ca bằng seed `2711` từ `viet_phat_trien_v2`.
  - `nap_nhan(tep_json: Path) -> list[dict]`
  - `cohen_kappa(a: list[str], b: list[str]) -> float`
  - `dong_thuan(nhan_nguoi, nhan_may) -> dict` trả về kappa theo từng nhãn, ma trận nhầm, và tỷ lệ bỏ sót theo người so với theo máy.

- [ ] **Step 1: Viết test** `cohen_kappa(["a","a","b","b"], ["a","a","b","b"]) == 1.0`, kappa khi ngẫu nhiên bằng 0 (ví dụ tự tính bằng tay); `dong_thuan` đếm đúng ma trận nhầm 2×2.
- [ ] **Step 2: Chạy test, phải FAIL** → **Step 3: Cài đặt** → **Step 4: Chạy test, phải PASS**
- [ ] **Step 5: Xuất phiếu 40 ca, giao cho người dùng.** Việc gán nhãn do người làm, tốt nhất là một sinh viên y hoặc bác sĩ. Không được tự gán nhãn hay giả lập nhãn người. Khi có tệp JSON trả về, chạy `dong_thuan` → `docs/ket-qua/nhan-nguoi-40-ca.md` (MT7).
- [ ] **Step 6: Commit** công cụ trước; commit kết quả sau khi có nhãn.

---

### Task 8: Trích theo cửa sổ trong lúc đang ghi âm (tốc độ)

**Files:**
- Create: `src/duong_ong/b1_trich_cuon.py`
- Modify: `src/he_thong/dich_vu_http.py` (thêm `POST /api/trich-cuon/:phien`), `web/may-chu/hang-doi.ts` (xếp việc trích cuốn), `web/src/App.tsx` (gửi lượt mới mỗi khi đủ cửa sổ)
- Test: `tests/test_trich_cuon.py`

**Interfaces:**
- Consumes: `chay_trung_gian` (ở chế độ một ca), `cac_doan`.
- Produces:
  - `class TrichCuon`, khởi tạo với `(kich_thuoc_cua_so: int = 6, chong_lan: int = 2)`. Có các phương thức:
    - `them_luot(luot: dict) -> list[dict] | None`: trả mệnh đề của cửa sổ vừa đủ, hoặc `None` khi chưa đủ.
    - `ket_thuc() -> list[dict]`: trích phần còn lại.
    - `tat_ca() -> list[dict]`: gộp các mệnh đề và bỏ trùng theo `(bang_chung, trich_dan)`.
  - Mỗi mệnh đề giữ số lượt tuyệt đối, không dùng số lượt trong cửa sổ.
  - Bước 2–5 chỉ chạy một lần trên `tat_ca()`, vì đính chính và chủ thể cần toàn ca.

- [ ] **Step 1: Viết test** với hàm trích giả (stub), không cần GPU:
  - 14 lượt, cửa sổ 6, chồng lấn 2 → gọi trích 3 lần trong khi ghi và 1 lần khi kết thúc.
  - Số lượt trong mệnh đề là số tuyệt đối.
  - Mệnh đề ở vùng chồng lấn không bị đếm hai lần.
  - Gọi `ket_thuc()` khi đang dở cửa sổ (Review Focus 5) vẫn trả về toàn bộ mệnh đề đã có.
- [ ] **Step 2: Chạy test, phải FAIL** → **Step 3: Cài đặt** → **Step 4: Chạy test, phải PASS**
- [ ] **Step 5: Đo MT8 trên HoaiĐức**: 10 ca dài, tính thời gian từ `ket_thuc()` đến khi có bản nháp. Đo đồng thời tỷ lệ bỏ sót của trích cuốn so với trích cả ca trên cùng 10 ca; chênh lệch phải ghi vào báo cáo `docs/ket-qua/trich-cuon-toc-do.md`.
- [ ] **Step 6: Commit** — `git commit -m "feat: trich cuon theo cua so trong luc ghi am, do MT8"`

---

### Task 9: Đo thời gian duyệt của bác sĩ (chỉ lưu tại chỗ)

**Files:**
- Create: `web/src/lib/doThoiGianDuyet.ts`, `web/src/lib/doThoiGianDuyet.test.ts`, `docs/giao-thuc-thu-nghiem-nguoi-dung.md`
- Modify: `web/src/App.tsx` (gọi `batDau` khi mở ca, `ghiThaoTac` khi giữ/sửa/bỏ/nghe lại, `ketThuc` khi ký), `web/may-chu/routes/sign-off.ts` (lưu bản tóm tắt cùng bản ký)

**Interfaces:**
- Produces: `taoDoThoiGian(now: () => number)` trả về `{ batDau(), ghiThaoTac(loai: "giu"|"sua"|"bo"|"nghe_lai"|"xem_can_cu"), ketThuc(): TomTatDuyet }`, trong đó `TomTatDuyet = { tongMs: number; soThaoTac: Record<string, number>; soCanXacNhan: number }`. Hàm không chứa nội dung hội thoại hay tên người bệnh và không gửi ra ngoài.

- [ ] **Step 1: Viết test** với đồng hồ giả: bắt đầu ở 0, 3 thao tác, kết thúc ở 42000 → `tongMs === 42000`, đếm đúng từng loại; gọi `ketThuc` hai lần thì lần sau trả cùng kết quả.
- [ ] **Step 2: Chạy test, phải FAIL** → **Step 3: Cài đặt** → **Step 4: Chạy `npx tsx --test src/lib/doThoiGianDuyet.test.ts`, phải PASS**
- [ ] **Step 5: Viết giao thức thử nghiệm**: 5 người dùng, mỗi người 3 ca mẫu, so thời gian ghi tay với thời gian duyệt bản nháp. Phiếu đồng ý và cách tuyển người do người dùng thực hiện. MT9 chỉ báo cáo khi đã có dữ liệu thật.
- [ ] **Step 6: Commit** — `git commit -m "feat(web): do thoi gian duyet tai cho + giao thuc thu nghiem"`

---

### Task 10: Quy trình duyệt bảng tri thức thuốc có người chịu trách nhiệm

**Files:**
- Create: `tools/duyet_tri_thuc.py`
- Modify: `src/cong_cu_lam_sang/tri_thuc_thuoc.py` (kiểm tính hợp lệ khi nạp)
- Test: `tests/test_duyet_tri_thuc.py`

**Interfaces:**
- Produces:
  - `duyet_muc(duong_dan: Path, ma_muc: str, duyet_boi: str, chuc_danh: str, ghi_chu: str = "") -> dict`. Hàm ghi `da_duyet=True`, `duyet_boi`, `chuc_danh`, `ngay_duyet` (ISO) và nối một dòng vào `data/tri_thuc_thuoc.duyet.jsonl`.
  - `nap_tri_thuc()` báo lỗi `ValueError` khi gặp mục `da_duyet=True` mà thiếu `duyet_boi` hoặc thiếu `ngay_duyet`.

- [ ] **Step 1: Viết test** cho 3 trường hợp:
  - `duyet_muc` với `duyet_boi=""` → `ValueError`.
  - Mục `da_duyet=True` không có `duyet_boi` → `nap_tri_thuc` báo lỗi.
  - Duyệt hợp lệ → nhật ký thêm đúng 1 dòng.
- [ ] **Step 2: Chạy test, phải FAIL** → **Step 3: Cài đặt** → **Step 4: Chạy test, phải PASS**
- [ ] **Step 5: Không tự duyệt mục nào.** Xuất `docs/tri-thuc-thuoc-can-duyet.md` (cập nhật tệp đã có) làm phiếu cho dược sĩ hoặc bác sĩ.
- [ ] **Step 6: Commit** — `git commit -m "feat: quy trinh duyet tri thuc thuoc co nguoi chiu trach nhiem"`

---

### Task 11: Bật các chốt mới trong sản phẩm (chỉ những chốt đạt mục tiêu)

**Files:**
- Modify: `src/he_thong/dich_vu_http.py` (cờ `quet_lai`, cổng ASR, hai nguồn chủ thể, ngân sách), `web/src/components/VerificationView.tsx` (nhãn "từ quét lại" cho mệnh đề `nguon == "quet_lai"`)
- Test: `tests/test_dich_vu.py` (thêm ca)

**Interfaces:**
- Consumes: kết quả MT1–MT5 trong `docs/ket-qua/`.
- Produces: cấu hình `CHOT_BAT = {"quet_lai": bool, "cong_asr": bool, "chu_the_hai_nguon": bool, "ngan_sach": int}`. Chốt nào không đạt mục tiêu đã đăng ký thì để `False` và ghi lý do vào báo cáo.

- [ ] **Step 1: Viết test**: `GET /api/sample-cases?bo=demo_bgk`, cả 3 ca mẫu vẫn cho đúng kết quả đã nêu trong `BAO_CAO_CAI_TIEN_CHANG_1.md` §2.2. Mệnh đề quét lại hiện nhãn và vẫn bị K1–K6 chặn khi sai.
- [ ] **Step 2: Chạy test, phải FAIL** → **Step 3: Cài đặt** → **Step 4: `pytest tests/ -q` và `cd web && npm run lint && npm test && npm run build`, tất cả phải PASS**
- [ ] **Step 5: Commit**

---

### Task 12: Đo tập kín một lần, cập nhật tài liệu, triển khai

**Files:**
- Create: `docs/ket-qua/tap-kin-27-11.md`
- Modify: `README.md` (bảng "Kết quả đo", nhật ký nâng cấp, mục "Những kết quả không có lợi"), `BAO_CAO_CAI_TIEN_CHANG_1.md`, `Q_AND_A_BAN_GIAM_KHAO.md`, `docs/bao-cao-cai-tien/*`

- [ ] **Step 1: Kiểm tập kín chưa bị mở**: so vân tay `data/viet_kiem_tra_cuoi_v2.van_tay.json` bằng `src/bo_du_lieu/van_tay_bo.py`. Expected: khớp.
- [ ] **Step 2: Chạy đường ống đã khóa trên `viet_kiem_tra_cuoi_v2` đúng MỘT lần.** Ghi bỏ sót, lỗi nguy hiểm lọt vào thân, gán sai người, cảnh báo hiển thị trên ca sạch, kèm khoảng Wilson. Ghi lệnh chạy và giờ chạy.
- [ ] **Step 3: Cập nhật README, báo cáo cải tiến và Q&A**, mỗi con số kèm đường dẫn tới tệp kết quả. Mục tiêu không đạt ghi vào "Những kết quả không có lợi".
- [ ] **Step 4: Hồi quy toàn bộ** — `PYTHONUTF8=1 pytest tests/ -q` và `cd web && npm test && npm run build`. Expected: 0 thất bại, ngoài các lỗi môi trường đã biết.
- [ ] **Step 5: Commit và push** (push cần người dùng đồng ý).
- [ ] **Step 6: Triển khai lên HoaiĐức theo quy trình cũ**: sao lưu vào `du-phong-<ngày>`, thử trên bản thử cổng 3198 với DB riêng, rồi `doi-dist.ps1` giữ tài sản cũ, khởi động lại dịch vụ 8765/3100. Kiểm Worker trả 200 và mở thử ca mẫu.

---

## Thứ tự và phụ thuộc

- **Task 0** phải làm trước mọi phép đo.
- **Task 1 → Task 2**: Task 2 dùng `ve_chua_phu` của Task 1.
- **Task 3, 4, 5** độc lập với nhau, nhưng cùng sửa `b5_xep_cho_cong_rui_ro.py` (Task 3, 4), nên làm lần lượt.
- **Task 6, 7, 9, 10** độc lập, có thể làm song song. Task 6 cần người dùng đồng ý chi phí; Task 7 và Task 9 cần người thật tham gia.
- **Task 8** độc lập về mã, nhưng đo trên GPU nên không chạy cùng lúc với đo của Task 1.
- **Task 11** phải chờ Task 1–5. **Task 12** phải chờ tất cả.

## Phần cần người dùng làm, không tự động hóa được

1. Đồng ý chi phí API trước khi chạy Task 6.
2. Tìm người gán nhãn 40 ca cho Task 7.
3. Tìm 5 người thử và lấy phiếu đồng ý cho Task 9.
4. Tìm dược sĩ hoặc bác sĩ duyệt bảng tri thức cho Task 10.
5. Đồng ý push và triển khai ở Task 12.
