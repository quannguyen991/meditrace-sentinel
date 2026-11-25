# -*- coding: utf-8 -*-
"""Lô 7 Khuôn Bệnh Lâm Sàng (Khuôn 501 - 550) cho MediTrace Sentinel V2.

Bộ 50 khuôn bệnh bổ sung:
- Nguồn: DANH_SACH_UNG_VIEN_CON_LAI[200:250]
- Hệ cơ quan: da liễu, miễn dịch - dị ứng, tim mạch, tiêu hoá, thần kinh, mắt, huyết học
- Đảm bảo 100% 6 biến thể khám, chẩn đoán, kế hoạch
- 0 cặp trùng lặp triệu chứng >= 20%
"""
from typing import Dict, List, Any

GIOI_TINH_LO_7: Dict[str, str] = {
    "lichen xơ teo âm hộ": "nữ",
    "rụng tóc nội tiết androgenic nam": "nam"
}

BENH_LO_7: List[Dict[str, Any]] = [{'bien_the_chan_doan': ['Bệnh da bọng nước tự miễn Pemphigus vulgaris đợt tiến triển.',
                         'Theo dõi bệnh da bọng nước tự miễn Pemphigus vulgaris mức độ trung bình.',
                         'Bệnh da bọng nước tự miễn Pemphigus vulgaris có tổn thương niêm mạc '
                         'miệng.',
                         'Bệnh da bọng nước tự miễn Pemphigus vulgaris thể thông thường giai đoạn '
                         'hoạt tính.',
                         'Bệnh da bọng nước tự miễn Pemphigus vulgaris tái phát.',
                         'Nghi ngờ bệnh da bọng nước tự miễn Pemphigus vulgaris tổn thương da và '
                         'niêm mạc.'],
  'bien_the_ke_hoach': ['Chỉ định sinh thiết rìa tổn thương làm miễn dịch huỳnh quang trực tiếp, '
                        'dùng corticosteroid đường toàn thân kết hợp chăm sóc vết trợt tại chỗ.',
                        'Làm sinh thiết mô bệnh học da, xét nghiệm kháng thể kháng desmoglein 1 và '
                        '3, dùng prednisolone đường uống liều cao.',
                        'Chỉ định xét nghiệm miễn dịch huỳnh quang trực tiếp, dùng '
                        'methylprednisolone tĩnh mạch kết hợp bôi thuốc mỡ sát khuẩn dịu da.',
                        'Thực hiện sinh thiết tổn thương da bọng nước, điều trị ức chế miễn dịch '
                        'bằng corticoid toàn thân, súc miệng dung dịch giảm đau sát khuẩn.',
                        'Hội chẩn chuyên khoa da liễu, làm xét nghiệm miễn dịch huỳnh quang, dùng '
                        'corticosteroid toàn thân và gạc mỡ che phủ vết trợt.',
                        'Làm giải phẫu bệnh vết loét da, dùng liệu pháp corticoid liều cao đường '
                        'uống phối hợp phòng ngừa loét dạ dày và chăm sóc niêm mạc.'],
  'bien_the_kham': ['Khám thấy nhiều bọng nước thành mỏng nhẽo dễ vỡ, trợt loét niêm mạc miệng rải '
                    'rác diện rộng, dấu hiệu Nikolsky dương tính rõ.',
                    'Tổn thương da là các vết trợt nông rỉ dịch sau bọng vỡ, niêm mạc miệng có '
                    'nhiều vết loét trợt đau rát, Nikolsky dương tính.',
                    'Ghi nhận bọng nước vách mỏng chứa dịch trong nằm rải rác thân mình, vòm miệng '
                    'có mảng loét sâu đau, dấu hiệu Nikolsky dương tính.',
                    'Da nhiều vết trợt rỉ dịch huyết thanh do bọng nước dập vỡ, niêm mạc má và lợi '
                    'có tổn thương trợt loét đỏ tươi điển hình.',
                    'Bọng nước nhẽo xuất hiện trên nền da bình thường kèm trợt loét niêm mạc miệng '
                    'rộng, dấu hiệu Nikolsky dương tính rõ rệt.',
                    'Bề mặt da rải rác bọng nước mềm dễ rách, niêm mạc họng viêm loét gây nuốt '
                    'nghẹn, khám thấy nghiệm pháp Nikolsky dương tính.'],
  'chan_doan': 'Bệnh da bọng nước tự miễn Pemphigus vulgaris đợt tiến triển.',
  'chinh': ['xuất hiện các bọng nước mỏng mềm dễ dập vỡ trên nền da bình thường',
            'tổn thương trợt loét đau rát dữ dội tại niêm mạc khoang miệng và vòm họng',
            'vết trợt da rỉ dịch huyết thanh vàng dễ chảy máu lâu đóng vảy lành'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định sinh thiết rìa tổn thương làm miễn dịch huỳnh quang trực tiếp, dùng '
              'corticosteroid đường toàn thân kết hợp chăm sóc vết trợt tại chỗ.',
  'kham': 'Khám thấy nhiều bọng nước thành mỏng nhẽo dễ vỡ, trợt loét niêm mạc miệng rải rác diện '
          'rộng, dấu hiệu Nikolsky dương tính rõ.',
  'nhom': 'người lớn',
  'phu': ['cảm giác đau buốt tăng nặng khi nuốt thức ăn làm hạn chế dinh dưỡng',
          'mùi hôi đặc trưng tiết ra từ các vết trợt da tiết dịch nhớt dính',
          'cảm giác râm ran bỏng rát nhẹ trên da trước khi xuất hiện bọng mới'],
  'ten': 'bệnh da bọng nước tự miễn Pemphigus vulgaris'},
 {'bien_the_chan_doan': ['Bệnh bọng nước dạng Pemphigoid ở người già thể bọng nước căng.',
                         'Bệnh bọng nước dạng Pemphigoid ở người già giai đoạn hoạt tính.',
                         'Theo dõi bệnh bọng nước dạng Pemphigoid ở người già mức độ trung bình.',
                         'Bệnh bọng nước dạng Pemphigoid ở người già có ngứa ngáy toàn thân.',
                         'Nghi ngờ bệnh bọng nước dạng Pemphigoid ở người già thể da đỏ.',
                         'Bệnh bọng nước dạng Pemphigoid ở người già tái phát đợt cấp.'],
  'bien_the_ke_hoach': ['Xét nghiệm định lượng tự kháng thể kháng BP180 và BP230, dùng kem bôi '
                        'clobetasol propionate liều cao phối hợp kháng histamine uống.',
                        'Chỉ định sinh thiết da làm miễn dịch huỳnh quang trực tiếp tìm lắng đọng '
                        'IgG màng đáy, bôi corticoid rất mạnh tại chỗ.',
                        'Làm xét nghiệm ELISA định lượng kháng thể BP180, bôi mỡ clobetasol toàn '
                        'thân kết hợp thuốc giảm ngứa kháng histamine thế hệ hai.',
                        'Sinh thiết tổn thương bọng nước, bôi kem corticoid liều cao trên vùng da '
                        'có bọng, theo dõi chức năng thận và đường máu người cao tuổi.',
                        'Xét nghiệm miễn dịch huỳnh quang màng đáy biểu bì, chỉ định bôi corticoid '
                        'tại chỗ kết hợp thuốc chống ngứa ban đêm.',
                        'Hướng dẫn bôi clobetasol dạng kem toàn thân, chăm sóc vô trùng các bọng '
                        'nước căng vỡ, xét nghiệm công thức máu toàn phần.'],
  'bien_the_kham': ['Ghi nhận nhiều bọng nước căng chắc chứa dịch trong suốt, dấu hiệu Nikolsky âm '
                    'tính, nền da xung quanh có dát đỏ phù nề.',
                    'Bọng nước kích thước 1-3cm vách dày khó vỡ ở vùng bụng và đùi, dấu hiệu '
                    'Nikolsky âm tính, không có tổn thương niêm mạc miệng.',
                    'Nhiều bọng nước căng bóng chứa dịch trong trên nền dát đỏ dạng mề đay, nghiệm '
                    'pháp Nikolsky hoàn toàn âm tính.',
                    'Tổn thương da gồm các bọng nước căng chắc mọc đối xứng ở nếp gấp và chi, '
                    'không trợt niêm mạc, dấu hiệu Nikolsky âm tính.',
                    'Khám thấy bọng nước vách dày căng tròn, đáy tổn thương không bị rách khi miết '
                    'ngón tay, Nikolsky âm tính rõ.',
                    'Bọng nước căng chứa dịch vàng chanh phân bố ở mặt trong đùi và cánh tay, dấu '
                    'hiệu Nikolsky âm tính, da có sẩn phù ngứa.'],
  'chan_doan': 'Bệnh bọng nước dạng Pemphigoid ở người già thể bọng nước căng.',
  'chinh': ['nổi nhiều bọng nước căng dày khó vỡ kích thước lớn trên nền ban đỏ hoặc da lành',
            'ngứa ngáy dữ dội kéo dài toàn thân xuất hiện trước khi tổn thương bọng nổi lên',
            'vị trí bọng nước tập trung chủ yếu ở vùng bụng dưới đùi trong và mặt gấp cẳng tay'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Xét nghiệm định lượng tự kháng thể kháng BP180 và BP230, dùng kem bôi clobetasol '
              'propionate liều cao phối hợp kháng histamine uống.',
  'kham': 'Ghi nhận nhiều bọng nước căng chắc chứa dịch trong suốt, dấu hiệu Nikolsky âm tính, nền '
          'da xung quanh có dát đỏ phù nề.',
  'nhom': 'người lớn',
  'phu': ['các vết trợt nông sau khi bọng vỡ có khuynh hướng tự lành nhanh không để lại sẹo',
          'thỉnh thoảng có vài sẩn phù đỏ ngứa tương tự mày đay xen kẽ rải rác',
          'giấc ngủ bị xáo trộn do cơn ngứa ngáy bùng phát mạnh vào ban đêm'],
  'ten': 'bệnh bọng nước dạng Pemphigoid ở người già'},
 {'bien_the_chan_doan': ['Viêm da dạng herpes Duhring-Brocq liên quan nhạy cảm với gluten.',
                         'Viêm da dạng herpes Duhring-Brocq giai đoạn hoạt tính.',
                         'Theo dõi viêm da dạng herpes Duhring-Brocq thể đối xứng.',
                         'Viêm da dạng herpes Duhring-Brocq tái phát đợt cấp.',
                         'Nghi ngờ viêm da dạng herpes Duhring-Brocq có triệu chứng tiêu hóa nhẹ.',
                         'Bệnh viêm da dạng herpes Duhring-Brocq mạn tính.'],
  'bien_the_ke_hoach': ['Tư vấn chế độ ăn kiêng loại bỏ hoàn toàn gluten trong khẩu phần, xét '
                        'nghiệm kháng thể IgA kháng nội mạc cơ, điều trị dapsone đường uống.',
                        'Chỉ định xét nghiệm IgA kháng transglutaminase mô, bắt đầu điều trị '
                        'dapsone sau khi kiểm tra men G6PD, kiêng ăn bánh mì lúa mì.',
                        'Làm sinh thiết da làm miễn dịch huỳnh quang tìm lắng đọng IgA đỉnh nhú '
                        'bì, dùng dapsone đường uống và kiểm tra công thức máu.',
                        'Tư vấn thực đơn không chứa lúa mì lúa mạch trọn đời, định lượng G6PD '
                        'trước khi kê đơn dapsone uống, bổ sung kem bôi dịu ngứa.',
                        'Chỉ định chế độ ăn kiêng gluten nghiêm ngặt, xét nghiệm kháng thể tự miễn '
                        'ruột non, dùng dapsone liều thấp tăng dần.',
                        'Hướng dẫn thực dưỡng không gluten hoàn toàn, kê đơn dapsone kết hợp '
                        'vitamin và theo dõi sát chỉ số hemoglobin máu.'],
  'bien_the_kham': ['Tổn thương đa dạng gồm sẩn đỏ, mụn nước dạng herpes mọc thành chùm đối xứng '
                    'mặt duỗi khuỷu và gối, nhiều vết xước gãi.',
                    'Các cụm mụn nước căng nhỏ phân bố đối xứng hai bên cùi chỏ và mông, bề mặt da '
                    'có sẩn phù đỏ và vết cào gãi.',
                    'Khám thấy mụn nước mọc chùm như hạt chùm nho trên nền ban đỏ đối xứng, nhiều '
                    'mài nâu do gãi xước sâu.',
                    'Tổn thương dạng đa hình sẩn mụn nước thành cụm ở khuỷu tay đầu gối, kèm theo '
                    'nhiều vết trầy da do cào xước liên tục.',
                    'Ghi nhận mụn nước căng xếp vòng cung ở vùng xương cùng và khuỷu tay hai bên, '
                    'tổn thương đối xứng điển hình.',
                    'Mụn nước nhỏ mọc thành đám trên nền da đỏ ngứa châm chích vùng gối và khuỷu, '
                    'các vết xước biểu bì rải rác.'],
  'chan_doan': 'Viêm da dạng herpes Duhring-Brocq liên quan nhạy cảm với gluten.',
  'chinh': ['xuất hiện các đám mụn nước căng nhỏ xếp thành cụm đối xứng hai bên cơ thể',
            'ngứa rát dữ dội và cảm giác châm chích bỏng rát tại vùng da tổn thương',
            'vị trí tổn thương ưu thế ở mặt duỗi cẳng tay khuỷu tay đầu gối và vùng mông'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Tư vấn chế độ ăn kiêng loại bỏ hoàn toàn gluten trong khẩu phần, xét nghiệm kháng '
              'thể IgA kháng nội mạc cơ, điều trị dapsone đường uống.',
  'kham': 'Tổn thương đa dạng gồm sẩn đỏ, mụn nước dạng herpes mọc thành chùm đối xứng mặt duỗi '
          'khuỷu và gối, nhiều vết xước gãi.',
  'nhom': 'người lớn',
  'phu': ['triệu chứng tiêu chảy phân lỏng thoáng qua hoặc đầy bụng sau khi ăn tinh bột lúa mì',
          'vết cào gãi sâu tạo mài xước nâu sẫm và dát sậm màu sắc tố sau viêm',
          'cảm giác châm chích rát tiền triệu báo trước tại vị trí chuẩn bị nổi mụn mới'],
  'ten': 'viêm da dạng herpes Duhring-Brocq'},
 {'bien_the_chan_doan': ['Hội chứng Stevens-Johnson do thuốc dị ứng mức độ cấp tính.',
                         'Hội chứng Stevens-Johnson do thuốc dị ứng nghi do kháng sinh.',
                         'Theo dõi hội chứng Stevens-Johnson do thuốc dị ứng diện tích trợt dưới '
                         '10%.',
                         'Hội chứng Stevens-Johnson do thuốc dị ứng có tổn thương niêm mạc mắt.',
                         'Hội chứng Stevens-Johnson do thuốc dị ứng đợt cấp nguy cơ tiến triển.',
                         'Cấp cứu hội chứng Stevens-Johnson do thuốc dị ứng thể nặng.'],
  'bien_the_ke_hoach': ['Ngừng ngay lập tức toàn bộ các thuốc nghi ngờ, chuyển phòng điều trị tích '
                        'cực bỏng, bù dịch điện giải và truyền tĩnh mạch immunoglobulin IVIG.',
                        'Dừng ngay thuốc nghi gây dị ứng, chuyển khoa hồi sức bỏng, chăm sóc mắt '
                        'phòng dính mi cầu, cân nhắc truyền IVIG hoặc cyclosporin.',
                        'Dừng mọi loại thuốc đang dùng, bù dịch qua đường tĩnh mạch theo dõi lượng '
                        'nước tiểu, tra mắt thuốc mỡ bảo vệ giác mạc liên tục.',
                        'Ngừng thuốc lập tức, chuyển vào phòng cách ly vô trùng, hồi sức cân bằng '
                        'nước điện giải, hội chẩn chuyên khoa mắt và da liễu.',
                        'Đình chỉ ngay các thuốc nghi vấn, bọc tổn thương bằng gạc vô trùng chống '
                        'dính, truyền dịch nuôi dưỡng và dùng kháng histamine.',
                        'Ngừng toàn bộ thuốc, theo dõi sát sinh hiệu và diện tích bong da hàng '
                        'ngày, dinh dưỡng qua ống thông dạ dày, chăm sóc vô trùng.'],
  'bien_the_kham': ['Bong trợt thượng bì khoảng 7% diện tích cơ thể, môi đóng vảy tiết nâu đen '
                    'hoại tử, kết mạc mắt viêm trợt sung huyết.',
                    'Diện tích da bong trợt dưới 10% bề mặt cơ thể, môi nứt nẻ đóng mài đen hoại '
                    'tử, kết mạc hai mắt sung huyết đỏ rực.',
                    'Tổn thương da dạng bia bắn không điển hình kèm trợt da khoảng 6%, hai niêm '
                    'mạc miệng và mắt viêm loét rỉ máu.',
                    'Da nhiều dát đỏ tím kèm bọng nước mềm trợt nông khoảng 8% diện tích, niêm mạc '
                    'môi loét xuất huyết đặc trưng.',
                    'Ghi nhận trợt biểu bì da 5% diện tích cơ thể, miệng loét đau rát không ăn '
                    'uống được, kết mạc mắt tiết dịch nhầy.',
                    'Bong tróc da diện tích 7%, dấu hiệu Nikolsky dương tính vùng ban đỏ, loét môi '
                    'miệng và niêm mạc sinh dục cấp.'],
  'chan_doan': 'Hội chứng Stevens-Johnson do thuốc dị ứng mức độ cấp tính.',
  'chinh': ['hoại tử bong trợt da nông diện tích dưới mười phần trăm kèm ban đỏ bia bắn không điển '
            'hình',
            'loét trợt xuất huyết đau đớn dữ dội tại ít nhất hai vị trí niêm mạc mắt môi hoặc sinh '
            'dục',
            'sốt cao đột ngột mệt lả xuất hiện sau khi dùng thuốc nghi ngờ từ một đến ba tuần'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Ngừng ngay lập tức toàn bộ các thuốc nghi ngờ, chuyển phòng điều trị tích cực bỏng, '
              'bù dịch điện giải và truyền tĩnh mạch immunoglobulin IVIG.',
  'kham': 'Bong trợt thượng bì khoảng 7% diện tích cơ thể, môi đóng vảy tiết nâu đen hoại tử, kết '
          'mạc mắt viêm trợt sung huyết.',
  'nhom': 'cả hai',
  'phu': ['mắt đỏ chói cộm rát sợ ánh sáng và tăng tiết dịch rỉ mắt',
          'nuốt đau nuốt khó làm giảm rõ rệt lượng thức ăn nước uống nạp vào',
          'cảm giác nóng rát châm chích bỏng buốt lan tỏa khắp bề mặt da cơ thể'],
  'ten': 'hội chứng Stevens-Johnson do thuốc dị ứng'},
 {'bien_the_chan_doan': ['Hoại tử thượng bì nhiễm độc Lyell do thuốc dị ứng thể nặng.',
                         'Hội chứng Lyell hoại tử thượng bì nhiễm độc do thuốc dị ứng đợt cấp.',
                         'Hoại tử thượng bì nhiễm độc Lyell do thuốc diện tích trợt trên 30%.',
                         'Cấp cứu hoại tử thượng bì nhiễm độc Lyell do thuốc dị ứng có suy tuần '
                         'hoàn.',
                         'Hoại tử thượng bì nhiễm độc Lyell do thuốc thể tiến triển nhanh.',
                         'Theo dõi hoại tử thượng bì nhiễm độc Lyell do thuốc biến chứng nhiễm '
                         'trùng.'],
  'bien_the_ke_hoach': ['Chuyển đơn vị hồi sức tích cực cách ly vô trùng, hồi sức bù dịch thể tích '
                        'lớn theo phác đồ bỏng, hội chẩn dùng cyclosporin hoặc IVIG.',
                        'Hồi sức tích cực bù dịch điện giải theo công thức Parkland cải biên, cách '
                        'ly buồng vô trùng nhiệt độ ấm, dùng IVIG liều cao.',
                        'Đặt catheter tĩnh mạch trung tâm bù dịch chống sốc, ngừng tuyệt đối các '
                        'thuốc dị ứng, chăm sóc chống dính niêm mạc mắt.',
                        'Chuyển khoa Hồi sức cấp cứu, nuôi dưỡng qua tĩnh mạch hoàn toàn, kiểm '
                        'soát nhiễm khuẩn tại chỗ bằng gạc hydrogel và kháng sinh phổ rộng.',
                        'Cấp cứu hồi sức tuần hoàn, theo dõi lượng nước tiểu qua sonde bàng quang, '
                        'hội chẩn đa chuyên khoa điều trị ức chế miễn dịch đặc hiệu.',
                        'Cách ly phòng hồi sức bỏng vô trùng, kiểm soát thăng bằng kiềm toan và '
                        'điện giải, truyền albumin bù dịch và giảm đau toàn thân.'],
  'bien_the_kham': ['Thượng bì bong trợt chiếm 38% diện tích cơ thể, da trượt tróc thành mảng lớn, '
                    'loét niêm mạc miệng và mắt diện rộng.',
                    'Diện tích bong tróc thượng bì hoại tử 35% diện tích da, dấu hiệu Nikolsky '
                    'dương tính diện rộng, sốt 39.5 độ C lơ mơ.',
                    'Khám thấy da tuột tróc thành mảng lớn chiếm 40% diện tích, nền da trợt đỏ rỉ '
                    'dịch nhiều, niêm mạc miệng mắt trợt loét nặng.',
                    'Thượng bì hoại tử bong trợt 32% cơ thể, toàn bộ môi và khoang miệng trợt loét '
                    'rỉ máu, mạch nhanh huyết áp dao động.',
                    'Tổn thương da dạng hội chứng Lyell bong tróc 36% diện tích, da trượt như luộc '
                    'nước sôi, mất nước điện giải nặng.',
                    'Ghi nhận hoại tử trợt da 42% diện tích cơ thể, Nikolsky dương tính toàn bộ '
                    'vùng dát đỏ, niêm mạc đa hốc tự nhiên bị tổn thương.'],
  'chan_doan': 'Hoại tử thượng bì nhiễm độc Lyell do thuốc dị ứng thể nặng.',
  'chinh': ['thượng bì bong tróc hoại tử từng mảng lớn trên ba mươi phần trăm diện tích da cơ thể',
            'da trợt đỏ ướt như bị luộc nước sôi với dấu hiệu Nikolsky dương tính trên diện rộng',
            'nhiễm độc toàn thân nặng sốt cao liên tục tụt huyết áp và lơ mơ mệt lả'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chuyển đơn vị hồi sức tích cực cách ly vô trùng, hồi sức bù dịch thể tích lớn theo '
              'phác đồ bỏng, hội chẩn dùng cyclosporin hoặc IVIG.',
  'kham': 'Thượng bì bong trợt chiếm 38% diện tích cơ thể, da trượt tróc thành mảng lớn, loét niêm '
          'mạc miệng và mắt diện rộng.',
  'nhom': 'cả hai',
  'phu': ['tổn thương niêm mạc hoại tử toàn bộ vùng miệng thanh quản và đường tiêu hóa',
          'mất nước điện giải ồ ạt qua nền da trợt tương tự phỏng diện rộng',
          'đau rát dữ dội toàn thân đến mức không chịu nổi va chạm nhẹ của vải áo'],
  'ten': 'hoại tử thượng bì nhiễm độc Lyell do thuốc'},
 {'bien_the_chan_doan': ['Vảy phấn đỏ chân tóc thể người lớn kinh điển.',
                         'Bệnh vảy phấn đỏ chân tóc thể mảng đỏ nang lông.',
                         'Theo dõi vảy phấn đỏ chân tóc giai đoạn hoạt tính.',
                         'Vảy phấn đỏ chân tóc thể sừng hóa lòng bàn tay bàn chân.',
                         'Nghi ngờ vảy phấn đỏ chân tóc phân biệt với vảy nến đỏ da.',
                         'Vảy phấn đỏ chân tóc mạn tính tái phát.'],
  'bien_the_ke_hoach': ['Chỉ định sinh thiết da kiểm tra mô bệnh học đặc trưng, kê đơn retinoid '
                        'đường uống acitretin phối hợp bôi thuốc tiêu sừng mỡ salicylic.',
                        'Sinh thiết tổn thương da kiểm tra mô bệnh học, điều trị acitretin đường '
                        'uống kiểm tra men gan mỡ máu, bôi mỡ salicylic 5%.',
                        'Chỉ định xét nghiệm chức năng gan thận trước khi dùng retinoid toàn thân, '
                        'hướng dẫn bôi kem làm mềm da chứa ure 10%.',
                        'Hội chẩn chuyên khoa Da liễu, làm giải phẫu bệnh tổn thương sẩn nang '
                        'lông, phối hợp bôi thuốc bong sừng và quang hóa trị liệu.',
                        'Kê đơn thuốc uống điều hòa sừng hóa acitretin, bôi mỡ calcipotriol kết '
                        'hợp dưỡng ẩm mỡ petrolatum làm mềm lớp sừng sáp.',
                        'Làm xét nghiệm sinh hóa máu định kỳ, dùng retinoid theo bậc liều chuẩn, '
                        'hướng dẫn ngâm nước ấm và bôi thuốc mỡ tiêu sừng.'],
  'bien_the_kham': ['Mảng đỏ cam phủ vảy mịn rải rác, các nốt sẩn sừng nang lông điển hình mu ngón '
                    'tay, dày sừng lòng bàn tay kiểu sáp vàng.',
                    'Khám thấy da đỏ cam có các đảo da lành kích thước nhỏ, sẩn sừng hình nón mu '
                    'ngón tay, lòng bàn chân dày sừng vàng như vỏ cam.',
                    'Tổn thương dạng mảng đỏ vảy mịn rải rác thân mình, dày sừng bàn tay bàn chân '
                    'màu sáp nến, nhiều sẩn sừng nút nang lông.',
                    'Ghi nhận sẩn dày sừng bao quanh chân lông mu ngón tay, mảng hồng ban phủ vảy '
                    'phấn xen kẽ vùng da nguyên vẹn.',
                    'Da toàn thân có các mảng đỏ cam bong vảy cám mịn, lòng bàn tay đóng sừng cứng '
                    'màu vàng sáp, đầu ngón tay nứt nẻ nhẹ.',
                    'Nhiều sẩn sừng nang lông nhọn khi sờ ráp như bàn nạo ở mu tay, mảng ban đỏ '
                    'tróc vảy mịn, da đầu có vảy dày.'],
  'chan_doan': 'Vảy phấn đỏ chân tóc thể người lớn kinh điển.',
  'chinh': ['nổi các sẩn sừng nhọn hình nón tại nang lông ở mu đốt ngón tay đốt một và đốt hai',
            'các mảng da đỏ cam phủ vảy phấn mịn lan rộng xen kẽ các đảo da hoàn toàn bình thường',
            'dày sừng lòng bàn tay bàn chân màu vàng cam như sáp sừng cứng ráp'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định sinh thiết da kiểm tra mô bệnh học đặc trưng, kê đơn retinoid đường uống '
              'acitretin phối hợp bôi thuốc tiêu sừng mỡ salicylic.',
  'kham': 'Mảng đỏ cam phủ vảy mịn rải rác, các nốt sẩn sừng nang lông điển hình mu ngón tay, dày '
          'sừng lòng bàn tay kiểu sáp vàng.',
  'nhom': 'người lớn',
  'phu': ['cảm giác căng cứng nứt nẻ đau rát tại lòng bàn tay và gót chân khi cử động',
          'da đầu phủ vảy trắng dày tương tự vảy nến làm rụng tóc nhẹ thoáng qua',
          'ngứa ngáy mức độ nhẹ đến trung bình rải rác toàn thân'],
  'ten': 'vảy phấn đỏ chân tóc'},
 {'bien_the_chan_doan': ['Vảy phấn hồng Gibert giai đoạn phát ban thứ phát.',
                         'Vảy phấn hồng Gibert thể điển hình có mảng báo hiệu.',
                         'Theo dõi vảy phấn hồng Gibert đợt phát tán dát đỏ thân mình.',
                         'Vảy phấn hồng Gibert cấp tính phân bố hình nhánh thông.',
                         'Nghi ngờ vảy phấn hồng Gibert phân biệt với giang mai thời kỳ hai.',
                         'Vảy phấn hồng Gibert thể nhẹ lành tính.'],
  'bien_the_ke_hoach': ['Giải thích tính chất lành tính tự thoái lui của bệnh trong 6-8 tuần, dùng '
                        'kem dưỡng ẩm làm dịu da và thuốc kháng histamine khi ngứa.',
                        'Tư vấn người bệnh yên tâm bệnh tự khỏi không để lại sẹo, bôi kem '
                        'hydrocortisone nhẹ nếu ngứa nhiều, tránh tắm nước quá nóng.',
                        'Kê đơn thuốc kháng histamine H1 uống giảm ngứa, bôi sữa dưỡng ẩm làm mềm '
                        'da toàn thân, xét nghiệm RPR loại trừ giang mai.',
                        'Hướng dẫn chế độ tắm rửa nhẹ nhàng tránh chà xát xà phòng kiềm mạnh, bôi '
                        'hồ nước làm dịu tổn thương ban đỏ.',
                        'Giải thích diễn tiến lành tính kéo dài 1-2 tháng, kê thuốc chống ngứa '
                        'đường uống, hẹn tái khám sau 4 tuần đánh giá lui bệnh.',
                        'Kê đơn lotion làm mát da có chứa menthol nhẹ hoặc calamine, tư vấn mặc '
                        'quần áo cotton rộng rãi thoáng mát.'],
  'bien_the_kham': ['Ghi nhận mảng báo hiệu kích thước 4cm ở ngực, hàng chục dát đỏ hình bầu dục '
                    'nhỏ hơn phân bố đối xứng dọc xương sườn hình nhánh thông.',
                    'Mảng tổn thương tiên phát hình bầu dục viền vảy xếp nếp ở lưng, nhiều dát '
                    'hồng ban nhỏ chạy xuôi theo nếp lằn da vùng ngực.',
                    'Khám thấy ban mẹ kích thước 3x5cm ở mạn sườn, các dát đỏ nhỏ viền vảy mỏng '
                    'xếp hình cây thông noel đặc trưng sau lưng.',
                    'Tổn thương da gồm mảng herald patch viền vảy phấn mịn kèm hàng loạt dát sẩn '
                    'màu hồng nhạt dọc theo cung sườn.',
                    'Các dát màu hồng phấn hình bầu dục viền vảy bên trong mép tổn thương, trục '
                    'dài song song đường căng da Langer vùng thân mình.',
                    'Ghi nhận tổn thương da điển hình dạng cây thông ở lưng, ban mẹ đã nhạt màu ở '
                    'bụng, không có tổn thương niêm mạc hay lòng bàn tay.'],
  'chan_doan': 'Vảy phấn hồng Gibert giai đoạn phát ban thứ phát.',
  'chinh': ['xuất hiện tổn thương ban mẹ mảng báo hiệu hình bầu dục viền vảy phấn đi trước',
            'sau một đến hai tuần phát tán nhiều dát đỏ nhỏ hình bầu dục xếp dọc đường căng da như '
            'hình cây thông',
            'vảy da mỏng xếp thành dải viền xung quanh bên trong mép của tổn thương'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Giải thích tính chất lành tính tự thoái lui của bệnh trong 6-8 tuần, dùng kem dưỡng '
              'ẩm làm dịu da và thuốc kháng histamine khi ngứa.',
  'kham': 'Ghi nhận mảng báo hiệu kích thước 4cm ở ngực, hàng chục dát đỏ hình bầu dục nhỏ hơn '
          'phân bố đối xứng dọc xương sườn hình nhánh thông.',
  'nhom': 'cả hai',
  'phu': ['ngứa ngáy thoảng qua mức độ nhẹ khi cơ thể nóng bức hoặc vận động đổ mồ hôi',
          'mệt mỏi nhẹ đau đầu thoáng qua trước khi tổn thương da bùng phát',
          'vùng da tổn thương tập trung phần lớn ở thân mình ngực bụng và lưng trên'],
  'ten': 'vảy phấn hồng Gibert'},
 {'bien_the_chan_doan': ['Lichen phẳng ở da và niêm mạc miệng tiến triển.',
                         'Bệnh lichen phẳng ở da và niêm mạc miệng thể sẩn đa giác.',
                         'Lichen phẳng ở da và niêm mạc miệng có mạng lưới sọc Wickham.',
                         'Theo dõi lichen phẳng ở da và niêm mạc miệng mạn tính.',
                         'Lichen phẳng ở da và niêm mạc miệng thể kết hợp da niêm mạc.',
                         'Nghi ngờ lichen phẳng ở da và niêm mạc miệng đợt hoạt tính.'],
  'bien_the_ke_hoach': ['Bôi corticosteroid tại chỗ dạng mỡ cho da và dạng gel dính cho niêm mạc '
                        'miệng, hướng dẫn vệ sinh răng miệng bằng dung dịch sát khuẩn nhẹ.',
                        'Chỉ định bôi mỡ clobetasol propionate cho tổn thương da, gel '
                        'triamcinolone acetonide thoa niêm mạc miệng sau ăn, dùng kháng histamine.',
                        'Sinh thiết sẩn da làm mô bệnh học loại trừ bệnh khác, xét nghiệm virus '
                        'viêm gan C, bôi corticoid giảm viêm tại chỗ.',
                        'Hướng dẫn bôi mỡ betamethasone mặt gấp cổ tay, tránh ăn đồ cay nóng kích '
                        'thích niêm mạc miệng, súc họng bằng nước muối sinh lý.',
                        'Chỉ định thuốc bôi ức chế calcineurin tacrolimus cho tổn thương niêm mạc '
                        'miệng dai dẳng, bôi mỡ corticoid mạnh trên da.',
                        'Tư vấn kiểm tra định kỳ niêm mạc miệng, kê đơn bôi thuốc corticoid niêm '
                        'mạc dạng dính Orabase, kiểm soát ngứa da bằng thuốc uống.'],
  'bien_the_kham': ['Nhiều sẩn phẳng đa giác màu tím hoa cà ở mặt gấp cổ tay, niêm mạc má có mạng '
                    'lưới sọc trắng Wickham dạng ren hoa.',
                    'Sẩn màu tím bóng đỉnh phẳng hình đa giác đối xứng hai cổ tay, niêm mạc miệng '
                    'có tổn thương dạng lưới trắng Wickham không trợt.',
                    'Khám thấy các nốt sẩn gờ nhẹ màu đỏ tím ánh bóng dưới ánh sáng xiên, mạng '
                    'lưới trắng dạng ren ở niêm mạc má đối xứng.',
                    'Tổn thương da dạng 4 chữ P kinh điển sẩn tím ngứa đa giác ở mặt gấp cẳng tay, '
                    'niêm mạc miệng có sọc trắng mạng lưới.',
                    'Ghi nhận sẩn phẳng màu tím hoa cà có sọc Wickham nhỏ li ti trên mặt sẩn, niêm '
                    'mạc môi và má có dải trắng đan xen.',
                    'Nhiều sẩn phẳng ngứa dữ dội ở cổ tay và mắt cá chân, tổn thương niêm mạc má '
                    'dạng ren lưới trắng mịn không loét.'],
  'chan_doan': 'Lichen phẳng ở da và niêm mạc miệng tiến triển.',
  'chinh': ['các sẩn dẹt đa giác màu đỏ tím bóng láng đỉnh phẳng gờ nhẹ trên mặt da',
            'mạng lưới các đường sọc trắng mảnh Wickham trên bề mặt sẩn và niêm mạc má trong',
            'cơn ngứa dữ dội dai dẳng đặc biệt tại mặt gấp cổ tay và cẳng chân trước'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Bôi corticosteroid tại chỗ dạng mỡ cho da và dạng gel dính cho niêm mạc miệng, '
              'hướng dẫn vệ sinh răng miệng bằng dung dịch sát khuẩn nhẹ.',
  'kham': 'Nhiều sẩn phẳng đa giác màu tím hoa cà ở mặt gấp cổ tay, niêm mạc má có mạng lưới sọc '
          'trắng Wickham dạng ren hoa.',
  'nhom': 'người lớn',
  'phu': ['cảm giác cay rát xót niêm mạc miệng khi ăn đồ mặn cay hoặc chua nóng',
          'móng tay có khía dọc teo mỏng hoặc chẻ đôi ở bờ tự do',
          'tăng sắc tố sẫm màu nâu đen tồn tại lâu dài sau khi sẩn xẹp phẳng'],
  'ten': 'lichen phẳng ở da và niêm mạc miệng'},
 {'bien_the_chan_doan': ['Lichen xơ teo âm hộ mạn tính thể teo hẹp.',
                         'Lichen xơ teo âm hộ giai đoạn hoạt tính có nứt kẽ đau rát.',
                         'Theo dõi lichen xơ teo âm hộ thể teo dính cấu trúc môi bé.',
                         'Bệnh lichen xơ teo âm hộ ở phụ nữ sau mãn kinh.',
                         'Lichen xơ teo âm hộ biến chứng co hẹp cửa mình.',
                         'Nghi ngờ lichen xơ teo âm hộ tổn thương xơ hóa hình số tám.'],
  'bien_the_ke_hoach': ['Chỉ định bôi corticosteroid nhóm rất mạnh clobetasol propionate theo phác '
                        'đồ hạ bậc dần, dùng chất làm mềm da và theo dõi nguy cơ ung thư biểu mô.',
                        'Bôi kem clobetasol propionate 0.05% hàng đêm trong 1 tháng rồi giảm liều '
                        'duy trì, dùng kem bôi trơn dưỡng ẩm không hương liệu.',
                        'Hướng dẫn vệ sinh vùng kín nhẹ nhàng bằng nước ấm không xà phòng xút, bôi '
                        'mỡ corticoid mạnh tại chỗ, theo dõi định kỳ 6 tháng.',
                        'Chỉ định sinh thiết nếu có mảng dày sừng sần sùi bất thường loại trừ ác '
                        'tính, duy trì bôi thuốc mỡ chống xơ teo bảo vệ biểu mô.',
                        'Kê đơn thuốc mỡ corticoid tác dụng mạnh giảm viêm xơ, tư vấn dùng kem '
                        'dưỡng ẩm phục hồi hàng rào biểu mô sau khi tiểu tiện.',
                        'Hội chẩn chuyên khoa Phụ sản và Da liễu, bôi thuốc ức chế calcineurin '
                        'tacrolimus duy trì sau khi kiểm soát viêm bằng corticoid.'],
  'bien_the_kham': ['Mảng xơ teo trắng ngà phân bố dạng hình số 8 quanh âm hộ và hậu môn, co kéo '
                    'mất ranh giới môi bé, nhiều vết nứt nông.',
                    'Da vùng âm hộ teo mỏng trắng bóng như giấy cuốn thuốc lá, môi nhỏ teo phẳng '
                    'dính liền môi lớn, lỗ âm đạo co hẹp nhẹ.',
                    'Tổn thương xơ teo màu trắng ngà quanh âm hộ và tầng sinh môn, niêm mạc khô '
                    'ráp có nhiều vết nứt kẽ rỉ máu rải rác.',
                    'Khám phụ khoa thấy mảng bạch sản xơ hóa đối xứng quanh âm hộ - hậu môn, mũ âm '
                    'vật teo dính, mô mềm mất độ đàn hồi.',
                    'Ghi nhận teo xơ trắng ngà niêm mạc sinh dục ngoài, cấu trúc giải phẫu môi bé '
                    'bị biến dạng co rút, vết trợt xước do gãi.',
                    'Vùng da âm hộ xơ cứng mỏng dính màu xà cừ, nứt kẽ nếp gấp môi lớn, âm đạo hẹp '
                    'nhẹ gây khó khăn khi đặt mỏ vịt khám.'],
  'chan_doan': 'Lichen xơ teo âm hộ mạn tính thể teo hẹp.',
  'chinh': ['teo mỏng da và niêm mạc vùng sinh dục ngoài tạo mảng xơ hóa trắng ngà như vỏ xà cừ',
            'ngứa rát dữ dội kéo dài và đau buốt nhiều tại vùng tầng sinh môn',
            'co rút dính môi bé làm hẹp lỗ âm đạo gây đau đớn khi quan hệ tình dục'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định bôi corticosteroid nhóm rất mạnh clobetasol propionate theo phác đồ hạ bậc '
              'dần, dùng chất làm mềm da và theo dõi nguy cơ ung thư biểu mô.',
  'kham': 'Mảng xơ teo trắng ngà phân bố dạng hình số 8 quanh âm hộ và hậu môn, co kéo mất ranh '
          'giới môi bé, nhiều vết nứt nông.',
  'nhom': 'người lớn',
  'phu': ['tiểu khó tiểu buốt hoặc cảm giác rát xót khi dòng nước tiểu chạm vào vết nứt nẻ',
          'các vết nứt kẽ và chấm xuất huyết dưới biểu mô do da khô xơ dễ rách trợt',
          'cảm giác bức bối khô khốc khó chịu ảnh hưởng nghiêm trọng đến tâm lý sinh hoạt'],
  'ten': 'lichen xơ teo âm hộ'},
 {'bien_the_chan_doan': ['Xơ cứng bì khu trú dạng mảng morphea đợt hoạt tính.',
                         'Bệnh xơ cứng bì khu trú dạng mảng morphea thể mảng đơn độc.',
                         'Xơ cứng bì khu trú dạng mảng morphea giai đoạn viêm hoạt động.',
                         'Theo dõi xơ cứng bì khu trú dạng mảng morphea vùng thân mình.',
                         'Xơ cứng bì khu trú dạng mảng morphea thể teo xơ mạn tính.',
                         'Nghi ngờ xơ cứng bì khu trú dạng mảng morphea tiến triển lan rộng.'],
  'bien_the_ke_hoach': ['Chỉ định siêu âm đo độ dày trung bì tổn thương, bôi tacrolimus hoặc '
                        'calcipotriol tại chỗ, chiếu tia cực tím UVA1 nếu tổn thương lan rộng.',
                        'Siêu âm da đánh giá mức độ thâm nhiễm trung bì và mô dưới da, chỉ định '
                        'bôi mỡ clobetasol kết hợp calcipotriol hàng ngày.',
                        'Làm sinh thiết da xác định xơ hóa collagen trung bì, dùng thuốc bôi ức '
                        'chế miễn dịch tại chỗ tacrolimus 0.1%, vật lý trị liệu.',
                        'Theo dõi sự tiến triển kích thước tổn thương bằng chụp ảnh định kỳ, cân '
                        'nhắc điều trị methotrexate đường uống nếu tổn thương lan tỏa.',
                        'Chỉ định bôi mỡ corticoid nhóm mạnh trong giai đoạn viền tím hoạt tính, '
                        'bôi kem dưỡng ẩm làm mềm da hàng ngày.',
                        'Hội chẩn chuyên khoa Da liễu làm kháng thể kháng nhân ANA loại trừ xơ '
                        'cứng bì hệ thống, áp dụng liệu pháp ánh sáng UVA1.'],
  'bien_the_kham': ['Mảng xơ cứng kích thước 5x8cm ở mạn sườn, trung tâm cứng chắc ấn không lõm '
                    'màu trắng ngà, bờ viền tím hoa cà sắc nét.',
                    'Tổn thương dạng mảng da dày cứng như gỗ ở vùng thắt lưng, trung tâm màu trắng '
                    'sứ nhẵn bóng, viền tím lilac bao quanh.',
                    'Khám thấy mảng thâm nhiễm xơ cứng ấn nhấc nếp da khó khăn, bề mặt mất hoàn '
                    'toàn lông nang, bờ viền đỏ tím đang lan.',
                    'Ghi nhận mảng xơ cứng khu trú đường kính 6cm ở bụng, da bóng lộn không véo '
                    'lên được, ranh giới rõ với da lành.',
                    'Vùng da mạn sườn xơ teo cứng ngắc màu vàng ngà, viền ngoài còn hoạt tính viêm '
                    'màu tím hoa cà, không có hội chứng Raynaud.',
                    'Mảng tổn thương da cứng chắc nhẵn bóng vùng đùi, mất cảm giác mồ hôi tại chỗ, '
                    'xung quanh có quầng sắc tố nâu nhạt.'],
  'chan_doan': 'Xơ cứng bì khu trú dạng mảng morphea đợt hoạt tính.',
  'chinh': ['mảng da xơ cứng dầy chắc hình bầu dục bề mặt nhẵn bóng mất nếp nhăn tự nhiên',
            'vùng trung tâm mảng tổn thương teo trắng ngà ngả màu sáp ong',
            'viền xung quanh tổn thương có màu tím hoa cà đặc trưng trong giai đoạn đang hoạt '
            'động'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định siêu âm đo độ dày trung bì tổn thương, bôi tacrolimus hoặc calcipotriol '
              'tại chỗ, chiếu tia cực tím UVA1 nếu tổn thương lan rộng.',
  'kham': 'Mảng xơ cứng kích thước 5x8cm ở mạn sườn, trung tâm cứng chắc ấn không lõm màu trắng '
          'ngà, bờ viền tím hoa cà sắc nét.',
  'nhom': 'cả hai',
  'phu': ['mất lông rụng tóc và giảm tiết mồ hôi hoàn toàn tại vị trí mảng da xơ cứng',
          'cảm giác căng tức bó chặt da vùng ngực hoặc bụng khi cúi gập người',
          'tăng sắc tố màu nâu xỉn bao quanh vùng xơ teo khi bệnh bước vào giai đoạn thoái trào'],
  'ten': 'xơ cứng bì khu trú dạng mảng morphea'},
 {'bien_the_chan_doan': ['Ban đỏ đa dạng thể nhẹ sau tái phát nhiễm herpes simplex.',
                         'Ban đỏ đa dạng thể nhẹ thể ban bia bắn điển hình.',
                         'Theo dõi ban đỏ đa dạng thể nhẹ mức độ khu trú ở chi.',
                         'Ban đỏ đa dạng thể nhẹ giai đoạn cấp sau đợt mụn rộp.',
                         'Bệnh ban đỏ đa dạng thể nhẹ không có tổn thương niêm mạc nặng.',
                         'Nghi ngờ ban đỏ đa dạng thể nhẹ phản ứng sau nhiễm virus.'],
  'bien_the_ke_hoach': ['Kê đơn thuốc kháng virus acyclovir uống nếu có đợt herpes bùng phát, dùng '
                        'thuốc bôi giảm viêm nhẹ và kháng histamine chống ngứa.',
                        'Chỉ định thuốc kháng histamine H1 uống giảm ngứa, bôi kem hydrocortisone '
                        '1% làm dịu tổn thương da, theo dõi tổn thương niêm mạc.',
                        'Tư vấn điều trị dự phòng acyclovir nếu ban đỏ tái phát theo đợt herpes, '
                        'bôi hồ nước hoặc kem dưỡng ẩm dịu da.',
                        'Kê đơn thuốc giảm đau paracetamol khi cần, bôi kem kẽm oxide bảo vệ vùng '
                        'da tổn thương, hẹn tái khám sau 1 tuần.',
                        'Hướng dẫn vệ sinh răng miệng bằng dung dịch sát khuẩn dịu nhẹ, bôi kem '
                        'kháng viêm tại chỗ, theo dõi các hốc tự nhiên.',
                        'Giải thích diễn tiến lành tính tự thoái lui trong 2-3 tuần, tránh chà xát '
                        'cào gãi tổn thương, dùng thuốc dị ứng đường uống.'],
  'bien_the_kham': ['Nhiều tổn thương hình bia bắn ba vòng đồng tâm rõ nét ở mu bàn tay và cẳng '
                    'tay hai bên, niêm mạc miệng chỉ có một vết trợt nông.',
                    'Tổn thương da dạng hình bia bắn điển hình đường kính 1-2cm đối xứng hai mu '
                    'bàn tay, trung tâm sẫm màu viền đỏ tươi.',
                    'Khám thấy các sẩn hồng ban hình mắt bò ba vòng màu sắc khác nhau ở cẳng tay '
                    'và cẳng chân, niêm mạc tổn thương tối thiểu.',
                    'Ghi nhận ban đỏ hình bia bắn rải rác tứ chi, vòng ngoài đỏ viền giữa nhạt màu '
                    'tâm có mụn nước nhỏ, không trợt da diện rộng.',
                    'Các dát sẩn hình bia đồng tâm ở mu chân và mu tay hai bên, niêm mạc môi có '
                    'một vết trợt nông đóng vảy tiết, Nikolsky âm tính.',
                    'Nhiều nốt tổn thương da hình hồng tâm đặc trưng ở chi trên, cảm giác nóng rát '
                    'nhẹ tại chỗ, không có dấu hiệu hoại tử thượng bì.'],
  'chan_doan': 'Ban đỏ đa dạng thể nhẹ sau tái phát nhiễm herpes simplex.',
  'chinh': ['tổn thương dát sẩn hình bia bắn điển hình gồm ba vòng tròn đồng tâm phân định rõ',
            'tâm tổn thương sẫm màu có mụn nước nhỏ hoặc vảy hoại tử ở chính giữa',
            'phân bố tổn thương đối xứng ưu thế ở mu bàn tay mu bàn chân và cẳng tay cẳng chân'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Kê đơn thuốc kháng virus acyclovir uống nếu có đợt herpes bùng phát, dùng thuốc bôi '
              'giảm viêm nhẹ và kháng histamine chống ngứa.',
  'kham': 'Nhiều tổn thương hình bia bắn ba vòng đồng tâm rõ nét ở mu bàn tay và cẳng tay hai bên, '
          'niêm mạc miệng chỉ có một vết trợt nông.',
  'nhom': 'cả hai',
  'phu': ['tiền sử tái phát vết loét mụn rộp herpes môi trước đó khoảng bảy đến mười ngày',
          'ngứa châm chích hoặc cảm giác rát buốt nhẹ tại các nốt bia bắn',
          'có vài vết trợt nhỏ ở niêm mạc môi nhưng không lan rộng sang các hốc tự nhiên khác'],
  'ten': 'ban đỏ đa dạng thể nhẹ'},
 {'bien_the_chan_doan': ['Ban đỏ nốt ở cẳng chân hồng ban nút cấp tính.',
                         'Bệnh ban đỏ nốt ở cẳng chân hồng ban nút nghi sau nhiễm liên cầu khuẩn.',
                         'Theo dõi ban đỏ nốt ở cẳng chân hồng ban nút đợt bột phát cấp.',
                         'Ban đỏ nốt ở cẳng chân hồng ban nút có đau nhức khớp chi dưới.',
                         'Hồng ban nút ban đỏ nốt ở cẳng chân thể điển hình.',
                         'Nghi ngờ ban đỏ nốt ở cẳng chân hồng ban nút cần tầm soát căn nguyên.'],
  'bien_the_ke_hoach': ['Hướng dẫn nghỉ ngơi kê cao chân, xét nghiệm công thức máu, tốc độ lắng '
                        'máu ESR, ASLO, chụp X-quang phổi tìm hạch rốn phổi, dùng NSAID giảm đau '
                        'chống viêm.',
                        'Chỉ định nghỉ ngơi tại giường tuyệt đối kê chân cao hơn tim, xét nghiệm '
                        'định lượng ASLO và CRP, kê đơn naproxen giảm đau viêm.',
                        'Làm bilan tìm nguyên nhân gồm Mantoux, X-quang ngực thẳng, cấy quệt họng, '
                        'dùng thuốc kháng viêm ibuprofen kết hợp băng ép nhẹ.',
                        'Kê đơn thuốc chống viêm không steroid NSAID kiểm soát triệu chứng sưng '
                        'đau, hướng dẫn chườm mát và hạn chế đi lại vận động mạnh.',
                        'Tầm soát bệnh sarcoidosis và lao qua X-quang phổi, dùng kali iodid dung '
                        'dịch bão hòa hoặc NSAID theo dõi đáp ứng lâm sàng.',
                        'Nghỉ ngơi tại chỗ, xét nghiệm chức năng gan thận tốc độ máu lắng, dùng '
                        'paracetamol kết hợp kháng viêm giảm đau trong 2 tuần.'],
  'bien_the_kham': ['Các nốt u dưới da kích thước 2-4cm ở cẳng chân hai bên, ấn đau rõ rệt, sưng '
                    'đỏ nóng, không có dấu hiệu dao động mủ.',
                    'Khám thấy 4-6 cục viêm dưới da đối xứng mặt trước xương chày, da phía trên đỏ '
                    'sẫm nóng rực, ấn rất đau, không có ổ mủ.',
                    'Nhiều cục nổi dưới da sưng đỏ kích thước quả táo nhỏ ở cẳng chân, bề mặt nhẵn '
                    'gờ nhẹ, màu đỏ tím như vết tụ máu bầm.',
                    'Tổn thương dạng hồng ban nút cứng chắc ấn đau chói dọc hai cẳng chân, sưng nề '
                    'nhẹ bàn chân, khớp cổ chân đau hạn chế đi lại.',
                    'Ghi nhận các khối viêm hạ bì tròn bầu dục mặt trước cẳng chân, sưng nóng đỏ '
                    'đau điển hình, không có hoại tử hay loét vỡ.',
                    'Nhiều nốt sưng đỏ ấn đau sâu dưới da chi dưới, ranh giới nốt không rõ, một số '
                    'nốt cũ ngả màu vàng úa như vết bầm máu.'],
  'chan_doan': 'Ban đỏ nốt ở cẳng chân hồng ban nút cấp tính.',
  'chinh': ['xuất hiện các cục viêm dưới da sưng đỏ nóng ấn đau chói tại mặt trước hai cẳng chân',
            'tổn thương cứng chắc gờ nhẹ nhô lên khỏi mặt da không bao giờ bị loét vỡ mủ',
            'màu sắc các cục chuyển đổi từ đỏ tươi sang đỏ tía rồi vàng xanh như vết thâm tím tụ '
            'máu'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Hướng dẫn nghỉ ngơi kê cao chân, xét nghiệm công thức máu, tốc độ lắng máu ESR, '
              'ASLO, chụp X-quang phổi tìm hạch rốn phổi, dùng NSAID giảm đau chống viêm.',
  'kham': 'Các nốt u dưới da kích thước 2-4cm ở cẳng chân hai bên, ấn đau rõ rệt, sưng đỏ nóng, '
          'không có dấu hiệu dao động mủ.',
  'nhom': 'người lớn',
  'phu': ['sốt vừa đau nhức ê ẩm các khớp cổ chân và khớp gối hai bên',
          'cảm giác nặng nề tức nặng cẳng chân tăng lên rõ rệt khi đứng lâu',
          'tiền sử đau họng viêm đường hô hấp trên do liên cầu trước đó vài tuần'],
  'ten': 'ban đỏ nốt ở cẳng chân hồng ban nút'},
 {'bien_the_chan_doan': ['Viêm tuyến mồ hôi mủ hidradenitis suppurativa giai đoạn hai theo Hurley.',
                         'Viêm tuyến mồ hôi mủ hidradenitis suppurativa đợt viêm tấy bội nhiễm '
                         'cấp.',
                         'Bệnh viêm tuyến mồ hôi mủ hidradenitis suppurativa thể sẹo rò phức tạp.',
                         'Theo dõi viêm tuyến mồ hôi mủ hidradenitis suppurativa vùng nách hai '
                         'bên.',
                         'Viêm tuyến mồ hôi mủ hidradenitis suppurativa tái phát dai dẳng.',
                         'Nghi ngờ viêm tuyến mồ hôi mủ hidradenitis suppurativa giai đoạn ba theo '
                         'Hurley.'],
  'bien_the_ke_hoach': ['Chỉ định kháng sinh đường uống phối hợp rifampicin và clindamycin dài '
                        'ngày, rửa sát khuẩn tổn thương tại chỗ, hội chẩn phẫu thuật dẫn lưu.',
                        'Kê đơn phối hợp kháng sinh clindamycin 300mg và rifampicin 300mg ngày 2 '
                        'lần trong 10 tuần, rửa tổn thương bằng chlorhexidine 4%.',
                        'Cấy mủ làm kháng sinh đồ tìm vi khuẩn phối hợp, chích rạch giải áp các ổ '
                        'mủ căng đau tức, tư vấn giảm cân và mặc đồ rộng.',
                        'Chỉ định tiêm triamcinolone vào nốt viêm cấp giảm sưng đau nhanh, vệ sinh '
                        'hàng ngày bằng dung dịch sát khuẩn povidone iodine.',
                        'Hội chẩn Ngoại Da liễu xem xét phẫu thuật cắt bỏ toàn bộ vùng da rò sẹo '
                        'xơ mạn tính, dùng kháng sinh kiểm soát nhiễm trùng.',
                        'Tư vấn kiêng hút thuốc lá và tránh cạo lông nách gây kích ứng nang lông, '
                        'điều trị kháng sinh toàn thân theo phác đồ đa tuần.'],
  'bien_the_kham': ['Vùng nách hai bên có nhiều cục viêm sưng đỏ, đường rò chảy mủ hôi, sẹo xơ phì '
                    'đại dạng cầu bắc co kéo.',
                    'Nách phải có 3 ổ áp xe sâu ấn đau nhói, dịch mủ lẫn máu rỉ qua lỗ rò, nhiều '
                    'dải sẹo xơ co rút hạn chế giơ cao tay.',
                    'Khám vùng nách và bẹn thấy các cục u viêm mưng mủ mạn tính, các lỗ chân lông '
                    'đầu đôi chứa chất bã đen, sẹo bắc cầu.',
                    'Tổn thương da vùng nách hai bên dạng cục viêm mủ tái diễn, nhiều đường rò '
                    'thông nhau dưới da tiết dịch nhầy mủ.',
                    'Ghi nhận khối viêm sưng tấy đỏ rò mủ ở nếp gấp bẹn hai bên, sẹo phì đại gồ '
                    'ghề dạng mạng lưới xơ cứng co kéo.',
                    'Nhiều nốt viêm sâu và ổ mủ tái phát vùng nách, đau chói khi sờ nắn, các đường '
                    'rò xơ hóa liên kết thành chùm phức tạp.'],
  'chan_doan': 'Viêm tuyến mồ hôi mủ hidradenitis suppurativa giai đoạn hai theo Hurley.',
  'chinh': ['các cục nốt viêm sâu tái phát nhiều lần hóa mủ đau nhức nhối ở nách và bẹn',
            'hình thành các ổ áp xe thông nhau dưới da rỉ dịch mủ đặc hôi lẫn máu',
            'sẹo xơ gồ ghề dải co kéo và các lỗ rò đầu mở nhân mụn đôi đặc trưng'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định kháng sinh đường uống phối hợp rifampicin và clindamycin dài ngày, rửa sát '
              'khuẩn tổn thương tại chỗ, hội chẩn phẫu thuật dẫn lưu.',
  'kham': 'Vùng nách hai bên có nhiều cục viêm sưng đỏ, đường rò chảy mủ hôi, sẹo xơ phì đại dạng '
          'cầu bắc co kéo.',
  'nhom': 'người lớn',
  'phu': ['đau đớn dữ dội làm hạn chế vận động dạng cánh tay và đi lại',
          'mùi hôi khó chịu từ dịch mủ rò rỉ gây mặc cảm tâm lý nặng nề',
          'sốt nhẹ hoặc ớn lạnh trong các đợt ổ mủ sưng tấy cấp tính'],
  'ten': 'viêm tuyến mồ hôi mủ hidradenitis suppurativa'},
 {'bien_the_chan_doan': ['Rụng tóc từng mảng alopecia areata thể khu trú đơn ổ.',
                         'Bệnh rụng tóc từng mảng alopecia areata giai đoạn tiến triển.',
                         'Rụng tóc từng mảng alopecia areata thể đa ổ vùng da đầu.',
                         'Theo dõi rụng tóc từng mảng alopecia areata nghi cơ chế tự miễn.',
                         'Rụng tóc từng mảng alopecia areata có kèm rỗ móng tay.',
                         'Nghi ngờ rụng tóc từng mảng alopecia areata thể mảng tròn đơn độc.'],
  'bien_the_ke_hoach': ['Tiêm corticosteroid nội thương tổn triamcinolone acetonide tại rìa mảng '
                        'rụng, kết hợp dung dịch xịt minoxidil tại chỗ.',
                        'Chỉ định tiêm vi điểm triamcinolone 5mg/ml vào mảng rụng tóc mỗi 4-6 '
                        'tuần, hướng dẫn bôi dung dịch minoxidil 5% hai lần mỗi ngày.',
                        'Bôi kem clobetasol propionate nắp bịt buổi tối nếu người bệnh sợ tiêm, bổ '
                        'sung kẽm vi chất và biotin đường uống.',
                        'Tầm soát bệnh tự miễn đi kèm bằng xét nghiệm TSH hormon tuyến giáp và '
                        'kháng thể kháng nhân ANA, trấn an tâm lý phục hồi tóc.',
                        'Hướng dẫn theo dõi mật độ tóc mọc lại sau 8-12 tuần, bôi dung dịch kích '
                        'thích mọc tóc tại chỗ, tránh nhổ giật tóc.',
                        'Chỉ định liệu pháp bôi miễn dịch tiếp xúc hoặc tiêm corticoid tại chỗ, tư '
                        'vấn giải tỏa stress và chăm sóc nhẹ nhàng da đầu.'],
  'bien_the_kham': ['Mảng rụng tóc tròn đường kính 3cm vùng đỉnh chẩm, da nhẵn không teo không '
                    'sẹo, soi dermoscopy thấy sợi tóc dấu chấm than rìa tổn thương.',
                    'Ghi nhận mảng rụng tóc hình tròn 4cm vùng thái dương, bề mặt da đầu trơn láng '
                    'bình thường, nghiệm pháp kéo tóc dương tính ở bờ viền.',
                    'Khám thấy 2 mảng rụng tóc ranh giới sắc nét không sẹo ở vùng đỉnh đầu, sợi '
                    'tóc dấu chấm than điển hình trên dermoscopy.',
                    'Da đầu tại vùng rụng tóc mềm mại không viêm đỏ không tróc vảy, móng tay hai '
                    'bên có chấm rỗ kim li ti dạng đòn gánh.',
                    'Mảng rụng tóc đơn độc kích thước 3x3cm vùng chẩm, lỗ chân lông còn nguyên '
                    'vẹn, không có hiện tượng teo xơ hay sẹo hóa.',
                    'Soi da đầu thấy nhiều chấm đen chấm vàng và sợi tóc hình dấu chấm than ở rìa '
                    'mảng rụng, da nhẵn bóng không gàu.'],
  'chan_doan': 'Rụng tóc từng mảng alopecia areata thể khu trú đơn ổ.',
  'chinh': ['tóc rụng đột ngột tạo thành một hoặc nhiều mảng tròn hình bầu dục giới hạn rõ',
            'vùng da đầu tại mảng rụng tóc hoàn toàn nhẵn bóng không có sẹo không có vảy',
            'dấu hiệu sợi tóc dấu chấm than ngắn cụt to ở ngọn nhỏ ở gốc tại rìa mảng rụng'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Tiêm corticosteroid nội thương tổn triamcinolone acetonide tại rìa mảng rụng, kết '
              'hợp dung dịch xịt minoxidil tại chỗ.',
  'kham': 'Mảng rụng tóc tròn đường kính 3cm vùng đỉnh chẩm, da nhẵn không teo không sẹo, soi '
          'dermoscopy thấy sợi tóc dấu chấm than rìa tổn thương.',
  'nhom': 'cả hai',
  'phu': ['nghiệm pháp giật tóc dương tính nhẹ quanh rìa của mảng tổn thương đang tiến triển',
          'móng tay có các vết lõm chấm kim nhỏ li ti xếp thành hàng',
          'không có cảm giác ngứa ngáy hay đau rát tại vùng da đầu bị rụng tóc'],
  'ten': 'rụng tóc từng mảng alopecia areata'},
 {'bien_the_chan_doan': ['Rụng tóc nội tiết androgenic nam độ ba theo thang Hamilton-Norwood.',
                         'Rụng tóc nội tiết androgenic nam thể hói chữ M trán đỉnh.',
                         'Theo dõi rụng tóc nội tiết androgenic nam tiến triển mạn tính.',
                         'Rụng tóc nội tiết androgenic nam phân độ 4 theo Hamilton-Norwood.',
                         'Bệnh rụng tóc nội tiết androgenic nam có tăng tiết bã nhờn da đầu.',
                         'Nghi ngờ rụng tóc nội tiết androgenic nam giai đoạn hoạt tính.'],
  'bien_the_ke_hoach': ['Kê đơn viên uống finasteride 1mg hàng ngày ức chế enzym 5-alpha '
                        'reductase, kết hợp xịt dung dịch minoxidil 5% vào da đầu.',
                        'Tư vấn uống finasteride 1mg mỗi ngày liên tục tối thiểu 6-12 tháng, kết '
                        'hợp xịt minoxidil 5% 1ml hai lần mỗi ngày vùng da thưa tóc.',
                        'Hướng dẫn gội đầu bằng dầu gội ketoconazole 2% giảm bã nhờn và ức chế '
                        'androgen tại chỗ, bôi minoxidil đều đặn hàng ngày.',
                        'Giải thích cơ chế tác dụng và tác dụng không mong muốn hiếm gặp của '
                        'finasteride, lập kế hoạch đánh giá mật độ tóc sau 6 tháng.',
                        'Kê đơn dung dịch xịt minoxidil 5% kích thích nang tóc, tư vấn lối sống '
                        'giảm stress và dinh dưỡng vi chất hỗ trợ tế bào mầm tóc.',
                        'Tư vấn các biện pháp can thiệp bổ trợ như lăn kim vi điểm phối hợp '
                        'minoxidil hoặc cấy tóc tự thân nếu hói ổn định lâu năm.'],
  'bien_the_kham': ['Đường viền trán thụt lùi tạo chữ M rõ rệt theo phân loại Hamilton-Norwood độ '
                    'ba, mật độ tóc vùng đỉnh thưa, da đầu nhờn.',
                    'Ghi nhận hói vùng trán hai bên sâu tạo chữ M điển hình, tóc vùng xoáy đỉnh '
                    'thưa thấy rõ da đầu, da đầu nhiều chất bã nhờn.',
                    'Khám thấy sợi tóc vùng trán đỉnh bị thu nhỏ kích thước teo mảnh không đồng '
                    'đều, mật độ tóc vùng chẩm gáy hoàn toàn bình thường.',
                    'Đường chân tóc trán lùi xa, hói trán đỉnh phối hợp theo phân loại Norwood độ '
                    '4, các sợi tóc tơ chiếm tỷ lệ cao trên dermoscopy.',
                    'Soi dermoscopy da đầu thấy hiện tượng teo kích thước nang tóc đa dạng, hơn '
                    '20% sợi tóc đường kính mảnh dưới 0.03mm.',
                    'Hói góc trán thái dương hai bên đối xứng rõ nét, tóc mỏng thưa vùng đỉnh đầu, '
                    'da đầu nhờn dính nhiều gàu nhỏ.'],
  'chan_doan': 'Rụng tóc nội tiết androgenic nam độ ba theo thang Hamilton-Norwood.',
  'chinh': ['tóc rụng thưa dần đều đặn tiến triển chậm tại vùng trán thái dương tạo hình chữ M',
            'đường chân tóc vùng trán lùi sâu dần về phía sau để lộ rõ góc trán hói',
            'sợi tóc mới mọc ngày càng teo nhỏ mảnh ngắn nhạt màu dần biến thành lông tơ'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Kê đơn viên uống finasteride 1mg hàng ngày ức chế enzym 5-alpha reductase, kết hợp '
              'xịt dung dịch minoxidil 5% vào da đầu.',
  'kham': 'Đường viền trán thụt lùi tạo chữ M rõ rệt theo phân loại Hamilton-Norwood độ ba, mật độ '
          'tóc vùng đỉnh thưa, da đầu nhờn.',
  'nhom': 'người lớn',
  'phu': ['da đầu tăng tiết bã nhờn bóng dầu và có vảy gàu mịn kèm theo',
          'vùng tóc phía sau gáy và hai bên tai vẫn giữ nguyên mật độ dày bình thường',
          'tiền sử gia đình có bố hoặc anh em trai ruột bị hói đầu sớm'],
  'ten': 'rụng tóc nội tiết androgenic nam'},
 {'bien_the_chan_doan': ['Rụng tóc telogen cấp tính sau biến cố stress thể chất.',
                         'Rụng tóc telogen cấp tính sau sốt xuất huyết nặng.',
                         'Theo dõi rụng tóc telogen sau sinh đẻ hoặc biến cố nhiễm trùng.',
                         'Rụng tóc telogen thể rụng lan tỏa toàn bộ da đầu.',
                         'Hội chứng rụng tóc telogen cấp tính hồi phục.',
                         'Nghi ngờ rụng tóc telogen do thiếu hụt vi chất dinh dưỡng sau biến cố.'],
  'bien_the_ke_hoach': ['Trấn an người bệnh về khả năng hồi phục tự nhiên sau 3-6 tháng, bổ sung '
                        'kẽm vi chất sắt và biotin đường uống, tránh kéo giật tóc.',
                        'Giải thích cặn kẽ chu kỳ sinh lý của sợi tóc để giảm lo âu, làm xét '
                        'nghiệm sắt huyết thanh ferritin và chức năng giáp TSH.',
                        'Kê đơn viên uống bổ sung phức hợp vitamin B, biotin, kẽm và acid amin '
                        'cystine hỗ trợ mọc tóc, hướng dẫn chải tóc bằng lược răng thưa.',
                        'Tư vấn chế độ dinh dưỡng giàu đạm protein động thực vật, tránh các tác '
                        'động hóa chất uốn nhuộm tẩy tóc trong giai đoạn này.',
                        'Trấn an người bệnh tóc sẽ tự mọc lại đầy đủ sau khi cân bằng nội môi, có '
                        'thể dùng dung dịch dưỡng da đầu dịu nhẹ dạng xịt.',
                        'Làm công thức máu toàn phần kiểm tra thiếu máu, kê đơn thuốc bổ sung sắt '
                        'nếu ferritin thấp, hẹn tái khám đánh giá lại sau 3 tháng.'],
  'bien_the_kham': ['Mật độ tóc giảm đồng đều toàn bộ da đầu, nghiệm pháp kéo tóc rút ra nhiều sợi '
                    'tóc pha nghỉ có bầu trắng ở chân, da đầu bình thường.',
                    'Khám thấy tóc thưa lan tỏa toàn thể da đầu không có mảng hói khu trú, nghiệm '
                    'pháp kéo tóc rút được trên 10 sợi tóc chân có củ trắng.',
                    'Da đầu hoàn toàn khỏe mạnh không viêm không có vảy sừng, tóc rụng nhiều khi '
                    'vuốt nhẹ ở mọi vị trí đỉnh trán chẩm.',
                    'Mật độ tóc giảm khoảng 30% trên toàn bộ vòm sọ, nang tóc còn nguyên vẹn, soi '
                    'chân tóc thấy 100% sợi tóc ở pha telogen.',
                    'Ghi nhận tình trạng rụng tóc cấp tính lan tỏa toàn bộ da đầu, không có sợi '
                    'tóc đứt gãy, da đầu mềm mại bình thường.',
                    'Nghiệm pháp giật tóc dương tính mạnh toàn thể da đầu, các sợi tóc rụng đều có '
                    'củ sừng trắng hình chùy ở gốc chân tóc.'],
  'chan_doan': 'Rụng tóc telogen cấp tính sau biến cố stress thể chất.',
  'chinh': ['tóc rụng lan tỏa đồng đều trên toàn bộ da đầu diễn ra đột ngột và ồ ạt',
            'lượng tóc rụng tăng vọt khi gội đầu chải tóc hoặc vuốt nhẹ qua kẽ tay',
            'khởi phát rụng tóc xảy ra sau một đợt sốt cao kéo dài hoặc stress lớn hai đến ba '
            'tháng'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Trấn an người bệnh về khả năng hồi phục tự nhiên sau 3-6 tháng, bổ sung kẽm vi chất '
              'sắt và biotin đường uống, tránh kéo giật tóc.',
  'kham': 'Mật độ tóc giảm đồng đều toàn bộ da đầu, nghiệm pháp kéo tóc rút ra nhiều sợi tóc pha '
          'nghỉ có bầu trắng ở chân, da đầu bình thường.',
  'nhom': 'người lớn',
  'phu': ['chân sợi tóc rụng có bầu màu trắng tròn nhỏ đặc trưng của pha nghỉ telogen',
          'không thấy mảng da đầu nào bị hói hoàn toàn và không có sẹo teo da',
          'lo lắng bất an sợ bị hói vĩnh viễn do tóc rụng vương vãi khắp gối nằm'],
  'ten': 'rụng tóc telogen sau sinh đẻ hoặc sốt nặng'},
 {'bien_the_chan_doan': ['Viêm kẽ ngón tay do nấm Candida albicans.',
                         'Nhiễm nấm Candida kẽ ngón tay mạn tính thể trợt đỏ.',
                         'Viêm kẽ ngón tay do nấm Candida thể trợt nứt kẽ đau xót.',
                         'Theo dõi viêm kẽ ngón tay do nấm Candida ở người làm việc môi trường ẩm '
                         'ướt.',
                         'Bệnh nấm Candida kẽ ngón tay có tổn thương mụn mủ vệ tinh.',
                         'Nghi ngờ viêm kẽ ngón tay do nấm Candida tái phát.'],
  'bien_the_ke_hoach': ['Soi tươi tìm bào tử nấm men và giả sợi, hướng dẫn giữ bàn tay khô ráo '
                        'mang găng tay bảo hộ, bôi kem chống nấm clotrimazole hoặc miconazole.',
                        'Chỉ định cạo vảy bờ tổn thương soi tươi KOH tìm nấm men hạt men nảy chồi, '
                        'bôi kem ketoconazole 2% ngày 2 lần trong 3 tuần.',
                        'Hướng dẫn giữ bàn tay luôn khô thoáng, đeo găng tay cao su có lót vải '
                        'cotton bên trong khi làm việc ướt, bôi kem miconazole.',
                        'Kê đơn thuốc chống nấm tại chỗ terbinafine bôi đều đặn, chấm dung dịch '
                        'cồn castellani làm khô vết nứt kẽ trợt ướt.',
                        'Tư vấn thay đổi thói quen sinh hoạt tránh để kẽ tay ẩm ướt kéo dài, lau '
                        'khô tay sau rửa, bôi kem chống nấm phổ rộng.',
                        'Chỉ định thuốc bôi kết hợp kháng nấm và kháng khuẩn nhẹ chống bội nhiễm, '
                        'xét nghiệm đường huyết mao mạch loại trừ tiểu đường.'],
  'bien_the_kham': ['Kẽ ngón 3-4 bàn tay phải trợt đỏ tươi, viền biểu bì trắng mủn mỏng, nứt kẽ '
                    'sâu đau rát, có vài sẩn mủ vệ tinh nhỏ.',
                    'Tổn thương trợt đỏ rỉ dịch kẽ ngón 3 và 4 bàn tay, viền vảy da ẩm mủn trắng '
                    'bờ gờ nhẹ, vết nứt kẽ gây đau xót khi xòe ngón.',
                    'Khám thấy đáy kẽ ngón tay đỏ tươi bóng lộn, biểu bì chung quanh ngâm nước mủn '
                    'trắng, có 2 sẩn mủ nhỏ li ti ở rìa ngoài.',
                    'Vùng da giữa ngón nhẫn và ngón giữa hai bàn tay viêm trợt đỏ ướt, bờ viền có '
                    'dải sừng trắng bong mép, mùi men chua ẩm.',
                    'Ghi nhận mảng da trợt loét nông hình bầu dục ở kẽ ngón tay ba bốn, nứt kẽ đau '
                    'rát, không có mụn nước sâu dạng tổ đỉa.',
                    'Đáy kẽ ngón tay đỏ ửng rỉ dịch huyết thanh nhẹ, lớp biểu bì quanh rìa mủn nát '
                    'như ngâm vôi, ấn đau rát buốt.'],
  'chan_doan': 'Viêm kẽ ngón tay do nấm Candida albicans.',
  'chinh': ['vùng da kẽ ngón tay ba và bốn bị trợt đỏ ướt viền bờ bong vảy trắng mủn',
            'đáy tổn thương trợt bóng màu đỏ tươi có vết nứt nẻ sâu gây đau xót rát buốt',
            'ngứa ngáy râm ran liên tục và tăng lên khi tay ngâm tiếp xúc với nước'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Soi tươi tìm bào tử nấm men và giả sợi, hướng dẫn giữ bàn tay khô ráo mang găng tay '
              'bảo hộ, bôi kem chống nấm clotrimazole hoặc miconazole.',
  'kham': 'Kẽ ngón 3-4 bàn tay phải trợt đỏ tươi, viền biểu bì trắng mủn mỏng, nứt kẽ sâu đau rát, '
          'có vài sẩn mủ vệ tinh nhỏ.',
  'nhom': 'người lớn',
  'phu': ['công việc hàng ngày thường xuyên phải rửa dọn ướt tay hoặc tiếp xúc xà phòng',
          'mùi chua ẩm đặc trưng toát ra từ vùng kẽ ngón tay bị trợt ẩm',
          'các sẩn mụn mủ nhỏ li ti vệ tinh xuất hiện xung quanh bờ tổn thương'],
  'ten': 'viêm kẽ ngón tay do nấm Candida'},
 {'bien_the_chan_doan': ['Lang ben lan tỏa do nấm men Malassezia furfur.',
                         'Bệnh lang ben lan tỏa thể giảm sắc tố ở thân mình.',
                         'Lang ben lan tỏa thể đa sắc tố mạn tính tái phát.',
                         'Theo dõi lang ben lan tỏa do vi nấm Malassezia diện rộng.',
                         'Lang ben lan tỏa có dấu hiệu cạo vỏ bào Besnier dương tính.',
                         'Nghi ngờ lang ben lan tỏa phân biệt với bệnh phong hoặc bạch biến.'],
  'bien_the_ke_hoach': ['Soi đèn Wood thấy huỳnh quang màu vàng sáng, dùng dầu tắm gội '
                        'ketoconazole 2% toàn thân kết hợp bôi kem terbinafine.',
                        'Chỉ định cạo vảy da soi trực tiếp KOH thấy sợi nấm ngắn và cụm bào tử '
                        'hình thịt viên mì ống, dùng dầu gội ketoconazole tạo bọt toàn thân.',
                        'Kê đơn thuốc chống nấm đường uống itraconazole 200mg/ngày trong 7 ngày '
                        'cho thể lan tỏa diện rộng, kết hợp kem bôi ngoài da.',
                        'Hướng dẫn giặt luộc quần áo phơi nắng to diệt bào tử nấm, dùng sữa tắm '
                        'chứa selenium sulfide 2.5% tắm 2 lần mỗi tuần.',
                        'Tư vấn giải thích tình trạng dát trắng cần vài tháng tiếp xúc ánh nắng '
                        'mới đều màu da trở lại dù vi nấm đã bị tiêu diệt.',
                        'Kê đơn kem bôi clotrimazole kết hợp dầu tắm chống nấm, dặn dò giữ cơ thể '
                        'khô thoáng tránh mặc quần áo ẩm ướt mồ hôi.'],
  'bien_the_kham': ['Nhiều dát giảm sắc tố ranh giới rõ phủ vảy cám mịn ở ngực và lưng, cạo vảy '
                    'bong mịn dấu hiệu Besnier dương tính.',
                    'Khám thấy các dát trắng và dát nâu xen kẽ loang lổ vùng lưng ngực, bề mặt phủ '
                    'lớp vảy mịn mỏng cạo tróc như phoi bào.',
                    'Tổn thương da dạng dát giảm sắc tố hình tròn bầu dục liên kết thành mảng lớn '
                    'ở thân mình, cạo vảy dấu hiệu vỏ bào dương tính.',
                    'Nhiều dát tăng giảm sắc tố không đều màu ở cổ ngực và mặt trong cánh tay, bờ '
                    'viền sắc nét, không teo da không mất cảm giác.',
                    'Ghi nhận mảng da loang lổ màu trắng sữa xen lẫn màu nâu nhạt vùng lưng trên, '
                    'soi đèn Wood phát huỳnh quang màu vàng cam mờ.',
                    'Da vùng ngực bụng có hàng chục dát giảm sắc tố phủ vảy cám nhỏ li ti, nghiệm '
                    'pháp cạo Besnier bong vảy cám mịn rõ rệt.'],
  'chan_doan': 'Lang ben lan tỏa do nấm men Malassezia furfur.',
  'chinh': ['nhiều dát giảm sắc tố màu trắng hoặc tăng sắc tố màu nâu cà phê rải rác',
            'bề mặt các dát phủ lớp vảy da mịn như cám cạo nhẹ có dấu hiệu vỏ bào dương tính',
            'tổn thương liên kết thành từng mảng lớn loang lổ ở vùng ngực lưng cổ và cánh tay'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Soi đèn Wood thấy huỳnh quang màu vàng sáng, dùng dầu tắm gội ketoconazole 2% toàn '
              'thân kết hợp bôi kem terbinafine.',
  'kham': 'Nhiều dát giảm sắc tố ranh giới rõ phủ vảy cám mịn ở ngực và lưng, cạo vảy bong mịn dấu '
          'hiệu Besnier dương tính.',
  'nhom': 'cả hai',
  'phu': ['cảm giác châm chích ngứa ngáy nhẹ khi cơ thể đổ nhiều mồ hôi hoặc đi nắng',
          'mùi mồ hôi chua nồng đặc trưng vào những ngày thời tiết oi bức',
          'vết loang lổ làm mất thẩm mỹ gây tự ti khi mặc áo hở cổ hoặc ngắn tay'],
  'ten': 'lang ben lan tỏa do Malassezia'},
 {'bien_the_chan_doan': ['Mụn cóc phẳng mu bàn tay do virus HPV thể sẩn dẹt.',
                         'Mụn cóc phẳng mu bàn tay do HPV thể sẩn phẳng đa phát.',
                         'Bệnh hạt cơm phẳng mụn cóc phẳng mu bàn tay do virus.',
                         'Theo dõi mụn cóc phẳng mu bàn tay có dấu hiệu Koebner dương tính.',
                         'Mụn cóc phẳng mu bàn tay mạn tính do nhiễm HPV týp 3 hoặc 10.',
                         'Nghi ngờ mụn cóc phẳng mu bàn tay thể sẩn màu da lành tính.'],
  'bien_the_ke_hoach': ['Chỉ định chấm dung dịch axit salicylic phối hợp lactic hoặc bôi kem '
                        'imiquimod kích thích miễn dịch tại chỗ, tránh cạy gãi làm lây lan.',
                        'Kê đơn kem bôi tretinoin 0.05% bôi mỏng buổi tối làm bong sừng nhẹ, tư '
                        'vấn không dùng kim chọc hoặc cạo nặn nốt sẩn.',
                        'Chỉ định bôi kem imiquimod 5% ba lần mỗi tuần kích hoạt đáp ứng miễn dịch '
                        'đào thải virus tại chỗ, theo dõi sau 4 tuần.',
                        'Cân nhắc áp lạnh nitơ lỏng nhẹ từng nốt sẩn phẳng nếu điều trị thuốc bôi '
                        'đáp ứng chậm, bảo vệ da tránh để lại thâm sẹo.',
                        'Hướng dẫn rửa tay sạch sẽ, bôi dung dịch axit salicylic nồng độ thấp tại '
                        'chỗ, dặn người bệnh kiên trì điều trị nhiều tuần.',
                        'Tư vấn hạn chế tiếp xúc trực tiếp cào gãi tránh gieo rắc virus sang vùng '
                        'da mặt và cơ thể, bôi thuốc điều biến miễn dịch tại chỗ.'],
  'bien_the_kham': ['Hàng chục sẩn dẹt kích thước 2-4mm màu vàng nhạt, bề mặt phẳng nhẵn, phân bố '
                    'thành vệt Koebner ở mu bàn tay hai bên.',
                    'Nhiều sẩn nhỏ đỉnh phẳng màu da hoặc nâu vàng rải rác mu bàn tay, bề mặt trơn '
                    'láng gờ nhẹ 1mm so với mặt da lành.',
                    'Khám thấy các tổn thương sẩn phẳng xếp thành hàng dọc theo vết trầy xước cũ ở '
                    'cổ tay mu tay, không có cuống không loét.',
                    'Tổn thương sẩn dẹt tròn hoặc đa giác nhỏ li ti tập trung thành đám ở mu bàn '
                    'tay, sờ hơi gợn tay, không đau khi ấn.',
                    'Ghi nhận hàng chục sẩn sừng dẹt màu vàng nâu nhạt ở mu hai bàn tay, hiện '
                    'tượng Koebner xuất hiện rõ rệt sau cào gãi.',
                    'Mu bàn tay có nhiều sẩn phẳng nhẵn bóng ranh giới rõ ràng, kích thước đều đặn '
                    '2-3mm, không có chấm xuất huyết đen như hạt cơm thường.'],
  'chan_doan': 'Mụn cóc phẳng mu bàn tay do virus HPV thể sẩn dẹt.',
  'chinh': ['các sẩn nhỏ phẳng dẹt hơi gờ nhẹ bề mặt nhẵn bóng màu da hoặc vàng nâu nhạt',
            'số lượng sẩn nhiều tập trung thành đám hoặc rải rác trên mu bàn tay và cẳng tay',
            'hiện tượng Koebner các nốt sẩn mọc thành hàng thẳng dọc theo vết xước cào gãi'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định chấm dung dịch axit salicylic phối hợp lactic hoặc bôi kem imiquimod kích '
              'thích miễn dịch tại chỗ, tránh cạy gãi làm lây lan.',
  'kham': 'Hàng chục sẩn dẹt kích thước 2-4mm màu vàng nhạt, bề mặt phẳng nhẵn, phân bố thành vệt '
          'Koebner ở mu bàn tay hai bên.',
  'nhom': 'cả hai',
  'phu': ['hoàn toàn không đau không ngứa hoặc chỉ ngứa thoáng qua rất nhẹ',
          'tổn thương lan rộng dần về số lượng sau các hành vi cạy nặn hoặc gãi cào',
          'cảm giác sần sùi cộm tay khi xoa vuốt lên bề mặt mu bàn tay'],
  'ten': 'mụn cóc phẳng mu bàn tay do HPV'},
 {'bien_the_chan_doan': ['U mềm lây Molluscum contagiosum do Poxvirus.',
                         'Bệnh u mềm lây Molluscum contagiosum thể sẩn bán cầu có rốn.',
                         'Theo dõi u mềm lây Molluscum contagiosum rải rác thân mình.',
                         'U mềm lây Molluscum contagiosum đợt lây nhiễm cấp tính.',
                         'U mềm lây Molluscum contagiosum thể đa nốt chưa bội nhiễm.',
                         'Nghi ngờ u mềm lây Molluscum contagiosum do virus đậu mùa lây truyền.'],
  'bien_the_ke_hoach': ['Thực hiện thủ thuật nạo nốt u mềm lây bằng thìa nạo vô khuẩn hoặc áp nitơ '
                        'lỏng, sát khuẩn bằng dung dịch povidone iodine.',
                        'Chỉ định bôi tê tại chỗ bằng kem EMLA 5% rồi dùng thìa curette nạo sạch '
                        'nhân u mềm lây, chấm cồn iod sát trùng.',
                        'Chấm dung dịch KOH 10% hoặc axit trichloroacetic TCA tại chỗ nốt sẩn, '
                        'hướng dẫn không dùng chung khăn tắm quần áo.',
                        'Thực hiện áp lạnh bằng tăm bông nhúng nitơ lỏng trong 5-10 giây mỗi nốt '
                        'u, giữ vùng da sạch sẽ khô ráo sau thủ thuật.',
                        'Tư vấn người bệnh không cào gãi nặn bóp tại nhà tránh lây lan rộng, bôi '
                        'kem kháng khuẩn tại chỗ sau khi nạo nhân.',
                        'Giải thích tính chất lây nhiễm cơ học của bệnh, hướng dẫn phòng ngừa lây '
                        'chéo cho người xung quanh, tái khám sau 2 tuần.'],
  'bien_the_kham': ['Nhiều nốt sẩn hình bán cầu có rốn lõm trung tâm chứa chất sáp trắng, đường '
                    'kính 2-5mm, không sưng đỏ xung quanh.',
                    'Khám thấy 8-12 nốt sẩn bán cầu màu ngọc trai nhẵn bóng ở nách và mạn sườn, '
                    'trung tâm có vết lõm dạng rốn điển hình.',
                    'Các nốt u nhỏ gờ cao trên da hình bán cầu đỉnh lõm rốn, bóp nhẹ thấy nhân '
                    'trắng như hạt bã đậu phòi ra ngoài.',
                    'Tổn thương dạng sẩn chắc màu hồng bóng có rốn lõm trung tâm rải rác ở thân '
                    'mình, không có quầng viêm đỏ bao quanh.',
                    'Ghi nhận tổn thương u mềm lây điển hình đường kính 3mm, bề mặt nhẵn bóng như '
                    'hạt ngọc trai, ranh giới sắc nét.',
                    'Nhiều sẩn sáp bán cầu có rốn lõm ở bụng và nách, không đau khi sờ nắn, một số '
                    'nốt cũ có phản ứng đỏ nhẹ tự thoái triển.'],
  'chan_doan': 'U mềm lây Molluscum contagiosum do Poxvirus.',
  'chinh': ['các nốt sẩn chắc hình bán cầu tròn nhẵn bóng màu hồng nhạt hoặc màu ngọc trai',
            'ở trung tâm của mỗi nốt sẩn có điểm rốn lõm xuống đặc trưng',
            'khi dùng kẹp nặn sẽ bật ra chất nhân màu trắng đục như hạt bã đậu sáp'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Thực hiện thủ thuật nạo nốt u mềm lây bằng thìa nạo vô khuẩn hoặc áp nitơ lỏng, sát '
              'khuẩn bằng dung dịch povidone iodine.',
  'kham': 'Nhiều nốt sẩn hình bán cầu có rốn lõm trung tâm chứa chất sáp trắng, đường kính 2-5mm, '
          'không sưng đỏ xung quanh.',
  'nhom': 'cả hai',
  'phu': ['không có cảm giác đau hay ngứa trừ khi có hiện tượng bội nhiễm vi khuẩn',
          'các nốt mọc rải rác hoặc thành cụm tại thân mình nách nếp gấp hoặc vùng da mỏng',
          'vùng da xung quanh có thể hơi ửng đỏ nhẹ trong phản ứng miễn dịch tự nhiên'],
  'ten': 'u mềm lây Molluscum contagiosum'},
 {'bien_the_chan_doan': ['Dày sừng quang hóa tiền ung thư da vùng mặt.',
                         'Dày sừng quang hóa tiền ung thư da thể sừng hóa thô ráp.',
                         'Bệnh dày sừng quang hóa tiền ung thư da do ánh nắng mạn tính.',
                         'Theo dõi dày sừng quang hóa tiền ung thư da nghi chuyển biến ác tính.',
                         'Dày sừng quang hóa tiền ung thư da đa ổ vùng đầu mặt.',
                         'Nghi ngờ dày sừng quang hóa tiền ung thư da phân biệt với ung thư tế bào '
                         'gai.'],
  'bien_the_ke_hoach': ['Chỉ định sinh thiết da loại trừ ung thư biểu mô vảy xâm lấn, điều trị '
                        'bằng áp lạnh nitơ lỏng hoặc bôi kem 5-fluorouracil tại chỗ.',
                        'Thực hiện áp lạnh nitơ lỏng chu kỳ đông rã 15 giây phá hủy tổn thương '
                        'tiền ung thư, bôi kem chống nắng SPF trên 50 hàng ngày.',
                        'Kê đơn kem 5-fluorouracil 5% bôi ngày 2 lần trong 3-4 tuần kích thích '
                        'hoại tử chọn lọc tế bào sừng bất thường, theo dõi phản ứng viêm.',
                        'Chỉ định sinh thiết trọn tổn thương gửi giải phẫu bệnh nếu nền thâm nhiễm '
                        'dày cứng, hướng dẫn đội mũ rộng vành khi ra nắng.',
                        'Kê đơn kem imiquimod 5% bôi 3 lần mỗi tuần kích hoạt miễn dịch tiêu diệt '
                        'tổn thương dày sừng quang hóa, tái khám sau 8 tuần.',
                        'Tư vấn các biện pháp bảo vệ chống tia cực tím UV nghiêm ngặt, bôi kem '
                        'dưỡng ẩm phục hồi biểu mô sau các liệu trình thủ thuật.'],
  'bien_the_kham': ['Mảng sần sùi đóng vảy khô ráp đường kính 8mm vùng gò má, cạy vảy đáy đỏ rớm '
                    'máu, nền da xung quanh có nhiều vết sần lão hóa.',
                    'Tổn thương thô ráp như giấy ráp kích thước 1cm vùng thái dương, vảy sừng bám '
                    'chặt khó bong, nền da có giãn mạch hình mạng nhện.',
                    'Khám thấy mảng sừng màu vàng nâu gồ nhẹ trên nền hồng ban ở sống mũi, sờ thô '
                    'cứng ráp tay, ấn đau nhói nhẹ.',
                    'Nhiều tổn thương dày sừng quang hóa rải rác trán và mu bàn tay, vảy khô dính '
                    'chặt, không thâm nhiễm cứng sâu xuống mô dưới.',
                    'Ghi nhận mảng sần đóng vảy sừng dày vùng gò má phải, đáy tổn thương đỏ rực '
                    'khi bóc vảy, nền da lão hóa do ánh sáng rõ.',
                    'Tổn thương sừng hóa thô ráp vùng đỉnh đầu hói, đường kính 7-10mm, bề mặt gồ '
                    'ghề không đều, bờ viền không thâm nhiễm hạt chai.'],
  'chan_doan': 'Dày sừng quang hóa tiền ung thư da vùng mặt.',
  'chinh': ['mảng sần sùi thô ráp màu đỏ hồng hoặc nâu nhạt như giấy ráp chà xát',
            'vảy da khô bám chặt cạy ra gây rớm máu hoặc cảm giác đau buốt nhói',
            'vị trí xuất hiện tập trung ở vùng da tiếp xúc nhiều với ánh nắng như mặt trán mu tay'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định sinh thiết da loại trừ ung thư biểu mô vảy xâm lấn, điều trị bằng áp lạnh '
              'nitơ lỏng hoặc bôi kem 5-fluorouracil tại chỗ.',
  'kham': 'Mảng sần sùi đóng vảy khô ráp đường kính 8mm vùng gò má, cạy vảy đáy đỏ rớm máu, nền da '
          'xung quanh có nhiều vết sần lão hóa.',
  'nhom': 'người lớn',
  'phu': ['cảm giác châm chích ngứa rát nhẹ thoáng qua khi đi ra ngoài trời nắng',
          'tiền sử làm việc ngoài trời nhiều năm hoặc tiếp xúc ánh nắng cường độ mạnh',
          'nền da xung quanh có dấu hiệu thoái hóa do nắng như giãn mạch da sần sùi'],
  'ten': 'dày sừng quang hóa tiền ung thư da'},
 {'bien_the_chan_doan': ['Dày sừng tiết bã tuổi già thể sần bã lành tính.',
                         'Bệnh dày sừng tiết bã tuổi già thể sừng sáp đa nốt thân mình.',
                         'Dày sừng tiết bã tuổi già có tăng sắc tố đen sẫm phân biệt với u hắc tố.',
                         'Theo dõi dày sừng tiết bã tuổi già có viêm kích ứng do cọ xát.',
                         'Dày sừng tiết bã tuổi già thể sùi bã nhờn lành tính.',
                         'Nghi ngờ dày sừng tiết bã tuổi già vùng mặt ảnh hưởng thẩm mỹ.'],
  'bien_the_ke_hoach': ['Giải thích tính chất lành tính không chuyển biến ác tính, loại bỏ bằng '
                        'đốt điện plasma hoặc nạo bằng thìa nếu ảnh hưởng thẩm mỹ.',
                        'Trấn an người bệnh về độ lành tính tuyệt đối của nốt dày sừng bã, xử trí '
                        'đốt laser CO2 hoặc áp nitơ lỏng nếu có nhu cầu thẩm mỹ.',
                        'Chỉ định sinh thiết nếu nốt sẫm màu biến đổi nhanh màu sắc hoặc chảy máu '
                        'loại trừ melanoma, chăm sóc vệ sinh da thường quy.',
                        'Thực hiện thủ thuật nạo bằng thìa curette vô khuẩn sau khi gây tê tại '
                        'chỗ, bôi dung dịch sát khuẩn povidone iodine khô lành sẹo.',
                        'Tư vấn người bệnh tránh cạy nặn làm xây xước chảy máu bội nhiễm, bôi kem '
                        'dưỡng dịu da và theo dõi kích thước các nốt định kỳ.',
                        'Hướng dẫn theo dõi tại nhà, giải thích bệnh liên quan quá trình lão hóa '
                        'tự nhiên của da, can thiệp plasma loại bỏ nốt to cộm.'],
  'bien_the_kham': ['Nhiều mảng màu nâu sẫm dán dính trên bề mặt da lưng ngực, bề mặt sần sùi như '
                    'gắn sáp, ranh giới rõ rệt, không thâm nhiễm đáy.',
                    'Tổn thương sẩn sáp màu nâu đen gồ cao dạng gắn dính trên da mặt và thái '
                    'dương, bờ nham nhở như sáp ong nứt nẻ.',
                    'Khám thấy mảng sừng bã nhờn đường kính 1.5cm ở vùng lưng, bề mặt có các nút '
                    'sừng nang lông nhỏ, đáy phẳng di động tự do.',
                    'Nhiều tổn thương dày sừng tiết bã màu nâu nhạt đến xám đen rải rác thân mình, '
                    'sờ nhờn trơn bóng, không có hạch vùng to.',
                    'Ghi nhận nốt sẩn tăng sắc tố dạng dán sáp ở vùng ngực, soi dermoscopy thấy '
                    'các nang giả sừng và khe nứt dạng não đặc trưng.',
                    'Mảng dày sừng tiết bã bề mặt thô ráp như hạt kê màu nâu xỉn ở cổ và mặt, ấn '
                    'không đau, ranh giới với da lành rất rõ nét.'],
  'chan_doan': 'Dày sừng tiết bã tuổi già thể sần bã lành tính.',
  'chinh': ['các nốt sẩn hoặc mảng da màu nâu nhạt đến đen sẫm có bề mặt sần sùi dầu nhờn',
            'tổn thương trông như được dán đè dính lên mặt da có thể dùng móng cạy nhẹ',
            'bề mặt nứt nẻ có các lỗ nhỏ chứa chất sừng bã đặc trưng như nhét sáp'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Giải thích tính chất lành tính không chuyển biến ác tính, loại bỏ bằng đốt điện '
              'plasma hoặc nạo bằng thìa nếu ảnh hưởng thẩm mỹ.',
  'kham': 'Nhiều mảng màu nâu sẫm dán dính trên bề mặt da lưng ngực, bề mặt sần sùi như gắn sáp, '
          'ranh giới rõ rệt, không thâm nhiễm đáy.',
  'nhom': 'người lớn',
  'phu': ['hoàn toàn lành tính tiến triển chậm chạp qua nhiều năm tháng',
          'không có triệu chứng đau đớn hay chảy máu trừ khi bị cọ xát dây thắt lưng quần áo',
          'xuất hiện nhiều nốt rải rác trên ngực lưng mặt ở người cao tuổi'],
  'ten': 'dày sừng tiết bã tuổi già'},
 {'bien_the_chan_doan': ['Sẹo lồi phì đại sau can thiệp phẫu thuật lồng ngực.',
                         'Sẹo lồi phì đại sau chấn thương rách da vùng vai cánh tay.',
                         'Bệnh sẹo lồi phì đại giai đoạn tăng sinh hoạt tính gây đau ngứa.',
                         'Theo dõi sẹo lồi phì đại dái tai sau bấm khuyên thủng tai.',
                         'Sẹo lồi phì đại bờ chân càng cua xâm lấn mô lành.',
                         'Nghi ngờ sẹo lồi phì đại kháng trị sau can thiệp phẫu thuật.'],
  'bien_the_ke_hoach': ['Chỉ định tiêm nội tổn thương triamcinolone acetonide kết hợp '
                        '5-fluorouracil định kỳ, dán miếng gel silicone bảo vệ chống tăng sinh.',
                        'Tiêm triamcinolone acetonide 20mg/ml trực tiếp vào lòng khối sẹo mỗi '
                        'tháng một lần, hướng dẫn dán tấm silicone gel liên tục 12 giờ/ngày.',
                        'Phối hợp tiêm corticoid nội sẹo và áp lạnh nitơ lỏng làm mềm mô sẹo xơ '
                        'cứng, tư vấn kiêng các thực phẩm gây kích ứng cơ địa.',
                        'Chỉ định điều trị laser màu PDL làm giảm tưới máu nuôi sẹo kết hợp tiêm '
                        '5-FU, hướng dẫn băng ép nén tạo áp lực cơ học.',
                        'Lập kế hoạch tiêm thuốc ức chế tăng sinh collagen 3-4 đợt cách nhau 4 '
                        'tuần, theo dõi tác dụng phụ teo da và giãn mạch.',
                        'Tư vấn không tự ý phẫu thuật cắt bỏ sẹo đơn thuần tránh nguy cơ tái phát '
                        'to hơn, duy trì bôi gel trị sẹo chứa chiết xuất hành tây.'],
  'bien_the_kham': ['Khối sẹo kích thước 2x6cm vùng trước xương ức, màu đỏ tím bóng, mật độ chắc '
                    'cứng, chân sẹo lan rộng ra ngoài bờ mép mổ cũ.',
                    'Sẹo gồ cao hơn mặt da 5mm màu hồng tím căng bóng vùng dái tai, mật độ chắc '
                    'như cao su, đau nhói khi chạm vào nốt sẹo.',
                    'Khám thấy khối xơ phì đại bờ hình càng cua bò ra mô lành xung quanh vết mổ cũ '
                    'ở vai, bề mặt nhẵn bóng giãn mạch nhỏ li ti.',
                    'Tổn thương sẹo lồi kích thước lớn vùng ngực, màu đỏ tươi đang trong giai đoạn '
                    'tăng sinh hoạt tính, nhiều cảm giác ngứa nhức.',
                    'Ghi nhận dải sẹo lồi cứng chắc màu nâu đỏ dài 8cm vùng cẳng tay sau tai nạn, '
                    'chân sẹo bám sâu dính chặt vào lớp cân mạc dưới.',
                    'Khối sẹo tăng sinh quá mức ranh giới vết khâu thẩm mỹ cũ, bề mặt trơn láng '
                    'không có chân lông, ấn thấy mật độ chắc như sụn cứng.'],
  'chan_doan': 'Sẹo lồi phì đại sau can thiệp phẫu thuật lồng ngực.',
  'chinh': ['khối mô sẹo tăng sinh gờ cao vượt ra ngoài ranh giới ban đầu của vết thương',
            'màu sắc sẹo đỏ hồng hoặc đỏ tía bề mặt căng bóng nhẵn không có lông tóc',
            'mật độ sẹo cứng chắc như sụn dính chặt vào tổ chức da sâu bên dưới'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định tiêm nội tổn thương triamcinolone acetonide kết hợp 5-fluorouracil định '
              'kỳ, dán miếng gel silicone bảo vệ chống tăng sinh.',
  'kham': 'Khối sẹo kích thước 2x6cm vùng trước xương ức, màu đỏ tím bóng, mật độ chắc cứng, chân '
          'sẹo lan rộng ra ngoài bờ mép mổ cũ.',
  'nhom': 'cả hai',
  'phu': ['cảm giác ngứa ngáy và đau nhức buốt nhói thường xuyên tại khối sẹo lồi',
          'cơn đau nhức tăng lên khi thời tiết thay đổi hoặc khi bị va chạm cọ xát quần áo',
          'tiền sử cá nhân có cơ địa tạo sẹo lồi sau các vết xước vết mổ trước đó'],
  'ten': 'sẹo lồi phì đại sau phẫu thuật chấn thương'},
 {'bien_the_chan_doan': ['Bệnh vảy cá bẩm sinh thể thông thường Ichthyosis vulgaris.',
                         'Bệnh vảy cá bẩm sinh thể thông thường đợt khô nẻ tăng nặng mùa lạnh.',
                         'Theo dõi bệnh vảy cá bẩm sinh thể thông thường có kèm viêm da cơ địa.',
                         'Bệnh vảy cá bẩm sinh thể thông thường thể tróc vảy đa giác đối xứng.',
                         'Bệnh vảy cá bẩm sinh thể thông thường di truyền gen trội.',
                         'Nghi ngờ bệnh vảy cá bẩm sinh thể thông thường thể nhẹ.'],
  'bien_the_ke_hoach': ['Kê đơn kem dưỡng ẩm chứa urea 10% kết hợp axit lactic thoa đều ngay sau '
                        'tắm, tránh dùng xà phòng kiềm mạnh và tắm nước quá nóng.',
                        'Chỉ định bôi kem chứa urea 10% và ceramide 2-3 lần/ngày phục hồi hàng rào '
                        'thượng bì, tắm bằng dầu tắm không chứa xà phòng tạo bọt.',
                        'Hướng dẫn bôi thuốc mỡ tiêu sừng axit salicylic 3% cho các vùng da đóng '
                        'vảy dày cẳng chân, duy trì bôi kem làm mềm da hàng ngày.',
                        'Tư vấn tắm nước ấm vừa phải trong thời gian ngắn dưới 10 phút, thoa kem '
                        'dưỡng ẩm ngay trong vòng 3 phút sau khi thấm khô da.',
                        'Kê đơn thuốc làm mềm sừng chứa ammonium lactate 12%, giải thích tính chất '
                        'di truyền mạn tính và cách kiểm soát nứt nẻ mùa đông.',
                        'Hướng dẫn sử dụng máy tạo ẩm trong phòng ngủ mùa khô hanh, kết hợp uống '
                        'đủ nước và bôi dưỡng ẩm mỡ khoáng petrolatum.'],
  'bien_the_kham': ['Da hai cẳng chân khô sần tróc vảy đa giác xám viền hơi bong mép, các nếp gấp '
                    'khoeo và nách hoàn toàn bình thường, vân bàn tay đậm nét.',
                    'Khám thấy vảy da hình đa giác nhỏ màu nâu nhạt bám dính như vảy cá ở mặt '
                    'trước xương chày hai bên, hố khoeo chân hoàn toàn sạch vảy.',
                    'Tổn thương da khô tróc vảy cám khắp mặt duỗi cẳng tay và cẳng chân, lòng bàn '
                    'tay tăng nhiều đường vân sâu nứt nẻ.',
                    'Da cẳng chân thô ráp bong vảy xám hình vảy rắn, sờ ráp như giấy nhám, các nếp '
                    'kẽ bẹn nách khuỷu không tổn thương.',
                    'Ghi nhận vảy da mỏng hình vảy cá đối xứng hai chi dưới, viền vảy hơi cuộn '
                    'mép, không có ban đỏ nền, da đầu có vảy mịn nhẹ.',
                    'Bề mặt da khô sần tróc các phiến sừng đa giác màu trắng xám, mật độ vảy dày ở '
                    'cẳng chân và đùi, bàn tay có dấu hiệu tăng nếp nhăn.'],
  'chan_doan': 'Bệnh vảy cá bẩm sinh thể thông thường Ichthyosis vulgaris.',
  'chinh': ['da khô ráp tróc vảy mỏng hình đa giác màu xám nhạt hoặc nâu bám chặt như vảy cá',
            'tổn thương phân bố đối xứng tập trung nhiều nhất ở mặt duỗi hai cẳng chân',
            'các nếp gấp lớn như khoeo chân nách và khuỷu tay hoàn toàn lành lặn không bị tổn '
            'thương'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Kê đơn kem dưỡng ẩm chứa urea 10% kết hợp axit lactic thoa đều ngay sau tắm, tránh '
              'dùng xà phòng kiềm mạnh và tắm nước quá nóng.',
  'kham': 'Da hai cẳng chân khô sần tróc vảy đa giác xám viền hơi bong mép, các nếp gấp khoeo và '
          'nách hoàn toàn bình thường, vân bàn tay đậm nét.',
  'nhom': 'cả hai',
  'phu': ['tình trạng khô nứt nẻ da trở nên nặng nề hơn vào mùa hanh khô mùa đông',
          'tăng đường vân sâu tại lòng bàn tay và lòng bàn chân',
          'tiền sử bản thân hoặc gia đình có kèm theo cơ địa dị ứng viêm mũi hen suyễn'],
  'ten': 'bệnh vảy cá bẩm sinh thể thông thường'},
 {'bien_the_chan_doan': ['Viêm quầng Erysipelas cẳng chân do nhiễm liên cầu khuẩn.',
                         'Viêm quầng Erysipelas cẳng chân cấp tính thể có bọng nước.',
                         'Theo dõi viêm quầng Erysipelas cẳng chân khởi phát từ nấm kẽ ngón chân.',
                         'Bệnh viêm quầng Erysipelas cẳng chân có phản ứng sốt cao rét run.',
                         'Viêm quầng Erysipelas cẳng chân mức độ trung bình.',
                         'Nghi ngờ viêm quầng Erysipelas cẳng chân phân biệt với viêm mô tế bào.'],
  'bien_the_ke_hoach': ['Chỉ định điều trị kháng sinh benzylpenicillin hoặc amoxicillin tĩnh mạch, '
                        'bất động kê cao chân, xét nghiệm công thức máu và cấy dịch.',
                        'Kê đơn kháng sinh amoxicillin phối hợp acid clavulanic đường uống hoặc '
                        'tiêm, bất động chi dưới kê cao chân trên gối 30 độ.',
                        'Làm xét nghiệm công thức máu bạch cầu tăng cao ưu thế trung tính, tốc độ '
                        'máu lắng ESR và CRP tăng, dùng paracetamol hạ sốt.',
                        'Điều trị kháng sinh chống liên cầu beta tan huyết nhóm A, bôi thuốc chống '
                        'nấm kẽ ngón chân triệt để loại bỏ đường vào của vi khuẩn.',
                        'Chỉ định kháng sinh tĩnh mạch cefazolin hoặc penicillin, theo dõi đánh '
                        'dấu đường bờ tổn thương bằng bút lông để theo dõi đáp ứng.',
                        'Hướng dẫn nghỉ ngơi tuyệt đối tại giường, chườm gạc mát bằng nước muối '
                        'sinh lý làm dịu đau rát, điều trị dự phòng tái phát.'],
  'bien_the_kham': ['Cẳng chân trái có mảng đỏ tươi phù nề giới hạn sắc nét gờ cao, ấn rất đau, '
                    'nhiệt độ da nóng, hạch bẹn trái sưng đau 1.5cm.',
                    'Khám thấy mảng hồng ban bóng phù nề bờ gờ bậc thang rõ nét cẳng chân phải, '
                    'sốt 39.2 độ C, kẽ ngón chân 4-5 có vết nứt trợt nấm.',
                    'Vùng cẳng chân sưng to đỏ tươi viền gờ nổi cao phân định rõ với vùng da lành, '
                    'sờ nóng rực, ấn đau chói nông lớp bì thượng bì.',
                    'Tổn thương da dạng viêm quầng điển hình mặt trước ngoài cẳng chân, bề mặt có '
                    'bọng nước nhỏ dịch trong, hạch bẹn sưng viêm to.',
                    'Mảng da đỏ tươi phù nề lan rộng nhanh sau 24 giờ, ranh giới bờ gồ gờ rõ như '
                    'bậc thềm, bệnh nhân run rẩy vì sốt cao dao động.',
                    'Ghi nhận mảng viêm đỏ rực căng bóng cẳng chân, sờ nóng hơn hẳn chi đối diện, '
                    'bờ mép nhô cao rõ, hạch vùng bẹn sưng đau nhức.'],
  'chan_doan': 'Viêm quầng Erysipelas cẳng chân do nhiễm liên cầu khuẩn.',
  'chinh': ['mảng đỏ da phù nề sưng bóng lan nhanh có bờ gờ cao ranh giới rõ rệt với da lành',
            'nóng đỏ đau nhức nhối dữ dội tại cẳng chân làm hạn chế việc bước đi',
            'khởi phát rầm rộ sốt cao đột ngột ba chín đến bốn mươi độ rét run và mệt mỏi'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Chỉ định điều trị kháng sinh benzylpenicillin hoặc amoxicillin tĩnh mạch, bất động '
              'kê cao chân, xét nghiệm công thức máu và cấy dịch.',
  'kham': 'Cẳng chân trái có mảng đỏ tươi phù nề giới hạn sắc nét gờ cao, ấn rất đau, nhiệt độ da '
          'nóng, hạch bẹn trái sưng đau 1.5cm.',
  'nhom': 'người lớn',
  'phu': ['nổi hạch bẹn sưng to ấn đau cùng bên chân bị tổn thương viêm',
          'da căng bóng có thể nổi thêm vài bọng nước dịch trong trên nền mảng đỏ',
          'ngõ vào vi khuẩn là vết trợt loét kẽ ngón chân do nấm hoặc vết xước da'],
  'ten': 'viêm quầng Erysipelas cẳng chân do liên cầu'},
 {'bien_the_chan_doan': ['Viêm mô tế bào cẳng chân cấp do nhiễm vi khuẩn tụ cầu.',
                         'Viêm mô tế bào cẳng chân cấp tính nghi do tụ cầu vàng Staphylococcus '
                         'aureus.',
                         'Theo dõi viêm mô tế bào cẳng chân ở bệnh nhân đái tháo đường.',
                         'Viêm mô tế bào cẳng chân có biến chứng viêm mạch bạch huyết đi kèm.',
                         'Bệnh viêm mô tế bào cẳng chân mức độ trung bình có sốt cao.',
                         'Nghi ngờ viêm mô tế bào cẳng chân phân biệt với huyết khối tĩnh mạch '
                         'sâu.'],
  'bien_the_ke_hoach': ['Kháng sinh tĩnh mạch kháng tụ cầu nhóm oxacillin hoặc cefazolin, kê cao '
                        'chi dưới nghỉ ngơi tại giường, theo dõi dấu hiệu hoại tử.',
                        'Chỉ định kháng sinh đường tiêm truyền oxacillin 2g mỗi 6 giờ hoặc '
                        'cefazolin, làm siêu âm Doppler mạch máu loại trừ huyết khối tĩnh mạch.',
                        'Lấy máu cấy tìm vi khuẩn trước khi dùng kháng sinh, theo dõi dấu sinh tồn '
                        'và đường kính vòng cẳng chân mỗi ngày.',
                        'Kê cao chi dưới nghỉ ngơi tránh đứng lâu, kiểm soát chặt chẽ đường huyết '
                        'bằng insulin nếu có đái tháo đường, dùng thuốc giảm đau hạ sốt.',
                        'Chỉ định kháng sinh phổ rộng bao phủ tụ cầu và trực khuẩn gram âm nếu có '
                        'suy giảm miễn dịch, đánh dấu viền đỏ theo dõi đáp ứng thuốc.',
                        'Hội chẩn Ngoại khoa nếu nghi ngờ có ổ áp xe sâu hoặc dấu hiệu viêm cân '
                        'mạc hoại tử, dùng kháng sinh phối hợp đường toàn thân.'],
  'bien_the_kham': ['Cẳng chân sưng to hơn chân đối diện, da đỏ sẫm ranh giới mờ nhạt, ấn đau chói '
                    'sâu mô mềm dưới da, hạch bẹn cùng bên sưng đau.',
                    'Bắp chân trái sưng to phù nề ấn lõm nhẹ, da đỏ tía lan tỏa không rõ bờ ranh '
                    'giới, nhiệt độ da tăng cao, ấn đau buốt sâu.',
                    'Khám thấy cẳng chân đỏ rực phù nề mô dưới da lan từ mắt cá lên gần khớp gối, '
                    'sốt 38.8 độ C, có vết trầy xước đóng vảy mủ ở mu chân.',
                    'Tổn thương viêm thâm nhiễm sâu hạ bì cẳng chân, da căng bóng mất nếp nhăn, '
                    'ranh giới hòa dần vào da lành, hạch bẹn sưng đau rõ.',
                    'Ghi nhận sưng tấy lan tỏa một bên cẳng chân, bờ tổn thương không sắc nét, ấn '
                    'đau tức sâu cơ bắp, mạch mu chân bắt rõ ràng.',
                    'Da cẳng chân phù nề đỏ sẫm tỏa nhiệt nóng ran, có vệt đỏ viêm bạch mạch chạy '
                    'dọc lên bẹn, ấn đau nhiều ở lớp mỡ dưới da.'],
  'chan_doan': 'Viêm mô tế bào cẳng chân cấp do nhiễm vi khuẩn tụ cầu.',
  'chinh': ['vùng da cẳng chân sưng nề đỏ rực lan tỏa ranh giới không rõ ràng nhòe với da lành',
            'cảm giác đau nhức sâu thâm tím căng tức nặng nề toàn bộ bắp chân',
            'sốt rét run mệt mỏi và cảm giác nóng ran toàn thân'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Kháng sinh tĩnh mạch kháng tụ cầu nhóm oxacillin hoặc cefazolin, kê cao chi dưới '
              'nghỉ ngơi tại giường, theo dõi dấu hiệu hoại tử.',
  'kham': 'Cẳng chân sưng to hơn chân đối diện, da đỏ sẫm ranh giới mờ nhạt, ấn đau chói sâu mô '
          'mềm dưới da, hạch bẹn cùng bên sưng đau.',
  'nhom': 'người lớn',
  'phu': ['da căng cứng bóng lộn ấn có thể để lại vết lõm nhẹ phù nề tổ chức dưới da',
          'nổi hạch vùng bẹn cùng bên sưng đau và đường viền đỏ viêm mạch bạch huyết',
          'tiền sử trầy xước da côn trùng cắn hoặc đái tháo đường kiểm soát kém'],
  'ten': 'viêm mô tế bào cẳng chân do tụ cầu'},
 {'bien_the_chan_doan': ['Nhọt cụm nhọt độc vùng gáy carbuncle do tụ cầu vàng.',
                         'Nhọt cụm nhọt độc vùng gáy carbuncle thể hoại tử nhiều ngòi mủ.',
                         'Bệnh nhọt cụm nhọt độc vùng gáy carbuncle ở người bệnh đái tháo đường.',
                         'Theo dõi nhọt cụm nhọt độc vùng gáy carbuncle nhiễm tụ cầu vàng kháng '
                         'methicillin.',
                         'Nhọt cụm nhọt độc vùng gáy carbuncle đợt viêm tấy lan tỏa mô mềm.',
                         'Nghi ngờ nhọt cụm nhọt độc vùng gáy carbuncle có nguy cơ nhiễm trùng '
                         'huyết.'],
  'bien_the_ke_hoach': ['Rạch dẫn lưu làm sạch ổ mủ hoại tử, dùng kháng sinh toàn thân liều cao '
                        'phổ diệt tụ cầu, kiểm soát chặt chẽ đường huyết.',
                        'Chỉ định chích rạch giải áp tháo mủ nhiều ngòi, cắt lọc tổ chức hoại tử, '
                        'đặt bấc dẫn lưu và cấy mủ làm kháng sinh đồ.',
                        'Dùng kháng sinh tĩnh mạch vancomycin hoặc oxacillin liều cao, thay băng '
                        'sát khuẩn bằng dung dịch povidone iodine 2 lần mỗi ngày.',
                        'Xét nghiệm đường huyết mao mạch và HbA1c, điều chỉnh liều insulin kiểm '
                        'soát glucose máu, dùng thuốc giảm đau kháng viêm.',
                        'Làm công thức máu cấy máu theo dõi biến chứng nhiễm trùng huyết, chăm sóc '
                        'vết thương hở bằng gạc tẩm dung dịch sát trùng.',
                        'Hội chẩn Ngoại khoa phẫu thuật mở rộng làm sạch ổ nhọt cụm, bù nước điện '
                        'giải và nâng cao thể trạng dinh dưỡng người bệnh.'],
  'bien_the_kham': ['Khối thâm nhiễm viêm tấy đường kính 6cm vùng sau gáy, cứng chắc ấn đau nhói, '
                    'bề mặt có 5 lỗ rò rỉ mủ vàng đặc, sốt 38.8 độ C.',
                    'Vùng gáy có ổ viêm cứng gồ cao kích thước quả quýt, đỏ sẫm da căng bóng, nặn '
                    'nhẹ thấy mủ vàng phòi qua nhiều lỗ nang lông dạng tổ ong.',
                    'Khám thấy khối nhọt chùm sau gáy đau nhức dữ dội, mô dưới da hoại tử lổn '
                    'nhổn, ấn có cảm giác dao động mủ ở trung tâm khối viêm.',
                    'Tổn thương dạng carbuncle thâm nhiễm sâu cơ gáy, da đỏ tím nề cứng, nhiều '
                    'miệng mủ đóng vảy xám đen, hạch góc hàm sau sưng to.',
                    'Khối sưng đỏ tấy kích thước 5x7cm vùng gáy cổ, ấn đau buốt người bệnh co rúm '
                    'người, sốt cao 39 độ C, hơi thở có mùi sốt nhiễm khuẩn.',
                    'Ghi nhận ổ nhọt độc liên kết nhiều nang lông vùng gáy, bề mặt rỉ dịch mủ máu '
                    'hôi, mô hạt xung quanh sưng nề đỏ rực lan tỏa.'],
  'chan_doan': 'Nhọt cụm nhọt độc vùng gáy carbuncle do tụ cầu vàng.',
  'chinh': ['khối viêm tấy gồ cao đau nhức dữ dội sâu dưới da vùng gáy tập hợp nhiều ngòi mủ',
            'bề mặt khối viêm thủng nhiều lỗ rò chảy dịch mủ đặc lẫn máu như tổ ong',
            'sốt cao dao động ớn lạnh mệt mỏi kiệt sức và đau đầu căng cơ cổ'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Rạch dẫn lưu làm sạch ổ mủ hoại tử, dùng kháng sinh toàn thân liều cao phổ diệt tụ '
              'cầu, kiểm soát chặt chẽ đường huyết.',
  'kham': 'Khối thâm nhiễm viêm tấy đường kính 6cm vùng sau gáy, cứng chắc ấn đau nhói, bề mặt có '
          '5 lỗ rò rỉ mủ vàng đặc, sốt 38.8 độ C.',
  'nhom': 'người lớn',
  'phu': ['vận động xoay cổ cúi ngửa bị hạn chế tối đa do khối sưng nề căng cứng',
          'vùng da xung quanh tấy đỏ thẫm lan rộng phù nề mô liên kết lân cận',
          'tiền sử mắc bệnh đái tháo đường hoặc thể trạng suy giảm miễn dịch'],
  'ten': 'nhọt cụm nhọt độc vùng gáy carbuncle'},
 {'bien_the_chan_doan': ['Chốc loét Ecthyma chi dưới do liên cầu phối hợp tụ cầu.',
                         'Bệnh chốc loét Ecthyma chi dưới thể loét sâu hoại tử.',
                         'Chốc loét Ecthyma chi dưới sau cào gãi nốt côn trùng đốt.',
                         'Theo dõi chốc loét Ecthyma chi dưới bội nhiễm vi khuẩn sinh mủ.',
                         'Chốc loét Ecthyma chi dưới có nguy cơ để lại sẹo lõm teo sắc tố.',
                         'Nghi ngờ chốc loét Ecthyma chi dưới ở người có cơ địa suy kiệt miễn '
                         'dịch.'],
  'bien_the_ke_hoach': ['Ngâm rửa bong vảy tiết bằng dung dịch sát khuẩn dịu nhẹ, bôi thuốc mỡ '
                        'kháng sinh mupirocin phối hợp kháng sinh uống cephalexin.',
                        'Ngâm đắp gạc nước muối sinh lý ấm làm mềm và bóc nhẹ lớp vảy tiết dày, '
                        'bôi mỡ mupirocin 2% ngày 3 lần, uống amoxicillin/clavulanate.',
                        'Chỉ định cấy dịch đáy loét làm kháng sinh đồ, kê đơn kháng sinh toàn thân '
                        'nhóm cephalosporin thế hệ 1 trong 7-10 ngày.',
                        'Rửa vết loét hàng ngày bằng dung dịch thuốc tím pha loãng 1/10000, băng '
                        'gạc vô trùng bảo vệ tránh ruồi bọ và bụi bẩn.',
                        'Kê đơn kháng sinh đường uống chống tụ cầu và liên cầu, bổ sung dinh dưỡng '
                        'vitamin C và kẽm thúc đẩy tái tạo tổ chức hạt.',
                        'Hướng dẫn vệ sinh thân thể sạch sẽ, giữ chân khô ráo, theo dõi sát tiến '
                        'trình biểu mô hóa đáy vết loét tại cơ sở y tế.'],
  'bien_the_kham': ['Vết loét sâu kích thước 1.5cm ở cẳng chân dưới vảy tiết dày sẫm màu, bóc vảy '
                    'đáy loét sâu bờ dựng đứng, xung quanh sưng đỏ tấy.',
                    'Khám thấy 3 vết loét hình tròn đường kính 1-2cm ở cẳng chân, vảy tiết xám đen '
                    'dày cộm bám chắc, viền bờ loét gồ cứng tím đỏ.',
                    'Tổn thương loét ăn sâu qua màng đáy da cẳng chân, đáy loét bẩn có mủ xám đục, '
                    'ấn xung quanh bờ loét đau nhói nhiều.',
                    'Ghi nhận vết chốc loét điển hình ở mặt trước xương chày, vảy cứng màu nâu đen '
                    'như mai rùa, bóc vảy lộ hố loét bờ sắc đứng.',
                    'Nhiều ổ chốc loét sâu chi dưới rải rác, bờ tổn thương đỏ gờ cao ấn cứng chắc, '
                    'đáy loét rỉ mủ nhớt, hạch bẹn cùng bên hơi sưng.',
                    'Vết loét tròn bờ gờ rõ đáy thâm nhiễm mủ vàng xám, phủ vảy tiết khô dày cứng, '
                    'xung quanh da có quầng đỏ viêm tấy.'],
  'chan_doan': 'Chốc loét Ecthyma chi dưới do liên cầu phối hợp tụ cầu.',
  'chinh': ['tổn thương loét sâu xuyên qua trung bì hình tròn bờ gờ đứng có gờ cứng xung quanh',
            'đáy vết loét phủ lớp mủ vàng xám bẩn và tiết dịch nhớt dính',
            'phủ bên trên là vảy tiết dày cứng màu xám nâu đen bám rất chặt'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Ngâm rửa bong vảy tiết bằng dung dịch sát khuẩn dịu nhẹ, bôi thuốc mỡ kháng sinh '
              'mupirocin phối hợp kháng sinh uống cephalexin.',
  'kham': 'Vết loét sâu kích thước 1.5cm ở cẳng chân dưới vảy tiết dày sẫm màu, bóc vảy đáy loét '
          'sâu bờ dựng đứng, xung quanh sưng đỏ tấy.',
  'nhom': 'cả hai',
  'phu': ['đau nhức nhói tại vị trí vết loét đặc biệt khi đi lại va chạm',
          'sau khi vết loét lành sẽ để lại sẹo lõm teo da vĩnh viễn kèm thâm sắc tố',
          'vệ sinh kém suy dinh dưỡng hoặc nhiều nốt côn trùng cắn bị gãi xước'],
  'ten': 'chốc loét Ecthyma chi dưới'},
 {'bien_the_chan_doan': ['Phù mạch dị ứng di truyền phù Quincke đợt cấp dọa tắc đường thở.',
                         'Phù mạch dị ứng di truyền phù Quincke do thiếu hụt chất ức chế C1-INH.',
                         'Theo dõi phù mạch dị ứng di truyền phù Quincke đợt cấp thể tiêu hóa '
                         'bụng.',
                         'Phù mạch dị ứng di truyền phù Quincke có biểu hiện phù thanh quản cấp.',
                         'Cấp cứu phù mạch dị ứng di truyền phù Quincke đợt bùng phát nặng.',
                         'Nghi ngờ phù mạch dị ứng di truyền phù Quincke thể gia đình qua trung '
                         'gian bradykinin.'],
  'bien_the_ke_hoach': ['Chuẩn bị sẵn sàng phương tiện đặt nội khí quản cấp cứu, truyền dịch cô '
                        'đặc C1-inhibitor hoặc huyết tương tươi đông lạnh, tiêm icatibant.',
                        'Chỉ định tiêm dưới da icatibant 30mg đối kháng thụ thể bradykinin B2, '
                        'chuẩn bị bộ mở khí quản cấp cứu bên giường bệnh.',
                        'Truyền tĩnh mạch chất ức chế C1 esterase cô đặc tinh chế 20 đơn vị/kg, '
                        'theo dõi sát dấu hiệu tắc nghẽn đường thở trên.',
                        'Truyền huyết tương tươi đông lạnh FFP nếu không có sẵn C1-INH tinh chế, '
                        'theo dõi SpO2 liên tục và đặt ống nội khí quản sớm.',
                        'Đo nồng độ bổ thể C4 máu giảm nặng và định lượng nồng độ chức năng '
                        'protein C1-INH, chuyển phòng hồi sức cấp cứu ICU.',
                        'Tư vấn điều trị dự phòng dài hạn bằng danazol hoặc kháng thể đơn dòng '
                        'lanadelumab, lập thẻ cảnh báo bệnh lý khẩn cấp mang theo người.'],
  'bien_the_kham': ['Môi trên và hai mi mắt sưng nề to biến dạng, niêm mạc họng phù nề thanh môn '
                    'hơi hẹp, da vùng phù trắng nhạt không có mày đay.',
                    'Phù nề to biến dạng toàn bộ mặt môi vều dày, lưỡi to chèn ép khoang miệng, '
                    'giọng nói khàn đặc, SpO2 94% khí phòng.',
                    'Khám thấy mô dưới da mi mắt và môi mọng nước căng cứng ấn không lõm, da nhợt '
                    'nhạt không đỏ rực, tiếng thở rít thanh quản nhẹ.',
                    'Phù nề dữ dội vùng hầu họng và môi trên, màn hầu phù mọng như giọt nước, cảm '
                    'giác nghẹt thở nuốt vướng tăng nhanh từng phút.',
                    'Ghi nhận sưng phù mô mềm môi và bàn tay đột ngột, không kèm sẩn phù mày đay '
                    'ngoài da, bụng đau quặn từng cơn kèm buồn nôn.',
                    'Mặt biến dạng do phù mạch cấp tính quanh hốc mắt và môi, nuốt khó thở nông '
                    'rít, không đáp ứng với tiêm adrenaline thông thường.'],
  'chan_doan': 'Phù mạch dị ứng di truyền phù Quincke đợt cấp dọa tắc đường thở.',
  'chinh': ['sưng nề phù đột ngột căng cứng mô mềm dưới da ở mi mắt môi lưỡi và bộ phận sinh dục',
            'phù thanh quản gây cảm giác nghẹn thở nuốt khó nói khàn giọng dọa ngạt thở',
            'vùng phù không đỏ không ngứa mà có cảm giác căng tức nặng nề bỏng rát'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Chuẩn bị sẵn sàng phương tiện đặt nội khí quản cấp cứu, truyền dịch cô đặc '
              'C1-inhibitor hoặc huyết tương tươi đông lạnh, tiêm icatibant.',
  'kham': 'Môi trên và hai mi mắt sưng nề to biến dạng, niêm mạc họng phù nề thanh môn hơi hẹp, da '
          'vùng phù trắng nhạt không có mày đay.',
  'nhom': 'cả hai',
  'phu': ['đau quặn bụng dữ dội buồn nôn do phù nề thành ruột cục bộ',
          'phù xuất hiện nhanh chóng tự thoái lui sau hai đến ba ngày mà không để lại di chứng',
          'tiền sử gia đình có người thân từng bị các đợt sưng phù mặt đột ngột tương tự'],
  'ten': 'phù mạch dị ứng di truyền phù Quincke'},
 {'bien_the_chan_doan': ['Sốc phản vệ độ 2 do dị ứng thức ăn hải sản.',
                         'Phản vệ độ 2 tiến triển cấp sau ăn tôm biển.',
                         'Theo dõi sốc phản vệ độ 2 do thức ăn hải sản có co thắt phế quản.',
                         'Cấp cứu phản vệ mức độ nặng độ hai liên quan hải sản.',
                         'Phản ứng phản vệ độ 2 đa cơ quan da hô hấp và tiêu hóa.',
                         'Nghi ngờ sốc phản vệ độ 2 dọa chuyển độ 3 nguy kịch.'],
  'bien_the_ke_hoach': ['Tiêm bắp ngay lập tức adrenaline 0.5mg mặt trước ngoài đùi, thở oxy qua '
                        'mask gọng kính, thiết lập đường truyền tĩnh mạch và tiêm '
                        'methylprednisolone.',
                        'Tiêm bắp adrenaline 1/2 ống (0.5mg) ngay tại đùi, cho nằm đầu bằng gác '
                        'chân cao, thở oxy 5 lít/phút, truyền tĩnh mạch NaCl 0.9%.',
                        'Đánh giá lại huyết áp và nhịp thở sau 3-5 phút, nhắc lại adrenaline tiêm '
                        'bắp nếu chưa đỡ khó thở, tiêm tĩnh mạch diphenhydramine và solumedrol.',
                        'Cấp cứu phản vệ theo phác đồ Thông tư 51 Bộ Y tế: adrenaline tiêm bắp lập '
                        'tức, lập 2 đường truyền tĩnh mạch lớn, theo dõi monitor liên tục.',
                        'Khí dung salbutamol giãn phế quản nếu còn co thắt đường thở, tiêm tĩnh '
                        'mạch methylprednisolone 40mg, theo dõi sát tối thiểu 24 giờ đề phòng pha '
                        'hai.',
                        'Tiêm bắp ngay adrenaline liều chuẩn, ghi chép bảng theo dõi sinh hiệu mỗi '
                        '5-10 phút, cấp đơn bút tiêm tự động adrenaline khi ra viện.'],
  'bien_the_kham': ['Mày đay toàn thân, nhịp thở 28 l/p có tiếng rít rale rít rải rác hai phế '
                    'trường, mạch nhanh 115 l/p, huyết áp 100/65 mmHg còn giữ được.',
                    'Khám thấy phát ban phù đỏ ngứa ngáy toàn thân, môi sưng phù nhẹ, thở rít '
                    'stridor nhẹ thì hít vào, mạch 110 l/p, HA 105/70 mmHg.',
                    'Bệnh nhân khó thở hốt hoảng, nghe phổi có ran rít ran ngáy co thắt phế quản, '
                    'bụng ấn đau quặn quanh rốn, mạch nhanh nhỏ.',
                    'Mày đay sẩn phù khắp người kèm phù mạch mi mắt, thở nhanh nông 30 l/p co kéo '
                    'hõm ức, SpO2 93%, huyết áp chưa tụt sâu.',
                    'Ghi nhận phản ứng phản vệ độ hai khởi phát 20 phút sau ăn tôm, da đỏ ửng mày '
                    'đay nổi cộm, nôn 2 lần ra thức ăn, mạch 118 l/p.',
                    'Khám cấp cứu: mày đay đa hình thái ngứa nhiều, thở rít thanh quản nhẹ, khó '
                    'nuốt, tim nhịp nhanh đều, huyết áp 100/60 mmHg.'],
  'chan_doan': 'Sốc phản vệ độ 2 do dị ứng thức ăn hải sản.',
  'chinh': ['nổi mày đay sẩn phù ngứa ngáy dữ dội toàn thân xuất hiện nhanh sau ăn tôm cua',
            'cảm giác bóp nghẹn lồng ngực khó thở khò khè thở rít thanh quản',
            'đau quặn bụng dồn dập nôn thốc tháo và tiêu chảy phân lỏng ồ ạt'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Tiêm bắp ngay lập tức adrenaline 0.5mg mặt trước ngoài đùi, thở oxy qua mask gọng '
              'kính, thiết lập đường truyền tĩnh mạch và tiêm methylprednisolone.',
  'kham': 'Mày đay toàn thân, nhịp thở 28 l/p có tiếng rít rale rít rải rác hai phế trường, mạch '
          'nhanh 115 l/p, huyết áp 100/65 mmHg còn giữ được.',
  'nhom': 'cả hai',
  'phu': ['choáng váng xây xẩm mặt mày hồi hộp đánh trống ngực đập nhanh dồn dập',
          'phù nề môi lưỡi nuốt nghẹn và cảm giác ngứa ran trong cổ họng',
          'vã mồ hôi lạnh cảm giác lo âu hoảng hốt bồn chồn sợ hãi'],
  'ten': 'sốc phản vệ độ 2 do thức ăn hải sản'},
 {'bien_the_chan_doan': ['Dị ứng thuốc kháng sinh nhóm beta-lactam thể phát ban dát sẩn.',
                         'Dị ứng thuốc kháng sinh nhóm beta-lactam mức độ nhẹ đến trung bình.',
                         'Phản ứng dị ứng thuốc kháng sinh nhóm beta-lactam thể ban đỏ dạng sởi.',
                         'Theo dõi dị ứng thuốc kháng sinh nhóm beta-lactam amoxicillin khởi phát '
                         'chậm.',
                         'Dị ứng thuốc kháng sinh nhóm beta-lactam cấp tính chưa có suy hô hấp.',
                         'Nghi ngờ dị ứng thuốc kháng sinh nhóm beta-lactam thể dát sẩn toàn '
                         'thân.'],
  'bien_the_ke_hoach': ['Ngừng ngay lập tức kháng sinh nghi ngờ, ghi nhận vào hồ sơ cảnh báo dị '
                        'ứng thuốc, kê thuốc kháng histamine thế hệ hai và corticoid ngắn ngày.',
                        'Dừng ngay thuốc kháng sinh nhóm beta-lactam đang dùng, kê đơn cetirizine '
                        '10mg/ngày, dùng methylprednisolone 16mg/ngày trong 3-5 ngày.',
                        'Ghi chú tiền sử dị ứng penicillin vào phần đầu hồ sơ bệnh án, thay thế '
                        'kháng sinh bằng nhóm macrolid hoặc fluoroquinolone nếu còn nhiễm trùng.',
                        'Kê đơn thuốc bôi dưỡng ẩm làm dịu ngứa, uống kháng histamine fexofenadine '
                        '180mg, dặn tái khám ngay nếu xuất hiện khó thở hay loét miệng.',
                        'Tư vấn người bệnh không bao giờ tự ý sử dụng lại các thuốc nhóm '
                        'ampicillin amoxicillin cephalosporin, cấp thẻ dị ứng thuốc cá nhân.',
                        'Chỉ định ngừng thuốc lập tức, xét nghiệm công thức máu và chức năng gan '
                        'thận, dùng thuốc chống dị ứng đường uống theo dõi ngoại trú.'],
  'bien_the_kham': ['Phát ban dạng dát sẩn đỏ dạng sởi lan tỏa toàn thân, không có bọng nước bong '
                    'trợt, dấu hiệu Nikolsky âm tính, niêm mạc không tổn thương.',
                    'Khám thấy dát sẩn hồng ban kích thước 2-5mm liên kết thành từng đám ở ngực '
                    'lưng và hai tay, không hoại tử thượng bì, niêm mạc mắt môi bình thường.',
                    'Ban đỏ dạng tinh hồng nhiệt toàn thân xuất hiện sau 3 ngày uống cefalexin, ấn '
                    'kính mất màu, không có tổn thương bọng nước hay loét miệng.',
                    'Tổn thương da dạng sẩn phù đỏ rải rác đối xứng khắp cơ thể, cào gãi tạo nhiều '
                    'vết xước nhẹ bề mặt, hạch ngoại biên không sưng.',
                    'Ghi nhận phát ban dạng dát sẩn ngứa nhiều vùng thân mình và gốc chi, mạch 84 '
                    'l/p, huyết áp 115/75 mmHg, hô hấp bình thường.',
                    'Nhiều dát đỏ nhỏ li ti dày đặc ở bụng lưng và hai đùi, bề mặt hơi gờ nhẹ, '
                    'không có dấu hiệu bong vảy hoại tử, phản xạ nuốt bình thường.'],
  'chan_doan': 'Dị ứng thuốc kháng sinh nhóm beta-lactam thể phát ban dát sẩn.',
  'chinh': ['phát ban dạng dát sẩn đỏ ngứa rải rác toàn thân xuất hiện sau khi dùng amoxicillin',
            'ngứa ngáy râm ran dữ dội châm chích khắp người không dứt',
            'các ban đỏ tập trung dày đặc ở vùng thân mình cánh tay và lan ra cẳng chân'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Ngừng ngay lập tức kháng sinh nghi ngờ, ghi nhận vào hồ sơ cảnh báo dị ứng thuốc, '
              'kê thuốc kháng histamine thế hệ hai và corticoid ngắn ngày.',
  'kham': 'Phát ban dạng dát sẩn đỏ dạng sởi lan tỏa toàn thân, không có bọng nước bong trợt, dấu '
          'hiệu Nikolsky âm tính, niêm mạc không tổn thương.',
  'nhom': 'cả hai',
  'phu': ['sốt nhẹ hoặc cảm giác gai rét ớn lạnh thoáng qua khi ban đỏ bắt đầu phát tán',
          'mắt hơi cộm đỏ xót và sưng nhẹ mi mắt hai bên',
          'cảm giác bứt rứt khó chịu khó ngủ vì các cơn ngứa châm chích kéo dài'],
  'ten': 'dị ứng thuốc kháng sinh nhóm beta-lactam'},
 {'bien_the_chan_doan': ['Viêm kết mạc dị ứng mùa phấn hoa thể cấp tính.',
                         'Viêm kết mạc dị ứng mùa phấn hoa theo mùa có kèm viêm mũi dị ứng.',
                         'Theo dõi viêm kết mạc dị ứng mùa phấn hoa đợt bùng phát cấp.',
                         'Viêm kết mạc dị ứng mùa phấn hoa thể phù mọng kết mạc chemosis.',
                         'Bệnh viêm kết mạc dị ứng mùa phấn hoa ở người có cơ địa atopy.',
                         'Nghi ngờ viêm kết mạc dị ứng mùa phấn hoa chưa có biến chứng loét giác '
                         'mạc.'],
  'bien_the_ke_hoach': ['Tra mắt thuốc nhỏ kháng histamine phối hợp chất ổn định dưỡng bào '
                        'olopatadine, chườm lạnh mi mắt, tránh tiếp xúc phấn hoa.',
                        'Kê đơn thuốc nhỏ mắt olopatadine 0.1% nhỏ 1 giọt mỗi mắt 2 lần/ngày, '
                        'chườm khăn mát lên mắt 10 phút giảm phù nề tức thì.',
                        'Hướng dẫn nhỏ nước mắt nhân tạo không chất bảo quản rửa trôi dị nguyên '
                        'phấn hoa, uống thuốc kháng histamine fexofenadine giảm ngứa.',
                        'Tuyệt đối dặn dò không dụi tay lên mắt tránh trầy xước trợt giác mạc, đeo '
                        'kính râm bảo vệ mắt khi đi ra ngoài trời.',
                        'Chỉ định thuốc nhỏ mắt ketotifen hoặc natri cromoglycate duy trì, vệ sinh '
                        'mi mắt sạch sẽ bằng gạc vô trùng thấm nước muối.',
                        'Tư vấn hạn chế mở cửa sổ vào mùa phấn hoa bay nhiều, tái khám chuyên khoa '
                        'Mắt nếu mắt mờ hoặc đau nhức sâu trong nhãn cầu.'],
  'bien_the_kham': ['Kết mạc mi và kết mạc nhãn cầu sung huyết đỏ rực, phù nề mọng nước chemosis '
                    'rõ, rải rác nhú gai nhỏ li ti ở kết mạc mi dưới.',
                    'Hai mắt đỏ ngầu phù mọng kết mạc góc trong, chảy nước mắt trong liên tục, '
                    'giác mạc trong suốt không trầy xước biểu mô.',
                    'Khám mắt thấy mi mắt sưng nề nhẹ, kết mạc sụn mi có nhiều nhú gai nhỏ li ti '
                    'dạng lát sỏi, dịch tiết nhầy trong dính bờ mi.',
                    'Ghi nhận kết mạc nhãn cầu phù nề phồng chemosis nhô cao quanh rìa giác mạc, '
                    'sung huyết đỏ rực hai bên đối xứng, thị lực bình thường.',
                    'Mắt đỏ ngứa dữ dội, củng mạc cương tụ mạch máu nông di động theo kết mạc, '
                    'đồng tử hai bên tròn đều phản xạ ánh sáng tốt.',
                    'Tổn thương viêm kết mạc dị ứng hai mắt điển hình, phù nề kết mạc mi dưới, '
                    'xuất hiện phản xạ chớp mắt liên tục và sợ ánh sáng.'],
  'chan_doan': 'Viêm kết mạc dị ứng mùa phấn hoa thể cấp tính.',
  'chinh': ['ngứa mắt dữ dội dụi mắt liên tục kèm theo cộm rát xót như có hạt cát trong mắt',
            'mắt đỏ sung huyết kết mạc phù nề mọng nước phồng rộp nhãn cầu',
            'chảy nước mắt giàn giụa dịch tiết mắt trong suốt dính nhầy không có mủ'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Tra mắt thuốc nhỏ kháng histamine phối hợp chất ổn định dưỡng bào olopatadine, '
              'chườm lạnh mi mắt, tránh tiếp xúc phấn hoa.',
  'kham': 'Kết mạc mi và kết mạc nhãn cầu sung huyết đỏ rực, phù nề mọng nước chemosis rõ, rải rác '
          'nhú gai nhỏ li ti ở kết mạc mi dưới.',
  'nhom': 'cả hai',
  'phu': ['sợ ánh sáng chói nhắm nghiền mắt khi ra ngoài trời nắng',
          'hắt hơi sổ mũi liên tục ngứa ngáy vòm họng và ngứa mũi đi kèm',
          'triệu chứng bùng phát theo mùa trùng với thời điểm các loài hoa thụ phấn'],
  'ten': 'viêm kết mạc dị ứng mùa phấn hoa'},
 {'bien_the_chan_doan': ['Mày đay mạn tính vô căn tự phát tiến triển.',
                         'Bệnh mày đay mạn tính vô căn tự phát kéo dài trên 6 tuần.',
                         'Mày đay mạn tính vô căn tự phát mức độ trung bình theo thang UAS7.',
                         'Theo dõi mày đay mạn tính vô căn tự phát nghi liên quan tự kháng thể.',
                         'Mày đay mạn tính vô căn tự phát tái phát ban đêm gây mất ngủ.',
                         'Nghi ngờ mày đay mạn tính vô căn tự phát kháng trị với liều chuẩn kháng '
                         'histamine.'],
  'bien_the_ke_hoach': ['Xét nghiệm tầm soát kháng thể tuyến giáp và ký sinh trùng, chỉ định thuốc '
                        'kháng histamine H1 thế hệ hai liều chuẩn tăng bậc lên tối đa bốn lần.',
                        'Kê đơn levocetirizine 5mg/ngày, nếu sau 2 tuần chưa kiểm soát tăng liều '
                        'gấp đôi lên 10mg/ngày, theo dõi nhật ký chấm điểm triệu chứng UAS7.',
                        'Làm xét nghiệm công thức máu, tốc độ máu lắng, men gan, chức năng thận, '
                        'huyết thanh chẩn đoán giun sán và kháng thể kháng TPO.',
                        'Áp dụng phác đồ bậc điều trị mày đay quốc tế EAACI: tăng liều kháng '
                        'histamine không gây buồn ngủ lên gấp 4 lần trước khi dùng sinh học '
                        'omalizumab.',
                        'Tư vấn hạn chế rượu bia thực phẩm cay nóng chất bảo quản, tránh mặc đồ '
                        'chật bó sát gây tì đè kích hoạt tế bào mast.',
                        'Kê đơn phối hợp fexofenadine buổi sáng và bilastine buổi tối, dặn dò '
                        'không tự ý tiêm truyền corticoid kéo dài gây hội chứng Cushing.'],
  'bien_the_kham': ['Nhiều mảng sẩn phù kích thước 1-5cm rải rác khắp thân mình và tứ chi, bờ viền '
                    'uốn lượn, ấn kính mất màu đỏ tạm thời.',
                    'Khám thấy các sẩn phù gờ cao màu hồng viền đỏ hình tròn và bầu dục ở lưng '
                    'bụng đùi, trung tâm phù nhạt màu, cào gãi trầy da nhẹ.',
                    'Tổn thương sẩn phù mày đay xuất hiện khắp người thay đổi hình dạng liên tục, '
                    'không có hoại tử hay ban xuất huyết kèm theo.',
                    'Nhiều mảng phù dát sẩn ngứa ngáy dữ dội ở hai cẳng tay và mạn sườn, ranh giới '
                    'rõ nét như vỏ bản đồ, ấn kính biến mất hoàn toàn.',
                    'Ghi nhận sẩn phù mày đay cấp tính trên nền mạn tính, da nóng ran tại nốt phù, '
                    'không có sưng phù môi hay khó thở thanh quản.',
                    'Khám thấy hàng chục nốt sẩn phù gờ cao trên mặt da thân mình, các nốt xuất '
                    'hiện từ sáng đã lặn dần để lại nền da hoàn toàn nguyên vẹn.'],
  'chan_doan': 'Mày đay mạn tính vô căn tự phát tiến triển.',
  'chinh': ['nổi các sẩn phù gờ cao màu hồng đỏ kích thước to nhỏ đa dạng ngứa ngáy dữ dội',
            'các nốt phù xuất hiện và lặn mất hoàn toàn trong vòng hai mươi bốn giờ không để lại '
            'sẹo',
            'cơn mày đay tái đi tái lại hàng ngày kéo dài liên tục trên sáu tuần không rõ căn '
            'nguyên'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Xét nghiệm tầm soát kháng thể tuyến giáp và ký sinh trùng, chỉ định thuốc kháng '
              'histamine H1 thế hệ hai liều chuẩn tăng bậc lên tối đa bốn lần.',
  'kham': 'Nhiều mảng sẩn phù kích thước 1-5cm rải rác khắp thân mình và tứ chi, bờ viền uốn lượn, '
          'ấn kính mất màu đỏ tạm thời.',
  'nhom': 'người lớn',
  'phu': ['cơn ngứa bùng phát mạnh nhất vào ban đêm gây mất ngủ suy kiệt cơ thể',
          'vết phù có thể kèm theo cảm giác nóng rát căng tức nhẹ dưới da',
          'lo âu căng thẳng tâm lý do bệnh dây dưa dai dẳng ảnh hưởng sinh hoạt'],
  'ten': 'mày đay mạn tính vô căn tự phát'},
 {'bien_the_chan_doan': ['Mày đay do lạnh do áp lực vật lý phối hợp.',
                         'Mày đay do lạnh thể khởi phát sau tiếp xúc nhiệt độ thấp.',
                         'Mày đay do áp lực vật lý chậm thể da vẽ nổi sẩn phù.',
                         'Theo dõi mày đay do lạnh nguyên phát có nguy cơ phản vệ khi bơi nước '
                         'lạnh.',
                         'Bệnh mày đay vật lý thể phối hợp kích thích cơ học và nhiệt độ lạnh.',
                         'Nghi ngờ mày đay do lạnh thứ phát sau nhiễm trùng hoặc bệnh tự miễn.'],
  'bien_the_ke_hoach': ['Dặn dò giữ ấm cơ thể tuyệt đối tránh tắm nước lạnh đột ngột, dùng kháng '
                        'histamine liều cao dự phòng trước khi tiếp xúc thời tiết lạnh.',
                        'Cảnh báo nguy hiểm tính mạng tuyệt đối không được bơi lặn ở hồ nước sông '
                        'biển lạnh đề phòng sốc giải phóng histamine toàn thân.',
                        'Kê đơn thuốc kháng histamine H1 rupatadine hoặc bilastine liều gấp đôi '
                        'uống đều đặn mỗi ngày, mặc quần áo giữ ấm nhiều lớp mùa đông.',
                        'Hướng dẫn tránh mang vác đồ quá nặng tạo áp lực đè ép lâu lên vai và tay, '
                        'nới lỏng thắt lưng quần áo, đeo găng tay khi cầm đá lạnh.',
                        'Trang bị bút tiêm adrenaline tự động nếu có tiền sử chóng mặt tụt huyết '
                        'áp khi trời lạnh, theo dõi xét nghiệm protein huyết thanh cryoglobulin.',
                        'Tư vấn người bệnh uống nước ấm, tắm nước ấm trong phòng kín gió, uống '
                        'thuốc kháng dị ứng dự phòng trước khi ra ngoài trời rét.'],
  'bien_the_kham': ['Test cục nước đá áp lên cẳng tay trong 5 phút dương tính với sẩn phù nổi ngay '
                    'sau khi làm ấm, test da vẽ nổi cơ học dương tính.',
                    'Khám thấy vệt phù nề đỏ gờ cao xuất hiện sau 3 phút vạch que đè lưỡi trên da '
                    'lưng (dermatographism dương tính mạnh).',
                    'Vùng cẳng tay áp đá lạnh nổi mảng phù tròn đỏ ngứa đúng kích thước viên đá, '
                    'sẩn phù lặn sau 30 phút ở nhiệt độ phòng.',
                    'Nhiều vệt sẩn phù đỏ dọc theo dây đai quần và quai ba lô tì đè trên vai, ranh '
                    'giới rõ rệt theo đường nén ép cơ học.',
                    'Ghi nhận sẩn phù đỏ rải rác bàn tay và mặt sau khi đi gió lạnh về, nghiệm '
                    'pháp kích thích lạnh tại chỗ dương tính rõ ràng.',
                    'Test áp lực cơ học dương tính với sẩn phù nổi gờ cao sau khi mang vật nặng 10 '
                    'phút, không có tổn thương xuất huyết.'],
  'chan_doan': 'Mày đay do lạnh do áp lực vật lý phối hợp.',
  'chinh': ['nổi sẩn phù đỏ ngứa ngáy dữ dội ngay tại vùng da vừa tiếp xúc với nước lạnh hoặc gió '
            'rét',
            'các vết lằn phù đỏ nổi gờ cao dọc theo vị trí da bị tì đè cọ xát cơ học hoặc thắt dây '
            'nịt',
            'tổn thương sưng phù phát tán nhanh sau vài phút và biến mất sau khi làm ấm cơ thể'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Dặn dò giữ ấm cơ thể tuyệt đối tránh tắm nước lạnh đột ngột, dùng kháng histamine '
              'liều cao dự phòng trước khi tiếp xúc thời tiết lạnh.',
  'kham': 'Test cục nước đá áp lên cẳng tay trong 5 phút dương tính với sẩn phù nổi ngay sau khi '
          'làm ấm, test da vẽ nổi cơ học dương tính.',
  'nhom': 'cả hai',
  'phu': ['cảm giác châm chích buốt rát nhói buốt khi gặp trời mưa lạnh hoặc cầm vật lạnh',
          'đau đầu vã mồ hôi thoáng qua nếu tắm ngâm toàn thân trong nước lạnh',
          'dấu hiệu da vẽ nổi xuất hiện rõ nét sau khi vạch nhẹ vật tù lên mặt da'],
  'ten': 'mày đay do lạnh do áp lực vật lý'},
 {'bien_the_chan_doan': ['Viêm da tiếp xúc dị ứng với niken kim loại mạn tính.',
                         'Viêm da tiếp xúc dị ứng với niken do cúc quần kim loại.',
                         'Theo dõi viêm da tiếp xúc dị ứng với niken kim loại ở dái tai do khuyên '
                         'tai.',
                         'Viêm da tiếp xúc dị ứng với niken thể chàm hóa lichen hóa.',
                         'Bệnh chàm tiếp xúc dị ứng với niken đợt trợt ướt bội nhiễm nhẹ.',
                         'Nghi ngờ viêm da tiếp xúc dị ứng với niken kim loại qua test áp da.'],
  'bien_the_ke_hoach': ['Thực hiện dán patch test da xác định dị nguyên niken, ngừng sử dụng trang '
                        'sức và phụ kiện kim loại chứa niken, bôi mỡ corticoid tại chỗ.',
                        'Chỉ định làm test áp bì Patch Test với bộ dị nguyên chuẩn châu Âu khẳng '
                        'định dị ứng niken sulfat, bôi mỡ betamethasone 0.05% trong 1 tuần.',
                        'Hướng dẫn sơn phủ lớp sơn móng tay bóng trong suốt lên mặt sau cúc quần '
                        'kim loại hoặc thay bằng cúc nhựa gỗ, bôi kem dưỡng phục hồi.',
                        'Khuyên người bệnh chỉ đeo trang sức bằng vàng bạc nguyên chất hoặc titan '
                        'thép y tế không chứa niken, bôi kem hydrocortisone khi ngứa.',
                        'Kê đơn thuốc mỡ ức chế miễn dịch tacrolimus 0.1% bôi duy trì chống tái '
                        'phát vùng da mỏng, uống kháng histamine giảm cào gãi ban đêm.',
                        'Tư vấn tránh tiếp xúc với chìa khóa tiền xu gọng kính kim loại chứa '
                        'niken, hướng dẫn bôi kem bảo vệ hàng rào da trước khi làm việc.'],
  'bien_the_kham': ['Mảng viêm da hình tròn kích thước 3cm ngay dưới rốn tương ứng cúc quần kim '
                    'loại, dát đỏ mụn nước trợt nông, dày da sần sùi.',
                    'Hai dái tai sưng đỏ nề rỉ dịch vàng và đóng vảy tiết tại lỗ xỏ khuyên kim '
                    'loại mỹ ký, ngứa rát châm chích nhiều.',
                    'Khám thấy mảng hồng ban mụn nước nông hình chữ nhật ở cổ tay tương ứng mặt '
                    'đáy đồng hồ kim loại, da dày cộm lichen hóa.',
                    'Vùng da quanh rốn có tổn thương viêm da tiếp xúc rõ rệt khớp đúng vị trí khóa '
                    'thắt lưng, nhiều vết xước gãi và sạm da sau viêm.',
                    'Tổn thương da dạng chàm tiếp xúc khu trú ở ngón tay đeo nhẫn kim loại rẻ '
                    'tiền, da trợt đỏ nứt nẻ bong vảy khô rát.',
                    'Ghi nhận mảng da dày đỏ sẫm trợt rỉ dịch mụn nước li ti vùng thắt lưng quần, '
                    'ranh giới tổn thương sắc nét theo vật tiếp xúc.'],
  'chan_doan': 'Viêm da tiếp xúc dị ứng với niken kim loại mạn tính.',
  'chinh': ['ngứa ngáy dữ dội châm chích và nổi dát đỏ mụn nước nông tại vị trí tiếp xúc niken',
            'tổn thương khu trú đúng theo hình dạng của cúc quần kim loại khóa thắt lưng hoặc '
            'khuyên tai',
            'da trợt rỉ dịch đóng vảy vàng khô dày và thâm nhiễm lichen hóa do cào gãi lâu ngày'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Thực hiện dán patch test da xác định dị nguyên niken, ngừng sử dụng trang sức và '
              'phụ kiện kim loại chứa niken, bôi mỡ corticoid tại chỗ.',
  'kham': 'Mảng viêm da hình tròn kích thước 3cm ngay dưới rốn tương ứng cúc quần kim loại, dát đỏ '
          'mụn nước trợt nông, dày da sần sùi.',
  'nhom': 'cả hai',
  'phu': ['cảm giác nóng rát bỏng buốt tại vùng rốn và dái tai khi đeo đồ trang sức xi mạ',
          'tổn thương bùng phát nặng hơn khi thời tiết oi bức ra nhiều mồ hôi muối',
          'vết sẫm màu tăng sắc tố tồn tại dai dẳng nhiều tháng tại chỗ cúc quần tiếp xúc'],
  'ten': 'viêm da tiếp xúc dị ứng với niken kim loại'},
 {'bien_the_chan_doan': ['Viêm da tiếp xúc do độc tố pederin kiến ba khoang cấp tính.',
                         'Viêm da tiếp xúc kích ứng do côn trùng kiến ba khoang thể vệt dài.',
                         'Theo dõi viêm da tiếp xúc do kiến ba khoang thể kissing lesion đối xứng.',
                         'Viêm da tiếp xúc do độc tố kiến ba khoang có sưng phù mi mắt.',
                         'Viêm da tiếp xúc do kiến ba khoang đợt cấp trợt mủ nông.',
                         'Nghi ngờ viêm da tiếp xúc do kiến ba khoang phân biệt với bệnh zona thần '
                         'kinh.'],
  'bien_the_ke_hoach': ['Rửa sạch vùng tổn thương bằng nước muối sinh lý, bôi dung dịch hồ nước '
                        'hoặc hồ kẽm làm dịu da, bôi kháng sinh tại chỗ chống bội nhiễm.',
                        'Rửa nhẹ nhàng tổn thương dưới vòi nước sạch hoặc nước muối sinh lý trung '
                        'hòa độc tố, bôi hồ nước ngày 2 lần làm dịu mát giảm rát bỏng.',
                        'Chỉ định bôi mỡ kháng sinh fucidin hoặc mupirocin khi mụn mủ dập vỡ trợt '
                        'loét, uống thuốc kháng histamine giảm ngứa châm chích.',
                        'Tuyệt đối dặn dò không chà xát miết nát côn trùng trên da, không chạm tay '
                        'từ vết thương lên mắt, bôi kem corticoid nhẹ khi hết mụn mủ.',
                        'Hướng dẫn vệ sinh nhà cửa đóng kín cửa sổ bật đèn vàng mùa mưa, phun '
                        'thuốc diệt côn trùng, giặt sạch quần áo khăn lau trước khi dùng.',
                        'Kê đơn thuốc kháng sinh đường uống nếu có dấu hiệu viêm tấy lan rộng bội '
                        'nhiễm vi khuẩn, hẹn tái khám sau 3-5 ngày đánh giá khô mài.'],
  'bien_the_kham': ['Tổn thương dạng vệt dài 7cm vùng cổ bên phải, dát đỏ phù nề rải rác mụn mủ li '
                    'ti ở giữa, cảm giác rát buốt nhiều.',
                    'Khám thấy vệt tổn thương viêm đỏ dài ở cẳng tay có tổn thương đối xứng mặt '
                    'đối diện dạng kissing lesion, giữa vệt có bọng mủ nông.',
                    'Vùng da sau gáy có mảng đỏ nề thành dải ngoằn ngoèo, mụn nước nhỏ li ti vỡ '
                    'trợt rỉ dịch, cảm giác bỏng rát như bị tạt axit.',
                    'Ghi nhận tổn thương vệt dài dát đỏ kèm bọng mủ trắng đục thành chuỗi ở mặt '
                    'trong cánh tay, bờ viền hơi gờ nhẹ, hạch lân cận không to.',
                    'Khám cấp tính: vệt da viêm trợt dài 5cm vùng thái dương mắt, bờ đỏ sưng nề '
                    'nhẹ, mí mắt sưng húp do tiếp xúc độc tố qua tay quệt.',
                    'Tổn thương da điển hình do pederin ở vùng ngực cổ, dát đỏ thành đường thẳng '
                    'kèm bọng mủ đầu đinh ghim, cảm giác buốt rát nhức nhối.'],
  'chan_doan': 'Viêm da tiếp xúc do độc tố pederin kiến ba khoang cấp tính.',
  'chinh': ['vệt dát đỏ nền hơi nề chạy dài ngoằn ngoèo thành dải như vết cào quệt',
            'xuất hiện các mụn nước bọng mủ nhỏ li ti xếp thành vệt dọc theo đường dát đỏ',
            'cảm giác bỏng rát châm chích đau rát buốt dữ dội khởi phát đột ngột sau một đêm'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'da liễu',
  'ke_hoach': 'Rửa sạch vùng tổn thương bằng nước muối sinh lý, bôi dung dịch hồ nước hoặc hồ kẽm '
              'làm dịu da, bôi kháng sinh tại chỗ chống bội nhiễm.',
  'kham': 'Tổn thương dạng vệt dài 7cm vùng cổ bên phải, dát đỏ phù nề rải rác mụn mủ li ti ở '
          'giữa, cảm giác rát buốt nhiều.',
  'nhom': 'cả hai',
  'phu': ['tổn thương đối xứng kiểu hôn nhau ở các vùng nếp gấp khuỷu tay nách hoặc cổ',
          'vùng da trợt rỉ dịch vàng mỏng đóng vảy tiết sau vài ngày tiến triển',
          'tiền sử ở khu vực gần đồng ruộng công trường có ánh đèn điện ban đêm mùa mưa'],
  'ten': 'viêm da tiếp xúc do thực vật kiến ba khoang'},
 {'bien_the_chan_doan': ['Bệnh huyết thanh sau tiêm kháng huyết thanh kháng nọc uốn ván.',
                         'Bệnh huyết thanh sau tiêm kháng huyết thanh kháng nọc rắn.',
                         'Theo dõi bệnh huyết thanh quá mẫn type 3 sau tiêm sinh phẩm y tế.',
                         'Bệnh huyết thanh thể viêm đa khớp và sưng hạch toàn thân.',
                         'Phản ứng bệnh huyết thanh cấp tính sau tiêm huyết thanh kháng dại SAR.',
                         'Nghi ngờ bệnh huyết thanh có tổn thương thận lắng đọng phức hợp miễn '
                         'dịch.'],
  'bien_the_ke_hoach': ['Xét nghiệm bổ thể C3 C4 giảm, tổng phân tích nước tiểu, dùng thuốc kháng '
                        'histamine phối hợp corticoid đường uống giảm viêm miễn dịch.',
                        'Chỉ định xét nghiệm nồng độ bổ thể C3, C4, chức năng thận creatinin và '
                        'protein niệu, dùng prednisolone 1mg/kg/ngày giảm liều dần trong 2 tuần.',
                        'Kê đơn thuốc kháng histamine H1 liều cao giảm ngứa và ban mày đay, dùng '
                        'paracetamol hạ sốt giảm đau khớp, truyền dịch bù nước.',
                        'Làm công thức máu tốc độ máu lắng ESR tăng cao, theo dõi sát lượng nước '
                        'tiểu 24 giờ tầm soát viêm cầu thận cấp phức hợp miễn dịch.',
                        'Chỉ định nghỉ ngơi tại giường, dùng NSAID hoặc corticosteroid toàn thân '
                        'kiểm soát viêm khớp và sưng đau hạch, theo dõi đáp ứng lâm sàng.',
                        'Ghi nhận phản ứng dị ứng nghiêm trọng với huyết thanh dị loài vào sổ theo '
                        'dõi tiêm chủng, lập kế hoạch dự phòng cho các lần điều trị sau.'],
  'bien_the_kham': ['Phát ban mày đay dát sẩn ngứa toàn thân, sưng đau nhẹ hai khớp gối, hạch góc '
                    'hàm và nách sưng đau 1-2cm, sốt 38.5 độ C.',
                    'Khám thấy ban đỏ sẩn phù dạng mày đay lan tỏa tứ chi, hai khớp cổ chân sưng '
                    'nóng ấn đau, hạch bẹn hai bên sưng to mềm di động.',
                    'Bệnh nhân sốt 39 độ C sau tiêm huyết thanh uốn ván SAT 8 ngày, mặt phù nhẹ, '
                    'phát ban dát sẩn ngứa rực, khớp cổ tay sưng đau hạn chế gập.',
                    'Tổn thương da dạng mày đay đa hình thái kèm sưng hạch nách và hạch cổ, các '
                    'khớp lớn sưng nề đối xứng, ấn tức dọc cơ bắp toàn thân.',
                    'Ghi nhận phản ứng quá mẫn type 3 sau dùng kháng huyết thanh kháng dại, sốt '
                    'cao rét run, phát ban đỏ ngứa nhiều, nước tiểu vàng sẫm.',
                    'Khám phát hiện ban xuất huyết nhẹ xen kẽ sẩn mày đay ở chi dưới, hạch toàn '
                    'thân to đau, sưng đau hai khớp gối đi lại khập khiễng.'],
  'chan_doan': 'Bệnh huyết thanh sau tiêm kháng huyết thanh kháng nọc uốn ván.',
  'chinh': ['sốt cao dao động kèm nổi ban mày đay dát sẩn ngứa khắp người sau tiêm huyết thanh bảy '
            'ngày',
            'đau nhức sưng nề hạn chế vận động nhiều khớp lớn như khớp cổ chân gối và cổ tay',
            'sưng to đau nhức các chuỗi hạch bạch huyết vùng cổ nách và bẹn toàn thân'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Xét nghiệm bổ thể C3 C4 giảm, tổng phân tích nước tiểu, dùng thuốc kháng histamine '
              'phối hợp corticoid đường uống giảm viêm miễn dịch.',
  'kham': 'Phát ban mày đay dát sẩn ngứa toàn thân, sưng đau nhẹ hai khớp gối, hạch góc hàm và '
          'nách sưng đau 1-2cm, sốt 38.5 độ C.',
  'nhom': 'cả hai',
  'phu': ['sưng phù nề mi mắt bàn tay bàn chân do ứ trệ dịch phức hợp miễn dịch',
          'đau mỏi cơ bắp toàn thân cảm giác kiệt sức mệt lả và nhức đầu',
          'nước tiểu sẫm màu hoặc có bọt nhẹ cảnh báo viêm cầu thận phức hợp'],
  'ten': 'bệnh huyết thanh sau tiêm kháng huyết thanh'},
 {'bien_the_chan_doan': ['Viêm mạch máu nhỏ hoại tử do phức hợp miễn dịch mạn tính.',
                         'Viêm mạch máu nhỏ hoại tử thể ban xuất huyết sờ thấy được palpale '
                         'purpura.',
                         'Bệnh viêm mạch máu nhỏ hoại tử do phức hợp miễn dịch đợt hoạt tính.',
                         'Theo dõi viêm mạch máu nhỏ hoại tử có tổn thương thận phối hợp.',
                         'Viêm mạch máu nhỏ hoại tử da do lắng đọng phức hợp miễn dịch lưu hành.',
                         'Nghi ngờ viêm mạch máu nhỏ hoại tử thứ phát sau nhiễm trùng hoặc tự '
                         'miễn.'],
  'bien_the_ke_hoach': ['Chỉ định sinh thiết da làm miễn dịch huỳnh quang trực tiếp tìm lắng đọng '
                        'IgA IgG quanh mạch, xét nghiệm chức năng thận, điều trị corticosteroid '
                        'toàn thân.',
                        'Làm sinh thiết tổn thương sẩn xuất huyết dưới 24-48 giờ gửi giải phẫu '
                        'bệnh tìm viêm mạch bạch cầu hạt vỡ vụn leukocytoclastic vasculitis.',
                        'Xét nghiệm tổng phân tích nước tiểu tìm hồng cầu niệu và protein niệu, đo '
                        'độ thanh thải creatinin, bắt đầu dùng methylprednisolone đường uống.',
                        'Hướng dẫn nghỉ ngơi tại giường kê cao chi dưới hạn chế đứng lâu, dùng '
                        'thuốc bảo vệ thành mạch và thuốc giảm đau chống viêm.',
                        'Tầm soát bệnh lý hệ thống tiềm ẩn gồm kháng thể kháng nhân ANA, bổ thể C3 '
                        'C4, ANCA, viêm gan B và C, phối hợp colchicine hoặc dapsone.',
                        'Hội chẩn chuyên khoa Miễn dịch Dị ứng lâm sàng, dùng thuốc ức chế miễn '
                        'dịch azathioprine nếu tái phát dai dẳng khi giảm liều corticoid.'],
  'bien_the_kham': ['Nhiều nốt xuất huyết sờ thấy được gờ cao kích thước 2-5mm ở cẳng chân hai '
                    'bên, một số nốt có vảy hoại tử đen trung tâm, ấn kính không mất màu.',
                    'Khám thấy ban xuất huyết sờ gờ cao palpable purpura dày đặc từ mắt cá chân '
                    'lên bắp chân, một vài nốt có bọng xuất huyết và loét nông.',
                    'Hai cẳng chân chi chít các nốt đỏ tím không phai khi ấn ngón tay, sờ thấy sẩn '
                    'cộm rõ, khớp cổ chân sưng nề ấn đau nhẹ.',
                    'Tổn thương viêm mạch da điển hình chi dưới, các sẩn xuất huyết liên kết thành '
                    'mảng kèm trung tâm hoại tử xơ đen, mạch mu chân đập tốt.',
                    'Ghi nhận ban xuất huyết sẩn gờ hai cẳng chân đối xứng, bờ sắc nét, cảm giác '
                    'buốt rát da tăng khi buông thõng chân, phù nhẹ mu bàn chân.',
                    'Khám da thấy nhiều ban xuất huyết dạng chấm và sẩn nổi gờ trên mặt da cẳng '
                    'chân đùi, trung tâm có vảy tiết hoại tử khô màu nâu đen.'],
  'chan_doan': 'Viêm mạch máu nhỏ hoại tử do phức hợp miễn dịch mạn tính.',
  'chinh': ['xuất hiện ban xuất huyết dạng sẩn sờ thấy gờ cao trên mặt da không biến mất khi ấn '
            'kính',
            'tổn thương xuất huyết tập trung dày đặc đối xứng hai bên cẳng chân và bàn chân',
            'các nốt hoại tử loét nông nhỏ màu đen vảy tiết ở trung tâm của ban xuất huyết'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Chỉ định sinh thiết da làm miễn dịch huỳnh quang trực tiếp tìm lắng đọng IgA IgG '
              'quanh mạch, xét nghiệm chức năng thận, điều trị corticosteroid toàn thân.',
  'kham': 'Nhiều nốt xuất huyết sờ thấy được gờ cao kích thước 2-5mm ở cẳng chân hai bên, một số '
          'nốt có vảy hoại tử đen trung tâm, ấn kính không mất màu.',
  'nhom': 'người lớn',
  'phu': ['đau nhức buốt hai cẳng chân tăng lên rõ rệt khi đi lại hoặc đứng lâu',
          'đau âm ỉ các khớp cổ chân khớp bàn ngón chân hai bên nhưng không biến dạng khớp',
          'cảm giác tê bì châm chích đầu ngón chân do tổn thương vi mạch nuôi dây thần kinh'],
  'ten': 'viêm mạch máu nhỏ hoại tử do phức hợp miễn dịch'},
 {'bien_the_chan_doan': ['Hội chứng kháng phospholipid tự miễn thể có huyết khối tái phát.',
                         'Hội chứng kháng phospholipid tự miễn nguyên phát đợt tắc mạch sâu.',
                         'Theo dõi hội chứng kháng phospholipid tự miễn có dấu hiệu livedo '
                         'reticularis.',
                         'Hội chứng kháng phospholipid tự miễn biến chứng huyết khối tĩnh mạch chi '
                         'dưới.',
                         'Bệnh hội chứng kháng phospholipid tự miễn có giảm tiểu cầu miễn dịch.',
                         'Nghi ngờ hội chứng kháng phospholipid tự miễn cần xét nghiệm kháng thể '
                         'khẳng định.'],
  'bien_the_ke_hoach': ['Xét nghiệm bộ ba kháng thể kháng phospholipid gồm lupus anticoagulant, '
                        'anticardiolipin và anti-beta2-glycoprotein I, dùng kháng đông warfarin '
                        'duy trì INR 2-3.',
                        'Chỉ định siêu âm Doppler mạch máu chi dưới chẩn đoán huyết khối tĩnh mạch '
                        'sâu, khởi đầu điều trị chống đông bằng heparin trọng lượng phân tử thấp.',
                        'Làm xét nghiệm kháng thể kháng cardiolipin IgG IgM và lupus anticoagulant '
                        '2 lần cách nhau 12 tuần để xác định tiêu chuẩn Sydney.',
                        'Chuyển sang thuốc chống đông kháng vitamin K warfarin dài hạn kiểm soát '
                        'mục tiêu INR trong khoảng 2.0 - 3.0, theo dõi định kỳ.',
                        'Tư vấn người bệnh tránh bất động kéo dài, không dùng thuốc tránh thai '
                        'chứa estrogen, bảo vệ giữ ấm chi dưới tránh tổn thương da.',
                        'Hội chẩn chuyên khoa Huyết học và Miễn dịch, bổ sung aspirin liều thấp '
                        'nếu có nguy cơ tắc mạch động mạch, xét nghiệm công thức máu kiểm tra tiểu '
                        'cầu.'],
  'bien_the_kham': ['Cẳng chân sưng nề một bên nghi huyết khối tĩnh mạch, da đùi và cánh tay có '
                    'mạng lưới vân tím livedo reticularis lan tỏa.',
                    'Khám thấy bắp chân trái sưng to căng cứng ấn đau sâu, chu vi bắp chân chênh '
                    'lệch 3cm so với chân phải, da thân mình có vân tím mạng nhện.',
                    'Tổn thương da dạng vân lưới tím tái livedo reticularis rõ ở hai đùi và cẳng '
                    'tay khi gặp lạnh, ngón chân có vết loét thiếu máu nhỏ ở đầu ngón.',
                    'Ghi nhận phù căng một bên chi dưới kèm dấu hiệu Homans dương tính, tuần hoàn '
                    'bàng hệ nổi nhẹ nông dưới da, huyết áp 130/80 mmHg.',
                    'Khám lâm sàng phát hiện mạng lưới tím tái loang lổ như rễ cây đối xứng hai '
                    'chi dưới, mạch mu chân đập yếu, không có sốt.',
                    'Bệnh nhân có tiền sử tắc mạch tái diễn, hiện tại cẳng chân phải phù nề ấn lõm '
                    'đau tức, vân tím nổi rõ khi buông chân xuống thấp.'],
  'chan_doan': 'Hội chứng kháng phospholipid tự miễn thể có huyết khối tái phát.',
  'chinh': ['xuất hiện huyết khối tĩnh mạch sâu chi dưới tái phát nhiều lần gây sưng đau chân',
            'da nổi vân tím hình mạng lưới tím tái loang lổ dạng cành cây livedo reticularis',
            'tiền sử các biến cố tắc mạch động mạch đột ngột không rõ nguyên nhân tim mạch'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Xét nghiệm bộ ba kháng thể kháng phospholipid gồm lupus anticoagulant, '
              'anticardiolipin và anti-beta2-glycoprotein I, dùng kháng đông warfarin duy trì INR '
              '2-3.',
  'kham': 'Cẳng chân sưng nề một bên nghi huyết khối tĩnh mạch, da đùi và cánh tay có mạng lưới '
          'vân tím livedo reticularis lan tỏa.',
  'nhom': 'người lớn',
  'phu': ['loét nông hoại tử đầu chi ngón chân do thiếu máu nuôi dưỡng vi mạch kéo dài',
          'đau đầu migraine kéo dài và suy giảm trí nhớ thoáng qua từng đợt',
          'giảm số lượng tiểu cầu mức độ nhẹ đến trung bình trên xét nghiệm máu'],
  'ten': 'hội chứng kháng phospholipid tự miễn'},
 {'bien_the_chan_doan': ['Hội chứng Churg-Strauss u hạt dị ứng viêm mạch EGPA giai đoạn toàn phát.',
                         'Hội chứng Churg-Strauss u hạt dị ứng viêm mạch thể tăng bạch cầu ái toan '
                         'nặng.',
                         'Bệnh u hạt dị ứng viêm mạch EGPA có tổn thương đa dây thần kinh ngoại '
                         'biên.',
                         'Theo dõi hội chứng Churg-Strauss u hạt dị ứng viêm mạch đợt tiến triển '
                         'cấp.',
                         'Hội chứng Churg-Strauss u hạt dị ứng viêm mạch có hen phế quản phụ thuộc '
                         'corticoid.',
                         'Nghi ngờ hội chứng Churg-Strauss u hạt dị ứng viêm mạch p-ANCA dương '
                         'tính.'],
  'bien_the_ke_hoach': ['Xét nghiệm kháng thể p-ANCA, chụp CT ngực độ phân giải cao tìm thâm nhiễm '
                        'phổi, điều trị phối hợp corticosteroid liều cao và cyclophosphamide.',
                        'Làm công thức máu định lượng bạch cầu ái toan tuyệt đối, xét nghiệm kháng '
                        'thể kháng enzym MPO (p-ANCA), dùng methylprednisolone truyền tĩnh mạch.',
                        'Chỉ định chụp HRCT lồng ngực tìm hình ảnh kính mờ hoặc đông đặc phổi '
                        'thoáng qua, đo điện cơ EMG xác định tổn thương đa dây thần kinh đơn độc.',
                        'Điều trị tấn công bằng glucocorticoid liều cao kết hợp cyclophosphamide '
                        'hoặc thuốc sinh học kháng IL-5 mepolizumab, phục hồi chức năng vận động.',
                        'Nội soi tai mũi họng đánh giá polyp mũi xoang, làm siêu âm tim tầm soát '
                        'viêm cơ tim do bạch cầu ái toan, bảo vệ dạ dày bằng thuốc PPI.',
                        'Hội chẩn chuyên khoa Hô hấp và Miễn dịch lâm sàng, theo dõi định kỳ chức '
                        'năng phổi và số lượng bạch cầu ái toan máu ngoại vi.'],
  'bien_the_kham': ['Nghe phổi có ran rít ran ngáy rải rác, liệt cơ nâng bàn chân một bên rủ bàn '
                    'chân, ban xuất huyết sờ thấy được ở cẳng chân.',
                    'Khám thấy bàn chân phải bị rủ không nhấc mũi chân lên được (mononeuritis '
                    'multiplex), phổi nhiều ran rít co thắt, ban xuất huyết ở hai cẳng chân.',
                    'Bệnh nhân khó thở dạng hen phế quản, niêm mạc mũi có polyp che lấp hốc mũi, '
                    'giảm cảm giác nông kiểu mang tất ở hai bàn chân.',
                    'Tổn thương thần kinh ngoại biên không đối xứng kèm yếu cơ cẳng tay trái, nghe '
                    'phổi thông khí giảm kèm ran ngáy, da cẳng chân có nốt viêm mạch.',
                    'Ghi nhận hội chứng viêm mạch hệ thống: hen suyễn nặng, liệt dây thần kinh mác '
                    'chung bên phải, sẩn xuất huyết sờ thấy ở hai chi dưới.',
                    'Khám phổi có tiếng rít thì thở ra, liệt vận động bàn tay dạng bàn tay rủ, sốt '
                    'nhẹ 37.8 độ C, sụt 4kg trong hai tháng gần đây.'],
  'chan_doan': 'Hội chứng Churg-Strauss u hạt dị ứng viêm mạch EGPA giai đoạn toàn phát.',
  'chinh': ['tiền sử hen phế quản nặng dai dẳng khó kiểm soát kèm viêm xoang mũi polyp tái phát',
            'tăng vọt tỷ lệ bạch cầu ái toan trong máu ngoại vi trên mười phần trăm',
            'tổn thương viêm đa dây thần kinh ngoại biên gây tê liệt yếu rủ bàn chân hoặc bàn tay'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Xét nghiệm kháng thể p-ANCA, chụp CT ngực độ phân giải cao tìm thâm nhiễm phổi, '
              'điều trị phối hợp corticosteroid liều cao và cyclophosphamide.',
  'kham': 'Nghe phổi có ran rít ran ngáy rải rác, liệt cơ nâng bàn chân một bên rủ bàn chân, ban '
          'xuất huyết sờ thấy được ở cẳng chân.',
  'nhom': 'người lớn',
  'phu': ['nổi các ban xuất huyết dạng sẩn nốt dưới da ở hai cẳng chân',
          'sốt sụt cân mệt mỏi suy kiệt cơ thể kéo dài nhiều tháng',
          'đau nhức cơ bắp dữ dội và đau các khớp lớn di chuyển không cố định'],
  'ten': 'hội chứng Churg-Strauss u hạt dị ứng viêm mạch'},
 {'bien_the_chan_doan': ['Bệnh u hạt Wegener viêm đa mạch GPA tổn thương tai mũi họng và phổi.',
                         'Bệnh u hạt Wegener viêm đa mạch GPA thể hô hấp thận phối hợp.',
                         'Theo dõi bệnh u hạt Wegener viêm đa mạch GPA giai đoạn hoạt tính cấp.',
                         'Bệnh u hạt Wegener viêm đa mạch GPA c-ANCA kháng thể PR3 dương tính.',
                         'Viêm đa mạch u hạt Wegener GPA biến chứng suy thận tiến triển nhanh.',
                         'Nghi ngờ bệnh u hạt Wegener viêm đa mạch GPA có tổn thương u hạt hốc '
                         'mắt.'],
  'bien_the_ke_hoach': ['Xét nghiệm c-ANCA kháng PR3 dương tính cao, chụp CT xoang và lồng ngực, '
                        'phác đồ tấn công bằng rituximab hoặc cyclophosphamide kết hợp '
                        'glucocorticoid.',
                        'Chỉ định định lượng kháng thể c-ANCA (anti-proteinase 3), chụp cắt lớp vi '
                        'tính lồng ngực HRCT tìm nốt tổn thương tạo hang nhu mô phổi.',
                        'Làm sinh thiết niêm mạc mũi hoặc sinh thiết phổi khẳng định u hạt hoại tử '
                        'và viêm mạch, xét nghiệm creatinin máu và protein niệu 24 giờ.',
                        'Điều trị tấn công bằng truyền tĩnh mạch rituximab 375mg/m2 mỗi tuần trong '
                        '4 tuần phối hợp methylprednisolone liều xung, bảo vệ niêm mạc dạ dày.',
                        'Chỉ định phác đồ cyclophosphamide phối hợp corticoid liều cao đường uống, '
                        'dự phòng viêm phổi do Pneumocystis jirovecii bằng cotrimoxazole.',
                        'Hội chẩn đa chuyên khoa Miễn dịch, Thận học và Hô hấp, theo dõi sát chức '
                        'năng lọc cầu thận và hiệu giá kháng thể c-ANCA trong quá trình điều trị.'],
  'bien_the_kham': ['Niêm mạc hốc mũi trợt loét đóng vảy mủ khô, vách ngăn thủng nhẹ gãy sụp sống '
                    'mũi yên ngựa, nghe phổi rải rác ran nổ đáy.',
                    'Khám tai mũi họng thấy loét thủng vách ngăn mũi, sống mũi sụp dạng yên ngựa '
                    'điển hình, nghe phổi có ran nổ rải rác thùy giữa.',
                    'Tổn thương u hạt hoại tử đường thở trên: chảy máu mũi mủ hôi kéo dài, ho khạc '
                    'đờm lẫn máu đỏ tươi, phù nhẹ hai mi mắt.',
                    'Khám thấy loét sâu vòm họng và niêm mạc cuốn mũi dưới, nghe phổi rì rào phế '
                    'nang giảm có tiếng cọ màng phổi, huyết áp 140/90 mmHg.',
                    'Ghi nhận viêm đa mạch dạng u hạt: sưng đau quanh hốc mắt gây lồi mắt một bên, '
                    'sống mũi biến dạng sụp lõm, tiểu ít sẫm màu.',
                    'Tổn thương đường hô hấp trên và dưới kết hợp: loét niêm mạc mũi đóng vảy mủ '
                    'nâu đen, ran nổ hai đáy phổi, phù mắt cá chân ấn lõm.'],
  'chan_doan': 'Bệnh u hạt Wegener viêm đa mạch GPA tổn thương tai mũi họng và phổi.',
  'chinh': ['loét hoại tử niêm mạc mũi họng mạn tính chảy mủ lẫn máu hình thành mũi biến dạng yên '
            'ngựa',
            'ho ra máu đau ngực khó thở do các nốt u hạt hoại tử tạo hang trong nhu mô phổi',
            'viêm cầu thận tiến triển nhanh biểu hiện phù tiểu ít và nước tiểu có protein máu'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Xét nghiệm c-ANCA kháng PR3 dương tính cao, chụp CT xoang và lồng ngực, phác đồ tấn '
              'công bằng rituximab hoặc cyclophosphamide kết hợp glucocorticoid.',
  'kham': 'Niêm mạc hốc mũi trợt loét đóng vảy mủ khô, vách ngăn thủng nhẹ gãy sụp sống mũi yên '
          'ngựa, nghe phổi rải rác ran nổ đáy.',
  'nhom': 'người lớn',
  'phu': ['viêm tai giữa thanh dịch tái phát giảm thính lực ù tai kéo dài',
          'sốt dai dẳng về chiều mệt mỏi sụt cân suy kiệt cơ thể rõ rệt',
          'đau nhức quanh hốc mắt lồi mắt do khối u hạt viêm sau nhãn cầu'],
  'ten': 'bệnh u hạt Wegener viêm đa mạch GPA'},
 {'bien_the_chan_doan': ['Viêm động mạch tế bào khổng lồ thái dương Horton cấp tính nguy cơ mất '
                         'thị lực.',
                         'Viêm động mạch tế bào khổng lồ thái dương Horton thể có biến chứng thị '
                         'giác cấp.',
                         'Theo dõi bệnh viêm động mạch tế bào khổng lồ thái dương Horton kết hợp '
                         'đau đa cơ do thấp.',
                         'Viêm động mạch tế bào khổng lồ thái dương Horton đợt bùng phát tốc độ '
                         'lắng máu cao.',
                         'Bệnh Horton viêm động mạch tế bào khổng lồ ở người cao tuổi thể thái '
                         'dương một bên.',
                         'Nghi ngờ viêm động mạch tế bào khổng lồ thái dương Horton cần sinh thiết '
                         'khẩn cấp.'],
  'bien_the_ke_hoach': ['Đo tốc độ máu lắng ESR và CRP tăng rất cao, chỉ định sinh thiết động mạch '
                        'thái dương, bắt đầu ngay methylprednisolone liều cao khẩn cấp để bảo vệ '
                        'thị lực.',
                        'Khởi động ngay truyền tĩnh mạch methylprednisolone 500mg-1000mg/ngày '
                        'trong 3 ngày cấp cứu bảo tồn thị giác, không trì hoãn chờ kết quả sinh '
                        'thiết.',
                        'Làm xét nghiệm tốc độ máu lắng ESR thường trên 50-100 mm/h và protein C '
                        'phản ứng CRP, sắp xếp phẫu thuật sinh thiết động mạch thái dương đoạn dài '
                        '2cm.',
                        'Chỉ định siêu âm Doppler mạch máu thái dương tìm dấu hiệu vòng hào quang '
                        'halo sign đặc trưng, chuyển khám chuyên khoa Mắt khẩn.',
                        'Chuyển sang prednisolone đường uống 1mg/kg/ngày sau liệu pháp xung '
                        'corticoid, bổ sung canxi vitamin D và thuốc bảo vệ niêm mạc dạ dày.',
                        'Hội chẩn chuyên khoa Miễn dịch lâm sàng xem xét dùng kháng thể kháng thụ '
                        'thể IL-6 tocilizumab hỗ trợ giảm phụ thuộc liều corticoid kéo dài.'],
  'bien_the_kham': ['Động mạch thái dương nông bên phải phồng to, sờ như sợi dây thừng cứng chắc '
                    'ấn rất đau, mạch đập giảm rõ, da phía trên đỏ sẫm.',
                    'Khám thấy nhánh trán của động mạch thái dương gồ cứng nổi ngoằn ngoèo ấn đau '
                    'buốt nhói, mất hoàn toàn sóng mạch đập khi bắt tay.',
                    'Đau chói khi chạm nhẹ vào da đầu vùng thái dương bên trái, cơ nhai mỏi cứng '
                    'khi há miệng khám, thị lực mắt trái giảm nhìn mờ như qua sương.',
                    'Động mạch thái dương hai bên sưng nề dày cứng như sợi bấc, da bao phủ căng '
                    'bóng đỏ tía, hạn chế nâng cánh tay do đau đa cơ vùng vai.',
                    'Khám phát hiện động mạch thái dương xơ cứng ấn đau dữ dội, soi đáy mắt có dấu '
                    'hiệu thiếu máu cục bộ đĩa thị trước cấp tính dọa teo gai.',
                    'Ghi nhận hội chứng Horton điển hình: động mạch thái dương sưng cứng mất mạch, '
                    'nghiệm pháp nhai mỏi hàm dương tính, sốt nhẹ 37.9 độ C.'],
  'chan_doan': 'Viêm động mạch tế bào khổng lồ thái dương Horton cấp tính nguy cơ mất thị lực.',
  'chinh': ['đau nhức nửa đầu vùng thái dương dữ dội dai dẳng như búa bổ không đáp ứng giảm đau',
            'động mạch thái dương nông sưng to nổi ngoằn ngoèo cứng chắc ấn đau chói và mất mạch '
            'đập',
            'dấu hiệu đau cách hồi cơ nhai mỏi hàm cứng hàm khi nhai thức ăn hoặc nói chuyện'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Đo tốc độ máu lắng ESR và CRP tăng rất cao, chỉ định sinh thiết động mạch thái '
              'dương, bắt đầu ngay methylprednisolone liều cao khẩn cấp để bảo vệ thị lực.',
  'kham': 'Động mạch thái dương nông bên phải phồng to, sờ như sợi dây thừng cứng chắc ấn rất đau, '
          'mạch đập giảm rõ, da phía trên đỏ sẫm.',
  'nhom': 'người lớn',
  'phu': ['nhìn mờ nhìn đôi thoáng qua hoặc mất thị lực đột ngột một bên mắt dọa mù vĩnh viễn',
          'đau mỏi cứng các cơ vùng vai gáy và khớp háng vào buổi sáng kiểu đau đa cơ do thấp',
          'sốt nhẹ gầy sút cân suy kiệt cơ thể ở người trên năm mươi tuổi'],
  'ten': 'viêm động mạch tế bào khổng lồ thái dương Horton'},
 {'bien_the_chan_doan': ['Viêm động mạch Takayasu không có mạch type một tổn thương quai động mạch '
                         'chủ.',
                         'Viêm động mạch Takayasu không có mạch giai đoạn hoạt tính viêm mạch lớn.',
                         'Bệnh Takayasu viêm động mạch không có mạch có hẹp nhánh động mạch dưới '
                         'đòn.',
                         'Theo dõi viêm động mạch Takayasu không có mạch có tăng huyết áp thứ '
                         'phát.',
                         'Viêm động mạch Takayasu không có mạch thể tổn thương lan tỏa toàn bộ '
                         'động mạch chủ.',
                         'Nghi ngờ viêm động mạch Takayasu không có mạch gây hội chứng cướp máu '
                         'động mạch dưới đòn.'],
  'bien_the_ke_hoach': ['Chỉ định chụp cắt lớp vi tính mạch máu CTA hoặc MRA toàn bộ quai động '
                        'mạch chủ và các nhánh lớn, điều trị ức chế miễn dịch bằng corticosteroid '
                        'và methotrexate.',
                        'Chụp cộng hưởng từ mạch máu MRA ngực bụng đánh giá mức độ dày thành mạch '
                        'và hẹp tắc các nhánh lớn, xét nghiệm tốc độ máu lắng ESR và CRP.',
                        'Khởi đầu điều trị tấn công bằng prednisone 1mg/kg/ngày kết hợp '
                        'methotrexate 15-20mg mỗi tuần kiểm soát tiến trình viêm xơ hẹp động mạch.',
                        'Hội chẩn chuyên khoa Tim mạch can thiệp và Ngoại Tim mạch lồng ngực đánh '
                        'giá chỉ định đặt stent hoặc bắc cầu mạch máu khi tình trạng viêm đã ổn '
                        'định.',
                        'Kê đơn thuốc kiểm soát huyết áp thích hợp và aspirin liều thấp dự phòng '
                        'huyết khối tắc mạch, theo dõi định kỳ kích thước lòng mạch trên siêu âm '
                        'Doppler.',
                        'Chỉ định dùng thuốc sinh học kháng TNF-alpha hoặc tocilizumab nếu bệnh '
                        'không đáp ứng với phác đồ ức chế miễn dịch kinh điển, theo dõi sát nhịp '
                        'tim.'],
  'bien_the_kham': ['Mạch quay tay trái không bắt được, huyết áp tay phải 135/85 mmHg trong khi '
                    'tay trái chỉ đo được 85/50 mmHg, tiếng thổi tâm thu rõ vùng cổ dưới đòn trái.',
                    'Mạch quay hai tay đập rất yếu mất đối xứng, chênh lệch huyết áp hai cánh tay '
                    '25 mmHg, nghe tiếng thổi mạch máu ở hố thượng đòn hai bên.',
                    'Khám thấy cánh tay trái lạnh nhạt màu khi giơ cao, mạch quay và mạch cánh tay '
                    'trái không sờ thấy, tiếng thổi tâm thu rõ vùng động mạch cảnh phải.',
                    'Huyết áp tay phải 150/90 mmHg (tăng huyết áp thứ phát do hẹp động mạch thận), '
                    'huyết áp tay trái không đo được, nghe tiếng thổi tâm thu ở bụng.',
                    'Ghi nhận hội chứng mất mạch bệnh Takayasu điển hình ở nữ trẻ tuổi, mạch cảnh '
                    'đập yếu bên trái, hoa mắt chóng mặt khi đứng dậy.',
                    'Khám mạch ngoại vi phát hiện mất mạch quay bên phải, mạch bẹn bắt rõ, nghe '
                    'thổi tâm thu liên tục ở vùng dưới đòn trái và quai động mạch chủ.'],
  'chan_doan': 'Viêm động mạch Takayasu không có mạch type một tổn thương quai động mạch chủ.',
  'chinh': ['mất mạch hoặc mạch đập rất yếu không đều ở một hoặc cả hai tay',
            'chênh lệch huyết áp đo giữa hai tay trên mười đến hai mươi milimét thủy ngân',
            'nghe thấy tiếng thổi tâm thu bất thường tại động mạch dưới đòn hoặc động mạch cảnh'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'tim mạch',
  'ke_hoach': 'Chỉ định chụp cắt lớp vi tính mạch máu CTA hoặc MRA toàn bộ quai động mạch chủ và '
              'các nhánh lớn, điều trị ức chế miễn dịch bằng corticosteroid và methotrexate.',
  'kham': 'Mạch quay tay trái không bắt được, huyết áp tay phải 135/85 mmHg trong khi tay trái chỉ '
          'đo được 85/50 mmHg, tiếng thổi tâm thu rõ vùng cổ dưới đòn trái.',
  'nhom': 'người lớn',
  'phu': ['đau mỏi yếu hai cánh tay tăng lên khi làm việc hoặc đưa tay lên cao',
          'chóng mặt hoa mắt ngất xỉu khi thay đổi tư thế do thiếu máu não từng cơn',
          'sốt nhẹ kéo dài đau mỏi các khớp và sụt cân không rõ nguyên nhân giai đoạn đầu'],
  'ten': 'viêm động mạch Takayasu không có mạch'},
 {'bien_the_chan_doan': ['Ngộ độc paracetamol giai đoạn sớm tại nhà trong 8 giờ đầu.',
                         'Ngộ độc paracetamol cấp tính giai đoạn một nguy cơ hoại tử gan.',
                         'Theo dõi ngộ độc paracetamol do uống quá liều cấp tính.',
                         'Ngộ độc paracetamol giai đoạn sớm tại nhà giờ thứ 4 có nôn ói.',
                         'Bệnh ngộ độc paracetamol cấp tính có chỉ định dùng thuốc giải độc '
                         'N-acetylcysteine.',
                         'Nghi ngờ ngộ độc paracetamol liều độc trên người có yếu tố nguy cơ gan.'],
  'bien_the_ke_hoach': ['Định lượng nồng độ paracetamol máu đối chiếu đồ thị Rumack-Matthew, dùng '
                        'ngay thuốc giải độc đặc hiệu N-acetylcysteine NAC đường uống hoặc truyền '
                        'tĩnh mạch.',
                        'Rửa dạ dày nếu đến trước 2 giờ kèm cho uống than hoạt 1g/kg kết hợp '
                        'sorbitol, truyền tĩnh mạch ngay N-acetylcysteine theo phác đồ chuẩn 3 gói '
                        '21 giờ.',
                        'Lấy máu định lượng nồng độ paracetamol huyết tương tại thời điểm sau 4 '
                        'giờ, xét nghiệm men gan AST ALT, đông máu cơ bản PT INR và bilirubin.',
                        'Bắt đầu ngay phác đồ truyền tĩnh mạch NAC liều nạp 150mg/kg trong 1 giờ '
                        'đầu, theo dõi sát điện tâm đồ và chức năng đông máu.',
                        'Hướng dẫn theo dõi men gan mỗi 12-24 giờ để đánh giá mức độ tổn thương tế '
                        'bào gan, hội chẩn chuyên khoa Chống độc và Hồi sức cấp cứu.',
                        'Chăm sóc tâm lý hỗ trợ người bệnh, kiểm tra độc chất nước tiểu tầm soát '
                        'các chất ngộ độc phối hợp, bồi phụ nước điện giải qua đường truyền.'],
  'bien_the_kham': ['Người bệnh tỉnh tiếp xúc được, da niêm mạc nhợt vã mồ hôi, bụng mềm ấn tức '
                    'nhẹ vùng thượng vị, chưa có dấu hiệu suy gan.',
                    'Bệnh nhân tỉnh táo nhưng lo âu vã mồ hôi trán, nôn 3 lần ra dịch thức ăn '
                    'chua, bụng mềm không chướng không điểm đau khu trú, mạch 92 l/p.',
                    'Khám cấp cứu giờ thứ tư sau uống 20 viên paracetamol 500mg: thể trạng nhợt '
                    'nhạt mệt mỏi, niêm mạc mắt không vàng, gan lách không sờ thấy.',
                    'Dấu hiệu sinh tồn ổn định, da ẩm lạnh vã mồ hôi nhiều, cảm giác buồn nôn liên '
                    'tục, ấn tức nhẹ hạ sườn phải và thượng vị, tri giác hoàn toàn tỉnh táo.',
                    'Ghi nhận ngộ độc thuốc hạ sốt giảm đau giờ thứ 5: bệnh nhân bứt rứt, niêm mạc '
                    'hồng nhạt, tim đều rõ, bụng mềm, không có xuất huyết dưới da.',
                    'Khám lâm sàng chưa phát hiện triệu chứng hoại tử tế bào gan cấp, đồng tử hai '
                    'bên co giãn bình thường, phản xạ nuốt tốt, mạch 88 l/p HA 110/70 mmHg.'],
  'chan_doan': 'Ngộ độc paracetamol giai đoạn sớm tại nhà trong 8 giờ đầu.',
  'chinh': ['tiền sử uống một lượng lớn thuốc paracetamol vượt quá mười gam trong một lần',
            'buồn nôn nôn mửa liên tục ra thức ăn dịch tiêu hóa ngay trong những giờ đầu',
            'vã mồ hôi nhợt nhạt mệt lả khó chịu vùng thượng vị sau khi uống thuốc vài giờ'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'tiêu hoá',
  'ke_hoach': 'Định lượng nồng độ paracetamol máu đối chiếu đồ thị Rumack-Matthew, dùng ngay thuốc '
              'giải độc đặc hiệu N-acetylcysteine NAC đường uống hoặc truyền tĩnh mạch.',
  'kham': 'Người bệnh tỉnh tiếp xúc được, da niêm mạc nhợt vã mồ hôi, bụng mềm ấn tức nhẹ vùng '
          'thượng vị, chưa có dấu hiệu suy gan.',
  'nhom': 'cả hai',
  'phu': ['cảm giác chán ăn đắng miệng bồn chồn lo lắng bất an',
          'chưa có biểu hiện vàng da vàng mắt hay đau hạ sườn phải trong giai đoạn sớm này',
          'tâm lý hoảng sợ sau khi uống thuốc với mục đích tự hại hoặc do nhầm lẫn'],
  'ten': 'ngộ độc paracetamol giai đoạn sớm tại nhà'},
 {'bien_the_chan_doan': ['Ngộ độc nấm độc chứa độc tố amanita phalloides giai đoạn tiêu hóa cấp.',
                         'Ngộ độc nấm độc chứa độc tố amanita phalloides có sốc giảm thể tích tuần '
                         'hoàn.',
                         'Theo dõi ngộ độc nấm độc chứa độc tố amanita nguy cơ suy gan thận bùng '
                         'phát.',
                         'Ngộ độc nấm rừng amatoxin giai đoạn một mất nước điện giải nặng.',
                         'Cấp cứu ngộ độc nấm độc chứa độc tố amanita phalloides thể khởi phát '
                         'muộn.',
                         'Nghi ngờ ngộ độc nấm độc chứa độc tố amanita ở nhóm người cùng ăn nấm '
                         'rừng.'],
  'bien_the_ke_hoach': ['Hồi sức truyền bù dịch thể tích lớn và cân bằng điện giải, dùng than hoạt '
                        'đa liều kết hợp thuốc bảo vệ gan silibinin hoặc benzylpenicillin liều '
                        'cao, chuẩn bị lọc máu.',
                        'Lập 2 đường truyền tĩnh mạch lớn truyền dung dịch Ringer Lactate và NaCl '
                        '0.9% tốc độ cao chống sốc, đặt sonde tiểu theo dõi lượng nước tiểu từng '
                        'giờ.',
                        'Chỉ định than hoạt đa liều 20g mỗi 4 giờ qua sonde dạ dày nhằm cắt chu kỳ '
                        'gan ruột của amatoxin, dùng silibinin truyền tĩnh mạch liều cao giải độc '
                        'gan.',
                        'Xét nghiệm khẩn men gan AST ALT, chức năng đông máu PT INR, khí máu động '
                        'mạch, điện giải đồ kiểm soát hạ kali và toan chuyển hóa.',
                        'Hội chẩn Trung tâm Chống độc quốc gia, chuẩn bị phương án lọc máu hấp phụ '
                        'than hoạt hoặc thay huyết tương sớm loại bỏ độc tố trong máu.',
                        'Dùng benzylpenicillin tĩnh mạch liều cao cạnh tranh thụ thể vận chuyển '
                        'amatoxin tại màng tế bào gan, theo dõi sát đường huyết tránh tụt đường '
                        'máu.'],
  'bien_the_kham': ['Dấu hiệu mất nước nặng: mắt trũng sâu véo da mất chậm, môi khô nứt, mạch '
                    'nhanh 120 l/p huyết áp tụt 85/55 mmHg, bụng co cứng nhẹ toàn thể.',
                    'Bệnh nhân lơ mơ mệt lả vì mất nước ồ ạt, nôn ra dịch mật vàng xanh, tiêu chảy '
                    'phân toàn nước đục bốc mùi tanh chua, huyết áp tụt 80/50 mmHg.',
                    'Khám thấy tình trạng trụy mạch do mất nước cấp sau ăn nấm độc rừng 8 tiếng, '
                    'môi se khô nứt nẻ, mạch nhanh nhỏ khó bắt, chuột rút đau quặn hai bắp chân.',
                    'Bụng ấn đau tức quanh rốn co thắt từng cơn dồn dập, tiếng nhu động ruột tăng '
                    'vọt, mắt trũng sâu tròng đen trơ trọi, da tái nhợt ẩm lạnh.',
                    'Ghi nhận ngộ độc nấm rừng amatoxin: sốc giảm thể tích tuần hoàn nặng, da niêm '
                    'khô xác, lượng nước tiểu dưới 20ml/giờ, tri giác lú lẫn kích thích.',
                    'Khám cấp cứu tiêu hóa: nôn mửa liên tục kèm đi ngoài tóe nước trên 15 lần '
                    'trong ngày, bụng chướng nhẹ ấn đau lan tỏa, mạch 118 l/p HA kẹp 90/65 mmHg.'],
  'chan_doan': 'Ngộ độc nấm độc chứa độc tố amanita phalloides giai đoạn tiêu hóa cấp.',
  'chinh': ['đau quặn bụng dữ dội nôn ói thốc tháo và tiêu chảy xối xả như tháo cống',
            'triệu chứng khởi phát muộn sau sáu đến mười hai giờ tính từ lúc ăn nấm rừng tự hái',
            'mất nước điện giải trầm trọng tụt huyết áp trụy mạch và chuột rút bắp chân'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'tiêu hoá',
  'ke_hoach': 'Hồi sức truyền bù dịch thể tích lớn và cân bằng điện giải, dùng than hoạt đa liều '
              'kết hợp thuốc bảo vệ gan silibinin hoặc benzylpenicillin liều cao, chuẩn bị lọc '
              'máu.',
  'kham': 'Dấu hiệu mất nước nặng: mắt trũng sâu véo da mất chậm, môi khô nứt, mạch nhanh 120 l/p '
          'huyết áp tụt 85/55 mmHg, bụng co cứng nhẹ toàn thể.',
  'nhom': 'cả hai',
  'phu': ['mệt lả kiệt sức khát nước cháy cổ miệng khô khốc',
          'giai đoạn tạm lắng giả tạo sau một ngày trước khi bước vào suy gan thận cấp',
          'hoa mắt chóng mặt nước tiểu ít sẫm màu dần do thiếu thể tích tuần hoàn'],
  'ten': 'ngộ độc nấm độc chứa độc tố amanita'},
 {'bien_the_chan_doan': ['Ngộ độc rượu cồn công nghiệp methanol nhẹ có tổn thương thần kinh thị '
                         'giác.',
                         'Ngộ độc rượu cồn công nghiệp methanol cấp tính thể có toan chuyển hóa.',
                         'Theo dõi ngộ độc rượu cồn công nghiệp methanol sau uống rượu nấu giả.',
                         'Ngộ độc rượu cồn công nghiệp methanol có nguy cơ teo gai thị vĩnh viễn.',
                         'Cấp cứu ngộ độc rượu cồn công nghiệp methanol giai đoạn toàn phát.',
                         'Nghi ngờ ngộ độc rượu cồn công nghiệp methanol có khoảng trống anion và '
                         'áp lực thẩm thấu tăng cao.'],
  'bien_the_ke_hoach': ['Làm khí máu động mạch đánh giá toan chuyển hóa khoảng trống anion, định '
                        'lượng nồng độ methanol máu, dùng ethanol đường uống hoặc fomepizole giải '
                        'độc, lọc máu ngắt quãng.',
                        'Khẩn trương làm khí máu động mạch kiểm tra pH máu và HCO3-, bù natri '
                        'bicarbonat 1.4% tĩnh mạch điều chỉnh toan chuyển hóa máu.',
                        'Dùng chất đối kháng cạnh tranh enzym alcohol dehydrogenase bằng '
                        'fomepizole hoặc dung dịch rượu ethanol 20% qua sonde dạ dày duy trì nồng '
                        'độ 100-150 mg/dl.',
                        'Chỉ định lọc máu ngắt quãng hemodialysis khẩn cấp để đào thải methanol và '
                        'acid formic bảo vệ thần kinh thị giác không bị teo mù vĩnh viễn.',
                        'Bổ sung acid folinic (leucovorin) 50mg tiêm tĩnh mạch mỗi 4 giờ thúc đẩy '
                        'chuyển hóa format thành CO2 và nước, bảo vệ tế bào võng mạc.',
                        'Chuyển ngay bệnh nhân đến khoa Hồi sức tích cực Chống độc, theo dõi sát '
                        'thị lực và nồng độ methanol máu định kỳ 4 giờ một lần.'],
  'bien_the_kham': ['Thị lực giảm nặng hai mắt, đồng tử giãn nhẹ phản xạ ánh sáng chậm, thở nhanh '
                    '26 l/p mùi cồn, bụng mềm không đau khu trú.',
                    'Bệnh nhân than phiền nhìn thấy cảnh vật như đang trong cơn bão tuyết trắng '
                    'xóa, thị lực đếm ngón tay 2 mét, đồng tử giãn 4mm kém phản xạ.',
                    'Khám mắt thấy gai thị phù nề sung huyết nhẹ trên soi đáy mắt, thở nhanh kiểu '
                    'Kussmaul 28 l/p, hơi thở nồng nặc mùi cồn este lạ.',
                    'Tri giác lơ mơ kích thích, thị lực hai mắt giảm nhanh đột ngột sau chầu rượu '
                    'trôi nổi 24 giờ, huyết áp 140/90 mmHg, mạch 96 l/p.',
                    'Ghi nhận tổn thương dây thần kinh thị giác hai bên do cồn methanol: đồng tử '
                    'giãn mất phản xạ ánh sáng trực tiếp, thở sâu toan hóa máu.',
                    'Khám lâm sàng phát hiện ám điểm trung tâm rộng hai mắt, nhức đầu vùng trán dữ '
                    'dội, buồn nôn nhiều, không có dấu hiệu liệt thần kinh khu trú.'],
  'chan_doan': 'Ngộ độc rượu cồn công nghiệp methanol nhẹ có tổn thương thần kinh thị giác.',
  'chinh': ['rối loạn thị giác nhìn mờ như có màn sương mù hoặc mây trắng phủ trước mắt',
            'nhìn thấy quầng sáng chói quanh các nguồn sáng và thu hẹp thị trường thị lực',
            'tiền sử uống rượu không rõ nguồn gốc rượu trắng pha cồn công nghiệp giá rẻ một ngày '
            'trước'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'mắt',
  'ke_hoach': 'Làm khí máu động mạch đánh giá toan chuyển hóa khoảng trống anion, định lượng nồng '
              'độ methanol máu, dùng ethanol đường uống hoặc fomepizole giải độc, lọc máu ngắt '
              'quãng.',
  'kham': 'Thị lực giảm nặng hai mắt, đồng tử giãn nhẹ phản xạ ánh sáng chậm, thở nhanh 26 l/p mùi '
          'cồn, bụng mềm không đau khu trú.',
  'nhom': 'người lớn',
  'phu': ['đau nhức đầu dữ dội chóng mặt buồn nôn và nôn ói ra dịch tiêu hóa',
          'thở nhanh sâu kiểu toan chuyển hóa do tích tụ nồng độ axit formic cao',
          'mệt mỏi lơ mơ li bì bứt rứt không tỉnh táo như say rượu kéo dài'],
  'ten': 'ngộ độc rượu cồn công nghiệp methanol nhẹ'},
 {'bien_the_chan_doan': ['Ngộ độc khí than CO mạn tính thể nhẹ do sinh hoạt trong môi trường thông '
                         'khí kém.',
                         'Ngộ độc khí than CO mạn tính thể nhẹ ở công nhân tiếp xúc khí thải lò '
                         'đốt.',
                         'Theo dõi ngộ độc khí than CO mạn tính thể nhẹ gây hội chứng suy nhược '
                         'thần kinh.',
                         'Ngộ độc khí than CO mạn tính thể nhẹ tích lũy carboxyhemoglobin.',
                         'Bệnh ngộ độc khí than CO mạn tính thể nhẹ ở các thành viên trong gia '
                         'đình dùng bếp than.',
                         'Nghi ngờ ngộ độc khí than CO mạn tính thể nhẹ phân biệt với đau đầu căng '
                         'thẳng mạn tính.'],
  'bien_the_ke_hoach': ['Đo nồng độ carboxyhemoglobin COHb trong máu động mạch, thở oxy lưu lượng '
                        'cao qua mask có túi dự trữ, hướng dẫn dừng ngay việc đốt than trong nhà '
                        'kín.',
                        'Chỉ định đo khí máu động mạch đo quang phổ co-oximetry xác định tỷ lệ '
                        'COHb, cho thở oxy 100% qua mặt nạ có túi thở lại trong 4-6 giờ.',
                        'Tư vấn giải thích nguy cơ ngộ độc khí CO không màu không mùi, nghiêm cấm '
                        'tuyệt đối đốt than củi than tổ ong sưởi ấm trong phòng ngủ đóng kín.',
                        'Chỉ định chụp MRI sọ não nếu có biểu hiện sa sút trí nhớ kéo dài loại trừ '
                        'tổn thương hoại tử nhân bèo thể chai muộn.',
                        'Kê đơn thuốc tăng cường tuần hoàn não hỗ trợ chuyển hóa tế bào thần kinh, '
                        'hướng dẫn mở toang cửa sổ thông gió nơi làm việc và sinh hoạt.',
                        'Lập kế hoạch tái khám đánh giá lại nồng độ COHb và chức năng thần kinh '
                        'nhận thức sau 1 tháng ngừng hoàn toàn tiếp xúc nguồn khí than.'],
  'bien_the_kham': ['Niêm mạc hồng hào không tái, khám thần kinh không có liệt định khu, test trí '
                    'nhớ ngắn hạn giảm chú ý, tim phổi bình thường.',
                    'Khám thấy da niêm mạc bình thường không tím, bệnh nhân chóng mặt khi thay đổi '
                    'tư thế, nghiệm pháp Romberg lảo đảo nhẹ, tim đều 80 l/p.',
                    'Bệnh nhân phàn nàn đau đầu kiểu căng siết hai bên thái dương kéo dài nhiều '
                    'tuần mùa đông, SpO2 đầu ngón 99% nhưng đo khí máu COHb tăng 8%.',
                    'Khám thần kinh nhận thức thấy giảm tốc độ xử lý thông tin và giảm trí nhớ '
                    'thao tác, trương lực cơ bình thường, phản xạ gân xương đều hai bên.',
                    'Ghi nhận tình trạng đau đầu buồn nôn mạn tính ở người bán hàng dùng bếp than '
                    'tổ ong khép kín, niêm mạc miệng hơi đỏ hồng hơn bình thường.',
                    'Khám toàn diện không phát hiện bệnh lý nội thần kinh khu trú, người bệnh mệt '
                    'mỏi suy nhược, nhịp tim bình thường, huyết áp 110/70 mmHg.'],
  'chan_doan': 'Ngộ độc khí than CO mạn tính thể nhẹ do sinh hoạt trong môi trường thông khí kém.',
  'chinh': ['đau đầu âm ỉ liên tục cảm giác nặng đầu như bị vòng đai siết chặt quanh trán',
            'chóng mặt hoa mắt buồn nôn cảm giác choáng váng khi đứng dậy',
            'tiền sử thường xuyên đốt lò than tổ ong sưởi ấm hoặc nấu nướng trong phòng kín thông '
            'khí kém'],
  'da_duyet': False,
  'dien_tien': 'mạn',
  'he_co_quan': 'thần kinh',
  'ke_hoach': 'Đo nồng độ carboxyhemoglobin COHb trong máu động mạch, thở oxy lưu lượng cao qua '
              'mask có túi dự trữ, hướng dẫn dừng ngay việc đốt than trong nhà kín.',
  'kham': 'Niêm mạc hồng hào không tái, khám thần kinh không có liệt định khu, test trí nhớ ngắn '
          'hạn giảm chú ý, tim phổi bình thường.',
  'nhom': 'cả hai',
  'phu': ['suy giảm trí nhớ hay quên mất tập trung chú ý và khó tiếp thu công việc',
          'mệt mỏi mạn tính uể oải đau mỏi cơ bắp toàn thân ngủ không sâu giấc',
          'các thành viên cùng sống chung trong gia đình đều có triệu chứng đau đầu tương tự'],
  'ten': 'ngộ độc khí than CO mạn tính thể nhẹ'},
 {'bien_the_chan_doan': ['Ong đốt nhiều nốt nhiễm độc nọc ong nhẹ chưa có biến chứng tiêu cơ vân.',
                         'Ong đốt nhiều nốt nhiễm độc nọc ong thể viêm mô mềm sưng nề tại chỗ.',
                         'Theo dõi ong đốt nhiều nốt nghi nhiễm độc nọc ong vò vẽ mức độ nhẹ.',
                         'Tai nạn ong đốt nhiều nốt từ 10 đến 20 nốt nguy cơ tổn thương thận cấp.',
                         'Ong đốt nhiều nốt có phản ứng viêm hạch và sốt nhẹ phản ứng.',
                         'Nghi ngờ ong đốt nhiều nốt có biến chứng tán huyết nhẹ cần theo dõi '
                         'sát.'],
  'bien_the_ke_hoach': ['Dùng nhíp vô khuẩn gắp bỏ toàn bộ ngòi ong, chườm lạnh giảm sưng đau, xét '
                        'nghiệm CK men gan creatinin, uống nhiều nước và dùng kháng histamine giảm '
                        'dị ứng.',
                        'Dùng dao cùn hoặc mép thẻ nhựa gạt nhẹ lấy hết ngòi ong tránh bóp vỡ túi '
                        'nọc, rửa sạch bằng xà phòng sát khuẩn và chườm đá lạnh 20 phút.',
                        'Làm xét nghiệm men cơ Creatine Kinase (CK), men gan AST ALT, tổng phân '
                        'tích nước tiểu tìm myoglobin, chức năng thận creatinin và điện giải đồ.',
                        'Hướng dẫn người bệnh uống nhiều nước 2-3 lít/ngày kiềm hóa nước tiểu bài '
                        'xuất độc tố, kê đơn paracetamol giảm đau và cetirizine giảm phù nề ngứa.',
                        'Tiêm phòng uốn ván SAT nếu vết đốt bẩn ngoài vườn rừng, theo dõi màu sắc '
                        'nước tiểu mỗi lần đi tiểu nếu chuyển màu nâu đỏ phải nhập viện ngay.',
                        'Theo dõi sát dấu sinh tồn và lượng nước tiểu 24 giờ tại phòng cấp cứu, '
                        'chỉ định truyền dịch tĩnh mạch tăng bài niệu phòng suy thận cấp.'],
  'bien_the_kham': ['Ghi nhận 15 vết ong đốt vùng đầu mặt và hai cánh tay, sưng nề tấy đỏ diện '
                    'rộng, vài nốt còn ngòi ong, nước tiểu vàng trong chưa có sắc tố đỏ.',
                    'Khám thấy 12 nốt ong vò vẽ đốt ở lưng và cổ, mỗi nốt có chấm hoại tử đen '
                    'trung tâm quầng đỏ phù nề 3cm, ấn rất đau buốt, sốt 38 độ C.',
                    'Nhiều vết ong mật đốt rải rác ở hai cẳng tay, ngòi độc còn cắm nguyên trên '
                    'da, mô mềm phù nề lan tỏa quanh vết đốt, không khó thở thanh quản.',
                    'Bệnh nhân tỉnh táo đau nhức nhiều vùng da bị ong đốt, 18 nốt sưng đỏ tấy gờ '
                    'cao, mạch 90 l/p, HA 120/80 mmHg, nước tiểu màu vàng trong.',
                    'Tổn thương da dạng sưng nề cục bộ do nọc độc côn trùng, các vết đốt vùng mặt '
                    'gây híp mắt nhẹ, hạch vùng sưng đau, SpO2 98% khí phòng.',
                    'Khám phát hiện 14 vết ong đốt có phản ứng viêm mô mềm cấp tính, chưa có biểu '
                    'hiện suy hô hấp hay sốc phản vệ, nước tiểu chưa sẫm màu.'],
  'chan_doan': 'Ong đốt nhiều nốt nhiễm độc nọc ong nhẹ chưa có biến chứng tiêu cơ vân.',
  'chinh': ['nhiều vết đốt từ mười đến hai mươi nốt sưng nề đỏ đau rát buốt dữ dội trên da',
            'vết đốt có điểm chấm hoại tử đen ở trung tâm có thể còn cắm lại ngòi độc của ong',
            'sưng nề phù cứng lan rộng xung quanh các vị trí bị đốt kèm nóng rát đỏ ửng'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'miễn dịch - dị ứng',
  'ke_hoach': 'Dùng nhíp vô khuẩn gắp bỏ toàn bộ ngòi ong, chườm lạnh giảm sưng đau, xét nghiệm CK '
              'men gan creatinin, uống nhiều nước và dùng kháng histamine giảm dị ứng.',
  'kham': 'Ghi nhận 15 vết ong đốt vùng đầu mặt và hai cánh tay, sưng nề tấy đỏ diện rộng, vài nốt '
          'còn ngòi ong, nước tiểu vàng trong chưa có sắc tố đỏ.',
  'nhom': 'cả hai',
  'phu': ['sốt nhẹ mệt mỏi buồn nôn bồn chồn khó chịu toàn thân sau khi bị đốt',
          'ngứa ngáy râm ran tại các vùng da xung quanh vết sưng tấy',
          'nước tiểu có màu đỏ sẫm hoặc nâu đen cảnh báo nguy cơ tiêu cơ vân tán huyết'],
  'ten': 'ong đốt nhiều nốt nhiễm độc nọc ong nhẹ'},
 {'bien_the_chan_doan': ['Rắn lục đuôi đỏ cắn có rối loạn đông máu và xuất huyết tại chỗ.',
                         'Rắn lục đuôi đỏ cắn giai đoạn nhiễm độc nọc gây tiêu thụ đông máu cấp.',
                         'Theo dõi rắn lục đuôi đỏ cắn có sưng nề hoại tử chi tiến triển nhanh.',
                         'Tai nạn rắn lục đuôi đỏ cắn có xuất huyết niêm mạc toàn thân.',
                         'Bệnh rắn lục đuôi đỏ cắn có nghiệm pháp đông máu toàn bộ 20WBCT không '
                         'đông.',
                         'Cấp cứu rắn lục đuôi đỏ cắn có giảm fibrinogen và giảm tiểu cầu nặng.'],
  'bien_the_ke_hoach': ['Bất động chi bị cắn bằng nẹp ép nhẹ, xét nghiệm đông máu toàn bộ 20WBCT '
                        'đông máu 20 phút, chỉ định truyền huyết thanh kháng nọc rắn lục đặc hiệu.',
                        'Rửa sạch vết thương, đặt nẹp bất động bàn chân ở tư thế cơ năng ngang '
                        'tim, tuyệt đối không rạch vết cắn hay buộc garo thắt chặt làm hoại tử '
                        'chi.',
                        'Thực hiện test đông máu toàn bộ 20 phút tại giường 20WBCT nếu máu không '
                        'đông chỉ định truyền ngay huyết thanh kháng nọc rắn lục tinh chế.',
                        'Xét nghiệm công thức máu kiểm tra số lượng tiểu cầu, xét nghiệm đông máu '
                        'toàn bộ PT, aPTT, định lượng nồng độ fibrinogen máu giảm nặng.',
                        'Tiêm phòng uốn ván SAT, dùng kháng sinh phổ rộng phòng ngừa nhiễm trùng '
                        'mô mềm do vi khuẩn kỵ khí miệng rắn, truyền dịch bù thể tích.',
                        'Hội chẩn Chống độc truyền nhắc lại liều huyết thanh kháng nọc sau 6 giờ '
                        'nếu tình trạng rối loạn đông máu và chảy máu tại chỗ chưa được kiểm '
                        'soát.'],
  'bien_the_kham': ['Mu bàn chân phải có 2 vết răng nanh cách nhau 1cm rỉ máu đỏ tươi không đông, '
                    'sưng phù tím lan đến 1/3 dưới cẳng chân, mạch mu chân bắt rõ.',
                    'Bàn tay trái sưng to gấp đôi tay phải màu tím bầm, 2 vết răng nanh ở ngón cái '
                    'máu rỉ liên tục thấm đẫm băng gạc, đau nhức buốt dữ dội.',
                    'Khám thấy vết cắn rắn lục ở cẳng chân có bọng xuất huyết đen xung quanh, phù '
                    'nề căng cứng lan lên khớp gối, chảy máu chân răng tự nhiên.',
                    'Ghi nhận hai vết móc độc cách nhau 8mm ở cổ chân, máu không đông tự nhiên '
                    'chảy rỉ rả, chi bị cắn lạnh phù tím, mạch chày sau còn bắt được.',
                    'Vết cắn rắn lục đuôi đỏ sưng nề bầm tím lan nhanh sau 2 giờ, nhiều mảng xuất '
                    'huyết dưới da quanh vết cắn, bệnh nhân hoảng hốt vã mồ hôi.',
                    'Khám cấp cứu vết rắn cắn: máu rỉ không cầm tại vết thương, sưng nề tiến triển '
                    'vượt qua cổ tay, không có triệu chứng liệt cơ hô hấp kiểu rắn cạp nong.'],
  'chan_doan': 'Rắn lục đuôi đỏ cắn có rối loạn đông máu và xuất huyết tại chỗ.',
  'chinh': ['vết răng nanh rắn cắn ở mu bàn chân hoặc bàn tay chảy máu rỉ rả liên tục không tự cầm',
            'sưng nề phù căng tím tái và đau nhức dữ dội lan nhanh từ vết cắn lên toàn bộ chi',
            'xuất hiện các bọng nước chứa dịch máu đen xuất huyết dưới da quanh vết cắn'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'huyết học',
  'ke_hoach': 'Bất động chi bị cắn bằng nẹp ép nhẹ, xét nghiệm đông máu toàn bộ 20WBCT đông máu 20 '
              'phút, chỉ định truyền huyết thanh kháng nọc rắn lục đặc hiệu.',
  'kham': 'Mu bàn chân phải có 2 vết răng nanh cách nhau 1cm rỉ máu đỏ tươi không đông, sưng phù '
          'tím lan đến 1/3 dưới cẳng chân, mạch mu chân bắt rõ.',
  'nhom': 'cả hai',
  'phu': ['chảy máu chân răng bầm tím rải rác dưới da ở các vị trí va chạm nhẹ',
          'lo lắng hoảng loạn vã mồ hôi mạch nhanh sau khi bị rắn tấn công',
          'tiền sử nhìn thấy rõ con rắn màu xanh lá cây đuôi có màu nâu đỏ đặc trưng'],
  'ten': 'rắn lục đuôi đỏ cắn chảy máu tại chỗ'},
 {'bien_the_chan_doan': ['Ngộ độc hải sản chứa độc tố ciguatera thể thần kinh cảm giác.',
                         'Ngộ độc hải sản chứa độc tố ciguatera có rối loạn nhịp tim chậm xoang.',
                         'Theo dõi ngộ độc hải sản chứa độc tố ciguatera sau ăn cá biển rạn san '
                         'hô.',
                         'Ngộ độc hải sản chứa độc tố ciguatera thể phối hợp tiêu hóa và thần '
                         'kinh.',
                         'Bệnh ngộ độc độc tố ciguatoxin có triệu chứng nghịch đảo cảm giác nhiệt '
                         'độ.',
                         'Nghi ngờ ngộ độc hải sản chứa độc tố ciguatera ở nhóm người cùng ăn cá '
                         'nhồng.'],
  'bien_the_ke_hoach': ['Bù nước điện giải đường uống hoặc truyền tĩnh mạch, truyền tĩnh mạch '
                        'mannitol 20% giảm phù nề dẫn truyền thần kinh, dùng gabapentin giảm dị '
                        'cảm buốt rát.',
                        'Chỉ định truyền tĩnh mạch dung dịch mannitol 20% liều 1g/kg trong 45 phút '
                        'nếu đến sớm trong vòng 48-72 giờ đầu cải thiện triệu chứng thần kinh.',
                        'Theo dõi sát điện tâm đồ liên tục phát hiện nhịp chậm xoang hoặc blốc nhĩ '
                        'thất, chuẩn bị sẵn atropine tiêm nếu nhịp tim xuống dưới 45 l/p.',
                        'Kê đơn thuốc giảm đau thần kinh gabapentin hoặc pregabalin kiểm soát cảm '
                        'giác buốt rát dị cảm, bổ sung vitamin nhóm B liều cao.',
                        'Tư vấn kiêng tuyệt đối rượu bia cá hải sản thịt gà các loại hạt trong 3-6 '
                        'tháng đề phòng kích hoạt tái phát cơn dị cảm buốt rát kéo dài.',
                        'Truyền dịch bù nước điện giải cân bằng thăng bằng kiềm toan, giải thích '
                        'tính chất mạn tính của rối loạn cảm giác và trấn an người bệnh.'],
  'bien_the_kham': ['Khám cảm giác có hiện tượng dị cảm nghịch đảo nhiệt độ rõ rệt khi tiếp xúc '
                    'cốc nước lạnh, bụng mềm, nhịp tim chậm xoang 54 l/p, huyết áp 105/65 mmHg.',
                    'Bệnh nhân giật nảy mình khi chạm tay vào nước mát vì cảm thấy như bị kim châm '
                    'lửa đốt (nghịch đảo nhiệt độ), tê bì quanh miệng và đầu chi.',
                    'Khám thấy nhịp tim chậm xoang 50 chu kỳ/phút, đồng tử bình thường, cảm giác '
                    'râm ran như kiến bò dày đặc ở hai lòng bàn chân bàn tay.',
                    'Tổn thương thần kinh cảm giác ngoại biên sau ăn cá mú rạn san hô: giảm cảm '
                    'giác đau nhưng tăng cảm giác buốt lạnh, cơ lực tứ chi bình thường.',
                    'Ghi nhận hội chứng ngộ độc ciguatera đặc trưng: mạch chậm hạ huyết áp tư thế, '
                    'tê môi lưỡi nuốt nghẹn thoáng qua, nôn tiêu chảy đã giảm bớt.',
                    'Khám lâm sàng phát hiện dị cảm nóng lạnh đảo ngược kinh điển khi áp ống '
                    'nghiệm nước đá lên da, phản xạ gân xương giảm nhẹ đồng đều.'],
  'chan_doan': 'Ngộ độc hải sản chứa độc tố ciguatera thể thần kinh cảm giác.',
  'chinh': ['rối loạn cảm giác đảo ngược nhiệt độ điển hình: sờ vật lạnh thấy nóng rát buốt như bị '
            'bỏng',
            'tê bì ngứa ran như kiến bò châm chích quanh môi lưỡi miệng và các đầu ngón tay chân',
            'tiền sử ăn cá rạn san hô cá nhồng cá mú biển vài giờ trước khi khởi phát triệu chứng'],
  'da_duyet': False,
  'dien_tien': 'cấp',
  'he_co_quan': 'tiêu hoá',
  'ke_hoach': 'Bù nước điện giải đường uống hoặc truyền tĩnh mạch, truyền tĩnh mạch mannitol 20% '
              'giảm phù nề dẫn truyền thần kinh, dùng gabapentin giảm dị cảm buốt rát.',
  'kham': 'Khám cảm giác có hiện tượng dị cảm nghịch đảo nhiệt độ rõ rệt khi tiếp xúc cốc nước '
          'lạnh, bụng mềm, nhịp tim chậm xoang 54 l/p, huyết áp 105/65 mmHg.',
  'nhom': 'cả hai',
  'phu': ['đau quặn bụng nôn ói và tiêu chảy phân lỏng nhiều lần trong giai đoạn đầu',
          'đau nhức cơ bắp ê ẩm rã rời khớp chân tay và cảm giác yếu mềm hai chân khi đi lại',
          'nhịp tim chậm hạ huyết áp nhẹ và cảm giác hoa mắt chóng mặt khi đứng'],
  'ten': 'ngộ độc hải sản chứa độc tố ciguatera'}]
