# Lớp cảnh báo — `src/canh_bao/`

Chạy sau bước kiểm căn cứ. Đối chiếu từng dòng của bản nháp với lời thoại để bắt lỗi khó thấy; mỗi cảnh báo nêu lượt nói và lý do. Toàn bộ là luật, không dùng mô hình.

| Tệp | Làm gì |
|---|---|
| [phat_hien.py](phat_hien.py) | Phát hiện lỗi theo từng mệnh đề so với lời thoại: sai người, đảo phủ định, sai số, sai bên trái/phải, sai mức độ, nhầm thời điểm. |
| [toan_ca.py](toan_ca.py) | Cảnh báo ở mức cả ca: thông tin bị bỏ sót, mâu thuẫn giữa các dòng, giá trị đã bị đính chính mà vẫn giữ, ghi lặp. |
| [bo_sot.py](bo_sot.py) | Tìm những đoạn hội thoại có thông tin lâm sàng mà bản nháp chưa ghi, dùng chung cho cả hệ thống. |
| [lam_sang.py](lam_sang.py) | Cảnh báo theo kiến thức lâm sàng: liều vượt trần ngày, tương tác thuốc, kê thuốc cho người đang dị ứng. |
| [asr.py](asr.py) | Cảnh báo dòng bản nháp có thể sai vì lỗi chép giọng nói, tách riêng do xảy ra trước bước mô hình. |
| [gop.py](gop.py) | Chạy mọi bộ phát hiện, gộp cảnh báo trùng, chọn cảnh báo chính và áp chính sách D để quyết định dòng nào bị chặn. |
| [loai.py](loai.py) | Định nghĩa chung của lớp cảnh báo: các loại lỗi, cấu trúc một cảnh báo và mức nghiêm trọng. |
| [loi_noi.py](loi_noi.py) | Chuẩn hoá lời nói tiếng Việt cho các luật: tách ý, nhận câu hỏi, bỏ từ đệm. |
| [so_lieu.py](so_lieu.py) | Tách con số kèm đơn vị trong câu tiếng Việt để so số ghi trong bản nháp với số được nói. |
| [nhat_ky.py](nhat_ky.py) | Ghi các cảnh báo ra tệp nhật ký từng dòng để phục vụ nghiên cứu sau này. |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
