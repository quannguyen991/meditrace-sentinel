# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Chạy mọi bộ phát hiện, gộp cảnh báo trùng, chọn cảnh báo chính và áp chính sách D
           để quyết định dòng nào bị chặn.
Vào → Ra : bản nháp + lời thoại (+ kết quả kiểm căn cứ) → dict cảnh báo theo dòng, cảnh báo
           toàn ca, trạng thái D
Đọc từ   : chay() là điểm vào của lớp; chon_chinh() chọn cảnh báo chính; trang_thai_D() áp
           chính sách D
Mục lục (các hàm/lớp chính):
  chay()                Chạy toàn bộ lớp cảnh báo cho một ca
  chon_chinh()          Chọn cảnh báo chính cho một mệnh đề
  trang_thai_D()        Quyết định trạng thái mệnh đề theo chính sách D
  phan_tang_canh_bao()  Xếp một cảnh báo vào một trong ba tầng
  phan_tang_ket_qua()   Tổng hợp ba tầng cảnh báo cho cả ca
  ly_do_chan_D()        Lấy lý do chuyển sang cần xác nhận theo chính sách D
  chon_hien_thi()       Ngân sách hiển thị: chia cảnh báo một mệnh đề thành hiện / gập
  hien_thi_ca()         Áp ngân sách hiển thị cho cả ca
  bo_sung_ngan_sach()   Thêm canh_bao_hien / canh_bao_gap cho bản JSON lưu trước đó
  to_dict()             Chuyển kết quả cảnh báo sang dạng JSON
Gọi tới  : canh_bao/asr, canh_bao/lam_sang, canh_bao/loai, canh_bao/phat_hien,
           canh_bao/toan_ca, duong_ong/b4_kiem_can_cu, duong_ong/b5_xep_cho_cong_rui_ro
Dùng bởi : do_luong/do_canh_bao, do_luong/do_cay_loi, duong_ong/chay_duong_ong,
           he_thong/dich_vu_http, he_thong/dieu_phoi_cac_chot_an_toan
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chạy mọi bộ phát hiện, GỘP cảnh báo trùng, chọn cảnh báo CHÍNH, áp chính sách D.

CHỐNG BÁO ĐỘNG TRÀN LAN (đặc tả mục 38-39). "Bố tôi bị hen" ghi thành "bệnh
nhân bị hen" có thể kích cả WRONG_SUBJECT, FAMILY_PATIENT_MIXUP, UNSUPPORTED...
Giao diện chỉ hiện MỘT cảnh báo chính cho mỗi nguyên nhân; phần còn lại là mã phụ:
  1. cùng MÃ từ nhiều bộ phát hiện -> gộp làm một (hợp lượt, hợp trích dẫn)
  2. cùng NHÓM -> mã ưu tiên cao nhất là chính, mã khác thành `phu`
  3. khác nhóm và ĐỦ NẶNG để đổi trạng thái -> giữ riêng (tối đa 2), còn lại -> `phu`

CHÍNH SÁCH D (mới, chưa dùng để đo). Chính sách C (`cong_rui_ro.CHINH_SACH`) vẫn là
chính sách của mọi con số đã báo cáo; D chỉ bật khi gọi rõ `chinh_sach="D"`.
    bị thay thế      trang_thai 'bị thay thế' — không vào thân, giữ dấu vết
    cần xác nhận     khoa chan, HOAC dang mau thuan, HOAC co canh bao du nang
    đã kiểm chứng    còn lại (vẫn có thể mang cảnh báo nhẹ để bác sĩ lưu ý)
"""
from typing import Dict, List, Optional

from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.canh_bao import asr, lam_sang, phat_hien, toan_ca
from src.canh_bao.loai import (CAN_XEM, CAO, LOAI, LOI_PHAT_HIEN, LUON_CAO, NGHI_RUI_RO, ON_DINH, PHIEN_BAN, THAP,
                               CanhBao, _HANG, la_ma_goi_y)

CHINH_SACH_D = "D-2026-09-24"
DA_KIEM_CHUNG = "đã kiểm chứng"
CAN_XAC_NHAN = "cần xác nhận"
BI_THAY_THE = "bị thay thế"

TANG_CHAN_NGAY = "CHAN_NGAY"
TANG_CAN_XEM_XET = "CAN_XEM_XET"
TANG_TINH_LUOC = "TINH_LUOC"

_MA_DUOC_LY_BAO_VE = {
    "CONTRAINDICATION",
    "CROSS_ALLERGY",
    "DOSE_OVER_MAX",
    "DRUG_INTERACTION",
}
_MA_BO_SOT_QUAN_TRONG = {
    "OMITTED_ALLERGY",
    "OMITTED_MEDICATION",
    "OMITTED_ANSWER",
    "OMITTED_NEGATION",
    "OMITTED_CORRECTION",
    "OMITTED_PLAN",
    "OMITTED_NUMERIC_VALUE",
    "OMITTED_DURATION",
    "AMBIGUOUS_LAY_TERM",
}
_MA_TINH_LUOC = {
    "POSSIBLE_IMPORTANT_OMISSION",
    "OMITTED_UNCERTAINTY",
    "APPROXIMATION_LOST",
    "RANGE_COLLAPSED",
    "EVIDENCE_CONTEXT_MISSING",
    "DOCTOR_STATEMENT_AS_PATIENT_FACT",
    "CLINICALLY_IRRELEVANT",
}


# ═══ phan_tang_canh_bao() — Xếp một cảnh báo vào một trong ba tầng ════════════════════
# Chặn ngay, cần xem xét hoặc tinh lược, nhằm giảm mệt mỏi vì quá nhiều cảnh báo.
def phan_tang_canh_bao(c: CanhBao) -> str:
    """Phân tầng cảnh báo thành 3 mức chống mệt mỏi cảnh báo (alert fatigue triage):
    - CHAN_NGAY: Lỗi/nguy cơ cao phải chặn ngay hoặc buộc xác nhận.
    - CAN_XEM_XET: Cảnh báo lâm sàng/dược lý/bỏ sót quan trọng cần bác sĩ rà soát.
    - TINH_LUOC: Nhiễu chất lượng/mơ hồ/giá trị thấp trên hồ sơ sạch được tinh lược khỏi luồng chính.
    """
    if c.anh_huong_trang_thai:
        return TANG_CHAN_NGAY
    if _la_goi_y(c):
        return TANG_TINH_LUOC
    if c.ma in _MA_DUOC_LY_BAO_VE and c.ket_luan != CAN_XEM and c.muc_do == CAO:
        return TANG_CHAN_NGAY
    if c.ma in _MA_DUOC_LY_BAO_VE or c.nhom == "CLINICAL_KNOWLEDGE":
        return TANG_CAN_XEM_XET
    if c.ma in _MA_BO_SOT_QUAN_TRONG:
        return TANG_CAN_XEM_XET
    if c.ma.startswith("POSSIBLE_") and c.ma.endswith("_TRANSCRIPTION_ERROR"):
        return TANG_CAN_XEM_XET
    if c.ma == "SPEAKER_SUBJECT_MISMATCH":
        if c.loai_tt in ("di_ung", "thuoc", "thuoc_nti"):
            return TANG_CAN_XEM_XET
        if c.bat_dinh == CAO:
            return TANG_TINH_LUOC
    if c.nhom == "QUALITY" or c.ma in _MA_TINH_LUOC:
        return TANG_TINH_LUOC
    if c.ket_luan == CAN_XEM and c.tin_cay != ON_DINH:
        return TANG_TINH_LUOC
    if c.muc_do == THAP and not c.anh_huong_trang_thai and c.ket_luan == CAN_XEM:
        return TANG_TINH_LUOC
    return TANG_CAN_XEM_XET


# ═══ phan_tang_ket_qua() — Tổng hợp ba tầng cảnh báo cho cả ca ════════════════════════
# Trả về danh sách mỗi tầng kèm thống kê số lượng và tỷ lệ tinh lược.
def phan_tang_ket_qua(theo_p: Dict[int, dict], toan: List[CanhBao]) -> Dict[str, object]:
    """Tổng hợp phân tầng 3 mức cho toàn ca mà không làm thay đổi cấu trúc theo_phat_bieu/toan_ca."""
    chan_ngay: List[CanhBao] = []
    can_xem_xet: List[CanhBao] = []
    tinh_luoc: List[CanhBao] = []

    tat_ca: List[CanhBao] = []
    for cb in theo_p.values():
        tat_ca.extend(cb.get("tat_ca") or [])
    tat_ca.extend(toan or [])

    for c in tat_ca:
        tang = phan_tang_canh_bao(c)
        if tang == TANG_CHAN_NGAY:
            chan_ngay.append(c)
        elif tang == TANG_CAN_XEM_XET:
            can_xem_xet.append(c)
        else:
            tinh_luoc.append(c)

    tong = len(tat_ca)
    return {
        TANG_CHAN_NGAY: chan_ngay,
        TANG_CAN_XEM_XET: can_xem_xet,
        TANG_TINH_LUOC: tinh_luoc,
        "thong_ke": {
            "tong": tong,
            "chan_ngay": len(chan_ngay),
            "can_xem_xet": len(can_xem_xet),
            "tinh_luoc": len(tinh_luoc),
            "ty_le_tinh_luoc": round(len(tinh_luoc) / tong, 3) if tong else 0.0,
        },
    }

_KL = {LOI_PHAT_HIEN: 2, NGHI_RUI_RO: 1, CAN_XEM: 0}


# ─── _gop_cung_ma() — Gộp các cảnh báo cùng mệnh đề và cùng mã ────────────────────────
# Hợp lượt và câu trích, lấy kết luận mạnh nhất, mức nghiêm trọng cao nhất.
def _gop_cung_ma(ds: List[CanhBao]) -> List[CanhBao]:
    theo = {}
    for c in ds:
        k = (c.phat_bieu_id, c.ma)
        if k not in theo:
            theo[k] = c
            continue
        a = theo[k]
        a.luot = sorted(set(a.luot) | set(c.luot))
        a.trich = a.trich + [t for t in c.trich if t not in a.trich]
        if c.bo_phat_hien not in a.bo_phat_hien.split("+"):
            a.bo_phat_hien += "+" + c.bo_phat_hien
        if _KL[c.ket_luan] > _KL[a.ket_luan]:
            a.ket_luan, a.ly_do = c.ket_luan, c.ly_do
        if _HANG[c.bat_dinh] < _HANG[a.bat_dinh]:
            a.bat_dinh = c.bat_dinh
        if _HANG[c.muc_do] > _HANG[a.muc_do]:
            a.muc_do = c.muc_do
    return list(theo.values())


# ─── _khoa_sap() — Khoá sắp xếp để chọn cảnh báo chính ────────────────────────────────
# Ưu tiên cảnh báo đổi được trạng thái, rồi theo thứ tự ưu tiên và mức nghiêm trọng.
def _khoa_sap(c: CanhBao):
    return (not c.anh_huong_trang_thai, LOAI[c.ma].uu_tien, -_HANG[c.muc_do], _HANG[c.bat_dinh])


# ─── Ngân sách cảnh báo (Task 5 plan 27/11, V11 plan 28/11) ───────────────────────────
# Mỗi mệnh đề chỉ HIỆN tối đa `ngan_sach` cảnh báo; phần còn lại GẬP sau nút "Xem thêm N gợi ý".
# Không bao giờ gập: mức `cao`, kết luận `loi_phat_hien`, mã LUON_CAO. Luôn gập: mã gợi ý
# (MA_GOI_Y_CHINH_XAC_THAP) và cảnh báo `can_xem` của bộ phát hiện thử nghiệm (cùng luật với
# chon_chinh). Chỉ đổi phần HIỂN THỊ — `tat_ca`, chính/khác và chính sách D giữ nguyên.
NGAN_SACH_MAC_DINH = 2

# Độ chính xác cùng loại theo mã, chép từ docs/ket-qua/canh-bao.json (24/09/2026, 4 bộ
# thach_thuc/*_phat_trien). Chỉ dùng để XẾP THỨ TỰ hiển thị; mã chưa đo xếp như 0.
CHINH_XAC_CUNG_LOAI = {
    "SPEAKER_SUBJECT_MISMATCH": 0.058, "UNSUPPORTED_INFORMATION": 0.31, "WRONG_SUBJECT": 0.5,
    "CONTRADICTION_UNRESOLVED": 0.866, "SUBJECT_AMBIGUOUS": 0.59, "DUPLICATE_INFORMATION": 0.056,
    "IMPORTANT_MODIFIER_DROPPED": 0.0, "CERTAINTY_INCREASED": 0.42, "POSSIBLE_NEGATION_ERROR": 0.319,
    "FAMILY_PATIENT_MIXUP": 0.231, "PAST_CURRENT_CONFUSION": 0.344, "NEGATION_FLIP": 0.684,
    "FABRICATED_QUOTE": 0.176, "ROUTE_MISMATCH": 0.875, "DOSE_MISMATCH": 1.0, "EVIDENCE_CONTEXT_MISSING": 0.143,
    "DOCTOR_STATEMENT_AS_PATIENT_FACT": 0.0, "APPROXIMATION_LOST": 1.0, "UNSUPPORTED_FACT_COMBINATION": 1.0,
    "NEGATION_SCOPE_ERROR": 1.0, "TEMPORAL_MISMATCH": 0.25, "CONTRADICTORY_INFORMATION": 0.5,
    "CORRECTION_NOT_APPLIED": 1.0, "WRONG_EVIDENCE": 0.0, "PLAN_AS_FACT": 0.5, "FREQUENCY_MISMATCH": 1.0,
    "QUESTION_AS_FACT": 0.0, "OVER_NORMALIZATION": 1.0, "SEMANTIC_DUPLICATE": 0.0,
    "FAMILY_STATEMENT_AS_CLINICIAN_PLAN": 1.0, "FABRICATED_MEDICATION": 0.0, "FABRICATED_ALLERGY": 0.0,
}


def _g(c, k):
    """Đọc trường của cảnh báo, dạng CanhBao hoặc dict (bản ghi đã lưu qua to_dict)."""
    if isinstance(c, dict):
        if k == "tin_cay" and k not in c:
            return LOAI[c["ma"]].tin_cay if c.get("ma") in LOAI else ON_DINH
        return c.get(k)
    return getattr(c, k)


def _la_goi_y(c) -> bool:
    # Trên dị ứng / thuốc mã gợi ý vẫn chặn D và vẫn hiện (loai.LOAI_GOI_Y_VAN_CHAN): cảnh báo
    # đã đổi trạng thái thì không được gập.
    return la_ma_goi_y(_g(c, "ma"), _g(c, "ket_luan"), _g(c, "loai_tt"))


def _luon_hien(c) -> bool:
    return _g(c, "muc_do") == CAO or _g(c, "ket_luan") == LOI_PHAT_HIEN or _g(c, "ma") in LUON_CAO


def _ha_ma_goi_y(ds) -> None:
    """Hạ mức mã gợi ý xuống `thap` (tại chỗ). Không đụng mã LUON_CAO, không đụng loi_phat_hien."""
    for c in ds:
        if _la_goi_y(c) and c.ma not in LUON_CAO:
            c.muc_do = THAP


def _khoa_hien_thi(c):
    """Thứ tự hiển thị xác định: mức nặng → kết luận → độ chính xác đã đo → ưu tiên → mã → lượt."""
    ma = _g(c, "ma")
    return (-_HANG.get(_g(c, "muc_do"), 0), -_KL.get(_g(c, "ket_luan"), 0),
            -CHINH_XAC_CUNG_LOAI.get(ma, 0.0), LOAI[ma].uu_tien if ma in LOAI else 99, ma,
            tuple(_g(c, "luot") or ()))


# ═══ chon_hien_thi() — Chia cảnh báo của một mệnh đề thành phần hiện và phần gập ═════
def chon_hien_thi(ds, ngan_sach: int = NGAN_SACH_MAC_DINH):
    """-> (hien, gap). `ds`: cảnh báo của MỘT mệnh đề (hoặc cảnh báo toàn ca), CanhBao hoặc dict.
    Cảnh báo luôn-hiện chiếm ngân sách trước và không bao giờ bị gập, kể cả khi vượt ngân sách."""
    luon, gap_san, con = [], [], []
    for c in sorted(ds, key=_khoa_hien_thi):
        if _la_goi_y(c):
            gap_san.append(c)
        elif _luon_hien(c):
            luon.append(c)
        elif _g(c, "ket_luan") == CAN_XEM and _g(c, "tin_cay") != ON_DINH:
            gap_san.append(c)
        else:
            con.append(c)
    cho = max(0, ngan_sach - len(luon))
    hien = luon + con[:cho]
    gap = sorted(con[cho:] + gap_san, key=_khoa_hien_thi)
    return hien, gap


# ═══ hien_thi_ca() — Áp ngân sách cho cả ca (mỗi mệnh đề + nhóm cảnh báo toàn ca) ═════
def hien_thi_ca(kq: dict, ngan_sach: int = NGAN_SACH_MAC_DINH) -> dict:
    """-> {"theo_phat_bieu": {id: (hien, gap)}, "toan_ca": (hien, gap)} từ kết quả `chay()`.
    Cảnh báo toàn ca (bỏ sót) là một nhóm riêng, cùng ngân sách như một mệnh đề."""
    return {"theo_phat_bieu": {i: chon_hien_thi(v["tat_ca"], ngan_sach) for i, v in kq["theo_phat_bieu"].items()},
            "toan_ca": chon_hien_thi(kq.get("toan_ca") or [], ngan_sach)}


# ═══ bo_sung_ngan_sach() — Thêm canh_bao_hien / canh_bao_gap cho bản JSON đã có ═══════
def bo_sung_ngan_sach(d: dict, ngan_sach: int = NGAN_SACH_MAC_DINH) -> dict:
    """Bản ghi lưu trước Task 5 (to_dict cũ) chưa có hai trường: tính từ `tat_ca`/`toan_ca`.
    Đã có `toan_ca_ngan_sach` thì trả nguyên. Sửa tại chỗ và trả lại chính `d`."""
    if not isinstance(d, dict) or "toan_ca_ngan_sach" in d:
        return d
    for v in (d.get("theo_phat_bieu") or {}).values():
        hien, gap = chon_hien_thi([c for c in (v.get("tat_ca") or []) if isinstance(c, dict)], ngan_sach)
        v["canh_bao_hien"], v["canh_bao_gap"] = hien, gap
    hien, gap = chon_hien_thi([c for c in (d.get("toan_ca") or []) if isinstance(c, dict)], ngan_sach)
    d["toan_ca_ngan_sach"] = {"canh_bao_hien": hien, "canh_bao_gap": gap}
    d["ngan_sach"] = ngan_sach
    return d


# ═══ chon_chinh() — Chọn cảnh báo chính cho một mệnh đề ═══════════════════════════════
# Trả về chính, tối đa 2 cảnh báo khác nhóm có sức đổi trạng thái, còn lại là mã phụ.
def chon_chinh(ds: List[CanhBao]) -> dict:
    """-> {chinh, khac: [..], phu: [ma..], tat_ca: [..]} cho MỘT phát biểu."""
    if not ds:
        return {"chinh": None, "khac": [], "phu": [], "tat_ca": []}
    ds = sorted(ds, key=_khoa_sap)
    # Cảnh báo "cần xem" của bộ phát hiện THỬ NGHIỆM không bao giờ là cảnh báo chính:
    # IMPORTANT_MODIFIER_DROPPED báo 84 lần, 0 lần trúng lỗi (đo 24/09/2026) — hiện nó
    # là tạo báo động giả. Vẫn giữ trong `tat_ca` để ghi nhật ký và đo tiếp.
    hien = [c for c in ds if not (c.ket_luan == CAN_XEM and c.tin_cay != ON_DINH)]
    if not hien:
        return {"chinh": None, "khac": [], "phu": [], "tat_ca": ds}
    ds = hien + [c for c in ds if c not in hien]
    chinh, khac, phu = ds[0], [], []
    nhom_da = {chinh.nhom}
    for c in hien[1:]:
        if c.nhom not in nhom_da and c.anh_huong_trang_thai and len(khac) < 2:
            khac.append(c)
            nhom_da.add(c.nhom)
        else:
            phu.append(c.ma)
    chinh.phu = sorted(set(chinh.phu) | {m for m in phu if m != chinh.ma})
    return {"chinh": chinh, "khac": khac, "phu": chinh.phu, "tat_ca": ds}


# ═══ trang_thai_D() — Quyết định trạng thái mệnh đề theo chính sách D ═════════════════
# Bị thay thế, cần xác nhận hoặc đã kiểm chứng, kèm lý do.
def trang_thai_D(p, cb: dict, kq_khoa=None) -> tuple:
    """-> (trạng thái, lý do) theo chính sách D."""
    if getattr(p, "trang_thai", "còn hiệu lực") == "bị thay thế":
        return BI_THAY_THE, "đã được thông tin mới thay thế"
    if kq_khoa is not None and kq_khoa.chan:
        c = cb["chinh"]
        return CAN_XAC_NHAN, (c.ly_do if c else "khoá bằng chứng chặn")
    if getattr(p, "trang_thai", "còn hiệu lực") == "chưa giải quyết":
        return CAN_XAC_NHAN, "hai nguồn mâu thuẫn, chưa xác nhận"
    for c in [cb["chinh"]] + cb["khac"]:
        if c is not None and c.anh_huong_trang_thai:
            return CAN_XAC_NHAN, f"{LOAI[c.ma].tieu_de}: {c.ly_do}"
    return DA_KIEM_CHUNG, ""


# ═══ chay() — Chạy toàn bộ lớp cảnh báo cho một ca ════════════════════════════════════
# Chạy mọi bộ phát hiện, gộp, chọn cảnh báo chính, áp chính sách D và phân tầng.
def chay(ps, hoi_thoai: str, kk: Optional[dict] = None, meta_asr: Optional[dict] = None) -> dict:
    """Cảnh báo cho MỘT ca. `kk` = kết quả `khoa_bang_chung.khoa_ca` (tính lại nếu
    không truyền). `meta_asr` = {số lượt: {asr_confidence, nguoi_noi_chua_chac}}
    khi lời thoại đến từ chép âm; không có thì không sinh cảnh báo chép âm."""
    from src.duong_ong import b4_kiem_can_cu as khoa_bang_chung
    ctx = phat_hien.NguCanh(hoi_thoai)
    if kk is None:
        kk = khoa_bang_chung.khoa_ca(ps, hoi_thoai)
    kq_theo_id = {k.id: k for k in kk["ket_qua"]}
    loai = {p.id: cong_rui_ro.loai_thong_tin(p) for p in ps}
    cac_sua = phat_hien.tim_dinh_chinh(ctx)

    tho: List[CanhBao] = []
    for p in ps:
        if getattr(p, "trang_thai", "còn hiệu lực") == "bị thay thế":
            continue
        tho += phat_hien.tu_khoa(ctx, p, kq_theo_id.get(p.id), loai[p.id])
        for f in phat_hien.BO_PHAT_HIEN:
            tho += f(ctx, p, loai[p.id])
        tho += phat_hien.dinh_chinh(ctx, p, loai[p.id], cac_sua)
    tho += toan_ca.mau_thuan(ctx, ps, loai)
    tho += toan_ca.ghi_lap(ctx, ps, loai)
    tho += toan_ca.dinh_chinh_nguoc(ctx, ps, loai)
    tho += lam_sang.quet(ctx, ps)
    if meta_asr:
        tho += asr.canh_bao(ctx, ps, meta_asr, loai)
    gop = _gop_cung_ma(tho)
    _ha_ma_goi_y(gop)

    theo_p: Dict[int, dict] = {}
    trang_thai: Dict[int, dict] = {}
    for p in ps:
        cb = chon_chinh([c for c in gop if c.phat_bieu_id == p.id])
        theo_p[p.id] = cb
        tt, ly = trang_thai_D(p, cb, kq_theo_id.get(p.id))
        trang_thai[p.id] = {"trang_thai": tt, "ly_do": ly}
    toan = toan_ca.bo_sot(ctx, kk.get("doan_chua_ghi", []), ps, kk.get("cap_hoi_dap_chua_ghi", []))
    phan_tang = phan_tang_ket_qua(theo_p, toan)
    return {
        "phien_ban": PHIEN_BAN,
        "chinh_sach": CHINH_SACH_D,
        "theo_phat_bieu": theo_p,
        "toan_ca": toan,
        "trang_thai_D": trang_thai,
        "cac_dinh_chinh": [{"luot": d["luot"], "cu": d["cu"].chu, "moi": d["moi"].chu} for d in cac_sua],
        "phan_tang": phan_tang,
    }


# ═══ ly_do_chan_D() — Lấy lý do chuyển sang cần xác nhận theo chính sách D ════════════
# Trả về {id mệnh đề: lý do} cho bước sinh bệnh án.
def ly_do_chan_D(kq: dict) -> Dict[int, str]:
    """{id: lý do} để `sinh_benh_an.sinh` đưa sang CẦN XÁC NHẬN theo chính sách D."""
    return {i: v["ly_do"] for i, v in kq["trang_thai_D"].items() if v["trang_thai"] == CAN_XAC_NHAN}


# ═══ to_dict() — Chuyển kết quả cảnh báo sang dạng JSON ═══════════════════════════════
# Dùng cho bản ghi kết quả, dịch vụ và giao diện.
def to_dict(kq: dict) -> dict:
    """Bản JSON — cho bản ghi kết quả, dịch vụ và giao diện."""
    def cb(c):
        return c.to_dict() if c is not None else None
    pt_raw = kq.get("phan_tang")
    if not isinstance(pt_raw, dict):
        pt_raw = phan_tang_ket_qua(kq.get("theo_phat_bieu") or {}, kq.get("toan_ca") or [])
    hs = hien_thi_ca(kq)
    hien_ca, gap_ca = hs["toan_ca"]
    return {
        "phien_ban": kq["phien_ban"], "chinh_sach": kq["chinh_sach"],
        "theo_phat_bieu": {str(i): {"chinh": cb(v["chinh"]), "khac": [cb(c) for c in v["khac"]],
                                    "phu": v["phu"], "tat_ca": [cb(c) for c in v["tat_ca"]],
                                    "canh_bao_hien": [cb(c) for c in hs["theo_phat_bieu"][i][0]],
                                    "canh_bao_gap": [cb(c) for c in hs["theo_phat_bieu"][i][1]]}
                           for i, v in kq["theo_phat_bieu"].items()},
        "toan_ca": [cb(c) for c in kq["toan_ca"]],
        "toan_ca_ngan_sach": {"canh_bao_hien": [cb(c) for c in hien_ca], "canh_bao_gap": [cb(c) for c in gap_ca]},
        "ngan_sach": NGAN_SACH_MAC_DINH,
        "trang_thai_D": {str(i): v for i, v in kq["trang_thai_D"].items()},
        "cac_dinh_chinh": kq["cac_dinh_chinh"],
        "phan_tang": {
            TANG_CHAN_NGAY: [cb(c) for c in pt_raw.get(TANG_CHAN_NGAY, [])],
            TANG_CAN_XEM_XET: [cb(c) for c in pt_raw.get(TANG_CAN_XEM_XET, [])],
            TANG_TINH_LUOC: [cb(c) for c in pt_raw.get(TANG_TINH_LUOC, [])],
            "thong_ke": dict(pt_raw.get("thong_ke") or {}),
        },
    }
