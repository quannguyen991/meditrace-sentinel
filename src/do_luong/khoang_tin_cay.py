# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Thống kê]
Làm gì   : Tính khoảng tin cậy bootstrap theo ca và theo khuôn bệnh, và so cặp các nhánh, để
           biết chênh lệch có vượt nhiễu không.
Vào → Ra : đầu ra các nhánh (--nhanh, --tep) + tập (--tap) → bảng điểm kèm khoảng tin cậy và
           hiệu cặp với nhánh gốc
Đọc từ   : khoang() bootstrap một chỉ số; so_sanh() so cặp hai nhánh; main() dựng bảng
Mục lục (các hàm/lớp chính):
  diem_tung_ca()   Lấy điểm từng ca của một nhánh theo thước đo
  doi_chieu_tap()  Đối chiếu kết quả với bộ dữ liệu, dừng nếu lệch
  khoang()         Tính khoảng tin cậy bootstrap cho một chỉ số
  so_sanh()        So sánh theo cặp hai nhánh bằng bootstrap
  do_cong_suat()   Đo công suất phép đo qua tỉ lệ mệnh đề tầng 4
  bang()           Dựng bảng khoảng tin cậy và so sánh cặp với nhánh gốc
  main()           Chạy dòng lệnh dựng bảng khoảng tin cậy các nhánh
Gọi tới  : do_luong/cham_diem, do_luong/thuoc_do_quy_gan, bo_du_lieu/nap_du_lieu,
           bo_du_lieu/van_tay_bo, duong_ong/b1_cau_truc_menh_de
Dùng bởi : do_luong/cham_he_thong, do_luong/danh_gia_khoa, do_luong/do_tang_quy_gan,
           bo_du_lieu/nap_bo_gpt500, bo_du_lieu/nap_bo_nguoi_that
Tên cũ   : sai_so.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Khoảng tin cậy và so sánh theo cặp cho bảng đối chiếu các nhánh.

VÌ SAO CẦN. Mỗi con số trong bảng so sánh hiện tại là MỘT điểm, chạy một lần.
Không có chỗ nào trong `src/` tính sai số. Với n = 60 ca, sai số chuẩn của một
tỷ lệ quanh 0,5 là khoảng 6,5 điểm phần trăm, nên khoảng tin cậy 95% rộng cỡ
±13 điểm — mọi câu "nhánh X hơn nhánh Y vài điểm" đều không đọc được.

BA CHỖ DỄ LÀM SAI, tệp này chặn cả ba.

1. ĐƠN VỊ ĐỘC LẬP LÀ KHUÔN BỆNH, KHÔNG PHẢI CA.

   `tach_tap_viet` đã ghi rõ: hai ca cùng khuôn dùng chung dẫn ý, chung khổ
   triệu chứng, chung mạch hội thoại — "chúng gần như là một bài". Lấy lại mẫu
   theo CA thì 60 ca được đếm là 60 đơn vị độc lập, trong khi thực tế chỉ có
   vài cụm. Khoảng tin cậy ra hẹp giả.

   Nên báo CẢ HAI:

       theo ca     lấy lại mẫu từng ca        -> khoảng lạc quan
       theo khuôn  lấy lại mẫu từng khuôn     -> khoảng thật (bootstrap cụm)

2. SO HAI KHOẢNG TIN CẬY CHỒNG NHAU RỒI KẾT LUẬN "không khác biệt" LÀ SAI.

   Các nhánh chạy trên CÙNG bộ ca, nên phải lấy khoảng tin cậy của HIỆU theo
   cặp. Hiệu theo cặp hẹp hơn nhiều so với hai khoảng rời, vì nó triệt tiêu
   phần "ca này dễ, ca kia khó".

3. TÊN TỆP KẾT QUẢ KHÔNG NÓI ĐƯỢC NÓ CHẠY TRÊN BỘ NÀO.

   Lỗi thật, tìm ra đúng lúc viết tệp này: `data/ra_C_viet_phat_trien.jsonl`
   có tên nói là `viet_phat_trien`, nhưng id trong nó khớp
   `viet3k_phat_trien.jsonl` đúng 60/60, và khớp `viet_phat_trien.jsonl`
   hiện tại chỉ 6/60. Nói cách khác đây là kết quả của BỘ 3.000, mang tên của
   bộ 5.000.

   Ghép nó với bộ dữ liệu hiện tại thì mất 54/60 ca mà không có ngoại lệ nào.
   Đây là họ lỗi B12 lần thứ bảy: MỘT TÊN TỆP, HAI BỘ DỮ LIỆU.

   Nên `doi_chieu_tap` đo khớp id trước khi tính bất kỳ con số nào, và khi
   không khớp 100% thì DỪNG HẲN, kèm tên tệp thật sự khớp.

GIỚI HẠN, phải ghi vào báo cáo. Tập phat_trien có 8 khuôn. Bootstrap cụm trên
8 cụm là xấp xỉ thô: nó nói được "khoảng này rộng", không nói được "p = 0,03".
Dùng nó để bác bỏ những chênh lệch nhỏ, không dùng nó để khẳng định chênh lệch
nhỏ.

    python -m src.do_luong.khoang_tin_cay --tap viet_phat_trien --nhanh B C D
"""
import argparse
import io
import json
import random
import sys
from pathlib import Path

from src.do_luong import cham_diem as cham_diem
from src.do_luong import thuoc_do_quy_gan as thuoc_do_quy_gan

# Hai HỌ thước đo, và chúng không thay nhau được.
#
#   cham_diem   ROUGE + SectionF1. Dự án này đã chứng minh nó NGƯỢC DẤU với
#               lỗi đổi chủ thể, nên nó là chỉ số tham chiếu.
#   quy_gan     F1 trên cặp (chủ thể, nội dung). Đây mới là thước đo chính.
#
# Một bảng chỉ có `final` thì không trả lời được câu hỏi của dự án.
HO_THUOC_DO = {
    "cham_diem": ("final", "rouge_avg", "section_f1",
                  "rouge1", "rouge2", "rougel"),
    "quy_gan": ("f1_quy_gan", "do_chinh_xac", "do_bao_phu"),
}


# ─── _ho_cua() — Tra thước đo thuộc họ cham_diem hay quy_gan ──────────────────────────
# Báo lỗi nếu khoá thước đo lạ.
def _ho_cua(khoa):
    for ho, cac in HO_THUOC_DO.items():
        if khoa in cac:
            return ho
    raise SystemExit(f"khong biet thuoc do {khoa!r}; "
                     f"co: {sorted(k for v in HO_THUOC_DO.values() for k in v)}")

THU_MUC_DATA = Path("data")

# Bao nhiêu khuôn thì một phép so sánh còn đọc được. Dưới mức này thì con số
# không sai, nhưng nó không nói gì về bộ khuôn đầy đủ.
KHUON_TOI_THIEU = 6

SO_LAN_MAC_DINH = 10000
HAT_MAC_DINH = 42


# --------------------------------------------------------------- nạp dữ liệu

# ─── _doc() — Đọc tệp jsonl thành danh sách bản ghi ───────────────────────────────────
def _doc(duong_dan):
    return [json.loads(d) for d in
            open(duong_dan, encoding="utf-8") if d.strip()]


# ═══ diem_tung_ca() — Lấy điểm từng ca của một nhánh theo thước đo ════════════════════
# Trả điểm theo id và bản ghi gốc, giữ từng ca để còn lấy lại mẫu bootstrap.
def diem_tung_ca(duong_dan, khoa="final", dung_muc_phu=True):
    """-> ({id: diem}, {id: ban_ghi}) cho MỘT tệp kết quả nhánh.

    Giữ điểm từng ca thay vì trả về trung bình: `do_dac.do_mot_nhanh` trung
    bình ngay rồi bỏ danh sách, nên không còn gì để lấy lại mẫu.

    Trả về cả bản ghi gốc vì hàng rào `doi_chieu_tap` phải so NỘI DUNG, không
    so id.
    """
    diem, ban_ghi = {}, {}
    for k in _doc(duong_dan):
        tham_chieu = k.get("tham_chieu") or ""
        if not tham_chieu:
            continue
        truong = "du_doan" if dung_muc_phu else "du_doan_khong_muc_phu"
        du_doan = k.get(truong, k.get("du_doan", ""))
        if _ho_cua(khoa) == "quy_gan":
            d = thuoc_do_quy_gan.diem(du_doan, tham_chieu)
        else:
            d = cham_diem.diem_cuoi(du_doan, tham_chieu)
        diem[k["id"]] = d[khoa]
        ban_ghi[k["id"]] = k
    return diem, ban_ghi


# ─── _khoa_noi_dung() — Lấy dấu vết nội dung hội thoại của một ca ─────────────────────
def _khoa_noi_dung(ban_ghi):
    """Dấu vết NỘI DUNG của một ca: chính văn bản hội thoại, đã chuẩn khoảng."""
    return " ".join(str(ban_ghi.get("input") or "").split())


# ═══ tim_tap_khop() — Tìm tệp dữ liệu khớp nội dung với kết quả ═══════════════════════
# Xếp theo số ca khớp nội dung; id trùng chưa đủ vì các thế hệ bộ dùng lại id.
def tim_tap_khop(theo_id, thu_muc=None):
    """-> [(ten_tep, khop_noi_dung, khop_id, tong)] sắp theo khớp nội dung.

    `theo_id`: {id: ban_ghi_ket_qua} — cần cả bản ghi, không chỉ id, vì phải
    so NỘI DUNG.

    ĐỐI ID KHÔNG ĐỦ ĐỂ NHẬN DẠNG BỘ DỮ LIỆU. Bộ sinh dùng lại không gian id:
    `hv_0019` là "sốt siêu vi" trong bộ 3.000 và "thiếu máu do giun" trong bộ
    5.000. Nên:

        đối theo id      bộ 3.000 khớp 60/60  VÀ  bộ 5.000 khớp 60/60
        đối theo nội dung bộ 3.000 khớp 60/60  VÀ  bộ 5.000 khớp  0/60

    Ghép theo id với bộ sai cho ra một phép ghép THÀNH CÔNG 100% với toàn bộ
    nhãn sai. Không ngoại lệ, không thiếu dòng, không dấu hiệu gì trên bảng
    số. Đây là họ lỗi B12 ở dạng nguy hiểm nhất.
    """
    thu_muc = Path(thu_muc or THU_MUC_DATA)
    ra = []
    for tep in sorted(thu_muc.glob("*.jsonl")):
        if tep.name.startswith(("ra_", "trich_")):
            continue
        try:
            goc = {b.get("id"): b for b in _doc(tep)}
        except Exception:                                      # noqa: BLE001
            continue
        khop_id = sum(1 for i in theo_id if i in goc)
        khop_nd = sum(1 for i, b in theo_id.items()
                      if i in goc and _khoa_noi_dung(goc[i]) == _khoa_noi_dung(b))
        if khop_id:
            ra.append((tep.name, khop_nd, khop_id, len(theo_id)))
    ra.sort(key=lambda x: (-x[1], -x[2]))
    return ra


# ═══ doi_chieu_tap() — Đối chiếu kết quả với bộ dữ liệu, dừng nếu lệch ════════════════
# Dừng hẳn nếu nội dung không khớp 100%; nếu khớp thì trả bệnh (khuôn) của từng ca.
def doi_chieu_tap(theo_id, duong_dan_tap):
    """-> {id: khuon}. DỪNG HẲN nếu bộ dữ liệu không khớp NỘI DUNG 100%.

    Lý do dừng hẳn chứ không cảnh báo: ghép sai ở đây không báo lỗi ở bước
    sau. Ghép thiếu thì làm n tụt âm thầm; ghép lẫn thế hệ thì giữ nguyên n
    và đổi hết nhãn khuôn. Cả hai đều ra một bảng số đọc được bình thường.
    """
    goc = {b["id"]: b for b in _doc(duong_dan_tap)}
    thieu = [i for i in theo_id if i not in goc]
    lech = [i for i, b in theo_id.items()
            if i in goc and _khoa_noi_dung(goc[i]) != _khoa_noi_dung(b)]
    if thieu or lech:
        dong = [f"  {t:<40} noi dung {nd:>3}/{tong}   id {ki:>3}/{tong}"
                for t, nd, ki, tong in tim_tap_khop(theo_id)[:5]]
        raise SystemExit(
            f"Ket qua va bo du lieu KHONG cung mot the he.\n"
            f"  bo du lieu dua vao : {duong_dan_tap}\n"
            f"  thieu id           : {len(thieu)}/{len(theo_id)}"
            + (f" (vi du {', '.join(thieu[:4])})" if thieu else "") + "\n"
            f"  co id nhung LECH noi dung: {len(lech)}/{len(theo_id)}"
            + (f" (vi du {', '.join(lech[:4])})" if lech else "") + "\n"
            f"Do khop tung tep trong data/:\n" + "\n".join(dong) +
            "\n\nDoi theo id KHONG du: bo sinh dung lai khong gian id giua cac\n"
            "the he, nen mot bo sai van khop 60/60 theo id. Chon tep khop\n"
            "NOI DUNG, bang --tap-goc.")
    return {i: goc[i].get("benh") for i in theo_id}


# ----------------------------------------------------------------- lấy lại mẫu

# ─── _trung_binh() — Tính trung bình, rỗng thì trả NaN ────────────────────────────────
def _trung_binh(gia_tri):
    return sum(gia_tri) / len(gia_tri) if gia_tri else float("nan")


# ─── _mau_theo_ca() — Lấy lại mẫu theo ca rồi tính trung bình ─────────────────────────
def _mau_theo_ca(gia_tri, rng):
    n = len(gia_tri)
    return _trung_binh([gia_tri[rng.randrange(n)] for _ in range(n)])


# ─── _mau_theo_khuon() — Lấy lại mẫu bootstrap theo cụm khuôn bệnh ────────────────────
# Lấy lại tên khuôn, mỗi khuôn kéo theo cả cụm ca của nó.
def _mau_theo_khuon(theo_khuon, rng):
    """Bootstrap cụm: lấy lại mẫu TÊN KHUÔN, mỗi khuôn lấy cả cụm ca của nó."""
    ten = list(theo_khuon)
    gop = []
    for _ in range(len(ten)):
        gop.extend(theo_khuon[ten[rng.randrange(len(ten))]])
    return _trung_binh(gop)


# ─── _phan_vi() — Tính phân vị có nội suy trên dãy đã sắp ─────────────────────────────
def _phan_vi(da_sap, p):
    if not da_sap:
        return float("nan")
    vi_tri = p * (len(da_sap) - 1)
    duoi = int(vi_tri)
    tren = min(duoi + 1, len(da_sap) - 1)
    le = vi_tri - duoi
    return da_sap[duoi] * (1 - le) + da_sap[tren] * le


# ═══ khoang() — Tính khoảng tin cậy bootstrap cho một chỉ số ══════════════════════════
# Lấy lại mẫu theo khuôn nếu có, không thì theo ca; trường don_vi ghi rõ để biết khoảng
# có lạc quan không.
def khoang(gia_tri_theo_id, khuon=None, so_lan=SO_LAN_MAC_DINH,
           hat=HAT_MAC_DINH, muc=0.95):
    """-> {trung_binh, thap, cao, so_ca, so_khuon, don_vi}.

    `khuon` có thì lấy lại mẫu theo khuôn (đơn vị độc lập đúng). Không có thì
    lấy lại mẫu theo ca, và trường `don_vi` ghi rõ là "ca" để đọc bảng biết
    đây là khoảng LẠC QUAN.
    """
    rng = random.Random(hat)
    gia_tri = list(gia_tri_theo_id.values())
    if khuon:
        theo_khuon = {}
        for i, v in gia_tri_theo_id.items():
            theo_khuon.setdefault(khuon[i], []).append(v)
        mau = sorted(_mau_theo_khuon(theo_khuon, rng) for _ in range(so_lan))
        don_vi, so_khuon = "khuôn", len(theo_khuon)
    else:
        mau = sorted(_mau_theo_ca(gia_tri, rng) for _ in range(so_lan))
        don_vi, so_khuon = "ca", None
    le = (1 - muc) / 2
    return {"trung_binh": _trung_binh(gia_tri),
            "thap": _phan_vi(mau, le), "cao": _phan_vi(mau, 1 - le),
            "so_ca": len(gia_tri), "so_khuon": so_khuon, "don_vi": don_vi}


# ═══ so_sanh() — So sánh theo cặp hai nhánh bằng bootstrap ════════════════════════════
# Tính hiệu, khoảng tin cậy của hiệu và tỉ lệ dấu ngược (không gọi là p) trên ca chung.
def so_sanh(a_theo_id, b_theo_id, khuon=None, so_lan=SO_LAN_MAC_DINH,
            hat=HAT_MAC_DINH, muc=0.95):
    """So sánh THEO CẶP trên các ca CÓ Ở CẢ HAI nhánh.

    -> {hieu, thap, cao, so_ca_chung, ty_le_dau_nguoc}

    `ty_le_dau_nguoc` là tỷ lệ lần lấy lại mẫu cho hiệu trái dấu với hiệu đo
    được. Nhân đôi nó được một giá trị gần nghĩa với p hai phía. Gọi đúng tên
    là tỷ lệ, không gọi là p: với 8 khuôn thì con số đó không đủ chính xác để
    mang tên p.
    """
    chung = sorted(set(a_theo_id) & set(b_theo_id))
    if not chung:
        raise SystemExit("hai nhanh khong co ca nao chung — khong so sanh duoc")
    hieu = {i: a_theo_id[i] - b_theo_id[i] for i in chung}
    k = khoang(hieu, {i: khuon[i] for i in chung} if khuon else None,
               so_lan, hat, muc)
    rng = random.Random(hat + 1)
    if khuon:
        theo_khuon = {}
        for i, v in hieu.items():
            theo_khuon.setdefault(khuon[i], []).append(v)
        mau = [_mau_theo_khuon(theo_khuon, rng) for _ in range(so_lan)]
    else:
        gt = list(hieu.values())
        mau = [_mau_theo_ca(gt, rng) for _ in range(so_lan)]
    quan_sat = k["trung_binh"]
    nguoc = sum(1 for m in mau
                if ((m <= 0) if quan_sat > 0 else (m >= 0)))
    return {"hieu": quan_sat, "thap": k["thap"], "cao": k["cao"],
            "so_ca_chung": len(chung), "so_khuon": k["so_khuon"],
            "don_vi": k["don_vi"], "ty_le_dau_nguoc": nguoc / len(mau)}


# ------------------------------------------------------------------ báo cáo

# ------------------------------------------------- đo CÔNG SUẤT của phép đo
#
# Bốn tầng quy gán, xếp theo độ khó THẬT:
#
#   1 lượt bác sĩ                 chủ thể luôn là bệnh nhân        không khó
#   2 lượt bệnh nhân              chủ thể là chính người nói       không khó
#   3 người nhà kể HỘ bệnh nhân   "chủ thể = người nói" SAI        khó
#   4 người nhà kể VỀ CHÍNH MÌNH  cả hai đường tắt đều SAI         khó nhất
#
# Tầng 4 là chỗ dự án này tồn tại. Đo được trên ba thế hệ dữ liệu:
#
#   bộ 3.000 (dev)   67/3.507 mệnh đề = 1,91%
#   bộ 5.000 (dev)  137/5.896 mệnh đề = 2,32%
#
# Và trong 60 ca đã dùng để so sánh các nhánh: 7 mệnh đề tầng 4 trên 514.
#
# HỆ QUẢ, và đây là chỗ phải ghi vào báo cáo: ảnh hưởng TỐI ĐA mà cơ chế quy
# gán có thể tạo ra trên một thước đo GỘP là 1,4 điểm. Bề rộng khoảng tin cậy
# đo được là ±0,9 đến ±1,4 điểm. Phép đo không đủ công suất để thấy điều nó
# được dùng để thấy.
#
# Không phải "cơ chế không hiệu quả". Là "phép đo không trả lời được câu hỏi".
# Hai kết luận đó khác nhau, và lần thứ hai bắt buộc phải sửa PHÉP ĐO, không
# phải sửa cơ chế.

VAI_BAC_SI = ("bác sĩ",)
VAI_BENH_NHAN = ("bệnh nhân",)
TANG = ("bac_si", "benh_nhan", "ke_ho", "ke_ve_minh")


# ═══ nguoi_noi_tung_luot() — Lấy vai người nói của từng lượt trong ca ═════════════════
# Trả {số lượt từ 1: vai}; dòng không có vai ghi dấu hỏi.
def nguoi_noi_tung_luot(ban_ghi):
    """-> {số thứ tự lượt (đếm từ 1): vai người nói}."""
    import re
    ra = {}
    dong = [d for d in str(ban_ghi.get("input") or "").split("\n") if d.strip()]
    for i, d in enumerate(dong, 1):
        m = re.match(r"^([^:]{1,30}):", d)
        ra[i] = m.group(1).strip() if m else "?"
    return ra


# ═══ tang_cua() — Xếp một mệnh đề đáp án vào tầng quy gán ═════════════════════════════
# Bốn tầng: bac_si, benh_nhan, ke_ho, ke_ve_minh. Người nói là lượt cuối trong bằng
# chứng; điều dưỡng tính là bác sĩ.
def tang_cua(menh_de, vai_theo_luot):
    """Tầng của MỘT mệnh đề đáp án -> "bac_si" | "benh_nhan" | "ke_ho" |
    "ke_ve_minh", hoặc None nếu mệnh đề không có lượt.

    MỘT ĐỊNH NGHĨA, dùng chung cho `tang_menh_de` và
    `do_tang_quy_gan.menh_de_dap_an`. Trước 11/09/2026 mỗi tệp giữ một bản sao
    của cùng logic này — họ lỗi "hai bảng cùng nghĩa ở hai tệp".

    Hai quy ước, cả hai sửa ngày 11/09/2026:

      NGƯỜI NÓI = người nói LƯỢT CUỐI trong bằng chứng, giống
      `phat_bieu.tu_json`. Câu trả lời tắt mang cả lượt CÂU HỎI đứng trước;
      lấy lượt đầu thì mọi câu "Dạ, không ạ" của người nhà thành lời bác sĩ.

      MỌI vai nhân viên y tế — cả ĐIỀU DƯỠNG — là tầng `bac_si`. Trước đó chỉ
      "bác sĩ": điều dưỡng đọc sinh hiệu là nói VỀ bệnh nhân, nhưng rơi vào
      tầng `ke_ho` như một người nhà kể thay.
    """
    from src.duong_ong.b1_cau_truc_menh_de import la_vai_nhan_vien
    luot = menh_de.get("luot") or []
    if not luot:
        return None
    nn = str(vai_theo_luot.get(max(luot), "?")).lower()
    if la_vai_nhan_vien(nn):
        return "bac_si"
    if nn in VAI_BENH_NHAN:
        return "benh_nhan"
    if menh_de.get("chu_the") == "bệnh nhân":
        return "ke_ho"
    return "ke_ve_minh"


# ═══ tang_menh_de() — Đếm mệnh đề của một ca theo bốn tầng ════════════════════════════
def tang_menh_de(ban_ghi_goc):
    """-> Counter trên bốn tầng, cho MỘT ca (bản ghi của bộ dữ liệu)."""
    from collections import Counter
    vai = nguoi_noi_tung_luot(ban_ghi_goc)
    ra = Counter()
    for m in ban_ghi_goc.get("dap_an") or []:
        tang = tang_cua(m, vai)
        if tang:
            ra[tang] += 1
    return ra


# ═══ do_cong_suat() — Đo công suất phép đo qua tỉ lệ mệnh đề tầng 4 ═══════════════════
# Trả ảnh hưởng tối đa mà cơ chế quy gán tạo được trên thước đo gộp; đây là trần, không
# phải dự đoán.
def do_cong_suat(goc_theo_id):
    """-> {tong, theo_tang, ty_le_tang4, anh_huong_toi_da}.

    `anh_huong_toi_da` là chênh lệch LỚN NHẤT có thể có trên một thước đo gộp
    nếu cơ chế quy gán sửa đúng hết tầng 4 và đối chứng sai hết. Nó là trần
    trên, không phải dự đoán.
    """
    from collections import Counter
    gop = Counter()
    for b in goc_theo_id.values():
        gop += tang_menh_de(b)
    tong = sum(gop.values()) or 1
    return {"tong": tong, "theo_tang": dict(gop),
            "ty_le_tang4": gop["ke_ve_minh"] / tong,
            "anh_huong_toi_da": gop["ke_ve_minh"] / tong}


# ═══ canh_cong_suat() — Cảnh báo khi phép đo không đủ công suất ═══════════════════════
# So trần ảnh hưởng với bề rộng khoảng tin cậy; trần nhỏ hơn thì không thấy được hiệu
# ứng.
def canh_cong_suat(cong_suat, rong_ktc):
    """-> chuỗi cảnh báo, hoặc None nếu phép đo đủ công suất.

    So TRẦN ẢNH HƯỞNG với BỀ RỘNG KHOẢNG TIN CẬY. Trần nhỏ hơn bề rộng thì
    phép so sánh không thể thấy được hiệu ứng, kể cả khi hiệu ứng có thật.
    """
    tran = cong_suat["anh_huong_toi_da"]
    if rong_ktc != rong_ktc or tran >= rong_ktc:
        return None
    n4 = cong_suat["theo_tang"].get("ke_ve_minh", 0)
    return (f"**Phép đo không đủ công suất.** Mệnh đề tầng 4 — người nhà kể về "
            f"chính mình, nơi cả hai đường tắt đều sai — chỉ có **{n4}/"
            f"{cong_suat['tong']} = {_pt(tran)}** trong mẫu này. Ảnh hưởng tối "
            f"đa mà cơ chế quy gán có thể tạo ra trên thước đo gộp là "
            f"{_pt(tran)}, trong khi khoảng tin cậy rộng {_pt(rong_ktc)}. "
            f"Mọi kết luận "
            f"*“cơ chế không có tác dụng”* đọc từ bảng này là đọc sai: phép đo "
            f"không trả lời được câu hỏi đó. Phải chấm riêng trên tầng 4, và "
            f"phải tăng tỷ lệ tầng 4 trong bộ sinh.")


# ═══ canh_so_khuon() — Cảnh báo khi mẫu có quá ít khuôn bệnh ══════════════════════════
# Dưới ngưỡng tối thiểu thì đơn vị độc lập quá ít, kết quả không nói được về cả bộ
# khuôn.
def canh_so_khuon(so_khuon, toi_thieu=KHUON_TOI_THIEU):
    """-> chuỗi cảnh báo, hoặc None. Đặt ở ĐẦU bảng, không nhét xuống cuối."""
    if so_khuon is None or so_khuon >= toi_thieu:
        return None
    return (f"**Mẫu chỉ nằm trên {so_khuon} khuôn bệnh.** Đơn vị độc lập của bộ "
            f"dữ liệu là khuôn, không phải ca (xem `tach_tap_viet`), nên phép so "
            f"sánh này có {so_khuon} đơn vị độc lập chứ không phải "
            f"{{so_ca}} — nó không nói được gì về bộ khuôn đầy đủ.")


# ─── _so() — Định dạng số thập phân dùng dấu phẩy ─────────────────────────────────────
def _so(x, chu_so=4):
    return "—" if x != x else f"{x:.{chu_so}f}".replace(".", ",")


# ─── _pt() — Định dạng tỉ lệ thành phần trăm dấu phẩy ─────────────────────────────────
def _pt(x, chu_so=2):
    """Phần trăm với dấu phẩy thập phân — bảng trong báo cáo tiếng Việt."""
    return "—" if x != x else f"{x * 100:.{chu_so}f}".replace(".", ",") + "%"


# ═══ bang() — Dựng bảng khoảng tin cậy và so sánh cặp với nhánh gốc ═══════════════════
# Đặt cảnh báo số khuôn và công suất ở đầu bảng, không để cuối.
def bang(ten_goc, diem_theo_nhanh, khuon, khoa="final", goc_theo_id=None):
    """Bảng khoảng tin cậy + so sánh theo cặp với nhánh gốc.

    Hai cảnh báo đặt ở ĐẦU bảng, không nhét xuống cuối: số khuôn, và công
    suất. Một cảnh báo ở cuối bảng thì người đọc đã đọc xong số rồi.
    """
    d = [f"### Thước đo `{khoa}`", ""]
    so_khuon = len(set(khuon.values())) if khuon else None
    canh = canh_so_khuon(so_khuon)
    if canh:
        mot = next(iter(diem_theo_nhanh.values()))
        d += ["> " + canh.replace("{so_ca}", str(len(mot))), ""]

    if goc_theo_id:
        cs = do_cong_suat(goc_theo_id)
        goc_diem = diem_theo_nhanh[ten_goc]
        k = khoang(goc_diem, khuon)
        cc = canh_cong_suat(cs, k["cao"] - k["thap"])
        if cc:
            d += ["> " + cc, ""]
        d += ["Phân tầng quy gán của mẫu: "
              + "  ·  ".join(f"{t} **{cs['theo_tang'].get(t, 0)}**"
                             for t in TANG), ""]

    d += ["| Nhánh | Trung bình | KTC 95% theo ca | KTC 95% theo khuôn |",
          "|---|---|---|---|"]
    for ten, diem in diem_theo_nhanh.items():
        kc = khoang(diem)
        kk = khoang(diem, khuon) if khuon else None
        d.append(f"| `{ten}` | {_so(kc['trung_binh'])} | "
                 f"[{_so(kc['thap'])}; {_so(kc['cao'])}] | "
                 f"{'[' + _so(kk['thap']) + '; ' + _so(kk['cao']) + ']' if kk else '—'} |")
    d += ["",
          f"So sánh **theo cặp** với `{ten_goc}` — khoảng tin cậy của HIỆU, "
          "không phải hai khoảng rời:", "",
          "| Nhánh | Hiệu | KTC 95% của hiệu (theo khuôn) | Tỷ lệ dấu ngược |",
          "|---|---|---|---|"]
    goc = diem_theo_nhanh[ten_goc]
    for ten, diem in diem_theo_nhanh.items():
        if ten == ten_goc:
            continue
        s = so_sanh(diem, goc, khuon)
        d.append(f"| `{ten}` | {_so(s['hieu'])} | "
                 f"[{_so(s['thap'])}; {_so(s['cao'])}] | "
                 f"{_pt(s['ty_le_dau_nguoc'], 1)} |")
    d += ["",
          "*Tỷ lệ dấu ngược* là tỷ lệ lần lấy lại mẫu cho hiệu trái dấu với "
          "hiệu đo được. Nhân đôi được một giá trị gần nghĩa với p hai phía. "
          "Không gọi là p: với số khuôn nhỏ thì con số đó không đủ chính xác "
          "để mang tên đó.", ""]
    return "\n".join(d)


# ═══ main() — Chạy dòng lệnh dựng bảng khoảng tin cậy các nhánh ═══════════════════════
# Nạp kết quả nhánh, đối chiếu bộ dữ liệu, kiểm dấu vân tay bộ, rồi in hoặc ghi bảng.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--tap-goc", default=None,
                    help="tep bo du lieu de lay khuon benh; mac dinh data/<tap>.jsonl")
    ap.add_argument("--nhanh", nargs="+", default=["B", "C", "D"])
    # Quy ước `ra_<nhanh>_<tap>.jsonl` đã sinh ra một lỗi thật: tên tệp nói
    # `viet_phat_trien` trong khi kết quả chạy trên `viet3k_phat_trien`. Chỗ
    # này để gọi thẳng đường dẫn, không phải vòng qua quy ước tên.
    ap.add_argument("--tep", nargs="+", default=None,
                    metavar="TEN=DUONG_DAN",
                    help="chi dinh thang tung nhanh, vi du B=data/ra_B.jsonl")
    ap.add_argument("--goc", default=None, help="nhanh lam moc so sanh")
    ap.add_argument("--khoa", default="f1_quy_gan",
                    choices=sorted(k for v in HO_THUOC_DO.values() for k in v),
                    help="mac dinh f1_quy_gan — thuoc do chinh cua du an")
    ap.add_argument("--so-lan", type=int, default=SO_LAN_MAC_DINH)
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()
    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_tap_khoa(a.tap)

    nguon = ({k: Path(v) for k, v in (x.split("=", 1) for x in a.tep)}
             if a.tep else
             {n: THU_MUC_DATA / f"ra_{n}_{a.tap}.jsonl" for n in a.nhanh})
    diem_theo_nhanh, ban_ghi = {}, {}
    for n, tep in nguon.items():
        if not tep.exists():
            print(f"bo qua {n}: khong co {tep}")
            continue
        diem_theo_nhanh[n], bg = diem_tung_ca(tep, a.khoa)
        ban_ghi.update(bg)
    if not diem_theo_nhanh:
        raise SystemExit("khong nap duoc nhanh nao")

    moi_id = sorted({i for d in diem_theo_nhanh.values() for i in d})
    tap_goc = Path(a.tap_goc) if a.tap_goc else THU_MUC_DATA / f"{a.tap}.jsonl"
    khuon = doi_chieu_tap({i: ban_ghi[i] for i in moi_id}, tap_goc)
    goc_theo_id = {b["id"]: b for b in _doc(tap_goc) if b["id"] in set(moi_id)}

    # Vân tay in ở ĐẦU bảng. Một bảng số không nói nó đo trên bộ nào thì ba
    # tháng sau không đọc được — và ba lần họ lỗi "một tên tệp, hai bộ dữ liệu"
    # đều bắt đầu từ một bảng như thế.
    from src.duong_ong import b1_cau_truc_menh_de as phat_bieu
    from src.bo_du_lieu import van_tay_bo as van_tay_bo
    dong_van_tay = [van_tay_bo.mo_ta(tap_goc)]
    # Đối chiếu với CẢ TỆP, không với `goc_theo_id` — biên độ chỉ chứa các ca
    # đang được đo (60 ca), còn vân tay lập trên cả bộ (408 ca). So hai thứ đó
    # với nhau thì hàng rào báo oan mỗi lần chạy, và một hàng rào báo oan sẽ bị
    # tắt đi — lúc đó nó thành vô dụng đúng vào lần nó cần lên tiếng.
    khop, thong_diep = van_tay_bo.khop(tap_goc, _doc(tap_goc))
    if khop is False:
        raise SystemExit(thong_diep)
    thieu = van_tay_bo.nhan_thieu_vi_du(
        tap_goc, {"quan_he": phat_bieu.QUAN_HE,
                  "trang_thai": phat_bieu.TRANG_THAI,
                  "tinh_huong": phat_bieu.TINH_HUONG})
    for truong, cac_nhan in thieu.items():
        dong_van_tay.append(
            f"**`{truong}`: {', '.join(cac_nhan)} không có ví dụ nào trong bộ "
            f"này** — mọi số về nhãn đó là số của một nhãn không có dữ liệu.")

    ten_goc = a.goc or list(diem_theo_nhanh)[0]
    van = bang(ten_goc, diem_theo_nhanh, khuon, a.khoa, goc_theo_id)
    van = "\n".join(f"> {x}" for x in dong_van_tay) + "\n\n" + van
    print(van)
    print(f"\n{len(moi_id)} ca, {len(set(khuon.values()))} khuon, "
          f"bo du lieu {tap_goc.name}")
    if a.ra:
        Path(a.ra).write_text(van + "\n", encoding="utf-8")
        print(f"-> {a.ra}")


if __name__ == "__main__":
    main()
