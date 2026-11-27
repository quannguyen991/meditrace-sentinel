# -*- coding: utf-8 -*-
"""Hoi quy an toan cho src/he_thong/dich_vu_http.py: ep kieu bien vao, duong may xa, xac thuc HTTP."""
import http.client
import json
import threading
import types
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from src.he_thong import dich_vu_http as dich_vu
from src.he_thong.khu_dinh_danh import ClinicalDeidentifier

KHOA = "khoa-thu-noi-bo-123"


# ------------------------------------------------------------ ep kieu bien vao (muc 4)
def test_ho_so_ep_kieu_thong_tin_benh_nhan_o_bien_vao(monkeypatch):
    da_nhan = {}

    def ho_so_tho(than):
        da_nhan["than"] = than
        return {"id": "ca", "nhanh": "C_khoa", "nguon": "bo_dem", "phat_bieu": []}

    def them_canh_bao(r, thong_tin_benh_nhan=None, du_lieu_xet_nghiem=None):
        da_nhan["tt"], da_nhan["xn"] = thong_tin_benh_nhan, du_lieu_xet_nghiem
        return r

    monkeypatch.setattr(dich_vu, "_them_canh_bao", them_canh_bao)
    monkeypatch.setattr(dich_vu, "lay_worm_logger", lambda: types.SimpleNamespace(
        append_event=lambda **k: {"seq": 1, "curr_hash": "h"}))
    gia = types.SimpleNamespace(_ho_so_tho=ho_so_tho, headers={})
    than = {"input": "x", "thong_tin_benh_nhan": {"tuoi": "82", "egfr": "rac", "tuan_thai": "10"},
            "du_lieu_xet_nghiem": {"egfr": "25", "creatinine_unit": "mg/dL"}}
    dich_vu.May._ho_so(gia, than)
    assert da_nhan["than"]["thong_tin_benh_nhan"] == {"tuoi": 82, "tuan_thai": 10}
    assert da_nhan["tt"] == {"tuoi": 82, "tuan_thai": 10}
    assert da_nhan["xn"] == {"egfr": 25.0, "creatinine_unit": "mg/dL"}


# ------------------------------------------------------------ may xa gia (muc 8, 9)
HOI_THOAI = ("Bác sĩ: Bác tên gì ạ?\n"
             "Bệnh nhân: Tôi tên là Trần Văn Bình, số tôi 0912 345 678.\n"
             "Bác sĩ: Bác tiếp tục uống metformin 850mg ngày 2 lần nhé.")


class _MayXaGia(BaseHTTPRequestHandler):
    nhan = []

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        than = json.loads(self.rfile.read(n))
        _MayXaGia.nhan.append({"than": than, "headers": self.headers})
        r = {
            "id": than["ca_id"], "input": than["input"], "nhanh": than["nhanh"], "nguon": "mo_hinh",
            "du_doan": "KẾ HOẠCH: metformin 850mg",
            "phat_bieu": [{"id": 1, "nguoi_noi": "bác sĩ", "chu_the_id": 0,
                           "noi_dung": "Metformin 850mg ngày 2 lần", "hanh_vi": "kế hoạch",
                           "thuoc": {"ten": "Metformin", "lieu": "850mg"}, "bang_chung": [3]}],
            # may xa tinh lop lam sang KHONG co thong tin benh nhan -> phai bi tinh lai tai cho
            "lam_sang_nang_cao": {"gia_tu_may_xa": True},
        }
        du = json.dumps(r, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(du)))
        self.end_headers()
        self.wfile.write(du)

    def log_message(self, *a):
        pass


@pytest.fixture
def may_xa():
    _MayXaGia.nhan = []
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _MayXaGia)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


@pytest.fixture
def worm_gia(monkeypatch):
    ghi = []

    def append_event(**k):
        ghi.append(k)
        return {"seq": len(ghi), "curr_hash": "h"}

    monkeypatch.setattr(dich_vu, "lay_worm_logger", lambda: types.SimpleNamespace(append_event=append_event))
    return ghi


def test_duong_may_xa_tinh_lai_lam_sang_tai_cho_va_khong_gui_thong_tin_bn(may_xa, worm_gia, monkeypatch):
    monkeypatch.setenv("MEDITRACE_INTERNAL_TOKEN", KHOA)
    loi = dich_vu.Loi(cho_nap_mo_hinh=False, mo_hinh_xa=may_xa)
    loi._dem, loi._dem_theo_chu = {}, {}
    gia = types.SimpleNamespace(headers={})
    gia._ho_so_tho = lambda than: dich_vu.May._ho_so_tho(
        types.SimpleNamespace(loi=loi, _kiem_ma_phien=dich_vu.May._kiem_ma_phien), than)
    than = {"input": HOI_THOAI, "ca_id": "ca_xa",
            "thong_tin_benh_nhan": {"ten": "Trần Văn Bình", "tuoi": 70, "can_nang_kg": 55},
            "du_lieu_xet_nghiem": {"egfr": "22"}}
    kq = dich_vu.May._ho_so(gia, than)

    assert len(_MayXaGia.nhan) == 1
    gui = _MayXaGia.nhan[0]
    # may xa khong thay PHI va khong nhan thong tin benh nhan / xet nghiem
    assert "Trần Văn Bình" not in gui["than"]["input"]
    assert "0912 345 678" not in gui["than"]["input"]
    assert "thong_tin_benh_nhan" not in gui["than"] and "du_lieu_xet_nghiem" not in gui["than"]
    # gui kem khoa noi bo cho may xa
    assert gui["headers"].get("X-MediTrace-Internal-Token") == KHOA
    # lop lam sang duoc tinh LAI tai cho voi thong tin benh nhan (eGFR 22 -> metformin CRITICAL)
    ls = kq["lam_sang_nang_cao"]
    assert "gia_tu_may_xa" not in ls
    assert ls["hieu_chinh_lieu"]["co_canh_bao_critical"] is True
    # PII duoc khoi phuc tai cho
    assert "Trần Văn Bình" in kq["input"]
    assert kq["da_khu_dinh_danh_truoc_gui_xa"] is True


def test_duong_may_xa_tu_choi_khi_con_sot_pii(may_xa, monkeypatch):
    monkeypatch.setenv("MEDITRACE_INTERNAL_TOKEN", KHOA)
    loi = dich_vu.Loi(cho_nap_mo_hinh=False, mo_hinh_xa=may_xa)
    loi._dem, loi._dem_theo_chu = {}, {}
    monkeypatch.setattr(ClinicalDeidentifier, "kiem_tra_con_sot",
                        classmethod(lambda cls, vb: [{"loai": "SDT", "vi_tri": [0, 1]}]))
    with pytest.raises(dich_vu.LoiDichVu) as e:
        loi.ho_so("ca_xa", HOI_THOAI, "C_khoa")
    assert e.value.ma == "khu_dinh_danh_chua_sach"
    assert _MayXaGia.nhan == []                      # KHONG gui gi ra may xa


# ------------------------------------------------------------ HTTP (muc 10)
class _MayThu(dich_vu.May):
    def log_message(self, *a):
        pass


@pytest.fixture
def may_http(monkeypatch, worm_gia):
    _MayThu.loi = dich_vu.Loi(cho_nap_mo_hinh=False)
    _MayThu.am = types.SimpleNamespace(
        cau_hinh_nhe=lambda: types.SimpleNamespace(asr_provider="x", asr_model="y", whisper_model="z",
                                                   diarization_provider="mot-nguoi"))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _MayThu)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield srv.server_address[1]
    srv.shutdown()
    srv.server_close()


def _goi(cong, phuong, duong, than=None, headers=None, tho=None):
    conn = http.client.HTTPConnection("127.0.0.1", cong, timeout=10)
    du = tho if tho is not None else (json.dumps(than).encode("utf-8") if than is not None else None)
    conn.putrequest(phuong, duong, skip_host=bool(headers and "Host" in headers))
    for k, v in (headers or {}).items():
        conn.putheader(k, v)
    if du is not None and not (headers and "Content-Length" in headers):
        conn.putheader("Content-Length", str(len(du)))
    # gui header + than trong mot lan (may chu co the tu choi va dong ket noi truoc khi doc than)
    conn.endheaders(message_body=du)
    r = conn.getresponse()
    body = r.read()
    conn.close()
    try:
        return r.status, json.loads(body.decode("utf-8") or "{}")
    except ValueError:
        return r.status, {}


def test_khong_cau_hinh_khoa_thi_tu_choi_moi_api_tru_suc_khoe(may_http, monkeypatch):
    monkeypatch.delenv("MEDITRACE_INTERNAL_TOKEN", raising=False)
    monkeypatch.setattr(_MayThu, "khoa_noi_bo", None, raising=False)
    assert _goi(may_http, "GET", "/api/suc-khoe")[0] == 200
    for phuong, duong in (("GET", "/api/phien/abc"), ("GET", "/api/ca-mau"),
                          ("POST", "/api/ocr/phieu-cu")):
        st, d = _goi(may_http, phuong, duong, than={"text": "Creatinin 1.2"} if phuong == "POST" else None)
        assert st in (401, 403, 503), (duong, st)


def test_khoa_sai_bi_tu_choi_khoa_dung_qua(may_http, monkeypatch):
    monkeypatch.setenv("MEDITRACE_INTERNAL_TOKEN", KHOA)
    st, _ = _goi(may_http, "GET", "/api/phien/abc", headers={"X-MediTrace-Internal-Token": "sai"})
    assert st == 403
    st, _ = _goi(may_http, "GET", "/api/ca-mau", headers={"X-MediTrace-Internal-Token": KHOA})
    assert st == 200


def test_khoa_tu_tao_luc_khoi_dong_duoc_dung(may_http, monkeypatch, tmp_path):
    monkeypatch.delenv("MEDITRACE_INTERNAL_TOKEN", raising=False)
    tep = tmp_path / "khoa.txt"
    k1 = dich_vu.nap_hoac_tao_khoa_noi_bo(tep)
    assert len(k1) >= 32 and tep.read_text(encoding="utf-8").strip() == k1
    assert dich_vu.nap_hoac_tao_khoa_noi_bo(tep) == k1          # on dinh qua cac lan khoi dong
    monkeypatch.setattr(_MayThu, "khoa_noi_bo", k1, raising=False)
    assert _goi(may_http, "GET", "/api/ca-mau", headers={"X-MediTrace-Internal-Token": k1})[0] == 200
    assert _goi(may_http, "GET", "/api/ca-mau")[0] == 403


def test_host_la_bi_tu_choi(may_http, monkeypatch):
    monkeypatch.setenv("MEDITRACE_INTERNAL_TOKEN", KHOA)
    st, d = _goi(may_http, "GET", "/api/ca-mau",
                 headers={"Host": "evil.example.com", "X-MediTrace-Internal-Token": KHOA})
    assert st == 403 and d.get("loi") == "host_khong_hop_le"
    st, _ = _goi(may_http, "GET", "/api/suc-khoe", headers={"Host": "evil.example.com"})
    assert st == 403
    st, _ = _goi(may_http, "GET", "/api/ca-mau",
                 headers={"Host": "localhost:8765", "X-MediTrace-Internal-Token": KHOA})
    assert st == 200


@pytest.mark.parametrize("cl,ma", [("-5", 400), ("abc", 400), ("1.5", 400),
                                   (str(dich_vu.GIOI_HAN_THAN + 1), 413)])
def test_content_length_khong_hop_le(may_http, monkeypatch, cl, ma):
    monkeypatch.setenv("MEDITRACE_INTERNAL_TOKEN", KHOA)
    st, _ = _goi(may_http, "POST", "/api/ocr/phieu-cu", tho=b"{}",
                 headers={"X-MediTrace-Internal-Token": KHOA, "Content-Length": cl})
    assert st == ma


def test_user_id_trong_than_chi_la_khai_bao(may_http, monkeypatch, worm_gia):
    monkeypatch.setenv("MEDITRACE_INTERNAL_TOKEN", KHOA)
    monkeypatch.setattr(dich_vu.May, "_ho_so_tho",
                        lambda self, than: {"id": "ca1", "nhanh": "C_khoa", "nguon": "chay_truoc",
                                            "phat_bieu": []})
    st, _ = _goi(may_http, "POST", "/api/ho-so", than={"input": "x", "user_id": "bs_gia_mao"},
                 headers={"X-MediTrace-Internal-Token": KHOA})
    assert st == 200
    ev = worm_gia[-1]
    assert ev["user_id"] != "bs_gia_mao"
    assert ev["user_id"].startswith(dich_vu.CHU_THE_NOI_BO)
    assert "khai_bao" in ev["user_id"] and ev["payload"]["user_id_khai_bao"] == "bs_gia_mao"
