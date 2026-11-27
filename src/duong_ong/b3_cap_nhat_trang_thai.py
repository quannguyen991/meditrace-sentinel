# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 3 – Cập nhật trạng thái]
Làm gì   : Cập nhật trạng thái mệnh đề bằng luật cố định: bản bị đính chính thì đánh dấu
           thay thế (không xoá), hai bên trái nhau thì đánh dấu mâu thuẫn.
Vào → Ra : danh sách mệnh đề có quan hệ (bổ sung, đính chính, diễn biến, mâu thuẫn) → danh
           sách mệnh đề có trạng thái
Đọc từ   : ap_luat() áp luật chuyển trạng thái; con_hieu_luc() / can_xac_nhan() / lich_su()
           lọc theo trạng thái
Mục lục (các hàm/lớp chính):
  ap_luat()                 Áp luật chuyển trạng thái cho cả danh sách mệnh đề
  ap_luat_theo_luot()       Chụp trạng thái sau từng lượt nói
  con_hieu_luc()            Lọc các mệnh đề còn hiệu lực
  can_xac_nhan()            Lọc mệnh đề chưa giải quyết hoặc giả định
  da_bi_thay_the()          Lọc mệnh đề đã bị đính chính thay thế
  lich_su()                 Nhật ký các mệnh đề không còn hiệu lực kèm lý do
  ghi_de_phat_bieu_truoc()  Đối chứng rẻ: mệnh đề sau ghi đè mệnh đề trước
Gọi tới  : duong_ong/b1_cau_truc_menh_de, duong_ong/b2_gom_nguoi_thuc_the
Dùng bởi : do_luong/duong_danh_doi, do_luong/kiem_thu_dot_bien,
           duong_ong/b2_bu_chu_ngu_tinh_luoc, duong_ong/chay_duong_ong,
           duong_ong/chay_nhanh_e
Tên cũ   : cap_nhat.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Luật chuyển trạng thái theo bốn quan hệ.

CHƯƠNG TRÌNH làm việc này, không phải mô hình — có chủ định. Nếu mô hình làm cả
bước này thì khi kết quả sai sẽ không tách được lỗi trích xuất khỏi lỗi cập nhật.

    quan hệ       luật
    ---------     -------------------------------------------------------------
    bổ sung       cả hai còn hiệu lực
    đính chính    bản cũ -> bị thay thế; bản mới -> còn hiệu lực.
                  Bản cũ KHÔNG XÓA, để truy lại được rằng đã có đính chính.
    diễn biến     CẢ HAI còn hiệu lực, gán mốc thời gian khác nhau.
                  Đây là chỗ dễ sai nhất: coi diễn biến là đính chính rồi vứt
                  mất câu đầu. "Hôm qua đau, hôm nay hết đau" — cả hai đều đúng.
    mâu thuẫn     cả hai -> chưa giải quyết, đưa vào mục cần xác nhận
"""
import re
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu

DAU_DONG_THUAN_CHEO = re.compile(
    r"(?i)\b(à ừ|ừ nhỉ|đúng rồi|chính xác rồi|nhớ nhầm|tôi nhầm|mẹ nhầm|em nhầm|vâng đúng)\b"
)


# ─── _co_dong_thuan_cheo() — Kiểm người bị đính chính có đồng thuận ở lượt kế ─────────
# Nếu A xác nhận ngay lượt sau ("ừ nhỉ") thì chấp nhận đính chính của B.
def _co_dong_thuan_cheo(p, truoc, hoi_thoai) -> bool:
    """Nếu người B đính chính người A ở lượt t, và tại lượt t+1 người A xác nhận
    đồng thuận ('A ừ nhỉ', 'Đúng rồi, tôi nhớ nhầm'), thì chấp nhận đính chính."""
    if not hoi_thoai:
        return False
    from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the
    luot_map = {so: (vai, van) for so, vai, van in thuc_the.tach_luot(hoi_thoai)}
    luot_sua = max(getattr(p, "bang_chung", None) or [0])
    for ke_tiep in (luot_sua + 1, luot_sua + 2):
        if ke_tiep in luot_map:
            vai_kt, van_kt = luot_map[ke_tiep]
            if vai_kt == getattr(truoc, "nguoi_noi", None) and DAU_DONG_THUAN_CHEO.search(van_kt):
                return True
    return False


# ═══ ap_luat() — Áp luật chuyển trạng thái cho cả danh sách mệnh đề ═══════════════════
# Trả về danh sách mới, không sửa bản gốc. Đính chính chỉ nhận khi cùng nguồn hoặc có
# đồng thuận, không thì thành mâu thuẫn.
def ap_luat(danh_sach, hoi_thoai=None):
    """Trả về danh sách MỚI với trang_thai đã cập nhật. Không sửa bản gốc."""
    ra = [PhatBieu(**p.to_dict()) for p in danh_sach]
    theo_id = {p.id: p for p in ra}

    for p in ra:
        if p.quan_he is None:
            continue
        truoc = theo_id.get(p.quan_he_voi)
        if truoc is None:
            # Tham chiếu tới phát biểu không tồn tại — không đoán, gán cờ.
            p.trang_thai = "chưa giải quyết"
            continue

        if p.quan_he == "bổ sung":
            pass                                    # cả hai giữ nguyên

        elif p.quan_he == "đính chính":
            # CHỈ chấp nhận đính chính của CHÍNH người đã nói bản trước (tự sửa),
            # HOẶC khi người nói bản trước xác nhận đồng thuận ngay ở lượt kế tiếp.
            # Người khác nói khác đi mà chưa được xác nhận là HAI NGUỒN khác nhau và
            # không có căn cứ chọn bên: hạ về mâu thuẫn, chờ xác nhận.
            if _cung_nguon(p, truoc) or _co_dong_thuan_cheo(p, truoc, hoi_thoai):
                truoc.trang_thai = "bị thay thế"
                p.trang_thai = "còn hiệu lực"
            else:
                p.quan_he = "mâu thuẫn"
                truoc.trang_thai = "chưa giải quyết"
                p.trang_thai = "chưa giải quyết"

        elif p.quan_he == "diễn biến":
            truoc.trang_thai = "còn hiệu lực"
            p.trang_thai = "còn hiệu lực"

        elif p.quan_he == "mâu thuẫn":
            truoc.trang_thai = "chưa giải quyết"
            p.trang_thai = "chưa giải quyết"

    return ra


# ═══ luot_cua() — Lấy lượt nói muộn nhất làm căn cứ của mệnh đề ═══════════════════════
# Cặp hỏi–đáp [3, 4] chỉ đủ nghĩa ở lượt 4.
def luot_cua(p) -> int:
    """Lượt thoại MUỘN NHẤT làm bằng chứng cho phát biểu — tức lượt mà thông tin này
    trở thành biết được. Cặp hỏi–đáp ([3, 4]) chỉ đủ nghĩa ở lượt 4."""
    return max(getattr(p, "bang_chung", None) or [0])


# ═══ ap_luat_theo_luot() — Chụp trạng thái sau từng lượt nói ══════════════════════════
# Trả về (số lượt, danh sách đã áp luật) để biết bản nháp bắt đầu sai từ lượt nào.
def ap_luat_theo_luot(danh_sach):
    """-> [(so_luot, danh sách PhatBieu đã áp luật)] — ảnh chụp trạng thái SAU MỖI LƯỢT.

    VÌ SAO CÓ (16/09/2026). `ap_luat` nhận TOÀN BỘ mệnh đề của ca rồi áp luật một lần,
    nên hệ thống không trả lời được câu "ở lượt thứ mấy thì bản nháp bắt đầu sai".
    Câu đó có nghĩa lâm sàng trực tiếp: một mốc bệnh sử bị đính chính ở lượt 4 thì từ
    lượt 2 đến lượt 3 hồ sơ đang mang số sai.
    Pan, Liu, You (arXiv 2603.17425, 18/03/2026) phát biểu đúng việc này thành một vòng
    cập nhật chạy ở mỗi lượt; họ có chỉ số `T_goal` (lượt đầu tiên mọi ô bắt buộc đã đủ)
    nhưng không có "lượt sai đầu tiên". Xem docs/nguon/cong-trinh-gan-nhat.md.

    KHÔNG SỬA `ap_luat`: hàm này gọi lại `ap_luat` trên từng tiền tố, nên hai đường
    không thể trôi nhau. `tests/test_theo_luot.py` chốt điều đó bằng phép so ảnh chụp
    cuối cùng với `ap_luat` trên cả danh sách.
    """
    moc = sorted({luot_cua(p) for p in danh_sach})
    return [(t, ap_luat([p for p in danh_sach if luot_cua(p) <= t])) for t in moc]


# ═══ con_hieu_luc() — Lọc các mệnh đề còn hiệu lực ════════════════════════════════════
def con_hieu_luc(danh_sach):
    return [p for p in danh_sach if p.trang_thai == "còn hiệu lực"]


# ═══ can_xac_nhan() — Lọc mệnh đề chưa giải quyết hoặc giả định ═══════════════════════
# Không được viết như sự thật trong bản nháp.
def can_xac_nhan(danh_sach):
    """Phát biểu chưa giải quyết + phát biểu giả định: không được viết như sự thật."""
    return [p for p in danh_sach
            if p.trang_thai == "chưa giải quyết" or p.tinh_huong != "thực tế"]


# ═══ da_bi_thay_the() — Lọc mệnh đề đã bị đính chính thay thế ═════════════════════════
# Giữ lại để ghi chú đã có đính chính.
def da_bi_thay_the(danh_sach):
    """Giữ lại để ghi chú 'đã có đính chính' trong bệnh án."""
    return [p for p in danh_sach if p.trang_thai == "bị thay thế"]


# --------------------------------------------------------- đối chứng đơn giản

# ═══ ghi_de_phat_bieu_truoc() — Đối chứng rẻ: mệnh đề sau ghi đè mệnh đề trước ════════
# Cùng chủ thể và nội dung thì bản sau thắng; dùng so với luật đầy đủ.
def ghi_de_phat_bieu_truoc(danh_sach):
    """Đối chứng rẻ: phát biểu sau ghi đè phát biểu trước, trên cùng nội dung.

    Nếu phương pháp không hơn quy tắc này trên các tình huống có đính chính,
    cần xem lại độ khó thật của bài toán.
    """
    ra = [PhatBieu(**p.to_dict()) for p in danh_sach]
    moi_nhat = {}
    for p in ra:
        khoa = (p.chu_the_id, p.noi_dung)
        if khoa in moi_nhat:
            moi_nhat[khoa].trang_thai = "bị thay thế"
        moi_nhat[khoa] = p
        p.trang_thai = "còn hiệu lực"
    return ra


# ─── _cung_nguon() — Kiểm hai mệnh đề có cùng người nói ───────────────────────────────
# Thiếu vai ở một bên thì coi là khác nguồn.
def _cung_nguon(sau, truoc) -> bool:
    """Hai phát biểu có cùng MỘT người nói không (theo vai người nói). Thiếu vai
    ở một bên thì coi là khác nguồn — không đủ căn cứ để cho bản sau thắng."""
    a = getattr(sau, "nguoi_noi", "") or ""
    b = getattr(truoc, "nguoi_noi", "") or ""
    return bool(a) and a == b


# ═══ lich_su() — Nhật ký các mệnh đề không còn hiệu lực kèm lý do ═════════════════════
# Để bác sĩ thấy giá trị cũ đã được đính chính thế nào.
def lich_su(danh_sach):
    """NHẬT KÝ KIỂM CHỨNG: mọi bản KHÔNG còn hiệu lực, kèm vì sao.

    Hồ sơ chính chỉ dùng bản còn hiệu lực; nhật ký giữ phần còn lại để bác sĩ
    thấy "4 ngày đã được người nói đính chính thành 2 ngày" thay vì thấy một con
    số biến mất.
    """
    ra = []
    for p in danh_sach:
        if p.trang_thai == "còn hiệu lực":
            continue
        boi = [q.id for q in danh_sach
               if q.quan_he_voi == p.id and q.quan_he in ("đính chính", "mâu thuẫn")]
        if p.trang_thai == "bị thay thế":
            ly_do = f"đính chính bởi bản #{boi[0]}" if boi else "bị thay thế"
        elif p.quan_he == "mâu thuẫn" or boi:
            doi = p.quan_he_voi if p.quan_he == "mâu thuẫn" else boi[0]
            ly_do = f"mâu thuẫn với bản #{doi}, chưa xác nhận"
        else:
            ly_do = "chưa giải quyết"
        ra.append({"id": p.id, "noi_dung": p.noi_dung,
                   "moc_thoi_gian": p.moc_thoi_gian, "nguoi_noi": p.nguoi_noi,
                   "trang_thai": p.trang_thai, "ly_do": ly_do,
                   "bang_chung": list(p.bang_chung)})
    return ra
