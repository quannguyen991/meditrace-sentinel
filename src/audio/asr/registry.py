"""[Âm thanh › Chép lời]
Làm gì   : Chọn bộ chép lời theo tên trong cấu hình để đổi nhà cung cấp mà không sửa mã.
Vào → Ra : tên nhà cung cấp hoặc cài đặt + đường dẫn WAV → ASRProvider hoặc (ASRResult,
           thông tin chạy)
Đọc từ   : from_settings() dựng bộ chép theo cấu hình; transcribe() chạy chép và so bộ phụ
Mục lục (các hàm/lớp chính):
  create()         Tạo nhà cung cấp chép lời theo tên cấu hình
  from_settings()  Tạo nhà cung cấp chép lời từ AudioSettings
  transcribe()     Chép lời bằng nhà cung cấp chính, dự phòng nếu cho phép
  register()       Đăng ký thêm một nhà cung cấp chép lời mới
  names()          Liệt kê tên các nhà cung cấp chép lời đã đăng ký
Gọi tới  : audio/asr/base, audio/asr/faster_whisper_provider, audio/asr/phowhisper_provider,
           audio/asr/schemas, audio/asr/sidecar_provider
Dùng bởi : audio/pipeline
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Sổ đăng ký nhà cung cấp ASR: chọn nhà cung cấp bằng cấu hình, không bao giờ bằng sửa mã.

    ASR_PROVIDER=phowhisper      ASR_MODEL=vinai/PhoWhisper-medium   ASR_DEVICE=cuda
    ASR_PROVIDER=faster_whisper  ASR_MODEL=small
    ASR_PROVIDER=sidecar

Ưu tiên cục bộ: ở PROCESSING_MODE=local, nhà cung cấp có ``external = True`` bị từ chối.
Dự phòng: nhà cung cấp lỗi chỉ được thay NẾU ALLOW_ASR_FALLBACK=true, và chỉ bằng
nhà cung cấp nêu trong ASR_FALLBACK_PROVIDER — không bao giờ âm thầm chuyển sang dịch vụ đám mây.
"""

from __future__ import annotations

from typing import Callable, Optional

from .base import ASRProvider
from .faster_whisper_provider import FasterWhisperProvider
from .phowhisper_provider import PhoWhisperProvider
from .schemas import ASRError, ASRResult
from .sidecar_provider import SidecarProvider

_REGISTRY: dict[str, Callable[..., ASRProvider]] = {
    "phowhisper": PhoWhisperProvider,
    "faster_whisper": FasterWhisperProvider,
    "sidecar": SidecarProvider,
}

_SIZES = ("tiny", "base", "small", "medium", "large")


# ═══ register() — Đăng ký thêm một nhà cung cấp chép lời mới ══════════════════════════
# Không cần sửa pipeline.
def register(name: str, factory: Callable[..., ASRProvider]) -> None:
    """Thêm nhà cung cấp mới (FutureASRProvider) mà không sửa pipeline."""
    _REGISTRY[name] = factory


# ═══ names() — Liệt kê tên các nhà cung cấp chép lời đã đăng ký ═══════════════════════
def names() -> list[str]:
    return sorted(_REGISTRY)


# ═══ create() — Tạo nhà cung cấp chép lời theo tên cấu hình ═══════════════════════════
# Ở chế độ local từ chối nhà cung cấp gửi âm thanh ra ngoài.
def create(name: str, model: Optional[str] = None, device: Optional[str] = None,
           revision: Optional[str] = None, processing_mode: str = "local") -> ASRProvider:
    if name not in _REGISTRY:
        raise ASRError("asr_provider_unknown", name)
    kw = {}
    if name == "phowhisper":
        if model:
            kw["model"] = f"vinai/PhoWhisper-{model}" if model in _SIZES else model
        if revision:
            kw["revision"] = revision
        if device:
            kw["device"] = device
    elif name == "faster_whisper":
        if model:
            kw["model"] = model
        if device:
            kw["device"] = device
    prov = _REGISTRY[name](**kw)
    if prov.external and processing_mode == "local":
        raise ASRError("asr_provider_external_blocked", name)
    return prov


# ═══ from_settings() — Tạo nhà cung cấp chép lời từ AudioSettings ═════════════════════
def from_settings(s) -> ASRProvider:
    return create(s.asr_provider, s.asr_model, s.asr_device, s.asr_revision, s.processing_mode)


# ═══ transcribe() — Chép lời bằng nhà cung cấp chính, dự phòng nếu cho phép ═══════════
# Chỉ chuyển sang nhà cung cấp dự phòng khi ALLOW_ASR_FALLBACK bật; trả kết quả kèm
# thông tin đã dùng bên nào.
def transcribe(settings, audio_path, primary: Optional[ASRProvider] = None) -> tuple[ASRResult, dict]:
    """Chạy nhà cung cấp chính; lỗi thì chỉ dự phòng khi cấu hình cho phép.

    -> (kết quả, thông tin: provider đã dùng, có dự phòng không, lỗi gốc nếu có).
    """
    prov = primary or from_settings(settings)
    try:
        return prov.transcribe(audio_path), {"used": prov.name, "fallback": False}
    except ASRError as err:
        if not (settings.allow_asr_fallback and settings.asr_fallback_provider):
            raise
        fb = create(settings.asr_fallback_provider, settings.asr_fallback_model,
                    settings.asr_device, None, settings.processing_mode)
        res = fb.transcribe(audio_path)
        res.notes.append(f"du phong sang {fb.name} vi {prov.name} loi: {err.code}")
        return res, {"used": fb.name, "fallback": True, "primary_error": err.to_dict()}
