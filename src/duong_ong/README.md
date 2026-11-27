# Đường ống dựng bản nháp — `src/duong_ong/`

Biến lời thoại thành bản nháp mà mỗi dòng đều có căn cứ. Tiền tố bN_ là số bước (b0 → b7); chỉ bước b1 dùng AI, các bước khác là luật.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [b0_cat_doan_van.py](b0_cat_doan_van.py) | Bước 0 – Chuẩn hoá đầu vào | Cắt một lời nói thành các đoạn ngắn theo dấu câu, để nơi sinh dữ liệu và nơi kiểm căn cứ cùng dùng một cách cắt. | `src/doan_van.py` |
| [b0_chuan_hoa_phuong_ngu.py](b0_chuan_hoa_phuong_ngu.py) | Bước 0 – Chuẩn hoá đầu vào | Hiểu từ địa phương và khẩu ngữ trong lời bệnh nhân nhưng vẫn giữ nguyên văn, để còn trích dẫn và đối chiếu. | `src/chuan_hoa.py` |
| [b1_cau_truc_menh_de.py](b1_cau_truc_menh_de.py) | Bước 1 – Rút mệnh đề | Định nghĩa bản ghi một mệnh đề (nội dung, chủ thể, người nói, câu trích, lượt căn cứ) và đổi kết quả JSON của mô hình thành bản ghi đó. | `src/phat_bieu.py` |
| [b1_ep_dau_ra_json.py](b1_ep_dau_ra_json.py) | Bước 1 – Rút mệnh đề | Ép mô hình trích mệnh đề đúng định dạng, câu trích khớp nguyên văn, rồi đổi đầu ra thành bản ghi mệnh đề. | `src/trich_xuat_thuc_the.py` |
| [b1_vi_du_mau_loi_nhac.py](b1_vi_du_mau_loi_nhac.py) | Bước 1 – Rút mệnh đề | Giữ các ví dụ mẫu đặt vào lời nhắc để mô hình biết cách rút mệnh đề đúng chủ thể, đúng người nói, đúng định dạng. | `src/vi_du_mau.py` |
| [b2_bu_chu_ngu_tinh_luoc.py](b2_bu_chu_ngu_tinh_luoc.py) | Bước 2 – Gom người | Bù chủ thể cho câu bị lược chủ ngữ theo ngữ cảnh hội thoại, và quản lý vòng đời mệnh đề khi có đính chính hay mâu thuẫn. | `src/may_trang_thai_hoi_thoai.py` |
| [b2_gom_nguoi_thuc_the.py](b2_gom_nguoi_thuc_the.py) | Bước 2 – Gom người | Gom các cách gọi khác nhau (tôi, chồng tôi, thuốc đó) về cùng một chủ thể, phân biệt người nói với người được nói đến. | `src/thuc_the.py` |
| [b3_cap_nhat_trang_thai.py](b3_cap_nhat_trang_thai.py) | Bước 3 – Cập nhật trạng thái | Cập nhật trạng thái mệnh đề bằng luật cố định: bản bị đính chính thì đánh dấu thay thế (không xoá), hai bên trái nhau thì đánh dấu mâu thuẫn. | `src/cap_nhat.py` |
| [b3_phan_xu_quan_he.py](b3_phan_xu_quan_he.py) | Bước 3 – Cập nhật trạng thái | Quyết định quan hệ (bổ sung, đính chính, diễn biến, mâu thuẫn) cho từng cặp mệnh đề ứng viên, bằng luật hoặc bằng một lượt hỏi mô hình. | `src/phan_quan_he.py` |
| [b3_sinh_cap_ung_vien_quan_he.py](b3_sinh_cap_ung_vien_quan_he.py) | Bước 3 – Cập nhật trạng thái | Tìm các cặp mệnh đề có thể liên quan (tự sửa, mâu thuẫn, nối tiếp theo thời gian) để đem đi phân xử quan hệ. | `src/ung_vien_quan_he.py` |
| [b4_kiem_can_cu.py](b4_kiem_can_cu.py) | Bước 4 – Kiểm căn cứ | Kiểm mỗi mệnh đề có thật sự được nói trong lời thoại không — đúng câu, đúng người, đúng mức — trước khi cho vào bản nháp. | `src/khoa_bang_chung.py` |
| [b4_kiem_day_du.py](b4_kiem_day_du.py) | Bước 4 – Kiểm căn cứ | Kiểm bản nháp có bỏ sót mệnh đề còn hiệu lực nào không, và thêm lại chỗ sót khi có căn cứ trong bảng mệnh đề. | `src/kiem_day_du.py` |
| [b5_diem_rui_ro_quy_gan.py](b5_diem_rui_ro_quy_gan.py) | Bước 5 – Xếp chỗ | Chấm điểm rủi ro mệnh đề bị gán nhầm người và đẩy mệnh đề điểm cao sang mục chưa giải quyết theo ngưỡng. | `src/rui_ro_quy_gan.py` |
| [b5_viet_ban_nhap.py](b5_viet_ban_nhap.py) | Bước 5 – Xếp chỗ | Viết bản nháp hồ sơ từ bảng mệnh đề bằng mẫu câu cố định, không dùng mô hình, mỗi mệnh đề vào đúng một mục. | `src/sinh_benh_an.py` |
| [b5_xep_cho_cong_rui_ro.py](b5_xep_cho_cong_rui_ro.py) | Bước 5 – Xếp chỗ | Chấm rủi ro lâm sàng từng mệnh đề và quyết định đưa vào thân bản nháp, mục CẦN XÁC NHẬN kèm lý do, hay loại (vẫn lưu vết). | `src/cong_rui_ro.py` |
| [b6_goi_y_hoi_lai.py](b6_goi_y_hoi_lai.py) | Bước 6 – Hỏi lại và sửa | Chọn ít câu hỏi nhất (tối đa 3) mà giải quyết được nhiều rủi ro nhất để bác sĩ hỏi lại người bệnh. | `src/hoi_lai.py` |
| [b6_sua_cuc_bo.py](b6_sua_cuc_bo.py) | Bước 6 – Hỏi lại và sửa | Kiểm từng câu của bản nháp với bảng mệnh đề và chỉ chuyển chỗ hoặc sửa câu sai, không sinh lại cả bản. | `src/sua_cuc_bo.py` |
| [b7_ban_duyet_html.py](b7_ban_duyet_html.py) | Bước 7 – Bản duyệt | Dựng trang duyệt ba cột (lời thoại, mệnh đề, bản nháp) thành một tệp HTML tự chứa, bấm dòng nào tô đoạn lời thoại dẫn của dòng đó. | `src/giao_dien_duyet.py` |
| [chay_duong_ong.py](chay_duong_ong.py) | Điều phối | Chạy các nhánh so sánh trên tập ca: A và A+ (mốc đối chứng), các nhánh B, C, D qua đường ống b1–b6, rồi ghi kết quả. | `src/nhanh.py` |
| [chay_nhanh_e.py](chay_nhanh_e.py) | Điều phối | Chạy nhánh E: lấy bản nháp của nhánh A, bổ sung chỗ sót và sửa cục bộ bằng bảng mệnh đề, không viết lại bản nháp. | `src/nhanh_e.py` |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
