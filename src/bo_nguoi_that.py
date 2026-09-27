# -*- coding: utf-8 -*-
"""Nap bo hoi thoai NGUOI THAT ghi tay, kiem, va doi sang dinh dang cua bo sinh.

VI SAO CAN BO NAY. Ca ba tap — train, phat_trien, kiem_tra_cuoi — deu do chinh
bo sinh cua du an sinh ra. Cach chia tap thi dung (cat theo khuon benh, 45/8/7,
xem `tach_tap_viet`), nhung "mo tap kiem tra cuoi mot lan" khong pha duoc vong
tron: 7 khuon giu lai do duoc "khuon chua thay", khong do duoc "NGUON NGON NGU
chua thay".

Va Task 42 do duoc cho hong cu the: **99,1% menh de dap an co nguyen van tu noi
dung trong hoi thoai**. Mot doi chung regex khong mo hinh da hon ca duong ong
day du tren moi tang. Tang ngu vuc (Task 43) ha duoc con so do xuong 92,0% —
thap hon nhung chua du, va tran cua no la that.

Nguoi that khong noi nhu bo sinh. Do la thu duy nhat pha duoc phep dong nhat
hoi thoai -> ban nhap.

AI VIET HOI THOAI — va day la rang buoc, khong phai tuy chon.

    Hoi thoai PHAI do NGUOI dong vai va goi lai. KHONG duoc sinh bang mo hinh
    ngon ngu, ke ca de lam tap DO.

Ly do khong phai hinh thuc: mot mo hinh ngon ngu viet hoi thoai SACH hon nguoi
noi that — no ghi ro chu ngu o hau het cac luot, dung thuat ngu thay vi loi dan
thuong, va khong bo lung cau. Dung mo hinh de sinh tap do chinh la lam lai dung
cai loi ma bo nay duoc dung ra de chua, chi khac la lan nay khong con cho nao
de phat hien.

Tep nay KHONG sinh hoi thoai. No nap thu nguoi da ghi, kiem, va bao lai.

DINH DANG — co tinh de go duoc bang Notepad, khong can cong cu:

    # HT-001
    ## Người
    bệnh nhân: nam, 54 tuổi
    vợ: người đi cùng

    ## Hội thoại
    1 Bác sĩ: Anh thấy thế nào ạ?
    2 Bệnh nhân: Tôi đau trên rốn mấy hôm rồi.
    3 Vợ: Anh ấy còn bỏ cơm nữa. Tôi thì cao huyết áp từ lâu.

    ## Đáp án
    bệnh nhân | đau thượng vị | BỆNH SỬ HIỆN TẠI | 2
    bệnh nhân | chán ăn | BỆNH SỬ HIỆN TẠI | 3
    vợ | tăng huyết áp | TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI | 3

Cot thu nam va sau la tuy chon: `phu_dinh` (co/khong) va `tinh_huong`.

    python -m src.bo_nguoi_that --vao data/nguoi_that --ra data/nguoi_that.jsonl
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

MUC_HOP_LE = ("LÝ DO KHÁM BỆNH", "BỆNH SỬ HIỆN TẠI", "TIỀN SỬ BỆNH",
              "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "THUỐC ĐANG DÙNG", "DỊ ỨNG",
              "KHÁM LÂM SÀNG", "CHẨN ĐOÁN", "KẾ HOẠCH ĐIỀU TRỊ")

TINH_HUONG_HOP_LE = ("thực tế", "giả định", "kế hoạch")

# Tieu de cac khoi. Viet hoa chu cai dau hay khong deu nhan.
KHOI = {"người": "nguoi", "hội thoại": "hoi_thoai", "đáp án": "dap_an"}


class LoiDinhDang(Exception):
    """Loi trong tep ghi tay. Thong bao phai chi ro DONG NAO, vi nguoi sua no
    la nguoi go Notepad chu khong phai lap trinh vien."""


def _khoi_cua(dong):
    m = re.match(r"^##\s+(.+?)\s*$", dong)
    if not m:
        return None
    ten = m.group(1).strip().lower()
    if ten not in KHOI:
        raise LoiDinhDang(f"khoi khong biet: {m.group(1)!r}; "
                          f"chi co {', '.join(KHOI)}")
    return KHOI[ten]


def doc_mot_tep(duong_dan):
    """-> {id, nguoi, luot, dap_an_tho}. Nem `LoiDinhDang` kem so dong."""
    ma = None
    khoi = None
    nguoi, luot, dap_an = {}, [], []
    for so_dong, dong in enumerate(
            Path(duong_dan).read_text(encoding="utf-8").split("\n"), 1):
        tho = dong.strip()
        if not tho or tho.startswith("<!--"):
            continue
        try:
            if tho.startswith("##"):
                khoi = _khoi_cua(tho)
                continue
            if tho.startswith("#"):
                ma = tho.lstrip("#").strip()
                continue
            if khoi == "nguoi":
                vai, _, mo_ta = tho.partition(":")
                if not vai.strip():
                    raise LoiDinhDang("dong nguoi phai co dang 'vai: mo ta'")
                nguoi[vai.strip().lower()] = mo_ta.strip()
            elif khoi == "hoi_thoai":
                m = re.match(r"^(\d+)\s+([^:]{1,30}):\s*(.+)$", tho)
                if not m:
                    raise LoiDinhDang(
                        "dong hoi thoai phai co dang '<so> <Vai>: <loi noi>'")
                luot.append((int(m.group(1)), m.group(2).strip(),
                             m.group(3).strip()))
            elif khoi == "dap_an":
                phan = [p.strip() for p in tho.split("|")]
                if len(phan) < 4:
                    raise LoiDinhDang(
                        "dong dap an phai co it nhat 4 cot: "
                        "chu the | noi dung | muc | luot")
                dap_an.append((phan, so_dong))
            elif khoi is None:
                raise LoiDinhDang("co noi dung truoc khi mo khoi '## ...'")
        except LoiDinhDang as e:
            raise LoiDinhDang(f"{Path(duong_dan).name} dong {so_dong}: {e}") from e
    if not ma:
        raise LoiDinhDang(f"{Path(duong_dan).name}: thieu dong '# <ma ca>'")
    return {"id": ma, "nguoi": nguoi, "luot": luot, "dap_an_tho": dap_an}


def kiem(tho, ten_tep=""):
    """-> danh sach loi (chuoi). Rong la dat.

    Kiem chu khong tu sua: mot tep ghi tay co loi thi NGUOI phai sua, vi chi
    nguoi do biet y minh la gi. Tu doan bu o day la bia thong tin lam sang.
    """
    loi = []
    tien_to = f"{ten_tep}: " if ten_tep else ""
    so_luot = {s for s, _v, _c in tho["luot"]}

    if not tho["luot"]:
        loi.append(f"{tien_to}khong co luot thoai nao")
    if not tho["dap_an_tho"]:
        loi.append(f"{tien_to}khong co dong dap an nao")

    mong_doi = list(range(1, len(tho["luot"]) + 1))
    if sorted(so_luot) != mong_doi:
        loi.append(f"{tien_to}so luot phai lien tuc tu 1; dang co "
                   f"{sorted(so_luot)}")

    vai_trong_thoai = {v.lower() for _s, v, _c in tho["luot"]}
    for _s, vai, _c in tho["luot"]:
        v = vai.lower()
        if v in ("bác sĩ", "điều dưỡng"):
            continue
        if v not in tho["nguoi"]:
            loi.append(f"{tien_to}vai {vai!r} noi trong hoi thoai nhung khong "
                       f"khai o khoi '## Người'")

    for phan, so_dong in tho["dap_an_tho"]:
        chu_the, noi_dung, muc = phan[0], phan[1], phan[2]
        if not noi_dung:
            loi.append(f"{tien_to}dong {so_dong}: noi dung rong")
        if muc not in MUC_HOP_LE:
            loi.append(f"{tien_to}dong {so_dong}: muc {muc!r} khong hop le")
        ct = chu_the.lower()
        if ct != "bệnh nhân" and ct not in tho["nguoi"]:
            loi.append(f"{tien_to}dong {so_dong}: chu the {chu_the!r} khong "
                       f"khai o khoi '## Người'")
        try:
            cac_luot = [int(x) for x in re.split(r"[,\s]+", phan[3]) if x]
        except ValueError:
            loi.append(f"{tien_to}dong {so_dong}: cot luot phai la so")
            continue
        if not cac_luot:
            loi.append(f"{tien_to}dong {so_dong}: thieu luot lam bang chung")
        for l in cac_luot:
            if l not in so_luot:
                loi.append(f"{tien_to}dong {so_dong}: dan luot {l} khong ton tai")
        if len(phan) >= 5 and phan[4] and phan[4].lower() not in ("có", "không"):
            loi.append(f"{tien_to}dong {so_dong}: phu_dinh phai la 'co' "
                       f"hoac 'khong'")
        if len(phan) >= 6 and phan[5] and phan[5] not in TINH_HUONG_HOP_LE:
            loi.append(f"{tien_to}dong {so_dong}: tinh huong {phan[5]!r} "
                       f"khong hop le")
    return loi


def doi_dinh_dang(tho):
    """-> ban ghi cung hinh voi bo sinh: {id, input, output, dap_an, ...}.

    Doi sang DUNG hinh do la ca y nghia cua tep nay: moi cong cu da co —
    `sai_so`, `do_tang_quy_gan`, `do_dac`, `nhanh` — chay duoc ngay tren bo
    nguoi that ma khong sua mot dong nao.
    """
    from src import sinh_benh_an

    dap_an, ps = [], []
    for i, (phan, _so_dong) in enumerate(tho["dap_an_tho"]):
        cac_luot = [int(x) for x in re.split(r"[,\s]+", phan[3]) if x]
        phu_dinh = len(phan) >= 5 and phan[4].lower() == "có"
        tinh_huong = phan[5] if len(phan) >= 6 and phan[5] else "thực tế"
        chu_the = phan[0].lower()
        dap_an.append({"chu_the": chu_the, "noi_dung": phan[1],
                       "muc": phan[2], "luot": cac_luot,
                       "phu_dinh": phu_dinh, "tinh_huong": tinh_huong,
                       "moc_thoi_gian": None, "quan_he": None,
                       "quan_he_voi": None, "trang_thai": "còn hiệu lực"})
        ps.append({"id": i, "chu_the_id": 0 if chu_the == "bệnh nhân" else 1,
                   "ten_chu_the": chu_the, "noi_dung": phan[1],
                   "bang_chung": cac_luot, "do_chac_chan": "chắc chắn",
                   "phu_dinh": phu_dinh, "tinh_huong": tinh_huong,
                   "thoi_gian_su_kien": "chưa rõ", "moc_thoi_gian": None,
                   "trang_thai": "còn hiệu lực", "quan_he": None,
                   "quan_he_voi": None})

    # Ban nhap tham chieu sinh tu dap an bang CHINH khau sinh cua du an, de no
    # cung dinh dang voi bo sinh — khong viet tay, vi viet tay thi hai bo lech
    # dinh dang va moi chenh lech do duoc se lan lon nguyen nhan.
    ten_khac = {1: next((v for v in tho["nguoi"] if v != "bệnh nhân"),
                        "người nhà")}
    output, _ghi_chu = sinh_benh_an.sinh(ps, id_benh_nhan=0,
                                        ten_chu_the=ten_khac)
    return {"id": tho["id"],
            "input": "\n".join(f"{v}: {c}" for _s, v, c in tho["luot"]),
            "output": output, "dap_an": dap_an,
            "so_luot": len(tho["luot"]),
            "nguon": "người thật", "benh": f"nguoi_that_{tho['id']}",
            "bay": [], "boi_canh": "nguoi_that",
            "la_tre_em": False, "nguoi_ke": None,
            "tu_phuong_ngu": [], "cum_dan_thuong": []}


def _phan_tang(ban_ghi):
    """-> Counter bon tang, dung chung dinh nghia voi `sai_so`."""
    from src import sai_so
    return sai_so.tang_menh_de(ban_ghi)


def gom(thu_muc):
    """-> (danh_sach_ban_ghi, danh_sach_loi)."""
    cac_tep = sorted(Path(thu_muc).glob("*.txt"))
    ra, loi = [], []
    for tep in cac_tep:
        try:
            tho = doc_mot_tep(tep)
        except LoiDinhDang as e:
            loi.append(str(e))
            continue
        l = kiem(tho, tep.name)
        if l:
            loi.extend(l)
            continue
        ra.append(doi_dinh_dang(tho))
    return ra, loi


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--vao", default="data/nguoi_that",
                    help="thu muc chua cac tep .txt ghi tay")
    ap.add_argument("--ra", default="data/nguoi_that.jsonl")
    a = ap.parse_args()

    thu_muc = Path(a.vao)
    if not thu_muc.exists():
        raise SystemExit(f"khong co thu muc {thu_muc}. Xem "
                         f"docs/bo-nguoi-that.md de biet dinh dang va "
                         f"phieu tinh huong.")
    ra, loi = gom(thu_muc)
    for x in loi:
        print(f"LOI  {x}")
    if not ra:
        raise SystemExit("khong nap duoc ca nao")

    Path(a.ra).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in ra),
        encoding="utf-8")
    print(f"\n{len(ra)} ca hop le -> {a.ra}")
    if loi:
        print(f"{len(loi)} loi, cac ca do BI BO (xem tren)")

    from collections import Counter
    gop = Counter()
    for r in ra:
        gop += _phan_tang(r)
    tong = sum(gop.values()) or 1
    print("\nPhan tang quy gan cua bo nguoi that:")
    for t in ("bac_si", "benh_nhan", "ke_ho", "ke_ve_minh"):
        print(f"  {t:<12} {gop[t]:>4}  {gop[t] / tong:>6.2%}")
    print(f"\nTang 4 tren bo SINH: 2,32%. Bo nay: {gop['ke_ve_minh'] / tong:.2%}")

    # Do CHINH cai ma bo nay duoc lap ra de pha: ty le sao chep nguyen van.
    from src import thuoc_do_quy_gan as t
    phu = []
    for r in ra:
        thoai = t._tu_noi_dung(r["input"])
        for m in r["dap_an"]:
            w = t._tu_noi_dung(str(m.get("noi_dung") or ""))
            if w:
                phu.append(len(w & thoai) / len(w))
    if phu:
        n = len(phu)
        print(f"\nTy le menh de phu NGUYEN VAN 100%: "
              f"{sum(1 for p in phu if p >= 0.999) / n:.1%}")
        print("  (bo sinh: 99,1% truoc tang ngu vuc, 92,0% sau)")
        print("  Day la con so quan trong nhat cua bo nay. Cao bang bo sinh "
              "thi no khong them gi.")


if __name__ == "__main__":
    main()
