# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 5 – Xếp chỗ]
Làm gì   : Chấm điểm rủi ro mệnh đề bị gán nhầm người và đẩy mệnh đề điểm cao sang mục chưa
           giải quyết theo ngưỡng.
Vào → Ra : danh sách mệnh đề + ngữ cảnh hội thoại + ngưỡng → điểm rủi ro 0–1 mỗi mệnh đề;
           danh sách đã sàng
Đọc từ   : diem_rui_ro() chấm một mệnh đề; sang_loc() đẩy mệnh đề vượt ngưỡng sang chưa giải
           quyết
Mục lục (các hàm/lớp chính):
  diem_rui_ro()          Chấm điểm rủi ro quy gán từ 0 đến 1
  dac_trung()            Tính bốn dấu hiệu rủi ro quy gán của mệnh đề
  sang_loc()             Đẩy mệnh đề điểm cao sang chưa giải quyết
  sang_loc_ngau_nhien()  Đối chứng: đẩy ngẫu nhiên đúng tỉ lệ mệnh đề
  thong_ke()             Thống kê số lần bật từng dấu hiệu và điểm
  class NguCanh          Thông tin chung của cả hội thoại
Gọi tới  : do_luong/thuoc_do_quy_gan, duong_ong/b1_cau_truc_menh_de
Dùng bởi : do_luong/duong_danh_doi
Tên cũ   : rui_ro_quy_gan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chấm điểm RỦI RO QUY GÁN cho từng phát biểu, và sàng lọc theo ngưỡng.

VÌ SAO PHẦN NÀY TỒN TẠI.

Hai cơ chế lỗi của dự án đều không khai hoá được trên dữ liệu thật: quan hệ
chỉ ra 2 cặp trên 282 phát biểu, và liên kết thực thể chỉ đổi tiền tố cách gọi.
Nhưng có MỘT hiện tượng thì có thật và đo được:

    0,6 mệnh đề gán nhầm người trên mỗi hồ sơ  (đo bằng `thuoc_do_quy_gan`)

Và hầu hết chúng đến từ cùng một đường tắt, đã thấy ở bake-off: mô hình gán
triệu chứng cho NGƯỜI VỪA NÓI. Đường tắt đó đúng ở phần lớn lượt — nên độ
chính xác cao không chứng minh được gì — và nó sai đúng vào nhóm ca nguy hiểm
nhất: người nhà kể hộ bệnh nhân.

ĐỔI CÁCH ĐẶT VẤN ĐỀ. Thay vì cố sửa cho mô hình gán đúng hẳn — việc mà ba
nhánh đã thử và không ăn thua — hãy **đánh dấu những phát biểu có nguy cơ gán
sai rồi đẩy chúng xuống mục CẦN XÁC NHẬN**.

Cái được: bác sĩ vẫn phải ký bản cuối, nên thứ họ thực sự cần không phải là
một bản hoàn hảo mà là một bản **kèm danh sách cho phải soát**. Và vì ngưỡng
là một nút vặn được, nó cho ra cả một ĐƯỜNG ĐÁNH ĐỔI thay vì một điểm: gán cờ
nhiều thì ít lỗi còn lại trong thân bài nhưng bỏ sót nhiều hơn, và ngược lại.

Đó là thứ mà kế hoạch đã yêu cầu ở Cửa 4 — *"chưa có căn cứ chọn ngưỡng thì
trình bày đường đánh đổi lỗi–bỏ sót thay vì kết luận một chiều"* — nhưng chưa
bao giờ dùng.

BỐN DẤU HIỆU, và vì sao là bốn dấu hiệu này.

  chu_the_suy_tu_nguoi_noi   Trong các lượt bằng chứng KHÔNG có từ nào gọi tên
                             chủ thể. Tức chủ thể không đọc được từ nội dung,
                             nó chỉ có thể đến từ nhãn vai của người nói. Đây
                             là dấu hiệu bắt ĐÚNG đường tắt, và là dấu hiệu
                             mạnh nhất trong bốn.
  nhieu_nguoi_ke             Hội thoại có từ hai người nói không phải bác sĩ.
                             Một người kể thì không thể lẫn; hai người thì có.
  bang_chung_mot_luot        Chỉ một lượt làm bằng chứng. Cặp hỏi–đáp cần hai
                             lượt mới đủ nghĩa, nên một lượt thường là đã mất
                             về ngữ cảnh.
  khong_chac_chan            `do_chac_chan` khac "chắc chắn".

TRỌNG SỐ ĐỀU NHAU, và đó là một GIỚI HẠN phải ghi vào báo cáo. Chưa có dữ liệu
gán nhãn tay để hiệu chuẩn trọng số; đặt trọng số bằng tay rồi báo "dấu hiệu
này quan trọng hơn" là bịa một con số không đo được. Khi Task 9 và Task 13 có
nhãn tay rồi thì hiệu chuẩn lại — và lúc đó phải đo xem hiệu chuẩn có thật sự
tốt hơn đều nhau không, chứ không mặc định là có.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.duong_ong.b1_cau_truc_menh_de import PhatBieu
from src.do_luong.thuoc_do_quy_gan import TU_BENH_NHAN, TU_NGUOI_NHA

import re

DAU_HIEU = ("chủ thể suy từ người nói", "nhiều người kể",
            "bằng chứng một lượt", "không chắc chắn")

VAI_KHONG_PHAI_NGUOI_KE = ("bác sĩ", "điều dưỡng", "bs", "y tá")


# ═══ class NguCanh — Thông tin chung của cả hội thoại ═════════════════════════════════
# Gồm các lượt nói và số người kể, dùng chung cho mọi mệnh đề.
@dataclass(frozen=True)
class NguCanh:
    """Thông tin của CẢ hội thoại, dùng chung cho mọi phát biểu trong đó."""
    luot_thoai: Dict[int, str]
    so_nguoi_ke: int

    @classmethod
    def tu_hoi_thoai(cls, cac_luot):
        """`cac_luot`: [(so, vai, noi_dung)] — đầu ra của `thuc_the.tach_luot`."""
        luot = {so: nd for so, _, nd in cac_luot}
        nguoi_ke = {
            (vai or "").strip().lower() for _, vai, _ in cac_luot
            if (vai or "").strip().lower() not in VAI_KHONG_PHAI_NGUOI_KE
        }
        return cls(luot_thoai=luot, so_nguoi_ke=len(nguoi_ke))


# ─── _co_tu() — Kiểm văn bản có chứa một cụm theo ranh giới từ ────────────────────────
def _co_tu(van_ban: str, cum_list) -> bool:
    thap = " " + (van_ban or "").lower() + " "
    return any(re.search(r"(?<![\w])" + re.escape(c) + r"(?![\w])", thap)
               for c in cum_list)


# ═══ dac_trung() — Tính bốn dấu hiệu rủi ro quy gán của mệnh đề ═══════════════════════
# Chủ thể suy từ người nói, nhiều người kể, căn cứ một lượt, độ chắc chắn thấp.
def dac_trung(p: PhatBieu, ngu_canh: NguCanh, id_benh_nhan: int = 0) -> Dict[str, bool]:
    van_ban = " ".join(ngu_canh.luot_thoai.get(l, "") for l in (p.bang_chung or []))
    cum = TU_BENH_NHAN if p.chu_the_id == id_benh_nhan else TU_NGUOI_NHA
    return {
        "chủ thể suy từ người nói": not _co_tu(van_ban, cum),
        "nhiều người kể": ngu_canh.so_nguoi_ke >= 2,
        "bằng chứng một lượt": len(p.bang_chung or []) <= 1,
        "không chắc chắn": p.do_chac_chan != "chắc chắn",
    }


# ═══ diem_rui_ro() — Chấm điểm rủi ro quy gán từ 0 đến 1 ══════════════════════════════
# Bằng tỉ lệ dấu hiệu đang bật, trọng số đều nhau.
def diem_rui_ro(p: PhatBieu, ngu_canh: NguCanh, id_benh_nhan: int = 0) -> float:
    """0,0 = không có dấu hiệu nào; 1,0 = đủ cả bốn. Trọng số đều nhau."""
    d = dac_trung(p, ngu_canh, id_benh_nhan)
    return sum(1 for v in d.values() if v) / len(DAU_HIEU)


# ═══ sang_loc() — Đẩy mệnh đề điểm cao sang chưa giải quyết ═══════════════════════════
# Trả về bản sao, không xoá gì; ngưỡng lớn hơn 1 nghĩa là không đánh dấu gì.
def sang_loc(danh_sach: List[PhatBieu], nguong: float, ngu_canh: NguCanh,
             id_benh_nhan: int = 0) -> List[PhatBieu]:
    """Trả về bản SAO; phát biểu có điểm >= `nguong` bị đánh `chưa giải quyết`.

    Không xoá phát biểu nào. `sinh_benh_an._muc_cho` đã có sẵn luật đưa mỗi bản
    ghi `chưa giải quyết` xuống mục CẦN XÁC NHẬN — nên sàng lọc chỉ là đánh dấu,
    không phải một đường sinh thứ hai. Bớt được một chỗ có thể lệch nhau.

    `nguong > 1` nghĩa là không đánh dấu gì cả — đây là mốc đối chứng, phải có
    trong đường đánh đổi chứ không được bỏ.
    """
    ra = []
    for p in danh_sach:
        q = PhatBieu(**p.to_dict())
        if diem_rui_ro(p, ngu_canh, id_benh_nhan) >= nguong:
            q.trang_thai = "chưa giải quyết"
        ra.append(q)
    return ra


# ═══ sang_loc_ngau_nhien() — Đối chứng: đẩy ngẫu nhiên đúng tỉ lệ mệnh đề ═════════════
# Để chứng tỏ sàng lọc theo điểm bắt lỗi tốt hơn chọn bừa cùng tỉ lệ.
def sang_loc_ngau_nhien(danh_sach: List[PhatBieu], ty_le: float,
                        seed: int) -> List[PhatBieu]:
    """Đối chứng: đẩy xuống ĐÚNG `ty_le` phát biểu, chọn NGẪU NHIÊN.

    Bắt buộc phải có. Đẩy 60% phát biểu xuống mục cần xác nhận thì lỗi gán nhầm
    còn lại tất nhiên giảm — kể cả khi chọn bừa. Đường đánh đổi về từ điểm rủi
    ro chỉ có ý nghĩa nếu nó nằm DƯỚI đường ngẫu nhiên ở cùng tỷ lệ đẩy xuống:
    tức cùng một cổng sàng lọc thì bắt được nhiều lỗi hơn.

    Không có vế này thì bảng số chỉ chứng minh được một điều ai cũng biết —
    viết ít đi thì sai ít đi.
    """
    import random

    rng = random.Random(seed)
    n = len(danh_sach)
    so_chon = int(round(ty_le * n))
    chon = set(rng.sample(range(n), so_chon)) if so_chon else set()

    ra = []
    for i, p in enumerate(danh_sach):
        q = PhatBieu(**p.to_dict())
        if i in chon:
            q.trang_thai = "chưa giải quyết"
        ra.append(q)
    return ra


# ═══ thong_ke() — Thống kê số lần bật từng dấu hiệu và điểm ═══════════════════════════
# Số liệu cho báo cáo.
def thong_ke(danh_sach: List[PhatBieu], ngu_canh: NguCanh,
             id_benh_nhan: int = 0) -> dict:
    dem = {t: 0 for t in DAU_HIEU}
    diem = []
    for p in danh_sach:
        for ten, co in dac_trung(p, ngu_canh, id_benh_nhan).items():
            dem[ten] += int(co)
        diem.append(diem_rui_ro(p, ngu_canh, id_benh_nhan))
    return {
        "so_phat_bieu": len(danh_sach),
        "dem_dau_hieu": dem,
        "diem_trung_binh": round(sum(diem) / len(diem), 4) if diem else 0.0,
    }
