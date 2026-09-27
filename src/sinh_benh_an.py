# -*- coding: utf-8 -*-
"""Sinh benh an TU BANG PHAT BIEU bang luat, khong bang mo hinh.

Day la cho du an chan loi quy gan. Neu de mo hinh tu do viet lai ca tap phat
bieu thanh van xuoi, no se gop hai phat bieu KHAC CHU THE thanh mot cau —
va do dung la loi ma du an dang muon chan. Nen buoc nay la ma, khong phai
mo hinh: moi phat bieu di vao dung mot muc, theo bang tra co dinh.

Hai luat khong duoc pha:

  1. Phat bieu co chu the KHONG PHAI benh nhan thi KHONG duoc vao cac muc noi
     ve benh nhan. Di ung cua me thuoc TIEN SU GIA DINH, khong thuoc DI UNG.

  2. "chua ghi nhan" phai ra chu "chua ghi nhan". Bien no thanh "khong co" la
     bien mot cho TRONG thanh mot khang dinh AM — hai chuyen khac han nhau
     ve mat lam sang.

Phat bieu khong du dieu kien (bi thay the, gia dinh, ke hoach, thieu bang
chung) khong bi vut di — no xuong muc CAN XAC NHAN, kem ly do.
"""
import re

from src import phat_bieu

MUC_BENH_NHAN = "__benh_nhan__"      # danh dau muc chi danh cho benh nhan

# Ten muc phai lay tu VON TU CUA CHINH BO DU LIEU, khong duoc tu dat.
# Ban dau toi dat la "TIEN SU GIA DINH". Ten do xuat hien 0 lan trong 35 ban
# tham chieu cua tap phat trien, nen 22 lan sinh ra deu la duong tinh gia,
# va 8 muc that bi tinh la bo sot. Chon lai theo tan suat trong TAP TRAIN
# (khong nhin tap phat trien): 376 lan "VA XA HOI" so voi 178 lan khong.
MUC_NGUOI_KHAC = "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"

# Nhan vien y te KHONG phai chu the lam sang. "Bac si: kho khai thac them
# thong tin benh su" khong phai tien su cua bac si. Ban dau moi phat bieu co
# chu the khac benh nhan deu bi day vao muc tien su gia dinh, ke ca 16 phat
# bieu co chu the la bac si — vua sai ve y nghia vua sinh ra muc thua.
# MOT dinh nghia duy nhat, dat o `phat_bieu` — xem chu thich o do. Truoc
# 10/09/2026 bang nay chi co o tep nay, con `tu_json` va `sua_cuc_bo`
# khong biet gi, gia la 104 cau bac si bi doi sang muc gia dinh.
NHAN_VIEN_Y_TE = phat_bieu.VAI_NHAN_VIEN

# Chuoi KHONG dung lam ten nguoi trong ban nhap: chung la cach goi benh nhan,
# nen dat chung truoc mot menh de o muc tien su gia dinh se noi sai nguoi.
TEN_KHONG_DAT_TEN = frozenset(phat_bieu.TEN_BENH_NHAN) | {""}

# Thu tu in ra. Theo thu tu benh an thong thuong, khong theo thu tu phat bieu.
THU_TU_MUC = [
    "LÝ DO KHÁM BỆNH",
    "BỆNH SỬ HIỆN TẠI",
    # Doi ten 11/09/2026: truoc day tep nay goi muc nay la
    # "KHAM HE THONG CAC CO QUAN" trong khi ban nhap tham chieu goi la
    # "KHAM LAM SANG". Hai khau dung hai bo ten muc khac nhau, nen duong ong
    # khong the sinh ra ten muc ma phep cham doi chieu: tham chieu co no o 60/60
    # ca, ban nhap cua nhanh B co 0. Hai cho khac trong du an
    # (`sinh_hoi_thoai_viet.MUC` va `bo_nguoi_that.MUC_HOP_LE`) deu dung
    # "KHAM LAM SANG", nen tep nay la cho lech.
    "KHÁM LÂM SÀNG",
    "SINH HIỆU",
    "TIỀN SỬ BỆNH",
    "TIỀN SỬ PHẪU THUẬT",
    "DỊ ỨNG",
    "THUỐC ĐANG DÙNG",
    "TIÊM CHỦNG",
    "TIỀN SỬ XÃ HỘI",
    MUC_NGUOI_KHAC,
    "CHẨN ĐOÁN",
    "KẾ HOẠCH ĐIỀU TRỊ",
    "CẦN XÁC NHẬN",
]

# Bang tra: (bieu thuc, muc). Xet theo thu tu, cai dau tien khop thi lay.
# Chi ap dung khi chu the LA benh nhan — xem `_muc_cho`.
BANG_TRA = [
    # `dị ứng` phai co CAI GI DUNG SAU no.
    #
    # Ban dau la `dị ứng` tran. "Viem mui di ung" va "Viem ket mac di ung" la
    # TEN BENH — tien su benh — nhung chung khop va bi day sang muc DI UNG. Da
    # thay dung the tren ban nhap cua nhanh B: muc TIEN SU BENH co 28/60 ca trong
    # ban tham chieu va 0 trong ban nhap.
    #
    # Trong ten benh, "di ung" dung o CUOI ("viem mui di ung"); trong mot loi ke
    # di ung that, no di kem chat gay di ung ("di ung penicillin", "di ung thuoc
    # can quang"). Nen doi hoi co tu dung sau.
    (r"dị ứng\s+\S|mẫn cảm|phát ban khi (uống|dùng)", "DỊ ỨNG"),
    (r"tiêm (chủng|phòng)|vắc[- ]?xin|vaccine", "TIÊM CHỦNG"),
    (r"mổ|phẫu thuật|cắt (ruột thừa|amidan|túi mật)", "TIỀN SỬ PHẪU THUẬT"),
    (r"đang (uống|dùng|điều trị bằng)|thuốc (đang|hiện)", "THUỐC ĐANG DÙNG"),
    # Bon muc duoi day them sau khi do: ban tham chieu co chung ma bo sinh
    # khong bao gio tao ra, nen moi lan xuat hien deu bi tinh la bo sot.
    (r"hút thuốc|thuốc lá|rượu|bia|nghề|làm việc|sống (một mình|cùng)|"
     r"học lớp|đi học|nhà trẻ", "TIỀN SỬ XÃ HỘI"),
    # `mạch`, `huyết áp` PHAI kem so. Tran thi "tang huyet ap" (mot BENH) roi vao
    # SINH HIEU: do tren dap an TAP TRAIN 11/09/2026, 80 phat bieu tien su benh
    # bi day nham, trong khi dap an khong co phat bieu nao o SINH HIEU.
    (r"nhiệt độ|mạch \d|huyết áp \d|nhịp thở|spo2|cân nặng \d|\d+ *°|\d+ *độ|"
     r"°f|°c", "SINH HIỆU"),
    (r"chẩn đoán|nghĩ nhiều đến|theo dõi (viêm|sốt|bệnh)", "CHẨN ĐOÁN"),
]

# Dau hieu DUNG THUOC trong TRICH DAN — xet sau `BANG_TRA`, tren loi noi chu
# khong tren noi dung. Do tren dap an TAP TRAIN 11/09/2026: 1.538 phat bieu THUOC
# DANG DUNG co noi dung chi la TEN THUOC ("salbutamol", "berberin"), va bang tra
# tren noi dung chi bat duoc 343. Hoc thuoc ten thuoc cua train la lap lai bay cua
# bang ten benh (100% train, 40% tap phat trien); cai khai quat duoc la DONG TU
# dung thuoc trong cau noi: "toi co uong salbutamol". Tren train mau nay ban
# 1.588 lan: 1.538 dung muc, 50 la ke hoach — da xu ly o `tinh_huong` truoc do.
# Tru do an uong: "co uong sua" la chuyen an, khong phai thuoc.
DUNG_THUOC = re.compile(
    r"(?<!\w)(có|đang|vẫn|hay|thường|mới) (uống|dùng|xịt|bôi|nhỏ|tiêm|ngậm)"
    r"(?!\w)(?! (nước|sữa|cháo|bia|rượu|cà phê|trà)(?!\w))", re.I)

# NGON NGU KHAM: viec nguoi kham LAM hoac QUAN SAT duoc.
#
# VI SAO CAN, va vi sao bang cu khong du — do ngay 11/09/2026.
#
# Ban tham chieu co `KHAM LAM SANG` o **60/60** ca; ban nhap cua nhanh B co
# **0**. Hai ly do, ca hai deu la lo~:
#
#   1. `THU_TU_MUC` cua tep nay goi muc do la `KHAM HE THONG CAC CO QUAN`, con
#      ban tham chieu (`sinh_hoi_thoai_viet.MUC`) goi la `KHAM LAM SANG`. Hai
#      khau dung hai BO TEN MUC khac nhau, nen duong ong KHONG THE sinh ra ten
#      muc ma phep cham doi chieu. Cung voi `CHAN DOAN` (40 ca tham chieu, B co
#      0) va `TIEN SU BENH` (28 ca, B co 0).
#
#   2. Bang cu khop tu khoa kieu `khám (thấy|phổi|...)`, nhung cau kham that
#      khong chua tu "kham": "Bụng mềm, ấn đau nhẹ quanh rốn". Nen luat gan nhu
#      khong bao gio ban, va cau kham roi xuong `BENH SU HIEN TAI`.
#
# BANG NAY CHON TU TAP TRAIN, khong tu tap do. Da thu ca mot bang TEN BENH va
# bo no: ten benh dat 100% tren train nhung chi 40,4% tren tap phat trien — no
# hoc thuoc 45 ten benh cua train. Ngon ngu kham thi khai quat duoc, vi no la
# mot ngu vuc dong: 95,5% tren train, 87,6% tren tap phat trien.
#
# Luat: co dau hieu kham -> KHAM LAM SANG; con lai (cau bac si noi, thuc te) ->
# CHAN DOAN. Do duoc 93,6% tren train va 93,4% tren tap phat trien.
# KHONG dung TEN BO PHAN don le lam dau hieu. Ban dau toi co `niêm mạc`,
# `kết mạc`, `bờ mi`, `màng nhĩ`, `amidan` trong bang, va do tren train thi
# **85 chan doan bi day sang muc kham**: "Viem ket mac cap", "Viem bo mi",
# "Viem ket mac di ung" — chan doan cung duoc goi theo TEN BO PHAN.
#
# Nen chi giu dau hieu la VIEC NGUOI KHAM LAM hoac DAU HIEU QUAN SAT DUOC. Ten
# bo phan chi duoc dung khi di kem mot dau hieu ("niêm mạc ... nhợt").
# MOI DAU HIEU O DAY DEU BAN TREN TAP TRAIN. Da kiem bang cach tach tung nhanh
# cua bieu thuc roi do rieng, va da BO sau dau hieu:
#
#   `sờ thấy`, `gan lách`, `lách to`   chi ban o TAP PHAT TRIEN — toi chon chung
#                                      tu 8 chuoi cua dev truoc khi doi sang
#                                      train, tuc la nhin vao du lieu danh gia
#   `gõ (đục|vang)`, `âm tính`,        khong ban o ca hai tap — toi tu bia
#   `mạch \d`
#
# Cung lo~i da mac voi bang tu dan thuong sang hom truoc, nen lan nay kiem truoc
# khi ghi so.
#
# BO SUNG 11/09/2026 khi bo khuon tang tu 60 len 100. Kiem lai tren TAP TRAIN MOI
# (75 khuon): 145/150 — 5 chuoi kham cua cac khuon moi khong khop. Ca 5 deu nam o
# TAP TRAIN, nen bo sung tu chung la hop le; tap phat trien dat 26/26 va KHONG
# duoc dung de chon dau hieu:
#
#   "Da vung mong do, khong co mun mu"               -> `mụn mủ`
#   "Mang hong ban gioi han ro, phu vay trang day"    -> `hồng ban`, `phủ vảy`,
#                                                        `giới hạn rõ`
#   "Ong tai ngoai sung ne, keo vanh tai dau tang"    -> `sưng nề`
#   "Bui tri noi do hai, khong chay mau luc kham"     -> `(lúc|khi) khám`
#   "Nhan mun va san viem vung tran, ma"              -> `sẩn viêm`, `nhân mụn`
NGON_NGU_KHAM = re.compile(
    r"ấn đau|nghe (có|thấy)|\bran\b|phản ứng thành bụng"
    r"|bụng (mềm|chướng)|cương tụ|dương tính|rải rác|có vảy|vảy tiết"
    r"|mụn nước|bọng nước|sẩn (phù|viêm)|phù nề|không phù|tim đều|tiếng thổi"
    r"|nhịp thở \d|huyết áp \d|mạch nhanh|thóp|gan (không )?to"
    r"|thị lực|dấu véo da|nhợt|mụn mủ|nhân mụn|hồng ban|phủ vảy|giới hạn rõ"
    r"|(lúc|khi) khám"
    r"|không (phát hiện|dấu hiệu|dấu) (bất thường|thần kinh)"
    r"|sưng (nóng|đỏ|nhẹ|tuyến|nề)|rút lõm|thể trạng|da (ẩm|khô)"
    r"|chấm mủ|tiết dịch|vết loét|điểm đau|khu trú|ban đỏ|nổi ban"
    r"|(niêm mạc|kết mạc|giác mạc|màng nhĩ|bờ mi|amidan|họng|phổi|khớp)"
    r"[^.;]{0,30}?(đỏ|sưng|nhợt|trong|phồng|to|nề|loét|dịch|mủ|ran|không)",
    re.I)


def _chuan(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _la_nhan_vien(p):
    return phat_bieu.la_vai_nhan_vien(
        _chuan(p.get("ten_chu_the") or p.get("chu_the") or ""))


def _muc_cho(p, id_benh_nhan):
    """Chon muc cho mot phat bieu. Tra ve (ten_muc, ly_do_neu_chuyen_huong)."""
    if not p.get("bang_chung"):
        return "CẦN XÁC NHẬN", "không có bằng chứng lượt thoại"
    if p.get("trang_thai", "còn hiệu lực") != "còn hiệu lực":
        return "CẦN XÁC NHẬN", f"trạng thái {p.get('trang_thai')}"

    tinh_huong = p.get("tinh_huong", "thực tế")
    hanh_vi = p.get("hanh_vi") or ""
    if tinh_huong == "giả định":
        return "CẦN XÁC NHẬN", "câu giả định, chưa xảy ra"
    if tinh_huong == "kế hoạch" or hanh_vi == "kế hoạch":
        return "KẾ HOẠCH ĐIỀU TRỊ", None

    # LUAT 1 — chu the khong phai benh nhan thi KHONG duoc vao muc cua benh nhan.
    if p.get("chu_the_id") != id_benh_nhan:
        if _la_nhan_vien(p):
            return "CẦN XÁC NHẬN", "chủ thể là nhân viên y tế, không phải người bệnh"
        return MUC_NGUOI_KHAC, None

    # HANH VI (the he 5) — LOAI LOI NOI quyet dinh nhom muc, truoc khi xet AI noi.
    #
    # Vi sao: bac si NHAC LAI benh su ("Vay la chau sot ba ngay") la cau bac si
    # noi nhung la BENH SU; luat theo nguoi noi ben duoi day no sang CHAN DOAN.
    # Chieu nguoc lai thi khong tin: nguoi nha khong kham, nen "quan sat" va
    # "nhan dinh" chi tinh khi nguoi noi la nhan vien y te — mo hinh gan nham
    # "quan sat" cho loi me ke "chau noi ban" thi van xuong benh su.
    #
    # Khong co hanh_vi (dau ra the he 4, du lieu cu) -> luat cu, khong doi gi.
    # Tren dap an tu sinh, hanh_vi va muc do cung mot bo sinh gan, nen do dung
    # 100% o day la THEO THIET KE; phep do that la tren hanh_vi mo hinh trich.
    la_nv = phat_bieu.la_vai_nhan_vien(_chuan(p.get("nguoi_noi") or ""))
    if la_nv and hanh_vi == "quan sát":
        return "KHÁM LÂM SÀNG", None
    if la_nv and hanh_vi == "nhận định":
        return "CHẨN ĐOÁN", None
    if la_nv and hanh_vi in ("trả lời", "tự kể"):
        la_nv = False               # benh su do nhan vien nhac lai

    # CAU DO BAC SI NOI la ket qua kham hoac chan doan, khong phai benh su.
    #
    # Do tren tap phat trien the he 2: trong 168 phat bieu co `nguoi_noi` la bac
    # si, dap an xep 60 vao KE HOACH DIEU TRI (da xu ly o `tinh_huong` tren), 56
    # vao KHAM LAM SANG, 40 vao CHAN DOAN. Truoc 11/09/2026 ca 96 cau kham va
    # chan doan deu roi xuong BENH SU HIEN TAI, vi bang tra khop tu khoa trong
    # NOI DUNG trong khi dau hieu that la AI NOI.
    #
    # Phai xet TRUOC `BANG_TRA`: "Viem mui di ung" la mot CHAN DOAN, nhung bang
    # tra khop `dị ứng` va day no sang muc DI UNG. Da thay dung the tren ban nhap
    # cua nhanh B.
    if la_nv:
        if NGON_NGU_KHAM.search(_chuan(p.get("noi_dung"))):
            return "KHÁM LÂM SÀNG", None
        return "CHẨN ĐOÁN", None

    noi_dung = _chuan(p.get("noi_dung")).lower()
    for bieu_thuc, muc in BANG_TRA:
        if re.search(bieu_thuc, noi_dung):
            return muc, None
    if any(DUNG_THUOC.search(_chuan(t)) for t in (p.get("trich_dan") or [])):
        return "THUỐC ĐANG DÙNG", None

    if p.get("thoi_gian_su_kien") == "quá khứ":
        return "TIỀN SỬ BỆNH", None
    return "BỆNH SỬ HIỆN TẠI", None


def _them_chi_tiet_thuoc(cum, t):
    """Chen lieu, duong dung, so lan NGAY SAU TEN THUOC; them moc bat dau hoac moc
    ngung o cuoi. Chi tiet nao da co trong cum (vi du "da ngung 2 tuan" nam san
    trong noi dung) thi khong viet lan hai.

        amlodipin                   ->  amlodipin 5 mg, uống ngày một lần buổi sáng (ba tháng nay)
        từng dùng omeprazole, đã ngừng 2 tuần
                                    ->  từng dùng omeprazole 20 mg, uống, đã ngừng 2 tuần

    Them 15/09/2026. Truoc do ban nhap chi in ten thuoc, nen bac si doc ho so khong
    biet lieu nao, dung the nao — va loi sai lieu khong co cho nao de hien ra.
    """
    thap = cum.lower()
    cach_dung = " ".join(v for v in (t.get("duong_dung"), t.get("so_lan")) if v)
    phan = [v for v in (t.get("lieu"), cach_dung) if v and v.lower() not in thap]
    ten = _chuan(t.get("ten"))
    if phan:
        chen = ", ".join(phan)
        k = thap.find(ten.lower()) if ten else -1
        if k >= 0:
            cuoi = k + len(ten)
            cum = f"{cum[:cuoi]} {chen}{cum[cuoi:]}"
        else:
            cum = f"{cum}, {chen}"
    if t.get("bat_dau") and t["bat_dau"].lower() not in thap:
        cum += f" ({_chuan(t['bat_dau'])})"
    if t.get("ngung") and t["ngung"].lower() not in thap:
        cum += f" (đã ngừng {_chuan(t['ngung'])})"
    return cum


def dien_dat(p, ten_chu_the=None):
    """Mot phat bieu -> mot cum chu. KHONG gop voi phat bieu khac.

    LUAT 2: "chua ghi nhan" ra chu "chua ghi nhan", khong ra "khong co".
    Ba muc do chac chan la ba cach dien dat khac nhau, khong quy ve nhau duoc:

        chac chan  + phu dinh False  ->  "sot"
        chac chan  + phu dinh True   ->  "không sốt"
        nghi ngo                     ->  "nghi ngờ sốt"
        chua ghi nhan                ->  "chưa ghi nhận sốt"

    `chua ghi nhan` bo qua phu_dinh: "chua thay bi bao gio" da la mot cho trong,
    khong phai mot phu dinh.
    """
    nd = _chuan(p.get("noi_dung"))
    muc_do = p.get("do_chac_chan", "chắc chắn")
    if muc_do == "chưa ghi nhận":
        cum = f"chưa ghi nhận {nd}"
    elif muc_do == "nghi ngờ":
        # Noi dung da mang dau rao don ("viem hong nghi do lien cau") thi khong
        # them lan nua — giong ban tham chieu cua bo sinh.
        cum = nd if re.search(r"(?<!\w)nghi(?!\w)", nd, re.I) else f"nghi ngờ {nd}"
    elif p.get("phu_dinh"):
        cum = f"không {nd}"
    else:
        cum = nd
    if p.get("thuoc"):
        cum = _them_chi_tiet_thuoc(cum, p["thuoc"])
    if p.get("moc_thoi_gian"):
        cum += f" ({_chuan(p['moc_thoi_gian'])})"
    if ten_chu_the:
        cum = f"{ten_chu_the}: {cum}"
    return cum


def sinh(phat_bieu, id_benh_nhan=0, ten_chu_the=None, ly_do_kham=None,
         ly_do_chan=None):
    """Tra ve (van_ban, ghi_chu).

    ghi_chu ghi lai TUNG phat bieu di dau va vi sao — de doi chieu nguoc lai
    duoc, va de Task 16 do do day du.

    ten_chu_the: {chu_the_id: "mẹ"} — dat ten cho nguoi khong phai benh nhan,
    de muc TIEN SU GIA DINH noi ro la cua ai.

    ly_do_chan: {id phat bieu: ly do} tu `khoa_bang_chung` — phat bieu bi khoa
    chan KHONG vao than, xuong CAN XAC NHAN kem DUNG ly do cua khoa.
    """
    ten_chu_the = ten_chu_the or {}
    ly_do_chan = ly_do_chan or {}
    theo_muc, ghi_chu = {}, []

    for p in phat_bieu:
        d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
        if d.get("id") in ly_do_chan:
            muc, ly_do = "CẦN XÁC NHẬN", ly_do_chan[d.get("id")]
        else:
            muc, ly_do = _muc_cho(d, id_benh_nhan)
        ten = None
        if muc == MUC_NGUOI_KHAC or d.get("chu_the_id") != id_benh_nhan:
            # Tra bang truoc; khong tra duoc thi dung CHINH CHUOI khau trich da
            # viet. Khong co buoc lui nay thi cau ra KHONG CO TEN NGUOI.
            #
            # LOI DA XAY RA, do duoc 11/09/2026: muc TIEN SU GIA DINH VA XA HOI
            # cua nhanh B, C, D co 50/50/53 cau va **0 cau neu ten nguoi**, trong
            # khi ban tham chieu co 22 cau va 22 cau neu ten. Mot bac si doc
            # "TIEN SU GIA DINH VA XA HOI / roi loan mo mau" khong biet AI bi.
            #
            # Va phep do khong thay: `thuoc_do_quy_gan._chu_the_cua_cau` suy chu
            # the tu TEN MUC khi cau khong co tu chi nguoi, nen mot cau khong ten
            # nam trong muc gia dinh van duoc cham la "nguoi nha" — dung 100% o
            # tang 4. Con so 100% do la diem cua viec XEP DUNG MUC, khong phai
            # diem cua viec GAN DUNG NGUOI.
            ten = ten_chu_the.get(d.get("chu_the_id"))
            if not ten and not _la_nhan_vien(d):
                tho = _chuan(d.get("ten_chu_the") or "")
                if tho and tho.lower() not in TEN_KHONG_DAT_TEN:
                    ten = tho
        cum = dien_dat(d, ten)
        if ly_do:
            cum = f"{cum} — {ly_do}"
        theo_muc.setdefault(muc, []).append(cum)
        ghi_chu.append({"id": d.get("id"), "muc": muc, "ly_do": ly_do,
                        "noi_dung": _chuan(d.get("noi_dung")),
                        "bang_chung": d.get("bang_chung"),
                        # DUNG dong chu trong ban nhap — giao dien duyet noi tung
                        # dong voi phat bieu cua no qua truong nay
                        "van": cum})

    # LY DO KHAM BENH: lay phat bieu hien tai dau tien, KHONG viet lai noi dung.
    if ly_do_kham is None and "BỆNH SỬ HIỆN TẠI" in theo_muc:
        ly_do_kham = theo_muc["BỆNH SỬ HIỆN TẠI"][0]
    if ly_do_kham:
        theo_muc["LÝ DO KHÁM BỆNH"] = [ly_do_kham]

    khoi = []
    for muc in THU_TU_MUC:
        cum_list = theo_muc.get(muc)
        if not cum_list:
            continue                          # khong sinh muc rong
        khoi.append(f"{muc}\n\n" + ". ".join(cum_list) + ".")
    return "\n\n".join(khoi), ghi_chu


MUC_PHU = "CẦN XÁC NHẬN"
# Cau hoi lam ro (`hoi_lai`) cung la PHAN PHU: no la viec bac si can lam, khong
# phai thong tin ve benh nhan. Dung sau CAN XAC NHAN, nhung phai tach duoc ca khi
# ho so khong co muc CAN XAC NHAN nao.
MUC_HOI_LAI = "CÂU HỎI LÀM RÕ"
MUC_PHU_TAT_CA = (MUC_PHU, MUC_HOI_LAI)


def tach_muc_phu(van_ban):
    """-> (benh_an, phan_can_xac_nhan).

    VI SAO CAN HAM NAY. `CẦN XÁC NHẬN` la muc do du an nay dat ra, khong co
    trong bat ky ban tham chieu nao. Bo cham cua cuoc thi nhan dien muc bang
    quy tac "dong viet hoa toan bo", nen no dem `CẦN XÁC NHẬN` la mot muc
    du doan — va vi ban tham chieu khong co muc do, day thanh mot DUONG TINH
    GIA, keo Section F1 xuong.

    Nghia la co che an toan cua du an bi chinh phep cham phat. Cach xu ly
    trung thuc khong phai la bo muc do di, ma la BAO CAO CA HAI SO:

        co muc phu    dung dau ra that cua he thong
        khong muc phu benh an thuan, so sanh cong bang voi cac nhanh khac

    Va bao cao luon so phat bieu nam trong muc phu — neu khong thi "chuyen
    sang can xac nhan" se thanh cho giau moi thu kho.
    """
    if not any(m in (van_ban or "") for m in MUC_PHU_TAT_CA):
        return van_ban or "", ""
    khoi = (van_ban or "").split("\n\n")
    than, phu, dang_phu = [], [], False
    i = 0
    while i < len(khoi):
        if khoi[i].strip() in MUC_PHU_TAT_CA:
            dang_phu = True
            phu.append(khoi[i])
            i += 1
            continue
        (phu if dang_phu else than).append(khoi[i])
        i += 1
    return "\n\n".join(than).strip(), "\n\n".join(phu).strip()
