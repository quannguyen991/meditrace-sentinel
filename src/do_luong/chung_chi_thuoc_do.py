# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Thước đo]
Làm gì   : Kiểm điểm quy gán có đủ nhạy với lỗi đổi chủ thể mà không quá nhạy với đổi từ
           đồng nghĩa, trên bệnh án thật.
Vào → Ra : bệnh án thật các tập (--tap) → bảng so điểm bản đổi chủ thể với bản đổi đồng
           nghĩa, JSON và markdown
Đọc từ   : do_mot_ban() làm hỏng một bệnh án hai kiểu rồi chấm; main() chạy cả tập
Mục lục (các hàm/lớp chính):
  do_mot_ban()        Làm hỏng một bệnh án hai kiểu và chấm cả hai
  hoan_doi_chu_the()  Đổi chỗ từ chỉ bệnh nhân và từ chỉ người nhà
  doi_dong_nghia()    Đổi từ đồng nghĩa cho đúng số từ cần đổi
  so_tu_khac()        Đếm số từ khác nhau giữa hai bản
  main()              Chạy dòng lệnh cấp chứng chỉ cho thước đo
  _bao_cao()          Dựng báo cáo Markdown của chứng chỉ thước đo
Gọi tới  : do_luong/cham_diem, do_luong/thuoc_do_quy_gan, bo_du_lieu/nap_du_lieu,
           he_thong/duong_dan
Tên cũ   : chung_chi_thuoc_do.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chứng chỉ cho thước đo: nó có NHÌN THẤY lỗi quy gán không.

Một thước đo mới không được tin chỉ vì tác giả nói nó tốt. Phải chứng minh hai
điều, và phải chứng minh trên BỆNH ÁN THẬT chứ không phải ví dụ tự viết:

    1. NHẠY  — lỗi nguy hiểm (đổi chủ thể) phải làm điểm sụp.
    2. KHÔNG QUÁ NHẠY — lỗi vô hại (đổi từ đồng nghĩa) phải bị trừ ít hơn HẲN.

Điều 2 là điều dễ quên. Một thước đo phạt mọi thay đổi như nhau thì cũng mù y
hệt ROUGE, chỉ mù theo kiểu khác: nó không phân biệt được *sai* với *khác*.

Và đã có bài học cụ thể ở Task 3: nhóm đối chứng PHẢI KHỚP SỐ TỪ BỊ ĐỔI. Lần
trước đó lệch vì lỗi nguy hiểm đổi 2 từ còn lỗi vô hại đổi 1 từ — kết luận suýt
bị rút ngược. Ở đây điều đó được cải thành điều kiện lọc: bệnh án nào không
tạo được phép đối chứng khớp số từ thì BỊ LOẠI khỏi phép so, và số bị loại
được báo cáo.

    python -m src.do_luong.chung_chi_thuoc_do
"""
import argparse
import io
import json
import re
import sys
import unicodedata

from src.do_luong import cham_diem as cham_diem
from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.he_thong import duong_dan as duong_dan
from src.do_luong import thuoc_do_quy_gan as tdq

# Cặp từ đồng nghĩa dùng cho nhóm đối chứng. Điều kiện chọn:
#   - thật sự đồng nghĩa trong ngữ cảnh bệnh án (không đổi nghĩa lâm sàng)
#   - CẢ HAI vế đều là từ nội dung với cả hai thước đo
#     (nếu một vế là từ đệm của thước đo quy gán thì phép đổi vô hình với nó,
#      và thước đo sẽ ăn điểm một cách không công bằng)
# Cặp (biểu thức tìm, từ thay). Dùng biểu thức chứ không dùng chuỗi vì một số
# từ chỉ đồng nghĩa trong MỘT SỐ ngữ cảnh:
#   "ba ngày" -> "ba hôm"        đúng
#   "ngày hôm qua" -> "hôm hôm qua"  sai — nên có chặn phía sau
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

# CHỈ dùng từ chỉ người MỘT ÂM TIẾT ở cả hai phía.
#
# Ban đầu có cả "Bà ngoại", "Bệnh nhân". Đổi "Trẻ" (1 từ) lấy "Bà ngoại"
# (2 từ) làm mọi token phía sau lệch một ô, và phép đếm `so_tu_khac` báo
# 82 từ bị đổi thay vì 2. Nhóm đối chứng không thể nào khớp được con số đó,
# nên bệnh án bị loại — mất mẫu vì một lỗi kỹ thuật chứ không phải vì dữ liệu.
#
# Giữ bằng số âm tiết thì phép đếm theo vị trí còn đúng, và "đổi 2 từ" của
# nhóm nguy hiểm khớp đúng "đổi 2 từ" của nhóm vô hại.
TU_BN = ("bệnh nhân", "trẻ", "bé", "cháu", "con")
# Bộ sinh dùng cả "vợ", "chồng", "con trai", "con gái" làm chủ thể người
# nhà; thiếu chúng thì số bản có người nhà bị đếm thiếu đi nhiều.
TU_NN = ("bà ngoại", "bà nội", "ông ngoại", "ông nội", "anh trai", "chị gái",
         "em trai", "em gái", "con trai", "con gái", "con dâu", "con rể",
         "người nhà", "gia đình", "bố mẹ", "cha mẹ",
         "mẹ", "bố", "cha", "vợ", "chồng", "dì", "cậu", "chú", "bác")


# ─── _chuan() — Chuẩn hoá Unicode về NFC ──────────────────────────────────────────────
def _chuan(s):
    return unicodedata.normalize("NFC", s or "")


# ─── _tach_tu() — Tách chuỗi thành các từ chữ thường ──────────────────────────────────
def _tach_tu(s):
    return re.findall(r"\w+", _chuan(s).lower(), re.UNICODE)


# ═══ so_tu_khac() — Đếm số từ khác nhau giữa hai bản ══════════════════════════════════
# Căn lệ bằng difflib nên đếm đúng phần thật sự khác, không đếm theo vị trí.
def so_tu_khac(a, b):
    """Số token khác nhau giữa hai bản, tính bằng căn lề (`difflib`).

    Ban đầu đếm theo VỊ TRÍ: ghép hai danh sách token rồi đếm chỗ lệch. Cách đó
    hỏng ngay khi hai từ thay cho nhau có số âm tiết khác nhau — đổi "trẻ"
    (1 từ) lấy "bà ngoại" (2 từ) làm mỗi token phía sau lệch một ô, và phép đếm
    báo 82 từ bị đổi thay vì 3. Hậu quả không phải sai số: bệnh án đó bị LOẠI
    khỏi phép so vì nhóm đối chứng không khớp nổi con số, nên mẫu tụt xuống 5.

    Căn lề lại bằng `SequenceMatcher` thì chỉ đếm đúng phần thật sự khác.
    """
    from difflib import SequenceMatcher
    ta, tb = _tach_tu(a), _tach_tu(b)
    n = 0
    for thao_tac, i1, i2, j1, j2 in SequenceMatcher(None, ta, tb).get_opcodes():
        if thao_tac != "equal":
            n += max(i2 - i1, j2 - j1)
    return n


# ------------------------------------------------------- phép đổi nguy hiểm

# ═══ hoan_doi_chu_the() — Đổi chỗ từ chỉ bệnh nhân và từ chỉ người nhà ════════════════
# Hai từ phải ở hai câu khác nhau; thiếu một bên thì trả None.
def hoan_doi_chu_the(ban):
    """Đổi chỗ từ chỉ BỆNH NHÂN và từ chỉ NGƯỜI NHÀ ở hai câu khác nhau.

    Trả về `None` nếu bệnh án không có đủ cả hai — không thể bịa ra một lỗi
    quy gán trên bản không nói tới người nhà.
    """
    ban = _chuan(ban)
    vi_bn = _tim(ban, TU_BN)
    vi_nn = _tim(ban, TU_NN)
    if vi_bn is None or vi_nn is None:
        return None
    # Hai từ phải nằm ở HAI CÂU khác nhau. Đổi chỗ trong cùng một câu thì câu
    # đó thành vô nghĩa ("Mẹ chưa ghi nhận dị ứng, mẹ dị ứng penicillin"),
    # còn đổi chỗ giữa hai câu mới tạo ra đúng một bệnh án vẫn đọc trôi chảy
    # nhưng gán sai người — chính là lỗi mà dự án đi chặn.
    if _cau_thu_may(ban, vi_bn[0]) == _cau_thu_may(ban, vi_nn[0]):
        return None

    (c1, t1), (c2, t2) = vi_bn, vi_nn
    if c1 > c2:
        (c1, t1), (c2, t2) = (c2, t2), (c1, t1)
    return (ban[:c1] + _theo_hoa(t1, t2) + ban[c1 + len(t1):c2]
            + _theo_hoa(t2, t1) + ban[c2 + len(t2):])


# ═══ vung_than_bai() — Lấy các đoạn không phải dòng tiêu đề mục ═══════════════════════
# Giúp phép đổi không làm hỏng tên mục.
def vung_than_bai(ban):
    """Các đoạn văn bản KHÔNG phải dòng tiêu đề mục, kèm vị trí tuyệt đối.

    Bắt buộc phải có. Tên mục "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" có chứa chữ
    "gia đình"; tìm không phân biệt hoa thường sẽ khớp vào chính TIÊU ĐỀ và
    phép hoán đổi sẽ phá tên mục. Lúc đó Section F1 tụt từ 1,00 xuống 0,69 —
    nhưng tụt vì CẤU TRÚC vỡ, không phải vì quy gán sai.

    Đó là một phép thử bị nhiễm: nó làm bộ chấm cuộc thi trông như thể có
    nhìn thấy lỗi quy gán, trong khi thực ra nó chỉ nhìn thấy một cái tiêu đề
    hỏng. Kết luận rút ra từ đó sẽ có lợi cho dự án một cách không thật.
    """
    ra, vi = [], 0
    for dong in _chuan(ban).split("\n"):
        if not _la_tieu_de(dong):
            ra.append((vi, vi + len(dong)))
        vi += len(dong) + 1
    return ra


# ─── _la_tieu_de() — Nhận biết dòng là tiêu đề mục viết hoa ───────────────────────────
def _la_tieu_de(dong):
    s = dong.strip()
    return bool(s) and len(s) <= 70 and s == s.upper() and not s.endswith(".")


# ─── _trong_than_bai() — Xét vị trí có nằm trong vùng thân bài không ──────────────────
def _trong_than_bai(vi_tri, vung):
    return any(d <= vi_tri < c for d, c in vung)


# ─── _tim() — Tìm vị trí xuất hiện đầu tiên của một trong các từ ──────────────────────
# Chỉ xét phần thân bài.
def _tim(ban, tu_list):
    """Vị trí xuất hiện đầu tiên của bất kỳ từ nào trong `tu_list`,
    CHỈ xét phần thân bài."""
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


# ─── _theo_hoa() — Giữ kiểu viết hoa khi thay từ ──────────────────────────────────────
def _theo_hoa(cu, moi):
    """Giữ kiểu viết hoa của từ cũ khi thay bằng từ mới."""
    return moi.capitalize() if cu[:1].isupper() else moi


# ─── _cau_thu_may() — Đếm số câu đứng trước một vị trí ────────────────────────────────
def _cau_thu_may(ban, vi_tri):
    return len(re.findall(r"[.;!?\n]", ban[:vi_tri]))


# --------------------------------------------------------- phép đổi vô hại

# ═══ doi_dong_nghia() — Đổi từ đồng nghĩa cho đúng số từ cần đổi ══════════════════════
# Từng lần một, không vượt số cần đạt; không đạt đúng thì trả None.
def doi_dong_nghia(ban, so_tu_can_doi):
    """Đổi từ đồng nghĩa cho đến khi số từ bị đổi ĐÚNG bằng `so_tu_can_doi`.

    Trả `None` nếu không đạt đúng con số — tốt hơn là loại mẫu đó khỏi phép so
    còn hơn là so hai nhóm có số từ bị đổi khác nhau.
    """
    ban = _chuan(ban)
    ra = ban
    # Thay TỪNG lần xuất hiện một, đếm lại sau mỗi lần. Thay hết một cặp rồi
    # mới đếm thì dễ vượt quá con số cần đạt và không lùi lại được.
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
                # Chỉ nhận nếu tiến thêm MÀ KHÔNG vượt quá con số cần đạt.
                # Không có vế này thì một phép đổi hai từ sẽ nhảy từ 3 lên 5 và
                # không bao giờ lùi lại được — bệnh án bị loại oan.
                if so_tu_khac(ra, ban) < moi_khac <= so_tu_can_doi:
                    ra, tien_bo = thu, True
                    break
    return ra if so_tu_khac(ra, ban) == so_tu_can_doi else None


# ------------------------------------------------------------------- chạy

# ═══ do_mot_ban() — Làm hỏng một bệnh án hai kiểu và chấm cả hai ══════════════════════
# Kiểu nguy hiểm đổi chủ thể, kiểu vô hại đổi đồng nghĩa, cùng số từ; chấm điểm cuộc thi
# và quy gán.
def do_mot_ban(goc):
    """Trả về dict số liệu cho một bệnh án, hoặc None nếu không dùng được."""
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


# ─── _tb() — Tính trung bình một giá trị lồng nhau ────────────────────────────────────
def _tb(ds, *duong_dan_khoa):
    lay = []
    for d in ds:
        v = d
        for k in duong_dan_khoa:
            v = v[k]
        lay.append(v)
    return sum(lay) / len(lay) if lay else 0.0


# ═══ main() — Chạy dòng lệnh cấp chứng chỉ cho thước đo ═══════════════════════════════
# Chặn tập khoá, chạy trên các tập, ghi JSON và báo cáo.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", nargs="*",
                    default=["phat_trien", "kiem_tra_chung", "train"])
    ap.add_argument("--toi-da", type=int, default=400)
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()

    # Chốt bảo vệ Cửa 5. `kiem_tra_cuoi` chỉ được mở SAU khi khoá thiết kế; mở
    # sớm là hỏng toàn bộ phần đánh giá, và hỏng một cách không lấy lại được.
    # Một dòng `--tap kiem_tra_cuoi` gõ nhầm là đủ. Chặn ở đây chứ không tin
    # vào việc nhớ.
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


# ─── _bao_cao() — Dựng báo cáo Markdown của chứng chỉ thước đo ────────────────────────
# So điểm lỗi nguy hiểm với lỗi vô hại ở cả bộ chấm cuộc thi và điểm quy gán.
def _bao_cao(b, tap):
    nh, vh = b["nguy_hiem"], b["vo_hai"]

    def dong(ten, khoa):
        return (f"| {ten} | {nh[khoa]:.4f} | {vh[khoa]:.4f} | "
                f"{vh[khoa] - nh[khoa]:+.4f} |")

    dau_hieu = ("**bộ chấm cuộc thi xếp lỗi nguy hiểm CAO HƠN lỗi vô hại**"
                if b["khoang_cach_final_cuoc_thi"] < 0
                else "bộ chấm cuộc thi có phân biệt được hai nhóm, nhưng ít")

    return f"""# Chứng chỉ thước đo — bộ chấm cuộc thi có nhìn thấy lỗi quy gán không

Sinh tự động bằng `python -m src.do_luong.chung_chi_thuoc_do`. Đừng sửa tay.

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
   `src/do_luong/thuoc_do_quy_gan.py`.
"""


if __name__ == "__main__":
    main()
