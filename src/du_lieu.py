# -*- coding: utf-8 -*-
"""Nap va loc bo du lieu hoi thoai y khoa.

Bon tap duoc chia o `tach_tap.py`, khong chia o day. Module nay chi lo
viec doc, tach luot thoai va thong ke.
"""
import json
import re
from collections import Counter

# Moi luot thoai nam tren mot dong, bat dau bang ten vai roi dau hai cham.
VAI_RE = re.compile(r"^\s*([^:]{1,20}?)\s*:\s*(.*)$")
NGUOI_NHA_RE = re.compile(r"(?mi)^\s*Người nhà\s*:")

# ---------------------------------------------------------------- nhan dien ca nhi
#
# BAN 1 (bo ngay 05/09/2026) chi khop tu khoa:
#     (cháu|bé |con tôi|con em|trẻ|nhi khoa|sơ sinh|tháng tuổi|em bé)
# Kiem tay 30 mau cho ra 16/30 dung = 53%, duoi nguong 80% cua Cua 1.
# Bon kieu sai:
#     "hồi trẻ em có hút"     — trang tu chi thoi gian, benh nhan la nguoi lon
#     "aspirin trẻ em"        — "tre em" lam dinh ngu cho thuoc
#     "chú có mấy cháu rồi"   — chau noi/ngoai cua benh nhan nguoi lon
#     "cô còn trẻ mà"         — thanh ngu
#
# BAN 2: doi hoi TRE PHAI LA BENH NHAN. Mot cum khang dinh, va khong dinh
# bat ky cum loai tru nao. Do lai o `docs/ket-qua/kiem-tay-nhan-nhi.md`.

_NHI_DUONG = re.compile(
    r"(?i)("
    r"em bé|sơ sinh|sinh non|tháng tuổi|nhi khoa|"
    r"(bé|cháu)\s+(bị|sốt|ho|nôn|ngã|khóc|đau|mệt|tăng cân|sinh)|"
    r"khám\s+cho\s+(bé|cháu|con)|"
    r"(bé|cháu)\s+(nhà|năm nay|được)\s|"
    r"(lịch sử sinh|cân nặng lúc sinh|tiêm chủng)\s+của\s+(bé|cháu)|"
    r"mẹ\s+của\s+(bé|cháu)|"
    r"con\s+(trai|gái)\s+(em|tôi|chị|anh)\s|"
    r"(con|bé)\s+bú"
    r")"
)

_NHI_AM = re.compile(
    r"(?i)("
    r"hồi trẻ|còn trẻ|trẻ lại|thời trẻ|lúc trẻ|"
    r"trẻ em\s+(có|vào|uống)|aspirin trẻ em|"
    r"cháu (nội|ngoại)|(mấy|các|hai|ba|bốn|những) (đứa )?cháu|"
    r"có\s+(mấy|hai|ba|bốn|một)\s+(đứa\s+)?(cháu|bé)"
    r")"
)


def co_dau_hieu_nhi(mau):
    """True khi TRE la benh nhan, khong phai khi hoi thoai co nhac toi tre."""
    t = mau["input"]
    return bool(_NHI_DUONG.search(t)) and not bool(_NHI_AM.search(t))


# Giu lai ban 1 de bao cao muc cai thien; khong dung o cho nao khac.
NHI_RE_BAN1 = re.compile(r"(?i)(cháu|bé |con tôi|con em|trẻ|nhi khoa|sơ sinh|tháng tuổi|em bé)")


def nap_mau(duong_dan):
    """Doc mot tep jsonl thanh danh sach dict."""
    with open(duong_dan, encoding="utf-8") as f:
        return [json.loads(dong) for dong in f if dong.strip()]


def ghi_mau(duong_dan, mau_list):
    """Ghi danh sach dict ra jsonl, giu nguyen dau tieng Viet."""
    with open(duong_dan, "w", encoding="utf-8") as f:
        for m in mau_list:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


def tach_luot_thoai(hoi_thoai):
    """Tra ve [(vai, noi_dung), ...]. Bo qua dong khong khop dinh dang."""
    ket_qua = []
    for dong in hoi_thoai.split("\n"):
        m = VAI_RE.match(dong)
        if m:
            ket_qua.append((m.group(1).strip(), m.group(2).strip()))
    return ket_qua


def co_nguoi_nha(mau):
    return bool(NGUOI_NHA_RE.search(mau["input"]))


def loc_mau_co_nguoi_nha(mau_list):
    return [m for m in mau_list if co_nguoi_nha(m)]


def thong_ke(mau_list):
    vai = Counter()
    for m in mau_list:
        for v, _ in tach_luot_thoai(m["input"]):
            vai[v] += 1
    nguoi_nha = [m for m in mau_list if co_nguoi_nha(m)]
    nhi = [m for m in mau_list if co_dau_hieu_nhi(m)]
    return {
        "tong": len(mau_list),
        "luot_theo_vai": dict(vai),
        "so_mau_nguoi_nha": len(nguoi_nha),
        "so_mau_nhi": len(nhi),
        "so_mau_ca_hai": len([m for m in nguoi_nha if co_dau_hieu_nhi(m)]),
    }


# --------------------------------------------------- chot bao ve Cua 5

TAP_KHOA = "kiem_tra_cuoi"
# Bien moi truong mo chot — CHI dat sau Cua 5 (khoa thiet ke), va ghi vao
# docs/NHAT-KY.md ngay luc dat. Giong `CHO_PHEP_TAP_NGOAI`: mot viec co chu
# dinh, khong phai mot gia tri mac dinh.
MO_TAP_KHOA = "MEDITRACE_MO_TAP_KHOA"

# ------------------------------------------- chot chan du lieu cua cuoc thi cu
#
# Bon tap nay la BAN SAO du lieu cua mot cuoc thi NLP, khong phai du lieu cua
# du an. Ban to chuc khuyen khong dung tai san cua ho de tranh cau hoi ve tinh
# chinh thong, va do dau vet cho thay bo do rat nhieu kha nang la BAN DICH tu
# tieng Anh (`src/dau_vet_nguon.py`).
#
# Chan bang MA chu khong bang tri nho, vi cai bay o day rat kin: `nhanh.py`
# tung de `--tap` mac dinh la "phat_trien", nen chay lenh mac dinh la doc phai
# du lieu cuoc thi ma khong ai dinh lam the.
TAP_NGOAI = ("train", "phat_trien", "kiem_tra_cuoi", "kiem_tra_chung",
             "train_tang_cuong")

CHO_PHEP_TAP_NGOAI = "MEDITRACE_CHO_PHEP_TAP_NGOAI"


def chan_tap_ngoai(cac_tap):
    """Nem loi neu ai do doc tap cua cuoc thi cu ma khong noi ro y dinh.

    Khong xoa han duong doc: phep do dau vet nguon goc (`dau_vet_nguon.py`) la
    mot ket qua that cua du an va can chay lai duoc. Nhung no phai la mot viec
    CO CHU DINH, dat bien moi truong `MEDITRACE_CHO_PHEP_TAP_NGOAI=1`, chu khong
    phai thu xay ra vi mot gia tri mac dinh.
    """
    import os
    if os.environ.get(CHO_PHEP_TAP_NGOAI):
        return
    ten = [cac_tap] if isinstance(cac_tap, str) else list(cac_tap)
    ngoai = [t for t in ten if t in TAP_NGOAI]
    if ngoai:
        raise SystemExit(
            f"TU CHOI: {', '.join(ngoai)} la du lieu cua cuoc thi cu, khong "
            f"phai cua du an.\n"
            f"Bo tu sinh tuong ung: viet_train / viet_phat_trien / "
            f"viet_kiem_tra_cuoi.\n"
            f"Neu that su can doc (vi du chay lai phep do dau vet nguon goc) "
            f"thi dat {CHO_PHEP_TAP_NGOAI}=1, va ghi vao docs/NHAT-KY.md.")


# ------------------------------------------- chot chan du lieu do GPT sinh
#
# Bo 500 hoi thoai phuong ngu va hai tu dien kem theo do GPT sinh (nguoi dung
# xac nhan 11/09/2026). Du an khong dung mo hinh ngon ngu thuong mai o bat ky
# khau nao, ke ca sinh du lieu huan luyen — nen du lieu do CHI DE DO. Moi tep
# chuyen tu bo do mang chu "gpt" trong ten (`src.bo_gpt500`), va moi duong huan
# luyen goi ham nay, ca tep train lan tep val (val chon checkpoint, tuc la cung
# anh huong mo hinh). KHONG co bien moi truong mo chot: khong co ly do chinh dang
# nao de huan luyen tren no.
DAU_DU_LIEU_GPT = "gpt"


def chan_du_lieu_gpt(cac_tep):
    import os
    ten = [cac_tep] if isinstance(cac_tep, (str, os.PathLike)) else list(cac_tep)
    bi_chan = [str(t) for t in ten
               if t and DAU_DU_LIEU_GPT in os.path.basename(str(t)).lower()]
    if bi_chan:
        raise SystemExit(
            f"TU CHOI HUAN LUYEN tren {', '.join(bi_chan)}: du lieu do GPT sinh "
            f"chi de do, khong de huan luyen (docs/nguon-du-lieu.md).")


def chan_tap_khoa(cac_tap):
    """Nem loi neu ai do dinh cham vao tap kiem tra cuoi truoc Cua 5.

    Ke hoach ghi: "Tap kiem tra cuoi chi mo sau Cua 5. Mo som la hong toan bo
    phan danh gia." Hong theo kieu khong lay lai duoc — mot khi da nhin so tren
    tap do thi moi lua chon sau deu co the bi anh huong, va khong co cach nao
    chung minh la khong.

    Mot dong `--tap kiem_tra_cuoi` go nham la du. Chan bang ma chu khong tin
    vao viec nho.
    """
    import os
    if os.environ.get(MO_TAP_KHOA):
        return
    ten = [cac_tap] if isinstance(cac_tap, str) else list(cac_tap)
    # Khop CHUOI CON, khong khop nguyen ten. LO~ DA TON TAI den 11/09/2026: tap
    # kiem tra cuoi cua bo tu sinh ten la `viet_kiem_tra_cuoi`, con chot nay chi
    # so `"kiem_tra_cuoi" in ten` — tuc so NGUYEN TEN, ten cua bo du lieu cuoc
    # thi cu. Voi bo du lieu dang dung, chot khong chan gi ca; va `nhanh.py` —
    # script chay nhieu nhat — con khong goi no.
    bi_chan = [t for t in ten if TAP_KHOA in str(t)]
    if bi_chan:
        raise SystemExit(
            f"TU CHOI: tap `{bi_chan[0]}` chi duoc mo sau Cua 5 (khoa thiet ke).\n"
            "Neu that su da qua Cua 5 thi bo chan nay co chu dinh, "
            "va ghi vao docs/NHAT-KY.md.")
