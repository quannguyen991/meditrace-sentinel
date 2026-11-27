# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Chấm quy gán riêng từng tầng độ khó (bác sĩ, bệnh nhân, kể hộ, kể về mình), vì số
           gộp không thấy được tầng người nhà.
Vào → Ra : đầu ra các nhánh (--nhanh) hoặc tệp (--tep) + đáp án trong bộ dữ liệu → bảng điểm
           quy gán theo tầng và nhánh
Đọc từ   : cham_mot_ca() chấm quy gán một ca theo tầng; main() dựng bảng theo nhánh
Mục lục (các hàm/lớp chính):
  menh_de_dap_an()  Lấy mệnh đề đáp án có lượt kèm tầng và chủ thể
  cham_mot_ca()     Chấm quy gán của một ca theo từng tầng
  ty_le_tung_ca()   Tính tỉ lệ theo từng ca cho một tầng
  bang()            Dựng bảng markdown điểm quy gán theo tầng và nhánh
  main()            Chạy dòng lệnh chấm quy gán theo tầng độ khó
Gọi tới  : do_luong/khoang_tin_cay, do_luong/thuoc_do_quy_gan, bo_du_lieu/nap_du_lieu
Tên cũ   : do_tang_quy_gan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chấm quy gán RIÊNG TỪNG TẦNG độ khó, thay vì gộp thành một số.

VÌ SAO CẦN. `thuoc_do_quy_gan.diem` chấm F1 trên toàn bộ mệnh đề của một ca.
Đo được trên bộ dữ liệu: mệnh đề tầng 4 — người nhà kể về CHÍNH MÌNH, cho cả
hai đường tắt đều sai — chiếm 1,91% (bộ 3.000) đến 2,32% (bộ 5.000). Trong 60
ca đã dùng để so sánh các nhánh: 7 mệnh đề trên 514.

    ảnh hưởng tối đa trên thước đo gộp   1,36%
    bề rộng khoảng tin cậy đo được       4,16%

Nên thước đo gộp KHÔNG THỂ thay được cơ chế quy gán có tác dụng hay không. Nó
không nói "cơ chế vô dụng", nó không nói gì cả. Tệp này chấm riêng từng tầng
để câu hỏi đó có chỗ trả lời.

BỐN TẦNG, xếp theo độ khó THẬT:

    1 bac_si        lượt bác sĩ              chủ thể luôn là bệnh nhân
    2 benh_nhan     lượt bệnh nhân           chủ thể là chính người nói
    3 ke_ho         người nhà kể HỘ          "chủ thể = người nói" SAI
    4 ke_ve_minh    người nhà kể VỀ MÌNH     cả hai đường tắt đều SAI

Tầng 3 và tầng 4 đối nhau: ở tầng 3 phải gán cho BỆNH NHÂN dù người nói là
người nhà; ở tầng 4 phải gán cho NGƯỜI NHÀ dù phần lớn lượt khác đều về bệnh
nhân. Một hệ thống chỉ biết một chiều sẽ ăn một tầng và trượt tầng kia — nên
hai tầng này phải báo RIÊNG, không được gộp.

GỐC ĐỐI CHIẾU LÀ `dap_an` TRONG BỘ DỮ LIỆU, không phải văn bản tham chiếu.
Văn bản tham chiếu sinh ra TỪ `dap_an`, nên đối chiếu qua nó là qua một lần
biến đổi nữa — và lần biến đổi đó làm mất nhãn tầng.

    python -m src.do_luong.do_tang_quy_gan --tap viet_phat_trien --nhanh B C D
"""
import argparse
import io
import sys
from pathlib import Path

from src.do_luong import khoang_tin_cay as sai_so
from src.do_luong import thuoc_do_quy_gan as thuoc_do_quy_gan

# Hai giá trị chủ thể mà `thuoc_do_quy_gan.tach_menh_de` phân biệt được.
# `dap_an` ghi vai cụ thể ("mẹ", "bà ngoại", "chồng"...); gom hết về "người
# nhà" vì đó là độ phân giải mà bản nháp thực sự mang.
BENH_NHAN = "bệnh nhân"
NGUOI_NHA = "người nhà"


# ─── _chu_the_chuan() — Gom chủ thể về hai giá trị: bệnh nhân, người nhà ──────────────
def _chu_the_chuan(chu_the):
    return BENH_NHAN if chu_the == BENH_NHAN else NGUOI_NHA


# ═══ menh_de_dap_an() — Lấy mệnh đề đáp án có lượt kèm tầng và chủ thể ════════════════
# Mỗi phần tử gồm tầng, chủ thể chuẩn và một mệnh đề giả để so nội dung.
def menh_de_dap_an(ban_ghi_goc):
    """-> [(tang, chu_the_chuan, MenhDe giả)] cho mỗi mệnh đề CÓ lượt.

    `MenhDe` giả chỉ để gọi `cung_noi_dung` — nó cần trường `tu` và `chu_the`.
    """
    vai = sai_so.nguoi_noi_tung_luot(ban_ghi_goc)
    ra = []
    for m in ban_ghi_goc.get("dap_an") or []:
        # MỘT định nghĩa tầng, dùng chung với `sai_so.tang_menh_de` — xem
        # `sai_so.tang_cua` (người nói lượt CUỐI, điều dưỡng là nhân viên y tế).
        tang = sai_so.tang_cua(m, vai)
        if tang is None:
            continue
        ct = _chu_the_chuan(m.get("chu_the"))
        noi_dung = str(m.get("noi_dung") or "")
        gia = thuoc_do_quy_gan.MenhDe(
            chu_the=ct, tu=thuoc_do_quy_gan._tu_noi_dung(noi_dung),
            cau=noi_dung, muc=str(m.get("muc") or ""))
        if gia.tu:
            ra.append((tang, ct, gia))
    return ra


# ═══ cham_mot_ca() — Chấm quy gán của một ca theo từng tầng ═══════════════════════════
# Mỗi tầng đếm đúng, sai chủ thể và thiếu. Tách sai chủ thể khỏi thiếu vì là hai lỗi
# khác nhau.
def cham_mot_ca(du_doan, ban_ghi_goc):
    """-> {tang: {dung, sai_chu_the, thieu}}.

    `dung`          tìm được mệnh đề cùng nội dung VÀ cùng chủ thể
    `sai_chu_the`   tìm được cùng nội dung nhưng gán sai người  <- lỗi của dự án
    `thieu`         không tìm được nội dung đó trong bản nháp

    Tách `sai_chu_the` khỏi `thieu` là chủ ý: bỏ sót và gán sai người là hai
    lỗi khác nhau, và gộp lại thì không thấy được cái nào đang giảm.
    """
    pd = thuoc_do_quy_gan.tach_menh_de(du_doan or "")
    ra = {}
    for tang, ct, goc in menh_de_dap_an(ban_ghi_goc):
        o = ra.setdefault(tang, {"dung": 0, "sai_chu_the": 0, "thieu": 0})
        khop = [p for p in pd if thuoc_do_quy_gan.cung_noi_dung(p, goc)]
        if not khop:
            o["thieu"] += 1
        elif any(p.chu_the == ct for p in khop):
            o["dung"] += 1
        else:
            o["sai_chu_the"] += 1
    return ra


# Hai trục, và TRỘN CHUNG LẠI LÀ LỖI.
#
#   quy_gan   dung / (dung + sai_chu_the)        -- trong số nội dung ĐÃ ghi
#                                                   được, bao nhiêu phần gán
#                                                   đúng người
#   bao_phu   (dung + sai) / (dung + sai + thieu) -- bao nhiêu phần nội dung
#                                                   vào được bản nháp
#
# Ban đầu tệp này tính dung/(dung+sai+thieu) rồi gọi là "gán đúng". Con số đó
# tụt xuống khi hệ thống BỎ SÓT, không phải khi nó GÁN SAI NGƯỜI — nên tầng
# `bac_si` ra 56% trong khi lỗi quy gán ở tầng đó gần như không có. Hai loại
# lỗi khác nhau gộp lại thì không thấy được cái nào đang giảm.
CHE_DO = ("quy_gan", "bao_phu")


# ═══ ty_le_tung_ca() — Tính tỉ lệ theo từng ca cho một tầng ═══════════════════════════
# Hai chế độ: quy_gan (đúng trên phần đã ghi) và bao_phu. Bỏ ca không có mệnh đề tầng
# đó.
def ty_le_tung_ca(ket_qua_theo_id, goc_theo_id, tang, che_do="quy_gan"):
    """-> {id: tỷ lệ} cho MỘT tầng, chỉ tính ca CÓ mệnh đề tầng đó.

    Bỏ ca không có mệnh đề tầng đó thay vì cho điểm 1.0: cho điểm 1.0 làm
    loãng hết hiệu ứng — đây đúng là lỗi mà tệp này được viết ra để chặn,
    không được lặp lại ở mức trong tệp.
    """
    if che_do not in CHE_DO:
        raise SystemExit(f"che do phai la mot trong {CHE_DO}")
    ra = {}
    for ma, k in ket_qua_theo_id.items():
        if ma not in goc_theo_id:
            continue
        d = cham_mot_ca(k.get("du_doan", ""), goc_theo_id[ma]).get(tang)
        if not d:
            continue
        if che_do == "quy_gan":
            mau = d["dung"] + d["sai_chu_the"]
            tu = d["dung"]
        else:
            mau = d["dung"] + d["sai_chu_the"] + d["thieu"]
            tu = d["dung"] + d["sai_chu_the"]
        if mau:
            ra[ma] = tu / mau
    return ra


# ═══ bang() — Dựng bảng markdown điểm quy gán theo tầng và nhánh ══════════════════════
# Mỗi tầng một khối, mỗi nhánh một dòng, kèm khoảng tin cậy và cảnh báo số khuôn bệnh.
def bang(ket_qua_theo_nhanh, goc_theo_id, khuon=None, so_lan=2000):
    """Bảng: mỗi tầng một khối, mỗi nhánh một dòng."""
    d = ["# Chấm quy gán theo tầng độ khó", "",
         "Tầng 3 và tầng 4 **đối nhau**: tầng 3 phải gán cho bệnh nhân dù người",
         "nói là người nhà; tầng 4 phải gán cho người nhà dù phần lớn lượt khác",
         "đều về bệnh nhân. Một hệ thống chỉ biết một chiều sẽ ăn một tầng và",
         "trượt tầng kia, nên hai tầng này không được gộp.", ""]
    so_khuon = len(set(khuon.values())) if khuon else None
    canh = sai_so.canh_so_khuon(so_khuon)
    if canh:
        d += ["> " + canh.replace("{so_ca}", str(len(goc_theo_id))),
              ">",
              "> Cụ thể với số khuôn này, cận dưới của khoảng tin cậy tụt về 0%:",
              "> một lần lấy lại mẫu có thể rút đúng một khuôn ba lần. Khoảng đó",
              "> không hỏng — nó đang nói rằng nó không nói được gì.", ""]

    d += ["Hai trục, **không gộp**: *gán đúng* tính trong số nội dung đã ghi",
          "được (mẫu số không có phần bỏ sót), *bao phủ* tính phần nội dung vào",
          "được bản nháp. Trộn hai trục thì điểm tụt vì bỏ sót bị đọc thành lỗi",
          "quy gán.", ""]

    for tang in sai_so.TANG:
        dong = []
        for ten, kq in ket_qua_theo_nhanh.items():
            qg = ty_le_tung_ca(kq, goc_theo_id, tang, "quy_gan")
            bp = ty_le_tung_ca(kq, goc_theo_id, tang, "bao_phu")
            if not bp:
                continue
            kq_g = (sai_so.khoang(qg, {i: khuon[i] for i in qg} if khuon else None,
                                  so_lan=so_lan) if qg else None)
            kb = sai_so.khoang(bp, {i: khuon[i] for i in bp} if khuon else None,
                               so_lan=so_lan)
            dong.append((ten, kq_g, kb, len(qg), len(bp)))
        if not dong:
            continue
        d += [f"## Tầng `{tang}` — {dong[0][4]} ca có mệnh đề tầng này", "",
              "| Nhánh | Gán đúng | KTC 95% | Bao phủ | n ca chấm được quy gán |",
              "|---|---|---|---|---|"]
        for ten, kg, kb, n_qg, _ in dong:
            cot = (f"{sai_so._pt(kg['trung_binh'])} | "
                   f"[{sai_so._pt(kg['thap'])}; {sai_so._pt(kg['cao'])}]"
                   if kg else "— | —")
            d.append(f"| `{ten}` | {cot} | {sai_so._pt(kb['trung_binh'])} | "
                     f"{n_qg} |")
        d.append("")
    return "\n".join(d)


# ═══ main() — Chạy dòng lệnh chấm quy gán theo tầng độ khó ════════════════════════════
# Nạp kết quả các nhánh, đối chiếu tập gốc, in bảng và có thể ghi ra tệp.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--tap-goc", default=None)
    ap.add_argument("--nhanh", nargs="+", default=["B", "C", "D"])
    # Xem chú thích cùng tên ở `sai_so`: quy ước tên tệp đã sinh ra một lỗi
    # thật, nên phải gọi thẳng đường dẫn được.
    ap.add_argument("--tep", nargs="+", default=None, metavar="TEN=DUONG_DAN")
    ap.add_argument("--so-lan", type=int, default=2000)
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()
    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_tap_khoa(a.tap)

    nguon = ({k: Path(v) for k, v in (x.split("=", 1) for x in a.tep)}
             if a.tep else
             {n: sai_so.THU_MUC_DATA / f"ra_{n}_{a.tap}.jsonl" for n in a.nhanh})
    ket_qua_theo_nhanh, moi = {}, {}
    for n, tep in nguon.items():
        if not tep.exists():
            print(f"bo qua {n}: khong co {tep}")
            continue
        kq = {b["id"]: b for b in sai_so._doc(tep)}
        ket_qua_theo_nhanh[n] = kq
        moi.update(kq)
    if not ket_qua_theo_nhanh:
        raise SystemExit("khong nap duoc nhanh nao")

    tap_goc = (Path(a.tap_goc) if a.tap_goc
               else sai_so.THU_MUC_DATA / f"{a.tap}.jsonl")
    khuon = sai_so.doi_chieu_tap(moi, tap_goc)
    goc = {b["id"]: b for b in sai_so._doc(tap_goc) if b["id"] in moi}

    van = bang(ket_qua_theo_nhanh, goc, khuon, a.so_lan)
    print(van)
    if a.ra:
        Path(a.ra).write_text(van + "\n", encoding="utf-8")
        print(f"-> {a.ra}")


if __name__ == "__main__":
    main()
