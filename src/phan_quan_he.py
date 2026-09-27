# -*- coding: utf-8 -*-
"""Phan xu quan he cho TUNG CAP ung vien — buoc con thieu cua lop 2.

VI SAO CO TEP NAY.

`bakeoff.trich` bat mo hinh vua liet ke phat bieu VUA tu danh dau `quan_he`
trong cung mot luot sinh. Do la bai toan **khoi phat**: mo hinh phai tu nho
rang minh vua ghi mot ban ghi tuong tu o dau do phia truoc, tu quay lai doi
chieu, roi tu quyet dinh ghi them mot truong khong ai hoi.

Tren hoi thoai 4 luot tu sinh thi lam duoc. Tren hoi thoai 10-28 luot cua nguoi
that thi khong: `quan_he` bang "khong" o **282/282** phat bieu, trong khi
21/35 hoi thoai co moc kieu "hom qua... hom nay..." — dung dang `dien bien`.

`ung_vien_quan_he.sinh_cap` da giai nua dau: chuong trinh liet ke cap dang ngo,
vet can theo cau truc. Tep nay giai nua sau: **hoi mo hinh mot cau bon lua chon
tren mot cap**, thay vi bat no tu tim quan he trong toan bo danh sach.

    truoc:  mo hinh doc 28 luot, tu nho, tu doi chieu, tu ghi them truong
    nay:    chuong trinh dua ra 2 phat bieu + cac luot thoai lam bang chung
            mo hinh chi tra loi: bo sung / dinh chinh / dien bien /
                                 mau thuan / khong

BA DUONG PHAN, xep theo chi phi tang dan. Ca ba deu tra ve cung mot kieu du
lieu nen thay nhau duoc, va deu la doi chung cua nhau:

    luat      goi_y_bang_luat, khong GPU. Duong lui khi khong co may, VA la
              doi chung: mo hinh khong hon luat nay thi buoc phan bang mo
              hinh khong dang chi phi.
    mo_hinh   mot luot goi mo hinh cho moi cap.
    ca_hai    luat quyet truoc; cap nao luat tra None thi moi hoi mo hinh.
              Re nhat trong ba, vi phan lon cap co dau hieu be mat.

KHONG doan bua. Ca ba duong deu duoc phep tra `None` (= khong co quan he).
Quan he gia nguy hiem hon la khong co quan he: `cap_nhat.ap_luat` se danh dau
mot ban ghi DUNG thanh "bi thay the" va vut no khoi benh an.
"""
import json
import re
from typing import Dict, List, Optional, Tuple

from src import ung_vien_quan_he as uv
from src.phat_bieu import QUAN_HE, PhatBieu

# "khong" khong nam trong QUAN_HE (do la bo bon gia tri quan he THAT). No la
# dap an thu nam cua cau hoi, va duoc dich thanh None truoc khi tra ra.
KHONG = "không"
DAP_AN = tuple(QUAN_HE) + (KHONG,)

# Ep dau ra ve dung mot truong. Cang it truong cang it cho hong: o day chi can
# mot nhan, khong can loi giai thich — loi giai thich cua mo hinh 4B khong
# dung de kiem tra duoc, chi lam ton token va tang co hoi lech dinh dang.
LUOC_DO_PHAN = {
    "type": "object",
    "properties": {"quan_he": {"type": "string", "enum": list(DAP_AN)}},
    "required": ["quan_he"],
}

HUONG_DAN = """Bạn được cho HAI phát biểu lấy từ cùng một cuộc hội thoại khám bệnh, kèm những lượt thoại mà chúng dựa vào.

Hãy xác định quan hệ giữa phát biểu B với phát biểu A. Chỉ chọn MỘT trong năm đáp án:

- "bổ sung": B thêm thông tin cho A. Cả hai cùng đúng.
- "đính chính": người nói đã nói sai ở A và sửa lại thành B. A không còn đúng nữa.
- "diễn biến": A và B nói về HAI THỜI ĐIỂM khác nhau. Cả hai đều đúng, không cái nào thay thế cái nào.
- "mâu thuẫn": A và B trái nhau, và trong hội thoại không ai xác nhận lại cái nào đúng.
- "không": A và B không liên quan tới nhau, hoặc chỉ tình cờ giống chữ.

Phân biệt quan trọng nhất:
- "đính chính" là MỘT sự thật bị nói nhầm rồi sửa ("sốt 4 ngày... à không, 2 ngày").
- "diễn biến" là HAI sự thật ở hai thời điểm ("hôm qua nôn, hôm nay hết nôn").

Nếu không có căn cứ rõ trong lượt thoại, hãy chọn "không".

Chỉ trả về JSON dạng {"quan_he": "..."}."""


# ------------------------------------------------------------------ cau hoi

def _mo_ta(p: PhatBieu) -> str:
    """Mot dong mo ta mot phat bieu. Chi in truong CO gia tri — truong rong in
    ra chi lam nhieu, va lam mo hinh tuong la co thong tin o do."""
    phan = [f"nội dung: {p.noi_dung}"]
    if p.ten_chu_the:
        phan.append(f"chủ thể: {p.ten_chu_the}")
    if p.moc_thoi_gian:
        phan.append(f"mốc thời gian: {p.moc_thoi_gian}")
    if p.do_chac_chan != "chắc chắn":
        phan.append(f"mức chắc chắn: {p.do_chac_chan}")
    if p.phu_dinh:
        phan.append("phủ định: có")
    if p.tinh_huong != "thực tế":
        phan.append(f"tình huống: {p.tinh_huong}")
    return "; ".join(phan)


def cau_hoi(cap: uv.CapUngVien, danh_sach: List[PhatBieu],
            luot_thoai: Optional[Dict[int, str]] = None) -> str:
    """Dung cau hoi cho MOT cap. Ham thuan tuy — test duoc khong can GPU.

    Luot thoai duoc in NGUYEN VAN kem so thu tu, vi dau hieu dinh chinh
    ("a khong", "nham roi") nam trong loi noi chu khong nam trong truong nao
    cua ban ghi. Bo luot thoai di la cat mat can cu chinh cua cau hoi.
    """
    theo_id = {p.id: p for p in danh_sach}
    a, b = theo_id.get(cap.a), theo_id.get(cap.b)
    if a is None or b is None:
        raise KeyError(f"cap tro toi ban ghi khong co: {cap.a}, {cap.b}")

    luot_thoai = luot_thoai or {}
    so_luot = sorted(set(a.bang_chung) | set(b.bang_chung))
    trich = "\n".join(f"{s}. {luot_thoai.get(s, '(không có lượt này)')}"
                      for s in so_luot) or "(không có lượt thoại kèm theo)"

    return (f"{HUONG_DAN}\n\n"
            f"Phát biểu A: {_mo_ta(a)}\n"
            f"Phát biểu B: {_mo_ta(b)}\n\n"
            f"Các lượt thoại liên quan:\n{trich}")


# --------------------------------------------------------------- doc dap an

def doc_dap_an(van_ban: str) -> Optional[str]:
    """-> mot gia tri trong QUAN_HE, hoac None.

    Chap nhan ca JSON lan van xuoi: khi khong ep duoc lm-format-enforcer thi
    mo hinh van tra loi duoc, chi la lon xon hon. Khong ep duoc ma van doc
    duoc thi ca co che chay tiep tren may khong cai duoc thu vien do.

    "khong" -> None. Rac -> None. Khong bao gio doan.
    """
    van = (van_ban or "").strip()
    try:
        d = json.loads(re.search(r"\{.*?\}", van, re.S).group(0))
        gia_tri = str(d.get("quan_he", "")).strip().lower()
    except Exception:                                       # noqa: BLE001
        gia_tri = ""
    if not gia_tri:
        # Van xuoi: tim nhan dai nhat xuat hien trong cau. Xet "dinh chinh"
        # truoc "bo sung" vi mot cau co the chua ca hai tu; uu tien nhan
        # NAO DAI HON de "khong" khong nuot mat "khong ro rang".
        thap = van.lower()
        ung = [d for d in DAP_AN if d in thap]
        if not ung:
            return None
        gia_tri = max(ung, key=len)
    return gia_tri if gia_tri in QUAN_HE else None


# ------------------------------------------------------------- ba duong phan

def phan_bang_luat(caps: List[uv.CapUngVien], danh_sach: List[PhatBieu],
                   luot_thoai: Dict[int, str]) -> Dict[Tuple[int, int], Optional[str]]:
    """Doi chung khong GPU. Chi tra loi khi co dau hieu be mat, con lai None."""
    return {c.khoa(): uv.goi_y_bang_luat(c, danh_sach, luot_thoai) for c in caps}


def phan_bang_mo_hinh(caps: List[uv.CapUngVien], danh_sach: List[PhatBieu],
                      luot_thoai: Dict[int, str], tok, model,
                      prefix_fn=None, max_token=24,
                      bo_qua=None) -> Dict[Tuple[int, int], Optional[str]]:
    """Mot luot goi mo hinh cho moi cap.

    `max_token=24` du cho `{"quan_he": "đính chính"}` va khong du cho mo hinh
    bat dau giai thich dai dong — dat that thap la mot cach chan re.

    `bo_qua`: cac cap da co dap an tu duong khac, khong hoi lai. Day la cho
    duong `ca_hai` tiet kiem: cap nao luat da quyet thi khong ton mot luot goi.
    """
    import torch

    bo_qua = bo_qua or {}
    ra: Dict[Tuple[int, int], Optional[str]] = {}
    for c in caps:
        if c.khoa() in bo_qua and bo_qua[c.khoa()] is not None:
            ra[c.khoa()] = bo_qua[c.khoa()]
            continue
        msgs = [{"role": "user", "content": cau_hoi(c, danh_sach, luot_thoai)}]
        prompt = tok.apply_chat_template(msgs, tokenize=False,
                                         add_generation_prompt=True,
                                         enable_thinking=False)
        inp = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=max_token, do_sample=False,
                                 pad_token_id=tok.eos_token_id,
                                 prefix_allowed_tokens_fn=prefix_fn)
        sinh = tok.decode(out[0][inp["input_ids"].shape[1]:],
                          skip_special_tokens=True)
        ra[c.khoa()] = doc_dap_an(sinh)
    return ra


def ep_json_phan(tok):
    """Ep dau ra theo LUOC_DO_PHAN. Giong `bakeoff._ep_json` nhung luoc do khac.

    Khong cai duoc thi tra None va NOI RO — im lang o day se thanh mot phep so
    sanh khong con dieu kien giong nhau giua cac lan chay.
    """
    try:
        from lmformatenforcer import JsonSchemaParser
        from lmformatenforcer.integrations.transformers import (
            build_transformers_prefix_allowed_tokens_fn)
        return build_transformers_prefix_allowed_tokens_fn(
            tok, JsonSchemaParser(LUOC_DO_PHAN))
    except Exception as e:                                  # noqa: BLE001
        print(f"  (khong ep duoc JSON o buoc phan quan he: {e}; chay tu do)")
        return None


# --------------------------------------------------------------- cua duy nhat

def phan(danh_sach: List[PhatBieu], luot_thoai: Dict[int, str],
         duong: str = "luat", tok=None, model=None, prefix_fn=None,
         toi_da: int = uv.TOI_DA_MAC_DINH) -> Tuple[List[PhatBieu], dict]:
    """Sinh cap, phan xu, ap phan quyet. -> (danh sach MOI, thong ke).

    Day la cua duy nhat ma `nhanh.py` goi. Ba duong deu di qua day de thong ke
    duoc dem giong nhau — neu moi duong tu dem mot kieu thi bang so sanh giua
    chung khong con doc duoc.
    """
    assert duong in ("luat", "mo_hinh", "ca_hai"), duong
    caps = uv.sinh_cap(danh_sach, luot_thoai, toi_da=toi_da)
    if not caps:
        return danh_sach, {"so_cap": 0, "so_phan": 0, "bi_cat": False,
                           "theo_nhan": {}, "duong": duong}

    if duong == "luat":
        phan_quyet = phan_bang_luat(caps, danh_sach, luot_thoai)
    elif duong == "mo_hinh":
        phan_quyet = phan_bang_mo_hinh(caps, danh_sach, luot_thoai, tok, model,
                                       prefix_fn)
    else:
        theo_luat = phan_bang_luat(caps, danh_sach, luot_thoai)
        phan_quyet = phan_bang_mo_hinh(caps, danh_sach, luot_thoai, tok, model,
                                       prefix_fn, bo_qua=theo_luat)

    moi = uv.ap_phan_quyet(danh_sach, phan_quyet)
    theo_nhan: Dict[str, int] = {}
    for v in phan_quyet.values():
        if v:
            theo_nhan[v] = theo_nhan.get(v, 0) + 1
    # `so_phan` dem sau khi AP, khong dem phan quyet: `ap_phan_quyet` bo bot
    # cac canh tao vong hoac trung dich, nen hai so nay khac nhau va so DUNG
    # de bao cao la so canh thuc su duoc gan.
    return moi, {
        "so_cap": len(caps),
        "so_phan": sum(1 for p in moi if p.quan_he),
        "so_phan_quyet": sum(1 for v in phan_quyet.values() if v),
        "bi_cat": uv.da_bi_cat(danh_sach, toi_da),
        "theo_nhan": theo_nhan,
        "duong": duong,
    }
