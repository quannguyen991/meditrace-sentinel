# Độ lặp lại của bộ dữ liệu: 200 khuôn và 5.000 ca

Ngày đo: 18/11/2026. Mã đo: [thi-nghiem/du-lieu/do_lap_lai.py](../thi-nghiem/du-lieu/do_lap_lai.py) và [thi-nghiem/du-lieu/so_sanh_nguon.py](../thi-nghiem/du-lieu/so_sanh_nguon.py). Bộ mô phỏng được sinh lại bằng `sinh_bo(5000, seed=42)` (không lưu vào repo).

## 1. Câu trả lời ngắn

- **Không có hội thoại trùng nguyên văn** (0/5.000).
- **Có lặp câu rất nhiều:** 93.288 câu thoại, chỉ 19.759 câu duy nhất (21%). Khoảng 72% câu là bản sao nguyên văn của một câu khác trong bộ.
- **Từ vựng hẹp:** 1.994 từ khác nhau trên 1.009.148 từ. Tỷ lệ TTR là 0,002. Dữ liệu thật có TTR 0,018–0,025, tức gấp khoảng 9–12 lần.
- **Khoảng cách với lời nói thật:** chỉ 1,0–1,5% các cụm 3 từ của VietMed và ViMedCSS xuất hiện trong bộ mô phỏng. Bộ mô phỏng không bao phủ được cách nói tự nhiên.

## 2. Số liệu chi tiết

### 2.1. Bộ mô phỏng (5.000 ca, 200 khuôn)

| Chỉ số | Giá trị |
|---|---|
| Số khuôn có ca | 200 |
| Số ca mỗi khuôn (min–max) | 11–41 |
| Hội thoại trùng nguyên văn | 0 |
| Câu thoại tổng / câu duy nhất | 93.288 / 19.759 |
| Câu xuất hiện ở nhiều hơn một ca | 24,8% |
| Jaccard 3-gram, cặp cùng khuôn (trung bình) | 0,229 |
| Cặp cùng khuôn có Jaccard ≥ 0,5 | 0,22% |
| Jaccard 3-gram, cặp khác khuôn (trung bình) | 0,061 |
| Cặp khác khuôn có Jaccard ≥ 0,5 | 0% |

Đọc kết quả: các ca cùng khuôn chia sẻ một phần cụm từ (0,229), nhưng gần như không có cặp nào trùng gần nguyên văn (0,22%). Các khuôn khác nhau gần như không chồng lấp. Phần lặp chủ yếu nằm ở câu đơn lẻ, không phải ở cả hội thoại.

### 2.2. So sánh ba nguồn

| Nguồn | Số câu | Số từ | Từ vựng | TTR | Câu trùng nguyên văn |
|---|---|---|---|---|---|
| Mô phỏng 5.000 ca | 87.539 | 1.009.148 | 1.994 | 0,0020 | 67.572 |
| Thật: VietMed-train | 2.773 | 67.901 | 1.720 | 0,0253 | 2 |
| Thật: ViMedCSS-train | 11.832 | 313.106 | 5.663 | 0,0181 | 135 |

Phủ 3-gram:

| Nguồn A → nguồn B | Tỷ lệ 3-gram của A có trong B |
|---|---|
| VietMed-thật → mô phỏng | 1,05% |
| ViMedCSS-thật → mô phỏng | 0,84% |
| Mô phỏng → VietMed-thật | 1,46% |
| VietMed-thật → ViMedCSS-thật | 26,2% |

Đọc kết quả: hai bộ thật có phần chung đáng kể với nhau (26%), nhưng gần như không chung với bộ mô phỏng. Bộ mô phỏng nằm ngoài phân phối của lời nói thật.

## 2.3. Tách tập huấn luyện, phát triển, kiểm tra theo khuôn

Kiểm bằng `src/tach_tap_viet.phan_khuon` trên 200 tên khuôn (ngày 18/11/2026):

| Tập | Số khuôn |
|---|---|
| Huấn luyện | 150 |
| Phát triển | 26 |
| Kiểm tra cuối | 24 |

Giao giữa các tập: 0 khuôn chung giữa huấn luyện–phát triển, huấn luyện–kiểm tra, phát triển–kiểm tra. Ba tập phủ kín 200 khuôn. Tách theo khuôn nghĩa là không có ca nào của cùng một khuôn nằm ở hai tập.

Giới hạn: tách theo khuôn chưa loại trùng nội dung ở cấp câu. Câu thoại lặp giữa các khuôn (mục 2.2) vẫn có thể rò rỉ dưới dạng cụm từ chung.

## 3. Hệ quả cho báo cáo

1. Không được viết "5.000 hội thoại đa dạng" hay "không lặp". Nên viết: 5.000 ca sinh từ 200 khuôn, không trùng nguyên văn hội thoại, nhưng 72% câu thoại là bản lặp của câu khác.
2. Số 5.000 ca không nói lên độ đa dạng. Số câu duy nhất (19.759) và số khuôn (200) là các con số đúng cần nêu.
3. Chỉ số "78,3% đa dạng" trong tài liệu cũ không có phép đo tương ứng trong mã. Lần đo này không tái tạo được con số đó, nên không nên dùng.
4. Muốn chứng minh khả năng tổng quát hóa, phải đánh giá trên dữ liệu thật (VietMed, ViMedCSS) ở mức ASR, và trên một tập mô phỏng ngoài khuôn cho bước trích xuất. Bộ thật không có nhãn ghi chú nên chưa đánh giá được bước trích xuất trên dữ liệu thật.

## 4. Việc có thể làm tiếp (chưa làm)

- Mở rộng ngân hàng câu của bộ sinh để giảm lặp câu (mục tiêu: tỷ lệ câu duy nhất trên 60%). Thay đổi này làm lại toàn bộ bộ dữ liệu, cần duyệt lại.
- Dùng VietMed-train làm nguồn cụm từ tự nhiên cho bộ sinh, sau khi kiểm tra giấy phép.
- Gán nhãn một tập nhỏ hội thoại thật (ví dụ 100 ca) để đánh giá trích xuất trên dữ liệu thật. Cần bác sĩ hoặc người gán nhãn đã được đào tạo.

## 5. Ghi chú

- Đo trên bộ sinh với seed 42. Các số có thể thay đổi nếu đổi seed; chưa đo độ ổn định theo seed.
- Jaccard 3-gram dùng mẫu ngẫu nhiên 4.000 cặp, không phải toàn bộ tổ hợp.
