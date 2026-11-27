"""[Âm thanh]
Làm gì   : Đổi bản chép lời đã được duyệt sang dạng hội thoại mà đường ống dựng bản nháp đọc
           được.
Vào → Ra : danh sách đoạn lời đã duyệt (người nói, chữ) → dict hội thoại cho đường ống
           MediTrace
Đọc từ   : to_meditrace() là hàm duy nhất của tệp
Mục lục (các hàm/lớp chính):
  to_meditrace()  Đổi lời thoại đã duyệt thành đầu vào cho lõi MediTrace
Dùng bởi : audio/pipeline, he_thong/dich_vu_http
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bộ chuyển đổi từ bản chép lời âm thanh đã duyệt sang đầu vào MediTrace hiện có.

Lõi MediTrace đọc một chuỗi ``input`` với mỗi lượt một dòng, ví dụ
``Bác sĩ: Cô ho bao lâu rồi?``. Bộ chuyển đổi này tạo ra chuỗi đó kèm danh sách
lượt, và giữ siêu dữ liệu âm thanh TÁCH RIÊNG để lược đồ lõi không bị đụng tới.

Văn bản dùng: ``text_original`` — những gì bộ nhận dạng đã nghe, hoặc những gì người duyệt đã gõ
khi chỉnh sửa. ``text_normalized`` không bao giờ được gửi vào lõi.
"""

from __future__ import annotations

from typing import Any

ROLE_TO_CORE = {
    "doctor": "bac_si",
    "nurse": "dieu_duong",
    "patient": "benh_nhan",
    "family_member": "nguoi_nha",
    "other": "nguoi_khac",
    "unknown": "unknown",
    "bác sĩ": "bac_si",
    "điều dưỡng": "dieu_duong",
    "bệnh nhân": "benh_nhan",
    "người nhà": "nguoi_nha",
    "người khác": "nguoi_khac",
}
# Nhãn vai trong chuỗi `input` của bộ dữ liệu MediTrace
ROLE_LABEL = {
    "doctor": "Bác sĩ",
    "nurse": "Điều dưỡng",
    "patient": "Bệnh nhân",
    "family_member": "Người nhà",
    "other": "Người khác",
    "bác sĩ": "Bác sĩ",
    "điều dưỡng": "Điều dưỡng",
    "bệnh nhân": "Bệnh nhân",
    "người nhà": "Người nhà",
    "người khác": "Người khác",
}


# ═══ to_meditrace() — Đổi lời thoại đã duyệt thành đầu vào cho lõi MediTrace ══════════
# Trả chuỗi input mỗi lượt một dòng, danh sách lượt và siêu dữ liệu âm thanh riêng.
# strict=True từ chối đoạn còn vai unknown.
def to_meditrace(segments: list[dict[str, Any]], strict: bool = False) -> dict[str, Any]:
    """-> {"input": str, "turns": [...], "metadata": [...]}.

    ``strict=True`` từ chối mọi đoạn mà vai vẫn là ``unknown``: lõi
    không bao giờ được đoán ai đã nói.
    """
    turns, metadata, lines = [], [], []
    for index, segment in enumerate(segments, 1):
        text = (segment.get("text_original") or "").strip()
        raw_role = segment.get("speaker_role", "unknown")
        role = str(raw_role.value if hasattr(raw_role, "value") else raw_role).strip().lower() or "unknown"
        if strict and role not in ROLE_LABEL:
            raise ValueError("speaker_unknown")
        turns.append({"luot": index, "nguoi_noi": ROLE_TO_CORE.get(role, "unknown"), "noi_dung": text})
        lines.append(f"{ROLE_LABEL.get(role, 'Chưa rõ')}: {text}")
        metadata.append({"luot": index, "utterance_id": index,
                         "segment_id": segment.get("segment_id"), "speaker_id": segment.get("speaker_id"),
                         "speaker_role": role, "audio_start": segment.get("start_time"),
                         "audio_end": segment.get("end_time"), "asr_confidence": segment.get("asr_confidence"),
                         "asr_provider": segment.get("asr_provider"), "asr_model": segment.get("asr_model"),
                         "edited": segment.get("edited", False)})
    return {"input": "\n".join(lines), "turns": turns, "metadata": metadata}
