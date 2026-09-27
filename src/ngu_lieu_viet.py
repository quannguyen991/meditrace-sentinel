# -*- coding: utf-8 -*-
"""Kho ngu lieu cho bo sinh hoi thoai kham benh Viet Nam.

Tach khoi `sinh_hoi_thoai_viet.py` co chu dinh: tep nay la DU LIEU, tep kia la
LUAT. Doc rieng de hon, va khi can them benh hay them cach noi thi chi sua o
day, khong dung toi phan sinh.

VI SAO PHAI TU DUNG KHO NAY.

Bo du lieu cua cuoc thi co dau vet ro la ban dich tu mot bo hoi thoai y khoa
tieng Anh (My): pound/ounce nhieu hon kg, Tylenol/Advil, "benh vien UIHC",
"phong kham Sample" — xem `docs/ket-qua/dau-vet-nguon.md`. Ngon ngu la tieng
Viet nhung boi canh lam sang va loi noi thi khong phai.

Hau qua nam dung cho du an quan tam: hai thu lam viec QUY GAN kho nhat trong
tieng Viet deu bi duoi dai dien trong mot ban dich tu tieng Anh —

  1. LUOC CHU NGU. Tieng Anh gan nhu luon co chu ngu; tieng Viet bo thoai mai:
     "Sot hai hom roi", "Non tu toi qua". Nguoi doc suy ra chu the tu ngu canh.
  2. TU CHI QUAN HE HO HANG LAM DAI TU. "chau", "em", "con" vua la cach nguoi
     noi tu xung, vua la cach goi nguoi thu ba. Cau "chau no sot" va "chau
     thay met" co cung chu "chau" nhung khac chu the hoan toan.

Kho nay dung de sinh ra dung hai hien tuong do, o mat do that.

NGUYEN TAC CHON NOI DUNG: benh, thuoc, don vi do va cach xung ho deu lay theo
thuc te Viet Nam. Can nang kg, nhiet do do C, thuoc la paracetamol/efferalgan/
hapacol chu khong phai Tylenol.
"""

# ---------------------------------------------------------------- xung ho

# Bac si goi benh nhan theo tuoi va gioi. Moi muc: (tu goi, tu benh nhan tu xung)
XUNG_HO_NGUOI_LON = [
    ("anh", "tôi"), ("anh", "em"), ("chị", "tôi"), ("chị", "em"),
    ("cô", "tôi"), ("chú", "tôi"), ("bác", "tôi"), ("ông", "tôi"),
    ("bà", "tôi"), ("em", "em"),
]
XUNG_HO_TRE_EM = [("bé", "con"), ("cháu", "cháu"), ("con", "con")]

# Nguoi nha ke ho: (vai, tu bac si goi ho, tu ho tu xung, quan he voi benh nhan)
NGUOI_NHA = [
    ("mẹ", "chị", "em", "mẹ"),
    ("mẹ", "chị", "tôi", "mẹ"),
    ("bố", "anh", "tôi", "bố"),
    ("bà ngoại", "bà", "tôi", "bà ngoại"),
    ("bà nội", "bà", "tôi", "bà nội"),
    ("vợ", "chị", "em", "vợ"),
    ("chồng", "anh", "tôi", "chồng"),
    ("con gái", "chị", "cháu", "con gái"),
    ("con trai", "anh", "cháu", "con trai"),
]
# Chi dung cho BENH NHI: bo, me, ong ba.
NGUOI_NHA_TRE_EM = NGUOI_NHA[:5]

# NGUOI LON: nguoi nha chon THEO lua tuoi va gioi cua benh nhan (tu bac si goi
# benh nhan) — xem `sinh_hoi_thoai_viet._chon_nguoi_nha_nguoi_lon`. Them
# 11/09/2026, sau khi nguoi dung doc mot ca minh hoa: "sao lai nha em cai gi day,
# khong ai noi nhu nay ca". Bang cu rut chung `NGUOI_NHA[3:]` cho moi nguoi lon:
#   - ba noi, ba ngoai ke ho benh nhan nguoi lon, ke ca nguoi bac si goi "ong"
#     (184 ca train)
#   - con gai tu xung "chau" trong khi bac si goi co la "chi"
#   - "vo" cua mot benh nhan bac si goi la "chi"
# `NGUOI_NHA` giu nguyen (bo thach thuc cu va test doc no), nhung khong con dung
# cho benh nhan nguoi lon.
LUA_TUOI_THEO_GOI = {"anh": "trẻ", "chị": "trẻ", "em": "trẻ",
                     "cô": "trung niên", "chú": "trung niên",
                     "bác": "cao tuổi", "ông": "cao tuổi", "bà": "cao tuổi"}
GIOI_THEO_GOI = {"anh": "nam", "chú": "nam", "ông": "nam",
                 "chị": "nữ", "cô": "nữ", "bà": "nữ"}      # "em", "bác": khong noi gioi
# Bac si goi vo/chong cua benh nhan CUNG vai ve voi benh nhan.
VO_CHONG_GOI = {"anh": "chị", "chị": "anh", "em": "em", "chú": "cô", "cô": "chú",
                "bác": "bác", "ông": "bà", "bà": "ông"}
# Khuon chi hop MOT gioi, MOT lua tuoi -> cach bac si goi benh nhan duoc phep. Bang
# cu khong rang buoc, va da sinh ra "anh" bi viem am dao do nam, "chi" bi phi dai
# tuyen tien liet (tap train, 11/09/2026).
XUNG_HO_THEO_KHUON = {
    "viêm âm đạo do nấm": ("chị", "em", "cô"),
    "rối loạn kinh nguyệt": ("chị", "em"),
    "loãng xương sau mãn kinh": ("cô", "bà", "bác"),
    "phì đại lành tính tuyến tiền liệt": ("chú", "ông", "bác"),
}
GIOI_THEO_KHUON = {
    "viêm âm đạo do nấm": "nữ", "rối loạn kinh nguyệt": "nữ",
    "loãng xương sau mãn kinh": "nữ", "phì đại lành tính tuyến tiền liệt": "nam",
}

# Tieu tu cuoi cau, CHIA THEO VUNG va chon mot vung cho ca cuoc hoi thoai.
#
# Ban dau tron chung mot ro va boc ngau nhien tung cau. No de ra nhung cau kieu
# "Vâng bé nhà em đau họng hai hôm rồi nha." — "Vâng" la mien Bac, "nha" la mien
# Nam, khong ai noi lan nhu vay trong mot cau. Mot bo du lieu sai giong noi thi
# mo hinh se hoc dung cai sai do.
# Moi vung co HAI ro tieu tu, khong phai mot:
#
#   ket      dung cho CAU HOI va CAU KE — chi "ạ" hoac de trong
#   de_nghi  dung cho LOI DE NGHI cua bac si — "nhé", "nha", "nghen"
#
# Ban dau gop lam mot ro va no de ra "Gia đình có ai bị bệnh gì không nhé?" —
# "nhé"/"nghen" la tieu tu DE NGHI, gan vao cau hoi thi sai nga. Tach hai ro
# thi loi giu duoc mau vung ma khong sai chuc nang.
# `chao_cuoi` cung phai theo vung. Ban dau de mot danh sach chung cho ca ba
# mien nen mot cuoc thoai giong Nam van ket bang "Vâng, tôi cảm ơn bác sĩ" —
# tron giong ngay o cau cuoi cung.
MIEN = {
    "bac": {"ket": ["ạ", "ạ", "", ""], "de_nghi": ["nhé", "nhé", ""],
            "da_vang": ["Vâng", "Vâng", "Dạ", "Vâng ạ"],
            "chao_cuoi": ["Vâng, tôi cảm ơn bác sĩ.", "Vâng ạ, em cảm ơn bác sĩ.",
                          "Vâng, tôi nhớ rồi ạ."]},
    "nam": {"ket": ["ạ", "ạ", "", ""], "de_nghi": ["nha", "nghen", "nhé", ""],
            "da_vang": ["Dạ", "Dạ", "Dạ", "Dạ thưa bác sĩ"],
            "chao_cuoi": ["Dạ, cảm ơn bác sĩ ạ.", "Dạ em nhớ rồi ạ.",
                          "Dạ, em cảm ơn bác sĩ nhiều."]},
    "trung": {"ket": ["ạ", "ạ", "", ""], "de_nghi": ["nghe", "nhé", ""],
              "da_vang": ["Dạ", "Dạ", "Dạ vâng"],
              "chao_cuoi": ["Dạ, cháu cảm ơn bác sĩ.", "Dạ vâng, tôi cảm ơn bác sĩ."]},
}

# Tu dem cua BAC SI khi tiep loi. "Ừ" / "Rồi" la loi nguoi tren noi voi nguoi
# duoi — benh nhan va nguoi nha KHONG dung chung voi bac si. Tach hai ro de
# khong bao gio gan nham vai.
BAC_SI_TIEP_LOI = ["Ừ", "Rồi", "Được rồi", "Vâng", "À", "Tôi hiểu rồi"]

# ------------------------------------------------------------------ benh

# Moi benh: ten, nhom (nhi/nguoi lon/ca hai), trieu chung chinh, trieu chung
# phu, kham, chan doan, ke hoach.
BENH = [
    dict(ten="sốt xuất huyết", nhom="cả hai", dien_tien="cấp",
         chinh=["sốt cao", "đau đầu", "đau nhức người"],
         phu=["chán ăn", "buồn nôn", "nổi ban đỏ ở tay"],
         kham="Da nổi ban rải rác, dấu hiệu dây thắt dương tính.",
         chan_doan="Theo dõi sốt xuất huyết Dengue ngày thứ ba.",
         ke_hoach="Xét nghiệm công thức máu và NS1. Uống nhiều nước, hạ sốt bằng paracetamol, tuyệt đối không dùng ibuprofen."),
    dict(ten="tay chân miệng", nhom="nhi", dien_tien="cấp",
         chinh=["sốt", "nổi mụn nước ở lòng bàn tay", "biếng ăn"],
         phu=["chảy nước dãi nhiều", "quấy khóc", "loét miệng"],
         kham="Họng có vết loét nhỏ, lòng bàn tay và bàn chân có bọng nước.",
         chan_doan="Tay chân miệng độ 1.",
         ke_hoach="Theo dõi tại nhà, hạ sốt khi trên 38,5 độ. Cách ly, không cho đi lớp."),
    dict(ten="viêm họng cấp", nhom="cả hai", dien_tien="cấp",
         chinh=["đau họng", "sốt nhẹ", "ho"],
         phu=["khàn tiếng", "nuốt vướng", "mệt mỏi"],
         kham="Họng đỏ, amidan sưng nhẹ, không có mủ.",
         chan_doan="Viêm họng cấp.",
         ke_hoach="Súc họng nước muối, uống nhiều nước ấm, hạ sốt khi cần."),
    dict(ten="viêm phế quản", nhom="cả hai", dien_tien="cấp",
         chinh=["ho có đờm", "khò khè", "sốt nhẹ"],
         phu=["tức ngực", "khó thở khi gắng sức", "mất ngủ vì ho"],
         kham="Phổi nghe có ran ngáy hai bên.",
         chan_doan="Viêm phế quản cấp.",
         ke_hoach="Long đờm, uống nhiều nước. Tái khám nếu sốt quá ba ngày."),
    dict(ten="tiêu chảy cấp", nhom="cả hai", dien_tien="cấp",
         chinh=["đi ngoài phân lỏng", "đau bụng", "buồn nôn"],
         phu=["mệt lả", "khát nước nhiều", "sốt nhẹ"],
         kham="Bụng mềm, không có phản ứng thành bụng. Dấu véo da mất nhanh.",
         chan_doan="Tiêu chảy cấp, chưa có dấu mất nước nặng.",
         ke_hoach="Bù nước bằng oresol sau mỗi lần đi ngoài. Ăn cháo loãng, chia nhỏ bữa."),
    dict(ten="viêm tai giữa", nhom="nhi", dien_tien="cấp",
         chinh=["đau tai", "sốt", "quấy khóc về đêm"],
         phu=["nghe kém", "chảy dịch tai", "bỏ bú"],
         kham="Màng nhĩ đỏ, phồng nhẹ bên phải.",
         chan_doan="Viêm tai giữa cấp bên phải.",
         ke_hoach="Kháng sinh amoxicillin bảy ngày, giảm đau khi cần. Tái khám sau một tuần."),
    dict(ten="cúm mùa", nhom="cả hai", dien_tien="cấp",
         chinh=["sốt", "đau mỏi người", "hắt hơi sổ mũi"],
         phu=["đau họng", "ho khan", "chán ăn"],
         kham="Họng hơi đỏ, phổi không ran.",
         chan_doan="Cúm mùa.",
         ke_hoach="Nghỉ ngơi, hạ sốt, uống đủ nước. Đeo khẩu trang tránh lây cho người nhà."),
    dict(ten="viêm phổi", nhom="cả hai", dien_tien="cấp",
         chinh=["sốt cao", "ho nhiều", "thở nhanh"],
         phu=["đau ngực khi ho", "mệt", "ăn kém"],
         kham="Phổi nghe có ran ẩm đáy phổi phải.",
         chan_doan="Viêm phổi thùy dưới phải.",
         ke_hoach="Chụp X-quang ngực. Kháng sinh đường uống, theo dõi sát nhịp thở."),
    dict(ten="hen phế quản", nhom="cả hai", dien_tien="mạn",
         chinh=["khó thở", "khò khè", "ho về đêm"],
         phu=["nặng ngực", "khó thở khi trời lạnh", "mất ngủ"],
         kham="Phổi nghe ran rít lan tỏa hai bên.",
         chan_doan="Hen phế quản, cơn nhẹ.",
         ke_hoach="Xịt salbutamol khi lên cơn. Tránh khói bụi và lông vật nuôi."),
    dict(ten="đau dạ dày", nhom="người lớn", dien_tien="mạn",
         chinh=["đau vùng thượng vị", "ợ chua", "đầy bụng"],
         phu=["buồn nôn", "chán ăn", "đau tăng khi đói"],
         kham="Bụng mềm, ấn đau vùng thượng vị.",
         chan_doan="Viêm dạ dày, theo dõi loét.",
         ke_hoach="Nội soi dạ dày. Ăn đúng bữa, kiêng rượu bia và đồ chua cay."),
    dict(ten="tăng huyết áp", nhom="người lớn", dien_tien="mạn",
         chinh=["đau đầu", "hoa mắt", "mệt"],
         phu=["ù tai", "khó ngủ", "hồi hộp"],
         kham="Huyết áp 160/95 mmHg, tim đều.",
         chan_doan="Tăng huyết áp độ 2.",
         ke_hoach="Uống amlodipin mỗi sáng. Ăn nhạt, đo huyết áp hằng ngày và ghi lại."),
    dict(ten="đái tháo đường típ 2", nhom="người lớn", dien_tien="mạn",
         chinh=["khát nước nhiều", "tiểu nhiều", "sụt cân"],
         phu=["mệt mỏi", "mờ mắt", "vết thương lâu lành"],
         kham="Thể trạng gầy, không phù.",
         chan_doan="Đái tháo đường típ 2.",
         ke_hoach="Xét nghiệm HbA1c. Uống metformin sau ăn, giảm tinh bột, đi bộ ba mươi phút mỗi ngày."),
    dict(ten="gout", nhom="người lớn", dien_tien="cấp",
         chinh=["sưng đau khớp ngón chân cái", "đau tăng về đêm", "đỏ khớp"],
         phu=["đi lại khó", "sốt nhẹ", "mất ngủ vì đau"],
         kham="Khớp bàn ngón chân cái bên trái sưng nóng đỏ.",
         chan_doan="Cơn gout cấp.",
         ke_hoach="Xét nghiệm acid uric máu. Kiêng bia rượu, hải sản và nội tạng."),
    dict(ten="sỏi thận", nhom="người lớn", dien_tien="cấp",
         chinh=["đau quặn vùng thắt lưng", "tiểu buốt", "tiểu ra máu"],
         phu=["buồn nôn", "đau lan xuống bẹn", "sốt nhẹ"],
         kham="Ấn đau vùng hố thắt lưng phải.",
         chan_doan="Cơn đau quặn thận do sỏi niệu quản phải.",
         ke_hoach="Siêu âm hệ tiết niệu. Uống nhiều nước, giảm đau khi cần."),
    dict(ten="viêm xoang", nhom="cả hai", dien_tien="cấp",
         chinh=["nghẹt mũi", "đau vùng trán", "chảy mũi vàng"],
         phu=["giảm ngửi", "đau tăng khi cúi", "ho về đêm"],
         kham="Ấn đau điểm xoang trán và xoang hàm hai bên.",
         chan_doan="Viêm xoang cấp.",
         ke_hoach="Rửa mũi nước muối sinh lý, kháng sinh nếu không đỡ sau năm ngày."),
    dict(ten="thoái hóa cột sống", nhom="người lớn", dien_tien="mạn",
         chinh=["đau lưng", "cứng lưng buổi sáng", "đau lan xuống chân"],
         phu=["tê chân", "đau tăng khi ngồi lâu", "khó cúi"],
         kham="Cột sống thắt lưng hạn chế vận động, không teo cơ.",
         chan_doan="Thoái hóa cột sống thắt lưng.",
         ke_hoach="Chụp X-quang cột sống. Tập vận động nhẹ, tránh mang vác nặng."),
    dict(ten="viêm da cơ địa", nhom="cả hai", dien_tien="mạn",
         chinh=["ngứa nhiều", "nổi mẩn đỏ", "da khô bong"],
         phu=["ngứa tăng về đêm", "mất ngủ", "gãi trầy da"],
         kham="Da vùng khoeo chân và khuỷu tay đỏ, có vảy khô.",
         chan_doan="Viêm da cơ địa.",
         ke_hoach="Dưỡng ẩm ngày hai lần, tránh tắm nước quá nóng và xà phòng mạnh."),
    dict(ten="rối loạn tiền đình", nhom="người lớn", dien_tien="mạn",
         chinh=["chóng mặt", "buồn nôn", "mất thăng bằng"],
         phu=["ù tai", "sợ đi lại", "mệt"],
         kham="Không có dấu thần kinh khu trú.",
         chan_doan="Rối loạn tiền đình ngoại biên.",
         ke_hoach="Nghỉ ngơi, tránh thay đổi tư thế đột ngột. Tái khám nếu chóng mặt tăng."),
    dict(ten="thiếu máu thiếu sắt", nhom="cả hai", dien_tien="mạn",
         chinh=["mệt mỏi", "da xanh", "chóng mặt khi đứng dậy"],
         phu=["hồi hộp", "rụng tóc", "khó tập trung"],
         kham="Niêm mạc mắt nhợt, không gan lách to.",
         chan_doan="Thiếu máu thiếu sắt.",
         ke_hoach="Xét nghiệm công thức máu và sắt huyết thanh. Bổ sung sắt uống lúc đói."),
    dict(ten="viêm kết mạc", nhom="cả hai", dien_tien="cấp",
         chinh=["đỏ mắt", "cộm mắt", "chảy nước mắt"],
         phu=["ghèn nhiều buổi sáng", "sợ ánh sáng", "ngứa mắt"],
         kham="Kết mạc hai mắt cương tụ, giác mạc trong.",
         chan_doan="Viêm kết mạc cấp.",
         ke_hoach="Nhỏ nước muối sinh lý, không dụi mắt, dùng riêng khăn mặt."),
    dict(ten="trào ngược dạ dày thực quản", nhom="người lớn", dien_tien="mạn",
         chinh=["ợ nóng", "đau rát sau xương ức", "ho về đêm"],
         phu=["khàn tiếng buổi sáng", "đầy hơi", "nuốt vướng"],
         kham="Bụng mềm, không đau khu trú.",
         chan_doan="Trào ngược dạ dày thực quản.",
         ke_hoach="Không nằm ngay sau ăn, kê cao đầu giường. Uống omeprazole trước ăn sáng."),
    dict(ten="viêm khớp dạng thấp", nhom="người lớn", dien_tien="mạn",
         chinh=["sưng đau khớp bàn tay", "cứng khớp buổi sáng", "đau đối xứng hai bên"],
         phu=["mệt mỏi", "khó cầm nắm", "sốt nhẹ"],
         kham="Khớp bàn ngón tay hai bên sưng, ấn đau.",
         chan_doan="Theo dõi viêm khớp dạng thấp.",
         ke_hoach="Xét nghiệm RF và anti-CCP. Chuyển khám chuyên khoa cơ xương khớp."),
    dict(ten="nhiễm giun", nhom="nhi", dien_tien="mạn",
         chinh=["đau bụng quanh rốn", "ngứa hậu môn về đêm", "biếng ăn"],
         phu=["ngủ không yên", "chậm tăng cân", "da xanh"],
         kham="Bụng mềm, ấn đau nhẹ quanh rốn.",
         chan_doan="Nhiễm giun đường ruột.",
         ke_hoach="Tẩy giun định kỳ sáu tháng một lần cho cả nhà. Rửa tay trước khi ăn."),
    dict(ten="sốt siêu vi", nhom="cả hai", dien_tien="cấp",
         chinh=["sốt", "đau đầu", "mệt mỏi"],
         phu=["đau họng nhẹ", "chán ăn", "đau cơ"],
         kham="Họng hơi đỏ, không có ban.",
         chan_doan="Sốt siêu vi.",
         ke_hoach="Hạ sốt, uống nhiều nước, theo dõi thêm hai ngày. Đến ngay nếu sốt cao liên tục."),
    # ---------------------------------------------------------------- bo sung
    # 36 khuon them 10/09/2026. Ly do: 24 khuon la qua it de noi ket qua tren
    # "khuon chua tung thay" co suc thuyet phuc. Nhung so khuon KHONG phai
    # thu quan trong nhat — xem BOI_CANH, do moi la cho pha duoc do deu cua
    # mach hoi thoai.
    #
    # Goi la KHUON CA LAM SANG MO PHONG, khong goi la "60 loai benh": chung
    # duoc viet de sinh hoi thoai co du cac hien tuong ngon ngu can do, khong
    # phai de mo ta benh hoc.
    dict(ten="viêm dạ dày cấp", nhom="người lớn", dien_tien="cấp",
         chinh=["đau vùng thượng vị", "buồn nôn", "đầy bụng"],
         phu=["ợ chua", "chán ăn", "mệt"],
         kham="Bụng mềm, ấn đau nhẹ vùng thượng vị.",
         chan_doan="Viêm dạ dày cấp.",
         ke_hoach="Uống thuốc ức chế tiết axit trước ăn. Kiêng rượu bia, đồ chua cay."),
    dict(ten="táo bón chức năng", nhom="nhi", dien_tien="mạn",
         chinh=["đi ngoài khó", "phân cứng", "đau bụng"],
         phu=["chán ăn", "quấy khóc", "bụng chướng"],
         kham="Bụng chướng nhẹ, sờ thấy khối phân ở hố chậu trái.",
         chan_doan="Táo bón chức năng.",
         ke_hoach="Tăng rau và nước. Tập đi ngoài giờ cố định. Khám lại sau hai tuần."),
    dict(ten="viêm amidan cấp", nhom="cả hai", dien_tien="cấp",
         chinh=["đau họng", "sốt", "nuốt vướng"],
         phu=["hôi miệng", "mệt", "hạch cổ sưng"],
         kham="Amidan sưng đỏ hai bên, có chấm mủ.",
         chan_doan="Viêm amidan cấp.",
         ke_hoach="Kháng sinh mười ngày. Súc họng nước muối. Uống hết liều dù đã đỡ."),
    dict(ten="mày đay", nhom="cả hai", dien_tien="cấp",
         chinh=["nổi mẩn", "ngứa", "sẩn phù"],
         phu=["nóng rát da", "khó chịu", "mất ngủ"],
         kham="Sẩn phù rải rác thân mình, không phù mạch.",
         chan_doan="Mày đay cấp.",
         ke_hoach="Thuốc kháng histamin. Ghi lại thức ăn và thuốc đã dùng trước khi nổi."),
    dict(ten="viêm mũi dị ứng", nhom="cả hai", dien_tien="mạn",
         chinh=["hắt hơi", "chảy mũi trong", "ngạt mũi"],
         phu=["ngứa mắt", "ho về đêm", "mệt"],
         kham="Niêm mạc mũi nhợt, phù nề, dịch trong.",
         chan_doan="Viêm mũi dị ứng.",
         ke_hoach="Xịt mũi corticoid. Tránh bụi nhà và lông thú."),
    dict(ten="đau nửa đầu", nhom="người lớn", dien_tien="mạn",
         chinh=["đau nửa đầu", "sợ ánh sáng", "buồn nôn"],
         phu=["hoa mắt", "mệt", "khó tập trung"],
         kham="Không dấu thần kinh khu trú.",
         chan_doan="Đau nửa đầu.",
         ke_hoach="Ghi nhật ký cơn đau. Tránh thức khuya và bỏ bữa."),
    dict(ten="rối loạn lo âu", nhom="người lớn", dien_tien="mạn",
         chinh=["hồi hộp", "khó ngủ", "lo lắng"],
         phu=["mệt", "vã mồ hôi", "run tay"],
         kham="Tim đều, không tiếng thổi. Huyết áp bình thường.",
         chan_doan="Rối loạn lo âu.",
         ke_hoach="Tư vấn tâm lý. Hạn chế cà phê. Hẹn khám lại sau một tháng."),
    dict(ten="thiếu vitamin D", nhom="nhi", dien_tien="mạn",
         chinh=["chậm mọc răng", "ra mồ hôi trộm", "quấy khóc đêm"],
         phu=["chậm lên cân", "khó ngủ", "biếng ăn"],
         kham="Thóp rộng, chưa biến dạng xương.",
         chan_doan="Thiếu vitamin D.",
         ke_hoach="Bổ sung vitamin D theo liều. Cho tắm nắng buổi sáng."),
    dict(ten="viêm đường tiết niệu", nhom="người lớn", dien_tien="cấp",
         chinh=["tiểu buốt", "tiểu rắt", "đau bụng dưới"],
         phu=["sốt nhẹ", "mệt", "nước tiểu đục"],
         kham="Ấn đau vùng hạ vị, không đau góc sườn lưng.",
         chan_doan="Viêm đường tiết niệu dưới.",
         ke_hoach="Xét nghiệm nước tiểu. Kháng sinh năm ngày. Uống nhiều nước."),
    dict(ten="zona thần kinh", nhom="người lớn", dien_tien="cấp",
         chinh=["đau rát một bên", "nổi mụn nước", "ngứa"],
         phu=["sốt nhẹ", "mệt", "mất ngủ"],
         kham="Mụn nước thành chùm theo một khoanh da, một bên.",
         chan_doan="Zona thần kinh.",
         ke_hoach="Thuốc kháng virus trong bảy ngày. Giữ khô vùng tổn thương."),
    dict(ten="viêm kết mạc dị ứng", nhom="cả hai", dien_tien="mạn",
         chinh=["ngứa mắt", "chảy nước mắt", "đỏ mắt"],
         phu=["cộm mắt", "sợ sáng", "sưng mi"],
         kham="Kết mạc cương tụ nhẹ hai bên, không tiết dịch mủ.",
         chan_doan="Viêm kết mạc dị ứng.",
         ke_hoach="Nhỏ mắt kháng dị ứng. Không dụi mắt."),
    dict(ten="hội chứng ruột kích thích", nhom="người lớn", dien_tien="mạn",
         chinh=["đau bụng", "đi ngoài thất thường", "đầy hơi"],
         phu=["mệt", "chán ăn", "khó ngủ"],
         kham="Bụng mềm, ấn đau lan tỏa nhẹ.",
         chan_doan="Hội chứng ruột kích thích.",
         ke_hoach="Ghi nhật ký ăn uống. Chia nhỏ bữa. Khám lại sau một tháng."),
    dict(ten="viêm gan B mạn", nhom="người lớn", dien_tien="mạn",
         chinh=["mệt", "chán ăn", "đau hạ sườn phải"],
         phu=["buồn nôn", "vàng da nhẹ", "khó ngủ"],
         kham="Gan không to, không vàng da rõ.",
         chan_doan="Viêm gan B mạn, theo dõi.",
         ke_hoach="Xét nghiệm men gan và tải lượng virus. Không uống rượu."),
    dict(ten="suy giáp", nhom="người lớn", dien_tien="mạn",
         chinh=["mệt", "sợ lạnh", "tăng cân"],
         phu=["táo bón", "da khô", "chậm chạp"],
         kham="Tuyến giáp không to, da khô.",
         chan_doan="Theo dõi suy giáp.",
         ke_hoach="Xét nghiệm TSH và FT4. Hẹn khám lại khi có kết quả."),
    dict(ten="viêm khớp gối", nhom="người lớn", dien_tien="mạn",
         chinh=["đau khớp gối", "cứng khớp buổi sáng", "đi lại khó"],
         phu=["sưng gối", "mệt", "khó ngủ"],
         kham="Gối phải sưng nhẹ, hạn chế gấp.",
         chan_doan="Thoái hóa khớp gối.",
         ke_hoach="Giảm cân, tập cơ đùi. Thuốc giảm đau khi cần."),
    dict(ten="chàm sữa", nhom="nhi", dien_tien="mạn",
         chinh=["nổi mẩn đỏ ở má", "ngứa", "da khô"],
         phu=["quấy khóc", "khó ngủ", "gãi nhiều"],
         kham="Ban đỏ hai má, có vảy tiết, không bội nhiễm.",
         chan_doan="Chàm sữa.",
         ke_hoach="Dưỡng ẩm ngày hai lần. Tắm nước ấm, không dùng xà phòng thơm."),
    dict(ten="viêm tiểu phế quản", nhom="nhi", dien_tien="cấp",
         chinh=["ho", "khò khè", "thở nhanh"],
         phu=["sốt nhẹ", "bú kém", "quấy khóc"],
         kham="Phổi có ran rít lan tỏa, không rút lõm lồng ngực.",
         chan_doan="Viêm tiểu phế quản.",
         ke_hoach="Nhỏ mũi nước muối, theo dõi nhịp thở. Đưa đi ngay nếu thở co kéo."),
    dict(ten="sốt phát ban", nhom="nhi", dien_tien="cấp",
         chinh=["sốt", "nổi ban", "quấy khóc"],
         phu=["chán ăn", "mệt", "chảy mũi"],
         kham="Ban hồng rải rác thân mình, hạch cổ nhỏ.",
         chan_doan="Sốt phát ban.",
         ke_hoach="Hạ sốt khi trên 38,5 độ. Theo dõi thêm hai ngày."),
    dict(ten="quai bị", nhom="nhi", dien_tien="cấp",
         chinh=["sưng góc hàm", "đau khi nhai", "sốt"],
         phu=["mệt", "chán ăn", "khô miệng"],
         kham="Sưng tuyến mang tai một bên, ấn đau.",
         chan_doan="Quai bị.",
         ke_hoach="Nghỉ học đến khi hết sưng. Ăn mềm. Theo dõi đau bụng và sưng tinh hoàn."),
    dict(ten="thủy đậu", nhom="cả hai", dien_tien="cấp",
         chinh=["nổi mụn nước", "sốt", "ngứa"],
         phu=["mệt", "chán ăn", "đau đầu"],
         kham="Mụn nước nhiều lứa tuổi rải rác toàn thân.",
         chan_doan="Thủy đậu.",
         ke_hoach="Cách ly đến khi bong hết vảy. Giữ vệ sinh da, cắt móng tay."),
    dict(ten="viêm loét dạ dày do HP", nhom="người lớn", dien_tien="mạn",
         chinh=["đau thượng vị", "ợ hơi", "đầy bụng"],
         phu=["buồn nôn", "chán ăn", "sụt cân"],
         kham="Ấn đau thượng vị, không phản ứng thành bụng.",
         chan_doan="Viêm loét dạ dày, nghi nhiễm HP.",
         ke_hoach="Test hơi thở tìm HP. Hẹn khám lại khi có kết quả."),
    dict(ten="rối loạn lipid máu", nhom="người lớn", dien_tien="mạn",
         chinh=["mệt", "hoa mắt", "tê tay"],
         phu=["khó ngủ", "đau đầu", "hồi hộp"],
         kham="Không dấu hiệu bất thường khi khám.",
         chan_doan="Rối loạn lipid máu.",
         ke_hoach="Xét nghiệm mỡ máu lại sau ba tháng. Giảm mỡ động vật, tập thể dục."),
    dict(ten="thiếu máu do giun", nhom="nhi", dien_tien="mạn",
         chinh=["da xanh", "mệt", "chán ăn"],
         phu=["đau bụng quanh rốn", "ngứa hậu môn", "khó ngủ"],
         kham="Da niêm mạc nhợt nhẹ, bụng mềm.",
         chan_doan="Thiếu máu, theo dõi nhiễm giun.",
         ke_hoach="Xét nghiệm phân và công thức máu. Tẩy giun định kỳ."),
    dict(ten="viêm họng do liên cầu", nhom="nhi", dien_tien="cấp",
         chinh=["đau họng", "sốt cao", "nuốt đau"],
         phu=["đau đầu", "buồn nôn", "hạch cổ sưng"],
         kham="Họng đỏ, amidan có mủ, hạch cổ trước sưng đau.",
         chan_doan="Viêm họng nghi do liên cầu.",
         ke_hoach="Test nhanh liên cầu. Chưa kê kháng sinh cho tới khi có kết quả."),
    dict(ten="đau thần kinh tọa", nhom="người lớn", dien_tien="mạn",
         chinh=["đau lưng lan xuống chân", "tê chân", "đi lại khó"],
         phu=["mất ngủ", "mệt", "yếu chân"],
         kham="Dấu Lasègue dương tính bên phải.",
         chan_doan="Đau thần kinh tọa.",
         ke_hoach="Chụp cộng hưởng từ cột sống thắt lưng. Tránh mang vác nặng."),
    dict(ten="viêm bờ mi", nhom="cả hai", dien_tien="mạn",
         chinh=["đỏ bờ mi", "ngứa mắt", "cộm"],
         phu=["chảy nước mắt", "vảy ở chân lông mi", "mỏi mắt"],
         kham="Bờ mi đỏ, có vảy, kết mạc không cương tụ.",
         chan_doan="Viêm bờ mi.",
         ke_hoach="Chườm ấm và vệ sinh bờ mi hằng ngày."),
    dict(ten="viêm phổi cộng đồng người lớn", nhom="người lớn", dien_tien="cấp",
         chinh=["ho có đờm", "sốt", "khó thở"],
         phu=["đau ngực", "mệt", "chán ăn"],
         kham="Phổi phải có ran nổ đáy, nhịp thở 24 lần/phút.",
         chan_doan="Viêm phổi cộng đồng.",
         ke_hoach="Chụp X-quang ngực. Kháng sinh đường uống, khám lại sau ba ngày."),
    dict(ten="suy tĩnh mạch chi dưới", nhom="người lớn", dien_tien="mạn",
         chinh=["nặng chân", "phù cổ chân", "chuột rút đêm"],
         phu=["tê chân", "mệt", "khó ngủ"],
         kham="Giãn tĩnh mạch nông hai cẳng chân, phù nhẹ.",
         chan_doan="Suy tĩnh mạch chi dưới.",
         ke_hoach="Mang vớ áp lực. Tránh đứng lâu, kê cao chân khi nằm."),
    dict(ten="viêm da tiếp xúc", nhom="cả hai", dien_tien="cấp",
         chinh=["đỏ da", "ngứa", "rát"],
         phu=["nổi mụn nước nhỏ", "khó ngủ", "khó chịu"],
         kham="Ban đỏ giới hạn rõ ở vùng tiếp xúc.",
         chan_doan="Viêm da tiếp xúc.",
         ke_hoach="Ngừng tiếp xúc chất nghi ngờ. Bôi corticoid nhẹ trong năm ngày."),
    dict(ten="rối loạn tiêu hóa do kháng sinh", nhom="cả hai", dien_tien="cấp",
         chinh=["đi ngoài phân lỏng", "đau bụng", "đầy hơi"],
         phu=["chán ăn", "mệt", "buồn nôn"],
         kham="Bụng mềm, không phản ứng thành bụng.",
         chan_doan="Rối loạn tiêu hóa sau dùng kháng sinh.",
         ke_hoach="Bù nước điện giải. Men vi sinh. Không tự ngừng kháng sinh đang điều trị."),
    dict(ten="cận thị tiến triển", nhom="nhi", dien_tien="mạn",
         chinh=["nhìn xa mờ", "nheo mắt", "mỏi mắt"],
         phu=["đau đầu", "khó tập trung", "chảy nước mắt"],
         kham="Thị lực không kính hai mắt giảm.",
         chan_doan="Cận thị tiến triển.",
         ke_hoach="Đo khúc xạ lại. Hạn chế màn hình, tăng hoạt động ngoài trời."),
    dict(ten="viêm tuyến giáp bán cấp", nhom="người lớn", dien_tien="cấp",
         chinh=["đau vùng cổ trước", "sốt nhẹ", "mệt"],
         phu=["hồi hộp", "sụt cân", "khó nuốt"],
         kham="Tuyến giáp to nhẹ, ấn đau.",
         chan_doan="Theo dõi viêm tuyến giáp bán cấp.",
         ke_hoach="Xét nghiệm chức năng tuyến giáp. Giảm đau khi cần."),
    dict(ten="loãng xương sau mãn kinh", nhom="người lớn", dien_tien="mạn",
         chinh=["đau lưng", "giảm chiều cao", "mỏi người"],
         phu=["chuột rút", "mệt", "khó ngủ"],
         kham="Gù nhẹ cột sống ngực, không điểm đau khu trú.",
         chan_doan="Theo dõi loãng xương.",
         ke_hoach="Đo mật độ xương. Bổ sung canxi và vitamin D."),
    dict(ten="viêm mũi họng cấp", nhom="nhi", dien_tien="cấp",
         chinh=["chảy mũi", "ho", "sốt nhẹ"],
         phu=["quấy khóc", "bú kém", "ngạt mũi"],
         kham="Họng đỏ nhẹ, mũi nhiều dịch trong.",
         chan_doan="Viêm mũi họng cấp do virus.",
         ke_hoach="Nhỏ mũi nước muối. Không dùng kháng sinh. Theo dõi ba ngày."),
    dict(ten="hạ đường huyết do thuốc", nhom="người lớn", dien_tien="cấp",
         chinh=["vã mồ hôi", "run tay", "hoa mắt"],
         phu=["hồi hộp", "mệt", "đói cồn cào"],
         kham="Da ẩm, mạch nhanh nhẹ, tỉnh táo.",
         chan_doan="Hạ đường huyết nghi do thuốc hạ đường huyết.",
         ke_hoach="Đo đường huyết mao mạch. Xem lại liều thuốc đang dùng."),
    dict(ten="mất ngủ mạn tính", nhom="người lớn", dien_tien="mạn",
         chinh=["khó vào giấc", "thức giấc đêm", "mệt ban ngày"],
         phu=["khó tập trung", "hồi hộp", "đau đầu"],
         kham="Không phát hiện bất thường khi khám.",
         chan_doan="Mất ngủ mạn tính.",
         ke_hoach="Vệ sinh giấc ngủ. Bỏ cà phê buổi chiều. Chưa dùng thuốc ngủ."),

    # ---------------------------------------------- 40 khuon them 11/09/2026
    #
    # VI SAO THEM, va chon theo cai gi. Do 60 khuon cu theo he co quan: TAI 1
    # khuon, TIET NIEU - SINH DUC 2, TIM MACH 3, HUYET HOC 3, CO XUONG KHOP 4,
    # MAT 4 — trong khi ho hap 12, tieu hoa 10. Va chi 13/60 khuon la nhi.
    #
    # 40 khuon duoi day lap cac he mong truoc, va nang so khuon nhi tu 13 len 21.
    # Chi chon benh NGOAI TRU THUONG GAP voi bieu hien SACH GIAO KHOA — khong
    # chon benh hiem, vi o do kha nang viet sai ve y khoa cao hon.
    #
    # PHAI CO BAC SI DOC. Cung nhu 60 khuon cu, 40 khuon nay do AI viet (xem
    # `docs/khai-ma-nguon.md`), va tinh dung ve y khoa chua duoc ai kiem.

    # --- tai (3)
    dict(ten="viêm tai ngoài", nhom="cả hai", dien_tien="cấp",
         chinh=["đau tai", "ngứa tai", "chảy dịch tai"],
         phu=["nghe kém", "đau khi nhai", "sốt nhẹ"],
         kham="Ống tai ngoài sưng nề, kéo vành tai đau tăng.",
         chan_doan="Viêm tai ngoài cấp.",
         ke_hoach="Giữ tai khô. Nhỏ tai kháng sinh. Hẹn khám lại sau một tuần."),
    dict(ten="nút ráy tai", nhom="cả hai", dien_tien="cấp",
         chinh=["ù tai", "nghe kém", "cảm giác đầy tai"],
         phu=["ngứa tai", "chóng mặt nhẹ", "khó chịu trong tai"],
         kham="Ống tai có nút ráy, màng nhĩ không quan sát được.",
         chan_doan="Nút ráy tai.",
         ke_hoach="Nhỏ dầu làm mềm ráy ba ngày rồi lấy ráy tại phòng khám."),
    dict(ten="viêm tai giữa ứ dịch", nhom="nhi", dien_tien="mạn",
         chinh=["nghe kém", "hay hỏi lại", "ù tai"],
         phu=["ngáy", "ngạt mũi", "chậm nói"],
         kham="Màng nhĩ đục, có mức dịch sau màng nhĩ.",
         chan_doan="Viêm tai giữa ứ dịch.",
         ke_hoach="Theo dõi ba tháng. Đo nhĩ lượng. Chuyển tai mũi họng nếu không cải thiện."),

    # --- tiet nieu, sinh duc (5)
    dict(ten="phì đại lành tính tuyến tiền liệt", nhom="người lớn", dien_tien="mạn",
         chinh=["tiểu đêm", "tiểu khó", "dòng tiểu yếu"],
         phu=["tiểu không hết", "tiểu gấp", "phải rặn khi tiểu"],
         kham="Bụng mềm, cầu bàng quang âm tính.",
         chan_doan="Phì đại lành tính tuyến tiền liệt.",
         ke_hoach="Siêu âm tiền liệt tuyến và đo nước tiểu tồn dư. Hạn chế uống nước buổi tối."),
    dict(ten="viêm âm đạo do nấm", nhom="người lớn", dien_tien="cấp",
         chinh=["ngứa âm hộ", "khí hư trắng đục", "rát khi tiểu"],
         phu=["đau khi quan hệ", "khó chịu vùng kín", "mất ngủ"],
         kham="Niêm mạc âm đạo đỏ, khí hư trắng như bột.",
         chan_doan="Viêm âm đạo do nấm.",
         ke_hoach="Đặt thuốc kháng nấm bảy ngày. Giữ vệ sinh, mặc đồ lót thoáng."),
    dict(ten="rối loạn kinh nguyệt", nhom="người lớn", dien_tien="mạn",
         chinh=["kinh không đều", "rong kinh", "đau bụng kinh"],
         phu=["mệt", "chóng mặt", "da xanh"],
         kham="Bụng mềm, không có khối bất thường vùng hạ vị.",
         chan_doan="Rối loạn kinh nguyệt.",
         ke_hoach="Siêu âm phụ khoa, xét nghiệm công thức máu. Ghi lịch kinh ba tháng."),
    dict(ten="đái dầm", nhom="nhi", dien_tien="mạn",
         chinh=["tiểu dầm ban đêm", "ngủ say khó đánh thức", "dậy ướt giường"],
         phu=["xấu hổ", "ngại ngủ nhà người khác", "uống nhiều nước buổi tối"],
         kham="Không phát hiện bất thường khi khám.",
         chan_doan="Đái dầm nguyên phát.",
         ke_hoach="Hạn chế nước sau bữa tối. Đi tiểu trước khi ngủ. Không la mắng trẻ."),
    dict(ten="nhiễm khuẩn tiết niệu ở trẻ", nhom="nhi", dien_tien="cấp",
         chinh=["sốt", "quấy khóc khi tiểu", "tiểu nhiều lần"],
         phu=["bỏ bú", "nôn", "nước tiểu đục"],
         kham="Bụng mềm, không có dấu mất nước.",
         chan_doan="Nhiễm khuẩn tiết niệu.",
         ke_hoach="Xét nghiệm và cấy nước tiểu. Kháng sinh theo kết quả. Uống nhiều nước."),

    # --- tim mach (4)
    dict(ten="đau thắt ngực ổn định", nhom="người lớn", dien_tien="mạn",
         chinh=["đau ngực khi gắng sức", "tức ngực lan tay trái", "khó thở khi leo cầu thang"],
         phu=["vã mồ hôi", "mệt", "hồi hộp"],
         kham="Tim đều, không tiếng thổi, huyết áp 140/85 mmHg.",
         chan_doan="Đau thắt ngực ổn định.",
         ke_hoach="Điện tim và nghiệm pháp gắng sức. Ngậm nitroglycerin khi đau. Tránh gắng sức nặng."),
    dict(ten="rung nhĩ", nhom="người lớn", dien_tien="mạn",
         chinh=["hồi hộp", "tim đập không đều", "mệt"],
         phu=["khó thở", "chóng mặt", "tức ngực"],
         kham="Tim loạn nhịp hoàn toàn, mạch nhanh không đều.",
         chan_doan="Rung nhĩ.",
         ke_hoach="Điện tim, siêu âm tim. Đánh giá nguy cơ đột quỵ để cân nhắc chống đông."),
    dict(ten="suy tim mạn", nhom="người lớn", dien_tien="mạn",
         chinh=["khó thở khi nằm", "phù chân", "mệt"],
         phu=["ho về đêm", "tiểu ít", "tăng cân nhanh"],
         kham="Phù hai chân, phổi có ran ẩm hai đáy.",
         chan_doan="Suy tim mạn.",
         ke_hoach="Siêu âm tim, xét nghiệm NT-proBNP. Hạn chế muối. Cân hằng ngày."),
    dict(ten="ngoại tâm thu", nhom="người lớn", dien_tien="mạn",
         chinh=["hồi hộp", "cảm giác hẫng nhịp", "tim đập mạnh"],
         phu=["lo lắng", "mất ngủ", "mệt"],
         kham="Tim đều, thỉnh thoảng có nhát bóp sớm.",
         chan_doan="Ngoại tâm thu thất.",
         ke_hoach="Điện tim và Holter 24 giờ. Giảm cà phê, trà đặc."),

    # --- co xuong khop (5)
    dict(ten="đau thắt lưng cơ năng", nhom="người lớn", dien_tien="cấp",
         chinh=["đau thắt lưng", "cứng lưng buổi sáng", "đau khi cúi"],
         phu=["khó ngủ", "đau tăng khi ngồi lâu", "mỏi vai"],
         kham="Co cứng cơ cạnh cột sống thắt lưng, không dấu thần kinh khu trú.",
         chan_doan="Đau thắt lưng cơ năng.",
         ke_hoach="Giảm đau, chườm ấm, vận động nhẹ. Tránh mang vác nặng."),
    dict(ten="bong gân cổ chân", nhom="cả hai", dien_tien="cấp",
         chinh=["đau cổ chân", "sưng cổ chân", "khó đi lại"],
         phu=["bầm tím", "đau khi xoay chân", "đi khập khiễng"],
         kham="Cổ chân sưng nhẹ, ấn đau dây chằng ngoài.",
         chan_doan="Bong gân cổ chân độ một.",
         ke_hoach="Nghỉ ngơi, chườm lạnh, băng ép, kê cao chân. Chụp X-quang nếu không đỡ."),
    dict(ten="hội chứng ống cổ tay", nhom="người lớn", dien_tien="mạn",
         chinh=["tê ngón tay", "tê về đêm", "yếu cầm nắm"],
         phu=["đau cổ tay", "hay rơi đồ", "tê lan cẳng tay"],
         kham="Dấu Tinel dương tính ở cổ tay.",
         chan_doan="Hội chứng ống cổ tay.",
         ke_hoach="Nẹp cổ tay ban đêm. Đo điện cơ. Hạn chế động tác lặp lại."),
    dict(ten="viêm quanh khớp vai", nhom="người lớn", dien_tien="mạn",
         chinh=["đau vai", "hạn chế giơ tay", "đau về đêm"],
         phu=["khó chải đầu", "khó mặc áo", "mỏi cổ"],
         kham="Hạn chế vận động khớp vai, ấn đau mặt trước vai.",
         chan_doan="Viêm quanh khớp vai.",
         ke_hoach="Giảm đau, tập vận động khớp vai. Siêu âm khớp vai nếu không đỡ."),
    dict(ten="đau vai gáy", nhom="người lớn", dien_tien="mạn",
         chinh=["đau gáy", "cứng cổ", "đau lan vai"],
         phu=["đau đầu", "mỏi mắt", "khó xoay cổ"],
         kham="Co cứng cơ thang hai bên, ấn đau vùng gáy.",
         chan_doan="Đau vai gáy do tư thế.",
         ke_hoach="Điều chỉnh tư thế làm việc. Chườm ấm, tập giãn cơ cổ vai."),

    # --- mat (2)
    dict(ten="lẹo mắt", nhom="cả hai", dien_tien="cấp",
         chinh=["sưng mi mắt", "đau mi mắt", "cộm mắt"],
         phu=["chảy nước mắt", "ngứa mắt", "đỏ mi"],
         kham="Bờ mi trên có khối sưng đỏ, ấn đau.",
         chan_doan="Lẹo mắt.",
         ke_hoach="Chườm ấm ngày ba lần. Không nặn. Tra mỡ kháng sinh."),
    dict(ten="khô mắt", nhom="người lớn", dien_tien="mạn",
         chinh=["cộm mắt", "mỏi mắt", "nóng rát mắt"],
         phu=["nhìn mờ thoáng qua", "chảy nước mắt", "sợ ánh sáng"],
         kham="Kết mạc không cương tụ, phim nước mắt vỡ nhanh.",
         chan_doan="Khô mắt.",
         ke_hoach="Nước mắt nhân tạo. Nghỉ mắt khi dùng máy tính. Hẹn khám lại một tháng."),

    # --- than kinh (3)
    dict(ten="đau đầu căng thẳng", nhom="người lớn", dien_tien="mạn",
         chinh=["đau đầu như đè ép", "đau hai bên thái dương", "đau về chiều"],
         phu=["mỏi cổ", "mất ngủ", "căng thẳng"],
         kham="Không dấu thần kinh khu trú.",
         chan_doan="Đau đầu kiểu căng thẳng.",
         ke_hoach="Giảm đau khi cần, không quá ba ngày một tuần. Ngủ đủ, giảm căng thẳng."),
    dict(ten="liệt mặt ngoại biên", nhom="người lớn", dien_tien="cấp",
         chinh=["méo miệng", "nhắm mắt không kín", "chảy nước bọt"],
         phu=["đau sau tai", "mất vị giác", "chảy nước mắt"],
         kham="Liệt mặt ngoại biên bên phải, dấu Charles Bell dương tính.",
         chan_doan="Liệt mặt ngoại biên.",
         ke_hoach="Dùng corticoid sớm. Bảo vệ mắt, tra nước mắt nhân tạo. Tập cơ mặt."),
    dict(ten="co giật do sốt", nhom="nhi", dien_tien="cấp",
         chinh=["sốt cao", "co giật toàn thân", "lơ mơ sau cơn"],
         phu=["quấy khóc", "chảy mũi", "bỏ bú"],
         kham="Tỉnh, thóp phẳng, không dấu màng não.",
         chan_doan="Co giật do sốt đơn giản.",
         ke_hoach="Hạ sốt tích cực. Hướng dẫn xử trí khi co giật. Đến viện ngay nếu cơn kéo dài."),

    # --- da lieu (5)
    dict(ten="nấm da thân", nhom="cả hai", dien_tien="mạn",
         chinh=["ngứa", "mảng da đỏ hình tròn", "bong vảy"],
         phu=["lan rộng dần", "ngứa tăng khi ra mồ hôi", "thâm da"],
         kham="Mảng da hình vòng, bờ đỏ có vảy.",
         chan_doan="Nấm da thân.",
         ke_hoach="Bôi kem kháng nấm hai tuần. Giữ da khô. Không dùng chung khăn."),
    dict(ten="trứng cá", nhom="cả hai", dien_tien="mạn",
         chinh=["nổi mụn ở mặt", "mụn mủ", "da nhờn"],
         phu=["thâm da", "ngứa", "tự ti"],
         kham="Nhân mụn và sẩn viêm vùng trán, má.",
         chan_doan="Trứng cá thông thường.",
         ke_hoach="Rửa mặt bằng sữa rửa dịu nhẹ. Bôi thuốc trị mụn. Không nặn mụn."),
    dict(ten="ghẻ", nhom="cả hai", dien_tien="cấp",
         chinh=["ngứa về đêm", "nổi sẩn ở kẽ tay", "người nhà cũng ngứa"],
         phu=["trầy xước do gãi", "mụn nước nhỏ", "khó ngủ"],
         kham="Sẩn và mụn nước ở kẽ ngón tay, có rãnh ghẻ.",
         chan_doan="Ghẻ.",
         ke_hoach="Bôi thuốc trị ghẻ cho cả nhà cùng lúc. Giặt nóng quần áo, chăn màn."),
    dict(ten="vảy nến", nhom="người lớn", dien_tien="mạn",
         chinh=["mảng da đỏ", "bong vảy trắng", "ngứa"],
         phu=["nứt da", "đau khớp nhẹ", "móng rỗ"],
         kham="Mảng hồng ban giới hạn rõ, phủ vảy trắng dày ở khuỷu tay.",
         chan_doan="Vảy nến thể mảng.",
         ke_hoach="Bôi thuốc làm mềm da và corticoid. Tránh cào gãi. Khám da liễu định kỳ."),
    dict(ten="chốc lở", nhom="nhi", dien_tien="cấp",
         chinh=["mụn nước quanh miệng", "vảy vàng", "ngứa"],
         phu=["lan nhanh", "sốt nhẹ", "quấy khóc"],
         kham="Mụn nước và vảy tiết màu mật ong quanh mũi miệng.",
         chan_doan="Chốc lở.",
         ke_hoach="Rửa sạch vảy, bôi kháng sinh. Cắt móng tay cho trẻ. Tránh lây cho trẻ khác."),

    # --- ho hap (3)
    dict(ten="viêm thanh quản cấp", nhom="nhi", dien_tien="cấp",
         chinh=["ho ông ổng", "khàn tiếng", "thở rít"],
         phu=["sốt nhẹ", "chảy mũi", "quấy khóc về đêm"],
         kham="Thở rít khi quấy khóc, không rút lõm lồng ngực.",
         chan_doan="Viêm thanh quản cấp.",
         ke_hoach="Corticoid một liều. Giữ trẻ yên, tránh khóc nhiều. Đến viện nếu thở rít khi nằm yên."),
    dict(ten="bệnh phổi tắc nghẽn mạn tính", nhom="người lớn", dien_tien="mạn",
         chinh=["khó thở khi gắng sức", "ho khạc đờm", "khò khè"],
         phu=["mệt", "sụt cân", "phải ngồi mới ngủ được"],
         kham="Phổi có ran rít hai bên, lồng ngực hình thùng.",
         chan_doan="Bệnh phổi tắc nghẽn mạn tính.",
         ke_hoach="Đo chức năng hô hấp. Thuốc giãn phế quản dạng xịt. Bỏ thuốc lá."),
    dict(ten="viêm mũi xoang mạn tính", nhom="người lớn", dien_tien="mạn",
         chinh=["ngạt mũi kéo dài", "chảy dịch xuống họng", "giảm ngửi"],
         phu=["nặng mặt", "ho về đêm", "đau đầu"],
         kham="Niêm mạc mũi phù nề, dịch nhầy khe giữa.",
         chan_doan="Viêm mũi xoang mạn tính.",
         ke_hoach="Rửa mũi nước muối. Xịt corticoid mũi. Chụp CT xoang nếu không đỡ."),

    # --- tieu hoa (4)
    dict(ten="trĩ", nhom="người lớn", dien_tien="mạn",
         chinh=["đi ngoài ra máu", "đau hậu môn", "sa búi trĩ"],
         phu=["ngứa hậu môn", "táo bón", "cộm khi ngồi"],
         kham="Búi trĩ nội độ hai, không chảy máu lúc khám.",
         chan_doan="Trĩ nội độ hai.",
         ke_hoach="Ăn nhiều chất xơ, uống nhiều nước. Ngâm hậu môn nước ấm. Thuốc bôi trĩ."),
    dict(ten="sỏi túi mật", nhom="người lớn", dien_tien="mạn",
         chinh=["đau hạ sườn phải", "đau sau ăn nhiều mỡ", "đầy bụng"],
         phu=["buồn nôn", "ợ hơi", "chán ăn"],
         kham="Bụng mềm, ấn đau nhẹ hạ sườn phải.",
         chan_doan="Sỏi túi mật.",
         ke_hoach="Siêu âm bụng. Hạn chế mỡ. Hẹn ngoại khoa nếu đau tái diễn."),
    dict(ten="gan nhiễm mỡ", nhom="người lớn", dien_tien="mạn",
         chinh=["mệt", "nặng hạ sườn phải", "đầy bụng"],
         phu=["tăng cân", "chán ăn", "khó tiêu"],
         kham="Gan không to, không vàng da.",
         chan_doan="Gan nhiễm mỡ.",
         ke_hoach="Siêu âm gan, xét nghiệm men gan và mỡ máu. Giảm cân, bỏ rượu bia."),
    dict(ten="ngộ độc thực phẩm", nhom="cả hai", dien_tien="cấp",
         chinh=["nôn nhiều", "đau bụng", "đi ngoài phân lỏng"],
         phu=["sốt nhẹ", "mệt", "khát nước"],
         kham="Bụng mềm, không có phản ứng thành bụng.",
         chan_doan="Ngộ độc thực phẩm.",
         ke_hoach="Bù nước bằng oresol. Ăn nhẹ. Đến viện nếu nôn không uống được."),

    # --- noi tiet, chuyen hoa (3)
    dict(ten="cường giáp", nhom="người lớn", dien_tien="mạn",
         chinh=["sụt cân", "hồi hộp", "run tay"],
         phu=["ra nhiều mồ hôi", "sợ nóng", "mất ngủ"],
         kham="Tuyến giáp to lan tỏa, mạch nhanh, run tay.",
         chan_doan="Cường giáp.",
         ke_hoach="Xét nghiệm TSH, FT4. Siêu âm tuyến giáp. Chuyển nội tiết."),
    dict(ten="tiền đái tháo đường", nhom="người lớn", dien_tien="mạn",
         chinh=["khát nước", "mệt", "tăng cân"],
         phu=["tiểu nhiều", "vết thương lâu lành", "buồn ngủ sau ăn"],
         kham="Thể trạng béo, không phát hiện bất thường khác.",
         chan_doan="Tiền đái tháo đường.",
         ke_hoach="Xét nghiệm HbA1c. Giảm tinh bột và đường. Tập thể dục ba mươi phút mỗi ngày."),
    dict(ten="béo phì", nhom="cả hai", dien_tien="mạn",
         chinh=["tăng cân", "khó thở khi gắng sức", "ngáy"],
         phu=["mệt", "đau khớp gối", "ăn nhiều về đêm"],
         kham="Thể trạng béo, vòng bụng lớn.",
         chan_doan="Béo phì độ một.",
         ke_hoach="Chế độ ăn giảm năng lượng. Tập thể dục. Xét nghiệm đường huyết và mỡ máu."),

    # --- tam than (1)
    dict(ten="trầm cảm", nhom="người lớn", dien_tien="mạn",
         chinh=["buồn chán kéo dài", "mất hứng thú", "mất ngủ"],
         phu=["chán ăn", "mệt", "khó tập trung"],
         kham="Không phát hiện bất thường khi khám.",
         chan_doan="Trầm cảm mức độ nhẹ.",
         ke_hoach="Chuyển khám tâm thần. Hỏi về ý nghĩ tự hại. Hẹn khám lại hai tuần."),

    # --- nhi them (2)
    dict(ten="viêm da tã lót", nhom="nhi", dien_tien="cấp",
         chinh=["đỏ da vùng quấn tã", "quấy khóc khi thay tã", "da ướt"],
         phu=["nổi mụn đỏ", "ngứa", "bong da"],
         kham="Da vùng mông đỏ, không có mụn mủ.",
         chan_doan="Viêm da tã lót.",
         ke_hoach="Thay tã thường xuyên. Để da thoáng. Bôi kem kẽm oxit."),
    dict(ten="nôn trớ sinh lý", nhom="nhi", dien_tien="mạn",
         chinh=["nôn trớ sau bú", "trớ sữa", "ợ hơi"],
         phu=["quấy khóc sau bú", "nấc", "ngủ không yên"],
         kham="Bụng mềm, trẻ tăng cân tốt.",
         chan_doan="Nôn trớ sinh lý.",
         ke_hoach="Cho bú ít một, bế đứng sau bú. Theo dõi cân nặng. Khám lại nếu nôn vọt."),
]

# ------------------------------------------------------------ tien su, thuoc

# Tien su cua chinh benh nhan, CHIA THEO LUA TUOI. Mot em be "co roi loan mo
# mau" hay "tang huyet ap" thi bac si doc qua la thay sai ngay.
TIEN_SU_NGUOI_LON = [
    "viêm dạ dày", "tăng huyết áp", "đái tháo đường", "sỏi thận", "viêm gan B",
    "thiếu máu", "viêm xoang mạn", "đau nửa đầu", "trào ngược dạ dày",
    "rối loạn mỡ máu", "viêm khớp", "gout",
]
TIEN_SU_TRE_EM = [
    "hen phế quản", "viêm mũi dị ứng", "viêm tai giữa tái đi tái lại",
    "chàm sữa", "viêm amidan hay tái phát", "thiếu máu thiếu sắt",
    "sinh non", "dị ứng đạm sữa bò",
]

# Benh cua NGUOI NHA — nguon loi quy gan quan trong nhat cua bo du lieu.
#
# Chia theo lua tuoi vi tinh hop ly cua ca benh cung la mot phan chat luong du
# lieu: mot nguoi me tre dua con di kham ma "bi tai bien mach mau nao" thi bac
# si doc qua la thay sai ngay. Benh nang cua nguoi gia de rieng.
# ------------------------------------------- noi dung ke ve NGUOI NHA (tang 4)
#
# VI SAO MO RONG — do ngay 11/09/2026. Tang 4 (nguoi nha ke ve CHINH MINH) la
# cho du an ton tai, va truoc do no chi co **25 noi dung khac nhau** tren 1.101
# menh de cua tap train: 12 benh + 6 benh tuoi gia + 7 thuoc di ung. Tap phat
# trien dung lai dung 25/25 chuoi do (284/284 menh de). Mot mo hinh hoc thuoc 25
# chuoi "cai nay thuoc tien su gia dinh" se dat diem cao ma khong hoc quy gan gi.
#
# Nay 200 noi dung: 112 benh moi lua tuoi + 38 benh tuoi gia + 50 chat di ung
# (DI_UNG_NGUOI_NHA, rieng voi THUOC_DI_UNG cua benh nhan). Va bo sinh rut chung
# theo TAP — xem `sinh_hoi_thoai_viet.be_theo_tap`.
#
# Tranh chuoi GAN TRUNG giua hai bang ("loang xuong" va "loang xuong nang"): de
# hai chuoi gan trung roi vao hai tap khac nhau la ro ri noi dung qua tap, dung
# cai ma viec chia theo tap duoc lam ra de chan.
TIEN_SU_GIA_DINH_MOI_TUOI = [
    # 12 chuoi cu, giu nguyen
    "tăng huyết áp", "đái tháo đường", "hen phế quản", "viêm gan B", "gout",
    "sỏi thận", "dị ứng thời tiết", "viêm khớp", "lao phổi", "viêm dạ dày",
    "rối loạn mỡ máu", "viêm xoang mạn",
    # tim mach (8)
    "hở van hai lá", "rối loạn nhịp tim", "giãn tĩnh mạch chân",
    "bệnh cơ tim giãn", "tim bẩm sinh đã mổ", "thiếu máu cơ tim",
    "huyết áp thấp", "sa van hai lá",
    # noi tiet, chuyen hoa (9)
    "cường giáp", "suy giáp", "bướu giáp nhân", "béo phì",
    "tiền đái tháo đường", "hội chứng buồng trứng đa nang",
    "đái tháo đường thai kỳ", "rối loạn chuyển hóa", "thiếu vitamin D",
    # ho hap (7)
    "viêm mũi dị ứng", "viêm phế quản mạn", "ngưng thở khi ngủ", "bụi phổi",
    "giãn phế quản", "viêm họng mạn", "tràn khí màng phổi cũ",
    # tieu hoa (13)
    "loét tá tràng", "trào ngược dạ dày thực quản", "viêm đại tràng mạn",
    "hội chứng ruột kích thích", "trĩ", "sỏi túi mật", "gan nhiễm mỡ",
    "viêm gan C", "polyp đại tràng", "viêm loét dạ dày do HP", "táo bón mạn",
    "viêm tụy mạn", "không dung nạp lactose",
    # than, tiet nieu (6)
    "viêm cầu thận", "thận đa nang", "nhiễm trùng tiểu tái phát",
    "sỏi niệu quản", "sỏi bàng quang", "hội chứng thận hư",
    # co xuong khop (10)
    "viêm khớp dạng thấp", "thoát vị đĩa đệm", "đau thần kinh tọa",
    "viêm cột sống dính khớp", "loãng xương", "thoái hóa cột sống cổ",
    "lupus ban đỏ", "viêm quanh khớp vai", "hội chứng ống cổ tay", "gai cột sống",
    # than kinh (6)
    "đau nửa đầu", "động kinh", "rối loạn tiền đình", "đau đầu mạn tính",
    "liệt mặt đã hồi phục", "run tay vô căn",
    # tam than (5)
    "trầm cảm", "rối loạn lo âu", "mất ngủ mạn tính", "rối loạn hoảng sợ",
    "rối loạn lưỡng cực",
    # da (7)
    "vảy nến", "chàm", "mày đay mạn", "viêm da cơ địa", "bạch biến",
    "rụng tóc từng vùng", "trứng cá nặng",
    # mat (5)
    "cận thị nặng", "glôcôm", "viêm kết mạc dị ứng", "loạn thị", "khô mắt",
    # tai mui hong (4)
    "viêm amidan mạn", "viêm tai giữa mạn", "nghe kém", "polyp mũi",
    # huyet hoc (5)
    "thalassemia", "thiếu máu thiếu sắt", "giảm tiểu cầu", "máu khó đông",
    "thiếu men G6PD",
    # ung thu da dieu tri (7)
    "ung thư vú", "ung thư tuyến giáp", "ung thư cổ tử cung",
    "ung thư đại tràng", "ung thư gan", "ung thư phổi", "ung thư vòm họng",
    # phu khoa, nam khoa (5)
    "u xơ tử cung", "lạc nội mạc tử cung", "u nang buồng trứng", "vô sinh",
    "giãn tĩnh mạch thừng tinh",
    # khac (3)
    "sốt rét cũ", "viêm gan A cũ", "zona đã khỏi",
]
TIEN_SU_GIA_DINH_LON_TUOI = [
    # 6 chuoi cu, giu nguyen
    "tai biến mạch máu não", "ung thư dạ dày", "bệnh tim", "suy thận",
    "thoái hóa khớp gối", "đục thủy tinh thể",
    # 32 them
    "bệnh Parkinson", "sa sút trí tuệ", "suy tim", "bệnh mạch vành",
    "nhồi máu cơ tim cũ", "rung nhĩ", "phì đại tuyến tiền liệt",
    "ung thư tiền liệt tuyến", "bệnh phổi tắc nghẽn mạn tính",
    "gãy cổ xương đùi", "thoái hóa hoàng điểm", "điếc do tuổi già",
    "hẹp động mạch cảnh", "xơ gan", "ung thư thực quản",
    "đái tháo đường biến chứng thận", "gù cột sống", "hẹp ống sống thắt lưng",
    "bệnh thận do tăng huyết áp", "run do tuổi già", "đau sau zona",
    "thiếu máu não", "hẹp van động mạch chủ", "phình động mạch chủ bụng",
    "huyết khối tĩnh mạch sâu", "tắc động mạch chi dưới",
    "thoái hóa khớp bàn tay", "ung thư da", "chóng mặt tư thế lành tính",
    "ung thư bàng quang", "u não lành tính", "viêm phổi tái phát",
]

# Benh CHI CO O MOT GIOI. "Bo toi bi u xo tu cung" thi bac si doc qua la thay
# sai ngay — dung loai hop ly ma `_benh_hop_tuoi` duoc viet ra de giu. Bo sinh
# loc theo gioi cua nguoi mang benh truoc khi rut.
CHI_NU = frozenset({
    "hội chứng buồng trứng đa nang", "đái tháo đường thai kỳ", "ung thư vú",
    "ung thư cổ tử cung", "u xơ tử cung", "lạc nội mạc tử cung",
    "u nang buồng trứng",
})
CHI_NAM = frozenset({
    "giãn tĩnh mạch thừng tinh", "phì đại tuyến tiền liệt",
    "ung thư tiền liệt tuyến",
})
# Vai nguoi nha theo gioi. Lay tu cac vai THAT dung trong bo sinh:
# `NGUOI_NHA[..][3]` va danh sach trong `_nguoi_nha_khac`.
VAI_NU = frozenset({"mẹ", "bà ngoại", "bà nội", "vợ", "con gái", "chị gái"})
VAI_NAM = frozenset({"bố", "ông nội", "ông ngoại", "chồng", "con trai", "anh trai"})
NGUOI_LON_TUOI = ("bà ngoại", "bà nội", "ông nội", "ông ngoại")

THUOC = [
    "paracetamol", "efferalgan", "hapacol", "panadol", "oresol", "amoxicillin",
    "augmentin", "berberin", "smecta", "salbutamol", "omeprazole", "amlodipin",
    "metformin", "cetirizine", "men tiêu hóa", "vitamin C", "thuốc ho bổ phế",
]
# Thuoc CHO TRE EM — tach 11/09/2026: ban minh hoa co "chau no co uong amlodipin"
# (thuoc huyet ap) vi benh nhi rut chung bang thuoc voi nguoi lon.
THUOC_TRE_EM = ["paracetamol", "efferalgan", "hapacol", "oresol", "amoxicillin",
                "augmentin", "smecta", "salbutamol", "cetirizine", "men tiêu hóa",
                "vitamin C", "thuốc ho bổ phế"]

# Thuoc KEM CHI TIET — them 15/09/2026 cho truong `thuoc` cua luoc do.
#
#     ten -> (duong dung, (cac lieu), (cac cach dung theo so lan))
#
# ⚠️ CHUA CO NGUOI CO CHUYEN MON DUYET. Lieu lay theo ham luong vien/goi thong dung
# ban o Viet Nam, KHONG phai lieu khuyen cao cho mot benh nhan cu the. Day la du lieu
# mo phong de do loi GHI CHEP (ghi dung dieu da noi), khong de do loi KE DON.
#
# Thuoc co HAI lieu tro len moi dung duoc cho tinh huong dinh chinh lieu
# ("5 mg, a nham, 10 mg"). Moi duong dung trong `phat_bieu.DUONG_DUNG` phai co it
# nhat mot thuoc o day — test canh.
#
# CACH DUNG KHONG DUOC CHUA TEN TRIEU CHUNG ("khi sot", "khi kho tho"). Tang loi dan
# thuong cua bo sinh doi ten trieu chung trong LOI THOAI ("sot" -> "nong ham hap")
# nhung khong doi trong dap an, nen chi tiet "khi sot" cua dap an khong con nguyen van
# trong hoi thoai. Da vap ngay 15/09/2026 (hv_0378, seed 7); dung "khi cần".
THUOC_CHI_TIET_NGUOI_LON = {
    "paracetamol": ("uống", ("500 mg",), ("ngày ba lần", "khi cần")),
    "panadol": ("uống", ("500 mg",), ("ngày ba lần", "khi cần")),
    "amoxicillin": ("uống", ("250 mg", "500 mg"), ("ngày hai lần", "ngày ba lần")),
    "augmentin": ("uống", ("625 mg", "1 g"), ("ngày hai lần",)),
    "omeprazole": ("uống", ("20 mg", "40 mg"), ("ngày một lần trước ăn sáng",)),
    "amlodipin": ("uống", ("5 mg", "10 mg"), ("ngày một lần buổi sáng",)),
    "metformin": ("uống", ("500 mg", "850 mg"), ("ngày hai lần sau ăn",)),
    "cetirizine": ("uống", ("10 mg",), ("ngày một lần buổi tối",)),
    "salbutamol": ("xịt", ("hai nhát",), ("khi cần",)),
    "kem bôi fucidin": ("bôi", ("một lớp mỏng",), ("ngày hai lần",)),
    "thuốc nhỏ mắt natri clorid": ("nhỏ", ("hai giọt",), ("ngày ba lần",)),
}
THUOC_CHI_TIET_TRE_EM = {
    "paracetamol": ("uống", ("nửa gói", "một gói"), ("khi cần", "ngày ba lần")),
    "amoxicillin": ("uống", ("5 ml", "7 ml"), ("ngày hai lần",)),
    "oresol": ("uống", ("một gói",), ("ngày ba lần",)),
    "smecta": ("uống", ("một gói",), ("ngày hai lần",)),
    "cetirizine": ("uống", ("2,5 ml", "5 ml"), ("ngày một lần buổi tối",)),
    "salbutamol": ("xịt", ("hai nhát",), ("khi cần",)),
    "thuốc nhỏ mắt natri clorid": ("nhỏ", ("một giọt",), ("ngày ba lần",)),
}
# Moc bat dau dung thuoc, noi trong cau "dung duoc {moc}".
BAT_DAU_THUOC = ("hai tuần nay", "một tháng nay", "ba tháng nay", "mấy hôm nay")

THUOC_DI_UNG = [
    "penicillin", "amoxicillin", "sulfamid", "aspirin", "cephalexin",
    "thuốc cản quang", "kháng sinh nhóm quinolon",
]

# Chat di ung cua NGUOI NHA — tach rieng khoi THUOC_DI_UNG (cua benh nhan).
#
# Tach vi hai bang phuc vu hai muc dich. THUOC_DI_UNG dung cho di ung cua benh
# nhan va KHONG duoc chia theo tap: no la tien su cua benh nhan, khong phai noi
# dung tang 4. Bang nay thi CO chia theo tap, de di ung cua nguoi nha tren
# dev/test la chat chua thay o train. Dung chung mot bang thi phai chon mot
# trong hai, va ca hai lua chon deu sai.
#
# Hien thanh "di ung <chat>". Khong co "thoi tiet": "di ung thoi tiet" da la mot
# benh trong TIEN_SU_GIA_DINH_MOI_TUOI.
DI_UNG_NGUOI_NHA = [
    # thuoc (22)
    "penicillin", "amoxicillin", "cephalexin", "ceftriaxone", "sulfamid",
    "aspirin", "ibuprofen", "diclofenac", "kháng sinh nhóm quinolon",
    "kháng sinh nhóm macrolid", "thuốc cản quang", "iốt", "codein", "morphin",
    "lidocain", "cotrimoxazol", "metronidazol", "allopurinol", "carbamazepin",
    "phenytoin", "tetracyclin", "vancomycin",
    # thuc an (14)
    "hải sản", "tôm", "cua", "cá biển", "đạm sữa bò", "trứng", "đậu phộng",
    "đậu nành", "bột mì", "vừng", "hạt điều", "dâu tây", "xoài", "nhộng",
    # moi truong (14)
    "phấn hoa", "bụi nhà", "mạt nhà", "lông mèo", "lông chó", "nấm mốc",
    "côn trùng đốt", "nọc ong", "cao su", "nickel", "mỹ phẩm",
    "thuốc nhuộm tóc", "nước hoa", "bột giặt",
]

NGHE_NGHIEP = [
    "làm ruộng", "công nhân may", "lái xe", "buôn bán ngoài chợ", "giáo viên",
    "thợ xây", "nhân viên văn phòng", "làm nghề tự do", "về hưu", "nội trợ",
]

# ---------------------------------------------------------------- moc thoi gian

# Chia theo dien tien cua benh. Ban dau dung chung mot ro nen ra nhung ca kieu
# "sot nua thang" roi chan doan "cum mua" — mot bac si doc qua la thay sai.
MOC_CAP = ["hai hôm", "ba hôm", "bốn hôm", "gần một tuần", "mấy hôm nay",
           "từ hôm kia", "năm hôm", "hơn một tuần"]
MOC_MAN = ["khoảng một tháng", "hai tháng nay", "nửa năm rồi", "hơn một năm",
           "mấy tháng nay", "từ năm ngoái", "vài năm rồi"]
MOC_KEO_DAI = MOC_CAP + MOC_MAN
MOC_THOI_DIEM = ["hôm qua", "hôm kia", "tối qua", "sáng nay", "đêm qua",
                 "chiều hôm qua", "từ tuần trước", "từ hôm chủ nhật"]

# ------------------------------------------------------------- cach hoi/dap

# Trao doi XA GIAO: co that trong phong kham, va KHONG mang thong tin lam sang
# nao. Dung de lam LOANG tin hieu do dai — xem `_xa_giao` trong bo sinh.
#
# BA DIEU KIEN cho moi cap, va ca ba deu da loai bot mot vai cau nghe tu nhien
# hon:
#   1. Khong co trieu chung, thuoc, moc thoi gian benh — neu co, dap an phai ghi
#      them mot menh de, va cap nay thoi la "trung tinh".
#   2. Khong noi VE AI ("ai dua di kham", "nha co ai bi khong") — moi cau nhu vay
#      deu cham vao truc chu the, dung truc du an dang do.
#   3. Bac si KHONG tu xung "chau": trong ca nhi khoa "chau" la cach goi benh
#      nhan, va mot tu tu xung lan cho nhu the tung la nguyen nhan chan oan.
XA_GIAO = [
    ("Mời {goi} ngồi ghế này ạ.", "Dạ, cảm ơn bác sĩ ạ."),
    ("{goi_hoa} đợi lâu chưa ạ?", "Dạ cũng vừa thôi ạ."),
    ("Nhà mình ở gần đây không ạ?", "Dạ cũng gần đây thôi ạ."),
    ("Phiền {goi} đưa thẻ bảo hiểm ạ.", "Dạ, đây ạ."),
    ("Hôm nay phòng khám hơi đông, {goi} thông cảm nhé.", "Dạ không sao đâu ạ."),
]

MO_DAU = [
    "Chào {goi}, hôm nay {goi} đến khám vì sao{tt}?",
    "{goi} thấy trong người thế nào{tt}?",
    "Mời {goi} ngồi. {goi_hoa} bị làm sao{tt}?",
    "Hôm nay {goi} khám gì{tt}?",
    "{goi_hoa} kể tôi nghe xem dạo này thế nào{tt}.",
]
# Bac si goi benh nhan bang tu CUA BAC SI ({goi_bs}), khong muon cach goi cua
# nguoi nha. Ban dau dung chung mot bien nen ra cau "Chị thấy bé nhà em có biểu
# hiện gì?" — "bé nhà em" la loi nguoi me tu noi ve con minh, bac si khong noi
# nhu vay.
MO_DAU_NGUOI_NHA = [
    "Chào {goi_nn}, hôm nay {goi_nn} đưa {goi_bs} đi khám vì sao{tt}?",
    "{goi_nn_hoa} thấy {goi_bs} có biểu hiện gì{tt}?",
    "Mời {goi_nn} ngồi. {goi_bs_hoa} nhà mình bị làm sao{tt}?",
    "Hôm nay {goi_bs} sao rồi{tt}?",
    "{goi_nn_hoa} kể tôi nghe {goi_bs} bị thế nào{tt}.",
]
HOI_THOI_GIAN = [
    "Bị bao lâu rồi{tt}?", "Tình trạng này có từ khi nào{tt}?",
    "Mấy hôm rồi{tt}?", "Bắt đầu từ bao giờ{tt}?",
]
HOI_THEM = [
    "Ngoài ra còn thấy gì nữa không{tt}?", "Còn triệu chứng gì khác không{tt}?",
    "Có kèm theo biểu hiện nào nữa không{tt}?", "Còn gì bất thường nữa không{tt}?",
]
HOI_TIEN_SU = [
    "Trước giờ có bệnh gì không{tt}?", "Có đang điều trị bệnh gì không{tt}?",
    "Tiền sử có gì đáng chú ý không{tt}?",
]
HOI_GIA_DINH = [
    "Trong nhà có ai mắc bệnh gì không{tt}?",
    "Gia đình có ai bị bệnh gì đáng chú ý không{tt}?",
    "Bố mẹ anh chị em có ai bệnh gì không{tt}?",
]
HOI_DI_UNG = [
    "Có dị ứng thuốc gì không{tt}?", "Trước giờ dùng thuốc có bị dị ứng lần nào chưa{tt}?",
    "Có tiền sử dị ứng gì không{tt}?",
]
HOI_THUOC = [
    "Đang uống thuốc gì không{tt}?", "Đã dùng thuốc gì chưa{tt}?",
    "Có tự mua thuốc uống không{tt}?",
]
# KHONG de tieu tu o cuoi mau — bo sinh tu them theo vung. De san "nhe" o day
# thi ra "Toi kham qua mot chut nhe nhe."
CHUYEN_KHAM = [
    "Rồi, để tôi khám cho {goi}",
    "Được rồi, {goi} nằm lên bàn khám giúp tôi",
    "Tôi khám qua một chút",
    "{goi_hoa} ngồi yên để tôi nghe phổi",
]

# Loi dan khi ra ve, dung cho cau gia dinh. Phai KHONG phu thuoc trieu chung —
# ban dau boc ngau nhien "cho uong ha sot" nen ra "Neu mai chau con dau tai thi
# cho uong ha sot", tuc loi khuyen khong khop trieu chung.
DAN_DO = ["quay lại đây", "gọi điện cho tôi", "đưa đi khám lại",
          "cho uống nốt thuốc rồi tái khám"]
