# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Dữ liệu ngoài]
Làm gì   : Chuyển bộ 500 hội thoại phương ngữ do GPT sinh sang định dạng ca của dự án và
           chấm điểm, chỉ để đo, không để huấn luyện.
Vào → Ra : tệp JSONL bộ GPT500 + tệp dự đoán của nhánh → tệp ca định dạng dự án (tên có chữ
           gpt) và bảng điểm từng mệnh đề
Đọc từ   : chuyen() đổi một bản ghi sang định dạng dự án; cham_ca() chấm một ca; main()
           chuyển, đo, chấm
Mục lục (các hàm/lớp chính):
  ghi()            Chuyển cả bộ GPT500 và ghi tệp ra
  chuyen()         Chuyển một bản ghi bộ GPT sang định dạng dự án
  do_phuong_ngu()  Đo bảng chuẩn hoá nhận ra phương ngữ của bộ này đến đâu
  tong_hop()       Tổng hợp điểm cả bộ từ dự đoán của một nhánh
  nap_du_doan()    Nạp tệp dự đoán của một nhánh theo id
  cham_ca()        Chấm một ca, mỗi mệnh đề đáp án một dòng kết quả
  main()           Điểm vào dòng lệnh: chuyển, đo phương ngữ, chấm
Gọi tới  : do_luong/khoang_tin_cay, do_luong/thuoc_do_quy_gan,
           duong_ong/b0_chuan_hoa_phuong_ngu, he_thong/duong_dan
Tên cũ   : bo_gpt500.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bộ 500 hội thoại phương ngữ DO GPT SINH -> định dạng ca của dự án. CHỈ ĐỂ ĐO.

NGUỒN — đọc trước khi dùng. Người dùng xác nhận ngày 11/09/2026: bộ 500 hội
thoại (`data/ngoai/phuong_ngu_500.jsonl`) và hai từ điển phương ngữ kèm theo do
GPT sinh. Dự án có ràng buộc cứng: KHÔNG dùng mô hình ngôn ngữ thương mại ở bất
kỳ khâu nào, kể cả sinh dữ liệu huấn luyện. Nên bộ này:

  - KHÔNG BAO GIỜ vào huấn luyện hay chọn checkpoint. Tên tệp ra mang chữ "gpt",
    và `du_lieu.chan_du_lieu_gpt` chặn mọi đường huấn luyện đọc tệp có chữ đó.
  - KHÔNG gộp vào tập kiểm tra cuối, không trộn với bộ tự sinh.
  - Mọi con số từ bộ này phải kèm `KHAI_NGUON`, và KHÔNG được gọi là hội thoại
    thật.

ĐÁP ÁN CỦA BỘ NÀY KHÁC ĐÁP ÁN CỦA ĐỀ TÀI:
  - không có lượt bằng chứng, không có trích dẫn -> không đo được tầng khoá
  - `status` gộp BA trục mà lược đồ dự án có ý tách (mức chắc chắn / tình huống /
    trạng thái) -> `ANH_XA` trả lại, và chính việc ánh xạ là một nguồn sai
  - chủ thể ghi bằng TỪ QUAN HỆ: khuôn `daughter_elderly_dizzy` thì "mẹ" là BỆNH
    NHÂN, khuôn `allergy_relative` thì "mẹ" là NGƯỜI NHÀ. Ai là bệnh nhân phải tra
    THEO KHUÔN (`BENH_NHAN`) — một bảng tôi ĐỌC TAY từ `speaker_context` và câu hỏi
    của bác sĩ trong từng khuôn, không phải đáp án có sẵn. Khuôn nào đọc không ra
    thì để trống `BENH_NHAN_MO_HO` và không chấm chủ thể.
  - hội thoại 4 lượt, 2,2 mệnh đề mỗi ca

ĐO ĐƯỢC: tìm thấy mệnh đề không, CHỦ THỂ (bệnh nhân hay người khác), và LỚP mức
khẳng định. Lớp quan trọng nhất là `KHONG_LA_SU_THAT` (câu hỏi chưa trả lời, giả
định, đang chờ kết quả, bản bị thay thế, mâu thuẫn): ghi nó vào thân hồ sơ như
một sự thật là RÒ RỈ.

    python -m src.bo_du_lieu.nap_bo_gpt500 --chuyen          # -> data/gpt500_phuong_ngu.jsonl
    python -m src.bo_du_lieu.nap_bo_gpt500 --do-phuong-ngu   # bảng chuẩn hoá nhận ra từ không
    python -m src.bo_du_lieu.nap_bo_gpt500 --cham data/ra_C_gpt500_phuong_ngu.jsonl
"""
import argparse
import io
import json
import re
import sys
from collections import Counter, defaultdict

from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.he_thong import duong_dan as duong_dan
from src.do_luong.thuoc_do_quy_gan import _tu_noi_dung

NGUON = duong_dan.THU_MUC_DU_LIEU / "ngoai" / "phuong_ngu_500.jsonl"
TEN_TAP = "gpt500_phuong_ngu"
TEP_RA = duong_dan.THU_MUC_DU_LIEU / f"{TEN_TAP}.jsonl"
KHAI_NGUON = ("dữ liệu tổng hợp do GPT sinh (người dùng cung cấp 10/09/2026, "
              "xác nhận nguồn 11/09/2026) — chỉ để đo, không huấn luyện")

# Vai trong bộ GPT -> vai trong hội thoại của dự án. Người nhà nào cũng thành
# "Người nhà" như bộ tự sinh (mô hình chưa từng thấy nhãn "Mẹ:", "Vợ:"); vai gốc
# giữ trong trường `vai_goc`. "Trẻ" là bệnh nhi TỰ NÓI (khuôn child_direct_speech).
VAI = {"Bác sĩ": "Bác sĩ", "Điều dưỡng": "Điều dưỡng", "Bệnh nhân": "Bệnh nhân",
       "Trẻ": "Bệnh nhân"}
VAI_NGUOI_NHA = "Người nhà"

# Ai là BỆNH NHÂN trong từng khuôn — đọc tay, xem docstring.
BENH_NHAN = {
    "guardian_child_fever": "trẻ",
    "guardian_child_cough": "trẻ",
    "spouse_headache": "chồng",        # "Người đau đầu là anh nhà chị hay chị?"
    "daughter_elderly_dizzy": "mẹ",    # con gái kể hộ người cao tuổi
    "nurse_breathing": "bệnh nhân",
    "allergy_relative": "trẻ",         # dị ứng là của MẸ; bệnh nhân là trẻ
    "allergy_patient": "bệnh nhân",
    "medication_unknown": "bệnh nhân",
    "medication_stopped": "cha",       # "Ba anh đã ngưng từ bao lâu?"
    "duration_correction": "trẻ",
    "vomiting_progress": "bệnh nhân",
    "diarrhea_progress": "trẻ",
    "unanswered_question": "bệnh nhân",
    "suspected_diagnosis": "bệnh nhân",
    "conditional_plan": "trẻ",
    "family_history": "mẹ",            # "Hôm nay người khám là ai?" "Dạ là má tôi"
    "surgery_history": "bệnh nhân",
    "vaccination_uncertain": "trẻ",
    "lab_pending": "bệnh nhân",
    "symptom_negation": "bệnh nhân",
    "multiple_relatives": "trẻ",       # bà ngoại là người nhà
    "pronoun_resolution": "chồng",     # KHÔNG CHẮC — xem BENH_NHAN_MO_HO
    "child_direct_speech": "trẻ",
    "social_history": "bệnh nhân",
    "contradictory_sources": "trẻ",
}
# Lời chào gọi tên một người ("đưa Nam đi khám") nhưng tên rút ngẫu nhiên, còn
# vợ chỉ nói thuốc của "ông ấy" — không đủ để biết ông ấy có phải bệnh nhân.
BENH_NHAN_MO_HO = frozenset({"pronoun_resolution"})

KHANG_DINH = "khẳng định"
PHU_DINH = "phủ định"
CHUA_GHI_NHAN = "chưa ghi nhận"
NGHI_NGO = "nghi ngờ"
KHONG_LA_SU_THAT = "không là sự thật"
LOP_SU_THAT = (KHANG_DINH, PHU_DINH, CHUA_GHI_NHAN, NGHI_NGO)

# `status` của bộ GPT -> lớp. "chưa xác định" ("tôi không nhớ bé đã dùng lần nào")
# gộp vào CHƯA GHI NHẬN: lược đồ dự án không có mục riêng, và cả hai đều là một
# chỗ TRỐNG, không phải một khẳng định âm.
ANH_XA = {
    "khẳng định": KHANG_DINH,
    "bệnh nhân báo cáo": KHANG_DINH,
    "phủ định": PHU_DINH,
    "chưa ghi nhận": CHUA_GHI_NHAN,
    "chưa xác định": CHUA_GHI_NHAN,
    "nghi ngờ": NGHI_NGO,
    "không được kết luận": KHONG_LA_SU_THAT,
    "bị thay thế": KHONG_LA_SU_THAT,
    "mâu thuẫn/chưa giải quyết": KHONG_LA_SU_THAT,
    "giả định": KHONG_LA_SU_THAT,
    "kế hoạch": KHONG_LA_SU_THAT,
    "kế hoạch có điều kiện": KHONG_LA_SU_THAT,
    "đang chờ": KHONG_LA_SU_THAT,
}


# ═══ chuyen() — Chuyển một bản ghi bộ GPT sang định dạng dự án ════════════════════════
# Đổi lượt nói thành văn bản, kiểm khuôn và trạng thái; báo lỗi nếu chưa ánh xạ.
# ------------------------------------------------------------------ chuyển đổi
def chuyen(ban_ghi) -> dict:
    kich = ban_ghi["scenario_id"]
    if kich not in BENH_NHAN:
        raise SystemExit(f"khuon moi chua co trong BENH_NHAN: {kich}")
    for g in ban_ghi["gold_claims"]:
        if g["status"] not in ANH_XA:
            raise SystemExit(f"status chua anh xa: {g['status']!r} ({ban_ghi['id']})")
    luot = sorted(ban_ghi["dialogue"], key=lambda t: t["turn_id"])
    return {"id": ban_ghi["id"],
            "input": "\n".join(f"{VAI.get(t['speaker'], VAI_NGUOI_NHA)}: {t['text']}"
                               for t in luot),
            "output": "",                   # bộ này không có bản tham chiếu
            "gpt_sinh": True, "khai_nguon": KHAI_NGUON,
            "scenario_id": kich, "region_style": ban_ghi.get("region_style"),
            "phenomena": list(ban_ghi.get("phenomena") or []),
            "dialect_terms_used": list(ban_ghi.get("dialect_terms_used") or []),
            "vai_goc": [t["speaker"] for t in luot],
            "benh_nhan": BENH_NHAN[kich],
            "gold_claims": ban_ghi["gold_claims"]}


# ═══ nap() — Đọc tệp JSONL thành danh sách bản ghi ════════════════════════════════════
# Bỏ qua dòng trống.
def nap(tep):
    return [json.loads(x) for x in open(tep, encoding="utf-8") if x.strip()]


# ═══ ghi() — Chuyển cả bộ GPT500 và ghi tệp ra ════════════════════════════════════════
# Dừng nếu id bị trùng.
def ghi(nguon=NGUON, tep=TEP_RA):
    ds = [chuyen(b) for b in nap(nguon)]
    ids = [d["id"] for d in ds]
    if len(set(ids)) != len(ids):
        raise SystemExit("id trung trong bo GPT")
    with open(tep, "w", encoding="utf-8") as f:
        for d in ds:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return ds


# ═══ do_phuong_ngu() — Đo bảng chuẩn hoá nhận ra phương ngữ của bộ này đến đâu ════════
# Đếm từ nhận ra và từ trượt; phép đo mang tính vòng tròn vì cùng nguồn GPT.
# ------------------------------------------------------ bảng chuẩn hoá, tầng 1
def do_phuong_ngu(ds):
    """Bảng chuẩn hoá có NHẬN RA từ phương ngữ bộ này khai không.

    VÒNG TRÒN: bảng chuẩn hoá lấy từ từ điển mở rộng, CÙNG nguồn GPT với bộ này.
    Con số "nhận ra" chỉ nói bảng phủ từ của chính nguồn của nó; chỗ TRƯỢT mới
    là thông tin — từ có trong hội thoại mà bảng không biết.
    """
    ket, truot = Counter(), Counter()
    for d in ds:
        thap = d["input"].lower()
        cho = [c for c in chuan_hoa.phan_tich(d["input"]) if c.muc_tin]
        for tu in d["dialect_terms_used"]:
            t = tu.lower()
            vt = [m.start() for m in re.finditer(re.escape(t), thap)]
            if not vt:
                ket["khong_thay_trong_hoi_thoai"] += 1
                continue
            if any(c.bat_dau < a + len(t) and a < c.ket_thuc for a in vt for c in cho):
                ket["nhan_ra"] += 1
            else:
                ket["truot"] += 1
                truot[tu] += 1
    return ket, truot


# ─── _tu() — Tách tập từ nội dung đã chuẩn hoá ────────────────────────────────────────
# Dùng để so từ giữa hai chuỗi.
# ------------------------------------------------------------------ chấm điểm
def _tu(s):
    return set(_tu_noi_dung(chuan_hoa.chuan_hoa(str(s or ""))))


# ═══ lop_phat_bieu() — Xếp một mệnh đề vào lớp để so với đáp án GPT ═══════════════════
# Lớp: khẳng định, phủ định, nghi ngờ, chưa ghi nhận hoặc không là sự thật.
def lop_phat_bieu(p) -> str:
    """Một phát biểu (dict, lược đồ dự án) -> lớp để so với `ANH_XA`."""
    if (p.get("tinh_huong") or "thực tế") != "thực tế" or \
            (p.get("trang_thai") or "còn hiệu lực") != "còn hiệu lực":
        return KHONG_LA_SU_THAT
    muc = p.get("do_chac_chan") or "chắc chắn"
    if muc == CHUA_GHI_NHAN:
        return CHUA_GHI_NHAN
    if muc == NGHI_NGO:
        return NGHI_NGO
    return PHU_DINH if p.get("phu_dinh") else KHANG_DINH


# ─── _diem() — Tính điểm giống nhau giữa một đáp án và một mệnh đề ────────────────────
# Cần chung ít nhất một từ nội dung; mốc thời gian chỉ cộng thêm.
def _diem(claim, p):
    """Trùng ít nhất một từ nội dung mới tính; mốc thời gian chỉ để phân xử hai
    bản cùng khái niệm ("sốt bốn ngày" bị thay thế, "sốt hai ngày" còn hiệu lực)."""
    a, b = _tu(claim.get("concept")), _tu(p.get("noi_dung"))
    chung = a & b
    if not chung:
        return 0.0
    d = len(chung) / len(a | b)
    t1, t2 = _tu(claim.get("time")), _tu(p.get("moc_thoi_gian"))
    if t1 and t2:
        d += 0.5 * len(t1 & t2) / len(t1 | t2)
    return d


# ═══ ghep() — Ghép đáp án với mệnh đề theo kiểu tham lam 1-1 ══════════════════════════
# Trả từ điển chỉ số đáp án sang chỉ số mệnh đề, điểm cao trước.
def ghep(claims, ps):
    """Ghép 1-1 tham lam theo điểm giảm dần -> {chỉ số claim: chỉ số phát biểu}."""
    cap = sorted(((_diem(c, p), i, j) for i, c in enumerate(claims)
                  for j, p in enumerate(ps)), key=lambda x: -x[0])
    ra, da = {}, set()
    for d, i, j in cap:
        if d <= 0:
            break
        if i in ra or j in da:
            continue
        ra[i] = j
        da.add(j)
    return ra


# ═══ cham_ca() — Chấm một ca, mỗi mệnh đề đáp án một dòng kết quả ═════════════════════
# Xét tìm thấy, đúng chủ thể, đúng lớp; có tính phần bị chặn của tầng khoá.
def cham_ca(ca, ps, bi_chan=frozenset()):
    """-> một dòng kết quả cho MỖI mệnh đề đáp án của ca.

    `ps`: phát biểu (dict) SAU áp luật. `bi_chan`: id phát biểu tầng khoá đã chặn
    — không vào thân hồ sơ, nên không thể rò rỉ.
    """
    ghep_ = ghep(ca["gold_claims"], ps)
    mo_ho = ca["scenario_id"] in BENH_NHAN_MO_HO
    ra = []
    for i, c in enumerate(ca["gold_claims"]):
        lop = ANH_XA[c["status"]]
        la_bn = c["subject"] == ca["benh_nhan"]
        p = ps[ghep_[i]] if i in ghep_ else None
        than = (p is not None and p.get("id") not in bi_chan
                and lop_phat_bieu(p) in LOP_SU_THAT)
        k = {"id": ca["id"], "scenario_id": ca["scenario_id"], "lop": lop,
             "la_benh_nhan": la_bn, "tim_thay": p is not None, "vao_than": than}
        if lop == KHONG_LA_SU_THAT:
            k["ro_ri"] = than
        elif p is not None:
            k["dung_lop"] = lop_phat_bieu(p) == lop
            if not mo_ho:
                bn_du_doan = p.get("chu_the_id", 0) == 0
                k["dung_chu_the"] = bn_du_doan == la_bn
                k["nguoi_khac_thanh_benh_nhan"] = (not la_bn) and bn_du_doan
        ra.append(k)
    return ra


# ─── _ty_le() — Tính tỷ lệ theo ca, bootstrap theo khuôn ──────────────────────────────
# Đơn vị độc lập là khuôn, không phải ca.
def _ty_le(ket, loc, truong, khuon):
    """Tỷ lệ theo CA rồi bootstrap cụm THEO KHUÔN (scenario_id) — 25 cụm, mỗi
    khuôn 20 ca gần như giống nhau, nên đơn vị độc lập là khuôn, không phải ca."""
    from src.do_luong import khoang_tin_cay as sai_so
    theo_ca = defaultdict(list)
    for k in ket:
        if loc(k) and k.get(truong) is not None:
            theo_ca[k["id"]].append(1.0 if k[truong] else 0.0)
    if not theo_ca:
        return None
    gt = {i: sum(v) / len(v) for i, v in theo_ca.items()}
    kq = sai_so.khoang(gt, {i: khuon[i] for i in gt})
    kq["so_menh_de"] = sum(len(v) for v in theo_ca.values())
    return kq


# ═══ tong_hop() — Tổng hợp điểm cả bộ từ dự đoán của một nhánh ════════════════════════
# Ca không có dự đoán tính là không tìm thấy gì, không bỏ đi.
def tong_hop(cac_ca, du_doan):
    """`du_doan`: {id: (phat_bieu, bi_chan)}. Ca không có dự đoán tính là không
    tìm thấy gì — không được bỏ đi cho đẹp số."""
    ket = []
    for ca in cac_ca:
        ps, chan = du_doan.get(ca["id"], ([], set()))
        ket.extend(cham_ca(ca, ps, chan))
    khuon = {ca["id"]: ca["scenario_id"] for ca in cac_ca}
    su_that = lambda k: k["lop"] in LOP_SU_THAT             # noqa: E731
    bang = {
        "tim_thay": _ty_le(ket, su_that, "tim_thay", khuon),
        "dung_chu_the": _ty_le(ket, su_that, "dung_chu_the", khuon),
        "dung_lop": _ty_le(ket, su_that, "dung_lop", khuon),
        "ro_ri": _ty_le(ket, lambda k: k["lop"] == KHONG_LA_SU_THAT, "ro_ri", khuon),
        "nguoi_khac_thanh_benh_nhan": _ty_le(
            ket, lambda k: su_that(k) and not k["la_benh_nhan"],
            "nguoi_khac_thanh_benh_nhan", khuon),
    }
    theo_khuon = {}
    for k in ket:
        t = theo_khuon.setdefault(k["scenario_id"], Counter())
        t["menh_de"] += 1
        for truong in ("tim_thay", "dung_chu_the", "dung_lop", "ro_ri",
                       "nguoi_khac_thanh_benh_nhan"):
            if k.get(truong) is not None:
                t[truong + "_n"] += 1
                t[truong] += bool(k[truong])
    return {"bang": bang, "theo_khuon": theo_khuon, "so_ca": len(cac_ca),
            "so_ca_co_du_doan": sum(1 for ca in cac_ca if ca["id"] in du_doan),
            "khai_nguon": KHAI_NGUON}


# ═══ nap_du_doan() — Nạp tệp dự đoán của một nhánh theo id ════════════════════════════
# Trả phát biểu và id bị chặn; thiếu trường phat_bieu thì dừng kèm lệnh sinh lại.
def nap_du_doan(tep):
    """ra_<nhanh>_gpt500_phuong_ngu.jsonl -> {id: (phat_bieu, id bị chặn)}."""
    ra = {}
    for r in nap(tep):
        if "phat_bieu" not in r:
            raise SystemExit(
                f"{tep}: ban ghi khong co truong `phat_bieu` — sinh lai bang "
                f"`python -m src.duong_ong.chay_duong_ong --nhanh C C_khoa --tu-dem --tap {TEN_TAP} "
                f"--adapter-trich <adapter>`")
        chan = {k["id"] for k in r.get("khoa", []) if k.get("chan")}
        ra[r["id"]] = (r["phat_bieu"], chan)
    return ra


# ─── _in_bang() — In bảng kết quả chấm ra màn hình ────────────────────────────────────
# Mỗi chỉ số có trung bình, khoảng tin cậy và số mệnh đề, ca, khuôn.
def _in_bang(tk):
    print(f"NGUON: {tk['khai_nguon']}")
    print(f"ca: {tk['so_ca']} (co du doan: {tk['so_ca_co_du_doan']})")
    for ten, k in tk["bang"].items():
        if k is None:
            print(f"  {ten:28} (khong co menh de)")
            continue
        print(f"  {ten:28} {k['trung_binh']:6.1%}  [{k['thap']:.1%}; {k['cao']:.1%}]"
              f"  n={k['so_menh_de']} menh de / {k['so_ca']} ca / "
              f"{k['so_khuon']} {k['don_vi']}")
    print("  theo khuon (ty le tren menh de):")
    for kich, t in sorted(tk["theo_khuon"].items()):
        o = [f"{ten}={t[ten]}/{t[ten + '_n']}" for ten in
             ("tim_thay", "dung_chu_the", "dung_lop", "ro_ri") if t[ten + "_n"]]
        print(f"    {kich:26} " + "  ".join(o))


# ═══ main() — Điểm vào dòng lệnh: chuyển, đo phương ngữ, chấm ═════════════════════════
# Các cờ --chuyen, --do-phuong-ngu, --cham chọn việc cần làm.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chuyen", action="store_true")
    ap.add_argument("--do-phuong-ngu", action="store_true")
    ap.add_argument("--cham", nargs="+", default=None,
                    help="tep ra_<nhanh>_gpt500_phuong_ngu.jsonl")
    a = ap.parse_args()
    if a.chuyen:
        ds = ghi()
        print(f"Ghi {len(ds)} ca -> {TEP_RA}\nNGUON: {KHAI_NGUON}")
    if a.do_phuong_ngu or a.cham:
        ds = nap(TEP_RA)
    if a.do_phuong_ngu:
        ket, truot = do_phuong_ngu(ds)
        tong = ket["nhan_ra"] + ket["truot"]
        print(f"bang chuan hoa nhan ra {ket['nhan_ra']}/{tong} lan xuat hien tu "
              f"phuong ngu duoc khai; khong thay trong hoi thoai: "
              f"{ket['khong_thay_trong_hoi_thoai']}")
        print("  (VONG TRON: bang va bo nay cung nguon GPT)")
        for tu, n in truot.most_common():
            print(f"  truot: {tu!r} x{n}")
    for tep in a.cham or []:
        print(f"\n=== {tep}")
        _in_bang(tong_hop(ds, nap_du_doan(tep)))


if __name__ == "__main__":
    main()
