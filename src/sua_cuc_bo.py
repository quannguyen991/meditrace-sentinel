# -*- coding: utf-8 -*-
"""Kiem chung tung cau cua ban nhap, sua CUC BO chu khong sinh lai ca ban.

Bon phep kiem, moi phep chan mot loi that:

    khong_co_nguon        cau khong doi chieu duoc voi phat bieu nao
    dung_ban_bi_thay_the  cau dung lai thong tin da bi dinh chinh
    them_muc_chac_chan    hoi thoai noi "chua ghi nhan", ban nhap noi chac
    sai_nguoi             thong tin cua nguoi khac nam trong muc cua benh nhan

Vi du trong ke hoach: hoi thoai "Benh nhan chua nho ro ten thuoc da dung",
ban nhap "Benh nhan da dung paracetamol" -> "paracetamol" khong co nguon,
nen cau bi chuyen xuong muc can xac nhan chu KHONG bi xoa.

BA RUI RO CUA CHINH CO CHE NAY (Task 17 buoc 6), phai do chu khong duoc bo qua:

  1. lam hong cau von dung — nen mac dinh cua moi phep sua la CHUYEN CHO,
     khong phai viet lai. Chuyen cho thi thong tin con nguyen.
  2. bo sot cho lien quan — sau moi vong sua phai chay lai het, vi sua mot
     cau co the lam mot cau khac thanh khong co nguon.
  3. do tre tang them — gioi han `max_vong`. Het vong ma van khong xac minh
     duoc thi chuyen thanh noi dung can bac si kiem, khong sua vo han.

GIOI HAN DA BIET: tren ban nhap do `sinh_benh_an` sinh ra bang luat, co che
nay gan nhu khong tim thay gi — vi khau sinh da ap dung dung nhung luat do.
No chi co viec tren ban nhap do MO HINH viet (nhanh A, A+, hoac ban nhap
ngoai). Dieu do phai ghi vao bao cao, khong duoc trinh bay nhu mot co che
lam nen chenh lech giua C va D.
"""
import re
from dataclasses import dataclass, field
from typing import List

from src import sinh_benh_an
from src.phat_bieu import la_vai_nhan_vien

MUC_PHU = sinh_benh_an.MUC_PHU
MUC_NGUOI_KHAC = sinh_benh_an.MUC_NGUOI_KHAC

HEDGE = {"chưa ghi nhận": "chưa ghi nhận", "nghi ngờ": "nghi ngờ"}


@dataclass
class KetQuaSua:
    van_ban: str
    so_vong: int = 0
    da_sua: List[dict] = field(default_factory=list)
    con_ngo: List[str] = field(default_factory=list)


def _co(cum, van_ban):
    """Cum va van ban co noi cung mot thu khong — doi CA HAI CHIEU.

    LOI DA XAY RA, do duoc 11/09/2026: 195/198 lan sua cua nhanh D la
    `khong_co_nguon`, va phan lon la KE HOACH DIEU TRI do bac si noi. Vi du:

        phat bieu da trich  "Sieu am he tiet nieu. Uong nhieu nuoc, giam dau
                             khi can"
        cau trong ban nhap  "Sieu am he tiet nieu"

    Khau trich sinh MOT phat bieu chua HAI cau. `sinh_benh_an` tach chung thanh
    hai cau rieng. Con phep kiem nay di tim CA `noi_dung` ben trong MOT cau —
    nen khong bao gio khop, va cau bi ket luan la khong co nguon.

    HAI KHAU KHONG DONG Y VE DON VI VAN BAN. Do la ho loi, khong phai mot chi
    tiet: giong truong hop `menh_de[0]` va truong hop doi id thay vi doi noi
    dung, moi lan deu la hai cho cung dung mot du lieu voi hai gia dinh khac
    nhau ve hinh cua no.

    Gia do duoc: bao phu tang bac si 95,00% -> 82,36%, diem gop -0,115.
    """
    cum = re.sub(r"\s+", " ", str(cum or "")).strip()
    van = re.sub(r"\s+", " ", str(van_ban or "")).strip()
    if not cum or not van:
        return False

    def trong(nho, to):
        return re.search(rf"(?<![\wÀ-ỹ]){re.escape(nho)}(?![\wÀ-ỹ])",
                         to, re.I) is not None

    # Chieu thuan: phat bieu nam trong cau.
    if trong(cum, van):
        return True
    # Chieu nguoc: cau la MOT PHAN cua mot phat bieu nhieu cau. Doi hoi cau du
    # dai de khong khop bua — mot cau ba chu nam trong moi thu.
    return len(van.split()) >= 3 and trong(van, cum)


def tach_muc(van_ban):
    """-> [(ten_muc_hoac_None, [cau, ...])] giu nguyen thu tu."""
    ra = []
    for khoi in (van_ban or "").split("\n\n"):
        t = khoi.strip()
        if not t:
            continue
        if t == t.upper() and len(t) > 3 and not any(c.isdigit() for c in t):
            ra.append([t, []])
        elif ra:
            ra[-1][1].extend(c.strip() for c in t.split(".") if c.strip())
        else:
            ra.append([None, [c.strip() for c in t.split(".") if c.strip()]])
    return [(m, cs) for m, cs in ra]


def _ghep(muc_list):
    khoi = []
    for muc, cau in muc_list:
        if not cau:
            continue
        khoi.append(muc if muc else "")
        khoi.append(". ".join(cau) + ".")
    return "\n\n".join(k for k in khoi if k != "" or True).strip()


def kiem_mot_cau(cau, muc, phat_bieu, id_benh_nhan=0):
    """-> (ten_loi, phat_bieu_lien_quan) hoac (None, ...)."""
    lien_quan = [p for p in phat_bieu if _co(p.get("noi_dung"), cau)]
    if not lien_quan:
        return "khong_co_nguon", []

    con_hieu_luc = [p for p in lien_quan
                    if p.get("trang_thai", "còn hiệu lực") == "còn hiệu lực"]
    if not con_hieu_luc:
        return "dung_ban_bi_thay_the", lien_quan

    for p in con_hieu_luc:
        muc_do = p.get("do_chac_chan", "chắc chắn")
        if muc_do in HEDGE and not _co(HEDGE[muc_do], cau):
            return "them_muc_chac_chan", [p]

    if muc not in (MUC_PHU, MUC_NGUOI_KHAC):
        # CHAN HAI LAN. `phat_bieu.tu_json` da quy vai nhan vien y te ve benh
        # nhan, nhung phep kiem nay cung phai tu chan: ban nhap ngoai va ban
        # ghi cu khong di qua duong do.
        #
        # Khong chan thi cau bac si noi bi ket luan la "thong tin cua nguoi
        # khac" va bi doi sang muc TIEN SU GIA DINH VA XA HOI — da xay ra 104
        # lan tren tap phat trien, lam tang bac si tut 98,6% -> 52,8%.
        khac = [p for p in con_hieu_luc
                if p.get("chu_the_id") != id_benh_nhan
                and not la_vai_nhan_vien(p.get("ten_chu_the"))]
        if khac and not any(p.get("chu_the_id") == id_benh_nhan
                            or la_vai_nhan_vien(p.get("ten_chu_the"))
                            for p in con_hieu_luc):
            return "sai_nguoi", khac

    return None, con_hieu_luc


def _mot_vong(muc_list, phat_bieu, id_benh_nhan, ten_chu_the):
    """Mot luot ra soat. -> (muc_list_moi, danh_sach_sua)."""
    moi = {m: list(c) for m, c in muc_list}
    thu_tu = [m for m, _ in muc_list]
    sua = []

    for muc, cau_list in muc_list:
        # Cau DA nam o muc phu thi khong ra soat lai. Vong sua chay lai sau moi
        # lan sua (co y, xem rui ro 2 o dau tep), nhung mot cau da bi chuyen
        # xuong muc phu thi da mang san chu thich
        #
        #     "<cau> — khong doi chieu duoc voi hoi thoai"
        #
        # va chinh chu thich do lam no khong con khop voi phat bieu nao nua. Nen
        # vong sau gan co no lan nua va noi them mot chu thich nua. Da thay ban
        # ghi "Sieu am he tiet nieu — khong doi chieu duoc voi hoi thoai" bi gan
        # co lan thu hai trong cung mot ca.
        if muc == MUC_PHU:
            continue
        for cau in cau_list:
            loi, lq = kiem_mot_cau(cau, muc, phat_bieu, id_benh_nhan)
            if loi is None:
                continue
            moi[muc].remove(cau)
            if loi == "dung_ban_bi_thay_the":
                # Ban moi da nam o cho khac trong benh an. Bo han, khong
                # chuyen xuong muc phu — chuyen xuong la noi lai mot thong
                # tin da bi dinh chinh.
                sua.append({"cau": cau, "loi": loi, "thanh": None, "muc": muc})
                continue
            if loi == "them_muc_chac_chan":
                hedge = HEDGE[lq[0].get("do_chac_chan")]
                cau_moi = f"{hedge} {cau}"
                moi[muc].append(cau_moi)
                sua.append({"cau": cau, "loi": loi, "thanh": cau_moi, "muc": muc})
                continue
            if loi == "sai_nguoi":
                ten = ten_chu_the.get(lq[0].get("chu_the_id"))
                # Cau tu `sinh_benh_an` da co san tien to "<ten>: ". Dan them
                # lan nua thanh "bac si: bac si: ..." — da xay ra that tren
                # tap phat trien.
                da_co_tien_to = re.match(r"^[^:]{1,20}:\s", cau) is not None
                cau_moi = f"{ten}: {cau}" if (ten and not da_co_tien_to) else cau
                dich = MUC_NGUOI_KHAC
                moi.setdefault(dich, [])
                if dich not in thu_tu:
                    thu_tu.append(dich)
                moi[dich].append(cau_moi)
                sua.append({"cau": cau, "loi": loi, "thanh": cau_moi, "muc": dich})
                continue
            # khong_co_nguon -> chuyen xuong muc phu, KHONG xoa
            moi.setdefault(MUC_PHU, [])
            if MUC_PHU not in thu_tu:
                thu_tu.append(MUC_PHU)
            moi[MUC_PHU].append(f"{cau} — không đối chiếu được với hội thoại")
            sua.append({"cau": cau, "loi": loi, "thanh": None, "muc": MUC_PHU})

    # giu thu tu muc chuan, MUC_PHU luon cuoi
    thu_tu_chuan = [m for m in sinh_benh_an.THU_TU_MUC if m in moi]
    con_lai = [m for m in thu_tu if m in moi and m not in thu_tu_chuan]
    return [(m, moi[m]) for m in thu_tu_chuan + con_lai], sua


def sua(van_ban, phat_bieu, id_benh_nhan=0, ten_chu_the=None, max_vong=3):
    """Sua cuc bo, lap toi khi on dinh hoac het `max_vong`."""
    ten_chu_the = ten_chu_the or {}
    ps = [p.to_dict() if hasattr(p, "to_dict") else dict(p) for p in phat_bieu]
    muc_list = tach_muc(van_ban)
    ket = KetQuaSua(van_ban=van_ban)

    for _ in range(max_vong):
        ket.so_vong += 1
        muc_list, sua_vong = _mot_vong(muc_list, ps, id_benh_nhan, ten_chu_the)
        ket.da_sua.extend(sua_vong)
        if not sua_vong:
            break

    ket.van_ban = _ghep(muc_list)
    # Het vong ma van con cho khong xac minh duoc -> de bac si kiem, khong
    # sua tiep. Sua vo han la cho du an tu bia them thong tin.
    for muc, cau_list in muc_list:
        if muc == MUC_PHU:
            ket.con_ngo.extend(cau_list)
    return ket
