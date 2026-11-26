# HỒ SƠ DỮ LIỆU (DATASHEET FOR DATASET) — MEDITRACE SENTINEL
*(Biên soạn theo chuẩn quốc tế Gebru et al., "Datasheets for Datasets", Communications of the ACM — Phục vụ Câu hỏi số 3 của Ban Giám khảo)*

---

## 1. Động cơ & Mục đích Xây dựng (Motivation)
- **Mục đích:** Xây dựng bộ ngữ liệu hội thoại khám bệnh tiếng Việt có nhãn mệnh đề lâm sàng nguyên tử (`PhatBieu`) và trích dẫn nguyên văn hai chiều (`trich_dan`, `luot_thoai`) để huấn luyện và đánh giá hệ thống dựng bản nháp bệnh án kiểm chứng được.
- **Lý do dùng dữ liệu mô phỏng (Synthetic Data):** Theo Nghị định 13/2023/NĐ-CP và Luật Khám bệnh, chữa bệnh 2023, dữ liệu ghi âm khám bệnh thật là dữ liệu cá nhân nhạy cảm tuyệt đối không được công bố hoặc chia sẻ tự do khi chưa có phê duyệt Hội đồng Đạo đức (IRB). Dữ liệu tổng hợp cho phép kiểm soát chính xác đáp án gốc (Ground Truth) và tái lập thí nghiệm 100% bằng `seed=42`.

## 2. Thành phần & Quy mô Bộ Dữ liệu (Composition)
| Thuộc tính | Bộ gốc v1 (`mo_rong=False`) | Bộ mở rộng v2 (`mo_rong=True`) | Bộ Thử thách Đối kháng (`thach_thuc`) |
| :--- | :--- | :--- | :--- |
| **Số lượng hội thoại** | 5.000 ca (`seed=42`) | 5.000 ca (`seed=2611`) | 300 ca (150 cặp đối chứng ranh giới) |
| **Số khuôn bệnh lâm sàng** | 200 khuôn gốc (`BENH_GOC`) | 657 khuôn (200 gốc + 70 mở rộng + 387 bổ sung; 656 ca xuất hiện) | 4 nhóm bẫy: Đổi chủ thể, Tự sửa, Nhiễu ASR, Phương ngữ |
| **Tổng số lượt thoại (câu)** | 87.473 lượt | 87.097 lượt | ~4.200 lượt |
| **Số câu duy nhất** | 20.190 câu | **45.835 câu (+127,0%)** | Đa dạng theo 3 miền Bắc – Trung – Nam |
| **Tỷ lệ lặp câu (mọi câu)** | 76,92% | **47,37%** (câu $\ge 8$ từ: **42,19%**, $\ge 10$ từ: **35,1%**) | < 25% |
| **Độ phong phú từ vựng (MTLD)** | 93,0 | **145,4 (+56,3%)** | 142,4 |
| **Độ đa dạng Bigram (Distinct-2)** | 0,0188 | **0,0468 (+148,9%)** | 0,0241 |
| **Trích dẫn nguyên văn tuyệt đối** | 100% | **100,0000% (52.634/52.634)** | 100% |
| **Lỗi vi phạm 6 quy tắc chất lượng** | 0 (gốc) | **0 lỗi / 87.097 lượt (0,000%)** | 0 lỗi |

## 3. Chiến lược Chia Tập & Chống Rò rỉ Dữ liệu (Template-Disjoint Split)
- **Đơn vị chia tách độc lập là KHUÔN BỆNH (`benh`), tuyệt đối không chia ngẫu nhiên theo dòng hội thoại:**
  - **Tập chia v1 gốc (`hoi_thoai_viet_5000.jsonl`):** 150 khuôn bệnh Train (3.751 ca, 31.916 mệnh đề) / 26 khuôn Dev (663 ca, 5.620 mệnh đề) / 24 khuôn Test (586 ca).
  - **Tập chia v2 mở rộng (`hoi_thoai_viet_v2_mo_rong.jsonl`):**
    - `viet_train_v2.jsonl`: 515 khuôn phân bổ (514 khuôn xuất hiện trong 3.925 ca khám, 37.232 mệnh đề).
    - `viet_phat_trien_v2.jsonl`: 72 khuôn bệnh độc lập (551 ca khám, 5.345 mệnh đề).
    - `viet_kiem_tra_cuoi_v2.jsonl`: 70 khuôn bệnh độc lập (524 ca khám, 4.953 mệnh đề).
- **Ma trận độc lập ngữ nghĩa Train – Test (`src/kiem_nghiem_ngoai_khuon.py`):** Trên 36.050 cặp khuôn giữa 515 khuôn Train và 70 khuôn Test, giao tập tên khuôn bằng **0**, độ tương đồng Jaccard từ khóa triệu chứng trung bình chỉ **0,0587** (`p95 = 0,1172`, tỷ lệ cặp $\ge 0,20$ chỉ **0,17%**), Bigram Jaccard **0,0891**, Trigram Jaccard **0,0287**. Danh sách tên từng khuôn theo tập được đóng băng công khai tại [`data/manifest_v2_mo_rong_5000.json`](../data/manifest_v2_mo_rong_5000.json).
- **Bảo toàn biên giới khi mở rộng (`tests/test_chia_khuon_mo_rong_khong_doi.py`):** Mọi lô khuôn mở rộng từ khuôn 201 trở đi được chia độc lập theo từng đợt (80% Train / 10% Dev / 10% Test), đảm bảo **0 khuôn nào trong 200 khuôn gốc bị dịch chuyển tập** (Mã băm vàng `sinh_bo(200, seed=42)` = `2bedc64168fe45dd…`).

## 4. Giới hạn Đã biết & Minh bạch Khoa học (Known Limitations)
1. **Khoảng cách Sim2Real & Độ lặp câu (Kích hoạt Điều kiện dừng Phương án B):** Dữ liệu sinh từ khuôn và bộ biến thể ngữ cảnh lâm sàng đa tầng (`src/bien_the_cau.py`) đã giảm tỷ lệ lặp câu từ `76,92%` xuống `47,37%` (đối với lượt thoại dài $\ge 8$ từ giảm từ `69,6%` xuống `42,19%`), số câu duy nhất tăng từ 20.190 lên 45.835 (+127,0%), độ đa dạng bigram Distinct-2 tăng lên `0,0468` (+148,9%). Sau hai vòng tối ưu tự nhiên (Vòng B1: ngữ cảnh hóa câu hỏi bác sĩ theo triệu chứng, tiền sử, thuốc, dị ứng, gia đình; Vòng B2: mở rộng biến thể câu ngắn lâm sàng 3 miền), tỷ lệ lặp dừng ở mức 47,37%. Dự án kích hoạt **Điều kiện dừng có chủ đích**: Không ép tỷ lệ lặp xuống $\le 30\%$ bằng cách kéo dài câu, chèn số hay thêm từ đệm vô nghĩa. Nguyên nhân cấu trúc: các lượt đáp ngắn xã giao và xác nhận danh tính mang tính tất yếu trong giao tiếp y khoa người Việt ("vâng ạ.", "của tôi ạ.", "tôi đi khám.", "dạ không sao.") chiếm tỷ trọng lớn trong 87.097 lượt thoại.
2. **Quy mô khuôn & Trạng thái duyệt y khoa:** Tích hợp đầy đủ 657 khuôn bệnh từ kho lâm sàng tập trung `src/kho_khuon.py`. Toàn bộ 200 khuôn gốc mang cờ `da_duyet = True`; 457 khuôn mở rộng mang cờ minh bạch `da_duyet = False` và phân loại `he_co_quan`, đảm bảo nguyên tắc y khoa không đưa các khuôn mở rộng vào quyết định điều trị khi chưa có hội đồng bác sĩ chuyên khoa thẩm định.
3. **Đánh giá trên người bệnh thật:** Kết quả F1, SER và CHWER hiện chỉ có hiệu lực trên dữ liệu mô phỏng và bộ thử thách đối kháng; cần thử nghiệm lâm sàng chéo (Crossover Trial) với 8–10 bác sĩ ngoại trú trước khi áp dụng lâm sàng thực tế.
