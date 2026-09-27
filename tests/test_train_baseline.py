# -*- coding: utf-8 -*-
"""Test ba sua doi CO THE test duoc bang may cua Task 6.

Sua doi thu tu (bf16, so buoc) nam trong TrainingArguments, chi doc mat duoc.
Ba cai con lai la hanh vi, va sai mot cai la hong ca 200 buoc train:

  1. mau qua dai bi LOAI, khong bi cat duoi
  2. mat na nhan che dung phan loi nhac, giu dung phan benh an
  3. `enable_thinking=False` duoc truyen o CA hai lan goi template

Khong tai tokenizer that — dung tokenizer gia, mot ky tu mot token, de do dai
tinh duoc bang tay.
"""
import json

import pytest

from src import train_baseline as tb


class TokGia:
    """Mot ky tu = mot token. Template gan nhan bang the chu."""

    eos_token = "<E>"
    pad_token = None

    def __init__(self):
        self.co_thinking = []          # ghi lai enable_thinking moi lan goi

    def apply_chat_template(self, msgs, tokenize=False,
                            add_generation_prompt=False, enable_thinking=None):
        self.co_thinking.append(enable_thinking)
        van = "[S]" + msgs[0]["content"] + "[U]" + msgs[1]["content"]
        if len(msgs) > 2:
            van += "[A]" + msgs[2]["content"]
        if add_generation_prompt:
            van += "[A]"
        return van

    def encode(self, s, add_special_tokens=False):
        return [ord(c) for c in s]

    def decode(self, ids):
        return "".join(chr(i) for i in ids)


def viet_jsonl(tmp_path, mau):
    p = tmp_path / "m.jsonl"
    p.write_text("\n".join(json.dumps(m, ensure_ascii=False) for m in mau),
                 encoding="utf-8")
    return p


def test_mau_qua_dai_bi_LOAI_chu_khong_bi_cat():
    """Cat tu duoi la cat mat benh an — tuc cat mat chinh cai can hoc."""
    tok = TokGia()
    dai = {"id": "dai", "input": "x" * 5000, "output": "BỆNH ÁN dài"}
    ngan = {"id": "ngan", "input": "ho 2 ngày", "output": "BỆNH ÁN ngắn"}
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        p = viet_jsonl(pathlib.Path(d), [dai, ngan])
        tap = tb.TapLamSang(p, tok, do_dai_toi_da=1024)
    assert [m["id"] for m in tap.mau] == ["ngan"]
    assert tap.bi_loai == ["dai"]


def test_mat_na_che_loi_nhac_va_giu_nguyen_benh_an():
    tok = TokGia()
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        p = viet_jsonl(pathlib.Path(d), [{"id": "a", "input": "ho", "output": "BỆNH ÁN"}])
        tap = tb.TapLamSang(p, tok, do_dai_toi_da=1024)
    x = tap[0]
    nhan = [t for t in x["labels"] if t != -100]
    assert tok.decode(nhan) == "BỆNH ÁN" + tok.eos_token
    che = sum(1 for t in x["labels"] if t == -100)
    assert che == len(tok.encode(tb.dung_chuoi(tok, "ho")))


def test_mat_na_dai_bang_dung_input_ids():
    tok = TokGia()
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        p = viet_jsonl(pathlib.Path(d), [{"id": "a", "input": "ho", "output": "BA"}])
        tap = tb.TapLamSang(p, tok, do_dai_toi_da=1024)
    x = tap[0]
    assert len(x["labels"]) == len(x["input_ids"])


def test_enable_thinking_False_o_CA_HAI_lan_goi():
    """Qwen3 chen cap <think></think> rong neu de mac dinh. Chi tat mot ben
    thi chuoi nhac va chuoi du lech nhau, mat na nhan lech theo."""
    tok = TokGia()
    tb.dung_chuoi(tok, "ho")
    tb.dung_chuoi(tok, "ho", "BỆNH ÁN")
    assert tok.co_thinking == [False, False]


def test_kiem_mat_na_DUNG_LAI_khi_lech():
    """Phep kiem phai bao hong duoc, khong thi no vo dung."""
    tok = TokGia()

    class TapLech:
        mau = [{"id": "a", "output": "BỆNH ÁN đúng phải bắt đầu thế này"}]

        def __len__(self):
            return 1

        def __getitem__(self, i):
            return {"labels": [ord(c) for c in "SAI HOÀN TOÀN"]}

    with pytest.raises(SystemExit):
        tb.kiem_mat_na(TapLech(), tok, so_mau=1)


def test_kiem_mat_na_qua_khi_khop():
    tok = TokGia()
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        p = viet_jsonl(pathlib.Path(d),
                       [{"id": "a", "input": "ho", "output": "BỆNH ÁN. Lý do khám: ho."}])
        tap = tb.TapLamSang(p, tok, do_dai_toi_da=1024)
    tb.kiem_mat_na(tap, tok, so_mau=1)      # khong duoc nem


def test_loi_nhac_he_thong_la_CUA_MINH_khong_chep_cua_cuoc_thi():
    """Ban to chuc cuoc thi cu khuyen khong nen dung tai san cua ho de tranh
    cau hoi ve tinh chinh thong. Loi nhac he thong la tai san cuoi cung con
    sot lai — ban dau toi chep NGUYEN VAN tu `train.py` cua ho.

    Test nay giu cho no khong bi chep lai. Doc tep goc neu con tren may; may
    nao khong co tep do thi bo qua phan doi chieu, nhung van kiem noi dung.
    """
    from src import duong_dan
    s = tb.LOI_NHAC_HE_THONG

    goc = duong_dan.GOC_VAIC / "train.py"
    if goc.exists():
        van_goc = goc.read_text(encoding="utf-8")
        dong = [c.strip("- ").strip() for c in s.split("\n") if len(c.strip()) > 25]
        trung = [c for c in dong if c in van_goc]
        assert not trung, f"chep nguyen van tu train.py cua cuoc thi: {trung}"

    # Van phai day du chuc nang, khong duoc cat bot khi viet lai
    assert "ĐÚNG NGƯỜI" in s, "phai noi ro chuyen gan dung nguoi"
    assert "chưa ghi nhận" in s and "phủ định" in s
    assert "Không suy diễn" in s
    assert "Không tạo mục trống" in s
