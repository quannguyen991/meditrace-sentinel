# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ sinh]
Làm gì   : Tăng thêm mẫu có người nhà bằng cách biến đổi hội thoại sẵn có, không dùng mô
           hình ngôn ngữ sinh mới.
Vào → Ra : danh sách mẫu chưa có người nhà + số lượng + hạt giống → mẫu mới (chèn lượt người
           nhà hoặc đổi vai) kèm nhãn đúng
Đọc từ   : tang_cuong() chạy cả hai phép; chen_tien_su_nguoi_nha() chèn lượt kể bệnh;
           doi_vai_thanh_nguoi_nha() đổi vai
Mục lục (các hàm/lớp chính):
  tang_cuong()               Tăng cường mẫu chưa có người nhà bằng hai cách biến đổi
  chen_tien_su_nguoi_nha()   Chèn một lượt người nhà kể bệnh của chính họ
  doi_vai_thanh_nguoi_nha()  Đổi lượt bệnh nhân thành người nhà và chuyển đại từ
  main()                     Chạy tăng cường dữ liệu và ghi tệp ra
Gọi tới  : bo_du_lieu/nap_du_lieu, he_thong/duong_dan
Tên cũ   : tang_cuong.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tăng cường tập huấn luyện bằng BIẾN ĐỔI dữ liệu có sẵn.

KHÔNG dùng mô hình ngôn ngữ để sinh hội thoại mới. Nên văn bản giữ nguyên là
văn phong và cách nói trong dữ liệu gốc; chỉ nhãn vai và lượt chèn thêm là do
chương trình đặt. Lý do ở Global Constraint 1: dữ liệu do một mô hình sinh khác
tạo ra sẽ có quy gán sạch một cách nhân tạo, làm nhiễm chính hiện tượng đang đo.

Hai phép biến đổi, và nhãn đòi KHÁC NHAU:

    doi_vai_thanh_nguoi_nha   bệnh án KHÔNG đổi — triệu chứng vẫn của bệnh nhân
    chen_tien_su_nguoi_nha    bệnh án PHẢI THÊM mục TIỀN SỬ GIA ĐÌNH

Câu "bệnh án luôn giữ nguyên" là SAI. Tiền sử của người nhà thuộc mục tiền sử
gia đình, không phải không ghi gì.

    python -m src.bo_du_lieu.tang_cuong --chen 150 --doi-vai 50
"""
import argparse
import copy
import io
import random
import re
import sys

# Mẫu câu RIÊNG cho tăng cường.
# PHẢI rời hẳn với `sinh_bo_chan_doan.MAU_CAU` — trùng mẫu câu nghĩa là huấn luyện
# trên đúng thứ sẽ dùng để kiểm tra. Có test `test_mau_cau_roi_han_voi_bo_chan_doan`.
MAU_CAU = [
    "Nhà tôi có tiền sử {benh}, riêng cháu thì chưa.",
    "Bên tôi thì bị {benh} lâu rồi, còn cháu chưa thấy gì.",
    "Trong nhà tôi bị {benh}, cháu chưa bao giờ.",
    "Bố mẹ tôi đều có {benh}, cháu thì chưa kiểm tra.",
]

BENH = ["cao huyết áp", "tiểu đường", "hen suyễn", "đau dạ dày", "tim mạch", "viêm xoang"]

MUC_GIA_DINH = "TIỀN SỬ GIA ĐÌNH"

# Đổi đại từ khi chuyển vai "Bệnh nhân" -> "Người nhà".
# Chỉ đổi đại từ NGÔI THỨ NHẤT đứng một mình, không động tới "con tôi", "nhà tôi"…
_DAI_TU = [
    (re.compile(r"\bTôi\b"), "Cháu"),
    (re.compile(r"\btôi\b"), "cháu"),
    (re.compile(r"\bEm\b"), "Cháu"),
    (re.compile(r"\bem\b"), "cháu"),
]

# Không đổi vai khi câu chứa những cụm này — đổi đại từ sẽ ra câu vô nghĩa:
# "Tôi thấy con tôi mệt" -> "Cháu thấy con cháu mệt"
# Mọi từ chỉ quan hệ họ hàng đi trước "tôi"/"em": đổi đại từ sẽ tạo cụm
# mơ hồ kiểu "ba cháu" (bố của cháu, hay ba đứa cháu?).
_QUAN_HE = (
    "con|cháu|nhà|vợ|chồng|mẹ|bố|ba|má|cha|anh|chị|em|ông|bà|"
    "gia đình|con trai|con gái|chị họ|anh họ|em họ|ông nội|bà nội|ông ngoại|bà ngoại"
)
_KHONG_DOI_VAI = re.compile(rf"(?i)\b({_QUAN_HE})\s+(tôi|em)\b")

# Từ chối luôn khi hội thoại ĐÃ CÓ sẵn chữ "cháu" hoặc "bé".
# Tìm ra khi soát tay 12 mẫu: đổi "tôi" -> "cháu" làm từ này quá tải.
#   "Tôi có hai bé trai, các cháu ở với tôi"
#       -> "Cháu có hai bé trai, các cháu ở với cháu"   (chau mang hai nghia)
#   "Ba tôi với ông nội đều bị đái tháo đường"
#       -> "Ba cháu với ông nội…"   ("ba chau" = bo cua chau hay ba dua chau?)
_DA_CO_CHAU = re.compile(r"(?i)\b(cháu|bé)\b")


# ═══ chen_tien_su_nguoi_nha() — Chèn một lượt người nhà kể bệnh của chính họ ══════════
# Bệnh án phải thêm mục tiền sử gia đình, vì thông tin đó không thuộc bệnh nhân.
def chen_tien_su_nguoi_nha(mau, seed):
    """Chèn một lượt người nhà kể bệnh CỦA CHÍNH HỌ.

    Bệnh án PHẢI thêm mục TIỀN SỬ GIA ĐÌNH — thông tin đó không thuộc bệnh nhân,
    nhưng cũng không được bỏ đi.
    """
    rnd = random.Random(seed)
    ra = copy.deepcopy(mau)
    benh = rnd.choice(BENH)
    cau = rnd.choice(MAU_CAU).format(benh=benh)

    dong = ra["input"].split("\n")
    vi_tri = rnd.randrange(1, len(dong) + 1)
    dong.insert(vi_tri, f"Người nhà: {cau}")
    ra["input"] = "\n".join(dong)

    ra["output"] = ra["output"].rstrip() + f"\n\n{MUC_GIA_DINH}\n\nNgười nhà có {benh}."
    ra["id"] = f"{mau['id']}_chen"
    ra["tang_cuong"] = "chen_tien_su"
    return ra


# ═══ doi_vai_thanh_nguoi_nha() — Đổi lượt bệnh nhân thành người nhà và chuyển đại từ ═══
# Bệnh án không đổi; trả None nếu không chuyển đại từ an toàn được.
def doi_vai_thanh_nguoi_nha(mau):
    """Đổi `Benh nhan:` thành `Nguoi nha:` và chuyển đại từ.

    Bệnh án KHÔNG đổi: triệu chứng vẫn thuộc về bệnh nhân, chỉ là người kể thay.
    Trả None khi không chuyển đại từ an toàn được.
    """
    dong = mau["input"].split("\n")
    if not any(d.startswith("Bệnh nhân:") for d in dong):
        return None
    if _KHONG_DOI_VAI.search(mau["input"]):
        return None
    if _DA_CO_CHAU.search(mau["input"]):
        return None

    moi = []
    for d in dong:
        if d.startswith("Bệnh nhân:"):
            noi_dung = d[len("Bệnh nhân:"):]
            for pat, thay in _DAI_TU:
                noi_dung = pat.sub(thay, noi_dung)
            moi.append("Người nhà:" + noi_dung)
        else:
            moi.append(d)

    ra = copy.deepcopy(mau)
    ra["input"] = "\n".join(moi)
    ra["id"] = f"{mau['id']}_doivai"
    ra["tang_cuong"] = "doi_vai"
    return ra


# ═══ tang_cuong() — Tăng cường mẫu chưa có người nhà bằng hai cách biến đổi ═══════════
# Chỉ biến đổi mẫu không có lượt người nhà; mẫu đã có giữ nguyên.
def tang_cuong(mau_list, n_chen=150, n_doi_vai=50, seed=42):
    """Chỉ biến đổi mẫu KHÔNG có lượt người nhà — mẫu đã có thì giữ nguyên."""
    from src.bo_du_lieu import nap_du_lieu as du_lieu

    rnd = random.Random(seed)
    ung_vien = [m for m in mau_list if not du_lieu.co_nguoi_nha(m)]
    rnd.shuffle(ung_vien)

    them = []
    for m in ung_vien:
        if len(them) >= n_chen:
            break
        them.append(chen_tien_su_nguoi_nha(m, seed=hash(m["id"]) % 10**6))

    da_dung = {m["id"] for m in them}
    doi = []
    for m in ung_vien:
        if len(doi) >= n_doi_vai:
            break
        if f"{m['id']}_chen" in da_dung:
            continue
        r = doi_vai_thanh_nguoi_nha(m)
        if r is not None:
            doi.append(r)

    return mau_list + them + doi


# ═══ main() — Chạy tăng cường dữ liệu và ghi tệp ra ═══════════════════════════════════
# Tham số: số mẫu chèn, số mẫu đổi vai và hạt giống.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chen", type=int, default=150)
    ap.add_argument("--doi-vai", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as du_lieu
    from src.he_thong import duong_dan as duong_dan

    goc = du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / "train.jsonl")
    ra = tang_cuong(goc, a.chen, a.doi_vai, a.seed)
    du_lieu.ghi_mau(duong_dan.THU_MUC_DU_LIEU / "train_tang_cuong.jsonl", ra)

    nn_goc = len(du_lieu.loc_mau_co_nguoi_nha(goc))
    nn_ra = len(du_lieu.loc_mau_co_nguoi_nha(ra))
    print(f"Truoc : {len(goc):5d} mau, {nn_goc:4d} co nguoi nha")
    print(f"Sau   : {len(ra):5d} mau, {nn_ra:4d} co nguoi nha")
    print(f"Them  : {len(ra) - len(goc):5d} mau  (+{nn_ra - nn_goc} co nguoi nha)")


if __name__ == "__main__":
    main()
