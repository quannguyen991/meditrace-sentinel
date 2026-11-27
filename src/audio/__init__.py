"""[Âm thanh]
Làm gì   : Gom các bước biến ghi âm buổi khám thành lời thoại theo lượt để bác sĩ duyệt,
           chạy hoàn toàn tại chỗ.
Gọi tới  : audio/models
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đường ống tiếp nhận âm thanh cho MediTrace Sentinel.

Gói này cố ý dừng ở bản chép lời đã được duyệt. Nó không suy ra
dữ kiện lâm sàng và không thay thế lõi MediTrace hiện có.
"""

from .models import SessionStatus, SpeakerRole, TranscriptSegment

__all__ = ["SessionStatus", "SpeakerRole", "TranscriptSegment"]
