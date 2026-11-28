# Nhật ký lời nhắc (Prompt) & Bảng khai mã nguồn
## MediTrace Sentinel

Nhật ký lời nhắc — phần mã nguồn
Phạm vi của tài liệu này
Tài liệu ghi lại các lời nhắc đã dẫn tới thay đổi trong mã nguồn (src/, tests/, tools/ của phần xử lý; src/, may-chu/, db/, server.ts của giao diện web, ghi là web/…), trích tự động từ bản ghi phiên làm việc.
Không bao gồm: lời nhắc chỉ dẫn tới tài liệu trong docs/, câu hỏi, và trao đổi. Phụ lục hướng dẫn sử dụng AI yêu cầu nhật ký lời nhắc ở mục “AI viết mã nguồn ban đầu”, nên phạm vi này khớp với yêu cầu — nhưng phải đọc đúng là nhật ký cho mã nguồn, không phải nhật ký cho toàn bộ cuộc trao đổi.
Cách lọc là theo việc đã làm, không theo từ khoá. Một lời nhắc vào đây khi công việc ngay sau nó thỏa một trong hai điều kiện:
ghi thẳng vào một tệp mã nguồn; hoặc
dẫn tới một commit mã nguồn: mỗi commit được gắn cho lời nhắc gần nhất trước nó mà phần việc sau lời nhắc đó có dùng tới kho đề tài. Cách gắn này theo thời gian, nên có thể lệch một lời nhắc; những mục gắn theo cách này ghi rõ “qua commit”.
Bản ghi phiên trên máy chứa cả các dự án khác; bộ trích chỉ lấy lời nhắc của người dùng, và chỉ lấy lời nhắc có phần việc chạm tới kho phần xử lý (meditrace-core) hoặc kho giao diện web (meditrace-sentinel).
Giờ ghi theo giờ Việt Nam (UTC+7).

Nội dung đã che
Lời nhắc là lời nói tự nhiên, có xen chuyện ngoài đề tài (dự án khác, máy chủ, tài khoản) và thông tin riêng (địa chỉ máy, đường dẫn máy cá nhân). Những cụm đó được thay bằng dấu [đã lược: …] hoặc [đã che: …]. Việc che không bỏ lời nhắc nào, không bỏ tệp hay commit nào; chỉ thay cụm từ. Lời nhắc dài quá 300 ký tự được cắt và ghi rõ là đã cắt.

Số lời nhắc: 135 · Số commit mã nguồn: 215 · Khoảng thời gian: 2026-09-05 → 2026-10-18 · Số chỗ đã che: 17 (trong 13 lời nhắc)

---

## Bảng khai mã nguồn

**Khai báo:** Toàn bộ mã nguồn trong src/, tests/, tools/ (phần xử lý) và web/ (giao diện) do AI viết, dưới sự chỉ đạo của học sinh. Không có tệp nào được viết tay hoàn toàn.

**Phân biệt: viết mã và quyết định thiết kế:**
Bảng dưới nói về việc gõ mã. Các quyết định thiết kế đến từ học sinh, và đọc thẳng ra được trong nhật ký lời nhắc. Ba ví dụ đã đổi hướng cả đề tài:
• “3.000 ca từ 24 khuôn vẫn có nguy cơ mô hình học công thức viết”
• “không huấn luyện trên hội thoại do mô hình khác sinh”
• “đừng dùng VAIC làm phần đề bạn đối chiếu”

**Số tệp mã nguồn: 302 · Tổng số lần sửa: 775**

### src/ — 103 tệp (kèm 12 tệp nâng cấp tháng 10)

| Tệp | Lần sửa | Từ ngày | Đến ngày | Nguồn |
| :--- | :---: | :---: | :---: | :--- |
| __init__.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| audio/__init__.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/adapter.py | 2 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/alignment.py | 3 | 2026-09-22 | 2026-09-25 | AI viết |
| audio/api.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/__init__.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/base.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/bench_metrics.py | 1 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Cập nhật chỉ số đánh giá tỷ lệ nhận dạng sai từ ngữ lâm sàng trọng yếu C-WER) |
| audio/asr/critical_tokens.py | 2 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Mở rộng từ điển 1.200 thuật ngữ y khoa trọng yếu: tên thuốc, liều lượng, huyết áp, dị ứng) |
| audio/asr/disagreement.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/faster_whisper_provider.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/phowhisper_provider.py | 3 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/registry.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/schemas.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/asr/sidecar_provider.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/config.py | 3 | 2026-09-22 | 2026-09-25 | AI viết |
| audio/models.py | 2 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/pipeline.py | 3 | 2026-09-22 | 2026-09-25 | AI viết + Quân (Thiết kế luồng xử lý âm thanh đa luồng: tiền xử lý, bóc tách người nói và nhận dạng giọng nói) |
| audio/preprocessing.py | 2 | 2026-09-22 | 2026-09-22 | AI viết |
| audio/providers.py | 3 | 2026-09-22 | 2026-09-25 | AI viết |
| audio/pyannote-moi-truong.txt | 1 | 2026-09-25 | 2026-09-25 | AI viết |
| audio/pyannote_chay.py | 1 | 2026-09-25 | 2026-09-25 | AI viết |
| audio/pyannote_provider.py | 1 | 2026-09-25 | 2026-09-25 | AI viết |
| audio/storage.py | 1 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Cấu hình cơ chế lưu trữ phân đoạn âm thanh an toàn với mã hóa đường truyền nội bộ) |
| bakeoff.py | 15 | 2026-09-06 | 2026-09-16 | AI viết |
| ban_duyet_mau.html | 2 | 2026-09-11 | 2026-09-11 | AI viết |
| bit_nhan.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| bo_gpt500.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| bo_nguoi_that.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| canh_bao/__init__.py | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| canh_bao/asr.py | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| canh_bao/gop.py | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| canh_bao/loai.py | 2 | 2026-09-23 | 2026-09-24 | AI viết + Quân (Phân loại 4 cấp độ cảnh báo an toàn: Thông tin, Cần chú ý, Nguy cơ cao, Đình chỉ khẩn cấp) |
| canh_bao/nhat_ky.py | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| canh_bao/phat_hien.py | 2 | 2026-09-23 | 2026-09-24 | AI viết + Quân (Định nghĩa các mẫu phát hiện sai lệch thông tin thuốc giữa lời thoại bác sĩ và đơn kê) |
| canh_bao/so_lieu.py | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| canh_bao/toan_ca.py | 1 | 2026-09-23 | 2026-09-23 | AI viết + Quân (Thiết lập ngưỡng kích hoạt cảnh báo đỏ toàn ca khi phát hiện sốc phản vệ hoặc ngộ độc cấp) |
| cap_nhat.py | 3 | 2026-09-05 | 2026-09-16 | AI viết |
| cham_chu_the.py | 1 | 2026-09-06 | 2026-09-06 | AI viết |
| cham_diem.py | 2 | 2026-09-05 | 2026-09-09 | AI viết + Quân (Xây dựng thang đo F1 lâm sàng có trọng số: ưu tiên phạt nặng bỏ sót dị ứng và sai liều thuốc) |
| cham_he_thong.py | 8 | 2026-09-11 | 2026-09-24 | AI viết |
| cham_lai_bang_quy_gan.py | 7 | 2026-09-07 | 2026-09-10 | AI viết |
| cham_muc_thach_thuc.py | 1 | 2026-09-15 | 2026-09-15 | AI viết |
| cham_tay.py | 3 | 2026-09-19 | 2026-09-22 | AI viết + Quân (Quy chuẩn hóa thang chấm điểm mù độc lập cho bác sĩ kiểm định chất lượng bệnh án) |
| chuan_dinh_dang.py | 2 | 2026-09-11 | 2026-09-11 | AI viết |
| chuan_hoa.py | 3 | 2026-09-11 | 2026-09-24 | AI viết + Quân (Bổ sung từ điển chuẩn hóa phương ngữ 3 miền, tên thuốc biệt dược và cách phát âm địa phương) |
| chung_chi_thuoc_do.py | 4 | 2026-09-07 | 2026-09-09 | AI viết |
| cong_rui_ro.py | 3 | 2026-09-11 | 2026-09-22 | AI viết + Quân (Tái cấu trúc 2 luồng xuất bản: SOAP chính thức vs Mục cách ly cần bác sĩ xác nhận) |
| context_vi.py | 1 | 2026-09-16 | 2026-09-16 | AI viết |
| dan_gian.py | 2 | 2026-09-24 | 2026-09-24 | AI viết |
| danh_gia_khoa.py | 3 | 2026-09-11 | 2026-09-15 | AI viết |
| dau_vet_nguon.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| dich_vu.py | 8 | 2026-09-23 | 2026-09-25 | AI viết |
| do_bit_nhan.py | 5 | 2026-09-07 | 2026-09-11 | AI viết |
| do_bo_chan_doan.py | 4 | 2026-09-06 | 2026-09-10 | AI viết |
| do_canh_bao.py | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| do_dac.py | 6 | 2026-09-06 | 2026-09-12 | AI viết |
| do_dan_gian.py | 2 | 2026-09-24 | 2026-09-24 | AI viết |
| do_neu_ten.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| do_quan_he.py | 3 | 2026-09-10 | 2026-09-11 | AI viết |
| do_tang_quan_he.py | 3 | 2026-09-07 | 2026-09-09 | AI viết |
| do_tang_quy_gan.py | 3 | 2026-09-10 | 2026-09-11 | AI viết |
| do_trich.py | 3 | 2026-09-09 | 2026-09-11 | AI viết |
| do_van_xuoi.py | 4 | 2026-09-07 | 2026-09-10 | AI viết |
| do_vidia2std.py | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| doan_van.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| doi_chung_tam_thuong.py | 5 | 2026-09-10 | 2026-09-16 | AI viết |
| du_lieu.py | 5 | 2026-09-05 | 2026-09-11 | AI viết |
| du_lieu_trich.py | 7 | 2026-09-08 | 2026-09-15 | AI viết |
| duong_dan.py | 4 | 2026-09-05 | 2026-09-22 | AI viết |
| duong_danh_doi.py | 3 | 2026-09-07 | 2026-09-09 | AI viết |
| giao_dien_duyet.py | 2 | 2026-09-11 | 2026-09-11 | AI viết |
| hoi_lai.py | 2 | 2026-09-11 | 2026-09-22 | AI viết |
| khai_ma_nguon.py | 3 | 2026-09-10 | 2026-09-30 | AI viết |
| khoa_bang_chung.py | 5 | 2026-09-11 | 2026-09-15 | AI viết + Quân (Thiết kế thuật toán khóa mỏ neo bằng chứng, ngăn AI tự bịa bằng chứng không có trong thoại) |
| kiem_day_du.py | 1 | 2026-09-06 | 2026-09-06 | AI viết |
| kiem_mo_hinh.py | 1 | 2026-09-06 | 2026-09-06 | AI viết |
| loi_dan_thuong.py | 4 | 2026-09-10 | 2026-09-12 | AI viết |
| ngu_lieu_viet.py | 5 | 2026-09-07 | 2026-09-15 | AI viết |
| nhanh.py | 19 | 2026-09-06 | 2026-09-23 | AI viết |
| nhanh_e.py | 3 | 2026-09-07 | 2026-09-11 | AI viết |
| nhat_ky_loi_nhac.py | 6 | 2026-09-10 | 2026-09-30 | AI viết |
| nhieu_asr.py | 1 | 2026-09-12 | 2026-09-12 | AI viết |
| phan_quan_he.py | 1 | 2026-09-09 | 2026-09-09 | AI viết |
| phat_bieu.py | 8 | 2026-09-05 | 2026-09-16 | AI viết |
| phuong_ngu.py | 3 | 2026-09-10 | 2026-09-24 | AI viết + Quân (Xây dựng bộ quy tắc chuyển đổi phương ngữ miền Tây và miền Trung về thuật ngữ y khoa chuẩn) |
| rui_ro_quy_gan.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| sai_so.py | 4 | 2026-09-10 | 2026-09-11 | AI viết |
| sinh_benh_an.py | 11 | 2026-09-06 | 2026-09-15 | AI viết |
| sinh_bo_chan_doan.py | 3 | 2026-09-05 | 2026-09-10 | AI viết |
| sinh_hoi_thoai_viet.py | 19 | 2026-09-07 | 2026-09-24 | AI viết + Quân (Biên soạn các bẫy lâm sàng: bệnh nhân tự sửa lời, câu hỏi giả định và vai người nhà) |
| sua_cuc_bo.py | 5 | 2026-09-06 | 2026-09-11 | AI viết |
| tach_tap.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| tach_tap_viet.py | 4 | 2026-09-09 | 2026-09-11 | AI viết |
| tang_cuong.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| thach_thuc.py | 5 | 2026-09-11 | 2026-09-24 | AI viết |
| thuc_the.py | 2 | 2026-09-06 | 2026-09-24 | AI viết + Quân (Bổ sung bộ nhận diện đại từ tự xưng phương ngữ Nam Bộ 'tui' tương đương 'tôi') |
| thuoc_do_quy_gan.py | 2 | 2026-09-07 | 2026-09-07 | AI viết |
| train_baseline.py | 9 | 2026-09-06 | 2026-09-19 | AI viết |
| tron_cap.py | 2 | 2026-09-06 | 2026-09-09 | AI viết |
| ung_vien_quan_he.py | 2 | 2026-09-07 | 2026-09-07 | AI viết |
| van_tay_bo.py | 3 | 2026-09-11 | 2026-09-11 | AI viết |
| vi_du_mau.py | 3 | 2026-09-06 | 2026-09-11 | AI viết |
| can_lam_sang.py | 4 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Thiết kế logic phân tích bất thường cận lâm sàng, gắn cờ báo động sinh hóa máu và điện giải) |
| da_benh_ly.py | 3 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Xây dựng ma trận cảnh báo tương tác bệnh học phức hợp: suy tim kèm đái tháo đường và suy thận) |
| dan_do_benh_nhan.py | 4 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Thiết kế ma trận dặn dò người bệnh chia 4 khung giờ chuẩn y khoa sáng - trưa - chiều - tối) |
| dieu_phoi_ha_tang.py | 6 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Thiết kế kiến trúc điều phối Orchestrator kết nối tuần tự và song song 8 chốt an toàn) |
| duoc_ly_lam_sang.py | 5 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Thiết kế Chốt 5 DDI: Tra cứu tương tác thuốc nguy cơ cao Clopidogrel + Omeprazole) |
| fhir_exporter.py | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Chuẩn hóa lược đồ ánh xạ dữ liệu bệnh án SOAP sang chuẩn liên thông y tế quốc tế HL7 FHIR R4) |
| guardrails.py | 4 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Xây dựng 8 chốt chặn an toàn lâm sàng, kiểm soát ranh giới liều và ngăn chặn ảo giác y khoa) |
| hieu_chinh_lieu.py | 3 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Hiện thực hóa công thức tính eGFR theo CKD-EPI 2021 và thuật toán cảnh báo giảm liều suy thận) |
| khu_dinh_danh.py | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Đặc tả bộ quy tắc ẩn danh dữ liệu sức khỏe; khung pháp lý hiện hành: Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15) |
| kiem_khuon.py | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Thiết kế bộ kiểm tra tính toàn vẹn cấu trúc 4 phần Subjective-Objective-Assessment-Plan) |
| thang_diem_lam_sang.py | 4 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Hiện thực hóa các thang điểm lâm sàng CKD-EPI, Cockcroft-Gault, CHA2DS2-VASc và HAS-BLED) |
| tro_ly_lam_sang.py | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Hiện thực hóa Chốt 8 SOCRATES: Tác tử chủ động gợi mở câu hỏi lâm sàng khi thiếu dữ kiện) |


### tests/ — 90 tệp (kèm 13 tệp kiểm thử nâng cấp)

| Tệp | Lần sửa | Từ ngày | Đến ngày | Nguồn |
| :--- | :---: | :---: | :---: | :--- |
| __init__.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| test_audio_adapter.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_audio_alignment.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_audio_asr_comparison.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_audio_asr_registry.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_audio_bench_metrics.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_audio_clinical_tokens.py | 1 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Kiểm thử bộ trích xuất từ khóa lâm sàng trọng yếu trên tập âm thanh đa phương ngữ) |
| test_audio_diarization.py | 2 | 2026-09-25 | 2026-09-25 | AI viết |
| test_audio_intake.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_audio_phowhisper_provider.py | 3 | 2026-09-22 | 2026-09-22 | AI viết |
| test_bakeoff.py | 3 | 2026-09-06 | 2026-09-06 | AI viết |
| test_ban_lap_ly_do_kham.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_bit_nhan.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| test_bo_chan_doan.py | 2 | 2026-09-05 | 2026-09-09 | AI viết |
| test_bo_gpt500.py | 2 | 2026-09-11 | 2026-09-27 | AI viết |
| test_bo_nguoi_that.py | 2 | 2026-09-10 | 2026-09-27 | AI viết |
| test_can_cu_bang_chung.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| test_canh_bao.py | 2 | 2026-09-23 | 2026-09-24 | AI viết |
| test_canh_lech_the_he.py | 1 | 2026-09-19 | 2026-09-19 | AI viết |
| test_cap_nhat.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| test_cap_nhat_nguon.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_cham_diem.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| test_cham_he_thong.py | 3 | 2026-09-11 | 2026-09-22 | AI viết |
| test_cham_lai_bang_quy_gan.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| test_cham_ma_loi_moi.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_cham_muc_thach_thuc.py | 1 | 2026-09-15 | 2026-09-15 | AI viết |
| test_cham_tay.py | 3 | 2026-09-19 | 2026-09-22 | AI viết |
| test_chan_du_lieu_gpt.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_chan_tap_khoa.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_chan_tap_ngoai.py | 1 | 2026-09-09 | 2026-09-09 | AI viết |
| test_chuan_dinh_dang.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_chuan_hoa.py | 1 | 2026-09-11 | 2026-09-11 | AI viết + Quân (Bổ sung kiểm thử quy đổi phương ngữ lâm sàng) |
| test_chung_chi_thuoc_do.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| test_cong_rui_ro.py | 2 | 2026-09-11 | 2026-09-22 | AI viết |
| test_context_vi.py | 1 | 2026-09-16 | 2026-09-16 | AI viết |
| test_dan_gian.py | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| test_dich_vu.py | 2 | 2026-09-23 | 2026-09-23 | AI viết |
| test_dinh_tuyen_muc.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_do_bo_chan_doan.py | 4 | 2026-09-06 | 2026-09-10 | AI viết |
| test_do_dac.py | 2 | 2026-09-06 | 2026-09-06 | AI viết |
| test_do_neu_ten.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_do_quan_he.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| test_do_trich.py | 1 | 2026-09-09 | 2026-09-09 | AI viết |
| test_do_van_xuoi.py | 2 | 2026-09-07 | 2026-09-07 | AI viết |
| test_doi_chung_tam_thuong.py | 2 | 2026-09-10 | 2026-09-10 | AI viết |
| test_du_lieu.py | 3 | 2026-09-05 | 2026-09-07 | AI viết |
| test_duong_dan.py | 3 | 2026-09-05 | 2026-09-09 | AI viết |
| test_duong_danh_doi.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| test_f1_ser.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| test_hoi_lai.py | 1 | 2026-09-11 | 2026-09-11 | AI viết + Quân (Bổ sung bộ test kiểm tra xung đột phát ngôn giữa bệnh nhân và người nhà) |
| test_khai_ma_nguon.py | 2 | 2026-09-10 | 2026-09-30 | AI viết |
| test_khoa_bang_chung.py | 3 | 2026-09-11 | 2026-09-11 | AI viết + Quân |
| test_kiem_day_du.py | 2 | 2026-09-06 | 2026-09-07 | AI viết |
| test_kiem_khop.py | 2 | 2026-09-10 | 2026-09-10 | AI viết |
| test_lo_danh_tinh.py | 1 | 2026-09-15 | 2026-09-15 | AI viết |
| test_loi_dan_thuong.py | 3 | 2026-09-10 | 2026-09-11 | AI viết |
| test_mo_rong_bo_du_lieu.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_nghi_ngo.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| test_nhan_dap_an.py | 2 | 2026-09-11 | 2026-09-11 | AI viết |
| test_nhanh.py | 1 | 2026-09-06 | 2026-09-06 | AI viết |
| test_nhanh_e.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| test_nhanh_trung_gian.py | 7 | 2026-09-06 | 2026-09-11 | AI viết |
| test_nhat_ky_loi_nhac.py | 6 | 2026-09-10 | 2026-09-30 | AI viết |
| test_nhat_quan.py | 1 | 2026-09-09 | 2026-09-09 | AI viết |
| test_nhieu_asr.py | 1 | 2026-09-12 | 2026-09-12 | AI viết |
| test_phan_quan_he.py | 1 | 2026-09-09 | 2026-09-09 | AI viết |
| test_phuong_ngu.py | 4 | 2026-09-10 | 2026-09-27 | AI viết |
| test_phuong_ngu_chi_o_tap_danh_gia.py | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| test_ps1_chi_ascii.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| test_quan_he_trong_dap_an.py | 4 | 2026-09-09 | 2026-09-11 | AI viết |
| test_rui_ro_quy_gan.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| test_sai_so.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| test_sinh_benh_an.py | 4 | 2026-09-06 | 2026-09-09 | AI viết |
| test_sinh_hoi_thoai_viet.py | 9 | 2026-09-07 | 2026-09-24 | AI viết + Quân (Xây dựng bộ test kiểm tra tính nhất quán giữa bệnh sử, triệu chứng và lý do khám) |
| test_sua_cuc_bo.py | 3 | 2026-09-06 | 2026-09-07 | AI viết |
| test_tang_cuong.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| test_ten_tep_ket_qua.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| test_thach_thuc.py | 2 | 2026-09-11 | 2026-09-24 | AI viết |
| test_theo_luot.py | 1 | 2026-09-16 | 2026-09-16 | AI viết |
| test_thuc_the.py | 2 | 2026-09-06 | 2026-09-24 | AI viết |
| test_thuoc_chi_tiet.py | 3 | 2026-09-15 | 2026-09-16 | AI viết |
| test_thuoc_do_quy_gan.py | 1 | 2026-09-07 | 2026-09-07 | AI viết |
| test_train_baseline.py | 2 | 2026-09-06 | 2026-09-09 | AI viết |
| test_tron_cap.py | 1 | 2026-09-06 | 2026-09-06 | AI viết |
| test_tu_json.py | 2 | 2026-09-06 | 2026-09-07 | AI viết |
| test_ung_vien_quan_he.py | 2 | 2026-09-07 | 2026-09-07 | AI viết |
| test_vai_nhan_vien.py | 1 | 2026-09-10 | 2026-09-10 | AI viết |
| test_van_tay_bo.py | 3 | 2026-09-11 | 2026-09-11 | AI viết |
| test_van_tay_du_lieu.py | 1 | 2026-09-10 | 2026-09-10 | AI viết + Quân (Kiểm thử cơ chế phát hiện trùng lặp dữ liệu huấn luyện để chống học vẹt) |
| test_xung_ho_nguoi_nha.py | 1 | 2026-09-12 | 2026-09-12 | AI viết + Quân (Kiểm thử phân biệt vai người nhà khai bệnh hộ và bệnh nhân trực tiếp trả lời) |
| test_can_lam_sang.py | 2 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử phát hiện bất thường kết quả xét nghiệm và ngưỡng báo động sinh hóa) |
| test_da_benh_ly.py | 2 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử xung đột đơn thuốc trên bệnh nhân đa bệnh mạn tính cao tuổi) |
| test_dan_do_benh_nhan.py | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử tính mạch lạc và độ an toàn của lời dặn dò thuốc phân theo 4 buổi sáng-trưa-chiều-tối) |
| test_dieu_phoi_ha_tang.py | 4 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử chuỗi điều phối liên hoàn 8 chốt an toàn từ âm thanh gốc đến bệnh án SOAP) |
| test_duoc_ly_lam_sang.py | 3 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử ma trận tương tác thuốc DDI và cơ chế chặn kết hợp nguy hiểm) |
| test_fhir_exporter.py | 2 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử tính hợp lệ JSON Bundle của tài nguyên FHIR Encounter, Condition, MedicationRequest) |
| test_guardrails.py | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử đơn vị và kịch bản tấn công bypass 8 chốt an toàn lâm sàng) |
| test_hieu_chinh_lieu.py | 2 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử các mốc giảm liều kháng sinh và thuốc hạ đường huyết theo độ lọc cầu thận) |
| test_khu_dinh_danh.py | 2 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử thuật toán bóc tách và che giấu thông tin định danh cá nhân) |
| test_kiem_khuon.py | 2 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử bẫy định dạng cấu trúc bệnh án khi thiếu mục khám thực thể hoặc chẩn đoán) |
| test_thang_diem_lam_sang.py | 3 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Bộ test case đối soát độ chính xác tính toán eGFR và phân tầng nguy cơ đột quỵ) |
| test_tro_ly_lam_sang.py | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử kịch bản SOCRATES chủ động gợi mở câu hỏi khi bệnh sử thiếu tính chất đau) |


### tools/ — 49 tệp

| Tệp | Lần sửa | Từ ngày | Đến ngày | Nguồn |
| :--- | :---: | :---: | :---: | :--- |
| asr-bench/chay-benchmark.py | 1 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Thiết kế kịch bản benchmark so sánh độ chính xác nhận dạng lời thoại y tế trên các mô hình ASR) |
| asr-bench/chay-thu-dau-cuoi.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| asr-bench/tao-am-thanh-thu.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| asr-bench/thu-tach-nguoi-noi.py | 1 | 2026-09-25 | 2026-09-25 | AI viết |
| canh-chuoi.ps1 | 1 | 2026-09-16 | 2026-09-16 | AI viết |
| cham-nhanh-a-8b.py | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| chay-bo-5000-voi-log.ps1 | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| chay-bo-5000.ps1 | 3 | 2026-09-10 | 2026-09-10 | AI viết |
| chay-het.ps1 | 2 | 2026-09-06 | 2026-09-06 | AI viết |
| chay-lai-tat-ca.ps1 | 1 | 2026-09-09 | 2026-09-09 | AI viết |
| chay-nhanh-A-voi-log.ps1 | 1 | 2026-09-14 | 2026-09-14 | AI viết |
| chay-nhanh-A.ps1 | 1 | 2026-09-14 | 2026-09-14 | AI viết |
| chay-the-he-5-voi-log.ps1 | 1 | 2026-09-11 | 2026-09-11 | AI viết |
| chay-the-he-5.ps1 | 2 | 2026-09-11 | 2026-09-11 | AI viết |
| chay-the-he-6-voi-log.ps1 | 1 | 2026-09-12 | 2026-09-12 | AI viết |
| chay-the-he-6.ps1 | 4 | 2026-09-12 | 2026-09-14 | AI viết |
| chay-the-he-7-voi-log.ps1 | 3 | 2026-09-15 | 2026-09-15 | AI viết |
| chay-the-he-7.ps1 | 1 | 2026-09-15 | 2026-09-15 | AI viết |
| chay-the-he-8-voi-log.ps1 | 1 | 2026-09-17 | 2026-09-17 | AI viết |
| chay-the-he-8.ps1 | 1 | 2026-09-17 | 2026-09-17 | AI viết |
| chung-chi-mo-rong.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| danh-gia-trich.ps1 | 1 | 2026-09-09 | 2026-09-09 | AI viết |
| do-trung-nguyen-van.py | 1 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Xây dựng thước đo kiểm tra độ trùng lặp nguyên văn để ngăn ngừa học vẹt dữ liệu) |
| doi-chung-thuong-mai.py | 1 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Thiết kế bộ tiêu chí đối sánh lâm sàng mù đôi với các phần mềm Scribe thương mại) |
| don-dem-trich.py | 1 | 2026-09-14 | 2026-09-14 | AI viết |
| dung-goi-drive.py | 3 | 2026-09-30 | 2026-09-30 | AI viết |
| goi-drive-huong-dan.md | 1 | 2026-09-30 | 2026-09-30 | AI viết |
| ho-so-sang-tao-tre.py | 3 | 2026-09-22 | 2026-09-30 | AI viết |
| kaggle_chay.py | 1 | 2026-09-16 | 2026-09-16 | AI viết |
| kaggle_goi.py | 2 | 2026-09-16 | 2026-09-19 | AI viết |
| kiem-the-he.py | 1 | 2026-09-15 | 2026-09-15 | AI viết |
| md-sang-docx.js | 5 | 2026-09-08 | 2026-09-19 | AI viết |
| md-sang-pdf.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| phieu-cham-tay.py | 3 | 2026-09-19 | 2026-09-22 | AI viết + Quân (Thiết kế quy trình và phiếu chấm điểm mù đối soát lâm sàng cho bác sĩ) |
| phieu-duyet-dan-gian.py | 1 | 2026-09-24 | 2026-09-24 | AI viết + Quân (Thiết kế biểu mẫu duyệt thuật ngữ y khoa dân gian cho hội đồng chuyên môn) |
| phieu-in.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| phieu-word.py | 3 | 2026-09-19 | 2026-09-22 | AI viết |
| quet-nguong-ghep.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| so-dap-an-8-8b.py | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| soi-sai-thuoc.py | 1 | 2026-09-19 | 2026-09-19 | AI viết + Quân (Xây dựng kịch bản truy vết lỗi nhận diện tên thuốc và sai khác liều dùng) |
| svg-sang-png.py | 1 | 2026-09-19 | 2026-09-19 | AI viết |
| tai-mo-hinh.ps1 | 2 | 2026-09-06 | 2026-09-10 | AI viết |
| va-dap-an-giu-loi.py | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| va-luot-thoai.py | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| ve-hinh-tai-lieu-v2.py | 4 | 2026-09-17 | 2026-09-19 | AI viết |
| ve-hinh-tai-lieu.py | 3 | 2026-09-17 | 2026-09-19 | AI viết |
| xuat-ma-nguon.py | 7 | 2026-09-27 | 2026-10-01 | AI viết |
| xuat-pdf.py | 1 | 2026-09-05 | 2026-09-05 | AI viết |
| xuat/README-github.md | 2 | 2026-09-27 | 2026-10-01 | AI viết |


### web/ — 49 tệp (kèm 2 component mới)

| Tệp | Lần sửa | Từ ngày | Đến ngày | Nguồn |
| :--- | :---: | :---: | :---: | :--- |
| db/schema.sql | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| may-chu/csdl.ts | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| may-chu/tai-khoan.ts | 2 | 2026-09-24 | 2026-09-27 | AI viết |
| server.ts | 25 | 2026-09-22 | 2026-09-29 | AI viết |
| src/App.tsx | 20 | 2026-09-22 | 2026-09-30 | AI viết |
| src/Goc.tsx | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| src/components/AudioDeviceDropdown.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/components/BangDuLieuMinhHoa.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/components/BottomPromptBar.tsx | 3 | 2026-09-22 | 2026-09-23 | AI viết + Quân (Tối ưu hóa thanh nhập lệnh AI phản hồi nhanh với gợi ý hành động lâm sàng một chạm) |
| src/components/ClinicalEvidenceDrawer.tsx | 12 | 2026-09-22 | 2026-09-29 | AI viết + Quân (Thiết kế ngăn kéo tra cứu bằng chứng lâm sàng và phác đồ điều trị của Bộ Y tế) |
| src/components/ClinicalSourcesPopover.tsx | 2 | 2026-09-22 | 2026-09-23 | AI viết + Quân (Thiết kế popup hiển thị nguồn trích dẫn y văn và khuyến cáo dược lâm sàng) |
| src/components/ContextView.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/components/DocumentTabs.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết + Quân (Thiết kế tab chuyển đổi linh hoạt giữa Bệnh án SOAP, Tờ dặn dò và Báo cáo FHIR) |
| src/components/DuyetBenCanh.tsx | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| src/components/EvidenceView.tsx | 13 | 2026-09-22 | 2026-09-29 | AI viết + Quân (Thiết kế giao diện trực quan hóa căn cứ lâm sàng và chỉ dẫn tương tác thuốc) |
| src/components/HomeDashboard.tsx | 3 | 2026-09-29 | 2026-09-30 | AI viết + Quân (Bố cục trung tâm điều hành ca khám, thống kê chỉ số an toàn và danh sách bệnh nhân chờ) |
| src/components/ManDangNhap.tsx | 3 | 2026-09-24 | 2026-09-30 | AI viết |
| src/components/MayTinhLamSang.tsx | 1 | 2026-09-23 | 2026-09-23 | AI viết + Quân (Xây dựng giao diện công cụ tính nhanh liều lượng thuốc và độ thanh thải thận cho bác sĩ) |
| src/components/MediTraceLogo.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/components/MenuTaiKhoan.tsx | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| src/components/NavigationRail.tsx | 6 | 2026-09-22 | 2026-09-30 | AI viết |
| src/components/NoteEditorView.tsx | 6 | 2026-09-22 | 2026-09-23 | AI viết + Quân (Tối ưu hóa bàn làm việc bác sĩ, phím tắt lâm sàng và thanh công cụ xuất bản A4) |
| src/components/PatientsView.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/components/ScribeHeader.tsx | 6 | 2026-09-22 | 2026-09-29 | AI viết + Quân (Thiết kế thanh trạng thái ca khám, hiển thị trực quan thông tin hành chính bệnh nhân và cờ dị ứng) |
| src/components/SessionsSidebar.tsx | 4 | 2026-09-22 | 2026-09-30 | AI viết |
| src/components/TaoVanBanModal.tsx | 3 | 2026-09-23 | 2026-09-29 | AI viết |
| src/components/TasksView.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/components/TemplatePickerModal.tsx | 2 | 2026-09-22 | 2026-09-23 | AI viết |
| src/components/TemplatesView.tsx | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/components/ThanhAmThanh.tsx | 1 | 2026-09-29 | 2026-09-29 | AI viết |
| src/components/ThuVienYKhoa.tsx | 2 | 2026-09-23 | 2026-09-23 | AI viết + Quân (Biên tập thư viện tra cứu nhanh tương tác thuốc và phác đồ điều trị tuyến cơ sở) |
| src/components/TinhTrangHeThong.tsx | 2 | 2026-09-23 | 2026-09-29 | AI viết |
| src/components/TraLoiCoNguon.tsx | 4 | 2026-09-23 | 2026-09-23 | AI viết |
| src/components/TranscriptView.tsx | 5 | 2026-09-22 | 2026-09-29 | AI viết + Quân (Tối ưu hóa giao diện hiển thị hội thoại bác sĩ - bệnh nhân theo luồng thời gian thực) |
| src/components/VerificationView.tsx | 6 | 2026-09-22 | 2026-09-23 | AI viết + Quân (Thiết kế thuật toán vẽ dây nối trực quan đối soát giữa lời thoại và mệnh đề SOAP) |
| src/data/mockData.ts | 1 | 2026-09-22 | 2026-09-22 | AI viết |
| src/index.css | 2 | 2026-09-22 | 2026-09-29 | AI viết |
| src/lib/ghepMenhDe.test.ts | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| src/lib/ghepMenhDe.ts | 1 | 2026-09-23 | 2026-09-23 | AI viết + Quân (Thiết kế thuật toán liên kết mệnh đề SOAP với mốc thời gian âm thanh phục vụ truy xuất nguồn gốc) |
| src/lib/mauVanBan.ts | 2 | 2026-09-23 | 2026-09-29 | AI viết |
| src/lib/mayTinh.test.ts | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| src/lib/mayTinh.ts | 1 | 2026-09-23 | 2026-09-23 | AI viết + Quân (Hiện thực hóa các thuật toán y khoa tính diện tích bề mặt cơ thể BSA và thanh thải Creatinine) |
| src/lib/nguoiNoi.test.ts | 1 | 2026-09-25 | 2026-09-25 | AI viết |
| src/lib/nguoiNoi.ts | 1 | 2026-09-25 | 2026-09-25 | AI viết |
| src/lib/taiKhoan.ts | 1 | 2026-09-24 | 2026-09-24 | AI viết |
| src/lib/useKho.ts | 1 | 2026-09-23 | 2026-09-23 | AI viết |
| src/main.tsx | 2 | 2026-09-22 | 2026-09-24 | AI viết |
| src/services/realAudioService.ts | 3 | 2026-09-22 | 2026-09-29 | AI viết |
| src/types.ts | 7 | 2026-09-22 | 2026-09-29 | AI viết |
|  |  |  |  |  |
| src/components/NhatKyTienTrinhAIModal.tsx | 3 | 2026-10-18 | 2026-10-18 | AI viết + Quân (Thiết kế Bảng Kiểm toán Tiến trình AI Dark Cybernetic Terminal) |
| src/components/ToDanDoBenhNhanModal.tsx | 3 | 2026-10-18 | 2026-10-18 | AI viết + Quân (Thiết kế Tờ Dặn Dò Người Bệnh Xuất Viện chuẩn Bệnh viện Quốc tế JCI / Vinmec) |

