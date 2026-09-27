# -*- coding: utf-8 -*-
"""Duong danh doi loi–bo sot, quet theo nguong rui ro quy gan.

Ke hoach yeu cau dieu nay o Cua 4 — *"chua co can cu chon nguong thi trinh bay
duong danh doi loi–bo sot thay vi ket luan mot chieu"* — nhung chua bao gio
dung, vi nam nhanh deu la diem co dinh, khong co nut nao de van.

`rui_ro_quy_gan` la nut do. Nguong cang thap thi cang nhieu phat bieu bi day
xuong muc CAN XAC NHAN, nen than bai cang it loi gan nham — nhung cung cang
bo sot.

CHAM TREN THAN BAI, KHONG CHAM TREN CA BAN. Do la diem mau chot: thu can do la
*"nhung gi con lai trong phan bac si doc nhu su that"*. Neu cham ca muc CAN XAC
NHAN thi day mot phat bieu xuong do khong lam thay doi gi, va ca duong danh doi
thanh mot duong thang.

    python -m src.duong_danh_doi --tap phat_trien
"""
import argparse
import io
import json
import sys

from src import (cap_nhat, du_lieu, duong_dan, phat_bieu, rui_ro_quy_gan as rr,
                 sinh_benh_an, thuc_the, thuoc_do_quy_gan as tdq)

NGUONG = [0.0, 0.25, 0.5, 0.75, 1.0, 1.01]


def _mot_nguong(ds_trich, mau_theo_id, nguong, ngau_nhien_seed=None,
                ty_le_ngau_nhien=None):
    """`ngau_nhien_seed` khac None: bo qua diem rui ro, day xuong ngau nhien
    dung `ty_le_ngau_nhien` — day la nhom doi chung."""
    tong = {"f1_quy_gan": 0.0, "do_bao_phu": 0.0, "bo_sot": 0.0,
            "so_sai_chu_the": 0.0, "so_menh_de_du_doan": 0.0}
    day_xuong = 0
    tong_pb = 0
    n = 0

    for d in ds_trich:
        m = mau_theo_id.get(d["id"])
        if m is None:
            continue
        cac_luot = thuc_the.tach_luot(m["input"])
        ngu_canh = rr.NguCanh.tu_hoi_thoai(cac_luot)
        nguoi_noi = {so: vai for so, vai, _ in cac_luot if vai}

        tt = thuc_the.lien_ket(m["input"])
        bang = phat_bieu.bang_ten_tu_thuc_the(tt)
        ten_chu_the = {t.id: t.ten_chuan for t in tt
                       if t.loai == "người" and t.id != 0}

        ps, _ = phat_bieu.tu_json(d.get("phat_bieu") or [],
                                  nguoi_noi_theo_luot=nguoi_noi, id_theo_ten=bang)
        ps = cap_nhat.ap_luat(ps)
        tong_pb += len(ps)

        truoc = sum(1 for p in ps if p.trang_thai != "còn hiệu lực")
        if ngau_nhien_seed is None:
            ps = rr.sang_loc(ps, nguong, ngu_canh)
        else:
            ps = rr.sang_loc_ngau_nhien(ps, ty_le_ngau_nhien,
                                        ngau_nhien_seed + n)
        day_xuong += sum(1 for p in ps if p.trang_thai != "còn hiệu lực") - truoc

        van, _ = sinh_benh_an.sinh(ps, ten_chu_the=ten_chu_the)
        than, _ = sinh_benh_an.tach_muc_phu(van)

        diem = tdq.diem(than, m.get("output") or "")
        for k in tong:
            tong[k] += diem[k]
        n += 1

    if not n:
        return {}
    ra = {k: round(v / n, 4) for k, v in tong.items()}
    ra["nguong"] = nguong
    ra["so_day_xuong"] = day_xuong
    ra["ty_le_day_xuong"] = round(day_xuong / tong_pb, 4) if tong_pb else 0.0
    return ra


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--trich", default="data/trich_phat_trien_3072.jsonl")
    a = ap.parse_args()
    du_lieu.chan_tap_khoa(a.tap)
    du_lieu.chan_tap_ngoai(a.tap)

    ds = [json.loads(l) for l in open(a.trich, encoding="utf-8") if l.strip()]
    mau = {m["id"]: m for m in du_lieu.nap_mau(
        duong_dan.THU_MUC_DU_LIEU / f"{a.tap}.jsonl")}

    bang = []
    for nguong in NGUONG:
        kq = _mot_nguong(ds, mau, nguong)
        if not kq:
            continue
        # Doi chung: day xuong DUNG cung ty le nhung chon ngau nhien, lay trung
        # binh ba lan gieo. Khong co ve nay thi bang chi chung minh duoc "viet
        # it di thi sai it di".
        ty_le = kq["ty_le_day_xuong"]
        nn = [_mot_nguong(ds, mau, nguong, ngau_nhien_seed=s * 1000,
                          ty_le_ngau_nhien=ty_le) for s in (1, 2, 3)]
        kq["ngau_nhien_sai_chu_the"] = round(
            sum(x["so_sai_chu_the"] for x in nn) / len(nn), 4)
        kq["ngau_nhien_bo_sot"] = round(sum(x["bo_sot"] for x in nn) / len(nn), 4)
        bang.append(kq)
        print(f"  ngưỡng {nguong:4.2f}  đẩy xuống {ty_le:6.1%}  "
              f"sai chủ thể {kq['so_sai_chu_the']:.4f} "
              f"(ngẫu nhiên {kq['ngau_nhien_sai_chu_the']:.4f})  "
              f"bỏ sót {kq['bo_sot']:.4f} "
              f"(ngẫu nhiên {kq['ngau_nhien_bo_sot']:.4f})")

    dp = duong_dan.THU_MUC_KET_QUA / f"duong-danh-doi-{a.tap}.json"
    dp.write_text(json.dumps(bang, ensure_ascii=False, indent=2), encoding="utf-8")
    dp_md = duong_dan.THU_MUC_KET_QUA / f"duong-danh-doi-{a.tap}.md"
    dp_md.write_text(_bao_cao(bang, a.tap), encoding="utf-8")
    print(f"\nda ghi {dp}\nda ghi {dp_md}")


def _bao_cao(bang, tap):
    dong = "\n".join(
        f"| {b['nguong']:.2f} | {b['ty_le_day_xuong']:.1%} | {b['so_sai_chu_the']:.4f} | "
        f"{b['ngau_nhien_sai_chu_the']:.4f} | {b['bo_sot']:.4f} | "
        f"{b['ngau_nhien_bo_sot']:.4f} | {b['f1_quy_gan']:.4f} |"
        for b in bang)

    # Diem rui ro co hon chon bua khong: o cung ty le day xuong, no phai de lai
    # IT loi gan nham hon. Neu khong hon thi ca tang nay chi la "viet it di".
    co_ich = [b for b in bang if 0 < b["ty_le_day_xuong"] < 1
              and b["so_sai_chu_the"] < b["ngau_nhien_sai_chu_the"]]
    thua = [b for b in bang if 0 < b["ty_le_day_xuong"] < 1
            and b["so_sai_chu_the"] > b["ngau_nhien_sai_chu_the"]]
    # Thang o mot nguong va thua o hai nguong KHONG phai bang chung. Ban dau
    # phep phan xu chi kiem `if not co_ich`, nen voi ket qua 1 thang / 2 thua no
    # van in ra "bon dau hieu co mang thong tin" — mot ket luan nguoc han voi so
    # lieu ngay ben tren no. Phai thang nhieu hon thua VA thang o da so nguong.
    tong_nguong = len(co_ich) + len(thua)
    thuyet_phuc = tong_nguong > 0 and len(co_ich) > len(thua) and len(co_ich) * 2 > tong_nguong
    phan_xu = (
        f"Điểm rủi ro hơn chọn bừa ở **{len(co_ich)}/{tong_nguong}** ngưỡng. "
        + ("Cùng một công sàng lọc thì nó bắt được nhiều lỗi hơn chọn bừa — "
           "bốn dấu hiệu có mang thông tin."
           if thuyet_phuc else
           "**Chưa chứng minh được bốn dấu hiệu mang thông tin.** Ở tỷ lệ đẩy "
           "xuống như nhau, nó ngang hoặc thua chọn bừa, và bỏ sót lại cao hơn. "
           "Nên bảng này hiện chỉ nói được một điều ai cũng biết: *đẩy xuống "
           "nhiều thì thân bài sai ít* — điều đúng với cả cách chọn bừa.\n\n"
           "Đây là kết quả âm của chính phần vừa dựng, và nó là lý do nhóm đối "
           "chứng phải có. Không có cột ngẫu nhiên thì đường cong bên trên trông "
           "như một thắng lợi."))

    goc = next((b for b in bang if b["nguong"] > 1), None)

    # Chon "diem tot nhat" PHAI loc qua dieu kien cong bang truoc, khong duoc
    # lay thang diem it loi nhat.
    #
    # Ban dau lay `min(so_sai_chu_the)` va no chon ngay nguong 0,00 — noi 100%
    # phat bieu bi day xuong, than bai gan nhu trong, loi gan nham bang 0 va bo
    # sot bang 1,0. Bao cao khi do viet "giam 100% loi". Do dung la cai bay ma
    # ke hoach da ghi la bay lon nhat cua ca du an: **giam loi bang cach viet
    # it di**. Mot phep chon tu no roi vao bay do thi con nguy hiem hon khong
    # co phep chon nao.
    #
    # Dieu kien loc lay tu chinh Cua 4: bo sot khong duoc tang qua 20% tuong doi.
    ung_vien = []
    if goc and goc["bo_sot"]:
        for b in bang:
            if not (0 < b["ty_le_day_xuong"] < 1):
                continue
            if (b["bo_sot"] - goc["bo_sot"]) / goc["bo_sot"] <= 0.20:
                ung_vien.append(b)
    tot = min(ung_vien, key=lambda b: b["so_sai_chu_the"], default=None)

    if goc and tot and goc["so_sai_chu_the"]:
        giam = (goc["so_sai_chu_the"] - tot["so_sai_chu_the"]) / goc["so_sai_chu_the"]
        them = (tot["bo_sot"] - goc["bo_sot"]) / goc["bo_sot"]
        nhan_xet = (
            f"Trong số các ngưỡng **thoả điều kiện công bằng của Cửa 4** (bỏ sót không "
            f"tăng quá 20% tương đối), ngưỡng tốt nhất là **{tot['nguong']:.2f}**: lỗi "
            f"gán nhầm giảm **{giam:.1%}** ({goc['so_sai_chu_the']:.4f} → "
            f"{tot['so_sai_chu_the']:.4f}), bỏ sót tăng **{them:+.1%}**, và "
            f"{tot['ty_le_day_xuong']:.1%} số phát biểu bị đẩy xuống mục cần xác nhận.\n\n"
            f"Nhưng ở đúng ngưỡng đó, chọn bừa cùng tỷ lệ để lại "
            f"**{tot['ngau_nhien_sai_chu_the']:.4f}** lỗi — "
            + ("**ít hơn**, tức điểm rủi ro không đóng góp gì."
               if tot["ngau_nhien_sai_chu_the"] <= tot["so_sai_chu_the"]
               else "nhiều hơn, tức điểm rủi ro có đóng góp."))
    elif goc:
        nhan_xet = (
            "**Không ngưỡng nào thoả điều kiện công bằng của Cửa 4.** Mọi mức sàng lọc "
            "đủ để giảm lỗi đều làm bỏ sót tăng quá 20% tương đối.\n\n"
            "Nói thẳng ra: trên bộ dữ liệu này, cách đẩy phát biểu xuống mục cần xác "
            "nhận **chưa mua được độ đúng bằng cái giá chấp nhận được**. Đó là kết quả "
            "phải báo cáo, không phải chỗ để hạ ngưỡng cho vừa."
        )
    else:
        nhan_xet = "Chưa đủ dữ liệu để chọn ngưỡng."

    return f"""# Đường đánh đổi lỗi–bỏ sót — tập `{tap}`

Sinh tự động bằng `python -m src.duong_danh_doi`. Đừng sửa tay.

## Vì sao là một ĐƯỜNG chứ không phải một điểm

Kế hoạch yêu cầu điều này ngay ở Cửa 4 — *"chưa có căn cứ chọn ngưỡng thì trình
bày đường đánh đổi lỗi–bỏ sót thay vì kết luận một chiều"* — nhưng chưa bao giờ
dựng được, vì năm nhánh đều là điểm cố định, không có nút nào để vặn.

`src/rui_ro_quy_gan.py` là nút đó: mỗi phát biểu được chấm theo bốn dấu hiệu
quan sát được, và phát biểu vượt ngưỡng bị **đẩy xuống mục CẦN XÁC NHẬN** thay
vì viết thẳng vào thân bài như một sự thật.

Đổi cách đặt vấn đề: bác sĩ vẫn phải ký bản cuối, nên thứ họ thật sự cần không
phải một bản hoàn hảo mà là một bản **kèm danh sách chỗ phải soát**.

## Bảng

Chấm **chỉ trên thân bài**, không tính mục CẦN XÁC NHẬN — vì thứ cần đo là
những gì còn lại trong phần bác sĩ đọc như sự thật. Chấm cả bản thì đẩy một
phát biểu xuống mục phụ không đổi gì, và đường này thành một đường thẳng.

| ngưỡng | % bị đẩy xuống | sai chủ thể | *ngẫu nhiên* | bỏ sót | *ngẫu nhiên* | f1 quy gán |
|---|---|---|---|---|---|---|
{dong}

Ngưỡng `1.01` là **mốc đối chứng: không sàng lọc gì**.

## Nhóm đối chứng ngẫu nhiên — cột quan trọng nhất

Đẩy 60% phát biểu xuống mục cần xác nhận thì lỗi gán nhầm còn lại tất nhiên
giảm, **kể cả khi chọn bừa**. Nên mỗi ngưỡng đều có một phép chạy đối chứng:
đẩy xuống **đúng cùng tỷ lệ** nhưng chọn ngẫu nhiên, lấy trung bình ba lần gieo.

Điểm rủi ro chỉ có giá trị nếu ở cùng tỷ lệ đẩy xuống, nó để lại **ít** lỗi gán
nhầm hơn cột ngẫu nhiên. Không có cột này thì bảng chỉ chứng minh được một điều
ai cũng biết: viết ít đi thì sai ít đi.

{phan_xu}

## Đọc bảng

{nhan_xet}

## Giới hạn, nói thẳng

1. **Bốn dấu hiệu có trọng số đều nhau**, vì chưa có dữ liệu gán nhãn tay để
   hiệu chuẩn. Đặt trọng số bằng tay rồi bảo "dấu hiệu này quan trọng hơn" là
   bịa một con số không đo được. Hiệu chuẩn lại sau Task 9 và Task 13 — và lúc
   đó phải **đo xem hiệu chuẩn có thật sự tốt hơn đều nhau không**, chứ không
   mặc định là có.
2. **35 hội thoại.** Đường vẽ được nhưng mỗi điểm đều rộng.
3. Bỏ sót đo bằng cách đối chiếu với **bản tham chiếu**, nên kế thừa mọi thiếu
   sót của bản tham chiếu.
4. Đẩy xuống mục cần xác nhận **không phải là sửa lỗi**. Nó chuyển việc sang cho
   bác sĩ. Muốn biết cách đó có đỡ được thật không thì phải đo thời gian bác sĩ
   soát — mà việc đó kế hoạch đã chốt là **không làm trước 15/11** vì cỡ mẫu quá
   nhỏ. Đừng ước lượng nó.
"""


if __name__ == "__main__":
    main()
