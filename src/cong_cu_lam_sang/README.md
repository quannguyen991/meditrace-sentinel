# Công cụ lâm sàng hỗ trợ bác sĩ — `src/cong_cu_lam_sang/`

Công cụ trong menu Công cụ quanh bản nháp (BHYT, thuốc, xét nghiệm, giấy tờ). Chỉ là gợi ý, không đổi cách dựng bản nháp; bảng tri thức chưa được chuyên gia duyệt.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [cam_doan_thu_thuat.py](cam_doan_thu_thuat.py) | Giấy tờ | Kiểm xem trước thủ thuật bác sĩ đã giải thích đủ các ý pháp lý cho người bệnh chưa, có căn cứ ở câu nào trong hội thoại. | `src/cam_doan_thu_thuat.py` |
| [canh_bao_tuong_tac_thuoc.py](canh_bao_tuong_tac_thuoc.py) | Thuốc | Cảnh báo bác sĩ khi các thuốc trong đơn tương tác với nhau, chống chỉ định theo bệnh nền hoặc vượt liều trần. | `src/duoc_ly_lam_sang.py` |
| [chuan_hoa_don_vi_xet_nghiem.py](chuan_hoa_don_vi_xet_nghiem.py) | Xét nghiệm | Đổi creatinin, glucose, urea giữa các đơn vị khác nhau về một đơn vị chung để các công cụ khác so được. | `src/chuan_hoa_don_vi_xet_nghiem.py` |
| [di_buong_noi_tru.py](di_buong_noi_tru.py) | Giấy tờ | So lời bệnh nhân và y lệnh hôm nay với hôm qua trong hồ sơ nội trú, chỉ ra triệu chứng, sinh hiệu, thuốc thay đổi để ghi tờ điều trị. | `src/di_buong_noi_tru.py` |
| [di_ung_cheo.py](di_ung_cheo.py) | Thuốc | Kiểm thuốc trong đơn có cùng nhóm với thuốc người bệnh từng dị ứng, theo hoạt chất, nhóm ATC và nhóm hoá học. | `src/di_ung_cheo.py` |
| [doc_phieu_xet_nghiem.py](doc_phieu_xet_nghiem.py) | Xét nghiệm | Lấy chỉ số xét nghiệm và thuốc từ văn bản phiếu hoặc đơn cũ, rồi quy đổi đơn vị và tính eGFR, đối soát ngưỡng. | `src/ocr_lam_sang.py` |
| [doi_soat_can_lam_sang.py](doi_soat_can_lam_sang.py) | Xét nghiệm | So chỉ số xét nghiệm với ngưỡng bình thường theo tuổi, giới và báo giá trị nguy kịch hoặc không khớp với lời bệnh nhân. | `src/can_lam_sang.py` |
| [goi_y_cau_hoi_socrates.py](goi_y_cau_hoi_socrates.py) | Trong lúc khám | Tìm điểm còn thiếu trong phần hỏi bệnh theo khung SOCRATES và gợi ý bác sĩ hỏi thêm câu nào. | `src/tro_ly_lam_sang.py` |
| [hieu_chinh_lieu.py](hieu_chinh_lieu.py) | Thuốc | Gợi ý chỉnh liều thuốc theo chức năng thận (CrCl, eGFR) và bệnh gan nền của người bệnh. | `src/hieu_chinh_lieu.py` |
| [ho_so_benh_nhan_qr.py](ho_so_benh_nhan_qr.py) | Giấy tờ | Gói thuốc, dặn dò và dấu hiệu cần quay lại khám thành một hồ sơ nhỏ ký HMAC để người bệnh quét mã QR mang về. | `src/ho_so_benh_nhan_qr.py` |
| [kiem_toan_xml_bhyt.py](kiem_toan_xml_bhyt.py) | BHYT | Rà gói XML1–XML5 của một lượt khám để tìm lỗi dễ bị giám định BHYT từ chối trước khi gửi cổng. | `src/kiem_toan_xml_bhyt.py` |
| [nap_ket_qua_lis_hl7.py](nap_ket_qua_lis_hl7.py) | Xét nghiệm | Đọc kết quả xét nghiệm từ hệ thống LIS ở dạng HL7, JSON hoặc CSV và đưa về dict chỉ số có mã chuẩn. | `src/lis_hl7_oru.py` |
| [quy_dao_nhieu_lan_kham.py](quy_dao_nhieu_lan_kham.py) | Xét nghiệm | So xét nghiệm và thuốc qua nhiều lần khám để thấy chỉ số tăng giảm, tổn thương thận cấp và thuốc dùng kéo dài. | `src/quy_dao_lam_sang.py` |
| [thang_diem_nguy_co.py](thang_diem_nguy_co.py) | Thang điểm | Tính các thang điểm lâm sàng thường dùng như CURB-65, CHA2DS2-VASc, Wells, GCS, Child-Pugh, BMI từ dữ kiện đã có. | `src/thang_diem_lam_sang.py` |
| [tien_kiem_bhyt_va_khoi_phuc_bo_sot.py](tien_kiem_bhyt_va_khoi_phuc_bo_sot.py) | BHYT | Tiền kiểm hồ sơ trước khi gửi BHYT, gợi ý mã ICD-10, và quét hội thoại tìm mục quan trọng chưa vào bản nháp. | `src/kiem_duyet_bhyt_va_bo_sot.py` |
| [to_dan_do_benh_nhan.py](to_dan_do_benh_nhan.py) | Giấy tờ | Soạn tờ dặn dò bằng lời dễ hiểu cho người bệnh: lịch uống thuốc, việc cần làm, dấu hiệu phải quay lại. | `src/dan_do_benh_nhan.py` |
| [tra_duoc_thu_aho_corasick.py](tra_duoc_thu_aho_corasick.py) | Tri thức | Tìm nhanh tên thuốc trong văn bản và tra thông tin Dược thư Quốc gia, chạy tại chỗ không cần mạng. | `src/aho_corasick_duoc_thu.py` |
| [tri_thuc_thuoc.py](tri_thuc_thuoc.py) | Tri thức | Đọc bảng tri thức thuốc dùng chung (tên, hoạt chất, liều tối đa) từ tệp dữ liệu; bảng này chưa được chuyên gia duyệt. | `src/tri_thuc_thuoc.py` |
| [tu_dien_phuong_ngu_lam_sang.py](tu_dien_phuong_ngu_lam_sang.py) | Tri thức | Đổi cách nói địa phương và khẩu ngữ của người bệnh ba miền sang thuật ngữ y khoa, vẫn giữ vết từ gốc. | `src/phuong_ngu_lam_sang.py` |
| [xuat_fhir_r4.py](xuat_fhir_r4.py) | Liên thông | Chuyển bản nháp hồ sơ khám thành gói FHIR R4 để chuyển sang hệ thống khác. | `src/fhir_exporter.py` |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
