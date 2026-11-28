# Bộ hỏi – đáp MediTrace Sentinel (từ dễ đến khó)

> Dùng để chuẩn bị trả lời Ban Giám khảo. Mỗi câu có **trả lời ngắn** (nói trong 15 giây), **giải thích chi tiết**, **bằng chứng** (tệp mã hoặc số đo), và với câu khó thì có thêm **nếu bị hỏi vặn**.
> Số liệu đo của dự án: [`BAO_CAO_CAI_TIEN_CHANG_1.md`](../BAO_CAO_CAI_TIEN_CHANG_1.md), [`docs/ket-qua/`](ket-qua/). Số liệu bối cảnh có nguồn: mục 1.1 của [`GIAI_THICH_DU_AN_MEDITRACE_SENTINEL.md`](../GIAI_THICH_DU_AN_MEDITRACE_SENTINEL.md). Cấu trúc mã: [`GIAI_THICH_CAU_TRUC_DU_AN.md`](GIAI_THICH_CAU_TRUC_DU_AN.md).
> Cập nhật: 28/11/2026.

**Nguyên tắc chung khi trả lời:** mỗi khi bị vặn, đừng cãi. Hãy (1) **nhận** giới hạn, (2) nói giới hạn đó **đã đo được bao nhiêu**, (3) nói **thiết kế xử lý nó thế nào**.

---

## Mục lục

- [Cấp 1 — Cơ bản: dự án là gì](#cấp-1--cơ-bản-dự-án-là-gì) (Câu 1–6)
- [Cấp 2 — Phương pháp: hệ thống hoạt động thế nào](#cấp-2--phương-pháp-hệ-thống-hoạt-động-thế-nào) (Câu 7–16)
- [Cấp 3 — Dữ liệu và đánh giá](#cấp-3--dữ-liệu-và-đánh-giá) (Câu 17–23)
- [Cấp 4 — Phản biện khó: khác biệt và sáng tạo](#cấp-4--phản-biện-khó-khác-biệt-và-sáng-tạo) (Câu 24–30)
- [Cấp 5 — Phản biện khó: giới hạn và rủi ro](#cấp-5--phản-biện-khó-giới-hạn-và-rủi-ro) (Câu 31–38)
- [Cấp 6 — Câu bẫy cần chuẩn bị trước](#cấp-6--câu-bẫy-cần-chuẩn-bị-trước) (Câu 39–45)
- [Phụ lục: các con số nên thuộc](#phụ-lục-các-con-số-nên-thuộc)

---

## Cấp 1 — Cơ bản: dự án là gì

### Câu 1. MediTrace Sentinel làm gì?

**Trả lời ngắn:** MediTrace nghe cuộc khám bằng tiếng Việt và dựng **bản nháp hồ sơ khám bệnh**, trong đó **mỗi dòng đều có bằng chứng** là câu nói gốc. Điều gì chưa chắc thì hệ thống không đoán, mà đưa vào mục **"Cần xác nhận"** để bác sĩ quyết định.

**Giải thích chi tiết:**
- Đầu vào là ghi âm (hoặc lời thoại đã chép) của cuộc khám giữa bác sĩ, người bệnh và người nhà.
- Đầu ra là bản nháp chia theo mục (bệnh sử, dị ứng, thuốc đang dùng, tiền sử gia đình…), cộng một mục "Cần xác nhận" kèm lý do cho từng dòng.
- Bác sĩ bấm vào dòng nào cũng thấy câu nói gốc và **nghe lại đúng đoạn ghi âm** đó.
- Còn mục "Cần xác nhận" thì **không ký được hồ sơ**.

**Câu chốt:** *"AI chỉ đọc hiểu, chương trình kiểm từng dòng, bác sĩ quyết định."*

---

### Câu 2. Vì sao cần giải quyết vấn đề này?

**Trả lời ngắn:** Bác sĩ quá tải và dành nhiều thời gian cho giấy tờ, dẫn tới kiệt sức và dễ sai sót. Trợ lý AI giúp được, nhưng AI viết bệnh án **vẫn bịa và bỏ sót**, nên cần một cách làm **kiểm được từng dòng**.

**Giải thích chi tiết (số liệu có nguồn, xem mục 1.1 bản giải thích toàn diện):**
- Ở Việt Nam, một bác sĩ khu vực phòng khám khám **60–100 bệnh nhân/ngày** là phổ biến (Viện Chiến lược và Chính sách Y tế). Bộ Y tế phải đặt trần **65 lượt BHYT/bàn khám/ngày**. Cả nước có **12,5 bác sĩ/10.000 dân** (2023), dưới mục tiêu 15.
- Ở Mỹ, **43,2%** bác sĩ có triệu chứng kiệt sức (AMA 2024). Bác sĩ ngoại trú dùng **5,8 giờ** trên phần mềm hồ sơ cho mỗi **8 giờ** khám.
- Ở Việt Nam chưa có số toàn quốc. Các khảo sát đơn lẻ ghi nhận **hơn 41%** bác sĩ một bệnh viện có nguy cơ kiệt sức.
- Trợ lý ghi chép AI giảm tỷ lệ kiệt sức từ **51,9% xuống 38,8%** sau 30 ngày (JAMA Network Open 2025).
- Nhưng AI viết ghi chú lâm sàng vẫn **bịa 1,47%** và **bỏ sót 3,45%** số câu (npj Digital Medicine 2025).
- WHO: khoảng **1/10** người bệnh bị tổn hại khi chăm sóc y tế; **một nửa** số tổn hại phòng tránh được liên quan đến thuốc.

**Lưu ý trung thực:** đây là số liệu bối cảnh. Dự án **chưa đo** mức giảm thời gian hay giảm kiệt sức trên bác sĩ thật.

---

### Câu 3. Bác sĩ dùng MediTrace như thế nào trong một ca khám?

**Trả lời ngắn:** Bác sĩ khám như bình thường. Sau ca khám, bác sĩ duyệt vai người nói, xem bản nháp, xử lý các mục "Cần xác nhận" rồi ký.

**Giải thích chi tiết:**
1. Bấm ghi âm và khám bình thường.
2. Hệ thống chép lời và tách người nói **tại máy**. Bác sĩ xác nhận ai là bác sĩ, ai là bệnh nhân, ai là người nhà. Chưa xác nhận xong thì **không dựng bản nháp** (dịch vụ trả lỗi 409).
3. Hệ thống dựng bản nháp và mục "Cần xác nhận", kèm **tối đa 3 câu hỏi gợi ý** để hỏi lại người bệnh ngay.
4. Với mỗi mục cần xác nhận, bác sĩ chọn **Xác nhận / Sửa / Bỏ**. Bấm vào dòng là nghe lại đoạn ghi âm.
5. Ký. Lần ký được ghi vào **nhật ký chỉ-ghi-thêm** có chuỗi băm. Sửa dù một ký tự thì phải ký lại.

**Bằng chứng:** [`DuyetBenCanh.tsx`](../web/src/components/DuyetBenCanh.tsx), [`VerificationView.tsx`](../web/src/components/VerificationView.tsx), [`kyDuyet.ts`](../web/src/lib/kyDuyet.ts), [`sign-off.ts`](../web/may-chu/routes/sign-off.ts), [`worm.ts`](../web/may-chu/worm.ts).

---

### Câu 4. MediTrace có thay thế bác sĩ, có chẩn đoán hay kê đơn không?

**Trả lời ngắn:** Không. MediTrace chỉ dựng **bản nháp** để bác sĩ duyệt. Hệ thống không chẩn đoán, không kê đơn, không tự hoàn tất hồ sơ.

**Giải thích chi tiết:**
- Bản nháp chỉ chứa những gì **đã được nói** trong buổi khám, có câu trích làm bằng chứng.
- Các công cụ như kiểm tương tác thuốc hay thang điểm nguy cơ chỉ là **gợi ý**, không thay đổi bản nháp. Bảng tri thức thuốc **chưa có chuyên gia duyệt**.
- Quyền quyết định cuối thuộc về bác sĩ, được bảo đảm bằng **khoá ký**.

---

### Câu 5. Hệ thống chạy ở đâu? Có gửi dữ liệu bệnh nhân ra internet không?

**Trả lời ngắn:** Phần lõi (chép lời, AI rút thông tin, kiểm tra, dựng bản nháp) chạy **tại máy**. Không gửi hội thoại ra ngoài.

**Giải thích chi tiết:**
- Chép lời bằng **PhoWhisper**, tách người nói bằng **pyannote**, AI rút thông tin bằng **Qwen3-4B** (nạp 4-bit). Tất cả chạy tại chỗ.
- Có một **cổng gọi AI bên ngoài** cho tính năng phụ như tra cứu y văn. Cổng này **mặc định tắt**, có hạn mức, dữ liệu được **ẩn danh** trước khi gửi, và **không bao giờ** dùng để viết bản nháp.
- Bộ khử định danh che tên, CCCD, số điện thoại, số BHYT.

**Bằng chứng:** [`src/audio/`](../src/audio/), [`llm-ngoai.ts`](../web/may-chu/routes/llm-ngoai.ts), [`an-danh.ts`](../web/may-chu/tro-ly/an-danh.ts), [`khu_dinh_danh.py`](../src/he_thong/khu_dinh_danh.py).

**Giới hạn cần biết:** bộ khử định danh chỉ che được các mẫu có cấu trúc rõ. Thử trên văn bản báo chí `PhoNER_COVID19`, nó mới che được **10/847 (1,2%)** nhãn tên và mã bệnh nhân viết tắt. Dự án đã ghi đây là điểm cần cải tiến.

---

### Câu 6. Cần phần cứng gì? Không có GPU thì sao?

**Trả lời ngắn:** Mô hình 4B nạp 4-bit, thiết kế cho GPU khoảng **12 GB** (như RTX 3060). Không có GPU vẫn **xem được demo** bằng ca mẫu.

**Giải thích chi tiết:**
- Dịch vụ hỗ trợ chế độ không mô hình, tự nhả bộ nhớ GPU khi nghỉ, và hàng đợi dựng nháp nền để bác sĩ khám tiếp người sau.
- Nút **"Xem thử với ca mẫu"** chạy 3 ca nhiều người nói mà không cần GPU.

**⚠ Chuẩn bị:** hiện tài liệu **chưa có số đo độ trễ** (mỗi ca mất bao nhiêu giây) và bộ nhớ GPU thực tế khi chạy. Nên tự đo một lần trước khi đi thi.

---

## Cấp 2 — Phương pháp: hệ thống hoạt động thế nào

### Câu 7. AI nằm ở bước nào? Các bước còn lại làm gì?

**Trả lời ngắn:** Đường ống thiết kế 8 bước (b0–b7). Luồng khám thật chạy 7 bước, b0–b6. **Chỉ bước b1 dùng AI**, các bước khác là luật cố định.

**Giải thích chi tiết:**

| Bước | Việc | AI hay luật |
|---|---|---|
| b0 | Hiểu phương ngữ, cắt đoạn, giữ nguyên lời gốc | Luật |
| **b1** | **Rút mệnh đề** kèm câu trích | **AI** (Qwen3-4B + adapter) |
| b2 | Gom người: ai nói, nói về ai | Luật |
| b3 | Đính chính, diễn biến, mâu thuẫn | Luật |
| b4 | Kiểm căn cứ K1–K7 | Luật |
| b5 | Chấm rủi ro, xếp chỗ, ghép mẫu câu | Luật |
| b6 | Gợi ý tối đa 3 câu hỏi lại | Luật |
| b7 | Trang duyệt HTML (chạy riêng; giao diện web làm thay) | — |

Sau đường ống, **lớp cảnh báo** soát lại thêm một lần (Câu 12).

**Bằng chứng:** [`chay_duong_ong.py`](../src/duong_ong/chay_duong_ong.py), [`src/duong_ong/`](../src/duong_ong/).

---

### Câu 8. "Mệnh đề" là gì? Vì sao không để AI viết thẳng bản nháp?

**Trả lời ngắn:** Mệnh đề là **một thông tin nhỏ kèm bằng chứng**. Tách ra như vậy để mỗi thông tin được **kiểm riêng, gán người riêng, sửa riêng và đo riêng**.

**Giải thích chi tiết:** Người mẹ nói một câu: *"Bản thân tôi thì bị dị ứng penicillin, còn cháu chưa thấy dị ứng gì, sốt từ 4 ngày… à không, từ chiều hôm qua."* Câu này chứa 4 thông tin, mỗi thông tin cần xử lý khác nhau:

| Thông tin | Của ai | Trạng thái | Nơi đặt |
|---|---|---|---|
| Dị ứng penicillin | Mẹ | Còn hiệu lực | Tiền sử gia đình |
| Chưa dị ứng thuốc | Bé | Còn hiệu lực | Dị ứng của bé |
| Sốt 4 ngày | Bé | Bị đính chính | Không vào hồ sơ, giữ vết |
| Sốt từ chiều qua | Bé | Còn hiệu lực | Bệnh sử |

Nếu AI viết thành một đoạn văn kiểu *"Bé sốt từ chiều qua, tiền sử dị ứng penicillin"*, cả đoạn đúng một nửa, sai một nửa, và không ai kiểm được.

Mỗi mệnh đề có các trường: nội dung, **ai nói**, **nói về ai**, **câu trích nguyên văn**, số lượt nói, mức chắc chắn, phủ định, thực tế hay giả định, thời gian, chi tiết thuốc, trạng thái.

**Bằng chứng:** [`b1_cau_truc_menh_de.py`](../src/duong_ong/b1_cau_truc_menh_de.py).

---

### Câu 9. K1–K7 là gì?

**Trả lời ngắn:** Đó là 7 câu hỏi kiểm tra mà chương trình đặt ra cho **từng mệnh đề**, bằng cách mở lại đúng câu nói gốc. Trượt câu nào nặng thì mệnh đề bị chặn khỏi bản nháp.

**Giải thích chi tiết:**

| | Kiểm gì | Ví dụ lỗi | Kết quả |
|---|---|---|---|
| K1 | Câu trích có **nguyên văn** trong lượt nói không | AI trích "sốt 3 ngày", người bệnh nói "sốt mấy hôm nay" | Chặn |
| K2 | Nội dung có khớp chữ với câu trích | Ghi "ho", câu trích nói đau đầu | Cảnh báo |
| K3 | Đúng **người** không | Ghi dị ứng cho bé, câu gốc là "bản thân tôi" của mẹ | Chặn |
| K4 | Không biến **nghi ngờ / "nếu…"** thành chắc chắn | "Nếu mai còn sốt thì chụp phim" thành "đã chụp phim" | Chặn |
| K5 | Mốc **thời gian** có trong lời nói | "Mười ngày" thành "ba tuần" | Cảnh báo |
| K6 | **Liều thuốc** có trong lời nói | Tự thêm "500 mg" | Chặn |
| K7 | Thông tin **đã bị đính chính** chưa | "250 mg… à nhầm, 500 mg" mà vẫn ghi 250 | Chặn |

"Chặn" **không phải xoá**: mệnh đề chuyển xuống "Cần xác nhận" kèm lý do bằng lời dễ hiểu.

**Bằng chứng:** [`b4_kiem_can_cu.py`](../src/duong_ong/b4_kiem_can_cu.py) (hàm `khoa_mot`). Kết quả: **0 / 30.136** dòng đáp án đúng bị chặn nhầm.

---

### Câu 10. Hệ thống quyết định đưa thông tin vào bản nháp hay vào "Cần xác nhận" thế nào?

**Trả lời ngắn:** Bằng **điểm rủi ro** và **quy tắc xếp chỗ**. Dị ứng và thuốc được đối xử chặt nhất.

**Giải thích chi tiết:**

```
điểm rủi ro = mức nghiêm trọng × độ thiếu căn cứ × hệ số cơ địa     (ngưỡng 0,5)
mức nghiêm trọng: dị ứng 1,0 · thuốc khoảng điều trị hẹp 1,0 · thuốc 0,9
                  chẩn đoán 0,8 · thời gian 0,6 · khác 0,3
hệ số cơ địa:     tăng với trẻ nhỏ, người cao tuổi, thai kỳ, suy thận, suy gan, đa thuốc
```

| Tình huống | Đi về |
|---|---|
| Qua kiểm, không cảnh báo | Thân bản nháp |
| Trượt K1–K7 | Cần xác nhận |
| **Dị ứng hoặc thuốc** có bất kỳ cảnh báo nào | Cần xác nhận |
| Thông tin khác có cảnh báo | Thân bản nháp, có đánh dấu |
| Đã bị đính chính | Không vào bản nháp, giữ vết |

Sau đó lớp cảnh báo áp **chính sách D** và có thể kéo thêm dòng sang "Cần xác nhận" (Câu 12).

**Bằng chứng:** [`b5_xep_cho_cong_rui_ro.py`](../src/duong_ong/b5_xep_cho_cong_rui_ro.py).

---

### Câu 11. Người nhà kể hộ, hoặc kể bệnh của chính họ, thì xử lý ra sao?

**Trả lời ngắn:** Mỗi mệnh đề có hai trường tách riêng: **ai nói** và **nói về ai**. Chương trình gom các cách gọi về đúng người, và K3 chặn khi câu gốc nói về người khác.

**Giải thích chi tiết:**
- Ở phòng khám Việt Nam, người nói thường **không phải** người bệnh: mẹ kể cho con, con gái kể cho bố, người ngồi cạnh xen vào.
- Bước b2 gom các cách gọi ("tôi", "mẹ tôi", "cháu nó", "ông nhà") về một người.
- Thông tin của người khác (`chu_the_id ≠ 0`) **không bao giờ** được vào mục dị ứng hay thuốc của bệnh nhân, kể cả khi xuất gói FHIR hay hồ sơ BHYT.
- Có phép thử **bịt nhãn người nói** để kiểm mô hình hiểu thật hay chỉ đoán "ai nói thì là của người đó".

**Bằng chứng:** [`b2_gom_nguoi_thuc_the.py`](../src/duong_ong/b2_gom_nguoi_thuc_the.py), [`bit_nhan.py`](../src/do_luong/bit_nhan.py). Demo: ca `demo_hai_benh_nhan` (người ngồi cạnh khai dị ứng cefuroxim của mình).

---

### Câu 12. Lớp cảnh báo làm gì? "Chính sách D" là gì?

**Trả lời ngắn:** Lớp cảnh báo là **người soát thứ hai**. Nó đối chiếu lại từng mệnh đề với lời gốc theo **56 mã lỗi** (13 nhóm), rồi chính sách D quyết định dòng nào phải chuyển sang "Cần xác nhận".

**Giải thích chi tiết:**
- Nó bắt những lỗi tinh vi: đảo có/không, sai số, nhầm trái/phải, nhầm quá khứ với hiện tại, giữ số đã bị sửa, thuốc bịa, dị ứng bịa.
- **Chống báo động tràn lan:** gộp cảnh báo trùng nguyên nhân thành một cảnh báo chính; mỗi dòng mặc định hiện tối đa 2 cảnh báo; phân 3 tầng (chặn ngay / cần xem xét / tinh lược).
- **Chính sách D** xét lần lượt: đã bị đính chính → bị thay thế; trượt K1–K7 → cần xác nhận; đang mâu thuẫn → cần xác nhận; có cảnh báo "đủ nặng" → cần xác nhận; còn lại → đã kiểm chứng.
- Chỉ bộ bắt lỗi **đã ổn định** mới được quyền đổi trạng thái. Bộ thử nghiệm chỉ hiện lên để bác sĩ lưu ý.
- Giao diện **ưu tiên** trạng thái của chính sách D, và khoá ký tính theo trạng thái này.

**Bằng chứng:** [`src/canh_bao/`](../src/canh_bao/) (`loai.py`, `gop.py`). Lỗi nguy hiểm lọt vào bản nháp: **45,9% → 11,8%**.

---

### Câu 13. Người bệnh tự sửa lời ("4 ngày… à không, hôm qua") thì sao?

**Trả lời ngắn:** Mỗi mệnh đề có **vòng đời**. Bản cũ được đánh dấu "bị thay thế", không vào hồ sơ nhưng **vẫn giữ lại để đối chiếu**.

**Giải thích chi tiết:** Hệ thống phân biệt 4 loại quan hệ giữa hai thông tin:

| Quan hệ | Ví dụ | Xử lý |
|---|---|---|
| Bổ sung | "Ho" rồi "ho có đờm" | Giữ cả hai |
| **Đính chính** | "4 ngày… à không, hôm qua" | Bản cũ thành **bị thay thế** |
| **Diễn biến** | "Hôm qua 38 độ, nay 39 độ" | Giữ cả hai theo thời gian |
| **Mâu thuẫn** | Con gái nói bố quên thuốc, bố nói vẫn uống | **Không tự chọn**, đưa bác sĩ hỏi lại |

Phân biệt "đính chính" với "diễn biến" là quan trọng về y khoa: lẫn hai loại này sẽ làm mất diễn tiến bệnh, hoặc giữ con số sai.

**Bằng chứng:** [`b3_cap_nhat_trang_thai.py`](../src/duong_ong/b3_cap_nhat_trang_thai.py). Thông tin đã bị đính chính mà vẫn còn trong bản nháp: **11,48% → 0,80%**.

---

### Câu 14. Vì sao bản nháp viết bằng mẫu câu cố định mà không để AI viết cho mượt?

**Trả lời ngắn:** Vì bước "viết lại cho mượt" chính là chỗ AI dễ **bịa thêm** nhất, và làm mất khả năng truy từng dòng về lời gốc.

**Giải thích chi tiết:** Hồ sơ y tế cần **đúng và truy được** hơn là hay. Mẫu câu chỉ ghép những mệnh đề đã qua kiểm tra, nên **không thể** sinh thêm thông tin mới. Bác sĩ vẫn sửa được câu chữ trực tiếp trên giao diện. Cái giá là câu văn kém tự nhiên hơn.

**Bằng chứng:** [`b5_viet_ban_nhap.py`](../src/duong_ong/b5_viet_ban_nhap.py).

---

### Câu 15. MediTrace làm gì để giảm ảo giác (hallucination) của mô hình?

**Trả lời ngắn:** Không cố làm AI hết bịa, mà làm cho **bịa không lọt được vào hồ sơ**, qua nhiều lớp phòng thủ.

**Giải thích chi tiết:** Mô hình ngôn ngữ sinh chữ theo cơ chế **tự hồi quy**: đoán token kế tiếp theo xác suất. Nó chọn cái **nghe hợp lý**, không phải cái **đúng sự thật**. MediTrace xử lý ở hai mặt:

**Về hình dạng:**
- **Giải mã có ràng buộc** (constrained decoding): ở mỗi bước sinh, logit của token làm sai lược đồ JSON bị đặt về −∞, tức xác suất bằng 0, nên mô hình chỉ điền được vào đúng các ô quy định. Ví dụ ô "ai nói" chỉ được chọn *bác sĩ / bệnh nhân / người nhà / điều dưỡng*. Kết quả: **0/30 ca lỗi JSON**.
- **Giải mã tham lam** và **tắt chế độ suy nghĩ**: kết quả tất định, chạy lại vẫn ra như cũ.

**Về nội dung:**
- **Thu hẹp tác vụ:** chỉ trích xuất mệnh đề, không viết đoạn văn.
- **Neo bằng chứng:** mỗi mệnh đề bắt buộc kèm câu trích nguyên văn và số lượt nói.
- **Huấn luyện** trên dữ liệu có 52.634/52.634 câu trích nguyên văn, để mô hình quen chép đúng chữ.
- **Kiểm chứng tất định sau sinh** K1–K7 và lớp cảnh báo.
- **Sinh văn bản theo khuôn mẫu** ở bước cuối.
- **Từ chối có chọn lọc + con người trong vòng lặp:** không chắc thì thành câu hỏi, chưa xử lý thì chưa ký.

**Lưu ý quan trọng:** giải mã có ràng buộc chỉ bảo đảm **đúng hình dạng**, không bảo đảm **đúng sự thật**. Trong ô viết tự do (câu trích, liều), mô hình vẫn có thể bịa. Đó là lý do cần K1–K7.

**Bằng chứng:** bộ ép JSON đang chạy là `_ep_json` trong [`chon_mo_hinh_bakeoff.py`](../src/huan_luyen/chon_mo_hinh_bakeoff.py) (thư viện lm-format-enforcer). Cấy lỗi bịa mệnh đề, bịa trích dẫn, đổi bằng chứng trên tập giữ kín: bắt được **100%**. Thử trên ViMQ: **272/276** câu trích là nguyên văn, 4 câu sai bị K1 chặn.

---

### Câu 16. Khi không chắc, hệ thống có gợi ý gì cho bác sĩ không?

**Trả lời ngắn:** Có. Hệ thống chọn **tối đa 3 câu hỏi** giải quyết được nhiều rủi ro nhất để bác sĩ hỏi lại ngay trong buổi khám.

**Giải thích chi tiết:** Ví dụ còn mơ hồ "ai bị dị ứng penicillin" và "thuốc 'vỉ a móc' là thuốc gì", thì hệ thống gợi ý hai câu hỏi nhắm thẳng vào hai điểm đó. Hỏi ít mà gỡ được nhiều, phù hợp với lượt khám chỉ vài phút.

**Bằng chứng:** [`b6_goi_y_hoi_lai.py`](../src/duong_ong/b6_goi_y_hoi_lai.py).

---

## Cấp 3 — Dữ liệu và đánh giá

### Câu 17. Dữ liệu lấy từ đâu? Vì sao dùng dữ liệu mô phỏng?

**Trả lời ngắn:** Dự án tự sinh **5.000 cuộc khám mô phỏng** từ **657 khuôn bệnh** thuộc 21 hệ cơ quan, vì hội thoại khám thật có thông tin định danh, muốn dùng phải xin phép đạo đức.

**Giải thích chi tiết:**
- Dữ liệu sinh **bằng luật có hạt giống cố định**, không nhờ ChatGPT viết. Lý do: hội thoại do mô hình lớn viết thường quá "sạch", đủ chủ ngữ, làm mất đúng các hiện tượng khó nhất trong tiếng Việt là **lược chủ ngữ** và **đại từ họ hàng đa nghĩa**.
- Đáp án có cấu trúc (của ai, đính chính ở đâu, bằng chứng ở lượt nào) được gán ngay lúc sinh. **100%** câu trích (52.634/52.634) là nguyên văn.
- 200 khuôn gốc đã duyệt; **457 khuôn mở rộng chưa có bác sĩ duyệt**, được gắn nhãn minh bạch.
- Có thêm **300 ca thử thách theo cặp**: mỗi cặp chỉ khác **một điểm** (đổi người mang dị ứng, tự sửa, lỗi chép giọng nói, phương ngữ).

**Bằng chứng:** [`sinh_hoi_thoai_viet.py`](../src/bo_du_lieu/sinh_hoi_thoai_viet.py), [`kho_khuon.py`](../src/bo_du_lieu/kho_khuon.py), [`HO_SO_DU_LIEU_DATASHEET.md`](HO_SO_DU_LIEU_DATASHEET.md).

---

### Câu 18. Làm sao chắc tập huấn luyện và tập kiểm tra không trùng nhau?

**Trả lời ngắn:** Chia tập **theo khuôn bệnh**, không chia ngẫu nhiên. Một bệnh chỉ nằm ở một tập: **515** khuôn huấn luyện, **72** phát triển, **70** kiểm tra, **0** khuôn giao nhau.

**Giải thích chi tiết:**
- Độ giống từ khoá triệu chứng giữa train và test trung bình chỉ **5,87%** (Jaccard), phân vị 95 là 11,72%.
- Mã **chặn việc chạm vào tập kiểm tra cuối** trong lúc phát triển.
- Mỗi bộ dữ liệu có "vân tay" (hạt giống, commit, băm nội dung) để phát hiện nhầm bộ.
- Thêm **10 kịch bản bệnh hiếm hoàn toàn ngoài kho** (Guillain-Barré, Wilson, Brugada…).

**Bằng chứng:** [`chia_tap_theo_khuon.py`](../src/bo_du_lieu/chia_tap_theo_khuon.py), [`kiem_nghiem_ngoai_khuon.py`](../src/do_luong/kiem_nghiem_ngoai_khuon.py), [`data/manifest_v2_mo_rong_5000.json`](../data/manifest_v2_mo_rong_5000.json).

---

### Câu 19. Vì sao không dùng ROUGE như các bài tóm tắt khác? Thước đo của dự án là gì?

**Trả lời ngắn:** ROUGE chỉ **đếm chữ trùng**. Ghi dị ứng của mẹ sang con vẫn được **100% điểm**. Dự án làm **thước đo quy gán**, chấm theo **"cái gì"** và **"của ai"**.

**Giải thích chi tiết:**
- Thử đổi chỗ bệnh nhân với người nhà: ROUGE-1 vẫn **1,0000**, Section F1 vẫn **1,0000** ở **271/271** cặp, tức không phát hiện được gì. Thước đo quy gán **giảm 0,138**, tức phát hiện được.
- Cách chấm: (1) tách mỗi bản ghi thành mệnh đề gồm **chủ thể** và **tập từ nội dung**; (2) ghép hai bên theo nội dung trước; (3) trong các cặp khớp nội dung, kiểm chủ thể. Kết quả phân biệt được ba loại lỗi: **sai người**, **bịa** và **bỏ sót**.
- Hai luật cứng: lệch **phủ định** ("không dị ứng" khác "dị ứng") và lệch **con số** ("3 ngày" khác "5 ngày") thì không bao giờ coi là cùng nội dung.
- Thước đo được **kiểm trên bệnh án thật**: đủ nhạy với lỗi đổi người, nhưng không phạt nặng việc đổi từ đồng nghĩa.

**Bằng chứng:** [`thuoc_do_quy_gan.py`](../src/do_luong/thuoc_do_quy_gan.py), [`chung_chi_thuoc_do.py`](../src/do_luong/chung_chi_thuoc_do.py).

**Nếu bị hỏi vặn "tự đặt thước đo rồi tự chấm có thiên vị không?":** có nguy cơ đó, nên dự án kiểm thước đo trên bệnh án thật trước khi dùng, ghi rõ khi nào **không được** dùng nó (không dùng một mình để so văn xuôi với bản sinh theo luật), và công bố cả kết quả bất lợi.

---

### Câu 20. Kết quả chính là gì?

**Trả lời ngắn:** Bỏ sót giảm từ **43,1% xuống 11,5%**; thông tin đã bị đính chính mà còn sót lại giảm từ **11,48% xuống 0,80%**; lỗi nguy hiểm lọt vào bản nháp giảm từ **45,9% xuống 11,8%**.

**Giải thích chi tiết:**

| Kết quả | Trước | Sau | Điều kiện đo |
|---|---|---|---|
| Bỏ sót mệnh đề | 43,1% (chưa huấn luyện) | **11,5%** (khoảng tin cậy 8,4–15,6%) | 30 ca phát triển, 304 mệnh đề |
| Đính chính còn sót lại | 11,48% | **0,80%** | Bộ thử thách "tự sửa" |
| F1 bộ "đổi người" | 66,1% | **70,8%** | Thêm các bước kiểm |
| Lỗi nguy hiểm lọt vào bản nháp | 45,9% (chính sách C) | **11,8%** (chính sách D), chặn 88,2% | 300 ca thử thách phát triển |
| Câu đúng bị chặn nhầm | 8,0% | 10,0% | Như trên (cái giá phải trả) |
| Lớp cảnh báo bắt lỗi cài sẵn | — | **0,871** | Tập giữ kín 240 ca, chạy một lần |
| Câu đúng bị kiểm căn cứ chặn oan | — | **0 / 30.136** | Đáp án hoàn hảo |

---

### Câu 21. Các con số đó có lạc quan không? Đo trên tập nào?

**Trả lời ngắn:** Có. Con số 88,2% đo trên **tập phát triển đã dùng để viết luật**, nên là cận lạc quan. Con số sạch hơn là **0,871** trên tập giữ kín chỉ chạy một lần.

**Giải thích chi tiết:**
- Các luật của lớp cảnh báo được sửa qua nhiều vòng trên 4 bộ thử thách phát triển. Đo lại trên chính các bộ đó thì số tốt hơn thực tế.
- Để chống điều này, dự án **đăng ký trước** tiêu chí và ngưỡng ([`dang-ky-truoc-bo-luat.md`](dang-ky-truoc-bo-luat.md)), rồi chạy tập giữ kín **đúng một lần**: kết quả 0,871, bằng với tập điều chỉnh.
- Một số luật của vòng 6 chưa chạy lại trên tập giữ kín, nên con số 0,889 cho lỗi khó cũng là cận lạc quan.
- Mọi con số đều **so với bộ chấm tự động**, chưa có nhãn của người.

**Nên tự nói điều này trước khi bị hỏi.**

---

### Câu 22. Huấn luyện mô hình thế nào? Các bản sau có tốt hơn không?

**Trả lời ngắn:** Tinh chỉnh **Qwen3-4B bằng QLoRA** cho riêng bước rút mệnh đề. Bản v3 **không tốt hơn** bản v1, và thử DPO **chưa đủ điều kiện** đưa vào hệ thống.

**Giải thích chi tiết:**
- Huấn luyện có giám sát trên dữ liệu rút mệnh đề, nạp 4-bit, tính loss theo đoạn để hạ đỉnh bộ nhớ GPU, chạy trên GPU Kaggle.
- Chọn mô hình bằng **so sánh số đo** trên tập phát triển, không chọn theo cảm tính.
- **v3** (huấn luyện trên dữ liệu v2) bỏ sót 14,1% so với 11,8% của v1. Hai khoảng tin cậy chồng nhau, nên chưa nói được bản nào hơn.
- **DPO** trên 407 cặp lỗi khó làm tăng khoảng cách giữa câu đúng và câu sai, nhưng làm giảm xác suất của câu đúng, nên chưa dùng.

**Thông điệp:** *quyết định dựa trên số đo, không dựa vào việc đã tốn công làm.*

**Bằng chứng:** [`huan_luyen_sft.py`](../src/huan_luyen/huan_luyen_sft.py), [`chon_mo_hinh_bakeoff.py`](../src/huan_luyen/chon_mo_hinh_bakeoff.py), [`dpo-v3.md`](ket-qua/dpo-v3.md).

---

### Câu 23. Làm sao chứng minh mỗi bước thật sự có đóng góp?

**Trả lời ngắn:** Bằng **thí nghiệm bỏ từng thành phần**: các nhánh A, B, C, C_khoa, D, E **dùng chung một đầu ra mô hình**, chỉ khác nhau ở các bước luật được bật hay tắt.

**Giải thích chi tiết:**
- Vì cùng một đầu ra AI, chênh lệch giữa các nhánh chỉ đến từ các bước luật, không lẫn với độ ngẫu nhiên của mô hình.
- Ví dụ: chênh lệch giữa **C_khoa** và **C** chính là đóng góp riêng của tầng kiểm căn cứ.
- Có khoảng tin cậy bootstrap theo ca và theo khuôn bệnh để biết chênh lệch có vượt mức nhiễu không.
- Có đối chứng "đường tắt": chủ thể luôn là người nói, chủ thể luôn là bệnh nhân. Hệ thống thật phải hơn cả hai thì mới có ý nghĩa.

**Bằng chứng:** [`chay_duong_ong.py`](../src/duong_ong/chay_duong_ong.py), [`do_dac.py`](../src/do_luong/do_dac.py), [`khoang_tin_cay.py`](../src/do_luong/khoang_tin_cay.py), [`doi_chung_tam_thuong.py`](../src/do_luong/doi_chung_tam_thuong.py).

---

## Cấp 4 — Phản biện khó: khác biệt và sáng tạo

### Câu 24. Khác gì so với nhờ ChatGPT tóm tắt cuộc khám?

**Trả lời ngắn:** ChatGPT **được yêu cầu** trích dẫn. MediTrace **kiểm lại** từng câu trích bằng chương trình. Chỗ khác nhau nằm ở chữ **bảo đảm**.

**Giải thích chi tiết:**

| | ChatGPT được yêu cầu trích dẫn | MediTrace |
|---|---|---|
| Ai kiểm câu trích? | Không ai | Chương trình so với lời gốc |
| Câu trích bịa | Lọt vào hồ sơ | Bị chặn (K1), kết quả tất định |
| Câu trích thật nhưng của người nhà | Lọt | Bị chặn (K3) |
| Câu trích thật nhưng đã bị đính chính | Lọt | Bị chặn (K7) |
| Liều thuốc không ai nói | Lọt | Bị chặn (K6) |
| Thông tin không chắc | Mô hình tự đoán, văn vẫn mượt | Thành mục "Cần xác nhận" có lý do |
| Dữ liệu bệnh nhân | Gửi ra máy chủ bên ngoài | Xử lý tại máy |

**Nếu bị hỏi vặn "bảo ChatGPT trích dẫn thì cũng được mà?":** bảo nó trích dẫn mới là **dặn**, chưa phải **kiểm**. Mô hình có thể bịa câu trích nghe rất hợp lý, hoặc trích đúng câu thật nhưng của người khác. Không có bước kiểm thì không ai biết.

---

### Câu 25. Vậy lấy ChatGPT thay mô hình của bạn, giữ bộ kiểm, chẳng phải tốt hơn sao?

**Trả lời ngắn:** **Đồng ý**, và đó chính là điểm sáng tạo: một **lớp kiểm độc lập với mô hình**. Dự án chọn mô hình nhỏ chạy tại chỗ vì **quyền riêng tư** và **khả năng chạy không cần mạng**.

**Giải thích chi tiết:**
- Bộ kiểm K1–K7, trạng thái mệnh đề, cổng rủi ro và lớp cảnh báo không phụ thuộc mô hình nào. Đó là phần khó làm và đáng giá, và vẫn là của dự án dù thay mô hình.
- Dữ liệu sức khỏe là **dữ liệu cá nhân nhạy cảm**. Từ 01/01/2026, khung pháp lý là Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP (thay Nghị định 13/2023/NĐ-CP). Dự án không khẳng định việc dùng dịch vụ đám mây là vi phạm; dự án chạy tại chỗ nên dữ liệu người bệnh không cần rời phòng khám.
- Bệnh viện tuyến dưới có thể mất mạng.
- Cổng gọi mô hình ngoài đã có sẵn trong hệ thống nếu bệnh viện muốn dùng cho việc phụ, nhưng mặc định tắt.

---

### Câu 26. Mô hình thương mại lớn có gán đúng người tốt hơn mô hình của bạn không?

**Trả lời ngắn:** **Có**, và dự án công bố điều đó. Điểm mạnh của MediTrace không phải mô hình giỏi hơn, mà là **kiểm được từng dòng** và **chạy tại chỗ**.

**Giải thích chi tiết:**
- Ở bộ "tự sửa", mô hình thương mại lớn gán nhầm người **1,4%**, mô hình của dự án **7,6%**.
- Cách để mô hình viết thẳng bản nháp ghi đúng người **97,1%**, MediTrace **88,3%**.
- README ghi rõ: dự án **không** khẳng định chính xác hơn. Đừng nói ngược với README.
- Vì độ đúng người 88,3% chưa đủ cho hồ sơ y tế, mọi mệnh đề có chủ thể không rõ đều bị đưa vào "Cần xác nhận", không tự điền.

---

### Câu 27. Phần nào là sáng tạo, phần nào là ghép đồ có sẵn?

**Trả lời ngắn:** Mô hình, LoRA, ý tưởng trích dẫn nguồn, luật kiểu ConText là **có sẵn**. Cái mới nằm ở **cách ghép** và ở **phần dành riêng cho tiếng Việt lâm sàng**.

**Giải thích chi tiết:**
1. **Không mới, nói thẳng:** Qwen3, QLoRA, giải mã có ràng buộc, ý tưởng trích dẫn nguồn, luật ConText.
2. **Mới ở cách ghép:**
   - AI chỉ rút mệnh đề; chương trình **chứng minh** từng mệnh đề bằng lời gốc.
   - Mệnh đề có **vòng đời**: đính chính, diễn biến, mâu thuẫn.
   - Không chắc thì thành **câu hỏi có lý do**, kèm **khoá ký**.
3. **Mới ở nội dung cho tiếng Việt:**
   - Tách "ai nói" khỏi "nói về ai" trong bối cảnh người nhà kể hộ và câu lược chủ ngữ.
   - Hiểu phương ngữ mà vẫn giữ nguyên văn để trích dẫn.
4. **Mới ở phương pháp đánh giá:** thước đo quy gán thấy được lỗi mà ROUGE bỏ qua; bộ thử thách theo cặp; cấy lỗi có đăng ký trước; bịt nhãn người nói.

> *"Chúng tôi không làm một AI viết hay hơn. Chúng tôi làm cho mỗi dòng AI đưa ra đều phải có bằng chứng, và khi không có thì nó phải hỏi."*

---

### Câu 28. Dùng luật là cách làm cũ. Sáng tạo ở đâu?

**Trả lời ngắn:** Sáng tạo nằm ở **việc đặt luật vào đúng chỗ**: AI làm phần **hiểu**, luật làm phần **bảo đảm**.

**Giải thích chi tiết:**
- Luật kém ở việc hiểu ngôn ngữ, nên phần đó giao cho AI.
- AI kém ở việc bảo đảm, nên phần đó giao cho luật.
- Trong y tế, luật có ba thứ AI không có: **đọc được, kiểm được, giải thích được**. Mỗi lần chặn đều có mã lý do bằng chữ. Khi có sự cố y khoa, người ta truy được vì sao dòng đó vào hồ sơ.
- Cách gọi chuyên môn: kiến trúc **lai nơ-ron – ký hiệu** (neuro-symbolic).

---

### Câu 29. Các sản phẩm như Abridge hay Nuance DAX cũng nối câu trong bản nháp về hội thoại gốc. Bạn khác gì?

**Trả lời ngắn:** Đừng nói "chưa ai làm truy vết". Khác biệt là MediTrace **chặn** dòng không chứng minh được, chứ không chỉ **hiển thị** nguồn; cộng với phần tiếng Việt và chạy tại chỗ.

**Giải thích chi tiết:**
- Hiển thị nguồn giúp bác sĩ tự kiểm. MediTrace để **chương trình kiểm trước**, rồi chỉ đưa cho bác sĩ phần cần xem.
- Có **khoá ký** buộc xử lý mục chưa chắc.
- Xử lý riêng các hiện tượng của tiếng Việt: lược chủ ngữ, người nhà kể hộ, phương ngữ, tên thuốc dân gian.

**Lưu ý:** không nắm chắc chi tiết bên trong các sản phẩm đó. Nên đọc tài liệu công khai của họ trước khi so sánh trực tiếp.

---

### Câu 30. Nếu các hãng lớn thêm tính năng kiểm tra trích dẫn thì lợi thế của bạn còn gì?

**Trả lời ngắn:** Lợi thế nằm ở **phần tiếng Việt lâm sàng** và ở **chạy tại chỗ**, không nằm ở ý tưởng chung.

**Giải thích chi tiết:** Bộ luật tiếng Việt (người nhà kể hộ, lược chủ ngữ, phương ngữ ba miền, tên thuốc dân gian), bộ dữ liệu 657 khuôn có đáp án quy gán, bộ thước đo và bộ thử thách, cùng việc tích hợp BHYT XML và Dược thư Quốc gia. Đó là những thứ cần thời gian xây và phải hiểu bối cảnh Việt Nam.

---

## Cấp 5 — Phản biện khó: giới hạn và rủi ro

### Câu 31. Dữ liệu tự sinh bằng luật, mô hình học theo luật đó, rồi bạn chấm bằng luật của mình. Đó có phải vòng tròn không?

**Trả lời ngắn:** Có nguy cơ đó, và dự án đã làm 4 việc để giảm nó. Nhưng phải nhận: kết quả hiện **chỉ có hiệu lực trên dữ liệu mô phỏng**.

**Giải thích chi tiết:**
1. **Chia tập theo khuôn bệnh**, mã chặn việc chạm vào tập kiểm tra.
2. **10 kịch bản hoàn toàn ngoài kho**, đúng chủ thể 52/52. *Lưu ý: phép thử này đo phần luật trên mệnh đề chuẩn, không đo bước AI.*
3. **Dữ liệu từ nguồn khác:** ViMQ (câu hỏi thật của người bệnh), VietMed, bộ 500 hội thoại do GPT sinh (chỉ dùng để đo), bộ hội thoại người thật ghi tay, và 5 bộ dữ liệu tiếng Việt công khai.
4. **Thước đo được kiểm trên bệnh án thật.**

**Phải nhận:** đáp án mô phỏng gần như chép nguyên văn lời thoại. Bước tiếp theo là thử trên hội thoại thật đã khử định danh, có bác sĩ gán nhãn.

---

### Câu 32. Bộ kiểm của bạn bảo đảm được những gì, và không bảo đảm được những gì?

**Trả lời ngắn:** **K1 bảo đảm chắc chắn** câu trích có thật. Các phép kiểm còn lại là luật theo từ, nên **chỉ bắt được một phần**.

**Giải thích chi tiết:**

| Bảo đảm chắc chắn (so chuỗi) | Chỉ kiểm một phần (luật theo từ) |
|---|---|
| Câu trích có nguyên văn trong hội thoại | Nội dung có diễn đạt đúng câu trích không: K2 chỉ kiểm **có trùng từ**, nên "trích đúng nhưng hiểu sai" có thể chỉ bị cảnh báo |
| Liều thuốc có xuất hiện trong lượt dẫn | Chủ thể: khi đoạn trích không có từ chỉ người, chương trình chỉ suy từ người nói, nên chỉ cảnh báo |
| Thông tin đã bị đính chính không vào bản nháp | Mức chắc chắn và câu điều kiện bắt bằng danh sách từ. Cách nói ngoài danh sách thì lọt |

> *"Phần kiểm bằng so chuỗi thì chắc chắn. Phần kiểm bằng luật thì chúng tôi đo và công bố tỷ lệ lọt."*

---

### Câu 33. Kiểm chặt như vậy có làm mất thông tin đúng không?

**Trả lời ngắn:** Có. Bỏ sót tăng từ **4,5% lên 7,7%** ở bộ "đổi người", và câu đúng bị chặn nhầm khoảng **10%**. Đây là đánh đổi có chủ ý.

**Giải thích chi tiết:**
- Lý lẽ y khoa: một dòng **sai** trong hồ sơ nguy hiểm hơn một dòng **thiếu**. Thiếu thì bác sĩ còn hỏi lại được; sai thì có thể dẫn tới kê thuốc sai.
- Thông tin bị chặn **không mất**: nó nằm ở "Cần xác nhận", bác sĩ xác nhận trong vài giây.
- Ngưỡng được chọn trên **đường đánh đổi** giữa lỗi và bỏ sót, không chọn tuỳ ý.
- Bộ dò bỏ sót bằng luật còn yếu: mới chạm đúng **12,5%** chỗ sót. Bỏ sót chủ yếu được giảm nhờ huấn luyện mô hình.

**Bằng chứng:** [`duong_danh_doi.py`](../src/do_luong/duong_danh_doi.py), [`canh-bao-moc-0.md`](ket-qua/canh-bao-moc-0.md).

---

### Câu 34. Bác sĩ bận sẽ bấm "đồng ý" hết. Khoá ký có tác dụng gì?

**Trả lời ngắn:** Khoá ký buộc bác sĩ **bấm**, chưa buộc được bác sĩ **đọc**. Hệ thống giảm nguy cơ này bằng cách **chỉ đưa ra ít mục, xếp theo mức nguy hiểm, kèm lý do và nút nghe lại**.

**Giải thích chi tiết:**
- Hiện tượng này gọi là **thiên kiến tin máy** (automation bias).
- Mỗi lần xác nhận được ghi vào nhật ký WORM, nên biết ai đã xác nhận mục nào.
- **Phải nhận:** muốn biết bác sĩ có đọc thật không thì cần nghiên cứu sử dụng thật. Việc này chưa làm.

---

### Câu 35. Có báo động giả nhiều không? Bác sĩ có bị "nhờn" cảnh báo không?

**Trả lời ngắn:** Có. Trên bản ghi **không có lỗi**, lớp cảnh báo vẫn đưa ra khoảng **7–8 cảnh báo mỗi ca**. Dự án giảm phần bác sĩ thực sự nhìn thấy bằng gộp cảnh báo, ngân sách hiển thị và phân tầng.

**Giải thích chi tiết:**
- Gộp các cảnh báo cùng nguyên nhân thành một; mỗi dòng mặc định hiện tối đa 2; nhiễu giá trị thấp được tinh lược khỏi luồng chính.
- Các mã có độ chính xác thấp (ví dụ một mã chỉ đúng 5,8%) bị hạ xuống thành **gợi ý**, không được đổi trạng thái.
- Số cảnh báo trên bản sạch đã giảm từ 8,98 xuống 7,11 mỗi ca, nhưng vẫn là điểm đang cải tiến.

---

### Câu 36. Máy chép giọng nói nghe nhầm tên thuốc thì sao?

**Trả lời ngắn:** Lỗi chép lời xảy ra **trước** bước AI, nên K1 không bắt được: câu trích vẫn "có thật" trong bản chép sai. Hệ thống xử lý bằng **so hai bộ chép**, **bác sĩ duyệt lời thoại**, và **cảnh báo chép âm**.

**Giải thích chi tiết:**
- Chạy hai bộ chép (PhoWhisper, faster-whisper) và đánh dấu chỗ hai bên bất đồng ở từ quan trọng: thuốc, liều, phủ định.
- Có bảng biến thể phát âm tên thuốc để **gợi ý đối chiếu**, không tự sửa đè chữ gốc.
- Tên thuốc dân gian như "vỉ a móc" bị K6 giữ lại ở "Cần xác nhận" để bác sĩ kiểm vỉ thuốc thật.
- **Phải nhận:** bộ nhiễu chép âm là bộ có tỷ lệ chặn lỗi nguy hiểm **thấp nhất (74,6%)**.

**Bằng chứng:** [`disagreement.py`](../src/audio/asr/disagreement.py), [`canh_bao/asr.py`](../src/canh_bao/asr.py).

---

### Câu 37. Khi AI sai, ai chịu trách nhiệm?

**Trả lời ngắn:** Bác sĩ ký hồ sơ, như hiện nay. Hệ thống được thiết kế để bác sĩ **có đủ bằng chứng** khi ký.

**Giải thích chi tiết:** Mỗi dòng truy được về câu nói gốc; mỗi lần chặn có lý do; mỗi lần ký và xác nhận được ghi vào nhật ký chỉ-ghi-thêm có chuỗi băm. Khi có sự cố, truy được dòng đó đến từ đâu, ai đã xác nhận, và hệ thống đã cảnh báo gì.

---

### Câu 38. Lỗi chưa giải quyết được là gì?

**Trả lời ngắn:** Dự án liệt kê công khai **7 nhóm lỗi chưa phát hiện được bằng luật**, cùng các giới hạn đã đo.

**Giải thích chi tiết:**
- 7 nhóm lỗi ngữ nghĩa sâu, ví dụ hiểu đại từ qua nhiều lượt nói, hay suy luận ngầm ý (`CHUA_PHAT_HIEN` trong [`loai.py`](../src/canh_bao/loai.py)).
- Bỏ sót do mô hình (11,5%), và bộ dò bỏ sót bằng luật còn yếu.
- Chưa thử trên hội thoại bệnh nhân thật; chưa đo trên bác sĩ thật.
- 457 khuôn mở rộng và bảng tri thức thuốc chưa có chuyên gia duyệt.
- Bộ khử định danh yếu với tên viết tắt không theo mẫu.

---

## Cấp 6 — Câu bẫy cần chuẩn bị trước

### Câu 39. "Đường ống có 7 bước hay 8 bước?"

**Trả lời:** *"Thiết kế 8 bước, b0 đến b7. Bản đang chạy dùng 7 bước, từ b0 đến b6; màn hình duyệt do giao diện web đảm nhận. Một số tệp trong thư mục là nhánh thử nghiệm để so sánh, chưa đưa vào luồng chính."*

Các tệp chỉ dùng ở nhánh thử nghiệm: `b2_bu_chu_ngu_tinh_luoc`, `b3_phan_xu_quan_he`, `b3_sinh_cap_ung_vien_quan_he`, `b4_kiem_day_du`, `b6_sua_cuc_bo`, `b5_diem_rui_ro_quy_gan`.

---

### Câu 40. "Phép thử 10 bệnh ngoài khuôn đạt 100% đo trên hệ thống nào?"

**Trả lời:** Phép thử này đo **phần luật** (gom người, khoá căn cứ, xử lý đính chính) trên **mệnh đề chuẩn** của kịch bản mới, **không đo bước AI**. Nó dùng bộ xử lý trong `b2_bu_chu_ngu_tinh_luoc.py`, là thành phần của nhánh thử nghiệm `C_khoa_v2`, không phải nhánh dịch vụ `C_khoa_hoi`. Đừng trình bày con số này như "AI đúng 100%".

---

### Câu 41. "Ngữ pháp GBNF và cây chuỗi con trong `b1_ep_dau_ra_json.py` có chạy thật không?"

**Trả lời:** Hiện **chưa**. Luồng thật ép JSON bằng thư viện **lm-format-enforcer** (`_ep_json` trong [`chon_mo_hinh_bakeoff.py`](../src/huan_luyen/chon_mo_hinh_bakeoff.py)). GBNF viết sẵn cho llama.cpp; cây chuỗi con hiện chỉ dùng để **kiểm sau**, chưa dùng để **ép trong lúc sinh**. Chú thích đầu tệp ghi "loại trừ hoàn toàn ảo giác trích dẫn" là **chưa đúng với luồng đang chạy**, nên đừng dùng câu đó. Nếu được hỏi hướng cải tiến, có thể nói: nối cây chuỗi con vào lúc sinh thì mô hình sẽ **không thể** bịa câu trích ngay từ đầu.

---

### Câu 42. "Chốt 7 trong báo cáo là gì?"

**Trả lời:** Trong mã, **Chốt 7 là "Hiệu chỉnh liều theo chức năng thận/gan và tờ dặn dò người bệnh"** ([`dieu_phoi_cac_chot_an_toan.py`](../src/he_thong/dieu_phoi_cac_chot_an_toan.py)). Một số bản báo cáo cũ từng mô tả Chốt 7 là "chặn kê NSAID trên nền suy tim" và gán cho tệp sinh dữ liệu đa bệnh lý. Mô tả đó **không khớp với mã** và đã được sửa ngày 28/11/2026. Nếu giám khảo cầm bản cũ, hãy nói thẳng là mô tả cũ bị nhầm và đã sửa.

---

### Câu 43. "Bảng tri thức thuốc ai duyệt?"

**Trả lời:** **Chưa có chuyên gia duyệt** (cờ `da_duyet = false` trong `data/tri_thuc_thuoc.json`). Vì vậy các cảnh báo kiến thức thuốc được đánh dấu **thử nghiệm**, chỉ nhắc bác sĩ, và các công cụ lâm sàng chỉ là gợi ý, không đổi bản nháp.

---

### Câu 44. "Lỗi nguy hiểm lọt qua là 42,9%, 24,1%, 6,4% hay 11,8%?"

**Trả lời:** **11,8% (26/220)** là số hiện tại, đo lại ngày 28/11/2026 trên mã đang chạy; hai phép đo độc lập ([`canh-bao.json`](ket-qua/canh-bao.json), [`truyen-lan-loi-tung-tang.json`](ket-qua/truyen-lan-loi-tung-tang.json)) cho cùng kết quả. Các số 42,9% và 24,1% là của bộ luật các vòng trước. Con số 6,4% là bản cũ chưa chạy lại sau khi siết luật. Nếu giám khảo cầm bản nộp ngày 26/11, giải thích rằng số đã được đo lại.

---

### Câu 45. "Bạn có dùng AI để viết mã không?"

**Trả lời:** Có, và dự án **công khai** điều đó: có bảng khai tệp nào do AI hỗ trợ viết, sửa mấy lần, theo lời nhắc nào ([`khai_ma_nguon.py`](../src/he_thong/khai_ma_nguon.py), [`nhat_ky_loi_nhac.py`](../src/he_thong/nhat_ky_loi_nhac.py)). Đừng phủ nhận. Nhấn mạnh rằng mọi con số đều do mã trong kho in ra, có kiểm thử tự động (hơn 1.950 test Python, 96 test web) và có thể chạy lại.

---

## Phụ lục: các con số nên thuộc

| Nhóm | Con số |
|---|---|
| **Bối cảnh** (nguồn ngoài) | 43,2% bác sĩ Mỹ kiệt sức (AMA 2024) · 5,8 giờ hồ sơ / 8 giờ khám · trợ lý ghi chép AI giảm kiệt sức 51,9% → 38,8% · AI viết ghi chú bịa 1,47%, bỏ sót 3,45% · 1/10 người bệnh bị tổn hại khi chăm sóc (WHO) · 12,5 bác sĩ/10.000 dân ở Việt Nam |
| **Dữ liệu** | 5.000 ca · 657 khuôn, 21 hệ cơ quan · 515/72/70 khuôn train/dev/test, 0 giao nhau · 100% câu trích nguyên văn · lặp câu 76,92% → 47,37% |
| **Bước AI** | Bỏ sót 43,1% → 11,5% · 0/30 lỗi JSON · ViMQ: 272/276 câu trích nguyên văn |
| **Kiểm và chặn** | 7 phép kiểm K1–K7 · 0/30.136 chặn oan · đính chính còn sót 11,48% → 0,80% · lỗi nguy hiểm lọt 45,9% → 11,8% (chặn 88,2%) · chặn nhầm 8,0% → 10,0% |
| **Lớp cảnh báo** | 13 nhóm, 56 mã · bắt lỗi cài sẵn 0,871 trên tập giữ kín · 7–8 cảnh báo trên bản sạch mỗi ca |
| **Đánh đổi** | Bỏ sót 4,5% → 7,7% ở bộ "đổi người" · mô hình thương mại gán nhầm người 1,4% so với 7,6% |
| **Kiểm thử** | Hơn 1.950 test Python · 96/96 test web |
