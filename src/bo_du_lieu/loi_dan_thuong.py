# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ sinh]
Làm gì   : Đổi thuật ngữ y khoa trong lời bệnh nhân sang lời dân thường, nhưng đáp án vẫn
           giữ thuật ngữ lâm sàng.
Vào → Ra : câu + rng + tỷ lệ → câu đã đổi sang lời dân thường; phu_duoc() cho biết văn bản
           được phủ đến đâu
Đọc từ   : doi_sang_dan_thuong() đổi một câu theo tỷ lệ; phu_duoc() kiểm mức phủ của phép
           đổi
Mục lục (các hàm/lớp chính):
  doi_sang_dan_thuong()  Đổi thuật ngữ trong câu sang lời dân thường
  phu_duoc()             Liệt kê thuật ngữ của bảng có mặt trong văn bản
  _bi_chan()             Kiểm tra từ sau cụm có nằm trong bảng chặn không
  _mau()                 Tạo mẫu tìm nguyên cụm, không phân biệt hoa thường
Dùng bởi : bo_du_lieu/sinh_hoi_thoai_viet
Tên cũ   : loi_dan_thuong.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Hội thoại nói bằng LỜI DÂN THƯỜNG, đáp án giữ THUẬT NGỮ LÂM SÀNG.

VÌ SAO CẦN — đo được ngày 10/09/2026, và đây là chỗ hỏng nặng nhất của bộ dữ
liệu. Tỷ lệ từ nội dung của mệnh đề đáp án xuất hiện NGUYÊN VĂN trong hội thoại:

    bộ 3.000   trung bình 99,7%   mệnh đề phụ 100%: 99,1%
    bộ 5.000   trung bình 99,6%   mệnh đề phụ 100%: 98,5%

Nghĩa là nhiệm vụ mà bộ dữ liệu đặt ra chỉ là: TÌM ĐÚNG ĐOẠN VÀ XẾP ĐÚNG MỤC.
Không chuẩn hoá, không suy luận, không diễn đạt lại. Một đối chứng regex cắt
đoạn rồi dán vào ĐÃ HƠN cả đường ống đầy đủ trên mọi tầng (Task 42).

Và nó giải thích ba thứ trước đó tưởng rối nhau:

    eval_loss dừng ở 10^-4            phép chiếu gần như tiền định
    đối chứng regex hơn đường ống     sao chép là chiến lược tối ưu
    đường ống không cho thấy lợi ích  không có gì để đường ống đóng góp

Chỗ này LỚN HƠN nhận định cũ "dữ liệu quá đều". Dữ liệu KHÔNG đều về bề mặt —
3.000/3.000 khung câu khác nhau. Nó đều ở chỗ **phép chiếu từ hội thoại sang
bản nháp gần như là phép đồng nhất**.

Tệp này phá phép đồng nhất đó: người bệnh nói "con bé cứ nôn trong suốt", bệnh
án ghi "nôn nhiều lần".

QUAN HỆ VỚI `phuong_ngu`. Cùng cơ chế, khác mối quan tâm:

    phuong_ngu      biến thể VÙNG      "sốt"  -> "nóng hâm hấp"
    loi_dan_thuong  biến thể NGỮ VỰC   "nôn nhiều lần" -> "cứ nôn trong suốt"

Tách hai tệp vì hai bảng phải đo riêng: một ca có thể có phương ngữ mà không có
lời dân thường, và ngược lại. Gộp vào một bảng thì không còn biết cái nào đang
làm mô hình sai.

HAI RÀNG BUỘC, giống `phuong_ngu`, và cả hai đều có kiểm thử:

  1. CHỈ thay trong lời bệnh nhân và người nhà. Bác sĩ được đào tạo nói thuật
     ngữ; đổi lời bác sĩ sang lời dân thường là làm mất một dấu hiệu thật.
  2. ĐÁP ÁN GIỮ THUẬT NGỮ CHUẨN. Hội thoại viết "cứ nôn trong suốt", đáp án vẫn
     ghi "nôn nhiều lần".

Ràng buộc hai CHÍNH LÀ phép thử. Nếu đáp án cũng đổi sang lời dân thường thì
không còn gì để đo — mô hình chỉ việc chép lại nguyên văn, và ta trở lại đúng
chỗ đang đứng.
"""
import re

# (thuật ngữ lâm sàng, các cách nói dân thường). Chiều ĐỔI LÀ: bảng này dùng để
# đổi ĐÁP ÁN -> HỘI THOẠI, ngược với `phuong_ngu`.
#
# BẢNG NÀY LẤY TỪ NGỮ LIỆU, KHÔNG TỰ PHỎNG ĐOÁN. Ban đầu tôi viết 18 cụm theo
# trí nhớ ("nôn nhiều lần", "tiêu chảy", "khó thở"...) rồi đo độ phủ: **9/18 cụm
# KHÔNG XUẤT HIỆN LẦN NÀO** trong 681 ca. Bộ sinh dùng chữ khác hẳn, và một bảng
# không khớp ngữ liệu thì không thay được gì — nó không báo lỗi, nó chỉ không
# chạy.
#
# Bảng dưới đây dùng các cụm có tần số cao nhất trong `dap_an`, và chỉ giữ cặp
# mà một người Việt không học y THẬT SỰ nói như thế. Không bịa cụm cho đủ dài
# bảng: một cặp sai nghĩa làm bản nháp tham chiếu sai theo, và lỗi đó không có
# cách nào phát hiện từ bảng số.
#
# Độ phủ sau khi lấy từ ngữ liệu: 630/681 ca (92,5%), cả 20/20 cụm đều bắt.
#
# LỖI THỨ HAI, sửa 11/09/2026: 20 cụm đầu tiên được chọn theo tần số đo trên
# TẬP PHÁT TRIỂN. Hai hậu quả, và hậu quả thứ hai nặng:
#
#   1. Bảng phủ 8 khuôn của tập dev rất tốt và 45 khuôn của tập train kém. Đo
#      được trên thế hệ 3: tỷ lệ mệnh đề sao chép nguyên văn là 83,3% ở dev
#      nhưng 93,8% ở train. Lệch 10 điểm, và lệch THEO HƯỚNG làm tập đo KHÓ HƠN
#      tập huấn luyện — vì một lý do không liên quan gì đến khả năng khái quát.
#
#   2. Chọn từ vựng theo tần số của tập ĐO là một dạng nhìn vào dữ liệu đánh
#      giá. Nó nhẹ, nhưng nó cùng hướng với mọi cách làm hỏng phép đo khác.
#
# Bảng giờ mở rộng theo từ vựng của TẬP TRAIN. Phép thử
# `test_do_phu_KHONG_lech_giua_train_va_dev` canh độ lệch đó.
CHENH_PHU_TOI_DA = 0.04
# Cụm ĐÃ BỎ ngày 11/09/2026 vì KHÔNG thuộc từ vựng của tập train — kiểm bằng
# `test_MOI_khoa_thuoc_TU_VUNG_TRAIN`. Cả tám đều nằm trong 20 cụm ĐẦU TIÊN, tức
# những cụm đã được chọn theo tần số của TẬP PHÁT TRIỂN (xem "LỖI THỨ HAI" ở
# trên). Khi bộ khuôn lên 100 và chia lại 13/12, khuôn mang chúng rơi vào tập
# phát triển, nên chúng thành từ vựng CHỈ có ở tập đo: giữ lại là để tập phát
# triển được "làm khó" bằng chính từ vựng của nó. Số bên phải: số mệnh đề tập
# phát triển mang cụm đó, đếm lúc bỏ.
#
# GIÁ PHẢI TRẢ, và phải báo cáo: bỏ tám cụm này thì tập phát triển DỄ CHÉP HƠN
# tập train — xem `test_do_phu_KHONG_lech_giua_train_va_dev`.
BO_VI_KHONG_THUOC_TRAIN = {
    "đau thượng vị": 139,
    "đau quặn vùng thắt lưng": 122,
    "đi ngoài khó": 106,
    "rụng tóc": 28,
    "đau lan xuống bẹn": 24,
    "bụng chướng": 19,
    "ngứa tăng về đêm": 17,
    "gãi trầy da": 17,
    # Bỏ 12/09/2026. Khuôn "viêm da cơ địa" mang cụm này nằm ở tập PHÁT TRIỂN:
    # 77 mệnh đề ở đó, và ĐÚNG MỘT ở tập train — cái một đó không phải từ vựng
    # train thật, nó là một lần ghép chuỗi tình cờ. Một mẫu duy nhất đủ để
    # `_khoa_trong` đọc ra "có trong train", nên ràng buộc chỉ lộ ra khi đếm lại.
    "ngứa nhiều": 77,
}

DAN_THUONG = {
    # --- cụm kỹ thuật thật: người dân gần như không bao giờ nói thế
    "đau bụng quanh rốn": ["đau quanh chỗ rốn", "đau ở giữa bụng"],
    "da xanh": ["da tái đi", "trông nhợt nhạt", "mặt xanh xao"],
    "buồn nôn": ["nôn nao", "lợm giọng", "muốn nôn"],
    # --- cụm vừa: có cách nói dân thường rõ ràng
    "chán ăn": ["không chịu ăn gì", "bỏ bữa suốt", "ăn uống kém đi"],
    "mệt mỏi": ["người rã rời", "không còn sức gì", "lừ đừ cả ngày"],
    "quấy khóc": ["khóc suốt đêm", "cứ quấy không yên"],
    "ngủ không yên": ["ngủ chập chờn", "đêm cứ trở mình"],
    "sụt cân": ["gầy đi nhiều", "xuống mấy cân"],
    "mất ngủ": ["không ngủ được", "trằn trọc cả đêm"],
    "khó tập trung": ["không tập trung được", "đầu cứ lơ mơ"],
    "chảy mũi": ["chảy nước mũi", "mũi thò lò"],
    # --- mở rộng 11/09/2026 theo từ vựng của TẬP TRAIN, xem chú thích dưới
    "đau vùng thượng vị": ["đau vùng trên rốn", "đau chỗ dưới ức"],
    "ho có đờm": ["ho ra đờm", "ho đặc tiếng"],
    "đi ngoài phân lỏng": ["đi ngoài toàn nước", "đi lỏng suốt"],
    # "khó vào giấc" đã bị bỏ: nó là CÁCH NÓI DÂN THƯỜNG tôi chọn, nhưng nó cũng
    # là một thuật ngữ CÓ THẬT trong đáp án của bộ sinh. Trùng như vậy thì phá
    # bất biến 2 — đáp án chứa một cụm của bảng này, và phép thử hết phân biệt
    # được đáp án với hội thoại. Test `test_BAT_BIEN_2_dap_an_giu_THUAT_NGU_CHUAN`
    # bắt được.
    "khó ngủ": ["nằm mãi không ngủ được", "trở mình cả đêm không ngủ"],
    "hồi hộp": ["tim đập loạn lên", "trong người bồn chồn"],
    "vã mồ hôi": ["mồ hôi ra đầm đìa", "ướt hết áo"],
    "sưng đau khớp ngón chân cái": ["ngón chân cái sưng đau",
                                    "ngón chân cái đau không đi được"],
    "sưng góc hàm": ["mang tai sưng lên", "sưng hai bên hàm"],
    "nổi mẩn": ["nổi lên từng đám", "mẩn lên khắp người"],
    "đỏ bờ mi": ["mí mắt đỏ", "viền mắt đỏ lên"],
    "ngứa mắt": ["mắt ngứa cứ muốn cọ", "ngứa trong mắt"],
    "khát nước nhiều": ["uống nước suốt không đỡ", "khát liên tục"],
    "chậm mọc răng": ["lâu rồi chưa thấy mọc răng", "răng mọc muộn"],
    "đỏ da": ["da đỏ lên", "đỏ ửng cả vùng"],
    "đau nửa đầu": ["đau một bên đầu", "nhức nửa bên đầu"],
    "đau họng": ["rát cổ", "cổ đau khi ăn"],
    # --- mở rộng LẦN HAI, 11/09/2026, khi bộ khuôn lên 100. 40 khuôn mới làm
    # tỷ lệ mệnh đề sao chép nguyên văn của train tăng 88,3% -> 90,6% (riêng
    # khuôn mới 94,5%), và tỷ lệ ca train có lời dân thường tụt 65,7% -> 51,7%
    # — vì bảng không có một từ nào của chúng.
    #
    # 29 cụm dưới đây LẤY TỪ TẬP TRAIN, mỗi cụm >= 96 lần trong lời bệnh nhân /
    # người nhà. Đã kiểm trên cả 5.000 ca: không cách nói nào trùng nội dung đáp
    # án, không cách nói nào chứa một khoá khác, và khoá không phải nội dung
    # người nhà. "nghe kém" bị LOẠI vì là một nội dung trong bể tiền sử gia đình:
    # bể đó chia theo tập, nên đổi nó chỉ làm lệch tầng 4 giữa các tập.
    "đau đầu": ["nhức đầu", "nặng đầu"],
    "đau tai": ["nhức trong tai", "tai nhức buốt"],
    "ù tai": ["tai kêu o o", "trong tai cứ o o"],
    "cộm mắt": ["mắt như có cát", "mắt vướng như có bụi"],
    "đau gáy": ["nhức sau gáy", "mỏi nhừ sau cổ"],
    "nôn nhiều": ["nôn thốc nôn tháo", "nôn hết cả ra"],
    "ngứa về đêm": ["tối đến là ngứa", "cứ tối là ngứa"],
    "sưng đau khớp bàn tay": ["mấy đốt ngón tay sưng nhức",
                              "khớp tay sưng tấy lên"],
    "đau lưng lan xuống chân": ["đau từ thắt lưng chạy xuống chân",
                                "buốt từ lưng xuống tận chân"],
    "đi ngoài ra máu": ["đi cầu có máu", "đi vệ sinh thấy máu"],
    "nổi mụn nước": ["mọc mấy nốt phỏng", "nổi nốt phỏng nước"],
    "ngứa âm hộ": ["ngứa vùng kín", "ngứa ở chỗ kín"],
    "khát nước": ["lúc nào cũng thèm uống", "uống bao nhiêu cũng không đã khát"],
    "đau cổ chân": ["nhức ở mắt cá chân", "nhức quanh cổ chân"],
    "đỏ da vùng quấn tã": ["chỗ đóng bỉm đỏ lên", "mông đỏ ửng chỗ quấn bỉm"],
    "tiểu đêm": ["đêm dậy đi vệ sinh mấy lần", "đêm phải dậy đi giải"],
    "đau ngực khi gắng sức": ["làm nặng là tức ngực",
                              "leo cầu thang là thấy nặng ngực"],
    "hắt hơi": ["hắt xì", "hay hắt xì"],
    "nôn trớ sau bú": ["bú xong là trớ ra", "ăn sữa xong lại ọc ra"],
    "kinh không đều": ["tháng có tháng không", "đến tháng lúc sớm lúc muộn"],
    "đau vùng cổ trước": ["đau phía trước cổ", "đau quanh chỗ yết hầu"],
    "sưng mi mắt": ["mí mắt sưng húp", "mắt sưng mọng lên"],
    "nhìn xa mờ": ["nhìn xa không rõ", "nhìn xa bị nhòe"],
    "chảy nước mắt": ["mắt cứ ứa nước", "mắt lúc nào cũng ướt"],
    "tiểu dầm ban đêm": ["đêm vẫn đái dầm", "ngủ vẫn tè dầm"],
    "nổi mụn ở mặt": ["mặt lên mụn", "mặt mọc mụn"],
    "đau rát một bên": ["nóng rát một bên", "rát như bỏng một bên"],
    "tê ngón tay": ["tê bì đầu ngón", "đầu ngón cứ rần rần"],
    "đau lưng": ["nhức lưng", "ê ẩm cả lưng"],
}

# Cụm KHÔNG đổi, kèm lý do. Ghi ra thay vì xoá im lặng, để người đọc sau biết
# là đã cân nhắc chứ không phải bỏ sót.
DA_BO = {
    "sốt": "`phuong_ngu` da phu cum nay (\"nong ham hap\"); doi o ca hai tep "
           "thi khong con biet tang nao lam mo hinh sai",
    "dị ứng thuốc": "nguoi dan cung noi \"di ung thuoc\" — khong co cach noi khac",
    "sốt phát ban": "ten CHAN DOAN, do bac si noi, khong phai loi benh nhan",
    "thiếu máu thiếu sắt": "ten chan doan, nhu tren",
    "co giật": "cach noi dan thuong (\"giat minh\", \"lam kinh\") lech nghia y hoc",
    "vàng da": "\"da vang\" va \"vang da\" khac nhau ve cu phap, doi de sinh cau sai",
}


# RANH GIỚI TỪ KHÔNG PHẢI RANH GIỚI TỪ GHÉP — cùng họ lỗi đã mắc ở `phuong_ngu`.
#
# `(?![\wÀ-ỹ])` chặn được "da xanh" nằm trong "da xanhxao", nhưng KHÔNG chặn
# được "da xanh" nằm trong "da xanh xao": giữa chúng là dấu cách nên lookahead
# cho qua. Kết quả: "trong da xanh xao" -> "trong da tái đi xao", không phải
# tiếng Việt.
#
# Test `test_khong_khop_tu_nam_TRONG_tu_khac` bắt được.
#
# Bảng dưới đây lấy từ NGỮ LIỆU: quét từ đứng sau mỗi cụm trên 681 ca. Phần lớn
# là mốc thời gian ("hai", "khoảng", "từ") và "nữa" — đều an toàn. Chỉ hai chỗ
# thật sự rủi ro.
CHAN_SAU = {
    # ("bụng chướng": {"nhẹ"} đã bỏ 11/09/2026 cùng khoá của nó — xem
    # BO_VI_KHONG_THUOC_TRAIN. Để lại thì là một dòng chặn cho khoá không tồn tại.)
    "da xanh": {"xao"},         # "da xanh xao" là một từ ghép
    # Thêm 11/09/2026, cùng cách: quét từ đứng sau mỗi khoá mới trên tập train.
    # Cả ba là chỗ một khoá NGẮN nằm ở đầu một cụm DÀI hơn cũng là khoá (hoặc
    # cũng là một triệu chứng): đổi khoá ngắn sẽ cắt đôi cụm dài.
    "đau lưng": {"lan"},        # 58 lần: "đau lưng lan xuống chân" là khoá riêng
    "khát nước": {"nhiều"},     # "khát nước nhiều" là khoá riêng
    "nổi mụn nước": {"nhỏ"},    # 24 lần: "nổi mụn nước nhỏ" là một triệu chứng
}


# ─── _mau() — Tạo mẫu tìm nguyên cụm, không phân biệt hoa thường ──────────────────────
# Không khớp khi cụm dính chữ khác ở hai đầu.
def _mau(cum):
    return re.compile(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])", re.I)


# ─── _bi_chan() — Kiểm tra từ sau cụm có nằm trong bảng chặn không ────────────────────
# Dùng để tránh đổi nhầm khi cụm là phần của từ ghép.
def _bi_chan(cum, cau, ket):
    """Từ ngay sau `cum` có nằm trong bảng chặn không."""
    sau = cau[ket:].lstrip()
    tu_sau = re.match(r"[\wÀ-ỹ]+", sau)
    if not tu_sau:
        return False
    return tu_sau.group(0).lower() in CHAN_SAU.get(cum, ())


# ═══ doi_sang_dan_thuong() — Đổi thuật ngữ trong câu sang lời dân thường ══════════════
# Mỗi cụm tìm thấy được đổi với xác suất 0,85; cụm dài được xét trước.
def doi_sang_dan_thuong(cau, rng, ty_le=0.85):
    """-> (cau_moi, [(thuat_ngu, cach_noi)]).

    `ty_le`: xác suất đổi MỖI cụm tìm thấy. Đặt 0,85 chứ không 1,0: hội thoại
    thật trộn cả hai ngữ vực — người bệnh có học vấn cũng nói "buồn nôn" — và
    đổi hết 100% thì phép thử thành "dịch từ điển một chiều".

    Tăng từ 0,55 lên 0,85 sau khi đo: ở 0,55 thì tỷ lệ mệnh đề sao chép nguyên
    văn chỉ tụt từ 99,1% xuống 93,8%, chưa đủ.

    Đổi cụm DÀI trước: "sốt cao" phải được xét trước "sốt", nếu không thì đổi
    "sốt" xong sẽ còn lại "nóng hâm hấp cao" — đúng họ lỗi phá từ ghép đã mắc ở
    `phuong_ngu`.
    """
    da_doi = []
    for thuat_ngu in sorted(DAN_THUONG, key=len, reverse=True):
        m = _mau(thuat_ngu).search(cau)
        if not m or _bi_chan(thuat_ngu, cau, m.end()):
            continue
        if rng.random() >= ty_le:
            continue
        cach_noi = rng.choice(DAN_THUONG[thuat_ngu])
        cau = cau[:m.start()] + cach_noi + cau[m.end():]
        da_doi.append((thuat_ngu, cach_noi))
    return cau, da_doi


# ═══ phu_duoc() — Liệt kê thuật ngữ của bảng có mặt trong văn bản ═════════════════════
# Dùng đo độ phủ của bảng trên ngữ liệu.
def phu_duoc(van_ban):
    """-> các thuật ngữ trong bảng CÓ mặt trong `van_ban`.

    Dùng để đo độ phủ của bảng: bảng có 18 cụm, nhưng nếu ngữ liệu chỉ dùng 3
    trong số đó thì tầng này gần như không chạy. Phải đo chứ không được giả
    định.
    """
    return [t for t in DAN_THUONG if _mau(t).search(van_ban or "")]
