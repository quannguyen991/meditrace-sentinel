# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ]
Làm gì   : Công cụ trong menu Công cụ quanh bản nháp (BHYT, thuốc, xét nghiệm, giấy tờ). Chỉ
           là gợi ý, không đổi cách dựng bản nháp; bảng tri thức chưa được chuyên gia duyệt.
Bản đồ   : BAN_DO_MA_NGUON.md

Các tệp:
    cam_doan_thu_thuat                  Kiểm xem trước thủ thuật bác sĩ đã giải thích đủ các
                                        ý pháp lý cho người bệnh chưa, có căn cứ ở câu nào
                                        trong hội thoại.
    canh_bao_tuong_tac_thuoc            Cảnh báo bác sĩ khi các thuốc trong đơn tương tác
                                        với nhau, chống chỉ định theo bệnh nền hoặc vượt
                                        liều trần.
    chuan_hoa_don_vi_xet_nghiem         Đổi creatinin, glucose, urea giữa các đơn vị khác
                                        nhau về một đơn vị chung để các công cụ khác so
                                        được.
    di_buong_noi_tru                    So lời bệnh nhân và y lệnh hôm nay với hôm qua trong
                                        hồ sơ nội trú, chỉ ra triệu chứng, sinh hiệu, thuốc
                                        thay đổi để ghi tờ điều trị.
    di_ung_cheo                         Kiểm thuốc trong đơn có cùng nhóm với thuốc người
                                        bệnh từng dị ứng, theo hoạt chất, nhóm ATC và nhóm
                                        hoá học.
    doc_phieu_xet_nghiem                Lấy chỉ số xét nghiệm và thuốc từ văn bản phiếu hoặc
                                        đơn cũ, rồi quy đổi đơn vị và tính eGFR, đối soát
                                        ngưỡng.
    doi_soat_can_lam_sang               So chỉ số xét nghiệm với ngưỡng bình thường theo
                                        tuổi, giới và báo giá trị nguy kịch hoặc không khớp
                                        với lời bệnh nhân.
    goi_y_cau_hoi_socrates              Tìm điểm còn thiếu trong phần hỏi bệnh theo khung
                                        SOCRATES và gợi ý bác sĩ hỏi thêm câu nào.
    hieu_chinh_lieu                     Gợi ý chỉnh liều thuốc theo chức năng thận (CrCl,
                                        eGFR) và bệnh gan nền của người bệnh.
    ho_so_benh_nhan_qr                  Gói thuốc, dặn dò và dấu hiệu cần quay lại khám
                                        thành một hồ sơ nhỏ ký HMAC để người bệnh quét mã QR
                                        mang về.
    kiem_toan_xml_bhyt                  Rà gói XML1–XML5 của một lượt khám để tìm lỗi dễ bị
                                        giám định BHYT từ chối trước khi gửi cổng.
    nap_ket_qua_lis_hl7                 Đọc kết quả xét nghiệm từ hệ thống LIS ở dạng HL7,
                                        JSON hoặc CSV và đưa về dict chỉ số có mã chuẩn.
    quy_dao_nhieu_lan_kham              So xét nghiệm và thuốc qua nhiều lần khám để thấy
                                        chỉ số tăng giảm, tổn thương thận cấp và thuốc dùng
                                        kéo dài.
    thang_diem_nguy_co                  Tính các thang điểm lâm sàng thường dùng như
                                        CURB-65, CHA2DS2-VASc, Wells, GCS, Child-Pugh, BMI
                                        từ dữ kiện đã có.
    tien_kiem_bhyt_va_khoi_phuc_bo_sot  Tiền kiểm hồ sơ trước khi gửi BHYT, gợi ý mã ICD-10,
                                        và quét hội thoại tìm mục quan trọng chưa vào bản
                                        nháp.
    to_dan_do_benh_nhan                 Soạn tờ dặn dò bằng lời dễ hiểu cho người bệnh: lịch
                                        uống thuốc, việc cần làm, dấu hiệu phải quay lại.
    tra_duoc_thu_aho_corasick           Tìm nhanh tên thuốc trong văn bản và tra thông tin
                                        Dược thư Quốc gia, chạy tại chỗ không cần mạng.
    tri_thuc_thuoc                      Đọc bảng tri thức thuốc dùng chung (tên, hoạt chất,
                                        liều tối đa) từ tệp dữ liệu; bảng này chưa được
                                        chuyên gia duyệt.
    tu_dien_phuong_ngu_lam_sang         Đổi cách nói địa phương và khẩu ngữ của người bệnh
                                        ba miền sang thuật ngữ y khoa, vẫn giữ vết từ gốc.
    xuat_fhir_r4                        Chuyển bản nháp hồ sơ khám thành gói FHIR R4 để
                                        chuyển sang hệ thống khác.
"""
