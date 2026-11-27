# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Dữ liệu ngoài]
Làm gì   : Đọc bộ hội thoại người thật ghi tay, kiểm lỗi định dạng rồi đổi sang định dạng
           của bộ sinh để đo.
Vào → Ra : thư mục tệp ghi tay → danh sách ca đúng định dạng bộ sinh; báo LoiDinhDang nếu
           tệp sai
Đọc từ   : gom() đọc cả thư mục; doc_mot_tep() đọc một tệp; kiem() soát lỗi; doi_dinh_dang()
           đổi sang định dạng ca
Mục lục (các hàm/lớp chính):
  gom()              Gom các tệp .txt trong thư mục thành bản ghi
  doc_mot_tep()      Đọc một tệp ghi tay thành cấu trúc thô
  kiem()             Kiểm tệp đã đọc, trả danh sách lỗi
  doi_dinh_dang()    Đổi bản đọc thô sang bản ghi cùng dạng bộ sinh
  main()             Nạp thư mục người thật, ghi JSONL và in thống kê
  class LoiDinhDang  Lỗi trong tệp ghi tay, nêu rõ dòng nào
Gọi tới  : do_luong/khoang_tin_cay, do_luong/thuoc_do_quy_gan, duong_ong/b5_viet_ban_nhap
Tên cũ   : bo_nguoi_that.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nạp bộ hội thoại NGƯỜI THẬT ghi tay, kiểm, và đổi sang định dạng của bộ sinh.

VÌ SAO CẦN BỘ NÀY. Cả ba tập — train, phat_trien, kiem_tra_cuoi — đều đo chính
bộ sinh của dự án sinh ra. Cách chia tập thì đúng (cắt theo khuôn bệnh, 45/8/7,
xem `tach_tap_viet`), nhưng "mở tập kiểm tra cuối một lần" không phá được vòng
tròn: 7 khuôn giữ lại đo được "khuôn chưa thấy", không đo được "NGUỒN NGÔN NGỮ
chưa thấy".

Và Task 42 đo được chỗ hỏng cụ thể: **99,1% mệnh đề đáp án có nguyên văn từ nội
dung trong hội thoại**. Một đối chứng regex không mô hình đã hơn cả đường ống
đầy đủ trên mọi tầng. Tầng ngữ vực (Task 43) hạ được con số đó xuống 92,0% —
thấp hơn nhưng chưa đủ, và trần của nó là thật.

Người thật không nói như bộ sinh. Đó là thứ duy nhất phá được phép đồng nhất
hội thoại -> bản nháp.

AI VIẾT HỘI THOẠI — và đây là ràng buộc, không phải tuỳ chọn.

    Hội thoại PHẢI do NGƯỜI đóng vai và gợi lại. KHÔNG được sinh bằng mô hình
    ngôn ngữ, kể cả để làm tập ĐO.

Lý do không phải hình thức: một mô hình ngôn ngữ viết hội thoại SẠCH hơn người
nói thật — nó ghi rõ chủ ngữ ở hầu hết các lượt, dùng thuật ngữ thay vì lời dân
thường, và không bỏ lửng câu. Dùng mô hình để sinh tập đo chính là làm lại đúng
cái lỗi mà bộ này được dựng ra để chữa, chỉ khác là lần này không còn chỗ nào
để phát hiện.

Tệp này KHÔNG sinh hội thoại. Nó nạp thứ người đã ghi, kiểm, và báo lại.

ĐỊNH DẠNG — cố tình để gõ được bằng Notepad, không cần công cụ:

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

Cột thứ năm và sáu là tuỳ chọn: `phu_dinh` (có/không) và `tinh_huong`.

    python -m src.bo_du_lieu.nap_bo_nguoi_that --vao data/nguoi_that --ra data/nguoi_that.jsonl
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

# Tiêu đề các khối. Viết hoa chữ cái đầu hay không đều nhận.
KHOI = {"người": "nguoi", "hội thoại": "hoi_thoai", "đáp án": "dap_an"}


# ═══ class LoiDinhDang — Lỗi trong tệp ghi tay, nêu rõ dòng nào ═══════════════════════
# Thông báo phải chỉ dòng vì người sửa là người gõ tay.
class LoiDinhDang(Exception):
    """Lỗi trong tệp ghi tay. Thông báo phải chỉ rõ DÒNG NÀO, vì người sửa nó
    là người gõ Notepad chứ không phải lập trình viên."""


# ─── _khoi_cua() — Nhận biết dòng mở đầu một khối trong tệp ───────────────────────────
# Dòng bắt đầu bằng ## và tên khối; tên lạ thì báo lỗi.
def _khoi_cua(dong):
    m = re.match(r"^##\s+(.+?)\s*$", dong)
    if not m:
        return None
    ten = m.group(1).strip().lower()
    if ten not in KHOI:
        raise LoiDinhDang(f"khoi khong biet: {m.group(1)!r}; "
                          f"chi co {', '.join(KHOI)}")
    return KHOI[ten]


# ═══ doc_mot_tep() — Đọc một tệp ghi tay thành cấu trúc thô ═══════════════════════════
# Trả id, người, lượt và đáp án thô; lỗi định dạng kèm số dòng.
def doc_mot_tep(duong_dan):
    """-> {id, nguoi, luot, dap_an_tho}. Ném `LoiDinhDang` kèm số dòng."""
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


# ═══ kiem() — Kiểm tệp đã đọc, trả danh sách lỗi ══════════════════════════════════════
# Rỗng là đạt; chỉ kiểm không tự sửa, vì tự đoán bù là bịa thông tin lâm sàng.
def kiem(tho, ten_tep=""):
    """-> danh sách lỗi (chuỗi). Rỗng là đạt.

    Kiểm chứ không tự sửa: một tệp ghi tay có lỗi thì NGƯỜI phải sửa, vì chỉ
    người đó biết ý mình là gì. Tự đoán bù ở đây là bịa thông tin lâm sàng.
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


# ═══ doi_dinh_dang() — Đổi bản đọc thô sang bản ghi cùng dạng bộ sinh ═════════════════
# Nhờ vậy các công cụ đo chạy ngay trên bộ người thật.
def doi_dinh_dang(tho):
    """-> bản ghi cùng hình với bộ sinh: {id, input, output, dap_an, ...}.

    Đổi sang ĐÚNG hình đó là cả ý nghĩa của tệp này: mọi công cụ đã có —
    `sai_so`, `do_tang_quy_gan`, `do_dac`, `nhanh` — chạy được ngay trên bộ
    người thật mà không sửa một dòng nào.
    """
    from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an

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

    # Bản nháp tham chiếu sinh từ đáp án bằng CHÍNH khâu sinh của dự án, để nó
    # cùng định dạng với bộ sinh — không viết tay, vì viết tay thì hai bộ lệch
    # định dạng và mọi chênh lệch đo được sẽ lẫn lộn nguyên nhân.
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


# ─── _phan_tang() — Đếm bốn tầng quy gán của một bản ghi ──────────────────────────────
# Dùng cùng định nghĩa với module sai số.
def _phan_tang(ban_ghi):
    """-> Counter bốn tầng, dùng chung định nghĩa với `sai_so`."""
    from src.do_luong import khoang_tin_cay as sai_so
    return sai_so.tang_menh_de(ban_ghi)


# ═══ gom() — Gom các tệp .txt trong thư mục thành bản ghi ═════════════════════════════
# Trả danh sách bản ghi và danh sách lỗi; tệp lỗi bị bỏ.
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


# ═══ main() — Nạp thư mục người thật, ghi JSONL và in thống kê ════════════════════════
# In tỷ lệ tầng quy gán và tỷ lệ mệnh đề phủ nguyên văn 100%.
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

    # Đo CHÍNH cái mà bộ này được lập ra để phá: tỷ lệ sao chép nguyên văn.
    from src.do_luong import thuoc_do_quy_gan as t
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
