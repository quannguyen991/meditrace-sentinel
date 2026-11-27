# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Bộ chấm]
Làm gì   : Chấm bốn bộ thử thách trực tiếp trên văn bản bản nháp, để nhánh A (văn xuôi,
           không có bảng mệnh đề) cũng được so công bằng.
Vào → Ra : tệp bản nháp từng nhánh + bộ thử thách (--tap, --nhanh) → tỉ lệ đúng từng bộ, ghi
           JSON
Đọc từ   : cham_tap() chấm một bộ thử thách; dung_doi_chu_the() là phép chấm bộ đổi chủ thể
Mục lục (các hàm/lớp chính):
  cham_tap()          Chấm một tập thuộc đúng một bộ thử thách
  dung_doi_chu_the()  Chấm bộ đổi chủ thể: ý dị ứng phải trùng tham chiếu
  dung_dinh_chinh()   Chấm bộ đính chính: ý bệnh sử liên quan phải đúng
  tach_muc()          Tách văn bản thành các mục và dòng nội dung
  cac_y()             Đổi dòng nội dung thành tập ý đã chuẩn hoá
  main()              Chạy dòng lệnh chấm bộ thử thách cho các nhánh
Gọi tới  : do_luong/chuan_dinh_dang, bo_du_lieu/nap_du_lieu, bo_du_lieu/sinh_hoi_thoai_viet,
           duong_ong/b5_viet_ban_nhap, he_thong/duong_dan
Tên cũ   : cham_muc_thach_thuc.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chấm bốn bộ thách thức TRÊN VĂN BẢN, áp NHƯ NHAU cho mọi nhánh — kể cả nhánh A.

VÌ SAO CÓ TỆP NÀY (15/09/2026).

Mỗi hàm chấm thách thức trong `cham_he_thong` đọc `r["phat_bieu"]` — bảng mệnh đề
của đường ống. Nhánh A sinh thẳng văn xuôi, không có bảng đó, nên A KHÔNG CHẤM
ĐƯỢC trên chính các bộ được dùng ra để so A với đường ống. Mà đó lại là câu hỏi
nghiên cứu. Còn thước đo đầu-cuối (ROUGE, F1 mục) thì chấm được A — và cho A
0,9935 trên tập phát triển, vì A học thuộc NGỮ PHÁP viết của bộ sinh: 36/60 bản
nháp trùng khít từng ký tự với bản tham chiếu. Một thước đo mà A đạt 0,99 thì
không còn chỗ nào để phân biệt ai hiểu chủ thể với ai chép khuôn.

ĐIỀU LÀM PHÉP CHẤM NÀY CÔNG BẰNG: bản tham chiếu của bộ sinh mã hoá ĐÚNG điều
từng bộ đo.

  doi_chu_the  hai bản của cặp khác nhau ĐÚNG ở mục DỊ ỨNG và TIỀN SỬ GIA ĐÌNH
  dinh_chinh   trạng thái cuối hiện trong mục BỆNH SỬ: bản đúng, "chưa rõ X hay
               Y" khi mâu thuẫn, cả hai mốc khi diễn biến
  phuong_ngu   hai bản tham chiếu của cặp GIỐNG HỆT nhau
  nhieu_asr    như trên

Nên đối chiếu từng MỤC VĂN BẢN của bản nháp với bản tham chiếu, bằng CÙNG một hàm
cho mọi nhánh, là phép so sánh cân. Không cần bảng mệnh đề.

CHỈ SO CÁC Ý LIÊN QUAN, KHÔNG SO CẢ MỤC. Đo trên ca `dch_001`: nhánh A xử lý mâu
thuẫn ĐÚNG ("sốt (chưa rõ ba hôm hay mấy hôm nay)") nhưng viết "mệt mỏi" thay vì
"mệt" ở một ý khác trong cùng mục. So cả mục thì ca đó bị chấm SAI OAN — và phép
đo lúc đó đo "viết giống khuôn" chứ không đo "giữ đúng trạng thái". Nên:

  doi_chu_the  chỉ các ý có chữ "dị ứng"
  dinh_chinh   chỉ các ý chứa nội dung của mệnh đề đáp án CÓ quan hệ

    python -m src.do_luong.cham_muc_thach_thuc --tap thach_thuc_doi_chu_the_phat_trien \\
        --nhanh A B C C_khoa C_khoa_hoi
"""
import argparse
import io
import json
import re
import sys
import unicodedata
from collections import defaultdict

from src.do_luong import chuan_dinh_dang as chuan_dinh_dang
from src.he_thong import duong_dan as duong_dan
from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
from src.bo_du_lieu import sinh_hoi_thoai_viet as sh

MUC_THAN = tuple(sh.MUC)
MUC_PHU = tuple(sinh_benh_an.MUC_PHU_TAT_CA)

# Bản nào của cặp là bản BỊ LÀM KHÓ. Hai bộ sinh đặt nhãn NGƯỢC nhau, và nhầm chỗ
# này thì con số "phương ngữ làm giảm độ chính xác" đổi dấu.
#   `thach_thuc.cap_phuong_ngu`: bản A CÓ từ phương ngữ, bản B tắt tầng vùng
#   `thach_thuc.cap_nhieu_asr` : bản A SẠCH, bản B đã làm nhiễu
BAN_BI_LAM_KHO = {"phuong_ngu": "A", "nhieu_asr": "B"}


# ─── _chuan() — Chuẩn hoá một chuỗi: NFC, chữ thường, bỏ dấu cuối ─────────────────────
def _chuan(s):
    s = unicodedata.normalize("NFC", s or "").lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s.strip(" .;:,")


# ─── _bo_cach_viet() — Bỏ khác biệt thuần cách viết giữa hai bản ──────────────────────
# Bỏ tiền tố bệnh nhân và dấu hai chấm sau tên người; giữ nguyên tên người.
def _bo_cach_viet(y):
    """Bỏ những khác biệt THUẦN CÁCH VIẾT giữa bộ sinh và khâu dựng bản nháp.

    Đo 15/09/2026 trên đầu ra thật, bản đầu của tệp này chưa có hàm này và chấm C
    0/40 cặp đổi chủ thể trong khi bộ chấm mệnh đề cho 28/40:
      - tham chiếu viết "bệnh nhân đau thượng vị (...)", đường ống viết "đau thượng
        vị (...)" — tiền tố chủ ngữ không mang thông tin
      - tham chiếu viết "bố dị ứng nong ong", đường ống viết "bố: dị ứng nong ong"
    Cả hai là định dạng. Tên NGƯỜI thì giữ nguyên: "bà ngoại: dị ứng…" đổi thành
    "bà ngoại dị ứng…" vẫn khác "bố dị ứng…", và phải khác.
    """
    y = re.sub(r"^bệnh nhân\s+", "", y)
    y = re.sub(r"^([^:]{1,20}):\s*", r"\1 ", y)
    return y


# ─── _bo_y_bi_bao_ham() — Bỏ ý trơn khi đã có cùng ý kèm mốc thời gian ────────────────
# Nhắc lại không mốc là lặp, không phải sai trạng thái.
def _bo_y_bi_bao_ham(tap_y):
    """Bỏ ý trọn "X" khi đã có "X (mốc)". Một lần nhắc lại không mốc là LẶP (đếm ở
    loại `trung_lap` của bộ chấm mệnh đề), không phải sai trạng thái."""
    co_moc = {re.sub(r"\s*\(.*\)$", "", y) for y in tap_y if y.endswith(")")}
    return {y for y in tap_y if y.endswith(")") or y not in co_moc}


# ═══ tach_muc() — Tách văn bản thành các mục và dòng nội dung ═════════════════════════
# Bỏ mục phụ vì bản tham chiếu không có.
def tach_muc(van_ban):
    """Văn bản -> {tên mục: [dòng nội dung]}. Bỏ hai mục phụ vì bản tham chiếu
    không có chúng — để chúng lại là phạt đường ống vì một mục nó tự đặt ra."""
    van = chuan_dinh_dang.chuan_hoa(van_ban)
    ra, dang = defaultdict(list), None
    for dong in van.split("\n"):
        t = dong.strip()
        if not t:
            continue
        if t in MUC_THAN or t in MUC_PHU:
            dang = t
            continue
        if dang and dang not in MUC_PHU:
            ra[dang].append(t)
    return dict(ra)


# ═══ dong_muc_phu() — Lấy các dòng dưới mục CẦN XÁC NHẬN ══════════════════════════════
# Là nơi đường ống đẩy thông tin chưa giải quyết.
def dong_muc_phu(van_ban):
    """Các dòng dưới mục CẦN XÁC NHẬN — nơi đường ống đưa thông tin chưa giải quyết."""
    van = chuan_dinh_dang.chuan_hoa(van_ban)
    ra, dang = [], False
    for dong in van.split("\n"):
        s = dong.strip()
        if not s:
            continue
        if s in MUC_THAN or s in MUC_PHU:
            dang = s == sinh_benh_an.MUC_PHU
            continue
        if dang:
            ra.append(_chuan(s))
    return ra


# ═══ cac_y() — Đổi dòng nội dung thành tập ý đã chuẩn hoá ═════════════════════════════
# Tách ở dấu chấm phẩy và hết câu; dùng tập vì thứ tự không quan trọng.
def cac_y(dong_noi_dung):
    """Các dòng của một mục -> tập các Ý đã chuẩn hoá (tách ở ';' và hết câu).

    Tập chứ không phải danh sách: thứ tự các ý trong một mục không phải điều bộ
    thách thức nào đó.
    """
    ra = set()
    for dong in dong_noi_dung:
        for manh in re.split(r";|\.(?=\s|$)", dong):
            c = _bo_cach_viet(_chuan(manh))
            if c:
                ra.add(c)
    return ra


# ─── _y_muc() — Lấy tập ý của một mục, có thể lọc ─────────────────────────────────────
def _y_muc(van_ban, muc, loc=None):
    y = cac_y(tach_muc(van_ban).get(muc, []))
    return {x for x in y if loc(x)} if loc else y


# ═══ dung_doi_chu_the() — Chấm bộ đổi chủ thể: ý dị ứng phải trùng tham chiếu ═════════
# So ở mục DỊ ỨNG và mục TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI.
# ------------------------------------------------------------ từng bộ thách thức
def dung_doi_chu_the(ca, du_doan):
    """Mỗi ý "dị ứng" ở mục DỊ ỨNG và ở mục TIỀN SỬ GIA ĐÌNH phải trùng tham chiếu."""
    co_di_ung = lambda y: "dị ứng" in y
    return all(
        _y_muc(du_doan, m, co_di_ung) == _y_muc(ca["output"], m, co_di_ung)
        for m in ("DỊ ỨNG", "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"))


# ─── _noi_dung_lien_quan() — Lấy nội dung các mệnh đề có quan hệ trong đáp án ─────────
def _noi_dung_lien_quan(ca):
    da = ca["dap_an"]
    chi_so = {i for i, d in enumerate(da) if d.get("quan_he")} | \
             {d.get("quan_he_voi") for d in da if d.get("quan_he")}
    return {_chuan(da[i]["noi_dung"]) for i in chi_so
            if isinstance(i, int) and 0 <= i < len(da)}


# ═══ dung_dinh_chinh() — Chấm bộ đính chính: ý bệnh sử liên quan phải đúng ════════════
# Với mâu thuẫn hoặc hai nguồn, đúng khi nêu rõ chưa rõ trong thân hoặc ở mục phụ.
def dung_dinh_chinh(ca, du_doan):
    """Các ý ở mục BỆNH SỬ chứa nội dung của mệnh đề CÓ quan hệ phải trùng tham chiếu.

    Lọc bằng nội dung đáp án thay vì so cả mục — xem giải thích ở đầu tệp.
    """
    nd = _noi_dung_lien_quan(ca)
    if not nd:
        return None
    m = "BỆNH SỬ HIỆN TẠI"

    # MÂU THUẪN và HAI NGUỒN: không ai sửa ai, nên không có bản đúng. Bản tham chiếu
    # viết "(chưa rõ X hay Y)" trong thân; đường ống theo chính sách của nó đưa cả hai
    # xuống CẦN XÁC NHẬN. Cả hai đều đúng về lâm sàng. Chấm theo ĐIỀU CÓ HẠI thay vì
    # theo cách viết của bộ sinh: SAI khi thân ghi hai mốc như hai sự thật, hoặc khi
    # mâu thuẫn biến mất không để lại dấu vết.
    if ca.get("bay_chinh") in ("mau_thuan", "nguon_khac_nhau"):
        moc = {_chuan(d["moc_thoi_gian"]) for d in ca["dap_an"]
               if d.get("trang_thai") == "chưa giải quyết" and d.get("moc_thoi_gian")}
        if len(moc) >= 2:
            than = cac_y(tach_muc(du_doan).get(m, []))
            hai_su_that = sum(any(f"({x})" in y for y in than) for x in moc) >= 2
            neu_trong_than = any("chưa rõ" in y and all(x in y for x in moc) for y in than)
            phu = dong_muc_phu(du_doan)
            neu_o_phu = all(any(x in y for y in phu) for x in moc)
            return (not hai_su_that) and (neu_trong_than or neu_o_phu)

    lien_quan = lambda y: any(n and n in y for n in nd)
    return (_bo_y_bi_bao_ham(_y_muc(du_doan, m, lien_quan))
            == _bo_y_bi_bao_ham(_y_muc(ca["output"], m, lien_quan)))


# ═══ than_ban_nhap() — Gom mọi ý của mục thân kèm tên mục ═════════════════════════════
# Dùng để so hai bản của một cặp.
def than_ban_nhap(du_doan):
    """Mỗi ý ở mỗi mục thân, gắn tên mục — để so hai bản của một cặp với nhau."""
    return frozenset((m, y) for m, dong in tach_muc(du_doan).items()
                     if m in MUC_THAN for y in cac_y(dong))


# ═══ cham_tap() — Chấm một tập thuộc đúng một bộ thử thách ════════════════════════════
# Tập chỉ được chứa một loại thử thách; trả số đúng và số ca, chia theo bẫy hoặc theo
# cặp.
# ------------------------------------------------------------------ tổng hợp tập
def cham_tap(cac_ca, ket_qua):
    loai = {ca.get("thach_thuc") for ca in cac_ca} - {None}
    if len(loai) != 1:
        raise ValueError(f"tap phai la MOT bo thach thuc, gap: {loai}")
    loai = loai.pop()

    if loai == "dinh_chinh":
        theo_bay = defaultdict(lambda: [0, 0])
        for ca in cac_ca:
            r = ket_qua.get(ca["id"])
            d = dung_dinh_chinh(ca, r["du_doan"]) if r else False
            if d is None:
                continue
            t = theo_bay[ca.get("bay_chinh")]
            t[0] += bool(d)
            t[1] += 1
        return {"thach_thuc": loai,
                "dung": sum(v[0] for v in theo_bay.values()),
                "so_ca": sum(v[1] for v in theo_bay.values()),
                "theo_bay": {b: f"{d}/{n}" for b, (d, n) in sorted(theo_bay.items())}}

    cap = defaultdict(dict)
    for ca in cac_ca:
        r = ket_qua.get(ca["id"])
        cap[ca["cap"]][ca["bien_the"]] = (ca, r)
    du = [v for v in cap.values() if len(v) == 2]

    if loai == "doi_chu_the":
        dung = [{b: bool(v[b][1]) and dung_doi_chu_the(v[b][0], v[b][1]["du_doan"])
                 for b in ("A", "B")} for v in du]
        return {"thach_thuc": loai, "so_cap": len(du),
                "dung_ca_cap": sum(d["A"] and d["B"] for d in dung),
                "dung_ban_A": sum(d["A"] for d in dung),
                "dung_ban_B": sum(d["B"] for d in dung)}

    if loai in BAN_BI_LAM_KHO:
        kho = BAN_BI_LAM_KHO[loai]
        sach = "B" if kho == "A" else "A"
        # CHỈ đo BẤT BIẾN: bản nháp của bản sạch và bản bị làm khó có giống nhau
        # không. Không so với bản tham chiếu — so cả thân hồ sơ với cách viết của bộ
        # sinh cho đường ống 0/40 và A 32/40 chỉ vì A chép khuôn (đo 15/09/2026).
        giong = 0
        for v in du:
            (_ca_s, r_s), (_ca_k, r_k) = v[sach], v[kho]
            if r_s and r_k:
                giong += than_ban_nhap(r_s["du_doan"]) == than_ban_nhap(r_k["du_doan"])
        return {"thach_thuc": loai, "so_cap": len(du), "hai_ban_giong_het": giong}

    raise ValueError(f"chua co phep cham van ban cho bo {loai!r}")


# ─── _nap() — Nạp tệp JSONL thành danh sách ───────────────────────────────────────────
def _nap(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(d) for d in f if d.strip()]


# ═══ main() — Chạy dòng lệnh chấm bộ thử thách cho các nhánh ══════════════════════════
# Chặn tập khoá, ghi kết quả ra tệp JSON.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", required=True)
    ap.add_argument("--nhanh", nargs="+", required=True)
    a = ap.parse_args()
    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    d = duong_dan.THU_MUC_DU_LIEU
    cac_ca = _nap(d / f"{a.tap}.jsonl")
    ra = {}
    for nhanh in a.nhanh:
        tep = d / f"ra_{nhanh}_{a.tap}.jsonl"
        if not tep.exists():
            print(f"(chua co {tep.name})")
            continue
        kq = {k["id"]: k for k in _nap(tep)}
        ra[nhanh] = cham_tap(cac_ca, kq)
        print(f"{nhanh:12} {json.dumps(ra[nhanh], ensure_ascii=False)}")

    dp = duong_dan.THU_MUC_KET_QUA / f"cham-muc-{a.tap}.json"
    dp.write_text(json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Ghi {dp}")


if __name__ == "__main__":
    main()
