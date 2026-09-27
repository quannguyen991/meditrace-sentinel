# -*- coding: utf-8 -*-
"""Tang cuong tap huan luyen bang BIEN DOI du lieu co san.

KHONG dung mo hinh ngon ngu de sinh hoi thoai moi. Nen van ban giu nguyen la
van phong va cach noi trong du lieu goc; chi nhan vai va luot chen them la do
chuong trinh dat. Ly do o Global Constraint 1: du lieu do mot mo hinh sinh khac
tao ra se co quy gan sach mot cach nhan tao, lam nhiem chinh hien tuong dang do.

Hai phep bien doi, va nhan doi KHAC NHAU:

    doi_vai_thanh_nguoi_nha   benh an KHONG doi — trieu chung van cua benh nhan
    chen_tien_su_nguoi_nha    benh an PHAI THEM muc TIEN SU GIA DINH

Cau "benh an luon giu nguyen" la SAI. Tien su cua nguoi nha thuoc muc tien su
gia dinh, khong phai khong ghi gi.

    python -m src.tang_cuong --chen 150 --doi-vai 50
"""
import argparse
import copy
import io
import random
import re
import sys

# Mau cau RIENG cho tang cuong.
# PHAI roi han voi `sinh_bo_chan_doan.MAU_CAU` — trung mau cau nghia la huan luyen
# tren dung thu se dung de kiem tra. Co test `test_mau_cau_roi_han_voi_bo_chan_doan`.
MAU_CAU = [
    "Nhà tôi có tiền sử {benh}, riêng cháu thì chưa.",
    "Bên tôi thì bị {benh} lâu rồi, còn cháu chưa thấy gì.",
    "Trong nhà tôi bị {benh}, cháu chưa bao giờ.",
    "Bố mẹ tôi đều có {benh}, cháu thì chưa kiểm tra.",
]

BENH = ["cao huyết áp", "tiểu đường", "hen suyễn", "đau dạ dày", "tim mạch", "viêm xoang"]

MUC_GIA_DINH = "TIỀN SỬ GIA ĐÌNH"

# Doi dai tu khi chuyen vai "Benh nhan" -> "Nguoi nha".
# Chi doi dai tu NGOI THU NHAT dung mot minh, khong dong toi "con toi", "nha toi"…
_DAI_TU = [
    (re.compile(r"\bTôi\b"), "Cháu"),
    (re.compile(r"\btôi\b"), "cháu"),
    (re.compile(r"\bEm\b"), "Cháu"),
    (re.compile(r"\bem\b"), "cháu"),
]

# Khong doi vai khi cau chua nhung cum nay — doi dai tu se ra cau vo nghia:
# "Toi thay con toi met" -> "Chau thay con chau met"
# Moi tu chi quan he ho hang di truoc "toi"/"em": doi dai tu se tao cum
# mo ho kieu "ba chau" (bo cua chau, hay ba dua chau?).
_QUAN_HE = (
    "con|cháu|nhà|vợ|chồng|mẹ|bố|ba|má|cha|anh|chị|em|ông|bà|"
    "gia đình|con trai|con gái|chị họ|anh họ|em họ|ông nội|bà nội|ông ngoại|bà ngoại"
)
_KHONG_DOI_VAI = re.compile(rf"(?i)\b({_QUAN_HE})\s+(tôi|em)\b")

# Tu choi luon khi hoi thoai DA CO san chu "chau" hoac "be".
# Tim ra khi soat tay 12 mau: doi "toi" -> "chau" lam tu nay qua tai.
#   "Tôi có hai bé trai, các cháu ở với tôi"
#       -> "Cháu có hai bé trai, các cháu ở với cháu"   (chau mang hai nghia)
#   "Ba tôi với ông nội đều bị đái tháo đường"
#       -> "Ba cháu với ông nội…"   ("ba chau" = bo cua chau hay ba dua chau?)
_DA_CO_CHAU = re.compile(r"(?i)\b(cháu|bé)\b")


def chen_tien_su_nguoi_nha(mau, seed):
    """Chen mot luot nguoi nha ke benh CUA CHINH HO.

    Benh an PHAI them muc TIEN SU GIA DINH — thong tin do khong thuoc benh nhan,
    nhung cung khong duoc bo di.
    """
    rnd = random.Random(seed)
    ra = copy.deepcopy(mau)
    benh = rnd.choice(BENH)
    cau = rnd.choice(MAU_CAU).format(benh=benh)

    dong = ra["input"].split("\n")
    vi_tri = rnd.randrange(1, len(dong) + 1)
    dong.insert(vi_tri, f"Người nhà: {cau}")
    ra["input"] = "\n".join(dong)

    ra["output"] = ra["output"].rstrip() + f"\n\n{MUC_GIA_DINH}\n\nNgười nhà có {benh}."
    ra["id"] = f"{mau['id']}_chen"
    ra["tang_cuong"] = "chen_tien_su"
    return ra


def doi_vai_thanh_nguoi_nha(mau):
    """Doi `Benh nhan:` thanh `Nguoi nha:` va chuyen dai tu.

    Benh an KHONG doi: trieu chung van thuoc ve benh nhan, chi la nguoi ke thay.
    Tra None khi khong chuyen dai tu an toan duoc.
    """
    dong = mau["input"].split("\n")
    if not any(d.startswith("Bệnh nhân:") for d in dong):
        return None
    if _KHONG_DOI_VAI.search(mau["input"]):
        return None
    if _DA_CO_CHAU.search(mau["input"]):
        return None

    moi = []
    for d in dong:
        if d.startswith("Bệnh nhân:"):
            noi_dung = d[len("Bệnh nhân:"):]
            for pat, thay in _DAI_TU:
                noi_dung = pat.sub(thay, noi_dung)
            moi.append("Người nhà:" + noi_dung)
        else:
            moi.append(d)

    ra = copy.deepcopy(mau)
    ra["input"] = "\n".join(moi)
    ra["id"] = f"{mau['id']}_doivai"
    ra["tang_cuong"] = "doi_vai"
    return ra


def tang_cuong(mau_list, n_chen=150, n_doi_vai=50, seed=42):
    """Chi bien doi mau KHONG co luot nguoi nha — mau da co thi giu nguyen."""
    from src import du_lieu

    rnd = random.Random(seed)
    ung_vien = [m for m in mau_list if not du_lieu.co_nguoi_nha(m)]
    rnd.shuffle(ung_vien)

    them = []
    for m in ung_vien:
        if len(them) >= n_chen:
            break
        them.append(chen_tien_su_nguoi_nha(m, seed=hash(m["id"]) % 10**6))

    da_dung = {m["id"] for m in them}
    doi = []
    for m in ung_vien:
        if len(doi) >= n_doi_vai:
            break
        if f"{m['id']}_chen" in da_dung:
            continue
        r = doi_vai_thanh_nguoi_nha(m)
        if r is not None:
            doi.append(r)

    return mau_list + them + doi


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chen", type=int, default=150)
    ap.add_argument("--doi-vai", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    from src import du_lieu, duong_dan

    goc = du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / "train.jsonl")
    ra = tang_cuong(goc, a.chen, a.doi_vai, a.seed)
    du_lieu.ghi_mau(duong_dan.THU_MUC_DU_LIEU / "train_tang_cuong.jsonl", ra)

    nn_goc = len(du_lieu.loc_mau_co_nguoi_nha(goc))
    nn_ra = len(du_lieu.loc_mau_co_nguoi_nha(ra))
    print(f"Truoc : {len(goc):5d} mau, {nn_goc:4d} co nguoi nha")
    print(f"Sau   : {len(ra):5d} mau, {nn_ra:4d} co nguoi nha")
    print(f"Them  : {len(ra) - len(goc):5d} mau  (+{nn_ra - nn_goc} co nguoi nha)")


if __name__ == "__main__":
    main()
