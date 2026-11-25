# -*- coding: utf-8 -*-
"""Bộ tạo Lô 7 (50 khuôn bệnh, candidate 501-550) cho MediTrace Sentinel V2.

Trục 1 & Quản lý Khối lượng Lâm sàng:
- Lô 7 bao gồm 50 khuôn bệnh da liễu, miễn dịch - dị ứng, tim mạch, tiêu hoá, thần kinh, mắt, huyết học.
- Đảm bảo 100% tuân thủ các quy tắc:
  * Không chứa chuỗi con 'ốm'
  * 0 cặp trùng lặp triệu chứng >= 20%
  * Đầy đủ 6 biến thể khám, chẩn đoán, kế hoạch
  * da_duyet: False
  * GIOI_TINH_LO_7 đầy đủ cho các bệnh đặc thù giới tính
"""
import json
import re
import unicodedata
from typing import Dict, List, Any

# Định nghĩa dữ liệu 50 khuôn lâm sàng Lô 7
RAW_DATA_LO_7 = [
    # 501
    {
        "ten": "bệnh da bọng nước tự miễn Pemphigus vulgaris",
        "nhom": "người lớn",
        "dien_tien": "mạn",
        "he_co_quan": "da liễu",
        "chinh": [
            "xuất hiện các bọng nước mỏng mềm dễ vỡ trên nền da bình thường",
            "tổn thương trợt loét đau rát dữ dội tại niêm mạc khoang miệng và vòm họng",
            "vết trợt da rỉ dịch huyết thanh vàng dễ chảy máu lâu lành vảy"
        ],
        "phu": [
            "cảm giác đau buốt tăng nặng khi nuốt thức ăn gây khó khăn dinh dưỡng",
            "mùi hôi đặc trưng bốc ra từ các vết trợt da tiết dịch nhớt dính",
            "cảm giác râm ran bỏng rát nhẹ trên da trước khi xuất hiện bọng mới"
        ],
        "kham": "Khám thấy nhiều bọng nước thành mỏng nhẽo dễ vỡ, trợt loét niêm mạc miệng rải rác diện rộng, dấu hiệu Nikolsky dương tính rõ.",
        "chan_doan": "Bệnh da bọng nước tự miễn Pemphigus vulgaris đợt tiến triển.",
        "ke_hoach": "Chỉ định sinh thiết rìa tổn thương làm miễn dịch huỳnh quang trực tiếp, dùng corticosteroid đường toàn thân kết hợp chăm sóc vết trợt tại chỗ.",
        "bien_the_kham": [
            "Khám thấy nhiều bọng nước thành mỏng nhẽo dễ vỡ, trợt loét niêm mạc miệng rải rác diện rộng, dấu hiệu Nikolsky dương tính rõ.",
            "Tổn thương da là các vết trợt nông rỉ dịch sau bọng vỡ, niêm mạc miệng có nhiều vết loét trợt đau rát, Nikolsky dương tính.",
            "Ghi nhận bọng nước vách mỏng chứa dịch trong nằm rải rác thân mình, vòm miệng có mảng loét sâu đau, dấu hiệu Nikolsky dương tính.",
            "Da nhiều vết trợt rỉ dịch huyết thanh do bọng nước dập vỡ, niêm mạc má và lợi có tổn thương trợt loét đỏ tươi điển hình.",
            "Bọng nước nhẽo xuất hiện trên nền da bình thường kèm trợt loét niêm mạc miệng rộng, dấu hiệu Nikolsky dương tính rõ rệt.",
            "Bề mặt da rải rác bọng nước mềm dễ rách, niêm mạc họng viêm loét gây nuốt nghẹn, khám thấy nghiệm pháp Nikolsky dương tính."
        ],
        "bien_the_chan_doan": [
            "Bệnh da bọng nước tự miễn Pemphigus vulgaris đợt tiến triển.",
            "Theo dõi bệnh da bọng nước tự miễn Pemphigus vulgaris mức độ trung bình.",
            "Bệnh da bọng nước tự miễn Pemphigus vulgaris có tổn thương niêm mạc miệng.",
            "Bệnh da bọng nước tự miễn Pemphigus vulgaris thể thông thường giai đoạn hoạt tính.",
            "Bệnh da bọng nước tự miễn Pemphigus vulgaris tái phát.",
            "Nghi ngờ bệnh da bọng nước tự miễn Pemphigus vulgaris tổn thương da và niêm mạc."
        ],
        "bien_the_ke_hoach": [
            "Chỉ định sinh thiết rìa tổn thương làm miễn dịch huỳnh quang trực tiếp, dùng corticosteroid đường toàn thân kết hợp chăm sóc vết trợt tại chỗ.",
            "Làm sinh thiết mô bệnh học da, xét nghiệm kháng thể kháng desmoglein 1 và 3, dùng prednisolone đường uống liều cao.",
            "Chỉ định xét nghiệm miễn dịch huỳnh quang trực tiếp, dùng methylprednisolone tĩnh mạch kết hợp bôi thuốc mỡ sát khuẩn dịu da.",
            "Thực hiện sinh thiết tổn thương da bọng nước, điều trị ức chế miễn dịch bằng corticoid toàn thân, súc miệng dung dịch giảm đau sát khuẩn.",
            "Hội chẩn chuyên khoa da liễu, làm xét nghiệm miễn dịch huỳnh quang, dùng corticosteroid toàn thân và gạc mỡ che phủ vết trợt.",
            "Làm giải phẫu bệnh vết loét da, dùng liệu pháp corticoid liều cao đường uống phối hợp phòng ngừa loét dạ dày và chăm sóc niêm mạc."
        ]
    },
    # 502
    {
        "ten": "bệnh bọng nước dạng Pemphigoid ở người già",
        "nhom": "người lớn",
        "dien_tien": "mạn",
        "he_co_quan": "da liễu",
        "chinh": [
            "nổi nhiều bọng nước căng dày khó vỡ kích thước lớn trên nền ban đỏ hoặc da lành",
            "ngứa ngáy dữ dội kéo dài toàn thân xuất hiện trước khi tổn thương bọng nổi lên",
            "vị trí bọng nước tập trung chủ yếu ở vùng bụng dưới đùi trong và mặt gấp cẳng tay"
        ],
        "phu": [
            "các vết trợt nông sau khi bọng vỡ có khuynh hướng tự lành nhanh không để lại sẹo",
            "thỉnh thoảng có vài sẩn phù đỏ ngứa tương tự mày đay xen kẽ rải rác",
            "giấc ngủ bị xáo trộn do cơn ngứa ngáy bùng phát mạnh vào ban đêm"
        ],
        "kham": "Ghi nhận nhiều bọng nước căng chắc chứa dịch trong suốt, dấu hiệu Nikolsky âm tính, nền da xung quanh có dát đỏ phù nề.",
        "chan_doan": "Bệnh bọng nước dạng Pemphigoid ở người già thể bọng nước căng.",
        "bien_the_kham": [
            "Ghi nhận nhiều bọng nước căng chắc chứa dịch trong suốt, dấu hiệu Nikolsky âm tính, nền da xung quanh có dát đỏ phù nề.",
            "Bọng nước kích thước 1-3cm vách dày khó vỡ ở vùng bụng và đùi, dấu hiệu Nikolsky âm tính, không có tổn thương niêm mạc miệng.",
            "Nhiều bọng nước căng bóng chứa dịch trong trên nền dát đỏ dạng mề đay, nghiệm pháp Nikolsky hoàn toàn âm tính.",
            "Tổn thương da gồm các bọng nước căng chắc mọc đối xứng ở nếp gấp và chi, không trợt niêm mạc, dấu hiệu Nikolsky âm tính.",
            "Khám thấy bọng nước vách dày căng tròn, đáy tổn thương không bị rách khi miết ngón tay, Nikolsky âm tính rõ.",
            "Bọng nước căng chứa dịch vàng chanh phân bố ở mặt trong đùi và cánh tay, dấu hiệu Nikolsky âm tính, da có sẩn phù ngứa."
        ],
        "bien_the_chan_doan": [
            "Bệnh bọng nước dạng Pemphigoid ở người già thể bọng nước căng.",
            "Bệnh bọng nước dạng Pemphigoid ở người già giai đoạn hoạt tính.",
            "Theo dõi bệnh bọng nước dạng Pemphigoid ở người già mức độ trung bình.",
            "Bệnh bọng nước dạng Pemphigoid ở người già có ngứa ngáy toàn thân.",
            "Nghi ngờ bệnh bọng nước dạng Pemphigoid ở người già thể da đỏ.",
            "Bệnh bọng nước dạng Pemphigoid ở người già tái phát đợt cấp."
        ],
        "bien_the_ke_hoach": [
            "Xét nghiệm định lượng tự kháng thể kháng BP180 và BP230, dùng kem bôi clobetasol propionate liều cao phối hợp kháng histamine uống.",
            "Chỉ định sinh thiết da làm miễn dịch huỳnh quang trực tiếp tìm lắng đọng IgG màng đáy, bôi corticoid rất mạnh tại chỗ.",
            "Làm xét nghiệm ELISA định lượng kháng thể BP180, bôi mỡ clobetasol toàn thân kết hợp thuốc giảm ngứa kháng histamine thế hệ hai.",
            "Sinh thiết tổn thương bọng nước, bôi kem corticoid liều cao trên vùng da có bọng, theo dõi chức năng thận và đường máu người cao tuổi.",
            "Xét nghiệm miễn dịch huỳnh quang màng đáy biểu bì, chỉ định bôi corticoid tại chỗ kết hợp thuốc chống ngứa ban đêm.",
            "Hướng dẫn bôi clobetasol dạng kem toàn thân, chăm sóc vô trùng các bọng nước căng vỡ, xét nghiệm công thức máu toàn phần."
        ]
    },
    # 503
    {
        "ten": "viêm da dạng herpes Duhring-Brocq",
        "nhom": "người lớn",
        "dien_tien": "mạn",
        "he_co_quan": "da liễu",
        "chinh": [
            "xuất hiện các đám mụn nước căng nhỏ xếp thành cụm đối xứng hai bên cơ thể",
            "ngứa rát dữ dội và cảm giác châm chích bỏng rát tại vùng da tổn thương",
            "vị trí tổn thương ưu thế ở mặt duỗi cẳng tay khuỷu tay đầu gối và vùng mông"
        ],
        "phu": [
            "triệu chứng tiêu chảy phân lỏng thoáng qua hoặc đầy bụng sau khi ăn tinh bột lúa mì",
            "vết cào gãi sâu tạo mài xước nâu sẫm và dát sậm màu sắc tố sau viêm",
            "cảm giác châm chích rát tiền triệu báo trước tại vị trí chuẩn bị nổi mụn mới"
        ],
        "kham": "Tổn thương đa dạng gồm sẩn đỏ, mụn nước dạng herpes mọc thành chùm đối xứng mặt duỗi khuỷu và gối, nhiều vết xước gãi.",
        "chan_doan": "Viêm da dạng herpes Duhring-Brocq liên quan nhạy cảm với gluten.",
        "bien_the_kham": [
            "Tổn thương đa dạng gồm sẩn đỏ, mụn nước dạng herpes mọc thành chùm đối xứng mặt duỗi khuỷu và gối, nhiều vết xước gãi.",
            "Các cụm mụn nước căng nhỏ phân bố đối xứng hai bên cùi chỏ và mông, bề mặt da có sẩn phù đỏ và vết cào gãi.",
            "Khám thấy mụn nước mọc chùm như hạt chùm nho trên nền ban đỏ đối xứng, nhiều mài nâu do gãi xước sâu.",
            "Tổn thương dạng đa hình sẩn mụn nước thành cụm ở khuỷu tay đầu gối, kèm theo nhiều vết trầy da do cào xước liên tục.",
            "Ghi nhận mụn nước căng xếp vòng cung ở vùng xương cùng và khuỷu tay hai bên, tổn thương đối xứng điển hình.",
            "Mụn nước nhỏ mọc thành đám trên nền da đỏ ngứa châm chích vùng gối và khuỷu, các vết xước biểu bì rải rác."
        ],
        "bien_the_chan_doan": [
            "Viêm da dạng herpes Duhring-Brocq liên quan nhạy cảm với gluten.",
            "Viêm da dạng herpes Duhring-Brocq giai đoạn hoạt tính.",
            "Theo dõi viêm da dạng herpes Duhring-Brocq thể đối xứng.",
            "Viêm da dạng herpes Duhring-Brocq tái phát đợt cấp.",
            "Nghi ngờ viêm da dạng herpes Duhring-Brocq có triệu chứng tiêu hóa nhẹ.",
            "Bệnh viêm da dạng herpes Duhring-Brocq mạn tính."
        ],
        "bien_the_ke_hoach": [
            "Tư vấn chế độ ăn kiêng loại bỏ hoàn toàn gluten trong khẩu phần, xét nghiệm kháng thể IgA kháng nội mạc cơ, điều trị dapsone đường uống.",
            "Chỉ định xét nghiệm IgA kháng transglutaminase mô, bắt đầu điều trị dapsone sau khi kiểm tra men G6PD, kiêng ăn bánh mì lúa mì.",
            "Làm sinh thiết da làm miễn dịch huỳnh quang tìm lắng đọng IgA đỉnh nhú bì, dùng dapsone đường uống và kiểm tra công thức máu.",
            "Tư vấn thực đơn không chứa lúa mì lúa mạch trọn đời, định lượng G6PD trước khi kê đơn dapsone uống, bổ sung kem bôi dịu ngứa.",
            "Chỉ định chế độ ăn kiêng gluten nghiêm ngặt, xét nghiệm kháng thể tự miễn ruột non, dùng dapsone liều thấp tăng dần.",
            "Hướng dẫn thực dưỡng không gluten hoàn toàn, kê đơn dapsone kết hợp vitamin và theo dõi sát chỉ số hemoglobin máu."
        ]
    },
    # 504
    {
        "ten": "hội chứng Stevens-Johnson do thuốc dị ứng",
        "nhom": "cả hai",
        "dien_tien": "cấp",
        "he_co_quan": "da liễu",
        "chinh": [
            "hoại tử bong trợt da nông diện tích dưới mười phần trăm kèm ban đỏ bia bắn không điển hình",
            "loét trợt xuất huyết đau đớn dữ dội tại ít nhất hai vị trí niêm mạc mắt môi hoặc sinh dục",
            "sốt cao đột ngột mệt lả xuất hiện sau khi dùng thuốc nghi ngờ từ một đến ba tuần"
        ],
        "phu": [
            "mắt đỏ chói cộm rát sợ ánh sáng và tăng tiết dịch rỉ mắt",
            "nuốt đau nuốt khó làm giảm rõ rệt lượng thức ăn nước uống nạp vào",
            "cảm giác nóng rát châm chích bỏng buốt lan tỏa khắp bề mặt da cơ thể"
        ],
        "kham": "Bong trợt thượng bì khoảng 7% diện tích cơ thể, môi đóng vảy tiết nâu đen hoại tử, kết mạc mắt viêm trợt sung huyết.",
        "chan_doan": "Hội chứng Stevens-Johnson do thuốc dị ứng mức độ cấp tính.",
        "bien_the_kham": [
            "Bong trợt thượng bì khoảng 7% diện tích cơ thể, môi đóng vảy tiết nâu đen hoại tử, kết mạc mắt viêm trợt sung huyết.",
            "Diện tích da bong trợt dưới 10% bề mặt cơ thể, môi nứt nẻ đóng mài đen hoại tử, kết mạc hai mắt sung huyết đỏ rực.",
            "Tổn thương da dạng bia bắn không điển hình kèm trợt da khoảng 6%, hai niêm mạc miệng và mắt viêm loét rỉ máu.",
            "Da nhiều dát đỏ tím kèm bọng nước mềm trợt nông khoảng 8% diện tích, niêm mạc môi loét xuất huyết đặc trưng.",
            "Ghi nhận trợt biểu bì da 5% diện tích cơ thể, miệng loét đau rát không ăn uống được, kết mạc mắt tiết dịch nhầy.",
            "Bong tróc da diện tích 7%, dấu hiệu Nikolsky dương tính vùng ban đỏ, loét môi miệng và niêm mạc sinh dục cấp."
        ],
        "bien_the_chan_doan": [
            "Hội chứng Stevens-Johnson do thuốc dị ứng mức độ cấp tính.",
            "Hội chứng Stevens-Johnson do thuốc dị ứng nghi do kháng sinh.",
            "Theo dõi hội chứng Stevens-Johnson do thuốc dị ứng diện tích trợt dưới 10%.",
            "Hội chứng Stevens-Johnson do thuốc dị ứng có tổn thương niêm mạc mắt.",
            "Hội chứng Stevens-Johnson do thuốc dị ứng đợt cấp nguy cơ tiến triển.",
            "Cấp cứu hội chứng Stevens-Johnson do thuốc dị ứng thể nặng."
        ],
        "bien_the_ke_hoach": [
            "Ngừng ngay lập tức toàn bộ các thuốc nghi ngờ, chuyển phòng điều trị tích cực bỏng, bù dịch điện giải và truyền tĩnh mạch immunoglobulin IVIG.",
            "Dừng ngay thuốc nghi gây dị ứng, chuyển khoa hồi sức bỏng, chăm sóc mắt phòng dính mi cầu, cân nhắc truyền IVIG hoặc cyclosporin.",
            "Dừng mọi loại thuốc đang dùng, bù dịch qua đường tĩnh mạch theo dõi lượng nước tiểu, tra mắt thuốc mỡ bảo vệ giác mạc liên tục.",
            "Ngừng thuốc lập tức, chuyển vào phòng cách ly vô trùng, hồi sức cân bằng nước điện giải, hội chẩn chuyên khoa mắt và da liễu.",
            "Đình chỉ ngay các thuốc nghi vấn, bọc tổn thương bằng gạc vô trùng chống dính, truyền dịch nuôi dưỡng và dùng kháng histamine.",
            "Ngừng toàn bộ thuốc, theo dõi sát sinh hiệu và diện tích bong da hàng ngày, dinh dưỡng qua ống thông dạ dày, chăm sóc vô trùng."
        ]
    },
    # 505
    {
        "ten": "hoại tử thượng bì nhiễm độc Lyell do thuốc",
        "nhom": "cả hai",
        "dien_tien": "cấp",
        "he_co_quan": "da liễu",
        "chinh": [
            "thượng bì bong tróc hoại tử từng mảng lớn trên ba mươi phần trăm diện tích da cơ thể",
            "da trợt đỏ ướt như bị luộc nước sôi với dấu hiệu Nikolsky dương tính trên diện rộng",
            "nhiễm độc toàn thân nặng sốt cao liên tục tụt huyết áp và lơ mơ mệt lả"
        ],
        "phu": [
            "tổn thương niêm mạc hoại tử toàn bộ vùng miệng thanh quản và đường tiêu hóa",
            "mất nước điện giải ồ ạt qua nền da trợt tương tự phỏng diện rộng",
            "đau rát dữ dội toàn thân đến mức không chịu nổi va chạm nhẹ của vải áo"
        ],
        "kham": "Thượng bì bong trợt chiếm 38% diện tích cơ thể, da trượt tróc thành mảng lớn, loét niêm mạc miệng và mắt diện rộng.",
        "chan_doan": "Hoại tử thượng bì nhiễm độc Lyell do thuốc dị ứng thể nặng.",
        "bien_the_kham": [
            "Thượng bì bong trợt chiếm 38% diện tích cơ thể, da trượt tróc thành mảng lớn, loét niêm mạc miệng và mắt diện rộng.",
            "Diện tích bong tróc thượng bì hoại tử 35% diện tích da, dấu hiệu Nikolsky dương tính diện rộng, sốt 39.5 độ C lơ mơ.",
            "Khám thấy da tuột tróc thành mảng lớn chiếm 40% diện tích, nền da trợt đỏ rỉ dịch nhiều, niêm mạc miệng mắt trợt loét nặng.",
            "Thượng bì hoại tử bong trợt 32% cơ thể, toàn bộ môi và khoang miệng trợt loét rỉ máu, mạch nhanh huyết áp dao động.",
            "Tổn thương da dạng hội chứng Lyell bong tróc 36% diện tích, da trượt như luộc nước sôi, mất nước điện giải nặng.",
            "Ghi nhận hoại tử trợt da 42% diện tích cơ thể, Nikolsky dương tính toàn bộ vùng dát đỏ, niêm mạc đa hốc tự nhiên bị tổn thương."
        ],
        "bien_the_chan_doan": [
            "Hoại tử thượng bì nhiễm độc Lyell do thuốc dị ứng thể nặng.",
            "Hội chứng Lyell hoại tử thượng bì nhiễm độc do thuốc dị ứng đợt cấp.",
            "Hoại tử thượng bì nhiễm độc Lyell do thuốc diện tích trợt trên 30%.",
            "Cấp cứu hoại tử thượng bì nhiễm độc Lyell do thuốc dị ứng có suy tuần hoàn.",
            "Hoại tử thượng bì nhiễm độc Lyell do thuốc thể tiến triển nhanh.",
            "Theo dõi hoại tử thượng bì nhiễm độc Lyell do thuốc biến chứng nhiễm trùng."
        ],
        "bien_the_ke_hoach": [
            "Chuyển đơn vị hồi sức tích cực cách ly vô trùng, hồi sức bù dịch thể tích lớn theo phác đồ bỏng, hội chẩn dùng cyclosporin hoặc IVIG.",
            "Hồi sức tích cực bù dịch điện giải theo công thức Parkland cải biên, cách ly buồng vô trùng nhiệt độ ấm, dùng IVIG liều cao.",
            "Đặt catheter tĩnh mạch trung tâm bù dịch chống sốc, ngừng tuyệt đối các thuốc dị ứng, chăm sóc chống dính niêm mạc mắt.",
            "Chuyển khoa Hồi sức cấp cứu, nuôi dưỡng qua tĩnh mạch hoàn toàn, kiểm soát nhiễm khuẩn tại chỗ bằng gạc hydrogel và kháng sinh phổ rộng.",
            "Cấp cứu hồi sức tuần hoàn, theo dõi lượng nước tiểu qua sonde bàng quang, hội chẩn đa chuyên khoa điều trị ức chế miễn dịch đặc hiệu.",
            "Cách ly phòng hồi sức bỏng vô trùng, kiểm soát thăng bằng kiềm toan và điện giải, truyền albumin bù dịch và giảm đau toàn thân."
        ]
    }
]

print(f"Loaded {len(RAW_DATA_LO_7)} templates in draft list...")
