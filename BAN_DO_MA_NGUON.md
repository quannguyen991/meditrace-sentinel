# Bản đồ mã nguồn MediTrace Sentinel

Tài liệu này giúp tìm nhanh **phần nào của hệ thống nằm ở tệp nào**. Mỗi tệp Python trong `src/` cũng có một khung ghi chú ở đầu tệp ghi: thuộc hệ thống nào, làm gì, gọi tới tệp nào, được tệp nào dùng, và tên cũ.

## Đường đi của một ca khám

```
Lời nói / tệp âm thanh
   │  src/audio/                      chép lời (PhoWhisper) + tách người nói — chạy tại chỗ
   ▼
Lời thoại theo lượt
   │  src/duong_ong/b0_*              chuẩn hoá phương ngữ, cắt đoạn (giữ nguyên văn)
   │  src/duong_ong/b1_*  ◄── AI      mô hình Qwen3-4B + adapter rút từng MỆNH ĐỀ kèm câu trích
   │  src/duong_ong/b2_*              gom người: thông tin nói về ai
   │  src/duong_ong/b3_*              cập nhật trạng thái: tự sửa, mâu thuẫn
   │  src/duong_ong/b4_*              kiểm căn cứ: 6 phép kiểm với đúng lượt nói
   │  src/canh_bao/                   lớp cảnh báo lỗi khó thấy
   │  src/duong_ong/b5_*              xếp chỗ: thân bản nháp / Cần xác nhận / loại → viết bản nháp
   │  src/duong_ong/b6_*              gợi ý câu hỏi lại
   ▼
Bản nháp + mục "Cần xác nhận"
   │  src/he_thong/dich_vu_http.py    dịch vụ HTTP tại chỗ
   │  web/                            giao diện bác sĩ: duyệt, sửa, ký (chặn ký khi còn mục chưa xác nhận)
   ▼
Bác sĩ ký duyệt → nhật ký WORM có chuỗi băm
```

Điều phối toàn bộ các bước nằm ở `src/duong_ong/chay_duong_ong.py` (nhánh C). **Chỉ bước 1 dùng mô hình AI; mọi bước khác là luật đọc được.**

## Giám khảo hỏi gì → mở tệp nào

| Câu hỏi | Mở tệp |
|---|---|
| Mô hình AI nằm ở bước nào, nhận gì và trả gì? | src/duong_ong/chay_duong_ong.py (nhánh C), src/duong_ong/b1_cau_truc_menh_de.py, src/huan_luyen/huan_luyen_sft.py (lời nhắc hệ thống) |
| Làm sao biết thông tin nói về ai (bệnh nhân hay người nhà)? | src/duong_ong/b2_gom_nguoi_thuc_the.py, src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py |
| Người bệnh tự sửa lời ("một tuần… à không, mười ngày") thì xử lý sao? | src/duong_ong/b3_cap_nhat_trang_thai.py |
| Kiểm căn cứ / chống bịa đặt ở đâu? | src/duong_ong/b4_kiem_can_cu.py (K1–K6 kiểm căn cứ, K7 loại thông tin đã bị thay thế) |
| Mục "Cần xác nhận" được quyết định thế nào? | src/duong_ong/b5_xep_cho_cong_rui_ro.py |
| Bản nháp được viết ra bằng gì, có dùng AI không? | src/duong_ong/b5_viet_ban_nhap.py (mẫu câu cố định, không dùng mô hình) |
| Lớp cảnh báo bắt những lỗi gì? | src/canh_bao/ (bắt đầu từ phat_hien.py và gop.py) |
| Chặn ký duyệt khi còn mục chưa xác nhận ở đâu? | web/src/lib/kyDuyet.ts, web/may-chu/routes/sign-off.ts, web/may-chu/worm.ts |
| Dữ liệu mô phỏng được sinh thế nào? Có trùng giữa train và test không? | src/bo_du_lieu/sinh_hoi_thoai_viet.py, src/bo_du_lieu/kho_khuon.py, src/bo_du_lieu/chia_tap_theo_khuon.py, src/do_luong/kiem_nghiem_ngoai_khuon.py |
| Con số tỷ lệ bỏ sót / F1 / SER tính ở đâu? | src/do_luong/do_bo_sot.py, src/do_luong/cham_he_thong.py, src/do_luong/do_dac.py |
| Vì sao ROUGE không đủ? Thước đo riêng là gì? | src/do_luong/thuoc_do_quy_gan.py, src/do_luong/chung_chi_thuoc_do.py |
| Huấn luyện mô hình thế nào, tốn bao nhiêu VRAM? | src/huan_luyen/huan_luyen_sft.py, src/huan_luyen/loss_theo_doan.py |
| Giọng nói được chép lời ở đâu, có gửi ra ngoài không? | src/audio/ (PhoWhisper chạy tại chỗ), web/may-chu/routes/asr.ts |
| Phần nào gọi AI bên ngoài? Có lộ dữ liệu bệnh nhân không? | web/may-chu/routes/llm-ngoai.ts (mặc định tắt), web/may-chu/tro-ly/an-danh.ts, src/he_thong/khu_dinh_danh.py |
| Tra cứu tài liệu y khoa lấy từ đâu? | web/may-chu/tra-cuu/nguon-ngoai.ts (PubMed, WHO, openFDA, kcb.vn…) |
| Tiền kiểm BHYT / ICD-10? | src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py, src/cong_cu_lam_sang/kiem_toan_xml_bhyt.py |
| Kiểm tương tác thuốc, dị ứng, chỉnh liều? | src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py, di_ung_cheo.py, hieu_chinh_lieu.py, tri_thuc_thuoc.py |
| Giao diện web gọi lõi Python thế nào? | web/server.ts → src/he_thong/dich_vu_http.py (hợp đồng: src/he_thong/hop_dong_api.py ↔ web/src/types/api-contract.ts) |

## Các thư mục trong `src/`

| Thư mục | Hệ thống | Nội dung | Số tệp |
|---|---|---|---|
| [`src/duong_ong/`](src/duong_ong/) | **Đường ống dựng bản nháp** | Biến lời thoại thành bản nháp mà mỗi dòng đều có căn cứ. Tiền tố bN_ là số bước (b0 → b7); chỉ bước b1 dùng AI, các bước khác là luật. | 20 |
| [`src/bo_du_lieu/`](src/bo_du_lieu/) | **Sinh, nạp và chia dữ liệu** | Sinh hội thoại khám bệnh mô phỏng và bộ thử thách, nạp dữ liệu ngoài, chia train / phát triển / kiểm tra theo khuôn bệnh. | 32 |
| [`src/huan_luyen/`](src/huan_luyen/) | **Huấn luyện mô hình** | Huấn luyện adapter Qwen3 cho bước rút mệnh đề (b1) và chọn mô hình bằng số đo. | 6 |
| [`src/do_luong/`](src/do_luong/) | **Đo lường và chấm điểm** | Sinh mọi con số trong báo cáo: cham_* là bộ chấm, do_* là các phép đo. | 34 |
| [`src/cong_cu_lam_sang/`](src/cong_cu_lam_sang/) | **Công cụ lâm sàng hỗ trợ bác sĩ** | Công cụ trong menu Công cụ quanh bản nháp (BHYT, thuốc, xét nghiệm, giấy tờ). Chỉ là gợi ý, không đổi cách dựng bản nháp; bảng tri thức chưa được chuyên gia duyệt. | 20 |
| [`src/he_thong/`](src/he_thong/) | **Dịch vụ, an toàn và minh bạch** | Dịch vụ HTTP mà web gọi vào, cùng các phần an toàn: khử định danh, rào chắn, nhật ký ký duyệt WORM, khai mã nguồn. | 10 |
| [`src/canh_bao/`](src/canh_bao/) | **Lớp cảnh báo** | Chạy sau bước kiểm căn cứ: đối chiếu từng dòng với lời thoại để bắt lỗi khó thấy. Toàn bộ là luật. | 10 |
| [`src/audio/`](src/audio/) | **Âm thanh** | Chép lời và tách người nói, chạy tại chỗ. | 14 |

## Danh sách tệp theo hệ thống

### Đường ống dựng bản nháp — `src/duong_ong/`

Biến lời thoại thành bản nháp mà mỗi dòng đều có căn cứ. Tiền tố bN_ là số bước (b0 → b7); chỉ bước b1 dùng AI, các bước khác là luật.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [b0_cat_doan_van.py](src/duong_ong/b0_cat_doan_van.py) | Bước 0 – Chuẩn hoá đầu vào | Cắt một lời nói thành các đoạn ngắn theo dấu câu, để nơi sinh dữ liệu và nơi kiểm căn cứ cùng dùng một cách cắt. | `src/doan_van.py` |
| [b0_chuan_hoa_phuong_ngu.py](src/duong_ong/b0_chuan_hoa_phuong_ngu.py) | Bước 0 – Chuẩn hoá đầu vào | Hiểu từ địa phương và khẩu ngữ trong lời bệnh nhân nhưng vẫn giữ nguyên văn, để còn trích dẫn và đối chiếu. | `src/chuan_hoa.py` |
| [b1_cau_truc_menh_de.py](src/duong_ong/b1_cau_truc_menh_de.py) | Bước 1 – Rút mệnh đề | Định nghĩa bản ghi một mệnh đề (nội dung, chủ thể, người nói, câu trích, lượt căn cứ) và đổi kết quả JSON của mô hình thành bản ghi đó. | `src/phat_bieu.py` |
| [b1_ep_dau_ra_json.py](src/duong_ong/b1_ep_dau_ra_json.py) | Bước 1 – Rút mệnh đề | Ép mô hình trích mệnh đề đúng định dạng, câu trích khớp nguyên văn, rồi đổi đầu ra thành bản ghi mệnh đề. | `src/trich_xuat_thuc_the.py` |
| [b1_vi_du_mau_loi_nhac.py](src/duong_ong/b1_vi_du_mau_loi_nhac.py) | Bước 1 – Rút mệnh đề | Giữ các ví dụ mẫu đặt vào lời nhắc để mô hình biết cách rút mệnh đề đúng chủ thể, đúng người nói, đúng định dạng. | `src/vi_du_mau.py` |
| [b2_bu_chu_ngu_tinh_luoc.py](src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py) | Bước 2 – Gom người | Bù chủ thể cho câu bị lược chủ ngữ theo ngữ cảnh hội thoại, và quản lý vòng đời mệnh đề khi có đính chính hay mâu thuẫn. | `src/may_trang_thai_hoi_thoai.py` |
| [b2_gom_nguoi_thuc_the.py](src/duong_ong/b2_gom_nguoi_thuc_the.py) | Bước 2 – Gom người | Gom các cách gọi khác nhau (tôi, chồng tôi, thuốc đó) về cùng một chủ thể, phân biệt người nói với người được nói đến. | `src/thuc_the.py` |
| [b3_cap_nhat_trang_thai.py](src/duong_ong/b3_cap_nhat_trang_thai.py) | Bước 3 – Cập nhật trạng thái | Cập nhật trạng thái mệnh đề bằng luật cố định: bản bị đính chính thì đánh dấu thay thế (không xoá), hai bên trái nhau thì đánh dấu mâu thuẫn. | `src/cap_nhat.py` |
| [b3_phan_xu_quan_he.py](src/duong_ong/b3_phan_xu_quan_he.py) | Bước 3 – Cập nhật trạng thái | Quyết định quan hệ (bổ sung, đính chính, diễn biến, mâu thuẫn) cho từng cặp mệnh đề ứng viên, bằng luật hoặc bằng một lượt hỏi mô hình. | `src/phan_quan_he.py` |
| [b3_sinh_cap_ung_vien_quan_he.py](src/duong_ong/b3_sinh_cap_ung_vien_quan_he.py) | Bước 3 – Cập nhật trạng thái | Tìm các cặp mệnh đề có thể liên quan (tự sửa, mâu thuẫn, nối tiếp theo thời gian) để đem đi phân xử quan hệ. | `src/ung_vien_quan_he.py` |
| [b4_kiem_can_cu.py](src/duong_ong/b4_kiem_can_cu.py) | Bước 4 – Kiểm căn cứ | Kiểm mỗi mệnh đề có thật sự được nói trong lời thoại không — đúng câu, đúng người, đúng mức — trước khi cho vào bản nháp. | `src/khoa_bang_chung.py` |
| [b4_kiem_day_du.py](src/duong_ong/b4_kiem_day_du.py) | Bước 4 – Kiểm căn cứ | Kiểm bản nháp có bỏ sót mệnh đề còn hiệu lực nào không, và thêm lại chỗ sót khi có căn cứ trong bảng mệnh đề. | `src/kiem_day_du.py` |
| [b5_diem_rui_ro_quy_gan.py](src/duong_ong/b5_diem_rui_ro_quy_gan.py) | Bước 5 – Xếp chỗ | Chấm điểm rủi ro mệnh đề bị gán nhầm người và đẩy mệnh đề điểm cao sang mục chưa giải quyết theo ngưỡng. | `src/rui_ro_quy_gan.py` |
| [b5_viet_ban_nhap.py](src/duong_ong/b5_viet_ban_nhap.py) | Bước 5 – Xếp chỗ | Viết bản nháp hồ sơ từ bảng mệnh đề bằng mẫu câu cố định, không dùng mô hình, mỗi mệnh đề vào đúng một mục. | `src/sinh_benh_an.py` |
| [b5_xep_cho_cong_rui_ro.py](src/duong_ong/b5_xep_cho_cong_rui_ro.py) | Bước 5 – Xếp chỗ | Chấm rủi ro lâm sàng từng mệnh đề và quyết định đưa vào thân bản nháp, mục CẦN XÁC NHẬN kèm lý do, hay loại (vẫn lưu vết). | `src/cong_rui_ro.py` |
| [b6_goi_y_hoi_lai.py](src/duong_ong/b6_goi_y_hoi_lai.py) | Bước 6 – Hỏi lại và sửa | Chọn ít câu hỏi nhất (tối đa 3) mà giải quyết được nhiều rủi ro nhất để bác sĩ hỏi lại người bệnh. | `src/hoi_lai.py` |
| [b6_sua_cuc_bo.py](src/duong_ong/b6_sua_cuc_bo.py) | Bước 6 – Hỏi lại và sửa | Kiểm từng câu của bản nháp với bảng mệnh đề và chỉ chuyển chỗ hoặc sửa câu sai, không sinh lại cả bản. | `src/sua_cuc_bo.py` |
| [b7_ban_duyet_html.py](src/duong_ong/b7_ban_duyet_html.py) | Bước 7 – Bản duyệt | Dựng trang duyệt ba cột (lời thoại, mệnh đề, bản nháp) thành một tệp HTML tự chứa, bấm dòng nào tô đoạn lời thoại dẫn của dòng đó. | `src/giao_dien_duyet.py` |
| [chay_duong_ong.py](src/duong_ong/chay_duong_ong.py) | Điều phối | Chạy các nhánh so sánh trên tập ca: A và A+ (mốc đối chứng), các nhánh B, C, D qua đường ống b1–b6, rồi ghi kết quả. | `src/nhanh.py` |
| [chay_nhanh_e.py](src/duong_ong/chay_nhanh_e.py) | Điều phối | Chạy nhánh E: lấy bản nháp của nhánh A, bổ sung chỗ sót và sửa cục bộ bằng bảng mệnh đề, không viết lại bản nháp. | `src/nhanh_e.py` |

### Sinh, nạp và chia dữ liệu — `src/bo_du_lieu/`

Sinh hội thoại khám bệnh mô phỏng và bộ thử thách, nạp dữ liệu ngoài, chia train / phát triển / kiểm tra theo khuôn bệnh.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [bien_the_cau.py](src/bo_du_lieu/bien_the_cau.py) | Bộ sinh | Cho bộ sinh nhiều cách nói khác nhau cho cùng một ý (câu hỏi bác sĩ, lời chào, câu đáp phủ định) để hội thoại bớt lặp câu. | `src/bien_the_cau.py` |
| [ca_mau_bgk.py](src/bo_du_lieu/ca_mau_bgk.py) | Ca mẫu | Dựng sẵn ba ca khám nhiều người nói để nút Xem thử với ca mẫu chạy được khi chưa có kết quả chạy thật. | `src/ca_mau_bgk.py` |
| [chia_bon_tap.py](src/bo_du_lieu/chia_bon_tap.py) | Nạp và chia | Chia bộ hội thoại thành bốn tập tách rời (huấn luyện, phát triển, kiểm tra cuối, kiểm tra chung) để không lộ đề. | `src/tach_tap.py` |
| [chia_tap_theo_khuon.py](src/bo_du_lieu/chia_tap_theo_khuon.py) | Nạp và chia | Chia bộ tự sinh thành huấn luyện, phát triển, kiểm tra cuối THEO KHUÔN BỆNH, để một khuôn chỉ nằm ở một tập, không lộ đề. | `src/tach_tap_viet.py` |
| [dan_gian.py](src/bo_du_lieu/dan_gian.py) | Bộ thử thách | Đổi câu bệnh nhân sang cách nói dân gian, địa phương, ẩn dụ để tạo bộ thử thách, giữ nguyên đáp án lâm sàng. | `src/dan_gian.py` |
| [du_lieu_huan_luyen_trich.py](src/bo_du_lieu/du_lieu_huan_luyen_trich.py) | Nạp và chia | Dựng dữ liệu huấn luyện cho bước rút mệnh đề từ các ca tự sinh: lời thoại vào, mệnh đề đáp án ra. | `src/du_lieu_trich.py` |
| [gan_nhan_truoc.py](src/bo_du_lieu/gan_nhan_truoc.py) | Dữ liệu ngoài | Cho mô hình của dự án gán trước mệnh đề lên câu ViMQ, rồi lọc bằng luật, ra nhãn máy chưa kiểm. | `src/gan_nhan_truoc.py` |
| [kho_khuon.py](src/bo_du_lieu/kho_khuon.py) | Khuôn bệnh | Giữ một danh sách khuôn bệnh duy nhất để bộ sinh, bước chia tập và bộ lọc giới tính cùng nhìn, không lệch nhau. | `src/kho_khuon.py` |
| [khuon_lo_3.py](src/bo_du_lieu/khuon_lo_3.py) | Khuôn bệnh | Chứa lô khuôn bệnh 301–350 (cơ xương khớp, thần kinh cơ, chấn thương chỉnh hình) cho bộ sinh. | `src/khuon_lo_3.py` |
| [khuon_lo_4.py](src/bo_du_lieu/khuon_lo_4.py) | Khuôn bệnh | Chứa lô 50 khuôn bệnh đánh số 351–400 cho bộ sinh, mỗi khuôn có đủ trường bắt buộc và biến thể. | `src/khuon_lo_4.py` |
| [khuon_lo_5.py](src/bo_du_lieu/khuon_lo_5.py) | Khuôn bệnh | Chứa lô khuôn bệnh 401–450 (truyền nhiễm nhiệt đới, ký sinh trùng, lao ngoài phổi, tiêu hoá) cho bộ sinh. | `src/khuon_lo_5.py` |
| [khuon_lo_6.py](src/bo_du_lieu/khuon_lo_6.py) | Khuôn bệnh | Chứa lô khuôn bệnh 451–500 (mắt, tai mũi họng, răng hàm mặt) cho bộ sinh. | `src/khuon_lo_6.py` |
| [khuon_lo_7.py](src/bo_du_lieu/khuon_lo_7.py) | Khuôn bệnh | Chứa lô 50 khuôn bệnh đánh số 501–550 cho bộ sinh, trải nhiều hệ cơ quan. | `src/khuon_lo_7.py` |
| [khuon_lo_8.py](src/bo_du_lieu/khuon_lo_8.py) | Khuôn bệnh | Chứa lô 50 khuôn bệnh đánh số 551–600 cho bộ sinh. | `src/khuon_lo_8.py` |
| [khuon_mo_rong.py](src/bo_du_lieu/khuon_mo_rong.py) | Khuôn bệnh | Gộp các lô khuôn bệnh mở rộng thành một danh sách chung (657 khuôn, 21 hệ cơ quan) cùng bảng giới tính theo khuôn. | `src/khuon_mo_rong.py` |
| [kiem_khuon.py](src/bo_du_lieu/kiem_khuon.py) | Khuôn bệnh | Kiểm khuôn bệnh có hợp lệ không (đủ trường, đúng giới, không trùng nhau quá) trước khi cho vào bộ sinh. | `src/kiem_khuon.py` |
| [loc_nhan_may.py](src/bo_du_lieu/loc_nhan_may.py) | Dữ liệu ngoài | Giữ lại mệnh đề do máy gán trước chỉ khi qua các phép kiểm bằng luật, như có câu trích thật trong lời thoại. | `src/loc_nhan_may.py` |
| [loi_dan_thuong.py](src/bo_du_lieu/loi_dan_thuong.py) | Bộ sinh | Đổi thuật ngữ y khoa trong lời bệnh nhân sang lời dân thường, nhưng đáp án vẫn giữ thuật ngữ lâm sàng. | `src/loi_dan_thuong.py` |
| [nap_bo_gpt500.py](src/bo_du_lieu/nap_bo_gpt500.py) | Dữ liệu ngoài | Chuyển bộ 500 hội thoại phương ngữ do GPT sinh sang định dạng ca của dự án và chấm điểm, chỉ để đo, không để huấn luyện. | `src/bo_gpt500.py` |
| [nap_bo_nguoi_that.py](src/bo_du_lieu/nap_bo_nguoi_that.py) | Dữ liệu ngoài | Đọc bộ hội thoại người thật ghi tay, kiểm lỗi định dạng rồi đổi sang định dạng của bộ sinh để đo. | `src/bo_nguoi_that.py` |
| [nap_du_lieu.py](src/bo_du_lieu/nap_du_lieu.py) | Nạp và chia | Đọc, tách lượt thoại và thống kê bộ hội thoại, đồng thời chặn bằng mã việc chạm tập kiểm tra cuối hay dữ liệu GPT. | `src/du_lieu.py` |
| [nap_vietmed.py](src/bo_du_lieu/nap_vietmed.py) | Dữ liệu ngoài | Đọc bản chép lời VietMed và ghép các dòng liền nhau thành đoạn hội thoại đủ dài cho bước rút. | `src/nap_vietmed.py` |
| [nap_vimq.py](src/bo_du_lieu/nap_vimq.py) | Dữ liệu ngoài | Đọc ViMQ (câu hỏi y tế có nhãn thực thể) và bỏ dấu gạch dưới để thành mẫu cho bước rút. | `src/nap_vimq.py` |
| [ngu_lieu_viet.py](src/bo_du_lieu/ngu_lieu_viet.py) | Bộ sinh | Chứa kho ngữ liệu thô cho bộ sinh: cách xưng hô, người nhà, câu mẫu, triệu chứng và danh sách khuôn bệnh gốc. | `src/ngu_lieu_viet.py` |
| [nhieu_asr.py](src/bo_du_lieu/nhieu_asr.py) | Bộ thử thách | Làm nhiễu lời thoại giống lỗi máy nhận dạng giọng nói (bỏ dấu, sai từ) để thử độ bền, chỉ dùng để đo. | `src/nhieu_asr.py` |
| [phuong_ngu.py](src/bo_du_lieu/phuong_ngu.py) | Bộ sinh | Đổi từ chuẩn sang phương ngữ miền Trung, Nam trong lời thoại và quy ngược về từ chuẩn bằng từ điển. | `src/phuong_ngu.py` |
| [sinh_bo_chan_doan.py](src/bo_du_lieu/sinh_bo_chan_doan.py) | Bộ thử thách | Sinh bộ kiểm tra chẩn đoán lỗi bằng luật, mỗi mẫu cài một bẫy (chủ thể, chắc chắn, đính chính, diễn biến...). | `src/sinh_bo_chan_doan.py` |
| [sinh_bo_thach_thuc.py](src/bo_du_lieu/sinh_bo_thach_thuc.py) | Bộ thử thách | Sinh bốn bộ thử thách theo cặp (đổi người, tự sửa, lỗi chép giọng nói, phương ngữ) bằng luật, từ tập ca sẵn có. | `src/thach_thuc.py` |
| [sinh_ca_da_benh_ly.py](src/bo_du_lieu/sinh_ca_da_benh_ly.py) | Bộ sinh | Sinh ca khám có bệnh chính cộng 1–2 bệnh nền và thuốc nền để tạo hội thoại huấn luyện đa bệnh; không dùng trong luồng khám. | `src/da_benh_ly.py` |
| [sinh_hoi_thoai_viet.py](src/bo_du_lieu/sinh_hoi_thoai_viet.py) | Bộ sinh | Sinh hội thoại khám bệnh tiếng Việt mô phỏng từ khuôn bệnh, kèm bệnh án và đáp án có cấu trúc. | `src/sinh_hoi_thoai_viet.py` |
| [tang_cuong.py](src/bo_du_lieu/tang_cuong.py) | Bộ sinh | Tăng thêm mẫu có người nhà bằng cách biến đổi hội thoại sẵn có, không dùng mô hình ngôn ngữ sinh mới. | `src/tang_cuong.py` |
| [van_tay_bo.py](src/bo_du_lieu/van_tay_bo.py) | Nạp và chia | Ghi vân tay bộ dữ liệu (thế hệ, hạt giống, commit, băm nội dung) để biết bộ nào sinh ra từ mã nào và bắt nhầm bộ. | `src/van_tay_bo.py` |

### Huấn luyện mô hình — `src/huan_luyen/`

Huấn luyện adapter Qwen3 cho bước rút mệnh đề (b1) và chọn mô hình bằng số đo.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [chon_mo_hinh_bakeoff.py](src/huan_luyen/chon_mo_hinh_bakeoff.py) | Chọn mô hình | So các mô hình ở bước rút mệnh đề bằng số đo trên tập phát triển thay vì chọn theo cảm tính. | `src/bakeoff.py` |
| [ham_thuong_rlvr.py](src/huan_luyen/ham_thuong_rlvr.py) | Học tăng cường | Chấm điểm thưởng kiểm chứng được cho một lần trích mệnh đề để dùng trong học tăng cường GRPO. | `src/bo_kiem_tra.py` |
| [huan_luyen_dpo.py](src/huan_luyen/huan_luyen_dpo.py) | Huấn luyện | Tinh chỉnh adapter trích v3 bằng DPO trên các cặp đầu ra đúng và sai khó (thử nghiệm, chưa dùng trong hệ thống). | `src/train_dpo.py` |
| [huan_luyen_sft.py](src/huan_luyen/huan_luyen_sft.py) | Huấn luyện | Huấn luyện có giám sát adapter LoRA cho Qwen3 ở bước rút mệnh đề, và giữ lời nhắc hệ thống dùng chung. | `src/train_baseline.py` |
| [kiem_moi_truong.py](src/huan_luyen/kiem_moi_truong.py) | Huấn luyện | Kiểm nhanh GPU và mô hình có sẵn sàng huấn luyện không: nạp 4-bit, tắt thinking, mặt nạ nhãn, sinh tiếng Việt. | `src/kiem_mo_hinh.py` |
| [loss_theo_doan.py](src/huan_luyen/loss_theo_doan.py) | Huấn luyện | Tính loss cross-entropy theo từng đoạn chuỗi để hạ đỉnh VRAM khi huấn luyện chuỗi dài. | `src/loss_theo_doan.py` |

### Đo lường và chấm điểm — `src/do_luong/`

Sinh mọi con số trong báo cáo: cham_* là bộ chấm, do_* là các phép đo.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [bit_nhan.py](src/do_luong/bit_nhan.py) | Phép đo | Kiểm mô hình gán chủ thể là hiểu thật hay chỉ đoán theo người vừa nói, bằng cách bịt nhãn người nói rồi so với bản gốc. | `src/bit_nhan.py` |
| [cham_chu_the.py](src/do_luong/cham_chu_the.py) | Bộ chấm | In ra từng phát biểu cùng nguyên văn lượt dẫn chứng để người chấm tay trường chủ thể, vì bộ đếm tự động sẽ chấm nhầm người nhà. | `src/cham_chu_the.py` |
| [cham_diem.py](src/do_luong/cham_diem.py) | Bộ chấm | Chấm độ giống giữa bản nháp và bản tham chiếu bằng ROUGE và Section F1, tách từ theo âm tiết tiếng Việt. | `src/cham_diem.py` |
| [cham_he_thong.py](src/do_luong/cham_he_thong.py) | Bộ chấm | Chấm từng mệnh đề đường ống rút ra so với đáp án có cấu trúc: sai người, sai mức, bịa, bỏ sót, và lượt sai đầu tiên. | `src/cham_he_thong.py` |
| [cham_lai_bang_quy_gan.py](src/do_luong/cham_lai_bang_quy_gan.py) | Bộ chấm | Chấm lại các nhánh bằng điểm quy gán trên đúng đầu ra đã sinh, để xem kết luận C không hơn B có do thước đo mù không. | `src/cham_lai_bang_quy_gan.py` |
| [cham_muc_thach_thuc.py](src/do_luong/cham_muc_thach_thuc.py) | Bộ chấm | Chấm bốn bộ thử thách trực tiếp trên văn bản bản nháp, để nhánh A (văn xuôi, không có bảng mệnh đề) cũng được so công bằng. | `src/cham_muc_thach_thuc.py` |
| [chuan_dinh_dang.py](src/do_luong/chuan_dinh_dang.py) | Bộ chấm | Đổi các kiểu viết tiêu đề mục khác nhau về tên mục chuẩn trước khi chấm, để cách trình bày không làm sai điểm Section F1. | `src/chuan_dinh_dang.py` |
| [chung_chi_thuoc_do.py](src/do_luong/chung_chi_thuoc_do.py) | Thước đo | Kiểm điểm quy gán có đủ nhạy với lỗi đổi chủ thể mà không quá nhạy với đổi từ đồng nghĩa, trên bệnh án thật. | `src/chung_chi_thuoc_do.py` |
| [danh_gia_khoa.py](src/do_luong/danh_gia_khoa.py) | Thước đo | Đo tầng khoá bằng chứng chặn oan bao nhiêu trên đáp án hoàn hảo và bắt được bao nhiêu lỗi cấy có chủ định. | `src/danh_gia_khoa.py` |
| [dau_vet_nguon.py](src/do_luong/dau_vet_nguon.py) | Chất lượng dữ liệu | Đếm các dấu vết nguồn gốc trong bộ hội thoại để biết nó có phải bản dịch từ tiếng Anh không, bằng số chứ không bằng phỏng đoán. | `src/dau_vet_nguon.py` |
| [do_bit_nhan.py](src/do_luong/do_bit_nhan.py) | Phép đo | Chạy phép thử bịt nhãn người nói với mô hình trên GPU để đo tỉ lệ chủ thể chỉ đúng nhờ đoán theo người nói. | `src/do_bit_nhan.py` |
| [do_bo_chan_doan.py](src/do_luong/do_bo_chan_doan.py) | Phép đo | Đo mô hình có sa vào từng bẫy của bộ chẩn đoán không (gán dị ứng sai người, nâng bệnh nghi thành chắc...), chấm tự động. | `src/do_bo_chan_doan.py` |
| [do_bo_sot.py](src/do_luong/do_bo_sot.py) | Phép đo | Đo tỉ lệ mệnh đề của đáp án mà bước rút không rút ra được, để trả lời câu giảm bỏ sót thông tin quan trọng bằng số. | `src/do_bo_sot.py` |
| [do_canh_bao.py](src/do_luong/do_canh_bao.py) | Phép đo | Đo lớp cảnh báo báo đúng bao nhiêu và bắt được bao nhiêu lỗi so với bộ chấm tự động, so chính sách C với D trên tập phát triển. | `src/do_canh_bao.py` |
| [do_cay_loi.py](src/do_luong/do_cay_loi.py) | Phép đo | Đo lớp cảnh báo có bắt đúng chỗ, đúng nhóm một lỗi cấy nhân tạo vào đáp án không, và báo nhầm bao nhiêu trên bản sạch. | `src/do_cay_loi.py` |
| [do_dac.py](src/do_luong/do_dac.py) | Phép đo | So các nhánh trên năm mặt chất lượng (điểm cuối, Section F1, bỏ sót, cần xác nhận, chi phí) và kiểm nhánh mới không giảm lỗi nhờ viết ít. | `src/do_dac.py` |
| [do_dan_gian.py](src/do_luong/do_dan_gian.py) | Phép đo | Đo bộ thử thách dân gian theo cặp A và B: nói chữ khác mà nghĩa không đổi thì hệ thống có chặn, cảnh báo hay tự chọn nghĩa không. | `src/do_dan_gian.py` |
| [do_lap_cau.py](src/do_luong/do_lap_cau.py) | Chất lượng dữ liệu | Đo độ lặp câu và độ đa dạng từ vựng của bộ hội thoại bằng một định nghĩa cố định, để so bộ cũ với bộ mới cùng một thước. | `src/do_lap_cau.py` |
| [do_neu_ten.py](src/do_luong/do_neu_ten.py) | Phép đo | Đo bản nháp có nêu tên người (mẹ, bố...) cho các câu thuộc mục không phải của bệnh nhân hay chỉ xếp đúng mục mà quên nêu người. | `src/do_neu_ten.py` |
| [do_quan_he.py](src/do_luong/do_quan_he.py) | Phép đo | Đo phát hiện quan hệ bằng bốn số đúng, thừa, sót, nhầm loại thay vì một số, so với đáp án cấu trúc. | `src/do_quan_he.py` |
| [do_tang_quan_he.py](src/do_luong/do_tang_quan_he.py) | Phép đo | Đếm cặp quan hệ ứng viên mà chương trình liệt kê trên dữ liệu thật và bộ chẩn đoán, để xem cơ chế quan hệ có khai hoa không. | `src/do_tang_quan_he.py` |
| [do_tang_quy_gan.py](src/do_luong/do_tang_quy_gan.py) | Phép đo | Chấm quy gán riêng từng tầng độ khó (bác sĩ, bệnh nhân, kể hộ, kể về mình), vì số gộp không thấy được tầng người nhà. | `src/do_tang_quy_gan.py` |
| [do_trich.py](src/do_luong/do_trich.py) | Phép đo | Đo trực tiếp bước rút mệnh đề: tìm thấy bao nhiêu mệnh đề đáp án, gán đúng người bao nhiêu, riêng mệnh đề ngoài bệnh nhân. | `src/do_trich.py` |
| [do_van_xuoi.py](src/do_luong/do_van_xuoi.py) | Phép đo | Đo một bệnh án văn xuôi trên bộ chẩn đoán có mắc đúng lỗi bẫy không, không dùng thước đo nào, để so nhánh A với nhánh C. | `src/do_van_xuoi.py` |
| [do_vidia2std.py](src/do_luong/do_vidia2std.py) | Phép đo | Đo bảng chuẩn hoá phương ngữ đổi đúng bao nhiêu chỗ khác biệt trên câu thật ViDia2Std, không phải đo hiểu lời bệnh nhân. | `src/do_vidia2std.py` |
| [doi_chung_context_vi.py](src/do_luong/doi_chung_context_vi.py) | Đối chứng | Gán chủ thể (bệnh nhân hay người khác) bằng luật kiểu ConText: từ kích hoạt, kích hoạt giả, hết phạm vi, không dùng mô hình. | `src/context_vi.py` |
| [doi_chung_tam_thuong.py](src/do_luong/doi_chung_tam_thuong.py) | Đối chứng | Dựng hai đường tắt không dùng mô hình (chủ thể là người nói, chủ thể luôn là bệnh nhân) để xem hệ thống thật có hơn cả hai. | `src/doi_chung_tam_thuong.py` |
| [duong_danh_doi.py](src/do_luong/duong_danh_doi.py) | Thống kê | Vẽ đường đánh đổi giữa lỗi và bỏ sót khi vặn ngưỡng rủi ro quy gán, chấm trên thân bài mà bác sĩ đọc như sự thật. | `src/duong_danh_doi.py` |
| [khoang_tin_cay.py](src/do_luong/khoang_tin_cay.py) | Thống kê | Tính khoảng tin cậy bootstrap theo ca và theo khuôn bệnh, và so cặp các nhánh, để biết chênh lệch có vượt nhiễu không. | `src/sai_so.py` |
| [kiem_nghiem_ngoai_khuon.py](src/do_luong/kiem_nghiem_ngoai_khuon.py) | Chất lượng dữ liệu | Kiểm hai điều: tập train và test không trùng khuôn, và hệ thống còn đúng trên 10 kịch bản lâm sàng hoàn toàn ngoài khuôn. | `src/kiem_nghiem_ngoai_khuon.py` |
| [kiem_thu_dot_bien.py](src/do_luong/kiem_thu_dot_bien.py) | Kiểm thử | Cấy 5 họ lỗi lâm sàng nguy hiểm vào ca hợp lệ rồi đếm các cổng chặn (khoá K1–K7, cổng rủi ro) bắt được bao nhiêu. | `src/kiem_thu_dot_bien.py` |
| [nguon_lap_cau.py](src/do_luong/nguon_lap_cau.py) | Chất lượng dữ liệu | Truy mỗi câu lặp của bộ hội thoại về chỗ sinh ra nó trong bộ sinh: nhóm câu, mẫu f-string, câu cố định hay ghép. | `src/nguon_lap_cau.py` |
| [quet_an_toan_duoc_ly_v2.py](src/do_luong/quet_an_toan_duoc_ly_v2.py) | Chất lượng dữ liệu | Quét bộ dữ liệu v2 tìm tương tác thuốc nguy hiểm, dị ứng người nhà bị gán cho bệnh nhân, đính chính hỏng và trích dẫn sai. | `src/quet_an_toan_duoc_ly_v2.py` |
| [thuoc_do_quy_gan.py](src/do_luong/thuoc_do_quy_gan.py) | Thước đo | Đo mệnh đề có được gán đúng người không: ghép theo nội dung trước, rồi đếm cặp khớp luôn chủ thể, thứ ROUGE không thấy. | `src/thuoc_do_quy_gan.py` |

### Công cụ lâm sàng hỗ trợ bác sĩ — `src/cong_cu_lam_sang/`

Công cụ trong menu Công cụ quanh bản nháp (BHYT, thuốc, xét nghiệm, giấy tờ). Chỉ là gợi ý, không đổi cách dựng bản nháp; bảng tri thức chưa được chuyên gia duyệt.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [cam_doan_thu_thuat.py](src/cong_cu_lam_sang/cam_doan_thu_thuat.py) | Giấy tờ | Kiểm xem trước thủ thuật bác sĩ đã giải thích đủ các ý pháp lý cho người bệnh chưa, có căn cứ ở câu nào trong hội thoại. | `src/cam_doan_thu_thuat.py` |
| [canh_bao_tuong_tac_thuoc.py](src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py) | Thuốc | Cảnh báo bác sĩ khi các thuốc trong đơn tương tác với nhau, chống chỉ định theo bệnh nền hoặc vượt liều trần. | `src/duoc_ly_lam_sang.py` |
| [chuan_hoa_don_vi_xet_nghiem.py](src/cong_cu_lam_sang/chuan_hoa_don_vi_xet_nghiem.py) | Xét nghiệm | Đổi creatinin, glucose, urea giữa các đơn vị khác nhau về một đơn vị chung để các công cụ khác so được. | `src/chuan_hoa_don_vi_xet_nghiem.py` |
| [di_buong_noi_tru.py](src/cong_cu_lam_sang/di_buong_noi_tru.py) | Giấy tờ | So lời bệnh nhân và y lệnh hôm nay với hôm qua trong hồ sơ nội trú, chỉ ra triệu chứng, sinh hiệu, thuốc thay đổi để ghi tờ điều trị. | `src/di_buong_noi_tru.py` |
| [di_ung_cheo.py](src/cong_cu_lam_sang/di_ung_cheo.py) | Thuốc | Kiểm thuốc trong đơn có cùng nhóm với thuốc người bệnh từng dị ứng, theo hoạt chất, nhóm ATC và nhóm hoá học. | `src/di_ung_cheo.py` |
| [doc_phieu_xet_nghiem.py](src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py) | Xét nghiệm | Lấy chỉ số xét nghiệm và thuốc từ văn bản phiếu hoặc đơn cũ, rồi quy đổi đơn vị và tính eGFR, đối soát ngưỡng. | `src/ocr_lam_sang.py` |
| [doi_soat_can_lam_sang.py](src/cong_cu_lam_sang/doi_soat_can_lam_sang.py) | Xét nghiệm | So chỉ số xét nghiệm với ngưỡng bình thường theo tuổi, giới và báo giá trị nguy kịch hoặc không khớp với lời bệnh nhân. | `src/can_lam_sang.py` |
| [goi_y_cau_hoi_socrates.py](src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py) | Trong lúc khám | Tìm điểm còn thiếu trong phần hỏi bệnh theo khung SOCRATES và gợi ý bác sĩ hỏi thêm câu nào. | `src/tro_ly_lam_sang.py` |
| [hieu_chinh_lieu.py](src/cong_cu_lam_sang/hieu_chinh_lieu.py) | Thuốc | Gợi ý chỉnh liều thuốc theo chức năng thận (CrCl, eGFR) và bệnh gan nền của người bệnh. | `src/hieu_chinh_lieu.py` |
| [ho_so_benh_nhan_qr.py](src/cong_cu_lam_sang/ho_so_benh_nhan_qr.py) | Giấy tờ | Gói thuốc, dặn dò và dấu hiệu cần quay lại khám thành một hồ sơ nhỏ ký HMAC để người bệnh quét mã QR mang về. | `src/ho_so_benh_nhan_qr.py` |
| [kiem_toan_xml_bhyt.py](src/cong_cu_lam_sang/kiem_toan_xml_bhyt.py) | BHYT | Rà gói XML1–XML5 của một lượt khám để tìm lỗi dễ bị giám định BHYT từ chối trước khi gửi cổng. | `src/kiem_toan_xml_bhyt.py` |
| [nap_ket_qua_lis_hl7.py](src/cong_cu_lam_sang/nap_ket_qua_lis_hl7.py) | Xét nghiệm | Đọc kết quả xét nghiệm từ hệ thống LIS ở dạng HL7, JSON hoặc CSV và đưa về dict chỉ số có mã chuẩn. | `src/lis_hl7_oru.py` |
| [quy_dao_nhieu_lan_kham.py](src/cong_cu_lam_sang/quy_dao_nhieu_lan_kham.py) | Xét nghiệm | So xét nghiệm và thuốc qua nhiều lần khám để thấy chỉ số tăng giảm, tổn thương thận cấp và thuốc dùng kéo dài. | `src/quy_dao_lam_sang.py` |
| [thang_diem_nguy_co.py](src/cong_cu_lam_sang/thang_diem_nguy_co.py) | Thang điểm | Tính các thang điểm lâm sàng thường dùng như CURB-65, CHA2DS2-VASc, Wells, GCS, Child-Pugh, BMI từ dữ kiện đã có. | `src/thang_diem_lam_sang.py` |
| [tien_kiem_bhyt_va_khoi_phuc_bo_sot.py](src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py) | BHYT | Tiền kiểm hồ sơ trước khi gửi BHYT, gợi ý mã ICD-10, và quét hội thoại tìm mục quan trọng chưa vào bản nháp. | `src/kiem_duyet_bhyt_va_bo_sot.py` |
| [to_dan_do_benh_nhan.py](src/cong_cu_lam_sang/to_dan_do_benh_nhan.py) | Giấy tờ | Soạn tờ dặn dò bằng lời dễ hiểu cho người bệnh: lịch uống thuốc, việc cần làm, dấu hiệu phải quay lại. | `src/dan_do_benh_nhan.py` |
| [tra_duoc_thu_aho_corasick.py](src/cong_cu_lam_sang/tra_duoc_thu_aho_corasick.py) | Tri thức | Tìm nhanh tên thuốc trong văn bản và tra thông tin Dược thư Quốc gia, chạy tại chỗ không cần mạng. | `src/aho_corasick_duoc_thu.py` |
| [tri_thuc_thuoc.py](src/cong_cu_lam_sang/tri_thuc_thuoc.py) | Tri thức | Đọc bảng tri thức thuốc dùng chung (tên, hoạt chất, liều tối đa) từ tệp dữ liệu; bảng này chưa được chuyên gia duyệt. | `src/tri_thuc_thuoc.py` |
| [tu_dien_phuong_ngu_lam_sang.py](src/cong_cu_lam_sang/tu_dien_phuong_ngu_lam_sang.py) | Tri thức | Đổi cách nói địa phương và khẩu ngữ của người bệnh ba miền sang thuật ngữ y khoa, vẫn giữ vết từ gốc. | `src/phuong_ngu_lam_sang.py` |
| [xuat_fhir_r4.py](src/cong_cu_lam_sang/xuat_fhir_r4.py) | Liên thông | Chuyển bản nháp hồ sơ khám thành gói FHIR R4 để chuyển sang hệ thống khác. | `src/fhir_exporter.py` |

### Dịch vụ, an toàn và minh bạch — `src/he_thong/`

Dịch vụ HTTP mà web gọi vào, cùng các phần an toàn: khử định danh, rào chắn, nhật ký ký duyệt WORM, khai mã nguồn.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [dich_vu_http.py](src/he_thong/dich_vu_http.py) | Dịch vụ | Chạy dịch vụ HTTP tại chỗ để giao diện chép lời, dựng bản nháp hồ sơ mà không gửi hội thoại ra internet. | `src/dich_vu.py` |
| [dieu_phoi_cac_chot_an_toan.py](src/he_thong/dieu_phoi_cac_chot_an_toan.py) | Dịch vụ | Nối các chốt an toàn lâm sàng thành một đường chạy và ghi vết từng chốt để kiểm toán được. | `src/dieu_phoi_ha_tang.py` |
| [duong_dan.py](src/he_thong/duong_dan.py) | Cấu hình | Khai báo tập trung các đường dẫn thư mục dữ liệu, mô hình và kết quả để nơi khác không ghi cứng. | `src/duong_dan.py` |
| [ep_kieu_dau_vao.py](src/he_thong/ep_kieu_dau_vao.py) | An toàn | Ép dữ liệu thô từ JSON/HTTP về kiểu đúng để lỗi nhập liệu không làm hỏng các bước sau. | `src/ep_kieu_dau_vao.py` |
| [hop_dong_api.py](src/he_thong/hop_dong_api.py) | Dịch vụ | Định nghĩa hình dạng dữ liệu mà dịch vụ Python trả về để máy chủ và giao diện TypeScript hiểu cùng một hợp đồng. | `src/api_contract.py` |
| [khai_ma_nguon.py](src/he_thong/khai_ma_nguon.py) | Minh bạch | Lập bảng khai tệp mã nguồn nào do AI viết, sửa mấy lần và theo lời nhắc nào, để minh bạch phần AI. | `src/khai_ma_nguon.py` |
| [khu_dinh_danh.py](src/he_thong/khu_dinh_danh.py) | An toàn | Tìm và che thông tin định danh cá nhân (tên, CCCD, số điện thoại, BHYT) trước khi văn bản đi tiếp. | `src/khu_dinh_danh.py` |
| [nhat_ky_ky_duyet_worm.py](src/he_thong/nhat_ky_ky_duyet_worm.py) | An toàn | Ghi nhật ký ký duyệt chỉ thêm, không sửa xoá, nối các dòng bằng chuỗi băm SHA-256 để phát hiện can thiệp. | `src/worm_audit_log.py` |
| [nhat_ky_loi_nhac.py](src/he_thong/nhat_ky_loi_nhac.py) | Minh bạch | Trích các lời nhắc của người dùng dẫn tới sửa mã nguồn từ bản ghi phiên làm việc, che thông tin nhạy cảm. | `src/nhat_ky_loi_nhac.py` |
| [rao_chan_an_toan.py](src/he_thong/rao_chan_an_toan.py) | An toàn | Chặn đầu ra không an toàn bằng nhiều tầng kiểm: chất lượng chép lời, nhất quán người nói, hành vi hội thoại, bằng chứng, an toàn lâm sàng. | `src/guardrails.py` |

### Lớp cảnh báo — `src/canh_bao/`

| Tệp | Làm gì |
|---|---|
| [phat_hien.py](src/canh_bao/phat_hien.py) | Phát hiện lỗi theo từng mệnh đề so với lời thoại: sai người, đảo phủ định, sai số, sai bên trái/phải, sai mức độ, nhầm thời điểm. |
| [toan_ca.py](src/canh_bao/toan_ca.py) | Cảnh báo ở mức cả ca: thông tin bị bỏ sót, mâu thuẫn giữa các dòng, giá trị đã bị đính chính mà vẫn giữ, ghi lặp. |
| [bo_sot.py](src/canh_bao/bo_sot.py) | Tìm những đoạn hội thoại có thông tin lâm sàng mà bản nháp chưa ghi, dùng chung cho cả hệ thống. |
| [lam_sang.py](src/canh_bao/lam_sang.py) | Cảnh báo theo kiến thức lâm sàng: liều vượt trần ngày, tương tác thuốc, kê thuốc cho người đang dị ứng. |
| [asr.py](src/canh_bao/asr.py) | Cảnh báo dòng bản nháp có thể sai vì lỗi chép giọng nói, tách riêng do xảy ra trước bước mô hình. |
| [gop.py](src/canh_bao/gop.py) | Chạy mọi bộ phát hiện, gộp cảnh báo trùng, chọn cảnh báo chính và áp chính sách D để quyết định dòng nào bị chặn. |
| [loai.py](src/canh_bao/loai.py) | Định nghĩa chung của lớp cảnh báo: các loại lỗi, cấu trúc một cảnh báo và mức nghiêm trọng. |
| [loi_noi.py](src/canh_bao/loi_noi.py) | Chuẩn hoá lời nói tiếng Việt cho các luật: tách ý, nhận câu hỏi, bỏ từ đệm. |
| [so_lieu.py](src/canh_bao/so_lieu.py) | Tách con số kèm đơn vị trong câu tiếng Việt để so số ghi trong bản nháp với số được nói. |
| [nhat_ky.py](src/canh_bao/nhat_ky.py) | Ghi các cảnh báo ra tệp nhật ký từng dòng để phục vụ nghiên cứu sau này. |

### Âm thanh — `src/audio/`

| Tệp | Làm gì |
|---|---|
| [pipeline.py](src/audio/pipeline.py) | Điều phối một phiên âm thanh từ ghi âm đến lời thoại chờ duyệt, qua các bước chuyển định dạng, chép, tách người nói, căn khớp. |
| [asr/phowhisper_provider.py](src/audio/asr/phowhisper_provider.py) | Chép lời tiếng Việt bằng PhoWhisper chạy tại chỗ, là bộ chép chính của hệ thống. |
| [asr/faster_whisper_provider.py](src/audio/asr/faster_whisper_provider.py) | Chép lời bằng faster-whisper làm mốc so sánh với bộ chép chính. |
| [asr/registry.py](src/audio/asr/registry.py) | Chọn bộ chép lời theo tên trong cấu hình để đổi nhà cung cấp mà không sửa mã. |
| [asr/critical_tokens.py](src/audio/asr/critical_tokens.py) | Lấy ra các từ lâm sàng dễ sai nghĩa (thuốc, liều, phủ định, ai) từ bản chép để so hai bản chép với nhau. |
| [asr/disagreement.py](src/audio/asr/disagreement.py) | Chạy so hai bộ chép lời và chọn ra những đoạn hai bên bất đồng ở từ quan trọng để người duyệt xem kỹ. |
| [asr/bench_metrics.py](src/audio/asr/bench_metrics.py) | Đo chất lượng chép lời bằng tỷ lệ sai từ và tỷ lệ sai từ khoá lâm sàng để so các bộ chép. |
| [pyannote_provider.py](src/audio/pyannote_provider.py) | Tách người nói bằng pyannote bằng cách gọi tiến trình con trong môi trường Python riêng, có giới hạn bộ nhớ. |
| [alignment.py](src/audio/alignment.py) | Gán người nói cho từng đoạn chép lời bằng cách đối chiếu mốc thời gian, không đổi chữ đã chép. |
| [adapter.py](src/audio/adapter.py) | Đổi bản chép lời đã được duyệt sang dạng hội thoại mà đường ống dựng bản nháp đọc được. |
| [preprocessing.py](src/audio/preprocessing.py) | Đưa âm thanh về WAV 16 kHz mono để bộ chép dùng, vẫn giữ nguyên tệp gốc. |
| [storage.py](src/audio/storage.py) | Lưu phiên âm thanh vào đĩa tại chỗ, bền vững qua các lần chạy, kèm nhật ký sự kiện để kiểm toán. |
| [api.py](src/audio/api.py) | Mở máy chủ HTTP nhỏ để tải ghi âm lên, xử lý và cho bác sĩ duyệt, sửa lời thoại trên trình duyệt. |
| [sim2real_v2.py](src/audio/sim2real_v2.py) | Mô phỏng nhiễu, vọng, mất gói trên chữ để thử độ bền chép lời với bộ dữ liệu v2; là mô phỏng, không phải đo ASR thật. |

### Giao diện và máy chủ web — `web/`

| Đường dẫn | Làm gì |
|---|---|
| `web/server.ts` | Máy chủ Node: nối giao diện với lõi Python và các route bên dưới. |
| `web/may-chu/routes/` | Các API: ca khám, ký duyệt (sign-off), ASR, BHYT/OCR, công cụ lâm sàng (boost), cổng người bệnh, quản trị, tra cứu, trợ lý, mô hình ngoài. |
| `web/may-chu/routes/llm-ngoai.ts` | Cổng gọi mô hình AI bên ngoài: mặc định tắt, có giới hạn tần suất, không dùng để viết bản nháp. |
| `web/may-chu/tro-ly/` | Trợ lý nhiều tác tử: điều phối (dieu-phoi.ts), tác tử tại chỗ, ẩn danh dữ liệu trước khi gửi ra ngoài (an-danh.ts). |
| `web/may-chu/tra-cuu/` | Tra cứu tài liệu y khoa từ nguồn công khai, phác đồ Bộ Y tế, từ điển, kiểm định số liệu. |
| `web/may-chu/worm.ts` | Nhật ký ký duyệt chỉ-ghi-thêm có chuỗi băm (phía web). |
| `web/may-chu/csdl.ts, tai-khoan.ts, hang-doi.ts` | Cơ sở dữ liệu SQLite theo người dùng, tài khoản mã mời, hàng đợi việc nền. |
| `web/src/components/` | Các màn hình React: soạn bản nháp, duyệt bên cạnh, các hộp công cụ (BHYT, SBAR, cam đoan, đi buồng, dặn dò…). |
| `web/src/lib/` | Logic phía giao diện: ký duyệt (kyDuyet.ts), ghép bản nháp hiệu lực, SBAR, câu hỏi cờ đỏ, đối chiếu lần khám trước, tô sáng ASR. |

### Các thư mục khác

| Thư mục | Nội dung |
|---|---|
| `tests/` | Phép thử tự động (`python -m pytest tests`). |
| `tools/` | Script chạy thí nghiệm, đo đạc, dựng báo cáo. |
| `kaggle-kernels/` | Kernel chạy huấn luyện/đo trên GPU Kaggle. |
| `data/` | Bộ dữ liệu mô phỏng, manifest đóng băng, bảng tri thức thuốc (chưa duyệt). |
| `docs/` | Tài liệu, báo cáo kết quả, báo cáo cải tiến. |
| `trien-khai/` | Cấu hình triển khai. |

## Đối chiếu tên cũ (trước 27/11/2026)

Ngày 27/11/2026 toàn bộ mã Python được xếp vào thư mục con và đổi tên cho dễ hiểu; tên cũ không còn trong `src/`. Các bản ghi lịch sử (nhật ký lệnh, kê khai mã nguồn, minh chứng, tiến độ theo ngày, bản đã nộp trong `docs/final/` và các tệp .docx) được giữ nguyên như lúc viết nên vẫn ghi tên cũ — tra bảng dưới để biết tệp đó nay ở đâu.

- Lệnh chạy: `python -m src.<thư_mục>.<tên_mới>`, ví dụ `python -m src.duong_ong.chay_duong_ong --nhanh C …`.
- Lịch sử git đầy đủ của một tệp (gồm cả thời tên cũ): `git log --follow src/<thư_mục>/<tên_mới>.py`.

| Tên cũ | Tên mới |
|---|---|
| `src/aho_corasick_duoc_thu.py` | `src/cong_cu_lam_sang/tra_duoc_thu_aho_corasick.py` |
| `src/api_contract.py` | `src/he_thong/hop_dong_api.py` |
| `src/bakeoff.py` | `src/huan_luyen/chon_mo_hinh_bakeoff.py` |
| `src/bien_the_cau.py` | `src/bo_du_lieu/bien_the_cau.py` |
| `src/bit_nhan.py` | `src/do_luong/bit_nhan.py` |
| `src/bo_gpt500.py` | `src/bo_du_lieu/nap_bo_gpt500.py` |
| `src/bo_kiem_tra.py` | `src/huan_luyen/ham_thuong_rlvr.py` |
| `src/bo_nguoi_that.py` | `src/bo_du_lieu/nap_bo_nguoi_that.py` |
| `src/ca_mau_bgk.py` | `src/bo_du_lieu/ca_mau_bgk.py` |
| `src/cam_doan_thu_thuat.py` | `src/cong_cu_lam_sang/cam_doan_thu_thuat.py` |
| `src/can_lam_sang.py` | `src/cong_cu_lam_sang/doi_soat_can_lam_sang.py` |
| `src/cap_nhat.py` | `src/duong_ong/b3_cap_nhat_trang_thai.py` |
| `src/cham_chu_the.py` | `src/do_luong/cham_chu_the.py` |
| `src/cham_diem.py` | `src/do_luong/cham_diem.py` |
| `src/cham_he_thong.py` | `src/do_luong/cham_he_thong.py` |
| `src/cham_lai_bang_quy_gan.py` | `src/do_luong/cham_lai_bang_quy_gan.py` |
| `src/cham_muc_thach_thuc.py` | `src/do_luong/cham_muc_thach_thuc.py` |
| `src/chuan_dinh_dang.py` | `src/do_luong/chuan_dinh_dang.py` |
| `src/chuan_hoa.py` | `src/duong_ong/b0_chuan_hoa_phuong_ngu.py` |
| `src/chuan_hoa_don_vi_xet_nghiem.py` | `src/cong_cu_lam_sang/chuan_hoa_don_vi_xet_nghiem.py` |
| `src/chung_chi_thuoc_do.py` | `src/do_luong/chung_chi_thuoc_do.py` |
| `src/cong_rui_ro.py` | `src/duong_ong/b5_xep_cho_cong_rui_ro.py` |
| `src/context_vi.py` | `src/do_luong/doi_chung_context_vi.py` |
| `src/da_benh_ly.py` | `src/bo_du_lieu/sinh_ca_da_benh_ly.py` |
| `src/dan_do_benh_nhan.py` | `src/cong_cu_lam_sang/to_dan_do_benh_nhan.py` |
| `src/dan_gian.py` | `src/bo_du_lieu/dan_gian.py` |
| `src/danh_gia_khoa.py` | `src/do_luong/danh_gia_khoa.py` |
| `src/dau_vet_nguon.py` | `src/do_luong/dau_vet_nguon.py` |
| `src/di_buong_noi_tru.py` | `src/cong_cu_lam_sang/di_buong_noi_tru.py` |
| `src/di_ung_cheo.py` | `src/cong_cu_lam_sang/di_ung_cheo.py` |
| `src/dich_vu.py` | `src/he_thong/dich_vu_http.py` |
| `src/dieu_phoi_ha_tang.py` | `src/he_thong/dieu_phoi_cac_chot_an_toan.py` |
| `src/do_bit_nhan.py` | `src/do_luong/do_bit_nhan.py` |
| `src/do_bo_chan_doan.py` | `src/do_luong/do_bo_chan_doan.py` |
| `src/do_bo_sot.py` | `src/do_luong/do_bo_sot.py` |
| `src/do_canh_bao.py` | `src/do_luong/do_canh_bao.py` |
| `src/do_cay_loi.py` | `src/do_luong/do_cay_loi.py` |
| `src/do_dac.py` | `src/do_luong/do_dac.py` |
| `src/do_dan_gian.py` | `src/do_luong/do_dan_gian.py` |
| `src/do_lap_cau.py` | `src/do_luong/do_lap_cau.py` |
| `src/do_neu_ten.py` | `src/do_luong/do_neu_ten.py` |
| `src/do_quan_he.py` | `src/do_luong/do_quan_he.py` |
| `src/do_tang_quan_he.py` | `src/do_luong/do_tang_quan_he.py` |
| `src/do_tang_quy_gan.py` | `src/do_luong/do_tang_quy_gan.py` |
| `src/do_trich.py` | `src/do_luong/do_trich.py` |
| `src/do_van_xuoi.py` | `src/do_luong/do_van_xuoi.py` |
| `src/do_vidia2std.py` | `src/do_luong/do_vidia2std.py` |
| `src/doan_van.py` | `src/duong_ong/b0_cat_doan_van.py` |
| `src/doi_chung_tam_thuong.py` | `src/do_luong/doi_chung_tam_thuong.py` |
| `src/du_lieu.py` | `src/bo_du_lieu/nap_du_lieu.py` |
| `src/du_lieu_trich.py` | `src/bo_du_lieu/du_lieu_huan_luyen_trich.py` |
| `src/duoc_ly_lam_sang.py` | `src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py` |
| `src/duong_dan.py` | `src/he_thong/duong_dan.py` |
| `src/duong_danh_doi.py` | `src/do_luong/duong_danh_doi.py` |
| `src/ep_kieu_dau_vao.py` | `src/he_thong/ep_kieu_dau_vao.py` |
| `src/fhir_exporter.py` | `src/cong_cu_lam_sang/xuat_fhir_r4.py` |
| `src/gan_nhan_truoc.py` | `src/bo_du_lieu/gan_nhan_truoc.py` |
| `src/giao_dien_duyet.py` | `src/duong_ong/b7_ban_duyet_html.py` |
| `src/guardrails.py` | `src/he_thong/rao_chan_an_toan.py` |
| `src/hieu_chinh_lieu.py` | `src/cong_cu_lam_sang/hieu_chinh_lieu.py` |
| `src/ho_so_benh_nhan_qr.py` | `src/cong_cu_lam_sang/ho_so_benh_nhan_qr.py` |
| `src/hoi_lai.py` | `src/duong_ong/b6_goi_y_hoi_lai.py` |
| `src/khai_ma_nguon.py` | `src/he_thong/khai_ma_nguon.py` |
| `src/kho_khuon.py` | `src/bo_du_lieu/kho_khuon.py` |
| `src/khoa_bang_chung.py` | `src/duong_ong/b4_kiem_can_cu.py` |
| `src/khu_dinh_danh.py` | `src/he_thong/khu_dinh_danh.py` |
| `src/khuon_lo_3.py` | `src/bo_du_lieu/khuon_lo_3.py` |
| `src/khuon_lo_4.py` | `src/bo_du_lieu/khuon_lo_4.py` |
| `src/khuon_lo_5.py` | `src/bo_du_lieu/khuon_lo_5.py` |
| `src/khuon_lo_6.py` | `src/bo_du_lieu/khuon_lo_6.py` |
| `src/khuon_lo_7.py` | `src/bo_du_lieu/khuon_lo_7.py` |
| `src/khuon_lo_8.py` | `src/bo_du_lieu/khuon_lo_8.py` |
| `src/khuon_mo_rong.py` | `src/bo_du_lieu/khuon_mo_rong.py` |
| `src/kiem_day_du.py` | `src/duong_ong/b4_kiem_day_du.py` |
| `src/kiem_duyet_bhyt_va_bo_sot.py` | `src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py` |
| `src/kiem_khuon.py` | `src/bo_du_lieu/kiem_khuon.py` |
| `src/kiem_mo_hinh.py` | `src/huan_luyen/kiem_moi_truong.py` |
| `src/kiem_nghiem_ngoai_khuon.py` | `src/do_luong/kiem_nghiem_ngoai_khuon.py` |
| `src/kiem_thu_dot_bien.py` | `src/do_luong/kiem_thu_dot_bien.py` |
| `src/kiem_toan_xml_bhyt.py` | `src/cong_cu_lam_sang/kiem_toan_xml_bhyt.py` |
| `src/lis_hl7_oru.py` | `src/cong_cu_lam_sang/nap_ket_qua_lis_hl7.py` |
| `src/loc_nhan_may.py` | `src/bo_du_lieu/loc_nhan_may.py` |
| `src/loi_dan_thuong.py` | `src/bo_du_lieu/loi_dan_thuong.py` |
| `src/loss_theo_doan.py` | `src/huan_luyen/loss_theo_doan.py` |
| `src/may_trang_thai_hoi_thoai.py` | `src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py` |
| `src/nap_vietmed.py` | `src/bo_du_lieu/nap_vietmed.py` |
| `src/nap_vimq.py` | `src/bo_du_lieu/nap_vimq.py` |
| `src/ngu_lieu_viet.py` | `src/bo_du_lieu/ngu_lieu_viet.py` |
| `src/nguon_lap_cau.py` | `src/do_luong/nguon_lap_cau.py` |
| `src/nhanh.py` | `src/duong_ong/chay_duong_ong.py` |
| `src/nhanh_e.py` | `src/duong_ong/chay_nhanh_e.py` |
| `src/nhat_ky_loi_nhac.py` | `src/he_thong/nhat_ky_loi_nhac.py` |
| `src/nhieu_asr.py` | `src/bo_du_lieu/nhieu_asr.py` |
| `src/ocr_lam_sang.py` | `src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py` |
| `src/phan_quan_he.py` | `src/duong_ong/b3_phan_xu_quan_he.py` |
| `src/phat_bieu.py` | `src/duong_ong/b1_cau_truc_menh_de.py` |
| `src/phuong_ngu.py` | `src/bo_du_lieu/phuong_ngu.py` |
| `src/phuong_ngu_lam_sang.py` | `src/cong_cu_lam_sang/tu_dien_phuong_ngu_lam_sang.py` |
| `src/quet_an_toan_duoc_ly_v2.py` | `src/do_luong/quet_an_toan_duoc_ly_v2.py` |
| `src/quy_dao_lam_sang.py` | `src/cong_cu_lam_sang/quy_dao_nhieu_lan_kham.py` |
| `src/rui_ro_quy_gan.py` | `src/duong_ong/b5_diem_rui_ro_quy_gan.py` |
| `src/sai_so.py` | `src/do_luong/khoang_tin_cay.py` |
| `src/sinh_benh_an.py` | `src/duong_ong/b5_viet_ban_nhap.py` |
| `src/sinh_bo_chan_doan.py` | `src/bo_du_lieu/sinh_bo_chan_doan.py` |
| `src/sinh_hoi_thoai_viet.py` | `src/bo_du_lieu/sinh_hoi_thoai_viet.py` |
| `src/sua_cuc_bo.py` | `src/duong_ong/b6_sua_cuc_bo.py` |
| `src/tach_tap.py` | `src/bo_du_lieu/chia_bon_tap.py` |
| `src/tach_tap_viet.py` | `src/bo_du_lieu/chia_tap_theo_khuon.py` |
| `src/tang_cuong.py` | `src/bo_du_lieu/tang_cuong.py` |
| `src/thach_thuc.py` | `src/bo_du_lieu/sinh_bo_thach_thuc.py` |
| `src/thang_diem_lam_sang.py` | `src/cong_cu_lam_sang/thang_diem_nguy_co.py` |
| `src/thuc_the.py` | `src/duong_ong/b2_gom_nguoi_thuc_the.py` |
| `src/thuoc_do_quy_gan.py` | `src/do_luong/thuoc_do_quy_gan.py` |
| `src/train_baseline.py` | `src/huan_luyen/huan_luyen_sft.py` |
| `src/train_dpo.py` | `src/huan_luyen/huan_luyen_dpo.py` |
| `src/tri_thuc_thuoc.py` | `src/cong_cu_lam_sang/tri_thuc_thuoc.py` |
| `src/trich_xuat_thuc_the.py` | `src/duong_ong/b1_ep_dau_ra_json.py` |
| `src/tro_ly_lam_sang.py` | `src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py` |
| `src/ung_vien_quan_he.py` | `src/duong_ong/b3_sinh_cap_ung_vien_quan_he.py` |
| `src/van_tay_bo.py` | `src/bo_du_lieu/van_tay_bo.py` |
| `src/vi_du_mau.py` | `src/duong_ong/b1_vi_du_mau_loi_nhac.py` |
| `src/worm_audit_log.py` | `src/he_thong/nhat_ky_ky_duyet_worm.py` |
