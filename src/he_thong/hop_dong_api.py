# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › Dịch vụ]
Làm gì   : Định nghĩa hình dạng dữ liệu mà dịch vụ Python trả về để máy chủ và giao diện
           TypeScript hiểu cùng một hợp đồng.
Vào → Ra : — (các lớp dữ liệu) → cấu trúc phản hồi: sức khoẻ, chép lời, bản nháp, cảnh báo,
           tiền kiểm BHYT
Đọc từ   : class PyNoteResponse là phản hồi bản nháp; validate_contract_keys() kiểm khoá hợp
           đồng
Mục lục (các hàm/lớp chính):
  class PyHealthResponse        Khuôn phản hồi kiểm tra sức khoẻ dịch vụ
  class PyNoteResponse          Khuôn phản hồi dựng bản nháp
  class PyPhatBieu              Khuôn một mệnh đề trong bản nháp
  class PyCanhBaoItem           Khuôn một cảnh báo lâm sàng
  class PyTranscribeResponse    Khuôn phản hồi chép âm thành văn bản
  class PyBhytPrecheckResponse  Khuôn phản hồi tiền kiểm BHYT
  validate_contract_keys()      Liệt kê trường bắt buộc còn thiếu trong phản hồi
Tên cũ   : api_contract.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────

Schema Contract chính thức giữa Python Core API (`src/he_thong/dich_vu_http.py`) và
Node/TypeScript BFF + Frontend (`web/src/types/api-contract.ts`).

Mọi thay đổi trường trả về của API lõi phải cập nhật đồng bộ tại đây và
trong `web/src/types/api-contract.ts`, sau đó kiểm tra bằng
`pytest tests/test_api_contract.py` và `tsx --test web/src/types/api-contract.test.ts`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


# ═══ class PyAsrInfo — Khuôn dữ liệu thông tin bộ chép âm ═════════════════════════════
# Nhà cung cấp và mô hình ASR.
class PyAsrInfo(TypedDict):
    nha_cung_cap: str
    mo_hinh: str


# ═══ class PyHealthResponse — Khuôn phản hồi kiểm tra sức khoẻ dịch vụ ════════════════
# Cho biết mô hình, adapter, thiết bị, chính sách cổng và ASR đang dùng.
class PyHealthResponse(TypedDict):
    ok: bool
    mo_hinh: str
    adapter_trich: Optional[str]
    da_nap_mo_hinh: bool
    cho_nap_mo_hinh: bool
    mo_hinh_xa: Optional[str]
    thiet_bi: str
    so_ca_bo_dem: int
    chinh_sach_cong: str
    bo_cham: str
    asr: PyAsrInfo
    tach_nguoi_noi: str


# ═══ class PySampleCaseItem — Khuôn một ca mẫu trong danh sách ════════════════════════
# Gồm id, bộ, tiêu đề và hội thoại đầu vào.
class PySampleCaseItem(TypedDict, total=False):
    id: str
    bo: str
    tieu_de: str
    input: str


# ═══ class PySampleCasesResponse — Khuôn phản hồi danh sách ca mẫu ════════════════════
class PySampleCasesResponse(TypedDict):
    ca: List[PySampleCaseItem]


# ═══ class PyDoanAsr — Khuôn một đoạn chép âm ═════════════════════════════════════════
# Có thời gian, lời gốc, người nói, vai và độ tin cậy ASR.
class PyDoanAsr(TypedDict, total=False):
    speaker_id: str
    text_original: str
    start_time: float
    end_time: float
    start_s: float
    end_s: float
    asr_confidence: float
    asr_review_required: bool


# ═══ class PyTranscribeResponse — Khuôn phản hồi chép âm thành văn bản ════════════════
# Chứa mã phiên và danh sách đoạn.
class PyTranscribeResponse(TypedDict, total=False):
    phien: str
    doan: List[PyDoanAsr]
    giay_xu_ly: float
    nguon: str
    tach_nguoi_noi: Optional[Dict[str, Any]]
    ghi_chu: Optional[str]


# ═══ class PyAssignRolesResponse — Khuôn phản hồi gán vai người nói ═══════════════════
class PyAssignRolesResponse(TypedDict):
    phien: str
    doan: List[PyDoanAsr]


# ═══ class PyPhatBieu — Khuôn một mệnh đề trong bản nháp ══════════════════════════════
# Các trường của mệnh đề lâm sàng trả về cho giao diện.
class PyPhatBieu(TypedDict, total=False):
    id: int
    noi_dung: str
    ten_chu_the: Optional[str]
    chu_the_id: Optional[int]
    do_chac_chan: str
    phu_dinh: bool
    tinh_huong: str
    moc_thoi_gian: Optional[str]
    bang_chung: List[int]
    trich_dan: List[str]
    thuoc: Optional[Dict[str, str]]


# ═══ class PyGhiChu — Khuôn ghi chú kèm bản nháp ══════════════════════════════════════
class PyGhiChu(TypedDict, total=False):
    id: int
    muc: str
    van: str
    ly_do: Optional[str]


# ═══ class PyCauHoi — Khuôn câu hỏi làm rõ gợi ý cho bác sĩ ═══════════════════════════
class PyCauHoi(TypedDict, total=False):
    van: str
    muc: str


# ═══ class PyCanhBaoItem — Khuôn một cảnh báo lâm sàng ════════════════════════════════
# Có mã, nhóm, mức độ, lý do, lượt thoại dẫn chứng và kết luận.
class PyCanhBaoItem(TypedDict, total=False):
    ma: str
    nhom: str
    nhom_ten: str
    tieu_de: str
    giai_thich: str
    ly_do: str
    luot: List[int]
    trich: List[str]
    muc_do: str
    bat_dinh: str
    ket_luan: str
    tin_cay: str
    anh_huong_trang_thai: bool
    phu: List[str]
    phu_tieu_de: List[str]
    bo_phat_hien: str


# ═══ class PyNoteResponse — Khuôn phản hồi dựng bản nháp ══════════════════════════════
# Gói mệnh đề, ghi chú, câu hỏi và cảnh báo trả cho giao diện.
class PyNoteResponse(TypedDict, total=False):
    id: str
    nhanh: str
    chinh_sach: str
    nguon: str
    giay_xu_ly: float
    input: str
    du_doan: str
    du_doan_khong_muc_phu: str
    phat_bieu: List[PyPhatBieu]
    ghi_chu: List[PyGhiChu]
    cau_hoi: List[PyCauHoi]
    so_can_xac_nhan: int
    canh_bao: Optional[Dict[str, Any]]
    lam_sang_nang_cao: Optional[Dict[str, Any]]
    worm_seq: Optional[int]
    worm_hash: Optional[str]


# ═══ class PyBhytIcd10Item — Khuôn một mã ICD-10 gợi ý cho BHYT ═══════════════════════
# Gồm mã, tên, nhóm và độ tin cậy.
class PyBhytIcd10Item(TypedDict, total=False):
    ma: str
    ten: str
    nhom: str
    do_tin_cay: float


# ═══ class PyBhytPrecheckResponse — Khuôn phản hồi tiền kiểm BHYT ═════════════════════
# Mã ICD-10, cảnh báo xuất toán, liều nhi và gói XML.
class PyBhytPrecheckResponse(TypedDict, total=False):
    ma_icd10_chinh: Optional[str]
    ma_icd10_kem_theo: List[str]
    canh_bao_xuat_toan_bhyt: List[Any]
    canh_bao_lieu_nhi_khoa: List[Any]
    canh_bao_da_thuoc_dong_tay_y: List[Any]
    bang_xml_130_4750: Dict[str, Any]
    dat_chuan_cdss_muc_6_7_tt54: bool
    icd10_chi_tiet: List[Any]
    canh_bao_xuat_toan: List[Any]
    goi_xml_1_5: Dict[str, Any]


# ═══ class PyOcrPhieuCuResponse — Khuôn phản hồi đọc phiếu cũ bằng OCR ════════════════
# Chỉ số, thuốc nhận diện và hiệu chỉnh liều.
class PyOcrPhieuCuResponse(TypedDict, total=False):
    chi_so: Dict[str, Any]
    thuoc_nhan_dien: List[Any]
    hieu_chinh_lieu: List[Any]


# ═══ class PyErrorAttributionResponse — Khuôn phản hồi quy kết lỗi ════════════════════
class PyErrorAttributionResponse(TypedDict):
    ok: bool
    quy_ket: Dict[str, Any]


# Bảng mô tả contract dùng để đối chiếu chéo Python <-> TypeScript trong unit test
CONTRACT_SCHEMA: Dict[str, Dict[str, List[str]]] = {
    "PyHealthResponse": {
        "required": [
            "ok",
            "mo_hinh",
            "adapter_trich",
            "da_nap_mo_hinh",
            "cho_nap_mo_hinh",
            "mo_hinh_xa",
            "thiet_bi",
            "so_ca_bo_dem",
            "chinh_sach_cong",
            "bo_cham",
            "asr",
            "tach_nguoi_noi",
        ],
    },
    "PySampleCasesResponse": {
        "required": ["ca"],
    },
    "PyTranscribeResponse": {
        "required": ["phien", "doan"],
    },
    "PyAssignRolesResponse": {
        "required": ["phien", "doan"],
    },
    "PyNoteResponse": {
        "required": [
            "id",
            "nhanh",
            "nguon",
            "du_doan",
            "phat_bieu",
            "ghi_chu",
        ],
    },
    "PyBhytPrecheckResponse": {
        "required": ["ma_icd10_chinh", "ma_icd10_kem_theo", "canh_bao_xuat_toan_bhyt", "icd10_chi_tiet"],
    },
    "PyOcrPhieuCuResponse": {
        "required": ["chi_so", "thuoc_nhan_dien", "hieu_chinh_lieu"],
    },
    "PyErrorAttributionResponse": {
        "required": ["ok", "quy_ket"],
    },
}


# ═══ validate_contract_keys() — Liệt kê trường bắt buộc còn thiếu trong phản hồi ══════
# Rỗng nghĩa là hợp lệ; tên hợp đồng lạ thì báo KeyError.
def validate_contract_keys(payload: Dict[str, Any], contract_name: str) -> List[str]:
    """Trả về danh sách các trường bắt buộc bị thiếu trong payload (rỗng = hợp lệ)."""
    spec = CONTRACT_SCHEMA.get(contract_name)
    if not spec:
        raise KeyError(f"Không tìm thấy contract {contract_name}")
    if not isinstance(payload, dict):
        return list(spec["required"])
    return [field for field in spec["required"] if field not in payload]
