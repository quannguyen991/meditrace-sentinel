"""Bộ đệm khâu trích tự ghi khi chạy trước ca demo (MEDITRACE_DEM_TU_DONG=bat, mặc định tắt)."""
import json

from src.he_thong import dich_vu_http as dv


def _loi(tmp_path, monkeypatch):
    monkeypatch.setattr(dv.duong_dan, "GOC_DU_AN", tmp_path)
    (tmp_path / "data").mkdir(exist_ok=True)
    monkeypatch.setattr(dv, "THU_MUC_BO", tmp_path / "khong-co")
    loi = dv.Loi.__new__(dv.Loi)
    import threading
    loi._khoa_dem = threading.Lock()
    loi._dem, loi._dem_theo_chu = None, {}
    return loi


BAN_THO = {"so_luot": 2, "json_hop_le": True, "ly_do": "", "phat_bieu": [{"noi_dung": "chóng mặt", "luot_thoai": [2]}]}
LOI_THOAI = "Bác sĩ: Chú bị sao ạ?\nBệnh nhân: Tôi chóng mặt."


def test_mac_dinh_tat_khong_ghi(tmp_path, monkeypatch):
    monkeypatch.delenv("MEDITRACE_DEM_TU_DONG", raising=False)
    loi = _loi(tmp_path, monkeypatch)
    assert loi.luu_dem(LOI_THOAI, BAN_THO) is False
    assert not (tmp_path / "data" / "trich_dem_dich_vu_hl.jsonl").exists()


def test_bat_thi_ghi_va_tra_lai_theo_loi_thoai(tmp_path, monkeypatch):
    monkeypatch.setenv("MEDITRACE_DEM_TU_DONG", "bat")
    loi = _loi(tmp_path, monkeypatch)
    assert loi.luu_dem(LOI_THOAI, BAN_THO) is True
    dong = (tmp_path / "data" / "trich_dem_dich_vu_hl.jsonl").read_text(encoding="utf-8").strip()
    assert json.loads(dong)["input"] == LOI_THOAI
    # tiến trình mới (nạp lại từ đĩa) vẫn tra được, khoảng trắng khác vẫn khớp
    loi2 = _loi(tmp_path, monkeypatch)
    b = loi2.dem_theo_chu(LOI_THOAI.replace("\n", "\r\n  "))
    assert b is not None and b["phat_bieu"][0]["noi_dung"] == "chóng mặt"


def test_khong_ghi_ban_tho_json_hong(tmp_path, monkeypatch):
    monkeypatch.setenv("MEDITRACE_DEM_TU_DONG", "bat")
    loi = _loi(tmp_path, monkeypatch)
    assert loi.luu_dem(LOI_THOAI, {**BAN_THO, "json_hop_le": False}) is False
