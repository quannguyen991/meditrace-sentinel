# -*- coding: utf-8 -*-
"""MODEL_CHINH phai la Qwen3-4B: moi lan huan luyen va chay that deu dung 4B.

Hang so nay la mac dinh cua `--model` o `src/huan_luyen/huan_luyen_sft.py` va `src/duong_ong/chay_duong_ong.py`.
De la Qwen3-8B thi quen go `--model` se huan luyen nham mo hinh khong vua RTX 3060.
Khong dat trong `test_duong_dan.py` vi tep do bi bo qua ca tep khi thieu
thu muc `D:/VAIC DE @`.
"""
from src.he_thong import duong_dan as duong_dan


def test_model_chinh_la_qwen3_4b():
    assert duong_dan.MODEL_CHINH == "Qwen/Qwen3-4B"
