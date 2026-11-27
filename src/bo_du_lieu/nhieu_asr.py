# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ thử thách]
Làm gì   : Làm nhiễu lời thoại giống lỗi máy nhận dạng giọng nói (bỏ dấu, sai từ) để thử độ
           bền, chỉ dùng để đo.
Vào → Ra : ca hoặc dòng thoại + rng + tỷ lệ → ca / dòng đã nhiễu, trích dẫn đáp án sửa theo
Đọc từ   : nhieu_ca() làm nhiễu cả ca; nhieu_dong() làm nhiễu một dòng; nhieu_trich() sửa
           trích dẫn khớp lời nhiễu
Mục lục (các hàm/lớp chính):
  nhieu_ca()     Làm nhiễu cả một ca như đầu ra của máy chép giọng nói
  nhieu_dong()   Làm nhiễu một lượt nói, giữ nhãn vai ở đầu dòng
  nhieu_trich()  Ánh xạ câu trích sang đoạn tương ứng đã làm nhiễu
  nhieu_tu()     Làm nhiễu một từ bằng cách bỏ dấu theo xác suất
  bo_dau()       Bỏ toàn bộ dấu tiếng Việt khỏi một từ
  bo_dau_cau()   Bỏ dấu câu nhưng giữ dấu giữa hai chữ số
Gọi tới  : do_luong/thuoc_do_quy_gan
Dùng bởi : bo_du_lieu/sinh_bo_thach_thuc
Tên cũ   : nhieu_asr.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nhiều ASR — làm bản ghi lời thoại giống đầu ra máy nhận dạng tiếng nói.

VÌ SAO CẦN TRỤC NÀY. Bộ dữ liệu tự sinh đang có là văn bản SẠCH: đủ dấu, đủ dấu
câu, viết hoa đúng chỗ. Hội thoại khám thật không đến dưới dạng đó — nó đến qua
một máy nhận dạng tiếng nói, và cái ra là văn bản mất dấu, mất dấu câu, ngắt câu
sai chỗ. Nếu không bao giờ đo trên dạng đó thì mọi kết luận của dự án chỉ đúng
cho một dạng đầu vào không tồn tại.

RÀNG BUỘC CỨNG: NHIỄU KHÔNG ĐƯỢC ĐỔI ĐÁP ÁN. Bộ này đo "hệ thống còn hiểu đúng
không khi chữ xấu đi", chứ không đo "hệ thống đoán được chữ bị xóa". Nên phép
làm nhiễu ở đây:

  1. GIỮ NGUYÊN SỐ TỪ. Mỗi từ vào một từ ra. Nhờ thế, đoạn trích dẫn trong đáp án
     ánh xạ lại được theo CHỈ SỐ TỪ, và `khoa_bang_chung` vẫn kiểm được K1.
  2. KHÔNG ĐỤNG TỚI TỪ CHỈ NGƯỜI, TỪ PHỦ ĐỊNH VÀ TỪ SỐ. Bỏ dấu những từ này là
     ĐỔI SỰ THẬT chứ không phải làm nhiễu:
         "bà"  -> "ba"   bà biến thành ba — đúng lỗi quy gán của dự án
         "mẹ"  -> "me"   mẹ lẫn với "me" trong "mẹ con"
         "năm" -> "nam"  năm (số 5) lẫn với nam (giới tính, miền Nam)
         "không" -> "khong"  còn đọc ra được, nhưng một chữ sai là mất phủ định
     Bỏ qua ba nhóm này là cách duy nhất giữ đáp án còn đúng sau khi làm nhiễu.

VÌ SAO KHÔNG DÙNG BẢNG ĐỒNG ÂM. Cám dỗ là đổi "sốt" -> "xốt", "chuẩn" -> "chân".
Nhưng khi đo hệ thống PHẢI đoán ngược lại, mà không phải lúc nào người thật cũng
đoán được — phép thử sẽ đo một thứ không ai giải được, và số liệu thu về không
nói lên điều gì. Hai hiện tượng ở đây (mất dấu, mất dấu câu) thì người đọc nào
cũng khôi phục được từ ngữ cảnh, nên chúng đo đúng cái cần đo.

CHỈ DÙNG Ở TẬP ĐÁNH GIÁ. Không khâu huấn luyện nào gọi tệp này — xem
`tests/test_nhieu_asr.py`. Cùng một lẽ với bảng phương ngữ: nếu bộ sinh và hệ
thống cùng biết một bảng, phép thử chỉ đo "hệ thống có áp dụng đúng bảng của nó".
"""
import re
import unicodedata

from src.do_luong.thuoc_do_quy_gan import (
    TU_BENH_NHAN,
    TU_NGUOI_NHA,
    TU_NGUOI_NHA_KHONG_NHAN_DIEN,
)

# Từ số và từ chỉ thời gian: bỏ dấu là đổi giá trị hoặc lẫn nghĩa.
TU_SO = (
    "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười",
    "mươi", "trăm", "nghìn", "rưỡi", "nửa", "vài",
)
TU_PHU_DINH = ("không", "chưa", "chẳng", "đừng", "khỏi", "hết", "còn")
TU_THOI_GIAN = ("hôm", "ngày", "tuần", "tháng", "năm", "giờ", "sáng", "chiều",
                "tối", "đêm", "trưa", "nay", "qua", "kia", "mai", "mốt")

# MỘT bảng duy nhất cho cả tệp. Gồm từ ba bảng đã có trong dự án thay vì gõ lại:
# hai bảng cùng nghĩa ở hai tệp là cách chúng trôi nhau (bài học đã ghi trong
# `phat_bieu`).
TU_CAM = frozenset(
    t
    for nhom in (TU_BENH_NHAN, TU_NGUOI_NHA, TU_NGUOI_NHA_KHONG_NHAN_DIEN,
                 TU_SO, TU_PHU_DINH, TU_THOI_GIAN)
    for cum in nhom
    for t in cum.split()
)

DAU_CAU = ",.?!;:"
_CHU = re.compile(r"[^\W\d_]", re.UNICODE)


# ═══ bo_dau() — Bỏ toàn bộ dấu tiếng Việt khỏi một từ ═════════════════════════════════
# Kể cả đ thành d; giữ dấu câu đi kèm.
def bo_dau(tu: str) -> str:
    """Bỏ toàn bộ dấu tiếng Việt, kể cả `đ` -> `d`. Giữ nguyên dấu câu đi kèm."""
    tach = unicodedata.normalize("NFD", tu)
    khong_dau = "".join(c for c in tach if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", khong_dau).replace("đ", "d").replace("Đ", "D")


# ═══ bo_dau_cau() — Bỏ dấu câu nhưng giữ dấu giữa hai chữ số ══════════════════════════
# Tránh biến 38,5 thành 385 vì đó là đổi giá trị.
def bo_dau_cau(van: str) -> str:
    """Bỏ dấu câu, NHƯNG giữ dấu phẩy/chấm nằm giữa hai chữ số.

    "38,5 độ" mà bỏ dấu phẩy thì thành "385 độ" — đó là ĐỔI GIÁ TRỊ, đúng cái mà
    tệp này cấm. Bẫy này xuất hiện ngay lần chạy thử đầu tiên, và nó không lộ ra
    ở chỗ nào khác: câu văn vẫn đọc trôi, chỉ có con số là sai.
    """
    ra = []
    for i, c in enumerate(van):
        if c in DAU_CAU:
            truoc = van[i - 1] if i else ""
            sau = van[i + 1] if i + 1 < len(van) else ""
            if c in ",." and truoc.isdigit() and sau.isdigit():
                ra.append(c)
            continue
        ra.append(c)
    return "".join(ra)


# ─── _goc() — Lấy phần chữ của một từ, bỏ dấu câu hai đầu ─────────────────────────────
# Dùng để tra bảng từ cấm.
def _goc(tu: str) -> str:
    """Phần chữ của một từ, bỏ dấu câu hai đầu — để tra bảng TU_CAM."""
    return tu.strip(DAU_CAU + '"“”‘’()').lower()


# ═══ cam_dung() — Kiểm tra từ có thuộc nhóm không được động tới ═══════════════════════
# Từ cấm, từ rỗng hoặc có chữ số đều không được làm nhiễu.
def cam_dung(tu: str) -> bool:
    """Từ này có thuộc nhóm KHÔNG được đụng tới không."""
    g = _goc(tu)
    return (not g) or (g in TU_CAM) or any(c.isdigit() for c in g)


# ═══ nhieu_tu() — Làm nhiễu một từ bằng cách bỏ dấu theo xác suất ═════════════════════
# Từ thuộc nhóm cấm giữ nguyên.
def nhieu_tu(tu: str, rng, ti_le: float) -> str:
    """Một từ -> một từ. Bỏ dấu theo xác suất, trừ các từ trong TU_CAM."""
    if cam_dung(tu) or not _CHU.search(tu):
        return tu
    return bo_dau(tu) if rng.random() < ti_le else tu


# ═══ nhieu_dong() — Làm nhiễu một lượt nói, giữ nhãn vai ở đầu dòng ═══════════════════
# Nhãn vai là của bộ sinh, không phải lời của ai nên không được làm nhiễu.
def nhieu_dong(dong: str, rng, ti_le: float = 0.5,
               xoa_dau_cau: bool = True) -> str:
    """Làm nhiễu MỘT lượt thoại, giữ nguyên nhãn vai ở đầu dòng.

    Nhãn vai ("Bác sĩ:", "Bệnh nhân:") là thứ bộ sinh đặt ra để đánh số lượt,
    không phải lời ai nói — máy nhận dạng không sinh ra nó, và `khoa_bang_chung`
    dựa vào nó để biết ai nói. Làm nhiễu chỗ đó là phá công cụ đo, không phải làm
    khó bài toán.
    """
    vai, ngan, than = dong.partition(": ")
    if not ngan:
        vai, than = "", dong

    tu = than.split(" ")
    ra = [nhieu_tu(t, rng, ti_le) for t in tu]
    assert len(ra) == len(tu), "phep lam nhieu phai giu nguyen so tu"

    van = " ".join(ra)
    if xoa_dau_cau:
        # Bỏ dấu câu và viết thường chữ đầu: đầu ra ASV thường không có cả hai.
        van = bo_dau_cau(van)
        van = re.sub(r"\s{2,}", " ", van).strip()
        if van:
            van = van[0].lower() + van[1:]
    return f"{vai}{ngan}{van}" if ngan else van


# ═══ nhieu_trich() — Ánh xạ câu trích sang đoạn tương ứng đã làm nhiễu ════════════════
# Trả None nếu câu trích không nằm trong dòng này; ánh xạ theo chỉ số từ.
def nhieu_trich(trich: str, dong_goc: str, dong_nhieu: str):
    """Đoạn trích dẫn trong đáp án -> đoạn tương ứng trong bản đã làm nhiễu.

    Trả `None` khi đoạn không nằm trong dòng này — để bên gọi còn biết mà thử
    dòng khác. Trả nguyên đoạn cũ thì không phân biệt được "tìm thấy mà không
    đổi gì" với "không tìm thấy", và lần chạy thử đầu tiên đã sai đúng chỗ đó.

    Ánh xạ theo CHỈ SỐ TỪ, đúng được vì phép làm nhiễu giữ nguyên số từ. Số khớp
    sau khi BỐC DẤU CÂU hai đầu mỗi từ: đáp án trích "… rồi rồi" còn lời thoại
    ghi "… rồi rồi." — dính dấu chấm ở từ cuối là đủ để trượt cả đoạn.
    """
    def than(d):
        _, ngan, t = d.partition(": ")
        return (t if ngan else d).split(" ")

    def boc(ds):
        return [t.strip(DAU_CAU) for t in ds]

    tu_goc, tu_nhieu = than(dong_goc), than(dong_nhieu)
    if len(tu_goc) != len(tu_nhieu):
        return None

    goc_boc, tu_trich = boc(tu_goc), boc(trich.split(" "))
    n = len(tu_trich)
    for i in range(len(goc_boc) - n + 1):
        if goc_boc[i:i + n] == tu_trich:
            return bo_dau_cau(" ".join(tu_nhieu[i:i + n])).strip()
    return None


# ═══ nhieu_ca() — Làm nhiễu cả một ca như đầu ra của máy chép giọng nói ═══════════════
# Đáp án giữ nguyên, riêng câu trích được ánh xạ sang chữ đã nhiễu.
def nhieu_ca(ca: dict, rng, ti_le: float = 0.5) -> dict:
    """Một ca -> bản đã làm nhiễu. `dap_an` giữ nguyên, trừ `trich_dan` được ánh
    xạ sang chữ đã nhiễu để vẫn đối chiếu được với hội thoại."""
    dong_goc = ca["input"].split("\n")
    dong_nhieu = [nhieu_dong(d, rng, ti_le) if d.strip() else d for d in dong_goc]

    dap_an = []
    for m in ca["dap_an"]:
        m = dict(m)
        if m.get("trich_dan"):
            moi = []
            for t in m["trich_dan"]:
                d = next(
                    (x for g, n in zip(dong_goc, dong_nhieu)
                     if (x := nhieu_trich(t, g, n)) is not None),
                    t,
                )
                moi.append(d)
            m["trich_dan"] = moi
        dap_an.append(m)

    moi_ca = dict(ca)
    moi_ca["input"] = "\n".join(dong_nhieu)
    moi_ca["dap_an"] = dap_an
    return moi_ca
