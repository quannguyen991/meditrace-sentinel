# -*- coding: utf-8 -*-
"""Sinh bo kiem tra chan doan bang LUAT, khong bang mo hinh ngon ngu.

Vi sao co bo nay: 35 mau tap phat trien la co nho, va bon nhom loi khong phan
bo deu trong do — co the ca 35 mau khong co mau nao chua dinh chinh. Bo nay
giai quyet dung chuyen do: sinh CA hoi thoai LAN benh an dung bang cung mot
doan ma, nen dap an biet truoc chinh xac, khong can gan nhan tay.

    CHI DE DANH GIA. Tuyet doi khong dua vao huan luyen.
    Train tren mau cau thi mo hinh hoc thuoc mau cau, moi ket qua thanh vo nghia.

    SINH BANG MA CUA MINH, khong bang LLM. Xem Global Constraint 1.

Tam tinh huong. Nhom `sach` la BAT BUOC: khong co no thi khong phan biet duoc
"bat duoc bay" voi "canh giac qua muc, gan co moi thu".

Nhom `nhat_quan` them 09/09/2026, cho thach thuc 5. Truoc do KHONG phep do
nao cua du an bat duoc loi mau thuan giua hai muc: bay nhom cu deu chi xet
MOT cau mot, con ROUGE thi dem tu nen hai cau deu khop.

Canh bao ve suc manh thong ke: 420 bien the sinh tu vai khuon KHONG tuong duong
420 ca doc lap. So khuon goc moi la don vi doc lap.

    python -m src.sinh_bo_chan_doan --n 60 --seed 42
"""
import argparse
import io
import random
import sys

# Mau cau RIENG cho bo chan doan.
# PHAI roi han voi `tang_cuong.MAU_CAU` — trung mau cau la ro ri: kiem tra
# tren dung thu da day. Co test `test_mau_cau_roi_han_voi_bo_chan_doan`.
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
# Thuoc dung RIENG cho bay nhat quan. Tach khoi THUOC vi bay nhat quan hoi
# "thuoc nay co dang dung khong", con THUOC dung cho bay di ung — tron vao
# nhau thi mot mau co the vua la bay nay vua la bay kia, va khong con biet
# phep kiem dang bat cai gi.
THUOC_DA_NGUNG = ["metformin", "omeprazole", "salbutamol", "cetirizine",
                  "paracetamol"]
TRIEU_CHUNG = ["sốt", "ho", "nôn", "đau bụng", "tiêu chảy", "khó thở"]
TRIEU_CHUNG_PHU = ["ho khan", "chán ăn", "quấy khóc", "mệt mỏi"]
# Benh dung RIENG cho bay nghi_ngo. Phai la benh CAN XET NGHIEM moi ket luan
# duoc — neu chon mot benh chan doan bang mat thuong thi bay khong con nghia.
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


def _mo_dau(rnd):
    tuoi = rnd.choice(TUOI)
    return (
        [f"Bác sĩ: Chào chị, cháu năm nay mấy tuổi ạ?",
         f"Người nhà: Dạ cháu {tuoi} tuổi."],
        f"Trẻ {tuoi} tuổi.",
    )


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


def _chon_khong_trung(rnd, nguon, khac):
    """Chon mot phan tu khong la chuoi con cua `khac` va nguoc lai.

    Can thiet vi "ho" la tien to cua "ho khan": neu dieu kien gia dinh la "ho"
    con trieu chung that la "ho khan" thi khong the kiem bang chuoi con duoc nua.
    """
    ung_vien = [x for x in nguon if x not in khac and khac not in x]
    return rnd.choice(ung_vien)


def _bay_gia_dinh(rnd, i):
    dong, mo = _mo_dau(rnd)
    tc_that = rnd.choice(TRIEU_CHUNG_PHU)
    tc = _chon_khong_trung(rnd, TRIEU_CHUNG, tc_that)
    # "Neu mai chau VAN {tc}" ngam khang dinh tre dang bi {tc} — trong khi
    # trieu chung that la {tc_that}. Bo chu "van" de cau thuan tuy gia dinh.
    dong += [f"Người nhà: Cháu đang {tc_that} ạ.",
             f"Người nhà: Nếu mai cháu {tc} thì tôi cho uống thêm ạ."]
    out = ("BỆNH SỬ HIỆN TẠI\n\n" + mo + f" Trẻ {tc_that}.")
    return {"id": f"cd_gia_dinh_{i:03d}", "input": "\n".join(dong), "output": out,
            "bay": "gia_dinh", "dieu_kien": tc, "trieu_chung_that": tc_that}


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


def _bay_nghi_ngo(rnd, i):
    """Thach thuc 3 — NGHI NGO khong duoc thanh CHAN DOAN XAC DINH.

    Bac si noi ro la nghi, va noi ro la CHUA ket luan duoc vi con cho ket qua.
    Ban dung phai giu nguyen muc do do. Loi can bat: benh an ghi thanh mot chan
    doan chac chan.

    VI SAO CAN NHOM NAY RIENG (them 10/09/2026). Nhom `gia_dinh` chi bat cau
    DIEU KIEN ("neu mai con sot thi..."). Day la kieu hong KHAC: mot nhan dinh
    co that cua bac si bi NANG MUC — tu "nghi" thanh "la". Truoc do khong nhom
    nao trong bo chan doan bat duoc no, nen mot nua cua thach thuc 3 khong co
    phep do.

    Bay nay con mot ve nua: benh an KHONG duoc bo han thong tin di. Ghi "nghi
    viem phoi, cho X-quang" moi la dung; im lang khong nhac gi la BO SOT, va
    do la mot cach khac de sai.
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


def _bay_nhat_quan(rnd, i):
    """Thach thuc 5 — tinh nhat quan giua HAI MUC trong cung mot benh an.

    Hoi thoai noi mot thuoc DA NGUNG. Ban dung ghi no o muc tien su, va muc
    THUOC DANG DUNG khong duoc chua no. Loi can bat: mot muc ghi "da ngung",
    muc kia ghi "dang dung" — moi cau doc rieng deu dung, chi sai khi doc
    CA HAI.

    Day la loai loi khong phep do nao trong du an bat duoc truoc 09/09/2026:
    ROUGE dem tu nen hai cau deu khop; diem quy gan chi xet chu the; sau nhom
    bay cu deu chi xet MOT cau mot.
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


def sinh_bo(n_moi_bay, seed=42):
    """Sinh n_moi_bay mau cho MOI tinh huong. Cung seed thi cung ket qua."""
    ra = []
    for ten in BAY:
        for i in range(n_moi_bay):
            # Moi (tinh huong, chi so) mot bo sinh rieng => on dinh khi doi n
            rnd = random.Random(f"{seed}-{ten}-{i}")
            ra.append(_DUNG[ten](rnd, i))
    return ra


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60, help="so mau moi tinh huong")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    import json
    from src import duong_dan

    bo = sinh_bo(a.n, a.seed)
    dp = a.out or (duong_dan.THU_MUC_DU_LIEU / "bo_chan_doan.jsonl")
    with open(dp, "w", encoding="utf-8") as f:
        for m in bo:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"{len(bo)} mau · {len(BAY)} tinh huong x {a.n} · {dp}")
    print(f"So KHUON goc: {len(MAU_CAU)} — day moi la don vi doc lap, khong phai {len(bo)}")


if __name__ == "__main__":
    main()
