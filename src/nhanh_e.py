# -*- coding: utf-8 -*-
"""Nhanh E — dung bang phat bieu de RA LAI ban nhap cua A, khong thay the no.

VI SAO CO NHANH NAY. Do tren tap phat trien cho ket qua ro rang:

    A (sinh truc tiep, da huan luyen)   0.6216
    C (sinh tu bang phat bieu)          0.4089

Sinh benh an TU bang phat bieu thua han sinh truc tiep, va thua chu yeu o
hinh thuc: A hoc van phong benh an tu 1.357 ban mau, con bo sinh bang luat
chi biet ghep cum theo bang tra.

Nhung bang phat bieu van co thu A khong co: no biet MOI menh de thuoc ve AI
va dua tren luot thoai nao. Nen thay vi dung bang de VIET, dung no de KIEM.

    E = ban nhap cua A  +  bo sung cho bo sot (Task 16)  +  sua cuc bo (Task 17)

Doi chung dung cua E la A+ (A tu doc lai ban cua chinh no, khong co bang):
A+ chi sua 3/35 ban va khong doi diem. Neu E hon A+ thi cai lam nen chenh
lech la BANG PHAT BIEU, khong phai chuyen "goi mo hinh hai lan".

RUI RO DA BIET, phai do chu khong duoc gia dinh: `sua_cuc_bo` doi menh de
trong bang phai xuat hien NGUYEN VAN trong cau thi moi coi la co nguon. A
viet van xuoi dai, nen nhieu cau se khong khop va bi day xuong muc can xac
nhan — tuc co che nay co the PHA ban nhap tot. `ty_le_giu` do dung dieu do.
"""
import io
import json
import sys

from src import cap_nhat, duong_dan, kiem_day_du, phat_bieu, sua_cuc_bo, thuc_the


def _bang_cho_mau(hoi_thoai, ps_json):
    """Dung bang phat bieu da lien ket + da ap luat cho mot hoi thoai."""
    tt = thuc_the.lien_ket(hoi_thoai)
    bang = phat_bieu.bang_ten_tu_thuc_the(tt)
    nguoi_noi = {so: vai for so, vai, _ in thuc_the.tach_luot(hoi_thoai) if vai}
    ps, loi = phat_bieu.tu_json(ps_json or [], nguoi_noi_theo_luot=nguoi_noi,
                                id_theo_ten=bang)
    for p_moi, p_goc in zip(ps, [x for x in (ps_json or []) if x.get("luot_thoai")]):
        p_moi.ten_chu_the = str(p_goc.get("chu_the", ""))
    ten_chu_the = {t.id: t.ten_chuan for t in tt
                   if t.loai == "người" and t.id != 0}
    return cap_nhat.ap_luat(ps), ten_chu_the, loi


def chay_E(ra_A, kq_tho, bo_sung=True, sua=True):
    """ra_A: doc tu ra_A_<tap>.jsonl. kq_tho: doc tu trich_<tap>_<n>.jsonl.

    Khong goi mo hinh. Ca hai dau vao deu la tep da sinh san.
    """
    theo_id = {k["id"]: k for k in kq_tho}
    ra = []
    for a in ra_A:
        tho = theo_id.get(a["id"])
        ps, ten_chu_the, loi = _bang_cho_mau(a["input"],
                                             (tho or {}).get("phat_bieu"))
        van = a["du_doan"]
        da_bo_sung, da_sua = [], []
        if bo_sung:
            van, da_bo_sung = kiem_day_du.bo_sung(ps, van, ten_chu_the=ten_chu_the)
        if sua:
            ket = sua_cuc_bo.sua(van, ps, ten_chu_the=ten_chu_the)
            van, da_sua = ket.van_ban, ket.da_sua

        from src import sinh_benh_an
        than, _phu = sinh_benh_an.tach_muc_phu(van)
        ra.append({"id": a["id"], "input": a["input"],
                   "tham_chieu": a["tham_chieu"], "du_doan": van,
                   "du_doan_khong_muc_phu": than,
                   "ban_nhap_A": a["du_doan"],
                   "so_luot_goi": a.get("so_luot_goi", 1),
                   "token_vao": a.get("token_vao", 0),
                   "token_ra": a.get("token_ra", 0),
                   "so_phat_bieu": len(ps), "loi_ban_ghi": loi,
                   "so_can_xac_nhan": len(da_sua),
                   "da_bo_sung": da_bo_sung, "da_sua": da_sua,
                   "ghi_chu": None})
    return ra


def ty_le_giu(ra_E):
    """Bao nhieu phan cua ban nhap A con nguyen sau khi ra lai.

    Con so nay quan trong ngang diem: mot co che "sua" xoa mat nua ban nhap
    thi diem co cao cung khong dung duoc.
    """
    giu = sum(len(k["du_doan_khong_muc_phu"]) for k in ra_E)
    goc = sum(len(k["ban_nhap_A"]) for k in ra_E)
    doi = sum(1 for k in ra_E if k["du_doan"].strip() != k["ban_nhap_A"].strip())
    return {"ky_tu_goc": goc, "ky_tu_con": giu,
            "ty_le_giu": giu / max(1, goc), "so_ban_bi_doi": doi,
            "so_ban": len(ra_E)}


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--max-token", type=int, default=3072)
    ap.add_argument("--khong-bo-sung", action="store_true")
    ap.add_argument("--khong-sua", action="store_true")
    ap.add_argument("--ten", default="E")
    a = ap.parse_args()

    from src import du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    d = duong_dan.THU_MUC_DU_LIEU
    ra_A = [json.loads(x) for x in open(d / f"ra_A_{a.tap}.jsonl",
                                        encoding="utf-8") if x.strip()]
    kq_tho = [json.loads(x) for x in
              open(d / f"trich_{a.tap}_{a.max_token}.jsonl",
                   encoding="utf-8") if x.strip()]

    ra = chay_E(ra_A, kq_tho, bo_sung=not a.khong_bo_sung, sua=not a.khong_sua)
    dp = d / f"ra_{a.ten}_{a.tap}.jsonl"
    dp.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in ra),
                  encoding="utf-8")

    t = ty_le_giu(ra)
    print(f"Ghi {len(ra)} dong -> {dp}")
    print(f"Ban bi sua doi: {t['so_ban_bi_doi']}/{t['so_ban']}")
    print(f"Giu lai {t['ty_le_giu']:.0%} do dai ban nhap cua A "
          f"({t['ky_tu_con']}/{t['ky_tu_goc']} ky tu)")
    print(f"Tong cho da sua: {sum(len(k['da_sua']) for k in ra)}, "
          f"da bo sung: {sum(len(k['da_bo_sung']) for k in ra)}")


if __name__ == "__main__":
    main()
