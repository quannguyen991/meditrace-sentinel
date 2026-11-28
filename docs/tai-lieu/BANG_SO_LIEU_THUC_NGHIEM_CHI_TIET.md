# TẬP HỒ SƠ THỰC NGHIỆM & CÁC BẢNG ĐỐI CHỨNG

**Dự án:** MediTrace Sentinel — Trợ lý Lâm sàng Có căn cứ & Phòng vệ An toàn Y khoa  
**Lưu ý đọc bảng (sửa lại 28/11/2026 theo `docs/doi-chieu-so-lieu-bao-cao.md`):**  
- Mọi con số trong tệp này đều có tệp đo đi kèm (ghi ở cột hoặc dòng "Nguồn"). Số nào chưa đo được ghi **"chưa đo"**.
- Bản thuyết minh tháng 10/2026 có một số bảng số liệu không có lần chạy nào đi kèm (bảng nhánh A → D với 12,4% → 2,1%, bảng so sánh GPT-4o/Gemini/Claude/Llama, bảng chống nhiễu âm thanh, bảng ngoài khuôn, bảng 10 bác sĩ). Các bảng đó đã được **gỡ bỏ** ở bản này. Danh sách đầy đủ: [`docs/doi-chieu-so-lieu-bao-cao.md`](../doi-chieu-so-lieu-bao-cao.md).
- Toàn bộ kết quả là **trên dữ liệu mô phỏng** do dự án tự sinh, so với **bộ chấm tự động**, chưa có nhãn của người và chưa thử trên hội thoại thật.

---

## MỤC LỤC

1. [BẢNG 1: So sánh các nhánh của đường ống (đã đo)](#bang-1)
2. [BẢNG 2: So sánh với mô hình thương mại (chưa chạy đầy đủ)](#bang-2)
3. [BẢNG 3: Nhận dạng giọng nói (ASR)](#bang-3)
4. [BẢNG 4: Dữ liệu, bỏ sót và lớp cảnh báo (đã đo)](#bang-4)
5. [BẢNG 5: Công cụ dược lý & thang điểm CDSS (phép thử đơn vị)](#bang-5)
6. [BẢNG 6: Đánh giá với bác sĩ (chưa làm)](#bang-6)

---

<a name="bang-1"></a>
## BẢNG 1: SO SÁNH CÁC NHÁNH CỦA ĐƯỜNG ỐNG

### 1.1. Câu hỏi
Mỗi bước phía sau phần rút thông tin (xử lý lời sửa, kiểm tra bằng chứng) giúp được bao nhiêu, và có chỗ nào không giúp?

### 1.2. Bảng số liệu (300 ca thử thách tạo theo cặp, không phải 5.000 ca)
Nguồn: `docs/final/Báo cáo dự án.md` mục 4.1–4.3, `README.md` mục "Kết quả đo". Mỗi ô: F1 / tỷ lệ lỗi theo ô (SER) / tỷ lệ ghi nhầm người.

| Bộ thử thách | Chỉ tách thông tin (B) | Tách + xử lý lời sửa (C) | + kiểm tra bằng chứng (C_khoá) |
| :--- | :---: | :---: | :---: |
| Đổi chủ thể (80 ca) | 66,1 / 45,4 / 22,0% | 69,2 / 38,2 / 20,0% | **70,8 / 36,9 / 17,9%** |
| Đính chính (60 ca) | 80,9 / 29,9 / 7,6% | 85,9 / 17,4 / 6,8% | **87,0 / 17,4 / 5,5%** |
| Nhiễu giọng nói (80 ca) | 63,2 / 63,7 / 3,7% | 64,9 / 58,4 / 3,3% | 64,8 / 58,6 / 3,5% |
| Vùng miền (80 ca) | 85,8 / 21,5 / 1,7% | 87,8 / 16,9 / 1,5% | 88,0 / 16,3 / 1,5% |

| Chỉ số khác | Trước | Sau | Nguồn |
| :--- | :---: | :---: | :--- |
| Thông tin đã bị sửa nhưng vẫn còn trong bản nháp (bộ đính chính 60 ca) | 11,48% | **0,80%** | `README.md`, Báo cáo dự án mục 4.2 |
| Cùng chỉ số, mẫu 240 ca tập phát triển | 5,21% | 0,36% | Báo cáo dự án mục 4.2 |
| Lỗi nghiêm trọng, bộ đổi chủ thể (thêm kiểm tra bằng chứng) | 43,0% | 36,2% | Báo cáo dự án mục 4.3 |
| Bỏ sót, bộ đổi chủ thể (thêm kiểm tra bằng chứng) | 4,5% | **7,7% (tăng)** | Báo cáo dự án mục 4.3 |

**Nhánh A (mô hình viết thẳng bản nháp):** ghi đúng người **cao hơn** đường ống ở cả bốn bộ thử thách, ví dụ **0,939 so với 0,748** ở bộ đổi chủ thể (`README.md`, "Những kết quả không có lợi"). Một phần do nhánh A chép giống bản mẫu ở 30–63% số ca; phần còn lại là thật (ghi đúng người 97,1% so với 88,3%). Dự án **không** khẳng định MediTrace chính xác hơn cách viết thẳng; điểm mạnh là kiểm tra được từng dòng.

**Nhánh D (bác sĩ xác nhận):** **chưa đo**. Chưa từng chạy với bác sĩ thật.

### 1.3. Đọc bảng
* Ở bộ đổi chủ thể, các bước phía sau giảm ghi nhầm người từ 22,0% xuống 17,9% và tăng F1 từ 66,1 lên 70,8. Đây là cải thiện có thật nhưng vừa phải, không phải "triệt tiêu".
* Ở bộ nhiễu giọng nói, thêm kiểm tra bằng chứng gần như không giúp (F1 64,9 → 64,8).
* Kiểm tra bằng chứng giảm lỗi nghiêm trọng nhưng **tăng bỏ sót**. Đây là một sự đánh đổi.
* **Chặn nhầm 0 trên 30.136 dòng** là số đo thật, nhưng chỉ đúng vì đáp án mô phỏng chép gần nguyên văn hội thoại (độ phủ 0,95; ghi chú ở `src/bo_du_lieu/dan_gian.py`). Trên đầu ra mô hình thật, chặn thừa là **8,0%** (chính sách C) và **10,0%** (chính sách D) (`docs/ket-qua/canh-bao.json`).
* Lỗi nguy hiểm vẫn lọt vào phần chính: **11,8%** với chính sách D, đo trên các tập **phát triển** đã dùng để chỉnh luật nên là số lạc quan (`docs/ket-qua/canh-bao.json`).

---

<a name="bang-2"></a>
## BẢNG 2: SO SÁNH VỚI MÔ HÌNH THƯƠNG MẠI

**Chưa chạy so sánh đầy đủ với mô hình thương mại.** Bảng GPT-4o / Gemini 1.5 Pro / Claude 3.5 Sonnet / Llama-3-8B và chi phí API trong bản cũ không có lần chạy nào đi kèm nên đã bị gỡ.

Phép đo duy nhất có thật (`docs/final/Báo cáo dự án.md` mục 4, `README.md`): một mô hình thương mại được thử với cùng lời nhắc trên 173/300 ca trước khi dừng do hết số dư.

| Bộ thử thách | Mô hình thương mại: ghi nhầm người | Mô hình nhỏ của dự án: ghi nhầm người |
| :--- | :---: | :---: |
| Đính chính ("tự sửa") | **1,4%** | 7,6% |
| Đổi chủ thể | **15,4%** | 22,9% |

Mô hình thương mại **tốt hơn** ở việc gán đúng người. Khi áp bước nhận người bằng luật lên mô hình thương mại, tỷ lệ ở bộ đổi chủ thể lại tăng từ 15,4% lên 25,2%. Điểm khác biệt của MediTrace là chạy ngay trên máy và kiểm được từng dòng, không phải chính xác hơn.

Kế hoạch đo đầy đủ: `docs/superpowers/plans/2026-11-27-nang-cap-toan-dien-bgk.md`, Task 6 (cần đồng ý chi phí API trước khi chạy).

**Về pháp lý:** từ 01/01/2026, dữ liệu cá nhân được điều chỉnh bởi Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định 356/2025/NĐ-CP (thay Nghị định 13/2023/NĐ-CP). Dự án không đánh giá việc dùng dịch vụ đám mây là đúng hay sai luật; dự án chạy tại chỗ nên dữ liệu người bệnh không cần rời phòng khám.

---

<a name="bang-3"></a>
## BẢNG 3: NHẬN DẠNG GIỌNG NÓI (ASR)

Bảng "500 đoạn âm thanh thu âm thực tế" trong bản cũ (WER 5,2%, nhận đúng tên thuốc 96,8%, "0,0% Zero Error"…) không có tệp đo nên đã bị gỡ. Dự án chưa thu âm thực tế tại bệnh viện.

Số có nguồn (`docs/BAN-GIAO-CONG-VIEC-DANG-DO.md`, thư mục `thi-nghiem/asr/`):

| Phép đo | Kết quả |
| :--- | :--- |
| Tinh chỉnh LoRA cho PhoWhisper trên VietMed | WER giảm 0,033 (khoảng 0,027–0,041, bootstrap theo câu) |
| Greedy → beam trên VietMed-500 | WER giảm 0,016; không áp dụng vì ViMedCSS không cải thiện |
| Rò rỉ dữ liệu | VietMed chung người nói/âm thanh/văn bản; ViMedCSS trùng video 93,8%, nên các số trên có thể lạc quan |

Tên thuốc dân gian (*a móc, ô mê*): có luật đưa sang mục "Cần xác nhận" thay vì tự sửa; **chưa đo** tỷ lệ trên tập độc lập.

---

<a name="bang-4"></a>
## BẢNG 4: DỮ LIỆU, BỎ SÓT VÀ LỚP CẢNH BÁO

### 4.1. Độ lặp câu và độ đa dạng từ vựng (Bộ v1 và bộ mở rộng v2 — 5.000 ca)
Đo bằng `src/do_luong/do_lap_cau.py` trên toàn bộ 5.000 ca:

| Chỉ số | Bộ cũ v1 (`mo_rong=False`) | Bộ mở rộng v2 (657 khuôn, seed 2611) | Thay đổi |
| :--- | :---: | :---: | :---: |
| **Số khuôn ca bệnh** | 200 khuôn | **657 khuôn (21 hệ cơ quan)** | +457 khuôn |
| **Tổng số lượt thoại** | 87.473 lượt | **87.097 lượt** | — |
| **Số câu khác nhau** | 20.190 câu | **45.835 câu** | +25.645 câu (+127,0%) |
| **Tỷ lệ lặp mọi câu** | 76,92% | **47,37%** | Giảm 29,55 điểm % |
| **Tỷ lệ lặp câu $\ge 8$ từ** | 69,60% | **42,19%** | Giảm 27,41 điểm % |
| **MTLD** | 93,0 | **145,4** | +56,3% |
| **Distinct-2** | 0,0188 | **0,0468** | +148,9% |
| **Trích dẫn khớp chuỗi con nguyên văn** | Không đo tự động | **52.634 / 52.634** | Kiểm **dữ liệu huấn luyện do dự án tự sinh**, không phải đầu ra mô hình. Trên đầu ra mô hình, lớp cảnh báo vẫn bắt câu trích bịa (`FABRICATED_QUOTE`) 17 lần. |
| **Lỗi ngữ pháp/hạt thừa (6 quy tắc)** | Chưa kiểm | **0 lỗi / 87.097 lượt** | Chỉ theo 6 quy tắc đã viết |

*Ghi chú:* Tỷ lệ lặp mọi câu dừng ở 47,37% do các lượt đáp ngắn của người bệnh ("của tôi ạ.", "vâng ạ."). Dự án không cắt gọt để làm đẹp chỉ số. Toàn bộ 5.000 ca gồm cả tập huấn luyện; không có "5.000 ca kiểm tra độc lập".

### 4.2. Tỷ lệ bỏ sót mệnh đề lâm sàng (30 ca phát triển)
Đo bằng `tools/do_bo_sot_tren_tap.py` trên 30 ca đầu tập phát triển, **so với bộ chấm tự động, đáp án v1** (304 mệnh đề, khoảng tin cậy Wilson 95%):

| Mô hình | Số mệnh đề đáp án | Bị bỏ sót | Tỷ lệ bỏ sót | Khoảng tin cậy 95% | Ca JSON lỗi |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Qwen3-4B chưa huấn luyện** | 304 | 131 | **43,1%** | 37,6% – 48,7% | 0 / 30 |
| **Qwen3-4B + adapter (best_checkpoint)** | 304 | 35 | **11,5%** | 8,4% – 15,6% | 0 / 30 |
| Lần chạy 26/11/2026: adapter v1 / adapter v3 | 304 | — | 11,8% / 14,1% | 8,7–16,0% / 10,7–18,5% | — |

Adapter v3 không tốt hơn v1. 30 ca là mẫu nhỏ.

### 4.3. Lớp cảnh báo đo bằng cấy lỗi & độc lập Train–Test (25–26/11/2026)
Đo bằng `src/do_luong/do_cay_loi.py` (`docs/ket-qua/cay-loi.md`) và `src/do_luong/kiem_nghiem_ngoai_khuon.py`. Cấy lỗi là đo khả năng bắt lỗi do chương trình tạo ra, **không phải** độ chính xác trên hồ sơ thật.

| Phép đo | Tập / quy mô | Kết quả | Nguồn |
| :--- | :---: | :---: | :--- |
| **Bắt đúng loại, 16 loại lỗi cơ bản (tập điều chỉnh)** | 400 ca (`viet_train_v2`) | 0,801 → **0,871** (báo nhầm 8,98 → 7,11 cảnh báo/ca sạch) | `docs/ket-qua/cay-loi.md` |
| **Bắt đúng loại, 16 loại lỗi cơ bản (tập giữ kín, chạy 1 lần)** | 240 ca (`thach_thuc_v2`) | **0,871**, báo nhầm 8,0 cảnh báo/ca sạch | `docs/ket-qua/cay-loi.md` |
| **Bắt đúng loại, 14 loại lỗi khó (vòng 6)** | 400 ca (`viet_train_v2`) | 0,682 → **0,889** *(số lạc quan: luật vòng 6 chỉ đo trên tập điều chỉnh)* | `docs/ket-qua/cay-loi.md` |
| **Trùng lặp từ khóa triệu chứng Train – Test** | 515 khuôn Train × 70 khuôn Test | Giao tên khuôn = **0**; Jaccard TB = **0,0587** (`p95 = 0,1172`) | `src/do_luong/kiem_nghiem_ngoai_khuon.py` |
| **10 kịch bản bệnh hiếm ngoài kho 657 khuôn (chỉ tầng luật, không qua mô hình)** | 10 ca (`OOT_01..10`, 52 mệnh đề) | Đúng chủ thể **52/52**, chống nhầm người nhà **11/11**, bắt đính chính **10/10** | `src/do_luong/kiem_nghiem_ngoai_khuon.py` |
| **Thử ngoài nguồn (`ViMQ`)** | 200 câu người bệnh | Phủ thực thể **284/322 (88,2%)** | `docs/tien-do-21-11-2026.md` |

---

<a name="bang-5"></a>
## BẢNG 5: CÔNG CỤ DƯỢC LÝ & THANG ĐIỂM CDSS

Bảng "300 kịch bản" với độ nhạy/độ đặc hiệu (100,0%, 98,0%, 96,7%…) và thời gian phản hồi trong bản cũ không có tệp đo nên đã bị gỡ.

Hiện trạng có thật: các công cụ (trần liều Paracetamol, tương tác thuốc, chống chỉ định theo eGFR, CURB-65, CHA₂DS₂-VASc, HAS-BLED, Child-Pugh, tờ dặn dò) có **phép thử đơn vị** trong `tests/` với ca do nhóm tự viết, chạy qua cùng bộ `pytest` (`README.md`: 1.942 bài qua, 27 bỏ qua). Đây là kiểm tra mã tính đúng công thức, **không phải** tỷ lệ phát hiện trên bệnh nhân thật. Bảng tri thức đi kèm **chưa được dược sĩ/bác sĩ duyệt**. Chưa đo độ nhạy, độ đặc hiệu hay tỷ lệ báo động rác trên tập độc lập.

---

<a name="bang-6"></a>
## BẢNG 6: ĐÁNH GIÁ VỚI BÁC SĨ

**Chưa làm.** Dự án chưa có dữ liệu của bác sĩ nào dùng thử. Các con số trong bản cũ (thời gian làm bệnh án, tỷ lệ nhìn mắt người bệnh, SUS, giảm kiệt sức) không phải kết quả đo và đã bị gỡ.

Thiết kế dự kiến: bác sĩ làm cùng một bộ ca theo ba cách (gõ tay, dùng chatbot, dùng MediTrace), đo thời gian hoàn thành, số lỗi nguy cơ cao bỏ qua, và điểm SUS. Kế hoạch: `docs/superpowers/plans/2026-11-27-nang-cap-toan-dien-bgk.md` (Task 9, cần người thật tham gia và phiếu đồng ý).

---

## CÁC TỆP LIÊN QUAN
1. Hình bảng đối chứng (sinh bằng `tools/ve_bang_doi_chung_thuc_nghiem.py`): `docs/tai-lieu/hinh/bang-doi-chung-thuc-nghiem.png`
2. Hình so sánh với mô hình thương mại: `docs/tai-lieu/hinh/flow-5-so-sanh-doi-dau-chatgpt-vs-meditrace.png`
3. Hình đường ống kiểm thử: `docs/tai-lieu/hinh/flow-6-duong-ong-kiem-thu-thuc-nghiem-1330-test.png` (số bài kiểm thử theo `README.md`)
4. Bảng đối chiếu số liệu: `docs/doi-chieu-so-lieu-bao-cao.md`
