# -*- coding: utf-8 -*-
"""Ban ghi phat bieu — cau truc trung tam cua phuong phap.

Moi thong tin lam sang rut ra tu hoi thoai duoc ghi thanh mot ban ghi 11 truong.
Benh an CHI duoc sinh tu tap ban ghi dang `con hieu luc`.

Ba truong quan trong nhat, moi truong chan mot loi that:

  tinh_huong    "Neu mai chau van dau thi…" khong duoc ghi thanh trieu chung
                da xay ra. Tach khoi do_chac_chan vi gia dinh KHONG PHAI la
                chua chac ve mot su that — no la su that CHUA XAY RA.

  quan_he       Co `dien_bien` ben canh `dinh_chinh`. "Hom qua dau, hom nay het
                dau" la dien bien, GIU CA HAI. Neu chi co `dinh_chinh` thi he
                thong se vut mat cau dau.

  bang_chung    La DANH SACH luot thoai. Cap "Anh co di ung thuoc khong?" / "Co."
                can ca hai luot moi du nghia.
"""
from dataclasses import asdict, dataclass, field
from typing import List, Optional

DO_CHAC_CHAN = ("chắc chắn", "nghi ngờ", "chưa ghi nhận")
TINH_HUONG = ("thực tế", "giả định", "kế hoạch")
QUAN_HE = ("bổ sung", "đính chính", "diễn biến", "mâu thuẫn")
TRANG_THAI = ("còn hiệu lực", "bị thay thế", "chưa giải quyết")
THOI_GIAN = ("hiện tại", "quá khứ", "chưa rõ")
NGUOI_NOI = ("bác sĩ", "bệnh nhân", "người nhà", "điều dưỡng")

# Loai phat bieu — THEM 11/09/2026 cho tang "phat bieu nguyen tu".
#
#   trả lời    loi benh nhan / nguoi nha ngay SAU mot luot cua nhan vien y te
#   tự kể      loi benh nhan / nguoi nha KHONG co ai hoi dan vao: dinh chinh,
#              bo sung, dien bien, va bay tang 4 deu thuoc loai nay
#   quan sát   ket qua kham, sinh hieu
#   nhận định  chan doan, ke ca muc "nghi ngo"
#   kế hoạch   chi dinh, dan do, ke ca dan do co dieu kien
#
# KHONG co "cau hoi": cau hoi khong ai tra loi thi KHONG tao ban ghi (xem
# `bakeoff.HUONG_DAN`), nen mot gia tri "cau hoi" se khong bao gio co vi du —
# dung ho loi "khai trong luoc do ma khong bao gio co gia tri" da gap nam lan.
HANH_VI = ("trả lời", "tự kể", "quan sát", "nhận định", "kế hoạch")

# Thong tin CHI TIET VE THUOC — THEM 15/09/2026.
#
# Truoc do mot phat bieu thuoc chi co `noi_dung` = ten thuoc ("amlodipin"). Nhom
# loi nguy hiem nhat ve thuoc — sai lieu, sai so lan, sai duong dung, thuoc da
# ngung ghi thanh dang dung — khong co cho nao de ghi, nen cung khong co cach nao
# de do (so tay, Phan II, nhom loi 9).
#
# `thuoc` la mot tu dien hoac None. Chi `ten` bat buoc; chi tiet nao hoi thoai KHONG
# noi thi de None — doan lieu la tu bia ra thong tin lam sang.
#
# HAI DANH SACH DONG chi khai nhung gia tri BO SINH THAT SU TAO RA. Khai mot gia
# tri ma khong bao gio co vi du ("tiem", "da ke chua dung") la ho loi "khai trong
# luoc do ma khong bao gio co gia tri" da gap sau lan. Muon them gia tri thi them
# kich ban vao bo sinh cung luc.
# DOI CHIEU VOI CHUAN QUOC TE (doc 16/09/2026, xem docs/nguon/thuoc-va-tieng-viet.md):
#   `lieu`  GOP hai truong cua n2c2 2018: `Strength` ("500 mg") va `Dosage`
#           ("nửa gói", "hai nhát"). Khong tach vi bo sinh khong sinh ca hai cung
#           luc; phai ghi ro cho nay khi so so lieu voi n2c2.
#   `ngung` KHONG phai `Duration` cua n2c2. `Duration` la do dai dot dung ("trong
#           7 ngày"); `ngung` la DA NGUNG DUOC BAO LAU ("2 tuần"). Hai thu khac
#           nhau, dung tra cheo.
#   MEDIQA-OE 2025 (y lenh thuoc tu hoi thoai kham) KHONG tach truong nao: moi y
#   lenh chi co description / order_type / reason / provenance, lieu va so lan
#   chim trong van xuoi. `provenance` cua ho la so luot thoai, giong `bang_chung`.
THUOC_KHOA = ("ten", "lieu", "so_lan", "duong_dung", "bat_dau", "ngung",
              "trang_thai_dung")
DUONG_DUNG = ("uống", "xịt", "bôi", "nhỏ")
# "được kê, chưa dùng" them 16/09/2026 cho y lenh cua bac si ngay trong loi thoai:
# thuoc da duoc ke nhung chua ai uong vien nao. Gop no vao "đang dùng" la ghi mot
# viec CHUA XAY RA thanh viec dang xay ra — dung nhom lo~i so 4 cua so tay.
TRANG_THAI_DUNG = ("đang dùng", "đã ngừng", "được kê, chưa dùng")


@dataclass
class PhatBieu:
    id: int
    nguoi_noi: str
    chu_the_id: int
    noi_dung: str
    bang_chung: List[int]                      # danh sach so luot thoai
    do_chac_chan: str = "chắc chắn"
    phu_dinh: bool = False
    tinh_huong: str = "thực tế"
    thoi_gian_su_kien: str = "chưa rõ"
    moc_thoi_gian: Optional[str] = None
    doi_tuong_id: Optional[int] = None
    quan_he: Optional[str] = None
    quan_he_voi: Optional[int] = None
    trang_thai: str = "còn hiệu lực"
    # Doan NGUYEN VAN trong hoi thoai lam bang chung, moi luot mot doan.
    #
    # Truong nay nam trong luoc do tu ngay dau nhung khong khau nao dien: bo
    # sinh khong xuat, `du_lieu_trich` khong day, `tu_json` khong doc. Ho loi
    # "khai ma khong dien" — va lan nay la dung cai truong ma ten du an ("truy
    # vet bang chung") dua vao. Dien tu 11/09/2026; `khoa_bang_chung` kiem no voi
    # CHINH hoi thoai, khong voi bang phat bieu.
    trich_dan: List[str] = field(default_factory=list)
    ten_chu_the: str = ""          # chuoi goc mo hinh viet, de tra vai nguoi noi
    hanh_vi: str = ""              # xem HANH_VI; "" = khong ro (dau ra cu)
    thuoc: Optional[dict] = None   # xem THUOC_KHOA; None = khong phai thong tin thuoc

    def __post_init__(self):
        if self.thuoc is not None:
            _kiem_thuoc(self.thuoc)
        _kiem("do_chac_chan", self.do_chac_chan, DO_CHAC_CHAN)
        if self.hanh_vi:
            _kiem("hanh_vi", self.hanh_vi, HANH_VI)
        _kiem("tinh_huong", self.tinh_huong, TINH_HUONG)
        _kiem("trang_thai", self.trang_thai, TRANG_THAI)
        _kiem("thoi_gian_su_kien", self.thoi_gian_su_kien, THOI_GIAN)
        _kiem("nguoi_noi", self.nguoi_noi, NGUOI_NOI)
        if self.quan_he is not None:
            _kiem("quan_he", self.quan_he, QUAN_HE)
            if self.quan_he_voi is None:
                raise ValueError(f"quan_he={self.quan_he!r} phai kem quan_he_voi")
        if not self.bang_chung:
            raise ValueError("bang_chung khong duoc rong — moi phat bieu phai truy vet duoc")

    # ---- ba truong bat buoc phai co gia tri: chu_the_id, do_chac_chan, bang_chung
    def du_dieu_kien_vao_benh_an(self):
        """Thieu mot trong ba truong bat buoc thi chuyen sang muc can xac nhan."""
        return (
            self.chu_the_id is not None
            and self.do_chac_chan in DO_CHAC_CHAN
            and bool(self.bang_chung)
            and self.trang_thai == "còn hiệu lực"
            and self.tinh_huong == "thực tế"
        )

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


def _kiem(ten, gia_tri, hop_le):
    if gia_tri not in hop_le:
        raise ValueError(f"{ten}={gia_tri!r} khong hop le; phai thuoc {hop_le}")


def _kiem_thuoc(t):
    """`thuoc` phai la tu dien, co `ten`, chi dung khoa trong THUOC_KHOA, va hai
    truong dong nam trong danh sach — hoac None khi hoi thoai khong noi."""
    if not isinstance(t, dict):
        raise ValueError(f"thuoc phai la tu dien, nhan {type(t).__name__}")
    thua = set(t) - set(THUOC_KHOA)
    if thua:
        raise ValueError(f"thuoc co khoa la: {sorted(thua)}")
    if not str(t.get("ten") or "").strip():
        raise ValueError("thuoc phai co ten")
    if t.get("duong_dung") is not None:
        _kiem("duong_dung", t["duong_dung"], DUONG_DUNG)
    if t.get("trang_thai_dung") is not None:
        _kiem("trang_thai_dung", t["trang_thai_dung"], TRANG_THAI_DUNG)


# ------------------------------------------------- cau noi tu dau ra mo hinh

# Cach goi benh nhan trong hoi thoai nhi khoa. Dung cho nhanh B, la nhanh
# KHONG co lien ket thuc the — no chi co chuoi tu do de doi chieu.
TEN_BENH_NHAN = ("trẻ", "bé", "cháu", "bệnh nhân", "con", "em bé", "trẻ nhỏ")

# Vai NHAN VIEN Y TE — MOT dinh nghia duy nhat cho ca du an.
#
# Chung khong bao gio la `chu_the` hop le cua thong tin lam sang: cau bac si
# noi la thong tin VE BENH NHAN. `chu_the` la thong tin ve ai, `nguoi_noi` la
# ai noi; gop hai truong do lai chinh la lo~i quy gan.
#
# VI SAO DAT O DAY. Hang rao nay truoc do nam o DUNG MOT trong ba cho can no:
# `sinh_benh_an` co `NHAN_VIEN_Y_TE`, con `phat_bieu.tu_json` va
# `sua_cuc_bo.kiem_mot_cau` thi khong. Hai bang cung nghia o hai tep la cach
# chung troi nhau; dat o `phat_bieu` vi cau hoi "cai gi duoc lam `chu_the`"
# thuoc ve luoc do, khong thuoc ve khau sinh van.
#
# GIA CUA CHO THIEU, do duoc: khau trich ghi `chu_the = "bac si"` cho 160/537
# phat bieu tren tap phat trien. `tu_json` cho chung `id_khac`, roi
# `sua_cuc_bo` ket luan "thong tin cua nguoi khac" va doi cau sang muc TIEN SU
# GIA DINH VA XA HOI — 104 lan. Tang bac si tut 98,6% -> 52,8%, diem gop tut
# 13,7 diem.
#
# VI SAO KHONG THUOC DO NAO THAY. Thuoc do dau-cuoi suy chu the tu VAN BAN
# sinh ra va ten muc, khong tu `chu_the_id`. Nhanh B va C giu cau dung muc nen
# thuoc do doc ra "benh nhan" va cho diem dung du bieu dien ben trong sai. Chi
# nhanh D phoi no ra, vi D la nhanh duy nhat HANH DONG theo `chu_the_id`.
#
# Day la luan diem cua du an xay ra ben trong du an: mot sai quy gan co the
# nam trong bieu dien ma thuoc do gop khong thay, cho den khi mot khau sau tin
# vao no.
VAI_NHAN_VIEN = ("bác sĩ", "bác sỹ", "bs", "điều dưỡng", "y sĩ", "y tá")


def la_vai_nhan_vien(ten):
    """Ten nay la vai nhan vien y te khong. Thuan tuy, de test duoc.

    Khop theo CHUOI CON co chu y: mo hinh viet "bac si Lan" hoac "bs Nam" chu
    khong chi viet "bac si". Day cung la ngu nghia cua `sinh_benh_an` truoc
    khi gop — doi sang khop chinh xac se lam mat nhung truong hop do.
    """
    thap = str(ten or "").strip().lower()
    return any(v in thap for v in VAI_NHAN_VIEN)


def dem_vai_nhan_vien(ps):
    """-> so ban ghi co `chu_the` la vai nhan vien y te.

    De do TY LE chu khong de chua: neu chi chuan hoa am tham thi khong ai biet
    khau trich sai bao nhieu. Con so nay phai vao bao cao.
    """
    return sum(1 for p in ps or [] if la_vai_nhan_vien(p.get("chu_the")))


def id_khac_an_toan(id_theo_ten, mac_dinh=1):
    """Id danh cho chu the KHONG tra duoc trong bang — phai khong dam vao id nao.

    LOI DA XAY RA, do duoc 11/09/2026, va no lam sai MOI menh de cua nguoi nha.

    `tu_json` co `id_khac=1` trong chu ky ham, va KHONG MOT cho goi nao truyen
    gia tri khac. Trong khi `thuc_the.lien_ket` cap id theo thu tu xuat hien, va
    tren hoi thoai kham benh thi:

        0  benh nhan
        1  BAC SI
        2  nguoi nha

    Nen moi chu the khong tra duoc — `chu_the = "me"` chang han — nhan id 1, tuc
    la **tro thanh bac si**. Do duoc tren ca dau tien cua tap phat trien:

        chu_the 'me' -> id 1 -> ten_chu_the[1] = 'bac si'

    Va hau qua o dau ra: muc TIEN SU GIA DINH VA XA HOI cua nhanh B, C, D co
    50/50/53 cau, va **0 cau neu ten nguoi**. Ban tham chieu co 22 cau, **22 cau
    neu ten nguoi**. Mot bac si doc ban nhap do khong biet ai bi roi loan mo mau.

    Tinh tu bang thay vi dat hang so: bang do `thuc_the.lien_ket` sinh ra nen so
    thuc the doi theo hoi thoai, va mot hang so nao cung se dam vao mot luc nao.
    """
    if not id_theo_ten:
        return mac_dinh
    so = [v for v in id_theo_ten.values() if isinstance(v, int)]
    return max(so) + 1 if so else mac_dinh


def tu_json(ps, nguoi_noi_theo_luot=None, id_theo_ten=None, id_khac=None):
    """Doi dau ra JSON cua mo hinh thanh danh sach PhatBieu da kiem hop le.

    `nguoi_noi` khong nam trong luoc do cua mo hinh — suy ra tu nguoi noi cua
    luot bang chung CUOI CUNG. Voi cap hoi–dap [1, 2] thi luot 2 la cau tra
    loi, va nguoi tra loi moi la nguoi phat ngon thong tin do.

    `id_theo_ten` anh xa chuoi `chu_the` sang `chu_the_id`:
      nhanh B  bang tra tho theo TEN_BENH_NHAN (khong co lien ket thuc the)
      nhanh C  bang dung tu `thuc_the.lien_ket()`

    Ban ghi khong dung luoc do bi BO va ghi vao `loi`, khong duoc doan bu —
    doan bu la tu bia ra thong tin lam sang.
    """
    nguoi_noi_theo_luot = nguoi_noi_theo_luot or {}
    if id_khac is None:
        id_khac = id_khac_an_toan(id_theo_ten)
    ra, loi = [], []
    for i, p in enumerate(ps):
        try:
            bang_chung = [int(x) for x in (p.get("luot_thoai") or p.get("bang_chung") or [])]
            if not bang_chung:
                raise ValueError("khong co luot thoai lam bang chung")
            nguoi_noi = nguoi_noi_theo_luot.get(max(bang_chung), "bệnh nhân")
            ten = str(p.get("chu_the", "")).strip().lower()
            # Vai nhan vien y te khong phai chu the cua thong tin lam sang:
            # cau bac si noi la thong tin VE BENH NHAN. Quy ve benh nhan thay
            # vi de no thanh "nguoi khac" — xem chu thich o VAI_NHAN_VIEN.
            if la_vai_nhan_vien(ten):
                chu_the_id = 0
            elif id_theo_ten is None:
                chu_the_id = 0 if ten in TEN_BENH_NHAN else id_khac
            else:
                chu_the_id = id_theo_ten.get(ten, id_khac)
            quan_he = p.get("quan_he")
            if quan_he in (None, "không", ""):
                quan_he, quan_he_voi = None, None
            else:
                quan_he_voi = p.get("quan_he_voi")
                if quan_he_voi is None:
                    raise ValueError(f"quan_he={quan_he!r} ma thieu quan_he_voi")
            ra.append(PhatBieu(
                id=i, nguoi_noi=nguoi_noi, chu_the_id=chu_the_id,
                # Gan NGAY TAI CHO DUNG BAN GHI. Truoc day truong nay duoc gan
                # o `nhanh.chay_trung_gian`, sau khi `tu_json` tra ve, bang
                #
                #     zip(ps, [x for x in phat_bieu_tho if x.get("luot_thoai")])
                #
                # Phep zip do LECH HANG khi co ban ghi vua co `luot_thoai` vua
                # khong hop le: no bi loai khoi `ps` nhung van con o danh sach
                # ben phai, nen tu do tro di moi phat bieu nhan ten chu the cua
                # phat bieu KE TIEP. Khong ngoai le, khong dau hieu.
                ten_chu_the=ten,
                noi_dung=str(p.get("noi_dung", "")).strip(),
                bang_chung=bang_chung,
                do_chac_chan=p.get("do_chac_chan", "chắc chắn"),
                phu_dinh=bool(p.get("phu_dinh", False)),
                tinh_huong=p.get("tinh_huong", "thực tế"),
                thoi_gian_su_kien=p.get("thoi_gian_su_kien", "chưa rõ"),
                moc_thoi_gian=p.get("moc_thoi_gian"),
                quan_he=quan_he, quan_he_voi=quan_he_voi,
                trich_dan=_doc_trich_dan(p), hanh_vi=_doc_hanh_vi(p),
                thuoc=_doc_thuoc(p)))
        except (ValueError, TypeError) as e:
            loi.append({"chi_so": i, "ly_do": str(e), "ban_ghi": p})
    return ra, loi


def bang_ten_tu_thuc_the(danh_sach_thuc_the):
    """{cach_goi_thuong: id} tu bang thuc the — dung cho nhanh C.

    Them ca TEN_BENH_NHAN vao thuc the co id 0: mo hinh viet `chu_the` la
    "tre" hoac "be", con bang thuc the goi no la "benh nhan".
    """
    bang = {}
    for t in danh_sach_thuc_the:
        if t.loai != "người":
            continue
        for goi in [t.ten_chuan] + list(t.cach_goi):
            bang.setdefault(str(goi).strip().lower(), t.id)
    for ten in TEN_BENH_NHAN:
        bang.setdefault(ten, 0)
    return bang


def _doc_trich_dan(p):
    """`trich_dan` cua mot ban ghi mo hinh -> danh sach chuoi.

    Chap nhan ca MOT chuoi (mo hinh viet `"trich_dan": "..."` thay vi danh
    sach): noi dung khong doi, chi doi vo boc, nen day khong phai doan bu. Phan
    tu rong bi bo. KHONG kiem o day chuyen trich dan co that trong hoi thoai hay
    khong — do la viec cua `khoa_bang_chung`, noi co hoi thoai.
    """
    td = p.get("trich_dan")
    if isinstance(td, str):
        td = [td]
    if not isinstance(td, (list, tuple)):
        return []
    return [str(x).strip() for x in td if str(x or "").strip()]


def _doc_hanh_vi(p):
    """Gia tri ngoai `HANH_VI` -> "" (khong ro), KHONG bo ca ban ghi.

    Khac `quan_he`: mot `hanh_vi` la khong lam hong thong tin lam sang cua ban
    ghi — chu the, noi dung, bang chung van dung — nen bo ca ban ghi vi no la
    mat thong tin that de doi lay su gon.
    """
    hv = str(p.get("hanh_vi") or "").strip()
    return hv if hv in HANH_VI else ""


def _doc_thuoc(p):
    """`thuoc` cua mot ban ghi mo hinh -> tu dien du THUOC_KHOA, hoac None.

    Cung nguyen tac voi `_doc_hanh_vi`: gia tri ngoai danh sach dong ("hít") hay
    khoa la thi BO RIENG chi tiet do, KHONG bo ca ban ghi — ten thuoc, chu the va
    bang chung van dung. Nhung KHONG DOAN BU: chi tiet nao bo thi thanh None, va
    khoa bang chung / bo cham se thay no la thieu.
    """
    t = p.get("thuoc")
    if not isinstance(t, dict):
        return None
    ten = str(t.get("ten") or "").strip()
    if not ten:
        return None

    def chuoi(k):
        v = t.get(k)
        return str(v).strip() or None if v is not None else None

    duong = chuoi("duong_dung")
    trang = chuoi("trang_thai_dung")
    return {"ten": ten, "lieu": chuoi("lieu"), "so_lan": chuoi("so_lan"),
            "duong_dung": duong if duong in DUONG_DUNG else None,
            "bat_dau": chuoi("bat_dau"), "ngung": chuoi("ngung"),
            "trang_thai_dung": trang if trang in TRANG_THAI_DUNG else None}
