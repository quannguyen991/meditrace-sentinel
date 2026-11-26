# Tỷ lệ bỏ sót — adapter v3 so với v1 (26/11/2026)

30 ca đầu `viet_phat_trien`, 304 mệnh đề đáp án, nhánh B, Qwen3-4B 4-bit trên HoaiĐức (RTX 3060, trần VRAM 0,70).
Chấm bằng `tools/do_bo_sot_tren_tap.py` (mệnh đề đáp án không ghép được với bản trích nào, độ giống từ ≥ 0,6).

| Mô hình | Mệnh đề đáp án | Bỏ sót | Tỷ lệ | Khoảng 95% (Wilson) | Ca JSON lỗi |
|---|---:|---:|---:|---|---:|
| v1 (`nen-qwen3-4b-trich-v2`) | 304 | 36 | 11,8% | 8,7%–16,0% | 0 |
| v3 (`nen-qwen3-4b-trich-v3`) | 304 | 43 | 14,1% | 10,7%–18,5% | 0 |

Đọc kết quả:
- v3 không tốt hơn v1; chênh 7 mệnh đề, khoảng tin cậy chồng nhau (và khoảng Wilson coi mệnh đề độc lập nên còn hẹp hơn thực tế).
- 30 ca này thuộc bộ dữ liệu v1; v3 train trên bộ v2 (`trich_train_v2`). Chênh phân phối có thể giải thích một phần.
- Lần đo trước của v1 ra 11,5% (35/304); lần này 11,8% (36/304) — dao động giữa hai lần chạy.

Tệp trích: `data-eval-v1/`, `data-eval-v3/` trên HoaiĐức (`trich_viet_phat_trien_3072_hl.jsonl`).
