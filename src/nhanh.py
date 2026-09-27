# -*- coding: utf-8 -*-
"""Nhanh A va A+ — hai moc so sanh cua du an.

  A   hoi thoai -> benh an, MOT luot goi. Day la baseline.
  A+  chay A, roi dua ca hoi thoai lan ban nhap cua A vao mo hinh va bao
      "tim cho sai va sua". HAI luot goi, khong bang trung gian, khong luat.

A+ la doi chung re nhung quan trong nhat cua du an. Neu A+ ngang C thi toan
bo bieu dien trung gian (ban ghi phat bieu, quan he, trang thai) la thua —
chi can bao mo hinh tu doc lai la du. Biet dieu do o tuan 4 tot hon o tuan 8.

Vi the A+ phai duoc lam TU TE, khong duoc lam yeu di de C thang.

    python -m src.nhanh --nhanh A  --model Qwen/Qwen3-8B --adapter models/nen-qwen3-8b/best_checkpoint
    python -m src.nhanh --nhanh A+ --model Qwen/Qwen3-8B --adapter ... --tu data/ra_A_phat_trien.jsonl
"""
import argparse
import io
import json
import sys

from src import duong_dan
from src.train_baseline import LOI_NHAC_HE_THONG, LOI_NHAC_NGUOI_DUNG

# Loi nhac hau kiem cua A+. Khong nhac toi bat ky khai niem nao cua nhanh C
# (chu the, quan he, trang thai) — neu nhac thi A+ khong con la doi chung nua,
# no thanh mot phien ban ngheo cua C.
LOI_NHAC_HAU_KIEM = """Dưới đây là một cuộc hội thoại khám bệnh và bản hồ sơ bệnh án được viết từ cuộc hội thoại đó.

Hãy đọc kỹ và tìm những chỗ bản hồ sơ ghi sai hoặc ghi thiếu so với hội thoại. Sau đó viết lại bản hồ sơ đã sửa.

Chỉ trả về bản hồ sơ đã sửa, không giải thích, không liệt kê chỗ sửa.

Hội thoại:
{hoi_thoai}

Bản hồ sơ cần rà lại:
{ban_nhap}"""


def _nap_mo_hinh(ten_mo_hinh, adapter=None):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tok = AutoTokenizer.from_pretrained(ten_mo_hinh)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                             bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(ten_mo_hinh, quantization_config=bnb,
                                                 device_map="auto")
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return tok, model


def _sinh(tok, model, noi_dung_nguoi_dung, max_token=512):
    """Tra ve (van_ban, so_token_vao, so_token_ra).

    `enable_thinking=False` giong luc train — khac nhau la lech phan phoi.
    Giai ma tham lam (`do_sample=False`) giong `inference.py` goc: hai lan chay
    cung mot dau vao phai ra cung mot ket qua, khong thi khong so sanh duoc nhanh.
    """
    import torch
    msgs = [{"role": "system", "content": LOI_NHAC_HE_THONG},
            {"role": "user", "content": noi_dung_nguoi_dung}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    inp = tok(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**inp, max_new_tokens=max_token, do_sample=False,
                             pad_token_id=tok.eos_token_id)
    vao = inp["input_ids"].shape[1]
    ra = out[0].shape[0] - vao
    return tok.decode(out[0][vao:], skip_special_tokens=True).strip(), vao, ra


def chay_A(mau_list, tok, model, max_token=512):
    """Mot luot goi mot mau. Ket qua: {id, input, tham_chieu, du_doan, token_*}."""
    kq = []
    for i, m in enumerate(mau_list, 1):
        van, vao, ra = _sinh(tok, model,
                             LOI_NHAC_NGUOI_DUNG.format(hoi_thoai=m["input"]), max_token)
        kq.append({"id": m["id"], "input": m["input"], "tham_chieu": m["output"],
                   "du_doan": van, "so_luot_goi": 1,
                   "token_vao": vao, "token_ra": ra})
        print(f"  [{i:2d}/{len(mau_list)}] {m['id']:14} {len(van):5d} ky tu",
              flush=True)
    return kq


def chay_A_cong(ra_A, tok, model, max_token=512):
    """Doc ket qua cua A, cho mo hinh tu ra lai mot luot nua.

    Cong don token cua CA hai luot: A+ ton gap doi A, va phai bao cao dung.
    """
    kq = []
    for i, r in enumerate(ra_A, 1):
        van, vao, ra = _sinh(tok, model, LOI_NHAC_HAU_KIEM.format(
            hoi_thoai=r["input"], ban_nhap=r["du_doan"]), max_token)
        kq.append({"id": r["id"], "input": r["input"], "tham_chieu": r["tham_chieu"],
                   "du_doan": van, "ban_nhap_A": r["du_doan"], "so_luot_goi": 2,
                   "token_vao": r["token_vao"] + vao,
                   "token_ra": r["token_ra"] + ra})
        doi = "sua" if van.strip() != r["du_doan"].strip() else "GIU NGUYEN"
        print(f"  [{i:2d}/{len(ra_A)}] {r['id']:14} {doi}", flush=True)
    return kq


def tom_tat_chi_phi(kq):
    """A+ ton gap doi A. Bao cao so luot goi va token la bat buoc, khong phai
    tuy chon — mot phuong phap dat gap doi ma hon 1 diem thi chua chac dang."""
    return {"so_mau": len(kq),
            "tong_luot_goi": sum(k["so_luot_goi"] for k in kq),
            "tong_token_vao": sum(k["token_vao"] for k in kq),
            "tong_token_ra": sum(k["token_ra"] for k in kq)}


# ==================================================== nhanh B, C va doi chung

def _nguoi_noi_theo_luot(hoi_thoai):
    from src import thuc_the
    return {so: vai for so, vai, _ in thuc_the.tach_luot(hoi_thoai) if vai}


def _van_ban_theo_luot(hoi_thoai):
    """{so luot: loi noi}. Buoc phan quan he can NGUYEN VAN loi thoai, vi dau
    hieu dinh chinh ("a khong", "nham roi") nam trong do chu khong nam trong
    truong nao cua ban ghi."""
    from src import thuc_the
    return {so: noi for so, _, noi in thuc_the.tach_luot(hoi_thoai)}


# Nhanh nao chay buoc phan quan he theo tung cap, va bang duong nao.
# Xem src/phan_quan_he.py de biet vi sao buoc nay ton tai.
DUONG_PHAN = {
    "C_quan_he_luat": "luat",     # doi chung khong GPU
    "C_quan_he": "ca_hai",        # luat quyet truoc, con lai hoi mo hinh
    "D_quan_he": "ca_hai",
}

# Nhanh nao lien ket thuc the (khong co ten o day = KHONG lien ket).
KHONG_LIEN_KET = ("B", "C_khong_lien_ket")

# Nhanh nao ap luat chuyen trang thai.
CO_AP_LUAT = ("C", "D", "C_khong_lien_ket",
              "C_quan_he", "C_quan_he_luat", "D_quan_he", "C_khoa", "C_khoa_hoi")

# Nhanh nao chay hau kiem (kiem day du + sua cuc bo).
CO_HAU_KIEM = ("D", "D_quan_he")

# Nhanh nao qua KHOA BANG CHUNG + CONG RUI RO (tang 4-5 cua de xuat 11/09/2026),
# va nhanh nao chon them cau HOI LAI (tang 6). Ca ba tang la MA THUAN doi chieu
# voi chinh hoi thoai, nen chay duoc bang `--tu-dem`, khong can GPU. C_khoa la C
# CONG khoa, khong gi khac: chenh lech C_khoa - C la dong gop cua rieng tang khoa.
CO_KHOA = ("C_khoa", "C_khoa_hoi")

NHANH_TRUNG_GIAN = ("B", "C", "C_ghi_de", "D", "C_khong_lien_ket",
                    "C_khong_luat", "C_quan_he", "C_quan_he_luat", "D_quan_he",
                    "C_khoa", "C_khoa_hoi")


def ten_ket_qua(nhanh, adapter):
    """Ten nhanh dung trong TEN TEP ket qua. Ham thuan tuy de test duoc.

    Nhanh A co adapter va nhanh A nen (khong adapter) la HAI thu khac nhau —
    chung la hai cot trong cung mot bang so sanh, va chenh lech giua chung
    chinh la "huan luyen dong gop bao nhieu".

    Truoc 10/09/2026 ca hai deu ghi vao `ra_A_<tap>.jsonl`. Chuoi dung lai
    chay 2b (co adapter) roi 2c (khong adapter) lien nhau, va ket qua cua 2b
    BIEN MAT — im lang, khong bao gi.

    Loi con kin hon o cho: `cham_lai_bang_quy_gan.NHANH` DA liet ke "A_nen"
    nhu mot nhanh rieng. Ben DOC luon mong doi mot tep ma ben GHI chua bao gio
    tao ra, va hai ben lech nhau suot ma khong ai bao.

    Cung ho voi ly do tep dem trich phai kem `max_token` va hau to `_hl`.
    """
    return nhanh if adapter else nhanh + "_nen"


def chay_trung_gian(mau_list, tok, model, prefix_fn, nhanh,
                    max_token=1536, kq_tho=None, prefix_phan=None,
                    bat_buoc_trich_dan=None, chinh_sach="C"):
    """Ba nhanh dung chung mot duong ong, khac nhau DUNG hai buoc.

        B        trich -> sinh.          Khong lien ket thuc the, khong ap luat.
        C        trich -> lien ket -> ap luat -> sinh (chi ban con hieu luc).
        C_ghi_de trich -> lien ket -> GHI DE ban truoc -> sinh.
        D        C, roi bo sung cho bo sot (Task 16) va sua cuc bo (Task 17).

    Hai cau hinh boc co che (Task 19) — chung lam day o 2x2, khong phai
    nhanh doc lap:

        C_khong_lien_ket  co luat quan he, KHONG lien ket thuc the
        C_khong_luat      co lien ket thuc the, KHONG luat quan he

    Cong voi B (khong co gi) va C (co ca hai) la du bon o. Thieu mot o thi
    khong tach duoc dong gop cua tung co che, chi noi duoc "gop lai thi hon".

    C_ghi_de la doi chung cua rieng phan cap nhat (Task 15 buoc 3): neu C
    khong hon duoc quy tac "phat bieu sau ghi de phat bieu truoc" tren cac
    tinh huong co dinh chinh, thi phan luat quan he chua chung minh duoc gi.

    Viet chung mot ham de ba nhanh KHAC NHAU dung o cho dinh noi, khong khac
    o nhung cho lat vat — neu khong thi chenh lech do duoc se lan lon
    nguyen nhan.

    `kq_tho`: dau ra trich xuat da co san. SAU nhanh dung CHUNG mot buoc
    trich; chay rieng tung nhanh la sinh lai sau lan, moi lan 30-40 phut.
    Truyen lai ket qua trich vao day vua nhanh gap sau lan, vua bao dam moi
    nhanh nhin thay DUNG mot dau ra mo hinh — chenh lech do duoc chac chan
    den tu hau xu ly chu khong tu mot lan sinh khac.
    """
    from src import bakeoff, cap_nhat, phat_bieu, sinh_benh_an, thuc_the

    assert nhanh in NHANH_TRUNG_GIAN, nhanh
    if kq_tho is None:
        kq_tho = bakeoff.trich(tok, model, prefix_fn, mau_list, max_token=max_token)
    if bat_buoc_trich_dan is None:
        # Tu dong theo DAU RA, mot lan cho ca lan chay: adapter the he 5 viet
        # truong trich dan, nen thieu trich dan la loi va bi chan. Dau ra cu (the
        # he 4, mo hinh nen) chua bao gio thay truong do — chan thi moi phat bieu
        # cua no deu bi chan, nen chi canh bao.
        bat_buoc_trich_dan = any(
            isinstance(x, dict) and x.get("trich_dan")
            for k in kq_tho for x in (k.get("phat_bieu") or []))

    ra = []
    for m, k in zip(mau_list, kq_tho):
        nguoi_noi = _nguoi_noi_theo_luot(m["input"])
        if nhanh in KHONG_LIEN_KET:
            bang, ten_chu_the = None, {}
        else:
            tt = thuc_the.lien_ket(m["input"])
            bang = phat_bieu.bang_ten_tu_thuc_the(tt)
            ten_chu_the = {t.id: t.ten_chuan for t in tt
                           if t.loai == "người" and t.id != 0}

        ps, loi = phat_bieu.tu_json(k["phat_bieu"] or [],
                                    nguoi_noi_theo_luot=nguoi_noi,
                                    id_theo_ten=bang)
        # `ten_chu_the` do `phat_bieu.tu_json` gan ngay tai cho dung ban ghi.
        # Truoc 10/09/2026 cho nay gan lai bang `zip(ps, [... luot_thoai])`,
        # va phep zip do lech hang khi co ban ghi vua co `luot_thoai` vua
        # khong hop le — no bi loai khoi `ps` nhung van con ben phai, nen tu
        # do tro di moi phat bieu nhan ten chu the cua phat bieu ke tiep.
        # Buoc phan quan he theo tung cap. Phai chay TRUOC `ap_luat`, vi
        # `ap_luat` doc truong `quan_he` — chay sau thi khong con tac dung gi.
        tk_phan = None
        if nhanh in DUONG_PHAN:
            from src import phan_quan_he
            tk_phan_duong = DUONG_PHAN[nhanh]
            if tk_phan_duong != "luat" and model is None:
                raise SystemExit(
                    f"nhanh {nhanh} can mo hinh de phan quan he; "
                    f"--tu-dem chi chay duoc nhanh C_quan_he_luat")
            ps, tk_phan = phan_quan_he.phan(
                ps, _van_ban_theo_luot(m["input"]), duong=tk_phan_duong,
                tok=tok, model=model, prefix_fn=prefix_phan)

        if nhanh in CO_AP_LUAT:
            ps = cap_nhat.ap_luat(ps)
        elif nhanh == "C_ghi_de":
            ps = cap_nhat.ghi_de_phat_bieu_truoc(ps)

        # Tang khoa + rui ro + hoi lai. Khoa doi chieu voi HOI THOAI, khong voi
        # bang phat bieu; phat bieu bi CHAN xuong CAN XAC NHAN kem ly do cua khoa.
        khoa, ly_do_chan = {}, None
        if nhanh in CO_KHOA:
            from src import cong_rui_ro, hoi_lai, khoa_bang_chung
            kk = khoa_bang_chung.khoa_ca(ps, m["input"],
                                         bat_buoc_trich_dan=bat_buoc_trich_dan)
            dg = cong_rui_ro.cham(ps, kk["ket_qua"])
            ly_do_chan = khoa_bang_chung.ly_do_chan(kk["ket_qua"])
            # Chinh sach cach C (22/09/2026): di ung / thuoc co canh bao cung sang
            # CAN XAC NHAN. Ly do chan cua khoa duoc uu tien khi trung id.
            ly_do_chan_khoa = ly_do_chan
            ly_do_chan = {**cong_rui_ro.dua_sang_xac_nhan(dg), **ly_do_chan}
            # Lop canh bao (24/09/2026). Luon tinh va luu de do/hien; CHI doi ban nhap
            # khi goi ro chinh_sach="D". Mac dinh "C": moi con so da bao cao khong doi.
            from src.canh_bao import gop as canh_bao_gop
            cb = canh_bao_gop.chay(ps, m["input"], kk)
            if chinh_sach == "D":
                ly_do_chan = {**canh_bao_gop.ly_do_chan_D(cb), **ly_do_chan_khoa}
            cau_hoi = (hoi_lai.chon(hoi_lai.ung_vien(ps, dg))
                       if nhanh == "C_khoa_hoi" else [])
            khoa = {"khoa": [k.to_dict() for k in kk["ket_qua"]],
                    "rui_ro": [d.to_dict() for d in dg],
                    "nhom": cong_rui_ro.dem_nhom(dg),
                    "doan_chua_ghi": kk["doan_chua_ghi"],
                    "cau_hoi": [c.to_dict() for c in cau_hoi],
                    "lich_su": cap_nhat.lich_su(ps),
                    "bat_buoc_trich_dan": bat_buoc_trich_dan,
                    "chinh_sach": (canh_bao_gop.CHINH_SACH_D if chinh_sach == "D"
                                   else cong_rui_ro.CHINH_SACH),
                    "canh_bao": canh_bao_gop.to_dict(cb)}

        van, ghi_chu = sinh_benh_an.sinh(ps, ten_chu_the=ten_chu_the,
                                         ly_do_chan=ly_do_chan)
        if khoa.get("cau_hoi"):
            van += (f"\n\n{sinh_benh_an.MUC_HOI_LAI}\n\n" + "\n".join(
                f"{i}. {c['van']}" for i, c in enumerate(khoa["cau_hoi"], 1)))

        da_bo_sung, da_sua = [], []
        if nhanh in CO_HAU_KIEM:
            from src import kiem_day_du, sua_cuc_bo
            van, da_bo_sung = kiem_day_du.bo_sung(ps, van, ten_chu_the=ten_chu_the)
            ket = sua_cuc_bo.sua(van, ps, ten_chu_the=ten_chu_the)
            van, da_sua = ket.van_ban, ket.da_sua
        # Luu CA HAI ban. Muc CAN XAC NHAN khong co trong ban tham chieu nen
        # bo cham dem no la mot muc du doan thua, keo Section F1 xuong. Phai
        # bao cao ca hai so, va bao cao luon so phat bieu bi chuyen xuong do —
        # neu khong thi muc do thanh cho giau moi thu kho.
        than, phu = sinh_benh_an.tach_muc_phu(van)
        ra.append({"id": m["id"], "input": m["input"],
                   "tham_chieu": m.get("output"), "du_doan": van,
                   "du_doan_khong_muc_phu": than,
                   "so_luot_goi": 1,
                   "token_vao": 0, "token_ra": 0,
                   "so_phat_bieu": len(ps), "loi_ban_ghi": loi,
                   "so_can_xac_nhan": sum(
                       1 for g in ghi_chu if g["muc"] == sinh_benh_an.MUC_PHU),
                   "da_bo_sung": da_bo_sung, "da_sua": da_sua,
                   "phan_quan_he": tk_phan,
                   "so_co_quan_he": sum(1 for p in ps if p.quan_he),
                   "ghi_chu": ghi_chu,
                   # Ban ghi SAU ap luat: dau vao cua phep do tang khoa, cua
                   # giao dien duyet va cua bo 500 GPT (`bo_gpt500 --cham`).
                   "phat_bieu": [p.to_dict() for p in ps],
                   **khoa})
        them = ""
        if tk_phan:
            them = (f", {tk_phan['so_cap']} cap -> "
                    f"{tk_phan['so_phan']} quan he")
        print(f"  [{len(ra):2d}/{len(mau_list)}] {m['id']:14} "
              f"{len(ps):2d} phat bieu, {len(van):5d} ky tu"
              + (f", {len(loi)} ban ghi hong" if loi else "") + them, flush=True)
    return ra


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    # nargs="+": nap 8B mat vai phut va chiem gan het VRAM, khong the nap
    # hai ban cung luc. Chay nhieu nhanh trong MOT lan nap tiet kiem han
    # thoi gian do, va bao dam moi nhanh thay dung mot mo hinh.
    ap.add_argument("--nhanh", nargs="+", required=True,
                    choices=["A", "A+"] + list(NHANH_TRUNG_GIAN))
    ap.add_argument("--model", default=duong_dan.MODEL_CHINH)
    ap.add_argument("--adapter", default=None,
                    help="A/A+: adapter viet benh an")
    ap.add_argument("--adapter-trich", default=None,
                    help="B/C/D: adapter da huan luyen cho khau TRICH")
    ap.add_argument("--tap", default="viet_phat_trien",
                    help="viet_phat_trien | viet_kiem_tra_cuoi")
    ap.add_argument("--tu", default=None, help="A+: tep ket qua cua A")
    ap.add_argument("--n", type=int, default=None)
    # 3072: o 1536 thi 8/35 hoi thoai that bi cat cut giua JSON
    # (14-28 luot thoai), lam 7/35 benh an ra rong.
    ap.add_argument("--max-token", type=int, default=3072)
    # Khau SINH benh an la ma thuan, khong dung mo hinh. Co co
    # tep dem trich roi thi sinh lai duoc trong vai giay, khong
    # phai nap mo hinh va khong tranh GPU voi ai.
    ap.add_argument("--tu-dem", action="store_true",
                    help="sinh lai tu tep dem, khong nap mo hinh")
    a = ap.parse_args()

    from src import du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    from src import du_lieu

    trung_gian = [n for n in a.nhanh if n not in ("A", "A+")]
    if trung_gian:
        from src import bakeoff
        # B/C trich ban ghi co cau truc, nen phai EP JSON. A/A+ sinh van xuoi,
        # khong ep. Do la ly do hai duong nap mo hinh khac nhau, khong phai
        # do trung lap.
        mau = du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / f"{a.tap}.jsonl")
        mau = mau[:a.n] if a.n else mau
        if a.tu_dem:
            hau = "_hl" if a.adapter_trich else ""
            dem = (duong_dan.THU_MUC_DU_LIEU /
                   f"trich_{a.tap}_{a.max_token}{hau}.jsonl")
            co = {json.loads(x)["id"] for x in open(dem, encoding="utf-8")
                  if x.strip()}
            thieu = [m["id"] for m in mau if m["id"] not in co]
            if thieu:
                raise SystemExit(f"tep dem thieu {len(thieu)} mau: {thieu[:5]}")
            tok = model = prefix_fn = None
        else:
            tok, model, prefix_fn = bakeoff.nap(a.model, ep_json=True,
                                            adapter=a.adapter_trich)
        # Trich MOT lan cho ca sau nhanh. Xem docstring chay_trung_gian.
        # `luu_dan`: ghi tung mau ngay khi xong. Chay lai lenh nay sau khi bi
        # ngat thi no chay tiep tu cho do, khong lam lai tu dau.
        # Ten tep dem KEM max_token: ket qua trich o 1536 va o 3072 la hai
        # thu khac nhau, tron chung mot tep thi lan chay sau se dung lai ban
        # bi cat cut ma khong ai biet.
        # Ten tep dem kem ca adapter: ket qua trich cua mo hinh nen va cua
        # mo hinh da huan luyen la hai thu khac nhau, tron chung mot tep thi
        # lan sau dung lai ban cu ma khong ai biet.
        hau = "_hl" if a.adapter_trich else ""
        dem = (duong_dan.THU_MUC_DU_LIEU /
               f"trich_{a.tap}_{a.max_token}{hau}.jsonl")
        kq_tho = bakeoff.trich(tok, model, prefix_fn, mau, luu_dan=dem,
                               max_token=a.max_token)
        # Buoc phan quan he dung LUOC DO KHAC voi buoc trich (mot truong thay
        # vi mot danh sach ban ghi), nen phai co bo ep rieng. Chi dung khi co
        # nhanh nao thuc su can, va chi khi co mo hinh.
        prefix_phan = None
        if model is not None and any(n in DUONG_PHAN and DUONG_PHAN[n] != "luat"
                                     for n in trung_gian):
            from src import phan_quan_he
            prefix_phan = phan_quan_he.ep_json_phan(tok)
        for ten in trung_gian:
            print(f"\n=== nhanh {ten} ===", flush=True)
            kq = chay_trung_gian(mau, tok, model, prefix_fn, ten,
                                 max_token=a.max_token, kq_tho=kq_tho,
                                 prefix_phan=prefix_phan)
            dp = duong_dan.THU_MUC_DU_LIEU / f"ra_{ten}_{a.tap}.jsonl"
            dp.write_text("\n".join(json.dumps(k, ensure_ascii=False)
                                    for k in kq), encoding="utf-8")
            hong = sum(len(k["loi_ban_ghi"]) for k in kq)
            rong = sum(1 for k in kq if not k["du_doan"].strip())
            cxn = sum(k["so_can_xac_nhan"] for k in kq)
            tong_pb = sum(k["so_phat_bieu"] for k in kq)
            print(f"Ghi {len(kq)} dong -> {dp}")
            print(f"Ban ghi bi bo vi khong dung luoc do: {hong}")
            print(f"Benh an rong: {rong}/{len(kq)}")
            print(f"Phat bieu chuyen sang CAN XAC NHAN: {cxn}/{tong_pb}")
            if ten in CO_KHOA:
                nhom = {}
                for k in kq:
                    for n, s in (k.get("nhom") or {}).items():
                        nhom[n] = nhom.get(n, 0) + s
                hoi = sum(len(k.get("cau_hoi") or []) for k in kq)
                print(f"Khoa + rui ro: {nhom}  | cau hoi lai: {hoi}  | bat buoc "
                      f"trich dan: {kq[0].get('bat_buoc_trich_dan') if kq else None}")
            # Con so quan trong nhat cua buoc phan quan he: truoc khi co no,
            # `quan_he` bang "khong" o 282/282 phat bieu. Bang 0 o day nghia
            # la buoc phan van chua chay duoc, khong phai la hoi thoai khong
            # co quan he.
            qh = sum(k.get("so_co_quan_he", 0) for k in kq)
            if ten in DUONG_PHAN:
                cap = sum(k["phan_quan_he"]["so_cap"] for k in kq
                          if k.get("phan_quan_he"))
                cat = sum(1 for k in kq
                          if (k.get("phan_quan_he") or {}).get("bi_cat"))
                nhan = {}
                for k in kq:
                    for n, s in ((k.get("phan_quan_he") or {})
                                 .get("theo_nhan", {}).items()):
                        nhan[n] = nhan.get(n, 0) + s
                print(f"Cap ung vien: {cap}   -> gan duoc {qh} quan he")
                print(f"  theo nhan: {nhan or '(khong co)'}")
                if cat:
                    print(f"  CANH BAO: {cat}/{len(kq)} mau bi cat bot cap")
            else:
                print(f"Phat bieu co quan he: {qh}/{tong_pb}")
            print("", flush=True)
        if not [n for n in a.nhanh if n in ("A", "A+")]:
            return

    tok, model = _nap_mo_hinh(a.model, a.adapter)

    if "A" in a.nhanh:
        mau = du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / f"{a.tap}.jsonl")
        kq = chay_A(mau[:a.n] if a.n else mau, tok, model)
    else:
        nguon = duong_dan.THU_MUC_DU_LIEU / (a.tu or f"ra_A_{a.tap}.jsonl")
        ra_A = [json.loads(d) for d in open(nguon, encoding="utf-8") if d.strip()]
        kq = chay_A_cong(ra_A[:a.n] if a.n else ra_A, tok, model)

    ten = ten_ket_qua("A" if "A" in a.nhanh else "A_cong", a.adapter)
    dp = duong_dan.THU_MUC_DU_LIEU / f"ra_{ten}_{a.tap}.jsonl"
    dp.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in kq),
                  encoding="utf-8")

    ct = tom_tat_chi_phi(kq)
    rong = sum(1 for k in kq if not k["du_doan"].strip())
    dai_tb = sum(len(k["du_doan"]) for k in kq) / max(1, len(kq))
    print("")
    print(f"Ghi {len(kq)} dong -> {dp}")
    print(f"Dong rong: {rong}/{len(kq)}   do dai trung binh: {dai_tb:.0f} ky tu")
    print(f"Chi phi: {ct['tong_luot_goi']} luot goi, "
          f"{ct['tong_token_vao']} token vao, {ct['tong_token_ra']} token ra")
    if rong * 2 > len(kq):
        print("QUA NUA SO DONG RONG — quay lai Task 6, khong chay tiep.")





if __name__ == "__main__":
    main()
