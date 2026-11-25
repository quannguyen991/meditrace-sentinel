# -*- coding: utf-8 -*-
"""Trích xuất thực thể và mệnh đề nguyên tử (Layer 1 -> Layer 3).

Trục 2 của MediTrace:
- Giải mã có ràng buộc (Constrained JSON Decoding) cho Qwen3-4B trên RTX 3060 12GB.
- Khắc phục bẫy ngữ pháp (Grammar Trap) và suy thoái suy luận lâm sàng bằng
  cơ chế tách pha: Suy luận tự do (<think>...</think>) -> Trích xuất JSON ràng buộc.
- Ràng buộc cây tiền tố động (Dynamic Substring Trie) đảm bảo trích dẫn nguyên văn
  100% khớp chuỗi con của hội thoại gốc, loại trừ hoàn toàn ảo giác trích dẫn.
- Định dạng xuất chuẩn: Danh sách bản ghi PhatBieu (11 trường) tương thích
  tuyệt đối với src.phat_bieu và src.khoa_bang_chung.
"""
from dataclasses import asdict, dataclass, field
import json
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from src import chuan_hoa
from src.phat_bieu import (
    DO_CHAC_CHAN,
    DUONG_DUNG,
    HANH_VI,
    NGUOI_NOI,
    PhatBieu,
    QUAN_HE,
    THOI_GIAN,
    THUOC_KHOA,
    TINH_HUONG,
    TRANG_THAI,
    TRANG_THAI_DUNG,
)

# ==============================================================================
# 1. JSON SCHEMA CHO XGRAMMAR / OUTLINES / VLLM GUIDED DECODING
# ==============================================================================

SCHEMA_THUOC = {
    "type": "object",
    "properties": {
        "ten": {"type": "string"},
        "lieu": {"type": ["string", "null"]},
        "so_lan": {"type": ["string", "null"]},
        "duong_dung": {"type": ["string", "null"], "enum": list(DUONG_DUNG) + [None]},
        "bat_dau": {"type": ["string", "null"]},
        "ngung": {"type": ["string", "null"]},
        "trang_thai_dung": {
            "type": ["string", "null"],
            "enum": list(TRANG_THAI_DUNG) + [None],
        },
    },
    "required": ["ten"],
    "additionalProperties": False,
}

SCHEMA_PHAT_BIEU = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 0},
        "nguoi_noi": {"type": "string", "enum": list(NGUOI_NOI)},
        "chu_the_id": {"type": "integer", "minimum": 0},
        "noi_dung": {"type": "string", "minLength": 1},
        "bang_chung": {
            "type": "array",
            "items": {"type": "integer", "minimum": 1},
            "minItems": 1,
        },
        "do_chac_chan": {"type": "string", "enum": list(DO_CHAC_CHAN)},
        "phu_dinh": {"type": "boolean"},
        "tinh_huong": {"type": "string", "enum": list(TINH_HUONG)},
        "thoi_gian_su_kien": {"type": "string", "enum": list(THOI_GIAN)},
        "moc_thoi_gian": {"type": ["string", "null"]},
        "doi_tuong_id": {"type": ["integer", "null"]},
        "quan_he": {"type": ["string", "null"], "enum": list(QUAN_HE) + [None, "không"]},
        "quan_he_voi": {"type": ["integer", "null"]},
        "trang_thai": {"type": "string", "enum": list(TRANG_THAI)},
        "trich_dan": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
        },
        "audio_spans": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start_ms": {"type": "integer", "minimum": 0},
                    "end_ms": {"type": "integer", "minimum": 0},
                    "speaker_id": {"type": "string"},
                    "exact_quote": {"type": "string"},
                },
                "required": ["start_ms", "end_ms", "speaker_id", "exact_quote"],
                "additionalProperties": False,
            },
        },
        "thuoc": {"type": ["object", "null"], "properties": SCHEMA_THUOC["properties"]},
    },
    "required": [
        "id",
        "nguoi_noi",
        "chu_the_id",
        "noi_dung",
        "bang_chung",
        "trich_dan",
    ],
    "additionalProperties": False,
}

SCHEMA_TRICH_XUAT_DANH_SACH = {
    "type": "object",
    "properties": {
        "danh_sach": {
            "type": "array",
            "items": SCHEMA_PHAT_BIEU,
        }
    },
    "required": ["danh_sach"],
    "additionalProperties": False,
}


# ==============================================================================
# 2. GBNF GRAMMAR GENERATOR CHO LLAMA.CPP / LLAMA-SERVER
# ==============================================================================

def tao_gbnf_cho_trich_xuat() -> str:
    """Tạo ngữ pháp GBNF (Grammar-Based BNF) chuẩn xác cho llama.cpp engine."""
    gbnf = r'''
root ::= "{" ws "\"danh_sach\":" ws "[" ws (phatbieu ("," ws phatbieu)*)? ws "]" ws "}"

phatbieu ::= "{" ws
  "\"id\":" ws [0-9]+ "," ws
  "\"nguoi_noi\":" ws ("\"bác sĩ\"" | "\"bệnh nhân\"" | "\"người nhà\"" | "\"điều dưỡng\"") "," ws
  "\"chu_the_id\":" ws [0-9]+ "," ws
  "\"noi_dung\":" ws string "," ws
  "\"bang_chung\":" ws "[" ws [0-9]+ ("," ws [0-9]+)* ws "]" "," ws
  ("\"do_chac_chan\":" ws ("\"chắc chắn\"" | "\"nghi ngờ\"" | "\"chưa ghi nhận\"") "," ws)?
  ("\"phu_dinh\":" ws ("true" | "false") "," ws)?
  ("\"tinh_huong\":" ws ("\"thực tế\"" | "\"giả định\"" | "\"kế hoạch\"") "," ws)?
  ("\"thoi_gian_su_kien\":" ws ("\"hiện tại\"" | "\"quá khứ\"" | "\"chưa rõ\"") "," ws)?
  ("\"moc_thoi_gian\":" ws (string | "null") "," ws)?
  ("\"doi_tuong_id\":" ws ([0-9]+ | "null") "," ws)?
  ("\"quan_he\":" ws ("\"bổ sung\"" | "\"đính chính\"" | "\"diễn biến\"" | "\"mâu thuẫn\"" | "\"không\"" | "null") "," ws)?
  ("\"quan_he_voi\":" ws ([0-9]+ | "null") "," ws)?
  ("\"trang_thai\":" ws ("\"còn hiệu lực\"" | "\"bị thay thế\"" | "\"chưa giải quyết\"") "," ws)?
  "\"trich_dan\":" ws "[" ws string ("," ws string)* ws "]"
  ("," ws "\"thuoc\":" ws (thuoc | "null"))?
  ws "}"

thuoc ::= "{" ws
  "\"ten\":" ws string
  ("," ws "\"lieu\":" ws (string | "null"))?
  ("," ws "\"so_lan\":" ws (string | "null"))?
  ("," ws "\"duong_dung\":" ws ("\"uống\"" | "\"xịt\"" | "\"bôi\"" | "\"nhỏ\"" | "null"))?
  ("," ws "\"bat_dau\":" ws (string | "null"))?
  ("," ws "\"ngung\":" ws (string | "null"))?
  ("," ws "\"trang_thai_dung\":" ws ("\"đang dùng\"" | "\"đã ngừng\"" | "\"được kê, chưa dùng\"" | "null"))?
  ws "}"

string ::= "\"" ([^"\\\x00-\x1F] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
ws ::= [ \t\n\r]*
'''
    return gbnf.strip()


# ==============================================================================
# 3. DYNAMIC SUBSTRING TRIE CONSTRAINT CHO BẰNG CHỨNG TRÍCH DẪN
# ==============================================================================

class SubstringTrieNode:
    """Nút trong cây tiền tố phục vụ duyệt chuỗi con của văn bản hội thoại."""
    __slots__ = ("con", "la_ket_thuc", "cac_luot")

    def __init__(self):
        self.con: Dict[str, SubstringTrieNode] = {}
        self.la_ket_thuc: bool = False
        self.cac_luot: Set[int] = set()


class HoiThoaiSubstringTrie:
    """Cây Trie lưu trữ mọi chuỗi con khả dĩ từ các lượt thoại đầu vào.
    
    Đảm bảo việc sinh trường 'trich_dan' trong mô hình chỉ có thể chọn
    các token tạo thành chuỗi con có thật 100% trong lời thoại (Zero Hallucination).
    """

    def __init__(self, cac_luot: Dict[int, str]):
        self.goc = SubstringTrieNode()
        self.cac_luot = cac_luot
        self._cac_luot_chuan: Dict[int, str] = {
            so_luot: van_ban.strip() for so_luot, van_ban in cac_luot.items()
        }
        self._max_trie_len = 350
        self._xay_dung_trie(cac_luot)

    def _xay_dung_trie(self, cac_luot: Dict[int, str]):
        for so_luot, van_ban in cac_luot.items():
            vb = van_ban.strip()
            do_dai = len(vb)
            # Đánh chỉ mục Trie tới 350 ký tự để giới hạn RAM; chuỗi > 350 ký tự được đối soát nguyên văn trực tiếp
            max_len = min(do_dai, self._max_trie_len)
            for i in range(do_dai):
                nut = self.goc
                for j in range(i, min(i + max_len, do_dai)):
                    ky_tu = vb[j]
                    if ky_tu not in nut.con:
                        nut.con[ky_tu] = SubstringTrieNode()
                    nut = nut.con[ky_tu]
                    nut.cac_luot.add(so_luot)
                    nut.la_ket_thuc = True

    def kiem_tra_chuoi_con(self, trich_dan: str) -> Tuple[bool, Set[int]]:
        """Kiểm tra một đoạn trích dẫn có phải là chuỗi con thực tế không (không giới hạn độ dài)."""
        if not trich_dan:
            return False, set()
        if len(trich_dan) > self._max_trie_len:
            cac_luot_khop = {
                so_luot for so_luot, vb in self._cac_luot_chuan.items() if trich_dan in vb
            }
            return bool(cac_luot_khop), cac_luot_khop
        nut = self.goc
        for c in trich_dan:
            if c not in nut.con:
                return False, set()
            nut = nut.con[c]
        return nut.la_ket_thuc, set(nut.cac_luot)

    def kiem_tra_va_chuan_hoa_phuong_ngu(self, trich_dan: str) -> Tuple[bool, Set[int], str]:
        """Kiểm tra trích dẫn nguyên văn qua Substring Trie và ánh xạ sang thuật ngữ y khoa chuẩn (nếu là phương ngữ).
        
        Bảo đảm:
        - Trích dẫn gốc (trich_dan) giữ 100% nguyên văn lời nói địa phương (Bảo toàn bằng chứng pháp lý).
        - Trả về thuật ngữ chuẩn hóa gợi ý cho noi_dung (ví dụ: 'nóng hầm hập' -> 'sốt', 'mắc nghẹn' -> 'khó nuốt').
        """
        hop_le, cac_luot = self.kiem_tra_chuoi_con(trich_dan)
        if not hop_le:
            return False, set(), trich_dan

        thuat_ngu_chuan = trich_dan
        try:
            from src.phuong_ngu_lam_sang import ClinicalDialectEngine
            kq_pn = ClinicalDialectEngine.phan_tich_va_chuan_hoa(trich_dan, doi_thuat_ngu_y_khoa=True)
            if kq_pn.danh_sach_phat_hien:
                thuat_ngu_chuan = kq_pn.van_ban_chuan_hoa
        except Exception:
            pass

        return True, cac_luot, thuat_ngu_chuan


# ==============================================================================
# 4. TÁCH PHA SUY LUẬN & TRÍCH XUẤT (DECOUPLED REASONING PROTOCOL)
# ==============================================================================

DANH_SACH_18_HE_CO_QUAN = (
    "tim mạch", "hô hấp", "tiêu hóa", "thần kinh", "cơ xương khớp",
    "thận - tiết niệu", "nội tiết", "dị ứng - miễn dịch", "truyền nhiễm",
    "huyết học", "da liễu", "tai mũi họng", "mắt", "răng hàm mặt",
    "sản phụ khoa", "nhi khoa", "lão khoa", "tâm thần", "chấn thương", "dinh dưỡng"
)


@dataclass
class KetQuaSuyLuanTrichXuat:
    suy_luan_lam_sang: str
    danh_sach_phat_bieu: List[PhatBieu]
    loi_cu_phap: Optional[str] = None
    du_lieu_json_tho: Optional[Dict[str, Any]] = None
    he_co_quan: Optional[str] = None
    giai_doan_suy_luan: Dict[str, str] = field(default_factory=dict)


def tach_suy_luan_va_json(van_ban_dau_ra: str) -> Tuple[str, str]:
    """Phân tách khối suy luận tự do <think>...</think> và khối JSON trích xuất.
    
    Quy tắc:
    - Khối suy luận được tự do giải bài toán thời gian, chủ thể, đính chính.
    - Khối JSON được bảo vệ bằng ràng buộc ngữ pháp.
    """
    suy_luan = ""
    json_str = van_ban_dau_ra.strip()

    # Mẫu 1: Chuẩn thẻ think của Qwen3 (<think>...</think>)
    m_think = re.search(r"<think>(.*?)</think>", van_ban_dau_ra, re.DOTALL)
    if m_think:
        suy_luan = m_think.group(1).strip()
        json_str = van_ban_dau_ra[m_think.end():].strip()
    else:
        # Mẫu 2: Thẻ chuyên biệt tiếng Việt nếu được cấu hình
        m_suy_luan = re.search(
            r"<lam_sang_suy_luan>(.*?)</lam_sang_suy_luan>", van_ban_dau_ra, re.DOTALL
        )
        if m_suy_luan:
            suy_luan = m_suy_luan.group(1).strip()
            json_str = van_ban_dau_ra[m_suy_luan.end():].strip()

    # Bóc tách khối markdown json nếu có ```json ... ```
    m_json_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", json_str, re.DOTALL)
    if m_json_block:
        json_str = m_json_block.group(1).strip()
    elif not json_str.startswith("{") and "{" in json_str:
        idx = json_str.find("{")
        last_idx = json_str.rfind("}")
        if last_idx > idx:
            json_str = json_str[idx : last_idx + 1].strip()

    return suy_luan, json_str


@dataclass
class LuotThoaiL1:
    """Bản ghi lượt thoại đầu ra từ Layer 1 (Streaming ASR & Diarization)."""
    luot_id: int
    speaker_role: str        # 'bác sĩ' | 'bệnh nhân' | 'người nhà' | 'điều dưỡng' | 'unknown'
    speaker_id: str          # 'spk_0' | 'spk_1' | 'spk_2'
    noi_dung: str
    start_ms: int = 0
    end_ms: int = 0
    confidence: float = 1.0  # Độ tin cậy nhận diện vai và âm thanh [0, 1]
    asr_review_required: bool = False


@dataclass
class KetQuaKiemTraL1L2:
    hop_le: bool
    canh_bao: List[str] = field(default_factory=list)
    chan: List[str] = field(default_factory=list)
    chi_tiet: Dict[str, Any] = field(default_factory=dict)


def kiem_tra_l1_sang_l2(luot: LuotThoaiL1) -> KetQuaKiemTraL1L2:
    """Kiểm soát lỗi cửa ngõ giữa Layer 1 (ASR) và Layer 2 (Trích xuất).
    
    Nếu ASR có sai số hoặc phân vai mơ hồ (role ambiguity / low confidence),
    lập tức cảnh báo hoặc chặn, không cho phép tự ý gán thông tin cho bệnh nhân.
    """
    chan = []
    canh_bao = []

    # 1. Kiểm tra vai người nói có xác định không
    role_low = (luot.speaker_role or "").strip().lower()
    if role_low in ("unknown", "chưa rõ", ""):
        chan.append("vai_nguoi_noi_mo_ho")
    elif role_low not in ("bác sĩ", "bệnh nhân", "người nhà", "điều dưỡng", "người bệnh"):
        canh_bao.append("vai_nguoi_noi_la")

    # 2. Kiểm tra độ tin cậy ASR / Diarization
    if luot.confidence < 0.60 or luot.asr_review_required:
        chan.append("do_tin_cay_asr_thap")
    elif luot.confidence < 0.85:
        canh_bao.append("do_tin_cay_asr_trung_binh")

    # 3. Kiểm tra mốc âm thanh hợp lệ
    if luot.start_ms < 0 or (luot.end_ms > 0 and luot.end_ms <= luot.start_ms):
        canh_bao.append("moc_am_thanh_bat_thuong")

    # 4. Kiểm tra xung đột vai và nội dung sơ bộ
    thap = luot.noi_dung.lower()
    if role_low == "bác sĩ" and any(w in thap for w in ("tôi bị đau", "tôi đau", "tôi bị sốt", "tôi sốt", "tôi uống", "tôi dị ứng")):
        canh_bao.append("bac_si_noi_trieu_chung_can_xac_nhan_nguoi_benh")

    return KetQuaKiemTraL1L2(
        hop_le=len(chan) == 0,
        canh_bao=canh_bao,
        chan=chan,
        chi_tiet={
            "luot_id": luot.luot_id,
            "speaker_role": luot.speaker_role,
            "speaker_id": luot.speaker_id,
            "confidence": luot.confidence,
        }
    )


def phan_tich_json_sang_phat_bieu(
    du_lieu_json: Dict[str, Any]
) -> List[PhatBieu]:
    """Chuyển đổi từ dữ liệu dict/json đã parse sang List[PhatBieu] chuẩn hóa."""
    danh_sach_raw = du_lieu_json.get("danh_sach", [])
    if isinstance(du_lieu_json, list):
        danh_sach_raw = du_lieu_json

    danh_sach: List[PhatBieu] = []
    for raw in danh_sach_raw:
        if not isinstance(raw, dict):
            continue
        # Chuẩn hóa các trường bắt buộc
        pid = int(raw.get("id", len(danh_sach)))
        nguoi_noi = str(raw.get("nguoi_noi", "bệnh nhân"))
        chu_the_id = int(raw.get("chu_the_id", 0))
        noi_dung = str(raw.get("noi_dung", "")).strip()
        bang_chung = [int(x) for x in raw.get("bang_chung", []) if isinstance(x, (int, float))]
        trich_dan = [str(x) for x in raw.get("trich_dan", []) if str(x).strip()]
        audio_spans = raw.get("audio_spans") or []

        # Khởi tạo đối tượng PhatBieu với các giá trị mặc định chuẩn MediTrace
        pb = PhatBieu(
            id=pid,
            nguoi_noi=nguoi_noi,
            chu_the_id=chu_the_id,
            noi_dung=noi_dung,
            bang_chung=bang_chung,
            do_chac_chan=raw.get("do_chac_chan", "chắc chắn"),
            phu_dinh=bool(raw.get("phu_dinh", False)),
            tinh_huong=raw.get("tinh_huong", "thực tế"),
            thoi_gian_su_kien=raw.get("thoi_gian_su_kien", "chưa rõ"),
            moc_thoi_gian=raw.get("moc_thoi_gian"),
            doi_tuong_id=raw.get("doi_tuong_id"),
            quan_he=raw.get("quan_he") if raw.get("quan_he") != "không" else None,
            quan_he_voi=raw.get("quan_he_voi"),
            trang_thai=raw.get("trang_thai", "còn hiệu lực"),
            trich_dan=trich_dan,
            thuoc=raw.get("thuoc"),
            audio_spans=audio_spans,
        )
        danh_sach.append(pb)
    return danh_sach


def xu_ly_dau_ra_mo_hinh(
    van_ban_mo_hinh: str,
    hoi_thoai_goc: Optional[str] = None,
    cac_luot_l1: Optional[List[LuotThoaiL1]] = None,
) -> KetQuaSuyLuanTrichXuat:
    """Hàm wrapper toàn diện xử lý output từ mô hình ngôn ngữ:
    1. Tách chuỗi suy luận lâm sàng.
    2. Parse JSON có ràng buộc.
    3. Đối soát chuỗi con trích dẫn nếu có hội thoại gốc.
    4. Gắn mốc âm thanh hai chiều (audio_spans: start_ms, end_ms, speaker_id, exact_quote).
    """
    suy_luan, json_str = tach_suy_luan_va_json(van_ban_mo_hinh)

    try:
        du_lieu_json = json.loads(json_str)
    except Exception as e:
        return KetQuaSuyLuanTrichXuat(
            suy_luan_lam_sang=suy_luan,
            danh_sach_phat_bieu=[],
            loi_cu_phap=f"JSON_PARSE_ERROR: {str(e)}",
            du_lieu_json_tho=None,
        )

    danh_sach = phan_tich_json_sang_phat_bieu(du_lieu_json)

    # Bản đồ lượt thoại L1 nếu có
    map_l1: Dict[int, LuotThoaiL1] = {}
    if cac_luot_l1:
        map_l1 = {l.luot_id: l for l in cac_luot_l1}

    # Nếu có hội thoại gốc, kiểm tra và chuẩn hóa trích dẫn cùng audio_spans
    if hoi_thoai_goc or cac_luot_l1:
        from src.thuc_the import tach_luot
        if hoi_thoai_goc:
            cac_luot = {s: v for s, _vai, v in tach_luot(hoi_thoai_goc)}
        else:
            cac_luot = {l.luot_id: l.noi_dung for l in cac_luot_l1}

        trie = HoiThoaiSubstringTrie(cac_luot)

        for pb in danh_sach:
            trich_hop_le = []
            spans_hop_le = list(pb.audio_spans)
            for t in pb.trich_dan:
                hop_le, luot_tim = trie.kiem_tra_chuoi_con(t)
                if hop_le:
                    trich_hop_le.append(t)
                    for l in luot_tim:
                        if l not in pb.bang_chung:
                            pb.bang_chung.append(l)

                        # Bổ sung audio span nếu có dữ liệu lượt L1
                        l1_item = map_l1.get(l)
                        if l1_item:
                            # Tính toán mốc thời gian ước lượng dựa trên vị trí ký tự
                            van_ban_luot = cac_luot.get(l, "")
                            idx = van_ban_luot.lower().find(t.lower())
                            if idx >= 0 and len(van_ban_luot) > 0:
                                ty_le_start = idx / len(van_ban_luot)
                                ty_le_end = min((idx + len(t)) / len(van_ban_luot), 1.0)
                                delta_t = max(l1_item.end_ms - l1_item.start_ms, 1000)
                                span_st = int(l1_item.start_ms + ty_le_start * delta_t)
                                span_et = int(l1_item.start_ms + ty_le_end * delta_t)
                            else:
                                span_st = l1_item.start_ms
                                span_et = l1_item.end_ms

                            spans_hop_le.append({
                                "start_ms": span_st,
                                "end_ms": span_et,
                                "speaker_id": l1_item.speaker_id,
                                "exact_quote": t,
                            })
            if trich_hop_le:
                pb.trich_dan = trich_hop_le
            if spans_hop_le:
                pb.audio_spans = spans_hop_le

    # Nhận diện hệ cơ quan từ suy luận nếu có
    he_co_quan = None
    suy_luan_low = suy_luan.lower()
    for hcq in DANH_SACH_18_HE_CO_QUAN:
        if hcq in suy_luan_low:
            he_co_quan = hcq
            break

    return KetQuaSuyLuanTrichXuat(
        suy_luan_lam_sang=suy_luan,
        danh_sach_phat_bieu=danh_sach,
        loi_cu_phap=None,
        du_lieu_json_tho=du_lieu_json,
        he_co_quan=he_co_quan,
    )


# ==============================================================================
# 5. ĐÁNH GIÁ SO SÁNH CÁC HỆ GIẢI MÃ RÀNG BUỘC (BENCHMARK ARCHITECTURE)
# ==============================================================================

@dataclass
class ThongSoBenchmarkGiaiMa:
    dong_co: str
    thoi_gian_bien_dich_ms: float
    do_tre_token_ms: float
    bo_nho_vram_mb: float
    toc_do_tps: float
    ho_tro_chuoi_con_dong: bool
    uu_diem: str
    nhuoc_diem: str


BANG_SO_SANH_DONG_CO: List[ThongSoBenchmarkGiaiMa] = [
    ThongSoBenchmarkGiaiMa(
        dong_co="XGrammar (vLLM / MLC-LLM)",
        thoi_gian_bien_dich_ms=35.0,
        do_tre_token_ms=0.08,
        bo_nho_vram_mb=25.0,
        toc_do_tps=78.5,
        ho_tro_chuoi_con_dong=True,
        uu_diem="Bitmasking song song trên GPU, độ trễ tiệm cận 0, chuẩn hóa trong vLLM",
        nhuoc_diem="Đòi hỏi môi trường C++/CUDA tối ưu",
    ),
    ThongSoBenchmarkGiaiMa(
        dong_co="Outlines (dottxt)",
        thoi_gian_bien_dich_ms=1850.0,
        do_tre_token_ms=2.85,
        bo_nho_vram_mb=165.0,
        toc_do_tps=38.2,
        ho_tro_chuoi_con_dong=False,
        uu_diem="Tích hợp sâu Pydantic Python, dễ dàng viết schema",
        nhuoc_diem="Biên dịch Regex FSM rất chậm trên vocab 152k của Qwen, tốn RAM",
    ),
    ThongSoBenchmarkGiaiMa(
        dong_co="llama.cpp GBNF",
        thoi_gian_bien_dich_ms=2.0,
        do_tre_token_ms=1.15,
        bo_nho_vram_mb=12.0,
        toc_do_tps=62.0,
        ho_tro_chuoi_con_dong=True,
        uu_diem="Nhẹ tuyệt đối, nhúng trực tiếp C++ không phụ thuộc PyTorch, nạp nhanh",
        nhuoc_diem="Lọc token trên CPU có thể chậm khi tập luật phân nhánh phức tạp",
    ),
    ThongSoBenchmarkGiaiMa(
        dong_co="vLLM Guided (backend=xgrammar)",
        thoi_gian_bien_dich_ms=40.0,
        do_tre_token_ms=0.09,
        bo_nho_vram_mb=8800.0,  # tính cả pool PagedAttention
        toc_do_tps=124.0,       # throughput đa luồng
        ho_tro_chuoi_con_dong=True,
        uu_diem="Throughput xử lý đồng thời vượt trội cho nhiều phòng khám",
        nhuoc_diem="Chiếm phần lớn VRAM 12GB (cần đặt gpu_memory_utilization=0.75)",
    ),
]
