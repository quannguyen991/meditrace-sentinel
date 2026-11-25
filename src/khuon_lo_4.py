# -*- coding: utf-8 -*-
"""Khuon benh Lo 4 (50 khuon: 351-400 tu DANH_SACH_UNG_VIEN_CON_LAI[50:100]).

Dam bao:
- Du 10 truong bat buoc + 3 truong bien the (moi truong 6 bien the khac nhau).
- Tuyet doi khong chua chuoi con om, len ban do, dau lon ruot.
- Khong chua tu ngu tre em trong nhom nguoi lon.
- Khop nguyen van danh sach ung vien con lai ve ten, nhom, dien_tien, he_co_quan.
- 0 cap trung lap >= 20% trieu chung giua cac khuon va voi 300 khuon da co.
"""

GIOI_TINH_LO_4 = {
    'viêm teo niêm mạc âm đạo do lão hóa': 'nữ',
    'sa bàng quang độ 2': 'nữ',
    'u tuyến yên tiết prolactin prolactinoma': 'nữ',
    'viêm tuyến tiền liệt mạn tính không do vi khuẩn': 'nam',
    'viêm tuyến tiền liệt cấp do vi khuẩn': 'nam',
    'xoắn tinh hoàn dọa nghẹt': 'nam',
    'tràn dịch màng tinh hoàn người lớn': 'nam',
    'nang mào tinh hoàn': 'nam',
    'viêm bao quy đầu bán cấp do nấm': 'nam',
    'xuất tinh sớm tiên phát': 'nam',
    'vô sinh nam do suy giảm số lượng tinh trùng': 'nam',
    'bệnh cong dương vật Peyronie': 'nam',
    'suy tuyến sinh dục nam muộn mãn dục nam': 'nam',
    'cương cứng dương vật kéo dài thể thiếu máu': 'nam',
    'loãng xương vô căn ở nam giới': 'nam',
}

CHI_NU_LO_4 = {k for k, v in GIOI_TINH_LO_4.items() if v == 'nữ'}
CHI_NAM_LO_4 = {k for k, v in GIOI_TINH_LO_4.items() if v == 'nam'}

BENH_LO_4 = [{'bien_the_chan_doan': ['Sa sút trí tuệ Alzheimer giai đoạn nhẹ.',
                         'Theo dõi sa sút trí tuệ Alzheimer giai đoạn nhẹ khởi phát muộn.',
                         'Sa sút trí tuệ Alzheimer giai đoạn nhẹ chưa có rối loạn hành vi.',
                         'Sa sút trí tuệ Alzheimer giai đoạn nhẹ có kèm lo âu giảm khí sắc.',
                         'Theo dõi sa sút trí tuệ Alzheimer giai đoạn nhẹ bảo tồn chức năng vận động.',
                         'Sa sút trí tuệ Alzheimer giai đoạn nhẹ mức độ suy giảm nhận thức nhẹ.'],
  'bien_the_ke_hoach': ['Chỉ định chụp cộng hưởng từ sọ não đánh giá teo hồi hải mã, làm xét nghiệm TSH và vitamin B12 '
                        'loại trừ căn nguyên thứ phát, bắt đầu dùng thuốc ức chế men cholinesterase donepezil 5mg/ngày '
                        'và tư vấn tập luyện nhận thức.',
                        'Chỉ định chụp MRI não đánh giá thang điểm teo thùy thái dương trong MTA, xét nghiệm bilan sa '
                        'sút trí tuệ, bắt đầu điều trị galantamine và hướng dẫn người nhà ghi nhật ký hành vi.',
                        'Làm xét nghiệm công thức máu sinh hóa đường huyết điện giải chức năng gan thận, chụp MRI sọ '
                        'não, kê đơn donepezil phối hợp bổ sung dưỡng chất thần kinh và duy trì hoạt động xã hội.',
                        'Hẹn làm trắc nghiệm tâm lý thần kinh chuyên sâu toàn diện, xét nghiệm hormone giáp trạng, bắt '
                        'đầu rivastigmine miếng dán ngoài da và tư vấn cải tạo môi trường sống an toàn tại gia đình.',
                        'Xét nghiệm loại trừ nguyên nhân thiếu hụt chuyển hóa, siêu âm Doppler mạch cảnh não, chỉ định '
                        'donepezil 5mg uống buổi tối và tập thể dục nhẹ nhàng rèn luyện thăng bằng.',
                        'Lập hồ sơ quản lý theo dõi trí nhớ ngoại trú, hẹn tái khám sau 4 tuần đánh giá tác dụng phụ '
                        'tiêu hóa của thuốc ức chế cholinesterase, kết hợp trị liệu gợi nhớ quá khứ.'],
  'bien_the_kham': ['Bệnh nhân tiếp xúc tốt, hợp tác nhưng giảm chú ý, thực hiện test MMSE đạt 22/30 điểm, giảm điểm '
                    'phần nhớ lại từ và định hướng ngày tháng, trương lực cơ và phản xạ bình thường không có dấu thần '
                    'kinh khu trú.',
                    'Khám nhận thức ghi nhận suy giảm trí nhớ phân đoạn, điểm MoCA đạt 21/30 mất điểm ở phần vẽ đồng '
                    'hồ và nhắc lại 5 từ, các dây thần kinh sọ nguyên vẹn, dáng đi bình thường.',
                    'Bệnh nhân trả lời chậm, lặp từ, thực hiện bài kiểm tra nhớ tức thời 3 đồ vật không hoàn tất, test '
                    'Mini-Cog 2/5 điểm, phản xạ gân xương hai bên đều không có phản xạ bệnh lý bó tháp.',
                    'Khám lâm sàng thần kinh không thấy liệt vận động, thang điểm đánh giá suy giảm nhận thức lâm sàng '
                    'CDR 0.5-1 điểm, bệnh nhân mất định hướng thời gian nhưng định hướng bản thân còn tốt.',
                    'Thực hiện bài kiểm tra trạng thái tâm thần MMSE 23/30 điểm, quên hoàn toàn các chi tiết vừa trao '
                    'đổi sau 5 phút, khám cảm giác và phối hợp vận động ngón tay chỉ mũi bình thường.',
                    'Bệnh nhân giao tiếp nhã nhặn nhưng hay nhìn sang người nhà nhờ trả lời hộ, test vẽ mặt đồng hồ '
                    'méo lệch kim giờ, khám 12 đôi dây thần kinh sọ không ghi nhận tổn thương khu trú.'],
  'chan_doan': 'Sa sút trí tuệ Alzheimer giai đoạn nhẹ.',
  'chinh': ['suy giảm trí nhớ ngắn hạn hay quên việc vừa xảy ra lặp lại câu hỏi',
            'khó khăn tìm từ ngữ diễn đạt phù hợp hoặc thường xuyên để lẫn đồ đạc',
            'giảm khả năng định hướng không gian và thời gian ở nơi quen thuộc'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Chỉ định chụp cộng hưởng từ sọ não đánh giá teo hồi hải mã, làm xét nghiệm TSH và vitamin B12 loại trừ '
              'căn nguyên thứ phát, bắt đầu dùng thuốc ức chế men cholinesterase donepezil 5mg/ngày và tư vấn tập '
              'luyện nhận thức.',
  'kham': 'Bệnh nhân tiếp xúc tốt, hợp tác nhưng giảm chú ý, thực hiện test MMSE đạt 22/30 điểm, giảm điểm phần nhớ '
          'lại từ và định hướng ngày tháng, trương lực cơ và phản xạ bình thường không có dấu thần kinh khu trú.',
  'nhom': 'người lớn',
  'phu': ['thay đổi tính tình thu mình ngại giao tiếp xã hội',
          'khó khăn khi xử lý các công việc tài chính chi tiêu hàng ngày',
          'giảm khả năng phán đoán và giải quyết các tình huống thông thường'],
  'ten': 'sa sút trí tuệ Alzheimer giai đoạn nhẹ'},
 {'bien_the_chan_doan': ['Hội chứng suy yếu dễ tổn thương ở người già mức độ trung bình.',
                         'Theo dõi hội chứng suy yếu dễ tổn thương ở người già có teo cơ sinh lý.',
                         'Hội chứng suy yếu dễ tổn thương ở người già nguy cơ ngã cao.',
                         'Hội chứng suy yếu dễ tổn thương ở người già kèm suy dinh dưỡng năng lượng.',
                         'Theo dõi hội chứng suy yếu dễ tổn thương ở người già giảm sức bền thể lực.',
                         'Hội chứng suy yếu dễ tổn thương ở người già giai đoạn tiến triển.'],
  'bien_the_ke_hoach': ['Thực hiện đánh giá lão khoa toàn diện CGA, xây dựng chế độ dinh dưỡng giàu năng lượng và '
                        'protein 1.2-1.5 g/kg/ngày, tập vật lý trị liệu phục hồi cơ lực kháng lực nhẹ và rà soát cắt '
                        'giảm đa thuốc.',
                        'Hội chẩn chuyên khoa dinh dưỡng bổ sung sữa cao năng lượng giàu đạm và vitamin D, thiết kế '
                        'bài tập thể dục thăng bằng kháng lực nhẹ hàng ngày, hướng dẫn phòng ngừa vấp ngã tại nhà.',
                        'Xét nghiệm albumin máu prealbumin điện giải đồ và 25-OH-vitamin D, bổ sung canxi và vitamin D '
                        'đường uống, hướng dẫn người nhà hỗ trợ tập vận động thích nghi.',
                        'Lập kế hoạch can thiệp lão khoa đa mô thức, điều chỉnh lại danh mục các thuốc đang dùng để '
                        'giảm thiểu mệt mỏi, tư vấn bài tập tăng cường sức cơ gốc chi.',
                        'Bổ sung khẩu phần ăn chia nhỏ nhiều bữa trong ngày, tập đi bộ có giám sát 15 phút mỗi ngày, '
                        'xét nghiệm đánh giá thiếu máu và chức năng tuyến giáp.',
                        'Tư vấn người chăm sóc về hỗ trợ sinh hoạt hàng ngày ADL và IADL, theo dõi cân nặng định kỳ '
                        'mỗi 2 tuần, khám chuyên khoa phục hồi chức năng vận động.'],
  'bien_the_kham': ['Thể trạng gầy, cơ bắp teo nhẽo tứ chi, đo lực nắm bàn tay đạt 21kg ở nam giới (dưới ngưỡng '
                    'chuẩn), tốc độ đi bộ 4 mét đạt 0.72 m/s, đánh giá theo tiêu chuẩn Fried thỏa mãn 4/5 tiêu chí hội '
                    'chứng suy yếu.',
                    'Bệnh nhân gầy sút, chỉ số khối cơ thể BMI 18.2 kg/m2, bước đi chậm chạp chân đế rộng, lực bóp bàn '
                    'tay yếu cả hai bên, thang điểm CFS (Clinical Frailty Scale) mức độ 5.',
                    'Khám thấy teo các nhóm cơ quanh vai và cẳng chân, đi bộ 4m mất 6.2 giây, sức bền giảm nhanh khi '
                    'vận động nhẹ, thang điểm Edmonton Frailty Scale đạt 8 điểm suy yếu rõ.',
                    'Bệnh nhân di chuyển khó khăn vào phòng khám, cơ tứ đầu đùi teo nhẹ, nghiệm pháp đứng lên ngồi '
                    'xuống 5 lần mất 18 giây, tiêu chuẩn Fried đạt 3 tiêu chí dương tính.',
                    'Thể trạng teo cơ giảm dự trữ sinh lý, lực kế cầm tay giảm sâu hai bên, da khô niêm mạc nhạt màu '
                    'vừa, không có dấu hiệu suy tim ứ huyết hay suy hô hấp.',
                    'Đo sức bóp cơ tay giảm dưới bách phân vị thứ 20, tốc độ di chuyển chậm, thang điểm đánh giá nguy '
                    'cơ suy kiệt đa cơ quan đạt mức nguy cơ cao cần can thiệp.'],
  'chan_doan': 'Hội chứng suy yếu dễ tổn thương ở người già mức độ trung bình.',
  'chinh': ['sụt cân không chủ đích trên 4.5kg trong vòng một năm qua',
            'cảm giác kiệt sức mệt mỏi thường xuyên khi thực hiện sinh hoạt',
            'tốc độ đi bộ chậm chạp và giảm sức nắm bàn tay rõ rệt'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Thực hiện đánh giá lão khoa toàn diện CGA, xây dựng chế độ dinh dưỡng giàu năng lượng và protein '
              '1.2-1.5 g/kg/ngày, tập vật lý trị liệu phục hồi cơ lực kháng lực nhẹ và rà soát cắt giảm đa thuốc.',
  'kham': 'Thể trạng gầy, cơ bắp teo nhẽo tứ chi, đo lực nắm bàn tay đạt 21kg ở nam giới (dưới ngưỡng chuẩn), tốc độ '
          'đi bộ 4 mét đạt 0.72 m/s, đánh giá theo tiêu chuẩn Fried thỏa mãn 4/5 tiêu chí hội chứng suy yếu.',
  'nhom': 'người lớn',
  'phu': ['mức độ hoạt động thể lực hàng ngày giảm sút nhiều ít vận động',
          'khó khăn khi tự đứng dậy khỏi ghế mà không dùng hai tay chống đỡ',
          'thường xuyên cảm thấy yếu sức và dễ choáng váng khi di chuyển'],
  'ten': 'hội chứng suy yếu dễ tổn thương ở người già'},
 {'bien_the_chan_doan': ['Ngã tái diễn ở người cao tuổi do rối loạn thăng bằng và hạ huyết áp tư thế.',
                         'Theo dõi ngã tái diễn ở người cao tuổi liên quan tác dụng phụ của thuốc.',
                         'Ngã tái diễn ở người cao tuổi do thoái hóa khớp gối và suy giảm thị lực.',
                         'Ngã tái diễn ở người cao tuổi nguy cơ cao chấn thương gãy xương.',
                         'Theo dõi ngã tái diễn ở người cao tuổi rối loạn dáng đi tuổi già.',
                         'Ngã tái diễn ở người cao tuổi thể đa yếu tố nguy cơ nội sinh và ngoại sinh.'],
  'bien_the_ke_hoach': ['Đo điện tâm đồ Holter 24 giờ tầm soát rối loạn nhịp tim chậm, khám chuyên khoa mắt chỉnh kính '
                        'đục thủy tinh thể, giảm liều thuốc hạ huyết áp, tập phục hồi thăng bằng với khung tập đi và '
                        'rà soát an toàn nhà ở gỡ bỏ thảm trơn.',
                        'Chỉ định đo mật độ xương DEXA tầm soát loãng xương phòng gãy xương cổ xương đùi, hướng dẫn '
                        'dùng gậy chống ba chân trợ lực, tập các bài tập thăng bằng Otaga.',
                        'Rà soát ngưng các thuốc an thần benzodiazepine gây ngủ ngày, hướng dẫn bệnh nhân ngồi dậy từ '
                        'từ tại mép giường 2 phút trước khi đứng, lắp tay vịn trong nhà vệ sinh.',
                        'Khám chuyên khoa mắt đo thị lực điều trị đục thủy tinh thể, bổ sung vitamin D3 liều thích hợp '
                        'tăng sức cơ, đo điện cơ chi dưới đánh giá bệnh lý dây thần kinh ngoại biên.',
                        'Tập vật lý trị liệu phục hồi dáng đi và phản xạ thăng bằng, mang giày đế bằng có độ bám tốt, '
                        'kiểm tra ánh sáng phòng ngủ và hành lang vào ban đêm.',
                        'Siêu âm tim và Doppler động mạch cảnh loại trừ cơn thiếu máu não thoáng qua hoặc hẹp van động '
                        'mạch chủ gây ngất ngã, hẹn tái khám định kỳ sau 1 tháng.'],
  'bien_the_kham': ['Nghiệm pháp Timed Up and Go (TUG) thực hiện mất 17 giây (nguy cơ ngã cao), huyết áp tư thế nằm '
                    '135/85 mmHg và đứng sau 3 phút 112/70 mmHg (hạ áp tư thế), dáng đi lê bước ngắn, thị lực hai mắt '
                    'giảm vừa.',
                    'Nghiệm pháp Romberg dương tính lắc lư khi nhắm mắt, bài test TUG mất 16 giây, giảm phản xạ gân '
                    'gót hai bên, khớp gối thoái hóa kêu lạo xạo nhẹ khi vận động.',
                    'Đo huyết áp có biến thiên tư thế tụt huyết áp tâm thu 24 mmHg khi đứng dậy, phối hợp vận động tay '
                    'chân hơi vụng về, test thăng bằng Berg đạt 38/56 điểm có nguy cơ té ngã.',
                    'Dáng đi chậm bước chân không nhấc cao khỏi mặt đất, chân đế rộng, xoay người lúng túng mất thăng '
                    'bằng, thính lực và thị giác suy giảm mức độ trung bình.',
                    'Khám chức năng thăng bằng tiền đình ngoại biên không rung giật nhãn cầu tự phát, test đứng một '
                    'chân không giữ được quá 3 giây, các khớp chi dưới không sưng nóng đỏ.',
                    'Bệnh nhân có biểu hiện rụt rè lo sợ khi bước đi, TUG test kéo dài 18 giây, hạ huyết áp tư thế '
                    'đứng rõ rệt kèm hoa mắt thoáng qua, nhịp tim xoang đều 70 ck/p.'],
  'chan_doan': 'Ngã tái diễn ở người cao tuổi do rối loạn thăng bằng và hạ huyết áp tư thế.',
  'chinh': ['tiền sử té ngã từ 2 lần trở lên trong vòng 6 tháng gần đây',
            'cảm giác lảo đảo mất thăng bằng khi đứng lên hoặc khi quay đầu',
            'nỗi sợ bị ngã thường trực dẫn đến hạn chế việc đi lại vận động'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Đo điện tâm đồ Holter 24 giờ tầm soát rối loạn nhịp tim chậm, khám chuyên khoa mắt chỉnh kính đục thủy '
              'tinh thể, giảm liều thuốc hạ huyết áp, tập phục hồi thăng bằng với khung tập đi và rà soát an toàn nhà '
              'ở gỡ bỏ thảm trơn.',
  'kham': 'Nghiệm pháp Timed Up and Go (TUG) thực hiện mất 17 giây (nguy cơ ngã cao), huyết áp tư thế nằm 135/85 mmHg '
          'và đứng sau 3 phút 112/70 mmHg (hạ áp tư thế), dáng đi lê bước ngắn, thị lực hai mắt giảm vừa.',
  'nhom': 'người lớn',
  'phu': ['choáng váng thoáng qua khi thay đổi tư thế từ nằm sang đứng',
          'giảm thị lực nhìn mờ do đục thủy tinh thể hoặc tật khúc xạ tuổi già',
          'đang dùng các thuốc gây buồn ngủ an thần hoặc thuốc lợi tiểu'],
  'ten': 'ngã tái diễn ở người cao tuổi'},
 {'bien_the_chan_doan': ['Loét tì đè độ 1-2 vùng cùng cụt ở người già do bất động kéo dài.',
                         'Theo dõi loét tì đè độ 1-2 vùng cùng cụt ở người già sau di chứng tai biến.',
                         'Loét tì đè độ 1-2 vùng cùng cụt ở người già có nguy cơ nhiễm trùng tại chỗ.',
                         'Loét tì đè độ 1-2 vùng cùng cụt ở người già giai đoạn mô hạt đang lành.',
                         'Theo dõi loét tì đè độ 1-2 vùng cùng cụt ở người già kèm tiêu tiểu không tự chủ.',
                         'Loét tì đè độ 1-2 vùng cùng cụt ở người già thể trợt nông thượng bì.'],
  'bien_the_ke_hoach': ['Chăm sóc vết loét hàng ngày rửa bằng nước muối sinh lý vô trùng đắp gạc hydrocolloid giữ ẩm '
                        'bảo vệ nền mô hạt, sử dụng đệm hơi luân chuyển áp lực, đổi tư thế nằm nghiêng trái nghiêng '
                        'phải mỗi 2 giờ, nâng cao dinh dưỡng tăng cường chất đạm.',
                        'Rửa vết trợt loét bằng dung dịch NaCl 0.9% ấm, đắp gạc foam xốp thấm hút bảo vệ da, hướng dẫn '
                        'người chăm sóc lăn trở bệnh nhân đúng kỹ thuật và kê gối mềm giảm áp lực tì đè.',
                        'Sử dụng màng phim trong suốt dán bảo vệ vùng da đỏ độ 1, bôi kem kẽm oxyd bảo vệ da khỏi phân '
                        'và nước tiểu, cho nằm đệm chống loét khí múi, bổ sung kẽm và vitamin C.',
                        'Thay băng cách ngày bằng gạc xốp tẩm nano bạc nếu có nguy cơ nhiễm khuẩn nhẹ, tránh dùng cồn '
                        'hoặc povidone iod đậm đặc làm tổn hại mô hạt non, kiểm tra dinh dưỡng albumin máu.',
                        'Tập vận động thụ động các khớp tại giường tránh cứng khớp, hướng dẫn chế độ ăn giàu đạm thịt '
                        'trứng sữa giúp tái tạo tổ chức biểu mô, giữ da vùng bẹn mông luôn khô thoáng sạch sẽ.',
                        'Theo dõi sát kích thước vết loét và lượng dịch tiết mỗi tuần, lập bảng theo dõi giờ lăn trở '
                        'tư thế tại giường bệnh, tham vấn bác sĩ ngoại khoa khi có dấu hiệu ăn sâu hoại tử.'],
  'bien_the_kham': ['Khám vùng da xương cùng cụt có mảng đỏ kích thước 4x5cm ấn không mất màu, ở trung tâm có vết trợt '
                    'nông mất lớp thượng bì kích thước 2x2.5cm đáy đỏ hồng sạch chưa lộ lớp mỡ dưới da, không có mô '
                    'hoại tử đen, rìa vết loét cương tụ phù nhẹ (loét độ 2 theo NPUAP).',
                    'Vùng xương cùng có tổn thương bọng nước trợt vỡ kích thước 3x3cm nền đỏ rỉ ít dịch thanh dịch, bờ '
                    'vết thương rõ, không có mủ hôi, xung quanh da sung huyết không đổi màu khi ấn kính (loét tì đè độ '
                    '2).',
                    'Quan sát vùng ụ cùng có mảng hồng ban thâm nhiễm ấn không chuyển màu trắng, da nguyên vẹn nhưng '
                    'ấm nóng nhẹ và ấn tức rõ rệt (loét tì đè độ 1 theo phân loại quốc tế).',
                    'Vết loét trợt nông biểu bì đáy vết thương đỏ tươi có mô hạt mới hình thành, không thâm nhiễm sâu '
                    'đến lớp cân cơ, dịch tiết ít không mùi, vùng da lân cận ẩm ướt nhẹ.',
                    'Tổn thương da vùng xương cùng cụt dạng trợt nông biểu mô diện tích khoảng 6cm2, bờ nhẵn, đáy hồng '
                    'không có giả mạc hoại tử, cảm giác đau tại chỗ giảm do bệnh lý thần kinh ngoại vi.',
                    'Khám vùng tì đè mông phát hiện vết xước loét mất lớp da trên bề mặt đường kính 2.5cm, rỉ dịch '
                    'nhẹ, không có ngóc ngách dò hốc sâu, da bao quanh đỏ ửng lan rộng.'],
  'chan_doan': 'Loét tì đè độ 1-2 vùng cùng cụt ở người già do bất động kéo dài.',
  'chinh': ['vùng da xương cùng cụt đỏ ửng cương tụ ấn ngón tay không mất màu',
            'xuất hiện vết trợt nông thượng bì hoặc bọng nước vỡ rỉ dịch trên nền da đỏ',
            'đau rát khó chịu vùng mông khi nằm ngửa liên tục trên mặt phẳng'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Chăm sóc vết loét hàng ngày rửa bằng nước muối sinh lý vô trùng đắp gạc hydrocolloid giữ ẩm bảo vệ nền '
              'mô hạt, sử dụng đệm hơi luân chuyển áp lực, đổi tư thế nằm nghiêng trái nghiêng phải mỗi 2 giờ, nâng '
              'cao dinh dưỡng tăng cường chất đạm.',
  'kham': 'Khám vùng da xương cùng cụt có mảng đỏ kích thước 4x5cm ấn không mất màu, ở trung tâm có vết trợt nông mất '
          'lớp thượng bì kích thước 2x2.5cm đáy đỏ hồng sạch chưa lộ lớp mỡ dưới da, không có mô hoại tử đen, rìa vết '
          'loét cương tụ phù nhẹ (loét độ 2 theo NPUAP).',
  'nhom': 'người lớn',
  'phu': ['người bệnh nằm bất động tại giường thời gian dài do tai biến hoặc suy kiệt',
          'tiểu tiện hoặc đại tiện không tự chủ làm ẩm ướt vùng da quanh mông',
          'thể trạng gầy da khô mỏng kèm giảm cảm giác đau tại chỗ'],
  'ten': 'loét tì đè độ 1-2 vùng cùng cụt ở người già'},
 {'bien_the_chan_doan': ['Hạ natri máu mạn tính ở người cao tuổi theo dõi do thuốc hoặc SIADH.',
                         'Hạ natri máu mạn tính ở người cao tuổi mức độ trung bình có triệu chứng dáng đi.',
                         'Theo dõi hạ natri máu mạn tính ở người cao tuổi liên quan thuốc lợi tiểu thiazide.',
                         'Hạ natri máu mạn tính ở người cao tuổi thể đồng thể tích máu.',
                         'Hạ natri máu mạn tính ở người cao tuổi tái diễn sau đợt viêm phổi.',
                         'Theo dõi hạ natri máu mạn tính ở người cao tuổi hội chứng tăng tiết ADH không thích hợp.'],
  'bien_the_ke_hoach': ['Xét nghiệm điện giải đồ máu và niệu, đo áp lực thẩm thấu máu và áp lực thẩm thấu nước tiểu, '
                        'ngừng thuốc lợi tiểu nghi ngờ, hạn chế lượng dịch uống vào khoảng 1000ml/ngày, bù natri đường '
                        'uống từ từ điều chỉnh nồng độ natri tăng không quá 8 mmol/l trong 24 giờ để phòng hủy myelin '
                        'cầu não.',
                        'Làm bilan xét nghiệm chức năng tuyến giáp và cortisol huyết thanh loại trừ suy giáp suy '
                        'thượng thận, ngưng nhóm thuốc SSRI đang dùng, bù viên muối natri clorid theo dõi ion đồ mỗi '
                        'ngày.',
                        'Hạn chế nước tự do 800-1000 ml/ngày, cho chế độ ăn tăng thêm chút muối súp, đo natri máu cách '
                        '12 giờ một lần kiểm soát tốc độ tăng natri an toàn.',
                        'Xét nghiệm axit uric máu (giảm trong SIADH), chụp X-quang phổi và CT sọ não tìm nguyên nhân '
                        'kích thích tiết ADH, bổ sung natri viên uống chia 3 lần.',
                        'Theo dõi sát tri giác và thang điểm Glasgow, bù dịch muối sinh lý đẳng trương NaCl 0.9% tốc '
                        'độ chậm nếu có giảm thể tích kèm theo, hẹn tái khám sau 3 ngày.',
                        'Tư vấn người nhà theo dõi lượng nước uống và lượng nước tiểu 24 giờ, tránh truyền dịch nhược '
                        'trương đường dextrose, điều chỉnh các thuốc tim mạch phối hợp.'],
  'bien_the_kham': ['Bệnh nhân tỉnh táo nhưng tiếp xúc chậm chạp, niêm mạc miệng ẩm vừa, không có phù ngoại biên hai '
                    'chân, tĩnh mạch cổ không nổi ở tư thế 45 độ, nhịp tim đều 72 ck/p, huyết áp 125/80 mmHg, khám '
                    'thần kinh không thấy dấu hiệu liệt khu trú.',
                    'Khám thể trạng bình thường không thiếu dịch cũng không thừa dịch, véo da âm tính, huyết áp tư thế '
                    'ổn định, phản xạ gân xương giảm nhẹ tứ chi, không rung giật cơ.',
                    'Bệnh nhân trả lời nhát gừng đờ đẫn nhẹ, da ấm không khô ráp, gõ bụng trong không cổ trướng, tim '
                    'đều T1 T2 rõ, xét nghiệm natri huyết thanh tại chỗ đo được 124 mmol/l.',
                    'Dáng đi hơi lảo đảo chệch choạc nhẹ khi nhắm mắt, khám đáy mắt bình thường không phù gai thị, '
                    'không có dấu hiệu màng não cổ cứng, sinh hiệu ổn định.',
                    'Bệnh nhân chậm chạp nhưng định hướng bản thân tốt, không phù mặt không phù mu bàn chân, trương '
                    'lực cơ giảm nhẹ toàn thân, các dây thần kinh sọ không liệt.',
                    'Khám tuần hoàn và hô hấp trong giới hạn bình thường, áp lực tĩnh mạch cảnh đo bình thường (thể '
                    'tích dịch ngoại bào bình thường), phản ứng tâm lý chậm hơn so với tuổi.'],
  'chan_doan': 'Hạ natri máu mạn tính ở người cao tuổi theo dõi do thuốc hoặc SIADH.',
  'chinh': ['nồng độ natri máu xét nghiệm dưới 130 mmol/l kéo dài nhiều tuần',
            'mệt mỏi rã rời uể oải bước đi loạng choạng dễ vấp ngã',
            'chán ăn nôn nao buồn nôn phản ứng chậm chạp với xung quanh'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Xét nghiệm điện giải đồ máu và niệu, đo áp lực thẩm thấu máu và áp lực thẩm thấu nước tiểu, ngừng thuốc '
              'lợi tiểu nghi ngờ, hạn chế lượng dịch uống vào khoảng 1000ml/ngày, bù natri đường uống từ từ điều chỉnh '
              'nồng độ natri tăng không quá 8 mmol/l trong 24 giờ để phòng hủy myelin cầu não.',
  'kham': 'Bệnh nhân tỉnh táo nhưng tiếp xúc chậm chạp, niêm mạc miệng ẩm vừa, không có phù ngoại biên hai chân, tĩnh '
          'mạch cổ không nổi ở tư thế 45 độ, nhịp tim đều 72 ck/p, huyết áp 125/80 mmHg, khám thần kinh không thấy dấu '
          'hiệu liệt khu trú.',
  'nhom': 'người lớn',
  'phu': ['suy giảm chú ý hay quên nhẹ dao động trong ngày',
          'tiền sử đang sử dụng thuốc lợi tiểu thiazide hoặc thuốc chống trầm cảm',
          'không có phù chân hoặc dấu hiệu mất nước nặng trên lâm sàng'],
  'ten': 'hạ natri máu mạn tính ở người cao tuổi'},
 {'bien_the_chan_doan': ['Mê sảng cấp tính ở người cao tuổi thúc đẩy bởi nhiễm trùng tiết niệu và bí tiểu.',
                         'Theo dõi mê sảng cấp tính ở người cao tuổi thể tăng động do nhiễm khuẩn huyết.',
                         'Mê sảng cấp tính ở người cao tuổi thể hỗn hợp sau dùng thuốc kháng cholinergic.',
                         'Mê sảng cấp tính ở người cao tuổi trên nền suy giảm nhận thức nhẹ có sốt cao.',
                         'Theo dõi mê sảng cấp tính ở người cao tuổi thể giảm hoạt động lơ mơ suy hô hấp.',
                         'Mê sảng cấp tính ở người cao tuổi do rối loạn nước điện giải cấp.'],
  'bien_the_ke_hoach': ['Đặt ống thông tiểu giải áp bàng quang lấy nước tiểu làm tổng phân tích và cấy khuẩn, xét '
                        'nghiệm công thức máu CRP điện giải đồ đường huyết khẩn, dùng kháng sinh đường tĩnh mạch điều '
                        'trị ổ nhiễm trùng, tạo môi trường phòng bệnh yên tĩnh có ánh sáng định hướng tránh cố định '
                        'thể chất.',
                        'Tìm và xử trí nguyên nhân khởi phát cấp tính, xét nghiệm khí máu động mạch và X-quang phổi '
                        'thẳng, điều chỉnh nước điện giải, bố trí người nhà túc trực trấn an định hướng không gian.',
                        'Chỉ định cấy máu xét nghiệm chức năng gan thận, đặt sonde bàng quang ngắt quãng, dùng thuốc '
                        'an thần haloperidol liều rất thấp 0.5mg chỉ khi kích động nguy hiểm tự hại.',
                        'Đảm bảo thông thoáng đường thở bù đủ dịch qua đường truyền tĩnh mạch, kiểm tra lại toàn bộ '
                        'đơn thuốc ngưng ngay các thuốc kháng histamin và an thần, để đồng hồ và lịch to trong tầm '
                        'mắt.',
                        'Chụp CT sọ não cấp loại trừ tụ máu dưới màng cứng hoặc nhồi máu não mới, cấy vi sinh nước '
                        'tiểu, dùng kháng sinh cephalosporin thế hệ 3, hỗ trợ dinh dưỡng đường tĩnh mạch.',
                        'Theo dõi sinh hiệu và thang điểm CAM mỗi 4 giờ, kiểm soát đau bằng paracetamol, duy trì đủ '
                        'oxy qua cannula gọng mũi, hướng dẫn điều dưỡng xoay trở nhẹ nhàng.'],
  'bien_the_kham': ['Bệnh nhân mất định hướng không gian và thời gian, không thể thực hiện bài test chú ý đếm ngược từ '
                    '20 về 1, lúc lơ mơ lú lẫn lúc kích động đòi giật kim truyền, thang điểm CAM (Confusion Assessment '
                    'Method) dương tính, thân nhiệt 38.3 độ C, ấn tức hạ vị có cầu bàng quang nổi rõ.',
                    'Khám thấy trạng thái ý thức dao động rõ, khó thu hút và duy trì sự chú ý, lời nói rời rạc hoang '
                    'tưởng nhẹ, thang CAM đạt 4/4 tiêu chí chẩn đoán mê sảng, phổi nghe ran nổ rải rác đáy phải.',
                    'Bệnh nhân bứt rứt không nhận ra người thân trong gia đình, nhìn trần nhà sợ hãi ảo thị, test CAM '
                    'dương tính, nhịp tim nhanh 105 ck/p, huyết áp 145/90 mmHg, bụng chướng nhẹ ấn đau hạ vị.',
                    'Ý thức lúc tỉnh táo trả lời ngắn lúc lơ đãng lim dim, nói lẩm bẩm một mình, thang điểm 4AT đạt 8 '
                    'điểm xác định mê sảng, nhiệt độ 38.0 độ C, không có dấu thần kinh định vị mới.',
                    'Bệnh nhân vật vã bồn chồn kéo giật áo quần, mất tập trung hoàn toàn khi bác sĩ hỏi chuyện, đồng '
                    'tử hai bên đều phản xạ ánh sáng tốt, cầu bàng quang trên xương mu căng tròn đau tức.',
                    'Khám ghi nhận chu kỳ thức ngủ đảo lộn, bệnh nhân kích động về chiều tối (hội chứng hoàng hôn), '
                    'CAM test dương tính, khám cổ mềm không gượng, thở nhanh nông 24 ck/p.'],
  'chan_doan': 'Mê sảng cấp tính ở người cao tuổi thúc đẩy bởi nhiễm trùng tiết niệu và bí tiểu.',
  'chinh': ['khởi phát rối loạn ý thức và chú ý đột ngột trong vài giờ đến vài ngày',
            'mức độ tỉnh táo dao động thất thường lúc lơ mơ lúc kích động',
            'tư duy vô tổ chức nói năng lộn xộn không đầu đuôi'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Đặt ống thông tiểu giải áp bàng quang lấy nước tiểu làm tổng phân tích và cấy khuẩn, xét nghiệm công '
              'thức máu CRP điện giải đồ đường huyết khẩn, dùng kháng sinh đường tĩnh mạch điều trị ổ nhiễm trùng, tạo '
              'môi trường phòng bệnh yên tĩnh có ánh sáng định hướng tránh cố định thể chất.',
  'kham': 'Bệnh nhân mất định hướng không gian và thời gian, không thể thực hiện bài test chú ý đếm ngược từ 20 về 1, '
          'lúc lơ mơ lú lẫn lúc kích động đòi giật kim truyền, thang điểm CAM (Confusion Assessment Method) dương '
          'tính, thân nhiệt 38.3 độ C, ấn tức hạ vị có cầu bàng quang nổi rõ.',
  'nhom': 'người lớn',
  'phu': ['rối loạn chu kỳ thức ngủ ngày ngủ gà đêm tỉnh la hét',
          'ảo giác thị giác nhìn thấy người lạ hoặc hình ảnh kì lạ không có thật',
          'xuất hiện sau một đợt nhiễm khuẩn cấp bí tiểu hoặc dùng thuốc mới'],
  'ten': 'mê sảng cấp tính ở người cao tuổi'},
 {'bien_the_chan_doan': ['Đa bệnh lý dùng nhiều thuốc ở người già hội chứng đa thuốc tương tác bất lợi.',
                         'Theo dõi đa bệnh lý dùng nhiều thuốc ở người già có hạ huyết áp tư thế do thuốc.',
                         'Đa bệnh lý dùng nhiều thuốc ở người già nguy cơ tương tác thuốc bất lợi cao.',
                         'Đa bệnh lý dùng nhiều thuốc ở người già có suy giảm nhẹ chức năng lọc thận.',
                         'Theo dõi đa bệnh lý dùng nhiều thuốc ở người già kèm quá tải gánh nặng điều trị.',
                         'Đa bệnh lý dùng nhiều thuốc ở người già biến chứng an thần quá mức ban ngày.'],
  'bien_the_ke_hoach': ['Rà soát toàn diện đơn thuốc theo tiêu chí Beers và tiêu chuẩn STOPP/START, ngừng các thuốc '
                        'trùng lặp tác dụng hoặc không còn chỉ định rõ ràng, thay thế bằng phác đồ kết hợp thuốc trong '
                        '1 viên uống, lập bảng hướng dẫn dùng thuốc bằng chữ in lớn có ô phân loại buổi sáng buổi tối.',
                        'Hội chẩn dược sĩ lâm sàng rà soát tương tác thuốc cytochrome P450, ngưng thuốc an thần gây '
                        'ngủ kéo dài, chỉnh liều thuốc tim mạch theo độ thanh thải creatinin.',
                        'Tối giản hóa đơn thuốc đưa về dưới 4 loại thiết yếu nhất, tư vấn gia đình sử dụng hộp chia '
                        'thuốc theo ngày có nắp phân chia sáng trưa chiều tối.',
                        'Đánh giá lại mục tiêu điều trị huyết áp và đường huyết cá thể hóa nới lỏng mục tiêu ở người '
                        'cao tuổi, ngưng các thực phẩm chức năng không rõ nguồn gốc.',
                        'Xét nghiệm định kỳ chức năng gan thận điện giải đồ kiểm tra tác động tích lũy của thuốc, hẹn '
                        'tái khám sau 2 tuần để đánh giá lại triệu chứng dung nạp.',
                        'Lập kế hoạch ngừng thuốc từng bước (deprescribing) đối với nhóm ức chế bơm proton và thuốc '
                        'giãn mạch không cần thiết, hướng dẫn người chăm sóc theo dõi huyết áp tại nhà.'],
  'bien_the_kham': ['Bệnh nhân mang theo túi gồm 7 loại thuốc khác nhau đang uống, thể trạng trung bình, niêm mạc hồng '
                    'vừa, nhịp tim đều 66 ck/p, huyết áp đo tư thế nằm 135/80 mmHg giảm xuống 112/68 mmHg ở tư thế '
                    'đứng, bụng mềm, không có thiếu sót vận động thần kinh.',
                    'Kiểm tra thực tế bệnh nhân đang dùng 8 loại thuốc gồm thuốc hạ áp lợi tiểu an thần giảm đau hạ '
                    'đường huyết, có dấu hiệu khô miệng niêm mạc môi se, mạch 70 lần/phút, dáng đi chậm chạp.',
                    'Khám lâm sàng ghi nhận dấu hiệu hạ huyết áp tư thế đứng rõ rệt do phối hợp thuốc giãn mạch và lợi '
                    'tiểu, bụng chướng nhẹ do nhu động ruột giảm, phản xạ bình thường.',
                    'Bệnh nhân mệt mỏi ngủ gà nhẹ ban ngày, nhịp thở 18 ck/p, gan lách không to, xét nghiệm chức năng '
                    'thận eGFR giảm nhẹ 52 ml/phút/1.73m2 do tuổi tác.',
                    'Bệnh nhân mang 6 vỉ thuốc các loại có một số thuốc cùng nhóm kháng viêm NSAID được kê đơn ở hai '
                    'nơi, tim phổi bình thường, khớp hai gối thoái hóa nhẹ.',
                    'Thể trạng người già dùng đa thuốc, khám thần kinh không có liệt, thang điểm đánh giá nguy cơ biến '
                    'cố bất lợi do thuốc ADR ở mức cao, huyết áp dao động nhiều.'],
  'chan_doan': 'Đa bệnh lý dùng nhiều thuốc ở người già hội chứng đa thuốc tương tác bất lợi.',
  'chinh': ['đang sử dụng từ 5 loại thuốc kê đơn trở lên cùng lúc hàng ngày',
            'xuất hiện các triệu chứng tương tác thuốc như chóng mặt ngủ gà hoặc tụt huyết áp',
            'mắc đồng thời từ 3 bệnh mạn tính tim mạch chuyển hóa và cơ xương khớp'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Rà soát toàn diện đơn thuốc theo tiêu chí Beers và tiêu chuẩn STOPP/START, ngừng các thuốc trùng lặp '
              'tác dụng hoặc không còn chỉ định rõ ràng, thay thế bằng phác đồ kết hợp thuốc trong 1 viên uống, lập '
              'bảng hướng dẫn dùng thuốc bằng chữ in lớn có ô phân loại buổi sáng buổi tối.',
  'kham': 'Bệnh nhân mang theo túi gồm 7 loại thuốc khác nhau đang uống, thể trạng trung bình, niêm mạc hồng vừa, nhịp '
          'tim đều 66 ck/p, huyết áp đo tư thế nằm 135/80 mmHg giảm xuống 112/68 mmHg ở tư thế đứng, bụng mềm, không '
          'có thiếu sót vận động thần kinh.',
  'nhom': 'người lớn',
  'phu': ['thường xuyên nhầm lẫn giữa các viên thuốc về liều dùng và giờ uống',
          'khó tiêu táo bón khô miệng do tác dụng kháng cholinergic tích lũy',
          'khám bệnh và nhận đơn thuốc từ nhiều cơ sở y tế chuyên khoa khác nhau'],
  'ten': 'đa bệnh lý dùng nhiều thuốc ở người già'},
 {'bien_the_chan_doan': ['Rối loạn nuốt ở người cao tuổi sau tai biến mạch máu não di chứng.',
                         'Theo dõi rối loạn nuốt ở người cao tuổi sau tai biến giai đoạn hồi phục chức năng.',
                         'Rối loạn nuốt ở người cao tuổi sau tai biến mức độ trung bình có hít sặc thầm lặng.',
                         'Rối loạn nuốt ở người cao tuổi sau tai biến biến chứng viêm phổi hít tái diễn.',
                         'Theo dõi rối loạn nuốt ở người cao tuổi sau tai biến thể liệt hầu họng một bên.',
                         'Rối loạn nuốt ở người cao tuổi sau tai biến cần can thiệp dinh dưỡng qua sonde.'],
  'bien_the_ke_hoach': ['Chỉ định nội soi đánh giá chức năng nuốt bằng ống mềm FEES hoặc chụp X-quang nuốt huỳnh quang '
                        'có cản quang VFSS, tập phục hồi chức năng nuốt cùng chuyên viên ngôn ngữ trị liệu, hướng dẫn '
                        'kỹ thuật gập cằm khi nuốt và sử dụng chất làm đặc thức ăn dạng gel sánh.',
                        'Hội chẩn chuyên khoa phục hồi chức năng tập bài tập Shaker tăng cường cơ nâng thanh quản và '
                        'bài tập nuốt gắng sức Masako, chuyển sang chế độ ăn thức ăn nghiền nhuyễn sệt.',
                        'Hướng dẫn tư thế ngồi thẳng 90 độ trong suốt bữa ăn và duy trì ngồi thêm 30 phút sau ăn, sử '
                        'dụng chất làm đặc chất lỏng mức độ 2 (nectar-thick), vệ sinh răng miệng kỹ sau mỗi bữa.',
                        'Chụp X-quang phổi kiểm tra thâm nhiễm đáy phổi, tập ho chủ động và dẫn lưu tư thế hỗ trợ tống '
                        'đờm, xem xét đặt ống thông dạ dày nuôi dưỡng nếu sặc nặng liên tục.',
                        'Theo dõi cân nặng và điện giải đồ hàng tuần tránh suy dinh dưỡng và mất nước, huấn luyện '
                        'người nhà nhận biết sớm các dấu hiệu nghẹn sặc nguy hiểm để xử trí Heimlich.',
                        'Kê đơn bột làm đặc thực phẩm tinh bột biến tính, chia nhỏ bữa ăn thành 5-6 lần mỗi ngày, hẹn '
                        'đánh giá lại chức năng nuốt sau 4 tuần tập luyện.'],
  'bien_the_kham': ['Khám họng phản xạ nôn vòm miệng giảm bên liệt, khẩu cái mềm nâng kém bên phải, thực hiện test '
                    'nuốt nước 30ml (WST) bệnh nhân nuốt 3 lần mới hết có ho húng hắng và giọng nói ướt sau nuốt, nghe '
                    'phổi hai bên thông khí giảm nhẹ rải rác đờm đáy phổi.',
                    'Bệnh nhân có liệt nhẹ dây thần kinh số IX và X bên trái, lưỡi gà lệch sang phải khi há miệng phát '
                    'âm A, test nuốt thìa nước có phản xạ ho sặc chậm trễ sau 3 giây.',
                    'Khám phản xạ ho bảo vệ đường thở yếu, đọng nước bọt góc miệng bên liệt, kiểm tra ăn thử thạch sệt '
                    'bệnh nhân nuốt an toàn hơn so với uống nước lỏng.',
                    'Vòm họng nâng không đối xứng, cảm giác thành sau họng giảm, sau khi uống ngụm nước thấy phát âm '
                    'có tiếng lọc xọc ẩm ướt ở thanh quản, SpO2 96%.',
                    'Bệnh nhân ăn uống ngậm lâu trong khoang miệng khó tạo viên thức ăn, cơ cắn và cơ vòng môi khép '
                    'kín kém bên liệt, test nuốt nước kích thích cơn ho kéo dài.',
                    'Khám đánh giá cơ họng hầu thấy cử động nâng thanh quản lên trên ra trước bị hạn chế khi nuốt, '
                    'nghe phổi đáy phải có ran ẩm nhỏ hạt do hít dịch vi thể.'],
  'chan_doan': 'Rối loạn nuốt ở người cao tuổi sau tai biến mạch máu não di chứng.',
  'chinh': ['ho sặc nghẹn tái diễn mỗi khi uống nước lọc hoặc ăn thức ăn lỏng',
            'cảm giác vướng ứ đọng thức ăn tại vùng hầu họng sau động tác nuốt',
            'giọng nói biến đổi ục ặc như có dịch đờm ứ trong cổ họng sau nuốt'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Chỉ định nội soi đánh giá chức năng nuốt bằng ống mềm FEES hoặc chụp X-quang nuốt huỳnh quang có cản '
              'quang VFSS, tập phục hồi chức năng nuốt cùng chuyên viên ngôn ngữ trị liệu, hướng dẫn kỹ thuật gập cằm '
              'khi nuốt và sử dụng chất làm đặc thức ăn dạng gel sánh.',
  'kham': 'Khám họng phản xạ nôn vòm miệng giảm bên liệt, khẩu cái mềm nâng kém bên phải, thực hiện test nuốt nước '
          '30ml (WST) bệnh nhân nuốt 3 lần mới hết có ho húng hắng và giọng nói ướt sau nuốt, nghe phổi hai bên thông '
          'khí giảm nhẹ rải rác đờm đáy phổi.',
  'nhom': 'người lớn',
  'phu': ['thời gian mỗi bữa ăn kéo dài trên 45 phút gây mệt mỏi',
          'sụt cân dần do sợ ăn uống và giảm lượng thức ăn đưa vào cơ thể',
          'tiền sử có các đợt sốt viêm phổi hít tái phát sau đột quỵ'],
  'ten': 'rối loạn nuốt ở người cao tuổi sau tai biến'},
 {'bien_the_chan_doan': ['Viêm teo niêm mạc âm đạo do lão hóa hội chứng niệu dục sau mãn kinh.',
                         'Theo dõi viêm teo niêm mạc âm đạo do lão hóa có kích thích đường tiểu dưới.',
                         'Viêm teo niêm mạc âm đạo do lão hóa mức độ vừa có đau khi giao hợp.',
                         'Viêm teo niêm mạc âm đạo do lão hóa gây xuất huyết điểm niêm mạc.',
                         'Theo dõi viêm teo niêm mạc âm đạo do lão hóa ở phụ nữ mãn kinh lâu năm.',
                         'Viêm teo niêm mạc âm đạo do lão hóa biến chứng viêm âm đạo thứ phát.'],
  'bien_the_ke_hoach': ['Kê kem bôi estrogen estriol hoặc estradiol tại chỗ đặt âm đạo liều thấp ban đêm trong 2-3 '
                        'tuần đầu sau đó giảm liều duy trì tuần 2 lần, hướng dẫn sử dụng chất giữ ẩm âm đạo không nội '
                        'tiết thường xuyên và gel bôi trơn khi sinh hoạt tình dục, vệ sinh bằng dung dịch dịu nhẹ '
                        'tránh thụt rửa.',
                        'Chỉ định viên đặt âm đạo chứa estrogen liều thấp promestriene 10mg mỗi tối trong 20 ngày liên '
                        'tiếp, hướng dẫn bôi kem giữ ẩm dưỡng ẩm gốc nước hàng ngày.',
                        'Kê đơn viên nén đặt âm đạo estradiol 10 mcg duy trì hai lần mỗi tuần, tư vấn mặc đồ lót '
                        'cotton thoáng mát, tránh dùng xà phòng thơm hay chất tẩy rửa mạnh.',
                        'Làm xét nghiệm tế bào học cổ tử cung Pap smear loại trừ tổn thương tiền ung thư, hướng dẫn '
                        'chế độ sinh hoạt tình dục nhẹ nhàng có hỗ trợ chất bôi trơn gốc silicon.',
                        'Tư vấn về tính an toàn của estrogen tác dụng tại chỗ không làm tăng nguy cơ ung thư vú hay '
                        'thuyên tắc mạch, hẹn tái khám đánh giá đáp ứng lâm sàng sau 6 tuần.',
                        'Phối hợp bổ sung viên đặt lợi khuẩn chứa chủng Lactobacillus tái lập hệ vi sinh đường âm đạo, '
                        'tư vấn uống đủ nước và tập bài tập sàn chậu tăng tưới máu vùng sinh dục.'],
  'bien_the_kham': ['Khám phụ khoa bằng mỏ vịt kích thước nhỏ thấy niêm mạc âm đạo nhợt nhạt mất các nếp nhăn sinh lý, '
                    'bề mặt niêm mạc khô mỏng bóng dễ xuất huyết điểm khi chạm nhẹ mỏ vịt, không có khối u sùi, đo pH '
                    'âm đạo tăng cao 6.2.',
                    'Âm hộ teo nhẹ vùng nếp gấp da ngoài giảm lớp mỡ dưới da, niêm mạc tiền đình và âm đạo khô ráp '
                    'nhợt nhạt có vài điểm xuất huyết dưới biểu mô nhỏ, lỗ niệu đạo tụt nhẹ vào trong.',
                    'Đặt mỏ vịt khó khăn do lối vào âm đạo hẹp và khô rát, niêm mạc thành âm đạo nhẵn láng mất nếp gấp '
                    'ngang sinh lý, không có khí hư mùi hôi, que thử giấy đo pH dịch đạt 6.5.',
                    'Khám thấy biểu mô âm đạo mỏng dính dễ trầy rướm ít máu khi quệt bông xét nghiệm, soi tươi dịch âm '
                    'đạo thấy nhiều tế bào biểu mô cận đáy và đáy, rất ít tế bào bề mặt và vắng bóng trực khuẩn '
                    'Doderlein.',
                    'Cửa mình khô rát, niêm mạc thành trước và thành sau âm đạo dính sát vào nhau, bề mặt nhợt bóng, '
                    'cổ tử cung teo nhỏ ngang bằng đáy cùng âm đạo không viêm loét ác tính.',
                    'Khám ngoài thấy lông mu thưa thớt, da vùng sinh dục ngoài mỏng khô, niêm mạc ống âm đạo giảm tính '
                    'đàn hồi rõ rệt, ấn nhẹ thành âm đạo bệnh nhân than đau rát tức thì.'],
  'chan_doan': 'Viêm teo niêm mạc âm đạo do lão hóa hội chứng niệu dục sau mãn kinh.',
  'chinh': ['cảm giác khô rát ngứa ngáy châm chích vùng âm đạo kéo dài sau mãn kinh',
            'đau buốt nhiều khi giao hợp hoặc cảm giác thốn rát khi ngồi lâu',
            'tiết dịch âm đạo rất ít hoặc dịch loãng hơi vàng có thể lẫn vệt máu nhạt do cọ xát'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Kê kem bôi estrogen estriol hoặc estradiol tại chỗ đặt âm đạo liều thấp ban đêm trong 2-3 tuần đầu sau '
              'đó giảm liều duy trì tuần 2 lần, hướng dẫn sử dụng chất giữ ẩm âm đạo không nội tiết thường xuyên và '
              'gel bôi trơn khi sinh hoạt tình dục, vệ sinh bằng dung dịch dịu nhẹ tránh thụt rửa.',
  'kham': 'Khám phụ khoa bằng mỏ vịt kích thước nhỏ thấy niêm mạc âm đạo nhợt nhạt mất các nếp nhăn sinh lý, bề mặt '
          'niêm mạc khô mỏng bóng dễ xuất huyết điểm khi chạm nhẹ mỏ vịt, không có khối u sùi, đo pH âm đạo tăng cao '
          '6.2.',
  'nhom': 'người lớn',
  'phu': ['tiểu buốt rắt tiểu gấp kích thích đường tiểu dưới không do vi khuẩn',
          'niêm mạc sinh dục mỏng manh dễ trầy xước rướm máu khi lau rửa vệ sinh',
          'tiền sử đã mãn kinh tự nhiên trên 5 năm không dùng liệu pháp nội tiết'],
  'ten': 'viêm teo niêm mạc âm đạo do lão hóa'},
 {'bien_the_chan_doan': ['Trầm cảm muộn ở người cao tuổi thể cơ thể hóa.',
                         'Theo dõi trầm cảm muộn ở người cao tuổi mức độ vừa có rối loạn giấc ngủ.',
                         'Trầm cảm muộn ở người cao tuổi kèm lo âu toàn thể.',
                         'Trầm cảm muộn ở người cao tuổi thể giả sa sút trí tuệ.',
                         'Theo dõi trầm cảm muộn ở người cao tuổi sau biến cố tang chế gia đình.',
                         'Trầm cảm muộn ở người cao tuổi khởi phát muộn sau tuổi 65.'],
  'bien_the_ke_hoach': ['Xét nghiệm hormone tuyến giáp TSH và vitamin B12 loại trừ căn nguyên thực thể, bắt đầu điều '
                        'trị thuốc chống trầm cảm nhóm SSRI liều thấp sertraline 25mg/ngày sau đó tăng dần 50mg/ngày, '
                        'kết hợp trị liệu tâm lý nâng đỡ và khuyến khích tham gia câu lạc bộ người cao tuổi.',
                        'Kê đơn escitalopram 5mg uống buổi sáng theo dõi tác dụng phụ tiêu hóa trong tuần đầu, hướng '
                        'dẫn vệ sinh giấc ngủ không nằm xem tivi trên giường, hẹn tái khám sau 2 tuần.',
                        'Lựa chọn mirtazapine 15mg uống trước khi ngủ giúp cải thiện giấc ngủ và kích thích ngon miệng '
                        'ở người cao tuổi gầy sút cân, tư vấn gia đình tăng cường trò chuyện lắng nghe.',
                        'Xét nghiệm điện giải đồ kiểm tra nồng độ natri máu trước và sau khi khởi trị SSRI, kết hợp '
                        'liệu pháp nhận thức hành vi thích nghi với tuổi già, tập thể dục dưỡng sinh nhẹ nhàng.',
                        'Tư vấn gia đình theo dõi sát khí sắc và giấc ngủ của bệnh nhân, giải thích thuốc chống trầm '
                        'cảm cần 3-4 tuần mới phát huy hiệu quả đầy đủ, tránh tự ý ngưng thuốc đột ngột.',
                        'Hội chẩn bác sĩ chuyên khoa tâm thần nếu triệu chứng không thuyên giảm sau 6 tuần điều trị đủ '
                        'liều, bổ sung thêm vitamin nhóm B và hướng dẫn chế độ sinh hoạt đều đặn.'],
  'bien_the_kham': ['Bệnh nhân nét mặt u buồn ít biểu cảm, giọng nói trầm nhỏ chậm rãi, cử động chậm chạp, thang điểm '
                    'đánh giá trầm cảm người cao tuổi GDS-15 đạt 11/15 điểm (trầm cảm rõ), định hướng không gian thời '
                    'gian bình thường, không có dấu thần kinh khu trú.',
                    'Tác phong chậm chạp, ánh mắt buồn bã né tránh nhìn thẳng, thang điểm GDS-15 đạt 10/15 điểm, khai '
                    'nhận nhiều triệu chứng mỏi mệt đau dạ dày hồi hộp đã đi khám nhiều nơi không ra bệnh.',
                    'Bệnh nhân than phiền trí nhớ giảm sút (giả sa sút trí tuệ do trầm cảm), nhưng làm test nhận thức '
                    'MMSE đạt 27/30 điểm bình thường, thang điểm Beck Depression Inventory đạt 24 điểm.',
                    'Khám toàn diện tim mạch hô hấp tiêu hóa bình thường không phát hiện tổn thương cơ quan đích, nét '
                    'mặt căng thẳng âu lo, phản xạ gân xương bình thường, nhịp tim 74 ck/p.',
                    'Bệnh nhân trả lời câu hỏi bằng giọng nhỏ yếu ớt, thở dài thường xuyên, thang điểm đánh giá trầm '
                    'cảm Hamilton 17 mục đạt 19 điểm mức độ trầm cảm vừa, không có ý định tự hại rõ rệt.',
                    'Khám lâm sàng ghi nhận tình trạng suy nhược khí sắc suy giảm nghiêm trọng, tiếp xúc hợp tác nhưng '
                    'thiếu sinh khí, cử động đầu chi chậm chạp, huyết áp 120/75 mmHg.'],
  'chan_doan': 'Trầm cảm muộn ở người cao tuổi thể cơ thể hóa.',
  'chinh': ['mất hứng thú và niềm vui trong hầu hết các hoạt động từng ưa thích kéo dài',
            'than phiền nhiều về các triệu chứng đau nhức cơ thể mơ hồ không rõ nguyên nhân',
            'khí sắc u sầu cảm giác bản thân vô dụng hoặc là gánh nặng cho con cháu'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'lão khoa',
  'ke_hoach': 'Xét nghiệm hormone tuyến giáp TSH và vitamin B12 loại trừ căn nguyên thực thể, bắt đầu điều trị thuốc '
              'chống trầm cảm nhóm SSRI liều thấp sertraline 25mg/ngày sau đó tăng dần 50mg/ngày, kết hợp trị liệu tâm '
              'lý nâng đỡ và khuyến khích tham gia câu lạc bộ người cao tuổi.',
  'kham': 'Bệnh nhân nét mặt u buồn ít biểu cảm, giọng nói trầm nhỏ chậm rãi, cử động chậm chạp, thang điểm đánh giá '
          'trầm cảm người cao tuổi GDS-15 đạt 11/15 điểm (trầm cảm rõ), định hướng không gian thời gian bình thường, '
          'không có dấu thần kinh khu trú.',
  'nhom': 'người lớn',
  'phu': ['mất ngủ thức giấc rất sớm lúc 3-4 giờ sáng và không thể ngủ lại được',
          'chán ăn ăn không ngon miệng dẫn đến sụt cân rõ trong vài tháng',
          'suy giảm năng lượng mệt mỏi cả ngày kèm theo lo âu căng thẳng thái quá'],
  'ten': 'trầm cảm muộn ở người cao tuổi'},
 {'bien_the_chan_doan': ['Bàng quang tăng hoạt OAB thể khô không són tiểu gấp.',
                         'Theo dõi bàng quang tăng hoạt OAB thể ướt có són tiểu gấp.',
                         'Bàng quang tăng hoạt OAB mức độ trung bình đáp ứng kém với thay đổi hành vi.',
                         'Bàng quang tăng hoạt OAB thể vô căn nguyên phát.',
                         'Theo dõi bàng quang tăng hoạt OAB có tiểu đêm chiếm ưu thế.',
                         'Bàng quang tăng hoạt OAB giai đoạn ổn định điều trị duy trì.'],
  'bien_the_ke_hoach': ['Hướng dẫn người bệnh ghi nhật ký đi tiểu liên tục trong 3 ngày, hướng dẫn bài tập phục hồi cơ '
                        'sàn chậu Kegel phối hợp tập luyện bàng quang kéo dài khoảng cách giữa các lần đi tiểu, chỉ '
                        'định dùng thuốc kháng muscarinic solifenacin 5mg/ngày hoặc đồng vận beta-3 mirabegron '
                        '50mg/ngày.',
                        'Tư vấn điều chỉnh lối sống hạn chế caffeine trà rượu bia và đồ uống có ga, không uống nhiều '
                        'nước sau 18 giờ tối, kê đơn mirabegron 50mg uống buổi sáng và theo dõi huyết áp.',
                        'Bắt đầu điều trị thuốc chẹn thụ thể muscarinic tolterodine 4mg phóng thích kéo dài, hướng dẫn '
                        'bài tập siết cơ đáy chậu khi có cơn buồn tiểu gấp để ức chế phản xạ co thắt bàng quang.',
                        'Kê đơn solifenacin 5mg uống hàng ngày, dặn dò các tác dụng phụ khô miệng táo bón nhẹ, hẹn tái '
                        'khám sau 4 tuần mang theo nhật ký đi tiểu để đánh giá hiệu quả.',
                        'Tư vấn kết hợp tập luyện phản xạ bàng quang tăng dần thời gian giữa hai lần đi tiểu thêm '
                        '15-30 phút mỗi tuần, hướng dẫn chế độ ăn nhiều chất xơ phòng ngừa táo bón.',
                        'Chỉ định đo niệu động học nếu triệu chứng không thuyên giảm sau 8 tuần dùng thuốc kháng '
                        'cholinergic, cân nhắc tiêm botulinum toxin thành bàng quang ở giai đoạn sau.'],
  'bien_the_kham': ['Khám bụng mềm không đau vùng hạ vị, không sờ thấy cầu bàng quang sau khi đi tiểu, vùng thắt lưng '
                    'hai bên không đau, tổng phân tích nước tiểu 10 thông số âm tính với bạch cầu và nitrit, siêu âm '
                    'đo thể tích nước tiểu tồn dư sau tiểu PVR dưới 20ml.',
                    'Bệnh nhân vào phòng khám với dáng vẻ bồn chồn muốn tìm nhà vệ sinh, bụng mềm ấn hạ vị tức nhẹ '
                    'nhưng không đề kháng, xét nghiệm que nhúng nước tiểu hoàn toàn bình thường không có nhiễm khuẩn.',
                    'Khám hệ tiết niệu chạm thận bập bềnh thận âm tính hai bên, siêu âm bàng quang thành đều không dày '
                    'không có sỏi hay u bàng quang, lượng nước tiểu tồn dư sau đi tiểu là 15ml.',
                    'Ấn vùng trên khớp mu không đau chói, khám loại trừ các nguyên nhân thần kinh gây rối loạn cơ '
                    'vòng, đo niệu dòng đồ đồ thị dạng hình chuông với tốc độ dòng cực đại Qmax bình thường.',
                    'Thể trạng bình thường, huyết áp 120/75 mmHg, thăm khám bụng không sờ thấy khối u vùng tiểu khung '
                    'chèn ép, xét nghiệm nước tiểu không có hồng cầu vi thể.',
                    'Khám cơ bản không ghi nhận dấu hiệu viêm bàng quang cấp, vùng đáy chậu trương lực cơ sàn chậu '
                    'bình thường, nhật ký đi tiểu ghi nhận số lần đi tiểu ban ngày 11 lần và ban đêm 3 lần.'],
  'chan_doan': 'Bàng quang tăng hoạt OAB thể khô không són tiểu gấp.',
  'chinh': ['tiểu gấp cảm giác buồn tiểu đột ngột không thể kìm nén trì hoãn',
            'tiểu nhiều lần trong ngày vượt quá 8 lần vào ban ngày',
            'tiểu đêm nhiều lần từ 2 lần trở lên làm gián đoạn giấc ngủ'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Hướng dẫn người bệnh ghi nhật ký đi tiểu liên tục trong 3 ngày, hướng dẫn bài tập phục hồi cơ sàn chậu '
              'Kegel phối hợp tập luyện bàng quang kéo dài khoảng cách giữa các lần đi tiểu, chỉ định dùng thuốc kháng '
              'muscarinic solifenacin 5mg/ngày hoặc đồng vận beta-3 mirabegron 50mg/ngày.',
  'kham': 'Khám bụng mềm không đau vùng hạ vị, không sờ thấy cầu bàng quang sau khi đi tiểu, vùng thắt lưng hai bên '
          'không đau, tổng phân tích nước tiểu 10 thông số âm tính với bạch cầu và nitrit, siêu âm đo thể tích nước '
          'tiểu tồn dư sau tiểu PVR dưới 20ml.',
  'nhom': 'người lớn',
  'phu': ['són tiểu gấp rỉ nước tiểu ra ngoài trước khi kịp vào nhà vệ sinh',
          'cảm giác căng tức nhẹ vùng hạ vị khi bàng quang bắt đầu có nước tiểu',
          'không có cảm giác tiểu buốt rát hay nước tiểu đục có cặn mủ'],
  'ten': 'bàng quang tăng hoạt OAB'},
 {'bien_the_chan_doan': ['Viêm bàng quang kẽ mạn tính hội chứng đau bàng quang.',
                         'Theo dõi viêm bàng quang kẽ mạn tính thể loét Hunner kinh điển.',
                         'Viêm bàng quang kẽ mạn tính thể không loét dung tích bàng quang giảm.',
                         'Viêm bàng quang kẽ mạn tính đau mạn tính vùng chậu dai dẳng.',
                         'Theo dõi viêm bàng quang kẽ mạn tính kèm tăng trương lực cơ sàn chậu.',
                         'Viêm bàng quang kẽ mạn tính đợt đau bùng phát sau kích thích thức ăn.'],
  'bien_the_ke_hoach': ['Chỉ định nội soi bàng quang dưới gây mê kết hợp làm căng bàng quang bằng nước thủy chướng để '
                        'phát hiện tổn thương loét Hunner hoặc xuất huyết dưới niêm mạc dạng chấm sao, hướng dẫn chế '
                        'độ ăn kiêng loại trừ thực phẩm kích thích, dùng thuốc giảm đau amitriptyline liều thấp '
                        '10-25mg uống tối và bơm rửa bàng quang bằng dung dịch acid hyaluronic.',
                        'Tư vấn chế độ ăn loại bỏ cà phê cam chanh sô cô la gia vị cay nồng, kê đơn thuốc kháng '
                        'histamin hydroxyzine 25mg uống buổi tối kết hợp pentosan polysulfate sodium 100mg ngày 3 lần.',
                        'Hội chẩn chuyên khoa tiết niệu nội soi bàng quang ống cứng đốt điện tổn thương loét nếu có, '
                        'tập vật lý trị liệu thư giãn giải phóng điểm co thắt cơ sàn chậu myofascial.',
                        'Kê đơn amitriptyline 10mg tăng dần liều để giảm đau dẫn truyền thần kinh trung ương, hướng '
                        'dẫn uống nước lọc đều đặn phân bố đều trong ngày tránh để nước tiểu quá cô đặc.',
                        'Lên kế hoạch bơm thuốc nội bàng quang dung dịch dimethyl sulfoxide (DMSO) hoặc chondroitin '
                        'sulfate tái tạo lớp glycosaminoglycan bảo vệ niêm mạc, kiểm tra định kỳ chức năng thận.',
                        'Tư vấn quản lý căng thẳng giảm stress, sử dụng túi chườm ấm vùng hạ vị khi đau tức, theo dõi '
                        'thang điểm đau VAS và tần suất đi tiểu trong sổ theo dõi ngoại trú.'],
  'bien_the_kham': ['Ấn nhẹ vùng trên khớp mu bệnh nhân thấy tức buốt khó chịu nhiều, thăm khám vùng chậu loại trừ tổn '
                    'thương viêm nhiễm phụ khoa hoặc nam khoa, cấy vi sinh nước tiểu âm tính, siêu âm hệ tiết niệu '
                    'thấy bàng quang thành đều không sỏi.',
                    'Bệnh nhân than đau nhiều khi bàng quang chứa trên 150ml nước tiểu, ấn điểm bàng quang tức buốt '
                    'lan xuống niệu đạo, xét nghiệm tổng phân tích nước tiểu có hồng cầu vi thể nhưng không có vi '
                    'khuẩn.',
                    'Khám vùng hạ vị có điểm đau khu trú trên khớp mu, khám ngoài cơ quan sinh dục bình thường không '
                    'viêm đỏ, siêu âm đường tiểu đo dung tích bàng quang chức năng giảm còn khoảng 180ml.',
                    'Bệnh nhân đi tiểu liên tục trong lúc chờ khám, ấn hạ vị đau tức dội ngược, khám tiểu khung các '
                    'tạng vùng chậu mềm không u cục, nước tiểu trong không cặn lắng.',
                    'Thăm khám lâm sàng ghi nhận hội chứng đau bàng quang kéo dài hơn một năm, không có sốt, sinh hiệu '
                    'ổn định, xét nghiệm sinh hóa máu urê creatinin bình thường.',
                    'Điểm đau bàng quang dương tính rõ khi ấn sâu hạ vị, khám cơ sàn chậu co thắt tăng trương lực do '
                    'đau mạn tính, các xét nghiệm tìm trực khuẩn lao và Chlamydia âm tính.'],
  'chan_doan': 'Viêm bàng quang kẽ mạn tính hội chứng đau bàng quang.',
  'chinh': ['đau tức âm ỉ vùng bàng quang tăng lên rõ rệt khi nước tiểu đầy',
            'cảm giác đau thuyên giảm nhanh chóng ngay sau khi đi tiểu làm rỗng bàng quang',
            'tiểu rất nhiều lần cả ngày lẫn đêm lên đến 15-25 lần mỗi ngày'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Chỉ định nội soi bàng quang dưới gây mê kết hợp làm căng bàng quang bằng nước thủy chướng để phát hiện '
              'tổn thương loét Hunner hoặc xuất huyết dưới niêm mạc dạng chấm sao, hướng dẫn chế độ ăn kiêng loại trừ '
              'thực phẩm kích thích, dùng thuốc giảm đau amitriptyline liều thấp 10-25mg uống tối và bơm rửa bàng '
              'quang bằng dung dịch acid hyaluronic.',
  'kham': 'Ấn nhẹ vùng trên khớp mu bệnh nhân thấy tức buốt khó chịu nhiều, thăm khám vùng chậu loại trừ tổn thương '
          'viêm nhiễm phụ khoa hoặc nam khoa, cấy vi sinh nước tiểu âm tính, siêu âm hệ tiết niệu thấy bàng quang '
          'thành đều không sỏi.',
  'nhom': 'người lớn',
  'phu': ['đau buốt lan tỏa ra vùng niệu đạo và vùng đáy chậu kéo dài trên 6 tháng',
          'các xét nghiệm cấy nước tiểu nhiều lần đều cho kết quả vô khuẩn',
          'đau tăng lên khi ăn các loại thức ăn chua cay cà chua hoặc khi căng thẳng'],
  'ten': 'viêm bàng quang kẽ mạn tính'},
 {'bien_the_chan_doan': ['Tiểu ra máu đại thể không triệu chứng theo dõi u đường tiết niệu.',
                         'Theo dõi tiểu ra máu đại thể không triệu chứng nghi ngờ u bàng quang.',
                         'Tiểu ra máu đại thể không triệu chứng cần phân biệt u biểu mô đường niệu trên.',
                         'Tiểu ra máu đại thể không triệu chứng đợt đầu tiên nguy cơ cao.',
                         'Theo dõi tiểu ra máu đại thể không triệu chứng ở người hút thuốc lá lâu năm.',
                         'Tiểu ra máu đại thể không triệu chứng nguồn gốc từ bàng quang.'],
  'bien_the_ke_hoach': ['Chỉ định chụp cắt lớp vi tính hệ tiết niệu đa dãy có tiêm thuốc cản quang theo quy trình chụp '
                        'đường tiểu (CT Urography), xét nghiệm tế bào học cặn lắng nước tiểu tìm tế bào ác tính 3 mẫu '
                        'liên tiếp, hẹn nội soi bàng quang ống mềm khẩn cấp để xác định vị trí nguồn gốc chảy máu.',
                        'Làm xét nghiệm công thức máu kiểm tra nồng độ hemoglobin, đông máu toàn bộ, chức năng thận '
                        'urê creatinin trước khi tiêm cản quang, tư vấn bệnh nhân uống nhiều nước lọc để tránh hình '
                        'thành cục máu đông bít tắc niệu đạo.',
                        'Chỉ định siêu âm Doppler hệ tiết niệu khảo sát thận bàng quang phát hiện chồi sùi niêm mạc, '
                        'sắp xếp lịch nội soi bàng quang bằng ống soi mềm tại phòng tiểu phẫu.',
                        'Xét nghiệm nước tiểu vi thể tìm hồng cầu dị dạng phân biệt tiểu máu cầu thận, chụp CT '
                        'Urography khảo sát đài bể thận niệu quản bàng quang, hướng dẫn nhập viện nếu có bí tiểu do '
                        'máu cục.',
                        'Tư vấn giải thích cho người bệnh về tầm quan trọng của việc khảo sát toàn bộ đường niệu loại '
                        'trừ tổn thương ác tính giai đoạn sớm, hẹn làm sinh thiết qua nội soi nếu phát hiện khối sùi.',
                        'Xét nghiệm đông máu cơ bản PT aPTT fibrinogen, kiểm tra chức năng đông cầm máu, dặn dò bệnh '
                        'nhân giữ lại mẫu nước tiểu có lẫn máu cục để bác sĩ đánh giá hình thái.'],
  'bien_the_kham': ['Bệnh nhân tỉnh táo, da niêm mạc hồng, chạm thận và bập bềnh thận hai bên âm tính, ấn các điểm '
                    'niệu quản trên và giữa không đau, khám trực tràng không có u cục vùng tiểu khung, lấy mẫu nước '
                    'tiểu quan sát thấy màu đỏ ánh hồng đồng nhất.',
                    'Khám lâm sàng bụng mềm không sờ thấy khối u vùng hông lưng hay tiểu khung, gõ vùng bàng quang '
                    'không chướng, mẫu nước tiểu đỏ đậm có sợi dây máu nhỏ, sinh hiệu mạch 78 ck/p huyết áp 125/80 '
                    'mmHg.',
                    'Thể trạng trung bình, niêm mạc mắt hồng hào chưa có dấu hiệu thiếu máu nặng, khám hố thắt lưng '
                    'hai bên đối xứng không sưng nề, xét nghiệm que thử nước tiểu hồng cầu 3+ protein 1+.',
                    'Bệnh nhân không sốt, không có điểm đau khu trú trên hệ tiết niệu, khám cơ quan sinh dục ngoài '
                    'bình thường, nước tiểu hứng tại phòng khám có màu đỏ như nước rửa thịt.',
                    'Khám tuần hoàn hô hấp bình thường, bụng mềm gan lách không to, ấn các điểm sườn lưng sườn cột '
                    'sống không đau, không có dấu hiệu nhiễm trùng toàn thân.',
                    'Bệnh nhân tiếp xúc tốt, huyết động ổn định, thăm khám không phát hiện chấn thương vùng hạ vị hay '
                    'vùng lưng hông, nước tiểu đỏ toàn bãi không có cặn mủ trắng.'],
  'chan_doan': 'Tiểu ra máu đại thể không triệu chứng theo dõi u đường tiết niệu.',
  'chinh': ['nước tiểu có màu đỏ tươi hoặc đỏ sẫm toàn bãi xuất hiện đột ngột',
            'hoàn toàn không có cảm giác đau buốt khi đi tiểu hay đau quặn hông lưng',
            'nước tiểu có thể lẫn vài cục máu đông nhỏ tự phát'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Chỉ định chụp cắt lớp vi tính hệ tiết niệu đa dãy có tiêm thuốc cản quang theo quy trình chụp đường '
              'tiểu (CT Urography), xét nghiệm tế bào học cặn lắng nước tiểu tìm tế bào ác tính 3 mẫu liên tiếp, hẹn '
              'nội soi bàng quang ống mềm khẩn cấp để xác định vị trí nguồn gốc chảy máu.',
  'kham': 'Bệnh nhân tỉnh táo, da niêm mạc hồng, chạm thận và bập bềnh thận hai bên âm tính, ấn các điểm niệu quản '
          'trên và giữa không đau, khám trực tràng không có u cục vùng tiểu khung, lấy mẫu nước tiểu quan sát thấy màu '
          'đỏ ánh hồng đồng nhất.',
  'nhom': 'người lớn',
  'phu': ['tiền sử hút thuốc lá nhiều năm hoặc làm việc trong môi trường hóa chất công nghiệp',
          'không sốt không có biểu hiện sút cân hay phù thũng trong giai đoạn đầu',
          'triệu chứng nước tiểu đỏ có thể tự hết sau vài ngày rồi tái diễn trở lại'],
  'ten': 'tiểu ra máu đại thể không triệu chứng'},
 {'bien_the_chan_doan': ['Thận đa nang di truyền trội ADPKD giai đoạn bảo tồn chức năng thận.',
                         'Theo dõi thận đa nang di truyền trội ADPKD có đợt xuất huyết trong nang.',
                         'Thận đa nang di truyền trội ADPKD kèm tăng huyết áp nguyên phát.',
                         'Thận đa nang di truyền trội ADPKD biến chứng nang gan phối hợp.',
                         'Theo dõi thận đa nang di truyền trội ADPKD suy giảm nhẹ độ lọc cầu thận.',
                         'Thận đa nang di truyền trội ADPKD thể tiến triển nhanh tổng thể tích thận lớn.'],
  'bien_the_ke_hoach': ['Siêu âm hoặc chụp cộng hưởng từ MRI hệ tiết niệu đo tổng thể tích thận nang TKV, xét nghiệm '
                        'chức năng thận urê creatinin máu và độ lọc cầu thận ước tính eGFR, kiểm soát huyết áp mục '
                        'tiêu dưới 130/80 mmHg ưu tiên dùng thuốc ức chế men chuyển hoặc chẹn thụ thể ARB, khuyến '
                        'khích uống nhiều nước trên 2.5-3 lít mỗi ngày.',
                        'Kê đơn thuốc chẹn thụ thể angiotensin losartan 50mg/ngày điều trị tăng huyết áp bảo vệ thận, '
                        'hướng dẫn chế độ ăn giảm muối dưới 5g/ngày và hạn chế lượng đạm vừa phải 0.8g/kg/ngày.',
                        'Chụp MRI thận đánh giá phân loại Mayo xác định nguy cơ tiến triển suy thận mạn, tầm soát '
                        'phình mạch máu não bằng chụp MRA sọ não nếu tiền sử gia đình có người vỡ phình mạch.',
                        'Xét nghiệm định kỳ creatinin máu protein niệu 24 giờ và điện giải đồ mỗi 3-6 tháng, tư vấn '
                        'dùng thuốc đối vận thụ thể vasopressin V2 tolvaptan nếu thuộc nhóm nguy cơ tiến triển nhanh.',
                        'Hướng dẫn bệnh nhân tránh các môn thể thao va chạm mạnh đối kháng để phòng ngừa vỡ nang thận, '
                        'uống đủ nước đều đặn kể cả ban đêm để ức chế bài tiết vasopressin nội sinh.',
                        'Tư vấn di truyền cho các thành viên trực hệ trong gia đình (con cái trên 18 tuổi) thực hiện '
                        'siêu âm sàng lọc thận, theo dõi chặt chẽ khi có cơn đau hông lưng cấp tính.'],
  'bien_the_kham': ['Huyết áp đo tại phòng khám 150/95 mmHg, sờ nắn sâu hai bên hông lưng phát hiện hai thận to gồ ghề '
                    'bề mặt có nhiều khối nang chắc không đều, nghiệm pháp bập bềnh thận dương tính cả hai bên, tim '
                    'mạch nhịp đều T1 T2 rõ không có tiếng thổi.',
                    'Khám bụng thấy hai bên mạn sườn nhô cao bất thường, sờ thấy cực dưới hai thận to vượt quá rốn bề '
                    'mặt mấp mô dạng chùm nho, ấn tức nhẹ không có phản ứng thành bụng, huyết áp 145/90 mmHg.',
                    'Hai thận to rõ rệt khi sờ nắn hai tay bập bềnh thận dương tính rõ, không nghe thấy tiếng thổi '
                    'động mạch thận hai bên, khám gan sờ thấy bờ dưới gan mấp mô vài nang nhỏ kèm theo.',
                    'Bệnh nhân thể trạng tốt, huyết áp tăng vừa, gõ đục vùng mạn sườn do khối thận phì đại chiếm chỗ, '
                    'tim nghe có tiếng T4 nhẹ ở mỏm tim, không có phù ngoại biên chân.',
                    'Khám hệ tiết niệu phát hiện khối thận hai bên kích thước lớn dọc hố thắt lưng, ấn tức nhẹ vùng '
                    'hông lưng bên phải nơi vừa có đợt tiểu máu tự hết, bụng mềm.',
                    'Bệnh nhân có bụng bè sang hai bên, nắn thận to cả hai bên bề mặt chắc sần sùi nhiều nang, huyết '
                    'áp đo tay phải 155/95 mmHg, đáy mắt có dấu hiệu co nhỏ tiểu động mạch do tăng áp.'],
  'chan_doan': 'Thận đa nang di truyền trội ADPKD giai đoạn bảo tồn chức năng thận.',
  'chinh': ['tiền sử gia đình có bố mẹ hoặc anh chị em ruột được chẩn đoán thận đa nang',
            'đau âm ỉ hai bên mạn sườn và vùng hông lưng tăng dần theo thời gian',
            'tăng huyết áp khởi phát từ độ tuổi 30-40 tuổi khó kiểm soát'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Siêu âm hoặc chụp cộng hưởng từ MRI hệ tiết niệu đo tổng thể tích thận nang TKV, xét nghiệm chức năng '
              'thận urê creatinin máu và độ lọc cầu thận ước tính eGFR, kiểm soát huyết áp mục tiêu dưới 130/80 mmHg '
              'ưu tiên dùng thuốc ức chế men chuyển hoặc chẹn thụ thể ARB, khuyến khích uống nhiều nước trên 2.5-3 lít '
              'mỗi ngày.',
  'kham': 'Huyết áp đo tại phòng khám 150/95 mmHg, sờ nắn sâu hai bên hông lưng phát hiện hai thận to gồ ghề bề mặt có '
          'nhiều khối nang chắc không đều, nghiệm pháp bập bềnh thận dương tính cả hai bên, tim mạch nhịp đều T1 T2 rõ '
          'không có tiếng thổi.',
  'nhom': 'người lớn',
  'phu': ['thỉnh thoảng xuất hiện các đợt tiểu ra máu đại thể do vỡ nang thận nhỏ',
          'nhiễm trùng đường tiết niệu hoặc sỏi thận tái diễn nhiều đợt',
          'bụng to dần hai bên sờ thấy khối gồ ghề vùng mạn sườn thắt lưng'],
  'ten': 'thận đa nang di truyền trội'},
 {'bien_the_chan_doan': ['Hẹp niệu đạo sau chấn thương đoạn niệu đạo hành.',
                         'Theo dõi hẹp niệu đạo sau chấn thương gây ứ đọng nước tiểu mạn tính.',
                         'Hẹp niệu đạo sau chấn thương mức độ khít đoạn ngắn dưới 2cm.',
                         'Hẹp niệu đạo sau chấn thương biến chứng nhiễm trùng tiết niệu tái phát.',
                         'Theo dõi hẹp niệu đạo sau chấn thương tái hẹp sau nong niệu đạo.',
                         'Hẹp niệu đạo sau chấn thương đoạn niệu đạo màng do vỡ khung chậu cũ.'],
  'bien_the_ke_hoach': ['Chỉ định chụp X-quang niệu đạo bàng quang ngược dòng kết hợp xuôi dòng khi đi tiểu (RUG/VCUG) '
                        'để xác định chính xác vị trí và độ dài đoạn hẹp, đo niệu dòng đồ đánh giá lưu lượng dòng tiểu '
                        'cực đại Qmax, hội chẩn chuyên khoa ngoại tiết niệu chỉ định nội soi xẻ hẹp niệu đạo bằng dao '
                        'lạnh hoặc phẫu thuật tạo hình niệu đạo cắt nối tận-tận.',
                        'Cấy nước tiểu làm kháng sinh đồ loại trừ nhiễm khuẩn trước can thiệp thủ thuật, chụp phim '
                        'niệu đạo ngược dòng RUG xác định vị trí đoạn xơ, chuẩn bị lịch phẫu thuật tạo hình niệu đạo '
                        'có vạt da hoặc niêm mạc miệng.',
                        'Tư vấn các phương pháp điều trị gồm nội soi xẻ rộng niệu đạo có đặt stent tạm thời hoặc phẫu '
                        'thuật mở tạo hình niệu đạo triệt để, tránh tự ý dùng que nong thô bạo tại nhà.',
                        'Kê đơn thuốc kháng sinh dự phòng chống nhiễm khuẩn và thuốc chống co thắt cơ trơn bàng quang '
                        'trong thời gian chờ mổ, siêu âm theo dõi đài bể thận phòng ngừa ứ nước ngược dòng.',
                        'Hướng dẫn bệnh nhân theo dõi sát lượng nước tiểu, nếu bí tiểu hoàn toàn cần đến viện cấp cứu '
                        'ngay để chọc dẫn lưu bàng quang trên xương mu bằng ống thông trocar.',
                        'Thực hiện đo thể tích tồn lưu bàng quang sau tiểu định kỳ, hẹn hội chẩn phẫu thuật viên niệu '
                        'khoa chuyên sâu về phẫu thuật tái tạo niệu đạo.'],
  'bien_the_kham': ['Sờ nắn dọc theo đường đi của niệu đạo vùng tầng sinh môn phát hiện một đoạn xơ chai cứng chắc dài '
                    'khoảng 1.5cm ấn tức nhẹ, khám bàng quang sau khi đi tiểu thấy có khối căng nhẹ trên mu, siêu âm '
                    'đo lượng nước tiểu tồn dư sau tiểu PVR đạt 130ml.',
                    'Khám tầng sinh môn có vết sẹo mờ chấn thương cũ, sờ thân niệu đạo trước thấy đoạn xơ cứng mất '
                    'tính đàn hồi, bàng quang sau tiểu vẫn còn đọng dịch trên siêu âm, lỗ sáo niệu đạo ngoài không '
                    'hẹp.',
                    'Đo niệu dòng đồ cho thấy đường biểu diễn dẹt dạng cao nguyên điển hình của tắc nghẽn hạ lưu, tốc '
                    'độ dòng cực đại Qmax giảm sâu còn 6.5 ml/s, ấn hạ vị bệnh nhân thấy tức buốt nhẹ.',
                    'Bệnh nhân rặn tiểu khó khăn tia nước tiểu mảnh như sợi chỉ, khám cơ quan sinh dục ngoài bình '
                    'thường không sưng tấy mưng mủ, không có ổ rò nước tiểu tầng sinh môn.',
                    'Khám vùng đáy chậu sờ thấy dải xơ hóa quanh niệu đạo hành, bàng quang căng vừa sau rặn tiểu, que '
                    'thông niệu đạo số 16 Fr bị tắc nghẽn không thể đi qua đoạn niệu đạo trước.',
                    'Bệnh nhân có biểu hiện tiểu khó tắc nghẽn mạn tính, sẹo xơ chai vùng đáy chậu ấn tức, thành bàng '
                    'quang dày nhẹ trên siêu âm do phì đại cơ bức niệu phản ứng chống lại tắc nghẽn.'],
  'chan_doan': 'Hẹp niệu đạo sau chấn thương đoạn niệu đạo hành.',
  'chinh': ['tiền sử chấn thương va đập mạnh vùng tầng sinh môn hoặc ngã kiểu xoạc chân',
            'tia nước tiểu nhỏ dần phân tán nhiều tia hoặc chảy yếu thành giọt',
            'phải rặn mạnh khi đi tiểu thời gian một lần đi tiểu kéo dài rất lâu'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Chỉ định chụp X-quang niệu đạo bàng quang ngược dòng kết hợp xuôi dòng khi đi tiểu (RUG/VCUG) để xác '
              'định chính xác vị trí và độ dài đoạn hẹp, đo niệu dòng đồ đánh giá lưu lượng dòng tiểu cực đại Qmax, '
              'hội chẩn chuyên khoa ngoại tiết niệu chỉ định nội soi xẻ hẹp niệu đạo bằng dao lạnh hoặc phẫu thuật tạo '
              'hình niệu đạo cắt nối tận-tận.',
  'kham': 'Sờ nắn dọc theo đường đi của niệu đạo vùng tầng sinh môn phát hiện một đoạn xơ chai cứng chắc dài khoảng '
          '1.5cm ấn tức nhẹ, khám bàng quang sau khi đi tiểu thấy có khối căng nhẹ trên mu, siêu âm đo lượng nước tiểu '
          'tồn dư sau tiểu PVR đạt 130ml.',
  'nhom': 'người lớn',
  'phu': ['cảm giác tiểu không hết nước tiểu còn ứ đọng lại trong bàng quang',
          'nước tiểu nhỏ giọt rỉ rả sau khi đã đi tiểu xong làm ướt quần',
          'thỉnh thoảng có cảm giác đau tức dọc theo đường đi của niệu đạo khi rặn'],
  'ten': 'hẹp niệu đạo sau chấn thương'},
 {'bien_the_chan_doan': ['Sỏi san hô đài bể thận bên phải gây ứ nước thận độ 2.',
                         'Theo dõi sỏi san hô đài bể thận bên trái thể toàn phần có nhiễm khuẩn niệu.',
                         'Sỏi san hô đài bể thận bán phần kèm suy giảm chức năng lọc một bên thận.',
                         'Sỏi san hô đài bể thận trên thận ứ mủ mạn tính.',
                         'Theo dõi sỏi san hô đài bể thận sỏi struvite do vi khuẩn sinh men urease.',
                         'Sỏi san hô đài bể thận hai bên giai đoạn chưa suy thận mạn tính.'],
  'bien_the_ke_hoach': ['Chụp cắt lớp vi tính CT hệ tiết niệu không tiêm cản quang dựng hình 3D đánh giá kích thước '
                        'phân nhánh đài thận và đậm độ Hounsfield của sỏi san hô, cấy nước tiểu làm kháng sinh đồ điều '
                        'trị triệt để nhiễm trùng trước mổ, chỉ định phẫu thuật tán sỏi thận qua da đường hầm nhỏ PCNL '
                        'hoặc kết hợp nội soi tán sỏi ngược dòng qua ống mềm ECIRS.',
                        'Làm xạ hình thận DMSA đánh giá tỷ lệ phần trăm chức năng thận từng bên, cấy vi trùng nước '
                        'tiểu dùng kháng sinh nhạy cảm ít nhất 1 tuần trước can thiệp ngoại khoa.',
                        'Xét nghiệm công thức máu chức năng đông máu urê creatinin điện giải đồ, giải thích kế hoạch '
                        'tán sỏi thận qua da PCNL có thể cần thực hiện 2 thì hoặc mở nhiều đường hầm.',
                        'Chỉ định chụp CT xoắn ốc hệ niệu khảo sát mối tương quan của thận với đại tràng và màng phổi '
                        'để chọn đường chọc hút an toàn vào đài thận, điều trị ổn định huyết áp.',
                        'Kê đơn kháng sinh đường uống cephalosporin phối hợp kiềm hóa nước tiểu nếu là sỏi acid uric, '
                        'hướng dẫn uống nhiều nước lọc 2.5 lít/ngày trong giai đoạn chuẩn bị mổ.',
                        'Tư vấn sau khi sạch sỏi cần làm xét nghiệm phân tích thành phần sỏi và bilan chuyển hóa '
                        'khoáng chất niệu 24 giờ để xây dựng phác đồ dự phòng sỏi tái phát.'],
  'bien_the_kham': ['Khám hố thắt lưng bên phải đầy hơn bên đối diện, chạm thận bập bềnh thận dương tính nhẹ, gõ rung '
                    'thận bên phải tức đau rõ, ấn điểm sườn lưng đau tức, sinh hiệu ổn định thân nhiệt 37.2 độ C, '
                    'huyết áp 130/80 mmHg.',
                    'Bệnh nhân than đau tức mạn sườn lưng kéo dài, thận phải to nhẹ sờ thấy cực dưới trơn láng, ấn '
                    'điểm sườn cột sống bên phải đau chói nhẹ, nước tiểu lấy ra hơi đục nhẹ.',
                    'Khám vùng thắt lưng bên có sỏi cơ cạnh sống co cứng nhẹ, nghiệm pháp rung thận dương tính, khám '
                    'tim phổi bình thường, xét nghiệm que thử nước tiểu nitrit dương tính và bạch cầu niệu 2+.',
                    'Thể trạng gầy nhẹ, da hơi nhợt do nhiễm trùng đường tiểu mạn tính, sờ nắn thận bên trái bình '
                    'thường, thận bên phải to ấn tức ê ẩm lan ra trước bụng, bụng mềm.',
                    'Khám hệ tiết niệu không có cơn đau quặn thận cấp, thận phải to độ 1 chạm thận dương tính, gõ đục '
                    'vùng hông lưng, không có cầu bàng quang, huyết áp ổn định.',
                    'Ấn tức rõ rệt ở góc sườn đốt sống thứ 12 bên phải, khám loại trừ các bệnh lý cột sống thắt lưng, '
                    'siêu âm tại giường thấy khối sỏi cản âm lớn phân nhánh chiếm trọn đài bể thận kèm giãn đài thận.'],
  'chan_doan': 'Sỏi san hô đài bể thận bên phải gây ứ nước thận độ 2.',
  'chinh': ['đau mỏi âm ỉ nặng tức vùng hông lưng bên có sỏi kéo dài nhiều tháng',
            'tiền sử nhiễm trùng đường tiết niệu tái phát nhiều đợt với nước tiểu đục',
            'xét nghiệm nước tiểu thường xuyên có bạch cầu và hồng cầu vi thể dai dẳng'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Chụp cắt lớp vi tính CT hệ tiết niệu không tiêm cản quang dựng hình 3D đánh giá kích thước phân nhánh '
              'đài thận và đậm độ Hounsfield của sỏi san hô, cấy nước tiểu làm kháng sinh đồ điều trị triệt để nhiễm '
              'trùng trước mổ, chỉ định phẫu thuật tán sỏi thận qua da đường hầm nhỏ PCNL hoặc kết hợp nội soi tán sỏi '
              'ngược dòng qua ống mềm ECIRS.',
  'kham': 'Khám hố thắt lưng bên phải đầy hơn bên đối diện, chạm thận bập bềnh thận dương tính nhẹ, gõ rung thận bên '
          'phải tức đau rõ, ấn điểm sườn lưng đau tức, sinh hiệu ổn định thân nhiệt 37.2 độ C, huyết áp 130/80 mmHg.',
  'nhom': 'người lớn',
  'phu': ['thỉnh thoảng có các đợt sốt nhẹ gai rét kèm nước tiểu có mùi hôi',
          'mệt mỏi ăn uống kém do chức năng thận bên tổn thương giảm sút',
          'rất ít khi có cơn đau quặn thận điển hình do sỏi kích thước lớn đúc khuôn cố định'],
  'ten': 'sỏi san hô đài bể thận'},
 {'bien_the_chan_doan': ['Trào ngược bàng quang niệu quản người lớn độ 3 gây viêm thận mạn tính.',
                         'Theo dõi trào ngược bàng quang niệu quản người lớn nguyên phát hai bên.',
                         'Trào ngược bàng quang niệu quản người lớn thứ phát sau bàng quang tăng hoạt.',
                         'Trào ngược bàng quang niệu quản người lớn biến chứng tạo sẹo xơ thận khu trú.',
                         'Theo dõi trào ngược bàng quang niệu quản người lớn độ 4 có giãn niệu quản ngoằn ngoèo.',
                         'Trào ngược bàng quang niệu quản người lớn ổn định sau điều trị nội khoa.'],
  'bien_the_ke_hoach': ['Chỉ định chụp bàng quang niệu đạo khi đi tiểu (VCUG) để xác định mức độ luồng trào ngược nước '
                        'tiểu từ bàng quang lên niệu quản đài thận, xạ hình thận DMSA đánh giá sẹo xơ vỏ thận, dùng '
                        'kháng sinh dự phòng liều thấp vào ban đêm nitrofurantoin hoặc trimethoprim, hội chẩn phẫu '
                        'thuật nội soi bơm chất làm phồng miệng niệu quản Deflux hoặc phẫu thuật cắm lại niệu quản vào '
                        'bàng quang theo phương pháp Cohen.',
                        'Chụp niệu động học đánh giá áp lực buồng bàng quang loại trừ hội chứng van niệu đạo sau hoặc '
                        'rối loạn chức năng bàng quang thần kinh gây trào ngược thứ phát, hướng dẫn đi tiểu hai thì '
                        'làm sạch bàng quang.',
                        'Kê đơn kháng sinh dự phòng trimethoprim 100mg uống trước khi đi ngủ, kiểm tra cấy nước tiểu '
                        'định kỳ hàng tháng, theo dõi huyết áp chặt chẽ tại nhà.',
                        'Chỉ định chụp MRI tiết niệu hoặc CT Urography khảo sát giải phẫu chỗ nối bàng quang niệu '
                        'quản, kiểm tra chức năng thận eGFR định kỳ 6 tháng một lần.',
                        'Tư vấn người bệnh về can thiệp nội soi ít xâm lấn bơm copolymer dextranomer/hyaluronic acid '
                        'quanh lỗ niệu quản chống trào ngược, hẹn lịch nhập viện khi có sốt đau thắt lưng.',
                        'Hướng dẫn chế độ sinh hoạt uống đủ nước, không nhịn tiểu quá 3 giờ, điều trị dứt điểm tình '
                        'trạng táo bón mạn tính đi kèm nhằm giảm áp lực ổ bụng.'],
  'bien_the_kham': ['Khám hông lưng hai bên đối xứng không sưng gồ, gõ rung thận bên nghi ngờ trào ngược thấy tức nhẹ, '
                    'huyết áp 138/88 mmHg, tim phổi bình thường, bụng mềm không sờ thấy khối u hay thận to ứ nước '
                    'nặng.',
                    'Bệnh nhân mô tả rõ cơn đau tức thắt lưng xuất hiện đồng thời khi bàng quang co bóp đi tiểu, khám '
                    'ấn điểm niệu quản trên không đau, xét nghiệm nước tiểu có bạch cầu niệu 1+.',
                    'Khám lâm sàng phát hiện huyết áp tăng nhẹ ở người tuổi 35, thận hai bên không to, bàng quang sau '
                    'tiểu không căng, các dấu hiệu thần kinh chi dưới bình thường.',
                    'Thể trạng tốt, không sốt tại thời điểm khám, gõ vùng thận hai bên có cảm giác tức ê hông lưng '
                    'phải, siêu âm thấy giãn nhẹ niệu quản đoạn chậu và đài bể thận phải sau khi bệnh nhân nhịn tiểu '
                    'căng.',
                    'Bệnh nhân có tiền sử nhiễm trùng tiểu nhiều lần, khám bụng mềm không chướng, ấn các điểm đau niệu '
                    'quản âm tính, xét nghiệm máu creatinin máu 105 umol/l.',
                    'Khám tuần hoàn hô hấp ổn định, vùng hố thắt lưng không đầy, rung thận âm tính khi bàng quang rỗng '
                    'nhưng tức rõ khi bàng quang đầy nước tiểu, tim đều T1 T2 rõ.'],
  'chan_doan': 'Trào ngược bàng quang niệu quản người lớn độ 3 gây viêm thận mạn tính.',
  'chinh': ['đau tức âm ỉ vùng hông lưng một hoặc hai bên tăng vọt ngay trong lúc đang rặn tiểu',
            'tiền sử nhiều đợt viêm đài bể thận cấp tái diễn từ trước đến nay',
            'xét nghiệm nước tiểu phát hiện protein niệu dai dẳng và suy giảm dần chức năng thận'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Chỉ định chụp bàng quang niệu đạo khi đi tiểu (VCUG) để xác định mức độ luồng trào ngược nước tiểu từ '
              'bàng quang lên niệu quản đài thận, xạ hình thận DMSA đánh giá sẹo xơ vỏ thận, dùng kháng sinh dự phòng '
              'liều thấp vào ban đêm nitrofurantoin hoặc trimethoprim, hội chẩn phẫu thuật nội soi bơm chất làm phồng '
              'miệng niệu quản Deflux hoặc phẫu thuật cắm lại niệu quản vào bàng quang theo phương pháp Cohen.',
  'kham': 'Khám hông lưng hai bên đối xứng không sưng gồ, gõ rung thận bên nghi ngờ trào ngược thấy tức nhẹ, huyết áp '
          '138/88 mmHg, tim phổi bình thường, bụng mềm không sờ thấy khối u hay thận to ứ nước nặng.',
  'nhom': 'người lớn',
  'phu': ['tiểu nhiều lần tiểu gấp cảm giác bàng quang chưa rỗng sau tiểu',
          'huyết áp tăng dần ở người độ tuổi thanh niên hoặc trung niên',
          'nước tiểu đục từng đợt kèm sốt nóng gai rét khi có nhiễm trùng ngược dòng'],
  'ten': 'trào ngược bàng quang niệu quản người lớn'},
 {'bien_the_chan_doan': ['Sa bàng quang độ 2 thành trước âm đạo.',
                         'Theo dõi sa bàng quang độ 2 có triệu chứng tiểu khó tắc nghẽn cơ học.',
                         'Sa bàng quang độ 2 kết hợp són tiểu khi gắng sức nhẹ.',
                         'Sa bàng quang độ 2 có chỉ định đặt vòng nâng pessary bảo tồn.',
                         'Theo dõi sa bàng quang độ 2 ở phụ nữ mãn kinh suy giảm trương lực cơ đáy chậu.',
                         'Sa bàng quang độ 2 giai đoạn ổn định sau can thiệp tập sàn chậu.'],
  'bien_the_ke_hoach': ['Tư vấn và hướng dẫn kỹ thuật bài tập phục hồi chức năng cơ sàn chậu Kegel kiên trì hàng ngày, '
                        'đặt vòng nâng âm đạo silicon pessary hỗ trợ cơ học nâng đỡ thành trước bàng quang, tư vấn '
                        'điều chỉnh lối sống tránh mang vác vật nặng trên 5kg và điều trị dứt điểm táo bón ho mạn '
                        'tính, hẹn tái khám sau 3 tháng đánh giá chỉ định phẫu thuật khâu phục hồi thành âm đạo nếu '
                        'triệu chứng không thuyên giảm.',
                        'Chọn kích cỡ vòng nâng pessary dạng vòng có núm nâng đỡ phù hợp đặt vào âm đạo thử nghiệm, '
                        'hướng dẫn người bệnh cách tự tháo lắp vệ sinh vòng nâng mỗi tuần.',
                        'Chỉ định tập phục hồi chức năng sàn chậu với máy kích thích điện sinh học và phản hồi sinh '
                        'học biofeedback, kê kem bôi estrogen tại chỗ làm dày biểu mô thành âm đạo trước khi đặt vòng.',
                        'Tư vấn chế độ ăn giàu chất xơ uống đủ nước để đi ngoài phân mềm tránh rặn mạnh làm nặng thêm '
                        'tình trạng sa tạng, hướng dẫn bài tập siết cơ đáy chậu trước khi nâng đồ vật.',
                        'Hẹn tái khám sau 4 tuần kiểm tra niêm mạc âm đạo có bị trợt do vòng nâng hay không, nếu không '
                        'dung nạp vòng nâng sẽ tư vấn phẫu thuật nội soi đặt lưới nâng bàng quang.',
                        'Lập hồ sơ quản lý bệnh lý sàn chậu nữ, đo lượng nước tiểu tồn dư sau tiểu định kỳ, dặn dò các '
                        'dấu hiệu viêm nhiễm âm đạo hoặc tắc tiểu cấp để đi khám lại ngay.'],
  'bien_the_kham': ['Khám phụ khoa ở tư thế sản khoa bảo bệnh nhân rặn mạnh (nghiệm pháp Valsalva) thấy thành trước âm '
                    'đạo sa xuống tới ngang mức màng trinh nhưng chưa vượt ra ngoài quá 1cm (sa bàng quang độ 2 theo '
                    'hệ thống phân loại POP-Q), bàng quang phồng tròn dưới niêm mạc, kiểm tra cơ sàn chậu yếu.',
                    'Đặt mỏ vịt một lá van đẩy thành sau thấy thành trước âm đạo phồng sa xuống che lấp một phần lỗ âm '
                    'đạo khi tăng áp lực ổ bụng, đo điểm Ba là 0cm tương đương sa độ 2.',
                    'Khám thấy khối sa mềm xẹp xuống khi dùng ngón tay ấn đẩy lên trên, niêm mạc thành âm đạo trùm lên '
                    'khối sa còn nguyên vẹn không trầy loét, nghiệm pháp ho són tiểu âm tính khi nâng khối sa.',
                    'Cơ nâng hậu môn hai bên co thắt yếu khi bảo bệnh nhân siết chặt đáy chậu (thang điểm Oxford 2/5), '
                    'khối thành trước âm đạo tụt xuống gần mép ngoài màng trinh khi đứng dậy rặn.',
                    'Khám phụ khoa ghi nhận sa thành trước bàng quang mức độ trung bình, cổ tử cung ở vị trí bình '
                    'thường không sa, siêu âm vùng chậu đo lượng nước tiểu tồn dư sau tiểu PVR 35ml.',
                    'Bệnh nhân có khối phồng rõ ở cửa mình khi ho mạnh, niêm mạc không viêm đỏ, sờ bàng quang căng '
                    'phồng sau khối sa, ấn đẩy bàng quang lên giúp giải phóng dòng tiểu thông suốt.'],
  'chan_doan': 'Sa bàng quang độ 2 thành trước âm đạo.',
  'chinh': ['cảm giác có khối phồng sa xuống cửa mình âm đạo khi đứng lâu hoặc khi ho rặn',
            'cảm giác tức nặng trì trệ vùng đáy chậu tăng dần về cuối ngày',
            'tiểu khó dòng tiểu yếu phải dùng ngón tay đẩy khối sa lên mới tiểu hết được'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thận - tiết niệu',
  'ke_hoach': 'Tư vấn và hướng dẫn kỹ thuật bài tập phục hồi chức năng cơ sàn chậu Kegel kiên trì hàng ngày, đặt vòng '
              'nâng âm đạo silicon pessary hỗ trợ cơ học nâng đỡ thành trước bàng quang, tư vấn điều chỉnh lối sống '
              'tránh mang vác vật nặng trên 5kg và điều trị dứt điểm táo bón ho mạn tính, hẹn tái khám sau 3 tháng '
              'đánh giá chỉ định phẫu thuật khâu phục hồi thành âm đạo nếu triệu chứng không thuyên giảm.',
  'kham': 'Khám phụ khoa ở tư thế sản khoa bảo bệnh nhân rặn mạnh (nghiệm pháp Valsalva) thấy thành trước âm đạo sa '
          'xuống tới ngang mức màng trinh nhưng chưa vượt ra ngoài quá 1cm (sa bàng quang độ 2 theo hệ thống phân loại '
          'POP-Q), bàng quang phồng tròn dưới niêm mạc, kiểm tra cơ sàn chậu yếu.',
  'nhom': 'người lớn',
  'phu': ['tiểu rắt tiểu ngắt quãng hoặc són tiểu khi ho hắt hơi cười lớn',
          'tiền sử mang thai sinh nở nhiều lần bằng đường âm đạo hoặc lao động nặng',
          'cảm giác vướng cộm khó chịu tại chỗ khi đi lại hoặc khi quan hệ'],
  'ten': 'sa bàng quang độ 2'},
 {'bien_the_chan_doan': ['Viêm tuyến tiền liệt mạn tính không do vi khuẩn hội chứng đau chậu mạn tính CPPS.',
                         'Theo dõi viêm tuyến tiền liệt mạn tính không do vi khuẩn thể có viêm IIIa.',
                         'Viêm tuyến tiền liệt mạn tính không do vi khuẩn thể không viêm IIIb đau vùng chậu.',
                         'Viêm tuyến tiền liệt mạn tính không do vi khuẩn có triệu chứng đau khi xuất tinh.',
                         'Theo dõi viêm tuyến tiền liệt mạn tính không do vi khuẩn kèm rối loạn lo âu nhẹ.',
                         'Viêm tuyến tiền liệt mạn tính không do vi khuẩn giai đoạn thuyên giảm từng phần.'],
  'bien_the_ke_hoach': ['Phác đồ phối hợp thuốc chẹn alpha-1 tamsulosin 0.4mg/ngày làm giãn cơ trơn cổ bàng quang và '
                        'tuyến tiền liệt, thuốc kháng viêm không steroid celecoxib 200mg/ngày từng đợt ngắn 2-4 tuần, '
                        'thuốc giãn cơ tolperisone, tư vấn liệu pháp tâm lý giải tỏa căng thẳng kết hợp tắm ngâm nước '
                        'ấm vùng chậu đáy chậu hàng ngày.',
                        'Kê đơn alfuzosin 10mg uống sau bữa tối trong 6-12 tuần, bổ sung chiết xuất phấn hoa cernilton '
                        'hoặc chiết xuất thảo dược quercetin hỗ trợ chống viêm mô kẽ tuyến tiền liệt.',
                        'Tư vấn bệnh nhân chế độ sinh hoạt tình dục điều độ xuất tinh đều đặn 2-3 lần/tuần giúp thông '
                        'thoáng ống tuyến, tránh ngồi lâu liên tục trên đệm cứng, sử dụng gối đệm hình chữ U.',
                        'Kết hợp thuốc giảm đau điều hòa thần kinh pregabalin 75mg uống tối nếu đau nhiều dẫn truyền '
                        'thần kinh, tập vật lý trị liệu thư giãn cơ sàn chậu và cơ đáy chậu.',
                        'Khuyên kiêng hẳn rượu bia cà phê đồ ăn nhiều gia vị ớt tiêu cay nóng, tránh đi xe đạp đường '
                        'dài gây chèn ép cơ học trực tiếp vào vùng tầng sinh môn.',
                        'Đánh giá lại triệu chứng bằng thang điểm NIH-CPSI sau 6 tuần điều trị, động viên tâm lý người '
                        'bệnh kiên trì vì bệnh lành tính nhưng diễn tiến kéo dài cần thời gian.'],
  'bien_the_kham': ['Thăm trực tràng chạm tuyến tiền liệt kích thước hơi to nhẹ mật độ mềm đều không có nhân cứng, ấn '
                    'tức nhẹ lan tỏa không đau chói dữ dội, xét nghiệm dịch xoa bóp tuyến tiền liệt EPS có nhiều bạch '
                    'cầu trên 10 bạch cầu/vi trường nhưng cấy vi khuẩn âm tính (hội chứng CPPS thể viêm IIIa).',
                    'Khám trực tràng thấy hai thùy tuyến tiền liệt đối xứng ranh giới rõ bề mặt nhẵn ấn căng tức nhẹ, '
                    'cơ thắt hậu môn và cơ nâng hậu môn co cứng nhẹ do đau mạn, xét nghiệm nước tiểu 2 cốc sau xoa bóp '
                    'tuyến không có vi khuẩn mọc.',
                    'Bệnh nhân than đau nhiều ở vùng tầng sinh môn khi ngồi ghế cứng lâu, thăm trực tràng tuyến tiền '
                    'liệt không đau chói cấp tính, xét nghiệm PSA toàn phần trong giới hạn bình thường 1.2 ng/ml.',
                    'Khám hệ sinh dục ngoài bình thường không sưng tinh hoàn, thăm tuyến tiền liệt mật độ đàn hồi hơi '
                    'sung huyết nhẹ, cấy dịch niệu đạo tìm lậu cầu Chlamydia và Mycoplasma đều âm tính.',
                    'Điểm đau vùng chậu mạn tính dương tính khi ấn sâu trên xương mu và vùng đáy chậu, thang điểm đánh '
                    'giá triệu chứng viêm tuyến tiền liệt mãn NIH-CPSI đạt 22 điểm (mức độ trung bình-nặng).',
                    'Thăm khám trực tràng nhẹ nhàng tuyến tiền liệt mềm không nóng, không có dấu hiệu ổ áp xe, nghiệm '
                    'pháp Stamey-Meares 4 cốc khẳng định không có vi khuẩn phát triển.'],
  'chan_doan': 'Viêm tuyến tiền liệt mạn tính không do vi khuẩn hội chứng đau chậu mạn tính CPPS.',
  'chinh': ['đau tức âm ỉ dai dẳng vùng đáy chậu tầng sinh môn bìu và trên xương mu trên 3 tháng',
            'cảm giác đau rát buốt dọc niệu đạo hoặc đau chói trong và sau khi xuất tinh',
            'tiểu buốt nhẹ dòng nước tiểu yếu ngập ngừng và cảm giác tiểu không hết'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Phác đồ phối hợp thuốc chẹn alpha-1 tamsulosin 0.4mg/ngày làm giãn cơ trơn cổ bàng quang và tuyến tiền '
              'liệt, thuốc kháng viêm không steroid celecoxib 200mg/ngày từng đợt ngắn 2-4 tuần, thuốc giãn cơ '
              'tolperisone, tư vấn liệu pháp tâm lý giải tỏa căng thẳng kết hợp tắm ngâm nước ấm vùng chậu đáy chậu '
              'hàng ngày.',
  'kham': 'Thăm trực tràng chạm tuyến tiền liệt kích thước hơi to nhẹ mật độ mềm đều không có nhân cứng, ấn tức nhẹ '
          'lan tỏa không đau chói dữ dội, xét nghiệm dịch xoa bóp tuyến tiền liệt EPS có nhiều bạch cầu trên 10 bạch '
          'cầu/vi trường nhưng cấy vi khuẩn âm tính (hội chứng CPPS thể viêm IIIa).',
  'nhom': 'người lớn',
  'phu': ['đau tức lan tỏa ra vùng thắt lưng cùng cụt và mặt trong hai bên đùi',
          'rối loạn chức năng cương dương và suy giảm ham muốn do tâm lý lo âu kéo dài',
          'các xét nghiệm cấy mẫu dịch tuyến tiền liệt và nước tiểu đều không tìm thấy vi khuẩn'],
  'ten': 'viêm tuyến tiền liệt mạn tính không do vi khuẩn'},
 {'bien_the_chan_doan': ['Viêm tuyến tiền liệt cấp do vi khuẩn có dọa bí tiểu cấp.',
                         'Theo dõi viêm tuyến tiền liệt cấp do vi khuẩn biến chứng áp xe tuyến tiền liệt.',
                         'Viêm tuyến tiền liệt cấp do vi khuẩn sau can thiệp sinh thiết tuyến tiền liệt.',
                         'Viêm tuyến tiền liệt cấp do vi khuẩn do vi khuẩn Gram âm E. coli.',
                         'Theo dõi viêm tuyến tiền liệt cấp do vi khuẩn có hội chứng nhiễm khuẩn huyết.',
                         'Viêm tuyến tiền liệt cấp do vi khuẩn đáp ứng với kháng sinh đường tĩnh mạch.'],
  'bien_the_ke_hoach': ['Chỉ định nhập viện khoa Tiết niệu điều trị nội trú, cấy máu và cấy nước tiểu làm kháng sinh '
                        'đồ khẩn cấp, sử dụng kháng sinh phổ rộng đường tĩnh mạch ceftriaxone 2g/ngày phối hợp '
                        'gentamicin hoặc ciprofloxacin liều cao, hạ sốt giảm đau bằng paracetamol truyền tĩnh mạch, '
                        'nếu bí tiểu hoàn toàn chỉ định dẫn lưu bàng quang qua da trên xương mu tránh đặt ống thông '
                        'niệu đạo qua tuyến tiền liệt đang viêm mủ.',
                        'Thiết lập ngay đường truyền tĩnh mạch bù dịch ringer lactat, chỉ định cấy máu 2 vị trí và xét '
                        'nghiệm cấy vi trùng nước tiểu định danh, tiêm tĩnh mạch ampicillin kết hợp tobramycin hoặc '
                        'piperacillin/tazobactam.',
                        'Chỉ định siêu âm qua trực tràng hoặc chụp CT tiểu khung kiểm tra ổ hóa mủ áp xe trong nhu mô '
                        'tuyến, nếu có khối áp xe lớn hội chẩn chọc hút dẫn lưu mủ dưới hướng dẫn siêu âm.',
                        'Dùng thuốc hạ sốt giảm đau truyền tĩnh mạch, cho thuốc làm mềm phân tránh rặn đại tiện gây '
                        'đau đớn, tuyệt đối không đặt sonde tiểu qua niệu đạo nếu có bí tiểu mà làm thủ thuật chọc dẫn '
                        'lưu trên mu.',
                        'Theo dõi sinh hiệu mạch nhiệt độ huyết áp mỗi 3 giờ đánh giá nguy cơ sốc nhiễm trùng, chuyển '
                        'sang kháng sinh đường uống thích hợp đủ liệu trình 4-6 tuần sau khi hết sốt 48 giờ để diệt '
                        'sạch ổ vi khuẩn.',
                        'Xét nghiệm lại công thức máu CRP và tổng phân tích nước tiểu sau 72 giờ điều trị, bổ sung '
                        'thuốc chẹn alpha tamsulosin sau vài ngày khi giai đoạn cấp dịu bớt để cải thiện lưu lượng '
                        'tiểu.'],
  'bien_the_kham': ['Bệnh nhân sốt cao 39.2 độ C vẻ mặt nhiễm trùng môi khô, thăm khám trực tràng rất nhẹ nhàng thấy '
                    'tuyến tiền liệt sưng to căng mọng nóng rực và cực kỳ đau chói khi chạm nhẹ (chống chỉ định tuyệt '
                    'đối động tác xoa bóp tuyến vì nguy cơ phóng thích vi khuẩn gây sốc nhiễm trùng), ấn trên mu có '
                    'cầu bàng quang căng đau.',
                    'Bệnh nhân rét run mạch nhanh 110 ck/p huyết áp 115/70 mmHg, khám trực tràng phát hiện tuyến tiền '
                    'liệt phù nề đối xứng căng như quả bóng da chạm vào đau thốn dữ dội, nước tiểu lấy qua que sonde '
                    'dẫn lưu ra đục nhiều cặn lơ lửng.',
                    'Hội chứng đáp ứng viêm toàn thân SIRS dương tính với sốt 39 độ bạch cầu máu tăng cao 16.500/mm3 '
                    'chiếm 85% đa nhân trung tính, vùng đáy chậu căng tức nề nhẹ, tuyến tiền liệt qua thăm trực tràng '
                    'cực kỳ nhạy cảm đau.',
                    'Bệnh nhân vã mồ hôi đau quặn vùng hạ vị do ứ nước tiểu, thăm trực tràng thận trọng thấy tuyến '
                    'tiền liệt phồng to che lấp thành trước trực tràng ấn đau buốt lan lên thắt lưng, CRP huyết thanh '
                    'tăng vọt 85 mg/l.',
                    'Tình trạng nhiễm trùng rầm rộ, sốt cao liên tục không hạ, vùng hội âm nóng tức, thăm khám tuyến '
                    'tiền liệt sưng to căng bóng đau chói không sờ nắn mạnh, cầu bàng quang vượt trên khớp mu 3 khoát '
                    'ngón tay.',
                    'Bệnh nhân biểu hiện mệt lả do sốt cao rét run, khám nhẹ ngón tay qua hậu môn thấy tuyến tiền liệt '
                    'tăng nhiệt độ rõ rệt sưng nề toả nhiệt đau dữ dội, không có ổ rò mủ ra ngoài da.'],
  'chan_doan': 'Viêm tuyến tiền liệt cấp do vi khuẩn có dọa bí tiểu cấp.',
  'chinh': ['sốt cao đột ngột rét run đau đầu mệt mỏi toàn thân',
            'tiểu buốt rát dữ dội tiểu gấp dòng nước tiểu ngắt quãng yếu ớt',
            'đau nhức chói dữ dội vùng đáy chậu tầng sinh môn và hậu môn trực tràng'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Chỉ định nhập viện khoa Tiết niệu điều trị nội trú, cấy máu và cấy nước tiểu làm kháng sinh đồ khẩn '
              'cấp, sử dụng kháng sinh phổ rộng đường tĩnh mạch ceftriaxone 2g/ngày phối hợp gentamicin hoặc '
              'ciprofloxacin liều cao, hạ sốt giảm đau bằng paracetamol truyền tĩnh mạch, nếu bí tiểu hoàn toàn chỉ '
              'định dẫn lưu bàng quang qua da trên xương mu tránh đặt ống thông niệu đạo qua tuyến tiền liệt đang viêm '
              'mủ.',
  'kham': 'Bệnh nhân sốt cao 39.2 độ C vẻ mặt nhiễm trùng môi khô, thăm khám trực tràng rất nhẹ nhàng thấy tuyến tiền '
          'liệt sưng to căng mọng nóng rực và cực kỳ đau chói khi chạm nhẹ (chống chỉ định tuyệt đối động tác xoa bóp '
          'tuyến vì nguy cơ phóng thích vi khuẩn gây sốc nhiễm trùng), ấn trên mu có cầu bàng quang căng đau.',
  'nhom': 'người lớn',
  'phu': ['bí tiểu cấp tính bàng quang căng tức đầy nước tiểu không đi được',
          'nước tiểu đục có thể lẫn vài sợi máu tươi hoặc mủ ở cuối bãi',
          'cảm giác đau thốn tăng vọt khi ngồi hoặc khi đại tiện phân rắn'],
  'ten': 'viêm tuyến tiền liệt cấp do vi khuẩn'},
 {'bien_the_chan_doan': ['Xoắn tinh hoàn dọa nghẹt bên trái giờ thứ 3 cấp cứu ngoại khoa.',
                         'Theo dõi xoắn tinh hoàn dọa nghẹt bên phải đến sớm trước 6 giờ.',
                         'Xoắn tinh hoàn dọa nghẹt có thiếu máu nuôi tinh hoàn trên siêu âm Doppler.',
                         'Xoắn tinh hoàn dọa nghẹt thể xoắn ngoài bao tinh mạc cấp tính.',
                         'Theo dõi xoắn tinh hoàn dọa nghẹt nghi ngờ xoắn thừng tinh hoàn toàn.',
                         'Xoắn tinh hoàn dọa nghẹt giai đoạn thiếu máu cấp cứu bảo tồn.'],
  'bien_the_ke_hoach': ['Chỉ định siêu âm Doppler màu mạch máu tinh hoàn cấp cứu tại giường đánh giá phổ dòng chảy '
                        'động mạch tinh hoàn, thiết lập đường truyền tĩnh mạch giảm đau chống nôn, chuyển phòng mổ cấp '
                        'cứu tối khẩn tháo xoắn tinh hoàn và cố định tinh hoàn hai bên trong khung giờ vàng trước 6 '
                        'giờ để bảo tồn nhu mô tinh hoàn.',
                        'Báo động đỏ phòng mổ phẫu thuật cấp cứu tháo xoắn thừng tinh, làm xét nghiệm đông máu cơ bản '
                        'và nhóm máu khẩn, giải thích gia đình nguy cơ hoại tử phải cắt tinh hoàn nếu tưới máu không '
                        'hồi phục.',
                        'Siêu âm Doppler bìu khẩn xác định mất tín hiệu dòng máu tâm thu trong nhu mô tinh hoàn, chuẩn '
                        'bị mổ mở thăm dò đường bìu, ủ ấm tinh hoàn bằng gạc ấm đánh giá hồi phục màu sắc trước khi '
                        'quyết định bảo tồn.',
                        'Đặt đường truyền tĩnh mạch truyền dung dịch natri clorid 0.9%, dùng paracetamol truyền tĩnh '
                        'mạch giảm đau, cố định tạm thời và chuyển ngay lên phòng mổ ngoại niệu.',
                        'Tư vấn phẫu thuật tháo xoắn đồng thời cố định tinh hoàn đối bên phòng ngừa xoắn tái diễn '
                        'trong tương lai, hướng dẫn theo dõi teo tinh hoàn sau mổ.',
                        'Thực hiện thủ thuật xoay tháo xoắn bằng tay mở xoắn từ trong ra ngoài (kiểu mở sách) trong '
                        'lúc chuẩn bị phòng mổ nếu bác sĩ niệu khoa có kinh nghiệm, chuyển mổ ngay lập tức.'],
  'bien_the_kham': ['Bìu bên trái sưng to nề đỏ nhẹ, tinh hoàn trái co rút lên cao sát gốc dương vật và xoay nằm '
                    'ngang, sờ nắn cực kỳ đau chói khiến bệnh nhân gạt tay bác sĩ, thừng tinh dày và ngắn lại, mất '
                    'hoàn toàn phản xạ cơ bìu trái, dấu hiệu Prehn âm tính, sinh hiệu mạch nhanh 105 ck/p do đau.',
                    'Bệnh nhân vào viện vì đau bìu dữ dội bên phải, tinh hoàn phải to gấp đôi bên trái và treo cao, sờ '
                    'thừng tinh có nút xoắn đau buốt, nâng nhẹ bìu lên bệnh nhân đau thét (Prehn âm tính), da bìu căng '
                    'bóng.',
                    'Khám cấp cứu phát hiện tinh hoàn trái nằm trục ngang bất thường ở phần cao của bìu, phản xạ da '
                    'bìu bên trái biến mất hoàn toàn, bụng mềm không có viêm phúc mạc, nhịp tim nhanh 110 lần/phút.',
                    'Bìu sưng nề một bên không đối xứng, tinh hoàn bị kéo ngược lên lỗ bẹn nông, nắn nhẹ cực dưới rất '
                    'nhạy cảm đau chói, mào tinh hoàn quay ra phía trước, dấu hiệu xoắn thừng tinh rõ rệt.',
                    'Bệnh nhân ôm bìu đau đớn vã mồ hôi, tinh hoàn sưng căng chắc nhạy cảm đau tối đa, nghiệm pháp '
                    'Prehn âm tính điển hình giúp phân biệt với viêm mào tinh hoàn, nhiệt độ 37.1 độ C không sốt cao.',
                    'Khám vùng bìu bẹn thấy tinh hoàn bên tổn thương co rút lên cao, trục dọc tinh hoàn đổi thành trục '
                    'ngang, vuốt mặt trong đùi không thấy tinh hoàn co lên (mất phản xạ cơ bìu), huyết áp 140/90 mmHg '
                    'do đau kích thích.'],
  'chan_doan': 'Xoắn tinh hoàn dọa nghẹt bên trái giờ thứ 3 cấp cứu ngoại khoa.',
  'chinh': ['đau dữ dội đột ngột vùng bìu một bên lan dọc theo thừng tinh lên hố chậu cùng bên',
            'bìu bên tổn thương sưng to nề đỏ và bị kéo rút treo cao nằm ngang hơn bình thường',
            'kèm theo buồn nôn nôn ói vã mồ hôi và hốt hoảng do cơn đau chói dữ dội'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Chỉ định siêu âm Doppler màu mạch máu tinh hoàn cấp cứu tại giường đánh giá phổ dòng chảy động mạch '
              'tinh hoàn, thiết lập đường truyền tĩnh mạch giảm đau chống nôn, chuyển phòng mổ cấp cứu tối khẩn tháo '
              'xoắn tinh hoàn và cố định tinh hoàn hai bên trong khung giờ vàng trước 6 giờ để bảo tồn nhu mô tinh '
              'hoàn.',
  'kham': 'Bìu bên trái sưng to nề đỏ nhẹ, tinh hoàn trái co rút lên cao sát gốc dương vật và xoay nằm ngang, sờ nắn '
          'cực kỳ đau chói khiến bệnh nhân gạt tay bác sĩ, thừng tinh dày và ngắn lại, mất hoàn toàn phản xạ cơ bìu '
          'trái, dấu hiệu Prehn âm tính, sinh hiệu mạch nhanh 105 ck/p do đau.',
  'nhom': 'người lớn',
  'phu': ['cơn đau thường khởi phát đột ngột lúc nửa đêm gần sáng hoặc sau vận động mạnh',
          'nâng bìu lên cao không làm giảm đau thậm chí làm đau tăng lên rõ rệt (dấu Prehn âm tính)',
          'mất hoàn toàn phản xạ da cơ bìu ở bên tinh hoàn bị tổn thương khi kích thích đùi'],
  'ten': 'xoắn tinh hoàn dọa nghẹt'},
 {'bien_the_chan_doan': ['Tràn dịch màng tinh hoàn người lớn bên phải vô căn thể nguyên phát.',
                         'Theo dõi tràn dịch màng tinh hoàn người lớn bên trái lượng nhiều gây tức nặng.',
                         'Tràn dịch màng tinh hoàn người lớn thể tự do màng bao tinh hoàn căng to.',
                         'Tràn dịch màng tinh hoàn người lớn thứ phát sau viêm mào tinh hoàn cũ.',
                         'Theo dõi tràn dịch màng tinh hoàn người lớn hai bên không biến chứng.',
                         'Tràn dịch màng tinh hoàn người lớn có chỉ định can thiệp phẫu thuật lộn màng.'],
  'bien_the_ke_hoach': ['Chỉ định siêu âm Doppler bìu để xác định mức độ dịch tự do màng tinh hoàn và kiểm tra nhu mô '
                        'tinh hoàn mào tinh hoàn toàn bình thường loại trừ u tinh hoàn tiềm ẩn, tư vấn hẹn lịch phẫu '
                        'thuật lộn màng tinh hoàn (phẫu thuật theo phương pháp Winkelmann hoặc Jaboulay) điều trị '
                        'triệt để tránh tái phát.',
                        'Giải thích cho người bệnh về phẫu thuật mổ mở lộn hoặc cắt bỏ bao màng tinh hoàn, khuyên '
                        'không nên chọc hút dịch đơn thuần bằng kim vì dịch sẽ nhanh chóng tái lập và tăng nguy cơ '
                        'nhiễm trùng.',
                        'Làm các xét nghiệm tiền phẫu thường quy đông máu công thức máu chức năng gan thận X-quang tim '
                        'phổi, hướng dẫn mặc quần lót nâng đỡ bìu giảm cảm giác trì nặng trong thời gian chờ mổ.',
                        'Siêu âm khảo sát kỹ cấu trúc bên trong dịch màng tinh hoàn tìm vách ngăn xơ hóa, tư vấn phẫu '
                        'thuật bảo tồn tinh hoàn gây tê tủy sống xuất viện sau 24 giờ.',
                        'Hướng dẫn theo dõi sau phẫu thuật chườm lạnh tại chỗ và băng nâng bìu, hạn chế hoạt động thể '
                        'lực gắng sức hoặc quan hệ tình dục trong 4 tuần đầu.',
                        'Khám loại trừ các nguyên nhân thứ phát như nhiễm giun chỉ Wuchereria bancrofti ở vùng dịch '
                        'tễ, hẹn lịch mổ phiên tại khoa Ngoại Tiết niệu.'],
  'bien_the_kham': ['Khám bìu phải to kích thước 8x10cm, sờ nắn khối tròn đều căng nhẵn không đau, có dấu hiệu bập '
                    'bềnh sóng dịch rõ rệt, nghiệm pháp soi đèn qua da (thấu quang) dương tính ánh sáng đỏ rực đồng '
                    'nhất, sờ phía trên thừng tinh bình thường tách biệt rõ ràng với khối ở bìu, không có khối thoát '
                    'vị bẹn kèm theo.',
                    'Bìu trái to bằng quả bưởi nhỏ, da bìu căng bóng mỏng, sờ nắn không đau không thấy tinh hoàn do '
                    'dịch bao quanh quá nhiều, nghiệm pháp thấu quang ánh sáng truyền qua hoàn toàn.',
                    'Khám lâm sàng thấy khối căng mọng nước ở bìu bên phải ranh giới trên rõ không đi vào ống bẹn, dấu '
                    'hiệu kẹp thừng tinh dương tính sờ thấy cuống thừng tinh thanh mảnh, không đau khi đè nắn.',
                    'Khối phồng vùng bìu dạng dịch thuần nhất, kích thước ổn định cả ngày lẫn đêm, sờ bập bềnh dịch rõ '
                    'rệt, tinh hoàn đối bên kích thước vị trí bình thường.',
                    'Bìu to không đối xứng bên trái phì đại do tích tụ dịch màng bao, sờ không thấy điểm đau khu trú, '
                    'soi đèn pin trong phòng tối ánh sáng xuyên thấu màu hồng đồng nhất, lỗ bẹn nông không rộng.',
                    'Bệnh nhân có khối to vùng bìu di chuyển vướng víu, sờ căng đàn hồi không co nhỏ lại khi nằm ngửa, '
                    'siêu âm ghi nhận lớp dịch màng tinh hoàn dày 45mm dịch trong thuần nhất.'],
  'chan_doan': 'Tràn dịch màng tinh hoàn người lớn bên phải vô căn thể nguyên phát.',
  'chinh': ['bìu một bên to dần đều đặn không đau hoặc chỉ có cảm giác tức nặng nhẹ',
            'khối ở bìu căng nhẵn hình quả lê ranh giới rõ ràng có thể tích tăng dần',
            'kích thước khối bìu to không thay đổi theo tư thế nằm hay tư thế đứng'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Chỉ định siêu âm Doppler bìu để xác định mức độ dịch tự do màng tinh hoàn và kiểm tra nhu mô tinh hoàn '
              'mào tinh hoàn toàn bình thường loại trừ u tinh hoàn tiềm ẩn, tư vấn hẹn lịch phẫu thuật lộn màng tinh '
              'hoàn (phẫu thuật theo phương pháp Winkelmann hoặc Jaboulay) điều trị triệt để tránh tái phát.',
  'kham': 'Khám bìu phải to kích thước 8x10cm, sờ nắn khối tròn đều căng nhẵn không đau, có dấu hiệu bập bềnh sóng '
          'dịch rõ rệt, nghiệm pháp soi đèn qua da (thấu quang) dương tính ánh sáng đỏ rực đồng nhất, sờ phía trên '
          'thừng tinh bình thường tách biệt rõ ràng với khối ở bìu, không có khối thoát vị bẹn kèm theo.',
  'nhom': 'người lớn',
  'phu': ['cảm giác vướng víu khó chịu khi mặc quần chật hoặc khi đi lại vận động thể lực',
          'không có tiền sử chấn thương va đập hay sốt sưng đau cấp tính vùng bìu',
          'da bìu căng bóng các nếp nhăn da bìu bình thường bị kéo giãn mờ đi'],
  'ten': 'tràn dịch màng tinh hoàn người lớn'},
 {'bien_the_chan_doan': ['Nang mào tinh hoàn bên trái kích thước trung bình lành tính.',
                         'Theo dõi nang mào tinh hoàn bên phải thể nang tinh trùng spermatocele.',
                         'Nang mào tinh hoàn kích thước nhỏ không triệu chứng cần theo dõi.',
                         'Nang mào tinh hoàn hai bên đơn thuần lành tính.',
                         'Theo dõi nang mào tinh hoàn có cảm giác căng tức nhẹ khi vận động.',
                         'Nang mào tinh hoàn bên trái ổn định không có chỉ định phẫu thuật.'],
  'bien_the_ke_hoach': ['Chỉ định siêu âm Doppler bìu để khẳng định hình ảnh nang dịch mỏng thuần nhất ở vùng đầu mào '
                        'tinh hoàn không có chồi sùi hay vôi hóa bên trong, tư vấn bệnh nhân theo dõi định kỳ hàng năm '
                        'nếu nang nhỏ không đau không phát triển nhanh, chỉ định phẫu thuật bóc tách nang khi nang to '
                        'gây tức khó chịu hoặc ảnh hưởng sinh hoạt.',
                        'Tư vấn giải thích bản chất tổn thương là u nang lành tính chứa dịch trong hoặc dịch tinh '
                        'trùng, hướng dẫn bệnh nhân tự kiểm tra bìu tại nhà và tái khám nếu thấy nang lớn nhanh.',
                        'Siêu âm kiểm tra loại trừ các tổn thương dạng đặc hoặc u mào tinh hoàn hiếm gặp, trấn an tinh '
                        'thần bệnh nhân không cần lo lắng về ung thư.',
                        'Chỉ định phẫu thuật bóc nang mào tinh hoàn qua đường rạch da bìu nhỏ dưới gây tê tại chỗ hoặc '
                        'tiền mê nếu nang gây đau tức thường xuyên làm ảnh hưởng chất lượng sống.',
                        'Tư vấn nguy cơ tiềm ẩn tổn thương ống mào tinh hoàn ảnh hưởng đến đường dẫn tinh trùng nếu '
                        'phẫu thuật bóc nang ở nam giới độ tuổi mong muốn sinh con.',
                        'Hẹn siêu âm định kỳ sau 6-12 tháng đánh giá kích thước nang, dặn dò mặc quần lót nâng đỡ '
                        'thoáng khí tránh cọ xát mạnh vào vùng bìu.'],
  'bien_the_kham': ['Khám bìu thấy một khối tròn kích thước khoảng 2x2.5cm nằm tách biệt ở cực trên mào tinh hoàn bên '
                    'trái, mật độ căng đàn hồi, ranh giới rõ ràng có thể tách biệt khỏi nhu mô tinh hoàn, ấn không '
                    'đau, soi đèn qua da thấu quang dương tính ánh sáng truyền qua khối nang, tinh hoàn hai bên bình '
                    'thường.',
                    'Sờ nắn vùng bìu phát hiện khối nhỏ trơn nhẵn như hòn bi ve ở đỉnh mào tinh hoàn phải, di động độc '
                    'lập với tinh hoàn, mật độ căng như bóng nước nhỏ, không đau khi bóp nhẹ.',
                    'Khám lâm sàng tinh hoàn hai bên đối xứng mềm mại, cực trên mào tinh trái có khối nang đường kính '
                    '20mm ranh giới cực kỳ rõ rệt, thừng tinh bình thường, không giãn tĩnh mạch thừng tinh.',
                    'Khối dạng nang ở đầu mào tinh hoàn sờ trơn láng, không dính vào da bìu, ấn vào không đổi kích '
                    'thước, soi đèn pin qua khối nang cho ánh sáng truyền qua màu hồng trong.',
                    'Bệnh nhân tình cờ phát hiện nốt cục nhỏ ở bìu khi tắm, khám thấy khối tròn mềm đàn hồi ở mào tinh '
                    'hoàn bên phải, không có hạch bẹn sưng, cơ quan sinh dục ngoài hoàn toàn bình thường.',
                    'Khám hệ sinh dục nam xác định khối nang dịch vị trí đầu mào tinh hoàn, cấu trúc tinh hoàn bên '
                    'dưới mềm đều không u cục, siêu âm xác nhận nang dịch thành mỏng kích thước 22x18mm.'],
  'chan_doan': 'Nang mào tinh hoàn bên trái kích thước trung bình lành tính.',
  'chinh': ['tự sờ thấy một khối tròn nhỏ trơn láng tách rời nằm ở phía cực trên tinh hoàn',
            'khối không đau hoặc chỉ có cảm giác hơi tức nhẹ khi dùng tay ấn nắn nhiều',
            'kích thước khối tăng rất chậm qua nhiều năm không gây đau nhức'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Chỉ định siêu âm Doppler bìu để khẳng định hình ảnh nang dịch mỏng thuần nhất ở vùng đầu mào tinh hoàn '
              'không có chồi sùi hay vôi hóa bên trong, tư vấn bệnh nhân theo dõi định kỳ hàng năm nếu nang nhỏ không '
              'đau không phát triển nhanh, chỉ định phẫu thuật bóc tách nang khi nang to gây tức khó chịu hoặc ảnh '
              'hưởng sinh hoạt.',
  'kham': 'Khám bìu thấy một khối tròn kích thước khoảng 2x2.5cm nằm tách biệt ở cực trên mào tinh hoàn bên trái, mật '
          'độ căng đàn hồi, ranh giới rõ ràng có thể tách biệt khỏi nhu mô tinh hoàn, ấn không đau, soi đèn qua da '
          'thấu quang dương tính ánh sáng truyền qua khối nang, tinh hoàn hai bên bình thường.',
  'nhom': 'người lớn',
  'phu': ['hoàn toàn không gây rối loạn tiểu tiện hay ảnh hưởng khả năng sinh hoạt tình dục',
          'không có tiền sử viêm nhiễm đường tiết niệu hay chấn thương vùng bìu',
          'cảm giác hơi cấn nhẹ khi mặc trang phục bó sát hoặc khi ngồi xổm'],
  'ten': 'nang mào tinh hoàn'},
 {'bien_the_chan_doan': ['Viêm bao quy đầu bán cấp do nấm Candida ở bệnh nhân đái tháo đường.',
                         'Theo dõi viêm bao quy đầu bán cấp do nấm kèm hẹp phù nề bao quy đầu.',
                         'Viêm bao quy đầu bán cấp do nấm Candida albicans tái phát nhiều lần.',
                         'Viêm bao quy đầu bán cấp do nấm thể trợt nông rỉ dịch rãnh quy đầu.',
                         'Theo dõi viêm bao quy đầu bán cấp do nấm trên cơ địa dài bao quy đầu.',
                         'Viêm bao quy đầu bán cấp do nấm giai đoạn đáp ứng với thuốc kháng nấm tại chỗ.'],
  'bien_the_ke_hoach': ['Lấy bệnh phẩm cạo bựa trắng soi tươi tìm nấm men Candida và sợi tơ nấm giả, bôi kem chống nấm '
                        'clotrimazole 1% hoặc ketoconazole tại chỗ ngày 2 lần trong 14 ngày, uống một liều duy nhất '
                        'fluconazole 150mg nếu viêm lan rộng, kiểm soát chặt chẽ đường huyết và tư vấn vệ sinh giữ khô '
                        'ráo rãnh quy đầu sau tiểu.',
                        'Rửa sạch nhẹ nhàng vùng quy đầu bằng nước muối sinh lý ấm sau đó lau khô bằng khăn mềm sạch '
                        'trước khi bôi thuốc, kê kem miconazole bôi mỏng ngày 2 lần liên tục trong 10-14 ngày.',
                        'Kê đơn fluconazole viên nang 150mg uống liều duy nhất, phối hợp kem bôi kết hợp chống nấm và '
                        'chống viêm hydrocortisone nhẹ trong 3 ngày đầu nếu phù nề rát nhiều, kiêng quan hệ tình dục '
                        'cho đến khi lành hẳn.',
                        'Xét nghiệm định lượng HbA1c và chỉnh liều thuốc hạ đường huyết cùng bác sĩ nội tiết, tư vấn '
                        'điều trị đồng thời cho bạn tình nếu có triệu chứng ngứa ngáy phụ khoa để tránh lây nhiễm '
                        'chéo.',
                        'Hướng dẫn cách lộn rửa vệ sinh rãnh quy đầu hàng ngày sau khi tắm và sau mỗi lần đi tiểu, hẹn '
                        'tái khám sau 7 ngày để đánh giá liền sẹo biểu mô.',
                        'Hội chẩn phẫu thuật cắt bao quy đầu sau khi điều trị dứt điểm đợt viêm nấm nhằm giải quyết '
                        'triệt để yếu tố thuận lợi gây ẩm ướt ứ đọng cặn bẩn.'],
  'bien_the_kham': ['Bao quy đầu dài trùm kín quy đầu, lộn nhẹ bao quy đầu thấy niêm mạc quy đầu và rãnh vành đỏ rực '
                    'phù nề có nhiều mảng bám trắng đục bở vụn dạng váng sữa, vài vết trợt nông rỉ dịch rướm máu nhẹ, '
                    'không có vết loét sâu hạ cam, hạch bẹn hai bên không sưng đau.',
                    'Quy đầu dương vật viêm đỏ lan tỏa, rãnh quy đầu đọng nhiều chất bã trắng mùi chua nhẹ, niêm mạc '
                    'mẫn cảm dễ chảy máu khi quệt gạc, bao quy đầu hẹp nhẹ do phù nề viêm.',
                    'Khám phát hiện nhiều vết trợt nông li ti hình tròn trên bề mặt niêm mạc quy đầu nền đỏ tươi phủ '
                    'lớp màng trắng mỏng, rãnh vành bao quy đầu có mảng giả mạc bở, không thấy sang chấn cơ học.',
                    'Bệnh nhân lộn bao quy đầu khó khăn do đau rát và nề mọng, niêm mạc quy đầu bóng đỏ có các chấm '
                    'mụn mủ nhỏ li ti rải rác, cạo mảng bám soi trực tiếp thấy tế bào nấm men nảy chồi.',
                    'Tổn thương viêm đỏ trợt nông bao quy đầu và quy đầu điển hình do nấm Candida, không có tổn thương '
                    'sùi mào gà hay săng giang mai, lỗ sáo không chảy mủ đục.',
                    'Khám ngoài thân dương vật bình thường, rãnh quy đầu và mặt trong bao quy đầu có mảng cặn trắng '
                    'dày dính chặt vào niêm mạc sung huyết, xét nghiệm đường huyết mao mạch tại chỗ 13.8 mmol/l.'],
  'chan_doan': 'Viêm bao quy đầu bán cấp do nấm Candida ở bệnh nhân đái tháo đường.',
  'chinh': ['ngứa rát dữ dội khó chịu vùng quy đầu và nếp gấp bao quy đầu dương vật',
            'xuất hiện các mảng bựa trắng đục vón cục bở dính như váng sữa ở rãnh quy đầu',
            'niêm mạc quy đầu trợt đỏ phù nề cương tụ và đau rát nhiều khi tuột bao quy đầu'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Lấy bệnh phẩm cạo bựa trắng soi tươi tìm nấm men Candida và sợi tơ nấm giả, bôi kem chống nấm '
              'clotrimazole 1% hoặc ketoconazole tại chỗ ngày 2 lần trong 14 ngày, uống một liều duy nhất fluconazole '
              '150mg nếu viêm lan rộng, kiểm soát chặt chẽ đường huyết và tư vấn vệ sinh giữ khô ráo rãnh quy đầu sau '
              'tiểu.',
  'kham': 'Bao quy đầu dài trùm kín quy đầu, lộn nhẹ bao quy đầu thấy niêm mạc quy đầu và rãnh vành đỏ rực phù nề có '
          'nhiều mảng bám trắng đục bở vụn dạng váng sữa, vài vết trợt nông rỉ dịch rướm máu nhẹ, không có vết loét '
          'sâu hạ cam, hạch bẹn hai bên không sưng đau.',
  'nhom': 'người lớn',
  'phu': ['thường xảy ra ở người có tiền sử đái tháo đường kiểm soát đường huyết chưa tốt',
          'đau rát châm chích tăng lên rõ rệt khi đi tiểu có nước tiểu dính vào vùng trợt da',
          'chưa cắt bao quy đầu hoặc có tình trạng dài bao quy đầu gây ẩm ướt rãnh vành'],
  'ten': 'viêm bao quy đầu bán cấp do nấm'},
 {'bien_the_chan_doan': ['Xuất tinh sớm tiên phát mức độ nặng thời gian xuất tinh dưới 1 phút.',
                         'Theo dõi xuất tinh sớm tiên phát thể suốt đời liên quan quá nhạy cảm quy đầu.',
                         'Xuất tinh sớm tiên phát có kèm theo lo âu thực hiện lo âu tình dục.',
                         'Xuất tinh sớm tiên phát đáp ứng với thuốc ức chế tái hấp thu serotonin.',
                         'Theo dõi xuất tinh sớm tiên phát chưa từng đạt kiểm soát xuất tinh.',
                         'Xuất tinh sớm tiên phát mức độ vừa thời gian xuất tinh 1-2 phút.'],
  'bien_the_ke_hoach': ['Tư vấn liệu pháp tâm lý hành vi tình dục kỹ thuật bóp quy đầu (squeeze technique) hoặc kỹ '
                        'thuật dừng - bắt đầu (stop-start) cùng với bạn tình, chỉ định dùng thuốc ức chế tái hấp thu '
                        'chọn lọc serotonin tác dụng ngắn dapoxetine 30mg uống trước khi quan hệ tình dục 1-2 giờ, có '
                        'thể phối hợp xịt gây tê lidocaine/prilocaine tại chỗ quy đầu trước quan hệ 15 phút rồi rửa '
                        'sạch.',
                        'Kê đơn dapoxetine 30mg uống theo nhu cầu trước quan hệ, hướng dẫn uống với một cốc nước đầy '
                        'tránh uống rượu bia cùng lúc, dặn dò tác dụng phụ buồn nôn đau đầu thoáng qua.',
                        'Tư vấn giải tỏa áp lực tâm lý vợ chồng, hướng dẫn màn dạo đầu thoải mái không đặt nặng thời '
                        'gian giao hợp, phối hợp sử dụng bao cao su kéo dài thời gian có chứa chất gây tê nhẹ ở đầu.',
                        'Nếu dapoxetine 30mg chưa đạt hiệu quả tối ưu sau 4 tuần có thể nâng liều lên 60mg theo chỉ '
                        'định, kết hợp bài tập cơ sàn chậu Kegel giúp kiểm soát tốt hơn phản xạ xuất tinh.',
                        'Kê đơn thuốc bôi gây tê tại chỗ lidocaine gel 2% bôi quy đầu trước quan hệ 20 phút rồi lau '
                        'sạch hoặc dùng bao cao su tránh làm tê rát bạn tình, theo dõi dung nạp.',
                        'Hẹn tái khám sau 4-6 tuần đánh giá sự cải thiện của thời gian IELT và mức độ hài lòng của cặp '
                        'đôi, tư vấn duy trì lối sống lành mạnh tập thể thao giảm căng thẳng.'],
  'bien_the_kham': ['Khám lâm sàng bộ phận sinh dục ngoài hoàn toàn bình thường, tinh hoàn hai bên kích thước đều mật '
                    'độ bình thường, dương vật không cong vẹo không viêm bao quy đầu, phản xạ hành hang bình thường, '
                    'xét nghiệm nồng độ testosterone toàn phần trong giới hạn bình thường 18.5 nmol/l.',
                    'Thể trạng nam tính khỏe mạnh, cơ quan sinh dục ngoài phát triển bình thường, quy đầu nhạy cảm cao '
                    'với kích thích xúc giác, đo thời gian tiềm tàng xuất tinh khi giao hợp IELT ghi nhận trung bình '
                    '35 giây.',
                    'Khám không có tổn thương thực thể đường tiết niệu sinh dục, tuyến tiền liệt mềm không đau qua '
                    'thăm trực tràng, bảng câu hỏi đánh giá xuất tinh sớm PEDT đạt 17 điểm (có xuất tinh sớm rõ).',
                    'Bệnh nhân có vẻ lo âu căng thẳng khi chia sẻ vấn đề tế nhị, khám bìu tinh hoàn thừng tinh hai bên '
                    'không sưng không giãn tĩnh mạch, phản xạ thần kinh vùng đáy chậu nguyên vẹn.',
                    'Khám bộ phận sinh dục bình thường không hẹp bao quy đầu, nhịp tim đều 72 ck/p huyết áp 120/75 '
                    'mmHg, xét nghiệm TSH bình thường loại trừ cường giáp gây xuất tinh sớm.',
                    'Khám lâm sàng nam khoa trong giới hạn sinh lý bình thường, độ nhạy cảm đầu dương vật tăng khi làm '
                    'test cảm giác nhẹ, tâm lý ức chế tự ti rõ rệt khi đối thoại.'],
  'chan_doan': 'Xuất tinh sớm tiên phát mức độ nặng thời gian xuất tinh dưới 1 phút.',
  'chinh': ['thời gian xuất tinh khi giao hợp luôn dưới 1 phút kể từ khi bắt đầu đưa vào',
            'mất hoàn toàn khả năng kiểm soát hoặc trì hoãn việc xuất tinh theo ý muốn',
            'tình trạng xuất tinh quá nhanh xảy ra ở hầu hết các lần giao hợp từ lần đầu tiên trong đời'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Tư vấn liệu pháp tâm lý hành vi tình dục kỹ thuật bóp quy đầu (squeeze technique) hoặc kỹ thuật dừng - '
              'bắt đầu (stop-start) cùng với bạn tình, chỉ định dùng thuốc ức chế tái hấp thu chọn lọc serotonin tác '
              'dụng ngắn dapoxetine 30mg uống trước khi quan hệ tình dục 1-2 giờ, có thể phối hợp xịt gây tê '
              'lidocaine/prilocaine tại chỗ quy đầu trước quan hệ 15 phút rồi rửa sạch.',
  'kham': 'Khám lâm sàng bộ phận sinh dục ngoài hoàn toàn bình thường, tinh hoàn hai bên kích thước đều mật độ bình '
          'thường, dương vật không cong vẹo không viêm bao quy đầu, phản xạ hành hang bình thường, xét nghiệm nồng độ '
          'testosterone toàn phần trong giới hạn bình thường 18.5 nmol/l.',
  'nhom': 'người lớn',
  'phu': ['gây tâm lý tự ti lo lắng căng thẳng và thất vọng cho bản thân và bạn đời',
          'xu hướng né tránh việc quan hệ tình dục do áp lực tâm lý thất bại',
          'không kèm theo rối loạn cương dương hay dị tật giải phẫu cơ quan sinh dục'],
  'ten': 'xuất tinh sớm tiên phát'},
 {'bien_the_chan_doan': ['Vô sinh nam do suy giảm số lượng tinh trùng thiểu tinh trùng mức độ trung bình.',
                         'Theo dõi vô sinh nam do suy giảm số lượng tinh trùng kết hợp giảm độ di động OAT.',
                         'Vô sinh nam do suy giảm số lượng tinh trùng mức độ nặng nồng độ dưới 5 triệu/ml.',
                         'Vô sinh nam do suy giảm số lượng tinh trùng vô căn nguyên phát.',
                         'Theo dõi vô sinh nam do suy giảm số lượng tinh trùng có tăng nhẹ nồng độ FSH.',
                         'Vô sinh nam do suy giảm số lượng tinh trùng giai đoạn chuẩn bị hỗ trợ sinh sản.'],
  'bien_the_ke_hoach': ['Chỉ định làm lại xét nghiệm tinh dịch đồ lần 2 sau khi kiêng xuất tinh 3-5 ngày để đối chiếu '
                        'kết quả, làm xét nghiệm nội tiết sinh dục nam FSH LH testosterone toàn phần và prolactin máu, '
                        'siêu âm Doppler mạch máu bìu đánh giá kích thước tinh hoàn và dòng trào ngược tĩnh mạch thừng '
                        'tinh vi thể, tư vấn lối sống tránh tắm nước nóng mặc đồ lót rộng rãi và bổ sung các chất '
                        'chống oxy hóa kẽm selen coenzyme Q10.',
                        'Xét nghiệm phân tích di truyền nhiễm sắc thể đồ Karyotype và xét nghiệm đột biến vi mất đoạn '
                        'nhiễm sắc thể Y (vùng AZF) nếu mật độ tinh trùng dưới 5 triệu/ml, đánh giá chỉ số đứt gãy DNA '
                        'tinh trùng DFI.',
                        'Kê đơn bổ sung các chất chống oxy hóa chuyên biệt cho nam giới gồm L-carnitine kẽm sulfate '
                        'selen vitamin E và acid folic trong 3-6 tháng chu kỳ sinh tinh mới.',
                        'Tư vấn kiêng hẳn thuốc lá rượu bia, tránh để máy tính xách tay lên đùi hoặc ngồi lái xe liên '
                        'tục nhiều giờ làm tăng nhiệt độ vùng bìu ảnh hưởng quá trình sinh tinh.',
                        'Hướng dẫn cả hai vợ chồng cùng khám chuyên khoa hiếm muộn, đánh giá song song sức khỏe sinh '
                        'sản của người vợ, tư vấn phương án thụ tinh nhân tạo IUI hoặc thụ tinh trong ống nghiệm ICSI.',
                        'Hẹn làm lại tinh dịch đồ kiểm tra sau 3 tháng dùng thuốc chống oxy hóa cải thiện chất lượng '
                        'tế bào sinh dục, kiểm tra hormone tuyến giáp TSH.'],
  'bien_the_kham': ['Thể trạng nam tính bình thường, giọng nói trầm, lông mu phân bố bình thường theo kiểu nam, đo thể '
                    'tích tinh hoàn hai bên bằng thước đo Prader đạt khoảng 13-14ml mật độ hơi mềm nhẹ, khám bìu ở tư '
                    'thế đứng làm nghiệm pháp Valsalva không sờ thấy búi giãn tĩnh mạch thừng tinh rõ rệt, hai ống dẫn '
                    'tinh sờ thấy rõ.',
                    'Khám lâm sàng nam khoa ghi nhận thể tích tinh hoàn hai bên hơi nhỏ khoảng 12ml, mật độ mềm đều, '
                    'mào tinh hoàn mềm mại, không có khối u bìu, cơ quan sinh dục ngoài không có dị tật bẩm sinh.',
                    'Hai ống dẫn tinh hai bên sờ chắc như sợi dây đàn nguyên vẹn, tuyến tiền liệt mềm đều qua thăm '
                    'trực tràng, không sưng đau tinh hoàn, lông râu cơ thể phát triển đầy đủ.',
                    'Bệnh nhân có thể trạng tốt không béo phì, huyết áp 120/80 mmHg, siêu âm đo kích thước tinh hoàn '
                    'phải 3.8x2.2cm tinh hoàn trái 3.6x2.1cm nhu mô đều không có nốt giảm âm khu trú.',
                    'Khám bộ phận sinh dục không có dấu hiệu viêm nhiễm, kết quả tinh dịch đồ mang theo có mật độ tinh '
                    'trùng 8 triệu/ml với độ di động tiến tới 22%, hình thái bình thường 3%.',
                    'Đo thước Prader thể tích tinh hoàn đạt 14ml mỗi bên, không có giãn tĩnh mạch thừng tinh độ lâm '
                    'sàng, phản xạ bìu tốt, các đặc tính sinh dục thứ phát nam tính hoàn toàn bình thường.'],
  'chan_doan': 'Vô sinh nam do suy giảm số lượng tinh trùng thiểu tinh trùng mức độ trung bình.',
  'chinh': ['hai vợ chồng chung sống sinh hoạt tình dục đều đặn trên 1 năm không dùng biện pháp mà chưa có thai',
            'kết quả tinh dịch đồ nồng độ tinh trùng dưới 15 triệu/ml (thiểu tinh trùng rõ)',
            'tổng số lượng tinh trùng trong một lần xuất tinh dưới 39 triệu tinh trùng'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Chỉ định làm lại xét nghiệm tinh dịch đồ lần 2 sau khi kiêng xuất tinh 3-5 ngày để đối chiếu kết quả, '
              'làm xét nghiệm nội tiết sinh dục nam FSH LH testosterone toàn phần và prolactin máu, siêu âm Doppler '
              'mạch máu bìu đánh giá kích thước tinh hoàn và dòng trào ngược tĩnh mạch thừng tinh vi thể, tư vấn lối '
              'sống tránh tắm nước nóng mặc đồ lót rộng rãi và bổ sung các chất chống oxy hóa kẽm selen coenzyme Q10.',
  'kham': 'Thể trạng nam tính bình thường, giọng nói trầm, lông mu phân bố bình thường theo kiểu nam, đo thể tích tinh '
          'hoàn hai bên bằng thước đo Prader đạt khoảng 13-14ml mật độ hơi mềm nhẹ, khám bìu ở tư thế đứng làm nghiệm '
          'pháp Valsalva không sờ thấy búi giãn tĩnh mạch thừng tinh rõ rệt, hai ống dẫn tinh sờ thấy rõ.',
  'nhom': 'người lớn',
  'phu': ['tỷ lệ tinh trùng di động tiến tới PR giảm dưới 32% hoặc di động chung giảm',
          'hoàn toàn không có triệu chứng đau tức hay bất thường chức năng sinh lý khi giao hợp',
          'tiền sử có thể từng mắc bệnh quai bị hoặc làm việc trong môi trường nhiệt độ cao tiếp xúc hóa chất'],
  'ten': 'vô sinh nam do suy giảm số lượng tinh trùng'},
 {'bien_the_chan_doan': ['Bệnh cong dương vật Peyronie giai đoạn viêm tiến triển góc cong 40 độ.',
                         'Theo dõi bệnh cong dương vật Peyronie giai đoạn ổn định mảng xơ vôi hóa.',
                         'Bệnh cong dương vật Peyronie biến dạng dạng thắt eo đồng hồ cát.',
                         'Bệnh cong dương vật Peyronie kèm rối loạn cương dương thứ phát.',
                         'Theo dõi bệnh cong dương vật Peyronie góc cong lớn trên 60 độ cản trở giao hợp.',
                         'Bệnh cong dương vật Peyronie giai đoạn mạn tính có chỉ định phẫu thuật chỉnh hình.'],
  'bien_the_ke_hoach': ['Hướng dẫn người bệnh tự chụp ảnh dương vật ở trạng thái cương cứng tối đa từ các góc độ nhìn '
                        'thẳng và nhìn nghiêng để đo góc cong biến dạng, chỉ định siêu âm Doppler mạch máu dương vật '
                        'đánh giá kích thước độ dày và mức độ vôi hóa của mảng xơ bao trắng, điều trị nội khoa giai '
                        'đoạn cấp bằng vitamin E liều cao 400 IU ngày 2 lần phối hợp thuốc kháng viêm NSAID và cân '
                        'nhắc tiêm collagenase Clostridium histolyticum vào mảng xơ.',
                        'Kê đơn pentoxifylline 400mg ngày 3 lần giúp giảm xơ hóa và ức chế lắng đọng collagen, kết hợp '
                        'thuốc ức chế men phosphodiesterase-5 tadalafil 5mg hàng ngày hỗ trợ tưới máu thể hang.',
                        'Tư vấn sử dụng thiết bị kéo giãn dương vật cơ học (penile traction therapy) hàng ngày 2-4 giờ '
                        'giúp nắn chỉnh góc cong và ngăn ngừa co rút chiều dài dương vật.',
                        'Giải thích diễn tiến tự nhiên của bệnh gồm 2 giai đoạn: giai đoạn viêm đau kéo dài 6-12 tháng '
                        'sau đó đến giai đoạn xơ hóa ổn định hết đau nhưng góc cong cố định.',
                        'Chỉ định phẫu thuật chỉnh thẳng dương vật bằng kỹ thuật khâu gấp nếp bao trắng (phương pháp '
                        'Nesbit hoặc 16-dot) chỉ khi bệnh đã bước vào giai đoạn ổn định trên 6 tháng và góc cong cản '
                        'trở quan hệ.',
                        'Siêu âm Doppler màu thể hang đánh giá lưu lượng mạch máu và mức độ rối loạn cương phối hợp, '
                        'động viên tâm lý tránh lo âu mặc cảm trong sinh hoạt lứa đôi.'],
  'bien_the_kham': ['Khám dương vật ở trạng thái mềm sờ thấy một mảng xơ cứng chắc kích thước khoảng 1.2x2.0cm ở mặt '
                    'lưng thân dương vật gần gốc, ranh giới rõ ràng, không di động dính sát vào bao trắng thể hang, ấn '
                    'tức nhẹ tại mảng xơ, không có vết loét da dương vật.',
                    'Sờ dọc mặt lưng thể hang dương vật phát hiện mảng xơ hóa cứng như sụn dài 2cm làm thân dương vật '
                    'hơi co rút về phía lưng, khi cương bệnh nhân mô tả dương vật cong gập lên trên khoảng 45 độ gây '
                    'đau thốn.',
                    'Khám thực thể phát hiện mảng xơ đơn độc ở mặt bên trái bao trắng thể hang, ấn chắc không đau '
                    'nhiều, quy đầu hồng mềm, tinh hoàn hai bên bình thường không có tổn thương phối hợp.',
                    'Dương vật khi mềm sờ thấy mảng xơ cứng dẹt gồ dưới da mặt lưng dương vật, da phủ ngoài di động '
                    'tốt trên mảng xơ, bệnh nhân than phiền dương vật ngắn lại và biến dạng dạng thắt eo đồng hồ cát '
                    'khi cương.',
                    'Khám lâm sàng nam khoa thấy mảng xơ hóa thể hang kích thước 1x1.5cm không đau chói, kiểm tra hai '
                    'bàn tay không thấy co thắt cân gan tay Dupuytren phối hợp.',
                    'Sờ nắn thân dương vật phát hiện dải xơ dài dọc theo vách giữa thể hang, bệnh nhân cung cấp hình '
                    'ảnh dương vật cương cong lệch sang phải 50 độ gây cản trở giao hợp hoàn toàn.'],
  'chan_doan': 'Bệnh cong dương vật Peyronie giai đoạn viêm tiến triển góc cong 40 độ.',
  'chinh': ['sờ thấy một mảng xơ cứng chắc gồ lên dọc theo thân dương vật',
            'dương vật bị cong vẹo biến dạng gập góc rõ rệt khi ở trạng thái cương cứng',
            'đau nhức tại vị trí mảng xơ trong lúc cương cứng hoặc khi quan hệ tình dục'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Hướng dẫn người bệnh tự chụp ảnh dương vật ở trạng thái cương cứng tối đa từ các góc độ nhìn thẳng và '
              'nhìn nghiêng để đo góc cong biến dạng, chỉ định siêu âm Doppler mạch máu dương vật đánh giá kích thước '
              'độ dày và mức độ vôi hóa của mảng xơ bao trắng, điều trị nội khoa giai đoạn cấp bằng vitamin E liều cao '
              '400 IU ngày 2 lần phối hợp thuốc kháng viêm NSAID và cân nhắc tiêm collagenase Clostridium histolyticum '
              'vào mảng xơ.',
  'kham': 'Khám dương vật ở trạng thái mềm sờ thấy một mảng xơ cứng chắc kích thước khoảng 1.2x2.0cm ở mặt lưng thân '
          'dương vật gần gốc, ranh giới rõ ràng, không di động dính sát vào bao trắng thể hang, ấn tức nhẹ tại mảng '
          'xơ, không có vết loét da dương vật.',
  'nhom': 'người lớn',
  'phu': ['khó khăn hoặc hoàn toàn không thể thực hiện giao hợp do góc cong dương vật quá lớn',
          'rút ngắn chiều dài dương vật rõ rệt khi cương cứng so với trước đây',
          'tiền sử có các vi chấn thương lặp lại nhiều lần trong sinh hoạt tình dục trước đó'],
  'ten': 'bệnh cong dương vật Peyronie'},
 {'bien_the_chan_doan': ['Suy tuyến sinh dục nam muộn mãn dục nam có hội chứng suy giảm testosterone.',
                         'Theo dõi suy tuyến sinh dục nam muộn mãn dục nam kết hợp rối loạn cương dương.',
                         'Suy tuyến sinh dục nam muộn mãn dục nam trên bệnh nhân hội chứng chuyển hóa.',
                         'Suy tuyến sinh dục nam muộn mãn dục nam mức độ trung bình có giảm mật độ xương.',
                         'Theo dõi suy tuyến sinh dục nam muộn mãn dục nam thể thiếu hụt testosterone sinh học.',
                         'Suy tuyến sinh dục nam muộn mãn dục nam giai đoạn điều chỉnh liệu pháp nội tiết.'],
  'bien_the_ke_hoach': ['Định lượng lại nồng độ testosterone toàn phần và testosterone tự do trong huyết thanh vào '
                        'buổi sáng sớm (từ 7-10 giờ sáng), làm xét nghiệm tầm soát an toàn trước điều trị gồm PSA máu '
                        'và hematocrit Hct, nếu không có chống chỉ định bắt đầu liệu pháp bổ sung hormone testosterone '
                        'thay thế bằng gel bôi ngoài da 1% hoặc tiêm bắp testosterone undecanoate tác dụng kéo dài kết '
                        'hợp tập thể dục thể thao tăng cường cơ bắp.',
                        'Kê đơn gel bôi testosterone 1% bôi vai hoặc bụng mỗi sáng 50mg, dặn dò rửa tay sạch sau bôi '
                        'tránh tiếp xúc trực tiếp da với người thân, theo dõi định kỳ PSA và công thức máu.',
                        'Chỉ định tiêm bắp sâu testosterone undecanoate 1000mg/4ml mũi thứ hai sau 6 tuần sau đó duy '
                        'trì mỗi 10-12 tuần một mũi, kiểm tra nồng độ hematocrit nếu vượt quá 54% phải tạm ngừng '
                        'thuốc.',
                        'Tư vấn giảm cân điều chỉnh chế độ ăn giảm đường bột chất béo, tập thể dục kháng lực cử tạ nhẹ '
                        'nhàng ít nhất 30 phút mỗi ngày giúp kích thích sản sinh testosterone tự nhiên.',
                        'Đo mật độ khoáng chất xương DEXA cột sống và cổ xương đùi, bổ sung canxi và vitamin D đường '
                        'uống phòng ngừa gãy xương do thiếu hụt androgen.',
                        'Tầm soát bệnh lý tim mạch và ngưng thở khi ngủ trước khi dùng liệu pháp testosterone, hẹn tái '
                        'khám sau 3 tháng để đánh giá lại triệu chứng tình dục và sức sống thể lực.'],
  'bien_the_kham': ['Thể trạng thừa cân béo bụng, vòng thắt lưng đo được 97cm, khối cơ bắp tay chân giảm nhẽo, râu và '
                    'lông trên cơ thể mọc thưa thớt hơn trước, thể tích tinh hoàn hai bên khoảng 12-13ml mật độ mềm, '
                    'huyết áp 138/86 mmHg, nhịp tim đều 70 ck/p.',
                    'Bệnh nhân nam giới 58 tuổi thể trạng mệt mỏi, tích mỡ nhiều vùng ngực và hông bụng, cơ lực tay '
                    'chân giảm nhẹ, thăm trực tràng tuyến tiền liệt trơn láng mềm mại kích thước bình thường, tinh '
                    'hoàn hai bên đối xứng không teo nhỏ nặng.',
                    'Khám lâm sàng ghi nhận các biểu hiện của hội chứng thiếu hụt androgen ở nam giới lớn tuổi ADAM, '
                    'bảng câu hỏi ADAM dương tính, râu cằm mọc chậm lâu cạo, huyết áp 140/90 mmHg, chỉ số BMI 27.5 '
                    'kg/m2.',
                    'Bệnh nhân than phiền suy nhược giảm sức sống uể oải cả ngày, khám phản xạ gân xương bình thường, '
                    'tinh hoàn thể tích 13ml mỗi bên hơi nhão, không có phì đại tuyến ngực nam giới rõ rệt.',
                    'Thể trạng béo trung tâm, khám bộ phận sinh dục ngoài bình thường, nồng độ testosterone toàn phần '
                    'lấy máu lúc 8 giờ sáng là 8.2 nmol/l (dưới ngưỡng tham chiếu chuẩn 12 nmol/l).',
                    'Khám tổng quát không thấy dấu hiệu suy tim suy giáp, cơ bắp teo nhão nhẹ, đo mật độ xương DEXA có '
                    'loãng xương nhẹ tại cột sống thắt lưng, tâm trạng âu sầu thiếu tự tin.'],
  'chan_doan': 'Suy tuyến sinh dục nam muộn mãn dục nam có hội chứng suy giảm testosterone.',
  'chinh': ['giảm ham muốn tình dục rõ rệt và giảm đáng kể tần suất cương cứng buổi sáng',
            'rối loạn cương dương không duy trì được độ cứng cần thiết trong quan hệ tình dục',
            'mệt mỏi suy giảm sức bền thể lực cơ bắp teo nhẽo và giảm khối lượng cơ xương'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Định lượng lại nồng độ testosterone toàn phần và testosterone tự do trong huyết thanh vào buổi sáng sớm '
              '(từ 7-10 giờ sáng), làm xét nghiệm tầm soát an toàn trước điều trị gồm PSA máu và hematocrit Hct, nếu '
              'không có chống chỉ định bắt đầu liệu pháp bổ sung hormone testosterone thay thế bằng gel bôi ngoài da '
              '1% hoặc tiêm bắp testosterone undecanoate tác dụng kéo dài kết hợp tập thể dục thể thao tăng cường cơ '
              'bắp.',
  'kham': 'Thể trạng thừa cân béo bụng, vòng thắt lưng đo được 97cm, khối cơ bắp tay chân giảm nhẽo, râu và lông trên '
          'cơ thể mọc thưa thớt hơn trước, thể tích tinh hoàn hai bên khoảng 12-13ml mật độ mềm, huyết áp 138/86 mmHg, '
          'nhịp tim đều 70 ck/p.',
  'nhom': 'người lớn',
  'phu': ['thay đổi khí sắc dễ cáu gắt trầm uất suy giảm trí nhớ và độ tập trung',
          'tăng tích tụ mỡ nội tạng vùng bụng béo bụng vòng eo tăng nhanh',
          'nồng độ testosterone toàn phần huyết thanh buổi sáng xét nghiệm dưới 11 nmol/l'],
  'ten': 'suy tuyến sinh dục nam muộn mãn dục nam'},
 {'bien_the_chan_doan': ['Cương cứng dương vật kéo dài thể thiếu máu priapism cấp cứu giờ thứ 5.',
                         'Theo dõi cương cứng dương vật kéo dài thể thiếu máu do thuốc ức chế PDE-5.',
                         'Cương cứng dương vật kéo dài thể thiếu máu giờ thứ 8 nguy cơ xơ hóa thể hang.',
                         'Cương cứng dương vật kéo dài thể thiếu máu tái phát trên bệnh nhân huyết học.',
                         'Theo dõi cương cứng dương vật kéo dài thể thiếu máu tắc nghẽn mạch máu thể hang.',
                         'Cương cứng dương vật kéo dài thể thiếu máu đáp ứng một phần sau chọc hút giải áp.'],
  'bien_the_ke_hoach': ['Xử trí cấp cứu nam khoa khẩn cấp tại phòng thủ thuật: gây tê gốc dương vật bằng lidocaine '
                        'không adrenaline, chọc hút máu khoang thể hang bằng kim 19G hút ra máu đen sẫm thiếu oxy làm '
                        'khí máu khẳng định toan chuyển hóa thiếu máu, bơm rửa thể hang bằng dung dịch nước muối sinh '
                        'lý ấm và tiêm phenylephrine pha loãng co mạch xẹp dương vật theo dõi huyết áp liên tục.',
                        'Pha dung dịch phenylephrine nồng độ 100-500 mcg/ml trong NaCl 0.9%, tiêm vào thể hang mỗi lần '
                        '1ml cách nhau 3-5 phút tối đa trong vòng 1 giờ, theo dõi sát điện tim và huyết áp phòng biến '
                        'chứng tim mạch.',
                        'Nếu hút giải áp và tiêm thuốc vận mạch co mạch thất bại sau 1 giờ khẩn trương chuyển phòng mổ '
                        'làm phẫu thuật tạo cầu nối thông thể hang - quy đầu (phẫu thuật Winter hoặc Al-Ghorab).',
                        'Đặt ống thông tiểu mềm làm rỗng bàng quang nếu bệnh nhân bí tiểu cấp tính, truyền dịch tĩnh '
                        'mạch và cho thuốc giảm đau gây nghiện nếu đau quá mức.',
                        'Giải thích nguy cơ di chứng rối loạn cương dương vĩnh viễn hoặc xơ hóa thể hang cho bệnh nhân '
                        'và gia đình do tình trạng thiếu máu kéo dài trên 6 giờ.',
                        'Sau khi dương vật xẹp hoàn toàn theo dõi tại phòng cấp cứu ít nhất 12-24 giờ đề phòng tái '
                        'cương, xét nghiệm huyết học tìm nguyên nhân hồng cầu hình liềm hoặc bạch cầu cấp.'],
  'bien_the_kham': ['Dương vật cương cứng ngắc ở góc 90 độ, sờ hai thể hang căng cứng ngắc như gỗ chạm vào cực kỳ đau '
                    'chói, thể xốp và quy đầu mềm nhạt màu đối lập hoàn toàn với thể hang, không có vết bầm tím chấn '
                    'thương tầng sinh môn, sinh hiệu mạch nhanh 110 ck/p huyết áp 150/95 mmHg do đau đớn dữ dội.',
                    'Bệnh nhân vào cấp cứu với tình trạng dương vật cương cứng liên tục đã 6 tiếng sau uống thuốc trợ '
                    'dương, thân dương vật căng cứng đau đớn vã mồ hôi, quy đầu mềm không cương, dấu hiệu thiếu máu ứ '
                    'trệ tĩnh mạch rõ.',
                    'Khám lâm sàng thấy hai thể hang căng phồng rắn chắc sờ vào đau nhức kịch liệt, da thân dương vật '
                    'căng bóng hơi tím nhẹ do ứ máu tĩnh mạch, không có khối máu tụ vùng bìu bẹn.',
                    'Dương vật cương thẳng đứng đau dữ dội, chọc hút thể hang ra máu đen đặc quánh không đông, khí máu '
                    'thể hang đo pH 6.98 pO2 28 mmHg pCO2 75 mmHg khẳng định thể thiếu máu tắc nghẽn tĩnh mạch.',
                    'Bệnh nhân đau đớn vật vã không thể ngồi được, hai thể hang rắn đanh, quy đầu mềm, không đi tiểu '
                    'được do sưng nề chèn ép niệu đạo thể xốp, bàng quang căng nhẹ trên mu.',
                    'Khám cấp cứu ghi nhận cương đau dương vật kéo dài thể tĩnh mạch giờ thứ 7, hai thể hang căng như '
                    'thanh gỗ, ấn đau chói lan lên hạ vị, phản xạ gân xương bình thường.'],
  'chan_doan': 'Cương cứng dương vật kéo dài thể thiếu máu priapism cấp cứu giờ thứ 5.',
  'chinh': ['dương vật cương cứng ngắc liên tục không xẹp kéo dài trên 4 giờ đồng hồ',
            'đau nhức dữ dội buốt nhói trong thân dương vật tăng dần theo thời gian',
            'hai thể hang cương cứng căng chắc như gỗ nhưng quy đầu và thể xốp vẫn mềm'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'nam khoa',
  'ke_hoach': 'Xử trí cấp cứu nam khoa khẩn cấp tại phòng thủ thuật: gây tê gốc dương vật bằng lidocaine không '
              'adrenaline, chọc hút máu khoang thể hang bằng kim 19G hút ra máu đen sẫm thiếu oxy làm khí máu khẳng '
              'định toan chuyển hóa thiếu máu, bơm rửa thể hang bằng dung dịch nước muối sinh lý ấm và tiêm '
              'phenylephrine pha loãng co mạch xẹp dương vật theo dõi huyết áp liên tục.',
  'kham': 'Dương vật cương cứng ngắc ở góc 90 độ, sờ hai thể hang căng cứng ngắc như gỗ chạm vào cực kỳ đau chói, thể '
          'xốp và quy đầu mềm nhạt màu đối lập hoàn toàn với thể hang, không có vết bầm tím chấn thương tầng sinh môn, '
          'sinh hiệu mạch nhanh 110 ck/p huyết áp 150/95 mmHg do đau đớn dữ dội.',
  'nhom': 'người lớn',
  'phu': ['cương cứng xuất hiện tự phát hoặc kéo dài sau giao hợp không giảm sau khi xuất tinh',
          'tiền sử sử dụng thuốc điều trị rối loạn cương thuốc tiêm thể hang hoặc bệnh hồng cầu hình liềm',
          'cảm giác căng tức đau buốt lan tỏa khắp vùng đáy chậu và tầng sinh môn'],
  'ten': 'cương cứng dương vật kéo dài thể thiếu máu'},
 {'bien_the_chan_doan': ['Đái tháo đường típ 1 mới phát hiện chưa có biến chứng toan ceton nặng.',
                         'Theo dõi đái tháo đường típ 1 mới phát hiện có nhiễm toan ceton nhẹ dọa biến chứng.',
                         'Đái tháo đường típ 1 mới phát hiện thể tự miễn phụ thuộc insulin hoàn toàn.',
                         'Đái tháo đường típ 1 mới phát hiện có mất nước trung bình do tăng thẩm thấu.',
                         'Theo dõi đái tháo đường típ 1 mới phát hiện ở người thanh niên khởi phát cấp tính.',
                         'Đái tháo đường típ 1 mới phát hiện giai đoạn bắt đầu dò liều insulin nội trú.'],
  'bien_the_ke_hoach': ['Chỉ định xét nghiệm khẩn cấp: đường huyết tĩnh mạch, HbA1c, tổng phân tích nước tiểu tìm '
                        'ceton niệu, khí máu động mạch và điện giải đồ loại trừ nhiễm toan ceton đái tháo đường DKA, '
                        'xét nghiệm định lượng kháng thể kháng tế bào đảo tụy anti-GAD và peptide C máu, nhập viện '
                        'thiết lập ngay phác đồ điều trị bổ sung insulin nhiều mũi tiêm dưới da hàng ngày (phác đồ nền '
                        '- xung basal-bolus) kết hợp hướng dẫn đếm lượng carbohydrate trong khẩu phần ăn.',
                        'Truyền bù dịch tĩnh mạch dung dịch mặn đẳng trương NaCl 0.9% tốc độ thích hợp bù thể tích '
                        'nước mất, tiêm dưới da insulin tác dụng nhanh trước các bữa ăn chính và insulin tác dụng kéo '
                        'dài trước khi đi ngủ.',
                        'Theo dõi đường huyết mao mạch 4-6 lần/ngày (trước các bữa ăn và trước khi đi ngủ), điều chỉnh '
                        'liều insulin theo mục tiêu đường huyết đói 4.4-7.2 mmol/l và sau ăn dưới 10.0 mmol/l.',
                        'Hướng dẫn bệnh nhân và gia đình kỹ thuật tiêm insulin bằng bút tiêm, cách luân chuyển vị trí '
                        'tiêm ở bụng đùi bắp tay tránh loạn dưỡng mỡ, nhận biết và xử trí sớm hạ đường huyết với quy '
                        'tắc 15g đường.',
                        'Tư vấn chuyên gia dinh dưỡng về việc cân đối tinh bột đạm béo, tuyệt đối không tự ý ngừng '
                        'tiêm insulin vì nguy cơ bùng phát toan ceton đe dọa tính mạng.',
                        'Trang bị máy đo đường huyết cá nhân que thử ceton máu hoặc nước tiểu, lập sổ theo dõi đường '
                        'huyết ngoại trú và hẹn tái khám định kỳ sau khi xuất viện.'],
  'bien_the_kham': ['Bệnh nhân tỉnh táo tiếp xúc tốt nhưng mệt mỏi thể trạng gầy hốc hác, dấu hiệu véo da mất chậm nhẹ '
                    'do mất nước, niêm mạc môi lưỡi khô ráo, nhịp tim nhanh 105 ck/p đều, huyết áp 105/70 mmHg, đo '
                    'đường huyết mao mạch ngẫu nhiên tại phòng khám đạt 22.4 mmol/l (rất cao).',
                    'Bệnh nhân vào khám vì sụt 5kg trong 3 tuần, mắt trũng nhẹ da khô ráp, hơi thở thoang thoảng mùi '
                    'quả táo lên men, nhịp thở nhanh nông 22 ck/p, que thử nước tiểu tại chỗ thấy glucose 4+ và ceton '
                    '2+.',
                    'Khám thể trạng gầy chỉ số BMI 17.5 kg/m2, không có dấu hiệu phù, tim đập nhanh hồi hộp, bụng mềm '
                    'không đau khu trú, xét nghiệm đường huyết tĩnh mạch lúc đói 18.6 mmol/l.',
                    'Bệnh nhân khát nước liên tục phải cầm chai nước uống trong phòng khám, niêm mạc mắt nhạt nhẹ, '
                    'mạch 100 lần/phút, không có rối loạn ý thức, phản xạ bình thường.',
                    'Dấu hiệu mất nước mức độ trung bình với họng khô niêm mạc miệng kém bóng, huyết áp tư thế đứng '
                    'giảm nhẹ, đường máu mao mạch vượt ngưỡng đo của máy cá nhân (> 27.8 mmol/l).',
                    'Khám toàn diện tim phổi bình thường, không có ổ nhiễm trùng ngoài da rõ rệt, bệnh nhân than nhìn '
                    'mờ hai mắt như có màn sương do biến đổi áp lực thẩm thấu thủy dịch.'],
  'chan_doan': 'Đái tháo đường típ 1 mới phát hiện chưa có biến chứng toan ceton nặng.',
  'chinh': ['hội chứng 4 nhiều kinh điển: ăn nhiều uống nhiều tiểu nhiều gầy sút cân nhanh chóng',
            'sút từ 4 đến 6kg trong vòng vài tuần ngắn ngủi dù ăn uống rất nhiều',
            'cảm giác khát nước dữ dội liên tục uống nước nhiều lít mỗi ngày cả ban đêm'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Chỉ định xét nghiệm khẩn cấp: đường huyết tĩnh mạch, HbA1c, tổng phân tích nước tiểu tìm ceton niệu, '
              'khí máu động mạch và điện giải đồ loại trừ nhiễm toan ceton đái tháo đường DKA, xét nghiệm định lượng '
              'kháng thể kháng tế bào đảo tụy anti-GAD và peptide C máu, nhập viện thiết lập ngay phác đồ điều trị bổ '
              'sung insulin nhiều mũi tiêm dưới da hàng ngày (phác đồ nền - xung basal-bolus) kết hợp hướng dẫn đếm '
              'lượng carbohydrate trong khẩu phần ăn.',
  'kham': 'Bệnh nhân tỉnh táo tiếp xúc tốt nhưng mệt mỏi thể trạng gầy hốc hác, dấu hiệu véo da mất chậm nhẹ do mất '
          'nước, niêm mạc môi lưỡi khô ráo, nhịp tim nhanh 105 ck/p đều, huyết áp 105/70 mmHg, đo đường huyết mao mạch '
          'ngẫu nhiên tại phòng khám đạt 22.4 mmol/l (rất cao).',
  'nhom': 'cả hai',
  'phu': ['mệt mỏi rã rời bủn rủn chân tay mắt nhìn mờ dao động theo đường huyết',
          'hơi thở có thể thoang thoảng mùi táo chín hoặc mùi ceton chua nhẹ',
          'khởi phát rầm rộ ở người thanh niên hoặc thiếu niên có thể trạng gầy'],
  'ten': 'đái tháo đường típ 1 mới phát hiện'},
 {'bien_the_chan_doan': ['U tuyến yên tiết prolactin prolactinoma thể u vi thể microprolactinoma.',
                         'Theo dõi u tuyến yên tiết prolactin prolactinoma thể u lớn macroprolactinoma có chèn ép giao '
                         'thoa thị giác.',
                         'U tuyến yên tiết prolactin prolactinoma gây hội chứng tiết sữa vô kinh.',
                         'U tuyến yên tiết prolactin prolactinoma mức độ tăng prolactin máu cao.',
                         'Theo dõi u tuyến yên tiết prolactin prolactinoma đáp ứng với điều trị thuốc đồng vận '
                         'dopamine.',
                         'U tuyến yên tiết prolactin prolactinoma giai đoạn theo dõi ngoại trú ổn định.'],
  'bien_the_ke_hoach': ['Chỉ định chụp cộng hưởng từ MRI sọ não vùng tuyến yên có tiêm thuốc đối quang từ gadolinium '
                        'dựng hình lát mỏng để đo kích thước khối u, đo thị trường kế tự động bằng máy Humphrey, bắt '
                        'đầu điều trị nội khoa bằng thuốc đồng vận dopamine cabergoline liều 0.5mg/tuần chia 2 lần '
                        'hoặc bromocriptine 2.5mg/ngày, theo dõi nồng độ prolactin máu định kỳ.',
                        'Xét nghiệm định lượng lại prolactin huyết thanh buổi sáng khi nghỉ ngơi tránh căng thẳng, làm '
                        'bilan hormone tuyến yên phối hợp gồm TSH FT4 cortisol máu và IGF-1 loại trừ u hỗn hợp.',
                        'Kê đơn cabergoline 0.25mg uống 2 lần mỗi tuần sau bữa ăn tối để giảm thiểu tác dụng phụ buồn '
                        'nôn và tụt huyết áp tư thế, theo dõi siêu âm tim định kỳ kiểm tra van tim.',
                        'Chụp MRI tuyến yên đánh giá mức độ u phát triển lên trên chèn ép giao thoa thị và sang hai '
                        'bên xoang hang, hội chẩn phẫu thuật thần kinh nội soi qua xoang bướm nếu u kháng thuốc.',
                        'Tư vấn về khả năng phục hồi chu kỳ kinh nguyệt và khả năng có thai tự nhiên sau khi prolactin '
                        'máu trở về ngưỡng bình thường, hướng dẫn ngừng thuốc khi phát hiện có thai.',
                        'Khám chuyên khoa mắt đo thị trường tự động mỗi 3 tháng trong thời gian điều trị tấn công, hẹn '
                        'tái khám sau 4 tuần làm lại xét nghiệm prolactin máu.'],
  'bien_the_kham': ['Khám tuyến vú nắn nhẹ có giọt dịch trắng đục dạng sữa trào ra từ các lỗ ống tuyến núm vú, kiểm '
                    'tra thị trường sơ bộ bằng tay thấy thu hẹp thị trường phía thái dương hai mắt, soi đáy mắt không '
                    'thấy phù gai thị, không có các dấu hiệu thần kinh khu trú khác.',
                    'Bệnh nhân có hội chứng tiết sữa vô kinh điển hình, nắn hai bên vú thấy dịch sữa tiết tự nhiên, '
                    'thị lực nhìn rõ 10/10 nhưng thị trường thái dương hai bên bị khuyết góc, tuyến giáp bình thường.',
                    'Khám thực thể không có biểu hiện rậm lông nam hóa, tuyến vú mềm mại không có khối u cục cứng khu '
                    'trú, nồng độ prolactin máu xét nghiệm lúc đói đạt 145 ng/ml.',
                    'Bệnh nhân than đau đầu âm ỉ sau hốc mắt, khám các dây thần kinh sọ III IV VI vận nhãn bình thường '
                    'không sụp mi, đo thị trường kế ghi nhận bán manh đồng danh thái dương mức độ nhẹ.',
                    'Khám phụ khoa cơ quan sinh dục ngoài bình thường niêm mạc hơi nhạt do thiếu estrogen, nắn núm vú '
                    'hai bên có giọt sữa trắng chảy ra, huyết áp 115/75 mmHg.',
                    'Thể trạng trung bình, không có kiểu hình to đầu chi hay hội chứng Cushing, nắn vú tiết dịch trắng '
                    'đục hai bên, kiểm tra phản xạ đồng tử với ánh sáng bình thường.'],
  'chan_doan': 'U tuyến yên tiết prolactin prolactinoma thể u vi thể microprolactinoma.',
  'chinh': ['tiết dịch màu trắng đục như sữa tự nhiên ở hai núm vú không liên quan đến sinh con',
            'rối loạn chu kỳ kinh nguyệt thưa kinh hoặc vô kinh thứ phát kéo dài nhiều tháng',
            'nồng độ prolactin huyết tương khi xét nghiệm tăng rất cao vượt trên 100 ng/ml'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Chỉ định chụp cộng hưởng từ MRI sọ não vùng tuyến yên có tiêm thuốc đối quang từ gadolinium dựng hình '
              'lát mỏng để đo kích thước khối u, đo thị trường kế tự động bằng máy Humphrey, bắt đầu điều trị nội khoa '
              'bằng thuốc đồng vận dopamine cabergoline liều 0.5mg/tuần chia 2 lần hoặc bromocriptine 2.5mg/ngày, theo '
              'dõi nồng độ prolactin máu định kỳ.',
  'kham': 'Khám tuyến vú nắn nhẹ có giọt dịch trắng đục dạng sữa trào ra từ các lỗ ống tuyến núm vú, kiểm tra thị '
          'trường sơ bộ bằng tay thấy thu hẹp thị trường phía thái dương hai mắt, soi đáy mắt không thấy phù gai thị, '
          'không có các dấu hiệu thần kinh khu trú khác.',
  'nhom': 'người lớn',
  'phu': ['đau đầu âm ỉ vùng trán thái dương tăng dần không đáp ứng với thuốc giảm đau thông thường',
          'giảm thị lực thu hẹp thị trường phía ngoài hai bên thái dương (bán manh hai bên thái dương)',
          'khó thụ thai và suy giảm ham muốn tình dục kèm theo khô rát niêm mạc'],
  'ten': 'u tuyến yên tiết prolactin prolactinoma'},
 {'bien_the_chan_doan': ['Bệnh to đầu chi Acromegaly do u tuyến yên tăng tiết hormone tăng trưởng GH.',
                         'Theo dõi bệnh to đầu chi Acromegaly thể u lớn chèn ép cuống tuyến yên.',
                         'Bệnh to đầu chi Acromegaly có biến chứng đái tháo đường thứ phát và tăng huyết áp.',
                         'Bệnh to đầu chi Acromegaly kèm hội chứng ngưng thở khi ngủ tắc nghẽn OSA.',
                         'Theo dõi bệnh to đầu chi Acromegaly có hội chứng ống cổ tay hai bên.',
                         'Bệnh to đầu chi Acromegaly giai đoạn chuẩn bị can thiệp phẫu thuật nội soi.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ yếu tố tăng trưởng giống insulin 1 (IGF-1) huyết thanh chuẩn hóa theo tuổi '
                        'và giới tính, thực hiện nghiệm pháp dung nạp glucose đường uống 75g đo nồng độ hormone GH '
                        '(OGTT-GH) khẳng định mất ức chế GH, chụp MRI sọ não vùng hố yên có cản quang đánh giá khối u '
                        'tuyến yên, hội chẩn chuyên khoa phẫu thuật thần kinh chỉ định phẫu thuật nội soi cắt u qua '
                        'xoang bướm.',
                        'Chỉ định siêu âm tim đánh giá bệnh cơ tim phì đại và chức năng tâm trương thất trái, đo đa ký '
                        'giấc ngủ chẩn đoán hội chứng ngưng thở khi ngủ OSA, soi đại tràng tầm soát polyp đại tràng.',
                        'Kê đơn điều trị nội khoa chuẩn bị trước mổ bằng thuốc đồng vận somatostatin tác dụng kéo dài '
                        'octreotide LAR hoặc lanreotide tiêm bắp mỗi 4 tuần để làm giảm thể tích u.',
                        'Làm bilan xét nghiệm chức năng tuyến yên toàn bộ gồm TSH FT4 ACTH cortisol buổi sáng để tầm '
                        'soát suy tuyến yên kèm theo, kiểm soát huyết áp và đường huyết bằng phác đồ chuẩn.',
                        'Tư vấn bệnh nhân về phẫu thuật nội soi qua đường mũi xoang bướm là phương pháp điều trị hàng '
                        'đầu giúp giảm áp lực và đưa GH/IGF-1 về ngưỡng an toàn.',
                        'Theo dõi nồng độ IGF-1 và GH máu sau phẫu thuật 3 tháng để đánh giá tiêu chuẩn khỏi bệnh sinh '
                        'hóa, xét nghiệm bổ sung pegvisomant nếu còn tồn dư u.'],
  'bien_the_kham': ['Khuôn mặt biến đổi thô đặc trưng của bệnh to đầu chi: trán dô cung mày gồ cao, xương hàm dưới '
                    'phát triển chìa ra trước (prognathism) làm khớp cắn lệch răng thưa, môi dày lưỡi to chiếm khoang '
                    'miệng, bàn tay to bè ngón tay hình thoi da lòng bàn tay dày mọng mồ hôi, huyết áp 150/95 mmHg, '
                    'nghe tim có tiếng T4.',
                    'Bệnh nhân có diện mạo to thô rõ rệt, hai bàn chân to bè phải đi dép cỡ 44 dù trước đây đi cỡ 39, '
                    'giọng nói vang trầm đặc biệt, đo huyết áp tăng vừa, mạch đập nảy mạnh.',
                    'Khám thấy da mặt nhờn dày lỗ chân lông to, các ngón tay to bè như quả chuối khó nắm chặt bàn tay, '
                    'lưỡi to có dấu ấn răng ở bờ lưỡi, khám thị trường phát hiện bán manh thái dương nhẹ.',
                    'Bệnh nhân có cằm nhô dài ra trước, khoảng cách giữa các răng cửa hàm dưới thưa rộng, bàn tay to '
                    'dày sờ mềm do phù mô đệm, nhịp tim đều 78 ck/p không có tiếng thổi tim.',
                    'Khám lâm sàng ghi nhận hội chứng ống cổ tay hai bên do phì đại mô mềm chèn ép thần kinh giữa (dấu '
                    'Tinel và Phalen dương tính), các khớp bàn ngón tay sưng to nhưng không viêm đỏ.',
                    'Hình thái người bệnh thay đổi rõ rệt qua các bức ảnh chụp nhiều năm trước, bàn tay bàn chân to '
                    'dày khác thường, đo đường huyết đói tăng nhẹ 7.4 mmol/l, tuyến giáp to lan tỏa độ 1.'],
  'chan_doan': 'Bệnh to đầu chi Acromegaly do u tuyến yên tăng tiết hormone tăng trưởng GH.',
  'chinh': ['bàn tay bàn chân to bè dày cộm phải tăng kích cỡ nhẫn đeo và cỡ giày liên tục',
            'khuôn mặt biến đổi thô ráp: cung mày nhô cao cằm chìa ra phía trước và răng thưa dần',
            'môi dày lưỡi to giọng nói trầm vang đục ồm ồm khác hẳn trước đây'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Định lượng nồng độ yếu tố tăng trưởng giống insulin 1 (IGF-1) huyết thanh chuẩn hóa theo tuổi và giới '
              'tính, thực hiện nghiệm pháp dung nạp glucose đường uống 75g đo nồng độ hormone GH (OGTT-GH) khẳng định '
              'mất ức chế GH, chụp MRI sọ não vùng hố yên có cản quang đánh giá khối u tuyến yên, hội chẩn chuyên khoa '
              'phẫu thuật thần kinh chỉ định phẫu thuật nội soi cắt u qua xoang bướm.',
  'kham': 'Khuôn mặt biến đổi thô đặc trưng của bệnh to đầu chi: trán dô cung mày gồ cao, xương hàm dưới phát triển '
          'chìa ra trước (prognathism) làm khớp cắn lệch răng thưa, môi dày lưỡi to chiếm khoang miệng, bàn tay to bè '
          'ngón tay hình thoi da lòng bàn tay dày mọng mồ hôi, huyết áp 150/95 mmHg, nghe tim có tiếng T4.',
  'nhom': 'người lớn',
  'phu': ['đau nhức các khớp bàn ngón tay khớp gối và đau mỏi cột sống thắt lưng',
          'da dày nhiều dầu nhờn tăng tiết mồ hôi toàn thân có mùi khó chịu',
          'kèm theo ngáy to khi ngủ và các cơn ngưng thở lúc ngủ do phì đại mô mềm họng'],
  'ten': 'bệnh to đầu chi Acromegaly'},
 {'bien_the_chan_doan': ['Viêm tuyến giáp Hashimoto giai đoạn suy giáp tiên phát.',
                         'Theo dõi viêm tuyến giáp Hashimoto giai đoạn suy giáp dưới lâm sàng TSH tăng nhẹ.',
                         'Viêm tuyến giáp Hashimoto có bướu giáp to lan tỏa mật độ chắc.',
                         'Viêm tuyến giáp Hashimoto tự miễn có kháng thể Anti-TPO và Anti-Tg dương tính cao.',
                         'Theo dõi viêm tuyến giáp Hashimoto thể teo tuyến giáp suy giáp rõ.',
                         'Viêm tuyến giáp Hashimoto đang điều trị bù hormone giáp đạt bình giáp.'],
  'bien_the_ke_hoach': ['Xét nghiệm hormone tuyến giáp định lượng nồng độ TSH và FT4 trong máu, siêu âm tuyến giáp '
                        'đánh giá hình thái nhu mô tuyến giáp giảm âm lan tỏa không đều dạng tổ ong, chỉ định điều trị '
                        'thay thế bằng hormone tuyến giáp tổng hợp levothyroxine liều khởi đầu 50 mcg/ngày uống lúc '
                        'bụng đói buổi sáng trước ăn 30-60 phút, hẹn xét nghiệm lại TSH sau 6-8 tuần để chỉnh liều tối '
                        'ưu.',
                        'Kê đơn levothyroxine 50 mcg uống duy nhất một lần vào buổi sáng cách bữa ăn sáng ít nhất 30 '
                        'phút, dặn dò không uống cùng lúc với viên canxi hay sắt vì làm giảm hấp thu thuốc.',
                        'Xét nghiệm định lượng nồng độ lipid máu toàn phần kiểm tra tình trạng tăng cholesterol thứ '
                        'phát do suy giáp, hướng dẫn theo dõi các dấu hiệu quá liều như hồi hộp đánh trống ngực run '
                        'tay.',
                        'Siêu âm doppler tuyến giáp định kỳ hàng năm theo dõi phát hiện các nhân giáp nghi ngờ trên '
                        'nền viêm tự miễn để chọc hút tế bào kim nhỏ FNA nếu có chỉ định.',
                        'Tư vấn giải thích cho bệnh nhân đây là bệnh lý tự miễn mạn tính cần điều trị hormone thay thế '
                        'lâu dài suốt đời, trấn an thuốc levothyroxine giống hệt hormone tự nhiên của cơ thể.',
                        'Đo nồng độ TSH sau mỗi 2 tháng cho đến khi TSH đạt mục tiêu trong khoảng tham chiếu 0.5-2.5 '
                        'mIU/L, sau đó kiểm tra định kỳ mỗi 6-12 tháng một lần.'],
  'bien_the_kham': ['Sờ tuyến giáp to độ 1b-2 lan tỏa hai thùy và eo tuyến, mật độ chắc đồng đều như cao su, bề mặt '
                    'hơi gồ ghề ranh giới rõ, không đau khi nắn, không có rung miêu hay tiếng thổi mạch máu, nhịp tim '
                    'chậm đều 56 ck/p, phản xạ gân gót thời gian hồi chậm rõ rệt, da hai cẳng chân khô ráp.',
                    'Bệnh nhân có nét mặt đờ đẫn mi mắt hơi húp nặng nề, tuyến giáp to chắc không đau di động tốt theo '
                    'nhịp nuốt, tiếng tim mờ nhịp chậm 54 lần/phút, da lòng bàn tay hơi vàng nhẹ do chậm chuyển hóa '
                    'caroten.',
                    'Khám cổ phát hiện bướu giáp lan tỏa mật độ chắc đanh ranh giới rõ ràng, không sờ thấy hạch cổ to, '
                    'giọng nói hơi khàn nhẹ, huyết áp 130/85 mmHg với huyết áp tâm trương tăng nhẹ.',
                    'Bệnh nhân mặc áo ấm trong phòng khám dù thời tiết bình thường (chứng sợ lạnh), tuyến giáp to đều '
                    'hai bên bề mặt hơi hạt hạt, ấn không đau, phản xạ gân xương gân bánh chè hồi chậm.',
                    'Khám vùng trước cổ thấy tuyến giáp nổi rõ thể tích tăng gấp rưỡi bình thường mật độ chắc, khám '
                    'mắt bình thường không lồi mắt không co rút cơ mi trên, không có run ngón tay.',
                    'Thể trạng hơi thừa cân phù nhẹ mặt và mu bàn tay ấn không để lại vết lõm, bướu cổ to chắc lan tỏa '
                    'không tiếng thổi, nghe tim nhịp xoang chậm 58 ck/p, bụng chướng nhẹ do giảm nhu động ruột.'],
  'chan_doan': 'Viêm tuyến giáp Hashimoto giai đoạn suy giáp tiên phát.',
  'chinh': ['tuyến giáp to lan tỏa hai thùy mật độ chắc như cao su không đau khi sờ nắn',
            'các biểu hiện suy giáp tiến triển: sợ lạnh mệt mỏi uể oải chậm chạp tăng cân nhẹ',
            'nồng độ kháng thể kháng peroxidase tuyến giáp (Anti-TPO) huyết thanh tăng rất cao'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Xét nghiệm hormone tuyến giáp định lượng nồng độ TSH và FT4 trong máu, siêu âm tuyến giáp đánh giá hình '
              'thái nhu mô tuyến giáp giảm âm lan tỏa không đều dạng tổ ong, chỉ định điều trị thay thế bằng hormone '
              'tuyến giáp tổng hợp levothyroxine liều khởi đầu 50 mcg/ngày uống lúc bụng đói buổi sáng trước ăn 30-60 '
              'phút, hẹn xét nghiệm lại TSH sau 6-8 tuần để chỉnh liều tối ưu.',
  'kham': 'Sờ tuyến giáp to độ 1b-2 lan tỏa hai thùy và eo tuyến, mật độ chắc đồng đều như cao su, bề mặt hơi gồ ghề '
          'ranh giới rõ, không đau khi nắn, không có rung miêu hay tiếng thổi mạch máu, nhịp tim chậm đều 56 ck/p, '
          'phản xạ gân gót thời gian hồi chậm rõ rệt, da hai cẳng chân khô ráp.',
  'nhom': 'người lớn',
  'phu': ['da khô ráp bong vảy tóc rụng nhiều xơ xác móng tay giòn dễ gãy',
          'táo bón kéo dài nhịp tim chậm dưới 60 lần/phút phản xạ gân gót hồi chậm',
          'phù niêm cứng vùng mặt và trước xương chày ấn ngón tay không lõm'],
  'ten': 'viêm tuyến giáp Hashimoto'},
 {'bien_the_chan_doan': ['Bướu cổ đơn thuần dịch tễ thiếu iod thể bình giáp lâm sàng.',
                         'Theo dõi bướu cổ đơn thuần dịch tễ thiếu iod mức độ to độ 2 lan tỏa.',
                         'Bướu cổ đơn thuần dịch tễ thiếu iod không có biến chứng chèn ép.',
                         'Bướu cổ đơn thuần dịch tễ thiếu iod ở người sinh sống vùng núi cao.',
                         'Theo dõi bướu cổ đơn thuần dịch tễ thiếu iod thể nhu mô mềm đồng nhất.',
                         'Bướu cổ đơn thuần dịch tễ thiếu iod giai đoạn theo dõi dinh dưỡng bổ sung.'],
  'bien_the_ke_hoach': ['Chỉ định siêu âm tuyến giáp để đo thể tích các thùy tuyến giáp và kiểm tra cấu trúc nhu mô '
                        'đồng nhất loại trừ nhân giáp ẩn, làm xét nghiệm TSH và FT4 để khẳng định tình trạng bình '
                        'giáp, tư vấn chế độ ăn bổ sung muối iod đều đặn hàng ngày trong các bữa ăn gia đình kết hợp '
                        'tăng cường ăn hải sản cá biển rong biển, theo dõi định kỳ kích thước bướu mỗi 6 tháng.',
                        'Tư vấn giáo dục dinh dưỡng cộng đồng về cách bảo quản muối iod trong lọ kín tránh ánh sáng '
                        'trực tiếp và nêm muối sau khi nấu chín để tránh thăng hoa iod, ăn thêm hải sản 2 bữa mỗi '
                        'tuần.',
                        'Siêu âm kiểm tra đường kính trước sau và thể tích toàn bộ tuyến giáp, nếu tuyến giáp to nhiều '
                        'gây vướng có thể cân nhắc dùng levothyroxine liều thấp ức chế TSH tạm thời trong 6 tháng.',
                        'Khuyên bệnh nhân không sử dụng các loại thuốc nam lá đắp cổ không rõ nguồn gốc có thể gây '
                        'bỏng da hoặc nhiễm độc, tái khám nếu bướu to nhanh hoặc xuất hiện nuốt nghẹn khó thở.',
                        'Xét nghiệm định lượng iod niệu ngẫu nhiên nếu có điều kiện để đánh giá mức độ thiếu hụt iod '
                        'trong khẩu phần ăn của bệnh nhân và gia đình.',
                        'Lập hồ sơ theo dõi ngoại trú đo chu vi vòng cổ định kỳ bằng thước dây, siêu âm kiểm tra sau 6 '
                        'tháng đánh giá mức độ thu nhỏ của bướu sau bổ sung muối iod.'],
  'bien_the_kham': ['Nhìn thấy khối phồng cân đối vùng trước cổ di động nhịp nhàng theo động tác nuốt, sờ tuyến giáp '
                    'to lan tỏa độ 2 mật độ mềm mại đồng đều không có nhân khu trú, không có rung miêu không nghe thấy '
                    'tiếng thổi mạch máu, mắt không lồi, run tay biên độ nhỏ âm tính, nhịp tim đều 72 ck/p.',
                    'Khám vùng cổ trước thấy tuyến giáp phì đại đều hai thùy sờ mềm trơn láng ranh giới rõ với cơ ức '
                    'đòn chũm, không có hạch cổ to, mạch đập đều 74 lần/phút huyết áp 115/75 mmHg.',
                    'Bướu cổ to độ 1b ngửa đầu nhìn thấy rõ, sờ không thấy nhân cứng, ấn không đau tức, người bệnh '
                    'không có triệu chứng nhiễm độc giáp hay suy giáp, phản xạ bình thường.',
                    'Khám lâm sàng ghi nhận tuyến giáp to lan tỏa dạng sinh lý dịch tễ ở người vùng trung du miền núi, '
                    'bề mặt nhẵn bóng không tiếng thổi mạch, tim phổi bình thường.',
                    'Tuyến giáp to hai bên cân xứng di động tốt khi nuốt nước bọt, thể tích hai thùy to nhẹ, không '
                    'chèn ép khí quản không có tiếng thở rít stridor, các dấu hiệu sinh tồn ổn định.',
                    'Khám vùng trước cổ có khối bướu mềm mại đồng nhất, không có triệu chứng lồi mắt Von Graefe hay '
                    'Dalrymple, xét nghiệm hormone TSH máu 1.85 uIU/ml hoàn toàn bình thường.'],
  'chan_doan': 'Bướu cổ đơn thuần dịch tễ thiếu iod thể bình giáp lâm sàng.',
  'chinh': ['tuyến giáp to đều hai bên vùng trước cổ to dần chậm chạp qua nhiều năm',
            'sinh sống lâu năm trong vùng địa dư thiếu iod vùng cao hoặc thói quen ăn muối không iod',
            'hoàn toàn không có triệu chứng run tay gầy sụt cân hồi hộp hay sợ nóng'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Chỉ định siêu âm tuyến giáp để đo thể tích các thùy tuyến giáp và kiểm tra cấu trúc nhu mô đồng nhất '
              'loại trừ nhân giáp ẩn, làm xét nghiệm TSH và FT4 để khẳng định tình trạng bình giáp, tư vấn chế độ ăn '
              'bổ sung muối iod đều đặn hàng ngày trong các bữa ăn gia đình kết hợp tăng cường ăn hải sản cá biển rong '
              'biển, theo dõi định kỳ kích thước bướu mỗi 6 tháng.',
  'kham': 'Nhìn thấy khối phồng cân đối vùng trước cổ di động nhịp nhàng theo động tác nuốt, sờ tuyến giáp to lan tỏa '
          'độ 2 mật độ mềm mại đồng đều không có nhân khu trú, không có rung miêu không nghe thấy tiếng thổi mạch máu, '
          'mắt không lồi, run tay biên độ nhỏ âm tính, nhịp tim đều 72 ck/p.',
  'nhom': 'cả hai',
  'phu': ['cảm giác hơi vướng nhẹ ở cổ khi nuốt thức ăn đặc hoặc khi cài khuy cổ áo',
          'không sốt không đau nhức tại vùng tuyến giáp và vùng cổ',
          'xét nghiệm chức năng tuyến giáp FT4 và TSH hoàn toàn trong giới hạn bình thường'],
  'ten': 'bướu cổ đơn thuần dịch tễ thiếu iod'},
 {'bien_the_chan_doan': ['Cường cận giáp tiên phát do u tuyến cận giáp đơn độc.',
                         'Theo dõi cường cận giáp tiên phát do u tuyến cận giáp cực dưới bên phải.',
                         'Cường cận giáp tiên phát có biến chứng sỏi thận tái diễn hai bên.',
                         'Cường cận giáp tiên phát có loãng xương nặng vùng cổ xương đùi.',
                         'Theo dõi cường cận giáp tiên phát thể tăng canxi máu không triệu chứng rầm rộ.',
                         'Cường cận giáp tiên phát giai đoạn chuẩn bị phẫu thuật nội soi cắt u.'],
  'bien_the_ke_hoach': ['Đo mật độ khoáng xương toàn thân bằng phương pháp DEXA đánh giá loãng xương vỏ xương (vị trí '
                        '1/3 xương quay), siêu âm vùng cổ độ phân giải cao kết hợp xạ hình tuyến cận giáp bằng '
                        'Technetium-99m Sestamibi (SPECT/CT) để định vị chính xác vị trí u tuyến cận giáp đơn độc, xét '
                        'nghiệm canxi niệu 24 giờ loại trừ hội chứng tăng canxi máu hạ canxi niệu gia đình FHH, hội '
                        'chẩn phẫu thuật cắt bỏ u tuyến cận giáp xâm lấn tối thiểu.',
                        'Hướng dẫn uống nhiều nước lọc từ 2.5 đến 3 lít mỗi ngày để tăng đào thải canxi qua đường tiểu '
                        'phòng ngừa cơn tăng canxi máu cấp và hạn chế hình thành sỏi thận mới.',
                        'Chỉ định chụp cắt lớp vi tính 4D vùng cổ (4D-CT parathyroid) nếu kết quả siêu âm và xạ hình '
                        'Sestamibi chưa đồng thuận vị trí khối u tuyến.',
                        'Xét nghiệm định lượng vitamin 25-OH-D máu để bổ sung thận trọng nếu có thiếu hụt vitamin D đi '
                        'kèm, tránh dùng thuốc lợi tiểu nhóm thiazide vì làm tăng canxi máu.',
                        'Tư vấn phẫu thuật cắt u tuyến cận giáp có định lượng nồng độ PTH trong mổ (intraoperative '
                        'PTH) để khẳng định đã lấy trọn khối u khi PTH giảm trên 50% sau cắt.',
                        'Theo dõi sát nồng độ canxi máu sau phẫu thuật phòng ngừa hội chứng xương đói (hungry bone '
                        'syndrome) gây hạ canxi máu đột ngột sau mổ.'],
  'bien_the_kham': ['Thể trạng mệt mỏi uể oải, da niêm mạc bình thường, khám vùng cổ không sờ thấy khối u tuyến cận '
                    'giáp (do u tuyến cận giáp thường nhỏ nằm sâu sau thùy giáp), huyết áp 142/88 mmHg, trương lực cơ '
                    'tứ chi giảm nhẹ, ấn dọc các xương dài và xương sườn có điểm đau tức mơ hồ, tim nhịp đều 72 ck/p.',
                    'Bệnh nhân than mỏi mệt yếu cơ gốc chi, khám cơ lực chi dưới 4/5, không có dấu hiệu co giật, canxi '
                    'máu toàn phần xét nghiệm đo được 2.85 mmol/l (tăng cao) kèm phospho máu giảm 0.72 mmol/l.',
                    'Khám vùng cổ bình thường không có sẹo mổ cũ, ấn các gai sống thắt lưng có cảm giác đau tức nhẹ, '
                    'huyết áp tăng nhẹ, điện tâm đồ có khoảng QT ngắn lại do tăng canxi máu.',
                    'Bệnh nhân có tiền sử mổ tán sỏi thận 2 lần, khám hiện tại bụng mềm không đau hông lưng, sờ tuyến '
                    'giáp mềm không nhân, nồng độ PTH huyết thanh tăng vọt 135 pg/ml.',
                    'Khám thần kinh cơ ghi nhận giảm trương lực cơ toàn thân nhẹ, phản xạ gân xương bình thường, bệnh '
                    'nhân uống nước liên tục do khát nước và tiểu nhiều lần trong ngày.',
                    'Thể trạng gầy nhẹ, khám các khớp không sưng nóng đỏ, chụp X-quang bàn tay phát hiện hình ảnh tiêu '
                    'dưới màng xương ở các đốt ngón tay đặc trưng của cường cận giáp.'],
  'chan_doan': 'Cường cận giáp tiên phát do u tuyến cận giáp đơn độc.',
  'chinh': ['xét nghiệm tăng canxi máu toàn phần và canxi ion hóa kéo dài không giải thích được',
            'nồng độ hormone tuyến cận giáp PTH huyết thanh tăng cao không phù hợp với mức canxi máu',
            'tiền sử sỏi đường tiết niệu hai bên tái phát nhiều lần hoặc sỏi thận cản quang'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Đo mật độ khoáng xương toàn thân bằng phương pháp DEXA đánh giá loãng xương vỏ xương (vị trí 1/3 xương '
              'quay), siêu âm vùng cổ độ phân giải cao kết hợp xạ hình tuyến cận giáp bằng Technetium-99m Sestamibi '
              '(SPECT/CT) để định vị chính xác vị trí u tuyến cận giáp đơn độc, xét nghiệm canxi niệu 24 giờ loại trừ '
              'hội chứng tăng canxi máu hạ canxi niệu gia đình FHH, hội chẩn phẫu thuật cắt bỏ u tuyến cận giáp xâm '
              'lấn tối thiểu.',
  'kham': 'Thể trạng mệt mỏi uể oải, da niêm mạc bình thường, khám vùng cổ không sờ thấy khối u tuyến cận giáp (do u '
          'tuyến cận giáp thường nhỏ nằm sâu sau thùy giáp), huyết áp 142/88 mmHg, trương lực cơ tứ chi giảm nhẹ, ấn '
          'dọc các xương dài và xương sườn có điểm đau tức mơ hồ, tim nhịp đều 72 ck/p.',
  'nhom': 'người lớn',
  'phu': ['đau mỏi xương khớp lan tỏa giảm mật độ chất khoáng xương loãng xương sớm',
          'táo bón mạn tính chán ăn nôn nao buồn nôn và mệt mỏi suy nhược toàn thân',
          'tiểu nhiều khát nước nhiều do giảm khả năng cô đặc nước tiểu của ống thận'],
  'ten': 'cường cận giáp tiên phát do u tuyến'},
 {'bien_the_chan_doan': ['Suy cận giáp sau phẫu thuật tuyến giáp mạn tính có hạ canxi máu.',
                         'Theo dõi suy cận giáp sau phẫu thuật tuyến giáp vĩnh viễn sau mổ ung thư giáp.',
                         'Suy cận giáp sau phẫu thuật tuyến giáp mức độ trung bình có cơn co thắt cơ tetany.',
                         'Suy cận giáp sau phẫu thuật tuyến giáp đáp ứng ổn định với calcitriol và canxi.',
                         'Theo dõi suy cận giáp sau phẫu thuật tuyến giáp kèm giảm nồng độ magie máu phối hợp.',
                         'Suy cận giáp sau phẫu thuật tuyến giáp giai đoạn chỉnh liều thuốc ngoại trú.'],
  'bien_the_ke_hoach': ['Xét nghiệm điện giải đồ đo canxi máu toàn phần canxi ion hóa albumin phospho và magie máu, đo '
                        'điện tâm đồ kiểm tra khoảng QT kéo dài, chỉ định bổ sung canxi đường uống canxi cacbonat '
                        '1000-2000mg canxi nguyên tố/ngày chia nhiều lần kết hợp chất chuyển hóa hoạt tính của vitamin '
                        'D calcitriol 0.25-0.5 mcg/ngày, theo dõi canxi niệu 24 giờ định kỳ tránh biến chứng sỏi thận '
                        'vôi hóa thận.',
                        'Kê đơn viên sủi canxi cacbonat 500mg uống 3 lần mỗi ngày sau ăn kết hợp viên nang calcitriol '
                        '0.25 mcg ngày 2 lần, hướng dẫn nhận biết sớm các triệu chứng tê môi chuột rút để uống thêm '
                        'liều canxi dự phòng.',
                        'Kiểm tra nồng độ magie huyết thanh bổ sung magie đường uống nếu có hạ magie máu vì thiếu '
                        'magie sẽ ức chế giải phóng và làm kháng tác dụng của PTH còn lại.',
                        'Mục tiêu điều trị duy trì nồng độ canxi máu toàn phần ở giới hạn dưới bình thường (2.0-2.15 '
                        'mmol/l) để tránh triệu chứng co giật mà không làm tăng canxi niệu quá mức gây sỏi thận.',
                        'Đo canxi niệu 24 giờ định kỳ mỗi 6 tháng, nếu canxi niệu vượt quá 300mg/24 giờ cân nhắc phối '
                        'hợp thuốc lợi tiểu thiazide liều thấp để tăng tái hấp thu canxi ở ống thận.',
                        'Tư vấn dinh dưỡng bổ sung thực phẩm giàu canxi như sữa chua phô mai đậu phụ cá nhỏ ăn cả '
                        'xương, dặn dò luôn mang theo vài viên canxi sủi bên người để xử trí cấp thời.'],
  'bien_the_kham': ['Khám vùng cổ có vết sẹo mổ ngang nếp lằn cổ lành sẹo tốt, nghiệm pháp Chvostek dương tính rõ (gõ '
                    'nhẹ vào vị trí trước nắp tai trên đường đi dây thần kinh mặt gây co giật cơ mép và cánh mũi cùng '
                    'bên), nghiệm pháp Trousseau dương tính (bơm băng đo huyết áp cao hơn huyết áp tâm thu 20 mmHg giữ '
                    '3 phút gây co quắp bàn tay kiểu người đỡ đẻ), tim đều 70 ck/p.',
                    'Bệnh nhân có biểu hiện co thắt ngón tay quắp vào trong (bàn tay người đỡ đẻ carpopedal spasm) khi '
                    'đang đo huyết áp, gõ trước gờ tai mép môi giật mạnh (dấu Chvostek độ 2), canxi toàn phần đo được '
                    '1.75 mmol/l.',
                    'Khám lâm sàng phát hiện dấu hiệu tăng tính kích thích thần kinh cơ rõ rệt, sẹo mổ cắt tuyến giáp '
                    '2 tháng trước liền tốt, bệnh nhân than tê rần quanh môi như kiến cắn liên tục.',
                    'Nghiệm pháp Trousseau xuất hiện sau 90 giây bơm băng huyết áp bàn tay co cứng gập cổ tay duỗi '
                    'khớp liên đốt, nồng độ PTH huyết thanh đo được 4.2 pg/ml (giảm sâu dưới ngưỡng 15 pg/ml).',
                    'Bệnh nhân lo âu căng thẳng, nhịp tim đều 74 ck/p, nghe tim phổi bình thường, phản xạ gân xương tứ '
                    'chi tăng nhạy, dấu hiệu Chvostek dương tính hai bên đối xứng.',
                    'Khám thấy da khô móng tay có nhiều khía rãnh ngang dễ gãy do thiếu canxi kéo dài, sẹo mổ vùng cổ '
                    'mềm không đau, khám mắt không thấy đục thủy tinh thể dưới bao.'],
  'chan_doan': 'Suy cận giáp sau phẫu thuật tuyến giáp mạn tính có hạ canxi máu.',
  'chinh': ['tiền sử phẫu thuật cắt toàn bộ tuyến giáp hoặc nạo vét hạch cổ diện rộng',
            'cảm giác tê bì châm chích kiến bò quanh vùng miệng môi và các đầu ngón tay ngón chân',
            'các cơn co thắt cơ chuột rút đau đớn ở bàn tay bàn chân tạo tư thế bàn tay người đỡ đẻ'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Xét nghiệm điện giải đồ đo canxi máu toàn phần canxi ion hóa albumin phospho và magie máu, đo điện tâm '
              'đồ kiểm tra khoảng QT kéo dài, chỉ định bổ sung canxi đường uống canxi cacbonat 1000-2000mg canxi '
              'nguyên tố/ngày chia nhiều lần kết hợp chất chuyển hóa hoạt tính của vitamin D calcitriol 0.25-0.5 '
              'mcg/ngày, theo dõi canxi niệu 24 giờ định kỳ tránh biến chứng sỏi thận vôi hóa thận.',
  'kham': 'Khám vùng cổ có vết sẹo mổ ngang nếp lằn cổ lành sẹo tốt, nghiệm pháp Chvostek dương tính rõ (gõ nhẹ vào vị '
          'trí trước nắp tai trên đường đi dây thần kinh mặt gây co giật cơ mép và cánh mũi cùng bên), nghiệm pháp '
          'Trousseau dương tính (bơm băng đo huyết áp cao hơn huyết áp tâm thu 20 mmHg giữ 3 phút gây co quắp bàn tay '
          'kiểu người đỡ đẻ), tim đều 70 ck/p.',
  'nhom': 'người lớn',
  'phu': ['nồng độ canxi máu toàn phần và canxi ion hóa giảm thấp dưới ngưỡng bình thường',
          'xét nghiệm hormone cận giáp PTH huyết thanh giảm thấp rõ rệt hoặc không đo được',
          'tâm trạng bồn chồn lo âu dễ cáu gắt và thỉnh thoảng có giật cơ mi mắt tự phát'],
  'ten': 'suy cận giáp sau phẫu thuật tuyến giáp'},
 {'bien_the_chan_doan': ['U tủy thượng thận Pheochromocytoma cơn tăng huyết áp kịch phát.',
                         'Theo dõi u tủy thượng thận Pheochromocytoma bên phải thể tiết noradrenaline ưu thế.',
                         'U tủy thượng thận Pheochromocytoma biến chứng tổn thương cơ quan đích do tăng huyết áp.',
                         'U tủy thượng thận Pheochromocytoma trong bệnh cảnh đa u tuyến nội tiết MEN 2.',
                         'Theo dõi u tủy thượng thận Pheochromocytoma thể có tụt huyết áp tư thế phối hợp.',
                         'U tủy thượng thận Pheochromocytoma giai đoạn chuẩn bị thuốc chẹn alpha trước mổ.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ metanephrine tự do trong huyết tương hoặc metanephrine và normetanephrine '
                        'trong nước tiểu thu thập 24 giờ, chụp cắt lớp vi tính CT bụng hoặc chụp cộng hưởng từ MRI có '
                        'tiêm thuốc khảo sát tuyến thượng thận hai bên, xử trí hạ huyết áp khẩn bằng thuốc chẹn '
                        'alpha-adrenergic phenoxybenzamine hoặc doxazosin chuẩn bị tối thiểu 10-14 ngày trước phẫu '
                        'thuật nội soi cắt bỏ u tuyến thượng thận (tuyệt đối không dùng thuốc chẹn beta trước khi chẹn '
                        'alpha đầy đủ).',
                        'Bắt đầu phác đồ ức chế alpha bằng doxazosin 2mg tăng dần liều lên 8-16mg/ngày cho đến khi '
                        'kiểm soát được huyết áp và xuất hiện nghẹt mũi nhẹ, sau đó mới phối hợp thuốc chẹn beta '
                        'propranolol để kiểm soát nhịp tim nhanh.',
                        'Hướng dẫn chế độ ăn tăng muối và uống nhiều nước trong giai đoạn chuẩn bị trước phẫu thuật để '
                        'bù lại thể tích lòng mạch bị co thắt mạn tính do thừa catecholamine.',
                        'Chỉ định xạ hình MIBG (I-123 metaiodobenzylguanidine) hoặc chụp PET/CT với Gallium-68 '
                        'DOTATATE để tầm soát các ổ u ngoài tuyến thượng thận (paraganglioma) hoặc di căn.',
                        'Tư vấn phẫu thuật nội soi sau phúc mạc cắt u tuyến thượng thận, chuẩn bị sẵn sàng thuốc vận '
                        'mạch và dịch truyền phòng ngừa tụt huyết áp sâu ngay sau khi kẹp cuống mạch nuôi u.',
                        'Tầm soát đột biến gen RET VHL NF1 và SDH cho bệnh nhân và người thân trực hệ nếu phát hiện u '
                        'tủy thượng thận ở lứa tuổi thanh niên hoặc u hai bên.'],
  'bien_the_kham': ['Trong cơn bệnh nhân da tái nhợt lạnh, vã mồ hôi ướt đẫm trán và lưng áo, đồng tử hai bên giãn nhẹ '
                    'phản xạ ánh sáng tốt, nhịp tim nhanh xoang 125 chu kỳ/phút, huyết áp đo được 215/120 mmHg, khám '
                    'bụng mềm không sờ thấy khối u thượng thận (không ấn sâu vùng thượng thận tránh kích thích phóng '
                    'thích catecholamine ồ ạt).',
                    'Bệnh nhân vào cấp cứu với cơn đau đầu dữ dội như búa bổ, nhịp tim nhanh 130 ck/p, đo huyết áp tay '
                    'phải 210/115 mmHg tay trái 208/110 mmHg, da toàn thân tái nhợt vã mồ hôi đầm đìa.',
                    'Khám lâm sàng trong cơn thấy run các ngón tay biên độ lớn, nhịp thở nhanh 24 ck/p, nghe tim tiếng '
                    'T1 T2 đập rất mạnh không có tiếng thổi, đáy mắt có dấu hiệu co thắt động mạch võng mạc cấp.',
                    'Bệnh nhân biểu hiện hoảng loạn lo sợ cực độ, huyết áp vọt lên 220/125 mmHg sau đó 30 phút tự hạ '
                    'xuống 150/90 mmHg kèm theo mệt lả và tiểu nhiều sau cơn.',
                    'Khám ngoài cơn bệnh nhân tỉnh táo da niêm mạc hồng hào, huyết áp đo lúc nghỉ 135/85 mmHg, nhịp '
                    'tim 80 ck/p, khám bụng không sờ thấy khối u bất thường ở hai hố thắt lưng.',
                    'Cơn kịch phát tái diễn với tam chứng nhức đầu vã mồ hôi tim đập nhanh, điện tâm đồ trong cơn ghi '
                    'nhận nhịp nhanh xoang có thiếu máu cơ tim thoáng qua đoạn ST chênh xuống nhẹ.'],
  'chan_doan': 'U tủy thượng thận Pheochromocytoma cơn tăng huyết áp kịch phát.',
  'chinh': ['tam chứng kinh điển xuất hiện theo cơn: đau đầu dữ dội toát mồ hôi đầm đìa và tim đập nhanh trống ngực',
            'huyết áp tăng vọt cơn kịch phát lên rất cao trên 200/120 mmHg trong cơn',
            'cơn xuất hiện đột ngột kèm theo cảm giác lo sợ hoảng loạn tái mặt và run rẩy'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Định lượng nồng độ metanephrine tự do trong huyết tương hoặc metanephrine và normetanephrine trong nước '
              'tiểu thu thập 24 giờ, chụp cắt lớp vi tính CT bụng hoặc chụp cộng hưởng từ MRI có tiêm thuốc khảo sát '
              'tuyến thượng thận hai bên, xử trí hạ huyết áp khẩn bằng thuốc chẹn alpha-adrenergic phenoxybenzamine '
              'hoặc doxazosin chuẩn bị tối thiểu 10-14 ngày trước phẫu thuật nội soi cắt bỏ u tuyến thượng thận (tuyệt '
              'đối không dùng thuốc chẹn beta trước khi chẹn alpha đầy đủ).',
  'kham': 'Trong cơn bệnh nhân da tái nhợt lạnh, vã mồ hôi ướt đẫm trán và lưng áo, đồng tử hai bên giãn nhẹ phản xạ '
          'ánh sáng tốt, nhịp tim nhanh xoang 125 chu kỳ/phút, huyết áp đo được 215/120 mmHg, khám bụng mềm không sờ '
          'thấy khối u thượng thận (không ấn sâu vùng thượng thận tránh kích thích phóng thích catecholamine ồ ạt).',
  'nhom': 'người lớn',
  'phu': ['run giật các đầu ngón tay và cảm giác đau tức ngực khó thở nghẹn họng trong cơn',
          'gầy sút cân dù ăn uống bình thường do tình trạng tăng chuyển hóa cơ bản quá mức',
          'huyết áp có thể trở về mức bình thường hoặc chỉ tăng nhẹ giữa các cơn kịch phát'],
  'ten': 'u tủy thượng thận Pheochromocytoma'},
 {'bien_the_chan_doan': ['Hội chứng Conn cường aldosteron tiên phát do u vỏ thượng thận tăng tiết aldosteron.',
                         'Theo dõi hội chứng Conn cường aldosteron tiên phát có hạ kali máu có triệu chứng yếu cơ.',
                         'Hội chứng Conn cường aldosteron tiên phát do adenoma tuyến thượng thận trái (hội chứng Conn '
                         'kinh điển).',
                         'Hội chứng Conn cường aldosteron tiên phát thể tăng sản vỏ thượng thận hai bên vô căn.',
                         'Theo dõi hội chứng Conn cường aldosteron tiên phát trên bệnh nhân tăng huyết áp kháng trị.',
                         'Hội chứng Conn cường aldosteron tiên phát giai đoạn chuẩn bị phẫu thuật nội soi.'],
  'bien_the_ke_hoach': ['Thực hiện xét nghiệm tỷ lệ nồng độ aldosterone huyết tương trên hoạt độ renin huyết tương (tỷ '
                        'lệ ARR) sau khi đã chuẩn bị ngừng các thuốc hạ áp gây nhiễu trong 2-4 tuần, làm nghiệm pháp '
                        'khẳng định tải muối truyền dung dịch natri clorid 0.9%, chụp cắt lớp vi tính CT tuyến thượng '
                        'thận lớp mỏng 1-2mm khảo sát u tuyến vỏ thượng thận adenoma, chỉ định phẫu thuật nội soi cắt '
                        'tuyến thượng thận một bên hoặc điều trị nội khoa bằng thuốc kháng thụ thể mineralocorticoid '
                        'spironolactone 50-100mg/ngày.',
                        'Bù kali đường uống bằng viên kali clorid phóng thích kéo dài 600mg ngày 2-3 lần để đưa kali '
                        'máu về ngưỡng an toàn trên 4.0 mmol/l trước khi tiến hành các xét nghiệm nội tiết.',
                        'Chuyển đổi tạm thời các thuốc hạ áp sang nhóm chẹn alpha doxazosin hoặc thuốc giãn mạch trung '
                        'ương verapamil ít ảnh hưởng đến nồng độ renin và aldosteron trong máu.',
                        'Chỉ định lấy mẫu máu tĩnh mạch tuyến thượng thận hai bên (AVS) để xác định bên tăng tiết ưu '
                        'thế trước khi quyết định phẫu thuật nếu hình ảnh CT không rõ ràng.',
                        'Kê đơn thuốc kháng aldosterone eplerenone 50mg/ngày thay thế nếu bệnh nhân nam giới gặp tác '
                        'dụng phụ căng tức tuyến ngực hoặc giảm ham muốn do spironolactone.',
                        'Tư vấn phẫu thuật nội soi sau phúc mạc cắt tuyến thượng thận chứa u adenoma giúp khỏi hoàn '
                        'toàn hạ kali máu và cải thiện huyết áp ở đa số bệnh nhân.'],
  'bien_the_kham': ['Huyết áp đo tại phòng khám 168/102 mmHg cả hai tay dù đang dùng 3 nhóm thuốc hạ áp, thể trạng béo '
                    'vừa không có kiểu hình Cushing, cơ lực tứ chi 4/5 giảm nhẹ gốc chi hai đùi, nhịp tim đều 74 ck/p '
                    'không có tiếng thổi tim, khám mạch ngoại biên hai bên đập rõ không có tiếng thổi động mạch thận.',
                    'Bệnh nhân than mệt mỏi rã rời bắp chân hay bị chuột rút khi ngủ, huyết áp đo được 170/100 mmHg, '
                    'nồng độ kali máu xét nghiệm tại chỗ là 2.9 mmol/l (hạ kali máu rõ), điện tâm đồ có sóng U dẹt '
                    'sóng T.',
                    'Khám lâm sàng không ghi nhận tiếng thổi vùng bụng hai bên rốn loại trừ hẹp động mạch thận, đáy '
                    'mắt có dấu hiệu xơ hóa tiểu động mạch võng mạc độ 2 do tăng huyết áp kéo dài.',
                    'Bệnh nhân có tăng huyết áp khởi phát lúc 38 tuổi, không phù mặt không phù chân, khám thần kinh '
                    'phản xạ gân xương bình thường, cơ lực tay chân hồi phục sau khi bù kali.',
                    'Thể trạng trung bình, huyết áp kháng trị dai dẳng với phác đồ chẹn canxi phối hợp ức chế men '
                    'chuyển và lợi tiểu, bụng mềm gan lách không to, ấn các điểm đau niệu quản âm tính.',
                    'Khám toàn diện hệ tim mạch mạch cảnh đập đều rõ, huyết áp 165/98 mmHg, nồng độ natri máu 144 '
                    'mmol/l ở giới hạn trên bình thường, không có dấu hiệu suy tim ứ huyết.'],
  'chan_doan': 'Hội chứng Conn cường aldosteron tiên phát do u vỏ thượng thận tăng tiết aldosteron.',
  'chinh': ['tăng huyết áp kháng trị dai dẳng khó kiểm soát dù đã phối hợp từ 3 loại thuốc hạ áp',
            'xét nghiệm hạ kali máu tự phát hoặc hạ kali máu nặng xuất hiện sau khi dùng thuốc lợi tiểu',
            'yếu cơ gốc chi mỏi cơ từng đợt kèm theo các cơn chuột rút co thắt cơ ban đêm'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Thực hiện xét nghiệm tỷ lệ nồng độ aldosterone huyết tương trên hoạt độ renin huyết tương (tỷ lệ ARR) '
              'sau khi đã chuẩn bị ngừng các thuốc hạ áp gây nhiễu trong 2-4 tuần, làm nghiệm pháp khẳng định tải muối '
              'truyền dung dịch natri clorid 0.9%, chụp cắt lớp vi tính CT tuyến thượng thận lớp mỏng 1-2mm khảo sát u '
              'tuyến vỏ thượng thận adenoma, chỉ định phẫu thuật nội soi cắt tuyến thượng thận một bên hoặc điều trị '
              'nội khoa bằng thuốc kháng thụ thể mineralocorticoid spironolactone 50-100mg/ngày.',
  'kham': 'Huyết áp đo tại phòng khám 168/102 mmHg cả hai tay dù đang dùng 3 nhóm thuốc hạ áp, thể trạng béo vừa không '
          'có kiểu hình Cushing, cơ lực tứ chi 4/5 giảm nhẹ gốc chi hai đùi, nhịp tim đều 74 ck/p không có tiếng thổi '
          'tim, khám mạch ngoại biên hai bên đập rõ không có tiếng thổi động mạch thận.',
  'nhom': 'người lớn',
  'phu': ['tiểu nhiều lần tiểu đêm nhiều do thận giảm khả năng cô đặc nước tiểu dưới tác động hạ kali',
          'tỷ lệ nồng độ aldosterone trên hoạt độ renin huyết tương (ARR) tăng rất cao',
          'hoàn toàn không có phù ngoại biên hai chân do hiện tượng thoát aldosteron sinh lý'],
  'ten': 'hội chứng Conn cường aldosteron tiên phát'},
 {'bien_the_chan_doan': ['Đái tháo nhạt do căn nguyên trung ương thiếu hụt hormone vasopressin ADH.',
                         'Theo dõi đái tháo nhạt do căn nguyên trung ương sau phẫu thuật can thiệp hố yên.',
                         'Đái tháo nhạt do căn nguyên trung ương vô căn tự miễn dịch.',
                         'Đái tháo nhạt do căn nguyên trung ương thể hoàn toàn lượng nước tiểu trên 8 lít/ngày.',
                         'Theo dõi đái tháo nhạt do căn nguyên trung ương sau chấn thương vỡ nền sọ.',
                         'Đái tháo nhạt do căn nguyên trung ương ổn định sau điều trị bổ sung desmopressin.'],
  'bien_the_ke_hoach': ['Thực hiện nghiệm pháp nhịn nước có giám sát chặt chẽ tại bệnh viện phối hợp tiêm thuốc tương '
                        'tự vasopressin (desmopressin) để chẩn đoán phân biệt với đái tháo nhạt do thận và chứng cuồng '
                        'uống tâm thần, chụp cộng hưởng từ MRI sọ não vùng tuyến yên cuống tuyến yên tìm tổn thương '
                        'mất tín hiệu sáng thùy sau trên T1, điều trị thay thế bằng chất đồng vận tổng hợp của hormone '
                        'chống bài niệu desmopressin (dDAVP) dạng xịt mũi hoặc viên uống tan trong miệng, theo dõi '
                        'natri máu định kỳ phòng ngừa hạ natri máu do ngộ độc nước.',
                        'Kê đơn desmopressin dạng viên nén uống 0.1mg ngày 2-3 lần, uống trước khi đi ngủ liều cao hơn '
                        'để đảm bảo giấc ngủ trọn vẹn không bị thức giấc đi tiểu đêm.',
                        'Hướng dẫn bệnh nhân chỉ uống nước khi thực sự có cảm giác khát sau khi đã dùng thuốc '
                        'desmopressin để phòng ngừa nguy cơ giữ nước thừa gây phù não và tụt natri máu nguy hiểm.',
                        'Lập bảng theo dõi lượng nước uống vào và lượng nước tiểu bài xuất ra mỗi 24 giờ tại nhà, cân '
                        'nặng hàng ngày vào cùng một thời điểm buổi sáng.',
                        'Chụp MRI tuyến yên có tiêm thuốc cản từ kiểm tra xem có viêm phễu cuống tuyến yên '
                        'hypophysitis hoặc u tế bào mầm thâm nhiễm vùng dưới đồi hay không.',
                        'Đo điện giải đồ định kỳ mỗi tuần trong tháng đầu điều trị để chỉnh liều desmopressin đạt hiệu '
                        'quả cô đặc nước tiểu tối ưu mà natri máu vẫn duy trì trong ngưỡng sinh lý.'],
  'bien_the_kham': ['Bệnh nhân tỉnh táo nhưng mệt mỏi, dấu hiệu mất nước nhẹ với niêm mạc lưỡi khô da kém đàn hồi, '
                    'mạch 88 ck/p, huyết áp 112/72 mmHg, tỷ trọng nước tiểu đo được 1.002 rất thấp (nước tiểu pha '
                    'loãng tối đa), nồng độ natri máu 143 mmol/l ở giới hạn bình thường cao, không có phù.',
                    'Bệnh nhân mang theo bình nước 2 lít uống liên tục trong lúc đợi khám, đo lượng nước tiểu 24 giờ '
                    'ghi nhận 6.5 lít, nước tiểu trong suốt như nước lọc, áp lực thẩm thấu niệu đo được 120 mOsm/kg.',
                    'Khám lâm sàng phát hiện dấu hiệu khát nước không kìm nén được, véo da bụng mất chậm nhẹ, các dấu '
                    'hiệu thần kinh sọ bình thường, soi đáy mắt không có phù gai thị.',
                    'Bệnh nhân có tiền sử phẫu thuật u tuyến yên qua đường xoang bướm cách 1 tháng, huyết áp tư thế '
                    'nằm 115/70 mmHg đứng 105/65 mmHg, nhịp tim đều 86 ck/p, glucose máu bình thường loại trừ đái tháo '
                    'đường.',
                    'Thể trạng gầy nhẹ, môi khô nứt nẻ nhẹ, xét nghiệm nước tiểu 10 thông số âm tính hoàn toàn với '
                    'đường protein và hồng cầu, nồng độ kali máu bình thường.',
                    'Khám tổng quát hô hấp tim mạch tiêu hóa bình thường, bệnh nhân than phiền mất ngủ kiệt sức vì ban '
                    'đêm phải thức dậy đi tiểu mỗi giờ một lần, áp lực thẩm thấu huyết tương tăng nhẹ 298 mOsm/kg.'],
  'chan_doan': 'Đái tháo nhạt do căn nguyên trung ương thiếu hụt hormone vasopressin ADH.',
  'chinh': ['tiểu nhiều số lượng lớn bất thường từ 4 đến 10 lít nước tiểu mỗi ngày',
            'nước tiểu rất trong nhạt màu như nước lã với áp lực thẩm thấu niệu giảm rất thấp',
            'uống nước liên tục cả ngày lẫn đêm do khát dữ dội đặc biệt rất thèm uống nước đá lạnh'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Thực hiện nghiệm pháp nhịn nước có giám sát chặt chẽ tại bệnh viện phối hợp tiêm thuốc tương tự '
              'vasopressin (desmopressin) để chẩn đoán phân biệt với đái tháo nhạt do thận và chứng cuồng uống tâm '
              'thần, chụp cộng hưởng từ MRI sọ não vùng tuyến yên cuống tuyến yên tìm tổn thương mất tín hiệu sáng '
              'thùy sau trên T1, điều trị thay thế bằng chất đồng vận tổng hợp của hormone chống bài niệu desmopressin '
              '(dDAVP) dạng xịt mũi hoặc viên uống tan trong miệng, theo dõi natri máu định kỳ phòng ngừa hạ natri máu '
              'do ngộ độc nước.',
  'kham': 'Bệnh nhân tỉnh táo nhưng mệt mỏi, dấu hiệu mất nước nhẹ với niêm mạc lưỡi khô da kém đàn hồi, mạch 88 ck/p, '
          'huyết áp 112/72 mmHg, tỷ trọng nước tiểu đo được 1.002 rất thấp (nước tiểu pha loãng tối đa), nồng độ natri '
          'máu 143 mmol/l ở giới hạn bình thường cao, không có phù.',
  'nhom': 'cả hai',
  'phu': ['thức giấc đi tiểu liên tục 4-6 lần mỗi đêm làm gián đoạn giấc ngủ gây suy nhược',
          'khô miệng khô da sụt cân nhẹ do mất nước qua đường tiểu không kịp bù',
          'tiền sử có chấn thương sọ não hoặc từng phẫu thuật can thiệp vùng tuyến yên hố yên'],
  'ten': 'đái tháo nhạt do căn nguyên trung ương'},
 {'bien_the_chan_doan': ['Tăng triglycerid máu nặng nguy cơ viêm tụy do rối loạn lipid máu hỗn hợp.',
                         'Theo dõi tăng triglycerid máu nặng nguy cơ viêm tụy có kèm u vàng phát ban ngoài da.',
                         'Tăng triglycerid máu nặng nguy cơ viêm tụy trên bệnh nhân đái tháo đường típ 2.',
                         'Tăng triglycerid máu nặng nguy cơ viêm tụy do lạm dụng rượu bia mạn tính.',
                         'Theo dõi tăng triglycerid máu nặng nguy cơ viêm tụy thể tăng chylomicron máu tiên phát.',
                         'Tăng triglycerid máu nặng nguy cơ viêm tụy đáp ứng ban đầu với phác đồ fibrate.'],
  'bien_the_ke_hoach': ['Chỉ định chế độ ăn giảm chất béo nghiêm ngặt xuống dưới 15% tổng năng lượng khẩu phần hàng '
                        'ngày, kiêng tuyệt đối rượu bia và nước ngọt bánh kẹo, dùng ngay thuốc hạ triglycerid nhóm '
                        'fibrate fenofibrate liều cao 200mg/ngày phối hợp acid béo omega-3 đậm đặc 2-4g/ngày, xét '
                        'nghiệm theo dõi nồng độ men tụy amylase lipase máu và triglycerid máu sau 48-72 giờ.',
                        'Hướng dẫn bệnh nhân nhận biết ngay dấu hiệu đau quặn bụng thượng vị lan ra sau lưng để nhập '
                        'viện cấp cứu lọc huyết tương thay huyết tương (plasmapheresis) kịp thời nếu triglycerid máu '
                        'vượt trên 20 mmol/l.',
                        'Khởi trị liệu trình fenofibrate 145mg/ngày uống cùng bữa ăn chính, phối hợp statin liều vừa '
                        'atorvastatin 20mg nếu có tăng cholesterol kèm theo sau khi triglycerid đã giảm về dưới 5.5 '
                        'mmol/l.',
                        'Kiểm soát tối ưu đường huyết bằng insulin nếu có đái tháo đường vì insulin kích thích men '
                        'lipoprotein lipase LPL làm tăng giáng hóa triglycerid nhanh chóng.',
                        'Tư vấn giảm cân bền vững, tập luyện thể dục nhịp điệu ít nhất 45 phút mỗi ngày, hạn chế tối '
                        'đa các loại tinh bột tinh chế đường đơn trong khẩu phần ăn.',
                        'Xét nghiệm lại bilan lipid máu toàn phần công thức máu chức năng gan men gan AST ALT sau 2 '
                        'tuần điều trị để đánh giá đáp ứng hạ lipid máu.'],
  'bien_the_kham': ['Bệnh nhân thể trạng béo phì trung tâm BMI 28.5 kg/m2, bụng mềm không đau thượng vị không có phản '
                    'ứng thành bụng, khám da vùng lưng mông và mặt duỗi hai cẳng tay có rải rác các nốt sẩn nhỏ màu '
                    'vàng cam kích thước 2-4mm nền ban đỏ nhẹ (u vàng phát ban eruptive xanthomas), gan to dưới bờ '
                    'sườn 2cm mật độ mềm nhẵn.',
                    'Bệnh nhân không sốt không đau bụng, khám mắt bằng đèn soi đáy mắt thấy các mạch máu võng mạc có '
                    'màu hồng nhạt như sữa (dấu hiệu lipidemia retinalis), huyết thanh trong ống máu ly tâm đục ngầu '
                    'như sữa chua.',
                    'Khám thực thể ghi nhận nhiều nốt u vàng phát ban ở mặt duỗi cẳng tay và đầu gối, bụng chướng nhẹ '
                    'ấn thượng vị tức nhẹ nhưng không đề kháng, huyết áp 145/90 mmHg.',
                    'Bệnh nhân đi kiểm tra sức khỏe định kỳ phát hiện kết quả triglycerid máu 14.2 mmol/l, niêm mạc '
                    'hồng hào, tim phổi bình thường, siêu âm ổ bụng phát hiện gan nhiễm mỡ độ 3.',
                    'Khám da phát hiện các đám sẩn mỡ màu vàng kích thước hạt đậu xanh ở vùng mông, bụng mềm không có '
                    'điểm đau khu trú, không có dấu hiệu viêm tụy khởi phát tại thời điểm khám.',
                    'Thể trạng thừa cân, gan to nhẹ mép tù bờ nhẵn không đau, lách không to, nhịp tim đều 82 ck/p, xét '
                    'nghiệm đường huyết đói kèm theo tăng nhẹ 7.8 mmol/l.'],
  'chan_doan': 'Tăng triglycerid máu nặng nguy cơ viêm tụy do rối loạn lipid máu hỗn hợp.',
  'chinh': ['xét nghiệm nồng độ triglycerid huyết thanh tăng rất nặng vượt trên 10 mmol/l (hoặc trên 1000 mg/dl)',
            'huyết thanh lấy ra có màu đục như sữa do tích tụ quá nhiều hạt chylomicron',
            'nguy cơ rất cao bùng phát đợt tổn thương viêm tụy do lắng đọng acid béo tự do'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Chỉ định chế độ ăn giảm chất béo nghiêm ngặt xuống dưới 15% tổng năng lượng khẩu phần hàng ngày, kiêng '
              'tuyệt đối rượu bia và nước ngọt bánh kẹo, dùng ngay thuốc hạ triglycerid nhóm fibrate fenofibrate liều '
              'cao 200mg/ngày phối hợp acid béo omega-3 đậm đặc 2-4g/ngày, xét nghiệm theo dõi nồng độ men tụy amylase '
              'lipase máu và triglycerid máu sau 48-72 giờ.',
  'kham': 'Bệnh nhân thể trạng béo phì trung tâm BMI 28.5 kg/m2, bụng mềm không đau thượng vị không có phản ứng thành '
          'bụng, khám da vùng lưng mông và mặt duỗi hai cẳng tay có rải rác các nốt sẩn nhỏ màu vàng cam kích thước '
          '2-4mm nền ban đỏ nhẹ (u vàng phát ban eruptive xanthomas), gan to dưới bờ sườn 2cm mật độ mềm nhẵn.',
  'nhom': 'người lớn',
  'phu': ['xuất hiện các nốt sẩn u vàng phát ban màu vàng cam trên da vùng lưng mông cánh tay',
          'hình ảnh váng mỡ võng mạc (lipidemia retinalis) khi soi kiểm tra đáy mắt',
          'tiền sử thường xuyên uống nhiều rượu bia ăn nhiều chất béo ngọt hoặc đái tháo đường đi kèm'],
  'ten': 'tăng triglycerid máu nặng nguy cơ viêm tụy'},
 {'bien_the_chan_doan': ['Bệnh nhiễm sắc tố sắt hemochromatosis di truyền đột biến gen HFE.',
                         'Theo dõi bệnh nhiễm sắc tố sắt hemochromatosis có biến chứng xơ gan còn bù.',
                         'Bệnh nhiễm sắc tố sắt hemochromatosis thể phối hợp tổn thương khớp và đái tháo đường.',
                         'Bệnh nhiễm sắc tố sắt hemochromatosis mức độ quá tải sắt mô nặng.',
                         'Theo dõi bệnh nhiễm sắc tố sắt hemochromatosis giai đoạn tấn công bằng trích máu.',
                         'Bệnh nhiễm sắc tố sắt hemochromatosis ổn định nồng độ ferritin mục tiêu.'],
  'bien_the_ke_hoach': ['Chỉ định xét nghiệm di truyền xác định đột biến gen HFE (đột biến C282Y và H63D), chụp cộng '
                        'hưởng từ MRI gan định lượng nồng độ sắt mô gan theo thang T2*, điều trị bằng phương pháp '
                        'trích máu tĩnh mạch định kỳ (phlebotomy) rút 500ml máu mỗi 1-2 tuần cho đến khi ferritin '
                        'huyết thanh giảm về dưới 50-100 ng/ml sau đó trích máu duy trì, kiêng các thực phẩm giàu sắt '
                        'và không uống viên bổ sung sắt hay vitamin C.',
                        'Lên kế hoạch trích máu tĩnh mạch mỗi tuần rút 450-500ml theo dõi chỉ số huyết sắc tố '
                        'hemoglobin duy trì trên 110 g/l trước mỗi lần trích máu, kiểm tra ferritin máu hàng tháng.',
                        'Chỉ định thuốc gắp sắt thải sắt deferasirox hoặc deferoxamine nếu bệnh nhân có thiếu máu hoặc '
                        'suy tim nặng không thể dung nạp phương pháp trích máu tĩnh mạch.',
                        'Tư vấn chế độ ăn tránh ăn thịt đỏ nội tạng động vật tiết canh hải sản sống, kiêng tuyệt đối '
                        'rượu bia để bảo vệ tế bào gan khỏi tổn thương cộng hưởng xơ gan.',
                        'Tầm soát ung thư biểu mô tế bào gan HCC định kỳ bằng siêu âm gan và xét nghiệm AFP mỗi 6 '
                        'tháng ở bệnh nhân đã có biến chứng xơ gan do ứ sắt.',
                        'Khuyên các anh chị em ruột và con cái ruột của bệnh nhân thực hiện xét nghiệm gen HFE và '
                        'bilan sắt huyết thanh để phát hiện bệnh sớm ở giai đoạn tiền triệu chứng.'],
  'bien_the_kham': ['Da toàn thân có màu sạm đồng ánh kim loại rõ ở vùng mặt mu bàn tay và nếp gấp nách, gan to chắc '
                    'dưới bờ sườn phải 3cm không đau, khám các khớp bàn ngón tay 2 và 3 hai bên sưng nhẹ cứng khớp '
                    'buổi sáng, nhịp tim đều 72 ck/p, huyết áp 120/75 mmHg.',
                    'Bệnh nhân có màu da nâu đồng sẫm đặc biệt như vừa tắm nắng lâu ngày, bờ gan sờ chắc cách bờ sườn '
                    '3.5cm, lách to độ 1, khám tim có tiếng T3 nhẹ ở mỏm tim, không có phù ngoại biên chân.',
                    'Khám lâm sàng phát hiện sạm da lan tỏa kèm theo đái tháo đường mới chẩn đoán (hội chứng đái tháo '
                    'đường đồng đen), khớp bàn ngón tay hai bên biến dạng nhẹ hạn chế nắm chặt bàn tay.',
                    'Thể trạng trung bình, niêm mạc mắt không vàng, khám bụng gan to bờ sắc chắc nịch, nồng độ '
                    'ferritin máu xét nghiệm đạt 1650 ng/ml với độ bão hòa transferrin 78%.',
                    'Da vùng cẳng tay và cổ có màu xám chì ánh đồng, các khớp ngón tay sờ dày bao khớp không nóng đỏ, '
                    'tim đều tiếng T1 T2 rõ, cơ lực tứ chi bình thường.',
                    'Khám phát hiện tam chứng kinh điển xơ gan sạm da đồng và đái tháo đường, gan to chắc lách to nhẹ, '
                    'lông tóc trên cơ thể thưa thớt khô rụng.'],
  'chan_doan': 'Bệnh nhiễm sắc tố sắt hemochromatosis di truyền đột biến gen HFE.',
  'chinh': ['da sạm màu đồng ánh xám đặc trưng rõ ở các vùng da hở và nếp gấp cơ thể',
            'xét nghiệm độ bão hòa transferrin tăng trên 50% và nồng độ ferritin huyết thanh tăng rất cao',
            'gan to chắc kèm theo suy giảm chức năng gan tiến triển dần đến xơ gan'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Chỉ định xét nghiệm di truyền xác định đột biến gen HFE (đột biến C282Y và H63D), chụp cộng hưởng từ '
              'MRI gan định lượng nồng độ sắt mô gan theo thang T2*, điều trị bằng phương pháp trích máu tĩnh mạch '
              'định kỳ (phlebotomy) rút 500ml máu mỗi 1-2 tuần cho đến khi ferritin huyết thanh giảm về dưới 50-100 '
              'ng/ml sau đó trích máu duy trì, kiêng các thực phẩm giàu sắt và không uống viên bổ sung sắt hay vitamin '
              'C.',
  'kham': 'Da toàn thân có màu sạm đồng ánh kim loại rõ ở vùng mặt mu bàn tay và nếp gấp nách, gan to chắc dưới bờ '
          'sườn phải 3cm không đau, khám các khớp bàn ngón tay 2 và 3 hai bên sưng nhẹ cứng khớp buổi sáng, nhịp tim '
          'đều 72 ck/p, huyết áp 120/75 mmHg.',
  'nhom': 'người lớn',
  'phu': ['đau nhức các khớp bàn ngón tay đặc biệt là khớp bàn ngón 2 và ngón 3',
          'xuất hiện đái tháo đường khởi phát muộn do ứ đọng sắt hủy hoại tế bào beta tụy',
          'suy giảm chức năng tuyến sinh dục và rối loạn nhịp tim suy tim do ứ sắt cơ tim'],
  'ten': 'bệnh nhiễm sắc tố sắt hemochromatosis'},
 {'bien_the_chan_doan': ['Bệnh Wilson lắng đọng đồng thể phối hợp tổn thương gan và thần kinh.',
                         'Theo dõi bệnh Wilson lắng đọng đồng thể thần kinh tâm thần ưu thế.',
                         'Bệnh Wilson lắng đọng đồng thể gan mạn tính có xơ gan lách to.',
                         'Bệnh Wilson lắng đọng đồng có vòng Kayser-Fleischer giác mạc điển hình.',
                         'Theo dõi bệnh Wilson lắng đọng đồng ở lứa tuổi thanh thiếu niên có run tay.',
                         'Bệnh Wilson lắng đọng đồng giai đoạn điều trị duy trì ổn định bằng kẽm.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ ceruloplasmin huyết thanh, định lượng bài tiết đồng trong nước tiểu thu '
                        'thập 24 giờ, xét nghiệm gen đột biến ATP7B, chỉ định điều trị suốt đời bằng thuốc thải đồng '
                        'gắp đồng D-penicillamine hoặc trientine dihydrochloride phối hợp kẽm acetate đường uống ngăn '
                        'hấp thu đồng qua đường ruột, tư vấn chế độ ăn kiêng thức ăn chứa nhiều đồng như phủ tạng nấm '
                        'sô cô la hạt điều tôm cua sáp ong.',
                        'Bắt đầu điều trị D-penicillamine 250mg/ngày tăng dần liều mỗi tuần đến 1000-1500mg/ngày chia '
                        '2-4 lần uống lúc bụng đói, phối hợp bổ sung vitamin B6 pyridoxine 25-50mg/ngày.',
                        'Theo dõi sát công thức máu và tổng phân tích nước tiểu hàng tuần trong tháng đầu điều trị '
                        'D-penicillamine phát hiện tác dụng phụ giảm bạch cầu giảm tiểu cầu hoặc protein niệu.',
                        'Chuyển sang dùng viên kẽm acetate 50mg ngày 3 lần uống cách xa bữa ăn khi các triệu chứng '
                        'thần kinh và nồng độ đồng tự do máu đã kiểm soát ổn định sau 1-2 năm.',
                        'Chụp cộng hưởng từ MRI sọ não khảo sát tổn thương tăng tín hiệu trên T2 ở nhân bèo nhân đuôi '
                        'đồi thị và dấu hiệu mặt gấu trúc (giant panda sign) ở trung não.',
                        'Tầm soát bệnh Wilson cho tất cả anh chị em ruột của người bệnh bằng khám mắt đèn khe và xét '
                        'nghiệm ceruloplasmin đồng niệu để can thiệp điều trị sớm trước khi có tổn thương không hồi '
                        'phục.'],
  'bien_the_kham': ['Khám mắt bằng đèn khe sinh hiển vi thấy vòng sắc tố Kayser-Fleischer màu xanh nâu vàng đồng lắng '
                    'đọng ở màng Descemet rìa giác mạc hai mắt, khám thần kinh phát hiện run hai bàn tay dạng đập cánh '
                    'chim khi giơ ngang tay, tăng trương lực cơ ngoại tháp kiểu bánh xe răng cưa, gan to 2cm dưới sườn '
                    'phải chắc mềm.',
                    'Bệnh nhân có dáng đi cứng nhắc chậm chạp, giọng nói phát âm khó nghẹn, cơ mặt ít biểu cảm (khuôn '
                    'mặt vô cảm mặt nạ), sờ thấy lách to độ 2 qua bờ sườn, củng mạc mắt ánh vàng nhẹ.',
                    'Khám mắt phát hiện vòng viền nâu đồng quanh giác mạc rõ hai bên, run biên độ lớn ở ngọn chi tăng '
                    'khi chú ý làm việc, tăng phản xạ gân xương, khám gan thấy bờ gan mấp mô nhẹ.',
                    'Bệnh nhân có biểu hiện rối loạn ngoại tháp với nuốt khó nói lắp, khám vận nhãn bình thường, xét '
                    'nghiệm ceruloplasmin máu giảm sâu còn 8 mg/dl (ngưỡng bình thường 20-40 mg/dl).',
                    'Khám thực thể phát hiện hội chứng suy tế bào gan nhẹ lòng bàn tay son, lách to chạm tay, trương '
                    'lực cơ chi trên tăng đều, nghiệm pháp ngón tay chỉ mũi run quá tầm nhẹ.',
                    'Bệnh nhân có nét mặt cười co cứng không tự nhiên, rung giật cơ tay khi giơ thẳng ra trước, soi '
                    'mắt có vòng Kayser-Fleischer điển hình, lượng đồng niệu 24 giờ đạt 220 mcg/ngày.'],
  'chan_doan': 'Bệnh Wilson lắng đọng đồng thể phối hợp tổn thương gan và thần kinh.',
  'chinh': ['vòng sắc tố Kayser-Fleischer màu nâu vàng đồng ở rìa giác mạc khi khám mắt',
            'nồng độ ceruloplasmin huyết thanh giảm thấp và bài tiết đồng trong nước tiểu 24 giờ tăng rất cao',
            'các triệu chứng thần kinh tiến triển: run vô căn rối loạn trương lực cơ đi lại cứng nhắc'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Định lượng nồng độ ceruloplasmin huyết thanh, định lượng bài tiết đồng trong nước tiểu thu thập 24 giờ, '
              'xét nghiệm gen đột biến ATP7B, chỉ định điều trị suốt đời bằng thuốc thải đồng gắp đồng D-penicillamine '
              'hoặc trientine dihydrochloride phối hợp kẽm acetate đường uống ngăn hấp thu đồng qua đường ruột, tư vấn '
              'chế độ ăn kiêng thức ăn chứa nhiều đồng như phủ tạng nấm sô cô la hạt điều tôm cua sáp ong.',
  'kham': 'Khám mắt bằng đèn khe sinh hiển vi thấy vòng sắc tố Kayser-Fleischer màu xanh nâu vàng đồng lắng đọng ở '
          'màng Descemet rìa giác mạc hai mắt, khám thần kinh phát hiện run hai bàn tay dạng đập cánh chim khi giơ '
          'ngang tay, tăng trương lực cơ ngoại tháp kiểu bánh xe răng cưa, gan to 2cm dưới sườn phải chắc mềm.',
  'nhom': 'cả hai',
  'phu': ['vẻ mặt đờ đẫn nụ cười co cứng khó khăn khi nói ngọng và khó nuốt',
          'rối loạn chức năng gan mạn tính gan to lách to vàng mắt nhẹ',
          'thay đổi tính tình cảm xúc thất thường sa sút khả năng học tập ở người trẻ tuổi'],
  'ten': 'bệnh Wilson lắng đọng đồng'},
 {'bien_the_chan_doan': ['Loãng xương vô căn ở nam giới mức độ nặng có giảm chiều cao cơ thể.',
                         'Theo dõi loãng xương vô căn ở nam giới biến chứng lún xẹp đốt sống thắt lưng cũ.',
                         'Loãng xương vô căn ở nam giới nguy cơ cao gãy xương tái phát.',
                         'Loãng xương vô căn ở nam giới chưa có biến chứng gãy xương lớn.',
                         'Theo dõi loãng xương vô căn ở nam giới thể mất chất khoáng xương vỏ sớm.',
                         'Loãng xương vô căn ở nam giới giai đoạn điều trị thuốc ức chế hủy xương.'],
  'bien_the_ke_hoach': ['Chụp X-quang cột sống thắt lưng thẳng nghiêng đánh giá tình trạng lún xẹp các thân đốt sống, '
                        'làm bilan xét nghiệm loại trừ loãng xương thứ phát gồm canxi máu vitamin D hormone giáp TSH '
                        'testosterone toàn phần và điện di protein huyết thanh loại trừ đa u tủy xương, chỉ định dùng '
                        'thuốc chống hủy xương nhóm bisphosphonate axit zoledronic 5mg truyền tĩnh mạch hàng năm hoặc '
                        'alendronate 70mg uống tuần 1 lần kết hợp bổ sung canxi và vitamin D.',
                        'Kê đơn alendronate 70mg uống vào một buổi sáng cố định trong tuần với một cốc nước lọc đầy '
                        'khi vừa thức dậy, giữ tư thế đứng hoặc ngồi thẳng lưng ít nhất 30 phút sau uống phòng viêm '
                        'loét thực quản.',
                        'Bổ sung canxi nguyên tố 1000mg/ngày chia làm 2 lần sau ăn kết hợp vitamin D3 1000-2000 '
                        'IU/ngày để đảm bảo đủ nguyên liệu khoáng hóa xương trong suốt quá trình điều trị.',
                        'Tư vấn kiêng bỏ thuốc lá hạn chế uống rượu bia, hướng dẫn bài tập thể dục có tải trọng nhẹ '
                        'như đi bộ nhanh tập tạ tay nhẹ nhàng giúp kích thích tế bào tạo xương osteoblast.',
                        'Đo nồng độ 25-OH-vitamin D huyết thanh đảm bảo nồng độ trên 30 ng/ml trước khi truyền tĩnh '
                        'mạch axit zoledronic để phòng ngừa phản ứng hạ canxi máu cấp tính.',
                        'Hẹn đo lại mật độ xương bằng phương pháp DEXA sau 1-2 năm tại cùng một cơ sở và trên cùng một '
                        'máy đo để đánh giá đáp ứng phục hồi mật độ xương.'],
  'bien_the_kham': ['Bệnh nhân có gù nhẹ cột sống ngực, chiều cao đo được giảm 3.5cm so với thời điểm thanh niên, ấn '
                    'dọc các gai sau đốt sống thắt lưng có điểm đau tức ê ẩm nhẹ, cơ lực chi dưới bình thường, không '
                    'có dấu hiệu chèn ép rễ tủy thần kinh, chỉ số T-score đo bằng DEXA tại cổ xương đùi là -2.8.',
                    'Bệnh nhân nam 54 tuổi thể trạng gầy, bước đi cẩn trọng, cột sống thắt lưng giảm độ ưỡn sinh lý, '
                    'ấn các gai đốt sống L1-L3 đau thốn nhẹ do lún xẹp vi thể mạn tính, các khớp ngoại biên bình '
                    'thường.',
                    'Khám phát hiện biến dạng gù lưng rõ khoảng cách chẩm - tường tăng 4cm, đo chiều cao giảm 4cm so '
                    'với trước đây, không có teo cơ tứ chi, nghiệm pháp nâng chân thẳng Lasegue âm tính.',
                    'Thể trạng bình thường không có kiểu hình suy tuyến sinh dục, lông râu phân bố nam tính, ấn khớp '
                    'háng hai bên không đau, chỉ số khối cơ thể BMI 19.5 kg/m2, kết quả T-score cột sống -3.1.',
                    'Khám lâm sàng vận động cột sống hạn chế ở động tác cúi gập thân, các khối cơ cạnh sống thắt lưng '
                    'co thắt nhẹ, không có điểm đau nhức tại các xương dài tay chân.',
                    'Bệnh nhân than đau lưng âm ỉ tăng khi ngồi lâu hoặc đứng lâu, gõ nhẹ dọc cột sống có cảm giác tức '
                    'ê, đo DEXA tại ba vị trí đều có T-score dưới ngưỡng -2.5, tim phổi khám bình thường.'],
  'chan_doan': 'Loãng xương vô căn ở nam giới mức độ nặng có giảm chiều cao cơ thể.',
  'chinh': ['đo mật độ khoáng chất xương DEXA có chỉ số T-score tại cột sống hoặc cổ xương đùi dưới -2.5',
            'tiền sử gãy xương tự nhiên hoặc gãy xương sau chấn thương nhẹ không đáng kể',
            'đau mỏi âm ỉ dọc cột sống thắt lưng kèm theo giảm chiều cao cơ thể trên 3cm'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'nội tiết - chuyển hoá',
  'ke_hoach': 'Chụp X-quang cột sống thắt lưng thẳng nghiêng đánh giá tình trạng lún xẹp các thân đốt sống, làm bilan '
              'xét nghiệm loại trừ loãng xương thứ phát gồm canxi máu vitamin D hormone giáp TSH testosterone toàn '
              'phần và điện di protein huyết thanh loại trừ đa u tủy xương, chỉ định dùng thuốc chống hủy xương nhóm '
              'bisphosphonate axit zoledronic 5mg truyền tĩnh mạch hàng năm hoặc alendronate 70mg uống tuần 1 lần kết '
              'hợp bổ sung canxi và vitamin D.',
  'kham': 'Bệnh nhân có gù nhẹ cột sống ngực, chiều cao đo được giảm 3.5cm so với thời điểm thanh niên, ấn dọc các gai '
          'sau đốt sống thắt lưng có điểm đau tức ê ẩm nhẹ, cơ lực chi dưới bình thường, không có dấu hiệu chèn ép rễ '
          'tủy thần kinh, chỉ số T-score đo bằng DEXA tại cổ xương đùi là -2.8.',
  'nhom': 'người lớn',
  'phu': ['dáng đi khom lưng gù cột sống đoạn ngực tăng dần theo thời gian',
          'nam giới lứa tuổi trung niên hoặc lớn tuổi không tìm thấy nguyên nhân thứ phát gây loãng xương',
          'hạn chế biên độ vận động cúi ngửa xoay người do co cứng khối cơ cạnh sống'],
  'ten': 'loãng xương vô căn ở nam giới'},
 {'bien_the_chan_doan': ['Thiếu vitamin D ở người trưởng thành mức độ trung bình có yếu cơ gốc chi.',
                         'Theo dõi thiếu vitamin D ở người trưởng thành mức độ nặng nồng độ dưới 10 ng/ml.',
                         'Thiếu vitamin D ở người trưởng thành có cường cận giáp thứ phát phản ứng.',
                         'Thiếu vitamin D ở người trưởng thành thể đau nhuyễn xương mạn tính.',
                         'Theo dõi thiếu vitamin D ở người trưởng thành do ít tiếp xúc ánh nắng mặt trời.',
                         'Thiếu vitamin D ở người trưởng thành giai đoạn bắt đầu bù liều tấn công.'],
  'bien_the_ke_hoach': ['Chỉ định điều trị tấn công bằng vitamin D3 (cholecalciferol) liều cao 50.000 IU mỗi tuần một '
                        'lần trong 8 tuần liên tục, sau đó chuyển sang liều duy trì 1.000-2.000 IU mỗi ngày, bổ sung '
                        'canxi nguyên tố đường uống 1.000mg/ngày, tư vấn tắm nắng mặt trời vào buổi sáng sớm khoảng '
                        '15-20 phút mỗi ngày để da tổng hợp vitamin D tự nhiên, hẹn xét nghiệm lại 25(OH)D sau 3 '
                        'tháng.',
                        'Kê đơn viên nang cholecalciferol 50.000 IU uống mỗi sáng chủ nhật sau bữa ăn có chất béo để '
                        'tối ưu hóa sự hấp thu qua đường tiêu hóa, uống liên tục 8 tuần.',
                        'Hướng dẫn chế độ ăn tăng cường các loại cá béo như cá thu cá hồi cá trích, lòng đỏ trứng gà, '
                        'nấm và sữa tăng cường vi chất dinh dưỡng.',
                        'Xét nghiệm định lượng lại nồng độ canxi máu canxi niệu 24 giờ và 25(OH)D huyết thanh sau liệu '
                        'trình tấn công để chỉnh liều duy trì phòng ngừa ngộ độc vitamin D.',
                        'Tư vấn phơi nắng cánh tay và cẳng chân từ 9 giờ đến 10 giờ sáng hoặc 15 giờ đến 16 giờ chiều '
                        'không dùng kem chống nắng trong khoảng 15 phút.',
                        'Đo mật độ xương DEXA tầm soát loãng xương phối hợp ở người trưởng thành thiếu vitamin D kéo '
                        'dài, hẹn tái khám định kỳ theo dõi triệu chứng đau mỏi cơ xương.'],
  'bien_the_kham': ['Ấn dọc bờ trước xương chày hai bên và xương ức bệnh nhân có cảm giác đau tức sâu ê ẩm trong màng '
                    'xương, cơ lực gốc chi hai đùi đạt 4/5 khi thực hiện nghiệm pháp đứng lên từ ghế bệnh nhân phải '
                    'dùng hai tay chống gối, dáng đi lạch bạch nhẹ, biên độ vận động thụ động các khớp bình thường '
                    'không sưng nóng.',
                    'Bệnh nhân than đau ê ẩm khắp mình mẩy xương chậu và thắt lưng, ấn điểm xương chậu hai bên tức rõ, '
                    'sức cơ đai vai và đai hông giảm nhẹ, không có teo cơ cục bộ, nồng độ 25-OH-D máu là 12 ng/ml.',
                    'Khám thực thể không thấy biến dạng khớp, phản xạ gân xương bình thường, bệnh nhân leo bậc thang '
                    'khó khăn do yếu cơ tứ đầu đùi, xét nghiệm canxi máu ở ngưỡng thấp 2.1 mmol/l kèm nồng độ PTH tăng '
                    'phản ứng.',
                    'Bệnh nhân có nước da xanh tái do làm việc văn phòng không ra ngoài trời, ấn xương sườn và xương '
                    'chày đau thốn mơ hồ, khám các dây thần kinh sọ bình thường, huyết áp 115/75 mmHg.',
                    'Thể trạng bình thường, khám cơ lực chi dưới cho thấy bệnh nhân gặp khó khăn khi ngồi xổm đứng '
                    'dậy, không có dấu hiệu viêm khớp dạng thấp, nghiệm pháp Trousseau âm tính.',
                    'Khám toàn diện hệ cơ xương khớp ghi nhận hội chứng nhuyễn xương nhẹ do thiếu vitamin D, đau xương '
                    'lan tỏa khi thay đổi thời tiết, nghe tim phổi bình thường nhịp tim 70 ck/p.'],
  'chan_doan': 'Thiếu vitamin D ở người trưởng thành mức độ trung bình có yếu cơ gốc chi.',
  'chinh': ['nồng độ 25-hydroxyvitamin D [25(OH)D] trong huyết thanh xét nghiệm dưới 20 ng/ml (dưới 50 nmol/l)',
            'đau nhức âm ỉ sâu trong xương đặc biệt là vùng xương chậu khớp háng và hai cẳng chân',
            'yếu cơ gốc chi làm khó khăn khi leo cầu thang hoặc khi tự đứng lên từ ghế thấp'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'dinh dưỡng',
  'ke_hoach': 'Chỉ định điều trị tấn công bằng vitamin D3 (cholecalciferol) liều cao 50.000 IU mỗi tuần một lần trong '
              '8 tuần liên tục, sau đó chuyển sang liều duy trì 1.000-2.000 IU mỗi ngày, bổ sung canxi nguyên tố đường '
              'uống 1.000mg/ngày, tư vấn tắm nắng mặt trời vào buổi sáng sớm khoảng 15-20 phút mỗi ngày để da tổng hợp '
              'vitamin D tự nhiên, hẹn xét nghiệm lại 25(OH)D sau 3 tháng.',
  'kham': 'Ấn dọc bờ trước xương chày hai bên và xương ức bệnh nhân có cảm giác đau tức sâu ê ẩm trong màng xương, cơ '
          'lực gốc chi hai đùi đạt 4/5 khi thực hiện nghiệm pháp đứng lên từ ghế bệnh nhân phải dùng hai tay chống '
          'gối, dáng đi lạch bạch nhẹ, biên độ vận động thụ động các khớp bình thường không sưng nóng.',
  'nhom': 'người lớn',
  'phu': ['thường xuyên làm việc trong phòng kín ít tiếp xúc với ánh sáng mặt trời tự nhiên',
          'cảm giác mệt mỏi uể oải toàn thân dễ cáu gắt và thỉnh thoảng hay bị chuột rút cơ bắp',
          'chế độ ăn thiếu các thực phẩm giàu vitamin D tự nhiên như cá béo sữa và trứng'],
  'ten': 'thiếu vitamin D ở người trưởng thành'},
 {'bien_the_chan_doan': ['Thiếu kẽm dinh dưỡng mạn tính mức độ trung bình có tổn thương da niêm mạc.',
                         'Theo dõi thiếu kẽm dinh dưỡng mạn tính thể viêm da quanh hốc tự nhiên và rụng tóc.',
                         'Thiếu kẽm dinh dưỡng mạn tính kèm theo rối loạn vị giác và chán ăn.',
                         'Thiếu kẽm dinh dưỡng mạn tính do chế độ ăn thuần chay thiếu vi chất.',
                         'Theo dõi thiếu kẽm dinh dưỡng mạn tính sau phẫu thuật cắt đoạn ruột hấp thu kém.',
                         'Thiếu kẽm dinh dưỡng mạn tính giai đoạn hồi phục sau bổ sung kẽm đường uống.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ kẽm huyết thanh lúc đói buổi sáng, chỉ định bổ sung kẽm nguyên tố đường '
                        'uống liều 20-40mg kẽm/ngày (tương đương kẽm gluconate hoặc kẽm sulfate) uống trước bữa ăn 1 '
                        'giờ hoặc sau ăn 2 giờ liên tục trong 2-3 tháng, tư vấn dinh dưỡng tăng cường thực phẩm giàu '
                        'kẽm sinh học cao như hàu thịt bò thịt gia cầm ngũ cốc nguyên hạt các loại đậu.',
                        'Kê đơn viên kẽm gluconate 70mg (chứa 10mg kẽm nguyên tố) uống 2 viên mỗi ngày sau bữa ăn trưa '
                        'để hạn chế kích ứng dạ dày gây nôn nao khó chịu.',
                        'Tư vấn giảm bớt các thực phẩm chứa nhiều chất phytate như cám gạo chưa tinh chế vì phytate '
                        'tạo phức hợp không tan cản trở ruột hấp thu kẽm.',
                        'Không uống viên bổ sung kẽm cùng thời điểm với viên sắt hoặc canxi vì các ion kim loại hóa '
                        'trị 2 cạnh tranh hấp thu qua kênh vận chuyển tại ruột non.',
                        'Theo dõi sự cải thiện của vị giác và tình trạng lành tổn thương da sau 2-4 tuần bù kẽm, kiểm '
                        'tra nồng độ kẽm huyết thanh sau 2 tháng điều trị.',
                        'Bổ sung đa vi chất vitamin A vitamin C phối hợp giúp tăng cường tái tạo biểu mô và kích thích '
                        'hệ miễn dịch tế bào phục hồi.'],
  'bien_the_kham': ['Tóc thưa rụng nhiều vuốt nhẹ rụng từng búi sợi tóc khô mất bóng, da quanh khóe mép hai bên và '
                    'cánh mũi có các mảng ban đỏ trợt nông tróc vảy khô, móng tay xuất hiện nhiều dải trắng ngang (dấu '
                    'hiệu vệt Beau-Reil), niêm mạc lưỡi nhẵn gai nhẹ, nồng độ kẽm huyết thanh xét nghiệm giảm dưới '
                    '10.5 umol/l.',
                    'Bệnh nhân có tổn thương viêm da quanh hốc tự nhiên điển hình, da mặt khô nứt nẻ, tóc rụng thưa lộ '
                    'rõ da đầu, các vết xước ở tay 2 tuần chưa liền miệng, không sốt.',
                    'Khám thấy móng tay giòn gồ ghề có chấm trắng và dải vệt trắng ngang trên bản móng (leukonychia), '
                    'lưỡi mất gai viền đỏ nhẹ, bệnh nhân than mất cảm nhận vị mặn ngọt khi ăn.',
                    'Tổn thương da dạng vảy nến nhẹ ở quanh khóe miệng và vùng hậu môn sinh dục, không ngứa nhiều, xét '
                    'nghiệm soi tươi không có nấm, da khô ráp toàn thân.',
                    'Khám lâm sàng ghi nhận tình trạng suy dinh dưỡng vi chất, tóc dễ nhổ không đau, cơ thể gầy sút '
                    'cân nhẹ do ăn uống kém, bụng mềm nhu động ruột tăng nhẹ.',
                    'Bệnh nhân có nhiều vết trợt khô ở mép môi, da vùng khớp khuỷu và gối dày sừng nang lông, nồng độ '
                    'kẽm trong huyết tương đo được 8.2 umol/l (ngưỡng bình thường 11-18 umol/l).'],
  'chan_doan': 'Thiếu kẽm dinh dưỡng mạn tính mức độ trung bình có tổn thương da niêm mạc.',
  'chinh': ['rụng tóc lan tỏa nhiều sợi tóc khô xơ chẻ ngọn dễ gãy rụng khi chải đầu',
            'tổn thương viêm da đỏ trợt tróc vảy khô quanh các hốc tự nhiên quanh miệng mũi và hậu môn',
            'móng tay mọc chậm có nhiều khía rãnh ngang và các dải vệt ngang màu trắng đục'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'dinh dưỡng',
  'ke_hoach': 'Định lượng nồng độ kẽm huyết thanh lúc đói buổi sáng, chỉ định bổ sung kẽm nguyên tố đường uống liều '
              '20-40mg kẽm/ngày (tương đương kẽm gluconate hoặc kẽm sulfate) uống trước bữa ăn 1 giờ hoặc sau ăn 2 giờ '
              'liên tục trong 2-3 tháng, tư vấn dinh dưỡng tăng cường thực phẩm giàu kẽm sinh học cao như hàu thịt bò '
              'thịt gia cầm ngũ cốc nguyên hạt các loại đậu.',
  'kham': 'Tóc thưa rụng nhiều vuốt nhẹ rụng từng búi sợi tóc khô mất bóng, da quanh khóe mép hai bên và cánh mũi có '
          'các mảng ban đỏ trợt nông tróc vảy khô, móng tay xuất hiện nhiều dải trắng ngang (dấu hiệu vệt Beau-Reil), '
          'niêm mạc lưỡi nhẵn gai nhẹ, nồng độ kẽm huyết thanh xét nghiệm giảm dưới 10.5 umol/l.',
  'nhom': 'cả hai',
  'phu': ['giảm vị giác ăn uống không có cảm giác ngon miệng mất cảm giác thèm ăn',
          'các vết thương xây xước ngoài da rất lâu lành và dễ bị nhiễm trùng mưng mủ tái phát',
          'thường xuyên có các đợt tiêu chảy phân sống lỏng sệt tái diễn không rõ nguyên nhân'],
  'ten': 'thiếu kẽm dinh dưỡng mạn tính'},
 {'bien_the_chan_doan': ['Thiếu máu do thiếu acid folic mức độ trung bình hồng cầu to.',
                         'Theo dõi thiếu máu do thiếu acid folic trên người lạm dụng rượu mạn tính.',
                         'Thiếu máu do thiếu acid folic có kèm viêm lưỡi Hunter teo gai lưỡi.',
                         'Thiếu máu do thiếu acid folic do kém hấp thu đường tiêu hóa.',
                         'Theo dõi thiếu máu do thiếu acid folic ở phụ nữ chuẩn bị mang thai.',
                         'Thiếu máu do thiếu acid folic giai đoạn đáp ứng tăng hồng cầu lưới sau điều trị.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ acid folic huyết thanh và định lượng vitamin B12 máu song song để loại trừ '
                        'tuyệt đối bệnh thiếu máu Biermer trước khi điều trị, chỉ định bổ sung acid folic đường uống '
                        'liều 5mg mỗi ngày liên tục trong 3 đến 4 tháng để hồi phục lượng dự trữ folate của cơ thể, tư '
                        'vấn chế độ ăn uống giàu rau có lá xanh đậm súp lơ các loại đậu đỗ và trái cây tươi cam chuối.',
                        'Kê đơn viên nén acid folic 5mg uống ngày 1 lần sau bữa ăn, dặn dò uống đều đặn hàng ngày '
                        'trong tối thiểu 3 tháng để tái tạo kho dự trữ folate tại gan.',
                        'Xét nghiệm công thức máu và đếm số lượng hồng cầu lưới sau 7-10 ngày điều trị để đánh giá cơn '
                        'bùng phát hồng cầu lưới (reticulocyte crisis) khẳng định chẩn đoán và đáp ứng tủy xương.',
                        'Cảnh báo tuyệt đối không dùng acid folic đơn độc khi chưa xét nghiệm nồng độ vitamin B12 vì '
                        'có thể làm che giấu biểu hiện huyết học trong khi tổn thương thoái hóa thần kinh do thiếu B12 '
                        'vẫn tiến triển nặng nề.',
                        'Hướng dẫn cách chế biến thực phẩm không đun nấu rau củ quá kỹ ở nhiệt độ cao kéo dài vì nhiệt '
                        'phân hủy dễ dàng làm phá hủy phần lớn hàm lượng acid folic tự nhiên.',
                        'Làm xét nghiệm chức năng gan thận và điện giải đồ, hẹn tái khám kiểm tra công thức máu tổng '
                        'quát sau 1 tháng để theo dõi tốc độ tăng huyết sắc tố.'],
  'bien_the_kham': ['Da xanh xao, niêm mạc mắt và vòm miệng nhợt nhạt rõ, lưỡi đỏ nhẵn bóng mất các gai lưỡi bình '
                    'thường không có vết loét sâu, nhịp tim nhanh 96 ck/p, nghe tim có tiếng thổi tâm thu cơ năng 2/6 '
                    'ở mỏm tim, khám thần kinh cảm giác sâu và phản xạ gân xương bình thường không có hội chứng tổn '
                    'thương kết hợp tủy sống (giúp phân biệt với thiếu vitamin B12).',
                    'Bệnh nhân mệt mỏi da xanh tái lòng bàn tay nhợt nhạt, củng mạc mắt có ánh vàng nhẹ do tán huyết '
                    'trong tủy xương, lưỡi viêm đỏ rát, xét nghiệm công thức máu có Hb 82 g/l với chỉ số MCV 108 fl.',
                    'Khám lâm sàng ghi nhận hội chứng thiếu máu rõ rệt, mạch nhanh 100 lần/phút huyết áp 110/65 mmHg, '
                    'nghe phổi trong, khám thần kinh cảm giác rung âm thoa và cảm giác bản thể ở hai bàn chân hoàn '
                    'toàn nguyên vẹn.',
                    'Bệnh nhân hoa mắt váng đầu khi ngồi dậy, niêm mạc môi nhạt màu, bề mặt lưỡi teo gai bóng loáng, '
                    'gan lách không sờ thấy, không có xuất huyết dưới da.',
                    'Thể trạng gầy nhợt nhạt, xét nghiệm huyết đồ phát hiện hồng cầu to đa hình thái kèm bạch cầu đa '
                    'nhân trung tính phân đoạn quá mức (hypersegmented neutrophils), nhịp tim đều.',
                    'Khám tuần hoàn có tiếng thổi tâm thu cơ năng nhẹ do giảm độ quánh máu, niêm mạc dưới lưỡi nhợt, '
                    'bệnh nhân ăn kém không ăn rau luộc chín kỹ kéo dài, sinh hiệu ổn định.'],
  'chan_doan': 'Thiếu máu do thiếu acid folic mức độ trung bình hồng cầu to.',
  'chinh': ['xét nghiệm tổng phân tích máu có thiếu máu hồng cầu to thể tích trung bình hồng cầu MCV trên 100 fl',
            'da xanh xao niêm mạc nhợt nhạt hoa mắt chóng mặt nhiều khi thay đổi tư thế',
            'nồng độ acid folic trong huyết thanh hoặc folate hồng cầu xét nghiệm giảm rất thấp'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'ke_hoach': 'Định lượng nồng độ acid folic huyết thanh và định lượng vitamin B12 máu song song để loại trừ tuyệt đối '
              'bệnh thiếu máu Biermer trước khi điều trị, chỉ định bổ sung acid folic đường uống liều 5mg mỗi ngày '
              'liên tục trong 3 đến 4 tháng để hồi phục lượng dự trữ folate của cơ thể, tư vấn chế độ ăn uống giàu rau '
              'có lá xanh đậm súp lơ các loại đậu đỗ và trái cây tươi cam chuối.',
  'kham': 'Da xanh xao, niêm mạc mắt và vòm miệng nhợt nhạt rõ, lưỡi đỏ nhẵn bóng mất các gai lưỡi bình thường không '
          'có vết loét sâu, nhịp tim nhanh 96 ck/p, nghe tim có tiếng thổi tâm thu cơ năng 2/6 ở mỏm tim, khám thần '
          'kinh cảm giác sâu và phản xạ gân xương bình thường không có hội chứng tổn thương kết hợp tủy sống (giúp '
          'phân biệt với thiếu vitamin B12).',
  'nhom': 'cả hai',
  'phu': ['viêm lưỡi Hunter lưỡi sưng đỏ bóng láng mất các gai lưỡi gây đau rát khi ăn đồ nóng',
          'mệt mỏi kiệt sức rã rời hồi hộp đánh trống ngực khi thực hiện công việc nhẹ',
          'chế độ ăn kiêng khem thiếu rau xanh tươi hoặc tiền sử nghiện rượu ăn uống kém kéo dài'],
  'ten': 'thiếu máu do thiếu acid folic'},
 {'bien_the_chan_doan': ['Bệnh Beriberi thiếu vitamin B1 thể ướt suy tim cung lượng cao cấp tính.',
                         'Theo dõi bệnh Beriberi thiếu vitamin B1 thể ướt thể tim mạch tối cấp Shoshin beriberi.',
                         'Bệnh Beriberi thiếu vitamin B1 thể ướt trên bệnh nhân lạm dụng rượu kéo dài.',
                         'Bệnh Beriberi thiếu vitamin B1 thể ướt biến chứng phù phổi ứ huyết nhẹ.',
                         'Theo dõi bệnh Beriberi thiếu vitamin B1 thể ướt kết hợp tổn thương dây thần kinh ngoại biên '
                         'thể khô.',
                         'Bệnh Beriberi thiếu vitamin B1 thể ướt đáp ứng ngoạn mục sau tiêm thiamine tĩnh mạch.'],
  'bien_the_ke_hoach': ['Chỉ định tiêm bắp hoặc tiêm tĩnh mạch chậm vitamin B1 (thiamine hydrochloride) liều 100-200mg '
                        'ngay lập tức và duy trì 100mg/ngày trong những ngày tiếp theo, dùng thuốc lợi tiểu quai '
                        'furosemide liều thấp giảm tải thể tích tuần hoàn, theo dõi sát sinh hiệu điện tâm đồ và độ '
                        'bão hòa oxy SpO2, cải thiện dinh dưỡng chuyển sang ăn gạo lứt hoặc bánh mì nguyên cám.',
                        'Tiêm tĩnh mạch chậm thiamine 100mg trong 100ml dung dịch NaCl 0.9% truyền trong 30 phút, dặn '
                        'dò điều dưỡng theo dõi sự giảm nhanh chóng của tần số tim và cải thiện huyết động trong vòng '
                        'vài giờ đầu.',
                        'Tuyệt đối không truyền dịch chứa đường dextrose nồng độ cao trước khi tiêm bổ sung thiamine '
                        'vì glucose sẽ tiêu thụ nốt lượng thiamine dự trữ cuối cùng làm khởi phát hội chứng não '
                        'Wernicke kịch phát.',
                        'Chỉ định siêu âm tim tại giường đánh giá phân suất tống máu thất trái EF (thường tăng hoặc '
                        'bảo tồn trong suy tim cung lượng cao) và kích thước buồng thất, đo men tim Troponin T và '
                        'NT-proBNP.',
                        'Bổ sung đa sinh tố nhóm B phối hợp gồm vitamin B2 B6 và acid folic qua đường uống, tư vấn cai '
                        'nghiện rượu hoàn toàn và hướng dẫn bảo tồn vitamin B1 khi nấu cơm không vo gạo quá kỹ.',
                        'Chuyển sang thiamine đường uống 50-100mg ngày 2-3 lần sau khi các triệu chứng suy tim và phù '
                        'chân đã thoái lui hoàn toàn, duy trì bổ sung liên tục trong tối thiểu 1-2 tháng.'],
  'bien_the_kham': ['Phù mềm ấn lõm rõ hai cẳng chân lan lên mu bàn chân hai bên, tĩnh mạch cổ nổi rõ ở tư thế 45 độ, '
                    'nhịp tim đập rất nhanh 118 chu kỳ/phút mạch ngoại vi nảy căng chìm nhanh (mạch Corrigan), huyết '
                    'áp đo được 145/55 mmHg (chênh lệch áp lực mạch rất rộng), nghe phổi có ran ẩm nhỏ hạt rải rác hai '
                    'đáy phổi, nghe tim có tiếng T3 ngựa phi.',
                    'Bệnh nhân khó thở phải ngồi dậy để thở, hai chân phù căng ấn lõm sâu mắt cá, nhịp tim nhanh xoang '
                    '120 ck/p, da tay chân ấm nóng do giãn mạch ngoại vi nghịch thường của suy tim cung lượng cao.',
                    'Khám lâm sàng ghi nhận phù toàn thân nhẹ kèm khó thở khi nằm, mạch nảy mạnh nghe rõ tiếng súng '
                    'lục trên động mạch đùi (dấu hiệu Traube), gan to 2cm dưới bờ sườn ấn đau tức nhẹ phản hồi gan '
                    'tĩnh mạch cổ (+).',
                    'Bệnh nhân có tiền sử nghiện rượu nặng ăn uống thất thường, vào viện vì phù chân và hồi hộp đánh '
                    'trống ngực, bắp chân bóp vào đau thốn, điện tâm đồ nhịp nhanh xoang sóng T dẹt.',
                    'Khám tuần hoàn phát hiện tim to sang trái mỏm tim đập mạnh lan tỏa ở liên sườn 6 ngoài đường '
                    'trung đòn, huyết áp 140/50 mmHg, nghe phổi rải rác ran ẩm đáy phổi hai bên.',
                    'Bệnh nhân thở nhanh 26 ck/p SpO2 93% khí phòng, phù mềm hai chi dưới đối xứng, tĩnh mạch cổ căng '
                    'phồng, khám phản xạ gân xương chi dưới giảm nhẹ cảm giác tê bì đầu ngón chân.'],
  'chan_doan': 'Bệnh Beriberi thiếu vitamin B1 thể ướt suy tim cung lượng cao cấp tính.',
  'chinh': ['phù to hai chi dưới xuất hiện và tiến triển nhanh chóng phù mềm ấn lõm rõ',
            'khó thở nhiều khi gắng sức và khó thở kịch phát khi nằm đầu bằng',
            'suy tim cung lượng cao với tim đập rất nhanh hồi hộp đánh trống ngực mạch nảy mạnh'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'dinh dưỡng',
  'ke_hoach': 'Chỉ định tiêm bắp hoặc tiêm tĩnh mạch chậm vitamin B1 (thiamine hydrochloride) liều 100-200mg ngay lập '
              'tức và duy trì 100mg/ngày trong những ngày tiếp theo, dùng thuốc lợi tiểu quai furosemide liều thấp '
              'giảm tải thể tích tuần hoàn, theo dõi sát sinh hiệu điện tâm đồ và độ bão hòa oxy SpO2, cải thiện dinh '
              'dưỡng chuyển sang ăn gạo lứt hoặc bánh mì nguyên cám.',
  'kham': 'Phù mềm ấn lõm rõ hai cẳng chân lan lên mu bàn chân hai bên, tĩnh mạch cổ nổi rõ ở tư thế 45 độ, nhịp tim '
          'đập rất nhanh 118 chu kỳ/phút mạch ngoại vi nảy căng chìm nhanh (mạch Corrigan), huyết áp đo được 145/55 '
          'mmHg (chênh lệch áp lực mạch rất rộng), nghe phổi có ran ẩm nhỏ hạt rải rác hai đáy phổi, nghe tim có tiếng '
          'T3 ngựa phi.',
  'nhom': 'người lớn',
  'phu': ['mệt mỏi rã rời bắp chân đau nhức căng tức và cảm giác nặng nề hai chân',
          'tiền sử ăn gạo xay xát quá kỹ vo gạo quá kỹ hoặc nghiện rượu ăn uống kém thiếu dinh dưỡng',
          'huyết áp tâm thu bình thường hoặc tăng nhẹ nhưng huyết áp tâm trương giảm sâu kẹp rộng'],
  'ten': 'bệnh Beriberi thiếu vitamin B1 thể ướt'},
 {'bien_the_chan_doan': ['Bệnh Scorbut thiếu vitamin C dinh dưỡng mạn tính.',
                         'Theo dõi bệnh Scorbut thiếu vitamin C có xuất huyết chân răng và nang lông điển hình.',
                         'Bệnh Scorbut thiếu vitamin C thể xuất huyết khớp và cơ sâu.',
                         'Bệnh Scorbut thiếu vitamin C ở người ăn kiêng cực đoan thiếu rau củ quả.',
                         'Theo dõi bệnh Scorbut thiếu vitamin C kèm theo thiếu máu thiếu sắt phối hợp.',
                         'Bệnh Scorbut thiếu vitamin C giai đoạn hồi phục nhanh sau bổ sung acid ascorbic.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ acid ascorbic (vitamin C) trong huyết tương hoặc bạch cầu khẳng định chẩn '
                        'đoán, chỉ định bổ sung vitamin C (acid ascorbic) đường uống liều cao 500-1000mg/ngày chia làm '
                        'nhiều lần trong ngày trong 2-4 tuần liên tục, sau đó giảm liều duy trì 100mg/ngày, tư vấn chế '
                        'độ ăn tăng cường rau xanh tươi củ quả và trái cây giàu vitamin C như cam chanh bưởi ớt chuông '
                        'ổi kiwi cà chua.',
                        'Kê đơn viên nén vitamin C 500mg uống ngày 2 lần sau bữa ăn chính trong 2 tuần đầu, dặn dò '
                        'uống nhiều nước trong ngày để phòng ngừa nguy cơ lắng đọng sỏi thận oxalat.',
                        'Hướng dẫn vệ sinh răng miệng nhẹ nhàng bằng bàn chải lông mềm và súc miệng bằng nước muối '
                        'sinh lý ấm, tránh chải răng mạnh gây tổn thương chảy máu nướu răng đang sưng phì đại.',
                        'Tư vấn giáo dục dinh dưỡng cụ thể về việc ăn rau củ quả tươi sống hoặc hấp chín vừa tới để '
                        'bảo tồn tối đa lượng vitamin C dễ bị phá hủy bởi nhiệt độ cao.',
                        'Xét nghiệm công thức máu và đông máu toàn bộ để loại trừ bệnh giảm tiểu cầu miễn dịch hoặc '
                        'rối loạn đông máu di truyền trước khi kết luận đơn thuần do thiếu vitamin C.',
                        'Theo dõi sự cầm máu chân răng và sự biến mất của các chấm đỏ xuất huyết nang lông sau 48-72 '
                        'giờ điều trị khẳng định đáp ứng ngoạn mục với liệu pháp vitamin C.'],
  'bien_the_kham': ['Khám khoang miệng nướu răng sưng nề màu tím đỏ bở rụng dễ chảy máu tự nhiên khi chạm nhẹ que đè '
                    'lưỡi, da hai cẳng chân có nhiều chấm đỏ xuất huyết quanh nang lông, sợi lông chân gãy xoắn hình '
                    'xoắn ốc, ấn khớp đầu gối sưng đau nhẹ do tụ máu màng hoạt dịch, không sốt, sinh hiệu ổn định.',
                    'Bệnh nhân có nướu răng phù nề phì đại che lấp một phần thân răng dễ rỉ máu tươi, rải rác cẳng '
                    'chân có nhiều mảng bầm tím xuất huyết dưới da tự nhiên sau va chạm nhẹ, sợi lông xoắn vặn nút '
                    'chai.',
                    'Khám răng miệng nướu xốp bở hơi thở có mùi hôi, da khô ráp nhiều chấm sẩn sừng hóa đỏ quanh chân '
                    'lông, các khớp cổ chân và khớp gối đau tức khi vận động thụ động do xuất huyết màng xương.',
                    'Khám lâm sàng ghi nhận các biểu hiện xuất huyết thành mạch điển hình, nghiệm pháp dây thắt (dấu '
                    'Lacet) dương tính mạnh xuất hiện nhiều chấm xuất huyết mới ở cẳng tay, xét nghiệm tiểu cầu bình '
                    'thường.',
                    'Bệnh nhân sống độc thân ăn mì gói đồ hộp nhiều tháng không ăn rau quả, da xanh nhợt, chân răng rỉ '
                    'máu thường xuyên khi đánh răng, các vết trầy xước ở chân 3 tuần chưa liền da.',
                    'Khám niêm mạc miệng thấy lợi răng viêm sưng bọng đỏ tím, chấm đỏ xuất huyết tập trung nhiều ở mặt '
                    'trước cẳng chân quanh nang lông, cơ lực chi dưới bình thường, nhịp tim đều 74 ck/p.'],
  'chan_doan': 'Bệnh Scorbut thiếu vitamin C dinh dưỡng mạn tính.',
  'chinh': ['chảy máu chân răng nướu răng sưng phì đại bở tím đỏ và rất dễ chảy máu tự phát',
            'xuất huyết dưới da dạng chấm đỏ quanh các nang lông ở hai cẳng chân và đùi',
            'đau nhức xương khớp và xuất huyết dưới màng xương làm hạn chế cử động đi lại'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'dinh dưỡng',
  'ke_hoach': 'Định lượng nồng độ acid ascorbic (vitamin C) trong huyết tương hoặc bạch cầu khẳng định chẩn đoán, chỉ '
              'định bổ sung vitamin C (acid ascorbic) đường uống liều cao 500-1000mg/ngày chia làm nhiều lần trong '
              'ngày trong 2-4 tuần liên tục, sau đó giảm liều duy trì 100mg/ngày, tư vấn chế độ ăn tăng cường rau xanh '
              'tươi củ quả và trái cây giàu vitamin C như cam chanh bưởi ớt chuông ổi kiwi cà chua.',
  'kham': 'Khám khoang miệng nướu răng sưng nề màu tím đỏ bở rụng dễ chảy máu tự nhiên khi chạm nhẹ que đè lưỡi, da '
          'hai cẳng chân có nhiều chấm đỏ xuất huyết quanh nang lông, sợi lông chân gãy xoắn hình xoắn ốc, ấn khớp đầu '
          'gối sưng đau nhẹ do tụ máu màng hoạt dịch, không sốt, sinh hiệu ổn định.',
  'nhom': 'cả hai',
  'phu': ['các sợi lông chân bị xoắn lại hình nút chai (corkscrew hairs) đặc trưng kèm dày sừng nang lông',
          'vết thương xây xước ngoài da rất lâu lành các vết sẹo cũ dễ bị bục toác rách lại',
          'chế độ ăn hoàn toàn thiếu rau xanh tươi và trái cây tươi có múi trong nhiều tháng liên tục'],
  'ten': 'bệnh Scorbut thiếu vitamin C'},
 {'bien_the_chan_doan': ['Thiếu vitamin A gây quáng gà khô mắt giai đoạn X1B có vệt Bitot.',
                         'Theo dõi thiếu vitamin A gây quáng gà khô mắt giai đoạn X1A khô kết mạc đơn thuần.',
                         'Thiếu vitamin A gây quáng gà khô mắt kèm theo dày sừng nang lông da.',
                         'Thiếu vitamin A gây quáng gà khô mắt do hội chứng kém hấp thu chất béo mạn tính.',
                         'Theo dõi thiếu vitamin A gây quáng gà khô mắt đe dọa loét nhuyễn giác mạc.',
                         'Thiếu vitamin A gây quáng gà khô mắt đáp ứng tốt sau liều vitamin A đầu tiên.'],
  'bien_the_ke_hoach': ['Chỉ định phác đồ điều trị vitamin A liều cao theo hướng dẫn của Tổ chức Y tế Thế giới WHO: '
                        'uống ngay ngày thứ nhất viên nang vitamin A 200.000 IU, ngày thứ hai uống tiếp 200.000 IU, và '
                        'uống nhắc lại liều 200.000 IU sau 2 tuần, nhỏ mắt nước mắt nhân tạo không chất bảo quản ngày '
                        '4-6 lần giữ ẩm giác mạc, tư vấn chế độ ăn tăng cường dầu mỡ giúp hấp thu vitamin A và thực '
                        'phẩm giàu caroten như gấc cà rốt bí đỏ đu đủ gan trứng.',
                        'Tra mỡ kháng sinh tetracyclin 1% hoặc tobramycin vào mắt ngày 2-3 lần để phòng ngừa bội nhiễm '
                        'vi khuẩn gây viêm loét hoại tử giác mạc trong giai đoạn niêm mạc mắt đang tổn thương khô ráp.',
                        'Hướng dẫn bảo vệ mắt tránh bụi bặm khói gió bằng cách đeo kính râm bảo hộ khi đi ra ngoài '
                        'đường, tuyệt đối không đắp lá thuốc dân gian vào mắt làm tăng nguy cơ mù lòa.',
                        'Tư vấn người bệnh bổ sung chất béo dầu ăn thực vật vào các bữa ăn hàng ngày vì vitamin A là '
                        'vitamin tan trong dầu cần có lipid để nhũ hóa hấp thu qua niêm mạc ruột non.',
                        'Khám chuyên khoa mắt định kỳ hàng tuần theo dõi sự thoái lui của vệt Bitot và phục hồi độ '
                        'trong suốt của giác mạc, đánh giá lại thị lực bóng tối sau 1 tháng.',
                        'Tầm soát các bệnh lý đường tiêu hóa gây kém hấp thu chất béo như viêm tụy mạn bệnh celiac '
                        'hoặc xơ gan mật để điều trị nguyên nhân gốc rễ gây thiếu hụt vitamin A.'],
  'bien_the_kham': ['Khám mắt bằng đèn khám chuyên khoa thấy kết mạc nhãn cầu khô ráp mất độ bóng ướt tự nhiên nhăn '
                    'nheo, phía ngoài thái dương kết mạc nhãn cầu hai mắt có mảng vệt Bitot màu trắng xốp dạng bọt khí '
                    'bám dính hình tam giác đáy quay về rìa giác mạc, giác mạc trong suốt chưa loét nhuyễn, da hai '
                    'cẳng tay khô ráp sần nang lông.',
                    'Bệnh nhân than nhìn mờ hẳn khi trời chập tối phải sờ soạng tìm đường, khám mắt có mảng vệt Bitot '
                    'trắng xám nổi gồ nhẹ ở góc ngoài kết mạc mắt phải, giác mạc bắt đầu mờ nhẹ mất độ bóng láng.',
                    'Khám thực thể mắt phát hiện khô kết mạc độ X1A kết mạc khô nhạt màu không có nước mắt làm ướt, '
                    'test Schirmer đo lượng nước mắt giảm sâu dưới 5mm sau 5 phút, da cánh tay dày sừng nang lông ráp '
                    'như giấy nhám.',
                    'Hai mắt có tổn thương vệt Bitot xốp bọt đặc trưng đối xứng hai bên, giác mạc còn nguyên vẹn chưa '
                    'loét thủng, thị lực ban ngày đo được 8/10 nhưng giảm nặng trong phòng tối.',
                    'Bệnh nhân chớp mắt liên tục do cộm xốn, màng kết mạc khô dính có nếp gấp đồng tâm quanh rìa giác '
                    'mạc khi liếc mắt, không có viêm mủ kết mạc cấp, cơ thể thiếu cân.',
                    'Khám mắt phát hiện quáng gà rõ qua thử nghiệm thích ứng bóng tối, kết mạc khô vệt Bitot góc thái '
                    'dương rõ rệt, nồng độ retinol huyết thanh xét nghiệm dưới 0.7 umol/l (dưới 20 mcg/dl).'],
  'chan_doan': 'Thiếu vitamin A gây quáng gà khô mắt giai đoạn X1B có vệt Bitot.',
  'chinh': ['quáng gà giảm thị lực nhìn mờ rõ rệt trong điều kiện ánh sáng yếu lúc chạng vạng tối',
            'khô kết mạc giác mạc mắt cộm xốn cay rát như có hạt cát cọ xát trong mắt',
            'xuất hiện vệt Bitot dải mảng xốp màu trắng bạc hình tam giác ở kết mạc nhãn cầu'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'dinh dưỡng',
  'ke_hoach': 'Chỉ định phác đồ điều trị vitamin A liều cao theo hướng dẫn của Tổ chức Y tế Thế giới WHO: uống ngay '
              'ngày thứ nhất viên nang vitamin A 200.000 IU, ngày thứ hai uống tiếp 200.000 IU, và uống nhắc lại liều '
              '200.000 IU sau 2 tuần, nhỏ mắt nước mắt nhân tạo không chất bảo quản ngày 4-6 lần giữ ẩm giác mạc, tư '
              'vấn chế độ ăn tăng cường dầu mỡ giúp hấp thu vitamin A và thực phẩm giàu caroten như gấc cà rốt bí đỏ '
              'đu đủ gan trứng.',
  'kham': 'Khám mắt bằng đèn khám chuyên khoa thấy kết mạc nhãn cầu khô ráp mất độ bóng ướt tự nhiên nhăn nheo, phía '
          'ngoài thái dương kết mạc nhãn cầu hai mắt có mảng vệt Bitot màu trắng xốp dạng bọt khí bám dính hình tam '
          'giác đáy quay về rìa giác mạc, giác mạc trong suốt chưa loét nhuyễn, da hai cẳng tay khô ráp sần nang lông.',
  'nhom': 'cả hai',
  'phu': ['da khô ráp tróc vảy sần sùi sừng hóa dày cộm quanh nang lông ở cánh tay và đùi',
          'thường xuyên chớp mắt sợ ánh sáng và hay bị viêm kết mạc nhiễm trùng mắt tái diễn',
          'chế độ ăn thiếu dầu mỡ chất béo và thực phẩm giàu tiền vitamin A beta-caroten'],
  'ten': 'thiếu vitamin A gây quáng gà khô mắt'},
 {'bien_the_chan_doan': ['Hội chứng tái nuôi dưỡng refeeding syndrome biến chứng hạ phospho máu nặng cấp tính.',
                         'Theo dõi hội chứng tái nuôi dưỡng refeeding syndrome có suy hô hấp do yếu cơ hoành.',
                         'Hội chứng tái nuôi dưỡng refeeding syndrome trên bệnh nhân suy kiệt nhịn đói kéo dài.',
                         'Hội chứng tái nuôi dưỡng refeeding syndrome kèm rối loạn nhịp tim do hạ điện giải.',
                         'Theo dõi hội chứng tái nuôi dưỡng refeeding syndrome thể giữ nước suy tim ứ huyết cấp.',
                         'Hội chứng tái nuôi dưỡng refeeding syndrome giai đoạn cấp cứu hồi sức điện giải.'],
  'bien_the_ke_hoach': ['Giảm ngay lập tức tốc độ nuôi dưỡng dinh dưỡng xuống dưới 50% nhu cầu (hoặc dưới 10 '
                        'kcal/kg/ngày), chỉ định bù phospho tĩnh mạch chậm dung dịch natri phosphate hoặc kali '
                        'phosphate kết hợp bù kali và magie đường truyền, tiêm tĩnh mạch thiamine liều cao '
                        '200-300mg/ngày trước khi tiếp tục truyền carbohydrate, theo dõi điện giải đồ và sinh hiệu '
                        'điện tâm đồ liên tục mỗi 6-12 giờ tại khoa Hồi sức tích cực.',
                        'Ngừng tạm thời các dung dịch truyền glucose đậm đặc, truyền bù natri phosphate 20-30 mmol pha '
                        'loãng trong NaCl 0.9% truyền tĩnh mạch chậm trong 4-6 giờ theo dõi nồng độ phospho máu.',
                        'Tiêm tĩnh mạch thiamine 200mg ngay lập tức trước khi cho dung nạp bất kỳ lượng tinh bột nào '
                        'để phòng ngừa bùng phát suy tim cấp và hội chứng não Wernicke do cạn kiệt thiamine '
                        'pyrophosphate.',
                        'Bù đồng thời magie sulfate tĩnh mạch và kali clorid vì hạ magie máu sẽ gây kháng điều trị hạ '
                        'kali và hạ phospho máu, mắc monitor theo dõi nhịp tim liên tục.',
                        'Khi các chỉ số điện giải phospho kali magie đã trở về ngưỡng an toàn mới tăng dần năng lượng '
                        'nuôi dưỡng rất chậm rãi tăng 200-300 kcal mỗi 2-3 ngày đến khi đạt mục tiêu.',
                        'Hạn chế truyền dịch muối nước dư thừa phòng ngừa quá tải tuần hoàn cấp và phù phổi cấp ở quả '
                        'tim đang suy yếu teo cơ của người suy kiệt dài ngày.'],
  'bien_the_kham': ['Bệnh nhân thể trạng gầy hốc hác suy kiệt rõ, vẻ mặt lo âu thở nhanh nông 26 ck/p, cơ lực tứ chi '
                    'giảm còn 3/5 gốc chi cử động yếu ớt, nhịp tim không đều 112 ck/p nghe có ngoại tâm thu rải rác, '
                    'nghe phổi có ran ẩm rải rác hai đáy phổi, phù nhẹ ấn lõm hai bên mắt cá chân, xét nghiệm ion đồ '
                    'khẩn có phospho máu 0.42 mmol/l kèm kali máu 3.0 mmol/l.',
                    'Bệnh nhân sau 48 giờ được truyền dịch nuôi dưỡng giàu đường glucose xuất hiện khó thở tím tái nhẹ '
                    'SpO2 91%, cơ hô hấp co kéo yếu, phù hai mu bàn chân mới xuất hiện, nồng độ phospho máu tụt sâu.',
                    'Khám lâm sàng phát hiện yếu liệt tứ chi tiến triển sau khi bắt đầu ăn lại bằng ống sonde dạ dày, '
                    'phản xạ gân xương giảm, nhịp tim nhanh 115 ck/p huyết áp 135/85 mmHg, tĩnh mạch cổ hơi nổi.',
                    'Bệnh nhân lơ mơ lú lẫn không định hướng được thời gian, cơ lực toàn thân suy sụp nhanh chóng, xét '
                    'nghiệm máu phát hiện tam chứng hạ phospho hạ kali và hạ magie máu cấp tính.',
                    'Thể trạng suy kiệt BMI 14.8 kg/m2, bụng chướng nhẹ giảm nhu động ruột, nghe tim có ngoại tâm thu '
                    'nhịp đôi, thở gắng sức co kéo cơ ức đòn chũm do yếu cơ hoành.',
                    'Khám cấp cứu ghi nhận tình trạng suy hô hấp cấp thứ phát sau nuôi dưỡng lại quá nhanh ở người '
                    'nhịn ăn 10 ngày, phù mềm hai cẳng chân, điện giải đồ phospho máu 0.38 mmol/l cực kỳ nguy hiểm.'],
  'chan_doan': 'Hội chứng tái nuôi dưỡng refeeding syndrome biến chứng hạ phospho máu nặng cấp tính.',
  'chinh': ['nồng độ phospho huyết thanh giảm nặng đột ngột dưới 0.65 mmol/l sau khi bắt đầu cho ăn lại',
            'xuất hiện tình trạng mệt mỏi lú lẫn yếu cơ hô hấp khó thở và yếu liệt cơ tứ chi',
            'khởi phát cấp tính ngay sau khi bắt đầu nuôi dưỡng tích cực ở người nhịn đói suy kiệt kéo dài'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'dinh dưỡng',
  'ke_hoach': 'Giảm ngay lập tức tốc độ nuôi dưỡng dinh dưỡng xuống dưới 50% nhu cầu (hoặc dưới 10 kcal/kg/ngày), chỉ '
              'định bù phospho tĩnh mạch chậm dung dịch natri phosphate hoặc kali phosphate kết hợp bù kali và magie '
              'đường truyền, tiêm tĩnh mạch thiamine liều cao 200-300mg/ngày trước khi tiếp tục truyền carbohydrate, '
              'theo dõi điện giải đồ và sinh hiệu điện tâm đồ liên tục mỗi 6-12 giờ tại khoa Hồi sức tích cực.',
  'kham': 'Bệnh nhân thể trạng gầy hốc hác suy kiệt rõ, vẻ mặt lo âu thở nhanh nông 26 ck/p, cơ lực tứ chi giảm còn '
          '3/5 gốc chi cử động yếu ớt, nhịp tim không đều 112 ck/p nghe có ngoại tâm thu rải rác, nghe phổi có ran ẩm '
          'rải rác hai đáy phổi, phù nhẹ ấn lõm hai bên mắt cá chân, xét nghiệm ion đồ khẩn có phospho máu 0.42 mmol/l '
          'kèm kali máu 3.0 mmol/l.',
  'nhom': 'người lớn',
  'phu': ['kèm theo hạ kali máu và hạ magie máu cấp tính do dịch chuyển ion vào nội bào',
          'phù ngoại vi giữ nước giữ muối do nồng độ insulin máu tăng tiết đột ngột sau ăn đường',
          'rối loạn nhịp tim nhanh hoặc xuất hiện ngoại tâm thu trên điện tâm đồ theo dõi'],
  'ten': 'hội chứng tái nuôi dưỡng refeeding syndrome'}]
