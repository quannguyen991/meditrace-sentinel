# Bảng nguồn và giấy phép dữ liệu

Tài liệu này chỉ ghi thông tin công khai đã kiểm chứng ngày 18/11/2026. Giấy phép riêng do tác giả cấp không đưa vào đây.

## 1. Bộ dữ liệu huấn luyện và kiểm thử

| Bộ | Nội dung kiểm chứng | Giấy phép ghi ở đâu | Ghi chú |
|---|---|---|---|
| VietMed (`leduckhai/VietMed`) | 16 giờ có nhãn, 1.000 giờ không nhãn. Ghi âm hội thoại y tế từ video công khai trên YouTube | Thẻ Hugging Face: **MIT**. Bài báo arXiv: **CC BY 4.0**. Kho GitHub MultiMed: không có tệp LICENSE. Notebook ghi CC BY-NC 4.0 | Ba nguồn không thống nhất. Cần xác nhận với tác giả |
| VietMed-Sum (`leduckhai/VietMed-Sum`) | Tóm tắt. Tập SYN là tóm tắt do GPT-3.5 tạo, không sửa | Thẻ Hugging Face ghi không có giấy phép | Chứa đầu ra của OpenAI, không dùng để huấn luyện mô hình trích xuất |
| ViMedCSS (`tensorxt/ViMedCSS`) | 34 giờ, 16.576 câu, thuật ngữ tiếng Anh xen trong câu tiếng Việt | **CC BY 4.0** (thẻ Hugging Face) | Đã dùng phân đoạn test |
| Meddies-Consultant (`Meddies/meddies-consultant`) | Hội thoại tư vấn tổng hợp bằng LLM. Bộ Vietnamese có 58.064 hội thoại | **CC BY-NC 4.0** (thẻ Hugging Face) | Chưa có bác sĩ duyệt. Lẫn thẻ suy luận `<think>`. Không có nhãn mệnh đề |
| MedSynth (`Ahmad0067/MedSynth`) | 10.035 cặp hội thoại-ghi chú SOAP, tiếng Anh | CC BY 4.0 theo bài báo | Không dùng cho tiếng Việt |

## 2. Mô hình

| Mô hình | Giấy phép | Ghi chú |
|---|---|---|
| vinai/PhoWhisper (small, medium, large) | BSD-3-Clause | Dùng làm bộ nhận dạng |
| Qwen3-4B | Xem thẻ mô hình trên Hugging Face | Bộ trích xuất của dự án |

## 3. Chú thích về tính hợp lệ

- Mọi dữ liệu huấn luyện từ bên ngoài chỉ dùng trong thí nghiệm nhận dạng, không dùng để sinh bệnh án.
- Bản nháp của dự án vẫn ở trạng thái chưa duyệt (`approved: false`), đến khi bác sĩ hoặc dược sĩ phê duyệt.
- Khi báo cáo, phải nêu rõ nguồn dữ liệu bên ngoài là ghi âm hội thoại từ video công khai (VietMed) và dữ liệu tổng hợp (Meddies, MedSynth).
