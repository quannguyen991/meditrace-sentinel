# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 6 – Hỏi lại và sửa]
Làm gì   : Chọn ít câu hỏi nhất (tối đa 3) mà giải quyết được nhiều rủi ro nhất để bác sĩ
           hỏi lại người bệnh.
Vào → Ra : danh sách mệnh đề + đánh giá rủi ro → danh sách CauHoi được chọn; cập nhật mệnh
           đề theo câu trả lời
Đọc từ   : ung_vien() sinh mọi câu hỏi khả dĩ; chon() chọn theo lợi ích trên chi phí;
           ap_dung_tra_loi() cập nhật mệnh đề
Mục lục (các hàm/lớp chính):
  ung_vien()          Sinh mọi câu hỏi lại khả dĩ
  chon()              Chọn các câu hỏi theo lợi ích trên chi phí
  ap_dung_tra_loi()   Cập nhật mệnh đề theo câu trả lời nhận được
  mo_phong_hoi_lai()  Mô phỏng trả lời để tính trần sửa lỗi
  class CauHoi        Một câu hỏi lại ứng viên
Gọi tới  : duong_ong/b0_chuan_hoa_phuong_ngu, duong_ong/b5_xep_cho_cong_rui_ro
Dùng bởi : duong_ong/chay_duong_ong
Tên cũ   : hoi_lai.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tầng 6 — HỎI LẠI: Chọn ít câu hỏi nhất mà giải quyết được nhiều rủi ro nhất.

Nâng cấp:
- Hỗ trợ kiểu câu hỏi (co_khong, lua_chon, tu_do) kèm danh sách chips UI.
- Gom cụm đa phát biểu (chủ thể, nhóm triệu chứng nặng, tương tác thuốc).
- Thuật toán tham lam tối ưu hoá theo tỷ lệ Lợi ích / Chi phí nhận thức.
- Hàm áp dụng câu trả lời & mô phỏng đối chứng với chọn ngẫu nhiên.
"""
import random
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.duong_ong import b5_xep_cho_cong_rui_ro as cr

TOI_DA = 3


# ═══ class CauHoi — Một câu hỏi lại ứng viên ══════════════════════════════════════════
# Gồm văn câu hỏi, lý do, mệnh đề nhắm tới, kiểu câu, lựa chọn, cờ khẩn cấp và chi phí
# nhận thức.
@dataclass
class CauHoi:
    van: str
    ly_do: str
    # {id phát biểu: điểm rủi ro} — những phát biểu câu hỏi này giải quyết
    muc_tieu: Dict[int, float] = field(default_factory=dict)
    kieu: str = "co_khong"  # "co_khong", "lua_chon", "tu_do", "thoi_gian"
    lua_chon: List[str] = field(default_factory=list)
    khan_cap: bool = False
    chi_phi: float = 1.0  # Tải nhận thức: 1.0 (nhanh/dễ), 1.5 - 2.0 (phức tạp/mơ)

    @property
    def loi_ich(self) -> float:
        return round(sum(self.muc_tieu.values()), 4)

    @property
    def hieu_qua(self) -> float:
        """Tỷ lệ lợi ích trên chi phí nhận thức của người trả lời."""
        return round(self.loi_ich / max(self.chi_phi, 0.1), 4)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["loi_ich"] = self.loi_ich
        d["hieu_qua"] = self.hieu_qua
        return d


# ─── _hoa() — Viết hoa chữ cái đầu của chuỗi ──────────────────────────────────────────
def _hoa(s: str) -> str:
    s = str(s or "").strip()
    return s[:1].upper() + s[1:]


# ─── _ten_khac() — Lấy tên gọi người không phải bệnh nhân ─────────────────────────────
# Dùng tên chủ thể nếu có, không thì "người nhà".
def _ten_khac(p) -> str:
    if getattr(p, "chu_the_id", 0) != 0 and getattr(p, "ten_chu_the", ""):
        return p.ten_chu_the
    return "người nhà"


# ─── _cau_don_theo_ly_do() — Dựng câu hỏi đơn theo lý do cần hỏi ──────────────────────
# Trả về (nội dung, kiểu câu, các lựa chọn, chi phí); ví dụ hỏi thông tin là của ai.
def _cau_don_theo_ly_do(p, ly: str) -> Tuple[str, str, List[str], float]:
    """Trả về: (noi_dung_cau_hoi, kieu_cau_hoi, danh_sach_lua_chon, chi_phi)."""
    nd = p.noi_dung
    
    if ly.startswith("chu_the"):
        ten = _ten_khac(p)
        return (
            f"Thông tin '{nd}' là của bệnh nhân hay của {ten} ạ?",
            "lua_chon",
            ["Bệnh nhân", ten, "Cả hai", "Không ai"],
            1.0,
        )
    if ly == "vuot_muc_nghi":
        return (
            f"'{_hoa(nd)}' đã được chẩn đoán/xác nhận chắc chắn hay mới là nghi ngờ ạ?",
            "lua_chon",
            ["Đã chắc chắn", "Chỉ nghi ngờ/tự phỏng đoán", "Chưa rõ"],
            1.0,
        )
    if ly in ("vuot_muc_chua_ghi_nhan", "phu_dinh_vuot_muc", "co_tu_phu_dinh"):
        return (
            f"Hiện tại đối với '{nd}': có, chắc chắn không có, hay chưa theo dõi ạ?",
            "lua_chon",
            ["Đang có", "Chắc chắn không có", "Chưa theo dõi/chưa rõ"],
            1.0,
        )
    if ly == "dieu_kien":
        return (
            f"'{_hoa(nd)}' là triệu chứng đang xảy ra thật, hay chỉ là giả định ('nếu có') ạ?",
            "lua_chon",
            ["Đang có thật", "Chỉ giả định/dặn dò", "Không rõ"],
            1.0,
        )
    if ly == "moc_khong_thay":
        return (
            f"'{_hoa(nd)}' xuất hiện bắt đầu từ khi nào và kéo dài bao lâu rồi ạ?",
            "thoi_gian",
            ["Hôm nay", "1-2 ngày trước", "> 3 ngày trước", "Không nhớ rõ"],
            1.2,
        )
    if ly == "phuong_ngu_can_hoi":
        for t in getattr(p, "trich_dan", None) or []:
            mo = chuan_hoa.can_hoi(t)
            if mo:
                return (
                    f"Từ '{mo[0].goc}' trong lời kể có nghĩa là gì ạ? ({mo[0].ly_do})",
                    "tu_do",
                    [],
                    1.5,
                )
    if ly == "noi_dung_khong_khop":
        t = (getattr(p, "trich_dan", None) or [""])[0]
        return (
            f"Khi nói '{t}', có phải ý bác muốn nói đến '{nd}' không ạ?",
            "co_khong",
            ["Đúng vậy", "Không phải", "Ý khác"],
            1.0,
        )
    if ly == "lieu_khong_thay":
        return (
            f"Liều dùng chính xác của thuốc '{nd}' là bao nhiêu ạ?",
            "tu_do",
            [],
            1.2,
        )
    if ly == "duong_dung_khong_thay":
        return (
            f"Thuốc '{nd}' dùng theo đường nào (uống, tiêm, bôi ngoài da...)?",
            "lua_chon",
            ["Đường uống", "Đường tiêm", "Bôi ngoài da", "Khác"],
            1.0,
        )
    if ly == "chi_tiet_thuoc_khong_thay":
        return (
            f"Thuốc '{nd}' dùng ngày mấy lần và thời điểm nào ạ?",
            "lua_chon",
            ["1 lần/ngày", "2 lần/ngày", "3 lần/ngày", "Khi cần", "Khác"],
            1.0,
        )
        
    return (f"Xin xác nhận lại thông tin: '{nd}' có đúng không ạ?", "co_khong", ["Đúng", "Sai"], 1.0)


# ═══ ung_vien() — Sinh mọi câu hỏi lại khả dĩ ═════════════════════════════════════════
# Từ các mệnh đề và kết quả chấm rủi ro; một câu giải quyết cả cặp mâu thuẫn.
def ung_vien(ps: List[Any], danh_gia: List[Any]) -> List[CauHoi]:
    """Tạo toàn bộ các ứng viên câu hỏi khả dĩ từ tập phát biểu và kết quả đánh giá."""
    theo_id = {p.id: p for p in ps}
    dg = {d.id: d for d in danh_gia}
    ra: List[CauHoi] = []
    da_phu: Set[int] = set()

    # -------------------------------------------------------------
    # 1. MÂU THUẪN: Một câu giải quyết cả cặp
    # -------------------------------------------------------------
    for p in ps:
        if p.quan_he != "mâu thuẫn" or p.quan_he_voi not in theo_id or p.id in da_phu:
            continue
        q = theo_id[p.quan_he_voi]
        a, b = q.moc_thoi_gian, p.moc_thoi_gian
        
        if a and b and a != b:
            van = f"Về '{p.noi_dung}': thời điểm đúng là {a} hay {b} ạ?"
            opts = [str(a), str(b), "Mốc khác"]
        else:
            van = f"Về '{p.noi_dung}': có hai thông tin trái ngược ('{q.noi_dung}' vs '{p.noi_dung}'), thông tin nào chính xác ạ?"
            opts = [q.noi_dung, p.noi_dung, "Cả hai đều chưa đúng"]

        diem_q = dg[q.id].nghiem_trong if q.id in dg else 1.0
        diem_p = dg[p.id].nghiem_trong if p.id in dg else 1.0

        ra.append(
            CauHoi(
                van=van,
                ly_do="mau_thuan",
                muc_tieu={q.id: diem_q, p.id: diem_p},
                kieu="lua_chon",
                lua_chon=opts,
                chi_phi=1.2,
            )
        )
        da_phu |= {p.id, q.id}

    # -------------------------------------------------------------
    # 2. DỊ ỨNG: Kết hợp "Chưa ghi nhận" bệnh nhân + "Dị ứng" người nhà
    # -------------------------------------------------------------
    nha_di_ung = [p for p in ps if getattr(p, "chu_the_id", 0) != 0 and "dị ứng" in p.noi_dung.lower()]
    for p in ps:
        if p.id in da_phu or getattr(p, "chu_the_id", 0) != 0 or not nha_di_ung:
            continue
        if "dị ứng" not in p.noi_dung.lower() or getattr(p, "do_chac_chan", "") != "chưa ghi nhận":
            continue

        chat = nha_di_ung[0].noi_dung.lower().replace("dị ứng", "").strip()
        ten_nha = _ten_khac(nha_di_ung[0])
        van = (
            f"Hồ sơ ghi nhận {ten_nha} có tiền sử dị ứng {chat}. "
            f"Bệnh nhân trước đây đã từng dùng hoặc có phản ứng với {chat} chưa ạ?"
        )
        
        muc = {p.id: dg[p.id].diem if p.id in dg else cr.MUC_NGHIEM_TRONG.get("di_ung", 1.0) * 0.5}
        for n in nha_di_ung:
            if n.id in dg and dg[n.id].nhom not in (cr.DA_KIEM_CHUNG, cr.RUI_RO_THAP):
                muc[n.id] = dg[n.id].diem

        ra.append(
            CauHoi(
                van=van,
                ly_do="di_ung_chua_ghi_nhan",
                muc_tieu=muc,
                kieu="lua_chon",
                lua_chon=["Đã từng dùng an toàn", f"Có từng bị dị ứng {chat}", "Chưa bao giờ dùng", "Không chắc chắn"],
                khan_cap=True,
                chi_phi=1.0,
            )
        )
        da_phu |= set(muc.keys())

    # -------------------------------------------------------------
    # 3. GOM CỤM CHỦ THỂ MƠ HỒ (Nhiều triệu chứng không rõ chủ thể)
    # -------------------------------------------------------------
    cac_chu_the_mo = [
        p for p in ps
        if p.id not in da_phu and p.id in dg
        and any(ly.startswith("chu_the") for ly in dg[p.id].ly_do)
    ]
    if len(cac_chu_the_mo) >= 2:
        ten_chung = _ten_khac(cac_chu_the_mo[0])
        ds_nd = ", ".join([f"'{p.noi_dung}'" for p in cac_chu_the_mo[:3]])
        van = f"Các biểu hiện gồm: {ds_nd} là của bệnh nhân hay của {ten_chung} ạ?"
        muc = {p.id: dg[p.id].diem for p in cac_chu_the_mo[:3]}
        ra.append(
            CauHoi(
                van=van,
                ly_do="gom_chu_the_mo_ho",
                muc_tieu=muc,
                kieu="lua_chon",
                lua_chon=["Tất cả của bệnh nhân", f"Tất cả của {ten_chung}", "Chỉ một số (cần tách riêng)"],
                chi_phi=1.3,
            )
        )
        da_phu |= set(muc.keys())

    # -------------------------------------------------------------
    # 4. GOM CỤM TRIỆU CHỨNG NGUY CƠ / KHẨN CẤP (Red Flags)
    # -------------------------------------------------------------
    trieu_chung_nang = [
        p for p in ps
        if p.id not in da_phu and p.id in dg
        and (getattr(dg[p.id], "nghiem_trong", 0) >= 0.8 or getattr(dg[p.id], "diem", 0) >= 0.8)
        and dg[p.id].nhom in (cr.BI_CHAN, cr.NGUY_CO_CAO)
    ]
    if len(trieu_chung_nang) >= 2:
        ds_nang = " và ".join([f"'{p.noi_dung}'" for p in trieu_chung_nang[:2]])
        van = f"Bệnh nhân có đồng thời xuất hiện {ds_nang} ở mức độ nguy hiểm hoặc tăng nhanh không ạ?"
        muc = {p.id: dg[p.id].diem for p in trieu_chung_nang[:2]}
        ra.append(
            CauHoi(
                van=van,
                ly_do="canh_bao_red_flag",
                muc_tieu=muc,
                kieu="co_khong",
                lua_chon=["Có, đang tăng nặng", "Có nhưng nhẹ", "Không có"],
                khan_cap=True,
                chi_phi=1.0,
            )
        )
        da_phu |= set(muc.keys())

    # -------------------------------------------------------------
    # 5. CÁC PHÁT BIỂU CÒN LẠI: Duyệt thứ tự rủi ro cao xuống thấp
    # -------------------------------------------------------------
    for d in cr.thu_tu_duyet(danh_gia):
        if d.nhom in (cr.DA_KIEM_CHUNG, cr.RUI_RO_THAP) or d.id in da_phu:
            continue
        p = theo_id[d.id]
        ly = d.ly_do[0] if d.ly_do else "khac"
        
        van, kieu, opts, phi = _cau_don_theo_ly_do(p, ly)
        khan_cap = (getattr(d, "nghiem_trong", 0) >= 0.8 and d.nhom in (cr.BI_CHAN, cr.NGUY_CO_CAO)) or getattr(d, "diem", 0) >= 0.8
        
        ra.append(
            CauHoi(
                van=van,
                ly_do=ly,
                muc_tieu={p.id: d.diem},
                kieu=kieu,
                lua_chon=opts,
                khan_cap=khan_cap,
                chi_phi=phi,
            )
        )
        da_phu.add(p.id)

    return ra


# ═══ chon() — Chọn các câu hỏi theo lợi ích trên chi phí ══════════════════════════════
# Tham lam theo hiệu quả biên, ưu tiên câu khẩn cấp khi ngang nhau, tối đa TOI_DA câu.
def chon(cac_cau: List[CauHoi], toi_da: int = TOI_DA) -> List[CauHoi]:
    """Chọn tham lam dựa trên Hiệu quả biên (Lợi ích còn lại / Chi phí nhận thức).
    
    Ưu tiên các câu hỏi có cờ khan_cap = True khi tỷ lệ hiệu quả tương đương.
    """
    con = list(cac_cau)
    ra: List[CauHoi] = []
    da_phu: Set[int] = set()

    while con and len(ra) < toi_da:
        def loi_ich_chua_phu(c: CauHoi) -> float:
            return sum(v for k, v in c.muc_tieu.items() if k not in da_phu)

        def tieu_chi_chon(c: CauHoi) -> Tuple[float, bool]:
            loi_ich_moi = loi_ich_chua_phu(c)
            hieu_qua_moi = loi_ich_moi / max(c.chi_phi, 0.1)
            # Ưu tiên hiệu quả biên; nếu tương đương ưu tiên câu khẩn cấp
            return (round(hieu_qua_moi, 4), bool(c.khan_cap and loi_ich_moi > 0))

        tot = max(con, key=tieu_chi_chon)
        if loi_ich_chua_phu(tot) <= 0:
            break

        ra.append(tot)
        da_phu |= set(tot.muc_tieu.keys())
        con.remove(tot)

    return ra


# =====================================================================
# VÒNG LẶP PHẢN HỒI (FEEDBACK LOOP) & MÔ PHỎNG ĐÁNH GIÁ
# =====================================================================

# ═══ ap_dung_tra_loi() — Cập nhật mệnh đề theo câu trả lời nhận được ══════════════════
# Tuỳ lý do hỏi (mâu thuẫn, chủ thể, mốc...) mà đổi trạng thái hoặc trường tương ứng.
def ap_dung_tra_loi(p, cau_hoi: CauHoi, cau_tra_loi: str) -> None:
    """Cập nhật trạng thái phát biểu dựa trên câu trả lời nhận được từ người dùng."""
    tl = cau_tra_loi.strip().lower()
    ly = cau_hoi.ly_do

    if ly == "mau_thuan":
        if "không" not in tl and "chưa đúng" not in tl:
            p.moc_thoi_gian = cau_tra_loi
            if getattr(p, "quan_he_voi", None) is not None:
                p.quan_he = "bổ sung"
            else:
                p.quan_he = None
                p.quan_he_voi = None
            p.trang_thai = "còn hiệu lực"
    elif ly == "chu_the" or ly == "gom_chu_the_mo_ho":
        if "bệnh nhân" in tl:
            p.chu_the_id = 0
            p.ten_chu_the = "bệnh nhân"
        elif "người nhà" in tl or any(x in tl for x in ["mẹ", "bố", "vợ", "chồng"]):
            p.chu_the_id = 1
    elif ly == "vuot_muc_nghi":
        if "chắc chắn" in tl:
            p.do_chac_chan = "chắc chắn"
        elif "nghi ngờ" in tl:
            p.do_chac_chan = "nghi ngờ"
    elif ly == "di_ung_chua_ghi_nhan":
        if getattr(p, "chu_the_id", 0) != 0:
            return
        if any(x in tl for x in ("chưa bao giờ", "chưa từng", "chưa dùng", "chưa thấy", "không chắc", "chưa rõ")):
            p.do_chac_chan = "chưa ghi nhận"
            p.phu_dinh = False
        elif (
            any(x in tl for x in ("an toàn", "không có", "không dị ứng", "không bị", "không phản ứng", "không mẫn cảm"))
            or tl in ("không", "ko", "dạ không")
        ):
            p.do_chac_chan = "chắc chắn"
            p.phu_dinh = True
        elif "có" in tl or "dị ứng" in tl:
            p.do_chac_chan = "chắc chắn"
            p.phu_dinh = False


# ═══ mo_phong_hoi_lai() — Mô phỏng trả lời để tính trần sửa lỗi ═══════════════════════
# Chọn câu hỏi, cho bộ trả lời giả định đáp, rồi tính tỉ lệ lỗi sửa được tối đa.
def mo_phong_hoi_lai(
    ps: List[Any],
    danh_gia: List[Any],
    oracle_tra_loi: Optional[Callable[[CauHoi], str]] = None,
    k: int = TOI_DA,
) -> Dict[str, Any]:
    """Mô phỏng trả lời và tính toán trần trên (upper bound) tỷ lệ sửa lỗi."""
    danh_sach_cau = ung_vien(ps, danh_gia)
    cac_cau_chon = chon(danh_sach_cau, toi_da=k)

    def _tinh_rui_ro_duy_nhat(cac_cau: List[CauHoi]) -> Tuple[int, float]:
        ids = set()
        tong = 0.0
        for c in cac_cau:
            for p_id, diem in c.muc_tieu.items():
                if p_id not in ids:
                    ids.add(p_id)
                    tong += diem
        return len(ids), round(tong, 4)

    so_sua, tong_diem_giai_quyet = _tinh_rui_ro_duy_nhat(cac_cau_chon)

    # Nếu có oracle_tra_loi thì áp dụng trực tiếp vào phát biểu
    if oracle_tra_loi is not None:
        theo_id = {p.id: p for p in ps}
        for c in cac_cau_chon:
            tl = oracle_tra_loi(c)
            for p_id in c.muc_tieu:
                if p_id in theo_id:
                    ap_dung_tra_loi(theo_id[p_id], c, tl)

    # Mô phỏng baseline: Chọn ngẫu nhiên cùng số lượng câu hỏi
    so_cau = min(k, len(danh_sach_cau))
    ngau_nhien = random.sample(danh_sach_cau, so_cau) if danh_sach_cau else []
    so_sua_nn, tong_diem_ngau_nhien = _tinh_rui_ro_duy_nhat(ngau_nhien)

    return {
        "so_cau_hoi": len(cac_cau_chon),
        "danh_sach_cau": [c.to_dict() for c in cac_cau_chon],
        "so_phat_bieu_duoc_sua": so_sua,
        "tong_rui_ro_giai_quyet": tong_diem_giai_quyet,
        "doi_chung_ngau_nhien": {
            "so_phat_bieu_duoc_sua": so_sua_nn,
            "tong_rui_ro_giai_quyet": tong_diem_ngau_nhien,
        },
        "hieu_qua_vuot_troi": round(tong_diem_giai_quyet - tong_diem_ngau_nhien, 4),
    }
