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
import io
import json
import os
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src import duong_dan

NHANH_CHO_PHEP = ("C_khoa", "C_khoa_hoi", "C", "B")
MAX_TOKEN = 3072
GIOI_HAN_AM_THANH = 40 * 1024 * 1024        # 40 MB
THU_MUC_PHIEN = duong_dan.GOC_DU_AN / "data" / "audio" / "phien-dich-vu"
THU_MUC_CHAY_TRUOC = duong_dan.GOC_DU_AN / "kaggle-ra" / "the-he-8-chinh-sach-C"
THU_MUC_BO = duong_dan.GOC_DU_AN / "kaggle-ra" / "the-he-8"


class LoiDichVu(Exception):
    def __init__(self, ma, thong_diep, code=400):
        super().__init__(thong_diep)
        self.ma, self.thong_diep, self.code = ma, thong_diep, code


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
        self._dem = None

    # -- bo dem khau trich (chay lai trong vai giay, khong can GPU) -------
    @property
    def dem(self):
        if self._dem is None:
            self._dem, self._dem_theo_chu = {}, {}
            for tep in sorted((duong_dan.GOC_DU_AN / "data").glob("trich_*_hl.jsonl")):
                for dong in open(tep, encoding="utf-8"):
                    if dong.strip():
                        b = json.loads(dong)
                        self._dem.setdefault(b["id"], b)
            # Tep dem chi co ma ca, khong co loi thoai. Giao dien lai gui LOI THOAI. Dung
            # chi muc loi thoai -> ma ca tu chinh cac bo du lieu de tra nguoc lai.
            for tep in sorted(THU_MUC_BO.glob("*.jsonl")):
                if tep.name.startswith("ra_"):
                    continue
                for dong in open(tep, encoding="utf-8"):
                    if not dong.strip():
                        continue
                    c = json.loads(dong)
                    if c.get("id") in self._dem and c.get("input"):
                        self._dem_theo_chu.setdefault(" ".join(c["input"].split()), self._dem[c["id"]])
        return self._dem

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

    def thiet_bi(self):
        try:
            import torch
            return f"cuda ({torch.cuda.get_device_name(0)})" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "khong ro"

    def _ho_so_xa(self, ca_id, hoi_thoai, nhanh):
        """Chuyen nguyen yeu cau sang dich vu o may khac; ket qua giu `nguon` = mo_hinh."""
        import urllib.error
        import urllib.request
        du = json.dumps({"input": hoi_thoai, "nhanh": nhanh, "ca_id": ca_id}, ensure_ascii=False).encode("utf-8")
        yc = urllib.request.Request(f"{self.mo_hinh_xa}/api/ho-so", data=du,
                                    headers={"Content-Type": "application/json"})
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
    def ho_so(self, ca_id, hoi_thoai, nhanh="C_khoa"):
        """-> ban ghi ket qua cua `src.nhanh.chay_trung_gian` + truong `nguon`."""
        if nhanh not in NHANH_CHO_PHEP:
            raise LoiDichVu("nhanh_khong_hop_le", f"nhánh {nhanh} không dùng được ở dịch vụ này")
        from src import nhanh as _nhanh
        mau = [{"id": ca_id, "input": hoi_thoai}]
        dem = self.dem.get(ca_id)
        if dem is None or dem.get("input", hoi_thoai) != hoi_thoai:
            dem = self.dem_theo_chu(hoi_thoai)        # khong co ma ca thi tra theo loi thoai
            if dem is not None:
                mau[0]["id"] = ca_id = dem["id"]
        if dem is not None:
            tok = model = prefix_fn = None
            kq_tho, nguon = [dem], "bo_dem"
        elif self.mo_hinh_xa:
            return self._ho_so_xa(ca_id, hoi_thoai, nhanh)
        else:
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
        return r


# ----------------------------------------------------------------- am thanh

class AmThanh:
    def __init__(self):
        self._pipe = None
        self._khoa = threading.Lock()

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
        pipe.process(phien, tach_nguoi_noi=tach_nguoi_noi)
        return phien, pipe.transcript(phien)


def _doan_ra_json(t):
    return {k: t.get(k) for k in ("segment_id", "start_time", "end_time", "text_original",
                                  "text_normalized", "speaker_id", "speaker_role",
                                  "asr_confidence", "asr_provider", "asr_model",
                                  "asr_review_required", "asr_review_reason", "asr_candidates",
                                  "reviewed", "edited")}


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
    """Danh sach ca da chay truoc, de demo khi GPU ban."""
    ra = []
    for tep in sorted(THU_MUC_CHAY_TRUOC.glob("ra_C_khoa_*.jsonl")):
        if "C_khoa_hoi" in tep.name:
            continue
        ten_bo = tep.name[len("ra_C_khoa_"):-len(".jsonl")]
        if bo and bo != ten_bo:
            continue
        for dong in open(tep, encoding="utf-8"):
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
    if nhanh == "C_khoa_hoi":
        for tep in sorted(THU_MUC_CHAY_TRUOC.glob("ra_C_khoa_hoi_*.jsonl")):
            for dong in open(tep, encoding="utf-8"):
                if dong.strip():
                    r = json.loads(dong)
                    if r["id"] == ca_id:
                        r["nhanh"] = "C_khoa_hoi"
                        return r
    for tep in sorted(THU_MUC_CHAY_TRUOC.glob("ra_C_khoa_*.jsonl")):
        if "C_khoa_hoi" in tep.name:
            continue
        for dong in open(tep, encoding="utf-8"):
            if dong.strip():
                r = json.loads(dong)
                if r["id"] == ca_id:
                    return r
    raise LoiDichVu("khong_co_ca", f"không có ca {ca_id} trong thư mục ca mẫu", 404)


# ----------------------------------------------------------------- HTTP

class May(BaseHTTPRequestHandler):
    server_version = "MediTrace/1.0"
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
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(du)

    def _than(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > GIOI_HAN_AM_THANH * 2:
            raise LoiDichVu("qua_lon", "nội dung gửi lên quá lớn", 413)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError as exc:
            raise LoiDichVu("json_hong", str(exc))

    def do_OPTIONS(self):
        self._tra({}, 204)

    def do_GET(self):
        try:
            duong = self.path.split("?")[0]
            tham = dict(x.split("=", 1) for x in self.path.split("?")[1].split("&")) \
                if "?" in self.path else {}
            if duong == "/api/suc-khoe":
                from src import cham_he_thong, cong_rui_ro
                return self._tra({
                    "ok": True, "mo_hinh": self.loi.ten_mo_hinh, "adapter_trich": self.loi.adapter_trich,
                    "da_nap_mo_hinh": self.loi.da_nap(), "cho_nap_mo_hinh": self.loi.cho_nap_mo_hinh,
                    "mo_hinh_xa": self.loi.mo_hinh_xa,
                    "thiet_bi": self.loi.thiet_bi(), "so_ca_bo_dem": len(self.loi.dem),
                    "chinh_sach_cong": cong_rui_ro.CHINH_SACH, "bo_cham": cham_he_thong.PHIEN_BAN,
                    "asr": {"nha_cung_cap": self.am.pipeline().settings.asr_provider,
                            "mo_hinh": self.am.pipeline().settings.asr_model},
                    "tach_nguoi_noi": self.am.pipeline().settings.diarization_provider,
                })
            if duong == "/api/ca-mau":
                return self._tra({"ca": ca_mau(tham.get("bo"))})
            if duong.startswith("/api/phien/"):
                phien = duong[len("/api/phien/"):]
                pipe = self.am.pipeline()
                return self._tra({"phien": phien,
                                  "doan": [_doan_ra_json(t) for t in pipe.transcript(phien)],
                                  "tach_nguoi_noi": pipe.store.load(phien).get("tach_nguoi_noi") or {}})
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
            duong = self.path.split("?")[0]
            than = self._than()
            if duong == "/api/chep-am":
                return self._tra(self._chep_am(than))
            if duong == "/api/gan-vai":
                phien = than.get("phien")
                vai = than.get("vai") or {}
                if not phien or not vai:
                    raise LoiDichVu("thieu_tham_so", "cần `phien` và `vai`")
                doan = self.am.pipeline().map_speakers(phien, vai)
                return self._tra({"phien": phien, "doan": [_doan_ra_json(t) for t in doan]})
            if duong == "/api/ho-so":
                return self._tra(self._ho_so(than))
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
        return _them_canh_bao(self._ho_so_tho(than))

    def _ho_so_tho(self, than):
        nhanh = than.get("nhanh") or "C_khoa"
        ca_id = than.get("ca_id") or f"ui_{int(time.time())}"
        if than.get("chay_truoc"):
            r = doc_ca(than["chay_truoc"], nhanh)
            r["nguon"], r["giay_xu_ly"] = "chay_truoc", 0.0
            r.setdefault("nhanh", "C_khoa")
            return r
        if than.get("phien"):
            from src.audio.adapter import to_meditrace
            doan = self.am.pipeline().transcript(than["phien"])
            try:
                vao = to_meditrace(doan, strict=True)
            except ValueError as exc:
                raise LoiDichVu(str(exc), "Chưa gán vai cho người nói, hoặc còn đoạn chờ người duyệt.", 409)
            hoi_thoai = vao["input"]
        else:
            hoi_thoai = (than.get("input") or "").strip()
        if not hoi_thoai:
            raise LoiDichVu("thieu_hoi_thoai", "cần `input`, `phien` hoặc `chay_truoc`")
        return self.loi.ho_so(ca_id, hoi_thoai, nhanh)

    def _bao_loi(self, exc):
        if isinstance(exc, LoiDichVu):
            return self._tra({"loi": exc.ma, "thong_diep": exc.thong_diep}, exc.code)
        traceback.print_exc()
        self._tra({"loi": "loi_khong_ro", "thong_diep": f"{type(exc).__name__}: {exc}"}, 500)

    def log_message(self, dang, *a):
        print(f"[dich-vu] {self.address_string()} {dang % a}", flush=True)


def _them_canh_bao(r):
    """Ban ghi chay truoc / tu may xa chua co lop canh bao (24/09/2026): tinh tai day
    tu phat bieu va loi thoai. Chi THEM truong `canh_bao`; ban nhap giu nguyen."""
    if not isinstance(r, dict) or r.get("canh_bao") or not r.get("phat_bieu") or not r.get("input"):
        return r
    from src.canh_bao import gop
    from src.phat_bieu import PhatBieu
    try:
        ps = [PhatBieu(**d) for d in r["phat_bieu"]]
        r["canh_bao"] = gop.to_dict(gop.chay(ps, r["input"]))
    except Exception:
        traceback.print_exc()
        r["canh_bao_loi"] = "không tính được lớp cảnh báo cho bản ghi này"
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
