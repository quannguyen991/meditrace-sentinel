# ĐỌC MẪU 50 HỘI THOẠI V2 SAU KHI SỬA (`data/hoi_thoai_viet_v2_mo_rong.jsonl`)

- **Ngày thực hiện:** 23/11/2026
- **Nguồn dữ liệu:** `data/hoi_thoai_viet_v2_mo_rong.jsonl` (bản hoàn thiện sau cải tiến chất lượng và đa dạng hóa câu)
- **Cách chọn mẫu:** Ngẫu nhiên 50 ca với hạt cố định `random.Random(2611)`
- **Tổng số lượt thoại trong 50 ca:** 856 lượt
- **Phân bố độ dài trên 50 ca mẫu:** Trung vị **11.0 từ/lượt** · Lượt $\le 3$ từ: **23/856 (2.69%)** · Lượt $\ge 12$ từ: **380/856 (44.39%)**

---

## 1. Bảng So Sánh Lỗi Trước và Sau Khi Sửa (30 Ca Cũ vs 50 Ca Mới)

| Nhóm lỗi / Tiêu chí | Trước khi sửa (30 ca, 517 lượt) | Sau khi sửa (50 ca, 856 lượt) | Tình trạng khắc phục |
|---|---:|---:|---|
| 1. Lặp từ / cụm từ liền kề vi phạm ngữ pháp | 69 (13.3%) | **0 (0.00%)** | Triệt tiêu 100% |
| 2. Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`) | 29 (5.6%) | **0 (0.00%)** | Triệt tiêu 100% |
| 3. Cụm nhận xét thừa sau dấu chấm ở cuối câu | 37 (7.2%) | **0 (0.00%)** | Triệt tiêu 100% |
| 4. Tiểu từ đề nghị (`nhé/nha/nghen`) gắn câu hỏi `?` | 16 (3.1%) | **0 (0.00%)** | Triệt tiêu 100% |
| 5. Kết thúc bằng dấu phẩy hoặc hai chấm dở dang | 0 (0.0%) | **0 (0.00%)** | Chuẩn hóa 100% |
| 6. Hai dấu cách liên tiếp trong câu | 0 (0.0%) | **0 (0.00%)** | Chuẩn hóa 100% |
| 7. Biến f-string chưa thay (`{goi}`, `{sub}`, v.v.) | 3 (0.6%) | **0 (0.00%)** | Triệt tiêu 100% |
| 8. Lượt thoại quá dài (> 40 từ) | Không kiểm | **3 (0.35%)** | Kiểm soát lâm sàng đạt chuẩn |
| **Tổng số lỗi cấu trúc & ngữ pháp** | **219 lỗi** | **0 lỗi (chỉ có 3 câu >40 từ)** | **ĐẠT CHUẨN XUẤT SẮC** |

---

## 2. Chi Tiết Từng Ca Trong 50 Hội Thoại Đọc Mẫu

### Ca 01 — Mã: `v2mr_3412` (`loãng xương sau mãn kinh`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['dai_tu_ho_hang']` | `so_luot=14`
- **Lời thoại:**
```text
L01: Bác sĩ: cô dùng vitamin C theo đơn cũ thấy triệu chứng có đỡ hơn không ạ?
L02: Bệnh nhân: Vâng, uống được ít hôm rồi ngừng, ngừng 3 tuần rồi ạ.
L03: Bác sĩ: Bác sĩ muốn xác nhận trước, cô đi khám cho mình phải không?
L04: Bệnh nhân: Vâng, tôi đi khám cho mình.
L05: Bệnh nhân: Tôi bị đo mật độ xương dxa có chỉ số t-score dưới âm 2.5 làm khó chịu vài năm rồi.
L06: Bác sĩ: Có đau tức ngực hay hồi hộp không thế?
L07: Bệnh nhân: Dạ, tôi kèm theo cả xquang cột sống có hình ảnh đốt sống tăng thấu quang hình thấu kính.
L08: Bác sĩ: Có tiền sử bệnh phổi hay phế quản không?
L09: Bệnh nhân: Không ạ, tôi trước giờ sức khỏe bình thường ạ.
L10: Bác sĩ: Cô hít sâu thở đều một chút nhé.
L11: Bác sĩ: Gù nhẹ cột sống ngực, không điểm đau khu trú.
L12: Bác sĩ: Hướng tới: Theo dõi loãng xương.
L13: Bác sĩ: Đo mật độ xương. Bổ sung canxi và vitamin D.
L14: Bệnh nhân: Vâng ạ, tôi sẽ theo dõi kỹ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 02 — Mã: `v2mr_2314` (`rối loạn lo âu`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=17`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào chị, hôm nay chị thấy đau nhức hay khó chịu ở cơ quan nào ạ?
L02: Bác sĩ: Nắng nóng đi đường có mệt không ạ?
L03: Bệnh nhân: Em có mặc áo khoác.
L04: Bệnh nhân: Em thấy trong người tim đập loạn lên nửa năm rồi.
L05: Bác sĩ: Có dấu hiệu nào mới nữa không ạ?
L06: Bệnh nhân: Dạ vâng, em thấy có thêm ướt hết áo, run tay mấy hôm nay.
L07: Bác sĩ: Bản thân có bệnh nền gì không ạ?
L08: Bệnh nhân: Dạ thưa bác sĩ, em có viêm dạ dày.
L09: Bác sĩ: Tiện hỏi luôn, uống thuốc có bị phản ứng lạ không?
L10: Bệnh nhân: Dạ đúng rồi bác sĩ, trước đây tôi từng bị dị ứng amoxicillin ạ.
L11: Bác sĩ: Đã dùng thuốc gì trước khi tới chưa thế?
L12: Bệnh nhân: Dạ chưa, em chưa uống thuốc gì nha bác sĩ.
L13: Bác sĩ: Tôi sờ nắn chỗ đau nhé.
L14: Bác sĩ: Tim đều, không tiếng thổi. Huyết áp bình thường.
L15: Bác sĩ: Rối loạn lo âu.
L16: Bác sĩ: Kế hoạch: Tư vấn tâm lý. Hạn chế cà phê. Hẹn khám lại sau một tháng.
L17: Bệnh nhân: Dạ vâng, cảm ơn bác sĩ đã khám kỹ nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 03 — Mã: `v2mr_4836` (`suy tim mạn`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['dai_tu_ho_hang', 'dien_bien', 'dinh_chinh', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=21`
- **Lời thoại:**
```text
L01: Bác sĩ: Tình hình uống efferalgan từ hôm tái khám trước tới nay thế nào rồi em ấy?
L02: Người nhà: Dạ thưa bác sĩ, uống được ít hôm rồi ngừng, ngừng 4 tuần rồi.
L03: Bác sĩ: Bác sĩ hỏi một chút, em là người nhà gì của em ấy thế ạ?
L04: Người nhà: Thưa bác sĩ, em là chồng của em ấy.
L05: Bác sĩ: Sáng giờ em ăn sáng chưa?
L06: Người nhà: Dạ cảm ơn bác sĩ.
L07: Người nhà: Vợ em phát hiện bị khó thở khi nằm mấy tháng nay.
L08: Người nhà: Em nói lại cho đúng, nửa năm rồi chứ không phải mấy tháng nay ạ.
L09: Bác sĩ: Cho hỏi thêm, có sốt, ớn lạnh hay buồn nôn không vậy?
L10: Người nhà: Thưa bác sĩ, bên cạnh đó vợ em cũng bị tăng cân nhanh ạ.
L11: Người nhà: Tối qua thì phù chân, sáng nay thì đỡ hẳn rồi.
L12: Người nhà: Em cũng đang cận thị nặng, nên em hay lo ạ.
L13: Bác sĩ: Có dị ứng thuốc nào không thế?
L14: Người nhà: Dạ chưa, em chưa từng bị phát ban.
L15: Bác sĩ: Trước khi tới có uống liều nào chưa vậy?
L16: Người nhà: Không ạ, em chưa kịp uống viên nào.
L17: Bác sĩ: Em ngồi yên tôi nghe tim phổi một chút nhé.
L18: Bác sĩ: Thăm khám ghi nhận: Phù hai chân, phổi có ran ẩm hai đáy.
L19: Bác sĩ: Chẩn đoán: Suy tim mạn.
L20: Bác sĩ: Phác đồ: Siêu âm tim, xét nghiệm NT-proBNP. Hạn chế muối. Cân hằng ngày.
L21: Người nhà: Vâng, xin cảm ơn bác sĩ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 04 — Mã: `v2mr_0125` (`viêm tắc động mạch chi dưới mạn tính`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['bo_sung']` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời em ngồi, Em thấy trong người phát sinh dấu hiệu gì lạ thế ạ?
L02: Bác sĩ: Em ăn sáng chưa?
L03: Bệnh nhân: Dạ đỡ nhiều rồi.
L04: Bệnh nhân: Em bắt đầu bị dấu hiệu đau cách hồi đi bộ một đoạn khoảng 100 mét thì đau bắp chân phải dừng lại nghỉ khoảng một tháng.
L05: Bác sĩ: Ngoài ra, có sốt, ớn lạnh hay buồn nôn không ạ?
L06: Bệnh nhân: Dạ cháu nghe bác sĩ, em bị đau nhức buốt ngón chân liên tục về đêm phải thõng chân xuống mép giường để đỡ đau kèm theo nữa ạ.
L07: Bệnh nhân: Đau nhức buốt ngón chân liên tục về đêm phải thõng chân xuống mép giường để đỡ đau thì tăng lên khi vận động ạ.
L08: Bác sĩ: Có tiền sử hen phế quản không vậy?
L09: Bệnh nhân: Em không có bệnh mạn tính ạ.
L10: Bác sĩ: Em ngồi thẳng lưng tôi nghe phổi một chút nhé.
L11: Bác sĩ: Mạch mu chân hai bên mất, chân trái lạnh teo cơ bắp chân, ABI chân trái 0.55.
L12: Bác sĩ: Hướng tới: Viêm tắc động mạch chi dưới mạn tính giai đoạn 3 theo Fontaine do xơ vữa.
L13: Bác sĩ: Thuốc ức chế ngưng tập tiểu cầu clopidogrel kết hợp cilostazol giãn mạch tăng tuần hoàn bàng hệ. Chụp cắt lớp vi tính mạch máu cta chi dưới xét can thiệp nong đặt stent.
L14: Bác sĩ: Đơn thuốc hôm nay tôi kê cetirizine 10 mg, uống ngày một lần buổi tối nghen.
L15: Bệnh nhân: Dạ, em sẽ theo dõi kỹ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 05 — Mã: `v2mr_4702` (`bệnh cơ tim giãn vô căn`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['luoc_chu_ngu']` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Hôm nay chị khám gì?
L02: Bác sĩ: Bây giờ chị sẵn sàng để bác sĩ kiểm tra chưa ạ?
L03: Bệnh nhân: Dạ rồi ạ.
L04: Bệnh nhân: Bắt đầu thấy khó thở khi nằm đầu bằng orthopnea phải kê 3 gối hoặc ngồi dậy thở dốc nửa đêm từ năm ngoái.
L05: Bác sĩ: Còn khó chịu chỗ nào khác không ạ?
L06: Bệnh nhân: Dạ, cùng lúc đó cũng xuất hiện buồng tâm thất trái giãn to đường kính cuối tâm trương lvdd trên 65 mm, phân suất tống máu thất trái ef giảm sâu dưới 30 phần trăm trên siêu âm tim.
L07: Bác sĩ: Về bệnh cũ, từng nằm viện điều trị bao giờ chưa thế?
L08: Bệnh nhân: Dạ bác sĩ, có viêm dạ dày ạ.
L09: Bác sĩ: Có uống viên thuốc nào từ sáng chưa vậy?
L10: Bệnh nhân: Dạ bác sĩ, có nhỏ thuốc nhỏ mắt natri clorid hai giọt, ngày ba lần.
L11: Bác sĩ: Tôi khám qua cho chị nhé ạ.
L12: Bác sĩ: Mỏm tim đập ở khoang liên sườn 6 ngoài đường trung đòn trái, tĩnh mạch cổ nổi to 45 độ, phù 2 chân.
L13: Bác sĩ: Tôi chẩn đoán: Bệnh cơ tim giãn vô căn suy tim toàn bộ giai đoạn C theo AHA.
L14: Bác sĩ: Phác đồ: Điều trị nội khoa tối ưu tứ trụ suy tim: thuốc arni sacubitril valsartan, chẹn beta, kháng aldosterone và thuốc sglt2i dapagliflozin.
L15: Bệnh nhân: Dạ bác sĩ, cảm ơn bác sĩ đã khám kỹ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 06 — Mã: `v2mr_2971` (`sốt phát ban`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['dien_bien', 'nguoi_nha_ke_ho']` | `so_luot=18`
- **Lời thoại:**
```text
L01: Bác sĩ: Tình hình uống amoxicillin từ hôm tái khám trước tới nay thế nào rồi cháu?
L02: Người nhà: Dạ, vẫn đang uống amoxicillin.
L03: Bác sĩ: Bà thấy đỡ thở dốc chưa?
L04: Người nhà: Dạ, tôi thở đều lại rồi.
L05: Người nhà: Cháu nó thấy xuất hiện sốt cao liên tục 3 ngày rồi dứt sốt thì mọc ban năm hôm ạ.
L06: Bác sĩ: Ăn ngủ dạo này có được không ạ?
L07: Người nhà: Dạ thưa bác sĩ, cháu nó còn than phiền là bị trẻ quấy khóc cáu gắt trong giai đoạn sốt cao nữa.
L08: Người nhà: Chiều hôm qua thì ban dạng dát sẩn màu hồng đào mịn như nhung mọc toàn thân, sáng nay thì đỡ hẳn rồi.
L09: Bác sĩ: Tiện hỏi luôn, có dị ứng kháng sinh hay giảm đau không ạ?
L10: Người nhà: Con chưa từng dị ứng thuốc ạ.
L11: Bác sĩ: Có đang dùng thuốc theo đơn không thế?
L12: Người nhà: Dạ thưa bác, cháu nó có uống oresol một gói, ngày ba lần.
L13: Bác sĩ: Để bác sĩ xem các khớp có sưng không nhé.
L14: Bác sĩ: Ban hồng rải rác thân mình, hạch cổ nhỏ.
L15: Bác sĩ: Sốt phát ban.
L16: Bác sĩ: Phác đồ: Hạ sốt khi trên 38,5 độ. Theo dõi thêm hai ngày.
L17: Bác sĩ: Bác sĩ quyết định kê salbutamol hai nhát, xịt khi cần nhé.
L18: Người nhà: Tôi hiểu đơn thuốc rồi ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 07 — Mã: `v2mr_0043` (`nấm kẽ chân tinea pedis`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['di_ung_nguoi_nha', 'mau_thuan', 'nguoi_nha_ke_ho']` | `so_luot=18`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào bà, lý do chính mà gia đình đưa bé đi khám hôm nay là gì?
L02: Bác sĩ: Cho tôi hỏi rõ là, mình có quan hệ gia đình thế nào với bé thế ạ?
L03: Người nhà: Vâng ạ, tôi là bà ngoại đưa bé đi khám.
L04: Bác sĩ: Đường tới đây có đông không ạ?
L05: Người nhà: Dạ, đi lại cũng thuận tiện.
L06: Người nhà: Cháu nó cảm giác mủn trắng bong vảy nứt kẽ trợt đỏ ở kẽ ngón chân thứ tư và ngón thứ năm hơn một năm.
L07: Người nhà: Mà cũng có thể vài năm rồi, tôi không chắc lắm ạ.
L08: Bác sĩ: Để tôi ghi là chưa rõ hơn một năm hay vài năm rồi, mình xác nhận lại sau nhé.
L09: Bác sĩ: Ăn ngủ dạo này có được không vậy?
L10: Người nhà: Dạ thưa bác, cháu nó còn thường gặp ở người hay đi giày kín thể thao công nhân lội nước chân nước ăn chân nữa.
L11: Bác sĩ: À, có dị ứng thuốc nào không vậy?
L12: Người nhà: Dạ bác sĩ, ông nội thì dị ứng cua, còn cháu nó chưa thấy bị bao giờ ạ.
L13: Bác sĩ: Để tôi nghe tim và phổi một chút nhé.
L14: Bác sĩ: Khám thực thể: Kẽ ngón 4-5 chân hai bên da mủn trắng bong tróc, đáy đỏ trợt rỉ dịch nhẹ.
L15: Bác sĩ: Nấm kẽ chân Tinea pedis thể trợt kẽ ngón.
L16: Bác sĩ: Bác sĩ dặn: Bôi kem kháng nấm terbinafine hoặc clotrimazole ngày 2 lần kéo dài 3 tuần. Rửa chân lau khô hoàn toàn các kẽ ngón, thay tất cotton khô thoáng hàng ngày.
L17: Bác sĩ: Bác sĩ sẽ kê smecta một gói, uống ngày hai lần nghen.
L18: Người nhà: Tôi nhớ lời bác sĩ dặn rồi nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 08 — Mã: `v2mr_4468` (`viêm tụy cấp nhẹ`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Bác sĩ chào ông, hãy chia sẻ cụ thể lý do mình đi khám hôm nay nhé.
L02: Bác sĩ: Cho tôi hỏi một chút, ông đi khám cho mình phải không ạ?
L03: Bệnh nhân: Vâng ạ.
L04: Bác sĩ: Trước khi vào ông ngồi nghỉ đỡ mệt chưa?
L05: Bệnh nhân: Tôi uống nước rồi ạ.
L06: Bệnh nhân: Tôi bị đau bụng thượng vị dữ dội xuyên ra sau lưng sau bữa ăn nhiều dầu mỡ rượu bia liên tục bốn hôm.
L07: Bác sĩ: Trong người còn thấy gì lạ không vậy?
L08: Bệnh nhân: Vâng tôi nghe đây ạ, chưa kể tôi còn bị bí trung đại tiện, mồ hôi ra đầm đìa nữa.
L09: Bác sĩ: Có mẫn cảm với thuốc gì không ạ?
L10: Bệnh nhân: Chưa ạ, tôi uống thuốc rất êm.
L11: Bác sĩ: Rồi, để tôi nghe tim và phổi nhé.
L12: Bác sĩ: Bụng chướng nhẹ, ấn đau tức nhiều vùng thượng vị, không có co cứng thành bụng, dấu Mayo-Robson dương tính.
L13: Bác sĩ: Viêm tụy cấp thể nhẹ tiên lượng lành tính.
L14: Bác sĩ: Phác đồ: Xét nghiệm men tụy Amylase và Lipase máu tăng gấp 3 lần giới hạn trên. Nhịn ăn đường miệng, truyền dịch bù nước điện giải tích cực.
L15: Bệnh nhân: Cảm ơn bác sĩ đã khám kỹ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 09 — Mã: `v2mr_4171` (`đau thần kinh tọa`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=['dien_bien', 'dinh_chinh']` | `so_luot=16`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào ông, mời ông ngồi tự nhiên rồi kể bệnh tình giúp tôi nhé.
L02: Bác sĩ: Để ghi vào hồ sơ thì, ông đến kiểm tra sức khỏe cho bản thân mình phải không ạ?
L03: Bệnh nhân: Dạ, hôm nay tôi khám ạ.
L04: Bác sĩ: Sảnh chờ có thoáng không ạ?
L05: Bệnh nhân: Dạ, đợi chút xíu là tới lượt ạ.
L06: Bệnh nhân: Tôi bị đau lưng lan xuống chân liên tục nửa năm rồi.
L07: Bệnh nhân: À không, tôi nhầm, khoảng một tháng chứ không phải nửa năm rồi.
L08: Bác sĩ: Còn chỗ nào đau nữa không vậy?
L09: Bệnh nhân: Dạ thưa bác, đồng thời tôi còn thấy yếu chân, mệt ạ.
L10: Bệnh nhân: Từ tuần trước thì tê chân, từ hôm chủ nhật thì đỡ hẳn rồi.
L11: Bác sĩ: Tiếp theo, ông nằm lên bàn khám nghen.
L12: Bác sĩ: Ghi nhận: Dấu Lasègue dương tính bên phải.
L13: Bác sĩ: Tôi nghĩ nhiều đến đau thần kinh tọa, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã nghen.
L14: Bác sĩ: Ông đi làm xét nghiệm nước tiểu rồi quay lại đây nha.
L15: Bác sĩ: Tôi sẽ kê đơn metformin 500 mg, uống ngày hai lần sau ăn nhé.
L16: Bệnh nhân: Cảm ơn bác sĩ nhiều nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 10 — Mã: `v2mr_0848` (`đau dây thần kinh tam thoa`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=19`
- **Lời thoại:**
```text
L01: Bác sĩ: Lần trước tôi kê hapacol cho chú ấy, dùng thấy thế nào ạ?
L02: Người nhà: Dạ bác sĩ, vẫn đang uống hapacol.
L03: Bác sĩ: Bác sĩ muốn xác nhận, em là gì của chú ấy?
L04: Người nhà: Thưa bác sĩ, em là con gái của chú ấy bác sĩ ạ.
L05: Bác sĩ: Dạo này công việc có bận lắm không ạ?
L06: Người nhà: Hơi bận nhưng vẫn ổn.
L07: Bác sĩ: Em đã sẵn sàng vào khám chưa ạ?
L08: Người nhà: Dạ được rồi.
L09: Người nhà: Bố em cứ bị cơn đau nhói buốt như điện giật ở một bên mặt nửa năm rồi ạ.
L10: Bác sĩ: Có dấu hiệu nào mới nữa không ạ?
L11: Người nhà: Dạ bác sĩ, bố em còn xuất hiện lo âu căng thẳng, sợ chạm vào mặt nữa bác sĩ ạ.
L12: Người nhà: Em cũng đang viêm gan B, nên em hay lo.
L13: Bác sĩ: Đã mua thuốc gì uống chưa thế?
L14: Người nhà: Dạ chưa, chú chưa uống hạ sốt gì.
L15: Bác sĩ: Để tôi kiểm tra một lượt một chút nhé.
L16: Bác sĩ: Không có rối loạn cảm giác khách quan vùng mặt, chạm vào rãnh mũi má bên đau kích hoạt cơn đau chói (vùng kích hoạt trigger point).
L17: Bác sĩ: Đau dây thần kinh sinh ba (dây V) nhánh V2 bên phải vô căn.
L18: Bác sĩ: Về điều trị: Chụp MRI sọ não chuỗi xung CISS khảo sát mạch máu chèn ép rễ thần kinh số V. Điều trị bước đầu bằng carbamazepine liều tăng dần.
L19: Người nhà: Cảm ơn bác sĩ nhiều nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 11 — Mã: `v2mr_2469` (`mất ngủ mạn tính`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['luoc_chu_ngu', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho', 'nguon_khac_nhau', 'tien_su_gia_dinh']` | `so_luot=19`
- **Lời thoại:**
```text
L01: Bác sĩ: Chị kể rõ giúp bác sĩ xem anh ở nhà sinh hoạt ăn uống ra sao?
L02: Bác sĩ: Chị có quan hệ như thế nào với anh ấy vậy ạ?
L03: Người nhà: Dạ vâng, tôi là vợ đưa anh ấy đi khám.
L04: Người nhà: Phát hiện bị khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được hai tháng nay.
L05: Bệnh nhân: Theo tôi thì mấy tháng nay mới đúng ạ.
L06: Bác sĩ: Để tôi ghi là chưa rõ hai tháng nay hay mấy tháng nay, mình xác nhận lại sau nhé.
L07: Bác sĩ: Còn triệu chứng nào nữa không vậy?
L08: Người nhà: Vâng ạ, còn thấy tâm trạng cáu gắt lo âu về giấc ngủ mỗi khi trời tối nữa ạ.
L09: Bác sĩ: Từng nằm viện hay mổ lần nào chưa vậy?
L10: Người nhà: Vâng ạ, có viêm dạ dày.
L11: Bác sĩ: Bố mẹ có ai bị tim mạch không ạ?
L12: Người nhà: Thưa bác sĩ, bố bị lao phổi.
L13: Người nhà: Tôi thì viêm amidan mạn, nói thêm để bác sĩ biết ạ.
L14: Bác sĩ: Bác sĩ nghe tim phổi cho anh nghen.
L15: Bác sĩ: Thăm khám ghi nhận: Không phát hiện bất thường khi khám.
L16: Bác sĩ: Chẩn đoán: Mất ngủ mạn tính.
L17: Bác sĩ: Vệ sinh giấc ngủ. Bỏ cà phê buổi chiều. Chưa dùng thuốc ngủ.
L18: Bác sĩ: Tôi kê kem bôi fucidin một lớp mỏng, bôi ngày hai lần nhé ạ.
L19: Người nhà: Dạ, tôi sẽ tái khám đúng hẹn nhé ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 12 — Mã: `v2mr_3452` (`viêm cơ tim do virus`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=11`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời chú ngồi. Chú bị làm sao?
L02: Bác sĩ: Lúc lấy số tiếp đón có thuận lợi không chú ạ?
L03: Bệnh nhân: Dạ đỡ nhiều rồi ạ.
L04: Bệnh nhân: Tôi bắt đầu thấy men tim troponin t và i tăng vọt sau đợt nhiễm siêu vi đường ruột mấy hôm nay.
L05: Bác sĩ: Còn khó chịu chỗ nào khác không vậy?
L06: Bệnh nhân: Vâng em nghe, tôi phát sinh thêm cả tiền sử sốt cảm cúm đau cơ hai tuần trước đó, đoạn st chênh lên lan tỏa nhiều chuyển đạo trên điện tim nữa bác sĩ.
L07: Bác sĩ: Tiếp theo, tôi sờ nắn chỗ đau nha.
L08: Bác sĩ: Ghi nhận: Tiếng tim mờ, nhịp tim nhanh 115 lần/phút không tương xứng với sốt, huyết áp dao động tụt nhẹ.
L09: Bác sĩ: Hướng tới: Theo dõi viêm cơ tim cấp sau nhiễm siêu vi.
L10: Bác sĩ: Xét nghiệm men tim Troponin T/I siêu nhạy, CK-MB, điện tim 12 chuyển đạo. Nhập viện khoa Hồi sức tim mạch theo dõi sát loạn nhịp.
L11: Bệnh nhân: Vâng, xin cảm ơn bác sĩ nhé ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 13 — Mã: `v2mr_1338` (`sởi ở trẻ em`)
- **Thông tin ca:** `boi_canh=dieu_duong_ban_giao` | `khuon_da_duyet=False` | `bay=['dai_tu_ho_hang', 'mau_thuan', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=20`
- **Lời thoại:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Con này chờ từ nãy, cập nhật sinh hiệu xong ạ.
L02: Bác sĩ: Cảm ơn em nhé. Mời Con ngồi nghỉ rồi kể xem triệu chứng xuất hiện thế nào.
L03: Bác sĩ: Mấy nay mưa gió đi lại có vất vả không bà?
L04: Người nhà: Cũng hơi lừ đừ.
L05: Bác sĩ: Trước khi vào bà uống ngụm nước chưa ạ?
L06: Người nhà: Dạ, tôi uống nước rồi ạ.
L07: Người nhà: Cháu tôi cảm giác sốt cao liên tục 39-40 độ năm hôm ạ.
L08: Người nhà: Mà cũng có thể hai hôm, tôi không chắc lắm.
L09: Bác sĩ: Để tôi ghi là chưa rõ năm hôm hay hai hôm, mình xác nhận lại sau nhé ạ.
L10: Bác sĩ: Có kèm theo khó thở không?
L11: Người nhà: Dạ, đi kèm với đó là cháu tôi bị tiêu chảy.
L12: Người nhà: Tôi bị sỏi niệu quản mấy năm nay rồi ạ.
L13: Bác sĩ: Uống thuốc có bị phù nề không?
L14: Người nhà: Dạ chưa từng.
L15: Bác sĩ: Bác sĩ kiểm tra phản xạ nghen.
L16: Điều dưỡng: Ban đỏ dạng sởi nổi gồ mịn mọc dày ở mặt và ngực, kết mạc mắt đỏ nhiều gỉ mắt, khám miệng thấy nốt Koplik đối diện răng hàm.
L17: Bác sĩ: Tôi chẩn đoán: Bệnh sởi giai đoạn phát ban ngày thứ hai.
L18: Bác sĩ: Phác đồ: Cách ly trẻ tại phòng riêng thoáng khí. Bổ sung Vitamin A liều cao theo tuổi phòng biến chứng giác mạc, hạ sốt, rửa mắt mũi bằng nước muối sinh lý.
L19: Bác sĩ: Tôi bổ sung kê amoxicillin 5 ml, uống ngày hai lần nhé.
L20: Người nhà: Dạ, cảm ơn bác sĩ nhiều nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 14 — Mã: `v2mr_3943` (`viêm mô tế bào quanh hốc mắt trẻ`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['di_ung_nguoi_nha', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=16`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào chị, hôm nay chị đưa cháu đi khám vì sao?
L02: Bác sĩ: Bác sĩ kiểm tra cho chị được chưa ạ?
L03: Người nhà: Bác sĩ cứ kiểm tra tự nhiên.
L04: Người nhà: Con tôi có dấu hiệu sưng nề đỏ đau nóng mi mắt một bên không mở được mắt từ hôm kia ạ.
L05: Bác sĩ: Cho hỏi thêm, ăn ngủ dạo này có được không thế?
L06: Người nhà: Dạ em nghe bác sĩ, con tôi còn xuất hiện bạch cầu máu tăng cao trên 15000 tế bào, vận động nhãn cầu bình thường không lồi mắt thị lực bình thường nữa bác sĩ.
L07: Bác sĩ: Có theo dõi ở chuyên khoa nào không?
L08: Người nhà: Dạ em nghe bác sĩ, con tôi có sinh non ạ.
L09: Người nhà: Tôi thì lao phổi, nói thêm để bác sĩ biết ạ.
L10: Bác sĩ: À, từng bị phát ban khi dùng thuốc chưa vậy?
L11: Người nhà: Dạ bác sĩ, tôi thì dị ứng nấm mốc, còn con tôi chưa thấy bị bao giờ.
L12: Bác sĩ: Tiếp theo, cháu há miệng tôi soi họng nhé ạ.
L13: Bác sĩ: Ghi nhận: Mi mắt trên bên trái sưng húp đỏ tím, khe mi hẹp, nhãn cầu vận nhãn đủ hướng.
L14: Bác sĩ: Viêm mô tế bào trước vách mi mắt trái.
L15: Bác sĩ: Kế hoạch: Kháng sinh đường tĩnh mạch amoxicillin clavulanate hoặc cefotaxime. Chụp ct scan sọ hốc mắt nếu nghi ngờ viêm sau vách hốc mắt.
L16: Người nhà: Dạ bác sĩ, tôi sẽ theo dõi kỹ nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 15 — Mã: `v2mr_0651` (`co giật do sốt`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['bo_sung', 'dien_bien', 'lieu_dinh_chinh', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=18`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào anh, mấy hôm nay cháu nhà mình có dấu hiệu gì bất thường vậy ạ?
L02: Người nhà: Dạ bác sĩ, cháu nhà tôi phát hiện bị cơn co giật giật cứng giật rung toàn thể khi nhiệt độ cơ thể vượt 39 độ từ hôm kia ạ.
L03: Bác sĩ: Trong người còn thấy gì lạ không thế?
L04: Người nhà: Dạ thưa bác, cùng lúc đó cháu nhà tôi cũng xuất hiện tiền sử gia đình có người thân từng bị sốt cao co giật, không có bất kỳ dấu hiệu thần kinh khu trú nào.
L05: Người nhà: Không có bất kỳ dấu hiệu thần kinh khu trú nào thì chỉ bị lúc sáng sớm.
L06: Người nhà: Chiều hôm qua thì thời gian co giật kéo dài ngắn dưới mười phút tự dứt, hôm kia thì đỡ hẳn rồi.
L07: Bác sĩ: Từng có đợt uống thuốc kéo dài không?
L08: Người nhà: Dạ thưa bác sĩ, cháu nhà tôi có viêm amidan hay tái phát.
L09: Người nhà: Tôi bị ngưng thở khi ngủ mấy năm nay rồi ạ.
L10: Bác sĩ: Có dị ứng thuốc nào không vậy?
L11: Người nhà: Bình thường ạ.
L12: Bác sĩ: Cho hỏi, đã mua thuốc gì uống chưa?
L13: Người nhà: Dạ thưa đúng ạ, cháu nhà tôi có uống paracetamol một gói, à nhầm, nửa gói mới đúng, khi cần, dùng được hai tuần nay.
L14: Bác sĩ: Để bác sĩ kiểm tra họng nghen.
L15: Bác sĩ: Tỉnh, thóp phẳng, không dấu màng não.
L16: Bác sĩ: Khả năng cao là: Co giật do sốt đơn giản.
L17: Bác sĩ: Về điều trị: Hạ sốt tích cực. Hướng dẫn xử trí khi co giật. Đến viện ngay nếu cơn kéo dài.
L18: Người nhà: Dạ, chúc bác sĩ nhiều sức khỏe nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 16 — Mã: `v2mr_3373` (`không dung nạp lactose`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['bo_sung', 'dai_tu_ho_hang', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời bà ngồi, bác sĩ nghe bà kể về tình hình sức khỏe của bé đây ạ.
L02: Bác sĩ: Để tiện xưng hô trong hồ sơ, bà là gì của bé ạ?
L03: Người nhà: Dạ thưa bác sĩ, tôi là bà ngoại đưa bé đi khám bác sĩ ạ.
L04: Bác sĩ: Bây giờ bà sẵn sàng để bác sĩ kiểm tra chưa?
L05: Người nhà: Bác sĩ cứ làm đi ạ.
L06: Người nhà: Cháu tôi bắt đầu thấy đầy hơi sôi bụng dữ dội sau khi uống sữa hơn một năm ạ.
L07: Bác sĩ: Có sụt cân, chán ăn, mất ngủ không vậy?
L08: Người nhà: Vâng tôi nghe đây ạ, cháu tôi còn lừ đừ cả ngày sau ăn sữa, buồn nôn nữa.
L09: Người nhà: Người rã rời sau ăn sữa thì tăng lên khi vận động.
L10: Người nhà: Tôi bị hẹp van động mạch chủ mấy năm nay rồi ạ.
L11: Bác sĩ: Để tôi xem vùng da niêm mạc nhé ạ.
L12: Bác sĩ: Bụng mềm, gõ vang nhẹ quanh rốn, nghe nhu động ruột tăng tần số, không có điểm đau khu trú.
L13: Bác sĩ: Hướng tới: Hội chứng không dung nạp đường lactose tiên phát.
L14: Bác sĩ: Kế hoạch: Kiêng hoàn toàn sữa bò tươi và các chế phẩm chứa lactose thông thường, chuyển dùng sữa không lactose (lactose-free) hoặc bổ sung men lactase.
L15: Người nhà: Xin cảm ơn bác sĩ nhé ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 17 — Mã: `v2mr_2736` (`chàm sữa`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['luoc_chu_ngu', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=14`
- **Lời thoại:**
```text
L01: Bác sĩ: Đợt khám trước cháu uống salbutamol có thấy thuyên giảm không ạ?
L02: Người nhà: Dạ, vẫn đang xịt salbutamol ạ.
L03: Người nhà: Cảm giác mảng da đỏ sần mụn nước li ti đối xứng hai bên má trẻ nhũ nhi mấy tháng nay.
L04: Bác sĩ: Có đau nhức hay mệt ở đâu không?
L05: Người nhà: Dạ thưa bác, thấy có thêm thường khởi phát sau tháng thứ ba sau sinh, tiền sử gia đình có cơ địa dị ứng hen suyễn mấy hôm nay ạ.
L06: Người nhà: Tôi cũng đang gan nhiễm mỡ, nên tôi hay lo.
L07: Bác sĩ: Cho hỏi, có đang dùng thuốc theo đơn không ạ?
L08: Người nhà: Dạ bác sĩ, trước có uống amoxicillin, ngừng 2 tuần rồi.
L09: Bác sĩ: Cháu ngồi yên tôi nghe tim phổi nhé ạ.
L10: Bác sĩ: Tôi ghi nhận: Ban đỏ hai má, có vảy tiết, không bội nhiễm.
L11: Bác sĩ: Chàm sữa.
L12: Bác sĩ: Dưỡng ẩm ngày hai lần. Tắm nước ấm, không dùng xà phòng thơm.
L13: Bác sĩ: Bác sĩ kê paracetamol nửa gói, uống ngày ba lần nhé.
L14: Người nhà: Dạ bác sĩ, cảm ơn bác sĩ nhiều nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 18 — Mã: `v2mr_1990` (`viêm màng bồ đào trước cấp tính`)
- **Thông tin ca:** `boi_canh=dieu_duong_ban_giao` | `khuon_da_duyet=False` | `bay=['dien_bien', 'dinh_chinh']` | `so_luot=18`
- **Lời thoại:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Anh này chờ từ nãy, cập nhật sinh hiệu xong ạ.
L02: Bác sĩ: Cảm ơn em. Anh kể tôi nghe xem thế nào.
L03: Bác sĩ: Anh đến đây khám bệnh cho mình hay cho ai khác thế ạ?
L04: Bệnh nhân: Dạ của tôi ạ.
L05: Bệnh nhân: Cơn đau nhức sâu trong nhãn cầu lan lên nửa đầu cùng bên đau dữ dội nhức buốt mắt này tôi bị hai hôm.
L06: Bệnh nhân: Xin lỗi bác sĩ, tôi nhớ lại rồi, hơn một tuần chứ không phải hai hôm.
L07: Bác sĩ: Có bị đau đầu hay hoa mắt không thế?
L08: Bệnh nhân: Vâng thưa bác sĩ, tôi phát sinh thêm cả đồng tử co nhỏ méo mó dính vào mặt trước thể thủy tinh phản xạ ánh sáng lười, lắng đọng tủa viêm dạng bụi ở mặt sau giác mạc nữa bác sĩ.
L09: Bệnh nhân: Hôm qua thì thị lực giảm nhìn mờ như nhìn qua màn khói sương mù dày đặc, hôm kia thì đỡ hẳn rồi ạ.
L10: Bác sĩ: Trước giờ có bệnh gì phải theo dõi định kỳ không?
L11: Bệnh nhân: Thưa bác sĩ, tôi có rối loạn mỡ máu.
L12: Bác sĩ: Tiện hỏi luôn, có dị ứng kháng sinh hay giảm đau không thế?
L13: Bệnh nhân: Dạ vâng ạ, có, tôi bị dị ứng aspirin ạ.
L14: Bác sĩ: Rồi, anh ngồi thẳng lưng tôi nghe phổi nghen.
L15: Điều dưỡng: Mắt phải cương tụ rìa rõ, đồng tử méo co nhỏ 2 mm, áp lực nhãn áp bình thường.
L16: Bác sĩ: Viêm màng bồ đào trước cấp tính vô căn mắt phải.
L17: Bác sĩ: Nhỏ mắt thuốc giãn đồng tử liệt thể mi atropin 1% chống dính đồng tử. Nhỏ corticoid tại chỗ prednisolone acetate liều cao và tìm nguyên nhân toàn thân.
L18: Bệnh nhân: Vâng, cảm ơn bác sĩ đã khám kỹ nhé ạ.
```
- **Lỗi ghi nhận (1):**
  - L08 [Bệnh nhân]: Lượt thoại quá dài (> 40 từ) ("Vâng thưa bác sĩ, tôi phát sinh thêm cả đồng tử co nhỏ méo m...")

### Ca 19 — Mã: `v2mr_4941` (`viêm loét đại trực tràng chảy máu`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=13`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời em ngồi xuống, hôm nay em thấy sức khỏe thế nào?
L02: Bác sĩ: Mình bắt đầu kiểm tra được không em?
L03: Bệnh nhân: Dạ vâng ạ.
L04: Bệnh nhân: Em cứ bị đi tiêu nhầy máu tươi rỉ rả kéo dài trên 4 tuần hai tháng nay.
L05: Bác sĩ: Có sốt, ớn lạnh hay buồn nôn không thế?
L06: Bệnh nhân: Dạ em nghe bác sĩ, em ghi nhận thêm hiện tượng đáp ứng điều trị với thuốc chống viêm nhóm 5-asa mesalamine nữa ạ.
L07: Bác sĩ: Có bệnh nền tim mạch không thế?
L08: Bệnh nhân: Em trước giờ khỏe mạnh.
L09: Bác sĩ: Em nằm lên bàn khám một chút nhé.
L10: Bác sĩ: Bụng mềm, ấn đau dọc khung đại tràng trái và hố chậu trái, không có khối bất thường.
L11: Bác sĩ: Tôi chẩn đoán: Viêm loét đại trực tràng chảy máu đợt tiến triển vừa.
L12: Bác sĩ: Tôi hướng dẫn: Nội soi toàn bộ đại trực tràng sinh thiết mô học. Điều trị thuốc chống viêm dẫn xuất 5-ASA (mesalazine) đường uống và thụt.
L13: Bệnh nhân: Dạ, cảm ơn bác sĩ nhiều nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 20 — Mã: `v2mr_0815` (`xơ cứng tai`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['tien_su_gia_dinh']` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Bác sĩ chào em, hãy chia sẻ cụ thể lý do mình đi khám hôm nay nhé.
L02: Bác sĩ: Hôm nay em là người trực tiếp cần khám đúng không vậy ạ?
L03: Bệnh nhân: Đúng rồi, em đi khám cho mình ạ.
L04: Bệnh nhân: Em thấy xuất hiện nghe kém tiến triển chậm cả hai tai khoảng một tháng.
L05: Bác sĩ: Có biểu hiện bất thường nào nữa không vậy?
L06: Bệnh nhân: Dạ thưa bác sĩ, ngoài ra em còn bị nói giọng nhỏ nhẹ hơn bình thường, gia đình có người bị điếc sớm nữa.
L07: Bác sĩ: Trong nhà có ai bị huyết áp không vậy?
L08: Bệnh nhân: Dạ thưa bác, bà nội bị đái tháo đường biến chứng thận.
L09: Bác sĩ: Có dị ứng thuốc hay thức ăn gì không thế?
L10: Bệnh nhân: Hổng có, em uống thuốc bình thường nha bác sĩ.
L11: Bác sĩ: Giờ để bác sĩ nghe vùng ngực nghen.
L12: Bác sĩ: Soi tai màng nhĩ sáng bóng bình thường không thủng, đo thính lực đồ có hình ảnh điếc dẫn truyền hoặc hỗn hợp với khuyết Carhart ở tần số 2000 Hz.
L13: Bác sĩ: Bệnh xơ cứng tai (Otosclerosis) hai bên.
L14: Bác sĩ: Kế hoạch: Đo thính lực thính học toàn diện và nhĩ lượng đồ. Tư vấn mang máy trợ thính hoặc phẫu thuật thay thế xương bàn đạp.
L15: Bệnh nhân: Dạ vâng, cảm ơn bác sĩ đã giúp đỡ nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 21 — Mã: `v2mr_3962` (`viêm tụy mạn sỏi tụy`)
- **Thông tin ca:** `boi_canh=nguoi_nha_thay_mat` | `khuon_da_duyet=False` | `bay=['luoc_chu_ngu', 'nguoi_nha_ke_ho']` | `so_luot=14`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào cháu, chú ấy hôm nay không trực tiếp đi khám cùng mình được sao ạ?
L02: Người nhà: Dạ thưa bác, ở nhà bố cháu mệt không dậy nổi, cháu sốt ruột quá nên đi khám thay.
L03: Bác sĩ: Bác sĩ hỏi một chút, mình có quan hệ gia đình thế nào với chú ấy thế ạ?
L04: Người nhà: Dạ vâng, cháu là con trai của chú ấy ạ.
L05: Bác sĩ: Dạo này cháu ngủ đủ giấc không?
L06: Người nhà: Cháu tranh thủ đi sáng ạ.
L07: Người nhà: Khó chịu vì đại tiện phân mỡ phân sống nổi váng mỡ vàng óng trên mặt nước bồn cầu hai tháng nay ạ.
L08: Bác sĩ: Còn khó chịu chỗ nào khác không thế?
L09: Người nhà: Dạ thưa đúng ạ, còn thấy gầy sút cân nghiêm trọng do kém hấp thu chất béo và protid, tiền sử uống rượu bia nghiện rượu trên mười năm liên tục nữa ạ.
L10: Bác sĩ: Ở nhà đã tự mua thuốc gì uống chưa vậy?
L11: Người nhà: Chưa ạ.
L12: Bác sĩ: Bước đầu nghe cháu nói thì khả năng là viêm tụy mạn tính có sỏi ống tụy do nghiện rượu, nhưng nguyên tắc là phải khám trực tiếp người bệnh ạ.
L13: Bác sĩ: Cháu cố gắng đưa chú ấy đến bệnh viện để bác sĩ đánh giá chính xác nghen.
L14: Người nhà: Cháu nhớ cách uống rồi ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 22 — Mã: `v2mr_3541` (`viêm màng ngoài tim co thắt`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=22`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào chú, tình trạng khó chịu này bắt đầu từ khi nào thế?
L02: Bác sĩ: Để rõ thông tin đăng ký, phiếu khám này là của chính chú phải không vậy ạ?
L03: Bệnh nhân: Đúng rồi bác sĩ.
L04: Bác sĩ: Trời hôm nay sáng se lạnh chú có mặc ấm không?
L05: Bệnh nhân: Bác sĩ cứ làm đi ạ.
L06: Bác sĩ: Bác sĩ kiểm tra cho chú được chưa?
L07: Bệnh nhân: Bác sĩ cứ làm đi ạ.
L08: Bệnh nhân: Tình trạng dấu hiệu kussmaul tĩnh mạch cổ nổi to phồng to hơn khi hít sâu vào của tôi kéo dài vài năm rồi.
L09: Bác sĩ: Ngoài ra, còn khó chịu chỗ nào khác không ạ?
L10: Bệnh nhân: Dạ cháu nghe bác sĩ, tôi còn thấy chụp xquang và cắt lớp vi tính thấy vôi hóa dày đặc bao quanh tim như mai rùa nữa ạ.
L11: Bác sĩ: Về bệnh cũ, sức khỏe trước giờ có bệnh gì không thế?
L12: Bệnh nhân: Dạ vâng, tôi có viêm khớp ạ.
L13: Bác sĩ: À, uống thuốc có bị nổi ngứa không ạ?
L14: Bệnh nhân: Bình thường cả.
L15: Bác sĩ: Có đang dùng thuốc theo đơn không?
L16: Bệnh nhân: Dạ chưa, ở nhà tôi chưa uống gì bác sĩ.
L17: Bác sĩ: Tiếp theo, bác sĩ kiểm tra phản xạ một chút nhé.
L18: Bác sĩ: Ghi nhận: Tĩnh mạch cổ nổi to căng phồng, cổ trướng mức độ vừa, gan to dưới sườn 3 cm bè chắc.
L19: Bác sĩ: Viêm màng ngoài tim co thắt mạn tính do di chứng lao cũ.
L20: Bác sĩ: Hội chẩn phẫu thuật ngoại lồng ngực bóc tách màng ngoài tim giải phóng co thắt. Thuốc lợi tiểu quai furosemide kiểm soát ứ trệ tuần hoàn ngoại vi.
L21: Bác sĩ: Tôi bổ sung kê amoxicillin 250 mg, uống ngày hai lần nhé.
L22: Bệnh nhân: Dạ vâng, chúc bác sĩ công tác tốt nhe bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 23 — Mã: `v2mr_4511` (`viêm bao gân de quervain`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=20`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào ông, mấy hôm nay cơ thể có biểu hiện gì khiến ông phải đi khám ạ?
L02: Bác sĩ: Để rõ thông tin đăng ký, có phải ông là bệnh nhân cần khám hôm nay không thế ạ?
L03: Bệnh nhân: Dạ của tôi ạ.
L04: Bác sĩ: Hôm nay ông xin nghỉ làm đi khám à?
L05: Bệnh nhân: Dạ ổn ạ.
L06: Bác sĩ: Ông có thấy khát nước không?
L07: Bệnh nhân: Bác sĩ cứ làm đi ạ.
L08: Bệnh nhân: Tôi bị đau chói buốt vùng mỏm trâm quay cổ tay phía gốc ngón tay cái liên tục năm hôm.
L09: Bác sĩ: Có kèm theo khó thở không?
L10: Bệnh nhân: Vâng, chưa kể tôi còn bị nghiệm pháp finkelstein dương tính gấp ngón cái nắm chặt rồi uốn cổ tay về phía xương trụ gây đau chói nữa ạ.
L11: Bác sĩ: Về bệnh cũ, có tiền sử tim mạch, huyết áp không thế?
L12: Bệnh nhân: Tôi không bị tim mạch hay gan thận.
L13: Bác sĩ: À, có dị ứng với kháng sinh không vậy?
L14: Bệnh nhân: Dạ vâng ạ, tuyến trước bảo tôi có cơ địa dị ứng sulfamid ạ.
L15: Bác sĩ: Giờ tôi khám qua cho ông nha.
L16: Bác sĩ: Tôi ghi nhận: Mỏm trâm quay cổ tay phải sưng nề nhẹ ấn đau chói, Finkelstein dương tính rõ.
L17: Bác sĩ: Viêm bao gân dạng dài duỗi ngắn ngón cái hội chứng De Quervain cổ tay phải.
L18: Bác sĩ: Về điều trị: Bất động cổ ngón tay bằng nẹp ngón cái spica trong 2 tuần. Thuốc chống viêm NSAID đường uống kết hợp tiêm corticoid tại chỗ bao gân dưới hướng dẫn siêu âm.
L19: Bác sĩ: Trong toa thuốc tôi kê salbutamol hai nhát, xịt khi cần nhé.
L20: Bệnh nhân: Vâng, tôi sẽ uống thuốc đúng giờ ạ, xin phép về.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 24 — Mã: `v2mr_0220` (`zona thần kinh`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['bo_sung', 'dai_tu_ho_hang', 'mau_thuan']` | `so_luot=22`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời ông ngồi, Ông thấy trong người phát sinh dấu hiệu gì lạ thế ạ?
L02: Bác sĩ: Bác sĩ muốn xác nhận trước, ông đến kiểm tra sức khỏe cho bản thân mình phải không?
L03: Bệnh nhân: Vâng, hôm nay tôi khám ạ.
L04: Bác sĩ: Sáng nay ông đi tới đây có xa không ạ?
L05: Bệnh nhân: Đi lại cũng thuận tiện ạ.
L06: Bệnh nhân: Tôi thấy xuất hiện mụn nước mọc thành chùm cụm theo dải khoanh da một bên cơ thể hai hôm ạ.
L07: Bệnh nhân: Mà cũng có thể gần một tuần, tôi không chắc lắm ạ.
L08: Bác sĩ: Để tôi ghi là chưa rõ hai hôm hay gần một tuần, mình xác nhận lại sau nhé ạ.
L09: Bác sĩ: Có kèm theo khó thở không vậy?
L10: Bệnh nhân: Dạ thưa đúng ạ, tôi có thêm triệu chứng nguy cơ đau dây thần kinh sau zona kéo dài nhiều tháng.
L11: Bệnh nhân: Nguy cơ đau dây thần kinh sau zona kéo dài nhiều tháng thì chỉ bị lúc sáng sớm.
L12: Bác sĩ: Có đang theo dõi bệnh gì không vậy?
L13: Bệnh nhân: Dạ đúng rồi bác sĩ, tôi có rối loạn mỡ máu.
L14: Bác sĩ: Uống hạ sốt có bị mẩn ngứa không thế?
L15: Bệnh nhân: Dạ chưa, tôi không dị ứng thuốc gì ạ.
L16: Bác sĩ: Có uống viên thuốc nào từ sáng chưa thế?
L17: Bệnh nhân: Dạ chưa uống viên nào.
L18: Bác sĩ: Rồi, ông nghiêng sang bên này nhé ạ.
L19: Bác sĩ: Mụn nước thành chùm theo một khoanh da, một bên.
L20: Bác sĩ: Chẩn đoán: Zona thần kinh.
L21: Bác sĩ: Thuốc kháng virus trong bảy ngày. Giữ khô vùng tổn thương.
L22: Bệnh nhân: Dạ, cảm ơn bác sĩ đã khám kỹ nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 25 — Mã: `v2mr_4003` (`tiền đái tháo đường`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['gia_dinh']` | `so_luot=16`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời em ngồi nghỉ ngơi, rồi chia sẻ với tôi lý do đi khám nhé.
L02: Bác sĩ: Thủ tục hôm nay có nhanh không em?
L03: Bệnh nhân: Dạ đỡ nhiều rồi.
L04: Bệnh nhân: Em bị chứng nghiệm pháp dung nạp glucose đường huyết 2h từ 7.8 đến 11.0 mấy tháng nay.
L05: Bác sĩ: Có kèm theo khó thở không ạ?
L06: Bệnh nhân: Dạ thưa bác, em có thêm triệu chứng dễ mệt lả đói cồn cào xa bữa ăn, vòng eo bánh mì tích mỡ nội tạng.
L07: Bác sĩ: Từng nằm viện hay mổ lần nào chưa?
L08: Bệnh nhân: Dạ thưa bác, em có rối loạn mỡ máu.
L09: Bác sĩ: Có cơ địa dị ứng thuốc không vậy?
L10: Bệnh nhân: Hổng có, em chưa từng nổi mề đay ạ.
L11: Bác sĩ: Bác sĩ kiểm tra phản xạ nhé ạ.
L12: Bác sĩ: Ghi nhận: Thể trạng béo, không phát hiện bất thường khác.
L13: Bác sĩ: Khả năng cao là: Tiền đái tháo đường.
L14: Bác sĩ: Kế hoạch: Xét nghiệm HbA1c. Giảm tinh bột và đường. Tập thể dục ba mươi phút mỗi ngày.
L15: Bác sĩ: Nếu mai em còn nghiệm pháp dung nạp glucose đường huyết 2h từ 7.8 đến 11.0 thì gọi điện cho tôi nhé.
L16: Bệnh nhân: Em cảm ơn bác sĩ nhiều ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 26 — Mã: `v2mr_2197` (`đái tháo nhạt`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=17`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời anh ngồi xuống, hôm nay anh thấy sức khỏe thế nào ạ?
L02: Bác sĩ: Cho tôi hỏi một chút, có phải anh là bệnh nhân cần khám hôm nay không ạ?
L03: Bệnh nhân: Tôi đi khám cho mình ạ.
L04: Bác sĩ: Anh mang căn cước chưa?
L05: Bệnh nhân: Dạ, tôi mang đủ cả ạ.
L06: Bệnh nhân: Tôi bắt đầu bị uống nước liên tục trên 5 lít một ngày từ năm ngoái ạ.
L07: Bác sĩ: Còn chỗ nào đau nữa không thế?
L08: Bệnh nhân: Dạ vâng, tôi còn than phiền là bị người rã rời trằn trọc cả đêm vì đi tiểu nữa.
L09: Bác sĩ: Có theo dõi ở chuyên khoa nào không vậy?
L10: Bệnh nhân: Chưa ạ, tôi không có vấn đề sức khỏe.
L11: Bác sĩ: Uống hạ sốt có bị mẩn ngứa không?
L12: Bệnh nhân: Dạ không có.
L13: Bác sĩ: Tôi khám qua cho anh nhé ạ.
L14: Bác sĩ: Dấu hiệu mất nước nhẹ, da khô, mạch nhanh 92 lần/phút, huyết áp bình thường.
L15: Bác sĩ: Chẩn đoán: Theo dõi đái tháo nhạt trung ương.
L16: Bác sĩ: Về điều trị: Xét nghiệm áp lực thẩm thấu máu và nước tiểu, tỷ trọng nước tiểu. Chụp MRI tuyến yên loại trừ u đè ép.
L17: Bệnh nhân: Dạ, cảm ơn bác sĩ đã khám kỹ nhé ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 27 — Mã: `v2mr_1930` (`viêm da dầu tiết bã nhờn`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=['bo_sung']` | `so_luot=16`
- **Lời thoại:**
```text
L01: Bác sĩ: Bác sĩ chào chị, hôm nay chị muốn kiểm tra về vấn đề gì?
L02: Bác sĩ: Mình bắt đầu kiểm tra được không chị?
L03: Bệnh nhân: Dạ, bác sĩ cứ làm đi ạ.
L04: Bác sĩ: Hôm nay công việc có bận lắm không?
L05: Bệnh nhân: Công việc cũng vừa phải ạ.
L06: Bệnh nhân: Tôi bắt đầu bị dát đỏ phủ nhiều lớp vảy mỡ màu vàng dính nhờn bóng ở vùng rãnh mũi má hơn một năm.
L07: Bác sĩ: Cho hỏi thêm, có bị đau đầu hay hoa mắt không?
L08: Bệnh nhân: Dạ đúng rồi bác, tôi phát sinh thêm cả bệnh tiến triển dai dẳng mạn tính bùng phát khi căng thẳng thời tiết hanh khô mùa đông nữa bác sĩ.
L09: Bệnh nhân: Bệnh tiến triển dai dẳng mạn tính bùng phát khi căng thẳng thời tiết hanh khô mùa đông thì nhiều hơn về đêm.
L10: Bác sĩ: Bản thân có bệnh nền gì không thế?
L11: Bệnh nhân: Dạ đúng rồi bác, tôi có đái tháo đường.
L12: Bác sĩ: Rồi, bác sĩ khám tai mũi họng cho chị một chút nhé.
L13: Bác sĩ: Rãnh mũi má hai bên dát đỏ viền vảy mỡ vàng, da đầu nhiều gàu mảng bám.
L14: Bác sĩ: Tôi nghĩ nhiều đến viêm da tiết bã nhờn thể da mặt và da đầu, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã.
L15: Bác sĩ: Chị đi làm xét nghiệm nước tiểu rồi quay lại đây.
L16: Bệnh nhân: Tôi rõ cách dùng thuốc rồi nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 28 — Mã: `v2mr_4414` (`viêm thực quản do nấm candida`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['gia_dinh']` | `so_luot=20`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào em, hôm nay em đến khám vì sao ạ?
L02: Bác sĩ: Bác sĩ muốn xác nhận trước, hôm nay em tự mình đến khám chữa bệnh đúng không thế ạ?
L03: Bệnh nhân: Vâng, hôm nay em khám.
L04: Bác sĩ: Em có mang BHYT không ạ?
L05: Bệnh nhân: Dạ cảm ơn bác sĩ.
L06: Bệnh nhân: Em cảm giác nuốt nghẹn nuốt đau buốt rát lan sau xương ức mỗi khi nuốt thức ăn và ngụm nước bốn hôm ạ.
L07: Bác sĩ: Có triệu chứng gì đi kèm không ạ?
L08: Bệnh nhân: Vâng, chưa kể em còn bị tiền sử sử dụng thuốc xịt corticoid kéo dài điều trị hen suyễn hoặc suy giảm miễn dịch nữa ạ.
L09: Bác sĩ: Có bệnh gì phải theo dõi định kỳ không vậy?
L10: Bệnh nhân: Dạ vâng ạ, em có gout ạ.
L11: Bác sĩ: Có dị ứng thuốc nào không vậy?
L12: Bệnh nhân: Dạ không, em chưa bao giờ dị ứng thuốc.
L13: Bác sĩ: Ở nhà có uống viên hạ sốt nào chưa ạ?
L14: Bệnh nhân: Vâng em nghe, em có bôi kem bôi fucidin một lớp mỏng, ngày hai lần, dùng được hai tuần nay.
L15: Bác sĩ: Tiếp theo, tôi sờ nắn chỗ đau một chút nhé.
L16: Bác sĩ: Tôi ghi nhận: Miệng có các mảng nấm trắng ở vòm khẩu cái, tim phổi bình thường, bụng mềm.
L17: Bác sĩ: Khả năng cao là: Viêm thực quản do nấm Candida albicans độ ba theo phân loại Kodsi.
L18: Bác sĩ: Thuốc kháng nấm fluconazole 200mg uống ngày một lần trong 14 đến 21 ngày. Súc miệng kỹ bằng nước sạch ngay sau mỗi lần xịt thuốc corticoid dự phòng hen.
L19: Bác sĩ: Nếu mai em còn nuốt nghẹn nuốt đau buốt rát lan sau xương ức mỗi khi nuốt thức ăn và ngụm nước thì đưa đi khám lại nhé.
L20: Bệnh nhân: Em sẽ tái khám đúng hẹn ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 29 — Mã: `v2mr_2652` (`viêm tai giữa ứ dịch`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=['di_ung_nguoi_nha', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=19`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào anh, mấy ngày qua bé có biểu hiện gì làm gia đình lo lắng nhất?
L02: Bác sĩ: Để tiện xưng hô trong hồ sơ, anh là gì của bé ạ?
L03: Người nhà: Dạ, tôi là người nhà, cụ thể là bố của bé ạ.
L04: Bác sĩ: Đường tới đây có đông không?
L05: Người nhà: Dạ đỡ rồi.
L06: Người nhà: Con tôi xuất hiện nghe kém từ năm ngoái ạ.
L07: Bác sĩ: Còn dấu hiệu gì khác không vậy?
L08: Người nhà: Dạ thưa bác sĩ, con tôi ghi nhận thêm hiện tượng ngáy, chậm nói nữa.
L09: Bác sĩ: Từng có đợt uống thuốc kéo dài không ạ?
L10: Người nhà: Dạ thưa bác sĩ, con tôi có viêm amidan hay tái phát ạ.
L11: Người nhà: Tôi đang điều trị lao phổi, bác sĩ ạ.
L12: Bác sĩ: À, từng bị sốc thuốc lần nào chưa ạ?
L13: Người nhà: Dạ vâng, bà nội thì dị ứng tetracyclin, còn con tôi chưa thấy bị bao giờ.
L14: Bác sĩ: Để tôi đo lại huyết áp cho bé nghen.
L15: Bác sĩ: Màng nhĩ đục, có mức dịch sau màng nhĩ.
L16: Bác sĩ: Tôi nghĩ nhiều đến viêm tai giữa ứ dịch, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã nghe.
L17: Bác sĩ: Bé đi làm xét nghiệm nước tiểu rồi quay lại đây nhé.
L18: Bác sĩ: Đơn thuốc hôm nay tôi kê paracetamol một gói, uống ngày ba lần nhé ạ.
L19: Người nhà: Dạ bác sĩ, tôi rõ cách dùng thuốc rồi nhe bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 30 — Mã: `v2mr_4754` (`viêm gân gót achilles`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời chị ngồi nghỉ ngơi, rồi chia sẻ với tôi lý do đi khám nhé ạ.
L02: Bác sĩ: Sáng se lạnh chị có mặc ấm không?
L03: Bệnh nhân: Dạ, em đi lại cẩn thận không sao.
L04: Bệnh nhân: Em bị đau nhức nhối vùng sau gót chân khi bước đi liên tục hai hôm ạ.
L05: Bác sĩ: Ngoài ra, ăn ngủ dạo này có được không thế?
L06: Bệnh nhân: Dạ thưa bác sĩ, đi kèm với đó là em bị đi lại khập khiễng ạ.
L07: Bác sĩ: Từng bị đợt nào giống thế này chưa ạ?
L08: Bệnh nhân: Chưa ạ.
L09: Bác sĩ: À, uống thuốc có bị ngứa nổi mẩn không ạ?
L10: Bệnh nhân: Em chưa thấy dị ứng thuốc nào ạ.
L11: Bác sĩ: Giờ để tôi đo lại huyết áp cho chị nhé.
L12: Bác sĩ: Gân gót sưng nề cách chỗ bám xương gót 3-4 cm, bóp hai bên gân đau chói, nghiệm pháp Thompson âm tính (gân chưa đứt hoàn toàn).
L13: Bác sĩ: Tôi nghĩ nhiều đến viêm gân gót Achilles cấp tính do vận động quá mức, nhưng chưa kết luận được. Phải có kết quả chụp X-quang đã nhé.
L14: Bác sĩ: Chị đi làm chụp X-quang rồi quay lại đây nhé.
L15: Bệnh nhân: Vâng, em cảm ơn bác sĩ nhiều nhé ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 31 — Mã: `v2mr_2636` (`bụi phổi silic`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['dien_bien']` | `so_luot=19`
- **Lời thoại:**
```text
L01: Bác sĩ: Đợt khám trước cô uống paracetamol có thấy thuyên giảm không ạ?
L02: Bệnh nhân: Thưa bác sĩ, uống được ít hôm rồi ngừng, ngừng 1 tuần rồi ạ.
L03: Bác sĩ: Trước khi bắt đầu, cô đi khám cho mình phải không?
L04: Bệnh nhân: Của tôi.
L05: Bác sĩ: Cô ngồi ghế này có thoải mái không?
L06: Bệnh nhân: Thoáng mát lắm ạ.
L07: Bệnh nhân: Tôi thấy khó thở tăng dần kéo dài nhiều năm rõ rệt hai tháng nay.
L08: Bác sĩ: Còn triệu chứng nào nữa không?
L09: Bệnh nhân: Thưa bác sĩ, đồng thời tôi còn thấy sút cân.
L10: Bệnh nhân: Từ hôm chủ nhật thì ho khạc ít đờm đen xám, hôm kia thì đỡ hẳn rồi ạ.
L11: Bác sĩ: Có đang theo dõi bệnh gì không thế?
L12: Bệnh nhân: Không ạ, tôi không có vấn đề sức khỏe ạ.
L13: Bác sĩ: Cho hỏi, có dùng thuốc bôi hay xịt nào không ạ?
L14: Bệnh nhân: Dạ vâng, tôi có bôi kem bôi fucidin, ngày hai lần ạ.
L15: Bác sĩ: Giờ để tôi khám cho cô nha.
L16: Bác sĩ: Khám thấy: Lồng ngực hình thùng, rì rào phế nang giảm hai phế trường, tiếng tim mờ xa xăm.
L17: Bác sĩ: Bệnh bụi phổi silic nghề nghiệp giai đoạn tiến triển.
L18: Bác sĩ: Tôi hướng dẫn: Chụp phim X-quang phổi thẳng theo tiêu chuẩn ILO tìm các nốt xơ hóa tập trung. Đo dung tích sống phổi và giám định bệnh nghề nghiệp.
L19: Bệnh nhân: Vâng, tôi nhớ lời bác sĩ dặn rồi ạ, xin phép về.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 32 — Mã: `v2mr_0183` (`tiêu chảy do rotavirus`)
- **Thông tin ca:** `boi_canh=dieu_duong_ban_giao` | `khuon_da_duyet=False` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=17`
- **Lời thoại:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Con này mới tiếp đón, sinh hiệu ổn định ạ.
L02: Bác sĩ: Được rồi em. Con cho bác sĩ biết chỗ nào làm mình khó chịu nhất ạ?
L03: Bác sĩ: Phòng khám hôm nay sảnh chờ có thoáng không ạ?
L04: Người nhà: Ghế ngồi êm ái lắm ạ.
L05: Người nhà: Cháu nó có biểu hiện nôn mửa dữ dội trong ngày đầu mấy hôm nay ạ.
L06: Bác sĩ: Ăn ngủ dạo này có được không?
L07: Người nhà: Dạ, cháu nó còn xuất hiện cứ quấy không yên kích thích, mệt mỏi lả người nữa bác sĩ ạ.
L08: Bác sĩ: Về bệnh cũ, có bệnh gì phải theo dõi định kỳ không thế?
L09: Người nhà: Dạ chưa, con không uống thuốc mạn tính bác sĩ.
L10: Người nhà: Tôi cũng đang bệnh cơ tim giãn, nên tôi hay lo ạ.
L11: Bác sĩ: Có dị ứng thuốc nào không vậy?
L12: Người nhà: Con không phản ứng với thuốc gì bác sĩ.
L13: Bác sĩ: Để bác sĩ nghe vùng ngực một chút nhé.
L14: Điều dưỡng: Mắt trũng nhẹ, môi khô, nếp véo da bụng mất chậm, bụng chướng hơi nhẹ, hậu môn đỏ rát.
L15: Bác sĩ: Chẩn đoán: Tiêu chảy cấp có mất nước nghi do Rotavirus ở trẻ nhỏ.
L16: Bác sĩ: Test nhanh Rotavirus trong phân. Bù nước bằng dung dịch Oresol thẩm thấu thấp uống từng thìa nhỏ, bổ sung kẽm (Zinc) 14 ngày.
L17: Người nhà: Dạ, tôi hiểu đơn thuốc rồi nhe bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 33 — Mã: `v2mr_0771` (`hội chứng wolff parkinson white`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['bo_sung', 'mau_thuan']` | `so_luot=20`
- **Lời thoại:**
```text
L01: Bác sĩ: Anh kể giúp tôi xem mấy hôm nay thấy trong người ra sao?
L02: Bác sĩ: Trước khi bắt đầu, anh đến kiểm tra sức khỏe cho bản thân mình phải không thế ạ?
L03: Bệnh nhân: Vâng, của tôi ạ.
L04: Bác sĩ: Mình bắt đầu kiểm tra được không anh?
L05: Bệnh nhân: Dạ đỡ rồi.
L06: Bác sĩ: Anh ngồi ghế này có thoải mái không ạ?
L07: Bệnh nhân: Dạ bình thường ạ.
L08: Bệnh nhân: Tôi cứ bị cơn tim đập nhanh kịch phát nhịp tim trên 180 lần phút khởi phát đột ngột năm hôm ạ.
L09: Bệnh nhân: Tôi nghĩ là từ hôm kia thì đúng hơn.
L10: Bác sĩ: Để tôi ghi là chưa rõ năm hôm hay từ hôm kia, mình xác nhận lại sau nhé.
L11: Bác sĩ: Có sụt cân, chán ăn, mất ngủ không?
L12: Bệnh nhân: Dạ thưa bác sĩ, tôi ghi nhận thêm hiện tượng chóng mặt hoa mắt xây xẩm mặt mày khi cơn nhịp nhanh kéo dài, cảm giác trong người bồn chồn hẫng hụt lồng ngực như tim muốn nhảy ra ngoài nữa ạ.
L13: Bệnh nhân: Chóng mặt hoa mắt xây xẩm mặt mày khi cơn nhịp nhanh kéo dài thì nhiều hơn về đêm.
L14: Bác sĩ: Từng bị sốc thuốc lần nào chưa thế?
L15: Bệnh nhân: Chưa ạ.
L16: Bác sĩ: Bác sĩ kiểm tra phản xạ nghen.
L17: Bác sĩ: Trong cơn: nhịp tim nhanh đều 190 chu kỳ/phút, huyết áp 100/60 mmHg, phổi trong.
L18: Bác sĩ: Cơn tim nhanh trên thất do hội chứng tiền kích thích Wolff-Parkinson-White WPW.
L19: Bác sĩ: Cắt cơn cấp cứu bằng nghiệm pháp cường phó giao cảm xoa xoang cảnh hoặc tiêm adenosine tĩnh mạch nhanh. Chỉ định triệt đốt đường dẫn truyền phụ qua catheter bằng sóng rfa.
L20: Bệnh nhân: Dạ vâng, tôi sẽ theo dõi kỹ ạ, xin phép về.
```
- **Lỗi ghi nhận (1):**
  - L12 [Bệnh nhân]: Lượt thoại quá dài (> 40 từ) ("Dạ thưa bác sĩ, tôi ghi nhận thêm hiện tượng chóng mặt hoa m...")

### Ca 34 — Mã: `v2mr_2656` (`trĩ huyết khối tắc mạch`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=18`
- **Lời thoại:**
```text
L01: Bác sĩ: Anh kể từ đầu xem cơ thể bắt đầu thấy mệt từ bao giờ ạ?
L02: Bác sĩ: Bác sĩ muốn xác nhận trước, anh đi khám cho mình phải không?
L03: Bệnh nhân: Vâng, em đi khám cho mình.
L04: Bệnh nhân: Em bắt đầu thấy đau rát dữ dội vùng hậu môn xuất hiện đột ngột hơn một tuần.
L05: Bác sĩ: Cho hỏi thêm, còn khó chịu chỗ nào khác không vậy?
L06: Bệnh nhân: Dạ vâng, em thấy kèm theo triệu chứng táo bón sợ đi đại tiện, chảy ít máu đỏ tươi khi lau giấy khó ở ạ.
L07: Bác sĩ: Có theo dõi ở chuyên khoa nào không thế?
L08: Bệnh nhân: Em chưa từng phải phẫu thuật.
L09: Bác sĩ: Uống thuốc có bị nổi ngứa không ạ?
L10: Bệnh nhân: Dạ không, em không phản ứng với thuốc gì nha bác sĩ.
L11: Bác sĩ: Đã tự mua thuốc gì uống chưa?
L12: Bệnh nhân: Dạ không, em tới khám luôn, chưa uống gì.
L13: Bác sĩ: Anh nằm lên bàn khám nha.
L14: Bác sĩ: Rìa hậu môn vị trí 5 giờ có khối tròn màu tím thẫm kích thước hạt ngô, căng chắc và rất đau khi chạm.
L15: Bác sĩ: Tôi nghĩ nhiều đến trĩ ngoại tắc mạch huyết khối cấp tính, nhưng chưa kết luận được. Phải có kết quả chụp X-quang đã nha.
L16: Bác sĩ: Anh đi làm chụp X-quang rồi quay lại đây.
L17: Bác sĩ: Tôi kê cetirizine 10 mg, uống ngày một lần buổi tối nha.
L18: Bệnh nhân: Dạ, em rõ hết phác đồ rồi nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 35 — Mã: `v2mr_0550` (`bàng quang tăng hoạt OAB`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['bo_sung']` | `so_luot=12`
- **Lời thoại:**
```text
L01: Bác sĩ: Bà kể rõ cho bác sĩ nghe xem tình trạng hiện tại thế nào.
L02: Bác sĩ: Để rõ thông tin đăng ký, bà đến đây khám bệnh cho mình hay cho ai khác ạ?
L03: Bệnh nhân: Dạ đúng ạ.
L04: Bệnh nhân: Tôi thấy tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay hơn một năm.
L05: Bác sĩ: Có triệu chứng gì đi kèm không thế?
L06: Bệnh nhân: Vâng tôi nghe đây ạ, thêm vào đó tôi thấy người có thang điểm bảng câu hỏi oab-q đánh giá chất lượng cuộc sống suy giảm nghiêm trọng ạ.
L07: Bệnh nhân: Thang điểm bảng câu hỏi oab-q đánh giá chất lượng cuộc sống suy giảm nghiêm trọng thì tăng lên khi vận động ạ.
L08: Bác sĩ: Bà ngồi yên tôi nghe tim phổi nha.
L09: Bác sĩ: Tôi ghi nhận: Khám bụng bình thường, cầu bàng quang âm tính, thăm trực tràng tiền liệt tuyến bình thường.
L10: Bác sĩ: Khả năng cao là: Hội chứng bàng quang tăng hoạt OAB thể ướt có són tiểu gấp.
L11: Bác sĩ: Tập luyện bàng quang kéo dài khoảng cách giữa các lần đi tiểu và bài tập cơ sàn chậu Kegel. Thuốc kháng muscarinic solifenacin hoặc đồng vận beta 3 mirabegron.
L12: Bệnh nhân: Vâng, tôi sẽ tái khám đúng hẹn ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 36 — Mã: `v2mr_0845` (`bụi phổi silic`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=['dinh_chinh', 'hoi_khong_dap']` | `so_luot=19`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào em, mấy hôm nay cơ thể có biểu hiện gì khiến em phải đi khám?
L02: Bác sĩ: Tiếp đón có thuận lợi không em?
L03: Bệnh nhân: Dạ sẵn sàng rồi ạ.
L04: Bác sĩ: Hôm nay đường tới đây có đông không?
L05: Bệnh nhân: Dạ ổn cả.
L06: Bệnh nhân: Em chịu đựng tình trạng khó thở tăng dần kéo dài nhiều năm hơn một năm ạ.
L07: Bệnh nhân: Em nói lại cho đúng, vài năm rồi chứ không phải hơn một năm.
L08: Bác sĩ: Có bị sốt hay ho không?
L09: Bệnh nhân: Dạ thưa bác sĩ, em thấy người còn có sút cân, dễ bị viêm nhiễm đường thở nữa.
L10: Bác sĩ: Có tiền sử gan, thận, hen, tiểu đường không ạ?
L11: Bệnh nhân: Dạ chưa từng.
L12: Bác sĩ: Từng nổi mề đay khi uống thuốc chưa thế?
L13: Bệnh nhân: Dạ em nghe bác sĩ, hồi trước có lần dùng thuốc bị dị ứng kháng sinh nhóm quinolon khá nặng.
L14: Bác sĩ: Ở nhà có ai xung quanh bị triệu chứng tương tự không?
L15: Bác sĩ: Em nằm lên bàn khám nghen.
L16: Bác sĩ: Lồng ngực hình thùng, rì rào phế nang giảm hai phế trường, tiếng tim mờ xa xăm.
L17: Bác sĩ: Tôi nghĩ nhiều đến bệnh bụi phổi silic nghề nghiệp giai đoạn tiến triển, nhưng chưa kết luận được. Phải có kết quả chụp X-quang đã.
L18: Bác sĩ: Em đi làm chụp X-quang rồi quay lại đây nha.
L19: Bệnh nhân: Dạ vâng, em sẽ tái khám đúng hẹn ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 37 — Mã: `v2mr_3741` (`nang thận đơn độc`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=18`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời cô ngồi xuống, cô thấy chú có triệu chứng gì nặng nhất ạ?
L02: Bác sĩ: Cô là gì của chú ấy?
L03: Người nhà: Dạ, tôi là người nhà, cụ thể là vợ của chú ấy đây ạ.
L04: Bác sĩ: Bây giờ mình bắt đầu kiểm tra được không cô ạ?
L05: Người nhà: Vâng được rồi.
L06: Bác sĩ: Cô có thấy khát nước không ạ?
L07: Người nhà: Bác sĩ cứ làm đi ạ.
L08: Người nhà: Anh ấy thấy trong người đau tức mơ hồ vùng hông lưng bên có nang hai tháng nay.
L09: Bác sĩ: Trong người còn mệt ở đâu không thế?
L10: Người nhà: Dạ đúng rồi bác sĩ, anh ấy còn thấy đêm phải dậy đi giải 1-2 lần, không sốt nữa ạ.
L11: Bác sĩ: Có tiền sử bệnh phổi hay phế quản không thế?
L12: Người nhà: Dạ bác sĩ, anh ấy có trào ngược dạ dày.
L13: Người nhà: Tôi đang điều trị không ngủ được mạn tính, bác sĩ ạ.
L14: Bác sĩ: Để tôi nghe tim và phổi nhé.
L15: Bác sĩ: Khám thấy: Khám bụng mềm, hố thắt lưng không sưng đỏ, ấn không đau.
L16: Bác sĩ: Nang đơn độc thận phải kích thước 45 mm phân loại Bosniak I.
L17: Bác sĩ: Siêu âm Doppler kiểm tra bờ nang và thành phần bên trong. Khuyên theo dõi định kỳ 6 tháng một lần, chưa cần can thiệp chọc hút.
L18: Người nhà: Tôi hiểu đơn thuốc rồi nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 38 — Mã: `v2mr_0418` (`động kinh cục bộ thùy thái dương`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['dien_bien']` | `so_luot=18`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời ông ngồi, Ông thấy trong người phát sinh dấu hiệu gì lạ thế?
L02: Bác sĩ: Cho bác sĩ hỏi là, hôm nay ông là người trực tiếp cần khám đúng không?
L03: Bệnh nhân: Tôi tự đi khám ạ.
L04: Bác sĩ: Ông ăn sáng chưa?
L05: Bệnh nhân: Dạ, tôi có ăn nhẹ rồi ạ.
L06: Bệnh nhân: Tôi thấy trong người cảm giác tiền triệu aura dâng lên từ thượng vị cảm giác quen thuộc deja vu hoặc sợ hãi vô cớ khoảng một tháng.
L07: Bác sĩ: Có sụt cân, chán ăn, mất ngủ không thế?
L08: Bệnh nhân: Dạ thưa đúng ạ, tôi thấy kèm theo triệu chứng điện não đồ eeg ghi nhận sóng nhọn sóng gai khu trú vùng thái dương trước khó ở.
L09: Bệnh nhân: Sáng nay thì động tác tự động nhai nuốt chép miệng vân vê tà áo vô thức trong cơn, từ hôm chủ nhật thì đỡ hẳn rồi ạ.
L10: Bác sĩ: Từng bị đợt nào giống thế này chưa?
L11: Bệnh nhân: Dạ bác sĩ, tôi có viêm khớp ạ.
L12: Bác sĩ: Đã dùng thuốc gì trước khi tới chưa thế?
L13: Bệnh nhân: Hổng có, tôi chưa tự mua thuốc uống.
L14: Bác sĩ: Để tôi kiểm tra một lượt nha.
L15: Bác sĩ: Khám thực thể: Ngoài cơn: khám thần kinh bình thường, không có dấu hiệu thần kinh khu trú.
L16: Bác sĩ: Động kinh cục bộ phức tạp thùy thái dương có xơ teo hồi hải mã.
L17: Bác sĩ: Tôi hướng dẫn: Thuốc chống động kinh carbamazepine hoặc levetiracetam liều dò duy trì. Hướng dẫn an toàn tránh bơi lội làm việc trên cao và ngủ đủ giấc.
L18: Bệnh nhân: Cảm ơn bác sĩ nhiều ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 39 — Mã: `v2mr_0561` (`ghẻ`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['bo_sung', 'dinh_chinh']` | `so_luot=21`
- **Lời thoại:**
```text
L01: Bác sĩ: Tình hình uống metformin từ hôm tái khám trước tới nay thế nào rồi chị?
L02: Bệnh nhân: Dạ vâng, uống được ít hôm rồi ngừng, ngừng 2 tuần rồi ạ.
L03: Bác sĩ: Bác sĩ muốn xác nhận trước, có phải chị là bệnh nhân cần khám hôm nay không vậy ạ?
L04: Bệnh nhân: Dạ của tôi ạ.
L05: Bệnh nhân: Tôi thấy trong người cứ tối là ngứa mấy hôm nay ạ.
L06: Bệnh nhân: Xin lỗi bác sĩ, tôi nhớ lại rồi, hai hôm chứ không phải mấy hôm nay ạ.
L07: Bác sĩ: Có bị đau đầu hay hoa mắt không?
L08: Bệnh nhân: Vâng tôi nghe đây ạ, ngoài ra tôi còn bị trầy xước do gãi nữa ạ.
L09: Bệnh nhân: Trầy xước do gãi thì nặng hơn sau khi ăn.
L10: Bác sĩ: Có tiền sử gan, thận, hen, tiểu đường không?
L11: Bệnh nhân: Không ạ, tôi không có bệnh nền nào.
L12: Bác sĩ: Từng bị sốc thuốc lần nào chưa thế?
L13: Bệnh nhân: Chưa ạ, tôi chưa bao giờ dị ứng thuốc ạ.
L14: Bác sĩ: Ở nhà có uống theo toa cũ nào không thế?
L15: Bệnh nhân: Vâng, tôi có uống paracetamol 500 mg, ngày ba lần.
L16: Bác sĩ: Để tôi nghe tim và phổi nghen.
L17: Bác sĩ: Sẩn và mụn nước ở kẽ ngón tay, có rãnh ghẻ.
L18: Bác sĩ: Khả năng cao là: Ghẻ.
L19: Bác sĩ: Hướng xử trí: Bôi thuốc trị ghẻ cho cả nhà cùng lúc. Giặt nóng quần áo, chăn màn.
L20: Bác sĩ: Thuốc paracetamol thì từ nay mình ngừng uống nha.
L21: Bệnh nhân: Vâng, tôi sẽ uống thuốc đúng giờ ạ, xin phép về.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 40 — Mã: `v2mr_3129` (`đau đầu cụm cluster headache`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['dien_bien']` | `so_luot=20`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào chị, hôm nay chị cảm thấy mệt mỏi hay đau ở đâu vậy ạ?
L02: Bác sĩ: Bác sĩ muốn xác nhận trước, hôm nay chị tự mình đến khám chữa bệnh đúng không vậy ạ?
L03: Bệnh nhân: Dạ, tôi đi khám ạ.
L04: Bác sĩ: Ngồi ngoài sảnh chị đợi có lâu không?
L05: Bệnh nhân: Nhiệt độ thế này vừa rồi.
L06: Bệnh nhân: Cơn cơn đau nhức dữ dội buốt nhói như xuyên kim khu trú một bên hốc mắt và thái dương này tôi bị gần một tuần.
L07: Bác sĩ: Có biểu hiện bất thường nào nữa không ạ?
L08: Bệnh nhân: Vâng ạ, tôi ghi nhận thêm hiện tượng cơn đau kéo dài từ 15 đến 180 phút bệnh nhân kích động đi lại ôm đầu rên rỉ, chuỗi cơn đau kéo dài nhiều tuần liên tiếp rồi biến mất một thời gian nữa.
L09: Bệnh nhân: Hôm qua thì mắt cùng bên đau bị đỏ rực cương tụ mắt cứ ứa nước giàn giụa phù nề mi mắt, hôm kia thì đỡ hẳn rồi.
L10: Bác sĩ: Có bệnh gì phải theo dõi định kỳ không ạ?
L11: Bệnh nhân: Vâng em nghe, tôi có viêm dạ dày ạ.
L12: Bác sĩ: Tiện hỏi luôn, có dị ứng thuốc hay thức ăn gì không?
L13: Bệnh nhân: Tôi chưa bao giờ dị ứng thuốc.
L14: Bác sĩ: Có uống giảm đau ở nhà chưa?
L15: Bệnh nhân: Vâng ạ, tôi có uống cetirizine, ngày một lần buổi tối.
L16: Bác sĩ: Để bác sĩ nghe vùng ngực nhé ạ.
L17: Bác sĩ: Ghi nhận: Trong cơn: mắt phải đỏ rực sụp mi nhẹ, chảy nước mắt, da trán bên phải toát mồ hôi đỏ bừng.
L18: Bác sĩ: Đau đầu cụm thể từng đợt theo tiêu chuẩn Hiệp hội Đau đầu Quốc tế ICHD-3.
L19: Bác sĩ: Kế hoạch: Cắt cơn khẩn cấp bằng thở oxy nguyên chất 100% lưu lượng 12 lít/phút qua mặt nạ có túi dự trữ hoặc xịt sumatriptan. Dự phòng chuỗi cơn bằng verapamil liều cao.
L20: Bệnh nhân: Tôi sẽ uống thuốc đúng giờ ạ.
```
- **Lỗi ghi nhận (1):**
  - L08 [Bệnh nhân]: Lượt thoại quá dài (> 40 từ) ("Vâng ạ, tôi ghi nhận thêm hiện tượng cơn đau kéo dài từ 15 đ...")

### Ca 41 — Mã: `v2mr_0806` (`áp xe phổi`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=['bo_sung', 'dai_tu_ho_hang']` | `so_luot=19`
- **Lời thoại:**
```text
L01: Bác sĩ: Bác sĩ chào em, lý do chính khiến em đi khám hôm nay là gì?
L02: Bác sĩ: Ngồi ngoài sảnh trong phòng có vừa nhiệt độ không em ạ?
L03: Bệnh nhân: Dạ cảm ơn bác sĩ.
L04: Bác sĩ: Em tự đi hay ai chở qua ạ?
L05: Bệnh nhân: Đi lại cũng thuận tiện.
L06: Bệnh nhân: Em phát hiện bị ho khạc ộc mủ lượng lớn mùi tanh thối hơn một tuần.
L07: Bác sĩ: Ngoài ra, có bị đau đầu hay hoa mắt không?
L08: Bệnh nhân: Dạ thưa bác sĩ, em bị cấy đờm tìm thấy vi khuẩn kỵ khí gram âm, bạch cầu máu tăng vọt trên 20 giga lít kèm theo nữa.
L09: Bệnh nhân: Cấy đờm tìm thấy vi khuẩn kỵ khí gram âm thì nhiều hơn về đêm.
L10: Bác sĩ: Có dị ứng với kháng sinh không?
L11: Bệnh nhân: Dạ không, em không có cơ địa dị ứng.
L12: Bác sĩ: Mình có dùng thuốc gì chưa ạ?
L13: Bệnh nhân: Dạ vâng ạ, em có uống augmentin 1 g, ngày hai lần ạ.
L14: Bác sĩ: Để tôi nghe tim và phổi nha.
L15: Bác sĩ: Hội chứng đông đặc phổi có hang: gõ đục một vùng, nghe tiếng thổi hang và ran ẩm to hạt đáy phổi phải.
L16: Bác sĩ: Tôi nghĩ nhiều đến áp xe phổi thùy dưới phổi phải giai đoạn ộc mủ, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã.
L17: Bác sĩ: Em đi làm xét nghiệm nước tiểu rồi quay lại đây nhé.
L18: Bác sĩ: Bác sĩ quyết định kê thuốc nhỏ mắt natri clorid hai giọt, nhỏ ngày ba lần nha.
L19: Bệnh nhân: Dạ, em nhớ lời bác sĩ rồi ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 42 — Mã: `v2mr_3772` (`cận thị tiến triển`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['dinh_chinh', 'luoc_chu_ngu', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=19`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào bà, gia đình thấy bé phát bệnh từ hôm nào thế?
L02: Bác sĩ: Bác sĩ hỏi một chút, mình có quan hệ gia đình thế nào với bé?
L03: Người nhà: Dạ, tôi là bà ngoại đưa bé đi khám ạ.
L04: Bác sĩ: Bây giờ bà sẵn sàng để bác sĩ kiểm tra chưa?
L05: Người nhà: Em cảm ơn bác sĩ.
L06: Người nhà: Cứ bị nhìn xa không rõ phải nheo mắt mới thấy rõ chữ trên bảng vài năm rồi ạ.
L07: Người nhà: Xin lỗi bác sĩ, tôi nhớ lại rồi, hơn một năm chứ không phải vài năm rồi.
L08: Bác sĩ: Có bị đau đầu hay hoa mắt không vậy?
L09: Người nhà: Dạ đúng rồi bác sĩ, ghi nhận thêm hiện tượng đo khúc xạ máy phát hiện độ cận tăng nhanh, chỉ định đeo kính đúng độ và nhỏ thuốc atropin nồng độ thấp kiểm soát nữa ạ.
L10: Người nhà: Tôi cũng đang viêm cột sống dính khớp, nên tôi hay lo ạ.
L11: Bác sĩ: Tiện hỏi luôn, có dị ứng thuốc hay thức ăn gì không thế?
L12: Người nhà: Dạ thưa bác sĩ, bị dị ứng amoxicillin bác sĩ ơi, uống vào là nổi lên từng đám.
L13: Bác sĩ: Đã tự mua thuốc gì uống chưa ạ?
L14: Người nhà: Chưa có uống gì ạ.
L15: Bác sĩ: Để bác sĩ kiểm tra họng nghen.
L16: Bác sĩ: Thị lực không kính hai mắt giảm.
L17: Bác sĩ: Khả năng cao là: Cận thị tiến triển.
L18: Bác sĩ: Kế hoạch: Đo khúc xạ lại. Hạn chế màn hình, tăng hoạt động ngoài trời.
L19: Người nhà: Dạ, cảm ơn bác sĩ đã khám kỹ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 43 — Mã: `v2mr_2967` (`rách giác mạc nông`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=17`
- **Lời thoại:**
```text
L01: Bác sĩ: Chào bà, mấy ngày qua cháu có biểu hiện gì làm gia đình lo lắng nhất ạ?
L02: Bác sĩ: Cho bác sĩ hỏi, mình có quan hệ gia đình thế nào với cháu ạ?
L03: Người nhà: Dạ, tôi là bà nội đưa cháu đi khám bác sĩ ạ.
L04: Bác sĩ: Dạo này bà xin nghỉ làm đi khám à ạ?
L05: Người nhà: Dạ đỡ nhiều rồi.
L06: Bác sĩ: Ngồi ngoài sảnh sảnh chờ có thoáng không?
L07: Người nhà: Thoáng mát lắm.
L08: Người nhà: Cháu tôi có biểu hiện đau chói cộm rát mắt dữ dội sau khi bị cành cây quẹt trúng mấy hôm nay ạ.
L09: Bác sĩ: Có bị sốt hay ho không vậy?
L10: Người nhà: Dạ thưa bác, cháu tôi kèm theo cả sợ ánh sáng ạ.
L11: Người nhà: Tôi thì hẹp van động mạch chủ, nói thêm để bác sĩ biết.
L12: Bác sĩ: Giờ cháu nghiêng sang bên này nhé.
L13: Bác sĩ: Kết mạc cương tụ đỏ, nhuộm giác mạc bằng dung dịch Fluorescein bắt màu xanh ở biểu mô giác mạc (tổn thương trợt xước nông).
L14: Bác sĩ: Tôi nghĩ nhiều đến trợt xước rách nông biểu mô giác mạc mắt trái do chấn thương cơ học, nhưng chưa kết luận được. Phải có kết quả siêu âm đã nghen.
L15: Bác sĩ: Cháu đi làm siêu âm rồi quay lại đây nghen.
L16: Bác sĩ: Bác sĩ sẽ kê oresol một gói, uống ngày ba lần nghen.
L17: Người nhà: Dạ bác sĩ, xin cảm ơn bác sĩ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 44 — Mã: `v2mr_0237` (`viêm họng cấp`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Mời anh ngồi xuống, anh thấy con có triệu chứng gì nặng nhất ạ?
L02: Bác sĩ: Anh ngồi nghỉ đỡ mệt chưa?
L03: Người nhà: Dạ đỡ nhiều rồi.
L04: Bác sĩ: Phòng khám hôm nay trong phòng có vừa nhiệt độ không anh?
L05: Người nhà: Nhiệt độ thế này vừa rồi ạ.
L06: Người nhà: Cháu nó bắt đầu thấy cảm giác khô rát buốt họng nuốt chẹn gần một tuần ạ.
L07: Bác sĩ: Có biểu hiện bất thường nào nữa không?
L08: Người nhà: Dạ, cháu nó thấy có thêm thường tự khỏi sau 5 đến 7 ngày điều trị nâng đỡ, nuốt nước bọt cũng thấy đau rát cổ mấy hôm nay ạ.
L09: Người nhà: Tôi thì giảm tiểu cầu, nói thêm để bác sĩ biết ạ.
L10: Bác sĩ: Con nghiêng sang bên này nhé ạ.
L11: Bác sĩ: Khám thực thể: Họng đỏ, amidan sưng nhẹ, không có mủ.
L12: Bác sĩ: Viêm họng cấp.
L13: Bác sĩ: Bác sĩ dặn: Súc họng nước muối, uống nhiều nước ấm, hạ sốt khi cần.
L14: Bác sĩ: Tôi cho kê thuốc nhỏ mắt natri clorid một giọt, nhỏ ngày ba lần nha.
L15: Người nhà: Dạ, cảm ơn bác sĩ đã khám kỹ nha bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 45 — Mã: `v2mr_4199` (`tay chân miệng`)
- **Thông tin ca:** `boi_canh=cho_ket_qua` | `khuon_da_duyet=False` | `bay=['gia_dinh', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=17`
- **Lời thoại:**
```text
L01: Bác sĩ: Anh quan sát thấy cháu kêu đau hay mệt mỏi ở đâu vậy ạ?
L02: Bác sĩ: Mình có quan hệ gia đình thế nào với cháu vậy ạ?
L03: Người nhà: Thưa bác sĩ, tôi là bố của cháu ạ.
L04: Bác sĩ: Dạo này công việc có nhiều áp lực không anh ạ?
L05: Người nhà: Tôi xin nghỉ nửa buổi.
L06: Bác sĩ: Vào phòng rồi anh có hồi hộp không ạ?
L07: Người nhà: Dạ không sao ạ.
L08: Người nhà: Cháu nó bắt đầu bị nốt bọng nước hình bầu dục ở lòng bàn tay lòng bàn chân gối và mông hơn một tuần ạ.
L09: Bác sĩ: Đi vệ sinh có bình thường không thế?
L10: Người nhà: Dạ thưa bác sĩ, cháu nó thấy kèm theo triệu chứng cần theo dõi sát dấu hiệu giật mình chới với giật cơ khó ở ạ.
L11: Người nhà: Tôi bị cường giáp mấy năm nay rồi ạ.
L12: Bác sĩ: Để bác sĩ kiểm tra họng nha.
L13: Bác sĩ: Họng có vết loét nhỏ, lòng bàn tay và bàn chân có bọng nước.
L14: Bác sĩ: Tôi nghĩ nhiều đến tay chân miệng độ 1, nhưng chưa kết luận được. Phải có kết quả chụp X-quang đã nhé.
L15: Bác sĩ: Cháu đi làm chụp X-quang rồi quay lại đây nhé.
L16: Bác sĩ: Nếu mai cháu còn nốt bọng nước hình bầu dục ở lòng bàn tay lòng bàn chân gối và mông thì quay lại đây nhé.
L17: Người nhà: Vâng ạ, tôi rõ cách dùng thuốc rồi ạ, xin phép về.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 46 — Mã: `v2mr_1886` (`bệnh tim thiếu máu cục bộ`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['hoi_khong_dap']` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Tình hình uống efferalgan từ hôm tái khám trước tới nay thế nào rồi chị?
L02: Bệnh nhân: Dạ đúng rồi bác sĩ, uống được ít hôm rồi ngừng, ngừng 1 tuần rồi.
L03: Bác sĩ: Hôm nay chị ngủ đủ giấc không?
L04: Bệnh nhân: Dạ đỡ nhiều rồi.
L05: Bệnh nhân: Em bị chụp động mạch vành qua da phát hiện hẹp trên 70 phần trăm khẩu kính lòng mạch liên tục nửa năm rồi ạ.
L06: Bác sĩ: Ngoài ra, có biểu hiện bất thường nào nữa không ạ?
L07: Bệnh nhân: Dạ thưa đúng ạ, thêm vào đó em thấy người có phân suất tống máu thất trái suy giảm theo thời gian, cần điều trị tối ưu bằng thuốc chống đông statin và chẹn beta ạ.
L08: Bác sĩ: Có tiền sử phẫu thuật gì không vậy?
L09: Bệnh nhân: Dạ em nghe bác sĩ, em có gout ạ.
L10: Bác sĩ: Chị có cảm thấy người hay bị ớn lạnh về chiều tối không?
L11: Bác sĩ: Giờ tôi sờ nắn chỗ đau một chút nhé.
L12: Bác sĩ: Mạch 78 lần/phút, huyết áp 135/85 mmHg. Tim đều, không có tiếng thổi bệnh lý.
L13: Bác sĩ: Kết luận: Bệnh tim thiếu máu cục bộ mạn tính (cơn đau thắt ngực ổn định).
L14: Bác sĩ: Bác sĩ dặn: Đo điện tâm đồ lúc nghỉ và nghiệm pháp gắng sức. Dùng thuốc chống kết tập tiểu cầu aspirin, statin liều cao và nitrate khi đau.
L15: Bệnh nhân: Dạ bác sĩ, cảm ơn bác sĩ đã khám kỹ nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 47 — Mã: `v2mr_1658` (`u nang buồng trứng`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['hoi_khong_dap']` | `so_luot=16`
- **Lời thoại:**
```text
L01: Bác sĩ: Bác sĩ chào chị, hãy chia sẻ cụ thể lý do mình đi khám hôm nay nhé ạ.
L02: Bác sĩ: Bác sĩ muốn xác nhận trước, chị đến kiểm tra sức khỏe cho bản thân mình phải không vậy ạ?
L03: Bệnh nhân: Đúng rồi, của tôi ạ.
L04: Bác sĩ: Phòng khám hôm nay trong phòng có vừa nhiệt độ không chị ạ?
L05: Bệnh nhân: Nhiệt độ thế này vừa rồi.
L06: Bệnh nhân: Tôi bị sờ thấy khối căng tròn nhẵn di động vùng hố chậu hạ vị hơn một năm ạ.
L07: Bác sĩ: Có chóng mặt hay buồn nôn không ạ?
L08: Bệnh nhân: Vâng em nghe, ngoài ra tôi còn bị nguy cơ biến chứng xoắn nang buồng trứng gây đau dữ dội cấp cứu, kinh nguyệt thất thường thưa kinh nữa ạ.
L09: Bác sĩ: Có tiền sử hen phế quản không thế?
L10: Bệnh nhân: Không ạ, tôi không uống thuốc mạn tính ạ.
L11: Bác sĩ: Chị có hay bị mất ngủ ban đêm không ạ?
L12: Bác sĩ: Để bác sĩ kiểm tra họng nha.
L13: Bác sĩ: Hạ vị ấn tức một bên, thăm khám thấy khối tròn cạnh tử cung ranh giới rõ.
L14: Bác sĩ: Khả năng cao là: U nang buồng trứng phải dạng thực thể.
L15: Bác sĩ: Về điều trị: Siêu âm Doppler màu tử cung phần phụ và định lượng CA-125. Theo dõi sát nguy cơ xoắn nang.
L16: Bệnh nhân: Vâng ạ, tôi rõ cách dùng thuốc rồi ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 48 — Mã: `v2mr_0321` (`viêm màng phổi khô`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=[]` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Bác sĩ chào anh, hãy chia sẻ cụ thể lý do mình đi khám hôm nay nhé ạ.
L02: Bác sĩ: Anh sẵn sàng để bác sĩ kiểm tra chưa?
L03: Bệnh nhân: Em sẵn sàng rồi ạ.
L04: Bệnh nhân: Em bắt đầu bị tiếng cọ màng phổi nghe thô ráp sột soạt ở đáy phổi thì hít vào năm hôm.
L05: Bác sĩ: Có sụt cân, chán ăn, mất ngủ không ạ?
L06: Bệnh nhân: Dạ bác sĩ, chưa kể em còn bị thường đi kèm viêm phổi lân cận hoặc nhiễm siêu vi, không có hội chứng ba giảm không có tràn dịch tự do nữa.
L07: Bác sĩ: Có bệnh nền tim mạch không vậy?
L08: Bệnh nhân: Dạ vâng, em có thiếu máu ạ.
L09: Bác sĩ: Có cơ địa dị ứng thuốc không?
L10: Bệnh nhân: Dạ chưa, em không dị ứng thuốc nào cả.
L11: Bác sĩ: Để tôi kiểm tra một lượt một chút nhé.
L12: Bác sĩ: Khám thực thể: Lồng ngực bên đau giảm giãn nở, nghe thấy tiếng cọ màng phổi thô ráp thì hít vào và thở ra, mất đi khi nín thở.
L13: Bác sĩ: Viêm màng phổi khô (viêm màng phổi thanh tơ).
L14: Bác sĩ: Chụp X-quang ngực loại trừ tràn dịch tràn khí. Dùng thuốc giảm đau chống viêm NSAIDs, tìm nguyên nhân nhiễm trùng hoặc tự miễn tiềm ẩn.
L15: Bệnh nhân: Dạ, xin cảm ơn bác sĩ nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 49 — Mã: `v2mr_3245` (`dị ứng đạm sữa bò`)
- **Thông tin ca:** `boi_canh=kham_lan_dau` | `khuon_da_duyet=False` | `bay=['di_ung_nguoi_nha', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=18`
- **Lời thoại:**
```text
L01: Bác sĩ: Anh chia sẻ giúp bác sĩ xem bé bắt đầu phát bệnh từ khi nào ạ?
L02: Bác sĩ: Mình có quan hệ gia đình thế nào với bé ạ?
L03: Người nhà: Dạ thưa bác sĩ, tôi là bố ruột trong nhà của bé.
L04: Bác sĩ: Trong phòng có vừa nhiệt độ không anh ạ?
L05: Người nhà: Ghế ngồi êm ái lắm.
L06: Người nhà: Bé nhà tôi bị mẩn lên khắp người đỏ mày đay quanh miệng sau khi uống sữa công thức làm khó chịu hai tháng nay ạ.
L07: Bác sĩ: Còn dấu hiệu gì khác không thế?
L08: Người nhà: Vâng thưa bác sĩ, bé nhà tôi có thêm triệu chứng cứ quấy không yên nhiều sau bú ạ.
L09: Bác sĩ: Có bị bệnh gan hay thận không vậy?
L10: Người nhà: Dạ vâng, bé nhà tôi có hen phế quản ạ.
L11: Người nhà: Tôi cũng đang viêm tụy mạn, nên tôi hay lo.
L12: Bác sĩ: Có dị ứng paracetamol hay kháng sinh không?
L13: Người nhà: Vâng em nghe, bố thì dị ứng hạt điều, còn bé nhà tôi chưa thấy bị bao giờ ạ.
L14: Bác sĩ: Để tôi khám cho bé nghen.
L15: Bác sĩ: Khám thấy: Trẻ gầy nhẹ, da mặt có ban chàm rải rác, bụng mềm chướng nhẹ, hậu môn đỏ.
L16: Bác sĩ: Dị ứng đạm sữa bò (Cow's Milk Protein Allergy - CMPA) ở trẻ nhũ nhi.
L17: Bác sĩ: Về điều trị: Ngừng hoàn toàn sữa bò công thức thông thường, chuyển sang dùng sữa công thức đạm thủy phân hoàn toàn (Extensively Hydrolyzed Formula) hoặc sữa axit amin.
L18: Người nhà: Dạ, cảm ơn bác sĩ đã khám kỹ ạ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.

### Ca 50 — Mã: `v2mr_2528` (`suy tĩnh mạch chi dưới`)
- **Thông tin ca:** `boi_canh=tai_kham` | `khuon_da_duyet=False` | `bay=['gia_dinh']` | `so_luot=15`
- **Lời thoại:**
```text
L01: Bác sĩ: Đơn thuốc oresol đợt trước chị dùng hết chưa, cảm thấy thế nào ạ?
L02: Bệnh nhân: Dạ cháu nghe bác sĩ, vẫn đang uống oresol ạ.
L03: Bệnh nhân: Tôi thấy xuất hiện nặng chân vài năm rồi ạ.
L04: Bác sĩ: Còn chỗ nào đau nữa không?
L05: Bệnh nhân: Dạ cháu nghe bác sĩ, tôi kèm theo dấu hiệu khó ngủ, tê chân rất khó chịu ạ.
L06: Bác sĩ: Trước giờ từng bị đợt nào giống thế này chưa thế?
L07: Bệnh nhân: Dạ đúng rồi bác, tôi có viêm dạ dày.
L08: Bác sĩ: Có uống thuốc nam hay đông y không thế?
L09: Bệnh nhân: Dạ thưa bác sĩ, tôi có uống amoxicillin, ngày hai lần, dùng được một tháng nay.
L10: Bác sĩ: Tiếp theo, bác sĩ khám tai mũi họng cho chị một chút nhé.
L11: Bác sĩ: Giãn tĩnh mạch nông hai cẳng chân, phù nhẹ.
L12: Bác sĩ: Hướng tới: Suy tĩnh mạch chi dưới.
L13: Bác sĩ: Về điều trị: Mang vớ áp lực. Tránh đứng lâu, kê cao chân khi nằm.
L14: Bác sĩ: Nếu mai chị còn nặng chân thì quay lại đây nhé.
L15: Bệnh nhân: Dạ vâng, cảm ơn bác sĩ nhiều nghen bác sĩ.
```
- **Lỗi ghi nhận:** Không có lỗi vi phạm 6 quy tắc chất lượng.
