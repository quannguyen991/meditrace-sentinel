# -*- coding: utf-8 -*-
"""Hoi thoai noi bang LOI DAN THUONG, dap an giu THUAT NGU LAM SANG.

VI SAO CAN — do duoc ngay 10/09/2026, va day la cho hong nang nhat cua bo du
lieu. Ty le tu noi dung cua menh de dap an xuat hien NGUYEN VAN trong hoi thoai:

    bo 3.000   trung binh 99,7%   menh de phu 100%: 99,1%
    bo 5.000   trung binh 99,6%   menh de phu 100%: 98,5%

Nghia la nhiem vu ma bo du lieu dat ra chi la: TIM DUNG DOAN VA XEP DUNG MUC.
Khong chuan hoa, khong suy luan, khong dien dat lai. Mot doi chung regex cat
doan roi dan vao DA HON ca duong ong day du tren moi tang (Task 42).

Va no giai thich ba thu truoc do tuong roi nhau:

    eval_loss dung o 10^-4            phep chieu gan nhu tien dinh
    doi chung regex hon duong ong     sao chep la chien luoc toi uu
    duong ong khong cho thay loi ich  khong co gi de duong ong dong gop

Cho nay LON HON nhan dinh cu "du lieu qua deu". Du lieu KHONG deu ve be mat —
3.000/3.000 khung cau khac nhau. No deu o cho **phep chieu tu hoi thoai sang
ban nhap gan nhu la phep dong nhat**.

Tep nay pha phep dong nhat do: nguoi benh noi "con be cu non trong suot", benh
an ghi "non nhieu lan".

QUAN HE VOI `phuong_ngu`. Cung co che, khac moi quan tam:

    phuong_ngu      bien the VUNG      "sot"  -> "nong ham hap"
    loi_dan_thuong  bien the NGU VUC   "non nhieu lan" -> "cu non trong suot"

Tach hai tep vi hai bang phai do rieng: mot ca co the co phuong ngu ma khong co
loi dan thuong, va nguoc lai. Gop vao mot bang thi khong con biet cai nao dang
lam mo hinh sai.

HAI RANG BUOC, giong `phuong_ngu`, va ca hai deu co kiem thu:

  1. CHI thay trong loi benh nhan va nguoi nha. Bac si duoc dao tao noi thuat
     ngu; doi loi bac si sang loi dan thuong la lam mat mot dau hieu that.
  2. DAP AN GIU THUAT NGU CHUAN. Hoi thoai viet "cu non trong suot", dap an van
     ghi "non nhieu lan".

Rang buoc hai CHINH LA phep thu. Neu dap an cung doi sang loi dan thuong thi
khong con gi de do — mo hinh chi viec chep lai nguyen van, va ta tro lai dung
cho dang dung.
"""
import re

# (thuat ngu lam sang, cac cach noi dan thuong). Chieu DOI LA: bang nay dung de
# doi DAP AN -> HOI THOAI, nguoc voi `phuong_ngu`.
#
# BANG NAY LAY TU NGU LIEU, KHONG TU PHONG DOAN. Ban dau toi viet 18 cum theo
# tri nho ("non nhieu lan", "tieu chay", "kho tho"...) roi do do phu: **9/18 cum
# KHONG XUAT HIEN LAN NAO** trong 681 ca. Bo sinh dung chu khac han, va mot bang
# khong khop ngu lieu thi khong thay duoc gi — no khong bao loi, no chi khong
# chay.
#
# Bang duoi day dung cac cum co tan so cao nhat trong `dap_an`, va chi giu cap
# ma mot nguoi Viet khong hoc y THAT SU noi nhu the. Khong bia cum cho du dai
# bang: mot cap sai nghia lam ban nhap tham chieu sai theo, va loi do khong co
# cach nao phat hien tu bang so.
#
# Do phu sau khi lay tu ngu lieu: 630/681 ca (92,5%), ca 20/20 cum deu bat.
#
# LOI THU HAI, sua 11/09/2026: 20 cum dau tien duoc chon theo tan so do tren
# TAP PHAT TRIEN. Hai hau qua, va hau qua thu hai nang:
#
#   1. Bang phu 8 khuon cua tap dev rat tot va 45 khuon cua tap train kem. Do
#      duoc tren the he 3: ty le menh de sao chep nguyen van la 83,3% o dev
#      nhung 93,8% o train. Lech 10 diem, va lech THEO HUONG lam tap do KHO HON
#      tap huan luyen — vi mot ly do khong lien quan gi den kha nang khai quat.
#
#   2. Chon tu vung theo tan so cua tap DO la mot dang nhin vao du lieu danh
#      gia. No nhe, nhung no cung huong voi moi cach lam hong phep do khac.
#
# Bang gio mo rong theo tu vung cua TAP TRAIN. Phep thu
# `test_do_phu_KHONG_lech_giua_train_va_dev` canh do lech do.
CHENH_PHU_TOI_DA = 0.04
# Cum DA BO ngay 11/09/2026 vi KHONG thuoc tu vung cua tap train — kiem bang
# `test_MOI_khoa_thuoc_TU_VUNG_TRAIN`. Ca tam deu nam trong 20 cum DAU TIEN, tuc
# nhung cum da duoc chon theo tan so cua TAP PHAT TRIEN (xem "LOI THU HAI" o
# tren). Khi bo khuon len 100 va chia lai 13/12, khuon mang chung roi vao tap
# phat trien, nen chung thanh tu vung CHI co o tap do: giu lai la de tap phat
# trien duoc "lam kho" bang chinh tu vung cua no. So ben phai: so menh de tap
# phat trien mang cum do, dem luc bo.
#
# GIA PHAI TRA, va phai bao cao: bo tam cum nay thi tap phat trien DE CHEP HON
# tap train — xem `test_do_phu_KHONG_lech_giua_train_va_dev`.
BO_VI_KHONG_THUOC_TRAIN = {
    "đau thượng vị": 139,
    "đau quặn vùng thắt lưng": 122,
    "đi ngoài khó": 106,
    "rụng tóc": 28,
    "đau lan xuống bẹn": 24,
    "bụng chướng": 19,
    "ngứa tăng về đêm": 17,
    "gãi trầy da": 17,
    # Bo 12/09/2026. Khuon "viem da co dia" mang cum nay nam o tap PHAT TRIEN:
    # 77 menh de o do, va DUNG MOT o tap train — cai mot do khong phai tu vung
    # train that, no la mot lan ghep chuoi tinh co. Mot mau duy nhat du de
    # `_khoa_trong` doc ra "co trong train", nen rang buoc chi lo ra khi dem lai.
    "ngứa nhiều": 77,
}

DAN_THUONG = {
    # --- cum ky thuat that: nguoi dan gan nhu khong bao gio noi the
    "đau bụng quanh rốn": ["đau quanh chỗ rốn", "đau ở giữa bụng"],
    "da xanh": ["da tái đi", "trông nhợt nhạt", "mặt xanh xao"],
    "buồn nôn": ["nôn nao", "lợm giọng", "muốn nôn"],
    # --- cum vua: co cach noi dan thuong ro rang
    "chán ăn": ["không chịu ăn gì", "bỏ bữa suốt", "ăn uống kém đi"],
    "mệt mỏi": ["người rã rời", "không còn sức gì", "lừ đừ cả ngày"],
    "quấy khóc": ["khóc suốt đêm", "cứ quấy không yên"],
    "ngủ không yên": ["ngủ chập chờn", "đêm cứ trở mình"],
    "sụt cân": ["gầy đi nhiều", "xuống mấy cân"],
    "mất ngủ": ["không ngủ được", "trằn trọc cả đêm"],
    "khó tập trung": ["không tập trung được", "đầu cứ lơ mơ"],
    "chảy mũi": ["chảy nước mũi", "mũi thò lò"],
    # --- mo rong 11/09/2026 theo tu vung cua TAP TRAIN, xem chu thich duoi
    "đau vùng thượng vị": ["đau vùng trên rốn", "đau chỗ dưới ức"],
    "ho có đờm": ["ho ra đờm", "ho đặc tiếng"],
    "đi ngoài phân lỏng": ["đi ngoài toàn nước", "đi lỏng suốt"],
    # "kho vao giac" da bi bo: no la CACH NOI DAN THUONG toi chon, nhung no cung
    # la mot thuat ngu CO THAT trong dap an cua bo sinh. Trung nhu vay thi pha
    # bat bien 2 — dap an chua mot cum cua bang nay, va phep thu het phan biet
    # duoc dap an voi hoi thoai. Test `test_BAT_BIEN_2_dap_an_giu_THUAT_NGU_CHUAN`
    # bat duoc.
    "khó ngủ": ["nằm mãi không ngủ được", "trở mình cả đêm không ngủ"],
    "hồi hộp": ["tim đập thình thịch", "trong người bồn chồn"],
    "vã mồ hôi": ["mồ hôi ra đầm đìa", "ướt hết áo"],
    "sưng đau khớp ngón chân cái": ["ngón chân cái sưng đau",
                                    "ngón chân cái đau không đi được"],
    "sưng góc hàm": ["mang tai sưng lên", "sưng hai bên hàm"],
    "nổi mẩn": ["nổi lên từng đám", "mẩn lên khắp người"],
    "đỏ bờ mi": ["mí mắt đỏ", "viền mắt đỏ lên"],
    "ngứa mắt": ["mắt ngứa cứ muốn cọ", "ngứa trong mắt"],
    "khát nước nhiều": ["uống nước suốt không đỡ", "khát liên tục"],
    "chậm mọc răng": ["lâu rồi chưa thấy mọc răng", "răng mọc muộn"],
    "đỏ da": ["da đỏ lên", "đỏ ửng cả vùng"],
    "đau nửa đầu": ["đau một bên đầu", "nhức nửa bên đầu"],
    "đau họng": ["rát cổ", "cổ đau khi ăn"],
    # --- mo rong LAN HAI, 11/09/2026, khi bo khuon len 100. 40 khuon moi lam
    # ty le menh de sao chep nguyen van cua train tang 88,3% -> 90,6% (rieng
    # khuon moi 94,5%), va ty le ca train co loi dan thuong tut 65,7% -> 51,7%
    # — vi bang khong co mot tu nao cua chung.
    #
    # 29 cum duoi day LAY TU TAP TRAIN, moi cum >= 96 lan trong loi benh nhan /
    # nguoi nha. Da kiem tren ca 5.000 ca: khong cach noi nao trung noi dung dap
    # an, khong cach noi nao chua mot khoa khac, va khoa khong phai noi dung
    # nguoi nha. "nghe kem" bi LOAI vi la mot noi dung trong be tien su gia dinh:
    # be do chia theo tap, nen doi no chi lam lech tang 4 giua cac tap.
    "đau đầu": ["nhức đầu", "nặng đầu"],
    "đau tai": ["nhức trong tai", "tai nhức buốt"],
    "ù tai": ["tai kêu o o", "trong tai cứ o o"],
    "cộm mắt": ["mắt như có cát", "mắt vướng như có bụi"],
    "đau gáy": ["nhức sau gáy", "mỏi nhừ sau cổ"],
    "nôn nhiều": ["nôn thốc nôn tháo", "nôn hết cả ra"],
    "ngứa về đêm": ["tối đến là ngứa", "cứ tối là ngứa"],
    "sưng đau khớp bàn tay": ["mấy đốt ngón tay sưng nhức",
                              "khớp tay sưng tấy lên"],
    "đau lưng lan xuống chân": ["đau từ thắt lưng chạy xuống chân",
                                "buốt từ lưng xuống tận chân"],
    "đi ngoài ra máu": ["đi cầu có máu", "đi vệ sinh thấy máu"],
    "nổi mụn nước": ["mọc mấy nốt phỏng", "nổi nốt phỏng nước"],
    "ngứa âm hộ": ["ngứa vùng kín", "ngứa ở chỗ kín"],
    "khát nước": ["lúc nào cũng thèm uống", "uống bao nhiêu cũng không đã khát"],
    "đau cổ chân": ["nhức ở mắt cá chân", "nhức quanh cổ chân"],
    "đỏ da vùng quấn tã": ["chỗ đóng bỉm đỏ lên", "mông đỏ ửng chỗ quấn bỉm"],
    "tiểu đêm": ["đêm dậy đi vệ sinh mấy lần", "đêm phải dậy đi giải"],
    "đau ngực khi gắng sức": ["làm nặng là tức ngực",
                              "leo cầu thang là thấy nặng ngực"],
    "hắt hơi": ["hắt xì", "hay hắt xì"],
    "nôn trớ sau bú": ["bú xong là trớ ra", "ăn sữa xong lại ọc ra"],
    "kinh không đều": ["tháng có tháng không", "đến tháng lúc sớm lúc muộn"],
    "đau vùng cổ trước": ["đau phía trước cổ", "đau quanh chỗ yết hầu"],
    "sưng mi mắt": ["mí mắt sưng húp", "mắt sưng mọng lên"],
    "nhìn xa mờ": ["nhìn xa không rõ", "nhìn xa bị nhòe"],
    "chảy nước mắt": ["mắt cứ ứa nước", "mắt lúc nào cũng ướt"],
    "tiểu dầm ban đêm": ["đêm vẫn đái dầm", "ngủ vẫn tè dầm"],
    "nổi mụn ở mặt": ["mặt lên mụn", "mặt mọc mụn"],
    "đau rát một bên": ["nóng rát một bên", "rát như bỏng một bên"],
    "tê ngón tay": ["tê bì đầu ngón", "đầu ngón cứ rần rần"],
    "đau lưng": ["nhức lưng", "ê ẩm cả lưng"],
}

# Cum KHONG doi, kem ly do. Ghi ra thay vi xoa im lang, de nguoi doc sau biet
# la da can nhac chu khong phai bo sot.
DA_BO = {
    "sốt": "`phuong_ngu` da phu cum nay (\"nong ham hap\"); doi o ca hai tep "
           "thi khong con biet tang nao lam mo hinh sai",
    "dị ứng thuốc": "nguoi dan cung noi \"di ung thuoc\" — khong co cach noi khac",
    "sốt phát ban": "ten CHAN DOAN, do bac si noi, khong phai loi benh nhan",
    "thiếu máu thiếu sắt": "ten chan doan, nhu tren",
    "co giật": "cach noi dan thuong (\"giat minh\", \"lam kinh\") lech nghia y hoc",
    "vàng da": "\"da vang\" va \"vang da\" khac nhau ve cu phap, doi de sinh cau sai",
}


# RANH GIOI TU KHONG PHAI RANH GIOI TU GHEP — cung ho loi da mac o `phuong_ngu`.
#
# `(?![\wÀ-ỹ])` chan duoc "da xanh" nam trong "da xanhxao", nhung KHONG chan
# duoc "da xanh" nam trong "da xanh xao": giua chung la dau cach nen lookahead
# cho qua. Ket qua: "trong da xanh xao" -> "trong da tai di xao", khong phai
# tieng Viet.
#
# Test `test_khong_khop_tu_nam_TRONG_tu_khac` bat duoc.
#
# Bang duoi day lay tu NGU LIEU: quet tu dung sau moi cum tren 681 ca. Phan lon
# la moc thoi gian ("hai", "khoang", "tu") va "nua" — deu an toan. Chi hai cho
# that su rui ro.
CHAN_SAU = {
    # ("bung chuong": {"nhe"} da bo 11/09/2026 cung khoa cua no — xem
    # BO_VI_KHONG_THUOC_TRAIN. De lai thi la mot dong chan cho khoa khong ton tai.)
    "da xanh": {"xao"},         # "da xanh xao" la mot tu ghep
    # Them 11/09/2026, cung cach: quet tu dung sau moi khoa moi tren tap train.
    # Ca ba la cho mot khoa NGAN nam o dau mot cum DAI hon cung la khoa (hoac
    # cung la mot trieu chung): doi khoa ngan se cat doi cum dai.
    "đau lưng": {"lan"},        # 58 lan: "dau lung lan xuong chan" la khoa rieng
    "khát nước": {"nhiều"},     # "khat nuoc nhieu" la khoa rieng
    "nổi mụn nước": {"nhỏ"},    # 24 lan: "noi mun nuoc nho" la mot trieu chung
}


def _mau(cum):
    return re.compile(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])", re.I)


def _bi_chan(cum, cau, ket):
    """Tu ngay sau `cum` co nam trong bang chan khong."""
    sau = cau[ket:].lstrip()
    tu_sau = re.match(r"[\wÀ-ỹ]+", sau)
    if not tu_sau:
        return False
    return tu_sau.group(0).lower() in CHAN_SAU.get(cum, ())


def doi_sang_dan_thuong(cau, rng, ty_le=0.85):
    """-> (cau_moi, [(thuat_ngu, cach_noi)]).

    `ty_le`: xac suat doi MOI cum tim thay. Dat 0,85 chu khong 1,0: hoi thoai
    that tron ca hai ngu vuc — nguoi benh co hoc van cung noi "buon non" — va
    doi het 100% thi phep thu thanh "dich tu dien mot chieu".

    Tang tu 0,55 len 0,85 sau khi do: o 0,55 thi ty le menh de sao chep nguyen
    van chi tut tu 99,1% xuong 93,8%, chua du.

    Doi cum DAI truoc: "sot cao" phai duoc xet truoc "sot", neu khong thi doi
    "sot" xong se con lai "nong ham hap cao" — dung ho loi pha tu ghep da mac o
    `phuong_ngu`.
    """
    da_doi = []
    for thuat_ngu in sorted(DAN_THUONG, key=len, reverse=True):
        m = _mau(thuat_ngu).search(cau)
        if not m or _bi_chan(thuat_ngu, cau, m.end()):
            continue
        if rng.random() >= ty_le:
            continue
        cach_noi = rng.choice(DAN_THUONG[thuat_ngu])
        cau = cau[:m.start()] + cach_noi + cau[m.end():]
        da_doi.append((thuat_ngu, cach_noi))
    return cau, da_doi


def phu_duoc(van_ban):
    """-> cac thuat ngu trong bang CO mat trong `van_ban`.

    Dung de do do phu cua bang: bang co 18 cum, nhung neu ngu lieu chi dung 3
    trong so do thi tang nay gan nhu khong chay. Phai do chu khong duoc gia
    dinh.
    """
    return [t for t in DAN_THUONG if _mau(t).search(van_ban or "")]
