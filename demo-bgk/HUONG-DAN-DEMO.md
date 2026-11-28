# Hướng dẫn demo MediTrace cho ban giám khảo

> Toàn bộ dữ liệu ở đây là tổng hợp (không có bệnh nhân thật). Âm thanh là giọng máy VieNeu-TTS, không phải giọng người.
>
> **Trạng thái duyệt lâm sàng: CHƯA DUYỆT, chờ bác sĩ.** Chưa có bác sĩ nào duyệt các ca. Phiếu in cho bác sĩ: `PHIEU-BAC-SI-DUYET.md` (11 ca của `3-ca-moi/` và `4-ca-kho/`). Bản tự kiểm của AI (không thay bác sĩ): `TU-KIEM-LAM-SANG.md`. Khi trình bày, chỉ nói "kịch bản đã được AI tự soát, đang chờ bác sĩ duyệt".

## Đã chạy trước (28/11 trưa) — ra bản nháp trong vài giây

11 ca (`3-ca-moi/ca_01…06`, `4-ca-kho/ca_01…05`) đã cho Qwen3-4B chạy thật một lần trên HoaiDuc; đầu ra khâu trích được giữ trong bộ đệm của dịch vụ. Khi thả đúng tệp **`.txt`** của các ca này rồi tạo bản nháp, hệ thống lấy kết quả đã chạy trước (không cần GPU), nên ra rất nhanh — tài khoản nào cũng vậy.

- Chỉ áp dụng cho **`.txt` giữ nguyên**: sửa lời thoại hoặc thả **`.mp3`** (lời chép khác bản gốc) thì mô hình chạy lại, mất khoảng 1–2 phút.
- Mô hình được giữ sẵn trong GPU 240 phút sau lần dùng cuối, nên lần chạy lại không phải chờ nạp.
- Nếu BGK hỏi: "kết quả này do chính mô hình tại chỗ chạy trước, hệ thống giữ lại để demo không phải chờ; thả lời thoại mới thì mô hình chạy thật trước mặt BGK".

## Bộ nên dùng: `3-ca-moi/` (28/11/2026)

6 ca viết lại cho giống buổi khám ngoại trú thật: chỉ Bác sĩ và Bệnh nhân (riêng `ca_05` là mẹ kể bệnh cho con), không điều dưỡng, mạch hỏi bệnh theo thứ tự lý do khám → bệnh sử → tiền sử, thuốc, dị ứng → khám → chẩn đoán → kế hoạch. Mỗi ca dài 75–100 giây, có `.txt` và `.mp3`. Đáp án, bẫy và SOAP mong đợi nằm ở `3-ca-moi/DAP-AN.md`. Ca 2 người nói không có hai lượt liền nhau của cùng một người, nên gợi ý vai xen kẽ đúng cả ca khi tải `.mp3`.

3 ca cho buổi demo 5 phút:
1. **`ca_01`**: tái khám tăng huyết áp. "Đau ngực thì không", tai biến là của bố, amlodipin tăng từ 5 lên 10 mg.
2. **`ca_06`** (giọng Nam Bộ): đau lưng. "À hông, chủ nhật", "tê chân cũng hổng có", dị ứng ibuprofen nên kế hoạch phải tránh thuốc kháng viêm nhóm này.
3. **`ca_05`**: mẹ kể bệnh con 3 tuổi. Đính chính "hôm qua → hôm kia", dị ứng penicillin là của bố, không phải của cháu. Khi tải `.mp3`, đổi các lượt "Bệnh nhân" sang Người nhà (phím 3), đúng lúc để nói "máy gợi ý, bác sĩ quyết".

Dự phòng: `ca_02` (viêm amidan, dị ứng amoxicillin, "hai hôm… à không, bốn hôm").

## Bộ khó: `4-ca-kho/` (28/11/2026)

5 ca dài 2–2,5 phút, mỗi ca 4–6 bẫy đan vào nhau. Đáp án, từng bẫy và SOAP mong đợi ở `4-ca-kho/DAP-AN.md`.

| Ca | Tình huống | Người nói | Bẫy chính |
|---|---|---|---|
| `ca_01` | Bác 72 tuổi suy tim + rung nhĩ | BS, BN | Ngừng aspirin, furosemid gấp đôi 3 ngày rồi về cũ, thêm spironolacton, bisoprolol "chưa tăng"; "uống đều" rồi thú nhận bỏ lợi tiểu; cân "64 → 65" |
| `ca_02` | Bà 78 tuổi ngã do hạ đường huyết | BS, BN, NN | Bà "có ngất đâu" và con gái "gọi mãi mới thưa"; bà chối dị ứng, con gái sửa (cefalexin, sưng môi); insulin là của con gái, đột quỵ là của chồng; 2,8 / 6,1 / 7,8 |
| `ca_03` | Gút cấp (giọng Nam Bộ) | BS, BN | "Ba bữa, à hông, năm bữa… cả tuần rồi"; allopurinol gây bóng nước, tróc da; gút của ba, sỏi thận của anh hai; febuxostat chỉ là dự định |
| `ca_04` | Đợt cấp hen (giọng Huế) | BS, BN | "Xịt đều lắm" rồi "hết thuốc cả tuần ni"; aspirin làm "thở không được"; hen của mạ, ung thư phổi của bọ; "không đau ngực" nhưng "tức ngực" |
| `ca_05` | Khám trước mổ sỏi túi mật | BS, BN, NN | Mổ là tuần sau; vợ sửa sốt 38 °C, dị ứng biseptol, rượu "tối nào cũng ba, bốn chén"; ngừng aspirin 7 ngày trước mổ |

2 ca khó nên dùng cho demo (nếu còn thời gian sau 3 ca ở trên, hoặc thay `ca_05`/`ca_06`):
1. **`4-ca-kho/ca_01`**: đa thuốc, mỗi thuốc một số phận (ngừng, tăng tạm, mới, giữ). Ca 2 người nên gợi ý vai xen kẽ đúng cả ca khi tải `.mp3`. Chỉ vào danh sách thuốc trong bản nháp: aspirin phải nằm ở "đã ngừng", spironolacton chỉ ở kế hoạch, bisoprolol vẫn 2,5 mg.
2. **`4-ca-kho/ca_02`**: 3 người nói, hai lời kể mâu thuẫn và dị ứng bị chối rồi được người nhà sửa. Khi tải `.mp3` phải đổi các lượt con gái sang **NN** (phím 3). Dùng `.txt` (Cách B) nếu thiếu thời gian.

Lưu ý ASR: xem mục "ASR còn nghe sai" trong `4-ca-kho/DAP-AN.md`. Hai ca đề xuất nghe đúng gần hết số và phủ định; `ca_04` (Huế) bị nhận kém, nên dùng `.txt`. Muốn chắc từng con số thì dùng `.txt`.

Hai thư mục cũ (`1-ca-huan-luyen/`, `2-ca-bay/`) giữ lại làm dự phòng.

## Cách dùng

1. Bấm **Ca khám mới**, mở tab **Lời thoại**.
2. **Cách A (cho thấy nhận dạng giọng nói):** kéo-thả tệp `.mp3` vào khung Lời thoại (hoặc bấm **Tải tệp âm thanh**). Chờ khoảng 30–60 giây.
   - Máy chủ chưa tách giọng nên mọi lượt hiện "Chưa rõ vai" kèm gợi ý xen kẽ Bác sĩ ↔ Bệnh nhân. Bấm **Áp dụng … vai gợi ý để bác sĩ kiểm lại**, rồi sửa các lượt sai bằng nút BS/BN/NN (phím 1/2/3). Đây cũng là lúc nói với BGK: "máy chỉ gợi ý, bác sĩ quyết".
   - Ca có điều dưỡng hoặc người nhà (phần lớn `ca_XX`) sẽ phải sửa vài lượt, nên dùng ca bẫy cho cách này.
3. **Cách B (chắc chắn, nhanh):** kéo-thả tệp `.txt` cùng tên vào khung Lời thoại. Vai đã ghi sẵn, không cần gán.
4. **Tạo mẫu → Bản nháp hồ sơ lâm sàng (Qwen3-4B, tại chỗ)**. Chờ 1–3 phút. Mở tab **Bệnh án SOAP**, chỉ các cảnh báo và câu trích lời thoại.
5. Thử bấm Chép/In/Xuất **trước khi ký**: bị khóa. Ký duyệt xong mới dùng được. Đó là minh chứng "bác sĩ phê duyệt trước khi dùng hồ sơ".

Thư mục:
- `1-ca-huan-luyen/`: 9 ca lấy từ bộ huấn luyện v2 (`ca_01` đến `ca_09`), mỗi ca có `.txt` và `.mp3` (bác sĩ, điều dưỡng, bệnh nhân, người nhà mỗi vai một giọng).
- `2-ca-bay/`: 16 ca bẫy (`bay_01` đến `bay_16`), có `.txt` và `.mp3`.

## 3 ca nên dùng cho buổi demo 5 phút

1. **`ca_06`** (ca huấn luyện, khoảng 70 giây): một người kể, có đính chính thời gian, sửa liều thuốc, câu hỏi dị ứng không được trả lời và thuốc bị ngừng. Dễ theo dõi từ đầu đến cuối.
2. **`bay_12`** (ca bẫy): lượt bệnh nhân dồn nhiều thông tin; dị ứng ibuprofen, thuốc panadol và "không buồn nôn" nằm giữa lượt dài. Lớp cảnh báo bắt đúng 6/6 bản sai, rất rõ ràng khi bỏ sót dị ứng.
3. **`bay_13`** (ca bẫy, giọng Nam Bộ): "bả hổng có ói", thông tin dị ứng tôm cua là của người con chứ không phải của mẹ. Lớp cảnh báo bắt đúng 5/5 bản sai. Dự phòng: `bay_01` (đổi thuốc huyết áp, 5/6).

## Ca huấn luyện (`1-ca-huan-luyen/`)

Cột "điều BGK nên thấy" tóm từ chính kịch bản; chưa có kết quả đối chiếu giữa đầu ra của mô hình và các ý này cho riêng bộ 9 ca. Kịch bản gốc là tổng hợp nên có vài lượt lạc đề (ví dụ kê thuốc không liên quan chẩn đoán), đó là chủ ý để thử hệ thống.

| Tệp | Tình huống lâm sàng | Điều BGK nên thấy |
|---|---|---|
| `ca_01.mp3` / `.txt` | Chị khám bìu to một bên (điều dưỡng, bác sĩ, bệnh nhân). | Bệnh nhân đính chính thời gian: từ "hai tháng nay" thành "vài năm". Không dị ứng thuốc. Bác sĩ hướng tới tràn dịch màng tinh hoàn bên phải, chỉ định siêu âm Doppler bìu, hẹn phẫu thuật. |
| `ca_02.mp3` / `.txt` | Bà nội đưa cháu 8 tháng đi khám mắt lác (điều dưỡng, bác sĩ, người nhà). | Thông tin của cháu (lác trong, viêm tai giữa tái diễn, chưa từng phát ban) phải tách khỏi thông tin của bà ("tôi đang điều trị viêm đại tràng mạn"). Chẩn đoán lác trong bẩm sinh, hẹn đo khúc xạ và soi đáy mắt. Lượt 19 (salbutamol) không liên quan chẩn đoán, xem hệ thống xử lý ra sao. |
| `ca_03.mp3` / `.txt` | Chồng kể bệnh vợ ho kéo dài; vợ nói ngược về thời gian. | Hai người nói khác nhau ("mấy tháng nay" và "nửa năm"), bác sĩ ghi "chưa rõ". Tiền sử người nhà (bố loạn thị, chồng bụi phổi) không được ghi cho bệnh nhân. Sốt đã đỡ. Hướng lao phổi AFB dương tính, chuyển chuyên khoa Lao. |
| `ca_04.mp3` / `.txt` | Người nhà kể về người bệnh gầy sút, mâu thuẫn thời gian. | "Khoảng một tháng" và "vài năm" được ghi là chưa rõ. Bệnh của người nhà (polyp đại tràng, đau đầu mạn tính) không thuộc về bệnh nhân. Bác sĩ nghĩ nhiều đến suy dinh dưỡng nặng nhưng chưa kết luận, chờ xét nghiệm nước tiểu. |
| `ca_05.mp3` / `.txt` | Bố kể bệnh con gái: tăng lympho kéo dài, hạch cổ nách. | Mâu thuẫn "từ năm ngoái" và "khoảng một tháng". Bướu giáp là của bố. Thuốc nhỏ mắt natri clorid đã ngừng 3 tuần. Hướng bạch cầu lympho mạn CLL giai đoạn sớm, theo dõi và chờ. |
| `ca_06.mp3` / `.txt` | Chị sốt kéo dài, nghi hội chứng màng não (có điều dưỡng). | Bệnh nhân đính chính "năm hôm" thành "hơn một tuần"; sửa liều amoxicillin 250 thành 500 mg ngày ba lần; câu hỏi dị ứng được trả lời lạc đề; bác sĩ cho ngừng amoxicillin. Kết luận hội chứng màng não nghi do virus, chọc dò dịch não tủy, nhập viện. |
| `ca_07.mp3` / `.txt` | Chồng kể bệnh vợ: tiết dịch niệu đạo (bác sĩ, người nhà, bệnh nhân). | Mâu thuẫn "gần một tuần" và "hai hôm". Triệu chứng hôm kia, đêm qua đã đỡ. Chưa từng dị ứng; paracetamol 500 mg khi cần. Bác sĩ nghĩ đến viêm niệu đạo không do lậu cầu, doxycycline 7 ngày. |
| `ca_08.mp3` / `.txt` | Con gái kể bệnh mẹ: đau bụng chuyển hố chậu phải. | Mâu thuẫn "bốn hôm" và "từ hôm kia". Con gái tự nói đang điều trị viêm đại tràng (không phải của mẹ). Lượt 16 (metformin) và lượt 17 (câu điều kiện) cần được ghi đúng là kế hoạch/giả định. Chẩn đoán viêm ruột thừa cấp, mổ nội soi cấp cứu. |
| `ca_09.mp3` / `.txt` | Chú khám lichen xơ teo vùng sinh dục ngoài (có điều dưỡng). | Bệnh nhân đính chính "mấy tháng" thành "nửa năm"; không dị ứng kháng sinh; không dùng thuốc thường xuyên. Chẩn đoán lichen xơ teo mạn tính, bôi clobetasol theo phác đồ hạ bậc. |

## Ca bẫy (`2-ca-bay/`)

Mỗi ca bẫy có đáp án sạch và nhiều bản ghi sai cố ý (từ `thi-nghiem/bo-bay-tay/ra/ca_bay.jsonl`). Số bắt đúng lấy từ `ra/ket_qua_luat.json` (lớp cảnh báo dạng luật chạy trên lời thoại gốc; tổng 66/91 bản sai bắt đúng, có 120 cảnh báo thừa trên bản sạch). Chưa có kết quả đối chiếu cho mô hình trích xuất Qwen3-4B trên bộ này, và nội dung lâm sàng chưa có bác sĩ duyệt.

| Tệp | Tình huống lâm sàng | Điều BGK nên thấy |
|---|---|---|
| `bay_01.mp3` / `.txt` | Chóng mặt tư thế, đổi thuốc huyết áp (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: giữ 'một tuần' dù đã sửa thành mười ngày; ghi amlodipin vẫn đang dùng; ghi 'không dị ứng penicillin' (lấy chữ 'Không' đầu câu); ghi huyết áp đứng 150/90; ghi như bệnh nhân đã ngất và vào viện; ghi 'có đau ngực'. Lớp cảnh báo bắt đúng 5/6 bản sai. |
| `bay_02.mp3` / `.txt` | Trẻ sốt ho, mẹ cũng ốm (Bắc; người kể: mẹ) | Lỗi cố ý cài vào bản ghi sai: ghi cháu nôn ba lần; ghi cháu dị ứng aspirin; ghi cháu có nôn; ghi sốt cao nhất 38,5 độ; ghi như đã sốt quá ba ngày; bỏ sót dị ứng aspirin của bố. Lớp cảnh báo bắt đúng 5/6 bản sai. |
| `bay_03.mp3` / `.txt` | Đau hố chậu, phủ định kép (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: ghi đau bên phải; giữ 'bên phải' dù đã sửa; ghi có buồn nôn; ghi kinh không đều (đọc sai phủ định kép); ghi chắc chắn đang mang thai; ghi bệnh nhân đã mổ ruột thừa. Lớp cảnh báo bắt đúng 3/6 bản sai. |
| `bay_04.mp3` / `.txt` | Đau gối, giọng Huế, kể hộ (Huế; người kể: con gái) | Lỗi cố ý cài vào bản ghi sai: ghi gối vẫn đang sưng; ghi mẹ bị tiểu đường; ghi bệnh nhân có tiểu đường; bịa tên thuốc là meloxicam; ghi đau gối trái. Lớp cảnh báo bắt đúng 3/5 bản sai. |
| `bay_05.mp3` / `.txt` | Đái tháo đường, bẫy số liệu (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: ghi 1,25 thay cho 12,5; ghi đang tiêm insulin; ghi phát hiện ba tháng (bản y tá ghi nhầm); ghi đang hút một bao/ngày; ghi có tê tay; ghi metformin 1000 mg (liều mới của kế hoạch) vào thuốc đang dùng. Lớp cảnh báo bắt đúng 4/6 bản sai. |
| `bay_06.mp3` / `.txt` | Ho đờm, hỏi gộp và hỏi không đáp (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: ghi 'không dị ứng thuốc' dù câu hỏi không được trả lời; ghi có sốt và khó thở từ câu 'Có ạ'; ghi đang sốt; ghi đã kê kháng sinh; ghi có khó thở. Lớp cảnh báo bắt đúng 3/5 bản sai. |
| `bay_07.mp3` / `.txt` | Suy tim, nhiều thuốc (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: ghi fluoxetin thay furosemid; ghi kali đang dùng; ghi chân phải nhiều hơn; ghi có dị ứng thuốc; ghi bisoprolol 5 mg; bỏ sót omeprazol. Lớp cảnh báo bắt đúng 3/6 bản sai. |
| `bay_08.mp3` / `.txt` | Hay quên, hai người kể mâu thuẫn (Bắc; người kể: con gái) | Lỗi cố ý cài vào bản ghi sai: chỉ ghi 'không uống rượu', bỏ lời con gái; ghi người nhà hay quên; ghi MMSE 28/30; ghi ba tuần; ghi chắc chắn sa sút trí tuệ. Lớp cảnh báo bắt đúng 3/5 bản sai. |
| `bay_09.mp3` / `.txt` | Ho kéo dài, lao cũ (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: ghi đang mắc lao phổi; ghi chắc chắn lao phổi tái phát; ghi viêm phổi như đã chẩn đoán xác định; ghi có ra mồ hôi đêm; bịa con số 5 kg; ghi đã chuyển chương trình chống lao. Lớp cảnh báo bắt đúng 5/6 bản sai. |
| `bay_10.mp3` / `.txt` | Trẻ đau tai, đổi bên (Bắc; người kể: mẹ) | Lỗi cố ý cài vào bản ghi sai: giữ 'tai phải'; ghi viêm tai giữa phải; ghi cháu đang sốt; ghi cháu đang uống kháng sinh; ghi đã kê azithromycin; bỏ sót dị ứng amoxicillin. Lớp cảnh báo bắt đúng 4/6 bản sai. |
| `bay_11.mp3` / `.txt` | Tiểu buốt, đính chính ngược (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: giữ 'năm ngày' (bản bị bỏ); giữ dị ứng cephalexin; ghi có sốt; ghi fosfomycin 3 mg; ghi đau lưng bên trái; ghi đang uống kháng sinh. Lớp cảnh báo bắt đúng 4/6 bản sai. |
| `bay_12.mp3` / `.txt` | Đau đầu, lượt dồn thông tin (Bắc; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: bỏ sót dị ứng ibuprofen (nằm giữa lượt dồn); bỏ sót panadol; ghi có nhìn mờ; ghi bệnh nhân bị đau nửa đầu do mẹ kể (gán nhầm); ghi paracetamol 10 g; bỏ sót 'không buồn nôn'. Lớp cảnh báo bắt đúng 6/6 bản sai. |
| `bay_13.mp3` / `.txt` | Nam Bộ: bả, hổng, bữa giờ (Nam Bộ; người kể: con trai) | Lỗi cố ý cài vào bản ghi sai: đọc 'hổng có ói' thành có nôn; ghi mẹ dị ứng tôm cua; ghi amlodipin đang dùng đều; ghi trầy chân phải; ghi bệnh nhân đã yếu tay chân. Lớp cảnh báo bắt đúng 5/5 bản sai. |
| `bay_14.mp3` / `.txt` | Nghệ Tĩnh: nỏ, chi, mô (Nghệ Tĩnh; người kể: bệnh nhân) | Lỗi cố ý cài vào bản ghi sai: không hiểu 'nỏ', ghi có phân đen; ghi có uống rượu; giữ 'mười điếu'; ghi đang uống diclofenac; ghi bệnh nhân bị loét dạ dày; ghi chắc chắn loét dạ dày. Lớp cảnh báo bắt đúng 4/6 bản sai. |
| `bay_15.mp3` / `.txt` | Nam Bộ: ổng, hổng phải hổng (Nam Bộ; người kể: vợ) | Lỗi cố ý cài vào bản ghi sai: đọc 'hổng phải hổng sốt' thành không sốt; ghi bệnh nhân đang điều trị lao; ghi nhịp thở 12 lần/phút; ghi ran nổ đáy phổi trái; ghi bệnh nhân có bệnh mạn tính; ghi amoxicillin clavulanat 1 mg. Lớp cảnh báo bắt đúng 5/6 bản sai. |
| `bay_16.mp3` / `.txt` | Bắc quê: u, thầy (Bắc quê; người kể: con gái) | Lỗi cố ý cài vào bản ghi sai: ghi bệnh nhân bị nhồi máu cơ tim; ghi digoxin 2,5 mg; ghi ho có đờm; ghi mạch 70 lần/phút; bỏ sót furosemid. Lớp cảnh báo bắt đúng 4/5 bản sai. |

Lưu ý: ca `bay_14` có từ Nghệ Tĩnh nhưng giọng đọc là giọng Trung của VieNeu, không phải ngữ điệu Nghệ.
