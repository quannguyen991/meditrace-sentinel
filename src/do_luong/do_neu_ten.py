# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo bản nháp có nêu tên người (mẹ, bố...) cho các câu thuộc mục không phải của
           bệnh nhân hay chỉ xếp đúng mục mà quên nêu người.
Vào → Ra : tệp bản nháp từng nhánh (--tep TEN=DUONG_DAN), mục cần xét (--muc) → bảng tỉ lệ
           câu nêu tên theo nhánh
Đọc từ   : co_neu_ten() kiểm câu có mở đầu bằng từ chỉ người; cham() tính tỉ lệ trong mục
Mục lục (các hàm/lớp chính):
  cau_trong_muc()  Lấy các câu nằm trong một mục của bản nháp
  co_neu_ten()     Kiểm tra câu có mở đầu bằng từ chỉ người không
  cham()           Tính tỉ lệ câu nêu tên người trong mục người khác
  main()           Chạy dòng lệnh in bảng tỉ lệ nêu tên theo nhánh
Gọi tới  : duong_ong/b5_viet_ban_nhap
Tên cũ   : do_neu_ten.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bản nháp có NÊU TÊN NGƯỜI cho mệnh đề không phải của bệnh nhân không.

VÌ SAO CẦN MỘT THƯỚC ĐO RIÊNG CHO VIỆC NÀY — đo được 11/09/2026, và nó là bằng
chứng mạnh nhất của cả dự án về chuyện thước đo đo thứ khác với thứ nó khai.

Mục TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI của bản nháp, trên tập phát triển thế hệ 2:

    bản tham chiếu      22 câu, 22 nêu tên người   (100%)
    nhánh B, C, D       50, 50, 53 câu, **0 nêu tên người**   (0%)

Một bác sĩ đọc `TIEN SU GIA DINH VA XA HOI / roi loan mo mau` không biết AI bị rối
loạn mỡ máu. Bản nháp đó không dùng được.

VÀ `f1_quy_gan` KHÔNG THẤY GÌ. Sau khi sửa để bản nháp nêu tên (0% -> 100%):

    B trước sửa   0,8032
    B sau sửa     0,8032      hiệu 0,0000, KTC [0,0000; 0,0000]

Đổi đúng bằng không. Lý do: `thuoc_do_quy_gan._chu_the_cua_cau` suy chủ thể từ TÊN
MỤC khi câu không có từ chỉ người (`MUC_NGUOI_NHA = ("GIA DINH",)`). Nên một câu
KHÔNG nêu tên nằm trong mục gia đình vẫn được chấm là "người nhà" — đúng 100% ở
tầng 4.

    Con số 100% ở tầng 4 là điểm của việc XẾP ĐÚNG MỤC, không phải điểm của việc
    GÁN ĐÚNG NGƯỜI.

ĐÂY LÀ LẦN THỨ BA trong hai ngày:

    ROUGE         mù trước lo~i đổi chủ thể      0,9799 so với 0,9661
    f1_quy_gan    bị tăng để chi phối            xếp regex trên đường ống
    f1_quy_gan    mù trước việc NÊU TÊN NGƯỜI    0% -> 100% làm điểm đổi 0,0000

Hai lần đầu là chuyện đo lớn. Lần này là chuyện đo KHÔNG HỀ đo.

GIỚI HẠN CỦA CHÍNH THƯỚC ĐO NÀY: nó kiểm sự CÓ MẶT của một từ chỉ người ở đầu câu,
không kiểm từ đó có ĐÚNG NGƯỜI không. Một bản nháp ghi "bố rối loạn mỡ máu" trong
khi đáp án là "mẹ" sẽ đạt ở đây. Nên đọc nó cùng `do_tang_quy_gan`, không thay thế.

    python -m src.do_luong.do_neu_ten --tep B=data/ra_B_viet_phat_trien_th2.jsonl
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an

# Từ chỉ người đứng ở ĐẦU câu trong mục tiền sử gia đình. Lấy từ chính bộ sinh
# để không trôi: `nl.NGUOI_NHA` là danh sách vai người nhà thật.
VAI_NGUOI = ("mẹ", "bố", "ba", "bà", "ông", "chị", "anh", "cô", "dì", "chú",
             "bác", "vợ", "chồng", "con", "em", "cháu", "người nhà", "gia đình")

MUC_NGUOI_KHAC = sinh_benh_an.MUC_NGUOI_KHAC


# ─── _la_tieu_de() — Nhận biết dòng tiêu đề mục viết hoa toàn bộ ──────────────────────
def _la_tieu_de(dong):
    d = dong.strip()
    return bool(d) and d == d.upper() and len(d) > 3


# ═══ cau_trong_muc() — Lấy các câu nằm trong một mục của bản nháp ═════════════════════
# Tách theo dấu câu vì bản nháp nối nhiều mệnh đề trên một dòng.
def cau_trong_muc(van_ban, muc=MUC_NGUOI_KHAC):
    """-> danh sách câu nằm trong `muc`.

    Tách theo dấu câu chứ không theo dòng: `sinh_benh_an` nối nhiều mệnh đề vào
    một dòng bằng dấu chấm.
    """
    ra = []
    trong = False
    for dong in str(van_ban or "").split("\n"):
        d = dong.strip()
        if d == muc:
            trong = True
            continue
        if _la_tieu_de(d):
            trong = False
            continue
        if trong and d:
            for cau in re.split(r"(?<=[.;])\s+", d):
                cau = cau.strip().lstrip("- ").strip()
                if cau:
                    ra.append(cau)
    return ra


# ═══ co_neu_ten() — Kiểm tra câu có mở đầu bằng từ chỉ người không ════════════════════
# Chỉ xét đầu câu, vì từ chỉ người giữa câu thường là nội dung chứ không phải nhãn chủ
# thể.
def co_neu_ten(cau):
    """Câu có bắt đầu bằng một từ chỉ người không.

    Chỉ xét ĐẦU câu: `sinh_benh_an.dien_dat` đặt tên ở đầu theo dạng "<tên>: ",
    và một từ chỉ người nằm giữa câu thường là một phần nội dung
    ("dị ứng thuốc của mẹ cho") chứ không phải nhãn chủ thể.
    """
    dau = str(cau or "").strip().lower().lstrip("- ").strip()
    return any(dau.startswith(v) for v in VAI_NGUOI)


# ═══ cham() — Tính tỉ lệ câu nêu tên người trong mục người khác ═══════════════════════
# Trả số câu, số câu có nêu tên và tỉ lệ; không có câu thì tỉ lệ là NaN.
def cham(ket_qua, khoa="du_doan", muc=MUC_NGUOI_KHAC):
    """-> {so_cau, so_neu_ten, ty_le}."""
    co = tong = 0
    for x in ket_qua:
        for cau in cau_trong_muc(x.get(khoa), muc):
            tong += 1
            co += 1 if co_neu_ten(cau) else 0
    return {"so_cau": tong, "so_neu_ten": co,
            "ty_le": co / tong if tong else float("nan")}


# ═══ main() — Chạy dòng lệnh in bảng tỉ lệ nêu tên theo nhánh ═════════════════════════
# Dòng đầu là bản tham chiếu, sau đó từng nhánh.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", nargs="+", required=True, metavar="TEN=DUONG_DAN")
    ap.add_argument("--muc", default=MUC_NGUOI_KHAC)
    a = ap.parse_args()

    print(f"Muc `{a.muc}` — cau co neu ten nguoi hay khong\n")
    print(f"| Nhánh | Số câu | Nêu tên | Tỷ lệ |")
    print(f"|---|---|---|---|")
    dau = True
    for x in a.tep:
        ten, _, duong = x.partition("=")
        p = Path(duong)
        if not p.exists():
            print(f"| `{ten}` | — | — | không có tệp |")
            continue
        kq = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        if dau:
            t = cham(kq, "tham_chieu", a.muc)
            print(f"| *tham chiếu* | {t['so_cau']} | {t['so_neu_ten']} | "
                  f"{t['ty_le']:.0%} |")
            dau = False
        d = cham(kq, "du_doan", a.muc)
        ty = "—" if d["so_cau"] == 0 else f"{d['ty_le']:.0%}"
        print(f"| `{ten}` | {d['so_cau']} | {d['so_neu_ten']} | {ty} |")


if __name__ == "__main__":
    main()
