# -*- coding: utf-8 -*-
"""Luat chuyen trang thai theo bon quan he.

CHUONG TRINH lam viec nay, khong phai mo hinh — co chu dinh. Neu mo hinh lam ca
buoc nay thi khi ket qua sai se khong tach duoc loi trich xuat khoi loi cap nhat.

    quan he       luat
    ---------     -------------------------------------------------------------
    bổ sung       ca hai con hieu luc
    đính chính    ban cu -> bi thay the; ban moi -> con hieu luc.
                  Ban cu KHONG XOA, de truy lai duoc rang da co dinh chinh.
    diễn biến     CA HAI con hieu luc, gan moc thoi gian khac nhau.
                  Day la cho de sai nhat: coi dien bien la dinh chinh roi vut
                  mat cau dau. "Hom qua dau, hom nay het dau" — ca hai deu dung.
    mâu thuẫn     ca hai -> chua giai quyet, dua vao muc can xac nhan
"""
from src.phat_bieu import PhatBieu


def ap_luat(danh_sach):
    """Tra ve danh sach MOI voi trang_thai da cap nhat. Khong sua ban goc."""
    ra = [PhatBieu(**p.to_dict()) for p in danh_sach]
    theo_id = {p.id: p for p in ra}

    for p in ra:
        if p.quan_he is None:
            continue
        truoc = theo_id.get(p.quan_he_voi)
        if truoc is None:
            # Tham chieu toi phat bieu khong ton tai — khong doan, gan co.
            p.trang_thai = "chưa giải quyết"
            continue

        if p.quan_he == "bổ sung":
            pass                                    # ca hai giu nguyen

        elif p.quan_he == "đính chính":
            # CHI chap nhan dinh chinh cua CHINH nguoi da noi ban truoc (tu sua).
            # Nguoi khac noi khac di — ke ca bac si — la HAI NGUON khac nhau va
            # khong co can cu chon ben: ha ve mau thuan, cho xac nhan. Truoc
            # 11/09/2026 ban sau luon thang, bat ke ai noi.
            if _cung_nguon(p, truoc):
                truoc.trang_thai = "bị thay thế"
                p.trang_thai = "còn hiệu lực"
            else:
                p.quan_he = "mâu thuẫn"
                truoc.trang_thai = "chưa giải quyết"
                p.trang_thai = "chưa giải quyết"

        elif p.quan_he == "diễn biến":
            truoc.trang_thai = "còn hiệu lực"
            p.trang_thai = "còn hiệu lực"

        elif p.quan_he == "mâu thuẫn":
            truoc.trang_thai = "chưa giải quyết"
            p.trang_thai = "chưa giải quyết"

    return ra


def luot_cua(p) -> int:
    """Luot thoai MUON NHAT lam bang chung cho phat bieu — tuc luot ma thong tin nay
    tro thanh biet duoc. Cap hoi–dap ([3, 4]) chi du nghia o luot 4."""
    return max(getattr(p, "bang_chung", None) or [0])


def ap_luat_theo_luot(danh_sach):
    """-> [(so_luot, danh sach PhatBieu da ap luat)] — anh chup trang thai SAU MOI LUOT.

    VI SAO CO (16/09/2026). `ap_luat` nhan TOAN BO menh de cua ca roi ap luat mot lan,
    nen he thong khong tra loi duoc cau "o luot thu may thi ban nhap bat dau sai".
    Cau do co nghia lam sang truc tiep: mot moc benh su bi dinh chinh o luot 4 thi tu
    luot 2 den luot 3 ho so dang mang so sai.
    Pan, Liu, You (arXiv 2603.17425, 18/03/2026) phat bieu dung viec nay thanh mot vong
    cap nhat chay o moi luot; ho co chi so `T_goal` (luot dau tien moi o bat buoc da du)
    nhung khong co "luot sai dau tien". Xem docs/nguon/cong-trinh-gan-nhat.md.

    KHONG SUA `ap_luat`: ham nay goi lai `ap_luat` tren tung tien to, nen hai duong
    khong the troi nhau. `tests/test_theo_luot.py` chot dieu do bang phep so anh chup
    cuoi cung voi `ap_luat` tren ca danh sach.
    """
    moc = sorted({luot_cua(p) for p in danh_sach})
    return [(t, ap_luat([p for p in danh_sach if luot_cua(p) <= t])) for t in moc]


def con_hieu_luc(danh_sach):
    return [p for p in danh_sach if p.trang_thai == "còn hiệu lực"]


def can_xac_nhan(danh_sach):
    """Phat bieu chua giai quyet + phat bieu gia dinh: khong duoc viet nhu su that."""
    return [p for p in danh_sach
            if p.trang_thai == "chưa giải quyết" or p.tinh_huong != "thực tế"]


def da_bi_thay_the(danh_sach):
    """Giu lai de ghi chu 'da co dinh chinh' trong benh an."""
    return [p for p in danh_sach if p.trang_thai == "bị thay thế"]


# --------------------------------------------------------- doi chung don gian

def ghi_de_phat_bieu_truoc(danh_sach):
    """Doi chung re: phat bieu sau ghi de phat bieu truoc, tren cung noi dung.

    Neu phuong phap khong hon quy tac nay tren cac tinh huong co dinh chinh,
    can xem lai do kho that cua bai toan.
    """
    ra = [PhatBieu(**p.to_dict()) for p in danh_sach]
    moi_nhat = {}
    for p in ra:
        khoa = (p.chu_the_id, p.noi_dung)
        if khoa in moi_nhat:
            moi_nhat[khoa].trang_thai = "bị thay thế"
        moi_nhat[khoa] = p
        p.trang_thai = "còn hiệu lực"
    return ra


def _cung_nguon(sau, truoc) -> bool:
    """Hai phat bieu co cung MOT nguoi noi khong (theo vai nguoi noi). Thieu vai
    o mot ben thi coi la khac nguon — khong du can cu de cho ban sau thang."""
    a = getattr(sau, "nguoi_noi", "") or ""
    b = getattr(truoc, "nguoi_noi", "") or ""
    return bool(a) and a == b


def lich_su(danh_sach):
    """NHAT KY KIEM CHUNG: moi ban KHONG con hieu luc, kem vi sao.

    Ho so chinh chi dung ban con hieu luc; nhat ky giu phan con lai de bac si
    thay "4 ngay da duoc nguoi noi dinh chinh thanh 2 ngay" thay vi thay mot con
    so bien mat.
    """
    ra = []
    for p in danh_sach:
        if p.trang_thai == "còn hiệu lực":
            continue
        boi = [q.id for q in danh_sach
               if q.quan_he_voi == p.id and q.quan_he in ("đính chính", "mâu thuẫn")]
        if p.trang_thai == "bị thay thế":
            ly_do = f"đính chính bởi bản #{boi[0]}" if boi else "bị thay thế"
        elif p.quan_he == "mâu thuẫn" or boi:
            doi = p.quan_he_voi if p.quan_he == "mâu thuẫn" else boi[0]
            ly_do = f"mâu thuẫn với bản #{doi}, chưa xác nhận"
        else:
            ly_do = "chưa giải quyết"
        ra.append({"id": p.id, "noi_dung": p.noi_dung,
                   "moc_thoi_gian": p.moc_thoi_gian, "nguoi_noi": p.nguoi_noi,
                   "trang_thai": p.trang_thai, "ly_do": ly_do,
                   "bang_chung": list(p.bang_chung)})
    return ra
