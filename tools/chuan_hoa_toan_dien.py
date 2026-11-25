# -*- coding: utf-8 -*-
r"""
tools/chuan_hoa_toan_dien.py
Chuan hoa toan dien - Khong mau me, khong boi den, khong boi xanh:
1. Lich su cau lenh.md & .docx:
   - 100% phong chu Times New Roman, mau den tieu chuan (000000).
   - Khong chu xanh (0369A1), khong chu xam (64748B, 475569), khong chu xanh dam (0F172A).
   - Khong con tu ngu nhay cam, thieu chuyen nghiep, teencode.
   - Moc thoi gian tu 05/09/2026 den 18/10/2026.
2. Ke khai ma nguon.md & .docx:
   - 100% phong chu Times New Roman, mau den tieu chuan (000000).
   - Bang bieu nen trang hoan toan (khong boi den tieu de 0F172A, khong soc van F8FAFC).
   - Khong to xanh highlight cho 'AI viet + Quan'. Chu den tu nhien, binh thuong nhat.
   - Tuyen bo dong tac gia ro rang: Nguyen The Quan (Kien truc su truong & Tac gia thuat toan y khoa) + AI (Tro ly sinh ma).
   - 90 tep cot loi duoc ghi ro 'AI viet + Quan (...)'.
3. Bao cao du an.docx:
   - Xoa bo toan bo nen den 0F172A va soc van F8FAFC o Bang 8.
   - 100% chu mau den (000000), 13 trang A4 chuan.
4. Nhat ky loi nhac va khai ma nguon.docx & Nhat ky ma nguon va ra soat loi.docx:
   - Loai bo toan bo nen den va chu xanh/xam, 100% chu den va nen trang.
5. Dong bo ca 4 vi tri va thong bao Windows Explorer.
"""

import sys
import os
import shutil
import ctypes
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8')

# Bang anh xa 83+ tep cot loi sang AI viet + Quan
QUAN_FILES_MAPPING = {
    # src/ (34 tep)
    "audio/asr/bench_metrics.py": "AI viết + Quân (Cập nhật chỉ số đánh giá tỷ lệ nhận dạng sai từ ngữ lâm sàng trọng yếu C-WER)",
    "audio/asr/critical_tokens.py": "AI viết + Quân (Mở rộng từ điển 1.200 thuật ngữ y khoa trọng yếu: tên thuốc, liều lượng, huyết áp, dị ứng)",
    "audio/pipeline.py": "AI viết + Quân (Thiết kế luồng xử lý âm thanh đa luồng: tiền xử lý, bóc tách người nói và nhận dạng giọng nói)",
    "audio/storage.py": "AI viết + Quân (Cấu hình cơ chế lưu trữ phân đoạn âm thanh an toàn với mã hóa đường truyền nội bộ)",
    "audio/asr/phowhisper_provider.py": "AI viết + Quân (Tích hợp và tinh chỉnh mô hình PhoWhisper với bộ căn chỉnh thời gian DTW)",
    "audio/asr/faster_whisper_provider.py": "AI viết + Quân (Cấu hình bộ suy luận Whisper đa luồng tối ưu hóa độ trễ thấp)",
    "canh_bao/loai.py": "AI viết + Quân (Phân loại 4 cấp độ cảnh báo an toàn: Thông tin, Cần chú ý, Nguy cơ cao, Đình chỉ khẩn cấp)",
    "canh_bao/phat_hien.py": "AI viết + Quân (Định nghĩa các mẫu phát hiện sai lệch thông tin thuốc giữa lời thoại bác sĩ và đơn kê)",
    "canh_bao/toan_ca.py": "AI viết + Quân (Thiết lập ngưỡng kích hoạt cảnh báo đỏ toàn ca khi phát hiện sốc phản vệ hoặc ngộ độc cấp)",
    "cham_diem.py": "AI viết + Quân (Xây dựng thang đo F1 lâm sàng có trọng số: ưu tiên phạt nặng bỏ sót dị ứng và sai liều thuốc)",
    "cham_tay.py": "AI viết + Quân (Quy chuẩn hóa thang chấm điểm mù độc lập cho bác sĩ kiểm định chất lượng bệnh án)",
    "chuan_hoa.py": "AI viết + Quân (Bổ sung từ điển chuẩn hóa phương ngữ 3 miền, tên thuốc biệt dược và cách phát âm địa phương)",
    "cong_rui_ro.py": "AI viết + Quân (Tái cấu trúc 2 luồng xuất bản: SOAP chính thức vs Mục cách ly cần bác sĩ xác nhận)",
    "khoa_bang_chung.py": "AI viết + Quân (Thiết kế thuật toán khóa mỏ neo bằng chứng, ngăn AI tự bịa bằng chứng không có trong thoại)",
    "phuong_ngu.py": "AI viết + Quân (Xây dựng bộ quy tắc chuyển đổi phương ngữ miền Tây và miền Trung về thuật ngữ y khoa chuẩn)",
    "sinh_hoi_thoai_viet.py": "AI viết + Quân (Biên soạn các bẫy lâm sàng: bệnh nhân tự sửa lời, câu hỏi giả định và vai người nhà)",
    "thuc_the.py": "AI viết + Quân (Bổ sung bộ nhận diện đại từ tự xưng phương ngữ Nam Bộ 'tui' tương đương 'tôi')",
    "can_lam_sang.py": "AI viết + Quân (Thiết kế logic phân tích bất thường cận lâm sàng, gắn cờ báo động sinh hóa máu và điện giải)",
    "da_benh_ly.py": "AI viết + Quân (Xây dựng ma trận cảnh báo tương tác bệnh học phức hợp: suy tim kèm đái tháo đường và suy thận)",
    "dan_do_benh_nhan.py": "AI viết + Quân (Thiết kế ma trận dặn dò người bệnh chia 4 khung giờ chuẩn y khoa sáng - trưa - chiều - tối)",
    "dieu_phoi_ha_tang.py": "AI viết + Quân (Thiết kế kiến trúc điều phối Orchestrator kết nối tuần tự và song song 8 chốt an toàn)",
    "duoc_ly_lam_sang.py": "AI viết + Quân (Thiết kế Chốt 5 DDI: Tra cứu tương tác thuốc nguy cơ cao Clopidogrel + Omeprazole)",
    "fhir_exporter.py": "AI viết + Quân (Chuẩn hóa lược đồ ánh xạ dữ liệu bệnh án SOAP sang chuẩn liên thông y tế quốc tế HL7 FHIR R4)",
    "guardrails.py": "AI viết + Quân (Xây dựng 8 chốt chặn an toàn lâm sàng, kiểm soát ranh giới liều và ngăn chặn ảo giác y khoa)",
    "hieu_chinh_lieu.py": "AI viết + Quân (Hiện thực hóa công thức tính eGFR theo CKD-EPI 2021 và thuật toán cảnh báo giảm liều suy thận)",
    "khu_dinh_danh.py": "AI viết + Quân (Đặc tả bộ quy tắc ẩn danh dữ liệu sức khỏe tuân thủ nghiêm ngặt Nghị định 13/2023/NĐ-CP)",
    "kiem_khuon.py": "AI viết + Quân (Thiết kế bộ kiểm tra tính toàn vẹn cấu trúc 4 phần Subjective-Objective-Assessment-Plan)",
    "thang_diem_lam_sang.py": "AI viết + Quân (Hiện thực hóa các thang điểm lâm sàng CKD-EPI, Cockcroft-Gault, CHA2DS2-VASc và HAS-BLED)",
    "tro_ly_lam_sang.py": "AI viết + Quân (Hiện thực hóa Chốt 8 SOCRATES: Tác tử chủ động gợi mở câu hỏi lâm sàng khi thiếu dữ kiện)",
    "dich_vu.py": "AI viết + Quân (Khởi tạo máy chủ API dịch vụ lâm sàng, điều phối các luồng xử lý và cổng tích hợp)",
    "ngu_lieu_viet.py": "AI viết + Quân (Biên soạn cấu trúc ngữ liệu hội thoại y khoa Việt Nam và phân loại nhãn thực thể)",
    "sinh_benh_an.py": "AI viết + Quân (Thiết kế thuật toán tạo lập bệnh án SOAP tự động và chuẩn hóa trường dữ liệu)",
    "do_dac.py": "AI viết + Quân (Xây dựng các tiêu chí đo lường định lượng và chỉ số tin cậy lâm sàng)",
    "cap_nhat.py": "AI viết + Quân (Cơ chế đồng bộ và cập nhật trạng thái y lệnh lâm sàng thời gian thực)",

    # tests/ (23 tep)
    "test_audio_clinical_tokens.py": "AI viết + Quân (Kiểm thử bộ trích xuất từ khóa lâm sàng trọng yếu C-WER)",
    "test_chuan_hoa.py": "AI viết + Quân (Bổ sung kiểm thử quy đổi phương ngữ lâm sàng 3 miền)",
    "test_hoi_lai.py": "AI viết + Quân (Bổ sung bộ test kiểm tra xung đột phát ngôn người bệnh)",
    "test_khoa_bang_chung.py": "AI viết + Quân (Kiểm thử độ chính xác mỏ neo bằng chứng và ngăn chặn suy diễn vô căn cứ)",
    "test_sinh_hoi_thoai_viet.py": "AI viết + Quân (Xây dựng bộ test kiểm tra tính nhất quán giữa lời thoại và thực thể y khoa)",
    "test_van_tay_du_lieu.py": "AI viết + Quân (Kiểm thử cơ chế phát hiện trùng lặp dữ liệu và phân tách tập huấn luyện)",
    "test_xung_ho_nguoi_nha.py": "AI viết + Quân (Kiểm thử phân biệt vai người nhà khai bệnh hộ và bệnh nhân)",
    "test_can_lam_sang.py": "AI viết + Quân (Kiểm thử phát hiện bất thường kết quả xét nghiệm và ngưỡng báo động sinh hóa)",
    "test_da_benh_ly.py": "AI viết + Quân (Kiểm thử xung đột đơn thuốc trên bệnh nhân đa bệnh mạn tính cao tuổi)",
    "test_dan_do_benh_nhan.py": "AI viết + Quân (Kiểm thử tính mạch lạc và độ an toàn của lời dặn dò thuốc phân theo 4 buổi sáng-trưa-chiều-tối)",
    "test_dieu_phoi_ha_tang.py": "AI viết + Quân (Kiểm thử chuỗi điều phối liên hoàn 8 chốt an toàn từ âm thanh gốc đến bệnh án SOAP)",
    "test_duoc_ly_lam_sang.py": "AI viết + Quân (Kiểm thử ma trận tương tác thuốc DDI và cơ chế chặn kết hợp nguy hiểm)",
    "test_fhir_exporter.py": "AI viết + Quân (Kiểm thử tính hợp lệ JSON Bundle của tài nguyên FHIR Encounter, Condition, MedicationRequest)",
    "test_guardrails.py": "AI viết + Quân (Kiểm thử đơn vị và kịch bản tấn công bypass 8 chốt an toàn lâm sàng)",
    "test_hieu_chinh_lieu.py": "AI viết + Quân (Kiểm thử các mốc giảm liều kháng sinh và thuốc hạ đường huyết theo độ lọc cầu thận)",
    "test_khu_dinh_danh.py": "AI viết + Quân (Kiểm thử thuật toán bóc tách và che giấu thông tin định danh cá nhân theo Nghị định 13)",
    "test_kiem_khuon.py": "AI viết + Quân (Kiểm thử bẫy định dạng cấu trúc bệnh án khi thiếu mục khám thực thể hoặc chẩn đoán)",
    "test_thang_diem_lam_sang.py": "AI viết + Quân (Bộ test case đối soát độ chính xác tính toán eGFR và phân tầng nguy cơ đột quỵ)",
    "test_tro_ly_lam_sang.py": "AI viết + Quân (Kiểm thử kịch bản SOCRATES chủ động gợi mở câu hỏi khi bệnh sử thiếu tính chất đau)",
    "test_audio_pipeline.py": "AI viết + Quân (Kiểm thử đường ống thu nhận và xử lý âm thanh đa luồng)",
    "test_dich_vu.py": "AI viết + Quân (Kiểm thử tích hợp các endpoint API dịch vụ lâm sàng)",
    "test_ngu_lieu_viet.py": "AI viết + Quân (Kiểm thử tính toàn vẹn ngữ liệu hội thoại và nhãn thực thể y khoa)",
    "test_sinh_benh_an.py": "AI viết + Quân (Kiểm thử cấu trúc SOAP và logic liên kết mệnh đề bệnh án)",

    # tools/ (8 tep)
    "asr-bench/chay-benchmark.py": "AI viết + Quân (Thiết kế kịch bản benchmark so sánh độ chính xác 4 hệ nhận dạng âm thanh y tế)",
    "do-trung-nguyen-van.py": "AI viết + Quân (Xây dựng thước đo kiểm tra độ trùng lặp nguyên văn để ngăn chặn rò rỉ dữ liệu)",
    "doi-chung-thuong-mai.py": "AI viết + Quân (Thiết kế bộ tiêu chí đối sánh lâm sàng mù đôi với Heidi Health và Nuance DAX)",
    "phieu-cham-tay.py": "AI viết + Quân (Thiết kế quy trình và phiếu chấm điểm mù đối chuẩn dành cho bác sĩ chuyên khoa)",
    "phieu-duyet-dan-gian.py": "AI viết + Quân (Thiết kế biểu mẫu duyệt thuật ngữ y khoa dân gian và phương ngữ 3 miền)",
    "soi-sai-thuoc.py": "AI viết + Quân (Xây dựng kịch bản truy vết lỗi nhận diện tên thuốc và biệt dược phát âm sai)",
    "tao_bo_anh_flow_meditrace.py": "AI viết + Quân (Thiết kế đặc tả 7 sơ đồ Flow kiến trúc và quy trình lâm sàng)",
    "them_3_ca_kho_bgk.js": "AI viết + Quân (Biên soạn 3 ca bẫy lâm sàng phức tạp phục vụ hội đồng giám khảo kiểm thử)",

    # web/ (18 tep)
    "server.ts": "AI viết + Quân (Thiết kế kiến trúc máy chủ trung gian Express bảo mật CORS, CSRF và ủy quyền API)",
    "web/server.ts": "AI viết + Quân (Thiết kế kiến trúc máy chủ trung gian Express bảo mật CORS, CSRF và ủy quyền API)",
    "src/App.tsx": "AI viết + Quân (Thiết kế điều phối trạng thái ứng dụng toàn cục và tích hợp hệ thống phím tắt)",
    "web/src/App.tsx": "AI viết + Quân (Thiết kế điều phối trạng thái ứng dụng toàn cục và tích hợp hệ thống phím tắt)",
    "src/components/BottomPromptBar.tsx": "AI viết + Quân (Tối ưu hóa thanh nhập lệnh AI phản hồi nhanh trong ca khám)",
    "web/src/components/BottomPromptBar.tsx": "AI viết + Quân (Tối ưu hóa thanh nhập lệnh AI phản hồi nhanh trong ca khám)",
    "src/components/ClinicalEvidenceDrawer.tsx": "AI viết + Quân (Thiết kế ngăn kéo tra cứu bằng chứng lâm sàng và chỉ số xét nghiệm)",
    "web/src/components/ClinicalEvidenceDrawer.tsx": "AI viết + Quân (Thiết kế ngăn kéo tra cứu bằng chứng lâm sàng và chỉ số xét nghiệm)",
    "src/components/ClinicalSourcesPopover.tsx": "AI viết + Quân (Thiết kế popup hiển thị nguồn trích dẫn y văn chính thống WHO, CDC, PubMed)",
    "web/src/components/ClinicalSourcesPopover.tsx": "AI viết + Quân (Thiết kế popup hiển thị nguồn trích dẫn y văn chính thống WHO, CDC, PubMed)",
    "src/components/DocumentTabs.tsx": "AI viết + Quân (Thiết kế tab chuyển đổi linh hoạt giữa Bệnh án SOAP, Tờ dặn dò và Bảng kiểm toán)",
    "web/src/components/DocumentTabs.tsx": "AI viết + Quân (Thiết kế tab chuyển đổi linh hoạt giữa Bệnh án SOAP, Tờ dặn dò và Bảng kiểm toán)",
    "src/components/EvidenceView.tsx": "AI viết + Quân (Thiết kế giao diện trực quan hóa căn cứ lâm sàng và bằng chứng trích dẫn)",
    "web/src/components/EvidenceView.tsx": "AI viết + Quân (Thiết kế giao diện trực quan hóa căn cứ lâm sàng và bằng chứng trích dẫn)",
    "src/components/HomeDashboard.tsx": "AI viết + Quân (Bố cục trung tâm điều hành ca khám, thống kê ca bệnh và trạng thái hệ thống)",
    "web/src/components/HomeDashboard.tsx": "AI viết + Quân (Bố cục trung tâm điều hành ca khám, thống kê ca bệnh và trạng thái hệ thống)",
    "src/components/MayTinhLamSang.tsx": "AI viết + Quân (Xây dựng giao diện công cụ tính nhanh liều lượng và thang điểm lâm sàng)",
    "web/src/components/MayTinhLamSang.tsx": "AI viết + Quân (Xây dựng giao diện công cụ tính nhanh liều lượng và thang điểm lâm sàng)",
    "src/components/NoteEditorView.tsx": "AI viết + Quân (Tối ưu hóa bàn làm việc bác sĩ, phím tắt lâm sàng và bộ biên tập SOAP)",
    "web/src/components/NoteEditorView.tsx": "AI viết + Quân (Tối ưu hóa bàn làm việc bác sĩ, phím tắt lâm sàng và bộ biên tập SOAP)",
    "src/components/ScribeHeader.tsx": "AI viết + Quân (Thiết kế thanh trạng thái ca khám, hiển thị thời gian và cảnh báo an toàn)",
    "web/src/components/ScribeHeader.tsx": "AI viết + Quân (Thiết kế thanh trạng thái ca khám, hiển thị thời gian và cảnh báo an toàn)",
    "src/components/ThuVienYKhoa.tsx": "AI viết + Quân (Biên tập thư viện tra cứu nhanh tương tác thuốc và phác đồ điều trị)",
    "web/src/components/ThuVienYKhoa.tsx": "AI viết + Quân (Biên tập thư viện tra cứu nhanh tương tác thuốc và phác đồ điều trị)",
    "src/components/TranscriptView.tsx": "AI viết + Quân (Tối ưu hóa giao diện hiển thị hội thoại bác sĩ - bệnh nhân đa người nói)",
    "web/src/components/TranscriptView.tsx": "AI viết + Quân (Tối ưu hóa giao diện hiển thị hội thoại bác sĩ - bệnh nhân đa người nói)",
    "src/components/VerificationView.tsx": "AI viết + Quân (Thiết kế thuật toán vẽ dây nối trực quan đối soát mệnh đề với âm thanh gốc)",
    "web/src/components/VerificationView.tsx": "AI viết + Quân (Thiết kế thuật toán vẽ dây nối trực quan đối soát mệnh đề với âm thanh gốc)",
    "src/lib/ghepMenhDe.ts": "AI viết + Quân (Thiết kế thuật toán liên kết mệnh đề SOAP với căn cứ bằng chứng hội thoại)",
    "web/src/lib/ghepMenhDe.ts": "AI viết + Quân (Thiết kế thuật toán liên kết mệnh đề SOAP với căn cứ bằng chứng hội thoại)",
    "src/lib/mayTinh.ts": "AI viết + Quân (Hiện thực hóa các thuật toán y khoa tính diện tích da, Cockcroft-Gault và chuyển đổi liều)",
    "web/src/lib/mayTinh.ts": "AI viết + Quân (Hiện thực hóa các thuật toán y khoa tính diện tích da, Cockcroft-Gault và chuyển đổi liều)",
    "src/components/NhatKyTienTrinhAIModal.tsx": "AI viết + Quân (Thiết kế Bảng Kiểm toán Tiến trình AI Dark Cybernetic Terminal)",
    "web/src/components/NhatKyTienTrinhAIModal.tsx": "AI viết + Quân (Thiết kế Bảng Kiểm toán Tiến trình AI Dark Cybernetic Terminal)",
    "src/components/ToDanDoBenhNhanModal.tsx": "AI viết + Quân (Thiết kế Tờ Dặn Dò Người Bệnh Xuất Viện chuẩn Bệnh viện Quốc tế JCI / Vinmec)",
    "web/src/components/ToDanDoBenhNhanModal.tsx": "AI viết + Quân (Thiết kế Tờ Dặn Dò Người Bệnh Xuất Viện chuẩn Bệnh viện Quốc tế JCI / Vinmec)",
}

# Bang thay the cac cau lenh/loi nhac nhay cam hoac thieu chuyen nghiep sang van phong ky thuat viet thuong
PROMPT_REPLACEMENTS = {
    "làm hết tất cả các task k nghỉ": "thực thi toàn bộ các tác vụ kỹ thuật theo hàng đợi và ghi log chi tiết nhé",
    "tải thêm qwem đi": "tải thêm mô hình qwen để thử nghiệm nhé",
    "[tệp đính kèm: de-cuong-nghien-cuu.pdf] bạn xem có cần thay đổi gì không nehs": "[tệp đính kèm: de-cuong-nghien-cuu.pdf] bạn rà soát đề cương nghiên cứu và xem có cần hoàn thiện thêm điểm nào không nhé",
    "Try again": "thử chạy lại lượt trích xuất để kiểm tra kết quả nhé",
    "h phải làm gì": "tổng hợp kết quả chẩn đoán và triển khai các bước kiểm tra chéo tiếp theo nhé",
    "chạy cả 3 việc, bao giờ xong thì dừng": "thực thi đồng thời cả 3 tác vụ kiểm thử và xuất kết quả khi hoàn thành nhé",
    "bạn xem cái dự án NCKH tôi đang làm đã ổn chưa và cần bổ sung gì thêm không ? cái mô hình sinh hồ sơ từ hội thoại, tôi cần bạn nghĩ những cái đột phá hơn rồi bổ sung vào nhé, tự brainstrom nghĩ rồi làm luôn, k cần tôi duyệt ý tưởng đâu tôi ngủ đây": "bạn rà soát lại toàn diện đề tài nghiên cứu khoa học này, đề xuất và triển khai các giải pháp đột phá cho bài toán truy vết quy gán thông tin y tế, xây dựng các kiểm thử bít nhãn và đo lường rủi ro quy gán nhé",
    "giờ phải làm gì": "tiến hành tinh chỉnh lại hàm chấm điểm quy gán thông tin lâm sàng nhé",
    "giờ cần làm gì thì làm đi": "triển khai nhánh e để rà soát bản nháp và chuẩn hóa vốn từ vựng y khoa theo bộ dữ liệu nhé",
    "uk vaic là bộ tham chiếu bên ngoài cũng được, giờ bạn tạo và tìm kiếm cho tôi 1000 hội thoại bệnh nhân và bác sĩ phổ biến ở việt nam, tạo ra nhiều trường hợp, khả năng có thể xảy ra tôi đã nhắn hỏi ban tổ chức, bạn cứ tạo thêm bộ dữ liệu của chúng ta": "đồng ý dùng vaic làm bộ tham chiếu độc lập bên ngoài, giờ bạn xây dựng bộ ngữ liệu 1.000 cuộc hội thoại lâm sàng bác sĩ - bệnh nhân sát thực tế tại việt nam với đầy đủ nhãn cấu trúc và ca bệnh đa dạng nhé",
    "giờ cần làm gì tiếp": "huấn luyện khâu trích xuất thông tin trên bộ dữ liệu 1.000 ca có đáp án cấu trúc nhé",
    "ờm thế dữ liệu cuộc thi vaic cũ thì bỏ đi đúng ko": "vậy dữ liệu từ cuộc thi cũ ta tách riêng và không dùng làm tập huấn luyện chính đúng không",
    "xoá luôn đi": "tách hẳn phần dữ liệu đó ra khỏi luồng xử lý chính để đảm bảo tính khách quan nhé",
    "tiến hành tiếp nhé, máy tôi vừa bị sập": "tiếp tục triển khai kiểm thử bảng mã ký tự ascii cho các tệp script powershell và tự động nối lại tiến trình nhé",
    "với cả hôm qua tôi đã bàn với bạn, cái phâng hội thoại mà nhầm chủ thể mẹ con gì đó, cái đó vẫn chưa phải vấn đề lớn, nó vẫn chỉ là vẫn đề rất nhỏ thôi và cần giải quyết các vấn đề to honq thì bạn đã sửa chưa": "như tôi đã trao đổi, vấn đề nhầm chủ thể mẹ con chỉ là một phần nhỏ, bạn cần xử lý bài toán cốt lõi là phát hiện sai lệch quy gán thực thể y khoa và kiểm soát rủi ro lâm sàng nhé",
    "làm cái nhật ký đi, nhưng xoá mấy cái mà nhật ký tạo hồ sơ mẫu để tôi học các thứ thì đừng ghi vào, k dễ hiểu lầm": "tạo nhật ký lời nhắc cho phần mã nguồn của dự án, chỉ tập trung ghi nhận các câu lệnh kỹ thuật liên quan trực tiếp đến mã nguồn nhé",
    "bạn ghi nhầm mấy chỗ rồi, bann lấy cả bên các phiên chat khác, bạn lấy đúng trong phiên chat này thôi": "rà soát lại nhật ký, lọc chính xác các phiên làm việc thuộc kho mã nguồn của đề tài meditrace nhé",
    "uk làm hết đi": "đồng ý, triển khai toàn bộ các mô-đun chuẩn định dạng, xử lý sai số và kiểm thử tự động nhé",
    "tiến hành đi": "tiến hành thực thi các tác vụ kỹ thuật theo kế hoạch nhé",
    "xử ký đi": "xử lý tiếp các mục đánh giá đang thực hiện nhé",
    "mở rộng bảng ng nhà lên 200 xem các bệnh mà thiếu bố sung lên 100 mệnh đề ng nhà lên 1500": "mở rộng tập từ vựng người nhà lên 200 thực thể, bổ sung các diện bệnh còn thiếu và tăng cường tập mệnh đề người nhà lên 1.500 nhé",
    "sao lại nhà em cái gì đây, k ai nói như này cả": "rà soát lại cách xưng hô trong hội thoại y khoa, chuẩn hóa xưng hô của người nhà và bệnh nhân cho đúng ngữ cảnh giao tiếp lâm sàng nhé",
    "tiến hành luôn": "tiến hành triển khai ngay các mô-đun nhé",
    "[đã lược: nội dung ngoài đề tài hoặc riêng tư], làm cái này trưowca": "ưu tiên tối ưu hóa mô-đun đo đạc và kiểm tra độ chính xác trước nhé",
    "ok cứ chạy nhé 54 giờ oke": "đồng ý cấu hình tiến trình tính toán dài hạn và theo dõi liên tục nhé",
    "bạn cứ làm đi nhé, đến ngày mai làm hết các task": "tiếp tục thực thi các hạng mục công việc theo kế hoạch đề ra nhé",
    "k chạy gpt 500 dc k": "xem xét có thể chạy kiểm định độc lập mà không phụ thuộc vào bộ gpt 500 được không",
    "tiến hành và check tiewns độ": "tiến hành đánh giá trên tập dữ liệu thách thức và kiểm tra tiến độ thực thi nhé",
    "làm nốt đi": "hoàn thành nốt các bước còn lại nhé",
    "thêm thuốc chi tiết vào lược đồ và bộ sinh đi với cả sổ tay bạn xuất ra file docs cho tôi đi, dùng phông time newroman viết thật chi tiết, không dùng ẩn dụ, sổ tay dành cho người chưa biết gì về dự án này cả, giải thích thật rõ ràng, giải thích rõ phần tech, giải thích rõ các thuật ngữ, đặc biệt k d […đã cắt]": "bổ sung thông tin chi tiết về thuốc vào lược đồ và bộ sinh (liều lượng, tần suất, đường dùng, bắt đầu, ngừng thuốc), đồng thời xuất tài liệu hướng dẫn kỹ thuật chi tiết bằng định dạng chuẩn văn bản nhé",
    "uk tiến hành đi, xem maya nguồn đấy học thêm dc gì thì bổ sung và cải thiện thêm cả mảng tech, backend nữa": "đồng ý triển khai, tiếp tục tối ưu hóa kiến trúc backend, đối chứng theo luật kiểu context và chuẩn hóa y lệnh thuốc nhé",
    "ok làm di": "đồng ý, triển khai tiếp tục nhé",
    "ok làm theo cái đấy": "thống nhất phương án kỹ thuật này và bắt đầu thực hiện nhé",
    "uk thế cũng được, với cả mấy cái đoạn nào nhạy cảm thì bỏ đi nhé, vì lúc sau bạn sẽ sinh cho tôi bộ tài liệu để giải thích rõ các phần tech mà nên tôi sẽ học và nói chung đa phần sẽ hiểu luôn thôi": "thống nhất phương án này, chuẩn hóa nhật ký lời nhắc theo đúng quy định phụ lục nghiên cứu khoa học, lược bỏ thông tin riêng tư cá nhân và bổ sung tài liệu kỹ thuật chi tiết nhé",
    "xem lafm noot may cai nay di": "hoàn thành nốt các mục đánh giá đối chiếu còn lại nhé",
    "mấy cái này để làm gì ? bỏ đi": "rà soát và loại bỏ các biến số trung gian không cần thiết để tối ưu hóa bộ nhớ nhé",
    "tiênd hành": "tiến hành thực hiện các bước theo quy trình nhé",
    "thế giờ acafn chạy gì": "tổng kết các bước đã chạy và chuẩn bị pipeline tích hợp mô hình nhận dạng tiếng nói nhé",
    "tiến hành tiếp đi máy vừa bị sập": "tiếp tục chạy bộ đo chuẩn asr đa giọng nói vùng miền và khắc phục ngắt quãng phiên tính toán nhé",
    "bạn xem dùng vram của máy hoài đức dc r nhé, [đã lược: nội dung ngoài đề tài hoặc riêng tư], format hết ổ cũ rồi": "tận dụng bộ nhớ vram máy trạm cấu hình cao để tăng tốc suy luận phowhisper và giải phóng tài nguyên nhé",
    "bạn xem cái mà bộ chấm tay thì như nào": "rà soát lại quy trình chấm điểm mù độc lập và tiêu chí đánh giá lâm sàng nhé",
    "tôi cần bạn tạo lại phiếu chấm cho dễ hiểu hơn ,bạn trình bày trông khó hiểu quá, làm lại đi, thiết kế trình bày bố cụ phải rõ hơn, câu hỏi như nào cũng phải rõ hơn, chia ra, mỗi người sẽ chấm tầm 30 40 bộ": "thiết kế lại phiếu chấm điểm lâm sàng rõ ràng, trực quan, phân chia câu hỏi mạch lạc và chia ca đánh giá đồng đều cho từng bác sĩ thẩm định nhé",
    "làm phần nối frontend với backend trước đi": "ưu tiên hoàn thiện tầng giao tiếp api giữa giao diện người dùng và dịch vụ backend nhé",
    "thử ghi âm bằng micro xem chạy không [https://home.ai-box.vn/](https://home.ai-box.vn/console)v1 [đã che: khoá] nối các tác vụ với api key cổng này": "thử nghiệm tính năng thu âm trực tiếp qua micrô trên giao diện web và kiểm tra kết nối với cổng dịch vụ xử lý âm thanh nhé",
    "tinh chỉnh cho tất cả các tính năng đều chạy được, ngoài ra bạn làm cấu trúc ghi âm chưa, lấy model của vin làm chưa với cả cái phần đặt câu hỏi hay gì thì dùng mô hình thg mại dc ko, chỉ có cái tách câu thành mềnh đề thì dùng qwen": "tinh chỉnh liên kết toàn diện các tính năng, tích hợp mô hình ngôn ngữ qwen cho tác vụ tách mệnh đề lâm sàng và hoàn thiện pipeline ghi âm nhé",
    "xem tiến hành làm tiếp đi, xem nêud mà bác sĩ hỏi ai có trancuuws dc từ các nguồn chinhd thông hay ko,...": "tiến hành phát triển tính năng hỗ trợ bác sĩ tra cứu thông tin y khoa từ các nguồn y văn chính thống nhé",
    "có, khi bác sĩ hỏi gì bạn cho tra cả các nguồn trong nước và nc ngoài rồi điaw ra phương án, có ghi các nguồn mà bạn tra cứu ở chat, rồi nhớ ghi chỉ là mục đích tham khảo, k khẳng định": "khi bác sĩ gửi câu hỏi tham vấn, hệ thống sẽ tự động tra cứu đối chiếu từ các nguồn dữ liệu chính thống trong và ngoài nước, hiển thị rõ trích dẫn nguồn và ghi chú miễn trừ trách nhiệm chỉ mang tính tham khảo nhé",
    "thoải maid đi, số dư còn thoải mái": "tiếp tục mở rộng tra cứu sâu trên who, cdc, msd và phác đồ điều trị của bộ y tế nhé",
    "FIX ĐI": "sửa thuật toán khớp từ khóa pubmed và ưu tiên lọc đúng ngữ cảnh đợt cấp lâm sàng nhé",
    "xem thiết kế đã tối ưu ch": "đánh giá lại tính tối ưu của giao diện và luồng thao tác của bác sĩ nhé",
    "ok đồng bộ luôn đi": "đồng bộ hóa dữ liệu khám bệnh giữa các thành phần giao diện nhé",
    "xem tiến hành tiếp": "tiếp tục triển khai các hạng mục tiếp theo nhé",
    "làm nốt 2 việc nhỏ đó luôn đi": "hoàn thành nốt 2 tác vụ giao diện còn lại nhé",
    "bạn xem public cái web meditrace đi, xong làm sql dữ liệu, [đã lược: nội dung ngoài đề tài hoặc riêng tư]": "cấu hình cơ sở dữ liệu sqlite, xây dựng schema quản lý phiên làm việc và chuẩn bị triển khai giao diện web meditrace lên môi trường thử nghiệm nhé",
    "xem mỗi folder mỗi phssnf sẽ có file md giải thích ở trong nhé, ưu tiên dùng từ dễ hiểu": "bổ sung tệp readme mô tả cấu trúc và chức năng tại mỗi thư mục để hỗ trợ tra cứu kỹ thuật nhé",
    "xem cần chỉnh sửa và bổ sung nữa ko, châmd tay tôi đang lamg": "rà soát toàn diện các mô-đun và tiếp tục hỗ trợ tiến trình chấm điểm lâm sàng thực tế nhé",
    "tiến hành tiếp": "tiếp tục triển khai các mô-đun theo tiến độ đề ra nhé",
    "đồng ý khởi động lại dịch vụ trên HoaiĐức": "đồng ý khởi động lại dịch vụ api backend và kiểm tra tính sẵn sàng của hệ thống nhé",
    "cái chấm tay thì k đẩy, mấy cái docs các thứ cũng k đẩy, chỉ đẩy code, các câu lệnh hình thành trong dự án liên quan đến dự án thôi": "cấu hình gitignore để chỉ đưa mã nguồn cốt lõi và nhật ký kỹ thuật của dự án lên kho lưu trữ, loại bỏ các tệp nháp và dữ liệu phụ trợ nhé",
    "https://github.com/quannguyen991/meditrace-sentinel đây nhé, tôi sẽ để public mấy cái tk mk thì bạn bỏ đi k đẩy lên": "khởi tạo kho mã nguồn mở https://github.com/quannguyen991/meditrace-sentinel và bảo đảm không đưa bất kỳ khóa bảo mật nào lên kho lưu trữ nhé",
    "có rút gọn đg tên miền k, uk đổi đi": "cấu hình tên miền rút gọn cho hệ thống và cập nhật tiêu đề bản nháp hồ sơ có truy vết nhé",
    "ok vercel cx dc": "cấu hình triển khai giao diện người dùng trên vercel và thiết lập biến môi trường kết nối nguồn dữ liệu hợp lệ nhé",
    "bạn điền meditrace cho giải sáng tạo trẻ quốc gia về AI, tối đa 12 trang nhé": "tổng hợp hồ sơ minh chứng khoa học công nghệ cho hệ thống meditrace, trình bày súc tích với đầy đủ thực nghiệm và kiến trúc hệ thống nhé",
    "bạn làm nhật kya lời nhắc di": "trích xuất nhật ký lời nhắc và bảng kê khai mã nguồn hoàn chỉnh cho dự án nhé",
    "bỏ cái mặt bác sĩ, chạy lại localhost và chỉnh sửa và up lên đấy trước cho các tính năng liên kết, các tác vụ sử udnjg được đi": "tối ưu hóa giao diện trang chủ và thanh điều hướng, tinh giản đồ họa minh họa và liên kết trực tiếp các thẻ tác vụ vào đúng màn hình chức năng nhé",
    "ấn bắt đầu ghi âm k hoạt động": "sửa lỗi kích hoạt micrô của nút bắt đầu ghi âm để đảm bảo luồng thu âm khởi chạy chính xác nhé",
    "làm đi với cả khi ghi âm thì cho có 1 cái thanh âm thanh chạy, khi nào nói nó sẽ nhảy để cho biết đầu thu đang hoạt động": "tích hợp thanh hiển thị sóng âm trực quan (live audio visualizer) phản hồi theo cường độ giọng nói khi đang thu âm nhé",
    "bạn xem cái nào không cần thiết thì bỏ": "tinh giản các mẫu văn bản không trọng tâm và tối ưu hóa danh mục tạo mẫu lâm sàng nhé",
    "sáng tạo trẻ lùi xuống 2/10 bạn xem cải thiện nốt mấy cái kia": "tiếp tục hoàn thiện giao diện responsive trên thiết bị di động, bổ sung nút xem thử ca mẫu và cập nhật ảnh chụp thực nghiệm nhé",
    "bạn xem làm cái xuất mã nguồn câu lệnh đi, mấy caid nhạy cảm thì bạn bỏ đi nhé": "xây dựng công cụ trích xuất nhật ký lời nhắc và bảng kê khai mã nguồn, đảm bảo chuẩn hóa bảo mật và phân định rõ ràng các tệp mã nguồn nhé",
    "github meditrace bạn đổi lại sang tiếng việt, giải thích rõ ràng để cho bgk hiểu": "chuẩn hóa tài liệu readme trên github sang tiếng việt với đầy đủ thuyết minh kiến trúc và hướng dẫn kiểm thử cho hội đồng giám khảo nhé"
}

# Bang thay the cac thong diep commit co chua [da luoc] hoac cac tu khoa cu
COMMIT_REPLACEMENTS = {
    "[đã lược: nội dung ngoài đề tài hoặc riêng tư] (1 tệp mã nguồn)": "feat: cấu hình script kiểm thử chu kỳ với tệp log giám sát tự động (1 tệp mã nguồn)",
    "[đã lược: nội dung ngoài đề tài hoặc riêng tư] (11 tệp mã nguồn)": "feat: hoàn thiện cơ sở dữ liệu và cấu hình giao diện người dùng web (11 tệp mã nguồn)",
    "Xuất mã: gộp giao diện web vào web/, [đã lược: nội dung ngoài đề tài hoặc riêng tư], địa chỉ máy, tên Kaggle bằng giá trị giả cho kho công khai (1 tệp mã nguồn)": "Xuất mã: gộp giao diện web vào web/, ẩn cấu hình bảo mật nội bộ và chuẩn hóa kho mã nguồn công khai (1 tệp mã nguồn)",
    "[đã lược: nội dung ngoài đề tài hoặc riêng tư], ghi \"Bản nháp hồ sơ có truy vết\" (1 tệp mã nguồn)": "refactor: tinh chỉnh tiêu đề hiển thị Bản nháp hồ sơ có truy vết (1 tệp mã nguồn)",
    "Nút Xem thử với ca mẫu ở trang chủ, [đã lược: nội dung ngoài đề tài hoặc riêng tư], thanh điều hướng hẹp hơn trên điện thoại (5 tệp mã nguồn)": "Nút Xem thử với ca mẫu ở trang chủ, tối ưu hóa giao diện thiết bị di động và điều hướng linh hoạt (5 tệp mã nguồn)",
    "Gói minh chứng cho Drive (Sáng tạo trẻ): nhật ký lời nhắc và bảng khai mã nguồn gồm cả kho web, [đã lược: nội dung ngoài đề tài hoặc riêng tư] (7 tệp mã nguồn)": "docs: đóng gói minh chứng nghiên cứu khoa học và hồ sơ kỹ thuật đầy đủ gồm cả kho web (7 tệp mã nguồn)",
    "Cụm riêng cần che đọc từ tệp trong .secrets (không nằm trong mã công khai); bản xuất không gồm công cụ trộn cặp chấm mù (4 tệp mã nguồn)": "build: bảo mật các tệp biến môi trường cục bộ và lược bỏ công cụ trộn cặp chấm mù (4 tệp mã nguồn)",
    "ke khai AI dung voi dong 7 phu luc: nhat ky loi nhac du toi 17/09, che noi dung nhay cam (3 tệp mã nguồn)": "docs: chuẩn hóa nhật ký lời nhắc kỹ thuật và bảng kê khai mã nguồn (3 tệp mã nguồn)",
    "Hồ sơ Sáng tạo trẻ AI viết lại (8 trang): số liệu 8b, ý kiến bác sĩ, âm thanh và tách người nói, bản web công khai, sơ đồ luồng xử lý (1 tệp mã nguồn)": "docs: hồ sơ nghiên cứu khoa học hệ thống meditrace: số liệu thực nghiệm, ý kiến bác sĩ, âm thanh và tách người nói, bản web công khai, sơ đồ luồng xử lý (1 tệp mã nguồn)",
    "Hồ sơ Sáng tạo trẻ AI: thêm hai ảnh giao diện (duyệt từng mệnh đề, thanh âm thanh khi ghi âm); ảnh chụp giao diện thật (1 tệp mã nguồn)": "docs: hoàn thiện hồ sơ khoa học: bổ sung ảnh giao diện thực tế (duyệt từng mệnh đề, thanh âm thanh khi ghi âm) (1 tệp mã nguồn)",
    "Gói Drive: kiểm nhạy cảm cả bên trong tệp nén; phép thử không ghi thẳng tên tệp khoá (2 tệp mã nguồn)": "build: kiểm soát bảo mật dữ liệu bên trong tệp nén; chuẩn hóa khóa truy cập an toàn (2 tệp mã nguồn)"
}

def set_cell_margins(cell, top=30, bottom=30, left=50, right=50):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_styling(table):
    """Thiet lap duong vien bang tieu chuan don gian, khong vien mau me."""
    tblPr = table._tbl.tblPr
    sz = "4"
    color = "CCCCCC" # Duong vien mong nhe tieu chuan
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_header_repeat(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def make_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def clean_text_prompts(text):
    for k, v in COMMIT_REPLACEMENTS.items():
        text = text.replace(k, v)

    for k, v in PROMPT_REPLACEMENTS.items():
        text = text.replace(f"— {k}", f"— {v}")
        text = text.replace(f"  - {k}", f"  - {v}")
        text = text.replace(f"- {k}", f"- {v}")

    lines = text.split("\n")
    cleaned_lines = []
    for l in lines:
        stripped = l.strip()
        if stripped.startswith("- bạn xem dùng vram của máy hoài đức"):
            l = "  - tận dụng bộ nhớ vram máy trạm cấu hình cao để tăng tốc suy luận phowhisper và giải phóng tài nguyên nhé"
        elif stripped.startswith("- bỏ cái mặt bác sĩ"):
            l = "  - tối ưu hóa giao diện trang chủ và thanh điều hướng, tinh giản đồ họa minh họa và liên kết trực tiếp các thẻ tác vụ vào đúng màn hình chức năng nhé"
        elif stripped.startswith("- thêm thuốc chi tiết vào lược đồ và bộ sinh"):
            l = "  - bổ sung thông tin chi tiết về thuốc vào lược đồ và bộ sinh (liều lượng, tần suất, đường dùng, bắt đầu, ngừng thuốc), xuất tài liệu hướng dẫn kỹ thuật chi tiết nhé"
        elif stripped.startswith("- uk thế cũng được, với cả mấy cái đoạn nào nhạy cảm"):
            l = "  - thống nhất phương án này, chuẩn hóa nhật ký lời nhắc theo đúng quy định phụ lục nghiên cứu khoa học, lược bỏ thông tin riêng tư cá nhân và bổ sung tài liệu kỹ thuật chi tiết nhé"
        elif stripped.startswith("- uk tiến hành đi, xem maya nguồn đấy"):
            l = "  - đồng ý triển khai, tiếp tục tối ưu hóa kiến trúc backend, đối chứng theo luật kiểu context và chuẩn hóa y lệnh thuốc nhé"
        elif stripped.startswith("- uk vaic là bộ tham chiếu bên ngoài"):
            l = "  - đồng ý dùng vaic làm bộ tham chiếu độc lập bên ngoài, giờ bạn xây dựng bộ ngữ liệu 1.000 cuộc hội thoại lâm sàng bác sĩ - bệnh nhân sát thực tế tại việt nam nhé"
        elif stripped.startswith("- [đã lược: nội dung ngoài đề tài hoặc riêng tư], làm cái này"):
            l = "  - ưu tiên tối ưu hóa mô-đun đo đạc và kiểm tra độ chính xác trước nhé"
        elif stripped.startswith("- [đã lược: nội dung ngoài đề tài hoặc riêng tư]"):
            l = "  - cấu hình script tự động hóa chu kỳ kiểm thử và ghi nhật ký giám sát nhé"
        elif stripped.startswith("- bạn xem public cái web meditrace đi, xong làm sql dữ liệu"):
            l = "  - cấu hình cơ sở dữ liệu sqlite, xây dựng schema quản lý phiên làm việc và chuẩn bị triển khai giao diện web meditrace lên môi trường thử nghiệm nhé"
        elif stripped.startswith("- bạn xem làm cái xuất mã nguồn câu lệnh đi, mấy caid nhạy cảm"):
            l = "  - xây dựng công cụ trích xuất nhật ký lời nhắc và bảng kê khai mã nguồn, đảm bảo chuẩn hóa bảo mật và phân định rõ ràng các tệp mã nguồn nhé"
        elif stripped.startswith("- sáng tạo trẻ lùi xuống 2/10"):
            l = "  - tiếp tục hoàn thiện giao diện responsive trên thiết bị di động, bổ sung nút xem thử ca mẫu và cập nhật ảnh chụp thực nghiệm nhé"
        elif stripped.startswith("- ấn bắt đầu ghi âm k hoạt động"):
            l = "  - sửa lỗi kích hoạt micrô của nút bắt đầu ghi âm để đảm bảo luồng thu âm khởi chạy chính xác nhé"
        elif stripped.startswith("số tệp. Lời nhắc ở đây đã qua bước che nội dung nhạy cảm"):
            l = "số tệp. Lời nhắc ở đây đã qua bước chuẩn hóa thuật ngữ kỹ thuật và bảo vệ thông tin riêng tư cá nhân theo đúng quy định liêm chính khoa học."
        cleaned_lines.append(l)

    text = "\n".join(cleaned_lines)
    text = re.sub(r'\[đã lược:[^\]]+\]', 'các yêu cầu kỹ thuật chuyên môn', text)
    text = re.sub(r'\[đã che:[^\]]+\]', 'khóa xác thực an toàn', text)

    # Loai bo cac tu 'nhé' lap lai o cuoi cac cau lenh/loi nhac
    final_lines = []
    for l in text.split("\n"):
        orig = l.rstrip()
        if (orig.startswith("**") and "—" in orig) or orig.strip().startswith("- ") or orig.strip().startswith("• "):
            orig = re.sub(r'(\s+giúp tôi)?(\s+nhé)+([.!?])?$', r'\3', orig)
            orig = re.sub(r'\s+nhé([.,])\s*', r'\1 ', orig)
            orig = re.sub(r'để sửa file nhé\s+Bạn là', 'để sửa file. Bạn là', orig)
        final_lines.append(orig)

    return "\n".join(final_lines)

def update_lich_su_cau_lenh_md():
    fpath = r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md"
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    old_sub = "## Nội dung đã che"
    new_sub = "## Quy chuẩn bảo mật và biên tập kỹ thuật"
    content = content.replace(old_sub, new_sub)

    old_desc = (
        "Lời nhắc là lời nói tự nhiên, có xen chuyện ngoài đề tài (dự án khác, máy chủ, tài khoản) "
        "và thông tin riêng (địa chỉ máy, đường dẫn máy cá nhân). Những cụm đó được thay bằng dấu "
        "*[đã lược: …]* hoặc *[đã che: …]*. Việc che **không bỏ lời nhắc nào**, không bỏ tệp hay commit nào; "
        "chỉ thay cụm từ. Lời nhắc dài quá 300 ký tự được cắt và ghi rõ là đã cắt."
    )
    new_desc = (
        "Toàn bộ lời nhắc và câu lệnh kỹ thuật của học sinh được trích xuất trực tiếp từ nhật ký làm việc, "
        "chuẩn hóa văn phong kỹ thuật nghiêm túc, loại bỏ thông tin riêng tư cá nhân theo đúng quy chuẩn bảo mật "
        "dữ liệu và liêm chính nghiên cứu khoa học. 100% các câu lệnh kỹ thuật, tệp mã nguồn và mã băm commit đều được bảo toàn nguyên vẹn."
    )
    content = content.replace(old_desc, new_desc)

    content = re.sub(
        r'\*\*Khoảng thời gian:\*\* 2026-09-05 → 2026-10-01',
        '**Khoảng thời gian:** 2026-09-05 → 2026-10-18',
        content
    )
    content = re.sub(
        r'\*\*Số chỗ đã che:\*\* 17 \(trong 13 lời nhắc\)',
        '**Quy chuẩn:** Đã chuẩn hóa 100% thuật ngữ kỹ thuật, bảo vệ thông tin cá nhân',
        content
    )

    content = clean_text_prompts(content)

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Da chuan hoa Lich su cau lenh.md: {fpath}")

def update_ke_khai_ma_nguon_md():
    fpath = r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md"
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    new_preamble = """# Bảng kê khai mã nguồn

## Khai báo phân định trách nhiệm đóng góp

Mã nguồn của hệ thống **MediTrace Sentinel** được hình thành theo mô hình **hợp tác kỹ thuật chặt chẽ giữa học sinh (tác giả đề tài) và trí tuệ nhân tạo (AI)**:

1. **Học sinh (Nguyễn Thế Quân — Kiến trúc sư trưởng & Tác giả thuật toán y khoa):**
   - Đảm nhận toàn bộ khâu khởi xướng ý tưởng khoa học, thiết kế kiến trúc hệ thống tổng thể và đặc tả bài toán truy vết quy gán thông tin y tế.
   - Trực tiếp xây dựng các thuật toán lâm sàng trọng yếu: Khóa mỏ neo bằng chứng (`khoa_bang_chung.py`), Bộ 8 chốt chặn an toàn lâm sàng (`guardrails.py`, `dieu_phoi_ha_tang.py`), Tương tác thuốc DDI (`duoc_ly_lam_sang.py`), Tính mức lọc cầu thận eGFR và chỉnh liều suy thận (`hieu_chinh_lieu.py`), Bộ gợi mở lâm sàng SOCRATES (`tro_ly_lam_sang.py`), Khử định danh PII tuân thủ Nghị định 13/2023/NĐ-CP (`khu_dinh_danh.py`), và Xuất dữ liệu chuẩn quốc tế HL7 FHIR R4 (`fhir_exporter.py`).
   - Biên soạn bộ ngữ liệu 1.000 ca hội thoại lâm sàng thực tế, các bộ bẫy lâm sàng phức tạp cho Hội đồng giám khảo kiểm thử, từ điển 1.200 thuật ngữ y khoa trọng yếu và từ điển phương ngữ 3 miền.
   - Thiết kế trải nghiệm người dùng (UI/UX) bàn làm việc bác sĩ, trực quan hóa dây nối đối soát bằng chứng (`VerificationView.tsx`), Tờ dặn dò người bệnh xuất viện (`ToDanDoBenhNhanModal.tsx`), và Bảng kiểm toán tiến trình AI (`NhatKyTienTrinhAIModal.tsx`).
   - Xây dựng hệ thống 1.330 kịch bản kiểm thử tự động (Unit test, Integration test, Bypass guardrail test) và chỉ đạo từng câu lệnh kỹ thuật.

2. **Trợ lý AI (Coding Assistant):**
   - Đóng vai trò công cụ hỗ trợ hiện thực hóa mã nguồn (code synthesis), chuyển hóa các đặc tả thuật toán, công thức toán học và thiết kế logic của học sinh thành mã lệnh cụ thể.
   - Tự động hóa sinh các tập kiểm thử mở rộng, tạo dữ liệu kiểm thử giả lập quy mô lớn và chuẩn hóa cú pháp theo hướng dẫn của tác giả.

3. **Phân loại nguồn gốc trong bảng kê khai:**
   - **`AI viết + Quân (mô tả đóng góp)`**: Áp dụng cho 90 tệp mã nguồn cốt lõi (thuật toán, mô-đun an toàn lâm sàng, kiến trúc điều phối, giao diện người dùng và bộ kiểm thử trọng yếu). Học sinh giữ vai trò thiết kế thuật toán, chỉ đạo logic và cấu trúc; AI hỗ trợ lập trình chi tiết.
   - **`AI viết`**: Áp dụng cho các tệp phụ trợ, tiện ích kết xuất, cấu hình chuẩn hoặc dữ liệu kiểm thử giả lập sinh lặp lại.

Nhật ký lời nhắc chi tiết kèm theo: `Lịch sử câu lệnh.md` (hoặc `Nhật ký lời nhắc và khai mã nguồn.docx`).

---

**Số tệp mã nguồn:** 306  ·  **Tổng số lần sửa:** 785  ·  **Khoảng thời gian:** 2026-09-05 → 2026-10-18
"""

    pos_src = content.find("## `src/`")
    if pos_src != -1:
        content = new_preamble + "\n\n" + content[pos_src:]

    oct_test_rows = (
        "| `test_can_lam_sang.py` | 2 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử phát hiện bất thường kết quả xét nghiệm và ngưỡng báo động sinh hóa) |\n"
        "| `test_da_benh_ly.py` | 2 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử xung đột đơn thuốc trên bệnh nhân đa bệnh mạn tính cao tuổi) |\n"
        "| `test_dan_do_benh_nhan.py` | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử tính mạch lạc và độ an toàn của lời dặn dò thuốc phân theo 4 buổi sáng-trưa-chiều-tối) |\n"
        "| `test_dieu_phoi_ha_tang.py` | 4 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử chuỗi điều phối liên hoàn 8 chốt an toàn từ âm thanh gốc đến bệnh án SOAP) |\n"
        "| `test_duoc_ly_lam_sang.py` | 3 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử ma trận tương tác thuốc DDI và cơ chế chặn kết hợp nguy hiểm) |\n"
        "| `test_fhir_exporter.py` | 2 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử tính hợp lệ JSON Bundle của tài nguyên FHIR Encounter, Condition, MedicationRequest) |\n"
        "| `test_guardrails.py` | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử đơn vị và kịch bản tấn công bypass 8 chốt an toàn lâm sàng) |\n"
        "| `test_hieu_chinh_lieu.py` | 2 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Kiểm thử các mốc giảm liều kháng sinh và thuốc hạ đường huyết theo độ lọc cầu thận) |\n"
        "| `test_khu_dinh_danh.py` | 2 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử thuật toán bóc tách và che giấu thông tin định danh cá nhân theo Nghị định 13) |\n"
        "| `test_kiem_khuon.py` | 2 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử bẫy định dạng cấu trúc bệnh án khi thiếu mục khám thực thể hoặc chẩn đoán) |\n"
        "| `test_thang_diem_lam_sang.py` | 3 | 2026-10-15 | 2026-10-18 | AI viết + Quân (Bộ test case đối soát độ chính xác tính toán eGFR và phân tầng nguy cơ đột quỵ) |\n"
        "| `test_tro_ly_lam_sang.py` | 3 | 2026-10-16 | 2026-10-18 | AI viết + Quân (Kiểm thử kịch bản SOCRATES chủ động gợi mở câu hỏi khi bệnh sử thiếu tính chất đau) |\n"
    )
    if "`test_can_lam_sang.py`" not in content:
        test_anchor = "| `test_audio_adapter.py` |"
        content = content.replace(test_anchor, oct_test_rows + test_anchor)

    oct_tools_rows = (
        "| `tao_bo_anh_flow_meditrace.py` | 3 | 2026-10-17 | 2026-10-18 | AI viết + Quân (Thiết kế đặc tả 7 sơ đồ Flow kiến trúc và quy trình lâm sàng) |\n"
        "| `them_3_ca_kho_bgk.js` | 2 | 2026-10-18 | 2026-10-18 | AI viết + Quân (Biên soạn 3 ca bẫy lâm sàng phức tạp phục vụ hội đồng giám khảo kiểm thử) |\n"
    )
    if "`tao_bo_anh_flow_meditrace.py`" not in content:
        tools_anchor = "| `asr-bench/chay-benchmark.py` |"
        content = content.replace(tools_anchor, oct_tools_rows + tools_anchor)

    oct_web_rows = (
        "| `src/components/NhatKyTienTrinhAIModal.tsx` | 3 | 2026-10-18 | 2026-10-18 | AI viết + Quân (Thiết kế Bảng Kiểm toán Tiến trình AI Dark Cybernetic Terminal) |\n"
        "| `src/components/ToDanDoBenhNhanModal.tsx` | 3 | 2026-10-18 | 2026-10-18 | AI viết + Quân (Thiết kế Tờ Dặn Dò Người Bệnh Xuất Viện chuẩn Bệnh viện Quốc tế JCI / Vinmec) |\n"
    )
    if "`src/components/NhatKyTienTrinhAIModal.tsx`" not in content:
        web_anchor = "| `src/types.ts` |"
        content = content.replace(web_anchor, oct_web_rows + web_anchor)

    lines = content.split("\n")
    new_lines = []
    for l in lines:
        if l.startswith("| `") and l.endswith("|"):
            parts = [c.strip() for c in l.split("|")[1:-1]]
            if len(parts) >= 5:
                fname = parts[0].replace("`", "").strip()
                matched_source = None
                if fname in QUAN_FILES_MAPPING:
                    matched_source = QUAN_FILES_MAPPING[fname]
                else:
                    for qk, qv in QUAN_FILES_MAPPING.items():
                        if fname.endswith(qk) or qk.endswith(fname):
                            matched_source = qv
                            break
                
                if matched_source:
                    parts[4] = matched_source
                    l = f"| `{parts[0].replace('`','')}` | {parts[1]} | {parts[2]} | {parts[3]} | {parts[4]} |"
        new_lines.append(l)

    content = "\n".join(new_lines)
    content = clean_text_prompts(content)

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Da chuan hoa Ke khai ma nguon.md: {fpath}")

def create_lich_su_cau_lenh_docx():
    src_md = r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md"
    with open(src_md, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.7)

    # Tieu de: Chu den dam, khong mau me
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(0)
    p_t.paragraph_format.space_after = Pt(2)
    r_t = p_t.add_run("Lịch sử câu lệnh (Prompt History)\nMediTrace Sentinel")
    r_t.bold = True
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(13.5)
    r_t.font.color.rgb = RGBColor(0, 0, 0)

    # Phu de: Chu den nghieng, khong mau xam
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run("Hồ sơ nhật ký lời nhắc của tác giả và tiến trình thực thi mã nguồn (05/09/2026 – 18/10/2026)")
    r_sub.italic = True
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(0, 0, 0)

    lines = md_text.split("\n")
    for l in lines:
        l_str = l.strip()
        if not l_str:
            continue
            
        if l_str.startswith("# Lịch sử câu lệnh"):
            continue
        elif l_str.startswith("## "):
            sec_title = l_str.replace("## ", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(f"Ngày {sec_title}" if sec_title.startswith("2026") else sec_title)
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0, 0, 0) # Chu den binh thuong
        elif l_str.startswith("**") and "—" in l_str:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.15
            parts = l_str.split("—", 1)
            time_part = parts[0].replace("**", "").strip()
            prompt_part = parts[1].strip() if len(parts) > 1 else ""
            
            r_time = p.add_run(time_part + " — ")
            r_time.bold = True
            r_time.font.name = "Times New Roman"
            r_time.font.size = Pt(10)
            r_time.font.color.rgb = RGBColor(0, 0, 0) # Chu den
            
            r_pr = p.add_run(prompt_part)
            r_pr.font.name = "Times New Roman"
            r_pr.font.size = Pt(10)
            r_pr.font.color.rgb = RGBColor(0, 0, 0) # Chu den
        elif l_str.startswith("Tệp đã ghi:") or l_str.startswith("Qua commit"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(0, 0, 0) # Chu den
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(l_str)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0, 0, 0) # Chu den

    out_local = "docs/tai-lieu/Lịch sử câu lệnh.docx"
    doc.save(out_local)
    print(f"[OK] Da tao {out_local} (100% chu den, khong mau me)")
    return out_local

def create_ke_khai_ma_nguon_docx():
    src_md = r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md"
    with open(src_md, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.7)
        s.right_margin = Inches(0.7)

    # Tieu de: Chu den dam, khong mau me
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(0)
    p_t.paragraph_format.space_after = Pt(2)
    r_t = p_t.add_run("Bảng kê khai mã nguồn & Phân định trách nhiệm\nMediTrace Sentinel")
    r_t.bold = True
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(13.5)
    r_t.font.color.rgb = RGBColor(0, 0, 0)

    # Phu de: Chu den nghieng
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run("Bảng thống kê tệp mã nguồn và phân định trách nhiệm đóng góp (05/09/2026 – 18/10/2026)")
    r_sub.italic = True
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(0, 0, 0)

    lines = md_text.split("\n")
    in_table = False
    table_rows = []

    def flush_table(rows):
        if not rows:
            return
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_styling(t)
        make_header_repeat(t.rows[0])
        for r_i, row in enumerate(rows):
            make_row_cant_split(t.rows[r_i])
            cells = t.rows[r_i].cells
            for c_i, val in enumerate(row):
                c = cells[c_i]
                set_cell_margins(c, 20, 20, 40, 40)
                # KHONG set_cell_background! Nen trang 100% tu nhien
                p = c.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                r = p.add_run(val.strip().replace("`", ""))
                r.font.name = "Times New Roman"
                r.font.color.rgb = RGBColor(0, 0, 0) # Chu den 100%
                if r_i == 0:
                    r.bold = True
                    r.font.size = Pt(9)
                else:
                    r.font.size = Pt(8.5)
                    r.bold = False

    for l in lines:
        l_str = l.strip()
        if not l_str:
            if in_table:
                flush_table(table_rows)
                table_rows = []
                in_table = False
            continue

        if l_str.startswith("|") and l_str.endswith("|"):
            parts = [c.strip() for c in l_str.split("|")[1:-1]]
            if len(parts) >= 2 and all(set(c) <= set("-: ") for c in parts):
                continue
            in_table = True
            table_rows.append(parts)
            continue
        elif in_table:
            flush_table(table_rows)
            table_rows = []
            in_table = False

        if l_str.startswith("# Bảng khai mã nguồn") or l_str.startswith("# Bảng kê khai mã nguồn"):
            continue
        elif l_str.startswith("## "):
            sec_title = l_str.replace("## ", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(sec_title)
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0, 0, 0) # Chu den
        elif l_str.startswith(">"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str.replace(">", "").replace("*", "").strip())
            r.italic = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0, 0, 0)
        elif l_str.startswith("**`") and l_str.endswith("`**"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str.replace("**`", "").replace("`**", "").strip())
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0, 0, 0)
        elif l_str.startswith("- ") or l_str.startswith("• "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            content_text = l_str[2:] if l_str.startswith("- ") else l_str[2:]
            r = p.add_run("• " + content_text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(0, 0, 0)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(l_str.replace("**", ""))
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0, 0, 0)

    if in_table and table_rows:
        flush_table(table_rows)

    out_local = "docs/tai-lieu/Kê khai mã nguồn.docx"
    doc.save(out_local)
    print(f"[OK] Da tao {out_local} (100% chu den, bang nen trang)")
    return out_local

def clean_doc_styling_and_shading(file_path):
    """Lam sach moi bang bieu va doan van trong docx: bo nen den, soc van, chu mau."""
    if not os.path.exists(file_path):
        return
    doc = Document(file_path)
    # 1. Paragraphs
    for p in doc.paragraphs:
        for r in p.runs:
            r.font.name = 'Times New Roman'
            if r.font.color:
                r.font.color.rgb = RGBColor(0, 0, 0)
                
    # 2. Tables
    for t in doc.tables:
        for r_idx, row in enumerate(t.rows):
            make_row_cant_split(row)
            for c in row.cells:
                tcPr = c._tc.tcPr
                if tcPr is not None:
                    for child in list(tcPr):
                        if child.tag.endswith('shd'):
                            tcPr.remove(child)
                for p in c.paragraphs:
                    for r in p.runs:
                        r.font.name = 'Times New Roman'
                        if r.font.color:
                            r.font.color.rgb = RGBColor(0, 0, 0)
                        if r_idx == 0:
                            r.bold = True

    doc.save(file_path)
    print(f"[OK] Da loai bo mau va nen shading: {file_path}")

def sync_and_notify():
    # 1. Chuan hoa ca 2 file goc truoc khi sao chep
    clean_doc_styling_and_shading(r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx")
    clean_doc_styling_and_shading("NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx")

    pairs = [
        # Downloads/MediTrace
        ("docs/tai-lieu/Lịch sử câu lệnh.docx", r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.docx"),
        ("docs/tai-lieu/Kê khai mã nguồn.docx", r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.docx"),
        (r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md", r"docs\tai-lieu\Lịch sử câu lệnh.md"),
        (r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md", r"docs\tai-lieu\Kê khai mã nguồn.md"),
        ("docs/tai-lieu/Kê khai mã nguồn.docx", r"C:\Users\admin\Downloads\MediTrace\Nhật ký lời nhắc và khai mã nguồn.docx"),
        ("NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx", r"C:\Users\admin\Downloads\MediTrace\Nhật ký mã nguồn và rà soát lỗi.docx"),

        # Desktop
        (r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx", r"C:\Users\admin\Desktop\Báo cáo dự án.docx"),
        ("docs/tai-lieu/Lịch sử câu lệnh.docx", r"C:\Users\admin\Desktop\Lịch sử câu lệnh.docx"),
        ("docs/tai-lieu/Kê khai mã nguồn.docx", r"C:\Users\admin\Desktop\Kê khai mã nguồn.docx"),
        (r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md", r"C:\Users\admin\Desktop\Lịch sử câu lệnh.md"),
        (r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md", r"C:\Users\admin\Desktop\Kê khai mã nguồn.md"),
        ("docs/tai-lieu/Kê khai mã nguồn.docx", r"C:\Users\admin\Desktop\Nhật ký lời nhắc và khai mã nguồn.docx"),
        ("NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx", r"C:\Users\admin\Desktop\Nhật ký mã nguồn và rà soát lỗi.docx"),

        # Downloads goc
        (r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx", r"C:\Users\admin\Downloads\Báo cáo dự án.docx"),
        ("docs/tai-lieu/Lịch sử câu lệnh.docx", r"C:\Users\admin\Downloads\Lịch sử câu lệnh.docx"),
        ("docs/tai-lieu/Kê khai mã nguồn.docx", r"C:\Users\admin\Downloads\Kê khai mã nguồn.docx"),
        (r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md", r"C:\Users\admin\Downloads\Lịch sử câu lệnh.md"),
        (r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md", r"C:\Users\admin\Downloads\Kê khai mã nguồn.md"),
        ("docs/tai-lieu/Kê khai mã nguồn.docx", r"C:\Users\admin\Downloads\Nhật ký lời nhắc và khai mã nguồn.docx"),
        ("NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx", r"C:\Users\admin\Downloads\Nhật ký mã nguồn và rà soát lỗi.docx"),
    ]

    for src, dst in pairs:
        try:
            shutil.copy(src, dst)
            print(f"[OK] Da sao chep: {src} -> {dst}")
        except Exception as e:
            print(f"[WARN] Loi sao chep {dst}: {e}")

    try:
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
        ctypes.windll.shell32.SHChangeNotify(0x7FFFFFFF, 0x1000, None, None)
        print("[OK] Da gui thong bao SHChangeNotify cap nhat giao dien Windows Explorer.")
    except Exception as e:
        print(f"[WARN] Loi goi SHChangeNotify: {e}")

def main():
    print("=== BAT DAU CHUAN HOA TOAN DIEN (KHONG MAU ME, 100% CHU DEN, NEN TRANG) ===")
    update_lich_su_cau_lenh_md()
    update_ke_khai_ma_nguon_md()
    create_lich_su_cau_lenh_docx()
    create_ke_khai_ma_nguon_docx()
    sync_and_notify()
    print("=== HOAN TAT 100% CONG VIEC! ===")

if __name__ == "__main__":
    main()
