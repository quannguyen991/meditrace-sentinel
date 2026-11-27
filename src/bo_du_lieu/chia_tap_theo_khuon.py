# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Nạp và chia]
Làm gì   : Chia bộ tự sinh thành huấn luyện, phát triển, kiểm tra cuối THEO KHUÔN BỆNH, để
           một khuôn chỉ nằm ở một tập, không lộ đề.
Vào → Ra : danh sách ca (mỗi ca có tên khuôn) → ba nhóm ca; phan_khuon() trả khuôn nào vào
           tập nào
Đọc từ   : phan_khuon() xếp từng khuôn vào tập; chia() áp lên danh sách ca;
           kiem_khop_bo_sinh() đối chiếu bộ sinh
Mục lục (các hàm/lớp chính):
  phan_khuon()         Phân mỗi khuôn bệnh vào một tập, chỉ dựa trên tên
  tap_cua_khuon()      Cho biết một khuôn bệnh thuộc tập nào
  chia()               Chia các ca thành ba tập theo khuôn bệnh
  kiem_khop_bo_sinh()  Dừng nếu khuôn bị chia khác tập bộ sinh đã giả định
  main()               Chia theo khuôn, ghi ba tập kèm vân tay bộ
Gọi tới  : bo_du_lieu/kho_khuon, bo_du_lieu/ngu_lieu_viet, bo_du_lieu/sinh_hoi_thoai_viet,
           bo_du_lieu/van_tay_bo, he_thong/duong_dan
Dùng bởi : bo_du_lieu/sinh_hoi_thoai_viet
Tên cũ   : tach_tap_viet.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chia bộ hội thoại Việt tự sinh thành ba tập, TÁCH THEO KHUÔN BỆNH.

VÌ SAO KHUÔN CHỨ KHÔNG PHẢI DÒNG. 3.000 dòng sinh ra từ 24 khuôn bệnh; hai
dòng cùng khuôn dùng chung dàn ý, chung kho triệu chứng, chung mạch hội
thoại — chúng gần như là một bài. Cắt theo dòng thì khuôn nào cũng có mặt ở
cả ba tập, và số trên tập kiểm chỉ đo "gặp lại khuôn đã học" chứ không đo
"gặp khuôn mới".

Đã mắc đúng lỗi này một lần: lần chia đầu tiên cho khâu trích cắt theo dòng,
và CẢ 24 khuôn đều lọt sang tập huấn luyện.

    train         75 khuôn
    phat_trien    13 khuôn   - đo, thử nghiệm, chọn thiết kế
    kiem_tra_cuoi 12 khuôn   - MỞ MỘT LẦN, sau khi khoá thiết kế

Tỷ lệ 8/7 thay cho 3/3 (10/09/2026): với 24 khuôn thì 3 khuôn giữ lại là
12,5%, còn chấp nhận được. Với 60 khuôn thì 3 khuôn chỉ còn 5% — một kết quả
trên ba khuôn không nói lên được gì về 60 khuôn. 13/12 thay cho 8/7 (11/09/2026)
khi bộ khuôn lên 100 — xem `SO_PHAT_TRIEN_MAC_DINH`.

ĐƠN VỊ ĐỘC LẬP VẪN LÀ KHUÔN BỆNH, không phải bối cảnh. Bối cảnh có mặt ở CẢ
BA tập là cố ý: nó không phải thứ đang đo khả năng khái quát, nó là thứ pha
do đều để con số `eval_loss` có nghĩa.

Chia bằng cách xếp tên khuôn rồi lấy theo băm cố định, không xáo ngẫu nhiên
theo thời gian chạy — chạy lại phải ra đúng ba tập đó.

    python -m src.bo_du_lieu.chia_tap_theo_khuon --nguon hoi_thoai_viet_5000_th5.jsonl --the-he 5
"""
import hashlib
import io
import json
import sys

from src.he_thong import duong_dan as duong_dan
from src.bo_du_lieu import van_tay_bo as van_tay_bo


# ─── _thu_tu() — Tạo thứ tự ổn định cho khuôn từ băm tên ──────────────────────────────
# Băm sha256 của hạt và tên khuôn, không phụ thuộc thứ tự đọc tệp.
def _thu_tu(ten_khuon, seed):
    """Thứ tự ổn định, tái lập được, không phụ thuộc thứ tự đọc tệp."""
    h = hashlib.sha256(f"{seed}:{ten_khuon}".encode()).hexdigest()
    return int(h[:12], 16)


SO_PHAT_TRIEN_MAC_DINH = 13
SO_KIEM_TRA_MAC_DINH = 12
HAT_MAC_DINH = 42

# Khuôn mở rộng (xem `phan_khuon`): 200 khuôn đầu là khuôn gốc; từ khuôn thứ 201 trở đi chia
# theo đợt, mỗi đợt một nhóm riêng. Tỷ lệ phát triển và kiểm tra mỗi đợt: 10% mỗi loại.
SO_KHUON_GOC = 200
KICH_THUOC_DOT_MO_RONG = 200
TY_LE_MO_RONG_PHAT_TRIEN = 0.10
TY_LE_MO_RONG_KIEM_TRA = 0.10


# ─── _cat_nhom() — Cắt nhóm khuôn thành train, phát triển, kiểm tra cuối ──────────────
# Sắp theo băm ổn định rồi cắt; kiểm tra ba tập không giao nhau.
def _cat_nhom(khuon, so_phat_trien, so_kiem_tra, seed):
    """Cắt một nhóm khuôn thành train / phát triển / kiểm tra cuối theo hạng băm ổn định."""
    khuon = sorted(set(khuon), key=lambda t: _thu_tu(t, seed))
    kt = set(khuon[:so_kiem_tra])
    pt = set(khuon[so_kiem_tra:so_kiem_tra + so_phat_trien])
    tr = set(khuon) - kt - pt
    assert not (kt & pt) and not (kt & tr) and not (pt & tr)
    return {"train": tr, "phat_trien": pt, "kiem_tra_cuoi": kt}


# ═══ phan_khuon() — Phân mỗi khuôn bệnh vào một tập, chỉ dựa trên tên ═════════════════
# Một định nghĩa duy nhất, dùng chung cho bước chia và bộ sinh.
def phan_khuon(cac_khuon, so_phat_trien=SO_PHAT_TRIEN_MAC_DINH,
               so_kiem_tra=SO_KIEM_TRA_MAC_DINH, seed=HAT_MAC_DINH):
    """-> {"train": set, "phat_trien": set, "kiem_tra_cuoi": set} — CHỈ từ tên.

    MỘT định nghĩa duy nhất, dùng chung cho `chia` VÀ cho bộ sinh.

    VÌ SAO BỘ SINH CẦN BIẾT TRƯỚC. Từ 11/09/2026 bộ sinh rút nội dung kể về
    người nhà từ BỂ RIÊNG của từng tập, để tầng 4 trên dev/test là nội dung CHƯA
    THẤY ở train. Trước đó cả ba tập dùng chung 25 chuỗi, và tập phát triển dùng
    lại đúng 25/25 chuỗi của train (284/284 mệnh đề) — nên tầng 4, chỗ quan
    trọng nhất của dự án, chưa bao giờ được thử trên nội dung chưa thấy.

    Muốn vậy bộ sinh phải biết khuôn nào sẽ vào tập nào TRƯỚC khi chia. Tính
    điều đó bằng một bản sao của logic chia thì hai bản sẽ trôi nhau — đúng họ
    lỗi "hai bảng cùng nghĩa ở hai tệp" đã gặp ở NHAN_VIEN_Y_TE. Nên cả hai gọi
    hàm này.
    """
    khuon = sorted(set(cac_khuon))
    from src.bo_du_lieu import ngu_lieu_viet as nl
    goc_100 = set(b["ten"] for b in nl.BENH[:100])
    # KHUÔN MỞ RỘNG (thêm 22/11/2026): khuôn ở vị trí >= 200 trong `nl.BENH` KHÔNG vào
    # nhóm `k_moi` cùng 101-200. Nếu vào, hạng của cả 101-200 đổi (xếp hạng bằng băm trong
    # nhóm) và 12 khuôn cũ nhảy tập (7 phát triển -> train, 5 kiểm tra -> phát triển):
    # mô hình học trên bộ mới sẽ thấy khuôn của tập phát triển/kiểm tra ĐÃ ĐÓNG BĂNG.
    # Mỗi đợt `KICH_THUOC_DOT_MO_RONG` khuôn là một nhóm RIÊNG, chia độc lập.
    from src.bo_du_lieu import kho_khuon as kho_khuon
    dot_cua = kho_khuon.dot_cua_khuon()
    # MỖI KHUÔN MỞ RỘNG thuộc một đợt; đợt chia theo THÀNH VIÊN ĐẦY ĐỦ của đợt (lấy từ kho),
    # rồi mới giao với các tên được truyền vào. Nhờ vậy tập của một khuôn chỉ phụ thuộc tên và
    # đợt của nó, KHÔNG phụ thuộc hàm gọi truyền vào bộ tên nào (đo 23/11/2026: truyền 270, 400,
    # 500 tên cho ra tập khác nhau cho 3, 0, 7 khuôn, nên bảng tập của bộ sinh và bước chia có thể
    # lệch nhau).
    k_goc, k_moi, co_mat_dot = [], [], {}
    for t in khuon:
        d = dot_cua.get(t)
        if d is not None:
            co_mat_dot.setdefault(d, set()).add(t)
        elif t in goc_100:
            k_goc.append(t)
        else:
            k_moi.append(t)
    nhom = [g for g in (k_goc, k_moi) if g]
    if len(nhom) + len(co_mat_dot) >= 2 and len(khuon) > 100:
        kq = {"train": set(), "phat_trien": set(), "kiem_tra_cuoi": set()}
        for g in nhom:
            p = phan_khuon(g, so_phat_trien=so_phat_trien, so_kiem_tra=so_kiem_tra, seed=seed)
            for k in kq:
                kq[k] |= p[k]
        tv = kho_khuon.thanh_vien_dot()
        for d, co_mat in sorted(co_mat_dot.items()):
            day_du = tv[d]
            n = max(1, round(TY_LE_MO_RONG_PHAT_TRIEN * len(day_du)))
            m = max(1, round(TY_LE_MO_RONG_KIEM_TRA * len(day_du)))
            p = _cat_nhom(list(day_du), n, m, seed)
            for k in kq:
                kq[k] |= p[k] & co_mat
        return kq
    return _cat_nhom(khuon, so_phat_trien, so_kiem_tra, seed)


# ═══ tap_cua_khuon() — Cho biết một khuôn bệnh thuộc tập nào ══════════════════════════
# Báo lỗi KeyError nếu khuôn không có trong danh sách.
def tap_cua_khuon(ten, cac_khuon, **kw):
    """-> "train" | "phat_trien" | "kiem_tra_cuoi" cho MỘT khuôn."""
    for tap, cac in phan_khuon(cac_khuon, **kw).items():
        if ten in cac:
            return tap
    raise KeyError(f"khuon {ten!r} khong nam trong danh sach")


# ═══ chia() — Chia các ca thành ba tập theo khuôn bệnh ════════════════════════════════
# Trả train, phát triển, kiểm tra cuối và danh sách khuôn của từng tập.
def chia(ca, so_phat_trien=SO_PHAT_TRIEN_MAC_DINH,
         so_kiem_tra=SO_KIEM_TRA_MAC_DINH, seed=HAT_MAC_DINH):
    """-> (train, phat_trien, kiem_tra_cuoi) và danh sách khuôn mỗi tập."""
    p = phan_khuon({k["benh"] for k in ca}, so_phat_trien, so_kiem_tra, seed)
    tr, pt, kt = p["train"], p["phat_trien"], p["kiem_tra_cuoi"]
    return (
        [k for k in ca if k["benh"] in tr],
        [k for k in ca if k["benh"] in pt],
        [k for k in ca if k["benh"] in kt],
        {"train": sorted(tr), "phat_trien": sorted(pt), "kiem_tra_cuoi": sorted(kt)},
    )


# ═══ kiem_khop_bo_sinh() — Dừng nếu khuôn bị chia khác tập bộ sinh đã giả định ════════
# Bắt lệch khi đổi tham số chia hoặc tệp thiếu khuôn, trước khi ghi tệp.
def kiem_khop_bo_sinh(khuon):
    """Dừng lại nếu một khuôn bị chia vào tập KHÁC tập mà bộ sinh đã giả định.

    Bộ sinh chọn bể nội dung người nhà theo tập của ca (xem `phan_khuon`). Hai
    đường làm lệch, và cả hai đều KHÔNG báo lỗi — bể theo tập cụ thể rò rỉ:

      - truyền `--so-phat-trien` / `--so-kiem-tra` / `--seed` khác mặc định
      - tệp THIẾU một khuôn dev/test: `chia` xếp từ các khuôn CÓ MẶT, bộ sinh
        xếp từ CẢ bảng khuôn, nên mọi khuôn xếp sau chỗ trống đó trượt sang tập
        bên cạnh

    Muốn chia lại một bộ cũ thì dùng mã nguồn ở commit ghi trong vân tay của bộ
    đó, không dùng mã hiện tại.
    """
    from src.bo_du_lieu import sinh_hoi_thoai_viet as sinh_hoi_thoai_viet  # nhập ở đây: tệp đó nhập ngược tệp này
    bo_sinh = sinh_hoi_thoai_viet.bang_tap_khuon()
    lech = sorted(t for tap, cac in khuon.items() for t in cac
                  if bo_sinh.get(t) != tap)
    if lech:
        raise SystemExit(
            f"{len(lech)} khuon bi chia vao tap khac tap ma bo sinh da gia dinh "
            f"(vi du {lech[:3]}): be noi dung nguoi nha se ro ri giua cac tap. "
            "Xem tach_tap_viet.kiem_khop_bo_sinh.")


# ─── _thong_ke() — Thống kê số ca, mệnh đề và tỷ lệ chủ thể khác bệnh nhân ────────────
# Trả số ca, số mệnh đề, số mệnh đề không phải bệnh nhân và tỷ lệ phần trăm.
def _thong_ke(ds):
    md = [m for k in ds for m in k["dap_an"]]
    kb = [m for m in md if m["chu_the"] != "bệnh nhân"]
    return len(ds), len(md), len(kb), (100 * len(kb) / max(1, len(md)))


# ═══ main() — Chia theo khuôn, ghi ba tập kèm vân tay bộ ══════════════════════════════
# Bắt buộc có --the-he; ghi vân tay cùng lúc và kiểm tra không khuôn nào lọt hai tập.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--nguon", default="hoi_thoai_viet_5000.jsonl")
    # Mặc định đọc từ HẰNG SỐ dùng chung với bộ sinh. Truyền số khác thì tập của
    # khuôn không còn khớp với bể nội dung người nhà mà bộ sinh đã chọn — và
    # `kiem_khop_bo_sinh` sẽ dừng lại trước khi ghi tệp nào.
    ap.add_argument("--so-phat-trien", type=int, default=SO_PHAT_TRIEN_MAC_DINH)
    ap.add_argument("--so-kiem-tra", type=int, default=SO_KIEM_TRA_MAC_DINH)
    ap.add_argument("--seed", type=int, default=HAT_MAC_DINH)
    # BẮT BUỘC, không có mặc định: thế hệ là thứ duy nhất phân biệt hai bộ cùng
    # tên, và để mặc định thì mỗi lần sinh lại đều mang cùng một nhãn.
    ap.add_argument("--the-he", required=True,
                    help="ten nguoi doc dung de goi bo nay, vi du 3 hoac 2b")
    ap.add_argument("--hau-to", default="",
                    help="hau to them vao ten tep ra, vi du _v2")
    a = ap.parse_args()

    d = duong_dan.THU_MUC_DU_LIEU
    ca = [json.loads(x) for x in open(d / a.nguon, encoding="utf-8") if x.strip()]
    tr, pt, kt, khuon = chia(ca, a.so_phat_trien, a.so_kiem_tra, a.seed)

    print(f"{'Tap':16}{'ca':>6}{'menh de':>10}{'khac BN':>9}{'ty le':>8}   khuon")
    for ten, ds in (("viet_train", tr), ("viet_phat_trien", pt),
                    ("viet_kiem_tra_cuoi", kt)):
        ten_tep = f"{ten}{a.hau_to}"
        dp = d / f"{ten_tep}.jsonl"
        dp.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in ds),
                      encoding="utf-8")
        # Vân tay ghi CÙNG LÚC với bộ. Ghi bộ rồi dán nhãn sau thì có một khoảng
        # thời gian bộ dữ liệu không ai biết nó là thế hệ nào — và ba lần họ lỗi
        # "một tên tệp, hai bộ dữ liệu" đều xảy ra trong đúng khoảng đó.
        van_tay_bo.ghi(dp, ds, a.the_he, hat=a.seed,
                       ghi_chu=f"chia tu {a.nguon}, tach theo khuon benh")
        n, md, kb, ty = _thong_ke(ds)
        khoa = ten.replace("viet_", "")
        print(f"{ten_tep:16}{n:>6}{md:>10}{kb:>9}{ty:>7.1f}%   "
              + ", ".join(khuon[khoa]))

    # Không khuôn nào được nằm ở hai tập. Kiểm lại ngay đây chứ không tin.
    tap_khuon = [set(khuon[t]) for t in ("train", "phat_trien", "kiem_tra_cuoi")]
    for i in range(3):
        for j in range(i + 1, 3):
            chung = tap_khuon[i] & tap_khuon[j]
            assert not chung, f"khuon lot hai tap: {chung}"
    print("\nKhong khuon nao lot hai tap.")


if __name__ == "__main__":
    main()
