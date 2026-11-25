# BÁO CÁO KIỂM TOÁN AN TOÀN DƯỢC LÝ & RÀO CHẮN LÂM SÀNG BỘ DỮ LIỆU V2
**Tệp kiểm tra:** `data/hoi_thoai_viet_5000.jsonl`
**Tổng số ca khám quét:** 5,000 ca

## 1. TỔNG HỢP CÁC CHỈ SỐ AN TOÀN CỐT LÕI

| Chỉ số An toàn & Bất biến Lâm sàng | Số lượng / Đo đạc | Tỷ lệ Đạt | Chuẩn Yêu Cầu | Kết Luận |
|---|---|---|---|---|
| **Rào chắn Dị ứng Người nhà (Zero-Leakage)** | 1406/1406 ca bẫy | **100.00%** | 100.00% | **ĐẠT XUẤT SẮC** |
| **Bảo toàn Trích dẫn Nguyên văn (Exact Substring)** | 5000/5000 ca | **100.00%** | 100.00% | **ĐẠT XUẤT SẮC** |
| **Xử lý Đính chính Hiệu lực (Self-Repair)** | 766/766 ca | **100.00%** | $\ge 95.00\%$ | **ĐẠT XUẤT SẮC** |
| **Tương tác thuốc Chống chỉ định (DDI)** | 0 trường hợp | - | Giám sát lâm sàng | Ghi nhận |
| **Tương tác thuốc Nguy cơ cao** | 2 trường hợp | - | Giám sát lâm sàng | Ghi nhận |
| **Thuốc Khoảng điều trị hẹp (NTI)** | 30 ca (30 lượt) | - | Giám sát cảnh báo | Ghi nhận |

## 2. PHÂN TÍCH RÀO CHẮN AN TOÀN DỊ ỨNG & CHỦ THỂ (BẤT BIẾN 2 & 5)
- Tổng số ca có tình huống bẫy người nhà (`di_ung_nguoi_nha`, `nguoi_ke_benh_minh`): **1406 ca**.
- Số ca bảo vệ thành công (chuyển sang Tiền sử gia đình hoặc cách ly CẦN XÁC NHẬN): **1406 ca**.
- Số ca vi phạm rò rỉ dị ứng người nhà sang bệnh nhân: **0 ca (0.00%)**.
-> **Khẳng định:** Hệ thống bảo toàn 100% rào chắn dị ứng, tuyệt đối không có hiện tượng bệnh nhân bị gán nhầm dị ứng thuốc của người nhà.

## 3. THỐNG KÊ DƯỢC LÝ & TƯƠNG TÁC THUỐC (PHARMACOVIGILANCE)
- Số ca có đề cập đến thuốc điều trị/tiền sử: **1753 ca** (2021 lượt thuốc).
- Số ca có từ 2 thuốc trở lên và xuất hiện tương tác lâm sàng: **2 ca**.
### Mẫu một số trường hợp tương tác thuốc tiêu biểu phát hiện được:
- **Ca hv_0793 (cơn thiếu máu não thoáng qua):**
  * [NGUY CƠ CAO] clopidogrel + omeprazole: Giảm hiệu lực chống kết tập tiểu cầu, tăng nguy cơ tái phát nhồi máu cơ tim/huyết khối stent
- **Ca hv_4527 (cơn thiếu máu não thoáng qua):**
  * [NGUY CƠ CAO] clopidogrel + omeprazole: Giảm hiệu lực chống kết tập tiểu cầu, tăng nguy cơ tái phát nhồi máu cơ tim/huyết khối stent

## 4. KẾT LUẬN & ĐỀ XUẤT CHO CHIEF VERIFIER
Bộ dữ liệu đáp ứng hoàn hảo các tiêu chuẩn an toàn dược lý và bất biến lâm sàng y tế, sẵn sàng nghiệm thu.