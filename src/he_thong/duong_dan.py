# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › Cấu hình]
Làm gì   : Khai báo tập trung các đường dẫn thư mục dữ liệu, mô hình và kết quả để nơi khác
           không ghi cứng.
Vào → Ra : — (đọc biến môi trường MEDITRACE_DATA) → các hằng đường dẫn Path dùng chung
Dùng bởi : do_luong/cham_chu_the, do_luong/cham_he_thong, do_luong/cham_lai_bang_quy_gan,
           do_luong/cham_muc_thach_thuc, do_luong/chung_chi_thuoc_do,
           do_luong/dau_vet_nguon, do_luong/do_bit_nhan, do_luong/do_bo_chan_doan … (tổng 35
           tệp)
Tên cũ   : duong_dan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Một chỗ duy nhất khai báo đường dẫn. Không hardcode ở nơi khác.

Thư mục gốc của dữ liệu kế thừa có dấu cách và ký tự '@' trong tên
("D:/VAIC DE @"), nên mọi nơi dùng Path chứ không nối chuỗi.
Thư mục đó là CHỈ ĐỌC — không ghi gì vào đây.
"""
import os
from pathlib import Path

GOC_DU_AN = Path(__file__).resolve().parents[2]  # src/he_thong/duong_dan.py -> gốc dự án
GOC_VAIC = Path("D:/VAIC DE @")

# Thư mục dữ liệu của cuộc thi cũ. CHỈ CÒN để các script cũ chạy lại được và
# để test đối chiếu lỗi nhắc; KHÔNG còn tệp nào của dự án dùng dữ liệu từ đây.
# Ban tổ chức khuyên không dùng tài sản của họ để tránh câu hỏi về tính chính
# thống, và dò dấu vết cho thấy bộ dữ liệu đó rất nhiều khả năng là bản dịch
# từ tiếng Anh. Dự án chuyển hẳn sang bộ tự sinh `hoi_thoai_viet_3000.jsonl`.
TRAIN_JSONL = GOC_VAIC / "train (2).jsonl"




THU_MUC_KET_QUA = GOC_DU_AN / "docs" / "ket-qua"

# Thư mục dữ liệu đổi được bằng biến môi trường MEDITRACE_DATA.
#
# VÌ SAO CẦN (19/09/2026). Tên tệp kết quả `ra_<nhanh>_<tap>.jsonl` KHÔNG kèm
# tên mô hình. Chạy cùng một nhánh với một mô hình khác — mô hình nền chưa huấn
# luyện, hay một mô hình thương mại làm mốc so — sẽ ĐÈ LÊN kết quả cũ mà không
# ai biết. Đó đúng nhóm lỗi đã xảy ra ngày 19/09: chấm nhầm thế hệ dữ liệu vì
# hai bộ trùng tên tệp.
#
# Cách dùng: MEDITRACE_DATA=.../data-gpt python -m src.duong_ong.chay_duong_ong ...
# Thư mục đó phải có sẵn các tệp bộ dữ liệu; `cham_he_thong --thu-muc` trỏ vào
# cùng chỗ.
THU_MUC_DU_LIEU = Path(os.environ.get("MEDITRACE_DATA") or (GOC_DU_AN / "data"))
THU_MUC_MO_HINH = GOC_DU_AN / "models"

MODEL_NHO = "Qwen/Qwen3-1.7B"
MODEL_GO_LOI = "Qwen/Qwen3-4B"
# Qwen3-4B: mọi lần huấn luyện và chạy thật đều dùng 4B. Qwen3-8B chưa huấn luyện
# kém 4B đã huấn luyện (F1 28,0 so với 66,1 ở bộ đối chủ thể; xem docs/final).
# Đổi từ 8B sang 4B ngày 21/11/2026 để hằng số khớp thực tế.
MODEL_CHINH = "Qwen/Qwen3-4B"

for _d in (THU_MUC_KET_QUA, THU_MUC_DU_LIEU, THU_MUC_MO_HINH):
    _d.mkdir(parents=True, exist_ok=True)
