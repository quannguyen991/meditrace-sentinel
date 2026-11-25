# Báo cáo Phân tích Phân bố Độ dài & Mốc Audio Segments Bộ Dữ liệu V2 (5.000 ca)
**Tệp dữ liệu:** `data\hoi_thoai_viet_v2_mo_rong.jsonl`
**Thời gian lập báo cáo:** 2026-11-22 21:41:17

---

## 1. Tổng quan Quy mô Âm thanh Lâm sàng

| Đại lượng Đo lường | Giá trị Thống kê | Đơn vị / Ghi chú |
| :--- | :--- | :--- |
| **Tổng số ca hội thoại khám** | **5,000** | Ca khám hoàn chỉnh |
| **Tổng số lượt thoại âm thanh** | **87,644** | Lượt phát ngôn |
| **Tổng thời lượng âm thanh dự tính** | **119.31** | Giờ âm thanh phòng khám |
| **Tổng số mốc căn cứ âm thanh (Spans)** | **52,618** | Spans phục vụ Click-to-Verify |
| **Tỷ lệ spans hợp lệ đơn điệu** | **100.0%** | 100% không chồng chéo |

---

## 2. Phân bố Lượt thoại & Thời lượng trên mỗi Ca khám

- **Số lượt thoại / ca:**
  * Trung bình: **17.53** lượt/ca
  * Trung vị (P50): **18.0** lượt/ca
  * Phân vị 95 (P95): **22.0** lượt/ca
  * Tối thiểu / Tối đa: **8** lượt / **27** lượt
- **Thời lượng âm thanh / ca (tốc độ chuẩn 4.2 âm tiết/s + khoảng lặng tự nhiên):**
  * Thời lượng trung bình: **85.91 s** (~**1.43 phút**)
  * Trung vị (P50): **85.45 s**
  * Phân vị 95 (P95): **109.89 s**
  * Ngắn nhất / Dài nhất: **42.63 s** / **140.99 s**

---

## 3. Phân bố Độ dài Lượt thoại & Từ vựng (Word Distribution)

- **Số từ trung bình trên mỗi lượt thoại:** **18.48** từ/lượt
- **Phân nhóm độ dài lượt thoại:**
  * Lượt ngắn (< 5 từ - câu đáp tắt, chào hỏi xã giao): **0.02%**
  * Lượt trung bình (5 - 15 từ - câu hỏi, mô tả triệu chứng ngắn): **32.53%**
  * Lượt dài (> 15 từ - lời kể bệnh sử, giải thích đơn thuốc): **67.45%**

---

## 4. Phân bố Phân đoạn Người nói (Diarization Speaker Breakdown)

- **Bác sĩ (Doctor):** **56.64%** (chủ động dẫn dắt, hỏi bệnh, ra y lệnh)
- **Bệnh nhân (Patient):** **25.83%** (trực tiếp mô tả triệu chứng, xác nhận)
- **Người nhà (Caregiver):** **17.53%** (kể hộ bệnh nhi/người già, khai tiền sử gia đình)

---

## 5. Đặc tính Mốc Trích dẫn Căn cứ Âm thanh (Audio Citation Spans)

- **Tổng số mốc âm thanh trích dẫn:** **52,618** mốc
- **Thời lượng trung bình mỗi đoạn trích dẫn:** **3901.6 ms** (~**3.90 s**)
- **Tương thích Click-to-Verify Scrubber:**
  * 100% mốc có `start_ms < end_ms` và liên kết trực tiếp với lượt thoại gốc.
  * Được đệm pre-roll 400ms và post-roll 300ms trong `VerificationView.tsx` đảm bảo không bị cắt cụt âm tiết đầu/cuối khi bác sĩ nghe lại.
