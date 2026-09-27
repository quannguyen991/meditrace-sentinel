# -*- coding: utf-8 -*-
"""Phep thu bit nhan nguoi noi — tach BIET voi DOAN TRUNG.

CAU HOI NO TRA LOI. Bake-off cho thay ty le gan sai `chu_the` tut manh theo co
mo hinh: 1.7B sai 100%, 4B sai 12%, 8B sai 2%. Cau phan bien hien nhien la
*"vay mo hinh to hon la het loi chu gi, dau can co che nao"*.

Do CHINH XAC khong tra loi duoc cau do, vi mot ly do tinh te:

    Trong hoi thoai kham benh, chu the CHINH LA nguoi noi o phan lon luot.
    Mot mo hinh chi lam dung mot viec — "gan trieu chung cho nguoi vua noi" —
    van dat do chinh xac rat cao. Duong tat DUNG hau het thoi gian.

Nen do chinh xac cao co the la BIET, cung co the la DOAN TRUNG. Hai thu do
khac nhau o cho: cai thu hai se sai dung vao nhung ca nguy hiem nhat — ca
nguoi nha ke ho benh nhan, dung ca ma du an quan tam.

CACH TACH. Chay trich xuat hai lan tren CUNG hoi thoai:

    ban goc    "Bác sĩ:" / "Người nhà:" / "Bệnh nhân:"
    ban bit    "Người 1:" / "Người 2:" / "Người 3:"

Noi dung khong doi mot chu. Dap an dung cung khong doi — cau "Tôi thì dị ứng
penicillin, còn cháu chưa thấy bị" van cho biet ai di ung, bat ke nhan vai.

    Mo hinh HIEU noi dung      -> bit nhan roi ket qua gan nhu khong doi
    Mo hinh DI THEO NHAN VAI   -> bit nhan roi ket qua doi nhieu

**Ty le doi y chinh la phan do CHUA tung duoc do.** No khong phai loi — mot mo
hinh co the doi y ma van dung — nhung no do muc PHU THUOC vao duong tat, va do
la thu ma tang mo hinh khong chac lam giam.

Cung ho y tuong voi phep thu bit mat da dung o cho khac: che bo phan bai doc
di ma he thong van tra loi duoc thi cau hoi do khong do doc hieu.

GIOI HAN, phai ghi vao bao cao. Bit nhan van khong xoa duoc **thu tu luot**:
bac si gan nhu luon noi truoc, nen "Người 1" van doan duoc la bac si. Phep thu
do phan phu thuoc vao TEN VAI, khong do phan phu thuoc vao vi tri.
"""
import re
from typing import Dict, Tuple

# Nhan trung tinh. Dung chu "Người" cho moi vai de khong con goi y nao ve
# chuc nang (bac si / benh nhan / nguoi nha) lot lai trong chinh cai nhan.
MAU_NHAN = "Người {}"

_DAU_DONG = re.compile(r"^(\s*)([^:\n]{1,20}?)(\s*:\s*)", re.MULTILINE)


def bit(hoi_thoai: str) -> Tuple[str, Dict[str, str]]:
    """Doi ten vai o dau moi luot thanh nhan trung tinh.

    Tra ve (hoi thoai da bit, bang tra {ten goc: nhan moi}). Cung mot vai luon
    duoc mot nhan — neu khong thi chinh phep bit se xoa mat thong tin "hai luot
    nay cung mot nguoi", va do la thong tin that chu khong phai duong tat.
    """
    bang: Dict[str, str] = {}

    def thay(m):
        khoang, ten, dau = m.group(1), m.group(2).strip(), m.group(3)
        if ten not in bang:
            bang[ten] = MAU_NHAN.format(len(bang) + 1)
        return f"{khoang}{bang[ten]}{dau}"

    return _DAU_DONG.sub(thay, hoi_thoai), bang


def bit_mau(mau: dict) -> dict:
    """Ban sao cua mot mau voi `input` da bit nhan. `output` GIU NGUYEN —
    dap an dung khong phu thuoc vao ten vai."""
    moi = dict(mau)
    moi["input"], moi["bang_nhan"] = bit(mau["input"])
    return moi


# ------------------------------------------------------------- doi chieu

def _chuan_chu_the(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def la_nhan_trung_tinh(chu_the: str) -> bool:
    """`chu_the` co phai chi la cai nhan chep lai khong.

    Mo hinh tra ve "Người 2" nghia la no khong rut duoc chu the tu noi dung —
    no chi chep lai nhan cua luot. Do la bang chung TRUC TIEP cua viec di theo
    duong tat, manh hon ca ty le doi y.
    """
    return bool(re.fullmatch(r"người\s*\d+", _chuan_chu_the(chu_the)))


def doi_chieu(goc: list, bit_nhan: list) -> dict:
    """So hai danh sach phat bieu tho (dict tu mo hinh) cua CUNG mot hoi thoai.

    Ghep theo `noi_dung` — khong ghep theo thu tu, vi hai lan chay co the trich
    ra so phat bieu khac nhau, va ghep theo thu tu se bao "doi y" o nhung cho
    that ra chi la lech mot o.
    """
    theo_nd = {}
    for p in bit_nhan:
        theo_nd.setdefault(_chuan_chu_the(p.get("noi_dung")), []).append(p)

    khop = doi_y = trung_tinh = 0
    vi_du = []
    for p in goc:
        nd = _chuan_chu_the(p.get("noi_dung"))
        ung_vien = theo_nd.get(nd)
        if not ung_vien:
            continue
        q = ung_vien.pop(0)
        khop += 1
        a, b = _chuan_chu_the(p.get("chu_the")), _chuan_chu_the(q.get("chu_the"))
        if la_nhan_trung_tinh(b):
            trung_tinh += 1
        if a != b:
            doi_y += 1
            if len(vi_du) < 5:
                vi_du.append({"noi_dung": p.get("noi_dung"),
                              "chu_the_goc": p.get("chu_the"),
                              "chu_the_bit": q.get("chu_the")})
    return {
        "so_phat_bieu_goc": len(goc),
        "so_phat_bieu_bit": len(bit_nhan),
        "so_khop_noi_dung": khop,
        "so_doi_y": doi_y,
        "so_chu_the_la_nhan": trung_tinh,
        "vi_du": vi_du,
    }
