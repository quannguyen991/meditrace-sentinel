# -*- coding: utf-8 -*-
"""Khuon benh mo rong (Task F1-F5, Axis: 600 Clinical Templates & Organ Diversity).

Tai lieu can cu:
  - docs/BAN-GIAO-SINH-DU-LIEU-V2.md
  - docs/khuon-mo-rong-danh-sach.md
  - docs/superpowers/plans/2026-11-21-nang-cap-toan-dien-meditrace.md

RANG BUOC BAT BUOC:
1. KHONG sua doi 200 khuon goc trong src/ngu_lieu_viet.py (test_du_200_khuon phai PASS).
2. Toan bo khuon moi nam trong src/khuon_mo_rong.py (DOT[1], DOT[2]), da_duyet = False.
3. Moi khuon CO TRUONG `he_co_quan`. Toi thieu 18 he co quan, khong he nao vuot 12% tong (test_da_dang_he_co_quan).
4. Chia tap doc lap (Task F2): Moi dot 200 khuon chia doc lap 160/20/20.

Noi dung y khoa do AI soan thao chuyen sau, da_duyet = False (cho Hoi dong Y khoa / bac si chuyen khoa phe duyet).
"""

# Bang anh xa he co quan cho 200 khuon goc cua src/ngu_lieu_viet.py:
HE_CO_QUAN_200_CU = {   'bong gân cổ chân': 'chấn thương',
    'béo phì': 'dinh dưỡng',
    'bướu nhân tuyến giáp': 'nội tiết - chuyển hoá',
    'bệnh parkinson giai đoạn sớm': 'thần kinh',
    'bệnh phổi tắc nghẽn mạn tính': 'hô hấp',
    'bệnh thận mạn giai đoạn 3': 'thận - tiết niệu',
    'bệnh tim thiếu máu cục bộ': 'tim mạch',
    'bụi phổi silic': 'hô hấp',
    'chàm sữa': 'da liễu',
    'chốc lở': 'da liễu',
    'chốc lở dạng bọng nước': 'da liễu',
    'co giật do sốt': 'nhi khoa',
    'cúm mùa': 'truyền nhiễm',
    'cơn thiếu máu não thoáng qua': 'thần kinh',
    'cơn tăng huyết áp kịch phát': 'tim mạch',
    'cơn đau thắt ngực không ổn định': 'tim mạch',
    'cường giáp': 'nội tiết - chuyển hoá',
    'cận thị tiến triển': 'mắt',
    'dị ứng đạm sữa bò': 'miễn dịch - dị ứng',
    'gai xương gót chân': 'cơ xương khớp',
    'gan nhiễm mỡ': 'tiêu hoá',
    'ghẻ': 'da liễu',
    'giãn phế quản bội nhiễm': 'hô hấp',
    'giãn tĩnh mạch thừng tinh': 'nam khoa',
    'glôcôm góc đóng cấp': 'mắt',
    'gout': 'cơ xương khớp',
    'hen phế quản': 'hô hấp',
    'hen tim': 'tim mạch',
    'ho gà ở trẻ em': 'truyền nhiễm',
    'huyết khối tĩnh mạch sâu': 'tim mạch',
    'huyết áp thấp tư thế': 'tim mạch',
    'hạ canxi máu': 'nội tiết - chuyển hoá',
    'hạ đường huyết do thuốc': 'nội tiết - chuyển hoá',
    'hẹp hở van hai lá': 'tim mạch',
    'hồng ban đa dạng do thuốc': 'da liễu',
    'hội chứng buồng trứng đa nang': 'sản phụ khoa',
    'hội chứng chân không yên': 'thần kinh',
    'hội chứng cushing do thuốc': 'nội tiết - chuyển hoá',
    'hội chứng ruột kích thích': 'tiêu hoá',
    'hội chứng thận hư': 'thận - tiết niệu',
    'hội chứng ống cổ tay': 'thần kinh',
    'khô mắt': 'mắt',
    'không dung nạp lactose': 'tiêu hoá',
    'liệt mặt ngoại biên': 'thần kinh',
    'loãng xương sau mãn kinh': 'cơ xương khớp',
    'lupus ban đỏ hệ thống': 'miễn dịch - dị ứng',
    'lạc nội mạc tử cung': 'sản phụ khoa',
    'lẹo mắt': 'mắt',
    'lỵ trực trùng': 'truyền nhiễm',
    'mày đay': 'miễn dịch - dị ứng',
    'mất ngủ mạn tính': 'tâm thần',
    'nang thận đơn độc': 'thận - tiết niệu',
    'ngoại tâm thu': 'tim mạch',
    'ngón tay lò xo': 'cơ xương khớp',
    'ngưng thở khi ngủ do tắc nghẽn': 'hô hấp',
    'ngộ độc thực phẩm': 'tiêu hoá',
    'nhiễm adenovirus đường hô hấp': 'truyền nhiễm',
    'nhiễm giun': 'truyền nhiễm',
    'nhiễm khuẩn HP dạ dày kháng thuốc': 'tiêu hoá',
    'nhiễm khuẩn tiết niệu ở trẻ': 'thận - tiết niệu',
    'nhiễm toan ống thận': 'thận - tiết niệu',
    'nôn nghén nặng': 'sản phụ khoa',
    'nôn trớ sinh lý': 'nhi khoa',
    'nút ráy tai': 'tai mũi họng',
    'nấm da thân': 'da liễu',
    'nấm móng do dermatophytes': 'da liễu',
    'phì đại lành tính tuyến tiền liệt': 'nam khoa',
    'phì đại tuyến tiền liệt': 'nam khoa',
    'quai bị': 'truyền nhiễm',
    'rubella': 'truyền nhiễm',
    'rung nhĩ': 'tim mạch',
    'rách bán phần dây chằng chéo trước': 'chấn thương',
    'rách giác mạc nông': 'mắt',
    'rối loạn cương dương': 'nam khoa',
    'rối loạn hoảng sợ kịch phát': 'tâm thần',
    'rối loạn kinh nguyệt': 'sản phụ khoa',
    'rối loạn lipid máu': 'nội tiết - chuyển hoá',
    'rối loạn lo âu': 'tâm thần',
    'rối loạn phân ly': 'tâm thần',
    'rối loạn tiêu hóa do kháng sinh': 'tiêu hoá',
    'rối loạn tiền đình': 'thần kinh',
    'rối loạn ám ảnh cưỡng chế': 'tâm thần',
    'sa sút trí tuệ mạch máu': 'thần kinh',
    'suy giáp': 'nội tiết - chuyển hoá',
    'suy tim mạn': 'tim mạch',
    'suy tim phân xuất tống máu giảm': 'tim mạch',
    'suy tuyến thượng thận': 'nội tiết - chuyển hoá',
    'suy tĩnh mạch chi dưới': 'tim mạch',
    'sỏi bàng quang': 'thận - tiết niệu',
    'sỏi niệu quản': 'thận - tiết niệu',
    'sỏi thận': 'thận - tiết niệu',
    'sỏi túi mật': 'tiêu hoá',
    'sốt mò': 'truyền nhiễm',
    'sốt phát ban': 'truyền nhiễm',
    'sốt siêu vi': 'truyền nhiễm',
    'sốt xuất huyết': 'truyền nhiễm',
    'sởi ở trẻ em': 'truyền nhiễm',
    'tay chân miệng': 'truyền nhiễm',
    'thalassemia thể nhẹ': 'huyết học',
    'thiếu máu do giun': 'huyết học',
    'thiếu máu thiếu sắt': 'huyết học',
    'thiếu vitamin D': 'dinh dưỡng',
    'thoái hóa cột sống': 'cơ xương khớp',
    'thoái hóa khớp háng': 'cơ xương khớp',
    'thoát vị đĩa đệm cột sống cổ': 'cơ xương khớp',
    'thoát vị đĩa đệm cột sống thắt lưng': 'cơ xương khớp',
    'thận ứ nước do sỏi': 'thận - tiết niệu',
    'thủy đậu': 'truyền nhiễm',
    'tiêu chảy cấp': 'tiêu hoá',
    'tiêu chảy do rotavirus': 'truyền nhiễm',
    'tiền đái tháo đường': 'nội tiết - chuyển hoá',
    'tràn dịch màng phổi do lao': 'hô hấp',
    'trào ngược dạ dày thực quản': 'tiêu hoá',
    'trĩ': 'tiêu hoá',
    'trĩ huyết khối tắc mạch': 'tiêu hoá',
    'trầm cảm': 'tâm thần',
    'trầm cảm sau sinh': 'tâm thần',
    'trứng cá': 'da liễu',
    'táo bón chức năng': 'tiêu hoá',
    'tăng huyết áp': 'tim mạch',
    'u bàng quang lành tính': 'thận - tiết niệu',
    'u nang buồng trứng': 'sản phụ khoa',
    'u xơ tử cung': 'sản phụ khoa',
    'ung thư cổ tử cung': 'sản phụ khoa',
    'ung thư tiền liệt tuyến': 'nam khoa',
    'ung thư vú': 'sản phụ khoa',
    'viêm amidan cấp': 'tai mũi họng',
    'viêm amidan hốc mủ': 'tai mũi họng',
    'viêm bàng quang cấp': 'thận - tiết niệu',
    'viêm bờ mi': 'mắt',
    'viêm cơ tim do virus': 'tim mạch',
    'viêm cầu thận cấp sau nhiễm liên cầu': 'thận - tiết niệu',
    'viêm cột sống dính khớp': 'cơ xương khớp',
    'viêm da cơ địa': 'da liễu',
    'viêm da tiếp xúc': 'da liễu',
    'viêm da tã lót': 'da liễu',
    'viêm dạ dày cấp': 'tiêu hoá',
    'viêm gan B mạn': 'truyền nhiễm',
    'viêm gan C mạn': 'truyền nhiễm',
    'viêm giác mạc chấm': 'mắt',
    'viêm gân gót achilles': 'cơ xương khớp',
    'viêm hạch mạc treo cấp': 'tiêu hoá',
    'viêm họng cấp': 'tai mũi họng',
    'viêm họng do liên cầu': 'tai mũi họng',
    'viêm khớp dạng thấp': 'cơ xương khớp',
    'viêm khớp gối': 'cơ xương khớp',
    'viêm kết mạc': 'mắt',
    'viêm kết mạc dị ứng': 'mắt',
    'viêm loét dạ dày do HP': 'tiêu hoá',
    'viêm loét đại trực tràng chảy máu': 'tiêu hoá',
    'viêm lộ tuyến cổ tử cung': 'sản phụ khoa',
    'viêm màng ngoài tim': 'tim mạch',
    'viêm màng não do virus': 'truyền nhiễm',
    'viêm màng phổi khô': 'hô hấp',
    'viêm mào tinh hoàn': 'nam khoa',
    'viêm mũi dị ứng': 'tai mũi họng',
    'viêm mũi họng cấp': 'tai mũi họng',
    'viêm mũi xoang mạn tính': 'tai mũi họng',
    'viêm phế quản': 'hô hấp',
    'viêm phổi': 'hô hấp',
    'viêm phổi cộng đồng người lớn': 'hô hấp',
    'viêm quanh khớp vai': 'cơ xương khớp',
    'viêm tai giữa': 'tai mũi họng',
    'viêm tai giữa ứ dịch': 'tai mũi họng',
    'viêm tai ngoài': 'tai mũi họng',
    'viêm thanh khí phế quản cấp': 'hô hấp',
    'viêm thanh quản cấp': 'tai mũi họng',
    'viêm tiểu phế quản': 'hô hấp',
    'viêm tuyến giáp bán cấp': 'nội tiết - chuyển hoá',
    'viêm tuyến vú': 'sản phụ khoa',
    'viêm túi mật cấp': 'tiêu hoá',
    'viêm tụy cấp nhẹ': 'tiêu hoá',
    'viêm xoang': 'tai mũi họng',
    'viêm xương chũm mạn': 'tai mũi họng',
    'viêm âm đạo do nấm': 'sản phụ khoa',
    'viêm đường tiết niệu': 'thận - tiết niệu',
    'vảy nến': 'da liễu',
    'xuất huyết tiêu hóa trên do loét': 'tiêu hoá',
    'xơ cứng bì toàn thể': 'miễn dịch - dị ứng',
    'xơ cứng tai': 'tai mũi họng',
    'xơ gan mất bù': 'tiêu hoá',
    'xơ phổi vô căn': 'hô hấp',
    'xơ vữa động mạch cảnh': 'tim mạch',
    'zona thần kinh': 'da liễu',
    'áp xe gan do amip': 'truyền nhiễm',
    'áp xe phổi': 'hô hấp',
    'đau dây thần kinh tam thoa': 'thần kinh',
    'đau dạ dày': 'tiêu hoá',
    'đau nửa đầu': 'thần kinh',
    'đau thần kinh tọa': 'thần kinh',
    'đau thắt lưng cơ năng': 'cơ xương khớp',
    'đau thắt ngực ổn định': 'tim mạch',
    'đau vai gáy': 'cơ xương khớp',
    'đau đầu căng thẳng': 'thần kinh',
    'đau đầu cụm': 'thần kinh',
    'đái dầm': 'nhi khoa',
    'đái tháo nhạt': 'nội tiết - chuyển hoá',
    'đái tháo đường thai kỳ': 'sản phụ khoa',
    'đái tháo đường típ 2': 'nội tiết - chuyển hoá',
    'đục thủy tinh thể tuổi già': 'mắt'}

# 50 khuon mo rong Lo 1 (Dot 1: khuon 201-250) da hien thuc hoa day du 6 bien the:
BENH_LO_1 = [
    {   'bien_the_chan_doan': [   'Viêm phổi ở trẻ em mức độ nặng.',
                              'Theo dõi viêm phổi ở trẻ em có suy hô hấp cấp.',
                              'Viêm phổi ở trẻ em bội nhiễm vi khuẩn.',
                              'Theo dõi viêm phổi ở trẻ em biến chứng đông đặc đáy phổi.',
                              'Viêm phổi ở trẻ em thùy dưới bên phải.',
                              'Viêm phổi ở trẻ em giai đoạn toàn phát.'],
    'bien_the_ke_hoach': [   'Chỉ định nhập viện điều trị, thở oxy qua gọng mũi, kháng sinh cefotaxime tĩnh mạch, khí '
                             'dung nước muối sinh lý và hút đờm dãi.',
                             'Chuyển khoa Nhi nội trú, đặt đường truyền tĩnh mạch dùng ampicillin kết hợp gentamicin, '
                             'chụp X-quang tim phổi thẳng.',
                             'Nhập viện khẩn cấp, hỗ trợ hô hấp duy trì SpO2 trên 95%, cấy máu, kháng sinh ceftriaxone '
                             'tiêm truyền và vỗ rung lồng ngực.',
                             'Cho trẻ vào viện điều trị tích cực, thở oxy cannula 1-2 lít/phút, dùng kháng sinh đường '
                             'toàn thân và bù dịch điện giải.',
                             'Làm bệnh án nhập viện, xét nghiệm công thức máu, CRP, X-quang ngực, dùng cefotaxime phối '
                             'hợp khí dung thông thoáng đường thở.',
                             'Chỉ định điều trị nội trú, theo dõi sát sinh hiệu từng giờ, kháng sinh tĩnh mạch liều '
                             'cao và hạ sốt tích cực.'],
    'bien_the_kham': [   'Nhịp thở 52 lần/phút, rút lõm lồng ngực rõ, phổi nghe nhiều ran ẩm nhỏ hạt và ran nổ rải rác '
                         'đáy phổi phải.',
                         'SpO2 93% khí phòng, thở nhanh 50 lần/phút có co kéo cơ liên sườn, nghe phổi đáy phải giảm '
                         'thông khí kèm ran nổ.',
                         'Trẻ thở co kéo hõm ức và rút lõm lồng ngực, tần số thở 54 l/p, thông khí phổi hai bên không '
                         'đều, rải rác ran ẩm.',
                         'Khám thấy cánh mũi phập phồng, nhịp thở nhanh 52 chu kỳ/phút, rì rào phế nang giảm nhẹ bên '
                         'phải, nghe rõ ran nổ cuối thì hít vào.',
                         'Dấu hiệu suy hô hấp độ 2: thở nhanh rút lõm ngực, nghe phổi rải rác ran ẩm nhỏ hạt tập trung '
                         'ở thùy dưới phổi phải.',
                         'Thở nhanh 55 lần/phút, nghe phổi có tiếng cọ màng phổi nhẹ và ran ẩm hai phế trường, rút lõm '
                         'lồng ngực trung bình.'],
    'chan_doan': 'Viêm phổi ở trẻ em mức độ nặng.',
    'chinh': [   'sốt cao liên tục đáp ứng kém với thuốc hạ sốt',
                 'thở nhanh nông kèm rút lõm lồng ngực rõ rệt',
                 'ho cơn dồn dập có đờm đục hoặc tím tái quanh môi'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'hô hấp',
    'ke_hoach': 'Chỉ định nhập viện điều trị, thở oxy qua gọng mũi, kháng sinh cefotaxime tĩnh mạch, khí dung nước '
                'muối sinh lý và hút đờm dãi.',
    'kham': 'Nhịp thở 52 lần/phút, rút lõm lồng ngực rõ, phổi nghe nhiều ran ẩm nhỏ hạt và ran nổ rải rác đáy phổi '
            'phải.',
    'nhom': 'nhi',
    'phu': [   'trẻ quấy khóc nhiều li bì khó đánh thức',
               'bỏ bú hoặc bú kém nôn trớ sau ăn',
               'cánh mũi phập phồng theo từng nhịp thở'],
    'ten': 'viêm phổi ở trẻ em'},
    {   'bien_the_chan_doan': [   'Vàng da sơ sinh kéo dài nghi do ứ mật.',
                              'Theo dõi vàng da sơ sinh kéo dài do bất đồng nhóm máu ABO muộn.',
                              'Vàng da sơ sinh kéo dài do sữa mẹ.',
                              'Theo dõi vàng da sơ sinh kéo dài nghi teo mật bẩm sinh.',
                              'Vàng da sơ sinh kéo dài kèm tăng bilirubin trực tiếp.',
                              'Vàng da sơ sinh kéo dài thể hỗn hợp.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm bilirubin toàn phần và trực tiếp, men gan AST ALT, siêu âm gan mật tìm '
                             'teo đường mật bẩm sinh.',
                             'Định lượng bilirubin máu toàn phần và trực tiếp, xét nghiệm nhóm máu mẹ con, siêu âm ổ '
                             'bụng khảo sát túi mật.',
                             'Chỉ định chiếu đèn ánh sáng xanh liên tục nếu bilirubin gián tiếp cao, xét nghiệm chức '
                             'năng gan và đông máu cơ bản.',
                             'Xét nghiệm máu tổng quát tìm nguyên nhân tán huyết hoặc nhiễm trùng, hướng dẫn mẹ duy '
                             'trì bú mẹ đúng cữ.',
                             'Hội chẩn chuyên khoa Tiêu hóa Nhi, làm bilan chuyển hóa và siêu âm gan mật sau nhịn ăn 4 '
                             'giờ.',
                             'Lấy máu xét nghiệm bilirubin định lượng, CRP, cấy nước tiểu loại trừ nhiễm khuẩn niệu và '
                             'theo dõi màu sắc phân.'],
    'bien_the_kham': [   'Da và củng mạc mắt vàng sẫm đến lòng bàn tay bàn chân (vùng Kramer 5), gan to 2cm dưới bờ '
                         'sườn, lách không sờ chạm.',
                         'Trẻ tỉnh, da vàng đậm toàn thân qua vùng đùi cẳng chân, củng mạc mắt vàng chanh, thóp phẳng '
                         'không căng phồng.',
                         'Đánh giá Kramer độ 4-5 vàng da tới cẳng chân mu bàn tay, gan mấp mé dưới hạ sườn phải 1,5cm '
                         'mật độ mềm.',
                         'Khám thấy vàng da sẫm kèm củng mạc mắt nhuộm vàng, trương lực cơ bình thường, phản xạ sơ '
                         'sinh còn tốt.',
                         'Vàng da sẫm màu rõ rệt dưới ánh sáng tự nhiên, ấn kính da vàng dai dẳng, gan to nhẹ dưới bờ '
                         'sườn 2cm mềm nhẵn.',
                         'Củng mạc mắt và niêm mạc dưới lưỡi vàng đậm, da toàn thân vàng rơm, phân quan sát thấy hơi '
                         'nhạt màu.'],
    'chan_doan': 'Vàng da sơ sinh kéo dài nghi do ứ mật.',
    'chinh': [   'vàng da toàn thân kéo dài quá 14 ngày sau sinh',
                 'mắt và niêm mạc miệng ánh vàng sẫm',
                 'phân bạc màu hoặc nước tiểu sẫm màu như nước trà đặc'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Làm xét nghiệm bilirubin toàn phần và trực tiếp, men gan AST ALT, siêu âm gan mật tìm teo đường mật '
                'bẩm sinh.',
    'kham': 'Da và củng mạc mắt vàng sẫm đến lòng bàn tay bàn chân (vùng Kramer 5), gan to 2cm dưới bờ sườn, lách '
            'không sờ chạm.',
    'nhom': 'nhi',
    'phu': [   'trẻ bú chậm chậm tăng cân so với mốc sinh',
               'bụng hơi chướng sờ thấy bờ gan mấp mé bờ sườn',
               'ngủ nhiều li bì hơn trẻ bình thường cùng tuần tuổi'],
    'ten': 'vàng da sơ sinh kéo dài'},
    {   'bien_the_chan_doan': [   'Suy dinh dưỡng thấp còi mức độ vừa.',
                              'Suy dinh dưỡng thấp còi mạn tính có thiếu vi chất dinh dưỡng.',
                              'Suy dinh dưỡng thấp còi do chế độ ăn mất cân đối kéo dài.',
                              'Theo dõi suy dinh dưỡng thấp còi thứ phát sau kém hấp thu.',
                              'Suy dinh dưỡng thấp còi mức độ nặng Z-score dưới -3SD.',
                              'Suy dinh dưỡng thấp còi có kèm thiếu máu dinh dưỡng nhẹ.'],
    'bien_the_ke_hoach': [   'Tư vấn chế độ dinh dưỡng giàu vi chất, bổ sung kẽm, vitamin D3, canxi và tẩy giun định '
                             'kỳ theo hướng dẫn quốc gia.',
                             'Lập phác đồ can thiệp dinh dưỡng 100 kcal/kg/ngày, kê siro kẽm gluconate, men vi sinh và '
                             'tái khám nhân trắc mỗi tháng.',
                             'Hướng dẫn gia đình tăng cường dầu mỡ và đạm động vật vào cháo, bổ sung đa vi chất sắt '
                             'kẽm và theo dõi biểu đồ tăng trưởng.',
                             'Tư vấn dinh dưỡng phục hồi, xét nghiệm kẽm huyết thanh, canxi ion hóa, tẩy giun bằng '
                             'albendazole liều duy nhất.',
                             'Kê đơn men vi sinh và phức hợp kẽm canxi nano, điều chỉnh thời gian ăn không ép buộc, '
                             'kiểm tra chiều cao sau 2 tháng.',
                             'Xây dựng thực đơn giàu vi chất theo tháp dinh dưỡng Viện Dinh Dưỡng, bổ sung vitamin D3 '
                             '800 UI/ngày liên tục 3 tháng.'],
    'bien_the_kham': [   'Chiều cao 78cm (dưới âm 2SD theo tuổi), cân nặng theo chiều cao bình thường, lớp mỡ dưới da '
                         'mỏng, trương lực cơ hơi nhẽo.',
                         'Nhân trắc học: Chiều cao/tuổi nằm ở ngưỡng -2.3 Z-score, cơ bắp nhẽo nhẹ, thóp đã đóng muộn, '
                         'răng mới mọc 6 chiếc.',
                         'Đo chiều dài nằm thấp hơn đường chuẩn P3 tăng trưởng WHO, xương lồng ngực phẳng, da khô lông '
                         'tóc thưa nhạt màu.',
                         'Trẻ thấp hơn rõ so với bạn cùng trang lứa, tỷ lệ chiều cao/tuổi -2.5 SD, không có phù, bụng '
                         'hơi ỏng.',
                         'Khám thấy chỉ số Haz đạt -2.2 SD, thể trạng thấp bé, niêm mạc mắt hồng nhạt, lớp mỡ cánh tay '
                         'teo mỏng.',
                         'Dáng người thấp lùn so với chuẩn tuổi, chiều cao dưới bách phân vị thứ 3, phản xạ nhanh nhẹn '
                         'nhưng cơ lực giảm nhẹ.'],
    'chan_doan': 'Suy dinh dưỡng thấp còi mức độ vừa.',
    'chinh': [   'chiều cao theo tuổi dưới trừ hai độ lệch chuẩn âm 2SD',
                 'chậm tăng trưởng chiều dài liên tục nhiều tháng',
                 'chậm biết đi mọc răng muộn so với lứa tuổi'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'dinh dưỡng',
    'ke_hoach': 'Tư vấn chế độ dinh dưỡng giàu vi chất, bổ sung kẽm, vitamin D3, canxi và tẩy giun định kỳ theo hướng '
                'dẫn quốc gia.',
    'kham': 'Chiều cao 78cm (dưới âm 2SD theo tuổi), cân nặng theo chiều cao bình thường, lớp mỡ dưới da mỏng, trương '
            'lực cơ hơi nhẽo.',
    'nhom': 'nhi',
    'phu': [   'trẻ biếng ăn kén ăn bữa ăn kéo dài trên 40 phút',
               'thường xuyên mắc các đợt nhiễm trùng hô hấp tái phát',
               'tóc thưa xơ xác dễ rụng móng tay khía rãnh'],
    'ten': 'suy dinh dưỡng thấp còi'},
    {   'bien_the_chan_doan': [   'Thừa cân béo phì ở trẻ em độ 1.',
                              'Thừa cân béo phì ở trẻ em có dấu hiệu kháng insulin gai đen.',
                              'Thừa cân béo phì ở trẻ em nguy cơ hội chứng chuyển hóa.',
                              'Thừa cân béo phì ở trẻ em thể đơn thuần do lối sống.',
                              'Theo dõi thừa cân béo phì ở trẻ em có rối loạn lipid máu.',
                              'Thừa cân béo phì ở trẻ em độ 2 cần can thiệp hành vi.'],
    'bien_the_ke_hoach': [   'Điều chỉnh chế độ ăn giảm tinh bột tinh chế và đường ngọt, tăng cường vận động thể lực '
                             'ít nhất 60 phút mỗi ngày.',
                             'Xét nghiệm đường huyết đói, HbA1c, lipid máu toàn phần, siêu âm bụng khảo sát gan nhiễm '
                             'mỡ và tư vấn lối sống.',
                             'Lập kế hoạch giảm calo rỗng từ nước ngọt có gas, thay sữa bột bằng sữa tươi không đường, '
                             'tập bơi lội 3 buổi/tuần.',
                             'Kiểm tra chức năng gan thận, chuyển hóa mỡ máu, tư vấn gia đình không cho trẻ vừa ăn vừa '
                             'xem màn hình điện tử.',
                             'Khám chuyên khoa Dinh dưỡng định kỳ mỗi tháng, hướng dẫn bài tập đốt mỡ vừa sức, hạn chế '
                             'đồ chiên ngập dầu.',
                             'Làm bilan lipid máu và men gan, thiết lập mục tiêu duy trì cân nặng chờ chiều cao bắt '
                             'kịp trong 6 tháng tới.'],
    'bien_the_kham': [   'BMI đạt 26 kg/m2 (vượt ngưỡng +2SD), lớp mỡ tích tụ nhiều ở vùng bụng và ngực, vùng gáy có '
                         'dấu hiệu gai đen rõ.',
                         'Trẻ bụ bẫm quá mức, vòng bụng 76cm, mỡ phân bố ưu thế thân mình, huyết áp đo tay 115/75 mmHg '
                         'ở giới hạn cao.',
                         'Khám thấy mô mỡ dày dưới da thành bụng và đùi, vùng cổ nếp gấp gáy xuất hiện tăng sắc tố '
                         'acanthosis nigricans.',
                         'BMI theo tuổi vượt ngưỡng bách phân vị 97, nhịp tim đều 88 l/p, gối có xu hướng vẹo ngoài '
                         'nhẹ do quá tải cân nặng.',
                         'Thể trạng béo trục thân, tỷ lệ mỡ cơ thể tăng cao, bụng to xệ, da vùng bẹn và nách sẫm màu '
                         'thô ráp.',
                         'Cân nặng vượt chuẩn 40%, đo bề dày nếp gấp da cơ tam đầu dày 24mm, không có phù ngoại biên, '
                         'vận động nặng nề.'],
    'chan_doan': 'Thừa cân béo phì ở trẻ em độ 1.',
    'chinh': [   'chỉ số khối cơ thể BMI theo tuổi vượt trên cộng hai độ lệch chuẩn',
                 'tăng cân nhanh mất kiểm soát trong thời gian ngắn',
                 'thở dốc hụt hơi khi chạy nhảy hoặc leo cầu thang'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'dinh dưỡng',
    'ke_hoach': 'Điều chỉnh chế độ ăn giảm tinh bột tinh chế và đường ngọt, tăng cường vận động thể lực ít nhất 60 '
                'phút mỗi ngày.',
    'kham': 'BMI đạt 26 kg/m2 (vượt ngưỡng +2SD), lớp mỡ tích tụ nhiều ở vùng bụng và ngực, vùng gáy có dấu hiệu gai '
            'đen rõ.',
    'nhom': 'nhi',
    'phu': [   'thói quen ăn nhiều đồ ngọt thức ăn nhanh chiên rán',
               'ngáy to khi ngủ hoặc có cơn ngừng thở ngắn ban đêm',
               'da vùng gáy và nách có mảng sẫm màu dày sừng gai đen'],
    'ten': 'thừa cân béo phì ở trẻ em'},
    {   'bien_the_chan_doan': [   'Hen phế quản ở trẻ em cơn cấp mức độ nhẹ đến trung bình.',
                              'Hen phế quản ở trẻ em chưa kiểm soát tốt.',
                              'Theo dõi hen phế quản ở trẻ em khởi phát do nhiễm siêu vi hô hấp.',
                              'Hen phế quản ở trẻ em bậc 2 giai đoạn duy trì.',
                              'Cơn hen phế quản ở trẻ em mức độ trung bình có co thắt phế quản.',
                              'Hen phế quản ở trẻ em thể dị ứng khởi phát sau gắng sức.'],
    'bien_the_ke_hoach': [   'Khí dung salbutamol cắt cơn khẩn cấp, kê thuốc xịt dự phòng corticoid dạng hít '
                             'budesonide duy trì và tái khám sau 2 tuần.',
                             'Xịt ventolin 2 nhát qua buồng đệm có mặt nạ, theo dõi đáp ứng sau 20 phút, hướng dẫn sử '
                             'dụng bình xịt định liều MDI.',
                             'Dùng thuốc giãn phế quản tác dụng ngắn salbutamol khi khó thở, duy trì xịt fluticasone '
                             'mỗi tối để dự phòng tái phát.',
                             'Kê đơn montelukast dạng nhai buổi tối kết hợp thuốc xịt dự phòng, tránh tiếp xúc khói '
                             'thuốc lá và lông thú nuôi.',
                             'Lập bảng kế hoạch hành động xử trí cơn hen tại nhà, đo lưu lượng đỉnh PEF định kỳ và '
                             'hướng dẫn mẹ cách nhận biết dấu hiệu nặng.',
                             'Khí dung kết hợp salbutamol và ipratropium nếu khó thở nhiều, sau đó duy trì ICS liều '
                             'thấp và hẹn khám kiểm soát sau 1 tháng.'],
    'bien_the_kham': [   'Phổi nghe nhiều tiếng ran rít và ran ngáy lan tỏa hai phế trường thì thở ra kéo dài, SpO2 '
                         '96% khí phòng.',
                         'Lồng ngực hơi căng phồng, thì thở ra kéo dài rõ rệt, nghe phổi hai bên đầy ran rít như tiếng '
                         'gió rít qua khe cửa.',
                         'Trẻ thở co kéo nhẹ hõm trên ức, nhịp thở 34 l/p, rì rào phế nang thô ráp, nghe thấy ran ngáy '
                         'trầm rải rác.',
                         'Khám thấy nhịp thở nhanh nông, nghe phổi có tiếng thở rít thì thở ra thì thầm, không có tím '
                         'tái quanh môi.',
                         'Nghe phổi giảm âm phế nang nhẹ kèm tiếng khò khè thì thở ra, SpO2 duy trì 95%, tim đều rõ.',
                         'Trẻ ngồi cúi người ra trước để thở, phổi thông khí kém nhẹ hai đáy, rải rác ran rít thanh âm '
                         'cao thì thở ra.'],
    'chan_doan': 'Hen phế quản ở trẻ em cơn cấp mức độ nhẹ đến trung bình.',
    'chinh': [   'cơn khó thở cò cử khò khè tái phát về đêm và sáng sớm',
                 'thở rít thì thở ra phải ngồi dậy để thở',
                 'ho dai dẳng tăng lên khi thời tiết thay đổi hoặc chạy nhảy'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'hô hấp',
    'ke_hoach': 'Khí dung salbutamol cắt cơn khẩn cấp, kê thuốc xịt dự phòng corticoid dạng hít budesonide duy trì và '
                'tái khám sau 2 tuần.',
    'kham': 'Phổi nghe nhiều tiếng ran rít và ran ngáy lan tỏa hai phế trường thì thở ra kéo dài, SpO2 96% khí phòng.',
    'nhom': 'nhi',
    'phu': [   'tiền sử bản thân bị chàm da hoặc viêm mũi dị ứng',
               'gia đình có bố hoặc mẹ mắc bệnh dị ứng hen suyễn',
               'đáp ứng cắt cơn nhanh chóng sau khi xịt thuốc giãn phế quản'],
    'ten': 'hen phế quản ở trẻ em'},
    {   'bien_the_chan_doan': [   'Bệnh Kawasaki thể điển hình ngày thứ sáu.',
                              'Theo dõi bệnh Kawasaki thể không điển hình.',
                              'Bệnh Kawasaki giai đoạn cấp có nguy cơ tổn thương mạch vành.',
                              'Bệnh Kawasaki ngày thứ bảy chưa có biến chứng tim mạch.',
                              'Bệnh Kawasaki thể toàn phát cần truyền globulin miễn dịch khẩn.',
                              'Nghi ngờ bệnh Kawasaki biến chứng giãn nhẹ gốc động mạch vành.'],
    'bien_the_ke_hoach': [   'Chỉ định nhập viện cấp cứu, truyền immunoglobulin tĩnh mạch IVIG liều cao kết hợp uống '
                             'aspirin và siêu âm tim đánh giá động mạch vành.',
                             'Nhập viện khoa Tim mạch Nhi, chỉ định IVIG 2g/kg truyền tĩnh mạch liên tục trong 12 giờ, '
                             'dùng aspirin liều kháng viêm.',
                             'Làm siêu âm Doppler tim khẩn kiểm tra đường kính động mạch vành, xét nghiệm công thức '
                             'máu, tiểu cầu, tốc độ máu lắng và CRP.',
                             'Khởi động phác đồ chuẩn IVIG phối hợp aspirin 30-50 mg/kg/ngày, theo dõi sát mạch nhiệt '
                             'độ và phản ứng truyền thuốc.',
                             'Lấy máu làm bilan viêm đầy đủ, điện giải đồ, men gan, siêu âm tim màu và hội chẩn chuyên '
                             'khoa can thiệp mạch máu nhi.',
                             'Nhập viện theo dõi tích cực, dự phòng phình giãn động mạch vành bằng IVIG liều duy nhất '
                             'kết hợp aspirin theo dõi nội trú.'],
    'bien_the_kham': [   'Củng mạc mắt đỏ viêm kết mạc hai bên không tiết dịch, môi đỏ nứt nẻ, lưỡi dâu tây, mu bàn '
                         'tay bàn chân sưng nề nhẹ.',
                         'Trẻ sốt cao 39.5 độ, kết mạc mắt cương tụ đỏ không mủ, niêm mạc họng đỏ rực, lưỡi sần gai đỏ '
                         'dâu tây đặc trưng.',
                         'Khám thấy hạch cổ góc hàm phải to 2cm chắc không hóa mủ, ban đỏ dạng dát sẩn rải rác vùng '
                         'ngực bụng, lòng bàn tay đỏ rực.',
                         'Mu bàn chân phù cứng ấn không lõm, da quanh hậu môn bong vảy nhẹ, mắt đỏ toàn bộ củng mạc, '
                         'môi khô nứt rớm máu.',
                         'Trẻ quấy khóc vật vã, môi đỏ chót nứt nẻ, gai lưỡi phì đại đỏ tươi, ban sẩn hồng ban lan tỏa '
                         'thân mình.',
                         'Dấu hiệu viêm mạch hệ thống rõ: mắt sung huyết kết mạc không dử, hạch cổ sờ chạm rõ một bên, '
                         'đầu chi sưng nề đỏ ửng.'],
    'chan_doan': 'Bệnh Kawasaki thể điển hình ngày thứ sáu.',
    'chinh': [   'sốt cao liên tục kéo dài trên 5 ngày không đáp ứng kháng sinh',
                 'mắt đỏ rực hai bên nhưng không có dử mắt mủ',
                 'môi đỏ nứt nẻ chảy máu và lưỡi đỏ rực nổi gai như quả dâu tây'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Chỉ định nhập viện cấp cứu, truyền immunoglobulin tĩnh mạch IVIG liều cao kết hợp uống aspirin và '
                'siêu âm tim đánh giá động mạch vành.',
    'kham': 'Củng mạc mắt đỏ viêm kết mạc hai bên không tiết dịch, môi đỏ nứt nẻ, lưỡi dâu tây, mu bàn tay bàn chân '
            'sưng nề nhẹ.',
    'nhom': 'nhi',
    'phu': [   'phù nề mu bàn tay bàn chân kèm ban đỏ lòng bàn tay',
               'nổi ban đa dạng toàn thân dạng sẩn hồng ban',
               'nổi hạch cổ một bên kích thước trên 1.5 cm không đau'],
    'ten': 'bệnh Kawasaki'},
    {   'bien_the_chan_doan': [   'Viêm ruột thừa cấp ở trẻ em giờ thứ 18.',
                              'Theo dõi viêm ruột thừa cấp ở trẻ em thể mủ.',
                              'Viêm ruột thừa cấp ở trẻ em có nguy cơ vỡ mủ phúc mạc.',
                              'Theo dõi viêm ruột thừa cấp ở trẻ em vị trí sau manh tràng.',
                              'Viêm ruột thừa cấp ở trẻ em giai đoạn viêm tấy.',
                              'Nghi ngờ viêm ruột thừa cấp ở trẻ em cần can thiệp phẫu thuật khẩn.'],
    'bien_the_ke_hoach': [   'Chuyển mổ cấp cứu ngoại nhi, nhịn ăn uống hoàn toàn, đặt đường truyền tĩnh mạch bù dịch '
                             'và tiêm kháng sinh dự phòng cefotaxime.',
                             'Hội chẩn khẩn bác sĩ Ngoại nhi chỉ định phẫu thuật nội soi cắt ruột thừa, làm xét nghiệm '
                             'tiền phẫu đông máu nhóm máu.',
                             'Siêu âm ổ bụng khẩn cấp đo đường kính ruột thừa, truyền dịch Ringer lactat duy trì huyết '
                             'áp và ngừng cho trẻ ăn uống.',
                             'Lập bệnh án phẫu thuật cấp cứu, xét nghiệm công thức máu bạch cầu tăng cao, tiêm kháng '
                             'sinh phổ rộng metronidazole kết hợp ceftriaxone.',
                             'Giải thích tình trạng phẫu thuật cho gia đình, ký cam kết mổ nội soi, đặt sonde dạ dày '
                             'nếu nôn nhiều và chuẩn bị phòng mổ.',
                             'Chuyển phòng phẫu thuật nhi, đặt đường truyền tĩnh mạch lớn, giảm đau sau khi bác sĩ '
                             'ngoại đã khám xác chẩn.'],
    'bien_the_kham': [   'Bụng mềm vùng trên, ấn đau chói và có phản ứng thành bụng rõ rệt tại điểm McBurney hố chậu '
                         'phải.',
                         'Trẻ nằm nghiêng co gập đùi phải vào bụng, sờ nắn hố chậu phải cơ co cứng gồng kháng cự, phản '
                         'ứng dội Blumberg dương tính.',
                         'Điểm McBurney ấn đau chói khiến trẻ gạt tay bác sĩ khóc thét, phản ứng thành bụng một phần '
                         'ba dưới bụng phải rõ.',
                         'Bụng chướng nhẹ, nhu động ruột giảm, khám hố chậu phải phát hiện co cứng cơ cục bộ và dấu '
                         'hiệu đề kháng thành bụng.',
                         'Dấu hiệu Rovsing dương tính ấn hố chậu trái đau sang hố chậu phải, điểm đau ruột thừa xác '
                         'định rõ, không có cảm ứng phúc mạc toàn thể.',
                         'Trẻ quấy khóc không cho sờ bụng, ấn nhẹ hạ sườn phải và quanh rốn bụng mềm nhưng chạm hố '
                         'chậu phải cơ gồng cứng ngay lập tức.'],
    'chan_doan': 'Viêm ruột thừa cấp ở trẻ em giờ thứ 18.',
    'chinh': [   'đau bụng quanh rốn sau đó khu trú rõ về hố chậu phải',
                 'trẻ đau quặn bụng nằm co chân phải không dám cử động',
                 'nôn trớ nhiều lần thức ăn lẫn dịch mật kèm sốt nhẹ'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Chuyển mổ cấp cứu ngoại nhi, nhịn ăn uống hoàn toàn, đặt đường truyền tĩnh mạch bù dịch và tiêm kháng '
                'sinh dự phòng cefotaxime.',
    'kham': 'Bụng mềm vùng trên, ấn đau chói và có phản ứng thành bụng rõ rệt tại điểm McBurney hố chậu phải.',
    'nhom': 'nhi',
    'phu': [   'trẻ kêu đau nhói khi ho hoặc khi người lớn chạm vào bụng',
               'bỏ ăn hoàn toàn mệt lả không chịu đi lại',
               'tiêu chảy vài lần phân lỏng sệt hoặc táo bón bí trung tiện'],
    'ten': 'viêm ruột thừa cấp ở trẻ em'},
    {   'bien_the_chan_doan': [   'Tắc lệ đạo sơ sinh bên phải bẩm sinh.',
                              'Theo dõi tắc lệ đạo sơ sinh có viêm túi lệ mạn tính nhẹ.',
                              'Tắc lệ đạo sơ sinh hai bên giai đoạn sớm.',
                              'Tắc lệ đạo sơ sinh bên phải bội nhiễm vi khuẩn nhẹ bờ mi.',
                              'Tắc lệ đạo sơ sinh do tồn tại màng Hasner.',
                              'Tắc lệ đạo sơ sinh cần hướng dẫn day mát-xa bảo tồn.'],
    'bien_the_ke_hoach': [   'Hướng dẫn phụ huynh kỹ thuật mát-xa day túi lệ góc mắt đúng cách hàng ngày, vệ sinh mắt '
                             'bằng nước muối sinh lý 0.9% và nhỏ tobradex nếu có bội nhiễm.',
                             'Thị phạm cách day vuốt dọc từ góc trong mắt xuống cánh mũi 10-15 lần mỗi hiệp, nhỏ nước '
                             'muối sinh lý ngày 4-5 lần.',
                             'Kê thuốc nhỏ mắt kháng sinh tobramycin 0.3% ngày 3 lần trong 5 ngày nếu có mủ đục, tiếp '
                             'tục day túi lệ kiên trì.',
                             'Tư vấn gia đình theo dõi đến 6-9 tháng tuổi, nếu không tự thông màng sẽ chuyển khám '
                             'chuyên khoa Mắt để thông lệ đạo.',
                             'Vệ sinh dử mắt bằng gạc vô khuẩn tẩm nước muối ấm, hướng dẫn mẹ cách rửa tay sạch trước '
                             'khi xoa bóp tuyến lệ cho bé.',
                             'Hẹn khám lại sau 1 tháng đánh giá mức độ ứ đọng dịch lệ, giải thích khả năng tự thoái '
                             'triển nhờ động tác day đúng kỹ thuật.'],
    'bien_the_kham': [   'Mắt ướt đọng nước góc trong, ấn vùng túi lệ khóe mắt phải trào ra ít dịch nhầy đục, củng mạc '
                         'mắt trắng bóng bình thường.',
                         'Khóe trong mắt phải ứ đọng nhiều nước mắt và dử nhầy, mi mắt hơi dính nhẹ lúc mở, giác mạc '
                         'trong suốt không xước.',
                         'Ấn nhẹ ngón trỏ vào vùng góc trong mí mắt trào dịch mủ nhầy qua điểm lệ, củng mạc không '
                         'cương tụ đỏ.',
                         'Mắt phải luôn ướt đẫm nước, da quanh bờ mi hơi nề nhẹ do tiếp xúc dịch mắt liên tục, đồng tử '
                         'tròn phản xạ ánh sáng tốt.',
                         'Dịch nhầy tích tụ ở khóe mắt trong bên phải, túi lệ giãn nhẹ mềm không sưng đỏ cấp tính, mắt '
                         'trái bình thường.',
                         'Khám mắt bằng đèn soi: giác mạc trong, tiền phòng sạch, bờ mi đọng lớp nhầy trong suốt, ấn '
                         'khóe trào chất tiết nhầy.'],
    'chan_doan': 'Tắc lệ đạo sơ sinh bên phải bẩm sinh.',
    'chinh': [   'chảy nước mắt sống thường xuyên ở một hoặc cả hai mắt',
                 'dử mắt dính vàng nhạt xuất hiện liên tục sau khi ngủ dậy',
                 'mắt lúc nào cũng ngấn nước long lanh dù không quấy khóc'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'mắt',
    'ke_hoach': 'Hướng dẫn phụ huynh kỹ thuật mát-xa day túi lệ góc mắt đúng cách hàng ngày, vệ sinh mắt bằng nước '
                'muối sinh lý 0.9% và nhỏ tobradex nếu có bội nhiễm.',
    'kham': 'Mắt ướt đọng nước góc trong, ấn vùng túi lệ khóe mắt phải trào ra ít dịch nhầy đục, củng mạc mắt trắng '
            'bóng bình thường.',
    'nhom': 'nhi',
    'phu': [   'vùng góc trong khóe mắt hơi phồng nhẹ',
               'ấn vào vùng túi lệ thấy trào dịch nhầy hoặc mủ trắng đục',
               'kết mạc mắt không đỏ hoặc chỉ cương tụ rất nhẹ'],
    'ten': 'tắc lệ đạo sơ sinh'},
    {   'bien_the_chan_doan': [   'Rối loạn tăng động giảm chú ý thể kết hợp.',
                              'Rối loạn tăng động giảm chú ý thể ưu thế giảm chú ý.',
                              'Rối loạn tăng động giảm chú ý thể ưu thế tăng động bốc đồng.',
                              'Theo dõi rối loạn tăng động giảm chú ý có rối loạn hành vi phối hợp.',
                              'Rối loạn tăng động giảm chú ý mức độ trung bình ảnh hưởng học đường.',
                              'Nghi ngờ rối loạn tăng động giảm chú ý cần trắc nghiệm tâm lý chuyên biệt.'],
    'bien_the_ke_hoach': [   'Tư vấn liệu pháp can thiệp hành vi tâm lý, hướng dẫn gia đình và nhà trường phương pháp '
                             'giáo dục hành vi tích cực, hẹn hội chẩn tâm lý chuyên sâu.',
                             'Chỉ định làm bài test tâm lý Conners hoặc Vanderbilt cho phụ huynh và giáo viên đánh '
                             'giá, lập kế hoạch can thiệp tâm lý giáo dục.',
                             'Hướng dẫn phụ huynh chia nhỏ nhiệm vụ học tập thành từng khoảng 15 phút, khen thưởng kịp '
                             'thời khi trẻ tập trung hoàn thành.',
                             'Tư vấn quản lý hành vi tại nhà, hạn chế tối đa thời gian sử dụng tivi điện thoại, tăng '
                             'cường thể thao rèn tính kỷ luật.',
                             'Chuyển khám chuyên khoa Tâm thần Nhi để đánh giá chỉ định dùng thuốc methylphenidate nếu '
                             'can thiệp hành vi sau 3 tháng không chuyển biến.',
                             'Phối hợp với nhà trường xếp trẻ ngồi bàn đầu gần giáo viên, tạo môi trường học tập ít '
                             'yếu tố gây xao nhãng.'],
    'bien_the_kham': [   'Trẻ liên tục rời ghế đi lại trong phòng khám, sờ nghịch các dụng cụ y tế, trả lời vội vã cắt '
                         'ngang câu hỏi, không giữ được giao tiếp mắt lâu.',
                         'Trong buổi khám trẻ không chịu ngồi yên quá 2 phút, liên tục với tay lấy ống nghe và gõ bàn, '
                         'chú ý phân tán nhanh chóng.',
                         'Quan sát hành vi: mức độ hoạt động vận động quá mức, khó kiểm soát hành vi bốc đồng, phản '
                         'ứng vội vàng trước khi nghe hết câu hỏi.',
                         'Trẻ biểu hiện bồn chồn vận động rõ, chạy quanh phòng khám, khó tuân thủ các y lệnh đơn giản '
                         'dù hiểu được lời nói.',
                         'Khám thần kinh cơ bản không phát hiện tổn thương khu trú, đánh giá thang điểm hành vi '
                         'Vanderbilt cho thấy tăng động rõ rệt.',
                         'Trẻ luôn tay luôn chân nói nhiều liên tục, khó kiềm chế cảm xúc khi bị nhắc nhở ngồi xuống, '
                         'chú ý chọn lọc kém.'],
    'chan_doan': 'Rối loạn tăng động giảm chú ý thể kết hợp.',
    'chinh': [   'không thể ngồi yên một chỗ liên tục ngọ nguậy tay chân',
                 'mất tập trung chú ý dễ bị phân tâm bởi kích thích xung quanh',
                 'thường xuyên cắt ngang lời người khác hoặc hành động bốc đồng'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tâm thần',
    'ke_hoach': 'Tư vấn liệu pháp can thiệp hành vi tâm lý, hướng dẫn gia đình và nhà trường phương pháp giáo dục hành '
                'vi tích cực, hẹn hội chẩn tâm lý chuyên sâu.',
    'kham': 'Trẻ liên tục rời ghế đi lại trong phòng khám, sờ nghịch các dụng cụ y tế, trả lời vội vã cắt ngang câu '
            'hỏi, không giữ được giao tiếp mắt lâu.',
    'nhom': 'nhi',
    'phu': [   'kết quả học tập sa sút dù khả năng nhận thức bình thường',
               'thường xuyên làm mất đồ dùng học tập sách vở',
               'khó khăn trong việc chờ đợi đến lượt mình khi chơi trò chơi'],
    'ten': 'rối loạn tăng động giảm chú ý'},
    {   'bien_the_chan_doan': [   'Dậy thì sớm trung ương theo dõi.',
                              'Dậy thì sớm ngoại biên nghi do u buồng trứng hoặc u thượng thận.',
                              'Dậy thì sớm thể phát triển tuyến vú sớm đơn độc lành tính.',
                              'Theo dõi dậy thì sớm phụ thuộc gonadotropin.',
                              'Dậy thì sớm thực sự tiến triển nhanh cần điều trị ức chế.',
                              'Nghi ngờ dậy thì sớm vô căn ở trẻ em gái.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm nội tiết tố LH FSH estradiol hoặc testosterone, chụp X-quang tuổi xương '
                             'bàn tay trái và siêu âm tử cung buồng trứng.',
                             'Chỉ định test kích thích GnRH để phân biệt dậy thì sớm trung ương và ngoại biên, chụp '
                             'cộng hưởng từ sọ não vùng tuyến yên.',
                             'Chụp X-quang cổ tay trái đánh giá tuổi xương xem có cốt hóa sớm, siêu âm tử cung kiểm '
                             'tra kích thước nội mạc.',
                             'Tư vấn tâm lý cho gia đình và trẻ về những biến đổi cơ thể, hẹn làm bilan nội tiết '
                             'chuyên sâu tại khoa Nội tiết Nhi.',
                             'Xem xét chỉ định tiêm thuốc đồng vận GnRH tác dụng kéo dài để làm chậm dậy thì và bảo '
                             'tồn chiều cao trưởng thành.',
                             'Theo dõi tốc độ tăng trưởng chiều cao và giai đoạn Tanner mỗi 3 tháng, kiểm tra siêu âm '
                             'ổ bụng loại trừ khối u tăng tiết hormone.'],
    'bien_the_kham': [   'Bé gái 7 tuổi có tuyến vú phát triển giai đoạn Tanner 2 hai bên có khối nụ vú đường kính '
                         '2.5cm ấn đau nhẹ, lông mu rải rác Tanner 2.',
                         'Khám thấy nụ vú hai bên nhô rõ dưới quầng vú, quầng vú sẫm màu nhẹ, chiều cao tăng vọt 9cm '
                         'trong năm qua vượt bách phân vị 95.',
                         'Đánh giá Tanner: vú độ 3 có mô tuyến lan rộng ngoài quầng vú, lông mu mềm thưa dọc môi lớn, '
                         'da mặt có vài mụn trứng cá nhỏ.',
                         'Bé trai 8 tuổi đo thể tích tinh hoàn bằng thước Prader đạt 6ml (vượt ngưỡng 4ml), chiều dài '
                         'dương vật tăng, xuất hiện lông mu gốc dương vật.',
                         'Tuyến vú sờ thấy khối chắc tròn đường kính 2cm phía sau núm vú hai bên, không tiết dịch núm '
                         'vú, không có u vùng bụng.',
                         'Khám toàn thân: vóc dáng cao vượt trội so với tuổi, các đặc tính sinh dục phụ phát triển sớm '
                         'tương đương trẻ 11 tuổi.'],
    'chan_doan': 'Dậy thì sớm trung ương theo dõi.',
    'chinh': [   'phát triển tuyến vú hoặc tăng kích thước tinh hoàn trước tuổi chuẩn',
                 'tăng vọt chiều cao nhanh bất thường so với bạn bè cùng trang lứa',
                 'xuất hiện lông mu lông nách sớm trước 8 tuổi ở gái hoặc trước 9 tuổi ở trai'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nội tiết - chuyển hoá',
    'ke_hoach': 'Làm xét nghiệm nội tiết tố LH FSH estradiol hoặc testosterone, chụp X-quang tuổi xương bàn tay trái '
                'và siêu âm tử cung buồng trứng.',
    'kham': 'Bé gái 7 tuổi có tuyến vú phát triển giai đoạn Tanner 2 hai bên có khối nụ vú đường kính 2.5cm ấn đau '
            'nhẹ, lông mu rải rác Tanner 2.',
    'nhom': 'nhi',
    'phu': [   'mùi cơ thể giống người lớn và nổi mụn trứng cá vùng mặt',
               'tâm trạng thay đổi thất thường dễ cáu gắt nhạy cảm',
               'bé gái có thể xuất hiện dịch nhầy âm đạo hoặc kinh nguyệt sớm'],
    'ten': 'dậy thì sớm'},
    {   'bien_the_chan_doan': [   'Tưa miệng ở trẻ nhỏ do nấm Candida albicans.',
                              'Tưa miệng ở trẻ nhỏ mức độ vừa sau dùng kháng sinh.',
                              'Theo dõi tưa miệng ở trẻ nhỏ tái phát nhiều lần.',
                              'Tưa miệng ở trẻ nhỏ có viêm niêm mạc miệng do nấm.',
                              'Tưa miệng ở trẻ nhỏ thể lan tỏa toàn bộ khoang miệng.',
                              'Nhiễm nấm miệng tưa miệng ở trẻ nhỏ giai đoạn cấp.'],
    'bien_the_ke_hoach': [   'Rơ lưỡi miệng bằng dung dịch nystatin hoặc gel daktarin oral gel ngày 3-4 lần sau ăn, '
                             'khử trùng toàn bộ bình sữa và núm ti giả.',
                             'Dùng gạc vô khuẩn thấm hỗn dịch nystatin 100.000 UI/ml rơ nhẹ nhàng khắp khoang miệng 4 '
                             'lần/ngày trong 7 ngày liên tục.',
                             'Vệ sinh miệng sạch bằng gạc mềm sau mỗi cữ bú, thoa miconazole gel đường miệng nếu trẻ '
                             'trên 4 tháng tuổi và vệ sinh đầu vú mẹ.',
                             'Kê đơn thuốc kháng nấm tại chỗ nystatin, luộc sôi núm vú cao su và đồ chơi ngậm của trẻ '
                             'trong 15 phút mỗi ngày.',
                             'Hướng dẫn mẹ cách rơ miệng đúng kỹ thuật không cạo mạnh gây xước niêm mạc, kiểm tra nấm '
                             'núm vú mẹ để điều trị đồng thời.',
                             'Chỉ định dùng nystatin nhỏ giọt rơ lưỡi liên tục sau khi hết triệu chứng thêm 48 giờ để '
                             'tránh tái phát, tái khám sau 1 tuần.'],
    'bien_the_kham': [   'Niêm mạc lưỡi, vòm miệng và mặt trong hai má phủ nhiều mảng trắng đục như váng sữa bám chặt, '
                         'cố cạo để lại đáy đỏ trợt nhẹ.',
                         'Khoang miệng có nhiều đám giả mạc màu trắng như cặn sữa ở niêm mạc má và viền lợi, cạo nhẹ '
                         'thấy rớm máu li ti dưới đáy.',
                         'Lưỡi sần sùi bám dính lớp màng trắng kem dày khó lau sạch, niêm mạc khẩu cái đỏ rực rát, '
                         'không có loét sâu.',
                         'Khám họng miệng: mảng trắng dạng tuyết rơi rải rác trên vòm họng và niêm mạc môi trong, trẻ '
                         'né tránh khóc vì đau rát.',
                         'Mặt lưng lưỡi và hai bên má phủ giả mạc trắng ngà từng mảng lớn, xung quanh niêm mạc sung '
                         'huyết đỏ nhạt, hạch góc hàm không to.',
                         'Tổn thương dạng chấm trắng và mảng bựa trắng như sữa chua bám chặt vào niêm mạc cung hàm, '
                         'trẻ phản ứng đau khi chạm gạc.'],
    'chan_doan': 'Tưa miệng ở trẻ nhỏ do nấm Candida albicans.',
    'chinh': [   'mảng giả mạc màu trắng sữa bám chắc trên niêm mạc lưỡi và má',
                 'trẻ đau rát miệng quấy khóc khi bú hoặc từ chối bú bình',
                 'lau mảng trắng thấy khó bong và để lại nền niêm mạc đỏ rớm máu'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Rơ lưỡi miệng bằng dung dịch nystatin hoặc gel daktarin oral gel ngày 3-4 lần sau ăn, khử trùng toàn '
                'bộ bình sữa và núm ti giả.',
    'kham': 'Niêm mạc lưỡi, vòm miệng và mặt trong hai má phủ nhiều mảng trắng đục như váng sữa bám chặt, cố cạo để '
            'lại đáy đỏ trợt nhẹ.',
    'nhom': 'nhi',
    'phu': [   'chảy nhiều dãi quanh miệng mép hơi nứt đỏ',
               'tiền sử dùng kháng sinh đường uống dài ngày gần đây',
               'vú mẹ có cảm giác nóng rát ngứa ran khi cho con bú'],
    'ten': 'tưa miệng ở trẻ nhỏ'},
    {   'bien_the_chan_doan': [   'Chảy máu cam tái phát ở trẻ do giãn điểm mạch Kiesselbach.',
                              'Chảy máu cam tái phát ở trẻ thể nhẹ do viêm mũi dị ứng cào gãi.',
                              'Theo dõi chảy máu cam tái phát ở trẻ nghi rối loạn đông máu nhẹ.',
                              'Chảy máu cam tái phát ở trẻ do tổn thương điểm mạch mũi trước.',
                              'Chảy máu cam tái phát ở trẻ do thời tiết khô hanh kích ứng.',
                              'Chảy máu cam tái phát ở trẻ cần làm đông mạch đốt điện nhẹ.'],
    'bien_the_ke_hoach': [   'Đè ép cánh mũi cầm máu tại chỗ trong 10 phút, làm xét nghiệm đông máu cơ bản và bôi mỡ '
                             'kháng sinh dưỡng ẩm niêm mạc mũi.',
                             'Hướng dẫn trẻ ngồi thẳng đầu hơi cúi ra trước, dùng ngón tay ép chặt hai cánh mũi trong '
                             '10-15 phút và thở bằng miệng.',
                             'Xét nghiệm công thức máu kiểm tra số lượng tiểu cầu, PT, APTT, kê thuốc bôi tetracyclin '
                             'mỡ giữ ẩm vết loét vách ngăn.',
                             'Nhỏ nước muối sinh lý làm mềm niêm mạc mũi hàng ngày, bôi vaseline dưỡng ẩm tiền đình '
                             'mũi trước khi ngủ, cắt ngắn móng tay trẻ.',
                             'Giải thích phụ huynh tuyệt đối không ngửa cổ ra sau khi chảy máu tránh nuốt máu gây sặc, '
                             'hẹn hội chẩn chấm nitrat bạc nếu tái diễn.',
                             'Hội chẩn bác sĩ Tai Mũi Họng xem xét đông điện điểm mạch lưỡng cực nếu các mao mạch giãn '
                             'nở quá lớn hay chảy tái đi tái lại.'],
    'bien_the_kham': [   'Soi mũi trước thấy niêm mạc vách ngăn vùng điểm mạch Kiesselbach bên phải giãn mao mạch rõ, '
                         'có điểm loét trợt nông đang rỉ máu nhẹ.',
                         'Soi tiền đình mũi bên phải thấy búi mao mạch điểm Kiesselbach cương tụ đỏ rực, có cục máu '
                         'đông nhỏ mới hình thành bám ở vách ngăn.',
                         'Niêm mạc hốc mũi hai bên khô ráp, vách ngăn mũi phải có vết trợt xước mao mạch do cào gãi '
                         'ngoáy mũi, không thấy dị vật mũi.',
                         'Máu đỏ tươi rỉ từng giọt từ vách ngăn trước bên phải, sau khi lau sạch thấy điểm mạch giãn '
                         'ngoằn ngoèo rỉ máu thành vệt.',
                         'Khám tai mũi họng: họng sạch không đọng máu thành sau, soi mũi trước thấy niêm mạc mũi phù '
                         'nề nhẹ kèm điểm rỉ máu vùng Kiesselbach.',
                         'Vùng trước sụn vách ngăn bên phải có vết loét nhỏ đóng vảy tiết máu khô, mạch máu quanh viền '
                         'sung huyết nổi rõ hình chân nhện.'],
    'chan_doan': 'Chảy máu cam tái phát ở trẻ do giãn điểm mạch Kiesselbach.',
    'chinh': [   'chảy máu tươi từ một bên lỗ mũi tái phát nhiều lần',
                 'máu cam chảy tự nhiên khi ngủ dậy hoặc sau khi hắt hơi xì mũi',
                 'chảy máu thường tự cầm hoặc cầm sau khi bóp cánh mũi vài phút'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tai mũi họng',
    'ke_hoach': 'Đè ép cánh mũi cầm máu tại chỗ trong 10 phút, làm xét nghiệm đông máu cơ bản và bôi mỡ kháng sinh '
                'dưỡng ẩm niêm mạc mũi.',
    'kham': 'Soi mũi trước thấy niêm mạc vách ngăn vùng điểm mạch Kiesselbach bên phải giãn mao mạch rõ, có điểm loét '
            'trợt nông đang rỉ máu nhẹ.',
    'nhom': 'nhi',
    'phu': [   'thói quen hay ngoáy mũi hay dụi mũi do ngứa mũi',
               'thường xảy ra vào mùa đông hanh khô hoặc khi nằm phòng điều hòa lạnh',
               'niêm mạc mũi có vảy tiết khô màu nâu đỏ bám dính'],
    'ten': 'chảy máu cam tái phát ở trẻ'},
    {   'bien_the_chan_doan': [   'Lao phổi AFB dương tính thùy trên phổi phải.',
                              'Lao phổi thâm nhiễm đỉnh phổi có biến chứng ho ra máu nhẹ.',
                              'Theo dõi lao phổi thể AFB âm tính có tổn thương hang trên X-quang.',
                              'Lao phổi mới phát hiện chưa có bằng chứng kháng thuốc.',
                              'Nghi ngờ lao phổi tiến triển trên người suy giảm miễn dịch.',
                              'Lao phổi tái phát có vi khuẩn học xác định.'],
    'bien_the_ke_hoach': [   'Chuyển phòng khám chuyên khoa Lao và Bệnh phổi đăng ký phác đồ chuẩn quốc gia '
                             '2RHZE/4RHE, xét nghiệm đờm GeneXpert và chụp X-quang phổi.',
                             'Lấy mẫu đờm 3 lần làm soi trực tiếp tìm AFB và xét nghiệm sinh học phân tử GeneXpert '
                             'MTB/RIF phát hiện kháng rifampicin.',
                             'Chụp phim X-quang ngực thẳng kiểm tra tổn thương thâm nhiễm hang hóa, xét nghiệm men '
                             'gan, chức năng thận trước khi bắt đầu dùng thuốc kháng lao.',
                             'Đăng ký quản lý điều trị DOTS tại trạm y tế địa phương, hướng dẫn cách ly phòng lây '
                             'nhiễm qua đường hô hấp cho người nhà.',
                             'Tư vấn dùng thuốc kháng lao đúng giờ đủ liều không được tự ý ngừng thuốc, theo dõi tác '
                             'dụng phụ của thuốc lên thị giác và chức năng gan.',
                             'Kê đơn hỗ trợ thuốc bổ gan silymarin và vitamin B6 phòng độc tính thần kinh của '
                             'isoniazid, hẹn kiểm tra đờm và men gan mỗi tháng.'],
    'bien_the_kham': [   'Thể trạng gầy yếu, nghe phổi có giảm rì rào phế nang và rải rác ran ẩm nhỏ hạt ở vùng đỉnh '
                         'phổi bên phải.',
                         'Bệnh nhân gầy gò da xanh, rung thanh tăng nhẹ vùng đỉnh phổi phải, gõ đục nhẹ dưới xương '
                         'đòn, nghe có tiếng ran nổ khô.',
                         'Khám phổi thấy lồng ngực hơi lép bên tổn thương, thông khí đỉnh phổi phải giảm rõ rệt, nghe '
                         'thấy tiếng thổi ống nhẹ.',
                         'Nghe phổi phát hiện vùng tổn thương thâm nhiễm đỉnh phổi có tiếng ran ẩm mịn khu trú không '
                         'mất đi sau khi ho, hạch ngoại biên không sờ thấy.',
                         'Khám thực thể: rì rào phế nang giảm hai phế trường ưu thế đỉnh phổi phải, nhịp thở 22 l/p, '
                         'SpO2 95% khí trời, tim đều rõ.',
                         'Dáng người hốc hác sút cân, lồng ngực di động kém ở nửa trên bên phải, nghe có ran nổ rải '
                         'rác ở liên sống bả bên phải.'],
    'chan_doan': 'Lao phổi AFB dương tính thùy trên phổi phải.',
    'chinh': [   'ho kéo dài trên ba tuần có đờm trắng đục hoặc ho ra máu tươi',
                 'sốt nhẹ về chiều kèm gai rét ớn lạnh vã mồ hôi trộm ban đêm',
                 'gầy sút cân nhanh chóng mệt mỏi suy nhược không rõ nguyên nhân'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Chuyển phòng khám chuyên khoa Lao và Bệnh phổi đăng ký phác đồ chuẩn quốc gia 2RHZE/4RHE, xét nghiệm '
                'đờm GeneXpert và chụp X-quang phổi.',
    'kham': 'Thể trạng gầy yếu, nghe phổi có giảm rì rào phế nang và rải rác ran ẩm nhỏ hạt ở vùng đỉnh phổi bên phải.',
    'nhom': 'cả hai',
    'phu': [   'đau tức ngực âm ỉ một bên tăng khi ho sâu',
               'khó thở nhẹ khi lao động gắng sức',
               'tiền sử tiếp xúc thường xuyên với người mắc bệnh lao phổi'],
    'ten': 'lao phổi'},
    {   'bien_the_chan_doan': [   'Viêm gan A cấp giai đoạn vàng da toàn phát.',
                              'Viêm gan A cấp thể thông thường có tăng men gan cao.',
                              'Theo dõi viêm gan A cấp thể ứ mật kéo dài.',
                              'Viêm gan A cấp khởi phát sau ăn thức ăn nhiễm khuẩn.',
                              'Nghi ngờ viêm gan A cấp có biểu hiện suy tế bào gan nhẹ.',
                              'Viêm gan A cấp tính chưa có biến chứng bệnh não gan.'],
    'bien_the_ke_hoach': [   'Xét nghiệm men gan ALT AST, bilirubin toàn phần trực tiếp, kháng thể Anti-HAV IgM, nghỉ '
                             'ngơi tuyệt đối tại giường và truyền dịch nâng đỡ gan.',
                             'Chỉ định xét nghiệm huyết thanh chẩn đoán Anti-HAV IgM khẳng định, làm đông máu PT/INR '
                             'theo dõi nguy cơ suy gan tối cấp.',
                             'Nghỉ ngơi tĩnh dưỡng hoàn toàn, áp dụng chế độ ăn giàu đạm dễ tiêu nhiều đường hoa quả '
                             'tươi, kiêng tuyệt đối bia rượu.',
                             'Truyền dung dịch glucose 10% bổ sung năng lượng, dùng các thuốc bổ trợ tế bào gan chứa '
                             'arginine, theo dõi nước tiểu 24 giờ.',
                             'Hướng dẫn vệ sinh ăn uống phòng ngừa lây truyền qua đường phân - miệng cho người sống '
                             'cùng nhà, tái khám kiểm tra men gan mỗi tuần.',
                             'Làm siêu âm ổ bụng khảo sát nhu mô gan và thành túi mật, theo dõi sát các dấu hiệu tiền '
                             'triệu của hôn mê gan.'],
    'bien_the_kham': [   'Da và củng mạc mắt vàng rực, sờ thấy gan to 2cm dưới bờ sườn mật độ mềm bờ tù ấn tức, lách '
                         'không to.',
                         'Vàng da nghệ toàn thân, củng mạc mắt vàng sẫm, gan dưới bờ sườn phải 1.5cm mật độ mềm bề mặt '
                         'nhẵn ấn đau tức nhẹ.',
                         'Khám bụng: hạ sườn phải đầy nhẹ, ấn tức vùng gan, túi mật không to, không có tuần hoàn bàng '
                         'hệ, phản ứng thành bụng âm tính.',
                         'Niêm mạc dưới lưỡi và da ngực vàng cam rõ rệt, gan mấp mé bờ sườn ấn tức rõ, rung gan âm '
                         'tính, không có phù mắt cá chân.',
                         'Khám thấy vàng da tiến triển nhanh sau đợt sốt rét run, gan to nhẹ ấn đau nhẹ nhàng, bụng '
                         'mềm không chướng.',
                         'Củng mạc mắt nhuộm vàng đậm, dấu hiệu ứ mật ngoại vi rõ, gan to nhẹ sờ thấy dưới góc sườn '
                         'phải, thể trạng mệt mỏi uể oải.'],
    'chan_doan': 'Viêm gan A cấp giai đoạn vàng da toàn phát.',
    'chinh': [   'vàng da và củng mạc mắt xuất hiện nhanh sau vài ngày sốt nhẹ',
                 'nước tiểu sẫm màu như nước vối hoặc nước trà đặc',
                 'chán ăn sợ dầu mỡ buồn nôn và nôn nao khó chịu'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Xét nghiệm men gan ALT AST, bilirubin toàn phần trực tiếp, kháng thể Anti-HAV IgM, nghỉ ngơi tuyệt '
                'đối tại giường và truyền dịch nâng đỡ gan.',
    'kham': 'Da và củng mạc mắt vàng rực, sờ thấy gan to 2cm dưới bờ sườn mật độ mềm bờ tù ấn tức, lách không to.',
    'nhom': 'cả hai',
    'phu': [   'đau tức âm ỉ vùng hạ sườn phải',
               'phân nhạt màu hoặc có màu xám như đất sét',
               'tiền sử ăn hải sản tươi sống hoặc sử dụng nguồn nước không đảm bảo'],
    'ten': 'viêm gan A cấp'},
    {   'bien_the_chan_doan': [   'Sốt thương hàn tuần lễ thứ hai nghi do Salmonella typhi.',
                              'Theo dõi sốt thương hàn thể thông thường chưa biến chứng.',
                              'Sốt thương hàn có biến chứng xuất huyết tiêu hóa nhẹ.',
                              'Nghi ngờ sốt thương hàn kháng fluoroquinolone.',
                              'Sốt thương hàn giai đoạn khởi phát tuần đầu.',
                              'Sốt thương hàn thể tiêu hóa có tiêu chảy phân rêu.'],
    'bien_the_ke_hoach': [   'Cấy máu làm kháng sinh đồ, xét nghiệm phản ứng Widal, điều trị kháng sinh nhóm '
                             'fluoroquinolone ciprofloxacin hoặc ceftriaxone đường tiêm truyền.',
                             'Chỉ định cấy máu 2 lần trước khi dùng kháng sinh, cấy phân tìm trực khuẩn thương hàn, '
                             'dùng ceftriaxone 2g/ngày truyền tĩnh mạch 10-14 ngày.',
                             'Làm xét nghiệm công thức máu kiểm tra bạch cầu giảm hoặc bình thường, phản ứng Widal '
                             'hiệu giá O và H, bù nước điện giải.',
                             'Nhập viện khoa Truyền nhiễm theo dõi sát biến chứng thủng ruột và chảy máu tiêu hóa ở '
                             'tuần thứ hai thứ ba, cho ăn cháo loãng dinh dưỡng.',
                             'Kê đơn azithromycin hoặc ciprofloxacin liều phù hợp, tuyệt đối không dùng thuốc xổ thuốc '
                             'tẩy ruột mạnh tránh nguy cơ thủng ruột.',
                             'Lập đường truyền tĩnh mạch hạ sốt bằng paracetamol cẩn trọng, theo dõi huyết áp mạch và '
                             'tính chất phân từng ca trực.'],
    'bien_the_kham': [   'Vẻ mặt thương hàn đờ đẫn, nhiệt độ 39.8 độ nhưng mạch chỉ 76 lần/phút, bụng chướng nhẹ, hố '
                         'chậu phải có tiếng óc ách, sờ thấy lách to độ 1.',
                         'Bệnh nhân li bì chậm chạp, sốt 40 độ nhưng mạch đập 78 nhịp/phút (phân ly mạch nhiệt), bụng '
                         'gõ vang trống vùng quanh rốn, lách sờ mấp mé bờ sườn.',
                         'Khám thấy da vùng ngực bụng có vài ban dát đỏ nhỏ 2-4mm ấn biến mất (hồng ban), hố chậu phải '
                         'ấn đau tức nhẹ có tiếng lạo xạo óc ách ruột.',
                         'Vẻ mặt phờ phạc mắt lờ đờ, lưỡi bẩn bựa trắng ở giữa bờ và chóp lưỡi đỏ rực (lưỡi thương '
                         'hàn), mạch chậm tương đối so với thân nhiệt.',
                         'Khám lâm sàng: sốt cao liên tục, bụng chướng hơi gõ vang, gan lách to nhẹ dưới bờ sườn, '
                         'không có phản ứng cảm ứng phúc mạc.',
                         'Trạng thái bán mê sảng đờ đẫn, sốt cao co giật nhẹ, mạch nẩy chậm 72 l/p, sờ nắn hố chậu '
                         'phải nghe tiếng ùng ục rõ.'],
    'chan_doan': 'Sốt thương hàn tuần lễ thứ hai nghi do Salmonella typhi.',
    'chinh': [   'sốt tăng dần từng ngày kiểu hình bậc thang kéo dài liên tục',
                 'mạch nhiệt độ phân ly mạch chậm so với mức độ sốt cao',
                 'bụng chướng óc ách kèm tiêu chảy phân màu xanh canh rêu hoặc táo bón'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Cấy máu làm kháng sinh đồ, xét nghiệm phản ứng Widal, điều trị kháng sinh nhóm fluoroquinolone '
                'ciprofloxacin hoặc ceftriaxone đường tiêm truyền.',
    'kham': 'Vẻ mặt thương hàn đờ đẫn, nhiệt độ 39.8 độ nhưng mạch chỉ 76 lần/phút, bụng chướng nhẹ, hố chậu phải có '
            'tiếng óc ách, sờ thấy lách to độ 1.',
    'nhom': 'cả hai',
    'phu': [   'vẻ mặt đờ đẫn vô cảm trạng thái typhos thờ ơ với ngoại cảnh',
               'đau đầu dữ dội âm ỉ mất ngủ kéo dài',
               'dát hồng ban rải rác nổi ở vùng ngực và bụng xuất hiện thoáng qua'],
    'ten': 'sốt thương hàn'},
    {   'bien_the_chan_doan': [   'Nhiễm COVID-19 thể nhẹ chưa có dấu hiệu suy hô hấp.',
                              'Nhiễm COVID-19 thể nhẹ giai đoạn khởi phát ngày thứ hai.',
                              'Theo dõi nhiễm COVID-19 thể nhẹ ở người đã tiêm đủ vaccine.',
                              'Nhiễm COVID-19 thể nhẹ có triệu chứng mất vị giác và khứu giác.',
                              'Nhiễm COVID-19 thể nhẹ không có yếu tố nguy cơ diễn tiến nặng.',
                              'Nhiễm virus SARS-CoV-2 thể nhẹ theo dõi cách ly tại nhà.'],
    'bien_the_ke_hoach': [   'Cách ly y tế tại nhà, xét nghiệm test nhanh kháng nguyên SARS-CoV-2, điều trị triệu '
                             'chứng hạ sốt giảm đau, súc họng nước muối và theo dõi SpO2.',
                             'Thực hiện test nhanh kháng nguyên định kỳ, uống paracetamol 500mg khi sốt trên 38.5 độ, '
                             'xịt mũi nước muối biển sâu ngày 3 lần.',
                             'Hướng dẫn bệnh nhân tự đo SpO2 bằng máy cầm tay ngày 3 lần, liên hệ y tế ngay nếu SpO2 '
                             'dưới 95% hoặc cảm giác khó thở hụt hơi.',
                             'Tư vấn chế độ dinh dưỡng đủ nước vitamin C và kẽm, nghỉ ngơi tại phòng thông thoáng '
                             'riêng biệt, đeo khẩu trang khi tiếp xúc người nhà.',
                             'Kê thuốc giảm ho long đờm thảo dược, viên ngậm sát khuẩn họng, tập các bài tập thở sâu '
                             'và vận động nhẹ nhàng tại chỗ.',
                             'Hẹn khám lại hoặc chuyển viện cấp cứu nếu xuất hiện thở nhanh trên 20 lần/phút, đau tức '
                             'ngực dữ dội hoặc tím tái đầu chi.'],
    'bien_the_kham': [   'Họng sung huyết đỏ nhẹ, không có mủ amidan, SpO2 98% khí phòng, phổi hai bên thông khí tốt '
                         'không nghe thấy tiếng ran bệnh lý.',
                         'Niêm mạc hầu họng đỏ rực, hai cuốn mũi phù nề ứ dịch trong, nhịp thở 18 l/p đều, đo SpO2 đầu '
                         'ngón tay đạt 97%, tim đều rõ.',
                         'Khám hô hấp: phổi rì rào phế nang êm dịu hai bên, không có tiếng rít thanh quản, lồng ngực '
                         'di động bình thường theo nhịp thở.',
                         'Trạng thái tỉnh táo tiếp xúc tốt, nhiệt độ 38.2 độ C, SpO2 99%, khám không phát hiện dấu '
                         'hiệu co kéo cơ hô hấp phụ.',
                         'Khám thực thể: họng đỏ hạt thành sau họng, tiếng thở thanh khí phế quản bình thường, không '
                         'nghe ran ẩm ran nổ ở hai đáy phổi.',
                         'Bệnh nhân mệt mỏi nhẹ, tiếng nói hơi khàn, nhịp thở 19 chu kỳ/phút, mạch 84 l/p huyết áp '
                         '120/75 mmHg, SpO2 ổn định 98%.'],
    'chan_doan': 'Nhiễm COVID-19 thể nhẹ chưa có dấu hiệu suy hô hấp.',
    'chinh': [   'sốt nhẹ đến vừa kèm gai rét và đau mỏi toàn thân',
                 'ho khan rát cổ họng hoặc nuốt đau như có gai đâm',
                 'mất khứu giác đột ngột không ngửi thấy mùi hoặc giảm vị giác'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Cách ly y tế tại nhà, xét nghiệm test nhanh kháng nguyên SARS-CoV-2, điều trị triệu chứng hạ sốt giảm '
                'đau, súc họng nước muối và theo dõi SpO2.',
    'kham': 'Họng sung huyết đỏ nhẹ, không có mủ amidan, SpO2 98% khí phòng, phổi hai bên thông khí tốt không nghe '
            'thấy tiếng ran bệnh lý.',
    'nhom': 'cả hai',
    'phu': [   'nghẹt mũi chảy nước mũi trong hắt hơi',
               'mệt mỏi uể oải chân tay rã rời',
               'tiêu chảy nhẹ vài lần hoặc đau đầu âm ỉ vùng trán'],
    'ten': 'nhiễm COVID-19 thể nhẹ'},
    {   'bien_the_chan_doan': [   'Bệnh do xoắn khuẩn leptospira thể vàng da xuất huyết hội chứng Weil.',
                              'Theo dõi bệnh do xoắn khuẩn leptospira thể thông thường không vàng da.',
                              'Bệnh do xoắn khuẩn leptospira biến chứng suy thận cấp và tổn thương gan.',
                              'Bệnh do xoắn khuẩn leptospira ngày thứ 5 nghi nguồn lây ngập lụt.',
                              'Nghi ngờ bệnh do xoắn khuẩn leptospira thể nhiễm trùng huyết.',
                              'Bệnh do xoắn khuẩn leptospira có hội chứng xuất huyết cơ vân.'],
    'bien_the_ke_hoach': [   'Lấy máu làm xét nghiệm ngưng kết vi lượng MAT, cấy máu, dùng kháng sinh đặc hiệu '
                             'penicillin G hoặc doxycycline tĩnh mạch và theo dõi chức năng thận.',
                             'Chỉ định tiêm truyền tĩnh mạch penicillin G 1.5 triệu đơn vị mỗi 6 giờ hoặc ceftriaxone '
                             '2g/ngày, xét nghiệm urea creatinine men gan CPK.',
                             'Làm phản ứng huyết thanh MAT khẳng định xoắn khuẩn Leptospira, bù dịch tích cực kiềm hóa '
                             'nước tiểu và theo dõi lượng nước tiểu từng giờ.',
                             'Nhập viện khoa Cấp cứu Truyền nhiễm điều trị tích cực, làm điện tâm đồ tìm biến chứng '
                             'viêm cơ tim, xét nghiệm đông máu toàn bộ.',
                             'Kê đơn kháng sinh doxycycline 100mg ngày 2 viên nếu thể nhẹ ngoại trú, theo dõi sát phản '
                             'ứng Jarisch-Herxheimer sau liều kháng sinh đầu.',
                             'Kiểm tra định kỳ creatin kinase CPK đánh giá tiêu cơ vân, hội chẩn lọc máu cấp cứu nếu '
                             'thiểu niệu vô niệu kèm kali máu tăng cao.'],
    'bien_the_kham': [   'Ấn vào cơ bắp chân hai bên bệnh nhân kêu đau chói dữ dội, củng mạc mắt sung huyết đỏ rực như '
                         'mắt cá chày không có mủ, da ánh vàng nhẹ.',
                         'Khám cơ thấy khối cơ bắp chuối căng cứng ấn đau nhảy dựng, kết mạc mắt cương tụ đỏ như mắt '
                         'thỏ, gan to 2cm dưới bờ sườn ấn đau tức.',
                         'Dấu hiệu sung huyết củng mạc mắt hai bên rất rõ không có tiết dịch, cơ tam đầu cẳng chân và '
                         'cơ đùi ấn đau co thắt, có chấm xuất huyết ở cẳng tay.',
                         'Thể trạng nhiễm độc rõ, nhiệt độ 39.5 độ C, vàng da nghệ nhẹ, củng mạc đỏ rực, ấn điểm cơ '
                         'bắp chân hai bên phản ứng đau né tránh mạnh.',
                         'Khám phát hiện hội chứng nhiễm trùng nhiễm độc toàn thân, cơ vân toàn thân đau nhức nhiều '
                         'nhất ở bắp chân, thận to nhẹ vùng hông lưng ấn đau tức.',
                         'Bệnh nhân đi lại khập khiễng do đau buốt cơ cẳng chân, mắt đỏ ngầu sung huyết mạch máu kết '
                         'mạc, da ngực có ban dát xuất huyết nhỏ.'],
    'chan_doan': 'Bệnh do xoắn khuẩn leptospira thể vàng da xuất huyết hội chứng Weil.',
    'chinh': [   'sốt cao đột ngột rét run kèm đau dữ dội cơ bắp đặc biệt là bắp chân',
                 'mắt đỏ rực do sung huyết kết mạc nhưng không chảy dử mắt',
                 'tiền sử tiếp xúc với nước lũ lội bùn đất ô nhiễm hoặc chất thải chuột'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Lấy máu làm xét nghiệm ngưng kết vi lượng MAT, cấy máu, dùng kháng sinh đặc hiệu penicillin G hoặc '
                'doxycycline tĩnh mạch và theo dõi chức năng thận.',
    'kham': 'Ấn vào cơ bắp chân hai bên bệnh nhân kêu đau chói dữ dội, củng mạc mắt sung huyết đỏ rực như mắt cá chày '
            'không có mủ, da ánh vàng nhẹ.',
    'nhom': 'cả hai',
    'phu': [   'da vàng củng mạc mắt vàng xuất hiện sau vài ngày sốt',
               'nước tiểu ít dần sẫm màu có cặn lắng hoặc tiểu buốt rắt',
               'chảy máu cam xuất huyết dưới da dạng chấm nốt rải rác'],
    'ten': 'bệnh do xoắn khuẩn leptospira'},
    {   'bien_the_chan_doan': [   'Viêm thận bể thận cấp bên phải nghi do vi khuẩn E. coli.',
                              'Viêm thận bể thận cấp thể sỏi tắc nghẽn đường tiểu.',
                              'Theo dõi viêm thận bể thận cấp biến chứng nhiễm khuẩn huyết.',
                              'Viêm thận bể thận cấp chưa có suy giảm chức năng thận cấp tính.',
                              'Viêm thận bể thận cấp nguyên phát đáp ứng kháng sinh tiêm.',
                              'Nghi ngờ viêm thận bể thận cấp tái phát trên cơ địa trào ngược.'],
    'bien_the_ke_hoach': [   'Cấy nước tiểu làm kháng sinh đồ, xét nghiệm tổng phân tích nước tiểu và cặn lắng, chỉ '
                             'định kháng sinh tĩnh mạch ceftriaxone kết hợp siêu âm thận.',
                             'Lấy nước tiểu giữa dòng cấy vi khuẩn trước liều kháng sinh đầu, bắt đầu điều trị '
                             'ceftriaxone 1-2g/ngày tiêm tĩnh mạch kết hợp truyền dịch.',
                             'Siêu âm hệ tiết niệu khẩn cấp tìm sỏi niệu quản gây ứ nước bể thận hoặc áp xe hóa, xét '
                             'nghiệm công thức máu bạch cầu và CRP tăng vọt.',
                             'Chỉ định nhập viện khoa Thận Tiết niệu theo dõi, truyền dịch bù nước 2-3 lít/ngày, dùng '
                             'thuốc hạ sốt giảm đau và giảm co thắt cơ trơn.',
                             'Xét nghiệm urea creatinine máu đánh giá chức năng thận, điều chỉnh liều kháng sinh theo '
                             'kết quả kháng sinh đồ sau 48-72 giờ.',
                             'Hội chẩn Ngoại Tiết niệu đặt ống thông JJ dẫn lưu bể thận khẩn cấp nếu có sỏi niệu quản '
                             'gây tắc nghẽn ứ mủ bể thận.'],
    'bien_the_kham': [   'Dấu hiệu rung thận vỗ hông lưng dương tính rõ rệt bên phải, điểm niệu quản trên ấn đau chói, '
                         'nhiệt độ 39 độ C.',
                         'Khám vùng hông lưng phải thấy cơ cạnh cột sống co cứng, vỗ nhẹ hố thắt lưng bệnh nhân đau '
                         'chói co rúm người (rung thận dương tính).',
                         'Khám bụng: điểm sườn lưng và điểm sườn cột sống bên phải ấn đau nhói, hố chậu phải mềm, bụng '
                         'không có phản ứng phúc mạc.',
                         'Bệnh nhân sốt cao rét run vã mồ hôi, ấn điểm đau niệu quản trên và giữa bên phải phản ứng '
                         'đau rõ, hố thắt lưng trái bình thường.',
                         'Dấu hiệu chạm thận và bập bềnh thận âm tính nhưng vỗ hông lưng bên tổn thương dương tính '
                         'mạnh, cầu bàng quang không căng.',
                         'Khám thực thể: hông thắt lưng bên phải đầy đau tức khi sờ nắn, nhịp tim nhanh 105 l/p theo '
                         'cơn sốt, huyết áp 130/80 mmHg ổn định.'],
    'chan_doan': 'Viêm thận bể thận cấp bên phải nghi do vi khuẩn E. coli.',
    'chinh': [   'sốt cao rét run đột ngột kèm đau quặn hoặc tức dữ dội vùng hông lưng',
                 'tiểu buốt tiểu rắt tiểu nhiều lần nước tiểu đục có mùi hôi',
                 'nước tiểu có thể có màu hồng đỏ rỉ máu cuối bãi'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'thận - tiết niệu',
    'ke_hoach': 'Cấy nước tiểu làm kháng sinh đồ, xét nghiệm tổng phân tích nước tiểu và cặn lắng, chỉ định kháng sinh '
                'tĩnh mạch ceftriaxone kết hợp siêu âm thận.',
    'kham': 'Dấu hiệu rung thận vỗ hông lưng dương tính rõ rệt bên phải, điểm niệu quản trên ấn đau chói, nhiệt độ 39 '
            'độ C.',
    'nhom': 'người lớn',
    'phu': [   'buồn nôn nôn mửa chán ăn mệt lả người',
               'tiền sử sỏi đường tiết niệu hoặc nhiễm khuẩn bàng quang gần đây',
               'cảm giác ớn lạnh gai rét tái phát nhiều cơn trong ngày'],
    'ten': 'viêm thận bể thận cấp'},
    {   'bien_the_chan_doan': [   'Suy thận cấp trước thận do mất nước và giảm thể tích tuần hoàn hiệu dụng.',
                              'Suy thận cấp trước thận thứ phát sau sốc giảm thể tích nôn ói.',
                              'Theo dõi suy thận cấp trước thận có toan chuyển hóa nhẹ.',
                              'Suy thận cấp trước thận do dùng thuốc lợi tiểu quá liều.',
                              'Suy thận cấp trước thận có nguy cơ hoại tử ống thận cấp nếu bù dịch chậm.',
                              'Nghi ngờ suy thận cấp trước thận trên nền bệnh thận mạn có sẵn.'],
    'bien_the_ke_hoach': [   'Bù dịch khẩn cấp bằng dung dịch natri clorid 0.9% hoặc Ringer lactat đường tĩnh mạch, '
                             'xét nghiệm urea creatinine điện giải đồ và đặt sonde tiểu.',
                             'Truyền tĩnh mạch nhanh 1000ml dung dịch đẳng trương trong 1-2 giờ đầu dưới sự theo dõi '
                             'sát áp lực tĩnh mạch trung tâm và thính chẩn phổi.',
                             'Đặt ống thông bàng quang lưu theo dõi thể tích nước tiểu từng giờ, mục tiêu phục hồi '
                             'lượng tiểu trên 0.5 ml/kg/giờ sau bù dịch.',
                             'Làm xét nghiệm tỷ số BUN/Creatinine máu tăng cao trên 20, natri niệu dưới 20 mEq/l và '
                             'phân suất bài tiết natri FeNa dưới 1%.',
                             'Tạm ngừng ngay toàn bộ các thuốc ức chế men chuyển, chẹn thụ thể ARB và thuốc giảm đau '
                             'chống viêm không steroid NSAID.',
                             'Đánh giá lại chức năng thận sau 24 giờ truyền dịch đầy đủ, nếu không cải thiện lượng '
                             'nước tiểu cần hội chẩn Thận học lọc máu hỗ trợ.'],
    'bien_the_kham': [   'Huyết áp tư thế nằm 90/60 mmHg, mạch nhanh nhỏ 110 lần/phút, tĩnh mạch cổ xẹp hoàn toàn ở tư '
                         'thế 45 độ, nếp véo da mất chậm.',
                         'Dấu hiệu mất nước nặng: niêm mạc lưỡi khô ráp như da cóc, mắt trũng sâu, mạch quay nhanh nhỏ '
                         'khó bắt, huyết áp tụt kẹp 85/55 mmHg.',
                         'Khám tuần hoàn thấy tĩnh mạch cảnh nông chìm lặn không thấy sóng mạch, chi lạnh ẩm, thời '
                         'gian đổ đầy mao mạch CRT kéo dài trên 3 giây.',
                         'Bệnh nhân mệt lả không tự ngồi dậy được, huyết áp tư thế đứng tụt 25 mmHg kèm choáng váng, '
                         'bàng quang xẹp không có nước tiểu.',
                         'Thể trạng suy kiệt do mất nước, nếp nhăn da bụng duy trì lâu sau khi buông tay, tim đập '
                         'nhanh đều tiếng tim mờ nhỏ.',
                         'Khám thực thể: dấu hiệu giảm thể tích nội mạch rõ rệt, nhịp thở nhanh nông bù toan chuyển '
                         'hóa, không có ran ứ đọng ở hai đáy phổi.'],
    'chan_doan': 'Suy thận cấp trước thận do mất nước và giảm thể tích tuần hoàn hiệu dụng.',
    'chinh': [   'lượng nước tiểu giảm đột ngột dưới 400ml trong 24 giờ thiểu niệu',
                 'khát nước dữ dội môi khô nứt nẻ mắt trũng sâu',
                 'mệt lả chóng mặt hoa mắt xây xẩm mặt mày khi đứng dậy'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'thận - tiết niệu',
    'ke_hoach': 'Bù dịch khẩn cấp bằng dung dịch natri clorid 0.9% hoặc Ringer lactat đường tĩnh mạch, xét nghiệm urea '
                'creatinine điện giải đồ và đặt sonde tiểu.',
    'kham': 'Huyết áp tư thế nằm 90/60 mmHg, mạch nhanh nhỏ 110 lần/phút, tĩnh mạch cổ xẹp hoàn toàn ở tư thế 45 độ, '
            'nếp véo da mất chậm.',
    'nhom': 'người lớn',
    'phu': [   'tiền sử mất nước nặng do nôn nhiều tiêu chảy cấp hoặc dùng thuốc lợi tiểu',
               'huyết áp tụt hoặc giảm rõ khi thay đổi tư thế từ nằm sang đứng',
               'da khô nhăn nheo véo da mất rất chậm'],
    'ten': 'suy thận cấp trước thận'},
    {   'bien_the_chan_doan': [   'Tiểu không tự chủ khi gắng sức ở phụ nữ độ 2.',
                              'Tiểu không tự chủ khi gắng sức thể đơn thuần cơ sàn chậu suy yếu.',
                              'Tiểu không tự chủ khi gắng sức sau sinh nhiều lần.',
                              'Theo dõi tiểu không tự chủ khi gắng sức có kèm sa thành âm đạo nhẹ.',
                              'Tiểu không tự chủ khi gắng sức mức độ trung bình ảnh hưởng chất lượng sống.',
                              'Nghi ngờ tiểu không tự chủ khi gắng sức thể hỗn hợp có bàng quang tăng hoạt.'],
    'bien_the_ke_hoach': [   'Hướng dẫn tập luyện bài tập cơ sàn chậu Kegel kiên trì hàng ngày, giảm cân nặng, điều '
                             'trị táo bón và hội chẩn phẫu thuật đặt dải băng nâng niệu đạo TOT nếu thất bại.',
                             'Lập phác đồ vật lý trị liệu phục hồi chức năng cơ đáy chậu với máy tập phản hồi sinh học '
                             'biofeedback 3 buổi/tuần trong 3 tháng.',
                             'Tư vấn chế độ sinh hoạt tránh uống nhiều nước trước khi đi ngủ, hạn chế cà phê trà rượu '
                             'bia và đồ uống có gas gây kích thích bàng quang.',
                             'Kê đơn kem estrogen thoa âm đạo tại chỗ nếu có teo niêm mạc do thiếu hụt nội tiết, điều '
                             'trị dứt điểm các cơn ho mạn tính.',
                             'Chỉ định đo niệu động học đánh giá áp lực đóng niệu đạo và chức năng cơ bàng quang để '
                             'loại trừ tiểu không kiểm soát do thôi thúc.',
                             'Hội chẩn bác sĩ Niệu Nữ xem xét phẫu thuật ít xâm lấn đặt dải băng nâng đỡ niệu đạo giữa '
                             'TVT hoặc TOT nếu điều trị nội khoa không đỡ.'],
    'bien_the_kham': [   'Khám tầng sinh môn phụ khoa thấy cơ đáy chậu nhão, làm nghiệm pháp ho gắng sức (cough stress '
                         'test) thấy nước tiểu rỉ ra tức thì qua lỗ niệu đạo.',
                         'Nghiệm pháp gắng sức dương tính: khi bệnh nhân ho mạnh ở tư thế sản khoa thấy nước tiểu phun '
                         'thành tia nhỏ qua lỗ tiểu ngoài.',
                         'Khám vùng đáy chậu thấy cơ thắt hậu môn và cơ nâng hậu môn co bóp yếu khi yêu cầu thắt cơ, '
                         'có sa nhẹ thành trước âm đạo độ 1.',
                         'Da vùng âm hộ và nếp gấp bẹn có mảng đỏ kích ứng nhẹ do tiếp xúc nước tiểu, lỗ niệu đạo '
                         'ngoài bình thường không viêm đỏ mủ.',
                         'Khám phụ khoa kết hợp: thành trước âm đạo dãn rộng tụt nhẹ, nghiệm pháp nghiệm pháp Bonney '
                         'nâng cổ bàng quang giúp ngừng són tiểu.',
                         'Đo lượng nước tiểu tồn dư sau khi đi tiểu bằng siêu âm dưới 30ml bình thường, nghiệm pháp '
                         'mang tã pad test dương tính thấm ướt 15g.'],
    'chan_doan': 'Tiểu không tự chủ khi gắng sức ở phụ nữ độ 2.',
    'chinh': [   'nước tiểu tự rỉ ra ngoài từng giọt hoặc thành dòng khi ho hắt hơi',
                 'són tiểu xuất hiện ngay khi cười to mang vác vật nặng hoặc chạy nhảy',
                 'phải thường xuyên mang băng vệ sinh hàng ngày để tránh ướt quần'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thận - tiết niệu',
    'ke_hoach': 'Hướng dẫn tập luyện bài tập cơ sàn chậu Kegel kiên trì hàng ngày, giảm cân nặng, điều trị táo bón và '
                'hội chẩn phẫu thuật đặt dải băng nâng niệu đạo TOT nếu thất bại.',
    'kham': 'Khám tầng sinh môn phụ khoa thấy cơ đáy chậu nhão, làm nghiệm pháp ho gắng sức (cough stress test) thấy '
            'nước tiểu rỉ ra tức thì qua lỗ niệu đạo.',
    'nhom': 'người lớn',
    'phu': [   'tiền sử sinh nở tự nhiên nhiều lần hoặc chuyển dạ đẻ khó',
               'cảm giác tự ti ngại ngùng hạn chế giao tiếp xã hội và thể thao',
               'da vùng sinh dục bẹn hay bị kích ứng mẩn đỏ do ẩm ướt liên tục'],
    'ten': 'tiểu không tự chủ khi gắng sức'},
    {   'bien_the_chan_doan': [   'Động kinh cơn co cứng co giật toàn thể cơn đơn độc giai đoạn sau cơn.',
                              'Động kinh cơn co cứng co giật toàn thể tái phát do quên uống thuốc.',
                              'Theo dõi động kinh cơn co cứng co giật toàn thể thứ phát sau chấn thương.',
                              'Động kinh cơn co cứng co giật toàn thể cơn lớn nghi căn nguyên mạch máu.',
                              'Động kinh cơn co cứng co giật toàn thể thể vô căn.',
                              'Cơn động kinh cơn co cứng co giật toàn thể có tổn thương cắn lưỡi.'],
    'bien_the_ke_hoach': [   'Ghi điện não đồ EEG tiêu chuẩn, chụp cộng hưởng từ sọ não MRI tìm tổn thương cấu trúc vỏ '
                             'não, kê thuốc kháng động kinh valproate natri hoặc levetiracetam.',
                             'Chỉ định đo điện não đồ video 24 giờ tìm sóng động kinh dạng nhọn sóng, chụp MRI sọ não '
                             '1.5 Tesla khảo sát thùy thái dương.',
                             'Khởi liều levetiracetam 500mg ngày 2 lần hoặc valproate natri 500mg/ngày, xét nghiệm '
                             'công thức máu và chức năng gan thận cơ bản.',
                             'Hướng dẫn gia đình kỹ năng sơ cứu an toàn khi lên cơn: đặt nằm nghiêng an toàn, không '
                             'nhét bất cứ vật gì vào miệng người bệnh.',
                             'Tư vấn tránh các yếu tố kích gợi cơn co giật như thức khuya thiếu ngủ, căng thẳng tâm lý '
                             'quá mức, uống rượu bia và ánh sáng chớp nháy.',
                             'Hẹn khám chuyên khoa Thần kinh định kỳ mỗi tháng, tuyệt đối không tự lái xe hoặc vận '
                             'hành máy móc nguy hiểm khi chưa kiểm soát được cơn.'],
    'bien_the_kham': [   'Trạng thái sau cơn co giật: bệnh nhân còn ngủ gà lú lẫn định hướng chậm, bờ bên lưỡi có vết '
                         'bầm rách rớm máu do cắn phải, không có liệt khu trú.',
                         'Bệnh nhân tỉnh chậm còn ngầy ngật lú lẫn nhẹ, đồng tử hai bên 3mm đều có phản xạ ánh sáng, '
                         'niêm mạc lưỡi rách rớm máu, phản xạ gân xương tứ chi nhạy.',
                         'Khám thần kinh sau cơn: glasgow 14 điểm, định hướng không gian thời gian chưa chuẩn xác, '
                         'không có dấu hiệu màng não, cơ lực hai bên đều nhau 5/5.',
                         'Dấu hiệu sau cơn động kinh: thở sâu nhịp đều, vết bầm cắn môi dưới và lưỡi, khám 12 đôi dây '
                         'thần kinh sọ không thấy tổn thương khu trú.',
                         'Khám thực thể: mệt mỏi rã rời, đau nhức cơ bắp toàn thân, dấu Babinski âm tính hai bên, phản '
                         'xạ nuốt bình thường.',
                         'Bệnh nhân tỉnh táo dần sau 30 phút, tiếp xúc được nhưng trả lời chậm, có vết trầy xước nông '
                         'ở cùi chỏ do ngã đập xuống sàn nhà.'],
    'chan_doan': 'Động kinh cơn co cứng co giật toàn thể cơn đơn độc giai đoạn sau cơn.',
    'chinh': [   'mất ý thức đột ngột ngã lăn ra đất kèm tiếng kêu rú ngắn',
                 'co cứng toàn thân sau đó co giật nhịp nhàng tứ chi liên tục',
                 'sùi bọt mép thở rít cắn vào lưỡi hoặc tiểu tiện mất tự chủ'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Ghi điện não đồ EEG tiêu chuẩn, chụp cộng hưởng từ sọ não MRI tìm tổn thương cấu trúc vỏ não, kê '
                'thuốc kháng động kinh valproate natri hoặc levetiracetam.',
    'kham': 'Trạng thái sau cơn co giật: bệnh nhân còn ngủ gà lú lẫn định hướng chậm, bờ bên lưỡi có vết bầm rách rớm '
            'máu do cắn phải, không có liệt khu trú.',
    'nhom': 'người lớn',
    'phu': [   'cơn co giật kéo dài khoảng 1 đến 3 phút rồi tự hết',
               'sau cơn rơi vào trạng thái lú lẫn ngủ gà đau đầu mỏi cơ toàn thân',
               'hoàn toàn không nhớ được các diễn biến xảy ra trong lúc lên cơn'],
    'ten': 'động kinh cơn co cứng co giật toàn thể'},
    {   'bien_the_chan_doan': [   'Nhồi máu não giai đoạn phục hồi tháng thứ ba di chứng liệt nửa người phải.',
                              'Nhồi máu não giai đoạn phục hồi có rối loạn ngôn ngữ diễn đạt Broca.',
                              'Theo dõi nhồi máu não giai đoạn phục hồi trên bệnh nhân tăng huyết áp và đái tháo '
                              'đường.',
                              'Nhồi máu não giai đoạn phục hồi bán cầu não trái di chứng co cứng cơ tháp.',
                              'Nhồi máu não giai đoạn phục hồi có nguy cơ đột quỵ tái phát cao.',
                              'Nhồi máu não giai đoạn phục hồi có hội chứng trầm cảm sau đột quỵ.'],
    'bien_the_ke_hoach': [   'Tập phục hồi chức năng vận động ngôn ngữ tích cực, duy trì thuốc kháng kết tập tiểu cầu '
                             'aspirin kết hợp statin liều cao kiểm soát huyết áp.',
                             'Chỉ định tập vật lý trị liệu vận động trị liệu tại trung tâm phục hồi chức năng 5 '
                             'buổi/tuần, châm cứu xoa bóp bấm huyệt hỗ trợ.',
                             'Uống thuốc chống huyết khối clopidogrel 75mg hoặc aspirin 81mg hàng ngày, atorvastatin '
                             '20mg buổi tối để ổn định mảng xơ vữa.',
                             'Kiểm soát huyết áp mục tiêu dưới 130/80 mmHg bằng thuốc amlodipine phối hợp ức chế men '
                             'chuyển, kiểm tra đường huyết đói định kỳ.',
                             'Hướng dẫn bài tập nói và phát âm phục hồi ngôn ngữ, tập nuốt từng ngụm nhỏ thức ăn sệt '
                             'để phòng tránh viêm phổi hít sặc.',
                             'Siêu âm Doppler động mạch cảnh kiểm tra mảng xơ vữa hẹp lòng mạch, hẹn tái khám chuyên '
                             'khoa Đột quỵ thần kinh mỗi tháng.'],
    'bien_the_kham': [   'Liệt nửa người bên phải: cơ lực tay phải 3/5, chân phải 4/5, tăng trương lực cơ kiểu co cứng '
                         'tháp, liệt dây VII trung ương méo miệng sang trái.',
                         'Dáng đi phát cỏ vung chân phải hình vòng cung, tay phải co gấp áp sát ngực, phản xạ gân '
                         'xương bên phải tăng mạnh kèm giật cơ bàn chân clonus.',
                         'Khám thần kinh: méo miệng bên phải rãnh mũi má phải mờ rõ, nâng lông mày hai bên đều nhau '
                         '(liệt mặt trung ương), nuốt nghẹn nhẹ.',
                         'Cơ lực nửa người bên trái giảm: tay trái 2/5 chân trái 3/5, dấu hiệu Babinski bên trái dương '
                         'tính, giảm cảm giác nông nửa người trái.',
                         'Bệnh nhân tự đứng được có người trợ giúp, bàn tay co cứng gập ngón khó xòe ra, nói ngọng lắp '
                         'bắp khó diễn đạt tròn vành rõ chữ.',
                         'Khám vận động: điểm Rankin sửa đổi mRS đạt 3 điểm, cơ lực chi trên 3/5 chi dưới 4/5, không '
                         'có rối loạn cảm giác sâu.'],
    'chan_doan': 'Nhồi máu não giai đoạn phục hồi tháng thứ ba di chứng liệt nửa người phải.',
    'chinh': [   'yếu hoặc liệt nửa người bên đối diện giảm khả năng cầm nắm đi lại',
                 'méo miệng nói ngọng phát âm khó hoặc nuốt nghẹn sặc chất lỏng',
                 'tê bì giảm cảm giác đau và xúc giác dọc nửa thân mình'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Tập phục hồi chức năng vận động ngôn ngữ tích cực, duy trì thuốc kháng kết tập tiểu cầu aspirin kết '
                'hợp statin liều cao kiểm soát huyết áp.',
    'kham': 'Liệt nửa người bên phải: cơ lực tay phải 3/5, chân phải 4/5, tăng trương lực cơ kiểu co cứng tháp, liệt '
            'dây VII trung ương méo miệng sang trái.',
    'nhom': 'người lớn',
    'phu': [   'trương lực cơ bên liệt bắt đầu tăng kiểu co cứng co gấp tay duỗi chân',
               'tiền sử tăng huyết áp đái tháo đường hoặc rung nhĩ đã điều trị cấp cứu',
               'tâm trạng dễ xúc động trầm cảm lo âu sau biến cố đột quỵ não'],
    'ten': 'nhồi máu não giai đoạn phục hồi'},
    {   'bien_the_chan_doan': [   'Chóng mặt tư thế kịch phát lành tính ống bán khuyên sau bên phải BPPV.',
                              'Chóng mặt tư thế kịch phát lành tính ống bán khuyên sau bên trái.',
                              'Theo dõi chóng mặt tư thế kịch phát lành tính ống bán khuyên ngang thể sỏi trong ống.',
                              'Chóng mặt tư thế kịch phát lành tính tái phát sau chấn thương đầu nhẹ.',
                              'Chóng mặt tư thế kịch phát lành tính thể sỏi mào tai cupulolithiasis.',
                              'Chóng mặt tư thế kịch phát lành tính đáp ứng tốt với nghiệm pháp Epley.'],
    'bien_the_ke_hoach': [   'Thực hiện nghiệm pháp tái định vị sỏi tai Epley bên phải giải phóng sỏi tai, kê thuốc ức '
                             'chế tiền đình betahistine ngắn ngày và hướng dẫn bài tập Brandt-Daroff tại nhà.',
                             'Tiến hành làm thủ thuật chuyển tư thế sỏi tai Epley 2 chu kỳ liên tiếp tại phòng khám, '
                             'dặn bệnh nhân giữ đầu thẳng không cúi gập trong 24 giờ.',
                             'Kê đơn betahistine 24mg ngày uống 2 lần trong 7 ngày giảm cảm giác mất thăng bằng dư âm, '
                             'kết hợp dimenhydrinate nếu buồn nôn nhiều.',
                             'Hướng dẫn bệnh nhân tự tập bài tập phục hồi chức năng tiền đình Brandt-Daroff sáng và '
                             'tối mỗi ngày 5 chu kỳ.',
                             'Tư vấn trấn an tâm lý giải thích đây là bệnh lý tai trong lành tính không phải tai biến '
                             'mạch máu não, tránh quay đầu quá đột ngột.',
                             'Hẹn khám lại sau 3 ngày đánh giá lại nghiệm pháp Dix-Hallpike, chuyển làm nghiệm pháp '
                             'Semont nếu sỏi còn tồn đọng.'],
    'bien_the_kham': [   'Thực hiện nghiệm pháp Dix-Hallpike bên phải dương tính: xuất hiện cơn chóng mặt dữ dội kèm '
                         'rung giật nhãn cầu xoay lên trên sau thời gian tiềm tàng 3 giây.',
                         'Nghiệm pháp Dix-Hallpike bên trái: sau khi hạ đầu thấy giật nhãn cầu xoay đập lên trên kéo '
                         'dài 25 giây kèm nôn nao sợ hãi.',
                         'Khám mắt: rung giật nhãn cầu ngang xoay có tính kiệt sức khi lặp lại nghiệm pháp, không có '
                         'rung giật nhãn cầu tự phát ở tư thế ngồi.',
                         'Khám thần kinh cơ bản: nghiệm pháp ngón tay chỉ mũi bình thường, dáng đi Romberg không ngã '
                         'về một bên cố định, không liệt dây thần kinh sọ.',
                         'Thính lực đồ bình thường hai tai, màng nhĩ sáng bóng không có tổn thương tai giữa, nghiệm '
                         'pháp lắc đầu không phát hiện tổn thương tiền đình trung ương.',
                         'Khám tiền đình: nghiệm pháp nằm nghiêng đầu Pagnini-McClure âm tính, nghiệm pháp '
                         'Dix-Hallpike bên phải tái hiện chính xác triệu chứng chóng mặt của bệnh nhân.'],
    'chan_doan': 'Chóng mặt tư thế kịch phát lành tính ống bán khuyên sau bên phải BPPV.',
    'chinh': [   'cơn chóng mặt dữ dội đồ vật xoay tròn lộn nhào khi thay đổi tư thế đầu',
                 'chóng mặt xuất hiện khi nghiêng người trở mình trên giường hoặc ngửa cổ',
                 'mỗi cơn chóng mặt kéo dài rất ngắn dưới một phút rồi dịu dần'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Thực hiện nghiệm pháp tái định vị sỏi tai Epley bên phải giải phóng sỏi tai, kê thuốc ức chế tiền '
                'đình betahistine ngắn ngày và hướng dẫn bài tập Brandt-Daroff tại nhà.',
    'kham': 'Thực hiện nghiệm pháp Dix-Hallpike bên phải dương tính: xuất hiện cơn chóng mặt dữ dội kèm rung giật nhãn '
            'cầu xoay lên trên sau thời gian tiềm tàng 3 giây.',
    'nhom': 'người lớn',
    'phu': [   'buồn nôn nôn nao dữ dội vã mồ hôi lạnh trong cơn',
               'cảm giác bồng bềnh mất thăng bằng sau khi cơn chóng mặt đã qua',
               'hoàn toàn không có ù tai giảm thính lực hay đau đầu kèm theo'],
    'ten': 'chóng mặt tư thế kịch phát lành tính'},
    {   'bien_the_chan_doan': [   'Bệnh thần kinh ngoại biên do đái tháo đường giai đoạn có tổn thương sợi thần kinh cảm '
                              'giác.',
                              'Bệnh thần kinh ngoại biên do đái tháo đường thể đau thần kinh mạn tính.',
                              'Theo dõi bệnh thần kinh ngoại biên do đái tháo đường có nguy cơ loét bàn chân đái tháo '
                              'đường cao.',
                              'Bệnh thần kinh ngoại biên do đái tháo đường thể sợi nhỏ ưu thế.',
                              'Bệnh thần kinh ngoại biên do đái tháo đường hỗn hợp cảm giác và vận động.',
                              'Bệnh thần kinh ngoại biên do đái tháo đường tiến triển sau 10 năm mắc bệnh.'],
    'bien_the_ke_hoach': [   'Kiểm soát đường huyết mục tiêu HbA1c dưới 7%, điều trị đau thần kinh bằng gabapentin '
                             'hoặc pregabalin, bổ sung acid alpha-lipoic và hướng dẫn chăm sóc bảo vệ bàn chân.',
                             'Chỉ định đo điện cơ và tốc độ dẫn truyền thần kinh EMG chi dưới, kê đơn pregabalin 75mg '
                             'uống buổi tối tăng dần liều nếu cần.',
                             'Dùng duloxetine 30-60mg/ngày để điều trị đau dây thần kinh, kết hợp vitamin B1, B6, B12 '
                             'liều cao hỗ trợ dinh dưỡng bao myelin sợi thần kinh.',
                             'Hướng dẫn bệnh nhân kiểm tra lòng bàn chân mỗi ngày bằng gương soi, chọn giày dép mềm '
                             'vừa vặn, không bao giờ đi chân đất ra ngoài.',
                             'Thoa kem dưỡng ẩm chống nứt nẻ gót chân mỗi tối, cắt móng chân thẳng ngang không cắt '
                             'khóe sâu tránh nhiễm trùng mưng mủ.',
                             'Điều chỉnh phác đồ thuốc hạ đường huyết tối ưu hóa insulin hoặc metformin, đo lại điện '
                             'thế cảm giác và tái khám bàn chân mỗi 3 tháng.'],
    'bien_the_kham': [   'Giảm rõ cảm giác nông và cảm giác rung âm thoa 128Hz ở hai bàn chân lên đến mắt cá, phản xạ '
                         'gân gót hai bên mất, nghiệm pháp sợi đơn Semmes-Weinstein dương tính mất cảm giác bảo vệ.',
                         'Khám bàn chân: mất cảm giác với sợi monofilament 10g tại 4/10 vị trí gan chân, phản xạ gân '
                         'gót Achilles mất đối xứng hai bên, da mu chân khô ráp rụng lông.',
                         'Đo cảm giác nhiệt độ thấy mất cảm giác nóng lạnh từ cổ chân trở xuống, gõ phản xạ gân bánh '
                         'chè giảm nhẹ, không có teo cơ cục bộ bàn chân.',
                         'Bàn chân hai bên có tăng cảm giác đau nhẹ khi chà nhẹ gạc (allodynia), nhưng cảm giác phân '
                         'biệt hai điểm và cảm giác sâu lại giảm rõ rệt.',
                         'Khám mạch máu ngoại vi: mạch mu chân và mạch chày sau bắt rõ hai bên, các khớp bàn ngón cử '
                         'động tốt, chưa có biến dạng bàn chân Charcot hay vết loét tì đè.',
                         'Dấu hiệu tổn thương thần kinh cảm giác ngoại biên rõ: cảm giác rung âm thoa mất tại ngón '
                         'chân cái, giảm phản xạ gân xương chi dưới kiểu bít tất.'],
    'chan_doan': 'Bệnh thần kinh ngoại biên do đái tháo đường giai đoạn có tổn thương sợi thần kinh cảm giác.',
    'chinh': [   'tê bì châm chích bỏng rát đối xứng hai bàn chân kiểu đi găng đi tất',
                 'đau nhức buốt sâu trong xương tăng nhiều về đêm gây mất ngủ',
                 'cảm giác bàn chân như đi trên đệm bông hoặc mất cảm giác tiếp đất'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Kiểm soát đường huyết mục tiêu HbA1c dưới 7%, điều trị đau thần kinh bằng gabapentin hoặc pregabalin, '
                'bổ sung acid alpha-lipoic và hướng dẫn chăm sóc bảo vệ bàn chân.',
    'kham': 'Giảm rõ cảm giác nông và cảm giác rung âm thoa 128Hz ở hai bàn chân lên đến mắt cá, phản xạ gân gót hai '
            'bên mất, nghiệm pháp sợi đơn Semmes-Weinstein dương tính mất cảm giác bảo vệ.',
    'nhom': 'người lớn',
    'phu': [   'tiền sử mắc bệnh đái tháo đường típ 2 nhiều năm kiểm soát đường huyết kém',
               'da hai bàn chân khô ráp nứt nẻ giảm tiết mồ hôi',
               'dễ bị phồng rộp loét trợt bàn chân mà không cảm thấy đau đớn'],
    'ten': 'bệnh thần kinh ngoại biên do đái tháo đường'},
    {   'bien_the_chan_doan': [   'Đau cơ xơ hoá mức độ vừa theo tiêu chuẩn ACR.',
                              'Đau cơ xơ hoá có kèm rối loạn giấc ngủ trầm cảm thứ phát.',
                              'Theo dõi đau cơ xơ hoá thể đau lan tỏa mạn tính kèm sương mù não.',
                              'Đau cơ xơ hoá kháng trị với thuốc giảm đau thông thường NSAID.',
                              'Đau cơ xơ hoá khởi phát sau stress tâm lý nặng kéo dài.',
                              'Hội chứng đau cơ xơ hoá kết hợp hội chứng mệt mỏi mạn tính.'],
    'bien_the_ke_hoach': [   'Tư vấn liệu pháp hành vi nhận thức, tập thể dục nhịp điệu dưới nước hoặc đi bộ nhẹ '
                             'nhàng, kê thuốc điều hòa đau duloxetine hoặc pregabalin và cải thiện giấc ngủ.',
                             'Khởi đầu bằng amitriptyline 10-25mg uống trước khi ngủ 2 giờ để phục hồi giấc ngủ sâu, '
                             'phối hợp pregabalin 75mg giảm dẫn truyền cảm giác đau trung ương.',
                             'Chỉ định tập yoga thiền định và vật lý trị liệu phục hồi chức năng nhẹ nhàng, giải thích '
                             'cơ chế quá mẫn cảm đau trung ương cho người bệnh hiểu.',
                             'Tránh dùng thuốc giảm đau nhóm opioid hoặc corticoid kéo dài do không có hiệu quả và gây '
                             'nghiện lệ thuộc thuốc.',
                             'Kê đơn duloxetine 30mg tăng dần lên 60mg/ngày, kết hợp tư vấn tâm lý trị liệu giảm tải '
                             'căng thẳng áp lực công việc gia đình.',
                             'Lập thời gian biểu sinh hoạt đều đặn, tắm nước ấm trước khi ngủ, theo dõi mức độ đau và '
                             'chất lượng giấc ngủ qua thang điểm VAS mỗi tháng.'],
    'bien_the_kham': [   'Ấn đau chói tại nhiều điểm kích hoạt điểm đau chuyên biệt (tender points) vùng chẩm, cơ '
                         'thang, cơ trên gai, lồi cầu ngoài và mào chậu hai bên, các khớp không sưng nóng đỏ.',
                         'Thăm khám theo tiêu chuẩn ACR 1990: dương tính 13/18 điểm đau nhạy cảm áp lực ngón tay '
                         '4kg/cm2, vận động khớp toàn thân bảo tồn không hạn chế.',
                         'Cơ bắp vùng cổ vai gáy và thắt lưng co cứng tăng cảm giác đau khi sờ nắn, không có teo cơ, '
                         'các khớp ngoại biên hoàn toàn không có viêm màng hoạt dịch.',
                         'Khám thần kinh và cơ xương khớp: cơ lực 5/5 tứ chi, phản xạ gân xương bình thường, chỉ số '
                         'đau lan tỏa WPI đạt 11/19 điểm, mức độ nặng triệu chứng SS đạt 8/12.',
                         'Bệnh nhân nhăn mặt kêu đau khi ấn vào cơ thang hai bên, khớp gối và khớp cổ tay không tràn '
                         'dịch, xét nghiệm các chỉ số viêm máu lắng âm tính.',
                         'Thể trạng mệt mỏi ủ rũ, điểm đau đối xứng ở vùng gân cơ cổ vai gáy và bờ trong xương bả vai '
                         'đau chói rõ rệt, vận động cột sống mềm mại.'],
    'chan_doan': 'Đau cơ xơ hoá mức độ vừa theo tiêu chuẩn ACR.',
    'chinh': [   'đau mỏi lan tỏa khắp cơ thể đau cả hai bên cơ thể trên và dưới thắt lưng',
                 'mệt mỏi kiệt sức mãn tính ngủ dậy không thấy hồi phục năng lượng',
                 'đau nhức cơ bắp kéo dài liên tục trên ba tháng không rõ nguyên nhân chấn thương'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Tư vấn liệu pháp hành vi nhận thức, tập thể dục nhịp điệu dưới nước hoặc đi bộ nhẹ nhàng, kê thuốc '
                'điều hòa đau duloxetine hoặc pregabalin và cải thiện giấc ngủ.',
    'kham': 'Ấn đau chói tại nhiều điểm kích hoạt điểm đau chuyên biệt (tender points) vùng chẩm, cơ thang, cơ trên '
            'gai, lồi cầu ngoài và mào chậu hai bên, các khớp không sưng nóng đỏ.',
    'nhom': 'người lớn',
    'phu': [   'rối loạn giấc ngủ hay thức giấc nửa đêm khó ngủ lại',
               'rối loạn nhận thức giảm khả năng tập trung sương mù não fibro-fog',
               'kèm theo hội chứng ruột kích thích đau đầu căng thẳng hoặc lo âu'],
    'ten': 'đau cơ xơ hoá'},
    {   'bien_the_chan_doan': [   'Viêm gân lồi cầu ngoài xương cánh tay bên phải tennis elbow.',
                              'Viêm gân lồi cầu ngoài xương cánh tay bên trái mạn tính do nghề nghiệp.',
                              'Theo dõi viêm gân lồi cầu ngoài xương cánh tay có rách vi thể gân duỗi.',
                              'Viêm gân lồi cầu ngoài xương cánh tay đợt cấp tính đau nhiều.',
                              'Viêm điểm bám gân lồi cầu ngoài xương cánh tay thể dai dẳng tái phát.',
                              'Hội chứng khuỷu tay quần vợt viêm gân lồi cầu ngoài cánh tay.'],
    'bien_the_ke_hoach': [   'Bất động tương đối cổ bàn tay, chườm lạnh, dùng thuốc giảm đau chống viêm không steroid '
                             'NSAID tại chỗ và tập bài tập kéo giãn gân duỗi cổ tay.',
                             'Đeo băng nẹp cẳng tay đối lực (counterforce brace) cách dưới mỏm lồi cầu ngoài 2-3cm khi '
                             'làm việc, chườm đá 15 phút ngày 3 lần.',
                             'Uống thuốc kháng viêm celecoxib 200mg/ngày trong 10 ngày kết hợp bôi gel diclofenac tại '
                             'chỗ mỏm lồi cầu ngoài.',
                             'Chỉ định siêu âm phần mềm khớp khuỷu kiểm tra mức độ dày phù nề hoặc vi rách điểm bám '
                             'gân duỗi cổ tay quay ngắn.',
                             'Xem xét tiêm huyết tương giàu tiểu cầu PRP hoặc tiêm corticoid cục bộ dưới hướng dẫn '
                             'siêu âm nếu các biện pháp bảo tồn sau 6 tuần thất bại.',
                             'Hướng dẫn bài tập phục hồi chức năng kéo giãn cơ duỗi và tập tăng cường sức cơ co cơ ly '
                             'tâm (eccentric exercise) với tạ nhẹ.'],
    'bien_the_kham': [   'Ấn vào mỏm lồi cầu ngoài xương cánh tay đau chói điểm bám gân, nghiệm pháp Cozen và nghiệm '
                         'pháp Mill dương tính rõ rệt.',
                         'Nghiệm pháp Cozen dương tính: bệnh nhân gập mu cổ tay có lực kháng cự xuất hiện cơn đau nhói '
                         'thốn tại vị trí lồi cầu ngoài cánh tay phải.',
                         'Nghiệm pháp Mill dương tính: duỗi thẳng khuỷu tay úp sấp bàn tay và gập lòng cổ tay thụ động '
                         'gây căng đau nhức vùng gân duỗi cổ tay quay ngắn.',
                         'Khám khuỷu tay: biên độ vận động gập duỗi khớp khuỷu bình thường, không có tràn dịch ổ khớp, '
                         'ấn điểm bám gân cơ duỗi chung đau buốt nhảy dựng.',
                         'Test nâng ghế Chair test dương tính: bệnh nhân không thể nhấc chiếc ghế tựa bằng cách úp bàn '
                         'tay duỗi khuỷu vì đau thốn lồi cầu ngoài.',
                         'Sờ nắn vị trí lồi cầu ngoài bên phải thấy gân hơi dày nhẹ so với bên đối diện, không nóng đỏ '
                         'sưng nề, lực nắm bàn tay giảm 30% do đau.'],
    'chan_doan': 'Viêm gân lồi cầu ngoài xương cánh tay bên phải tennis elbow.',
    'chinh': [   'đau nhói vùng mỏm lồi cầu ngoài khuỷu tay lan xuống cẳng tay',
                 'đau tăng lên khi duỗi cổ tay ngửa bàn tay hoặc cầm nắm vật nặng',
                 'cầm cốc nước vặn nắp chai hay vặn tay nắm cửa cũng thấy đau thốn'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Bất động tương đối cổ bàn tay, chườm lạnh, dùng thuốc giảm đau chống viêm không steroid NSAID tại chỗ '
                'và tập bài tập kéo giãn gân duỗi cổ tay.',
    'kham': 'Ấn vào mỏm lồi cầu ngoài xương cánh tay đau chói điểm bám gân, nghiệm pháp Cozen và nghiệm pháp Mill '
            'dương tính rõ rệt.',
    'nhom': 'người lớn',
    'phu': [   'tiền sử chơi tennis cầu lông hoặc công việc sử dụng cổ tay lặp đi lặp lại',
               'lực nắm bàn tay yếu đi rõ rệt do cảm giác đau buốt ở khuỷu tay',
               'vùng ngoài khuỷu tay có thể hơi sưng nhẹ nhưng không đỏ'],
    'ten': 'viêm gân lồi cầu ngoài xương cánh tay'},
    {   'bien_the_chan_doan': [   'Gãy xương cổ tay do ngã gãy kín đầu dưới xương quay kiểu Colles bên phải.',
                              'Gãy xương cổ tay do ngã gãy đầu dưới xương quay di lệch gập góc ra sau.',
                              'Gãy xương cổ tay do ngã kiểu Smith di lệch gập góc ra trước.',
                              'Theo dõi gãy xương cổ tay do ngã có kèm gãy mỏm trâm trụ.',
                              'Gãy xương cổ tay do ngã thấu khớp cần phẫu thuật kết hợp xương.',
                              'Gãy kín đầu dưới xương quay gãy xương cổ tay do ngã chưa có biến chứng mạch máu.'],
    'bien_the_ke_hoach': [   'Cố định tạm thời bằng nẹp cẳng bàn tay, chụp X-quang cổ tay thẳng nghiêng khẩn cấp, giảm '
                             'đau và chuyển chuyên khoa Chấn thương Chỉnh hình nắn bó bột.',
                             'Đặt nẹp bột cẳng bàn tay cố định tư thế chức năng, tiêm thuốc giảm đau tramadol phối hợp '
                             'paracetamol, làm phim X-quang 2 tư thế thẳng nghiêng.',
                             'Hội chẩn bác sĩ Chấn thương Chỉnh hình thực hiện thủ thuật nắn kín ổ gãy dưới gây tê ổ '
                             'gãy và bất động bằng bột cẳng bàn tay ôm ngón.',
                             'Chụp X-quang kiểm tra lại sau nắn bột xem trục xương và góc nghiêng mặt khớp xương quay '
                             'đã được phục hồi đúng giải phẫu hay chưa.',
                             'Kê đơn thuốc giảm đau chống phù nề alphachymotrypsin, hướng dẫn bệnh nhân treo tay cao '
                             'trước ngực và theo dõi sát dấu hiệu chèn ép bột.',
                             'Chỉ định phẫu thuật mổ mở kết hợp xương bằng nẹp vít khóa nếu gãy vụn nát thấu khớp hoặc '
                             'nắn chỉnh thất bại.'],
    'bien_the_kham': [   'Cổ tay phải biến dạng điển hình hình lưng dĩa (Colles), sưng nề bầm tím vùng đầu dưới xương '
                         'quay, ấn có điểm đau chói và lạo xạo xương, mạch quay bắt rõ.',
                         'Biến dạng lệch trục cổ tay rõ rệt: nhìn nghiêng hình mu thìa dĩa, nhìn thẳng hình lưỡi lê, '
                         'sưng nề căng mọng quanh khớp cổ tay.',
                         'Khám chấn thương: sờ thấy gờ đầu dưới xương quay nhô ra sau, ấn điểm đau chói tại vị trí gãy '
                         'xương cách khe khớp 2cm, mất cơ năng cổ tay.',
                         'Đầu ngón tay ấm hồng, thời gian hồi phục màu da CRT dưới 2 giây, cảm giác xúc giác các đầu '
                         'ngón tay còn tốt, không có dấu hiệu chèn ép khoang.',
                         'Khám thực thể: da cổ tay căng bóng bầm tím lan xuống mu bàn tay, không có vết rách da hở '
                         'xương gãy, mạch quay và mạch trụ hai bên đều rõ.',
                         'Bệnh nhân đau đớn co rúm người khi chạm nhẹ vào cổ tay, cử động thụ động sấp ngửa cẳng tay '
                         'bị khóa cứng hoàn toàn do đau chói.'],
    'chan_doan': 'Gãy xương cổ tay do ngã gãy kín đầu dưới xương quay kiểu Colles bên phải.',
    'chinh': [   'đau dữ dội vùng cổ tay sau khi ngã chống bàn tay xuống đất',
                 'cổ tay sưng to bầm tím nhanh chóng và biến dạng hình mu thìa dĩa',
                 'mất hoàn toàn khả năng cử động gập duỗi và xoay cổ tay'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Cố định tạm thời bằng nẹp cẳng bàn tay, chụp X-quang cổ tay thẳng nghiêng khẩn cấp, giảm đau và '
                'chuyển chuyên khoa Chấn thương Chỉnh hình nắn bó bột.',
    'kham': 'Cổ tay phải biến dạng điển hình hình lưng dĩa (Colles), sưng nề bầm tím vùng đầu dưới xương quay, ấn có '
            'điểm đau chói và lạo xạo xương, mạch quay bắt rõ.',
    'nhom': 'cả hai',
    'phu': [   'tê bì châm chích các ngón tay cái trỏ giữa do chèn ép thần kinh giữa',
               'nghe thấy tiếng rắc gãy xương lúc va chạm ngã',
               'tay lành phải nâng đỡ tay đau không dám buông thõng'],
    'ten': 'gãy xương cổ tay do ngã'},
    {   'bien_the_chan_doan': [   'Chấn thương sọ não nhẹ thể chấn động não theo dõi tụ máu nội sọ.',
                              'Chấn thương sọ não nhẹ chấn động não có thời gian mất tri giác ngắn.',
                              'Theo dõi chấn thương sọ não nhẹ có khối máu tụ dưới da đầu vùng trán.',
                              'Chấn thương sọ não nhẹ nguy cơ thấp theo tiêu chuẩn Canadian CT Head Rule.',
                              'Hội chứng sau chấn động não của chấn thương sọ não nhẹ.',
                              'Nghi ngờ chấn thương sọ não nhẹ có nứt rạn xương vòm sọ kín.'],
    'bien_the_ke_hoach': [   'Theo dõi sát tri giác và dấu hiệu sinh tồn mỗi 2-4 giờ trong 24 giờ đầu, chụp cắt lớp vi '
                             'tính CT sọ não không tiêm cản quang để loại trừ xuất huyết não.',
                             'Chỉ định chụp CT scan sọ não lát mỏng cửa sổ xương và nhu mô kiểm tra chảy máu ngoài '
                             'màng cứng hoặc dập não xuất huyết.',
                             'Phát phiếu theo dõi chấn thương sọ não tại nhà cho người thân, dặn dò đánh thức kiểm tra '
                             'bệnh nhân mỗi 2 giờ ban đêm.',
                             'Kê thuốc giảm đau paracetamol đơn thuần, tuyệt đối tránh dùng thuốc an thần hay kháng '
                             'viêm NSAID làm tăng nguy cơ chảy máu não.',
                             'Hướng dẫn đưa bệnh nhân vào viện cấp cứu ngay nếu có các dấu hiệu báo động: nôn vọt liên '
                             'tục, đau đầu dữ dội tăng dần, lú lẫn ngủ gọi không dậy hoặc co giật.',
                             'Cho bệnh nhân nằm nghỉ ngơi tại phòng yên tĩnh tránh ánh sáng mạnh, hẹn khám lại kiểm '
                             'tra sau 48 giờ nếu tiến triển ổn định.'],
    'bien_the_kham': [   'Glasgow 15 điểm tỉnh táo hoàn toàn, đồng tử hai bên 2.5mm đều phản xạ ánh sáng tốt, không có '
                         'dấu thần kinh khu trú, da đầu vùng đính có khối máu tụ bầm tím 3x3cm.',
                         'Khám thần kinh: định hướng bản thân không gian chuẩn xác, đồng tử tròn đều nhạy ánh sáng, '
                         'dấu hiệu màng não cổ cứng âm tính, cơ lực tứ chi 5/5.',
                         'Vùng trán phải có vết xây xát da và sưng nề tụ máu mô mềm, không sờ thấy lún xương sọ, không '
                         'chảy máu hay chảy dịch não tủy qua tai mũi.',
                         'Bệnh nhân than đau đầu âm ỉ vùng chẩm và buồn nôn nhẹ, khám 12 đôi dây thần kinh sọ bình '
                         'thường, phản xạ gân xương hai bên đối xứng.',
                         'Dấu hiệu sinh tồn ổn định: huyết áp 120/75 mmHg mạch 78 l/p nhịp thở 18 l/p, glasgow duy trì '
                         '15 điểm, không có dấu hiệu liệt nửa người.',
                         'Khám chuyên khoa ngoại thần kinh: không có dấu hiệu bầm quanh mắt dấu hiệu mắt kính râm hay '
                         'bầm sau tai Battle sign, tri giác hoàn toàn tỉnh táo.'],
    'chan_doan': 'Chấn thương sọ não nhẹ thể chấn động não theo dõi tụ máu nội sọ.',
    'chinh': [   'va đập đầu mạnh do tai nạn giao thông té ngã hoặc va chạm vật cứng',
                 'mất ý thức thoáng qua vài giây đến vài phút sau chấn thương',
                 'đau đầu chóng mặt buồn nôn nôn mửa sau khi va chạm'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Theo dõi sát tri giác và dấu hiệu sinh tồn mỗi 2-4 giờ trong 24 giờ đầu, chụp cắt lớp vi tính CT sọ '
                'não không tiêm cản quang để loại trừ xuất huyết não.',
    'kham': 'Glasgow 15 điểm tỉnh táo hoàn toàn, đồng tử hai bên 2.5mm đều phản xạ ánh sáng tốt, không có dấu thần '
            'kinh khu trú, da đầu vùng đính có khối máu tụ bầm tím 3x3cm.',
    'nhom': 'cả hai',
    'phu': [   'quên thuận chiều hoặc quên ngược chiều không nhớ sự việc xảy ra lúc tai nạn',
               'xây xẩm mặt mày nhạy cảm với ánh sáng chói và tiếng động mạnh',
               'vùng đầu có vết sưng nề bầm tím u cục dưới da đầu'],
    'ten': 'chấn thương sọ não nhẹ'},
    {   'bien_the_chan_doan': [   'Bỏng nhiệt độ II diện tích nhỏ khoảng 2% cơ thể ở cẳng tay phải do nước sôi.',
                              'Bỏng nhiệt độ II diện tích nhỏ thể nông chưa có bội nhiễm vi khuẩn.',
                              'Bỏng nhiệt độ II diện tích nhỏ do bỏng dầu mỡ rán nóng mu bàn tay.',
                              'Theo dõi bỏng nhiệt độ II diện tích nhỏ có bọng nước vỡ rách da.',
                              'Bỏng nhiệt độ II diện tích nhỏ ở cẳng chân giai đoạn cấp giờ thứ 2.',
                              'Bỏng nhiệt độ II diện tích nhỏ cần chăm sóc thay băng vô khuẩn ngoại trú.'],
    'bien_the_ke_hoach': [   'Rửa sạch tổn thương bằng nước muối sinh lý vô khuẩn, giữ nguyên vòm bọng nước tránh chọc '
                             'vỡ, băng đắp gạc mỡ kháng sinh urgo tul và tiêm phòng uốn ván SAT.',
                             'Ngâm xối rửa vùng bỏng dưới vòi nước sạch mát trong 15-20 phút, sát khuẩn nhẹ bằng dung '
                             'dịch povidone iodine pha loãng hoặc chlorhexidine.',
                             'Băng vô trùng bằng gạc chống dính vaseline hoặc gạc mỡ bạc silver sulfadiazine 1%, thay '
                             'băng mỗi 2 ngày một lần nhẹ nhàng.',
                             'Kê đơn thuốc giảm đau paracetamol kết hợp kháng viêm nhẹ, tiêm huyết thanh kháng độc tố '
                             'uốn ván SAT 1500 UI nếu chưa tiêm phòng đầy đủ.',
                             'Hướng dẫn bệnh nhân tuyệt đối không bôi kem đánh răng nước mắm hay các loại lá cây dân '
                             'gian lên vết bỏng gây nhiễm trùng nặng.',
                             'Theo dõi dịch tiết tại vết bỏng, nếu bọng nước quá căng gây tức có thể dùng kim vô trùng '
                             'chọc hút dịch giữ lại màng bảo vệ, hẹn khám lại sau 3 ngày.'],
    'bien_the_kham': [   'Vùng cẳng tay phải có nốt bọng nước căng kích thước 4x6cm chứa dịch màu vàng chanh trong '
                         'suốt, nền da xung quanh đỏ rực phù nề, cảm giác đau rát nhạy cảm tăng khi chạm nhẹ.',
                         'Khám vết bỏng: lớp thượng bì bong tách tạo bọng nước đáy ẩm ướt màu hồng hào rỉ dịch huyết '
                         'thanh, thử cảm giác châm kim rất đau (bỏng nông độ II).',
                         'Tổn thương bỏng nhiệt độ II nông diện tích ước tính 1.5% diện tích da ở mu bàn tay, các ngón '
                         'tay vận động co duỗi bình thường, mạch quay nẩy tốt.',
                         'Vết bỏng có vài bọng nước nhỏ đã vỡ để lộ đáy đỏ tươi rớm dịch trong, viền da xung quanh '
                         'sung huyết không có dấu hiệu hoại tử đen sạm.',
                         'Đánh giá tổn thương: bỏng nhiệt độ II nông sạch không dính dị vật than tro, diện tích dưới '
                         '3% diện tích cơ thể, không có bỏng ở vùng mặt hay sinh dục.',
                         'Khám thực thể: da mu bàn chân sưng nề có bọng nước đường kính 5cm chưa vỡ, bờ tổn thương '
                         'ranh giới rõ ràng với da lành, ấn đau chói.'],
    'chan_doan': 'Bỏng nhiệt độ II diện tích nhỏ khoảng 2% cơ thể ở cẳng tay phải do nước sôi.',
    'chinh': [   'da đỏ rực phồng rộp hình thành các nốt bọng nước chứa dịch trong',
                 'đau rát dữ dội tại vị trí tiếp xúc với nước sôi dầu mỡ nóng hoặc lửa',
                 'vết bỏng xuất hiện ngay sau tai nạn sinh hoạt nhiệt độ cao'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'chấn thương',
    'ke_hoach': 'Rửa sạch tổn thương bằng nước muối sinh lý vô khuẩn, giữ nguyên vòm bọng nước tránh chọc vỡ, băng đắp '
                'gạc mỡ kháng sinh urgo tul và tiêm phòng uốn ván SAT.',
    'kham': 'Vùng cẳng tay phải có nốt bọng nước căng kích thước 4x6cm chứa dịch màu vàng chanh trong suốt, nền da '
            'xung quanh đỏ rực phù nề, cảm giác đau rát nhạy cảm tăng khi chạm nhẹ.',
    'nhom': 'cả hai',
    'phu': [   'vòm bọng nước căng mỏng dễ vỡ khi va chạm cọ xát',
               'vùng da xung quanh vết bỏng phù nề sung huyết đỏ nhẹ',
               'diện tích tổn thương nhỏ dưới 5% diện tích cơ thể'],
    'ten': 'bỏng nhiệt độ II diện tích nhỏ'},
    {   'bien_the_chan_doan': [   'Viêm ruột thừa cấp giờ thứ 14 chưa có biến chứng vỡ mủ.',
                              'Viêm ruột thừa cấp thể viêm mủ có nguy cơ hoại tử thủng.',
                              'Theo dõi viêm ruột thừa cấp vị trí tiểu khung gây kích thích trực tràng.',
                              'Viêm ruột thừa cấp thể sau manh tràng ấn bụng trước ít đau.',
                              'Viêm ruột thừa cấp giai đoạn sung huyết sớm.',
                              'Nghi ngờ viêm ruột thừa cấp cần can thiệp mổ cấp cứu khẩn.'],
    'bien_the_ke_hoach': [   'Chỉ định phẫu thuật nội soi cắt ruột thừa cấp cứu, làm xét nghiệm tiền phẫu đông máu '
                             'nhóm máu, siêu âm ổ bụng và tiêm kháng sinh dự phòng ceftriaxone kết hợp metronidazole.',
                             'Chuyển phòng mổ ngoại tổng quát cắt ruột thừa nội soi khẩn cấp, nhịn ăn uống hoàn toàn, '
                             'đặt đường truyền tĩnh mạch Ringer lactat bù nước.',
                             'Siêu âm cấp cứu ổ bụng đo đường kính ruột thừa trên 6mm thành dày mất cấu trúc lớp, có '
                             'dịch viêm đọng quanh gốc ruột thừa.',
                             'Làm bilan xét nghiệm khẩn: công thức máu thấy bạch cầu đa nhân trung tính tăng cao trên '
                             '13.000, CRP tăng vọt, xét nghiệm đông máu cơ bản.',
                             'Giải thích tình trạng phẫu thuật cho người bệnh và gia đình ký giấy cam kết mổ, đặt ống '
                             'thông dạ dày nếu bụng chướng nôn nhiều.',
                             'Tiêm tĩnh mạch kháng sinh phổ rộng dự phòng nhiễm khuẩn ổ bụng, giảm đau sau khi bác sĩ '
                             'ngoại khoa đã khám xác chẩn chỉ định phẫu thuật.'],
    'bien_the_kham': [   'Bụng mềm, ấn đau chói và có phản ứng thành bụng cục bộ tại điểm McBurney hố chậu phải, dấu '
                         'hiệu Rovsing và dấu hiệu gót chân Blumberg dương tính.',
                         'Khám hố chậu phải thấy cơ thành bụng co cứng gồng kháng lại tay bác sĩ, ấn vào điểm đau ruột '
                         'thừa bệnh nhân đau thốn bật nảy người.',
                         'Nghiệm pháp Rovsing dương tính: dồn hơi từ hố chậu trái sang hố chậu phải gây đau nhói chói '
                         'vùng ruột thừa viêm.',
                         'Dấu hiệu cơ thắt lưng chậu (Psoas sign) dương tính: cho bệnh nhân nằm nghiêng trái duỗi khớp '
                         'háng phải ra sau thấy đau nhói sâu trong hố chậu phải.',
                         'Khám bụng: điểm Lans và điểm Clado ấn đau nhói, phản ứng dội Blumberg dương tính một phần ba '
                         'dưới bụng phải, không có co cứng bụng như gỗ.',
                         'Bệnh nhân sốt 38.3 độ môi khô se lưỡi phủ rêu trắng bẩn, ấn vùng hố chậu phải có cảm ứng '
                         'phúc mạc cục bộ, nhu động ruột giảm.'],
    'chan_doan': 'Viêm ruột thừa cấp giờ thứ 14 chưa có biến chứng vỡ mủ.',
    'chinh': [   'đau bụng khởi phát ở thượng vị quanh rốn sau chuyển khu trú về hố chậu phải',
                 'cơn đau bụng âm ỉ liên tục tăng dần mức độ đau nhói khi ho cử động',
                 'buồn nôn nôn mửa chán ăn kèm sốt nhẹ 38 độ C'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Chỉ định phẫu thuật nội soi cắt ruột thừa cấp cứu, làm xét nghiệm tiền phẫu đông máu nhóm máu, siêu '
                'âm ổ bụng và tiêm kháng sinh dự phòng ceftriaxone kết hợp metronidazole.',
    'kham': 'Bụng mềm, ấn đau chói và có phản ứng thành bụng cục bộ tại điểm McBurney hố chậu phải, dấu hiệu Rovsing '
            'và dấu hiệu gót chân Blumberg dương tính.',
    'nhom': 'người lớn',
    'phu': [   'bụng có cảm giác đầy chướng khó chịu bí trung đại tiện',
               'mệt mỏi môi khô lưỡi bẩn dấu hiệu nhiễm trùng',
               'bệnh nhân thường đi lom khom tay ôm bụng bên phải để đỡ đau'],
    'ten': 'viêm ruột thừa cấp'},
    {   'bien_the_chan_doan': [   'Thoát vị bẹn gián tiếp bên phải chưa có biến chứng nghẹt.',
                              'Thoát vị bẹn trực tiếp hai bên thể dễ đẩy lên.',
                              'Theo dõi thoát vị bẹn bên trái có nguy cơ nghẹt kẹt tạng.',
                              'Thoát vị bẹn tái phát sau phẫu thuật khâu phục hồi thành bụng.',
                              'Thoát vị bẹn thể bẹn bìu kích thước lớn.',
                              'Thoát vị bẹn nguyên phát ở người lao động nặng.'],
    'bien_the_ke_hoach': [   'Tư vấn phẫu thuật đặt lưới nhân tạo tái tạo thành bụng mổ mở hoặc nội soi TAPP/TEP, '
                             'tránh mang vác nặng và điều trị dứt điểm chứng ho táo bón.',
                             'Chỉ định mổ chương trình đặt tấm lưới polypropylene củng cố thành bẹn theo phương pháp '
                             'Lichtenstein, làm xét nghiệm tiền phẫu thường quy.',
                             'Siêu âm vùng bẹn bìu đánh giá kích thước lỗ bẹn và thành phần tạng thoát vị (quai ruột '
                             'hay mạc nối lớn), hẹn lịch phẫu thuật ngoại khoa.',
                             'Hướng dẫn bệnh nhân nhận biết các dấu hiệu thoát vị bẹn nghẹt: đau dữ dội đột ngột, khối '
                             'phồng cứng ngắc không đẩy lên được, nôn ói bí trung tiện để vào viện cấp cứu ngay.',
                             'Tránh tuyệt đối các hoạt động gắng sức nặng nâng tạ mang vác, đeo đai hỗ trợ thoát vị '
                             'tạm thời nếu chưa thể sắp xếp phẫu thuật ngay.',
                             'Khám chuyên khoa Ngoại Tiêu hóa tư vấn ưu nhược điểm của phẫu thuật nội soi đặt lưới '
                             'ngoài phúc mạc TEP giúp phục hồi nhanh ít đau.'],
    'bien_the_kham': [   'Vùng bẹn phải có khối phồng kích thước 3x4cm mật độ mềm không đau, sờ thấy lỗ bẹn nông rộng, '
                         'nghiệm pháp chạm ngón tay (finger test) chạm đỉnh khối thoát vị khi bệnh nhân rặn ho.',
                         'Bệnh nhân đứng ho rặn xuất hiện khối tròn mềm xuất phát từ nếp lằn bẹn chạy dọc xuống gốc '
                         'bìu, ấn nhẹ tay khối dễ dàng tụt êm ái vào ổ bụng.',
                         'Khám lỗ bẹn nông bên phải rộng khoảng 2 ngón tay, nghiệm pháp chạm ngón phát hiện khối thoát '
                         'vị đập vào đầu ngón khi tăng áp lực ổ bụng.',
                         'Nghiệm pháp chẹn lỗ bẹn sâu dương tính: đè ngón cái tại điểm giữa nếp bẹn rồi yêu cầu bệnh '
                         'nhân rặn thì khối thoát vị không trồi ra (thoát vị gián tiếp).',
                         'Khám vùng bìu bẹn: khối mềm không nóng đỏ, soi đèn không thấu sáng (loại trừ tràn dịch màng '
                         'tinh hoàn), sờ nắn mào tinh và tinh hoàn tách biệt rõ.',
                         'Khối phồng vùng bẹn trái kích thước 2.5x3cm xuất hiện khi ho, tiếng gõ vang nhẹ (quai ruột '
                         'bên trong), không có điểm ấn đau chói cục bộ.'],
    'chan_doan': 'Thoát vị bẹn gián tiếp bên phải chưa có biến chứng nghẹt.',
    'chinh': [   'xuất hiện khối phồng vùng bẹn hoặc bìu to lên khi đứng lâu đi lại ho rặn',
                 'cảm giác tức nặng vướng víu khó chịu ở vùng bẹn bìu',
                 'khối phồng tự thụt vào trong ổ bụng khi nằm nghỉ hoặc dùng tay đẩy nhẹ lên'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Tư vấn phẫu thuật đặt lưới nhân tạo tái tạo thành bụng mổ mở hoặc nội soi TAPP/TEP, tránh mang vác '
                'nặng và điều trị dứt điểm chứng ho táo bón.',
    'kham': 'Vùng bẹn phải có khối phồng kích thước 3x4cm mật độ mềm không đau, sờ thấy lỗ bẹn nông rộng, nghiệm pháp '
            'chạm ngón tay (finger test) chạm đỉnh khối thoát vị khi bệnh nhân rặn ho.',
    'nhom': 'người lớn',
    'phu': [   'tiền sử ho mạn tính táo bón kéo dài hoặc làm việc nặng mang vác vất vả',
               'khối phồng có thể tăng kích thước dần theo thời gian nhiều năm',
               'lo lắng sợ nguy cơ khối thoát vị bị kẹt nghẹt gây hoại tử ruột'],
    'ten': 'thoát vị bẹn'},
    {   'bien_the_chan_doan': [   'Sỏi ống mật chủ có viêm đường mật cấp tính.',
                              'Sỏi ống mật chủ gây tắc mật hoàn toàn chưa có sốc nhiễm trùng đường mật.',
                              'Theo dõi sỏi ống mật chủ kèm sỏi túi mật có biến chứng viêm tụy cấp nhẹ.',
                              'Sỏi ống mật chủ tái phát sau mổ hở lấy sỏi dẫn lưu Kehr cũ.',
                              'Nghi ngờ sỏi ống mật chủ có nhiễm trùng đường mật nặng ngũ chứng Reynolds.',
                              'Sỏi ống mật chủ đoạn thấp bóng Vater gây giãn đường mật trong và ngoài gan.'],
    'bien_the_ke_hoach': [   'Chỉ định nhập viện khẩn cấp, kháng sinh phổ rộng ceftriaxone kết hợp metronidazole đường '
                             'tĩnh mạch, siêu âm ổ bụng và chụp cộng hưởng từ mật tụy MRCP, chuẩn bị nội soi mật tụy '
                             'ngược dòng ERCP lấy sỏi.',
                             'Hội chẩn Nội soi can thiệp tiêu hóa thực hiện ERCP cắt cơ vòng Oddi gắp sỏi ống mật chủ '
                             'tán sỏi, đặt stent dẫn lưu đường mật nếu sỏi kẹt chặt.',
                             'Làm siêu âm Doppler gan mật đo đường kính ống mật chủ giãn trên 10mm có bóng cản âm kèm '
                             'bóng lưng, chụp MRCP dựng hình cây đường mật.',
                             'Xét nghiệm máu khẩn: bilirubin toàn phần và trực tiếp tăng vọt, men phosphatase kiềm và '
                             'GGT tăng cao, amylase máu loại trừ viêm tụy cấp.',
                             'Truyền dịch tích cực bù nước điện giải, tiêm thuốc giãn cơ trơn chống co thắt papaverine '
                             'hoặc buscopan kết hợp kháng sinh tĩnh mạch liều cao.',
                             'Chuẩn bị phương án phẫu thuật mổ mở hoặc nội soi mở ống mật chủ lấy sỏi đặt dẫn lưu Kehr '
                             'nếu can thiệp nội soi ERCP thất bại.'],
    'bien_the_kham': [   'Tam chứng Charcot kinh điển (đau hạ sườn phải - sốt rét run - vàng da), củng mạc mắt vàng '
                         'đậm, hạ sườn phải ấn đau tức rõ rệt, sờ thấy túi mật to căng tròn.',
                         'Khám bụng: điểm Murphy dương tính ấn đau hạ sườn phải cơ gồng nhẹ đề kháng, sờ thấy đáy túi '
                         'mật căng to nhô dưới bờ sườn mật độ mềm nhẵn.',
                         'Dấu hiệu vàng da tắc mật rõ: da toàn thân và niêm mạc dưới lưỡi vàng chanh sẫm, nhiệt độ 39 '
                         'độ C sốt vã mồ hôi, mạch 100 l/p huyết áp ổn định.',
                         'Bệnh nhân lăn lộn vì cơn đau quặn gan dữ dội, củng mạc mắt vàng cam, ấn kẽ liên sườn vùng '
                         'gan không đau chói (loại trừ áp xe gan), túi mật to căng tức.',
                         'Khám thực thể: hội chứng ứ mật ngoài gan kết hợp hội chứng nhiễm trùng đường mật cấp, gan to '
                         '1.5cm dưới bờ sườn ấn đau tức nhẹ.',
                         'Bụng mềm vùng hạ vị nhưng gồng cứng phản ứng nhẹ ở hạ sườn phải, nước tiểu lấy ra có màu '
                         'vàng sẫm như nước chè đặc, phân nhạt màu.'],
    'chan_doan': 'Sỏi ống mật chủ có viêm đường mật cấp tính.',
    'chinh': [   'đau quặn dữ dội từng cơn vùng hạ sườn phải lan ra sau lưng hoặc lên vai phải',
                 'sốt cao rét run vã mồ hôi xuất hiện sau cơn đau bụng vài giờ',
                 'vàng da và vàng củng mạc mắt tăng dần nước tiểu sẫm màu phân bạc màu'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Chỉ định nhập viện khẩn cấp, kháng sinh phổ rộng ceftriaxone kết hợp metronidazole đường tĩnh mạch, '
                'siêu âm ổ bụng và chụp cộng hưởng từ mật tụy MRCP, chuẩn bị nội soi mật tụy ngược dòng ERCP lấy sỏi.',
    'kham': 'Tam chứng Charcot kinh điển (đau hạ sườn phải - sốt rét run - vàng da), củng mạc mắt vàng đậm, hạ sườn '
            'phải ấn đau tức rõ rệt, sờ thấy túi mật to căng tròn.',
    'nhom': 'người lớn',
    'phu': [   'buồn nôn nôn mửa nhiều dịch tiêu hóa và dịch mật chua đắng',
               'ngứa ngáy da khắp người do lắng đọng muối mật',
               'tiền sử có sỏi túi mật hoặc đã từng điều trị giun chui ống mật'],
    'ten': 'sỏi ống mật chủ'},
    {   'bien_the_chan_doan': [   'Bệnh Crohn thể hồi manh tràng đợt tiến triển mức độ trung bình.',
                              'Bệnh Crohn thể đại tràng có biến chứng rò quanh hậu môn.',
                              'Theo dõi bệnh Crohn có tổn thương hẹp lòng ruột non bán tắc.',
                              'Bệnh Crohn thể hoạt động phụ thuộc thuốc corticoid.',
                              'Nghi ngờ bệnh Crohn cần chẩn đoán phân biệt với lao ruột.',
                              'Bệnh Crohn giai đoạn lui bệnh đang duy trì thuốc sinh học kháng TNF.'],
    'bien_the_ke_hoach': [   'Nội soi đại hồi tràng sinh thiết tổn thương giải phẫu bệnh, xét nghiệm calprotectin '
                             'phân, chụp CT ruột enterography và điều trị kiểm soát bằng 5-ASA corticoid hoặc thuốc '
                             'sinh học.',
                             'Chỉ định nội soi toàn bộ đại tràng vào sâu hồi tràng lấy mẫu sinh thiết tìm hình ảnh u '
                             'hạt không bã đậu đặc trưng của Crohn.',
                             'Đo nồng độ calprotectin trong phân đánh giá mức độ viêm niêm mạc ruột, xét nghiệm CRP '
                             'tốc độ máu lắng và kháng thể ASCA.',
                             'Kê đơn methylprednisolone đường uống tấn công giảm liều dần, kết hợp azathioprine hoặc '
                             'thuốc sinh học infliximab duy trì ổn định.',
                             'Tư vấn chế độ ăn ít xơ không sinh hơi chia nhỏ bữa ăn khi đang có đợt cấp, bổ sung vi '
                             'chất sắt acid folic kẽm và vitamin B12.',
                             'Hội chẩn Ngoại Tiêu hóa xử trí dẫn lưu các ổ áp xe rò hậu môn bằng đặt dây seton dẫn lưu '
                             'mềm tránh biến chứng phức tạp.'],
    'bien_the_kham': [   'Bụng mềm sờ thấy khối dính ranh giới không rõ ấn đau tức tại hố chậu phải (quai ruột viêm '
                         'dầy), vùng quanh hậu môn có vết rò rỉ dịch nhầy.',
                         'Khám hố chậu phải: có cảm giác khối đầy chắc mềm di động kém do quai hồi tràng viêm dày '
                         'thành dính mạc treo, ấn tức khó chịu.',
                         'Khám hậu môn trực tràng: phát hiện đường rò cạnh hậu môn đang rỉ dịch mủ nhầy mạn tính, da '
                         'quanh rìa hậu môn có vết loét nứt kẽ sâu.',
                         'Thể trạng gầy gò niêm mạc mắt nhợt thiếu máu mạn, bụng chướng nhẹ dọc khung đại tràng, nhu '
                         'động ruột tăng có tiếng óc ách khi khám.',
                         'Khoang miệng có hai vết loét aphthous ở niêm mạc môi trong đau rát, cẳng chân hai bên có vài '
                         'nốt hồng ban nút đỏ sẫm ấn đau nhẹ.',
                         'Khám thực thể tiêu hóa: ấn đau khu trú hồi tràng vùng hố chậu phải, không có dấu hiệu viêm '
                         'phúc mạc toàn thể, khớp cổ chân sưng nhẹ không nóng.'],
    'chan_doan': 'Bệnh Crohn thể hồi manh tràng đợt tiến triển mức độ trung bình.',
    'chinh': [   'đau bụng quặn từng cơn mạn tính thường khu trú vùng hố chậu phải',
                 'tiêu chảy phân lỏng nhiều lần trong ngày có nhầy máu tái diễn',
                 'sụt cân nhanh chóng sốt nhẹ kéo dài suy nhược cơ thể'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Nội soi đại hồi tràng sinh thiết tổn thương giải phẫu bệnh, xét nghiệm calprotectin phân, chụp CT '
                'ruột enterography và điều trị kiểm soát bằng 5-ASA corticoid hoặc thuốc sinh học.',
    'kham': 'Bụng mềm sờ thấy khối dính ranh giới không rõ ấn đau tức tại hố chậu phải (quai ruột viêm dầy), vùng '
            'quanh hậu môn có vết rò rỉ dịch nhầy.',
    'nhom': 'người lớn',
    'phu': [   'loét áp-tơ niêm mạc miệng tái phát nhiều lần',
               'nứt kẽ hậu môn rò hậu môn hoặc áp xe quanh hậu môn phức tạp',
               'đau nhức các khớp ngoại biên hoặc nổi hồng ban nút ở cẳng chân'],
    'ten': 'bệnh Crohn'},
    {   'bien_the_chan_doan': [   'Polyp đại tràng sigma nghi polyp tuyến tuyến đại tràng.',
                              'Polyp đại tràng đa polyp tuyến có cuống vùng đại tràng xuống.',
                              'Theo dõi polyp đại tràng kích thước lớn trên 2cm có nguy cơ nghịch sản ác tính.',
                              'Polyp đại tràng góc gan đã can thiệp cắt nội soi an toàn.',
                              'Polyp đại tràng thể không cuống (polyp dẹt) cần kỹ thuật cắt niêm mạc EMR.',
                              'Hội chứng đa polyp đại tràng gia đình FAP cần tầm soát gen.'],
    'bien_the_ke_hoach': [   'Nội soi đại tràng toàn bộ làm sạch ruột can thiệp cắt polyp bằng thòng lọng điện snare, '
                             'gửi bệnh phẩm làm xét nghiệm mô bệnh học giải phẫu bệnh.',
                             'Chuẩn bị làm sạch ruột bằng dung dịch uống PEG, tiến hành nội soi đại trực tràng ống mềm '
                             'có tiền mê cắt trọn polyp bằng thắt kẹp clip.',
                             'Lấy toàn bộ mẫu polyp gửi khoa Giải phẫu bệnh nhuộm HE xác định phân loại polyp tuyến '
                             'ống hay nhung mao và mức độ loạn sản tế bào.',
                             'Dặn dò bệnh nhân theo dõi dấu hiệu chảy máu sau cắt polyp: đại tiện ra máu đỏ tươi nhiều '
                             'lần hoặc đau bụng tăng dần để xử trí kịp thời.',
                             'Chế độ ăn nhẹ cháo loãng nguội trong 24 giờ sau thủ thuật cắt polyp, tránh vận động mạnh '
                             'chạy nhảy mang vác trong 1 tuần đầu.',
                             'Lập kế hoạch nội soi đại tràng kiểm tra định kỳ sau 1-3 năm tùy thuộc vào số lượng kích '
                             'thước và kết quả mô bệnh học của polyp.'],
    'bien_the_kham': [   'Khám bụng mềm hoàn toàn không sờ thấy khối u bụng, thăm trực tràng bằng ngón tay không chạm '
                         'tổn thương (polyp vị trí cao trên trực tràng).',
                         'Thể trạng bình thường niêm mạc mắt hồng hào, bụng phẳng mềm không chướng, ấn dọc khung đại '
                         'tràng không có điểm đau khu trú.',
                         'Thăm khám trực tràng bằng ngón tay găng sạch không dính máu mủ, cơ thắt hậu môn tốt, không '
                         'sờ thấy búi trĩ sa hay khối u trực tràng thấp.',
                         'Khám tiêu hóa tổng quát: gan lách không to, không sờ thấy hạch ổ bụng, không có dấu hiệu tắc '
                         'ruột hay bán tắc ruột.',
                         'Bệnh nhân tỉnh táo khám lâm sàng không phát hiện dấu hiệu bất thường ngoài tiền sử gia đình '
                         'có người bị ung thư đại trực tràng.',
                         'Khám thực thể bình thường, xét nghiệm test tìm máu ẩn trong phân FOBT dương tính, chỉ định '
                         'nội soi đại tràng kiểm tra trực quan.'],
    'chan_doan': 'Polyp đại tràng sigma nghi polyp tuyến tuyến đại tràng.',
    'chinh': [   'đại tiện ra máu tươi hoặc máu lẫn nhầy dính trên bề mặt khuôn phân',
                 'thay đổi thói quen đại tiện lúc táo bón lúc đi phân lỏng kéo dài',
                 'phân có vết lõm dẹt hoặc vệt rãnh nhỏ do khối u chèn ép khuôn phân'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Nội soi đại tràng toàn bộ làm sạch ruột can thiệp cắt polyp bằng thòng lọng điện snare, gửi bệnh phẩm '
                'làm xét nghiệm mô bệnh học giải phẫu bệnh.',
    'kham': 'Khám bụng mềm hoàn toàn không sờ thấy khối u bụng, thăm trực tràng bằng ngón tay không chạm tổn thương '
            '(polyp vị trí cao trên trực tràng).',
    'nhom': 'người lớn',
    'phu': [   'đau quặn bụng âm ỉ mơ hồ không cố định dọc khung đại tràng',
               'thiếu máu thiếu sắt âm ỉ mệt mỏi chóng mặt không rõ nguyên nhân',
               'hoàn toàn không có triệu chứng tình cờ phát hiện khi nội soi tầm soát'],
    'ten': 'polyp đại tràng'},
    {   'bien_the_chan_doan': [   'Táo bón mạn tính ở người cao tuổi thể giảm nhu động ruột có ứ đọng phân trực tràng.',
                              'Táo bón mạn tính ở người cao tuổi do tác dụng phụ của thuốc điều trị bệnh phối hợp.',
                              'Theo dõi táo bón mạn tính ở người cao tuổi có biến chứng nứt kẽ hậu môn trĩ.',
                              'Táo bón mạn tính ở người cao tuổi thể suy giảm phản xạ tống phân sàn chậu.',
                              'Táo bón mạn tính ở người cao tuổi cần nội soi đại tràng loại trừ bệnh ác tính.',
                              'Hội chứng táo bón mạn tính ở người cao tuổi lạm dụng thuốc nhuận tràng kích thích.'],
    'bien_the_ke_hoach': [   'Thụt tháo giải phóng khối phân ứ đọng, bổ sung chất xơ hòa tan macrogol đường uống, tăng '
                             'cường uống nước và điều chỉnh vận động thể lực phù hợp.',
                             'Kê thuốc nhuận tràng thẩm thấu polyethylene glycol macrogol 4000 ngày 1-2 gói uống với '
                             'nhiều nước duy trì làm mềm phân sinh lý an toàn.',
                             'Thụt tháo hậu môn nhẹ nhàng bằng dung dịch glycerol hoặc microlax để làm mềm tống xuất '
                             'nút phân cứng kẹt tại bóng trực tràng.',
                             'Hướng dẫn chế độ ăn tăng cường chất xơ từ rau củ quả chín như mồng tơi khoai lang thanh '
                             'long chuối tiêu, uống đủ 1.5 - 2 lít nước mỗi ngày.',
                             'Rà soát cắt giảm hoặc thay thế các loại thuốc gây táo bón đang dùng như thuốc chẹn kênh '
                             'canxi, thuốc kháng cholinergic và viên uống bổ sung sắt.',
                             'Tập thói quen đi đại tiện vào một giờ cố định mỗi sáng sau bữa ăn, kết hợp kê ghế nhỏ '
                             'dưới chân khi ngồi bồn cầu để tạo góc tống phân tự nhiên.'],
    'bien_the_kham': [   'Bụng chướng nhẹ gõ vang, nắn dọc hố chậu trái sờ thấy quai đại tràng sigma ứ đọng nhiều thỏi '
                         'phân cứng, thăm trực tràng thấy khối phân khô chặt bóng trực tràng.',
                         'Khám hố chậu trái sờ thấy khối dài chắc hình ống ấn hơi tức (quai đại tràng chứa phân u '
                         'phân), không có phản ứng thành bụng.',
                         'Thăm khám trực tràng bằng ngón tay: bóng trực tràng giãn to chứa đầy khối phân cứng chắc '
                         '(fecal impaction), cơ thắt hậu môn nhão giảm trương lực.',
                         'Khám bụng: bụng mềm gõ hơi chướng dọc khung đại tràng, nhu động ruột nghe thưa thớt 1-2 '
                         'lần/phút, không có dấu hiệu rắn bò hay quai ruột nổi.',
                         'Thể trạng người già chậm chạp ít vận động, da khô nhăn nheo, khám không phát hiện dấu hiệu '
                         'ngoại khoa bán tắc ruột do u bướu.',
                         'Khám vùng tầng sinh môn: không có trĩ tắc mạch cấp tính, thăm trực tràng găng dính ít dịch '
                         'nhầy phân khô, lỗ hậu môn sạch.'],
    'chan_doan': 'Táo bón mạn tính ở người cao tuổi thể giảm nhu động ruột có ứ đọng phân trực tràng.',
    'chinh': [   'đại tiện dưới 3 lần một tuần kéo dài liên tục trên 6 tháng',
                 'phân khô cứng lổn nhổn từng cục như phân dê phải rặn nhiều gây đau rát',
                 'cảm giác đại tiện không hết phân tắc nghẽn ở trực tràng sau mỗi lần đi'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'lão khoa',
    'ke_hoach': 'Thụt tháo giải phóng khối phân ứ đọng, bổ sung chất xơ hòa tan macrogol đường uống, tăng cường uống '
                'nước và điều chỉnh vận động thể lực phù hợp.',
    'kham': 'Bụng chướng nhẹ gõ vang, nắn dọc hố chậu trái sờ thấy quai đại tràng sigma ứ đọng nhiều thỏi phân cứng, '
            'thăm trực tràng thấy khối phân khô chặt bóng trực tràng.',
    'nhom': 'người lớn',
    'phu': [   'phải dùng tay hỗ trợ đẩy phân hoặc phụ thuộc hoàn toàn vào thuốc thụt hậu môn',
               'chướng bụng đầy hơi chán ăn mệt mỏi ậm ạch khó chịu',
               'tiền sử ít vận động uống ít nước và sử dụng nhiều loại thuốc mạn tính'],
    'ten': 'táo bón mạn tính ở người cao tuổi'},
    {   'bien_the_chan_doan': [   'Hội chứng chuyển hoá theo tiêu chuẩn IDF có rối loạn lipid máu và tiền tăng huyết áp.',
                              'Hội chứng chuyển hoá có kèm gan nhiễm mỡ không do rượu NAFLD.',
                              'Theo dõi hội chứng chuyển hoá trên bệnh nhân tiền đái tháo đường rối loạn dung nạp '
                              'glucose.',
                              'Hội chứng chuyển hoá mức độ trung bình có nguy cơ tim mạch 10 năm cao.',
                              'Hội chứng chuyển hoá thể tăng triglycerid máu nặng và giảm HDL.',
                              'Hội chứng chuyển hoá kết hợp tăng acid uric máu không triệu chứng.'],
    'bien_the_ke_hoach': [   'Thiết lập chế độ ăn giảm calo hạn chế đường ngọt tinh bột xấu, tăng cường tập thể dục '
                             'cường độ vừa ít nhất 150 phút/tuần và theo dõi định kỳ mỡ máu đường huyết.',
                             'Áp dụng chế độ ăn Địa Trung Hải giàu dầu ô liu cá béo quả hạch rau xanh, cắt giảm hoàn '
                             'toàn nước ngọt bánh kẹo đồ uống có cồn.',
                             'Lập kế hoạch giảm 7-10% trọng lượng cơ thể trong vòng 6 tháng bằng cách đi bộ nhanh đạp '
                             'xe 30-45 phút mỗi ngày 5 ngày/tuần.',
                             'Xét nghiệm lipid máu toàn phần, đường huyết đói, HbA1c, men gan và acid uric định kỳ mỗi '
                             '3 tháng để đánh giá chuyển hóa.',
                             'Xem xét khởi trị statin liều thấp atorvastatin nếu nguy cơ tim mạch cao hoặc metformin '
                             'nếu đường huyết đói không kiểm soát được bằng lối sống.',
                             'Đo huyết áp hàng ngày tại nhà ghi nhật ký huyết áp, tư vấn bỏ hút thuốc lá và cải thiện '
                             'chất lượng giấc ngủ phòng ngừa ngưng thở khi ngủ.'],
    'bien_the_kham': [   'Đo vòng eo đạt 94cm ở nam (vượt ngưỡng 90cm), huyết áp đo hai tay trung bình 135/88 mmHg, '
                         'chỉ số khối cơ thể BMI 27.5 kg/m2, thể trạng béo trục thân bụng to.',
                         'Vòng bụng phụ nữ đo ngang rốn 86cm (vượt chuẩn 80cm), huyết áp 140/90 mmHg, vùng cổ sau gáy '
                         'có dấu hiệu tăng sắc tố gai đen nhẹ acanthosis nigricans.',
                         'Khám thực thể: mỡ tích tụ nhiều ở vùng trung tâm bụng ngực, tỷ số vòng eo/vòng mông vượt '
                         'ngưỡng 0.9 ở nam, tim đều rõ không có tiếng thổi.',
                         'Khám toàn diện: mạch 76 l/p huyết áp 138/85 mmHg, gan to nhẹ dưới bờ sườn 1cm mềm nhẵn do '
                         'thoái hóa mỡ, đáy mắt chưa có tổn thương xơ vữa.',
                         'Chỉ số khối BMI 28.2 kg/m2, vòng bụng 96cm, nghe tim T1 T2 rõ đều, hai chi dưới không có '
                         'phù, các mạch máu ngoại biên bắt đập tốt.',
                         'Bệnh nhân thể trạng béo phì trung tâm, vòng eo 92cm, đo huyết áp dao động 135-140 mmHg, dấu '
                         'hiệu lâm sàng gợi ý kháng insulin rõ.'],
    'chan_doan': 'Hội chứng chuyển hoá theo tiêu chuẩn IDF có rối loạn lipid máu và tiền tăng huyết áp.',
    'chinh': [   'béo bụng tích tụ mỡ nội tạng vòng bụng tăng kích thước rõ rệt',
                 'huyết áp đo thường xuyên ở mức cao trên 130/85 mmHg',
                 'xét nghiệm mỡ máu có tăng triglycerid và giảm cholesterol tốt HDL-C'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nội tiết - chuyển hoá',
    'ke_hoach': 'Thiết lập chế độ ăn giảm calo hạn chế đường ngọt tinh bột xấu, tăng cường tập thể dục cường độ vừa ít '
                'nhất 150 phút/tuần và theo dõi định kỳ mỡ máu đường huyết.',
    'kham': 'Đo vòng eo đạt 94cm ở nam (vượt ngưỡng 90cm), huyết áp đo hai tay trung bình 135/88 mmHg, chỉ số khối cơ '
            'thể BMI 27.5 kg/m2, thể trạng béo trục thân bụng to.',
    'nhom': 'người lớn',
    'phu': [   'đường huyết lúc đói tăng nhẹ ở ngưỡng tiền đái tháo đường',
               'cơ thể nặng nề dễ mệt mỏi hay buồn ngủ sau bữa ăn nhiều tinh bột',
               'lối sống tĩnh tại ít vận động công việc văn phòng bàn giấy'],
    'ten': 'hội chứng chuyển hoá'},
    {   'bien_the_chan_doan': [   'Suy dinh dưỡng ở người cao tuổi mức độ nặng theo tiêu chuẩn GLIM.',
                              'Suy dinh dưỡng ở người cao tuổi thể teo cơ thiểu cơ sarcopenia suy yếu frailty.',
                              'Theo dõi suy dinh dưỡng ở người cao tuổi do giảm khẩu phần ăn và cô đơn trầm cảm.',
                              'Suy dinh dưỡng ở người cao tuổi kèm theo thiếu máu thiếu đạm dinh dưỡng.',
                              'Suy dinh dưỡng ở người cao tuổi thứ phát sau bệnh lý mạn tính tiêu hao.',
                              'Hội chứng suy kiệt suy dinh dưỡng ở người cao tuổi cần can thiệp nuôi dưỡng tích cực.'],
    'bien_the_ke_hoach': [   'Bổ sung dinh dưỡng đường uống giàu năng lượng và đạm ONS, điều trị các bệnh mạn tính đi '
                             'kèm, khám nha khoa phục hình răng và tập vận động cơ nhẹ nhàng.',
                             'Kê sữa dinh dưỡng y học chuyên biệt cho người cao tuổi giàu đạm whey và leucine uống bổ '
                             'sung 2 ly mỗi ngày giữa các bữa phụ.',
                             'Chỉ định chế độ ăn mềm lỏng giàu dinh dưỡng chia nhỏ 5-6 bữa/ngày, chế biến thức ăn đậm '
                             'vị thơm ngon kích thích khứu vị giác.',
                             'Xét nghiệm albumin máu, prealbumin, protein toàn phần, điện giải đồ và công thức máu '
                             'đánh giá mức độ suy kiệt dinh dưỡng.',
                             'Khám chuyên khoa Răng Hàm Mặt làm răng giả tháo lắp phục hồi chức năng nhai nuốt, điều '
                             'trị triệt để các vấn đề khô miệng và trào ngược.',
                             'Lập bài tập vật lý trị liệu tăng cường sức mạnh cơ bắp tại giường hoặc ngồi ghế có trợ '
                             'giúp, bổ sung vitamin D3 và kẽm hàng ngày.'],
    'bien_the_kham': [   'Chỉ chỉ số khối cơ thể BMI 17 kg/m2, lớp mỡ dưới da mu bàn tay và cánh tay teo mỏng, teo '
                         'khối cơ thái dương và cơ liên đốt bàn tay, thang điểm MNA dưới 17 điểm.',
                         'Đánh giá nhân trắc: vòng bắp chân 28cm (dưới ngưỡng 31cm báo hiệu teo cơ sarcopenia), niêm '
                         'mạc mắt nhợt nhạt, da khô nứt nẻ như vảy cá.',
                         'Khám khoang miệng thấy mất 10 răng hàm chưa làm răng giả, niêm mạc lưỡi teo gai nhẵn bóng, '
                         'lực bóp bàn tay đo lực kế giảm dưới 16kg ở nữ.',
                         'Thể trạng gầy trơ xương, hai hõm thái dương lõm sâu, xương sườn nhô rõ, lớp mỡ dưới da bụng '
                         'dày dưới 0.5cm, không có phù ngoại biên.',
                         'Khám dinh dưỡng tổng thể MNA-SF đạt 6/14 điểm suy dinh dưỡng rõ, bệnh nhân di chuyển chậm '
                         'chạp phải có người dìu đỡ, cơ bắp nhẽo teo.',
                         'Bệnh nhân già yếu sụt 4kg trong 2 tháng, mạch 68 l/p chậm yếu, huyết áp 100/60 mmHg, xét '
                         'nghiệm albumin máu giảm dưới 30 g/l.'],
    'chan_doan': 'Suy dinh dưỡng ở người cao tuổi mức độ nặng theo tiêu chuẩn GLIM.',
    'chinh': [   'sụt cân không chủ ý trên 5% trọng lượng cơ thể trong 3 tháng qua',
                 'ăn uống kém ngon miệng lượng thức ăn nạp vào mỗi bữa giảm rõ rệt',
                 'teo cơ bắp chân tay khẳng khiu suy giảm thể lực cầm nắm đi lại yếu'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'dinh dưỡng',
    'ke_hoach': 'Bổ sung dinh dưỡng đường uống giàu năng lượng và đạm ONS, điều trị các bệnh mạn tính đi kèm, khám nha '
                'khoa phục hình răng và tập vận động cơ nhẹ nhàng.',
    'kham': 'Chỉ số khối cơ thể BMI 17 kg/m2, lớp mỡ dưới da mu bàn tay và cánh tay teo mỏng, teo khối cơ thái dương '
            'và cơ liên đốt bàn tay, thang điểm MNA dưới 17 điểm.',
    'nhom': 'người lớn',
    'phu': [   'mất răng tụt lợi rụng răng nhiều khiến việc nhai nghiền thức ăn khó khăn',
               'da khô nhăn nheo vết thương bầm tím lâu lành',
               'thường xuyên mệt mỏi nằm một chỗ thờ ơ hay bị ngã khi đi lại'],
    'ten': 'suy dinh dưỡng ở người cao tuổi'},
    {   'bien_the_chan_doan': [   'Thiếu vitamin B12 có biểu hiện thiếu máu hồng cầu to và thoái hóa kết hợp tủy sống.',
                              'Thiếu vitamin B12 do bệnh thiếu máu ác tính Biermer tự miễn kháng yếu tố nội tại.',
                              'Theo dõi thiếu vitamin B12 ở người ăn chay trường thuần thực vật kéo dài.',
                              'Thiếu vitamin B12 thứ phát sau phẫu thuật cắt dạ dày bán phần.',
                              'Thiếu máu hồng cầu khổng lồ do thiếu vitamin B12 có triệu chứng tâm thần kinh.',
                              'Thiếu vitamin B12 do dùng thuốc metformin hoặc thuốc kháng acid dạ dày PPI kéo dài.'],
    'bien_the_ke_hoach': [   'Xét nghiệm định lượng vitamin B12 huyết thanh, acid folic, huyết đồ xem kích thước hồng '
                             'cầu MCV, tiêm bắp vitamin B12 liều cao hydroxocobalamin theo phác đồ tấn công.',
                             'Chỉ định tiêm bắp vitamin B12 (cyanocobalamin hoặc hydroxocobalamin) 1000 mcg mỗi ngày '
                             'trong 1 tuần đầu, sau đó 1000 mcg mỗi tuần trong 1 tháng.',
                             'Làm xét nghiệm công thức máu kiểm tra chỉ số thể tích trung bình hồng cầu MCV tăng cao '
                             'trên 100 fl, nồng độ B12 huyết thanh dưới 200 pg/ml.',
                             'Xét nghiệm kháng thể kháng tế bào thành dạ dày và kháng thể kháng yếu tố nội tại '
                             'Intrinsic Factor để xác định bệnh thiếu máu Biermer.',
                             'Theo dõi số lượng hồng cầu lưới tăng vọt sau 5-7 ngày bắt đầu tiêm B12, kiểm tra nồng độ '
                             'kali máu đề phòng hạ kali máu cấp trong giai đoạn sinh máu bù.',
                             'Tư vấn chế độ ăn bổ sung thực phẩm giàu B12 từ thịt đỏ trứng sữa gan động vật hoặc uống '
                             'viên bổ sung B12 hàng ngày suốt đời nếu cắt dạ dày.'],
    'bien_the_kham': [   'Da xanh niêm mạc nhợt ánh vàng nhẹ, lưỡi teo gai nhẵn bóng màu đỏ tươi (viêm lưỡi Hunter), '
                         'khám thần kinh thấy giảm cảm giác sâu rung âm thoa và tư thế khớp, nghiệm pháp Romberg dương '
                         'tính.',
                         'Khám khoang miệng: lưỡi đỏ rực như miếng thịt bò tươi các gai lưỡi teo phẳng nhẵn thín (viêm '
                         'lưỡi Hunter kinh điển), niêm mạc miệng nhợt nhạt.',
                         'Khám thần kinh: nghiệm pháp Romberg dương tính lảo đảo ngã khi nhắm mắt, cảm giác vị trí '
                         'ngón chân cái hai bên bị sai lệch hoàn toàn.',
                         'Cảm giác rung âm thoa 128Hz mất hoàn toàn ở mắt cá chân và củ xương chày hai bên, phản xạ '
                         'gân gót Achilles tăng nhẹ kèm dấu Babinski nghi ngờ.',
                         'Bệnh nhân dáng đi thất điều cảm giác dập mạnh gót chân xuống sàn nhà khi bước đi, trí nhớ '
                         'ngắn hạn giảm sút, định hướng thời gian chậm.',
                         'Khám toàn thân: da màu vàng rơm nhạt củng mạc mắt hơi ánh vàng do tán huyết nhẹ trong tủy '
                         'xương, tim đập nhanh 96 l/p có tiếng thổi tâm thu cơ năng 2/6.'],
    'chan_doan': 'Thiếu vitamin B12 có biểu hiện thiếu máu hồng cầu to và thoái hóa kết hợp tủy sống.',
    'chinh': [   'mệt mỏi hoa mắt chóng mặt da xanh xao ánh vàng rơm',
                 'tê bì châm chích như kiến bò đối xứng ở đầu ngón tay và ngón chân',
                 'lưỡi đỏ rát mất gai lưỡi bóng nhẵn sưng đau khó ăn uống'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'huyết học',
    'ke_hoach': 'Xét nghiệm định lượng vitamin B12 huyết thanh, acid folic, huyết đồ xem kích thước hồng cầu MCV, tiêm '
                'bắp vitamin B12 liều cao hydroxocobalamin theo phác đồ tấn công.',
    'kham': 'Da xanh niêm mạc nhợt ánh vàng nhẹ, lưỡi teo gai nhẵn bóng màu đỏ tươi (viêm lưỡi Hunter), khám thần kinh '
            'thấy giảm cảm giác sâu rung âm thoa và tư thế khớp, nghiệm pháp Romberg dương tính.',
    'nhom': 'người lớn',
    'phu': [   'dáng đi loạng choạng mất thăng bằng đặc biệt khi nhắm mắt hoặc trong bóng tối',
               'suy giảm trí nhớ hay quên lú lẫn thay đổi tính tình cáu gắt',
               'tiền sử ăn chay trường nghiêm ngặt hoặc đã phẫu thuật cắt dạ dày ruột'],
    'ten': 'thiếu vitamin B12'},
    {   'bien_the_chan_doan': [   'Bệnh động mạch ngoại biên chi dưới bên phải giai đoạn 2 Fontaine (đau cách hồi).',
                              'Bệnh động mạch ngoại biên chi dưới hai bên do xơ vữa động mạch tắc nghẽn mạn tính.',
                              'Theo dõi bệnh động mạch ngoại biên chi dưới giai đoạn thiếu máu chi đe dọa đoạn chi cấp '
                              'CLTI.',
                              'Bệnh động mạch ngoại biên chi dưới ở bệnh nhân đái tháo đường típ 2 lâu năm.',
                              'Bệnh động mạch ngoại biên chi dưới giai đoạn 3 đau liên tục lúc nghỉ ban đêm.',
                              'Bệnh động mạch ngoại biên chi dưới tắc mạn tính tầng chậu đùi bên phải.'],
    'bien_the_ke_hoach': [   'Đo chỉ số ABI, siêu âm Doppler mạch máu chi dưới, dùng thuốc chống ngưng tập tiểu cầu '
                             'aspirin statin thuốc giãn mạch cilostazol và tập đi bộ có giám sát.',
                             'Kê đơn cilostazol 100mg ngày 2 lần giúp cải thiện khoảng cách đi bộ không đau, kết hợp '
                             'clopidogrel 75mg và atorvastatin 40mg kiểm soát mảng xơ vữa.',
                             'Chỉ định siêu âm Doppler mạch máu động mạch chi dưới khảo sát vị trí mức độ hẹp vôi hóa '
                             'thành mạch từ động mạch chậu đến động mạch mu chân.',
                             'Tư vấn bắt buộc cai nghiện thuốc lá hoàn toàn, hướng dẫn chương trình tập luyện đi bộ '
                             'ngắt quãng ít nhất 30 phút/ngày 3-5 ngày mỗi tuần.',
                             'Chụp cắt lớp vi tính mạch máu CTA chi dưới dựng hình hệ động mạch nếu chỉ số ABI dưới '
                             '0.5 để đánh giá can thiệp nong mạch đặt stent.',
                             'Chăm sóc bàn chân tỉ mỉ tránh va chạm cọ xát gây loét thiếu máu hoại tử khô, hội chẩn '
                             'bác sĩ Phẫu thuật Tim mạch lồng ngực can thiệp tái tưới máu.'],
    'bien_the_kham': [   'Mạch mu chân và mạch chày sau bên phải bắt rất yếu hoặc mất hoàn toàn, da bàn chân phải lạnh '
                         'nhạt màu, đo chỉ số huyết áp cổ chân - cánh tay ABI đạt 0.65.',
                         'Nghiệm pháp Buerger dương tính: nâng chân phải lên cao 60 độ trong 1 phút da bàn chân tái '
                         'nhợt trắng bệch, hạ chân buông thõng xuống da chuyển đỏ tím chậm trên 20 giây.',
                         'Bắt mạch chi dưới: mạch đùi và mạch khoeo bên phải nẩy yếu, mạch mu chân không bắt được, '
                         'nhiệt độ da bàn chân phải thấp hơn bàn chân trái 2 độ C.',
                         'Khám thực thể chi dưới: teo cơ cẳng chân phải chu vi bắp chân nhỏ hơn bên trái 2cm, móng '
                         'chân dày xù xì biến màu nâu, da mu chân khô bóng nhẵn rụng hết lông.',
                         'Đo chỉ số áp lực cổ chân - cánh tay ABI hai bên: chân trái 0.95 bình thường, chân phải 0.60 '
                         'hẹp động mạch mức độ trung bình, nghe thấy tiếng thổi tâm thu ở động mạch đùi phải.',
                         'Bàn chân phải có vết loét nông ở đầu ngón 1 do thiếu máu nuôi ranh giới rõ đáy khô xám không '
                         'có mủ, chạm vào bệnh nhân đau thốn.'],
    'chan_doan': 'Bệnh động mạch ngoại biên chi dưới bên phải giai đoạn 2 Fontaine (đau cách hồi).',
    'chinh': [   'đau nhức bắp chân khi đi bộ một đoạn phải dừng lại nghỉ thì hết đau (cơn đau cách hồi)',
                 'khoảng cách đi bộ không đau ngày càng rút ngắn dần',
                 'chân bên bệnh cảm giác lạnh buốt tê bì teo cơ so với chân lành'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tim mạch',
    'ke_hoach': 'Đo chỉ số ABI, siêu âm Doppler mạch máu chi dưới, dùng thuốc chống ngưng tập tiểu cầu aspirin statin '
                'thuốc giãn mạch cilostazol và tập đi bộ có giám sát.',
    'kham': 'Mạch mu chân và mạch chày sau bên phải bắt rất yếu hoặc mất hoàn toàn, da bàn chân phải lạnh nhạt màu, đo '
            'chỉ số huyết áp cổ chân - cánh tay ABI đạt 0.65.',
    'nhom': 'người lớn',
    'phu': [   'tiền sử hút thuốc lá nhiều năm tăng huyết áp xơ vữa động mạch hoặc đái tháo đường',
               'móng chân dày sần sùi giòn dễ gãy lông cẳng chân rụng trụi',
               'da cẳng bàn chân tái nhợt khi giơ cao và tím đỏ thẫm khi buông thõng'],
    'ten': 'bệnh động mạch ngoại biên chi dưới'},
    {   'bien_the_chan_doan': [   'Nhịp nhanh trên thất kịch phát SVT nghi cơn tim nhanh vào lại nút nhĩ thất AVNRT.',
                              'Nhịp nhanh trên thất kịch phát nghi cơn tim nhanh vào lại nhĩ thất AVRT hội chứng WPW.',
                              'Cơn nhịp nhanh trên thất kịch phát huyết động ổn định.',
                              'Theo dõi nhịp nhanh trên thất kịch phát tái phát nhiều đợt trong tuần.',
                              'Nhịp nhanh trên thất kịch phát đã cắt cơn bằng nghiệm pháp Valsalva.',
                              'Cơn tim nhanh trên thất kịch phát có hạ huyết áp tư thế nhẹ trong cơn.'],
    'bien_the_ke_hoach': [   'Ghi điện tâm đồ 12 chuyển đạo khẩn cấp, làm nghiệm pháp cường phế vị Valsalva cải tiến, '
                             'tiêm tĩnh mạch nhanh thuốc adenosine cắt cơn nếu nghiệm pháp thất bại.',
                             'Ghi điện tâm đồ 12 cần ngay trong cơn: phức bộ QRS hẹp đều tần số 180 l/p không thấy '
                             'sóng P hoặc sóng P âm giả dính ngay sau phức bộ QRS.',
                             'Hướng dẫn bệnh nhân thực hiện nghiệm pháp Valsalva cải tiến (thổi vào bơm tiêm 20ml '
                             'trong 15 giây rồi nằm ngửa nâng cao chân 45 độ).',
                             'Chuẩn bị tiêm tĩnh mạch bolus cực nhanh adenosine 6mg qua tĩnh mạch lớn gần tim kèm bơm '
                             'xả nhanh 20ml nước muối sinh lý dưới máy monitor theo dõi.',
                             'Xét nghiệm điện giải đồ kiểm tra kali magie máu, hormone tuyến giáp TSH Free T4 loại trừ '
                             'cơn cường giáp gây loạn nhịp.',
                             'Tư vấn chuyển viện chuyên khoa Tim mạch làm thăm dò điện sinh lý tim và can thiệp triệt '
                             'đốt đường dẫn truyền phụ bằng sóng radio RF dứt điểm.'],
    'bien_the_kham': [   'Nhịp tim đều tăm tắp tần số tim đập rất nhanh 180 lần/phút, tiếng tim T1 T2 thanh gọn không '
                         'nghe thấy tiếng thổi bệnh lý, huyết áp 110/70 mmHg.',
                         'Khám trong cơn: bệnh nhân lo âu hốt hoảng vã mồ hôi, mạch quay bắt nhanh nhỏ đều tăm tắp khó '
                         'đếm đếm được khoảng 190 nhịp/phút, SpO2 97%.',
                         'Khám tim: mỏm tim đập nhanh liên hồi ở khoang liên sườn 5 đường giữa đòn trái, diện tim bình '
                         'thường, không có tiếng ngựa phi T3, phổi hai bên trong.',
                         'Huyết áp đo tay 105/65 mmHg ổn định chưa có dấu hiệu sốc tụt huyết áp, tĩnh mạch cổ có sóng '
                         'đập nhanh đều nhịp nhàng theo nhịp tim.',
                         'Thực hiện xoa xoang cảnh một bên dưới theo dõi monitor: nhịp tim đột ngột chậm lại nhảy về '
                         'nhịp xoang đều 75 lần/phút, bệnh nhân thấy nhẹ bẫng lồng ngực ngay tức thì.',
                         'Khám thực thể: nhịp tim đập liên hồi tần số 175 chu kỳ/phút, không có ran ẩm ứ huyết ở phổi, '
                         'không có phù ngoại biên, tri giác tỉnh táo tiếp xúc tốt.'],
    'chan_doan': 'Nhịp nhanh trên thất kịch phát SVT nghi cơn tim nhanh vào lại nút nhĩ thất AVNRT.',
    'chinh': [   'cơn hồi hộp đánh trống ngực tim đập dồn dập xuất hiện đột ngột và kết thúc đột ngột',
                 'cảm giác tim đập thình thịch như muốn nhảy ra khỏi lồng ngực',
                 'mệt lả khó thở tức ngực chóng mặt hoa mắt trong cơn'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tim mạch',
    'ke_hoach': 'Ghi điện tâm đồ 12 chuyển đạo khẩn cấp, làm nghiệm pháp cường phế vị Valsalva cải tiến, tiêm tĩnh '
                'mạch nhanh thuốc adenosine cắt cơn nếu nghiệm pháp thất bại.',
    'kham': 'Nhịp tim đều tăm tắp tần số tim đập rất nhanh 180 lần/phút, tiếng tim T1 T2 thanh gọn không nghe thấy '
            'tiếng thổi bệnh lý, huyết áp 110/70 mmHg.',
    'nhom': 'người lớn',
    'phu': [   'cảm giác mạch đập thình thịch rõ ở vùng cổ họng',
               'buồn tiểu và đi tiểu tiện nhiều lần nước tiểu trong sau khi cơn nhịp nhanh chấm dứt',
               'tiền sử đã từng xuất hiện các cơn tương tự tự hết sau khi nín thở rặn hoặc uống ngụm nước lạnh'],
    'ten': 'nhịp nhanh trên thất kịch phát'},
    {   'bien_the_chan_doan': [   'Viêm vùng chậu cấp tính mức độ nhẹ đến trung bình nghi do lậu hoặc Chlamydia.',
                              'Viêm vùng chậu cấp tính đợt đầu sau thủ thuật nạo hút buồng tử cung.',
                              'Theo dõi viêm vùng chậu có nguy cơ hình thành khối áp xe vòi trứng buồng trứng TOA.',
                              'Viêm vùng chậu cấp tính trên người mang vòng tránh thai IUD.',
                              'Viêm vùng chậu mạn tính đợt bùng phát cấp tính.',
                              'Viêm vùng chậu do tạp khuẩn phối hợp vi khuẩn kỵ khí.'],
    'bien_the_ke_hoach': [   'Kháng sinh đồ phối hợp tiêm bắp ceftriaxone liều duy nhất kết hợp doxycycline và '
                             'metronidazole uống trong 14 ngày, kiêng quan hệ tình dục và điều trị đồng thời cho bạn '
                             'tình.',
                             'Chỉ định tiêm ceftriaxone 500mg bắp sâu một liều duy nhất, kê đơn doxycycline 100mg ngày '
                             '2 lần và metronidazole 500mg ngày 2 lần đủ 14 ngày liên tục.',
                             'Lấy dịch cổ tử cung làm xét nghiệm nhuộm soi vi khuẩn và xét nghiệm PCR tìm Chlamydia '
                             'trachomatis và Neisseria gonorrhoeae.',
                             'Siêu âm phụ khoa qua đầu dò âm đạo kiểm tra độ dày niêm mạc tử cung và loại trừ ổ áp xe '
                             'phần phụ hoặc dịch ứ đọng vòi trứng.',
                             'Tư vấn kiêng hoàn toàn quan hệ tình dục cho đến khi cả hai người hoàn thành đủ liệu '
                             'trình kháng sinh và hết sạch triệu chứng.',
                             'Hẹn khám lại đánh giá lâm sàng sau 72 giờ, nếu đau bụng tăng lên hoặc sốt cao cần nhập '
                             'viện chuyển sang kháng sinh truyền tĩnh mạch.'],
    'bien_the_kham': [   'Khám mỏ vịt âm đạo thấy nhiều khí hư mủ vàng cổ tử cung sung huyết đỏ dễ chảy máu, khám bằng '
                         'hai tay thấy lắc cổ tử cung đau chói (dấu hiệu Chandelier), tử cung và hai phần phụ ấn đau '
                         'tức nề nhẹ.',
                         'Dấu hiệu lắc cổ tử cung dương tính mạnh khiến bệnh nhân nhảy thót người vì đau chói, hai túi '
                         'cùng âm đạo ấn căng tức đau, cổ tử cung rỉ dịch mủ nhầy đục.',
                         'Khám phụ khoa: thân tử cung hơi to mềm ấn đau tức rõ, phần phụ bên phải sờ thấy dày nề ấn '
                         'đau thốn, không có khối áp xe phần phụ rõ rệt.',
                         'Khám mỏ vịt phát hiện viêm lộ tuyến cổ tử cung mủn đỏ rỉ máu khi chạm gạc, khí hư màu xanh '
                         'vàng bám dính thành âm đạo hôi nồng, thân nhiệt 38.3 độ C.',
                         'Khám bụng dưới: hạ vị hai bên ấn đau tức có phản ứng đề kháng cơ nhẹ, không có cảm ứng phúc '
                         'mạc toàn bụng, gan lách không to.',
                         'Khám bằng hai tay: đau nhói khi di động tử cung sang hai bên, cùng đồ sau đầy nhẹ ấn đau '
                         'tức, không có khối u buồng trứng tách biệt.'],
    'chan_doan': 'Viêm vùng chậu cấp tính mức độ nhẹ đến trung bình nghi do lậu hoặc Chlamydia.',
    'chinh': [   'đau tức âm ỉ hoặc quặn thắt liên tục vùng bụng dưới hạ vị',
                 'khí hư âm đạo ra nhiều mùi hôi tanh biến đổi màu vàng xanh',
                 'sốt nhẹ hoặc sốt vừa kèm ớn lạnh gai rét và mệt mỏi'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'sản phụ khoa',
    'ke_hoach': 'Kháng sinh đồ phối hợp tiêm bắp ceftriaxone liều duy nhất kết hợp doxycycline và metronidazole uống '
                'trong 14 ngày, kiêng quan hệ tình dục và điều trị đồng thời cho bạn tình.',
    'kham': 'Khám mỏ vịt âm đạo thấy nhiều khí hư mủ vàng cổ tử cung sung huyết đỏ dễ chảy máu, khám bằng hai tay thấy '
            'lắc cổ tử cung đau chói (dấu hiệu Chandelier), tử cung và hai phần phụ ấn đau tức nề nhẹ.',
    'nhom': 'người lớn',
    'phu': [   'đau rát dữ dội khi quan hệ tình dục hoặc khi đi tiểu tiện',
               'chảy máu âm đạo bất thường giữa kỳ kinh hoặc sau giao hợp',
               'tiền sử đặt dụng cụ tử cung tránh thai hoặc nhiễm khuẩn phụ khoa gần đây'],
    'ten': 'viêm vùng chậu'},
    {   'bien_the_chan_doan': [   'Tiền sản giật thai 34 tuần có dấu hiệu nặng cần theo dõi sát.',
                              'Tiền sản giật chưa có dấu hiệu nặng thai 35 tuần.',
                              'Tiền sản giật thể khởi phát sớm trước 34 tuần có biến chứng suy bánh nhau.',
                              'Theo dõi tiền sản giật có hội chứng HELLP tăng men gan giảm tiểu cầu.',
                              'Tiền sản giật thể nặng đe dọa sản giật cần dùng thuốc cắt cơn giật.',
                              'Tiền sản giật trên nền tăng huyết áp mạn tính từ trước mang thai.'],
    'bien_the_ke_hoach': [   'Chỉ định nhập viện khoa Sản bệnh lý theo dõi khẩn cấp, làm xét nghiệm đạm niệu 24 giờ, '
                             'tiểu cầu men gan creatinine, dùng thuốc hạ áp methyldopa và magie sulfat dự phòng co '
                             'giật sản giật.',
                             'Chuyển viện tuyến chuyên khoa Phụ sản bằng xe cứu thương có nhân viên y tế đi kèm, tiêm '
                             'tĩnh mạch magnesium sulfate chống co giật theo phác đồ Pritchard.',
                             'Kê đơn thuốc hạ huyết áp an toàn trong thai kỳ labetalol hoặc methyldopa 250mg, duy trì '
                             'huyết áp mục tiêu 130-140/80-90 mmHg.',
                             'Làm bilan tiền sản giật toàn diện: định lượng protein niệu 24 giờ, số lượng tiểu cầu, '
                             'men gan AST ALT, acid uric, đông máu toàn bộ.',
                             'Chạy máy Monitoring tim thai và cơn co tử cung CTG đánh giá sức khỏe thai nhi, siêu âm '
                             'Doppler màu động mạch rốn và động mạch não giữa thai.',
                             'Tiêm trưởng thành phổi thai nhi bằng betamethasone nếu tuổi thai từ 24 đến 34 tuần phòng '
                             'ngừa suy hô hấp sau sinh nếu phải đình chỉ thai kỳ sớm.'],
    'bien_the_kham': [   'Huyết áp đo hai tay 155/95 mmHg, phù trắng ấn lõm hai cẳng bàn chân độ 2, phù mi mắt và mu '
                         'bàn tay, tim thai nghe rõ 142 lần/phút, que thử nước tiểu protein niệu 2+.',
                         'Khám thai: thai phụ phù toàn thân ấn lõm sâu vùng trước xương chày, mặt tròn phù mi mắt, '
                         'huyết áp tái đo sau 15 phút nghỉ ngơi 160/100 mmHg.',
                         'Khám phản xạ gân xương bánh chè tăng nhạy hai bên, bề cao tử cung tương đương tuổi thai, tim '
                         'thai đập đều nhịp 138 l/p, bụng mềm ấn tức nhẹ hạ sườn phải.',
                         'Huyết áp đo tay phải 150/95 mmHg tay trái 152/96 mmHg, xét nghiệm que nhúng nước tiểu tại '
                         'chỗ protein 3+, thị lực hơi giảm nhẹ nhìn mờ.',
                         'Khám thực thể: thai phụ 32 tuần tuổi thai tỉnh táo, đau đầu vùng chẩm, phù mu bàn tay tháo '
                         'nhẫn không vừa, không có dấu hiệu co cứng cơ tử cung.',
                         'Dấu hiệu dọa sản giật: huyết áp tâm thu 160 mmHg, phản xạ gân xương tăng nhạy rõ, phù nề mi '
                         'mắt và cẳng chân độ 3, thai nhi cử động tốt.'],
    'chan_doan': 'Tiền sản giật thai 34 tuần có dấu hiệu nặng cần theo dõi sát.',
    'chinh': [   'huyết áp tăng cao trên 140/90 mmHg xuất hiện sau tuần thứ 20 của thai kỳ',
                 'xét nghiệm nước tiểu phát hiện có protein niệu đạm niệu dương tính',
                 'phù nề nhanh chóng mặt mắt cá chân mu bàn tay và mi mắt buổi sáng'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'sản phụ khoa',
    'ke_hoach': 'Chỉ định nhập viện khoa Sản bệnh lý theo dõi khẩn cấp, làm xét nghiệm đạm niệu 24 giờ, tiểu cầu men '
                'gan creatinine, dùng thuốc hạ áp methyldopa và magie sulfat dự phòng co giật sản giật.',
    'kham': 'Huyết áp đo hai tay 155/95 mmHg, phù trắng ấn lõm hai cẳng bàn chân độ 2, phù mi mắt và mu bàn tay, tim '
            'thai nghe rõ 142 lần/phút, que thử nước tiểu protein niệu 2+.',
    'nhom': 'người lớn',
    'phu': [   'đau đầu âm ỉ vùng trán mắt nhìn mờ hoa mắt có chấm sáng bay',
               'đau tức dữ dội vùng thượng vị hoặc hạ sườn phải buồn nôn',
               'tăng cân nhanh bất thường trên 1kg mỗi tuần do tích tụ nước'],
    'ten': 'tiền sản giật'},
    {   'bien_the_chan_doan': [   'Dọa sẩy thai 7 tuần có tụ dịch dưới màng nuôi mức độ nhẹ.',
                              'Dọa sẩy thai 6 tuần chưa có tim thai theo dõi thai sớm.',
                              'Dọa sẩy thai 9 tuần có hiện tượng bóc tách túi thai 10%.',
                              'Theo dõi dọa sẩy thai cần phân biệt với chửa ngoài tử cung thể thoái triển.',
                              'Dọa sẩy thai trên thai phụ có tiền sử sẩy thai liên tiếp.',
                              'Dọa sẩy thai giai đoạn ổn định sau điều trị giữ thai.'],
    'bien_the_ke_hoach': [   'Nghỉ ngơi tuyệt đối tại giường, kiêng quan hệ tình dục, siêu âm thai kiểm tra tim thai '
                             'và khối tụ dịch, bổ sung hormone progesterone dưỡng thai đường uống hoặc đặt âm đạo.',
                             'Chỉ định siêu âm thai đầu dò âm đạo khẩn cấp xác định vị trí thai trong buồng tử cung, '
                             'đo chiều dài đầu mông CRL và kiểm tra tim thai.',
                             'Kê đơn progesterone tự nhiên dạng đặt âm đạo utrogestan 200mg ngày 2 lần hoặc '
                             'dydrogesterone uống duy trì hỗ trợ hoàng thể thai kỳ.',
                             'Dặn dò thai phụ nằm nghỉ ngơi tại chỗ hạn chế tối đa đi lại lên xuống cầu thang, tránh '
                             'mang vác nặng và kiêng sinh hoạt vợ chồng.',
                             'Làm xét nghiệm định lượng beta-hCG máu hai lần cách nhau 48 giờ để đánh giá tốc độ phát '
                             'triển và sự sống của phôi thai.',
                             'Uống thuốc giảm co thắt tử cung spasmaverine nếu có cơn gò đau bụng dưới nhẹ, tái khám '
                             'siêu âm lại sau 1 tuần hoặc ngay khi máu ra nhiều.'],
    'bien_the_kham': [   'Khám mỏ vịt âm đạo thấy ít máu đỏ sẫm đọng cùng đồ sau, cổ tử cung còn đóng kín dài không '
                         'thấy tổ chức thai thập thò, thân tử cung to tương đương tuổi thai 7 tuần ấn đau tức nhẹ.',
                         'Khám âm đạo: cổ tử cung đóng chặt kín lỗ ngoài, đầu ngón tay không lọt, thân tử cung to mềm '
                         'tương đương thai 8 tuần, hai phần phụ mềm không sờ thấy khối bất thường.',
                         'Soi mỏ vịt thấy một ít máu nâu đen rỉ từ lỗ cổ tử cung ra thành âm đạo, không thấy khối mô '
                         'rách màng, âm đạo không sung huyết loét.',
                         'Khám thực thể: bụng mềm không có phản ứng thành bụng, vùng hạ vị ấn đau tức nhẹ khi sờ sâu, '
                         'không có dấu hiệu kích thích phúc mạc.',
                         'Cổ tử cung hình nón chắc đóng kín hoàn toàn, dịch máu trong lòng âm đạo số lượng rất ít '
                         'khoảng 2-3 giọt, thai phụ lo lắng nhiều.',
                         'Khám lâm sàng sản khoa: không có hiện tượng xóa mở cổ tử cung, tử cung kích thước phù hợp '
                         'tuổi thai chậm kinh, túi cùng âm đạo không đau nhói.'],
    'chan_doan': 'Dọa sẩy thai 7 tuần có tụ dịch dưới màng nuôi mức độ nhẹ.',
    'chinh': [   'ra máu âm đạo đỏ tươi hoặc nâu sẫm từng giọt trong 3 tháng đầu thai kỳ',
                 'đau bụng dưới âm ỉ quặn nhẹ từng cơn tương tự đau bụng kinh',
                 'cảm giác tức nặng vùng hạ vị và mỏi thắt lưng hông liên tục'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'sản phụ khoa',
    'ke_hoach': 'Nghỉ ngơi tuyệt đối tại giường, kiêng quan hệ tình dục, siêu âm thai kiểm tra tim thai và khối tụ '
                'dịch, bổ sung hormone progesterone dưỡng thai đường uống hoặc đặt âm đạo.',
    'kham': 'Khám mỏ vịt âm đạo thấy ít máu đỏ sẫm đọng cùng đồ sau, cổ tử cung còn đóng kín dài không thấy tổ chức '
            'thai thập thò, thân tử cung to tương đương tuổi thai 7 tuần ấn đau tức nhẹ.',
    'nhom': 'người lớn',
    'phu': [   'chậm kinh thử que thử thai hai vạch đậm rõ',
               'vú vẫn còn căng tức không có hiện tượng mất dấu hiệu thai nghén đột ngột',
               'máu ra ít không có mảnh mô màng phôi hay cục máu đông lớn thoát ra'],
    'ten': 'dọa sẩy thai'},
    {   'bien_the_chan_doan': [   'Tắc tia sữa nang sữa ứ đọng bên phải sau sinh ngày thứ năm.',
                              'Tắc tia sữa có dấu hiệu dọa viêm tuyến vú cấp tính bên phải.',
                              'Tắc tia sữa do bít tắc lỗ núm vú bởi nốt sữa đông kết.',
                              'Theo dõi tắc tia sữa hai bên thể cương sữa sinh lý sau sinh.',
                              'Tắc tia sữa tái phát nhiều lần do cấu tạo đầu núm vú thụt.',
                              'Tắc tia sữa cần can thiệp thông tắc bằng sóng siêu âm đa tần.'],
    'bien_the_ke_hoach': [   'Chườm ấm nhẹ nhàng, hướng dẫn kỹ thuật mát-xa thông nang tắc dọc ống dẫn sữa từ ngoài '
                             'vào núm vú, dùng máy hút sữa hút kiệt sau bú và hạ sốt bằng paracetamol.',
                             'Thực hiện vật lý trị liệu chiếu tia hồng ngoại hoặc siêu âm vi sóng làm tan cục sữa đông '
                             'vón, kết hợp mát-xa ép đẩy nhẹ nhàng hướng tâm.',
                             'Dùng gạc vô trùng thấm nước ấm làm mềm và gẩy nhẹ nốt cặn trắng bít tắc tại đầu núm vú '
                             'để khơi thông đường thoát của tia sữa.',
                             'Cho trẻ tích cực bú bên vú tắc trước khi đang đói để lực mút mạnh giúp thông tia sữa, '
                             'chỉnh lại khớp ngậm đúng ngậm sâu quầng vú.',
                             'Uống thuốc giảm đau kháng viêm paracetamol 500mg, chườm mát giữa các cữ bú để giảm phù '
                             'nề mô tuyến vú, uống nhiều nước ấm.',
                             'Theo dõi sát nhiệt độ nếu sốt cao trên 38.5 độ kèm quầng vú đỏ rực đau tăng dần cần dùng '
                             'thêm kháng sinh phòng ngừa áp xe hóa.'],
    'bien_the_kham': [   'Bầu vú bên phải căng tức to hơn bên trái, sờ thấy một khối chắc ranh giới rõ kích thước '
                         '4x5cm ở góc một phần tư trên ngoài ấn đau chói, núm vú nứt kẽ nhẹ không chảy mủ.',
                         'Khám vú phải: phát hiện nhiều khối tắc cục lổn nhổn sờ chắc như hòn bi nằm rải rác vùng '
                         'quầng vú, ấn đau tức buốt, da bề mặt căng bóng không đỏ tấy.',
                         'Núm vú bên phải có nốt bọng trắng sữa li ti (milk blister) làm bít tắc lỗ chân ống dẫn sữa, '
                         'bóp nhẹ núm vú không thấy tia sữa bắn ra.',
                         'Khám thực thể: thân nhiệt 38.1 độ C, vú trái mềm tiết sữa tốt, vú phải cương cứng như đá ấn '
                         'đau nhói, hạch nách cùng bên không sưng to.',
                         'Bầu vú cương tức lan tỏa, vùng một phần tư dưới ngoài hơi ửng hồng ấm nhẹ, các nang sữa ứ '
                         'đọng tạo dải cứng chắc dọc hướng về quầng vú.',
                         'Khám tuyến vú: không có dấu hiệu dao động sóng mủ (loại trừ áp xe vú), khối tắc chắc di động '
                         'nhẹ, ấn mạnh rỉ ra vài giọt sữa đặc quánh màu vàng.'],
    'chan_doan': 'Tắc tia sữa nang sữa ứ đọng bên phải sau sinh ngày thứ năm.',
    'chinh': [   'bầu vú căng tức cương cứng đau nhức nổi cục cục sau sinh',
                 'sữa mẹ không tiết ra được hoặc chỉ chảy nhỏ giọt ngắt quãng dù ngực rất căng sữa',
                 'đau nhức tăng dữ dội khi chạm vào hoặc khi trẻ ngậm bắt núm vú'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'sản phụ khoa',
    'ke_hoach': 'Chườm ấm nhẹ nhàng, hướng dẫn kỹ thuật mát-xa thông nang tắc dọc ống dẫn sữa từ ngoài vào núm vú, '
                'dùng máy hút sữa hút kiệt sau bú và hạ sốt bằng paracetamol.',
    'kham': 'Bầu vú bên phải căng tức to hơn bên trái, sờ thấy một khối chắc ranh giới rõ kích thước 4x5cm ở góc một '
            'phần tư trên ngoài ấn đau chói, núm vú nứt kẽ nhẹ không chảy mủ.',
    'nhom': 'người lớn',
    'phu': [   'sốt nhẹ gai rét mệt mỏi khó chịu toàn thân',
               'da vùng bầu vú có chỗ cương đỏ nóng nhẹ nhưng chưa hóa mủ',
               'tiền sử không vắt hết sữa thừa sau khi cho con bú hoặc dùng áo lót quá chật'],
    'ten': 'tắc tia sữa'},
    {   'bien_the_chan_doan': [   'Rối loạn tiền mãn kinh hội chứng vận mạch và niệu dục do suy giảm nội tiết tố buồng '
                              'trứng.',
                              'Rối loạn tiền mãn kinh thể ưu thế cơn bốc hỏa và rối loạn giấc ngủ.',
                              'Theo dõi rối loạn tiền mãn kinh có hội chứng teo đường niệu dục GSM.',
                              'Rối loạn tiền mãn kinh kèm theo loãng xương và đau mỏi cơ xương khớp.',
                              'Rối loạn tiền mãn kinh có rối loạn tâm lý lo âu trầm cảm thứ phát.',
                              'Rối loạn tiền mãn kinh thể rong kinh tiền mãn kinh cần sinh thiết nội mạc.'],
    'bien_the_ke_hoach': [   'Tư vấn chế độ dinh dưỡng bổ sung isoflavone phytoestrogen từ đậu nành, tập yoga đi bộ, '
                             'kê thuốc dưỡng ẩm bôi trơn âm đạo và xem xét liệu pháp hormone thay thế HRT liều thấp '
                             'nếu triệu chứng nặng.',
                             'Làm xét nghiệm định lượng hormone sinh dục nữ FSH tăng cao, LH, estradiol E2 giảm thấp, '
                             'đo mật độ xương DEXA tầm soát loãng xương.',
                             'Chỉ định siêu âm tử cung buồng trứng qua ngã âm đạo kiểm tra độ dày nội mạc tử cung, '
                             'chụp nhũ ảnh Mammography tầm soát u tuyến vú trước khi dùng thuốc.',
                             'Kê gel dưỡng ẩm âm đạo chứa acid hyaluronic dùng hàng ngày và chất bôi trơn gốc nước khi '
                             'sinh hoạt vợ chồng để cải thiện đau rát.',
                             'Bổ sung canxi nano 1000mg kết hợp vitamin D3 và magie hàng ngày, hướng dẫn bài tập thở '
                             'sâu và thư giãn giải tỏa stress.',
                             'Tư vấn liệu pháp nội tiết thay thế HRT phối hợp estrogen và progesterone tự nhiên liều '
                             'thấp nhất có hiệu quả nếu cơn bốc hỏa làm đảo lộn cuộc sống.'],
    'bien_the_kham': [   'Khám phụ khoa thấy niêm mạc âm đạo mỏng nhạt màu giảm độ ẩm ướt nếp gấp âm đạo mờ (teo nhẹ '
                         'niêm mạc do thiếu estrogen), tử cung phần phụ teo nhỏ sinh lý.',
                         'Khám mỏ vịt âm đạo: thành âm đạo khô trơn láng rải rác vài điểm xuất huyết chấm nhỏ li ti, '
                         'dịch âm đạo ít độ pH kiềm tính 5.5, cổ tử cung nhỏ nhẵn.',
                         'Khám thực thể: huyết áp dao động 130/80 mmHg, tim đập nhanh nhẹ lúc vào khám 88 l/p, da mặt '
                         'ửng hồng trong cơn bốc hỏa thoáng qua, khám tuyến giáp bình thường.',
                         'Khám tổng quát: thể trạng phụ nữ 48 tuổi, vòng eo tăng nhẹ, các khớp ngón tay ngón chân '
                         'không sưng viêm, tâm lý nhạy cảm dễ xúc động.',
                         'Thăm khám phụ khoa: tử cung nhỏ kích thước mãn kinh, hai buồng trứng teo nhỏ không sờ thấy u '
                         'bướu, không có điểm ấn đau vùng chậu.',
                         'Đánh giá thang điểm Kupperman về các triệu chứng mãn kinh đạt 28 điểm (mức độ trung bình), '
                         'biểu hiện rõ rệt hội chứng bốc hỏa và mất ngủ.'],
    'chan_doan': 'Rối loạn tiền mãn kinh hội chứng vận mạch và niệu dục do suy giảm nội tiết tố buồng trứng.',
    'chinh': [   'cơn bốc hỏa nóng bừng mặt và ngực bốc lên đầu vã mồ hôi đầm đìa ban đêm',
                 'rối loạn chu kỳ kinh nguyệt kinh thưa vòng kinh kéo dài hoặc rong kinh',
                 'mất ngủ trằn trọc khó vào giấc ngủ hay thức giấc nửa đêm giật mình'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'sản phụ khoa',
    'ke_hoach': 'Tư vấn chế độ dinh dưỡng bổ sung isoflavone phytoestrogen từ đậu nành, tập yoga đi bộ, kê thuốc dưỡng '
                'ẩm bôi trơn âm đạo và xem xét liệu pháp hormone thay thế HRT liều thấp nếu triệu chứng nặng.',
    'kham': 'Khám phụ khoa thấy niêm mạc âm đạo mỏng nhạt màu giảm độ ẩm ướt nếp gấp âm đạo mờ (teo nhẹ niêm mạc do '
            'thiếu estrogen), tử cung phần phụ teo nhỏ sinh lý.',
    'nhom': 'người lớn',
    'phu': [   'tâm trạng thay đổi thất thường dễ cáu gắt hồi hộp lo âu vô cớ',
               'khô rát âm đạo đau khi quan hệ tình dục giảm ham muốn tình dục',
               'da khô sạm nám tàn nhang rụng tóc và đau nhức xương khớp rải rác'],
    'ten': 'rối loạn tiền mãn kinh'},
    {   'bien_the_chan_doan': [   'Viêm nha chu mạn tính giai đoạn tiến triển có túi mủ nha chu.',
                              'Viêm nha chu mạn tính mức độ nặng độ 3 giai đoạn C theo phân loại AAP.',
                              'Theo dõi viêm nha chu tấn công tiến triển nhanh ở người trẻ tuổi.',
                              'Viêm nha chu có áp xe nha chu cấp tính ở răng hàm dưới.',
                              'Viêm nha chu trên bệnh nhân đái tháo đường kiểm soát kém.',
                              'Viêm nha chu khu trú vùng răng cửa và răng cối lớn thứ nhất.'],
    'bien_the_ke_hoach': [   'Lấy cao răng trên và dưới nướu triệt để, nạo túi nha chu làm nhẵn chân răng, súc miệng '
                             'dung dịch chlorhexidine 0.12% và kê kháng sinh spiramycin phối hợp metronidazole.',
                             'Lập phác đồ điều trị nha chu không phẫu thuật: cạo vôi răng siêu âm, xử lý bề mặt gốc '
                             'chân răng SRP từng góc hàm dưới gây tê tại chỗ.',
                             'Bơm rửa túi nha chu hàng ngày bằng dung dịch povidone iodine 1% hoặc oxy già pha loãng, '
                             'đặt gel kháng sinh tại chỗ minocycline vào túi nha chu.',
                             'Kê đơn phối hợp kháng sinh chuyên khoa răng hàm mặt rodogyl (spiramycin + metronidazole) '
                             'uống trong 7 ngày giảm tải lượng vi khuẩn kỵ khí.',
                             'Hướng dẫn vệ sinh răng miệng tỉ mỉ: sử dụng bàn chải lông mềm chải kẽ răng, chỉ nha khoa '
                             'và máy tăm nước sau mỗi bữa ăn.',
                             'Đánh giá lại độ sâu túi nha chu sau 6-8 tuần, nếu túi nha chu còn sâu trên 5mm sẽ chỉ '
                             'định phẫu thuật vạt nha chu hoặc ghép xương ổ răng.'],
    'bien_the_kham': [   'Khám răng miệng thấy nướu sưng đỏ phì đại dễ chảy máu khi thăm khám, đo độ sâu túi nha chu '
                         'bằng cây đo túi đạt 5-6mm, có mủ rỉ ra ở bờ nướu răng hàm dưới, răng lung lay độ 2.',
                         'Thăm khám bằng thám trâm nha chu: phát hiện túi nha chu sâu từ 4-7mm tại các răng cối lớn, '
                         'chảy máu chân răng ngay khi chạm nhẹ (BOP dương tính 100%).',
                         'Lợi viền và gai nướu mất độ săn chắc, chuyển màu đỏ sẫm tím tái, tụt nướu lộ chân răng 3mm, '
                         'cao răng dưới nướu bám chặt đen sì quanh cổ răng.',
                         'Ấn nhẹ ngón tay lên vùng xương ổ răng thấy giọt mủ đục xì ra từ kẽ răng hàm, kiểm tra độ '
                         'lung lay thấy răng 36 và 46 lung lay theo chiều ngang độ 2.',
                         'Khám khoang miệng: hơi thở có mùi hôi đặc trưng của vi khuẩn kỵ khí nha chu, khớp cắn sang '
                         'chấn nhẹ ở các răng cửa lung lay xòe hình nan quạt.',
                         'Phim X-quang toàn cảnh Panorama cho thấy tiêu xương ổ răng theo chiều ngang và chiều dọc lan '
                         'rộng quá một phần hai chiều dài chân răng.'],
    'chan_doan': 'Viêm nha chu mạn tính giai đoạn tiến triển có túi mủ nha chu.',
    'chinh': [   'chảy máu chân răng tự nhiên hoặc khi đánh răng xỉa răng ăn đồ cứng',
                 'nướu lợi sưng đỏ tấy viền lợi tụt để lộ chân răng dài ra',
                 'răng lung lay xô lệch cảm giác yếu răng ê buốt khi ăn nhai'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'răng hàm mặt',
    'ke_hoach': 'Lấy cao răng trên và dưới nướu triệt để, nạo túi nha chu làm nhẵn chân răng, súc miệng dung dịch '
                'chlorhexidine 0.12% và kê kháng sinh spiramycin phối hợp metronidazole.',
    'kham': 'Khám răng miệng thấy nướu sưng đỏ phì đại dễ chảy máu khi thăm khám, đo độ sâu túi nha chu bằng cây đo '
            'túi đạt 5-6mm, có mủ rỉ ra ở bờ nướu răng hàm dưới, răng lung lay độ 2.',
    'nhom': 'cả hai',
    'phu': [   'hơi thở hôi kéo dài dù đã chải răng sạch sẽ',
               'ấn vào kẽ nướu thấy có dịch mủ trắng đục chảy ra',
               'cao răng mảng bám tích tụ nhiều dưới nướu chân răng sẫm màu'],
    'ten': 'viêm nha chu'},
    {   'bien_the_chan_doan': [   'Ù tai chủ quan mạn tính tai phải nghi do thoái hóa cơ quan Corti.',
                              'Ù tai thần kinh giác quan tai trái sau chấn thương âm thanh tiếng ồn.',
                              'Theo dõi ù tai do xơ cứng chuỗi xương con tai giữa giai đoạn sớm.',
                              'Ù tai chủ quan mạn tính mức độ nặng gây rối loạn giấc ngủ và lo âu.',
                              'Nghi ngờ ù tai triệu chứng đầu tiên của u bao dây thần kinh thính giác Schwannoma.',
                              'Ù tai hai bên do thoái hóa thính lực tuổi già Presbycusis.'],
    'bien_the_ke_hoach': [   'Đo thính lực đơn âm và nhĩ lượng đồ, chụp MRI góc cầu tiểu não loại trừ u dây thần kinh '
                             'số 8, dùng thuốc tăng tuần hoàn tai trong ginkgo biloba và liệu pháp âm thanh che lấp '
                             'tiếng ù.',
                             'Chỉ định đo thính lực đồ lời, đo âm ốc tai OAE và điện thính giác thân não ABR để xác '
                             'định chính xác tổn thương ốc tai hay sau ốc tai.',
                             'Kê đơn betahistine 16mg ngày 2 lần phối hợp cao bạch quả ginkgo biloba 80mg giúp tăng vi '
                             'tuần hoàn ốc tai và dinh dưỡng thần kinh thính giác.',
                             'Hướng dẫn sử dụng liệu pháp âm thanh che lấp tinnitus retraining therapy (TRT): nghe '
                             'tiếng ồn trắng, tiếng mưa rơi hoặc nhạc nhẹ khi ngủ để phân tán chú ý.',
                             'Tư vấn tâm lý trị liệu nhận thức hành vi CBT giúp giảm căng thẳng ám ảnh bởi tiếng ù '
                             'tai, tránh cà phê rượu bia thuốc lá làm tăng triệu chứng.',
                             'Hội chẩn chuyên khoa Tai Mũi Họng chỉ định đeo máy trợ thính tích hợp bộ tạo âm che '
                             'tiếng ù nếu có suy giảm thính lực kèm theo.'],
    'bien_the_kham': [   'Soi tai thấy màng nhĩ hai bên sáng bóng góc nón sáng tam giác bình thường không thủng không '
                         'ứ dịch, đo thính lực đồ có giảm thính lực tiếp nhận ở dải tần số cao 4000-8000Hz bên tai '
                         'phải.',
                         'Soi đèn khám tai: ống tai ngoài sạch không có nút ráy tai gây bít tắc, màng nhĩ màu trắng '
                         'xám trong suốt mấu ngắn xương búa rõ, cử động màng nhĩ tốt.',
                         'Khám nghiệm pháp âm thoa: nghiệm pháp Weber thiên về tai trái (tai lành), nghiệm pháp Rinne '
                         'dương tính cả hai tai (nghe đường khí tốt hơn đường xương).',
                         'Khám thực thể: nghe vùng quanh tai và mạch máu cổ không nghe thấy tiếng thổi đồng thì với '
                         'mạch đập (loại trừ ù tai khách quan do dị dạng mạch).',
                         'Khám các dây thần kinh sọ sọ não: dây V và VII bình thường, không có liệt mặt không có mất '
                         'cảm giác giác mạc, nghiệm pháp thăng bằng tiền đình tốt.',
                         'Bệnh nhân mệt mỏi than phiền tiếng vo ve liên tục tai trái làm mất ngủ, đo thính lực âm '
                         'trường phát hiện giảm nhẹ ngưỡng nghe tiếp nhận tần số cao.'],
    'chan_doan': 'Ù tai chủ quan mạn tính tai phải nghi do thoái hóa cơ quan Corti.',
    'chinh': [   'tiếng kêu vo ve như tiếng ve kêu tiếng sóng biển hoặc tiếng dế rả rích trong tai',
                 'tiếng ù tai xuất hiện liên tục hoặc từng lúc rõ nhất về đêm trong phòng yên tĩnh',
                 'nghe kém giảm thính lực nhẹ bên tai có tiếng ù'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tai mũi họng',
    'ke_hoach': 'Đo thính lực đơn âm và nhĩ lượng đồ, chụp MRI góc cầu tiểu não loại trừ u dây thần kinh số 8, dùng '
                'thuốc tăng tuần hoàn tai trong ginkgo biloba và liệu pháp âm thanh che lấp tiếng ù.',
    'kham': 'Soi tai thấy màng nhĩ hai bên sáng bóng góc nón sáng tam giác bình thường không thủng không ứ dịch, đo '
            'thính lực đồ có giảm thính lực tiếp nhận ở dải tần số cao 4000-8000Hz bên tai phải.',
    'nhom': 'người lớn',
    'phu': [   'căng thẳng mất ngủ mệt mỏi khó chịu không thể tập trung làm việc',
               'cảm giác đầy tức nặng nề trong ống tai',
               'tiền sử tiếp xúc với tiếng ồn lớn công nghiệp hoặc dùng thuốc độc cho tai'],
    'ten': 'ù tai'},
    {   'bien_the_chan_doan': [   'Chảy máu cam do tăng huyết áp kịch phát chảy máu mũi sau.',
                              'Chảy máu cam do tăng huyết áp mức độ nặng mất máu cấp tính.',
                              'Chảy máu cam do tăng huyết áp vị trí điểm mạch Woodruff mũi sau.',
                              'Theo dõi chảy máu cam do tăng huyết áp có nguy cơ tái phát cao.',
                              'Chảy máu cam do tăng huyết áp trên bệnh nhân đang dùng thuốc chống đông.',
                              'Cơn tăng huyết áp kịch phát biến chứng chảy máu cam ồ ạt.'],
    'bien_the_ke_hoach': [   'Hạ huyết áp khẩn cấp bằng thuốc nhỏ ngậm dưới lưỡi nifedipine hoặc tiêm tĩnh mạch, nhét '
                             'bấc mũi trước (anterior nasal packing) hoặc bấc mũi sau cầm máu, theo dõi mạch huyết áp '
                             'liên tục.',
                             'Dùng thuốc hạ huyết áp tĩnh mạch nicardipine truyền qua bơm tiêm điện kiểm soát hạ huyết '
                             'áp từ từ về mức an toàn 150/90 mmHg.',
                             'Tiến hành đặt merocel hoặc nhét meche mũi trước tẩm mỡ kháng sinh ép chặt điểm mạch cầm '
                             'máu, nếu còn chảy máu sau sẽ nhét bấc mũi sau hoặc đặt ống thông bóng Foley.',
                             'Tiêm tĩnh mạch thuốc cầm máu tranexamic acid 500mg, truyền dịch đẳng trương bù dịch và '
                             'làm xét nghiệm công thức máu kiểm tra hemoglobin hematocrit.',
                             'Chỉ định nội soi mũi xoang cầm máu bằng dao điện đông cao tần hoặc kẹp clip động mạch '
                             'bướm khẩu cái tại phòng mổ Tai Mũi Họng nếu nhét bấc thất bại.',
                             'Theo dõi sát dấu hiệu sinh tồn mạch huyết áp mỗi 30 phút, dặn dò bệnh nhân nằm đầu cao '
                             '30-45 độ nhổ máu ra khay không được nuốt.'],
    'bien_the_kham': [   'Huyết áp đo lúc vào khám tăng vọt 190/110 mmHg, máu đỏ tươi đang đùn chảy thành dòng từ hốc '
                         'mũi phải xuống thành sau họng, soi mũi trước thấy máu chảy từ phía sau vách ngăn.',
                         'Khám cấp cứu: bệnh nhân kích thích lo âu, huyết áp 185/105 mmHg mạch 102 l/p, dùng đèn soi '
                         'thấy máu đỏ tươi chảy xối xả từ cuốn mũi dưới bên trái ra cửa mũi trước.',
                         'Soi thành sau họng thấy dải máu đỏ tươi chảy liên tục từ vòm mũi họng xuống hạ họng, bệnh '
                         'nhân ho khạc nhổ ra nhiều cục máu đông đỏ thẫm.',
                         'Đặt banh mũi hút sạch máu cục thấy vị trí chảy máu từ động mạch bướm khẩu cái mũi sau, máu '
                         'phun thành tia nhỏ theo nhịp mạch đập.',
                         'Khám thần kinh nhanh: bệnh nhân tỉnh táo không yếu liệt tay chân, đồng tử hai bên đều có '
                         'phản xạ tốt, không có dấu hiệu tai biến mạch máu não kèm theo.',
                         'Khám thực thể: da mặt sung huyết đỏ bừng, nghe tim T2 đanh rõ ở ổ van động mạch chủ, nhịp '
                         'tim đều nhanh, phổi không ran ứ huyết.'],
    'chan_doan': 'Chảy máu cam do tăng huyết áp kịch phát chảy máu mũi sau.',
    'chinh': [   'máu đỏ tươi chảy ồ ạt từ một hoặc cả hai lỗ mũi khó cầm',
                 'máu cam chảy liên tục kèm nuốt thấy máu tươi tanh nồng ở cổ họng',
                 'xuất hiện đồng thời với cơn tăng huyết áp kịch phát đau đầu chóng mặt'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tai mũi họng',
    'ke_hoach': 'Hạ huyết áp khẩn cấp bằng thuốc nhỏ ngậm dưới lưỡi nifedipine hoặc tiêm tĩnh mạch, nhét bấc mũi trước '
                '(anterior nasal packing) hoặc bấc mũi sau cầm máu, theo dõi mạch huyết áp liên tục.',
    'kham': 'Huyết áp đo lúc vào khám tăng vọt 190/110 mmHg, máu đỏ tươi đang đùn chảy thành dòng từ hốc mũi phải '
            'xuống thành sau họng, soi mũi trước thấy máu chảy từ phía sau vách ngăn.',
    'nhom': 'người lớn',
    'phu': [   'mặt đỏ bừng bừng tim đập nhanh hồi hộp tức ngực',
               'tiền sử tăng huyết áp điều trị không đều hoặc quên uống thuốc hạ áp',
               'bệnh nhân hốt hoảng sợ hãi khi nhìn thấy lượng máu chảy nhiều'],
    'ten': 'chảy máu cam do tăng huyết áp'},
    {   'bien_the_chan_doan': [   'Nấm bàn chân thể kẽ ngón chân do nấm sợi Trichophyton rubrum (nước ăn chân).',
                              'Nấm bàn chân thể tróc vảy khô dày sừng hai bên mạn tính.',
                              'Nấm bàn chân thể mụn nước có ngứa dữ dội.',
                              'Theo dõi nấm bàn chân có bội nhiễm vi khuẩn gây viêm mô tế bào cẳng chân.',
                              'Nấm bàn chân kết hợp nấm móng chân cái do dermatophytes.',
                              'Nấm da bàn chân tinea pedis thể hỗn hợp kẽ ngón và mụn nước.'],
    'bien_the_ke_hoach': [   'Giữ bàn chân khô ráo thoáng khí, bôi kem chống nấm terbinafine 1% hoặc clotrimazole ngày '
                             '2 lần trong 2-4 tuần, rắc bột chống nấm vào giày và tất.',
                             'Chỉ định bôi thuốc kháng nấm terbinafine 1% cream liên tục 14 ngày, tiếp tục bôi thêm 1 '
                             'tuần sau khi tổn thương da đã lành hẳn để diệt sạch mầm nấm.',
                             'Ngâm chân bằng nước ấm pha thuốc tím pha loãng 1/10.000 hoặc nước muối loãng 15 phút mỗi '
                             'tối làm sạch se khô vết loét trợt trước khi bôi thuốc.',
                             'Kê đơn thuốc kháng nấm đường uống itraconazole 100mg ngày 2 viên trong 1 tuần nếu tổn '
                             'thương dày sừng lan rộng hoặc thất bại với thuốc bôi.',
                             'Hướng dẫn vệ sinh: giặt tất bằng nước nóng phơi dưới nắng to, thay tất hàng ngày, chọn '
                             'giày thông thoáng có lỗ thoát khí, không dùng chung khăn lau chân.',
                             'Kê thuốc kháng histamin cetirizine 10mg buổi tối giảm ngứa chống cào gãi gây trầy xước '
                             'nhiễm trùng thứ phát vi khuẩn tụ cầu.'],
    'bien_the_kham': [   'Da kẽ ngón chân 3-4 và 4-5 hai bên bàn chân bong trợt thượng bì màu trắng mủn như ngâm nước, '
                         'nền dưới đỏ ướt rỉ dịch nhẹ, viền có vảy da mỏng, không có mủ bội nhiễm.',
                         'Tổn thương da kẽ ngón chân: lớp sừng mủn trắng dày bợt ra, bóc nhẹ để lộ vết nứt kẽ nông đỏ '
                         'rát chảy dịch trong, ngứa nhiều khi khám.',
                         'Khám rìa gan bàn chân thấy các đám mụn nước sâu dạng tổ đỉa kích thước 1-2mm mọc rải rác '
                         'trên nền da đỏ, bờ tổn thương viền vảy rõ (thể mụn nước).',
                         'Lòng bàn chân hai bên da dày sừng bong vảy mịn dạng bột phấn trắng dọc các nếp gấp da (thể '
                         'dày sừng dạng giày moccasin), không có sưng nóng mu chân.',
                         'Soi tươi vảy da kẽ ngón chân dưới kính hiển vi với dung dịch KOH 10%: phát hiện nhiều sợi '
                         'nấm có vách ngăn và bào tử nấm sợi phát triển.',
                         'Khám thực thể: các kẽ ngón chân ẩm ướt bốc mùi hôi nấm mốc, da bờ kẽ nứt kẽ gây đau buốt nhẹ '
                         'khi xòe ngón chân, móng chân chưa biến dạng.'],
    'chan_doan': 'Nấm bàn chân thể kẽ ngón chân do nấm sợi Trichophyton rubrum (nước ăn chân).',
    'chinh': [   'ngứa ngáy dữ dội kẽ các ngón chân đặc biệt là kẽ ngón 3-4 và 4-5',
                 'da kẽ ngón chân bị mủn trắng bong tróc trợt đỏ rớm dịch ướt át',
                 'mùi hôi chân khó chịu nồng nặc tăng khi đi tất giày bít bùng kín'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'da liễu',
    'ke_hoach': 'Giữ bàn chân khô ráo thoáng khí, bôi kem chống nấm terbinafine 1% hoặc clotrimazole ngày 2 lần trong '
                '2-4 tuần, rắc bột chống nấm vào giày và tất.',
    'kham': 'Da kẽ ngón chân 3-4 và 4-5 hai bên bàn chân bong trợt thượng bì màu trắng mủn như ngâm nước, nền dưới đỏ '
            'ướt rỉ dịch nhẹ, viền có vảy da mỏng, không có mủ bội nhiễm.',
    'nhom': 'cả hai',
    'phu': [   'thói quen thường xuyên đi giày ẩm ướt lội nước bẩn hoặc đi bơi công cộng',
               'rìa bàn chân xuất hiện các mụn nước nhỏ sâu ngứa ngáy khó chịu',
               'móng chân cái cùng bên có thể bị dày sừng xù xì ngả màu vàng đục'],
    'ten': 'nấm bàn chân'},
    {   'bien_the_chan_doan': [   'Herpes môi tái phát do virus Herpes simplex típ 1 (HSV-1).',
                              'Herpes môi tái phát thể mụn nước điển hình giai đoạn tiến triển ngày thứ 2.',
                              'Herpes môi tái phát có đóng vảy tiết giai đoạn hồi phục.',
                              'Theo dõi herpes môi tái phát đợt cấp sau nhiễm siêu vi cảm lạnh.',
                              'Herpes môi tái phát thể nặng tổn thương lan rộng quanh miệng.',
                              'Nhiễm virus Herpes simplex môi tái phát có bội nhiễm vi khuẩn nhẹ viền vảy.'],
    'bien_the_ke_hoach': [   'Bôi kem kháng virus acyclovir 5% ngày 5 lần càng sớm càng tốt, uống acyclovir 400mg ngày '
                             '3 lần trong 5 ngày nếu tổn thương lan rộng và tránh sờ chạm gãi lây lan.',
                             'Bôi kem acyclovir hoặc valacyclovir cách nhau mỗi 4 giờ ngay từ giai đoạn có cảm giác '
                             'tiền triệu ngứa râm ran để ức chế virus nhân lên.',
                             'Uống thuốc kháng virus acyclovir 400mg x 3 lần/ngày trong 5 ngày liên tục hoặc '
                             'valacyclovir 1000mg ngày 2 lần trong 1 ngày rút ngắn thời gian lành bệnh.',
                             'Chấm dung dịch sát khuẩn dịu da milian hoặc betadine pha loãng khi mụn nước vỡ để ngăn '
                             'ngừa nhiễm trùng vi khuẩn thứ phát tạo mủ.',
                             'Dặn dò bệnh nhân rửa tay sạch sau khi chạm vào môi, không hôn người khác đặc biệt là trẻ '
                             'sơ sinh, không dùng chung cốc uống nước khăn mặt và son môi.',
                             'Thoa kem chống nắng cho môi khi ra ngoài trời, duy trì chế độ sinh hoạt giảm căng thẳng '
                             'lo âu để hạn chế số lần tái phát trong năm.'],
    'bien_the_kham': [   'Ranh giới da niêm mạc bờ môi trên bên phải có một đám mụn nước nhỏ như hạt tấm kích thước '
                         '1x1.5cm xếp thành chùm trên nền hồng ban sung huyết, một số nốt đã vỡ rớm dịch vàng đóng vảy '
                         'tiết.',
                         'Khám vùng môi: khóe mép bên trái có chùm mụn nước căng chứa dịch trong mọc cụm hình hoa cúc, '
                         'vùng da xung quanh nề đỏ rát buốt khi cử động miệng.',
                         'Tổn thương bờ môi dưới: đám mụn nước đã khô tạo thành vảy tiết màu nâu vàng mật ong bám '
                         'chặt, bóc nhẹ thấy đáy trợt đỏ rớm máu nhẹ, không có mủ đục.',
                         'Khám đầu mặt cổ: hạch dưới cằm và hạch góc hàm cùng bên sờ chạm to khoảng 1cm mềm ấn hơi tức '
                         'nhẹ, niêm mạc nướu họng hoàn toàn bình thường.',
                         'Bệnh nhân than đau rát nhức nhối vùng mép môi khi ăn đồ mặn cay, đám bọng nước li ti ranh '
                         'giới rõ ràng với da lành, không có sưng phù mặt.',
                         'Khám thực thể: tổn thương da herpes điển hình ở nhân trung mép môi, các mụn nước nhỏ đứng '
                         'chen chúc thành cụm 8-10 nốt, cảm giác châm kim rát bỏng tại chỗ.'],
    'chan_doan': 'Herpes môi tái phát do virus Herpes simplex típ 1 (HSV-1).',
    'chinh': [   'chùm mụn nước nhỏ li ti nổi cụm trên nền da niêm mạc bờ môi đỏ rực',
                 'cảm giác nóng rát ngứa ngáy châm chích tại vị trí bờ môi trước khi mọc mụn',
                 'mụn nước nhanh chóng vỡ tạo thành vết trợt nông đóng vảy tiết màu vàng nâu'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'da liễu',
    'ke_hoach': 'Bôi kem kháng virus acyclovir 5% ngày 5 lần càng sớm càng tốt, uống acyclovir 400mg ngày 3 lần trong '
                '5 ngày nếu tổn thương lan rộng và tránh sờ chạm gãi lây lan.',
    'kham': 'Ranh giới da niêm mạc bờ môi trên bên phải có một đám mụn nước nhỏ như hạt tấm kích thước 1x1.5cm xếp '
            'thành chùm trên nền hồng ban sung huyết, một số nốt đã vỡ rớm dịch vàng đóng vảy tiết.',
    'nhom': 'cả hai',
    'phu': [   'tái phát nhiều lần tại cùng một vị trí mép môi hoặc nhân trung',
               'thường xuất hiện sau đợt cảm sốt stress căng thẳng tiếp xúc ánh nắng gắt',
               'hạch vùng dưới hàm cùng bên hơi sưng đau nhẹ thoáng qua'],
    'ten': 'herpes môi tái phát'},
]

# 50 khuon mo rong Lo 2 (Dot 1: khuon 251-300) da hien thuc hoa day du 6 bien the:
BENH_LO_2 = [
    {   'bien_the_chan_doan': [   'Lồng ruột cấp ở nhũ nhi thể hồi manh đại tràng.',
                              'Theo dõi lồng ruột cấp ở nhũ nhi đến sớm trước 24 giờ.',
                              'Lồng ruột cấp ở nhũ nhi có dấu hiệu tắc ruột cơ học.',
                              'Theo dõi lồng ruột cấp ở nhũ nhi biến chứng chảy máu tiêu hoá dưới.',
                              'Lồng ruột cấp ở nhũ nhi thể hồi hồi tràng hiếm gặp.',
                              'Lồng ruột cấp ở nhũ nhi giai đoạn chưa có hoại tử ruột.'],
    'bien_the_ke_hoach': [   'Cho trẻ nhịn bú hoàn toàn, đặt ống thông dạ dày giải áp, siêu âm bụng cấp cứu xác định '
                             'hình ảnh khối lồng bia đạn và chỉ định tháo lồng bằng hơi áp lực có kiểm soát.',
                             'Chỉ định siêu âm ổ bụng khẩn cấp tìm dấu hiệu bánh sandwich, lập đường truyền tĩnh mạch '
                             'bù dịch điện giải, chuyển phòng thủ thuật bơm hơi tháo lồng.',
                             'Ngừng cho ăn đường miệng, đặt sonde dạ dày hút ngắt quãng, làm xét nghiệm công thức máu '
                             'và đông máu, chuẩn bị tháo lồng bằng áp lực khí dưới màn tăng sáng.',
                             'Thiết lập đường truyền tĩnh mạch dung dịch mặn đẳng trương, chụp X-quang bụng không '
                             'chuẩn bị, siêu âm khẳng định lồng ruột và hội chẩn ngoại nhi can thiệp tháo hơi.',
                             'Cho trẻ nằm phòng cấp cứu theo dõi sát mạch nhiệt độ, kháng sinh dự phòng ampicillin '
                             'phối hợp gentamicin, tháo lồng bằng hơi không mổ nếu chưa có viêm phúc mạc.',
                             'Nhập viện khoa Ngoại Nhi cấp cứu, hồi sức dịch tĩnh mạch tích cực, tiến hành siêu âm '
                             'hướng dẫn tháo khối lồng bằng thụt hơi áp lực tối đa 100-120 mmHg.'],
    'bien_the_kham': [   'Trẻ quấy khóc từng cơn ngắt quãng, bụng mềm có phản ứng nhẹ góc phần tư trên phải, nắn thấy '
                         'khối lồng dạng quả chuối di động nhẹ, thăm trực tràng găng có máu tươi theo nhầy.',
                         'Cơn khóc ngắt quãng điển hình, sờ nắn thượng vị và hạ sườn phải phát hiện khối mật độ chắc '
                         'dài 4cm di động nhẹ, hố chậu phải có cảm giác rỗng (dấu Dance).',
                         'Bé li bì giữa hai cơn đau quấy, bụng chướng nhẹ, nắn dọc khung đại tràng thấy khối tròn dài '
                         'như quả chuối, găng thăm hậu môn có máu nhầy đỏ thẫm dính theo.',
                         'Trẻ co chân khóc ngặt, bụng mềm, sờ thấy khối u lồng chắc nằm ngang dưới gan đẩy nhẹ di '
                         'động, nhịp tim nhanh 145 l/p do đau.',
                         'Khám bụng mềm không có phản xạ thành bụng lan toả, hạ sườn phải sờ chạm khối u hình trứng '
                         'chắc trơn láng, rút găng trực tràng có chất nhầy vệt máu.',
                         'Trẻ mệt mỏi quấy khóc ưỡn cong người, bụng chướng vừa, sờ thấy khối lồng ruột góc gan dài '
                         '3-5cm, thăm trực tràng thấy niêm mạc phù nề có dịch máu đỏ.'],
    'chan_doan': 'Lồng ruột cấp ở nhũ nhi thể hồi manh đại tràng.',
    'chinh': [   'trẻ khóc thét từng cơn ưỡn người co hai chân gập lên bụng',
                 'nôn trớ nhiều thức ăn sữa cũ kèm dịch mật xanh vàng',
                 'đi ngoài phân nhầy máu đỏ tươi như thạch hoặc nâu sẫm'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Cho trẻ nhịn bú hoàn toàn, đặt ống thông dạ dày giải áp, siêu âm bụng cấp cứu xác định hình ảnh khối '
                'lồng bia đạn và chỉ định tháo lồng bằng hơi áp lực có kiểm soát.',
    'kham': 'Trẻ quấy khóc từng cơn ngắt quãng, bụng mềm có phản ứng nhẹ góc phần tư trên phải, nắn thấy khối lồng '
            'dạng quả chuối di động nhẹ, thăm trực tràng găng có máu tươi theo nhầy.',
    'nhom': 'nhi',
    'phu': [   'giữa các cơn khóc trẻ mệt lả li bì bú kém bỏ bú',
               'bụng chướng nhẹ sờ thấy khối dài hình quả chuối ở hạ sườn phải',
               'thăm trực tràng rút găng có nhầy máu dính theo'],
    'ten': 'lồng ruột cấp ở nhũ nhi'},
    {   'bien_the_chan_doan': [   'Teo đường mật bẩm sinh ngoài gan thể teo hoàn toàn.',
                              'Theo dõi teo đường mật bẩm sinh hội chứng ứ mật sơ sinh tiến triển.',
                              'Teo đường mật bẩm sinh ngoài gan type 3.',
                              'Theo dõi teo đường mật bẩm sinh chưa có biến chứng xơ gan tăng áp cửa.',
                              'Teo đường mật bẩm sinh phát hiện sớm giai đoạn vàng trước 2 tháng tuổi.',
                              'Nghi ngờ teo đường mật bẩm sinh cần phân biệt với viêm gan sơ sinh khổng lồ.'],
    'bien_the_ke_hoach': [   'Xét nghiệm định lượng bilirubin máu trực tiếp, siêu âm gan mật nhịn bú 4 giờ tìm dấu '
                             'hiệu dải xơ hình tam giác, hội chẩn phẫu thuật nhi mổ Kasai trước 60 ngày tuổi.',
                             'Làm bộ xét nghiệm chức năng gan AST ALT GGT bilirubin toàn phần và trực tiếp, siêu âm '
                             'doppler mạch máu gan mật, chụp xạ hình đường mật HIDA.',
                             'Chỉ định sinh thiết gan qua da đánh giá tăng sinh ống mật và nút mật xơ hoá, hội chẩn '
                             'liên chuyên khoa Gan mật Nhi phẫu thuật nối mật ruột kiểu Kasai sớm.',
                             'Xét nghiệm đông máu cơ bản PT INR, bổ sung vitamin tan trong dầu A D E K tiêm bắp, chuẩn '
                             'bị chuyển tuyến trung ương phẫu thuật Kasai tạo lưu thông mật.',
                             'Nhập viện khoa Tiêu hoá Gan mật Nhi, siêu âm bụng đo kích thước túi mật trước và sau bú, '
                             'làm bilan loại trừ nhiễm trùng bẩm sinh TORCH và chuyển phẫu thuật.',
                             'Làm xét nghiệm gen và sinh hóa đánh giá ứ mật tiến triển, siêu âm gan xác định dấu dải '
                             'xơ tam giác rốn gan, lập kế hoạch phẫu thuật Kasai cấp thời.'],
    'bien_the_kham': [   'Da và củng mạc mắt nhuộm vàng sẫm sẫm màu nghệ, gan to 3cm dưới bờ hạ sườn mật độ chắc bờ '
                         'sắc, phân quan sát thực tế màu trắng xám như đất sét.',
                         'Vàng da ứ mật sẫm ánh đồng, củng mạc mắt vàng cam đậm, gan to 3,5cm dưới bờ sườn phải mật độ '
                         'chắc nhẵn, lách mấp mé bờ sườn.',
                         'Toàn thân vàng sậm màu, quan sát tã thấy phân hoàn toàn mất sắc tố mật trắng bệch như vôi, '
                         'gan sờ thấy dưới sườn 3cm bờ rõ đều.',
                         'Trẻ vàng da ứ mật tiến triển, ấn kính da vàng đậm không phai, khám bụng thấy gan to mấp mé '
                         'mào chậu phải bờ chắc sắc, lách chưa to.',
                         'Khám thấy vàng da ánh xanh củng mạc mắt vàng sẫm, gan mấp mé 4cm dưới sườn phải mật độ chắc '
                         'cứng, tĩnh mạch nông thành bụng hơi giãn nhẹ.',
                         'Vàng da sẫm kèm phân bạc màu liên tục trên 10 ngày, gan sờ thấy 2,5cm dưới bờ hạ sườn phải, '
                         'lách to độ 1, thóp phẳng không trũng.'],
    'chan_doan': 'Teo đường mật bẩm sinh ngoài gan thể teo hoàn toàn.',
    'chinh': [   'vàng da và vàng mắt xuất hiện từ tuần thứ hai sau sinh tăng dần',
                 'phân bạc màu như phân cò hoặc màu đất sét xám trắng',
                 'nước tiểu vàng sậm màu sẫm như nước chè đặc dính tã'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Xét nghiệm định lượng bilirubin máu trực tiếp, siêu âm gan mật nhịn bú 4 giờ tìm dấu hiệu dải xơ hình '
                'tam giác, hội chẩn phẫu thuật nhi mổ Kasai trước 60 ngày tuổi.',
    'kham': 'Da và củng mạc mắt nhuộm vàng sẫm sẫm màu nghệ, gan to 3cm dưới bờ hạ sườn mật độ chắc bờ sắc, phân quan '
            'sát thực tế màu trắng xám như đất sét.',
    'nhom': 'nhi',
    'phu': [   'gan to chắc mấp mé 3cm dưới bờ sườn phải',
               'trẻ vẫn bú tốt tăng cân chậm trong những tháng đầu',
               'bụng trướng bè hai bên kèm tuần hoàn bàng hệ nổi rõ'],
    'ten': 'teo đường mật bẩm sinh'},
    {   'bien_the_chan_doan': [   'Suy giáp bẩm sinh tiên phát do loạn sản tuyến giáp.',
                              'Theo dõi suy giáp bẩm sinh phát hiện qua sàng lọc sơ sinh lấy máu gót chân.',
                              'Suy giáp bẩm sinh tiên phát thể mất tuyến giáp hoàn toàn.',
                              'Suy giáp bẩm sinh do rối loạn tổng hợp hormone giáp trạng gia đình.',
                              'Theo dõi suy giáp bẩm sinh có biểu hiện phù niêm và chậm phát triển thể chất.',
                              'Suy giáp bẩm sinh thể nhẹ cần chuẩn độ liều hormone thay thế.'],
    'bien_the_ke_hoach': [   'Xét nghiệm định lượng TSH máu tăng cao kèm Free T4 giảm nặng, chụp xạ hình tuyến giáp, '
                             'bắt đầu liệu pháp hormone thay thế Levothyroxine liều 10-15 mcg/kg/ngày đường uống sớm.',
                             'Lấy máu tĩnh mạch định lượng ngay TSH và FT4 khẳng định chẩn đoán, siêu âm Doppler tuyến '
                             'giáp vùng cổ, khởi động điều trị Levothyroxine natri viên nghiền pha nước.',
                             'Chỉ định dùng L-thyroxine liều ban đầu 12 mcg/kg/ngày uống một lần vào buổi sáng trước '
                             'bú 30 phút, hẹn tái khám kiểm tra hormone giáp sau 2-4 tuần.',
                             'Làm xét nghiệm TSH FT3 FT4, chụp X-quang khớp gối tìm điểm cốt hoá đầu dưới xương đùi '
                             'đánh giá tuổi xương bào thai, bổ sung hormone giáp kịp thời tránh di chứng trí tuệ.',
                             'Hướng dẫn gia đình kỹ thuật nghiền thuốc Levothyroxine cho uống với vài giọt sữa mẹ, '
                             'theo dõi tăng trưởng chu vi vòng đầu và chiều cao hàng tháng.',
                             'Thiết lập phác đồ điều trị suy giáp thay thế hormone trọn đời, kiểm tra chức năng giáp '
                             'định kỳ mỗi 1-2 tháng trong năm đầu đời để chỉnh liều.'],
    'bien_the_kham': [   'Trẻ ít cử động vẻ mặt thờ thẫn phù niêm, thóp sau mở rộng 2cm, lưỡi to bè đẩy ra ngoài cung '
                         'răng, bụng to bè có thoát vị rốn nhỏ, phản xạ gân xương giảm.',
                         'Vẻ mặt phù niêm đặc trưng mi mắt sưng mọng, mũi tẹt gốc mũi gãy, lưỡi dày nhô ra khe môi, '
                         'thóp trước rộng 4x4cm, trương lực cơ toàn thân giảm.',
                         'Trẻ ngủ gà phản ứng chậm với kích thích, tiếng khóc trầm khàn, bụng trướng mềm có vòng rốn '
                         'giãn rộng thoát vị 1cm, da khô lạnh nổi vân tím.',
                         'Khám thấy vàng da kéo dài ở mặt và thân mình, thóp sau rộng 1,5cm chưa khép, gốc lưỡi dày '
                         'thè liên tục, nhịp tim chậm 100 lần/phút so với lứa tuổi sơ sinh.',
                         'Trẻ giảm trương lực cơ ngoại vi rõ, đầu to thóp rộng bờ thóp mềm, da nhợt nhạt bong vảy nhẹ, '
                         'sờ không thấy tuyến giáp vùng cổ trước.',
                         'Vẻ mặt ngơ ngác mi mắt nề, lưỡi to chiếm trọn khoang miệng, thân nhiệt đo hậu môn 36,1 độ C, '
                         'gân cơ tứ chi mềm nhẽo đáp ứng chậm chạp.'],
    'chan_doan': 'Suy giáp bẩm sinh tiên phát do loạn sản tuyến giáp.',
    'chinh': [   'vàng da sơ sinh kéo dài trên 3 tuần không tự thoái lui',
                 'chậm đi phân su bụng chướng to kèm táo bón dai dẳng',
                 'lưỡi to dày thè ra ngoài miệng thường xuyên'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nội tiết - chuyển hoá',
    'ke_hoach': 'Xét nghiệm định lượng TSH máu tăng cao kèm Free T4 giảm nặng, chụp xạ hình tuyến giáp, bắt đầu liệu '
                'pháp hormone thay thế Levothyroxine liều 10-15 mcg/kg/ngày đường uống sớm.',
    'kham': 'Trẻ ít cử động vẻ mặt thờ thẫn phù niêm, thóp sau mở rộng 2cm, lưỡi to bè đẩy ra ngoài cung răng, bụng to '
            'bè có thoát vị rốn nhỏ, phản xạ gân xương giảm.',
    'nhom': 'nhi',
    'phu': [   'trẻ ngủ li bì ít thức quấy khóc tiếng khàn đục',
               'thóp trước và thóp sau giãn rộng chậm đóng',
               'thân nhiệt hạ tay chân lạnh da khô ráp nhờn nhợt'],
    'ten': 'suy giáp bẩm sinh'},
    {   'bien_the_chan_doan': [   'Tăng sản thượng thận bẩm sinh thể mất muối thiếu hụt enzym 21-hydroxylase.',
                              'Theo dõi cơn suy thượng thận cấp trên nền tăng sản thượng thận bẩm sinh.',
                              'Tăng sản thượng thận bẩm sinh thể nam hoá đơn thuần phát hiện ở trẻ nhỏ.',
                              'Hội chứng tăng sản thượng thận bẩm sinh di truyền lặn NST thường.',
                              'Tăng sản thượng thận bẩm sinh thể mất muối nặng có rối loạn điện giải đe dọa tính mạng.',
                              'Nghi ngờ tăng sản thượng thận bẩm sinh do thiếu hụt men 11-beta-hydroxylase.'],
    'bien_the_ke_hoach': [   'Xét nghiệm cấp cứu điện giải đồ, 17-hydroxyprogesterone, cortisol máu, bù dịch điện giải '
                             'khẩn cấp bằng dung dịch mặn đẳng trương pha glucose, bổ sung Hydrocortisone và '
                             'Fludrocortisone.',
                             'Lập ngay hai đường truyền tĩnh mạch truyền dung dịch Natri Clorid 0,9% kết hợp Glucose '
                             '5% hồi sức chống sốc mất muối, tiêm tĩnh mạch Hydrocortisone liều tấn công.',
                             'Làm xét nghiệm khẩn cấp 17-OHP huyết thanh, điện giải đồ Na+ K+ Cl-, khí máu động mạch, '
                             'chỉ định Fludrocortisone đường uống và bổ sung muối ăn NaCl hàng ngày.',
                             'Làm nhiễm sắc thể đồ karyotype xác định giới tính di truyền 46,XX hay 46,XY, siêu âm ổ '
                             'bụng tử cung buồng trứng hoặc tìm tinh hoàn lạc chỗ, duy trì liệu pháp glucocorticoid.',
                             'Bù dịch điều chỉnh hạ natri và tăng kali máu nặng, theo dõi điện tâm đồ liên tục đề '
                             'phòng loạn nhịp tim do tăng kali máu, hội chẩn Nội tiết Nhi khoa điều trị duy trì.',
                             'Tư vấn di truyền cho bố mẹ, hướng dẫn gia đình nhận biết dấu hiệu cơn suy thượng thận '
                             'cấp và cách tiêm bắp hydrocortisone cấp cứu tại nhà khi trẻ sốt cao hoặc nhiễm trùng.'],
    'bien_the_kham': [   'Cơ quan sinh dục ngoài phì đại âm vật kiểu Prader 3, tăng sắc tố da rõ rệt ở vùng bìu bẹn và '
                         'quầng vú, mạch nhanh nhỏ khó bắt, dấu véo da mất chậm do mất nước.',
                         'Trẻ li bì mắt trũng sâu, sạm da sẫm quanh núm vú và nếp lằn cổ bẹn, bộ phận sinh dục ngoài '
                         'lưỡng giới giả âm vật phì đại trông như dương vật nhỏ, không sờ thấy tinh hoàn.',
                         'Bé trai có da vùng bìu sẫm màu nâu đen đậm, nắn thấy hai tinh hoàn trong bìu, dấu hiệu mất '
                         'nước nặng: thóp trũng véo da nếp gấp bụng đàn hồi kém, huyết áp kẹp.',
                         'Khám thấy hạ huyết áp tư thế, nhịp tim nhanh 160 l/p, da sạm màu chì tập trung các nếp gấp, '
                         'phì đại củ âm vật kèm dính môi lớn tạo xoang niệu dục chung.',
                         'Dấu hiệu suy vỏ thượng thận cấp: trẻ mệt lả đầu chi mát lạnh, sạm da toàn thân, sinh dục '
                         'ngoài phân kỳ bất thường chưa rõ giới tính giải phẫu.',
                         'Trẻ nôn nhiều sút cân gầy gò, da sạm màu đồng vùng cơ quan sinh dục ngoài, mạch quay yếu khó '
                         'bắt, bụng mềm chướng hơi nhẹ.'],
    'chan_doan': 'Tăng sản thượng thận bẩm sinh thể mất muối thiếu hụt enzym 21-hydroxylase.',
    'chinh': [   'bộ phận sinh dục ngoài biến đổi mơ hồ phì đại âm vật ở bé gái hoặc tăng sắc tố sẫm màu bìu ở bé trai',
                 'nôn trớ nhiều kèm sụt cân nhanh không rõ nguyên nhân',
                 'mất nước sụt cân li bì hạ huyết áp trong những tuần đầu'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nội tiết - chuyển hoá',
    'ke_hoach': 'Xét nghiệm cấp cứu điện giải đồ, 17-hydroxyprogesterone, cortisol máu, bù dịch điện giải khẩn cấp '
                'bằng dung dịch mặn đẳng trương pha glucose, bổ sung Hydrocortisone và Fludrocortisone.',
    'kham': 'Cơ quan sinh dục ngoài phì đại âm vật kiểu Prader 3, tăng sắc tố da rõ rệt ở vùng bìu bẹn và quầng vú, '
            'mạch nhanh nhỏ khó bắt, dấu véo da mất chậm do mất nước.',
    'nhom': 'nhi',
    'phu': [   'trẻ bú kém thường xuyên ọc sữa kèm thở nhanh nông',
               'da sạm đen vùng nếp gấp bẹn quanh hậu môn và quầng ngực',
               'rối loạn điện giải natri máu hạ thấp và kali máu tăng vọt'],
    'ten': 'tăng sản thượng thận bẩm sinh'},
    {   'bien_the_chan_doan': [   'Còi xương do thiếu vitamin D thể hoạt động giai đoạn tiến triển.',
                              'Còi xương do thiếu vitamin D có biến dạng lồng ngực và sọ não.',
                              'Còi xương dinh dưỡng ở trẻ nhỏ giai đoạn cấp.',
                              'Theo dõi còi xương do thiếu vitamin D biến chứng chậm phát triển vận động.',
                              'Còi xương thiếu vitamin D thể hồi phục bắt đầu canxi hoá xương.',
                              'Còi xương dinh dưỡng mức độ trung bình có giảm trương lực cơ.'],
    'bien_the_ke_hoach': [   'Định lượng 25(OH) vitamin D máu, canxi và phospho huyết thanh, chụp X-quang xương cổ '
                             'tay, bổ sung Vitamin D3 liều điều trị 2000-5000 IU/ngày trong 6-8 tuần kết hợp canxi '
                             'sinh học.',
                             'Xét nghiệm sinh hóa định lượng 25-hydroxyvitamin D3, phosphatase kiềm tăng cao, chụp '
                             'X-quang đầu dưới xương cẳng tay thấy đầu xương bè rộng đáy lõm hình chén.',
                             'Uống Vitamin D3 liều 2.000 IU/ngày liên tục trong 8 tuần kèm canxi nguyên tố 500mg/ngày, '
                             'sau đó chuyển sang liều dự phòng 400 IU/ngày duy trì.',
                             'Tư vấn gia đình cho trẻ tắm nắng đúng cách buổi sớm trước 8 giờ sáng, cải thiện chế độ '
                             'ăn dặm giàu canxi từ tôm cua cá trứng sữa chua.',
                             'Bổ sung canxi corbiere dạng ống uống kết hợp cholecalciferol giọt hàng ngày, hẹn kiểm '
                             'tra lại canxi máu và 25(OH)D sau 2 tháng điều trị.',
                             'Chỉ định liều cao Vitamin D3 một liều duy nhất 100.000 IU đường uống cho trẻ kém tuân '
                             'thủ uống hàng ngày, theo dõi sát nồng độ canxi niệu đề phòng ngộ độc.'],
    'bien_the_kham': [   'Thóp trước rộng 3x3 cm bờ mềm nhuyễn sọ vùng chẩm, chuỗi hạt sườn hai bên lồng ngực rõ, vòng '
                         'cổ tay phình to (vòng cổ tay còi xương), rụng tóc vành khăn sau chẩm.',
                         'Khám đầu thấy bướu trán bướu đỉnh nhô gồ (đầu hộp), vùng chẩm ấn vào có cảm giác mềm lún như '
                         'bóng bàn (dấu nhuyễn sọ), rụng tóc sau gáy tạo vệt trắng rộng.',
                         'Lồng ngực biến dạng hình ức gà nhẹ, rãnh Harrison hằn sâu dọc hai bên bờ sườn, đầu dưới '
                         'xương quay và xương trụ phình to như chuỗi hạt cườm.',
                         'Trẻ 14 tháng chưa biết tự đi, hai chân vòng kiềng cong hình chữ O rõ rệt, trương lực cơ toàn '
                         'thân nhẽo mềm, thóp trước vẫn mở rộng 2x2cm.',
                         'Trẻ có biểu hiện chuỗi hạt sườn sờ rất rõ hai bên ngực, răng mới mọc 2 chiếc men răng xấu '
                         'lởm chởm, mồ hôi trộm ướt đẫm vùng lưng gáy khi ngủ.',
                         'Khám hệ cơ xương thấy khớp cổ chân cổ tay bè rộng, cơ bụng nhão trướng bè sang hai bên hình '
                         'bụng ếch, phản xạ gân xương bình thường.'],
    'chan_doan': 'Còi xương do thiếu vitamin D thể hoạt động giai đoạn tiến triển.',
    'chinh': [   'trẻ quấy khóc đêm hay giật mình đổ mồ hôi trộm nhiều vùng đầu gáy',
                 'rụng tóc hình vành khăn sau gáy rõ rệt',
                 'thóp rộng chậm liền bờ thóp mềm nhuyễn sọ'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'dinh dưỡng',
    'ke_hoach': 'Định lượng 25(OH) vitamin D máu, canxi và phospho huyết thanh, chụp X-quang xương cổ tay, bổ sung '
                'Vitamin D3 liều điều trị 2000-5000 IU/ngày trong 6-8 tuần kết hợp canxi sinh học.',
    'kham': 'Thóp trước rộng 3x3 cm bờ mềm nhuyễn sọ vùng chẩm, chuỗi hạt sườn hai bên lồng ngực rõ, vòng cổ tay phình '
            'to (vòng cổ tay còi xương), rụng tóc vành khăn sau chẩm.',
    'nhom': 'nhi',
    'phu': [   'chậm mọc răng chậm biết lẫy bò đứng đi so với chuẩn tuổi',
               'chuỗi hạt sườn nổi gồ dọc khớp sụn sườn lồng ngực',
               'biến dạng xương chân vòng kiềng chữ O hoặc chữ X khi tập đi'],
    'ten': 'còi xương do thiếu vitamin D'},
    {   'bien_the_chan_doan': [   'Bệnh celiac ở trẻ em thể điển hình kém hấp thu.',
                              'Theo dõi bệnh celiac ở trẻ em thể tiêu hoá khởi phát sau cai sữa ăn dặm.',
                              'Bệnh celiac ở trẻ nhỏ gây suy dinh dưỡng gầy còm và thiếu máu thiếu sắt mạn.',
                              'Bệnh nhạy cảm với gluten thể cổ điển có tổn thương niêm mạc ruột non.',
                              'Theo dõi bệnh celiac ở trẻ có tiền sử gia đình mắc bệnh tự miễn.',
                              'Bệnh celiac biến chứng kém hấp thu đa chất dinh dưỡng và còi xương thứ phát.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm kháng thể kháng mô transglutaminase IgA, tổng lượng IgA máu, nội soi tá '
                             'tràng sinh thiết niêm mạc ruột non, thiết lập chế độ ăn kiêng hoàn toàn gluten suốt đời.',
                             'Xét nghiệm định lượng kháng thể Anti-tTG IgA và Anti-Endomysial IgA (EMA), công thức '
                             'máu, sắt huyết thanh ferritin, tư vấn chế độ ăn loại bỏ hoàn toàn lúa mì lúa mạch.',
                             'Chỉ định nội soi thực quản dạ dày tá tràng bấm sinh thiết bóng tá tràng gửi giải phẫu '
                             'bệnh phân loại tổn thương theo Marsh-Oberhuber khẳng định chẩn đoán.',
                             'Bổ sung sắt đường uống, acid folic, kẽm và vitamin tổng hợp bù đắp thiếu hụt dinh dưỡng, '
                             'hướng dẫn mẹ đọc nhãn thực phẩm tìm sản phẩm dán nhãn Gluten-Free.',
                             'Chuyển chuyên khoa Dinh dưỡng lâm sàng lên thực đơn ăn dặm không chứa gluten từ bột gạo '
                             'ngô khoai sắn, theo dõi sự phục hồi cân nặng và kháng thể sau 6 tháng.',
                             'Làm xét nghiệm kháng thể kháng deamidated gliadin peptide (DGP), tầm soát bệnh tuyến '
                             'giáp và đái tháo đường típ 1 đi kèm ở trẻ mắc celiac.'],
    'bien_the_kham': [   'Thể trạng suy kiệt gầy mòn, cơ mông teo nhăn nheo hình túi da, bụng trướng căng mềm không '
                         'điểm đau khu trú, niêm mạc mắt nhợt nhẹ.',
                         'Trẻ gầy teo cơ rõ ở gốc chi bắp tay bắp đùi, bụng to bè như bụng cóc gõ vang khắp bụng, da '
                         'khô bong tróc vảy nhỏ rải rác.',
                         'Khám dấu hiệu thiếu máu mạn: niêm mạc mắt và vòm miệng nhạt màu, móng tay dẹt dễ gãy, cơ '
                         'mông teo nhăn nheo chảy xệ.',
                         'Thể trạng còi cọc chiều cao cân nặng dưới đường bách phân vị thứ 3, bụng chướng to tĩnh mạch '
                         'nông nổi rõ, khám bụng không sờ thấy u cục.',
                         'Trẻ quấy khóc cáu kỉnh khi thăm khám, lớp mỡ dưới da bụng và đùi mỏng dính, phân quan sát '
                         'thấy nhiều mỡ váng bốc mùi hôi chua nồng nặc.',
                         'Suy dinh dưỡng thể teo đét phối hợp thiếu vi chất dinh dưỡng, cơ thể gầy guộc đối lập với '
                         'bụng căng tròn đầy hơi, tim phổi chưa thấy bất thường.'],
    'chan_doan': 'Bệnh celiac ở trẻ em thể điển hình kém hấp thu.',
    'chinh': [   'tiêu chảy mạn tính phân nhiều bã nhờn lổn nhổn bóng nhờn bốc mùi chua nồng sau khi ăn dặm đồ bột',
                 'bụng trướng to căng bóng tương phản với chân tay teo tóp khẳng khiu',
                 'chậm tăng cân suy dinh dưỡng gầy sút rõ rệt'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Làm xét nghiệm kháng thể kháng mô transglutaminase IgA, tổng lượng IgA máu, nội soi tá tràng sinh '
                'thiết niêm mạc ruột non, thiết lập chế độ ăn kiêng hoàn toàn gluten suốt đời.',
    'kham': 'Thể trạng suy kiệt gầy mòn, cơ mông teo nhăn nheo hình túi da, bụng trướng căng mềm không điểm đau khu '
            'trú, niêm mạc mắt nhợt nhẹ.',
    'nhom': 'nhi',
    'phu': [   'trẻ thường xuyên khó chịu bứt rứt thay đổi tính khí dễ cáu gắt',
               'nôn trớ thức ăn tái diễn biếng ăn kéo dài',
               'thiếu máu da xanh xao niêm mạc nhợt nhạt do kém hấp thu sắt'],
    'ten': 'bệnh celiac ở trẻ em'},
    {   'bien_the_chan_doan': [   'Xuất huyết giảm tiểu cầu miễn dịch nguyên phát ở trẻ em mức độ vừa.',
                              'Xuất huyết giảm tiểu cầu miễn dịch cấp tính ở trẻ em sau nhiễm virus.',
                              'Theo dõi xuất huyết giảm tiểu cầu miễn dịch có xuất huyết niêm mạc miệng nguy cơ cao.',
                              'Xuất huyết giảm tiểu cầu nguyên phát ở trẻ nhỏ đáp ứng tốt với globulin miễn dịch.',
                              'Xuất huyết giảm tiểu cầu miễn dịch mới chẩn đoán mức độ nặng tiểu cầu dưới 10 G/L.',
                              'Theo dõi xuất huyết giảm tiểu cầu tự miễn cần chẩn đoán phân biệt với bạch cầu cấp.'],
    'bien_the_ke_hoach': [   'Xét nghiệm tổng phân tích tế bào máu ngoại vi đo số lượng tiểu cầu, đông máu toàn bộ, '
                             'phết máu ngoại biên loại trừ ác tính, theo dõi sát nếu tiểu cầu trên 30 G/L hoặc truyền '
                             'IVIG nếu có xuất huyết niêm mạc.',
                             'Làm công thức máu khẩn đếm số lượng tiểu cầu bằng máy và soi kính hiển vi, làm đông máu '
                             'cơ bản PT aPTT Fibrinogen, cho trẻ nằm bất động hạn chế va đập mạnh.',
                             'Chỉ định truyền tĩnh mạch Immunoglobulin (IVIG) liều 0,8-1 g/kg một liều duy nhất khi '
                             'tiểu cầu dưới 20 G/L kèm chảy máu niêm mạc tiến triển.',
                             'Dùng Corticosteroid đường uống Prednisolone liều 2-4 mg/kg/ngày ngắn ngày trong 4-7 '
                             'ngày, hướng dẫn phụ huynh tránh dùng các thuốc hạ sốt nhóm NSAID như ibuprofen.',
                             'Chỉ định tủy đồ nếu tiểu cầu không tăng sau điều trị hoặc kèm sốt thiếu máu gan lách to '
                             'bất thường, cảnh báo dấu hiệu nguy hiểm đau đầu nôn vọt đề phòng xuất huyết não.',
                             'Theo dõi số lượng tiểu cầu mỗi 48-72 giờ đến khi ổn định trên 50 G/L, hướng dẫn chăm sóc '
                             'chải răng bằng gạc mềm và tránh tiêm bắp tiêm dưới da.'],
    'bien_the_kham': [   'Chấm xuất huyết và mảng bầm tím rải rác toàn thân kích thước từ đầu ghim đến vài cm, niêm '
                         'mạc má có nốt phỏng máu, gan lách và hạch ngoại biên không to.',
                         'Khắp cẳng tay cẳng chân và ngực bụng có vô số nốt chấm xuất huyết màu đỏ tươi xen lẫn tím '
                         'thẫm không biến mất khi ấn kính, niêm mạc miệng có bọng xuất huyết nhỏ.',
                         'Khám thấy chảy máu rỉ rả từ khe chân răng hàm dưới, các mảng bầm tím xuất hiện tự phát hai '
                         'bên đùi và mông, hạch cổ nách bẹn không sờ chạm, lách không to.',
                         'Trẻ tỉnh táo tiếp xúc tốt, da niêm hồng hào, nốt xuất huyết dạng chấm rải rác tập trung ở '
                         'vùng tỳ đè hai cẳng chân, không có dấu hiệu thần kinh khu trú.',
                         'Xuất huyết dưới da đa hình thái từ dạng điểm chấm đến mảng đụng dập lớn ở hai cẳng tay, ấn '
                         'kính không mất màu, họng sạch không sung huyết.',
                         'Khám toàn diện không thấy dấu hiệu vàng da xuất huyết kết mạc mắt, gan lách bình thường '
                         'không to, ban xuất huyết phân bố không đều khắp hai bên cơ thể.'],
    'chan_doan': 'Xuất huyết giảm tiểu cầu miễn dịch nguyên phát ở trẻ em mức độ vừa.',
    'chinh': [   'xuất hiện nhiều chấm nốt ban xuất huyết dưới da đa hình thái đa lứa tuổi đột ngột',
                 'chảy máu chân răng tự nhiên hoặc chảy máu mũi rỉ rả khó cầm',
                 'các mảng bầm tím xuất hiện tự nhiên sau va chạm rất nhẹ'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'huyết học',
    'ke_hoach': 'Xét nghiệm tổng phân tích tế bào máu ngoại vi đo số lượng tiểu cầu, đông máu toàn bộ, phết máu ngoại '
                'biên loại trừ ác tính, theo dõi sát nếu tiểu cầu trên 30 G/L hoặc truyền IVIG nếu có xuất huyết niêm '
                'mạc.',
    'kham': 'Chấm xuất huyết và mảng bầm tím rải rác toàn thân kích thước từ đầu ghim đến vài cm, niêm mạc má có nốt '
            'phỏng máu, gan lách và hạch ngoại biên không to.',
    'nhom': 'nhi',
    'phu': [   'tiền sử nhiễm siêu vi đường hô hấp hoặc sốt phát ban 1-3 tuần trước',
               'trẻ không sốt thể trạng chung vẫn tỉnh táo chơi ngoan',
               'nước tiểu hơi hồng hoặc phân có vệt máu khi niêm mạc xuất huyết nặng'],
    'ten': 'xuất huyết giảm tiểu cầu miễn dịch nhi'},
    {   'bien_the_chan_doan': [   'Viêm màng não mủ ở trẻ em giai đoạn cấp tính chưa biến chứng.',
                              'Theo dõi viêm màng não mủ do phế cầu khuẩn Streptococcus pneumoniae.',
                              'Viêm màng não mủ ở trẻ nhỏ biến chứng co giật sốt cao.',
                              'Theo dõi viêm màng não mủ do vi khuẩn Hib ở trẻ chưa tiêm phòng đầy đủ.',
                              'Viêm màng não mủ tối cấp có hội chứng tăng áp lực nội sọ.',
                              'Viêm màng não mủ do não mô cầu Neisseria meningitidis nghi ngờ thể bùng phát.'],
    'bien_the_ke_hoach': [   'Chỉ định chọc dò dịch não tủy cấp cứu xét nghiệm sinh hóa vi sinh tế bào, cấy máu, dùng '
                             'ngay kháng sinh tĩnh mạch liều cao Ceftriaxone kết hợp Vancomycin và Dexamethasone.',
                             'Khẩn trương chọc dò tủy sống đo áp lực và xét nghiệm dịch não tủy tế bào vi trùng sinh '
                             'hóa đường đạm, cấy máu hai vị trí, dùng ngay kháng sinh tĩnh mạch không chờ kết quả '
                             'dịch.',
                             'Nhập khoa Hồi sức cấp cứu Nhi, tiêm tĩnh mạch Dexamethasone 0,15 mg/kg trước hoặc cùng '
                             'lúc với liều kháng sinh đầu Ceftriaxone 100 mg/kg/ngày chia 2 lần.',
                             'Đặt đường truyền tĩnh mạch trung tâm, chống phù não bằng Mannitol 20% liều 0,5 g/kg '
                             'truyền nhanh nếu có dấu hiệu tăng áp lực nội sọ, hạ sốt tích cực.',
                             'Theo dõi tri giác thang điểm Coma Glasgow nhi khoa mỗi 2 giờ, chụp CT sọ não cấp cứu nếu '
                             'nghi ngờ có khối choán chỗ hoặc tụ dịch dưới màng cứng.',
                             'Điều trị hỗ trợ hô hấp duy trì SpO2 trên 95%, cắt cơn co giật bằng Diazepam tiêm tĩnh '
                             'mạch chậm hoặc bơm hậu môn khi xuất hiện co giật.'],
    'bien_the_kham': [   'Trẻ li bì kích thích, hội chứng màng não dương tính rõ với gáy cứng, dấu hiệu Kernig và '
                         'Brudzinski dương tính, thóp căng phồng, đồng tử phản xạ ánh sáng tốt.',
                         'Khám dấu gáy cứng rõ rệt nâng đầu không gập được cằm vào ngực, dấu Brudzinski trên dương '
                         'tính khi gập cổ hai chân co gập, thóp trước phồng căng đập yếu.',
                         'Trẻ sốt cao 39,5 độ C, nằm co quắp tư thế cò súng sợ ánh sáng và tiếng động, dấu hiệu Kernig '
                         'góc dưới 135 độ gây đau, vẻ mặt nhiễm trùng nhiễm độc nặng.',
                         'Trẻ nhũ nhi li bì khó đánh thức, thóp trước phồng căng đo chu vi vòng đầu tăng nhanh, trương '
                         'lực cơ tăng nhẹ, ánh mắt nhìn sững định thần.',
                         'Hội chứng kích thích màng não dương tính: gáy cứng 3 khoát ngón tay, vạch màng não dương '
                         'tính rõ rệt, thở không đều có cơn ngưng thở ngắn.',
                         'Khám thấy dấu thần kinh khu trú âm tính, đồng tử hai bên đều 2,5mm đáp ứng tốt với ánh sáng, '
                         'gáy cứng rõ kèm quấy khóc thét chói tai khi chạm vào người.'],
    'chan_doan': 'Viêm màng não mủ ở trẻ em giai đoạn cấp tính chưa biến chứng.',
    'chinh': [   'sốt cao liên tục kèm rét run đáp ứng kém với thuốc hạ sốt thông thường',
                 'nôn vọt không liên quan đến bữa ăn tái diễn nhiều lần',
                 'đau đầu dữ dội quấy khóc ôm đầu hoặc li bì mê sảng khó đánh thức'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Chỉ định chọc dò dịch não tủy cấp cứu xét nghiệm sinh hóa vi sinh tế bào, cấy máu, dùng ngay kháng '
                'sinh tĩnh mạch liều cao Ceftriaxone kết hợp Vancomycin và Dexamethasone.',
    'kham': 'Trẻ li bì kích thích, hội chứng màng não dương tính rõ với gáy cứng, dấu hiệu Kernig và Brudzinski dương '
            'tính, thóp căng phồng, đồng tử phản xạ ánh sáng tốt.',
    'nhom': 'nhi',
    'phu': [   'dấu hiệu cứng gáy cổ cứng sợ ánh sáng chói',
               'thóp trước phồng căng ở trẻ nhũ nhi',
               'co giật toàn thân hoặc co giật cục bộ thoáng qua'],
    'ten': 'viêm màng não mủ ở trẻ em'},
    {   'bien_the_chan_doan': [   'Viêm mô tế bào trước vách hốc mắt ở trẻ em do biến chứng viêm xoang.',
                              'Viêm mô tế bào trước vách ổ mắt ở trẻ nhỏ sau chấn thương xây xước da mi.',
                              'Theo dõi viêm mô tế bào quanh hốc mắt phân biệt với viêm tổ chức hốc mắt sau vách.',
                              'Viêm mô tế bào trước vách hốc mắt cấp tính nghi do tụ cầu vàng Staphylococcus aureus.',
                              'Viêm mô mềm quanh ổ mắt ở trẻ em biến chứng từ nhiễm trùng răng hàm mặt.',
                              'Viêm mô tế bào quanh mắt mức độ trung bình đáp ứng điều trị nội khoa.'],
    'bien_the_ke_hoach': [   'Chụp CT hốc mắt và xoang có tiêm cản quang để phân biệt viêm sau vách, cấy dịch mũi mủ, '
                             'nhập viện dùng kháng sinh tĩnh mạch Amoxicillin-Clavulanate hoặc Ceftriaxone, nhỏ mắt '
                             'kháng sinh và chườm ấm.',
                             'Chỉ định chụp cắt lớp vi tính CT scan sọ não hốc mắt để loại trừ áp xe dưới màng xương '
                             'hốc mắt, dùng kháng sinh Ceftriaxone phối hợp Oxacillin đường tĩnh mạch.',
                             'Nhập viện khoa Mắt Nhi theo dõi sát thị lực và phản xạ ánh sáng mỗi 4-6 giờ đề phòng '
                             'nhiễm trùng lan vào khoang sau vách gây mù lòa, nhỏ dung dịch Tobramycin 0,3%.',
                             'Lấy dịch tiết mi mắt làm xét nghiệm soi tươi nhuộm Gram và nuôi cấy vi khuẩn định danh '
                             'làm kháng sinh đồ, dùng thuốc giảm đau hạ sốt paracetamol đường uống.',
                             'Hội chẩn chuyên khoa Tai Mũi Họng kiểm tra nội soi xoang hút sạch mủ hốc mũi, dùng thuốc '
                             'co mạch nhỏ mũi Otrivin 0,05% trong 3 ngày để dẫn lưu xoang.',
                             'Theo dõi sát dấu hiệu lồi mắt giới hạn vận nhãn hoặc giảm thị lực để can thiệp phẫu '
                             'thuật dẫn lưu mủ kịp thời nếu chuyển dạng viêm mô tế bào sau vách.'],
    'bien_the_kham': [   'Mi mắt trên và dưới bên phải phù nề đỏ tấy căng bóng, ấn đau chói quanh bờ mi, vận nhãn các '
                         'hướng bình thường không đau khi liếc mắt, phản xạ đồng tử bình thường.',
                         'Mi mắt sưng mọng đỏ ửng lan rộng lên cung mày và gò má cùng bên, khe mi hẹp chỉ hé mở nhẹ, '
                         'kết mạc cương tụ đỏ nhẹ nhưng không phù gai thị hay phù nề kết mạc (chemosis).',
                         'Quan sát thấy mắt trái mở to bình thường còn mắt phải nhắm tịt do mi nề đỏ căng bóng, ấn nhẹ '
                         'góc trong mắt trẻ kêu đau gạt tay bác sĩ, vận động nhãn cầu đủ tầm.',
                         'Phù nề mi mắt mức độ nặng lan toả trước vách ngăn hốc mắt, nhiệt độ da tại chỗ nóng hơn bên '
                         'đối diện rõ rệt, thị lực định tính hai mắt tương đương nhau.',
                         'Khám mắt thấy bờ mi tấy đỏ có vảy mủ khô dính góc mắt, không có dấu lồi mắt (proptosis), soi '
                         'đáy mắt hai bên mạch máu và gai thị bình thường.',
                         'Sưng nề tấy đỏ vùng mô mềm trước cung mi mắt, hạch góc hàm cùng bên sưng đau kích thước 1cm '
                         'di động, tai mũi họng có niêm mạc cuốn mũi dưới phù nề xuất tiết mủ.'],
    'chan_doan': 'Viêm mô tế bào trước vách hốc mắt ở trẻ em do biến chứng viêm xoang.',
    'chinh': [   'mi mắt sưng đỏ nóng húp phù nề không mở được khe mi một bên',
                 'sốt vừa đến sốt cao kèm quấy khóc nhiều',
                 'vùng da quanh hốc mắt đỏ ửng căng tức khi chạm vào'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'mắt',
    'ke_hoach': 'Chụp CT hốc mắt và xoang có tiêm cản quang để phân biệt viêm sau vách, cấy dịch mũi mủ, nhập viện '
                'dùng kháng sinh tĩnh mạch Amoxicillin-Clavulanate hoặc Ceftriaxone, nhỏ mắt kháng sinh và chườm ấm.',
    'kham': 'Mi mắt trên và dưới bên phải phù nề đỏ tấy căng bóng, ấn đau chói quanh bờ mi, vận nhãn các hướng bình '
            'thường không đau khi liếc mắt, phản xạ đồng tử bình thường.',
    'nhom': 'nhi',
    'phu': [   'tiền sử viêm xoang sàng xoang hàm hoặc vết xước nhỏ vùng trán mặt',
               'chảy nước mắt nhiều rỉ mắt đặc dính',
               'thị lực và vận nhãn còn bảo tồn nhãn cầu không bị đẩy lồi'],
    'ten': 'viêm mô tế bào quanh hốc mắt trẻ'},
    {   'bien_the_chan_doan': [   'Hẹp phì đại môn vị bẩm sinh ở trẻ nhũ nhi.',
                              'Theo dõi hẹp phì đại môn vị có rối loạn kiềm chuyển hoá giảm clo máu.',
                              'Hẹp phì đại môn vị ở trẻ sơ sinh 4 tuần tuổi thể điển hình.',
                              'Hẹp phì đại môn vị ở trẻ bú mẹ có mất nước và suy dinh dưỡng cấp.',
                              'Theo dõi hẹp phì đại môn vị cần phân biệt với trào ngược dạ dày thực quản nặng.',
                              'Hẹp phì đại môn vị giai đoạn sớm chưa biến chứng kiềm chuyển hoá.'],
    'bien_the_ke_hoach': [   'Siêu âm dạ dày môn vị đo độ dày cơ môn vị và chiều dài ống môn vị, xét nghiệm điện giải '
                             'đồ và khí máu đánh giá kiềm chuyển hóa hạ clo, bù dịch điện giải trước khi phẫu thuật mở '
                             'cơ môn vị ngoài niêm mạc.',
                             'Chỉ định siêu âm đường tiêu hoá trên xác định độ dày cơ môn vị trên 3mm và chiều dài ống '
                             'môn vị trên 15mm, đặt ống thông dạ dày hút sạch dịch ứ đọng.',
                             'Xét nghiệm sinh hóa máu ion đồ Na+ K+ Cl-, khí máu thăng bằng kiềm toan, truyền dịch bù '
                             'nước điện giải Natri Clorid 0,9% pha Kali Clorid điều chỉnh kiềm chuyển hoá trước phẫu '
                             'thuật.',
                             'Ngừng cho trẻ bú đường miệng, hội chẩn khoa Ngoại Nhi chuẩn bị phẫu thuật mở cơ môn vị '
                             'ngoài niêm mạc theo phương pháp Ramstedt qua nội soi ổ bụng.',
                             'Hồi sức dịch tích cực trong 24 giờ để đưa nồng độ Clo và kiềm dư về giới hạn bình thường '
                             'đảm bảo an toàn gây mê hồi sức, sau đó tiến hành phẫu thuật.',
                             'Chăm sóc hậu phẫu cho trẻ tập bú lại sữa mẹ từng lượng nhỏ sau mổ 12-24 giờ, theo dõi '
                             'nôn trớ và tốc độ tăng trưởng cân nặng xuất viện sau 48 giờ.'],
    'bien_the_kham': [   'Trẻ gầy hốc hác dấu hiệu mất nước nhẹ, thấy rõ sóng nhu động dạ dày nổi gồ ở thượng vị sau '
                         'bú, sờ thấy khối u môn vị hình quả trám ở hạ sườn phải.',
                         'Khám lúc trẻ nằm yên bú chút nước đường thấy sóng nhu động dạ dày dâng lên từng đợt chạy từ '
                         'trái qua phải thượng vị, nắn hạ sườn phải thấy u môn vị chắc bằng đầu ngón tay cái.',
                         'Trẻ thể trạng teo tóp mặt nhăn nheo như ông già, mắt trũng sâu, sờ sâu dưới bờ gan tìm thấy '
                         'khối u cơ môn vị hình quả ô-liu mật độ chắc di động nhẹ.',
                         'Dấu hiệu mất nước trung bình: da khô véo da mất chậm, thóp trước trũng nhẹ, bụng trên chướng '
                         'căng tương phản với bụng dưới lõm lòng thuyền.',
                         'Khám bụng mềm hoàn toàn, sau khi nôn hết dịch dạ dày sờ nắn thấy khối u tròn chắc đường kính '
                         '1,5cm ở góc hạ sườn phải trên rốn.',
                         'Trẻ quấy khóc đòi bú liên tục, cơ thể gầy sút rõ rệt, nắn bụng thấy khối cơ môn vị phì đại '
                         'đặc trưng (olive sign), nghe nhu động dạ dày tăng âm sắc.'],
    'chan_doan': 'Hẹp phì đại môn vị bẩm sinh ở trẻ nhũ nhi.',
    'chinh': [   'nôn vọt thành tia dữ dội ngay sau khi bú xong trong tuần thứ 3 đến 6 sau sinh',
                 'chất nôn là sữa chua vón cục hoàn toàn không có dịch mật màu xanh vàng',
                 'trẻ háu đói đòi bú lại liên tục ngay sau khi nôn xong'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Siêu âm dạ dày môn vị đo độ dày cơ môn vị và chiều dài ống môn vị, xét nghiệm điện giải đồ và khí máu '
                'đánh giá kiềm chuyển hóa hạ clo, bù dịch điện giải trước khi phẫu thuật mở cơ môn vị ngoài niêm mạc.',
    'kham': 'Trẻ gầy hốc hác dấu hiệu mất nước nhẹ, thấy rõ sóng nhu động dạ dày nổi gồ ở thượng vị sau bú, sờ thấy '
            'khối u môn vị hình quả trám ở hạ sườn phải.',
    'nhom': 'nhi',
    'phu': [   'sút cân hoặc đứng cân kéo dài da nhăn nheo mất nước',
               'đi tiểu ít tã khô và phân táo bón ít ỏi',
               'nhìn thấy sóng nhu động dạ dày chạy từ hạ sườn trái sang phải'],
    'ten': 'hẹp phì đại môn vị ở trẻ nhũ nhi'},
    {   'bien_the_chan_doan': [   'Bướu máu sơ sinh thể nông vùng má đang trong giai đoạn tăng sinh.',
                              'Bướu máu sơ sinh thể hỗn hợp có nguy cơ loét và biến dạng thẩm mỹ.',
                              'Bướu máu tế bào nội mô mạch máu ở trẻ nhũ nhi giai đoạn phát triển nhanh.',
                              'Theo dõi bướu máu sơ sinh quanh mắt đe dọa trục thị giác gây nhược thị.',
                              'Bướu máu sơ sinh thể phẳng bắt đầu chuyển dạng gồ dâu tây.',
                              'Bướu máu trẻ em lành tính đang trong chu kỳ tăng sinh tự nhiên.'],
    'bien_the_ke_hoach': [   'Chỉ định siêu âm Doppler màu mạch máu đánh giá độ sâu và dòng chảy, điều trị nội khoa '
                             'bước một bằng Propranolol đường uống liều 2-3 mg/kg/ngày chia 2 lần dưới sự theo dõi '
                             'nhịp tim huyết áp.',
                             'Siêu âm mạch máu ổ bụng và gan tầm soát u máu nội tạng đa ổ, làm điện tâm đồ kiểm tra '
                             'đoạn PR và nhịp tim trước khi khởi đầu điều trị chẹn beta giao cảm.',
                             'Chỉ định Propranolol uống khởi đầu liều 1 mg/kg/ngày tăng dần lên 2 mg/kg/ngày sau 1 '
                             'tuần, theo dõi đường huyết và nhịp tim tại phòng khám chuyên khoa.',
                             'Bôi tại chỗ dung dịch Timolol 0,5% nhỏ giọt ngày 2 lần cho các bướu máu nông kích thước '
                             'nhỏ ngoài vùng mắt, hẹn tái khám đánh giá đáp ứng sau 4 tuần.',
                             'Hướng dẫn phụ huynh vệ sinh da nhẹ nhàng tránh cọ xát gây rỉ máu, cách xử trí băng ép vô '
                             'khuẩn tại nhà nếu bướu bị xước rách chảy máu.',
                             'Hội chẩn chuyên khoa Da liễu Nhi và Mắt Nhi nếu bướu nằm sát mi mắt gây che khuất đồng '
                             'tử, cân nhắc can thiệp laser xung nhuộm màu khi có loét trợt.'],
    'bien_the_kham': [   'Khối u mạch máu gồ cao trên bề mặt da kích thước 2x3cm màu đỏ tươi dạng quả dâu tây vùng má '
                         'phải, sờ mềm ấm không có tiếng thổi, bờ rõ không thâm nhiễm mô sâu.',
                         'Tổn thương da gồ màu đỏ thẫm như chùm dâu tây đường kính 25mm ở vùng trán trên cung mày '
                         'trái, ấn xẹp một phần thả tay phồng lại nhanh, không loét hoại tử.',
                         'Bướu mạch máu thể hỗn hợp nông sâu vùng cẳng tay, bề mặt đỏ tím gồ nhẹ kèm khối dưới da mật '
                         'độ mềm ấn không đau, nghe không thấy rung miu hay âm thổi.',
                         'Khám thấy khối đỏ tươi viền không đều kích thước 15x20mm ở môi trên, làm biến dạng nhẹ viền '
                         'môi nhưng trẻ bú mút bình thường, không rỉ máu.',
                         'Khối gồ dạng dâu tây vùng chẩm da đầu, tóc vùng tổn thương thưa thớt, sờ mềm đàn hồi tốt '
                         'không đập theo nhịp mạch, ấn kính đổi sang màu nhạt hơn.',
                         'Bướu máu kích thước tăng gấp đôi sau 2 tháng, bề mặt đỏ tươi căng bóng không trầy xước, tổ '
                         'chức xung quanh không sưng phù không có hạch vùng to.'],
    'chan_doan': 'Bướu máu sơ sinh thể nông vùng má đang trong giai đoạn tăng sinh.',
    'chinh': [   'dát màu đỏ hoặc gồ đỏ tươi như quả dâu tây trên da xuất hiện vài tuần sau sinh',
                 'tổn thương lớn dần nhanh chóng về kích thước và độ gồ trong những tháng đầu',
                 'bề mặt đỏ thẫm ấm nhẹ ấn kính đổi màu một phần'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Chỉ định siêu âm Doppler màu mạch máu đánh giá độ sâu và dòng chảy, điều trị nội khoa bước một bằng '
                'Propranolol đường uống liều 2-3 mg/kg/ngày chia 2 lần dưới sự theo dõi nhịp tim huyết áp.',
    'kham': 'Khối u mạch máu gồ cao trên bề mặt da kích thước 2x3cm màu đỏ tươi dạng quả dâu tây vùng má phải, sờ mềm '
            'ấm không có tiếng thổi, bờ rõ không thâm nhiễm mô sâu.',
    'nhom': 'nhi',
    'phu': [   'vị trí thường gặp ở vùng đầu mặt cổ hoặc thân mình',
               'nguy cơ loét trợt rỉ máu hoặc bội nhiễm vi khuẩn khi cọ xát tã lót',
               'có thể ảnh hưởng tầm nhìn thở hoặc bú nếu nằm gần mắt mũi miệng'],
    'ten': 'bướu máu sơ sinh'},
    {   'bien_the_chan_doan': [   'Bất sản da bẩm sinh vùng da đầu thể đơn độc nhóm 1.',
                              'Bất sản da bẩm sinh da đầu không kèm khuyết xương sọ.',
                              'Theo dõi bất sản da bẩm sinh nghi ngờ có khuyết xương vòm sọ đi kèm.',
                              'Bất sản da bẩm sinh thể sẹo teo da đầu phát hiện sau sinh.',
                              'Khuyết da đầu bẩm sinh đơn thuần chưa có biến chứng nhiễm trùng.',
                              'Bất sản da bẩm sinh nhóm Adams-Oliver cần tầm soát dị tật chi phối hợp.'],
    'bien_the_ke_hoach': [   'Chụp X-quang hoặc siêu âm sọ não qua thóp đánh giá khuyết xương và màng não bên dưới, '
                             'chăm sóc tại chỗ vô khuẩn bôi mỡ kháng sinh và băng gạc ẩm chờ biểu mô hóa tự nhiên.',
                             'Chỉ định siêu âm phần mềm da đầu và vòm sọ loại trừ xoang tĩnh mạch màng cứng bất '
                             'thường, rửa vết thương bằng nước muối sinh lý bôi mỡ Sulfadiazine bạc 1%.',
                             'Chụp MRI sọ não có cản quang nếu tổn thương lớn trên 3cm hoặc nghi ngờ thoát vị màng '
                             'não, theo dõi sát đề phòng biến chứng viêm màng não và rò dịch não tủy.',
                             'Băng vô trùng bảo vệ ổ khuyết da tránh sang chấn tỳ đè, hướng dẫn mẹ theo dõi dấu hiệu '
                             'sưng nóng đỏ chảy mủ của nhiễm trùng thứ phát.',
                             'Hội chẩn phẫu thuật tạo hình nhi khoa lên phương pháp ghép da hoặc chuyển vạt da đầu khi '
                             'trẻ lớn nếu diện tích khuyết da rộng không tự liền sẹo được.',
                             'Khám toàn diện loại trừ các dị tật bẩm sinh đi kèm ở ngón tay ngón chân tim mạch và mắt '
                             'theo phân loại Frieden.'],
    'bien_the_kham': [   'Vùng đỉnh da đầu có một ổ khuyết da tròn đường kính 2cm ranh giới rõ, đáy phủ màng mỏng bán '
                         'trong suốt nhìn thấy mô liên kết dưới da, không rỉ mủ, xương sọ bên dưới còn nguyên vẹn.',
                         'Tổn thương mất thượng bì và trung bì da đầu hình bầu dục kích thước 15x25mm tại đỉnh chẩm, '
                         'đáy có lớp vảy tiết khô màu nâu nhạt, sờ nắn nhẹ bản xương sọ bên dưới phẳng chắc.',
                         'Ổ khuyết da đơn độc đường kính 1,5cm vùng đỉnh đầu, xung quanh viền tóc mọc xoắn đặc trưng, '
                         'đáy phẳng màu hồng nhạt sạch không chảy máu, không có khối thoát vị màng não.',
                         'Khám da đầu trẻ sơ sinh phát hiện vết loét teo da tròn đường kính 10mm, đáy nhẵn bóng như '
                         'sẹo mỏng, ranh giới rõ ràng với vùng da đầu có tóc bình thường.',
                         'Khuyết da đầu kích thước 2x2cm bờ sắc gọn, sờ không thấy khiếm khuyết xương vòm sọ, không có '
                         'mạch máu bất thường đập dưới đáy tổn thương.',
                         'Trẻ sơ sinh có vết trợt da bẩm sinh vùng đỉnh, quan sát đáy là màng mỏng trơn láng, không '
                         'sưng đỏ mô xung quanh, thóp trước cách tổn thương 3cm mềm phẳng.'],
    'chan_doan': 'Bất sản da bẩm sinh vùng da đầu thể đơn độc nhóm 1.',
    'chinh': [   'khuyết hổng da bẩm sinh ranh giới rõ ràng có ngay từ lúc mới sinh',
                 'vị trí tổn thương điển hình ở vùng đỉnh đầu đường giữa da đầu',
                 'vùng tổn thương trơ trụi mất toàn bộ lớp da không có nang tóc chân tóc'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'da liễu',
    'ke_hoach': 'Chụp X-quang hoặc siêu âm sọ não qua thóp đánh giá khuyết xương và màng não bên dưới, chăm sóc tại '
                'chỗ vô khuẩn bôi mỡ kháng sinh và băng gạc ẩm chờ biểu mô hóa tự nhiên.',
    'kham': 'Vùng đỉnh da đầu có một ổ khuyết da tròn đường kính 2cm ranh giới rõ, đáy phủ màng mỏng bán trong suốt '
            'nhìn thấy mô liên kết dưới da, không rỉ mủ, xương sọ bên dưới còn nguyên vẹn.',
    'nhom': 'nhi',
    'phu': [   'đáy tổn thương là màng mỏng trong suốt hoặc mô hạt màu đỏ tươi',
               'kích thước từ vài milimet đến vài centimet hình tròn hoặc bầu dục',
               'nguy cơ rỉ dịch tiết hoặc rỉ máu nhẹ khi va chạm cọ xát'],
    'ten': 'bất sản da bẩm sinh'},
    {   'bien_the_chan_doan': [   'Hội chứng thận hư tiên phát ở trẻ em thể tổn thương tối thiểu đợt đầu.',
                              'Hội chứng thận hư tiên phát ở trẻ em thể nhạy cảm hoàn toàn với corticoid.',
                              'Theo dõi hội chứng thận hư đợt bùng phát đầu tiên chưa biến chứng nhiễm trùng.',
                              'Hội chứng thận hư tiên phát ở trẻ nhỏ có tràn dịch đa màng.',
                              'Hội chứng thận hư đợt tái phát thường xuyên sau giảm liều steroid.',
                              'Hội chứng thận hư tiên phát ở trẻ lứa tuổi nhà trẻ có protein niệu chọn lọc cao.'],
    'bien_the_ke_hoach': [   'Xét nghiệm tổng phân tích nước tiểu đo protein niệu 24 giờ, định lượng albumin máu và '
                             'lipid máu toàn phần, điều trị tấn công bằng Prednisolone liều chuẩn 2 mg/kg/ngày trong '
                             '4-6 tuần kết hợp hạn chế muối.',
                             'Làm xét nghiệm tỷ lệ Protein/Creatinine nước tiểu mẫu sáng sớm (uPCR), định lượng '
                             'Albumin máu dưới 25 g/L, Cholesterol máu toàn phần tăng cao khẳng định hội chứng thận '
                             'hư.',
                             'Chỉ định dùng Prednisone hoặc Prednisolone liều 60 mg/m2/ngày hoặc 2 mg/kg/ngày uống '
                             'buổi sáng sau ăn, theo dõi que nhúng protein niệu tại nhà hàng ngày.',
                             'Truyền Albumin 20% liều 0,5-1 g/kg phối hợp Furosemide tĩnh mạch chậm khi có phù nặng đe '
                             'dọa chèn ép suy hô hấp hoặc phù bìu căng tức loét da.',
                             'Tư vấn chế độ ăn lạt giảm muối tuyệt đối trong giai đoạn phù nề, bổ sung canxi và '
                             'vitamin D dự phòng tác dụng phụ loãng xương do dùng corticoid kéo dài.',
                             'Tầm soát biến chứng tắc mạch và viêm phúc mạc tiên phát, tiêm phòng phế cầu và thủy đậu '
                             'sau khi ngừng thuốc corticoid theo phác đồ hướng dẫn.'],
    'bien_the_kham': [   'Phù mềm trắng ấn lõm hai mi mắt hai cẳng chân và mu bàn chân, bụng chướng báng mức độ vừa gõ '
                         'đục vùng thấp, tiếng tim đều rõ, phổi thông khí tốt.',
                         'Toàn thân phù rõ hai mắt híp lại do mi mắt mọng nước, da bụng căng bóng nổi mạch máu nông '
                         'mờ, khám thấy dấu hiệu sóng vỗ dương tính nhẹ, huyết áp bình thường.',
                         'Trẻ tăng 3kg trong vòng một tuần, phù nhiều vùng bìu và hai chi dưới ấn lõm lâu hồi phục, '
                         'nghe phổi đáy hai bên thông khí hơi giảm nhẹ do tràn dịch màng phổi ít.',
                         'Dấu hiệu phù kiểu thận: mặt tròn mi mắt nặng trĩu vào buổi sáng, phù trắng đối xứng cẳng '
                         'chân mu chân, nước tiểu thu thập được trong bô sủi bọt trắng đục như xà phòng.',
                         'Khám thấy phù toàn thân kèm cổ trướng tự do mức độ trung bình, nhịp tim đều 105 l/p, không '
                         'có dấu hiệu suy tim ứ huyết, gan mấp mé bờ sườn.',
                         'Phù trắng mềm ấn lõm sâu từ đùi xuống mắt cá chân hai bên, bìu sưng to căng bóng da trong '
                         'suốt, trẻ nằm mệt không muốn vận động.'],
    'chan_doan': 'Hội chứng thận hư tiên phát ở trẻ em thể tổn thương tối thiểu đợt đầu.',
    'chinh': [   'phù toàn thân xuất hiện đầu tiên ở mi mắt vào buổi sáng rồi lan xuống hai chân và bụng',
                 'tiểu ít rõ rệt nước tiểu sẫm màu có nhiều bọt lâu tan',
                 'tăng cân nhanh bất thường do ứ dịch trong cơ thể'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thận - tiết niệu',
    'ke_hoach': 'Xét nghiệm tổng phân tích nước tiểu đo protein niệu 24 giờ, định lượng albumin máu và lipid máu toàn '
                'phần, điều trị tấn công bằng Prednisolone liều chuẩn 2 mg/kg/ngày trong 4-6 tuần kết hợp hạn chế '
                'muối.',
    'kham': 'Phù mềm trắng ấn lõm hai mi mắt hai cẳng chân và mu bàn chân, bụng chướng báng mức độ vừa gõ đục vùng '
            'thấp, tiếng tim đều rõ, phổi thông khí tốt.',
    'nhom': 'nhi',
    'phu': [   'bụng trướng to do dịch cổ trướng màng bụng',
               'trẻ mệt mỏi ăn uống kém chán ăn bỏ chơi',
               'da trắng bệch nhợt nhạt căng bóng ấn lõm rõ rệt'],
    'ten': 'hội chứng thận hư tiên phát ở trẻ em'},
    {   'bien_the_chan_doan': [   'Viêm mao mạch dị ứng Schonlein-Henoch ở trẻ em thể da khớp tiêu hoá.',
                              'Viêm mao mạch Henoch-Schonlein có tổn thương thận biểu hiện đái máu vi thể.',
                              'Viêm mạch IgA Schonlein-Henoch ở trẻ nhỏ thể tiêu hoá cấp tính.',
                              'Theo dõi viêm mao mạch Schonlein-Henoch có biến chứng lồng ruột cấp.',
                              'Viêm mao mạch dị ứng thể da khớp đơn thuần đáp ứng tốt với giảm đau.',
                              'Viêm mạch lắng đọng IgA ở trẻ em sau đợt viêm đường hô hấp cấp.'],
    'bien_the_ke_hoach': [   'Làm tổng phân tích tế bào máu, đông máu cơ bản, tổng phân tích nước tiểu tìm hồng cầu và '
                             'đạm niệu, nghỉ ngơi tại giường, giảm đau bằng Paracetamol, dùng Corticoid ngắn ngày nếu '
                             'có đau bụng dữ dội.',
                             'Xét nghiệm công thức máu số lượng tiểu cầu hoàn toàn bình thường để loại trừ xuất huyết '
                             'giảm tiểu cầu, làm xét nghiệm cặn lắng nước tiểu mỗi tuần trong tháng đầu.',
                             'Chỉ định dùng Methylprednisolone hoặc Prednisolone liều 1-2 mg/kg/ngày trong 1-2 tuần '
                             'khi trẻ có đau bụng quặn dữ dội hoặc xuất huyết tiêu hoá do phù nề thành ruột.',
                             'Cho trẻ nằm nghỉ ngơi bất động tương đối tại giường nâng cao hai chân giúp giảm phù nề '
                             'chi dưới, dùng Paracetamol giảm đau khớp định kỳ.',
                             'Siêu âm ổ bụng kiểm tra Doppler mạch mạc treo và thành ruột nhằm phát hiện sớm biến '
                             'chứng lồng ruột thứ phát ở hồi tràng.',
                             'Theo dõi chức năng thận đo huyết áp và xét nghiệm nước tiểu định kỳ hàng tháng trong 6 '
                             'tháng liên tục để phát hiện kịp thời viêm cầu thận Schonlein-Henoch.'],
    'bien_the_kham': [   'Ban xuất huyết dạng sẩn hoại tử nhỏ gồ nhẹ trên mặt da không mất khi ấn kính, tập trung dày '
                         'đặc đối xứng ở hai cẳng chân và mông, hai khớp cổ chân sưng nề ấn đau.',
                         'Khám da thấy sẩn ban xuất huyết dạng chấm tròn màu đỏ tía nhô gồ sờ ram ráp ngón tay, phân '
                         'bố dày đặc từ mông xuống mặt sau đùi và quanh mắt cá hai bên.',
                         'Khớp gối và cổ chân hai bên sưng phù nóng nhẹ không đỏ bầm, biên độ vận động khớp thụ động '
                         'bị hạn chế do trẻ kêu đau khóc thét khi cử động.',
                         'Bụng mềm ấn đau nhẹ vùng quanh rốn không có phản ứng thành bụng, siêu âm loại trừ lồng ruột '
                         'thứ phát do tụ máu thành ruột, ban da phân bố đối xứng điển hình.',
                         'Sẩn xuất huyết gồ gờ dạng bản đồ tập trung nhiều ở mặt duỗi hai cẳng chân, tiểu cầu bình '
                         'thường, thăm trực tràng không thấy máu đại thể.',
                         'Trẻ đi khập khiễng do đau khớp cổ chân, khám thấy phù mu bàn chân kèm ban xuất huyết tím sẫm '
                         'hình đĩa đồng xu rải rác từ mu chân lên cẳng chân.'],
    'chan_doan': 'Viêm mao mạch dị ứng Schonlein-Henoch ở trẻ em thể da khớp tiêu hoá.',
    'chinh': [   'ban xuất huyết dạng sẩn gồ gờ trên mặt da phân bố đối xứng hai cẳng chân và mông',
                 'đau sưng các khớp lớn như cổ chân khớp gối gây hạn chế đi lại',
                 'đau bụng từng cơn quanh rốn kèm nôn ói hoặc đi ngoài phân có máu'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'miễn dịch - dị ứng',
    'ke_hoach': 'Làm tổng phân tích tế bào máu, đông máu cơ bản, tổng phân tích nước tiểu tìm hồng cầu và đạm niệu, '
                'nghỉ ngơi tại giường, giảm đau bằng Paracetamol, dùng Corticoid ngắn ngày nếu có đau bụng dữ dội.',
    'kham': 'Ban xuất huyết dạng sẩn hoại tử nhỏ gồ nhẹ trên mặt da không mất khi ấn kính, tập trung dày đặc đối xứng '
            'ở hai cẳng chân và mông, hai khớp cổ chân sưng nề ấn đau.',
    'nhom': 'nhi',
    'phu': [   'tiền sử nhiễm trùng đường hô hấp trên 1-2 tuần trước khi phát ban',
               'trẻ sốt nhẹ hoặc không sốt mệt mỏi quấy khóc do đau khớp',
               'tiểu ra máu vi thể hoặc protein niệu nhẹ do tổn thương thận'],
    'ten': 'viêm mao mạch dị ứng Schonlein-Henoch ở trẻ'},
    {   'bien_the_chan_doan': [   'Hội chứng West co thắt nhũ nhi có thoái lui phát triển tâm thần vận động.',
                              'Hội chứng West căn nguyên triệu chứng sau bệnh não thiếu oxy thiếu máu chu sinh.',
                              'Co thắt nhũ nhi động kinh hội chứng West thể nguyên phát vô căn.',
                              'Hội chứng West ở trẻ có tổn thương xơ cứng củ Bourneville.',
                              'Động kinh co thắt nhũ nhi giai đoạn tiến triển có điện não loạn nhịp cao thế.',
                              'Hội chứng West kháng trị cần phối hợp thuốc chống động kinh thế hệ mới.'],
    'bien_the_ke_hoach': [   'Đo điện não đồ video giấc ngủ EEG tìm hình ảnh loạn nhịp cao điện thế đặc trưng, chụp '
                             'cộng hưởng từ MRI sọ não tìm nguyên nhân cấu trúc, điều trị bước một bằng ACTH tiêm bắp '
                             'hoặc Vigabatrin đường uống.',
                             'Chỉ định ghi điện não đồ liên tục ít nhất 1 giờ ghi nhận chu kỳ ngủ thức để tìm sóng '
                             'Hypsarrhythmia, chụp MRI sọ não từ lực 1.5 Tesla khảo sát vỏ não.',
                             'Bắt đầu điều trị bằng hormone vỏ thượng thận tổng hợp Synacthen (ACTH) tiêm bắp liều cao '
                             'trong 2 tuần rồi giảm liều dần theo dõi huyết áp và điện giải.',
                             'Lựa chọn Vigabatrin (Sabril) dạng gói bột pha uống liều 50-150 mg/kg/ngày đặc biệt khi '
                             'trẻ có căn nguyên bệnh xơ cứng củ, kiểm tra thị trường định kỳ.',
                             'Hội chẩn chuyên khoa Thần kinh Nhi lập kế hoạch can thiệp phục hồi chức năng sớm, bổ '
                             'sung Pyridoxine (Vitamin B6) liều cao loại trừ co giật phụ thuộc B6.',
                             'Hướng dẫn gia đình ghi hình video các cơn giật bằng điện thoại để bác sĩ đối chiếu lâm '
                             'sàng, theo dõi tái khám điện não đồ sau 14 ngày dùng thuốc.'],
    'bien_the_kham': [   'Trẻ 6 tháng tuổi chậm lẫy mắt không dõi theo đồ chơi, ghi nhận cơn co thắt gập đầu gập thân '
                         'khép hai tay nhanh 1-2 giây rồi thả lỏng lặp lại 15 lần trong 3 phút, phản xạ gân xương tăng '
                         'nhẹ.',
                         'Quan sát trực tiếp thấy chuỗi cơn co thắt gập người: đầu chúi gập vào ngực hai tay dang rộng '
                         'rồi ôm chéo trước ngực hai chân co gấp lên bụng diễn ra chớp nhoáng 1 giây.',
                         'Trẻ giảm giao tiếp mắt vẻ mặt vô hồn không cười đáp ứng mẹ, trương lực cơ trục thân giảm đầu '
                         'còn ngửa ra sau khi kéo ngồi, thóp trước phẳng.',
                         'Chuỗi cơn co giật 20 nhịp liên tục mỗi nhịp cách nhau 5-10 giây kèm tiếng khóc thét ngắn '
                         'cuối mỗi nhịp giật, đồng tử co nhỏ thoáng qua trong cơn.',
                         'Khám thần kinh trẻ nhũ nhi thấy phản xạ nắm tay và phản xạ Moro còn tồn tại bất thường ở '
                         'tháng thứ 7, cơ bắp nhẽo mềm ít cử động tự phát.',
                         'Trẻ có biểu hiện co thắt thể duỗi: ngửa cổ cong lưng hai tay giạng thẳng hai chân duỗi cứng '
                         'xuất hiện thành chùm sau khi thức giấc.'],
    'chan_doan': 'Hội chứng West co thắt nhũ nhi có thoái lui phát triển tâm thần vận động.',
    'chinh': [   'các cơn co thắt cơ đột ngột gập người về phía trước hoặc ưỡn người ra sau xảy ra thành chuỗi hàng '
                 'chục cơn liên tiếp',
                 'cơn co giật thường xuất hiện ngay lúc trẻ vừa thức giấc hoặc sắp ngủ',
                 'chững lại hoặc thoái lui các mốc phát triển tâm thần vận động mất nụ cười xã hội'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Đo điện não đồ video giấc ngủ EEG tìm hình ảnh loạn nhịp cao điện thế đặc trưng, chụp cộng hưởng từ '
                'MRI sọ não tìm nguyên nhân cấu trúc, điều trị bước một bằng ACTH tiêm bắp hoặc Vigabatrin đường uống.',
    'kham': 'Trẻ 6 tháng tuổi chậm lẫy mắt không dõi theo đồ chơi, ghi nhận cơn co thắt gập đầu gập thân khép hai tay '
            'nhanh 1-2 giây rồi thả lỏng lặp lại 15 lần trong 3 phút, phản xạ gân xương tăng nhẹ.',
    'nhom': 'nhi',
    'phu': [   'trẻ quấy khóc thét chói tai trước hoặc sau chuỗi cơn co thắt',
               'mắt trợn ngược hoặc giật nhãn cầu thoáng qua trong cơn giật',
               'trương lực cơ toàn thân giảm mềm nhẽo giữa các cơn'],
    'ten': 'hội chứng West co thắt nhũ nhi'},
    {   'bien_the_chan_doan': [   'Bại não thể co cứng hai chi dưới ở trẻ em do tiền sử sinh non.',
                              'Bại não thể co cứng tứ chi mức độ nặng theo phân loại chức năng vận động GMFCS độ 4.',
                              'Bại não thể liệt nửa người co cứng sau di chứng xuất huyết não sơ sinh.',
                              'Theo dõi bại não thể co cứng kèm chậm phát triển ngôn ngữ và rối loạn nuốt.',
                              'Bại não thể co cứng hai bên có co rút gân gót biến dạng bàn chân thuổng.',
                              'Bại não thể liệt cứng nhẹ có khả năng đi lại độc lập với dụng cụ trợ giúp.'],
    'bien_the_ke_hoach': [   'Chụp MRI sọ não đánh giá nhuyễn hóa chất trắng quanh não thất, xây dựng chương trình can '
                             'thiệp phục hồi chức năng vật lý trị liệu sớm, nẹp chỉnh hình và thuốc giãn cơ Baclofen '
                             'đường uống nếu co cứng nặng.',
                             'Lập kế hoạch tập vật lý trị liệu phục hồi chức năng vận động định kỳ kéo giãn cơ ức đòn '
                             'chũm gân gót và nhóm cơ khép háng, hướng dẫn mẹ tư thế bế ẵm đúng.',
                             'Chỉ định mang nẹp chỉnh hình cổ bàn chân AFO (Ankle-Foot Orthosis) ban ngày và ban đêm '
                             'để phòng ngừa biến dạng co rút gân gót kiễng chân.',
                             'Cân nhắc tiêm độc tố Botulinum toxin type A (Botox) vào các nhóm cơ co cứng bắp chân '
                             'hoặc cơ khép háng nhằm giảm trương lực cơ cục bộ hỗ trợ tập vận động.',
                             'Chụp X-quang khớp háng tư thế thẳng định kỳ mỗi 6-12 tháng để phát hiện sớm bán trật '
                             'khớp háng do co cứng cơ khép, chuyển phẫu thuật chỉnh hình khi có chỉ định.',
                             'Điều trị hỗ trợ ngôn ngữ trị liệu và can thiệp dinh dưỡng qua sonde nếu rối loạn nuốt '
                             'nặng, bổ sung canxi và vitamin D chống loãng xương do giảm vận động.'],
    'bien_the_kham': [   'Trương lực cơ tứ chi tăng kiểu co cứng tháp, phản xạ gân xương bánh chè tăng nhạy có rung '
                         'giật bàn chân (clonus), dấu Babinski hai bên dương tính, hai chân duỗi khép chéo nhau kiểu '
                         'cắt kéo.',
                         'Khám vận động thấy độ gập góc khép háng hẹp dưới 60 độ, gân gót co rút khiến bàn chân kiễng '
                         'gót ngón chân quắp, nhấc nách trẻ thấy hai chân bắt chéo bắt chéo hình kéo.',
                         'Dấu hiệu dao gấp dương tính rõ ở khớp khuỷu và khớp gối khi cử động thụ động, phản xạ gân '
                         'xương tứ chi tăng mạnh lan toả kèm rung giật xương bánh chè.',
                         'Trẻ 2 tuổi chưa tự ngồi thăng bằng được do lưng cong gập thân mình co cứng, hai tay gập khép '
                         'ngón cái khép chặt vào lòng bàn tay (ngón cái nằm trong lòng bàn tay).',
                         'Khám miệng họng thấy cử động lưỡi vụng về rối loạn vận động miệng gây chảy dãi liên tục, '
                         'phản xạ nôn tăng nhạy, trí tuệ tiếp xúc nhận biết được mẹ.',
                         'Co cứng ưu thế hai chi dưới nhiều hơn hai chi trên (thể co cứng hai chi dưới), cột sống cong '
                         'vẹo tư thế, phản xạ trương lực cổ không đối xứng còn tồn tại.'],
    'chan_doan': 'Bại não thể co cứng hai chi dưới ở trẻ em do tiền sử sinh non.',
    'chinh': [   'tăng trương lực cơ kiểu co cứng làm các chi co cứng kháng cự lại cử động thụ động',
                 'chậm đạt rõ rệt các mốc phát triển vận động như chậm kiểm soát đầu cổ lẫy ngồi bò đi',
                 'tư thế bất thường hai chân bắt chéo kiểu lưỡi kéo khi nhấc bổng trẻ lên'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chụp MRI sọ não đánh giá nhuyễn hóa chất trắng quanh não thất, xây dựng chương trình can thiệp phục '
                'hồi chức năng vật lý trị liệu sớm, nẹp chỉnh hình và thuốc giãn cơ Baclofen đường uống nếu co cứng '
                'nặng.',
    'kham': 'Trương lực cơ tứ chi tăng kiểu co cứng tháp, phản xạ gân xương bánh chè tăng nhạy có rung giật bàn chân '
            '(clonus), dấu Babinski hai bên dương tính, hai chân duỗi khép chéo nhau kiểu cắt kéo.',
    'nhom': 'nhi',
    'phu': [   'tiền sử sinh non nhẹ cân ngạt chu sinh hoặc vàng da nhân não',
               'phản xạ nguyên phát sơ sinh tồn tại dai dẳng quá tuổi biến mất',
               'khó khăn trong việc bú nuốt chảy nước dãi thường xuyên'],
    'ten': 'bại não thể co cứng'},
    {   'bien_the_chan_doan': [   'Xơ nang tụy thể phối hợp hô hấp và tiêu hoá có suy tụy ngoại tiết.',
                              'Bệnh xơ nang tụy biến chứng giãn phế quản bội nhiễm trực khuẩn mủ xanh.',
                              'Xơ nang tụy ở trẻ nhỏ phát hiện sớm qua biểu hiện tắc ruột phân su sơ sinh.',
                              'Theo dõi bệnh xơ nang CFTR có suy dinh dưỡng nặng và kém hấp thu mỡ.',
                              'Xơ nang tụy đợt cấp nhiễm trùng đường hô hấp dưới do Pseudomonas aeruginosa.',
                              'Bệnh xơ nang di truyền lặn NST thường thể nhẹ ưu thế biểu hiện hô hấp.'],
    'bien_the_ke_hoach': [   'Thực hiện nghiệm pháp đo clo mồ hôi bằng phương pháp điện di pilocarpine, xét nghiệm '
                             'phân tích đột biến gen CFTR, bổ sung men tụy Pancreatin uống trước bữa ăn và vỗ rung '
                             'lồng ngực hàng ngày.',
                             'Làm test mồ hôi xác định nồng độ Clo trên 60 mmol/L khẳng định chẩn đoán, cấy đờm tìm vi '
                             'khuẩn định danh mủ xanh và tụ cầu, chụp CT ngực độ phân giải cao HRCT.',
                             'Chỉ định uống enzyme tụy vi nang kháng acid (Creon) liều chuẩn theo lượng mỡ bữa ăn ngay '
                             'trước khi ăn, bổ sung các vitamin tan trong dầu A D E K dạng nước.',
                             'Điều trị phục hồi chức năng hô hấp bằng kỹ thuật dẫn lưu tư thế kết hợp khí dung nước '
                             'muối ưu trương 3-7% và dornase alfa làm loãng đờm đặc.',
                             'Dùng kháng sinh hít khí dung Tobramycin chu kỳ 28 ngày hoặc kháng sinh tĩnh mạch liều '
                             'cao khi có đợt cấp bùng phát nhiễm trùng hô hấp.',
                             'Tư vấn chế độ ăn giàu calo giàu chất béo 120-150% nhu cầu khuyến nghị, bổ sung thêm muối '
                             'ăn NaCl vào thức ăn hàng ngày đặc biệt trong mùa nóng.'],
    'bien_the_kham': [   'Thể trạng gầy còm lồng ngực hình thùng, nghe phổi có ran ẩm rải rác và rít thì thở ra hai '
                         'phế trường, ngón tay hình dùi trống độ 2, khám bụng mềm chướng hơi nhẹ.',
                         'Khám hô hấp thấy lồng ngực căng phồng đường kính trước sau tăng, thở co kéo cơ liên sườn '
                         'nhẹ, nghe phổi đầy ran nổ nhỏ hạt và ran ẩm khắp hai bên phế trường.',
                         'Trẻ gầy trơ xương sườn bụng to bè phân bóng mỡ dính bết đáy bỉm, đầu ngón tay khum tròn mặt '
                         'kính đồng hồ hình dùi trống, SpO2 94% khí trời.',
                         'Khám mũi xoang thấy niêm mạc mũi nhợt nhạt có nhiều khối polyp mềm thòng xuống ngách mũi '
                         'giữa hai bên, ho khạc ra cục đờm xanh đặc quánh dính chặt.',
                         'Trẻ còi cọc chiều cao cân nặng dưới ngưỡng -2SD, da khô bong vảy, mồ hôi vùng trán nếm thấy '
                         'vị mặn rõ rệt, gan mấp mé 2cm dưới sườn phải.',
                         'Khám phổi thấy thông khí giảm hai bên đáy kèm ran rít ran ngáy rải rác, nhịp thở 36 l/p, các '
                         'mốc phát triển thể chất chậm 1 năm so với tuổi.'],
    'chan_doan': 'Xơ nang tụy thể phối hợp hô hấp và tiêu hoá có suy tụy ngoại tiết.',
    'chinh': [   'ho mạn tính đờm đặc quánh dai dẳng kèm thở khò khè nhiễm trùng phổi tái diễn',
                 'tiêu chảy mạn tính phân mỡ váng bốc mùi hôi thối do suy tụy ngoại tiết',
                 'chậm tăng cân suy dinh dưỡng dù trẻ ăn rất nhiều và háu đói'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'hô hấp',
    'ke_hoach': 'Thực hiện nghiệm pháp đo clo mồ hôi bằng phương pháp điện di pilocarpine, xét nghiệm phân tích đột '
                'biến gen CFTR, bổ sung men tụy Pancreatin uống trước bữa ăn và vỗ rung lồng ngực hàng ngày.',
    'kham': 'Thể trạng gầy còm lồng ngực hình thùng, nghe phổi có ran ẩm rải rác và rít thì thở ra hai phế trường, '
            'ngón tay hình dùi trống độ 2, khám bụng mềm chướng hơi nhẹ.',
    'nhom': 'nhi',
    'phu': [   'vị mồ hôi mặn chát bất thường khi cha mẹ hôn lên trán trẻ',
               'ngón tay ngón chân dùi trống do thiếu oxy mạn tính',
               'polyp mũi hoặc viêm xoang mạn tính tái phát sớm ở trẻ nhỏ'],
    'ten': 'xơ nang tụy'},
    {   'bien_the_chan_doan': [   'Hội chứng Down thể thuần trisomy 21 nghi kèm dị tật tim bẩm sinh.',
                              'Hội chứng Down trisomy 21 tự do có thông liên thất phần quanh màng.',
                              'Theo dõi hội chứng Down thể khảm với biểu hiện lâm sàng nhẹ hơn.',
                              'Hội chứng Down ở trẻ sơ sinh có hẹp tá tràng bẩm sinh phối hợp.',
                              'Hội chứng Down có suy giáp bẩm sinh thứ phát cần điều trị hormone.',
                              'Hội chứng Down trisomy 21 chuyển đoạn cần làm di truyền học cho cha mẹ.'],
    'bien_the_ke_hoach': [   'Làm nhiễm sắc thể đồ Karyotype tế bào lympho máu ngoại vi khẳng định chẩn đoán, siêu âm '
                             'tim Doppler màu tầm soát tật kênh nhĩ thất hoặc thông liên thất, kiểm tra chức năng '
                             'tuyến giáp và thính lực định kỳ.',
                             'Chỉ định siêu âm tim qua thành ngực khảo sát dị tật kênh nhĩ thất toàn bộ hoặc thông '
                             'liên nhĩ lỗ tiên phát, chụp X-quang bụng loại trừ hẹp tá tràng hình bóng đôi.',
                             'Làm xét nghiệm định lượng TSH và FT4 tầm soát suy giáp bẩm sinh định kỳ lúc 6 tháng và '
                             '12 tháng tuổi, kiểm tra công thức máu loại trừ phản ứng giả bạch cầu.',
                             'Đo thính lực phản ứng thân não ABR và khám mắt khúc xạ đáy mắt tầm soát đục thủy tinh '
                             'thể bẩm sinh, lập hồ sơ quản lý sức khỏe trẻ em Down.',
                             'Tư vấn di truyền cho bố mẹ nguy cơ tái mắc ở lần mang thai sau, giới thiệu tham gia nhóm '
                             'hỗ trợ can thiệp sớm vật lý trị liệu và giáo dục đặc biệt.',
                             'Chụp X-quang cột sống cổ tư thế gập duỗi sau 3 tuổi tầm soát mất vững khớp đội - trục '
                             '(atlantoaxial instability) trước khi tham gia các hoạt động thể thao.'],
    'bien_the_kham': [   'Mặt dẹt rãnh mắt xếch nếp da góc mắt trong, lưỡi to rãnh nứt nhô ra ngoài cung răng, trương '
                         'lực cơ nhão mềm nâng trẻ lên đầu rủ ra sau, bàn tay ngắn có nếp hằn ngang duy nhất, nghe tim '
                         'có tiếng thổi tâm thu 3/6 ở bờ trái xương ức.',
                         'Đầu nhỏ chẩm phẳng, hai mắt cách xa nhau khe mắt xếch lên trên ra ngoài có nếp quạt '
                         'epicanthus, trương lực cơ giảm rõ rệt gập khớp háng sát thành ngực không cản trở.',
                         'Bàn tay ngắn dày ngón út ngắn cong vào trong (clinodactyly), nếp gấp đơn độc lòng bàn tay rõ '
                         'rệt ở cả hai bên, bàn chân có rãnh sâu rộng giữa ngón chân 1 và ngón chân 2.',
                         'Khám trẻ sơ sinh thấy da thừa vùng gáy dày cộm, miệng nhỏ vòm hầu cao hẹp khiến lưỡi luôn '
                         'thè ra ngoài mép, nhịp tim đều nghe tiếng T2 mạnh ở đáy tim.',
                         'Trẻ 1 tuổi chưa ngồi vững trương lực cơ nhão cơ bụng mềm trướng nhẹ, cổ ngắn ngực hơi lõm, '
                         'nghe tim có tiếng thổi tâm thu dạng tống máu ở khoang liên sườn 2-3 trái.',
                         'Vẻ mặt Down điển hình dễ nhận diện, khớp lỏng lẻo biên độ vận động khớp thụ động vượt quá '
                         'giới hạn bình thường, phản xạ gân xương giảm đồng đều.'],
    'chan_doan': 'Hội chứng Down thể thuần trisomy 21 nghi kèm dị tật tim bẩm sinh.',
    'chinh': [   'khuôn mặt đặc trưng với mắt xếch góc mắt có nếp quạt gốc mũi tẹt miệng nhỏ lưỡi thè ra',
                 'trương lực cơ toàn thân giảm nhẽo mềm rõ rệt từ lúc mới sinh',
                 'chậm phát triển tâm thần vận động và ngôn ngữ so với trẻ cùng trang lứa'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Làm nhiễm sắc thể đồ Karyotype tế bào lympho máu ngoại vi khẳng định chẩn đoán, siêu âm tim Doppler '
                'màu tầm soát tật kênh nhĩ thất hoặc thông liên thất, kiểm tra chức năng tuyến giáp và thính lực định '
                'kỳ.',
    'kham': 'Mặt dẹt rãnh mắt xếch nếp da góc mắt trong, lưỡi to rãnh nứt nhô ra ngoài cung răng, trương lực cơ nhão '
            'mềm nâng trẻ lên đầu rủ ra sau, bàn tay ngắn có nếp hằn ngang duy nhất, nghe tim có tiếng thổi tâm thu '
            '3/6 ở bờ trái xương ức.',
    'nhom': 'nhi',
    'phu': [   'rãnh khỉ một đường chỉ tay ngang duy nhất trong lòng bàn tay',
               'tai nhỏ vành tai đóng thấp gập mép',
               'nguy cơ cao mắc dị tật tim bẩm sinh như thông liên thất hoặc kênh nhĩ thất'],
    'ten': 'hội chứng Down'},
    {   'bien_the_chan_doan': [   'Chậm phát triển tâm thần vận động mức độ trung bình chưa rõ căn nguyên.',
                              'Chậm phát triển toàn diện ở trẻ dưới 5 tuổi theo tiêu chuẩn DSM-5.',
                              'Theo dõi chậm phát triển tâm thần vận động nghi do di chứng thiếu máu não chu sinh.',
                              'Chậm phát triển nhận thức và vận động phối hợp tật đầu nhỏ.',
                              'Chậm phát triển tâm thần vận động liên quan hội chứng di truyền nhiễm sắc thể.',
                              'Chậm phát triển vận động và ngôn ngữ mức độ nhẹ đáp ứng tốt với can thiệp sớm.'],
    'bien_the_ke_hoach': [   'Đánh giá mức độ phát triển theo thang điểm Denver II hoặc Bayley III, chụp MRI sọ não, '
                             'làm xét nghiệm sàng lọc rối loạn chuyển hóa bẩm sinh và nhiễm sắc thể, chỉ định can '
                             'thiệp sớm đa chuyên khoa tâm lý vận động và ngôn ngữ trị liệu.',
                             'Đo thính lực đồ khách quan ABR và khám thị giác loại trừ suy giảm giác quan nguyên phát, '
                             'chỉ định chụp cộng hưởng từ MRI sọ não khảo sát quá trình myelin hoá chất trắng.',
                             'Làm xét nghiệm sàng lọc di truyền microarray lai so sánh bộ gen (aCGH) và xét nghiệm '
                             'sàng lọc axit amin axit hữu cơ máu nước tiểu phát hiện bệnh chuyển hoá.',
                             'Lập phác đồ can thiệp kích thích phát triển sớm bao gồm vật lý trị liệu kích thích vận '
                             'động thô, hoạt động trị liệu rèn luyện kỹ năng cầm nắm và ngôn ngữ trị liệu.',
                             'Tư vấn cho cha mẹ kỹ năng tương tác chơi cùng con tại nhà đọc sách tranh nói chuyện chậm '
                             'rãi, theo dõi đánh giá lại sau mỗi chu kỳ can thiệp 3-6 tháng.',
                             'Chuyển khám chuyên khoa Thần kinh Nhi và Di truyền Nhi tìm kiếm các dị tật bẩm sinh vỏ '
                             'não hoặc hội chứng gen hiếm gặp.'],
    'bien_the_kham': [   'Trẻ 18 tháng tuổi chưa biết tự đứng chựng chỉ ngồi tựa, không nói được từ đơn có nghĩa, '
                         'không biết chỉ ngón tay vào đồ vật mình muốn, trương lực cơ trục thân giảm nhẹ, phản xạ gân '
                         'xương bình thường.',
                         'Đánh giá tuổi phát triển tương đương trẻ 9 tháng trong khi tuổi thực 20 tháng, chưa biết '
                         'phối hợp hai tay chuyền đồ vật, không quay đầu lại khi nghe mẹ gọi tên quen thuộc.',
                         'Khám vận động thấy trẻ ngồi chưa vững cột sống gập lưng tôm, chân tay vận động tự do nhưng '
                         'yếu ớt, ánh mắt thờ thẫn ít biểu lộ cảm xúc vui buồn.',
                         'Trẻ 2 tuổi chưa có ngôn ngữ chủ động chỉ phát ra âm thanh ê a vô nghĩa, không nhận biết được '
                         'các bộ phận trên cơ thể khi được hỏi, không biết bắt chước hành động đơn giản.',
                         'Trương lực cơ toàn thân giảm nhẹ kiểu mềm nhẽo, đầu lắc lư nhẹ khi đổi tư thế, phản xạ gân '
                         'cơ bình thường không có dấu hiệu tổn thương bó tháp.',
                         'Vòng đầu trẻ nhỏ hơn 2 độ lệch chuẩn so với tuổi (tật đầu nhỏ), các mốc vận động thô và nhận '
                         'thức bị đình trệ đáng kể, chưa có kỹ năng tự xúc thìa hay cầm cốc.'],
    'chan_doan': 'Chậm phát triển tâm thần vận động mức độ trung bình chưa rõ căn nguyên.',
    'chinh': [   'chậm đạt các mốc vận động thô và vận động tinh như chưa biết lẫy ngồi bò đứng so với lứa tuổi',
                 'chậm phát triển ngôn ngữ không bập bẹ hoặc không nói được từ đơn khi đến tuổi',
                 'khiếm khuyết trong khả năng nhận thức phản ứng kém với môi trường xung quanh'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tâm thần',
    'ke_hoach': 'Đánh giá mức độ phát triển theo thang điểm Denver II hoặc Bayley III, chụp MRI sọ não, làm xét nghiệm '
                'sàng lọc rối loạn chuyển hóa bẩm sinh và nhiễm sắc thể, chỉ định can thiệp sớm đa chuyên khoa tâm lý '
                'vận động và ngôn ngữ trị liệu.',
    'kham': 'Trẻ 18 tháng tuổi chưa biết tự đứng chựng chỉ ngồi tựa, không nói được từ đơn có nghĩa, không biết chỉ '
            'ngón tay vào đồ vật mình muốn, trương lực cơ trục thân giảm nhẹ, phản xạ gân xương bình thường.',
    'nhom': 'nhi',
    'phu': [   'chậm phát triển các kỹ năng tự phục vụ như tự cầm thìa ăn uống mặc áo',
               'tương tác giao tiếp bằng mắt kém hơn so với mốc lứa tuổi',
               'trương lực cơ toàn thân có thể giảm hoặc tăng nhẹ bất thường'],
    'ten': 'chậm phát triển tâm thần vận động'},
    {   'bien_the_chan_doan': [   'Rối loạn phổ tự kỷ ở trẻ em mức độ 2 cần hỗ trợ đáng kể.',
                              'Rối loạn phổ tự kỷ ở trẻ nhỏ có thoái lui ngôn ngữ sau 18 tháng tuổi.',
                              'Rối loạn phổ tự kỷ kèm tăng động giảm chú ý và nhạy cảm quá mức về giác quan.',
                              'Theo dõi rối loạn phổ tự kỷ mức độ 1 cần phân biệt với chậm nói đơn thuần.',
                              'Rối loạn phổ tự kỷ thể nặng mức độ 3 cần hỗ trợ rất đáng kể.',
                              'Rối loạn phổ tự kỷ ở trẻ mầm non có rối loạn giấc ngủ và hành vi tự làm đau.'],
    'bien_the_ke_hoach': [   'Đánh giá chẩn đoán chuyên sâu theo bảng kiểm M-CHAT-R và thang CARS hoặc ADOS-2, khám '
                             'loại trừ suy giảm thính lực bằng đo thính lực ABR, xây dựng kế hoạch can thiệp hành vi '
                             'giáo dục sớm ABA kết hợp trị liệu ngôn ngữ và hoạt động trị liệu.',
                             'Đo thính lực điện sinh lý loại trừ khiếm thính nguyên nhân gây chậm nói, làm điện não đồ '
                             'video giấc ngủ tầm soát động kinh thể cận lâm sàng (hội chứng Landau-Kleffner).',
                             'Thiết lập chương trình can thiệp hành vi chuyên sâu ứng dụng ABA (Applied Behavior '
                             'Analysis) tối thiểu 15-20 giờ mỗi tuần cùng chuyên viên tâm lý giáo dục đặc biệt.',
                             'Trị liệu ngôn ngữ và giao tiếp tăng cường thay thế (PECS) bằng hình ảnh giúp trẻ biểu '
                             'đạt nhu cầu cơ bản, giảm thiểu các hành vi cáu giận đập phá.',
                             'Trị liệu điều hòa cảm giác (Sensory Integration) cải thiện tình trạng sợ tiếng ồn quá '
                             'mức và thói quen đi kiễng gót, hướng dẫn phụ huynh tạo môi trường trực quan tại nhà.',
                             'Khám định kỳ chuyên khoa Tâm thần Nhi để theo dõi tiến bộ, cân nhắc dùng thuốc hỗ trợ '
                             'Risperidone liều thấp nếu trẻ có hành vi hung tính kích động hoặc tự gây thương tích.'],
    'bien_the_kham': [   'Trẻ không giao tiếp bằng mắt khi bác sĩ gọi tên, không đáp ứng với lời nói dù thính lực bình '
                         'thường, liên tục dùng tay xoay tròn bánh xe đồ chơi và lắc lư thân mình, không chỉ ngón tay '
                         'hay khoe đồ vật.',
                         'Trẻ vào phòng khám lảng tránh ánh mắt nhìn chăm chú vào quạt trần quay, gọi tên 5 lần không '
                         'quay đầu lại nhưng lại phản ứng nhạy với tiếng sột soạt mở gói kẹo.',
                         'Khám hành vi thấy trẻ có cử chỉ vẫy tay định hình (flapping hands) mỗi khi phấn khích, đi '
                         'lại bằng đầu ngón chân kiễng gót, cầm đồ chơi xếp thành một hàng dài thẳng tắp.',
                         'Trẻ không có ngôn ngữ biểu đạt chỉ phát ra âm thanh gầm gừ cổ họng, khi muốn lấy vật trên '
                         'cao chỉ biết cầm tay mẹ kéo đặt vào đồ vật đó chứ không nhìn hay chỉ tay.',
                         'Phản ứng bùng nổ la hét bịt chặt hai tai khi nghe tiếng máy sấy tóc hoặc tiếng ồn ngoài hành '
                         'lang, cự tuyệt việc thay đổi chỗ ngồi hay trật tự đồ chơi.',
                         'Không có tương tác hai chiều với người khám, không biết chơi trò giả vờ hay ú òa, hoàn toàn '
                         'đắm chìm trong thế giới riêng cô lập với xung quanh.'],
    'chan_doan': 'Rối loạn phổ tự kỷ ở trẻ em mức độ 2 cần hỗ trợ đáng kể.',
    'chinh': [   'khiếm khuyết kéo dài trong tương tác xã hội và giao tiếp không biết nhìn mắt không cười đáp lại',
                 'chậm nói hoặc hoàn toàn không phát triển ngôn ngữ lời nói không biết dùng cử chỉ chỉ tay',
                 'hành vi định hình lặp đi lặp lại như xoay tròn đồ vật vẫy tay nhón chân đi lại'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tâm thần',
    'ke_hoach': 'Đánh giá chẩn đoán chuyên sâu theo bảng kiểm M-CHAT-R và thang CARS hoặc ADOS-2, khám loại trừ suy '
                'giảm thính lực bằng đo thính lực ABR, xây dựng kế hoạch can thiệp hành vi giáo dục sớm ABA kết hợp '
                'trị liệu ngôn ngữ và hoạt động trị liệu.',
    'kham': 'Trẻ không giao tiếp bằng mắt khi bác sĩ gọi tên, không đáp ứng với lời nói dù thính lực bình thường, liên '
            'tục dùng tay xoay tròn bánh xe đồ chơi và lắc lư thân mình, không chỉ ngón tay hay khoe đồ vật.',
    'nhom': 'nhi',
    'phu': [   'khó thích nghi với sự thay đổi trong thói quen sinh hoạt hàng ngày gắn bó quá mức với trình tự cố định',
               'tăng hoặc giảm phản ứng bất thường với các kích thích giác quan như âm thanh ánh sáng xúc giác',
               'thích chơi một mình cô lập không chia sẻ sở thích hay đồ chơi với người khác'],
    'ten': 'tự kỷ ở trẻ em'},
    {   'bien_the_chan_doan': [   'Viêm khớp vô căn thiếu niên thể ít khớp kéo dài.',
                              'Viêm khớp vô căn thiếu niên thể đa khớp yếu tố dạng thấp âm tính.',
                              'Theo dõi viêm khớp vô căn thiếu niên thể hệ thống Still trẻ em.',
                              'Viêm khớp vô căn thiếu niên có biến chứng teo cơ cạnh khớp.',
                              'Viêm khớp thiếu niên tự phát thể viêm điểm bám gân.',
                              'Viêm khớp vô căn thiếu niên cần tầm soát viêm màng bồ đào trước mạn.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm máu tốc độ lắng máu ESR, CRP, yếu tố dạng thấp RF, kháng thể kháng nhân '
                             'ANA, siêu âm khớp đánh giá tràn dịch màng hoạt dịch, khởi trị bằng Naproxen và hội chẩn '
                             'Mắt tầm soát viêm màng bồ đào.',
                             'Dùng thuốc kháng viêm không steroid Naproxen liều 15 mg/kg/ngày chia 2 lần sau ăn, kết '
                             'hợp tiêm nội khớp Triamcinolone hexacetonide nếu chỉ viêm 1-2 khớp lớn.',
                             'Chỉ định Methotrexate đường uống hoặc tiêm dưới da liều 10-15 mg/m2/tuần phối hợp Acid '
                             'folic nếu bệnh tiến triển đa khớp không đáp ứng NSAID.',
                             'Chuyển khám chuyên khoa Mắt soi đèn khe (slit-lamp) định kỳ mỗi 3-6 tháng để phát hiện '
                             'sớm viêm màng bồ đào trước âm thầm phòng ngừa mù lòa.',
                             'Lập kế hoạch vật lý trị liệu phục hồi chức năng duy trì tầm vận động khớp và sức cơ tứ '
                             'đầu đùi, tránh bất động khớp kéo dài gây cứng dính khớp.',
                             'Theo dõi công thức máu và men gan AST ALT định kỳ hàng tháng trong quá trình điều trị '
                             'Methotrexate hoặc thuốc sinh học kháng TNF.'],
    'bien_the_kham': [   'Khớp gối phải sưng to mất các hõm tự nhiên quanh xương bánh chè, sờ ấm nhẹ có dấu hiệu bập '
                         'bềnh xương bánh chè dương tính, hạn chế gấp duỗi tối đa, teo nhẹ cơ tứ đầu đùi bên phải.',
                         'Viêm đa khớp đối xứng các khớp cổ tay, khớp bàn ngón tay và hai khớp cổ chân, biến dạng nhẹ '
                         'trục ngón tay, biên độ vận động gập duỗi cổ tay giảm 30 độ.',
                         'Trẻ đi khập khiễng bên trái, khớp gối trái tràn dịch lượng vừa, sờ khớp ấm hơn bên đối diện '
                         'nhưng không đỏ da, gấp gối chỉ đạt 100 độ do căng tức.',
                         'Khám thấy sưng đau khớp cổ chân và gân gót hai bên, kèm sưng ngón chân hình khúc dồi '
                         '(dactylitis), phát hiện ban hồng nhạt thoáng qua vùng thân mình khi trẻ sốt.',
                         'Khớp khuỷu và khớp gối sưng nề dai dẳng, trẻ có tư thế chống đau giữ khớp hơi gập nhẹ, đo '
                         'chu vi vòng đùi bên bệnh nhỏ hơn bên lành 1,5cm.',
                         'Viêm khớp cột sống cổ gây hạn chế quay nghiêng cổ, sưng đau khớp háng bên phải dấu hiệu '
                         'Patrick dương tính, gan lách không to ở thể ít khớp.'],
    'chan_doan': 'Viêm khớp vô căn thiếu niên thể ít khớp kéo dài.',
    'chinh': [   'sưng khớp gối hoặc khớp cổ chân kéo dài liên tục trên 6 tuần ở trẻ dưới 16 tuổi',
                 'cứng khớp buổi sáng sau khi thức dậy khiến trẻ đi khập khiễng hoặc ngại vận động',
                 'khớp sưng ấm nhẹ tràn dịch nhưng ít khi đỏ rực như viêm khớp nhiễm khuẩn'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'cơ xương khớp',
    'ke_hoach': 'Làm xét nghiệm máu tốc độ lắng máu ESR, CRP, yếu tố dạng thấp RF, kháng thể kháng nhân ANA, siêu âm '
                'khớp đánh giá tràn dịch màng hoạt dịch, khởi trị bằng Naproxen và hội chẩn Mắt tầm soát viêm màng bồ '
                'đào.',
    'kham': 'Khớp gối phải sưng to mất các hõm tự nhiên quanh xương bánh chè, sờ ấm nhẹ có dấu hiệu bập bềnh xương '
            'bánh chè dương tính, hạn chế gấp duỗi tối đa, teo nhẹ cơ tứ đầu đùi bên phải.',
    'nhom': 'nhi',
    'phu': [   'teo cơ vùng đùi hoặc bắp chân quanh khớp bị viêm mạn tính',
               'sốt từng cơn buổi chiều tối kèm phát ban hồng cá hồi thoáng qua ở thể hệ thống',
               'nguy cơ viêm màng bồ đào mạn tính không triệu chứng gây mờ mắt'],
    'ten': 'viêm khớp vô căn thiếu niên'},
    {   'bien_the_chan_doan': [   'Thoát vị rốn bẩm sinh ở trẻ nhỏ chưa có biến chứng nghẹt.',
                              'Thoát vị rốn bẩm sinh vòng cân nhỏ lành tính theo dõi tự đóng.',
                              'Thoát vị rốn kích thước trung bình ở trẻ nhũ nhi không triệu chứng.',
                              'Thoát vị rốn tồn tại dai dẳng ở trẻ trên 4 tuổi cần cân nhắc phẫu thuật.',
                              'Thoát vị rốn lành tính phân biệt với thoát vị trên rốn đường trắng.',
                              'Thoát vị rốn đơn độc ở trẻ phát triển thể chất bình thường.'],
    'bien_the_ke_hoach': [   'Giải thích cho cha mẹ bản chất lành tính có khả năng tự đóng kín trước 3-5 tuổi, không '
                             'dùng đồng xu hay băng ép chặt lên rốn, theo dõi định kỳ và dặn tái khám ngay nếu khối '
                             'sưng cứng không đẩy vào được.',
                             'Trấn an gia đình không áp dụng các mẹo dân gian băng đồng xu hay dán cao gây loét nhiễm '
                             'trùng da rốn, hướng dẫn theo dõi kích thước vòng thoát vị mỗi 6 tháng.',
                             'Tư vấn các dấu hiệu cảnh báo thoát vị rốn nghẹt hiếm gặp như khối phồng cứng căng đỏ '
                             'tím, trẻ khóc thét bỏ bú nôn dịch xanh để đưa đi cấp cứu ngay.',
                             'Chỉ định siêu âm thành bụng vùng rốn đo chính xác kích thước cổ túi thoát vị nếu nghi '
                             'ngờ khối thoát vị đường trắng trên rốn hoặc nang rốn.',
                             'Hẹn tái khám hội chẩn chuyên khoa Ngoại Nhi lên lịch phẫu thuật khâu phục hồi cân thành '
                             'bụng nếu trẻ trên 4-5 tuổi mà lỗ thoát vị vẫn rộng trên 1,5cm chưa tự bít.',
                             'Kiểm tra kết hợp tầm soát các bệnh lý đi kèm như suy giáp bẩm sinh hoặc hội chứng tăng '
                             'áp lực ổ bụng mạn tính nếu vòng thoát vị giãn rất lớn.'],
    'bien_the_kham': [   'Tại rốn có khối phồng tròn đường kính 2cm nổi rõ khi trẻ rặn khóc, da phủ trên khối bình '
                         'thường, nắn mềm không đau đẩy tụt vào ổ bụng nghe tiếng lọc xọc nhẹ, sờ thấy lỗ khuyết cân '
                         'thành bụng đường kính 1,2cm.',
                         'Quan sát vùng rốn thấy lồi hình vòi voi kích thước 1,5x2cm mỗi khi trẻ gồng bụng ho, khi trẻ '
                         'ngủ say khối xẹp hẳn xuống phẳng với thành bụng, vòng cân rốn hở khoảng 1cm.',
                         'Khối thoát vị rốn đường kính 2,5cm mật độ mềm chứa hơi và quai ruột non, đẩy nhẹ lên trên là '
                         'vào hết hoàn toàn, trẻ hoàn toàn thoải mái không phản ứng đau khi thăm khám.',
                         'Vùng rốn lồi ra khoảng 1,8cm khi bé vặn mình rặn, da rốn mỏng hơi sẫm màu bình thường không '
                         'loét trợt, sờ chạm rõ bờ cân trắng quanh cổ túi thoát vị rộng 1,5cm.',
                         'Khối thoát vị rốn đơn thuần kích thước nhỏ, khi ấn giữ vào lòng bụng thấy rõ cảm giác rỗng '
                         'của lỗ thoát vị đường kính 1cm, bụng mềm không chướng không có khối thoát vị bẹn đi kèm.',
                         'Trẻ 8 tháng tuổi có túi thoát vị rốn phồng to bằng quả chanh nhỏ lúc khóc thét, ấn vào thấy '
                         'mềm mại tụt nhanh vào khoang phúc mạc, không có dấu hiệu tắc nghẽn hay thiếu máu da.'],
    'chan_doan': 'Thoát vị rốn bẩm sinh ở trẻ nhỏ chưa có biến chứng nghẹt.',
    'chinh': [   'khối phồng tròn lồi lên ngay tại vùng rốn khi trẻ khóc ho rặn đi ngoài',
                 'khối phồng mềm tự xẹp nhỏ lại hoặc biến mất hoàn toàn khi trẻ nằm yên thư giãn',
                 'ấn nhẹ tay thấy khối thoát vị tụt vào trong ổ bụng dễ dàng và sờ được vòng rốn hở'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nhi khoa',
    'ke_hoach': 'Giải thích cho cha mẹ bản chất lành tính có khả năng tự đóng kín trước 3-5 tuổi, không dùng đồng xu '
                'hay băng ép chặt lên rốn, theo dõi định kỳ và dặn tái khám ngay nếu khối sưng cứng không đẩy vào '
                'được.',
    'kham': 'Tại rốn có khối phồng tròn đường kính 2cm nổi rõ khi trẻ rặn khóc, da phủ trên khối bình thường, nắn mềm '
            'không đau đẩy tụt vào ổ bụng nghe tiếng lọc xọc nhẹ, sờ thấy lỗ khuyết cân thành bụng đường kính 1,2cm.',
    'nhom': 'nhi',
    'phu': [   'kích thước vòng rốn thường nhỏ dưới 1,5 đến 2 cm',
               'trẻ không đau đớn không quấy khóc bất thường vẫn bú ngủ tăng cân tốt',
               'da phủ trên khối thoát vị rốn bình thường không sưng đỏ bầm tím'],
    'ten': 'thoát vị rốn ở trẻ nhỏ'},
    {   'bien_the_chan_doan': [   'Tinh hoàn ẩn bẩm sinh bên trái sờ thấy ở ống bẹn.',
                              'Tinh hoàn ẩn bẩm sinh hai bên cần phẫu thuật hạ tinh hoàn sớm.',
                              'Tinh hoàn ẩn bẩm sinh bên phải thể không sờ thấy nghi nằm trong ổ bụng.',
                              'Tinh hoàn ẩn bẩm sinh kèm thoát vị bẹn tồn tại ống phúc tinh mạc.',
                              'Tinh hoàn lạc chỗ bẩm sinh phân biệt với tinh hoàn lò xo (co rút).',
                              'Tinh hoàn ẩn bẩm sinh ở trẻ nhũ nhi giai đoạn chuẩn bị can thiệp ngoại khoa.'],
    'bien_the_ke_hoach': [   'Chỉ định siêu âm vùng bẹn bìu và ổ bụng xác định vị trí kích thước tinh hoàn, hội chẩn '
                             'phẫu thuật Ngoại Nhi Tiết niệu thực hiện mổ hạ tinh hoàn xuống bìu trước 12-18 tháng '
                             'tuổi.',
                             'Chuyển chuyên khoa Ngoại Tiết niệu Nhi lập kế hoạch phẫu thuật hạ tinh hoàn cố định vào '
                             'bìu (Orchiopexy) kết hợp thắt ống phúc tinh mạc ở thời điểm vàng 6-18 tháng tuổi.',
                             'Chỉ định nội soi ổ bụng thám sát chẩn đoán và can thiệp đối với thể tinh hoàn ẩn không '
                             'sờ thấy nhằm xác định tinh hoàn trong ổ bụng hay bất sản tinh hoàn.',
                             'Làm xét nghiệm nhiễm sắc thể và nội tiết tố testosterone FSH LH hCG test nếu bé bị tinh '
                             'hoàn ẩn hai bên kèm lỗ tiểu đóng thấp nghi ngờ rối loạn phát triển giới tính.',
                             'Giải thích cho cha mẹ tầm quan trọng của việc phẫu thuật sớm nhằm bảo tồn chức năng sinh '
                             'tinh sau dậy thì và giảm nguy cơ xoắn hoặc ung thư hóa tinh hoàn.',
                             'Hướng dẫn theo dõi chăm sóc vết mổ vùng bẹn bìu sau phẫu thuật và tái khám kiểm tra vị '
                             'trí thể tích tinh hoàn hàng năm cho đến tuổi trưởng thành.'],
    'bien_the_kham': [   'Bé trai bìu phải phát triển bình thường sờ thấy tinh hoàn kích thước chuẩn, bìu trái lép xẹp '
                         'nhẵn da không sờ chạm tinh hoàn trong bìu, dọc ống bẹn trái sờ thấy khối bầu dục 1x0,5cm '
                         'trơn láng không kéo xuống bìu được.',
                         'Khám vùng sinh dục ở phòng ấm áp thấy cả hai bên bìu đều xẹp nhỏ trống rỗng, da bìu kém nhăn '
                         'nheo, nắn kỹ dọc hai bên nếp bẹn tìm thấy tinh hoàn nằm kẹt sát lỗ bẹn nông.',
                         'Bìu phải xẹp lép hoàn toàn, phản xạ cơ bìu âm tính, khám dọc ống bẹn phải và ổ bụng hạ vị '
                         'không sờ thấy tinh hoàn phải (thể tinh hoàn ẩn không sờ thấy).',
                         'Bé trai 10 tháng tuổi có bìu trái nhỏ lép, sờ thấy tinh hoàn trái tại vị trí ống bẹn có thể '
                         'đẩy trượt nhẹ xuống phần trên bìu nhưng thả tay ra lại co tụt lên ống bẹn ngay.',
                         'Khám ở tư thế nằm ngửa và ngồi xổm xác định rõ tinh hoàn phải nằm cố định cao trên lỗ bẹn '
                         'nông không xuống được đáy bìu, kèm túi thoát vị bẹn nhỏ cùng bên.',
                         'Tinh hoàn trái nằm đúng vị trí trong bìu kích thước bình thường, bìu phải trống rỗng xẹp '
                         'hoàn toàn không tìm thấy khối tinh hoàn dọc đường đi xuống bìu.'],
    'chan_doan': 'Tinh hoàn ẩn bẩm sinh bên trái sờ thấy ở ống bẹn.',
    'chinh': [   'bìu một bên hoặc cả hai bên nhỏ xẹp lép bất đối xứng do không có tinh hoàn bên trong',
                 'sờ nắn vùng bìu trống rỗng không thấy khối tinh hoàn di chuyển xuống đáy bìu',
                 'có thể sờ thấy một hạt khối bầu dục nhỏ nằm kẹt ở ống bẹn cùng bên'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nam khoa',
    'ke_hoach': 'Chỉ định siêu âm vùng bẹn bìu và ổ bụng xác định vị trí kích thước tinh hoàn, hội chẩn phẫu thuật '
                'Ngoại Nhi Tiết niệu thực hiện mổ hạ tinh hoàn xuống bìu trước 12-18 tháng tuổi.',
    'kham': 'Bé trai bìu phải phát triển bình thường sờ thấy tinh hoàn kích thước chuẩn, bìu trái lép xẹp nhẵn da '
            'không sờ chạm tinh hoàn trong bìu, dọc ống bẹn trái sờ thấy khối bầu dục 1x0,5cm trơn láng không kéo '
            'xuống bìu được.',
    'nhom': 'nhi',
    'phu': [   'da bìu bên tinh hoàn ẩn kém phát triển ít nếp nhăn hơn bên bình thường',
               'có thể kèm thoát vị bẹn bẩm sinh do còn tồn tại ống phúc tinh mạc',
               'trẻ không có triệu chứng đau đớn hay rối loạn tiểu tiện lúc bình thường'],
    'ten': 'tinh hoàn ẩn bẩm sinh'},
    {   'bien_the_chan_doan': [   'Hẹp bao quy đầu bệnh lý có vòng xơ chít hẹp kèm viêm quy đầu tái diễn.',
                              'Hẹp bao quy đầu bệnh lý ở trẻ em gây cản trở dòng tiểu.',
                              'Hẹp bao quy đầu thứ phát do xơ sẹo sau cố nong tách thô bạo.',
                              'Hẹp bao quy đầu bệnh lý biến chứng viêm bao quy đầu cấp tính.',
                              'Hẹp bao quy đầu bệnh lý có nguy cơ nghẹt quy đầu cần can thiệp cắt bao quy đầu.',
                              'Viêm dính xơ hóa bao quy đầu BXO ở trẻ lớn gây hẹp lỗ tiểu.'],
    'bien_the_ke_hoach': [   'Điều trị đợt viêm cấp bằng vệ sinh ngâm nước ấm và kháng sinh bôi tại chỗ nếu có nhiễm '
                             'khuẩn, sau đó bôi kem Corticoid Betamethasone 0,05% kéo giãn nhẹ hàng ngày hoặc chỉ định '
                             'phẫu thuật cắt bao quy đầu.',
                             'Chỉ định bôi thuốc mỡ Betamethasone 0,05% hoặc Clobetasol lên vùng vòng xơ hẹp ngày 2 '
                             'lần trong 4-6 tuần kết hợp hướng dẫn bố mẹ nong giãn nhẹ nhàng trong khi tắm nước ấm.',
                             'Làm tổng phân tích nước tiểu và cấy nước tiểu loại trừ nhiễm trùng đường tiết niệu đi '
                             'kèm do ứ đọng dòng tiểu, dùng kháng sinh đường uống Cefixime nếu có viêm mủ lan tỏa.',
                             'Hội chẩn chuyên khoa Ngoại Tiết niệu Nhi lên lịch phẫu thuật cắt bao quy đầu '
                             '(circumcision) hoặc tạo hình mở rộng vòng bao quy đầu khi điều trị bảo tồn bằng thuốc '
                             'bôi thất bại.',
                             'Dặn dò phụ huynh tuyệt đối không tự ý cố lộn mạnh bao quy đầu gây rách chảy máu hoặc tạo '
                             'vòng thắt nghẹt cấp cứu bán hẹp (paraphimosis).',
                             'Hướng dẫn chăm sóc vệ sinh vùng kín đúng cách cho trẻ sau tắm, lau khô ráo nhẹ nhàng và '
                             'theo dõi dòng tiểu sau điều trị.'],
    'bien_the_kham': [   'Đầu dương vật có vòng xơ sẹo trắng dày cứng chít hẹp lỗ bao quy đầu chỉ còn lỗ nhỏ như đầu '
                         'tăm, không thể kéo lộn bao quy đầu ra sau được, quy đầu sưng đỏ nhẹ có dịch đục ứ đọng.',
                         'Bao quy đầu dài phủ kín dương vật với lỗ mở ngoài tạo thành vòng xơ hóa cứng màu trắng ngà '
                         '(xơ teo quy đầu BXO), khi bé rặn tiểu đầu bao quy đầu phồng tròn lên rồi nước tiểu mới rỉ '
                         'ra.',
                         'Khám vùng sinh dục bé trai thấy miệng bao quy đầu hẹp khít sưng đỏ phù nề chảy dịch mủ vàng '
                         'đục hôi nhẹ, sờ dọc thân dương vật thấy các khối cặn bựa cứng dưới da quy đầu.',
                         'Vòng hẹp xơ chắc tại đầu da quy đầu gây thắt nghẹt bán phần, cố kéo nhẹ xuất hiện vết nứt '
                         'rách nhỏ rớm máu, trẻ kêu đau rát dữ dội khi chạm vào.',
                         'Lỗ tiểu bị che khuất hoàn toàn bởi vòng da quy đầu xơ dính chặt vào đỉnh quy đầu, có dấu '
                         'hiệu viêm da tiếp xúc quanh lỗ tiểu do nước tiểu ứ đọng lâu ngày.',
                         'Bao quy đầu chít hẹp bệnh lý hoàn toàn không lộ được lỗ sáo, khi quan sát trẻ đi tiểu thấy '
                         'tia nước tiểu rất mảnh bắn cong sang một bên và bao da phồng căng rõ rệt.'],
    'chan_doan': 'Hẹp bao quy đầu bệnh lý có vòng xơ chít hẹp kèm viêm quy đầu tái diễn.',
    'chinh': [   'vòng xơ trắng chít hẹp ở đầu bao quy đầu khiến không thể tuột lộn để lộ quy đầu dương vật',
                 'tiểu khó rặn tiểu tia nước tiểu yếu hoặc vọt lệch hướng kèm phồng căng bao quy đầu như bong bóng khi '
                 'đi tiểu',
                 'viêm nhiễm tái diễn vùng đầu dương vật gây sưng đỏ ngứa đau rát tiểu buốt'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nam khoa',
    'ke_hoach': 'Điều trị đợt viêm cấp bằng vệ sinh ngâm nước ấm và kháng sinh bôi tại chỗ nếu có nhiễm khuẩn, sau đó '
                'bôi kem Corticoid Betamethasone 0,05% kéo giãn nhẹ hàng ngày hoặc chỉ định phẫu thuật cắt bao quy '
                'đầu.',
    'kham': 'Đầu dương vật có vòng xơ sẹo trắng dày cứng chít hẹp lỗ bao quy đầu chỉ còn lỗ nhỏ như đầu tăm, không thể '
            'kéo lộn bao quy đầu ra sau được, quy đầu sưng đỏ nhẹ có dịch đục ứ đọng.',
    'nhom': 'nhi',
    'phu': [   'tích tụ bựa sinh dục trắng đục (smegma) hoặc sỏi bựa dưới lớp da bao quy đầu',
               'trẻ hay sờ gãi kéo vùng kín hoặc khóc thét mỗi lần đi tiểu',
               'có thể xuất hiện biến chứng thắt nghẹt bao quy đầu nếu cố tuột mạnh'],
    'ten': 'hẹp bao quy đầu bệnh lý ở trẻ'},
    {   'bien_the_chan_doan': [   'Lỗ tiểu lệch thấp hypospadias thể giữa thân dương vật có cong dương vật nhẹ.',
                              'Lỗ tiểu lệch thấp hypospadias thể quy đầu không kèm cong thân dương vật.',
                              'Lỗ tiểu lệch thấp thể gốc bìu dương vật nặng cần phẫu thuật nhiều thì.',
                              'Dị tật lỗ tiểu đóng thấp hypospadias bẩm sinh kèm tinh hoàn ẩn một bên.',
                              'Lỗ tiểu lệch thấp thể tầng sinh môn cần tầm soát rối loạn phát triển giới tính.',
                              'Dị tật bẩm sinh lỗ tiểu thấp hypospadias cần tạo hình niệu đạo sử dụng da bao quy đầu.'],
    'bien_the_ke_hoach': [   'Tuyệt đối không cắt bao quy đầu vì cần giữ lại làm vạt da tạo hình niệu đạo, chuyển khám '
                             'chuyên khoa Ngoại Tiết niệu Nhi lập kế hoạch phẫu thuật tạo hình niệu đạo và làm thẳng '
                             'dương vật ở lứa tuổi 6-18 tháng.',
                             'Khuyến cáo gia đình giữ nguyên vẹn bao quy đầu làm chất liệu vá tạo hình ống niệu đạo '
                             'sau này, siêu âm hệ tiết niệu bụng chậu tầm soát dị tật đường tiết niệu trên phối hợp.',
                             'Làm xét nghiệm nhiễm sắc thể đồ Karyotype và nội tiết sinh dục nếu trẻ bị lỗ tiểu lệch '
                             'thấp thể nặng bìu tầng sinh môn phối hợp với tinh hoàn ẩn không sờ thấy.',
                             'Lên lịch phẫu thuật tạo hình niệu đạo một thì theo kỹ thuật Snodgrass hoặc Duckett khi '
                             'trẻ được 6-18 tháng tuổi với điều kiện kích thước quy đầu đạt chuẩn.',
                             'Cân nhắc dùng kem bôi Testosterone liều thấp tại chỗ hoặc tiêm bắp ngắn ngày trước phẫu '
                             'thuật nếu quy đầu và dương vật kích thước quá nhỏ để hỗ trợ phẫu thuật thành công.',
                             'Hướng dẫn chăm sóc sonde tiểu lưu dẫn lưu nước tiểu và giữ băng ép cố định dương vật sau '
                             'phẫu thuật tạo hình niệu đạo, theo dõi phát hiện sớm biến chứng rò hoặc hẹp niệu đạo.'],
    'bien_the_kham': [   'Bé trai có lỗ tiểu đóng thấp nằm ở vị trí rãnh quy đầu mặt dưới, mặt dưới bao quy đầu thiếu '
                         'khuyết tạo hình tạp dề ở mặt lưng, thân dương vật cong gập xuống dưới khoảng 20 độ, hai tinh '
                         'hoàn nằm trong bìu.',
                         'Khám sinh dục trẻ sơ sinh thấy lỗ niệu đạo mở ở phần giữa thân dương vật mặt bụng, đỉnh quy '
                         'đầu chỉ có rãnh lõm tịt, da bao quy đầu chỉ có ở mặt lưng như mũ trùm đầu.',
                         'Thể lỗ tiểu lệch thấp nặng vị trí gốc dương vật bìu: bìu chẻ đôi nhẹ giống môi lớn, dương '
                         'vật nhỏ cong quặp xuống dưới nhiều, sờ thấy hai tinh hoàn hai bên bìu kích thước bình '
                         'thường.',
                         'Quan sát thấy lỗ tiểu đóng lệch thấp ở khấc quy đầu kèm hẹp nhẹ miệng sáo, rãnh niệu đạo '
                         'phía xa nông hẹp, bao quy đầu mặt bụng khuyết hoàn toàn lộ rõ mặt dưới quy đầu.',
                         'Bé trai 1 tuổi đến khám vì tiểu ngồi bắn tóe ướt quần, khám thấy lỗ sáo nằm ở phần xa thân '
                         'dương vật, dây chằng xơ mặt dưới kéo cong thân dương vật góc 30 độ.',
                         'Lỗ tiểu lạc chỗ mở ngay tại vùng tầng sinh môn trước hậu môn, dương vật cong nặng về phía '
                         'bụng, tinh hoàn hai bên đều đã xuống đáy bìu.'],
    'chan_doan': 'Lỗ tiểu lệch thấp hypospadias thể giữa thân dương vật có cong dương vật nhẹ.',
    'chinh': [   'lỗ tiểu không nằm ở đỉnh quy đầu mà mở bất thường ở mặt dưới thân dương vật bìu hoặc tầng sinh môn',
                 'tia nước tiểu bắn xuống dưới hoặc ra sau khiến bé trai không thể đứng tiểu thẳng bình thường',
                 'da bao quy đầu thiếu khuyết ở mặt dưới tạo hình mũ trùm chụp ở mặt lưng quy đầu'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'nam khoa',
    'ke_hoach': 'Tuyệt đối không cắt bao quy đầu vì cần giữ lại làm vạt da tạo hình niệu đạo, chuyển khám chuyên khoa '
                'Ngoại Tiết niệu Nhi lập kế hoạch phẫu thuật tạo hình niệu đạo và làm thẳng dương vật ở lứa tuổi 6-18 '
                'tháng.',
    'kham': 'Bé trai có lỗ tiểu đóng thấp nằm ở vị trí rãnh quy đầu mặt dưới, mặt dưới bao quy đầu thiếu khuyết tạo '
            'hình tạp dề ở mặt lưng, thân dương vật cong gập xuống dưới khoảng 20 độ, hai tinh hoàn nằm trong bìu.',
    'nhom': 'nhi',
    'phu': [   'dương vật bị cong gập xuống dưới rõ rệt đặc biệt khi cương cứng',
               'lỗ tiểu có thể bị hẹp gây tia tiểu nhỏ yếu rặn tiểu lâu',
               'có thể đi kèm dị tật tinh hoàn ẩn hoặc thoát vị bẹn cùng bên'],
    'ten': 'lỗ tiểu lệch thấp hypospadias'},
    {   'bien_the_chan_doan': [   'Trào ngược bàng quang niệu quản tiên phát ở trẻ em nghi độ 3 kèm nhiễm trùng tiểu.',
                              'Trào ngược bàng quang niệu quản hai bên ở trẻ nhỏ có nguy cơ sẹo thận.',
                              'Trào ngược bàng quang niệu quản độ nhẹ phân độ 1-2 phát hiện sau sốt nhiễm khuẩn niệu.',
                              'Theo dõi trào ngược bàng quang niệu quản thứ phát do van niệu đạo sau hoặc bàng quang '
                              'thần kinh.',
                              'Trào ngược bàng quang niệu quản độ 4-5 gây giãn ngoằn ngoèo niệu quản và ứ nước thận.',
                              'Viêm đài bể thận cấp tái phát trên nền trào ngược bàng quang niệu quản bẩm sinh.'],
    'bien_the_ke_hoach': [   'Làm tổng phân tích nước tiểu, cấy nước tiểu tìm vi khuẩn làm kháng sinh đồ, siêu âm hệ '
                             'tiết niệu, chụp bàng quang niệu đạo ngược dòng khi rặn tiểu khẳng định chẩn đoán và phân '
                             'độ trào ngược.',
                             'Điều trị dứt điểm đợt nhiễm trùng tiểu cấp bằng kháng sinh Ceftriaxone tĩnh mạch hoặc '
                             'Cefixime đường uống đủ 10-14 ngày trước khi tiến hành chụp VCUG.',
                             'Chỉ định chụp xạ hình thận DMSA bằng đồng vị phóng xạ sau đợt nhiễm trùng 4-6 tháng để '
                             'đánh giá chính xác mức độ sẹo thận và chức năng tương đối từng thận.',
                             'Xem xét điều trị kháng sinh dự phòng liều thấp ban đêm bằng '
                             'Trimethoprim-Sulfamethoxazole hoặc Cephalexin đối với trào ngược độ 3-5 hoặc có tái phát '
                             'nhiễm trùng.',
                             'Điều trị triệt để tình trạng táo bón bằng thuốc nhuận tràng Macrogol và tập thói quen đi '
                             'tiểu theo giờ (tiểu hai lần) giúp giảm áp lực bàng quang.',
                             'Hội chẩn Ngoại Tiết niệu Nhi cân nhắc tiêm chất độn nội soi lỗ niệu quản (Deflux) hoặc '
                             'phẫu thuật cắm lại niệu quản vào bàng quang nếu nhiễm trùng tái diễn dù đã dự phòng.'],
    'bien_the_kham': [   'Trẻ tỉnh táo nhưng vẻ mặt mệt mỏi, nhiệt độ 38,8 độ C, ấn vùng hạ vị trên xương mu và hai hố '
                         'thắt lưng trẻ nhăn mặt phản ứng đau nhẹ, cơ quan sinh dục ngoài bình thường không hẹp bao '
                         'quy đầu.',
                         'Bé gái 2 tuổi sốt cao 39,2 độ C không kèm triệu chứng ho sổ mũi, nước tiểu trong túi thu '
                         'thập vẩn đục lợn cợn, rung thận bên trái trẻ khóc thét né tránh.',
                         'Khám bụng thấy hố thắt lưng không sưng nề, sờ chạm nhẹ cực dưới thận phải không đau nhiều, '
                         'trẻ có thói quen nhịn tiểu vắt chéo hai chân và táo bón phân cứng.',
                         'Trẻ nhũ nhi sốt cao kéo dài quấy khóc liên tục, sút cân nhẹ, khám toàn thân tai mũi họng '
                         'phổi sạch hoàn toàn, chỉ thấy vùng hạ vị hơi căng tức khi ấn sâu.',
                         'Khám định kỳ trẻ có tiền sử giãn bể thận bào thai: trẻ phát triển thể chất bình thường, '
                         'huyết áp đo tay ở mức bình thường theo tuổi, bụng mềm không sờ thấy cầu bàng quang.',
                         'Trẻ 4 tuổi than đau lưng trái khi tiểu, ấn điểm đau niệu quản trên và giữa bên trái dương '
                         'tính, mạch nhanh 125 l/p do sốt, tã ướt nước tiểu màu vàng đục.'],
    'chan_doan': 'Trào ngược bàng quang niệu quản tiên phát ở trẻ em nghi độ 3 kèm nhiễm trùng tiểu.',
    'chinh': [   'nhiễm trùng đường tiết niệu có sốt cao tái đi tái lại nhiều đợt ở trẻ nhỏ',
                 'tiểu rắt tiểu buốt khóc thét khi đi tiểu kèm nước tiểu đục mùi hôi khai nồng',
                 'trẻ có thể có biểu hiện tiểu dầm ban ngày hoặc tiểu ngập ngừng tiểu hai thì'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'thận - tiết niệu',
    'ke_hoach': 'Làm tổng phân tích nước tiểu, cấy nước tiểu tìm vi khuẩn làm kháng sinh đồ, siêu âm hệ tiết niệu, '
                'chụp bàng quang niệu đạo ngược dòng khi rặn tiểu (VCUG) khẳng định chẩn đoán và phân độ trào ngược.',
    'kham': 'Trẻ tỉnh táo nhưng vẻ mặt mệt mỏi, nhiệt độ 38,8 độ C, ấn vùng hạ vị trên xương mu và hai hố thắt lưng '
            'trẻ nhăn mặt phản ứng đau nhẹ, cơ quan sinh dục ngoài bình thường không hẹp bao quy đầu.',
    'nhom': 'nhi',
    'phu': [   'trẻ sốt cao không rõ nguyên nhân kèm chán ăn nôn trớ chậm tăng cân',
               'tiền sử siêu âm tiền sản phát hiện thận ứ nước giãn đài bể thận bẩm sinh',
               'táo bón kéo dài đi kèm rối loạn chức năng bàng quang ruột'],
    'ten': 'trào ngược bàng quang niệu quản ở trẻ'},
    {   'bien_the_chan_doan': [   'Viêm tai giữa mạn tính thủng màng nhĩ bên phải giai đoạn chảy mủ.',
                              'Viêm tai giữa mạn tính thủng nhĩ đơn thuần hai bên có giảm thính lực dẫn truyền.',
                              'Viêm tai giữa mạn tính thủng màng nhĩ giai đoạn khô ổn định.',
                              'Theo dõi viêm tai giữa mạn thủng sát rìa xương nghi ngờ có cholesteatoma.',
                              'Viêm tai giữa mạn tính chảy mủ kéo dài ở trẻ có quá phát V.A.',
                              'Viêm tai giữa thủng nhĩ mạn tính đợt bùng phát cấp sau nhiễm khuẩn hô hấp trên.'],
    'bien_the_ke_hoach': [   'Lấy mủ tai làm xét nghiệm nuôi cấy vi khuẩn và kháng sinh đồ, hút rửa làm thuốc tai sạch '
                             'hàng ngày, nhỏ tai dung dịch kháng sinh không độc cho ốc tai như Ciprofloxacin hoặc '
                             'Ofloxacin, phối hợp kháng sinh uống nếu đợt cấp.',
                             'Chỉ định đo thính lực đồ đơn âm đánh giá mức độ nghe kém dẫn truyền và đo nhĩ lượng kiểm '
                             'tra thể tích ống tai, chụp CT xương thái dương nếu nghi ngờ cholesteatoma.',
                             'Thực hiện vệ sinh hút sạch dịch mủ tai bằng ống hút vi phẫu dưới nội soi kết hợp nhỏ '
                             'Ofloxacin 0,3% ngày 2 lần trong 10 ngày cho đến khi tai khô hoàn toàn.',
                             'Điều trị triệt để ổ viêm vùng mũi họng đi kèm bằng rửa mũi nước muối sinh lý, cân nhắc '
                             'phẫu thuật nạo V.A nếu V.A phì đại gây tắc vòi nhĩ tái phát.',
                             'Hướng dẫn gia đình tuyệt đối giữ tai khô ráo khi tắm gội hoặc bơi lội bằng nút tai chống '
                             'nước chuyên dụng, không tự ý nhỏ các loại thuốc bột hay thuốc lá dân gian.',
                             'Hội chẩn chuyên khoa Tai Mũi Họng lên kế hoạch phẫu thuật vá màng nhĩ (Tympanoplasty) '
                             'tạo hình chuỗi xương con khi tai khô ổn định trên 3-6 tháng và trẻ đạt độ tuổi phù hợp.'],
    'bien_the_kham': [   'Ống tai ngoài bên phải chứa nhiều dịch mủ vàng xanh nhầy dính, hút sạch mủ quan sát thấy '
                         'màng nhĩ thủng rộng hình quả thận ở góc phần tư trước dưới, bờ lỗ thủng nhẵn dày, niêm mạc '
                         'hòm nhĩ xung huyết đỏ.',
                         'Nội soi tai trái ghi nhận lỗ thủng trung tâm màng nhĩ chiếm khoảng 40% diện tích màng căng, '
                         'qua lỗ thủng thấy niêm mạc hòm nhĩ phù nề ướt ẩm, không thấy khối vảy trắng cholesteatoma.',
                         'Ống tai ngoài đọng dịch nhầy trong lẫn vệt mủ khô đóng vảy ở cửa tai, soi màng nhĩ hai bên '
                         'phát hiện lỗ thủng nhỏ phần tư sau dưới bên phải bờ xơ chai nhẵn.',
                         'Khám tai mũi họng thấy lỗ thủng màng nhĩ trái rộng gần toàn bộ màng căng, niêm mạc đáy hòm '
                         'nhĩ nhợt nhạt ít xuất tiết mủ, trẻ có V.A phì đại độ 3 bít tắc cửa mũi sau.',
                         'Tai phải chảy dịch mủ loãng kéo dài trên 6 tuần sau đợt viêm mũi họng, soi tai thấy lỗ thủng '
                         'sát khung xương ở góc sau trên kèm tổ chức hạt viêm sùi đỏ dễ chảy máu.',
                         'Kiểm tra thính lực thô trẻ nghe kém rõ bên tai thủng màng nhĩ khi nói thầm sau lưng, màng '
                         'nhĩ mất tam giác sáng thủng lỗ tròn đường kính 3mm rỉ dịch mủ trắng.'],
    'chan_doan': 'Viêm tai giữa mạn tính thủng màng nhĩ bên phải giai đoạn chảy mủ.',
    'chinh': [   'chảy mủ tai kéo dài hoặc chảy mủ tái đi tái lại từng đợt mùi hôi khẳm hoặc tanh',
                 'lỗ thủng màng nhĩ tồn tại dai dẳng nhìn thấy qua soi tai',
                 'nghe kém giảm thính lực bên tai bệnh khiến trẻ hay hỏi lại hoặc tăng âm lượng tivi'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tai mũi họng',
    'ke_hoach': 'Lấy mủ tai làm xét nghiệm nuôi cấy vi khuẩn và kháng sinh đồ, hút rửa làm thuốc tai sạch hàng ngày, '
                'nhỏ tai dung dịch kháng sinh không độc cho ốc tai như Ciprofloxacin hoặc Ofloxacin, phối hợp kháng '
                'sinh uống nếu đợt cấp.',
    'kham': 'Ống tai ngoài bên phải chứa nhiều dịch mủ vàng xanh nhầy dính, hút sạch mủ quan sát thấy màng nhĩ thủng '
            'rộng hình quả thận ở góc phần tư trước dưới, bờ lỗ thủng nhẵn dày, niêm mạc hòm nhĩ xung huyết đỏ.',
    'nhom': 'nhi',
    'phu': [   'trẻ thường không sốt hoặc chỉ sốt nhẹ khi có đợt cấp bùng phát',
               'tiền sử viêm tai giữa cấp tái diễn nhiều lần không điều trị triệt để',
               'có cảm giác ù tai đầy nặng tai hoặc chóng mặt nhẹ nếu tổn thương lan vào mê nhĩ'],
    'ten': 'viêm tai giữa màng nhĩ thủng ở trẻ'},
    {   'bien_the_chan_doan': [   'Viêm xoang hàm cấp tính do vi khuẩn ở trẻ em.',
                              'Viêm xoang hàm cấp ở trẻ nhỏ tiến triển nặng sau cảm lạnh siêu vi.',
                              'Theo dõi viêm xoang hàm sàng cấp tính ở trẻ em chưa biến chứng ổ mắt.',
                              'Viêm xoang hàm cấp tính bên trái gây ho kéo dài ban đêm ở trẻ em.',
                              'Viêm mũi xoang cấp nhiễm khuẩn ở trẻ em đáp ứng kém với amoxicillin đơn thuần.',
                              'Viêm xoang hàm cấp tính ở trẻ có tiền sử viêm mũi dị ứng.'],
    'bien_the_ke_hoach': [   'Điều trị kháng sinh đường uống Amoxicillin-Clavulanate liều cao 80-90 mg/kg/ngày chia 2 '
                             'lần trong 10-14 ngày, rửa mũi bằng nước muối sinh lý đẳng trương, dùng thuốc co mạch nhỏ '
                             'mũi ngắn ngày dưới 5 ngày và hạ sốt giảm đau.',
                             'Kê đơn kháng sinh Cefuroxime hoặc Cefdinir thay thế nếu trẻ có tiền sử dị ứng nhẹ với '
                             'nhóm Penicillin, kết hợp thuốc giảm ho tiêu nhầy Acetylcysteine đường uống.',
                             'Hướng dẫn phụ huynh kỹ thuật rửa mũi đúng tư thế bằng bình xịt nước muối sinh lý ấm giúp '
                             'làm sạch dịch mủ ứ đọng và thông thoáng lỗ thông xoang.',
                             'Chỉ định thuốc xịt mũi Corticosteroid tại chỗ (Mometasone hoặc Fluticasone) nếu trẻ có '
                             'cơ địa viêm mũi dị ứng đi kèm để giảm phù nề niêm mạc khe giữa.',
                             'Theo dõi sát diễn tiến lâm sàng trong 48-72 giờ đầu, dặn tái khám khẩn cấp nếu trẻ xuất '
                             'hiện sưng đỏ mi mắt, đau đầu dữ dội hoặc sốt cao rét run.',
                             'Hội chẩn Tai Mũi Họng đánh giá khả năng quá phát V.A hoặc dị tật vách ngăn nếu viêm '
                             'xoang hàm tái phát nhiều đợt liên tục trong năm.'],
    'bien_the_kham': [   'Niêm mạc mũi hai bên phù nề xung huyết đỏ rực, khe mũi giữa xuất tiết nhiều dịch mủ đặc màu '
                         'vàng xanh chảy xuống vòm họng, ấn điểm hố nanh vùng gò má hai bên trẻ kêu đau nhăn mặt, '
                         'thành sau họng có dải mủ chảy xuống.',
                         'Nội soi mũi trước thấy cuốn mũi dưới nề to chít hẹp đường thở, có vệt dịch nhầy đục đọng ở '
                         'sàn mũi và khe giữa bên trái, gõ nhẹ vùng xoang hàm trái trẻ kêu đau nhói.',
                         'Trẻ hơi thở hôi nồng mùi mủ, vùng má dưới mi mắt dưới hơi nề nhẹ không đỏ nóng, khám họng '
                         'thấy amidan bình thường nhưng thành sau họng phủ lớp dịch nhầy vàng chảy từ vòm xuống.',
                         'Dịch mũi đặc quánh dính bít lỗ mũi trước gây thở bằng miệng, ấn vùng mặt trước xương hàm '
                         'trên hai bên gây đau rõ rệt, phổi nghe thông khí đều không có ran ẩm ran rít.',
                         'Trẻ sốt 38,5 độ C ngày thứ 12 của đợt viêm mũi họng, soi mũi thấy mủ đặc chảy ra từ lỗ thông '
                         'xoang hàm ở khe giữa, hạch cổ hai bên sưng nhẹ kích thước 0,5cm.',
                         'Khám tai mũi họng ghi nhận tình trạng viêm mũi xoang mủ cấp tính: niêm mạc hốc mũi sưng nề '
                         'nhợt đỏ, khe giữa đầy mủ trắng đục, tai hai bên màng nhĩ hơi đục nhẹ.'],
    'chan_doan': 'Viêm xoang hàm cấp tính do vi khuẩn ở trẻ em.',
    'chinh': [   'nghẹt mũi chảy nước mũi mủ đặc màu vàng hoặc xanh kéo dài trên 10 ngày không thuyên giảm',
                 'ho nhiều vào ban đêm khi nằm ngủ do dịch mủ chảy xuống thành sau họng',
                 'đau nhức vùng gò má hốc mắt hoặc đau đầu âm ỉ kèm hơi thở có mùi hôi'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tai mũi họng',
    'ke_hoach': 'Điều trị kháng sinh đường uống Amoxicillin-Clavulanate liều cao 80-90 mg/kg/ngày chia 2 lần trong '
                '10-14 ngày, rửa mũi bằng nước muối sinh lý đẳng trương, dùng thuốc co mạch nhỏ mũi ngắn ngày dưới 5 '
                'ngày và hạ sốt giảm đau.',
    'kham': 'Niêm mạc mũi hai bên phù nề xung huyết đỏ rực, khe mũi giữa xuất tiết nhiều dịch mủ đặc màu vàng xanh '
            'chảy xuống vòm họng, ấn điểm hố nanh vùng gò má hai bên trẻ kêu đau nhăn mặt, thành sau họng có dải mủ '
            'chảy xuống.',
    'nhom': 'nhi',
    'phu': [   'trẻ sốt nhẹ hoặc sốt cao trở lại sau vài ngày tưởng chừng đã khỏi cảm lạnh',
               'sưng nề nhẹ vùng má dưới mi mắt vào buổi sáng thức dậy',
               'trẻ mệt mỏi biếng ăn khứu giác giảm ngửi kém'],
    'ten': 'viêm xoang hàm cấp ở trẻ em'},
    {   'bien_the_chan_doan': [   'Áp xe quanh amidan bên phải ở trẻ em giai đoạn tụ mủ.',
                              'Áp xe quanh amidan bên trái biến chứng khít hàm nặng và mất nước.',
                              'Theo dõi viêm tấy quanh amidan đang chuyển thành áp xe hóa ở trẻ em.',
                              'Áp xe quanh amidan cấp tính gây chèn ép bán phần eo họng.',
                              'Áp xe quanh amidan ở trẻ lớn nghi do liên cầu khuẩn hoặc vi khuẩn kỵ khí.',
                              'Áp xe quanh amidan tái phát ở trẻ có tiền sử viêm amidan mạn tính.'],
    'bien_the_ke_hoach': [   'Nhập viện điều trị khẩn cấp, chỉ định chọc hút dẫn lưu hoặc rạch tháo mủ ổ áp xe quanh '
                             'amidan dưới an thần giảm đau, cấy mủ làm kháng sinh đồ, dùng kháng sinh tĩnh mạch '
                             'Amoxicillin-Clavulanate hoặc Clindamycin phối hợp bù dịch.',
                             'Siêu âm vùng cổ góc hàm hoặc qua khoang miệng xác định kích thước ổ mủ và loại trừ biến '
                             'chứng lan sang áp xe thành bên họng gần động mạch cảnh.',
                             'Lập đường truyền tĩnh mạch truyền dịch đẳng trương bù nước điện giải do trẻ không nuốt '
                             'được, tiêm tĩnh mạch Ampicillin-Sulbactam hoặc Ceftriaxone phối hợp Metronidazole phủ vi '
                             'khuẩn kỵ khí.',
                             'Dùng một liều Corticosteroid Dexamethasone đường tĩnh mạch để giảm nhanh phù nề vùng màn '
                             'hầu cải thiện khít hàm và hỗ trợ trẻ nuốt dễ hơn.',
                             'Thực hiện rạch tháo mủ tại điểm phồng nhất (điểm giao nhau theo đường kinh điển Chiari) '
                             'hoặc chọc hút kim lớn dưới gây mê ngắn an toàn tại phòng mổ Nhi.',
                             'Theo dõi sát đường thở đề phòng phù nề thanh quản, lên kế hoạch cắt amidan nguội sau khi '
                             'ổ áp xe ổn định hoàn toàn khoảng 4-6 tuần nếu tái diễn nhiều lần.'],
    'bien_the_kham': [   'Trẻ há miệng hạn chế chỉ đạt 1,5cm (dấu khít hàm), trụ trước amidan phải sưng phồng căng đỏ '
                         'lồi vượt qua đường giữa đẩy lệch lưỡi gà sang bên trái, amidan phải bị đẩy tụt vào trong '
                         'xuống dưới, hạch góc hàm phải to 2,5cm đau.',
                         'Khám họng khó khăn do co cứng cơ cắn khít hàm vừa, quan sát thấy khối phồng căng mọng đỏ tấy '
                         'ở cực trên amidan trái, lưỡi gà phù nề phù mọng lệch hẳn sang bên phải.',
                         'Trẻ chảy nước miếng liên tục không nuốt được, giọng nói nghẹt như ngậm vật nóng trong miệng, '
                         'sờ vùng góc hàm trái sưng nề nóng cứng ấn đau chói, màng hầu một bên phồng căng.',
                         'Vùng quanh amidan phải sưng tấy mất rãnh họng màn hầu, ấn nhẹ bằng đầu que đè lưỡi có cảm '
                         'giác bùng nhùng tụ mủ bên dưới, hơi thở hôi khẳm, nhiệt độ 39,4 độ C.',
                         'Trẻ nghiêng cổ chống đau sang bên phải, khám thấy mất cân đối vùng họng hầu rõ rệt: trụ '
                         'trước bên phải phồng to chèn ép eo họng làm hẹp đường thở nhẹ, không có tiếng thở rít thanh '
                         'quản.',
                         'Dấu hiệu nhiễm trùng nhiễm độc toàn thân: môi khô lưỡi bẩn đóng bựa trắng, khít hàm độ 2, '
                         'khối sưng phồng quanh amidan trái căng bóng đẩy lưỡi gà lệch trục.'],
    'chan_doan': 'Áp xe quanh amidan bên phải ở trẻ em giai đoạn tụ mủ.',
    'chinh': [   'đau họng dữ dội một bên tăng nhanh khiến trẻ không nuốt nổi nước bọt chảy dãi ròng ròng',
                 'khít hàm hạn chế mở miệng không há to miệng được để ăn uống hay thăm khám',
                 'sốt cao liên tục vẻ mặt nhiễm trùng kèm giọng nói ngậm hạt thị ồm ồm'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tai mũi họng',
    'ke_hoach': 'Nhập viện điều trị khẩn cấp, chỉ định chọc hút dẫn lưu hoặc rạch tháo mủ ổ áp xe quanh amidan dưới an '
                'thần giảm đau, cấy mủ làm kháng sinh đồ, dùng kháng sinh tĩnh mạch Amoxicillin-Clavulanate hoặc '
                'Clindamycin phối hợp bù dịch.',
    'kham': 'Trẻ há miệng hạn chế chỉ đạt 1,5cm (dấu khít hàm), trụ trước amidan phải sưng phồng căng đỏ lồi vượt qua '
            'đường giữa đẩy lệch lưỡi gà sang bên trái, amidan phải bị đẩy tụt vào trong xuống dưới, hạch góc hàm phải '
            'to 2,5cm đau.',
    'nhom': 'nhi',
    'phu': [   'đau lan lên tai cùng bên khi nuốt',
               'hạch góc hàm cùng bên sưng to ấn đau chói và cổ hơi nghiêng về bên đau',
               'hơi thở rất hôi thối kèm mệt mỏi li bì mất nước do không ăn uống được'],
    'ten': 'áp xe quanh amidan ở trẻ'},
    {   'bien_the_chan_doan': [   'Thở rít thanh quản bẩm sinh do mềm sụn thanh nhiệt mức độ nhẹ.',
                              'Mềm sụn thanh quản bẩm sinh ở trẻ nhũ nhi kèm trào ngược dạ dày thực quản.',
                              'Thở rít thanh quản bẩm sinh mức độ trung bình có rút lõm lồng ngực khi bú.',
                              'Theo dõi mềm sụn thanh quản thể nặng gây chậm tăng cân và cơn ngưng thở.',
                              'Thở rít thì hít vào ở trẻ nhũ nhi nghi ngờ mềm sụn thanh quản điển hình.',
                              'Mềm sụn thanh quản bẩm sinh phân biệt với liệt dây thanh âm hay hẹp hạ thanh môn.'],
    'bien_the_ke_hoach': [   'Chỉ định nội soi thanh quản ống mềm qua đường mũi đánh giá trực tiếp hình ảnh sụn thanh '
                             'nhiệt hình omega và độ sa sụn phễu khi hít vào, tư vấn cha mẹ cho trẻ nằm nghiêng đầu '
                             'cao, chia nhỏ cữ bú và theo dõi tự khỏi trước 18-24 tháng tuổi.',
                             'Thực hiện nội soi tai mũi họng ống mềm không gây mê quan sát cử động dây thanh và mức độ '
                             'sụp hẹp thanh môn thì hít vào, loại trừ các dị tật thanh quản khác như u nang hay màng '
                             'ngăn.',
                             'Hướng dẫn gia đình tư thế cho trẻ bú ngồi thẳng đầu cao tránh sặc sữa, vỗ ợ hơi kỹ sau '
                             'mỗi cữ bú và chia thành nhiều bữa nhỏ lượng ít hơn.',
                             'Điều trị kiểm soát trào ngược dạ dày thực quản đi kèm bằng thuốc ức chế bơm proton '
                             'Omeprazole hoặc làm đặc sữa nếu trẻ thường xuyên nôn trớ kích thích phù nề thanh quản.',
                             'Dặn dò các dấu hiệu nguy hiểm cần nhập viện ngay như cơn tím tái ngừng thở khi bú, rút '
                             'lõm lồng ngực nặng liên tục hoặc đứng cân suy dinh dưỡng.',
                             'Hội chẩn phẫu thuật Tai Mũi Họng Nhi cân nhắc chỉ định tạo hình thượng thanh môn '
                             '(Supraglottoplasty) qua nội soi đối với những trường hợp thể nặng suy hô hấp.'],
    'bien_the_kham': [   'Trẻ tỉnh táo hồng hào SpO2 98% khí phòng, nghe rõ tiếng thở rít nhẹ thì hít vào khi trẻ nằm '
                         'ngửa cử động tay chân, giọng khóc trong vang bình thường không khàn, lồng ngực rút lõm nhẹ '
                         'hõm ức khi kích thích, phổi hai bên không có ran.',
                         'Nghe tiếng khò khè rít thanh quản thì hít vào rất đặc trưng khi trẻ bú bình, khi bế vác trẻ '
                         'thẳng đứng hoặc đặt nằm sấp sấp ngực tiếng rít giảm hẳn ngay lập tức.',
                         'Khám hô hấp thấy trẻ thở co kéo nhẹ khoảng gian sườn và hõm trên xương ức mức độ nhẹ lúc '
                         'khóc thét, nhịp thở 42 l/p, không tím tái môi đầu chi, tim phổi bình thường.',
                         'Tiếng thở rít thì hít vào êm dịu kiểu rung âm sắc cao, tiếng khóc bình thường chứng tỏ dây '
                         'thanh âm hai bên nguyên vẹn, trẻ tăng cân chậm nhẹ do hay bị mệt ọc sữa khi bú.',
                         'Trẻ 3 tháng tuổi thở rít liên tục tăng dần từ lúc 2 tuần tuổi, khi ngủ yên thở nhẹ nhàng '
                         'hơn, không có bướu máu vùng da mặt cổ hay dấu hiệu chèn ép khí quản.',
                         'Khám thấy lõm nhẹ phần dưới xương ức lúc hít vào gắng sức, da niêm hồng hào SpO2 97%, nghe '
                         'phổi rì rào phế nang đều rõ hai bên nhưng có tiếng lan truyền từ thanh quản.'],
    'chan_doan': 'Thở rít thanh quản bẩm sinh do mềm sụn thanh nhiệt mức độ nhẹ.',
    'chinh': [   'tiếng thở rít âm sắc cao ở thì hít vào xuất hiện từ những tuần đầu sau sinh',
                 'tiếng thở rít tăng rõ rệt khi trẻ nằm ngửa khi quấy khóc kích thích hoặc khi bú sữa',
                 'tiếng thở rít giảm hoặc biến mất khi trẻ nằm sấp nằm nghiêng hoặc ngủ yên'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tai mũi họng',
    'ke_hoach': 'Chỉ định nội soi thanh quản ống mềm qua đường mũi đánh giá trực tiếp hình ảnh sụn thanh nhiệt hình '
                'omega và độ sa sụn phễu khi hít vào, tư vấn cha mẹ cho trẻ nằm nghiêng đầu cao, chia nhỏ cữ bú và '
                'theo dõi tự khỏi trước 18-24 tháng tuổi.',
    'kham': 'Trẻ tỉnh táo hồng hào SpO2 98% khí phòng, nghe rõ tiếng thở rít nhẹ thì hít vào khi trẻ nằm ngửa cử động '
            'tay chân, giọng khóc trong vang bình thường không khàn, lồng ngực rút lõm nhẹ hõm ức khi kích thích, phổi '
            'hai bên không có ran.',
    'nhom': 'nhi',
    'phu': [   'trẻ vẫn khóc to rõ tiếng không bị khàn tiếng hay mất tiếng',
               'thở hơi lõm hõm ức hoặc rút lõm nhẹ dưới sườn lúc bú gắng sức',
               'có thể kèm trào ngược dạ dày thực quản ọc sữa và chậm tăng cân nếu thể nặng'],
    'ten': 'thở rít thanh quản bẩm sinh mềm sụn thanh nhiệt'},
    {   'bien_the_chan_doan': [   'Dị vật đường thở bỏ quên ở trẻ em tại phế quản gốc phải gây viêm phổi tắc nghẽn.',
                              'Theo dõi dị vật đường thở bỏ quên ở trẻ em biến chứng xẹp phổi thùy dưới trái.',
                              'Dị vật hữu cơ (hạt lạc) bỏ quên trong phế quản gây ứ khí van một chiều.',
                              'Viêm phổi tái diễn cùng vị trí nghi ngờ dị vật đường thở bỏ sót ở trẻ nhỏ.',
                              'Dị vật đường thở bỏ quên gây giãn phế quản khu trú và u hạt viêm.',
                              'Nghi ngờ dị vật khí phế quản bỏ quên ở trẻ dưới 3 tuổi cần nội soi thám sát.'],
    'bien_the_ke_hoach': [   'Chụp X-quang ngực thẳng thì hít vào và thở ra tối đa tìm dấu hiệu ứ khí lệch trung thất '
                             'hoặc xẹp phổi, chụp CT ngực dựng hình cây khí phế quản, hội chẩn nội soi phế quản ống '
                             'cứng gắp dị vật dưới gây mê toàn thân.',
                             'Chỉ định chụp cắt lớp vi tính lồng ngực đa dãy (MSCT) tái tạo 3D cây khí phế quản xác '
                             'định chính xác vị trí kích thước dị vật và mức độ tổn thương nhu mô phổi.',
                             'Chuyển chuyên khoa Hô hấp Nhi và Tai Mũi Họng phối hợp chuẩn bị nội soi phế quản ống '
                             'cứng cấp cứu lấy bỏ dị vật và hút rửa sạch dịch mủ ứ đọng phía sau.',
                             'Điều trị kháng sinh tĩnh mạch phối hợp Cefotaxime hoặc Amoxicillin-Clavulanate trước và '
                             'sau nội soi để kiểm soát tình trạng viêm phổi tắc nghẽn bội nhiễm.',
                             'Dùng Corticosteroid đường toàn thân ngắn ngày Dexamethasone sau thủ thuật nội soi để '
                             'giảm phù nề niêm mạc thanh khí phế quản và mô hạt viêm.',
                             'Tư vấn phòng ngừa cho cha mẹ tuyệt đối không cho trẻ dưới 4 tuổi ăn các loại hạt cứng '
                             'lạc đỗ hay chơi đồ chơi có chi tiết tháo rời nhỏ.'],
    'bien_the_kham': [   'Trẻ tỉnh táo ho khúc khắc, nghe phổi thấy giảm thông khí rõ rệt kèm tiếng ran rít khu trú '
                         'một bên đáy phổi phải, bên phổi trái thông khí bù trừ bình thường, gõ ngực phải hơi vang nhẹ '
                         'do ứ khí.',
                         'Khám hô hấp thấy lồng ngực bên trái kém di động hơn bên phải, rung thanh giảm vùng đáy phổi '
                         'trái, nghe rì rào phế nang mất hoàn toàn ở thùy dưới trái nghi xẹp phổi sau dị vật.',
                         'Nghe phổi có tiếng thở rít khu trú một thì cố định ở vùng rốn phổi phải, không thay đổi sau '
                         'khi trẻ ho mạnh hay khí dung salbutamol, nhịp thở 32 lần/phút SpO2 95%.',
                         'Trẻ ho từng tràng dài khạc đờm đặc vàng, khám thấy gõ đục và ran ẩm nổ tập trung duy nhất ở '
                         'thùy dưới phổi phải tái đi tái lại suốt 2 tháng nay.',
                         'Dấu hiệu bất đối xứng thông khí hai phế trường rõ rệt: phổi trái rì rào phế nang êm dịu '
                         'mạnh, phổi phải giảm âm sắc kèm ran ngáy ran ẩm khu trú đáy phải.',
                         'Trẻ hơi mệt mỏi da niêm hồng, không rút lõm lồng ngực nặng, nghe phổi phát hiện tiếng khò '
                         'khè đơn âm (monophonic wheeze) chỉ nghe thấy tại vùng phế quản gốc phải.'],
    'chan_doan': 'Dị vật đường thở bỏ quên ở trẻ em tại phế quản gốc phải gây viêm phổi tắc nghẽn.',
    'chinh': [   'ho kéo dài dai dẳng nhiều tuần không dứt kèm khò khè khu trú một bên phổi dù đã uống nhiều đợt kháng '
                 'sinh',
                 'tiền sử có cơn sặc sụa tím tái đột ngột khi đang ăn hạt lạc hoặc ngậm đồ chơi nhỏ bị bỏ qua trước đó',
                 'viêm phổi tái phát nhiều lần tại cùng một vị trí thùy phổi duy nhất'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'hô hấp',
    'ke_hoach': 'Chụp X-quang ngực thẳng thì hít vào và thở ra tối đa tìm dấu hiệu ứ khí lệch trung thất hoặc xẹp '
                'phổi, chụp CT ngực dựng hình cây khí phế quản, hội chẩn nội soi phế quản ống cứng gắp dị vật dưới gây '
                'mê toàn thân.',
    'kham': 'Trẻ tỉnh táo ho khúc khắc, nghe phổi thấy giảm thông khí rõ rệt kèm tiếng ran rít khu trú một bên đáy '
            'phổi phải, bên phổi trái thông khí bù trừ bình thường, gõ ngực phải hơi vang nhẹ do ứ khí.',
    'nhom': 'nhi',
    'phu': [   'thở khò khè một bên phế trường không đáp ứng với thuốc giãn phế quản',
               'ho khạc đờm nhầy mủ có thể lẫn ít tia máu hoặc mùi hôi do ứ đọng sau tắc nghẽn',
               'trẻ gầy sút chậm lên cân sốt âm ỉ kéo dài từng đợt'],
    'ten': 'dị vật đường thở bỏ quên ở trẻ'},
    {   'bien_the_chan_doan': [   'Viêm phế quản co thắt cấp tính ở trẻ em mức độ trung bình.',
                              'Viêm phế quản co thắt khởi phát sau nhiễm virus đường hô hấp trên.',
                              'Viêm phế quản co thắt tái diễn ở trẻ nhỏ có cơ địa dị ứng.',
                              'Viêm phế quản co thắt mức độ nhẹ đáp ứng tốt với thuốc khí dung giãn phế quản.',
                              'Theo dõi viêm phế quản co thắt cần theo dõi tiến triển thành hen phế quản nhũ nhi.',
                              'Đợt cấp viêm phế quản co thắt chưa có biến chứng suy hô hấp.'],
    'bien_the_ke_hoach': [   'Cho trẻ khí dung thuốc giãn phế quản Salbutamol liều theo cân nặng đánh giá đáp ứng sau '
                             '20 phút, hút rửa mũi sạch bằng nước muối sinh lý, uống đủ nước làm loãng đờm và theo dõi '
                             'sát nhịp thở.',
                             'Thực hiện test thử giãn phế quản bằng khí dung Salbutamol 2,5mg pha nước muối sinh lý, '
                             'nếu cải thiện rõ có thể kê bình xịt định liều qua buồng đệm (MDI + Spacer) tại nhà.',
                             'Cân nhắc dùng một đợt ngắn Prednisolone đường uống 1-2 mg/kg/ngày trong 3-5 ngày nếu trẻ '
                             'khò khè co thắt nặng đáp ứng chậm với khí dung đơn thuần.',
                             'Không lạm dụng kháng sinh khi không có bằng chứng bội nhiễm vi khuẩn (sốt cao CRP tăng '
                             'bạch cầu tăng), giữ ấm vùng cổ ngực và tránh khói thuốc lá bụi bặm.',
                             'Hướng dẫn phụ huynh đếm nhịp thở của trẻ khi ngủ yên và nhận biết các dấu hiệu cần nhập '
                             'viện cấp cứu như thở rút lõm ngực sâu tím môi bỏ bú.',
                             'Theo dõi số lần tái phát khò khè trong năm để đánh giá chỉ số nguy cơ hen (API) và xem '
                             'xét dự phòng nếu trẻ khò khè tái đi tái lại trên 3 lần.'],
    'bien_the_kham': [   'Trẻ tỉnh táo SpO2 96% khí phòng, nhịp thở 44 lần/phút, co kéo nhẹ cơ liên sườn, nghe phổi có '
                         'nhiều ran rít và ran ngáy lan toả hai phế trường ở thì thở ra, không có ran nổ khu trú.',
                         'Nhịp thở 40 l/p, thì thở ra kéo dài nghe rõ tiếng rít cò cử không cần ống nghe, đặt ống nghe '
                         'thấy ran rít ran ngáy rải rác đều cả hai bên phổi, phổi không có vùng giảm thông khí.',
                         'Trẻ sốt nhẹ 37,9 độ C, mũi chảy dịch trong loãng, họng sung huyết nhẹ, khám phổi có ran ngáy '
                         'to hạt và ran rít hai bên phế trường, phản xạ ho tốt khạc ra ít đờm trắng trong.',
                         'Khám thấy trẻ hơi thở nhanh nông 46 l/p, hõm trên ức rút nhẹ lúc hít vào, SpO2 95%, nghe '
                         'phổi đầy tiếng ran rít thì thở ra đáp ứng cải thiện rõ rệt sau một cữ khí dung giãn phế '
                         'quản.',
                         'Lồng ngực hơi phồng cân đối, không tím tái đầu chi, tiếng tim đều rõ 120 l/p, phổi có tiếng '
                         'ran rít rải rác hai bên kèm vài ran ẩm to hạt đường thở lớn.',
                         'Trẻ chơi ngoan giữa các cơn ho, nhịp thở 38 l/p, nghe phổi thông khí đều hai phế trường xen '
                         'lẫn tiếng ran ngáy ran rít lan tỏa, đáp ứng tốt với thuốc giãn phế quản khí dung.'],
    'chan_doan': 'Viêm phế quản co thắt cấp tính ở trẻ em mức độ trung bình.',
    'chinh': [   'ho từng cơn kèm tiếng thở khò khè rít rõ rệt đặc biệt ở thì thở ra khởi phát sau nhiễm siêu vi hô '
                 'hấp',
                 'thở nhanh nhẹ rút lõm nhẹ cơ liên sườn khi trẻ quấy khóc hoặc bú sữa',
                 'chảy nước mũi trong nghẹt mũi sốt nhẹ trước khi xuất hiện khò khè 1-2 ngày'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'hô hấp',
    'ke_hoach': 'Cho trẻ khí dung thuốc giãn phế quản Salbutamol (Ventolin) liều theo cân nặng đánh giá đáp ứng sau 20 '
                'phút, hút rửa mũi sạch bằng nước muối sinh lý, uống đủ nước làm loãng đờm và theo dõi sát nhịp thở '
                'tại nhà hoặc nội trú.',
    'kham': 'Trẻ tỉnh táo SpO2 96% khí phòng, nhịp thở 44 lần/phút, co kéo nhẹ cơ liên sườn, nghe phổi có nhiều ran '
            'rít và ran ngáy lan toả hai phế trường ở thì thở ra, không có ran nổ khu trú.',
    'nhom': 'nhi',
    'phu': [   'trẻ có thể nôn trớ đờm nhớt sau cơn ho dữ dội',
               'ăn bú kém hơn bình thường do mệt và nghẹt thở nhẹ',
               'lồng ngực hơi căng nhẹ do ứ khí phế quản'],
    'ten': 'viêm phế quản co thắt ở trẻ'},
    {   'bien_the_chan_doan': [   'Giãn phế quản bẩm sinh khu trú thùy dưới phổi trái giai đoạn bội nhiễm.',
                              'Giãn phế quản bẩm sinh ở trẻ em có ngón tay dùi trống và suy dinh dưỡng.',
                              'Giãn phế quản bẩm sinh dạng túi lan tỏa hai đáy phổi.',
                              'Đợt cấp bội nhiễm trên nền giãn phế quản bẩm sinh ở trẻ nhỏ.',
                              'Theo dõi giãn phế quản bẩm sinh nghi do hội chứng rối loạn vận động lông chuyển nguyên '
                              'phát.',
                              'Giãn phế quản bẩm sinh khu trú cần đánh giá chỉ định phẫu thuật cắt thùy phổi.'],
    'bien_the_ke_hoach': [   'Chụp CT ngực độ phân giải cao tìm hình ảnh giãn phế quản dạng ống hoặc dạng túi, cấy đờm '
                             'định danh vi khuẩn, phối hợp kháng sinh diệt khuẩn theo kháng sinh đồ và vật lý trị liệu '
                             'dẫn lưu tư thế hàng ngày.',
                             'Làm xét nghiệm định lượng kháng thể miễn dịch IgG IgA IgM IgE và đo điện giải mồ hôi để '
                             'loại trừ suy giảm miễn dịch bẩm sinh hoặc xơ nang tụy phối hợp.',
                             'Điều trị đợt cấp bùng phát nhiễm khuẩn bằng kháng sinh đường uống hoặc tĩnh mạch '
                             'Amoxicillin-Clavulanate hay Cefuroxime đủ 14 ngày dựa theo kết quả cấy đờm.',
                             'Hướng dẫn gia đình kỹ thuật vỗ rung lồng ngực kết hợp dẫn lưu tư thế (nằm dốc đầu thấp) '
                             'mỗi sáng và tối giúp tống xuất sạch đờm mủ ứ đọng trong các túi giãn.',
                             'Tiêm phòng đầy đủ vắc xin phế cầu và cúm mùa hàng năm để giảm thiểu tối đa các đợt bội '
                             'nhiễm cấp tính làm nặng thêm tổn thương phế quản.',
                             'Hội chẩn Ngoại Lồng ngực Nhi cân nhắc phẫu thuật cắt bỏ thùy phổi tổn thương nếu giãn '
                             'phế quản khu trú một thùy gây ho ra máu tái diễn hoặc nhiễm trùng không kiểm soát.'],
    'bien_the_kham': [   'Thể trạng trẻ gầy nhỏ, đầu ngón tay hơi khum hình dùi trống độ 1, nghe phổi thấy ran ẩm to '
                         'hạt và ran nổ cố định kéo dài ở thùy dưới phổi trái kèm giảm thông khí nhẹ đáy trái.',
                         'Khám hô hấp thấy lồng ngực hơi gồ bên phải, gõ đục nhẹ vùng đáy phổi phải, nghe phổi có ổ '
                         'ran ẩm dày đặc cố định không mất đi sau khi ho khạc đờm.',
                         'Trẻ ho khạc ra chén đờm màu vàng xanh đặc sánh mùi hôi nhẹ, SpO2 94% khí phòng, các ngón tay '
                         'biến dạng dùi trống nhẹ, lồng ngực rút lõm nhẹ khi gắng sức.',
                         'Nghe phổi phát hiện nhiều ran nổ to hạt và ran ngáy tập trung ở vùng phân thùy đáy sau phổi '
                         'hai bên, tim đều nghe rõ không thấy đảo ngược phủ tạng (loại trừ Kartagener).',
                         'Dấu hiệu nhiễm trùng hô hấp mạn tính: cân nặng chiều cao dưới bách phân vị thứ 10, ho khạc '
                         'đờm mạn tính, nghe phổi trái nhiều tiếng ran ẩm rải rác cố định.',
                         'Trẻ có nhịp thở 30 l/p khi nghỉ, biến dạng nhẹ lồng ngực hình ức gà, vùng đáy phổi trái rì '
                         'rào phế nang giảm rõ kèm ran ẩm nhỏ và trung bình hạt.'],
    'chan_doan': 'Giãn phế quản bẩm sinh khu trú thùy dưới phổi trái giai đoạn bội nhiễm.',
    'chinh': [   'ho khạc lượng nhiều dịch tiết mủ xanh vàng vào sáng sớm ngay sau khi ngủ dậy',
                 'tình trạng viêm phổi thùy tái diễn nhiều lần cố định ở một bên đáy phổi từ nhỏ',
                 'ho khạc ra tia máu hoặc vệt máu đỏ tươi lẫn trong chất khạc'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'hô hấp',
    'ke_hoach': 'Chụp CT ngực độ phân giải cao (HRCT) tìm hình ảnh giãn phế quản dạng ống hoặc dạng túi, cấy đờm định '
                'danh vi khuẩn, phối hợp kháng sinh diệt khuẩn theo kháng sinh đồ và vật lý trị liệu dẫn lưu tư thế '
                'hàng ngày.',
    'kham': 'Thể trạng trẻ gầy nhỏ, đầu ngón tay hơi khum hình dùi trống độ 1, nghe phổi thấy ran ẩm to hạt và ran nổ '
            'cố định kéo dài ở thùy dưới phổi trái kèm giảm thông khí nhẹ đáy trái.',
    'nhom': 'nhi',
    'phu': [   'chất khạc nhổ vào cốc để lắng tự tách thành ba lớp bọt dịch trong và cặn mủ',
               'hơi thở có mùi hôi tanh đặc trưng của ổ ứ đọng phế quản kéo dài',
               'giảm khả năng gắng sức chạy nhảy thở dốc nhanh hơn bạn bè cùng trang lứa'],
    'ten': 'giãn phế quản bẩm sinh ở trẻ'},
    {   'bien_the_chan_doan': [   'Nhiễm trùng huyết sơ sinh khởi phát muộn nghi ngờ đường vào từ da hoặc tiêu hoá.',
                              'Nhiễm trùng sơ sinh muộn biến chứng viêm màng não mủ sơ sinh.',
                              'Nhiễm trùng sơ sinh muộn thể suy hô hấp tuần hoàn nặng nghi do tụ cầu vàng.',
                              'Nhiễm khuẩn sơ sinh muộn khởi phát tại cộng đồng chưa rõ ổ nhiễm trùng nguyên phát.',
                              'Theo dõi nhiễm trùng huyết sơ sinh muộn có dấu hiệu viêm ruột hoại tử sớm.',
                              'Nhiễm trùng sơ sinh muộn nghi ngờ do liên cầu khuẩn nhóm B thể muộn.'],
    'bien_the_ke_hoach': [   'Nhập viện cấp cứu khoa Hồi sức Sơ sinh, lấy máu cấy 2 vị trí, công thức máu, CRP, '
                             'Procalcitonin, chọc dò dịch não tủy loại trừ viêm màng não, khởi trị kháng sinh tĩnh '
                             'mạch ngay lập tức bằng Vancomycin phối hợp Cefotaxime hoặc Meropenem.',
                             'Thiết lập đường truyền tĩnh mạch nuôi dưỡng toàn phần, giữ trẻ nằm lồng ấp ổn định thân '
                             'nhiệt, hỗ trợ thở áp lực dương liên tục CPAP nếu có cơn ngưng thở hoặc thở rên.',
                             'Làm đầy đủ xét nghiệm bilan nhiễm trùng: công thức máu xem tỷ lệ bạch cầu non/tổng bạch '
                             'cầu (I/T), CRP, Procalcitonin, cấy nước tiểu qua chọc hút trên xương mu và cấy dịch não '
                             'tủy.',
                             'Truyền dịch điện giải và vận mạch Dopamine hoặc Dobutamine nếu trẻ có biểu hiện sốc '
                             'nhiễm trùng tụt huyết áp thời gian đổ đầy mao mạch kéo dài.',
                             'Phối hợp kháng sinh phổ rộng Cefotaxime kết hợp Ampicillin hoặc Gentamicin cho trẻ nhiễm '
                             'trùng từ cộng đồng, điều chỉnh liều theo chức năng thận và kết quả kháng sinh đồ.',
                             'Theo dõi sát diễn tiến tri giác, cân bằng dịch xuất nhập, đường huyết và khí máu động '
                             'mạch mỗi 4-6 giờ trong giai đoạn nguy kịch.'],
    'bien_the_kham': [   'Trẻ sơ sinh 15 ngày tuổi vẻ mặt nhiễm trùng li bì đáp ứng kích thích kém, thân nhiệt 38,6 độ '
                         'C, da nổi vân tím toàn thân, CRT 4 giây, nhịp thở nhanh 64 l/p có cơn rên nhẹ thì thở ra, '
                         'bụng hơi chướng mềm.',
                         'Trẻ 12 ngày tuổi hạ thân nhiệt 35,8 độ C, trương lực cơ giảm nhẽo mềm, bú kém sặc sữa, nhịp '
                         'tim nhanh 175 lần/phút, chân rốn khô sạch nhưng vùng da bẹn có vài mụn mủ nhỏ.',
                         'Dấu hiệu cảnh báo nhiễm khuẩn huyết muộn: trẻ quấy khóc rên yếu ớt, da tái xám nổi bông, '
                         'thóp trước hơi căng phồng nhẹ, gan sờ thấy 3cm dưới bờ sườn phải.',
                         'Bé 20 ngày tuổi sốt 38,9 độ C kèm các cơn ngưng thở ngắn 10 giây, SpO2 tụt xuống 89%, bụng '
                         'chướng căng gõ vang nhiều hơi, nhu động ruột giảm.',
                         'Khám sơ sinh thấy vẻ mặt lờ đờ giảm vận động tự nhiên, phản xạ bú mút yếu hẳn, xuất hiện các '
                         'chấm xuất huyết nhỏ rải rác ngực bụng, mạch quay nhanh nhẹ.',
                         'Trẻ li bì khó đánh thức, vàng da tăng nhanh đến cẳng chân kèm phân nhạt màu thoáng qua, thở '
                         'nhanh co kéo cơ liên sườn độ 2, lách mấp mé bờ sườn trái.'],
    'chan_doan': 'Nhiễm trùng huyết sơ sinh khởi phát muộn nghi ngờ đường vào từ da hoặc tiêu hoá.',
    'chinh': [   'trẻ sơ sinh trên 7 ngày tuổi đột ngột bú kém bỏ bú hoặc nôn trớ bụng chướng',
                 'rối loạn thân nhiệt sốt cao trên 38 độ hoặc hạ thân nhiệt dưới 36 độ C',
                 'li bì giảm phản xạ sơ sinh thở rên rỉ hoặc xuất hiện các cơn ngưng thở tím tái'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Nhập viện cấp cứu khoa Hồi sức Sơ sinh, lấy máu cấy 2 vị trí, công thức máu, CRP, Procalcitonin, chọc '
                'dò dịch não tủy loại trừ viêm màng não, khởi trị kháng sinh tĩnh mạch ngay lập tức bằng Vancomycin '
                'phối hợp Cefotaxime hoặc Meropenem.',
    'kham': 'Trẻ sơ sinh 15 ngày tuổi vẻ mặt nhiễm trùng li bì đáp ứng kích thích kém, thân nhiệt 38,6 độ C, da nổi '
            'vân tím toàn thân, CRT 4 giây, nhịp thở nhanh 64 l/p có cơn rên nhẹ thì thở ra, bụng hơi chướng mềm.',
    'nhom': 'nhi',
    'phu': [   'da nổi vân tím lạnh đầu chi thời gian phục hồi màu da (CRT) kéo dài trên 3 giây',
               'vàng da xuất hiện mới hoặc tăng đậm bất thường kèm gan lách to',
               'cơ thể co giật thóp phồng nếu có biến chứng viêm màng não kèm theo'],
    'ten': 'nhiễm trùng sơ sinh muộn'},
    {   'bien_the_chan_doan': [   'Sốt co giật phức tạp ở trẻ em dạng cục bộ kéo dài kèm yếu nửa người sau cơn.',
                              'Sốt co giật phức tạp tái phát nhiều cơn trong 24 giờ trên nền viêm đường hô hấp trên.',
                              'Theo dõi sốt co giật phức tạp cần phân biệt với viêm màng não hoặc viêm não cấp.',
                              'Sốt co giật phức tạp kéo dài gần mức trạng thái động kinh do sốt.',
                              'Sốt co giật phức tạp ở trẻ dưới 12 tháng tuổi nguy cơ cao nhiễm trùng thần kinh.',
                              'Sốt co giật phức tạp nghi ngờ tiến triển thành động kinh cục bộ.'],
    'bien_the_ke_hoach': [   'Cấp cứu cắt cơn ngay bằng Diazepam bơm hậu môn hoặc Midazolam tĩnh mạch nếu còn giật, hạ '
                             'sốt tích cực bằng Paracetamol kết hợp lau mát, theo dõi sát tri giác và làm điện não đồ '
                             'EEG sau cơn loại trừ viêm não màng não.',
                             'Nhập viện theo dõi nội trú tối thiểu 24 giờ, đặt đường truyền tĩnh mạch lấy máu xét '
                             'nghiệm công thức máu, CRP, đường huyết và điện giải đồ loại trừ hạ đường huyết hạ natri '
                             'máu.',
                             'Cân nhắc chỉ định chọc dò dịch não tủy nếu trẻ dưới 12 tháng tuổi hoặc nghi ngờ dấu hiệu '
                             'kích thích màng não, hoặc đã dùng kháng sinh trước đó che lấp triệu chứng.',
                             'Chỉ định đo điện não đồ EEG ngoài cơn (sau khi hết sốt 1-2 tuần) và chụp MRI sọ não nếu '
                             'có dấu hiệu thần kinh khu trú kéo dài hoặc liệt Todd không hồi phục.',
                             'Tìm và điều trị triệt để nguyên nhân gây sốt (như viêm tai giữa cấp hoặc viêm họng vi '
                             'khuẩn), dặn dò cha mẹ tuyệt đối không nhét vật cứng vào miệng trẻ khi đang co giật.',
                             'Hướng dẫn gia đình kỹ năng xử trí cấp cứu ban đầu khi trẻ co giật tại nhà (đặt nằm '
                             'nghiêng an toàn, nới lỏng quần áo) và trang bị thuốc cắt cơn Diazepam đặt hậu môn dự '
                             'phòng.'],
    'bien_the_kham': [   'Trẻ vừa qua cơn co giật nửa người bên phải kéo dài 20 phút, hiện tại tri giác lơ mơ chậm '
                         'chạp nhưng gọi hỏi biết mở mắt, nhiệt độ 39,2 độ C, cổ mềm không có dấu hiệu màng não, yếu '
                         'nhẹ tay phải sau cơn.',
                         'Bé nhập viện trong cơn co giật thứ hai chỉ cách cơn đầu 4 giờ trong cùng một ngày, tay chân '
                         'bên trái giật liên hồi mắt trợn lệch sang trái, sốt 39,5 độ C do viêm amidan mủ.',
                         'Khám sau khi được cắt cơn bằng diazepam: trẻ ngủ gà nhưng đánh thức được, đồng tử hai bên '
                         'đều phản xạ ánh sáng tốt, thóp phẳng không căng, không có dấu cứng gáy.',
                         'Ghi nhận cơn co giật toàn thân kéo dài 18 phút làm trẻ tím tái nhẹ trong cơn, hiện tại SpO2 '
                         '97% tự thở đều, họng đỏ sung huyết nhiều, phổi không có ran.',
                         'Trẻ 2 tuổi có 3 cơn co giật ngắn liên tiếp trong vòng 12 giờ đầu của đợt sốt cao 39 độ C, '
                         'giữa các cơn trẻ tỉnh táo nhưng kích thích quấy khóc nhiều, tai phải màng nhĩ đỏ phồng.',
                         'Khám thần kinh sau cơn giật phức tạp không phát hiện dấu màng não Kernig Brudzinski, sức cơ '
                         'tứ chi đều nhau sau 2 giờ theo dõi, cần loại trừ nhiễm khuẩn thần kinh trung ương.'],
    'chan_doan': 'Sốt co giật phức tạp ở trẻ em dạng cục bộ kéo dài kèm yếu nửa người sau cơn.',
    'chinh': [   'cơn co giật xảy ra khi trẻ sốt cao nhưng cơn giật kéo dài trên 15 phút không tự cắt',
                 'cơn co giật mang tính chất cục bộ chỉ giật một bên tay chân hoặc một nửa mặt',
                 'cơn co giật tái phát nhiều hơn 1 lần trong vòng 24 giờ cùng một đợt sốt'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Cấp cứu cắt cơn ngay bằng Diazepam bơm hậu môn hoặc Midazolam tĩnh mạch nếu còn giật, hạ sốt tích cực '
                'bằng Paracetamol kết hợp lau mát, theo dõi sát tri giác và làm điện não đồ EEG sau cơn loại trừ viêm '
                'não màng não hoặc động kinh.',
    'kham': 'Trẻ vừa qua cơn co giật nửa người bên phải kéo dài 20 phút, hiện tại tri giác lơ mơ chậm chạp nhưng gọi '
            'hỏi biết mở mắt, nhiệt độ 39,2 độ C, cổ mềm không có dấu hiệu màng não, yếu nhẹ tay phải sau cơn (liệt '
            'Todd).',
    'nhom': 'nhi',
    'phu': [   'trẻ rơi vào trạng thái lơ mơ mệt mỏi sâu hoặc yếu thoáng qua nửa người sau cơn (liệt Todd)',
               'nhiệt độ cơ thể đo được thường cao trên 38,5 độ C kèm ổ nhiễm trùng hô hấp hoặc tiêu hoá',
               'gia đình có thể có người thân từng bị co giật do sốt hoặc động kinh'],
    'ten': 'sốt co giật phức tạp ở trẻ'},
    {   'bien_the_chan_doan': [   'Đau nửa đầu liệt nửa người thể gia đình hoặc đơn lẻ ở trẻ em.',
                              'Đau nửa đầu Migraine có tiền triệu vận động ở trẻ lớn.',
                              'Theo dõi đau nửa đầu liệt nửa người cần loại trừ khẩn cấp cơn thiếu máu não thoáng qua '
                              'TIA.',
                              'Đau nửa đầu liệt nửa người đơn phát thể tái phát ở trẻ em.',
                              'Đau nửa đầu có tiền triệu liệt nửa người biến chứng rối loạn ngôn ngữ thoáng qua.',
                              'Đau nửa đầu liệt nửa người thể gia đình liên quan đột biến kênh ion.'],
    'bien_the_ke_hoach': [   'Chụp MRI sọ não và mạch máu não MRA khẩn cấp để loại trừ đột quỵ thiếu máu não cục bộ '
                             'hoặc dị dạng mạch máu não, dùng thuốc giảm đau Ibuprofen trong cơn cấp và hội chẩn Thần '
                             'kinh Nhi.',
                             'Làm điện não đồ EEG loại trừ cơn động kinh cục bộ kèm liệt sau cơn, xét nghiệm bilan '
                             'đông máu tầm soát rối loạn tăng đông máu gây tắc mạch não ở trẻ em.',
                             'Điều trị cắt cơn đau đầu cấp tính trong phòng tối yên tĩnh bằng Ibuprofen 10 mg/kg hoặc '
                             'Paracetamol 15 mg/kg phối hợp chống nôn Ondansetron; tuyệt đối tránh dùng thuốc nhóm '
                             'Triptan hoặc Ergotamine.',
                             'Chỉ định thuốc điều trị dự phòng cơn tái phát như Flunarizine, Topiramate hoặc Verapamil '
                             'nếu tần suất cơn xuất hiện nhiều hơn 2 lần mỗi tháng hoặc liệt nặng kéo dài.',
                             'Xét nghiệm giải trình tự gen tầm soát đột biến các gen CACNA1A, ATP1A2, SCN1A đối với '
                             'thể đau nửa đầu liệt nửa người có tính chất gia đình.',
                             'Hướng dẫn gia đình và nhà trường nhận biết sớm các yếu tố khởi phát cơn như thiếu ngủ '
                             'căng thẳng ánh sáng chói hoặc chấn thương đầu nhẹ để phòng tránh.'],
    'bien_the_kham': [   'Trẻ tỉnh táo nhưng vẻ mặt đau đớn nhắm mắt tránh ánh sáng, khám thấy giảm sức cơ tay và chân '
                         'bên trái (3/5) kèm cảm giác tê bì nửa người trái, đồng tử hai bên đều 2,5mm, tim phổi bình '
                         'thường, không sốt.',
                         'Bé trai 10 tuổi than đau nhức đầu bên trái dữ dội kèm mờ mắt thoáng qua, khám thần kinh ghi '
                         'nhận liệt nhẹ dây VII trung ương bên phải và yếu tay phải sức cơ 4/5.',
                         'Trẻ nói ngọng khó tìm từ diễn đạt kết hợp tê yếu nửa người bên phải kéo dài 45 phút ngay sau '
                         'khi xuất hiện quầng sáng lấp lánh trước mắt, sau đó bùng phát cơn đau đầu dữ dội.',
                         'Khám trong giai đoạn hồi phục: sức cơ nửa người bên yếu đã cải thiện lên 4+/5, phản xạ gân '
                         'xương hai bên còn hơi chênh lệch nhẹ, trẻ vẫn còn sợ ánh sáng và buồn nôn.',
                         'Trẻ không sốt không có dấu hiệu cứng gáy, huyết áp ổn định 105/65 mmHg, khám đáy mắt gai thị '
                         'bờ rõ không phù gai, yếu nửa người bên trái hoàn toàn hồi phục sau 4 giờ.',
                         'Cơn yếu nửa người diễn tiến tuần tự từ tê ngón tay lan lên cánh tay mặt rồi đến chân trong '
                         'vòng 20 phút trước khi đau nửa đầu bên đối diện.'],
    'chan_doan': 'Đau nửa đầu liệt nửa người thể gia đình hoặc đơn lẻ ở trẻ em.',
    'chinh': [   'cơn đau đầu dữ dội một bên đầu kiểu mạch đập kèm buồn nôn sợ ánh sáng và tiếng ồn',
                 'yếu hoặc liệt hẳn một nửa người thoáng qua (tay và chân cùng bên) xuất hiện trước hoặc trong cơn đau '
                 'đầu',
                 'tê bì kim châm nửa mặt và nửa thân người hoặc nói khó thất ngôn thoáng qua'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'thần kinh',
    'ke_hoach': 'Chụp MRI sọ não và mạch máu não MRA khẩn cấp để loại trừ đột quỵ thiếu máu não cục bộ hoặc dị dạng '
                'mạch máu não, dùng thuốc giảm đau Ibuprofen hoặc Paracetamol trong cơn cấp và hội chẩn Thần kinh Nhi '
                'xem xét điều trị dự phòng bằng Flunarizine.',
    'kham': 'Trẻ tỉnh táo nhưng vẻ mặt đau đớn nhắm mắt tránh ánh sáng, khám thấy giảm sức cơ tay và chân bên trái '
            '(3/5) kèm cảm giác tê bì nửa người trái, đồng tử hai bên đều 2,5mm, tim phổi bình thường, không sốt.',
    'nhom': 'nhi',
    'phu': [   'tiền triệu rối loạn thị giác thấy vệt sáng nhấp nháy hoặc mờ một bên thị trường',
               'triệu chứng yếu liệt hồi phục hoàn toàn sau vài giờ đến vài ngày hết cơn đau đầu',
               'tiền sử gia đình có bố mẹ hoặc anh chị em mắc chứng đau nửa đầu tương tự'],
    'ten': 'đau nửa đầu liệt nửa người ở trẻ'},
    {   'bien_the_chan_doan': [   'Hạ canxi máu sơ sinh muộn do suy cận giáp thoáng qua hoặc bẩm sinh.',
                              'Hạ canxi máu sơ sinh gây cơn tetany và co giật trên nền suy cận giáp.',
                              'Theo dõi suy cận giáp sơ sinh nghi ngờ hội chứng mất đoạn 22q11.2 (DiGeorge).',
                              'Hạ canxi máu sơ sinh kèm hạ magie máu thứ phát do rối loạn cận giáp.',
                              'Hạ canxi máu sơ sinh muộn liên quan chế độ sữa công thức quá tải phosphat.',
                              'Cơn co giật do hạ canxi máu cấp tính ở trẻ sơ sinh đủ tháng.'],
    'bien_the_ke_hoach': [   'Xét nghiệm khẩn cấp canxi toàn phần, canxi ion hóa, phospho, magiê máu và hormone tuyến '
                             'cận giáp PTH, truyền tĩnh mạch chậm dung dịch Canxi Gluconate 10% dưới theo dõi nhịp tim '
                             'trên monitor liên tục.',
                             'Tiêm tĩnh mạch cực chậm (trên 10-15 phút) dung dịch Canxi Gluconate 10% pha loãng tỷ lệ '
                             '1:1 với Glucose 5% liều 1-2 ml/kg khi có co giật hoặc co thắt thanh quản, ngừng ngay nếu '
                             'nhịp tim chậm dưới 100 l/p.',
                             'Kiểm tra và điều chỉnh đồng thời nồng độ Magie máu nếu thấp bằng Magie Sulfat tiêm bắp '
                             'hoặc truyền tĩnh mạch vì hạ magie làm ức chế tiết và tác dụng của PTH.',
                             'Chuyển sang duy trì Canxi nguyên tố đường uống liều 50-75 mg/kg/ngày kết hợp Calcitriol '
                             '(Vitamin D dạng hoạt động 1,25-(OH)2D3) khi trẻ hết triệu chứng cấp và bú được.',
                             'Chỉ định siêu âm tim Doppler màu và xét nghiệm di truyền FISH tìm đột biến mất đoạn '
                             '22q11.2 nếu phát hiện bất thường hình thái khuôn mặt hoặc dị tật tim bẩm sinh kèm theo.',
                             'Tư vấn mẹ chuyển sang bú sữa mẹ hoàn toàn hoặc dùng sữa công thức có tỷ lệ canxi/phospho '
                             'thấp hợp lý hơn để hạn chế tình trạng tăng phosphat máu.'],
    'bien_the_kham': [   'Trẻ sơ sinh kích thích run giật đầu chi liên tục dù đang nằm yên, trương lực cơ tăng nhẹ, gõ '
                         'nhẹ vùng trước tai gây co giật khóe miệng cùng bên, nghe tim rõ đều, thóp phẳng.',
                         'Trẻ 10 ngày tuổi nhập viện vì cơn co giật co cứng toàn thân kéo dài 3 phút hết giật không '
                         'sốt, khám thấy các ngón tay co quắp chụm lại, thở rít nhẹ lúc khóc.',
                         'Khám trẻ sơ sinh thấy các cơn giật rung chi thô bạo nhưng vẫn tỉnh táo không mất ý thức '
                         'trong lúc giật (khác động kinh thật), da niêm hồng hào không vàng da.',
                         'Trẻ có dấu hiệu tăng kích thích thần kinh cơ rõ: chỉ cần chạm nhẹ tã là toàn thân giật nẩy '
                         'mình, dấu Chvostek dương tính rõ, nghe tim có tiếng thổi tâm thu nghi thông liên thất.',
                         'Trẻ bú sữa công thức giàu phospho xuất hiện run giật hai tay và cằm liên tục, nhịp tim 160 '
                         'l/p đều, phổi trong không ran, không có dấu hiệu nhiễm trùng.',
                         'Đo điện tâm đồ tại giường thấy khoảng QTc kéo dài 0,48 giây, trẻ kích thích vật vã, sờ nắn '
                         'cơ bắp căng cứng và có cơn co cứng cơ bàn chân.'],
    'chan_doan': 'Hạ canxi máu sơ sinh muộn do suy cận giáp thoáng qua hoặc bẩm sinh.',
    'chinh': [   'run giật cơ tự phát kích thích quá mức tăng phản xạ hoặc cơn co giật toàn thân ở trẻ sơ sinh',
                 'cơn co thắt thanh quản gây thở rít hoặc cơn ngưng thở tím tái đột ngột',
                 'co cứng bàn tay bàn chân tư thế bàn tay đỡ đẻ (dấu hiệu Trousseau) hoặc co giật cơ mặt khi gõ'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'nội tiết - chuyển hoá',
    'ke_hoach': 'Xét nghiệm khẩn cấp canxi toàn phần, canxi ion hóa, phospho, magiê máu và hormone tuyến cận giáp PTH, '
                'truyền tĩnh mạch chậm dung dịch Canxi Gluconate 10% dưới theo dõi nhịp tim trên monitor liên tục.',
    'kham': 'Trẻ sơ sinh kích thích run giật đầu chi liên tục dù đang nằm yên, trương lực cơ tăng nhẹ, gõ nhẹ vùng '
            'trước tai gây co giật khóe miệng cùng bên (dấu hiệu Chvostek dương tính), nghe tim rõ đều, thóp phẳng.',
    'nhom': 'nhi',
    'phu': [   'trẻ bú kém nôn trớ kích thích khóc thét không dỗ được',
               'mẹ có tiền sử tiểu đường trước sinh hoặc trẻ có dị tật tim vùng thân động mạch (hội chứng DiGeorge)',
               'khoảng QT kéo dài trên điện tâm đồ có nguy cơ loạn nhịp tim'],
    'ten': 'hạ canxi máu sơ sinh do suy cận giáp'},
    {   'bien_the_chan_doan': [   'Cơn tán huyết cấp do thiếu men G6PD ở trẻ em.',
                              'Thiếu máu tán huyết cấp nội mạch ở trẻ thiếu men G6PD sau dùng thuốc.',
                              'Cơn tan máu cấp tính do thiếu G6PD khởi phát sau tiếp xúc băng phiến long não.',
                              'Cơn tán huyết cấp mức độ nặng ở trẻ nam thiếu men G6PD di truyền liên kết NST X.',
                              'Theo dõi tán huyết cấp do thiếu men G6PD có nguy cơ tổn thương thận cấp do hemoglobin '
                              'niệu.',
                              'Thiếu máu huyết tán cấp ở trẻ em cần định lượng lại hoạt độ G6PD sau đợt hồi phục.'],
    'bien_the_ke_hoach': [   'Ngừng ngay lập tức tác nhân kích phát nghi ngờ, làm xét nghiệm công thức máu, hồng cầu '
                             'lưới, bilirubin gián tiếp, LDH, test Coombs trực tiếp âm tính, truyền dịch kiềm hoá nước '
                             'tiểu và truyền hồng cầu lắng nếu thiếu máu nặng.',
                             'Truyền khối hồng cầu lắng nhóm máu phù hợp khẩn cấp khi nồng độ Hemoglobin tụt xuống '
                             'dưới 70 g/L hoặc có dấu hiệu suy tim mất bù do thiếu máu cấp.',
                             'Đảm bảo cung cấp đủ dịch truyền tĩnh mạch duy trì lượng nước tiểu dồi dào kết hợp kiềm '
                             'hóa nước tiểu nhẹ để phòng ngừa tắc ống thận cấp do huyết sắc tố lắng đọng.',
                             'Lưu ý xét nghiệm định lượng hoạt độ men G6PD có thể cho kết quả âm tính giả trong cơn '
                             'cấp do hồng cầu già bị vỡ hết chỉ còn hồng cầu non giàu men, cần hẹn thử lại sau 2-3 '
                             'tháng.',
                             'Cung cấp cho gia đình bản danh sách chi tiết các thuốc, thực phẩm (đậu tằm) và hóa chất '
                             '(băng phiến, thuốc nhuộm) tuyệt đối phải tránh suốt đời cho trẻ.',
                             'Bổ sung Acid folic đường uống trong giai đoạn phục hồi tủy xương tạo hồng cầu mới, theo '
                             'dõi kiểm tra lại công thức máu và chức năng thận sau 48-72 giờ.'],
    'bien_the_kham': [   'Bé trai da niêm nhợt nhạt rõ rệt kèm ánh vàng chanh ở củng mạc mắt và lòng bàn tay, nhịp tim '
                         'nhanh 148 lần/phút nghe có tiếng thổi cơ năng thiếu máu, nước tiểu thu trong bô màu nâu đỏ '
                         'sẫm như nước xá xị, lách mấp mé bờ sườn.',
                         'Trẻ nhập viện trong tình trạng mệt lả môi nhợt tái, kết mạc mắt vàng sậm nhanh chóng sau 24 '
                         'giờ uống thuốc cotrimoxazole điều trị viêm họng, mạch quay nhanh 150 l/p.',
                         'Khám thấy trẻ thiếu máu cấp mức độ nặng da xanh xao như tàu lá chuối, thở nhanh 40 l/p nhưng '
                         'phổi trong không ran, tã bỉm thấm nước tiểu màu nâu đen sậm.',
                         'Thân nhiệt 37,8 độ C, vàng da niêm mức độ trung bình kết hợp xanh xao rõ rệt (dấu hiệu vàng '
                         'da thiếu máu tán huyết), gan to nhẹ 1,5cm dưới bờ sườn mềm, không có ban xuất huyết.',
                         'Trẻ than đau tức vùng bụng quanh rốn và thắt lưng, tim đập mạnh dồn dập hồi hộp, phết máu '
                         'ngoại biên thấy hình ảnh hồng cầu bị cắn (bite cells) và thể Heinz.',
                         'Da và niêm mạc dưới lưỡi nhợt nhạt nặng kèm vàng mắt nhẹ, huyết áp ổn định 90/60 mmHg, trẻ '
                         'tiếp xúc chậm do thiếu oxy mô vì hemoglobin tụt nhanh.'],
    'chan_doan': 'Cơn tán huyết cấp do thiếu men G6PD ở trẻ em.',
    'chinh': [   'da xanh xao nhợt nhạt đột ngột kèm vàng da vàng mắt xuất hiện nhanh chỉ trong 1-2 ngày',
                 'nước tiểu sẫm màu đỏ nâu hoặc đen như nước xá xị hay nước chè đặc (đái huyết sắc tố)',
                 'mệt lả thở nhanh nhịp tim nhanh và đau bụng hoặc đau lưng sau khi tiếp xúc chất oxy hoá'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'huyết học',
    'ke_hoach': 'Ngừng ngay lập tức tác nhân kích phát nghi ngờ, làm xét nghiệm công thức máu, hồng cầu lưới, '
                'bilirubin gián tiếp, LDH, test Coombs trực tiếp âm tính, truyền dịch kiềm hoá nước tiểu và truyền '
                'hồng cầu lắng nếu thiếu máu nặng.',
    'kham': 'Bé trai da niêm nhợt nhạt rõ rệt kèm ánh vàng chanh ở củng mạc mắt và lòng bàn tay, nhịp tim nhanh 148 '
            'lần/phút nghe có tiếng thổi cơ năng thiếu máu, nước tiểu thu trong bô màu nâu đỏ sẫm như nước xá xị, lách '
            'mấp mé bờ sườn.',
    'nhom': 'nhi',
    'phu': [   'tiền sử mới ăn đậu tằm (fava), ngửi băng phiến (long não) hoặc uống thuốc hạ sốt kháng sinh sulfa',
               'trẻ sốt nhẹ kèm nôn ói biếng ăn đột ngột',
               'lách và gan có thể hơi to nhẹ nhưng hạch ngoại biên không sưng'],
    'ten': 'thiếu men G6PD gây tán huyết cấp ở trẻ'},
    {   'bien_the_chan_doan': [   'Bệnh lỵ amip cấp tính ở trẻ em do Entamoeba histolytica.',
                              'Bệnh lỵ amip đường ruột ở trẻ nhỏ mức độ trung bình chưa có biến chứng áp xe gan.',
                              'Theo dõi lỵ amip cấp tính ở trẻ em cần phân biệt với lỵ trực khuẩn Shigella.',
                              'Viêm đại tràng cấp do amip ở trẻ lớn đáp ứng tốt với điều trị đặc hiệu.',
                              'Bệnh lỵ amip bán cấp kéo dài gây rối loạn tiêu hoá và sút cân nhẹ.',
                              'Bệnh lỵ amip ở trẻ em chưa có dấu hiệu thủng ruột hay phình đại tràng nhiễm độc.'],
    'bien_the_ke_hoach': [   'Soi tươi phân tươi ấm trong vòng 30 phút tìm thể hoạt động ăn hồng cầu của Entamoeba '
                             'histolytica hoặc test kháng nguyên phân, điều trị diệt amip mô bằng Metronidazole đường '
                             'uống liều 30-50 mg/kg/ngày trong 7-10 ngày kết hợp thuốc diệt kén lòng ruột.',
                             'Chỉ định uống Metronidazole chia 3 lần mỗi ngày trong 10 ngày hoặc Tinidazole ngắn ngày '
                             'hơn (3-5 ngày), sau đó phối hợp Paromomycin hoặc Diloxanide furoate để diệt sạch bào '
                             'nang tránh tái phát.',
                             'Bù nước và điện giải đường uống bằng dung dịch Oresol áp lực thẩm thấu thấp sau mỗi lần '
                             'đi ngoài, tuyệt đối không dùng thuốc cầm tiêu chảy Loperamide vì gây ứ đọng độc tố và '
                             'phình đại tràng.',
                             'Làm siêu âm ổ bụng kiểm tra nhu mô gan để loại trừ biến chứng áp xe gan do amip nếu trẻ '
                             'có sốt cao trở lại hoặc đau tức vùng hạ sườn phải.',
                             'Hướng dẫn vệ sinh an toàn thực phẩm ăn chín uống sôi, rửa tay bằng xà phòng trước khi ăn '
                             'và sau khi đi vệ sinh, xử lý sạch sẽ phân trẻ để tránh lây lan cho người thân.',
                             'Xét nghiệm soi lại phân 3 mẫu cách ngày sau khi kết thúc liệu trình thuốc 2 tuần để chắc '
                             'chắn đã sạch hoàn toàn ký sinh trùng.'],
    'bien_the_kham': [   'Trẻ tỉnh táo không sốt (37,2 độ C), không có dấu hiệu mất nước nặng, khám bụng mềm ấn tức '
                         'nhẹ dọc khung đại tràng nhất là hố chậu phải, phân quan sát thấy lượng ít toàn nhầy đục '
                         'quyện vệt máu đỏ sẫm mùi tanh khẳm.',
                         'Bé 5 tuổi đau quặn vùng bụng dưới từng cơn trước khi vào nhà vệ sinh, đi ngoài 7-8 lần/ngày '
                         'nhưng lượng phân rất ít lẫn nhiều dịch nhầy hồng và tia máu, thân nhiệt 37,5 độ C.',
                         'Khám bụng không chướng, ấn hố chậu trái và dọc đại tràng sigma thấy thừng đại tràng hơi co '
                         'cứng và trẻ nhăn mặt kêu đau tức, niêm mạc hậu môn hơi sưng đỏ sung huyết do rặn nhiều.',
                         'Trẻ gầy sút nhẹ môi hơi khô, dấu véo da mất nhanh dưới 1 giây, không có biểu hiện nhiễm độc '
                         'toàn thân, gan không to và ấn kẽ sườn không đau.',
                         'Phân trong bô đặc sệt lổn nhổn lẫn nhiều mũi nhầy màu nâu đỏ như mứt mâm xôi mùi hôi đặc '
                         'trưng, bé vẫn chơi được giữa các cơn đau quặn bụng và mót rặn.',
                         'Thăm khám lâm sàng thấy trẻ không sốt cao rét run, tim phổi bình thường, vùng hố chậu phải '
                         'ấn đau sâu nhẹ cần lưu ý phân biệt với viêm ruột thừa thể đại tràng.'],
    'chan_doan': 'Bệnh lỵ amip cấp tính ở trẻ em do Entamoeba histolytica.',
    'chinh': [   'đi ngoài phân lỏng ít một nhiều lần trong ngày có lẫn nhiều chất nhầy và máu đỏ thẫm như nhựa mận '
                 'hoặc máu cá',
                 'đau quặn bụng dọc khung đại tràng đặc biệt vùng hố chậu phải và hạ vị trước mỗi lần đi tiêu',
                 'mót rặn hậu môn dữ dội muốn đi ngoài liên tục nhưng chỉ ra chút nhầy máu'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'truyền nhiễm',
    'ke_hoach': 'Soi tươi phân tươi ấm trong vòng 30 phút tìm thể hoạt động ăn hồng cầu của Entamoeba histolytica hoặc '
                'test kháng nguyên phân, điều trị diệt amip mô bằng Metronidazole đường uống liều 30-50 mg/kg/ngày '
                'trong 7-10 ngày kết hợp thuốc diệt kén lòng ruột.',
    'kham': 'Trẻ tỉnh táo không sốt (37,2 độ C), không có dấu hiệu mất nước nặng, khám bụng mềm ấn tức nhẹ dọc khung '
            'đại tràng nhất là hố chậu phải, phân quan sát thấy lượng ít toàn nhầy đục quyện vệt máu đỏ sẫm mùi tanh '
            'khẳm.',
    'nhom': 'nhi',
    'phu': [   'trẻ thường không sốt hoặc chỉ sốt nhẹ dưới 38 độ C (khác với lỵ trực khuẩn sốt cao)',
               'ăn uống kém buồn nôn chán ăn mệt mỏi',
               'hậu môn đỏ rát có thể sa trực tràng nhẹ nếu trẻ rặn quá nhiều'],
    'ten': 'bệnh lỵ amip ở trẻ em'},
    {   'bien_the_chan_doan': [   'Viêm da tã lót nhiễm nấm Candida albicans vùng bẹn ở trẻ nhũ nhi.',
                              'Nhiễm nấm Candida da vùng nếp bẹn thứ phát sau dùng kháng sinh đường uống.',
                              'Hăm tã bội nhiễm nấm men Candida có tổn thương sẩn vệ tinh điển hình.',
                              'Nhiễm nấm Candida da bẹn phối hợp nấm miệng tưa lưỡi ở trẻ nhũ nhi.',
                              'Viêm kẽ bẹn do nấm Candida phân biệt với viêm da tiếp xúc kích ứng tã lót.',
                              'Nhiễm nấm Candida da vùng sinh dục bẹn mức độ trung bình đáp ứng tốt thuốc bôi.'],
    'bien_the_ke_hoach': [   'Cạo vảy da vùng tổn thương soi tươi bằng KOH 10% tìm sợi tơ nấm giả và bào tử men, bôi '
                             'kem kháng nấm tại chỗ Nystatin hoặc Clotrimazole 1% mỗi lần thay tã trong 10-14 ngày, '
                             'giữ vùng tã khô thoáng.',
                             'Chỉ định bôi kem Miconazole 2% hoặc Ketoconazole 2% lớp mỏng ngày 2-3 lần sau khi vệ '
                             'sinh sạch, kết hợp bôi thêm lớp kem bảo vệ chứa kẽm oxit (Zinc oxide) phủ lên trên để '
                             'ngăn cách nước tiểu và phân.',
                             'Nếu trẻ có kèm tưa miệng (nấm Candida khoang miệng), phối hợp rơ miệng bằng dung dịch '
                             'Nystatin uống hoặc gel Miconazole đường miệng để cắt nguồn tái nhiễm từ đường tiêu hoá.',
                             'Hướng dẫn cha mẹ thay tã thường xuyên mỗi 2-3 giờ hoặc ngay sau khi trẻ đại tiện, rửa '
                             'nhẹ bằng nước ấm sạch tránh dùng khăn giấy ướt có cồn hay hương liệu, để trẻ thả rông '
                             'thoáng khí vài giờ mỗi ngày.',
                             'Tuyệt đối không tự ý bôi các loại kem trộn chứa corticoid mạnh (như bảy màu) vì làm suy '
                             'giảm miễn dịch tại chỗ khiến nấm bùng phát lan rộng và teo da.',
                             'Tái khám đánh giá lại sau 7-10 ngày nếu tổn thương không thuyên giảm để cân nhắc tầm '
                             'soát bội nhiễm vi khuẩn tụ cầu liên cầu hoặc suy giảm miễn dịch.'],
    'bien_the_kham': [   'Toàn bộ vùng bẹn, kẽ mông và sinh dục ngoài quấn tã có mảng hồng ban đỏ tươi bóng láng lan '
                         'sâu vào đáy các nếp gấp da, bờ viền rõ có viền bong vảy trắng mỏng và nhiều sẩn mụn mủ vệ '
                         'tinh kích thước 1-2mm xung quanh.',
                         'Hăm tã nặng vùng tầng sinh môn và nếp bẹn hai bên đỏ rực như thịt bò sống, trợt da nông rỉ '
                         'dịch nhẹ tại kẽ đùi, xung quanh mép mảng đỏ có nhiều nốt sẩn đỏ nhỏ rời rạc đặc trưng của '
                         'nấm men.',
                         'Khám da trẻ 4 tháng tuổi thấy mảng đỏ lan rộng vùng đeo bỉm kể cả trong các nếp lằn da sâu, '
                         'kèm khám miệng phát hiện các mảng giả mạc trắng như cặn sữa bám chặt trên niêm mạc má khó '
                         'cạo (nấm miệng phối hợp).',
                         'Vùng da quanh hậu môn và bìu bẹn có ban đỏ tươi ranh giới sắc nét hình cung đa vòng, bề mặt '
                         'hơi ẩm ướt có viền vảy bong mỏng, trẻ khóc thét khi chạm nhẹ lau rửa.',
                         'Tổn thương da bẹn đỏ bóng xuất hiện từ 5 ngày nay sau đợt điều trị kháng sinh viêm tai giữa, '
                         'bôi kem dưỡng ẩm thông thường càng lan rộng và mọc thêm nhiều chấm mụn mủ nhỏ vùng đùi trên.',
                         'Mảng hồng ban đỏ thẫm tập trung đậm đặc ở nếp gấp bẹn và mặt trong đùi, da mất lớp sừng bề '
                         'mặt mỏng bóng, không có mùi hôi mủ vàng của chốc lở vi khuẩn.'],
    'chan_doan': 'Viêm da tã lót nhiễm nấm Candida albicans vùng bẹn ở trẻ nhũ nhi.',
    'chinh': [   'vùng da quấn tã nếp lằn bẹn và mông đỏ rực bóng láng với ranh giới rõ rệt có viền vảy mỏng',
                 'xuất hiện nhiều sẩn mụn mủ nhỏ vệ tinh (tổn thương vệ tinh) rải rác xung quanh mảng đỏ chính',
                 'tổn thương ăn sâu vào tận đáy các nếp gấp kẽ bẹn và kẽ mông không chừa nếp lằn da'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'da liễu',
    'ke_hoach': 'Cạo vảy da vùng tổn thương soi tươi bằng KOH 10% tìm sợi tơ nấm giả và bào tử men, bôi kem kháng nấm '
                'tại chỗ Nystatin hoặc Clotrimazole 1% mỗi lần thay tã trong 10-14 ngày, giữ vùng tã khô thoáng tránh '
                'dùng phấn rôm.',
    'kham': 'Toàn bộ vùng bẹn, kẽ mông và sinh dục ngoài quấn tã có mảng hồng ban đỏ tươi bóng láng lan sâu vào đáy '
            'các nếp gấp da, bờ viền rõ có viền bong vảy trắng mỏng và nhiều sẩn mụn mủ vệ tinh kích thước 1-2mm xung '
            'quanh.',
    'nhom': 'nhi',
    'phu': [   'trẻ quấy khóc dữ dội khó chịu mỗi khi đi tiểu hoặc đi đại tiện làm ướt vùng bẹn',
               'thường xuất hiện sau đợt trẻ bị tiêu chảy kéo dài hoặc vừa dùng kháng sinh phổ rộng đường uống',
               'có thể kèm tưa miệng mảng trắng bám ở niêm mạc lưỡi và má trong'],
    'ten': 'nhiễm nấm candida da bẹn ở trẻ nhũ nhi'},
    {   'bien_the_chan_doan': [   'Chàm thể tạng đợt cấp bội nhiễm vi khuẩn tụ cầu vàng.',
                              'Viêm da cơ địa bội nhiễm chốc hóa mức độ trung bình nặng ở trẻ em.',
                              'Chàm thể tạng bội nhiễm có phản ứng hạch vùng và sốt nhẹ.',
                              'Theo dõi chàm thể tạng bội nhiễm cần phân biệt với nhiễm virus herpes simplex (chàm '
                              'Kaposi).',
                              'Chàm thể tạng bội nhiễm tái phát ở trẻ có cơ địa dị ứng nặng.',
                              'Đợt bùng phát chàm thể tạng bội nhiễm vi khuẩn đáp ứng tốt kháng sinh đường toàn thân.'],
    'bien_the_ke_hoach': [   'Cấy dịch mủ tổn thương da tìm vi khuẩn làm kháng sinh đồ, điều trị kháng sinh đường uống '
                             'Cephalexin hoặc Amoxicillin-Clavulanate 7-10 ngày kết hợp đắp gạc ẩm nước muối sinh lý '
                             'làm bong vảy tiết, sau đó bôi thuốc kháng viêm nhẹ và dưỡng ẩm.',
                             'Kê đơn kháng sinh đường uống Cefadroxil hoặc Clindamycin nếu nghi ngờ tụ cầu kháng '
                             'methicillin (MRSA) cộng đồng, phối hợp thuốc kháng histamin thế hệ 1 Hydroxyzine buổi '
                             'tối giúp trẻ giảm ngứa ngủ ngon.',
                             'Hướng dẫn tắm rửa nhẹ nhàng bằng dung dịch sát khuẩn dịu nhẹ pha loãng (như nước thuốc '
                             'tím pha hồng nhạt hoặc sữa tắm chứa chlorhexidine dịu nhẹ), tuyệt đối không chà xát mạnh '
                             'làm trợt da.',
                             'Ngưng tạm thời các thuốc ức chế calcineurin (Tacrolimus) tại vùng đang chảy mủ; khi hết '
                             'mủ và đóng mài khô bắt đầu bôi Hydrocortisone 1% ngắn ngày kết hợp dưỡng ẩm chuyên biệt '
                             'cho da cơ địa.',
                             'Cắt ngắn móng tay trẻ và đeo bao tay cotton mềm ban đêm để ngăn ngừa tổn thương da thêm '
                             'do gãi trong lúc ngủ.',
                             'Tái khám sau 5-7 ngày đánh giá độ sạch khuẩn tổn thương, tư vấn gia đình quy trình dưỡng '
                             'ẩm hàng ngày lâu dài và tránh các dị nguyên kích ứng như xà phòng kiềm lông thú len dạ.'],
    'bien_the_kham': [   'Hai bên má, nếp khuỷu tay và khoeo chân có các mảng hồng ban rỉ dịch vàng đục đóng vảy tiết '
                         'màu mật ong dày đặc kèm nhiều vết cào xước chảy máu và mụn mủ nhỏ rải rác, hạch cổ hai bên '
                         'sưng nhẹ 1cm ấn đau.',
                         'Da vùng cẳng chân và mu bàn tay có nhiều mảng chàm trợt loét rỉ dịch mủ hôi nhẹ, bề mặt phủ '
                         'lớp mài vàng nâu dày cộm, sờ vùng da quanh tổn thương thấy ấm nóng và phù nề nhẹ.',
                         'Trẻ gãi liên tục vùng cổ và nếp gấp chi, quan sát thấy các nốt mụn nước vỡ để lại vết trợt '
                         'hình đồng xu đóng vảy tiết vàng mật ong xen kẽ da khô nứt nẻ lichen hóa lâu ngày.',
                         'Nhiệt độ 38,2 độ C, mảng da chàm bội nhiễm lan rộng vùng lưng và ngực, không thấy các mụn '
                         'nước lõm giữa dạng thủy đậu (loại trừ chàm dạng herpes Eczema herpeticum).',
                         'Khám da liễu thấy tổn thương viêm da cơ địa lan tỏa bội nhiễm nặng ở hai khoeo chân gây đau '
                         'rát khi duỗi chân đi lại, hạch bẹn hai bên phản ứng to 1,5cm mềm di động.',
                         'Tổn thương da mặt và cổ đỏ tấy sưng nề rỉ dịch đục liên tục thấm ướt cổ áo trẻ, có nhiều vết '
                         'xước da sâu do móng tay cào gãi làm nhiễm trùng thứ phát.'],
    'chan_doan': 'Chàm thể tạng (viêm da cơ địa) đợt cấp bội nhiễm vi khuẩn tụ cầu vàng.',
    'chinh': [   'các mảng da khô đỏ ngứa gãi nhiều nay đột ngột chảy dịch vàng đóng vảy tiết dày màu vàng mật ong',
                 'xuất hiện nhiều mụn mủ nhỏ hoặc vết trợt loét nông sưng nóng đau rát tại vùng nếp gấp khuỷu tay '
                 'khoeo chân',
                 'ngứa dữ dội tăng vọt làm trẻ quấy khóc mất ngủ gãi chảy máu lở loét lan nhanh'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'da liễu',
    'ke_hoach': 'Cấy dịch mủ tổn thương da tìm vi khuẩn làm kháng sinh đồ, điều trị kháng sinh đường uống Cephalexin '
                'hoặc Amoxicillin-Clavulanate 7-10 ngày kết hợp đắp gạc ẩm nước muối sinh lý làm bong vảy tiết, sau đó '
                'bôi thuốc kháng viêm nhẹ và dưỡng ẩm phục hồi hàng rào da.',
    'kham': 'Hai bên má, nếp khuỷu tay và khoeo chân có các mảng hồng ban rỉ dịch vàng đục đóng vảy tiết màu mật ong '
            'dày đặc kèm nhiều vết cào xước chảy máu và mụn mủ nhỏ rải rác, hạch cổ hai bên sưng nhẹ 1cm ấn đau.',
    'nhom': 'nhi',
    'phu': [   'trẻ có thể sốt nhẹ đến vừa kèm nổi hạch vùng bẹn hoặc nách sưng đau',
               'tiền sử bản thân hoặc gia đình có cơ địa dị ứng hen suyễn viêm mũi dị ứng',
               'tổn thương da xung quanh khô ráp dày sừng lichen hóa từ trước'],
    'ten': 'chàm thể tạng bội nhiễm ở trẻ'},
    {   'bien_the_chan_doan': [   'Vảy nến thể giọt cấp tính ở trẻ em khởi phát sau viêm họng liên cầu.',
                              'Vảy nến thể giọt ở trẻ lớn bùng phát lan tỏa thân mình mức độ trung bình.',
                              'Theo dõi vảy nến thể giọt cần phân biệt với vảy phấn hồng Gibert và phát ban giang mai.',
                              'Vảy nến thể giọt ở trẻ em có dấu hiệu Koebner dương tính.',
                              'Vảy nến thể giọt đợt cấp ổn định dần sau kiểm soát ổ nhiễm trùng tai mũi họng.',
                              'Vảy nến thể giọt lần đầu ở trẻ em chưa có tổn thương viêm khớp vảy nến.'],
    'bien_the_ke_hoach': [   'Làm xét nghiệm ngoáy họng nuôi cấy vi khuẩn hoặc test nhanh liên cầu nhóm A, định lượng '
                             'ASO máu, điều trị kháng sinh diệt liên cầu nếu còn dương tính, bôi kem dưỡng ẩm và '
                             'corticoid tại chỗ hiệu lực nhẹ-trung bình.',
                             'Chỉ định kháng sinh Penicillin V hoặc Amoxicillin đường uống đủ 10 ngày nếu xét nghiệm '
                             'cấy dịch họng còn sự hiện diện của liên cầu khuẩn tan huyết beta nhóm A.',
                             'Bôi thuốc mỡ phối hợp Calcipotriol và Betamethasone dipropionate (hoặc Hydrocortisone '
                             'butyrate 0,1% trên vùng da mỏng) lên các sẩn lớn ngày 1-2 lần trong thời gian ngắn 2-3 '
                             'tuần.',
                             'Kết hợp sử dụng kem dưỡng ẩm làm mềm da chứa ceramide hoặc petrolatum đều đặn hàng ngày '
                             'giúp giảm khô ngứa và hạn chế bong tróc vảy.',
                             'Chuyển chuyên khoa Da liễu cân nhắc liệu pháp chiếu tia cực tím dải hẹp (Narrowband UVB) '
                             '2-3 buổi/tuần đối với các trường hợp sẩn giọt lan tỏa quá rộng toàn thân không đáp ứng '
                             'thuốc bôi.',
                             'Giải thích cho gia đình tiên lượng vảy nến thể giọt ở trẻ thường đáp ứng tốt và có thể '
                             'thoái lui hoàn toàn sau vài tháng, đồng thời theo dõi định kỳ đề phòng chuyển sang vảy '
                             'nến thể mảng mạn tính.'],
    'bien_the_kham': [   'Toàn bộ vùng lưng, ngực, bụng và hai đùi có rất nhiều sẩn hồng ban hình tròn bầu dục giống '
                         'giọt nước kích thước 3-8mm ranh giới rõ, bề mặt phủ vảy trắng đục mỏng dễ bong, cạo vảy '
                         'dương tính với dấu hiệu vết nến và giọt sương máu, họng còn hai amidan quá phát độ 2.',
                         'Khám da thân mình phát hiện hàng trăm nốt sẩn đỏ tươi kích thước như hạt đậu xanh rải rác '
                         'đều không liên kết thành mảng lớn, vảy trắng bạc lấm tấm phủ trung tâm nốt sẩn, không có tổn '
                         'thương móng hay khớp.',
                         'Trẻ 8 tuổi nổi sẩn đỏ vảy trắng dày đặc ở thân mình và phần gần cánh tay hai bên sau đợt sốt '
                         'đau họng 10 ngày trước, niêm mạc miệng sạch không có ban ở lòng bàn tay bàn chân (giúp loại '
                         'trừ giang mai 2).',
                         'Các sẩn vảy nến giọt xuất hiện dọc theo vết xước da cũ vùng cẳng tay (hiện tượng Koebner '
                         'dương tính), bề mặt sẩn hơi gồ nhẹ, trẻ chỉ cảm thấy ngứa râm ran nhẹ khi ra mồ hôi.',
                         'Da đầu vùng chân tóc có một vài mảng đỏ bong vảy trắng mỏng kèm rải rác các sẩn giọt nước '
                         'màu cá hồi vùng thân mình, hạch cổ dưới hàm sưng nhẹ di động không đau.',
                         'Tổn thương da cấp tính bùng phát nhanh trong 4 ngày với vô số nốt đỏ 2-6mm phủ vảy trắng '
                         'mỏng dễ rơi, cạo nhẹ lớp vảy trắng tạo bụi mịn như cạo sáp nến.'],
    'chan_doan': 'Vảy nến thể giọt cấp tính ở trẻ em khởi phát sau viêm họng liên cầu.',
    'chinh': [   'khởi phát đột ngột hàng loạt các sẩn dát đỏ kích thước nhỏ 2-10mm hình giọt nước rải rác khắp thân '
                 'mình và gốc chi',
                 'trên bề mặt các sẩn đỏ có phủ lớp vảy trắng bạc mịn dễ bong tróc khi cạo nhẹ',
                 'tổn thương da bùng phát cấp tính khoảng 1-3 tuần sau một đợt viêm họng cấp hoặc viêm amidan có sốt'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'da liễu',
    'ke_hoach': 'Làm xét nghiệm ngoáy họng nuôi cấy vi khuẩn hoặc test nhanh liên cầu nhóm A, định lượng ASO '
                '(Anti-Streptolysin O) máu, điều trị kháng sinh diệt liên cầu nếu còn dương tính, bôi kem dưỡng ẩm và '
                'corticoid tại chỗ hiệu lực nhẹ-trung bình hoặc quang trị liệu UVB dải hẹp nếu lan tỏa rộng.',
    'kham': 'Toàn bộ vùng lưng, ngực, bụng và hai đùi có rất nhiều sẩn hồng ban hình tròn bầu dục giống giọt nước kích '
            'thước 3-8mm ranh giới rõ, bề mặt phủ vảy trắng đục mỏng dễ bong, cạo vảy dương tính với dấu hiệu vết nến '
            'và giọt sương máu, họng còn hai amidan quá phát độ 2.',
    'nhom': 'nhi',
    'phu': [   'ngứa nhẹ hoặc không ngứa tại các nốt ban đỏ trên da',
               'vị trí xuất hiện dày đặc ở ngực lưng bụng đùi cánh tay ít khi có ở lòng bàn tay chân',
               'có hiện tượng giọt sương máu (dấu hiệu Auspitz) khi cạo hết lớp vảy trên sẩn'],
    'ten': 'vảy nến thể giọt ở trẻ em'},
    {   'bien_the_chan_doan': [   'Nhược thị mắt trái mức độ trung bình do bất đồng tật khúc xạ nặng.',
                              'Nhược thị mắt phải thể nặng kèm lác trong điều tiết ở trẻ mẫu giáo.',
                              'Nhược thị hai mắt do tật loạn thị và viễn thị cao không được điều chỉnh kính sớm.',
                              'Nhược thị do che lấp trục thị giác thứ phát sau sụp mi bẩm sinh.',
                              'Nhược thị chức năng mức độ nhẹ phát hiện sớm trong giai đoạn vàng trước 7 tuổi.',
                              'Nhược thị phối hợp bất đồng khúc xạ và vi lác ở trẻ nhỏ.'],
    'bien_the_ke_hoach': [   'Tra thuốc liệt điều tiết Cyclopentolate đo khúc xạ chính xác tuyệt đối, cấp đơn kính '
                             'gọng chỉnh tật khúc xạ đeo thường xuyên toàn thời gian, thực hiện liệu pháp bịt mắt lành '
                             '2-6 giờ mỗi ngày kết hợp bài tập kích thích thị giác.',
                             'Chỉ định đeo kính đúng độ quang học liên tục suốt cả ngày trong 4-8 tuần đầu để thích '
                             'nghi quang học trước khi đánh giá lại xem có cần phối hợp miếng dán bịt mắt.',
                             'Áp dụng dán băng bịt hoàn toàn mắt có thị lực tốt hơn (bịt mắt phải) trong 2 giờ/ngày '
                             '(với nhược thị vừa) đến 6 giờ/ngày (với nhược thị nặng), khuyến khích trẻ vẽ tô màu xâu '
                             'hạt lắp ghép lego trong thời gian bịt mắt.',
                             'Sử dụng biện pháp làm mờ mắt lành bằng thuốc nhỏ mắt Atropine 1% cuối tuần (Atropine '
                             'penalization) làm giải pháp thay thế hiệu quả nếu trẻ không hợp tác dán băng bịt mắt.',
                             'Phối hợp tập luyện phục hồi chức năng thị giác bằng máy kích thích thị giác Synoptophore '
                             'hoặc phần mềm trò chơi thị giác hai mắt tại khoa Mắt Nhi.',
                             'Hẹn tái khám đo thị lực kiểm tra đáp ứng mỗi 4-6 tuần để điều chỉnh thời gian bịt mắt '
                             'kịp thời, tránh biến chứng nhược thị đảo ngược sang mắt lành và duy trì kết quả điều '
                             'trị.'],
    'bien_the_kham': [   'Thị lực mắt phải đo bằng bảng chữ E đạt 10/10, thị lực mắt trái chỉ đạt 3/10 và chỉnh kính '
                         'thử tối đa chỉ lên được 4/10, khúc xạ liệt điều tiết mắt trái viễn thị +4,50 Diop và loạn '
                         'thị +1,50 Diop trong khi mắt phải +0,50 Diop, soi đáy mắt bình thường.',
                         'Trẻ 5 tuổi có dấu hiệu che mắt phải lại là phản kháng khóc thét gạt tay ra ngay vì mắt trái '
                         'nhìn rất mờ, khám vận nhãn thấy mắt trái lác trong khoảng 15 độ, thị lực mắt trái 2/10 có '
                         'kính.',
                         'Đo thị lực từng mắt bằng bảng hình ảnh Lea: mắt phải 8/10 mắt trái 2/10, phản xạ ánh hồng '
                         'đồng tử Bruckner hai mắt cân xứng bình thường không có đục thủy tinh thể bẩm sinh.',
                         'Thị lực hai mắt cùng giảm còn 3/10 có kính ở trẻ bị loạn thị cao bẩm sinh cả hai bên +3,50D '
                         'trục 90 độ không được đeo kính sớm (nhược thị hai mắt do tật khúc xạ).',
                         'Khám nghiệm pháp che mắt (Cover test) thấy mắt phải định thị vững chắc, mắt trái đảo nhẹ ra '
                         'ngoài khi che mắt phải, thị lực chỉnh kính tối đa mắt trái chênh lệch 4 hàng bảng thị lực so '
                         'với mắt phải.',
                         'Soi đèn khe phần trước và soi đáy mắt gián tiếp hoàn toàn bình thường không có sẹo giác mạc '
                         'hay tổn thương thần kinh thị giác, xác định giảm thị lực chức năng do ức chế vỏ não thị '
                         'giác.'],
    'chan_doan': 'Nhược thị mắt trái mức độ trung bình do bất đồng tật khúc xạ nặng.',
    'chinh': [   'thị lực một mắt hoặc cả hai mắt suy giảm rõ rệt không thể đạt mức 10/10 ngay cả khi đã đeo kính '
                 'chỉnh tật khúc xạ tối ưu',
                 'trẻ hay nheo mắt nghiêng đầu vẹo cổ khi nhìn bảng hoặc xem tivi từ xa',
                 'mắt có thể kèm biểu hiện lác lé hoặc bất đồng tật khúc xạ nặng giữa hai mắt'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'mắt',
    'ke_hoach': 'Tra thuốc liệt điều tiết Cyclopentolate đo khúc xạ chính xác tuyệt đối, cấp đơn kính gọng chỉnh tật '
                'khúc xạ đeo thường xuyên toàn thời gian, thực hiện liệu pháp bịt mắt lành (occlusion therapy) 2-6 giờ '
                'mỗi ngày kết hợp bài tập kích thích thị giác mắt nhược thị và tái khám đánh giá mỗi 4-8 tuần.',
    'kham': 'Thị lực mắt phải đo bằng bảng chữ E đạt 10/10, thị lực mắt trái chỉ đạt 3/10 và chỉnh kính thử tối đa chỉ '
            'lên được 4/10, khúc xạ liệt điều tiết mắt trái viễn thị +4,50 Diop và loạn thị +1,50 Diop trong khi mắt '
            'phải +0,50 Diop, soi đáy mắt hai bên đĩa thị hoàng điểm hoàn toàn bình thường.',
    'nhom': 'nhi',
    'phu': [   'trẻ thường không tự than phiền nhìn mờ do mắt lành còn lại bù trừ tốt',
               'dễ vấp ngã ước lượng khoảng cách chiều sâu kém khi bắt bóng hoặc bước cầu thang',
               'phát hiện tình cờ qua khám sàng lọc thị lực định kỳ ở trường học hoặc phòng khám mắt'],
    'ten': 'nhược thị ở trẻ em'},
    {   'bien_the_chan_doan': [   'Lác trong bẩm sinh (lác trong trẻ nhũ nhi) góc lớn định thị luân phiên.',
                              'Lác trong bẩm sinh ở trẻ nhỏ có nguy cơ nhược thị mắt lác cố định.',
                              'Lác trong nhũ nhi phối hợp tăng hoạt cơ chéo dưới hai bên.',
                              'Lác trong bẩm sinh phân biệt với giả lác do nếp quạt mũi rộng (epicanthus).',
                              'Lác trong bẩm sinh kèm lác đứng phân ly (DVD) cần theo dõi chỉ định phẫu thuật.',
                              'Lác trong bẩm sinh ở trẻ nhũ nhi không do tật khúc xạ viễn thị cao.'],
    'bien_the_ke_hoach': [   'Đo khúc xạ dưới liệt điều tiết và soi đáy mắt loại trừ u nguyên bào võng mạc hay tổn '
                             'thương thực thể đáy mắt, hướng dẫn bịt mắt luân phiên nếu có dấu hiệu ưu thế một mắt '
                             'phòng nhược thị và lên lịch phẫu thuật lùi cơ thẳng trong hai bên trước 18-24 tháng '
                             'tuổi.',
                             'Chỉnh kính nếu phát hiện có kèm viễn thị trên +2,50D để loại trừ yếu tố lác trong điều '
                             'tiết phối hợp trước khi quyết định chỉ định mổ.',
                             'Điều trị nhược thị tích cực bằng bịt mắt lành vài giờ mỗi ngày cho đến khi trẻ đạt khả '
                             'năng định thị luân phiên đều đặn cả hai mắt trước ngày phẫu thuật.',
                             'Hội chẩn chuyên khoa Nhãn nhi thực hiện phẫu thuật chỉnh lác (lùi cơ thẳng trong hai '
                             'mắt) ở giai đoạn lý tưởng từ 9-18 tháng tuổi nhằm phục hồi tối đa khả năng phát triển '
                             'thị giác hai mắt và hợp thị.',
                             'Theo dõi sát sau phẫu thuật lác để phát hiện sớm hiện tượng lác tồn dư hoặc lác ngoài '
                             'thứ phát, phối hợp điều trị tăng hoạt cơ chéo dưới nếu xuất hiện.',
                             'Tư vấn cho gia đình hiểu rõ phẫu thuật lác giúp trả lại trục nhãn cầu thẳng nhưng trẻ '
                             'vẫn cần theo dõi mắt lâu dài đến 8-10 tuổi phòng ngừa tái phát lác hoặc nhược thị.'],
    'bien_the_kham': [   'Bé trai 8 tháng tuổi có góc lác trong lớn khoảng 40 đi-ốp lăng kính nhìn thấy rõ qua nghiệm '
                         'pháp ánh phản giác mạc Hirschberg lệch thái dương nhiều, trẻ định thị luân phiên cả hai mắt, '
                         'vận nhãn liếc ngoài hai bên hơi hạn chế nhẹ nhưng mở rộng hết tầm khi làm nghiệm pháp mắt '
                         'búp bê.',
                         'Mắt phải luôn bị lé quay sâu vào góc trong ngay cả khi nhìn thẳng đồ chơi ở xa và gần, '
                         'nghiệm pháp che mắt cho thấy trẻ từ chối khi che mắt trái (dấu hiệu nhược thị mắt phải kèm '
                         'theo).',
                         'Trẻ 5 tháng tuổi có góc lác trong cố định 35 độ kèm nếp quạt gốc mũi rộng, soi ánh đồng tử '
                         'hai mắt đỏ hồng đều bình thường, kiểm tra phản xạ xoay đầu cho thấy vận động cơ thẳng ngoài '
                         'bình thường giúp loại trừ liệt dây VI.',
                         'Khám mắt trẻ 1 tuổi phát hiện lác trong bẩm sinh góc lớn kèm rung giật nhãn cầu ẩn (latent '
                         'nystagmus) xuất hiện khi che một mắt và tăng hoạt cơ chéo dưới hai bên khi liếc vào trong.',
                         'Soi đáy mắt gián tiếp qua đồng tử giãn không phát hiện bất thường gai thị hay khối u võng '
                         'mạc, khúc xạ viễn thị sinh lý +1,25 Diop hai mắt không phải nguyên nhân lác điều tiết.',
                         'Trẻ có tư thế nghiêng đầu nhẹ sang phải khi tập trung nhìn đồ vật sáng, góc lác trong đo '
                         'bằng thanh lăng kính Krimsky đạt 45 PD ổn định ở cả khoảng cách xa và gần.'],
    'chan_doan': 'Lác trong bẩm sinh (lác trong trẻ nhũ nhi) góc lớn định thị luân phiên.',
    'chinh': [   'hai mắt lệch trục rõ rệt một hoặc cả hai mắt luân phiên lé quay vào phía trong gốc mũi',
                 'tình trạng lác mắt xuất hiện rất sớm ngay trong 6 tháng đầu đời sau sinh',
                 'góc lác thường rất lớn và ổn định liên tục không phụ thuộc vào việc trẻ nhìn xa hay nhìn gần'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'mắt',
    'ke_hoach': 'Đo khúc xạ dưới liệt điều tiết Atropine hoặc Cyclopentolate và soi đáy mắt loại trừ u nguyên bào võng '
                'mạc hay tổn thương thực thể đáy mắt, hướng dẫn bịt mắt luân phiên nếu có dấu hiệu ưu thế một mắt '
                'phòng nhược thị và lên lịch phẫu thuật lùi cơ thẳng trong hai bên trước 18-24 tháng tuổi.',
    'kham': 'Bé trai 8 tháng tuổi có góc lác trong lớn khoảng 40 đi-ốp lăng kính (PD) nhìn thấy rõ qua nghiệm pháp ánh '
            'phản giác mạc Hirschberg lệch thái dương nhiều, trẻ định thị luân phiên cả hai mắt, vận nhãn liếc ngoài '
            'hai bên hơi hạn chế nhẹ nhưng mở rộng hết tầm khi làm nghiệm pháp mắt búp bê, khúc xạ liệt điều tiết viễn '
            'thị nhẹ +1,00D bình thường theo tuổi.',
    'nhom': 'nhi',
    'phu': [   'trẻ có thể quay đầu sang bên để nhìn bằng mắt định thị (định thị chéo)',
               'có thể đi kèm hiện tượng rung giật nhãn cầu nhẹ hoặc lác đứng phân ly',
               'nguy cơ phát triển nhược thị nếu trẻ chỉ sử dụng cố định một mắt để nhìn'],
    'ten': 'lác trong bẩm sinh ở trẻ'},
    {   'bien_the_chan_doan': [   'Viêm kết mạc sơ sinh tối cấp nghi do vi khuẩn lậu cầu Neisseria gonorrhoeae.',
                              'Viêm kết mạc sơ sinh do lậu cầu có nguy cơ biến chứng loét thủng giác mạc cấp.',
                              'Theo dõi viêm kết mạc sơ sinh cấp tính nghi đồng nhiễm lậu cầu và Chlamydia '
                              'trachomatis.',
                              'Viêm kết mạc mủ tối cấp ở trẻ sơ sinh giai đoạn sớm giác mạc còn nguyên vẹn.',
                              'Viêm kết mạc do lậu ở trẻ sơ sinh cần cấp cứu điều trị kháng sinh toàn thân ngay.',
                              'Viêm mắt sơ sinh tối cấp xuất hiện trong tuần đầu sau sinh ngả âm đạo.'],
    'bien_the_ke_hoach': [   'Cấp cứu nhãn khoa khẩn cấp: lấy mủ mắt nhuộm Gram ngay tìm song cầu khuẩn Gram âm nằm '
                             'trong bạch cầu và cấy vi khuẩn, nhập viện tiêm tĩnh mạch hoặc tiêm bắp ngay Ceftriaxone '
                             '25-50 mg/kg liều duy nhất (tối đa 125mg), đồng thời rửa mắt liên tục mỗi giờ bằng nước '
                             'muối sinh lý.',
                             'Dùng kháng sinh Cefotaxime tĩnh mạch thay thế Ceftriaxone nếu trẻ sơ sinh đang có tình '
                             'trạng vàng da tăng bilirubin máu nặng để tránh nguy cơ vàng da nhân não.',
                             'Phối hợp điều trị thêm Erythromycin đường uống 50 mg/kg/ngày trong 14 ngày (hoặc '
                             'Azithromycin) để phủ luôn đồng nhiễm Chlamydia trachomatis rất thường đi kèm với lậu '
                             'cầu.',
                             'Tổ chức rửa trôi mủ mắt liên tục bằng dung dịch Natri Clorid 0,9% mỗi 30-60 phút cho đến '
                             'khi sạch mủ hoàn toàn, nhỏ bổ sung thuốc mỡ hoặc dung dịch kháng sinh tại chỗ như '
                             'Moxifloxacin hoặc Tobramycin theo hướng dẫn nhãn khoa.',
                             'Theo dõi giác mạc hàng ngày bằng nhuộm Fluorescein qua đèn khe cầm tay để phát hiện sớm '
                             'ổ loét giác mạc, đảm bảo nhân viên y tế đeo kính bảo hộ và rửa tay nghiêm ngặt tránh lây '
                             'nhiễm chéo.',
                             'Khám và điều trị đồng thời cho cả người mẹ và bạn tình bằng phác đồ kháng sinh điều trị '
                             'bệnh lậu và Chlamydia lây truyền qua đường tình dục.'],
    'bien_the_kham': [   'Trẻ sơ sinh 3 ngày tuổi có hai mi mắt sưng phù căng mọng màu đỏ tím không tự mở được mắt, '
                         'banh nhẹ khe mi thấy mủ đặc màu vàng xanh trào ra liên tục ồ ạt, kết mạc phù nề đỏ rực, giác '
                         'mạc hai bên hiện còn trong chưa thấy ổ loét trắng.',
                         'Khám mắt trẻ 4 ngày tuổi thấy mủ vàng đặc quánh đóng thành mảng xung quanh hai hàng mi mắt, '
                         'mở vành mi cẩn thận thấy giác mạc mắt phải bắt đầu có đám đục mờ nhỏ vùng chu biên bắt màu '
                         'thuốc nhuộm Fluorescein (dọa loét giác mạc).',
                         'Sưng nề đỏ tấy mi mắt hai bên mức độ nặng xuất hiện từ ngày thứ 2 sau sinh, dịch tiết mủ đặc '
                         'trào ra nhiều đến mức vừa lau sạch lại đùn ra ngay sau vài phút, kết mạc sụn mi có lớp giả '
                         'mạc mỏng.',
                         'Trẻ quấy khóc dữ dội sợ ánh sáng mạnh, mi mắt co quắp chặt khó mở, kết mạc phù mọng che lấp '
                         'phần rìa giác mạc, hạch trước tai hai bên sưng nhỏ, toàn thân không sốt.',
                         'Cần hết sức lưu ý khi banh mi khám vì mủ trong hốc mắt đang chịu áp lực cao có thể bắn phụt '
                         'vào mắt người khám; quan sát thấy đồng tử và tiền phòng mắt trái sạch, mắt phải kết mạc '
                         'cương tụ toàn bộ.',
                         'Khám sơ sinh phát hiện hội chứng mắt đỏ tiết mủ cấp tính khởi phát ngày thứ 3 sau sinh '
                         'thường, mẹ chưa từng sàng lọc bệnh lây truyền qua đường tình dục trong thai kỳ.'],
    'chan_doan': 'Viêm kết mạc sơ sinh tối cấp nghi do vi khuẩn lậu cầu Neisseria gonorrhoeae.',
    'chinh': [   'hai mắt sưng húp phù nề mi mắt dữ dội chỉ sau 2-5 ngày sau khi sinh thường ngả dưới',
                 'chảy mủ vàng xanh đặc sánh rất nhiều trào ra liên tục từ khe mi mắt như suối mủ',
                 'kết mạc nhãn cầu đỏ rực cương tụ mạnh kèm phù nề phồng mọng kết mạc (chemosis)'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'mắt',
    'ke_hoach': 'Cấp cứu nhãn khoa khẩn cấp: lấy mủ mắt nhuộm Gram ngay tìm song cầu khuẩn Gram âm hình hạt cà phê nằm '
                'trong tế bào bạch cầu đa nhân và cấy vi khuẩn, nhập viện tiêm tĩnh mạch hoặc tiêm bắp ngay một liều '
                'Ceftriaxone 25-50 mg/kg, đồng thời rửa mắt liên tục mỗi giờ bằng nước muối sinh lý.',
    'kham': 'Trẻ sơ sinh 3 ngày tuổi có hai mi mắt sưng phù căng mọng màu đỏ tím không tự mở được mắt, banh nhẹ khe mi '
            'thấy mủ đặc màu vàng xanh trào ra liên tục ồ ạt, kết mạc phù nề đỏ rực, giác mạc hai bên hiện còn trong '
            'chưa thấy ổ loét trắng.',
    'nhom': 'nhi',
    'phu': [   'có thể xuất hiện giả mạc bám dính ở kết mạc sụn mi gây chảy máu nhẹ khi lau',
               'nguy cơ rất cao biến chứng loét thủng giác mạc nhanh chóng trong 24-48 giờ gây mù lòa vĩnh viễn',
               'mẹ có tiền sử khí hư bất thường hoặc nhiễm lậu cầu chưa được điều trị trước khi sinh'],
    'ten': 'viêm kết mạc sơ sinh do lậu'},
    {   'bien_the_chan_doan': [   'Nứt kẽ hậu môn cấp tính ở trẻ em thứ phát sau táo bón kéo dài.',
                              'Nứt kẽ hậu môn cấp ở trẻ nhũ nhi sau giai đoạn chuyển ăn dặm thiếu chất xơ.',
                              'Nứt kẽ hậu môn tái diễn kèm hội chứng sợ đi tiêu và nín nhịn phân ở trẻ nhỏ.',
                              'Nứt kẽ hậu môn bán cấp có hình thành mẩu da thừa nhỏ ở rìa hậu môn.',
                              'Nứt kẽ hậu môn chảy máu đỏ tươi mức độ nhẹ ở trẻ em cần phân biệt polyp trực tràng.',
                              'Nứt kẽ hậu môn cấp tính đáp ứng tốt với điều trị làm mềm phân bảo tồn.'],
    'bien_the_ke_hoach': [   'Điều trị dứt điểm táo bón bằng thuốc làm mềm phân thẩm thấu Polyethylene Glycol '
                             '(Macrogol) liều 0,5-1 g/kg/ngày giúp phân mềm mịn dễ đi, hướng dẫn ngâm hậu môn nước ấm '
                             'ngày 2-3 lần sau đại tiện để giãn cơ thắt và giảm đau.',
                             'Kê đơn Lactulose uống hàng ngày thay thế nếu trẻ dưới 6 tháng tuổi chưa dùng được '
                             'Macrogol, điều chỉnh liều sao cho trẻ đi tiêu phân mềm sệt dễ dàng mỗi ngày 1 lần.',
                             'Hướng dẫn gia đình cho trẻ ngồi ngâm mông trong chậu nước ấm sạch khoảng 10-15 phút mỗi '
                             'ngày đặc biệt ngay sau khi đi tiêu nhằm làm dịu cơn đau rát và tăng tưới máu giúp lành '
                             'vết nứt.',
                             'Tư vấn tăng cường lượng nước uống, bổ sung chất xơ tự nhiên từ rau xanh mồng tơi khoai '
                             'lang đu đủ chuối chín, hạn chế sữa bò quá mức hoặc đồ ăn nhanh khô cứng.',
                             'Dặn không tự ý thụt tháo hậu môn thô bạo hay dùng nhiệt kế ngoáy kích thích hậu môn gây '
                             'rách rộng thêm vết nứt, có thể bôi lớp mỏng vaseline quanh rìa hậu môn giúp bôi trơn.',
                             'Hẹn tái khám sau 2 tuần kiểm tra độ liền sẹo niêm mạc hậu môn, tiếp tục duy trì thuốc '
                             'làm mềm phân ít nhất 2-3 tháng để cắt đứt hoàn toàn vòng xoắn đau - nhịn đi tiêu - táo '
                             'bón.'],
    'bien_the_kham': [   'Banh nhẹ rìa ống hậu môn ở tư thế nằm nghiêng gấp gối quan sát thấy một vết rách niêm mạc '
                         'dọc hình thoi màu đỏ tươi dài 4mm tại vị trí 6 giờ, đáy vết nứt nông sạch rớm ít máu đỏ '
                         'tươi, cơ thắt hậu môn co thắt chặt khi chạm vào, bụng mềm sờ thấy khối phân dọc khung đại '
                         'tràng trái.',
                         'Khám hậu môn trẻ 3 tuổi phát hiện vết nứt rách nông ở vị trí 12 giờ phía trước có giọt máu '
                         'tươi mới chảy, da quanh hậu môn sạch không có ổ áp xe hay lỗ dò, khám bụng sờ thấy nhiều cục '
                         'phân cứng ở hố chậu trái.',
                         'Trẻ khóc thét co giật người lại không cho sờ vùng mông vì quá đau rát, tách nhẹ hai nếp mông '
                         'lộ vết loét nứt dọc rìa niêm mạc hậu môn dài 5mm bờ gọn mềm chưa có mẩu da thừa gác cổng của '
                         'giai đoạn mạn.',
                         'Quan sát tã có vài chấm máu đỏ tươi tách rời khỏi khuôn phân cứng chắc như đá, vết rách kẽ '
                         'hậu môn nằm nông ở đường giữa sau, phản xạ cơ thắt hậu môn tăng co thắt phản ứng.',
                         'Vết nứt kẽ hậu môn tái phát nhiều đợt kèm một nếp gấp da nhỏ phù nề nhẹ (mẩu da thừa báo '
                         'hiệu) ở bờ ngoài vị trí 6 giờ, trẻ có dấu hiệu sợ bô rõ rệt.',
                         'Khám tiêu hoá bụng không chướng hơi, nhu động ruột bình thường, rìa hậu môn có 2 vết xước '
                         'nứt niêm mạc nhỏ đối xứng 6 giờ và 12 giờ rớm máu nhẹ sau đợt táo bón 5 ngày chưa đi.'],
    'chan_doan': 'Nứt kẽ hậu môn cấp tính ở trẻ em thứ phát sau táo bón kéo dài.',
    'chinh': [   'trẻ khóc thét sợ hãi nín nhịn không chịu đi đại tiện vì đau rát dữ dội vùng hậu môn mỗi khi rặn',
                 'có vệt máu đỏ tươi dính trên bề mặt cục phân rắn hoặc thấm ra giấy vệ sinh tã lót sau khi đi tiêu',
                 'tiền sử đi tiêu phân rất to cứng khô thành từng viên như phân dê nhiều ngày mới đi một lần'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Điều trị dứt điểm táo bón bằng thuốc làm mềm phân thẩm thấu Polyethylene Glycol (Macrogol) liều 0,5-1 '
                'g/kg/ngày giúp phân mềm mịn dễ đi, hướng dẫn ngâm hậu môn nước ấm ngày 2-3 lần sau đại tiện để giãn '
                'cơ thắt và giảm đau, bôi kem bảo vệ Zinc oxide hoặc Lidocaine gel trước khi đi tiêu nếu đau nhiều.',
    'kham': 'Banh nhẹ rìa ống hậu môn ở tư thế nằm nghiêng gấp gối quan sát thấy một vết rách niêm mạc dọc hình thoi '
            'màu đỏ tươi dài 4mm tại vị trí 6 giờ (đường giữa sau), đáy vết nứt nông sạch rớm ít máu đỏ tươi, cơ thắt '
            'hậu môn co thắt chặt khi chạm vào, bụng mềm sờ thấy khối phân dọc khung đại tràng trái.',
    'nhom': 'nhi',
    'phu': [   'trẻ thường gồng cứng người bắt chéo hai chân hoặc trốn vào góc nhà để nhịn đi ngoài',
               'đau rát hậu môn kéo dài vài chục phút sau khi đại tiện xong làm trẻ khó chịu cáu gắt',
               'sợ ăn uống do ngại đi vệ sinh dẫn đến vòng xoắn bệnh lý táo bón nặng thêm'],
    'ten': 'nứt kẽ hậu môn ở trẻ em do táo bón'},
    {   'bien_the_chan_doan': [   'Hội chứng nôn chu kỳ ở trẻ em giai đoạn cơn cấp có mất nước nhẹ.',
                              'Hội chứng nôn chu kỳ ở trẻ em thể liên quan đau nửa đầu Migraine.',
                              'Hội chứng nôn chu kỳ tái phát định kỳ theo tiêu chuẩn chẩn đoán Rome IV.',
                              'Đợt cấp hội chứng nôn chu kỳ có biến chứng nhiễm toan ceton và hạ kali máu nhẹ.',
                              'Theo dõi hội chứng nôn chu kỳ cần loại trừ dị tật ruột quay bất toàn và rối loạn chuyển '
                              'hoá bẩm sinh.',
                              'Hội chứng nôn chu kỳ mức độ trung bình đáp ứng tốt với Ondansetron tĩnh mạch.'],
    'bien_the_ke_hoach': [   'Loại trừ các nguyên nhân thực thể nguy hiểm bằng xét nghiệm sinh hóa máu, siêu âm ổ bụng '
                             'loại trừ tắc ruột xoay bất toàn và chụp MRI não nếu cần; truyền dịch Glucose 5% pha điện '
                             'giải tĩnh mạch và tiêm tĩnh mạch Ondansetron 0,15 mg/kg cắt cơn nôn.',
                             'Cho trẻ nghỉ ngơi trong phòng yên tĩnh ánh sáng dịu mát, cân nhắc dùng Lorazepam hoặc '
                             'Diphenhydramine hỗ trợ an thần gây ngủ giúp cắt đứt chu kỳ buồn nôn trung ương.',
                             'Làm xét nghiệm tầm soát rối loạn chuyển hóa bẩm sinh (khí máu, amoniac, acid lactic, '
                             'ceton niệu) lấy mẫu ngay trong lúc trẻ đang có cơn cấp để không bỏ sót bệnh lý chu trình '
                             'ure hay rối loạn oxy hoá acid béo.',
                             'Chỉ định chụp lưu thông đường tiêu hóa trên (UGI series) hoặc siêu âm Doppler mạch mạc '
                             'treo nếu trẻ có nôn dịch mật xanh nhiều để loại trừ chắc chắn hội chứng kìm động mạch '
                             'mạc treo hay ruột xoay bất toàn.',
                             'Tư vấn điều trị dự phòng hàng ngày bằng Cyproheptadine (cho trẻ dưới 5 tuổi) hoặc '
                             'Amitriptyline / Propranolol (cho trẻ lớn trên 5 tuổi) nếu cơn nôn xảy ra thường xuyên '
                             'hàng tháng gây ảnh hưởng học tập.',
                             'Hướng dẫn gia đình nhận diện sớm các yếu tố kích phát cơn (thiếu ngủ, căng thẳng tâm lý, '
                             'nhịn đói quá lâu, nhiễm siêu vi nhẹ) và dùng thuốc chống nôn sớm ngay ở giai đoạn tiền '
                             'triệu.'],
    'bien_the_kham': [   'Trẻ đến khám trong cơn nôn ngày thứ 2 vẻ mặt mệt lả nhợt nhạt môi khô mắt hơi trũng nhẹ do '
                         'mất nước độ 1, nôn liên tục ra dịch trong lẫn ít mật vàng, bụng mềm hoàn toàn không có điểm '
                         'đau khu trú hay khối lồng, không có dấu hiệu cứng gáy màng não.',
                         'Ghi nhận bệnh nhi có 4 đợt nôn tương tự trong 6 tháng qua, mỗi đợt đều khởi phát lúc 4 giờ '
                         'sáng nôn 8-10 lần/giờ kéo dài đúng 48 giờ rồi tự hết hẳn, hiện tại mạch 115 l/p bụng lõm '
                         'lòng thuyền không chướng.',
                         'Trẻ nằm thiếp đi vì kiệt sức giữa các cơn buồn nôn khan dữ dội, hơi thở có mùi axeton nhẹ do '
                         'nhịn đói nhiễm ceton thứ phát, đồng tử hai bên đều phản xạ tốt, không phù gai thị.',
                         'Khám ngoài cơn sau 5 ngày điều trị: trẻ hoàn toàn tươi tỉnh hồng hào cân nặng trở lại bình '
                         'thường, bụng mềm không sờ thấy u cục, không có triệu chứng thần kinh hay rối loạn tiêu hoá.',
                         'Bé gái 7 tuổi trong cơn nôn dữ dội kèm than đau âm ỉ vùng trán hai bên và sợ ánh sáng phòng '
                         'khám, dấu véo da mất nhanh, không sốt không tiêu chảy phân lỏng.',
                         'Trẻ có tiền sử dễ say xe và mẹ bị đau nửa đầu Migraine, đợt này nôn ói liên hồi sau một kỳ '
                         'thi căng thẳng, khám toàn thân không phát hiện ổ nhiễm trùng hay tắc nghẽn đường tiêu hoá.'],
    'chan_doan': 'Hội chứng nôn chu kỳ ở trẻ em giai đoạn bùng phát có mất nước nhẹ.',
    'chinh': [   'các đợt nôn ói dữ dội liên tục nhiều lần trong một giờ kéo dài từ vài giờ đến vài ngày',
                 'các đợt nôn lặp lại theo tính chất chu kỳ rập khuôn giống hệt nhau về thời gian khởi phát và triệu '
                 'chứng',
                 'giữa các đợt nôn trẻ hoàn toàn khỏe mạnh ăn uống chơi đùa tăng cân bình thường không có triệu chứng '
                 'tiêu hoá nào'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'tiêu hoá',
    'ke_hoach': 'Loại trừ các nguyên nhân thực thể nguy hiểm bằng xét nghiệm sinh hóa máu (điện giải, đường huyết, '
                'amoniac, lactat), siêu âm ổ bụng loại trừ tắc ruột xoay bất toàn và chụp MRI não nếu có dấu hiệu thần '
                'kinh; điều trị cắt cơn bằng truyền dịch Glucose điện giải tĩnh mạch và thuốc chống nôn Ondansetron, '
                'sau đó xem xét dự phòng bằng Cyproheptadine hoặc Propranolol.',
    'kham': 'Trẻ đến khám trong cơn nôn ngày thứ 2 vẻ mặt mệt lả nhợt nhạt môi khô mắt hơi trũng nhẹ do mất nước độ 1, '
            'nôn liên tục ra dịch trong lẫn ít mật vàng, bụng mềm hoàn toàn không có điểm đau khu trú hay khối lồng, '
            'không có dấu hiệu cứng gáy màng não, thính lực và thần kinh bình thường.',
    'nhom': 'nhi',
    'phu': [   'cơn nôn thường bắt đầu đột ngột vào lúc sáng sớm hoặc nửa đêm kèm da tái xanh mệt lả li bì',
               'đau bụng quanh rốn đau đầu nhẹ sợ ánh sáng và chảy nước bọt nhiều trong cơn',
               'tiền sử bản thân hoặc gia đình có người mắc chứng đau nửa đầu Migraine hoặc say tàu xe'],
    'ten': 'hội chứng nôn chu kỳ ở trẻ em'},
    {   'bien_the_chan_doan': [   'Dị ứng đạm sữa đậu nành ở trẻ nhũ nhi phản ứng quá mẫn tức thì qua trung gian IgE.',
                              'Dị ứng sữa đậu nành ở trẻ nhũ nhi thể không qua trung gian IgE biểu hiện viêm đại tràng '
                              'chảy máu.',
                              'Hội chứng dị ứng chéo giữa đạm sữa bò và đạm sữa đậu nành ở trẻ nhỏ.',
                              'Hội chứng viêm ruột do protein sữa đậu nành (FPIES) cấp tính ở trẻ nhũ nhi.',
                              'Dị ứng đạm đậu nành mức độ nhẹ biểu hiện mề đay cấp và nôn trớ.',
                              'Theo dõi dị ứng sữa đậu nành cần thử nghiệm ăn kiêng loại trừ chẩn đoán.'],
    'bien_the_ke_hoach': [   'Ngừng ngay hoàn toàn sữa đậu nành và mọi chế phẩm chứa đạm đậu nành, dùng thuốc kháng '
                             'Histamin Cetirizine cắt cơn mề đay cấp, chuyển sang sử dụng sữa công thức đạm thủy phân '
                             'hoàn toàn hoặc sữa axit amin và làm test lẩy da.',
                             'Khuyến khích duy trì sữa mẹ tối đa nếu có thể; trường hợp mẹ cho con bú trực tiếp cần '
                             'hướng dẫn mẹ ăn kiêng nghiêm ngặt đạm sữa đậu nành và sữa bò trong 2-4 tuần theo dõi đáp '
                             'ứng.',
                             'Đối với trẻ có hội chứng FPIES nôn vọt mệt lả mất nước sau uống sữa đậu nành, cần lập '
                             'đường truyền tĩnh mạch bù dịch nhanh Natri Clorid 0,9% và theo dõi sát đề phòng sốc giảm '
                             'thể tích.',
                             'Chỉ định xét nghiệm định lượng kháng thể IgE đặc hiệu với protein đậu nành (f14) và xét '
                             'nghiệm test lẩy da (Skin Prick Test) tại chuyên khoa Dị ứng Miễn dịch Nhi.',
                             'Hướng dẫn cha mẹ đọc kỹ thành phần nhãn thực phẩm ăn dặm (bánh quy, bột ăn dặm, cháo chế '
                             'biến sẵn) để tránh đạm đậu nành ẩn (soy lecithin, đậu phụ, tương).',
                             'Hẹn tái khám đánh giá lại khả năng dung nạp đường miệng (Oral Food Challenge) sau 6-12 '
                             'tháng kiêng hoàn toàn dưới sự giám sát an toàn tại bệnh viện vì đa số trẻ sẽ tự hết dị '
                             'ứng khi lớn.'],
    'bien_the_kham': [   'Trẻ nhũ nhi 5 tháng tuổi sau uống sữa đậu nành 45 phút xuất hiện các mảng sẩn phù mề đay màu '
                         'hồng nổi gồ vùng má cằm và ngực bụng, mi mắt hơi sưng nề nhẹ, thở đều không có tiếng thở rít '
                         'thanh quản, phổi không ran.',
                         'Bé 4 tháng tuổi tiêu chảy phân lỏng nhiều nước lẫn vệt nhầy máu đỏ tươi kéo dài 1 tuần sau '
                         'khi đổi sang sữa đậu nành, bụng hơi chướng mềm, vùng da quanh hậu môn đỏ rát, không sốt.',
                         'Khám thấy các nốt ban đỏ sẩn ngứa tập trung quanh vùng miệng cằm nơi sữa đậu nành tiếp xúc '
                         'dây ra kèm trẻ nôn trớ thức ăn cũ ngay sau bữa bú 30 phút, sinh hiệu ổn định.',
                         'Trẻ có biểu hiện chàm thể tạng ở hai má và thân mình đỏ rực rỉ dịch nặng lên rõ rệt sau 3 '
                         'ngày dùng sữa công thức đậu nành, kèm khò khè nhẹ hai phổi thông khí đều.',
                         'Dấu hiệu viêm ruột non đại tràng do protein thức ăn (FPIES) với đậu nành: trẻ nôn vọt liên '
                         'tục sau bú sữa đậu nành 2 giờ, da tái mệt lả lơ mơ nhẹ, mạch nhanh 150 l/p, không nổi mề '
                         'đay.',
                         'Trẻ gầy nhẹ đứng cân 2 tháng nay từ khi thay sữa đậu nành, bụng chướng hơi, phân sống nhiều '
                         'cặn nhầy, khám họng phổi tim mạch chưa thấy bất thường thực thể.'],
    'chan_doan': 'Dị ứng đạm sữa đậu nành ở trẻ nhũ nhi phản ứng quá mẫn tức thì qua trung gian IgE.',
    'chinh': [   'xuất hiện nổi mề đay mẩn đỏ quanh miệng toàn thân hoặc phù môi mi mắt sau khi uống sữa công thức '
                 'nguồn gốc đậu nành',
                 'nôn trớ nhiều đau quặn bụng khóc thét tiêu chảy phân lỏng có thể lẫn nhầy máu sau khi chuyển sang '
                 'dùng sữa đậu nành',
                 'thở khò khè nghẹt mũi hắt hơi hoặc bùng phát nặng hơn tình trạng chàm da cơ địa'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'miễn dịch - dị ứng',
    'ke_hoach': 'Ngừng ngay hoàn toàn sữa đậu nành và mọi chế phẩm chứa đạm đậu nành, dùng thuốc kháng Histamin '
                'Cetirizine cắt cơn mề đay cấp, chuyển sang sử dụng sữa công thức đạm thủy phân hoàn toàn (eHF) hoặc '
                'đạm axit amin (AAF) và làm test lẩy da hoặc định lượng IgE đặc hiệu đậu nành.',
    'kham': 'Trẻ nhũ nhi 5 tháng tuổi sau uống sữa đậu nành 45 phút xuất hiện các mảng sẩn phù mề đay màu hồng nổi gồ '
            'vùng má cằm và ngực bụng, mi mắt hơi sưng nề nhẹ, thở đều không có tiếng thở rít thanh quản, phổi không '
            'ran, bụng mềm nhu động ruột tăng nhẹ.',
    'nhom': 'nhi',
    'phu': [   'trẻ thường có tiền sử dị ứng đạm sữa bò trước đó được chuyển sang dùng thử sữa đậu nành thay thế',
               'chậm tăng cân biếng ăn từ chối bình sữa đậu nành khi đưa lại gần miệng',
               'gia đình có tiền sử cơ địa dị ứng thức ăn hen suyễn hoặc viêm mũi dị ứng'],
    'ten': 'dị ứng sữa đậu nành ở trẻ nhũ nhi'},
    {   'bien_the_chan_doan': [   'Hội chứng ruột ngắn ở trẻ em sau cắt ruột rộng giai đoạn suy ruột mạn tính.',
                              'Hội chứng ruột ngắn ở trẻ nhũ nhi hậu phẫu viêm ruột hoại tử mất van hồi manh tràng.',
                              'Suy dinh dưỡng nặng và rối loạn điện giải thứ phát trên nền hội chứng ruột ngắn.',
                              'Hội chứng ruột ngắn ở trẻ em có biến chứng bệnh gan liên quan suy ruột (IFALD).',
                              'Hội chứng ruột ngắn giai đoạn ruột đang thích nghi tăng sinh niêm mạc.',
                              'Hội chứng ruột ngắn sau cắt đoạn ruột xoắn bẩm sinh phụ thuộc nuôi dưỡng tĩnh mạch.'],
    'bien_the_ke_hoach': [   'Áp dụng phác đồ phục hồi chức năng ruột đa chuyên khoa: phối hợp nuôi dưỡng tĩnh mạch '
                             'đảm bảo đủ năng lượng tăng trưởng kết hợp kích thích thích nghi ruột bằng ăn nhỏ giọt '
                             'sữa đạm thủy phân hoàn toàn giàu MCT, bổ sung vi chất sắt kẽm vitamin B12 và A D E K.',
                             'Theo dõi sát lượng dịch mất qua phân hoặc hậu môn nhân tạo hàng ngày để bù trừ chính xác '
                             'lượng nước và điện giải (Natri, Kali, Magie, Bicarbonat) qua đường tĩnh mạch hoặc '
                             'Oresol.',
                             'Sử dụng nhũ dịch lipid thế hệ mới chứa dầu cá Omega-3 (SMOFlipid hoặc Omegaven) trong '
                             'nuôi ăn tĩnh mạch nhằm phòng ngừa và đảo ngược tổn thương ứ mật gan.',
                             'Làm xét nghiệm định kỳ hàng tuần tháng các chỉ số điện giải đồ, chức năng gan bilirubin, '
                             'pre-albumin, sắt ferritin, kẽm và vitamin B12 nếu trẻ đã bị cắt đoạn hồi tràng cuối.',
                             'Điều trị hỗ trợ thuốc làm chậm nhu động ruột Loperamide (thận trọng ở trẻ lớn) hoặc '
                             'thuốc ức chế tiết axit dạ dày Omeprazole để giảm lượng dịch tiết tiêu hoá và ngừa loét '
                             'miệng nối.',
                             'Tập huấn nghiêm ngặt cho cha mẹ quy trình vô khuẩn khi chăm sóc catheter trung tâm phòng '
                             'nhiễm khuẩn huyết, xem xét phẫu thuật kéo dài ruột STEP nếu ruột giãn quá mức nhưng '
                             'không hấp thu được.'],
    'bien_the_kham': [   'Trẻ thể trạng suy dinh dưỡng nặng gầy teo cơ mỡ dưới da vùng mông đùi, trên thành bụng có '
                         'vết sẹo mổ cũ dài đường giữa trên dưới rốn đã liền sẹo, vùng cổ ngực còn lưu ống thông tĩnh '
                         'mạch trung tâm đường hầm sạch không sưng đỏ, bụng mềm trướng hơi nhẹ.',
                         'Bé 10 tháng tuổi cân nặng chỉ 5,5kg, hậu môn nhân tạo hỗng tràng vùng hố chậu phải ra nhiều '
                         'dịch phân lỏng xanh rêu lổn nhổn cặn sữa không tiêu, da xung quanh chân hậu môn nhân tạo đỏ '
                         'rát.',
                         'Khám thấy dấu hiệu thiếu vi chất mạn tính: tóc thưa dễ gãy rụng nhạt màu, niêm mạc mắt nhợt '
                         'nhạt thiếu máu, gan mấp mé 2,5cm dưới bờ sườn phải do ứ mật nhẹ từ nuôi ăn tĩnh mạch dài '
                         'ngày.',
                         'Dấu hiệu mất nước và rối loạn điện giải nhẹ: môi hơi khô, tiểu ít hơn bình thường sau đợt '
                         'tăng lượng sữa đường miệng gây tăng khối lượng phân, bụng mềm nhu động ruột tăng nhanh.',
                         'Trẻ có sẹo mổ xoắn ruột sơ sinh, hiện tại chậm tăng chiều cao cân nặng dưới bách phân vị thứ '
                         '3, các đầu xương cổ tay hơi bè nhẹ biểu hiện thiếu vitamin D và canxi thứ phát.',
                         'Khám kiểm tra vị trí catheter tĩnh mạch trung tâm không thấy dấu hiệu đỏ tấy hay chảy dịch '
                         'mủ, trẻ tỉnh táo nhưng thể lực yếu ớt ít vận động so với lứa tuổi.'],
    'chan_doan': 'Hội chứng ruột ngắn ở trẻ em sau cắt ruột rộng giai đoạn suy ruột mạn tính.',
    'chinh': [   'tiêu chảy mất nước phân lỏng ồ ạt chứa nhiều thức ăn chưa tiêu ngay sau khi ăn uống ở trẻ từng phẫu '
                 'thuật cắt đoạn ruột dài',
                 'kém hấp thu nặng dẫn đến sụt cân suy dinh dưỡng còi cọc chậm phát triển thể chất trầm trọng',
                 'tiền sử phẫu thuật cắt ruột non diện rộng do viêm ruột hoại tử sơ sinh teo ruột bẩm sinh hoặc xoắn '
                 'ruột'],
    'da_duyet': False,
    'dien_tien': 'mạn',
    'he_co_quan': 'dinh dưỡng',
    'ke_hoach': 'Áp dụng phác đồ phục hồi chức năng ruột đa chuyên khoa: phối hợp nuôi dưỡng tĩnh mạch tại bệnh viện '
                'hoặc tại nhà đảm bảo đủ năng lượng tăng trưởng kết hợp kích thích thích nghi ruột bằng ăn nhỏ giọt '
                'sữa thủy phân qua miệng hoặc sonde dạ dày, bổ sung vi chất sắt kẽm vitamin B12 và vitamin tan trong '
                'dầu.',
    'kham': 'Trẻ thể trạng suy dinh dưỡng nặng gầy teo cơ mỡ dưới da vùng mông đùi, trên thành bụng có vết sẹo mổ cũ '
            'dài đường giữa trên dưới rốn đã liền sẹo, vùng cổ ngực còn lưu ống thông tĩnh mạch trung tâm đường hầm '
            '(Broviac) sạch không sưng đỏ, bụng mềm trướng hơi nhẹ, da quanh hậu môn đỏ trợt nhẹ.',
    'nhom': 'nhi',
    'phu': [   'thiếu hụt đa vi chất dinh dưỡng điện giải thiếu máu xanh xao và loãng xương còi xương',
               'nguy cơ ứ mật tổn thương gan liên quan nuôi dưỡng tĩnh mạch kéo dài và nhiễm trùng catheter tĩnh mạch '
               'trung tâm',
               'hăm đỏ loét da vùng hậu môn tầng sinh môn nặng do phân có tính axit cao và đi ngoài liên tục'],
    'ten': 'hội chứng ruột ngắn ở trẻ em'},
    {   'bien_the_chan_doan': [   'Suy dinh dưỡng cấp tính nặng thể phù Kwashiorkor do thiếu protein nghiêm trọng.',
                              'Suy dinh dưỡng nặng thể phối hợp Marasmus - Kwashiorkor có phù chân độ 2.',
                              'Suy dinh dưỡng thể phù Kwashiorkor giai đoạn nguy kịch có nguy cơ hạ đường huyết và '
                              'nhiễm trùng huyết.',
                              'Suy dinh dưỡng cấp tính nặng Kwashiorkor kèm tổn thương da bong tróc và gan nhiễm mỡ.',
                              'Suy dinh dưỡng nặng thể phù ở trẻ sau cai sữa sớm chỉ ăn cháo loãng bột đường.',
                              'Suy dinh dưỡng thể phù Kwashiorkor biến chứng thiếu vitamin A và thiếu máu nặng.'],
    'bien_the_ke_hoach': [   'Nhập viện điều trị cấp cứu theo phác đồ 10 bước của WHO: phòng ngừa và xử trí hạ đường '
                             'huyết, hạ thân nhiệt và mất nước bằng dung dịch ReSoMal, điều trị nhiễm khuẩn ẩn bằng '
                             'kháng sinh phổ rộng, khởi đầu cho ăn thận trọng với sữa trị liệu F-75.',
                             'Tuyệt đối không dùng thuốc lợi tiểu để chữa phù dinh dưỡng và không truyền dịch tĩnh '
                             'mạch ồ ạt trừ khi trẻ bị sốc giảm thể tích nặng vì dễ gây suy tim quá tải tuần hoàn chết '
                             'người.',
                             'Bổ sung ngay Vitamin A liều cao theo tuổi vào ngày đầu nhập viện, bổ sung axit folic, '
                             'kẽm, đồng và vitamin tổng hợp; chú ý CHƯA bổ sung Sắt trong tuần đầu giai đoạn ổn định '
                             'để tránh vi khuẩn phát triển và tổn thương oxy hóa.',
                             'Cho trẻ uống sữa công thức đặc trị năng lượng thấp F-75 (75 kcal/100ml) từng lượng nhỏ '
                             'mỗi 2 giờ (hoặc đặt sonde dạ dày nhỏ giọt nếu trẻ biếng ăn nặng) trong giai đoạn ổn định '
                             'để tránh hội chứng nuôi ăn lại (Refeeding syndrome).',
                             'Khi trẻ hết phù, giảm gan to và thèm ăn trở lại (giai đoạn phục hồi), chuyển dần sang '
                             'sữa cao năng lượng F-100 hoặc thực phẩm điều trị ăn liền RUTF kết hợp bổ sung sắt để bắt '
                             'kịp đà tăng trưởng.',
                             'Chăm sóc vùng da trợt bong tróc bằng vệ sinh nhẹ nhàng, bôi kem kẽm oxit hoặc mỡ kháng '
                             'sinh tại chỗ bảo vệ da, ủ ấm cho trẻ theo phương pháp da kề da và tư vấn dinh dưỡng cân '
                             'bằng đạm - tinh bột cho gia đình trước xuất viện.'],
    'bien_the_kham': [   'Trẻ 2 tuổi lờ đờ ánh mắt thờ thẫn buồn bã, phù mềm trắng ấn lõm sâu ở hai mu bàn chân cẳng '
                         'chân và mi mắt, khuôn mặt tròn phúng nhưng cánh tay và bắp đùi teo nhão cơ rõ, da vùng bẹn '
                         'mông bong mảng vảy sẫm màu như sơn tróc để lộ lớp da non trợt hồng, tóc thưa mỏng màu vàng '
                         'hung xơ xác, gan to 3cm dưới bờ sườn phải.',
                         'Chu vi vòng cánh tay (MUAC) đo được 110mm, phù toàn thân độ 3 từ mu bàn chân lên đến đùi bộ '
                         'phận sinh dục và mặt, trẻ biếng ăn tuyệt đối đẩy thìa cháo ra, hạ thân nhiệt nhẹ 35,8 độ C.',
                         'Quan sát vùng da cẳng chân và lưng thấy các mảng tăng sắc tố nứt nẻ như vết rạn sơn khô, xen '
                         'kẽ vùng da trợt loét nông rỉ dịch dễ bội nhiễm, niêm mạc mắt và miệng nhợt nhạt do thiếu máu '
                         'phối hợp.',
                         'Bụng trướng căng mềm, gan sờ thấy 3,5cm dưới bờ sườn mật độ mềm bờ tù (gan nhiễm mỡ), trẻ '
                         'nằm co quắp bất động rên khẽ khi đụng chạm, nhịp tim hơi chậm 85 l/p.',
                         'Trẻ có dấu hiệu khô mắt nhẹ do thiếu vitamin A đi kèm (kết mạc mắt mất độ bóng ướt có vệt '
                         'bọt Bitot), phù trắng mềm mu bàn chân ấn giữ 3 giây để lại hố lõm sâu rõ rệt.',
                         'Tóc trên đỉnh đầu thưa lộ da đầu, sợi tóc mảnh khô quăn đổi màu từng khúc (dấu hiệu lá cờ), '
                         'phù mặt che lấp nét gầy hốc hác nhưng sờ xương sườn và cơ vai thấy teo mòn nặng.'],
    'chan_doan': 'Suy dinh dưỡng cấp tính nặng thể phù Kwashiorkor do thiếu protein nghiêm trọng.',
    'chinh': [   'phù mềm trắng ấn lõm đối xứng bắt đầu từ hai bàn chân cẳng chân rồi lan lên mặt tạo khuôn mặt tròn '
                 'như mặt trăng',
                 'tổn thương da đặc trưng bong tróc nứt nẻ từng mảng sẫm màu kiểu da vảy nến hoặc vệt sơn bong để lộ '
                 'nền da hồng trợt bên dưới',
                 'tóc thưa khô xơ xác giòn dễ rụng nhổ không đau và đổi sang màu hung đỏ vàng nhạt (dấu hiệu cờ hiệu)'],
    'da_duyet': False,
    'dien_tien': 'cấp',
    'he_co_quan': 'dinh dưỡng',
    'ke_hoach': 'Nhập viện điều trị cấp cứu theo phác đồ 10 bước phục hồi suy dinh dưỡng nặng của WHO: xử trí và phòng '
                'ngừa hạ đường huyết, hạ thân nhiệt và mất nước bằng dung dịch ReSoMal, điều trị nhiễm khuẩn ẩn bằng '
                'kháng sinh phổ rộng, khởi đầu cho ăn thận trọng với sữa trị liệu F-75 liều nhỏ nhiều bữa trước khi '
                'chuyển sang F-100 hoặc RUTF.',
    'kham': 'Trẻ 2 tuổi lờ đờ ánh mắt thờ thẫn buồn bã, phù mềm trắng ấn lõm sâu ở hai mu bàn chân cẳng chân và mi '
            'mắt, khuôn mặt tròn phúng nhưng cánh tay và bắp đùi teo nhão cơ rõ, da vùng bẹn mông bong mảng vảy sẫm '
            'màu như sơn tróc để lộ lớp da non trợt hồng, tóc thưa mỏng màu vàng hung xơ xác, gan to 3cm dưới bờ sườn '
            'phải mềm nhẵn.',
    'nhom': 'nhi',
    'phu': [   'trẻ cực kỳ bơ phờ thờ ơ ít phản ứng hoặc quấy khóc rên rỉ cáu gắt liên tục',
               'chán ăn nặng nề từ chối mọi thức ăn dẫn đến hạ đường huyết và hạ thân nhiệt dễ tử vong',
               'gan to mềm nhẵn do gan nhiễm mỡ và bụng chướng to'],
    'ten': 'suy dinh dưỡng thể phù Kwashiorkor'},
]

# Nhan gioi tinh cho cac khuon chi xuat hien o mot gioi:
GIOI_THEO_KHUON_MO_RONG = {
    "tiểu không tự chủ khi gắng sức": "nữ",
    "viêm vùng chậu": "nữ",
    "tiền sản giật": "nữ",
    "dọa sẩy thai": "nữ",
    "tắc tia sữa": "nữ",
    "rối loạn tiền mãn kinh": "nữ",
    "tinh hoàn ẩn bẩm sinh": "nam",
    "hẹp bao quy đầu bệnh lý ở trẻ": "nam",
    "lỗ tiểu lệch thấp hypospadias": "nam",
}

CHI_NU_MO_RONG = {k for k, v in GIOI_THEO_KHUON_MO_RONG.items() if v == "nữ"}
CHI_NAM_MO_RONG = {k for k, v in GIOI_THEO_KHUON_MO_RONG.items() if v == "nam"}

# Cac lo va dot khuon mo rong:
# DOT[1]: Khuon 201-400 (hien tai Lo 1 + Lo 2 gom 100 khuon da hien thuc hoa hoan tat 100%)
# DOT[2]: Khuon 401-600 (200 khuon Dot 2)
from src.khuon_lo_3 import BENH_LO_3, GIOI_TINH_LO_3  # noqa: E402
from src.khuon_lo_4 import BENH_LO_4, GIOI_TINH_LO_4  # noqa: E402
from src.khuon_lo_5 import BENH_LO_5, GIOI_TINH_LO_5  # noqa: E402
from src.khuon_lo_6 import BENH_LO_6, GIOI_TINH_LO_6  # noqa: E402
from src.khuon_lo_7 import BENH_LO_7, GIOI_TINH_LO_7  # noqa: E402
from src.khuon_lo_8 import BENH_LO_8, GIOI_TINH_LO_8  # noqa: E402

for _g in (GIOI_TINH_LO_3, GIOI_TINH_LO_4, GIOI_TINH_LO_5,
           GIOI_TINH_LO_6, GIOI_TINH_LO_7, GIOI_TINH_LO_8):
    GIOI_THEO_KHUON_MO_RONG.update(_g)
CHI_NU_MO_RONG = {k for k, v in GIOI_THEO_KHUON_MO_RONG.items() if v == "nữ"}
CHI_NAM_MO_RONG = {k for k, v in GIOI_THEO_KHUON_MO_RONG.items() if v == "nam"}

LO = {
    1: BENH_LO_1,
    2: BENH_LO_2,
    3: BENH_LO_3,
    4: BENH_LO_4,
    5: BENH_LO_5,
    6: BENH_LO_6,
    7: BENH_LO_7,
    8: BENH_LO_8,
}
DOT = {
    1: BENH_LO_1 + BENH_LO_2 + BENH_LO_3 + BENH_LO_4,
    2: BENH_LO_5 + BENH_LO_6 + BENH_LO_7 + BENH_LO_8,
}
BENH_DOT_1 = DOT[1]

BENH_MO_RONG = list(DOT[1]) + list(DOT[2])

TEN = frozenset(b["ten"] for b in BENH_MO_RONG)
TEN_THEO_DOT = {
    1: frozenset(b["ten"] for b in DOT[1]),
    2: frozenset(b["ten"] for b in DOT[2]),
}

# 350 ung vien da thiet ke he co quan cho cac Lo 2-8 (Khuon 251-600):
DANH_SACH_UNG_VIEN_350 = [   ('lồng ruột cấp ở nhũ nhi', 'nhi', 'cấp', 'nhi khoa', 'Cấp cứu ngoại tiêu hoá nhi phổ biến ở trẻ nhũ nhi bú mẹ'),
    ('teo đường mật bẩm sinh', 'nhi', 'mạn', 'nhi khoa', 'Bệnh lý gan mật bẩm sinh hiếm gặp cần chẩn đoán sớm'),
    (   'suy giáp bẩm sinh',
        'nhi',
        'mạn',
        'nội tiết - chuyển hoá',
        'Sàng lọc sơ sinh phát hiện sớm tránh chậm phát triển trí tuệ'),
    (   'tăng sản thượng thận bẩm sinh',
        'nhi',
        'mạn',
        'nội tiết - chuyển hoá',
        'Rối loạn tổng hợp cortisol di truyền lặn nhiễm sắc thể thường'),
    (   'còi xương do thiếu vitamin D',
        'nhi',
        'mạn',
        'dinh dưỡng',
        'Bệnh lý dinh dưỡng chuyển hoá xương thường gặp ở trẻ nhỏ'),
    ('bệnh celiac ở trẻ em', 'nhi', 'mạn', 'tiêu hoá', 'Bệnh không dung nạp gluten miễn dịch gây teo nhung mao ruột'),
    (   'xuất huyết giảm tiểu cầu miễn dịch nhi',
        'nhi',
        'cấp',
        'huyết học',
        'Bệnh lý huyết học miễn dịch thường sau đợt nhiễm siêu vi'),
    ('viêm màng não mủ ở trẻ em', 'nhi', 'cấp', 'truyền nhiễm', 'Cấp cứu truyền nhiễm thần kinh nhi khoa'),
    (   'viêm mô tế bào quanh hốc mắt trẻ',
        'nhi',
        'cấp',
        'mắt',
        'Nhiễm trùng phần mềm quanh mắt biến chứng từ viêm xoang'),
    (   'hẹp phì đại môn vị ở trẻ nhũ nhi',
        'nhi',
        'cấp',
        'nhi khoa',
        'Tắc nghẽn cơ học đường tiêu hoá trên ở trẻ 3-6 tuần tuổi'),
    ('bướu máu sơ sinh', 'nhi', 'mạn', 'nhi khoa', 'U mạch máu bẩm sinh lành tính thường gặp ở nhũ nhi'),
    ('bất sản da bẩm sinh', 'nhi', 'mạn', 'da liễu', 'Khuyết tật bẩm sinh da hiếm gặp vùng đỉnh đầu'),
    (   'hội chứng thận hư tiên phát ở trẻ em',
        'nhi',
        'mạn',
        'thận - tiết niệu',
        'Bệnh cầu thận tổn thương tối thiểu thường gặp ở lứa tuổi mầm non'),
    (   'viêm mao mạch dị ứng Schonlein-Henoch ở trẻ',
        'nhi',
        'cấp',
        'miễn dịch - dị ứng',
        'Viêm mạch máu nhỏ lắng đọng IgA thường gặp ở trẻ nhỏ'),
    ('hội chứng West co thắt nhũ nhi', 'nhi', 'mạn', 'thần kinh', 'Bệnh não động kinh khởi phát sớm ở trẻ nhũ nhi'),
    ('bại não thể co cứng', 'nhi', 'mạn', 'thần kinh', 'Rối loạn vận động không tiến triển do tổn thương não chu sinh'),
    ('xơ nang tụy', 'nhi', 'mạn', 'hô hấp', 'Bệnh di truyền gen CFTR ảnh hưởng hệ hô hấp và tiêu hoá'),
    ('hội chứng Down', 'nhi', 'mạn', 'nhi khoa', 'Bất thường nhiễm sắc thể trisomy 21 phổ biến nhất'),
    ('chậm phát triển tâm thần vận động', 'nhi', 'mạn', 'tâm thần', 'Chậm đạt các mốc phát triển nhận thức vận động'),
    ('tự kỷ ở trẻ em', 'nhi', 'mạn', 'tâm thần', 'Rối loạn phổ tự kỷ khiếm khuyết tương tác xã hội'),
    ('viêm khớp vô căn thiếu niên', 'nhi', 'mạn', 'cơ xương khớp', 'Viêm khớp mạn tính tự miễn khởi phát dưới 16 tuổi'),
    ('thoát vị rốn ở trẻ nhỏ', 'nhi', 'mạn', 'nhi khoa', 'Khuyết tật thành bụng bẩm sinh vùng rốn lành tính'),
    ('tinh hoàn ẩn bẩm sinh', 'nhi', 'mạn', 'nam khoa', 'Bất thường di chuyển tinh hoàn cần can thiệp hạ tinh hoàn'),
    ('hẹp bao quy đầu bệnh lý ở trẻ', 'nhi', 'mạn', 'nam khoa', 'Chít hẹp xơ dính bao quy đầu cản trở tiểu tiện'),
    ('lỗ tiểu lệch thấp hypospadias', 'nhi', 'mạn', 'nam khoa', 'Dị tật bẩm sinh lỗ tiểu mặt dưới dương vật'),
    (   'trào ngược bàng quang niệu quản ở trẻ',
        'nhi',
        'mạn',
        'thận - tiết niệu',
        'Nguyên nhân hàng đầu gây nhiễm trùng tiết niệu tái phát ở trẻ'),
    (   'viêm tai giữa màng nhĩ thủng ở trẻ',
        'nhi',
        'mạn',
        'tai mũi họng',
        'Viêm tai giữa mạn tính chảy mủ thủng màng nhĩ'),
    ('viêm xoang hàm cấp ở trẻ em', 'nhi', 'cấp', 'tai mũi họng', 'Nhiễm trùng xoang mặt thường gặp sau cảm lạnh'),
    (   'áp xe quanh amidan ở trẻ',
        'nhi',
        'cấp',
        'tai mũi họng',
        'Biến chứng tụ mủ khoang quanh amidan gây khít hàm nuốt khó'),
    (   'thở rít thanh quản bẩm sinh mềm sụn thanh nhiệt',
        'nhi',
        'mạn',
        'tai mũi họng',
        'Mềm sụn thanh quản là nguyên nhân thở rít bẩm sinh phổ biến nhất'),
    (   'dị vật đường thở bỏ quên ở trẻ',
        'nhi',
        'mạn',
        'hô hấp',
        'Hội chứng xâm nhập bỏ sót gây ho dai dẳng viêm phổi tái diễn'),
    ('viêm phế quản co thắt ở trẻ', 'nhi', 'cấp', 'hô hấp', 'Tăng phản ứng phế quản sau nhiễm virus hô hấp'),
    ('giãn phế quản bẩm sinh ở trẻ', 'nhi', 'mạn', 'hô hấp', 'Tổn thương cấu trúc phế quản giãn không hồi phục'),
    ('nhiễm trùng sơ sinh muộn', 'nhi', 'cấp', 'truyền nhiễm', 'Nhiễm khuẩn mắc phải sau ngày thứ 7 sau sinh'),
    ('sốt co giật phức tạp ở trẻ', 'nhi', 'cấp', 'thần kinh', 'Cơn co giật cục bộ hoặc kéo dài trên 15 phút khi sốt'),
    ('đau nửa đầu liệt nửa người ở trẻ', 'nhi', 'cấp', 'thần kinh', 'Thể đau nửa đầu gia đình hiếm gặp ở trẻ em'),
    (   'hạ canxi máu sơ sinh do suy cận giáp',
        'nhi',
        'cấp',
        'nội tiết - chuyển hoá',
        'Rối loạn chuyển hoá canxi gây cơn tetany co cứng cơ'),
    (   'thiếu men G6PD gây tán huyết cấp ở trẻ',
        'nhi',
        'cấp',
        'huyết học',
        'Thiếu men di truyền liên kết X gây vỡ hồng cầu khi gặp tác nhân oxy hóa'),
    ('bệnh lỵ amip ở trẻ em', 'nhi', 'cấp', 'truyền nhiễm', 'Nhiễm Entamoeba histolytica gây hội chứng lỵ'),
    ('nhiễm nấm candida da bẹn ở trẻ nhũ nhi', 'nhi', 'cấp', 'da liễu', 'Hăm tã bội nhiễm nấm men Candida albicans'),
    ('chàm thể tạng bội nhiễm ở trẻ', 'nhi', 'cấp', 'da liễu', 'Viêm da cơ địa đợt cấp bội nhiễm tụ cầu vàng'),
    ('vảy nến thể giọt ở trẻ em', 'nhi', 'cấp', 'da liễu', 'Vảy nến bùng phát sau đợt viêm họng liên cầu'),
    ('nhược thị ở trẻ em', 'nhi', 'mạn', 'mắt', 'Giảm thị lực một hoặc hai mắt do tật khúc xạ hoặc lác'),
    ('lác trong bẩm sinh ở trẻ', 'nhi', 'mạn', 'mắt', 'Lác mắt khởi phát sớm trong 6 tháng đầu đời'),
    ('viêm kết mạc sơ sinh do lậu', 'nhi', 'cấp', 'mắt', 'Cấp cứu nhãn khoa lây truyền qua đường sinh đẻ'),
    (   'nứt kẽ hậu môn ở trẻ em do táo bón',
        'nhi',
        'cấp',
        'tiêu hoá',
        'Tổn thương rách niêm mạc ống hậu môn do phân cứng'),
    (   'hội chứng nôn chu kỳ ở trẻ em',
        'nhi',
        'mạn',
        'tiêu hoá',
        'Rối loạn chức năng đường tiêu hoá khởi phát từng đợt tái diễn'),
    ('dị ứng sữa đậu nành ở trẻ nhũ nhi', 'nhi', 'mạn', 'miễn dịch - dị ứng', 'Dị ứng đạm thực vật thay thế sữa bò'),
    ('hội chứng ruột ngắn ở trẻ em', 'nhi', 'mạn', 'dinh dưỡng', 'Hội chứng kém hấp thu nặng sau phẫu thuật cắt ruột'),
    ('suy dinh dưỡng thể phù Kwashiorkor', 'nhi', 'cấp', 'dinh dưỡng', 'Suy dinh dưỡng protein nặng có phù dinh dưỡng'),
    (   'viêm gân lồi cầu trong xương cánh tay',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Hội chứng khuỷu tay người chơi golf viêm gân gấp cổ tay'),
    ('viêm bao gân De Quervain', 'người lớn', 'mạn', 'cơ xương khớp', 'Viêm bao gân cơ dạng dài và duỗi ngắn ngón cái'),
    (   'viêm bao hoạt dịch mỏm khuỷu',
        'người lớn',
        'cấp',
        'cơ xương khớp',
        'Tràn dịch viêm bọng hoạt dịch sau mỏm khuỷu'),
    (   'viêm bao hoạt dịch trước xương bánh chè',
        'người lớn',
        'cấp',
        'cơ xương khớp',
        'Tổn thương hoạt dịch do quỳ gối tì đè nhiều'),
    (   'hội chứng chèn ép khoang dưới mỏm cùng vai',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Hẹp khoang dưới mỏm cùng vai cọ xát gân cơ trên gai'),
    ('rách chóp xoay khớp vai', 'người lớn', 'mạn', 'cơ xương khớp', 'Tổn thương đứt rách gân chóp xoay vai mạn tính'),
    (   'viêm khớp cùng chậu',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Viêm khớp trục đặc trưng trong nhóm bệnh cột sống huyết thanh âm tính'),
    (   'hoại tử vô mạch chỏm xương đùi',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Thiếu máu nuôi dưỡng gây xẹp chỏm xương đùi vô trùng'),
    (   'nang bao hoạt dịch khoeo chân Baker',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Nang thoát vị màng hoạt dịch vùng khoeo chân'),
    (   'hội chứng dải chậu chày',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Viêm cọ xát dải chậu chày ở vận động viên chạy bộ'),
    (   'viêm gân bánh chè',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Tổn thương gân bánh chè jumper knee ở người chơi thể thao'),
    (   'thoái hóa khớp bàn ngón tay',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Hạt Heberden và Bouchard thoái hóa biến dạng ngón tay'),
    (   'biến dạng ngón chân cái vẹo ngoài Hallux valgus',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Vẹo trục ngón chân cái bunion gây đau buốt đi lại'),
    ('ngón chân hình búa', 'người lớn', 'mạn', 'cơ xương khớp', 'Biến dạng co rút gân gập khớp liên đốt ngón chân'),
    (   'viêm bao hoạt dịch khớp cổ chân',
        'người lớn',
        'cấp',
        'cơ xương khớp',
        'Tràn dịch sưng đau bao hoạt dịch quanh mắt cá chân'),
    ('gãy kín xương đòn do ngã', 'cả hai', 'cấp', 'chấn thương', 'Gãy xương thường gặp nhất khi ngã đập vai'),
    (   'trật khớp vai tái hồi',
        'người lớn',
        'mạn',
        'chấn thương',
        'Trật khớp vai lặp đi lặp lại sau chấn thương rách sụn viền'),
    ('trật khớp khuỷu tay', 'cả hai', 'cấp', 'chấn thương', 'Sai khớp khuỷu tay ra sau do ngã chống tay'),
    ('bong gân ngón tay do bóng rổ', 'cả hai', 'cấp', 'chấn thương', 'Tổn thương dây chằng bên khớp liên đốt ngón tay'),
    ('rách sụn chêm khớp gối', 'người lớn', 'mạn', 'chấn thương', 'Rách sụn chêm trong hoặc ngoài gây kẹt khớp gối'),
    ('đụng dập phần mềm đùi do chấn thương', 'cả hai', 'cấp', 'chấn thương', 'Tụ máu trong cơ tứ đầu đùi sau va đập'),
    (   'gãy xương sườn đơn thuần do tai nạn',
        'người lớn',
        'cấp',
        'chấn thương',
        'Gãy rạn 1-2 xương sườn kín không tổn thương màng phổi'),
    ('gãy rạn xương bánh chè kín', 'cả hai', 'cấp', 'chấn thương', 'Nứt rạn xương bánh chè không di lệch do đập gối'),
    (   'tổn thương rách dây chằng bên trong khớp gối',
        'cả hai',
        'cấp',
        'chấn thương',
        'Rách MCL khớp gối sau chấn thương vẹo ngoài'),
    (   'hội chứng cơ hình lê chèn ép thần kinh tọa',
        'người lớn',
        'mạn',
        'thần kinh',
        'Cơ hình lê co thắt phì đại chèn ép dây thần kinh hông to'),
    (   'liệt dây thần kinh quay gây bàn tay rủ',
        'người lớn',
        'cấp',
        'thần kinh',
        'Tổn thương thần kinh quay rủ cổ tay sau tì đè ngủ say'),
    (   'hội chứng đường hầm xương trụ ở khuỷu',
        'người lớn',
        'mạn',
        'thần kinh',
        'Chèn ép thần kinh trụ tại rãnh ròng rọc khuỷu tay'),
    (   'đau thần kinh đùi bì dị cảm',
        'người lớn',
        'mạn',
        'thần kinh',
        'Hội chứng meralgia paresthetica tê rát mặt ngoài đùi'),
    (   'đau dây thần kinh liên sườn sau zona',
        'người lớn',
        'mạn',
        'thần kinh',
        'Đau dây thần kinh sau zona dai dẳng trên 3 tháng'),
    (   'nhược cơ thể mắt',
        'người lớn',
        'mạn',
        'thần kinh',
        'Bệnh tự miễn màng sau synap thần kinh cơ gây sụp mi nhìn đôi'),
    (   'liệt dây thần kinh mác chung bàn tay rủ chân',
        'người lớn',
        'cấp',
        'thần kinh',
        'Tổn thương thần kinh mác sâu chỏm xương mác gây chân rủ'),
    (   'xơ cứng rải rác thể tái phát thuyên giảm',
        'người lớn',
        'mạn',
        'thần kinh',
        'Bệnh thoái hóa myelin tự miễn hệ thần kinh trung ương'),
    (   'teo cơ tủy sống khởi phát người lớn',
        'người lớn',
        'mạn',
        'thần kinh',
        'Bệnh nơ-ron vận động tủy sống SMA type 4'),
    (   'co thắt nửa mặt vô căn',
        'người lớn',
        'mạn',
        'thần kinh',
        'Co thắt giật cơ nửa mặt do xung đột mạch máu thần kinh VII'),
    ('run vô căn gia đình', 'người lớn', 'mạn', 'thần kinh', 'Rối loạn vận động run tư thế và hành động đối xứng'),
    ('múa giật Huntington', 'người lớn', 'mạn', 'thần kinh', 'Bệnh di truyền gen trội lặp đoạn CAG thể vân thoái hóa'),
    ('bệnh rỗng tủy sống cổ', 'người lớn', 'mạn', 'thần kinh', 'Hình thành khoang nang chứa dịch trong tủy sống cổ'),
    (   'hội chứng Guillain-Barre thể nhẹ phục hồi',
        'người lớn',
        'mạn',
        'thần kinh',
        'Viêm đa rễ dây thần kinh hủy myelin cấp tính giai đoạn phục hồi'),
    (   'đau dây thần kinh thiệt hầu',
        'người lớn',
        'mạn',
        'thần kinh',
        'Cơn đau chói như điện giật vùng đáy lưỡi và họng'),
    (   'viêm đa rễ dây thần kinh mạn tính CIDP',
        'người lớn',
        'mạn',
        'thần kinh',
        'Bệnh lý đa dây thần kinh hủy myelin viêm mạn tính'),
    ('bệnh cơ viêm đa cơ tự miễn', 'người lớn', 'mạn', 'cơ xương khớp', 'Viêm cơ vô căn tự miễn yếu gốc chi đối xứng'),
    (   'viêm da cơ tự miễn',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Viêm đa cơ kèm ban đỏ Gottron và phù mí mắt tím Gottron'),
    (   'viêm khớp vảy nến',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Viêm khớp ngón tay hình khúc dồi trên bệnh nhân vảy nến'),
    (   'hội chứng Sjogren khô mắt khô miệng',
        'người lớn',
        'mạn',
        'miễn dịch - dị ứng',
        'Bệnh tự miễn tổn thương tuyến ngoại tiết lệ và nước bọt'),
    (   'bệnh Still người lớn',
        'người lớn',
        'cấp',
        'miễn dịch - dị ứng',
        'Bệnh tự viêm sốt cao thất thường ban hồng và viêm khớp'),
    (   'giả gout do lắng đọng pyrophosphate canxi',
        'người lớn',
        'cấp',
        'cơ xương khớp',
        'Bệnh lắng đọng tinh thể CPPD khớp gối cấp tính'),
    ('viêm sụn sườn Tietze', 'người lớn', 'cấp', 'cơ xương khớp', 'Viêm sưng đau khớp sụn sườn 2-3 một bên lành tính'),
    (   'gù vẹo cột sống ngực thắt lưng thiếu niên',
        'cả hai',
        'mạn',
        'cơ xương khớp',
        'Cong vẹo cột sống vô căn AIS góc Cobb trên 15 độ'),
    (   'trượt đốt sống thắt lưng độ 1',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Trượt thân đốt sống L4-L5 gây đau thắt lưng cơ năng'),
    (   'hẹp ống sống thắt lưng thoái hóa',
        'người lớn',
        'mạn',
        'cơ xương khớp',
        'Hẹp ống sống gây đau cách hồi thần kinh khi đi lại'),
    (   'sa sút trí tuệ Alzheimer giai đoạn nhẹ',
        'người lớn',
        'mạn',
        'lão khoa',
        'Suy giảm trí nhớ phân đoạn và định hướng không gian'),
    (   'hội chứng suy yếu dễ tổn thương ở người già',
        'người lớn',
        'mạn',
        'lão khoa',
        'Giảm dự trữ sinh lý tăng nguy cơ té ngã và nhập viện'),
    (   'ngã tái diễn ở người cao tuổi',
        'người lớn',
        'mạn',
        'lão khoa',
        'Hội chứng lão khoa do rối loạn thăng bằng và thị lực'),
    (   'loét tì đè độ 1-2 vùng cùng cụt ở người già',
        'người lớn',
        'mạn',
        'lão khoa',
        'Tổn thương thiếu máu cục bộ do bất động nằm lâu'),
    (   'hạ natri máu mạn tính ở người cao tuổi',
        'người lớn',
        'mạn',
        'lão khoa',
        'Rối loạn điện giải mạn do hội chứng SIADH hoặc thuốc'),
    (   'mê sảng cấp tính ở người cao tuổi',
        'người lớn',
        'cấp',
        'lão khoa',
        'Rối loạn ý thức và chú ý dao động sau nhiễm trùng'),
    (   'đa bệnh lý dùng nhiều thuốc ở người già',
        'người lớn',
        'mạn',
        'lão khoa',
        'Hội chứng Polypharmacy tương tác thuốc bất lợi'),
    (   'rối loạn nuốt ở người cao tuổi sau tai biến',
        'người lớn',
        'mạn',
        'lão khoa',
        'Suy giảm cơ nâng vòm hầu gây nghẹn sặc chất lỏng'),
    (   'viêm teo niêm mạc âm đạo do lão hóa',
        'người lớn',
        'mạn',
        'lão khoa',
        'Hội chứng niệu dục sau mãn kinh teo khô rát'),
    (   'trầm cảm muộn ở người cao tuổi',
        'người lớn',
        'mạn',
        'lão khoa',
        'Rối loạn khí sắc biểu hiện bằng triệu chứng cơ thể'),
    (   'bàng quang tăng hoạt OAB',
        'người lớn',
        'mạn',
        'thận - tiết niệu',
        'Tiểu gấp tiểu nhiều lần tiểu không kiểm soát do thôi thúc'),
    (   'viêm bàng quang kẽ mạn tính',
        'người lớn',
        'mạn',
        'thận - tiết niệu',
        'Hội chứng đau bàng quang mạn tính không do vi khuẩn'),
    (   'tiểu ra máu đại thể không triệu chứng',
        'người lớn',
        'cấp',
        'thận - tiết niệu',
        'Dấu hiệu cảnh báo khối u đường tiết niệu cần nội soi'),
    (   'thận đa nang di truyền trội',
        'người lớn',
        'mạn',
        'thận - tiết niệu',
        'Bệnh ADPKD nang thận to hai bên giảm dần chức năng'),
    (   'hẹp niệu đạo sau chấn thương',
        'người lớn',
        'mạn',
        'thận - tiết niệu',
        'Xơ hẹp lòng niệu đạo gây tiểu khó tia nước tiểu nhỏ'),
    (   'sỏi san hô đài bể thận',
        'người lớn',
        'mạn',
        'thận - tiết niệu',
        'Sỏi kích thước lớn lấp đầy các đài thận gây ứ nước'),
    (   'trào ngược bàng quang niệu quản người lớn',
        'người lớn',
        'mạn',
        'thận - tiết niệu',
        'Trào ngược nước tiểu bàng quang lên thận gây viêm mạn'),
    ('sa bàng quang độ 2', 'người lớn', 'mạn', 'thận - tiết niệu', 'Sa thành trước âm đạo kèm sa cổ bàng quang'),
    (   'viêm tuyến tiền liệt mạn tính không do vi khuẩn',
        'người lớn',
        'mạn',
        'nam khoa',
        'Hội chứng đau vùng chậu mạn tính CPPS ở nam giới'),
    (   'viêm tuyến tiền liệt cấp do vi khuẩn',
        'người lớn',
        'cấp',
        'nam khoa',
        'Nhiễm trùng cấp tính tuyến tiền liệt sốt cao tiểu buốt'),
    (   'xoắn tinh hoàn dọa nghẹt',
        'người lớn',
        'cấp',
        'nam khoa',
        'Cấp cứu ngoại nam khoa xoắn thừng tinh thiếu máu nuôi'),
    (   'tràn dịch màng tinh hoàn người lớn',
        'người lớn',
        'mạn',
        'nam khoa',
        'Tụ dịch trong bao tinh hoàn gây bìu to căng'),
    ('nang mào tinh hoàn', 'người lớn', 'mạn', 'nam khoa', 'Nang chứa tinh trùng lành tính ở đầu mào tinh'),
    (   'viêm bao quy đầu bán cấp do nấm',
        'người lớn',
        'cấp',
        'nam khoa',
        'Viêm đỏ trợt quy đầu do nấm Candida ở người tiểu đường'),
    (   'xuất tinh sớm tiên phát',
        'người lớn',
        'mạn',
        'nam khoa',
        'Rối loạn chức năng tình dục nam giới xuất tinh dưới 1 phút'),
    (   'vô sinh nam do suy giảm số lượng tinh trùng',
        'người lớn',
        'mạn',
        'nam khoa',
        'Thiểu tinh trùng nồng độ dưới 15 triệu/ml'),
    ('bệnh cong dương vật Peyronie', 'người lớn', 'mạn', 'nam khoa', 'Mảng xơ hóa thể hang gây cong vẹo đau khi cương'),
    (   'suy tuyến sinh dục nam muộn mãn dục nam',
        'người lớn',
        'mạn',
        'nam khoa',
        'Suy giảm testosterone theo tuổi tác gây mệt mỏi'),
    (   'cương cứng dương vật kéo dài thể thiếu máu',
        'người lớn',
        'cấp',
        'nam khoa',
        'Cấp cứu nam khoa priapism kéo dài trên 4 giờ'),
    (   'đái tháo đường típ 1 mới phát hiện',
        'cả hai',
        'cấp',
        'nội tiết - chuyển hoá',
        'Bệnh tự miễn phá hủy tế bào beta tụy phụ thuộc insulin'),
    (   'u tuyến yên tiết prolactin prolactinoma',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'U lành tuyến yên tăng prolactin gây tiết sữa mất kinh'),
    (   'bệnh to đầu chi Acromegaly',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'Tăng tiết GH sau tuổi dậy thì gây to bàn chân bàn tay'),
    (   'viêm tuyến giáp Hashimoto',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'Viêm tuyến giáp tự miễn mạn tính gây suy giáp nguyên phát'),
    (   'bướu cổ đơn thuần dịch tễ thiếu iod',
        'cả hai',
        'mạn',
        'nội tiết - chuyển hoá',
        'Phì đại tuyến giáp lan tỏa không rối loạn chức năng'),
    (   'cường cận giáp tiên phát do u tuyến',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'Tăng hormone PTH gây tăng canxi máu và sỏi thận'),
    (   'suy cận giáp sau phẫu thuật tuyến giáp',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'Tổn thương tuyến cận giáp gây hạ canxi máu mạn'),
    (   'u tủy thượng thận Pheochromocytoma',
        'người lớn',
        'cấp',
        'nội tiết - chuyển hoá',
        'U tủy thượng thận tăng tiết catecholamine kịch phát'),
    (   'hội chứng Conn cường aldosteron tiên phát',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'U vỏ thượng thận tăng aldosteron gây tăng HA và hạ kali'),
    (   'đái tháo nhạt do căn nguyên trung ương',
        'cả hai',
        'mạn',
        'nội tiết - chuyển hoá',
        'Thiếu hụt hormone chống bài niệu ADH tuyến yên'),
    (   'tăng triglycerid máu nặng nguy cơ viêm tụy',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'Triglycerid trên 10 mmol/l nguy cơ viêm tụy cấp'),
    (   'bệnh nhiễm sắc tố sắt hemochromatosis',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'Rối loạn quá tải sắt di truyền tổn thương gan tim tụy'),
    (   'bệnh Wilson lắng đọng đồng',
        'cả hai',
        'mạn',
        'nội tiết - chuyển hoá',
        'Rối loạn chuyển hoá đồng lắng đọng vòng Kayser-Fleischer'),
    (   'loãng xương vô căn ở nam giới',
        'người lớn',
        'mạn',
        'nội tiết - chuyển hoá',
        'Giảm mật độ xương T-score dưới -2.5 ở nam giới'),
    (   'thiếu vitamin D ở người trưởng thành',
        'người lớn',
        'mạn',
        'dinh dưỡng',
        'Nồng độ 25-OH-D huyết thanh dưới 20 ng/ml'),
    (   'thiếu kẽm dinh dưỡng mạn tính',
        'cả hai',
        'mạn',
        'dinh dưỡng',
        'Thiếu vi chất kẽm gây rụng tóc viêm da quanh hốc'),
    ('thiếu máu do thiếu acid folic', 'cả hai', 'mạn', 'huyết học', 'Thiếu máu hồng cầu to do chế độ ăn thiếu folate'),
    (   'bệnh Beriberi thiếu vitamin B1 thể ướt',
        'người lớn',
        'cấp',
        'dinh dưỡng',
        'Thiếu hụt thiamine cấp tính suy tim cung lượng cao'),
    (   'bệnh Scorbut thiếu vitamin C',
        'cả hai',
        'mạn',
        'dinh dưỡng',
        'Thiếu acid ascorbic gây xuất huyết chân răng xuất huyết da'),
    (   'thiếu vitamin A gây quáng gà khô mắt',
        'cả hai',
        'mạn',
        'dinh dưỡng',
        'Khô giác mạc và vệt Bitot do thiếu vitamin A'),
    (   'hội chứng tái nuôi dưỡng refeeding syndrome',
        'người lớn',
        'cấp',
        'dinh dưỡng',
        'Rối loạn điện giải hạ phospho máu sau nhịn đói lâu ngày'),
    (   'lao hạch ngoại biên vùng cổ',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Lao ngoài phổi thể chuỗi hạch cổ dính nhuyễn hóa bã đậu'),
    (   'lao màng bụng thể cổ trướng',
        'người lớn',
        'mạn',
        'truyền nhiễm',
        'Lao màng bụng dịch tự do giàu protein và tế bào lympho'),
    (   'lao xương khớp cột sống bệnh Pott',
        'người lớn',
        'mạn',
        'truyền nhiễm',
        'Lao thân đốt sống đĩa đệm gây gù gập cột sống áp xe lạnh'),
    ('lao màng tinh hoàn', 'người lớn', 'mạn', 'truyền nhiễm', 'Lao hệ niệu sinh dục mạn tính nề chắc mào tinh'),
    ('lao da lupus vulgaris', 'cả hai', 'mạn', 'truyền nhiễm', 'Lao da hạt bã đậu sẹo co kéo mạn tính'),
    ('lao thận', 'người lớn', 'mạn', 'truyền nhiễm', 'Tiểu ra mủ vô khuẩn nước tiểu toan tính đặc trưng của lao'),
    (   'sốt rét cơn do Plasmodium vivax tái phát',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Sốt rét tái phát xa do thể ngủ hypnozoite trong gan'),
    (   'sốt rét thể thông thường do Plasmodium falciparum',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Sốt rét nhiệt đới nguy cơ biến chứng sốt rét ác tính'),
    (   'bệnh sán lá gan lớn Fasciola',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Nhiễm sán lá gan từ rau thủy sinh gây tổn thương gan'),
    (   'bệnh sán lá gan nhỏ Clonorchis',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Nhiễm sán từ gỏi cá sống gây viêm xơ đường mật mạn'),
    (   'bệnh sán lá phổi Paragonimus',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Nhiễm sán do ăn cua đá nướng ho ra máu nhầm lao'),
    ('ấu trùng sán lợn dưới da và cơ', 'cả hai', 'mạn', 'truyền nhiễm', 'Nang ấu trùng Taenia solium hạt gạo dưới da'),
    (   'ấu trùng sán dải chó Echinococcus ở gan',
        'người lớn',
        'mạn',
        'truyền nhiễm',
        'Nang sán hydatid gan vỏ vôi hóa cản quang'),
    (   'nhiễm giun lươn Strongyloides đường ruột',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Ký sinh trùng tự nhiễm mạn tính nguy cơ hội chứng tăng nhiễm'),
    (   'hội chứng ấu trùng di chuyển dưới da do giun móc chó mèo',
        'cả hai',
        'cấp',
        'da liễu',
        'Đường ngoằn ngoèo đỏ ngứa dưới da bàn chân'),
    (   'hội chứng ấu trùng di chuyển nội tạng Toxocara',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Nhiễm giun đũa chó mèo tăng bạch cầu ái toan kéo dài'),
    (   'nhiễm giun chỉ bạch huyết phù chân voi',
        'người lớn',
        'mạn',
        'truyền nhiễm',
        'Tắc nghẽn mạch bạch huyết do giun Wuchereria bancrofti'),
    (   'nhiễm amip ruột thể lỵ cấp tính',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Lỵ amip Entamoeba histolytica phân nhầy máu mót rặn'),
    (   'nhiễm trùng roi Giardia lamblia tá tràng',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Nhiễm đơn bào tá tràng gây tiêu chảy kéo dài phân mỡ'),
    (   'viêm ruột do Clostridioides difficile sau kháng sinh',
        'người lớn',
        'cấp',
        'tiêu hoá',
        'Viêm đại tràng giả mạc sau dùng kháng sinh dài ngày'),
    (   'bệnh tả dịch tả Vibrio cholerae',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Tiêu chảy xối xả nước vo gạo mất nước trụy mạch'),
    (   'bệnh than thể da do tiếp xúc gia súc',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Nốt mụn mủ hoại tử vảy đen do Bacillus anthracis'),
    (   'bệnh dại giai đoạn tiền triệu sau chó cắn',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Virus Lyssavirus giai đoạn ngứa rát vết cắn sợ gió sợ nước'),
    (   'bệnh uốn ván thể cục bộ sau vết thương dơ',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Ngoại độc tố tetanospasmin gây co cứng cơ cục bộ'),
    (   'nhiễm vi khuẩn ăn thịt người Aeromonas hydrophila',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Viêm mô bào hoại tử tiến triển sau tiếp xúc nước ngọt dơ'),
    (   'bệnh Whitmore thể viêm phổi áp xe hóa Melioidosis',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Nhiễm Burkholderia pseudomallei từ đất bùn vi khuẩn ăn thịt người'),
    (   'nhiễm nấm huyết nấm sâu Cryptococcus',
        'người lớn',
        'mạn',
        'truyền nhiễm',
        'Nhiễm nấm men có bao hạt Cryptococcus neoformans'),
    (   'nhiễm nấm Histoplasma phổi thể bán cấp',
        'người lớn',
        'mạn',
        'truyền nhiễm',
        'Nấm lưỡng hình lây từ phân chim phân dơi'),
    (   'bệnh do virus Epstein-Barr tăng bạch cầu đơn nhân',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Hội chứng mononucleosis sốt đau họng hạch to tế bào lympho không điển hình'),
    (   'nhiễm Cytomegalovirus thể tiềm tàng bùng phát',
        'người lớn',
        'mạn',
        'truyền nhiễm',
        'Tái hoạt virus CMV ở người suy giảm miễn dịch'),
    (   'bệnh sốt xuất huyết hantavirus sốt kèm suy thận',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Hội chứng sốt xuất huyết kèm suy thận lây qua chuột'),
    (   'sốt Chikungunya đau nhức khớp kéo dài',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Virus lây truyền qua muỗi Aedes gây đau khớp dữ dội'),
    (   'nhiễm virus Zika gây phát ban đau khớp',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Sốt nhẹ phát ban kết mạc đỏ nguy cơ dị tật thai'),
    (   'sốt mò thể nhẹ có vết loét eschar đặc trưng',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Nhiễm Orientia tsutsugamushi vết loét hoại tử lõm đen'),
    (   'bệnh phong thể củ Hansen',
        'cả hai',
        'mạn',
        'truyền nhiễm',
        'Mảng da mất cảm giác nóng lạnh và xúc giác do Mycobacterium leprae'),
    (   'bệnh mèo cào do Bartonella henselae',
        'cả hai',
        'bán cấp',
        'truyền nhiễm',
        'Viêm hạch sưng to vùng nách bẹn sau vết cào của mèo'),
    (   'nhiễm trùng vết cắn động vật do Pasteurella',
        'cả hai',
        'cấp',
        'truyền nhiễm',
        'Viêm mô tế bào cấp tính sau vết chó mèo cắn'),
    (   'viêm hạch mủ bẹn do vi khuẩn sinh dục',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Hội chứng bục hạch bẹn rò mủ lây qua đường tình dục'),
    (   'hạ cam mềm Chancroid',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Vết loét sinh dục mềm đau đáy bẩn do Haemophilus ducreyi'),
    (   'viêm niệu đạo không do lậu cầu',
        'người lớn',
        'cấp',
        'truyền nhiễm',
        'Viêm niệu đạo rỉ dịch trong do Chlamydia hoặc Ureaplasma'),
    (   'bệnh viêm loét miệng aphthous lớn tái diễn',
        'cả hai',
        'mạn',
        'tiêu hoá',
        'Loét áp-tơ Sutton đường kính trên 1cm lâu lành để lại sẹo'),
    (   'viêm thực quản do trào ngược độ B Los Angeles',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'Vết trợt niêm mạc thực quản dài trên 5mm không liên tục'),
    (   'co thắt tâm vị thực quản Achalasia',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'Mất nhu động thực quản và không giãn cơ thắt thực quản dưới'),
    (   'viêm loét hành tá tràng biến chứng hẹp môn vị nhẹ',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'Loét tá tràng xơ chai gây hẹp lưu thông thức ăn dạ dày'),
    (   'túi thừa đại tràng sigma viêm cấp tính',
        'người lớn',
        'cấp',
        'tiêu hoá',
        'Viêm ruột thừa bên trái đau hố chậu trái sốt nhẹ'),
    (   'viêm túi mật mạn tính do sỏi bùn',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'Thành túi mật dày xơ hóa sỏi bùn mật tái diễn'),
    (   'u gan lành tính u máu thể hang gan',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'Hemangioma gan kích thước lớn phát hiện qua siêu âm'),
    (   'u tuyến tụy nội tiết insulinoma gây hạ đường huyết',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'U tế bào beta tụy tiết insulin gây tam chứng Whipple'),
    (   'viêm đại tràng vi thể thể collagen',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'Tiêu chảy nước mạn tính niêm mạc soi bình thường có dải collagen'),
    (   'viêm trực tràng sau xạ trị vùng chậu',
        'người lớn',
        'mạn',
        'tiêu hoá',
        'Chảy máu trực tràng mạn do giãn mao mạch sau xạ trị ung thư'),
    ('viêm kết mạc mùa xuân ở thiếu niên', 'cả hai', 'mạn', 'mắt', 'Viêm kết mạc dị ứng nhú gai khổng lồ vòm sụn'),
    (   'viêm củng mạc trước hoại tử',
        'người lớn',
        'mạn',
        'mắt',
        'Bệnh lý viêm mạch tự miễn gây mỏng củng mạc thủng nhãn cầu'),
    (   'viêm màng bồ đào trước vô căn',
        'người lớn',
        'cấp',
        'mắt',
        'Cương tụ rìa tủa giác mạc mủ tiền phòng đau nhức mắt'),
    (   'bong võng mạc nguyên phát có rách võng mạc',
        'người lớn',
        'cấp',
        'mắt',
        'Hiện tượng ruồi bay chớp sáng kèm rèm đen che thị trường'),
    (   'tắc tĩnh mạch trung tâm võng mạc',
        'người lớn',
        'cấp',
        'mắt',
        'Mất thị lực đột ngột xuất huyết võng mạc hình ngọn lửa bão hòa'),
    (   'thoái hóa hoàng điểm tuổi già thể khô',
        'người lớn',
        'mạn',
        'mắt',
        'Lắng đọng chất drusen vùng hoàng điểm giảm thị lực trung tâm'),
    (   'bệnh võng mạc đái tháo đường tiền tăng sinh',
        'người lớn',
        'mạn',
        'mắt',
        'Vi phình mạch xuất huyết chấm xuất huyết thiếu máu võng mạc'),
    (   'mộng thịt độ 3 xâm lấn giác mạc',
        'người lớn',
        'mạn',
        'mắt',
        'Màng mạch xơ xâm lấn qua rìa giác mạc che phủ đồng tử'),
    (   'viêm loét giác mạc do nấm sợi',
        'cả hai',
        'cấp',
        'mắt',
        'Ổ loét bờ nham nhở tủa vệ tinh sau chấn thương nông nghiệp cành cây'),
    (   'viêm giác mạc do virus herpes simplex',
        'cả hai',
        'cấp',
        'mắt',
        'Vết loét hình cành cây cành trơ trụi nhuộm fluorescein bắt màu'),
    (   'xước rách giác mạc trợt biểu mô do chấn thương',
        'cả hai',
        'cấp',
        'mắt',
        'Trợt biểu mô giác mạc đau buốt cộm chói chảy nước mắt'),
    (   'đục bao sau sau phẫu thuật Phaco',
        'người lớn',
        'mạn',
        'mắt',
        'Tăng sinh tế bào biểu mô thể thủy tinh sau mổ thay IOL'),
    (   'sụp mi mắc phải một bên do yếu cơ nâng mi',
        'người lớn',
        'mạn',
        'mắt',
        'Bờ mi trên che quá 2mm giác mạc che lấp đồng tử'),
    (   'quặm mi tuổi già gây cọ xát giác mạc',
        'người lớn',
        'mạn',
        'mắt',
        'Bờ mi cuộn vào trong lông mi chọc xước biểu mô giác mạc'),
    ('chắp mắt tái phát nhiều lần mi trên', 'cả hai', 'mạn', 'mắt', 'Nang viêm hạt mạn tính tuyến bã Meibomius mi mắt'),
    ('viêm hốc mắt trước vách', 'cả hai', 'cấp', 'mắt', 'Nhiễm trùng phần mềm mi mắt trước vách ngăn hốc mắt'),
    (   'xuất huyết kết mạc tự phát sau ho rặn',
        'người lớn',
        'cấp',
        'mắt',
        'Vỡ mao mạch kết mạc đỏ tươi góc mắt không đau không giảm thị lực'),
    (   'viêm tai giữa mạn tính có cholesteatoma',
        'cả hai',
        'mạn',
        'tai mũi họng',
        'Khối biểu mô phá hủy ăn mòn xương chũm mủ thối khẳn'),
    (   'điếc đột ngột tiếp nhận thần kinh một bên',
        'người lớn',
        'cấp',
        'tai mũi họng',
        'Mất thính lực thần kinh giác quan xảy ra trong vòng 72 giờ'),
    (   'bệnh Meniere ứ dịch nội bạch huyết',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Tứ chứng Meniere: chóng mặt ù tai nghe kém đầy tức tai'),
    (   'thủng màng nhĩ chấn thương do tát tai',
        'cả hai',
        'cấp',
        'tai mũi họng',
        'Chấn thương áp lực xé rách màng nhĩ chảy máu tai ngoài'),
    (   'dị vật ống tai ngoài do hạt côn trùng',
        'cả hai',
        'cấp',
        'tai mũi họng',
        'Côn trùng sống chui vào tai cào xước màng nhĩ gây đau buốt'),
    (   'viêm sụn vành tai do bấm lỗ xỏ khuyên',
        'cả hai',
        'cấp',
        'tai mũi họng',
        'Nhiễm khuẩn trực khuẩn mủ xanh sưng nóng đỏ biến dạng vành tai'),
    (   'viêm mũi teo trĩ mũi Ozaena',
        'cả hai',
        'mạn',
        'tai mũi họng',
        'Teo niêm mạc cuốn mũi hốc mũi rộng đóng vảy xanh hôi thối'),
    (   'polyp mũi hai bên độ 2 che lấp khe giữa',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Khối u lành tính mọng nước bóng xám nghẹt mũi mất mùi'),
    (   'phì đại cuốn mũi dưới quá phát',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Cuốn mũi dưới thoái hóa xơ phì đại nghẹt thở hai bên'),
    (   'vẹo vách ngăn mũi gây nghẹt mũi một bên',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Gai mào vách ngăn lệch trục chạm cuốn mũi gây nghẹt thở'),
    (   'viêm xoang bướm đơn độc',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Viêm xoang sâu đỉnh đầu nhức sâu sau hốc mắt dễ bỏ sót'),
    (   'viêm xoang hàm do nấm Aspergillus',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Khối bóng nấm dị vật cản quang trong lòng xoang hàm'),
    (   'u nhú đảo ngược hốc mũi',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'U nhú lành tính có xu hướng phá hủy xương và nguy cơ ác tính hóa'),
    (   'nang hố lưỡi thanh thiệt',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Nang ứ đọng nhầy đáy lưỡi gây nuốt vướng khó thở khi nằm'),
    (   'hạt xơ dây thanh do nói nhiều',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Tổn thương đối xứng bờ tự do dây thanh ở giáo viên ca sĩ'),
    (   'polyp dây thanh quản một bên',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Khối mềm có cuống bờ tự do dây thanh gây khàn tiếng'),
    ('nang biểu bì dây thanh', 'người lớn', 'mạn', 'tai mũi họng', 'Nang vùi biểu bì nằm dưới lớp đệm dây thanh'),
    (   'phù Reinke dây thanh ở người hút thuốc',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Khoang Reinke phù nề ứ dịch nhầy tiếng nói trầm khàn đục'),
    (   'liệt dây thanh quản một bên sau phẫu thuật',
        'người lớn',
        'mạn',
        'tai mũi họng',
        'Tổn thương thần kinh thanh quản quặt ngược sau mổ tuyến giáp'),
    (   'viêm tuyến nước bọt mang tai do sỏi ống Wharton',
        'người lớn',
        'cấp',
        'tai mũi họng',
        'Sỏi tắc ống dẫn nước bọt gây sưng đau góc hàm khi ăn nhai'),
    (   'viêm khớp thái dương hàm loạn năng thái dương hàm TMD',
        'người lớn',
        'mạn',
        'răng hàm mặt',
        'Tiếng kêu lục cục khớp hàm đau khi há miệng nhai đồ cứng'),
    (   'trật khớp thái dương hàm hai bên cấp tính',
        'người lớn',
        'cấp',
        'răng hàm mặt',
        'Sai khớp lồi cầu ra trước không khép miệng được chảy dãi'),
    (   'răng khôn hàm dưới mọc lệch biến chứng viêm lợi trùm',
        'người lớn',
        'cấp',
        'răng hàm mặt',
        'Răng số 8 mọc kẹt lợi trùm sưng mủ khít hàm sốt nhẹ'),
    (   'viêm tủy răng cấp tính hồi phục được',
        'cả hai',
        'cấp',
        'răng hàm mặt',
        'Ê buốt răng dữ dội khi gặp kích thích nóng lạnh thoáng qua'),
    (   'viêm tủy răng hoại tử không hồi phục',
        'cả hai',
        'mạn',
        'răng hàm mặt',
        'Cơn đau tủy tự phát dữ dội buốt lên tận óc tăng về đêm'),
    (   'áp xe quanh chóp răng hàm trên',
        'cả hai',
        'cấp',
        'răng hàm mặt',
        'Viêm nhiễm lan tỏa chóp răng tạo bọc mủ sưng phồng ngách lợi'),
    (   'sâu răng ngà sâu buốt răng khi ăn ngọt',
        'cả hai',
        'mạn',
        'răng hàm mặt',
        'Lỗ sâu thủng ngà men răng mắc thức ăn gây ê ẩm'),
    (   'mòn ngót cổ răng ê buốt ngà răng',
        'người lớn',
        'mạn',
        'răng hàm mặt',
        'Tổn thương khuyết hình chêm cổ răng do đánh răng ngang'),
    (   'u nang chân răng nang xương hàm lành tính',
        'cả hai',
        'mạn',
        'răng hàm mặt',
        'Nang biểu mô phồng xương hàm từ răng chết tủy cũ'),
    (   'rách niêm mạc môi lợi do chấn thương ngã',
        'cả hai',
        'cấp',
        'răng hàm mặt',
        'Vết rách phần mềm khoang miệng rớm máu do va đập răng'),
    (   'nứt gãy xương ổ răng đơn thuần',
        'cả hai',
        'cấp',
        'răng hàm mặt',
        'Chấn thương gãy thành xương ổ răng lung lay cụm răng'),
    (   'bạch sản niêm mạc má tiền ung thư',
        'người lớn',
        'mạn',
        'răng hàm mặt',
        'Mảng trắng sừng hóa niêm mạc miệng không cạo bong được'),
    (   'viêm lưỡi bản đồ lành tính',
        'cả hai',
        'mạn',
        'răng hàm mặt',
        'Mảng teo gai lưỡi viền trắng chuyển dịch vị trí hình bản đồ'),
    (   'bệnh da bọng nước tự miễn Pemphigus vulgaris',
        'người lớn',
        'mạn',
        'da liễu',
        'Bọng nước mỏng dễ vỡ dấu hiệu Nikolsky dương tính loét trợt niêm mạc'),
    (   'bệnh bọng nước dạng Pemphigoid ở người già',
        'người lớn',
        'mạn',
        'da liễu',
        'Bọng nước căng dày dưới thượng bì tự miễn ở người trên 65 tuổi'),
    (   'viêm da dạng herpes Duhring-Brocq',
        'người lớn',
        'mạn',
        'da liễu',
        'Mụn nước cụm ngứa dữ dội liên quan không dung nạp gluten'),
    (   'hội chứng Stevens-Johnson do thuốc dị ứng',
        'cả hai',
        'cấp',
        'da liễu',
        'Hoại tử bong trợt da niêm mạc dưới 10% do phản ứng dị ứng thuốc'),
    (   'hoại tử thượng bì nhiễm độc Lyell do thuốc',
        'cả hai',
        'cấp',
        'da liễu',
        'Hội chứng TEN bong trợt thượng bì trên 30% diện tích da'),
    ('vảy phấn đỏ chân tóc', 'người lớn', 'mạn', 'da liễu', 'Dày sừng nang lông mảng đỏ vảy da đảo da lành đặc trưng'),
    ('vảy phấn hồng Gibert', 'cả hai', 'cấp', 'da liễu', 'Tổn thương mảng báo hiệu herald patch ban hình cây thông'),
    (   'lichen phẳng ở da và niêm mạc miệng',
        'người lớn',
        'mạn',
        'da liễu',
        'Sẩn đa giác màu tím ngứa dải sọc Wickham ở niêm mạc'),
    ('lichen xơ teo âm hộ', 'người lớn', 'mạn', 'da liễu', 'Teo mỏng xơ trắng ngứa rát vùng sinh dục ngoài nữ'),
    (   'xơ cứng bì khu trú dạng mảng morphea',
        'cả hai',
        'mạn',
        'da liễu',
        'Mảng da xơ cứng màu trắng ngà viền tím hoa cà'),
    ('ban đỏ đa dạng thể nhẹ', 'cả hai', 'cấp', 'da liễu', 'Tổn thương da hình bia bắn 3 vòng đồng tâm sau herpes'),
    (   'ban đỏ nốt ở cẳng chân hồng ban nút',
        'người lớn',
        'cấp',
        'da liễu',
        'Cục viêm dưới da ấn đau mặt trước cẳng chân hai bên'),
    (   'viêm tuyến mồ hôi mủ hidradenitis suppurativa',
        'người lớn',
        'mạn',
        'da liễu',
        'Nốt mủ áp xe đường rò sẹo xơ vùng nách bẹn tái phát'),
    (   'rụng tóc từng mảng alopecia areata',
        'cả hai',
        'mạn',
        'da liễu',
        'Rụng tóc tự miễn thành từng mảng tròn da đầu nhẵn bóng'),
    (   'rụng tóc nội tiết androgenic nam',
        'người lớn',
        'mạn',
        'da liễu',
        'Hói đầu chữ M do nhạy cảm với hormone dihydrotestosterone'),
    (   'rụng tóc telogen sau sinh đẻ hoặc sốt nặng',
        'người lớn',
        'cấp',
        'da liễu',
        'Rụng tóc lan tỏa phản ứng sau stress biến cố sinh nở'),
    (   'viêm kẽ ngón tay do nấm Candida',
        'người lớn',
        'mạn',
        'da liễu',
        'Trợt đỏ kẽ ngón tay 3-4 ở người làm bếp thường xuyên ướt tay'),
    ('lang ben lan tỏa do Malassezia', 'cả hai', 'mạn', 'da liễu', 'Dát giảm hoặc tăng sắc tố phủ vảy cám mồ hôi chua'),
    (   'mụn cóc phẳng mu bàn tay do HPV',
        'cả hai',
        'mạn',
        'da liễu',
        'Sẩn phẳng màu da hơi gờ nhẹ bề mặt nhẵn bóng do virus'),
    ('u mềm lây Molluscum contagiosum', 'cả hai', 'cấp', 'da liễu', 'Nốt sẩn sáp hình bán cầu có rốn lõm ở trung tâm'),
    (   'dày sừng quang hóa tiền ung thư da',
        'người lớn',
        'mạn',
        'da liễu',
        'Mảng sần sùi đóng vảy thô ráp vùng da tiếp xúc nắng'),
    (   'dày sừng tiết bã tuổi già',
        'người lớn',
        'mạn',
        'da liễu',
        'U da lành tính màu nâu sẫm dán dính bề mặt như gắn sáp'),
    (   'sẹo lồi phì đại sau phẫu thuật chấn thương',
        'cả hai',
        'mạn',
        'da liễu',
        'Mô sẹo tăng sinh vượt ra ngoài ranh giới tổn thương ban đầu'),
    (   'bệnh vảy cá bẩm sinh thể thông thường',
        'cả hai',
        'mạn',
        'da liễu',
        'Da khô ráp tróc vảy đa giác xám như vảy cá hai cẳng chân'),
    (   'viêm quầng Erysipelas cẳng chân do liên cầu',
        'người lớn',
        'cấp',
        'da liễu',
        'Nhiễm trùng nông da gờ cao ranh giới rõ sốt rét run'),
    (   'viêm mô tế bào cẳng chân do tụ cầu',
        'người lớn',
        'cấp',
        'da liễu',
        'Nhiễm trùng sâu lớp hạ bì da sưng nóng đỏ ranh giới mờ'),
    (   'nhọt cụm nhọt độc vùng gáy carbuncle',
        'người lớn',
        'cấp',
        'da liễu',
        'Ổ tụ mủ nhiều ngòi nang lông đau nhức nhối sốt cao'),
    (   'chốc loét Ecthyma chi dưới',
        'cả hai',
        'cấp',
        'da liễu',
        'Loét sâu qua trung bì đóng vảy tiết dày màu xám nâu bẩn'),
    (   'phù mạch dị ứng di truyền phù Quincke',
        'cả hai',
        'cấp',
        'miễn dịch - dị ứng',
        'Phù nề mô mềm đột ngột mi mắt môi hầu họng dọa tắc thở'),
    (   'sốc phản vệ độ 2 do thức ăn hải sản',
        'cả hai',
        'cấp',
        'miễn dịch - dị ứng',
        'Mày đay khó thở tức ngực nôn ói sau ăn tôm cua'),
    (   'dị ứng thuốc kháng sinh nhóm beta-lactam',
        'cả hai',
        'cấp',
        'miễn dịch - dị ứng',
        'Phản ứng ban dát sẩn ngứa toàn thân sau tiêm uống kháng sinh'),
    (   'viêm kết mạc dị ứng mùa phấn hoa',
        'cả hai',
        'cấp',
        'miễn dịch - dị ứng',
        'Mắt ngứa cộm đỏ dử trong theo mùa hoa nở'),
    (   'mày đay mạn tính vô căn tự phát',
        'người lớn',
        'mạn',
        'miễn dịch - dị ứng',
        'Sẩn phù ngứa tái phát hàng ngày kéo dài trên 6 tuần'),
    (   'mày đay do lạnh do áp lực vật lý',
        'cả hai',
        'mạn',
        'miễn dịch - dị ứng',
        'Nổi mề đay khi tiếp xúc nước lạnh gió rét hoặc cọ xát cơ học'),
    (   'viêm da tiếp xúc dị ứng với niken kim loại',
        'cả hai',
        'mạn',
        'da liễu',
        'Ngứa đỏ mụn nước vị trí đeo đồng hồ cúc quần khóa thắt lưng'),
    (   'viêm da tiếp xúc do thực vật kiến ba khoang',
        'cả hai',
        'cấp',
        'da liễu',
        'Tổn thương vệt đỏ bọng nước bọng mủ do độc tố pederin'),
    (   'bệnh huyết thanh sau tiêm kháng huyết thanh',
        'cả hai',
        'cấp',
        'miễn dịch - dị ứng',
        'Phản ứng quá mẫn type 3 sốt đau khớp nổi ban sau 7-14 ngày'),
    (   'viêm mạch máu nhỏ hoại tử do phức hợp miễn dịch',
        'người lớn',
        'mạn',
        'miễn dịch - dị ứng',
        'Tổn thương ban xuất huyết sờ thấy được hoại tử nông'),
    (   'hội chứng kháng phospholipid tự miễn',
        'người lớn',
        'mạn',
        'miễn dịch - dị ứng',
        'Huyết khối tái phát sẩy thai liên tiếp kháng thể aPL dương tính'),
    (   'hội chứng Churg-Strauss u hạt dị ứng viêm mạch',
        'người lớn',
        'mạn',
        'miễn dịch - dị ứng',
        'Viêm mạch hen suyễn tăng bạch cầu ái toan ANCA dương tính'),
    (   'bệnh u hạt Wegener viêm đa mạch GPA',
        'người lớn',
        'mạn',
        'miễn dịch - dị ứng',
        'Viêm mạch hoại tử u hạt đường hô hấp trên và viêm cầu thận'),
    (   'viêm động mạch tế bào khổng lồ thái dương Horton',
        'người lớn',
        'cấp',
        'miễn dịch - dị ứng',
        'Đau đầu thái dương động mạch nổi cứng nguy cơ mù mắt'),
    (   'viêm động mạch Takayasu không có mạch',
        'người lớn',
        'mạn',
        'tim mạch',
        'Viêm xơ hẹp các nhánh lớn của quai động mạch chủ'),
    (   'ngộ độc paracetamol giai đoạn sớm tại nhà',
        'cả hai',
        'cấp',
        'tiêu hoá',
        'Uống quá liều paracetamol buồn nôn đau hạ sườn phải'),
    (   'ngộ độc nấm độc chứa độc tố amanita',
        'cả hai',
        'cấp',
        'tiêu hoá',
        'Đau bụng nôn tiêu chảy dữ dội sau ăn nấm rừng tự hái'),
    (   'ngộ độc rượu cồn công nghiệp methanol nhẹ',
        'người lớn',
        'cấp',
        'mắt',
        'Nhìn mờ thị lực như qua màn sương toan chuyển hóa sau uống rượu giả'),
    (   'ngộ độc khí than CO mạn tính thể nhẹ',
        'cả hai',
        'mạn',
        'thần kinh',
        'Đau đầu chóng mặt buồn nôn do sưởi than tổ ong trong phòng kín'),
    (   'ong đốt nhiều nốt nhiễm độc nọc ong nhẹ',
        'cả hai',
        'cấp',
        'miễn dịch - dị ứng',
        'Vết đốt sưng nề đỏ đau buốt hoại tử trung tâm'),
    (   'rắn lục đuôi đỏ cắn chảy máu tại chỗ',
        'cả hai',
        'cấp',
        'huyết học',
        'Rối loạn đông máu chảy máu không cầm vùng vết cắn rắn lục'),
    (   'ngộ độc hải sản chứa độc tố ciguatera',
        'cả hai',
        'cấp',
        'tiêu hoá',
        'Rối loạn cảm giác đảo ngược nóng lạnh sau ăn cá biển'),
    (   'suy tủy xương dòng hồng cầu đơn thuần',
        'người lớn',
        'mạn',
        'huyết học',
        'Hội chứng Blackfan-Diamond người lớn thiếu máu đơn độc'),
    (   'thiếu máu do suy thận mạn thiếu erythropoietin',
        'người lớn',
        'mạn',
        'huyết học',
        'Thiếu máu đẳng sắc hồng cầu bình thường ở bệnh thận mạn'),
    (   'thiếu máu bất sản tủy aplastic anemia',
        'cả hai',
        'mạn',
        'huyết học',
        'Giảm 3 dòng tế bào máu ngoại vi tủy xương nghèo tế bào'),
    (   'bệnh đa hồng cầu nguyên phát Polycythemia vera',
        'người lớn',
        'mạn',
        'huyết học',
        'Tăng sinh tủy ác tính đột biến JAK2 V617F da đỏ tía ngứa sau tắm'),
    (   'tăng tiểu cầu nguyên phát',
        'người lớn',
        'mạn',
        'huyết học',
        'Số lượng tiểu cầu tăng cao trên 450.000 nguy cơ huyết khối'),
    (   'bệnh máu khó đông Hemophilia A di truyền',
        'cả hai',
        'mạn',
        'huyết học',
        'Thiếu hụt yếu tố VIII đông máu chảy máu khớp cơ tự phát'),
    (   'bệnh von Willebrand thể nhẹ type 1',
        'cả hai',
        'mạn',
        'huyết học',
        'Rối loạn kết dính tiểu cầu chảy máu niêm mạc răng mũi'),
    (   'xuất huyết giảm tiểu cầu huyết khối TTP',
        'người lớn',
        'cấp',
        'huyết học',
        'Thiếu men ADAMTS13 ngũ chứng sốt thiếu máu tan máu tiểu cầu giảm'),
    (   'bệnh bạch cầu lympho mạn tính CLL giai đoạn sớm',
        'người lớn',
        'mạn',
        'huyết học',
        'Tăng sinh dòng lympho B tế bào nhỏ hạch cổ nách không đau'),
    (   'đau tủy xương đa u tủy xương Multiple Myeloma',
        'người lớn',
        'mạn',
        'huyết học',
        'Đau xương tiêu xương protein Bence Jones tăng canxi máu'),
    (   'u lympho Hodgkin hạch cổ nách giai đoạn sớm',
        'cả hai',
        'mạn',
        'huyết học',
        'Hạch to không đau triệu chứng B tế bào Reed-Sternberg'),
    (   'u lympho không Hodgkin thâm nhiễm hạch mạc treo',
        'người lớn',
        'mạn',
        'huyết học',
        'Khối u lympho ác tính đường tiêu hoá sụt cân nhanh'),
    (   'hội chứng tăng bạch cầu ái toan vô căn HES',
        'người lớn',
        'mạn',
        'huyết học',
        'Bạch cầu ái toan trên 1500 tổn thương tim phổi thần kinh'),
    (   'huyết khối tĩnh mạch chi trên do đặt buồng tiêm',
        'người lớn',
        'cấp',
        'tim mạch',
        'Sưng nề tím tái tay phải sau đặt catheter buồng truyền hóa chất'),
    (   'viêm nội tâm mạc nhiễm khuẩn bán cấp Osler',
        'người lớn',
        'bán cấp',
        'tim mạch',
        'Sùi van tim vi khuẩn sốt kéo dài nốt Osler xuất huyết võng mạc Roth'),
    (   'bệnh cơ tim phì đại không tắc nghẽn',
        'người lớn',
        'mạn',
        'tim mạch',
        'Dày đồng tâm vách liên thất di truyền gen sarcomere'),
    ('bệnh cơ tim giãn vô căn', 'người lớn', 'mạn', 'tim mạch', 'Giãn buồng thất giảm phân suất tống máu EF dưới 40%'),
    (   'hội chứng Brugada typ 1 nguy cơ đột tử',
        'người lớn',
        'mạn',
        'tim mạch',
        'Đoạn ST chênh vòm ở V1-V2 nguy cơ rung thất ban đêm'),
    (   'hội chứng QT dài bẩm sinh',
        'cả hai',
        'mạn',
        'tim mạch',
        'Khoảng QTc kéo dài trên điện tim nguy cơ xoắn đỉnh ngất'),
    (   'block nhĩ thất độ 2 Mobitz 2',
        'người lớn',
        'mạn',
        'tim mạch',
        'Sóng P không dẫn ngắt quãng phức bộ QRS nguy cơ block hoàn toàn'),
    (   'block nhánh trái hoàn toàn mới xuất hiện',
        'người lớn',
        'mạn',
        'tim mạch',
        'QRS giãn rộng dạng chữ M ở V5-V6 dấu hiệu suy tim xơ vữa'),
    (   'hội chứng suy nút xoang nhịp chậm xoang',
        'người lớn',
        'mạn',
        'tim mạch',
        'Nhịp tim chậm dưới 50 l/p kèm khoảng ngừng xoang ngất thiu'),
    (   'hẹp van động mạch chủ thoái hóa vôi hóa tuổi già',
        'người lớn',
        'mạn',
        'tim mạch',
        'Tiếng thổi tâm thu tống máu khoang liên sườn 2 phải lan cổ'),
    (   'hở van động mạch chủ mạn tính',
        'người lớn',
        'mạn',
        'tim mạch',
        'Tiếng thổi tâm trương êm dịu bờ trái xương ức mạch nảy mạnh chìm sâu'),
    (   'sa van hai lá biến chứng hở van nhẹ',
        'người lớn',
        'mạn',
        'tim mạch',
        'Tiếng click giữa tâm thu kèm thổi muộn ở mỏm tim'),
    (   'tăng áp lực động mạch phổi tiên phát vô căn',
        'người lớn',
        'mạn',
        'tim mạch',
        'Áp lực động mạch phổi tâm thu trên 35 mmHg khó thở gắng sức'),
    (   'viêm tắc tĩnh mạch nông chi dưới do tiêm truyền',
        'người lớn',
        'cấp',
        'tim mạch',
        'Dải xơ cứng đỏ đau dọc tĩnh mạch hiển nông cẳng chân'),
    (   'phình động mạch chủ bụng dưới thận kích thước nhỏ',
        'người lớn',
        'mạn',
        'tim mạch',
        'Đường kính động mạch chủ bụng 3.5cm đập theo nhịp tim'),
    (   'xơ cứng động mạch Monckeberg',
        'người lớn',
        'mạn',
        'tim mạch',
        'Vôi hóa lớp áo giữa thành động mạch không gây hẹp lòng mạch'),
    (   'rối loạn stress sau sang chấn PTSD',
        'người lớn',
        'mạn',
        'tâm thần',
        'Hồi tưởng ác mộng lo âu hoảng loạn sau biến cố kinh hoàng'),
    (   'rối loạn ám ảnh sợ khoảng trống Agoraphobia',
        'người lớn',
        'mạn',
        'tâm thần',
        'Sợ hãi né tránh nơi công cộng không có lối thoát an toàn'),
    (   'rối loạn ám ảnh sợ xã hội Social Phobia',
        'người lớn',
        'mạn',
        'tâm thần',
        'Sợ bị người khác đánh giá chú ý khi phát biểu giao tiếp'),
    (   'rối loạn dạng cơ thể Somatization disorder',
        'người lớn',
        'mạn',
        'tâm thần',
        'Đau đớn đa cơ quan kéo dài không tìm thấy tổn thương thực thể'),
    (   'rối loạn nghi bệnh Hypochondriasis sợ mắc bệnh hiểm nghèo',
        'người lớn',
        'mạn',
        'tâm thần',
        'Nỗi sợ thường trực bị ung thư hoặc bệnh nan y dù khám bình thường'),
    (   'rối loạn cảm xúc lưỡng cực giai đoạn hưng cảm nhẹ',
        'người lớn',
        'mạn',
        'tâm thần',
        'Khí sắc phấn chấn nói nhiều tăng hoạt động giảm nhu cầu ngủ'),
    (   'tâm thần phân liệt thể paranoid giai đoạn ổn định',
        'người lớn',
        'mạn',
        'tâm thần',
        'Hoang tưởng bị hại ảo thanh bình phẩm đã kiểm soát thuốc'),
    (   'rối loạn ăn uống chán ăn tâm thần Anorexia nervosa',
        'cả hai',
        'mạn',
        'tâm thần',
        'Nỗi sợ tăng cân ám ảnh nhịn ăn cực đoan thể trạng suy kiệt'),
    (   'rối loạn TIC vận động và âm thanh mạn tính',
        'nhi',
        'mạn',
        'tâm thần',
        'Nháy mắt giật cơ phát âm tiếng hắng giọng không tự chủ'),
    (   'rối loạn ác mộng kinh hoàng khi ngủ ban đêm',
        'nhi',
        'mạn',
        'tâm thần',
        'Tỉnh giấc hoảng loạn la hét ban đêm không nhớ nội dung giấc mơ'),
    (   'nghiện rượu mạn tính hội chứng cai rượu nhẹ',
        'người lớn',
        'mạn',
        'tâm thần',
        'Run tay vã mồ hôi lo âu khi ngừng uống rượu buổi sáng'),
    (   'xơ cứng bì phổi tổn thương phổi kẽ',
        'người lớn',
        'mạn',
        'hô hấp',
        'Xơ hóa mô kẽ phổi tiến triển ở bệnh nhân xơ cứng bì'),
    (   'bệnh u hạt Sarcoidosis phổi hạch rốn phổi',
        'người lớn',
        'mạn',
        'hô hấp',
        'U hạt không bã đậu hạch rốn phổi hai bên đối xứng'),
    (   'viêm phổi tăng bạch cầu ái toan mạn tính',
        'người lớn',
        'mạn',
        'hô hấp',
        'Thâm nhiễm phổi ngoại vi âm bản phù phổi giàu bạch cầu ái toan'),
    (   'bệnh phổi kẽ liên quan hút thuốc lá',
        'người lớn',
        'mạn',
        'hô hấp',
        'Viêm tiểu phế quản hô hấp bệnh phổi mô kẽ RB-ILD'),
    (   'viêm tiểu phế quản tắc nghẽn sau nhiễm virus',
        'cả hai',
        'mạn',
        'hô hấp',
        'Tắc nghẽn đường thở nhỏ cố định sau viêm tiểu phế quản nặng'),
    (   'bui phổi amiăng Asbestosis',
        'người lớn',
        'mạn',
        'hô hấp',
        'Xơ hóa màng phổi mảng màng phổi do hít bụi sợi amiăng'),
    (   'bụi phổi than thợ mỏ anthracosis',
        'người lớn',
        'mạn',
        'hô hấp',
        'Nốt xơ hóa phổi nhiễm hắc tố than ở công nhân mỏ'),
    (   'bệnh phổi nông dân do nấm mốc dị ứng',
        'người lớn',
        'cấp',
        'hô hấp',
        'Viêm phế nang dị ứng ngoại lai do hít bào tử nấm rơm cỏ khô'),
    (   'viêm màng phổi dày dính màng phổi sau tràn dịch',
        'người lớn',
        'mạn',
        'hô hấp',
        'Dày dính vôi hóa lá thành và lá tạng màng phổi hạn chế hô hấp'),
    (   'rò dưỡng chấp màng phổi vô căn',
        'người lớn',
        'mạn',
        'hô hấp',
        'Tràn dịch màng phổi dưỡng chấp màu trắng sữa giàu triglycerid')]

# 300 ung vien con lai chua hien thuc hoa cho cac Lo 3-8 (Khuon 301-600):
DANH_SACH_UNG_VIEN_CON_LAI = DANH_SACH_UNG_VIEN_350[50:]
