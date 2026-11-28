# Kịch bản nâng cấp MediTrace v2 (28/11/2026)

> **Cho người/agent thực thi:** dùng superpowers:executing-plans (khuyên dùng) hoặc superpowers:subagent-driven-development. Bước dạng checkbox `- [ ]`. Kế hoạch này **bổ sung và sắp lại thứ tự** [plan 27/11](2026-11-27-nang-cap-toan-dien-bgk.md); chi tiết từng bước của Task 1–12 nằm ở đó, ở đây chỉ ghi chỗ thay đổi.

**Mục tiêu:** Đóng các lỗ hổng làm BGK chưa thể tin con số của dự án, theo đúng thứ tự mắt xích lỗi, và chỉ tuyên bố những số đo trên dữ liệu chưa ai dùng để chỉnh luật.

**Spec:** `BAO_CAO_CAI_TIEN_CHANG_1.md`, `Q_AND_A_BAN_GIAM_KHAO.md`, `docs/ket-qua/*`, sổ thực thi `.superpowers/sdd/2026-11-25-cai-thien-bo-luat/progress.md`.

---

## 1. Chẩn đoán lại: lỗi nằm ở đâu, số nào đáng tin

Chuỗi xử lý: **ghi âm → chép lời (ASR) → tách người nói → Bước 1 trích mệnh đề → gom người/trạng thái → khóa căn cứ K1–K7 → cảnh báo + chính sách → bác sĩ duyệt → ký.**

| Mắt xích | Số đo hiện có | Đo trên cái gì | Độ tin |
|---|---|---|---|
| ASR (PhoWhisper-medium) | WER 0,204–0,237 (VietMed); thuật ngữ Anh nhận đúng 17–23% (ViMedCSS); sai tên thuốc "gần như mọi câu" (README) | giọng thật, nhưng không phải hội thoại khám | **Thật, nhưng chưa nối vào đường ống** |
| Tách người nói | chưa chạy thử với mô hình thật (README) | — | **Không có số** |
| Bước 1 trích | bỏ sót 11,5% (v1), 14,1% (v3) | 30 ca dev, chữ sạch, bộ sinh của dự án | Thấp: tập dev, mô phỏng |
| Khóa K1–K7 | trích khớp nguyên văn 100% | đúng theo cấu trúc (ràng buộc cây chuỗi con) | Cao nhưng **không chứng minh nội dung đúng** |
| Cảnh báo + chính sách D | lọt nguy hiểm 11,8%; báo 7–8 lần/ca sạch; độ phủ bỏ sót 12,5%, chính xác 2,8% | 4 tập dev đã chỉnh luật nhiều vòng | **Thiên lạc quan** |
| Giao diện, bác sĩ | không có | — | **Không có số** |
| Bảng thuốc | 0/158 mục có người duyệt | — | — |

### Năm phát hiện

- **F1. Mắt xích yếu nhất lại ít được đo nhất.** Mọi con số từ Bước 1 trở đi đo trên chữ sạch hoặc chữ nhiễu mô phỏng (`nhieu_asr.py`). Chưa có một ca nào chạy từ âm thanh đến bản nháp. Nên "lọt 11,8%" không nói gì về buổi khám thật.
- **F2. Phép đo bị nhiễm.** Luật được viết và chỉnh qua 6 vòng (25–26/11) rồi thêm đợt 27/11 trên cùng 4 tập `thach_thuc/*_phat_trien`. Tập kín 240 ca v2 đã dùng một lần. Chưa có tập mù thứ ba mà người viết luật chưa thấy.
- **F3. Sót nằm ở vế, không ở lượt.** 86% mệnh đề bị sót nằm trong lượt đã có mệnh đề khác (sổ 25/11). Huấn luyện thêm không giúp (v3 không hơn v1) và DPO làm log-prob câu đúng tụt từ −1,38 xuống −4,90, nên hướng huấn luyện không phải đường ngắn nhất. Đường ngắn: quét lại những vế chưa được trích.
- **F4. Báo nhầm giết niềm tin.** Cứ 8 mệnh đề sót thì 7 không có cảnh báo, và 97% cảnh báo bỏ sót là nhầm. Có mã báo hàng trăm lần mà độ chính xác cùng loại bằng 0 (`IMPORTANT_MODIFIER_DROPPED` 84 lần, `SPEAKER_SUBJECT_MISMATCH` 382 lần chỉ 5,8%).
- **F5. Không có người trong vòng đo.** Nhãn người 0, bác sĩ 0, thời gian duyệt 0, người thử bắt lỗi cấy 0. Đây là điều BGK hỏi cuối cùng và thêm luật không trả lời được.

Ngoài ra: nhiều phiên cùng sửa một repo (ví dụ đợt 27/11 làm lệch bản đồ tài liệu và 3 lỗi phải sửa lại). Cần **cổng hồi quy cứng** trước khi sửa tiếp.

---

## 2. Sáu nguyên tắc của v2

1. **Đo trước, sửa sau, mốc 0 đóng băng.** Mỗi cải tiến có mục tiêu đăng ký và commit trước khi đo.
2. **Đi từ đầu chuỗi:** âm thanh trước, luật sau. Sửa luật khi đầu vào còn sai tên thuốc là tối ưu nhầm chỗ.
3. **Hai loại số, không trộn:** số *phát triển* (dùng để chỉnh) và số *mù* (đo một lần sau khi khóa luật). Tài liệu nộp chỉ trích số mù khi nói về khả năng tổng quát.
4. **Không thêm tính năng mới** trước khi F1–F2 được đóng. Phần lớn "tính năng đột phá" trong báo cáo 21/11 đã có sẵn dấu vết trong mã (xem mục 4).
5. **Trung thực khi không đạt:** ghi đúng số, ghi lý do, không đổi ngưỡng sau khi đo.
6. **Người thật không thay được bằng máy:** nhãn, duyệt thuốc, thử người dùng chỉ do người làm; máy chỉ chuẩn bị phiếu và đo.

---

## 3. Bộ mục tiêu đăng ký trước (MT)

MT1–MT9 giữ nguyên như plan 27/11. Thêm:

| Mã | Chỉ số | Tập đo | Ngưỡng |
|---|---|---|---|
| MT10 | Tên thuốc ASR nhận đúng, có hotwords so với không | ViMedCSS-test (323 câu) + 20 ca giọng thật (V6) | tăng ≥ **15 điểm** tuyệt đối, báo cáo khoảng tin cậy |
| MT11 | Lỗi nguy hiểm lọt vào thân, **từ âm thanh đến bản nháp** | 20 ca giọng thật (V6), chính sách D | chỉ báo cáo (số đầu tiên của loại này) |
| MT12 | Gán vai đúng trên giọng thật, phần còn lại thành "chưa rõ" | 20 ca V6 | ≥ 90% đúng hoặc "chưa rõ", sai cứng ≤ 3% |
| MT13 | Người thử bắt được lỗi nguy hiểm cấy sẵn (automation bias) | 10 ca × 2 lỗi, ≥ 5 người | chỉ báo cáo |
| MT14 | Hồi quy: 3 ca demo BGK và toàn bộ test | `ca_mau_bgk.py` + pytest | 0 thay đổi, 0 lỗi |

**Giao thức tập mù:**

- *Mù A:* `bo_gpt500` (bộ sinh khác hẳn, "chỉ để đo"). Điều kiện: trước khi dùng phải kiểm lịch sử git và nhật ký để chắc luật chưa từng chỉnh theo nó. Nếu đã chỉnh thì hạ xuống thành tập dev.
- *Mù B:* 20 ca giọng thật do đội đọc (V6), sinh sau khi khóa luật.
- *Mù C (đã niêm phong):* `viet_kiem_tra_cuoi_v2`, chỉ mở một lần ở V15.
- Mốc khóa luật = commit của V12. Sau đó **không sửa luật**, chỉ đo.

---

## 4. Đối chiếu báo cáo nghiên cứu 21/11: lấy gì, bỏ gì

Báo cáo ghi số liệu cũ (1.331 test) và đường dẫn tệp đã đổi. Các tuyên bố chưa được kiểm; **giấy phép phải tự đối chiếu trước khi dùng** (báo cáo tự nhận đã sửa 5 chỗ sai của bản trước, nên bản này cũng cần kiểm).

| Gợi ý | Quyết định | Lý do |
|---|---|---|
| Contextual biasing tên thuốc | **Làm, nhưng đo trước (V4)** | Đã nối `hotwords` và `LogitsProcessor` trong `phowhisper_provider.py` nhưng chưa có số tên thuốc trước/sau. Không thêm cơ chế mới khi chưa biết cơ chế cũ hiệu quả thế nào |
| Cờ bất định ASR + hiệu chuẩn conformal | **Làm (V5)** | Khớp Task 3. Cho phép nói "lỗi ≤ α trên tập hiệu chuẩn" thay vì đặt ngưỡng cảm tính |
| Tách người nói không cần token (Sherpa-ONNX) | **Có điều kiện (V7)** | Chỉ làm nếu pyannote không chạy nổi trên máy phòng khám hoặc vai sai > ngưỡng MT12. Tránh thay mô hình khi chưa có số |
| XGrammar | **Bỏ** | Đã có GBNF + cây chuỗi con (`b1_ep_dau_ra_json.py`); JSON lỗi = 0 ca trên 30 ca dev. Không có vấn đề để giải |
| RLVR/GRPO/DAPO | **Hoãn sang pha F** | Hàm thưởng đã có (`ham_thuong_rlvr.py`). Huấn luyện tốn GPU và rủi ro "ăn gian hàm thưởng"; DPO vừa cho kết quả mâu thuẫn |
| Chunked loss, QLoRA 4096 | **Đã có** (`loss_theo_doan.py`) | Không làm lại |
| 5 bẫy đối kháng (tự sửa, họ hàng, điều kiện, nhầm liều ×10, nói đè) | **Làm (V13), dạng test** | Rẻ, chạm đúng điểm BGK hỏi. Bẫy 5 (nói đè) cần âm thanh nên gộp vào V6 |
| Thử nghiệm chéo 8–10 bác sĩ, PDQI-9, NASA-TLX | **Thu nhỏ (V14)** | Cần IRB và bác sĩ; trước mắt thử 5+ người, đo thời gian duyệt và bắt lỗi cấy |
| 7 tính năng UX (duyệt theo ngoại lệ, nghe 3 giây, SBAR, FHIR, so lần khám, WORM) | **Phần lớn đã có dấu vết** | Có `VerificationView.tsx`, `DuyetBenCanh.tsx`, `SbarModal.tsx`, `xuat_fhir_r4.py`, `doiChieuLanKham.ts`, `nhat_ky_ky_duyet_worm.py`. *Chưa kiểm hành vi từng cái.* Chỉ thêm khi V14 cho thấy bác sĩ cần |
| Tờ dặn dò bình dân, macro thoại, cầu nối EMR | **Không làm bây giờ** | Mở rộng phạm vi khi lỗ hổng đo lường chưa đóng |
| DPIA Nghị định 13, chữ ký số PKCS#11 | **Pha F, song song, do người** | Hồ sơ pháp lý, không chặn đo |

---

## 5. Lộ trình theo pha

**Pha 0 (làm trước, BTC giao đề 28/11):** [Đề cải tiến 1 — làm chủ và bảo vệ dữ liệu sức khỏe](2026-11-28-de-cai-tien-1-du-lieu-suc-khoe.md), các việc P1–P8.

```
Pha 0  Đề cải tiến 1 (BTC)      trước tiên   P1–P8
Pha A  Đóng băng & đo thật      ngày 1–2     V1 V2 V3
Pha B  Sửa lỗi từ nguồn         ngày 3–10    V4 V5 V6 V7 | V8 V9 V10
Pha C  Giảm báo nhầm, khóa luật ngày 11–14   V11 V12
Pha D  Người & dữ liệu thật     chạy nền từ ngày 1   V13 V14 V15(duyệt thuốc) V16(thương mại)
Pha E  Đo mù, công bố           ngày 15–18   V17 V18
Pha F  Sau thi/hạ tầng          không chặn   RLVR, Sherpa, DPIA, ký số, thử lâm sàng
```

**Đường ngắn (nếu chỉ có ~1 tuần):** V1, V2, V3, V8, V9, V10, V11, V12, rồi V6 chỉ với 10 ca. Bỏ V4/V5/V7 và nói thẳng "âm thanh chưa đo hết".

Phụ thuộc: V1→mọi việc; V3→V17; V4→V5; V6→V7, V13(nhãn), V17; V8→V9; V10 tuần tự sau V5 (cùng sửa `b5_xep_cho_cong_rui_ro.py`); V11→V12→V17. V13, V14, V15, V16 chạy song song, không chặn.

### Pha A: đóng băng và đo thật

#### V1. Mốc 0 và ba ca demo bất biến

**Files:** Create `tests/test_ca_demo_bat_bien.py`, `tests/golden/ca_demo_bgk.json`; Create `tools/chup_ca_demo.py`.
**Interfaces:** Consumes `danh_sach_ca_demo()`, `doc_ca_demo(ca_id)` trong `src/bo_du_lieu/ca_mau_bgk.py`. Produces: tệp golden cho 3 ca (`demo_bs_nguoi_nha_nhi`, `demo_hai_benh_nhan`, `demo_lao_khoa_con_gai`).

- [ ] **Step 1:** Viết `tools/chup_ca_demo.py` ghi JSON của 3 ca (khóa sắp xếp, `ensure_ascii=False`) ra `tests/golden/ca_demo_bgk.json`. Chạy ở commit hiện tại (`0d94d03`).
- [ ] **Step 2 (test):** `test_ba_ca_demo_khong_doi` so từng ca với golden, `assert hien_tai == golden`; `test_co_dung_ba_ca` kiểm đúng 3 mã ca.
- [ ] **Step 3:** `pytest tests/test_ca_demo_bat_bien.py -v` → PASS. Sửa một ký tự trong ca mẫu → test FAIL (xác nhận test bắt được), rồi hoàn lại.
- [ ] **Step 4:** `git tag moc0-28-11` tại commit mốc; chép các tệp `docs/ket-qua/*.json` quan trọng vào `docs/ket-qua/moc0-28-11/` để so sánh sau này.
- [ ] **Step 5: Commit** `test: dong bang ba ca demo BGK va moc 0 28/11`

Lý do: hôm 27/11 mình phải so ba ca bằng tay; test này biến việc đó thành tự động.

#### V2. Đăng ký trước MT1–MT14

Làm như Task 0 plan 27/11 nhưng tệp là `docs/dang-ky-truoc-nang-cap-28-11.md`, đủ 14 dòng, kèm giao thức tập mù (mục 3). Test `tests/test_dang_ky_truoc_28_11.py` kiểm có `| MT1 |` … `| MT14 |` và cụm "chỉ đo một lần". Commit **trước mọi phép đo**.

#### V3. Kiểm kê tập đo: ai đã nhìn tập nào

**Files:** Create `docs/kiem-ke-tap-do.md`, `tools/kiem_ke_tap_do.py`, `tests/test_kiem_ke_tap_do.py`.

- [ ] **Step 1 (test):** `test_van_tay_khop` đọc `data/*.van_tay.json` và kiểm tệp `.jsonl` tương ứng còn đúng vân tay; `test_tap_kin_khong_doi` kiểm `viet_kiem_tra_cuoi.jsonl` và `viet_kiem_tra_cuoi_v2.jsonl` còn nguyên vân tay.
- [ ] **Step 2:** Tool in bảng: tập, số ca, vân tay, **ai/lúc nào đã dùng** (lấy từ `git log -- <tệp>` và nhật ký sổ thực thi), vai trò (`dev` / `mù` / `niêm phong`).
- [ ] **Step 3:** Với `bo_gpt500`: tìm trong lịch sử git mọi commit sửa `b0_chuan_hoa_phuong_ngu.py`, `phuong_ngu.py`, `phat_hien.py` có nhắc gpt500. Nếu có commit chỉnh luật theo nó thì ghi "dev", ngược lại ghi "mù A".
- [ ] **Step 4:** `pytest tests/test_kiem_ke_tap_do.py -v` → PASS. Commit.

### Pha B: sửa lỗi từ nguồn

#### V4. Đo tên thuốc ở tầng ASR (có và không hotwords)

**Files:** Create `tools/do_asr_thuoc.py`, `tests/test_do_asr_thuoc.py`; reuse `src/audio/asr/bench_metrics.py`, `contextual_trie_600.py`.
**Interfaces:** Produces `ty_le_thuoc_dung(ref: str, hyp: str, ds_thuoc: set[str]) -> tuple[int,int]` (số đúng, số tổng) và báo cáo `docs/ket-qua/asr-thuoc.md`.

- [ ] **Step 1 (test):** `ty_le_thuoc_dung("uống amoxicillin 500", "uống a móc xi lin 500", {"amoxicillin"}) == (0, 1)`; `ty_le_thuoc_dung("uống amoxicillin", "uống Amoxicillin", {"amoxicillin"}) == (1, 1)` (không phân biệt hoa thường, bỏ dấu câu).
- [ ] **Step 2:** FAIL → cài đặt, PASS.
- [ ] **Step 3 (đo, GPU HoaiĐức, `--phan-vram 0.70`):** chạy PhoWhisper-medium trên ViMedCSS-test shard0 hai lần: `hotwords=None` và `hotwords=trie.xuat_hotwords()`. Ghi tỷ lệ thuốc đúng, WER, khoảng tin cậy bootstrap theo câu (tái dùng `thi-nghiem/asr/so_sanh_bootstrap.py`).
- [ ] **Step 4:** Đối chiếu MT10. **Nếu không đạt:** thử `prompt_hotwords` rút gọn theo hệ cơ quan (`xuat_hotwords(he_co_quan=...)`), rồi mới xét cơ chế khác (TCPGen). Ghi mọi thử nghiệm, kể cả thất bại.
- [ ] **Step 5:** Commit kết quả và báo cáo.

#### V5. Cổng ASR có hiệu chuẩn (Task 3 + conformal)

Làm theo Task 3 plan 27/11 (`b5_cong_asr.py`, `can_qua_cong_asr(p, meta_asr, nguong)`), thêm bước chọn ngưỡng:

- [ ] **Step 1 (test):** `test_chon_nguong_dam_bao_loi` — cho 100 mẫu hiệu chuẩn có độ tin cậy và nhãn "sai", hàm `chon_nguong(mau, alpha=0.05)` trả ngưỡng nhỏ nhất sao cho tỷ lệ lỗi lọt trong tập hiệu chuẩn ≤ alpha (công thức có hiệu chỉnh `(n+1)`). Kiểm bằng dữ liệu tổng hợp biết trước đáp án.
- [ ] **Step 2:** Lấy dữ liệu hiệu chuẩn từ `thach_thuc_nhieu_asr_phat_trien` (đã có `meta_asr`); **không** dùng tập mù để chọn ngưỡng.
- [ ] **Step 3:** Đo MT3 (≤ 15% lọt, chặn thừa ≤ 8%) trên 4 tập dev. Nếu chặn thừa vượt 8% mà lọt chưa đạt: ưu tiên giữ chặn thừa, báo cáo thẳng không đạt.
- [ ] **Commit** theo Task 3.

#### V6. Thu giọng thật: số đo đầu–cuối đầu tiên

Mục đích: lần đầu có số **từ âm thanh đến bản nháp**, và ba thứ chưa từng đo (tên thuốc trong hội thoại, tách người nói, nói đè).

**Files:** Create `tools/ghi_am_kich_ban.py` (in kịch bản để đọc), `tools/chay_dau_cuoi_am_thanh.py`, `docs/ket-qua/dau-cuoi-am-thanh.md`; Test `tests/test_chay_dau_cuoi_am_thanh.py`.
**Interfaces:** Consumes `src/audio/pipeline.py` (một phiên: ghi âm → lời thoại), `src/audio/adapter.py` (lời thoại đã duyệt → hội thoại), `chay_trung_gian`, `gop.chay`. Produces `chay_mot_ca(wav_path, ca_goc) -> dict{wer, thuoc_dung, vai_dung, loi_nguy_hiem_lot, ban_nhap}`.

- [ ] **Step 1 (người làm):** chọn 20 ca từ `bo_gpt500` hoặc ca mới viết sau khi khóa luật (không lấy từ tập dev); mỗi ca 2–3 người đọc (bác sĩ, bệnh nhân, người nhà) bằng micro laptop, thêm 5 ca có chen ngang/tiếng ồn nền. **Máy không đọc thay.**
- [ ] **Step 2 (test):** `chay_mot_ca` với `wav` giả (hoặc tệp ngắn có sẵn) và hội thoại gốc trả đủ khóa; `test_khong_tu_duyet`: `da_duyet` luôn `False` ở đầu ra.
- [ ] **Step 3 (đo):** chạy 20 ca qua toàn bộ đường ống (≈ 3,5 phút/ca trên RTX 3060, tổng khoảng 70 phút). Ghi WER, tên thuốc đúng, vai đúng, lọt nguy hiểm (MT11), so với đáp án gốc của ca.
- [ ] **Step 4:** Báo cáo thẳng: số có thể rất xấu, đó chính là phát hiện. Không chỉnh luật theo 20 ca này nếu còn dùng làm tập mù B; nếu cần chỉnh, ghi rõ và hạ xuống thành dev, rồi thu thêm 20 ca mới.
- [ ] **Commit** báo cáo + mã (không commit âm thanh có giọng người thật khi chưa có đồng ý ghi bằng văn bản của người đọc).

#### V7. Tách người nói chạy thật

- [ ] **Step 1 (đo):** trên âm thanh V6, chạy `pyannote_provider.py` (tiến trình con, môi trường riêng, giới hạn RAM) và đo MT12: tỷ lệ lượt gán vai đúng, đúng/chưa rõ/sai cứng.
- [ ] **Step 2:** Nếu pyannote không chạy (thiếu token, xung đột môi trường) hoặc sai cứng > 3%: mới thử Sherpa-ONNX; trước tiên đọc giấy phép trực tiếp từ kho chính thức của từng mô hình, không dựa báo cáo 21/11.
- [ ] **Step 3:** Khi độ tin vai < ngưỡng thì giữ nhãn "chưa rõ" và hiện nút gán vai (kiểm `web/src/lib/nguoiNoi.ts` đã có gì, không làm lại).
- [ ] **Commit.**

#### V8–V9. Nhóm bỏ sót

Làm đúng Task 1 (quét lại vế, MT1 ≤ 8%) rồi Task 2 (cảnh báo theo vế, MT2 phủ ≥ 40%, chính xác ≥ 10%). Thêm một ràng buộc rút từ F3:

- [ ] Test bổ sung `test_quet_lai_khong_tao_menh_de_ngoai_van`: mọi mệnh đề sinh từ quét lại đều có `trich_dan` là chuỗi con của lượt dẫn (K1). Mệnh đề không qua K1–K6 chỉ vào `CẦN XÁC NHẬN`.
- [ ] Đo MT1 cả trên `bo_gpt500` (mù A nếu hợp lệ) để biết vế "quét lại" có tổng quát không, nhưng chỉ ghi vào cột mù sau mốc khóa V12.

#### V10. Gán người hai nguồn + lỗi "bố em" đã biết

Làm Task 4 (`chu_the_theo_luat`, MT4 ≤ 4%). Thêm mục tiêu riêng: sửa lỗi README ghi ("bố em" bị gộp vào người bệnh).

- [ ] **Step 1 (test):** `test_bo_em_la_nguoi_khac`: lượt người nhà "Bố em dị ứng penicillin" với mô hình gán `chu_the_id=0` phải bị hạ về `CẦN XÁC NHẬN` (hai nguồn không đồng ý); khi người nhà nói "Bố em" **và** bác sĩ đã hỏi về "ông/bác" thì không hạ (ca người nhà trả lời hộ bệnh nhân là bình thường).
- [ ] **Step 2:** Kiểm `FAMILY_PATIENT_MIXUP` không bắn trên ca người nhà trả lời hộ nếu lượt bác sĩ trước đó nhắm đúng bệnh nhân. Đo ảnh hưởng tới số cảnh báo/ca (nhắm giảm).
- [ ] **Commit.**

### Pha C: giảm báo nhầm, khóa luật

#### V11. Ngân sách cảnh báo và dọn mã vô dụng

Task 5 (`chon_hien_thi(ds, ngan_sach=2)`) cộng thêm bước dọn mã:

- [ ] **Step 1:** Lập bảng từ `docs/ket-qua/canh-bao.json`: mã nào báo ≥ 20 lần mà độ chính xác cùng loại < 0,10 **và** không thuộc `LUON_CAO`/`LOI_PHAT_HIEN`.
- [ ] **Step 2 (test):** `test_ma_vo_dung_xuong_goi_y`: các mã này có mức `THAP` và không đưa vào hàng chặn của chính sách D; mã `LUON_CAO` không bao giờ bị hạ (`test_luon_cao_khong_ha`).
- [ ] **Step 3 (đo):** độ nhạy của cảnh báo hiển thị (MT5 ≥ 0,85) và số cảnh báo/ca sạch (≤ 2,0) trước và sau, trên 400 ca cấy lỗi. Ghi cả độ nhạy từng loại lỗi nguy hiểm, không chỉ trung bình.
- [ ] **Commit.**

#### V12. Khóa luật và cờ sản phẩm

Task 11 như plan 27/11, cộng:

- [ ] `pytest -q` toàn bộ + `tests/test_ca_demo_bat_bien.py` (MT14) trước và sau khi bật từng cờ `CHOT_BAT`.
- [ ] Chỉ bật cờ đạt mục tiêu ở dev. Commit riêng mang nhãn `luat-khoa-<ngày>`, đây là **mốc khóa luật**: từ đây không sửa luật nữa.

### Pha D: người và dữ liệu thật (chạy nền)

#### V13. Bẫy đối kháng thành bộ test, cộng nhãn người

- [ ] **Step 1 (test, máy làm):** `tests/test_bay_doi_khang.py` — 20 ca chữ, 4 nhóm: (1) tự sửa "à nhầm, mới 2 hôm nay" chỉ giữ "2 ngày", mốc cũ `bi_thay_the`; (2) "Mẹ cháu bị hen, còn cháu viêm mũi dị ứng": hen → gia đình, viêm mũi → bệnh sử; (3) "nếu sốt trên 38 độ rưỡi thì uống" không vào thuốc cố định; (4) "amlodipin năm mươi miligam" (liều trần 10 mg/ngày) vào `CẦN XÁC NHẬN`. Mỗi ca assert vị trí cuối cùng của mệnh đề, không assert tên mã cảnh báo.
- [ ] **Step 2:** Bẫy nào FAIL thì ghi vào danh sách lỗi thật, không sửa trong task này. Báo số bẫy qua/20.
- [ ] **Step 3 (Task 7, người làm):** `tools/phieu_gan_nhan_nguoi.py` xuất 40 phiếu = 20 ca V6 + 20 ca `bo_gpt500`; **hai người gán độc lập**, mù với đầu ra máy; `cohen_kappa ≥ 0,6` (MT7). Máy không bao giờ điền nhãn.

#### V14. Thử người dùng thu nhỏ (thay thử nghiệm chéo)

Dùng Task 9 (`doThoiGianDuyet.ts`) và thêm:

- [ ] `docs/giao-thuc-thu-nghiem-nguoi-dung.md`: ≥ 5 người; mỗi người duyệt 10 ca, trong đó 2 ca/lượt có **2 lỗi nguy hiểm cấy sẵn** (liều ×10, gán nhầm họ hàng) mà người thử không biết.
- [ ] Đo: trung vị thời gian duyệt (MT9), tỷ lệ lỗi cấy bị bắt (MT13), có bấm "duyệt tất cả" không. Báo cáo cả nếu tỷ lệ bắt thấp: đó là bằng chứng về nguy cơ phụ thuộc máy, hợp pháp để trình bày như một giới hạn.
- [ ] Ngưỡng đạo đức: người thử là người lớn tự nguyện; dữ liệu mô phỏng; không dùng hồ sơ thật.

#### V15. Duyệt bảng thuốc có tên người chịu trách nhiệm

Task 10. Ưu tiên: duyệt trước **30 thuốc dùng nhiều nhất và 20 thuốc khoảng điều trị hẹp** (warfarin, digoxin, insulin, methotrexat…). Người duyệt là dược sĩ hoặc bác sĩ **thật**; máy không đặt `da_duyet=true`. Nếu chưa có người trong thời gian này, ghi rõ trong tài liệu nộp: "bảng thuốc chưa được duyệt".

#### V16. Đối chứng với AI thương mại

Task 6. Trước khi chạy: kiểm số dư, ước tính chi phí, **hỏi người dùng**. Chỉ dùng để đo, không đưa vào sản phẩm. Câu hỏi đo: với cùng lời nhắc "hãy ghi nguồn", mô hình thương mại bịa bao nhiêu câu trích, dẫn sai lượt bao nhiêu, đúng câu nhưng sai người bao nhiêu (MT6).

#### V17′. Tốc độ (Task 8)

Làm sau Pha C. Lưu ý trung thực: bác sĩ cho biết thời gian ghi hồ sơ chủ yếu ở việc hỏi bệnh, nên tài liệu **không hứa** giảm thời gian làm hồ sơ; MT8 chỉ nói về độ trễ từ lúc dừng ghi đến lúc có bản nháp.

### Pha E: đo mù và công bố

#### V17. Đo mù một lần

- [ ] **Step 1:** Kiểm vân tay mọi tập mù trước khi đo (V3). Sai một tập thì dừng.
- [ ] **Step 2:** Chạy trên mù A (`bo_gpt500` nếu hợp lệ), mù B (20 ca giọng thật), rồi mù C (`viet_kiem_tra_cuoi_v2`). **Mỗi tập một lần.** Ghi vào `docs/ket-qua/do-mu-<ngày>.md`, cột *dev* và cột *mù* cạnh nhau.
- [ ] **Step 3:** Mọi số trong README/báo cáo về "khả năng tổng quát" lấy từ cột mù. Số dev ghi rõ nhãn "dev".

#### V18. Cập nhật tài liệu và triển khai

- [ ] README, `BAO_CAO_CAI_TIEN_CHANG_1.md`, `Q_AND_A_BAN_GIAM_KHAO.md`, cẩm nang, rồi xuất lại Word/PDF (`tools/tao_cam_nang_giai_thich_va_qna_word.py`).
- [ ] Bản ghi nhận hiện hành (mục 8 bên dưới).
- [ ] Rà soát độc lập bằng một agent đọc toàn bộ diff từ `moc0-28-11` (một agent, dùng mô hình mạnh nhất).
- [ ] Push chỉ khi người dùng đồng ý. Triển khai theo quy trình HoaiĐức (sao lưu, chạy thử cổng 3198, đổi `dist`), **không khởi động lại máy**.

---

## 6. Kịch bản rủi ro

| Nếu… | Thì… |
|---|---|
| V4 cho thấy hotwords không tăng tên thuốc ≥ 15 điểm | Thử hotwords theo hệ cơ quan, rồi TCPGen; nếu vẫn không đạt, tài liệu nói thẳng "ASR sai tên thuốc; hệ thống bắt bằng cổng ASR (V5) thay vì sửa ASR" |
| V6 cho MT11 rất cao (lọt nhiều) | Đó là kết quả. Chuyển trọng tâm sang V5 (cổng ASR) và chính sách D; **không** chỉnh luật theo 20 ca rồi vẫn gọi là mù |
| MT1 (sót ≤ 8%) không đạt | Giữ quét lại ở dạng *cảnh báo* (V9) thay vì mệnh đề; ghi số thật |
| MT5: độ nhạy hiển thị < 0,85 khi ép ≤ 2 cảnh báo | Nới ngân sách lên 3, ghi đánh đổi; không hạ ngưỡng độ nhạy |
| Không có người gán nhãn/dược sĩ/người thử | Bỏ V13 (nhãn), V14, V15; tài liệu ghi từng mục "chưa làm" và lý do. Không thay bằng nhãn máy |
| Máy GPU HoaiĐức không sẵn | V4, V6, V17 dời; làm trước các phần chỉ cần CPU (V1, V2, V3, V9–V13) |
| Một phiên khác sửa cùng tệp | `git status` trước khi sửa; V1 bắt hồi quy; chỉ `git add` tệp của task |

## 7. Việc chỉ người làm được

1. Đọc to và ghi âm 20 ca (V6) và đồng ý bằng văn bản cho dùng giọng (V6).
2. Hai người gán nhãn 40 ca độc lập (V13).
3. Ít nhất 5 người thử duyệt (V14).
4. Dược sĩ/bác sĩ duyệt bảng thuốc (V15).
5. Đồng ý chi phí API thương mại (V16), đồng ý push/triển khai (V18).
6. IRB, DPIA, chữ ký số (pha F).

## 8. Điều được và không được nói với BGK sau nâng cấp

**Được nói** (khi đã có số): "lần đầu đo từ âm thanh đến bản nháp trên 20 ca giọng thật, kết quả X"; "số mù khác số dev thế này, vì sao"; "đây là chỗ hệ thống vẫn sai: tên thuốc ở tầng ASR, tách người nói"; "bảng thuốc chưa được duyệt" (nếu vậy).

**Không được nói:** "an toàn", "giảm thời gian làm hồ sơ", "chạy trên bệnh nhân thật", "AI khác không có trích dẫn" (Abridge có bằng chứng liên kết), mọi số dev như số tổng quát, và bảng so GPT-4o/Gemini/Claude khi chưa có lần chạy nào (`docs/doi-chieu-so-lieu-bao-cao.md` cảnh báo điều này).

---

## Self-review

- **Phủ yêu cầu BGK:** sót (V8–V9), kiểm soát lỗi giữa các bước (V5, V6, V10), độc lập dữ liệu (V3, mù A/B/C), thương mại (V16), con người (V13–V15), tốc độ (V17′).
- **Nhất quán tên:** `chu_the_theo_luat`, `can_qua_cong_asr`, `chon_hien_thi`, `ve_chua_phu` trùng plan 27/11; tên mới `ty_le_thuoc_dung`, `chay_mot_ca`, `chon_nguong` chỉ định nghĩa một lần ở V4, V6, V5.
- **Chưa kiểm:** các tên phiên bản/giấy phép mô hình trong báo cáo 21/11; hành vi từng màn UI; lịch sử dùng `bo_gpt500` (V3 sẽ kiểm); khả năng ghi âm 20 ca đúng lịch.
