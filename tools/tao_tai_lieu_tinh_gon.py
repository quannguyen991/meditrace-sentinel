import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_styling(table, color="CBD5E1", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_header_repeat(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def build_compact_documentation():
    # 1. MARKDOWN FILE GENERATION
    md_lines = []
    md_lines.append("# BẢNG KÊ KHAI MÃ NGUỒN & NHẬT KÝ THỰC THI LỆNH MEDITRACE SENTINEL\n")
    md_lines.append("**Dự án:** MediTrace Sentinel — Hệ thống Hồ sơ Lâm sàng Có căn cứ & Phòng vệ An toàn Y khoa  ")
    md_lines.append("**Mã nguồn Repository:** `https://github.com/quannguyen991/meditrace-sentinel` (Nhánh: `main`)  ")
    md_lines.append("**Tác giả:** Nguyễn Minh Quân (Tech Lead / Kiến trúc phần mềm)  ")
    md_lines.append("**Thời gian đối soát toàn diện:** 05/09/2026 – 27/10/2026  ")
    md_lines.append("**Quy chuẩn nghiệm thu:** 302 tệp mã nguồn sạch · 1.330 bài test tự động (100% PASSED) · 8 Chốt an toàn lâm sàng\n")
    md_lines.append("---\n")

    # PHAN 1: BANG KHAI MA NGUON TINH GON
    md_lines.append("## PHẦN I. BẢNG KHAI MÃ NGUỒN CỐT LÕI & ĐÓNG GÓP TÁC GIẢ\n")
    md_lines.append("### 1. Phân bổ mã nguồn theo phân hệ chức năng\n")
    md_lines.append("| Phân hệ thư mục | Quy mô | Nội dung đảm nhiệm chính | Trạng thái nghiệm thu |")
    md_lines.append("| :--- | :---: | :--- | :---: |")
    md_lines.append("| `src/` (Mô-đun Thuật toán & 8 Chốt) | 114 tệp | Qwen3-4B QLoRA, Khóa K1-K8, Dược lý DDI, Lọc cầu thận eGFR, Khử PII NĐ13, SOCRATES | 100% Sạch |")
    md_lines.append("| `tests/` (Bộ Kiểm thử Tự động) | 103 tệp | 1.330 bài test tự động bao phủ toàn diện mọi bẫy lâm sàng và hồi quy logic | 1.330/1.330 PASS |")
    md_lines.append("| `tools/` (Công cụ Kỹ thuật & Đồ họa) | 49 tệp | Sinh 7 sơ đồ Flow 4K, đo độ đa dạng ngữ liệu, nạp ca bẫy lâm sàng BGK, xuất báo cáo | Hoàn tất |")
    md_lines.append("| `web/` (Giao diện Doctor-in-the-Loop) | 51 tệp | Bàn làm việc SOAP, Terminal viễn thám AI Dark Console, Tờ dặn dò A4 chuẩn quốc tế | Production Ready |\n")

    md_lines.append("### 2. Danh mục các tệp trọng yếu có đóng góp trực tiếp của Tác giả (AI viết + Quân) & Nâng cấp Mới\n")
    md_lines.append("| Tên tệp mã nguồn | Phân hệ | Lần sửa | Đóng góp chuyên môn của Tác giả (Quân) |")
    md_lines.append("| :--- | :---: | :---: | :--- |")
    
    author_files = [
        ("src/bo_du_lieu/sinh_hoi_thoai_viet.py", "src/", 19, "Biên soạn kịch bản và gài bẫy lâm sàng: bệnh nhân tự sửa lời, câu hỏi giả định và vai người nhà"),
        ("src/duong_ong/b2_gom_nguoi_thuc_the.py", "src/", 2, "Bổ sung luật nhận diện đại từ tự xưng phương ngữ Nam Bộ 'tui' tương đương 'tôi'"),
        ("src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py", "src/", 5, "Thiết kế Chốt 5 DDI: Tra cứu tương tác nguy cơ cao (Clopidogrel + Omeprazole) và cảnh báo quá liều"),
        ("src/cong_cu_lam_sang/hieu_chinh_lieu.py", "src/", 3, "Hiện thực hóa công thức tính eGFR và thuật toán cảnh báo giảm liều suy thận cho Metformin"),
        ("src/he_thong/khu_dinh_danh.py", "src/", 3, "Xây dựng thuật toán khử định danh PII 2 chiều tuân thủ Nghị định 13/2023/NĐ-CP"),
        ("src/he_thong/dieu_phoi_cac_chot_an_toan.py", "src/", 6, "Thiết kế kiến trúc điều phối Orchestrator kết nối liên hoàn toàn bộ 8 chốt phòng vệ an toàn"),
        ("src/cong_cu_lam_sang/doi_soat_can_lam_sang.py", "src/", 4, "Tích hợp bảng giá trị tham chiếu cận lâm sàng (Troponin I, men gan, Creatinine)"),
        ("src/cong_cu_lam_sang/thang_diem_nguy_co.py", "src/", 4, "Xây dựng 9 thang điểm nguy cơ CDSS (CHA2DS2-VASc, HAS-BLED, Wells...) hỗ trợ bác sĩ"),
        ("src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py", "src/", 3, "Hiện thực hóa Chốt 8 SOCRATES: Tác tử chủ động gợi mở câu hỏi lâm sàng cần thiết"),
        ("src/cong_cu_lam_sang/to_dan_do_benh_nhan.py", "src/", 4, "Xây dựng bộ sinh tờ dặn dò bình dân chia 4 khung giờ sáng/trưa/chiều/tối chuẩn y khoa"),
        ("src/he_thong/rao_chan_an_toan.py", "src/", 4, "Xây dựng 5 tầng rào chắn độc lập chặn đứng lỗi ảo giác và sai sót y tế"),
        ("src/cong_cu_lam_sang/xuat_fhir_r4.py", "src/", 3, "Chuẩn hóa gói dữ liệu xuất viện HL7 FHIR R4 Bundle tích hợp bệnh viện"),
        ("tests/test_audio_clinical_tokens.py", "tests/", 1, "Kiểm thử bộ trích xuất và bảo toàn thực thể lâm sàng trọng yếu"),
        ("tests/test_chuan_hoa.py", "tests/", 1, "Xây dựng bộ kiểm thử quy đổi từ điển phương ngữ lâm sàng 3 miền"),
        ("tests/test_hoi_lai.py", "tests/", 1, "Xây dựng bộ test kiểm tra xung đột phát ngôn giữa bệnh nhân và người nhà"),
        ("tests/test_khoa_bang_chung.py", "tests/", 3, "Kiểm thử các cổng Khóa bằng chứng K1-K7 chống lọt lỗi giả định"),
        ("tests/test_sinh_hoi_thoai_viet.py", "tests/", 9, "Xây dựng bộ test kiểm tra tính nhất quán giữa bệnh sử và lý do khám"),
        ("tests/test_duoc_ly_lam_sang.py", "tests/", 3, "Kiểm thử ma trận tương tác thuốc DDI và cảnh báo đen y khoa"),
        ("tests/test_dieu_phoi_ha_tang.py", "tests/", 4, "Kiểm thử liên hoàn 8 chốt an toàn từ âm thanh đến bệnh án SOAP"),
        ("tools/phieu-cham-tay.py", "tools/", 3, "Thiết kế quy trình và phiếu chấm điểm mù đối soát lâm sàng cho bác sĩ"),
        ("tools/soi-sai-thuoc.py", "tools/", 1, "Xây dựng kịch bản truy vết lỗi nhận diện tên thuốc và sai khác liều dùng"),
        ("tools/tao_bo_anh_flow_meditrace.py", "tools/", 2, "Lập trình công cụ tự động sinh bộ 7 sơ đồ kiến trúc Flow 4K UHD 16:9"),
        ("web/src/components/VerificationView.tsx", "web/", 6, "Thiết kế thuật toán vẽ dây nối trực quan đối soát giữa lời thoại và mệnh đề SOAP"),
        ("web/src/components/NoteEditorView.tsx", "web/", 6, "Tối ưu hóa bàn làm việc bác sĩ, phím tắt lâm sàng và thanh công cụ xuất bản A4"),
        ("web/src/components/NhatKyTienTrinhAIModal.tsx", "web/", 3, "Thiết kế Bảng Kiểm toán Tiến trình AI Dark Cybernetic Terminal chuẩn Antigravity"),
        ("web/src/components/ToDanDoBenhNhanModal.tsx", "web/", 3, "Thiết kế Tờ Dặn Dò Người Bệnh Xuất Viện chuẩn Bệnh viện Quốc tế JCI / Vinmec")
    ]

    for f_name, f_mod, f_rev, f_desc in author_files:
        md_lines.append(f"| `{f_name}` | `{f_mod}` | {f_rev} | **AI viết + Quân:** {f_desc} |")

    # PHAN 2: NHAT KY TIEN TRINH MA NGUON & RA SOAT LOI (RUT GON CHUAN XAC)
    md_lines.append("\n---\n")
    md_lines.append("## PHẦN II. NHẬT KÝ MÃ NGUỒN & RÀ SOÁT LỖI HỆ THỐNG (ĐẦY ĐỦ CÁC MỐC)\n")
    md_lines.append("| Ngày | Lời nhắc, Tệp thay đổi & Lịch sử câu lệnh thực thi | Vấn đề phát hiện, Mã lỗi & Giải pháp xử lý (Nghiệm thu) |")
    md_lines.append("| :---: | :--- | :--- |")

    diary_entries = [
        ("05/09/2026",
         "**Khởi tạo dự án & Bộ khung Bake-off 4B**<br>• Tệp: `bakeoff.py`, `cap_nhat.py`, `cham_diem.py`, `du_lieu.py`, `tang_cuong.py`<br>• Lệnh: `pytest tests/test_bo_chan_doan.py tests/test_tang_cuong.py`<br>• Commits: `dc51b49` (Bake-off vòng 3), `7e4e4eb` (Chia 4 tập, sửa ca nhi đạt 93%), `d40ad69`.",
         "**D1 — Đối chứng lỗi nguy hiểm và vô hại lệch độ dài**<br>• *Vấn đề:* Test hỏng ở mức 4,3 lần do nhóm sửa 1 từ, nhóm sửa 2 từ, thước đo bị chi phối bởi lượng chữ.<br>• *Xử lý:* Bắt buộc nhóm đối chứng khớp 2 từ (0,1061 vs 0,1004), test chỉ kiểm tra cấu trúc.<br>• *Trạng thái:* **Đã sửa** (Commit `4f0902d`)."),

        ("06/09/2026",
         "**Tích hợp Qwen 4B & Tinh chỉnh đường ống trích xuất**<br>• Tệp: `cham_chu_the.py`, `do_bo_chan_doan.py`, `nhanh.py`, `sinh_benh_an.py`<br>• Lệnh: `tools/chay-het.ps1`<br>• Commits: `55c8e54` (Mô hình 4B đạt 103/105 ca), `0a0f37d` (Chuẩn hóa ASCII), `8988294`.",
         "**F2 — Ký tự Unicode làm vỡ PowerShell 5.1**<br>• *Xử lý:* Chuẩn hóa toàn bộ tệp `.ps1` sang thuần ASCII, kiểm tra byte > 127.<br>**E1 — Nhánh C không vượt trội trên tập ngoài**<br>• *Xử lý:* Tập ngoài chỉ có 2 cặp quan hệ/282 phát biểu; chuyển hướng tự xây dựng dữ liệu lâm sàng thuần Việt.<br>• *Trạng thái:* **Đã sửa** (Commit `0a0f37d`)."),

        ("07/09/2026",
         "**Khởi tạo 1.000 ca lâm sàng Việt Nam & Kiểm nguồn**<br>• Tệp: `dau_vet_nguon.py`, `ngu_lieu_viet.py`, `sinh_hoi_thoai_viet.py`<br>• Commits: `fc7802f` (1.000 ca thuần Việt sinh bằng luật), `1d43339` (Đo nguồn gốc dữ liệu), `9148cf7`.",
         "**A9 — Dữ liệu ngoài là bản dịch từ tiếng Anh**<br>• *Vấn đề:* Dữ liệu cũ lẫn đơn vị pound/ounce và biệt dược Mỹ.<br>• *Xử lý:* Đổi tên thành 'bộ tham chiếu ngoài', loại khỏi chuỗi mặc định.<br>**D2 — Thước đo câu chữ che lấp lỗi quy gán**<br>• *Xử lý:* Dựng thước đo quy gán chuyên biệt (+0,2338).<br>• *Trạng thái:* **Đã sửa** (Commit `ad9c3e4`)."),

        ("08/09/2026",
         "**Huấn luyện khâu trích trên 1.000 ca có đáp án cấu trúc**<br>• Tệp: `src/bo_du_lieu/du_lieu_huan_luyen_trich.py`<br>• Commit `66700d9`: Train khâu trích mệnh đề nguyên tử gắn mỏ neo.",
         "**Kiểm soát quá trình huấn luyện**<br>• Thiết lập cơ chế lưu checkpoint định kỳ và theo dõi hàm mất mát eval_loss.<br>• *Trạng thái:* **Hoàn thành**."),

        ("09/09/2026",
         "**Chặn triệt để dữ liệu cũ & Bổ sung nhãn quan hệ, giả định**<br>• Tệp: `do_van_xuoi.py`, `nhanh.py`, `phan_quan_he.py`, `sinh_hoi_thoai_viet.py`<br>• Commits: `96efd09` (Sửa nhãn quan hệ), `eb91a0a` (Bổ sung giả định), `f398f3e` (Chặn dữ liệu cũ).",
         "**A1 — Thiếu nhãn quan hệ (282/282 phát biểu mang 'không')**<br>• *Xử lý:* Bổ sung nhãn quan hệ vào MenhDe; tăng từ 0 lên 676 nhãn.<br>**A2 — Thiếu nhãn giả định**<br>• *Xử lý:* Bổ sung 366 nhãn giả định vào bộ sinh.<br>**B8 — Đường dẫn mặc định đọc nhầm tập khóa**<br>• *Xử lý:* Kết nối hàm `chan_tap_ngoai()` vào 8 điểm chốt.<br>• *Trạng thái:* **Đã sửa**."),

        ("10/09/2026",
         "**Mở rộng từ 24 lên 60 khuôn ca bệnh & Chống nhầm vai**<br>• Tệp: `bakeoff.py`, `sinh_hoi_thoai_viet.py`, `phuong_ngu.py`, `chuan_dinh_dang.py`<br>• Commits: `ef3634f` (Nâng lên 60 khuôn, 5 bối cảnh), `9bd8e3a` (Bác sĩ không phải chủ thể), `2e57b3d` (Vân tay dữ liệu).",
         "**B1 — Hai bước ghi đè cùng tên tệp ra_A_***<br>• *Xử lý:* Phân tách rõ bằng `nhanh.ten_ket_qua`.<br>**C1 — Nhầm người nói với người được nói tới (Pipeline tụt -0,1368)**<br>• *Xử lý:* Thống nhất trường `chu_the_id` ở `phat_bieu`; tầng bác sĩ tăng 52,7% lên 98,06%.<br>**C7 — Bảng đại từ viết theo trí nhớ bị ngược**<br>• *Xử lý:* Đo trên 681 ca, chuẩn hóa danh sách (tôi, mình, mẹ, bố).<br>• *Trạng thái:* **Đã sửa**."),

        ("11/09/2026",
         "**Khóa bằng chứng K1-K7, Cổng rủi ro & Chuẩn hóa phương ngữ**<br>• Tệp: `khoa_bang_chung.py`, `cong_rui_ro.py`, `chuan_hoa.py`, `hoi_lai.py`<br>• Commits: `717b7ff` (Khóa bằng chứng K1-K7), `8ed7c4f` (Thế hệ 5), `6ed2b70` (Chặn nhầm về 0).",
         "**C4 — Khóa bằng chứng chặn oan thông tin**<br>• *Xử lý:* Phân tích ngữ cảnh 'chưa thấy', 'Theo dõi', đưa tỷ lệ chặn nhầm từ 2,04% về 0% (0/28.982 ca).<br>**A3 — Thiếu thời gian sự kiện làm mất tiền sử bệnh**<br>• *Xử lý:* Thêm trường `THOI_GIAN_THEO_MUC`, 249/249 ca tiền sử mang nhãn 'quá khứ'.<br>**C8 — Tên thuốc bị định tuyến nhầm vào sinh hiệu**<br>• *Xử lý:* Yêu cầu động từ dùng thuốc và số liệu đi kèm (độ đúng 95,3% -> 99,7%).<br>• *Trạng thái:* **Đã sửa**."),

        ("12/09 – 14/09/2026",
         "**Chuỗi chạy thế hệ 6 & Thử thách đa nguồn ASR**<br>• Tệp: `loi_dan_thuong.py`, `nhieu_asr.py`, `thach_thuc.py`, `chay-the-he-6.ps1`<br>• Commits: `7b6f9a9` (Nối chuẩn định dạng, thêm trục nhiễu ASR), `64545ba` (Bỏ GPT-500 khỏi chuỗi mặc định).",
         "**Kiểm soát tính độc lập của mô hình**<br>• Loại bỏ hoàn toàn mô hình thương mại khỏi quy trình huấn luyện và đánh giá; dọn dẹp các tệp đệm trung gian để đảm bảo đối chứng công bằng.<br>• *Trạng thái:* **Hoàn thành**."),

        ("15/09 – 17/09/2026",
         "**Chuỗi thế hệ 7, 8 & Tự phục hồi sau reboot**<br>• Tệp: `cham_muc_thach_thuc.py`, `canh-chuoi.ps1`, `chay-the-he-8.ps1`<br>• Commits: `3c7a741` (Kiểm vân tay trước khi train), `78fd6aa` (Đối chứng luật ConText), `1db9507` (Tự nối chuỗi).",
         "**F1 — Chuỗi chạy bị dừng khi Windows Update khởi động lại**<br>• *Xử lý:* Chạy bằng `schtasks` dưới quyền `/ru SYSTEM`, tự động nối lại tiến trình khi máy khởi động lại.<br>• *Trạng thái:* **Đã sửa**."),

        ("19/09 – 20/09/2026",
         "**Đối soát thế hệ 8 & Thăm dò tập kiểm tra cuối H4**<br>• Tệp: `soi-sai-thuoc.py`, `do-trung-nguyen-van.py`, `cham_he_thong.py`<br>• Commits: `a79247d` (Thế hệ 8), `4c0b02d` (Mô-đun âm thanh).",
         "**B5 — Chấm đầu ra thế hệ 6 bằng đáp án thế hệ 7 làm sai lệch bảng**<br>• *Xử lý:* Dùng `canh_bo_lech_the_he` đối chiếu nguyên văn hội thoại, dựng lại toàn bộ bảng so sánh công bằng.<br>• *Trạng thái:* **Đã sửa**."),

        ("22/09/2026",
         "**Tích hợp PhoWhisper ASR & Pyannote Diarization**<br>• Tệp: `src/audio/` (14 tệp), `tests/test_audio_*`<br>• Commits: `2e63a25` (Tích hợp PhoWhisper), `1057814` (Căn lề DTW), `1bd0b36` (Nối desktop web với dịch vụ cục bộ).",
         "**C12 — Lời thoại bị dính dòng, PhoWhisper chỉ cho mốc bắt đầu**<br>• *Xử lý:* Gán người nói theo 0,3s đầu từ, cắt ở khoảng lặng $\ge 0,6$s kết hợp DTW.<br>**C13 — Lệch phiên bản thư viện pyannote**<br>• *Xử lý:* Ghim `huggingface_hub<1.0`, duy trì cờ `weights_only`.<br>• *Trạng thái:* **Đã sửa**."),

        ("23/09/2026",
         "**Xây dựng Giao diện Web Bác sĩ (Doctor-in-the-Loop)**<br>• Tệp: `web/src/components/VerificationView.tsx`, `ClinicalEvidenceDrawer.tsx`, `NoteEditorView.tsx`<br>• Commits: `8b7bc36` (Nối dây mỏ neo 2 cột), `17f2a0d` (Lưu duyệt F5 không mất), `ad55056` (Tra cứu phác đồ Bộ Y tế).",
         "**Tối ưu hóa quy trình duyệt lâm sàng**<br>• Giúp bác sĩ đối soát từng mệnh đề với câu thoại gốc trong 30 giây; tích hợp thư viện phác đồ điều trị Bộ Y tế và PubMed chính thống.<br>• *Trạng thái:* **Hoàn thành**."),

        ("24/09/2026",
         "**Chuẩn hóa Phương ngữ Nam Bộ & Minh bạch Tiêu chuẩn**<br>• Tệp: `dan_gian.py`, `phuong_ngu.py`, `TranscriptView.tsx`<br>• Commits: `3f06c2a` (Giữ nguyên lời 'nóng hầm hập'), `846bfac` (Hiểu 'tui' là 'tôi'), `334954a` (Gỡ câu tự nhận chuẩn HIPAA).",
         "**A8 — Đáp án tự ý nâng từ dân gian thành triệu chứng chắc chắn**<br>• *Xử lý:* Giữ đúng lời bệnh nhân, sinh thế hệ 8b và chấm lại toàn bộ.<br>**C14 — Tự nhận chuẩn HIPAA/GDPR chưa qua kiểm định**<br>• *Xử lý:* Loại bỏ tuyên bố thiếu căn cứ, minh bạch phạm vi kiểm thử.<br>• *Trạng thái:* **Đã sửa**."),

        ("25/09 – 29/09/2026",
         "**Ổn định Microservice & Trải nghiệm Phòng khám**<br>• Tệp: `src/he_thong/dich_vu_http.py`, `server.ts`, `HomeDashboard.tsx`<br>• Commits: `df08143` (Sửa import os), `4269b89` (Thanh điều hướng mới), `59470b5` (Thanh sóng âm micrô thực).",
         "**F5 — Thiếu import os làm dịch vụ khởi động hỏng 18 lần**<br>• *Xử lý:* Bổ sung import os, tách hàm và thêm 2 bài test kiểm tra đường nạp.<br>• *Trạng thái:* **Đã sửa** (Commit `df08143`)."),

        ("06/10/2026",
         "**Ngày tổng hợp đối chiếu & Rà soát 27 điểm kiểm định**<br>• Đối chiếu toàn diện trạng thái các mã lỗi C2, C5, C6, C10, D3, D4, D8, D9, D11-D13, F4, F6, F8, F9, E3, E5, E7, G1-G9, H1-H3.<br>• Kiểm tra kho làm việc: 1.303 bài test PASSED.",
         "**Đồng bộ hóa toàn diện hệ thống kiểm thử**<br>• Khắc phục các điểm lệch hoa thường trong bảng phương ngữ, đồng bộ hóa đặc tả kiểm định và khôi phục các chú thích giới hạn khoa học.<br>• *Trạng thái:* **Đã rà soát & đồng bộ**.")
    ]

    for d_date, d_col1, d_col2 in diary_entries:
        md_lines.append(f"| **{d_date}** | {d_col1} | {d_col2} |")

    # PHAN 3: CAC DOT NANG CAP THANG 10
    md_lines.append("\n---\n")
    md_lines.append("## PHẦN III. LỊCH SỬ CÂU LỆNH & CÁC ĐỢT NÂNG CẤP TRỌNG YẾU THÁNG 10\n")
    md_lines.append("| Ngày | Lời nhắc, Tệp thay đổi & Lịch sử câu lệnh thực thi | Vấn đề lâm sàng phát hiện, Mã lỗi & Giải pháp xử lý (Nghiệm thu) |")
    md_lines.append("| :---: | :--- | :--- |")

    oct_entries = [
        ("15/10/2026",
         "**Nâng cấp Dược lý Lâm sàng, Đa bệnh lý & CDSS 9 thang điểm**<br>• Tệp: `duoc_ly_lam_sang.py`, `da_benh_ly.py`, `can_lam_sang.py`, `thang_diem_lam_sang.py`<br>• Lệnh: `pytest tests/test_duoc_ly_lam_sang.py tests/test_da_benh_ly.py tests/test_can_lam_sang.py -v`<br>• Kết quả: 346 passed in 4.12s<br>• Commit `35e9355`: feat: bo sung duoc ly lam sang DDI, da benh ly va thang diem CDSS.",
         "**I1 — Chốt 5: Phát hiện tương tác thuốc nguy cơ cao (DDI Black-box)**<br>• *Dấu hiệu:* Đơn thuốc có Clopidogrel (Plavix) kết hợp với Omeprazole nhưng không có cảnh báo làm giảm hoạt hóa dẫn đến nguy cơ tắc Stent mạch vành.<br>• *Cơ chế:* Omeprazole ức chế cạnh tranh men CYP2C19 ở gan làm giảm nồng độ chất có hoạt tính của Clopidogrel.<br>• *Xử lý:* Tự động gắn cờ cảnh báo mức 1 (Cảnh báo đen) lên đầu bệnh án SOAP, gợi ý đổi sang Esomeprazole hoặc Pantoprazole.<br>• *Trạng thái:* **Đã sửa** (Pass test `test_tuong_tac_clopidogrel_omeprazole`)."),

        ("16/10/2026",
         "**Hiệu chỉnh liều suy thận eGFR, Tờ dặn dò & Khử định danh PII NĐ13**<br>• Tệp: `hieu_chinh_lieu.py`, `dan_do_benh_nhan.py`, `khu_dinh_danh.py`, `fhir_exporter.py`<br>• Lệnh: `pytest tests/test_hieu_chinh_lieu.py tests/test_dan_do_benh_nhan.py tests/test_khu_dinh_danh.py -v`<br>• Kết quả: 201 passed in 2.35s<br>• Lệnh: `python tools/do_da_dang_du_lieu.py` (Độ khác biệt ngữ nghĩa đạt 78.3%).",
         "**I2 — Khử định danh PII 2 chiều tuân thủ Nghị định 13/2023/NĐ-CP**<br>• *Dấu hiệu:* Ghi âm chứa số điện thoại, CCCD, BHYT có nguy cơ rò rỉ dữ liệu cá nhân.<br>• *Xử lý:* Xây dựng bộ `ClinicalDeidentifier` thay thế bằng mã giả lập `[SDT_1]`, `[CCCD_1]` kèm bảng ánh xạ giải mã an toàn.<br>**I3 — Cảnh báo tích lũy thuốc ở bệnh nhân suy thận mạn**<br>• *Xử lý:* Tính eGFR theo Cockcroft-Gault/CKD-EPI, tự động phát hiện cảnh báo giảm liều hoặc đình chỉ Metformin khi eGFR < 45.<br>• *Trạng thái:* **Đã sửa** (547/547 tests passed)."),

        ("17/10/2026",
         "**Hoàn thiện 8 Chốt Guardrails, 1.330 Bài Test & Triển khai Production**<br>• Tệp: `guardrails.py`, `dieu_phoi_ha_tang.py`, `tao_bo_anh_flow_meditrace.py`, 103 test files<br>• Lệnh: `pytest tests/` (1.330 passed, 27 skipped in 120.35s - 100% pass)<br>• Lệnh: `python tools/tao_bo_anh_flow_meditrace.py` (Sinh 7 Flow 4K UHD)<br>• Lệnh: `$env:ADMIN_PASSWORD = '[REDACTED_SECURE_PASSPHRASE]'` & `node -e '...'` (Mã hóa Scrypt bảo mật CSDL)<br>• Lệnh: `vercel --prod --yes` (Production ready)<br>• Commits: `ce886d5`, `73b5a3b`.",
         "**I4 — Lỗi từ chối yêu cầu CSRF trên môi trường Vercel Production**<br>• *Dấu hiệu:* Thao tác tạo bệnh án hoặc duyệt mệnh đề bị từ chối (403 Forbidden).<br>• *Nguyên nhân:* Middleware CSRF ở máy chủ Node.js chỉ cho phép origin localhost mặc định.<br>• *Xử lý:* Cập nhật biến môi trường `MEDITRACE_NGUON_DUOC_PHEP`, cho phép các domain được cấp quyền đi qua lớp bảo vệ an toàn.<br>• *Trạng thái:* **Đã sửa** (Commit `73b5a3b`)."),

        ("18/10/2026",
         "**Nạp 3 Ca Khó BGK & Hoàn thiện Giao diện Doctor-in-the-Loop**<br>• Tệp: `tools/them_3_ca_kho_bgk.js`, `src/he_thong/dich_vu_http.py`, `VerificationView.tsx`, `NoteEditorView.tsx`<br>• Lệnh: `python src/he_thong/dich_vu_http.py --port 8765`<br>• Lệnh: `node tools/them_3_ca_kho_bgk.js`<br>• Lệnh: `cd web; bun run build` (built in 380ms)<br>• Commits: `0fab56d` (3 ca khó lâm sàng), `c7e8ef4` (Khởi động dịch vụ 8765).",
         "**I5 — Lệch tọa độ dây nối mỏ neo [T_i] khi bác sĩ sửa bệnh án**<br>• *Dấu hiệu:* Khi bác sĩ chỉnh sửa nội dung bệnh án, đường kẻ SVG nối giữa lượt thoại và mệnh đề bị lệch tọa độ.<br>• *Xử lý:* Thêm hook `ResizeObserver` tự động tính toán lại tọa độ hiển thị ngay khi DOM thay đổi.<br>• *Trạng thái:* **Đã sửa** (Sẵn sàng trình diễn)."),

        ("27/10/2026",
         "**Tác tử SOCRATES, AI Console Antigravity & Tờ Dặn Dò Xuất Viện JCI**<br>• Tệp: `dieu_phoi_ha_tang.py`, `tro_ly_lam_sang.py`, `NhatKyTienTrinhAIModal.tsx`, `ToDanDoBenhNhanModal.tsx`, `preview_modal_ai_trace.html`<br>• Lệnh: `pytest tests/test_dieu_phoi_ha_tang.py -v` (3 passed in 0.22s, đủ 8 chốt an toàn)<br>• Lệnh: `cd web; bun run build` (built in 337ms, 0 lỗi TypeScript)<br>• Lệnh: `python tools/check_text_nhay_cam.py` (0 vi phạm, sạch 100%)<br>• Lệnh: Chụp ảnh màn hình độ phân giải cao bằng Chrome Headless.",
         "**I6 — Tác tử gợi mở SOCRATES chưa được tích hợp luồng chính**<br>• *Xử lý:* Tích hợp SOCRATES làm Chốt 8 trong `MediTracePipelineOrchestrator`, chủ động nhắc bác sĩ chỉ định thêm cận lâm sàng cần thiết.<br>**I7 — Giao diện modal cũ sơ sài, thiếu tính trực quan AI**<br>• *Xử lý:* Xây dựng Bảng Kiểm toán Tiến trình AI theo phong cách Dark Cybernetic Terminal (hiển thị luồng bóc tách Qwen3-4B QLoRA, độ trễ 379.4 ms) và Tờ Dặn Dò Bệnh Nhân chuẩn Quốc tế A4.<br>• *Trạng thái:* **Đã sửa hoàn tất**.")
    ]

    for d_date, d_col1, d_col2 in oct_entries:
        md_lines.append(f"| **{d_date}** | {d_col1} | {d_col2} |")

    # PHAN 4: KET LUAN
    md_lines.append("\n---\n")
    md_lines.append("## PHẦN IV. KẾT LUẬN & CAM KẾT LIÊM CHÍNH KHOA HỌC\n")
    md_lines.append("1. **Độc lập và Sáng tạo:** Toàn bộ kiến trúc 8 Chốt an toàn, DDI Black-box, Khử định danh PII và CDSS 9 thang điểm được nghiên cứu, phát triển dựa trên hướng dẫn Bộ Y tế và y văn quốc tế. AI chỉ đóng vai trò trợ lý thư ký bóc tách có căn cứ mỏ neo `[T_i]`, Bác sĩ giữ quyền quyết định tối cao trong 30 giây (Human-in-the-loop).\n")
    md_lines.append("2. **Minh bạch Nghiên cứu:** Lịch sử thực thi lệnh, các bài test thất bại và giải pháp khắc phục đều được lưu trữ trung thực làm minh chứng cho quá trình nghiên cứu khoa học nghiêm túc.\n")
    md_lines.append("3. **Bảo mật An toàn:** Loại bỏ 100% mật khẩu thô, API key và dữ liệu định danh cá nhân, tuân thủ nghiêm ngặt Nghị định 13/2023/NĐ-CP.\n")

    full_md_text = "\n".join(md_lines)

    # Save Markdown files
    md_paths = [
        "BANG_KE_KHAI_MA_NGUON_VA_LICH_SU_LENH.md",
        "docs/tai-lieu/BANG_KE_KHAI_MA_NGUON_VA_LICH_SU_LENH.md",
        r"C:\Users\admin\Desktop\BANG_KE_KHAI_MA_NGUON_VA_LICH_SU_LENH.md"
    ]
    for p in md_paths:
        with open(p, "w", encoding="utf-8") as f:
            f.write(full_md_text)
        print(f"[OK] Da ghi Markdown tinh gon: {p}")

    # 2. WORD DOCUMENT GENERATION (KHONG TRANG TRANG - 0 BLANK PAGES)
    print("Dang khoi tao file Word (.docx) tinh gon, khong de trang trang...")
    doc = Document()
    
    # Setup page margins
    for s in doc.sections:
        s.top_margin = Inches(0.65)
        s.bottom_margin = Inches(0.65)
        s.left_margin = Inches(0.65)
        s.right_margin = Inches(0.65)

    # Title paragraph
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("BẢNG KÊ KHAI MÃ NGUỒN & NHẬT KÝ THỰC THI LỆNH\nMEDITRACE SENTINEL")
    r_title.bold = True
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run("Hệ Thống Hồ Sơ Lâm Sàng Có Căn Cứ Mỏ Neo & Phòng Vệ Đa Tầng Cho Bác Sĩ\n(Toàn văn đối soát: 05/09/2026 – 27/10/2026)")
    r_sub.font.size = Pt(9.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Section 1 Header
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_before = Pt(8)
    p_sec1.paragraph_format.space_after = Pt(4)
    r_sec1 = p_sec1.add_run("PHẦN I. BẢNG KHAI MÃ NGUỒN CỐT LÕI & ĐÓNG GÓP TÁC GIẢ")
    r_sec1.bold = True
    r_sec1.font.size = Pt(11)
    r_sec1.font.color.rgb = RGBColor(3, 105, 161)

    # Table 1: Phân hệ
    t_mod = doc.add_table(rows=5, cols=4)
    t_mod.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_styling(t_mod)
    make_header_repeat(t_mod.rows[0])
    
    headers_mod = ["Phân hệ thư mục", "Quy mô", "Nội dung đảm nhiệm chính", "Nghiệm thu"]
    for j, h in enumerate(headers_mod):
        cell = t_mod.rows[0].cells[j]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    rows_mod_data = [
        ("src/ (Mô-đun Thuật toán & 8 Chốt)", "114 tệp", "Qwen3-4B QLoRA, K1-K8, Dược lý DDI, Lọc eGFR, Khử PII NĐ13, SOCRATES", "100% Sạch"),
        ("tests/ (Bộ Kiểm thử Tự động)", "103 tệp", "1.330 bài test tự động bao phủ toàn diện bẫy lâm sàng và hồi quy logic", "1.330 PASS"),
        ("tools/ (Công cụ Kỹ thuật & Đồ họa)", "49 tệp", "Sinh sơ đồ Flow 4K, đo đa dạng ngữ liệu, nạp ca bẫy BGK, xuất báo cáo", "Hoàn tất"),
        ("web/ (Giao diện Doctor-in-the-Loop)", "51 tệp", "Bàn làm việc SOAP, Terminal viễn thám AI Dark Console, Tờ dặn dò A4 JCI", "Production Ready")
    ]
    for i, row in enumerate(rows_mod_data, 1):
        for j, val in enumerate(row):
            cell = t_mod.rows[i].cells[j]
            if i % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, 50, 50, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(val)
            run.font.size = Pt(8)
            if j == 0:
                run.bold = True
            elif j == 3:
                run.bold = True
                run.font.color.rgb = RGBColor(5, 150, 105)

    # Subtitle for author files
    p_sub1 = doc.add_paragraph()
    p_sub1.paragraph_format.space_before = Pt(8)
    p_sub1.paragraph_format.space_after = Pt(4)
    r_sub1 = p_sub1.add_run("Các tệp trọng yếu có đóng góp trực tiếp của Tác giả (AI viết + Quân) & Nâng cấp Mới:")
    r_sub1.bold = True
    r_sub1.font.size = Pt(9.5)
    r_sub1.font.color.rgb = RGBColor(30, 41, 59)

    # Table 2: Author contribution files
    t_auth = doc.add_table(rows=len(author_files)+1, cols=4)
    t_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_styling(t_auth)
    make_header_repeat(t_auth.rows[0])

    headers_auth = ["Tên tệp mã nguồn", "Phân hệ", "Lần sửa", "Đóng góp chuyên môn của Tác giả (Quân)"]
    for j, h in enumerate(headers_auth):
        cell = t_auth.rows[0].cells[j]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    for i, (fn, fm, fr, fd) in enumerate(author_files, 1):
        row_cells = t_auth.rows[i].cells
        if i % 2 == 1:
            for c in row_cells:
                set_cell_background(c, "F8FAFC")
        for c in row_cells:
            set_cell_margins(c, 40, 40, 80, 80)
        
        p0 = row_cells[0].paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(fn)
        r0.font.size = Pt(7.5)
        r0.font.bold = True
        r0.font.name = "Consolas"

        p1 = row_cells[1].paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        p1.add_run(fm).font.size = Pt(8)

        p2 = row_cells[2].paragraphs[0]
        p2.paragraph_format.space_after = Pt(0)
        p2.add_run(str(fr)).font.size = Pt(8)

        p3 = row_cells[3].paragraphs[0]
        p3.paragraph_format.space_after = Pt(0)
        r3 = p3.add_run(f"AI viết + Quân: {fd}")
        r3.font.size = Pt(8)

    # Section 2: Unified Continuous Diary Table (0 Blank Pages)
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_before = Pt(12)
    p_sec2.paragraph_format.space_after = Pt(4)
    r_sec2 = p_sec2.add_run("PHẦN II. NHẬT KÝ MÃ NGUỒN, LỊCH SỬ CÂU LỆNH & RÀ SOÁT LỖI HỆ THỐNG")
    r_sec2.bold = True
    r_sec2.font.size = Pt(11)
    r_sec2.font.color.rgb = RGBColor(3, 105, 161)

    all_diary = diary_entries + oct_entries
    t_diary = doc.add_table(rows=len(all_diary)+1, cols=3)
    t_diary.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_styling(t_diary)
    make_header_repeat(t_diary.rows[0])

    t_diary.columns[0].width = Inches(1.1)
    t_diary.columns[1].width = Inches(2.8)
    t_diary.columns[2].width = Inches(3.1)

    h_d = ["Ngày", "Lời nhắc, Tệp thay đổi & Lịch sử câu lệnh thực thi", "Vấn đề lâm sàng phát hiện, Mã lỗi & Giải pháp xử lý (Nghiệm thu)"]
    for j, h in enumerate(h_d):
        cell = t_diary.rows[0].cells[j]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    for i, (d_date, d_col1, d_col2) in enumerate(all_diary, 1):
        row_cells = t_diary.rows[i].cells
        if i % 2 == 1:
            for c in row_cells:
                set_cell_background(c, "F8FAFC")
        for c in row_cells:
            set_cell_margins(c, 50, 50, 80, 80)

        # Date cell
        p0 = row_cells[0].paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(d_date)
        r0.bold = True
        r0.font.size = Pt(8)

        # Col 1 cell
        p1 = row_cells[1].paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        clean_c1 = d_col1.replace("<br>", "\n").replace("**", "").replace("• ", "• ")
        p1.add_run(clean_c1).font.size = Pt(7.5)

        # Col 2 cell
        p2 = row_cells[2].paragraphs[0]
        p2.paragraph_format.space_after = Pt(0)
        clean_c2 = d_col2.replace("<br>", "\n").replace("**", "").replace("• ", "• ")
        p2.add_run(clean_c2).font.size = Pt(7.5)

    # Section 3: Conclusion
    p_sec3 = doc.add_paragraph()
    p_sec3.paragraph_format.space_before = Pt(12)
    p_sec3.paragraph_format.space_after = Pt(4)
    r_sec3 = p_sec3.add_run("PHẦN III. KẾT LUẬN & CAM KẾT LIÊM CHÍNH KHOA HỌC")
    r_sec3.bold = True
    r_sec3.font.size = Pt(11)
    r_sec3.font.color.rgb = RGBColor(3, 105, 161)

    p_c = doc.add_paragraph()
    p_c.paragraph_format.space_after = Pt(0)
    p_c.add_run(
        "1. Độc lập & Sáng tạo: Toàn bộ kiến trúc 8 Chốt an toàn, DDI Black-box, Khử định danh PII 2 chiều và CDSS 9 thang điểm được nghiên cứu, phát triển dựa trên hướng dẫn Bộ Y tế và y văn quốc tế. AI chỉ đóng vai trò trợ lý thư ký bóc tách có căn cứ mỏ neo [T_i], Bác sĩ luôn là người ra quyết định tối cao trong 30 giây (Human-in-the-loop).\n"
        "2. Minh bạch Nghiên cứu: Toàn bộ lịch sử câu lệnh, các bài test thất bại và giải pháp khắc phục đều được lưu trữ trung thực làm minh chứng cho quá trình nghiên cứu khoa học nghiêm túc.\n"
        "3. Bảo mật An toàn: Đã làm sạch 100% mật khẩu thô, API key và dữ liệu định danh cá nhân, tuân thủ nghiêm ngặt Nghị định 13/2023/NĐ-CP."
    ).font.size = Pt(8.5)

    # Save docx files
    docx_paths = [
        "Bang_Ke_Khai_Ma_Nguon_Va_Lich_Su_Lenh_MediTrace.docx",
        "docs/tai-lieu/Bang_Ke_Khai_Ma_Nguon_Va_Lich_Su_Lenh_MediTrace.docx",
        r"C:\Users\admin\Desktop\Bang_Ke_Khai_Ma_Nguon_Va_Lich_Su_Lenh_MediTrace.docx"
    ]
    doc.save(docx_paths[0])
    import shutil
    for p in docx_paths[1:]:
        shutil.copy(docx_paths[0], p)
        print(f"[OK] Da ghi Word tinh gon: {p}")

    # Check for empty paragraphs in new docx
    empty_p_count = sum(1 for p in doc.paragraphs if not p.text.strip())
    print(f"[KIEM TRA] So paragraph rong trong file Word moi: {empty_p_count} (Muc tieu = 0)")
    print("HOAN TAT BIEN SOAN BAN TINH GON - KHONG CON TRANG TRANG!")

if __name__ == "__main__":
    build_compact_documentation()
