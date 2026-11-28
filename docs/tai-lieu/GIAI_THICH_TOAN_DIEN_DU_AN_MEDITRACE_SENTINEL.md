# BẢN GIẢI THÍCH TOÀN DIỆN DỰ ÁN MEDITRACE SENTINEL

> **Tóm tắt một câu:**  
> **MediTrace Sentinel** là trợ lý trí tuệ nhân tạo chuyên dụng lắng nghe cuộc khám bệnh bằng tiếng Việt ngay trên máy trạm nội bộ, tự động dựng bản nháp bệnh án chuẩn cấu trúc SOAP trong đó **mỗi dòng đều nối về lượt thoại & giây ghi âm gốc (`Click-to-Verify`)**, đồng thời cô lập mọi mẩu tin chưa chắc vào mục **`CẦN XÁC NHẬN`** và hỗ trợ rà soát an toàn dược lý/BHYT cho bác sĩ. Các bước luật và cảnh báo giúp giảm tối đa rủi ro lâm sàng, không thay thế quyết định chuyên môn của bác sĩ; bộ khử định danh chỉ che các mẫu nhận diện được theo cấu trúc.

---

## MỤC LỤC
1. [Bối cảnh thực tế: Khủng hoảng quá tải phòng khám và áp lực bệnh án](#1-bối-cảnh-thực-tế)
2. [Tại sao cần phải giải quyết vấn đề này ngay lập tức?](#2-tại-sao-cần-phải-giải-quyết)
3. [Bài toán cốt lõi MediTrace Sentinel giải quyết](#3-bài-toán-cốt-lõi)
4. [Sự khác biệt, đặc biệt và cần thiết: Vì sao phải là MediTrace mà không thể dùng ChatGPT?](#4-sự-khác-biệt-và-đặc-biệt)
5. [Kiến trúc 5 tầng & 6 gói lõi: Cách MediTrace khoanh vùng ảo giác AI và khóa bằng chứng](#5-cấu-trúc-triệt-tiêu-ảo-giác)
6. [Chi tiết 14 năng lực cốt lõi & Bộ công cụ thực chiến MediTrace Boost](#6-chi-tiết-14-tính-năng-nâng-cấp)
7. [Bảng số liệu thực nghiệm & Kiểm chứng đa nguồn (Cập nhật 27/11/2026)](#7-số-liệu-thực-nghiệm)
8. [Tầm nhìn và giá trị thực tế mang lại cho nền y tế Việt Nam](#8-giá-trị-thực-tế)

---

<a name="1-bối-cảnh-thực-tế"></a>
## 1. BỐI CẢNH THỰC TẾ: KHỦNG HOẢNG QUÁ TẢI PHÒNG KHÁM VÀ ÁP LỰC BỆNH ÁN

Tại các bệnh viện công lập và phòng khám đa khoa ở Việt Nam hiện nay, công tác ghi chép hồ sơ khám bệnh đang đối mặt với áp lực lớn:

* **Quá tải bệnh nhân ngoại trú:** Viện Chiến lược và Chính sách Y tế ghi nhận ở khu vực phòng khám, một bác sĩ khám **60–100 bệnh nhân/ngày** là phổ biến [6]. Bộ Y tế phải đặt trần **65 lượt khám BHYT/bàn khám/ngày** (Thông tư 15) [7]. Với nhịp đó, mỗi lượt gặp chỉ còn vài phút, và một lượt khám thường phải chia làm hai lần (hỏi bệnh, rồi xem kết quả xét nghiệm để kê đơn) [8].
* **Thiếu nhân lực:** Việt Nam có **12,5 bác sĩ/10.000 dân (2023)**, thấp hơn mục tiêu **15 (2025)** và **19 (2030)** của quy hoạch mạng lưới y tế [9].
* **Gánh nặng gõ bàn phím ("Pajama Time"):** Bác sĩ phải vừa hỏi bệnh vừa nhập liệu vào phần mềm bệnh viện (HIS), làm giảm giao tiếp mắt với người bệnh và kéo dài giờ hoàn tất hồ sơ sau ca trực.
* **Áp lực chuẩn hóa hồ sơ & pháp lý:** **Thông tư 46/2018/TT-BYT**, **Thông tư 32/2023/TT-BYT**, **Thông tư 26/2025/TT-BYT** và **Quyết định 130/QĐ-BYT** đòi hỏi bệnh án điện tử (EMR), đơn thuốc điện tử và bảng XML BHYT phải đầy đủ, chính xác và có căn cứ chặt chẽ.

### 1.1. Số liệu bối cảnh (nguồn bên ngoài, không phải số đo của dự án)

| Vấn đề | Số liệu | Nguồn |
|---|---|---|
| **Bác sĩ kiệt sức (Mỹ)** | **43,2%** bác sĩ có ít nhất một triệu chứng kiệt sức năm 2024, giảm từ 48,2% (2023) và 53% (2022). Cấp cứu 52,2%, y học gia đình 46,4% | AMA [1] |
| **Bác sĩ kiệt sức (Việt Nam)** | Chưa có ước tính đại diện toàn quốc. Các khảo sát đơn lẻ: **hơn 41%** bác sĩ có nguy cơ kiệt sức (374 bác sĩ, BV TP Thủ Đức, 2022–2023); **25,4%** nhân viên Viện Sức khỏe Tâm thần Quốc gia; **21,3%** bác sĩ nội trú (ĐH Y Dược Thái Nguyên, 2025) | [2] |
| **Thời gian dành cho hồ sơ điện tử** | Bác sĩ ngoại trú dùng trung bình **5,8 giờ trên phần mềm hồ sơ cho mỗi 8 giờ khám theo lịch**, riêng ghi chép **2,3 giờ**; khoảng **42%** thời gian này rơi ra ngoài giờ khám (dữ liệu 200.081 bác sĩ, 396 tổ chức) | J Gen Intern Med 2024 [3] |
| **Hiệu quả của trợ lý ghi chép AI** | Sau 30 ngày dùng trợ lý ghi chép AI, tỷ lệ kiệt sức giảm từ **51,9% xuống 38,8%** (6 hệ thống y tế Mỹ). Một thử nghiệm ngẫu nhiên trên 238 bác sĩ ghi nhận giảm thời gian viết ghi chú | JAMA Netw Open 2025; NEJM AI 2025 [4] |
| **AI viết bệnh án vẫn có thể bịa và bỏ sót** | Trên 12.999 câu do bác sĩ chấm, mô hình ngôn ngữ lớn viết ghi chú lâm sàng có tỷ lệ **bịa 1,47%** và **bỏ sót 3,45%** | npj Digital Medicine 2025 [5] |
| **An toàn người bệnh (toàn cầu)** | Khoảng **1/10** người bệnh bị tổn hại khi được chăm sóc y tế; **hơn 3 triệu** ca tử vong mỗi năm do chăm sóc không an toàn; **hơn 50%** tổn hại có thể phòng tránh, và **một nửa** trong số đó liên quan đến thuốc | WHO 2023 [10] |
| **Chi phí sai sót dùng thuốc** | Khoảng **42 tỷ USD/năm**, gần 1% chi tiêu y tế toàn cầu. Mệt mỏi của nhân viên y tế và quá tải là các nguyên nhân được nêu | WHO [11] |

**Ý nghĩa với MediTrace:**
- Trợ lý ghi chép AI có thể giảm gánh nặng giấy tờ và kiệt sức, nhưng **AI viết bệnh án vẫn bịa khoảng 1–2% số câu**. Trong hồ sơ y tế, mỗi câu bịa về dị ứng hay thuốc là một nguy cơ thật.
- Vì vậy MediTrace không cố làm một AI "viết hay hơn", mà làm cho **mỗi dòng đều phải có bằng chứng**, và dòng nào không chứng minh được thì thành câu hỏi cho bác sĩ.
- *Lưu ý trung thực:* dự án **chưa đo** thời gian tiết kiệm hay mức giảm kiệt sức trên bác sĩ thật. Các số trên chỉ mô tả bối cảnh.

**Nguồn:**
1. AMA, *Physician burnout rate drops below 50% for first time in 4 years* — https://www.ama-assn.org/practice-management/physician-health/physician-burnout-rate-drops-below-50-first-time-4-years ; *Physician burnout statistics 2024* — https://www.ama-assn.org/practice-management/physician-health/physician-burnout-statistics-2024-latest-changes-and-trends
2. VOV, *Nhiều bác sĩ bị "kiệt sức" ở mức cao* — https://vov.gov.vn/nhieu-bac-si-bi-kiet-suc-o-muc-cao-dtnew-528022 ; Tạp chí Nghiên cứu Y học, *Tình trạng kiệt sức và yếu tố liên quan của bác sĩ nội trú ĐH Y Dược Thái Nguyên* — https://tapchinghiencuuyhoc.vn/index.php/tcncyh/article/view/4087 ; Tạp chí Y học Cộng đồng, *Burnout among medical staff at the National Institute of Mental Health* — https://tapchiyhcd.vn/index.php/yhcd/en/article/download/4465/4170 ; Lifestyle Medicine Việt Nam (nhận định chưa có ước tính toàn quốc) — https://lifestylemedicinevietnam.org/lifestyle-medicine-for-healthcare-professionals-in-viet-nam-personal-health-burnout-and-the-role-of-individual-and-organizational-action
3. Journal of General Internal Medicine (2024), EHR use across specialties — https://link.springer.com/article/10.1007/s11606-024-08930-4
4. JAMA Network Open (10/2025), *Use of Ambient AI Scribes to Reduce Administrative Burden and Professional Burnout* — https://pubmed.ncbi.nlm.nih.gov/41037268/ ; NEJM AI (2025), *Ambient AI Scribes in Clinical Practice: A Randomized Trial* — https://pubmed.ncbi.nlm.nih.gov/41497288/
5. Asgari và cộng sự, *A framework to assess clinical safety and hallucination rates of LLMs for medical text summarisation*, npj Digital Medicine (2025) — https://pmc.ncbi.nlm.nih.gov/articles/PMC12075489/
6. Viện Chiến lược và Chính sách Y tế, nghiên cứu thực trạng quá tải bệnh viện — http://www.hspi.org.vn/vcl/Nghien-cuu-thuc-trang-qua-tai-duoi-tai-cua--he-thong-benh-vien-cac-tuyen-va-de-xuat-giai--phap-khac-phuc-t85-8128.html
7. VOV, *Bác sĩ khám tối đa 65 bệnh nhân/bàn khám/ngày* — https://vov.vn/xa-hoi/bac-si-kham-toi-da-65-benh-nhanban-khamngay-con-nhieu-ban-khoan-786748.vov
8. VnExpress, *Tự sự của bác sĩ cấp cứu về áp lực với thầy thuốc VN* — https://vnexpress.net/tu-su-cua-bac-si-cap-cuu-ve-ap-luc-voi-thay-thuoc-vn-3176759.html
9. VnExpress, *Vietnam aims for 15 doctors per 10,000 people by 2025* — https://e.vnexpress.net/news/news/vietnam-aims-for-15-doctors-per-10-000-people-by-2025-4716651.html ; Tạp chí Y học Cộng đồng — https://tapchiyhcd.vn/index.php/yhcd/article/download/2066/1537/1793
10. WHO, *Patient safety — fact sheet* (11/9/2023) — https://www.who.int/news-room/fact-sheets/detail/patient-safety
11. WHO, *WHO launches global effort to halve medication-related errors in 5 years* — https://www.who.int/news-room/detail/29-03-2017-who-launches-global-effort-to-halve-medication-related-errors-in-5-years

---

<a name="2-tại-sao-cần-phải-giải-quyết"></a>
## 2. TẠI SAO CẦN PHẢI GIẢI QUYẾT VẤN ĐỀ NÀY NGAY LẬP TỨC?

1. **Nguy cơ ghi chép thiếu hoặc sót tiền sử trọng yếu:** Khi quá vội, các chi tiết nhạy cảm như dị ứng thuốc, bệnh nền (suy thận, tăng huyết áp, đái tháo đường) hoặc thuốc bệnh nhân tự mua uống ở nhà rất dễ bị bỏ sót. WHO nêu mệt mỏi của nhân viên y tế và quá tải là các nguyên nhân dẫn tới sai sót dùng thuốc, và một nửa số tổn hại có thể phòng tránh trong chăm sóc y tế liên quan đến thuốc (mục 1.1).
2. **Giải pháp AI phổ thông chưa đủ an toàn:** Trợ lý ghi chép AI giúp giảm kiệt sức, nhưng AI viết văn xuôi vẫn bịa và bỏ sót một phần nhỏ số câu (mục 1.1). Nếu không có cơ chế kiểm từng dòng, bác sĩ phải đọc lại toàn bộ, và lợi ích tiết kiệm thời gian bị mất.
3. **Nguy cơ tai biến dược lý:**
   * Quên ghi nhận dị ứng kháng sinh làm tăng rủi ro kê trùng thuốc gây phản vệ.
   * Kê đồng thời hai thuốc có tương tác nặng (như Clopidogrel + Omeprazole hoặc Warfarin + Ibuprofen) mà không kịp tra cứu Dược thư.
   * Chưa kịp hiệu chỉnh liều cho bệnh nhân suy thận theo độ lọc cầu thận (eGFR).
4. **Rủi ro pháp lý khi hồ sơ thiếu truy vết:** Bệnh án là tài liệu pháp lý cốt lõi; nếu bản nháp ghi nhầm lời người nhà thành bệnh sử bệnh nhân hoặc giữ lại thông tin người bệnh đã đính chính, bác sĩ sẽ gánh rủi ro chuyên môn.

---

<a name="3-bài-toán-cốt-lõi"></a>
## 3. BÀI TOÁN CỐT LÕI MEDITRACE SENTINEL GIẢI QUYẾT

**MediTrace Sentinel** hướng tới mục tiêu: **Trả lại đôi mắt và đôi tay cho bác sĩ trong phòng khám, nhưng luôn giữ bác sĩ ở vị trí người duyệt cuối cùng có chứng cứ đối chiếu.**

* Bác sĩ tập trung trò chuyện và thăm khám tự nhiên với bệnh nhân và người nhà.
* Hệ thống ghi âm/gỡ băng tại chỗ (`PhoWhisper`) và dựng **bản nháp bệnh án cấu trúc SOAP** (*Chủ quan – Khách quan – Đánh giá – Kế hoạch*).
* Bất kỳ mẩu tin nào chưa chắc chắn, thiếu căn cứ đối chiếu, sai chủ thể hoặc nghi nhiễu ASR đều **không bị xóa ngầm** và **không tự lọt vào thân bệnh án**, mà được cô lập sang mục **`CẦN XÁC NHẬN`** kèm câu trích, giây ghi âm (`±0,5s`) và nút `Nghe lại` một chạm.

---

<a name="4-sự-khác-biệt-và-đặc-biệt"></a>
## 4. SỰ KHÁC BIỆT, ĐẶC BIỆT VÀ CẦN THIẾT: VÌ SAO PHẢI DÙNG MEDITRACE MÀ KHÔNG THỂ DÙNG CHATGPT?

| Tiêu chí | ChatGPT / LLM đám mây viết văn xuôi | MediTrace Sentinel |
| :--- | :--- | :--- |
| **1. Pháp lý & Bảo mật dữ liệu** | Gửi dữ liệu hội thoại nhạy cảm ra máy chủ bên thứ ba ngoài cơ sở khám chữa bệnh. Mặc định không đáp ứng yêu cầu giữ dữ liệu nội bộ tại chỗ. | **Lõi dựng bản nháp chạy 100% tại chỗ (`On-premise`).** Sử dụng mô hình mở `Qwen3-4B` (Apache-2.0); công tắc mô hình ngoài mặc định **TẮT**; Trợ lý tra cứu y văn dùng danh sách cho phép ẩn danh (Allowlist). |
| **2. Kiểm soát ảo giác AI** | Sinh văn xuôi mượt mà trong hộp đen; có thể tự suy diễn lý do, chẩn đoán hoặc thông tin không có trong lời thoại. | **Kiến trúc Lai (Neuro-Symbolic):** AI chỉ rút JSON mệnh đề thô ở Bước 1; toàn bộ khâu gom người, đính chính, **7 cổng khóa K1–K7** và **56 mã cảnh báo (Chính sách D)** đều là mã luật kiểm thử được. |
| **3. Truy vết hai chiều (`Click-to-Verify`)** | Văn xuôi dài không gắn chỉ mục từng câu về giây ghi âm gốc. | **Mỗi dòng bệnh án nối tới đúng lượt `[T_i]` và đoạn băng gốc `[start_s - 0.5, end_s + 0.5]`**, cho phép bấm `Space` nghe lại tức thì. |
| **4. Xử lý bẫy ngôn ngữ Việt** | Dễ gộp nhầm *"Bố em bị hen"* vào bệnh nhân; dễ bỏ qua tự sửa *"4 ngày… à không, 10 ngày"*; dễ hiểu nhầm câu điều kiện/hỏi đáp. | **Tách riêng `nguoi_noi` và `chu_the_id`**, dùng **FSM đính chính** lưu vết trạng thái `bị thay thế`, khóa chặt mẫu người nhà tự xưng và câu hỏi chưa trả lời (`QUESTION_AS_FACT`). |
| **5. Dược lý, BHYT & Chốt ký WORM** | Không tích hợp Dược thư VN, BHYT XML1–XML5 hay sổ cái chống sửa lén sau ký duyệt. | Tích hợp **158 hoạt chất Dược thư QG**, tính eGFR/9 thang điểm, tiền kiểm BHYT XML3/XML5 TT 26/2025, và **khóa cứng ký duyệt WORM `SHA-256` + `.anchor.json`** khi còn mục `Cần xác nhận`. |

**Bảng trên so sánh thiết kế, không phải kết quả đo.** Dự án **chưa chạy so sánh đầy đủ** với mô hình thương mại. Phép đo duy nhất có thật (173/300 ca, dừng do hết số dư) cho thấy mô hình thương mại **ghi nhầm người ít hơn** mô hình nhỏ của dự án: 1,4% so với 7,6% ở bộ đính chính, 15,4% so với 22,9% ở bộ đổi chủ thể (`docs/final/Báo cáo dự án.md`, `README.md`). Cách để mô hình nhỏ viết thẳng bản nháp cũng ghi đúng người **cao hơn** đường ống (0,939 so với 0,748 ở bộ đổi chủ thể). Vì vậy điểm khác biệt của MediTrace là chạy tại chỗ và kiểm tra được từng dòng, không phải chính xác hơn. Kế hoạch đo đầy đủ: `docs/superpowers/plans/2026-11-27-nang-cap-toan-dien-bgk.md` Task 6.

---

<a name="5-cấu-trúc-triệt-tiêu-ảo-giác"></a>
## 5. KIẾN TRÚC 5 TẦNG & 6 GÓI LÕI: CÁCH MEDITRACE KHOANH VÙNG ẢO GIÁC AI VÀ KHÓA BẰNG CHỨNG

Thư mục lõi Python `src/` được quy hoạch rành mạch thành **6 gói nghiệp vụ** (chi tiết tại [`BAN_DO_MA_NGUON.md`](BAN_DO_MA_NGUON.md)): `bo_du_lieu/`, `duong_ong/`, `canh_bao/`, `cong_cu_lam_sang/`, `do_luong/`, `he_thong/` (cùng mô-đun `audio/` và `huan_luyen/`):

```text
[Lời nói cuộc khám]
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│ TẦNG 0: Gỡ băng & Chuẩn hóa đầu vào (PhoWhisper + b0_chuan_hoa)     │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ TẦNG 1: Rút mệnh đề nguyên tử `PhatBieu` (duy nhất dùng Qwen3-4B)   │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ TẦNG 2: Gom người & thực thể (b2_gom_nguoi_thuc_the.py)              │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ TẦNG 3: Máy trạng thái đính chính & diễn biến (b3_cap_nhat)          │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ TẦNG 4: Khóa căn cứ K1–K7 + Lớp cảnh báo 56 mã Chính sách D          │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ TẦNG 5: Ghép bản nháp SOAP mẫu cứng + Định tuyến 3 vùng (b5_*)       │
└──────────────────────────────────────────────────────────────────────┘
```

* **Chỉ duy nhất Tầng 1 dùng AI (`Qwen3-4B` QLoRA 4-bit):** Đọc hội thoại và xuất JSON các `PhatBieu` (`noi_dung`, `nguoi_noi`, `chu_the_id`, `phu_dinh`, `do_chac_chan`, `tinh_huong`, `bang_chung`, `trich_dan`, `thuoc`, `audio_spans`).
* **Từ Tầng 2 đến Tầng 5 là 100% mã luật xác định:**
  * **Cổng K1 (`trich_khong_co` / `FABRICATED_QUOTE`):** Đối chiếu từng câu trích dẫn với đúng lượt nói được dẫn; sai lượt hoặc không tồn tại là chặn ngay.
  * **Cổng K2–K3:** Khóa đại từ nhân xưng và tách biệt người nhà (`chu_the_id != 0`) khỏi hồ sơ chính của bệnh nhân.
  * **Cổng K4–K6:** Chặn câu điều kiện/kế hoạch bị ghi thành sự việc đã làm, chặn nâng mức chắc chắn, và đối chiếu số liệu liều thuốc/thời gian.
  * **Cổng K7 & Tầng 3 (`FSM`):** Khi người nói tự sửa (*"uống 2 viên… à nhầm 1 viên"*), bản cũ chuyển sang `bị thay thế` ở `CẦN XÁC NHẬN` để giữ vết kiểm toán chứ không xóa mất.
  * **Lớp cảnh báo Chính sách D (`src/canh_bao/` — cập nhật 27/11/2026):**
    * Đưa `"thuoc_nti"` vào `LOAI_NANG` (`src/canh_bao/loai.py`) để thuốc khoảng điều trị hẹp được bảo vệ ngang mức `"thuoc"` và `"di_ung"`.
    * Bắt rơi liều (`DOSE_MISMATCH`) khi lượt dẫn có nêu đơn vị liều thuốc (`s.ho == "lieu"`, vd `mg`, `viên`, `ml`) nhưng mệnh đề rút ra thiếu cả `thuoc` lẫn liều (`src/canh_bao/phat_hien.py`).
    * Bắt 16 âm tiết tiếng Việt mất dấu bắt buộc nghi nhiễu ASR (`thuc_the:nhieu_dau_asr` -> `UNSUPPORTED_INFORMATION`, bỏ qua chữ viết tắt in hoa như `DIA`) và lỗi trộn chủ thể người nhà có kiểm ranh giới từ (`FAMILY_PATIENT_MIXUP`, loại trừ tiền sử gia đình và số đếm *"ba ngày/ba lần"*).
* **Tầng 5 (`b5_viet_ban_nhap.py` & `b5_xep_cho_cong_rui_ro.py`):** Tuyệt đối không dùng AI viết tự do; lắp ghép câu cố định vào đúng ngăn SOAP hoặc chuyển sang `CẦN XÁC NHẬN`.

---

<a name="6-chi-tiết-14-tính-năng-nâng-cấp"></a>
## 6. CHI TIẾT 14 NĂNG LỰC CỐT LÕI & BỘ CÔNG CỤ MEDITRACE BOOST

### 1. Hệ thống chốt kiểm soát an toàn đa tầng — `src/duong_ong/b4_kiem_can_cu.py`, `src/canh_bao/`, `src/he_thong/rao_chan_an_toan.py`
* **Vấn đề giải quyết:** Ngăn lỗi lan truyền dây chuyền từ ASR/diarization → rút mệnh đề → bản nháp bệnh án cuối.
* **Cơ chế:** Kết hợp 7 khóa căn cứ (K1–K7), 56 mã cảnh báo phân tầng 3 mức chống mệt mỏi cảnh báo (`CHAN_NGAY`, `CAN_XEM_XET`, `TINH_LUOC` trong `src/canh_bao/gop.py`) và khóa cứng ký duyệt khi `tongMenhDe < 1` hoặc còn mục `Cần xác nhận` chưa xử lý (`web/may-chu/worm.ts`).

### 2. Bộ tra cứu dược lý Aho-Corasick & Tương tác thuốc (DDI) — `src/cong_cu_lam_sang/tra_duoc_thu_aho_corasick.py`, `canh_bao_tuong_tac_thuoc.py`
* **Vấn đề giải quyết:** Phát hiện nhanh cặp thuốc tương tác nguy hiểm (Clopidogrel ↔ Omeprazole, Warfarin ↔ Ibuprofen), dị ứng chéo (`di_ung_cheo.py`), trùng hoạt chất từ nhiều toa cũ và liều trần 24h.
* **Nâng cấp mới (27/11/2026):** Sửa lỗi nạp `ThongTinDuocThu` để `BoTraCuuDuocThuAhoCorasick` nạp đầy đủ **158 hoạt chất & biệt dược** từ `data/tri_thuc_thuoc.json` *(lưu ý: tệp tri thức mang cờ `da_duyet = false`, đóng vai trò tham khảo cho bác sĩ)*.

### 3. Hiệu chỉnh liều theo chức năng thận (eGFR) — `src/cong_cu_lam_sang/hieu_chinh_lieu.py`, `doc_phieu_xet_nghiem.py`, `chuan_hoa_don_vi_xet_nghiem.py`
* **Cơ chế:** Bóc chỉ số từ phiếu xét nghiệm cũ, quy đổi đơn vị (`Creatinine µmol/L ↔ mg/dL`), tính Cockcroft-Gault / CKD-EPI theo tuổi-giới-cân nặng thật và nhắc điều chỉnh liều.

### 4. Tự động tính 9 thang điểm nguy cơ lâm sàng — `src/cong_cu_lam_sang/thang_diem_nguy_co.py`
* **Cơ chế:** Hỗ trợ tính nhanh **GCS, qSOFA, CURB-65, CHA2DS2-VASc, Wells, Glasgow-Blatchford, NYHA, Child-Pugh, BMI**.

### 5. Báo động đỏ cận lâm sàng & Đối soát kết quả — `src/cong_cu_lam_sang/doi_soat_can_lam_sang.py`, `nap_ket_qua_lis_hl7.py`
* **Cơ chế:** Quét ngưỡng nguy hiểm sinh tồn (Troponin, Kali máu…) và hỗ trợ nạp thông điệp LIS HL7v2 ORU^R01.

### 6. Gợi ý câu hỏi lâm sàng theo khung SOCRATES — `src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py`, `src/duong_ong/b6_goi_y_hoi_lai.py`
* **Cơ chế:** Gợi ý tối đa 3 câu hỏi súc tích giúp bác sĩ hỏi nốt thông tin còn thiếu trong 3–5 phút khám.

### 7. Khử định danh bảo vệ thông tin cá nhân (PHI/PII) — `src/he_thong/khu_dinh_danh.py`, `web/may-chu/tro-ly/an-danh.ts`
* **Cơ chế:** `ClinicalDeidentifier` ẩn danh các định danh theo mẫu (tên có xưng hô, SĐT, CCCD, BHYT, địa chỉ) trước khi xuất/gửi ra trợ lý ngoài; trên Trợ lý y văn còn sử dụng Allowlist chỉ trích trường cấu trúc và chặn ngay câu hỏi có PII từ bác sĩ.
* **Minh bạch giới hạn đo đạc (27/11/2026):** Khi kiểm tra chéo với **847 nhãn vàng `NAME`/`PATIENT_ID` trên 1.000 câu báo chí `PhoNER_COVID19`**, `ClinicalDeidentifier` mới che được **`10/847` (`1,2%`)** do văn bản báo chí viết mã số/tên viết tắt không khung (*"bệnh nhân 416", "bà H.T.P"*) — nhóm ghi nhận rõ để cải tiến nhận diện tên riêng không khung.

### 8. Liên thông chuẩn HL7 FHIR R4 & BHYT XML1–XML5 — `src/cong_cu_lam_sang/xuat_fhir_r4.py`, `tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`, `kiem_toan_xml_bhyt.py`
* **Cơ chế:** Xuất gói `HL7 FHIR R4 Bundle` (loại bỏ mệnh đề bị bác sĩ bấm `Bỏ` và thuốc đã ngừng) và tiền kiểm **13 quy tắc biện luận CLS (XML3/XML4 ↔ XML5)** + kiểm tra cân nặng Nhi khoa (`< 72 tháng` theo **TT 26/2025/TT-BYT**).

### 9. Bản dặn dò người bệnh đời thường & Mã QR theo dõi — `src/cong_cu_lam_sang/to_dan_do_benh_nhan.py`, `ho_so_benh_nhan_qr.py`
* **Cơ chế:** Dịch đơn thuốc thành lịch uống Sáng – Trưa – Chiều – Tối dễ hiểu kèm dấu hiệu cảnh báo đỏ cần tái khám ngay và cổng QR chỉ đọc có hạn cho bệnh nhân.

### 10. Chuẩn hóa phương ngữ 3 miền & Từ điển âm vị thuốc ASR (G2P) — `src/duong_ong/b0_chuan_hoa_phuong_ngu.py`, `src/cong_cu_lam_sang/tu_dien_phuong_ngu_lam_sang.py`, `src/audio/asr/contextual_trie_600.py`
* **Nâng cấp mới (27/11/2026):**
  * Mở rộng phương ngữ 3 miền Bắc–Trung–Nam khai thác từ tập `ViDia2Std/train.csv`, kèm **khiên bảo vệ ngữ cảnh nghiêm ngặt** để không làm sai nghĩa thuật ngữ y khoa chuẩn (*tê bì tứ chi, sinh thiết mô gan, cấy ghép thận, vô kinh, viêm bờ mi, giời leo, ảnh chụp X-quang*).
  * `ContextualPrefixTrie600` bổ sung **65+ biến thể G2P thuốc trại âm** (kèm điều kiện ngữ cảnh thuốc cho cụm 2 âm tiết để không báo nhầm với câu đời thường như *"nấm a mốc"*, *"đi pa ra công viên"*), **chỉ trả thẻ gợi ý đối chiếu chứ tuyệt đối không tự sửa đè chữ gốc**.

### 11. Điều phối phần cứng & Hàng đợi bất đồng bộ — `src/he_thong/dieu_phoi_cac_chot_an_toan.py`, `dich_vu_http.py`, `web/may-chu/hang-doi.ts`
* **Cơ chế:** Hỗ trợ chạy chế độ không GPU (`--khong-mo-hinh`), tự nhả VRAM khi nghỉ (`--nghi-sau-phut`), giới hạn RAM (`--tran-ram-gb`) và xử lý hàng đợi tạo nháp nền `202 Accepted` để bác sĩ khám cuốn chiếu ngay sang bệnh nhân kế tiếp.

### 12. Ma trận đa bệnh lý & Sinh hội thoại có kiểm soát — `src/bo_du_lieu/sinh_ca_da_benh_ly.py`
* **Cơ chế:** Ghép bệnh cấp tính trên nền bệnh mạn tính để tăng tính chân thực của dữ liệu mô phỏng và đánh giá khả năng tách diễn biến của hệ thống.

### 13. Định tuyến an toàn "Không bao giờ xóa ngầm" (`CẦN XÁC NHẬN`) — `src/canh_bao/`, `src/duong_ong/b5_xep_cho_cong_rui_ro.py`
* **Cơ chế:** Tách 2 trục (mức nghiêm trọng lâm sàng × độ bất định căn cứ); thông tin trọng yếu còn nghi ngờ luôn nằm trong `CẦN XÁC NHẬN` và khóa nút ký duyệt.

### 14. Mở rộng kho 657 khuôn bệnh độc lập & Kiểm chứng 5 bộ dữ liệu ngoài nguồn — `src/bo_du_lieu/kho_khuon.py`, `tools/do_da_nguon_doc_lap.py`
* **Cơ chế:** Mở rộng từ 200 lên **657 khuôn ca bệnh (21 hệ cơ quan)** chia rời theo tên bệnh (`515` Train / `72` Dev / `70` Test, `0` khuôn giao nhau, bảo toàn nguyên vẹn mã băm vàng `BAM_VANG` 200 khuôn gốc trong `tests/test_bo_sinh_goc_khong_doi.py`), đồng thời kiểm chứng chéo trên **5 bộ dữ liệu tiếng Việt công khai bên ngoài**: `ViDia2Std`, `ViHealthQA`, `ViMedAQA`, `ViMQ`, `PhoNER_COVID19`.

### MediTrace Boost (Tối ưu thực chiến phòng khám & Pháp lý bệnh viện)
* **Chép HIS 1 chạm & Giữ chữ ký WORM chống sửa lén:** Chuỗi dán 5 ô VNPT-HIS/Viettel HIS (`HisSmartCopyPopover.tsx`), kết hợp sổ cái WORM `SHA-256` kèm tệp neo ngoài `.anchor.json` phát hiện cả thao tác sửa/xóa trực tiếp dưới SQLite (`worm.ts` / `nhat_ky_ky_duyet_worm.py`).
* **8 biểu mẫu hành chính chạy tại chỗ & Nội trú/Thủ thuật:** Phiếu chuyển tuyến TT 01/2025, Giấy nghỉ BHXH kiểm trần 30 ngày TT 25/2025, Tờ điều trị đi buồng nội trú TT 32/2023 (`di_buong_noi_tru.py`), Cam đoan PTTT 6 trụ cột Luật KCB 2023 (`cam_doan_thu_thuat.py`), cùng thao tác bàn phím `J/K/Enter/Space` và đọc khám thực thể `F2`.

---

<a name="7-số-liệu-thực-nghiệm"></a>
## 7. BẢNG SỐ LIỆU THỰC NGHIỆM CHỨNG MINH HIỆU QUẢ

Toàn bộ các cải tiến được đo đạc và tái lập trực tiếp bằng kịch bản Python/TypeScript trong kho mã (xem điều kiện đo và giới hạn chi tiết tại [`BAO_CAO_CAI_TIEN_CHANG_1.md`](BAO_CAO_CAI_TIEN_CHANG_1.md) và `docs/ket-qua/`):

| Hạng mục đo đạc | Đối chứng / Trước nâng cấp | Kết quả hiện tại (Cập nhật 27/11/2026) | Phạm vi & Ghi chú trung thực |
| :--- | :--- | :--- | :--- |
| **Kiểm thử tự động toàn kho** | 370 test ban đầu | **`1.942` test Pytest qua, `27` bỏ qua (lần chạy 26/11/2026, `README.md`) + `96` test TypeScript/BFF** | TypeScript `tsc --noEmit` 0 lỗi, build sản xuất thành công. |
| **Lỗi nguy hiểm lọt thân bản nháp (`lot_nguy_hiem`)** | Chính sách C: `45,9%` (`101/220`)<br>Chính sách D cũ: `24,1%` (`53/220`) | **Chính sách D mới: `11,8%` (`26/220`) — chặn `88,2%` (`194/220`)** | Đo trên **chính 4 tập phát triển đã dùng để viết các luật mới** (300 ca, 2.789 phát biểu, so với bộ chấm tự động — chưa phải số liệu trên tập kín); đổi lại chặn thừa `8,0%` (C) → `10,0%` (D). Tập giữ kín `thach_thuc_v2` giữ `0,946` (`doi_chu_the`) & `0,871` (`cay-loi`). |
| **Chặn lỗi nguy hiểm theo nhóm (`do_truyen_lan_loi_tung_tang`)** | Tổng tuyến: `75,9%` (`167/220`)<br>Nhiễu ASR: `53,7%` (`36/67`) | **Tổng tuyến: `88,2%` (`194/220`)** — Đổi chủ thể `96,5%`, Phương ngữ `93,3%`, Đính chính `84,0%`, Nhiễu ASR **`74,6%` (`50/67`)** | Trên cùng 4 tập thách thức phát triển (`docs/ket-qua/truyen-lan-loi-tung-tang.json`). |
| **Tỷ lệ bỏ sót mệnh đề (`bo-sot-qwen3-4b.md`)** | Qwen3-4B chưa train: `43,1%` | **Qwen3-4B + QLoRA: `11,5%`** (Wilson 95%: `8,4%–15,6%`, 0 lỗi JSON) | Đo trên 30 ca phát triển ngoài khuôn (304 mệnh đề), so với bộ chấm tự động, đáp án v1; lần chạy 26/11: adapter v1 `11,8%`, adapter v3 `14,1%`; lưu ý trọng số Qwen3-4B chạy trên GPU 12 GB. |
| **Chuẩn hóa phương ngữ trên `ViDia2Std/test.csv`** | Lỗi từ gốc so với câu chuẩn: `30,1%` | **Đổi đúng `28,0%` (`1.192/4.264`), tổng phủ `37,1%`, lỗi từ giảm còn `21,9%` (`doi_thua: 44`)** | 1.603 câu phương ngữ 63 tỉnh; bảng có khai thác thêm từ `ViDia2Std/train.csv`, giữ nguyên từ y khoa chuẩn. |
| **Phủ dược lý & Đối chiếu 4 bộ công khai khác** | Trước sửa chỉ nạp 33 thuốc cứng | **Nạp `158` hoạt chất (`ViMedAQA`: `87/500` mẫu bắt thuốc; `ViHealthQA`: bắt thuốc ở `14` câu hỏi và `42` câu trả lời trên `2.013` mẫu)** | `PhoNER_COVID19` (`1.000` câu): chỉ che được `10/847` (`1,2%`) nhãn vàng `NAME`/`PATIENT_ID` viết tắt/mã số không khung — ghi nhận làm hạn chế cần cải tiến. |
| **Độ phong phú kho khuôn v2 (5.000 ca)** | v1: `20.190` câu duy nhất (lặp `76,92%`) | **v2: `45.835` câu duy nhất (lặp `47,37%`, ≥ 8 từ: `42,19%`)** | 657 khuôn thuộc 21 hệ cơ quan; Jaccard từ khóa Train–Test trung bình `5,87%`; 100% trích dẫn trong dữ liệu tự sinh là chuỗi con (kiểm dữ liệu huấn luyện, không phải đầu ra mô hình). |

---

<a name="8-giá-trị-thực-tế"></a>
## 8. TẦM NHÌN VÀ GIÁ TRỊ THỰC TẾ MANG LẠI CHO NỀN Y TẾ VIỆT NAM

1. **Đối với Bác sĩ:** Giảm thao tác gõ phím lặp lại, có công cụ kiểm tra tương tác thuốc, eGFR, 9 thang điểm lâm sàng, biện luận CLS BHYT và phát lại đúng câu nói gốc chỉ bằng 1 chạm — giúp tập trung hơn vào thăm khám và giải thích cho người bệnh *(chưa công bố số giờ tiết kiệm thực tế vì dự án chưa thực hiện thử nghiệm lâm sàng với bác sĩ ngoài đời)*.
2. **Đối với Người bệnh:** Được lắng nghe trọn vẹn hơn, giảm nguy cơ bỏ sót dị ứng/tương tác thuốc nhờ chốt rà soát đa tầng, và nhận bản dặn dò tiếng Việt dễ hiểu kèm lịch uống thuốc rõ ràng.
3. **Đối với Bệnh viện và Ngành Y tế:** Chạy tại chỗ nên dữ liệu người bệnh không cần rời phòng khám (khung pháp lý hiện hành: **Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15** và **Nghị định 356/2025/NĐ-CP**, hiệu lực 01/01/2026), sẵn sàng liên thông chuẩn **HL7 FHIR R4 / XML1–XML5** theo **QĐ 130/QĐ-BYT** & **TT 26/2025/TT-BYT**, và đảm bảo vết kiểm toán pháp lý WORM `SHA-256` minh bạch.

---

> **Tài liệu đi kèm:** bộ hỏi – đáp từ dễ đến khó [`docs/HOI_DAP_BGK.md`](docs/HOI_DAP_BGK.md) · giải thích cấu trúc mã [`docs/GIAI_THICH_CAU_TRUC_DU_AN.md`](docs/GIAI_THICH_CAU_TRUC_DU_AN.md).

> **THÔNG ĐIỆP KẾT LUẬN:**  
> **MediTrace Sentinel** không thay thế bác sĩ và không viết bệnh án kiểu "hộp đen". Đây là hệ thống trợ lý lâm sàng **lấy bằng chứng lời thoại làm gốc, lấy luật y khoa xác định làm rào chắn an toàn, và lấy quyết định duyệt cuối của thầy thuốc làm chuẩn mực pháp lý**.
