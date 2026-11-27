# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Khuôn bệnh]
Làm gì   : Chứa lô 50 khuôn bệnh đánh số 551–600 cho bộ sinh.
Vào → Ra : — (chỉ chứa dữ liệu: danh sách các khuôn bệnh lô 8 và bảng giới tính kèm theo)
Dùng bởi : bo_du_lieu/khuon_mo_rong
Tên cũ   : khuon_lo_8.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Khuôn bệnh Lô 8 (Khuôn 551 - 600, Task Axis: 600 Clinical Templates).

Chứa 50 khuôn từ DANH_SACH_UNG_VIEN_CON_LAI[250:300].
da_duyet = False (chờ Hội đồng Y khoa / bác sĩ chuyên khoa phê duyệt).
TUYỆT ĐỐI KHÔNG chứa chuỗi con "om".
0 cặp trùng >= 20%.
"""

GIOI_TINH_LO_8 = {}

BENH_LO_8 = [{'ten': 'suy tủy xương dòng hồng cầu đơn thuần',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['thiếu máu tiến triển mạn tính mức độ nặng dai dẳng',
            'số lượng hồng cầu lưới giảm nghiêm trọng gần như bằng không',
            'thể trạng mệt lả suy kiệt nhưng không có xuất huyết hay sốt nhiễm trùng'],
  'phu': ['da niêm mạc nhợt nhạt rõ rệt',
          'chóng mặt xây xẩm khi thay đổi tư thế',
          'không thấy gan lách hạch to khi thăm khám'],
  'bien_the_kham': ['Niêm mạc mắt nhợt, lòng bàn tay trắng bệch, nhịp tim nhanh 105 l/p có tiếng thổi tâm thu cơ năng '
                    '2/6 mỏm tim, không sờ thấy gan lách.',
                    'Da xanh tái, củng mạc mắt không vàng, nhịp tim đều rõ tần số 102 chu kỳ/phút, hạch ngoại biên '
                    'không sờ chạm, bụng mềm.',
                    'Thể trạng suy kiệt do thiếu máu kéo dài, kết mạc mắt nhợt nhạt, móng tay dẹt khum, tuyến giáp và '
                    'hạch lympho không to.',
                    'Khám thấy da xanh xao rõ rệt, mạch nhanh 100 lần/phút, huyết áp 110/70 mmHg, tiếng T1 T2 nghe rõ, '
                    'lách không sờ thấy dưới bờ sườn.',
                    'Niêm mạc miệng và lưỡi nhợt nhưng không viêm teo gai, tim đập nhanh do bù trừ thiếu máu, không có '
                    'nốt ban hay chấm xuất huyết.',
                    'Da xanh xao toàn thân, mạch quay nảy nhanh 104 l/p, bụng mềm không chướng, lách không to qua '
                    'nghiệm pháp gõ và sờ sâu.'],
  'bien_the_chan_doan': ['Suy tủy xương dòng hồng cầu đơn thuần Pure Red Cell Aplasia.',
                         'Theo dõi bất sản tủy dòng hồng cầu đơn thuần người lớn.',
                         'Suy giảm sản xuất dòng hồng cầu đơn độc tại tủy xương.',
                         'Hội chứng Pure Red Cell Aplasia PRCA mắc phải ở người lớn.',
                         'Thiếu máu nặng do bất sản tủy chọn lọc dòng hồng cầu.',
                         'Bất sản dòng hồng cầu đơn thuần mắc phải có thiếu máu mạn tính.'],
  'bien_the_ke_hoach': ['Làm tủy đồ và sinh thiết tủy xương, xét nghiệm kháng thể kháng erythropoietin, xét nghiệm '
                        'parvovirus B19, truyền khối hồng cầu cùng nhóm khi Hb dưới 70 g/L.',
                        'Chỉ định huyết đồ tủy đồ đo tỷ lệ hồng cầu lưới, chụp cắt lớp lồng ngực tầm soát u tuyến ức, '
                        'hội chẩn chuyên khoa huyết học để dùng thuốc ức chế miễn dịch cyclosporin.',
                        'Làm tủy đồ đánh giá mẫu hồng cầu, xét nghiệm sắt huyết thanh ferritin, tư vấn truyền máu phân '
                        'đoạn và kế hoạch điều trị corticosteroid đường toàn thân.',
                        'Hẹn làm sinh thiết tủy xác chẩn, định lượng erythropoietin máu, xét nghiệm sinh học phân tử '
                        'tìm virus parvovirus B19, hỗ trợ truyền hồng cầu lắng.',
                        'Xét nghiệm công thức máu toàn phần kèm đếm hồng cầu lưới, tủy đồ xác định mật độ tế bào dòng '
                        'tủy, chụp CT trung thất tìm u ức kèm theo.',
                        'Nhập viện chuyên khoa huyết học, làm xét nghiệm tủy đồ, tầm soát bệnh tự miễn phối hợp và bắt '
                        'đầu phác đồ ức chế miễn dịch phù hợp.'],
  'kham': 'Niêm mạc mắt nhợt, lòng bàn tay trắng bệch, nhịp tim nhanh 105 l/p có tiếng thổi tâm thu cơ năng 2/6 mỏm '
          'tim, không sờ thấy gan lách.',
  'chan_doan': 'Suy tủy xương dòng hồng cầu đơn thuần Pure Red Cell Aplasia.',
  'ke_hoach': 'Làm tủy đồ và sinh thiết tủy xương, xét nghiệm kháng thể kháng erythropoietin, xét nghiệm parvovirus '
              'B19, truyền khối hồng cầu cùng nhóm khi Hb dưới 70 g/L.'},
 {'ten': 'thiếu máu do suy thận mạn thiếu erythropoietin',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['mức lọc cầu thận eGFR giảm nặng kèm thiếu máu đẳng sắc đẳng bào',
            'hồng cầu giảm tương ứng với mức độ suy thận không đáp ứng với sắt đơn thuần',
            'nồng độ erythropoietin máu giảm bất thường so với mức độ thiếu máu thực tế'],
  'phu': ['thể trạng mệt mỏi hoa mắt thường xuyên',
          'da khô sạm màu rơm kèm ngứa ngáy râm ran',
          'phù nhẹ hai mi mắt buổi sáng'],
  'bien_the_kham': ['Da xanh xao ánh màu vàng rơm, niêm mạc nhợt vừa, huyết áp 150/90 mmHg, phù nhẹ hai mắt cá chân, '
                    'tim phổi bình thường.',
                    'Niêm mạc mắt nhợt, da khô sạm có vết cào gãi ngứa, huyết áp cao 145/85 mmHg, phù nhẹ mi mắt và '
                    'mặt trước cẳng chân.',
                    'Khám thấy da xanh niêm mạc nhợt rõ, mạch 86 l/p, huyết áp 155/95 mmHg, tiếng tim mờ nhẹ, hai đáy '
                    'phổi thông khí tốt.',
                    'Thể trạng mệt mỏi xanh xao, niêm mạc đáy mắt nhạt màu, ấn lõm nhẹ trước xương chày, tiếng thổi '
                    'tâm thu 2/6 cơ năng ổ van tim.',
                    'Sắc diện xanh xao kết hợp sạm da đặc trưng bệnh thận, phù mềm hai chi dưới, huyết áp giao động '
                    '150/90 mmHg.',
                    'Da xanh niêm mạc nhạt, mạch đập 88 chu kỳ/phút, huyết áp kiểm soát chưa tốt 160/90 mmHg, không có '
                    'ban xuất huyết dưới da.'],
  'bien_the_chan_doan': ['Thiếu máu mạn tính do bệnh thận mạn thiếu hụt erythropoietin.',
                         'Thiếu máu đẳng sắc đẳng bào ở bệnh nhân suy thận mạn giai đoạn tiến triển.',
                         'Thiếu máu liên quan bệnh thận mạn tính do suy giảm sản xuất EPO.',
                         'Bệnh thận mạn biến chứng thiếu máu thiếu hụt hormone erythropoietin.',
                         'Theo dõi thiếu máu do suy thận mạn giảm tiết erythropoietin kết hợp tăng ure huyết.',
                         'Hội chứng thiếu máu do bệnh thận mạn có chỉ định bổ sung chất kích thích tạo hồng cầu.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ ferritin máu và độ bão hòa transferrin TSAT, tiêm dưới da erythropoietin '
                        'tái tổ hợp EPO liều khởi đầu 4000 đơn vị tuần 2 lần, bổ sung sắt tĩnh mạch hoặc uống.',
                        'Kiểm tra bộ chỉ số chuyển hóa sắt, bắt đầu phác đồ ESA kích thích dòng hồng cầu mục tiêu Hb '
                        '100-115 g/L, kiểm soát huyết áp bằng thuốc ức chế thụ thể.',
                        'Xét nghiệm công thức máu creatinin ure điện giải đồ, bù sắt đường tiêm nếu TSAT dưới 30%, chỉ '
                        'định tiêm erythropoietin tuần 1-2 lần kèm theo dõi sát huyết áp.',
                        'Theo dõi sát công thức máu mỗi 2-4 tuần khi bắt đầu dùng EPO, duy trì sắt huyết thanh đầy đủ, '
                        'tối ưu hóa điều trị nội khoa bệnh thận mạn nền.',
                        'Chỉ định xét nghiệm ferritin và TSAT loại trừ thiếu sắt chức năng, tiêm thuốc kích thích sinh '
                        'hồng cầu Darbepoetin hoặc EPO định kỳ, theo dõi chỉ số Hb máu.',
                        'Bổ sung viên sắt kết hợp tiêm erythropoietin liều chuẩn, tái khám định kỳ mỗi tháng xét '
                        'nghiệm công thức máu và chức năng lọc thận.'],
  'kham': 'Da xanh xao ánh màu vàng rơm, niêm mạc nhợt vừa, huyết áp 150/90 mmHg, phù nhẹ hai mắt cá chân, tim phổi '
          'bình thường.',
  'chan_doan': 'Thiếu máu mạn tính do bệnh thận mạn thiếu hụt erythropoietin.',
  'ke_hoach': 'Định lượng nồng độ ferritin máu và độ bão hòa transferrin TSAT, tiêm dưới da erythropoietin tái tổ hợp '
              'EPO liều khởi đầu 4000 đơn vị tuần 2 lần, bổ sung sắt tĩnh mạch hoặc uống.'},
 {'ten': 'thiếu máu bất sản tủy aplastic anemia',
  'nhom': 'cả hai',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['giảm đồng thời ba dòng tế bào máu ngoại vi gồm hồng cầu bạch cầu và tiểu cầu',
            'xuất huyết dưới da niêm mạc tự phát do giảm tiểu cầu nặng',
            'sốt tái diễn do nhiễm trùng cơ hội vì bạch cầu hạt trung tính giảm sâu'],
  'phu': ['da xanh xao nhợt nhạt rõ',
          'chảy máu chân răng rỉ rả kéo dài',
          'không thấy phì đại gan lách hoặc hạch ngoại biên'],
  'bien_the_kham': ['Da xanh nhợt rõ, rải rác chấm và nốt xuất huyết đa hình thái ở hai cẳng tay cẳng chân, họng đỏ '
                    'nhẹ, gan lách hạch không to.',
                    'Niêm mạc mắt trắng nhợt, chảy máu rỉ rả chân răng cửa hàm dưới, các mảng bầm tím rải rác trên da '
                    'tay chân, nhiệt độ 38 độ C.',
                    'Khám thấy hội chứng thiếu máu nặng kết hợp hội chứng xuất huyết dạng chấm dưới da, không sờ thấy '
                    'hạch to các vùng ngoại biên.',
                    'Thể trạng suy kiệt xanh xao, niêm mạc miệng có vài nốt phồng xuất huyết, nghe tim nhịp nhanh 110 '
                    'l/p, phổi thông khí rõ.',
                    'Da tái nhợt toàn thân, nhiều vết bầm xuất huyết tự nhiên chi dưới, sốt 38.2 độ C, bụng mềm lách '
                    'không to qua khám lâm sàng.',
                    'Niêm mạc nhạt màu nặng, chấm xuất huyết rải rác mặt trước hai cẳng chân, không sờ thấy gan lách '
                    'to, nhịp tim đều nhanh 105 chu kỳ/phút.'],
  'bien_the_chan_doan': ['Thiếu máu bất sản tủy Aplastic Anemia mức độ nặng.',
                         'Suy tủy toàn bộ giảm ba dòng tế bào máu ngoại vi Aplastic Anemia.',
                         'Bất sản tủy xương giảm sinh hồng cầu bạch cầu và tiểu cầu.',
                         'Hội chứng suy tủy xương toàn bộ aplastic anemia vô căn.',
                         'Theo dõi thiếu máu bất sản tủy giảm sinh tủy xương nặng.',
                         'Bệnh suy tủy toàn thể Aplastic Anemia biến chứng nhiễm trùng và xuất huyết.'],
  'bien_the_ke_hoach': ['Nhập viện phòng cách ly bảo vệ, làm tủy đồ và sinh thiết tủy xương xác chẩn, truyền khối tiểu '
                        'cầu gạn tách và khối hồng cầu lọc bạch cầu khi có chỉ định khẩn.',
                        'Chỉ định sinh thiết tủy xương đánh giá độ giàu tế bào tủy, cấy máu và dùng kháng sinh phổ '
                        'rộng chống nhiễm trùng, xét nghiệm HLA chuẩn bị ghép tủy.',
                        'Cách ly vô khuẩn tránh lây nhiễm chéo, truyền chế phẩm máu an toàn, hội chẩn dùng huyết thanh '
                        'kháng tế bào lympho ATG kết hợp cyclosporin A.',
                        'Xét nghiệm tủy đồ sinh thiết gai chậu, xét nghiệm tìm dòng tế bào PNH bằng kỹ thuật đếm tế '
                        'bào dòng chảy flow cytometry, điều trị nâng đỡ tích cực.',
                        'Hỗ trợ truyền máu phù hợp kháng nguyên, xét nghiệm HLA người thân tìm người hiến ghép tế bào '
                        'gốc tạo máu, kiểm soát sốt nhiễm trùng bằng kháng sinh tĩnh mạch.',
                        'Làm thủ tục nhập viện khoa Huyết học, thực hiện sinh thiết tủy xương, lập kế hoạch ức chế '
                        'miễn dịch chuyên sâu hoặc ghép tế bào gốc đồng loại.'],
  'kham': 'Da xanh nhợt rõ, rải rác chấm và nốt xuất huyết đa hình thái ở hai cẳng tay cẳng chân, họng đỏ nhẹ, gan '
          'lách hạch không to.',
  'chan_doan': 'Thiếu máu bất sản tủy Aplastic Anemia mức độ nặng.',
  'ke_hoach': 'Nhập viện phòng cách ly bảo vệ, làm tủy đồ và sinh thiết tủy xương xác chẩn, truyền khối tiểu cầu gạn '
              'tách và khối hồng cầu lọc bạch cầu khi có chỉ định khẩn.'},
 {'ten': 'bệnh đa hồng cầu nguyên phát Polycythemia vera',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['da niêm mạc đỏ tía đặc biệt ở mặt lòng bàn tay và kết mạc mắt',
            'ngứa dữ dội toàn thân sau khi tắm nước ấm hoặc tiếp xúc nước nóng',
            'nồng độ hemoglobin và hematocrit tăng rất cao kèm đột biến gen JAK2 V617F'],
  'phu': ['đau đầu váng đầu cảm giác nặng tức ngực',
          'lách to sờ thấy dưới bờ sườn',
          'rối loạn thị giác nhìn mờ từng cơn'],
  'bien_the_kham': ['Khuôn mặt đỏ tía bừng sáng, kết mạc mắt cương tụ đỏ, lòng bàn tay đỏ rực, sờ thấy cực dưới lách '
                    'mấp mé bờ sườn trái 2cm.',
                    'Da mặt và cổ đỏ bừng kiểu đa hồng cầu, huyết áp 150/95 mmHg, niêm mạc mắt xung huyết, lách to độ '
                    '1 chắc không đau.',
                    'Khám thấy da đỏ sẫm đặc trưng, mạch 84 l/p, gõ đục vùng lách vượt quá bờ sườn, tim phổi chưa ghi '
                    'nhận bất thường khác.',
                    'Kết mạc mắt đỏ quạch xung huyết, da lòng bàn tay bàn chân đỏ bừng nóng ran, sờ thấy bờ dưới lách '
                    'cách bờ sườn trái 3cm.',
                    'Sắc mặt đỏ ửng dù không sốt hay uống rượu, huyết áp tăng nhẹ 145/90 mmHg, lách to rõ dưới bờ sườn '
                    'khi hít sâu.',
                    'Sung huyết niêm mạc hầu họng và mắt, da đỏ tía vùng ngực cổ, lách sờ chạm dưới bờ sườn trái, mạch '
                    'nảy căng.'],
  'bien_the_chan_doan': ['Bệnh đa hồng cầu nguyên phát Polycythemia vera mang đột biến gen JAK2.',
                         'Tăng sinh tủy ác tính thể đa hồng cầu nguyên phát Polycythemia vera.',
                         'Đa hồng cầu nguyên phát Polycythemia vera giai đoạn tiến triển có lách to.',
                         'Theo dõi bệnh đa hồng cầu nguyên phát Polycythemia vera tăng hematocrit cao.',
                         'Hội chứng tăng sinh tủy mạn thể đa hồng cầu chân chính Polycythemia vera.',
                         'Đa hồng cầu nguyên phát Polycythemia vera có nguy cơ cao biến cố huyết khối tắc mạch.'],
  'bien_the_ke_hoach': ['Chích máu rút bớt thể tích máu 300-500 ml định kỳ duy trì Hematocrit dưới 45%, dùng aspirin '
                        'liều thấp 81-100 mg mỗi ngày phòng huyết khối, xét nghiệm định lượng đột biến JAK2 V617F.',
                        'Lập kế hoạch trích máu tĩnh mạch hạ Hct, bắt đầu điều trị thuốc hạ tế bào Hydroxyurea đường '
                        'uống, theo dõi công thức máu toàn phần định kỳ hàng tháng.',
                        'Chỉ định rút máu điều trị mục tiêu Hct dưới 45%, dùng thuốc kháng histamin giảm ngứa khi tắm '
                        'nước ấm, bổ sung Hydroxyurea nếu nguy cơ cao.',
                        'Kiểm tra chức năng đông máu và siêu âm Doppler tĩnh mạch bụng tầm soát huyết khối, duy trì '
                        'aspirin liều thấp và phác đồ hạ tế bào tủy phù hợp.',
                        'Tư vấn trích máu tĩnh mạch định kỳ, xét nghiệm tủy đồ và sinh thiết tủy xương đánh giá tăng '
                        'sinh ba dòng tế bào, dùng thuốc giảm số lượng tế bào tủy.',
                        'Phác đồ phối hợp trích máu tĩnh mạch cấp thời và Hydroxyurea dài hạn, duy trì uống đủ nước '
                        'tránh cô đặc máu và kiểm soát huyết áp.'],
  'kham': 'Khuôn mặt đỏ tía bừng sáng, kết mạc mắt cương tụ đỏ, lòng bàn tay đỏ rực, sờ thấy cực dưới lách mấp mé bờ '
          'sườn trái 2cm.',
  'chan_doan': 'Bệnh đa hồng cầu nguyên phát Polycythemia vera mang đột biến gen JAK2.',
  'ke_hoach': 'Chích máu rút bớt thể tích máu 300-500 ml định kỳ duy trì Hematocrit dưới 45%, dùng aspirin liều thấp '
              '81-100 mg mỗi ngày phòng huyết khối, xét nghiệm định lượng đột biến JAK2 V617F.'},
 {'ten': 'tăng tiểu cầu nguyên phát',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['số lượng tiểu cầu máu ngoại vi tăng dai dẳng trên 450000 trên một microlit',
            'dị cảm bỏng rát đau đỏ ở các đầu ngón tay ngón chân do giãn mạch đỏ ngón',
            'tăng sinh mẫu tiểu cầu dòng khổng lồ trong tủy xương kèm đột biến JAK2 hoặc CALR'],
  'phu': ['xuất huyết bầm tím nhẹ dưới da không rõ va chạm', 'nhức đầu chóng mặt thoáng qua', 'lách to nhẹ kín đáo'],
  'bien_the_kham': ['Đầu các ngón chân tay đỏ hồng ấm nóng ấn đau rát nhẹ, da niêm mạc hồng hào, lách mấp mé bờ sườn, '
                    'không có ban xuất huyết hoại tử.',
                    'Khám thấy đầu ngón tay đỏ tía nóng rát kiểu đau đỏ chi erythromelalgia, mạch quay đều rõ 80 l/p, '
                    'gan lách không to rõ trên lâm sàng.',
                    'Da bình thường không phù, vài vết bầm tím nhỏ ở cẳng chân do va quệt nhẹ, sờ cực dưới lách to nhẹ '
                    'dưới hạ sườn trái.',
                    'Đầu ngón tay ngón chân sung huyết đỏ rực tăng cảm giác đau khi buông thõng, mạch ngoại vi bắt rõ, '
                    'tim phổi nghe trong.',
                    'Lòng bàn tay và đầu ngón ấm nóng đỏ da, gõ lách to nhẹ vượt bờ sườn 1cm, huyết áp 130/80 mmHg, '
                    'không dấu thần kinh khu trú.',
                    'Chi trên và chi dưới ấm, đầu ngón tay đỏ rát dị cảm nhẹ, mạch mu chân nảy đều hai bên, lách sờ '
                    'thấy mấp mé bờ sườn trái.'],
  'bien_the_chan_doan': ['Tăng tiểu cầu nguyên phát Essential Thrombocythemia nguy cơ huyết khối mạch máu.',
                         'Tăng sinh tủy mạn thể tăng tiểu cầu nguyên phát Essential Thrombocythemia.',
                         'Bệnh tăng tiểu cầu nguyên phát ET có biểu hiện đau đỏ đầu chi erythromelalgia.',
                         'Theo dõi tăng tiểu cầu nguyên phát có đột biến gen JAK2 hoặc CALR.',
                         'Hội chứng tăng tiểu cầu nguyên phát dòng tủy xương chưa biến chứng tắc mạch lớn.',
                         'Tăng tiểu cầu nguyên phát Essential Thrombocythemia giai đoạn cần can thiệp hạ tế bào.'],
  'bien_the_ke_hoach': ['Dùng aspirin liều thấp 81-100 mg hàng ngày kiểm soát đau đỏ đầu chi và phòng ngừa huyết khối, '
                        'xét nghiệm đột biến gen JAK2 CALR MPL, xét nghiệm tủy đồ sinh thiết tủy.',
                        'Chỉ định thuốc hạ số lượng tiểu cầu Hydroxyurea hoặc Anagrelide nếu thuộc nhóm nguy cơ cao, '
                        'kiểm tra công thức máu định kỳ mỗi 2-4 tuần.',
                        'Làm sinh thiết tủy xương xác định mật độ mẫu tiểu cầu khổng lồ, dùng aspirin liều nhỏ, tầm '
                        'soát các yếu tố nguy cơ tim mạch kèm theo.',
                        'Xét nghiệm tủy đồ loại trừ bạch cầu dòng tủy mạn và tăng sinh tủy khác, duy trì aspirin 100 '
                        'mg ngày 1 lần, theo dõi sát số lượng tiểu cầu.',
                        'Chỉ định Hydroxyurea duy trì số lượng tiểu cầu trong khoảng an toàn 400000, xét nghiệm đông '
                        'máu toàn bộ và siêu âm mạch máu.',
                        'Khám chuyên khoa Huyết học, bắt đầu điều trị hạ tế bào kết hợp thuốc chống kết tập tiểu cầu '
                        'liều thấp, dặn dò bệnh nhân tránh chấn thương chảy máu.'],
  'kham': 'Đầu các ngón chân tay đỏ hồng ấm nóng ấn đau rát nhẹ, da niêm mạc hồng hào, lách mấp mé bờ sườn, không có '
          'ban xuất huyết hoại tử.',
  'chan_doan': 'Tăng tiểu cầu nguyên phát Essential Thrombocythemia nguy cơ huyết khối mạch máu.',
  'ke_hoach': 'Dùng aspirin liều thấp 81-100 mg hàng ngày kiểm soát đau đỏ đầu chi và phòng ngừa huyết khối, xét '
              'nghiệm đột biến gen JAK2 CALR MPL, xét nghiệm tủy đồ sinh thiết tủy.'},
 {'ten': 'bệnh máu khó đông Hemophilia A di truyền',
  'nhom': 'cả hai',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['chảy máu khớp tái diễn gây sưng đau hạn chế vận động khớp gối hoặc cổ chân',
            'xuất huyết khối cơ lớn tự phát sau va chạm nhẹ hoặc không rõ chấn thương',
            'hoạt độ yếu tố VIII đông máu giảm sâu kèm thời gian aPTT kéo dài bất thường'],
  'phu': ['chảy máu khó cầm sau nhổ răng hoặc rách da nông',
          'biến dạng cứng khớp do tràn máu ổ khớp mạn tính',
          'tiền sử gia đình có người thân nam giới mắc bệnh tương tự'],
  'bien_the_kham': ['Khớp gối phải sưng to căng bóng da ấm đau nhiều khi cử động, hạn chế gập duỗi khớp gối, có khối '
                    'máu tụ lớn vùng bắp chân phải.',
                    'Khớp cổ chân sưng nề biến dạng nhẹ do tràn máu tái diễn, da phủ khớp ấm nhẹ, xuất huyết cơ delta '
                    'cánh tay ấn đau tức.',
                    'Khám thấy khớp gối sưng phù tràn dịch máu ổ khớp, ấn đau chói quanh khe khớp, da cẳng chân có '
                    'mảng bầm tím rộng ấn căng cứng.',
                    'Hạn chế tầm vận động khớp khuỷu và gối do cứng khớp thoái hóa sau tràn máu, cơ đùi teo nhẹ, không '
                    'có vết thương hở rỉ máu.',
                    'Khớp gối trái sưng căng nóng đau nhức rõ rệt, bập bềnh xương bánh chè dương tính, khối máu tụ sâu '
                    'trong cơ đùi gây co rút chân.',
                    'Biến dạng khớp gối hai bên do bệnh khớp Hemophilia mạn tính, sưng cấp gối bên phải, vết rách niêm '
                    'mạc miệng rỉ máu liên tục.'],
  'bien_the_chan_doan': ['Bệnh máu khó đông Hemophilia A di truyền thể nặng đợt tràn máu khớp cấp.',
                         'Hemophilia A thiếu hụt yếu tố VIII đông máu có biến chứng bệnh khớp do chảy máu.',
                         'Hội chứng xuất huyết di truyền Hemophilia A đợt chảy máu khối cơ lớn.',
                         'Theo dõi bệnh ưa chảy máu Hemophilia A di truyền gen lặn liên kết nhiễm sắc thể X.',
                         'Hemophilia A thể trung bình biến chứng tràn máu khớp gối tái diễn.',
                         'Bệnh máu khó đông Hemophilia A có tổn thương phá hủy sụn khớp mạn tính.'],
  'bien_the_ke_hoach': ['Tiêm truyền tĩnh mạch cô đặc yếu tố VIII tái tổ hợp hoặc huyết tương tươi đông lạnh nâng hoạt '
                        'độ yếu tố VIII lên 40-50%, bất động khớp gối chườm lạnh, tuyệt đối không chọc hút khớp khi '
                        'chưa bù đủ yếu tố đông máu.',
                        'Truyền bù yếu tố VIII cô đặc khẩn cấp theo cân nặng, dùng thuốc giảm đau paracetamol đơn '
                        'thuần tránh NSAID và aspirin, chụp X-quang khớp gối đánh giá sụn khớp.',
                        'Lập kế hoạch điều trị dự phòng yếu tố VIII định kỳ 2-3 lần tuần, vật lý trị liệu phục hồi '
                        'chức năng vận động khớp sau khi hết giai đoạn chảy máu cấp.',
                        'Xét nghiệm định lượng chất ức chế kháng thể yếu tố VIII inhibitor, truyền yếu tố VIII điều '
                        'trị chảy máu cơ sâu, tư vấn di truyền học cho gia đình.',
                        'Bù yếu tố VIII liều tấn công, nẹp cố định khớp gối ở tư thế cơ năng, theo dõi sát chu vi vòng '
                        'gối và nồng độ hemoglobin máu.',
                        'Chỉ định truyền chế phẩm yếu tố VIII, hướng dẫn bệnh nhân và người nhà kỹ thuật sơ cứu RICE '
                        'khi chấn thương, lập sổ theo dõi bệnh nhân Hemophilia quản lý định kỳ.'],
  'kham': 'Khớp gối phải sưng to căng bóng da ấm đau nhiều khi cử động, hạn chế gập duỗi khớp gối, có khối máu tụ lớn '
          'vùng bắp chân phải.',
  'chan_doan': 'Bệnh máu khó đông Hemophilia A di truyền thể nặng đợt tràn máu khớp cấp.',
  'ke_hoach': 'Tiêm truyền tĩnh mạch cô đặc yếu tố VIII tái tổ hợp hoặc huyết tương tươi đông lạnh nâng hoạt độ yếu tố '
              'VIII lên 40-50%, bất động khớp gối chườm lạnh, tuyệt đối không chọc hút khớp khi chưa bù đủ yếu tố đông '
              'máu.'},
 {'ten': 'bệnh von Willebrand thể nhẹ type 1',
  'nhom': 'cả hai',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['chảy máu niêm mạc mũi miệng rỉ rả kéo dài khó cầm',
            'nồng độ kháng nguyên vWF và hoạt độ vWF ristocetin cofactor giảm nhẹ',
            'thời gian máu chảy kéo dài nhưng số lượng tiểu cầu hoàn toàn bình thường'],
  'phu': ['kinh nguyệt kéo dài ra nhiều ở phụ nữ độ tuổi sinh sản',
          'dễ xuất hiện vết bầm tím mảng da khi va quệt nhẹ',
          'chảy máu sau can thiệp thủ thuật răng miệng'],
  'bien_the_kham': ['Niêm mạc hốc mũi có vết đông rỉ máu nhẹ, rải rác vài mảng bầm tím nông kích thước 1-2cm ở mặt '
                    'trước cẳng chân, tim phổi bình thường.',
                    'Chảy máu rỉ rả tại viền nướu răng cửa hàm trên sau đánh răng, da có vài vết bầm xuất huyết nông, '
                    'niêm mạc mắt hồng nhạt.',
                    'Khám thấy niêm mạc mũi sung huyết rỉ dịch máu, da vùng cẳng tay có mảng bầm nhạt màu không sờ '
                    'thấy khối tụ máu sâu, khớp không sưng.',
                    'Da niêm mạc hồng hào, rải rác dát xuất huyết và mảng bầm da lành sẹo bình thường, không có sưng '
                    'đau khớp hay khối cơ.',
                    'Chảy máu chân răng rỉ rả kéo dài sau nhổ răng số 6, da tay chân có vết bầm nông tự nhiên, không '
                    'sờ thấy gan lách hạch.',
                    'Niêm mạc miệng bình thường ngoại trừ vài điểm rỉ máu chân răng nướu, da tay chân có vết bầm tím '
                    'do va chạm nhẹ, khớp cử động tự do.'],
  'bien_the_chan_doan': ['Bệnh von Willebrand thể nhẹ Type 1 có triệu chứng chảy máu niêm mạc.',
                         'Rối loạn đông cầm máu di truyền bệnh von Willebrand Type 1.',
                         'Hội chứng von Willebrand Type 1 thiếu hụt số lượng một phần yếu tố vWF.',
                         'Theo dõi bệnh von Willebrand Type 1 biến chứng rong kinh kéo dài.',
                         'Bệnh von Willebrand thể nhẹ có đợt chảy máu chân răng khó cầm sau can thiệp thủ thuật.',
                         'Bệnh lý đông máu von Willebrand Type 1 mức độ nhẹ đáp ứng với desmopressin.'],
  'bien_the_ke_hoach': ['Dùng thuốc Desmopressin DDAVP xịt mũi hoặc tiêm truyền tĩnh mạch để kích thích giải phóng vWF '
                        'nội sinh, phối hợp acid tranexamic uống cầm máu niêm mạc, kiểm tra vWF:Ag và vWF:RCo.',
                        'Kê đơn acid tranexamic 500mg uống 3 lần ngày khi có chảy máu niêm mạc hoặc chu kỳ kinh '
                        'nguyệt, xét nghiệm định lượng kháng nguyên và hoạt độ von Willebrand.',
                        'Tư vấn tiêm phòng viêm gan B, dùng Desmopressin trước các can thiệp nhổ răng hoặc tiểu phẫu, '
                        'tránh hoàn toàn các thuốc chống đông và aspirin.',
                        'Xét nghiệm phân tích đa trùng phân tử vWF multimers loại trừ type 2, chuẩn bị chế phẩm cô đặc '
                        'chứa vWF và yếu tố VIII dự phòng khi phẫu thuật lớn.',
                        'Điều trị hỗ trợ cầm máu tại chỗ bằng gạc tẩm acid tranexamic, bổ sung viên sắt nếu có thiếu '
                        'máu do rong kinh, theo dõi sát thời gian aPTT.',
                        'Lập thẻ cảnh báo bệnh lý von Willebrand cho bệnh nhân, hướng dẫn phác đồ sử dụng DDAVP và '
                        'thuốc ức chế tiêu sợi huyết khi chảy máu cấp.'],
  'kham': 'Niêm mạc hốc mũi có vết đông rỉ máu nhẹ, rải rác vài mảng bầm tím nông kích thước 1-2cm ở mặt trước cẳng '
          'chân, tim phổi bình thường.',
  'chan_doan': 'Bệnh von Willebrand thể nhẹ Type 1 có triệu chứng chảy máu niêm mạc.',
  'ke_hoach': 'Dùng thuốc Desmopressin DDAVP xịt mũi hoặc tiêm truyền tĩnh mạch để kích thích giải phóng vWF nội sinh, '
              'phối hợp acid tranexamic uống cầm máu niêm mạc, kiểm tra vWF:Ag và vWF:RCo.'},
 {'ten': 'xuất huyết giảm tiểu cầu huyết khối TTP',
  'nhom': 'người lớn',
  'dien_tien': 'cấp',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['thiếu hụt nghiêm trọng hoạt tính men phân cắt ADAMTS13 dưới 10 phần trăm',
            'thiếu máu tan máu vi mạch kèm xuất hiện mảnh vỡ hồng cầu schistocytes trên tiêu bản máu',
            'tiểu cầu máu ngoại vi giảm sâu gây xuất huyết kết hợp rối loạn thần kinh dao động'],
  'phu': ['sốt nhẹ đến sốt vừa không tìm thấy ổ nhiễm khuẩn',
          'chức năng thận suy giảm với protein niệu và tăng creatinin',
          'lú lẫn đau đầu lơ mơ hoặc co giật từng cơn'],
  'bien_the_kham': ['Bệnh nhân lơ mơ lú lẫn tiếp xúc chậm, da xanh xao củng mạc mắt vàng nhẹ, nhiều chấm và mảng xuất '
                    'huyết rải rác toàn thân, sốt 38.3 độ C.',
                    'Ý thức dao động lúc tỉnh lúc kích động, kết mạc mắt nhợt vàng rơm, ban xuất huyết chấm nốt dưới '
                    'da chi trên chi dưới, huyết áp 140/85 mmHg.',
                    'Khám thấy thiếu máu nặng da xanh niêm vàng, chấm xuất huyết niêm mạc vòm miệng, nhiệt độ 38.5 độ '
                    'C, phản xạ gân xương hai bên tăng nhẹ.',
                    'Bệnh nhân đau đầu dữ dội kèm lú lẫn định hướng không gian, da niêm nhợt nhạt ánh vàng chanh, xuất '
                    'huyết dưới da tự phát, nước tiểu sẫm màu.',
                    'Dấu hiệu thần kinh dao động rõ, nói ngọng thoáng qua, niêm mạc mắt nhợt vàng củng mạc, chấm xuất '
                    'huyết dày đặc ở hai cẳng chân.',
                    'Thể trạng lơ mơ, sốt 38 độ C, thiếu máu rõ rệt kèm hoàng đản nhẹ, mạch nhanh 110 l/p, rải rác các '
                    'vết bầm xuất huyết da tự nhiên.'],
  'bien_the_chan_doan': ['Xuất huyết giảm tiểu cầu huyết khối TTP cấp tính có tổn thương thần kinh.',
                         'Bệnh vi mạch huyết khối TTP giảm nặng hoạt tính men ADAMTS13.',
                         'Hội chứng huyết khối giảm tiểu cầu TTP nguy kịch cần thay huyết tương khẩn.',
                         'Theo dõi xuất huyết giảm tiểu cầu huyết khối TTP đầy đủ ngũ chứng lâm sàng.',
                         'Ban xuất huyết giảm tiểu cầu huyết khối TTP đợt bùng phát cấp tính.',
                         'Bệnh TTP cấp tính có thiếu máu tan máu vi mạch và suy giảm chức năng thận.'],
  'bien_the_ke_hoach': ['Chỉ định thay huyết tương PEX khẩn cấp thể tích 1-1.5 lần thể tích huyết tương với huyết '
                        'tương tươi đông lạnh, dùng methylprednisolone liều cao tĩnh mạch, tuyệt đối không truyền tiểu '
                        'cầu trừ khi xuất huyết đe dọa tính mạng.',
                        'Chuyển phòng Hồi sức tích cực thực hiện lọc huyết tương khẩn, tiêm kháng thể đơn dòng '
                        'Rituximab phối hợp thuốc ức chế men Caplacizumab nếu có điều kiện, lấy mẫu xét nghiệm định '
                        'lượng ADAMTS13 trước khi thay huyết tương.',
                        'Cấp cứu thay huyết tương mỗi ngày cho đến khi sốt giảm ý thức phục hồi tiểu cầu trên 150000 '
                        'trong hai ngày liên tiếp, bổ sung acid folic, theo dõi sát LDH máu.',
                        'Thực hiện đặt catheter tĩnh mạch trung tâm hai nòng tiến hành PEX cấp cứu, dùng corticoid '
                        'đường tĩnh mạch, theo dõi sát công thức máu và tiêu bản máu ngoại vi.',
                        'Theo dõi sát dấu hiệu thần kinh từng giờ, tiến hành huyết tương trị liệu cấp, truyền dịch duy '
                        'trì nước tiểu, kiểm tra creatinin và men gan định kỳ.',
                        'Bắt đầu quy trình cấp cứu TTP khẩn cấp bằng thay đổi huyết tương thể tích lớn, phối hợp '
                        'corticoid liều 1 mg/kg ngày, theo dõi sát số lượng mảnh vỡ hồng cầu.'],
  'kham': 'Bệnh nhân lơ mơ lú lẫn tiếp xúc chậm, da xanh xao củng mạc mắt vàng nhẹ, nhiều chấm và mảng xuất huyết rải '
          'rác toàn thân, sốt 38.3 độ C.',
  'chan_doan': 'Xuất huyết giảm tiểu cầu huyết khối TTP cấp tính có tổn thương thần kinh.',
  'ke_hoach': 'Chỉ định thay huyết tương PEX khẩn cấp thể tích 1-1.5 lần thể tích huyết tương với huyết tương tươi '
              'đông lạnh, dùng methylprednisolone liều cao tĩnh mạch, tuyệt đối không truyền tiểu cầu trừ khi xuất '
              'huyết đe dọa tính mạng.'},
 {'ten': 'bệnh bạch cầu lympho mạn tính CLL giai đoạn sớm',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['tăng số lượng tế bào lympho B tuyệt đối ngoại vi trên 5000 kéo dài trên ba tháng',
            'hạch ngoại vi nhiều nơi to đối xứng không đau mật độ chắc di động tốt',
            'dấu ấn miễn dịch tế bào dòng lympho B đồng biểu hiện CD5 CD19 và CD23'],
  'phu': ['thể trạng mệt mỏi mơ hồ giảm khả năng gắng sức',
          'sốt nhẹ về chiều không rõ nguyên nhân nhiễm trùng',
          'ra mồ hôi nhiều về ban đêm khi ngủ'],
  'bien_the_kham': ['Sờ thấy nhiều hạch vùng cổ hai bên và nách đường kính 1.5-2.5cm chắc trơn láng không đau di động '
                    'tốt, lách sờ mấp mé bờ sườn trái 1cm.',
                    'Khám hệ hạch phát hiện chuỗi hạch cổ trước sau và hạch bẹn hai bên to đối xứng kích thước 2cm '
                    'không nóng đỏ không dính nhau, gan không to.',
                    'Thể trạng tương đối tốt, hạch góc hàm và hạch thượng đòn phải to kích thước 1.5cm mật độ chắc đàn '
                    'hồi, lách to nhẹ dưới bờ sườn.',
                    'Hạch nách hai bên to đối xứng không đau khi nắn, da niêm mạc hồng hào, tim phổi bình thường, họng '
                    'không loét viêm.',
                    'Khám thấy cụm hạch cổ hai bên mềm chắc ranh giới rõ ràng không sưng đau, mạch 76 l/p, bụng mềm '
                    'lách không to qua sờ nắn lâm sàng.',
                    'Phát hiện nhiều hạch cổ và hạch nách hai bên dạng chuỗi hạt kích thước 1-2cm, niêm mạc mắt hồng, '
                    'không có ban xuất huyết ngoài da.'],
  'bien_the_chan_doan': ['Bệnh bạch cầu lympho mạn tính CLL giai đoạn sớm Rai giai đoạn I hoặc Binet A.',
                         'Bạch cầu lympho mạn tính CLL thể không triệu chứng tiến triển chậm.',
                         'Lơ xê mi kinh dòng lympho CLL giai đoạn ổn định theo dõi ngoại trú.',
                         'Bệnh bạch cầu mạn dòng lympho CLL đồng biểu hiện CD5 và CD23.',
                         'Hội chứng tăng lympho mạn tính tế bào B nghi ngờ bệnh bạch cầu lympho mạn tính CLL.',
                         'Bạch cầu lympho mạn tính CLL giai đoạn sớm chưa có chỉ định điều trị đặc hiệu.'],
  'bien_the_ke_hoach': ['Chiến lược theo dõi và chờ đợi Watch and Wait, xét nghiệm công thức máu định kỳ mỗi 3 tháng, '
                        'làm xét nghiệm di truyền tế bào tìm đột biến gen IGHV và đột biến mất đoạn del 17p.',
                        'Hẹn tái khám định kỳ theo dõi tốc độ nhân đôi số lượng lympho máu, tư vấn tiêm phòng cúm và '
                        'phế cầu phòng ngừa nhiễm khuẩn thứ phát, chưa cần hóa trị.',
                        'Chỉ định đếm tế bào dòng chảy xác định dấu ấn miễn dịch CD5 CD19 CD20 CD23, siêu âm ổ bụng '
                        'đánh giá kích thước lách và hạch sâu trong ổ bụng.',
                        'Tư vấn giải thích bản chất diễn tiến chậm của bệnh, kiểm tra toàn diện các chỉ số Binet và '
                        'Rai, theo dõi triệu chứng B như sụt cân sốt ra mồ hôi đêm.',
                        'Đánh giá định kỳ chức năng gan thận công thức máu toàn phần, hướng dẫn bệnh nhân tự kiểm tra '
                        'phát hiện hạch to nhanh hoặc các dấu hiệu nhiễm trùng.',
                        'Duy trì theo dõi lâm sàng không can thiệp thuốc độc tế bào, kiểm tra huyết đồ mỗi quý, chuyển '
                        'viện chuyên khoa Huyết học khi có dấu hiệu tiến triển bệnh.'],
  'kham': 'Sờ thấy nhiều hạch vùng cổ hai bên và nách đường kính 1.5-2.5cm chắc trơn láng không đau di động tốt, lách '
          'sờ mấp mé bờ sườn trái 1cm.',
  'chan_doan': 'Bệnh bạch cầu lympho mạn tính CLL giai đoạn sớm Rai giai đoạn I hoặc Binet A.',
  'ke_hoach': 'Chiến lược theo dõi và chờ đợi Watch and Wait, xét nghiệm công thức máu định kỳ mỗi 3 tháng, làm xét '
              'nghiệm di truyền tế bào tìm đột biến gen IGHV và đột biến mất đoạn del 17p.'},
 {'ten': 'đau tủy xương đa u tủy xương Multiple Myeloma',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['đau xương cột sống và xương sườn kéo dài tăng khi vận động',
            'hình ảnh tiêu xương đục lỗ hình đột dập trên phim X quang xương sọ hoặc chậu',
            'tăng globulin miễn dịch đơn dòng trong huyết thanh hoặc protein Bence Jones nước tiểu'],
  'phu': ['thiếu máu đẳng sắc kéo dài kèm mệt mỏi',
          'tăng canxi máu gây táo bón chán ăn và lú lẫn',
          'suy giảm chức năng thận với creatinin máu tăng cao'],
  'bien_the_kham': ['Ấn đau chói các gai sống thắt lưng L2-L4 và các cung xương sườn hai bên, da niêm mạc nhợt nhạt '
                    'rõ, không sờ thấy u cục phần mềm gồ trên da.',
                    'Bệnh nhân đi lại khó khăn do đau lưng và đau khung chậu, gõ đau nhẹ vùng cột sống thắt lưng, niêm '
                    'mạc mắt nhợt, thể trạng mệt mỏi.',
                    'Khám thấy hạn chế vận động cột sống thắt lưng do đau, ấn đau các xương dài chi trên chi dưới, '
                    'tiếng tim mờ, huyết áp 135/85 mmHg.',
                    'Da xanh niêm nhợt, ấn dọc các đốt sống ngực và thắt lưng có điểm đau chói rõ, lách gan không to, '
                    'mạch 88 lần/phút.',
                    'Cử động xoay người gây đau nhức sâu trong xương sườn và cột sống, niêm mạc mắt trắng bợt, không '
                    'sờ thấy hạch to ngoại biên.',
                    'Bệnh nhân gầy sút cân, đi đứng chậm chạp vì đau xương chậu, ấn đau vùng xương ức và cột sống thắt '
                    'lưng, niêm mạc nhợt nhạt.'],
  'bien_the_chan_doan': ['Bệnh đa u tủy xương Multiple Myeloma giai đoạn tiến triển có tổn thương xương tiêu hủy.',
                         'Đau tủy xương Kahler đa u tủy xương biến chứng suy thận và thiếu máu.',
                         'Đa u tủy xương Multiple Myeloma tăng canxi máu và tiêu xương đa ổ.',
                         'Bệnh lý tương bào ác tính Multiple Myeloma có tăng protein đơn dòng huyết thanh.',
                         'Theo dõi đa u tủy xương Multiple Myeloma đợt gãy xương bệnh lý hoặc đau xương mạn.',
                         'Đa u tủy xương Multiple Myeloma thể tiết kháng thể chuỗi nhẹ có tổn thương thận.'],
  'bien_the_ke_hoach': ['Chụp X-quang xương toàn thân hoặc CT liều thấp toàn thân tìm ổ tiêu xương, điện di protein '
                        'huyết thanh và nước tiểu tìm đỉnh đơn dòng M-spike, làm sinh thiết tủy xương xác định tỷ lệ '
                        'tương bào.',
                        'Kiểm tra chức năng thận creatinin canxi máu toàn phần và canxi ion hóa, bù dịch đường tĩnh '
                        'mạch kiểm soát tăng canxi máu, dùng thuốc nhóm Bisphosphonate hoặc Denosumab bảo vệ xương.',
                        'Định lượng chuỗi nhẹ tự do huyết thanh sFLC, xét nghiệm beta 2-microglobulin đánh giá phân '
                        'giai đoạn ISS, hội chẩn phác đồ điều trị ức chế proteasome Bortezomib kết hợp Dexamethasone.',
                        'Chỉ định đo tủy đồ sinh thiết gai chậu, điện di miễn dịch cố định, dùng thuốc giảm đau phù '
                        'hợp tránh NSAID hại thận, lập kế hoạch đánh giá ghép tế bào gốc tự thân.',
                        'Chụp cộng hưởng từ MRI cột sống tầm soát chèn ép tủy sống do sụp lún đốt sống, bù dịch natri '
                        'clorid 0.9% đường truyền, kiểm soát huyết áp và đường huyết.',
                        'Làm thủ tục nhập khoa Huyết học, hoàn thiện chẩn đoán CRAB của bệnh đa u tủy xương, bắt đầu '
                        'liệu pháp đích kết hợp thuốc điều hòa miễn dịch.'],
  'kham': 'Ấn đau chói các gai sống thắt lưng L2-L4 và các cung xương sườn hai bên, da niêm mạc nhợt nhạt rõ, không sờ '
          'thấy u cục phần mềm gồ trên da.',
  'chan_doan': 'Bệnh đa u tủy xương Multiple Myeloma giai đoạn tiến triển có tổn thương xương tiêu hủy.',
  'ke_hoach': 'Chụp X-quang xương toàn thân hoặc CT liều thấp toàn thân tìm ổ tiêu xương, điện di protein huyết thanh '
              'và nước tiểu tìm đỉnh đơn dòng M-spike, làm sinh thiết tủy xương xác định tỷ lệ tương bào.'},
 {'ten': 'u lympho Hodgkin hạch cổ nách giai đoạn sớm',
  'nhom': 'cả hai',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['hạch to đơn độc hoặc từng chùm ở vùng cổ thượng đòn mật độ chắc như cao su không đau',
            'ngứa da dai dẳng toàn thân không đáp ứng thuốc chống dị ứng thông thường',
            'đau nhức tại vị trí hạch xuất hiện đặc trưng sau khi uống rượu hoặc bia'],
  'phu': ['sốt chu kỳ kiểu Pel-Ebstein ngắt quãng vài ngày rồi hạ',
          'ra mồ hôi nhiều ban đêm ướt đẫm áo gối',
          'gầy sút cân trên mười phần trăm trọng lượng cơ thể không rõ lý do'],
  'bien_the_kham': ['Sờ thấy khối hạch thượng đòn trái và dọc cơ ức đòn chũm kích thước 3x4cm mật độ chắc đàn hồi '
                    'không nóng đỏ không đau dính lỏng lẻo, lách không to.',
                    'Cụm hạch cổ dưới bên phải to gồ dưới da kích thước 2.5cm chắc không đau khi nắn, da vùng cổ bình '
                    'thường, khám họng không phát hiện sưng amidan.',
                    'Hạch nách trái to đường kính 3cm mật độ chắc như cao su di động được dưới tay, không có ổ loét '
                    'ngoài da, củng mạc mắt trong.',
                    'Khám thấy khối hạch vùng cổ trước to tròn ranh giới rõ ràng nắn không đau, bệnh nhân khai đau '
                    'nhức tại khối hạch sau uống bia, tim phổi bình thường.',
                    'Hạch thượng đòn và hạch cổ bên kích thước 3cm chắc không dính da, sờ thấy cực dưới lách to nhẹ '
                    'dưới bờ sườn, hạch ngoại biên vùng bẹn không to.',
                    'Cụm hạch cổ nách kích thước 2-3cm tập trung thành chuỗi chắc đều không hóa mủ, thể trạng gầy sút '
                    'cân nhẹ, nhiệt độ cơ thể 37.8 độ C.'],
  'bien_the_chan_doan': ['U lympho Hodgkin thể xơ nốt giai đoạn sớm Ann Arbor giai đoạn I-II.',
                         'Bệnh Hodgkin hạch vùng cổ thượng đòn có triệu chứng ngứa da và đau sau uống rượu.',
                         'U lympho ác tính Hodgkin giai đoạn khu trú hạch cổ nách.',
                         'Theo dõi bệnh Hodgkin hạch ngoại biên nghi ngờ tế bào Reed-Sternberg.',
                         'U lympho Hodgkin giai đoạn IIA chưa có triệu chứng B toàn thân.',
                         'Bệnh Hodgkin thể giàu lympho bào vùng cổ nách giai đoạn sớm.'],
  'bien_the_ke_hoach': ['Sinh thiết trọn vẹn hạch cổ làm giải phẫu bệnh và nhuộm hóa mô miễn dịch tìm tế bào '
                        'Reed-Sternberg CD30 và CD15, chụp PET-CT toàn thân đánh giá giai đoạn Ann Arbor.',
                        'Phẫu thuật bóc trọn hạch ngoại biên gửi sinh thiết mô bệnh học, làm xét nghiệm công thức máu '
                        'tốc độ máu lắng ESR LDH, siêu âm khảo sát các nhóm hạch ngoại vi.',
                        'Chỉ định sinh thiết hạch chẩn đoán xác định, chụp CT scan ngực bụng chậu cản quang đánh giá '
                        'hạch trung thất và hạch ổ bụng, tư vấn phác đồ hóa trị ABVD.',
                        'Lập kế hoạch sinh thiết mở hạch cổ, xét nghiệm chức năng gan thận virus viêm gan B C và HIV, '
                        'hội chẩn chuyên khoa ung bướu huyết học.',
                        'Chụp PET-CT xác định giai đoạn tổn thương, đo chức năng hô hấp đánh giá thông khí phổi trước '
                        'khi dùng thuốc Bleomycin, tư vấn phác đồ điều trị chuẩn.',
                        'Khám chuyên khoa Huyết học Ung bướu, chuẩn bị can thiệp sinh thiết hạch tổn thương, đánh giá '
                        'chỉ số tiên lượng quốc tế IPS cho bệnh Hodgkin.'],
  'kham': 'Sờ thấy khối hạch thượng đòn trái và dọc cơ ức đòn chũm kích thước 3x4cm mật độ chắc đàn hồi không nóng đỏ '
          'không đau dính lỏng lẻo, lách không to.',
  'chan_doan': 'U lympho Hodgkin thể xơ nốt giai đoạn sớm Ann Arbor giai đoạn I-II.',
  'ke_hoach': 'Sinh thiết trọn vẹn hạch cổ làm giải phẫu bệnh và nhuộm hóa mô miễn dịch tìm tế bào Reed-Sternberg CD30 '
              'và CD15, chụp PET-CT toàn thân đánh giá giai đoạn Ann Arbor.'},
 {'ten': 'u lympho không Hodgkin thâm nhiễm hạch mạc treo',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['sờ thấy khối u chắc vùng bụng hoặc mạc treo ruột ranh giới không rõ',
            'đau bụng âm ỉ mơ hồ kèm cảm giác chướng đầy bụng sau ăn',
            'kết quả sinh thiết hạch mạc treo cho thấy tăng sinh dòng lympho ác tính phá vỡ cấu trúc hạch'],
  'phu': ['gầy sút cân nhanh chóng không rõ nguyên nhân',
          'rối loạn tiêu hóa đi ngoài phân lỏng xen lẫn táo bón',
          'sốt nhẹ kéo dài về chiều tối'],
  'bien_the_kham': ['Bụng mềm chướng nhẹ, sờ thấy khối vùng quanh rốn và hạ vị kích thước khoảng 5x6cm mật độ chắc gồ '
                    'ghề ít di động ấn tức nhẹ, không có phản ứng thành bụng.',
                    'Khám bụng phát hiện khối chắc sâu vùng mạc treo ruột ấn tức, gõ đục vùng khối u, nhu động ruột '
                    'bình thường, không có tuần hoàn bàng hệ.',
                    'Thể trạng gầy suy kiệt, sờ thấy mảng u chắc vùng mạn sườn trái và hố chậu, gan lách không sờ '
                    'chạm, hạch ngoại biên không sờ thấy.',
                    'Bụng đầy trướng hơi, sờ sâu thấy khối hạch mạc treo dính kết thành chùm vùng bụng giữa ranh giới '
                    'tương đối rõ, ấn đau tức âm ỉ.',
                    'Khối u chắc vùng hạ sườn trái lan vào mạc treo ruột kích thước 4x5cm, bụng không có cảm ứng phúc '
                    'mạc, tiếng óc ách dạ dày âm tính.',
                    'Khám thấy khối chắc không đau vùng quanh rốn sâu trong ổ bụng, niêm mạc nhợt vừa, mạch 82 l/p, '
                    'thể trạng sút 4kg trong hai tháng.'],
  'bien_the_chan_doan': ['U lympho không Hodgkin tế bào B lớn lan tỏa thâm nhiễm hạch mạc treo ruột.',
                         'U lympho không Hodgkin thể nang xâm lấn mạc treo ruột giai đoạn tiến triển.',
                         'Khối u hạch mạc treo ổ bụng do u lympho không Hodgkin Non-Hodgkin Lymphoma.',
                         'Theo dõi u lympho không Hodgkin ổ bụng thể thâm nhiễm mạc treo ruột.',
                         'U lympho ác tính không Hodgkin đường tiêu hóa và hạch mạc treo.',
                         'U lympho không Hodgkin hạch mạc treo ruột có hội chứng bán tắc ruột mạn tính.'],
  'bien_the_ke_hoach': ['Chụp CT scan hoặc MRI ổ bụng có cản quang đánh giá vị trí xâm lấn của khối u hạc mạc treo, '
                        'nội soi đại tràng và dạ dày tầm soát tổn thương niêm mạc, sinh thiết khối u dưới hướng dẫn '
                        'của CT hoặc phẫu thuật nội soi.',
                        'Sinh thiết kim lõi hoặc phẫu thuật nội soi lấy mẫu mô hạch mạc treo làm hóa mô miễn dịch CD20 '
                        'CD3 Ki67, xét nghiệm LDH máu và công thức máu toàn phần.',
                        'Chỉ định chụp PET-CT toàn thân xác định giai đoạn bệnh, hội chẩn đa chuyên khoa Ung bướu '
                        'Ngoại khoa Huyết học để bắt đầu phác đồ R-CHOP.',
                        'Đánh giá dinh dưỡng và hỗ trợ nâng đỡ thể trạng, xét nghiệm sinh hóa gan thận acid uric máu '
                        'dự phòng hội chứng ly giải u trước khi truyền hóa chất.',
                        'Chụp cắt lớp vi tính bụng ngực chậu, làm tủy đồ và sinh thiết tủy xương tầm soát thâm nhiễm '
                        'tủy, giải thích kế hoạch điều trị kháng thể đơn dòng rituximab.',
                        'Nhập viện chuyên khoa Huyết học Ung bướu, điều trị nội khoa nâng đỡ, lên lịch sinh thiết chẩn '
                        'đoán mô bệnh học và phác đồ điều trị miễn dịch hóa chất.'],
  'kham': 'Bụng mềm chướng nhẹ, sờ thấy khối vùng quanh rốn và hạ vị kích thước khoảng 5x6cm mật độ chắc gồ ghề ít di '
          'động ấn tức nhẹ, không có phản ứng thành bụng.',
  'chan_doan': 'U lympho không Hodgkin tế bào B lớn lan tỏa thâm nhiễm hạch mạc treo ruột.',
  'ke_hoach': 'Chụp CT scan hoặc MRI ổ bụng có cản quang đánh giá vị trí xâm lấn của khối u hạc mạc treo, nội soi đại '
              'tràng và dạ dày tầm soát tổn thương niêm mạc, sinh thiết khối u dưới hướng dẫn của CT hoặc phẫu thuật '
              'nội soi.'},
 {'ten': 'hội chứng tăng bạch cầu ái toan vô căn HES',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'huyết học',
  'da_duyet': False,
  'chinh': ['số lượng bạch cầu ái toan tuyệt đối trong máu trên 1500 tế bào kéo dài trên sáu tháng',
            'tổn thương nội tâm mạc xơ hóa van tim hoặc huyết khối vách tim do thâm nhiễm bạch cầu ái toan',
            'loại trừ hoàn toàn các nguyên nhân nhiễm ký sinh trùng dị ứng thuốc hoặc bệnh ác tính khác'],
  'phu': ['ho khan kéo dài kèm khó thở khò khè từng cơn',
          'phát ban dát sẩn ngứa ngáy tái phát dai dẳng trên da',
          'tê bì dị cảm đầu chi do viêm đa dây thần kinh ngoại biên'],
  'bien_the_kham': ['Nghe tim có tiếng thổi tâm thu 3/6 ở mỏm do hở van hai lá, phổi rải rác ran rít hai phế trường, '
                    'da cẳng tay có dát sẩn đỏ ngứa rải rác.',
                    'Khám thấy ban dát sẩn đỏ ngứa rải rác ở thân mình và tay chân, mạch 88 l/p, nghe tim tiếng T1 '
                    'đanh nhẹ và tiếng thổi tâm thu cơ năng, gan lách không to.',
                    'Phổi nghe thở khò khè nhẹ cuối thì thở ra, da có nhiều vết cào gãi ngứa do sẩn phù, giảm phản xạ '
                    'gân gót hai bên do tổn thương thần kinh ngoại biên.',
                    'Nghe tim phát hiện tiếng click mở van và tiếng thổi tâm thu vùng van hai lá, nhịp tim 92 l/p, da '
                    'có các dát hồng ban đỏ không vảy rải rác vùng ngực lưng.',
                    'Thể trạng mệt mỏi nhẹ, tiếng tim đều rõ có tiếng thổi hở van tim mới xuất hiện, rải rác ran ngáy '
                    'hai bên phổi, không phù chi dưới.',
                    'Da nhiều dát sẩn đỏ ngứa toàn thân, giảm cảm giác nông ngọn chi dưới hai bên, tim nhịp đều tần số '
                    '86 chu kỳ/phút, bụng mềm.'],
  'bien_the_chan_doan': ['Hội chứng tăng bạch cầu ái toan vô căn Hypereosinophilic Syndrome HES tổn thương tim mạch.',
                         'Hội chứng tăng bạch cầu ái toan HES có biểu hiện viêm nội tâm mạc Loeffler.',
                         'Hội chứng tăng bạch cầu ái toan vô căn HES biến chứng đa cơ quan da phổi thần kinh.',
                         'Theo dõi hội chứng tăng bạch cầu ái toan nguyên phát HES chưa rõ đột biến FIP1L1-PDGFRA.',
                         'Hội chứng tăng bạch cầu ái toan vô căn HES đợt tiến triển suy tim hở van hai lá.',
                         'Bệnh lý tăng bạch cầu ái toan toàn thân HES loại trừ nguyên nhân thứ phát.'],
  'bien_the_ke_hoach': ['Làm siêu âm tim qua thành ngực khảo sát độ dày vách tim và huyết khối buồng thất, xét nghiệm '
                        'đột biến gen dung hợp FIP1L1-PDGFRA bằng kỹ thuật RT-PCR hoặc FISH, bắt đầu dùng corticoid '
                        'Prednisolone đường uống.',
                        'Kiểm tra tủy đồ và sinh thiết tủy xương đánh giá tăng sinh dòng ái toan, xét nghiệm huyết '
                        'thanh học loại trừ giun sán giun lươn toxocara, chỉ định thuốc Imatinib nếu có đột biến gen '
                        'PDGFRA.',
                        'Xét nghiệm nồng độ troponin tim và men tim đánh giá tổn thương cơ tim, phối hợp thuốc kháng '
                        'histamin giảm ngứa, theo dõi sát số lượng bạch cầu ái toan tuyệt đối máu.',
                        'Đo điện cơ EMG đánh giá viêm đa dây thần kinh sợi trục ngoại biên, chụp CT ngực tầm soát thâm '
                        'nhiễm phổi, tối ưu hóa phác đồ ức chế miễn dịch bằng corticoid.',
                        'Chỉ định siêu âm Doppler tim định kỳ 3 tháng tầm soát xơ hóa nội tâm mạc, điều trị nâng đỡ '
                        'chống huyết khối tắc mạch nếu có tổn thương buồng tim.',
                        'Khám hội chẩn chuyên khoa Huyết học và Dị ứng Miễn dịch lâm sàng, khởi trị liệu pháp '
                        'corticoid liều 1 mg/kg ngày kết hợp bảo vệ niêm mạc dạ dày.'],
  'kham': 'Nghe tim có tiếng thổi tâm thu 3/6 ở mỏm do hở van hai lá, phổi rải rác ran rít hai phế trường, da cẳng tay '
          'có dát sẩn đỏ ngứa rải rác.',
  'chan_doan': 'Hội chứng tăng bạch cầu ái toan vô căn Hypereosinophilic Syndrome HES tổn thương tim mạch.',
  'ke_hoach': 'Làm siêu âm tim qua thành ngực khảo sát độ dày vách tim và huyết khối buồng thất, xét nghiệm đột biến '
              'gen dung hợp FIP1L1-PDGFRA bằng kỹ thuật RT-PCR hoặc FISH, bắt đầu dùng corticoid Prednisolone đường '
              'uống.'},
 {'ten': 'huyết khối tĩnh mạch chi trên do đặt buồng tiêm',
  'nhom': 'người lớn',
  'dien_tien': 'cấp',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['phù to căng tím toàn bộ cánh tay và bả vai cùng bên mang buồng truyền hóa chất catheter port',
            'tắc nghẽn hoàn toàn đường truyền dịch không thể bơm hoặc hút máu trào ngược qua buồng tiêm',
            'siêu âm mạch máu phát hiện huyết khối gây bít tắc lòng mạch dưới đòn hoặc mạch nách'],
  'phu': ['nổi rõ mạng lưới mao mạch bàng hệ tuần hoàn nông vùng ngực trước',
          'cảm giác nặng trịch mỏi nhức sâu trong cơ delta và hố nách',
          'dị cảm tê buốt mặt trong cánh tay lan xuống bàn tay'],
  'bien_the_kham': ['Cánh tay và cẳng tay phải sưng nề to rõ, chu vi cánh tay tăng 3cm so với bên trái, da căng bóng '
                    'ánh tím nhẹ, ấn tức dọc rãnh delta ngực vùng đặt buồng tiêm.',
                    'Phù mềm chi trên bên đặt catheter tĩnh mạch trung tâm, tĩnh mạch nông vùng ngực và cổ nổi ngoằn '
                    'ngoèo, mạch quay bắt rõ nhưng chi lạnh nhẹ.',
                    'Khám thấy tay phải sưng to đau nhức khi cử động, ấn dọc tĩnh mạch dưới đòn đau chói, buồng tiêm '
                    'sờ chắc không nóng đỏ nhiễm trùng ngoài da.',
                    'Cánh tay phải sưng căng tím sẫm hơn tay đối bên, tuần hoàn bàng hệ tĩnh mạch vùng vai ngực cùng '
                    'bên giãn rõ, không có dấu hoại tử đầu ngón.',
                    'Phù nề một bên tay sau thủ thuật đặt catheter buồng tiêm 2 tuần, cánh tay căng tức nặng, mạch '
                    'quay đều rõ 82 l/p, SpO2 đầu chi 98%.',
                    'Sưng nề toàn bộ cánh tay và bàn tay phải, đo chênh lệch vòng cánh tay 3.5cm, da ấm tím nhẹ, ấn '
                    'đau rát vùng mỏm cùng vai và xương đòn.'],
  'bien_the_chan_doan': ['Huyết khối tĩnh mạch sâu chi trên cấp tính liên quan đặt buồng tiêm truyền catheter.',
                         'Tắc huyết khối tĩnh mạch nách dưới đòn do biến chứng catheter buồng tiêm tĩnh mạch.',
                         'Huyết khối tĩnh mạch chi trên thứ phát sau đặt catheter buồng truyền hóa chất.',
                         'Theo dõi huyết khối tĩnh mạch sâu chi trên có tắc nghẽn dòng chảy buồng tiêm.',
                         'Huyết khối tắc mạch tĩnh mạch dưới đòn cấp do dụng cụ đặt trong lòng mạch.',
                         'Huyết khối tĩnh mạch chi trên liên quan buồng tiêm truyền đang điều trị ung thư.'],
  'bien_the_ke_hoach': ['Làm siêu âm Doppler mạch máu chi trên cấp cứu xác định vị trí và mức độ tắc nghẽn tĩnh mạch, '
                        'bắt đầu dùng thuốc chống đông trọng lượng phân tử thấp LMWH Enoxaparin hoặc DOAC, đánh giá '
                        'chỉ định rút buồng tiêm nếu có nhiễm trùng hoặc thất bại chống đông.',
                        'Chỉ định siêu âm Doppler mạch máu vùng cổ ngực nách, dùng kháng đông Enoxaparin tiêm dưới da '
                        'liều 1 mg/kg mỗi 12 giờ, chụp CT mạch máu ngực nếu nghi ngờ huyết khối lan vào tĩnh mạch chủ '
                        'trên.',
                        'Bắt đầu điều trị thuốc chống đông đường uống Rivaroxaban hoặc Apixaban, kê cao tay tổn thương '
                        'giảm phù nề, xét nghiệm đông máu D-dimer chức năng đông máu cơ bản.',
                        'Theo dõi sát dấu hiệu phù nề chi trên và tầm soát thuyên tắc phổi PE, duy trì thuốc chống '
                        'đông ít nhất 3 tháng, hội chẩn bác sĩ ung bướu về việc sử dụng buồng tiêm.',
                        'Thực hiện siêu âm mạch máu xác định kích thước huyết khối, dùng thuốc chống đông chuẩn, hướng '
                        'dẫn bệnh nhân theo dõi dấu hiệu đau ngực khó thở thuyên tắc mạch phổi.',
                        'Nhập viện theo dõi điều trị chống đông tích cực, đánh giá khả năng thông catheter buồng '
                        'truyền, hội chẩn ngoại mạch máu nếu huyết khối tiến triển lan rộng.'],
  'kham': 'Cánh tay và cẳng tay phải sưng nề to rõ, chu vi cánh tay tăng 3cm so với bên trái, da căng bóng ánh tím '
          'nhẹ, ấn tức dọc rãnh delta ngực vùng đặt buồng tiêm.',
  'chan_doan': 'Huyết khối tĩnh mạch sâu chi trên cấp tính liên quan đặt buồng tiêm truyền catheter.',
  'ke_hoach': 'Làm siêu âm Doppler mạch máu chi trên cấp cứu xác định vị trí và mức độ tắc nghẽn tĩnh mạch, bắt đầu '
              'dùng thuốc chống đông trọng lượng phân tử thấp LMWH Enoxaparin hoặc DOAC, đánh giá chỉ định rút buồng '
              'tiêm nếu có nhiễm trùng hoặc thất bại chống đông.'},
 {'ten': 'viêm nội tâm mạc nhiễm khuẩn bán cấp Osler',
  'nhom': 'người lớn',
  'dien_tien': 'cấp',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['tiếng thổi tim mới xuất hiện hoặc thay đổi tính chất kèm sốt dai dẳng kéo dài',
            'tổn thương nốt Osler đau ở đầu ngón tay ngón chân hoặc dát xuất huyết Janeway lòng bàn tay',
            'siêu âm tim qua thành ngực hoặc thực quản thấy khối sùi di động trên van tim'],
  'phu': ['xuất huyết kết mạc mắt dạng vệt hoặc tổn thương võng mạc Roth',
          'thiếu máu mức độ vừa lách to sờ thấy mấp mé bờ sườn',
          'tiểu máu vi thể khi xét nghiệm tổng phân tích nước tiểu'],
  'bien_the_kham': ['Sốt 38.4 độ C, nghe tim phát hiện tiếng thổi tâm thu mới 3/6 ở mỏm tim lan nách, đầu ngón tay có '
                    'nốt Osler gồ nhỏ màu đỏ ấn đau, kết mạc mắt có vệt xuất huyết.',
                    'Khám thấy tiếng thổi tâm trương 2/6 bờ trái xương ức, lòng bàn tay có các dát đỏ Janeway phẳng '
                    'không đau, củng mạc mắt không vàng, lách to độ 1.',
                    'Bệnh nhân sốt ngắt quãng kéo dài 3 tuần, nhịp tim nhanh 102 l/p, tiếng thổi toàn tâm thu thô ráp '
                    'vùng van hai lá, rải rác vệt xuất huyết dưới móng tay dạng mảnh vụn.',
                    'Khám tim thấy tiếng thổi thay đổi rõ so với tiền sử bệnh, nốt Osler đầu ngón tay cái sưng đau '
                    'nhẹ, sốt 38 độ C, thiếu máu da xanh niêm mạc nhạt.',
                    'Sắc diện mệt mỏi sốt âm ỉ, nghe tim tiếng T1 mờ kèm tiếng thổi tâm thu 3/6 tại ổ van hai lá, lòng '
                    'bàn chân có dát Janeway màu tím đỏ, lách sờ chạm.',
                    'Tiếng thổi tim mới xuất hiện ở khoang liên sườn 2 phải, sốt dai dẳng về chiều, xuất huyết dạng '
                    'vệt sợi huyết dưới móng tay, hạch cổ không to.'],
  'bien_the_chan_doan': ['Viêm nội tâm mạc nhiễm khuẩn bán cấp bệnh Osler trên nền bệnh van tim thoái hóa.',
                         'Viêm nội tâm mạc nhiễm trùng bán cấp Osler biến chứng hở van hai lá cấp.',
                         'Nhiễm khuẩn nội tâm mạc bán cấp có khối sùi van tim và nốt Osler ngoại vi.',
                         'Theo dõi viêm nội tâm mạc nhiễm khuẩn bán cấp Osler theo tiêu chuẩn Duke cải tiến.',
                         'Viêm nội tâm mạc nhiễm trùng do liên cầu khuẩn Viridans thể bán cấp tính.',
                         'Bệnh Osler viêm nội tâm mạc bán cấp có biểu hiện tổn thương miễn dịch da niêm mạc.'],
  'bien_the_ke_hoach': ['Cấy máu ít nhất 3 bộ tại các vị trí tiêm tĩnh mạch khác nhau trước khi dùng kháng sinh, làm '
                        'siêu âm tim qua thực quản TEE đánh giá kích thước sùi và thủng van, bắt đầu kháng sinh tĩnh '
                        'mạch diệt khuẩn liều cao Ceftriaxone phối hợp Gentamicin hoặc Ampicillin.',
                        'Chỉ định cấy máu tìm vi khuẩn hiếu khí và kỵ khí, làm siêu âm tim qua thành ngực và qua thực '
                        'quản khẩn, điều trị kháng sinh đường tiêm tĩnh mạch kéo dài 4-6 tuần.',
                        'Nhập viện khoa Tim mạch hoặc Truyền nhiễm, theo dõi điện tim tầm soát block dẫn truyền do áp '
                        'xe quanh vòng van, hội chẩn phẫu thuật tim hở nếu sùi lớn trên 10mm hoặc suy tim tiến triển.',
                        'Kiểm tra chức năng thận công thức máu lắng CRP mỗi tuần, cấy máu lại sau 48-72 giờ đánh giá '
                        'đáp ứng tiệt trùng máu, dùng kháng sinh phối hợp đủ liều.',
                        'Hoàn thiện các tiêu chuẩn Duke chẩn đoán viêm nội tâm mạc nhiễm khuẩn, siêu âm tim đánh giá '
                        'chức năng tống máu thất trái, hướng dẫn vệ sinh răng miệng dự phòng tái phát.',
                        'Điều trị nội trú dùng kháng sinh tĩnh mạch phổ rộng theo kháng sinh đồ, chụp CT sọ não loại '
                        'trừ thuyên tắc mạch não do mảnh sùi trôi dạt.'],
  'kham': 'Sốt 38.4 độ C, nghe tim phát hiện tiếng thổi tâm thu mới 3/6 ở mỏm tim lan nách, đầu ngón tay có nốt Osler '
          'gồ nhỏ màu đỏ ấn đau, kết mạc mắt có vệt xuất huyết.',
  'chan_doan': 'Viêm nội tâm mạc nhiễm khuẩn bán cấp bệnh Osler trên nền bệnh van tim thoái hóa.',
  'ke_hoach': 'Cấy máu ít nhất 3 bộ tại các vị trí tiêm tĩnh mạch khác nhau trước khi dùng kháng sinh, làm siêu âm tim '
              'qua thực quản TEE đánh giá kích thước sùi và thủng van, bắt đầu kháng sinh tĩnh mạch diệt khuẩn liều '
              'cao Ceftriaxone phối hợp Gentamicin hoặc Ampicillin.'},
 {'ten': 'bệnh cơ tim phì đại không tắc nghẽn',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['vách liên thất hoặc thành sau thất trái dày đồng tâm trên 15mm không giải thích được do tăng huyết áp',
            'chênh áp đường ra thất trái khi nghỉ và khi làm nghiệm pháp Valsalva dưới 30 mmHg',
            'đoạn ST chênh xuống và sóng T âm sâu khổng lồ ở các chuyển đạo trước tim V4-V6 trên điện tâm đồ'],
  'phu': ['khó thở khi gắng sức kèm đau thắt ngực không điển hình',
          'hồi hộp đánh trống ngực hoặc ngất thiu thoáng qua',
          'tiền sử gia đình có người đột tử khi còn trẻ tuổi'],
  'bien_the_kham': ['Mỏm tim đập mạnh diện đập rộng ở khoang liên sườn 5 ngoài đường trung đòn trái, tiếng T4 nghe rõ '
                    'mỏm tim, không có tiếng thổi tống máu gia tăng khi làm nghiệm pháp đứng lên.',
                    'Khám thấy tiếng T1 T2 rõ, nghe được tiếng T4 trước tâm thu ổ van hai lá do nhĩ bóp tống máu vào '
                    'tâm thất phì đại cứng, không có tiếng thổi hẹp đường ra.',
                    'Mạch nảy bình thường không có dạng hai đỉnh, huyết áp 120/75 mmHg, mỏm tim đập nâng đầu ngón tay '
                    'khám, phổi thông khí trong không ran.',
                    'Tiếng tim đanh, T4 nghe rõ ở mỏm tim khi bệnh nhân nằm nghiêng trái, nhịp tim đều 74 l/p, không '
                    'phù chi dưới, tĩnh mạch cổ không nổi.',
                    'Diện tim không to trên gõ, nghe tim thấy tiếng ngựa phi nhĩ T4 rõ ràng, không có tiếng cọ màng '
                    'tim hay tiếng thổi tâm thu bệnh lý đáng kể.',
                    'Nhịp tim đều rõ tần số 72 chu kỳ/phút, mỏm tim đập ở khoang liên sườn 5 đường trung đòn, nghe rõ '
                    'T4 ở mỏm, huyết áp bình thường.'],
  'bien_the_chan_doan': ['Bệnh cơ tim phì đại không tắc nghẽn Hypertrophic Cardiomyopathy thể mỏm hoặc vách.',
                         'Bệnh cơ tim phì đại tiên phát non-obstructive HCM có nguy cơ rối loạn nhịp thất.',
                         'Bệnh cơ tim phì đại thể không tắc nghẽn đường ra thất trái có suy chức năng tâm trương.',
                         'Theo dõi bệnh cơ tim phì đại gia đình thể không có chênh áp buồng thất.',
                         'Bệnh cơ tim phì đại phì đại đồng tâm vách liên thất không tắc nghẽn đường tống máu.',
                         'Bệnh cơ tim phì đại không tắc nghẽn có triệu chứng đau ngực và khó thở gắng sức.'],
  'bien_the_ke_hoach': ['Làm siêu âm Doppler tim đánh giá độ dày các thành tim và đo chênh áp buồng thất qua nghiệm '
                        'pháp gắng sức, chụp MRI tim đánh giá xơ hóa cơ tim qua ngấm thuốc tương phản muộn LGE, dùng '
                        'thuốc chẹn beta giao cảm Metoprolol hoặc chẹn kênh canxi Verapamil.',
                        'Đo điện tâm đồ Holter 24-48 giờ tầm soát cơn nhịp nhanh thất kịch phát, tính thang điểm nguy '
                        'cơ đột tử HCM Risk-SCD 5 năm để quyết định cấy máy phá rung tự động ICD, khuyến cáo tránh vận '
                        'động thể lực cường độ cao thi đấu.',
                        'Kê đơn thuốc chẹn beta liều tối ưu kiểm soát nhịp tim và cải thiện thời gian đổ đầy tâm '
                        'trương thất trái, xét nghiệm di truyền tầm soát đột biến gen sarcomere cho bệnh nhân và thân '
                        'nhân bậc một.',
                        'Chỉ định chụp cộng hưởng từ tim xác định tỷ lệ sẹo xơ hóa vách tim, theo dõi chức năng tâm '
                        'trương thất trái, dặn dò bệnh nhân tránh mất nước và tránh các nghiệm pháp rặn mạnh.',
                        'Tư vấn chế độ sinh hoạt vừa sức, dùng thuốc chẹn beta giao cảm đều đặn hàng ngày, tái khám '
                        'định kỳ mỗi 6 tháng làm siêu âm tim và Holter điện tim.',
                        'Khám chuyên khoa Tim mạch sâu, đánh giá toàn diện nguy cơ loạn nhịp thất ác tính, xem xét chỉ '
                        'định đặt ICD phòng ngừa đột tử nguyên phát.'],
  'kham': 'Mỏm tim đập mạnh diện đập rộng ở khoang liên sườn 5 ngoài đường trung đòn trái, tiếng T4 nghe rõ mỏm tim, '
          'không có tiếng thổi tống máu gia tăng khi làm nghiệm pháp đứng lên.',
  'chan_doan': 'Bệnh cơ tim phì đại không tắc nghẽn Hypertrophic Cardiomyopathy thể mỏm hoặc vách.',
  'ke_hoach': 'Làm siêu âm Doppler tim đánh giá độ dày các thành tim và đo chênh áp buồng thất qua nghiệm pháp gắng '
              'sức, chụp MRI tim đánh giá xơ hóa cơ tim qua ngấm thuốc tương phản muộn LGE, dùng thuốc chẹn beta giao '
              'cảm Metoprolol hoặc chẹn kênh canxi Verapamil.'},
 {'ten': 'bệnh cơ tim giãn vô căn',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['giãn buồng thất trái hoặc cả bốn buồng tim kèm giảm nặng phân suất tống máu EF dưới 40 phần trăm',
            'loại trừ hoàn toàn bệnh mạch vành tắc nghẽn bệnh van tim tiên phát hoặc tăng huyết áp mạn tính',
            'rối loạn chức năng co bóp tâm thu toàn bộ thành tim trên siêu âm tim'],
  'phu': ['khó thở tăng dần khi gắng sức khó thở khi nằm đầu thấp',
          'phù mềm hai chi dưới gan to phản hồi gan tĩnh mạch cổ dương tính',
          'mệt mỏi suy kiệt giảm khả năng lao động sinh hoạt'],
  'bien_the_kham': ['Mỏm tim đập lan tỏa xuống khoang liên sườn 6 đường nách trước, nghe tim có tiếng ngựa phi T3 và '
                    'tiếng thổi tâm thu cơ năng 2/6 ở mỏm do giãn vòng van hai lá, tĩnh mạch cổ nổi tư thế 45 độ.',
                    'Khám thấy diện tim to toàn bộ, mỏm tim lệch trái và xuống dưới, tiếng tim T1 T2 mờ, tiếng T3 '
                    'gallop rõ ở mỏm, phù mềm ấn lõm hai mắt cá chân.',
                    'Nhịp tim nhanh 100 l/p, huyết áp thấp 95/65 mmHg, nghe hai đáy phổi có ran ẩm nhỏ hạt rải rác, '
                    'gan to dưới bờ sườn phải 2cm mật độ mềm ấn tức nhẹ.',
                    'Mỏm tim đập yếu lan rộng ra ngoài đường trung đòn trái, tiếng ngựa phi T3 nghe rõ khi bệnh nhân '
                    'nằm nghiêng trái, phản hồi gan tĩnh mạch cổ dương tính rõ rệt.',
                    'Thể trạng gầy mòn do suy tim mạn, phù nhẹ mu chân, nghe tim nhịp đều nhanh có tiếng T3 bù trừ, '
                    'huyết áp dao động thấp 100/60 mmHg.',
                    'Diện đục tim giãn rộng hai bên, nghe tim có tiếng thổi tâm thu nhẹ ở mỏm lan nách do hở hai lá cơ '
                    'năng, hai phế trường thông khí giảm đáy phổi.'],
  'bien_the_chan_doan': ['Bệnh cơ tim giãn vô căn Idiopathic Dilated Cardiomyopathy suy tim mạn phân suất tống máu '
                         'giảm NYHA III.',
                         'Bệnh cơ tim giãn vô căn phân suất tống máu giảm nặng EF dưới 35 phần trăm.',
                         'Bệnh cơ tim giãn vô căn có biến chứng rối loạn nhịp tim và suy tim ứ huyết.',
                         'Theo dõi bệnh cơ tim giãn vô căn giai đoạn tiến triển có chỉ định tái đồng bộ cơ tim CRT.',
                         'Bệnh cơ tim giãn nở tự phát suy tim toàn bộ phân suất tống máu giảm nặng.',
                         'Bệnh cơ tim giãn vô căn có nguy cơ cao hình thành huyết khối buồng tim.'],
  'bien_the_ke_hoach': ['Tối ưu hóa phác đồ điều trị suy tim tứ trụ bao gồm ức chế thụ thể neprilysin ARNI '
                        'Sacubitril/Valsartan, chẹn beta Metoprolol succinate, kháng aldosterone Spironolactone, và ức '
                        'chế SGLT2 Dapagliflozin.',
                        'Chụp mạch vành qua da loại trừ bệnh cơ tim do thiếu máu cục bộ, chụp MRI tim đánh giá mô học '
                        'cơ tim, dùng thuốc lợi tiểu quai Furosemide đường uống kiểm soát ứ huyết.',
                        'Đo điện tâm đồ 12 chuyển đạo đánh giá độ rộng phức bộ QRS xem xét chỉ định cấy máy tái đồng '
                        'bộ cơ tim kèm máy phá rung CRT-D, kiểm tra nồng độ NT-proBNP và điện giải đồ.',
                        'Tư vấn hạn chế muối ăn dưới 2g natri mỗi ngày, theo dõi cân nặng hàng ngày tại nhà phát hiện '
                        'ứ dịch sớm, điều chỉnh liều các thuốc điều trị suy tim nền tảng.',
                        'Làm siêu âm tim qua thành ngực định kỳ 3-6 tháng đánh giá kích thước buồng tim và EF, tầm '
                        'soát huyết khối mỏm thất trái dùng kháng đông nếu có chỉ định.',
                        'Đăng ký chương trình quản lý suy tim ngoại trú chuyên sâu, tập phục hồi chức năng tim mạch '
                        'vừa sức, theo dõi sát chức năng thận và kali máu.'],
  'kham': 'Mỏm tim đập lan tỏa xuống khoang liên sườn 6 đường nách trước, nghe tim có tiếng ngựa phi T3 và tiếng thổi '
          'tâm thu cơ năng 2/6 ở mỏm do giãn vòng van hai lá, tĩnh mạch cổ nổi tư thế 45 độ.',
  'chan_doan': 'Bệnh cơ tim giãn vô căn Idiopathic Dilated Cardiomyopathy suy tim mạn phân suất tống máu giảm NYHA '
               'III.',
  'ke_hoach': 'Tối ưu hóa phác đồ điều trị suy tim tứ trụ bao gồm ức chế thụ thể neprilysin ARNI Sacubitril/Valsartan, '
              'chẹn beta Metoprolol succinate, kháng aldosterone Spironolactone, và ức chế SGLT2 Dapagliflozin.'},
 {'ten': 'hội chứng Brugada typ 1 nguy cơ đột tử',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['đoạn ST chênh lên dạng vòm coved-type trên 2mm kết thúc bằng sóng T âm ở các chuyển đạo V1 V2 trên điện '
            'tâm đồ',
            'hình ảnh điện tim điển hình xuất hiện tự nhiên hoặc sau khi dùng thuốc chẹn kênh natri như ajmaline '
            'flecainide',
            'nguy cơ loạn nhịp thất đa hình thái rung thất kịch phát dẫn đến ngất hoặc đột tử trong khi ngủ'],
  'phu': ['tiền sử ngất đột ngột không có triệu chứng báo trước đặc biệt vào ban đêm',
          'cơn thở ngáy bất thường hoặc co giật lúc ngủ rạng sáng',
          'tiền sử gia đình có người thân đột tử không rõ nguyên nhân trước 45 tuổi'],
  'bien_the_kham': ['Khám thực thể tim mạch hoàn toàn bình thường, huyết áp 120/80 mmHg, nhịp tim đều 72 l/p, nghe tim '
                    'tiếng T1 T2 rõ không có tiếng thổi bệnh lý, không phù.',
                    'Bệnh nhân tỉnh táo tiếp xúc tốt, khám lâm sàng lồng ngực và tuần hoàn ngoại vi không phát hiện dị '
                    'tật hay tổn thương thực thể, nhịp tim đều rõ.',
                    'Thể trạng khỏe mạnh bình thường, nghe tim rõ không tiếng ngựa phi hay tiếng thổi bất thường, các '
                    'mạch ngoại vi bắt nảy đều hai bên.',
                    'Khám hệ tim mạch chưa ghi nhận bất thường về giải phẫu, huyết áp 115/75 mmHg, tim nhịp xoang đều '
                    '70 lần/phút, phổi trong bụng mềm.',
                    'Toàn thân không sốt, không có dấu hiệu suy tim ứ trệ, khám tim không nghe tiếng thổi hay tiếng '
                    'cọ, điện tim tại giường bộc lộ hình ảnh ST chênh vòm V1 V2.',
                    'Khám không thấy dấu hiệu tổn thương thực thể tại tim, sinh hiệu bình thường, không có dấu hiệu '
                    'thần kinh khu trú sau các cơn ngất thoáng qua.'],
  'bien_the_chan_doan': ['Hội chứng Brugada typ 1 nguy cơ cao có tiền sử ngất ngưng thở ban đêm.',
                         'Hội chứng Brugada typ 1 thể ST chênh vòm điển hình nguy cơ đột tử tim mạch.',
                         'Hội chứng rối loạn nhịp Brugada typ 1 có chỉ định cấy máy phá rung tự động ICD.',
                         'Theo dõi hội chứng Brugada typ 1 tự phát ghi nhận trên điện tâm đồ 12 chuyển đạo.',
                         'Hội chứng Brugada typ 1 có tính chất gia đình cần tầm soát người thân bậc một.',
                         'Bệnh lý kênh ion tim hội chứng Brugada typ 1 biểu hiện cơn ngất tái diễn.'],
  'bien_the_ke_hoach': ['Tư vấn cấy máy phá rung tự động ICD dưới da hoặc qua tĩnh mạch để phòng ngừa đột tử do loạn '
                        'nhịp thất, giáo dục tránh hoàn toàn các thuốc làm nặng thêm Brugada như thuốc chống trầm cảm '
                        '3 vòng thuốc tê nhóm Na-channel blocker.',
                        'Hướng dẫn hạ sốt tích cực khẩn cấp khi bị sốt cao bằng paracetamol vì sốt kích hoạt cơn rung '
                        'thất, xét nghiệm di truyền học tầm soát đột biến gen kênh natri SCN5A.',
                        'Đo điện tâm đồ chuyển đạo trước tim V1 V2 đặt cao hơn ở khoang liên sườn 2 và 3 để tăng độ '
                        'nhạy, đo Holter điện tim 24 giờ phát hiện ngoại tâm thu thất kích hoạt.',
                        'Cung cấp danh mục thuốc chống chỉ định trên trang web brugadadrugs.org cho bệnh nhân và gia '
                        'đình, dặn dò thân nhân học kỹ năng hồi sinh tim phổi cơ bản CPR.',
                        'Hội chẩn chuyên gia Điện sinh lý tim xem xét triệt đốt qua đường ống thông qua màng ngoài tim '
                        'nếu có các cơn bão điện rung thất tái phát, kiểm tra điện tâm đồ người thân trong gia đình.',
                        'Khám tim mạch chuyên sâu loạn nhịp, lập hồ sơ quản lý bệnh lý kênh ion di truyền, hẹn tái '
                        'khám kiểm tra định kỳ chức năng máy phá rung.'],
  'kham': 'Khám thực thể tim mạch hoàn toàn bình thường, huyết áp 120/80 mmHg, nhịp tim đều 72 l/p, nghe tim tiếng T1 '
          'T2 rõ không có tiếng thổi bệnh lý, không phù.',
  'chan_doan': 'Hội chứng Brugada typ 1 nguy cơ cao có tiền sử ngất ngưng thở ban đêm.',
  'ke_hoach': 'Tư vấn cấy máy phá rung tự động ICD dưới da hoặc qua tĩnh mạch để phòng ngừa đột tử do loạn nhịp thất, '
              'giáo dục tránh hoàn toàn các thuốc làm nặng thêm Brugada như thuốc chống trầm cảm 3 vòng thuốc tê nhóm '
              'Na-channel blocker.'},
 {'ten': 'hội chứng QT dài bẩm sinh',
  'nhom': 'cả hai',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['khoảng thời gian QT hiệu chỉnh QTc kéo dài trên 460ms ở nữ hoặc trên 450ms ở nam trên điện tâm đồ nhiều '
            'lần',
            'nguy cơ cao xuất hiện cơn nhịp nhanh thất xoắn đỉnh Torsades de Pointes gây ngất hoặc tử vong',
            'đột biến gen di truyền mã hóa các kênh ion kali hoặc natri ở màng tế bào cơ tim LQT1 LQT2 LQT3'],
  'phu': ['ngất đột ngột khi bị giật mình hoảng sợ bởi tiếng động lớn như tiếng chuông báo thức',
          'ngất xảy ra khi đang bơi lội hoặc vận động thể lực gắng sức mạnh',
          'tiền sử điếc thần kinh giác quan bẩm sinh trong hội chứng Jervell and Lange-Nielsen'],
  'bien_the_kham': ['Khám tim mạch bình thường ngoài cơn ngất, nhịp tim đều 68 l/p, huyết áp 110/70 mmHg, tiếng T1 T2 '
                    'nghe rõ không có tiếng thổi tim bệnh lý.',
                    'Thể trạng phát triển bình thường, thính lực bình thường loại trừ điếc bẩm sinh, khám tim không '
                    'thấy diện tim to hay tiếng cọ màng tim.',
                    'Bệnh nhân tỉnh táo hoàn toàn, nghe tim nhịp xoang đều tần số 65 chu kỳ/phút, không nghe tiếng '
                    'thổi tâm thu hay tâm trương, phổi không ran.',
                    'Khám lâm sàng tim mạch chưa ghi nhận dị tật cấu trúc tim, huyết áp 115/75 mmHg, mạch ngoại vi nảy '
                    'đều, không phù chi.',
                    'Nhịp tim chậm xoang nhẹ 60 l/p, khám thực thể trong giới hạn bình thường, đo điện tim tại phòng '
                    'khám thấy khoảng QTc kéo dài 490ms.',
                    'Sinh hiệu ổn định, khám đầu mặt cổ và tim phổi bình thường, không có dấu hiệu suy tim ứ trệ, khám '
                    'thần kinh không có liệt khu trú.'],
  'bien_the_chan_doan': ['Hội chứng QT dài bẩm sinh LQTS type 1 có cơn ngất khi gắng sức bơi lội.',
                         'Hội chứng khoảng QT kéo dài bẩm sinh LQTS type 2 khởi phát do tiếng động mạnh.',
                         'Hội chứng QT dài bẩm sinh LQTS có nguy cơ xoắn đỉnh và đột tử do tim.',
                         'Theo dõi hội chứng QT dài di truyền bẩm sinh thang điểm Schwartz trên 3.5 điểm.',
                         'Bệnh lý kênh ion màng tế bào tim hội chứng QT dài bẩm sinh LQTS.',
                         'Hội chứng QT kéo dài bẩm sinh thể Romano-Ward không kèm điếc giác quan.'],
  'bien_the_ke_hoach': ['Bắt đầu điều trị bằng thuốc chẹn beta giao cảm Propranolol hoặc Nadolol liều đầy đủ để rút '
                        'ngắn và ổn định thời kỳ tái cực, tránh hoàn toàn các thuốc làm kéo dài khoảng QT theo danh '
                        'mục crediblemeds.org.',
                        'Tư vấn cấy máy phá rung tự động ICD nếu bệnh nhân đã từng bị ngưng tuần hoàn hoặc ngất tái '
                        'diễn dù đã dùng đủ liều thuốc chẹn beta giao cảm.',
                        'Xét nghiệm di truyền học xác định type đột biến gen KCNQ1 KCNH2 SCN5A để định hướng điều trị '
                        'đặc hiệu theo kiểu gen, tầm soát điện tim cho tất cả người thân thế hệ thứ nhất.',
                        'Khuyến cáo kiêng tuyệt đối bơi lội một mình và thể thao đối kháng nặng, loại bỏ chuông báo '
                        'thức hoặc chuông điện thoại âm thanh lớn đột ngột trong phòng ngủ.',
                        'Kiểm tra định kỳ nồng độ kali và magie máu duy trì kali máu trên 4.0 mmol/L, đo điện tâm đồ '
                        'định kỳ đánh giá khoảng QTc khi chỉnh liều thuốc chẹn beta.',
                        'Lập kế hoạch theo dõi chuyên khoa nhịp học tim mạch, cấp thẻ thông tin cảnh báo bệnh lý QT '
                        'dài và danh sách thuốc chống chỉ định cho bệnh nhân.'],
  'kham': 'Khám tim mạch bình thường ngoài cơn ngất, nhịp tim đều 68 l/p, huyết áp 110/70 mmHg, tiếng T1 T2 nghe rõ '
          'không có tiếng thổi tim bệnh lý.',
  'chan_doan': 'Hội chứng QT dài bẩm sinh LQTS type 1 có cơn ngất khi gắng sức bơi lội.',
  'ke_hoach': 'Bắt đầu điều trị bằng thuốc chẹn beta giao cảm Propranolol hoặc Nadolol liều đầy đủ để rút ngắn và ổn '
              'định thời kỳ tái cực, tránh hoàn toàn các thuốc làm kéo dài khoảng QT theo danh mục crediblemeds.org.'},
 {'ten': 'block nhĩ thất độ 2 Mobitz 2',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['sóng P không dẫn ngắt quãng phức bộ QRS mà không có sự kéo dài dần của khoảng PR trước đó trên điện tâm '
            'đồ',
            'vị trí tổn thương nghẽn dẫn truyền nằm dưới nút nhĩ thất thường ở thân chùm His hoặc nhánh His',
            'nguy cơ rất cao tiến triển đột ngột thành block nhĩ thất hoàn toàn độ 3 gây vô tâm thu hoặc ngất '
            'Stokes-Adams'],
  'phu': ['hoa mắt chóng mặt choáng váng cảm giác hẫng hụt trong ngực',
          'mệt mỏi giảm khả năng vận động gắng sức do nhịp tim chậm gián đoạn',
          'cơn ngất thiu thoáng qua khi tim ngừng đập vài giây'],
  'bien_the_kham': ['Nhịp tim không đều, nghe tim phát hiện ngắt quãng mất một nhịp đập theo chu kỳ, nhịp cơ bản chậm '
                    '52 l/p, huyết áp 130/80 mmHg, không tiếng thổi bệnh lý.',
                    'Mạch quay bắt lúc có lúc mất nhịp, nghe tim tiếng T1 T2 rõ nhưng ngắt quãng đột ngột, tần số tim '
                    '50 lần/phút, phổi thông khí trong.',
                    'Khám thấy nhịp tim chậm không đều có khoảng lặng nghỉ nhịp, huyết áp 125/75 mmHg, không có phù '
                    'mắt cá chân, tĩnh mạch cổ không đập nảy.',
                    'Bệnh nhân than choáng váng khi ngồi dậy, nhịp tim nghe được khoảng 48 chu kỳ/phút có nhát ngắt '
                    'nhịp, tiếng T1 biến đổi cường độ nhẹ.',
                    'Nhịp tim chậm gián đoạn, bắt mạch thấy nhát đập bị hẫng nhịp rõ ràng, tiếng tim T1 T2 không đều, '
                    'không sờ thấy rung miu vùng trước tim.',
                    'Thể trạng tỉnh táo, nhịp tim nghe ngắt nhịp chu kỳ 3:2 hoặc 4:3, tần số thất trung bình 54 l/p, '
                    'bụng mềm gan lách không to.'],
  'bien_the_chan_doan': ['Block nhĩ thất độ 2 type Mobitz II có nguy cơ tiến triển block tim hoàn toàn.',
                         'Rối loạn dẫn truyền nhĩ thất block AV độ 2 Mobitz 2 có chỉ định cấy máy tạo nhịp tim.',
                         'Block nhĩ thất độ 2 Mobitz II kèm cơn ngất thiu thoáng qua thiếu máu não.',
                         'Theo dõi block nhĩ thất độ II kiểu Mobitz 2 tổn thương hệ dẫn truyền dưới nút.',
                         'Block nhĩ thất độ 2 Mobitz 2 có nhịp chậm thất có triệu chứng choáng váng.',
                         'Rối loạn nhịp tim chậm block nhĩ thất độ 2 Mobitz 2 giai đoạn cần can thiệp tim mạch.'],
  'bien_the_ke_hoach': ['Chỉ định cấy máy tạo nhịp tim vĩnh viễn hai buồng DDD để đảm bảo nhịp thất và phòng ngừa '
                        'ngưng tim đột ngột, ngừng ngay lập tức các thuốc làm chậm dẫn truyền nhĩ thất như chẹn beta '
                        'chẹn canxi digoxin nếu đang dùng.',
                        'Nhập viện theo dõi điện tim liên tục tại giường có gắn máy monitor theo dõi nhịp, chuẩn bị '
                        'sẵn sàng máy tạo nhịp tạm thời qua da hoặc qua đường tĩnh mạch nếu có ngưng thất.',
                        'Xét nghiệm điện giải đồ troponin tim đánh giá tổn thương thiếu máu cục bộ cơ tim vùng vách, '
                        'làm siêu âm tim đánh giá chức năng co bóp cơ tim.',
                        'Đặt đường truyền tĩnh mạch dự phòng, chuẩn bị thuốc Atropine và Isoproterenol hỗ trợ nhịp tim '
                        'cấp cứu khi có tụt nhịp tim nguy hiểm trước phẫu thuật cấy máy.',
                        'Hội chẩn bác sĩ chuyên khoa Nhịp tim can thiệp thực hiện cấy máy tạo nhịp tim vĩnh viễn theo '
                        'chỉ định loại I của các khuyến cáo tim mạch quốc tế.',
                        'Theo dõi sát dấu hiệu sinh tồn và điện tâm đồ monitor, hướng dẫn bệnh nhân nằm nghỉ ngơi tại '
                        'giường tránh vận động mạnh đột ngột gây té ngã ngất xỉu.'],
  'kham': 'Nhịp tim không đều, nghe tim phát hiện ngắt quãng mất một nhịp đập theo chu kỳ, nhịp cơ bản chậm 52 l/p, '
          'huyết áp 130/80 mmHg, không tiếng thổi bệnh lý.',
  'chan_doan': 'Block nhĩ thất độ 2 type Mobitz II có nguy cơ tiến triển block tim hoàn toàn.',
  'ke_hoach': 'Chỉ định cấy máy tạo nhịp tim vĩnh viễn hai buồng DDD để đảm bảo nhịp thất và phòng ngừa ngưng tim đột '
              'ngột, ngừng ngay lập tức các thuốc làm chậm dẫn truyền nhĩ thất như chẹn beta chẹn canxi digoxin nếu '
              'đang dùng.'},
 {'ten': 'block nhánh trái hoàn toàn mới xuất hiện',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['thời gian phức bộ QRS kéo dài trên 120ms kèm dạng sóng R rộng có khía chữ M ở các chuyển đạo V5 V6 I aVL '
            'trên điện tâm đồ',
            'sóng QS hoặc rS giãn rộng ở chuyển đạo V1 V2 kèm đoạn ST và sóng T biến đổi ngược hướng với phức bộ QRS',
            'dấu hiệu block nhánh trái hoàn toàn mới xuất hiện phản ánh tổn thương cơ tim cấp hoặc bệnh cơ tim xơ vữa '
            'tiến triển'],
  'phu': ['cảm giác tức nặng ngực mơ hồ khi gắng sức',
          'khó thở nhẹ khi leo cầu thang hoặc mang vác vật nặng',
          'tiếng tim thứ hai T2 tách đôi đảo ngược khi nghe tim'],
  'bien_the_kham': ['Nghe tim có tiếng T2 tách đôi đảo ngược nghẽn trễ van động mạch chủ đóng muộn hơn van động mạch '
                    'phổi khi thở ra, nhịp tim đều 78 l/p, huyết áp 135/85 mmHg.',
                    'Khám thấy tiếng T1 hơi mờ, tiếng T2 tách đôi nghịch thường nghe rõ nhất ở khoang liên sườn 2 bờ '
                    'trái xương ức, không có tiếng thổi tâm thu hay cọ màng tim.',
                    'Nhịp tim đều rõ tần số 80 chu kỳ/phút, mỏm tim đập ở khoang liên sườn 5 đường trung đòn trái, '
                    'không nghe tiếng ngựa phi, phổi thông khí trong.',
                    'Huyết áp 140/90 mmHg, nghe tim nhịp xoang đều có tiếng T2 tách đôi ngược chiều sinh lý, mạch quay '
                    'nảy đều hai bên, không có phù ngoại biên.',
                    'Khám tim thấy diện tim bình thường, tiếng tim thứ hai tách đôi nghịch thường, không có ran ẩm ran '
                    'rít ở hai phế trường, bụng mềm.',
                    'Bệnh nhân có cảm giác nặng ngực nhẹ, nhịp tim đều 76 lần/phút, khám thực thể ngoài tiếng T2 biến '
                    'đổi chưa thấy dấu hiệu ứ trệ tuần hoàn ngoại biên.'],
  'bien_the_chan_doan': ['Block nhánh trái hoàn toàn LBBB mới xuất hiện nghi ngờ bệnh mạch vành thiếu máu cục bộ.',
                         'Rối loạn dẫn truyền trong thất block nhánh trái hoàn toàn mới phát hiện trên điện tâm đồ.',
                         'Block nhánh trái hoàn toàn LBBB kèm theo dõi bệnh cơ tim do xơ vữa động mạch.',
                         'Theo dõi block nhánh trái hoàn toàn mới xuất hiện cần loại trừ hội chứng vành cấp tương '
                         'đương STEMI.',
                         'Block nhánh trái hoàn toàn LBBB biến đổi vận động nghịch thường vách liên thất.',
                         'Block nhánh trái hoàn toàn mới xuất hiện ở bệnh nhân tăng huyết áp có yếu tố nguy cơ tim '
                         'mạch.'],
  'bien_the_ke_hoach': ['Làm xét nghiệm men tim Troponin I hoặc Troponin T siêu nhạy định lượng nhiều lần để loại trừ '
                        'nhồi máu cơ tim cấp tương đương STEMI theo tiêu chuẩn Sgarbossa cải tiến, làm siêu âm tim '
                        'đánh giá vận động vùng vách liên thất và chức năng tâm thu thất trái.',
                        'Chỉ định chụp cắt lớp vi tính động mạch vành MSCT hoặc chụp mạch vành qua da khảo sát hệ mạch '
                        'vành, kiểm tra điện tâm đồ cũ để đối chiếu thời điểm xuất hiện block nhánh.',
                        'Đo siêu âm Doppler tim đánh giá độ mất đồng bộ co bóp giữa vách liên thất và thành sau thất '
                        'trái, tầm soát các bệnh lý van tim như hẹp van động mạch chủ.',
                        'Tối ưu hóa các thuốc kiểm soát huyết áp lipid máu statin và thuốc chống kết tập tiểu cầu nếu '
                        'phát hiện bệnh lý xơ vữa mạch vành nền tảng.',
                        'Đăng ký theo dõi ngoại trú chuyên khoa Tim mạch, thực hiện nghiệm pháp gắng sức bằng thuốc xạ '
                        'hình tưới máu cơ tim SPECT nếu nghi ngờ thiếu máu cục bộ.',
                        'Tư vấn giải thích ý nghĩa của block nhánh trái mới phát hiện, lên kế hoạch kiểm tra chức năng '
                        'tim định kỳ và tầm soát sớm các biến cố suy tim.'],
  'kham': 'Nghe tim có tiếng T2 tách đôi đảo ngược nghẽn trễ van động mạch chủ đóng muộn hơn van động mạch phổi khi '
          'thở ra, nhịp tim đều 78 l/p, huyết áp 135/85 mmHg.',
  'chan_doan': 'Block nhánh trái hoàn toàn LBBB mới xuất hiện nghi ngờ bệnh mạch vành thiếu máu cục bộ.',
  'ke_hoach': 'Làm xét nghiệm men tim Troponin I hoặc Troponin T siêu nhạy định lượng nhiều lần để loại trừ nhồi máu '
              'cơ tim cấp tương đương STEMI theo tiêu chuẩn Sgarbossa cải tiến, làm siêu âm tim đánh giá vận động vùng '
              'vách liên thất và chức năng tâm thu thất trái.'},
 {'ten': 'hội chứng suy nút xoang nhịp chậm xoang',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['nhịp chậm xoang dai dẳng dưới 50 lần một phút không tương thích với nhu cầu sinh lý của cơ thể',
            'xuất hiện các khoảng ngừng xoang hoặc block xoang nhĩ kéo dài trên 3 giây trên điện tâm đồ hoặc Holter',
            'kém đáp ứng tần số tim khi gắng sức thể lực do suy giảm chức năng tạo nhịp của nút xoang'],
  'phu': ['choáng váng xây xẩm mặt mày lảo đảo khi đi lại',
          'cơn ngất thiu thoáng qua hoặc ngã do tụt cung lượng tim tưới máu não',
          'mệt mỏi uể oải triền miên giảm tập trung chú ý'],
  'bien_the_kham': ['Nhịp tim chậm đều tần số 44 lần/phút, mạch quay bắt chậm nảy rõ, huyết áp 130/80 mmHg, tiếng T1 '
                    'T2 nghe rõ không tiếng thổi bệnh lý, bệnh nhân tỉnh táo.',
                    'Khám thấy nhịp tim chậm 46 l/p không tăng lên rõ rệt khi yêu cầu bệnh nhân vận động tại chỗ, mạch '
                    'cổ đập chậm đều, không có dấu phù ngoại vi.',
                    'Thể trạng mệt mỏi chậm chạp, mạch quay đều chậm 42 chu kỳ/phút, nghe tim nhịp xoang chậm tiếng '
                    'tim rõ, phổi trong không có ran ẩm.',
                    'Nhịp tim chậm 48 lần/phút, huyết áp đo được 125/75 mmHg, nghe tim không phát hiện âm thổi hay '
                    'tiếng cọ màng ngoài tim, gan lách bình thường.',
                    'Mạch chậm đều 45 l/p, da niêm hồng nhạt, không có dấu suy tim ứ trệ, bệnh nhân có biểu hiện '
                    'choáng váng nhẹ khi thay đổi tư thế nhanh.',
                    'Khám tim thấy nhịp chậm xoang đều 46 lần/phút, mạch cảnh đập chậm tương ứng, tim phổi nghe bình '
                    'thường, các chi ấm không run.'],
  'bien_the_chan_doan': ['Hội chứng suy nút xoang thể nhịp chậm xoang dai dẳng có triệu chứng choáng váng.',
                         'Bệnh lý nút xoang Sick Sinus Syndrome kèm khoảng ngừng xoang trên 3 giây.',
                         'Hội chứng suy nút xoang có cơn ngất thiu thoáng qua thiếu máu não cục bộ.',
                         'Theo dõi hội chứng suy nút xoang nhịp chậm xoang trơ với atropine.',
                         'Suy nút xoang nhịp chậm có giảm khả năng đáp ứng nhịp tim khi gắng sức thể lực.',
                         'Rối loạn tạo nhịp nút xoang Sick Sinus Syndrome có chỉ định cấy máy tạo nhịp tim.'],
  'bien_the_ke_hoach': ['Gắn máy ghi Holter điện tâm đồ 24-48 giờ để phát hiện các khoảng ngừng xoang và ghi nhận mối '
                        'tương quan giữa nhịp chậm với triệu chứng lâm sàng của bệnh nhân, rà soát và ngừng các thuốc '
                        'ức chế nút xoang như chẹn beta digoxin chẹn kênh canxi.',
                        'Chỉ định cấy máy tạo nhịp tim vĩnh viễn hai buồng DDD hoặc tạo nhịp nhĩ AAI để phục hồi tần '
                        'số tim sinh lý và ngăn ngừa ngất xỉu chấn thương.',
                        'Xét nghiệm hormone tuyến giáp TSH FT4 để loại trừ nguyên nhân suy giáp gây nhịp chậm xoang, '
                        'kiểm tra điện giải đồ đặc biệt là kali máu.',
                        'Làm siêu âm tim qua thành ngực đánh giá kích thước buồng nhĩ và chức năng tâm thu thất trái, '
                        'loại trừ các bệnh cơ tim thoái hóa đi kèm.',
                        'Đánh giá trắc nghiệm gắng sức điện tâm đồ thảm lăn để xác định mức độ bất toàn đáp ứng tần số '
                        'tim khi vận động thể lực.',
                        'Hội chẩn bác sĩ chuyên khoa Nhịp tim can thiệp, tư vấn bệnh nhân và gia đình về quy trình cấy '
                        'máy tạo nhịp tim và chế độ theo dõi sau thủ thuật.'],
  'kham': 'Nhịp tim chậm đều tần số 44 lần/phút, mạch quay bắt chậm nảy rõ, huyết áp 130/80 mmHg, tiếng T1 T2 nghe rõ '
          'không tiếng thổi bệnh lý, bệnh nhân tỉnh táo.',
  'chan_doan': 'Hội chứng suy nút xoang thể nhịp chậm xoang dai dẳng có triệu chứng choáng váng.',
  'ke_hoach': 'Gắn máy ghi Holter điện tâm đồ 24-48 giờ để phát hiện các khoảng ngừng xoang và ghi nhận mối tương quan '
              'giữa nhịp chậm với triệu chứng lâm sàng của bệnh nhân, rà soát và ngừng các thuốc ức chế nút xoang như '
              'chẹn beta digoxin chẹn kênh canxi.'},
 {'ten': 'hẹp van động mạch chủ thoái hóa vôi hóa tuổi già',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['tiếng thổi tâm thu tống máu hình quả trám thô ráp ở khoang liên sườn 2 bên phải xương ức lan lên hai động '
            'mạch cảnh vùng cổ',
            'vôi hóa dày cứng các lá van động mạch chủ làm giảm diện tích mở van dưới 1.0 cm2 trên siêu âm Doppler tim',
            'chênh áp trung bình qua van động mạch chủ tăng cao trên 40 mmHg kèm vận tốc đỉnh dòng chảy trên 4 m/s'],
  'phu': ['đau thắt ngực khi gắng sức dù mạch vành có thể không tắc nghẽn',
          'ngất thiu xảy ra đặc trưng ngay trong hoặc sau khi vận động gắng sức',
          'khó thở khi gắng sức do rối loạn đổ đầy tâm trương thất trái'],
  'bien_the_kham': ['Nghe tim có tiếng thổi tâm thu tống máu thô ráp 4/6 ở khoang liên sườn 2 bờ phải xương ức lan '
                    'mạnh lên động mạch cảnh hai bên, mạch cảnh nảy chậm chìm chậm parvus et tardus, tiếng T2 mờ mất '
                    'thành phần chủ.',
                    'Khám thấy tiếng thổi tâm thu tống máu mạnh kèm rung miu tâm thu ở khoang liên sườn 2 phải, mỏm '
                    'tim đập mạnh nâng đầu ngón tay, huyết áp 110/85 mmHg kẹp nhẹ.',
                    'Mạch quay nảy yếu và chậm, tiếng thổi tâm thu thô ráp hình quả trám khoang liên sườn 2 bên phải '
                    'xương ức lan dọc hai bờ cổ, T2 van chủ mờ.',
                    'Tiếng thổi tâm thu 3/6 thô ráp nghe rõ nhất ở đáy tim lan lên góc hàm phải, mỏm tim lệch nhẹ sang '
                    'trái, nghe có tiếng T4 ở mỏm do phì đại tâm thất.',
                    'Mạch ngoại vi nảy yếu chậm chạp, nghe tim thấy tiếng thổi tống máu mạnh khoang liên sườn 2 phải '
                    'lan lên cổ, huyết áp 115/80 mmHg, phổi không ran.',
                    'Khám phát hiện tiếng thổi tâm thu cơ học dạng thô ráp khoang liên sườn 2 phải, tiếng A2 mờ hẳn, '
                    'mạch cảnh hai bên đập yếu và trễ so với tiếng tim.'],
  'bien_the_chan_doan': ['Hẹp van động mạch chủ vôi hóa người cao tuổi mức độ nặng có triệu chứng lâm sàng đau ngực và '
                         'ngất.',
                         'Hẹp van động mạch chủ thoái hóa mức độ khít chênh áp qua van cao.',
                         'Hẹp van động mạch chủ vôi hóa tuổi già biến chứng phì đại thất trái và suy tim.',
                         'Theo dõi hẹp van động mạch chủ thoái hóa vôi hóa có chỉ định thay van TAVI.',
                         'Bệnh van động mạch chủ vôi hóa hẹp nặng diện tích lỗ van dưới 1cm2.',
                         'Hẹp van động mạch chủ vôi hóa tuổi già có nguy cơ đột tử khi gắng sức.'],
  'bien_the_ke_hoach': ['Làm siêu âm tim qua thành ngực khảo sát diện tích lỗ van động mạch chủ theo phương trình liên '
                        'tục và đo chênh áp qua van, hội chẩn hội đồng Tim mạch Heart Team đánh giá chỉ định thay van '
                        'động mạch chủ qua da TAVI hoặc phẫu thuật thay van tim hở SAVR.',
                        'Chụp cắt lớp vi tính đa dãy MSCT tim và mạch máu chủ chậu đánh giá giải phẫu vòng van và '
                        'đường vào mạch máu cho thủ thuật TAVI.',
                        'Chụp động mạch vành qua da khảo sát tổn thương xơ vữa mạch vành phối hợp trước khi can thiệp '
                        'van tim, dặn dò bệnh nhân tuyệt đối tránh vận động thể lực gắng sức nặng.',
                        'Tránh dùng các thuốc dãn mạch liều cao như ức chế men chuyển hoặc nitrat vì nguy cơ gây tụt '
                        'huyết áp nghiêm trọng do hẹp cố định đường tống máu.',
                        'Theo dõi sát các triệu chứng ngất đau ngực khó thở, làm điện tâm đồ tầm soát dày thất trái và '
                        'rối loạn dẫn truyền nhĩ thất do vôi hóa lan vào vòng van.',
                        'Khám chuyên khoa Phẫu thuật Tim mạch và Tim mạch Can thiệp, lập kế hoạch thay van nhân tạo để '
                        'phục hồi huyết động và kéo dài tuổi thọ cho bệnh nhân.'],
  'kham': 'Nghe tim có tiếng thổi tâm thu tống máu thô ráp 4/6 ở khoang liên sườn 2 bờ phải xương ức lan mạnh lên động '
          'mạch cảnh hai bên, mạch cảnh nảy chậm chìm chậm parvus et tardus, tiếng T2 mờ mất thành phần chủ.',
  'chan_doan': 'Hẹp van động mạch chủ vôi hóa người cao tuổi mức độ nặng có triệu chứng lâm sàng đau ngực và ngất.',
  'ke_hoach': 'Làm siêu âm tim qua thành ngực khảo sát diện tích lỗ van động mạch chủ theo phương trình liên tục và đo '
              'chênh áp qua van, hội chẩn hội đồng Tim mạch Heart Team đánh giá chỉ định thay van động mạch chủ qua da '
              'TAVI hoặc phẫu thuật thay van tim hở SAVR.'},
 {'ten': 'hở van động mạch chủ mạn tính',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['tiếng thổi tâm trương êm dịu hình giảm dần ở khoang liên sườn 3 bờ trái xương ức nghe rõ khi bệnh nhân '
            'ngồi nghiêng người ra trước thở ra hết',
            'huyết áp tâm thu tăng cao kèm huyết áp tâm trương giảm sâu tạo hiệu áp rộng trên 60 mmHg',
            'dòng phụt ngược tâm trương qua van động mạch chủ đo được trên siêu âm tim Doppler màu'],
  'phu': ['mạch nảy mạnh chìm sâu Corrigan mạch đập nẩy như búa nước',
          'cảm giác tim đập mạnh như trống đánh trong lồng ngực khi nằm nghỉ',
          'dấu hiệu nhấp nháy mạch mao mạch đầu móng tay Quincke'],
  'bien_the_kham': ['Nghe tim có tiếng thổi tâm trương 3/6 êm dịu ở ổ Erb khoang liên sườn 3 bờ trái xương ức lan dọc '
                    'bờ trái ức xuống mỏm, mỏm tim đập mạnh lan tỏa xuống khoang liên sườn 6, huyết áp 160/50 mmHg '
                    'hiệu áp rộng 110 mmHg, mạch Corrigan nảy mạnh chìm sâu.',
                    'Khám thấy tiếng thổi tâm trương êm dịu giảm dần ở bờ trái xương ức, huyết áp 150/45 mmHg, đầu '
                    'móng tay có dấu hiệu mạch đập Quincke nhấp nháy rõ, mạch quay bắt nảy vút rồi xẹp nhanh.',
                    'Mỏm tim đập lệch xuống dưới và sang trái, diện đập rộng, nghe tiếng thổi tâm trương êm tai ở ổ '
                    'van động mạch chủ 2 và mỏm tim có tiếng thổi Austin Flint rung nhẹ.',
                    'Hiệu số huyết áp rất rộng 155/50 mmHg, nghe rõ tiếng thổi tâm trương thì thở ra khi cúi người ra '
                    'trước, mạch cảnh hai bên đập dội mạnh theo từng nhịp co bóp.',
                    'Khám tuần hoàn thấy dấu hiệu búa nước mạch đập mạnh chìm sâu, tiếng T2 van chủ mờ, tiếng thổi tâm '
                    'trương thì đầu kéo dài ổ Erb, không có ran ở phổi.',
                    'Huyết áp 165/55 mmHg, nghe tim có tiếng thổi tâm trương tần số cao êm dịu dọc bờ trái xương ức, '
                    'mỏm tim tăng động đẩy mạnh vào lòng bàn tay khám.'],
  'bien_the_chan_doan': ['Hở van động mạch chủ mạn tính mức độ nặng có giãn buồng thất trái.',
                         'Hở van động mạch chủ mạn tính do thoái hóa van kèm quá tải thể tích thất trái.',
                         'Bệnh hở van động mạch chủ mạn tính phân suất tống máu bắt đầu giảm.',
                         'Theo dõi hở van động mạch chủ mạn tính mức độ nhiều có hiệu áp rộng.',
                         'Bệnh lý hở van động mạch chủ mạn tính có chỉ định phẫu thuật thay hoặc sửa van tim.',
                         'Hở van động mạch chủ mạn tính có tiếng thổi Austin Flint cơ năng ở mỏm tim.'],
  'bien_the_ke_hoach': ['Làm siêu âm Doppler tim định kỳ đo đường kính cuối tâm thu thất trái LVESD và đường kính cuối '
                        'tâm trương LVEDD cùng phân suất tống máu EF để xác định thời điểm mổ thay van chủ trước khi '
                        'cơ tim bị suy không hồi phục.',
                        'Chỉ định phẫu thuật thay van động mạch chủ hoặc sửa van khi LVESD trên 50mm hoặc EF dưới 50% '
                        'hoặc khi xuất hiện triệu chứng cơ năng suy tim.',
                        'Dùng thuốc hạ áp nhóm ức chế men chuyển hoặc thuốc chẹn kênh canxi dihydropyridine nifedipine '
                        'để giảm hậu tải thất trái trong thời gian chờ can thiệp phẫu thuật.',
                        'Chụp MRI tim đánh giá chính xác thể tích dòng hở phân số dòng hở Regurgitant Fraction nếu '
                        'siêu âm tim chưa đánh giá đầy đủ mức độ hở van.',
                        'Chụp động mạch vành tầm soát tổn thương trước phẫu thuật van tim ở bệnh nhân nam trên 40 tuổi '
                        'hoặc nữ sau mãn kinh.',
                        'Tư vấn phòng ngừa viêm nội tâm mạc nhiễm trùng bằng kháng sinh dự phòng trước các thủ thuật '
                        'răng miệng can thiệp, theo dõi sát siêu âm tim mỗi 6 tháng.'],
  'kham': 'Nghe tim có tiếng thổi tâm trương 3/6 êm dịu ở ổ Erb khoang liên sườn 3 bờ trái xương ức lan dọc bờ trái ức '
          'xuống mỏm, mỏm tim đập mạnh lan tỏa xuống khoang liên sườn 6, huyết áp 160/50 mmHg hiệu áp rộng 110 mmHg, '
          'mạch Corrigan nảy mạnh chìm sâu.',
  'chan_doan': 'Hở van động mạch chủ mạn tính mức độ nặng có giãn buồng thất trái.',
  'ke_hoach': 'Làm siêu âm Doppler tim định kỳ đo đường kính cuối tâm thu thất trái LVESD và đường kính cuối tâm '
              'trương LVEDD cùng phân suất tống máu EF để xác định thời điểm mổ thay van chủ trước khi cơ tim bị suy '
              'không hồi phục.'},
 {'ten': 'sa van hai lá biến chứng hở van nhẹ',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['tiếng click giữa tâm thu kèm theo tiếng thổi muộn cuối tâm thu nghe rõ ở mỏm tim',
            'hình ảnh một hoặc hai lá van hai lá di động sa vượt quá mặt phẳng vòng van vào tâm nhĩ trái trên 2mm '
            'trong thời kỳ tâm thu trên siêu âm tim',
            'dòng hở van hai lá mức độ nhẹ xuất hiện muộn ở nửa sau thời kỳ tâm thu'],
  'phu': ['cảm giác hồi hộp đánh trống ngực từng cơn không liên quan gắng sức',
          'đau nhói ngực thoáng qua vùng trước tim kéo dài vài giây rồi tự hết',
          'lo âu mệt mỏi nhẹ kèm hội chứng rối loạn thần kinh thực vật'],
  'bien_the_kham': ['Nghe tim có tiếng click giữa tâm thu sắc gọn theo sau bởi tiếng thổi tâm thu muộn 2/6 ở mỏm tim, '
                    'tiếng click và tiếng thổi dịch chuyển sớm hơn về phía T1 khi bệnh nhân đứng dậy hoặc làm nghiệm '
                    'pháp Valsalva.',
                    'Khám thấy tiếng click giữa tâm thu nghe rõ nhất ở mỏm khi nằm nghiêng trái, nhịp tim đều 76 l/p, '
                    'huyết áp 115/75 mmHg, không có tiếng ngựa phi hay ứ trệ tuần hoàn.',
                    'Mỏm tim đập ở vị trí bình thường khoang liên sườn 5 đường trung đòn trái, nghe tim phát hiện '
                    'tiếng click sắc nhọn giữa thì tâm thu kèm tiếng thổi hở van nhẹ cuối thì.',
                    'Bệnh nhân có thể trạng gầy cao ngực phẳng, nghe tim tiếng T1 T2 rõ kèm tiếng click tâm thu điển '
                    'hình của sa lá van, không có ran phổi.',
                    'Tiếng tim đều, có tiếng click tâm thu rõ ở mỏm lan nhẹ nách, tiếng thổi muộn nhẹ 1-2/6, nghiệm '
                    'pháp ngồi xổm làm tiếng click dịch chuyển muộn về phía T2.',
                    'Khám lâm sàng tim mạch ngoài tiếng click giữa tâm thu sắc gọn và tiếng thổi nhẹ ở mỏm tim thì các '
                    'cơ quan khác hoàn toàn bình thường, huyết áp ổn định.'],
  'bien_the_chan_doan': ['Hội chứng sa van hai lá Mitral Valve Prolapse biến chứng hở van hai lá nhẹ.',
                         'Sa lá sau van hai lá thể thoái hóa nhầy có hở van nhẹ không rối loạn huyết động.',
                         'Sa van hai lá có triệu chứng hồi hộp đánh trống ngực và đau ngực không điển hình.',
                         'Theo dõi hội chứng sa van hai lá Barlow biến chứng hở van hai lá mức độ nhẹ.',
                         'Sa van hai lá có tiếng click tâm thu và tiếng thổi muộn ổn định.',
                         'Hội chứng sa van hai lá tiên phát biến chứng hở van hai lá nhẹ bảo tồn chức năng tim.'],
  'bien_the_ke_hoach': ['Làm siêu âm tim qua thành ngực khảo sát hình thái lá van độ dày lá van thoái hóa nhầy và đo '
                        'mức độ hở van hai lá, trấn an bệnh nhân về tiên lượng rất lành tính của bệnh.',
                        'Kê đơn thuốc chẹn beta giao cảm liều thấp như Propranolol hoặc Bisoprolol nếu bệnh nhân có '
                        'nhiều triệu chứng hồi hộp đánh trống ngực hoặc lo âu thần kinh thực vật.',
                        'Đo Holter điện tim 24 giờ tầm soát các ngoại tâm thu nhĩ hoặc thất nếu bệnh nhân than phiền '
                        'hồi hộp tim nhiều, tránh dùng các chất kích thích như cà phê rượu bia thuốc lá.',
                        'Hướng dẫn chế độ sinh hoạt thể dục đều đặn uống đủ nước, tái khám kiểm tra siêu âm tim định '
                        'kỳ mỗi 2-3 năm hoặc khi có triệu chứng mới xuất hiện.',
                        'Giáo dục bệnh nhân nhận biết các dấu hiệu cảnh báo như khó thở khi gắng sức hoặc tiếng thổi '
                        'tim to lên gợi ý đứt dây chằng van hai lá gây hở van nặng cấp.',
                        'Không cần dùng kháng sinh dự phòng viêm nội tâm mạc cho sa van hai lá đơn thuần hở nhẹ theo '
                        'các khuyến cáo tim mạch hiện hành, duy trì lối sống lành mạnh.'],
  'kham': 'Nghe tim có tiếng click giữa tâm thu sắc gọn theo sau bởi tiếng thổi tâm thu muộn 2/6 ở mỏm tim, tiếng '
          'click và tiếng thổi dịch chuyển sớm hơn về phía T1 khi bệnh nhân đứng dậy hoặc làm nghiệm pháp Valsalva.',
  'chan_doan': 'Hội chứng sa van hai lá Mitral Valve Prolapse biến chứng hở van hai lá nhẹ.',
  'ke_hoach': 'Làm siêu âm tim qua thành ngực khảo sát hình thái lá van độ dày lá van thoái hóa nhầy và đo mức độ hở '
              'van hai lá, trấn an bệnh nhân về tiên lượng rất lành tính của bệnh.'},
 {'ten': 'tăng áp lực động mạch phổi tiên phát vô căn',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['áp lực động mạch phổi tâm thu ước tính qua siêu âm tim trên 35 mmHg hoặc áp lực động mạch phổi trung bình '
            'qua thông tim phải trên 20 mmHg khi nghỉ',
            'sức cản mạch máu phổi PVR tăng cao trên 2 đơn vị Wood kèm áp lực mao mạch phổi bít bình thường dưới 15 '
            'mmHg',
            'loại trừ hoàn toàn các nguyên nhân tăng áp phổi thứ phát do bệnh tim trái bệnh phổi tắc nghẽn hoặc thuyên '
            'tắc huyết khối mạn tính'],
  'phu': ['khó thở tiến triển tăng dần khi gắng sức ban đầu kín đáo sau đó rõ rệt',
          'tiếng tim thứ hai T2 có thành phần phổi P2 đanh mạnh tách đôi hẹp ở đáy tim',
          'choáng váng xây xẩm hoặc ngất khi gắng sức do không tăng được cung lượng tim qua phổi'],
  'bien_the_kham': ['Nghe tim có tiếng P2 đanh mạnh rõ ở khoang liên sườn 2 bờ trái xương ức, sờ thấy thất phải đập '
                    'nảy vùng dưới mũi ức dấu hiệu Hartzer dương tính, nghe được tiếng thổi tâm thu 2/6 do hở van ba '
                    'lá cơ năng ở bờ trái ức tăng lên khi hít sâu dấu Carvallo.',
                    'Khám thấy tiếng thành phần phổi P2 đanh vang tách đôi hẹp, mỏm thất phải đập mạnh cạnh bờ trái '
                    'xương ức, tĩnh mạch cổ nổi nhẹ sóng a đập nẩy, gan to nhẹ dưới bờ sườn.',
                    'Nhịp tim nhanh nhẹ 90 l/p, tiếng T2 đanh rất mạnh ở đáy tim, có tiếng click tống máu động mạch '
                    'phổi đầu tâm thu, hai phổi thông khí rất tốt không có ran ẩm ran rít.',
                    'Bệnh nhân khó thở nhẹ khi đi lại trong phòng, môi hồng nhạt, khám tim phát hiện tiếng P2 đanh như '
                    'tiếng gõ kim loại ở bờ trái xương ức, phù nhẹ hai mắt cá chân.',
                    'Dấu hiệu Hartzer dương tính thất phải đập nâng đầu ngón tay dưới mũi kiếm xương ức, tiếng thổi '
                    'tâm thu hở ba lá cơ năng, SpO2 94% khí phòng giảm khi đi bộ.',
                    'Tiếng tim T2 đanh mạnh thành phần phổi vượt trội thành phần chủ, tĩnh mạch cổ nổi tư thế 45 độ, '
                    'bụng mềm gan mấp mé bờ sườn phải, không có ngón tay dùi trống.'],
  'bien_the_chan_doan': ['Tăng áp lực động mạch phổi nguyên phát vô căn Idiopathic Pulmonary Arterial Hypertension '
                         'nhóm 1.',
                         'Tăng áp động mạch phổi vô căn IPAH giai đoạn chức năng NYHA/WHO nhóm III.',
                         'Tăng áp lực động mạch phổi nguyên phát có suy chức năng thất phải tiến triển.',
                         'Theo dõi tăng áp động mạch phổi vô căn cần thực hiện thông tim phải xác chẩn.',
                         'Tăng áp động mạch phổi nguyên phát có hở van ba lá cơ năng và tăng sức cản mạch phổi.',
                         'Bệnh lý mạch máu phổi tăng áp động mạch phổi tiên phát chưa rõ đột biến gen BMPR2.'],
  'bien_the_ke_hoach': ['Chỉ định thông tim phải chẩn đoán xác định đo áp lực động mạch phổi trung bình sức cản mạch '
                        'phổi và làm test giãn mạch cấp với nitric oxide để chọn lựa thuốc điều trị đích.',
                        'Bắt đầu liệu pháp điều trị giãn mạch phổi đặc hiệu kết hợp nhóm kháng thụ thể Endothelin '
                        'Bosentan hoặc Macitentan với nhóm ức chế men PDE-5 Sildenafil hoặc Tadalafil.',
                        'Làm nghiệm pháp đi bộ 6 phút 6MWD đánh giá khả năng dung nạp thể lực và phân tầng nguy cơ tử '
                        'vong định kỳ, cho thở oxy hỗ trợ duy trì SpO2 trên 92%.',
                        'Chụp CT ngực cản quang mạch máu phổi CTPA và xạ hình thông khí tưới máu phổi V/Q scan loại '
                        'trừ hoàn toàn tăng áp phổi do huyết khối thuyên tắc mạn tính CTEPH.',
                        'Dùng thuốc lợi tiểu quai Furosemide liều thích hợp kiểm soát ứ trệ dịch thất phải, tránh hoàn '
                        'toàn thai kỳ vì nguy cơ tử vong chu sinh cực kỳ cao.',
                        'Đăng ký quản lý tại trung tâm chuyên sâu về Tăng áp động mạch phổi, lập kế hoạch đánh giá '
                        'dùng thuốc đồng vận prostacyclin đường tiêm truyền nếu thuộc nhóm nguy cơ cao.'],
  'kham': 'Nghe tim có tiếng P2 đanh mạnh rõ ở khoang liên sườn 2 bờ trái xương ức, sờ thấy thất phải đập nảy vùng '
          'dưới mũi ức dấu hiệu Hartzer dương tính, nghe được tiếng thổi tâm thu 2/6 do hở van ba lá cơ năng ở bờ trái '
          'ức tăng lên khi hít sâu dấu Carvallo.',
  'chan_doan': 'Tăng áp lực động mạch phổi nguyên phát vô căn Idiopathic Pulmonary Arterial Hypertension nhóm 1.',
  'ke_hoach': 'Chỉ định thông tim phải chẩn đoán xác định đo áp lực động mạch phổi trung bình sức cản mạch phổi và làm '
              'test giãn mạch cấp với nitric oxide để chọn lựa thuốc điều trị đích.'},
 {'ten': 'viêm tắc tĩnh mạch nông chi dưới do tiêm truyền',
  'nhom': 'người lớn',
  'dien_tien': 'cấp',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['dải gân sưng đỏ nóng rát sờ cứng như sợi dây thừng chạy dọc mắt cá cẳng chân trong',
            'phản ứng viêm thâm nhiễm nông tại vị trí chọc kim luồn sau truyền kháng sinh kích ứng',
            'siêu âm chẩn đoán hình ảnh thấy lòng tĩnh mạch hiển nông giãn chứa cục huyết khối thành dày'],
  'phu': ['đau buốt tăng lên khi cử động bàn chân hoặc bước đi dồn trọng lượng',
          'vùng mô mềm quanh vết chọc kim sưng nóng đỏ giới hạn rõ',
          'không có sưng to bắp chân sâu loại trừ tổn thương mạch máu sâu'],
  'bien_the_kham': ['Nhìn thấy vệt da đỏ dọc theo đường đi tĩnh mạch hiển nông ở mặt trong cẳng chân dài khoảng 8cm, '
                    'sờ thấy dải xơ cứng như sợi dây thừng ấn rất đau rát, nhiệt độ da tại chỗ ấm nóng, không phù toàn '
                    'bộ cẳng chân.',
                    'Vùng mu bàn chân và cổ chân trong có dải cứng đỏ đau xuất phát từ vị trí lưu kim tiêm truyền tĩnh '
                    'mạch cũ, ấn đau chói dọc tĩnh mạch, mạch mu chân và chày sau bắt rõ bình thường.',
                    'Khám thấy đoạn tĩnh mạch nông cẳng chân viêm đỏ gồ trên mặt da, sờ chắc đau rát khi miết nhẹ ngón '
                    'tay, không có mủ chảy ra từ lỗ chọc kim tiêm, cẳng chân không sưng to.',
                    'Da cẳng chân trong có đường sọc ban đỏ sưng nề theo giải phẫu tĩnh mạch hiển, sờ thấy cục huyết '
                    'khối nông chắc cứng, nghiệm pháp Homans âm tính không đau bắp chân sâu.',
                    'Dải tĩnh mạch nông viêm tắc cứng đau dài 6cm sau tiêm truyền kháng sinh tĩnh mạch 3 ngày, da phủ '
                    'lên trên đỏ ấm ấn tức, khớp cổ chân cử động bình thường.',
                    'Vệt đỏ dọc tĩnh mạch hiển nông mặt trong cẳng chân ấn chắc và đau nhạy cảm, không có phù nề lan '
                    'tỏa toàn chi, các mạch máu nuôi dưỡng đầu chi bắt đập tốt.'],
  'bien_the_chan_doan': ['Viêm tắc tĩnh mạch nông chi dưới cấp tính do biến chứng tiêm truyền tĩnh mạch ngoại vi.',
                         'Viêm huyết khối tĩnh mạch nông cẳng chân sau lưu kim luồn tĩnh mạch.',
                         'Viêm tắc tĩnh mạch hiển nông chi dưới thứ phát sau truyền dịch kích ứng.',
                         'Theo dõi viêm tắc tĩnh mạch nông chi dưới có huyết khối khu trú nông.',
                         'Huyết khối tĩnh mạch nông chi dưới do can thiệp mạch máu ngoại biên cấp tính.',
                         'Viêm tĩnh mạch nông nông do tiêm truyền có phản ứng viêm mô bào xung quanh.'],
  'bien_the_ke_hoach': ['Chườm ấm tại chỗ vùng tĩnh mạch viêm 3-4 lần mỗi ngày, dùng thuốc chống viêm giảm đau không '
                        'steroid NSAID Ibuprofen hoặc Celecoxib đường uống, bôi gel chứa heparin tại chỗ giảm viêm tan '
                        'cục máu đông.',
                        'Làm siêu âm Doppler mạch máu chi dưới xác định khoảng cách từ đầu huyết khối tĩnh mạch nông '
                        'đến quai tĩnh mạch hiển đùi hoặc hiển khoeo để loại trừ nguy cơ lan vào hệ tĩnh mạch sâu.',
                        'Kê đơn thuốc chống đông liều dự phòng Fondaparinux 2.5 mg tiêm dưới da mỗi ngày trong 45 ngày '
                        'nếu huyết khối tĩnh mạch nông dài trên 5cm hoặc nằm gần quai hiển đùi dưới 3cm.',
                        'Hướng dẫn bệnh nhân kê cao chân khi nghỉ ngơi, mang vớ ép y khoa áp lực nhẹ sau giai đoạn đau '
                        'cấp, khuyến khích vận động đi lại nhẹ nhàng tránh nằm bất động kéo dài.',
                        'Theo dõi sát diễn tiến của dải xơ viêm đỏ, tái khám làm lại siêu âm Doppler mạch máu sau 7-10 '
                        'ngày để kiểm tra sự thoái lui của huyết khối.',
                        'Dặn dò bệnh nhân các dấu hiệu cần đến viện ngay như sưng to toàn bộ cẳng chân bắp chân căng '
                        'cứng hoặc đau ngực khó thở bất thường.'],
  'kham': 'Nhìn thấy vệt da đỏ dọc theo đường đi tĩnh mạch hiển nông ở mặt trong cẳng chân dài khoảng 8cm, sờ thấy dải '
          'xơ cứng như sợi dây thừng ấn rất đau rát, nhiệt độ da tại chỗ ấm nóng, không phù toàn bộ cẳng chân.',
  'chan_doan': 'Viêm tắc tĩnh mạch nông chi dưới cấp tính do biến chứng tiêm truyền tĩnh mạch ngoại vi.',
  'ke_hoach': 'Chườm ấm tại chỗ vùng tĩnh mạch viêm 3-4 lần mỗi ngày, dùng thuốc chống viêm giảm đau không steroid '
              'NSAID Ibuprofen hoặc Celecoxib đường uống, bôi gel chứa heparin tại chỗ giảm viêm tan cục máu đông.'},
 {'ten': 'phình động mạch chủ bụng dưới thận kích thước nhỏ',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['đoạn động mạch chủ bụng dưới chỗ xuất phát động mạch thận giãn phình với đường kính ngang từ 3.0 đến 4.4 '
            'cm trên siêu âm hoặc CT',
            'sờ thấy khối đập theo nhịp tim nằm ở vùng bụng trên rốn hoặc quanh rốn hơi lệch sang bên trái',
            'phình động mạch tiến triển mạn tính chưa có dấu hiệu dọa vỡ hay rò rỉ vào khoang sau phúc mạc'],
  'phu': ['thường không có triệu chứng cơ năng rõ rệt phát hiện tình cờ qua siêu âm ổ bụng tổng quát',
          'cảm giác tức nặng âm ỉ mơ hồ vùng bụng giữa hoặc thắt lưng',
          'nghe thấy tiếng thổi tâm thu nhẹ dọc đường đi của động mạch chủ bụng'],
  'bien_the_kham': ['Sờ thấy khối đập theo nhịp đập của tim vùng quanh rốn và hơi lệch trái, đường kính khối ước lượng '
                    'qua sờ nắn khoảng 3.5cm, không đau khi ấn nhẹ, nghe có tiếng thổi tâm thu nhẹ vùng trên rốn.',
                    'Bụng mềm phẳng, đặt hai bàn tay hai bên đường giữa trên rốn thấy khối mạch đập dội hai bên ra '
                    'ngoài dấu hiệu expansile pulsation dương tính, không có phản ứng thành bụng.',
                    'Khám thấy khối đập theo nhịp mạch ở vùng bụng giữa ranh giới rõ không ấn đau chói, mạch hai chi '
                    'dưới mạch đùi mu chân bắt đều rõ hai bên, huyết áp 135/85 mmHg.',
                    'Khối phình động mạch chủ bụng đập theo tim sờ rõ ở người gầy, bề ngang khoảng 3-4cm di động nhẹ, '
                    'bụng không chướng không gõ đục vùng thấp.',
                    'Sờ nắn vùng trên rốn phát hiện khối mạch đập nhịp nhàng theo nhịp tim, không có điểm đau nhạy '
                    'cảm, nghe không có tiếng cọ màng bụng, mạch bẹn đập rõ.',
                    'Bụng mềm, sờ thấy khối đập dội nở rộng theo nhịp tim vùng bụng giữa lệch trái, ấn không đau, nghe '
                    'tiếng thổi tâm thu nhẹ trên khối phình, mạch ngoại biên tốt.'],
  'bien_the_chan_doan': ['Phình động mạch chủ bụng dưới thận kích thước nhỏ đường kính dưới 4.5 cm chưa biến chứng.',
                         'Phình động mạch chủ bụng thể hình thoi dưới thận phát hiện tình cờ qua siêu âm.',
                         'Phình động mạch chủ bụng dưới thận kích thước nhỏ mạn tính do vữa xơ động mạch.',
                         'Theo dõi phình động mạch chủ bụng dưới thận kích thước nhỏ nguy cơ vỡ thấp.',
                         'Bệnh lý giãn phình động mạch chủ bụng dưới nguyên ủy động mạch thận giai đoạn theo dõi ngoại '
                         'trú.',
                         'Phình động mạch chủ bụng dưới thận kích thước nhỏ kiểm soát tốt các yếu tố nguy cơ tim '
                         'mạch.'],
  'bien_the_ke_hoach': ['Siêu âm Doppler mạch máu bụng định kỳ mỗi 6-12 tháng để theo dõi tốc độ phát triển đường kính '
                        'khối phình, chỉ định can thiệp đặt stent-graft EVAR hoặc mổ hở khi đường kính đạt từ 5.5 cm '
                        'trở lên hoặc tốc độ dãn trên 1 cm mỗi năm.',
                        'Kiểm soát huyết áp nghiêm ngặt mục tiêu huyết áp dưới 130/80 mmHg ưu tiên dùng thuốc chẹn '
                        'beta giao cảm hoặc ức chế men chuyển để giảm áp lực lên thành mạch phình.',
                        'Dùng thuốc nhóm Statin liều cao để ổn định mảng xơ vữa thành mạch và aspirin liều thấp phòng '
                        'ngừa huyết khối tắc mạch, bỏ thuốc lá hoàn toàn và vĩnh viễn.',
                        'Chụp cắt lớp vi tính cản quang mạch máu bụng CTA khi khối phình đạt kích thước 5.0 cm hoặc '
                        'khi có triệu chứng đau bụng lưng mới xuất hiện để đánh giá chi tiết giải phẫu cổ túi phình.',
                        'Giáo dục bệnh nhân nhận thức về bệnh, dặn dò đến cấp cứu ngay lập tức nếu xuất hiện cơn đau '
                        'bụng hoặc đau thắt lưng dữ dội đột ngột kèm vã mồ hôi tụt huyết áp.',
                        'Tư vấn tránh các hoạt động nâng vác vật quá nặng hoặc làm các nghiệm pháp rặn mạnh đột ngột '
                        'làm tăng áp lực trong ổ bụng.'],
  'kham': 'Sờ thấy khối đập theo nhịp đập của tim vùng quanh rốn và hơi lệch trái, đường kính khối ước lượng qua sờ '
          'nắn khoảng 3.5cm, không đau khi ấn nhẹ, nghe có tiếng thổi tâm thu nhẹ vùng trên rốn.',
  'chan_doan': 'Phình động mạch chủ bụng dưới thận kích thước nhỏ đường kính dưới 4.5 cm chưa biến chứng.',
  'ke_hoach': 'Siêu âm Doppler mạch máu bụng định kỳ mỗi 6-12 tháng để theo dõi tốc độ phát triển đường kính khối '
              'phình, chỉ định can thiệp đặt stent-graft EVAR hoặc mổ hở khi đường kính đạt từ 5.5 cm trở lên hoặc tốc '
              'độ dãn trên 1 cm mỗi năm.'},
 {'ten': 'xơ cứng động mạch Monckeberg',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'da_duyet': False,
  'chinh': ['vôi hóa lớp áo giữa thành động mạch kích thước trung bình và nhỏ tạo hình ảnh ống điếu hoặc đường ray xe '
            'lửa trên X-quang chi',
            'thành mạch máu xơ cứng không thể ép xẹp khi đo huyết áp dẫn đến chỉ số huyết áp cổ chân cánh tay ABI tăng '
            'giả tạo trên 1.4',
            'vôi hóa thành mạch không xâm lấn vào lớp nội mạc và không gây hẹp trực tiếp lòng động mạch'],
  'phu': ['sờ các động mạch ngoại vi như động mạch quay động mạch chày sau thấy cứng chắc như ống nhựa hoặc sợi dây '
          'kim loại',
          'thường gặp ở bệnh nhân cao tuổi mắc bệnh đái tháo đường lâu năm hoặc bệnh thận mạn tính',
          'không có triệu chứng thiếu máu cục bộ chi dưới như đau cách hồi trừ khi có xơ vữa nội mạc phối hợp'],
  'bien_the_kham': ['Sờ động mạch quay hai bên và động mạch chày sau thấy thành mạch cứng chắc lăn tăn dưới ngón tay '
                    'như ống dẫn nước cứng nhưng mạch vẫn đập rõ, đo huyết áp khó ép xẹp bao đo, chi dưới ấm hồng '
                    'không loét.',
                    'Khám thấy mạch mu chân và chày sau bắt nảy đều nhưng thành mạch cứng rắn rõ rệt, không có tổn '
                    'thương thiếu máu hoại tử đầu chi, không đau khi ấn dọc đường đi mạch máu.',
                    'Động mạch cánh tay và động mạch quay xơ cứng chắc như ống điếu cao su cứng, mạch đập nẩy dưới '
                    'thành mạch vôi hóa, huyết áp tâm thu đo được tăng giả tạo 170/80 mmHg.',
                    'Chi dưới ấm áp mạch ngoại vi bắt rõ ràng nhưng thành mạch cảm giác cứng như sợi dây thép cuộn, '
                    'không có dấu hiệu teo cơ hay rụng lông do thiếu máu mạn tính.',
                    'Khám mạch máu thấy thành động mạch quay cứng chắc không xẹp khi ấn đè, đo chỉ số ABI cho kết quả '
                    'trên 1.4 do động mạch không thể ép xẹp, phản hồi mao mạch dưới 2 giây.',
                    'Thể trạng bình thường, hệ thống động mạch ngoại biên sờ thấy các dải xơ vôi hóa lớp áo giữa cứng '
                    'đều, không có tiếng thổi hẹp lòng mạch ở động mạch đùi hay động mạch cảnh.'],
  'bien_the_chan_doan': ['Xơ cứng động mạch Monckeberg vôi hóa lớp áo giữa thành mạch ở bệnh nhân đái tháo đường.',
                         'Bệnh xơ cứng vôi hóa lớp áo giữa động mạch Mönckeberg vôi hóa thành mạch không tắc nghẽn.',
                         'Xơ cứng động mạch Monckeberg có chỉ số huyết áp cổ chân cánh tay ABI tăng cao giả tạo.',
                         'Theo dõi bệnh xơ cứng áo giữa động mạch Mönckeberg kết hợp bệnh thận mạn tính.',
                         'Xơ cứng thành mạch thể Monckeberg mạn tính ở người cao tuổi.',
                         'Xơ cứng áo giữa Monckeberg có thành mạch máu cứng không ép xẹp được.'],
  'bien_the_ke_hoach': ['Đo chỉ số huyết áp ngón chân cánh tay TBI Toe-Brachial Index để đánh giá chính xác tuần hoàn '
                        'tưới máu chi dưới vì chỉ số ABI bị sai lệch do thành mạch không thể ép xẹp.',
                        'Chụp X-quang thường quy chi dưới hoặc bàn chân đánh giá hình thái vôi hóa dạng ống song song '
                        'đặc trưng của lớp áo giữa động mạch, làm siêu âm Doppler mạch máu chi dưới.',
                        'Kiểm soát tối ưu đường huyết HbA1c ở bệnh nhân đái tháo đường và cân bằng chuyển hóa canxi '
                        'phospho ở bệnh nhân bệnh thận mạn để làm chậm tiến trình vôi hóa mạch máu.',
                        'Tầm soát bệnh lý xơ vữa động mạch nội mạc đi kèm tại các vị trí mạch vành mạch cảnh và động '
                        'mạch chi dưới bằng các phương tiện chẩn đoán hình ảnh chuyên sâu.',
                        'Chăm sóc bàn chân đúng cách, mang giày dép mềm vừa vặn tránh cọ xát gây sang chấn loét chân '
                        'khó lành, khám bàn chân định kỳ mỗi lần tái khám.',
                        'Tư vấn giải thích cho bệnh nhân về tình trạng vôi hóa thành mạch lành tính Monckeberg, phân '
                        'biệt với bệnh viêm tắc xơ vữa động mạch gây hẹp lòng mạch máu.'],
  'kham': 'Sờ động mạch quay hai bên và động mạch chày sau thấy thành mạch cứng chắc lăn tăn dưới ngón tay như ống dẫn '
          'nước cứng nhưng mạch vẫn đập rõ, đo huyết áp khó ép xẹp bao đo, chi dưới ấm hồng không loét.',
  'chan_doan': 'Xơ cứng động mạch Monckeberg vôi hóa lớp áo giữa thành mạch ở bệnh nhân đái tháo đường.',
  'ke_hoach': 'Đo chỉ số huyết áp ngón chân cánh tay TBI Toe-Brachial Index để đánh giá chính xác tuần hoàn tưới máu '
              'chi dưới vì chỉ số ABI bị sai lệch do thành mạch không thể ép xẹp.'},
 {'ten': 'rối loạn stress sau sang chấn PTSD',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['ký ức đau buồn hoặc hồi tưởng xâm nhập dạng flashback tái hiện sự kiện sang chấn kinh hoàng',
            'né tránh tích cực mọi kích thích địa điểm con người gợi nhớ đến biến cố sang chấn quá khứ',
            'trạng thái kích thích quá mức giật mình cảnh giác cao độ và khó ngủ kéo dài trên một tháng'],
  'phu': ['ác mộng kinh hoàng lặp đi lặp lại về sự kiện đe dọa tính mạng',
          'tê liệt cảm xúc mất hứng thú với các hoạt động giao tiếp xã hội',
          'cảm giác tội lỗi hoặc đổ lỗi sai lầm cho bản thân về biến cố'],
  'bien_the_kham': ['Bệnh nhân nét mặt căng thẳng lo âu, giật mình hoảng hốt khi có tiếng đóng cửa lớn, bàn tay run '
                    'nhẹ vã mồ hôi, tiếp xúc dè dặt cảnh giác, nhịp tim nhanh 96 l/p.',
                    'Khám tâm thần thấy khí sắc lo âu trầm uất, hay nhìn quanh phòng kiểm tra lối thoát hiểm, trả lời '
                    'ngập ngừng khi nhắc đến sự kiện chấn thương, không có hoang tưởng ảo giác.',
                    'Ánh mắt bồn chồn lo lắng thường trực, lòng bàn tay ướt mồ hôi lạnh, nhịp thở nhanh nông, bệnh '
                    'nhân kể lại cảm giác hoảng loạn sống lại ký ức cũ, huyết áp 135/85 mmHg.',
                    'Tác phong bồn chồn đứng ngồi không yên, phản xạ giật mình tăng nhạy cảm, biểu cảm nét mặt cứng đờ '
                    'thiếu linh hoạt, tư duy tập trung vào cảm giác bất an.',
                    'Tiếp xúc hợp tác nhưng luôn giữ khoảng cách phòng vệ, nét mặt đượm vẻ sợ hãi và mệt mỏi do mất '
                    'ngủ kinh niên, không có dấu hiệu thần kinh thực thể.',
                    'Bệnh nhân kích động bồn chồn nhẹ khi nghe câu hỏi liên quan biến cố quá khứ, vã mồ hôi trán, tim '
                    'đập nhanh hồi hộp, định hướng không gian thời gian bản thân chuẩn xác.'],
  'bien_the_chan_doan': ['Rối loạn stress sau sang chấn PTSD mạn tính có phản ứng hồi tưởng xâm nhập và kích thích quá '
                         'mức.',
                         'Rối loạn căng thẳng sau sang chấn PTSD mạn tính sau tai nạn nghiêm trọng.',
                         'Hội chứng stress sau sang chấn PTSD thể có triệu chứng né tránh chiếm ưu thế.',
                         'Theo dõi rối loạn stress sau sang chấn PTSD biến chứng rối loạn giấc ngủ trầm cảm thứ phát.',
                         'Rối loạn stress sau sang chấn PTSD tiến triển kéo dài trên 6 tháng sau biến cố kinh hoàng.',
                         'Rối loạn stress sau sang chấn PTSD có rối loạn lo âu và phản ứng giật mình quá mức.'],
  'bien_the_ke_hoach': ['Chỉ định liệu pháp tâm lý chuyên sâu xử lý sang chấn tái xử lý bằng chuyển động mắt EMDR hoặc '
                        'liệu pháp hành vi nhận thức tập trung vào sang chấn TF-CBT, dùng thuốc chống trầm cảm nhóm '
                        'SSRI Sertraline hoặc Paroxetine kiểm soát triệu chứng lo âu xâm nhập.',
                        'Kê đơn thuốc Sertraline 50mg mỗi ngày tăng dần liều theo đáp ứng, kết hợp thuốc chẹn thụ thể '
                        'alpha Prazosin vào buổi tối để điều trị ác mộng và giảm kích thích giao cảm ban đêm.',
                        'Thực hiện trắc nghiệm tâm lý đánh giá mức độ sang chấn qua thang PCL-5, thiết lập kế hoạch '
                        'trị liệu tâm lý cá nhân định kỳ hàng tuần, hướng dẫn kỹ thuật thở thư giãn sâu.',
                        'Tư vấn giải thích bản chất bệnh lý của PTSD cho bệnh nhân và gia đình, xây dựng môi trường '
                        'sống an toàn ít kích thích gây sợ hãi, tránh sử dụng rượu bia chất kích thích.',
                        'Phối hợp điều trị dược lý với phục hồi chức năng xã hội, hỗ trợ bệnh nhân tái hòa nhập công '
                        'việc từng bước, theo dõi sát nguy cơ tự sát hoặc hành vi tiêu cực.',
                        'Đăng ký chương trình trị liệu tâm lý ngoại trú dài hạn, kiểm tra đánh giá lại thang điểm trầm '
                        'cảm và lo âu sau 4-6 tuần điều trị thuốc SSRI.'],
  'kham': 'Bệnh nhân nét mặt căng thẳng lo âu, giật mình hoảng hốt khi có tiếng đóng cửa lớn, bàn tay run nhẹ vã mồ '
          'hôi, tiếp xúc dè dặt cảnh giác, nhịp tim nhanh 96 l/p.',
  'chan_doan': 'Rối loạn stress sau sang chấn PTSD mạn tính có phản ứng hồi tưởng xâm nhập và kích thích quá mức.',
  'ke_hoach': 'Chỉ định liệu pháp tâm lý chuyên sâu xử lý sang chấn tái xử lý bằng chuyển động mắt EMDR hoặc liệu pháp '
              'hành vi nhận thức tập trung vào sang chấn TF-CBT, dùng thuốc chống trầm cảm nhóm SSRI Sertraline hoặc '
              'Paroxetine kiểm soát triệu chứng lo âu xâm nhập.'},
 {'ten': 'rối loạn ám ảnh sợ khoảng trống Agoraphobia',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['sợ hãi hoặc lo âu mãnh liệt dai dẳng đối với ít nhất hai trong các tình huống: phương tiện giao thông '
            'công cộng không gian mở không gian kín xếp hàng đông người ở một mình ngoài nhà',
            'người bệnh sợ hãi vì nghĩ rằng việc thoát thân sẽ rất khó khăn hoặc không có sự trợ giúp kịp thời nếu '
            'xuất hiện triệu chứng hoảng loạn',
            'hành vi né tránh chủ động các tình huống này khiến người bệnh tự giam mình trong nhà hoặc chỉ đi ra ngoài '
            'khi có người thân đi cùng'],
  'phu': ['cảm giác khó thở nghẹt thở tim đập dồn dập khi bước vào nơi đông người',
          'chóng mặt xây xẩm mất thăng bằng hoặc cảm giác sắp ngất',
          'sợ mất kiểm soát hoặc sợ phát điên khi bị mắc kẹt'],
  'bien_the_kham': ['Bệnh nhân được người nhà dìu vào phòng khám với dáng vẻ bồn chồn sợ hãi tột độ, nắm chặt tay '
                    'người thân không rời, thở nhanh nông, nhịp tim 105 l/p, lòng bàn tay ướt lạnh.',
                    'Khám thấy bệnh nhân biểu hiện lo lắng căng thẳng khi ngồi trong phòng khám kín, mắt liên tục nhìn '
                    'ra cửa sổ và cửa ra vào, nhịp thở 24 l/p, huyết áp tăng nhẹ 140/85 mmHg.',
                    'Tác phong co cụm sợ sệt, khai báo không thể tự đi xe buýt hay vào siêu thị một mình trong suốt 8 '
                    'tháng qua, tim phổi khám thực thể không có tổn thương van tim.',
                    'Bệnh nhân biểu lộ nỗi sợ rõ rệt khi được yêu cầu thử bước ra ngoài hành lang bệnh viện một mình, '
                    'vã mồ hôi tay chân run rẩy, ý thức hoàn toàn tỉnh táo định hướng tốt.',
                    'Nét mặt căng thẳng cảnh giác, hơi thở dồn dập khi kể về cảm giác sợ hãi nơi công cộng, phản xạ '
                    'gân xương bình thường, không có dấu liệt khu trú.',
                    'Tiếp xúc tốt nhưng tỏ rõ sự lo sợ bị ngất xỉu giữa chốn đông người, bàn tay run nhẹ biên độ nhỏ, '
                    'nhịp tim đều nhanh 100 lần/phút, bụng mềm.'],
  'bien_the_chan_doan': ['Rối loạn ám ảnh sợ khoảng trống Agoraphobia mạn tính có hành vi né tránh nghiêm trọng.',
                         'Ám ảnh sợ nơi trống trải Agoraphobia kết hợp cơn hoảng loạn Panic Disorder.',
                         'Rối loạn lo âu ám ảnh sợ khoảng trống thể không có tiền sử cơn hoảng loạn toàn phát.',
                         'Theo dõi chứng sợ khoảng trống Agoraphobia hạn chế nghiêm trọng khả năng sinh hoạt độc lập.',
                         'Rối loạn ám ảnh sợ nơi công cộng Agoraphobia mức độ nặng lệ thuộc người thân.',
                         'Ám ảnh sợ khoảng rộng Agoraphobia giai đoạn mạn tính điều trị liệu pháp hành vi kết hợp.'],
  'bien_the_ke_hoach': ['Bắt đầu điều trị bằng thuốc chống trầm cảm ức chế tái hấp thu chọn lọc serotonin SSRI '
                        'Escitalopram hoặc Sertraline liều thấp tăng dần, kết hợp liệu pháp tâm lý tiếp xúc phơi nhiễm '
                        'từng bước Exposure Therapy và liệu pháp nhận thức hành vi CBT.',
                        'Kê đơn thuốc Escitalopram 10mg mỗi ngày, có thể dùng ngắn hạn thuốc nhóm Benzodiazepine '
                        'Alprazolam 0.25mg trong 2 tuần đầu để kiểm soát lo âu cấp trước khi SSRI có tác dụng.',
                        'Lập kế hoạch phơi nhiễm từng nấc thang từ tưởng tượng đến thực tế cùng với nhà tâm lý học và '
                        'người thân trong gia đình, khuyến khích bệnh nhân tự bước ra sân nhà.',
                        'Tư vấn giải thích cơ chế sinh lý của nỗi sợ hãi và phản ứng cơ thể, tập kỹ thuật thư giãn cơ '
                        'bắp tiến triển Jacobson và điều hòa nhịp thở.',
                        'Hẹn tái khám định kỳ mỗi 2 tuần đánh giá sự cải thiện về phạm vi di chuyển của bệnh nhân, '
                        'giảm dần và ngừng thuốc Benzodiazepine tránh gây phụ thuộc thuốc.',
                        'Hỗ trợ người nhà phương pháp đồng hành cùng bệnh nhân không bao bọc quá mức để tạo điều kiện '
                        'cho bệnh nhân từng bước phục hồi tính tự lập.'],
  'kham': 'Bệnh nhân được người nhà dìu vào phòng khám với dáng vẻ bồn chồn sợ hãi tột độ, nắm chặt tay người thân '
          'không rời, thở nhanh nông, nhịp tim 105 l/p, lòng bàn tay ướt lạnh.',
  'chan_doan': 'Rối loạn ám ảnh sợ khoảng trống Agoraphobia mạn tính có hành vi né tránh nghiêm trọng.',
  'ke_hoach': 'Bắt đầu điều trị bằng thuốc chống trầm cảm ức chế tái hấp thu chọn lọc serotonin SSRI Escitalopram hoặc '
              'Sertraline liều thấp tăng dần, kết hợp liệu pháp tâm lý tiếp xúc phơi nhiễm từng bước Exposure Therapy '
              'và liệu pháp nhận thức hành vi CBT.'},
 {'ten': 'rối loạn ám ảnh sợ xã hội Social Phobia',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['nỗi sợ hãi hoặc lo âu rõ rệt dai dẳng về một hoặc nhiều tình huống xã hội mà người bệnh có thể bị người '
            'khác soi mói đánh giá tiêu cực',
            'sợ rằng bản thân sẽ hành động hoặc bộc lộ các triệu chứng lo âu dẫn đến bị bẽ mặt xấu hổ hoặc xúc phạm '
            'người khác',
            'các tình huống xã hội hầu như luôn kích phát nỗi sợ hãi khiến người bệnh phải né tránh hoặc chịu đựng với '
            'nỗi khổ sở tột cùng'],
  'phu': ['đỏ mặt bừng bừng tim đập nhanh vã mồ hôi run giọng khi phải phát biểu hoặc ăn uống trước đám đông',
          'tránh nhìn thẳng vào mắt người đối diện khi giao tiếp',
          'lo âu chờ đợi căng thẳng nhiều ngày trước một sự kiện xã hội sắp tới'],
  'bien_the_kham': ['Bệnh nhân cúi đầu tránh ánh mắt người khám, mặt đỏ bừng khi bắt đầu nói chuyện, giọng nói run rẩy '
                    'đứt quãng, hai tay bứt rứt xoắn vạt áo, mạch 98 l/p.',
                    'Khám thấy bệnh nhân giao tiếp dè dặt, đỏ mặt ngực khi trả lời câu hỏi trực tiếp, nhịp tim nhanh '
                    '95 l/p, lòng bàn tay ướt đẫm mồ hôi, tư duy mạch lạc rõ ràng.',
                    'Nét mặt căng thẳng e ngại quá mức, trả lời rất ngắn gọn bằng câu đơn, bàn tay run nhẹ khi viết '
                    'bảng câu hỏi trắc nghiệm tâm lý, không có rối loạn tri giác.',
                    'Bệnh nhân biểu hiện bối rối tột độ khi có thêm người bước vào phòng khám, ngồi khép nép ở góc '
                    'ghế, nhịp thở nhanh nhẹ, huyết áp bình thường.',
                    'Tiếp xúc ngập ngừng thiếu tự tin, mặt ửng đỏ rõ rệt, giọng nói nhỏ lý nhí trong miệng, định hướng '
                    'lực tốt, không có triệu chứng trầm cảm nặng.',
                    'Khám lâm sàng ghi nhận tình trạng lo âu rõ khi giao tiếp trực diện, mạch quay 92 l/p nảy nhanh, '
                    'không có tổn thương thực thể ở hệ thần kinh hay tim mạch.'],
  'bien_the_chan_doan': ['Rối loạn ám ảnh sợ xã hội Social Anxiety Disorder thể lan tỏa ảnh hưởng nhiều bối cảnh.',
                         'Chứng sợ giao tiếp xã hội Social Phobia mức độ vừa đến nặng gây suy giảm chất lượng cuộc '
                         'sống.',
                         'Rối loạn lo âu xã hội Social Phobia thể chỉ xuất hiện khi biểu diễn hoặc phát biểu trước '
                         'công chúng.',
                         'Theo dõi rối loạn ám ảnh sợ xã hội kéo dài từ lứa tuổi thanh thiếu niên.',
                         'Ám ảnh sợ xã hội Social Phobia có phản ứng thần kinh thực vật đỏ mặt run tay chiếm ưu thế.',
                         'Rối loạn lo âu sợ xã hội mạn tính có né tránh giao tiếp nghề nghiệp và học tập.'],
  'bien_the_ke_hoach': ['Chỉ định liệu pháp hành vi nhận thức CBT cá nhân hoặc nhóm rèn luyện kỹ năng xã hội tái cấu '
                        'trúc nhận thức về sự đánh giá của người khác, dùng thuốc chống trầm cảm nhóm SSRI Paroxetine '
                        'hoặc Sertraline kéo dài ít nhất 6-12 tháng.',
                        'Kê đơn thuốc chẹn beta giao cảm Propranolol 10-20mg uống trước các sự kiện giao tiếp quan '
                        'trọng 30-60 phút để ngăn chặn run tay tim đập nhanh và đỏ mặt.',
                        'Thực hiện bài tập trị liệu nhận thức nhận diện các suy nghĩ tự động tiêu cực méo mó, hướng '
                        'dẫn kỹ năng giao tiếp mắt và điều hòa giọng nói khi tương tác xã hội.',
                        'Tư vấn giải thích cho bệnh nhân hiểu rằng lo âu là phản ứng có thể làm chủ được, khuyến khích '
                        'tham gia các nhóm hỗ trợ đồng đẳng tăng cường tương tác tích cực.',
                        'Theo dõi định kỳ hàng tháng sự cải thiện qua thang đo lo âu xã hội Liebowitz LSAS, điều chỉnh '
                        'liều thuốc SSRI đạt hiệu quả tối ưu.',
                        'Động viên người bệnh kiên trì trị liệu tâm lý, dần mở rộng các hoạt động giao lưu nhỏ từ '
                        'người quen đến môi trường rộng hơn mà không cần trốn tránh.'],
  'kham': 'Bệnh nhân cúi đầu tránh ánh mắt người khám, mặt đỏ bừng khi bắt đầu nói chuyện, giọng nói run rẩy đứt '
          'quãng, hai tay bứt rứt xoắn vạt áo, mạch 98 l/p.',
  'chan_doan': 'Rối loạn ám ảnh sợ xã hội Social Anxiety Disorder thể lan tỏa ảnh hưởng nhiều bối cảnh.',
  'ke_hoach': 'Chỉ định liệu pháp hành vi nhận thức CBT cá nhân hoặc nhóm rèn luyện kỹ năng xã hội tái cấu trúc nhận '
              'thức về sự đánh giá của người khác, dùng thuốc chống trầm cảm nhóm SSRI Paroxetine hoặc Sertraline kéo '
              'dài ít nhất 6-12 tháng.'},
 {'ten': 'rối loạn dạng cơ thể Somatization disorder',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['nhiều triệu chứng cơ thể đau đớn và khó chịu ở nhiều cơ quan khác nhau kéo dài nhiều năm bắt đầu trước '
            'tuổi 30',
            'các xét nghiệm cận lâm sàng hình ảnh học và thăm khám chuyên khoa lặp đi lặp lại không tìm thấy tổn '
            'thương bệnh học thực thể nào giải thích được',
            'người bệnh từ chối tin tưởng lời giải thích của bác sĩ rằng không có bệnh thực thể tiếp tục đi khám nhiều '
            'bệnh viện khác nhau doctor shopping'],
  'phu': ['triệu chứng đau đa dạng như đau đầu đau lưng đau khớp đau ngực đau bụng',
          'triệu chứng tiêu hóa như buồn nôn đầy trướng ợ hơi rối loạn nhu động ruột',
          'triệu chứng thần kinh giả tạo như nuốt nghẹn tê bì mất tiếng thoáng qua'],
  'bien_the_kham': ['Bệnh nhân mang theo một tập hồ sơ xét nghiệm dày cộp từ nhiều bệnh viện, than phiền đau nhức khắp '
                    'người đau lưng tức ngực tê rát dạ dày, khám thực thể toàn diện không phát hiện điểm đau khu trú '
                    'hay tổn thương thực thể.',
                    'Khám lâm sàng tỉ mỉ các hệ cơ quan tim phổi bụng thần kinh cơ xương khớp đều trong giới hạn bình '
                    'thường, bệnh nhân miêu tả triệu chứng một cách sinh động bi kịch hóa nỗi đau.',
                    'Thể trạng bình thường không thiếu máu không sút cân, vẻ mặt nhăn nhó biểu lộ sự chịu đựng đau đớn '
                    'kéo dài, các phản xạ gân xương và cảm giác đối xứng hai bên.',
                    'Khám bụng mềm không chướng không điểm đau ngoại khoa, khám tim mạch nhịp tim đều 78 l/p huyết áp '
                    '120/80 mmHg, các khớp cử động bình thường không sưng nóng.',
                    'Bệnh nhân liệt kê chi tiết hàng loạt cảm giác khó chịu khắp cơ thể từ đau nhức cơ bắp đến cảm '
                    'giác có cục vướng ở cổ họng, khám tai mũi họng bình thường.',
                    'Tác phong mệt mỏi than phiền nhiều về sức khỏe kém, kết quả khám thần kinh ngoại biên và trung '
                    'ương hoàn toàn bình thường, không có teo cơ hay rối loạn cơ tròn.'],
  'bien_the_chan_doan': ['Rối loạn dạng cơ thể Somatization Disorder mạn tính thể đa triệu chứng theo tiêu chuẩn '
                         'DSM-5.',
                         'Rối loạn cơ thể hóa Somatization Disorder có hội chứng đau mạn tính đa vị trí.',
                         'Rối loạn dạng cơ thể dai dẳng có hành vi khám bệnh lặp lại nhiều cơ sở y tế.',
                         'Theo dõi rối loạn triệu chứng cơ thể Somatic Symptom Disorder mức độ nặng.',
                         'Bệnh lý cơ thể hóa dạng cơ thể Somatization Disorder kết hợp lo âu thứ phát.',
                         'Rối loạn dạng cơ thể đa hình thái có niềm tin bất di bất dịch về tổn thương thể xác.'],
  'bien_the_ke_hoach': ['Thiết lập mối quan hệ điều trị tin cậy vững chắc với một bác sĩ đa khoa duy nhất hẹn khám '
                        'định kỳ đều đặn không phụ thuộc vào việc có triệu chứng mới hay không, tránh chỉ định các xét '
                        'nghiệm xâm lấn hoặc thủ thuật không cần thiết.',
                        'Chỉ định liệu pháp hành vi nhận thức CBT nhằm chuyển hướng sự chú ý của bệnh nhân khỏi các '
                        'cảm giác cơ thể và giải quyết các xung đột tâm lý tiềm ẩn.',
                        'Dùng thuốc chống trầm cảm ức chế tái hấp thu serotonin-norepinephrine SNRI Duloxetine hoặc '
                        'Venlafaxine liều thấp để điều hòa ngưỡng dẫn truyền cảm giác đau trung ương.',
                        'Thừa nhận nỗi đau đớn khó chịu thực tế của bệnh nhân nhưng giải thích bằng cơ chế nhạy cảm '
                        'hóa hệ thần kinh trung ương thay vì bệnh lý nội tạng ác tính.',
                        'Khuyến khích bệnh nhân tham gia các hoạt động thể chất nhẹ nhàng như đi bộ dưỡng sinh yoga để '
                        'phục hồi chức năng thể chất hàng ngày.',
                        'Hội chẩn bác sĩ chuyên khoa Tâm thần và Tâm lý học lâm sàng, phối hợp người nhà tạo môi '
                        'trường động viên khích lệ tránh củng cố hành vi người bệnh than thở.'],
  'kham': 'Bệnh nhân mang theo một tập hồ sơ xét nghiệm dày cộp từ nhiều bệnh viện, than phiền đau nhức khắp người đau '
          'lưng tức ngực tê rát dạ dày, khám thực thể toàn diện không phát hiện điểm đau khu trú hay tổn thương thực '
          'thể.',
  'chan_doan': 'Rối loạn dạng cơ thể Somatization Disorder mạn tính thể đa triệu chứng theo tiêu chuẩn DSM-5.',
  'ke_hoach': 'Thiết lập mối quan hệ điều trị tin cậy vững chắc với một bác sĩ đa khoa duy nhất hẹn khám định kỳ đều '
              'đặn không phụ thuộc vào việc có triệu chứng mới hay không, tránh chỉ định các xét nghiệm xâm lấn hoặc '
              'thủ thuật không cần thiết.'},
 {'ten': 'rối loạn nghi bệnh Hypochondriasis sợ mắc bệnh hiểm nghèo',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['sự bận tâm hoặc nỗi sợ dai dẳng quá mức rằng bản thân đang mắc phải một căn bệnh hiểm nghèo nan y như ung '
            'thư HIV xơ cứng rải rác',
            'nỗi sợ dựa trên sự diễn giải sai lệch các dấu hiệu sinh lý bình thường hoặc triệu chứng cơ thể rất nhẹ '
            'của bản thân',
            'nỗi sợ bệnh tật vẫn tồn tại bất chấp các kết quả xét nghiệm âm tính và những lời trấn an y khoa đầy đủ '
            'của bác sĩ chuyên khoa'],
  'phu': ['hành vi kiểm tra cơ thể lặp đi lặp lại nhiều lần trong ngày như sờ nắn hạch soi gương đo huyết áp',
          'thường xuyên tìm kiếm thông tin bệnh lý trên mạng internet Cyberchondria dẫn đến hoảng loạn gia tăng',
          'hoặc ngược lại có hành vi né tránh hoàn toàn việc đi khám bệnh hay xem các chương trình y tế vì quá sợ hãi'],
  'bien_the_kham': ['Bệnh nhân mang theo danh sách ghi chép chi tiết các số đo nhịp tim huyết áp từng giờ trong tháng, '
                    'yêu cầu bác sĩ sờ một nốt gồ bình thường ở cổ và khẳng định đó là u ác tính, khám lâm sàng không '
                    'có u hạch bất thường.',
                    'Khám thực thể toàn diện không phát hiện bất kỳ dấu hiệu tổn thương thực thể bệnh học nào, bệnh '
                    'nhân liên tục hỏi lại và yêu cầu giải thích tại sao mình lại có cảm giác đau âm ỉ vùng gan.',
                    'Nét mặt âu lo căng thẳng tột độ, chăm chú quan sát từng động tác khám của bác sĩ, mạch 82 l/p, '
                    'bụng mềm gan lách không to, tuyến giáp bình thường.',
                    'Bệnh nhân tha thiết xin được chụp MRI toàn thân và làm các xét nghiệm chỉ dấu ung thư tumor '
                    'markers, khám hệ hô hấp và tiêu hóa hoàn toàn bình thường.',
                    'Tác phong bồn chồn đứng ngồi không yên, kể rằng đã đọc trên mạng thấy triệu chứng mệt mỏi của '
                    'mình giống hệt bệnh xơ cột bên teo cơ, khám cơ lực và phản xạ hoàn toàn tốt.',
                    'Khám lâm sàng ngoài tình trạng lo âu quá mức về sức khỏe thì các cơ quan phủ tạng đều trong giới '
                    'hạn bình thường, không có thiếu máu hay suy kiệt.'],
  'bien_the_chan_doan': ['Rối loạn lo âu bệnh tật Illness Anxiety Disorder chứng nghi bệnh Hypochondriasis mức độ '
                         'nặng.',
                         'Rối loạn nghi bệnh Hypochondriasis nỗi sợ mắc bệnh ung thư nan y mạn tính.',
                         'Chứng nghi bệnh Hypochondriasis thể thường xuyên tìm kiếm sự trấn an y tế.',
                         'Theo dõi rối loạn nghi bệnh Hypochondriasis kết hợp hành vi tìm kiếm bệnh trên mạng '
                         'internet.',
                         'Rối loạn lo âu về sức khỏe Hypochondriasis có hành vi tự kiểm tra cơ thể cưỡng chế.',
                         'Chứng nghi bệnh thể ám ảnh sợ bệnh hiểm nghèo gây suy giảm nghiêm trọng hoạt động nghề '
                         'nghiệp.'],
  'bien_the_ke_hoach': ['Áp dụng liệu pháp nhận thức hành vi CBT tập trung vào việc nhận diện và thay đổi niềm tin sai '
                        'lệch về bệnh tật, hạn chế hành vi tự kiểm tra cơ thể và ngừng tìm kiếm triệu chứng bệnh trên '
                        'internet.',
                        'Chỉ định thuốc chống trầm cảm nhóm SSRI Fluoxetine hoặc Sertraline liều chuẩn để làm giảm sự '
                        'bận tâm ám ảnh cưỡng chế về bệnh tật và hạ thấp mức độ lo âu cơ bản.',
                        'Thiết lập lịch khám định kỳ cố định với bác sĩ tin cậy, thống nhất nguyên tắc không làm các '
                        'xét nghiệm lặp lại vô lý khi không có chỉ định lâm sàng rõ ràng.',
                        'Giáo dục tâm lý cho người bệnh hiểu về hiện tượng khuếch đại cảm giác của não bộ khi chú ý '
                        'quá mức vào một vùng cơ thể.',
                        'Tư vấn người thân trong gia đình không tham gia vào các cuộc thảo luận tranh cãi về bệnh tật '
                        'hay hỗ trợ bệnh nhân kiểm tra cơ thể.',
                        'Theo dõi tiến triển lâm sàng định kỳ qua thang điểm lo âu sức khỏe HAI Health Anxiety '
                        'Inventory, kiên trì duy trì điều trị phối hợp tâm lý dược lý.'],
  'kham': 'Bệnh nhân mang theo danh sách ghi chép chi tiết các số đo nhịp tim huyết áp từng giờ trong tháng, yêu cầu '
          'bác sĩ sờ một nốt gồ bình thường ở cổ và khẳng định đó là u ác tính, khám lâm sàng không có u hạch bất '
          'thường.',
  'chan_doan': 'Rối loạn lo âu bệnh tật Illness Anxiety Disorder chứng nghi bệnh Hypochondriasis mức độ nặng.',
  'ke_hoach': 'Áp dụng liệu pháp nhận thức hành vi CBT tập trung vào việc nhận diện và thay đổi niềm tin sai lệch về '
              'bệnh tật, hạn chế hành vi tự kiểm tra cơ thể và ngừng tìm kiếm triệu chứng bệnh trên internet.'},
 {'ten': 'rối loạn cảm xúc lưỡng cực giai đoạn hưng cảm nhẹ',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['khí sắc tăng cao hưng phấn hoặc dễ cáu gắt bất thường kéo dài liên tục ít nhất bốn ngày liên tiếp',
            'tăng rõ rệt mức năng lượng và hoạt động có mục đích nói nhiều nói nhanh nói dồn dập khó ngắt lời',
            'giảm nhu cầu ngủ rõ rệt chỉ ngủ 2-3 tiếng mỗi đêm nhưng sáng dậy vẫn cảm thấy tràn đầy sinh lực'],
  'phu': ['tự đánh giá bản thân quá cao hoặc có ý tưởng tự cao nhẹ',
          'tư duy bay nhảy ý nghĩ dồn dập nối tiếp nhau chuyển từ chủ đề này sang chủ đề khác nhanh chóng',
          'dễ bị phân tán chú ý tham gia quá mức vào các hoạt động có nguy cơ cao như mua sắm quá tay hoặc đầu tư mạo '
          'hiểm'],
  'bien_the_kham': ['Bệnh nhân ăn mặc sặc sỡ nổi bật, trang điểm đậm, bước vào phòng khám với thái độ niềm nở quá mức, '
                    'bắt tay bác sĩ cười nói huyên thuyên không ngừng, giọng to hào sảng, ý nghĩ bay nhảy chuyển liên '
                    'tục nhiều đề tài.',
                    'Khám tâm thần ghi nhận khí sắc hưng phấn tươi vui, nói rất nhanh khó ngắt lời, tự hào kể về những '
                    'dự án kinh doanh vĩ đại sắp triển khai, tiếp xúc suồng sã thân mật quá mức.',
                    'Bệnh nhân tràn đầy năng lượng, liên tục đi lại trong phòng khám, kể rằng cả tuần nay chỉ ngủ 2 '
                    'tiếng mỗi đêm mà không thấy mệt mỏi, mắt sáng hoạt bát, không có hoang tưởng kỳ quái.',
                    'Tác phong tăng động rõ, nét mặt rạng rỡ tươi cười, tư duy dồn dập bay nhảy, phân tán chú ý khi có '
                    'tiếng động nhỏ ngoài hành lang, không có ảo thanh hay ảo giác.',
                    'Bệnh nhân tự tin thái quá về tài năng và sức khỏe của mình, nói to hào hứng về kế hoạch mua sắm '
                    'nhiều xe hơi, nhận thức bệnh chưa đầy đủ nhưng chưa gây phá vỡ hoàn toàn chức năng xã hội.',
                    'Khí sắc tăng cao pha lẫn dễ nổi cáu khi bị bác sĩ cắt lời, nói nhanh như súng liên thanh, huyết '
                    'áp 130/80 mmHg, mạch 88 l/p, khám thực thể thần kinh bình thường.'],
  'bien_the_chan_doan': ['Rối loạn cảm xúc lưỡng cực typ II giai đoạn hưng cảm nhẹ Hypomanic episode.',
                         'Rối loạn cảm xúc lưỡng cực giai đoạn hưng cảm nhẹ không có triệu chứng loạn thần.',
                         'Đợt hưng cảm nhẹ Hypomania ở bệnh nhân có tiền sử giai đoạn trầm cảm tái diễn.',
                         'Theo dõi rối loạn khí sắc lưỡng cực thể hưng cảm nhẹ có khí sắc tăng cao và giảm ngủ.',
                         'Rối loạn cảm xúc lưỡng cực typ 2 đợt hưng cảm nhẹ tiến triển.',
                         'Hưng cảm nhẹ Hypomania khởi phát ở người lớn có tăng hoạt động và tư duy dồn dập.'],
  'bien_the_ke_hoach': ['Bắt đầu điều trị bằng thuốc chỉnh khí sắc Lithium hoặc Valproate natri Depakine kiểm soát '
                        'nồng độ thuốc trong máu định kỳ, hoặc thuốc chống loạn thần không điển hình thế hệ hai '
                        'Quetiapine hoặc Aripiprazole.',
                        'Ngừng ngay lập tức các thuốc chống trầm cảm nếu bệnh nhân đang dùng vì nguy cơ kích hoạt đảo '
                        'pha chuyển sang hưng cảm nặng hoặc cơn hỗn hợp.',
                        'Xét nghiệm công thức máu chức năng gan men gan chức năng thận creatinin điện giải đồ và chức '
                        'năng tuyến giáp TSH trước khi khởi trị thuốc chỉnh khí sắc.',
                        'Tư vấn vệ sinh giấc ngủ nghiêm ngặt, thiết lập lại nhịp sinh học ngủ thức đều đặn, có thể '
                        'dùng thuốc hỗ trợ giấc ngủ ngắn hạn như Olanzapine liều thấp ban đêm.',
                        'Giáo dục bệnh nhân và người nhà nhận biết các dấu hiệu sớm của đợt hưng cảm nhẹ và trầm cảm, '
                        'quản lý tài chính ngăn ngừa các quyết định chi tiêu mạo hiểm.',
                        'Tái khám định kỳ mỗi 1-2 tuần theo dõi đáp ứng điều trị và các tác dụng phụ của thuốc, duy '
                        'trì thuốc ổn định khí sắc dài hạn phòng ngừa tái phát.'],
  'kham': 'Bệnh nhân ăn mặc sặc sỡ nổi bật, trang điểm đậm, bước vào phòng khám với thái độ niềm nở quá mức, bắt tay '
          'bác sĩ cười nói huyên thuyên không ngừng, giọng to hào sảng, ý nghĩ bay nhảy chuyển liên tục nhiều đề tài.',
  'chan_doan': 'Rối loạn cảm xúc lưỡng cực typ II giai đoạn hưng cảm nhẹ Hypomanic episode.',
  'ke_hoach': 'Bắt đầu điều trị bằng thuốc chỉnh khí sắc Lithium hoặc Valproate natri Depakine kiểm soát nồng độ thuốc '
              'trong máu định kỳ, hoặc thuốc chống loạn thần không điển hình thế hệ hai Quetiapine hoặc Aripiprazole.'},
 {'ten': 'tâm thần phân liệt thể paranoid giai đoạn ổn định',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['tiền sử hoang tưởng bị hại hoặc hoang tưởng liên hệ chi phối hành vi kèm ảo thanh bình phẩm hoặc ra lệnh',
            'các triệu chứng dương tính loạn thần hiện tại đã được kiểm soát tốt hoặc thuyên giảm đáng kể nhờ duy trì '
            'thuốc chống loạn thần đều đặn',
            'người bệnh duy trì được khả năng tự phục vụ sinh hoạt cá nhân và tiếp xúc thực tế tương đối ổn định'],
  'phu': ['cảm xúc có phần cùn mòn giảm biểu lộ cảm xúc trên nét mặt',
          'suy giảm nhẹ tính chủ động và ý chí trong công việc và các mối quan hệ xã hội',
          'nhận thức bệnh ở mức độ trung bình hiểu được sự cần thiết của việc uống thuốc duy trì'],
  'bien_the_kham': ['Bệnh nhân đến khám cùng người nhà với tác phong gọn gàng sạch sẽ, nét mặt có phần ít biểu cảm cùn '
                    'mòn nhẹ, tiếp xúc hợp tác trả lời câu hỏi đúng trọng tâm, khai rằng không còn nghe thấy tiếng nói '
                    'lạ trong đầu.',
                    'Khám tâm thần thấy tư duy mạch lạc rõ ràng, không bộc lộ hoang tưởng bị theo dõi hay đầu độc, '
                    'nhận thức bệnh tốt thừa nhận trước đây mình bị bệnh và nhờ thuốc mới bình phục.',
                    'Bệnh nhân giao tiếp bình tĩnh, giọng nói đều đều ít biến đổi ngữ điệu, ánh mắt tiếp xúc tốt, phủ '
                    'nhận các ảo thanh ra lệnh, định hướng không gian thời gian bản thân chính xác.',
                    'Tác phong điềm tĩnh, không có hành vi bất thường hay kích động, cảm xúc hơi trầm phẳng lặng, bệnh '
                    'nhân kể lại các triệu chứng loạn thần quá khứ như một kỷ niệm xa xôi.',
                    'Tiếp xúc tốt, không phát hiện triệu chứng dương tính cấp thời, vận động không run rẩy, không có '
                    'dấu hiệu hội chứng ngoại tháp do thuốc chống loạn thần.',
                    'Nét mặt hơi cứng đờ do tác dụng phụ nhẹ của thuốc, giao tiếp lịch sự nhã nhặn, tự khai uống thuốc '
                    'Risperidone đều đặn mỗi tối theo đơn của bác sĩ.'],
  'bien_the_chan_doan': ['Tâm thần phân liệt thể Paranoid giai đoạn thuyên giảm ổn định duy trì điều trị ngoại trú.',
                         'Tâm thần phân liệt thể hoang tưởng Paranoid giai đoạn ổn định kiểm soát tốt triệu chứng loạn '
                         'thần.',
                         'Tâm thần phân liệt thể Paranoid mạn tính giai đoạn hồi phục chức năng xã hội.',
                         'Theo dõi tâm thần phân liệt thể Paranoid thuyên giảm hoàn toàn triệu chứng dương tính.',
                         'Tâm thần phân liệt Paranoid giai đoạn duy trì thuốc chống loạn thần thế hệ mới.',
                         'Tâm thần phân liệt thể Paranoid ổn định có triệu chứng âm tính mức độ nhẹ.'],
  'bien_the_ke_hoach': ['Duy trì phác đồ thuốc chống loạn thần không điển hình thế hệ hai Risperidone 2-4mg hoặc '
                        'Olanzapine 5-10mg hoặc Aripiprazole mỗi ngày để phòng ngừa tái phát loạn thần, tuyệt đối '
                        'không tự ý ngừng thuốc.',
                        'Theo dõi định kỳ các tác dụng không mong muốn như hội chứng ngoại tháp tăng cân rối loạn '
                        'lipid máu tăng đường huyết prolactin máu mỗi 3-6 tháng.',
                        'Chỉ định liệu pháp tâm lý hỗ trợ và phục hồi chức năng tâm thần xã hội, khuyến khích bệnh '
                        'nhân tham gia các công việc phù hợp và câu lạc bộ người bệnh.',
                        'Giáo dục người nhà nhận biết các dấu hiệu tái phát sớm như mất ngủ bồn chồn nghi ngờ quay trở '
                        'lại hoặc lơ là vệ sinh cá nhân để đưa đi khám kịp thời.',
                        'Tái khám định kỳ mỗi tháng lĩnh thuốc và đánh giá tình trạng lâm sàng tâm thần, kiểm tra sự '
                        'tuân thủ điều trị của bệnh nhân.',
                        'Tư vấn duy trì lối sống lành mạnh ngủ đủ giấc, tuyệt đối kiêng rượu bia ma túy chất kích '
                        'thích vì là yếu tố nguy cơ hàng đầu kích hoạt bùng phát cơn loạn thần cấp.'],
  'kham': 'Bệnh nhân đến khám cùng người nhà với tác phong gọn gàng sạch sẽ, nét mặt có phần ít biểu cảm cùn mòn nhẹ, '
          'tiếp xúc hợp tác trả lời câu hỏi đúng trọng tâm, khai rằng không còn nghe thấy tiếng nói lạ trong đầu.',
  'chan_doan': 'Tâm thần phân liệt thể Paranoid giai đoạn thuyên giảm ổn định duy trì điều trị ngoại trú.',
  'ke_hoach': 'Duy trì phác đồ thuốc chống loạn thần không điển hình thế hệ hai Risperidone 2-4mg hoặc Olanzapine '
              '5-10mg hoặc Aripiprazole mỗi ngày để phòng ngừa tái phát loạn thần, tuyệt đối không tự ý ngừng thuốc.'},
 {'ten': 'rối loạn ăn uống chán ăn tâm thần Anorexia nervosa',
  'nhom': 'cả hai',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['hạn chế nghiêm ngặt lượng năng lượng ăn vào dẫn đến trọng lượng cơ thể thấp hơn đáng kể so với mức tối '
            'thiểu chuẩn theo lứa tuổi chỉ số BMI dưới 17.5 kg/m2',
            'nỗi sợ hãi mãnh liệt về việc tăng cân hoặc trở nên béo phì dù thể trạng đang gầy trơ xương',
            'rối loạn sâu sắc trong nhận thức về hình thể và cân nặng của bản thân đánh giá quá mức tầm quan trọng của '
            'thân hình gầy gò'],
  'phu': ['da khô bong vảy xuất hiện lớp lông tơ mịn lanugo phủ khắp lưng và cánh tay',
          'mất kinh nguyệt liên tục ít nhất ba chu kỳ ở nữ giới sau tuổi dậy thì',
          'nhịp tim chậm xoang hạ huyết áp và thân nhiệt giảm dưới 36 độ C do hạ chuyển hóa'],
  'bien_the_kham': ['Bệnh nhân gầy gò hốc hác trơ khung xương sườn, mắt trũng sâu má hóp, chỉ số BMI đo được 14.8 '
                    'kg/m2, da khô ráp có lớp lông tơ mịn mọc nhiều ở hai bên má và cẳng tay, mạch chậm 48 l/p, huyết '
                    'áp 85/55 mmHg.',
                    'Thể trạng suy kiệt nặng, teo cơ toàn thân, móng tay giòn dễ gãy, các khớp xương gồ rõ dưới da, '
                    'bệnh nhân vẫn khẳng định đùi và bụng mình còn quá nhiều mỡ.',
                    'Khám thấy da xanh xao lạnh đầu chi, nhiệt độ cơ thể 35.8 độ C, nghe tim nhịp xoang chậm 50 '
                    'lần/phút, tiếng tim mờ, bụng lõm lòng thuyền không sờ thấy u cục.',
                    'Bệnh nhân mặc nhiều lớp áo dày để che giấu thân hình gầy guộc và giữ ấm, BMI 15.2 kg/m2, niêm mạc '
                    'nhợt nhạt, phù nhẹ hai mắt cá chân do giảm albumin máu.',
                    'Khám dinh dưỡng thấy thiếu năng lượng trường diễn mức độ nặng, mạch quay yếu chậm 46 l/p, huyết '
                    'áp thấp, không có dấu hiệu viêm loét miệng.',
                    'Thể trạng suy dinh dưỡng nghiêm trọng, xương sườn nhô cao, bụng xẹp sâu, hai chi teo tóp, bệnh '
                    'nhân biểu lộ nỗi lo lắng sợ hãi khi bác sĩ yêu cầu tăng cân.'],
  'bien_the_chan_doan': ['Rối loạn ăn uống chán ăn tâm thần Anorexia Nervosa thể hạn chế ăn uống mức độ nặng.',
                         'Chán ăn tâm thần Anorexia Nervosa thể thanh lọc tống thức ăn ra ngoài suy dinh dưỡng nặng.',
                         'Rối loạn chán ăn tâm thần Anorexia Nervosa biến chứng mất kinh và rối loạn điện giải.',
                         'Theo dõi chán ăn tâm thần Anorexia Nervosa có chỉ số khối cơ thể BMI dưới 15.',
                         'Bệnh lý rối loạn ăn uống Anorexia Nervosa nguy cơ biến chứng tim mạch do suy kiệt.',
                         'Chán ăn do căn nguyên tâm lý Anorexia Nervosa kèm biến dạng nhận thức hình thể nặng.'],
  'bien_the_ke_hoach': ['Lập kế hoạch can thiệp dinh dưỡng từng bước phối hợp bác sĩ tâm thần và chuyên gia dinh '
                        'dưỡng, bắt đầu nâng dần lượng calo từ tốn phòng ngừa hội chứng nuôi ăn lại Refeeding Syndrome '
                        'nguy hiểm đến tính mạng, xét nghiệm điện giải đồ phospho magie canxi hàng ngày.',
                        'Chỉ định liệu pháp tâm lý chuyên sâu liệu pháp nhận thức hành vi nâng cao CBT-E hoặc liệu '
                        'pháp gia đình Maudsley cho trẻ vị thành niên, hỗ trợ điều chỉnh nhận thức sai lệch về hình '
                        'ảnh cơ thể.',
                        'Theo dõi điện tâm đồ liên tục tầm soát khoảng QT kéo dài và rối loạn nhịp tim do nhịp chậm '
                        'suy dinh dưỡng, làm siêu âm tim đánh giá chức năng co bóp và tràn dịch màng ngoài tim.',
                        'Nhập viện điều trị nội trú khẩn cấp nếu BMI dưới 13.5 hoặc có hạ huyết áp tư thế nhịp tim '
                        'dưới 40 l/p hoặc rối loạn điện giải nghiêm trọng.',
                        'Cân nhắc dùng thuốc chống loạn thần Olanzapine liều thấp 2.5-5mg buổi tối để hỗ trợ giảm bớt '
                        'nỗi ám ảnh sợ ăn tăng cảm giác ngon miệng và hỗ trợ tăng cân.',
                        'Tư vấn gia đình về chế độ chăm sóc và giám sát các bữa ăn của người bệnh, kiên trì trị liệu '
                        'dài hạn nhằm phục hồi cả thể chất lẫn tâm lý.'],
  'kham': 'Bệnh nhân gầy gò hốc hác trơ khung xương sườn, mắt trũng sâu má hóp, chỉ số BMI đo được 14.8 kg/m2, da khô '
          'ráp có lớp lông tơ mịn mọc nhiều ở hai bên má và cẳng tay, mạch chậm 48 l/p, huyết áp 85/55 mmHg.',
  'chan_doan': 'Rối loạn ăn uống chán ăn tâm thần Anorexia Nervosa thể hạn chế ăn uống mức độ nặng.',
  'ke_hoach': 'Lập kế hoạch can thiệp dinh dưỡng từng bước phối hợp bác sĩ tâm thần và chuyên gia dinh dưỡng, bắt đầu '
              'nâng dần lượng calo từ tốn phòng ngừa hội chứng nuôi ăn lại Refeeding Syndrome nguy hiểm đến tính mạng, '
              'xét nghiệm điện giải đồ phospho magie canxi hàng ngày.'},
 {'ten': 'rối loạn TIC vận động và âm thanh mạn tính',
  'nhom': 'nhi',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['xuất hiện các cử động co giật cơ đột ngột nhanh lặp đi lặp lại không nhịp điệu tic vận động hoặc phát âm '
            'thanh không tự chủ tic âm thanh kéo dài trên một năm',
            'các tật tic vận động thường gặp như nháy mắt liên tục giật cơ mặt lắc đầu nhún vai giật cơ tay',
            'các tật tic âm thanh thường gặp như hắng giọng ho khẹc tặc lưỡi khịt mũi gầm gừ phát ra tiếng kêu bất '
            'thường'],
  'phu': ['cảm giác thôi thúc khó chịu từ bên trong cơ thể thôi thúc tiền triệu trước khi thực hiện động tác tic và '
          'cảm thấy nhẹ nhõm sau khi làm',
          'các tật tic tăng lên rõ rệt khi trẻ căng thẳng mệt mỏi lo âu và giảm đi khi tập trung chú ý vào hoạt động '
          'yêu thích',
          'trẻ có thể kìm nén cơn tic trong một khoảng thời gian ngắn nhưng sau đó cơn tic bùng phát dồn dập'],
  'bien_the_kham': ['Trong lúc ngồi khám trẻ liên tục nháy mắt hai bên theo từng chùm 3-4 cái kèm theo giật cơ khóe '
                    'miệng và giật nhún vai trái, thỉnh thoảng phát ra tiếng hắng giọng khẹc khẹc ở cổ họng, khám thần '
                    'kinh vận động bình thường.',
                    'Quan sát thấy trẻ có các động tác giật lắc đầu nhanh sang phải lặp đi lặp lại mỗi 20-30 giây, kèm '
                    'tiếng khịt mũi ngắn, khi hỏi chuyện trẻ có thể nín được khoảng 1 phút rồi lại giật liên hồi.',
                    'Trẻ tỉnh táo giao tiếp thông minh, trong buổi khám ghi nhận các cử động nháy mắt liên tục co giật '
                    'cơ vòng mi mắt và nhếch mép, không có yếu liệt chi hay rối loạn cảm giác.',
                    'Ghi nhận tật tic âm thanh dạng ho khan hắng giọng cách quãng không kèm viêm họng, kết hợp nhún '
                    'một bên vai lên cao, khám đáy mắt và phản xạ gân xương hoàn toàn bình thường.',
                    'Trẻ biểu lộ cử động nhăn trán chớp mắt dồn dập, cơ lực hai tay hai chân 5/5, trương lực cơ bình '
                    'thường, các động tác phối hợp vận động ngón tay ngón chân chính xác.',
                    'Khám lâm sàng nhi khoa tổng quát bình thường, quan sát thấy trẻ thỉnh thoảng phát ra âm thanh tặc '
                    'lưỡi và giật nhẹ cẳng tay phải, không có co giật toàn thể kiểu động kinh.'],
  'bien_the_chan_doan': ['Rối loạn Tic vận động và âm thanh kết hợp hội chứng Tourette mạn tính ở trẻ em.',
                         'Rối loạn Tic vận động mạn tính Chronic Motor Tic Disorder kéo dài trên 12 tháng.',
                         'Rối loạn Tic âm thanh mạn tính kèm hắng giọng khịt mũi liên tục.',
                         'Theo dõi rối loạn Tic mạn tính ở trẻ em ảnh hưởng đến sinh hoạt học đường.',
                         'Rối loạn Tic mạn tính kết hợp hội chứng tăng động giảm chú ý ADHD nhẹ.',
                         'Rối loạn Tic vận động âm thanh mạn tính thể đáp ứng với can thiệp hành vi.'],
  'bien_the_ke_hoach': ['Chỉ định can thiệp hành vi toàn diện cho tật tic CBIT Comprehensive Behavioral Intervention '
                        'for Tics rèn luyện nhận thức về cảm giác thôi thúc tiền triệu và tập phản ứng đối kháng cạnh '
                        'tranh thay thế tật tic.',
                        'Giải thích cho phụ huynh và giáo viên hiểu rõ bản chất không tự chủ của tật tic, tuyệt đối '
                        'không la mắng trừng phạt hay nhắc nhở quá mức khiến trẻ thêm căng thẳng làm tic nặng hơn.',
                        'Dùng thuốc nếu tật tic gây đau cơ chấn thương hoặc ảnh hưởng nghiêm trọng đến học tập giao '
                        'tiếp như thuốc đồng vận alpha-2 adrenergic Clonidine hoặc Guanfacine, hoặc thuốc chống loạn '
                        'thần liều thấp Aripiprazole.',
                        'Làm điện não đồ EEG để loại trừ các cơn co giật cục bộ vận động của bệnh động kinh, xét '
                        'nghiệm loại trừ múa giật Sydenham sau nhiễm liên cầu.',
                        'Tạo môi trường học tập thoải mái giảm áp lực thi cử, hướng dẫn trẻ các bài tập thở thư giãn '
                        'và duy trì giấc ngủ đủ thời lượng mỗi ngày.',
                        'Hẹn tái khám định kỳ mỗi 1-2 tháng theo dõi diễn tiến tần số và cường độ của các tật tic qua '
                        'thang đo độ nặng Tic Yale YGTSS.'],
  'kham': 'Trong lúc ngồi khám trẻ liên tục nháy mắt hai bên theo từng chùm 3-4 cái kèm theo giật cơ khóe miệng và '
          'giật nhún vai trái, thỉnh thoảng phát ra tiếng hắng giọng khẹc khẹc ở cổ họng, khám thần kinh vận động bình '
          'thường.',
  'chan_doan': 'Rối loạn Tic vận động và âm thanh kết hợp hội chứng Tourette mạn tính ở trẻ em.',
  'ke_hoach': 'Chỉ định can thiệp hành vi toàn diện cho tật tic CBIT Comprehensive Behavioral Intervention for Tics '
              'rèn luyện nhận thức về cảm giác thôi thúc tiền triệu và tập phản ứng đối kháng cạnh tranh thay thế tật '
              'tic.'},
 {'ten': 'rối loạn ác mộng kinh hoàng khi ngủ ban đêm',
  'nhom': 'nhi',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['những đợt thức giấc đột ngột lúc nửa đêm kèm theo tiếng la hét khóc thét kinh hoàng biểu lộ nỗi khiếp sợ '
            'tột độ xảy ra ở một phần ba đầu của giấc ngủ đêm trong giai đoạn giấc ngủ NREM sóng chậm',
            'dấu hiệu kích hoạt thần kinh thực vật dữ dội trong cơn như tim đập nhanh thở dồn dập vã mồ hôi giãn đồng '
            'tử và tăng trương lực cơ',
            'người bệnh hoàn toàn không đáp ứng với những nỗ lực dỗ dành vỗ về của người thân xung quanh và mất trí '
            'nhớ hoàn toàn về sự việc khi tỉnh dậy vào sáng hôm sau'],
  'phu': ['thường gặp ở trẻ em lứa tuổi từ 4 đến 12 tuổi với xu hướng giảm dần khi lớn lên',
          'trẻ ở trong trạng thái lơ mơ lú lẫn không nhận ra cha mẹ trong cơn kéo dài từ vài phút đến 15 phút',
          'sau cơn trẻ nhanh chóng ngủ thiếp trở lại bình thường và không có ký ức về giấc mơ'],
  'bien_the_kham': ['Khám lâm sàng vào ban ngày trẻ hoàn toàn bình thường, tinh thần vui vẻ nhanh nhẹn, tiếp xúc hoạt '
                    'bát, khám hệ thần kinh không phát hiện tổn thương khu trú, mẹ kể đêm nào trẻ cũng ngồi bật dậy '
                    'thét lớn mắt mở trừng trừng không nhận ra ai.',
                    'Thể trạng trẻ phát triển tốt theo lứa tuổi, khám tim phổi họng bình thường, trương lực cơ và phản '
                    'xạ gân xương hai bên đều, tâm lý trẻ thoải mái không có dấu hiệu trầm cảm.',
                    'Trẻ tỉnh táo hoàn toàn, trí tuệ phát triển phù hợp lứa tuổi, không có dị tật thần kinh sọ não, '
                    'khám tai mũi họng thông thoáng không có phì đại amidan gây ngưng thở khi ngủ.',
                    'Khám thực thể nhi khoa tổng quát chưa ghi nhận bệnh lý nội khoa, nhịp tim đều 85 l/p, bụng mềm, '
                    'trẻ không nhớ gì về các cơn la hét hoảng loạn lúc ban đêm.',
                    'Trẻ hợp tác tốt khi khám, kiểm tra phản xạ vận động cảm giác bình thường, không có dấu hiệu co '
                    'giật ban ngày, các chỉ số phát triển thể chất trong bách phân vị chuẩn.',
                    'Khám lâm sàng thần kinh nhi bình thường, đồng tử hai bên đều phản xạ ánh sáng tốt, trẻ không có '
                    'rối loạn hành vi trong giờ học hay khi chơi với bạn bè.'],
  'bien_the_chan_doan': ['Rối loạn kinh hoàng ban đêm Sleep Terrors rối loạn giấc ngủ NREM ở trẻ em.',
                         'Rối loạn giấc ngủ hoảng sợ ban đêm Night Terrors thể mạn tính lặp lại.',
                         'Rối loạn dạng ác mộng kinh hoàng trong giấc ngủ sâu Parasomnia NREM lành tính.',
                         'Theo dõi chứng kinh hoàng khi ngủ Sleep Terrors cần phân biệt với động kinh thùy trán ban '
                         'đêm.',
                         'Rối loạn hoảng hốt ban đêm ở trẻ em có kích hoạt thần kinh thực vật mạnh.',
                         'Hội chứng cơn kinh hoàng khi ngủ ban đêm Parasomnia tuổi ấu thơ diễn tiến lành tính.'],
  'bien_the_ke_hoach': ['Trấn an cha mẹ giải thích bản chất lành tính không gây tổn thương não của cơn kinh hoàng ban '
                        'đêm và bệnh sẽ tự thoái lui theo lứa tuổi khi hệ thần kinh hoàn thiện, hướng dẫn cha mẹ chỉ '
                        'cần đứng bên cạnh quan sát bảo vệ trẻ khỏi té ngã chấn thương không cố đánh thức hay giữ chặt '
                        'trẻ trong cơn.',
                        'Thực hiện biện pháp đánh thức theo lịch trình Scheduled Awakening đánh thức trẻ nhẹ nhàng dậy '
                        'trước thời điểm thường xảy ra cơn khoảng 15-30 phút trong vài tuần liên tiếp để làm gián đoạn '
                        'chu kỳ giấc ngủ sâu.',
                        'Tối ưu hóa vệ sinh giấc ngủ cho trẻ bảo đảm trẻ ngủ đủ giấc tránh tình trạng thiếu ngủ mệt '
                        'mỏi ban ngày vì thiếu ngủ là yếu tố kích hoạt hàng đầu của cơn kinh hoàng.',
                        'Làm đo đa ký giấc ngủ Polysomnography hoặc điện não đồ video giấc ngủ đêm nếu cơn xảy ra '
                        'nhiều lần trong đêm kéo dài bất thường hoặc có nghi ngờ co giật động kinh ban đêm.',
                        'Rà soát và loại bỏ các yếu tố gây căng thẳng tâm lý ban ngày của trẻ ở trường học gia đình, '
                        'tránh xem tivi xem điện thoại hoặc các hình ảnh bạo lực trước giờ đi ngủ.',
                        'Hạn chế sử dụng thuốc ở trẻ em, chỉ cân nhắc dùng thuốc nhóm Benzodiazepine Clonazepam liều '
                        'rất thấp ngắn hạn trong trường hợp cơn quá dày đặc gây kiệt sức cho trẻ và gia đình.'],
  'kham': 'Khám lâm sàng vào ban ngày trẻ hoàn toàn bình thường, tinh thần vui vẻ nhanh nhẹn, tiếp xúc hoạt bát, khám '
          'hệ thần kinh không phát hiện tổn thương khu trú, mẹ kể đêm nào trẻ cũng ngồi bật dậy thét lớn mắt mở trừng '
          'trừng không nhận ra ai.',
  'chan_doan': 'Rối loạn kinh hoàng ban đêm Sleep Terrors rối loạn giấc ngủ NREM ở trẻ em.',
  'ke_hoach': 'Trấn an cha mẹ giải thích bản chất lành tính không gây tổn thương não của cơn kinh hoàng ban đêm và '
              'bệnh sẽ tự thoái lui theo lứa tuổi khi hệ thần kinh hoàn thiện, hướng dẫn cha mẹ chỉ cần đứng bên cạnh '
              'quan sát bảo vệ trẻ khỏi té ngã chấn thương không cố đánh thức hay giữ chặt trẻ trong cơn.'},
 {'ten': 'nghiện rượu mạn tính hội chứng cai rượu nhẹ',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'tâm thần',
  'da_duyet': False,
  'chinh': ['tiền sử uống rượu lượng lớn kéo dài nhiều năm kèm theo hiện tượng dung nạp tăng liều và mất kiểm soát '
            'hành vi uống rượu',
            'xuất hiện run tay thô biên độ lớn kèm vã mồ hôi lo âu bồn chồn trong vòng 6 đến 24 giờ sau khi ngừng hoặc '
            'giảm lượng rượu uống',
            'các triệu chứng thuyên giảm nhanh chóng khi người bệnh uống lại một lượng rượu vào buổi sáng'],
  'phu': ['mất ngủ trằn trọc ác mộng khi ngủ chập chờn',
          'buồn nôn nôn khan chán ăn vào buổi sáng sớm',
          'nhịp tim nhanh hồi hộp đánh trống ngực huyết áp dao động tăng nhẹ'],
  'bien_the_kham': ['Bàn tay run thô rõ rệt khi giơ thẳng ra trước mặt, lòng bàn tay ướt đẫm mồ hôi, da mặt và cổ đỏ '
                    'bừng có nhiều mạch máu hình sao sao mạch, nhịp tim nhanh 102 l/p, huyết áp 145/90 mmHg, nét mặt '
                    'bồn chồn lo lắng.',
                    'Bệnh nhân vào viện trong tình trạng bồn chồn bứt rứt, run đầu ngón tay và lưỡi khi thè lưỡi, hơi '
                    'thở còn mùi rượu cũ thoang thoảng, khám bụng gan to dưới bờ sườn 3cm mật độ chắc trơn láng.',
                    'Khám thấy hội chứng thần kinh thực vật tăng hoạt, mạch nhanh 98 lần/phút, run tay biên độ lớn '
                    'tăng lên khi cầm cốc nước, phản xạ gân xương hai bên tăng nhẹ, không có ảo giác hay sảng run.',
                    'Bệnh nhân than mệt mỏi run rẩy vã mồ hôi toàn thân từ sáng sớm sau khi ngưng rượu tối qua, tiếp '
                    'xúc tỉnh táo định hướng không gian thời gian tốt, tim đập nhanh đều.',
                    'Thể trạng gầy, da sạm lòng bàn tay son, run giật ngón tay rõ khi duỗi thẳng các ngón, huyết áp '
                    'tăng 150/95 mmHg, nghe tim nhịp nhanh xoang không có tiếng thổi.',
                    'Bệnh nhân kích thích lo âu nhẹ, run rẩy hai tay và run giật mí mắt, vã mồ hôi trán, nhiệt độ 37.4 '
                    'độ C, mạch 100 l/p, khám thần kinh không có liệt khu trú.'],
  'bien_the_chan_doan': ['Nghiện rượu mạn tính Alcohol Dependence hội chứng cai rượu mức độ nhẹ đến trung bình theo '
                         'thang CIWA-Ar.',
                         'Hội chứng cai rượu không biến chứng ở bệnh nhân nghiện rượu mạn tính có gan nhiễm mỡ.',
                         'Nghiện rượu mạn tính đợt cai rượu cấp tính có biểu hiện run tay và rối loạn thần kinh thực '
                         'vật.',
                         'Theo dõi hội chứng cai rượu nhẹ thang điểm CIWA-Ar dưới 10 điểm chưa có sảng run.',
                         'Rối loạn sử dụng rượu mạn tính hội chứng cai rượu khởi phát sớm sau giảm lượng cồn.',
                         'Nghiện rượu mạn tính hội chứng cai rượu nhẹ kết hợp tăng men gan do rượu.'],
  'bien_the_ke_hoach': ['Dùng thuốc nhóm Benzodiazepine Diazepam đường uống liều giảm dần từng ngày theo phác đồ hướng '
                        'dẫn của thang điểm CIWA-Ar để phòng ngừa co giật do cai rượu và ngăn tiến triển thành sảng '
                        'run Delirium Tremens.',
                        'Bổ sung Vitamin B1 Thiamine liều cao 100-200mg tiêm bắp hoặc truyền tĩnh mạch trước khi '
                        'truyền đường glucose để phòng ngừa hội chứng não Wernicke cấp tính, bổ sung vitamin nhóm B '
                        'tổng hợp và acid folic.',
                        'Bù nước và điện giải đường uống hoặc truyền dịch tĩnh mạch cân bằng điện giải đồ, kiểm tra '
                        'chức năng gan men gan AST ALT GGT và đông máu toàn bộ.',
                        'Đánh giá thang điểm cai rượu CIWA-Ar định kỳ mỗi 4-6 giờ để điều chỉnh liều thuốc an dịu '
                        'Diazepam kịp thời theo mức độ nặng của triệu chứng.',
                        'Tư vấn động viên người bệnh tham gia chương trình cai nghiện rượu dài hạn sau khi cắt cơn '
                        'cai, xem xét dùng thuốc hỗ trợ chống thèm rượu như Naltrexone hoặc Acamprosate.',
                        'Tuyên truyền tác hại của rượu lên gan tim thần kinh cho bệnh nhân và gia đình, hướng dẫn '
                        'người nhà theo dõi phát hiện sớm các dấu hiệu sảng run như sốt cao nói lảm nhảm ảo thị để đưa '
                        'vào viện cấp cứu.'],
  'kham': 'Bàn tay run thô rõ rệt khi giơ thẳng ra trước mặt, lòng bàn tay ướt đẫm mồ hôi, da mặt và cổ đỏ bừng có '
          'nhiều mạch máu hình sao sao mạch, nhịp tim nhanh 102 l/p, huyết áp 145/90 mmHg, nét mặt bồn chồn lo lắng.',
  'chan_doan': 'Nghiện rượu mạn tính Alcohol Dependence hội chứng cai rượu mức độ nhẹ đến trung bình theo thang '
               'CIWA-Ar.',
  'ke_hoach': 'Dùng thuốc nhóm Benzodiazepine Diazepam đường uống liều giảm dần từng ngày theo phác đồ hướng dẫn của '
              'thang điểm CIWA-Ar để phòng ngừa co giật do cai rượu và ngăn tiến triển thành sảng run Delirium '
              'Tremens.'},
 {'ten': 'xơ cứng bì phổi tổn thương phổi kẽ',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['khó thở khi gắng sức tăng dần kèm ho khan dai dẳng trên bệnh nhân xơ cứng bì hệ thống đã xác định',
            'nghe phổi phát hiện ran nổ nhỏ hạt khô cuối thì hít vào như tiếng mở khóa nhám Velcro ở hai đáy phổi',
            'hình ảnh tổn thương mô kẽ dạng lưới mờ kính và giãn phế quản co kéo trên phim chụp cắt lớp vi tính lồng '
            'ngực độ phân giải cao HRCT'],
  'phu': ['da ngón tay dày cứng mất nếp nhăn xơ cứng ngón tay xơ cứng da mặt',
          'hiện tượng Raynaud tái nhợt tím đỏ các đầu ngón tay khi tiếp xúc lạnh',
          'dung tích sống gắng sức FVC và độ khuếch tán khí qua màng phế nang mao mạch DLCO giảm tiến triển'],
  'bien_the_kham': ['Nghe hai đáy phổi có ran nổ khô dạng Velcro rất rõ cuối thì hít vào, da các ngón tay xơ cứng bóng '
                    'láng hạn chế duỗi thẳng các ngón, da mặt căng mất nếp nhăn quanh miệng, SpO2 93% khí phòng.',
                    'Khám thấy da hai bàn tay dày cứng co rút ngón nhẹ, ngón tay hình búp chuối, nghe phổi hai bên đáy '
                    'nghe nhiều ran nổ mịn như tiếng xé băng dán velcro, không có ran ẩm ran rít.',
                    'Khó thở nhẹ khi đi bộ trên bằng phẳng, tím nhẹ các đầu ngón tay khi trời lạnh, nghe phổi phát '
                    'hiện ran nổ kẽ đặc trưng rải rác hai đáy phổi, tiếng T2 phổi không đanh.',
                    'Da mặt căng bóng mũi nhọn môi mỏng có các vết giãn mạch nông ở ngực, nghe phổi có ran nổ khô hai '
                    'phế trường tập trung nhiều ở thùy dưới hai bên, nhịp thở 22 l/p.',
                    'Các đầu ngón tay có vết sẹo lõm nhỏ do thiếu máu đầu chi cũ, nghe đáy phổi hai bên rải rác ran nổ '
                    'âm sắc cao cuối thì hít vào, không có phù ngoại biên, tim đều rõ.',
                    'Khám phổi thấy rì rào phế nang giảm nhẹ kèm ran nổ khô vùng đáy hai bên, da cẳng tay và bàn tay '
                    'xơ cứng không véo được nếp gấp da, SpO2 giảm xuống 89% sau khi đi bộ 6 phút.'],
  'bien_the_chan_doan': ['Bệnh phổi kẽ liên quan xơ cứng bì hệ thống SSc-ILD tổn thương dạng viêm phổi kẽ không đặc '
                         'hiệu NSIP.',
                         'Xơ cứng bì toàn thể biến chứng bệnh phổi mô kẽ tiến triển có suy giảm chức năng hô hấp.',
                         'Bệnh phổi kẽ do xơ cứng bì SSc-ILD giai đoạn hoạt động cần điều trị thuốc ức chế miễn dịch.',
                         'Theo dõi xơ cứng bì tổn thương phổi kẽ thể xơ hóa mô kẽ đáy phổi hai bên.',
                         'Bệnh mô liên kết xơ cứng bì biến chứng xơ hóa phổi kẽ và giảm độ khuếch tán DLCO.',
                         'Xơ cứng bì phổi kẽ mạn tính có suy giảm dung tích sống gắng sức FVC.'],
  'bien_the_ke_hoach': ['Đo chức năng thông khí phổi toàn thân bao gồm thể tích phổi TLC FVC và đo độ khuếch tán khí '
                        'DLCO định kỳ mỗi 3-6 tháng để theo dõi tiến triển xơ hóa, chụp CT ngực độ phân giải cao HRCT '
                        'đánh giá diện tích tổn thương kính mờ và xơ hóa.',
                        'Bắt đầu điều trị ức chế miễn dịch bằng Mycophenolate Mofetil MMF liều 2-3g mỗi ngày để làm '
                        'chậm sự suy giảm chức năng phổi, hoặc cân nhắc phối hợp thuốc chống xơ hóa Nintedanib nếu '
                        'bệnh phổi kẽ tiến triển nhanh.',
                        'Tầm soát tăng áp động mạch phổi phối hợp bằng siêu âm Doppler tim màu định kỳ đo vận tốc dòng '
                        'hở van ba lá và đo NT-proBNP máu.',
                        'Tư vấn tiêm phòng vắc xin cúm và phế cầu hàng năm phòng ngừa nhiễm trùng hô hấp cấp kích hoạt '
                        'đợt cấp suy hô hấp, hướng dẫn tập phục hồi chức năng hô hấp tại nhà.',
                        'Bảo vệ giữ ấm bàn tay bàn chân tránh lạnh tuyệt đối để giảm các cơn co thắt mạch máu Raynaud, '
                        'dùng thuốc chẹn kênh canxi Nifedipine liều thấp nếu cần thiết.',
                        'Hội chẩn đa chuyên khoa Khớp Miễn dịch và Hô hấp, đánh giá chỉ định truyền tĩnh mạch '
                        'Cyclophosphamide hoặc kháng thể đơn dòng Tocilizumab nếu bệnh nhân không dung nạp với MMF.'],
  'kham': 'Nghe hai đáy phổi có ran nổ khô dạng Velcro rất rõ cuối thì hít vào, da các ngón tay xơ cứng bóng láng hạn '
          'chế duỗi thẳng các ngón, da mặt căng mất nếp nhăn quanh miệng, SpO2 93% khí phòng.',
  'chan_doan': 'Bệnh phổi kẽ liên quan xơ cứng bì hệ thống SSc-ILD tổn thương dạng viêm phổi kẽ không đặc hiệu NSIP.',
  'ke_hoach': 'Đo chức năng thông khí phổi toàn thân bao gồm thể tích phổi TLC FVC và đo độ khuếch tán khí DLCO định '
              'kỳ mỗi 3-6 tháng để theo dõi tiến triển xơ hóa, chụp CT ngực độ phân giải cao HRCT đánh giá diện tích '
              'tổn thương kính mờ và xơ hóa.'},
 {'ten': 'bệnh u hạt Sarcoidosis phổi hạch rốn phổi',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['hình ảnh phì đại hạch rốn phổi hai bên đối xứng kèm theo hoặc không kèm hạch cạnh khí quản trên phim chụp '
            'X-quang hoặc CT ngực',
            'kết quả sinh thiết hạch hoặc mô phổi cho thấy tổn thương u hạt biểu mô không bã đậu non-caseating '
            'granulomas',
            'nồng độ men chuyển angiotensin ACE trong huyết thanh tăng cao kèm rối loạn chuyển hóa canxi gây tăng '
            'canxi máu hoặc canxi niệu'],
  'phu': ['ho khan kéo dài từng cơn kèm cảm giác tức nghẽn ngực mơ hồ',
          'sốt nhẹ về chiều mệt mỏi uể oải sụt cân nhẹ',
          'tổn thương da dạng hồng ban nút hoặc sẩn sẹo lupus pernio trên mặt cánh mũi'],
  'bien_the_kham': ['Khám phổi thông khí hai bên đều rõ không nghe thấy ran ẩm hay ran rít, mặt trước hai cẳng chân có '
                    'vài nốt hồng ban nút màu đỏ ấn đau nhẹ, không có hạch ngoại biên sờ thấy dưới da.',
                    'Thể trạng tương đối tốt, nghe tim phổi bình thường, khám da vùng sống mũi và hai cánh má có mảng '
                    'sẩn màu tím đỏ sẫm đặc trưng của lupus pernio, mắt không đỏ không đau.',
                    'Bệnh nhân ho khan từng cơn, nghe phổi rì rào phế nang êm dịu hai bên, khám các nhóm hạch cổ '
                    'thượng đòn nách không to, nhiệt độ cơ thể 37.5 độ C.',
                    'Khám lâm sàng đường hô hấp chưa ghi nhận bất thường tại thực thể phổi, củng mạc mắt trong, kiểm '
                    'tra tuyến mang tai không sưng to, không có phù chi.',
                    'Bệnh nhân than tức ngực nhẹ sau xương ức, nghe phổi trong sáng, mạch 80 l/p, da cẳng chân có vết '
                    'ban đỏ cũ đang thuyên giảm, huyết áp 120/75 mmHg.',
                    'Phổi thông khí tốt đều hai bên phế trường, không ran bệnh lý, khám mắt bằng đèn khe loại trừ viêm '
                    'màng bồ đào phối hợp, hạch góc hàm không sờ chạm.'],
  'bien_the_chan_doan': ['Bệnh u hạt Sarcoidosis phổi giai đoạn I hạch rốn phổi hai bên đối xứng chưa có tổn thương '
                         'nhu mô.',
                         'Bệnh Sarcoidosis phổi giai đoạn II hạch rốn phổi hai bên kèm thâm nhiễm nhu mô phổi kẽ.',
                         'U hạt Sarcoidosis hệ thống biểu hiện ở phổi và da có nồng độ men ACE máu tăng cao.',
                         'Theo dõi bệnh Sarcoidosis phổi thể hạch rốn phổi cần loại trừ bệnh lao và u lympho.',
                         'Bệnh Sarcoidosis lồng ngực thể u hạt không bã đậu có tăng canxi máu nhẹ.',
                         'Hội chứng Lofgren thể cấp tính của bệnh Sarcoidosis gồm hạch rốn phổi hai bên hồng ban nút '
                         'và đau khớp.'],
  'bien_the_ke_hoach': ['Chỉ định nội soi phế quản sinh thiết xuyên thành phế quản dưới hướng dẫn siêu âm nội soi '
                        'EBUS-TBNA lấy mẫu hạch rốn phổi làm mô bệnh học tìm u hạt không hoại tử bã đậu và nhuộm soi '
                        'AFB nuôi cấy MGIT loại trừ lao.',
                        'Đo nồng độ men chuyển ACE huyết thanh nồng độ canxi máu toàn phần canxi ion hóa và canxi nước '
                        'tiểu 24 giờ để phát hiện rối loạn chuyển hóa canxi.',
                        'Chụp CT ngực độ phân giải cao HRCT đánh giá chi tiết đặc điểm hạch trung thất và các nốt vi '
                        'hạt phân bố dọc bó mạch phế quản phổi.',
                        'Theo dõi lâm sàng định kỳ mỗi 3-6 tháng nếu bệnh nhân ở giai đoạn I không có triệu chứng cơ '
                        'năng nghiêm trọng vì tỷ lệ tự thoái lui tự nhiên lên đến trên 60%.',
                        'Khởi trị liệu pháp Corticosteroid đường uống Prednisolone 0.5 mg/kg mỗi ngày nếu có suy giảm '
                        'chức năng hô hấp tổn thương nhu mô tiến triển tổn thương mắt hoặc tăng canxi máu.',
                        'Khám chuyên khoa Mắt soi đáy mắt bằng sinh hiển vi tầm soát viêm màng bồ đào không triệu '
                        'chứng và đo điện tâm đồ tầm soát tổn thương u hạt cơ tim.'],
  'kham': 'Khám phổi thông khí hai bên đều rõ không nghe thấy ran ẩm hay ran rít, mặt trước hai cẳng chân có vài nốt '
          'hồng ban nút màu đỏ ấn đau nhẹ, không có hạch ngoại biên sờ thấy dưới da.',
  'chan_doan': 'Bệnh u hạt Sarcoidosis phổi giai đoạn I hạch rốn phổi hai bên đối xứng chưa có tổn thương nhu mô.',
  'ke_hoach': 'Chỉ định nội soi phế quản sinh thiết xuyên thành phế quản dưới hướng dẫn siêu âm nội soi EBUS-TBNA lấy '
              'mẫu hạch rốn phổi làm mô bệnh học tìm u hạt không hoại tử bã đậu và nhuộm soi AFB nuôi cấy MGIT loại '
              'trừ lao.'},
 {'ten': 'viêm phổi tăng bạch cầu ái toan mạn tính',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['hình ảnh thâm nhiễm phế nang ngoại vi hai bên phổi tạo hình ảnh âm bản của phù phổi photographic negative '
            'of pulmonary edema trên X-quang hoặc CT ngực',
            'tỷ lệ bạch cầu ái toan trong dịch rửa phế quản phế nang BALF tăng rất cao trên 25 phần trăm thường vượt '
            'quá 40 phần trăm',
            'triệu chứng lâm sàng và tổn thương phổi thuyên giảm ngoạn mục nhanh chóng trong vòng 48 giờ sau khi bắt '
            'đầu dùng Corticosteroid'],
  'phu': ['ho khạc đờm trắng khó thở khò khè kéo dài tiến triển trên hai tuần',
          'sốt vừa về chiều ra mồ hôi trộm ban đêm sụt cân rõ rệt',
          'tiền sử bệnh nhân thường có cơ địa hen phế quản hoặc viêm mũi dị ứng từ trước'],
  'bien_the_kham': ['Nghe phổi có ran rít ran ngáy rải rác hai phế trường kèm ran ẩm nhỏ hạt ở hai vùng ngoại vi nách '
                    'và đáy phổi, nhịp thở 24 l/p, SpO2 92% khí phòng, sốt nhẹ 38 độ C.',
                    'Bệnh nhân khó thở khi nói chuyện, nghe phổi hai bên có ran nổ ran ẩm tập trung ở vùng ngoại vi '
                    'dưới màng phổi, tiếng tim nhanh 100 l/p, không phù hai chân.',
                    'Khám thấy tiếng thở khò khè thì thở ra, ran rít rải rác khắp hai phế trường, nhiệt độ 38.2 độ C, '
                    'thể trạng gầy sút cân mệt mỏi, không có ban dị ứng trên da.',
                    'Nhịp thở nhanh 22 lần/phút, nghe phổi rì rào phế nang giảm nhẹ ở vùng ngoại vi hai bên kèm theo '
                    'ran ẩm rải rác, củng mạc mắt không vàng, họng sạch.',
                    'Nghe phổi thấy ran ẩm và ran ngáy hai bên đặc biệt là thùy trên và thùy giữa ngoại biên, bệnh '
                    'nhân ho cơn khạc ít đờm trong, huyết áp 120/80 mmHg.',
                    'Phổi nghe thở khò khè giống cơn hen phế quản nhưng đáp ứng kém với thuốc giãn phế quản, có ran ẩm '
                    'nhỏ hạt vùng ngoại vi lồng ngực, SpO2 93%.'],
  'bien_the_chan_doan': ['Viêm phổi tăng bạch cầu ái toan mạn tính Chronic Eosinophilic Pneumonia CEP bệnh Carrington.',
                         'Viêm phổi ái toan mạn tính thể thâm nhiễm ngoại vi tái phát có tiền sử hen phế quản.',
                         'Bệnh phổi tăng bạch cầu ái toan mạn tính CEP đáp ứng nhanh với liệu pháp Corticoid.',
                         'Theo dõi viêm phổi tăng bạch cầu ái toan mạn tính cần phân biệt với hội chứng Churg-Strauss.',
                         'Viêm phổi ái toan mạn tính thâm nhiễm phế nang hai bên có suy hô hấp nhẹ.',
                         'Hội chứng thâm nhiễm phổi giàu bạch cầu ái toan thể mạn tính CEP.'],
  'bien_the_ke_hoach': ['Tiến hành nội soi phế quản lấy dịch rửa phế quản phế nang BAL đếm công thức tế bào xác định '
                        'tỷ lệ bạch cầu ái toan trên 25% và loại trừ nhiễm nấm hoặc ký sinh trùng đường thở.',
                        'Bắt đầu điều trị bằng Corticoid đường toàn thân Prednisolone 0.5-1 mg/kg mỗi ngày, bệnh nhân '
                        'thường cải thiện triệu chứng ho sốt khó thở rất nhanh trong vòng 24-48 giờ.',
                        'Xét nghiệm công thức máu kiểm tra số lượng bạch cầu ái toan tuyệt đối máu và nồng độ kháng '
                        'thể IgE toàn phần trong huyết thanh.',
                        'Chụp cắt lớp vi tính ngực HRCT kiểm tra sự tan biến nhanh chóng của các đám thâm nhiễm đông '
                        'đặc phế nang ngoại vi sau 1-2 tuần điều trị steroid.',
                        'Lập kế hoạch giảm liều Corticoid rất chậm kéo dài từ 6 tháng đến 1 năm vì nguy cơ tái phát '
                        'bệnh khi ngừng thuốc sớm là rất cao trên 50%.',
                        'Bổ sung canxi vitamin D và thuốc bảo vệ dạ dày trong suốt thời gian dùng corticoid kéo dài, '
                        'theo dõi đường huyết và huyết áp định kỳ.'],
  'kham': 'Nghe phổi có ran rít ran ngáy rải rác hai phế trường kèm ran ẩm nhỏ hạt ở hai vùng ngoại vi nách và đáy '
          'phổi, nhịp thở 24 l/p, SpO2 92% khí phòng, sốt nhẹ 38 độ C.',
  'chan_doan': 'Viêm phổi tăng bạch cầu ái toan mạn tính Chronic Eosinophilic Pneumonia CEP bệnh Carrington.',
  'ke_hoach': 'Tiến hành nội soi phế quản lấy dịch rửa phế quản phế nang BAL đếm công thức tế bào xác định tỷ lệ bạch '
              'cầu ái toan trên 25% và loại trừ nhiễm nấm hoặc ký sinh trùng đường thở.'},
 {'ten': 'bệnh phổi kẽ liên quan hút thuốc lá',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['tiền sử hút thuốc lá nặng nhiều năm từ 20 đến 30 bao năm trở lên',
            'hình ảnh các nốt mờ trung tâm tiểu thùy dạng kính mờ phân bố ưu thế ở các thùy trên phổi trên phim chụp '
            'cắt lớp vi tính HRCT',
            'kết quả sinh thiết mô phổi hoặc dịch rửa phế quản thấy sự tích tụ dày đặc của các đại thực bào chứa sắc '
            'tố màu nâu vàng trong lòng tiểu phế quản hô hấp RB-ILD'],
  'phu': ['ho khan dai dẳng hoặc ho khạc ít đờm nhầy vào buổi sáng',
          'khó thở khi gắng sức tiến triển chậm chạp qua nhiều năm',
          'nghe phổi có ran nổ rải rác hoặc thông khí phổi giảm nhẹ'],
  'bien_the_kham': ['Đầu các ngón tay và móng tay vàng ố do khói thuốc lá, ngực hình thùng nhẹ, nghe phổi có ran nổ '
                    'mịn khô rải rác hai thì hít vào tập trung ở hai thùy trên và giữa, SpO2 94% khí phòng.',
                    'Khám thấy tiếng thở thô ráp hai phế trường, rải rác ran nổ nhỏ hạt ở đỉnh phổi hai bên, nhịp thở '
                    '20 l/p, hơi thở nồng mùi khói thuốc lá mạn tính.',
                    'Bệnh nhân ho hắng từng cơn khạc đờm nhầy trong, nghe rì rào phế nang hai phổi giảm nhẹ, rải rác '
                    'ran ngáy và ran nổ khô thì hít vào, tim mạch bình thường.',
                    'Thể trạng trung bình, niêm mạc môi hơi thâm nhẹ, khám phổi phát hiện ran nổ khô mịn rải rác hai '
                    'bên phổi không cố định, tiếng T2 phổi không mạnh.',
                    'Nghe phổi thấy tiếng thở hơi kéo dài ở thì thở ra kèm theo ran nổ nhỏ hạt thùy trên hai phổi, '
                    'lồng ngực di động đều theo nhịp thở, không có rút lõm lồng ngực.',
                    'Khám hô hấp ghi nhận ran nổ âm sắc cao rải rác hai phế trường, mạch 82 l/p, huyết áp 130/80 mmHg, '
                    'không có ngón tay dùi trống rõ rệt.'],
  'bien_the_chan_doan': ['Bệnh phổi mô kẽ liên quan viêm tiểu phế quản hô hấp RB-ILD do hút thuốc lá.',
                         'Bệnh phổi kẽ liên quan hút thuốc lá Smoking-Related Interstitial Lung Disease thể RB-ILD.',
                         'Bệnh phổi kẽ bong vảy DIP liên quan hút thuốc lá mạn tính nhiều năm.',
                         'Theo dõi bệnh phổi kẽ do khói thuốc lá RB-ILD có tổn thương kính mờ tiểu thùy.',
                         'Bệnh lý mô kẽ phổi liên quan thuốc lá thể tổn thương tiểu phế quản hô hấp có tắc nghẽn nhẹ.',
                         'Bệnh phổi kẽ do hút thuốc lá tiến triển có giảm dung tích khuếch tán khí DLCO.'],
  'bien_the_ke_hoach': ['Tư vấn và thực hiện can thiệp cai nghiện thuốc lá tuyệt đối và vĩnh viễn là biện pháp điều '
                        'trị quan trọng nhất mang tính quyết định sự thoái lui của tổn thương phổi kẽ.',
                        'Đo chức năng thông khí phổi hô hấp ký và đo thể tích kế thân plethysmography kết hợp đo độ '
                        'khuếch tán khí DLCO đánh giá hội chứng hạn chế hoặc tắc nghẽn hỗn hợp.',
                        'Chụp cắt lớp vi tính lồng ngực độ phân giải cao HRCT kiểm tra lại sau 6-12 tháng cai thuốc lá '
                        'để đánh giá sự thoái lui của các nốt mờ trung tâm tiểu thùy.',
                        'Cân nhắc dùng thử Corticosteroid đường uống ngắn hạn Prednisolone liều vừa nếu các triệu '
                        'chứng hô hấp và tổn thương phổi vẫn tiếp tục tiến triển dù đã cai thuốc lá hoàn toàn.',
                        'Tiêm phòng vắc xin phòng bệnh đường hô hấp bao gồm cúm hàng năm vắc xin phế cầu và vắc xin ho '
                        'gà để bảo vệ đường thở tổn thương.',
                        'Khuyến khích bệnh nhân tham gia chương trình tập phục hồi chức năng phổi cải thiện thể lực và '
                        'chất lượng cuộc sống hàng ngày.'],
  'kham': 'Đầu các ngón tay và móng tay vàng ố do khói thuốc lá, ngực hình thùng nhẹ, nghe phổi có ran nổ mịn khô rải '
          'rác hai thì hít vào tập trung ở hai thùy trên và giữa, SpO2 94% khí phòng.',
  'chan_doan': 'Bệnh phổi mô kẽ liên quan viêm tiểu phế quản hô hấp RB-ILD do hút thuốc lá.',
  'ke_hoach': 'Tư vấn và thực hiện can thiệp cai nghiện thuốc lá tuyệt đối và vĩnh viễn là biện pháp điều trị quan '
              'trọng nhất mang tính quyết định sự thoái lui của tổn thương phổi kẽ.'},
 {'ten': 'viêm tiểu phế quản tắc nghẽn sau nhiễm virus',
  'nhom': 'cả hai',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['tắc nghẽn đường thở cố định không hồi phục kéo dài trên 6 tuần sau đợt viêm tiểu phế quản cấp tính nặng '
            'do nhiễm virus Adenovirus RSV hoặc cúm',
            'chỉ số FEV1 và FEV1/FVC giảm nặng không đáp ứng có ý nghĩa với thuốc giãn phế quản khí dung test giãn phế '
            'quản âm tính',
            'hình ảnh khảm khí mosaic attenuation kèm bẫy khí air trapping trên phim chụp cắt lớp vi tính lồng ngực '
            'thì thở ra'],
  'phu': ['thở khò khè thở rít và ho khan dai dẳng không dứt',
          'thở nhanh co kéo nhẹ cơ hô hấp phụ khi gắng sức nhẹ',
          'lồng ngực căng phồng tăng đường kính trước sau ứ khí phổi'],
  'bien_the_kham': ['Phổi nghe thông khí giảm hai bên kèm nhiều ran rít ran ngáy rải rác khắp hai phế trường, thì thở '
                    'ra kéo dài rõ rệt, lồng ngực ứ khí nhô cao, SpO2 93% khí phòng.',
                    'Khám thấy trẻ thở co kéo nhẹ hõm ức và cơ liên sườn, nhịp thở 34 l/p, nghe phổi ran rít ran ngáy '
                    'dai dẳng không giảm sau khi khí dung Salbutamol.',
                    'Nghe hai phổi rải rác tiếng rít thì thở ra, rì rào phế nang giảm ở các vùng bẫy khí tạo nên tiếng '
                    'thở không đồng đều, tim nhịp nhanh đều 105 l/p.',
                    'Lồng ngực hình thùng nhẹ ứ khí mạn tính, gõ vang hai phế trường, nghe phổi có ran ngáy thô ráp '
                    'rải rác khắp hai thì hô hấp, không có ran ẩm nhỏ hạt.',
                    'Khám hô hấp thấy bệnh nhân thở nhanh nông, thì thở ra gắng sức nghe rõ tiếng khò khè ở miệng, '
                    'nghe phổi ran rít hai bên phế trường, ngón tay không dùi trống.',
                    'Thông khí phổi hai bên kém đều, nhiều ran rít cố định qua nhiều lần khám, trẻ thở nhanh khi chạy '
                    'nhảy chơi đùa, SpO2 giảm xuống 90% khi gắng sức.'],
  'bien_the_chan_doan': ['Viêm tiểu phế quản tắc nghẽn hậu nhiễm trùng Post-infectious Bronchiolitis Obliterans sau '
                         'nhiễm Adenovirus.',
                         'Viêm tiểu phế quản tắc nghẽn sau nhiễm virus tắc nghẽn đường thở cố định không hồi phục.',
                         'Bệnh lý viêm tiểu phế quản tắc nghẽn PIBO biến chứng bẫy khí phổi mạn tính.',
                         'Theo dõi viêm tiểu phế quản tắc nghẽn sau viêm phổi virus nặng thể mosaic phổi.',
                         'Viêm tiểu phế quản bít tắc sau nhiễm khuẩn hô hấp có suy giảm chức năng thông khí tắc nghẽn '
                         'nặng.',
                         'Hội chứng viêm tiểu phế quản tắc nghẽn sau nhiễm virus đường thở mạn tính.'],
  'bien_the_ke_hoach': ['Chụp cắt lớp vi tính ngực HRCT hai thì thì hít vào và thì thở ra để xác định hình ảnh tổn '
                        'thương khảm bẫy khí điển hình của viêm tiểu phế quản tắc nghẽn.',
                        'Đo chức năng hô hấp dao động xung ký IOS ở trẻ nhỏ hoặc hô hấp ký ở trẻ lớn làm test giãn phế '
                        'quản chứng minh tình trạng tắc nghẽn đường thở cố định.',
                        'Dùng Corticosteroid đường hít liều cao ICS Budesonide hoặc Fluticasone kết hợp thuốc giãn phế '
                        'quản tác dụng kéo dài LABA nhằm giảm phản ứng viêm tại chỗ đường thở nhỏ.',
                        'Cân nhắc dùng kháng sinh nhóm Macrolide Azithromycin liều thấp 3 lần mỗi tuần kéo dài 3-6 '
                        'tháng nhờ tác dụng chống viêm và điều hòa miễn dịch đường thở.',
                        'Tập vật lý trị liệu hô hấp vỗ rung lồng ngực và dẫn lưu tư thế hỗ trợ tống xuất đờm dãi ứ '
                        'đọng phòng ngừa xẹp phổi và giãn phế quản thứ phát.',
                        'Tiêm phòng đầy đủ các vắc xin hô hấp, tránh xa môi trường khói thuốc lá khói bụi độc hại, tái '
                        'khám định kỳ theo dõi chức năng hô hấp và sự phát triển thể chất.'],
  'kham': 'Phổi nghe thông khí giảm hai bên kèm nhiều ran rít ran ngáy rải rác khắp hai phế trường, thì thở ra kéo dài '
          'rõ rệt, lồng ngực ứ khí nhô cao, SpO2 93% khí phòng.',
  'chan_doan': 'Viêm tiểu phế quản tắc nghẽn hậu nhiễm trùng Post-infectious Bronchiolitis Obliterans sau nhiễm '
               'Adenovirus.',
  'ke_hoach': 'Chụp cắt lớp vi tính ngực HRCT hai thì thì hít vào và thì thở ra để xác định hình ảnh tổn thương khảm '
              'bẫy khí điển hình của viêm tiểu phế quản tắc nghẽn.'},
 {'ten': 'bui phổi amiăng Asbestosis',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['tiền sử phơi nhiễm trực tiếp lâu năm với bụi sợi amiăng trong các ngành công nghiệp đóng tàu cách nhiệt '
            'dệt amiăng sản xuất tấm lợp fibrô xi măng',
            'hình ảnh xơ hóa mô kẽ phổi chiếm ưu thế ở thùy dưới phổi kèm theo các mảng dày vôi hóa màng phổi pleural '
            'plaques đặc trưng trên HRCT',
            'tìm thấy thể amiăng asbestos bodies hoặc sợi amiăng trong mô sinh thiết phổi hoặc dịch rửa phế quản'],
  'phu': ['khó thở khi gắng sức tiến triển chậm chạp và ho khan không có đờm',
          'ngón tay hình dùi trống và móng tay khum mặt kính đồng hồ',
          'ran nổ khô nhỏ hạt cuối thì hít vào ở hai đáy phổi'],
  'bien_the_kham': ['Mười đầu ngón tay dùi trống rõ rệt móng tay khum, nghe phổi hai bên có ran nổ khô mịn cuối thì '
                    'hít vào nghe rõ ở vùng nách và đáy phổi hai bên, nhịp thở 22 l/p, SpO2 93% khí phòng.',
                    'Khám thấy bệnh nhân thở nhanh nông khi vận động nhẹ, ngón tay dùi trống điển hình ở cả hai bàn '
                    'tay, nghe phổi rì rào phế nang giảm nhẹ đáy phổi kèm ran nổ khô kiểu velcro.',
                    'Thể trạng gầy, lồng ngực giảm độ giãn nở hai bên khi hít sâu, nghe phổi hai phế trường có ran nổ '
                    'nhỏ hạt âm sắc cao vùng đáy phổi, tiếng tim rõ không tiếng thổi.',
                    'Bệnh nhân có tiền sử làm thợ cán tấm lợp 20 năm, khám thấy các đầu ngón tay to bè hình dùi trống, '
                    'ran nổ khô rải rác hai đáy phổi, SpO2 giảm xuống 88% sau nghiệm pháp đi bộ 6 phút.',
                    'Khám hô hấp ghi nhận ran nổ âm sắc cao thì hít vào ở hai đáy phổi không thay đổi sau khi ho, các '
                    'mảng vôi hóa màng phổi không gây đau khi ấn lồng ngực.',
                    'Nhịp thở 20 lần/phút, rì rào phế nang êm dịu ở đỉnh phổi nhưng giảm rõ ở hai đáy phổi kèm ran nổ '
                    'mịn khô, ngón tay khum mặt kính đồng hồ rõ nét.'],
  'bien_the_chan_doan': ['Bệnh bụi phổi amiăng Asbestosis mạn tính có xơ hóa phổi kẽ thùy dưới và mảng màng phổi.',
                         'Bệnh bụi phổi amiăng nghề nghiệp biến chứng suy hô hấp hạn chế và ngón tay dùi trống.',
                         'Bụi phổi amiăng Asbestosis có tổn thương dày vôi hóa màng phổi hai bên.',
                         'Theo dõi bệnh bụi phổi amiăng Asbestosis cần tầm soát nguy cơ u trung biểu mô màng phổi.',
                         'Bệnh phổi nghề nghiệp do phơi nhiễm bụi amiăng mạn tính thể xơ hóa mô kẽ tiến triển.',
                         'Bệnh bụi phổi Asbestosis giảm dung tích sống FVC và giảm độ khuếch tán khí qua màng phế '
                         'nang.'],
  'bien_the_ke_hoach': ['Chụp cắt lớp vi tính lồng ngực độ phân giải cao HRCT đánh giá mức độ xơ hóa đáy phổi và định '
                        'kỳ tầm soát sớm ung thư phế quản và u trung biểu mô màng phổi Mesothelioma.',
                        'Đo chức năng thông khí phổi hô hấp ký đánh giá mức độ hội chứng hạn chế giảm FVC và đo độ '
                        'khuếch tán khí DLCO để xác định mức độ suy giảm trao đổi khí.',
                        'Ngừng tiếp xúc hoàn toàn với bụi amiăng, chuyển đổi vị trí công tác hoặc nghỉ chế độ bệnh '
                        'nghề nghiệp theo quy định của pháp luật lao động y tế.',
                        'Tư vấn bỏ thuốc lá tuyệt đối vì sự kết hợp giữa hút thuốc lá và phơi nhiễm amiăng làm tăng '
                        'nguy cơ ung thư phổi lên gấp 50-60 lần so với người bình thường.',
                        'Cho thở oxy dài hạn tại nhà nếu bệnh nhân có suy hô hấp mạn tính SpO2 dưới 88% khi nghỉ ngơi '
                        'hoặc khi gắng sức, hướng dẫn tập phục hồi chức năng hô hấp.',
                        'Tiêm vắc xin phòng cúm và phế cầu hàng năm phòng ngừa các đợt nhiễm trùng hô hấp cấp, lập hồ '
                        'sơ bệnh nghề nghiệp quản lý theo dõi lâu dài.'],
  'kham': 'Mười đầu ngón tay dùi trống rõ rệt móng tay khum, nghe phổi hai bên có ran nổ khô mịn cuối thì hít vào nghe '
          'rõ ở vùng nách và đáy phổi hai bên, nhịp thở 22 l/p, SpO2 93% khí phòng.',
  'chan_doan': 'Bệnh bụi phổi amiăng Asbestosis mạn tính có xơ hóa phổi kẽ thùy dưới và mảng màng phổi.',
  'ke_hoach': 'Chụp cắt lớp vi tính lồng ngực độ phân giải cao HRCT đánh giá mức độ xơ hóa đáy phổi và định kỳ tầm '
              'soát sớm ung thư phế quản và u trung biểu mô màng phổi Mesothelioma.'},
 {'ten': 'bụi phổi than thợ mỏ anthracosis',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['tiền sử làm việc tiếp xúc lâu năm trong các hầm lò khai thác than hít phải bụi than mạn tính',
            'hình ảnh nhiều nốt mờ nhỏ kích thước 1-5mm phân bố dày đặc ở các thùy trên của cả hai phổi trên phim '
            'X-quang hoặc CT ngực',
            'ho khạc đờm màu đen đặc trưng chứa bụi than melanoptysis trong các đợt bội nhiễm hoặc hoại tử khối xơ '
            'than'],
  'phu': ['khó thở khi gắng sức tăng dần theo thời gian',
          'ho khan hoặc ho khạc đờm nhầy mạn tính giống viêm phế quản mạn',
          'nghe phổi rì rào phế nang giảm nhẹ có thể kèm ran rải rác'],
  'bien_the_kham': ['Bệnh nhân có màu da sạm bụi bẩn khó rửa ở các nếp gấp da, ho khạc ra ít đờm có chấm đen lấm tấm, '
                    'nghe phổi rì rào phế nang giảm ở hai thùy trên kèm vài ran nổ khô rải rác, SpO2 95%.',
                    'Khám thấy lồng ngực hơi giãn rộng, nghe phổi thông khí hai bên tương đối đều rải rác ít ran ngáy '
                    'thô ráp, bệnh nhân khai tiền sử 18 năm làm công nhân khai thác than hầm lò.',
                    'Thể trạng rắn rỏi nhưng thở nhanh nhẹ khi đi lên cầu thang, nghe phổi có tiếng thở thô ráp ở đỉnh '
                    'phổi hai bên, không có ran ẩm ướt, tim mạch bình thường.',
                    'Khám lâm sàng hô hấp phát hiện rì rào phế nang giảm nhẹ hai đỉnh phổi, bệnh nhân ho khạc mẫu đờm '
                    'có màu đen than rõ rệt, không có hạch ngoại biên to.',
                    'Nhịp thở 20 l/p, ngực di động đều, gõ trong hai phế trường, nghe phổi không có ran rít co thắt, '
                    'khám móng tay không có dùi trống rõ rệt, huyết áp 125/80 mmHg.',
                    'Nghe phổi thấy tiếng thở phế nang hơi thô ráp ở vùng liên bả cột sống hai bên, nhịp tim đều 78 '
                    'l/p, không có dấu suy tim phải phù gan to.'],
  'bien_the_chan_doan': ['Bệnh bụi phổi than thợ mỏ Anthracosis thể nốt đơn thuần Coal Workers Pneumoconiosis CWP.',
                         'Bệnh bụi phổi than thợ mỏ thể xơ hóa tiến triển khối lớn PMF Progressive Massive Fibrosis.',
                         'Bệnh bụi phổi công nhân than Anthracosis kết hợp viêm phế quản mạn tính nghề nghiệp.',
                         'Theo dõi bệnh bụi phổi than Anthracosis cần phân biệt với lao phổi nốt kê.',
                         'Bệnh bụi phổi than nghề nghiệp thể nốt mạn tính ổn định.',
                         'Bệnh bụi phổi công nhân than CWP có triệu chứng khạc đờm đen anthracosis.'],
  'bien_the_ke_hoach': ['Chụp phim X-quang lồng ngực thẳng chuẩn quốc tế theo phân loại ILO về bệnh bụi phổi hoặc chụp '
                        'CT ngực liều thấp để phân độ tổn thương dạng nốt và khối xơ hóa.',
                        'Đo chức năng thông khí phổi hô hấp ký định kỳ hàng năm đánh giá mức độ suy giảm FEV1 và FVC, '
                        'xét nghiệm đờm soi trực tiếp và nuôi cấy tìm vi khuẩn lao AFB để tầm soát biến chứng lao phối '
                        'hợp hội chứng Silicotuberculosis.',
                        'Chuyển khỏi môi trường lao động hầm lò tiếp xúc bụi than sang vị trí làm việc trên mặt đất '
                        'thông thoáng, giám định bệnh nghề nghiệp hưởng trợ cấp bảo hiểm.',
                        'Tư vấn kiên quyết bỏ thuốc lá để ngăn ngừa biến chứng khí phế thũng và xơ hóa khối tiến triển '
                        'PMF, tiêm vắc xin phòng phế cầu và vắc xin cúm mùa.',
                        'Điều trị triệu chứng bằng thuốc giãn phế quản dạng hít nếu có kèm theo hội chứng tắc nghẽn '
                        'phế quản, hướng dẫn tập thở chúm môi và thở cơ hoành.',
                        'Lập sổ theo dõi sức khỏe bệnh nghề nghiệp định kỳ mỗi 6 tháng tại cơ sở y tế chuyên khoa lao '
                        'và bệnh phổi.'],
  'kham': 'Bệnh nhân có màu da sạm bụi bẩn khó rửa ở các nếp gấp da, ho khạc ra ít đờm có chấm đen lấm tấm, nghe phổi '
          'rì rào phế nang giảm ở hai thùy trên kèm vài ran nổ khô rải rác, SpO2 95%.',
  'chan_doan': 'Bệnh bụi phổi than thợ mỏ Anthracosis thể nốt đơn thuần Coal Workers Pneumoconiosis CWP.',
  'ke_hoach': 'Chụp phim X-quang lồng ngực thẳng chuẩn quốc tế theo phân loại ILO về bệnh bụi phổi hoặc chụp CT ngực '
              'liều thấp để phân độ tổn thương dạng nốt và khối xơ hóa.'},
 {'ten': 'bệnh phổi nông dân do nấm mốc dị ứng',
  'nhom': 'người lớn',
  'dien_tien': 'cấp',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['khởi phát cấp tính sốt rét run ho khan khó thở nặng nề xuất hiện từ 4 đến 8 giờ sau khi tiếp xúc với cỏ '
            'khô rơm rạ hoặc ngũ cốc ẩm mốc',
            'viêm phế nang dị ứng ngoại lai Hypersensitivity Pneumonitis do hít phải bào tử vi khuẩn ưa nhiệt '
            'Thermoactinomyces hoặc nấm mốc trong cỏ rơm mục',
            'hình ảnh thâm nhiễm kính mờ lan tỏa hai bên phổi kèm các nốt mờ trung tâm tiểu thùy kém nét trên phim '
            'chụp CT ngực'],
  'phu': ['nghe phổi có nhiều ran nổ mịn nhỏ hạt rải rác hai phế trường',
          'các triệu chứng tự thuyên giảm sau vài ngày nếu không tiếp xúc lại với nguồn kháng nguyên dị ứng',
          'tăng nồng độ kháng thể kết tủa IgG precipitin đặc hiệu với kháng nguyên nấm mốc trong huyết thanh'],
  'bien_the_kham': ['Bệnh nhân sốt 38.8 độ C rét run thở nhanh nông 28 l/p, môi tím nhẹ, SpO2 89% khí phòng, nghe hai '
                    'phổi ran nổ nhỏ hạt mịn rải rác khắp hai phế trường tập trung nhiều ở hai đáy phổi, tim nhịp '
                    'nhanh 110 l/p.',
                    'Khám thấy bệnh nhân khó thở co kéo cơ liên sườn sau khi dọn kho rơm mục chiều qua, nghe phổi dày '
                    'đặc ran nổ khô mịn hai bên thì hít vào, không có tiếng ran rít ran ngáy phế quản.',
                    'Thể trạng mệt mỏi sốt cao vã mồ hôi, nhịp thở 26 l/p, nghe rì rào phế nang giảm lan tỏa kèm nhiều '
                    'ran nổ nhỏ hạt ở cả hai bên lồng ngực, củng mạc mắt không vàng.',
                    'Bệnh nhân ho sặc sụa từng cơn không có đờm, da nóng sốt 38.5 độ C, nghe phổi nghe ran nổ nhỏ hạt '
                    'khắp hai trường phổi, SpO2 tăng lên 95% khi thở oxy qua gọng kính 3 lít/phút.',
                    'Khám cấp cứu thấy suy hô hấp cấp độ 1, thở nhanh nông, nghe phổi có ran nổ dạng kẽ hai bên đáy và '
                    'nách phổi, tiếng tim nhanh rõ, không có phù hay ban da dị ứng.',
                    'Nhịp thở 27 lần/phút, nghe phổi nhiều ran nổ mịn cuối thì hít vào, không nghe thấy tiếng thổi ống '
                    'hay đông đặc phổi điển hình, bệnh nhân khai xúc cỏ khô bị mốc cách 6 giờ.'],
  'bien_the_chan_doan': ['Bệnh phổi nông dân Farmers Lung đợt cấp tính thể viêm phế nang dị ứng ngoại lai do nấm mốc '
                         'cỏ khô.',
                         'Viêm phổi tăng cảm ngoại lai cấp tính Farmers Lung có suy hô hấp cấp mức độ vừa.',
                         'Viêm phế nang dị ứng do hít bào tử nấm mốc rơm rạ bệnh phổi người làm nông đợt cấp.',
                         'Theo dõi bệnh phổi nông dân đợt cấp cần phân biệt với viêm phổi nhiễm trùng mắc phải cộng '
                         'đồng.',
                         'Bệnh phổi nông dân Farmers Lung thể cấp tính đáp ứng tốt sau cách ly kháng nguyên dị ứng.',
                         'Hội chứng viêm phế nang quá mẫn cấp tính nghề nghiệp nông nghiệp do bụi nấm hữu cơ.'],
  'bien_the_ke_hoach': ['Biện pháp quan trọng hàng đầu là cách ly bệnh nhân hoàn toàn khỏi nguồn cỏ khô rơm rạ ngũ cốc '
                        'ẩm mốc gây bệnh, cho thở oxy hỗ trợ qua gọng mũi duy trì SpO2 trên 94%.',
                        'Chỉ định điều trị bằng Corticoid toàn thân Prednisolone 0.5-1 mg/kg mỗi ngày đường uống hoặc '
                        'tiêm tĩnh mạch trong 1-2 tuần sau đó giảm dần liều khi triệu chứng lâm sàng và tổn thương '
                        'phổi cải thiện hoàn toàn.',
                        'Xét nghiệm tìm kháng thể kết tủa huyết thanh IgG precipitin đặc hiệu với các tác nhân '
                        'Thermoactinomyces vulgaris hoặc Saccharopolyspora rectivirgula.',
                        'Chụp cắt lớp vi tính lồng ngực độ phân giải cao HRCT đánh giá mức độ tổn thương kính mờ và '
                        'các nốt vi hạt trung tâm tiểu thùy.',
                        'Đo chức năng thông khí phổi hô hấp ký theo dõi sự phục hồi của hội chứng hạn chế và độ khuếch '
                        'tán khí DLCO sau giai đoạn cấp tính.',
                        'Hướng dẫn các biện pháp bảo hộ lao động mang khẩu trang lọc bụi chuyên dụng N95 hoặc làm khô '
                        'thông thoáng nông sản rơm rạ trước khi vận chuyển bốc dỡ.'],
  'kham': 'Bệnh nhân sốt 38.8 độ C rét run thở nhanh nông 28 l/p, môi tím nhẹ, SpO2 89% khí phòng, nghe hai phổi ran '
          'nổ nhỏ hạt mịn rải rác khắp hai phế trường tập trung nhiều ở hai đáy phổi, tim nhịp nhanh 110 l/p.',
  'chan_doan': 'Bệnh phổi nông dân Farmers Lung đợt cấp tính thể viêm phế nang dị ứng ngoại lai do nấm mốc cỏ khô.',
  'ke_hoach': 'Biện pháp quan trọng hàng đầu là cách ly bệnh nhân hoàn toàn khỏi nguồn cỏ khô rơm rạ ngũ cốc ẩm mốc '
              'gây bệnh, cho thở oxy hỗ trợ qua gọng mũi duy trì SpO2 trên 94%.'},
 {'ten': 'viêm màng phổi dày dính màng phổi sau tràn dịch',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['tiền sử viêm màng phổi tràn dịch màng phổi do lao do mủ màng phổi hoặc chấn thương tràn máu màng phổi cũ',
            'dày dính xơ hóa vôi hóa lá thành và lá tạng màng phổi làm giảm thể tích khoang màng phổi trên phim chụp '
            'X-quang hoặc CT ngực',
            'hội chứng hạn chế thông khí phổi thể hiện qua dung tích sống gắng sức FVC giảm rõ rệt trên hô hấp ký'],
  'phu': ['đau tức âm ỉ cố định tại vùng hạ sườn hoặc thành ngực bên tổn thương tăng lên khi thở sâu hoặc vặn người',
          'cảm giác khó thở tức thở khi vận động gắng sức thể lực',
          'lồng ngực bên tổn thương bị co kéo lép xẹp giảm độ giãn nở khi thở'],
  'bien_the_kham': ['Lồng ngực bên phải hơi lép hẹp khoang liên sườn co kéo nhẹ, biên độ di động lồng ngực bên phải '
                    'giảm rõ so với bên trái, gõ đục vùng đáy phổi phải, rì rào phế nang giảm rõ vùng đáy, không có '
                    'ran.',
                    'Khám thấy giảm độ giãn nở nửa dưới lồng ngực bên trái, rung thanh giảm, gõ đục vùng đáy nách phổi '
                    'trái, nghe rì rào phế nang vùng đáy mờ nhạt, không có tiếng cọ màng phổi.',
                    'Bệnh nhân có vết sẹo mổ dẫn lưu màng phổi cũ ở khoang liên sườn 5 nách giữa, thành ngực bên tổn '
                    'thương co rút nhẹ, gõ đục đáy phổi, thông khí phổi giảm đáy, tim đều rõ.',
                    'Thành ngực bên phải giảm di động rõ rệt, khoảng gian sườn hẹp lại, nghe tiếng thở phế nang giảm '
                    'sâu ở một phần ba dưới phế trường phải, không nghe ran ẩm hay ran rít.',
                    'Lồng ngực bên dày dính giảm giãn nở khi hít sâu, gõ đục vùng dưới góc xương bả vai, rì rào phế '
                    'nang giảm nhẹ, bệnh nhân than tức đau cơ năng khi xoay người vặn mình.',
                    'Khám lồng ngực thấy co rút cơ liên sườn một bên, gõ đục đáy phổi, rung thanh giảm nhẹ, không có '
                    'dấu tràn dịch tự do qua thay đổi tư thế, các cơ quan khác bình thường.'],
  'bien_the_chan_doan': ['Dày dính màng phổi mạn tính di chứng sau viêm mủ màng phổi cũ có hội chứng hạn chế hô hấp.',
                         'Dày dính xơ hóa vôi hóa màng phổi Fibrothorax sau tràn dịch màng phổi do lao cũ.',
                         'Dày dính màng phổi một bên di chứng sau chấn thương tràn máu màng phổi.',
                         'Theo dõi dày dính màng phổi vôi hóa thể nặng gây hạn chế thông khí lồng ngực.',
                         'Dày màng phổi xơ dính khu trú đáy phổi sau điều trị viêm màng phổi xuất tiết.',
                         'Di chứng xơ dính màng phổi hạn chế giãn nở phổi mạn tính.'],
  'bien_the_ke_hoach': ['Chụp cắt lớp vi tính lồng ngực CT scan có tiêm thuốc cản quang đo độ dày của lớp vỏ xơ màng '
                        'phổi và đánh giá mức độ co kéo nhu mô phổi bên dưới.',
                        'Đo chức năng hô hấp toàn diện hô hấp ký đánh giá mức độ giảm dung tích sống FVC và chỉ số '
                        'Tiffeneau để xác định mức độ suy giảm thông khí hạn chế.',
                        'Hướng dẫn tập vật lý trị liệu hô hấp chuyên sâu các bài tập giãn nở lồng ngực tập thở sâu và '
                        'tập với dụng cụ thổi phế dung kế khuyến khích Spirometry nhằm cải thiện dung tích phổi.',
                        'Hội chẩn phẫu thuật viên Lồng ngực xem xét chỉ định phẫu thuật bóc vỏ màng phổi Decortication '
                        'nếu lớp vỏ xơ dày gây co kéo xẹp phổi nghiêm trọng và hạn chế hô hấp nặng ảnh hưởng nhiều đến '
                        'sinh hoạt.',
                        'Điều trị thuốc giảm đau thông thường paracetamol nếu có đau tức ngực âm ỉ do co kéo cơ màng '
                        'phổi, tránh lạm dụng thuốc kháng viêm kéo dài.',
                        'Tái khám định kỳ theo dõi diễn tiến chức năng hô hấp và tầm soát các bệnh lý hô hấp mắc kèm.'],
  'kham': 'Lồng ngực bên phải hơi lép hẹp khoang liên sườn co kéo nhẹ, biên độ di động lồng ngực bên phải giảm rõ so '
          'với bên trái, gõ đục vùng đáy phổi phải, rì rào phế nang giảm rõ vùng đáy, không có ran.',
  'chan_doan': 'Dày dính màng phổi mạn tính di chứng sau viêm mủ màng phổi cũ có hội chứng hạn chế hô hấp.',
  'ke_hoach': 'Chụp cắt lớp vi tính lồng ngực CT scan có tiêm thuốc cản quang đo độ dày của lớp vỏ xơ màng phổi và '
              'đánh giá mức độ co kéo nhu mô phổi bên dưới.'},
 {'ten': 'rò dưỡng chấp màng phổi vô căn',
  'nhom': 'người lớn',
  'dien_tien': 'mạn',
  'he_co_quan': 'hô hấp',
  'da_duyet': False,
  'chinh': ['dịch màng phổi chọc hút có màu trắng đục như sữa không đổi màu sau khi ly tâm',
            'nồng độ triglyceride trong dịch màng phổi tăng rất cao trên 110 mg/dL hoặc phát hiện hạt vi thể mỡ dưỡng '
            'chấp chylomicrons khi điện di',
            'loại trừ hoàn toàn các nguyên nhân thứ phát do chấn thương ngực phẫu thuật lồng ngực hoặc bệnh lý u '
            'lympho ác tính chèn ép ống ngực'],
  'phu': ['khó thở tiến triển tăng dần do tràn dịch màng phổi lượng nhiều tái lập nhanh',
          'sụt cân suy dinh dưỡng và suy giảm miễn dịch do mất dịch dưỡng chấp giàu protein và lympho bào',
          'gõ đục và rì rào phế nang mất hoàn toàn ở vùng thấp lồng ngực'],
  'bien_the_kham': ['Khám thấy hội chứng ba giảm rõ rệt ở nửa dưới lồng ngực bên phải gồm rung thanh mất gõ đục như gỗ '
                    'và rì rào phế nang mất hoàn toàn, khí quản và tim bị đẩy lệch nhẹ sang bên trái, SpO2 92% khí '
                    'phòng.',
                    'Bệnh nhân khó thở khi nằm phẳng, ngồi dậy thở thoải mái hơn, lồng ngực bên phải căng to hơn bên '
                    'trái, mất tiếng thở phế nang từ khoang liên sườn 4 trở xuống bên phải, không sốt.',
                    'Thể trạng gầy mòn suy dinh dưỡng, niêm mạc nhợt nhạt, khám lồng ngực có hội chứng tràn dịch màng '
                    'phổi lượng nhiều bên phải, tiếng tim mờ nhịp nhanh 98 l/p.',
                    'Khám thấy giảm rì rào phế nang và gõ đục rõ rệt ở đáy phổi, không có hạch ngoại biên vùng cổ nách '
                    'bẹn, không sờ thấy gan lách to, bụng mềm.',
                    'Hội chứng tràn dịch màng phổi một bên lượng trung bình đến nhiều, gõ đục vùng thấp thay đổi theo '
                    'tư thế, mạch 90 lần/phút, huyết áp 110/70 mmHg.',
                    'Lồng ngực bên tổn thương kém di động theo nhịp thở, mất hoàn toàn rì rào phế nang đáy phổi, khám '
                    'không phát hiện dị tật lồng ngực hay vết mổ cũ.'],
  'bien_the_chan_doan': ['Tràn dưỡng chấp màng phổi tự phát vô căn Idiopathic Chylothorax lượng nhiều dịch màu trắng '
                         'sữa.',
                         'Rò dưỡng chấp màng phổi vô căn tái lập nhanh gây suy dinh dưỡng giảm protein máu.',
                         'Bệnh lý tràn dịch dưỡng chấp màng phổi vô căn có nồng độ Triglyceride dịch màng phổi cao.',
                         'Theo dõi rò ống ngực màng phổi tự phát vô căn cần chụp cộng hưởng từ bạch mạch.',
                         'Rò dưỡng chấp màng phổi vô căn đợt tiến triển suy hô hấp hạn chế do tràn dịch ép phổi.',
                         'Tràn dịch màng phổi dưỡng chấp tự phát vô căn loại trừ u lympho và dị dạng mạch bạch huyết.'],
  'bien_the_ke_hoach': ['Chọc hút dẫn lưu dịch dưỡng chấp màng phổi giảm áp lực khoang màng phổi cải thiện suy hô hấp, '
                        'gửi dịch màng phổi xét nghiệm định lượng Triglyceride protein đếm tế bào lympho bào và soi '
                        'tìm vi thể chylomicrons dưới kính hiển vi nhuộm Sudan III.',
                        'Áp dụng chế độ ăn kiêng chất béo nghiêm ngặt không mỡ chuỗi dài LCT bổ sung chất béo trung '
                        'tính chuỗi trung bình MCT Medium-Chain Triglycerides hấp thu trực tiếp vào hệ tĩnh mạch cửa '
                        'không qua ống ngực, hoặc nuôi dưỡng hoàn toàn qua đường tĩnh mạch TPN để ống ngực được nghỉ '
                        'ngơi giảm lưu lượng dưỡng chấp.',
                        'Dùng thuốc Octreotide hoặc Somatostatin tiêm dưới da để giảm tiết dịch tiêu hóa và giảm lưu '
                        'lượng dòng chảy dưỡng chấp qua ống ngực hỗ trợ làm lành lỗ rò tự nhiên.',
                        'Chụp cộng hưởng từ hệ bạch huyết MR Lymphangiography hoặc chụp bạch mạch cản quang quy ước để '
                        'xác định vị trí chính xác của điểm rò ống ngực vào màng phổi.',
                        'Hội chẩn phẫu thuật Lồng ngực xem xét nội soi lồng ngực thắt ống ngực hoặc gây dính màng phổi '
                        'hóa học bằng bột talc nếu điều trị nội khoa bảo tồn thất bại sau 1-2 tuần.',
                        'Bù phụ protein albumin huyết tương và các vitamin tan trong dầu A D E K bị thất thoát qua '
                        'dịch dưỡng chấp, theo dõi cân nặng và điện giải đồ hàng ngày.'],
  'kham': 'Khám thấy hội chứng ba giảm rõ rệt ở nửa dưới lồng ngực bên phải gồm rung thanh mất gõ đục như gỗ và rì rào '
          'phế nang mất hoàn toàn, khí quản và tim bị đẩy lệch nhẹ sang bên trái, SpO2 92% khí phòng.',
  'chan_doan': 'Tràn dưỡng chấp màng phổi tự phát vô căn Idiopathic Chylothorax lượng nhiều dịch màu trắng sữa.',
  'ke_hoach': 'Chọc hút dẫn lưu dịch dưỡng chấp màng phổi giảm áp lực khoang màng phổi cải thiện suy hô hấp, gửi dịch '
              'màng phổi xét nghiệm định lượng Triglyceride protein đếm tế bào lympho bào và soi tìm vi thể '
              'chylomicrons dưới kính hiển vi nhuộm Sudan III.'}]
