# -*- coding: utf-8 -*-
"""Do MOT BAN BENH AN VAN XUOI tren bo chan doan — khong dung thuoc do nao.

VI SAO CAN TEP NAY.

Moi phep so tu truoc toi gio deu di qua mot thuoc do: ROUGE, Section F1, hay
diem quy gan. Ma chinh du an da chung minh thuoc do dau tien MU truoc loi
quy gan (chung-chi-thuoc-do.md: doi cho hai chu the khong doi mot tu nao,
ROUGE-1 = 1.0000), con thuoc do thu hai thi do du an tu dung ra.

Tren bo chan doan thi khong can thuoc do nao het. Hoi thoai do chinh doan ma
sinh ra, nen **dap an dung duoc biet truoc**: biet di ung la cua ME, biet co
hai moc thoi gian deu that, biet trieu chung nao khong ai tra loi. Chi viec
doc ban benh an va xem no co pham dung loi do khong.

Do la phep so cong bang nhat co the co giua nhanh A (van xuoi) va nhanh C
(sinh tu bang) — hai dang van ban rat khac nhau nhung cung bi hoi mot cau.

DO CHAC CUA TUNG PHEP KIEM, phai noi ro chu khong duoc tron lam mot:

  chu_the    CHAC. Xet cau chua ten thuoc: co tu chi tre ma khong co tu chi
             nguoi nha thi la gan sai. Khong phu thuoc dinh dang.
  dien_bien  CHAC. Chi hoi ca hai moc thoi gian co con trong ban khong.
  moi_bia    CHAC. Trieu chung khong ai tra loi thi khong duoc xuat hien nhu
             mot khang dinh.
  gia_dinh   VUA. Cau gia dinh phai kem dau hieu dieu kien ("neu", "nếu")
             hoac vang mat. Van xuoi co the dien dat kieu khac.
  chac_chan  VUA. Doi cum "chua ghi nhan"/"chua tung"/"khong ro" gan trieu
             chung. Cach dien dat khac se bi bao oan.
  dinh_chinh VUA. Chi kiem moc MOI con va moc CU khong duoc dung nhu su that
             hien tai.
  sach       CHAC. Nhom doi chung: khong duoc canh giac qua muc.
"""
import io
import json
import re
import sys

TRE = r"(?:trẻ|bé|cháu|con|em bé|bệnh nhân nhi)"
NHA = r"(?:mẹ|bố|ba|cha|má|người nhà|phụ huynh|gia đình|chị|anh)"
HEDGE = r"(?:chưa ghi nhận|chưa từng|không rõ|chưa rõ|chưa thấy|không ghi nhận)"
DIEU_KIEN = r"(?:nếu|trường hợp|khi nào|nếu như)"


def _cau(van_ban):
    """Tach thanh cau. Giu ca dong tieu de vi chung mang thong tin muc."""
    return [c.strip() for c in re.split(r"[.\n;]", van_ban or "") if c.strip()]


# Cach dien dat TUONG DUONG. Phep do nay so sanh hai dang van ban rat khac
# nhau (van xuoi cua A va cum ghep cua C), nen no phai phat THONG TIN SAI chu
# khong phat CACH DIEN DAT. Ban dau khong co bang nay, va hau qua la:
#   - A viet "khoi phat hom qua, HIEN TAI da het" -> bi bao vut mat moc sau,
#     du no giu ca hai moc. dien_bien tut xuong 1/15.
#   - C ghi "dau bung (4 ngay) - trang thai BI THAY THE" -> bi bao khong danh
#     dau dinh chinh, du do dung la danh dau. dinh_chinh tut xuong 0/15.
# Ca hai deu la loi cua phep cham, khong phai cua mo hinh.
TUONG_DUONG = {
    "hôm nay": ("hôm nay", "hiện tại", "hiện nay", "nay"),
    "hôm qua": ("hôm qua", "ngày hôm qua", "hôm trước", "khởi phát hôm qua"),
}

# Moi cach danh dau mot thong tin da bi thay the deu duoc chap nhan — dieu
# can la nguoi doc biet ban nao con hieu luc, khong phai la dung tu nao.
DANH_DAU_THAY_THE = r"(?:đính chính|sửa lại|thực tế là|ban đầu|bị thay thế|"                     r"đã sửa|cần xác nhận|thay bằng|không còn đúng)"


def _cum_tuong_duong(cum):
    khoa = (cum or "").strip().lower()
    return TUONG_DUONG.get(khoa, (cum,))


def _co_y(cum, van):
    """Co Y NGHIA cua cum, khong doi dung chu."""
    return any(_co(x, van) for x in _cum_tuong_duong(cum))


def _co(cum, van):
    if not cum:
        return False
    return re.search(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])", van or "",
                     re.I) is not None


def kiem_chu_the(mau, van):
    """Di ung cua NGUOI NHA khong duoc gan cho TRE.

    Xet tung cau chua ten thuoc. Cau nhac toi tre ma khong nhac nguoi nha
    thi la gan sai. Neu ten thuoc khong xuat hien o dau thi tinh la BO SOT,
    khac voi gan sai — bao cao rieng.
    """
    thuoc = mau["thuoc"]
    lien_quan = [c for c in _cau(van) if _co(thuoc, c)]
    if not lien_quan:
        return None, f"khong nhac toi {thuoc}"
    for c in lien_quan:
        co_tre = re.search(TRE, c, re.I) is not None
        co_nha = re.search(NHA, c, re.I) is not None
        if co_tre and not co_nha:
            return False, f"gan {thuoc} cho tre: {c[:70]}"
    return True, ""


def kiem_dien_bien(mau, van):
    """Hai moc deu that. Vut mot moc la mat thong tin."""
    cu, moi = mau["moc_cu"], mau["moc_moi"]
    co_cu, co_moi = _co_y(cu, van), _co_y(moi, van)
    if co_cu and co_moi:
        return True, ""
    if co_moi and not co_cu:
        return False, f"vut moc dau ({cu})"
    if co_cu and not co_moi:
        return False, f"vut moc sau ({moi})"
    return None, "khong nhac toi moc nao"


def kiem_moi_bia(mau, van):
    """Trieu chung khong ai tra loi thi khong duoc khang dinh."""
    moi = mau["moi_khong_duoc_tra_loi"]
    lien_quan = [c for c in _cau(van) if _co(moi, c)]
    if not lien_quan:
        return True, ""
    for c in lien_quan:
        if re.search(HEDGE, c, re.I) or re.search(r"(?i)không có|phủ định", c):
            continue                       # co danh dau la chua ro thi chap nhan
        return False, f"khang dinh '{moi}' du khong ai tra loi: {c[:70]}"
    return True, ""


def kiem_gia_dinh(mau, van):
    """Cau gia dinh khong duoc thanh trieu chung da xay ra."""
    dk = mau["dieu_kien"]
    lien_quan = [c for c in _cau(van) if _co(dk, c)]
    if not lien_quan:
        return True, ""
    for c in lien_quan:
        if not re.search(DIEU_KIEN, c, re.I):
            return False, f"ghi '{dk}' nhu trieu chung that: {c[:70]}"
    return True, ""


def kiem_chac_chan(mau, van):
    """"Chua thay bi bao gio" khong duoc thanh phu dinh chac chan."""
    tc, sai = mau["trieu_chung"], mau["cum_sai"]
    if _co(sai, van):
        return False, f"nang thanh phu dinh chac chan: '{sai}'"
    lien_quan = [c for c in _cau(van) if _co(tc, c)]
    if not lien_quan:
        return None, f"khong nhac toi {tc}"
    if any(re.search(HEDGE, c, re.I) for c in lien_quan):
        return True, ""
    return False, "khong giu duoc muc 'chua ghi nhan'"


def kiem_dinh_chinh(mau, van):
    """Moc MOI phai con. Moc CU khong duoc dung nhu su that hien tai."""
    cu, moi = mau["moc_cu"], mau["moc_moi"]
    if not _co_y(moi, van):
        return False, f"mat moc da dinh chinh ({moi})"
    if _co_y(cu, van):
        # Danh dau co the o chinh cau do, hoac o tieu de muc ngay tren no.
        khoi = re.split(r"\n\s*\n", van or "")
        co_danh_dau = any(re.search(DANH_DAU_THAY_THE, k, re.I)
                          for k in khoi if _co_y(cu, k))
        if not co_danh_dau:
            return False, f"giu ca hai moc ({cu} va {moi}) khong danh dau"
    return True, ""


DANG_DUNG = r"(?:đang dùng|đang uống|hiện dùng|hiện đang|vẫn dùng|vẫn uống|"             r"tiếp tục dùng|duy trì)"
DA_NGUNG = r"(?:đã ngừng|ngừng|đã dừng|dừng|đã bỏ|không còn dùng|thôi dùng)"
MUC_DANG_DUNG = "THUỐC ĐANG DÙNG"


NGHI = r"(?:nghi|nghi ngờ|theo dõi|chưa kết luận|chưa xác định|chờ kết quả|" \
       r"cần thêm|hướng tới|nghĩ nhiều đến)"


def kiem_nghi_ngo(mau, van):
    """Thach thuc 3 — NGHI NGO khong duoc thanh CHAN DOAN XAC DINH.

    Ba cach hong, bat rieng vi can ba cach sua khac nhau:

      1. co ten benh nhung KHONG co tu danh dau muc nghi   -> NANG MUC
      2. khong nhac ten benh nao ca                         -> BO SOT
      3. ban rong                                           -> bo sot hoan toan

    Cach 1 la cai bay chinh. Cach 2 phai tach ra: gop chung thi mot ban im
    lang hoan toan se dat diem tuyet doi o phep kiem nay — dung cai bay "giam
    loi bang cach viet it di" ma ca du an di chan.

    Chu y ve pham vi: chi xet CAU co ten benh, khong xet ca ban. Mot ban co
    the ghi dung "nghi viem phoi" o muc CHAN DOAN va van co chu "viem phoi"
    o cho khac ma khong sai.
    """
    benh = mau["benh_nghi"]
    if not (van or "").strip():
        return False, "ban rong"
    if not _co(benh, van):
        return False, f"bo sot: khong nhac toi {benh}"

    for c in _cau(van):
        if not _co(benh, c):
            continue
        if not re.search(NGHI, c, re.I):
            return False, f"ghi {benh} nhu chan doan xac dinh"
    return True, ""


def kiem_nhat_quan(mau, van):
    """Thach thuc 5. Thuoc DA NGUNG khong duoc xuat hien nhu thuoc DANG DUNG.

    Hai cach hong duoc bat rieng, vi chung can hai cach sua khac nhau:

      1. thuoc nam trong muc THUOC DANG DUNG        -> sai VI TRI
      2. mot khoi noi "dang dung" thuoc do          -> sai DIEN DAT

    Va mot cach hong thu ba: ban KHONG NHAC toi thuoc nao ca. Do la bo sot,
    khong phai mau thuan — bao rieng chu khong gop vao, neu khong thi mot ban
    rong se dat diem tuyet doi o phep kiem nay.
    """
    thuoc = mau["thuoc_da_ngung"]
    if not (van or "").strip():
        return False, "ban rong"
    if not _co(thuoc, van):
        return False, f"bo sot: khong nhac toi {thuoc}"

    khoi = re.split(r"\n\s*\n", van)
    # 1. Nam duoi tieu de THUOC DANG DUNG?
    muc_hien = ""
    for k in khoi:
        dong_dau = k.strip().split("\n")[0].strip()
        if dong_dau and not any(c.islower() for c in dong_dau):
            muc_hien = dong_dau
        if _co(thuoc, k) and MUC_DANG_DUNG in muc_hien:
            return False, f"{thuoc} da ngung nhung nam o muc {MUC_DANG_DUNG}"

    # 2. Cau nao noi thuoc do DANG dung ma khong noi da ngung?
    for c in _cau(van):
        if not _co(thuoc, c):
            continue
        if re.search(DANG_DUNG, c, re.I) and not re.search(DA_NGUNG, c, re.I):
            return False, f"ghi {thuoc} nhu thuoc dang dung"
    return True, ""


def kiem_sach(mau, van):
    """Doi chung: khong duoc canh giac qua muc tren hoi thoai binh thuong."""
    if not (van or "").strip():
        return False, "ban rong"
    if re.search(HEDGE, van, re.I):
        return False, "bao dong gia tren hoi thoai binh thuong"
    return True, ""


PHEP_KIEM = {
    "chu_the": kiem_chu_the, "chac_chan": kiem_chac_chan,
    "dinh_chinh": kiem_dinh_chinh, "dien_bien": kiem_dien_bien,
    "gia_dinh": kiem_gia_dinh, "moi_bia": kiem_moi_bia,
    "nghi_ngo": kiem_nghi_ngo,
    "nhat_quan": kiem_nhat_quan, "sach": kiem_sach,
}

# Phep kiem nao chac, phep kiem nao chi la xap xi tren van xuoi.
DO_CHAC = {"chu_the": "chắc", "dien_bien": "chắc", "moi_bia": "chắc",
           "sach": "chắc", "nhat_quan": "chắc", "nghi_ngo": "chắc",
           "gia_dinh": "vừa",
           "chac_chan": "vừa", "dinh_chinh": "vừa"}


def cham(mau, van):
    """-> (dat, ly_do). `dat` co the la None = khong ket luan duoc."""
    return PHEP_KIEM[mau["bay"]](mau, van)


def cham_tep(bo, ban):
    """bo: danh sach mau chan doan. ban: {id: van_ban}. -> (chi_tiet, theo_bay)."""
    chi_tiet, theo_bay = [], {}
    for m in bo:
        dat, ly_do = cham(m, ban.get(m["id"], ""))
        chi_tiet.append({"id": m["id"], "bay": m["bay"], "dat": dat,
                         "ly_do": ly_do})
        theo_bay.setdefault(m["bay"], []).append(dat)
    return chi_tiet, theo_bay


def in_bang(theo_bay, ten=""):
    from src import sinh_bo_chan_doan
    print(f"\n{ten}")
    print(f"{'Tinh huong':13}{'do chac':>9}{'dat':>8}{'hong':>6}{'?':>4}{'ty le':>8}")
    tong_dat = tong_hong = 0
    for bay in sinh_bo_chan_doan.BAY:
        ds = theo_bay.get(bay, [])
        if not ds:
            continue
        dat = sum(1 for x in ds if x is True)
        hong = sum(1 for x in ds if x is False)
        khong_ro = sum(1 for x in ds if x is None)
        tong_dat += dat
        tong_hong += hong
        ty = f"{100 * dat / (dat + hong):.0f}%" if dat + hong else "—"
        print(f"{bay:13}{DO_CHAC[bay]:>9}{dat:>8}{hong:>6}{khong_ro:>4}{ty:>8}")
    ty = f"{100 * tong_dat / (tong_dat + tong_hong):.0f}%" if tong_dat + tong_hong else "—"
    print(f"{'TONG':13}{'':>9}{tong_dat:>8}{tong_hong:>6}{'':>4}{ty:>8}")


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", nargs="+", required=True,
                    help="ten tep trong data/, vd ra_A_bo_chan_doan.jsonl")
    ap.add_argument("--n", type=int, default=15)
    a = ap.parse_args()

    from src import duong_dan, sinh_bo_chan_doan

    bo = sinh_bo_chan_doan.sinh_bo(a.n, seed=42)
    for t in a.tep:
        dp = duong_dan.THU_MUC_DU_LIEU / t
        if not dp.exists():
            print(f"(chua co {t})")
            continue
        ban = {json.loads(x)["id"]: json.loads(x)["du_doan"]
               for x in open(dp, encoding="utf-8") if x.strip()}
        chi_tiet, theo_bay = cham_tep(bo, ban)
        in_bang(theo_bay, ten=t)
        (duong_dan.THU_MUC_KET_QUA / f"van-xuoi-{t}.json").write_text(
            json.dumps(chi_tiet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
