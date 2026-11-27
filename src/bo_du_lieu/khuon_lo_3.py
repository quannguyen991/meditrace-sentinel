# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Khuôn bệnh]
Làm gì   : Chứa lô khuôn bệnh 301–350 (cơ xương khớp, thần kinh cơ, chấn thương chỉnh hình)
           cho bộ sinh.
Vào → Ra : — (chỉ chứa dữ liệu: danh sách BENH_LO_3 các khuôn bệnh và bảng giới tính
           GIOI_TINH_LO_3)
Dùng bởi : bo_du_lieu/khuon_mo_rong
Tên cũ   : khuon_lo_3.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Khuôn bệnh mở rộng Lô 3 (Khuôn 301-350): Cơ xương khớp, Thần kinh cơ & Chấn thương chỉnh hình ngoại trú."""

GIOI_TINH_LO_3 = {}

BENH_LO_3 = [
    {   'bien_the_chan_doan': [   'Viêm gân lồi cầu trong xương cánh tay phải (hội chứng khuỷu tay người chơi golf).',
                              'Viêm điểm bám gân cơ gấp cổ tay tại lồi cầu trong xương cánh tay giai đoạn mạn tính.',
                              'Theo dõi viêm gân lồi cầu trong xương cánh tay bên trái do quá tải vận động.',
                              'Viêm gân lồi cầu trong xương cánh tay mức độ trung bình chưa có rách gân hoàn toàn.',
                              'Hội chứng khuỷu tay golfer kèm kích thích nhẹ dây thần kinh trụ vùng rãnh ròng rọc.',
                              'Viêm gân lồi cầu trong xương cánh tay mạn tính tái phát ở người lao động tay chân.'],
    'bien_the_ke_hoach': [   'Cho nghỉ ngơi hạn chế động tác gấp xoay sấp cổ tay gắng sức, chườm lạnh 15 phút ngày 3 '
                             'lần, đeo băng đai ép dưới khuỷu (counterforce brace) và uống Celecoxib 200mg/ngày trong '
                             '7-10 ngày.',
                             'Chỉ định siêu âm phần mềm vùng khuỷu tay đánh giá độ dày sợi gân và mức độ thoái hóa vi '
                             'rách, hướng dẫn bài tập kéo giãn và tăng sức mạnh cơ ly tâm nhóm gấp cổ tay.',
                             'Kê đơn Meloxicam 7,5mg uống sau ăn sáng kết hợp gel Diclofenac bôi ngoài da vùng mặt '
                             'trong khuỷu tay ngày 3 lần, phối hợp vật lý trị liệu siêu âm điều trị.',
                             'Cân nhắc tiêm huyết tương giàu tiểu cầu (PRP) hoặc tiêm corticoid quanh bao gân thận '
                             'trọng tránh tiêm trực tiếp vào thân gân nếu điều trị bảo tồn sau 6 tuần không cải thiện.',
                             'Chụp X-quang khớp khuỷu thẳng nghiêng loại trừ vôi hóa điểm bám gân hoặc gai xương, tư '
                             'vấn điều chỉnh tư thế cầm dụng cụ lao động và kỹ thuật chơi thể thao.',
                             'Hẹn tái khám sau 3 tuần đánh giá mức độ giảm đau qua thang điểm VAS và hướng dẫn phục '
                             'hồi lực nắm bàn tay từng bước.'],
    'bien_the_kham': [   'Ấn chói điểm bám gân gấp chung ngay phía trước dưới lồi cầu trong xương cánh tay phải, '
                         'nghiệm pháp gấp cổ tay có kháng lực gây đau tái hiện rõ, tầm vận động khuỷu tay bình thường '
                         'không sưng nóng.',
                         'Khám vùng khuỷu tay không thấy sưng đỏ hay biến dạng trục, sờ nắn dọc bờ trong khuỷu đau '
                         'nhói tại điểm bám gân cơ sấp tròn và cơ gấp cổ tay quay, lực bóp tay phải giảm so với tay '
                         'trái.',
                         'Nghiệm pháp căng thụ động nhóm gân gấp cổ tay (ngửa cẳng tay duỗi thẳng khuỷu và duỗi cổ '
                         'tay) gây đau giật vùng lồi cầu trong, không có tiếng lạo xạo khớp khuỷu.',
                         'Điểm đau khu trú chính xác cách mỏm lồi cầu trong 5mm về phía xa, nghiệm pháp Tinel rãnh trụ '
                         'âm tính, không teo cơ mô út, mạch quay bắt rõ đều.',
                         'Ấn đau dọc khối cơ gấp chung cẳng tay đoạn 1/3 trên, bệnh nhân nhăn mặt khi thực hiện động '
                         'tác sấp cẳng tay chống lại sức cản của bác sĩ.',
                         'Khuỷu tay trái không tràn dịch không hạn chế gấp duỗi thụ động, chỉ đau tăng khi bóp mạnh '
                         'vật cứng hoặc xoay vặn cổ tay vào trong.'],
    'chan_doan': 'Viêm gân lồi cầu trong xương cánh tay phải (hội chứng khuỷu tay người chơi golf).',
    'chinh': [   'đau nhói mặt trong khuỷu tay ngay tại mỏm lồi cầu trong khi gấp cổ tay hoặc sấp cẳng tay có kháng '
                 'lực',
                 'lực nắm bàn tay suy giảm rõ rệt khi vặn tay nắm cửa xách đồ nặng hoặc vung gậy đánh golf',
                 'tăng cảm giác căng tức dọc nhóm cơ gấp cổ tay mặt trước cẳng tay khi duỗi thẳng khuỷu và ngửa bàn '
                 'tay'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Cho nghỉ ngơi hạn chế động tác gấp xoay sấp cổ tay gắng sức, chườm lạnh 15 phút ngày 3 lần, đeo băng '
                'đai ép dưới khuỷu (counterforce brace) và uống Celecoxib 200mg/ngày trong 7-10 ngày.',
    'kham': 'Ấn chói điểm bám gân gấp chung ngay phía trước dưới lồi cầu trong xương cánh tay phải, nghiệm pháp gấp cổ '
            'tay có kháng lực gây đau tái hiện rõ, tầm vận động khuỷu tay bình thường không sưng nóng.',
    'nhom': 'người lớn',
    'phu': [   'tê bì nhẹ dọc bờ trụ ngón áp út và ngón út nếu có kích thích dây thần kinh trụ đi kèm',
               'cứng nhẹ vùng mặt trong khuỷu tay vào buổi sáng mới ngủ dậy',
               'đau tăng khi thực hiện động tác lặp đi lặp lại trong lao động hoặc thể thao dùng cổ tay'],
    'ten': 'viêm gân lồi cầu trong xương cánh tay'},
    {   'bien_the_chan_doan': [   'Viêm hẹp bao gân De Quervain cổ tay phải mức độ trung bình.',
                              'Viêm bao gân cơ dạng dài và duỗi ngắn ngón cái (hội chứng De Quervain).',
                              'Viêm bao gân De Quervain hai bên ở phụ nữ sau sinh.',
                              'Hội chứng De Quervain giai đoạn mạn tính có dày xơ bao gân khoang duỗi thứ nhất.',
                              'Theo dõi viêm bao gân De Quervain cần phân biệt với thoái hóa khớp thang bàn ngón cái.',
                              'Viêm bao gân De Quervain cấp tính tái phát do lao động sử dụng ngón cái liên tục.'],
    'bien_the_ke_hoach': [   'Đeo nẹp cố định cổ tay và ngón tay cái (thumb spica splint) giữ tư thế trung tính trong '
                             '2-3 tuần, uống thuốc kháng viêm NSAID ngắn ngày kết hợp bôi gel Ketoprofen.',
                             'Chỉ định siêu âm gân cơ vùng cổ tay xác định dày bao gân và dịch quanh khoang duỗi thứ '
                             'nhất, hướng dẫn tránh bế ẵm vặn cổ tay dùng ngón cái quá mức.',
                             'Tiêm Corticoid tại chỗ (Triamcinolone hoặc Methylprednisolone pha Lidocaine) vào trong '
                             'bao gân khoang duỗi 1 dưới hướng dẫn siêu âm nếu đeo nẹp và thuốc uống không đỡ.',
                             'Phối hợp vật lý trị liệu chiếu laser công suất thấp, điện xung giảm đau và siêu âm trị '
                             'liệu vùng mỏm trâm quay trong 10 buổi.',
                             'Chụp X-quang cổ tay thẳng nghiêng để loại trừ gãy xương thuyền cũ hoặc thoái hóa khớp '
                             'gốc ngón cái khi triệu chứng kéo dài dai dẳng.',
                             'Hội chẩn phẫu thuật chỉnh hình giải phóng ròng rọc khoang duỗi thứ nhất nếu bệnh tái '
                             'phát nhiều lần sau 2 mũi tiêm corticoid nội bao gân.'],
    'bien_the_kham': [   'Vùng mỏm trâm quay cổ tay phải sưng nề nhẹ không đỏ da, ấn dọc đường đi bao gân cơ dạng dài '
                         'và duỗi ngắn ngón cái đau chói, nghiệm pháp Finkelstein dương tính rõ rệt.',
                         'Khám cổ tay trái thấy khối gồ kích thước 1x2cm dọc khoang duỗi thứ nhất, sờ chắc ấm nhẹ, '
                         'động tác dạng và duỗi ngón cái chống lại lực cản gây đau tăng vọt.',
                         'Nghiệm pháp Eichhoff dương tính mạnh khi bẻ nghiêng trụ cổ tay, ấn điểm bám mỏm trâm quay '
                         'đau nhói nhưng khớp thang bàn ngón cái (CMC 1) không có tiếng lạo xạo (nghiệm pháp nghiền âm '
                         'tính).',
                         'Sờ thấy bao gân khoang duỗi một dày cứng kèm tiếng lạo xạo nhỏ khi bệnh nhân cử động ngón '
                         'cái, không mất cảm giác mu ngón cái (nhánh nông thần kinh quay nguyên vẹn).',
                         'Cổ tay sưng khu trú bờ quay, bệnh nhân không thể cầm cốc nước bằng tay phải do đau giật tại '
                         'cổ tay, biên độ vận động gập duỗi cổ tay thụ động vẫn còn đủ tầm.',
                         'Tổn thương bao gân De Quervain hai bên trên phụ nữ sau sinh chăm con nhỏ, ấn đau chói hai '
                         'mỏm trâm quay và test Finkelstein dương tính cả hai tay.'],
    'chan_doan': 'Viêm hẹp bao gân De Quervain cổ tay phải mức độ trung bình.',
    'chinh': [   'đau buốt vùng mỏm trâm quay cổ tay phía gốc ngón tay cái mỗi khi cầm nắm vặn xoắn hoặc bế trẻ nhỏ',
                 'nghiệm pháp Finkelstein (nắm ngón cái trong lòng bàn tay rồi bẻ cổ tay về phía trụ) gây đau chói dữ '
                 'dội',
                 'sưng nề khu trú tạo thành khối gồ nhẹ dọc bờ ngoài cổ tay trên mỏm trâm xương quay'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Đeo nẹp cố định cổ tay và ngón tay cái (thumb spica splint) giữ tư thế trung tính trong 2-3 tuần, '
                'uống thuốc kháng viêm NSAID ngắn ngày kết hợp bôi gel Ketoprofen.',
    'kham': 'Vùng mỏm trâm quay cổ tay phải sưng nề nhẹ không đỏ da, ấn dọc đường đi bao gân cơ dạng dài và duỗi ngắn '
            'ngón cái đau chói, nghiệm pháp Finkelstein dương tính rõ rệt.',
    'nhom': 'người lớn',
    'phu': [   'cảm giác lạo xạo nhẹ hoặc kẹt khựng nhẹ khi gấp duỗi ngón tay cái',
               'đau lan ngược lên mặt ngoài cẳng tay hoặc lan xuống đốt ngón cái',
               'khó khăn khi vắt khăn mặt mở nắp chai lọ hoặc đánh máy bằng ngón cái'],
    'ten': 'viêm bao gân De Quervain'},
    {   'bien_the_chan_doan': [   'Viêm bao hoạt dịch mỏm khuỷu cấp tính thể vô khuẩn sau tỳ đè.',
                              'Viêm bao hoạt dịch mỏm khuỷu bên trái nghi ngờ có bội nhiễm tụ cầu vàng.',
                              'Tràn dịch viêm cấp bao hoạt dịch mỏm khuỷu (hội chứng khuỷu tay sinh viên).',
                              'Viêm bao hoạt dịch mỏm khuỷu cấp tính do lắng đọng tinh thể urat (gout).',
                              'Tụ máu kích ứng viêm bao hoạt dịch mỏm khuỷu cấp sau va đập.',
                              'Viêm bao hoạt dịch mỏm khuỷu cấp đáp ứng tốt với bảo tồn chọc hút.'],
    'bien_the_ke_hoach': [   'Siêu âm vùng khuỷu xác định dịch trong bao hoạt dịch ngoài khớp, chọc hút dịch vô khuẩn '
                             'bằng kim lớn gửi xét nghiệm tế bào, nhuộm Gram, cấy vi khuẩn và soi tinh thể loại trừ '
                             'nhiễm trùng hoặc gout.',
                             'Nếu dịch trong vô khuẩn: băng ép nhẹ bằng băng thun cố định khuỷu tay tránh tỳ đè, chườm '
                             'đá lạnh, kê đơn Ibuprofen 400mg ngày 3 lần trong 5-7 ngày.',
                             'Nếu nghi ngờ viêm mủ nhiễm khuẩn (sốt, dịch đục, bạch cầu dịch tăng cao): dùng kháng '
                             'sinh đường uống hoặc tĩnh mạch phủ tụ cầu (Cephalexin hoặc Oxacillin), dẫn lưu sạch mủ.',
                             'Tuyệt đối không tiêm corticoid trực tiếp vào bao hoạt dịch mỏm khuỷu khi chưa loại trừ '
                             'hoàn toàn nguy cơ nhiễm trùng tại chỗ.',
                             'Hướng dẫn bệnh nhân sử dụng miếng đệm lót bảo vệ khuỷu tay khi làm việc trên bàn cứng và '
                             'tránh thói quen chống cằm tỳ khuỷu.',
                             'Hội chẩn ngoại chấn thương chỉnh hình cắt bỏ toàn bộ túi bao hoạt dịch nếu viêm mạn tính '
                             'tái phát dai dẳng hoặc tạo ổ mủ vách hóa.'],
    'bien_the_kham': [   'Mặt sau mỏm khuỷu phải có khối sưng tròn kích thước 4x5cm ranh giới rõ, sờ mềm bùng nhùng có '
                         'dấu hiệu ba động dịch, da trên khối hơi ấm không đỏ tấy, khớp khuỷu gập duỗi tự do không đau '
                         'bên trong.',
                         'Khối sưng mỏm khuỷu trái căng mọng đỏ nhẹ và ấm nóng tại chỗ, ấn vào khối thấy đau tức, quan '
                         'sát thấy một vết trầy xước nhỏ đóng vảy trên đỉnh mỏm khuỷu nghi đường vào nhiễm khuẩn.',
                         'Bao hoạt dịch sau khuỷu căng phồng chứa dịch rõ rệt, gấp khuỷu 110 độ gây căng đau mặt sau, '
                         'còn xoay sấp ngửa cẳng tay hoàn toàn bình thường không đau khớp.',
                         'Sờ thấy khối tụ dịch mềm khu trú ở vùng dưới da ngay trên mỏm khuỷu xương trụ, không có hạch '
                         'nách sưng to, nhiệt độ cơ thể 37,1 độ C.',
                         'Khối sưng phồng vùng mỏm khuỷu xuất hiện nhanh sau chấn thương đập nhẹ khuỷu, ấn mềm lún '
                         'không có tiếng lạo xạo xương, mạch ngoại vi và thần kinh trụ vùng khuỷu bình thường.',
                         'Viêm bao hoạt dịch mỏm khuỷu thể vô khuẩn mạn tính đợt cấp: sờ bên trong túi dịch có vài hạt '
                         'cục nhỏ xơ hóa di động nhẹ, da trên khối không nóng đỏ.'],
    'chan_doan': 'Viêm bao hoạt dịch mỏm khuỷu cấp tính thể vô khuẩn sau tỳ đè.',
    'chinh': [   'xuất hiện khối sưng tròn phồng mềm bùng nhùng như quả trứng gà ngay sau mỏm khuỷu tay',
                 'da phủ trên khối sưng căng bóng có thể đỏ ấm nếu viêm phản ứng hoặc nhiễm trùng nhưng không lan rộng '
                 'toàn khớp',
                 'đau tức tăng khi chống khuỷu tay xuống bàn hoặc gập tối đa khuỷu tay làm căng bao hoạt dịch'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Siêu âm vùng khuỷu xác định dịch trong bao hoạt dịch ngoài khớp, chọc hút dịch vô khuẩn bằng kim lớn '
                'gửi xét nghiệm tế bào, nhuộm Gram, cấy vi khuẩn và soi tinh thể loại trừ nhiễm trùng hoặc gout.',
    'kham': 'Mặt sau mỏm khuỷu phải có khối sưng tròn kích thước 4x5cm ranh giới rõ, sờ mềm bùng nhùng có dấu hiệu ba '
            'động dịch, da trên khối hơi ấm không đỏ tấy, khớp khuỷu gập duỗi tự do không đau bên trong.',
    'nhom': 'người lớn',
    'phu': [   'biên độ duỗi và gập khuỷu tay gần như bình thường không bị kẹt khớp bên trong',
               'tiền sử hay tỳ đè khuỷu tay lên mặt bàn cứng hoặc va đập nhẹ vùng khuỷu',
               'sốt nhẹ ớn lạnh nếu có nhiễm khuẩn xâm nhập vào túi hoạt dịch qua vết trầy xước'],
    'ten': 'viêm bao hoạt dịch mỏm khuỷu'},
    {   'bien_the_chan_doan': [   'Viêm cấp bao hoạt dịch trước xương bánh chè (gối người lau nhà) thể vô khuẩn.',
                              'Viêm bao hoạt dịch trước xương bánh chè cấp tính nghi ngờ nhiễm khuẩn.',
                              'Tràn dịch viêm cấp tính bao hoạt dịch trước bánh chè sau chấn thương đập gối.',
                              'Viêm bao hoạt dịch trước xương bánh chè cấp liên quan đến lao động quỳ gối.',
                              'Theo dõi viêm bao hoạt dịch trước bánh chè cần phân biệt tràn dịch ổ khớp gối.',
                              'Viêm bao hoạt dịch trước xương bánh chè cấp tính mức độ vừa.'],
    'bien_the_ke_hoach': [   'Siêu âm khớp gối xác định ổ tụ dịch nằm nông hoàn toàn trong khoang trước xương bánh '
                             'chè, ổ khớp gối sạch không có dịch, thực hiện chọc hút dịch gửi xét nghiệm soi tinh thể '
                             'và cấy khuẩn.',
                             'Điều trị bảo tồn với trường hợp vô khuẩn: nghỉ ngơi tránh quỳ gối, chườm lạnh 15 phút '
                             'mỗi 4 giờ, băng ép nhẹ vùng gối và dùng Naproxen 500mg ngày 2 lần trong 7 ngày.',
                             'Khởi trị kháng sinh Cefuroxime hoặc Cloxacillin đường uống ngay nếu có dấu hiệu viêm tấy '
                             'nhiễm trùng tại chỗ hoặc kết quả nhuộm Gram có cầu khuẩn Gram dương.',
                             'Trang bị đệm bảo vệ đầu gối chuyên dụng bằng gel mềm nếu bắt buộc phải quay lại công '
                             'việc có tư thế quỳ gối.',
                             'Chụp X-quang khớp gối thẳng nghiêng loại trừ nứt gãy xương bánh chè hoặc gai xương trước '
                             'bánh chè sau chấn thương va đập.',
                             'Hẹn tái khám sau 5-7 ngày đánh giá tốc độ tiêu dịch, cân nhắc phẫu thuật nội soi cắt bao '
                             'hoạt dịch nếu tụ dịch tái lập liên tục thành mạn tính.'],
    'bien_the_kham': [   'Mặt trước xương bánh chè phải có khối sưng tròn đường kính 5cm nổi gồ ngay dưới lớp da, sờ '
                         'bùng nhùng chứa dịch, không thấy bập bềnh xương bánh chè bên trong ổ khớp (khối dịch nằm '
                         'nông trên xương bánh chè).',
                         'Khám gối trái thấy túi hoạt dịch trước bánh chè căng phồng đỏ nhẹ và ấm nóng tại chỗ, ấn '
                         'trực tiếp lên đỉnh bánh chè đau tăng, các nghiệm pháp Lachman và ngăn kéo âm tính.',
                         'Gấp gối quá 90 độ làm căng lớp da trước gối gây đau tức, đi lại chịu lực trên chân bệnh '
                         'không đau sâu trong khe khớp, khe khớp trong và ngoài ấn không đau.',
                         'Da vùng trước xương bánh chè dày sừng thâm nhẹ do tỳ đè nghề nghiệp kèm khối tụ dịch mới '
                         'xuất hiện 3 ngày nay, không sốt toàn thân không có vết thương hở.',
                         'Khối sưng phồng nông ngay trước gối phải ấn mềm lún có ranh giới tròn rõ, chọc dò nhẹ ra ít '
                         'dịch vàng chanh hơi đục, hạch bẹn không sưng.',
                         'Khớp gối vận động duỗi thẳng hoàn toàn bình thường, không có tiếng lạo xạo trong khớp, chỉ '
                         'có bọng dịch khu trú ngay bề mặt trước xương bánh chè.'],
    'chan_doan': 'Viêm cấp bao hoạt dịch trước xương bánh chè (gối người lau nhà) thể vô khuẩn.',
    'chinh': [   'sưng phồng một bọc dịch tròn căng ngay phía trước xương bánh chè làm mất hình dáng gồ tự nhiên của '
                 'đầu gối',
                 'đau tức căng vùng mặt trước gối đặc biệt khi quỳ gối tỳ đè trực tiếp xuống sàn nhà',
                 'ổ khớp gối bên dưới không bị tràn dịch và không có dấu hiệu kẹt khớp hay lỏng lẻo dây chằng'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Siêu âm khớp gối xác định ổ tụ dịch nằm nông hoàn toàn trong khoang trước xương bánh chè, ổ khớp gối '
                'sạch không có dịch, thực hiện chọc hút dịch gửi xét nghiệm soi tinh thể và cấy khuẩn.',
    'kham': 'Mặt trước xương bánh chè phải có khối sưng tròn đường kính 5cm nổi gồ ngay dưới lớp da, sờ bùng nhùng '
            'chứa dịch, không thấy bập bềnh xương bánh chè bên trong ổ khớp (khối dịch nằm nông trên xương bánh chè).',
    'nhom': 'người lớn',
    'phu': [   'tiền sử làm nghề nghiệp phải quỳ gối kéo dài như thợ lát gạch thợ sửa ống nước hoặc lao công',
               'da mặt trước gối có thể hơi ấm đỏ nhẹ hoặc có vết chai sần dày da do ma sát lâu ngày',
               'gập gối sâu tối đa hơi căng tức mặt trước nhưng đi lại bình thường vẫn vững'],
    'ten': 'viêm bao hoạt dịch trước xương bánh chè'},
    {   'bien_the_chan_doan': [   'Hội chứng chèn ép khoang dưới mỏm cùng vai phải (viêm gân chóp xoay giai đoạn 2).',
                              'Hội chứng hẹp khoang dưới mỏm cùng vai gây viêm bao hoạt dịch dưới delta.',
                              'Hội chứng chạm mỏm cùng vai trái mạn tính ở người lao động giơ tay quá đầu.',
                              'Chèn ép khoang dưới mỏm cùng vai kèm viêm gân cơ trên gai chưa rách.',
                              'Hội chứng chèn ép dưới mỏm cùng vai giai đoạn phù nề xuất huyết bao hoạt dịch.',
                              'Hội chứng chạm khớp vai phải mức độ trung bình đáp ứng với tập vật lý trị liệu.'],
    'bien_the_ke_hoach': [   'Chụp X-quang khớp vai tư thế thẳng và tư thế chữ Y xương bả vai đánh giá hình thái mỏm '
                             'cùng vai (loại I, II hay móc loại III) và đo khoảng cách dưới mỏm cùng vai.',
                             'Chỉ định siêu âm khớp vai động tìm hình ảnh gân trên gai dày sưng tụ dịch bao hoạt dịch '
                             'dưới mỏm cùng vai và kẹt gân khi dạng tay.',
                             'Điều trị nội khoa: kê đơn Meloxicam hoặc Etoricoxib trong 10-14 ngày, tránh tuyệt đối '
                             'các động tác nâng tạ hay với tay quá đầu trong giai đoạn đau cấp.',
                             'Phối hợp chương trình vật lý trị liệu phục hồi chức năng tập kéo giãn bao khớp sau, tăng '
                             'cường sức mạnh nhóm cơ hạ chỏm xương cánh tay và cơ ổn định xương bả vai.',
                             'Tiêm Corticosteroid phối hợp thuốc tê vào khoang dưới mỏm cùng vai dưới hướng dẫn siêu '
                             'âm nếu đau nhiều gây mất ngủ và không giảm sau 4 tuần uống thuốc.',
                             'Chụp MRI khớp vai và hội chẩn nội soi mài tạo hình mỏm cùng vai (acromioplasty) nếu điều '
                             'trị bảo tồn tích cực trên 3-6 tháng thất bại.'],
    'bien_the_kham': [   'Khám khớp vai phải không sưng nề, không teo cơ delta, nghiệm pháp cung đau dương tính rõ khi '
                         'bệnh nhân chủ động dạng vai từ 70 đến 110 độ, test Neer và test Hawkins-Kennedy dương tính '
                         'mạnh.',
                         'Ấn đau khu trú vùng mấu động lớn xương cánh tay và khe dưới mỏm cùng vai trước ngoài, test '
                         'Jobe (empty can) gây đau nhưng sức cơ vẫn còn giữ được (4+/5) loại trừ đứt hoàn toàn gân '
                         'trên gai.',
                         'Tầm vận động thụ động khớp vai đủ các hướng (khác với đông cứng khớp vai), nhưng vận động '
                         'chủ động dạng vai và xoay trong gây nhăn mặt đau nhói ở bờ trước mỏm cùng vai.',
                         'Khám vai trái thấy đau tái hiện rõ khi bác sĩ cố định xương bả vai và nâng thụ động cánh tay '
                         'xoay trong lên tối đa (nghiệm pháp Neer dương tính), cột sống cổ vận động không đau.',
                         'Bệnh nhân có tư thế vai gù khom nhẹ về trước, sờ dọc rãnh nhị đầu hơi tức nhẹ, test Hawkins '
                         'đưa tay gấp trước 90 độ rồi xoay trong mạnh làm tái hiện cơn đau quen thuộc.',
                         'Sức cơ xoay ngoài và xoay trong vai bình thường 5/5, chỉ xuất hiện cơn đau chói khoang dưới '
                         'mỏm cùng vai khi với tay ra sau lưng hoặc giơ tay ngang vai.'],
    'chan_doan': 'Hội chứng chèn ép khoang dưới mỏm cùng vai phải (viêm gân chóp xoay giai đoạn 2).',
    'chinh': [   'đau nhói mặt trước ngoài khớp vai lan xuống vùng cơ delta khi giơ cánh tay lên cao quá đầu',
                 'cung đau điển hình xuất hiện trong khoảng góc dạng vai từ 60 đến 120 độ và hết đau khi qua khỏi 120 '
                 'độ',
                 'đau nhức khớp vai tăng lên về đêm đặc biệt khi nằm nghiêng đè lên bên vai bị bệnh'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang khớp vai tư thế thẳng và tư thế chữ Y xương bả vai đánh giá hình thái mỏm cùng vai (loại '
                'I, II hay móc loại III) và đo khoảng cách dưới mỏm cùng vai.',
    'kham': 'Khám khớp vai phải không sưng nề, không teo cơ delta, nghiệm pháp cung đau dương tính rõ khi bệnh nhân '
            'chủ động dạng vai từ 70 đến 110 độ, test Neer và test Hawkins-Kennedy dương tính mạnh.',
    'nhom': 'người lớn',
    'phu': [   'khó khăn khi chải đầu với tay lấy đồ trên kệ cao mặc áo hoặc cài khuy áo sau lưng',
               'khớp vai không bị cứng hoàn toàn mà vẫn giữ được tầm vận động thụ động bình thường',
               'yếu nhẹ cơ vai khi giữ cánh tay ở tư thế giơ ngang kéo dài'],
    'ten': 'hội chứng chèn ép khoang dưới mỏm cùng vai'},
    {   'bien_the_chan_doan': [   'Rách hoàn toàn gân cơ trên gai thuộc chóp xoay khớp vai phải mạn tính.',
                              'Rách bán phần mặt khớp gân chóp xoay khớp vai trái kèm teo cơ vùng bả vai.',
                              'Rách rộng đa gân chóp xoay khớp vai (gân trên gai và dưới gai) mạn tính.',
                              'Theo dõi rách chóp xoay khớp vai mạn tính sau thoái hóa gân ở người lớn tuổi.',
                              'Rách chóp xoay khớp vai có dấu hiệu giả liệt khớp vai mức độ nặng.',
                              'Tổn thương rách gân cơ chóp xoay khớp vai cần đánh giá chỉ định khâu gân nội soi.'],
    'bien_the_ke_hoach': [   'Chỉ định chụp cộng hưởng từ (MRI) khớp vai không tiêm hoặc có tiêm thuốc cản từ để xác '
                             'định chính xác kích thước vết rách, mức độ co rút đầu gân và độ thoái hóa mỡ cơ chóp '
                             'xoay.',
                             'Chụp X-quang khớp vai thẳng đánh giá khoảng cách mỏm cùng - chỏm cánh tay (dưới 7mm gợi '
                             'ý rách rộng lâu ngày) và mức độ thoái hóa khớp ổ chảo - cánh tay kèm theo.',
                             'Hội chẩn chuyên khoa Chấn thương chỉnh hình phẫu thuật nội soi khâu phục hồi gân chóp '
                             'xoay (arthroscopic rotator cuff repair) nếu rách hoàn toàn ở bệnh nhân còn nhu cầu vận '
                             'động.',
                             'Đối với vết rách bán phần nhỏ hoặc người lớn tuổi không mổ: điều trị bảo tồn bằng vật lý '
                             'trị liệu tăng cường sức mạnh cơ delta và các phần chóp xoay còn nguyên vẹn.',
                             'Giảm đau bằng Acetaminophen hoặc NSAID ngắn ngày, thận trọng hạn chế tiêm corticoid lặp '
                             'lại nhiều lần vì làm bở rách nặng thêm mô gân.',
                             'Hướng dẫn đeo đai treo tay bảo vệ nếu có chỉ định sau phẫu thuật khâu gân và thực hiện '
                             'đúng lộ trình tập thụ động - chủ động theo từng giai đoạn.'],
    'bien_the_kham': [   'Quan sát thấy teo nhẹ cơ trên gai và cơ dưới gai vùng bả vai phải, tầm vận động chủ động '
                         'dạng vai chỉ đạt 50 độ nhưng người khám nâng thụ động lên được 160 độ, test cánh tay rơi '
                         '(Drop-arm) và test Jobe dương tính với sức cơ giảm còn 2/5.',
                         'Sức cơ xoay ngoài khớp vai trái yếu rõ rệt khi chống kháng lực, test Lag xoay ngoài dương '
                         'tính (bàn tay tự xoay bật về bụng khi thả ra), ấn mấu động lớn xương cánh tay đau tức.',
                         'Khớp vai phải mất đường cong tròn đều do teo cơ delta và cơ hố dưới gai, test Lift-off (đẩy '
                         'tay ra khỏi thắt lưng) yếu không thực hiện được nghi ngờ tổn thương thêm gân cơ dưới vai.',
                         'Bệnh nhân không thể tự chải đầu bằng tay phải phải dùng tay trái nâng đỡ khuỷu tay phải lên, '
                         'nghe tiếng lạo xạo rõ dưới mỏm cùng vai khi xoay khớp vai thụ động.',
                         'Khám cột sống cổ nghiệm pháp Spurling âm tính loại trừ đau rễ cổ C5, khám vai thấy yếu nặng '
                         'động tác dạng vai chủ động kèm đau dữ dội vùng cơ delta khi kháng lực.',
                         'Sờ thấy điểm khuyết lõm nhẹ vùng bám tận gân trên gai ngay mấu động lớn, test Belly-press '
                         'yếu nhẹ, dấu hiệu co rút nhẹ bao khớp vai sau.'],
    'chan_doan': 'Rách hoàn toàn gân cơ trên gai thuộc chóp xoay khớp vai phải mạn tính.',
    'chinh': [   'đau âm ỉ sâu trong khớp vai kéo dài nhiều tháng lan xuống mặt ngoài cánh tay làm mất ngủ về đêm',
                 'yếu liệt rõ rệt sức cơ khi giơ cánh tay lên ngang hoặc xoay cánh tay ra ngoài không giữ được tay '
                 'trên cao',
                 'dấu hiệu cánh tay rơi (drop arm sign) khi đưa tay dạng ngang 90 độ thả ra tay rơi tụt xuống không '
                 'kiểm soát'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chỉ định chụp cộng hưởng từ (MRI) khớp vai không tiêm hoặc có tiêm thuốc cản từ để xác định chính xác '
                'kích thước vết rách, mức độ co rút đầu gân và độ thoái hóa mỡ cơ chóp xoay.',
    'kham': 'Quan sát thấy teo nhẹ cơ trên gai và cơ dưới gai vùng bả vai phải, tầm vận động chủ động dạng vai chỉ đạt '
            '50 độ nhưng người khám nâng thụ động lên được 160 độ, test cánh tay rơi (Drop-arm) và test Jobe dương '
            'tính với sức cơ giảm còn 2/5.',
    'nhom': 'người lớn',
    'phu': [   'teo rõ khối cơ hố trên gai và hố dưới gai xương bả vai bên bệnh so với bên lành',
               'nghe tiếng lạo xạo lụp cụp trong khớp vai khi cố gắng xoay cánh tay',
               'tầm vận động chủ động bị hạn chế nặng trong khi tầm vận động thụ động vẫn rộng hơn nhiều'],
    'ten': 'rách chóp xoay khớp vai'},
    {   'bien_the_chan_doan': [   'Viêm khớp cùng chậu mạn tính hai bên nghi ngờ nhóm bệnh lý cột sống huyết thanh âm '
                              'tính.',
                              'Viêm khớp cùng chậu bên phải thể không có tổn thương trên X-quang (giai đoạn sớm).',
                              'Viêm khớp cùng chậu mạn tính giai đoạn 2 theo tiêu chuẩn New York cải tiến.',
                              'Theo dõi viêm khớp cùng chậu liên quan HLA-B27 chưa có dính khớp cột sống.',
                              'Viêm khớp cùng chậu đơn độc mạn tính bên trái đáp ứng tốt với NSAID.',
                              'Viêm khớp cùng chậu mạn tính cần phân biệt với đau thần kinh tọa do thoát vị đĩa đệm.'],
    'bien_the_ke_hoach': [   'Chụp X-quang khung chậu thẳng (tư thế Ferguson) và chụp MRI khớp cùng chậu chuỗi xung '
                             'STIR phát hiện dấu hiệu phù tủy xương đặc trưng của viêm khớp cùng chậu hoạt động.',
                             'Làm xét nghiệm máu bilan viêm CRP, tốc độ máu lắng ESR, xét nghiệm kháng nguyên HLA-B27 '
                             'và loại trừ các yếu tố nhiễm khuẩn vùng chậu.',
                             'Khởi đầu điều trị bằng thuốc kháng viêm không steroid liều tối đa dung nạp như '
                             'Etoricoxib 90mg hoặc Celecoxib 200mg/ngày liên tục trong 4 tuần đánh giá đáp ứng theo '
                             'phác đồ ASAS.',
                             'Xây dựng chương trình tập thể dục trị liệu giãn cơ cột sống lưng chậu, bơi lội và duy '
                             'trì tư thế đúng hàng ngày để giữ độ linh hoạt khớp cùng chậu.',
                             'Hội chẩn chuyên khoa Cơ xương khớp cân nhắc tiêm Corticoid vào khớp cùng chậu dưới hướng '
                             'dẫn CT/siêu âm hoặc khởi trị thuốc sinh học kháng TNF-alpha nếu bệnh hoạt động mạnh '
                             'kháng NSAID.',
                             'Tư vấn bệnh nhân ngưng hút thuốc lá hoàn toàn vì thuốc lá làm tiến triển dính khớp cột '
                             'sống nhanh chóng, theo dõi phát hiện sớm triệu chứng đau mắt đỏ sợ ánh sáng.'],
    'bien_the_kham': [   'Ấn trực tiếp lên rãnh khớp cùng chậu hai bên gây đau tức sâu rõ rệt, chùm nghiệm pháp kích '
                         'thích khớp cùng chậu (FABER/Patrick, Gaenslen và ép cánh chậu) dương tính mạnh bên phải.',
                         'Bệnh nhân đi lại hơi cứng lưng dưới, nghiệm pháp Schober đo độ giãn cột sống thắt lưng hơi '
                         'giảm nhẹ còn 13,5/10cm, ấn điểm bám gân Achilles hai bên không sưng nóng, tim phổi bình '
                         'thường.',
                         'Khám cột sống thắt lưng thấy mất đường cong sinh lý nhẹ, đau tái hiện vùng mông sâu khi thực '
                         'hiện động tác ép giãn khớp cùng chậu tư thế nằm nghiêng, test nâng thẳng chân Lasegue âm '
                         'tính.',
                         'Đau khu trú vùng mông trên bên trái ngay dưới gai chậu sau trên (điểm Fortin finger dương '
                         'tính), không tê bì hay mất phản xạ gân gót S1, khớp háng xoay trong ngoài tự do không đau '
                         'bẹn.',
                         'Nghiệm pháp ép khung chậu hai bên (pelvic compression test) gây đau sâu vùng mông hai bên, '
                         'có kèm điểm đau nhẹ vùng khớp ức đòn phải, kết mạc mắt hai bên trong không đỏ.',
                         'Cơ cạnh sống thắt lưng hơi co cứng nhẹ, nghiệm pháp Gaenslen làm căng xoắn khớp cùng chậu '
                         'gây đau chói vùng mông lan xuống 1/3 trên đùi sau.'],
    'chan_doan': 'Viêm khớp cùng chậu mạn tính hai bên nghi ngờ nhóm bệnh lý cột sống huyết thanh âm tính.',
    'chinh': [   'đau âm ỉ sâu vùng mông hai bên hoặc một bên có tính chất kiểu viêm tăng lên về nửa đêm gần sáng',
                 'đau vùng mông có thể chuyển bên luân phiên từ mông trái sang mông phải hoặc lan xuống mặt sau đùi '
                 'nhưng không qua gối',
                 'cứng khớp vùng thắt lưng hông kéo dài trên 30 phút vào buổi sáng và cải thiện khi vận động đi lại'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang khung chậu thẳng (tư thế Ferguson) và chụp MRI khớp cùng chậu chuỗi xung STIR phát hiện '
                'dấu hiệu phù tủy xương đặc trưng của viêm khớp cùng chậu hoạt động.',
    'kham': 'Ấn trực tiếp lên rãnh khớp cùng chậu hai bên gây đau tức sâu rõ rệt, chùm nghiệm pháp kích thích khớp '
            'cùng chậu (FABER/Patrick, Gaenslen và ép cánh chậu) dương tính mạnh bên phải.',
    'nhom': 'người lớn',
    'phu': [   'đau tăng rõ rệt khi ngồi lâu đứng yên một chỗ hoặc bước lên cầu thang bằng một chân',
               'có thể đi kèm đau gót chân viêm điểm bám gân gót hoặc viêm màng bồ đào mắt đỏ',
               'đáp ứng giảm đau rất nhanh với thuốc kháng viêm không steroid NSAID'],
    'ten': 'viêm khớp cùng chậu'},
    {   'bien_the_chan_doan': [   'Hoại tử vô mạch chỏm xương đùi phải giai đoạn 3 theo phân loại Ficat-Arlet.',
                              'Hoại tử vô mạch chỏm xương đùi hai bên ở bệnh nhân có tiền sử dùng corticoid kéo dài.',
                              'Hoại tử chỏm xương đùi vô trùng bên trái giai đoạn sớm chưa xẹp chỏm.',
                              'Hoại tử vô mạch chỏm xương đùi biến chứng xẹp chỏm và thoái hóa khớp háng thứ phát.',
                              'Theo dõi hoại tử vô mạch chỏm xương đùi liên quan lạm dụng rượu bia.',
                              'Hoại tử chỏm xương đùi bên phải cần đánh giá chỉ định thay khớp háng nhân tạo.'],
    'bien_the_ke_hoach': [   'Chụp X-quang khung chậu thẳng và tư thế chân ếch (frog-leg lateral) tìm dấu hiệu hình '
                             'liềm dưới sụn hoặc xẹp lún biến dạng chỏm; chỉ định chụp MRI khớp háng hai bên phát hiện '
                             'hoại tử giai đoạn sớm (dấu hiệu đường đôi).',
                             'Xét nghiệm kiểm tra chức năng gan thận, bilan mỡ máu (cholesterol, triglyceride), tầm '
                             'soát rối loạn đông máu hoặc bệnh hồng cầu hình liềm nếu không có yếu tố nguy cơ rõ.',
                             'Yêu cầu ngừng ngay lập tức nguồn corticoid không cần thiết và cai rượu bia tuyệt đối, sử '
                             'dụng nạng giảm tải hoàn toàn trọng lực lên bên chân đau ở giai đoạn sớm.',
                             'Hội chẩn chuyên khoa Chấn thương chỉnh hình thực hiện phẫu thuật khoan giảm áp chỏm '
                             'xương đùi (core decompression) kèm ghép xương nếu chỏm chưa bị xẹp (giai đoạn I-II).',
                             'Lên kế hoạch phẫu thuật thay khớp háng toàn phần (THA) nếu chỏm xương đùi đã sập lún '
                             'nặng (giai đoạn III-IV) gây đau dữ dội mất chức năng vận động hàng ngày.',
                             'Dùng thuốc giảm đau nhóm Paracetamol hoặc NSAID kiểm soát triệu chứng tạm thời trước mổ '
                             'và điều trị rối loạn lipid máu bằng Statin nếu có tăng mỡ máu.'],
    'bien_the_kham': [   'Khám khớp háng phải thấy biên độ xoay trong giảm nặng chỉ đạt 10 độ kèm đau chói sâu vùng '
                         'bẹn (bên trái 40 độ), nghiệm pháp Patrick (FABER) dương tính mạnh, dáng đi khập khiễng '
                         'nghiêng người về bên phải.',
                         'Bệnh nhân dùng nạng chống đau bên trái, ấn vùng tam giác Scarpa bẹn trái đau tức, hạn chế '
                         'mọi tầm vận động thụ động khớp háng trái đặc biệt là xoay trong và dạng háng, đo chiều dài '
                         'chi hai bên còn bằng nhau.',
                         'Teo nhẹ cơ tứ đầu đùi và cơ mông bên phải (chu vi đùi phải nhỏ hơn trái 2cm), dấu hiệu '
                         'Trendelenburg dương tính bên phải do yếu cơ giạng háng, khớp gối hoàn toàn bình thường.',
                         'Đau sâu vùng bẹn lan dọc mặt trước đùi phải khi thực hiện nghiệm pháp lăn tròn khớp háng '
                         '(Log roll test), tầm duỗi háng thiếu 10 độ do co rút bao khớp trước.',
                         'Dấu hiệu Sectorial sign dương tính: bệnh nhân gấp háng lên thì tự động bị xoay ngoài và dạng '
                         'nhẹ đùi ra ngoài do kẹt biến dạng chỏm xương đùi, ngắn chi thực sự 1cm bên bệnh.',
                         'Khám hai khớp háng ghi nhận hạn chế xoay trong đối xứng cả hai bên (phải nặng hơn trái), '
                         'trên nền bệnh nhân có tiền sử uống thuốc nam giảm đau kéo dài chứa corticoid.'],
    'chan_doan': 'Hoại tử vô mạch chỏm xương đùi phải giai đoạn 3 theo phân loại Ficat-Arlet.',
    'chinh': [   'đau sâu vùng bẹn và mặt trước trong đùi tăng lên rõ rệt khi đứng tỳ trọng lực hoặc đi lại',
                 'hạn chế nặng động tác xoay trong và dạng khớp háng kèm dáng đi khập khiễng chống đau',
                 'tiền sử sử dụng corticoid kéo dài uống nhiều rượu bia hoặc chấn thương gãy cổ xương đùi trước đó'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang khung chậu thẳng và tư thế chân ếch (frog-leg lateral) tìm dấu hiệu hình liềm dưới sụn '
                'hoặc xẹp lún biến dạng chỏm; chỉ định chụp MRI khớp háng hai bên phát hiện hoại tử giai đoạn sớm (dấu '
                'hiệu đường đôi).',
    'kham': 'Khám khớp háng phải thấy biên độ xoay trong giảm nặng chỉ đạt 10 độ kèm đau chói sâu vùng bẹn (bên trái '
            '40 độ), nghiệm pháp Patrick (FABER) dương tính mạnh, dáng đi khập khiễng nghiêng người về bên phải.',
    'nhom': 'người lớn',
    'phu': [   'đau có thể lan xuống mặt trước gối khiến dễ chẩn đoán nhầm sang bệnh khớp gối',
               'teo nhỏ khối cơ vùng mông và cơ đùi bên chân đau khi bệnh kéo dài nhiều tháng',
               'ngắn chi nhẹ bên bệnh ở giai đoạn muộn khi chỏm xương đùi đã bị xẹp lún'],
    'ten': 'hoại tử vô mạch chỏm xương đùi'},
    {   'bien_the_chan_doan': [   'Nang bao hoạt dịch khoeo chân Baker bên phải thứ phát sau thoái hóa khớp gối.',
                              'Nang khoeo chân Baker kích thước lớn gây hạn chế gập gối và tức vùng khoeo.',
                              'Nang Baker khớp gối trái kèm tràn dịch nhẹ ổ khớp gối.',
                              'Theo dõi nang Baker vùng khoeo cần phân biệt với phình động mạch khoeo hoặc huyết khối '
                              'tĩnh mạch sâu.',
                              'Nang bao hoạt dịch khoeo chân Baker mạn tính tái phát ở người trung niên.',
                              'Nang Baker đơn thuần vùng khoeo chân chưa có biến chứng vỡ nang hay chèn ép mạch.'],
    'bien_the_ke_hoach': [   'Chỉ định siêu âm Doppler vùng khoeo chân và khớp gối để xác định kích thước cổ nang '
                             'thông vào khe khớp giữa cơ bụng chân và cơ bán màng, đồng thời loại trừ phình động mạch '
                             'khoeo hoặc huyết khối tĩnh mạch sâu.',
                             'Chụp X-quang khớp gối hoặc MRI khớp gối nếu cần đánh giá nguyên nhân nền bên trong ổ '
                             'khớp như rách sụn chêm trong hay thoái hóa sụn khớp.',
                             'Điều trị nguyên nhân nền trong khớp gối là chủ đạo: nghỉ ngơi giảm tải, chườm lạnh, tập '
                             'mạnh cơ tứ đầu đùi và dùng thuốc kháng viêm NSAID ngắn ngày giảm tiết dịch khớp.',
                             'Thực hiện chọc hút giảm áp dịch trong nang Baker kết hợp tiêm Corticosteroid vào ổ khớp '
                             'gối hoặc vào nang dưới hướng dẫn siêu âm giúp giảm kích thước nang nhanh chóng.',
                             'Băng thun ép nhẹ vùng gối khi đi lại và kê cao chân khi nghỉ ngơi để giảm phù nề ứ trệ '
                             'vùng khoeo.',
                             'Hội chẩn phẫu thuật nội soi khớp gối xử lý rách sụn chêm hoặc cắt bỏ nang qua nội soi '
                             'nếu nang quá to gây chèn ép thần kinh mạch máu hoặc tái phát liên tục.'],
    'bien_the_kham': [   'Vùng hố khoeo chân phải lệch về phía trong có khối u nang hình bầu dục kích thước 4x5cm, mật '
                         'độ căng mềm đàn hồi, khi bệnh nhân gấp gối 45 độ khối nang mềm xẹp đi rõ rệt (dấu hiệu '
                         'Foucher dương tính), không đập theo nhịp mạch.',
                         'Khám gối trái thấy có tràn dịch nhẹ ổ khớp gối kèm một khối phồng căng vùng khoeo sau bên '
                         'trong ấn hơi tức, nghe không có tiếng thổi mạch máu, nghiệm pháp Bào gỗ khớp bánh chè dương '
                         'tính.',
                         'Khối nang vùng khoeo căng chắc khi đứng thẳng duỗi hết gối làm hạn chế 15 độ cuối của động '
                         'tác gập gối tối đa, bắp chân hai bên mềm đều không sưng nóng, dấu hiệu Homan âm tính.',
                         'Sờ thấy khối nang trơn láng ranh giới rõ ở nếp khoeo chân phải, soi đèn qua khối có độ thấu '
                         'quang nhẹ, mạch khoeo và mạch mu chân bắt rõ mạnh đều.',
                         'Bệnh nhân cao tuổi có trục gối vẹo trong nhẹ và lạo xạo khớp gối hai bên, vùng khoeo bên '
                         'trái phồng khối dịch đường kính 3,5cm gây tức bắp chân khi đi bộ lâu.',
                         'Khối nang Baker khoeo chân không dính vào da bên trên, đẩy sang hai bên di động rất hạn chế '
                         'do thông với bao khớp sau, bắp chân không có ban xuất huyết quanh mắt cá.'],
    'chan_doan': 'Nang bao hoạt dịch khoeo chân Baker bên phải thứ phát sau thoái hóa khớp gối.',
    'chinh': [   'xuất hiện khối phồng tròn căng tức ở hố khoeo phía sau đầu gối nhìn rõ hơn khi đứng thẳng duỗi gối',
                 'cảm giác đầy tức vướng víu vùng khoeo chân gây khó khăn khi gập tối đa đầu gối hoặc ngồi xổm',
                 'khối phồng mềm nhỏ đi hoặc lặn bớt vào trong khi gấp đầu gối một góc 45 độ (dấu hiệu Foucher)'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chỉ định siêu âm Doppler vùng khoeo chân và khớp gối để xác định kích thước cổ nang thông vào khe '
                'khớp giữa cơ bụng chân và cơ bán màng, đồng thời loại trừ phình động mạch khoeo hoặc huyết khối tĩnh '
                'mạch sâu.',
    'kham': 'Vùng hố khoeo chân phải lệch về phía trong có khối u nang hình bầu dục kích thước 4x5cm, mật độ căng mềm '
            'đàn hồi, khi bệnh nhân gấp gối 45 độ khối nang mềm xẹp đi rõ rệt (dấu hiệu Foucher dương tính), không đập '
            'theo nhịp mạch.',
    'nhom': 'người lớn',
    'phu': [   'thường đi kèm với bệnh lý thoái hóa khớp gối hoặc rách sụn chêm gây tràn dịch khớp gối mạn tính',
               'nếu nang bị vỡ đột ngột gây đau nhức bắp chân cấp tính và sưng đỏ cẳng chân giống huyết khối tĩnh mạch '
               'sâu',
               'có thể chèn ép nhẹ tĩnh mạch hoặc thần kinh vùng khoeo gây tê bì cẳng chân thoáng qua'],
    'ten': 'nang bao hoạt dịch khoeo chân Baker'},
    {   'bien_the_chan_doan': [   'Hội chứng ma sát dải chậu chày (ITBS) bên phải ở vận động viên chạy bộ.',
                              'Viêm kích thích dải chậu chày tại lồi cầu ngoài xương đùi bên trái.',
                              'Hội chứng dải chậu chày mạn tính kèm co cứng cơ căng mạc đùi và yếu cơ mông nhỡ.',
                              'Hội chứng dải chậu chày mức độ vừa chưa có tràn dịch bao hoạt dịch dưới dải gân.',
                              'Theo dõi hội chứng dải chậu chày cần phân biệt với rách sụn chêm ngoài khớp gối.',
                              'Hội chứng dải chậu chày tái phát do tăng cường độ tập luyện đột ngột.'],
    'bien_the_ke_hoach': [   'Tạm ngưng chạy bộ hoặc đạp xe cường độ cao trong 2-4 tuần để giảm ma sát cấp tính, chườm '
                             'đá mặt ngoài gối 15 phút sau vận động và dùng thuốc kháng viêm NSAID ngắn ngày hoặc gel '
                             'bôi giảm đau.',
                             'Xây dựng chương trình vật lý trị liệu chuyên sâu: lăn ống xốp (foam rolling) thư giãn cơ '
                             'căng mạc đùi và dải chậu chày, kết hợp bài tập tăng cường sức mạnh cơ dạng háng (cơ mông '
                             'nhỡ) như bước đi ngang với dây kháng lực.',
                             'Chỉ định siêu âm phần mềm mặt ngoài gối đánh giá tình trạng phù nề bao hoạt dịch kẹp '
                             'giữa dải chậu chày và lồi cầu ngoài xương đùi, loại trừ tổn thương rách sụn chêm.',
                             'Tư vấn thay giày chạy bộ mới nếu đế giày đã mòn vẹt lệch trục, cân nhắc dùng lót giày '
                             'chỉnh hình nếu có bàn chân bẹt sấp quá mức.',
                             'Tiêm Corticosteroid vào khoang mô liên kết dưới dải chậu chày tại lồi cầu ngoài dưới '
                             'hướng dẫn siêu âm nếu đau kéo dài không cải thiện sau 4-6 tuần tập phục hồi chức năng.',
                             'Hướng dẫn lộ trình quay lại đường chạy từ từ theo nguyên tắc tăng quãng đường không quá '
                             '10% mỗi tuần và tránh chạy trên mặt đường nghiêng một bên.'],
    'bien_the_kham': [   'Ấn chói điểm đau khu trú chính xác trên lồi cầu ngoài xương đùi cách khe khớp ngoài 2cm phía '
                         'trên, nghiệm pháp Noble dương tính rõ (ấn giữ lồi cầu ngoài trong khi duỗi gối từ 90 độ về '
                         '30 độ gây đau nhói).',
                         'Nghiệm pháp Ober dương tính rõ rệt: khi cho bệnh nhân nằm nghiêng bên lành, đùi bên đau '
                         'không thể khép rơi xuống mặt giường do co cứng rút ngắn dải chậu chày và cơ căng mạc đùi.',
                         'Khám khớp gối phải không thấy tràn dịch khớp, các nghiệm pháp đánh giá sụn chêm ngoài '
                         '(McMurray) và dây chằng bên ngoài (Varus stress) đều âm tính, chỉ đau nông dọc dải gân mặt '
                         'ngoài đùi dưới.',
                         'Bệnh nhân chạy bộ phong trào có dấu hiệu yếu cơ dạng háng (cơ mông nhỡ) bên trái khi đứng '
                         'một chân (dấu hiệu Trendelenburg nhẹ), kèm điểm đau bỏng rát trên lồi cầu ngoài xương đùi '
                         'trái.',
                         'Sờ dọc dải chậu chày đoạn 1/3 dưới mặt ngoài đùi thấy căng cứng như sợi dây thừng, ấn điểm '
                         'bám củ Gerdy xương chày không đau nhưng ngay mỏm lồi cầu ngoài đùi đau chói.',
                         'Đánh giá bàn chân có xu hướng sấp bàn chân quá mức (overpronation) khi đứng chịu lực, nghiệm '
                         'pháp Renne dương tính khi bệnh nhân đứng một chân gập gối 30 độ tạo cơn đau mặt ngoài gối.'],
    'chan_doan': 'Hội chứng ma sát dải chậu chày (ITBS) bên phải ở vận động viên chạy bộ.',
    'chinh': [   'đau rát nhói ở mặt ngoài đầu gối ngay trên lồi cầu ngoài xương đùi khi chạy bộ hoặc đạp xe đường dài',
                 'cơn đau thường xuất hiện lặp lại đúng sau một cự ly chạy cố định và hết đau ngay khi dừng nghỉ',
                 'đau tăng rõ rệt khi chạy xuống dốc đi xuống cầu thang hoặc khi gập gối ở góc khoảng 30 độ'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Tạm ngưng chạy bộ hoặc đạp xe cường độ cao trong 2-4 tuần để giảm ma sát cấp tính, chườm đá mặt ngoài '
                'gối 15 phút sau vận động và dùng thuốc kháng viêm NSAID ngắn ngày hoặc gel bôi giảm đau.',
    'kham': 'Ấn chói điểm đau khu trú chính xác trên lồi cầu ngoài xương đùi cách khe khớp ngoài 2cm phía trên, nghiệm '
            'pháp Noble dương tính rõ (ấn giữ lồi cầu ngoài trong khi duỗi gối từ 90 độ về 30 độ gây đau nhói).',
    'nhom': 'người lớn',
    'phu': [   'cảm giác cọ xát lật bật nhẹ bên ngoài gối mỗi lần co duỗi chân',
               'bên trong ổ khớp gối không bị sưng tràn dịch hay kẹt khớp',
               'thường gặp ở vận động viên chạy bộ mới tăng đột ngột quãng đường chạy hoặc người chân vòng kiềng'],
    'ten': 'hội chứng dải chậu chày'},
    {   'bien_the_chan_doan': [   'Viêm gân bánh chè mạn tính bên phải (hội chứng đầu gối người nhảy - Jumper knee).',
                              'Viêm điểm bám gân bánh chè cực dưới xương bánh chè hai bên giai đoạn 2.',
                              'Bệnh lý thoái hóa vi rách gân bánh chè mạn tính ở vận động viên thể thao.',
                              'Viêm gân bánh chè mức độ trung bình chưa có dấu hiệu đứt bán phần gân.',
                              'Theo dõi viêm gân bánh chè cần phân biệt với hội chứng đau khớp chè đùi.',
                              'Viêm gân bánh chè tái phát do tập bật nhảy quá tải kéo dài.'],
    'bien_the_ke_hoach': [   'Điều chỉnh cường độ tập luyện tránh các động tác bật nhảy tiếp đất mạnh, sử dụng đai '
                             'băng hỗ trợ gân bánh chè (patellar strap) khi vận động và chườm lạnh 15 phút sau tập.',
                             'Hướng dẫn chương trình bài tập tăng sức bền gân ly tâm trên ván nghiêng 25 độ (eccentric '
                             'decline squat) và bài tập đẳng trường giữ tĩnh giúp giảm đau gân hiệu quả.',
                             'Chỉ định siêu âm gân cơ vùng trước gối đánh giá độ dày sợi gân, vùng giảm âm thoái hóa '
                             'và tân tạo mạch máu quanh cực dưới xương bánh chè.',
                             'Uống thuốc giảm đau kháng viêm NSAID ngắn ngày trong đợt đau cấp, không tiêm corticoid '
                             'trực tiếp vào thân gân bánh chè vì nguy cơ cao gây đứt gân thứ phát.',
                             'Cân nhắc liệu pháp sóng xung kích ngoài cơ thể (ESWT) hoặc tiêm huyết tương giàu tiểu '
                             'cầu (PRP) nếu bệnh nhân đau mạn tính kháng trị sau 8 tuần tập phục hồi.',
                             'Tư vấn kéo giãn nhóm cơ tứ đầu đùi và cơ gân kheo hàng ngày nhằm giảm lực kéo căng quá '
                             'mức lên điểm bám gân bánh chè.'],
    'bien_the_kham': [   'Ấn đau nhói điểm bám tận gân bánh chè tại cực dưới xương bánh chè phải (dấu hiệu Basset '
                         'dương tính khi gối duỗi, giảm khi gối gập 90 độ căng gân), động tác duỗi gối kháng lực gây '
                         'đau tái hiện rõ.',
                         'Khám gối trái thấy vùng gân bánh chè ngay dưới cực dưới xương bánh chè hơi dày nề nhẹ không '
                         'đỏ da, thực hiện đứng lên ngồi xuống trên một chân (single-leg decline squat) gây đau tăng '
                         'vọt.',
                         'Không có dấu hiệu bập bềnh xương bánh chè, các dây chằng chéo và sụn chêm vững chắc, chỉ khu '
                         'trú đau tại 1/3 trên gân bánh chè và cơ tứ đầu đùi hơi co rút ngắn.',
                         'Bệnh nhân chơi bóng chuyền lâu năm có sờ thấy hạt xơ nhỏ dày cứng tại gân bánh chè hai bên, '
                         'ấn đau bên phải nhiều hơn, phản xạ gân bánh chè hai bên bình thường.',
                         'Test nghiêng ván dốc 25 độ gây đau nhói vùng dưới xương bánh chè ở góc gập 45 độ, độ linh '
                         'hoạt cơ gân kheo (hamstring) và cơ bắp chân giảm rõ rệt.',
                         'Khớp gối hoàn toàn không có tiếng lạo xạo sụn chè đùi (nghiệm pháp Clark âm tính), điểm đau '
                         'chính xác cách khe khớp 1cm phía trước trên dây chằng bánh chè.'],
    'chan_doan': 'Viêm gân bánh chè mạn tính bên phải (hội chứng đầu gối người nhảy - Jumper knee).',
    'chinh': [   'đau nhói chính xác ở cực dưới xương bánh chè ngay điểm bám gân bánh chè khi bật nhảy hoặc tiếp đất',
                 'đau tăng rõ rệt khi ngồi xổm xuống sâu hoặc khi bước xuống cầu thang và đứng dậy sau khi ngồi lâu '
                 '(dấu hiệu rạp chiếu phim)',
                 'ấn chói khu trú cực dưới xương bánh chè khi gối duỗi thẳng và gân thả lỏng'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Điều chỉnh cường độ tập luyện tránh các động tác bật nhảy tiếp đất mạnh, sử dụng đai băng hỗ trợ gân '
                'bánh chè (patellar strap) khi vận động và chườm lạnh 15 phút sau tập.',
    'kham': 'Ấn đau nhói điểm bám tận gân bánh chè tại cực dưới xương bánh chè phải (dấu hiệu Basset dương tính khi '
            'gối duỗi, giảm khi gối gập 90 độ căng gân), động tác duỗi gối kháng lực gây đau tái hiện rõ.',
    'nhom': 'người lớn',
    'phu': [   'thường gặp ở người chơi bóng chuyền bóng rổ nhảy cao (jumper knee)',
               'sưng dày nhẹ vùng gân bánh chè ngay dưới đầu gối không kèm tràn dịch trong ổ khớp',
               'cứng nhẹ mặt trước gối vào buổi sáng nhưng bớt đau sau khi khởi động làm nóng cơ'],
    'ten': 'viêm gân bánh chè'},
    {   'bien_the_chan_doan': [   'Thoái hóa khớp bàn ngón tay và khớp thang bàn ngón cái hai bên nguyên phát.',
                              'Thoái hóa khớp liên đốt ngón tay có hạt Heberden và Bouchard điển hình.',
                              'Thoái hóa khớp gốc ngón cái (rhizarthrosis) mức độ vừa hai bàn tay.',
                              'Thoái hóa khớp bàn ngón tay thể bào mòn (erosive hand osteoarthritis) đợt đau tiến '
                              'triển.',
                              'Thoái hóa đa khớp bàn tay mạn tính ở người cao tuổi gây giảm lực kẹp véo.',
                              'Theo dõi thoái hóa khớp bàn ngón tay cần phân biệt với viêm khớp vảy nến.'],
    'bien_the_ke_hoach': [   'Chụp X-quang hai bàn tay tư thế thẳng và chếch đánh giá mức độ hẹp khe khớp, đặc xương '
                             'dưới sụn, gai xương rìa khớp và biến dạng khớp thang bàn ngón cái.',
                             'Làm xét nghiệm máu kiểm tra yếu tố dạng thấp RF, Anti-CCP, CRP và acid uric nếu cần phân '
                             'biệt với viêm khớp dạng thấp hoặc gout mạn tính.',
                             'Điều trị ưu tiên dùng thuốc bôi tại chỗ nhóm NSAID (gel Diclofenac 1%) bôi lên các khớp '
                             'ngón tay 3-4 lần/ngày để an toàn cho dạ dày và thận ở người lớn tuổi.',
                             'Kết hợp ngâm tay nước ấm hoặc đắp sáp parafin nóng buổi sáng giúp giảm cứng khớp, sử '
                             'dụng nẹp mềm nâng đỡ khớp gốc ngón cái khi làm việc nặng.',
                             'Kê đơn Acetaminophen hoặc thuốc giảm đau chống viêm đường uống ngắn ngày (hoặc '
                             'Chondroitin sulfate hỗ trợ) khi có đợt bùng phát đau sưng nhiều khớp.',
                             'Hướng dẫn bài tập vật lý trị liệu vận động nhẹ nhàng các khớp ngón tay và sử dụng dụng '
                             'cụ hỗ trợ mở nắp hộp cầm nắm cán to để bảo vệ khớp.'],
    'bien_the_kham': [   'Khám hai bàn tay thấy nhiều nốt u xương cứng chắc đối xứng hai bên tại các khớp liên đốt xa '
                         'ngón 2, 3, 5 (nốt Heberden) và khớp liên đốt gần ngón 3 (nốt Bouchard), đầu ngón tay hơi '
                         'lệch trục nhẹ, khớp cổ tay bình thường.',
                         'Khớp thang bàn ngón cái (CMC 1) bên phải biến dạng vuông góc (square shoulder sign) do bán '
                         'trật nhẹ xương bàn 1, thực hiện nghiệm pháp nghiền (grind test) gây đau chói kèm tiếng lạo '
                         'xạo thô.',
                         'Các khớp bàn ngón tay (MCP) hoàn toàn bình thường không sưng nóng (giúp phân biệt với viêm '
                         'khớp dạng thấp), chủ yếu tổn thương biến dạng phì đại đầu xương ở khớp liên đốt xa và gốc '
                         'ngón cái.',
                         'Bàn tay mất khả năng nắm chặt hoàn toàn các đầu ngón tay chạm vào nếp lằn lòng bàn tay, sờ '
                         'vào các hạt nổi gồ trên khớp ngón tay thấy cứng như xương không ấn lõm, da phủ bình thường.',
                         'Bệnh nhân than đau buốt gốc ngón cái hai bên khi làm động tác vắt quần áo, khám thấy hạn chế '
                         'động tác đối chiếu ngón cái chạm gốc ngón út kèm teo nhẹ cơ mô cái.',
                         'Phát hiện một vài nang nhầy nhỏ căng trong suốt ngay cạnh khớp liên đốt xa ngón trỏ (nang '
                         'nhầy thoái hóa) kèm nốt Heberden đặc trưng hai bàn tay.'],
    'chan_doan': 'Thoái hóa khớp bàn ngón tay và khớp thang bàn ngón cái hai bên nguyên phát.',
    'chinh': [   'xuất hiện các nốt u cục xương cứng ở mặt lưng bên các khớp liên đốt ngón tay xa (hạt Heberden) và '
                 'liên đốt gần (hạt Bouchard)',
                 'đau âm ỉ và biến dạng vẹo lệch trục các đầu ngón tay kèm đau gốc ngón tay cái khi véo hoặc vặn nắm',
                 'cứng các khớp ngón tay thoáng qua vào buổi sáng dưới 30 phút và khớp đau tăng khi làm việc tay chân '
                 'nhiều'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang hai bàn tay tư thế thẳng và chếch đánh giá mức độ hẹp khe khớp, đặc xương dưới sụn, gai '
                'xương rìa khớp và biến dạng khớp thang bàn ngón cái.',
    'kham': 'Khám hai bàn tay thấy nhiều nốt u xương cứng chắc đối xứng hai bên tại các khớp liên đốt xa ngón 2, 3, 5 '
            '(nốt Heberden) và khớp liên đốt gần ngón 3 (nốt Bouchard), đầu ngón tay hơi lệch trục nhẹ, khớp cổ tay '
            'bình thường.',
    'nhom': 'người lớn',
    'phu': [   'giảm lực cầm nắm bóp kẹp khiến dễ làm rơi chén bát hoặc khó mở nắp lọ chặt',
               'nghe tiếng lạo xạo lụp cụp nhỏ khi gấp duỗi các khớp ngón tay hoặc xoay gốc ngón cái',
               'có thể xen kẽ từng đợt sưng ấm nhẹ tại các khớp ngón tay bị thoái hóa kích thích'],
    'ten': 'thoái hóa khớp bàn ngón tay'},
    {   'bien_the_chan_doan': [   'Biến dạng ngón chân cái vẹo ngoài (Hallux valgus) hai bên mức độ trung bình.',
                              'Biến dạng Hallux valgus bên phải biến chứng viêm bao hoạt dịch bunion cấp.',
                              'Ngón chân cái vẹo ngoài Hallux valgus nặng gây chồng chéo ngón chân thứ hai.',
                              'Biến dạng ngón chân cái vẹo ngoài kèm đau đầu xương bàn chân chuyển tải '
                              '(metatarsalgia).',
                              'Biến dạng Hallux valgus mức độ nhẹ đáp ứng tốt với chỉnh hình bảo tồn giày dép.',
                              'Ngón chân cái vẹo ngoài mạn tính cần đánh giá chỉ định phẫu thuật cắt xương chỉnh '
                              'trục.'],
    'bien_the_ke_hoach': [   'Chụp X-quang hai bàn chân tư thế thẳng và nghiêng có chịu lực (đứng thẳng) để đo chính '
                             'xác góc vẹo ngoài (HVA > 15 độ) và góc gian xương bàn 1-2 (IMA) cũng như đánh giá thoái '
                             'hóa khớp kèm theo.',
                             'Tư vấn thay đổi ngay thói quen mang giày: chọn giày mũi rộng thoải mái, đế thấp mềm, '
                             'tránh tuyệt đối giày mũi nhọn và giày cao gót trên 3-4cm.',
                             'Sử dụng miếng đệm silicon ngăn cách giữa ngón cái và ngón hai, miếng dán bảo vệ khối '
                             'bunion tránh cọ xát và lót giày nâng vòm bàn chân nếu kèm bàn chân bẹt.',
                             'Điều trị đợt viêm đỏ bao hoạt dịch bunion bằng chườm lạnh, kê chân nghỉ ngơi và thuốc '
                             'kháng viêm NSAID đường uống trong 5-7 ngày.',
                             'Hướng dẫn các bài tập kéo giãn cơ khép ngón cái và tập mạnh cơ vòm bàn chân để hạn chế '
                             'tiến triển nặng thêm biến dạng.',
                             'Hội chẩn chuyên khoa Chấn thương chỉnh hình bàn chân lên kế hoạch phẫu thuật chỉnh trục '
                             'xương bàn ngón cái (như phẫu thuật Scarf hoặc Chevron osteotomy) nếu đau mạn tính ảnh '
                             'hưởng nặng sinh hoạt.'],
    'bien_the_kham': [   'Bàn chân phải ở tư thế đứng chịu lực thấy ngón chân cái vẹo lệch ra ngoài góc khoảng 30 độ '
                         'đè nhẹ dưới ngón thứ 2, đầu xương bàn 1 nhô gồ rõ ở bờ trong tạo cục bunion đỏ nhẹ, ấn vào '
                         'bao hoạt dịch bên trên đau tức.',
                         'Biến dạng Hallux valgus hai bàn chân đối xứng, mặt trong khớp bàn ngón 1 bên trái có vùng da '
                         'dày sừng hồng nhẹ do ma sát giày, bàn chân bẹt vòm dọc trong sụp nhẹ.',
                         'Khám vận động thụ động thấy khớp bàn ngón chân cái bên phải còn nắn chỉnh thẳng trục được '
                         'một phần (biến dạng còn mềm dẻo nhẹ), gấp duỗi khớp còn 50 độ không có tiếng lạo xạo thoái '
                         'hóa nặng.',
                         'Đo góc vẹo ngoài ngón cái lâm sàng lớn hơn 35 độ kèm xoay sấp nhẹ thân ngón cái (pronation), '
                         'dưới lòng bàn chân vùng khớp bàn ngón 2-3 có nốt chai sừng đau khi ấn trực tiếp.',
                         'Khối lồi bunion bờ trong bàn chân trái sưng nóng đỏ tấy nhẹ do viêm bao hoạt dịch thứ phát '
                         'từ đi giày cao gót chật mũi, ngón chân thứ 2 bắt đầu bị đẩy gập lên dạng ngón búa.',
                         'Thử nghiệm kiểm tra mạch mu chân và chày sau bắt rõ đều, cảm giác da các ngón chân nguyên '
                         'vẹn, biên độ khớp cổ chân bình thường.'],
    'chan_doan': 'Biến dạng ngón chân cái vẹo ngoài (Hallux valgus) hai bên mức độ trung bình.',
    'chinh': [   'ngón chân cái bị nghiêng vẹo lệch ra phía ngoài ép sát hoặc chèn lên ngón chân thứ hai',
                 'xuất hiện khối xương gồ lồi to (bunion) ở mặt trong khớp bàn ngón chân cái đỏ đau do cọ xát với '
                 'thành giày',
                 'đau nhức buốt vùng khớp gốc ngón cái tăng lên nhiều khi đi bộ đứng lâu hoặc mang giày mũi nhọn chật'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang hai bàn chân tư thế thẳng và nghiêng có chịu lực (đứng thẳng) để đo chính xác góc vẹo '
                'ngoài (HVA > 15 độ) và góc gian xương bàn 1-2 (IMA) cũng như đánh giá thoái hóa khớp kèm theo.',
    'kham': 'Bàn chân phải ở tư thế đứng chịu lực thấy ngón chân cái vẹo lệch ra ngoài góc khoảng 30 độ đè nhẹ dưới '
            'ngón thứ 2, đầu xương bàn 1 nhô gồ rõ ở bờ trong tạo cục bunion đỏ nhẹ, ấn vào bao hoạt dịch bên trên đau '
            'tức.',
    'nhom': 'người lớn',
    'phu': [   'hình thành vết chai sần dày cứng dưới lòng bàn chân vùng chỏm xương bàn 2-3 do phân bố lại áp lực tỳ '
               'đè',
               'da vùng khớp gồ mặt trong ngón cái hay bị phồng rộp sưng đỏ tấy từng đợt khi đi giày kín',
               'bàn chân trước bè ngang rộng ra bất thường khiến khó chọn mua giày dép vừa vặn'],
    'ten': 'biến dạng ngón chân cái vẹo ngoài Hallux valgus'},
    {   'bien_the_chan_doan': [   'Biến dạng ngón chân hình búa (Hammer toe) ngón 2 bàn chân phải thể cứng cố định.',
                              'Ngón chân hình búa thể mềm dẻo ngón 2 và 3 hai bàn chân.',
                              'Ngón chân hình búa thứ phát đi kèm biến dạng Hallux valgus.',
                              'Biến dạng ngón chân hình búa có viêm bao hoạt dịch ma sát và chai sừng mặt lưng.',
                              'Ngón chân hình búa mức độ nặng biến chứng bán trật khớp bàn ngón 2.',
                              'Ngón chân hình búa mạn tính ở người lớn cần cân nhắc phẫu thuật chỉnh hình gân xương.'],
    'bien_the_ke_hoach': [   'Chụp X-quang bàn chân tư thế đứng chịu lực thẳng và nghiêng đánh giá tình trạng bán trật '
                             'khớp bàn ngón chân, thoái hóa khớp liên đốt và độ dài xương bàn chân.',
                             'Tư vấn chuyển sang mang giày có mũi giày cao và rộng rãi (deep toe box), chất liệu da '
                             'mềm co giãn, tránh giày cao gót làm dồn lực trượt ngón chân về phía trước.',
                             'Sử dụng vòng đệm silicon bọc ngón chân hoặc miếng lót đỡ vòm ngang (metatarsal pad) đặt '
                             'phía sau chỏm xương bàn chân để giải phóng áp lực và kéo duỗi nhẹ ngón búa thể mềm.',
                             'Hướng dẫn bệnh nhân tự xoa bóp kéo giãn nhẹ nhàng ngón chân bị co rút hàng ngày kết hợp '
                             'bài tập dùng các ngón chân nhặt khăn hoặc viên bi để cân bằng lực cơ nội tại bàn chân.',
                             'Chăm sóc làm mềm và bào mỏng nhẹ nhàng vùng da chai sừng sau khi ngâm chân nước ấm, '
                             'tuyệt đối không tự ý cắt gọt sâu hay dùng axit dán chai chân đặc biệt ở người có bệnh lý '
                             'mạch máu hoặc tiểu đường.',
                             'Hội chẩn Ngoại Chỉnh hình thực hiện tiểu phẫu chuyển gân gấp sang gân duỗi (cho thể mềm) '
                             'hoặc phẫu thuật cắt chỏm đốt gần làm thẳng khớp PIP (cho thể cứng cố định) nếu đau dai '
                             'dẳng.'],
    'bien_the_kham': [   'Ngón chân thứ 2 bàn chân phải có tư thế gấp cứng tại khớp liên đốt gần (PIP) và ưỡn quá mức '
                         'khớp bàn ngón (MTP), mặt mu khớp PIP có cục chai sừng dày tròn đỏ nhẹ ấn đau chói, dùng tay '
                         'nắn không duỗi thẳng ra được.',
                         'Khám bàn chân trái thấy cả ngón chân 2 và 3 đều biến dạng kiểu hình búa còn mềm dẻo (khi đẩy '
                         'nhẹ dưới chỏm xương bàn thì ngón chân duỗi thẳng lại được), chưa có vết loét trợt.',
                         'Ngón chân cái vẹo ngoài chèn đẩy làm ngón chân thứ 2 bị gập vồng lên trên tạo thành ngón '
                         'chân hình búa điển hình, đầu ngón 2 có nốt chai cứng tiếp xúc trực tiếp mặt sàn.',
                         'Bệnh nhân than đau rát dữ dội mỗi khi xỏ giày tây đi làm, khám thấy đỉnh gập khớp liên đốt '
                         'gần ngón 2 đỏ ửng sưng nề bao hoạt dịch giả do ma sát, mạch mu chân và cảm giác ngón chân '
                         'bình thường.',
                         'Khám lòng bàn chân ngay dưới chỏm xương bàn chân ngón 2 có lớp da sừng dày ấn đau buốt (dấu '
                         'hiệu quá tải chỏm xương bàn thứ phát), các ngón chân còn lại thẳng trục.',
                         'Ngón chân hình búa cứng cố định lâu năm kèm bán trật nhẹ lên trên tại khớp bàn ngón thứ 2, '
                         'bệnh nhân phải cắt khoét lỗ trên mũi giày vải để tránh cọ đau.'],
    'chan_doan': 'Biến dạng ngón chân hình búa (Hammer toe) ngón 2 bàn chân phải thể cứng cố định.',
    'chinh': [   'ngón chân thứ hai hoặc thứ ba bị co quắp gập xuống giống hình chiếc búa tại khớp liên đốt gần',
                 'hình thành mắt cá hoặc vết chai sừng đau buốt ở mặt mu đốt ngón chân do cọ xát liên tục vào mặt trên '
                 'mũi giày',
                 'đầu mút ngón chân cắm thẳng xuống đế giày gây đau nhức và chai cứng ở đầu ngón chân khi bước đi'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang bàn chân tư thế đứng chịu lực thẳng và nghiêng đánh giá tình trạng bán trật khớp bàn '
                'ngón chân, thoái hóa khớp liên đốt và độ dài xương bàn chân.',
    'kham': 'Ngón chân thứ 2 bàn chân phải có tư thế gấp cứng tại khớp liên đốt gần (PIP) và ưỡn quá mức khớp bàn ngón '
            '(MTP), mặt mu khớp PIP có cục chai sừng dày tròn đỏ nhẹ ấn đau chói, dùng tay nắn không duỗi thẳng ra '
            'được.',
    'nhom': 'người lớn',
    'phu': [   'thường đi kèm với biến dạng ngón chân cái vẹo ngoài hoặc bàn chân vòm cao',
               'khớp liên đốt ngón chân lâu ngày trở nên cứng đơ không thể dùng tay kéo duỗi thẳng lại được',
               'có thể bị loét trợt hoặc bội nhiễm nhẹ tại đỉnh chai mặt lưng ngón chân nếu cọ xát mạnh'],
    'ten': 'ngón chân hình búa'},
    {   'bien_the_chan_doan': [   'Viêm cấp bao hoạt dịch sau gân gót cổ chân (retrocalcaneal bursitis) do ma sát giày.',
                              'Viêm bao hoạt dịch dưới da gót chân cấp tính bên phải sau đi bộ đường dài.',
                              'Viêm bao hoạt dịch quanh mắt cá ngoài cổ chân cấp tính thể vô khuẩn.',
                              'Viêm bao hoạt dịch khớp cổ chân cấp kèm kích thích điểm bám gân Achilles.',
                              'Theo dõi viêm bao hoạt dịch cổ chân cấp cần phân biệt với viêm gân gót hoặc bệnh '
                              'Haglund.',
                              'Viêm bao hoạt dịch cổ chân cấp tính mức độ vừa đáp ứng tốt điều trị bảo tồn.'],
    'bien_the_ke_hoach': [   'Siêu âm phần mềm vùng cổ chân và gân gót xác định túi hoạt dịch giãn chứa dịch viêm khu '
                             'trú và đánh giá tình trạng gân Achilles đi kèm; chụp X-quang cổ chân nghiêng tìm gai lồi '
                             'xương gót Haglund nếu tái diễn.',
                             'Cho cổ chân nghỉ ngơi, tạm thời đi dép hở gót hoặc giày thể thao cổ thấp gót mềm để loại '
                             'bỏ hoàn toàn ma sát tỳ đè lên vùng bao hoạt dịch sưng đau.',
                             'Chườm đá lạnh vùng cổ chân 15 phút ngày 3 lần trong 48-72 giờ đầu, kê đơn thuốc kháng '
                             'viêm giảm đau đường uống Celecoxib hoặc Ibuprofen trong 5-7 ngày kết hợp bôi gel kháng '
                             'viêm tại chỗ.',
                             'Đặt miếng đệm silicon nâng gót chân nhẹ trong giày giúp giảm góc gập mu và giảm áp lực '
                             'tỳ nén trực tiếp lên bao hoạt dịch sau xương gót.',
                             'Phối hợp vật lý trị liệu siêu âm trị liệu, điện xung giảm đau và hướng dẫn bài tập kéo '
                             'giãn cơ bắp chân nhẹ nhàng khi đã qua giai đoạn đau cấp.',
                             'Lưu ý thận trọng tránh tiêm corticoid gần gân gót vì nguy cơ cao gây đứt gân Achilles; '
                             'chỉ cân nhắc chọc hút dịch hoặc tiêm định vị siêu âm ở các túi hoạt dịch xa gân lớn.'],
    'bien_the_kham': [   'Vùng sau cổ chân ngay phía trước điểm bám gân Achilles sưng phồng đều hai bên khe gân tạo '
                         'khối mềm bùng nhùng, ấn vào hai bên gân gót đau nhói rõ (viêm bao hoạt dịch sau xương gót), '
                         'gập mu bàn chân tối đa gây căng đau vùng gót sau.',
                         'Ngay trên mắt cá ngoài cổ chân phải có bọc sưng căng mềm kích thước 3x3cm ranh giới rõ không '
                         'lan vào khe khớp cổ chân, da trên khối hơi đỏ ấm do ma sát quai dép, khớp sên chày vững chắc '
                         'khi làm test ngăn kéo trước.',
                         'Khám cổ chân trái thấy khối sưng khu trú ngay phía sau gân gót (viêm bao hoạt dịch dưới da '
                         'gót chân) bề mặt da ửng đỏ dày nhẹ do cọ sát gót giày cứng, điểm bám gân gót không có khe '
                         'khuyết đứt gân, test Thompson âm tính.',
                         'Bệnh nhân đi hơi nhón gót để tránh căng vùng cổ chân sau, sờ nắn dọc thân gân gót bình '
                         'thường không sưng cục nhưng khoang tam giác Kager phía trước gân sưng đầy ấn đau tức.',
                         'Vùng mắt cá trong cổ chân phải sưng một túi dịch nhỏ mềm ấn lún, không có điểm đau dọc mắt '
                         'cá xương chày hay xương mác, vận động xoay lật cổ chân trong biên độ sinh lý không đau.',
                         'Khám thấy cổ chân không có tràn dịch ổ khớp lớn, mạch mu chân và chày sau đập rõ, không có '
                         'dấu hiệu nhiễm trùng lan tỏa hay hạch bẹn sưng đau.'],
    'chan_doan': 'Viêm cấp bao hoạt dịch sau gân gót cổ chân (retrocalcaneal bursitis) do ma sát giày.',
    'chinh': [   'sưng phồng một vùng mềm căng tức khu trú ngay phía sau gân gót (sau xương gót) hoặc quanh mắt cá '
                 'ngoài cổ chân',
                 'đau nhói vùng cổ chân mỗi khi gập duỗi bàn chân tối đa hoặc khi thành sau cổ giày tỳ ép vào gót chân',
                 'da tại vùng sưng nề có thể hơi ấm và đỏ nhẹ khu trú nhưng khớp cổ chân chịu lực vẫn vững chắc'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Siêu âm phần mềm vùng cổ chân và gân gót xác định túi hoạt dịch giãn chứa dịch viêm khu trú và đánh '
                'giá tình trạng gân Achilles đi kèm; chụp X-quang cổ chân nghiêng tìm gai lồi xương gót Haglund nếu '
                'tái diễn.',
    'kham': 'Vùng sau cổ chân ngay phía trước điểm bám gân Achilles sưng phồng đều hai bên khe gân tạo khối mềm bùng '
            'nhùng, ấn vào hai bên gân gót đau nhói rõ (viêm bao hoạt dịch sau xương gót), gập mu bàn chân tối đa gây '
            'căng đau vùng gót sau.',
    'nhom': 'người lớn',
    'phu': [   'tiền sử mới đi giày mới cổ cứng chật gót chạy bộ đường dài hoặc đi bộ leo dốc nhiều',
               'đau tăng khi nhón gót chân lên cao hoặc ấn bóp ngang hai bên ngay phía trước gân gót Achilles',
               'không có tiền sử lật sơ mi trẹo cổ chân cấp tính hay vết bầm tím tụ máu lan tỏa'],
    'ten': 'viêm bao hoạt dịch khớp cổ chân'},
    {   'bien_the_chan_doan': [   'Gãy kín 1/3 giữa xương đòn phải di lệch vừa sau ngã đập vai.',
                              'Gãy kín xương đòn trái thể cành tươi không di lệch ở trẻ em.',
                              'Gãy kín đầu ngoài xương đòn phải có tổn thương dây chằng quạ đòn kèm theo.',
                              'Gãy kín 1/3 giữa xương đòn trái có mảnh rời thứ ba chưa biến chứng mạch máu thần kinh.',
                              'Gãy kín xương đòn cấp tính do chấn thương thể thao không có tổn thương phổi màng phổi.',
                              'Gãy kín xương đòn phải cần bất động đai số 8 hoặc phẫu thuật kết hợp xương.'],
    'bien_the_ke_hoach': [   'Chụp X-quang xương đòn thẳng và tư thế chếch lên 20 độ (Zanca view) đánh giá chính xác '
                             'vị trí gãy, mức độ chồng ngắn và di lệch ổ gãy; kiểm tra luôn vùng đỉnh phổi cùng bên '
                             'loại trừ tràn khí màng phổi.',
                             'Đánh giá cẩn thận tình trạng mạch quay, màu sắc đầu chi, cảm giác vận động thần kinh '
                             'ngoại vi chi trên và kiểm tra vùng da trên đầu xương gãy có bị căng trắng dọa thủng hay '
                             'không.',
                             'Điều trị bảo tồn cho đa số trường hợp gãy ít di lệch hoặc trẻ em: bất động bằng đai số 8 '
                             'chỉnh nhẹ hai vai ra sau hoặc túi treo tay (arm sling) trong 4-6 tuần kết hợp thuốc giảm '
                             'đau Paracetamol hoặc Ibuprofen.',
                             'Hội chẩn phẫu thuật Chấn thương chỉnh hình kết hợp xương bằng nẹp vít hoặc đinh nội tủy '
                             'nếu xương đòn gãy di lệch chồng ngắn trên 2cm, có đầu xương nhọn dọa chọc thủng da, gãy '
                             'nhiều mảnh hoặc gãy đầu ngoài mất vững.',
                             'Hướng dẫn bệnh nhân giữ nguyên đai bất động kể cả khi ngủ (nằm ngửa kê gối mỏng giữa hai '
                             'bả vai), thường xuyên cử động các ngón tay cổ tay và khuỷu tay để tránh cứng khớp.',
                             'Hẹn tái khám chụp X-quang kiểm tra can xương sau 2 tuần và 6 tuần, hướng dẫn tập phục '
                             'hồi tầm vận động vai tăng dần khi ổ gãy đã liền vững.'],
    'bien_the_kham': [   'Vai phải sệ thấp hơn vai trái, bệnh nhân dùng tay trái nâng đỡ khuỷu tay phải ép sát thân '
                         'mình; quan sát vùng 1/3 giữa xương đòn phải có khối gồ nhô cao dưới da kèm sưng nề và mảng '
                         'bầm tím mới, ấn nhẹ có điểm đau chói và cử động bất thường nhưng da nguyên vẹn không dọa '
                         'chọc thủng.',
                         'Sờ dọc bờ trên xương đòn trái từ khớp ức đòn ra ngoài thấy mất liên tục rõ rệt tại đoạn 1/3 '
                         'giữa, đầu gãy trong nhô lên trên do cơ ức đòn chũm kéo, mạch quay bắt rõ đều và cảm giác vận '
                         'động các ngón tay hoàn toàn bình thường.',
                         'Trẻ em sau ngã xe đạp chống tay trái đau khóc nhiều không chịu cử động tay trái, khám vùng '
                         'xương đòn trái thấy sưng nề khu trú đoạn giữa và ấn đau chói (nghi gãy cành tươi xương đòn), '
                         'phổi hai bên rì rào phế nang đều rõ không tràn khí màng phổi.',
                         'Biến dạng gập góc rõ tại 1/3 ngoài xương đòn phải kèm dấu hiệu phím đàn nhẹ tại vùng khớp '
                         'cùng đòn, không có dấu hiệu tổn thương đám rối thần kinh cánh tay hay mạch máu dưới đòn.',
                         'Vùng hố trên đòn đầy nề tụ máu nhẹ, bệnh nhân nghiêng đầu nhẹ sang bên đau để làm chùng cơ '
                         'ức đòn chũm giúp giảm đau, sờ đầu xương gãy sắc nhọn dưới da nhưng không có dấu hiệu thiếu '
                         'máu trắng da đe dọa hoại tử.',
                         'Khám lồng ngực và hô hấp ổn định SpO2 99%, tim đều, ổ gãy kín xương đòn trái không có tiếng '
                         'lạo xạo khí dưới da vùng cổ ngực.'],
    'chan_doan': 'Gãy kín 1/3 giữa xương đòn phải di lệch vừa sau ngã đập vai.',
    'chinh': [   'đau nhói dữ dội vùng vai và xương đòn ngay sau khi ngã chống tay hoặc ngã đập vai trực tiếp xuống '
                 'đất',
                 'bên vai bị chấn thương sệ thấp xuống và hơi đổ ra trước kèm bệnh nhân phải dùng tay lành đỡ lấy '
                 'khuỷu tay bên đau',
                 'nhìn thấy gồ xương biến dạng mất liên tục rõ rệt dưới da dọc thân xương đòn kèm bầm tím sưng nề'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chụp X-quang xương đòn thẳng và tư thế chếch lên 20 độ (Zanca view) đánh giá chính xác vị trí gãy, '
                'mức độ chồng ngắn và di lệch ổ gãy; kiểm tra luôn vùng đỉnh phổi cùng bên loại trừ tràn khí màng '
                'phổi.',
    'kham': 'Vai phải sệ thấp hơn vai trái, bệnh nhân dùng tay trái nâng đỡ khuỷu tay phải ép sát thân mình; quan sát '
            'vùng 1/3 giữa xương đòn phải có khối gồ nhô cao dưới da kèm sưng nề và mảng bầm tím mới, ấn nhẹ có điểm '
            'đau chói và cử động bất thường nhưng da nguyên vẹn không dọa chọc thủng.',
    'nhom': 'cả hai',
    'phu': [   'sờ nhẹ dọc xương đòn phát hiện điểm đau chói cố định dấu hiệu lạo xạo xương hoặc đầu xương gãy gồ lên '
               'dưới da',
               'không thể tự nhấc cánh tay bên đau lên khỏi thân người vì đau giật tại ổ gãy',
               'không có vết thương hở thông vào ổ gãy da phủ trên chỗ gồ vẫn còn nguyên vẹn'],
    'ten': 'gãy kín xương đòn do ngã'},
    {   'bien_the_chan_doan': [   'Trật khớp vai tái hồi ra trước bên phải sau chấn thương thể thao.',
                              'Mất vững khớp vai mạn tính gây trật khớp vai tái hồi nhiều lần nghi rách sụn viền '
                              'Bankart.',
                              'Trật khớp vai tái hồi hai bên trên nền cơ địa lỏng lẻo dây chằng toàn thân.',
                              'Trật khớp vai tái hồi có tổn thương khuyết xương chỏm cánh tay (Hill-Sachs) và bờ ổ '
                              'chảo.',
                              'Bán trật khớp vai ra trước tái diễn ở vận động viên ném bóng.',
                              'Trật khớp vai tái hồi mức độ nặng cần phẫu thuật nội soi khâu sụn viền.'],
    'bien_the_ke_hoach': [   'Chụp X-quang khớp vai thẳng và tư thế Stryker notch hoặc West Point để phát hiện tổn '
                             'thương lõm xương Hill-Sachs ở chỏm cánh tay và mẻ bờ trước dưới ổ chảo (Bankart xương).',
                             'Chỉ định chụp cộng hưởng từ khớp vai có tiêm thuốc cản từ nội khớp (MRA) đánh giá chi '
                             'tiết mức độ rách sụn viền ổ chảo trước dưới, giãn bao khớp và rách dây chằng ổ chảo cánh '
                             'tay.',
                             'Hội chẩn Chấn thương chỉnh hình phẫu thuật nội soi khâu phục hồi sụn viền Bankart và '
                             'khâu thu hẹp bao khớp (hoặc phẫu thuật chuyển khối xương Latarjet nếu khuyết xương ổ '
                             'chảo lớn trên 20%).',
                             'Trong thời gian chờ mổ hoặc đối với người lỏng lẻo đa hướng không do chấn thương: áp '
                             'dụng chương trình tập phục hồi chức năng chuyên sâu tăng cường nhóm cơ chóp xoay (đặc '
                             'biệt cơ dưới vai) và cơ ổn định xương bả vai.',
                             'Hướng dẫn bệnh nhân tuyệt đối tránh tư thế nguy hiểm (dạng vai quá 90 độ phối hợp xoay '
                             'ngoài tối đa) trong sinh hoạt hàng ngày và tạm ngưng các môn thể thao đối kháng ném '
                             'bóng.',
                             'Nếu đang trong cơn trật cấp: nắn trật nhẹ nhàng dưới giảm đau giãn cơ, kiểm tra lại thần '
                             'kinh nách và mạch máu sau nắn rồi đeo đai treo tay bảo vệ.'],
    'bien_the_kham': [   'Khám khớp vai phải ngoài cơn trật: tầm vận động bình thường nhưng khi bác sĩ đưa cánh tay '
                         'bệnh nhân dạng 90 độ và từ từ xoay ngoài tối đa, bệnh nhân lập tức co cứng cơ gồng lại vì '
                         'cảm giác sợ khớp vai tuột ra trước (nghiệm pháp e ngại - Apprehension test dương tính mạnh).',
                         'Nghiệm pháp tái định vị (Relocation test) dương tính rõ: khi đang làm test e ngại gây sợ '
                         'hãi, bác sĩ dùng lòng bàn tay ấn nhẹ chỏm xương cánh tay ra sau thì cảm giác sợ trật biến '
                         'mất ngay lập tức.',
                         'Khám thấy dấu hiệu rãnh lõm dưới mỏm cùng vai (Sulcus sign dương tính nhẹ 1,5cm) khi kéo '
                         'cánh tay dọc trục xuống dưới kèm tăng lỏng lẻo bao khớp toàn thể ở cả hai bên vai.',
                         'Bệnh nhân vào viện trong đợt trật tái hồi lần thứ 5 trong năm: vai trái vuông góc hõm khớp '
                         'rỗng mất đường cong tròn cơ delta, sờ thấy chỏm xương cánh tay trật ra trước dưới mỏm quạ, '
                         'mạch quay và cảm giác vùng cơ delta bình thường.',
                         'Test Load-and-Shift (kéo trượt chỏm xương cánh tay ra trước sau) cho thấy chỏm xương cánh '
                         'tay trượt quá bờ trước ổ chảo độ 2 kèm tiếng lụp cụp nhẹ gợi ý rách sụn viền Bankart.',
                         'Khớp vai phải không sưng đỏ, không có dấu hiệu tổn thương thần kinh nách (cảm giác mặt ngoài '
                         'cơ delta bảo tồn tốt), test e ngại dương tính rõ ở góc dạng 90 độ.'],
    'chan_doan': 'Trật khớp vai tái hồi ra trước bên phải sau chấn thương thể thao.',
    'chinh': [   'khớp vai bị trật khớp lặp đi lặp lại nhiều lần chỉ sau các động tác nhẹ nhàng như vươn tay ném bóng '
                 'mặc áo hoặc trở mình khi ngủ',
                 'cảm giác lo sợ khớp vai sắp bị tuột trượt ra khỏi ổ khớp (dấu hiệu e ngại dương tính) mỗi khi đưa '
                 'cánh tay lên cao dạng và xoay ngoài',
                 'tiền sử từng bị trật khớp vai cấp tính lần đầu do chấn thương mạnh trước đó không được bất động hoặc '
                 'phục hồi tốt'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chụp X-quang khớp vai thẳng và tư thế Stryker notch hoặc West Point để phát hiện tổn thương lõm xương '
                'Hill-Sachs ở chỏm cánh tay và mẻ bờ trước dưới ổ chảo (Bankart xương).',
    'kham': 'Khám khớp vai phải ngoài cơn trật: tầm vận động bình thường nhưng khi bác sĩ đưa cánh tay bệnh nhân dạng '
            '90 độ và từ từ xoay ngoài tối đa, bệnh nhân lập tức co cứng cơ gồng lại vì cảm giác sợ khớp vai tuột ra '
            'trước (nghiệm pháp e ngại - Apprehension test dương tính mạnh).',
    'nhom': 'người lớn',
    'phu': [   'khớp vai bên bệnh thường có thể tự nắn nhẹ là vào lại dễ dàng hơn lần đầu nhưng gây mất tự tin nặng nề '
               'khi sinh hoạt',
               'cảm giác lụp cụp hoặc trật nhẹ thoáng qua (bán trật) khi xoay vai đột ngột',
               'teo nhẹ cơ delta hoặc yếu lực khớp vai ở tư thế giơ tay quá đầu'],
    'ten': 'trật khớp vai tái hồi'},
    {   'bien_the_chan_doan': [   'Trật khớp khuỷu tay ra sau cấp tính thể đơn thuần chưa có biến chứng mạch máu thần '
                              'kinh.',
                              'Trật khớp khuỷu tay trái ra sau ngoài cấp tính sau ngã chống tay.',
                              'Theo dõi trật khớp khuỷu tay cấp nghi kèm gãy mỏm vẹt hoặc chỏm xương quay (tam chứng '
                              'kinh khủng).',
                              'Trật khớp khuỷu tay cấp ở trẻ em nghi kèm bong mỏm trên lồi cầu trong xương cánh tay.',
                              'Sai khớp khuỷu tay ra sau cấp tính có chèn ép nhẹ thần kinh trụ thoáng qua.',
                              'Trật khớp khuỷu tay cấp tính cần nắn chỉnh cấp cứu và kiểm tra độ vững sau nắn.'],
    'bien_the_ke_hoach': [   'Đánh giá ngay lập tức tình trạng mạch máu (mạch quay, thời gian đổ đầy mao mạch bàn tay) '
                             'và chức năng thần kinh giữa, thần kinh trụ, thần kinh quay trước khi nắn chỉnh; chụp '
                             'X-quang khuỷu tay thẳng nghiêng cấp cứu xác định hướng trật và loại trừ gãy xương phối '
                             'hợp.',
                             'Thực hiện nắn trật khớp khuỷu cấp cứu càng sớm càng tốt dưới gây mê ngắn hoặc tiền mê '
                             'giảm đau tĩnh mạch kết hợp giãn cơ bằng kỹ thuật kéo nhẹ dọc trục cẳng tay và đẩy mỏm '
                             'khuỷu ra trước.',
                             'Sau khi nắn vào khớp nghe tiếng "cục" rõ ràng: kiểm tra lại ngay độ vững của khớp khuỷu '
                             'qua toàn tầm vận động gấp duỗi, chụp X-quang kiểm tra sau nắn đảm bảo khớp đồng tâm hoàn '
                             'toàn và không có mảnh xương kẹt trong khe khớp.',
                             'Kiểm tra lại mạch quay và thần kinh ngoại vi sau nắn; bất động khuỷu tay ở tư thế gấp 90 '
                             'độ cẳng tay trung tính bằng nẹp bột cánh bàn tay (posterior splint) trong 7-14 ngày.',
                             'Hướng dẫn bệnh nhân kê cao tay chườm lạnh giảm sưng nề trong 48 giờ đầu và bắt đầu tập '
                             'vận động chủ động có kiểm soát sớm sau 1-2 tuần bất động để phòng tránh biến chứng cứng '
                             'khớp khuỷu.',
                             'Hội chẩn phẫu thuật ngay nếu khớp khuỷu mất vững tái trật ngay khi duỗi dưới 30-45 độ '
                             'hoặc có gãy vỡ chỏm quay/mỏm vẹt lớn (tam chứng kinh khủng khuỷu tay).'],
    'bien_the_kham': [   'Khuỷu tay phải biến dạng nặng giữ cố định ở tư thế gấp 40 độ, cẳng tay nhìn ngắn rõ rệt, mặt '
                         'sau mỏm khuỷu nhô lồi hẳn ra sau tạo hõm lõm ngay phía trên mỏm khuỷu, tam giác Hueter bị '
                         'biến dạng mất thẳng hàng khi duỗi, mạch quay bắt rõ đều.',
                         'Bệnh nhân ôm giữ cẳng tay trái đau dữ dội sau ngã cầu thang, khuỷu tay sưng to biến dạng ra '
                         'sau ngoài, sờ thấy đầu dưới xương cánh tay gồ lên ở nếp gấp khuỷu trước, kiểm tra cảm giác '
                         'ngón út và ngón trỏ còn nguyên vẹn.',
                         'Khám cấp cứu sau tai nạn thể thao: khuỷu tay phải không thể gấp duỗi dù chỉ 5 độ do kẹt khớp '
                         'cơ học (dấu hiệu lò xo đàn hồi khi thử cử động thụ động), không có vết thương hở rách da.',
                         'Trật khớp khuỷu ra sau điển hình kèm sưng nề tụ máu quanh hố khuỷu, bàn tay hồng ấm độ bão '
                         'hòa oxy đầu ngón SpO2 99%, các ngón tay gấp duỗi chủ động được bình thường.',
                         'Biến dạng khớp khuỷu trái ra sau ở trẻ em sau ngã xà đơn, sờ thấy chỏm xương quay lệch ra '
                         'sau ngoài cùng mỏm khuỷu, không thấy gồ xương dọc thân xương cánh tay hay cẳng tay.',
                         'Khuỷu tay biến dạng trật khớp cấp tính với đầu dưới xương trụ và chỏm quay bị đẩy trượt hoàn '
                         'toàn ra sau lồi cầu xương cánh tay, mạch quay hơi yếu nhẹ do sưng nề cần nắn khẩn cấp.'],
    'chan_doan': 'Trật khớp khuỷu tay ra sau cấp tính thể đơn thuần chưa có biến chứng mạch máu thần kinh.',
    'chinh': [   'đau dữ dội và mất hoàn toàn khả năng gấp duỗi khuỷu tay ngay sau khi ngã chống bàn tay xuống đất '
                 'trong tư thế khuỷu hơi duỗi',
                 'khuỷu tay biến dạng rõ rệt mỏm khuỷu nhô gồ bất thường ra phía sau tạo hình bậc thang rõ',
                 'tam giác khuỷu Hueter (mỏm trên lồi cầu trong ngoài và đỉnh mỏm khuỷu) bị đảo lộn biến dạng mất cân '
                 'xứng'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Đánh giá ngay lập tức tình trạng mạch máu (mạch quay, thời gian đổ đầy mao mạch bàn tay) và chức năng '
                'thần kinh giữa, thần kinh trụ, thần kinh quay trước khi nắn chỉnh; chụp X-quang khuỷu tay thẳng '
                'nghiêng cấp cứu xác định hướng trật và loại trừ gãy xương phối hợp.',
    'kham': 'Khuỷu tay phải biến dạng nặng giữ cố định ở tư thế gấp 40 độ, cẳng tay nhìn ngắn rõ rệt, mặt sau mỏm '
            'khuỷu nhô lồi hẳn ra sau tạo hõm lõm ngay phía trên mỏm khuỷu, tam giác Hueter bị biến dạng mất thẳng '
            'hàng khi duỗi, mạch quay bắt rõ đều.',
    'nhom': 'cả hai',
    'phu': [   'cẳng tay trông có vẻ ngắn lại bất thường so với cánh tay bên lành và luôn giữ ở tư thế gấp nhẹ 45 độ',
               'sưng nề rất nhanh quanh vùng khuỷu tay kèm bầm tím lan rộng',
               'cần kiểm tra ngay mạch quay và cảm giác bàn tay đề phòng chèn ép động mạch cánh tay hoặc thần kinh trụ '
               'giữa'],
    'ten': 'trật khớp khuỷu tay'},
    {   'bien_the_chan_doan': [   'Bong gân độ 2 dây chằng bên khớp liên đốt gần ngón giữa tay phải do chấn thương thể '
                              'thao.',
                              'Giãn rách bán phần dây chằng bên khớp liên đốt ngón tay sau chơi bóng rổ.',
                              'Bong gân khớp liên đốt gần ngón áp út có phù nề bao khớp và đĩa sụn lòng bàn tay (volar '
                              'plate).',
                              'Bong gân độ 1 dây chằng bên trụ khớp bàn ngón cái (Skier thumb nhẹ) sau bắt bóng.',
                              'Theo dõi bong gân ngón tay do bóng rổ cần loại trừ gãy giật mảnh xương nền đốt ngón.',
                              'Tổn thương dây chằng bên khớp liên đốt ngón tay mức độ nhẹ vừa đáp ứng tốt với băng dán '
                              'ngón.'],
    'bien_the_ke_hoach': [   'Chụp X-quang ngón tay thẳng nghiêng chếch chuẩn xác ngay để loại trừ gãy rạn xương phạm '
                             'khớp hoặc bong mảnh xương nhỏ nơi bám dây chằng (avulsion fracture) hay bán trật khớp.',
                             'Áp dụng nguyên tắc RICE trong 48 giờ đầu: nghỉ chơi bóng rổ hoàn toàn, chườm đá bọc khăn '
                             '10-15 phút mỗi 3 giờ, nâng cao bàn tay giảm sưng nề.',
                             'Thực hiện kỹ thuật cố định băng dính hai ngón cạnh nhau (buddy taping): dán cố định ngón '
                             'đau vào ngón lành kế bên có lót gạc mềm ở kẽ ngón giúp bảo vệ dây chằng bên mà vẫn cho '
                             'phép tập gấp duỗi sớm tránh cứng khớp.',
                             'Uống thuốc giảm đau kháng viêm NSAID (Ibuprofen hoặc Meloxicam) hoặc bôi gel giảm đau '
                             'tại chỗ trong 3-5 ngày đầu nếu sưng đau nhiều.',
                             'Hướng dẫn bệnh nhân tập co duỗi nhẹ nhàng ngón tay trong nước ấm sau 3-5 ngày khi bớt '
                             'sưng để phòng ngừa biến chứng co rút cứng khớp liên đốt rất hay gặp ở ngón tay.',
                             'Khuyến cáo chỉ quay lại chơi bóng rổ sau 2-4 tuần khi hết sưng đau hoàn toàn, lực nắm '
                             'hồi phục đủ và vẫn nên băng bảo vệ buddy taping khi thi đấu trong vài tuần đầu.'],
    'bien_the_kham': [   'Khớp liên đốt gần ngón giữa bàn tay phải sưng tròn đều hình thoi, da hơi bầm tím nhẹ ở bờ '
                         'quay, ấn đau chói dọc theo đường đi dây chằng bên quay nhưng không đau thân đốt xương, test '
                         'bẻ nghiêng trụ nhẹ gây đau nhưng không thấy khớp há rộng mất vững.',
                         'Ngón áp út tay trái sưng nề đau khu trú mặt lòng và hai bên khớp PIP sau pha bắt bóng rổ, '
                         'tầm vận động gấp chủ động bị giảm còn 50 độ do phù nề, đầu đốt xa ngón tay duỗi thẳng bình '
                         'thường.',
                         'Khám ngón trỏ bàn tay phải thấy khớp liên đốt gần sưng nề căng bóng gấp nhẹ 15 độ chống đau, '
                         'sờ không có tiếng lạo xạo gãy xương, test đẩy trước sau (palmar plate stress) vững chắc.',
                         'Vùng khớp bàn ngón tay cái (MCP 1) sưng đau mặt trong sau bị bóng bật ngược ngón cái ra sau, '
                         'ấn đau điểm bám dây chằng bên trụ nhưng có điểm dừng chắc (firm endpoint) khi test nghiêng '
                         'quay.',
                         'Các ngón tay hồng ấm bình thường, đầu ngón tay hồi lưu mao mạch dưới 2 giây, không mất cảm '
                         'giác hai bên bờ ngón tay bị chấn thương.',
                         'Bong gân độ 1-2 khớp liên đốt ngón tay không có dấu hiệu xoay lệch trục ngón tay khi bệnh '
                         'nhân thử gấp nhẹ các ngón hướng về phía xương thuyền.'],
    'chan_doan': 'Bong gân độ 2 dây chằng bên khớp liên đốt gần ngón giữa tay phải do chấn thương thể thao.',
    'chinh': [   'đau nhói và sưng to hình thoi quanh khớp liên đốt gần (PIP) ngón tay ngay sau khi bóng rổ đập thẳng '
                 'vào đầu ngón tay',
                 'bầm tím nhẹ hai bên mặt khớp ngón tay kèm hạn chế gấp duỗi ngón tay do sưng đau căng tức',
                 'nghiệm pháp căng nghiêng bên (stress test) khớp liên đốt đau tăng tại dây chằng bên nhưng khớp vẫn '
                 'còn vững không há rộng bất thường'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chụp X-quang ngón tay thẳng nghiêng chếch chuẩn xác ngay để loại trừ gãy rạn xương phạm khớp hoặc '
                'bong mảnh xương nhỏ nơi bám dây chằng (avulsion fracture) hay bán trật khớp.',
    'kham': 'Khớp liên đốt gần ngón giữa bàn tay phải sưng tròn đều hình thoi, da hơi bầm tím nhẹ ở bờ quay, ấn đau '
            'chói dọc theo đường đi dây chằng bên quay nhưng không đau thân đốt xương, test bẻ nghiêng trụ nhẹ gây đau '
            'nhưng không thấy khớp há rộng mất vững.',
    'nhom': 'cả hai',
    'phu': [   'không nhìn thấy biến dạng lệch trục vẹo góc hay ngắn gập ngón tay',
               'cảm giác ngón tay nóng râm ran nhức buốt đặc biệt khi cố nắm chặt bàn tay',
               'đầu ngón tay vẫn tự duỗi thẳng được đốt xa (giúp phân biệt với ngón tay búa đứt gân duỗi)'],
    'ten': 'bong gân ngón tay do bóng rổ'},
    {   'bien_the_chan_doan': [   'Rách sụn chêm trong khớp gối phải thể quai xô hoặc rách sừng sau mạn tính.',
                              'Rách sụn chêm ngoài khớp gối trái kèm nang sụn chêm ngoài.',
                              'Rách thoái hóa sụn chêm trong khớp gối mạn tính ở người trung niên.',
                              'Rách sụn chêm khớp gối có hội chứng kẹt khớp tái diễn cần nội soi xử lý.',
                              'Theo dõi rách sụn chêm khớp gối bên phải đơn thuần không kèm đứt dây chằng chéo.',
                              'Rách sụn chêm khớp gối giai đoạn mạn tính có tràn dịch khớp tái phát và teo cơ đùi.'],
    'bien_the_ke_hoach': [   'Chỉ định chụp cộng hưởng từ (MRI) khớp gối không tiêm thuốc để xác định chính xác vị trí '
                             'rách (sừng trước, thân, sừng sau sụn chêm trong hay ngoài), hình thái vết rách (rách '
                             'dọc, quai xô, rách ngang, rách phức tạp) và loại trừ tổn thương dây chằng đi kèm.',
                             'Chụp X-quang khớp gối tư thế đứng thẳng đánh giá chiều cao khe khớp và loại trừ thoái '
                             'hóa khớp gối tiến triển hoặc dị vật khớp cản quang.',
                             'Hội chẩn Chấn thương chỉnh hình chỉ định phẫu thuật nội soi khớp gối khâu sụn chêm (nếu '
                             'rách ở vùng giàu mạch máu nuôi đỏ-đỏ ở người trẻ) hoặc cắt tạo hình phần sụn rách gây '
                             'kẹt khớp.',
                             'Đối với rách nhỏ ổn định hoặc rách thoái hóa không gây kẹt khớp: điều trị bảo tồn bằng '
                             'giảm tải vận động xoay vặn gối, chườm lạnh, thuốc kháng viêm NSAID ngắn ngày và tập vật '
                             'lý trị liệu mạnh cơ tứ đầu đùi và cơ gân kheo.',
                             'Hướng dẫn bệnh nhân tránh tuyệt đối tư thế ngồi xổm sâu, vắt chéo chân hay xoay vặn trụ '
                             'gối đột ngột trong sinh hoạt hàng ngày.',
                             'Theo dõi tiến trình phục hồi chức năng sau mổ nội soi hoặc điều trị bảo tồn, đánh giá '
                             'lại tầm vận động và sức cơ tứ đầu đùi sau 4-6 tuần.'],
    'bien_the_kham': [   'Ấn dọc khe khớp gối bên trong phía sau bên phải gây đau chói rõ rệt (joint line tenderness), '
                         'nghiệm pháp McMurray (xoay ngoài cẳng chân kết hợp duỗi gối) tạo ra tiếng "click" kèm đau '
                         'nhói tại khe khớp trong, test Thessaly đứng một chân xoay gối dương tính.',
                         'Khớp gối trái tràn dịch nhẹ có dấu hiệu bập bềnh xương bánh chè dương tính nhẹ, tầm duỗi gối '
                         'thiếu 10 độ cuối so với bên phải do mảnh sụn chêm rách quai xô kẹt nhẹ trong khe khớp, test '
                         'Lachman và ngăn kéo âm tính.',
                         'Nghiệm pháp Apley ép và xoay cẳng chân ở tư thế nằm sấp gây đau tái hiện rõ vùng khe khớp '
                         'ngoài gối phải, khi kéo giãn dọc trục lại hết đau (giúp phân biệt rách sụn chêm với tổn '
                         'thương dây chằng).',
                         'Teo nhẹ cơ rộng trong tứ đầu đùi bên trái (chu vi đùi cách bờ trên bánh chè 10cm nhỏ hơn bên '
                         'phải 1,5cm), bệnh nhân không ngồi xổm được quá 90 độ vì đau kẹt mặt sau trong gối.',
                         'Sờ thấy một khối nang nhỏ căng chắc lồi nhẹ tại khe khớp ngoài gối phải (nang sụn chêm ngoài '
                         '- parameniscal cyst) đi kèm đau khe khớp ngoài và test McMurray xoay trong dương tính.',
                         'Trục chân hai bên bình thường, dây chằng chéo trước và chéo sau vững chắc hoàn toàn, chỉ có '
                         'dấu hiệu đau khu trú khe khớp trong và kẹt khớp ngắt quãng.'],
    'chan_doan': 'Rách sụn chêm trong khớp gối phải thể quai xô hoặc rách sừng sau mạn tính.',
    'chinh': [   'đau nhói khu trú dọc khe khớp gối trong hoặc khe khớp gối ngoài đặc biệt khi xoay vặn gối hoặc ngồi '
                 'xổm đứng lên',
                 'hiện tượng kẹt khớp gối (locking) làm đầu gối đột ngột bị khựng cứng không thể duỗi thẳng hoàn toàn '
                 'được phải lắc nhẹ chân mới mở ra',
                 'tràn dịch sưng gối tái diễn mức độ vừa sau mỗi lần đi lại nhiều hoặc chơi thể thao'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chỉ định chụp cộng hưởng từ (MRI) khớp gối không tiêm thuốc để xác định chính xác vị trí rách (sừng '
                'trước, thân, sừng sau sụn chêm trong hay ngoài), hình thái vết rách (rách dọc, quai xô, rách ngang, '
                'rách phức tạp) và loại trừ tổn thương dây chằng đi kèm.',
    'kham': 'Ấn dọc khe khớp gối bên trong phía sau bên phải gây đau chói rõ rệt (joint line tenderness), nghiệm pháp '
            'McMurray (xoay ngoài cẳng chân kết hợp duỗi gối) tạo ra tiếng "click" kèm đau nhói tại khe khớp trong, '
            'test Thessaly đứng một chân xoay gối dương tính.',
    'nhom': 'người lớn',
    'phu': [   'cảm giác tiếng lục cục lật bật bên trong ổ khớp gối khi co duỗi chân',
               'khớp gối có cảm giác hẫng hụt nhẹ (giving way) nhưng thực chất do đau ức chế cơ chứ không lỏng lẻo dây '
               'chằng nặng',
               'teo nhẹ cơ tứ đầu đùi bên chân đau khi tình trạng kéo dài nhiều tháng'],
    'ten': 'rách sụn chêm khớp gối'},
    {   'bien_the_chan_doan': [   'Đụng dập phần mềm và tụ máu cơ tứ đầu đùi phải độ 2 sau chấn thương thể thao.',
                              'Đụng dập phần mềm đùi trái mức độ vừa chưa có dấu hiệu chèn ép khoang.',
                              'Tụ máu phần mềm đùi phải cấp tính sau va đập trực tiếp không gãy xương.',
                              'Chấn thương đụng dập cơ rộng ngoài đùi bên trái gây hạn chế gập gối tạm thời.',
                              'Đụng dập phần mềm đùi cấp tính cần theo dõi phòng ngừa cốt hóa cơ thứ phát.',
                              'Tổn thương đụng dập cơ đùi cấp tính đáp ứng tốt với chườm lạnh bất động sớm.'],
    'bien_the_ke_hoach': [   'Chụp X-quang xương đùi thẳng nghiêng nếu va đập rất mạnh để loại trừ gãy rạn thân xương '
                             'đùi; siêu âm phần mềm vùng đùi đánh giá kích thước ổ tụ máu trong cơ xem có cần chọc hút '
                             'hay điều trị bảo tồn.',
                             'Áp dụng phác đồ bảo tồn chuẩn trong 48 giờ đầu: nghỉ ngơi hoàn toàn tránh tỳ lực mạnh, '
                             'chườm đá lạnh bọc khăn 15-20 phút mỗi 2-3 giờ, băng thun ép nhẹ vùng đùi (giữ gối ở tư '
                             'thế hơi gập nhẹ nhẹ nhàng để giãn nhẹ sợi cơ đang lành tránh co rút) và kê cao chân.',
                             'Tuyệt đối nghiêm cấm xoa bóp bấm huyệt mạnh, đắp lá hoặc bôi dầu nóng lên khối tụ máu cơ '
                             'trong tuần đầu vì làm tăng chảy máu và kích thích biến chứng cốt hóa cơ (myositis '
                             'ossificans).',
                             'Dùng thuốc giảm đau Paracetamol hoặc kháng viêm NSAID ngắn ngày sau 48 giờ (tránh dùng '
                             'Aspirin trong 24 giờ đầu vì có thể làm tăng chảy máu ổ tụ máu), theo dõi sát dấu hiệu '
                             'đau dữ dội không giảm để loại trừ hội chứng chèn ép khoang.',
                             'Sau 48-72 giờ khi sưng đau ổn định: bắt đầu tập gập duỗi gối chủ động nhẹ nhàng trong '
                             'ngưỡng không đau để phục hồi dần chiều dài sợi cơ tứ đầu đùi.',
                             'Hẹn tái khám sau 2 tuần đánh giá độ mềm khối cơ và tầm vận động gập gối; chụp X-quang '
                             'kiểm tra lại sau 4-6 tuần nếu vẫn còn khối cứng bất thường nghi cốt hóa cơ.'],
    'bien_the_kham': [   'Mặt trước ngoài 1/3 giữa đùi phải sưng nề căng cứng, da phủ bên trên có mảng bầm tím rộng '
                         '8x10cm còn nguyên vẹn không rách, sờ thấy khối tụ máu chắc sâu trong cơ rộng ngoài, gập gối '
                         'chủ động chỉ đạt 70 độ do căng cơ đùi, mạch mu chân và chày sau bắt rõ.',
                         'Khối đụng dập cơ tứ đầu đùi bên trái sau va chạm đá bóng, đo chu vi vòng đùi trái lớn hơn '
                         'đùi phải 2,5cm, ấn đau tức lan tỏa nhưng khoang đùi vẫn còn độ đàn hồi không có dấu hiệu '
                         'chèn ép khoang cấp, không mất cảm giác cẳng bàn chân.',
                         'Trẻ em sau ngã đập mặt ngoài đùi vào cạnh bàn đau nhức đi khập khiễng, vùng đùi phải hơi '
                         'sưng nề bầm tím nông, gõ dọc trục xương đùi từ gót chân lên không đau chói (giúp loại trừ '
                         'gãy xương đùi).',
                         'Đùi trái sưng nề căng cơ vùng mặt trước, nâng thẳng chân chủ động đau tăng nhẹ nhưng thực '
                         'hiện được, không có cử động bất thường hay biến dạng ngắn chi.',
                         'Khám phần mềm đùi phải ghi nhận vết tụ máu bầm tím đang ngả màu xanh vàng ở vùng đùi ngoài, '
                         'gối và khớp háng hai bên vận động bình thường trong giới hạn cho phép bởi độ căng cơ.',
                         'Khối tụ máu trong cơ tứ đầu đùi kích thước vừa, đau giảm khi đặt chân kê cao và gập gối nhẹ '
                         '30 độ, không có triệu chứng tê bì hay yếu liệt bàn chân.'],
    'chan_doan': 'Đụng dập phần mềm và tụ máu cơ tứ đầu đùi phải độ 2 sau chấn thương thể thao.',
    'chinh': [   'đau tức căng cứng mặt trước hoặc mặt ngoài đùi ngay sau khi bị va đập mạnh trực tiếp (như đầu gối '
                 'húc vào đùi khi đá bóng hoặc ngã đập đùi)',
                 'xuất hiện khối sưng nề tụ máu dưới da và bầm tím lan rộng vùng đùi bị va chạm',
                 'gập đầu gối bị hạn chế rõ rệt do khối cơ tứ đầu đùi sưng căng cứng đau khi bị kéo giãn'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chụp X-quang xương đùi thẳng nghiêng nếu va đập rất mạnh để loại trừ gãy rạn thân xương đùi; siêu âm '
                'phần mềm vùng đùi đánh giá kích thước ổ tụ máu trong cơ xem có cần chọc hút hay điều trị bảo tồn.',
    'kham': 'Mặt trước ngoài 1/3 giữa đùi phải sưng nề căng cứng, da phủ bên trên có mảng bầm tím rộng 8x10cm còn '
            'nguyên vẹn không rách, sờ thấy khối tụ máu chắc sâu trong cơ rộng ngoài, gập gối chủ động chỉ đạt 70 độ '
            'do căng cơ đùi, mạch mu chân và chày sau bắt rõ.',
    'nhom': 'cả hai',
    'phu': [   'đi lại tập tễnh khó nhấc chân chịu lực hoàn toàn trong vài ngày đầu',
               'ấn vào khối cơ đùi thấy căng chắc ấm nhẹ nhưng mạch khoeo và mạch mu chân vẫn đập bình thường',
               'nguy cơ biến chứng cốt hóa cơ (myositis ossificans) nếu xoa bóp dầu nóng mạnh quá sớm'],
    'ten': 'đụng dập phần mềm đùi do chấn thương'},
    {   'bien_the_chan_doan': [   'Gãy kín đơn thuần xương sườn số 6-7 bên phải không biến chứng tràn khí tràn máu màng '
                              'phổi.',
                              'Gãy rạn kín cung trước xương sườn số 5 bên trái sau tai nạn sinh hoạt.',
                              'Gãy đơn thuần 2 xương sườn liên tiếp bên phải thành ngực vững.',
                              'Gãy kín xương sườn đơn thuần chưa có tổn thương nhu mô phổi và mạch máu liên sườn.',
                              'Theo dõi gãy xương sườn đơn thuần bên trái cần kiểm tra loại trừ tổn thương lách nếu '
                              'gãy sườn thấp 9-11.',
                              'Gãy kín xương sườn không di lệch đáp ứng tốt với giảm đau và tập thở.'],
    'bien_the_ke_hoach': [   'Chụp X-quang ngực thẳng và phim chuyên biệt khung sườn chếch để xác định số lượng vị trí '
                             'xương sườn gãy, đồng thời loại trừ dập phổi, tràn khí màng phổi hoặc tràn máu màng phổi '
                             'đi kèm; siêu âm ổ bụng kiểm tra gan lách nếu gãy các xương sườn thấp (9-12).',
                             'Kiểm soát đau tích cực là ưu tiên hàng đầu giúp bệnh nhân dám hít thở sâu và ho khạc đờm '
                             'phòng tránh xẹp phổi và viêm phổi bội nhiễm: kê đơn Paracetamol phối hợp NSAID (hoặc '
                             'Tramadol ngắn ngày nếu đau nhiều, miếng dán Lidocaine 5% tại chỗ).',
                             'Không băng quấn ép chặt vòng quanh lồng ngực vì làm hạn chế biên độ giãn nở phổi gây '
                             'tăng nguy cơ xẹp phổi và suy hô hấp.',
                             'Hướng dẫn bệnh nhân kỹ thuật ôm gối mềm ép nhẹ lên vùng ngực đau mỗi khi ho hoặc hít sâu '
                             '(splinting), kết hợp bài tập hít thở sâu chậm bằng bụng mỗi giờ 10 lần hoặc dùng bóng '
                             'tập thở.',
                             'Dặn dò các dấu hiệu nguy hiểm cần quay lại cấp cứu ngay: khó thở tăng dần, đau ngực lan '
                             'tỏa, chóng mặt tụt huyết áp, ho khạc ra máu hoặc sờ thấy lép bép khí dưới da vùng cổ '
                             'ngực.',
                             'Hẹn tái khám và chụp X-quang ngực kiểm tra lại sau 5-7 ngày để phát hiện các trường hợp '
                             'tràn dịch tràn khí màng phổi xuất hiện muộn và theo dõi quá trình liền xương tự nhiên '
                             'trong 4-6 tuần.'],
    'bien_the_kham': [   'Thành ngực bên phải vùng cung bên xương sườn số 6-7 có vết bầm tím nhẹ, ấn trực tiếp thấy '
                         'điểm đau chói cố định trên cung sườn 6, nghiệm pháp ép lồng ngực trước sau gây đau nhói tại '
                         'điểm này; phổi hai bên rì rào phế nang đều rõ không ran, không có mảng sườn di động, SpO2 '
                         '98% khí trời.',
                         'Bệnh nhân ôm giữ mạn sườn trái sau ngã đập ngực vào thành ghế, hít sâu giữa chừng phải nín '
                         'thở vì đau nhói, khám thấy không có tràn khí dưới da, gõ phổi trong đều hai bên, nhịp thở 20 '
                         'lần/phút.',
                         'Khám cấp cứu thành ngực trái ghi nhận điểm đau khu trú tại cung trước xương sườn 5 và 6, ấn '
                         'cảm giác lún nhẹ không mất vững mảng sườn, nhịp tim đều 84 l/p huyết áp 120/75 mmHg.',
                         'Không có vết thương thấu ngực, bệnh nhân nói chuyện tròn câu không khó thở, vùng lưng ngực '
                         'phải đau tăng khi xoay thân mình hoặc giơ tay phải lên cao.',
                         'Gõ ngực hai bên vang đều không có vùng gõ đục đáy phổi (loại trừ tràn máu màng phổi lượng '
                         'nhiều), tiếng tim rõ không mờ, chỉ đau chói tại cung bên sườn 8 bên phải.',
                         'Bệnh nhân thở nông đều 22 lần/phút để tránh đau thành ngực, không tím môi, ổ gãy rạn kín '
                         'cung trước sườn 7 không có dấu hiệu di lệch chọc vào khoang màng phổi.'],
    'chan_doan': 'Gãy kín đơn thuần xương sườn số 6-7 bên phải không biến chứng tràn khí tràn máu màng phổi.',
    'chinh': [   'đau nhói như dao đâm khu trú tại một điểm trên thành ngực mỗi khi hít thở sâu ho hắt hơi hoặc xoay '
                 'trở người',
                 'ấn nhẹ dọc theo cung xương sườn bị tổn thương có điểm đau chói cố định hoặc cảm giác lạo xạo nhẹ',
                 'nghiệm pháp ép lồng ngực trước sau hoặc hai bên gây đau nhói lan truyền đúng về vị trí xương sườn '
                 'gãy'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chụp X-quang ngực thẳng và phim chuyên biệt khung sườn chếch để xác định số lượng vị trí xương sườn '
                'gãy, đồng thời loại trừ dập phổi, tràn khí màng phổi hoặc tràn máu màng phổi đi kèm; siêu âm ổ bụng '
                'kiểm tra gan lách nếu gãy các xương sườn thấp (9-12).',
    'kham': 'Thành ngực bên phải vùng cung bên xương sườn số 6-7 có vết bầm tím nhẹ, ấn trực tiếp thấy điểm đau chói '
            'cố định trên cung sườn 6, nghiệm pháp ép lồng ngực trước sau gây đau nhói tại điểm này; phổi hai bên rì '
            'rào phế nang đều rõ không ran, không có mảng sườn di động, SpO2 98% khí trời.',
    'nhom': 'người lớn',
    'phu': [   'bệnh nhân có xu hướng thở nông nhanh giữ chặt tay lên vùng ngực đau để hạn chế di động thành ngực',
               'không có dấu hiệu suy hô hấp nặng ho ra máu hay tràn khí dưới da vùng cổ ngực',
               'da thành ngực có thể bầm tím nhẹ tại nơi va đập trực tiếp'],
    'ten': 'gãy xương sườn đơn thuần do tai nạn'},
    {   'bien_the_chan_doan': [   'Gãy rạn kín xương bánh chè phải không di lệch còn nguyên vẹn hệ thống gân duỗi gối.',
                              'Gãy nứt dọc xương bánh chè trái kín sau chấn thương đập gối trực tiếp.',
                              'Gãy rạn xương bánh chè kín độ 1 chưa di lệch mặt khớp dưới 2mm.',
                              'Theo dõi gãy rạn xương bánh chè kín ở trẻ em phân biệt với xương bánh chè hai mảnh bẩm '
                              'sinh.',
                              'Gãy rạn xương bánh chè kín kèm tràn máu ổ khớp gối cấp tính.',
                              'Gãy rạn kín xương bánh chè không di lệch đủ điều kiện điều trị bảo tồn.'],
    'bien_the_ke_hoach': [   'Chụp X-quang khớp gối thẳng, nghiêng và tư thế tiếp tuyến mặt trời mọc (skyline view) để '
                             'xác định đường rạn xương bánh chè, đánh giá mức độ di lệch mặt khớp (dưới 2mm) và loại '
                             'trừ xương bánh chè hai mảnh bẩm sinh.',
                             'Kiểm tra khả năng duỗi thẳng nâng thẳng chân chủ động (có thể gây tê ổ khớp hoặc chọc '
                             'hút máu tụ khớp gối vô khuẩn nếu quá căng đau) để khẳng định mạc giữ bánh chè hai bên '
                             'còn nguyên vẹn.',
                             'Điều trị bảo tồn cho gãy rạn không di lệch và còn cơ chế duỗi: bất động khớp gối ở tư '
                             'thế duỗi thẳng hoàn toàn bằng nẹp khóa gối (hinged knee brace) hoặc nẹp bột ống đùi cổ '
                             'chân (cylinder cast) trong 4-6 tuần.',
                             'Cho phép bệnh nhân đi lại chống chân chịu lực một phần với nẹp khóa thẳng gối và hai '
                             'nạng hỗ trợ ngay khi bớt đau, kê cao chân và chườm lạnh ngoài nẹp trong 48 giờ đầu.',
                             'Hướng dẫn tập gồng cơ tứ đầu đùi đẳng trường (quadriceps sets) và nâng thẳng chân trong '
                             'nẹp sớm để tránh teo cơ và cứng khớp gối.',
                             'Chụp X-quang kiểm tra lại sau 1 tuần và 3 tuần để chắc chắn ổ gãy không bị di lệch thứ '
                             'phát; bắt đầu tập gập gối tăng dần biên độ khi ổ rạn có dấu hiệu liền xương trên phim.'],
    'bien_the_kham': [   'Khớp gối phải sưng nề tụ máu mức độ vừa (bập bềnh xương bánh chè dương tính), da mặt trước '
                         'gối có vết trầy xước bầm tím mới không rách sâu thông khớp, ấn trực tiếp lên cực giữa xương '
                         'bánh chè đau chói, bệnh nhân vẫn cố gắng duỗi thẳng gối nâng gót chân khỏi mặt giường được '
                         'nhưng rất đau (cân duỗi còn nguyên vẹn).',
                         'Khám gối trái thấy sưng phù mặt trước xương bánh chè, sờ nắn cẩn thận dọc bờ xương bánh chè '
                         'thấy đau nhói đường ngang giữa nhưng không sờ thấy rãnh khuyết tách rời hai mảnh (nghi gãy '
                         'rạn không di lệch), dây chằng bên và ngăn kéo vững.',
                         'Bệnh nhân không thể tự gấp gối quá 30 độ do khớp gối căng dịch máu và đau buốt tại xương '
                         'bánh chè, mạch khoeo và mạch mu chân bắt rõ mạnh đều hai bên.',
                         'Trẻ em sau ngã đập gối xuống sân bê tông đau khóc sưng gối phải, ấn chói cực dưới xương bánh '
                         'chè, không có vết thương hở, cần lưu ý phân biệt gãy rạn hay bong sụn cực dưới bánh chè.',
                         'Đầu gối trái sưng tròn bầm tím, sờ xương bánh chè thấy ấm và căng dịch khớp, không có tiếng '
                         'lạo xạo di lệch mạnh hay mảnh vỡ tách rời dưới da.',
                         'Cơ chế duỗi gối còn bảo tồn một phần sau chọc hút giảm áp hoặc gây tê khớp, khớp gối không '
                         'biến dạng lệch trục, bàn chân hồng ấm cử động các ngón tốt.'],
    'chan_doan': 'Gãy rạn kín xương bánh chè phải không di lệch còn nguyên vẹn hệ thống gân duỗi gối.',
    'chinh': [   'đau nhói mặt trước đầu gối ngay sau khi ngã quỳ đập mạnh trực tiếp đầu gối xuống nền cứng',
                 'sưng to nhanh vùng khớp gối kèm tụ máu tràn dịch trong ổ khớp gối',
                 'mất hoặc giảm nặng khả năng tự nâng thẳng chân lên khỏi mặt giường khi giữ đầu gối duỗi thẳng (cơ '
                 'chế duỗi gối bị ảnh hưởng hoặc ức chế đau)'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chụp X-quang khớp gối thẳng, nghiêng và tư thế tiếp tuyến mặt trời mọc (skyline view) để xác định '
                'đường rạn xương bánh chè, đánh giá mức độ di lệch mặt khớp (dưới 2mm) và loại trừ xương bánh chè hai '
                'mảnh bẩm sinh.',
    'kham': 'Khớp gối phải sưng nề tụ máu mức độ vừa (bập bềnh xương bánh chè dương tính), da mặt trước gối có vết '
            'trầy xước bầm tím mới không rách sâu thông khớp, ấn trực tiếp lên cực giữa xương bánh chè đau chói, bệnh '
            'nhân vẫn cố gắng duỗi thẳng gối nâng gót chân khỏi mặt giường được nhưng rất đau (cân duỗi còn nguyên '
            'vẹn).',
    'nhom': 'cả hai',
    'phu': [   'ấn trực tiếp lên mặt trước xương bánh chè có điểm đau chói cố định kèm sưng bầm tím da trước gối',
               'sờ kỹ có thể thấy đường rạn nông hoặc không có khe hở gián đoạn lớn giữa hai mảnh xương',
               'không đứng tỳ trọng lực được lên bên chân bị chấn thương'],
    'ten': 'gãy rạn xương bánh chè kín'},
    {   'bien_the_chan_doan': [   'Tổn thương rách bán phần dây chằng bên trong khớp gối phải (MCL độ 2) đơn độc.',
                              'Rách dây chằng bên trong khớp gối trái độ 1 sau chấn thương thể thao vẹo ngoài.',
                              'Đứt hoàn toàn dây chằng bên trong khớp gối phải (MCL độ 3) cần đánh giá dây chằng chéo '
                              'trước.',
                              'Tổn thương rách dây chằng bên trong khớp gối cấp tính ở trẻ thanh thiếu niên.',
                              'Rách dây chằng bên chày (MCL) tại điểm bám lồi cầu trong xương đùi cấp tính.',
                              'Tổn thương dây chằng bên trong khớp gối mức độ vừa đáp ứng tốt điều trị bảo tồn nẹp bản '
                              'lề.'],
    'bien_the_ke_hoach': [   'Chụp X-quang khớp gối thẳng nghiêng loại trừ gãy xương mâm chày hoặc bong điểm bám '
                             'xương; chỉ định chụp MRI khớp gối nếu tổn thương độ 2-3 để đánh giá vị trí rách MCL và '
                             'tầm soát rách dây chằng chéo trước (ACL) hoặc sụn chêm đi kèm (bộ ba bất hạnh '
                             'O’Donoghue).',
                             'Điều trị bảo tồn cho đa số tổn thương MCL đơn thuần (độ 1, 2 và nhiều ca độ 3): bất động '
                             'bảo vệ bằng nẹp khớp gối có bản lề giới hạn biên độ (hinged knee brace) giữ trục không '
                             'cho vẹo ngoài trong 4-6 tuần.',
                             'Áp dụng RICE trong 48-72 giờ đầu: chườm lạnh mặt trong gối, băng ép nhẹ, kê cao chân và '
                             'dùng thuốc giảm đau chống viêm NSAID đường uống trong 5-7 ngày.',
                             'Cho phép chống chân đi lại có nạng và tập gấp duỗi gối trong khung bảo vệ của nẹp bản lề '
                             'sớm ngay khi đỡ đau (từ 0-90 độ) kết hợp tập gồng cơ tứ đầu đùi để chống cứng khớp.',
                             'Hội chẩn Chấn thương chỉnh hình phẫu thuật khâu nối tái tạo dây chằng nếu rách độ 3 nặng '
                             'gây mất vững đa hướng, rách đầu xa kẹt vào khe khớp (tổn thương Stener gối) hoặc phối '
                             'hợp đứt dây chằng chéo.',
                             'Hướng dẫn lộ trình tập vật lý trị liệu tăng sức mạnh cơ rộng trong, cơ gân kheo và thăng '
                             'bằng cảm thụ bản thể trước khi quay lại thể thao sau 6-12 tuần.'],
    'bien_the_kham': [   'Mặt trong khớp gối phải sưng nề bầm tím nhẹ dọc theo đường đi dây chằng bên chày (MCL), ấn '
                         'đau chói tại điểm bám lồi cầu trong xương đùi; làm test Valgus stress ở góc gập gối 30 độ '
                         'thấy khe khớp trong há mở khoảng 7mm (độ 2) với điểm dừng mềm dẻo nhưng ở góc 0 độ gối vẫn '
                         'vững, test Lachman âm tính.',
                         'Khám gối trái sau chấn thương đá bóng bị xoắn vẹo ngoài: ấn đau suốt dọc dải dây chằng bên '
                         'trong, bệnh nhân đi tập tễnh chân trái hơi gập 15 độ để giảm căng mặt trong gối, không có '
                         'dấu hiệu kẹt khớp sụn chêm.',
                         'Nghiệm pháp Valgus stress test ở gối gập 30 độ gây há khe khớp trong rõ rệt kèm cảm giác '
                         'hẫng không có điểm dừng chắc (nghi rách độ 3 hoàn toàn), cần kiểm tra kỹ phối hợp dây chằng '
                         'chéo trước (test Lachman) vì hay đi kèm.',
                         'Khớp gối phải sưng khu trú cạnh trong, không có bập bềnh xương bánh chè rõ, test ngăn kéo '
                         'trước và sau âm tính, mạch khoeo và mu chân bình thường không có dấu hiệu trật khớp gối.',
                         'Bệnh nhân trẻ tuổi than đau buốt mặt trong gối khi xoay chân ra ngoài, test Valgus ở góc 30 '
                         'độ đau tăng nhưng độ há khe khớp dưới 5mm (rách nhẹ độ 1-2) với điểm dừng chắc chắn.',
                         'Ấn điểm bám đầu trên xương chày vùng chân ngỗng đau nhẹ kèm tụ máu dưới da mặt trong gối '
                         'trái, tầm vận động gập gối chủ động đạt 95 độ.'],
    'chan_doan': 'Tổn thương rách bán phần dây chằng bên trong khớp gối phải (MCL độ 2) đơn độc.',
    'chinh': [   'đau nhói dữ dội ở mặt trong đầu gối ngay sau cú va chạm lực đẩy từ mặt ngoài gối làm gối vẹo vào '
                 'trong (lực valgus)',
                 'sưng nề và bầm tím dọc theo mặt trong khớp gối từ lồi cầu trong xương đùi xuống đầu trên xương chày',
                 'nghiệm pháp ép vẹo ngoài (Valgus stress test) ở góc gập gối 30 độ làm khe khớp trong há rộng bất '
                 'thường kèm đau chói'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Chụp X-quang khớp gối thẳng nghiêng loại trừ gãy xương mâm chày hoặc bong điểm bám xương; chỉ định '
                'chụp MRI khớp gối nếu tổn thương độ 2-3 để đánh giá vị trí rách MCL và tầm soát rách dây chằng chéo '
                'trước (ACL) hoặc sụn chêm đi kèm (bộ ba bất hạnh O’Donoghue).',
    'kham': 'Mặt trong khớp gối phải sưng nề bầm tím nhẹ dọc theo đường đi dây chằng bên chày (MCL), ấn đau chói tại '
            'điểm bám lồi cầu trong xương đùi; làm test Valgus stress ở góc gập gối 30 độ thấy khe khớp trong há mở '
            'khoảng 7mm (độ 2) với điểm dừng mềm dẻo nhưng ở góc 0 độ gối vẫn vững, test Lachman âm tính.',
    'nhom': 'cả hai',
    'phu': [   'cảm giác khớp gối bị yếu lỏng lẻo lảo đảo sang bên khi đặt chân chịu lực hoặc đổi hướng đột ngột',
               'gối thường không bị tràn máu ổ khớp nhiều như đứt dây chằng chéo trước mà sưng khu trú phần mềm mặt '
               'trong',
               'hạn chế duỗi thẳng gối hoàn toàn do co thắt cơ đau mặt trong gối'],
    'ten': 'tổn thương rách dây chằng bên trong khớp gối'},
    {   'bien_the_chan_doan': [   'Hội chứng cơ hình lê chèn ép dây thần kinh tọa bên phải mạn tính.',
                              'Co thắt phì đại cơ hình lê bên trái gây đau thần kinh tọa ngoài cột sống.',
                              'Hội chứng cơ hình lê mạn tính ở người ngồi làm việc văn phòng kéo dài.',
                              'Theo dõi hội chứng cơ hình lê cần phân biệt với thoát vị đĩa đệm cột sống thắt lưng '
                              'L5-S1.',
                              'Hội chứng cơ hình lê hai bên mức độ nhẹ vừa đáp ứng tốt với kéo giãn cơ.',
                              'Chèn ép dây thần kinh tọa tại khoang mông sâu do co thắt cơ hình lê.'],
    'bien_the_ke_hoach': [   'Chụp MRI cột sống thắt lưng nếu cần để loại trừ chắc chắn thoát vị đĩa đệm chèn ép rễ '
                             'L5-S1; siêu âm hoặc chụp MRI vùng mông khung chậu đánh giá phì đại bất đối xứng hoặc '
                             'giải phẫu bất thường cơ hình lê.',
                             'Điều trị bảo tồn chủ đạo bằng vật lý trị liệu chuyên biệt: hướng dẫn các bài tập kéo '
                             'giãn cơ hình lê (nằm ngửa bắt chéo mắt cá chân đau lên gối lành rồi kéo ép gối lành về '
                             'phía ngực giữ 30 giây, ngày 3 lần) và lăn bóng massage giải phóng điểm kích hoạt '
                             '(trigger point) vùng mông.',
                             'Dùng thuốc giãn cơ vân tác dụng trung ương (Eperisone hoặc Tolperisone) kết hợp thuốc '
                             'kháng viêm NSAID (Meloxicam) hoặc Gabapentin liều thấp trong 1-2 tuần để cắt vòng xoắn '
                             'co thắt cơ - kích thích thần kinh.',
                             'Tư vấn thay đổi thói quen sinh hoạt: không bỏ ví tiền hay điện thoại dày ở túi quần sau '
                             'khi ngồi, sử dụng đệm ngồi êm và đứng dậy đi lại giãn cơ mỗi 45-60 phút làm việc.',
                             'Chỉ định tiêm Corticoid pha thuốc tê (hoặc tiêm Botulinum toxin type A trong ca kháng '
                             'trị) chính xác vào bụng cơ hình lê dưới hướng dẫn siêu âm hoặc CT tránh tiêm trúng dây '
                             'thần kinh tọa.',
                             'Hẹn tái khám đánh giá mức độ cải thiện triệu chứng tê lan sau 3-4 tuần tập vật lý trị '
                             'liệu tích cực.'],
    'bien_the_kham': [   'Cột sống thắt lưng thẳng mềm dẻo, ấn dọc các gai sống và điểm cạnh sống L4-L5-S1 hoàn toàn '
                         'không đau, nhưng ấn sâu vào điểm chính giữa khối cơ mông phải gây đau chói lan dọc mặt sau '
                         'đùi; nghiệm pháp FAIR (gấp 60 độ, khép và xoay trong háng) và nghiệm pháp Pace (dạng đùi '
                         'kháng lực) dương tính mạnh bên phải.',
                         'Nghiệm pháp Freiberg (xoay trong thụ động khớp háng ở tư thế duỗi thẳng) gây đau tức sâu '
                         'vùng mông trái lan tê xuống khoeo chân, test nâng thẳng chân Lasegue dưới 60 độ âm tính ở tư '
                         'thế trung tính nhưng dương tính khi xoay trong đùi.',
                         'Bệnh nhân có dáng ngồi hơi nghiêng mông sang một bên để tránh tỳ đè lên mông phải, khám phản '
                         'xạ gân gót S1 và gân gối L4 hai bên đều bình thường, sức cơ gấp duỗi ngón cái 5/5.',
                         'Sờ thấy dải cơ hình lê vùng mông sâu bên trái co cứng như thừng chắc và rất nhạy cảm đau khi '
                         'ấn sâu, khớp háng xoay trong ngoài tự do không đau vùng bẹn (loại trừ bệnh khớp háng).',
                         'Khám thần kinh chi dưới ghi nhận tê râm ran nhẹ mặt ngoài cẳng chân nhưng không có teo cơ '
                         'bắp chân hay mất phản xạ gân xương, đau giảm rõ khi bệnh nhân nằm ngửa xoay bàn chân ra '
                         'ngoài.',
                         'Nghiệm pháp Beatty (nằm nghiêng bên lành, nhấc đầu gối bên đau lên khỏi giường giữ 10 giây) '
                         'gây đau sâu ngay giữa mông phải rất đặc trưng cho chèn ép từ cơ hình lê.'],
    'chan_doan': 'Hội chứng cơ hình lê chèn ép dây thần kinh tọa bên phải mạn tính.',
    'chinh': [   'đau nhức sâu ở chính giữa vùng mông một bên lan xuống mặt sau đùi và có thể tê buốt xuống cẳng chân '
                 'theo đường đi thần kinh tọa',
                 'đau tăng vọt khi ngồi lâu trên ghế cứng lái xe đường dài leo cầu thang hoặc ngồi bắt chéo chân',
                 'nghiệm pháp kéo căng cơ hình lê (FAIR test: gấp háng khép và xoay trong đùi) gây tái hiện cơn đau tê '
                 'từ mông lan xuống chân'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chụp MRI cột sống thắt lưng nếu cần để loại trừ chắc chắn thoát vị đĩa đệm chèn ép rễ L5-S1; siêu âm '
                'hoặc chụp MRI vùng mông khung chậu đánh giá phì đại bất đối xứng hoặc giải phẫu bất thường cơ hình '
                'lê.',
    'kham': 'Cột sống thắt lưng thẳng mềm dẻo, ấn dọc các gai sống và điểm cạnh sống L4-L5-S1 hoàn toàn không đau, '
            'nhưng ấn sâu vào điểm chính giữa khối cơ mông phải gây đau chói lan dọc mặt sau đùi; nghiệm pháp FAIR '
            '(gấp 60 độ, khép và xoay trong háng) và nghiệm pháp Pace (dạng đùi kháng lực) dương tính mạnh bên phải.',
    'nhom': 'người lớn',
    'phu': [   'cột sống thắt lưng hoàn toàn không đau không cứng lưng và không hạn chế động tác cúi ngửa lưng',
               'ấn sâu vào điểm giữa mông (điểm giao mấu chuyển lớn và gai chậu sau dưới) gây đau giật lan xuống đùi '
               'sau',
               'thường gặp ở người chạy bộ đường dài hoặc nhân viên văn phòng ngồi ví dày ở túi quần sau'],
    'ten': 'hội chứng cơ hình lê chèn ép thần kinh tọa'},
    {   'bien_the_chan_doan': [   'Liệt dây thần kinh quay ngoại biên cấp tính gây bàn tay rủ do chèn ép tại rãnh xoắn '
                              'xương cánh tay.',
                              'Tổn thương thần kinh quay cấp tính thể mất dẫn truyền thoáng qua (Neurapraxia - liệt '
                              'đêm thứ bảy).',
                              'Liệt dây thần kinh quay bên phải cấp tính chưa rõ tổn thương sợi trục hay bao myelin.',
                              'Liệt dây thần kinh quay cấp gây mất duỗi cổ tay và mất duỗi khớp bàn ngón tay.',
                              'Theo dõi liệt dây thần kinh quay cấp cần chẩn đoán phân biệt với tổn thương thần kinh '
                              'gian cốt sau.',
                              'Liệt dây thần kinh quay ngoại biên cấp tính cần đo điện cơ và đeo nẹp nâng cổ tay.'],
    'bien_the_ke_hoach': [   'Đeo ngay nẹp nâng đỡ cổ tay động hoặc nẹp tĩnh giữ cổ tay ở tư thế duỗi nhẹ 20-30 độ và '
                             'các khớp bàn ngón hơi nâng (cock-up splint) để tránh giãn căng quá mức nhóm cơ duỗi liệt '
                             'và giúp bàn tay cầm nắm được trong sinh hoạt.',
                             'Chỉ định siêu âm dây thần kinh quay dọc cánh tay loại trừ khối u nang hay mảnh xương '
                             'chèn ép; hẹn đo điện cơ đồ và dẫn truyền thần kinh (EMG/NCS) sau ngày thứ 14-21 để đánh '
                             'giá mức độ tổn thương sợi trục (axonotmesis) hay chỉ tổn thương myelin đơn thuần '
                             '(neurapraxia) giúp tiên lượng phục hồi.',
                             'Kê đơn Vitamin nhóm B liều cao (B1, B6, Methylcobalamin B12) hỗ trợ tái tạo bao myelin '
                             'thần kinh, dùng NSAID hoặc Corticoid ngắn ngày trong vài ngày đầu nếu do phù nề chèn ép '
                             'cấp.',
                             'Hướng dẫn vật lý trị liệu tập vận động thụ động duỗi cổ tay và ngón tay nhiều lần mỗi '
                             'ngày nhằm duy trì độ mềm dẻo bao khớp chống co rút dính khớp, phối hợp kích thích điện '
                             'cơ liệt (NMES).',
                             'Khuyên bệnh nhân tránh tuyệt đối tỳ đè gác cánh tay lên vật cứng hoặc gối đầu tay khi '
                             'ngủ.',
                             'Theo dõi tái khám định kỳ mỗi 4 tuần đánh giá dấu hiệu phục hồi sức cơ (thường hồi phục '
                             'dần từ cơ cánh tay quay đến duỗi cổ tay sau 6-12 tuần ở thể neurapraxia).'],
    'bien_the_kham': [   'Cổ tay phải rủ thõng xuống khi bệnh nhân đưa cẳng tay ra trước, sức cơ duỗi cổ tay và duỗi '
                         'các ngón tay tại khớp bàn ngón bằng 0/5, không dạng được ngón cái, nhưng lực gập ngón tay và '
                         'đối chiếu ngón cái vẫn tốt, cảm giác nông giảm rõ ở mu vùng kẽ ngón 1-2, phản xạ cơ tam đầu '
                         'bình thường nhưng phản xạ trâm quay mất.',
                         'Bệnh nhân vào viện sáng hôm sau ngủ dậy thấy liệt hoàn toàn động tác duỗi cổ tay trái (bàn '
                         'tay rủ cổ cò), khám dọc rãnh xoắn thân xương cánh tay trái hơi ê nhẹ khi ấn sâu, sức cơ tam '
                         'đầu duỗi khuỷu còn 5/5 (chứng tỏ tổn thương dưới nhánh tam đầu), mạch quay bắt rõ.',
                         'Đánh giá sức cơ chi trên: cơ cánh tay quay yếu 1/5 khi gấp khuỷu tư thế trung tính, mất khả '
                         'năng duỗi khớp bàn ngón tay 1-5 tay phải, nhưng khi bác sĩ giữ cố định cổ tay ở tư thế duỗi '
                         '20 độ thì bệnh nhân vẫn có thể duỗi nhẹ các khớp liên đốt (do các cơ giun do thần kinh trụ '
                         'giữa chi phối còn tốt).',
                         'Giảm cảm giác đau nông và xúc giác tinh khu trú ở vùng mu bàn tay phía bờ quay (hố lào giải '
                         'phẫu), cơ gập cổ tay quay và cơ gập sâu các ngón bình thường 5/5.',
                         'Bệnh nhân có tiền sử uống say ngủ quên gục cánh tay lên thành ghế gỗ 4 tiếng, sáng ra mất '
                         'hoàn toàn động tác ngửa cổ tay và duỗi ngón tay phải, không có vết thương hay gãy xương cánh '
                         'tay.',
                         'Khám thần kinh chi trên không thấy tổn thương dây giữa hay dây trụ đi kèm, chỉ tổn thương '
                         'đơn độc dây thần kinh quay đoạn 1/3 giữa ngoài cánh tay.'],
    'chan_doan': 'Liệt dây thần kinh quay ngoại biên cấp tính gây bàn tay rủ do chèn ép tại rãnh xoắn xương cánh tay.',
    'chinh': [   'bàn tay và các ngón tay bên bệnh bị rủ thõng xuống hoàn toàn không thể ngóc duỗi cổ tay và duỗi các '
                 'khớp bàn ngón tay lên được (dấu hiệu bàn tay rủ cổ cò)',
                 'mất khả năng dạng ngón tay cái ra ngoài trong mặt phẳng lòng bàn tay',
                 'tê bì giảm cảm giác vùng mu bàn tay đặc biệt ở khoang liên cốt thứ nhất giữa ngón cái và ngón trỏ'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Đeo ngay nẹp nâng đỡ cổ tay động hoặc nẹp tĩnh giữ cổ tay ở tư thế duỗi nhẹ 20-30 độ và các khớp bàn '
                'ngón hơi nâng (cock-up splint) để tránh giãn căng quá mức nhóm cơ duỗi liệt và giúp bàn tay cầm nắm '
                'được trong sinh hoạt.',
    'kham': 'Cổ tay phải rủ thõng xuống khi bệnh nhân đưa cẳng tay ra trước, sức cơ duỗi cổ tay và duỗi các ngón tay '
            'tại khớp bàn ngón bằng 0/5, không dạng được ngón cái, nhưng lực gập ngón tay và đối chiếu ngón cái vẫn '
            'tốt, cảm giác nông giảm rõ ở mu vùng kẽ ngón 1-2, phản xạ cơ tam đầu bình thường nhưng phản xạ trâm quay '
            'mất.',
    'nhom': 'người lớn',
    'phu': [   'thường khởi phát đột ngột sau một đêm ngủ say gối đầu tỳ đè lên mặt sau ngoài cánh tay (liệt đêm thứ '
               'bảy) hoặc sau chấn thương gãy thân xương cánh tay',
               'vẫn gập nắm chặt các ngón tay vào lòng bàn tay được nhưng lực nắm yếu hẳn đi do mất điểm tựa duỗi cổ '
               'tay',
               'phản xạ gân cơ tam đầu cánh tay thường vẫn còn nếu chèn ép xảy ra ở đoạn rãnh xoắn cánh tay'],
    'ten': 'liệt dây thần kinh quay gây bàn tay rủ'},
    {   'bien_the_chan_doan': [   'Hội chứng đường hầm xương trụ ở khuỷu tay phải mức độ trung bình.',
                              'Chèn ép dây thần kinh trụ tại rãnh ròng rọc khuỷu tay trái mạn tính có teo cơ bàn tay.',
                              'Hội chứng đường hầm khuỷu tay phải giai đoạn sớm chưa có teo cơ nội tại bàn tay.',
                              'Bán trật dây thần kinh trụ qua lồi cầu trong gây viêm kích thích đường hầm khuỷu.',
                              'Hội chứng đường hầm xương trụ hai bên liên quan thói quen tỳ gập khuỷu kéo dài.',
                              'Hội chứng đường hầm xương trụ giai đoạn muộn có dấu hiệu Froment dương tính và vuốt '
                              'trụ.'],
    'bien_the_ke_hoach': [   'Chỉ định đo điện cơ đồ và tốc độ dẫn truyền thần kinh chi trên (NCS/EMG) để đo mức độ '
                             'chậm tốc độ dẫn truyền thần kinh trụ qua đoạn khuỷu (giảm > 10 m/s so với đoạn cẳng tay) '
                             'và đánh giá tổn thương cơ nội tại bàn tay.',
                             'Siêu âm thần kinh trụ động qua rãnh ròng rọc đánh giá kích thước sưng phù thần kinh, '
                             'tình trạng bán trật dây thần kinh khi gấp khuỷu hoặc nang hạch chèn ép; chụp X-quang '
                             'khuỷu nếu có tiền sử chấn thương cũ.',
                             'Điều trị bảo tồn cho mức độ nhẹ-vừa: đeo nẹp khuỷu tay mềm ban đêm giữ khuỷu ở tư thế '
                             'duỗi nhẹ 30-45 độ (tránh gập khuỷu khi ngủ), hướng dẫn không tỳ khuỷu tay lên mặt bàn '
                             'cứng và dùng tai nghe khi gọi điện thoại.',
                             'Kê đơn Vitamin nhóm B (Methylcobalamin) và thuốc giảm đau thần kinh Pregabalin hoặc '
                             'Gabapentin liều thấp vào buổi tối nếu cảm giác tê buốt ảnh hưởng giấc ngủ.',
                             'Hướng dẫn các bài tập trượt dây thần kinh trụ nhẹ nhàng (nerve gliding exercises) dưới '
                             'sự hướng dẫn của kỹ thuật viên vật lý trị liệu.',
                             'Hội chẩn Ngoại Thần kinh hoặc Chỉnh hình phẫu thuật giải phóng đường hầm khuỷu (in situ '
                             'decompression) hoặc chuyển dây thần kinh trụ ra trước nếu có teo cơ tiến triển, yếu tay '
                             'rõ hoặc thất bại điều trị bảo tồn sau 3 tháng.'],
    'bien_the_kham': [   'Khám bàn tay phải thấy teo nhẹ cơ gian cốt mu tay thứ nhất và cơ mô út, dấu hiệu Froment '
                         'dương tính rõ khi kẹp giấy giữa ngón cái và trỏ, giảm cảm giác xúc giác tinh ở mặt gan và '
                         'mặt mu ngón 5 cùng nửa trụ ngón 4, gõ rãnh ròng rọc khuỷu phải gây tê giật xuống ngón út '
                         '(Tinel dương tính).',
                         'Nghiệm pháp gấp khuỷu tối đa (Elbow flexion test) kết hợp ép nhẹ vào rãnh trụ trong 60 giây '
                         'làm xuất hiện ngay cơn tê râm ran dữ dội vùng ngón áp út và ngón út bên trái, lực khép ngón '
                         'út yếu hơn bên phải (dấu hiệu Wartenberg dương tính nhẹ: ngón út hơi dạng ra ngoài).',
                         'Sờ dọc rãnh thần kinh trụ mặt sau trong khuỷu tay phải cảm nhận dây thần kinh trụ hơi dày và '
                         'trượt bán trật nhẹ lên mỏm trên lồi cầu trong mỗi khi gấp duỗi khuỷu, cảm giác bờ quay bàn '
                         'tay hoàn toàn bình thường (loại trừ chèn ép rễ C8 hoặc ống cổ tay).',
                         'Bàn tay trái bắt đầu có tư thế vuốt trụ nhẹ ở ngón 4 và ngón 5 (tăng duỗi khớp bàn ngón và '
                         'hơi gấp khớp liên đốt), sức cơ gấp sâu ngón 4-5 yếu nhẹ 4/5.',
                         'Bệnh nhân có tiền sử từng gãy cũ vùng khuỷu tay nhiều năm nay dẫn đến vẹo khuỷu ra ngoài, '
                         'khám thấy hội chứng chèn ép thần kinh trụ khuỷu tay điển hình tiến triển từ từ.',
                         'Khám cột sống cổ nghiệm pháp Spurling âm tính, cảm giác vùng trên cẳng tay trong (thần kinh '
                         'bì cẳng tay trong) hoàn toàn bình thường giúp định khu chèn ép đúng tại đường hầm xương trụ '
                         'khuỷu.'],
    'chan_doan': 'Hội chứng đường hầm xương trụ ở khuỷu tay phải mức độ trung bình.',
    'chinh': [   'tê bì châm chích như kiến bò dọc bờ trong cẳng tay xuống ngón tay út và nửa bờ trong ngón áp út',
                 'triệu chứng tê đau vùng khuỷu và ngón út tăng lên rõ rệt khi gập khuỷu tay lâu (như khi nghe điện '
                 'thoại hoặc nằm ngủ gập tay)',
                 'yếu lực kẹp véo giữa ngón cái và ngón trỏ kèm teo lõm khe gian cốt bàn tay ở giai đoạn muộn'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chỉ định đo điện cơ đồ và tốc độ dẫn truyền thần kinh chi trên (NCS/EMG) để đo mức độ chậm tốc độ dẫn '
                'truyền thần kinh trụ qua đoạn khuỷu (giảm > 10 m/s so với đoạn cẳng tay) và đánh giá tổn thương cơ '
                'nội tại bàn tay.',
    'kham': 'Khám bàn tay phải thấy teo nhẹ cơ gian cốt mu tay thứ nhất và cơ mô út, dấu hiệu Froment dương tính rõ '
            'khi kẹp giấy giữa ngón cái và trỏ, giảm cảm giác xúc giác tinh ở mặt gan và mặt mu ngón 5 cùng nửa trụ '
            'ngón 4, gõ rãnh ròng rọc khuỷu phải gây tê giật xuống ngón út (Tinel dương tính).',
    'nhom': 'người lớn',
    'phu': [   'dấu hiệu Froment dương tính: khi kẹp tờ giấy giữa ngón cái và ngón trỏ phải gập đốt xa ngón cái lại để '
               'bù trừ cho cơ khép ngón cái bị yếu',
               'gõ vào rãnh thần kinh trụ mặt trong khuỷu tay tạo cảm giác điện giật chạy xuống ngón út (dấu hiệu '
               'Tinel dương tính)',
               'mất khéo léo các ngón tay khi cài nút áo đánh máy tính hoặc cầm đũa gắp thức ăn'],
    'ten': 'hội chứng đường hầm xương trụ ở khuỷu'},
    {   'bien_the_chan_doan': [   'Đau thần kinh đùi bì dị cảm (Meralgia paresthetica) bên phải do chèn ép tại dây chằng '
                              'bẹn.',
                              'Hội chứng chèn ép dây thần kinh bì đùi ngoài bên trái mức độ vừa.',
                              'Đau thần kinh đùi bì dị cảm mạn tính liên quan đến béo phì và mặc đồ bó sát.',
                              'Đau thần kinh bì đùi ngoài đơn thuần không có tổn thương vận động chi dưới.',
                              'Theo dõi đau thần kinh đùi bì dị cảm cần phân biệt với chèn ép rễ thần kinh thắt lưng '
                              'L2-L3.',
                              'Đau thần kinh đùi bì dị cảm đáp ứng tốt với giải phóng áp lực vùng bẹn.'],
    'bien_the_ke_hoach': [   'Tư vấn điều chỉnh lối sống giải phóng áp lực chèn ép cơ học vùng nếp bẹn: mặc quần áo '
                             'rộng rãi cạp chun mềm, tháo bỏ thắt lưng chật hoặc dây đai mang dụng cụ nặng ở hông, và '
                             'lập kế hoạch giảm cân khoa học nếu thừa cân.',
                             'Chỉ định siêu âm dây thần kinh bì đùi ngoài vùng gai chậu trước trên để khảo sát hình '
                             'thái dây thần kinh bị phù nề dưới dây chằng bẹn và loại trừ khối u nang vùng hố chậu '
                             'chèn ép.',
                             'Đo tốc độ dẫn truyền cảm giác dây thần kinh bì đùi ngoài hoặc chụp MRI cột sống thắt '
                             'lưng nếu có triệu chứng không điển hình cần phân biệt với bệnh lý rễ thần kinh L2-L3.',
                             'Điều trị giảm đau thần kinh bằng Pregabalin hoặc Gabapentin liều thấp tăng dần, kết hợp '
                             'miếng dán Lidocaine 5% hoặc kem bôi Capsaicin tại vùng da dị cảm mặt ngoài đùi.',
                             'Thực hiện tiêm phong bế dây thần kinh bì đùi ngoài bằng thuốc tê pha Corticoid ngay phía '
                             'trong gai chậu trước trên dưới hướng dẫn siêu âm nếu đau rát ảnh hưởng nặng sinh hoạt.',
                             'Hội chẩn Ngoại Thần kinh xem xét phẫu thuật giải ép thần kinh hoặc cắt thần kinh chọn '
                             'lọc trong những trường hợp cực kỳ hiếm gặp kháng trị mọi biện pháp nội khoa trên 6 '
                             'tháng.'],
    'bien_the_kham': [   'Khám vùng đùi phải phát hiện một vùng giảm cảm giác đau và xúc giác tinh giới hạn rõ hình '
                         'vợt cầu lông kích thước 15x25cm ở mặt trước ngoài 1/3 giữa đùi, ấn điểm cách gai chậu trước '
                         'trên 1cm vào trong và xuống dưới làm tái hiện cơn tê giật xuống mặt ngoài đùi (Tinel bẹn '
                         'dương tính).',
                         'Sức cơ tứ đầu đùi và cơ khép đùi hai bên đạt 5/5 hoàn toàn bình thường, phản xạ gân gối L4 '
                         'đều hai bên, khớp háng và cột sống thắt lưng vận động tự do không đau.',
                         'Nghiệm pháp ép khung chậu (Pelvic compression test: nằm nghiêng bên lành, bác sĩ ấn ép thẳng '
                         'cánh chậu xuống dưới trong 30 giây làm chùng dây chằng bẹn) giúp giảm hẳn cảm giác tê rát '
                         'mặt ngoài đùi trái ngay lập tức.',
                         'Khi bệnh nhân đứng ưỡn hông duỗi quá mức khớp háng phải thì cảm giác châm chích rát bỏng mặt '
                         'ngoài đùi tăng vọt; sờ chạm nhẹ bằng bông gòn lên mặt ngoài đùi gây cảm giác tê bì lạ khác '
                         'hẳn mặt trong đùi.',
                         'Không có rối loạn vận mạch hay ban mụn nước ngoài da vùng đùi, mạch bẹn và mạch mu chân bắt '
                         'rõ mạnh, cân nặng bệnh nhân thuộc nhóm thừa cân béo bụng.',
                         'Khám thần kinh chi dưới loại trừ chèn ép rễ L2-L3 do không có yếu cơ thắt lưng chậu hay cơ '
                         'tứ đầu đùi, vùng tê khu trú thuần túy cảm giác mặt ngoài đùi.'],
    'chan_doan': 'Đau thần kinh đùi bì dị cảm (Meralgia paresthetica) bên phải do chèn ép tại dây chằng bẹn.',
    'chinh': [   'cảm giác tê bì nóng rát châm chích như kim châm hoặc bỏng rát trên một vùng da hình bầu dục ở mặt '
                 'trước ngoài đùi',
                 'triệu chứng tê rát tăng lên khi đứng thẳng lâu đi bộ kéo dài hoặc khi mặc quần bò bó sát thắt lưng',
                 'hoàn toàn không có yếu cơ teo cơ hay đau lan xuống dưới đầu gối'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Tư vấn điều chỉnh lối sống giải phóng áp lực chèn ép cơ học vùng nếp bẹn: mặc quần áo rộng rãi cạp '
                'chun mềm, tháo bỏ thắt lưng chật hoặc dây đai mang dụng cụ nặng ở hông, và lập kế hoạch giảm cân khoa '
                'học nếu thừa cân.',
    'kham': 'Khám vùng đùi phải phát hiện một vùng giảm cảm giác đau và xúc giác tinh giới hạn rõ hình vợt cầu lông '
            'kích thước 15x25cm ở mặt trước ngoài 1/3 giữa đùi, ấn điểm cách gai chậu trước trên 1cm vào trong và '
            'xuống dưới làm tái hiện cơn tê giật xuống mặt ngoài đùi (Tinel bẹn dương tính).',
    'nhom': 'người lớn',
    'phu': [   'thường giảm bớt khó chịu khi ngồi xuống gập nhẹ khớp háng làm chùng dây chằng bẹn',
               'sờ chạm nhẹ lên vùng da mặt ngoài đùi lại có cảm giác dị cảm khó chịu tăng cảm (allodynia) nhưng vận '
               'động đùi bình thường',
               'thường gặp ở người béo phì bụng to, người thắt dây lưng thợ xây nặng hoặc phụ nữ mang thai'],
    'ten': 'đau thần kinh đùi bì dị cảm'},
    {   'bien_the_chan_doan': [   'Đau dây thần kinh liên sườn sau zona (Postherpetic neuralgia) khoanh da T5-T6 phải.',
                              'Đau thần kinh sau zona dai dẳng vùng liên sườn trái mức độ nặng gây mất ngủ.',
                              'Hội chứng đau dây thần kinh liên sườn mạn tính sau nhiễm virus Herpes Zoster.',
                              'Đau thần kinh sau zona vùng ngực phải có biểu hiện loạn cảm đau (allodynia) rõ rệt.',
                              'Đau dây thần kinh liên sườn sau zona ở người cao tuổi đáp ứng chậm với giảm đau thông '
                              'thường.',
                              'Đau thần kinh mạn tính sau zona khoang liên sườn cần phối hợp thuốc điều trị đau thần '
                              'kinh.'],
    'bien_the_ke_hoach': [   'Giải thích rõ bản chất đau do tổn thương sợi thần kinh cảm giác sau virus zona (các '
                             'thuốc giảm đau kháng viêm thông thường như Paracetamol hay Ibuprofen ít có tác dụng) để '
                             'bệnh nhân kiên trì theo phác đồ thuốc đau thần kinh.',
                             'Khởi trị hàng đầu bằng thuốc điều biến kênh canxi Gabapentin (khởi đầu 300mg tối rồi '
                             'tăng dần liều theo đáp ứng dung nạp) hoặc Pregabalin (75-150mg ngày 2 lần) giúp giảm '
                             'phóng điện thần kinh và cải thiện giấc ngủ.',
                             'Phối hợp thuốc bôi/dán tại chỗ tác dụng trực tiếp lên vùng da sẹo lành hoàn toàn: miếng '
                             'dán Lidocaine 5% (dán 12 giờ, nghỉ 12 giờ/ngày) hoặc kem Capsaicin nồng độ thấp bôi giúp '
                             'khử nhạy thụ thể đau.',
                             'Cân nhắc phối hợp thuốc chống trầm cảm ba vòng liều thấp (Amitriptyline 10-25mg uống '
                             'buổi tối) hoặc nhóm SNRI (Duloxetine) nếu đơn trị liệu chưa kiểm soát tốt cơn đau mạn '
                             'tính ở bệnh nhân không có chống chỉ định tim mạch hay glôcôm.',
                             'Chuyển chuyên khoa Chống đau thực hiện thủ thuật phong bế thần kinh liên sườn chọn lọc '
                             'hoặc đốt sóng cao tần xung (PRF) rễ hạch gai sau nếu đau kháng trị nặng.',
                             'Tư vấn mặc áo lót cotton mềm mịn hoặc dùng miếng gạc lụa che nhẹ tránh ma sát áo lên '
                             'vùng da tăng cảm, đồng thời khuyến cáo tiêm vắc xin zona thế hệ mới khi ổn định cho '
                             'người lớn tuổi.'],
    'bien_the_kham': [   'Dọc khoang liên sườn T5-T6 bên phải từ cột sống lưng vòng sang mạn sườn ra xương ức có dải '
                         'vết sẹo thâm phẳng xen lẫn chấm sẹo bạc màu tròn nhỏ của tổn thương zona cũ đã khô lành hoàn '
                         'toàn cách đây 4 tháng, chạm nhẹ đầu ngón tay hoặc mảnh bông gòn lên vùng da này bệnh nhân co '
                         'rúm người kêu đau rát dữ dội (dấu hiệu loạn cảm đau allodynia).',
                         'Vùng lưng ngực bên trái theo khoanh da T7 có nhiều vết sẹo lõm giảm sắc tố giới hạn sắc nét '
                         'ở đường giữa cột sống và đường giữa ngực, thử cảm giác kim châm thấy giảm cảm giác nền nhưng '
                         'kích thích nhẹ gây đau bùng phát dữ dội kéo dài.',
                         'Bệnh nhân lớn tuổi nét mặt hốc hác thiếu ngủ, mặc áo rất rộng hở một bên vai ngực trái vì '
                         'không chịu nổi cảm giác vải áo cọ sát vào dải da liên sườn T4 trái, nghe phổi trong đều hai '
                         'bên, nhịp tim đều 76 l/p.',
                         'Sờ dọc bờ dưới xương sườn số 8 bên phải không thấy khối u hạch hay lạo xạo gãy xương, chỉ có '
                         'biểu hiện đau rát kiểu thần kinh khu trú đúng dải khoanh da (dermatome) từng mọc mụn nước '
                         'zona trước đó.',
                         'Vùng da sẹo zona cũ vùng hạ sườn phải có tăng sắc tố sẫm màu, dấu hiệu đau buốt từng cơn như '
                         'kim chích điện giật tăng về đêm khiến bệnh nhân phải thức trắng nhiều tuần.',
                         'Khám cột sống ngực không gù vẹo ấn không đau điểm xương, các xét nghiệm tim mạch điện tâm đồ '
                         'loại trừ cơn đau thắt ngực.'],
    'chan_doan': 'Đau dây thần kinh liên sườn sau zona (Postherpetic neuralgia) khoanh da T5-T6 phải.',
    'chinh': [   'đau bỏng rát buốt nhói hoặc như điện giật kéo dài trên 3 tháng dọc theo một khoang liên sườn một bên '
                 'thân mình sau khi ban mụn nước zona đã lành sẹo',
                 'hiện tượng tăng đau khi chạm nhẹ (allodynia): chỉ cần áo sơ mi cọ nhẹ hoặc làn gió thổi qua vùng da '
                 'sẹo cũ cũng gây đau buốt dữ dội',
                 'trên vùng da đau có các vết sẹo bạc màu hoặc sẹo thâm tăng sắc tố phân bố thành dải khoanh vùng một '
                 'bên từ cột sống ra trước ngực không vượt quá đường giữa'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Giải thích rõ bản chất đau do tổn thương sợi thần kinh cảm giác sau virus zona (các thuốc giảm đau '
                'kháng viêm thông thường như Paracetamol hay Ibuprofen ít có tác dụng) để bệnh nhân kiên trì theo phác '
                'đồ thuốc đau thần kinh.',
    'kham': 'Dọc khoang liên sườn T5-T6 bên phải từ cột sống lưng vòng sang mạn sườn ra xương ức có dải vết sẹo thâm '
            'phẳng xen lẫn chấm sẹo bạc màu tròn nhỏ của tổn thương zona cũ đã khô lành hoàn toàn cách đây 4 tháng, '
            'chạm nhẹ đầu ngón tay hoặc mảnh bông gòn lên vùng da này bệnh nhân co rúm người kêu đau rát dữ dội (dấu '
            'hiệu loạn cảm đau allodynia).',
    'nhom': 'người lớn',
    'phu': [   'ngứa ngáy râm ran hoặc tê bì mất cảm giác xen kẽ với các cơn đau nhói đột ngột về đêm làm mất ngủ '
               'triền miên',
               'mệt mỏi lo âu suy nhược tinh thần do đau mạn tính dai dẳng',
               'khám tim phổi và X-quang ngực bình thường không có tổn thương nội tạng vùng ngực'],
    'ten': 'đau dây thần kinh liên sườn sau zona'},
    {   'bien_the_chan_doan': [   'Bệnh nhược cơ thể mắt (Ocular Myasthenia Gravis) mức độ nhẹ vừa chưa toàn thể hóa.',
                              'Nhược cơ thể mắt biểu hiện sụp mi bất đối xứng và nhìn đôi biến thiên trong ngày.',
                              'Theo dõi nhược cơ thể mắt cần tầm soát u tuyến ức và kháng thể kháng thụ thể '
                              'Acetylcholine.',
                              'Bệnh nhược cơ thể mắt độ 1 theo phân loại MGFA có test túi đá lạnh dương tính.',
                              'Nhược cơ thể mắt giai đoạn sớm cần phân biệt với liệt dây thần kinh vận nhãn hoặc bệnh '
                              'lý tuyến giáp.',
                              'Nhược cơ tự miễn thể mắt đơn thuần đáp ứng tốt với thuốc kháng men cholinesterase.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm máu tìm kháng thể kháng thụ thể Acetylcholine (AChR-Ab) và kháng thể '
                             'kháng MuSK (lưu ý thể mắt có tỷ lệ âm tính cao hơn thể toàn thân nên cần phối hợp thêm '
                             'chẩn đoán điện sinh lý).',
                             'Chỉ định đo điện cơ sợi đơn độc (SFEMG) vùng cơ vòng mi hoặc test kích thích thần kinh '
                             'lặp lại (RNS) và chụp CT lồng ngực có tiêm thuốc cản quang tầm soát tăng sản hoặc u '
                             'tuyến ức (Thymoma) bắt buộc cho mọi bệnh nhân nhược cơ.',
                             'Xét nghiệm kiểm tra chức năng tuyến giáp TSH, FT4 và chụp MRI sọ não mạch máu não nếu '
                             'cần loại trừ phình mạch chèn ép dây III hoặc bệnh mắt tuyến giáp.',
                             'Khởi đầu điều trị triệu chứng bằng thuốc ức chế men Acetylcholinesterase đường uống '
                             'Pyridostigmine (Mestinon) 60mg chia 3-4 lần/ngày; nếu không cải thiện đủ song thị/sụp mi '
                             'thì phối hợp Corticoid (Prednisolone liều tăng chậm cẩn trọng) hoặc thuốc ức chế miễn '
                             'dịch.',
                             'Hướng dẫn bệnh nhân sử dụng miếng che mắt luân phiên tạm thời hoặc dán lăng kính lên '
                             'kính mắt để giảm khó chịu do nhìn đôi khi lái xe đọc sách.',
                             'Dặn dò theo dõi sát và tái khám ngay nếu xuất hiện các dấu hiệu lan tỏa toàn thân như '
                             'nói ngọng giọng mũi, nuốt nghẹn sặc, khó nhai hoặc khó thở yếu tay chân; cung cấp danh '
                             'sách các thuốc chống chỉ định gây nặng bệnh nhược cơ (như kháng sinh aminoglycoside, '
                             'fluoroquinolone, thuốc chẹn beta, magie).'],
    'bien_the_kham': [   'Mi mắt trên bên phải sụp xuống che gần nửa đồng tử khi khám lúc 4 giờ chiều (mắt trái sụp '
                         'nhẹ hơn), yêu cầu bệnh nhân nhìn ngước lên trần nhà liên tục 45 giây thì mi phải sụp kín '
                         'xuống che hoàn toàn con ngươi; đặt túi đá lạnh bọc gạc lên mi phải trong 2 phút sau đó mi '
                         'mắt mở nâng lên cao hơn rõ rệt 3mm (Ice-pack test dương tính).',
                         'Khám vận nhãn thấy hạn chế đưa mắt phải ra ngoài và lên trên gây nhìn đôi hai hình ngang, '
                         'đồng tử hai bên đều 3mm phản xạ ánh sáng nhạy bình thường (loại trừ liệt dây III chèn ép '
                         'phình mạch), không yếu cơ vòng mi khi nhắm chặt mắt.',
                         'Bệnh nhân có dấu hiệu Cogan giật mi mắt (Cogan lid twitch sign) dương tính rõ: khi nhìn '
                         'xuống rồi đột ngột nhìn thẳng về trước, mi mắt trên bên trái giật nẩy lên cao thoáng qua rồi '
                         'lại tụt xuống.',
                         'Test nhắm mắt chủ động bộc lộ yếu nhẹ cơ vòng mắt hai bên (dấu hiệu lông mi vùi không kín '
                         'hoàn toàn), nhưng sức cơ nói nuốt (giọng nói không khàn mũi), cơ cổ và sức cơ tứ chi đều đạt '
                         '5/5.',
                         'Hiện tượng sụp mi luân phiên lúc bên trái nặng lúc bên phải nặng hơn, không đau nhức đầu '
                         'không đau hốc mắt, hoàn toàn không có lồi mắt hay phù nề mi mắt.',
                         'Khi bệnh nhân dùng tay nâng giữ mi mắt đang sụp lên thì mi mắt bên đối diện lập tức sụp '
                         'xuống nhẹ theo định luật Hering.'],
    'chan_doan': 'Bệnh nhược cơ thể mắt (Ocular Myasthenia Gravis) mức độ nhẹ vừa chưa toàn thể hóa.',
    'chinh': [   'sụp mi mắt một bên hoặc hai bên bất đối xứng tiến triển nặng dần về cuối ngày chiều tối và cải thiện '
                 'rõ sau khi ngủ nghỉ',
                 'nhìn đôi (song thị) hai hình khi nhìn tập trung kéo dài hoặc nhìn lệch sang bên do yếu mệt các cơ '
                 'vận nhãn',
                 'triệu chứng sụp mi và nhìn đôi biến thiên thất thường trong ngày không theo quy luật cố định của một '
                 'dây thần kinh sọ đơn lẻ'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Làm xét nghiệm máu tìm kháng thể kháng thụ thể Acetylcholine (AChR-Ab) và kháng thể kháng MuSK (lưu ý '
                'thể mắt có tỷ lệ âm tính cao hơn thể toàn thân nên cần phối hợp thêm chẩn đoán điện sinh lý).',
    'kham': 'Mi mắt trên bên phải sụp xuống che gần nửa đồng tử khi khám lúc 4 giờ chiều (mắt trái sụp nhẹ hơn), yêu '
            'cầu bệnh nhân nhìn ngước lên trần nhà liên tục 45 giây thì mi phải sụp kín xuống che hoàn toàn con ngươi; '
            'đặt túi đá lạnh bọc gạc lên mi phải trong 2 phút sau đó mi mắt mở nâng lên cao hơn rõ rệt 3mm (Ice-pack '
            'test dương tính).',
    'nhom': 'người lớn',
    'phu': [   'nghiệm pháp nhìn ngước lên trần nhà liên tục trong 60 giây làm mi mắt sụp nhanh xuống (nghiệm pháp '
               'Simpson dương tính)',
               'chườm túi đá lạnh lên mi mắt sụp trong 2 phút giúp nâng mi mắt mở to ra rõ rệt ngay sau đó (Ice-pack '
               'test dương tính)',
               'hoàn toàn không có rối loạn đồng tử, không yếu cơ nhai nuốt hay yếu liệt tay chân ở thể mắt đơn thuần'],
    'ten': 'nhược cơ thể mắt'},
    {   'bien_the_chan_doan': [   'Liệt dây thần kinh mác chung bên phải cấp tính gây bàn chân rủ do chèn ép vùng chỏm '
                              'xương mác.',
                              'Tổn thương thần kinh mác chung cấp tính sau tư thế ngồi vắt chéo chân hoặc ngồi xổm kéo '
                              'dài.',
                              'Liệt dây thần kinh mác chung bên trái thể mất dẫn truyền myelin thoáng qua.',
                              'Theo dõi liệt dây thần kinh mác chung cần phân biệt với chèn ép rễ thần kinh thắt lưng '
                              'L5.',
                              'Liệt dây thần kinh mác chung cấp tính chưa có teo cơ khu trước ngoài cẳng chân.',
                              'Bàn chân rủ cấp tính do tổn thương thần kinh mác chung cần đeo nẹp nâng bàn chân.'],
    'bien_the_ke_hoach': [   'Đeo ngay nẹp chỉnh hình cổ bàn chân (AFO - Ankle Foot Orthosis) để nâng giữ bàn chân ở '
                             'góc 90 độ khi đi lại, giúp cải thiện dáng đi bình thường và phòng ngừa té ngã vấp mũi '
                             'chân cũng như co rút gân gót.',
                             'Chỉ định đo điện cơ đồ và dẫn truyền thần kinh chi dưới (NCS/EMG) qua đoạn chỏm xương '
                             'mác (nên làm sau 2-3 tuần nếu mới khởi phát) để xác định chính xác vị trí nghẽn dẫn '
                             'truyền và tiên lượng tổn thương sợi trục hay myelin.',
                             'Siêu âm dây thần kinh mác chung tại vùng chỏm xương mác loại trừ nang hoạt dịch khớp '
                             'chày mác trên chèn ép thần kinh (intraneural ganglion cyst) hoặc chụp MRI cột sống thắt '
                             'lưng nếu nghi ngờ rễ L5.',
                             'Kê đơn Vitamin nhóm B (Methylcobalamin, B1, B6) hỗ trợ phục hồi sợi thần kinh, hướng dẫn '
                             'tránh tuyệt đối tư thế ngồi vắt chéo chân, ngồi xổm hay tỳ ép mặt ngoài đầu gối.',
                             'Tập vật lý trị liệu vận động thụ động kéo giãn gân gót chống co rút, kích thích điện cơ '
                             'vùng cẳng chân trước (NMES) và tập phục hồi sức cơ chủ động khi có tín hiệu hồi phục.',
                             'Hội chẩn Ngoại Thần kinh giải ép thần kinh mác chung tại đường hầm xương mác nếu phát '
                             'hiện khối u nang chèn ép hoặc không có dấu hiệu hồi phục điện cơ sau 3-4 tháng theo '
                             'dõi.'],
    'bien_the_kham': [   'Bàn chân phải ở tư thế rủ thõng tự nhiên khi ngồi buông thõng chân, sức cơ chày trước (gấp '
                         'mu bàn chân) và cơ duỗi ngón cái dài chỉ đạt 1/5, động tác nghiêng ngoài bàn chân yếu 1/5, '
                         'nhưng sức cơ gấp lòng bàn chân và nghiêng trong bàn chân đạt 5/5 (khác với tổn thương rễ '
                         'L5).',
                         'Bệnh nhân bước đi trong phòng khám với dáng đi bước cao bên trái rõ rệt, mũi chân trái vỗ '
                         'phạch xuống sàn mỗi bước đi, giảm cảm giác châm kim dọc mặt ngoài 1/3 dưới cẳng chân và toàn '
                         'bộ mu bàn chân trái, gõ vùng cổ chỏm xương mác trái có dấu Tinel tê giật xuống mu chân.',
                         'Khám thần kinh chi dưới ghi nhận phản xạ gân gót và gân gối hai bên bình thường đối xứng, '
                         'nghiệm pháp Lasegue âm tính, cột sống thắt lưng không đau giúp loại trừ thoát vị đĩa đệm '
                         'chèn ép rễ L5.',
                         'Yếu liệt đột ngột động tác ngóc cổ chân phải sau một ca phẫu thuật nằm nghiêng kéo dài hoặc '
                         'ngồi xổm làm vườn nhiều giờ, không có sưng đau bắp chân hay gãy xương chỏm mác.',
                         'Thử nghiệm vận động các cơ vùng cẳng chân: bệnh nhân đi bằng mũi chân (nhón gót) rất tốt '
                         'nhưng hoàn toàn không thể đi bằng gót chân bên phải được.',
                         'Khám vùng chỏm xương mác ngoài đầu gối trái không thấy khối u hạch chèn ép rõ dưới da, mạch '
                         'mu chân đập rõ, chỉ có mất dẫn truyền cấp tính dây thần kinh mác chung.'],
    'chan_doan': 'Liệt dây thần kinh mác chung bên phải cấp tính gây bàn chân rủ do chèn ép vùng chỏm xương mác.',
    'chinh': [   'bàn chân bên bệnh bị rủ thõng xuống không thể nhấc mu bàn chân và các ngón chân lên khỏi mặt đất '
                 '(dấu hiệu bàn chân rủ)',
                 'dáng đi bước cao nhấc đầu gối lên cao bất thường để mũi bàn chân không bị quệt lê trên mặt sàn (dáng '
                 'đi vạt cỏ / steppage gait)',
                 'mất hoặc giảm cảm giác tê bì dọc mặt ngoài cẳng chân và mu bàn chân cùng vùng kẽ ngón chân 1-2'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Đeo ngay nẹp chỉnh hình cổ bàn chân (AFO - Ankle Foot Orthosis) để nâng giữ bàn chân ở góc 90 độ khi '
                'đi lại, giúp cải thiện dáng đi bình thường và phòng ngừa té ngã vấp mũi chân cũng như co rút gân gót.',
    'kham': 'Bàn chân phải ở tư thế rủ thõng tự nhiên khi ngồi buông thõng chân, sức cơ chày trước (gấp mu bàn chân) '
            'và cơ duỗi ngón cái dài chỉ đạt 1/5, động tác nghiêng ngoài bàn chân yếu 1/5, nhưng sức cơ gấp lòng bàn '
            'chân và nghiêng trong bàn chân đạt 5/5 (khác với tổn thương rễ L5).',
    'nhom': 'người lớn',
    'phu': [   'thường xuất hiện sau thói quen ngồi vắt chéo chân kéo dài ngồi xổm lâu bó bột cẳng chân chật hoặc chấn '
               'thương vùng chỏm xương mác',
               'lực xoay nghiêng bàn chân ra ngoài (nhóm cơ mác) bị yếu nặng nhưng lực gấp lòng bàn chân và xoay vào '
               'trong (thần kinh chày sau) vẫn khỏe 5/5',
               'phản xạ gân gót S1 hai bên vẫn còn nguyên vẹn bình thường'],
    'ten': 'liệt dây thần kinh mác chung bàn tay rủ chân'},
    {   'bien_the_chan_doan': [   'Bệnh xơ cứng rải rác thể tái phát thuyên giảm (RRMS) đang trong đợt tái phát cấp tính.',
                              'Xơ cứng rải rác thể tái phát thuyên giảm biểu hiện viêm thần kinh thị giác và tổn '
                              'thương tủy cổ.',
                              'Xơ cứng rải rác (Multiple Sclerosis) thể tái phát thuyên giảm giai đoạn ổn định ngoại '
                              'đợt cấp.',
                              'Xơ cứng rải rác thể tái phát thuyên giảm đáp ứng tốt với điều trị điều hòa miễn dịch.',
                              'Theo dõi xơ cứng rải rác thể tái phát thuyên giảm phân biệt với viêm tủy thị thần kinh '
                              '(NMO).',
                              'Xơ cứng rải rác thể tái phát thuyên giảm có hội chứng mất myelin đa ổ theo không gian '
                              'và thời gian.'],
    'bien_the_ke_hoach': [   'Chụp cộng hưởng từ (MRI) sọ não và tủy sống có tiêm thuốc đối quang từ Gadolinium tìm '
                             'các ổ tổn thương mất myelin chất trắng đặc trưng quanh não thất (ngón tay Dawson), thể '
                             'chai, thân não và tủy sống (đánh giá tiêu chuẩn McDonald phân tán theo không gian và '
                             'thời gian).',
                             'Xét nghiệm dịch não tủy tìm dải Oligoclonal (Oligoclonal bands - OCB dương tính) và chỉ '
                             'số IgG, đồng thời xét nghiệm máu tìm kháng thể AQP4-IgG và MOG-IgG để phân biệt với phổ '
                             'bệnh viêm tủy thị thần kinh (NMOSD).',
                             'Điều trị đợt tái phát cấp tính bằng truyền tĩnh mạch liều cao Methylprednisolone '
                             '(Solu-Medrol 1000mg/ngày trong 3-5 ngày) để rút ngắn thời gian hồi phục triệu chứng thần '
                             'kinh.',
                             'Khởi động sớm liệu pháp điều biến bệnh lâu dài (DMT - Disease Modifying Therapies) như '
                             'Interferon beta, Dimethyl fumarate, Fingolimod hoặc Ocrelizumab/Natalizumab tùy mức độ '
                             'hoạt động bệnh nhằm ngăn ngừa tái phát và tích lũy khuyết tật.',
                             'Điều trị triệu chứng hỗ trợ: dùng Baclofen giảm co cứng cơ nếu có, Oxybutynin cho rối '
                             'loạn tiểu gấp bàng quang, bổ sung Vitamin D3 duy trì nồng độ tối ưu và tập phục hồi chức '
                             'năng.',
                             'Tư vấn bệnh nhân tránh tắm nước quá nóng phòng hiện tượng Uhthoff, giữ lối sống điều độ '
                             'và khám theo dõi định kỳ chuyên khoa Thần kinh mỗi 3-6 tháng.'],
    'bien_the_kham': [   'Khám thần kinh bệnh nhân nữ trẻ tuổi ghi nhận liệt vận nhãn liên nhân hai bên (khi liếc sang '
                         'phải mắt trái không đưa vào trong được và mắt phải rung giật nhãn cầu), tổn thương khuyết '
                         'đồng tử hướng tâm tương đối (RAPD) bên mắt phải và đĩa thị giác phải hơi bạc màu thái dương '
                         '(di chứng viêm thị thần kinh cũ).',
                         'Bệnh nhân có biểu hiện thất điều tiểu não nhẹ (test ngón tay chỉ mũi hơi run cuối tầm bên '
                         'trái), tăng phản xạ gân xương tứ chi lan tỏa kèm dấu hiệu Babinski dương tính hai bên và '
                         'giảm cảm giác rung âm thoa ở hai mắt cá chân.',
                         'Khi cho bệnh nhân gập cổ tối đa cằm chạm ngực, bệnh nhân xuất hiện ngay cảm giác luồng điện '
                         'chạy dọc cột sống xuống hai chân (dấu hiệu Lhermitte dương tính), sức cơ hai chân đạt 4/5.',
                         'Đánh giá tiền sử có 3 đợt bùng phát khác nhau trong 2 năm qua (đợt mờ mắt trái tự khỏi, đợt '
                         'tê bì nửa thân phải và đợt này tiểu gấp kèm yếu hai chân), khám hiện tại tiểu tiện hơi són '
                         'gấp và giảm cảm giác nông từ ngang mức rốn trở xuống.',
                         'Thị lực mắt trái giảm còn 4/10 kèm ám điểm trung tâm và rối loạn sắc giác đỏ-xanh, đau tăng '
                         'khi ấn nhẹ nhãn cầu hoặc liếc mắt, phản xạ bụng nông mất cả hai bên.',
                         'Khám thấy rung giật nhãn cầu đa hướng nhẹ, nói hơi ngập ngừng kiểu tiểu não nhẹ, thang điểm '
                         'khuyết tật mở rộng EDSS hiện ở mức 2,5 điểm.'],
    'chan_doan': 'Bệnh xơ cứng rải rác thể tái phát thuyên giảm (RRMS) đang trong đợt tái phát cấp tính.',
    'chinh': [   'các đợt triệu chứng thần kinh khu trú khởi phát bán cấp kéo dài trên 24 giờ rồi thuyên giảm dần hoàn '
                 'toàn hoặc một phần xen kẽ giai đoạn ổn định',
                 'mờ nhòe mất thị lực cấp một bên mắt kèm đau nhức hốc mắt khi liếc mắt (viêm thần kinh thị giác hậu '
                 'nhãn cầu)',
                 'tê bì mất cảm giác theo khoanh tủy yếu liệt nửa người hoặc liệt hai chi dưới kèm dáng đi loạng '
                 'choạng thất điều tiểu não'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chụp cộng hưởng từ (MRI) sọ não và tủy sống có tiêm thuốc đối quang từ Gadolinium tìm các ổ tổn '
                'thương mất myelin chất trắng đặc trưng quanh não thất (ngón tay Dawson), thể chai, thân não và tủy '
                'sống (đánh giá tiêu chuẩn McDonald phân tán theo không gian và thời gian).',
    'kham': 'Khám thần kinh bệnh nhân nữ trẻ tuổi ghi nhận liệt vận nhãn liên nhân hai bên (khi liếc sang phải mắt '
            'trái không đưa vào trong được và mắt phải rung giật nhãn cầu), tổn thương khuyết đồng tử hướng tâm tương '
            'đối (RAPD) bên mắt phải và đĩa thị giác phải hơi bạc màu thái dương (di chứng viêm thị thần kinh cũ).',
    'nhom': 'người lớn',
    'phu': [   'dấu hiệu Lhermitte: cảm giác luồng điện giật chạy dọc xuống sống lưng và tay chân khi gập cổ cúi đầu '
               'về trước',
               'hiện tượng Uhthoff: các triệu chứng mờ mắt yếu chi nặng lên rõ rệt khi tắm nước nóng sốt hoặc tập thể '
               'dục nóng người',
               'liệt vận nhãn liên nhân (INO) gây nhìn đôi và rung giật nhãn cầu khi liếc ngang kèm mệt mỏi mạn tính'],
    'ten': 'xơ cứng rải rác thể tái phát thuyên giảm'},
    {   'bien_the_chan_doan': [   'Teo cơ tủy sống khởi phát người lớn (SMA type 4) liên quan đột biến gen SMN1.',
                              'Bệnh lý nơ-ron vận động dưới mạn tính kiểu teo cơ tủy sống người trưởng thành.',
                              'Teo cơ tủy sống khởi phát muộn biểu hiện yếu gốc chi đối xứng và mất phản xạ gân xương.',
                              'Theo dõi teo cơ tủy sống người lớn (SMA typ IV) tiến triển chậm giữ được vận động đi '
                              'lại.',
                              'Teo cơ tủy sống người lớn cần chẩn đoán phân biệt với bệnh loạn dưỡng cơ chi-gốc và xơ '
                              'cứng cột bên teo cơ.',
                              'Teo cơ tủy sống khởi phát tuổi trưởng thành có chỉ định làm xét nghiệm gen SMN1.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm di truyền phân tử (MLPA hoặc giải trình tự gen) tìm đột biến mất đoạn '
                             'đồng hợp tử exon 7-8 gen SMN1 trên nhiễm sắc thể 5q13 và đếm số lượng bản sao gen dự '
                             'phòng SMN2 để khẳng định chẩn đoán.',
                             'Chỉ định đo điện cơ đồ (EMG) bộc lộ hình ảnh tổn thương nơ-ron sừng trước tủy sống mạn '
                             'tính (điện thế sợi cơ tự phát, đơn vị vận động khổng lồ biên độ cao thời khoảng rộng) và '
                             'tốc độ dẫn truyền cảm giác hoàn toàn bình thường.',
                             'Xét nghiệm men cơ Creatine Kinase (CK) máu (thường bình thường hoặc chỉ tăng nhẹ dưới 5 '
                             'lần, giúp phân biệt với bệnh cơ nguyên phát tăng rất cao) và chụp MRI tủy sống loại trừ '
                             'chèn ép tủy.',
                             'Hội chẩn chuyên khoa Thần kinh Di truyền đánh giá chỉ định tiếp cận các liệu pháp điều '
                             'trị đặc hiệu tăng tổng hợp protein SMN như Risdiplam đường uống hoặc Nusinersen tiêm nội '
                             'tủy nếu có điều kiện áp dụng.',
                             'Xây dựng chương trình tập vật lý trị liệu nhẹ nhàng vừa sức (bơi lội, đạp xe đạp tĩnh, '
                             'kéo giãn chống co rút khớp) tuyệt đối tránh tập tạ quá sức gây kiệt quệ nơ-ron vận động '
                             'còn lại.',
                             'Theo dõi chức năng hô hấp định kỳ hàng năm và tư vấn di truyền học cho các thành viên '
                             'gia đình.'],
    'bien_the_kham': [   'Khám vận động cho thấy yếu cơ gốc chi đối xứng hai bên: sức cơ gập đùi và giạng vai đạt '
                         '3+/5, sức cơ ngọn chi bàn tay bàn chân còn khá tốt 4+/5; bệnh nhân phải dùng tay chống lên '
                         'đùi để tự đứng dậy từ tư thế ngồi thấp (dấu hiệu Gowers nhẹ), hoàn toàn mất phản xạ gân gối '
                         'và gân gót hai bên.',
                         'Quan sát khối cơ tứ đầu đùi và cơ delta thấy teo mỏng nhẹ kèm hiện tượng rung giật bó cơ '
                         '(fasciculations) lăn tăn dưới da vùng đùi và cơ tam đầu cánh tay; thè lưỡi kiểm tra thấy hơi '
                         'run giật bó cơ rìa lưỡi nhẹ nhưng không khó nuốt hay nói ngọng.',
                         'Khi bệnh nhân đưa thẳng hai tay ra trước xòe ngón, xuất hiện run nhẹ không đều biên độ nhỏ ở '
                         'các ngón tay (polyminimyoclonus); khám cảm giác nông đau nhiệt và cảm giác sâu rung âm thoa '
                         'ở ngón chân cái hoàn toàn nguyên vẹn.',
                         'Không có dấu hiệu tổn thương nơ-ron vận động trên (không tăng trương lực cơ, dấu hiệu '
                         'Babinski âm tính hai bên, không có rung giật bàn chân), chức năng hô hấp đo dung tích sống '
                         'FVC bình thường.',
                         'Dáng đi lắc lư hai bên mông (dáng đi Trendelenburg hai bên / dáng đi vịt) do yếu nhóm cơ '
                         'mông nhỡ gốc chi, bắp chân không có phì đại giả như loạn dưỡng cơ Duchenne.',
                         'Bệnh nhân có tiền sử yếu mỏi hai chân âm thầm kéo dài 4 năm nay, khám thấy tổn thương nơ-ron '
                         'vận động dưới đơn thuần tại sừng trước tủy sống không kèm rối loạn tiểu tiện.'],
    'chan_doan': 'Teo cơ tủy sống khởi phát người lớn (SMA type 4) liên quan đột biến gen SMN1.',
    'chinh': [   'yếu cơ gốc chi tiến triển rất chậm và đối xứng hai bên ưu thế hai chân (khó leo cầu thang đứng lên '
                 'từ ghế thấp hoặc chải đầu)',
                 'teo cơ rõ rệt ở vùng đùi vai kèm các sợi cơ rung giật tự phát li ti dưới da (rung giật bó cơ - '
                 'fasciculations) đặc biệt ở đùi cánh tay và lưỡi',
                 'mất hoặc giảm sâu toàn bộ phản xạ gân xương tứ chi trong khi cảm giác nông sâu và cơ tròn hoàn toàn '
                 'bình thường'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Làm xét nghiệm di truyền phân tử (MLPA hoặc giải trình tự gen) tìm đột biến mất đoạn đồng hợp tử exon '
                '7-8 gen SMN1 trên nhiễm sắc thể 5q13 và đếm số lượng bản sao gen dự phòng SMN2 để khẳng định chẩn '
                'đoán.',
    'kham': 'Khám vận động cho thấy yếu cơ gốc chi đối xứng hai bên: sức cơ gập đùi và giạng vai đạt 3+/5, sức cơ ngọn '
            'chi bàn tay bàn chân còn khá tốt 4+/5; bệnh nhân phải dùng tay chống lên đùi để tự đứng dậy từ tư thế '
            'ngồi thấp (dấu hiệu Gowers nhẹ), hoàn toàn mất phản xạ gân gối và gân gót hai bên.',
    'nhom': 'người lớn',
    'phu': [   'run nhẹ đầu ngón tay kiểu rung tần số nhanh (polyminimyoclonus) khi đưa hai tay thẳng ra trước',
               'chuột rút đau mỏi bắp chân đùi xuất hiện thường xuyên sau vận động nhẹ',
               'bệnh khởi phát ở tuổi trưởng thành (sau 20-30 tuổi) tiến triển từ từ giữ được khả năng tự đi lại nhiều '
               'năm'],
    'ten': 'teo cơ tủy sống khởi phát người lớn'},
    {   'bien_the_chan_doan': [   'Co thắt nửa mặt bên trái vô căn nguyên phát (nghi xung đột mạch máu - thần kinh VII).',
                              'Co thắt nửa mặt phải mạn tính mức độ nặng gây co nhắm mắt ảnh hưởng thị lực.',
                              'Co thắt nửa mặt vô căn bên trái giai đoạn lan tỏa xuống cơ vùng miệng và cổ.',
                              'Theo dõi co thắt nửa mặt nguyên phát cần chụp MRI sọ não loại trừ u góc cầu tiểu não.',
                              'Co thắt nửa mặt vô căn đáp ứng tốt với tiêm độc tố Botulinum toxin type A.',
                              'Co thắt nửa mặt bên phải tái phát mạn tính sau hết tác dụng tiêm Botulinum.'],
    'bien_the_ke_hoach': [   'Chỉ định chụp cộng hưởng từ (MRI) sọ não chuỗi xung phân giải cao vùng hố sau '
                             '(CISS/FIESTA) và MRA mạch máu não để phát hiện quai mạch máu (thường là động mạch tiểu '
                             'não trước dưới AICA hoặc PICA) chèn ép vào vùng rễ xuất phát của dây thần kinh VII và '
                             'loại trừ khối u góc cầu tiểu não.',
                             'Lựa chọn điều trị nội khoa tối ưu hàng đầu hiện nay: tiêm vi điểm độc tố Botulinum toxin '
                             'type A (Botox/Dysport) vào các cơ bị co giật (cơ vòng mi, cơ gò má, cơ cằm) giúp cắt cơn '
                             'co giật hiệu quả 85-95% trong 3-4 tháng.',
                             'Cân nhắc dùng thuốc uống hỗ trợ tạm thời trong lúc chờ tiêm hoặc ca nhẹ như '
                             'Carbamazepine, Clonazepam hoặc Gabapentin (tuy nhiên hiệu quả thuốc uống thường hạn chế '
                             'hơn nhiều so với tiêm Botulinum).',
                             'Hội chẩn chuyên khoa Ngoại Thần kinh xem xét phẫu thuật giải ép vi mạch (MVD - '
                             'Microvascular Decompression) tách quai mạch máu khỏi rễ thần kinh số VII nếu bệnh nhân '
                             'trẻ khỏe, có bằng chứng xung đột mạch máu rõ trên MRI và mong muốn điều trị triệt để.',
                             'Tư vấn bệnh nhân giữ tinh thần thư giãn ngủ đủ giấc, hạn chế cà phê chất kích thích và '
                             'tránh căng thẳng vì stress làm cơn giật bùng phát mạnh hơn.',
                             'Theo dõi tái khám lặp lại mũi tiêm Botulinum định kỳ mỗi 3-4 tháng và kiểm tra tránh tác '
                             'dụng phụ sụp mi hay khô mắt nhẹ sau tiêm.'],
    'bien_the_kham': [   'Quan sát bệnh nhân lúc ngồi yên thấy xuất hiện các cơn co giật rung liên hồi ở mi mắt dưới '
                         'bên trái rồi nhanh chóng co thắt mạnh làm mắt trái nhắm híp lại đồng thời kéo giật khóe '
                         'miệng trái chếch lên trên và co cứng cơ bám da cổ trái (dấu hiệu Babinski-2: đồng thời nâng '
                         'cung mày khi mắt nhắm chặt), nửa mặt phải hoàn toàn bình thường.',
                         'Khi yêu cầu bệnh nhân nhắm mắt mở mắt mạnh hoặc chu môi thổi sáo làm kích hoạt ngay một '
                         'tràng co giật nửa mặt bên phải kéo dài 15 giây, sau cơn sức cơ mặt hai bên vẫn đối xứng '
                         'không liệt mặt.',
                         'Khám thần kinh sọ não: cảm giác da mặt 3 nhánh dây V bình thường, phản xạ giác mạc hai bên '
                         'nhạy đều, không có dấu hiệu đau mặt hay ù tai điếc tai (dây VIII bảo tồn tốt).',
                         'Bệnh nhân có tiền sử co giật mi mắt phải âm ỉ 3 năm trước nay lan xuống toàn bộ nửa mặt phải '
                         'gây khó khăn khi lái xe và đọc sách do mắt phải tự động nhắm tịt liên tục.',
                         'Trong cơn co thắt kéo dài trương lực cơ nửa mặt trái co cứng liên tục kèm các nhịp rung giật '
                         'nhanh tần số cao, không mất ý thức trong cơn (giúp loại trừ động kinh cục bộ vận động).',
                         'Khám vận động tự nhiên giữa các cơn không phát hiện khối u góc cầu tiểu não trên lâm sàng, '
                         'các dây thần kinh sọ khác từ III đến XII hoạt động bình thường.'],
    'chan_doan': 'Co thắt nửa mặt bên trái vô căn nguyên phát (nghi xung đột mạch máu - thần kinh VII).',
    'chinh': [   'các cơn co giật cơ không tự chủ xuất hiện từng đợt ở một bên mặt thường khởi phát từ cơ vòng mi mắt '
                 'dưới rồi lan dần xuống cơ gò má và khóe miệng cùng bên',
                 'cơn co thắt kéo dài vài giây đến vài chục giây làm nhắm tịt một bên mắt và kéo méo xệch khóe miệng '
                 'về bên bệnh',
                 'co giật vẫn tiếp diễn cả khi đang nghỉ ngơi hoặc trong lúc ngủ và tăng nặng rõ rệt khi căng thẳng '
                 'mệt mỏi hay nói chuyện'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chỉ định chụp cộng hưởng từ (MRI) sọ não chuỗi xung phân giải cao vùng hố sau (CISS/FIESTA) và MRA '
                'mạch máu não để phát hiện quai mạch máu (thường là động mạch tiểu não trước dưới AICA hoặc PICA) chèn '
                'ép vào vùng rễ xuất phát của dây thần kinh VII và loại trừ khối u góc cầu tiểu não.',
    'kham': 'Quan sát bệnh nhân lúc ngồi yên thấy xuất hiện các cơn co giật rung liên hồi ở mi mắt dưới bên trái rồi '
            'nhanh chóng co thắt mạnh làm mắt trái nhắm híp lại đồng thời kéo giật khóe miệng trái chếch lên trên và '
            'co cứng cơ bám da cổ trái (dấu hiệu Babinski-2: đồng thời nâng cung mày khi mắt nhắm chặt), nửa mặt phải '
            'hoàn toàn bình thường.',
    'nhom': 'người lớn',
    'phu': [   'bệnh nhân không thể tự kìm nén hay kiểm soát bằng ý chí các cơn nháy mắt giật mặt',
               'hoàn toàn không gây đau nhức dữ dội vùng mặt (khác với đau dây thần kinh V) và không tê bì mất cảm '
               'giác da mặt',
               'cơ mặt bên lành hoàn toàn bình thường không giật đối xứng (khác với co thắt mi mắt hai bên lành tính)'],
    'ten': 'co thắt nửa mặt vô căn'},
    {   'bien_the_chan_doan': [   'Run vô căn gia đình (Familial Essential Tremor) mức độ trung bình hai tay và đầu.',
                              'Bệnh run vô căn di truyền gia đình biểu hiện run tư thế và run hành động đối xứng.',
                              'Run vô căn gia đình tiến triển chậm chưa có dấu hiệu hội chứng Parkinson.',
                              'Run vô căn gia đình thể phối hợp run tay và run giọng nói.',
                              'Theo dõi run vô căn gia đình cần loại trừ run do cường giáp hoặc tác dụng phụ của '
                              'thuốc.',
                              'Run vô căn gia đình đáp ứng tốt với thuốc chẹn beta giao cảm Propranolol.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm máu kiểm tra chức năng tuyến giáp (TSH, FT4), đồng huyết thanh, '
                             'ceruloplasmin (ở người trẻ dưới 40 tuổi để loại trừ bệnh Wilson) và rà soát toàn bộ '
                             'thuốc đang dùng để loại trừ các nguyên nhân run thứ phát.',
                             'Điều trị nội khoa hàng đầu khi run gây cản trở sinh hoạt: dùng thuốc chẹn beta giao cảm '
                             'không chọn lọc Propranolol (khởi đầu 20-40mg chia 2 lần tăng dần đến liều hiệu quả, chú '
                             'ý loại trừ hen phế quản hay block nhĩ thất) hoặc thuốc chống co giật Primidone liều rất '
                             'thấp (12,5-25mg tối tăng dần).',
                             'Cân nhắc sử dụng Topiramate, Gabapentin hoặc Alprazolam hỗ trợ nếu bệnh nhân không dung '
                             'nạp hoặc chống chỉ định với Propranolol và Primidone.',
                             'Tư vấn sử dụng các dụng cụ hỗ trợ sinh hoạt thực tế như thìa dĩa cán nặng, cốc uống nước '
                             'có nắp ống hút hoặc trọng lượng đeo nhẹ cổ tay giúp giảm biên độ run khi ăn uống viết '
                             'lách, hạn chế caffein và căng thẳng.',
                             'Chuyển chuyên khoa Ngoại Thần kinh đánh giá phương pháp kích thích não sâu nhân trung '
                             'gian bụng đồi thị (VIM-DBS) hoặc sóng siêu âm hội tụ (MRgFUS) đối với các ca run vô căn '
                             'nặng kháng trị mọi thuốc uống.',
                             'Tái khám định kỳ điều chỉnh liều thuốc theo đáp ứng lâm sàng và theo dõi nhịp tim huyết '
                             'áp khi dùng Propranolol.'],
    'bien_the_kham': [   'Khi bệnh nhân thả lỏng hai tay đặt trên đùi hoàn toàn không thấy run; yêu cầu đưa thẳng hai '
                         'tay ra trước mặt xuất hiện run đều hai tay tần số khoảng 6-10 Hz, khi vẽ hình xoắn ốc '
                         'Archimedes trên giấy thấy đường nét rung lắc răng cưa đều theo một trục cố định và chữ viết '
                         'hơi to nguệch ngoạc (không bị nhỏ chữ như Parkinson).',
                         'Test ngón tay chỉ mũi và test rót nước từ cốc này sang cốc khác làm bộc lộ run hành động '
                         'biên độ vừa rõ rệt ở cả hai bàn tay, kèm run lắc nhẹ đầu theo chiều ngang (kiểu "no-no") và '
                         'giọng nói hơi rung khi kéo dài âm "a".',
                         'Khám trương lực cơ tứ chi mềm mại hoàn toàn không có dấu hiệu bánh xe răng cưa, test gõ ngón '
                         'cái-trỏ (finger tapping) và sấp ngửa bàn tay nhanh đều không chậm dần hay nhỏ dần biên độ.',
                         'Khám dáng đi bình thường vung tay hai bên tự nhiên, nghiệm pháp kéo đẩy (pull test) vững '
                         'chắc không ngã, nét mặt biểu cảm linh hoạt bình thường.',
                         'Thử nghiệm chức năng tuyến giáp trên lâm sàng bình thường (không lồi mắt, không bướu cổ, '
                         'mạch 74 l/p đều), không dùng các thuốc gây run như salbutamol hay valproate.',
                         'Bệnh nhân có bố và em gái cùng bị run tay từ năm 30 tuổi, hiện tại run hai tay ảnh hưởng chủ '
                         'yếu lúc cầm bát ăn cơm ký tên và bưng ly cà phê.'],
    'chan_doan': 'Run vô căn gia đình (Familial Essential Tremor) mức độ trung bình hai tay và đầu.',
    'chinh': [   'run hai tay đối xứng xuất hiện khi giữ tay ở một tư thế chống lại trọng lực (run tư thế) và khi thực '
                 'hiện động tác có mục đích như cầm thìa viết chữ rót nước (run hành động)',
                 'biên độ run giảm hẳn hoặc biến mất hoàn toàn khi hai tay thả lỏng nghỉ ngơi hoàn toàn trên đùi (khác '
                 'với run khi nghỉ của Parkinson)',
                 'run tiến triển chậm nhiều năm và có tiền sử nhiều người trong gia đình (cha mẹ anh chị em) bị run '
                 'tương tự'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Làm xét nghiệm máu kiểm tra chức năng tuyến giáp (TSH, FT4), đồng huyết thanh, ceruloplasmin (ở người '
                'trẻ dưới 40 tuổi để loại trừ bệnh Wilson) và rà soát toàn bộ thuốc đang dùng để loại trừ các nguyên '
                'nhân run thứ phát.',
    'kham': 'Khi bệnh nhân thả lỏng hai tay đặt trên đùi hoàn toàn không thấy run; yêu cầu đưa thẳng hai tay ra trước '
            'mặt xuất hiện run đều hai tay tần số khoảng 6-10 Hz, khi vẽ hình xoắn ốc Archimedes trên giấy thấy đường '
            'nét rung lắc răng cưa đều theo một trục cố định và chữ viết hơi to nguệch ngoạc (không bị nhỏ chữ như '
            'Parkinson).',
    'nhom': 'người lớn',
    'phu': [   'cơn run cải thiện giảm nhẹ rõ rệt sau khi uống một lượng nhỏ rượu bia rồi nặng lại khi hết tác dụng',
               'có thể kèm run lắc đầu gật gù hoặc lắc ngang ("gật đầu đồng ý" hoặc "lắc đầu từ chối") và run giọng '
               'nói rung rung',
               'hoàn toàn không có triệu chứng chậm vận động (bradykinesia), không cứng đơ bánh xe răng cưa hay mất '
               'thăng bằng dáng đi'],
    'ten': 'run vô căn gia đình'},
    {   'bien_the_chan_doan': [   'Bệnh múa giật Huntington di truyền gen trội nhiễm sắc thể thường giai đoạn toàn phát.',
                              'Hội chứng múa giật Huntington biểu hiện tam chứng rối loạn vận động tâm thần và sa sút '
                              'trí tuệ.',
                              'Theo dõi bệnh Huntington khởi phát tuổi trung niên có tiền sử gia đình rõ rệt.',
                              'Bệnh múa giật Huntington tiến triển có rối loạn vận nhãn và dấu hiệu không duy trì vận '
                              'động.',
                              'Múa giật Huntington giai đoạn vừa cần điều trị kiểm soát triệu chứng múa giật và rối '
                              'loạn hành vi.',
                              'Bệnh Huntington di truyền lặp đoạn CAG cần khẳng định bằng xét nghiệm gen HTT.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm di truyền phân tử định lượng số lần lặp lại bộ ba CAG trên gen HTT (nhiễm '
                             'sắc thể 4p16.3; >= 40 lần lặp là khẳng định chắc chắn mắc bệnh) kèm tư vấn di truyền tâm '
                             'lý chuyên sâu cho bệnh nhân và gia đình.',
                             'Chụp cộng hưởng từ (MRI) sọ não tìm dấu hiệu teo chọn lọc nhân đuôi và nhân bèo sẫm (thể '
                             'vân) gây giãn rộng sừng trán não thất bên (hình ảnh hộp não thất) và loại trừ các nguyên '
                             'nhân gây múa giật mắc phải khác.',
                             'Điều trị triệu chứng múa giật gây ảnh hưởng chức năng hoặc té ngã bằng thuốc ức chế '
                             'VMAT2 đặc hiệu (Tetrabenazine hoặc Deutetrabenazine) hoặc thuốc an thần kinh thế hệ mới '
                             'liều thấp (Risperidone, Olanzapine, Haloperidol) đặc biệt nếu kèm kích động hoang tưởng.',
                             'Điều trị rối loạn trầm cảm lo âu bằng thuốc ức chế tái hấp thu serotonin chọn lọc (SSRI '
                             'như Sertraline, Escitalopram) hoặc Mirtazapine.',
                             'Phối hợp đa chuyên khoa: âm ngữ trị liệu đánh giá chức năng nuốt phòng sặc phổi, chế độ '
                             'ăn giàu năng lượng mềm dễ nuốt chống suy kiệt, và vật lý trị liệu giữ thăng bằng an '
                             'toàn.',
                             'Hướng dẫn gia đình chăm sóc hỗ trợ, lập kế hoạch an toàn môi trường sống tránh té ngã và '
                             'kết nối các tổ chức hỗ trợ bệnh nhân bệnh lý thoái hóa thần kinh di truyền.'],
    'bien_the_kham': [   'Quan sát bệnh nhân 42 tuổi thấy liên tục có các cử động múa giật không mục đích, nhướng mày '
                         'nhăn trán, nhún vai và uốn vặn các ngón tay chân ngẫu nhiên không theo nhịp; bệnh nhân '
                         'thường cố tình biến cử động giật tay thành động tác vuốt tóc để che giấu; làm test giữ lưỡi '
                         'thè ra ngoài chỉ giữ được 4 giây rồi thụt vào (motor impersistence).',
                         'Khi yêu cầu bệnh nhân nắm chặt hai ngón tay của bác sĩ thấy lực nắm lúc siết mạnh lúc buông '
                         'lỏng liên tục không đều (dấu hiệu vắt sữa - milkmaid grip dương tính), khám vận nhãn phát '
                         'hiện liếc mắt ngang chậm chạp phải lắc đầu mới chuyển hướng nhìn được.',
                         'Đánh giá nhận thức hành vi (thang MoCA 21/30) ghi nhận suy giảm chú ý, chậm xử lý thông tin '
                         'và mất khả năng tổ chức công việc, người nhà khai bệnh nhân thay đổi tính tình hay gắt gỏng '
                         'vô cớ 2 năm nay.',
                         'Dáng đi bước rộng loạng choạng ngắt quãng với các nhịp lắc hông vung tay đột ngột bất '
                         'thường, phản xạ gân gối có hiện tượng treo lơ lửng (hung-up knee jerk reflex), trương lực cơ '
                         'hơi giảm nhẹ.',
                         'Bệnh nhân có bố ruột mất năm 55 tuổi với triệu chứng tương tự (giật tay chân mất trí nhớ), '
                         'hiện tại bệnh nhân nói hơi ngọng khó phát âm rõ và sụt 4kg trong 6 tháng qua.',
                         'Không có rối loạn cảm giác hay dấu hiệu tổn thương bó tháp rõ rệt, không thấy vòng '
                         'Kayser-Fleischer ở rìa giác mạc (giúp loại trừ bệnh Wilson).'],
    'chan_doan': 'Bệnh múa giật Huntington di truyền gen trội nhiễm sắc thể thường giai đoạn toàn phát.',
    'chinh': [   'các động tác múa giật (chorea) bất thường nhanh ngắt quãng không tự chủ giống như nhảy múa chảy mượt '
                 'từ vùng cơ này sang vùng cơ khác ở mặt đầu vai và ngón tay chân',
                 'rối loạn tâm thần và tính cách tiến triển như dễ cáu gắt bùng nổ trầm cảm mất kiểm soát hành vi hoặc '
                 'hoang tưởng',
                 'suy giảm nhận thức sa sút trí tuệ tiến triển dần về trí nhớ điều hành lập kế hoạch và tiền sử gia '
                 'đình có bố hoặc mẹ mắc bệnh tương tự'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Làm xét nghiệm di truyền phân tử định lượng số lần lặp lại bộ ba CAG trên gen HTT (nhiễm sắc thể '
                '4p16.3; >= 40 lần lặp là khẳng định chắc chắn mắc bệnh) kèm tư vấn di truyền tâm lý chuyên sâu cho '
                'bệnh nhân và gia đình.',
    'kham': 'Quan sát bệnh nhân 42 tuổi thấy liên tục có các cử động múa giật không mục đích, nhướng mày nhăn trán, '
            'nhún vai và uốn vặn các ngón tay chân ngẫu nhiên không theo nhịp; bệnh nhân thường cố tình biến cử động '
            'giật tay thành động tác vuốt tóc để che giấu; làm test giữ lưỡi thè ra ngoài chỉ giữ được 4 giây rồi thụt '
            'vào (motor impersistence).',
    'nhom': 'người lớn',
    'phu': [   'dấu hiệu lưỡi thằn lằn (không thể giữ lưỡi thè ra ngoài giữ yên quá 10 giây) và dấu hiệu vắt sữa khi '
               'nắm tay bác sĩ (lực bóp siết chặt rồi thả lỏng liên hồi)',
               'dáng đi loạng choạng khua khoắng bất thường dễ té ngã ở giai đoạn giữa và muộn',
               'rối loạn vận nhãn khó khởi phát động tác liếc mắt nhanh (saccades chậm) và nuốt nghẹn sụt cân dần'],
    'ten': 'múa giật Huntington'},
    {   'bien_the_chan_doan': [   'Bệnh rỗng tủy sống cổ (Syringomyelia) điển hình với hội chứng phân ly cảm giác kiểu áo '
                              'choàng.',
                              'Bệnh rỗng tủy cổ ngực nghi ngờ phối hợp dị tật Arnold-Chiari typ 1.',
                              'Bệnh rỗng tủy sống cổ gây teo cơ bàn tay hai bên và sẹo bỏng không đau.',
                              'Bệnh rỗng tủy sống cổ thứ phát muộn sau chấn thương cột sống cổ cũ.',
                              'Rỗng tủy cổ C4-T1 có hội chứng Horner và tăng phản xạ tháp hai chi dưới.',
                              'Bệnh rỗng tủy sống cổ tiến triển chậm cần phẫu thuật giải ép dẫn lưu nang tủy.'],
    'bien_the_ke_hoach': [   'Chỉ định chụp cộng hưởng từ (MRI) toàn bộ cột sống cổ ngực và vùng bản lề chẩm cổ (có '
                             'tiêm thuốc đối quang từ Gadolinium) để thấy rõ kích thước chiều dài khoang nang chứa '
                             'dịch bên trong ống tủy, phát hiện dị tật Chiari typ 1 (hạnh nhân tiểu não tụt qua lỗ '
                             'chẩm) hoặc khối u nội tủy đi kèm.',
                             'Hội chẩn chuyên khoa Ngoại Thần kinh cột sống đánh giá chỉ định phẫu thuật: phẫu thuật '
                             'giải ép hố sau mở rộng lỗ chẩm và tạo hình màng cứng (nếu do Chiari typ 1) hoặc đặt ống '
                             'thông dẫn lưu nang rỗng tủy vào khoang dưới nhện/khoang màng phổi nếu triệu chứng thần '
                             'kinh tiến triển nặng.',
                             'Nếu nang tủy nhỏ ổn định không tiến triển: theo dõi sát lâm sàng và chụp MRI kiểm tra '
                             'định kỳ mỗi 6-12 tháng.',
                             'Giáo dục bảo vệ an toàn cực kỳ quan trọng cho bệnh nhân: luôn thử nhiệt độ nước tắm và '
                             'thức ăn bằng chân hoặc nhờ người thân kiểm tra, đeo găng tay bảo vệ khi nấu nướng cầm '
                             'nắm vật sắc nhọn, chăm sóc kỹ vết thương nhỏ bàn tay tránh nhiễm trùng hoại tử không hay '
                             'biết.',
                             'Điều trị giảm đau thần kinh vùng cổ vai bằng Gabapentin hoặc Pregabalin nếu có đau rát '
                             'trung tâm, và tuyệt đối tránh các động tác rặn mạnh nâng tạ nặng hay nắn bẻ cột sống cổ.',
                             'Tập vật lý trị liệu duy trì tầm vận động bàn tay khớp vai và bảo tồn lực cơ còn lại.'],
    'bien_the_kham': [   'Thử cảm giác trên hai tay và phần ngực trên: bệnh nhân hoàn toàn không nhận biết được cảm '
                         'giác đau khi châm kim đầu nhọn và không phân biệt được ống nghiệm nước nóng lạnh (45°C và '
                         '10°C) ở vùng cổ vai cánh tay hai bên phân bố dạng áo khoác (cape-like distribution), nhưng '
                         'vẫn cảm nhận chính xác sờ nhẹ bằng bông gòn và cảm giác rung âm thoa (phân ly cảm giác kinh '
                         'điển).',
                         'Quan sát hai bàn tay thấy có nhiều vết sẹo bỏng cũ và vết thương đã liền ở đầu ngón tay và '
                         'cẳng tay mà bệnh nhân không nhớ bị lúc nào, kèm teo rõ rệt các cơ gian cốt mu tay và cơ mô '
                         'cái mô út hai bên, mất phản xạ gân cơ nhị đầu và cơ tam đầu hai tay.',
                         'Khám chi dưới thấy dấu hiệu tháp nhẹ do nang tủy chèn ép bó tháp đi xuống: phản xạ gân gối '
                         'hai bên tăng nhạy lan tỏa, dấu Babinski dương tính nhẹ bên phải, trương lực cơ hai chân tăng '
                         'nhẹ nhưng sức cơ chân còn 4+/5.',
                         'Khám mắt phát hiện hội chứng Horner nhẹ bên trái (sụp mi nhẹ 1,5mm và đồng tử co nhỏ hơn bên '
                         'phải) do nang rỗng tủy cổ C8-T1 tổn thương trung tâm tủy giao cảm (trung khu Budge).',
                         'Bệnh nhân có cột sống ngực hơi vẹo nhẹ sang phải kèm cổ ngắn, đau vùng chẩm gáy mỗi khi ho '
                         'mạnh hoặc rặn đi vệ sinh (gợi ý phối hợp thoát vị hạnh nhân tiểu não Chiari loại I).',
                         'Sức cơ ngọn chi hai tay giảm còn 3+/5, rung giật bó cơ thưa thớt ở cẳng tay, hoàn toàn không '
                         'có rối loạn cảm giác ở mặt (hoặc chỉ mất cảm giác đau nhiệt vùng quanh mặt ngoài kiểu củ '
                         'hành nếu nang lan lên hành tủy).'],
    'chan_doan': 'Bệnh rỗng tủy sống cổ (Syringomyelia) điển hình với hội chứng phân ly cảm giác kiểu áo choàng.',
    'chinh': [   'mất cảm giác đau và nhiệt độ (nóng lạnh) phân bố kiểu áo choàng khoác hai vai cánh tay và ngực trên '
                 'trong khi cảm giác sờ chạm nhẹ và rung âm thoa vẫn còn nguyên vẹn (phân ly cảm giác)',
                 'bệnh nhân thường bị bỏng da tay khi cầm nồi nóng hoặc tàn thuốc lá, bị vết thương đứt tay mà hoàn '
                 'toàn không cảm thấy đau đớn',
                 'teo cơ và yếu dần các cơ nhỏ bàn tay hai bên (cơ mô cái mô út cơ gian cốt) tiến triển chậm tạo bàn '
                 'tay vuốt khỉ'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chỉ định chụp cộng hưởng từ (MRI) toàn bộ cột sống cổ ngực và vùng bản lề chẩm cổ (có tiêm thuốc đối '
                'quang từ Gadolinium) để thấy rõ kích thước chiều dài khoang nang chứa dịch bên trong ống tủy, phát '
                'hiện dị tật Chiari typ 1 (hạnh nhân tiểu não tụt qua lỗ chẩm) hoặc khối u nội tủy đi kèm.',
    'kham': 'Thử cảm giác trên hai tay và phần ngực trên: bệnh nhân hoàn toàn không nhận biết được cảm giác đau khi '
            'châm kim đầu nhọn và không phân biệt được ống nghiệm nước nóng lạnh (45°C và 10°C) ở vùng cổ vai cánh tay '
            'hai bên phân bố dạng áo khoác (cape-like distribution), nhưng vẫn cảm nhận chính xác sờ nhẹ bằng bông gòn '
            'và cảm giác rung âm thoa (phân ly cảm giác kinh điển).',
    'nhom': 'người lớn',
    'phu': [   'giảm hoặc mất phản xạ gân cơ nhị đầu và trâm quay ở hai tay trong khi phản xạ gân gối ở hai chân lại '
               'tăng nhẹ (liệt cứng hai chân nhẹ)',
               'đau nhức âm ỉ vùng cổ gáy lan xuống hai vai tăng lên khi ho rặn hắt hơi (nếu có dị tật Chiari type 1 '
               'đi kèm)',
               'vẹo cột sống ngực lưng hoặc xuất hiện khớp thần kinh Charcot ở khớp vai khuỷu tay không đau'],
    'ten': 'bệnh rỗng tủy sống cổ'},
    {   'bien_the_chan_doan': [   'Hội chứng Guillain-Barre thể nhẹ (AIDP) đang trong giai đoạn phục hồi chức năng tốt.',
                              'Di chứng phục hồi bán phần sau hội chứng Guillain-Barre mức độ nhẹ tuần thứ 6.',
                              'Hội chứng Guillain-Barre giai đoạn lui bệnh còn giảm phản xạ gân xương và tê nhẹ ngọn '
                              'chi.',
                              'Hội chứng Guillain-Barre thể nhẹ phục hồi ổn định không cần thông khí hỗ trợ.',
                              'Giai đoạn phục hồi hội chứng Guillain-Barre cần duy trì vật lý trị liệu tránh mệt quá '
                              'sức.',
                              'Hội chứng viêm đa rễ dây thần kinh cấp Guillain-Barre thể nhẹ đang hồi phục hoàn toàn.'],
    'bien_the_ke_hoach': [   'Tiếp tục chương trình phục hồi chức năng vận động chuyên sâu từng bước: tập thăng bằng '
                             'đứng đi, tăng sức bền cơ tứ đầu đùi và cơ chày trước nhưng phân bổ quãng nghỉ hợp lý '
                             'tránh tập quá tải gây kiệt sức cơ đang tái tạo myelin.',
                             'Theo dõi sát diễn tiến sức cơ và cảm giác mỗi 2-4 tuần (lưu ý nếu sức cơ đột ngột yếu '
                             'trở lại hoặc kéo dài quá 8 tuần cần đánh giá lại để loại trừ chuyển thể viêm đa dây thần '
                             'kinh mạn tính CIDP).',
                             'Điều trị triệu chứng đau mỏi cơ hoặc dị cảm tê buốt chân tay giai đoạn phục hồi bằng '
                             'Gabapentin hoặc Pregabalin liều thấp.',
                             'Bổ sung Vitamin nhóm B (B1, B6, Methylcobalamin B12) và chế độ dinh dưỡng giàu đạm hỗ '
                             'trợ quá trình tái myelin hóa sợi thần kinh ngoại biên.',
                             'Tư vấn lịch tiêm chủng an toàn trong tương lai: khuyến cáo thận trọng theo dõi và tham '
                             'khảo ý kiến bác sĩ thần kinh trước khi tiêm các loại vắc xin (đặc biệt vắc xin cúm) '
                             'trong vòng 1 năm đầu sau bệnh.',
                             'Động viên tâm lý bệnh nhân yên tâm vì tiên lượng hội chứng Guillain-Barre thể nhẹ có tỷ '
                             'lệ hồi phục hoàn toàn trên 85-90% trong 6-12 tháng.'],
    'bien_the_kham': [   'Bệnh nhân hồi phục tuần thứ 5 sau khởi phát hội chứng Guillain-Barre thể hủy myelin (AIDP) '
                         'mức độ nhẹ: sức cơ gốc chi hai chân đã tăng từ 3/5 lên 4+/5, sức cơ bàn tay đạt 4+/5, tự '
                         'đứng vững được và đi lại trong phòng không cần nâng đỡ, phản xạ gân gối và gân gót hai bên '
                         'vẫn còn giảm sâu (1+).',
                         'Khám thần kinh ghi nhận tình trạng yếu nhẹ hai bàn chân (4/5) khiến dáng đi hơi chậm và mệt '
                         'sau 50 mét, còn cảm giác tê râm ran nhẹ kiểu đi tất ở hai bàn chân nhưng cảm giác rung âm '
                         'thoa và tư thế khớp đã phục hồi tốt.',
                         'Bệnh nhân không còn liệt mặt hai bên, nói rõ ràng, nuốt tốt hoàn toàn không sặc, dung tích '
                         'sống hô hấp ổn định, nhịp tim đều 78 l/p huyết áp 118/74 mmHg ổn định không dao động.',
                         'Không có teo cơ nặng hay loét tỳ đè, không còn đau rễ thần kinh cấp tính vùng thắt lưng, chỉ '
                         'còn cảm giác nhức mỏi bắp chân nhẹ sau khi tập vật lý trị liệu.',
                         'Đánh giá thang điểm khuyết tật GBS Hughes hiện ở mức 2 điểm (có thể đi bộ trên 10m độc lập '
                         'nhưng chưa chạy được), tiến triển hồi phục thuận lợi qua từng tuần.',
                         'Khám cơ tròn kiểm soát tiểu tiện đại tiện hoàn toàn bình thường, phản xạ da lòng bàn chân '
                         'đáp ứng gấp bình thường.'],
    'chan_doan': 'Hội chứng Guillain-Barre thể nhẹ (AIDP) đang trong giai đoạn phục hồi chức năng tốt.',
    'chinh': [   'tiền sử yếu liệt đối xứng hai chân lan dần lên tay kèm tê bì châm chích đầu ngón chân tay sau đợt '
                 'nhiễm trùng hô hấp hoặc tiêu chảy trước đó',
                 'hiện tại đang trong giai đoạn phục hồi dần sức cơ từ ngọn chi hoặc gốc chi cải thiện rõ so với lúc '
                 'đỉnh bệnh',
                 'vẫn còn giảm hoặc mất phản xạ gân xương tứ chi và cảm giác tê râm ran nhẹ ở bàn chân bàn tay'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Tiếp tục chương trình phục hồi chức năng vận động chuyên sâu từng bước: tập thăng bằng đứng đi, tăng '
                'sức bền cơ tứ đầu đùi và cơ chày trước nhưng phân bổ quãng nghỉ hợp lý tránh tập quá tải gây kiệt sức '
                'cơ đang tái tạo myelin.',
    'kham': 'Bệnh nhân hồi phục tuần thứ 5 sau khởi phát hội chứng Guillain-Barre thể hủy myelin (AIDP) mức độ nhẹ: '
            'sức cơ gốc chi hai chân đã tăng từ 3/5 lên 4+/5, sức cơ bàn tay đạt 4+/5, tự đứng vững được và đi lại '
            'trong phòng không cần nâng đỡ, phản xạ gân gối và gân gót hai bên vẫn còn giảm sâu (1+).',
    'nhom': 'người lớn',
    'phu': [   'không có suy hô hấp khó nuốt hay rối loạn thần kinh thực vật huyết áp nhịp tim nguy hiểm',
               'bệnh nhân đã tự đứng dậy đi lại được có người dìu hoặc khung tập đi nhưng còn mệt nhanh khi đi xa',
               'đau mỏi nhức cơ bắp chân lưng nhẹ về đêm trong giai đoạn tái tạo thần kinh'],
    'ten': 'hội chứng Guillain-Barre thể nhẹ phục hồi'},
    {   'bien_the_chan_doan': [   'Đau dây thần kinh thiệt hầu (dây IX) vô căn nguyên phát bên phải.',
                              'Đau dây thần kinh thiệt hầu bên trái thể kịch phát có dấu hiệu tiền ngất do kích thích '
                              'phế vị.',
                              'Đau dây thần kinh thiệt hầu mạn tính nghi do xung đột mạch máu - thần kinh tại hố sau.',
                              'Theo dõi đau dây thần kinh thiệt hầu cần loại trừ u vùng hầu họng hoặc hội chứng Eagle '
                              '(mỏm trâm dài).',
                              'Đau dây thần kinh thiệt hầu mức độ nặng gây sợ nuốt và sụt cân.',
                              'Đau dây thần kinh số IX kịch phát đáp ứng tốt với điều trị Carbamazepine.'],
    'bien_the_ke_hoach': [   'Bắt buộc chỉ định nội soi tai mũi họng kỹ lưỡng vùng vòm mũi họng, hạ họng và đáy lưỡi '
                             'để loại trừ ung thư vòm hầu hoặc khối u vùng amidan; chụp MRI sọ não chuỗi xung hố sau '
                             '(CISS/FIESTA) và MRA mạch máu não tìm xung đột quai động mạch (PICA hoặc động mạch đốt '
                             'sống) chèn ép rễ dây IX-X; chụp CT cổ nếu nghi ngờ hội chứng Eagle (vôi hóa dài mỏm '
                             'trâm).',
                             'Làm điện tâm đồ (ECG) hoặc đeo Holter điện tim 24 giờ nếu bệnh nhân có tiền sử chóng mặt '
                             'ngất xỉu trong cơn đau để tầm soát block nhĩ thất hoặc ngừng xoang phản xạ qua trung '
                             'gian dây phế vị.',
                             'Điều trị nội khoa hàng đầu bằng thuốc ổn định kênh natri chống đau thần kinh: '
                             'Carbamazepine (khởi đầu 100mg ngày 2 lần tăng dần theo đáp ứng và theo dõi công thức máu '
                             'men gan natri máu) hoặc Oxcarbazepine (dung nạp tốt hơn).',
                             'Phối hợp hoặc thay thế bằng Gabapentin, Pregabalin hoặc Baclofen nếu không dung nạp '
                             'Carbamazepine hay cơn đau chưa kiểm soát hoàn toàn.',
                             'Hướng dẫn bệnh nhân ăn thức ăn mềm nguội vừa phải, tránh đồ ăn quá nóng lạnh chua cay '
                             'kích thích vùng hầu họng; đảm bảo cung cấp đủ nước dinh dưỡng.',
                             'Hội chẩn Ngoại Thần kinh xem xét phẫu thuật giải ép vi mạch (MVD) rễ dây IX (và phần rễ '
                             'trên dây X nếu cần) tại hố sau khi bệnh nhân kháng trị với liều tối đa thuốc uống.'],
    'bien_the_kham': [   'Khám vùng hầu họng và tai bên phải không thấy sưng đỏ, amidan không có mủ hay khối u sùi, '
                         'màng nhĩ hai bên sáng bóng bình thường; nhưng khi bác sĩ chạm nhẹ đầu que bông vào vùng trụ '
                         'amidan và đáy lưỡi bên phải lập tức kích hoạt cơn đau giật dữ dội như điện giật lan từ họng '
                         'lên sâu trong tai phải khiến bệnh nhân ôm cổ nhăn mặt suốt 30 giây.',
                         'Bệnh nhân có thể trạng gầy sút nhẹ do sợ nuốt thức ăn, giữ cốc nước không dám uống, dùng '
                         'thuốc tê Xylocaine 10% xịt tại chỗ vào vùng họng amidan bên trái giúp cắt cơn đau tạm thời '
                         'trong 30 phút (test chẩn đoán hữu ích).',
                         'Khám thần kinh sọ não: màn hầu nâng cân xứng, phản xạ nôn (gag reflex) hai bên còn nhạy '
                         '(nhưng chạm bên đau gây bùng phát cơn đau), cảm giác mặt vùng dây V hoàn toàn bình thường '
                         'không có điểm đau kích hoạt trên da mặt.',
                         'Đo nhịp tim và huyết áp ngoài cơn bình thường 72 l/p 120/75 mmHg, bệnh nhân khai có 2 lần '
                         'cảm thấy choáng váng tối sầm mặt mũi ngay đỉnh cơn đau họng dữ dội tuần trước.',
                         'Bệnh nhân 58 tuổi đau kịch phát vùng đáy lưỡi bên trái lan góc hàm và ống tai ngoài trái lặp '
                         'lại 15-20 cơn mỗi ngày suốt 3 tháng nay, sờ vùng cổ dưới góc hàm không thấy hạch to hay mỏm '
                         'trâm dài bất thường.',
                         'Soi thanh quản gián tiếp và nội soi vòm mũi họng sạch hoàn toàn không phát hiện ung thư vòm '
                         'hay u hạch vùng hầu họng chèn ép.'],
    'chan_doan': 'Đau dây thần kinh thiệt hầu (dây IX) vô căn nguyên phát bên phải.',
    'chinh': [   'các cơn đau chói dữ dội như dao đâm hoặc điện giật kéo dài vài giây đến dưới 2 phút khu trú ở vùng '
                 'đáy lưỡi, hố amidan, thành sau họng và lan sâu vào trong ống tai một bên',
                 'cơn đau bị kích phát đột ngột mỗi khi nuốt nước bọt, nuốt thức ăn lạnh, nhai, ho, ngáp hoặc nói '
                 'chuyện to',
                 'bệnh nhân sợ ăn uống nuốt nước bọt dẫn đến sụt cân gầy sút hoặc phải nghiêng đầu giữ im miệng khi '
                 'cơn đau ập đến'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Bắt buộc chỉ định nội soi tai mũi họng kỹ lưỡng vùng vòm mũi họng, hạ họng và đáy lưỡi để loại trừ '
                'ung thư vòm hầu hoặc khối u vùng amidan; chụp MRI sọ não chuỗi xung hố sau (CISS/FIESTA) và MRA mạch '
                'máu não tìm xung đột quai động mạch (PICA hoặc động mạch đốt sống) chèn ép rễ dây IX-X; chụp CT cổ '
                'nếu nghi ngờ hội chứng Eagle (vôi hóa dài mỏm trâm).',
    'kham': 'Khám vùng hầu họng và tai bên phải không thấy sưng đỏ, amidan không có mủ hay khối u sùi, màng nhĩ hai '
            'bên sáng bóng bình thường; nhưng khi bác sĩ chạm nhẹ đầu que bông vào vùng trụ amidan và đáy lưỡi bên '
            'phải lập tức kích hoạt cơn đau giật dữ dội như điện giật lan từ họng lên sâu trong tai phải khiến bệnh '
            'nhân ôm cổ nhăn mặt suốt 30 giây.',
    'nhom': 'người lớn',
    'phu': [   'một số trường hợp nặng cơn đau có thể kích thích dây thần kinh X gây nhịp tim chậm tụt huyết áp thậm '
               'chí ngất xỉu thoáng qua trong cơn đau',
               'giữa các cơn đau vùng họng và tai hoàn toàn bình thường không đau âm ỉ và soi tai mũi họng không thấy '
               'tổn thương viêm loét hay khối u',
               'đáp ứng kém với thuốc giảm đau thông thường nhưng cải thiện với thuốc chống động kinh nhóm ổn định '
               'màng tế bào'],
    'ten': 'đau dây thần kinh thiệt hầu'},
    {   'bien_the_chan_doan': [   'Viêm đa rễ dây thần kinh hủy myelin mạn tính (CIDP) thể điển hình.',
                              'Bệnh lý viêm đa rễ dây thần kinh mạn tính CIDP tiến triển tăng dần trên 8 tuần.',
                              'Viêm đa rễ dây thần kinh mạn tính CIDP giai đoạn tái phát sau giảm liều corticoid.',
                              'CIDP thể điển hình biểu hiện yếu gốc chi ngọn chi đối xứng và thất điều cảm giác.',
                              'Theo dõi CIDP cần phân biệt với bệnh thần kinh đái tháo đường và bệnh lý đơn dòng IgM.',
                              'Viêm đa rễ dây thần kinh mạn tính CIDP có chỉ định chọc dịch não tủy và điện cơ đồ.'],
    'bien_the_ke_hoach': [   'Chỉ định đo điện cơ đồ và tốc độ dẫn truyền thần kinh (NCS/EMG) đa dây thần kinh tìm '
                             'bằng chứng hủy myelin nguyên phát đặc trưng (giảm mạnh tốc độ dẫn truyền vận động, kéo '
                             'dài thời gian tiềm ngoại vi, block dẫn truyền một phần hoặc phân tán thời khoảng, kéo '
                             'dài sóng F) theo tiêu chuẩn chẩn đoán EAN/PNS.',
                             'Chọc dò dịch não tủy tìm hình ảnh phân ly đạm - tế bào điển hình (protein dịch não tủy '
                             'tăng cao > 0,45 g/L trong khi số lượng bạch cầu bình thường < 10 tế bào/mm3).',
                             'Làm xét nghiệm máu loại trừ các nguyên nhân bắt chước CIDP như điện di đạm huyết thanh '
                             'và cố định miễn dịch tìm protein đơn dòng (POEMS, MGUS), HbA1c, Vitamin B12, chức năng '
                             'tuyến giáp, HIV và kháng thể nốt Ranvier (anti-NF155, anti-CNTN1) nếu kháng trị.',
                             'Khởi đầu điều trị đặc hiệu bằng liệu pháp miễn dịch hàng đầu: truyền tĩnh mạch '
                             'Immunoglobulin (IVIG liều tấn công 2 g/kg chia 2-5 ngày rồi duy trì mỗi 3-4 tuần) HOẶC '
                             'Corticosteroid đường uống/tĩnh mạch (Prednisolone 1 mg/kg/ngày hoặc Methylprednisolone '
                             'xung).',
                             'Xem xét phối hợp thuốc ức chế miễn dịch tiết kiệm corticoid (Azathioprine, Mycophenolate '
                             'mofetil hoặc Methotrexate) hoặc thay huyết tương (PLEX) đối với các trường hợp nặng hoặc '
                             'đáp ứng kém với IVIG/Steroid.',
                             'Phối hợp tập vật lý trị liệu phục hồi sức cơ, tập thăng bằng chống té ngã và theo dõi '
                             'định kỳ thang điểm INCAT để điều chỉnh phác đồ duy trì lâu dài.'],
    'bien_the_kham': [   'Khám vận động tứ chi cho thấy yếu đối xứng cả nhóm cơ gốc chi (gấp háng, giạng vai sức cơ '
                         '3+/5) và nhóm cơ ngọn chi (gấp mu bàn chân, nắm tay 3/5), hoàn toàn mất phản xạ gân xương ở '
                         'cả 4 chi, khám cảm giác phát hiện mất cảm giác rung âm thoa tại mắt cá chân và ngón chân cái '
                         'hai bên kèm dấu hiệu Romberg dương tính rõ.',
                         'Bệnh nhân 52 tuổi khai tình trạng yếu hai chân tê hai tay tiến triển nặng dần trong suốt 4 '
                         'tháng nay (đã phải chống gậy khi đi lại), sức cơ ngọn chi và gốc chi giảm đều hai bên, không '
                         'có teo cơ bắp chân nặng hay rung giật bó cơ, cơ tròn tiêu tiểu bình thường.',
                         'Dáng đi thất điều cảm giác (sensory ataxia): bước đi chân đập mạnh xuống sàn và nhìn xuống '
                         'đất để giữ thăng bằng, nhắm mắt lại là loạng choạng ngã ngay; sờ dây thần kinh trụ ở khuỷu '
                         'tay hơi dày nhẹ.',
                         'Không có rối loạn chức năng dây sọ hay khó thở, nhưng lực kẹp tay và lực đứng dậy khỏi ghế '
                         'giảm rõ rệt so với 2 tháng trước, bệnh diễn tiến liên tục vượt mốc 8 tuần.',
                         'Khám thần kinh không phát hiện dấu hiệu tháp (Babinski âm tính, không tăng trương lực cơ), '
                         'không có ranh giới mất cảm giác theo khoanh tủy (loại trừ chèn ép tủy sống).',
                         'Thử nghiệm rung âm thoa 128Hz tại khớp đốt ngón chân và đầu gối giảm mất rõ, bệnh nhân có '
                         'cảm giác đi trên bông gòn dưới hai lòng bàn chân kèm yếu cơ hai tay hai chân mạn tính.'],
    'chan_doan': 'Viêm đa rễ dây thần kinh hủy myelin mạn tính (CIDP) thể điển hình.',
    'chinh': [   'yếu cơ đối xứng cả gốc chi lẫn ngọn chi ở hai tay và hai chân tiến triển từ từ kéo dài liên tục trên '
                 '8 tuần (hoặc từng đợt tái phát nặng dần)',
                 'tê bì giảm cảm giác sâu rung âm thoa và cảm giác tư thế khớp ở hai bàn chân bàn tay gây dáng đi mất '
                 'vững loạng choạng khi nhắm mắt (dấu hiệu Romberg dương tính)',
                 'mất hoàn toàn phản xạ gân xương tứ chi (gân gối, gân gót, nhị đầu, tam đầu) đối xứng hai bên'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chỉ định đo điện cơ đồ và tốc độ dẫn truyền thần kinh (NCS/EMG) đa dây thần kinh tìm bằng chứng hủy '
                'myelin nguyên phát đặc trưng (giảm mạnh tốc độ dẫn truyền vận động, kéo dài thời gian tiềm ngoại vi, '
                'block dẫn truyền một phần hoặc phân tán thời khoảng, kéo dài sóng F) theo tiêu chuẩn chẩn đoán '
                'EAN/PNS.',
    'kham': 'Khám vận động tứ chi cho thấy yếu đối xứng cả nhóm cơ gốc chi (gấp háng, giạng vai sức cơ 3+/5) và nhóm '
            'cơ ngọn chi (gấp mu bàn chân, nắm tay 3/5), hoàn toàn mất phản xạ gân xương ở cả 4 chi, khám cảm giác '
            'phát hiện mất cảm giác rung âm thoa tại mắt cá chân và ngón chân cái hai bên kèm dấu hiệu Romberg dương '
            'tính rõ.',
    'nhom': 'người lớn',
    'phu': [   'yếu cả các động tác nâng vai đứng lên từ ghế (gốc chi) lẫn cài cúc áo nhấc mũi chân (ngọn chi)',
               'diễn biến mạn tính kéo dài trên 2 tháng giúp phân biệt với hội chứng Guillain-Barre cấp tính (< 4 '
               'tuần)',
               'hiếm khi gây liệt hô hấp cấp nhưng gây tàn phế đi lại tăng dần nếu không điều trị miễn dịch'],
    'ten': 'viêm đa rễ dây thần kinh mạn tính CIDP'},
    {   'bien_the_chan_doan': [   'Bệnh cơ viêm đa cơ tự miễn (Polymyositis) giai đoạn tiến triển có yếu cơ gốc chi đối '
                              'xứng.',
                              'Viêm đa cơ tự miễn không kèm tổn thương da mức độ trung bình.',
                              'Bệnh cơ viêm đa cơ tự miễn có biểu hiện yếu cơ gấp cổ và khó nuốt vùng hầu họng.',
                              'Theo dõi viêm đa cơ tự miễn nghi ngờ kèm tổn thương phổi kẽ (hội chứng kháng '
                              'synthetase).',
                              'Viêm đa cơ tự miễn ở người trưởng thành cần sinh thiết cơ loại trừ viêm cơ thể vùi.',
                              'Bệnh cơ viêm đa cơ tự miễn đáp ứng tốt với liệu pháp Corticoid liều cao.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm máu đo men cơ Creatine Kinase (CK), Aldolase, AST, ALT, LDH (thường tăng '
                             'rất cao), bộ kháng thể đặc hiệu viêm cơ (anti-Jo-1, anti-SRP, anti-Mi-2) và tầm soát '
                             'bilan viêm CRP, tốc độ máu lắng.',
                             'Chỉ định đo điện cơ đồ kim (Needle EMG) tìm tam chứng bệnh cơ điển hình (điện thế tự '
                             'phát tăng hoạt động đâm kim, rung sợi cơ, đơn vị vận động biên độ thấp thời khoảng ngắn '
                             'đa pha) và chụp MRI cơ đùi hai bên định vị vùng cơ viêm phù nề để chỉ định sinh thiết '
                             'cơ.',
                             'Thực hiện sinh thiết cơ (thường ở cơ đùi hoặc cơ delta đối bên nơi làm EMG) làm giải '
                             'phẫu bệnh khẳng định thâm nhiễm tế bào lympho T CD8+ xâm nhập sợi cơ lành và loại trừ '
                             'viêm cơ thể vùi hoặc loạn dưỡng cơ.',
                             'Chụp cắt lớp vi tính lồng ngực độ phân giải cao (HRCT) và đo chức năng hô hấp tầm soát '
                             'bệnh phổi kẽ đi kèm; siêu âm tim và điện tâm đồ tầm soát viêm cơ tim.',
                             'Khởi đầu điều trị bằng Corticosteroid liều cao (Prednisolone 1 mg/kg/ngày hoặc '
                             'Methylprednisolone truyền tĩnh mạch 500-1000mg x 3 ngày nếu khó nuốt nặng), đồng thời '
                             'phối hợp sớm thuốc ức chế miễn dịch tiết kiệm steroid như Methotrexate hoặc '
                             'Azathioprine.',
                             'Phối hợp tập vật lý trị liệu nhẹ nhàng thụ động trong giai đoạn men cơ còn rất cao rồi '
                             'tăng dần tập chủ động khi men cơ giảm, kèm theo dõi đường huyết huyết áp và dự phòng '
                             'loãng xương.'],
    'bien_the_kham': [   'Khám vận động ghi nhận yếu cơ gốc chi đối xứng rõ rệt: sức cơ tứ đầu đùi và thắt lưng chậu '
                         '3/5, cơ delta và đai vai 3+/5, bệnh nhân phải vịn tay vào thành ghế mới đứng dậy được; sức '
                         'cơ bàn tay và bàn chân vẫn đạt 5/5, cơ gấp cổ yếu 3+/5, hoàn toàn không có ban đỏ ngoài da.',
                         'Bệnh nhân nữ 45 tuổi than yếu mỏi hai đùi và hai vai tăng dần 2 tháng nay kèm nuốt hơi nghẹn '
                         'khi ăn cơm khô; khám cảm giác nông sâu tứ chi bình thường, phản xạ gân gối còn bảo tồn 2+, '
                         'bóp nắn cơ bắp đùi hơi đau tức nhẹ.',
                         'Thử nghiệm nâng đầu khỏi gối ở tư thế nằm ngửa không giữ được quá 5 giây, không có teo cơ '
                         'nặng hay rung giật bó cơ, nghe đáy phổi hai bên có ít ran nổ mịn gợi ý bệnh phổi kẽ đi kèm.',
                         'Khám da toàn thân bình thường không có sẩn Gottron ở khớp ngón tay hay ban tím vùng mi mắt '
                         '(loại trừ viêm da cơ), sức cơ hai bên đối xứng kiểu đai vai đai chậu.',
                         'Bệnh nhân không tự trèo lên giường khám được mà cần trợ giúp nâng hai chân, khi ngồi xổm '
                         'xuống không tự đứng lên nổi nếu không chống hai tay lên đùi (dấu hiệu đứng dậy kiểu trèo '
                         'trên thân mình).',
                         'Nhịp tim đều 82 l/p, không có dấu hiệu tổn thương dây thần kinh sọ vận nhãn (không sụp mi '
                         'hay nhìn đôi giúp phân biệt với nhược cơ).'],
    'chan_doan': 'Bệnh cơ viêm đa cơ tự miễn (Polymyositis) giai đoạn tiến triển có yếu cơ gốc chi đối xứng.',
    'chinh': [   'yếu cơ gốc chi đối xứng hai bên tiến triển bán cấp trong vài tuần đến vài tháng (khó đứng lên từ ghế '
                 'thấp, khó bước lên bậc thang hoặc giơ tay chải đầu)',
                 'yếu cơ gấp cổ khiến khó nhấc đầu khỏi gối khi nằm ngửa và có thể kèm nuốt nghẹn sặc vùng hầu họng',
                 'hoàn toàn không có tổn thương phát ban da đặc hiệu vùng mặt hay mu bàn tay (khác với viêm da cơ)'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Làm xét nghiệm máu đo men cơ Creatine Kinase (CK), Aldolase, AST, ALT, LDH (thường tăng rất cao), bộ '
                'kháng thể đặc hiệu viêm cơ (anti-Jo-1, anti-SRP, anti-Mi-2) và tầm soát bilan viêm CRP, tốc độ máu '
                'lắng.',
    'kham': 'Khám vận động ghi nhận yếu cơ gốc chi đối xứng rõ rệt: sức cơ tứ đầu đùi và thắt lưng chậu 3/5, cơ delta '
            'và đai vai 3+/5, bệnh nhân phải vịn tay vào thành ghế mới đứng dậy được; sức cơ bàn tay và bàn chân vẫn '
            'đạt 5/5, cơ gấp cổ yếu 3+/5, hoàn toàn không có ban đỏ ngoài da.',
    'nhom': 'người lớn',
    'phu': [   'cơ vùng đùi và vai có thể đau nhức nhẹ khi vận động hoặc bóp nắn nhưng không mất cảm giác da',
               'phản xạ gân xương và sức cơ ngọn chi (nắm bàn tay, gấp duỗi cổ chân) vẫn còn bảo tồn tương đối tốt',
               'xét nghiệm men cơ Creatine Kinase (CK) tăng rất cao gấp nhiều lần bình thường'],
    'ten': 'bệnh cơ viêm đa cơ tự miễn'},
    {   'bien_the_chan_doan': [   'Viêm da cơ tự miễn (Dermatomyositis) thể kinh điển ở người trưởng thành.',
                              'Viêm da cơ tự miễn biểu hiện ban Heliotrope, sẩn Gottron và yếu cơ gốc chi đối xứng.',
                              'Viêm da cơ tự miễn có dấu hiệu bàn tay thợ cơ khí nghi ngờ hội chứng kháng synthetase.',
                              'Viêm da cơ tự miễn thể ít triệu chứng cơ (Amyopathic dermatomyositis) ưu thế tổn thương '
                              'da.',
                              'Viêm da cơ tự miễn ở người lớn tuổi cần tầm soát toàn diện ung thư tiềm ẩn.',
                              'Viêm da cơ tự miễn giai đoạn hoạt động kèm bệnh phổi kẽ.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm men cơ CK, Aldolase, bilan tự miễn (ANA, bộ kháng thể đặc hiệu viêm da cơ '
                             'như anti-Mi-2, anti-TIF1-gamma, anti-MDA5, anti-NXP2), điện cơ đồ EMG hoặc sinh thiết '
                             'da/cơ khẳng định chẩn đoán.',
                             'Bắt buộc thực hiện tầm soát ung thư toàn diện phù hợp theo tuổi và giới tính (chụp CT '
                             'ngực bụng chậu, nội soi tiêu hóa dạ dày đại tràng, siêu âm vú/tử cung buồng trứng hoặc '
                             'PSA, CA-125) đặc biệt khi dương tính với anti-TIF1-gamma hoặc ở bệnh nhân > 40 tuổi.',
                             'Chụp CT ngực phân giải cao (HRCT) tầm soát bệnh phổi kẽ tiến triển nhanh (đặc biệt nếu '
                             'có anti-MDA5 dương tính kèm loét da).',
                             'Khởi đầu điều trị toàn thân bằng Prednisolone liều 0,5-1 mg/kg/ngày kết hợp thuốc ức chế '
                             'miễn dịch như Methotrexate, Azathioprine hoặc Mycophenolate mofetil để kiểm soát viêm cơ '
                             'và ban da.',
                             'Điều trị hỗ trợ ban da: hướng dẫn tránh nắng tuyệt đối dùng kem chống nắng phổ rộng SPF '
                             '>= 50 hàng ngày, bôi Corticoid tại chỗ hoặc Tacrolimus cho tổn thương da mặt tay, cân '
                             'nhắc Hydroxychloroquine giúp giảm ban da nhạy cảm ánh sáng.',
                             'Theo dõi đáp ứng sức cơ, men cơ và tác dụng phụ của thuốc định kỳ hàng tháng tại chuyên '
                             'khoa Cơ xương khớp - Miễn dịch.'],
    'bien_the_kham': [   'Khám vùng mặt thấy ban màu tím hoa cà đặc trưng kèm phù nề nhẹ hai mi mắt trên (ban '
                         'Heliotrope), vùng cổ ngực trước có mảng hồng ban lan tỏa hình chữ V; hai bàn tay có nhiều '
                         'sẩn đỏ tím dày sừng hơi lõm nhẹ ngay trên mặt lưng khớp bàn ngón và liên đốt gần (sẩn '
                         'Gottron), kèm giãn mao mạch quanh chân móng tay.',
                         'Đánh giá sức cơ thấy yếu đối xứng gốc chi: giạng vai và gấp đùi 3+/5, khó tự đứng dậy từ '
                         'ghế, cơ ngọn chi bình thường 5/5; da mặt duỗi hai khuỷu tay và đầu gối có mảng đỏ sậm (dấu '
                         'hiệu Gottron).',
                         'Hai bờ bên ngón trỏ và ngón cái tay bệnh nhân có lớp da dày sừng nứt nẻ thô ráp đen sạm '
                         'giống bàn tay người sửa máy (bàn tay thợ cơ khí), nghe đáy phổi hai bên có tiếng ran nổ kiểu '
                         'khóa dán Velcro.',
                         'Vùng da bả vai và gáy sau cổ có mảng hồng ban rộng nhạy cảm ánh nắng (dấu hiệu khăn choàng - '
                         'Shawl sign) kèm sẩn Gottron rõ ở mu bàn tay, men cơ CK trước đó ghi nhận tăng gấp 10 lần.',
                         'Khám vùng mặt ngoài đùi phải có mảng đỏ tím nhẹ (dấu hiệu bao súng - Holster sign), cơ gấp '
                         'cổ yếu nhẹ, không có đau khớp sưng khớp biến dạng.',
                         'Bệnh nhân có biểu hiện viêm da cơ kinh điển với ban da rất rõ rệt ở mi mắt và mu ngón tay '
                         'kèm yếu nhẹ đai hông.'],
    'chan_doan': 'Viêm da cơ tự miễn (Dermatomyositis) thể kinh điển ở người trưởng thành.',
    'chinh': [   'phát ban tím hồng đặc trưng ở hai mi mắt trên kèm phù nề mi mắt (ban Heliotrope) và ban đỏ hình chữ '
                 'V trước cổ ngực hoặc vùng vai gáy (dấu hiệu khăn choàng)',
                 'xuất hiện các sẩn đỏ tím hơi gồ có vảy nhẹ ở mặt mu các khớp bàn ngón tay và liên đốt ngón tay (sẩn '
                 'Gottron)',
                 'yếu cơ gốc chi đối xứng hai bên (khó đứng lên ngồi xuống, khó giơ tay lên cao) đi kèm tổn thương da '
                 'đặc trưng'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Làm xét nghiệm men cơ CK, Aldolase, bilan tự miễn (ANA, bộ kháng thể đặc hiệu viêm da cơ như '
                'anti-Mi-2, anti-TIF1-gamma, anti-MDA5, anti-NXP2), điện cơ đồ EMG hoặc sinh thiết da/cơ khẳng định '
                'chẩn đoán.',
    'kham': 'Khám vùng mặt thấy ban màu tím hoa cà đặc trưng kèm phù nề nhẹ hai mi mắt trên (ban Heliotrope), vùng cổ '
            'ngực trước có mảng hồng ban lan tỏa hình chữ V; hai bàn tay có nhiều sẩn đỏ tím dày sừng hơi lõm nhẹ ngay '
            'trên mặt lưng khớp bàn ngón và liên đốt gần (sẩn Gottron), kèm giãn mao mạch quanh chân móng tay.',
    'nhom': 'người lớn',
    'phu': [   'da vùng rìa móng tay có ban đỏ giãn mao mạch quanh móng và tăng sừng nứt nẻ bờ ngoài ngón tay (bàn tay '
               'thợ cơ khí)',
               'tăng nhạy cảm rõ rệt với ánh nắng mặt trời gây đỏ bùng phát ban vùng hở',
               'bệnh nhân trên 40 tuổi mắc viêm da cơ tự miễn cần tầm soát kỹ các bệnh lý ác tính tiềm ẩn'],
    'ten': 'viêm da cơ tự miễn'},
    {   'bien_the_chan_doan': [   'Viêm khớp vảy nến thể ít khớp không đối xứng kèm viêm ngón hình khúc dồi.',
                              'Viêm khớp vảy nến thể tổn thương khớp liên đốt xa (DIP) và loạn dưỡng rỗ móng.',
                              'Viêm khớp vảy nến thể đa khớp đối xứng giống viêm khớp dạng thấp (RF âm tính).',
                              'Viêm khớp vảy nến thể trục cột sống kèm viêm điểm bám gân Achilles.',
                              'Viêm khớp vảy nến giai đoạn hoạt động mức độ vừa theo tiêu chuẩn CASPAR.',
                              'Viêm khớp vảy nến mạn tính cần điều trị thuốc điều chỉnh bệnh DMARDs sớm.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm máu kiểm tra CRP, tốc độ máu lắng ESR, loại trừ yếu tố dạng thấp RF và '
                             'Anti-CCP (thường âm tính), xét nghiệm acid uric (vảy nến nặng hay có tăng acid uric máu '
                             'kèm theo) và HLA-B27 nếu có đau cột sống.',
                             'Chụp X-quang hai bàn tay, bàn chân và khung chậu tìm dấu hiệu đặc trưng của viêm khớp '
                             'vảy nến (bào mòn rìa khớp kèm tân tạo xương cạnh khớp, hình ảnh "bút chì cắm vào chén" ở '
                             'khớp liên đốt xa) và siêu âm khớp tìm viêm điểm bám gân.',
                             'Đối với thể nhẹ ít khớp/viêm điểm bám gân: dùng NSAID đường uống kết hợp tiêm Corticoid '
                             'nội khớp hoặc quanh điểm bám gân (tránh tiêm gân gót) khi chỉ sưng khu trú 1-2 khớp.',
                             'Khởi trị sớm thuốc chống thấp khớp tác dụng chậm kinh điển (csDMARDs) như Methotrexate '
                             '(10-20mg/tuần uống hoặc tiêm dưới da kèm Acid folic giúp kiểm soát tốt cả khớp ngoại '
                             'biên lẫn mảng da vảy nến) hoặc Leflunomide, Sulfasalazine.',
                             'Xem xét nâng bậc sang thuốc sinh học (kháng TNF-alpha, kháng IL-17 như '
                             'Secukinumab/Ixekizumab hoặc kháng IL-12/23, thuốc ức chế JAK) nếu bệnh nhân có viêm ngón '
                             'nặng, viêm khớp cột sống trục hoặc không đáp ứng Methotrexate.',
                             'Phối hợp chăm sóc da liễu bôi thuốc mỡ Calcipotriol/Betamethasone trên mảng vảy nến, '
                             'tránh dùng Corticoid đường toàn thân liều cao rồi ngưng đột ngột vì dễ gây bùng phát vảy '
                             'nến thể mủ nguy hiểm.'],
    'bien_the_kham': [   'Khám bàn tay phải thấy ngón tay giữa sưng to tròn đỏ ấm toàn bộ từ gốc đến ngọn trông như '
                         'cây xúc xích (dactylitis - ngón tay hình khúc dồi), khớp liên đốt xa ngón trỏ sưng nề biến '
                         'dạng nhẹ, móng tay nhiều ngón có hàng loạt chấm rỗ nhỏ li ti (rỗ móng) kèm mảng vảy nến da '
                         'đầu sau tai và mặt duỗi khuỷu tay.',
                         'Khám khớp không đối xứng: sưng tràn dịch khớp gối trái và khớp cổ chân phải, kèm sưng đau rõ '
                         'rệt vùng điểm bám gân gót Achilles bên phải, da vùng rãnh liên mông có mảng hồng ban tróc '
                         'vảy trắng bạc kín đáo.',
                         'Tổn thương ưu thế các khớp liên đốt xa (DIP) hai bàn tay sưng đỏ hơi tím kèm tách bờ tự do '
                         'bản móng và đổi màu móng kiểu giọt dầu, khớp bàn ngón MCP bình thường, yếu tố RF trước đó âm '
                         'tính.',
                         'Bệnh nhân có tiền sử vảy nến mảng 8 năm nay, đợt này xuất hiện đau lưng vùng cùng chậu về '
                         'gần sáng kèm sưng đau hai khớp ức đòn và khớp gối phải.',
                         'Ngón chân thứ 3 và thứ 4 bàn chân trái sưng phồng mọng đỏ kiểu ngón chân hình khúc dồi làm '
                         'bệnh nhân không đi vừa giày, vùng mặt trước cẳng chân có vài mảng vảy nến ranh giới sắc nét.',
                         'Khám da liễu - cơ xương khớp phối hợp đạt điểm CASPAR dương tính rõ rệt: tổn thương vảy nến '
                         'hiện hữu, rỗ móng tay, viêm ngón và đau điểm bám cân gan chân.'],
    'chan_doan': 'Viêm khớp vảy nến thể ít khớp không đối xứng kèm viêm ngón hình khúc dồi.',
    'chinh': [   'sưng đau cứng khớp ngoại biên không đối xứng đặc biệt hay gặp ở các khớp liên đốt ngón xa (DIP) hoặc '
                 'sưng phồng toàn bộ một ngón tay ngón chân như hình khúc dồi (viêm ngón - dactylitis)',
                 'có tổn thương da vảy nến (mảng đỏ ranh giới rõ phủ vảy trắng bạc ở khuỷu tay đầu gối da đầu rãnh '
                 'mông) hoặc tiền sử gia đình mắc vảy nến',
                 'tổn thương móng tay đặc trưng dạng rỗ móng như đầu kim châm (pitting), tách móng hoặc dày sừng dưới '
                 'móng'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Làm xét nghiệm máu kiểm tra CRP, tốc độ máu lắng ESR, loại trừ yếu tố dạng thấp RF và Anti-CCP '
                '(thường âm tính), xét nghiệm acid uric (vảy nến nặng hay có tăng acid uric máu kèm theo) và HLA-B27 '
                'nếu có đau cột sống.',
    'kham': 'Khám bàn tay phải thấy ngón tay giữa sưng to tròn đỏ ấm toàn bộ từ gốc đến ngọn trông như cây xúc xích '
            '(dactylitis - ngón tay hình khúc dồi), khớp liên đốt xa ngón trỏ sưng nề biến dạng nhẹ, móng tay nhiều '
            'ngón có hàng loạt chấm rỗ nhỏ li ti (rỗ móng) kèm mảng vảy nến da đầu sau tai và mặt duỗi khuỷu tay.',
    'nhom': 'người lớn',
    'phu': [   'viêm điểm bám gân (enthesitis) gây đau gót chân tại chỗ bám gân Achilles hoặc cân gan chân khi bước đi',
               'cứng khớp buổi sáng kéo dài trên 30-45 phút và có thể kèm đau lưng kiểu viêm cột sống khớp cùng chậu',
               'yếu tố dạng thấp RF thường âm tính giúp phân biệt với viêm khớp dạng thấp'],
    'ten': 'viêm khớp vảy nến'},
    {   'bien_the_chan_doan': [   'Hội chứng Sjogren nguyên phát thể tổn thương tuyến ngoại tiết (khô mắt khô miệng).',
                              'Hội chứng Sjogren nguyên phát có biểu hiện sưng tuyến mang tai tái diễn và đau đa khớp.',
                              'Hội chứng Sjogren thứ phát trên nền bệnh tự miễn mô liên kết.',
                              'Hội chứng Sjogren có giảm nặng tiết nước mắt nước bọt (test Schirmer dương tính).',
                              'Theo dõi hội chứng Sjogren mạn tính cần tầm soát định kỳ biến chứng u lympho tế bào B.',
                              'Hội chứng Sjogren khô mắt khô miệng mức độ trung bình cần điều trị kích thích tiết '
                              'dịch.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm tự miễn chuyên sâu tìm kháng thể kháng nhân (ANA), yếu tố dạng thấp RF, '
                             'kháng thể đặc hiệu anti-SSA/Ro và anti-SSB/La, định lượng bổ thể C3 C4, điện di protein '
                             'huyết thanh (tìm tăng gamma globulin đa dòng) và công thức máu.',
                             'Phối hợp chuyên khoa Mắt đo chính xác nghiệm pháp Schirmer, nhuộm bề mặt nhãn cầu tìm '
                             'tổn thương biểu mô giác kết mạc (Ocular Staining Score) và đánh giá thời gian vỡ phim '
                             'nước mắt (TBUT).',
                             'Chỉ định sinh thiết tuyến nước bọt phụ môi dưới đánh giá chỉ số tập trung tế bào lympho '
                             '(focus score >= 1 ổ/4mm2) nếu kháng thể anti-SSA/SSB âm tính nhưng lâm sàng nghi ngờ '
                             'cao.',
                             'Điều trị bảo vệ mắt và miệng tại chỗ: nhỏ nước mắt nhân tạo không chất bảo quản thường '
                             'xuyên ban ngày kèm gel tra mắt ban đêm (hoặc nhỏ Cyclosporine 0,05% tại chỗ nếu viêm bề '
                             'mặt nhãn cầu nặng); súc miệng giữ ẩm, nhai kẹo không đường kích thích tiết nước bọt và '
                             'khám nha khoa bôi fluor ngừa sâu răng mỗi 3-6 tháng.',
                             'Dùng thuốc chủ vận muscarinic kích thích tuyến ngoại tiết tiết dịch đường uống như '
                             'Pilocarpine (5mg x 3-4 lần/ngày) hoặc Cevimeline nếu khô miệng nặng không đáp ứng biện '
                             'pháp tại chỗ (chú ý tác dụng phụ vã mồ hôi).',
                             'Dùng Hydroxychloroquine hoặc thuốc ức chế miễn dịch nhẹ nếu có đau mỏi khớp mệt mỏi '
                             'nhiều hay tổn thương ngoài tuyến (phổi kẽ, thận, thần kinh ngoại biên), và khám theo dõi '
                             'sát kích thước tuyến mang tai hạch ngoại biên phát hiện sớm u lympho.'],
    'bien_the_kham': [   'Khám khoang miệng thấy niêm mạc má khô dính không có hồ nước bọt dưới sàn miệng (gương khám '
                         'dính nhẹ vào niêm mạc má), lưỡi đỏ bóng khô ráo ít gai có các rãnh nứt nhỏ, nhiều răng hàm '
                         'bị sâu cổ răng; hai tuyến mang tai vùng góc hàm hơi sưng phì đại chắc nhẹ không đau nhiều '
                         'khi ấn.',
                         'Khám mắt thực hiện test Schirmer I không nhỏ tê: dải giấy thấm tiêu chuẩn chỉ thấm ướt được '
                         '2mm ở mắt phải và 3mm ở mắt trái sau 5 phút (dương tính rõ <= 5mm), kết mạc mắt hơi đỏ nhẹ '
                         'mất độ bóng ướt.',
                         'Bệnh nhân nữ 48 tuổi mang theo chai nước bên mình liên tục, khai phải thức dậy uống nước '
                         'nhiều lần ban đêm và không thể nuốt bánh quy khô nếu không có nước uống kèm; các khớp cổ tay '
                         'và khớp bàn ngón hai bên hơi đau nhẹ không sưng tràn dịch.',
                         'Phát hiện ban xuất huyết chấm nhỏ do tăng gamma globulin máu hoặc viêm mạch nhỏ ở hai cẳng '
                         'chân kèm khô da toàn thân và khô họng ho khan mạn tính.',
                         'Lấy mẫu thử tốc độ dòng nước bọt không kích thích (UWSF) thu được dưới 0,1 ml/phút (giảm '
                         'nặng), không có hạch cổ to cứng bất thường hay lách to (tầm soát nguy cơ u lympho).',
                         'Bệnh nhân có tiền sử chẩn đoán viêm khớp dạng thấp ổn định nay xuất hiện thêm hội chứng khô '
                         'mắt khô miệng tiến triển (hội chứng Sjogren thứ phát).'],
    'chan_doan': 'Hội chứng Sjogren nguyên phát thể tổn thương tuyến ngoại tiết (khô mắt khô miệng).',
    'chinh': [   'khô mắt kéo dài trên 3 tháng cảm giác cộm rát như có cát bụi bay trong mắt, đỏ mắt nhẹ và phải dùng '
                 'nước mắt nhân tạo hàng ngày',
                 'khô miệng nặng kéo dài khiến bệnh nhân luôn phải nhấp nước mới nuốt trôi thức ăn khô (như bánh mì '
                 'bánh quy) và khó nói chuyện liên tục lâu',
                 'nghiệm pháp Schirmer đo lượng nước mắt thấm giấy lọc dưới 5mm trong 5 phút và sưng tuyến mang tai '
                 'hai bên từng đợt'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'miễn dịch - dị ứng',
    'ke_hoach': 'Làm xét nghiệm tự miễn chuyên sâu tìm kháng thể kháng nhân (ANA), yếu tố dạng thấp RF, kháng thể đặc '
                'hiệu anti-SSA/Ro và anti-SSB/La, định lượng bổ thể C3 C4, điện di protein huyết thanh (tìm tăng gamma '
                'globulin đa dòng) và công thức máu.',
    'kham': 'Khám khoang miệng thấy niêm mạc má khô dính không có hồ nước bọt dưới sàn miệng (gương khám dính nhẹ vào '
            'niêm mạc má), lưỡi đỏ bóng khô ráo ít gai có các rãnh nứt nhỏ, nhiều răng hàm bị sâu cổ răng; hai tuyến '
            'mang tai vùng góc hàm hơi sưng phì đại chắc nhẹ không đau nhiều khi ấn.',
    'nhom': 'người lớn',
    'phu': [   'lưỡi khô đỏ mất gai nứt nẻ kèm sâu răng tiến triển nhanh ở cổ răng và hay bị tưa nấm miệng tái phát',
               'đau mỏi khớp không biến dạng, mệt mỏi kéo dài và có thể khô âm đạo ở nữ giới',
               'kháng thể tự miễn kháng SSA (Ro) và/hoặc SSB (La) dương tính trong máu'],
    'ten': 'hội chứng Sjogren khô mắt khô miệng'},
    {   'bien_the_chan_doan': [   'Bệnh Still khởi phát ở người lớn (AOSD) giai đoạn cấp tính hoạt động mạnh.',
                              'Bệnh Still người lớn biểu hiện tam chứng sốt cao kịch phát, ban hồng cá hồi và viêm đa '
                              'khớp.',
                              'Theo dõi bệnh Still người lớn (sốt chưa rõ nguyên nhân) cần loại trừ nhiễm khuẩn huyết '
                              'và u lympho.',
                              'Bệnh Still người lớn có tăng vọt Ferritin huyết thanh nguy cơ hội chứng thực bào máu '
                              '(MAS).',
                              'Bệnh Still ở người trưởng thành thể đa khớp đáp ứng tốt với Corticosteroid toàn thân.',
                              'Đợt bùng phát cấp bệnh Still người lớn không đáp ứng với kháng sinh thông thường.'],
    'bien_the_ke_hoach': [   'Làm đầy đủ xét nghiệm loại trừ nhiễm khuẩn, ác tính và bệnh tự miễn khác (tiêu chuẩn '
                             'loại trừ của Yamaguchi): cấy máu nhiều lần, cấy nước tiểu, procalcitonin, huyết thanh '
                             'chẩn đoán virus, RF, ANA, chụp CT ngực bụng tìm hạch sâu u lympho.',
                             'Định lượng bộ chỉ dấu đặc hiệu: tổng phân tích tế bào máu (bạch cầu thường > 10-15 G/L '
                             'với >= 80% bạch cầu đa nhân trung tính), CRP/ESR tăng cao, men gan AST ALT tăng nhẹ và '
                             'đặc biệt là Ferritin huyết thanh (thường tăng gấp 5-10 lần ngưỡng trên, > 1000 ng/mL).',
                             'Theo dõi chặt chẽ các dấu hiệu cảnh báo biến chứng nguy hiểm chết người là Hội chứng '
                             'hoạt hóa đại thực bào (MAS): sốt cao liên tục không hạ, giảm 3 dòng tế bào máu đột ngột, '
                             'triglyceride tăng vọt, fibrinogen tụt giảm và ferritin tăng cực cao.',
                             'Điều trị cắt cơn cấp tính bằng Corticosteroid toàn thân (Prednisolone 0,5-1 mg/kg/ngày '
                             'hoặc Methylprednisolone tĩnh mạch xung liều cao nếu có viêm màng tim, viêm gan nặng hoặc '
                             'dọa hội chứng MAS), kết hợp thuốc hạ sốt NSAID (Indomethacin hoặc Naproxen) hỗ trợ.',
                             'Phối hợp sớm thuốc điều hòa miễn dịch tiết kiệm steroid như Methotrexate nếu có biểu '
                             'hiện viêm khớp mạn tính dai dẳng hoặc phụ thuộc corticoid.',
                             'Chuyển tuyến chuyên khoa Miễn dịch - Dị ứng xem xét chỉ định thuốc sinh học kháng thụ '
                             'thể IL-1 (Anakinra) hoặc kháng thụ thể IL-6 (Tocilizumab) đối với thể nặng kháng trị '
                             'corticoid.'],
    'bien_the_kham': [   'Bệnh nhân nam 29 tuổi nhập viện vì sốt cao chưa rõ nguyên nhân 3 tuần nay: nhiệt độ lúc 18 '
                         'giờ đo được 39,6 độ C kèm ớn lạnh và xuất hiện mảng ban dát sẩn màu hồng cá hồi không ngứa '
                         'rải rác ở ngực lưng và mặt trong cánh tay; khám lại sáng hôm sau bệnh nhân hoàn toàn hết sốt '
                         'và ban da cũng biến mất sạch sẽ.',
                         'Khám khớp thấy sưng đau nóng hai khớp cổ tay và hai khớp gối mức độ vừa, họng đỏ nhẹ không '
                         'có giả mạc mủ amidan nhưng bệnh nhân khai đau rát họng dữ dội trước khi bắt đầu đợt sốt; sờ '
                         'thấy vài hạch cổ hai bên kích thước 1,5cm mềm di động và gan mấp mé 2cm dưới bờ sườn phải.',
                         'Dấu hiệu Koebner dương tính tại vùng da ngực bị cào nhẹ tạo vệt ban hồng cá hồi nổi rõ lúc '
                         'sốt cao, tiếng tim hơi nhanh 110 l/p lúc sốt không nghe thấy tiếng cọ màng ngoài tim hay '
                         'tiếng thổi bất thường.',
                         'Bệnh nhân mệt mỏi gầy sút nhẹ sau 2 tuần sốt cao thất thường hàng ngày không đáp ứng với 2 '
                         'đợt kháng sinh phổ rộng từ tuyến trước, phổi thông khí đều hai bên, bụng mềm.',
                         'Khớp cổ tay hai bên đau nhức hạn chế gấp duỗi rõ trong cơn sốt, lách sờ chạm dưới bờ sườn '
                         'trái 1cm, không có xuất huyết dưới da hay vết đốt côn trùng trên người.',
                         'Thăm khám lâm sàng đáp ứng đầy đủ các tiêu chuẩn chính Yamaguchi: sốt cao >= 39 độ C kéo dài '
                         '> 1 tuần, đau sưng khớp > 2 tuần và ban hồng cá hồi thoáng qua đặc trưng.'],
    'chan_doan': 'Bệnh Still khởi phát ở người lớn (AOSD) giai đoạn cấp tính hoạt động mạnh.',
    'chinh': [   'sốt cao kịch phát hàng ngày lên tới 39-40 độ C vào một giờ cố định buổi chiều tối rồi tự hạ về bình '
                 'thường hoặc dưới 37 độ vào ban sáng (sốt hình tháp chuông)',
                 'phát ban màu hồng cá hồi (salmon-pink) thoáng qua xuất hiện ở thân mình gốc chi đúng lúc nhiệt độ '
                 'sốt vọt lên cao rồi lặn mất khi hạ sốt',
                 'đau khớp hoặc sưng viêm đa khớp cấp tính ở cổ tay khớp gối cổ chân kèm đau họng nhiều ở giai đoạn '
                 'khởi phát'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'miễn dịch - dị ứng',
    'ke_hoach': 'Làm đầy đủ xét nghiệm loại trừ nhiễm khuẩn, ác tính và bệnh tự miễn khác (tiêu chuẩn loại trừ của '
                'Yamaguchi): cấy máu nhiều lần, cấy nước tiểu, procalcitonin, huyết thanh chẩn đoán virus, RF, ANA, '
                'chụp CT ngực bụng tìm hạch sâu u lympho.',
    'kham': 'Bệnh nhân nam 29 tuổi nhập viện vì sốt cao chưa rõ nguyên nhân 3 tuần nay: nhiệt độ lúc 18 giờ đo được '
            '39,6 độ C kèm ớn lạnh và xuất hiện mảng ban dát sẩn màu hồng cá hồi không ngứa rải rác ở ngực lưng và mặt '
            'trong cánh tay; khám lại sáng hôm sau bệnh nhân hoàn toàn hết sốt và ban da cũng biến mất sạch sẽ.',
    'nhom': 'người lớn',
    'phu': [   'sưng hạch ngoại biên di động, gan lách to nhẹ và có thể kèm tràn dịch màng phổi màng tim',
               'xét nghiệm bạch cầu máu tăng rất cao ưu thế đa nhân trung tính và nồng độ Ferritin huyết thanh tăng '
               'vọt trên 1000-3000 ng/mL (với tỷ lệ Ferritin glycosyl hóa giảm dưới 20%)',
               'cấy máu âm tính nhiều lần, yếu tố dạng thấp RF và kháng thể kháng nhân ANA âm tính'],
    'ten': 'bệnh Still người lớn'},
    {   'bien_the_chan_doan': [   'Viêm khớp cấp giả gout (Pseudogout) khớp gối phải do lắng đọng tinh thể pyrophosphate '
                              'canxi (CPPD).',
                              'Cơn viêm khớp cấp tính cổ tay trái do bệnh lắng đọng tinh thể CPPD (giả gout).',
                              'Viêm khớp giả gout cấp khởi phát sau phẫu thuật ở người cao tuổi.',
                              'Bệnh khớp tinh thể CPPD đợt cấp khớp gối trái có vôi hóa sụn chêm (chondrocalcinosis).',
                              'Theo dõi giả gout cấp tính cần chọc dịch khớp loại trừ tuyệt đối viêm khớp nhiễm khuẩn.',
                              'Viêm khớp giả gout cấp đáp ứng nhanh với chọc hút tháo dịch và thuốc kháng viêm.'],
    'bien_the_ke_hoach': [   'Thực hiện chọc hút dịch khớp gối vô khuẩn khẩn cấp gửi xét nghiệm: đếm tế bào dịch khớp, '
                             'nhuộm Gram, nuôi cấy vi khuẩn (bắt buộc để loại trừ viêm khớp nhiễm khuẩn cấp) và soi '
                             'dưới kính hiển vi phân cực tìm tinh thể CPPD hình thoi/que ngắn lưỡng chiết quang dương '
                             'tính yếu (màu xanh lam khi song song trục chậm, khác với tinh thể urat hình kim của bệnh '
                             'gout).',
                             'Chụp X-quang khớp gối hai bên và khớp cổ tay tìm dấu hiệu vôi hóa sụn khớp '
                             '(chondrocalcinosis) dọc theo sụn chêm và sụn khớp, đồng thời xét nghiệm máu loại trừ các '
                             'nguyên nhân rối loạn chuyển hóa gây CPPD thứ phát ở người < 60 tuổi (canxi, magie, '
                             'phospho, sắt/ferritin tìm bệnh ứ sắt, TSH, PTH tìm cường cận giáp).',
                             'Điều trị cắt cơn cấp khi đã loại trừ nhiễm khuẩn: chọc hút tháo bớt dịch căng giảm áp '
                             'khớp kết hợp tiêm Corticoid nội khớp (Triamcinolone acetonide) giúp cắt đau nhanh chóng '
                             'và an toàn nhất cho người cao tuổi có nhiều bệnh nền thận dạ dày.',
                             'Nếu tổn thương nhiều khớp hoặc không tiêm nội khớp: dùng thuốc kháng viêm NSAID ngắn '
                             'ngày (nếu chức năng thận dạ dày tốt), hoặc Prednisolone đường uống 20-30mg/ngày giảm '
                             'liều nhanh trong 5-7 ngày, hoặc Colchicine liều thấp (0,5mg x 2 lần/ngày).',
                             'Nghỉ ngơi cố định khớp tạm thời, chườm túi đá lạnh bọc khăn lên khớp sưng nóng 15 phút '
                             'mỗi 3-4 giờ.',
                             'Tư vấn tái khám kiểm soát tốt bệnh thoái hóa khớp đi kèm và dùng Colchicine liều thấp '
                             '0,5mg/ngày dự phòng nếu cơn giả gout cấp tái phát quá thường xuyên (>= 3 lần/năm).'],
    'bien_the_kham': [   'Khớp gối phải sưng to căng bóng đỏ nhẹ và rất nóng khi sờ mu bàn tay, dấu hiệu bập bềnh '
                         'xương bánh chè dương tính rõ với lượng dịch khớp nhiều, bệnh nhân 72 tuổi đau nhức dữ dội '
                         'không gấp được gối quá 20 độ, nhiệt độ cơ thể 37,9 độ C.',
                         'Khám khớp cổ tay trái thấy sưng phù nóng đỏ lan tỏa mặt mu cổ tay, hạn chế mọi động tác gấp '
                         'duỗi cổ tay, nhưng các khớp bàn ngón chân cái (MTP 1) hai bên hoàn toàn bình thường không '
                         'sưng đau.',
                         'Bệnh nhân cao tuổi sau mổ nội soi tuyến tiền liệt 3 ngày đột ngột sưng nóng đau khớp gối '
                         'trái cấp tính, ấn khe khớp đau dữ dội, không có hạt tophi ở vành tai hay khuỷu tay, không có '
                         'vết thương xước da gần khớp.',
                         'Khám vùng khớp vai phải sưng ấm hạn chế vận động cấp tính ở cụ bà 78 tuổi, rung nhẹ khớp gây '
                         'đau nhói, trước đó khớp gối có tiền sử thoái hóa vôi hóa sụn khớp.',
                         'Chọc hút dịch khớp gối phải thu được dịch vàng hơi đục độ nhớt giảm, không có mùi hôi mủ, '
                         'sau khi tháo bớt 40ml dịch bệnh nhân cảm thấy đỡ căng tức khớp gối ngay.',
                         'Các khớp khác không sưng đau, thân nhiệt 37,6 độ C, huyết áp 135/80 mmHg, tim phổi đều rõ.'],
    'chan_doan': 'Viêm khớp cấp giả gout (Pseudogout) khớp gối phải do lắng đọng tinh thể pyrophosphate canxi (CPPD).',
    'chinh': [   'sưng nóng đỏ đau dữ dội cấp tính đột ngột tại một khớp lớn (thường gặp nhất là khớp gối, kế đến là '
                 'khớp cổ tay khớp vai hoặc cổ chân) giống hệt cơn gout cấp',
                 'khớp bị ảnh hưởng tràn dịch căng tức rõ rệt khiến người bệnh cao tuổi không thể tự đứng đi lại hay '
                 'cử động khớp',
                 'phim X-quang khớp thấy hình ảnh vôi hóa sụn khớp đặc trưng (đường viền vôi trắng mảnh chạy dọc sụn '
                 'chêm khớp gối hoặc dây chằng tam giác cổ tay)'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Thực hiện chọc hút dịch khớp gối vô khuẩn khẩn cấp gửi xét nghiệm: đếm tế bào dịch khớp, nhuộm Gram, '
                'nuôi cấy vi khuẩn (bắt buộc để loại trừ viêm khớp nhiễm khuẩn cấp) và soi dưới kính hiển vi phân cực '
                'tìm tinh thể CPPD hình thoi/que ngắn lưỡng chiết quang dương tính yếu (màu xanh lam khi song song '
                'trục chậm, khác với tinh thể urat hình kim của bệnh gout).',
    'kham': 'Khớp gối phải sưng to căng bóng đỏ nhẹ và rất nóng khi sờ mu bàn tay, dấu hiệu bập bềnh xương bánh chè '
            'dương tính rõ với lượng dịch khớp nhiều, bệnh nhân 72 tuổi đau nhức dữ dội không gấp được gối quá 20 độ, '
            'nhiệt độ cơ thể 37,9 độ C.',
    'nhom': 'người lớn',
    'phu': [   'thường xảy ra ở người lớn tuổi trên 60 tuổi và có thể bùng phát ngay sau phẫu thuật, chấn thương nhẹ '
               'hoặc mắc bệnh cấp tính nội khoa',
               'có thể kèm sốt nhẹ 38 độ C, tăng bạch cầu máu và tăng CRP dễ nhầm với viêm khớp nhiễm khuẩn',
               'nồng độ acid uric máu thường hoàn toàn bình thường (trừ khi đồng mắc)'],
    'ten': 'giả gout do lắng đọng pyrophosphate canxi'},
    {   'bien_the_chan_doan': [   'Hội chứng viêm sụn sườn Tietze cấp tính tại khớp sụn sườn số 2 bên trái.',
                              'Viêm sụn sườn Tietze lành tính bên phải khởi phát sau ho kéo dài.',
                              'Hội chứng Tietze sưng đau đơn độc sụn sườn số 3 không do nhiễm khuẩn.',
                              'Viêm sụn sườn Tietze cấp tính cần loại trừ bệnh lý mạch vành cấp.',
                              'Viêm sụn sườn Tietze mức độ vừa đáp ứng tốt với thuốc kháng viêm giảm đau.',
                              'Hội chứng Tietze thành ngực trước giai đoạn cấp ổn định sau điều trị bảo tồn.'],
    'bien_the_ke_hoach': [   'Bắt buộc thực hiện điện tâm đồ (ECG 12 chuyển đạo), men tim Troponin nếu cần (ở người có '
                             'yếu tố nguy cơ tim mạch) và chụp X-quang tim phổi thẳng để loại trừ chắc chắn cơn đau '
                             'thắt ngực, nhồi máu cơ tim, bóc tách động mạch chủ hoặc thuyên tắc phổi trước khi kết '
                             'luận lành tính.',
                             'Siêu âm phần mềm thành ngực vùng sụn sườn đánh giá độ phì đại phù nề sụn sườn và loại '
                             'trừ khối u xương sụn hay áp xe thành ngực; xét nghiệm CRP/máu lắng thường bình thường '
                             'hoặc tăng rất nhẹ.',
                             'Giải thích trấn an bệnh nhân hội chứng Tietze là bệnh lý viêm sụn thành ngực hoàn toàn '
                             'lành tính không nguy hiểm tính mạng tim phổi để giảm tâm lý lo âu hoảng sợ.',
                             'Điều trị bảo tồn bằng nghỉ ngơi tránh các động tác chống đẩy kéo xà nặng ngực, chườm ấm '
                             'hoặc chườm lạnh tại chỗ, uống thuốc giảm đau kháng viêm NSAID (Ibuprofen, Meloxicam hoặc '
                             'Celecoxib) trong 7-10 ngày kết hợp gel bôi NSAID hoặc miếng dán Lidocaine.',
                             'Xem xét tiêm tại chỗ một liều Corticoid pha thuốc tê vào khớp sụn sườn sưng đau (dưới '
                             'hướng dẫn siêu âm tránh vào khoang màng phổi) nếu đau nặng dai dẳng không đáp ứng thuốc '
                             'uống.',
                             'Dặn bệnh nhân rằng đau thường hết sau vài tuần nhưng khối sưng gồ sụn sườn có thể xẹp '
                             'chậm hơn trong vài tháng.'],
    'bien_the_kham': [   'Thành ngực trước bên trái ngay cạnh bờ xương ức tại vị trí khớp sụn sườn số 2 có một khối '
                         'sưng chắc hình thoi đường kính 2,5x3cm nhô gồ rõ rệt hơn bên đối diện, da bên trên hoàn toàn '
                         'bình thường không đỏ nóng; ấn nhẹ đầu ngón tay vào khối sưng bệnh nhân nhăn mặt kêu đau nhói '
                         'đúng điểm.',
                         'Nghiệm pháp ép chéo cánh tay trái qua ngực (crowing rooster maneuver) làm tăng căng khớp sụn '
                         'sườn 2-3 khiến cơn đau vùng ức trái tái hiện rõ; nghe tim đều 76 l/p không tiếng thổi, phổi '
                         'trong đều hai bên.',
                         'Khám vùng khớp sụn sườn số 3 bên phải thấy nề gồ nhẹ cứng chắc ấn đau chói khu trú một khớp '
                         'duy nhất, không có tiếng lạo xạo gãy xương, bệnh nhân không sốt không khó thở, SpO2 99%.',
                         'Bệnh nhân thanh niên 28 tuổi sau đợt ho khan kéo dài 1 tuần xuất hiện khối sưng đau cạnh ức '
                         'phải, đau tăng khi chống đẩy hoặc xoay thân người, điện tâm đồ đo tại phòng khám nhịp xoang '
                         'bình thường không biến đổi ST-T.',
                         'Khối sưng sụn sườn Tietze giới hạn rõ, di động cùng lồng ngực khi hít thở, các khớp khác như '
                         'cổ tay đầu gối không sưng đau, hạch thượng đòn và hạch nách không sờ thấy.',
                         'Phân biệt rõ với viêm sụn sườn thông thường (costochondritis) nhờ dấu hiệu sưng phồng cục bộ '
                         'thực sự thấy rõ bằng mắt và sờ nắn tại sụn sườn số 2 bên trái.'],
    'chan_doan': 'Hội chứng viêm sụn sườn Tietze cấp tính tại khớp sụn sườn số 2 bên trái.',
    'chinh': [   'đau tức ngực phía trước cạnh xương ức một bên kèm khối sưng nổi gồ rõ rệt ngay tại khớp sụn sườn thứ '
                 '2 hoặc thứ 3',
                 'ấn trực tiếp bằng đầu ngón tay lên khối sưng sụn sườn gây đau chói dữ dội tái hiện đúng cơn đau bệnh '
                 'nhân mô tả',
                 'đau tăng lên khi hít thở thật sâu, ho mạnh, hắt hơi, vươn vai hoặc nằm nghiêng ép lên bên ngực đau'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Bắt buộc thực hiện điện tâm đồ (ECG 12 chuyển đạo), men tim Troponin nếu cần (ở người có yếu tố nguy '
                'cơ tim mạch) và chụp X-quang tim phổi thẳng để loại trừ chắc chắn cơn đau thắt ngực, nhồi máu cơ tim, '
                'bóc tách động mạch chủ hoặc thuyên tắc phổi trước khi kết luận lành tính.',
    'kham': 'Thành ngực trước bên trái ngay cạnh bờ xương ức tại vị trí khớp sụn sườn số 2 có một khối sưng chắc hình '
            'thoi đường kính 2,5x3cm nhô gồ rõ rệt hơn bên đối diện, da bên trên hoàn toàn bình thường không đỏ nóng; '
            'ấn nhẹ đầu ngón tay vào khối sưng bệnh nhân nhăn mặt kêu đau nhói đúng điểm.',
    'nhom': 'người lớn',
    'phu': [   'khối sưng ở sụn sườn có hình thoi chắc hơi ấm nhẹ nhưng da phủ bên trên không đỏ tấy mưng mủ',
               'cơn đau có thể lan nhẹ lên vai hoặc cánh tay cùng bên làm bệnh nhân rất lo lắng tưởng nhầm nhồi máu cơ '
               'tim',
               'điện tâm đồ, men tim và X-quang ngực hoàn toàn bình thường'],
    'ten': 'viêm sụn sườn Tietze'},
    {   'bien_the_chan_doan': [   'Vẹo cột sống ngực thắt lưng vô căn tuổi thiếu niên (AIS) đường cong kép hình chữ S.',
                              'Gù vẹo cột sống ngực phải vô căn tuổi vị thành niên mức độ trung bình.',
                              'Vẹo cột sống lưng thắt lưng thiếu niên có nghiệm pháp Adams dương tính và mất cân xứng '
                              'vai.',
                              'Gù vẹo cột sống thiếu niên giai đoạn tăng trưởng xương cần theo dõi chỉ định nẹp chỉnh '
                              'hình.',
                              'Theo dõi gù vẹo cột sống ngực thắt lưng thiếu niên cần chụp X-quang toàn bộ cột sống đo '
                              'góc Cobb.',
                              'Cong vẹo cột sống ngực thắt lưng vô căn mức độ nhẹ đáp ứng tốt với bài tập vật lý trị '
                              'liệu.'],
    'bien_the_ke_hoach': [   'Chụp X-quang toàn bộ cột sống thẳng và nghiêng ở tư thế đứng trên phim dài (EOS hoặc '
                             'phim ghép toàn trục cột sống từ chẩm đến khớp háng) để đo chính xác góc vẹo Cobb, góc gù '
                             'ngực, đánh giá độ trưởng thành xương (chỉ số Risser tại mào chậu) và loại trừ dị tật đốt '
                             'sống bẩm sinh.',
                             'Chỉ định chụp MRI toàn bộ cột sống nếu phát hiện đường cong vẹo ngực lệch sang trái '
                             'không điển hình, tiến triển quá nhanh, có đau lưng nhiều ban đêm hoặc dấu hiệu thần kinh '
                             'bất thường (để loại trừ rỗng tủy sống hoặc dây tủy bám thấp).',
                             'Lập kế hoạch điều trị theo góc Cobb và tuổi xương (Risser): nếu góc Cobb < 20-25 độ thì '
                             'theo dõi chụp kiểm tra định kỳ mỗi 4-6 tháng và tập vật lý trị liệu chuyên biệt cho vẹo '
                             'cột sống (phương pháp Schroth điều chỉnh 3D tư thế và tập thở giãn lồng ngực bên lõm).',
                             'Nếu góc Cobb từ 25 đến 40 độ ở trẻ vẫn còn đang trong giai đoạn phát triển xương (Risser '
                             '0-2): chỉ định đeo áo nẹp chỉnh hình cột sống chuyên dụng (nẹp Boston hoặc Cheneau) '
                             '18-23 giờ/ngày để ngăn chặn tiến triển nặng thêm trong thời kỳ dậy thì.',
                             'Hội chẩn Ngoại Chỉnh hình Cột sống xem xét phẫu thuật nắn chỉnh hàn xương cột sống nếu '
                             'góc Cobb vượt quá 45-50 độ dù đã đeo nẹp nhằm bảo vệ chức năng hô hấp tim mạch và hình '
                             'thể lâu dài.',
                             'Hướng dẫn tư thế ngồi học bàn ghế chuẩn kích thước, đeo cặp sách hai quai cân xứng hai '
                             'bên và khuyến khích các môn thể thao rèn cơ lưng như bơi lội xà đơn.'],
    'bien_the_kham': [   'Quan sát từ phía sau ở tư thế đứng thẳng: vai phải cao hơn vai trái 2cm, góc dưới xương bả '
                         'vai phải nhô cao và đẩy ra sau hơn bên trái, rãnh eo bên trái sâu lõm hơn bên phải; làm '
                         'nghiệm pháp cúi gập thân mình về trước (Adams test) thấy gồ lồng ngực lưng bên phải rõ rệt '
                         '(đo thước đo độ nghiêng Scoliometer đạt 8 độ vùng ngực T7-T10).',
                         'Đo chiều cao hai mào chậu tương đối cân bằng (loại trừ vẹo cột sống chức năng do chênh lệch '
                         'chiều dài hai chân), đường dây dọi thả từ gai sống cổ C7 rơi lệch sang phải so với rãnh liên '
                         'mông 2,5cm (mất cân bằng thân mình), khám thần kinh hai chi dưới phản xạ bụng và phản xạ gân '
                         'gối bình thường.',
                         'Nữ sinh 13 tuổi có đường cong kép ngực phải - thắt lưng trái hình chữ S rõ rệt khi nhìn sau '
                         'lưng, không có bớt sắc tố cà phê sữa hay u xơ thần kinh trên da, không có chùm lông bất '
                         'thường vùng thắt lưng.',
                         'Nhìn nghiêng thấy tăng độ gù nhẹ vùng cột sống ngực trên kèm vai tròn đổ về trước (gù vẹo '
                         'phối hợp), nghiệm pháp Adams dương tính với độ xoay thân mình vùng thắt lưng trái 6 độ.',
                         'Khám cột sống ở tư thế nằm sấp đường cong cột sống vẫn không thẳng lại hoàn toàn (xác nhận '
                         'vẹo cột sống cấu trúc thực sự), sức cơ tứ chi 5/5 không có dấu hiệu tổn thương tủy sống.',
                         'Thử nghiệm tầm vận động cột sống dẻo dai không hạn chế đau cấp, bệnh nhân có kinh nguyệt lần '
                         'đầu cách đây 6 tháng (giai đoạn tăng trưởng xương còn mạnh dễ tiến triển độ cong).'],
    'chan_doan': 'Vẹo cột sống ngực thắt lưng vô căn tuổi thiếu niên (AIS) đường cong kép hình chữ S.',
    'chinh': [   'lệch trục cột sống cong hình chữ S hoặc chữ C nhìn rõ từ phía sau kèm mất cân đối hai bên vai (một '
                 'bên vai cao hơn bên kia) và một bên xương bả vai nhô gồ ra sau',
                 'nghiệm pháp cúi người về phía trước (Adams forward bend test) bộc lộ rõ một bên lồng ngực lưng hoặc '
                 'thắt lưng nổi gồ lên thành bướu sườn bất đối xứng',
                 'khoảng cách tam giác eo giữa hai cánh tay thả lỏng và hai bên hông không đều nhau kèm lệch hông chậu '
                 'một bên cao thấp'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang toàn bộ cột sống thẳng và nghiêng ở tư thế đứng trên phim dài (EOS hoặc phim ghép toàn '
                'trục cột sống từ chẩm đến khớp háng) để đo chính xác góc vẹo Cobb, góc gù ngực, đánh giá độ trưởng '
                'thành xương (chỉ số Risser tại mào chậu) và loại trừ dị tật đốt sống bẩm sinh.',
    'kham': 'Quan sát từ phía sau ở tư thế đứng thẳng: vai phải cao hơn vai trái 2cm, góc dưới xương bả vai phải nhô '
            'cao và đẩy ra sau hơn bên trái, rãnh eo bên trái sâu lõm hơn bên phải; làm nghiệm pháp cúi gập thân mình '
            'về trước (Adams test) thấy gồ lồng ngực lưng bên phải rõ rệt (đo thước đo độ nghiêng Scoliometer đạt 8 độ '
            'vùng ngực T7-T10).',
    'nhom': 'cả hai',
    'phu': [   'thường phát hiện tình cờ ở tuổi tiền dậy thì và dậy thì (10-16 tuổi) khi mặc áo đồng phục hoặc đi bơi',
               'đa số giai đoạn đầu không đau nhức lưng nhiều mà chủ yếu gây mất thẩm mỹ biến dạng thân mình và mỏi '
               'lưng khi ngồi học lâu',
               'nếu độ cong vẹo tiến triển nặng góc Cobb trên 45-50 độ có thể gây gù vẹo chèn ép giảm dung tích hô hấp '
               'tim phổi'],
    'ten': 'gù vẹo cột sống ngực thắt lưng thiếu niên'},
    {   'bien_the_chan_doan': [   'Trượt đốt sống thắt lưng L4-L5 ra trước độ 1 (dưới 25% bề rộng thân đốt) thể thoái hóa.',
                              'Trượt đốt sống L5-S1 độ 1 do khuyết eo cung sau (Spondylolysis) ở người trưởng thành.',
                              'Trượt đốt sống thắt lưng độ 1 gây đau thắt lưng cơ học chưa có biến chứng chèn ép rễ '
                              'nặng.',
                              'Trượt thân đốt sống L4-L5 độ 1 mức độ nhẹ đáp ứng tốt với tập vật lý trị liệu lõi.',
                              'Trượt đốt sống thắt lưng độ 1 kèm co cứng cơ gân kheo và đau khi ưỡn lưng.',
                              'Theo dõi trượt đốt sống thắt lưng độ 1 cần chụp X-quang động gập duỗi đánh giá mất '
                              'vững.'],
    'bien_the_ke_hoach': [   'Chụp X-quang cột sống thắt lưng thẳng, nghiêng và đặc biệt hai phim tư thế động (cúi tối '
                             'đa và ưỡn tối đa - flexion/extension views) để đo tỷ lệ trượt (độ 1 là trượt < 25% thân '
                             'đốt sống) và đánh giá mức độ mất vững cột sống; chụp thêm tư thế chếch 3/4 nếu nghi ngờ '
                             'khuyết eo (hình ảnh gãy cổ chó Scotty).',
                             'Chỉ định chụp MRI cột sống thắt lưng nếu bệnh nhân có triệu chứng đau tê lan xuống chân '
                             'kiểu rễ thần kinh để đánh giá độ hẹp lỗ liên hợp và tình trạng đĩa đệm kèm theo.',
                             'Điều trị bảo tồn là ưu tiên hàng đầu cho trượt đốt sống độ 1 không mất vững nặng: xây '
                             'dựng chương trình tập vật lý trị liệu chuyên biệt tập mạnh nhóm cơ lõi ổn định cột sống '
                             '(core stabilization: cơ ngang bụng, cơ đa gai) ở tư thế trung tính hoặc hơi gập (bài tập '
                             'Williams flexion exercises) và kéo giãn nhẹ cơ gân kheo.',
                             'Tuyệt đối tránh các động tác ưỡn ngửa cột sống quá mức (như tư thế rắn hổ mang trong '
                             'yoga, uốn dẻo lưng) và tránh mang vác vật nặng còng lưng.',
                             'Dùng thuốc giảm đau kháng viêm NSAID ngắn ngày kết hợp thuốc giãn cơ (Eperisone) trong '
                             'đợt đau cấp, cân nhắc đeo đai lưng cột sống mềm hỗ trợ tạm thời khi phải đứng lâu hoặc '
                             'đi xa (không đeo liên tục suốt ngày gây yếu cơ lưng).',
                             'Theo dõi định kỳ mỗi 6 tháng; chỉ hội chẩn Ngoại Thần kinh Cột sống phẫu thuật cố định '
                             'hàn xương nếu đau dữ dội kháng trị bảo tồn trên 6 tháng hoặc tiến triển sang trượt độ '
                             '2-3 kèm chèn ép rễ thần kinh nặng.'],
    'bien_the_kham': [   'Khám cột sống thắt lưng ở tư thế đứng thấy tăng ưỡn nhẹ vùng thắt lưng dưới, sờ dọc theo '
                         'đường gai sau đốt sống phát hiện dấu hiệu bậc thang lõm nhẹ tại khe L4-L5, ấn trực tiếp vào '
                         'gai sau L4 đau tức vừa; động tác ưỡn ngửa cột sống thắt lưng ra sau (extension) gây đau tăng '
                         'rõ rệt, còn cúi gập trước dễ chịu hơn.',
                         'Cơ cạnh sống thắt lưng hai bên hơi co cứng nhẹ, nghiệm pháp đứng một chân ngửa lưng (Stork '
                         'test) dương tính gây đau khu trú vùng thắt lưng thấp bên phải, sức cơ tứ chi 5/5 và phản xạ '
                         'gân xương hai chân đều bình thường.',
                         'Nghiệm pháp nâng thẳng chân Lasegue hai bên không đau rễ thần kinh rõ nhưng bộc lộ tình '
                         'trạng căng cứng ngắn nhóm cơ gân kheo mặt sau đùi hai bên ở góc 70 độ.',
                         'Bệnh nhân nữ 54 tuổi đau thắt lưng mạn tính 2 năm nay tăng khi đứng nấu bếp lâu, khám không '
                         'có mất cảm giác hay teo cơ cẳng chân, khi nằm ngửa co hai gối lên bụng thì hết đau lưng '
                         'ngay.',
                         'Khám thần kinh chi dưới ghi nhận tê nhẹ mu bàn chân bên trái thoáng qua khi đứng lâu, không '
                         'có dấu hiệu yếu gấp mu bàn chân hay bàn chân rủ, mạch mu chân hai bên bắt rõ.',
                         'Đánh giá dáng đi bình thường trên quãng đường ngắn, bệnh nhân không cần chống gậy, không có '
                         'mất kiểm soát tiểu tiện hay tê vùng tầng sinh môn.'],
    'chan_doan': 'Trượt đốt sống thắt lưng L4-L5 ra trước độ 1 (dưới 25% bề rộng thân đốt) thể thoái hóa.',
    'chinh': [   'đau âm ỉ vùng thắt lưng dưới lan tỏa sang hai bên mông hoặc mặt sau đùi tăng lên rõ rệt khi đứng lâu '
                 'đi bộ hoặc ưỡn ngửa lưng ra sau',
                 'cơn đau thắt lưng giảm bớt đáng kể khi ngồi nghỉ cúi gập người về trước hoặc nằm co gối',
                 'sờ dọc các gai sau đốt sống thắt lưng có thể cảm nhận một bậc thang lõm nhẹ bất thường tại đoạn '
                 'L4-L5 hoặc L5-S1'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chụp X-quang cột sống thắt lưng thẳng, nghiêng và đặc biệt hai phim tư thế động (cúi tối đa và ưỡn '
                'tối đa - flexion/extension views) để đo tỷ lệ trượt (độ 1 là trượt < 25% thân đốt sống) và đánh giá '
                'mức độ mất vững cột sống; chụp thêm tư thế chếch 3/4 nếu nghi ngờ khuyết eo (hình ảnh gãy cổ chó '
                'Scotty).',
    'kham': 'Khám cột sống thắt lưng ở tư thế đứng thấy tăng ưỡn nhẹ vùng thắt lưng dưới, sờ dọc theo đường gai sau '
            'đốt sống phát hiện dấu hiệu bậc thang lõm nhẹ tại khe L4-L5, ấn trực tiếp vào gai sau L4 đau tức vừa; '
            'động tác ưỡn ngửa cột sống thắt lưng ra sau (extension) gây đau tăng rõ rệt, còn cúi gập trước dễ chịu '
            'hơn.',
    'nhom': 'người lớn',
    'phu': [   'cứng mỏi vùng thắt lưng vào buổi sáng hoặc sau khi ngồi lâu một tư thế rồi đứng dậy',
               'cơ gân kheo (mặt sau đùi) hai bên thường bị co cứng căng chặt khi gập người chạm tay xuống đất',
               'có thể kèm tê bì râm ran nhẹ theo rễ thần kinh L5 hoặc S1 xuống cẳng bàn chân khi đi lại nhiều nhưng '
               'chưa yếu liệt nặng'],
    'ten': 'trượt đốt sống thắt lưng độ 1'},
    {   'bien_the_chan_doan': [   'Hẹp ống sống thắt lưng thoái hóa tầng L4-L5 gây hội chứng đau cách hồi thần kinh điển '
                              'hình.',
                              'Hẹp ống sống thắt lưng thoái hóa đa tầng ở người cao tuổi mức độ trung bình.',
                              'Hẹp ống sống thắt lưng trung tâm và ngách bên hai bên do phì đại dây chằng vàng và '
                              'thoái hóa khớp liên mấu.',
                              'Hẹp ống sống thắt lưng thoái hóa giai đoạn chưa có yếu liệt vận động nặng hay rối loạn '
                              'cơ tròn.',
                              'Theo dõi hẹp ống sống thắt lưng thoái hóa cần phân biệt với bệnh động mạch ngoại biên '
                              'chi dưới.',
                              'Hẹp ống sống thắt lưng thoái hóa cần chụp MRI cột sống đánh giá mức độ hẹp ống sống.'],
    'bien_the_ke_hoach': [   'Chỉ định chụp cộng hưởng từ (MRI) cột sống thắt lưng đánh giá chi tiết mức độ hẹp ống '
                             'sống trung tâm (đường kính trước sau < 10-12mm, mất dịch não tủy quanh chùm rễ đuôi '
                             'ngựa), hẹp ngách bên, phì đại dây chằng vàng, lồi đĩa đệm và thoái hóa khớp liên mấu đa '
                             'tầng; đo siêu âm Doppler động mạch chi dưới hoặc chỉ số ABI nếu cần loại trừ bệnh động '
                             'mạch ngoại biên phối hợp.',
                             'Chụp X-quang cột sống thắt lưng thẳng nghiêng và động cúi-ưỡn để đánh giá xem có trượt '
                             'đốt sống mất vững kèm theo hẹp ống sống hay không.',
                             'Điều trị bảo tồn cho mức độ nhẹ-vừa: hướng dẫn tập vật lý trị liệu tư thế gập (Williams '
                             'flexion exercises), đạp xe đạp tĩnh tại chỗ, bơi lội giúp mở rộng đường kính ống sống và '
                             'tăng sức bền cơ bụng lưng.',
                             'Dùng thuốc giảm đau thần kinh (Gabapentin hoặc Pregabalin) kiểm soát cảm giác tê buốt '
                             'nặng chân, kết hợp NSAID ngắn ngày hoặc Paracetamol trong đợt đau tăng; tư vấn dùng gậy '
                             'hoặc khung đẩy hỗ trợ đi bộ nếu cần.',
                             'Cân nhắc thủ thuật tiêm Corticoid ngoài màng cứng thắt lưng (Epidural steroid injection) '
                             'dưới màn tăng sáng đối với các đợt đau lan rễ nặng kéo dài giúp giảm viêm phù nề rễ thần '
                             'kinh tạm thời.',
                             'Hội chẩn Ngoại Thần kinh Cột sống phẫu thuật giải ép ống sống (cắt bản sống giải ép tối '
                             'thiểu hoặc mở cửa sổ xương cắt dây chằng vàng, kèm hàn xương nếu có mất vững trượt đốt '
                             'sống) khi quãng đường đi bộ giảm dưới 50-100m ảnh hưởng nặng chất lượng sống hoặc xuất '
                             'hiện yếu chân tiến triển/rối loạn cơ tròn.'],
    'bien_the_kham': [   'Bệnh nhân 66 tuổi đi vào phòng khám với tư thế thân mình hơi cúi khom nhẹ về phía trước '
                         '(dáng đi vượn), khai chỉ đi bộ khoảng 150 mét là hai bắp chân nặng trĩu như đeo chì kèm tê '
                         'râm ran xuống lòng bàn chân phải ngồi xuống ghế đá nghỉ 5 phút mới đi tiếp được; khám tại '
                         'giường lúc nghỉ: nghiệm pháp Lasegue âm tính hai bên, sức cơ 5/5 nhưng giảm nhẹ phản xạ gân '
                         'gót hai bên, mạch mu chân và chày sau bắt rất rõ đều (loại trừ tắc động mạch chi dưới).',
                         'Khi yêu cầu bệnh nhân đứng thẳng và ưỡn nhẹ cột sống thắt lưng ra sau giữ trong 45 giây '
                         '(Extension test) làm tái hiện ngay cảm giác tê mỏi nặng dọc hai mông lan xuống hai bắp chân, '
                         'sau đó cho bệnh nhân ngồi cúi gập người về trước thì hết tê ngay sau 1 phút.',
                         'Cột sống thắt lưng giảm độ ưỡn sinh lý và hạn chế rõ động tác ưỡn ngửa ra sau, trong khi '
                         'động tác cúi gập người xuống lại hoàn toàn dễ dàng không gây đau, da hai cẳng bàn chân hồng '
                         'ấm không có loét thiếu máu hay rụng lông.',
                         'Khám chi dưới thấy rối loạn cảm giác nhẹ không theo một rễ đơn thuần mà lan tỏa cả vùng bắp '
                         'chân hai bên (chèn ép đa rễ L4-L5-S1), test Romberg hơi chao đảo nhẹ khi đi lại nhiều.',
                         'Bệnh nhân kể đi xe đạp tập thể dục 30 phút vẫn bình thường nhưng đi bộ siêu thị phải chống '
                         'khuỷu tay tỳ lên xe đẩy hàng khom lưng mới đi hết vòng siêu thị được; khám mạch ngoại vi '
                         'bình thường chỉ số ABI ước lượng tốt.',
                         'Không có rối loạn cơ tròn đại tiểu tiện cấp tính hay tê mất cảm giác vùng yên ngựa (chưa có '
                         'hội chứng chùm đuôi ngựa cấp cứu).'],
    'chan_doan': 'Hẹp ống sống thắt lưng thoái hóa tầng L4-L5 gây hội chứng đau cách hồi thần kinh điển hình.',
    'chinh': [   'đau cách hồi thần kinh (neurogenic claudication): đau nhức nặng mỏi tê bì hai bắp chân và đùi xuất '
                 'hiện sau khi đi bộ được một quãng đường nhất định (ví dụ 100-300m) buộc phải dừng lại',
                 'triệu chứng tê nặng mỏi chân giảm nhanh chóng rõ rệt sau vài phút ngồi xuống nghỉ ngơi hoặc cúi khom '
                 'người về phía trước (như tỳ tay lên xe đẩy siêu thị - dấu hiệu xe đẩy hàng)',
                 'đứng yên thẳng lưng lâu cũng gây đau tê tăng dần xuống hai chân, trong khi đạp xe đạp (tư thế lưng '
                 'hơi gập) lại đi được rất xa mà không bị đau'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Chỉ định chụp cộng hưởng từ (MRI) cột sống thắt lưng đánh giá chi tiết mức độ hẹp ống sống trung tâm '
                '(đường kính trước sau < 10-12mm, mất dịch não tủy quanh chùm rễ đuôi ngựa), hẹp ngách bên, phì đại '
                'dây chằng vàng, lồi đĩa đệm và thoái hóa khớp liên mấu đa tầng; đo siêu âm Doppler động mạch chi dưới '
                'hoặc chỉ số ABI nếu cần loại trừ bệnh động mạch ngoại biên phối hợp.',
    'kham': 'Bệnh nhân 66 tuổi đi vào phòng khám với tư thế thân mình hơi cúi khom nhẹ về phía trước (dáng đi vượn), '
            'khai chỉ đi bộ khoảng 150 mét là hai bắp chân nặng trĩu như đeo chì kèm tê râm ran xuống lòng bàn chân '
            'phải ngồi xuống ghế đá nghỉ 5 phút mới đi tiếp được; khám tại giường lúc nghỉ: nghiệm pháp Lasegue âm '
            'tính hai bên, sức cơ 5/5 nhưng giảm nhẹ phản xạ gân gót hai bên, mạch mu chân và chày sau bắt rất rõ đều '
            '(loại trừ tắc động mạch chi dưới).',
    'nhom': 'người lớn',
    'phu': [   'mạch mu chân và động mạch chày sau vẫn đập rõ mạnh, bàn chân ấm hồng (giúp phân biệt với đau cách hồi '
               'mạch máu)',
               'khám thần kinh lúc nghỉ ngơi tại phòng khám thường ít triệu chứng thực thể nặng hoặc chỉ giảm nhẹ phản '
               'xạ gân gót',
               'thường gặp ở người lớn tuổi trên 55-60 tuổi có thoái hóa cột sống phì đại dây chằng vàng và lồi đĩa '
               'đệm đa tầng'],
    'ten': 'hẹp ống sống thắt lưng thoái hóa'},
]
