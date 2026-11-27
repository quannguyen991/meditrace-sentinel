"""[Âm thanh › Chép lời]
Làm gì   : Chạy so hai bộ chép lời và chọn ra những đoạn hai bên bất đồng ở từ quan trọng để
           người duyệt xem kỹ.
Vào → Ra : hai ASRResult (chính, phụ) → danh sách đoạn bất đồng kèm chữ của hai bên
Đọc từ   : compare() so hai kết quả theo độ chồng lấn mốc thời gian và từ quan trọng
Mục lục (các hàm/lớp chính):
  compare()  So hai bản chép lời và đánh dấu bất đồng từ khoá
Gọi tới  : audio/asr/critical_tokens, audio/asr/schemas
Dùng bởi : audio/pipeline
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chạy hai nhà cung cấp ASR trên cùng âm thanh và đánh dấu các bất đồng trọng yếu.

Nếu hai bản chép lời khác nhau ở tên thuốc, liều, con số, phủ định, biểu thức
thời gian, trạng thái dùng thuốc hoặc đối tượng đang được nhắc tới, đoạn đó nhận
``asr_review_required = True`` kèm cả hai ứng viên. Hệ thống KHÔNG BAO GIỜ tự chọn một:
con người nghe lại và quyết định.
"""

from __future__ import annotations

from typing import Any

from . import critical_tokens as ct
from .schemas import ASRResult


# ─── _overlap() — Tính độ chồng lấn giữa hai khoảng thời gian ─────────────────────────
def _overlap(a0, a1, b0, b1) -> float:
    if None in (a0, a1, b0, b1):
        return 0.0
    return max(0.0, min(a1, b1) - max(a0, b0))


# ═══ compare() — So hai bản chép lời và đánh dấu bất đồng từ khoá ═════════════════════
# Mỗi đoạn chính có từ khoá khác bản phụ thì ghi cả hai ứng viên để người nghe lại; hệ
# thống không tự chọn.
def compare(primary: ASRResult, secondary: ASRResult) -> list[dict[str, Any]]:
    """-> mỗi đoạn chính có các token trọng yếu khác với bản chép lời
    phụ trong cùng cửa sổ thời gian thì ra một mục duyệt."""
    items = []
    co_moc = all(s.start_time is not None for s in primary.segments + secondary.segments)
    for s in primary.segments:
        if co_moc:
            ben_kia = [x for x in secondary.segments
                       if _overlap(s.start_time, s.end_time, x.start_time, x.end_time) > 0]
        else:                                  # không có mốc: số ca bản chép
            ben_kia = secondary.segments if len(primary.segments) == 1 else []
        chu_kia = " ".join(x.text for x in ben_kia)
        loai = ct.khac_nhau(ct.trich(s.text), ct.trich(chu_kia))
        if loai:
            items.append({
                "segment_id": s.segment_id,
                "asr_review_required": True,
                "reason": ct.LY_DO[loai[0]],
                "reasons": sorted({ct.LY_DO[k] for k in loai}),
                "start_time": s.start_time, "end_time": s.end_time,
                "candidates": [
                    {"provider": primary.provider, "model": primary.model, "text": s.text},
                    {"provider": secondary.provider, "model": secondary.model, "text": chu_kia},
                ],
            })
    return items
