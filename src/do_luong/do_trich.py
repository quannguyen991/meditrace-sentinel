# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo trực tiếp bước rút mệnh đề: tìm thấy bao nhiêu mệnh đề đáp án, gán đúng người
           bao nhiêu, riêng mệnh đề ngoài bệnh nhân.
Vào → Ra : tệp trích (--tep) + đáp án (--dap-an) → bảng tìm thấy, đúng chủ thể, đúng căn cứ,
           ngoài bệnh nhân
Đọc từ   : ghep() ghép đáp án với bản trích theo độ giống; cham() tính ba số của bước rút
Mục lục (các hàm/lớp chính):
  do_giong()     Tính độ giống hai câu bằng F1 trên tập từ
  ghep()         Ghép mệnh đề đáp án với bản trích theo độ giống
  cham_can_cu()  Chấm việc dẫn đúng lượt nói làm căn cứ
  cham()         Chấm bản trích: tìm thấy, đúng chủ thể, căn cứ
  in_bang()      In bảng kết quả chấm trích ra màn hình
  main()         Chạy dòng lệnh chấm các tệp trích với đáp án
Gọi tới  : bo_du_lieu/du_lieu_huan_luyen_trich, he_thong/duong_dan
Dùng bởi : do_luong/cham_he_thong, do_luong/do_bo_sot, bo_du_lieu/loc_nhan_may
Tên cũ   : do_trich.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo CHẤT LƯỢNG KHÂU TRÍCH trực tiếp, đối chiếu với đáp án cấu trúc.

VÌ SAO CẦN RIÊNG TỆP NÀY. Các phép đo đang có đều đo SẢN PHẨM CUỐI (bệnh án),
nên chất lượng khâu trích bị trộn với chất lượng khâu sinh:

    do_bo_chan_doan   chấm theo BẪY của từng tình huống, không chấm từng mệnh đề
    do_van_xuoi       chấm bản bệnh án, không chấm bảng phát biểu
    thuoc_do_quy_gan  đối chiếu bệnh án với bệnh án, nhạy với cách đóng gói câu

Bộ `hoi_thoai_viet.jsonl` có đáp án ở mức MỆNH ĐỀ, nên đo thẳng được:
mô hình trích ra bao nhiêu mệnh đề đúng, và trong số đó bao nhiêu phần gán
đúng người.

BA CON SỐ, không gộp làm một:

    tim_thay      bao nhiêu mệnh đề trong đáp án được trích ra (nhớ lại)
    dung_chu_the  trong số mệnh đề tìm thấy, bao nhiêu phần gán ĐÚNG người
    khac_bn       ba con số trên, tính RIÊNG cho các mệnh đề KHÔNG thuộc
                  bệnh nhân — chỉ 2,8% tổng số nhưng là toàn bộ phần đo
                  quy gán. Gộp chung thì 97% mệnh đề dễ gán sẽ che mất nó.

CÁCH GHÉP MỆNH ĐỀ. Đáp án và bản trích không bao giờ trùng từng chữ, nên
ghép theo độ chồng lấp từ (F1 trên tập từ), ngưỡng 0,6. Ghép tham lam theo
điểm giảm dần, mỗi bên dùng một lần.

    python -m src.do_luong.do_trich --tep trich_giu_lai_hl.jsonl --dap-an trich_giu_lai
"""
import io
import json
import re
import sys

NGUONG_GHEP = 0.6


# ─── _tu() — Tách chuỗi thành các từ chữ thường ───────────────────────────────────────
def _tu(s):
    return [t for t in re.split(r"[^\wÀ-ỹ]+", str(s or "").lower()) if t]


# ═══ do_giong() — Tính độ giống hai câu bằng F1 trên tập từ ═══════════════════════════
# Không dùng khớp nguyên văn vì hai bên hiếm khi trùng từng chữ.
def do_giong(a, b):
    """F1 trên tập từ. Không dùng khớp nguyên văn vì hai bên không bao giờ
    trùng từng chữ."""
    ta, tb = set(_tu(a)), set(_tu(b))
    if not ta or not tb:
        return 0.0
    chung = len(ta & tb)
    if not chung:
        return 0.0
    p, r = chung / len(tb), chung / len(ta)
    return 2 * p * r / (p + r)


# ═══ ghep() — Ghép mệnh đề đáp án với bản trích theo độ giống ═════════════════════════
# Ghép tham lam theo điểm giảm dần, mỗi bên dùng một lần. Trả cặp ghép, đáp án thiếu,
# bản trích thừa.
def ghep(dap_an, trich, nguong=NGUONG_GHEP):
    """-> (cap_da_ghep, dap_an_khong_tim_thay, trich_thua).

    Ghép THAM LAM theo điểm giảm dần, mỗi bên dùng một lần. Không ghép một
    mệnh đề đáp án với nhiều bản trích: làm thế thì một bản trích đúng sẽ
    che được nhiều bản sai.
    """
    diem = []
    for i, d in enumerate(dap_an):
        for j, t in enumerate(trich):
            s = do_giong(d.get("noi_dung"), t.get("noi_dung"))
            if s >= nguong:
                diem.append((s, i, j))
    diem.sort(reverse=True)
    da_d, da_t, cap = set(), set(), []
    for s, i, j in diem:
        if i in da_d or j in da_t:
            continue
        da_d.add(i)
        da_t.add(j)
        cap.append((dap_an[i], trich[j], s))
    thieu = [d for i, d in enumerate(dap_an) if i not in da_d]
    thua = [t for j, t in enumerate(trich) if j not in da_t]
    return cap, thieu, thua


# Cách gọi bệnh nhân trong đáp án và trong bản trích không nhất thiết trùng
# chữ. Coi là CÙNG một người nếu cả hai đều nằm trong rổ này.
RO_BENH_NHAN = {"bệnh nhân", "trẻ", "bé", "cháu", "con", "em bé", "bệnh nhi",
                "trẻ nhỏ", "bn"}


# ═══ cung_nguoi() — Kiểm tra hai cách gọi có cùng một người không ═════════════════════
# Bằng nhau hoặc cùng nằm trong rổ cách gọi bệnh nhân thì coi là cùng người.
def cung_nguoi(a, b):
    a, b = str(a or "").strip().lower(), str(b or "").strip().lower()
    if a == b:
        return True
    return a in RO_BENH_NHAN and b in RO_BENH_NHAN


# ─── _luot() — Lấy tập số lượt của một mệnh đề ────────────────────────────────────────
# Chấp nhận cả hai tên khoá: luot ở đáp án và luot_thoai ở bản trích.
def _luot(m, *khoa):
    """Tập số lượt của một mệnh đề. Đáp án dùng khoá `luot`, bản trích dùng
    `luot_thoai` — nên phải nhận cả hai tên."""
    for k in khoa:
        v = m.get(k)
        if v:
            return {int(x) for x in v if isinstance(x, (int, float))}
    return set()


# ═══ cham_can_cu() — Chấm việc dẫn đúng lượt nói làm căn cứ ═══════════════════════════
# Đếm lượt dẫn đúng, sót, thừa theo từng mệnh đề, tách khỏi việc gán đúng người.
def cham_can_cu(cap):
    """Đo nửa THỨ HAI của thách thức 4: có DẪN ĐÚNG lượt thoại nguồn không.

    VÌ SAO TÁCH RIÊNG (thêm 10/09/2026). Thách thức 4 gọi là "liên kết chủ thể
    và căn cứ bằng chứng", và nó gồm HAI việc:

        gán đúng người   thông tin này thuộc về ai
        dẫn đúng nguồn   thông tin này dựa vào câu nào

    Trước đó chỉ đo được việc đầu. Một hệ thống có thể gán ĐÚNG người mà DẪN
    SAI lượt thoại, và không phép đo nào của dự án bắt được — trong khi truy
    vết bằng chứng là chính điều dự án đặt tên.

    Đếm theo TỪNG MỆNH ĐỀ rồi lấy trung bình, không gộp tất cả lượt lại:
    một mệnh đề dẫn đúng 2/2 lượt và một mệnh đề dẫn sai cả 2/2 phải ra 50%,
    không phải một tỷ lệ gộp làm mờ mất cả hai.
    """
    du = sot = thua = 0
    khop_hoan_toan = 0
    xet = 0
    for d, t, _s in cap:
        that = _luot(d, "luot", "luot_thoai")
        doan = _luot(t, "luot_thoai", "luot")
        if not that:
            continue                  # đáp án không có lượt thì không đo được
        xet += 1
        du += len(that & doan)
        sot += len(that - doan)
        thua += len(doan - that)
        khop_hoan_toan += (that == doan)
    return {
        "so_menh_de_xet": xet,
        "luot_dung": du,
        "luot_sot": sot,
        "luot_thua": thua,
        "do_phu": du / max(1, du + sot),
        "do_chuan": du / max(1, du + thua),
        "khop_hoan_toan": khop_hoan_toan,
        "ty_le_khop_hoan_toan": khop_hoan_toan / max(1, xet),
    }


# ═══ cham() — Chấm bản trích: tìm thấy, đúng chủ thể, căn cứ ══════════════════════════
# Có thêm số riêng cho mệnh đề không thuộc bệnh nhân; trả cả danh sách lỗi.
def cham(danh_sach):
    """danh_sach: [(dap_an_menh_de_list, trich_menh_de_list)] cho từng ca."""
    tong_da = tong_tim = tong_dung = 0
    kb_da = kb_tim = kb_dung = 0
    tong_thua = 0
    loi = []
    moi_cap = []
    for dap_an, trich in danh_sach:
        cap, thieu, thua = ghep(dap_an, trich)
        moi_cap.extend(cap)
        tong_da += len(dap_an)
        tong_tim += len(cap)
        tong_thua += len(thua)
        kb_da += sum(1 for d in dap_an if d.get("chu_the") not in RO_BENH_NHAN)
        for d, t, _s in cap:
            khac_bn = d.get("chu_the") not in RO_BENH_NHAN
            dung = cung_nguoi(d.get("chu_the"), t.get("chu_the"))
            tong_dung += dung
            if khac_bn:
                kb_tim += 1
                kb_dung += dung
            if not dung:
                loi.append({"noi_dung": d.get("noi_dung"),
                            "dap_an": d.get("chu_the"),
                            "trich": t.get("chu_the"),
                            "khac_benh_nhan": khac_bn})
    return {
        "can_cu": cham_can_cu(moi_cap),
        "menh_de_dap_an": tong_da,
        "tim_thay": tong_tim,
        "ty_le_tim_thay": tong_tim / max(1, tong_da),
        "dung_chu_the": tong_dung,
        "ty_le_dung_chu_the": tong_dung / max(1, tong_tim),
        "trich_thua": tong_thua,
        "khac_bn_dap_an": kb_da,
        "khac_bn_tim_thay": kb_tim,
        "khac_bn_ty_le_tim_thay": kb_tim / max(1, kb_da),
        "khac_bn_dung": kb_dung,
        "khac_bn_ty_le_dung": kb_dung / max(1, kb_tim),
        "loi": loi,
    }


# ═══ in_bang() — In bảng kết quả chấm trích ra màn hình ═══════════════════════════════
def in_bang(k, ten=""):
    print("")
    print(f"{ten}")
    print(f"  Menh de trong dap an        {k['menh_de_dap_an']:6}")
    print(f"  Trich ra va ghep duoc       {k['tim_thay']:6}"
          f"   ({100 * k['ty_le_tim_thay']:.1f}%)")
    print(f"  Trong so do, gan DUNG nguoi {k['dung_chu_the']:6}"
          f"   ({100 * k['ty_le_dung_chu_the']:.1f}%)")
    print(f"  Ban trich thua (khong ghep) {k['trich_thua']:6}")
    print(f"  --- rieng menh de KHONG thuoc benh nhan ---")
    print(f"  Trong dap an                {k['khac_bn_dap_an']:6}")
    print(f"  Ghep duoc                   {k['khac_bn_tim_thay']:6}"
          f"   ({100 * k['khac_bn_ty_le_tim_thay']:.1f}%)")
    print(f"  Gan DUNG nguoi              {k['khac_bn_dung']:6}"
          f"   ({100 * k['khac_bn_ty_le_dung']:.1f}%)")
    cc = k.get("can_cu")
    if cc:
        print(f"  --- nua thu hai cua thach thuc 4: DAN DUNG NGUON ---")
        print(f"  Menh de do duoc             {cc['so_menh_de_xet']:6}")
        print(f"  Luot dan dung               {cc['luot_dung']:6}")
        print(f"  Luot bo sot                 {cc['luot_sot']:6}")
        print(f"  Luot dan thua               {cc['luot_thua']:6}")
        print(f"  Do phu / do chuan           "
              f"{100 * cc['do_phu']:.1f}% / {100 * cc['do_chuan']:.1f}%")
        print(f"  Dan DUNG HET, khong thua    {cc['khop_hoan_toan']:6}"
              f"   ({100 * cc['ty_le_khop_hoan_toan']:.1f}%)")


# ═══ main() — Chạy dòng lệnh chấm các tệp trích với đáp án ════════════════════════════
# Bỏ bản lặp lý do khám khỏi đáp án trước khi chấm, rồi ghi JSON kết quả mỗi tệp.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", nargs="+", required=True,
                    help="tep trich_*.jsonl trong data/")
    ap.add_argument("--dap-an", default="hoi_thoai_viet",
                    help="ten tep nguon chua dap an (khong duoi)")
    a = ap.parse_args()

    from src.he_thong import duong_dan as duong_dan
    d = duong_dan.THU_MUC_DU_LIEU

    # Bỏ bản sao lý do khám khỏi đáp án: từ 11/09/2026 nhãn huấn luyện không còn
    # chúng (`du_lieu_trich.ban_lap_ly_do_kham`), giữ lại thì mỗi ca mất oan một
    # mệnh đề "không tìm thấy". Số đo trước ngày đó tính CẢ bản sao ở hai phía.
    from src.bo_du_lieu.du_lieu_huan_luyen_trich import ban_lap_ly_do_kham
    goc = {}
    for x in open(d / f"{a.dap_an}.jsonl", encoding="utf-8"):
        if x.strip():
            k = json.loads(x)
            da = k.get("dap_an") or []
            lap = ban_lap_ly_do_kham(da)
            goc[k["id"]] = [m for i, m in enumerate(da) if i not in lap]

    for t in a.tep:
        dp = d / t
        if not dp.exists():
            print(f"(chua co {t})")
            continue
        cap = []
        for x in open(dp, encoding="utf-8"):
            if not x.strip():
                continue
            k = json.loads(x)
            if k["id"] not in goc:
                continue
            cap.append((goc[k["id"]], k.get("phat_bieu") or []))
        if not cap:
            print(f"({t}: khong ca nao khop id voi dap an)")
            continue
        kq = cham(cap)
        in_bang(kq, ten=f"{t}  ({len(cap)} ca)")
        (duong_dan.THU_MUC_KET_QUA / f"do-trich-{t}.json").write_text(
            json.dumps(kq, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
