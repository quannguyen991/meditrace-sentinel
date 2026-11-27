# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Kiểm mô hình gán chủ thể là hiểu thật hay chỉ đoán theo người vừa nói, bằng cách
           bịt nhãn người nói rồi so với bản gốc.
Vào → Ra : ca hội thoại + mệnh đề của bản gốc → bản bịt nhãn và bảng mệnh đề nào đổi chủ thể
Đọc từ   : bit_mau() tạo bản bịt nhãn; doi_chieu() so mệnh đề gốc với bản bịt
Mục lục (các hàm/lớp chính):
  bit()                 Đổi tên người nói thành nhãn trung tính
  bit_mau()             Tạo bản sao ca có lời thoại đã bịt nhãn
  la_nhan_trung_tinh()  Kiểm tra chủ thể chỉ là nhãn chép lại của lượt
  doi_chieu()           So mệnh đề bản gốc với bản bịt nhãn
Dùng bởi : do_luong/do_bit_nhan
Tên cũ   : bit_nhan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Phép thử bịt nhãn người nói — tách BIẾT với ĐOÁN TRÚNG.

CÂU HỎI NÓ TRẢ LỜI. Bake-off cho thấy tỷ lệ gán sai `chu_the` tụt mạnh theo cỡ
mô hình: 1.7B sai 100%, 4B sai 12%, 8B sai 2%. Câu phản biện hiển nhiên là
*"vậy mô hình to hơn là hết lỗi chứ gì, đâu cần cơ chế nào"*.

Đo CHÍNH XÁC không trả lời được câu đó, vì một lý do tinh tế:

    Trong hội thoại khám bệnh, chủ thể CHÍNH LÀ người nói ở phần lớn lượt.
    Một mô hình chỉ làm đúng một việc — "gán triệu chứng cho người vừa nói" —
    vẫn đạt độ chính xác rất cao. Đường tắt ĐÚNG hầu hết thời gian.

Nên độ chính xác cao có thể là BIẾT, cũng có thể là ĐOÁN TRÚNG. Hai thứ đó
khác nhau ở chỗ: cái thứ hai sẽ sai đúng vào những ca nguy hiểm nhất — ca
người nhà kể hộ bệnh nhân, đúng ca mà dự án quan tâm.

CÁCH TÁCH. Chạy trích xuất hai lần trên CÙNG hội thoại:

    ban goc    "Bác sĩ:" / "Người nhà:" / "Bệnh nhân:"
    ban bit    "Người 1:" / "Người 2:" / "Người 3:"

Nội dung không đổi một chữ. Đáp án đúng cũng không đổi — câu "Tôi thì dị ứng
penicillin, còn cháu chưa thấy bị" van cho biet ai di ung, bat ke nhan vai.

    Mô hình HIỂU nội dung      -> bịt nhãn rồi kết quả gần như không đổi
    Mô hình ĐI THEO NHÃN VAI   -> bịt nhãn rồi kết quả đổi nhiều

**Tỷ lệ đổi ý chính là phần đo CHƯA từng được đo.** Nó không phải lỗi — một mô
hình có thể đổi ý mà vẫn đúng — nhưng nó đo mức PHỤ THUỘC vào đường tắt, và đó
là thứ mà tăng mô hình không chắc làm giảm.

Cùng họ ý tưởng với phép thử bịt mắt đã dùng ở chỗ khác: che bỏ phần bài đọc
đi mà hệ thống vẫn trả lời được thì câu hỏi đó không đo đọc hiểu.

GIỚI HẠN, phải ghi vào báo cáo. Bịt nhãn vẫn không xóa được **thứ tự lượt**:
bác sĩ gần như luôn nói trước, nên "Người 1" vẫn đoán được là bác sĩ. Phép thử
đo phần phụ thuộc vào TÊN VAI, không đo phần phụ thuộc vào vị trí.
"""
import re
from typing import Dict, Tuple

# Nhãn trung tính. Dùng chữ "Người" cho mọi vai để không còn gợi ý nào về
# chức năng (bác sĩ / bệnh nhân / người nhà) lọt lại trong chính cái nhãn.
MAU_NHAN = "Người {}"

_DAU_DONG = re.compile(r"^(\s*)([^:\n]{1,20}?)(\s*:\s*)", re.MULTILINE)


# ═══ bit() — Đổi tên người nói thành nhãn trung tính ══════════════════════════════════
# Trả về hội thoại đã bịt và bảng tra tên gốc sang nhãn. Cùng một người luôn nhận cùng
# một nhãn.
def bit(hoi_thoai: str) -> Tuple[str, Dict[str, str]]:
    """Đổi tên vai ở đầu mỗi lượt thành nhãn trung tính.

    Trả về (hội thoại đã bịt, bảng tra {tên gốc: nhãn mới}). Cùng một vai luôn
    được một nhãn — nếu không thì chính phép bịt sẽ xóa mất thông tin "hai lượt
    này cùng một người", và đó là thông tin thật chứ không phải đường tắt.
    """
    bang: Dict[str, str] = {}

    def thay(m):
        khoang, ten, dau = m.group(1), m.group(2).strip(), m.group(3)
        if ten not in bang:
            bang[ten] = MAU_NHAN.format(len(bang) + 1)
        return f"{khoang}{bang[ten]}{dau}"

    return _DAU_DONG.sub(thay, hoi_thoai), bang


# ═══ bit_mau() — Tạo bản sao ca có lời thoại đã bịt nhãn ══════════════════════════════
# Chỉ đổi phần input; đáp án output giữ nguyên vì không phụ thuộc tên vai.
def bit_mau(mau: dict) -> dict:
    """Bản sao của một mẫu với `input` đã bịt nhãn. `output` GIỮ NGUYÊN —
    đáp án đúng không phụ thuộc vào tên vai."""
    moi = dict(mau)
    moi["input"], moi["bang_nhan"] = bit(mau["input"])
    return moi


# ------------------------------------------------------------- đối chiếu

# ─── _chuan_chu_the() — Chuẩn hoá chủ thể về chữ thường, gộp khoảng trắng ─────────────
def _chuan_chu_the(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


# ═══ la_nhan_trung_tinh() — Kiểm tra chủ thể chỉ là nhãn chép lại của lượt ════════════
# Chủ thể dạng "Người N" nghĩa là mô hình đi theo nhãn vai chứ không rút từ nội dung.
def la_nhan_trung_tinh(chu_the: str) -> bool:
    """`chu_the` có phải chỉ là cái nhãn chép lại không.

    Mô hình trả về "Người 2" nghĩa là nó không rút được chủ thể từ nội dung —
    nó chỉ chép lại nhãn của lượt. Đó là bằng chứng TRỰC TIẾP của việc đi theo
    đường tắt, mạnh hơn cả tỷ lệ đổi ý.
    """
    return bool(re.fullmatch(r"người\s*\d+", _chuan_chu_the(chu_the)))


# ═══ doi_chieu() — So mệnh đề bản gốc với bản bịt nhãn ════════════════════════════════
# Ghép theo nội dung chứ không theo thứ tự; đếm số khớp, số đổi ý, số chủ thể chỉ là
# nhãn.
def doi_chieu(goc: list, bit_nhan: list) -> dict:
    """So hai danh sách phát biểu thô (dict từ mô hình) của CÙNG một hội thoại.

    Ghép theo `noi_dung` — không ghép theo thứ tự, vì hai lần chạy có thể trích
    ra số phát biểu khác nhau, và ghép theo thứ tự sẽ báo "đổi ý" ở những chỗ
    thật ra chỉ là lệch một ô.
    """
    theo_nd = {}
    for p in bit_nhan:
        theo_nd.setdefault(_chuan_chu_the(p.get("noi_dung")), []).append(p)

    khop = doi_y = trung_tinh = 0
    vi_du = []
    for p in goc:
        nd = _chuan_chu_the(p.get("noi_dung"))
        ung_vien = theo_nd.get(nd)
        if not ung_vien:
            continue
        q = ung_vien.pop(0)
        khop += 1
        a, b = _chuan_chu_the(p.get("chu_the")), _chuan_chu_the(q.get("chu_the"))
        if la_nhan_trung_tinh(b):
            trung_tinh += 1
        if a != b:
            doi_y += 1
            if len(vi_du) < 5:
                vi_du.append({"noi_dung": p.get("noi_dung"),
                              "chu_the_goc": p.get("chu_the"),
                              "chu_the_bit": q.get("chu_the")})
    return {
        "so_phat_bieu_goc": len(goc),
        "so_phat_bieu_bit": len(bit_nhan),
        "so_khop_noi_dung": khop,
        "so_doi_y": doi_y,
        "so_chu_the_la_nhan": trung_tinh,
        "vi_du": vi_du,
    }
