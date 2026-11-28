# Tự kiểm lâm sàng 11 ca demo

> **Tự kiểm bởi AI (Claude), KHÔNG thay bác sĩ duyệt.** Ngày 28/11/2026.
> Đây là AI tự soát lại kịch bản mình viết. Kết quả có thể sai hoặc thiếu. Chưa có bác sĩ nào duyệt; phiếu cho bác sĩ ở `PHIEU-BAC-SI-DUYET.md` (trạng thái: CHƯA DUYỆT).

## Đã kiểm những gì

Với mỗi ca: (1) liều so với khoảng liều chuẩn người lớn hoặc theo cân nặng ở trẻ; (2) thuốc kê có đụng dị ứng đã khai không, kể cả dị ứng chéo; (3) chẩn đoán có khớp triệu chứng, khám, xét nghiệm trong lời thoại không; (4) kế hoạch theo dõi và dấu hiệu cần đi cấp cứu có hợp lý không; (5) đáp án `DAP-AN.md` có khớp lời thoại không (số, thuốc, ai nói gì).

Mức đánh giá: **Lỗi** (đã sửa) · **Nên xem** (không sai rõ, nhưng bác sĩ có thể muốn đổi) · **Ổn**.

## Tóm tắt

| Ca | Kết quả | Thay đổi |
|---|---|---|
| `3-ca-moi/ca_01` | Ổn | Không |
| `3-ca-moi/ca_02` | Nên xem (1 điểm) | Không |
| `3-ca-moi/ca_03` | Nên xem (1 điểm) | Không |
| `3-ca-moi/ca_04` | Ổn | Không |
| `3-ca-moi/ca_05` | **Lỗi: liều paracetamol vượt 15 mg/kg/lần** | Sửa cân nặng 15 → 17 kg, đọc lại `ca_05.mp3`, cập nhật DAP-AN |
| `3-ca-moi/ca_06` | Nên xem (1 điểm) | Không |
| `4-ca-kho/ca_01` | Đã sửa khi viết; còn 1 điểm nên xem | Bisoprolol giữ nguyên thay vì tăng liều |
| `4-ca-kho/ca_02` | Đã sửa khi viết; còn 1 điểm nên xem | Thêm khám đầu (không bầm, không sưng) |
| `4-ca-kho/ca_03` | Nên xem (2 điểm) | Không |
| `4-ca-kho/ca_04` | Nên xem (1 điểm) | Không |
| `4-ca-kho/ca_05` | Nên xem (2 điểm) | Không |

## Chi tiết từng ca

### `3-ca-moi/ca_01` — Tăng huyết áp, amlodipin 5 → 10 mg
- Liều: amlodipin 10 mg/ngày là liều tối đa thường dùng. Ổn.
- Mục tiêu < 130/80, xét nghiệm mỡ máu, đường, thận, điện tâm đồ, hẹn 2 tuần: hợp lý.
- Không có thuốc đụng dị ứng (không dị ứng). Ổn.

### `3-ca-moi/ca_02` — Viêm amidan cấp, dị ứng amoxicillin
- Azithromycin 500 mg ngày 1, 250 mg ngày 2–5: phác đồ người lớn thường dùng. Paracetamol 500 mg cách ≥ 6 giờ: ổn.
- Dị ứng amoxicillin (mẩn ngứa toàn thân, phải cấp cứu): không kê penicillin; cũng không kê cephalosporin. Ổn.
- **Nên xem:** bác sĩ lấy test nhanh liên cầu ("15 phút có kết quả") nhưng kê kháng sinh ngay trong cùng lượt, không chờ kết quả. Với Centor 4/4 (sốt, mủ amidan, hạch đau, không ho) kê theo kinh nghiệm vẫn chấp nhận được, nhưng bác sĩ có thể muốn sửa câu thành "có kết quả dương tính thì uống".

### `3-ca-moi/ca_03` — Đau thượng vị sau diclofenac
- Test hơi thở HP làm **trước** khi dùng PPI: đúng thứ tự. Ngừng diclofenac, chuyển paracetamol: đúng.
- **Nên xem:** omeprazol 20 mg × 2 lần/ngày × 4 tuần cao hơn liều liền loét chuẩn (20 mg × 1 lần/ngày, 4–8 tuần); liều 2 lần/ngày thường dùng trong phác đồ diệt HP. Không sai về an toàn, để bác sĩ quyết có hạ về 1 lần/ngày không.

### `3-ca-moi/ca_04` — Đái tháo đường type 2, thêm gliclazid
- Metformin 850 mg × 2 (chức năng thận bình thường), gliclazid MR 30 mg sáng, atorvastatin 10 mg: trong khoảng chuẩn.
- Dặn hạ đường huyết, không bỏ bữa, soi đáy mắt, HbA1c sau 3 tháng: hợp lý. Ổn.

### `3-ca-moi/ca_05` — Trẻ 3 tuổi viêm mũi họng cấp — **Lỗi đã sửa**
- **Lỗi:** bản cũ trẻ nặng 15 kg, paracetamol 250 mg/lần = 16,7 mg/kg/lần, vượt khoảng chuẩn 10–15 mg/kg/lần.
- **Sửa:** đổi cân nặng thành **17 kg** (250 mg ≈ 14,7 mg/kg/lần; tối đa 4 gói = 1 g/ngày ≈ 59 mg/kg/ngày, dưới 60–75 mg/kg/ngày). Sửa `ca_05.txt` ("mười bảy cân"), đọc lại `ca_05.mp3` bằng cùng script, sửa dòng S và P trong `3-ca-moi/DAP-AN.md`.
- Các điểm khác: nhịp thở 30 lần/phút ở trẻ 3 tuổi là bình thường (ngưỡng thở nhanh 1–5 tuổi là ≥ 40), không kháng sinh cho viêm mũi họng virus: đúng. Dị ứng penicillin của bố không gán cho trẻ: đúng.

### `3-ca-moi/ca_06` — Đau lưng cơ học, dị ứng ibuprofen
- Paracetamol 1 g × 3 lần/ngày (3 g/ngày), eperison 50 mg × 3 lần/ngày: trong khoảng chuẩn.
- **Nên xem:** mề đay do ibuprofen hay phản ứng chéo với các NSAID khác (ức chế COX-1). Lời thoại nói "không cho thuốc kháng viêm nhóm đó", đáp án ghi tránh "NSAID nhóm ibuprofen (ibuprofen, diclofenac…)". Bác sĩ có thể muốn ghi rõ "tránh mọi NSAID". Paracetamol 1 g/lần hiếm khi gây phản ứng chéo ở người mề đay do NSAID, nhưng có thể cân nhắc 500 mg/lần.

### `4-ca-kho/ca_01` — Suy tim EF giảm + rung nhĩ
- Apixaban 5 mg × 2: đúng tiêu chí (72 tuổi < 80, 65 kg > 60, creatinin 92 µmol/L < 133). Không cần giảm liều.
- Ngừng aspirin khi đã chống đông và không có bệnh mạch vành/stent mới: hợp lý.
- Spironolacton 25 mg với kali 4,2, creatinin 92: an toàn; hẹn xét nghiệm lại kali, thận sau 1 tuần: đúng.
- Furosemid 80 mg × 3 ngày rồi về 40 mg, ăn nhạt, hạn chế dịch, cân hằng ngày: hợp lý.
- **Đã sửa khi viết:** bản nháp đầu tăng bisoprolol 2,5 → 5 mg ngay lúc đang ứ dịch. Khuyến cáo không tăng chẹn beta khi đang mất bù, nên đổi thành "giữ nguyên, hết phù mới tính tăng".
- **Nên xem:** lời thoại không hỏi tiền sử bệnh mạch vành hay đặt stent, là lý do duy nhất để giữ aspirin cùng apixaban.

### `4-ca-kho/ca_02` — Ngã do hạ đường huyết, 3 người nói
- Ngừng sulfonylurea ở người cao tuổi bị hạ đường huyết nặng: đúng. Giữ metformin 500 mg × 2 và chờ chức năng thận: hợp lý (ngừng nếu eGFR < 30).
- Dị ứng cefalexin (phù mạch): không có thuốc nào kê đụng dị ứng.
- X-quang khung chậu, hông dù khám chưa nghĩ gãy: hợp lý ở người 78 tuổi.
- **Đã sửa khi viết:** thêm "Đầu không có vết bầm, không sưng" vào lượt khám, vì người cao tuổi ngã không rõ cơ chế cần được khám đầu.
- **Nên xem:** bệnh nhân không nhớ rõ lúc ngã. Nếu nghi có đập đầu thì bác sĩ có thể muốn chụp CT sọ não (tuổi ≥ 65 là yếu tố nguy cơ cao). Lời thoại hiện quy cho hạ đường huyết và không chụp CT.

### `4-ca-kho/ca_03` — Gút cấp, Nam Bộ
- Prednisolon 30 mg/ngày × 5 ngày: trong khuyến cáo (30–35 mg × 3–5 ngày). Không dùng NSAID vì tiền sử loét và đến muộn; thêm omeprazol khi dùng corticoid: hợp lý.
- Allopurinol bị loại hẳn sau phản ứng da bóng nước, tróc da: đúng.
- **Nên xem (1):** febuxostat sau phản ứng da nặng với allopurinol hiếm khi phản ứng chéo nhưng vẫn cần thận trọng, và cần cân nhắc nguy cơ tim mạch. Lời thoại chỉ nói "tính dùng" (dự định).
- **Nên xem (2):** HA 150/90 đang dùng amlodipin 5 mg; lời thoại hẹn đo lại. Bác sĩ có thể cân nhắc losartan (có tác dụng hạ axit uric nhẹ) khi tái khám. Không đổi trong kịch bản.

### `4-ca-kho/ca_04` — Đợt cấp hen, Huế
- Prednisolon 40 mg × 5 ngày: đúng khuyến cáo (40–50 mg × 5–7 ngày). Dùng lại ICS/LABA, salbutamol khi cần, hẹn 1 tuần, dấu hiệu cấp cứu: hợp lý.
- Phản ứng aspirin gây khó thở: tránh aspirin và NSAID; paracetamol ≤ 500 mg/lần đúng với khuyến cáo cho người hen nhạy cảm aspirin.
- **Nên xem:** lời thoại không nói hàm lượng ống budesonid/formoterol (ví dụ 160/4,5) và không có số đo lại sau khí dung. Đáp án yêu cầu bản ghi **không** tự điền hàm lượng.

### `4-ca-kho/ca_05` — Khám trước mổ túi mật, 3 người nói
- Ngừng aspirin dự phòng tiên phát 7 ngày trước mổ, xét nghiệm công thức máu, men gan, bilirubin, đông máu vì có cơn sốt: hợp lý. Dị ứng co-trimoxazol ghi cho gây mê; không thuốc nào kê đụng dị ứng.
- **Nên xem (1):** aspirin dự phòng tiên phát ở người 52 tuổi không có bệnh tim mạch đã biết có chỉ định yếu; bác sĩ có thể muốn ghi "cân nhắc không dùng lại".
- **Nên xem (2):** uống rượu hằng ngày 3–4 chén: lời thoại dặn "cố bớt" và báo gây mê (nguy cơ hội chứng cai quanh mổ). Paracetamol 500 mg khi đau ở người uống rượu đều nên giữ tổng liều thấp (≤ 2–3 g/ngày); lời thoại không nêu tổng liều tối đa.

## Kiểm đáp án so với lời thoại

- Đã đối chiếu từng số, liều, thời gian và người nói trong `3-ca-moi/DAP-AN.md` và `4-ca-kho/DAP-AN.md` với `.txt`. Ngoài cân nặng `ca_05` (đã sửa ở cả hai nơi), không thấy chỗ lệch.

## Việc còn lại

- Một bác sĩ thật cần đọc, đánh dấu và ký `PHIEU-BAC-SI-DUYET.md`. Trước khi có chữ ký, mọi tài liệu phải ghi "chưa có bác sĩ duyệt".
