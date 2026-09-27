# -*- coding: utf-8 -*-
"""Bake-off chon mo hinh bang so, khong bang phan doan.

Qwen3-8B duoc chon theo benchmark chung — KHONG phai theo bai toan trich phat
bieu lam sang tieng Viet. Hai thu do tuong quan chu khong dong nhat. 30 phut thu
re hon 3 gio train nham.

Do HAI con so tren 20 hoi thoai cua tap PHAT TRIEN:

    ty le JSON hop le      may bang, dem tu dong
    ty le gan dung chu the  QUAN TRONG HON, phai cham tay

Mot mo hinh sinh JSON dep ma gan nham chu the thi vo dung cho du an nay.

    python -m src.bakeoff --model Qwen/Qwen3-4B --n 20
"""
import argparse
import io
import json
import sys
from pathlib import Path

from src.phat_bieu import DUONG_DUNG, HANH_VI, TRANG_THAI_DUNG

LUOC_DO = {
    "type": "object",
    "properties": {
        "phat_bieu": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "chu_the": {"type": "string"},
                    "noi_dung": {"type": "string"},
                    "do_chac_chan": {"enum": ["chắc chắn", "nghi ngờ", "chưa ghi nhận"]},
                    "phu_dinh": {"type": "boolean"},
                    "tinh_huong": {"enum": ["thực tế", "giả định", "kế hoạch"]},
                    "thoi_gian_su_kien": {"enum": ["hiện tại", "quá khứ", "chưa rõ"]},
                    "moc_thoi_gian": {"type": ["string", "null"]},
                    "quan_he": {"enum": ["bổ sung", "đính chính", "diễn biến", "mâu thuẫn", "không"]},
                    "quan_he_voi": {"type": ["integer", "null"]},
                    "luot_thoai": {"type": "array", "items": {"type": "integer"}},
                    # Them 11/09/2026 — xem `phat_bieu.PhatBieu.trich_dan`. KHONG
                    # dua vao "required": dau ra cu va mo hinh nen khong co hai
                    # truong nay, va `_phan_tich` dung danh sach bat buoc cua rieng
                    # no. Thieu trich dan thi `khoa_bang_chung` coi la bang chung
                    # yeu hon, khong coi la ban ghi hong.
                    "trich_dan": {"type": "array", "items": {"type": "string"}},
                    "hanh_vi": {"enum": list(HANH_VI)},
                    # Them 15/09/2026 — xem `phat_bieu.THUOC_KHOA`. Chi phat bieu ve
                    # thuoc mang truong nay; KHONG vao "required", cung ly do voi
                    # `trich_dan`. Hai danh sach dong lay tu `phat_bieu`, khong go
                    # lai o day: hai ban go tay la hai ban se troi nhau.
                    "thuoc": {
                        "type": ["object", "null"],
                        "properties": {
                            "ten": {"type": "string"},
                            "lieu": {"type": ["string", "null"]},
                            "so_lan": {"type": ["string", "null"]},
                            "duong_dung": {"enum": list(DUONG_DUNG) + [None]},
                            "bat_dau": {"type": ["string", "null"]},
                            "ngung": {"type": ["string", "null"]},
                            "trang_thai_dung": {"enum": list(TRANG_THAI_DUNG) + [None]},
                        },
                        "required": ["ten"],
                    },
                },
                "required": ["chu_the", "noi_dung", "do_chac_chan", "luot_thoai"],
            },
        }
    },
    "required": ["phat_bieu"],
}

HUONG_DAN = """Đọc hội thoại khám bệnh dưới đây. Với MỖI thông tin lâm sàng, ghi một bản ghi gồm:

- chu_the: thông tin này nói VỀ AI. Người nhà thường kể hộ bệnh nhân — khi đó chủ thể là bệnh nhân, không phải người kể. Nhưng nếu người nhà kể bệnh CỦA CHÍNH HỌ thì chủ thể là người nhà.
  Tuổi, cân nặng, giới tính của bệnh nhân là thông tin VỀ BỆNH NHÂN, kể cả khi người nhà là người nói ra.
- noi_dung: triệu chứng, bệnh, thuốc hoặc kết quả
- thuoc: CHỈ ghi khi bản ghi là thông tin về thuốc; bản ghi khác thì bỏ trường này. Gồm ten; lieu (ví dụ "5 mg", "hai nhát"); so_lan (ví dụ "ngày hai lần", "khi cần"); duong_dung: "uống" | "xịt" | "bôi" | "nhỏ"; bat_dau (ví dụ "hai tuần nay"); ngung (ví dụ "2 tuần"); trang_thai_dung: "đang dùng" | "đã ngừng" | "được kê, chưa dùng" (bác sĩ vừa kê trong buổi khám, người bệnh chưa dùng viên nào). Chi tiết nào hội thoại KHÔNG nói thì để null — không đoán liều, không đoán số lần dùng. GIỮ NGUYÊN chữ trong hội thoại. Liều bị người nói sửa lại ("5 mg, à nhầm, 10 mg") thì ghi CẢ HAI bản, bản sau "đính chính" bản trước.
- do_chac_chan: "chắc chắn" | "nghi ngờ" | "chưa ghi nhận". "Chưa thấy bị bao giờ" là "chưa ghi nhận", KHÔNG phải phủ định chắc chắn.
- phu_dinh: true nếu là phủ định
- tinh_huong: "thực tế" | "giả định" | "kế hoạch". "Nếu mai vẫn đau thì..." là "giả định".
- thoi_gian_su_kien: "hiện tại" | "quá khứ" | "chưa rõ"
- moc_thoi_gian: mốc CỤ THỂ nếu hội thoại nêu, ví dụ "2 ngày", "hôm qua", "hôm nay". Để null nếu không có. GIỮ NGUYÊN chữ trong hội thoại.
- quan_he: quan hệ với một bản ghi TRƯỚC ĐÓ, kèm quan_he_voi là số thứ tự bản ghi đó (đếm từ 0):
    "đính chính" — người nói tự sửa lại chính thông tin vừa nêu ("4 ngày... à không, 2 ngày"). Ghi CẢ HAI bản, bản sau đính chính bản trước.
    "diễn biến"  — hai mốc thời gian khác nhau, CẢ HAI đều đúng ("hôm qua đau, hôm nay hết"). Ghi CẢ HAI bản.
    "bổ sung"    — thêm chi tiết cho thông tin đã nêu
    "mâu thuẫn"  — hai nguồn nói trái nhau, chưa ai xác nhận lại
    "không"      — không liên quan bản ghi nào trước đó
- luot_thoai: danh sách SỐ THỨ TỰ các lượt làm bằng chứng — lượt CHỨA thông tin đó. Câu trả lời tắt như "Dạ, không ạ" thì thêm cả lượt câu hỏi ngay trước.
- trich_dan: với MỖI lượt trong luot_thoai, chép NGUYÊN VĂN đoạn ngắn nhất trong lượt đó nói ra thông tin — đúng từng chữ, kể cả cách nói dân dã hay phương ngữ. Không sửa, không tóm tắt, không chuẩn hóa.
- hanh_vi: "trả lời" | "tự kể" | "quan sát" | "nhận định" | "kế hoạch". Bệnh nhân hoặc người nhà nói ngay sau lượt của bác sĩ là "trả lời"; tự nói ra khi không ai hỏi là "tự kể". Kết quả khám là "quan sát", chẩn đoán là "nhận định", chỉ định và dặn dò là "kế hoạch".

Câu hỏi mà không ai trả lời thì KHÔNG tạo bản ghi.
Chỉ trả về JSON, không giải thích."""

from src.vi_du_mau import VI_DU  # noqa: E402  (4 vi du, xem tep do)


def danh_so_luot(hoi_thoai):
    dong = [d for d in hoi_thoai.split("\n") if d.strip()]
    return "\n".join(f"{i+1}. {d}" for i, d in enumerate(dong)), len(dong)


def kiem_khop(mau_theo_id, tho, ten_dem=""):
    """Tep dem trich co PHAI cua bo du lieu nay khong. Sai thi nem loi ngay.

    VI SAO CAN (10/09/2026). Bo du lieu duoc sinh lai tu 3.000 ca len 5.000 ca,
    va `viet_phat_trien.jsonl` bi ghi de bang tap phat trien MOI. Tep dem trich
    van la cua bo cu. Ma cua ca la `hv_xxxx` o CA HAI bo — nen id khop het, va
    phep do chay tron tru, cho ra mot bang so hoan toan vo nghia:

        do tren bo cu   ca co quan he that: 16/60
        do sau khi doi  ca co quan he that:  1/60   <- so cua bo khac

    Khong co gi bao loi. Khong JSON hong, khong ngoai le, khong dong canh bao.
    Neu khong doi chieu tay voi lan do truoc thi da bao cao con so do.

    Phep kiem: `so_luot` trong tep dem phai bang so luot cua hoi thoai trong
    dap an. Re, va du de bat moi truong hop hai bo khac nhau — hai hoi thoai
    khac nhau gan nhu khong bao gio cung so luot o TAT CA cac ca.
    """
    lech = []
    for k in tho:
        ca = mau_theo_id.get(k["id"])
        if ca is None:
            lech.append(f"{k['id']}: khong co trong dap an")
            continue
        that = len([d for d in ca["input"].split("\n") if d.strip()])
        if k.get("so_luot") != that:
            lech.append(f"{k['id']}: dem ghi {k.get('so_luot')} luot, "
                        f"dap an co {that}")
    if lech:
        raise SystemExit(
            f"TU CHOI: tep dem trich {ten_dem} KHONG phai cua bo du lieu nay.\n"
            + "\n".join("  " + x for x in lech[:5])
            + (f"\n  ... va {len(lech) - 5} cho nua" if len(lech) > 5 else "")
            + "\nSinh lai tep dem, hoac tro toi dung bo du lieu da dung de trich.")


def nap(ten_mo_hinh, ep_json=True, adapter=None):
    """Nap mo hinh mot lan, dung lai cho nhieu luot chay.

    Tach khoi `chay` de nhanh B va C khong phai nap lai 8B moi lan — nap mat
    vai phut va chiem het VRAM, khong the nap hai ban cung luc.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tok = AutoTokenizer.from_pretrained(ten_mo_hinh)
    bnb = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(
        ten_mo_hinh, quantization_config=bnb, device_map="auto")
    if adapter:
        # Adapter huan luyen RIENG cho khau trich (`--nhiem-vu trich`).
        # Khac han adapter cua nhanh A, von hoc viet benh an.
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
        print(f"  (da nap adapter trich: {adapter})", flush=True)
    model.eval()

    prefix_fn = _ep_json(tok) if ep_json else None
    return tok, model, prefix_fn


def _ep_json(tok):
    """Ep dau ra theo LUOC_DO. Khong cai duoc lm-format-enforcer thi chay tu do
    va NOI RO — im lang o day se thanh mot phep so sanh khong con dieu kien
    giong nhau giua cac lan chay."""
    try:
        from lmformatenforcer import JsonSchemaParser
        from lmformatenforcer.integrations.transformers import (
            build_transformers_prefix_allowed_tokens_fn)
        return build_transformers_prefix_allowed_tokens_fn(
            tok, JsonSchemaParser(LUOC_DO))
    except Exception as e:                           # noqa: BLE001
        print(f"  (khong ep duoc JSON: {e}; chay tu do)")
        return None


def trich(tok, model, prefix_fn, mau_list, max_token=1536, vi_du=True,
          luu_dan=None):
    """max_token=1536: o 768 thi 4B bi CAT CUT giua JSON (2/8 mau), vi no trich
    duoc nhieu phat bieu hon 1.7B. Do la loi co hoc, khong phai loi nang luc.

    `luu_dan`: duong dan jsonl. Ghi TUNG mau ngay khi xong, va bo qua mau da
    co trong tep.

    Vi sao can: mot lan chay 35 mau mat khoang 85 phut. Lan chay dau bi
    `CUDA error: unspecified launch failure` o mau 15 va mat sach 14 mau da
    lam, vi tep chi duoc ghi o cuoi. Loi CUDA do la muc driver, khong phong
    truoc duoc — nhung mat 35 phut moi lan thi phong duoc.
    """
    # Chay tiep bo qua mau THEO ID. Nhung id la `hv_xxxx` o MOI bo tu sinh,
    # nen mot tep dem cua bo 3.000 se duoc dung lai nguyen cho bo 5.000 —
    # va do la mot phep do tren du lieu tron lan, im lang hoan toan.
    #
    # Nen moi ban ghi trong tep dem phai chung minh no la cua DUNG hoi thoai
    # dang xet: `so_luot` phai khop. Ban nao khong khop thi BO va trich lai,
    # chu khong dung lai. Bao ra so ban bi bo — im lang o day cung nguy hiem
    # ngang im lang khi dung lai ban sai.
    da_co = {}
    if luu_dan is not None:
        dp = Path(luu_dan)
        if dp.exists():
            so_luot_that = {}
            for m in mau_list:
                so_luot_that[m["id"]] = len(
                    [d for d in m["input"].split("\n") if d.strip()])
            bo = 0
            for dong in dp.read_text(encoding="utf-8").splitlines():
                if not dong.strip():
                    continue
                k = json.loads(dong)
                mong = so_luot_that.get(k["id"])
                if mong is not None and k.get("so_luot") != mong:
                    bo += 1
                    continue
                da_co[k["id"]] = k
            print(f"  (da co {len(da_co)} mau trong {dp.name}, chay tiep)",
                  flush=True)
            if bo:
                print(f"  (BO {bo} mau trong tep dem: so luot khong khop "
                      f"hoi thoai dang xet — tep dem cua bo du lieu khac)",
                      flush=True)

    ket_qua = []
    tep = open(luu_dan, "a", encoding="utf-8") if luu_dan is not None else None
    try:
        return _vong_trich(tok, model, prefix_fn, mau_list, max_token, vi_du,
                           da_co, tep, ket_qua)
    finally:
        if tep is not None:
            tep.close()


def _vong_trich(tok, model, prefix_fn, mau_list, max_token, vi_du,
                da_co, tep, ket_qua):
    for i, m in enumerate(mau_list, 1):
        if m["id"] in da_co:
            ket_qua.append(da_co[m["id"]])
            print(f"  [{i:2d}/{len(mau_list)}] {m['id']:14} (da co, bo qua)",
                  flush=True)
            continue
        danh_so, so_luot = danh_so_luot(m["input"])
        loi_nhac = HUONG_DAN + (f"\n\n{VI_DU}\n\nBây giờ đến lượt bạn." if vi_du else "")
        msgs = [{"role": "user",
                 "content": f"{loi_nhac}\n\nHội thoại:\n{danh_so}"}]
        prompt = tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        # torch nap o day chu khong o dau ham: mau lay tu tep dem khong can
        # den no, nen chay tiep duoc ca tren may khong co GPU.
        import torch
        inp = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=max_token, do_sample=False,
                                 pad_token_id=tok.eos_token_id,
                                 prefix_allowed_tokens_fn=prefix_fn)
        sinh = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)

        hop_le, du_lieu, ly_do = _phan_tich(sinh, so_luot)
        ban_ghi = {"id": m["id"], "so_luot": so_luot, "json_hop_le": hop_le,
                   "ly_do": ly_do, "phat_bieu": du_lieu, "tho": sinh[:400]}
        ket_qua.append(ban_ghi)
        if tep is not None:
            # flush ngay: treo may hay mat dien thi mau vua xong van con.
            tep.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
            tep.flush()
        # flush=True: khi chuyen huong ra tep, Python dem stdout theo khoi 8 KB
        # nen khong theo doi duoc tien do cua mot lan chay 40 phut.
        print(f"  [{i:2d}/{len(mau_list)}] {m['id']:14} "
              f"{'JSON OK' if hop_le else 'JSON HONG'} "
              f"{len(du_lieu) if du_lieu else 0} phat bieu", flush=True)
    return ket_qua


def chay(ten_mo_hinh, mau_list, ep_json=True, max_token=1536, vi_du=True):
    """Nap roi trich. Giu chu ky cu de cac cho goi san khong phai sua."""
    tok, model, prefix_fn = nap(ten_mo_hinh, ep_json)
    return trich(tok, model, prefix_fn, mau_list, max_token, vi_du)


def _phan_tich(van_ban, so_luot):
    """Tra ve (hop_le, danh_sach_phat_bieu, ly_do_hong)."""
    try:
        d = json.loads(van_ban)
    except json.JSONDecodeError as e:
        return False, None, f"json hong: {e}"
    if "phat_bieu" not in d or not isinstance(d["phat_bieu"], list):
        return False, None, "thieu khoa 'phat_bieu'"
    for p in d["phat_bieu"]:
        thieu = [k for k in ("chu_the", "noi_dung", "do_chac_chan", "luot_thoai")
                 if k not in p]
        if thieu:
            return False, d["phat_bieu"], f"thieu truong {thieu}"
        # Bang chung phai tro toi luot thoai CO THAT — day la kiem bang luat,
        # khong phai kiem cu phap
        xau = [n for n in p["luot_thoai"] if not (1 <= n <= so_luot)]
        if xau:
            return False, d["phat_bieu"], f"luot thoai khong ton tai: {xau}"
    return True, d["phat_bieu"], ""


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--khong-ep-json", action="store_true")
    ap.add_argument("--khong-vi-du", action="store_true")
    a = ap.parse_args()

    from src import du_lieu, duong_dan

    mau = du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / "phat_trien.jsonl")[:a.n]
    print(f"Bake-off: {a.model} tren {len(mau)} hoi thoai tap phat trien")
    kq = chay(a.model, mau, ep_json=not a.khong_ep_json, vi_du=not a.khong_vi_du)

    hop_le = sum(1 for k in kq if k["json_hop_le"])
    ten_tep = a.model.split("/")[-1].replace(".", "_")
    hau_to = "" if not a.khong_vi_du else "-khong-vi-du"
    dp = duong_dan.THU_MUC_KET_QUA / f"bakeoff-{ten_tep}{hau_to}.json"
    dp.write_text(json.dumps(kq, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"Ty le JSON hop le: {hop_le}/{len(kq)} = {100*hop_le/len(kq):.0f}%")
    print(f"Ket qua tho: {dp}")
    print("Ty le gan dung chu the PHAI CHAM TAY — mo tep tren va doc tung phat bieu.")


if __name__ == "__main__":
    main()
