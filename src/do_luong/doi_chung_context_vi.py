# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Đối chứng]
Làm gì   : Gán chủ thể (bệnh nhân hay người khác) bằng luật kiểu ConText: từ kích hoạt, kích
           hoạt giả, hết phạm vi, không dùng mô hình.
Vào → Ra : một câu hoặc lượt thoại → chủ thể bệnh nhân hay người nhà cùng từ kích hoạt để
           giải thích
Đọc từ   : chu_the_cua() quyết định chủ thể một câu; giai_thich() liệt kê phạm vi và từ kích
           hoạt
Mục lục (các hàm/lớp chính):
  chu_the_cua()      Xác định mệnh đề nói về bệnh nhân hay người khác
  ten_chu_the_cua()  Lấy từ chỉ người nhà đã đổi chủ thể
  giai_thich()       Liệt kê từng phạm vi với từ kích hoạt để đọc lại
Gọi tới  : duong_ong/b0_chuan_hoa_phuong_ngu
Dùng bởi : do_luong/doi_chung_tam_thuong
Tên cũ   : context_vi.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đối chứng theo LUẬT cho trục chủ thể, đúng theo lối ConText — tiếng Việt.

VÌ SAO CÓ (16/09/2026). ConText (Harkema, Chapman và cộng sự, 2009) có trục
`Experiencer` với hai giá trị `patient` / `other`, chạy bằng một danh sách từ kích
hoạt cộng phạm vi ảnh hưởng tính từ chỗ từ kích hoạt đến hết câu. Đó là tiền lệ
trực tiếp của trục chủ thể trong dự án này, nên phải có một bản tiếng Việt để đối
chiếu: mô hình đóng góp bao nhiêu SO VỚI một bảng từ.

ConText dùng 26 từ kích hoạt và 18 từ kích hoạt GIẢ cho giá trị `other`. Bản này
nhỏ hơn vì bộ sinh chỉ dùng một số vai người nhà cố định.

BA BỘ PHẬN, đúng như ConText:

  từ kích hoạt   từ chỉ NGƯỜI NHÀ ("bố", "mẹ", "bà ngoại"...) -> thông tin là của
                 người đó, không phải của bệnh nhân
  kích hoạt GIẢ  cùng từ đó nhưng trong vai NGƯỜI ĐƯA ĐI KHÁM hoặc NGƯỜI KỂ, không
                 phải người mang bệnh: "mẹ đưa cháu đi khám", "bà kể là cháu ho".
                 Không có bộ phận này thì mọi câu người nhà kể hộ đều bị gán sai.
  hết phạm vi    dấu câu, và các liên từ đối lập ("còn", "nhưng") — "bà ngoại thì dị
                 ứng penicillin, còn cháu chưa bị bao giờ" doi chu the giua chung cau

GIỚI HẠN PHẢI GHI VÀO BÁO CÁO. Bảng từ này chọn từ VAI NGƯỜI NHÀ mà bộ sinh dùng
(`ngu_lieu_viet.NGUOI_NHA`, `VAI_NU`, `VAI_NAM`), KHÔNG chọn bằng cách nhìn vào tập
đánh giá. Một bảng từ chọn từ chính tập đánh giá sẽ cho một con số cao giả.
"""
import re

from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa

# Từ chỉ người nhà — từ kích hoạt. Lấy từ các vai bộ sinh thật sự dùng.
TU_NGUOI_NHA = (
    "bà ngoại", "bà nội", "ông ngoại", "ông nội", "anh trai", "chị gái",
    "em trai", "em gái", "con trai", "con gái", "bố", "mẹ", "ba", "má",
    "vợ", "chồng",
)

# KHÔNG đưa vào bảng: "ba", "ông", "anh", "chị", "cháu", "con" ĐÚNG MỘT ÂM. Trong
# hội thoại khám tiếng Việt đó là cách gọi CHÍNH BỆNH NHÂN, không phải người nhà —
# đo trên 681 ca của chính kho này (bảng đếm ở `doi_chung_tam_thuong.TU_XUNG_MINH`):
# "cháu" 438 lần chỉ bệnh nhân so với 5 lần chỉ người nói, "ba" 98 so với 9, "ông"
# 78 so với 9. Ban đầu tôi CÓ đưa chúng vào, và đo được trên bộ đổi chủ thể ngày
# 16/09/2026: tỷ lệ sai chủ thể trên mệnh đề ghép được là 20,00%, TỆ HƠN cả đường
# "luôn gán cho bệnh nhân" (13,14%). Đây đúng là chỗ ConText không chuyển thẳng sang
# tiếng Việt được: tiếng Anh không gọi bệnh nhân bằng từ thân tộc.

# Động từ làm cho từ chỉ người nhà thành NGƯỜI ĐƯA ĐI hoặc NGƯỜI KỂ, không phải
# người mang bệnh. Xét trong một cửa sổ ngắn ngay sau từ kích hoạt.
DONG_TU_KICH_HOAT_GIA = (
    "đưa", "dẫn", "chở", "bế", "ẵm", "kể", "nói", "bảo", "trình bày", "hỏi",
    "thấy", "sờ", "đo", "nhắc",
    # "cho" một mình: trong "bố cho cháu uống hạ sốt", người nhà là người CHO, còn
    # người uống là bệnh nhân. Rộng hơn các từ trên nhưng vẫn là vai tác nhân.
    "cho",
)

# Hết phạm vi ảnh hưởng: dấu câu, hoặc liên từ đối lập.
LIEN_TU_DOI_LAP = ("còn", "nhưng", "riêng")

_CUA_SO_TU = 4          # số từ sau từ kích hoạt còn xét là kích hoạt giả


# ─── _tach_pham_vi() — Cắt mệnh đề thành các phạm vi nhỏ ──────────────────────────────
# Cắt theo dấu câu và liên từ đối lập như còn, nhưng, riêng.
def _tach_pham_vi(cau: str):
    """Cắt một mệnh đề thành các PHẠM VI: dấu phẩy, dấu chấm, và liên từ đối lập."""
    tho = re.split(r"[.;,?!]", cau)
    ra = []
    for phan in tho:
        con = [phan]
        for lt in LIEN_TU_DOI_LAP:
            moi = []
            for x in con:
                moi.extend(re.split(rf"(?<!\w){lt}(?!\w)", x))
            con = moi
        ra.extend(c.strip() for c in con if c.strip())
    return ra


# ─── _kich_hoat() — Tìm từ chỉ người nhà và xét có phải kích hoạt giả ─────────────────
# Kích hoạt giả là khi động từ như đưa, kể đứng ngay sau từ chỉ người nhà (cửa sổ 4 từ).
def _kich_hoat(pham_vi: str):
    """-> (từ kích hoạt, có phải kích hoạt giả) hoặc (None, False)."""
    t = chuan_hoa.chuan_hoa(pham_vi).lower()
    tim = None
    for tu in sorted(TU_NGUOI_NHA, key=len, reverse=True):
        m = re.search(rf"(?<!\w){re.escape(tu)}(?!\w)", t)
        if m and (tim is None or m.start() < tim[1]):
            tim = (tu, m.start(), m.end())
    if tim is None:
        return None, False
    tu, _a, b = tim
    sau = t[b:].split()[:_CUA_SO_TU]
    doan_sau = " ".join(sau)
    gia = any(re.search(rf"(?<!\w){re.escape(d)}(?!\w)", doan_sau)
              for d in DONG_TU_KICH_HOAT_GIA)
    return tu, gia


# ═══ chu_the_cua() — Xác định mệnh đề nói về bệnh nhân hay người khác ═════════════════
# Trả 0 là bệnh nhân, 1 là người khác. Có từ chỉ người nhà và không phải kích hoạt giả
# thì là 1.
def chu_the_cua(cau: str, vai_nguoi_noi: str = "") -> int:
    """-> 0 nếu mệnh đề nói VỀ BỆNH NHÂN, 1 nếu nói về một người khác.

    Luật, theo thứ tự:
      1. Có từ chỉ người nhà và KHÔNG phải kích hoạt giả -> người khác.
      2. Còn lại -> bệnh nhân. Kể cả khi người nhà đang nói: người nhà kể HỘ là
         trường hợp thường gặp nhất, và ConText cũng mặc định `patient`.
    """
    for pv in _tach_pham_vi(cau):
        tu, gia = _kich_hoat(pv)
        if tu and not gia:
            return 1
    return 0


# ═══ ten_chu_the_cua() — Lấy từ chỉ người nhà đã đổi chủ thể ══════════════════════════
# Trả từ kích hoạt như bà ngoại, hoặc None nếu chủ thể là bệnh nhân.
def ten_chu_the_cua(cau: str):
    """-> TỪ KÍCH HOẠT đã làm đổi chủ thể ("bà ngoại"), hoặc None nếu là bệnh nhân.

    Can rieng ham nay vi bo cham doi chieu ca DANH TINH: ghi "người nhà" trong khi
    đáp án ghi "anh trai" vẫn là sai chủ thể (xem `cham_he_thong.dung_nguoi`). Trước
    khi có hàm này, đường đối chứng ghi tên theo VAI NGƯỜI NÓI nên mọi mệnh đề về
    người nhà đều mang tên "người nhà" — 22/68 lỗi chủ thể ngày 16/09/2026 là vì thế.
    """
    for pv in _tach_pham_vi(cau):
        tu, gia = _kich_hoat(pv)
        if tu and not gia:
            return tu
    return None


# ═══ giai_thich() — Liệt kê từng phạm vi với từ kích hoạt để đọc lại ══════════════════
# Mỗi phần tử gồm phạm vi, từ kích hoạt, cờ kích hoạt giả; dùng khi chấm tay.
def giai_thich(cau: str) -> list:
    """-> [(phạm vi, từ kích hoạt, là kích hoạt giả)] — để đọc lại khi chấm tay."""
    return [(pv,) + _kich_hoat(pv) for pv in _tach_pham_vi(cau)]
