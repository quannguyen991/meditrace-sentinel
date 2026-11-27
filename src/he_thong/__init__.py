# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch]
Làm gì   : Dịch vụ HTTP mà web gọi vào, cùng các phần an toàn: khử định danh, rào chắn, nhật
           ký ký duyệt WORM, khai mã nguồn.
Bản đồ   : BAN_DO_MA_NGUON.md

Các tệp:
    dich_vu_http                Chạy dịch vụ HTTP tại chỗ để giao diện chép lời, dựng bản
                                nháp hồ sơ mà không gửi hội thoại ra internet.
    dieu_phoi_cac_chot_an_toan  Nối các chốt an toàn lâm sàng thành một đường chạy và ghi
                                vết từng chốt để kiểm toán được.
    duong_dan                   Khai báo tập trung các đường dẫn thư mục dữ liệu, mô hình và
                                kết quả để nơi khác không ghi cứng.
    ep_kieu_dau_vao             Ép dữ liệu thô từ JSON/HTTP về kiểu đúng để lỗi nhập liệu
                                không làm hỏng các bước sau.
    hop_dong_api                Định nghĩa hình dạng dữ liệu mà dịch vụ Python trả về để máy
                                chủ và giao diện TypeScript hiểu cùng một hợp đồng.
    khai_ma_nguon               Lập bảng khai tệp mã nguồn nào do AI viết, sửa mấy lần và
                                theo lời nhắc nào, để minh bạch phần AI.
    khu_dinh_danh               Tìm và che thông tin định danh cá nhân (tên, CCCD, số điện
                                thoại, BHYT) trước khi văn bản đi tiếp.
    nhat_ky_ky_duyet_worm       Ghi nhật ký ký duyệt chỉ thêm, không sửa xoá, nối các dòng
                                bằng chuỗi băm SHA-256 để phát hiện can thiệp.
    nhat_ky_loi_nhac            Trích các lời nhắc của người dùng dẫn tới sửa mã nguồn từ
                                bản ghi phiên làm việc, che thông tin nhạy cảm.
    rao_chan_an_toan            Chặn đầu ra không an toàn bằng nhiều tầng kiểm: chất lượng
                                chép lời, nhất quán người nói, hành vi hội thoại, bằng
                                chứng, an toàn lâm sàng.
"""
