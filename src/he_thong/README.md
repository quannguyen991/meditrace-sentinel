# Dịch vụ, an toàn và minh bạch — `src/he_thong/`

Dịch vụ HTTP mà web gọi vào, cùng các phần an toàn: khử định danh, rào chắn, nhật ký ký duyệt WORM, khai mã nguồn.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [dich_vu_http.py](dich_vu_http.py) | Dịch vụ | Chạy dịch vụ HTTP tại chỗ để giao diện chép lời, dựng bản nháp hồ sơ mà không gửi hội thoại ra internet. | `src/dich_vu.py` |
| [dieu_phoi_cac_chot_an_toan.py](dieu_phoi_cac_chot_an_toan.py) | Dịch vụ | Nối các chốt an toàn lâm sàng thành một đường chạy và ghi vết từng chốt để kiểm toán được. | `src/dieu_phoi_ha_tang.py` |
| [duong_dan.py](duong_dan.py) | Cấu hình | Khai báo tập trung các đường dẫn thư mục dữ liệu, mô hình và kết quả để nơi khác không ghi cứng. | `src/duong_dan.py` |
| [ep_kieu_dau_vao.py](ep_kieu_dau_vao.py) | An toàn | Ép dữ liệu thô từ JSON/HTTP về kiểu đúng để lỗi nhập liệu không làm hỏng các bước sau. | `src/ep_kieu_dau_vao.py` |
| [hop_dong_api.py](hop_dong_api.py) | Dịch vụ | Định nghĩa hình dạng dữ liệu mà dịch vụ Python trả về để máy chủ và giao diện TypeScript hiểu cùng một hợp đồng. | `src/api_contract.py` |
| [khai_ma_nguon.py](khai_ma_nguon.py) | Minh bạch | Lập bảng khai tệp mã nguồn nào do AI viết, sửa mấy lần và theo lời nhắc nào, để minh bạch phần AI. | `src/khai_ma_nguon.py` |
| [khu_dinh_danh.py](khu_dinh_danh.py) | An toàn | Tìm và che thông tin định danh cá nhân (tên, CCCD, số điện thoại, BHYT) trước khi văn bản đi tiếp. | `src/khu_dinh_danh.py` |
| [nhat_ky_ky_duyet_worm.py](nhat_ky_ky_duyet_worm.py) | An toàn | Ghi nhật ký ký duyệt chỉ thêm, không sửa xoá, nối các dòng bằng chuỗi băm SHA-256 để phát hiện can thiệp. | `src/worm_audit_log.py` |
| [nhat_ky_loi_nhac.py](nhat_ky_loi_nhac.py) | Minh bạch | Trích các lời nhắc của người dùng dẫn tới sửa mã nguồn từ bản ghi phiên làm việc, che thông tin nhạy cảm. | `src/nhat_ky_loi_nhac.py` |
| [rao_chan_an_toan.py](rao_chan_an_toan.py) | An toàn | Chặn đầu ra không an toàn bằng nhiều tầng kiểm: chất lượng chép lời, nhất quán người nói, hành vi hội thoại, bằng chứng, an toàn lâm sàng. | `src/guardrails.py` |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
