# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Điều phối]
Làm gì   : Chạy các nhánh so sánh trên tập ca: A và A+ (mốc đối chứng), các nhánh B, C, D
           qua đường ống b1–b6, rồi ghi kết quả.
Vào → Ra : tệp ca hội thoại + tên mô hình, adapter, tên nhánh → tệp jsonl kết quả mỗi ca và
           thống kê chi phí gọi
Đọc từ   : main() là lối vào chọn nhánh; chay_trung_gian() chạy nhánh dùng đường ống;
           chay_A() là baseline một lượt
Mục lục (các hàm/lớp chính):
  main()             Điểm vào dòng lệnh chạy các nhánh so sánh
  chay_trung_gian()  Chạy các nhánh B, C, D dùng chung một đường ống
  chay_A()           Chạy nhánh A: một lượt gọi mỗi mẫu
  chay_A_cong()      Chạy nhánh A+: cho mô hình tự rà lại bản của A
  tom_tat_chi_phi()  Tóm tắt chi phí số lượt gọi và token
  ten_ket_qua()      Đặt tên nhánh trong tên tệp kết quả
Gọi tới  : bo_du_lieu/nap_du_lieu, duong_ong/b1_cau_truc_menh_de,
           duong_ong/b2_bu_chu_ngu_tinh_luoc, duong_ong/b2_gom_nguoi_thuc_the,
           duong_ong/b3_cap_nhat_trang_thai, duong_ong/b3_phan_xu_quan_he,
           duong_ong/b4_kiem_can_cu, duong_ong/b4_kiem_day_du … (tổng 15 tệp)
Dùng bởi : bo_du_lieu/ca_mau_bgk, duong_ong/b7_ban_duyet_html, he_thong/dich_vu_http
Tên cũ   : nhanh.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nhánh A và A+ — hai mốc so sánh của dự án.

  A   hội thoại -> bệnh án, MỘT lượt gọi. Đây là baseline.
  A+  chạy A, rồi đưa cả hội thoại lẫn bản nháp của A vào mô hình và bảo
      "tìm chỗ sai và sửa". HAI lượt gọi, không bảng trung gian, không luật.

A+ là đối chứng rẻ nhưng quan trọng nhất của dự án. Nếu A+ ngang C thì toàn
bộ biểu diễn trung gian (bản ghi phát biểu, quan hệ, trạng thái) là thừa —
chỉ cần bảo mô hình tự đọc lại là đủ. Biết điều đó ở tuần 4 tốt hơn ở tuần 8.

Vì thế A+ phải được làm TỬ TẾ, không được làm yếu đi để C thắng.

    python -m src.duong_ong.chay_duong_ong --nhanh A  --model Qwen/Qwen3-8B --adapter models/nen-qwen3-8b/best_checkpoint
    python -m src.duong_ong.chay_duong_ong --nhanh A+ --model Qwen/Qwen3-8B --adapter ... --tu data/ra_A_phat_trien.jsonl
"""
import argparse
import io
import json
import sys

from src.he_thong import duong_dan as duong_dan
from src.huan_luyen.huan_luyen_sft import LOI_NHAC_HE_THONG, LOI_NHAC_NGUOI_DUNG

# Lời nhắc hậu kiểm của A+. Không nhắc tới bất kỳ khái niệm nào của nhánh C
# (chủ thể, quan hệ, trạng thái) — nếu nhắc thì A+ không còn là đối chứng nữa,
# nó thành một phiên bản nghèo của C.
LOI_NHAC_HAU_KIEM = """Dưới đây là một cuộc hội thoại khám bệnh và bản hồ sơ bệnh án được viết từ cuộc hội thoại đó.

Hãy đọc kỹ và tìm những chỗ bản hồ sơ ghi sai hoặc ghi thiếu so với hội thoại. Sau đó viết lại bản hồ sơ đã sửa.

Chỉ trả về bản hồ sơ đã sửa, không giải thích, không liệt kê chỗ sửa.

Hội thoại:
{hoi_thoai}

Bản hồ sơ cần rà lại:
{ban_nhap}"""


# ─── _nap_mo_hinh() — Nạp mô hình lượng tử 4 bit và adapter ───────────────────────────
# Dùng cấu hình nf4; adapter là tuỳ chọn.
def _nap_mo_hinh(ten_mo_hinh, adapter=None):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tok = AutoTokenizer.from_pretrained(ten_mo_hinh)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                             bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(ten_mo_hinh, quantization_config=bnb,
                                                 torch_dtype=torch.bfloat16,
                                                 device_map="auto")
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return tok, model


# ─── _sinh() — Gọi mô hình sinh một lần ───────────────────────────────────────────────
# Tắt thinking và giải mã tham lam để hai lần chạy cho cùng kết quả; trả về (văn bản,
# token vào, token ra).
def _sinh(tok, model, noi_dung_nguoi_dung, max_token=512):
    """Trả về (van_ban, so_token_vao, so_token_ra).

    `enable_thinking=False` giống lúc train — khác nhau là lệch phân phối.
    Giải mã tham lam (`do_sample=False`) giống `inference.py` gốc: hai lần chạy
    cùng một đầu vào phải ra cùng một kết quả, không thì không so sánh được nhánh.
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


# ═══ chay_A() — Chạy nhánh A: một lượt gọi mỗi mẫu ════════════════════════════════════
# Trả về id, đầu vào, tham chiếu, dự đoán và số token.
def chay_A(mau_list, tok, model, max_token=512):
    """Một lượt gọi một mẫu. Kết quả: {id, input, tham_chieu, du_doan, token_*}."""
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


# ═══ chay_A_cong() — Chạy nhánh A+: cho mô hình tự rà lại bản của A ═══════════════════
# Cộng dồn token của cả hai lượt vì A+ tốn gấp đôi.
def chay_A_cong(ra_A, tok, model, max_token=512):
    """Đọc kết quả của A, cho mô hình tự ra lại một lượt nữa.

    Cộng dồn token của CẢ hai lượt: A+ tốn gấp đôi A, và phải báo cáo đúng.
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


# ═══ tom_tat_chi_phi() — Tóm tắt chi phí số lượt gọi và token ═════════════════════════
# Báo cáo bắt buộc vì phương pháp gấp đôi chi phí cần hơn rõ rệt mới đáng.
def tom_tat_chi_phi(kq):
    """A+ tốn gấp đôi A. Báo cáo số lượt gọi và token là bắt buộc, không phải
    tuỳ chọn — một phương pháp đắt gấp đôi mà hơn 1 điểm thì chưa chắc đáng."""
    return {"so_mau": len(kq),
            "tong_luot_goi": sum(k["so_luot_goi"] for k in kq),
            "tong_token_vao": sum(k["token_vao"] for k in kq),
            "tong_token_ra": sum(k["token_ra"] for k in kq)}


# ==================================================== nhánh B, C và đối chứng

# ─── _nguoi_noi_theo_luot() — Lập bảng người nói theo số lượt ─────────────────────────
def _nguoi_noi_theo_luot(hoi_thoai):
    from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the
    return {so: vai for so, vai, _ in thuc_the.tach_luot(hoi_thoai) if vai}


# ─── _van_ban_theo_luot() — Lập bảng lời nói nguyên văn theo số lượt ──────────────────
# Bước phân xử quan hệ cần nguyên văn vì dấu hiệu đính chính nằm trong lời.
def _van_ban_theo_luot(hoi_thoai):
    """{số lượt: lời nói}. Bước phân quan hệ cần NGUYÊN VĂN lời thoại, vì dấu
    hiệu đính chính ("à không", "nhầm rồi") nằm trong đó chứ không nằm trong
    trường nào của bản ghi."""
    from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the
    return {so: noi for so, _, noi in thuc_the.tach_luot(hoi_thoai)}


# Nhánh nào chạy bước phân quan hệ theo từng cặp, và bằng đường nào.
# Xem src/duong_ong/b3_phan_xu_quan_he.py để biết vì sao bước này tồn tại.
DUONG_PHAN = {
    "C_quan_he_luat": "luat",     # đối chứng không GPU
    "C_quan_he": "ca_hai",        # luật quyết trước, còn lại hỏi mô hình
    "D_quan_he": "ca_hai",
}

# Nhánh nào liên kết thực thể (không có tên ở đây = KHÔNG liên kết).
KHONG_LIEN_KET = ("B", "C_khong_lien_ket")

# Nhánh nào áp luật chuyển trạng thái.
CO_AP_LUAT = ("C", "D", "C_khong_lien_ket",
              "C_quan_he", "C_quan_he_luat", "D_quan_he", "C_khoa", "C_khoa_hoi")

# Nhánh nào chạy hậu kiểm (kiểm đầy đủ + sửa cục bộ).
CO_HAU_KIEM = ("D", "D_quan_he")

# Nhánh nào qua KHOÁ BẰNG CHỨNG + CỔNG RỦI RO (tầng 4-5 của đề xuất 11/09/2026),
# và nhánh nào chọn thêm câu HỎI LẠI (tầng 6). Cả ba tầng là MÃ THUẦN đối chiếu
# với chính hội thoại, nên chạy được bằng `--tu-dem`, không cần GPU. C_khoa là C
# CỘNG khoá, không gì khác: chênh lệch C_khoa - C là đóng góp của riêng tầng khoá.
# `C_khoa_v2` sử dụng `may_trang_thai_hoi_thoai` (Conversational FSM) thay cho `cap_nhat`,
# bảo toàn 100% hành vi của nhánh `C_khoa` cũ.
CO_KHOA = ("C_khoa", "C_khoa_hoi", "C_khoa_v2")

NHANH_TRUNG_GIAN = ("B", "C", "C_ghi_de", "D", "C_khong_lien_ket",
                    "C_khong_luat", "C_quan_he", "C_quan_he_luat", "D_quan_he",
                    "C_khoa", "C_khoa_hoi", "C_khoa_v2")


# ═══ ten_ket_qua() — Đặt tên nhánh trong tên tệp kết quả ══════════════════════════════
# A có adapter và A nền khác nhau để không ghi đè lên nhau.
def ten_ket_qua(nhanh, adapter):
    """Tên nhánh dùng trong TÊN TỆP kết quả. Hàm thuần tuý để test được.

    Nhánh A có adapter và nhánh A nền (không adapter) là HAI thứ khác nhau —
    chúng là hai cột trong cùng một bảng so sánh, và chênh lệch giữa chúng
    chính là "huấn luyện đóng góp bao nhiêu".

    Trước 10/09/2026 cả hai đều ghi vào `ra_A_<tap>.jsonl`. Chuỗi dùng lại
    chạy 2b (có adapter) rồi 2c (không adapter) liền nhau, và kết quả của 2b
    BIẾN MẤT — im lặng, không báo gì.

    Lỗi còn kín hơn ở chỗ: `cham_lai_bang_quy_gan.NHANH` ĐÃ liệt kê "A_nen"
    như một nhánh riêng. Bên ĐỌC luôn mong đợi một tệp mà bên GHI chưa bao giờ
    tạo ra, và hai bên lệch nhau suốt mà không ai báo.

    Cùng họ với lý do tệp đệm trích phải kèm `max_token` và hậu tố `_hl`.
    """
    return nhanh if adapter else nhanh + "_nen"


# ═══ chay_trung_gian() — Chạy các nhánh B, C, D dùng chung một đường ống ══════════════
# Khác nhau đúng hai bước: liên kết chủ thể và áp luật, sau đó bổ sung và sửa ở nhánh D.
def chay_trung_gian(mau_list, tok, model, prefix_fn, nhanh,
                    max_token=1536, kq_tho=None, prefix_phan=None,
                    bat_buoc_trich_dan=None, chinh_sach="C",
                    prompt_lookup_num_tokens=None):
    """Ba nhánh dùng chung một đường ống, khác nhau ĐÚNG hai bước.

        B        trích -> sinh.          Không liên kết thực thể, không áp luật.
        C        trích -> liên kết -> áp luật -> sinh (chỉ bản còn hiệu lực).
        C_ghi_de trích -> liên kết -> GHI ĐÈ bản trước -> sinh.
        D        C, rồi bổ sung cho bỏ sót (Task 16) và sửa cục bộ (Task 17).

    Hai cấu hình bóc cơ chế (Task 19) — chúng làm đầy ô 2x2, không phải
    nhánh độc lập:

        C_khong_lien_ket  có luật quan hệ, KHÔNG liên kết thực thể
        C_khong_luat      có liên kết thực thể, KHÔNG luật quan hệ

    Cộng với B (không có gì) và C (có cả hai) là đủ bốn ô. Thiếu một ô thì
    không tách được đóng góp của từng cơ chế, chỉ nói được "gộp lại thì hơn".

    C_ghi_de là đối chứng của riêng phần cập nhật (Task 15 bước 3): nếu C
    không hơn được quy tắc "phát biểu sau ghi đè phát biểu trước" trên các
    tình huống cố định chính, thì phần luật quan hệ chưa chứng minh được gì.

    Viết chung một hàm để ba nhánh KHÁC NHAU đúng ở chỗ định nói, không khác
    ở những chỗ lặt vặt — nếu không thì chênh lệch đo được sẽ lẫn lộn
    nguyên nhân.

    `kq_tho`: đầu ra trích xuất đã có sẵn. SÁU nhánh dùng CHUNG một bước
    trích; chạy riêng từng nhánh là sinh lại sáu lần, mỗi lần 30-40 phút.
    Truyền lại kết quả trích vào đây vừa nhanh gấp sáu lần, vừa bảo đảm mỗi
    nhánh nhìn thấy ĐÚNG một đầu ra mô hình — chênh lệch đo được chắc chắn
    đến từ hậu xử lý chứ không từ một lần sinh khác.
    """
    from src.huan_luyen import chon_mo_hinh_bakeoff as bakeoff
    from src.duong_ong import b3_cap_nhat_trang_thai as cap_nhat
    from src.duong_ong import b1_cau_truc_menh_de as phat_bieu
    from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
    from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the

    assert nhanh in NHANH_TRUNG_GIAN, nhanh
    if kq_tho is None:
        if prompt_lookup_num_tokens is not None:
            kq_tho = bakeoff.trich(tok, model, prefix_fn, mau_list, max_token=max_token,
                                   prompt_lookup_num_tokens=prompt_lookup_num_tokens)
        else:
            kq_tho = bakeoff.trich(tok, model, prefix_fn, mau_list, max_token=max_token)
    if bat_buoc_trich_dan is None:
        # Tự động theo ĐẦU RA, một lần cho cả lần chạy: adapter thế hệ 5 viết
        # trường trích dẫn, nên thiếu trích dẫn là lỗi và bị chặn. Đầu ra cũ (thế
        # hệ 4, mô hình nền) chưa bao giờ thấy trường đó — chặn thì mọi phát biểu
        # của nó đều bị chặn, nên chỉ cảnh báo.
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
        # `ten_chu_the` do `phat_bieu.tu_json` gán ngay tại chỗ đúng bản ghi.
        # Trước 10/09/2026 chỗ này gán lại bằng `zip(ps, [... luot_thoai])`,
        # và phép zip đó lệch hàng khi có bản ghi vừa có `luot_thoai` vừa
        # không hợp lệ — nó bị loại khỏi `ps` nhưng vẫn còn bên phải, nên từ
        # đó trở đi mỗi phát biểu nhận tên chủ thể của phát biểu kế tiếp.
        # Bước phân quan hệ theo từng cặp. Phải chạy TRƯỚC `ap_luat`, vì
        # `ap_luat` đọc trường `quan_he` — chạy sau thì không còn tác dụng gì.
        tk_phan = None
        if nhanh in DUONG_PHAN:
            from src.duong_ong import b3_phan_xu_quan_he as phan_quan_he
            tk_phan_duong = DUONG_PHAN[nhanh]
            if tk_phan_duong != "luat" and model is None:
                raise SystemExit(
                    f"nhanh {nhanh} can mo hinh de phan quan he; "
                    f"--tu-dem chi chay duoc nhanh C_quan_he_luat")
            ps, tk_phan = phan_quan_he.phan(
                ps, _van_ban_theo_luot(m["input"]), duong=tk_phan_duong,
                tok=tok, model=model, prefix_fn=prefix_phan)

        fsm_meta = {}
        if nhanh in CO_AP_LUAT:
            ps = cap_nhat.ap_luat(ps, hoi_thoai=m["input"])
        elif nhanh == "C_khoa_v2":
            from src.duong_ong import b2_bu_chu_ngu_tinh_luoc as _fsm_mod
            fsm = _fsm_mod.MayTrangThaiHoiThoai()
            canh_bao_l2_l3 = []
            for item_p in ps:
                ok_l23, loi_l23 = _fsm_mod.kiem_tra_l2_sang_l3(item_p)
                if not ok_l23:
                    canh_bao_l2_l3.extend(loi_l23)
                fsm.them_phat_bieu(item_p)
            ps = fsm.danh_sach
            fsm_meta = {
                "fsm_lich_su_chuyen": [
                    {
                        "id_moi": s.id_moi,
                        "id_cu": s.id_cu,
                        "quan_he": s.quan_he,
                        "trang_thai_truoc": s.trang_thai_truoc,
                        "trang_thai_sau": s.trang_thai_sau,
                        "ly_do": s.ly_do,
                    }
                    for s in fsm.lich_su_chuyen
                ],
                "fsm_dinh_chinh": fsm.lay_lich_su_dinh_chinh_kem_am_thanh(),
                "fsm_mau_thuan": fsm.lay_danh_sach_mau_thuan_kem_am_thanh(),
                "fsm_canh_bao_l2_l3": canh_bao_l2_l3,
            }
        elif nhanh == "C_ghi_de":
            ps = cap_nhat.ghi_de_phat_bieu_truoc(ps)

        # Tầng khoá + rủi ro + hỏi lại. Khoá đối chiếu với HỘI THOẠI, không với
        # bảng phát biểu; phát biểu bị CHẶN xuống CẦN XÁC NHẬN kèm lý do của khoá.
        khoa, ly_do_chan = {}, None
        if nhanh in CO_KHOA:
            from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
            from src.duong_ong import b6_goi_y_hoi_lai as hoi_lai
            from src.duong_ong import b4_kiem_can_cu as khoa_bang_chung
            kk = khoa_bang_chung.khoa_ca(ps, m["input"],
                                         bat_buoc_trich_dan=bat_buoc_trich_dan)
            thong_tin_bn = m.get("thong_tin_benh_nhan") if isinstance(m.get("thong_tin_benh_nhan"), dict) else None
            dg = cong_rui_ro.cham(ps, kk["ket_qua"], thong_tin_bn)
            ly_do_chan = khoa_bang_chung.ly_do_chan(kk["ket_qua"])
            # Chính sách cách C (22/09/2026): dị ứng / thuốc có cảnh báo cứng sang
            # CẦN XÁC NHẬN. Lý do chặn của khoá được ưu tiên khi trùng id.
            ly_do_chan_khoa = ly_do_chan
            ly_do_chan = {**cong_rui_ro.dua_sang_xac_nhan(dg), **ly_do_chan}
            # Lớp cảnh báo (24/09/2026). Luôn tính và lưu để đo/hiện; CHỈ đổi bản nháp
            # khi gọi rõ chinh_sach="D". Mặc định "C": mọi con số đã báo cáo không đổi.
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
                    "canh_bao": canh_bao_gop.to_dict(cb),
                    **fsm_meta}

        van, ghi_chu = sinh_benh_an.sinh(ps, ten_chu_the=ten_chu_the,
                                         ly_do_chan=ly_do_chan)
        if khoa.get("cau_hoi"):
            van += (f"\n\n{sinh_benh_an.MUC_HOI_LAI}\n\n" + "\n".join(
                f"{i}. {c['van']}" for i, c in enumerate(khoa["cau_hoi"], 1)))

        da_bo_sung, da_sua = [], []
        if nhanh in CO_HAU_KIEM:
            from src.duong_ong import b4_kiem_day_du as kiem_day_du
            from src.duong_ong import b6_sua_cuc_bo as sua_cuc_bo
            van, da_bo_sung = kiem_day_du.bo_sung(ps, van, ten_chu_the=ten_chu_the)
            ket = sua_cuc_bo.sua(van, ps, ten_chu_the=ten_chu_the)
            van, da_sua = ket.van_ban, ket.da_sua
        # Lưu CẢ HAI bản. Mục CẦN XÁC NHẬN không có trong bản tham chiếu nên
        # bộ chấm đếm nó là một mục dự đoán thừa, kéo Section F1 xuống. Phải
        # báo cáo cả hai số, và báo cáo luôn số phát biểu bị chuyển xuống đó —
        # nếu không thì mục đó thành chỗ giấu mọi thứ khó.
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
                   # Bản ghi SAU áp luật: đầu vào của phép đo tầng khoá, của
                   # giao diện duyệt và của bộ 500 GPT (`bo_gpt500 --cham`).
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


# ═══ main() — Điểm vào dòng lệnh chạy các nhánh so sánh ═══════════════════════════════
# Nạp mô hình một lần rồi chạy lần lượt nhiều nhánh trên cùng một tập.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    # nargs="+": nạp 8B mất vài phút và chiếm gần hết VRAM, không thể nạp
    # hai bản cùng lúc. Chạy nhiều nhánh trong MỘT lần nạp tiết kiệm hẳn
    # thời gian đo, và bảo đảm mọi nhánh thấy đúng một mô hình.
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
    # 3072: ở 1536 thì 8/35 hội thoại thật bị cắt cụt giữa JSON
    # (14-28 lượt thoại), làm 7/35 bệnh án ra rỗng.
    ap.add_argument("--max-token", type=int, default=3072)
    # Khâu SINH bệnh án là mã thuần, không dùng mô hình. Có cờ
    # tệp đệm trích rồi thì sinh lại được trong vài giây, không
    # phải nạp mô hình và không tranh GPU với ai.
    ap.add_argument("--tu-dem", action="store_true",
                    help="sinh lai tu tep dem, khong nap mo hinh")
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    from src.bo_du_lieu import nap_du_lieu as du_lieu

    trung_gian = [n for n in a.nhanh if n not in ("A", "A+")]
    if trung_gian:
        from src.huan_luyen import chon_mo_hinh_bakeoff as bakeoff
        # B/C trích bản ghi có cấu trúc, nên phải ÉP JSON. A/A+ sinh văn xuôi,
        # không ép. Đó là lý do hai đường nạp mô hình khác nhau, không phải
        # do trùng lặp.
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
        # Trích MỘT lần cho cả sáu nhánh. Xem docstring chay_trung_gian.
        # `luu_dan`: ghi từng mẫu ngay khi xong. Chạy lại lệnh này sau khi bị
        # ngắt thì nó chạy tiếp từ chỗ đó, không làm lại từ đầu.
        # Tên tệp đệm KÈM max_token: kết quả trích ở 1536 và ở 3072 là hai
        # thứ khác nhau, trộn chung một tệp thì lần chạy sau sẽ dùng lại bản
        # bị cắt cụt mà không ai biết.
        # Tên tệp đệm kèm cả adapter: kết quả trích của mô hình nền và của
        # mô hình đã huấn luyện là hai thứ khác nhau, trộn chung một tệp thì
        # lần sau dùng lại bản cũ mà không ai biết.
        hau = "_hl" if a.adapter_trich else ""
        dem = (duong_dan.THU_MUC_DU_LIEU /
               f"trich_{a.tap}_{a.max_token}{hau}.jsonl")
        kq_tho = bakeoff.trich(tok, model, prefix_fn, mau, luu_dan=dem,
                               max_token=a.max_token)
        # Bước phân quan hệ dùng LƯỢC ĐỒ KHÁC với bước trích (một trường thay
        # vì một danh sách bản ghi), nên phải có bộ ép riêng. Chỉ dùng khi có
        # nhánh nào thực sự cần, và chỉ khi có mô hình.
        prefix_phan = None
        if model is not None and any(n in DUONG_PHAN and DUONG_PHAN[n] != "luat"
                                     for n in trung_gian):
            from src.duong_ong import b3_phan_xu_quan_he as phan_quan_he
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
            # Con số quan trọng nhất của bước phân quan hệ: trước khi có nó,
            # `quan_he` bằng "không" ở 282/282 phát biểu. Bằng 0 ở đây nghĩa
            # là bước phân vẫn chưa chạy được, không phải là hội thoại không
            # có quan hệ.
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
