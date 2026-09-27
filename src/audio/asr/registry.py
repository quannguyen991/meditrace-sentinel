"""ASR provider registry: pick a provider by configuration, never by code edits.

    ASR_PROVIDER=phowhisper      ASR_MODEL=vinai/PhoWhisper-medium   ASR_DEVICE=cuda
    ASR_PROVIDER=faster_whisper  ASR_MODEL=small
    ASR_PROVIDER=sidecar

Local-first: in PROCESSING_MODE=local a provider with ``external = True`` is refused.
Fallback: a failing provider is replaced ONLY if ALLOW_ASR_FALLBACK=true, and only by
the provider named in ASR_FALLBACK_PROVIDER — never silently by a cloud service.
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


def register(name: str, factory: Callable[..., ASRProvider]) -> None:
    """Them nha cung cap moi (FutureASRProvider) ma khong sua pipeline."""
    _REGISTRY[name] = factory


def names() -> list[str]:
    return sorted(_REGISTRY)


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


def from_settings(s) -> ASRProvider:
    return create(s.asr_provider, s.asr_model, s.asr_device, s.asr_revision, s.processing_mode)


def transcribe(settings, audio_path, primary: Optional[ASRProvider] = None) -> tuple[ASRResult, dict]:
    """Chay nha cung cap chinh; loi thi chi du phong khi cau hinh cho phep.

    -> (ket qua, thong tin: provider da dung, co du phong khong, loi goc neu co).
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
