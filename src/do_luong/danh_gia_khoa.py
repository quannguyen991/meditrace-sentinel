# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Thước đo]
Làm gì   : Đo tầng khoá bằng chứng chặn oan bao nhiêu trên đáp án hoàn hảo và bắt được bao
           nhiêu lỗi cấy có chủ định.
Vào → Ra : đáp án có cấu trúc (nguyên bản hoặc bị làm hỏng) → số mệnh đề bị chặn, cảnh báo
           hoặc lọt theo loại lỗi
Đọc từ   : phat_bieu_tu_dap_an() dựng mệnh đề hoàn hảo; do_bat_loi() đo bắt lỗi cấy
Mục lục (các hàm/lớp chính):
  phat_bieu_tu_dap_an()  Đổi đáp án có cấu trúc thành mệnh đề hoàn hảo
  thong_ke_khoa()        Đo tỉ lệ khoá chặn oan trên đáp án hoàn hảo
  do_bat_loi()           Đo khoá chặn, cảnh báo hay để lọt lỗi cấy
  do_bat_bo_sot()        Đo khoá có bắt được mệnh đề bị bỏ sót
  lam_hong()             Làm hỏng đúng một mệnh đề theo loại lỗi
Gọi tới  : do_luong/khoang_tin_cay, bo_du_lieu/du_lieu_huan_luyen_trich,
           duong_ong/b1_cau_truc_menh_de, duong_ong/b4_kiem_can_cu
Dùng bởi : do_luong/do_cay_loi, do_luong/do_dan_gian
Tên cũ   : danh_gia_khoa.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đánh giá các tầng mới — khoá bằng chứng, rủi ro, hỏi lại — trên ĐÁP ÁN CẤU TRÚC.

HAI LOẠI ĐẦU VÀO, và vì sao cần cả hai:

  đáp án hoàn hảo   `phat_bieu_tu_dap_an`: khâu trích KHÔNG sai gì. Mỗi lần tầng
                    khoá CHẶN ở đây là một lần chặn oan — đo được giá của tầng
                    khoá mà không lẫn với lỗi của mô hình.
  đáp án bị làm hỏng có chủ định (`lam_hong`): đổi chủ thể, nâng mức khẳng định,
                    bịa trích dẫn... — biết trước lỗi nào ở đâu, nên đo được tầng
                    khoá BẮT được bao nhiêu, theo TỪNG loại lỗi.

Đầu ra của mô hình (sau khi huấn luyện lại trên bộ thế hệ 5) đi qua cùng các hàm
này, nhưng phải kèm CỘT CHỌN BỪA cùng tỷ lệ — bài học của `duong_danh_doi`.

CHỈ HIỆU CHỈNH TRÊN KHUÔN CỦA TẬP TRAIN. Tập phát triển để xem, tập kiểm tra cuối
chỉ mở một lần.
"""
import random
from collections import Counter

from src.do_luong import khoang_tin_cay as sai_so
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu

VAI_HOP_LE = ("bác sĩ", "bệnh nhân", "điều dưỡng")


# ═══ phat_bieu_tu_dap_an() — Đổi đáp án có cấu trúc thành mệnh đề hoàn hảo ════════════
# Chủ thể chỉ chia hai mức: bệnh nhân hoặc người khác; bỏ mệnh đề lặp lý do khám.
def phat_bieu_tu_dap_an(ca) -> list:
    """Đáp án -> PhatBieu, như một khâu trích HOÀN HẢO.

    `id` = chỉ số trong `dap_an`, nên `quan_he_voi` giữ nguyên nghĩa. Chủ thể chỉ
    phân hai mức (0 = bệnh nhân, 1 = người khác) — tầng khoá chỉ cần thế.
    """
    from src.bo_du_lieu.du_lieu_huan_luyen_trich import ban_lap_ly_do_kham
    vai = sai_so.nguoi_noi_tung_luot(ca)
    lap = ban_lap_ly_do_kham(ca["dap_an"])
    ra = []
    for i, d in enumerate(ca["dap_an"]):
        luot = list(d.get("luot") or [])
        if not luot or i in lap:
            continue
        nn = str(vai.get(max(luot), "")).lower()
        qh = d.get("quan_he")
        ra.append(PhatBieu(
            id=i, nguoi_noi=nn if nn in VAI_HOP_LE else "người nhà",
            chu_the_id=0 if d["chu_the"] == "bệnh nhân" else 1,
            noi_dung=d["noi_dung"], bang_chung=luot,
            do_chac_chan=d.get("do_chac_chan") or "chắc chắn",
            phu_dinh=bool(d.get("phu_dinh")),
            tinh_huong=d.get("tinh_huong") or "thực tế",
            thoi_gian_su_kien=d.get("thoi_gian_su_kien") or "chưa rõ",
            moc_thoi_gian=d.get("moc_thoi_gian"),
            quan_he=qh, quan_he_voi=d.get("quan_he_voi") if qh else None,
            trang_thai=d.get("trang_thai") or "còn hiệu lực",
            trich_dan=list(d.get("trich_dan") or []),
            ten_chu_the=d["chu_the"], hanh_vi=d.get("hanh_vi") or "",
            # Chi tiết thuốc (15/09/2026): không chép sang thì phép đo chặn oan trên
            # đáp án hoàn hảo không bao giờ chạy K6 của khoá.
            thuoc=d.get("thuoc")))
    return ra


# ═══ vao_than() — Xét mệnh đề có vào thân hồ sơ nếu không bị khoá ═════════════════════
# Chỉ khi còn hiệu lực và không phải câu giả định.
def vao_than(p) -> bool:
    """Phát biểu này, nếu không bị khoá chặn, có vào THÂN hồ sơ không. Chặn oan
    chỉ tính trên những phát biểu này — bản bị thay thế hay câu gia đình vốn đã
    xuống CẦN XÁC NHẬN, khoá thêm lý do cũng không làm mất gì."""
    return p.trang_thai == "còn hiệu lực" and p.tinh_huong != "giả định"


# ═══ thong_ke_khoa() — Đo tỉ lệ khoá chặn oan trên đáp án hoàn hảo ════════════════════
# Đếm chặn, cảnh báo, đoạn chưa ghi theo từng lý do, kèm vài ví dụ.
def thong_ke_khoa(ds, bat_buoc_trich_dan=True, so_vi_du=3):
    """Chạy tầng khoá trên ĐÁP ÁN HOÀN HẢO của `ds` -> tỷ lệ chặn oan, cảnh báo,
    và đoạn chưa ghi — theo từng lý do, kèm vài ví dụ."""
    from src.duong_ong import b4_kiem_can_cu as kbc
    chan, canh, vi_du, doan = Counter(), Counter(), {}, Counter()
    tong_than = so_chan_oan = 0
    for ca in ds:
        ps = phat_bieu_tu_dap_an(ca)
        kq = kbc.khoa_ca(ps, ca["input"], bat_buoc_trich_dan)
        for p, k in zip(ps, kq["ket_qua"]):
            if not vao_than(p):
                continue
            tong_than += 1
            so_chan_oan += bool(k.chan)
            for m in k.chan:
                chan[m] += 1
                vi_du.setdefault(m, [])
                if len(vi_du[m]) < so_vi_du:
                    vi_du[m].append((ca["id"], p.noi_dung, p.trich_dan))
            for m in k.canh_bao:
                canh[m] += 1
        for d in kq["doan_chua_ghi"]:
            doan[d["doan"].lower()] += 1
    return {"tong_than": tong_than, "so_chan_oan": so_chan_oan,
            "chan": dict(chan), "canh_bao": dict(canh), "vi_du": vi_du,
            "doan_chua_ghi": doan}


# ------------------------------------------------------- làm hỏng có chủ định
LOAI_HONG = ("doi_chu_the", "nang_muc", "gia_dinh_thanh_that", "bia_trich_dan")


# ═══ lam_hong() — Làm hỏng đúng một mệnh đề theo loại lỗi ═════════════════════════════
# Loại: đổi chủ thể, nâng mức chắc chắn, giả định thành thật, bịa trích dẫn; trả bản mới
# và id.
def lam_hong(ps, loai, rng):
    """-> (danh sách MỚI, id phát biểu đã bị làm hỏng). Mỗi lần hỏng ĐÚNG MỘT
    phát biểu, chọn ngẫu nhiên trong những phát biểu hỏng được theo `loai`."""
    ung = []
    for p in ps:
        if not vao_than(p) and loai != "gia_dinh_thanh_that":
            continue
        if loai == "doi_chu_the":
            ung.append(p)
        elif loai == "nang_muc" and (p.do_chac_chan != "chắc chắn"):
            ung.append(p)
        elif loai == "gia_dinh_thanh_that" and p.tinh_huong == "giả định":
            ung.append(p)
        elif loai == "bia_trich_dan" and p.trich_dan:
            ung.append(p)
    if not ung:
        return None, None
    dich = rng.choice(ung)
    moi = []
    for p in ps:
        q = PhatBieu(**p.to_dict())
        if p.id == dich.id:
            if loai == "doi_chu_the":
                q.chu_the_id = 1 if p.chu_the_id == 0 else 0
            elif loai == "nang_muc":
                q.do_chac_chan, q.phu_dinh = "chắc chắn", False
            elif loai == "gia_dinh_thanh_that":
                q.tinh_huong = "thực tế"
            elif loai == "bia_trich_dan":
                q.trich_dan = [f"{p.noi_dung} từ tuần trước"] + p.trich_dan[1:]
        moi.append(q)
    return moi, dich.id


# ═══ do_bat_bo_sot() — Đo khoá có bắt được mệnh đề bị bỏ sót ══════════════════════════
# Bỏ một mệnh đề có trích dẫn mỗi ca, xem phép kiểm có chỉ ra đoạn đó không.
def do_bat_bo_sot(ds, seed=0):
    """BỎ một phát biểu vào thân (có trích dẫn) khỏi mỗi ca, rồi xem phép kiểm
    đầy đủ có chỉ ra ĐOẠN của nó không -> Counter{"phat_hien", "lot"}.

    Đây là phép đo cho nửa "kiểm đầy đủ đối chiếu với HỘI THOẠI": bỏ sót là lỗi
    mà `kiem_day_du` cũ không thể thấy, vì nó chỉ so bản nháp với bảng phát biểu.
    """
    from src.duong_ong import b4_kiem_can_cu as kbc
    rng = random.Random(seed)
    ket = Counter()
    for ca in ds:
        ps = phat_bieu_tu_dap_an(ca)
        ung = [p for p in ps if vao_than(p) and p.trich_dan]
        if not ung:
            continue
        bo = rng.choice(ung)
        con = [p for p in ps if p.id != bo.id]
        kq = kbc.khoa_ca(con, ca["input"])
        cac_luot = kbc._luot(ca["input"])
        vi_tri = []
        for so, t in zip(bo.bang_chung, bo.trich_dan):
            if so in cac_luot:
                vt = kbc.tim_trich(t, cac_luot[so][1])
                if vt:
                    vi_tri.append((so, vt))
        thay = any(d["luot"] == so and d["bat_dau"] < b and a < d["ket_thuc"]
                   for d in kq["doan_chua_ghi"] for so, (a, b) in vi_tri)
        ket["phat_hien" if thay else "lot"] += 1
    return ket


# ═══ do_bat_loi() — Đo khoá chặn, cảnh báo hay để lọt lỗi cấy ═════════════════════════
# Mỗi ca làm hỏng một mệnh đề theo loại; trả đếm chặn, cảnh báo, lọt và lý do.
def do_bat_loi(ds, loai, seed=0, bat_buoc_trich_dan=True):
    """Trên mỗi ca, làm hỏng một phát biểu theo `loai` rồi xem khoá CHẶN, CẢNH
    BÁO, hay để lọt -> Counter{"chan", "canh_bao", "lot"} và Counter lý do."""
    from src.duong_ong import b4_kiem_can_cu as kbc
    rng = random.Random(seed)
    ket, ly = Counter(), Counter()
    for ca in ds:
        ps = phat_bieu_tu_dap_an(ca)
        moi, dich = lam_hong(ps, loai, rng)
        if moi is None:
            continue
        kq = kbc.khoa_ca(moi, ca["input"], bat_buoc_trich_dan)["ket_qua"]
        k = next(x for x in kq if x.id == dich)
        if k.chan:
            ket["chan"] += 1
            ly.update(k.chan)
        elif k.canh_bao:
            ket["canh_bao"] += 1
            ly.update(k.canh_bao)
        else:
            ket["lot"] += 1
    return ket, ly
