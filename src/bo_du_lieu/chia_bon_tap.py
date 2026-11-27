# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Nạp và chia]
Làm gì   : Chia bộ hội thoại thành bốn tập tách rời (huấn luyện, phát triển, kiểm tra cuối,
           kiểm tra chung) để không lộ đề.
Vào → Ra : danh sách mẫu hội thoại + hạt giống → dict 4 tập train / phat_trien /
           kiem_tra_cuoi / kiem_tra_chung; main() ghi tệp
Đọc từ   : chia() chọn mẫu có người nhà cho hai tập chuyên biệt rồi chia phần còn lại;
           main() đọc bộ và ghi bốn tệp
Mục lục (các hàm/lớp chính):
  chia()  Chia bộ dữ liệu thành bốn tập tách rời
  main()  Đọc bộ huấn luyện, chia bốn tập và ghi tệp
Gọi tới  : bo_du_lieu/nap_du_lieu, he_thong/duong_dan
Tên cũ   : tach_tap.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chia bộ dữ liệu thành BỐN tập tách rời.

Vì sao bốn tập chứ không phải một:

  train           huấn luyện mô hình
  phat_trien      ĐƯỢC xem lỗi, sửa phương pháp, chọn ngưỡng
  kiem_tra_cuoi   KHÔNG được mở trước Cửa 5 — mọi con số trong báo cáo cuối lấy từ đây
  kiem_tra_chung  lấy ngẫu nhiên, để báo cáo chất lượng CHUNG

Bản kế hoạch đầu tiên dùng CÙNG MỘT tập cho cả việc thăm dò lỗi lẫn đánh giá cuối.
Như vậy tập đó đã thành tập phát triển và không còn đánh giá được nữa.

`phat_trien` và `kiem_tra_cuoi` đều chọn từ nhóm có lượt "Người nhà", nên chúng là
tập kiểm tra CHUYÊN BIỆT cho tình huống nhiều người nói, KHÔNG đại diện cho toàn bộ
hội thoại. Đó là lý do có thêm `kiem_tra_chung`.

    python -m src.bo_du_lieu.chia_bon_tap
"""
import io
import random
import sys

from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.he_thong import duong_dan as duong_dan

SEED = 42
SO_PHAT_TRIEN = 35
SO_KIEM_TRA_CUOI = 40
SO_KIEM_TRA_CHUNG = 60


# ═══ chia() — Chia bộ dữ liệu thành bốn tập tách rời ══════════════════════════════════
# Gồm train, phát triển, kiểm tra cuối, kiểm tra chung; hai tập giữ lại chọn từ mẫu có
# người nhà.
def chia(mau_list, seed=SEED):
    rnd = random.Random(seed)

    co_nn = du_lieu.loc_mau_co_nguoi_nha(mau_list)
    rnd.shuffle(co_nn)

    phat_trien = co_nn[:SO_PHAT_TRIEN]
    kiem_tra_cuoi = co_nn[SO_PHAT_TRIEN:SO_PHAT_TRIEN + SO_KIEM_TRA_CUOI]
    # co_nn[SO_PHAT_TRIEN + SO_KIEM_TRA_CUOI:] vẫn ở lại huấn luyện — cố ý.
    # Bỏ hết mẫu người nhà khỏi train thì mô hình không học được tình huống
    # nhiều người nói, và baseline yếu giả theo chiều ngược lại.

    id_giu = {m["id"] for m in phat_trien + kiem_tra_cuoi}
    con_lai = [m for m in mau_list if m["id"] not in id_giu]
    rnd.shuffle(con_lai)

    kiem_tra_chung = con_lai[:SO_KIEM_TRA_CHUNG]
    train = con_lai[SO_KIEM_TRA_CHUNG:]

    return {
        "train": train,
        "phat_trien": phat_trien,
        "kiem_tra_cuoi": kiem_tra_cuoi,
        "kiem_tra_chung": kiem_tra_chung,
    }


# ═══ main() — Đọc bộ huấn luyện, chia bốn tập và ghi tệp ══════════════════════════════
# In số mẫu và số mẫu có người nhà của mỗi tập.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    mau = du_lieu.nap_mau(duong_dan.TRAIN_JSONL)
    tap = chia(mau)
    for ten, ds in tap.items():
        dp = duong_dan.THU_MUC_DU_LIEU / f"{ten}.jsonl"
        du_lieu.ghi_mau(dp, ds)
        so_nn = len(du_lieu.loc_mau_co_nguoi_nha(ds))
        print(f"{ten:16} {len(ds):5d} mau  ({so_nn} co nguoi nha)")
    print(f"{'TONG':16} {sum(len(d) for d in tap.values()):5d}")


if __name__ == "__main__":
    main()
