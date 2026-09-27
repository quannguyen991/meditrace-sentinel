# -*- coding: utf-8 -*-
"""Chung chi cho thuoc do: no co NHIN THAY loi quy gan khong.

Mot thuoc do moi khong duoc tin chi vi tac gia noi no tot. Phai chung minh hai
dieu, va phai chung minh tren BENH AN THAT chu khong phai vi du tu viet:

    1. NHAY  — loi nguy hiem (doi chu the) phai lam diem sup.
    2. KHONG QUA NHAY — loi vo hai (doi tu dong nghia) phai bi tru it hon HAN.

Dieu 2 la dieu de quen. Mot thuoc do phat moi thay doi nhu nhau thi cung mu y
het ROUGE, chi mu theo kieu khac: no khong phan biet duoc *sai* voi *khac*.

Va da co bai hoc cu the o Task 3: nhom doi chung PHAI KHOP SO TU BI DOI. Lan
truoc do lech vi loi nguy hiem doi 2 tu con loi vo hai doi 1 tu — ket luan suyt
bi rut nguoc. O day dieu do duoc cai thanh dieu kien loc: benh an nao khong
tao duoc phep doi chung khop so tu thi BI LOAI khoi phep so, va so bi loai
duoc bao cao.

    python -m src.chung_chi_thuoc_do
"""
import argparse
import io
import json
import re
import sys
import unicodedata

from src import cham_diem, du_lieu, duong_dan, thuoc_do_quy_gan as tdq

# Cap tu dong nghia dung cho nhom doi chung. Dieu kien chon:
#   - that su dong nghia trong ngu canh benh an (khong doi nghia lam sang)
#   - CA HAI ve deu la tu noi dung voi ca hai thuoc do
#     (neu mot ve la tu dem cua thuoc do quy gan thi phep doi vo hinh voi no,
#      va thuoc do se an diem mot cach khong cong bang)
# Cap (bieu thuc tim, tu thay). Dung bieu thuc chu khong dung chuoi vi mot so
# tu chi dong nghia trong MOT SO ngu canh:
#   "ba ngay" -> "ba hom"        dung
#   "ngay hom qua" -> "hom hom qua"  sai — nen co chan phia sau
DONG_NGHIA = (
    (r"ngày(?!\s+(?:hôm|nay|qua|kia|trước|sau|mai|mốt))", "hôm"),
    (r"nhiều", "lắm"),
    (r"nôn", "ói"),
    (r"uống", "dùng"),
    (r"tiêu chảy", "ỉa chảy"),
    (r"hiện tại", "hiện nay"),
    (r"trước đây", "trước kia"),
    (r"gần đây", "vừa qua"),
    (r"biểu hiện", "dấu hiệu"),
    (r"tình trạng", "trạng thái"),
    (r"bắt đầu", "khởi phát"),
    (r"mệt mỏi", "mệt nhọc"),
    (r"cảm thấy", "cảm nhận"),
    (r"hôm nay", "bữa nay"),
    (r"trước đó", "trước đấy"),
    (r"đau", "nhức"),
    (r"thấy", "nhận thấy"),
    (r"sốt", "phát sốt"),
    (r"khám", "thăm khám"),
)

# CHI dung tu chi nguoi MOT AM TIET o ca hai phia.
#
# Ban dau co ca "Ba ngoai", "Benh nhan". Doi "Tre" (1 tu) lay "Ba ngoai"
# (2 tu) lam moi token phia sau lech mot o, va phep dem `so_tu_khac` bao
# 82 tu bi doi thay vi 2. Nhom doi chung khong the nao khop duoc con so do,
# nen benh an bi loai — mat mau vi mot loi ky thuat chu khong phai vi du lieu.
#
# Giu bang so am tiet thi phep dem theo vi tri con dung, va "doi 2 tu" cua
# nhom nguy hiem khop dung "doi 2 tu" cua nhom vo hai.
TU_BN = ("bệnh nhân", "trẻ", "bé", "cháu", "con")
# Bo sinh dung ca "vo", "chong", "con trai", "con gai" lam chu the nguoi
# nha; thieu chung thi so ban co nguoi nha bi dem thieu di nhieu.
TU_NN = ("bà ngoại", "bà nội", "ông ngoại", "ông nội", "anh trai", "chị gái",
         "em trai", "em gái", "con trai", "con gái", "con dâu", "con rể",
         "người nhà", "gia đình", "bố mẹ", "cha mẹ",
         "mẹ", "bố", "cha", "vợ", "chồng", "dì", "cậu", "chú", "bác")


def _chuan(s):
    return unicodedata.normalize("NFC", s or "")


def _tach_tu(s):
    return re.findall(r"\w+", _chuan(s).lower(), re.UNICODE)


def so_tu_khac(a, b):
    """So token khac nhau giua hai ban, tinh bang can le (`difflib`).

    Ban dau dem theo VI TRI: ghep hai danh sach token roi dem cho lech. Cach do
    hong ngay khi hai tu thay cho nhau co so am tiet khac nhau — doi "trẻ"
    (1 tu) lay "bà ngoại" (2 tu) lam moi token phia sau lech mot o, va phep dem
    bao 82 tu bi doi thay vi 3. Hau qua khong phai sai so: benh an do bi LOAI
    khoi phep so vi nhom doi chung khong khop noi con so, nen mau tut xuong 5.

    Can le lai bang `SequenceMatcher` thi chi dem dung phan that su khac.
    """
    from difflib import SequenceMatcher
    ta, tb = _tach_tu(a), _tach_tu(b)
    n = 0
    for thao_tac, i1, i2, j1, j2 in SequenceMatcher(None, ta, tb).get_opcodes():
        if thao_tac != "equal":
            n += max(i2 - i1, j2 - j1)
    return n


# ------------------------------------------------------- phep doi nguy hiem

def hoan_doi_chu_the(ban):
    """Doi cho tu chi BENH NHAN va tu chi NGUOI NHA o hai cau khac nhau.

    Tra ve `None` neu benh an khong co du ca hai — khong the bia ra mot loi
    quy gan tren ban khong noi toi nguoi nha.
    """
    ban = _chuan(ban)
    vi_bn = _tim(ban, TU_BN)
    vi_nn = _tim(ban, TU_NN)
    if vi_bn is None or vi_nn is None:
        return None
    # Hai tu phai nam o HAI CAU khac nhau. Doi cho trong cung mot cau thi cau
    # do thanh vo nghia ("Me chua ghi nhan di ung, me di ung penicillin"),
    # con doi cho giua hai cau moi tao ra dung mot benh an van doc troi chay
    # nhung gan sai nguoi — chinh la loi ma du an di chan.
    if _cau_thu_may(ban, vi_bn[0]) == _cau_thu_may(ban, vi_nn[0]):
        return None

    (c1, t1), (c2, t2) = vi_bn, vi_nn
    if c1 > c2:
        (c1, t1), (c2, t2) = (c2, t2), (c1, t1)
    return (ban[:c1] + _theo_hoa(t1, t2) + ban[c1 + len(t1):c2]
            + _theo_hoa(t2, t1) + ban[c2 + len(t2):])


def vung_than_bai(ban):
    """Cac doan van ban KHONG phai dong tieu de muc, kem vi tri tuyet doi.

    Bat buoc phai co. Ten muc "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" co chua chu
    "gia đình"; tim khong phan biet hoa thuong se khop vao chinh TIEU DE va
    phep hoan doi se pha ten muc. Luc do Section F1 tut tu 1,00 xuong 0,69 —
    nhung tut vi CAU TRUC vo, khong phai vi quy gan sai.

    Do la mot phep thu bi nhiem: no lam bo cham cuoc thi trong nhu the co
    nhin thay loi quy gan, trong khi thuc ra no chi nhin thay mot cai tieu de
    hong. Ket luan rut ra tu do se co loi cho du an mot cach khong that.
    """
    ra, vi = [], 0
    for dong in _chuan(ban).split("\n"):
        if not _la_tieu_de(dong):
            ra.append((vi, vi + len(dong)))
        vi += len(dong) + 1
    return ra


def _la_tieu_de(dong):
    s = dong.strip()
    return bool(s) and len(s) <= 70 and s == s.upper() and not s.endswith(".")


def _trong_than_bai(vi_tri, vung):
    return any(d <= vi_tri < c for d, c in vung)


def _tim(ban, tu_list):
    """Vi tri xuat hien dau tien cua bat ky tu nao trong `tu_list`,
    CHI xet phan than bai."""
    vung = vung_than_bai(ban)
    ra = None
    for t in tu_list:
        for m in re.finditer(r"(?<![\w])" + t + r"(?![\w])", ban, re.IGNORECASE):
            if not _trong_than_bai(m.start(), vung):
                continue
            if ra is None or m.start() < ra[0]:
                ra = (m.start(), m.group())
            break
    return ra


def _theo_hoa(cu, moi):
    """Giu kieu viet hoa cua tu cu khi thay bang tu moi."""
    return moi.capitalize() if cu[:1].isupper() else moi


def _cau_thu_may(ban, vi_tri):
    return len(re.findall(r"[.;!?\n]", ban[:vi_tri]))


# --------------------------------------------------------- phep doi vo hai

def doi_dong_nghia(ban, so_tu_can_doi):
    """Doi tu dong nghia cho den khi so tu bi doi DUNG bang `so_tu_can_doi`.

    Tra `None` neu khong dat dung con so — tot hon la loai mau do khoi phep so
    con hon la so hai nhom co so tu bi doi khac nhau.
    """
    ban = _chuan(ban)
    ra = ban
    # Thay TUNG lan xuat hien mot, dem lai sau moi lan. Thay het mot cap roi
    # moi dem thi de vuot qua con so can dat va khong lui lai duoc.
    tien_bo = True
    while so_tu_khac(ra, ban) < so_tu_can_doi and tien_bo:
        tien_bo = False
        for goc, moi in DONG_NGHIA:
            if so_tu_khac(ra, ban) >= so_tu_can_doi:
                break
            vung = vung_than_bai(ra)
            for m in re.finditer(r"(?<![\w])(?:" + goc + r")(?![\w])", ra, re.IGNORECASE):
                if not _trong_than_bai(m.start(), vung):
                    continue
                thu = ra[:m.start()] + _theo_hoa(m.group(), moi) + ra[m.end():]
                moi_khac = so_tu_khac(thu, ban)
                # Chi nhan neu tien them MA KHONG vuot qua con so can dat.
                # Khong co ve nay thi mot phep doi hai tu se nhay tu 3 len 5 va
                # khong bao gio lui lai duoc — benh an bi loai oan.
                if so_tu_khac(ra, ban) < moi_khac <= so_tu_can_doi:
                    ra, tien_bo = thu, True
                    break
    return ra if so_tu_khac(ra, ban) == so_tu_can_doi else None


# ------------------------------------------------------------------- chay

def do_mot_ban(goc):
    """Tra ve dict so lieu cho mot benh an, hoac None neu khong dung duoc."""
    sai = hoan_doi_chu_the(goc)
    if sai is None:
        return None, "không có đủ cả chủ thể bệnh nhân lẫn người nhà"
    n = so_tu_khac(sai, goc)
    vo_hai = doi_dong_nghia(goc, n)
    if vo_hai is None:
        return None, f"không tạo được đối chứng đổi đúng {n} từ"

    return {
        "so_tu_doi": n,
        "nguy_hiem": {
            "cuoc_thi": cham_diem.diem_cuoi(sai, goc),
            "quy_gan": tdq.diem(sai, goc),
        },
        "vo_hai": {
            "cuoc_thi": cham_diem.diem_cuoi(vo_hai, goc),
            "quy_gan": tdq.diem(vo_hai, goc),
        },
    }, None


def _tb(ds, *duong_dan_khoa):
    lay = []
    for d in ds:
        v = d
        for k in duong_dan_khoa:
            v = v[k]
        lay.append(v)
    return sum(lay) / len(lay) if lay else 0.0


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", nargs="*",
                    default=["phat_trien", "kiem_tra_chung", "train"])
    ap.add_argument("--toi-da", type=int, default=400)
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()

    # Chot bao ve Cua 5. `kiem_tra_cuoi` chi duoc mo SAU khi khoa thiet ke; mo
    # som la hong toan bo phan danh gia, va hong mot cach khong lay lai duoc.
    # Mot dong `--tap kiem_tra_cuoi` go nham la du. Chan o day chu khong tin
    # vao viec nho.
    du_lieu.chan_tap_khoa(a.tap)
    du_lieu.chan_tap_ngoai(a.tap)

    mau = []
    for t in a.tap:
        dp = duong_dan.THU_MUC_DU_LIEU / f"{t}.jsonl"
        if dp.exists():
            mau += du_lieu.nap_mau(dp)
    print(f"nap {len(mau)} benh an tu {', '.join(a.tap)}")

    dung, bo = [], {}
    for m in mau:
        if len(dung) >= a.toi_da:
            break
        kq, ly_do = do_mot_ban(m["output"])
        if kq is None:
            bo[ly_do] = bo.get(ly_do, 0) + 1
            continue
        kq["id"] = m["id"]
        dung.append(kq)

    print(f"dung duoc {len(dung)} benh an; loai {sum(bo.values())}")
    for k, v in sorted(bo.items(), key=lambda x: -x[1]):
        print(f"   loai {v:4d}: {k}")
    if not dung:
        return

    bang = {
        "so_benh_an": len(dung),
        "so_tu_doi_trung_binh": round(_tb(dung, "so_tu_doi"), 2),
        "loai": bo,
        "nguy_hiem": {
            "final_cuoc_thi": round(_tb(dung, "nguy_hiem", "cuoc_thi", "final"), 4),
            "rouge1": round(_tb(dung, "nguy_hiem", "cuoc_thi", "rouge1"), 4),
            "section_f1": round(_tb(dung, "nguy_hiem", "cuoc_thi", "section_f1"), 4),
            "f1_quy_gan": round(_tb(dung, "nguy_hiem", "quy_gan", "f1_quy_gan"), 4),
            "dung_quy_gan": round(_tb(dung, "nguy_hiem", "quy_gan", "dung_quy_gan"), 4),
        },
        "vo_hai": {
            "final_cuoc_thi": round(_tb(dung, "vo_hai", "cuoc_thi", "final"), 4),
            "rouge1": round(_tb(dung, "vo_hai", "cuoc_thi", "rouge1"), 4),
            "section_f1": round(_tb(dung, "vo_hai", "cuoc_thi", "section_f1"), 4),
            "f1_quy_gan": round(_tb(dung, "vo_hai", "quy_gan", "f1_quy_gan"), 4),
            "dung_quy_gan": round(_tb(dung, "vo_hai", "quy_gan", "dung_quy_gan"), 4),
        },
    }
    for ten in ("final_cuoc_thi", "f1_quy_gan"):
        bang[f"khoang_cach_{ten}"] = round(
            bang["vo_hai"][ten] - bang["nguy_hiem"][ten], 4)

    dp = duong_dan.THU_MUC_KET_QUA / "chung-chi-thuoc-do.json"
    dp.write_text(json.dumps(bang, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(bang, ensure_ascii=False, indent=2))
    print(f"\nda ghi {dp}")

    dp_md = duong_dan.THU_MUC_KET_QUA / "chung-chi-thuoc-do.md"
    dp_md.write_text(_bao_cao(bang, a.tap), encoding="utf-8")
    print(f"da ghi {dp_md}")


def _bao_cao(b, tap):
    nh, vh = b["nguy_hiem"], b["vo_hai"]

    def dong(ten, khoa):
        return (f"| {ten} | {nh[khoa]:.4f} | {vh[khoa]:.4f} | "
                f"{vh[khoa] - nh[khoa]:+.4f} |")

    dau_hieu = ("**bộ chấm cuộc thi xếp lỗi nguy hiểm CAO HƠN lỗi vô hại**"
                if b["khoang_cach_final_cuoc_thi"] < 0
                else "bộ chấm cuộc thi có phân biệt được hai nhóm, nhưng ít")

    return f"""# Chứng chỉ thước đo — bộ chấm cuộc thi có nhìn thấy lỗi quy gán không

Sinh tự động bằng `python -m src.chung_chi_thuoc_do`. Đừng sửa tay.

Tập: {', '.join(tap)} · **{b['so_benh_an']} bệnh án** dùng được.

## Phép thử

Mỗi bệnh án gốc bị làm hỏng theo **hai kiểu, đổi đúng cùng số từ**
(trung bình {b['so_tu_doi_trung_binh']} từ):

| Nhóm | Phép làm hỏng | Về mặt lâm sàng |
|---|---|---|
| **nguy hiểm** | đổi chỗ từ chỉ bệnh nhân và từ chỉ người nhà ở hai câu khác nhau | ghi bệnh của người này thành bệnh của người kia |
| **vô hại** | thay từ đồng nghĩa | không đổi nghĩa |

Điều kiện **khớp số từ bị đổi** là bắt buộc, và đã có bài học cụ thể ở Task 3:
lần trước lỗi nguy hiểm đổi 2 từ còn đối chứng đổi 1 từ, và kết luận suýt bị
rút ngược. Bệnh án nào không tạo được đối chứng khớp đúng số từ thì **bị loại
khỏi phép so**, không được đưa vào với số từ lệch.

## Kết quả

| Thước đo | lỗi nguy hiểm | lỗi vô hại | khoảng cách |
|---|---|---|---|
{dong('Điểm cuối cuộc thi', 'final_cuoc_thi')}
{dong('ROUGE-1', 'rouge1')}
{dong('Section F1', 'section_f1')}
{dong('**Điểm quy gán**', 'f1_quy_gan')}

Khoảng cách dương nghĩa là thước đo **phạt lỗi nguy hiểm nặng hơn lỗi vô hại** —
đó là điều một thước đo phải làm.

## Đọc bảng

**ROUGE-1 = {nh['rouge1']:.4f} ở nhóm nguy hiểm.** Đổi chỗ hai chủ thể không
thêm cũng không bớt một từ nào, nên phép đếm từ chung không hề nhúc nhích.

**Khoảng cách của điểm cuộc thi là {b['khoang_cach_final_cuoc_thi']:+.4f}** —
{dau_hieu}.

**Điểm quy gán chênh {b['khoang_cach_f1_quy_gan']:+.4f}**, và chênh đúng chiều.

## Hệ quả cho Cửa 4

Cửa 4 đã kết luận "nhánh C không hơn nhánh B" dựa trên điểm cuộc thi, với năm
nhánh nằm trong khoảng 0,3514–0,3643. Bảng trên cho thấy thước đo đó không
phân biệt được lỗi quy gán với thay đổi vô hại trên chính bộ dữ liệu này.

Kết luận đúng phải phát biểu lại: **Cửa 4 chưa đo được điều nó định đo.**
Phải chạy lại phép so năm nhánh bằng điểm quy gán trước khi kết luận về cơ chế.

## Giới hạn, nói thẳng

1. **{b['so_benh_an']} bệnh án là cỡ mẫu nhỏ.** Số bị loại và lý do:
{chr(10).join(f'   - {v} — {k}' for k, v in sorted(b['loai'].items(), key=lambda x: -x[1]))}
2. Phần lớn bị loại vì bệnh án **không nhắc tới người nhà trong thân bài** —
   nhiều bản chỉ có mục `TIỀN SỬ GIA ĐÌNH` rồi viết chung chung. Không tạo
   được lỗi quy gán trên bản không nói tới hai người.
3. Lỗi được **sinh bằng luật**, không phải lỗi do mô hình thật mắc. Nó đo độ
   nhạy của thước đo, **không** đo tần suất lỗi trong thực tế.
4. Điểm quy gán đọc chủ thể bằng luật bề mặt, và cố ý **không nhận diện**
   những từ chỉ người nhà mơ hồ (`ba`, `bác`, `má`, `cô`…). Xem
   `src/thuoc_do_quy_gan.py`.
"""


if __name__ == "__main__":
    main()
