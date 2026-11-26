# -*- coding: utf-8 -*-
"""Dich vu HTTP chay TAI CHO cho giao dien MediTrace (D:/meditrace-sentinel).

VI SAO CO TEP NAY. Giao dien do AI Studio dung san goi thang Gemini cho ca bon viec
(chep am, viet ho so, sua ho so, hoi dap). Nhu vay la gui hoi thoai kham benh ra may chu
ngoai, va mo hinh cua du an khong duoc dung den. Tep nay thay cho lop do: giao dien goi
vao day, day goi dung duong ong cua du an (`src/audio` cho am thanh, `src.nhanh` nhanh
C_khoa cho ho so). Khong co loi goi ra ngoai internet o day.

    python -m src.dich_vu --cong 8765

Duong:
  GET  /api/suc-khoe                     tinh trang: mo hinh, thiet bi, phien ban
  POST /api/chep-am    {am_thanh_base64, dinh_dang, ten_tep}
                                         -> phien am thanh + cac doan chep, VAI = unknown
  POST /api/gan-vai    {phien, vai: {speaker_1: "doctor", ...}}
  GET  /api/phien/<id>                   doan chep hien tai cua mot phien
  POST /api/ho-so      {input | phien, nhanh}
                                         -> ban nhap + tung menh de kem bang chung
  GET  /api/ca-mau[?bo=...]              danh sach ca da chay truoc (demo khong can GPU)

XAC THUC (26/11/2026). Moi duong /api/* tru GET /api/suc-khoe deu doi header
`X-MediTrace-Internal-Token` (so bang hmac.compare_digest):
  - co bien MEDITRACE_INTERNAL_TOKEN -> dung khoa do;
  - khong co -> luc khoi dong (main) nap khoa tu tep data/.meditrace_internal_token, chua co thi
    sinh ngau nhien va ghi vao tep do (in DUONG DAN ra log, khong in khoa). Phia web dat
    MEDITRACE_INTERNAL_TOKEN = noi dung tep nay;
  - khong co khoa nao (vd lop May dung truc tiep khong qua main) -> tu choi (fail-closed).
  Header Host phai la localhost / 127.0.0.1 / ::1 / dia chi --dia-chi hoac MEDITRACE_ALLOWED_HOSTS
  (chong DNS rebinding). Content-Length am / khong phai so nguyen -> 400, qua GIOI_HAN_THAN -> 413.
  `user_id` trong than yeu cau chi la KHAI BAO cua ben goi: ghi WORM duoi chu the da xac thuc
  ("dich_vu_noi_bo/khai_bao:<id>"), khong ghi thang nhu danh tinh da xac minh.
  Goi may xa (--mo-hinh-xa) gui kem MEDITRACE_REMOTE_TOKEN (khong co thi MEDITRACE_INTERNAL_TOKEN).

MAY XA. Hoi thoai duoc khu dinh danh truoc khi gui; con sot dau vet PII (kiem_tra_con_sot)
thi TU CHOI gui (loi khu_dinh_danh_chua_sach). Thong tin benh nhan / xet nghiem KHONG gui ra
may xa; lop `lam_sang_nang_cao` va `canh_bao` luon tinh lai TAI CHO sau khi co ket qua.

MOI DAP AN DEU CO TRUONG `nguon`:
  "mo_hinh"     khau trich chay ngay bang mo hinh cua du an
  "bo_dem"      khau trich lay tu tep dem da chay truoc, khau sinh chay ngay
  "chay_truoc"  ban ghi ket qua da chay tu truoc, khong tinh lai gi
Giao dien PHAI hien nhan nay. Khong duoc de nguoi xem tuong mot ban ghi cu la may vua chay.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hmac
import io
import json
import os
import re
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src import duong_dan

NHANH_CHO_PHEP = ("C_khoa", "C_khoa_v2", "C_khoa_hoi", "C", "B")
MAX_TOKEN = 3072
GIOI_HAN_AM_THANH = 40 * 1024 * 1024        # 40 MB
# Than JSON toi da: am thanh 40 MB sau base64 ~54 MB + phan con lai
GIOI_HAN_THAN = GIOI_HAN_AM_THANH * 2
TEP_KHOA_NOI_BO = duong_dan.GOC_DU_AN / "data" / ".meditrace_internal_token"
CHU_THE_NOI_BO = "dich_vu_noi_bo"            # chu the da xac thuc bang khoa noi bo
HOST_MAC_DINH = ("localhost", "127.0.0.1", "::1")
# Hang nhe cho /api/suc-khoe de KHONG keo cham_he_thong -> sai_so -> scipy luc khoi dong
PHIEN_BAN_BO_CHAM = "2026-09-22"
CHINH_SACH_CONG_MAC_DINH = "C-2026-09-22"
THU_MUC_PHIEN = duong_dan.GOC_DU_AN / "data" / "audio" / "phien-dich-vu"
THU_MUC_CHAY_TRUOC = duong_dan.GOC_DU_AN / "kaggle-ra" / "the-he-8-chinh-sach-C"
THU_MUC_BO = duong_dan.GOC_DU_AN / "kaggle-ra" / "the-he-8"


class LoiDichVu(Exception):
    def __init__(self, ma, thong_diep, code=400):
        super().__init__(thong_diep)
        self.ma, self.thong_diep, self.code = ma, thong_diep, code


def nap_hoac_tao_khoa_noi_bo(tep=None) -> str:
    """Khoa noi bo khi KHONG dat MEDITRACE_INTERNAL_TOKEN: doc tu tep, chua co thi sinh moi va ghi.

    Tep nam trong data/ (bo qua khoi git). Khoa on dinh qua cac lan khoi dong lai de phia web
    chi can dat mot lan MEDITRACE_INTERNAL_TOKEN = noi dung tep.
    """
    import secrets
    khoa_env = os.environ.get("MEDITRACE_INTERNAL_TOKEN", "").strip()
    if khoa_env:
        return khoa_env
    tep = Path(tep) if tep is not None else TEP_KHOA_NOI_BO
    try:
        cu = tep.read_text(encoding="utf-8").strip()
        if cu:
            return cu
    except OSError:
        pass
    moi = secrets.token_urlsafe(32)
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text(moi + "\n", encoding="utf-8")
    try:
        os.chmod(tep, 0o600)
    except OSError:
        pass
    return moi


def _khoa_goi_may_xa() -> str:
    return (os.environ.get("MEDITRACE_REMOTE_TOKEN", "").strip()
            or os.environ.get("MEDITRACE_INTERNAL_TOKEN", "").strip())


# ----------------------------------------------------------------- mo hinh

class Loi:
    """Giu mo hinh trich va cac tep dem. Nap CHAM: chi nap khi co yeu cau can den."""

    def __init__(self, ten_mo_hinh=None, adapter_trich=None, cho_nap_mo_hinh=True, mo_hinh_xa=None,
                 nhuong_cho=()):
        # 4B: adapter khau trich cua du an huan luyen tren Qwen3-4B, khong phai 8B
        self.ten_mo_hinh = ten_mo_hinh or "Qwen/Qwen3-4B"
        # URL mot dich vu khac (vd HoaiDuc qua duong ham SSH) lam khau TRICH khi can mo hinh.
        # Laptop 4 GB VRAM mat hon 25 phut moi hoi thoai; GPU 12 GB thi vai phut.
        self.mo_hinh_xa = (mo_hinh_xa or "").rstrip("/") or None
        self.adapter_trich = adapter_trich
        self.cho_nap_mo_hinh = cho_nap_mo_hinh
        # Chuoi can tim trong dong lenh cac tien trinh khac (vd "chuoi_hoaiduc"): thay tien trinh do
        # dang chay thi KHONG nap mo hinh, de thi nghiem do va dich vu khong cong RAM vuot tran.
        self.nhuong_cho = tuple(nhuong_cho or ())
        self._mo_hinh = None
        self._khoa = threading.Lock()
        self._khoa_suy_luan = threading.Lock()
        self._khoa_dem = threading.Lock()
        self._dem = None
        self._dem_theo_chu = {}

    # -- bo dem khau trich (chay lai trong vai giay, khong can GPU) -------
    @property
    def dem(self):
        if self._dem is None:
            with self._khoa_dem:
                if self._dem is None:
                    dem_moi, dem_chu_moi = {}, {}
                    for tep in sorted((duong_dan.GOC_DU_AN / "data").glob("trich_*_hl.jsonl")):
                        with open(tep, encoding="utf-8") as fh:
                            for dong in fh:
                                if dong.strip():
                                    b = json.loads(dong)
                                    dem_moi.setdefault(b["id"], b)
                    # Tep dem chi co ma ca, khong co loi thoai. Giao dien lai gui LOI THOAI. Dung
                    # chi muc loi thoai -> ma ca tu chinh cac bo du lieu de tra nguoc lai.
                    for tep in sorted(THU_MUC_BO.glob("*.jsonl")):
                        if tep.name.startswith("ra_"):
                            continue
                        with open(tep, encoding="utf-8") as fh:
                            for dong in fh:
                                if not dong.strip():
                                    continue
                                c = json.loads(dong)
                                if c.get("id") in dem_moi and c.get("input"):
                                    dem_chu_moi.setdefault(" ".join(c["input"].split()), dem_moi[c["id"]])
                    self._dem_theo_chu = dem_chu_moi
                    self._dem = dem_moi
        return self._dem

    def so_ca_bo_dem(self) -> int:
        """Tra so ca da nap trong bo dem ma KHONG ep quet dia neu chua nap."""
        return len(self._dem) if self._dem is not None else 0

    def dem_theo_chu(self, hoi_thoai):
        _ = self.dem                                  # bao dam da nap
        return self._dem_theo_chu.get(" ".join((hoi_thoai or "").split()))

    def nap(self):
        """-> (tok, model, prefix_fn). Nap mot lan, dung chung moi yeu cau."""
        if not self.cho_nap_mo_hinh:
            raise LoiDichVu("mo_hinh_bi_tat", "Dịch vụ đang chạy ở chế độ không nạp mô hình "
                            "(--khong-mo-hinh). Chỉ dùng được ca đã chạy trước hoặc có bộ đệm khâu trích.", 503)
        with self._khoa:
            if self._mo_hinh is None:
                ban = may_dang_ban(self.nhuong_cho)
                if ban:
                    raise LoiDichVu("may_ban", "Máy chủ đang chạy thí nghiệm đo (" + ban + "), chưa tạo được "
                                    "bản nháp mới. Thử lại sau khi thí nghiệm xong; các ca đã có vẫn mở được.", 503)
                from src import bakeoff
                t0 = time.time()
                print(f"[dich-vu] nap mo hinh {self.ten_mo_hinh} "
                      f"(adapter trich: {self.adapter_trich})", flush=True)
                try:
                    self._mo_hinh = bakeoff.nap(self.ten_mo_hinh, ep_json=True,
                                                adapter=self.adapter_trich)
                except Exception as exc:
                    raise LoiDichVu("khong_nap_duoc_mo_hinh", f"{type(exc).__name__}: {exc}", 503)
                print(f"[dich-vu] nap xong sau {time.time() - t0:.0f} s", flush=True)
        return self._mo_hinh

    def da_nap(self):
        return self._mo_hinh is not None

    def thiet_bi(self, cho_import: bool = False):
        """Khong tu y `import torch` neu `torch` chua co trong `sys.modules` (tranh treo /api/suc-khoe)."""
        torch_mod = sys.modules.get("torch")
        if torch_mod is None:
            if not cho_import:
                return "chua_nap"
            try:
                import torch as torch_mod
            except Exception:
                return "khong ro"
        try:
            return f"cuda ({torch_mod.cuda.get_device_name(0)})" if torch_mod.cuda.is_available() else "cpu"
        except Exception:
            return "khong ro"

    def _ho_so_xa(self, ca_id, hoi_thoai, nhanh, metadata=None):
        """Chuyen nguyen yeu cau sang dich vu o may khac; ket qua giu `nguon` = mo_hinh."""
        import urllib.error
        import urllib.request
        payload_xa = {"input": hoi_thoai, "nhanh": nhanh, "ca_id": ca_id}
        if metadata is not None:
            payload_xa["metadata"] = metadata
        du = json.dumps(payload_xa, ensure_ascii=False).encode("utf-8")
        tieu_de = {"Content-Type": "application/json"}
        khoa_xa = _khoa_goi_may_xa()
        if khoa_xa:
            tieu_de["X-MediTrace-Internal-Token"] = khoa_xa
        yc = urllib.request.Request(f"{self.mo_hinh_xa}/api/ho-so", data=du, headers=tieu_de)
        t0 = time.time()
        try:
            with urllib.request.urlopen(yc, timeout=1800) as res:
                r = json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                d = json.loads(exc.read().decode("utf-8"))
            except Exception:
                d = {}
            raise LoiDichVu(d.get("loi", "loi_may_xa"), d.get("thong_diep", f"máy xa trả mã {exc.code}"), exc.code)
        except Exception as exc:
            raise LoiDichVu("khong_toi_may_xa", f"Không tới được dịch vụ ở {self.mo_hinh_xa}: {exc}. "
                            "Kiểm tra đường hầm SSH tới HoaiDuc.", 503)
        r["may_chay"] = self.mo_hinh_xa
        r["giay_tong"] = round(time.time() - t0, 2)
        return r

    # -- sinh ho so -------------------------------------------------------
    def ho_so(self, ca_id, hoi_thoai, nhanh="C_khoa", thong_tin_benh_nhan=None, metadata=None):
        """-> ban ghi ket qua cua `src.nhanh.chay_trung_gian` + truong `nguon`."""
        if nhanh not in NHANH_CHO_PHEP:
            raise LoiDichVu("nhanh_khong_hop_le", f"nhánh {nhanh} không dùng được ở dịch vụ này")
        from src import nhanh as _nhanh
        mau_item = {"id": ca_id, "input": hoi_thoai}
        if isinstance(thong_tin_benh_nhan, dict):
            mau_item["thong_tin_benh_nhan"] = thong_tin_benh_nhan
        mau = [mau_item]
        dem = self.dem.get(ca_id)
        if dem is None or dem.get("input", hoi_thoai) != hoi_thoai:
            dem = self.dem_theo_chu(hoi_thoai)        # khong co ma ca thi tra theo loi thoai
            if dem is not None:
                mau[0]["id"] = ca_id = dem["id"]
        if dem is not None:
            tok = model = prefix_fn = None
            kq_tho, nguon = [dem], "bo_dem"
            t0 = time.time()
            try:
                kq = _nhanh.chay_trung_gian(mau, tok, model, prefix_fn, nhanh,
                                            max_token=MAX_TOKEN, kq_tho=kq_tho)
            except LoiDichVu:
                raise
            except Exception as exc:
                traceback.print_exc()
                raise LoiDichVu("loi_sinh_ho_so", f"{type(exc).__name__}: {exc}", 500)
        elif self.mo_hinh_xa:
            from src.khu_dinh_danh import ClinicalDeidentifier
            ten_bn_xa = (
                (thong_tin_benh_nhan.get("ten") or thong_tin_benh_nhan.get("ho_ten"))
                if isinstance(thong_tin_benh_nhan, dict)
                else None
            )
            kq_ad = ClinicalDeidentifier.an_danh_van_ban(hoi_thoai, ten_benh_nhan=ten_bn_xa)
            # Fail-closed: quet lai van ban DA CHE; con dau vet PII (so dai, ten sau tien to)
            # thi KHONG gui ra may xa.
            con_sot = ClinicalDeidentifier.kiem_tra_con_sot(kq_ad.van_ban_da_an_danh)
            if con_sot:
                loai_sot = sorted({str(x.get("loai")) for x in con_sot})
                raise LoiDichVu("khu_dinh_danh_chua_sach",
                                "Khử định danh chưa sạch (còn " + ", ".join(loai_sot) + "): không gửi hội "
                                "thoại ra máy xa. Sửa bản ghi hoặc chạy mô hình tại chỗ.", 422)
            # Thong tin benh nhan / xet nghiem KHONG gui ra may xa
            r_xa = self._ho_so_xa(ca_id, kq_ad.van_ban_da_an_danh, nhanh, metadata=metadata)
            if not isinstance(r_xa, dict):
                raise LoiDichVu("loi_may_xa", "máy xa trả kết quả không hợp lệ", 502)
            # May xa tinh lop canh bao / lam sang tren van ban da che va KHONG co thong tin benh
            # nhan: bo di de _them_canh_bao tinh lai TAI CHO tren van ban da khoi phuc.
            r_xa.pop("lam_sang_nang_cao", None)
            r_xa.pop("canh_bao", None)
            if kq_ad.bang_anh_xa_giai_ma:
                # Khôi phục cục bộ các token PII sau khi máy xa xử lý xong (máy xa không bao giờ thấy PII gốc)
                def _giai_ma(obj):
                    if isinstance(obj, str):
                        s = obj
                        for tok_pii, goc in kq_ad.bang_anh_xa_giai_ma.items():
                            s = s.replace(tok_pii, goc)
                        return s
                    if isinstance(obj, list):
                        return [_giai_ma(x) for x in obj]
                    if isinstance(obj, dict):
                        return {k: _giai_ma(v) for k, v in obj.items()}
                    return obj
                r_xa = _giai_ma(r_xa)
            r_xa["da_khu_dinh_danh_truoc_gui_xa"] = True
            r_xa["so_pii_da_chan"] = kq_ad.tong_so_thuc_the
            r_xa["lam_sang_tinh_tai_cho"] = True
            if metadata is not None:
                _gan_metadata_am_thanh(r_xa, metadata)
            return r_xa
        else:
            with self._khoa_suy_luan:
                tok, model, prefix_fn = self.nap()
                kq_tho, nguon = None, "mo_hinh"
                t0 = time.time()
                try:
                    kq = _nhanh.chay_trung_gian(mau, tok, model, prefix_fn, nhanh,
                                                max_token=MAX_TOKEN, kq_tho=kq_tho)
                except LoiDichVu:
                    raise
                except Exception as exc:
                    traceback.print_exc()
                    raise LoiDichVu("loi_sinh_ho_so", f"{type(exc).__name__}: {exc}", 500)
        r = kq[0]
        r["nguon"] = nguon
        r["nhanh"] = nhanh
        r["giay_xu_ly"] = round(time.time() - t0, 2)
        if metadata is not None:
            _gan_metadata_am_thanh(r, metadata)
        return r


def _gan_metadata_am_thanh(r: dict, metadata: list) -> None:
    """Gan `metadata` am thanh cua `to_meditrace` vao ho so va dien `audio_spans` cho menh de."""
    if not isinstance(r, dict) or not isinstance(metadata, list):
        return
    r["metadata"] = metadata
    theo_luot = {
        int(m["luot"]): m
        for m in metadata
        if isinstance(m, dict) and m.get("luot") is not None
    }
    if not theo_luot:
        return
    for pb in r.get("phat_bieu") or []:
        if not isinstance(pb, dict) or pb.get("audio_spans"):
            continue
        spans = []
        trich_list = pb.get("trich_dan") or []
        for idx_bc, luot_so in enumerate(pb.get("bang_chung") or []):
            m_luot = theo_luot.get(int(luot_so))
            if not m_luot:
                continue
            a_start = m_luot.get("audio_start")
            a_end = m_luot.get("audio_end")
            if a_start is None and a_end is None:
                continue
            quote = trich_list[idx_bc] if idx_bc < len(trich_list) else (trich_list[0] if trich_list else (pb.get("noi_dung") or ""))
            spans.append({
                "start_ms": int(round(float(a_start or 0.0) * 1000)),
                "end_ms": int(round(float(a_end or 0.0) * 1000)),
                "speaker_id": str(m_luot.get("speaker_id") or m_luot.get("speaker_role") or ""),
                "exact_quote": str(quote),
            })
        if spans:
            pb["audio_spans"] = spans


# ----------------------------------------------------------------- am thanh

class AmThanh:
    def __init__(self):
        self._pipe = None
        self._khoa = threading.Lock()
        self._khoa_suy_luan = threading.Lock()

    def cau_hinh_nhe(self):
        """Doc cau hinh ASR/Diarization nhe tu bien moi truong ma KHONG khoi tao `_pipe`
        (giu nguyen `self._pipe is None` de khong pha vo `canh_nghi`)."""
        if self._pipe is not None:
            return self._pipe.settings
        from src.audio.config import AudioSettings
        return AudioSettings.from_env()

    def pipeline(self):
        with self._khoa:
            if self._pipe is None:
                from src.audio.pipeline import AudioPipeline
                from src.audio.storage import SessionStore
                THU_MUC_PHIEN.mkdir(parents=True, exist_ok=True)
                self._pipe = AudioPipeline(SessionStore(THU_MUC_PHIEN))
        return self._pipe

    def chep(self, du_lieu: bytes, ten_tep: str, tach_nguoi_noi: bool = True):
        pipe = self.pipeline()
        phien = pipe.store.create()["session_id"]
        pipe.upload(phien, du_lieu, ten_tep)
        with self._khoa_suy_luan:
            pipe.process(phien, tach_nguoi_noi=tach_nguoi_noi)
        return phien, pipe.transcript(phien)


def _doan_ra_json(t):
    return {k: t.get(k) for k in ("segment_id", "start_time", "end_time", "text_original",
                                  "text_normalized", "speaker_id", "speaker_role",
                                  "suggested_role", "suggested_role_reason",
                                  "asr_confidence", "asr_provider", "asr_model",
                                  "asr_review_required", "asr_review_reason", "asr_candidates",
                                  "reviewed", "edited")}


_WORM_LOGGER = None
_WORM_LOCK = threading.Lock()


def lay_worm_logger():
    """Singleton thread-safe WormAuditLogger cho dịch vụ HTTP."""
    global _WORM_LOGGER
    with _WORM_LOCK:
        if _WORM_LOGGER is None:
            from src.worm_audit_log import WormAuditLogger
            _WORM_LOGGER = WormAuditLogger(duong_dan.GOC_DU_AN / "data" / "audit_log_worm.db")
    return _WORM_LOGGER


def ghi_chu_tach(tach: dict | None) -> str:
    """Cau bao cho nguoi dung: may da tach nguoi noi chua, va vai con phai gan tay."""
    tach = tach or {}
    n = tach.get("so_nguoi_noi") or 1
    if tach.get("tach_that"):
        if n >= 2:
            return (f"Máy đã tách {n} người nói (Người nói 1, 2…) bằng {tach.get('phuong_phap')}. "
                    "Máy không biết ai là bác sĩ: gán vai cho từng người nói, kiểm lại từng dòng, "
                    "rồi mới tạo hồ sơ.")
        return ("Máy chỉ nghe ra một người nói. Nếu cuộc khám có nhiều người, gán vai "
                "từng dòng trước khi tạo hồ sơ.")
    if tach.get("lui_ve"):
        return (f"Chưa tách được người nói ({tach.get('loi')}); cả bản ghi được coi là một "
                "người nói. Gán vai từng dòng trước khi tạo hồ sơ.")
    return ("Chưa bật tách người nói; cả bản ghi được coi là một người nói. "
            "Gán vai từng dòng trước khi tạo hồ sơ.")


# ----------------------------------------------------------------- ca mau

def ca_mau(bo=None):
    """Danh sach ca da chay truoc, de demo khi GPU ban (kem 3 ca demo BGK khi khong co kaggle-ra)."""
    from src.ca_mau_bgk import danh_sach_ca_demo
    ra = list(danh_sach_ca_demo(bo))
    if THU_MUC_CHAY_TRUOC.exists():
        for tep in sorted(THU_MUC_CHAY_TRUOC.glob("ra_C_khoa_*.jsonl")):
            if "C_khoa_hoi" in tep.name:
                continue
            ten_bo = tep.name[len("ra_C_khoa_"):-len(".jsonl")]
            if bo and bo != ten_bo:
                continue
            with open(tep, encoding="utf-8") as fh:
                for dong in fh:
                    if not dong.strip():
                        continue
                    r = json.loads(dong)
                    ra.append({"id": r["id"], "bo": ten_bo,
                               "so_luot": len([x for x in r["input"].split("\n") if x.strip()]),
                               "so_menh_de": len(r.get("phat_bieu") or []),
                               "so_can_xac_nhan": r.get("so_can_xac_nhan", 0)})
    return ra


def doc_ca(ca_id, nhanh="C_khoa"):
    """-> ban ghi da chay truoc cua mot ca mau.

    Nhanh C_khoa_hoi co cung phat bieu voi C_khoa (da so tren ca 4 bo), chi them cau hoi lam ro;
    hoi nhanh C_khoa_hoi thi doc tep C_khoa_hoi, khong co thi lui ve C_khoa.
    """
    from src.ca_mau_bgk import doc_ca_demo
    r_demo = doc_ca_demo(ca_id, nhanh)
    if r_demo is not None:
        if r_demo.get("metadata"):
            _gan_metadata_am_thanh(r_demo, r_demo["metadata"])
        return r_demo

    if THU_MUC_CHAY_TRUOC.exists():
        if nhanh == "C_khoa_hoi":
            for tep in sorted(THU_MUC_CHAY_TRUOC.glob("ra_C_khoa_hoi_*.jsonl")):
                with open(tep, encoding="utf-8") as fh:
                    for dong in fh:
                        if dong.strip():
                            r = json.loads(dong)
                            if r["id"] == ca_id:
                                r["nhanh"] = "C_khoa_hoi"
                                return r
        for tep in sorted(THU_MUC_CHAY_TRUOC.glob("ra_C_khoa_*.jsonl")):
            if "C_khoa_hoi" in tep.name:
                continue
            with open(tep, encoding="utf-8") as fh:
                for dong in fh:
                    if dong.strip():
                        r = json.loads(dong)
                        if r["id"] == ca_id:
                            return r
    raise LoiDichVu("khong_co_ca", f"không có ca {ca_id} trong thư mục ca mẫu", 404)


# ----------------------------------------------------------------- HTTP

class May(BaseHTTPRequestHandler):
    server_version = "MediTrace/1.0"
    timeout = 60
    loi: Loi
    am: AmThanh
    lan_cuoi = time.time()                   # moc yeu cau POST gan nhat XONG (cho canh_nghi)
    dang_xu_ly = 0                           # so yeu cau POST dang chay
    _khoa_dem = threading.Lock()

    def _tra(self, gia_tri, code=200):
        du = json.dumps(gia_tri, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(du)))
        # Chi cho phep Origin noi bo (localhost / 127.0.0.1) hoac danh sach cau hinh,
        # chan trang web la tren trinh duyet goi truc tiep vao cong 8765.
        origin = (self.headers.get("Origin") or "").strip()
        if origin and re.match(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$", origin, re.I):
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:3000")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-MediTrace-Internal-Token")
        self.end_headers()
        self.wfile.write(du)

    khoa_noi_bo = None                       # dat boi main() khi khong co bien moi truong
    host_cho_phep = ()                       # them ngoai HOST_MAC_DINH (--dia-chi)

    def _khoa_hieu_luc(self):
        return os.environ.get("MEDITRACE_INTERNAL_TOKEN", "").strip() or (self.khoa_noi_bo or "")

    def _kiem_khoa_noi_bo(self):
        """Fail-closed: khong co khoa cau hinh thi tu choi; so khoa bang hmac.compare_digest."""
        khoa = self._khoa_hieu_luc()
        if not khoa:
            raise LoiDichVu("chua_cau_hinh_khoa_noi_bo",
                            "Dịch vụ chưa có khóa nội bộ (MEDITRACE_INTERNAL_TOKEN); từ chối truy cập.", 503)
        nhan = (self.headers.get("X-MediTrace-Internal-Token") or "").strip()
        if not hmac.compare_digest(nhan.encode("utf-8"), khoa.encode("utf-8")):
            raise LoiDichVu("khong_hop_le_token_noi_bo", "Thiếu hoặc sai khóa xác thực nội bộ", 403)

    def _kiem_host(self):
        """Chong DNS rebinding: Host phai la may nay (hoac dia chi da cau hinh)."""
        host = (self.headers.get("Host") or "").strip().lower()
        if host.startswith("["):                      # [::1]:8765
            ten = host[1:].split("]", 1)[0]
        else:
            ten = host.rsplit(":", 1)[0] if host.count(":") == 1 else host
        them = [x.strip().lower() for x in os.environ.get("MEDITRACE_ALLOWED_HOSTS", "").split(",") if x.strip()]
        cho_phep = set(HOST_MAC_DINH) | {h.lower() for h in self.host_cho_phep} | set(them)
        if not ten or ten not in cho_phep:
            raise LoiDichVu("host_khong_hop_le", "Host không được phép", 403)

    @staticmethod
    def _kiem_ma_phien(phien: str) -> str:
        phien_sach = str(phien or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", phien_sach) or ".." in phien_sach:
            raise LoiDichVu("ma_phien_khong_hop_le", "Mã phiên âm thanh không hợp lệ", 400)
        return phien_sach

    def _than(self):
        cl = (self.headers.get("Content-Length") or "0").strip()
        if not re.fullmatch(r"\d{1,12}", cl):
            raise LoiDichVu("content_length_khong_hop_le", "Content-Length không hợp lệ", 400)
        n = int(cl)
        if n > GIOI_HAN_THAN:
            raise LoiDichVu("qua_lon", "nội dung gửi lên quá lớn", 413)
        try:
            than = json.loads(self.rfile.read(n) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise LoiDichVu("json_hong", str(exc))
        if not isinstance(than, dict):
            raise LoiDichVu("json_hong", "thân yêu cầu phải là một đối tượng JSON")
        return than

    def do_OPTIONS(self):
        self._tra({}, 204)

    def do_GET(self):
        try:
            duong, _, chuoi_tham = self.path.partition("?")
            tham = {}
            if chuoi_tham:
                for phan in chuoi_tham.split("&"):
                    if not phan:
                        continue
                    k_p, _, v_p = phan.partition("=")
                    tham[k_p] = v_p
            self._kiem_host()
            # Moi duong /api/* tru suc-khoe deu can khoa noi bo
            if duong.startswith("/api/") and duong != "/api/suc-khoe":
                self._kiem_khoa_noi_bo()
            if duong == "/api/suc-khoe":
                cfg_am = self.am.cau_hinh_nhe()
                cr_mod = sys.modules.get("src.cong_rui_ro")
                chinh_sach_cong = getattr(cr_mod, "CHINH_SACH", CHINH_SACH_CONG_MAC_DINH)
                return self._tra({
                    "ok": True,
                    "mo_hinh": self.loi.ten_mo_hinh,
                    "adapter_trich": self.loi.adapter_trich,
                    "da_nap_mo_hinh": self.loi.da_nap(),
                    "cho_nap_mo_hinh": self.loi.cho_nap_mo_hinh,
                    "mo_hinh_xa": self.loi.mo_hinh_xa,
                    "thiet_bi": self.loi.thiet_bi(cho_import=False),
                    "so_ca_bo_dem": self.loi.so_ca_bo_dem(),
                    "chinh_sach_cong": chinh_sach_cong,
                    "bo_cham": PHIEN_BAN_BO_CHAM,
                    "asr": {
                        "nha_cung_cap": cfg_am.asr_provider,
                        "mo_hinh": cfg_am.asr_model or cfg_am.whisper_model,
                    },
                    "tach_nguoi_noi": cfg_am.diarization_provider,
                })
            if duong == "/api/ca-mau":
                return self._tra({"ca": ca_mau(tham.get("bo"))})
            if duong.startswith("/api/phien/"):
                phien = self._kiem_ma_phien(duong[len("/api/phien/"):])
                pipe = self.am.pipeline()
                return self._tra({"phien": phien,
                                  "doan": [_doan_ra_json(t) for t in pipe.transcript(phien)],
                                  "tach_nguoi_noi": pipe.store.load(phien).get("tach_nguoi_noi") or {}})
            if duong in ("/copilot", "/ui", "/"):
                tep_ui = duong_dan.GOC_DU_AN / "src" / "giao_dien_copilot.html"
                if tep_ui.exists():
                    du = tep_ui.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(du)))
                    self.end_headers()
                    self.wfile.write(du)
                    return
            raise LoiDichVu("khong_co_duong", f"không có đường {duong}", 404)
        except Exception as exc:
            self._bao_loi(exc)

    def do_POST(self):
        # Dem viec dang xu ly: tao ban nhap mat vai phut, canh_nghi khong duoc tat tien trinh giua chung.
        with May._khoa_dem:
            May.dang_xu_ly += 1
        try:
            self._xu_ly_post()
        finally:
            with May._khoa_dem:
                May.dang_xu_ly -= 1
            May.lan_cuoi = time.time()

    def _xu_ly_post(self):
        try:
            self._kiem_host()
            self._kiem_khoa_noi_bo()
            duong = self.path.split("?")[0]
            than = self._than()
            if duong == "/api/chep-am":
                return self._tra(self._chep_am(than))
            if duong == "/api/gan-vai":
                phien = self._kiem_ma_phien(than.get("phien") or "")
                vai = than.get("vai") or {}
                if not phien or not vai:
                    raise LoiDichVu("thieu_tham_so", "cần `phien` và `vai`")
                doan = self.am.pipeline().map_speakers(phien, vai)
                return self._tra({"phien": phien, "doan": [_doan_ra_json(t) for t in doan]})
            if duong == "/api/ho-so":
                return self._tra(self._ho_so(than))
            if duong == "/api/bhyt/precheck":
                from src.kiem_duyet_bhyt_va_bo_sot import tien_kiem_bhyt_tu_du_lieu
                tt_bn = than.get("thong_tin_benh_nhan")
                kq = tien_kiem_bhyt_tu_du_lieu(
                    than.get("propositions") or [],
                    than.get("transcript") or "",
                    thong_tin_benh_nhan=tt_bn if isinstance(tt_bn, dict) else None,
                )
                return self._tra(kq)
            if duong == "/api/ocr/phieu-cu":
                txt = str(than.get("text") or "").strip()
                if not txt:
                    raise LoiDichVu("thieu_noi_dung", "Cần `text` phiếu xét nghiệm / đơn thuốc cũ", 400)
                from src.ocr_lam_sang import boc_tach_phieu_cu
                kq = boc_tach_phieu_cu(
                    van_ban=txt,
                    tuoi=than.get("tuoi"),          # thieu tuoi -> khong mac dinh 50
                    la_nu=bool(than.get("laNu", False)),
                    can_nang_kg=than.get("canNangKg"),
                )
                return self._tra(kq)
            if duong == "/api/quy-ket-loi":
                from src.kiem_duyet_bhyt_va_bo_sot import ClinicalHarmWeightedEvaluator
                kq = ClinicalHarmWeightedEvaluator.quy_ket_nguoc_tang_loi(
                    thao_tac_bac_si=str(than.get("thao_tac") or ""),
                    menh_de_goc=than.get("menh_de_goc"),
                    menh_de_sua=than.get("menh_de_sua"),
                )
                return self._tra({"ok": True, "quy_ket": kq})
            raise LoiDichVu("khong_co_duong", f"không có đường {duong}", 404)
        except Exception as exc:
            self._bao_loi(exc)

    # -- viec --------------------------------------------------------------
    def _chep_am(self, than):
        b64 = than.get("am_thanh_base64")
        if not b64:
            raise LoiDichVu("thieu_am_thanh", "cần `am_thanh_base64`")
        try:
            du = base64.b64decode(b64.split(",")[-1], validate=True)
        except (binascii.Error, ValueError) as exc:
            raise LoiDichVu("am_thanh_hong", f"không giải mã được base64: {exc}")
        if len(du) > GIOI_HAN_AM_THANH:
            raise LoiDichVu("qua_lon", f"tệp âm thanh {len(du) // 2**20} MB, vượt giới hạn "
                            f"{GIOI_HAN_AM_THANH // 2**20} MB", 413)
        ten = than.get("ten_tep") or "ghi-am.webm"
        t0 = time.time()
        # `tach_nguoi_noi: false`: nguoi goi biet chi mot nguoi noi (cau hoi ghi bang micro).
        phien, doan = self.am.chep(du, ten, tach_nguoi_noi=than.get("tach_nguoi_noi") is not False)
        tach = self.am.pipeline().store.load(phien).get("tach_nguoi_noi") or {}
        return {"phien": phien, "doan": [_doan_ra_json(t) for t in doan],
                "giay_xu_ly": round(time.time() - t0, 2),
                "nguon": "mo_hinh",
                "tach_nguoi_noi": tach,
                "ghi_chu": ghi_chu_tach(tach)}

    def _ho_so(self, than):
        # Bien vao: ep kieu an toan ("25" -> 25.0, rac -> thieu) truoc khi toi bat ky cong nao
        from src.ep_kieu_dau_vao import (chuan_hoa_du_lieu_xet_nghiem_dau_vao,
                                         chuan_hoa_thong_tin_benh_nhan)
        than = dict(than)
        thong_tin_bn = than["thong_tin_benh_nhan"] = chuan_hoa_thong_tin_benh_nhan(than.get("thong_tin_benh_nhan"))
        du_lieu_xn = than["du_lieu_xet_nghiem"] = chuan_hoa_du_lieu_xet_nghiem_dau_vao(
            than.get("du_lieu_xet_nghiem"))
        kq = _them_canh_bao(
            self._ho_so_tho(than),
            thong_tin_benh_nhan=thong_tin_bn,
            du_lieu_xet_nghiem=du_lieu_xn,
        )
        try:
            # Chu the DA XAC THUC la ben giu khoa noi bo; `user_id` trong than chi la khai bao cua
            # ben goi -> ghi ro "khai_bao:" chu khong ghi nhu danh tinh da xac minh.
            khai_bao = str(than.get("user_id") or "").strip()[:128]
            user_id = f"{CHU_THE_NOI_BO}/khai_bao:{khai_bao}" if khai_bao else CHU_THE_NOI_BO
            ma_ca = str(kq.get("id") or than.get("ca_id") or "ca_kham")
            worm_ev = lay_worm_logger().append_event(
                user_id=user_id,
                action="HO_SO_TAO_BAN_NHAP",
                case_id=ma_ca,
                payload={"nhanh": kq.get("nhanh"), "nguon": kq.get("nguon"), "so_phat_bieu": len(kq.get("phat_bieu") or []),
                         "user_id_khai_bao": khai_bao or None},
                details="Sinh bản nháp & kiểm duyệt 8 chốt",
            )
            kq["worm_seq"] = worm_ev.get("seq")
            kq["worm_hash"] = worm_ev.get("curr_hash")
        except Exception:
            traceback.print_exc()
        return kq

    def _ho_so_tho(self, than):
        nhanh = than.get("nhanh") or "C_khoa"
        ca_id = than.get("ca_id") or f"ui_{int(time.time())}"
        thong_tin_bn = than.get("thong_tin_benh_nhan") if isinstance(than.get("thong_tin_benh_nhan"), dict) else None
        metadata = than.get("metadata") if isinstance(than.get("metadata"), list) else None
        if than.get("chay_truoc"):
            r = doc_ca(than["chay_truoc"], nhanh)
            r["nguon"], r["giay_xu_ly"] = "chay_truoc", 0.0
            r.setdefault("nhanh", "C_khoa")
            if metadata is not None:
                _gan_metadata_am_thanh(r, metadata)
            return r
        if than.get("phien"):
            from src.audio.adapter import to_meditrace
            phien_id = self._kiem_ma_phien(than["phien"])
            doan = self.am.pipeline().transcript(phien_id)
            if any(s.get("asr_review_required") for s in doan):
                raise LoiDichVu("asr_review_pending", "Chưa gán vai cho người nói, hoặc còn đoạn chờ người duyệt.", 409)
            try:
                vao = to_meditrace(doan, strict=True)
            except ValueError as exc:
                raise LoiDichVu(str(exc), "Chưa gán vai cho người nói, hoặc còn đoạn chờ người duyệt.", 409)
            hoi_thoai = vao["input"]
            metadata = vao.get("metadata")
        else:
            hoi_thoai = (than.get("input") or "").strip()
        if not hoi_thoai:
            raise LoiDichVu("thieu_hoi_thoai", "cần `input`, `phien` hoặc `chay_truoc`")
        return self.loi.ho_so(ca_id, hoi_thoai, nhanh, thong_tin_benh_nhan=thong_tin_bn, metadata=metadata)

    def _bao_loi(self, exc):
        if isinstance(exc, LoiDichVu):
            return self._tra({"loi": exc.ma, "thong_diep": exc.thong_diep}, exc.code)
        traceback.print_exc()
        self._tra({"loi": "loi_khong_ro", "thong_diep": f"{type(exc).__name__}: {exc}"}, 500)

    def log_message(self, dang, *a):
        print(f"[dich-vu] {self.address_string()} {dang % a}", flush=True)


def _them_canh_bao(r, thong_tin_benh_nhan=None, du_lieu_xet_nghiem=None):
    """Ban ghi chay truoc / tu may xa chua co lop canh bao (24/09/2026): tinh tai day
    tu phat bieu va loi thoai. Dong thoi ket noi 14 module lam sang nang cao
    (`dieu_phoi_ha_tang` + `kiem_duyet_bhyt_va_bo_sot`) vao truong `lam_sang_nang_cao`."""
    if not isinstance(r, dict) or not r.get("phat_bieu") or not r.get("input"):
        return r
    from dataclasses import asdict
    from src.canh_bao import gop
    from src.phat_bieu import PhatBieu
    try:
        ps = [
            PhatBieu(**{k: v for k, v in d.items() if k in PhatBieu.__dataclass_fields__})
            if isinstance(d, dict) else d
            for d in r["phat_bieu"]
        ]
        if not r.get("canh_bao"):
            r["canh_bao"] = gop.to_dict(gop.chay(ps, r["input"]))
    except Exception:
        traceback.print_exc()
        r["canh_bao_loi"] = "không tính được lớp cảnh báo cho bản ghi này"
        return r

    if not r.get("lam_sang_nang_cao"):
        try:
            from src.dieu_phoi_ha_tang import MediTracePipelineOrchestrator
            from src.kiem_duyet_bhyt_va_bo_sot import (
                ActiveOmissionRecoveryEngine,
                BHYTXmlPreChecker,
                xuat_goi_xml_1_5_qd130,
            )
            ma_ca = str(r.get("id") or "ca_kham")
            dp = MediTracePipelineOrchestrator.xu_ly_ca_kham(
                ma_ca=ma_ca,
                hoi_thoai=r["input"],
                danh_sach_phat_bieu=ps,
                thong_tin_benh_nhan=thong_tin_benh_nhan,
                du_lieu_xet_nghiem=du_lieu_xet_nghiem,
            )
            bo_sot = ActiveOmissionRecoveryEngine.quet_khoi_phuc(ps, r["input"])
            bhyt = BHYTXmlPreChecker.kiem_duyet_ho_so(
                ma_ca, ps, r["input"], thong_tin_benh_nhan=thong_tin_benh_nhan
            )
            xml_1_5 = xuat_goi_xml_1_5_qd130(
                ma_lk=ma_ca,
                ket_qua_bhyt=bhyt,
                danh_sach_phat_bieu=ps,
                thong_tin_benh_nhan=thong_tin_benh_nhan,
                hoi_thoai=r["input"],
            )
            from src.canh_bao import lam_sang
            from src.canh_bao.phat_hien import NguCanh
            r["lam_sang_nang_cao"] = {
                # 25/11/2026: lieu / tuong tac / di ung theo ma cua lop canh bao (thu nghiem, co muc
                # tin cay), doc tu cung tri_thuc_thuoc voi cac truong ben duoi.
                "lop_canh_bao_lam_sang": [c.to_dict() for c in lam_sang.quet(NguCanh(r["input"]), ps)],
                "bhyt_icd10": bhyt.to_dict(),
                "goi_xml_1_5": xml_1_5,
                "khoi_phuc_bo_sot_tang_45": [x.to_dict() for x in bo_sot],
                "duoc_ly_ddi": asdict(dp.kiem_duyet_duoc_ly),
                "doi_soat_can_lam_sang": asdict(dp.doi_soat_can_lam_sang) if dp.doi_soat_can_lam_sang else None,
                "thang_diem_nguy_co": dp.thang_diem_nguy_co,
                "hieu_chinh_lieu": dp.hieu_chinh_lieu,
                "tro_ly_socrates": dp.tro_ly_lam_sang,
                "ban_dan_do_benh_nhan": dp.ban_dan_do_benh_nhan,
                "audit_trail_worm": dp.audit_trail.to_dict(),
                "fhir_r4_summary": {
                    "resourceType": dp.fhir_bundle.get("resourceType", "Bundle"),
                    "totalEntries": len(dp.fhir_bundle.get("entry") or []),
                },
                "fhir_bundle": dp.fhir_bundle,
            }
        except Exception:
            traceback.print_exc()
    return r


def may_dang_ban(nhuong_cho):
    """-> chuoi khop dau tien neu co tien trinh KHAC dang chay voi dong lenh chua no, khong thi None."""
    if not nhuong_cho:
        return None
    import os
    import psutil

    # Bo qua chinh minh, cac tien trinh cha (vong lap khoi dong lai, cmd) va moi dong lenh mang co
    # --nhuong-cho: cac dong lenh nay chua san chuoi can tim nen se tu khop voi chinh no.
    than = psutil.Process(os.getpid())
    bo_qua = {than.pid} | {p.pid for p in than.parents()}
    for p in psutil.process_iter(["pid", "cmdline"]):
        if p.info["pid"] in bo_qua:
            continue
        dong = " ".join(p.info.get("cmdline") or [])
        if "--nhuong-cho" in dong:
            continue
        for c in nhuong_cho:
            if c in dong:
                return c
    return None


def canh_nghi(phut):
    """Luong nen: da nap mo hinh/PhoWhisper ma `phut` phut khong ai dung thi tu thoat (ma 0), de nha RAM
    va VRAM. Chay kem vong lap khoi dong lai (chay-dich-vu.cmd) thi tien trinh moi len lai o dang nhe,
    chi nap mo hinh khi co yeu cau tiep theo."""
    import os

    def chay():
        while True:
            time.sleep(30)
            da_nap = May.loi.da_nap() or May.am._pipe is not None
            if da_nap and May.dang_xu_ly == 0 and time.time() - May.lan_cuoi > phut * 60:
                print(f"[dich-vu] {phut:g} phut khong co yeu cau — thoat de nha RAM", flush=True)
                os._exit(0)

    threading.Thread(target=chay, daemon=True).start()


def canh_ram(tran_gb):
    """Luong nen: RAM vat ly (RSS) cua tien trinh vuot tran thi ghi log va tu dung ngay."""
    import os
    import psutil

    p = psutil.Process()

    def chay():
        while True:
            dung = p.memory_info().rss / 1024 ** 3
            if dung > tran_gb:
                print(f"[dich-vu] RAM {dung:.2f} GB vuot tran {tran_gb} GB — tu dung", flush=True)
                os._exit(3)
            time.sleep(3)

    threading.Thread(target=chay, daemon=True).start()


def dat_bien_tach_nguoi_noi(a, env=None) -> None:
    """Doi cac co dong lenh ve tach nguoi noi thanh bien moi truong.

    Bo chep am doc cau hinh tu bien moi truong luc tao pipeline lan dau (AmThanh.pipeline), nen
    phai dat truoc. 25/09/2026 doan nay nam thang trong main() va thieu `import os`: chi hong khi
    co --tran-ram-gb (cach HoaiDuc chay), nen dich vu tren HoaiDuc lap khoi dong hong ~1,5 phut.
    Phep thu: tests/test_audio_diarization.py.
    """
    env = os.environ if env is None else env
    for bien, gia_tri in (("DIARIZATION_PROVIDER", a.tach_nguoi_noi), ("PYANNOTE_PYTHON", a.pyannote_python),
                          ("PYANNOTE_TOKEN_FILE", a.pyannote_khoa), ("PYANNOTE_DEVICE", a.pyannote_thiet_bi)):
        if gia_tri:
            env[bien] = gia_tri
    if a.tran_ram_gb and not env.get("PYANNOTE_TONG_RAM_GB"):
        # Tran chung: dich vu + tien trinh pyannote khong vuot tran da dat cho dich vu.
        env["PYANNOTE_TONG_RAM_GB"] = str(a.tran_ram_gb)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--cong", type=int, default=8765)
    ap.add_argument("--dia-chi", default="127.0.0.1", help="mac dinh chi nghe tren may nay")
    ap.add_argument("--model", default=None)
    ap.add_argument("--adapter-trich", default=str(duong_dan.GOC_DU_AN / "models" /
                                                   "nen-qwen3-4b-trich" / "best_checkpoint"))
    ap.add_argument("--mo-hinh-xa", default=None,
                    help="URL dich vu o may khac lam khau trich, vd http://127.0.0.1:8766 (duong ham SSH)")
    ap.add_argument("--tran-ram-gb", type=float, default=None,
                    help="RAM vat ly toi da cua tien trinh nay; vuot thi tu dung (HoaiDuc: tran chung 10 GB)")
    ap.add_argument("--nghi-sau-phut", type=float, default=None,
                    help="da nap mo hinh ma bay nhieu phut khong co yeu cau thi tu thoat de nha RAM")
    ap.add_argument("--nhuong-cho", default="",
                    help="danh sach (phay) chuoi trong dong lenh tien trinh khac; thay thi khong nap mo hinh, "
                         "vd chuoi_hoaiduc")
    ap.add_argument("--khong-mo-hinh", action="store_true",
                    help="khong nap mo hinh: chi dung ca da chay truoc va bo dem khau trich")
    ap.add_argument("--tach-nguoi-noi", choices=["mot-nguoi", "pyannote"], default=None,
                    help="tach nguoi noi khi chep am; mac dinh theo bien DIARIZATION_PROVIDER (mot-nguoi)")
    ap.add_argument("--pyannote-python", default=None,
                    help="python cua moi truong rieng co pyannote.audio, vd D:/pyannote-venv/Scripts/python.exe")
    ap.add_argument("--pyannote-khoa", default=None,
                    help="TEP chua khoa Hugging Face (chi can lan tai mo hinh dau tien); khong nhan gia tri khoa")
    ap.add_argument("--pyannote-thiet-bi", choices=["cpu", "cuda"], default=None)
    a = ap.parse_args()
    dat_bien_tach_nguoi_noi(a)

    May.loi = Loi(a.model, a.adapter_trich, cho_nap_mo_hinh=not a.khong_mo_hinh, mo_hinh_xa=a.mo_hinh_xa,
                  nhuong_cho=[x.strip() for x in a.nhuong_cho.split(",") if x.strip()])
    # Khoa noi bo: bien moi truong, khong co thi doc/sinh tep (in duong dan, KHONG in khoa)
    May.khoa_noi_bo = nap_hoac_tao_khoa_noi_bo()
    if not os.environ.get("MEDITRACE_INTERNAL_TOKEN", "").strip():
        print(f"[dich-vu] chua dat MEDITRACE_INTERNAL_TOKEN: dung khoa trong tep {TEP_KHOA_NOI_BO} "
              "(dat MEDITRACE_INTERNAL_TOKEN o phia web = noi dung tep nay)", flush=True)
    if a.dia_chi not in ("0.0.0.0", "::", ""):
        May.host_cho_phep = (a.dia_chi,)
    if a.tran_ram_gb:
        canh_ram(a.tran_ram_gb)
    May.am = AmThanh()
    if a.nghi_sau_phut:
        canh_nghi(a.nghi_sau_phut)
    may = ThreadingHTTPServer((a.dia_chi, a.cong), May)
    print(f"[dich-vu] nghe tai http://{a.dia_chi}:{a.cong} "
          f"({'khong nap mo hinh' if a.khong_mo_hinh else 'nap mo hinh khi can'})", flush=True)
    try:
        may.serve_forever()
    except KeyboardInterrupt:
        print("[dich-vu] dung", flush=True)


if __name__ == "__main__":
    main()
