# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Nạp và chia]
Làm gì   : Đọc, tách lượt thoại và thống kê bộ hội thoại, đồng thời chặn bằng mã việc chạm
           tập kiểm tra cuối hay dữ liệu GPT.
Vào → Ra : đường dẫn JSONL / danh sách tên tập → danh sách mẫu, cặp (vai, nội dung), thống
           kê; ném lỗi nếu tập bị cấm
Đọc từ   : nap_mau() đọc JSONL; chan_tap_khoa() chặn tập kiểm tra cuối; chan_du_lieu_gpt()
           chặn huấn luyện trên dữ liệu GPT
Mục lục (các hàm/lớp chính):
  nap_mau()               Đọc tệp JSONL thành danh sách mẫu
  ghi_mau()               Ghi danh sách mẫu ra tệp JSONL
  tach_luot_thoai()       Tách hội thoại thành các cặp (vai, nội dung)
  loc_mau_co_nguoi_nha()  Lọc các mẫu có lượt người nhà
  chan_tap_khoa()         Chặn chạm vào tập kiểm tra cuối trước Cửa 5
  chan_tap_ngoai()        Chặn đọc tập của cuộc thi cũ nếu không chủ ý
  chan_du_lieu_gpt()      Từ chối huấn luyện trên dữ liệu do GPT sinh
  thong_ke()              Thống kê số mẫu, lượt theo vai, mẫu người nhà, mẫu nhi
Dùng bởi : do_luong/cham_chu_the, do_luong/cham_he_thong, do_luong/cham_lai_bang_quy_gan,
           do_luong/cham_muc_thach_thuc, do_luong/chung_chi_thuoc_do,
           do_luong/dau_vet_nguon, do_luong/do_bit_nhan, do_luong/do_bo_chan_doan … (tổng 26
           tệp)
Tên cũ   : du_lieu.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nạp và lọc bộ dữ liệu hội thoại y khoa.

Bốn tập được chia ở `tach_tap.py`, không chia ở đây. Module này chỉ lo
việc đọc, tách lượt thoại và thống kê.
"""
import json
import re
from collections import Counter

# Mỗi lượt thoại nằm trên một dòng, bắt đầu bằng tên vai rồi dấu hai chấm.
VAI_RE = re.compile(r"^\s*([^:]{1,20}?)\s*:\s*(.*)$")
NGUOI_NHA_RE = re.compile(r"(?mi)^\s*Người nhà\s*:")

# ---------------------------------------------------------------- nhận diện ca nhi
#
# BẢN 1 (bỏ ngày 05/09/2026) chỉ khớp từ khoá:
#     (cháu|bé |con tôi|con em|trẻ|nhi khoa|sơ sinh|tháng tuổi|em bé)
# Kiểm tay 30 mẫu cho ra 16/30 đúng = 53%, dưới ngưỡng 80% của Cửa 1.
# Bốn kiểu sai:
#     "hồi trẻ em có hút"     — trạng từ chỉ thời gian, bệnh nhân là người lớn
#     "aspirin trẻ em"        — "tre em" lam dinh ngu cho thuoc
#     "chú có mấy cháu rồi"   — cháu nội/ngoại của bệnh nhân người lớn
#     "cô còn trẻ mà"         — thanh ngu
#
# BẢN 2: đòi hỏi TRẺ PHẢI LÀ BỆNH NHÂN. Một cụm khẳng định, và không dính
# bất kỳ cụm loại trừ nào. Đo lại ở `docs/ket-qua/kiem-tay-nhan-nhi.md`.

_NHI_DUONG = re.compile(
    r"(?i)("
    r"em bé|sơ sinh|sinh non|tháng tuổi|nhi khoa|"
    r"(bé|cháu)\s+(bị|sốt|ho|nôn|ngã|khóc|đau|mệt|tăng cân|sinh)|"
    r"khám\s+cho\s+(bé|cháu|con)|"
    r"(bé|cháu)\s+(nhà|năm nay|được)\s|"
    r"(lịch sử sinh|cân nặng lúc sinh|tiêm chủng)\s+của\s+(bé|cháu)|"
    r"mẹ\s+của\s+(bé|cháu)|"
    r"con\s+(trai|gái)\s+(em|tôi|chị|anh)\s|"
    r"(con|bé)\s+bú"
    r")"
)

_NHI_AM = re.compile(
    r"(?i)("
    r"hồi trẻ|còn trẻ|trẻ lại|thời trẻ|lúc trẻ|"
    r"trẻ em\s+(có|vào|uống)|aspirin trẻ em|"
    r"cháu (nội|ngoại)|(mấy|các|hai|ba|bốn|những) (đứa )?cháu|"
    r"có\s+(mấy|hai|ba|bốn|một)\s+(đứa\s+)?(cháu|bé)"
    r")"
)


# ═══ co_dau_hieu_nhi() — Nhận biết mẫu có bệnh nhân là trẻ em ═════════════════════════
# Đúng khi trẻ là bệnh nhân, không phải khi chỉ nhắc đến trẻ.
def co_dau_hieu_nhi(mau):
    """True khi TRẺ là bệnh nhân, không phải khi hội thoại có nhắc tới trẻ."""
    t = mau["input"]
    return bool(_NHI_DUONG.search(t)) and not bool(_NHI_AM.search(t))


# Giữ lại bản 1 để báo cáo mức cải thiện; không dùng ở chỗ nào khác.
NHI_RE_BAN1 = re.compile(r"(?i)(cháu|bé |con tôi|con em|trẻ|nhi khoa|sơ sinh|tháng tuổi|em bé)")


# ═══ nap_mau() — Đọc tệp JSONL thành danh sách mẫu ════════════════════════════════════
# Mỗi dòng không trống là một dict.
def nap_mau(duong_dan):
    """Đọc một tệp jsonl thành danh sách dict."""
    with open(duong_dan, encoding="utf-8") as f:
        return [json.loads(dong) for dong in f if dong.strip()]


# ═══ ghi_mau() — Ghi danh sách mẫu ra tệp JSONL ═══════════════════════════════════════
# Giữ nguyên dấu tiếng Việt.
def ghi_mau(duong_dan, mau_list):
    """Ghi danh sách dict ra jsonl, giữ nguyên dấu tiếng Việt."""
    with open(duong_dan, "w", encoding="utf-8") as f:
        for m in mau_list:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


# ═══ tach_luot_thoai() — Tách hội thoại thành các cặp (vai, nội dung) ═════════════════
# Dòng không đúng định dạng bị bỏ qua.
def tach_luot_thoai(hoi_thoai):
    """Trả về [(vai, noi_dung), ...]. Bỏ qua dòng không khớp định dạng."""
    ket_qua = []
    for dong in hoi_thoai.split("\n"):
        m = VAI_RE.match(dong)
        if m:
            ket_qua.append((m.group(1).strip(), m.group(2).strip()))
    return ket_qua


# ═══ co_nguoi_nha() — Kiểm tra mẫu có lượt nói của người nhà không ════════════════════
# Dò mẫu người nhà trong phần hội thoại.
def co_nguoi_nha(mau):
    return bool(NGUOI_NHA_RE.search(mau["input"]))


# ═══ loc_mau_co_nguoi_nha() — Lọc các mẫu có lượt người nhà ═══════════════════════════
# Giữ mẫu mà co_nguoi_nha đúng.
def loc_mau_co_nguoi_nha(mau_list):
    return [m for m in mau_list if co_nguoi_nha(m)]


# ═══ thong_ke() — Thống kê số mẫu, lượt theo vai, mẫu người nhà, mẫu nhi ══════════════
# Trả từ điển số liệu tổng quan của bộ.
def thong_ke(mau_list):
    vai = Counter()
    for m in mau_list:
        for v, _ in tach_luot_thoai(m["input"]):
            vai[v] += 1
    nguoi_nha = [m for m in mau_list if co_nguoi_nha(m)]
    nhi = [m for m in mau_list if co_dau_hieu_nhi(m)]
    return {
        "tong": len(mau_list),
        "luot_theo_vai": dict(vai),
        "so_mau_nguoi_nha": len(nguoi_nha),
        "so_mau_nhi": len(nhi),
        "so_mau_ca_hai": len([m for m in nguoi_nha if co_dau_hieu_nhi(m)]),
    }


# --------------------------------------------------- chốt bảo vệ Cửa 5

TAP_KHOA = "kiem_tra_cuoi"
# Biến môi trường mở chốt — CHỈ đặt sau Cửa 5 (khoá thiết kế), và ghi vào
# docs/NHAT-KY.md ngay lúc đặt. Giống `CHO_PHEP_TAP_NGOAI`: một việc có chủ
# định, không phải một giá trị mặc định.
MO_TAP_KHOA = "MEDITRACE_MO_TAP_KHOA"

# ------------------------------------------- chốt chặn dữ liệu của cuộc thi cũ
#
# Bốn tập này là BẢN SAO dữ liệu của một cuộc thi NLP, không phải dữ liệu của
# dự án. Ban tổ chức khuyên không dùng tài sản của họ để tránh câu hỏi về tính
# chính thống, và đo dấu vết cho thấy bộ đó rất nhiều khả năng là BẢN DỊCH từ
# tiếng Anh (`src/do_luong/dau_vet_nguon.py`).
#
# Chặn bằng MÃ chứ không bằng trí nhớ, vì cái bẫy ở đây rất kín: `nhanh.py`
# từng để `--tap` mặc định là "phat_trien", nên chạy lệnh mặc định là đọc phải
# dữ liệu cuộc thi mà không ai định làm thế.
TAP_NGOAI = ("train", "phat_trien", "kiem_tra_cuoi", "kiem_tra_chung",
             "train_tang_cuong")

CHO_PHEP_TAP_NGOAI = "MEDITRACE_CHO_PHEP_TAP_NGOAI"


# ═══ chan_tap_ngoai() — Chặn đọc tập của cuộc thi cũ nếu không chủ ý ══════════════════
# Chỉ qua được khi đặt biến môi trường cho phép tập ngoài.
def chan_tap_ngoai(cac_tap):
    """Ném lỗi nếu ai đó đọc tập của cuộc thi cũ mà không nói rõ ý định.

    Không xoá hẳn đường đọc: phép đo dấu vết nguồn gốc (`dau_vet_nguon.py`) là
    một kết quả thật của dự án và cần chạy lại được. Nhưng nó phải là một việc
    CÓ CHỦ ĐỊNH, đặt biến môi trường `MEDITRACE_CHO_PHEP_TAP_NGOAI=1`, chứ không
    phải thứ xảy ra vì một giá trị mặc định.
    """
    import os
    if os.environ.get(CHO_PHEP_TAP_NGOAI):
        return
    ten = [cac_tap] if isinstance(cac_tap, str) else list(cac_tap)
    ngoai = [t for t in ten if t in TAP_NGOAI]
    if ngoai:
        raise SystemExit(
            f"TU CHOI: {', '.join(ngoai)} la du lieu cua cuoc thi cu, khong "
            f"phai cua du an.\n"
            f"Bo tu sinh tuong ung: viet_train / viet_phat_trien / "
            f"viet_kiem_tra_cuoi.\n"
            f"Neu that su can doc (vi du chay lai phep do dau vet nguon goc) "
            f"thi dat {CHO_PHEP_TAP_NGOAI}=1, va ghi vao docs/NHAT-KY.md.")


# ------------------------------------------- chốt chặn dữ liệu do GPT sinh
#
# Bộ 500 hội thoại phương ngữ và hai từ điển kèm theo do GPT sinh (người dùng
# xác nhận 11/09/2026). Dự án không dùng mô hình ngôn ngữ thương mại ở bất kỳ
# khâu nào, kể cả sinh dữ liệu huấn luyện — nên dữ liệu đó CHỈ ĐỂ ĐO. Mọi tệp
# chuyển từ bộ đó mang chữ "gpt" trong tên (`src.bo_du_lieu.nap_bo_gpt500`), và mọi đường huấn
# luyện gọi hàm này, cả tệp train lẫn tệp val (val chọn checkpoint, tức là cũng
# ảnh hưởng mô hình). KHÔNG có biến môi trường mở chốt: không có lý do chính đáng
# nào để huấn luyện trên nó.
DAU_DU_LIEU_GPT = "gpt"


# ═══ chan_du_lieu_gpt() — Từ chối huấn luyện trên dữ liệu do GPT sinh ═════════════════
# Dữ liệu GPT chỉ để đo; nhận ra qua dấu trong tên tệp.
def chan_du_lieu_gpt(cac_tep):
    import os
    ten = [cac_tep] if isinstance(cac_tep, (str, os.PathLike)) else list(cac_tep)
    bi_chan = [str(t) for t in ten
               if t and DAU_DU_LIEU_GPT in os.path.basename(str(t)).lower()]
    if bi_chan:
        raise SystemExit(
            f"TU CHOI HUAN LUYEN tren {', '.join(bi_chan)}: du lieu do GPT sinh "
            f"chi de do, khong de huan luyen (docs/nguon-du-lieu.md).")


# ═══ chan_tap_khoa() — Chặn chạm vào tập kiểm tra cuối trước Cửa 5 ════════════════════
# Gõ nhầm tập này là bị chặn bằng mã, không dựa vào việc nhớ.
def chan_tap_khoa(cac_tap):
    """Ném lỗi nếu ai đó định chạm vào tập kiểm tra cuối trước Cửa 5.

    Kế hoạch ghi: "Tập kiểm tra cuối chỉ mở sau Cửa 5. Mở sớm là hỏng toàn bộ
    phần đánh giá." Hỏng theo kiểu không lấy lại được — một khi đã nhìn số trên
    tập đó thì mọi lựa chọn sau đều có thể bị ảnh hưởng, và không có cách nào
    chứng minh là không.

    Một dòng `--tap kiem_tra_cuoi` gõ nhầm là đủ. Chặn bằng mã chứ không tin
    vào việc nhớ.
    """
    import os
    if os.environ.get(MO_TAP_KHOA):
        return
    ten = [cac_tap] if isinstance(cac_tap, str) else list(cac_tap)
    # Khớp CHUỖI CON, không khớp nguyên tên. LO~ ĐÃ TỒN TẠI đến 11/09/2026: tập
    # kiểm tra cuối của bộ tự sinh tên là `viet_kiem_tra_cuoi`, còn chốt này chỉ
    # so `"kiem_tra_cuoi" in ten` — tức so NGUYÊN TÊN, tên của bộ dữ liệu cuộc
    # thi cũ. Với bộ dữ liệu đang dùng, chốt không chặn gì cả; và `nhanh.py` —
    # script chạy nhiều nhất — còn không gọi nó.
    bi_chan = [t for t in ten if TAP_KHOA in str(t)]
    if bi_chan:
        raise SystemExit(
            f"TU CHOI: tap `{bi_chan[0]}` chi duoc mo sau Cua 5 (khoa thiet ke).\n"
            "Neu that su da qua Cua 5 thi bo chan nay co chu dinh, "
            "va ghi vao docs/NHAT-KY.md.")
