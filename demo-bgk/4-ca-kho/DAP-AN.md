# Đáp án bộ 5 ca khó (`4-ca-kho/`)

> Kịch bản tổng hợp, Claude viết 28/11/2026, không có bệnh nhân thật. **Chưa có bác sĩ duyệt** (xem `../PHIEU-BAC-SI-DUYET.md`; tự kiểm của AI ở `../TU-KIEM-LAM-SANG.md`, không thay bác sĩ). Âm thanh là giọng máy VieNeu-TTS v3 Turbo, cùng cách làm với `3-ca-moi/` (nghỉ 0,4–1,1 giây, tốc độ từng vai lệch ±5 %, tiếng phòng rất nhỏ).
> Mỗi ca cài 4–6 bẫy đan vào nhau. Ca 2 người nói (`ca_01`, `ca_03`, `ca_04`) không có hai lượt liền nhau cùng một người, nên gợi ý vai xen kẽ đúng cả ca. Ca 3 người (`ca_02`, `ca_05`) phải sửa vai Người nhà bằng phím 3.
> Trong `.txt`, đơn vị viết "mi-li-gam"; khi đọc thành tiếng, máy chèn một nhịp ngắt giữa số và đơn vị ("năm, mi li gam") để ASR không nghe thành "năm mươi lăm gam".

| Ca | Tình huống | Giọng | Người nói | Bẫy chính |
|---|---|---|---|---|
| `ca_01` | Bác 72 tuổi suy tim + rung nhĩ, nặng lên vì bỏ lợi tiểu | Bắc (Hải Đăng / Phạm Tuyên) | BS, BN | Nhiều thuốc: 1 ngừng, 1 tăng tạm thời, 1 mới, 1 "chưa tăng"; tự mâu thuẫn; đính chính cân nặng; chuỗi phủ định |
| `ca_02` | Bà 78 tuổi ngã do hạ đường huyết vì gliclazid | Bắc (Hải Đăng / Ngọc Linh / Trúc Ly) | BS, BN, NN | Hai người kể mâu thuẫn; dị ứng bị chối rồi người nhà sửa; tiền sử của con gái và chồng; số đường máu |
| `ca_03` | Anh 48 tuổi gút cấp tái phát, từng phản ứng da nặng với allopurinol | Nam Bộ (Thùy Dung / Adam) | BS, BN | Đính chính hai lần; phủ định Nam Bộ; dị ứng kể gián tiếp; tiền sử gia đình; thuốc dự định chưa dùng; liều 6 viên × 5 mg |
| `ca_04` | Chị 40 tuổi đợt cấp hen, hết thuốc dự phòng | Huế (Quang Sơn / Ngọc Trân) | BS, BN | Tự mâu thuẫn "xịt đều"; aspirin gây khó thở (kể gián tiếp); tiền sử của mẹ, bố; "không đau ngực" nhưng "tức ngực"; số đo |
| `ca_05` | Anh 52 tuổi khám trước mổ sỏi túi mật | Bắc (Hải Đăng / Quốc Tuấn / Đoan Trang) | BS, BN, NN | Mổ là kế hoạch; người nhà sửa sốt, dị ứng, rượu; câu điều kiện; aspirin ngừng; tiền sử bố mẹ |

---

## ca_01 — Suy tim nặng lên, nhiều thuốc

**Tình huống:** Bác trai 72 tuổi, suy tim phân suất tống máu giảm (EF 35 %), rung nhĩ đang dùng apixaban. Đi khám sớm vì khó thở khi nằm, phù chân, tăng cân. Hóa ra đã bỏ furosemid 3 ngày và ăn mặn khi về quê.

**Bẫy và bản ghi đúng phải nói:**
1. **Chuỗi phủ định:** "Không đau ngực, không ngất, ho cũng không. Chỉ khó thở với hai chân sưng" → không đau ngực, không ngất, không ho; **có** khó thở khi nằm (phải kê 2 gối) và phù chân.
2. **Đính chính số:** "sáu mươi tư… à không, sáu mươi lăm" → cân nặng nay **65 kg**, tuần trước 62 kg (tăng 3 kg). Không ghi 64.
3. **Bệnh nhân tự mâu thuẫn:** đầu tiên "uống đều cả, không bỏ hôm nào", sau đó thừa nhận **bỏ furosemid 3 ngày** tuần trước, ăn mặn. Bản ghi phải ghi tuân thủ kém (bỏ lợi tiểu), không ghi "tuân thủ tốt".
4. **Nhiều thuốc, mỗi thuốc một số phận:**
   - Aspirin 81 mg: **ngừng** (đã có apixaban, dùng cả hai tăng nguy cơ chảy máu).
   - Furosemid 40 mg sáng: **tăng tạm thời** lên 80 mg ("hai viên, tức là gấp đôi" buổi sáng) trong **3 ngày**, sau đó **về lại 40 mg**. Lời thoại không nói con số 80, bản ghi được suy ra 2 × 40 mg.
   - Spironolacton 25 mg sáng: **thuốc mới**.
   - Bisoprolol 2,5 mg: **giữ nguyên**; "khi nào hết phù mới tính tăng" là dự định, **không** ghi là đã tăng lên 5 mg.
   - Apixaban: "giữ nguyên liều cũ, sáng một viên, tối một viên" = 5 mg × 2 lần/ngày (liều đọc ở đầu ca).
   - Thuốc đang dùng trước khám phải là danh sách cũ (có aspirin, furosemid 40 mg, không có spironolacton).
5. **Số dễ nghe nhầm:** bisoprolol **2,5 mg** (không phải 25 mg), spironolacton **25 mg**, kali **4,2**, creatinin **92 µmol/L**, HA 135/80, mạch ~92 không đều, SpO₂ 94 %.
6. **Câu điều kiện:** "Nếu ba ngày tăng quá hai cân, hoặc phải ngồi dậy mới thở được, thì vào viện ngay" là dặn dò, không phải sự việc đã xảy ra.

**SOAP mong đợi:**
- S: Khó thở tăng, khó thở khi nằm (kê 2 gối), phù hai chân; cân 62 → 65 kg trong 1 tuần. Không đau ngực, không ngất, không ho. Bỏ furosemid 3 ngày tuần trước, ăn mặn. Thuốc: furosemid 40 mg sáng, bisoprolol 2,5 mg sáng, apixaban 5 mg × 2, aspirin 81 mg. Không dị ứng thuốc.
- O: HA 135/80 mmHg, mạch không đều ~92 l/ph, ran ẩm hai đáy phổi, phù hai chân ấn lõm đến giữa cẳng chân, SpO₂ 94 %. EF lần trước 35 %. Kali 4,2 mmol/L, creatinin 92 µmol/L.
- A: Suy tim EF giảm mất bù nhẹ (ứ dịch) do bỏ lợi tiểu và ăn mặn; rung nhĩ đang chống đông. Chưa cần nhập viện.
- P: Ngừng aspirin. Furosemid 80 mg sáng × 3 ngày rồi về 40 mg. Thêm spironolacton 25 mg sáng. Giữ bisoprolol 2,5 mg (tính tăng khi hết phù), giữ apixaban 5 mg × 2. Ăn nhạt, dịch ≤ 1,5 L/ngày (~6 cốc), cân mỗi sáng. Vào viện nếu tăng > 2 kg/3 ngày hoặc khó thở phải ngồi. Tái khám 1 tuần: kali, chức năng thận, siêu âm tim.

## ca_02 — Ngã do hạ đường huyết (3 người nói)

**Tình huống:** Bà 78 tuổi đái tháo đường type 2, dùng metformin + gliclazid MR 60 mg, mấy hôm ăn kém. Con gái thấy bà nằm dưới sàn, đường máu 2,8 mmol/L.

**Bẫy và bản ghi đúng phải nói:**
1. **Hai người kể mâu thuẫn:** con gái "gọi mãi mới thưa, vã mồ hôi"; bệnh nhân "tôi có ngất đâu, chỉ trượt chân". Bệnh nhân **không nhớ rõ** lúc ngã. Bản ghi nên ghi cả hai lời kể (giảm ý thức theo người nhà), **không** kết luận "không ngất" theo lời bệnh nhân.
2. **Số đường máu:** tại nhà **2,8 mmol/L**, sau nước đường **6,1**, tại phòng khám **7,8**. Ba số khác thời điểm, không gộp. Ngưỡng dặn dò "dưới 4" là ngưỡng xử trí, không phải số đo.
3. **Dị ứng bị chối rồi được sửa:** bệnh nhân "chẳng dị ứng gì" → con gái: cefalexin gây **sưng môi, sưng mắt** (phù mạch), bệnh nhân xác nhận. Bản ghi phải ghi **dị ứng cefalexin (phù mạch)**, không ghi "không dị ứng".
4. **Tiền sử của người khác:** con gái **tự** bị đái tháo đường, tiêm insulin; **chồng** bệnh nhân mất vì đột quỵ. Không ghi bệnh nhân tiêm insulin, không ghi bệnh nhân bị đột quỵ.
5. **Chuỗi phủ định:** không đau đầu, không yếu tay chân, **chỉ** đau hông trái.
6. **Kế hoạch so với thực tế:** chụp phim khung chậu, hông trái **hôm nay** là chỉ định, chưa có kết quả; "chưa nghĩ đến gãy" không phải "đã loại trừ gãy".

**SOAP mong đợi:**
- S: Người nhà (con gái) kể: sáng qua thấy bà nằm dưới sàn bếp, gọi mãi mới thưa, vã mồ hôi; đường máu 2,8 mmol/L, uống nước đường 15 phút sau 6,1, tỉnh hẳn. Bệnh nhân cho là chỉ trượt chân, không nhớ rõ; trước đó run tay, đói cồn cào. Mấy hôm ăn kém nhưng vẫn uống đủ thuốc. Không đau đầu, không yếu tay chân; đau hông trái. Thuốc: metformin 500 mg × 2, gliclazid MR 30 mg × 2 viên sáng (60 mg). Dị ứng cefalexin (sưng môi, mắt). Gia đình: con gái ĐTĐ (insulin); chồng mất vì đột quỵ.
- O: Tỉnh, định hướng tốt, không yếu liệt. Đầu không bầm, không sưng. HA 140/80 mmHg. Hông trái bầm, ấn đau nhẹ, chân không ngắn, không xoay ngoài, tự đi lại được. Đường máu mao mạch 7,8 mmol/L.
- A: Hạ đường huyết nặng do sulfonylurea (gliclazid) khi ăn kém, gây ngã; đụng dập hông trái, chưa loại trừ gãy. ĐTĐ type 2 ở người cao tuổi.
- P: Ngừng gliclazid. Giữ metformin 500 mg × 2 sau ăn. X-quang khung chậu, hông trái hôm nay. HbA1c, chức năng thận. Dặn xử trí hạ đường huyết (< 4 mmol/L hoặc run, vã mồ hôi: nước đường/nước cam, đo lại sau 15 phút; lơ mơ thì gọi cấp cứu). Đo đường máu 2 lần/ngày, tái khám 1 tuần. Ghi dị ứng cefalexin vào hồ sơ.

## ca_03 — Gút cấp, giọng Nam Bộ

**Tình huống:** Anh 48 tuổi, sưng đỏ khớp bàn ngón chân cái phải sau nhậu bia, đồ biển. Hai năm trước từng có cơn gút; dùng allopurinol thì sốt, bóng nước, tróc da, nằm viện (nghi phản ứng da nặng kiểu SJS/TEN). Tiền sử loét dạ dày. Đang dùng amlodipin.

**Bẫy và bản ghi đúng phải nói:**
1. **Đính chính hai lần:** "ba bữa, à hông, năm bữa… à mà tính ra từ thứ bảy tuần rồi, cả tuần rồi" → **khởi phát khoảng 1 tuần (từ tối thứ bảy tuần trước)**. Không ghi 3 hay 5 ngày.
2. **Phủ định Nam Bộ:** "hổng sốt, hổng ho, mấy khớp khác cũng hổng sao" → không sốt, không ho, chỉ một khớp.
3. **Dị ứng kể gián tiếp:** "uống allopurinol… sốt, nổi bóng nước, tróc da khắp người, nằm viện cả tuần" → **dị ứng nặng allopurinol (phản ứng da bóng nước, tróc da)**. Kế hoạch **không** được có allopurinol.
4. **Tiền sử gia đình lẫn với bản thân:** bố bị gút, anh trai mổ sỏi thận; **bệnh nhân chưa có sỏi thận**.
5. **Thuốc đã ngừng, không rõ tên:** thuốc giảm đau tự mua, không nhớ tên, đã ngừng → **không bịa tên thuốc**.
6. **Kế hoạch so với thực tế:** febuxostat là **dự định** sau khi hết sưng ~2 tuần, **chưa kê** hôm nay.
7. **Số:** prednisolon **5 mg × 6 viên = 30 mg** mỗi sáng × 5 ngày; omeprazol 20 mg; axit uric **480 µmol/L**; HA **150/90**; nhiệt độ 37,2 °C.

**SOAP mong đợi:**
- S: Sưng nóng đỏ đau khớp bàn ngón chân cái phải ~1 tuần, sau nhậu bia, đồ biển (tối thứ bảy). Không sốt, không ho, không đau khớp khác. Cơn gút 2 năm trước. Dị ứng nặng allopurinol (sốt, bóng nước, tróc da, nằm viện). Tiền sử loét dạ dày đã điều trị. Không ĐTĐ, chưa sỏi thận. Đang dùng amlodipin 5 mg sáng; đã ngừng thuốc giảm đau tự mua (không rõ tên). Gia đình: bố gút, anh trai sỏi thận.
- O: Khớp bàn ngón I chân phải sưng, nóng, đỏ, ấn đau nhiều; khớp khác bình thường. T 37,2 °C, HA 150/90 mmHg. Axit uric 480 µmol/L, creatinin bình thường.
- A: Cơn gút cấp tái phát khớp bàn ngón I chân phải. Tiền sử phản ứng da nặng với allopurinol. Tiền sử loét dạ dày. HA cao trong cơn đau, cần theo dõi.
- P: Không dùng NSAID (loét dạ dày, đến muộn). Prednisolon 30 mg (6 viên × 5 mg) sáng sau ăn × 5 ngày + omeprazol 20 mg sáng trước ăn × 5 ngày. Chưa dùng thuốc hạ axit uric; tái khám sau hết sưng ~2 tuần để cân nhắc febuxostat; tuyệt đối không dùng lại allopurinol. Tiếp tục amlodipin, đo HA tại nhà. Bớt bia, đồ biển, nội tạng, uống nhiều nước. Quay lại ngay nếu sau 3 ngày không đỡ, sốt > 38,5 °C hoặc sưng thêm (có thể chọc hút dịch khớp).

## ca_04 — Đợt cấp hen, giọng Huế

**Tình huống:** Chị 40 tuổi hen từ nhỏ, dùng budesonid/formoterol hai nhát × 2 lần/ngày; ống đã hết cả tuần. Trời trở lạnh, khò khè 5 ngày, xịt salbutamol 4–5 lần/ngày. Từng khó thở phải cấp cứu sau uống aspirin.

**Bẫy và bản ghi đúng phải nói:**
1. **Tự mâu thuẫn:** "xịt đều lắm" → sau đó "ống đỏ hết thuốc cả tuần ni rồi, tui chưa đi mua" → **đã ngừng thuốc dự phòng ~1 tuần** (tuân thủ kém). Không ghi "đang dùng đều".
2. **Phủ định chồng nhau:** "không sốt, không đau ngực chi hết… ho khan, không có đờm. Chỉ khò khè với tức ngực về đêm" → không sốt, không đau ngực, không đờm; **có** tức ngực về đêm và ho khan. "Không đau ngực" và "có tức ngực" phải cùng có mặt, không mâu thuẫn.
3. **Dị ứng kể gián tiếp:** "uống viên aspirin… nghẹt mũi, thở không được, phải đi cấp cứu" → **phản ứng với aspirin (khó thở, nghẹt mũi), nghi hen nhạy cảm aspirin/NSAID**. Kế hoạch phải tránh aspirin, ibuprofen và các NSAID; giảm đau chỉ paracetamol ≤ 500 mg/lần.
4. **Tiền sử của người khác:** mẹ ("mạ") bị hen; bố ("bọ") hút thuốc, mất vì ung thư phổi; chồng hút thuốc ngoài hiên. **Bệnh nhân không hút thuốc** (có phơi nhiễm khói thuốc thụ động).
5. **Từ Huế:** "mô" (đâu/nào), "ni" (này), "nớ" (đó), "rứa" (vậy), "chừ" (bây giờ), "mạ/bọ" (mẹ/bố).
6. **Số:** thời gian **5 ngày** (từ thứ tư); nhịp thở 22; SpO₂ **95 %**; lưu lượng đỉnh **280 L/ph ≈ 70 %** mức tốt nhất; prednisolon **5 mg × 8 viên = 40 mg** × 5 ngày.
7. **Thực hiện tại chỗ, chưa có kết quả:** khí dung salbutamol tại phòng khám "rồi đo lại", không có số đo lại trong lời thoại.

**SOAP mong đợi:**
- S: Khò khè, khó thở, ho khan về đêm 5 ngày sau trời trở lạnh. Không sốt, không đau ngực, không đờm; tức ngực về đêm. Hen từ nhỏ. Budesonid/formoterol 2 nhát × 2 lần/ngày nhưng **hết thuốc ~1 tuần**; salbutamol 4–5 lần/ngày. Phản ứng aspirin (nghẹt mũi, khó thở, cấp cứu). Không hút thuốc; chồng hút thuốc. Gia đình: mẹ hen; bố hút thuốc, mất vì ung thư phổi.
- O: Ran rít, ran ngáy rải rác hai phổi. Nhịp thở 22 l/ph, SpO₂ 95 %. PEF 280 L/ph (~70 % tốt nhất).
- A: Đợt cấp hen mức trung bình, yếu tố khởi phát: ngừng corticoid hít, lạnh. Nghi hen nhạy cảm aspirin.
- P: Khí dung salbutamol tại chỗ, đánh giá lại. Prednisolon 40 mg (8 viên × 5 mg) sáng sau ăn × 5 ngày. Dùng lại budesonid/formoterol 2 nhát × 2 lần/ngày, súc miệng sau xịt. Salbutamol khi cần. Tránh aspirin, ibuprofen, NSAID; đau đầu dùng paracetamol 500 mg/lần. Tái khám 1 tuần; cấp cứu nếu xịt cắt cơn không đỡ, nói không thành câu, tím môi.

## ca_05 — Khám trước mổ sỏi túi mật (3 người nói)

**Tình huống:** Anh 52 tuổi, cơn đau quặn mật 3 tháng, siêu âm nhiều sỏi túi mật, hẹn mổ nội soi thứ ba tuần sau. Vợ đi cùng, sửa lời chồng ba lần.

**Bẫy và bản ghi đúng phải nói:**
1. **Kế hoạch so với thực tế:** mổ cắt túi mật là **dự kiến thứ ba tuần sau, chưa mổ**, và còn **phụ thuộc kết quả xét nghiệm**. Không ghi "đã mổ" hay "sau mổ".
2. **Người nhà sửa triệu chứng:** bệnh nhân "không sốt" → vợ: tuần trước một đêm rét run, **38 °C**, sáng hết; bệnh nhân xác nhận. Bản ghi phải ghi **có một cơn sốt 38 °C kèm rét run tuần trước**; hiện không sốt (36,8 °C), không vàng da, nước tiểu bình thường.
3. **Dị ứng bị chối rồi được sửa, kể gián tiếp:** "uống biseptol vào là nổi mẩn đỏ khắp người, ngứa" → **dị ứng co-trimoxazol (biseptol), phát ban ngứa toàn thân**.
4. **Lời kể rượu mâu thuẫn:** bệnh nhân "thỉnh thoảng", vợ "tối nào cũng ba, bốn chén" → ghi **uống rượu hằng ngày 3–4 chén theo người nhà** (bệnh nhân khai ít hơn). Không hút thuốc.
5. **Tiền sử gia đình:** bố mổ sỏi mật, mẹ đái tháo đường. **Bệnh nhân không có bệnh nền đã biết**, không ghi ĐTĐ cho bệnh nhân.
6. **Thuốc ngừng:** aspirin 81 mg/ngày (dự phòng, do trạm y tế phường kê) **ngừng từ hôm nay, 7 ngày trước mổ**; dùng lại theo hẹn sau mổ.
7. **Câu điều kiện:** "nếu sốt trên 38,5, rét run, vàng da hay đau không đỡ thì vào cấp cứu" là dặn dò. Paracetamol 500 mg khi đau, cách ≥ 6 giờ.

**SOAP mong đợi:**
- S: Đau hạ sườn phải sau ăn mỡ, lan ra lưng, mỗi cơn 1–2 giờ, 3 tháng. Theo vợ: tuần trước một đêm rét run, sốt 38 °C, tự hết (bệnh nhân xác nhận). Không vàng da, nước tiểu bình thường. Thuốc: aspirin 81 mg sáng. Dị ứng co-trimoxazol/biseptol (mẩn đỏ ngứa toàn thân). Không hút thuốc; rượu 3–4 chén mỗi tối (theo vợ). Gia đình: bố mổ sỏi mật, mẹ ĐTĐ.
- O: Không vàng da, vàng mắt. Bụng mềm, ấn hạ sườn phải hơi tức, Murphy âm tính. T 36,8 °C, HA 130/85 mmHg. Siêu âm: nhiều sỏi túi mật, thành không dày.
- A: Sỏi túi mật có triệu chứng, dự kiến cắt túi mật nội soi; có cơn sốt rét run tuần trước, cần loại trừ viêm túi mật/viêm đường mật. Uống rượu hằng ngày.
- P: Xét nghiệm hôm nay: công thức máu, men gan, bilirubin, đông máu; mổ thứ ba tuần sau nếu kết quả ổn. Ngừng aspirin từ hôm nay (7 ngày trước mổ). Ghi dị ứng co-trimoxazol và uống rượu hằng ngày cho gây mê. Paracetamol 500 mg khi đau, cách ≥ 6 giờ. Nhịn ăn từ 22 giờ tối trước mổ. Bớt rượu. Vào cấp cứu nếu sốt > 38,5 °C, rét run, vàng da, đau không đỡ. Hẹn 2 ngày xem kết quả.

---

## ASR còn nghe sai (PhoWhisper-small, chạy tại máy 28/11/2026)

Đã thử: viết "năm mi-li-gam" hay "năm mi li gam" thì máy đọc dính, ASR nghe ra "năm mươi lăm gam"/"năm mươi linh gam". Chèn một nhịp ngắt khi đọc ("năm, mi li gam", tệp `.txt` giữ nguyên) sửa được phần lớn. Ở `ca_01`, các lần nhắc liều sau (spironolacton, furosemid 80, apixaban) vẫn bị nghe thành "… mươi lăm gam", nên lời thoại được viết lại cho tự nhiên hơn ("mỗi sáng một viên hai mươi lăm mi-li-gam", "hai viên, tức là gấp đôi", "giữ nguyên liều cũ, sáng một viên, tối một viên") và đọc lại.

| Ca | Chỗ then chốt nghe đúng | Còn nghe sai |
|---|---|---|
| `ca_01` | 62 → "64 à không 65" cân; bisoprolol 2,5 mg; apixaban 5 mg ngày hai lần; aspirin 81 mg; spironolacton 25 mg; kali 4,2; creatinin 92; chuỗi "không đau ngực, không ngất"; "bỏ thuốc lợi tiểu ba hôm" | Lần đọc đầu "furosemid bốn mươi mi-li-gam" ra "phu rô s mươi gam" (mất số 40; lần sau "một viên bốn mươi" nghe đúng). Tên thuốc phiên âm lệch (spironolacton, apixaban) |
| `ca_02` | 2,8 / 6,1 / 7,8; gliclazid 30 mg × 2 viên; metformin 500; "tôi có ngất đâu"; "sưng môi sưng mắt"; insulin của con gái, đột quỵ của bố | Tên **cefalexin** ra "xe phép sinh"/"sê phèo xin"; gliclazid ra "cờ líp la dít". Phản ứng dị ứng vẫn nghe đúng |
| `ca_03` (Nam Bộ) | "ba bữa à hông năm bữa… cả tuần rồi"; "hổng sốt, hổng ho" (ASR viết "hỏng"); bóng nước, tróc da; 480; 150/90; prednisolon "năm mi(li)gam" | "amlodipin năm mi-li-gam" ra "… âm mi li ga"; "sáu viên" ra "sáu huyền"; "dị ứng" ra "bị ứng"; "loét bao tử" ra "rét tàu tử"; allopurinol phiên âm nhiều kiểu |
| `ca_04` (Huế) | "không sốt, không đau ngực", "tức ngực"; aspirin → "nghẹt mũi, thở không được"; "hết thuốc cả tuần ni"; 22, 95 %, 280, 70 %; paracetamol 500 | Giọng Huế bị nhận kém nhất: "tám viên" ra "tạm viếng", prednisolon ra "picnic o", budesonid/formoterol ra chuỗi vô nghĩa, nhiều từ địa phương sai chính tả. **Nên dùng `.txt`** cho ca này |
| `ca_05` | "không sốt" rồi "rét run… ba mươi tám độ"; aspirin 81 mg; "tối nào cũng ba, bốn chén"; 36,8; 130/85; 38,5; paracetamol 500 | **biseptol** ra "bai thôn", co-trimoxazol ra "co chi mô xa rôn"; "gây mê" ra "kênh mới". Phản ứng "nổi mẩn đỏ khắp người" nghe đúng |

Cũng đã kiểm `3-ca-moi/ca_05` sau khi đọc lại: "mười bảy cân" và "hai trăm năm mươi mi li gam" nghe đúng.
