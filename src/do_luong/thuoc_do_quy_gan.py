# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Thước đo]
Làm gì   : Đo mệnh đề có được gán đúng người không: ghép theo nội dung trước, rồi đếm cặp
           khớp luôn chủ thể, thứ ROUGE không thấy.
Vào → Ra : hai bệnh án (bản nháp, tham chiếu) → điểm quy gán: khớp nội dung và chủ thể, đổi
           người, thừa, sót
Đọc từ   : diem() tính bộ điểm một cặp; doi_chieu() ghép mệnh đề theo độ trùng từ
Mục lục (các hàm/lớp chính):
  diem()           Tính bộ điểm quy gán cho một cặp bản nháp và tham chiếu
  tach_menh_de()   Tách bệnh án thành mệnh đề có chủ thể
  doi_chieu()      Ghép mệnh đề dự đoán với tham chiếu theo độ trùng từ
  cung_noi_dung()  Kiểm tra hai mệnh đề nói cùng một nội dung
  class MenhDe     Một mệnh đề trích từ bệnh án: chủ thể, tập từ, câu
Dùng bởi : canh_bao/phat_hien, do_luong/cham_lai_bang_quy_gan, do_luong/chung_chi_thuoc_do,
           do_luong/do_tang_quy_gan, do_luong/duong_danh_doi, do_luong/khoang_tin_cay,
           bo_du_lieu/nap_bo_gpt500, bo_du_lieu/nap_bo_nguoi_that … (tổng 12 tệp)
Tên cũ   : thuoc_do_quy_gan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Điểm quy gán — thước đo NHÌN THẤY được lỗi đổi chủ thể.

LÝ DO TỒN TẠI.

Dự án phát biểu rằng ROUGE và Section F1 mù trước lỗi quy gán, và đã chứng
minh điều đó bằng số: hoán đổi "mẹ dị ứng penicillin" <-> "trẻ dị ứng
penicillin" cho Section F1 = 1,0000 ở 271/271 cặp, ROUGE-1 = 1,0000 khi hai
chủ thể xuất hiện cùng số lần.

Nhưng rồi Cửa 4 lại dùng chính bộ chấm đó để kết luận về nhánh C. Kết quả:
năm nhánh nằm trong khoảng 0,3514–0,3643 — chênh nhau 0,006, tức dưới mức
nhiễu. Kết luận "C không hơn B" được rút ra từ một cái thước mà chính dự án
đã chứng minh là không đo được đại lượng đang xét.

Đó là một lỗi thiết kế đánh giá, không phải một kết quả nghiên cứu.

CÁI NÀY ĐO GÌ. Đúng một đại lượng: **mệnh đề có được gán cho đúng người không**.

    mệnh đề  =  (chủ thể, tập từ nội dung)

Hai bản được đối chiếu theo NỘI DUNG trước; trong số các cặp đã khớp nội dung,
đếm xem bao nhiêu cặp khớp luôn CHỦ THỂ. Nhờ tách hai bước này mà phân biệt
được ba thứ mà ROUGE trộn làm một:

    khớp nội dung + khớp chủ thể  ->  đúng
    khớp nội dung + LỆCH chủ thể  ->  SAI QUY GÁN   (lỗi nguy hiểm)
    không khớp nội dung           ->  thừa / thiếu  (bịa / bỏ sót)

GIỚI HẠN, phải ghi vào báo cáo.

  1. Chủ thể đọc bằng LUẬT bề mặt (từ chỉ người trong câu, rồi đến tên mục).
     Nó không hiểu câu; "ba cháu" hay "con của chị gái" sẽ đọc sai. Đã đo trên
     tập thật trước khi dùng — xem `docs/ket-qua/`.
  2. Chỉ phân biệt hai mục `bệnh nhân` / `người nhà`. Hai người nhà khác nhau
     (mẹ và bà) bị gộp. Đó là lựa chọn có chủ định: bộ dữ liệu chỉ có 8,8% mẫu
     có lượt người nhà, tách nhỏ hơn nữa thì không còn có mẫu.
  3. Đối chiếu với BẢN THAM CHIẾU, nên kế thừa mọi thiếu sót của bản tham
     chiếu. Chấm với hội thoại là việc của phép chấm tay.

  4. NHẠY VỚI CÁCH ĐÓNG GÓI CÂU — giới hạn nặng nhất, phát hiện 07/09/2026 khi
     so nhánh A với nhánh B. Mệnh đề tách theo RANH GIỚI CÂU. Bản tham chiếu
     gói nhiều sự kiện vào một câu văn xuôi:

         "Bệnh nhân nam nhỏ tuổi, trong tuần qua có biểu hiện nghẹt mũi nhiều,
          ho tăng hơn bình thường, sốt 101 độ F vào ngày hôm qua."  -> 1 mệnh đề

     còn nhánh B xuất từng mảnh một:

         "nghẹt mũi nhiều (mấy hôm nay)."  "ho nhiều hơn bình thường."
         "sốt (hôm qua)."  "nhiệt độ 101 độ F."                     -> 4 mệnh đề

     Ghép tham lam nối MỘT mảnh với câu dài đó, ba mảnh còn lại thành "thừa".
     Tức một phần điểm trừ của nhánh B đến từ CÁCH ĐÓNG GÓI CÂU, không phải từ
     nội dung sai.

     Hai hệ quả, phải nói cả hai:

       - `f1_quy_gan` KHÔNG được dùng một mình để so một mô hình viết văn xuôi
         với một bộ sinh theo luật. Nó thiên vị bên nào giống bản tham chiếu về
         HÌNH THỨC — và mô hình fine-tune thì giống theo định nghĩa, vì nó học
         từ chính các bản ấy.
       - `dung_quy_gan` và `so_sai_chu_the` chịu ảnh hưởng ít hơn vì chỉ tính
         trên cặp ĐÃ KHỚP nội dung, nhưng không miễn nhiễm: cặp nào khớp được
         vẫn phụ thuộc cách đóng gói.

     CHƯA SỬA. Sửa đúng phải tách đến đơn vị nhỏ hơn câu (mệnh đề con), và đó là
     bài toán phân tích cú pháp tiếng Việt, không làm được bằng biểu thức chính
     quy. Ghi ở đây để không ai đọc bằng số mà quên mất.
"""
import re
import unicodedata
from dataclasses import dataclass
from typing import FrozenSet, List, Optional, Tuple

# Ngưỡng trùng từ để coi hai mệnh đề là "cùng nội dung".
NGUONG_NOI_DUNG = 0.6

# Từ chỉ BỆNH NHÂN và từ chỉ NGƯỜI NHÀ. Đọc trong câu, ưu tiên hơn tên mục.
TU_BENH_NHAN = ("trẻ", "bé", "cháu", "bệnh nhân", "con", "em bé", "trẻ nhỏ",
                "trẻ sơ sinh", "bn")

# CHỈ những từ chỉ người nhà KHÔNG thể hiểu theo nghĩa khác.
#
# Đã thử dùng danh sách đầy đủ và nó hỏng ngay ở câu đầu tiên:
#
#     "Ho và sốt ba ngày."     -> "ba" khớp từ chỉ BỐ      -> gán cho người nhà
#     "Bác sĩ khám thấy..."    -> "bác" khớp từ chỉ BÁC    -> gán cho người nhà
#     "Sưng má bên trái."      -> "má" khớp từ chỉ MẸ      -> gán cho người nhà
#     "Cô bé quấy khóc."       -> "cô" khớp từ chỉ CÔ      -> gán cho người nhà
#
# Dùng một họ lớp lỗi đã gặp ở Task 1 (nhãn "nhi" chỉ đúng 53% vì "hỏi trẻ em
# có hút", "aspirin trẻ em"). Nguyên tắc đã chốt của dự án: **chặn gộp nhầm
# quan trọng hơn chặn bỏ sót**. Một mệnh đề bị bỏ sót chỉ làm giảm độ bao phủ;
# một mệnh đề bị gán nhầm người làm hỏng đúng đại lượng đang đo.
#
# Cái giá phải trả được ghi lại bằng test: câu chỉ nói "Ba cháu bị tiểu đường"
# sẽ bị đọc thành chuyện của bệnh nhân. Xem `TU_NGUOI_NHA_KHONG_NHAN_DIEN`.
TU_NGUOI_NHA = ("mẹ", "bố", "cha", "người nhà", "gia đình", "bố mẹ", "cha mẹ",
                "phụ huynh", "anh trai", "chị gái", "em trai", "em gái",
                "ông nội", "bà nội", "ông ngoại", "bà ngoại", "mẹ ruột",
                "bố ruột", "mẹ đẻ", "bố đẻ")

# Không nhận diện, có chủ định. Mỗi từ ở đây đều có nghĩa thứ hai thường gặp
# trong bệnh án. Ghi ra đây để báo cáo nêu được giới hạn, không giấu.
TU_NGUOI_NHA_KHONG_NHAN_DIEN = ("ba", "má", "cô", "chú", "bác", "cậu", "dì",
                                "mợ", "thím", "ông", "bà", "anh", "chị", "em")

# Mục mặc định thuộc về người nhà khi câu không nêu rõ ai.
MUC_NGUOI_NHA = ("GIA ĐÌNH",)

# Từ đệm. CÓ Ý KHÔNG CHỨA từ phủ định.
#
# Mọi bảng từ đệm tiếng Việt sẵn có đều liệt "không" / "chưa" vào từ đệm. Nếu
# bỏ chúng ở đây thì "trẻ không dị ứng penicillin" và "trẻ dị ứng penicillin"
# thành cùng một mệnh đề — đúng cái lỗi chết người mà thước đo này sinh ra để
# chặn. Có một test riêng giữ điều này.
TU_DEM = frozenset("""
là và của với trong cho các những đã đang sẽ ở tại một này đó ạ rồi thì mà
nhưng vào ra lên xuống về từ đến do bởi được bị có khi nếu nên cũng còn rất
hơn nữa khoảng chừng trên dưới sau trước cùng theo qua vẫn lại mới
""".split())

TU_PHU_DINH = frozenset(["không", "chưa", "chẳng", "chả", "khỏi", "hết"])

# Chữ số viết bằng chữ -> chữ số. Để "ba ngày" và "3 ngày" là một mệnh đề.
SO_BANG_CHU = {"một": "1", "hai": "2", "ba": "3", "bốn": "4", "năm": "5",
               "sáu": "6", "bảy": "7", "tám": "8", "chín": "9", "mười": "10",
               "mốt": "1", "tư": "4", "rưỡi": "0.5"}

_TIEU_DE = re.compile(r"^[^a-zà-ỹ]{3,}$")
_KHONG_PHAI_CHU = re.compile(r"[^\w]+", re.UNICODE)


# ═══ class MenhDe — Một mệnh đề trích từ bệnh án: chủ thể, tập từ, câu ════════════════
# Bất biến; tập từ đã bỏ từ chỉ người và từ đệm, giữ từ phủ định và con số.
@dataclass(frozen=True)
class MenhDe:
    chu_the: str
    tu: FrozenSet[str]
    cau: str
    muc: str


# ------------------------------------------------------------------ tách

# ─── _la_tieu_de() — Nhận biết dòng tiêu đề mục viết hoa toàn bộ ──────────────────────
def _la_tieu_de(dong: str) -> bool:
    """Dòng toàn chữ hoa, không có dấu câu kết — là tên mục chứ không phải mệnh đề."""
    s = dong.strip()
    if not s or len(s) > 70:
        return False
    return s == s.upper() and not s.endswith(".")


# ─── _chuan() — Chuẩn hoá chuỗi về NFC và cắt khoảng trắng ────────────────────────────
def _chuan(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").strip()


# ─── _tu_noi_dung() — Lấy tập từ nội dung để đối chiếu hai mệnh đề ────────────────────
# Bỏ từ chỉ người và từ đệm; giữ từ phủ định và con số, đổi số bằng chữ thành số.
def _tu_noi_dung(cau: str) -> FrozenSet[str]:
    """Tập từ để đối chiếu nội dung.

    Bỏ từ chỉ người (chúng đã thành trường `chu_the`, giữ lại thì hai bản khác
    chủ thể sẽ tự động khác nội dung và phép đo sụp đổ). Bỏ từ đệm. GIỮ từ phủ
    định.
    """
    tho = [t for t in _KHONG_PHAI_CHU.split(_chuan(cau).lower()) if t]
    nguoi = set()
    for cum in TU_BENH_NHAN + TU_NGUOI_NHA:
        nguoi.update(cum.split())
    # GIỮ lại con số. "đau bụng 3 ngày" và "đau bụng 5 ngày" phải là hai mệnh
    # đề khác nhau — sai một con số trong bệnh án là lỗi thật, không phải biến
    # thể cách diễn đạt.
    return frozenset(SO_BANG_CHU.get(t, t) for t in tho if t in TU_PHU_DINH
                     or (t not in TU_DEM and t not in nguoi))


# ─── _con_so() — Lấy các từ chứa chữ số trong một tập từ ──────────────────────────────
def _con_so(tu: FrozenSet[str]) -> FrozenSet[str]:
    return frozenset(t for t in tu if any(c.isdigit() for c in t))


# ─── _chu_the_cua_cau() — Suy chủ thể của câu từ từ chỉ người hoặc tên mục ────────────
# Từ chỉ người trong câu ưu tiên hơn tên mục; không có thì mục gia đình là người nhà.
def _chu_the_cua_cau(cau: str, muc: str) -> str:
    """Từ trong câu thắng tên mục — 'Bé đi học' dưới mục GIA ĐÌNH vẫn là của bé."""
    thap = " " + _chuan(cau).lower() + " "

    def co(cum_list):
        return any(re.search(r"(?<![\w])" + re.escape(c) + r"(?![\w])", thap)
                   for c in cum_list)

    bn, nn = co(TU_BENH_NHAN), co(TU_NGUOI_NHA)
    if bn and not nn:
        return "bệnh nhân"
    if nn and not bn:
        return "người nhà"
    if bn and nn:
        # Cả hai cùng xuất hiện: lấy từ đúng ĐẦU câu làm chủ ngữ.
        vi_bn = min((thap.find(" " + c + " ") for c in TU_BENH_NHAN
                     if " " + c + " " in thap), default=10**6)
        vi_nn = min((thap.find(" " + c + " ") for c in TU_NGUOI_NHA
                     if " " + c + " " in thap), default=10**6)
        return "bệnh nhân" if vi_bn <= vi_nn else "người nhà"
    return "người nhà" if any(k in muc.upper() for k in MUC_NGUOI_NHA) else "bệnh nhân"


# ═══ tach_menh_de() — Tách bệnh án thành mệnh đề có chủ thể ═══════════════════════════
# Thuần tuý luật, không gọi mô hình; tiêu đề viết hoa đặt mục cho các câu sau.
def tach_menh_de(ban: str) -> List[MenhDe]:
    """Bệnh án -> danh sách mệnh đề có chủ thể. Thuần tuý, không gọi mô hình."""
    ra: List[MenhDe] = []
    muc = ""
    for dong in _chuan(ban).split("\n"):
        dong = dong.strip()
        if not dong:
            continue
        if _la_tieu_de(dong):
            muc = dong
            continue
        for cau in re.split(r"(?<=[.;!?])\s+", dong):
            cau = cau.strip(" -•\t")
            if not cau:
                continue
            tu = _tu_noi_dung(cau)
            if not tu:
                continue
            ra.append(MenhDe(chu_the=_chu_the_cua_cau(cau, muc),
                             tu=tu, cau=cau, muc=muc))
    return ra


# ------------------------------------------------------------- đối chiếu

# ─── _giao() — Tính độ giao hai tập từ trên tập nhỏ hơn ───────────────────────────────
def _giao(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


# ═══ cung_noi_dung() — Kiểm tra hai mệnh đề nói cùng một nội dung ═════════════════════
# Chưa xét chủ thể. Lệch phủ định hoặc lệch con số thì không bao giờ cùng nội dung.
def cung_noi_dung(x: MenhDe, y: MenhDe) -> bool:
    """Hai mệnh đề nói cùng một thứ không — CHƯA xét chủ thể.

    Phủ định lệch nhau thì không bao giờ là cùng nội dung, dù từ còn lại trùng
    hết. Kiểm riêng vì phép đo trùng từ đơn thuần sẽ cho "không dị ứng" và
    "dị ứng" tỷ lệ 2/3 và lọt qua ngưỡng.
    """
    if (x.tu & TU_PHU_DINH) != (y.tu & TU_PHU_DINH):
        return False
    # Lệch con số cũng không bao giờ là cùng mệnh đề. "đau bụng 3 ngày" và
    # "đau bụng 5 ngày" trùng 3/4 từ — đặt ngưỡng nào thì cũng lọt. Con số
    # sai trong bệnh án là lỗi thật chứ không phải cách diễn đạt khác.
    if _con_so(x.tu) != _con_so(y.tu):
        return False
    return _giao(x.tu, y.tu) >= NGUONG_NOI_DUNG


# ═══ doi_chieu() — Ghép mệnh đề dự đoán với tham chiếu theo độ trùng từ ═══════════════
# Ghép tham lam; trả cặp trùng, cặp sai chủ thể, mệnh đề thừa và mệnh đề thiếu.
def doi_chieu(du_doan: List[MenhDe], tham_chieu: List[MenhDe]):
    """Ghép tham lam theo độ trùng từ giảm dần.

    Trả về (trung, sai_chu_the, thua, thieu) — `trung` và `sai_chu_the` là các
    cặp đã khớp nội dung.
    """
    cap = []
    for i, p in enumerate(du_doan):
        for j, t in enumerate(tham_chieu):
            if cung_noi_dung(p, t):
                cap.append((_giao(p.tu, t.tu), i, j))
    cap.sort(key=lambda c: (-c[0], c[1], c[2]))

    da_p, da_t = set(), set()
    trung, sai = [], []
    for _, i, j in cap:
        if i in da_p or j in da_t:
            continue
        da_p.add(i)
        da_t.add(j)
        (trung if du_doan[i].chu_the == tham_chieu[j].chu_the else sai).append((i, j))

    thua = [i for i in range(len(du_doan)) if i not in da_p]
    thieu = [j for j in range(len(tham_chieu)) if j not in da_t]
    return trung, sai, thua, thieu


# ------------------------------------------------------------------ điểm

# ═══ diem() — Tính bộ điểm quy gán cho một cặp bản nháp và tham chiếu ═════════════════
# Điểm chính f1_quy_gan phạt cả gán sai người lẫn viết thiếu; có thêm bỏ sót, thêm mới,
# số sai chủ thể.
def diem(du_doan: str, tham_chieu: str) -> dict:
    """Bộ chỉ số quy gán của một cặp (bản sinh, bản tham chiếu).

    `f1_quy_gan` là chỉ số chính: F1 trên cặp (chủ thể, nội dung). Nó phạt CẢ
    HAI chiều — ghi sai người bị trừ, mà viết ít đi cho an toàn cũng bị trừ.
    """
    p = tach_menh_de(du_doan)
    t = tach_menh_de(tham_chieu)
    trung, sai, thua, thieu = doi_chieu(p, t)

    dung = len(trung)
    do_chinh_xac = dung / len(p) if p else 0.0
    do_bao_phu = dung / len(t) if t else 0.0
    f1 = (2 * do_chinh_xac * do_bao_phu / (do_chinh_xac + do_bao_phu)
          if (do_chinh_xac + do_bao_phu) else 0.0)
    khop_noi_dung = dung + len(sai)

    return {
        "f1_quy_gan": round(f1, 4),
        "do_chinh_xac": round(do_chinh_xac, 4),
        "do_bao_phu": round(do_bao_phu, 4),
        # Trong số mệnh đề đã nói ĐÚNG NỘI DUNG, bao nhiêu phần gán ĐÚNG NGƯỜI.
        # Tách riêng vì nó không bị ảnh hưởng bởi bỏ sót — hai lỗi khác nhau.
        "dung_quy_gan": round(dung / khop_noi_dung, 4) if khop_noi_dung else 0.0,
        "bo_sot": round(len(thieu) / len(t), 4) if t else 0.0,
        "them_moi": round(len(thua) / len(p), 4) if p else 0.0,
        "so_sai_chu_the": len(sai),
        "so_thieu": len(thieu),
        "so_thua": len(thua),
        "so_menh_de_du_doan": len(p),
        "so_menh_de_tham_chieu": len(t),
    }
