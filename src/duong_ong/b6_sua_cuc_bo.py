# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 6 – Hỏi lại và sửa]
Làm gì   : Kiểm từng câu của bản nháp với bảng mệnh đề và chỉ chuyển chỗ hoặc sửa câu sai,
           không sinh lại cả bản.
Vào → Ra : văn bản bản nháp + danh sách mệnh đề → KetQuaSua (bản nháp đã sửa, các câu bị
           chuyển xuống mục cần xác nhận)
Đọc từ   : sua() lặp sửa đến khi ổn định; kiem_mot_cau() kiểm một câu theo bốn phép kiểm
Mục lục (các hàm/lớp chính):
  sua()            Sửa cục bộ bản nháp, lặp đến khi ổn định
  kiem_mot_cau()   Kiểm một câu trong bản nháp với bảng mệnh đề
  tach_muc()       Tách bản nháp thành các mục và câu
  class KetQuaSua  Kết quả vòng sửa cục bộ
  _mot_vong()      Chạy một lượt rà soát toàn bản nháp
Gọi tới  : duong_ong/b1_cau_truc_menh_de, duong_ong/b5_viet_ban_nhap
Dùng bởi : duong_ong/chay_duong_ong, duong_ong/chay_nhanh_e
Tên cũ   : sua_cuc_bo.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Kiểm chứng từng câu của bản nháp, sửa CỤC BỘ chứ không sinh lại cả bản.

Bốn phép kiểm, mỗi phép chặn một lỗi thật:

    khong_co_nguon        câu không đối chiếu được với phát biểu nào
    dung_ban_bi_thay_the  câu dùng lại thông tin đã bị đính chính
    them_muc_chac_chan    hội thoại nói "chưa ghi nhận", bản nháp nói chắc
    sai_nguoi             thông tin của người khác nằm trong mục của bệnh nhân

Ví dụ trong kế hoạch: hội thoại "Bệnh nhân chưa nhớ rõ tên thuốc đã dùng",
bản nháp "Bệnh nhân đã dùng paracetamol" -> "paracetamol" không có nguồn,
nên câu bị chuyển xuống mục cần xác nhận chứ KHÔNG bị xóa.

BA RỦI RO CỦA CHÍNH CƠ CHẾ NÀY (Task 17 bước 6), phải đo chứ không được bỏ qua:

  1. làm hỏng câu vốn đúng — nên mặc định của mỗi phép sửa là CHUYỂN CHỖ,
     không phải viết lại. Chuyển chỗ thì thông tin còn nguyên.
  2. bỏ sót chỗ liên quan — sau mỗi vòng sửa phải chạy lại hết, vì sửa một
     câu có thể làm một câu khác thành không có nguồn.
  3. độ trễ tăng thêm — giới hạn `max_vong`. Hết vòng mà vẫn không xác minh
     được thì chuyển thành nội dung cần bác sĩ kiểm, không sửa vô hạn.

GIỚI HẠN ĐÃ BIẾT: trên bản nháp do `sinh_benh_an` sinh ra bằng luật, cơ chế
này gần như không tìm thấy gì — vì khâu sinh đã áp dụng đúng những luật đó.
Nó chỉ có việc trên bản nháp do MÔ HÌNH viết (nhánh A, A+, hoặc bản nháp
ngoài). Điều đó phải ghi vào báo cáo, không được trình bày như một cơ chế
làm nên chênh lệch giữa C và D.
"""
import re
from dataclasses import dataclass, field
from typing import List

from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
from src.duong_ong.b1_cau_truc_menh_de import la_vai_nhan_vien

MUC_PHU = sinh_benh_an.MUC_PHU
MUC_NGUOI_KHAC = sinh_benh_an.MUC_NGUOI_KHAC

HEDGE = {"chưa ghi nhận": "chưa ghi nhận", "nghi ngờ": "nghi ngờ"}


# ═══ class KetQuaSua — Kết quả vòng sửa cục bộ ════════════════════════════════════════
# Gồm văn bản mới, số vòng, các chỗ đã sửa và các chỗ còn ngờ.
@dataclass
class KetQuaSua:
    van_ban: str
    so_vong: int = 0
    da_sua: List[dict] = field(default_factory=list)
    con_ngo: List[str] = field(default_factory=list)


# ─── _co() — Kiểm cụm và văn bản có nói cùng một thứ ──────────────────────────────────
# Đối chiếu hai chiều để kế hoạch điều trị dài không bị coi là không có nguồn.
def _co(cum, van_ban):
    """Cụm và văn bản có nói cùng một thứ không — đòi CẢ HAI CHIỀU.

    LỖI ĐÃ XẢY RA, đo được 11/09/2026: 195/198 lần sửa của nhánh D là
    `khong_co_nguon`, và phần lớn là KẾ HOẠCH ĐIỀU TRỊ do bác sĩ nói. Ví dụ:

        phát biểu đã trích  "Siêu âm hệ tiết niệu. Uống nhiều nước, giảm đau
                             khi cần"
        câu trong bản nháp  "Siêu âm hệ tiết niệu"

    Khâu trích sinh MỘT phát biểu chứa HAI câu. `sinh_benh_an` tách chúng thành
    hai câu riêng. Còn phép kiểm này đi tìm CẢ `noi_dung` bên trong MỘT câu —
    nên không bao giờ khớp, và câu bị kết luận là không có nguồn.

    HAI KHÂU KHÔNG ĐỒNG Ý VỀ ĐƠN VỊ VĂN BẢN. Đó là họ lỗi, không phải một chi
    tiết: giống trường hợp `menh_de[0]` và trường hợp đổi id thay vì đổi nội
    dung, mỗi lần đều là hai chỗ cùng dùng một dữ liệu với hai giả định khác
    nhau về hình của nó.

    Giá đo được: bao phủ tầng bác sĩ 95,00% -> 82,36%, điểm gộp -0,115.
    """
    cum = re.sub(r"\s+", " ", str(cum or "")).strip()
    van = re.sub(r"\s+", " ", str(van_ban or "")).strip()
    if not cum or not van:
        return False

    def trong(nho, to):
        return re.search(rf"(?<![\wÀ-ỹ]){re.escape(nho)}(?![\wÀ-ỹ])",
                         to, re.I) is not None

    # Chiều thuận: phát biểu nằm trong câu.
    if trong(cum, van):
        return True
    # Chiều ngược: câu là MỘT PHẦN của một phát biểu nhiều câu. Đòi hỏi câu đủ
    # dài để không khớp bừa — một câu ba chữ nằm trong mọi thứ.
    return len(van.split()) >= 3 and trong(van, cum)


# ═══ tach_muc() — Tách bản nháp thành các mục và câu ══════════════════════════════════
# Trả về danh sách (tên mục hoặc None, các câu) giữ nguyên thứ tự.
def tach_muc(van_ban):
    """-> [(ten_muc_hoac_None, [cau, ...])] giữ nguyên thứ tự."""
    ra = []
    for khoi in (van_ban or "").split("\n\n"):
        t = khoi.strip()
        if not t:
            continue
        if t == t.upper() and len(t) > 3 and not any(c.isdigit() for c in t):
            ra.append([t, []])
        elif ra:
            ra[-1][1].extend(c.strip() for c in t.split(".") if c.strip())
        else:
            ra.append([None, [c.strip() for c in t.split(".") if c.strip()]])
    return [(m, cs) for m, cs in ra]


# ─── _ghep() — Ghép lại các mục thành văn bản ─────────────────────────────────────────
def _ghep(muc_list):
    khoi = []
    for muc, cau in muc_list:
        if not cau:
            continue
        khoi.append(muc if muc else "")
        khoi.append(". ".join(cau) + ".")
    return "\n\n".join(k for k in khoi if k != "" or True).strip()


# ═══ kiem_mot_cau() — Kiểm một câu trong bản nháp với bảng mệnh đề ════════════════════
# Trả về (tên lỗi, mệnh đề liên quan), ví dụ không có nguồn hoặc dùng bản đã bị thay
# thế.
def kiem_mot_cau(cau, muc, phat_bieu, id_benh_nhan=0):
    """-> (ten_loi, phat_bieu_lien_quan) hoặc (None, ...)."""
    lien_quan = [p for p in phat_bieu if _co(p.get("noi_dung"), cau)]
    if not lien_quan:
        return "khong_co_nguon", []

    con_hieu_luc = [p for p in lien_quan
                    if p.get("trang_thai", "còn hiệu lực") == "còn hiệu lực"]
    if not con_hieu_luc:
        return "dung_ban_bi_thay_the", lien_quan

    for p in con_hieu_luc:
        muc_do = p.get("do_chac_chan", "chắc chắn")
        if muc_do in HEDGE and not _co(HEDGE[muc_do], cau):
            return "them_muc_chac_chan", [p]

    if muc not in (MUC_PHU, MUC_NGUOI_KHAC):
        # CHẶN HAI LẦN. `phat_bieu.tu_json` đã quy vai nhân viên y tế về bệnh
        # nhân, nhưng phép kiểm này cũng phải tự chặn: bản nháp ngoài và bản
        # ghi cũ không đi qua đường đó.
        #
        # Không chặn thì câu bác sĩ nói bị kết luận là "thông tin của người
        # khác" và bị đổi sang mục TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI — đã xảy ra 104
        # lần trên tập phát triển, làm tầng bác sĩ tụt 98,6% -> 52,8%.
        khac = [p for p in con_hieu_luc
                if p.get("chu_the_id") != id_benh_nhan
                and not la_vai_nhan_vien(p.get("ten_chu_the"))]
        if khac and not any(p.get("chu_the_id") == id_benh_nhan
                            or la_vai_nhan_vien(p.get("ten_chu_the"))
                            for p in con_hieu_luc):
            return "sai_nguoi", khac

    return None, con_hieu_luc


# ─── _mot_vong() — Chạy một lượt rà soát toàn bản nháp ────────────────────────────────
# Trả về (các mục mới, danh sách chỗ đã sửa).
def _mot_vong(muc_list, phat_bieu, id_benh_nhan, ten_chu_the):
    """Một lượt rà soát. -> (muc_list_moi, danh_sach_sua)."""
    moi = {m: list(c) for m, c in muc_list}
    thu_tu = [m for m, _ in muc_list]
    sua = []

    for muc, cau_list in muc_list:
        # Câu ĐÃ nằm ở mục phụ thì không rà soát lại. Vòng sửa chạy lại sau mỗi
        # lần sửa (có ý, xem rủi ro 2 ở đầu tệp), nhưng một câu đã bị chuyển
        # xuống mục phụ thì đã mang sẵn chú thích
        #
        #     "<cau> — không đối chiếu được với hội thoại"
        #
        # và chính chú thích đó làm nó không còn khớp với phát biểu nào nữa. Nên
        # vòng sau gán cờ nó lần nữa và nói thêm một chú thích nữa. Đã thấy bản
        # ghi "Siêu âm hệ tiết niệu — không đối chiếu được với hội thoại" bị gán
        # cờ lần thứ hai trong cùng một ca.
        if muc == MUC_PHU:
            continue
        for cau in cau_list:
            loi, lq = kiem_mot_cau(cau, muc, phat_bieu, id_benh_nhan)
            if loi is None:
                continue
            moi[muc].remove(cau)
            if loi == "dung_ban_bi_thay_the":
                # Bản mới đã nằm ở chỗ khác trong bệnh án. Bỏ hẳn, không
                # chuyển xuống mục phụ — chuyển xuống là nói lại một thông
                # tin đã bị đính chính.
                sua.append({"cau": cau, "loi": loi, "thanh": None, "muc": muc})
                continue
            if loi == "them_muc_chac_chan":
                hedge = HEDGE[lq[0].get("do_chac_chan")]
                cau_moi = f"{hedge} {cau}"
                moi[muc].append(cau_moi)
                sua.append({"cau": cau, "loi": loi, "thanh": cau_moi, "muc": muc})
                continue
            if loi == "sai_nguoi":
                ten = ten_chu_the.get(lq[0].get("chu_the_id"))
                # Câu từ `sinh_benh_an` đã có sẵn tiền tố "<ten>: ". Dán thêm
                # lần nữa thành "bác sĩ: bác sĩ: ..." — đã xảy ra thật trên
                # tập phát triển.
                da_co_tien_to = re.match(r"^[^:]{1,20}:\s", cau) is not None
                cau_moi = f"{ten}: {cau}" if (ten and not da_co_tien_to) else cau
                dich = MUC_NGUOI_KHAC
                moi.setdefault(dich, [])
                if dich not in thu_tu:
                    thu_tu.append(dich)
                moi[dich].append(cau_moi)
                sua.append({"cau": cau, "loi": loi, "thanh": cau_moi, "muc": dich})
                continue
            # khong_co_nguon -> chuyển xuống mục phụ, KHÔNG xóa
            moi.setdefault(MUC_PHU, [])
            if MUC_PHU not in thu_tu:
                thu_tu.append(MUC_PHU)
            moi[MUC_PHU].append(f"{cau} — không đối chiếu được với hội thoại")
            sua.append({"cau": cau, "loi": loi, "thanh": None, "muc": MUC_PHU})

    # giữ thứ tự mục chuẩn, MUC_PHU luôn cuối
    thu_tu_chuan = [m for m in sinh_benh_an.THU_TU_MUC if m in moi]
    con_lai = [m for m in thu_tu if m in moi and m not in thu_tu_chuan]
    return [(m, moi[m]) for m in thu_tu_chuan + con_lai], sua


# ═══ sua() — Sửa cục bộ bản nháp, lặp đến khi ổn định ═════════════════════════════════
# Dừng khi không còn chỗ sửa hoặc hết max_vong (mặc định 3).
def sua(van_ban, phat_bieu, id_benh_nhan=0, ten_chu_the=None, max_vong=3):
    """Sửa cục bộ, lặp tới khi ổn định hoặc hết `max_vong`."""
    ten_chu_the = ten_chu_the or {}
    ps = [p.to_dict() if hasattr(p, "to_dict") else dict(p) for p in phat_bieu]
    muc_list = tach_muc(van_ban)
    ket = KetQuaSua(van_ban=van_ban)

    for _ in range(max_vong):
        ket.so_vong += 1
        muc_list, sua_vong = _mot_vong(muc_list, ps, id_benh_nhan, ten_chu_the)
        ket.da_sua.extend(sua_vong)
        if not sua_vong:
            break

    ket.van_ban = _ghep(muc_list)
    # Hết vòng mà vẫn còn chỗ không xác minh được -> để bác sĩ kiểm, không
    # sửa tiếp. Sửa vô hạn là chỗ dự án tự bịa thêm thông tin.
    for muc, cau_list in muc_list:
        if muc == MUC_PHU:
            ket.con_ngo.extend(cau_list)
    return ket
