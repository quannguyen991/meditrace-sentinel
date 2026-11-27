# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Đối chứng]
Làm gì   : Dựng hai đường tắt không dùng mô hình (chủ thể là người nói, chủ thể luôn là bệnh
           nhân) để xem hệ thống thật có hơn cả hai.
Vào → Ra : ca hội thoại (--tap) hoặc bộ chẩn đoán (--bo-chan-doan) + tên đường (--duong) →
           bản nháp đối chứng, ghi tệp kết quả
Đọc từ   : sinh_ban_nhap() dựng bản nháp cho một đường tắt; chay() chạy đường tắt trên các
           ca
Mục lục (các hàm/lớp chính):
  tach_luot()            Tách hội thoại thành lượt kèm số thứ tự và vai
  menh_de_bang_luat()    Cắt lượt nói thành mệnh đề thô bằng luật
  phat_bieu_bang_luat()  Dựng mệnh đề thô cho một đường đối chứng
  sinh_ban_nhap()        Dựng bản nháp từ mệnh đề thô của đường đối chứng
  chay()                 Chạy một đường đối chứng trên danh sách ca
  chay_bo_chan_doan()    Chạy các đường đối chứng trên bộ chẩn đoán
  main()                 Chạy dòng lệnh đối chứng tầm thường, ghi tệp kết quả
Gọi tới  : do_luong/do_bo_chan_doan, do_luong/doi_chung_context_vi, bo_du_lieu/nap_du_lieu,
           bo_du_lieu/sinh_bo_chan_doan, duong_ong/b5_viet_ban_nhap
Tên cũ   : doi_chung_tam_thuong.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Hai đối chứng KHÔNG DÙNG MÔ HÌNH. Chúng chặn hai câu hỏi khác nhau.

VÌ SAO CẦN. Tài liệu của dự án đã viết, nhiều lần, rằng "một hệ thống chỉ làm
đúng một việc — gán triệu chứng cho người vừa nói — vẫn đạt độ chính xác cao".
Câu đó LẬP LUẬN chứ không ĐO: không có cấu hình nào chạy đường tắt đó. Người
chấm sẽ tự hỏi đúng câu hỏi đấy, và không có số để trả lời.

    đường tắt A   chủ thể = NGƯỜI NÓI của lượt
    đường tắt B   chủ thể = BỆNH NHÂN, luôn luôn

Hai đường tắt này SAI Ở HAI CHỖ ĐỐI NHAU, và đó là cả ý nghĩa của chúng:

    tầng 3  người nhà kể HỘ bệnh nhân      -> A sai,  B đúng
    tầng 4  người nhà kể VỀ CHÍNH MÌNH     -> A đúng, B sai

Nên một hệ thống thật phải hơn CẢ HAI trên CẢ HAI tầng. Hơn một đường tắt ở
một tầng thì chưa nói lên gì — nó có thể chỉ đang làm đúng việc của đường tắt
kia.

CHÚNG DÙNG CHUNG MỌI KHÂU KHÁC với nhánh B: cùng `sinh_benh_an.sinh`, cùng
bảng tra mục, cùng cách diễn đạt. Chỉ khác ĐÚNG MỘT chỗ — bước trích và bước
gán chủ thể. Nếu khác ở những chỗ lắt vặt thì chênh lệch đo được sẽ lẫn lộn
nguyên nhân.

GIỚI HẠN, phải ghi vào báo cáo. Bước trích ở đây là tách câu bằng luật, thô
hơn mô hình thật nhiều. Nên con số của chúng là SÀN DƯỚI cho cả đường ống, và
đọc đúng phải là "mô hình đóng góp bao nhiêu so với luật thô", không phải
"luật làm được việc này".

    python -m src.do_luong.doi_chung_tam_thuong --tap viet_phat_trien --n 60
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an

# Ba đường tắt. Hai đầu khác nhau ở CÁCH GÁN CHỦ THỂ; đường thứ ba khác ở
# PHẠM VI — nó lấy cả lượt bác sĩ.
#
# VÌ SAO CẦN ĐƯỜNG THỨ BA. Hai đường đầu bỏ hẳn lượt bác sĩ, nên chúng không
# viết kết quả khám, chẩn đoán hay kế hoạch: bao phủ tầng bác sĩ chỉ 4,17%. Một
# sàn dưới bỏ mất một phần ba bản nháp là sàn YẾU GIẢ, và sàn yếu giả làm đường
# ống trông tốt hơn thực tế. `day_du` lấy cả lượt bác sĩ với chủ thể = bệnh
# nhân, và đó là sàn dưới đúng để đối chiếu.
#
# ĐƯỜNG THỨ TƯ (16/09/2026) — `context`. Giống `day_du` ở mọi khâu, chỉ khác cách
# gán chủ thể: dùng bảng từ kiểu ConText (`src/do_luong/doi_chung_context_vi.py`) thay vì hai đường tắt.
# VÌ SAO CẦN: trục chủ thể của dự án có tiền lệ trực tiếp là trục `Experiencer` của
# ConText (Harkema, Chapman và cộng sự, 2009), chạy bằng một bảng từ. Không có đường
# này thì không trả lời được câu "mô hình đóng góp bao nhiêu so với một bảng từ".
DUONG = ("nguoi_noi", "benh_nhan", "day_du", "context", "context_vai")

# Tiểu từ và cụm mở đầu không mang thông tin lâm sàng. Bỏ trước khi tách câu,
# nếu không thì mọi mệnh đề đều bắt đầu bằng "dạ" hoặc "vâng".
RAC_DAU = re.compile(r"^(dạ|vâng|thưa|ừ|à|ạ|thì|vậy|thế)\b[\s,]*", re.I)
RAC_CUOI = re.compile(r"[\s,]*(ạ|nhé|nghen|nghe|đấy|cơ|mà|rồi)\s*$", re.I)

# Câu giao tiếp, không mang thông tin lâm sàng. Giữ lại thì sàn dưới thấp GIẢ
# — và sàn thấp giả làm mô hình trông tốt hơn thực tế, nên phải bỏ.
CAU_GIAO_TIEP = re.compile(
    r"^(cảm ơn|cám ơn|xin cảm ơn|vâng|dạ|được|ok|không có gì|tôi cảm ơn"
    r"|chào|tạm biệt|nhờ bác sĩ|bác sĩ xem)\b", re.I)

# Cụm chuyển ý: tách ở đây vì hai bên thường là hai chủ thể khác nhau.
#   "Tôi thì dị ứng aspirin, CÒN cháu chưa thấy bị bao giờ"
TACH_MENH_DE = re.compile(r"[.;?!]|,\s*(?=còn\b|mà\b|nhưng\b)", re.I)

# Từ mở đầu mệnh đề báo hiệu người nói đang nói VỀ CHÍNH MÌNH.
#
# BẢNG NÀY ĐO TỪ NGỮ LIỆU, không tự phỏng đoán. Ban đầu tôi viết
#
#     ("tôi", "em", "mình", "cháu", "con", "bà", "ông", "mẹ", "bố")
#
# rồi đo trên 681 ca — đếm từ mở đầu của mệnh đề trong lượt NGƯỜI NHÀ, đối chiếu
# với `chu_the` thật trong đáp án:
#
#     từ      về BỆNH NHÂN   về chính mình
#     cháu         438             5
#     con          235             0
#     bà            98             9
#     ông           78             9
#     tôi           28            58
#     em            18            13
#     mẹ             2             7
#     bố             3             7
#
# Bốn từ đầu là NGƯỢC HOÀN TOÀN với giả định của tôi: trong hội thoại khám bệnh
# Việt Nam, người nhà gọi BỆNH NHÂN là "cháu"/"con", và bệnh nhân cao tuổi được
# gọi là "bà"/"ông". Giữ chúng trong bảng này làm đối chứng sai ở đúng tầng 3 —
# tầng đồng nhất trong ba tầng khó.
#
# "em" thì 18/13, gần như tung đồng xu, nên bỏ: một luật đối chứng phải là luật
# RÕ RÀNG, không phải luật đoán bừa.
#
# "mình" không xuất hiện lần nào nhưng giữ lại vì nó không bao giờ mơ hồ.
TU_XUNG_MINH = ("tôi", "mình", "mẹ", "bố")

VAI_BENH_NHAN = ("bệnh nhân",)
VAI_BAC_SI = ("bác sĩ", "điều dưỡng")


# ═══ tach_luot() — Tách hội thoại thành lượt kèm số thứ tự và vai ═════════════════════
# Trả danh sách (số lượt từ 1, vai, nội dung); dòng không có vai thì vai là dấu hỏi.
def tach_luot(hoi_thoai):
    """-> [(so_luot_dem_tu_1, vai, noi_dung_luot)]."""
    ra = []
    for i, dong in enumerate(
            [d for d in str(hoi_thoai or "").split("\n") if d.strip()], 1):
        m = re.match(r"^([^:]{1,30}):\s*(.*)$", dong)
        ra.append((i, m.group(1).strip(), m.group(2).strip()) if m
                  else (i, "?", dong.strip()))
    return ra


# ─── _gon() — Bỏ từ đệm ở đầu và cuối câu ─────────────────────────────────────────────
# Lặp ở đầu vì từ đệm đi thành chùm, như "Vâng ạ, tôi sốt".
def _gon(cau):
    """Bỏ tiểu từ đầu và cuối. Lặp ở đầu vì chúng đi thành chùm.

    "Vâng ạ, tôi sốt ba hôm rồi" -> bỏ một lần được "ạ, tôi sốt ba hôm rồi",
    còn nguyên một tiểu từ ở đầu. Phải lặp cho tới khi không còn.
    """
    cau = cau.strip()
    for _ in range(4):
        moi = RAC_DAU.sub("", cau).lstrip(" ,")
        if moi == cau:
            break
        cau = moi
    cau = RAC_CUOI.sub("", cau)
    return cau.strip(" ,.")


# Câu hỏi của bác sĩ: không mang thông tin lâm sàng. Nhận ra bằng dấu hỏi hoặc
# cụm hỏi ở đầu. Lời bác sĩ còn lại (kết quả khám, chẩn đoán, kế hoạch) thì CÓ
# mang thông tin và phải lấy.
CAU_HOI = re.compile(r"\?|^(có|còn|đã|bao|mấy|nhà mình|cháu có|em có|anh có"
                     r"|chị có|cô có|ngoài ra|từ khi|bị từ)\b", re.I)


# ═══ menh_de_bang_luat() — Cắt lượt nói thành mệnh đề thô bằng luật ═══════════════════
# Mặc định bỏ lượt bác sĩ; nếu lấy thì bỏ câu hỏi. Loại câu giao tiếp và mệnh đề dưới
# hai từ.
def menh_de_bang_luat(hoi_thoai, lay_bac_si=False):
    """-> [(so_luot, vai, noi_dung)].

    `lay_bac_si=False` bỏ hẳn lượt bác sĩ — dùng cho hai đường tắt thuần, để
    chúng chỉ đo ĐÚNG cách gán chủ thể.

    `lay_bac_si=True` lấy thêm lời bác sĩ KHÔNG phải câu hỏi: kết quả khám,
    chẩn đoán, kế hoạch. Không lấy câu hỏi, vì câu hỏi không là mệnh đề lâm
    sàng và đưa vào thì bản nháp đầy rác.
    """
    ra = []
    for so, vai, noi in tach_luot(hoi_thoai):
        if vai.lower() in VAI_BAC_SI:
            if not lay_bac_si or CAU_HOI.search(noi):
                continue
        for phan in TACH_MENH_DE.split(noi):
            if not phan:
                continue
            g = _gon(phan)
            # Dưới 2 từ thì không phải mệnh đề lâm sàng, chỉ là tiểu từ.
            if g and len(g.split()) >= 2 and not CAU_GIAO_TIEP.match(g):
                ra.append((so, vai, g))
    return ra


# ─── _noi_ve_chinh_minh() — Nhận biết mệnh đề mở đầu bằng từ tự xưng ──────────────────
def _noi_ve_chinh_minh(noi_dung):
    """Mệnh đề có dấu hiệu nói về CHÍNH người đang nói không.

    Chỉ dùng cho đường tắt `nguoi_noi`: nó cần biết lượt này là người nói tự
    kể về mình hay kể hộ. Đây vẫn là một luật thô — dùng từ xưng ở đầu mệnh đề.
    """
    dau = (noi_dung or "").strip().lower().split()
    return bool(dau) and dau[0] in TU_XUNG_MINH


# ═══ phat_bieu_bang_luat() — Dựng mệnh đề thô cho một đường đối chứng ═════════════════
# Không gọi mô hình. Năm đường: nguoi_noi, benh_nhan, day_du, context, context_vai; khác
# nhau ở cách gán chủ thể.
def phat_bieu_bang_luat(hoi_thoai, duong="nguoi_noi"):
    """-> danh sách phát biểu thô của một đường đối chứng. KHÔNG gọi mô hình.

    `duong`:
      nguoi_noi  chủ thể = người nói của lượt (bệnh nhân -> 0, người nhà -> 1)
      benh_nhan  chủ thể = 0 cho mọi mệnh đề
      day_du     như `benh_nhan` nhưng lấy cả lời bác sĩ
      context    chủ thể đọc từ bảng từ kiểu ConText (`src/do_luong/doi_chung_context_vi.py`)

    MỘT BẢN MÃ DUY NHẤT (gộp 16/09/2026). Trước đó `sinh_ban_nhap` và `_ps_cua`
    dùng hai bản chép tay khác nhau: bản dùng để CHẤM thiếu hẳn `chu_the_id`, nên
    bản nháp và bảng phát biểu của cùng một đường nói hai điều khác nhau — đúng họ
    lo~i "hai khâu của một dự án dùng hai định nghĩa" mà chính tệp này cảnh báo.
    """
    if duong not in DUONG:
        raise SystemExit(f"duong phai la mot trong {DUONG}")
    ps = []
    for i, (so, vai, noi) in enumerate(
            menh_de_bang_luat(
            hoi_thoai,
            lay_bac_si=(duong in ("day_du", "context", "context_vai")))):
        la_bn_noi = vai.lower() in VAI_BENH_NHAN
        la_bs_noi = vai.lower() in VAI_BAC_SI
        if duong in ("context", "context_vai"):
            # Bảng từ kiểu ConText: chủ thể đọc từ CHÍNH mệnh đề, không từ vai
            # người nói. Lời bác sĩ cũng đi qua cùng một bảng — "bà ngoại có bị
            # tiểu đường không" thì chủ thể là bà ngoại, dù bác sĩ nói.
            from src.do_luong import doi_chung_context_vi as context_vi
            chu_the_id = context_vi.chu_the_cua(noi, vai)
            # `context_vai` = bảng từ CỘNG vai người nói. Vì sao tách làm hai đường:
            # bảng từ kiểu ConText không nhìn vai người nói được, nên nó không thể
            # đúng ở câu "Tôi bị rối loạn lo âu" DO NGƯỜI NHÀ nói — đo trên bộ đối
            # chủ thể 16/09/2026, phần lớn 70 lỗi của đường `context` là đúng câu này.
            # Hai đường cạnh nhau tách được đóng góp của bảng từ khỏi đóng góp của vai.
            if (duong == "context_vai" and chu_the_id == 0
                    and not la_bn_noi and not la_bs_noi
                    and _noi_ve_chinh_minh(noi)):
                chu_the_id = 1
        elif duong == "benh_nhan" or la_bs_noi:
            # Lời bác sĩ: chủ thể luôn là bệnh nhân. Đây không phải đường tắt,
            # đây là đúng — và chính chỗ này `sua_cuc_bo` đã hiểu sai 104 lần.
            chu_the_id = 0
        elif la_bn_noi:
            chu_the_id = 0
        else:
            # Người nhà đang nói. Đường tắt này gán cho NGƯỜI NÓI, tức là
            # người nhà — trừ khi mệnh đề không có dấu hiệu tự xưng, lúc đó
            # gán cho bệnh nhân mới đúng với chính nó ("gán cho người vừa
            # nói" chỉ có nghĩa khi câu nói VỀ người đó).
            chu_the_id = 1 if _noi_ve_chinh_minh(noi) else 0
        # `chu_the` là CHUỖI tên người, `chu_the_id` là số. Giữ cả hai vì các
        # bộ chấm đọc trường khác nhau: `sinh_benh_an` đọc `chu_the_id`, còn
        # `do_bo_chan_doan.kiem_chu_the` đọc `chu_the`. Thiếu một trường thì bộ
        # chấm kia đọc chuỗi rỗng và cho qua hết — nó không báo lỗi.
        ten = "bệnh nhân" if chu_the_id == 0 else vai.lower()
        if chu_the_id == 1 and duong in ("context", "context_vai"):
            # Tên người lấy từ CHÍNH từ đã kích hoạt, không lấy vai người nói: bộ
            # cham doi chieu danh tinh, "người nhà" thay cho "anh trai" van tinh sai.
            from src.do_luong import doi_chung_context_vi as context_vi
            ten = context_vi.ten_chu_the_cua(noi) or vai.lower()
        ps.append({"id": i, "nguoi_noi": vai, "chu_the_id": chu_the_id,
                   "chu_the": ten, "ten_chu_the": ten,
                   "noi_dung": noi, "bang_chung": [so],
                   "do_chac_chan": "chắc chắn", "phu_dinh": False,
                   "tinh_huong": "thực tế", "thoi_gian_su_kien": "chưa rõ",
                   "moc_thoi_gian": None, "trang_thai": "còn hiệu lực",
                   "quan_he": None, "quan_he_voi": None})
    return ps


# ═══ sinh_ban_nhap() — Dựng bản nháp từ mệnh đề thô của đường đối chứng ═══════════════
# Trả (văn bản, ghi chú, số mệnh đề); không gọi mô hình.
def sinh_ban_nhap(hoi_thoai, duong="nguoi_noi", ten_nguoi_nha="người nhà"):
    """-> (van_ban, ghi_chu, so_menh_de). KHÔNG gọi mô hình."""
    ps = phat_bieu_bang_luat(hoi_thoai, duong)
    van, ghi_chu = sinh_benh_an.sinh(ps, id_benh_nhan=0,
                                    ten_chu_the={1: ten_nguoi_nha})
    return van, ghi_chu, len(ps)


# ═══ chay() — Chạy một đường đối chứng trên danh sách ca ══════════════════════════════
# Mỗi ca ra bản ghi cùng định dạng với tệp kết quả các nhánh, số lượt gọi và token bằng
# 0.
def chay(mau_list, duong):
    """-> danh sách bản ghi cùng định dạng `ra_<nhanh>_<tap>.jsonl`."""
    ra = []
    for m in mau_list:
        van, ghi_chu, n = sinh_ban_nhap(m["input"], duong)
        ra.append({"id": m["id"], "input": m["input"],
                   "tham_chieu": m.get("output") or m.get("tham_chieu") or "",
                   "du_doan": van, "du_doan_khong_muc_phu": van,
                   # `phat_bieu` để `cham_he_thong` chấm được đường đối chứng bằng
                   # CÙNG một bộ chấm với đường ống (16/09/2026). Thiếu trường này
                   # thì bộ chấm bỏ qua cả nhánh và in một dòng cảnh báo.
                   "phat_bieu": phat_bieu_bang_luat(m["input"], duong),
                   "ghi_chu": ghi_chu, "so_phat_bieu": n,
                   "so_can_xac_nhan": sum(1 for g in ghi_chu
                                          if g["muc"] == sinh_benh_an.MUC_PHU),
                   "so_luot_goi": 0, "token_vao": 0, "token_ra": 0,
                   "loi_ban_ghi": []})
    return ra


# ═══ chay_bo_chan_doan() — Chạy các đường đối chứng trên bộ chẩn đoán ═════════════════
# Chấm theo từng loại bẫy, không cần GPU; dùng để đo tầng 4 với cỡ mẫu đủ lớn.
def chay_bo_chan_doan(so_moi_bay=60, duong_list=DUONG):
    """Chạy các đường tắt trên BỘ CHẨN ĐOÁN và chấm theo từng tình huống.

    VÌ SAO Ở ĐÂY. Tập phát triển chỉ có **7 mệnh đề tầng 4 trên 514** (1,36%),
    nên mọi số đo trên tầng 4 có khoảng tin cậy vô dụng. Bộ chẩn đoán thì CÂN
    BẰNG: nhóm `chu_the` — "Tôi thì dị ứng X, còn cháu chưa thấy bị" — có đúng
    60 ca, gấp 8,5 lần.

    Đây là chỗ duy nhất hiện có để đo tầng 4 với công suất thật, và nó chạy
    KHÔNG CẦN GPU vì đối chứng không gọi mô hình.
    """
    from src.do_luong import do_bo_chan_doan as do_bo_chan_doan
    from src.bo_du_lieu import sinh_bo_chan_doan as sinh_bo_chan_doan

    bo = sinh_bo_chan_doan.sinh_bo(so_moi_bay, seed=42)
    ra = {}
    for duong in duong_list:
        theo_bay = {}
        for mau in bo:
            _van, _gc, _n = sinh_ban_nhap(mau["input"], duong)
            ps = [p for p in _ps_cua(mau["input"], duong)]
            dat, _ly_do = do_bo_chan_doan.cham(mau, ps)
            theo_bay.setdefault(mau["bay"], []).append(dat)
        ra[duong] = theo_bay
    return ra, bo


# ─── _ps_cua() — Lấy mệnh đề thô của một đường đối chứng ──────────────────────────────
# Dùng chung một bản mã với bản nháp để hai khâu không lệch định nghĩa.
def _ps_cua(hoi_thoai, duong):
    """Phát biểu thô của một đường đối chứng — một bản mã duy nhất với bản nháp."""
    return phat_bieu_bang_luat(hoi_thoai, duong)


# ═══ main() — Chạy dòng lệnh đối chứng tầm thường, ghi tệp kết quả ════════════════════
# Hoặc chạy bộ chẩn đoán và in bảng đạt theo từng loại bẫy và đường.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--duong", nargs="+", default=list(DUONG), choices=DUONG)
    ap.add_argument("--bo-chan-doan", type=int, default=0, metavar="N",
                    help="chay tren bo chan doan, N ca MOI tinh huong")
    a = ap.parse_args()
    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_tap_khoa(a.tap)

    if a.bo_chan_doan:
        ra, bo = chay_bo_chan_doan(a.bo_chan_doan, a.duong)
        from src.bo_du_lieu import sinh_bo_chan_doan as sinh_bo_chan_doan
        print(f"Doi chung khong mo hinh tren {len(bo)} ca bo chan doan "
              f"({len(sinh_bo_chan_doan.BAY)} tinh huong x {a.bo_chan_doan})\n")
        rong = max(len(b) for b in sinh_bo_chan_doan.BAY) + 2
        print(f"{'Tinh huong':{rong}}" +
              "".join(f"{d:>16}" for d in a.duong))
        for bay in sinh_bo_chan_doan.BAY:
            dong = f"{bay:{rong}}"
            for d in a.duong:
                ds = ra[d].get(bay, [])
                dong += (f"{sum(ds)}/{len(ds)} = {100 * sum(ds) / len(ds):.0f}%"
                         .rjust(16) if ds else "—".rjust(16))
            print(dong)
        print(f"\nNhom `chu_the` la tang 4: \"Toi thi di ung X, con chau chua "
              f"thay bi\".\nTap phat trien chi co 7 menh de tang 4 tren 514; "
              f"o day co {a.bo_chan_doan}.")
        return

    tep = Path("data") / f"{a.tap}.jsonl"
    mau = [json.loads(l) for l in open(tep, encoding="utf-8") if l.strip()]
    if a.n:
        mau = mau[:a.n]
    for duong in a.duong:
        kq = chay(mau, duong)
        ra = Path("data") / f"ra_tat_{duong}_{a.tap}.jsonl"
        ra.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in kq),
                      encoding="utf-8")
        print(f"{len(kq)} ca, {sum(r['so_phat_bieu'] for r in kq)} menh de "
              f"-> {ra}")


if __name__ == "__main__":
    main()
