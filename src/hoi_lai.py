# -*- coding: utf-8 -*-
"""Tang 6 — HOI LAI: chon it cau hoi nhat ma giai quyet duoc nhieu rui ro nhat.

Thay vi hoi lan man, he thong tim 1-3 cau hoi co the lam giam rui ro nhieu nhat.
Mot cau hoi co the giai quyet NHIEU phat bieu cung luc: "Moc sot dung la hai
ngay hay bon ngay?" giai quyet ca cap mau thuan; "Chau da tung dung penicillin
lan nao chua?" (vi du cua ban de xuat) giai quyet ca di ung cua me lan cho trong
"chua ghi nhan" cua tre.

CHON THAM LAM: moi buoc lay cau hoi co tong diem rui ro CUA NHUNG PHAT BIEU CHUA
DUOC CAU NAO PHU lon nhat. Diem rui ro lay tu `cong_rui_ro`.

DANH GIA BANG MO PHONG — va phai noi ro dieu do. Chua co benh nhan that de hoi.
`danh_gia_khoa.mo_phong_hoi_lai` tra loi moi cau hoi bang dap an cua bo sinh (mot
nguoi tra loi HOAN HAO), roi dem so loi nguy co cao duoc sua. Con so do la TRAN
TREN: nguoi that tra loi mo ho, tra loi sai, hoac khong nho. Va phai co doi chung
CHON CAU HOI NGAU NHIEN cung so cau.
"""
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from src import chuan_hoa
from src import cong_rui_ro as cr

TOI_DA = 3


@dataclass
class CauHoi:
    van: str
    ly_do: str
    # {id phat bieu: diem rui ro} — nhung phat bieu cau hoi nay giai quyet
    muc_tieu: Dict[int, float] = field(default_factory=dict)

    @property
    def loi_ich(self) -> float:
        return round(sum(self.muc_tieu.values()), 4)

    def to_dict(self):
        d = asdict(self)
        d["loi_ich"] = self.loi_ich
        return d


def _hoa(s):
    s = str(s or "").strip()
    return s[:1].upper() + s[1:]


def _ten_khac(p):
    if getattr(p, "chu_the_id", 0) != 0 and getattr(p, "ten_chu_the", ""):
        return p.ten_chu_the
    return "người nhà"


def _cau_theo_ly_do(p, ly):
    nd = p.noi_dung
    if ly.startswith("chu_the"):
        return f"Thông tin '{nd}' là của bệnh nhân hay của {_ten_khac(p)} ạ?"
    if ly == "vuot_muc_nghi":
        return f"'{_hoa(nd)}' đã chắc chắn hay mới là nghi ngờ ạ?"
    if ly in ("vuot_muc_chua_ghi_nhan", "phu_dinh_vuot_muc", "co_tu_phu_dinh"):
        return f"Về '{nd}': đã có, chắc chắn không có, hay chưa rõ ạ?"
    if ly == "dieu_kien":
        return f"'{_hoa(nd)}' là đang có thật, hay chỉ nói trong trường hợp nếu ạ?"
    if ly == "moc_khong_thay":
        return f"'{_hoa(nd)}' bắt đầu từ khi nào ạ?"
    if ly == "phuong_ngu_can_hoi":
        for t in getattr(p, "trich_dan", None) or []:
            mo = chuan_hoa.can_hoi(t)
            if mo:
                return f"'{mo[0].goc}' ở đây nghĩa là gì ạ? ({mo[0].ly_do})"
    if ly in ("noi_dung_khong_khop", "phuong_ngu_can_hoi"):
        t = (getattr(p, "trich_dan", None) or [""])[0]
        return f"Câu '{t}' có phải ý là '{nd}' không ạ?"
    return f"Có đúng là '{nd}' không ạ?"


def ung_vien(ps, danh_gia) -> List[CauHoi]:
    """Moi cau hoi co the dat ra, kem nhung phat bieu no giai quyet."""
    theo_id = {p.id: p for p in ps}
    dg = {d.id: d for d in danh_gia}
    ra, da_phu = [], set()

    # 1. MAU THUAN: mot cau cho CA CAP
    for p in ps:
        if p.quan_he != "mâu thuẫn" or p.quan_he_voi not in theo_id:
            continue
        q = theo_id[p.quan_he_voi]
        a, b = q.moc_thoi_gian, p.moc_thoi_gian
        if a and b and a != b:
            van = f"{_hoa(p.noi_dung)}: đúng là {a} hay {b} ạ?"
        else:
            van = f"Về '{p.noi_dung}': hai lời kể khác nhau — thông tin nào đúng ạ?"
        ra.append(CauHoi(van, "mau_thuan", {q.id: dg[q.id].nghiem_trong,
                                            p.id: dg[p.id].nghiem_trong}))
        da_phu |= {p.id, q.id}

    # 2. DI UNG: cho trong "chua ghi nhan" cua benh nhan + di ung cua nguoi nha
    nha = [p for p in ps if p.chu_the_id != 0 and "dị ứng" in p.noi_dung.lower()]
    for p in ps:
        if p.id in da_phu or p.chu_the_id != 0 or not nha:
            continue
        if "dị ứng" not in p.noi_dung.lower() or p.do_chac_chan != "chưa ghi nhận":
            continue
        chat = nha[0].noi_dung.lower().replace("dị ứng", "").strip()
        van = (f"Dị ứng {chat} là của {_ten_khac(nha[0])}; còn bệnh nhân đã từng "
               f"dùng {chat} lần nào chưa ạ?")
        muc = {p.id: dg[p.id].diem or cr.MUC_NGHIEM_TRONG["di_ung"] * 0.5}
        for n in nha:
            if dg[n.id].nhom not in (cr.DA_KIEM_CHUNG, cr.RUI_RO_THAP):
                muc[n.id] = dg[n.id].diem
        ra.append(CauHoi(van, "di_ung_chua_ghi_nhan", muc))
        da_phu |= set(muc)

    # 3. moi phat bieu BI CHAN / NGUY CO CAO con lai: hoi theo ly do dau tien
    for d in cr.thu_tu_duyet(danh_gia):
        if d.nhom in (cr.DA_KIEM_CHUNG, cr.RUI_RO_THAP) or d.id in da_phu:
            continue
        p = theo_id[d.id]
        ly = d.ly_do[0] if d.ly_do else ""
        ra.append(CauHoi(_cau_theo_ly_do(p, ly), ly or "khac", {p.id: d.diem}))
    return ra


def chon(cac_cau: List[CauHoi], toi_da: int = TOI_DA) -> List[CauHoi]:
    """Tham lam theo LOI ICH CON LAI; dung khi het cau co loi ich > 0."""
    con, ra, da = list(cac_cau), [], set()
    while con and len(ra) < toi_da:
        def them(c):
            return sum(v for k, v in c.muc_tieu.items() if k not in da)
        tot = max(con, key=them)
        if them(tot) <= 0:
            break
        ra.append(tot)
        da |= set(tot.muc_tieu)
        con.remove(tot)
    return ra
