# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Nạp và chia]
Làm gì   : Ghi vân tay bộ dữ liệu (thế hệ, hạt giống, commit, băm nội dung) để biết bộ nào
           sinh ra từ mã nào và bắt nhầm bộ.
Vào → Ra : danh sách bản ghi + thế hệ + hạt giống → dict vân tay ghi cạnh bộ; khop() đối
           chiếu bộ trên đĩa với vân tay
Đọc từ   : ghi() dựng và ghi vân tay cạnh bộ; khop() kiểm bộ trên đĩa có đúng vân tay không
Mục lục (các hàm/lớp chính):
  dung()              Dựng vân tay bộ dữ liệu
  ghi()               Dựng và ghi tệp vân tay JSON cạnh bộ
  doc()               Đọc vân tay của một bộ
  khop()              Đối chiếu bộ trên đĩa với vân tay của nó
  mo_ta()             Viết một dòng mô tả bộ để đặt đầu bảng số
  nhan_thieu_vi_du()  Tìm nhãn được khai nhưng vân tay cho thấy 0 ví dụ
Dùng bởi : do_luong/khoang_tin_cay, bo_du_lieu/chia_tap_theo_khuon,
           bo_du_lieu/sinh_bo_thach_thuc
Tên cũ   : van_tay_bo.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Vân tay của một bộ dữ liệu: thế hệ nào, hạt giống nào, mã nguồn nào sinh ra.

VÌ SAO CẦN — HỌ LỖI NÀY ĐÃ QUAY LẠI BA LẦN.

  lần 1 (09/09)  `train_baseline` chạy tiếp từ checkpoint của bộ 3.000 trên dữ
                 liệu bộ 5.000. Chỉ bị bắt vì `eval_loss` ở các bước đầu TRÙNG
                 TỪNG CHỮ SỐ với lần chạy trước — một dấu hiệu chỉ thấy được nếu
                 tình cờ còn nhớ số cũ. Mất khoảng 4 giờ GPU.

  lần 2 (10/09)  `data/ra_C_viet_phat_trien.jsonl` mang tên `viet_phat_trien`
                 nhưng là kết quả của bộ 3.000. Ghép nó với bộ dữ liệu hiện tại
                 mất 54/60 ca.

  lần 3 (10/09)  Và nặng hơn lần 2: bộ sinh DÙNG LẠI không gian id giữa các thế
                 hệ. `hv_0019` là "sốt siêu vi" trong bộ 3.000 và "thiếu máu do
                 giun" trong bộ 5.000. Đổi theo id thì bộ SAI cũng khớp 60/60 —
                 một phép ghép THÀNH CÔNG 100% với toàn bộ nhãn sai, không ngoại
                 lệ, không thiếu dòng, không dấu hiệu gì trên bảng số.

Ba lần đều cùng một hình: **tên tệp không nói được nó chứa gì.** Và cả ba lần
đều chỉ bị bắt bằng một dấu hiệu tình cờ.

Chữa bằng cách dán nhãn: mỗi bộ dữ liệu sinh ra thì ghi kèm một tệp vân tay, và
mọi chỗ ĐỌC bộ dữ liệu thì đối chiếu vân tay trước khi tính số.

    data/viet_train.jsonl
    data/viet_train.van_tay.json     <- sinh cùng lúc, không bao giờ sửa tay

VÂN TAY GHI GÌ, và vì sao từng mục:

    the_he      tên người đọc dùng để gọi bộ này ("3", "2b") — số liệu trong
                báo cáo phải gọi đúng tên
    hat         hạt giống; bộ này sinh lại được không
    commit      mã nguồn nào sinh ra. Đổi bộ sinh mà giữ hạt thì ra bộ KHÁC
    so_ca       để bắt trường hợp ghép thiếu
    bam_noi_dung  băm của NỘI DUNG, không của id — vì id bị dùng lại
    phan_bo     phân bố nhãn: để thấy ngay một nhãn có 0 ví dụ
"""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

DUOI = ".van_tay.json"


# ─── _commit() — Lấy mã commit, thêm hậu tố bản nháp nếu cây còn sửa ──────────────────
# Tránh ghi commit cũ không chứa mã đã sinh ra bộ.
def _commit():
    """-> mã commit, kèm hậu tố `-ban-nhap` nếu cây làm việc còn thay đổi.

    LỖ~ TRONG BAN ĐẦU CỦA CHÍNH TỆP NÀY: ghi `git rev-parse HEAD` là ghi commit
    CUỐI CÙNG ĐÃ COMMIT, không phải mã nguồn thật sự đã sinh ra bộ dữ liệu. Sinh
    bộ khi đang có sửa chưa commit thì vân tay ghi một commit **không chứa đoạn
    mã đó** — tức là trường `commit` nói sai, và nói sai một cách không thể phát
    hiện từ chính nó.

    Đã xảy ra ngay trong lần dùng đầu tiên: bộ thế hệ 3 được sinh khi
    `loi_dan_thuong.py` còn đang sửa, nên vân tay ghi commit 2e57b3d trong khi
    bảng từ dùng để sinh không nằm trong commit đó.
    """
    try:
        ma = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True, timeout=10
                            ).stdout.strip()
        ban_nhap = subprocess.run(["git", "status", "--porcelain", "--",
                                   "src", "tests"],
                                  capture_output=True, text=True, timeout=10
                                  ).stdout.strip()
        if not ma:
            return "khong-ro"
        return ma + ("-ban-nhap" if ban_nhap else "")
    except Exception:                                          # noqa: BLE001
        return "khong-ro"


# ═══ bam_noi_dung() — Băm theo nội dung hội thoại và đáp án, không theo id ════════════
# Id dùng lại giữa các thế hệ nên băm theo id là vô nghĩa.
def bam_noi_dung(cac_ban_ghi):
    """Băm theo NỘI DUNG hội thoại VÀ ĐÁP ÁN, không theo id.

    Băm theo id là vô nghĩa ở đây: id bị dùng lại giữa các thế hệ, nên hai bộ
    khác nhau hoàn toàn sẽ cho cùng một băm.

    VÀ PHẢI GỒM CẢ ĐÁP ÁN — lỗ~ trong ban đầu của chính hàm này.
    Ban đầu nó chỉ băm trường `input`. Ngày 11/09/2026 tôi thêm trường
    `thoi_gian_su_kien` vào đáp án rồi sinh lại bộ: hội thoại không đổi một chữ,
    nên thế hệ 3 và thế hệ 4 cho **cùng một băm** — `9486115ed86f669a` cho cả
    hai. Hai bộ có cùng hội thoại nhưng KHÁC NHÃN sẽ lẫn vào nhau mà vân tay
    không thấy, tức là đúng loại hỏng mà hàm này được viết ra để chặn.
    """
    h = hashlib.sha256()
    for b in cac_ban_ghi:
        h.update(" ".join(str(b.get("input") or "").split()).encode("utf-8"))
        h.update(b"\x01")
        # Đáp án: băm các trường MANG NHÃN, theo thứ tự cố định. Không băm cả
        # dict vì thứ tự khoá có thể đổi mà nội dung không đổi.
        for m in (b.get("dap_an") or []):
            for khoa in ("chu_the", "noi_dung", "muc", "moc_thoi_gian",
                         "phu_dinh", "tinh_huong", "thoi_gian_su_kien",
                         "quan_he", "quan_he_voi", "trang_thai", "luot"):
                h.update(f"{khoa}={m.get(khoa)!r}".encode("utf-8"))
            h.update(b"\x02")
        h.update(b"\x00")
    return h.hexdigest()[:16]


# ─── _phan_bo() — Đếm phân bố các nhãn trong bộ ───────────────────────────────────────
# Nhãn có 0 ví dụ phải hiện ngay ở đây.
def _phan_bo(cac_ban_ghi):
    """Phân bố nhãn. Một nhãn có 0 ví dụ phải NHÌN THẤY NGAY ở đây."""
    ra = {}
    for truong in ("quan_he", "trang_thai", "tinh_huong"):
        c = Counter(str(m.get(truong)) for b in cac_ban_ghi
                    for m in (b.get("dap_an") or []))
        if c:
            ra[truong] = dict(sorted(c.items(), key=lambda x: -x[1]))
    for truong in ("benh", "boi_canh"):
        c = Counter(str(b.get(truong)) for b in cac_ban_ghi)
        ra[f"so_{truong}"] = len(c)
    return ra


# ═══ dung() — Dựng vân tay bộ dữ liệu ═════════════════════════════════════════════════
# Gồm thế hệ, hạt, commit, số ca, số mệnh đề, băm và phân bố.
def dung(cac_ban_ghi, the_he, hat=None, ghi_chu=""):
    """-> dict vân tay."""
    return {"the_he": str(the_he), "hat": hat, "commit": _commit(),
            "so_ca": len(cac_ban_ghi),
            "so_menh_de": sum(len(b.get("dap_an") or []) for b in cac_ban_ghi),
            "bam_noi_dung": bam_noi_dung(cac_ban_ghi),
            "phan_bo": _phan_bo(cac_ban_ghi), "ghi_chu": ghi_chu}


# ═══ duong_dan_van_tay() — Tính đường dẫn tệp vân tay cạnh bộ dữ liệu ═════════════════
# Đổi đuôi tên tệp thành đuôi vân tay.
def duong_dan_van_tay(duong_dan_bo):
    p = Path(duong_dan_bo)
    return p.with_name(p.name.rsplit(".", 1)[0] + DUOI)


# ═══ ghi() — Dựng và ghi tệp vân tay JSON cạnh bộ ═════════════════════════════════════
# Trả dict vân tay.
def ghi(duong_dan_bo, cac_ban_ghi, the_he, hat=None, ghi_chu=""):
    vt = dung(cac_ban_ghi, the_he, hat, ghi_chu)
    duong_dan_van_tay(duong_dan_bo).write_text(
        json.dumps(vt, ensure_ascii=False, indent=2), encoding="utf-8")
    return vt


# ═══ doc() — Đọc vân tay của một bộ ═══════════════════════════════════════════════════
# Trả None nếu bộ chưa có vân tay.
def doc(duong_dan_bo):
    """-> dict vân tay, hoặc None nếu bộ này chưa có vân tay."""
    p = duong_dan_van_tay(duong_dan_bo)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


# ═══ mo_ta() — Viết một dòng mô tả bộ để đặt đầu bảng số ══════════════════════════════
# Bộ không có vân tay thì cảnh báo chưa biết thế hệ.
def mo_ta(duong_dan_bo):
    """-> chuỗi một dòng để in ở đầu mỗi bảng số.

    Một bảng số không nói nó đo trên bộ nào thì không đọc được sau ba tháng.
    """
    vt = doc(duong_dan_bo)
    if not vt:
        return (f"{Path(duong_dan_bo).name}: CHUA CO VAN TAY — khong biet day la "
                f"the he nao. Sinh lai bo nay, hoac ghi van tay bang "
                f"`src.bo_du_lieu.van_tay_bo.ghi`.")
    return (f"{Path(duong_dan_bo).name}: thế hệ {vt['the_he']}, "
            f"{vt['so_ca']} ca, hạt {vt['hat']}, commit {vt['commit']}, "
            f"băm {vt['bam_noi_dung']}")


# ═══ khop() — Đối chiếu bộ trên đĩa với vân tay của nó ════════════════════════════════
# Phát hiện tệp bị sửa tay hoặc bị thế hệ khác ghi đè.
def khop(duong_dan_bo, cac_ban_ghi):
    """-> (khop, thong_diep). Đối chiếu bộ đang nằm trên đĩa với vân tay của nó.

    Dùng khi một tệp bị sửa tay, hoặc bị ghi đè bởi một thế hệ khác mà vân tay
    không được cập nhật theo.
    """
    vt = doc(duong_dan_bo)
    if not vt:
        return None, mo_ta(duong_dan_bo)
    bam = bam_noi_dung(cac_ban_ghi)
    if bam == vt["bam_noi_dung"] and len(cac_ban_ghi) == vt["so_ca"]:
        return True, f"khớp vân tay thế hệ {vt['the_he']}"
    return False, (
        f"{Path(duong_dan_bo).name} KHONG khop van tay cua chinh no.\n"
        f"  van tay ghi : the he {vt['the_he']}, {vt['so_ca']} ca, "
        f"bam {vt['bam_noi_dung']}\n"
        f"  tep hien co : {len(cac_ban_ghi)} ca, bam {bam}\n"
        f"Tep da bi ghi de hoac sua tay sau khi van tay duoc lap. Sinh lai bo, "
        f"dung tiep se cho mot bang so khong the truy nguoc.")


# ═══ nhan_thieu_vi_du() — Tìm nhãn được khai nhưng vân tay cho thấy 0 ví dụ ═══════════
# Bắt lỗi khai quá so với dữ liệu thật.
def nhan_thieu_vi_du(duong_dan_bo, khai_bao):
    """-> các nhãn được khai trong lược đồ mà vân tay cho thấy có 0 ví dụ.

    `khai_bao`: {ten_truong: tuple các giá trị hợp lệ}.

    Đây là chỗ để bắt lỗ~ "khai quá": lược đồ khai bốn quan hệ, dữ liệu có hai.
    Trước 11/09/2026 chuyện đó chỉ bị phát hiện bằng cách tình cờ đi đếm.
    """
    vt = doc(duong_dan_bo)
    if not vt:
        return {}
    ra = {}
    for truong, cac_gia_tri in khai_bao.items():
        co = vt.get("phan_bo", {}).get(truong, {})
        thieu = [v for v in cac_gia_tri if not co.get(v)]
        if thieu:
            ra[truong] = thieu
    return ra
