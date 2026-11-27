# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ thử thách]
Làm gì   : Sinh bộ kiểm tra chẩn đoán lỗi bằng luật, mỗi mẫu cài một bẫy (chủ thể, chắc
           chắn, đính chính, diễn biến...).
Vào → Ra : số mẫu mỗi loại bẫy + hạt giống → danh sách mẫu có bẫy kèm đáp án; main() ghi tệp
Đọc từ   : sinh_bo() dựng cả bộ từ các hàm _bay_*; _bay_chu_the() là một mẫu bẫy
Mục lục (các hàm/lớp chính):
  sinh_bo()          Sinh bộ chẩn đoán, mỗi tình huống bẫy n mẫu
  main()             Sinh và ghi bộ chẩn đoán bằng dòng lệnh
  _bay_chu_the()     Sinh ca bẫy chủ thể: người nhà dị ứng, trẻ chưa
  _bay_chac_chan()   Sinh ca bẫy độ chắc chắn của phủ định
  _bay_dinh_chinh()  Sinh ca bẫy tự sửa số ngày sốt
  _bay_nghi_ngo()    Sinh ca bẫy nghi ngờ không thành chẩn đoán xác định
  _bay_nhat_quan()   Sinh ca bẫy nhất quán giữa hai mục bệnh án
Gọi tới  : he_thong/duong_dan
Dùng bởi : do_luong/do_bo_chan_doan, do_luong/do_van_xuoi, do_luong/doi_chung_tam_thuong
Tên cũ   : sinh_bo_chan_doan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Sinh bộ kiểm tra chẩn đoán bằng LUẬT, không bằng mô hình ngôn ngữ.

Vì sao có bộ này: 35 mẫu tập phát triển là cỡ nhỏ, và bốn nhóm lỗi không phân
bố đều trong đó — có thể cả 35 mẫu không có mẫu nào chứa đính chính. Bộ này
giải quyết đúng chuyện đó: sinh CẢ hội thoại LẪN bệnh án đúng bằng cùng một
đoạn mã, nên đáp án biết trước chính xác, không cần gán nhãn tay.

    CHỈ ĐỂ ĐÁNH GIÁ. Tuyệt đối không đưa vào huấn luyện.
    Train trên mẫu câu thì mô hình học thuộc mẫu câu, mọi kết quả thành vô nghĩa.

    SINH BẰNG MÃ CỦA MÌNH, không bằng LLM. Xem Global Constraint 1.

Tám tình huống. Nhóm `sach` là BẮT BUỘC: không có nó thì không phân biệt được
"bắt được bẫy" với "cảnh giác quá mức, gán cờ mọi thứ".

Nhóm `nhat_quan` thêm 09/09/2026, cho thách thức 5. Trước đó KHÔNG phép đo
nào của dự án bắt được lỗi mâu thuẫn giữa hai mục: bảy nhóm cũ đều chỉ xét
MỘT câu một, còn ROUGE thì đếm từ nên hai câu đều khớp.

Cảnh báo về sức mạnh thống kê: 420 biến thể sinh từ vài khuôn KHÔNG tương đương
420 ca độc lập. Số khuôn gốc mới là đơn vị độc lập.

    python -m src.bo_du_lieu.sinh_bo_chan_doan --n 60 --seed 42
"""
import argparse
import io
import random
import sys

# Mẫu câu RIÊNG cho bộ chẩn đoán.
# PHẢI rời hẳn với `tang_cuong.MAU_CAU` — trùng mẫu câu là rò rỉ: kiểm tra
# trên đúng thứ đã dạy. Có test `test_mau_cau_roi_han_voi_bo_chan_doan`.
MAU_CAU = [
    "Tôi thì dị ứng {thuoc}, còn cháu chưa thấy bị bao giờ.",
    "Bản thân tôi dị ứng {thuoc}, cháu thì chưa lần nào.",
    "Chưa thấy cháu bị {trieu_chung} bao giờ ạ.",
    "Cháu chưa lần nào bị {trieu_chung} cả.",
    "{n} ngày ạ… À không, hôm kia mới bắt đầu, vậy là {m} ngày.",
    "Khoảng {n} hôm rồi… à mà không, {m} hôm thôi ạ.",
    "Hôm qua cháu {trieu_chung}, hôm nay thì hết rồi ạ.",
    "Tối qua cháu còn {trieu_chung}, sáng nay đỡ hẳn.",
    "Nếu mai cháu vẫn {trieu_chung} thì tôi cho uống thêm ạ.",
    "Trường hợp cháu {trieu_chung} tiếp thì tôi đưa cháu quay lại nhé.",
]

THUOC = ["penicillin", "amoxicillin", "cephalexin", "sulfamid", "aspirin"]
# Thuốc dùng RIÊNG cho bẫy nhất quán. Tách khỏi THUOC vì bẫy nhất quán hỏi
# "thuốc này có đang dùng không", còn THUOC dùng cho bẫy dị ứng — trộn vào
# nhau thì một mẫu có thể vừa là bẫy này vừa là bẫy kia, và không còn biết
# phép kiểm đang bắt cái gì.
THUOC_DA_NGUNG = ["metformin", "omeprazole", "salbutamol", "cetirizine",
                  "paracetamol"]
TRIEU_CHUNG = ["sốt", "ho", "nôn", "đau bụng", "tiêu chảy", "khó thở"]
TRIEU_CHUNG_PHU = ["ho khan", "chán ăn", "quấy khóc", "mệt mỏi"]
# Bệnh dùng RIÊNG cho bẫy nghi_ngo. Phải là bệnh CẦN XÉT NGHIỆM mới kết luận
# được — nếu chọn một bệnh chẩn đoán bằng mắt thường thì bẫy không còn nghĩa.
BENH_CHO_KET_QUA = [
    ("viêm phổi", "chụp X-quang ngực"),
    ("sốt xuất huyết", "xét nghiệm công thức máu"),
    ("viêm đường tiết niệu", "xét nghiệm nước tiểu"),
    ("thiếu máu", "xét nghiệm công thức máu"),
    ("sỏi thận", "siêu âm bụng"),
]
TUOI = ["hai", "ba", "bốn", "năm", "sáu"]

BAY = ("chu_the", "chac_chan", "dinh_chinh", "dien_bien", "gia_dinh",
       "moi_bia", "nghi_ngo", "nhat_quan", "sach")


# ─── _mo_dau() — Dựng đoạn mở đầu hỏi tuổi trẻ ────────────────────────────────────────
# Trả các dòng hội thoại và câu bệnh sử mở đầu.
def _mo_dau(rnd):
    tuoi = rnd.choice(TUOI)
    return (
        [f"Bác sĩ: Chào chị, cháu năm nay mấy tuổi ạ?",
         f"Người nhà: Dạ cháu {tuoi} tuổi."],
        f"Trẻ {tuoi} tuổi.",
    )


# ─── _bay_chu_the() — Sinh ca bẫy chủ thể: người nhà dị ứng, trẻ chưa ─────────────────
# Đáp án đúng: dị ứng thuộc tiền sử gia đình, không thuộc trẻ.
def _bay_chu_the(rnd, i):
    dong, mo = _mo_dau(rnd)
    thuoc = rnd.choice(THUOC)
    dong += ["Bác sĩ: Nhà mình có ai dị ứng thuốc gì không ạ?",
             f"Người nhà: Tôi thì dị ứng {thuoc}, còn cháu chưa thấy bị bao giờ."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo + "\n\n"
           "TIỀN SỬ DỊ ỨNG\n\nTrẻ chưa ghi nhận dị ứng thuốc.\n\n"
           f"TIỀN SỬ GIA ĐÌNH\n\nMẹ dị ứng {thuoc}.")
    return {"id": f"cd_chu_the_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "chu_the", "thuoc": thuoc, "chu_the_dung": "mẹ"}


# ─── _bay_chac_chan() — Sinh ca bẫy độ chắc chắn của phủ định ─────────────────────────
# Đáp án đúng ghi chưa ghi nhận, không ghi không có.
def _bay_chac_chan(rnd, i):
    dong, mo = _mo_dau(rnd)
    tc = rnd.choice(TRIEU_CHUNG)
    dong += [f"Bác sĩ: Cháu có bị {tc} bao giờ chưa ạ?",
             f"Người nhà: Chưa thấy cháu bị {tc} bao giờ ạ."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo + "\n\n"
           f"TIỀN SỬ BỆNH\n\nTrẻ chưa ghi nhận {tc}.")
    return {"id": f"cd_chac_chan_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "chac_chan", "trieu_chung": tc,
            "cum_dung": "chưa ghi nhận", "cum_sai": f"không {tc}"}


# ─── _bay_dinh_chinh() — Sinh ca bẫy tự sửa số ngày sốt ───────────────────────────────
# Người nhà nói n ngày rồi sửa thành m ngày; đáp án ghi m ngày.
def _bay_dinh_chinh(rnd, i):
    dong, mo = _mo_dau(rnd)
    m = rnd.randint(1, 4)
    n = m + rnd.randint(1, 3)
    dong += ["Bác sĩ: Cháu sốt mấy hôm rồi chị?",
             f"Người nhà: {n} ngày ạ… À không, hôm kia mới bắt đầu, vậy là {m} ngày."]
    out = ("LÝ DO KHÁM BỆNH\n\n" + f"Sốt {m} ngày.\n\n"
           "BỆNH SỬ HIỆN TẠI\n\n" + mo
           + f" Sốt {m} ngày. Người nhà nêu ban đầu là {n} ngày rồi tự đính chính.")
    return {"id": f"cd_dinh_chinh_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "dinh_chinh", "moc_cu": f"{n} ngày", "moc_moi": f"{m} ngày"}


# ─── _bay_dien_bien() — Sinh ca bẫy diễn biến: hôm qua có, hôm nay hết ────────────────
# Đáp án phải ghi cả hai mốc thời gian.
def _bay_dien_bien(rnd, i):
    dong, mo = _mo_dau(rnd)
    tc = rnd.choice(TRIEU_CHUNG)
    dong += [f"Bác sĩ: Cháu còn {tc} không chị?",
             f"Người nhà: Hôm qua cháu {tc}, hôm nay thì hết rồi ạ."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo
           + f" Hôm qua trẻ {tc}, hôm nay đã hết {tc}.")
    return {"id": f"cd_dien_bien_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "dien_bien", "moc_cu": "Hôm qua", "moc_moi": "hôm nay",
            "trieu_chung": tc}


# ─── _chon_khong_trung() — Chọn phần tử không là chuỗi con của nhau ───────────────────
# Tránh nhầm như ho với ho khan khi kiểm bằng chuỗi con.
def _chon_khong_trung(rnd, nguon, khac):
    """Chọn một phần tử không là chuỗi con của `khac` và ngược lại.

    Cần thiết vì "ho" là tiền tố của "ho khan": nếu điều kiện giả định là "ho"
    còn triệu chứng thật là "ho khan" thì không thể kiểm bằng chuỗi con được nữa.
    """
    ung_vien = [x for x in nguon if x not in khac and khac not in x]
    return rnd.choice(ung_vien)


# ─── _bay_gia_dinh() — Sinh ca bẫy câu điều kiện giả định ─────────────────────────────
# Đáp án không được ghi triệu chứng chỉ nêu trong câu nếu mai.
def _bay_gia_dinh(rnd, i):
    dong, mo = _mo_dau(rnd)
    tc_that = rnd.choice(TRIEU_CHUNG_PHU)
    tc = _chon_khong_trung(rnd, TRIEU_CHUNG, tc_that)
    # "Nếu mãi cháu VẪN {tc}" ngầm khẳng định trẻ đang bị {tc} — trong khi
    # triệu chứng thật là {tc_that}. Bỏ chữ "vẫn" để câu thuần túy giả định.
    dong += [f"Người nhà: Cháu đang {tc_that} ạ.",
             f"Người nhà: Nếu mai cháu {tc} thì tôi cho uống thêm ạ."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo + f" Trẻ {tc_that}.")
    return {"id": f"cd_gia_dinh_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "gia_dinh", "dieu_kien": tc, "trieu_chung_that": tc_that}


# ─── _bay_moi_bia() — Sinh ca bẫy bác sĩ hỏi mà bệnh nhân chưa trả lời ────────────────
# Triệu chứng bác sĩ hỏi suông không được vào bệnh án.
def _bay_moi_bia(rnd, i):
    dong, mo = _mo_dau(rnd)
    tc_that = rnd.choice(TRIEU_CHUNG_PHU)
    moi = _chon_khong_trung(rnd, TRIEU_CHUNG, tc_that)
    dong += [f"Người nhà: Cháu {tc_that} mấy hôm nay ạ.",
             f"Bác sĩ: Cháu có {moi} không?",
             "Bác sĩ: Thôi để tôi khám cho cháu đã."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo + f" Trẻ {tc_that}.")
    return {"id": f"cd_moi_bia_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "moi_bia", "moi_khong_duoc_tra_loi": moi,
            "trieu_chung_that": tc_that}


# ─── _bay_nghi_ngo() — Sinh ca bẫy nghi ngờ không thành chẩn đoán xác định ────────────
# Bản đúng giữ mức nghi ngờ của bác sĩ, không nâng thành chắc chắn.
def _bay_nghi_ngo(rnd, i):
    """Thách thức 3 — NGHI NGỜ không được thành CHẨN ĐOÁN XÁC ĐỊNH.

    Bác sĩ nói rõ là nghi, và nói rõ là CHƯA kết luận được vì còn chờ kết quả.
    Bản đúng phải giữ nguyên mức độ đó. Lỗi cần bắt: bệnh án ghi thành một chẩn
    đoán chắc chắn.

    VÌ SAO CẦN NHÓM NÀY RIÊNG (thêm 10/09/2026). Nhóm `gia_dinh` chỉ bắt câu
    ĐIỀU KIỆN ("nếu mai còn sốt thì..."). Đây là kiểu hỏng KHÁC: một nhận định
    có thật của bác sĩ bị NÂNG MỨC — từ "nghi" thành "là". Trước đó không nhóm
    nào trong bộ chẩn đoán bắt được nó, nên một nửa của thách thức 3 không có
    phép đo.

    Bẫy này còn một vế nữa: bệnh án KHÔNG được bỏ hẳn thông tin đi. Ghi "nghi
    viêm phổi, chờ X-quang" mới là đúng; im lặng không nhắc gì là BỎ SÓT, và
    đó là một cách khác để sai.
    """
    dong, mo = _mo_dau(rnd)
    benh, xn = rnd.choice(BENH_CHO_KET_QUA)
    tc = rnd.choice(TRIEU_CHUNG)
    dong += [f"Người nhà: Cháu {tc} mấy hôm nay ạ.",
             f"Bác sĩ: Tôi nghi {benh}, nhưng chưa kết luận được. "
             f"Phải có kết quả {xn} đã.",
             f"Bác sĩ: Chị cho cháu đi làm {xn} rồi quay lại nhé."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo + f" Trẻ {tc}.\n\n"
           "CHẨN ĐOÁN\n\n"
           f"Nghi {benh}, chưa kết luận, chờ kết quả {xn}.\n\n"
           "KẾ HOẠCH ĐIỀU TRỊ\n\n"
           f"Làm {xn}, hẹn khám lại khi có kết quả.")
    return {"id": f"cd_nghi_ngo_{i:03d}", "input": "\n".join(dong),
            "output": out, "bay": "nghi_ngo", "benh_nghi": benh,
            "xet_nghiem": xn, "trieu_chung_that": tc}


# ─── _bay_nhat_quan() — Sinh ca bẫy nhất quán giữa hai mục bệnh án ────────────────────
# Thuốc đã ngừng không được còn trong mục thuốc đang dùng.
def _bay_nhat_quan(rnd, i):
    """Thách thức 5 — tính nhất quán giữa HAI MỤC trong cùng một bệnh án.

    Hội thoại nói một thuốc ĐÃ NGƯNG. Bản đúng ghi nó ở mục tiền sử, và mục
    THUỐC ĐANG DÙNG không được chứa nó. Lỗi cần bắt: một mục ghi "đã ngưng",
    mục kia ghi "đang dùng" — mỗi câu đọc riêng đều đúng, chỉ sai khi đọc
    CẢ HAI.

    Đây là loại lỗi không phép đo nào trong dự án bắt được trước 09/09/2026:
    ROUGE đếm từ nên hai câu đều khớp; điểm quy gán chỉ xét chủ thể; sáu nhóm
    bẫy cũ đều chỉ xét MỘT câu một.
    """
    dong, mo = _mo_dau(rnd)
    thuoc = rnd.choice(THUOC_DA_NGUNG)
    tuan = rnd.randint(2, 8)
    tc = rnd.choice(TRIEU_CHUNG_PHU)
    dong += [f"Người nhà: Cháu {tc} mấy hôm nay ạ.",
             "Bác sĩ: Cháu có đang dùng thuốc gì không chị?",
             f"Người nhà: Trước có uống {thuoc}, nhưng ngừng {tuan} tuần rồi ạ."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo + f" Trẻ {tc}.\n\n"
           "TIỀN SỬ BỆNH\n\n"
           f"Trẻ từng dùng {thuoc}, đã ngừng {tuan} tuần.")
    return {"id": f"cd_nhat_quan_{i:03d}", "input": "\n".join(dong),
            "output": out,
            "bay": "nhat_quan", "thuoc_da_ngung": thuoc,
            "trieu_chung_that": tc}


# ─── _bay_sach() — Sinh ca sạch làm đối chứng, không có bẫy ───────────────────────────
# Hội thoại ngắn có triệu chứng và số ngày.
def _bay_sach(rnd, i):
    dong, mo = _mo_dau(rnd)
    tc = rnd.choice(TRIEU_CHUNG_PHU)
    so = rnd.randint(1, 5)
    dong += ["Bác sĩ: Hôm nay cháu làm sao ạ?",
             f"Người nhà: Cháu {tc} được {so} ngày rồi ạ."]
    out = ("LÝ DO KHÁM BỆNH\n\n" + f"{tc.capitalize()} {so} ngày.\n\n"
           "BỆNH SỬ HIỆN TẠI\n\n" + mo + f" Trẻ {tc} {so} ngày.")
    return {"id": f"cd_sach_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "sach"}


_DUNG = {
    "chu_the": _bay_chu_the, "chac_chan": _bay_chac_chan,
    "dinh_chinh": _bay_dinh_chinh, "dien_bien": _bay_dien_bien,
    "gia_dinh": _bay_gia_dinh, "moi_bia": _bay_moi_bia,
    "nghi_ngo": _bay_nghi_ngo,
    "nhat_quan": _bay_nhat_quan, "sach": _bay_sach,
}


# ═══ sinh_bo() — Sinh bộ chẩn đoán, mỗi tình huống bẫy n mẫu ══════════════════════════
# Cùng hạt giống cho cùng kết quả; mỗi cặp (tình huống, chỉ số) có bộ sinh riêng.
def sinh_bo(n_moi_bay, seed=42):
    """Sinh n_moi_bay mẫu cho MỖI tình huống. Cùng seed thì cùng kết quả."""
    ra = []
    for ten in BAY:
        for i in range(n_moi_bay):
            # Mỗi (tình huống, chỉ số) một bộ sinh riêng => ổn định khi đổi n
            rnd = random.Random(f"{seed}-{ten}-{i}")
            ra.append(_DUNG[ten](rnd, i))
    return ra


# ═══ main() — Sinh và ghi bộ chẩn đoán bằng dòng lệnh ═════════════════════════════════
# Có các tham số --n, --seed, --out; in số mẫu và số khuôn gốc.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60, help="so mau moi tinh huong")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    import json
    from src.he_thong import duong_dan as duong_dan

    bo = sinh_bo(a.n, a.seed)
    dp = a.out or (duong_dan.THU_MUC_DU_LIEU / "bo_chan_doan.jsonl")
    with open(dp, "w", encoding="utf-8") as f:
        for m in bo:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"{len(bo)} mau · {len(BAY)} tinh huong x {a.n} · {dp}")
    print(f"So KHUON goc: {len(MAU_CAU)} — day moi la don vi doc lap, khong phai {len(bo)}")


if __name__ == "__main__":
    main()
