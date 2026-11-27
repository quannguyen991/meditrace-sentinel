# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp]
Làm gì   : Biến lời thoại thành bản nháp mà mỗi dòng đều có căn cứ. Tiền tố bN_ là số bước
           (b0 → b7); chỉ bước b1 dùng AI, các bước khác là luật.
Bản đồ   : BAN_DO_MA_NGUON.md

Các tệp:
    b0_cat_doan_van               Cắt một lời nói thành các đoạn ngắn theo dấu câu, để nơi
                                  sinh dữ liệu và nơi kiểm căn cứ cùng dùng một cách cắt.
    b0_chuan_hoa_phuong_ngu       Hiểu từ địa phương và khẩu ngữ trong lời bệnh nhân nhưng
                                  vẫn giữ nguyên văn, để còn trích dẫn và đối chiếu.
    b1_cau_truc_menh_de           Định nghĩa bản ghi một mệnh đề (nội dung, chủ thể, người
                                  nói, câu trích, lượt căn cứ) và đổi kết quả JSON của mô
                                  hình thành bản ghi đó.
    b1_ep_dau_ra_json             Ép mô hình trích mệnh đề đúng định dạng, câu trích khớp
                                  nguyên văn, rồi đổi đầu ra thành bản ghi mệnh đề.
    b1_vi_du_mau_loi_nhac         Giữ các ví dụ mẫu đặt vào lời nhắc để mô hình biết cách
                                  rút mệnh đề đúng chủ thể, đúng người nói, đúng định dạng.
    b2_bu_chu_ngu_tinh_luoc       Bù chủ thể cho câu bị lược chủ ngữ theo ngữ cảnh hội
                                  thoại, và quản lý vòng đời mệnh đề khi có đính chính hay
                                  mâu thuẫn.
    b2_gom_nguoi_thuc_the         Gom các cách gọi khác nhau (tôi, chồng tôi, thuốc đó) về
                                  cùng một chủ thể, phân biệt người nói với người được nói
                                  đến.
    b3_cap_nhat_trang_thai        Cập nhật trạng thái mệnh đề bằng luật cố định: bản bị đính
                                  chính thì đánh dấu thay thế (không xoá), hai bên trái nhau
                                  thì đánh dấu mâu thuẫn.
    b3_phan_xu_quan_he            Quyết định quan hệ (bổ sung, đính chính, diễn biến, mâu
                                  thuẫn) cho từng cặp mệnh đề ứng viên, bằng luật hoặc bằng
                                  một lượt hỏi mô hình.
    b3_sinh_cap_ung_vien_quan_he  Tìm các cặp mệnh đề có thể liên quan (tự sửa, mâu thuẫn,
                                  nối tiếp theo thời gian) để đem đi phân xử quan hệ.
    b4_kiem_can_cu                Kiểm mỗi mệnh đề có thật sự được nói trong lời thoại không
                                  — đúng câu, đúng người, đúng mức — trước khi cho vào bản
                                  nháp.
    b4_kiem_day_du                Kiểm bản nháp có bỏ sót mệnh đề còn hiệu lực nào không, và
                                  thêm lại chỗ sót khi có căn cứ trong bảng mệnh đề.
    b5_diem_rui_ro_quy_gan        Chấm điểm rủi ro mệnh đề bị gán nhầm người và đẩy mệnh đề
                                  điểm cao sang mục chưa giải quyết theo ngưỡng.
    b5_viet_ban_nhap              Viết bản nháp hồ sơ từ bảng mệnh đề bằng mẫu câu cố định,
                                  không dùng mô hình, mỗi mệnh đề vào đúng một mục.
    b5_xep_cho_cong_rui_ro        Chấm rủi ro lâm sàng từng mệnh đề và quyết định đưa vào
                                  thân bản nháp, mục CẦN XÁC NHẬN kèm lý do, hay loại (vẫn
                                  lưu vết).
    b6_goi_y_hoi_lai              Chọn ít câu hỏi nhất (tối đa 3) mà giải quyết được nhiều
                                  rủi ro nhất để bác sĩ hỏi lại người bệnh.
    b6_sua_cuc_bo                 Kiểm từng câu của bản nháp với bảng mệnh đề và chỉ chuyển
                                  chỗ hoặc sửa câu sai, không sinh lại cả bản.
    b7_ban_duyet_html             Dựng trang duyệt ba cột (lời thoại, mệnh đề, bản nháp)
                                  thành một tệp HTML tự chứa, bấm dòng nào tô đoạn lời thoại
                                  dẫn của dòng đó.
    chay_duong_ong                Chạy các nhánh so sánh trên tập ca: A và A+ (mốc đối
                                  chứng), các nhánh B, C, D qua đường ống b1–b6, rồi ghi kết
                                  quả.
    chay_nhanh_e                  Chạy nhánh E: lấy bản nháp của nhánh A, bổ sung chỗ sót và
                                  sửa cục bộ bằng bảng mệnh đề, không viết lại bản nháp.
"""
