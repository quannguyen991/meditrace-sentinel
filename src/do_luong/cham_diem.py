# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Bộ chấm]
Làm gì   : Chấm độ giống giữa bản nháp và bản tham chiếu bằng ROUGE và Section F1, tách từ
           theo âm tiết tiếng Việt.
Vào → Ra : hai bản bệnh án (nháp, tham chiếu) → ROUGE-1/2/L, Section F1 và điểm cuối 0,6
           ROUGE + 0,4 F1
Đọc từ   : diem_cuoi() gộp điểm; rouge() và section_f1() là hai nửa của điểm
Mục lục (các hàm/lớp chính):
  rouge()       Tính ROUGE-1, ROUGE-2, ROUGE-L và trung bình
  cac_muc()     Rút tên các mục viết hoa toàn bộ của bệnh án
  section_f1()  Tính Section F1 giữa hai tập tên mục
  diem_cuoi()   Gộp ROUGE và Section F1 thành điểm cuối
Dùng bởi : do_luong/cham_lai_bang_quy_gan, do_luong/chung_chi_thuoc_do, do_luong/do_dac,
           do_luong/khoang_tin_cay
Tên cũ   : cham_diem.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bộ chấm điểm: ROUGE + Section F1, cài đặt ĐỘC LẬP.

VÌ SAO VIẾT LẠI. Bản trước bọc `evaluate.py` của ban tổ chức một cuộc thi mà
tác giả từng dự. Ban tổ chức khuyên không nên dùng tài sản của cuộc thi đó để
tránh câu hỏi về tính chính thống, và lo`i khuyên đó đúng: bộ dữ liệu đi kèm
cũng đã bị dò dấu vết cho thấy rất nhiều khả năng là bản dịch từ tiếng Anh.

Vì thế dự án này cắt hết: dữ liệu, bộ chấm, và cả lời nhắc hệ thống.

Cài đặt hiện tại dùng `rouge-score` — bản tham chiếu của Google, trích dẫn
được — với một BỘ TÁCH TỪ riêng cho tiếng Việt.

**Tách từ theo ÂM TIẾT, không theo từ.** Tiếng Việt viết rời từng âm tiết;
bộ tách từ mặc định của `rouge-score` là cho tiếng Anh và sẽ cắt sai. Quy tắc
ở đây: hạ chữ thường, thay mọi ký tự không phải chữ/số bằng dấu cách, rồi cắt
theo dấu cách. Đây cũng là quy tắc các bộ chấm tiếng Việt thường dùng, nên số
so sánh được với công trình khác.

Công thức điểm tổng hợp `0,6 x ROUGE_avg + 0,4 x SectionF1` là cách chấm phổ
biến cho tóm tắt lâm sàng. **Dự án này chứng minh nó NGƯỢC DẤU với lỗi đổi
chủ thể** (xem `chung_chi_thuoc_do.py`), nên nó được báo cáo như một chỉ số
tham chiếu, không phải làm trọng tài.
"""
import re

from rouge_score import rouge_scorer, tokenizers

TRONG_SO_ROUGE = 0.6
TRONG_SO_SECTION = 0.4


# ═══ class TachAmTiet — Bộ tách từ cho ROUGE: hạ chữ thường, bỏ dấu câu ═══════════════
# Cắt theo khoảng trắng, giữ nguyên dấu tiếng Việt.
class TachAmTiet(tokenizers.Tokenizer):
    """Hạ chữ thường, bỏ dấu câu, cắt theo dấu cách."""

    def tokenize(self, van_ban):
        van = re.sub(r"[^\w\s\d]", " ", str(van_ban or "").lower())
        return [t for t in van.split() if t]


_cham = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"],
                                 tokenizer=TachAmTiet())


# ═══ rouge() — Tính ROUGE-1, ROUGE-2, ROUGE-L và trung bình ═══════════════════════════
# Trả về F-measure của bản dự đoán so với bản tham chiếu.
def rouge(du_doan, tham_chieu):
    """-> {rouge1, rouge2, rougel, avg} theo F-measure."""
    r = _cham.score(tham_chieu or "", du_doan or "")
    r1, r2, rl = (r["rouge1"].fmeasure, r["rouge2"].fmeasure,
                  r["rougeL"].fmeasure)
    return {"rouge1": r1, "rouge2": r2, "rougel": rl,
            "avg": (r1 + r2 + rl) / 3}


# ═══ cac_muc() — Rút tên các mục viết hoa toàn bộ của bệnh án ═════════════════════════
# Dòng là tiêu đề mục khi viết hoa hết, dài hơn 3 ký tự, không chứa chữ số.
def cac_muc(van_ban):
    """Rút tên các mục của bệnh án.

    Quy tắc: một dòng được coi là tiêu đề mục khi nó VIẾT HOA TOÀN BỘ, dài
    hơn 3 ký tự, và không chứa chữ số. Đó là quy tắc thường dùng cho bệnh án
    tiếng Việt, và cũng là quy tắc dễ bị đánh lừa — một mục do hệ thống tự
    đặt ra (ví dụ "CẦN XÁC NHẬN") sẽ bị đếm là một mục dự đoán thừa dù nó
    không phải lỗi nội dung. Điểm này được báo cáo riêng.
    """
    ra = set()
    for dong in (van_ban or "").split("\n"):
        t = dong.strip()
        if len(t) > 3 and not any(c.islower() for c in t) \
                and not any(c.isdigit() for c in t):
            ra.add(t)
    return ra


# ═══ section_f1() — Tính Section F1 giữa hai tập tên mục ══════════════════════════════
# Cả hai không có mục thì được 1.0; không trùng mục nào thì 0.0.
def section_f1(du_doan, tham_chieu):
    p, r = cac_muc(du_doan), cac_muc(tham_chieu)
    if not p and not r:
        return 1.0
    tp = len(p & r)
    if tp == 0:
        return 0.0
    prec, rec = tp / len(p), tp / len(r)
    return 2 * prec * rec / (prec + rec)


# ═══ diem_cuoi() — Gộp ROUGE và Section F1 thành điểm cuối ════════════════════════════
# Trả về từng ROUGE, Section F1 và điểm final theo trọng số cố định.
def diem_cuoi(du_doan, tham_chieu):
    r = rouge(du_doan, tham_chieu)
    sf1 = section_f1(du_doan, tham_chieu)
    return {
        "rouge1": r["rouge1"],
        "rouge2": r["rouge2"],
        "rougel": r["rougel"],
        "rouge_avg": r["avg"],
        "section_f1": sf1,
        "final": TRONG_SO_ROUGE * r["avg"] + TRONG_SO_SECTION * sf1,
    }
