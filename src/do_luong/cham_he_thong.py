# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Bộ chấm]
Làm gì   : Chấm từng mệnh đề đường ống rút ra so với đáp án có cấu trúc: sai người, sai mức,
           bịa, bỏ sót, và lượt sai đầu tiên.
Vào → Ra : tệp ra_<nhánh>_<tập>.jsonl + đáp án bộ tự sinh → bảng tỉ số kèm khoảng tin cậy,
           ghi JSON theo nhánh
Đọc từ   : loi_phat_bieu() tìm lỗi một mệnh đề; cham_ca() đếm một ca; main() chạy các nhánh
Mục lục (các hàm/lớp chính):
  loi_phat_bieu()    Tìm lỗi từng mệnh đề so với đáp án
  ghep_menh_de()     Ghép một-một mệnh đề đáp án với mệnh đề bản rút
  cham_ca()          Đếm các số liệu chấm cho một ca
  cham_theo_luot()   Đo lượt sai đầu tiên và lượt đúng hẳn của một ca
  tong_hop()         Tổng hợp mọi ca thành bảng tỉ số
  ti_so()            Tính tỉ số tổng kèm khoảng tin cậy bootstrap 95%
  cham_thach_thuc()  Chấm một tập thử thách theo cặp
  main()             Chạy dòng lệnh chấm đầu ra các nhánh
Gọi tới  : do_luong/do_trich, do_luong/khoang_tin_cay, bo_du_lieu/du_lieu_huan_luyen_trich,
           bo_du_lieu/nap_du_lieu, duong_ong/b0_chuan_hoa_phuong_ngu,
           duong_ong/b5_viet_ban_nhap, duong_ong/b5_xep_cho_cong_rui_ro, he_thong/duong_dan
Dùng bởi : do_luong/do_canh_bao
Tên cũ   : cham_he_thong.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chấm ĐẦU RA THẬT của đường ống trên đáp án cấu trúc: nhánh B, C, C_khoa, C_khoa_hoi.

Khác `danh_gia_khoa` (chạy tầng khóa trên ĐÁP ÁN — đo giá của tầng khóa), tệp này
đối chiếu từng phát biểu mà đường ống đã trích (trường `phat_bieu` của tệp
ra_<nhanh>_<tap>.jsonl, có từ 11/09/2026) với đáp án của bộ tự sinh.

BỐN LỖI trên phát biểu VÀO THÂN hồ sơ (không xuống CẦN XÁC NHẬN), và bỏ sót:

  sai_chu_the    ghép được đáp án nhưng sai người (bệnh nhân <-> người khác)
  sai_muc        sai MỨC KHẲNG ĐỊNH: chắc / nghi / chưa ghi nhận / phủ định /
                 giả định / kế hoạch. Tách thành ba mã con (22/09/2026), xem
                 MA_CON_MUC
  sai_thoi_gian  (22/09/2026) quá khứ <-> hiện tại, hoặc hai mốc thời gian không
                 khop. "chưa rõ" hay thieu moc o mot ben KHONG tinh
  ban_cu         đáp án nói bản này ĐÃ BỊ THAY hoặc CÒN MÂU THUẪN, mà nó vào thân
  khong_can_cu   không ghép được mệnh đề đáp án nào — bịa, hoặc nói quá lời
  sai_thuoc      (15/09/2026) ghép được, nhưng chi tiết thuốc (liều, số lần, đường
                 dùng, lúc bắt đầu, lúc ngưng, trạng thái dùng) KHÁC đáp án — kể cả
                 ghi một chi tiết đáp án để trống, tức là bịa
  bo_sot         mệnh đề đáp án lẽ ra vào thân mà không phát biểu thân nào ghép được

Mỗi lỗi còn tính riêng cho DỊ ỨNG, THUỐC, CHẨN ĐOÁN — ba loại `cong_rui_ro` xếp
nghiêm trọng nhất.

GHÉP: nội dung đã chuẩn hóa phương ngữ, F1 trên tập từ, ngưỡng 0,6 — CÙNG ngưỡng
với phép đo khâu trích (`do_trich`). Mốc thời gian chỉ để xếp hạng: hai bản "sốt"
(4 ngày bị thay, 2 ngày còn hiệu lực) phải ghép đúng bản. Ghép trượt thì một lỗi
thành hai (khong_can_cu + bo_sot): số lỗi CAO hơn thật, và như nhau giữa các nhánh.

KHOẢNG TIN CẬY: tỷ số TỔNG, bootstrap cụm THEO KHUÔN. Tập phát triển có 13 khuôn;
ca không phải đơn vị độc lập (`sai_so`).

ĐỐI CHỨNG BẮT BUỘC — bài học của `duong_danh_doi` (07/09/2026):
  - đánh dấu (khóa + rủi ro): so với ĐÁNH DẤU NGẪU NHIÊN cùng số lượng trong cùng
    ca. Kỳ vọng của đối chứng tính ĐỘNG: k*e/n mỗi ca, không phải rút ngẫu nhiên.
  - hỏi lại: so với hỏi NGẪU NHIÊN cùng số phát biểu. Người trả lời mô phỏng là
    HOÀN HẢO — con số là TRẦN TRÊN, phải ghi rõ mỗi lần dùng.

    python -m src.do_luong.cham_he_thong --tap viet_phat_trien --nhanh C C_khoa C_khoa_hoi
"""
import argparse
import io
import json
import random
import re as _re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.he_thong import duong_dan as duong_dan
from src.do_luong import khoang_tin_cay as sai_so
from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
from src.do_luong.do_trich import NGUONG_GHEP, do_giong

LOI = ("sai_chu_the", "sai_muc", "ban_cu", "khong_can_cu", "sai_thuoc",
       "sai_thoi_gian")

# Ba MÃ CON của `sai_muc` (22/09/2026). `sai_muc` là "sai MỨC KHẲNG ĐỊNH" — gộp
# chung mức chắc chắn, phủ định và tình huống (thực tế / giả định / kế hoạch).
# Mã con chỉ TÁCH `sai_muc` ra xem sai ở trục nào; chúng KHÔNG nằm trong LOI, nên
# một mệnh đề không bị đếm lỗi hai lần.
MA_CON_MUC = ("sai_muc_chac_chan", "sai_muc_phu_dinh", "sai_muc_tinh_huong")

# Phiên bản bộ chấm. Đổi mỗi lần thêm hay đổi định nghĩa một mã lỗi — số liệu của
# hai phiên bản KHÔNG so thẳng được với nhau. Ghi vào mỗi tệp kết quả.
#   2026-09-20  thêm do_chinh_xac, do_phu, f1, ser, sai_chu_the_tren_gold
#   2026-09-22  thêm mã lỗi sai_thoi_gian (trước đó KHÔNG chấm thời gian); tách
#               sai_muc thành ba mã con; `_muc` hiểu từ phủ định đầu câu; thêm
#               phủ định làm tiêu chí phá thế hóa khi ghép
PHIEN_BAN = "2026-09-22"

# Từ mở đầu câu làm đảo nghĩa. "không sốt" (phu_dinh=False) và "sốt"
# (phu_dinh=True) là CÙNG một ý — số có phủ định trần sẽ đếm lỗi oan.
_TU_PHU_DINH = _re.compile(r"^\s*(không|chưa|chẳng|ko)\b", _re.I)


# ─── _phu_dinh_that() — Xác định phủ định có hiệu lực ─────────────────────────────────
# Có cờ phủ định XOR nội dung mở đầu bằng từ phủ định.
def _phu_dinh_that(x) -> bool:
    """Phủ định có hiệu lực = có `phu_dinh` XOR nội dung mở đầu bằng từ phủ định."""
    return bool(x.get("phu_dinh")) != bool(_TU_PHU_DINH.match(x.get("noi_dung") or ""))


# Hai giá trị thời gian "chắc" — "chưa rõ" ở một bên thì KHÔNG tính là lỗi: nói
# "chưa rõ" khi đáp án có mốc là bỏ sót chi tiết, không phải nói sai.
_THOI_GIAN_CHAC = ("hiện tại", "quá khứ")


# ═══ sai_thoi_gian() — Xét mệnh đề có sai thời gian so với đáp án ═════════════════════
# Sai khi hai bên chắc mà khác nhau, hoặc hai mốc không khớp; thiếu mốc không tính.
def sai_thoi_gian(d, p) -> bool:
    """Lỗi thời gian: (1) cả hai bên nói chắc mà khác nhau (quá khứ <-> hiện tại),
    hoặc (2) cả hai bên có mốc thời gian mà hai mốc không khớp.
    Thiếu mốc ở một bên KHÔNG tính — đó là bỏ sót chi tiết."""
    a, b = d.get("thoi_gian_su_kien"), p.get("thoi_gian_su_kien")
    if a in _THOI_GIAN_CHAC and b in _THOI_GIAN_CHAC and a != b:
        return True
    ma, mb = _nd(d.get("moc_thoi_gian")), _nd(p.get("moc_thoi_gian"))
    return bool(ma and mb and do_giong(ma, mb) < NGUONG_GHEP)


LOAI_NGHIEM_TRONG = ("di_ung", "thuoc", "chan_doan")
CO_DANH_DAU = (cong_rui_ro.BI_CHAN, cong_rui_ro.NGUY_CO_CAO)


# ─── _nd() — Chuẩn hoá nội dung để so sánh ────────────────────────────────────────────
# Giữ lại các cụm dân gian, khác với đường ống.
def _nd(x):
    # Bộ chấm biết CẢ các cụm dân gian giữ lại (24/09/2026); đường ống thì không —
    # đó mới đo được đường ống chịu cách nói chưa gặp. Các cụm đó không có trong dữ
    # liệu thế hệ 8 nên mọi số đã báo cáo không đổi (tests/test_dan_gian.py).
    return chuan_hoa.chuan_hoa(str(x or ""), gom_giu_lai=True)


# ─── _muc() — Lấy bộ ba độ chắc chắn, phủ định, tình huống ────────────────────────────
# Phủ định chỉ có nghĩa khi độ chắc chắn là chắc chắn.
def _muc(d):
    """(độ chắc chắn, phủ định, tình huống). Phủ định chỉ có nghĩa khi chắc chắn:
    "chưa ghi nhận" bỏ qua phủ định, giống `sinh_benh_an.dien_dat`."""
    dcc = d.get("do_chac_chan") or "chắc chắn"
    return (dcc, _phu_dinh_that(d) and dcc == "chắc chắn",
            d.get("tinh_huong") or "thực tế")


# ─── _con_hieu_luc() — Xét mệnh đề còn hiệu lực ───────────────────────────────────────
def _con_hieu_luc(d):
    return (d.get("trang_thai") or "còn hiệu lực") == "còn hiệu lực"


# ─── _gold_vao_than() — Xét mệnh đề đáp án có vào thân hồ sơ ──────────────────────────
# Còn hiệu lực và không phải câu giả định.
def _gold_vao_than(d):
    return _con_hieu_luc(d) and (d.get("tinh_huong") or "thực tế") != "giả định"


# ─── _la_bn_gold() — Xét mệnh đề đáp án có chủ thể là bệnh nhân ───────────────────────
def _la_bn_gold(d):
    return d.get("chu_the") == "bệnh nhân"


# Cách mô hình gọi CHÍNH người đang kể mà không nêu quan hệ. Dùng khi đáp án ghi
# "người nhà" — tức lời thoại KHÔNG lộ người đó là ai.
TEN_NGUOI_NHA_CHUNG = frozenset({"người nhà", "người kể", "tôi", "em", "cháu", ""})


# ═══ dung_nguoi() — Kiểm mệnh đề có gán đúng người so với đáp án ══════════════════════
# Không chỉ chia bệnh nhân hay người khác; người nhà phải gọi chung, không bịa danh
# xưng.
def dung_nguoi(d, p) -> bool:
    """Phát biểu có gán ĐÚNG NGƯỜI với mệnh đề đáp án không.

    VÌ SAO KHÔNG CHỈ KIỂM BỆNH NHÂN HAY NGƯỜI KHÁC (15/09/2026). Bản cũ chỉ so
    `chu_the_id == 0`. Trên bộ đổi chủ thể thế hệ 6, nó chấm C đúng 28/40 cặp trong
    khi 29/40 ca đường ống ghi dị ứng của "bố" thành của "bà ngoại" — đúng MỤC tiền
    sử gia đình, SAI NGƯỜI. Với hồ sơ, ghi nhầm bố thành bà ngoại cũng là một lo~i
    quy gán: dị ứng của một người đã được gán cho một người khác.

    Đáp án "người nhà" (lời thoại không lộ quan hệ): mô hình phải gọi chung chung.
    Nếu nó ghi đích danh "bố", đó là BỊA ra một thông tin không ai nói.
    """
    if _la_bn_gold(d) != (p.get("chu_the_id", 0) == 0):
        return False
    if _la_bn_gold(d):
        return True
    vang = _nd(d.get("chu_the", ""))
    ten = _nd(p.get("ten_chu_the", ""))
    if vang == "người nhà":
        return ten in TEN_NGUOI_NHA_CHUNG
    return ten == vang or ten.startswith(vang + " ")


CHI_TIET_THUOC_CHAM = ("lieu", "so_lan", "duong_dung", "bat_dau", "ngung",
                       "trang_thai_dung")


# ═══ dung_thuoc() — Kiểm chi tiết thuốc có khớp đáp án ════════════════════════════════
# Mọi chi tiết phải bằng nhau; đáp án không có thuốc thì không chấm.
def dung_thuoc(d, p) -> bool:
    """Chi tiết thuốc của phát biểu có KHỚP đáp án không (15/09/2026).

    Mỗi chi tiết số sau chuẩn hóa, BẰNG NHAU MỚI TÍNH LÀ ĐÚNG. Cả hai chiều đều là
    lỗi: đáp án có liều mà phát biểu không ghi (mất thông tin nguy hiểm), và phát
    biểu ghi liều mà đáp án để trống (bịa một con số không ai nói). Đáp án không có
    `thuoc` (mệnh đề không phải thuốc, hoặc bộ dữ liệu trước 15/09) thì không chấm
    trục này — chấm thì mọi phát biểu của bộ cũ đều thành lỗi.
    """
    vang = d.get("thuoc")
    if not vang:
        return True
    du = p.get("thuoc") or {}
    return all(_nd(vang.get(k)) == _nd(du.get(k)) for k in CHI_TIET_THUOC_CHAM)


# ─── _loai_gold() — Phân loại thông tin của mệnh đề đáp án ────────────────────────────
# Dị ứng, thuốc, chẩn đoán hoặc khác.
def _loai_gold(d):
    m = d.get("muc")
    if m == "DỊ ỨNG" or "dị ứng" in str(d.get("noi_dung", "")).lower():
        return "di_ung"
    return {"THUỐC ĐANG DÙNG": "thuoc", "CHẨN ĐOÁN": "chan_doan"}.get(m, "khac")


# ═══ dap_an() — Lấy mệnh đề đáp án để chấm, kèm chỉ số gốc ════════════════════════════
# Bỏ bản sao ở lý do khám.
def dap_an(ca):
    """Mệnh đề đáp án để chấm, kèm chỉ số gốc `_i`. Bỏ bản sao ở LÝ DO KHÁM
    (`du_lieu_trich.ban_lap_ly_do_kham`): nó không phải một thông tin riêng."""
    from src.bo_du_lieu.du_lieu_huan_luyen_trich import ban_lap_ly_do_kham
    lap = ban_lap_ly_do_kham(ca["dap_an"])
    return [dict(d, _i=i) for i, d in enumerate(ca["dap_an"]) if i not in lap]


# ═══ ghep_menh_de() — Ghép một-một mệnh đề đáp án với mệnh đề bản rút ═════════════════
# Nội dung phải đạt ngưỡng; hoà thì xếp theo mốc thời gian rồi theo lượt dẫn.
def ghep_menh_de(da, ps, nguong=NGUONG_GHEP):
    """Ghép 1-1 tham lam -> {chỉ số trong `da`: chỉ số trong `ps`}.

    Nội dung phải đạt NGUONG_GHEP. Khi nhiều mệnh đề CÙNG nội dung — hai bản "sốt"
    của một lần đính chính; "đi ngoài phân lỏng" thật và "nếu còn đi ngoài phân
    lỏng" giả định — xếp hạng bằng mốc thời gian rồi bằng LƯỢT dẫn. Ghép sai bản thì
    một phát biểu đúng bị tính là "bản cũ" hay "sai mức": đo 11/09/2026 trên trích
    HOÀN HẢO, 21/531 lỗi giả trước khi có hai tiêu chí này.
    """
    diem = []
    for i, d in enumerate(da):
        a = _nd(d.get("noi_dung"))
        la = set(d.get("luot") or [])
        for j, p in enumerate(ps):
            s = do_giong(a, _nd(p.get("noi_dung")))
            if s < nguong:
                continue
            t = do_giong(_nd(d.get("moc_thoi_gian")), _nd(p.get("moc_thoi_gian")))
            lb = set(p.get("bang_chung") or p.get("luot_thoai") or [])
            lu = len(la & lb) / len(la | lb) if (la and lb) else 0.0
            # Hai bản của một lần sửa LIỀU cùng tên thuốc, cùng lượt, không mốc thời
            # gian — chỉ liều phân biệt được. Thêm 15/09/2026 cùng trường `thuoc`.
            lieu = 0.0
            if d.get("thuoc") and p.get("thuoc"):
                lieu = float(_nd(d["thuoc"].get("lieu")) == _nd(p["thuoc"].get("lieu")))
            # Phá thế hóa khi hai bản GIỐNG HỆT nhau cả nội dung, mốc thời gian và lượt,
            # chỉ khác phủ định: ghép bản cùng phủ định với nhau. Trọng số nhỏ nên KHÔNG
            # đổi cặp khi mốc thời gian khác. Lưu ý (22/09/2026): ca dct_030_A từng bị
            # nghi là ghép chéo, kiểm lại thì KHÔNG — mô hình đảo phủ định thật ở cả hai
            # mốc của một diễn biến, và ghép theo mốc thời gian là đúng.
            pd = 0.05 * float(_phu_dinh_that(d) == _phu_dinh_that(p))
            diem.append((s + 0.5 * t + 0.25 * lu + 0.5 * lieu + pd, -i, -j, i, j))
    diem.sort(reverse=True)
    ra, da_p = {}, set()
    for *_x, i, j in diem:
        if i in ra or j in da_p:
            continue
        ra[i] = j
        da_p.add(j)
    return ra


# ─── _khoa_trung() — Tạo khoá nhận diện mệnh đề lặp ───────────────────────────────────
def _khoa_trung(p):
    return (_nd(p.get("noi_dung")), p.get("chu_the_id", 0) == 0, _muc(p))


# ═══ loi_phat_bieu() — Tìm lỗi từng mệnh đề so với đáp án ═════════════════════════════
# Trả lỗi theo id và các mệnh đề đáp án bị bỏ sót; tách lặp khỏi không căn cứ.
def loi_phat_bieu(ca, ps, xet=None):
    """Ghép TOÀN BỘ `ps` với đáp án — để bản cũ của hệ thống ghép với bản cũ của đáp
    án, dù bản cũ không nằm trong phần đang xét — rồi chấm những phát biểu có id
    trong `xet` (mặc định: tất cả).

    -> ({id: (danh sách lỗi, loại thông tin)}, [mệnh đề đáp án bỏ sót]).

    `trung_lap`: phát biểu không ghép được nhưng GIỐNG HỆT một phát biểu đang xét
    khác — dòng viết lặp, không phải thông tin bịa. Tách khỏi `khong_can_cu`.
    Bỏ sót: mệnh đề đáp án VÀO THÂN mà phát biểu ghép với nó không nằm trong `xet`.
    """
    da = dap_an(ca)
    xet = {p["id"] for p in ps} if xet is None else set(xet)
    g = ghep_menh_de(da, ps)
    theo_p = {ps[j]["id"]: da[i] for i, j in g.items()}
    co_ghep = {_khoa_trung(p) for p in ps if p["id"] in xet and p["id"] in theo_p}
    ra, da_gap = {}, set()
    for p in ps:
        if p["id"] not in xet:
            continue
        d = theo_p.get(p["id"])
        if d is None:
            k = _khoa_trung(p)
            loai = "trung_lap" if (k in co_ghep or k in da_gap) else "khong_can_cu"
            da_gap.add(k)
            ra[p["id"]] = ([loai], cong_rui_ro.loai_thong_tin(p))
            continue
        loi = []
        if not dung_nguoi(d, p):
            loi.append("sai_chu_the")
        if _muc(d) != _muc(p):
            loi.append("sai_muc")
        if not _con_hieu_luc(d):
            loi.append("ban_cu")
        if not dung_thuoc(d, p):
            loi.append("sai_thuoc")
        # Mã con của sai_muc (22/09/2026): sai ở trục nào trong ba trục.
        if "sai_muc" in loi:
            md, mp = _muc(d), _muc(p)
            for truc, ma in zip(range(3), MA_CON_MUC):
                if md[truc] != mp[truc]:
                    loi.append(ma)
        # Thời gian (22/09/2026) — trước đó bộ chấm không chấm trục này.
        if sai_thoi_gian(d, p):
            loi.append("sai_thoi_gian")
        ra[p["id"]] = (loi, _loai_gold(d))
    bo_sot = [d for i, d in enumerate(da) if _gold_vao_than(d)
              and (i not in g or ps[g[i]]["id"] not in xet)]
    return ra, bo_sot


# ─── _co_loi() — Xét danh sách mã có chứa lỗi thật ────────────────────────────────────
def _co_loi(ds):
    return bool(set(ds) & set(LOI))


# ─── _than() — Lấy các mệnh đề vào thân hồ sơ ─────────────────────────────────────────
# Loại mệnh đề nằm ở mục phụ.
def _than(r):
    muc = {g["id"]: g["muc"] for g in r.get("ghi_chu", [])}
    return [p for p in r["phat_bieu"]
            if p["id"] in muc and muc[p["id"]] not in sinh_benh_an.MUC_PHU_TAT_CA]


# ─── _truoc_khoa() — Lấy mệnh đề sẽ vào thân nếu không có khoá ────────────────────────
# Dùng để đánh dấu tập đo.
def _truoc_khoa(r):
    """Phát biểu SẼ vào thân nếu KHÔNG có khóa — tập để đo đánh dấu."""
    return [p for p in r["phat_bieu"]
            if sinh_benh_an._muc_cho(p, 0)[0] not in sinh_benh_an.MUC_PHU_TAT_CA]


# ═══ cham_ca() — Đếm các số liệu chấm cho một ca ══════════════════════════════════════
# Gồm số vào thân, ghép được, đúng, chèn, bỏ sót: tử và mẫu của các tỉ số.
def cham_ca(ca, r) -> dict:
    """-> số đếm cho MỘT ca. Mỗi trường là tử số hoặc mẫu số của một tỷ số."""
    than = {p["id"] for p in _than(r)}
    loi, bo_sot = loi_phat_bieu(ca, r["phat_bieu"], than)
    da = dap_an(ca)
    k = Counter(so_than=len(than),
                so_dap_an_than=sum(1 for d in da if _gold_vao_than(d)),
                bo_sot=len(bo_sot))
    for ds, loai in loi.values():
        # Số mệnh đề GHÉP ĐƯỢC với đáp án (16/09/2026). Vì sao cần: `sai_chu_the`
        # chia cho MỌI phát biểu vào thân, mà một phát biểu không ghép được thì
        # không bao giờ bị tính sai chủ thể. Nên một nhánh trích thô, ghép trượt
        # gần hết, lại có tỷ lệ sai chủ thể ĐẸP hơn một nhánh trích đúng. Đo được
        # 16/09 trên bộ đổi chủ thể: đường đối chứng theo luật có 66-77% phát biểu
        # không căn cứ, và nhờ thế tỷ lệ sai chủ thể của nó tụt xuống 4-8%.
        if not ({"khong_can_cu", "trung_lap"} & set(ds)):
            k["so_ghep"] += 1
            # Mệnh đề ghép được VÀ không dính lỗi nào — tử số của Precision/Recall.
            if not _co_loi(ds):
                k["so_dung"] += 1
        else:
            # Mệnh đề không ứng với thông tin nào trong đáp án — lỗi CHÈN của SER.
            k["chen"] += 1
        for m in ds:
            k[m] += 1
        k["loi_bat_ky"] += _co_loi(ds)
        if loai in LOAI_NGHIEM_TRONG:
            k["so_than_nghiem_trong"] += 1
            k["loi_nghiem_trong"] += _co_loi(ds)
    k["bo_sot_nghiem_trong"] = sum(1 for d in bo_sot
                                   if _loai_gold(d) in LOAI_NGHIEM_TRONG)
    k["so_dap_an_nghiem_trong"] = sum(1 for d in da if _gold_vao_than(d)
                                      and _loai_gold(d) in LOAI_NGHIEM_TRONG)

    # --- Độ chính xác / Độ phủ / F1 / Tỷ lệ lỗi ô (SER) (20/09/2026)
    #
    # VÌ SAO THÊM. Mọi tỷ lệ lỗi ở trên đều chia cho một mẫu số PHỤ THUỘC HỆ THỐNG
    # (số mệnh đề nó viết ra, hoặc số mệnh đề nó ghép được). Một hệ thống viết ít
    # có mẫu số nhỏ nên tỷ lệ đẹp. Đo được 19/09 trên bộ đổi chủ thể: đường tắt
    # bằng luật đạt 13,1% sai chủ thể — THẤP HƠN mọi nhánh có mô hình — nhưng nó
    # bỏ sót 51,3% thông tin và chỉ 350/1.156 mệnh đề ghép được với đáp án.
    #
    # Chuẩn của lĩnh vực trích xuất thông tin là báo cáo Precision, Recall, F1 trên
    # MẪU SỐ ĐÁP ÁN, cộng thêm Slot Error Rate (Makhoul, Kubala, Schwartz,
    # Weischedel 1999 — "Performance measures for information extraction").
    #
    # F1 viết dưới dạng một tỷ số DUY NHẤT để bootstrap theo cụm kịch bản vẫn dùng:
    #     F1 = 2*dung / (số hệ thống viết ra + số đáp án)
    #
    # SER đếm ba loại lỗi trên tổng số ô đáp án. SER CÓ THỂ VƯỢT 1 — đó là bình
    # thường, khi hệ thống chèn thêm nhiều hơn số ô có thật.
    #     SER = (thay thế + xóa + chèn) / số đáp án
    #     thay thế = mệnh đề ghép được nhưng dính lỗi
    #     xóa      = bỏ sót
    #     chèn     = mệnh đề không ứng với thông tin nào trong đáp án
    k["f1_tu"] = 2 * k["so_dung"]
    k["f1_mau"] = k["so_than"] + k["so_dap_an_than"]
    k["ser_tu"] = (k["so_ghep"] - k["so_dung"]) + k["bo_sot"] + k["chen"]

    # --- đánh dấu: trên tập TRƯỚC khóa, so với đánh dấu ngẫu nhiên cùng số lượng
    if "rui_ro" in r:
        tk = {p["id"] for p in _truoc_khoa(r)}
        loi_tk, _ = loi_phat_bieu(ca, r["phat_bieu"], tk)
        sai = {i for i, (ds, _l) in loi_tk.items() if _co_loi(ds)}
        co = {d["id"] for d in r["rui_ro"] if d["nhom"] in CO_DANH_DAU} & tk
        n, e = len(tk), len(sai)
        k["dd_n"], k["dd_loi"], k["dd_co"] = n, e, len(co)
        k["dd_trung"] = len(co & sai)
        k["dd_ngau_nhien"] = len(co) * e / n if n else 0.0

        # --- hỏi lại: người trả lời HOÀN HẢO sửa mọi lỗi ở phát biểu được hỏi
        hoi = set()
        for c in r.get("cau_hoi") or []:
            hoi |= {int(x) for x in c.get("muc_tieu", {})}
        hoi &= tk
        k["hl_so_cau"] = len(r.get("cau_hoi") or [])
        k["hl_so_hoi"] = len(hoi)
        k["hl_sua"] = len(hoi & sai)
        k["hl_ngau_nhien"] = len(hoi) * e / n if n else 0.0
    return k


# ─── _luot_cua() — Lấy lượt nói muộn nhất làm bằng chứng ──────────────────────────────
def _luot_cua(x) -> int:
    """Lượt thoại muộn nhất làm bằng chứng — cho cả mệnh đề đáp án (`luot`) lẫn phát
    biểu của đường ống (`bang_chung` hoặc `luot_thoai`)."""
    return max(x.get("luot") or x.get("bang_chung") or x.get("luot_thoai") or [0])


# ═══ cham_theo_luot() — Đo lượt sai đầu tiên và lượt đúng hẳn của một ca ══════════════
# T_dung là lượt đầu tiên mọi mệnh đề đáp án vào thân đều đúng, hết lỗi.
def cham_theo_luot(ca, r) -> dict:
    """Hai chỉ số có đơn vị là LƯỢT, cho MỘT ca (16/09/2026).

      luot_sai_dau_tien  lượt đầu tiên mà bản nháp dựng TỚI lượt đó đã mang một lỗi
                         thuộc `LOI`, hoặc đã bỏ sót một mệnh đề đáp án lẽ ra có
                         trong bản nháp tính tới lượt đó. None = không lượt nào sai.
      T_dung             lượt đầu tiên mà MỌI mệnh đề đáp án vào thân (của cả ca) đã
                         được ghi đúng, và không còn lỗi nào. None = không bao giờ đủ.

    VÌ SAO. Mọi thước đo khác của dự án cộng dồn theo CA: một bản nháp sai ở lượt 2
    rồi được sửa ở lượt 9 chấm bằng một bản đúng từ đầu. Với hồ sơ lâm sàng thì hai
    thứ đó khác nhau — bác sĩ đọc hồ sơ giữa buổi khám. Pan, Liu, You (arXiv
    2603.17425) đo `T_goal` (tương ứng `T_dung`) nhưng không đo lượt sai đầu tiên.

    Dùng lại `loi_phat_bieu` và `ghep_menh_de` có sẵn, chỉ đổi tập `xet` theo từng
    lượt — không có luật chấm thứ hai để trôi khỏi luật chính.
    """
    than = {p["id"] for p in _than(r)}
    ps = r["phat_bieu"]
    da = [d for d in dap_an(ca) if _gold_vao_than(d)]
    moc = sorted({_luot_cua(p) for p in ps if p["id"] in than}
                 | {_luot_cua(d) for d in da})
    dau_sai = t_dung = None
    for t in moc:
        xet = {p["id"] for p in ps if p["id"] in than and _luot_cua(p) <= t}
        loi, _ = loi_phat_bieu(ca, ps, xet)
        co_loi = any(_co_loi(ds) for ds, _l in loi.values())
        # Bỏ sót TÍNH TỚI LƯỢT t: mệnh đề đáp án đã đủ bằng chứng mà chưa vào thân.
        den_gio = [d for d in da if _luot_cua(d) <= t]
        thieu_gio = len(den_gio) - len(ghep_menh_de(
            den_gio, [p for p in ps if p["id"] in xet]))
        if dau_sai is None and (co_loi or thieu_gio):
            dau_sai = t
        # T_dung xét trên TOÀN BỘ đáp án của ca, không chỉ phần đã đến.
        if t_dung is None and not co_loi and da and len(ghep_menh_de(
                da, [p for p in ps if p["id"] in xet])) == len(da):
            t_dung = t
    return {"luot_sai_dau_tien": dau_sai, "T_dung": t_dung,
            "so_luot_co_menh_de": len(moc), "so_menh_de_than_dap_an": len(da)}


# ═══ ti_so() — Tính tỉ số tổng kèm khoảng tin cậy bootstrap 95% ═══════════════════════
# Lấy mẫu lại theo cụm khuôn bệnh; trả None khi mẫu số bằng 0.
def ti_so(tu, mau, khuon, so_lan=sai_so.SO_LAN_MAC_DINH, hat=sai_so.HAT_MAC_DINH):
    """Tỷ số TỔNG (sum tử / sum mẫu) + khoảng 95% bootstrap cụm theo khuôn."""
    cum = defaultdict(lambda: [0.0, 0.0])
    for i in mau:
        cum[khuon[i]][0] += tu.get(i, 0)
        cum[khuon[i]][1] += mau[i]
    cum = list(cum.values())
    T, M = sum(c[0] for c in cum), sum(c[1] for c in cum)
    if not M:
        return None
    rng = random.Random(hat)
    bs = []
    for _ in range(so_lan):
        t = m = 0.0
        for _k in range(len(cum)):
            c = cum[rng.randrange(len(cum))]
            t += c[0]
            m += c[1]
        if m:
            bs.append(t / m)
    bs.sort()
    return {"gia_tri": T / M, "thap": sai_so._phan_vi(bs, 0.025),
            "cao": sai_so._phan_vi(bs, 0.975), "tu": T, "mau": M,
            "so_khuon": len(cum)}


BANG = (  # (tên, tử số, mẫu số)
    ("sai_chu_the", "sai_chu_the", "so_than"),
    ("sai_muc", "sai_muc", "so_than"),
    ("ban_cu", "ban_cu", "so_than"),
    ("khong_can_cu", "khong_can_cu", "so_than"),
    ("sai_thuoc", "sai_thuoc", "so_than"),
    # Cùng tử số, mẫu số là số mệnh đề GHÉP ĐƯỢC — đọc kèm hai dòng trên, vì mẫu số
    # "so_than" thường cho điểm đẹp cho nhánh ghép trượt nhiều.
    ("sai_chu_the_tren_ghep", "sai_chu_the", "so_ghep"),
    ("sai_muc_tren_ghep", "sai_muc", "so_ghep"),
    # Phiên bản 2026-09-22, tính trên mệnh đề GHÉP ĐƯỢC — lý do như dòng
    # `sai_chu_the_tren_ghep`. Ba mã con cộng lại có thể LỚN HƠN sai_muc: một mệnh
    # đề sai cả hai trục thì có hai mã con.
    ("sai_muc_chac_chan_tren_ghep", "sai_muc_chac_chan", "so_ghep"),
    ("sai_muc_phu_dinh_tren_ghep", "sai_muc_phu_dinh", "so_ghep"),
    ("sai_muc_tinh_huong_tren_ghep", "sai_muc_tinh_huong", "so_ghep"),
    ("sai_thoi_gian_tren_ghep", "sai_thoi_gian", "so_ghep"),
    ("loi_bat_ky", "loi_bat_ky", "so_than"),
    ("trung_lap", "trung_lap", "so_than"),
    ("loi_nghiem_trong", "loi_nghiem_trong", "so_than_nghiem_trong"),
    ("bo_sot", "bo_sot", "so_dap_an_than"),
    ("bo_sot_nghiem_trong", "bo_sot_nghiem_trong", "so_dap_an_nghiem_trong"),
    # Bốn dòng dưới đây dùng MẪU SỐ KHÔNG PHỤ THUỘC hệ thống, nên so sánh được
    # giữa các hệ thống viết ra số lượng mệnh đề khác nhau. Xem ghi chú trong
    # `cham_ca`. `sai_chu_the_tren_gold` là cùng tử số với `sai_chu_the`, chia
    # cho tổng số ô đáp án thay vì cho số mệnh đề hệ thống viết ra.
    ("do_chinh_xac", "so_dung", "so_than"),
    ("do_phu", "so_dung", "so_dap_an_than"),
    ("f1", "f1_tu", "f1_mau"),
    ("ser", "ser_tu", "so_dap_an_than"),
    ("sai_chu_the_tren_gold", "sai_chu_the", "so_dap_an_than"),
    ("danh_dau_do_chuan", "dd_trung", "dd_co"),
    ("danh_dau_do_chuan_NGAU_NHIEN", "dd_ngau_nhien", "dd_co"),
    ("danh_dau_do_phu", "dd_trung", "dd_loi"),
    ("danh_dau_do_phu_NGAU_NHIEN", "dd_ngau_nhien", "dd_loi"),
    ("hoi_lai_sua_moi_phat_bieu_hoi", "hl_sua", "hl_so_hoi"),
    ("hoi_lai_NGAU_NHIEN", "hl_ngau_nhien", "hl_so_hoi"),
)


# ═══ tong_hop() — Tổng hợp mọi ca thành bảng tỉ số ════════════════════════════════════
# Thiếu kết quả của một ca thì dừng, tránh chọn ca cho số đẹp.
def tong_hop(cac_ca, ket_qua):
    """`ket_qua`: {id: bản ghi của nhánh}. Mỗi ca trong `cac_ca` PHẢI có bản ghi —
    thiếu là dừng hẳn: bỏ ca đi là chọn ca để cho số đẹp."""
    thieu = [ca["id"] for ca in cac_ca if ca["id"] not in ket_qua]
    if thieu:
        raise SystemExit(f"thieu ket qua cho {len(thieu)} ca: {thieu[:5]}")
    dem = {ca["id"]: cham_ca(ca, ket_qua[ca["id"]]) for ca in cac_ca}
    khuon = {ca["id"]: ca.get("benh") or "?" for ca in cac_ca}
    bang = {}
    for ten, tu, mau in BANG:
        m = {i: dem[i][mau] for i in dem if mau in dem[i]}
        if m:
            bang[ten] = ti_so({i: dem[i][tu] for i in m}, m, khuon)
    return {"bang": bang, "so_ca": len(cac_ca),
            "tong": dict(sum((Counter(d) for d in dem.values()), Counter()))}


# ─── _than_khang_dinh_di_ung_bn() — Lấy mệnh đề thân khẳng định dị ứng của bệnh nhân ───
# ------------------------------------------------------------- ba thách thức
def _than_khang_dinh_di_ung_bn(r):
    return [p for p in _than(r) if p.get("chu_the_id", 0) == 0
            and "dị ứng" in str(p.get("noi_dung", "")).lower()
            and _muc(p) == ("chắc chắn", False, "thực tế")]


# ═══ dung_di_ung() — Chấm bộ đổi chủ thể: dị ứng gán đúng người ═══════════════════════
# Dị ứng đáp án phải ghép được và đúng người; bản A không được ghi bệnh nhân dị ứng.
def dung_di_ung(ca, r) -> bool:
    """Bản A: dị ứng của NGƯỜI NHÀ. Bản B: của BỆNH NHÂN. Dùng khi mệnh đề dị ứng
    khẳng định ghép được và đúng người, và ở bản A không có phát biểu thân nào ghi
    bệnh nhân dị ứng chất đó."""
    if r is None:
        return False
    gold = [d for d in dap_an(ca) if "dị ứng" in d["noi_dung"].lower()
            and _muc(d) == ("chắc chắn", False, "thực tế") and _con_hieu_luc(d)]
    if not gold:
        return False
    g = ghep_menh_de(gold, r["phat_bieu"])
    for i, d in enumerate(gold):
        if i not in g:
            return False
        if not dung_nguoi(d, r["phat_bieu"][g[i]]):
            return False
    if not any(_la_bn_gold(d) for d in gold):
        chat = {_nd(d["noi_dung"]) for d in gold}
        if any(do_giong(_nd(p["noi_dung"]), c) >= NGUONG_GHEP
               for p in _than_khang_dinh_di_ung_bn(r) for c in chat):
            return False
    return True


# ═══ chu_ky() — Lấy dấu hai bản của cặp phương ngữ ════════════════════════════════════
# Mỗi mệnh đề gồm nội dung, bệnh nhân, mức khẳng định, vào thân.
def chu_ky(r):
    """Cái phải GIỐNG NHAU giữa hai bản của cặp phương ngữ: mỗi phát biểu là (nội
    dung chuẩn hóa, bệnh nhân?, mức khẳng định, vào thân?)."""
    muc = {g["id"]: g["muc"] for g in r.get("ghi_chu", [])}
    return frozenset((_nd(p["noi_dung"]), p.get("chu_the_id", 0) == 0, _muc(p),
                      muc.get(p["id"]) not in sinh_benh_an.MUC_PHU_TAT_CA)
                     for p in r["phat_bieu"])


# ═══ dung_trang_thai_cuoi() — Chấm trạng thái cuối của mệnh đề có quan hệ ═════════════
# Còn hiệu lực phải ở thân; bị thay thế hoặc chưa giải quyết thì không.
def dung_trang_thai_cuoi(ca, r) -> bool:
    """Mỗi mệnh đề đáp án CÓ quan hệ, và mệnh đề nó trỏ tới, phải ở đúng chỗ:
    còn hiệu lực -> thân; bị thay / chưa giải quyết -> KHÔNG ở thân."""
    if r is None:
        return False
    da = dap_an(ca)
    lq_i = {d["_i"] for d in da if d.get("quan_he")} | \
           {d.get("quan_he_voi") for d in da if d.get("quan_he")}
    if not lq_i:
        return False
    than_id = {p["id"] for p in _than(r)}
    g = ghep_menh_de(da, r["phat_bieu"])       # ghép TOÀN BỘ, xét phần liên quan
    for i, d in enumerate(da):
        if d["_i"] not in lq_i:
            continue
        o_than = i in g and r["phat_bieu"][g[i]]["id"] in than_id
        if o_than != _gold_vao_than(d):
            return False
    return True


# ═══ cham_thach_thuc() — Chấm một tập thử thách theo cặp ══════════════════════════════
# Bộ đổi chủ thể đếm đúng cả cặp; bộ phương ngữ so dấu hai bản.
def cham_thach_thuc(cac_ca, ket_qua):
    loai = {ca.get("thach_thuc") for ca in cac_ca} - {None}
    if len(loai) != 1:
        return None
    loai = loai.pop()
    if loai == "doi_chu_the":
        cap = defaultdict(dict)
        for ca in cac_ca:
            cap[ca["cap"]][ca["bien_the"]] = dung_di_ung(ca, ket_qua.get(ca["id"]))
        du = [v for v in cap.values() if len(v) == 2]
        return {"thach_thuc": loai, "so_cap": len(du),
                "dung_ca_cap": sum(all(v.values()) for v in du),
                "dung_ban_A": sum(v["A"] for v in du),
                "dung_ban_B": sum(v["B"] for v in du)}
    if loai == "phuong_ngu":
        cap = defaultdict(dict)
        for ca in cac_ca:
            r = ket_qua.get(ca["id"])
            cap[ca["cap"]][ca["bien_the"]] = (ca, r)
        du = [v for v in cap.values() if len(v) == 2]
        giong = sum(1 for v in du if v["A"][1] and v["B"][1]
                    and chu_ky(v["A"][1]) == chu_ky(v["B"][1]))
        loi = {b: sum(cham_ca(ca, r)["loi_bat_ky"] for v in du
                      for ca, r in [v[b]] if r) for b in ("A", "B")}
        than = {b: sum(cham_ca(ca, r)["so_than"] for v in du
                       for ca, r in [v[b]] if r) for b in ("A", "B")}
        return {"thach_thuc": loai, "so_cap": len(du), "giong_het": giong,
                "loi_ban_co_phuong_ngu": f"{loi['A']}/{than['A']}",
                "loi_ban_khong_phuong_ngu": f"{loi['B']}/{than['B']}"}
    if loai == "dinh_chinh":
        theo_bay = defaultdict(lambda: [0, 0])
        for ca in cac_ca:
            t = theo_bay[ca.get("bay_chinh")]
            t[1] += 1
            t[0] += dung_trang_thai_cuoi(ca, ket_qua.get(ca["id"]))
        return {"thach_thuc": loai,
                "dung_theo_bay": {b: f"{d}/{n}" for b, (d, n) in theo_bay.items()},
                "dung": sum(d for d, _n in theo_bay.values()),
                "so_ca": sum(n for _d, n in theo_bay.values())}
    return None


# ─── _in() — In một dòng tỉ số kèm khoảng tin cậy ─────────────────────────────────────
# ----------------------------------------------------------------------- CLI
def _in(ten, k):
    if k is None:
        return
    print(f"  {ten:34} {k['gia_tri']:7.2%}  [{k['thap']:.2%}; {k['cao']:.2%}]"
          f"  ({k['tu']:.1f}/{k['mau']:.0f}, {k['so_khuon']} khuon)")


# ═══ canh_bo_lech_the_he() — Dừng nếu hội thoại kết quả khác bộ dữ liệu ═══════════════
# So đầu vào từng ca với bộ dữ liệu, tránh chấm nhầm thế hệ dữ liệu.
def canh_bo_lech_the_he(tep, goc, kq):
    """Dừng nếu hội thoại trong tệp kết quả khác hội thoại trong bộ dữ liệu.

    LỖI ĐÃ XẢY RA (phát hiện 19/09/2026). Ngày 15/09 lúc 13:04 các nhánh chạy trên
    bộ đổi chủ thể THẾ HỆ 6. Lúc 13:40 cùng ngày, bộ thế hệ 7 được sinh ra và GHI ĐÈ
    lên cùng tên tệp trong `data/`. Ngày 16/09 bộ chấm chạy lại: nó nạp kết quả thế
    hệ 6 và đáp án thế hệ 7. Phép kiểm id ở trên KHÔNG bắt được, vì hai thế hệ sinh
    từ cùng danh sách kịch bản nên id trùng nhau — chỉ nội dung lời thoại là khác.

    Kết quả sai đi rõ: bỏ sót của nhánh B từ 15,60% thành 29,39%.

    Phép kiểm: `input` của từng ca trong tệp kết quả phải giống hệt `input` của ca
    cùng id trong bộ dữ liệu. Bản ghi không có `input` thì bỏ qua (tệp cũ).
    """
    lech = [i for i, r in kq.items()
            if "input" in r and r["input"] != goc[i].get("input")]
    if not lech:
        return
    raise SystemExit(
        f"{Path(tep).name}: {len(lech)}/{len(kq)} ca co hoi thoai KHAC bo du lieu hien tai "
        f"(vd {lech[:3]}).\nTep ket qua nay chay tren mot the he du lieu khac. Cham "
        f"no voi dap an nay ra so SAI. Dua dung cap tep ve cung thu muc roi chay lai.")


# ═══ main() — Chạy dòng lệnh chấm đầu ra các nhánh ════════════════════════════════════
# Chặn tập khoá, kiểm lệch thế hệ rồi tổng hợp và in.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", required=True)
    ap.add_argument("--nhanh", nargs="+", required=True)
    # Chấm một thế hệ cũ hoặc một bản tải về từ Kaggle: đưa cả tệp kết quả LẪN bộ dữ
    # liệu sinh ra chúng vào một thư mục rồi trỏ `--thu-muc` vào đó. Dùng `data/` để
    # chấm một thế hệ cũ là cách đã làm ra số sai ngày 16/09/2026.
    ap.add_argument("--thu-muc", default=None,
                    help="thu muc chua ra_*.jsonl VA <tap>.jsonl (mac dinh: data/)")
    ap.add_argument("--hau-to", default="", help="hau to them vao ten tep ket qua")
    a = ap.parse_args()
    from src.bo_du_lieu import nap_du_lieu as du_lieu
    du_lieu.chan_tap_ngoai(a.tap)
    du_lieu.chan_tap_khoa(a.tap)
    d = Path(a.thu_muc) if a.thu_muc else duong_dan.THU_MUC_DU_LIEU
    goc = {c["id"]: c for c in du_lieu.nap_mau(d / f"{a.tap}.jsonl")}
    ra = {}
    for nhanh in a.nhanh:
        tep = d / f"ra_{nhanh}_{a.tap}.jsonl"
        kq = {r["id"]: r for r in du_lieu.nap_mau(tep)}
        la = [i for i in kq if i not in goc]
        if la:
            raise SystemExit(f"{tep.name}: {len(la)} id KHONG co trong {a.tap} "
                             f"(vd {la[:3]}) — mot ten tep, hai bo du lieu?")
        canh_bo_lech_the_he(tep, goc, kq)
        if not all("phat_bieu" in r for r in kq.values()):
            print(f"\n=== {nhanh}: khong co truong phat_bieu — sinh lai bang "
                  f"`--tu-dem` voi ma tu 11/09/2026")
            continue
        cac_ca = [goc[i] for i in kq]
        tk = tong_hop(cac_ca, kq)
        print(f"\n=== {nhanh} tren {a.tap}: {tk['so_ca']} ca")
        for ten, k in tk["bang"].items():
            _in(ten, k)
        tt = cham_thach_thuc(cac_ca, kq)
        if tt:
            print(f"  thach thuc: {tt}")
        ra[nhanh] = {"tong_hop": tk, "thach_thuc": tt, "phien_ban_bo_cham": PHIEN_BAN}
    if any(n.startswith("C_khoa_hoi") for n in ra):
        print("\nHOI LAI: nguoi tra loi MO PHONG la HOAN HAO — so tren la TRAN TREN.")
    dp = duong_dan.THU_MUC_KET_QUA / f"cham-he-thong-{a.tap}{a.hau_to}.json"
    dp.write_text(json.dumps(ra, ensure_ascii=False, indent=2, default=str),
                  encoding="utf-8")
    print(f"\nGhi {dp}")


if __name__ == "__main__":
    main()
