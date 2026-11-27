# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ sinh]
Làm gì   : Đổi từ chuẩn sang phương ngữ miền Trung, Nam trong lời thoại và quy ngược về từ
           chuẩn bằng từ điển.
Vào → Ra : câu + vùng + rng + tỷ lệ → câu đã đổi phương ngữ; nội dung → nội dung quy về từ
           chuẩn
Đọc từ   : doi_sang_phuong_ngu() đổi câu theo vùng; ve_tu_chuan() quy ngược về từ chuẩn;
           nap() đọc từ điển
Mục lục (các hàm/lớp chính):
  nap()                  Nạp từ điển phương ngữ thành danh sách theo vùng
  doi_sang_phuong_ngu()  Đổi một số từ chuẩn trong câu sang phương ngữ của vùng
  giu_loi_nguoi_noi()    Đổi nội dung mệnh đề về đúng lời người nói
  ve_tu_chuan()          Đổi cụm phương ngữ về từ chuẩn để so hai bản của cặp
  bang_quy_chuan()       Lập bảng từ phương ngữ về nghĩa chuẩn
Gọi tới  : he_thong/duong_dan
Dùng bởi : bo_du_lieu/sinh_bo_thach_thuc, bo_du_lieu/sinh_hoi_thoai_viet
Tên cũ   : phuong_ngu.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Từ điển phương ngữ miền Trung / miền Nam, và phép thay từ trong lời thoại.

VÌ SAO CẦN (10/09/2026).

Bộ sinh của dự án trước đó CÓ ba vùng (`bac`, `nam`, `trung`) nhưng khác nhau
chỉ ở TIỂU TỪ: "a", "nghen", "hi", "nha". Từ vựng thì giống hệt nhau — mỗi
vùng đều nói "sốt", "ho", "mệt".

Người thật không nói vậy. Ở miền Nam một người mẹ sẽ nói "cháu nóng hâm hấp"
chứ ít khi nói "cháu sốt"; ở miền Trung sẽ là "hôm tê" chứ không phải "hôm kia".

Đây là một dạng của LỖI QUY GÁN mà dự án đi dò, chỉ là ở tầng từ vựng: hệ
thống phải hiểu "nóng hâm hấp" và "sốt" là MỘT THỨ. Nếu không thì:

  - bước trích ghi "nóng hâm hấp" nguyên văn    -> bệnh án không chuẩn hoá
  - bước lọc cặp ứng viên không ghép được       -> mất quan hệ
  - phép chấm theo chuỗi không khớp             -> báo lỗi oan

NGUYÊN TẮC THAY TỪ. Chỉ thay trong lời của BỆNH NHÂN và NGƯỜI NHÀ, không thay
trong lời BÁC SĨ: bác sĩ được đào tạo nói chuẩn, và trộn lại thì mất một dấu
hiệu thật trong hội thoại khám bệnh.

ĐÁP ÁN GIỮ NGHĨA CHUẨN. Hội thoại viết "lừ đừ", đáp án vẫn ghi "mệt".
Đó chính là phép thử: mô hình có quy được về khái niệm chuẩn không.

TRỪ cụm KHÔNG đồng nghĩa với từ chuẩn (`GIU_NGUYEN`, sửa 24/09/2026): "nóng
hâm hấp" chưa phải "sốt" khi chưa đo nhiệt độ, nên đáp án ghi đúng lời người nói.
Ví dụ cũ ở dòng trên từng là "nóng hâm hấp -> sốt" — chính ví dụ đó sai.

NGUỒN. Từ điển 30 từ do người dùng cung cấp (`data/ngoai/tu_dien_phuong_ngu.csv`),
mà người dùng xác nhận ngày 11/09/2026 là do GPT SINH. Từ ngày đó bảng thay KHÔNG
áp vào khuôn train (`sinh_hoi_thoai_viet.PHUONG_NGU_TRONG_TRAIN`), chỉ ở tập đánh
giá. Mỗi mục phải đối chiếu từ điển thật (Huỳnh Công Tín 2007) hoặc người địa
phương trước khi dùng cho kết luận. Xem `docs/nguon-du-lieu.md`.
"""
import csv
import re
from pathlib import Path

from src.he_thong import duong_dan as duong_dan

TEP_TU_DIEN = duong_dan.THU_MUC_DU_LIEU / "ngoai" / "tu_dien_phuong_ngu.csv"

# Vùng trong từ điển -> khoá vùng của bộ sinh.
VUNG = {"miền Trung": "trung", "miền Nam": "nam"}


# ═══ nap() — Nạp từ điển phương ngữ thành danh sách theo vùng ═════════════════════════
# Không có tệp thì trả rỗng, không báo lỗi; bộ sinh vẫn chạy được.
def nap(tep=None):
    """-> {khoa_vung: [(tu_phuong_ngu, nghia_chuan), ...]}.

    Trả về rỗng khi không có tệp, KHÔNG ném lỗi: bộ sinh phải chạy được cả khi
    chưa có từ điển, và phải báo ra chứ không im lặng thay bằng từ chuẩn.
    """
    tep = Path(tep or TEP_TU_DIEN)
    ra = {v: [] for v in VUNG.values()}
    if not tep.exists():
        return ra
    with open(tep, encoding="utf-8", newline="") as f:
        for hang in csv.DictReader(f):
            vung = VUNG.get((hang.get("vùng") or "").strip())
            tu = (hang.get("từ/cụm từ") or "").strip()
            nghia = (hang.get("nghĩa chuẩn") or "").strip()
            if vung and tu and nghia:
                ra[vung].append((tu, nghia))
    return ra


# Chỉ những cặp có thể thay THẲNG trong câu mà không phá ngữ pháp. Nhiều mục
# trong từ điển là đại từ hoặc từ để hỏi ("răng", "mô", "tê") — thay bừa vào
# một câu bất kỳ sẽ ra câu sai, nên phải liệt kê tay chứ không quét cả từ điển.
#
# Chiều thay là CHUẨN -> PHƯƠNG NGỮ: bộ sinh viết câu bằng từ chuẩn trước, rồi
# đổi sang phương ngữ để đưa vào hội thoại. Đáp án giữ bản chuẩn.
THAY_DUOC = {
    "trung": [
        ("hôm kia", "hôm tê"),
        ("dạo này", "bữa chừ"),
        ("bây giờ", "chừ"),
        ("trẻ em", "con nít"),
    ],
    "nam": [
        ("hôm trước", "bữa hổm"),
        ("dạo gần đây", "hổm rày"),
        ("ngất", "xỉu"),
        ("sốt", "nóng hầm hập"),
        ("mệt", "lừ đừ"),
        ("đại tiện", "đi cầu"),
    ],
}

THAY_DUOC_MO_RONG = {
    "trung": [
        ("hôm qua", "bữa qua"),
        ("đau đầu", "nhức trốc"),
        ("bà ngoại", "mệ ngoại"),
        ("bà nội", "mệ nội"),
        ("sốt", "hầm hầm"),
    ],
    "nam": [
        ("nôn", "ói mửa"),
        ("tiêu chảy", "đi tháo"),
        ("sưng chân", "phù giò"),
        ("cộm mắt", "xốn mắt"),
        ("đau vùng lưng dưới", "đau ngang hông"),
        ("nhanh", "mau lẹ"),
    ],
}

# Từ DÙNG SAU chặn phép thay. Không có bảng này thì bộ sinh viết ra tiếng Việt
# sai, và đó là lỗi tệ hơn không có phương ngữ: dữ liệu hỏng mà nhìn bằng số
# không thấy.
#
# Đã hỏng thật, test bắt được:
#     "mệt mỏi"  ->  "lừ đừ mỏi"    (không phải tiếng Việt)
#     "sốt cao"  ->  "nóng hầm hập cao"
#
# Nguyên nhân: ranh giới TỪ không phải ranh giới TỪ GHÉP. "mệt" trong "mệt
# mỏi" đúng là một từ tách bằng dấu cách, nhưng thay riêng nó thì vô nghĩa.
CHAN_SAU = {
    "sốt": {"cao", "nhẹ", "siêu", "xuất", "phát", "rét", "ruột", "li"},
    "mệt": {"mỏi"},
    "ngất": {"xỉu"},
}

CHAN_SAU_MO_RONG = {
    "sốt": set(CHAN_SAU["sốt"]),
    "nôn": {"nao", "mửa", "trớ", "thốc", "hết"},
    "đau đầu": {"dữ", "âm"},
    "nhanh": {"nhẹn", "chóng"},
}

# Hai từ bị BỎ HẲN khỏi bảng thay, dù có trong từ điển:
#
#   "không" -> "nỏ"   "nỏ" la phu dinh TRAN THUAT. Cau hoi "co sot khong?"
#                     đổi thành "có sốt nỏ?" là sai. Tách hai trường hợp đó
#                     cần phân tích cú pháp, chưa làm.
#   "làm"   -> "mần"  xuat hien trong "lam xet nghiem", "lam sao" voi nghia
#                     rất khác nhau; thay đồng loạt ra câu không tự nhiên.
#
# Ghi ra đây chứ không xoá im lặng, để người đọc sau biết là đã cân nhắc.
DA_BO = {"không": "nỏ", "làm": "mần"}

# Cụm phương ngữ KHÔNG đồng nghĩa với từ chuẩn: đáp án GIỮ NGUYÊN lời người nói.
#
# SỬA 24/09/2026. Cặp ("sốt", "nóng hâm hấp") ở THAY_DUOC từ 10/09, theo quy ước
# "đáp án giữ nghĩa chuẩn" ở đầu tệp: hội thoại viết "nóng hâm hấp", đáp án ghi
# "sốt, chắc chắn". Nhưng bảng chuẩn hoá của chính dự án (`chuan_hoa`, từ 11/09)
# ghi cụm này là CẦN HỎI: "người nói chưa đo nhiệt độ — không tự đổi thành sốt".
# Hai chỗ của cùng một dự án nói hai điều, và phép chấm đứng về phía sai: đầu ra
# chép nguyên văn "nóng hâm hấp" bị tính là không căn cứ + bỏ sót, còn đầu ra đổi
# thẳng thành "sốt, chắc chắn" — đúng điều bảng chuẩn hoá cấm — được tính là đúng.
#
# Từ nay mệnh đề nào mà KHÔNG trích dẫn nào còn từ chuẩn, chỉ còn cụm ở đây, thì
# nội dung ghi đúng cụm người nói dùng. Độ chắc chắn GIỮ NGUYÊN: người nói không
# ra dấu nghi ngờ, cái chưa chắc là phép đổi từ chứ không phải lời kể. Các cặp
# còn lại của THAY_DUOC đều là CHẮC trong `chuan_hoa`, vẫn giữ nghĩa chuẩn. Test
# `test_giu_nguyen_khop_chuan_hoa` bắt khi hai bảng lệch nhau.
GIU_NGUYEN = {"nóng hầm hập"}
GIU_NGUYEN_MO_RONG = {"nóng hầm hập", "hầm hầm"}


# ─── _mau() — Tạo mẫu tìm nguyên cụm, không phân biệt hoa thường ──────────────────────
# Không khớp khi cụm dính chữ khác ở hai đầu.
def _mau(cum):
    return re.compile(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])", re.I)


# ═══ giu_loi_nguoi_noi() — Đổi nội dung mệnh đề về đúng lời người nói ═════════════════
# Chỉ đổi khi từ chuẩn không còn trong câu trích mà câu trích có cụm phương ngữ.
def giu_loi_nguoi_noi(noi_dung, trich_dan):
    """-> nội dung mới của mệnh đề (hoặc chính `noi_dung`). Xem GIU_NGUYEN.

    Chỉ đổi khi cả ba điều cùng đúng:
      1. nội dung có từ chuẩn (cả từ, không phân biệt hoa thường);
      2. KHÔNG trích dẫn nào còn từ chuẩn đó — bác sĩ hỏi "có sốt không", hay
         "sốt cao" bị CHAN_SAU giữ lại, thì "sốt" có căn cứ nguyên văn;
      3. ít nhất một trích dẫn mang cụm phương ngữ.
    """
    for cac in THAY_DUOC.values():
        for chuan, dia_phuong in cac:
            if dia_phuong not in GIU_NGUYEN:
                continue
            m_chuan = _mau(chuan)
            if (not m_chuan.search(noi_dung)
                    or any(m_chuan.search(t) for t in trich_dan)
                    or not any(_mau(dia_phuong).search(t) for t in trich_dan)):
                continue
            noi_dung = m_chuan.sub(
                lambda m: (dia_phuong[:1].upper() + dia_phuong[1:]
                           if m.group(0)[:1].isupper() else dia_phuong),
                noi_dung)
    return noi_dung


# ═══ ve_tu_chuan() — Đổi cụm phương ngữ về từ chuẩn để so hai bản của cặp ═════════════
# Chỉ dùng để so hai bản của một cặp thử thách.
def ve_tu_chuan(noi_dung):
    """Ngược của `giu_loi_nguoi_noi`, CHỈ để so hai bản của một cặp thử thách
    (`thach_thuc`): bản có phương ngữ ghi "nóng hâm hấp", bản không có ghi "sốt",
    hai bản có ý khác nhau đúng ở chỗ đó."""
    for cac in THAY_DUOC.values():
        for chuan, dia_phuong in cac:
            if dia_phuong in GIU_NGUYEN:
                noi_dung = _mau(dia_phuong).sub(chuan, noi_dung)
    return noi_dung


# ═══ doi_sang_phuong_ngu() — Đổi một số từ chuẩn trong câu sang phương ngữ của vùng ═══
# Mỗi cặp đổi với xác suất 0,6; trả câu mới và các cặp đã đổi.
def doi_sang_phuong_ngu(cau, vung, rng, ty_le=0.6, mo_rong=False):
    """Đổi một số từ chuẩn trong `cau` sang dạng phương ngữ của `vung`.

    -> (cau_moi, [các cặp đã đổi]). Trả về cả danh sách đã đổi để bộ sinh ghi
    lại được — không ghi lại thì không biết ca nào có phương ngữ, và không đo
    được riêng nhóm đó.

    `ty_le`: xác suất đổi MỖI cặp tìm thấy. Không đổi hết 100%: hội thoại thật
    trộn cả hai cách nói, và nếu đổi hết thì phép thử thành "dịch từ điển" chứ
    không còn là "hiểu câu có lẫn phương ngữ".
    """
    da_doi = []
    cap_list = list(THAY_DUOC.get(vung, []))
    chan = dict(CHAN_SAU)
    if mo_rong:
        cap_list += list(THAY_DUOC_MO_RONG.get(vung, []))
        for k, v in CHAN_SAU_MO_RONG.items():
            chan[k] = set(chan.get(k, ())) | set(v)
    for chuan, dia_phuong in cap_list:
        # Không phân biệt hoa thường: "Hôm kia" đầu câu và "hôm kia" giữa câu
        # là một từ. Ban đầu khớp phân biệt hoa thường, và hậu quả là mọi từ
        # đứng ở ĐẦU CÂU đều không bao giờ được đổi — đúng những chỗ dễ nhìn
        # nhất, nên lỗi đó rất dễ lọt.
        mau = re.compile(rf"(?<![\wÀ-ỹ]){re.escape(chuan)}(?![\wÀ-ỹ])", re.I)
        m = mau.search(cau)
        if not m:
            continue
        # Ranh giới TỪ không phải ranh giới TỪ GHÉP — xem CHAN_SAU.
        sau = cau[m.end():].lstrip()
        tu_sau = re.split(r"[^\wÀ-ỹ]", sau, maxsplit=1)[0].lower()
        if tu_sau in chan.get(chuan, ()):
            continue
        if rng.random() > ty_le:
            continue
        # Giữ chữ hoa đầu từ nếu bản gốc viết hoa.
        thay = dia_phuong
        if m.group(0)[:1].isupper():
            thay = dia_phuong[:1].upper() + dia_phuong[1:]
        cau = cau[:m.start()] + thay + cau[m.end():]
        da_doi.append((chuan, dia_phuong))
    return cau, da_doi


# ═══ bang_quy_chuan() — Lập bảng từ phương ngữ về nghĩa chuẩn ═════════════════════════
# Hiện không nơi nào trong mã gọi hàm này nữa.
def bang_quy_chuan(tu_dien=None):
    """-> {từ phương ngữ (thường): nghĩa chuẩn}. Dùng cho phép chấm và cho
    bước lọc cặp ứng viên, để "nóng hâm hấp" ghép được với "sốt".

    GHI CHÚ 24/09/2026: không nơi nào trong `src` gọi hàm này nữa. Phép chấm và
    đường ống dùng `chuan_hoa`, nơi đó "nóng hâm hấp" là CẦN HỎI (`GIU_NGUYEN`)."""
    tu_dien = tu_dien if tu_dien is not None else nap()
    ra = {}
    for cap in THAY_DUOC.values():
        for chuan, dia_phuong in cap:
            ra[dia_phuong.lower()] = chuan
    for cac in tu_dien.values():
        for tu, nghia in cac:
            ra.setdefault(tu.lower(), nghia)
    return ra
