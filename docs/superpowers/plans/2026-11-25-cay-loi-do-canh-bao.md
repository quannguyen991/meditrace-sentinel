# Cấy lỗi để đo và cải thiện lớp cảnh báo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đo lớp cảnh báo mà không cần người gán nhãn: cấy lỗi có chủ đích vào bản ghi đúng (đáp án) rồi đếm
cảnh báo bắt được bao nhiêu lỗi đã cấy (độ nhạy) và báo nhầm bao nhiêu trên bản ghi sạch. Dùng một tập lớn để
sửa luật, đo **một lần** trên tập giữ kín.

**Architecture:** `tools/cay_loi.py` biến danh sách `PhatBieu` hoàn hảo (`danh_gia_khoa.phat_bieu_tu_dap_an`)
thành bản có đúng một lỗi đã biết vị trí và loại. `src/do_cay_loi.py` chạy `canh_bao.gop.chay` trên bản sạch và
bản cấy, tính độ nhạy theo loại lỗi, báo nhầm trên mỗi ca sạch, và precision trong lượt cấy. Không mô hình,
không GPU, không nhãn người.

**Tech Stack:** Python 3.11 (venv `D:/khkt-venv-lap`), pytest, mã sẵn có (`danh_gia_khoa`, `canh_bao.gop`,
`tri_thuc_thuoc`).

**Spec:** `docs/dang-ky-truoc-bo-luat.md` (bản đăng ký trước, có mục sửa đổi 25/11) và plan mẹ
`docs/superpowers/plans/2026-11-25-cai-thien-bo-luat.md` (Task 1.2 đã bỏ — plan này thay phần đo của nó).

## Global Constraints

- Tập điều chỉnh: 400 ca rút từ `data/viet_train_v2.jsonl`, hạt 42. Tập giữ kín: **đáp án** 240 ca của
  `data/thach_thuc_v2/` (khuôn tập phát triển, không trùng khuôn với tập train). Tập giữ kín chỉ chạy **một lần**,
  sau khi khoá luật. Không mở `viet_kiem_tra_cuoi*`.
- Không dùng mô hình ngôn ngữ thương mại ở bất kỳ khâu nào. Không cần GPU.
- Mọi con số ghi "trên lỗi cấy nhân tạo", không viết "độ chính xác thực tế".
- Không đổi chính sách mặc định C; không đặt `da_duyet=true`; không commit khi người dùng chưa đồng ý.
- Mỗi lần sửa luật: phép thử đỏ → xanh; cả bộ phép thử xanh; lọt nguy hiểm trên `data/thach_thuc` (đầu ra mô
  hình cũ) không tăng; Jaccard bất biến dấu câu ≥ 0,85.
- Chạy với `PYTHONUTF8=1 PYTHONPATH=.`; bỏ qua `tests/test_loss_theo_doan.py` (torch không nạp được trên laptop).

## Danh mục lỗi cấy

Mỗi loại: điều kiện chọn mệnh đề, phép biến đổi, nhóm cảnh báo được tính là "bắt đúng loại".

| Loại | Chọn | Biến đổi | Nhóm đúng |
|---|---|---|---|
| `doi_chu_the` | vào thân | `chu_the_id` 0↔1 | SUBJECT_ATTRIBUTION |
| `dao_phu_dinh` | vào thân | đảo `phu_dinh`; thêm/bỏ "không " đầu `noi_dung` | NEGATION_ASSERTION |
| `nang_chac_chan` | `do_chac_chan` ≠ chắc chắn | → "chắc chắn" | NEGATION_ASSERTION |
| `gia_dinh_thanh_that` | `tinh_huong` ≠ thực tế | → "thực tế" | PLAN_FACT_CONDITIONAL |
| `ban_cu_con_hieu_luc` | `trang_thai` = bị thay thế | → còn hiệu lực | STATE_UPDATE |
| `doi_lieu` | có số + đơn vị liều trong `noi_dung`/`thuoc` | số × 10 | ENTITY_VALUE |
| `doi_so` | có số khác (nhiệt độ, ngày…) | số + 2 (giữ dạng) | ENTITY_VALUE, TEMPORAL |
| `doi_thuoc` | là dòng thuốc, có tên trong `tri_thuc_thuoc` | đổi sang hoạt chất khác cùng bảng | ENTITY_VALUE, UNSUPPORTED |
| `doi_thoi_gian` | có `moc_thoi_gian` | thay bằng mốc khác ("ba năm trước") | TEMPORAL, ENTITY_VALUE |
| `bia_menh_de` | — (thêm mới) | thêm dòng "dị ứng {thuốc}" hoặc "đang dùng {thuốc}" không có trong hội thoại, dẫn tới một lượt người bệnh | UNSUPPORTED, ENTITY_VALUE, EVIDENCE_PROVENANCE |
| `bia_trich_dan` | có `trich_dan` | trích đầu → câu không có trong lượt | EVIDENCE_PROVENANCE, UNSUPPORTED |
| `doi_bang_chung` | có `bang_chung` | dời sang một lượt bác sĩ không liên quan | EVIDENCE_PROVENANCE |
| `xoa_di_ung` / `xoa_thuoc` / `xoa_phu_dinh` / `xoa_so_lieu` | vào thân, đúng loại | xoá mệnh đề | OMISSION (cảnh báo toàn ca chạm lượt của nó) |

Không cấy được trên một ca (không có mệnh đề đủ điều kiện) thì bỏ ca đó cho loại đó và đếm `khong_ap_dung`.

## Chỉ số

- **Độ nhạy theo loại** = số lượt cấy có ≥ 1 cảnh báo thuộc nhóm đúng trên mệnh đề bị cấy (bỏ sót: cảnh báo
  toàn ca có lượt giao với lượt của mệnh đề bị xoá) / số lượt cấy. Báo kèm "bắt bất kỳ" (mọi nhóm) và khoảng
  Wilson 95%.
- **Báo nhầm trên bản sạch** = số cảnh báo / ca sạch, theo mã. Mọi cảnh báo trên bản sạch là báo nhầm vì đáp án
  được coi là đúng (giới hạn: đáp án có thể thiếu câu âm tính chung — ghi rõ).
- **Precision theo mã trong lượt cấy** = cảnh báo mã đó trên mệnh đề bị cấy và đúng nhóm / mọi cảnh báo mã đó
  trong các lượt cấy.
- **Chính sách D trên bản cấy:** tỉ lệ mệnh đề bị cấy rơi vào "cần xác nhận"; trên bản sạch: tỉ lệ chặn thừa.

## Review Focus

- Ca có nhiều lần nhắc cùng nội dung: cảnh báo rơi vào mệnh đề trùng chứ không phải mệnh đề bị cấy — phải tính
  theo `phat_bieu_id`, không theo nội dung.
- Mệnh đề bị xoá có lượt cũng được mệnh đề khác dẫn: không cảnh báo bỏ sót là hợp lý nếu lượt vẫn phủ — vẫn đếm
  lọt, nhưng báo riêng số "lượt còn được dẫn" để không đổ lỗi oan cho luật.
- Cấy sinh văn bản không tự nhiên ("không không đau") — phép biến đổi phải chuẩn hoá trước khi thêm/bỏ "không".
- Hạt ngẫu nhiên: cùng hạt → cùng kết quả byte-for-byte (để đăng ký trước có ý nghĩa).
- Sửa luật làm tăng độ nhạy trên tập điều chỉnh nhưng tăng báo nhầm trên bản sạch — mọi vòng sửa báo cả hai số.

---

### Task 1: Ghi sửa đổi vào bản đăng ký trước

**Files:** Modify: `docs/dang-ky-truoc-bo-luat.md` (mục "Sửa đổi sau khi đăng ký")

- [ ] Thêm mục "25/11/2026 — thêm phép đo cấy lỗi": tập điều chỉnh/giữ kín như Global Constraints, danh mục lỗi,
  bốn chỉ số, và ngưỡng khoá trước:
  - Một mã `thu_nghiem` chỉ lên `on_dinh` khi trên tập giữ kín: độ nhạy loại đích ≥ 0,5, precision trong lượt
    cấy ≥ 0,5, báo nhầm ≤ 0,05 cảnh báo/ca sạch.
  - Một vòng sửa luật được giữ khi trên tập điều chỉnh: độ nhạy trung bình các loại tăng và báo nhầm/ca sạch
    không tăng quá 0,02; kèm các ràng buộc trong Global Constraints.
  - Tối đa 5 vòng sửa; sau đó khoá luật và chạy tập giữ kín đúng một lần.
- [ ] Ghi SHA-256 của `data/viet_train_v2.jsonl` và danh sách id 400 ca điều chỉnh (tệp
  `data/cay_loi/tap_dieu_chinh_ids.json`).

### Task 2: Bộ cấy lỗi

**Files:** Create: `tools/cay_loi.py`; Test: `tests/test_cay_loi.py`

**Interfaces:**
- Produces: `LOAI_CAY: tuple[str, ...]` (đúng thứ tự bảng trên); `NHOM_DUNG: dict[str, set[str]]`;
  `@dataclass Cay(loai: str, phat_bieu_id: int | None, luot: list[int], mo_ta: str)`;
  `cay(ps: list[PhatBieu], ca: dict, loai: str, rng: random.Random) -> tuple[list[PhatBieu], Cay] | None`
  (bản sao mới, không sửa `ps`; `None` khi không áp dụng); `tap_dieu_chinh(n=400, seed=42) -> list[dict]`.

- [ ] Viết phép thử: mỗi loại có một ca nhỏ dựng tay trả đúng biến đổi (vd `doi_lieu` "amlodipin 5 mg" → "50 mg"
  và `thuoc["lieu"]` đổi theo); `ps` gốc không đổi; cùng hạt cùng kết quả; loại không áp dụng → `None`;
  `xoa_*` trả `phat_bieu_id` của mệnh đề đã xoá và `luot` của nó; `bia_menh_de` tạo id mới không trùng và thuốc
  không xuất hiện trong hội thoại; `dao_phu_dinh` không sinh "không không".
- [ ] Chạy thấy đỏ.
- [ ] Viết `tools/cay_loi.py`.
- [ ] Chạy thấy xanh: `pytest tests/test_cay_loi.py -q`.

### Task 3: Bộ đo

**Files:** Create: `src/do_cay_loi.py`; Test: `tests/test_do_cay_loi.py`

**Interfaces:**
- Consumes: `cay_loi.cay`, `cay_loi.LOAI_CAY`, `cay_loi.NHOM_DUNG`, `danh_gia_khoa.phat_bieu_tu_dap_an`,
  `canh_bao.gop.chay`.
- Produces: `do(ds: list[dict], loai=LOAI_CAY, seed=42) -> dict` với khoá `theo_loai` (mỗi loại:
  `so_lan, bat_dung_loai, bat_bat_ky, khong_ap_dung, luot_con_duoc_dan, wilson, d_can_xac_nhan`),
  `sach` (`so_ca, bao_nham_moi_ca, theo_ma, chan_thua_D`), `theo_ma_trong_cay` (precision theo mã),
  `do_nhay_trung_binh`; CLI `python -m src.do_cay_loi --tap dieu_chinh|giu_kin --ra-json PATH`.
  `--tap giu_kin` đòi cờ `--toi-da-khoa-luat` (chặn chạy nhầm).

- [ ] Phép thử: trên 3 ca dựng tay — bản sạch không lỗi → `bao_nham_moi_ca` tính đúng từ cảnh báo giả lập
  (monkeypatch `gop.chay`); `bat_dung_loai` chỉ đếm cảnh báo có `phat_bieu_id` của mệnh đề bị cấy và nhóm thuộc
  `NHOM_DUNG`; bỏ sót đếm theo giao lượt với `toan_ca`; cùng hạt cùng kết quả JSON.
- [ ] Đỏ → viết → xanh.

### Task 4: Đo mốc trên tập điều chỉnh

**Files:** Create: `docs/ket-qua/cay-loi-moc.json`, `docs/ket-qua/cay-loi.md`

- [ ] `python -m src.do_cay_loi --tap dieu_chinh --ra-json docs/ket-qua/cay-loi-moc.json`
- [ ] Viết `cay-loi.md`: bảng độ nhạy theo loại (đúng loại / bất kỳ / Wilson), báo nhầm theo mã trên bản sạch,
  precision theo mã, và 3 ví dụ lọt tiêu biểu mỗi loại có độ nhạy < 0,5.

### Task 5: Vòng sửa luật (tối đa 5 vòng)

**Files:** các tệp `src/canh_bao/*` và `src/khoa_bang_chung.py` mà vòng đó chạm; phép thử trong
`tests/test_cay_loi_vong.py`.

Mỗi vòng:
- [ ] Chọn loại có (độ nhạy thấp × mức nguy hiểm) lớn nhất, hoặc mã báo nhầm nhiều nhất trên bản sạch.
- [ ] Viết phép thử đỏ từ một ca lọt thật (ghi id ca).
- [ ] Sửa luật, nhỏ nhất có thể. Xanh.
- [ ] Cả bộ phép thử xanh; đo lại tập điều chỉnh; đo `src.do_canh_bao` trên `data/thach_thuc` (lọt nguy hiểm
  không tăng) và `tools.do_bat_bien_dau_cau` (Jaccard ≥ 0,85).
- [ ] Giữ vòng nếu đạt tiêu chí giữ của Task 1, không thì hoàn tác. Ghi một dòng vào bảng vòng trong
  `cay-loi.md` (vòng, sửa gì, độ nhạy TB trước/sau, báo nhầm/ca trước/sau, giữ hay hoàn tác).

### Task 6: Tập giữ kín — một lần

- [ ] Ghi vào sổ thực thi dòng "Khoá luật" kèm SHA-256 các tệp `src/canh_bao/*.py`, `src/khoa_bang_chung.py`.
- [ ] `python -m src.do_cay_loi --tap giu_kin --toi-da-khoa-luat --ra-json docs/ket-qua/cay-loi-giu-kin.json`
- [ ] Ghi kết quả vào `cay-loi.md` và bảng trong `docs/ket-qua/canh-bao-moc-0.md`; áp ngưỡng Task 1 cho từng mã
  `thu_nghiem` — chỉ ghi khuyến nghị, không tự đổi `tin_cay` trong `loai.py`.
- [ ] Cập nhật bộ nhớ dự án.

## Ngoài phạm vi

- Dùng lỗi cấy làm dữ liệu huấn luyện mô hình (dạy mô hình tự tránh lỗi): cần GPU và một lần train mới; ghi làm
  việc sau, không làm ở đây.
- Cấy lỗi lên đầu ra thật của mô hình (thay vì đáp án): làm được sau Giai đoạn 5, dùng cùng `cay_loi`.
