# Đối chiếu số liệu trong tài liệu báo cáo (25/11/2026)

Mục đích: tìm con số về lọt lỗi, chặn nhầm, bỏ sót trong `docs/tai-lieu/*.md` và `docs/final/*.md` mà không có
nguồn đo, hoặc trái với lần đo `docs/ket-qua/canh-bao-moc-0.md`. **Chưa sửa tài liệu nào** — bảng này để bạn duyệt.

Cách lấy: lọc các dòng có `%` và một trong các từ lọt, sai lệch, bỏ sót, bịa, chặn, ảo giác, precision, recall,
chính xác, F1 (71 dòng). Bỏ qua các dòng nhật ký lệnh và trích dẫn tài liệu ngoài (Palm 2025, Asgari 2025).

## Mức 1 — Trái với số đã đo hoặc không có nguồn: nên sửa trước khi nộp

| Tệp:dòng | Con số trong tài liệu | Nguồn đo | Số đúng thay thế |
|---|---|---|---|
| `docs/tai-lieu/BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md:55` | "Tỷ lệ sinh thông tin sai lệch 0,0% (K1–K7 ngăn chặn hoàn toàn)" | Không tìm thấy | Lỗi nguy hiểm lọt vào thân **45,2%** (C) / 43,3% (D), so với bộ chấm tự động, 4 bộ thử thách phát triển (`canh-bao-moc-0.md`). Không có số nào là 0%. |
| `…BANG_SO_LIEU…:55-59` | Cột GPT-4o 5,2%, Gemini 1.5 Pro 4,8%, Claude 3.5 Sonnet 3,9%, Llama-3-8B 8,4%; chi phí API | Không có tệp kết quả, lệnh gọi hay mã nào gọi các mô hình này trong `src/`, `tools/`, `docs/ket-qua/` | Xoá cả bảng 2.2, hoặc ghi rõ "chưa đo". Bảng so sánh với mô hình thương mại mà không có lần chạy là rủi ro liêm chính lớn nhất trong bộ tài liệu. |
| `…BANG_SO_LIEU…:57` | "Xử lý đính chính: 0,8% lọt lỗi" | Không tìm thấy | Không có phép đo riêng. Lớp cảnh báo có độ phủ `ban_cu` 81,9% cùng loại (`canh-bao-moc-0.md`), tức khoảng 18% lỗi đính chính không có cảnh báo cùng loại. |
| `…BANG_SO_LIEU…:58` | "Kiểm soát liều tối đa Paracetamol 0,0% bỏ sót" | Không tìm thấy | Không có tập đo. Ghi "có luật kiểm tra, chưa đo trên tập độc lập". |
| `…BANG_SO_LIEU…:27-35` | Bảng nhánh A → D: sai chủ thể 12,4% → 2,1%, đính chính 11,5% → 0,8%, giả định 14,8% → 0,4%, SER, F1 51,4 → 76,5, "đo trên 5.000 ca độc lập" | Chỉ có trong `tools/tao_word_bang_thuc_nghiem.py` (số gõ tay vào mã sinh Word) | Số có nguồn: ghi nhầm người 22,0% → 17,9%, F1 66,1 → 70,8 ở bộ đổi chủ thể 80 ca (`docs/final/Báo cáo dự án.md:278`). "5.000 ca độc lập" sai: 5.000 là toàn bộ dữ liệu, gồm cả tập huấn luyện. Nhánh D (bác sĩ xác nhận) chưa từng chạy với bác sĩ thật. |
| `…BANG_SO_LIEU…:42`, `GIAI_THICH_TOAN_DIEN…:206`, `SO_DO_FLOW…:60,114`, `Q_AND_A…:56` | "Chặn nhầm 0,0% (0 / 30.136 dòng)" | Có (`danh_gia_khoa.thong_ke_khoa`) | Số này **có thật nhưng bị hiểu sai**: `src/bo_du_lieu/dan_gian.py:4` ghi nó "chỉ đúng vì đáp án chép gần nguyên văn hội thoại (Coverage 0,95)". Trên đầu ra mô hình thật, chặn thừa là **8,0%** (C) / 6,1% (D). Phải ghi kèm điều kiện, hoặc thay bằng 8,0%. |
| `SO_DO_FLOW…:113`, `Q_AND_A…:56` | "Tỷ lệ bỏ sót dị ứng 0,0%" | Không tìm thấy | Chưa đo riêng. Lớp cảnh báo bỏ sót chung chỉ phủ **12,5%** mệnh đề bị sót, precision 2,8%. Mã nguồn còn lỗi che bỏ sót dị ứng (`kiem_duyet_bhyt_va_bo_sot.py:225`). |
| `…BANG_SO_LIEU…:126` | "Trích dẫn chuỗi con nguyên văn 100% (52.634 / 52.634), triệt tiêu 100% ảo giác trích dẫn" | Có (`docs/ket-qua/bao_cao_kiem_dinh_trich_dan_v2.json`) | Số đúng nhưng là kiểm **dữ liệu huấn luyện do mình sinh**, không phải đầu ra mô hình. Câu "triệt tiêu 100% ảo giác" phải bỏ: lớp cảnh báo vẫn bắt `FABRICATED_QUOTE` 17 lần trên đầu ra mô hình. |

## Mức 2 — Có nguồn nhưng cần ghi kèm điều kiện

| Tệp:dòng | Con số | Ghi chú |
|---|---|---|
| `…BANG_SO_LIEU…:134-138` | Bỏ sót 43,1% → 11,5% (30 ca phát triển, Wilson 95%) | Có nguồn (`tools/do_bo_sot_tren_tap.py`). Thêm: "so với bộ chấm tự động, 30 ca, đáp án v1". |
| `…BANG_SO_LIEU…:162`, `Báo cáo dự án.md:360-365`, `Bao_Cao_Nghien_Cuu…:316-317` | "Độ chính xác 96,7–100%", DDI Clopidogrel + Omeprazole 100%, eGFR sai số 0 | Là phép thử đơn vị với ca tự viết, không phải tỷ lệ trên dữ liệu thật. Nên viết "vượt qua N phép thử đơn vị" thay vì "%". |
| `Q_AND_A…:131` | 45.835 câu duy nhất, lặp giảm từ 76,92% | Số của bản v2 cũ. Bản v2 đã chấp nhận (phương án A) có tỷ lệ lặp **47,37%**; cần cập nhật theo `docs/tien-do-21-11-2026.md`. |

## Mức 3 — Khớp nguồn, giữ nguyên

`docs/final/Báo cáo dự án.md:278, 280, 299, 301, 316, 350, 352, 392` và các dòng tương ứng ở `docs/tai-lieu/Báo cáo dự án.md`:
có số đo cụ thể (22,0% → 17,9%; 15,06% → 12,52%; bỏ sót nghiêm trọng 0,58% → 3,48%), đã nêu cả mặt bất lợi
và câu "các tỷ lệ 100% đo khả năng bắt lỗi có chủ đích". Đây là văn phong nên dùng cho các tệp ở Mức 1.

## Nhận xét

- `docs/final/Báo cáo dự án.md` (bản nộp) khá trung thực. Các con số nói quá tập trung ở `docs/tai-lieu/`
  (bảng số liệu, Q&A ban giám khảo, sơ đồ flow) và các tệp `.docx` sinh từ đó. Nếu các tệp này sẽ đưa cho
  ban giám khảo, cần sửa Mức 1 trước.
- Các tệp `.docx` ở gốc repo và trong `docs/tai-lieu/` được sinh bằng `tools/tao_*.py`, trong đó số được gõ
  thẳng vào mã. Sửa `.md` mà không sửa mã sinh Word thì `.docx` vẫn giữ số cũ.

## Đã áp dụng (28/11/2026)

Nguồn số thay thế: `README.md` mục "Kết quả đo", `docs/final/Báo cáo dự án.md` mục 4.1–4.4, `docs/ket-qua/canh-bao.json`,
`docs/ket-qua/cay-loi.md`, `docs/ket-qua/da-nguon-doc-lap.json`. Số không có nguồn bị gỡ hoặc ghi "chưa đo".

### Tài liệu chữ

| Tệp | Đã sửa |
|---|---|
| `docs/tai-lieu/BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md` + bản ở gốc repo | Viết lại. Bảng 1: bỏ nhánh A/A+/B/C/C_KHOÁ/D bịa (12,4% → 2,1%, 11,5% → 0,8%, 14,8% → 0,4%, SER 68,2/31,2, F1 51,4 → 76,5, "5.000 ca độc lập", "an toàn tuyệt đối", "giảm 93%"); thay bằng bảng 3 phương án × 4 bộ đã đo, 11,48% → 0,80%, bỏ sót 4,5% → 7,7%, nhánh A ghi đúng người cao hơn (0,939 so với 0,748), nhánh D "chưa đo"; 0/30.136 kèm điều kiện (độ phủ 0,95; chặn thừa 8,0% C / 10,0% D); lọt lỗi nguy hiểm D 11,8% trên tập phát triển. Bảng 2: bỏ cột GPT-4o/Gemini/Claude/Llama, chi phí API, "0,0% ảo giác", "0,8% lọt", "Paracetamol 0,0% bỏ sót", "vi phạm Nghị định 13"; thay bằng phép đo duy nhất (173/300 ca: 1,4% so với 7,6%; 15,4% so với 22,9% — thương mại tốt hơn) và kế hoạch Task 6. Bảng 3 (ASR 500 đoạn) bỏ, thay bằng số VietMed có nguồn. Bảng 4 (ngoài khuôn 72,4/70,8/97,9…) bỏ. Bảng 5 bỏ % độ nhạy/đặc hiệu, ghi "phép thử đơn vị". Bảng 6 bỏ mọi số, giữ thiết kế. "Triệt tiêu 100% ảo giác trích dẫn" → kiểm dữ liệu tự sinh, `FABRICATED_QUOTE` 17 lần. |
| `docs/tai-lieu/Q_AND_A_BAN_GIAM_KHAO.md` + bản ở gốc | Câu 2: thêm phép đo thương mại 1,4%/7,6%, bỏ "vi phạm Nghị định 13" → Luật 91/2025/QH15 + NĐ 356/2025. 0/30.136 kèm điều kiện; 11,8% ghi "lạc quan"; 1.974/25 → 1.942/27 (README); F1 66,1 → 70,8 ghi rõ bộ đổi chủ thể + nhánh A 0,939/0,748; ViHealthQA "14/42" → 14 câu hỏi và 42 câu trả lời trên 2.013 mẫu; 52.634/52.634 ghi là kiểm dữ liệu tự sinh. |
| `docs/tai-lieu/SO_DO_FLOW_HE_THONG_MEDITRACE.md` | Bỏ 12,4% → 2,1% ("giảm 6 lần"), 11,5% → 0,8%, "0,0% chặn nhầm" không điều kiện, "bỏ sót dị ứng 0,0%" (→ chưa đo), 1.528/1.330 tests và các nhóm số test bịa (→ 1.942/27 + 96 TS), "30–45 giây" (→ ~3,5 phút RTX 3060), "20s/1s/<60 giây/5–7 phút" (→ chưa đo), NĐ 13. Thêm kết quả không có lợi (thương mại 1,4%/7,6%, nhánh A 0,939/0,748). |
| `docs/tai-lieu/GIAI_THICH_TOAN_DIEN_DU_AN_MEDITRACE_SENTINEL.md`, `GIAI_THICH_DU_AN_MEDITRACE_SENTINEL.md` | Thêm đoạn "bảng so sánh là thiết kế, không phải đo" + 1,4%/7,6%, 15,4%/22,9%, 0,939/0,748; 1.960+ → 1.942/27; ViHealthQA 14/42 sửa; 100% trích dẫn ghi là dữ liệu tự sinh; NĐ 13 → luật mới. |
| `docs/tai-lieu/CAM_NANG_KIEN_TRUC_MA_NGUON_VA_PHAN_BIEN_BGK_2026.md` | 1.960 → 1.942; "15–30 giây", "20 giây" duyệt → chưa đo; "15–25 giây/ca" → mục tiêu chưa đo; NĐ 13 → luật mới; ViHealthQA sửa; 52.634 kèm điều kiện; ảnh trỏ sang `so-do-flow-5-tang-meditrace.png`, `flow-3-khoa-bang-chung-k1-k7-chong-ao-giac.png`, `flow-4-duoc-ly-lam-sang-va-cdss-thang-diem.png`. |
| `docs/tai-lieu/HANDOVER.md`, `MINH_CHUNG_NANG_CAP_VA_LICH_SU_LENH.md`, `BANG_KE_KHAI_MA_NGUON_VA_LICH_SU_LENH.md` (+ bản ở gốc), `NHAT_KY_LOI_NHAC_VA_KHAI_MA_NGUON.md` (cả 2 bản), `docs/tai-lieu/Kê khai mã nguồn.md`, `docs/final/Kê khai mã nguồn.md` | NĐ 13 như luật hiện hành → Luật 91/2025/QH15 + NĐ 356/2025 hoặc bỏ; "1.330 (100% PASSED)" → ghi rõ là lần chạy 17/10 kèm 1.942/27 của 26/11; "1.779 test, 43 TS" → 1.942 + 96; "làm sạch 100%" bỏ chữ 100%. |
| `docs/final/Báo cáo dự án.md` | Mục 4.8: "1.330 … 100%" → lần chạy 18/10 + 26/11; "phát hiện chính xác 100%" DDI/eGFR, "sai số tuyệt đối bằng 0" → "vượt qua phép thử đơn vị, chưa đo trên tập độc lập"; "ẩn danh 100%, không rò rỉ" → phép thử đơn vị + PhoNER 10/847 (1,2%). NĐ 13 (6 chỗ) → luật mới. |
| `docs/GIOI-THIEU-DU-AN-MEDITRACE.md` | Ghi Bảng 2/Bảng 6 đã gỡ; "0,0% ảo giác" → không có phép đo (`FABRICATED_QUOTE` 17 lần); thêm số test 26/11. |
| `docs/HO_SO_DU_LIEU_DATASHEET.md`, `docs/HOI_DAP_BGK.md` | NĐ 13 → Luật 91/2025/QH15 + NĐ 356/2025, bỏ ý "vi phạm". |

### Mã sinh ảnh/Word và ảnh

Đã sửa số trong `tools/tao_word_bang_thuc_nghiem.py`, `ve_bang_doi_chung_thuc_nghiem.py`, `tao_bo_anh_flow_meditrace.py`,
`ve_so_do_flow_5_tang_meditrace.py`, `ve_so_do_so_sanh_nhanh.py`, `ve_so_do_tong_the_cac_tang.py`,
`ve_slide_problem_evidence_meditrace.py`, `tao_word_so_do_flow.py`, `tao_bao_cao_word_chi_tiet.py`,
`tao_bao_cao_nang_cap_word.py`, `tao_word_minh_chung_lenh.py`, và `tao_cam_nang_giai_thich_va_qna_word.py` (mã này cũng ghi
đè `CAM_NANG….md`, nên đã sửa cùng nội dung). Đã sinh lại và xem từng ảnh trong `docs/tai-lieu/hinh/`:
`bang-doi-chung-thuc-nghiem.png`, `so-do-so-sanh-cac-nhanh.png`, `so-do-flow-5-tang-meditrace.png` (+ `h1-duong-ong.png`),
`so-do-tong-the-cac-tang.png`, `slide-problem-evidence-meditrace.png`, 7 ảnh `flow-1…flow-7`. Ba ảnh không có mã sinh
(`flow-1-tong-the-5-tang-guardrails.png`, `flow-2-khoa-bang-chung-k1-k7.png`, `flow-3-an-toan-duoc-ly-cdss.png`) và ảnh
thừa `flow-4-so-sanh-doi-dau-chatgpt-vs-meditrace.png` được chép đè bằng ảnh đã sửa tương ứng.

### Đợt 2 (28/11/2026, chiều)

- Đã sửa 5 tệp ghi ở mục dưới (`BAO_CAO_CAI_TIEN_CHANG_1.md`, `Bao_Cao_Nghien_Cuu…md`, `docs/tai-lieu/Báo cáo dự án.md`,
  `tools/bo_sung_nckh_thang_10.py`, `tools/nang_cap_bao_cao_chuan.py`) theo mục 4.8 của bản nộp: NĐ 13 → Luật 91/2025/QH15 +
  NĐ 356/2025; "1.330 … 100%" → lần chạy 18/10 + 1.942/27 của 26/11; "chính xác 100%", "sai số tuyệt đối bằng 0" → phép thử
  đơn vị, chưa đo trên tập độc lập; ẩn danh 100% → PhoNER 10/847; 1.960+ → 1.942. Các tệp này còn thay đổi chưa commit của phiên
  khác (đổi tên Chốt 2/Chốt 7), nên chưa commit.
- `tools/tao_word_qna_giam_khao.py` (mã sinh Word bộ Q&A, chưa được sửa ở đợt 1): 1.974/25 → 1.942/27, 0/30.136 kèm điều kiện,
  11,8% ghi "lạc quan", Câu 2 thêm phép đo thương mại 1,4%/7,6% + luật mới, F1 66,1 → 70,8 ghi bộ đổi chủ thể + 0,939/0,748,
  ViHealthQA. `tao_cam_nang…py`: "phát hiện chính xác 100%" (WORM) → "4 phép thử". Đã sinh lại hai bộ Word này.
- Các `.docx` không còn mã sinh chạy được (thiếu tệp gốc ở Downloads) được thay chữ trực tiếp: `docs/final/Báo cáo dự án*.docx`,
  `Báo cáo nghiên cứu khoa học*.docx`, `Kê khai…`, `Nhật ký…`, và bản tương ứng ở `docs/tai-lieu/` + gốc repo. Bản trước khi sửa
  lưu ở `scratch/sao-luu-docx-28-11/`. Chỉ còn "nghị định 13" viết thường trong lời nhắc người dùng gõ (trích dẫn lịch sử, giữ
  nguyên) và câu "thay Nghị định 13/2023" (đúng).

### Chưa sửa được (đợt 1)

- 5 tệp do phiên khác đang sửa (đã sửa ở đợt 2): `BAO_CAO_CAI_TIEN_CHANG_1.md` (dòng 20: "100% trích dẫn chuỗi con" thiếu điều kiện dữ liệu
  tự sinh; dòng 241: "1.960+" khác README 1.942), `docs/tai-lieu/Bao_Cao_Nghien_Cuu_Khoa_Hoc_MediTrace_Sentinel.md`
  (dòng 21, 153, 167, 180, 319, 362: NĐ 13; 21, 316: "1.330 … 100%"; 317–319: "chính xác 100%" DDI/eGFR/ẩn danh),
  `docs/tai-lieu/Báo cáo dự án.md` (dòng 8, 203, 214, 227, 241, 251, 362, 392, 410: NĐ 13; 8, 359: "1.330 … 100%";
  360–362: "chính xác 100%"), `tools/bo_sung_nckh_thang_10.py` (191–193, 224, 241, 261, 301–307, 329) và
  `tools/nang_cap_bao_cao_chuan.py` (18, 205–207, 231, 246, 265, 316–322, 357, 372) — cùng các câu trên. Sửa theo
  mục 4.8 của `docs/final/Báo cáo dự án.md` bản mới.
- Nhật ký lệnh/lời nhắc (câu người dùng gõ "theo nghị định 13", thông điệp commit "1.330 automated tests", dòng nhật ký
  I2 "78.3%" ở `BANG_KE_KHAI…:125`, `NHAT_KY_MA_NGUON…:30`) giữ nguyên vì là trích dẫn lịch sử.
- Số liệu từ tài liệu ngoài trong `ve_slide_problem_evidence_meditrace.py` (70%, 18%/11,5%, 5,3%, 44%, 1,47%) chưa kiểm được
  với bài gốc. Các số "43/43 test TS", "< 10 ms" trong `CAM_NANG…` chưa đối chiếu với lần chạy.
- Tệp `.docx` đã nộp trong `docs/final/` và `docs/tai-lieu/` chưa sinh lại hết; chạy lại các mã `tools/tao_*.py` trước khi nộp.
