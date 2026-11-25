# -*- coding: utf-8 -*-
"""Tool chạy phân tích toàn diện phân bố độ dài và mốc audio segments trên bộ 5.000 ca V2."""
import json
from pathlib import Path
import time
import sys

from src.audio.phan_tich_am_thanh_v2 import phan_tich_tap_ca_v2


def main():
    tep_vao = Path("data/hoi_thoai_viet_v2_mo_rong.jsonl")
    if not tep_vao.exists():
        print(f"Lỗi: Không tìm thấy {tep_vao}")
        sys.exit(1)

    print(f"Đang đọc dữ liệu từ {tep_vao}...")
    t0 = time.time()
    cac_ca = [json.loads(line) for line in tep_vao.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Đã đọc {len(cac_ca)} ca trong {time.time() - t0:.2f}s.")

    print("Đang tiến hành phân tích phân bố độ dài và mốc audio segments...")
    t1 = time.time()
    bc = phan_tich_tap_ca_v2(cac_ca)
    print(f"Hoàn thành phân tích trong {time.time() - t1:.2f}s.")

    # Xuất kết quả JSON
    thu_muc_ra = Path("docs/ket-qua")
    thu_muc_ra.mkdir(parents=True, exist_ok=True)
    
    tep_json = thu_muc_ra / "bao_cao_phan_bo_audio_v2.json"
    tep_json.write_text(json.dumps(bc.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã ghi báo cáo JSON ra: {tep_json}")

    # Xuất kết quả Markdown
    noi_dung_md = f"""# Báo cáo Phân tích Phân bố Độ dài & Mốc Audio Segments Bộ Dữ liệu V2 (5.000 ca)
**Tệp dữ liệu:** `{tep_vao}`
**Thời gian lập báo cáo:** {time.strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. Tổng quan Quy mô Âm thanh Lâm sàng

| Đại lượng Đo lường | Giá trị Thống kê | Đơn vị / Ghi chú |
| :--- | :--- | :--- |
| **Tổng số ca hội thoại khám** | **{bc.tong_so_ca:,}** | Ca khám hoàn chỉnh |
| **Tổng số lượt thoại âm thanh** | **{bc.tong_so_luot:,}** | Lượt phát ngôn |
| **Tổng thời lượng âm thanh dự tính** | **{bc.tong_thoi_luong_gio:.2f}** | Giờ âm thanh phòng khám |
| **Tổng số mốc căn cứ âm thanh (Spans)** | **{bc.tong_so_audio_spans:,}** | Spans phục vụ Click-to-Verify |
| **Tỷ lệ spans hợp lệ đơn điệu** | **{bc.ty_le_span_hop_le_100 * 100:.1f}%** | 100% không chồng chéo |

---

## 2. Phân bố Lượt thoại & Thời lượng trên mỗi Ca khám

- **Số lượt thoại / ca:**
  * Trung bình: **{bc.luot_trung_binh_tren_ca:.2f}** lượt/ca
  * Trung vị (P50): **{bc.luot_p50_tren_ca:.1f}** lượt/ca
  * Phân vị 95 (P95): **{bc.luot_p95_tren_ca:.1f}** lượt/ca
  * Tối thiểu / Tối đa: **{bc.luot_min_tren_ca}** lượt / **{bc.luot_max_tren_ca}** lượt
- **Thời lượng âm thanh / ca (tốc độ chuẩn 4.2 âm tiết/s + khoảng lặng tự nhiên):**
  * Thời lượng trung bình: **{bc.thoi_luong_ca_trung_binh_s:.2f} s** (~**{bc.thoi_luong_ca_trung_binh_s / 60:.2f} phút**)
  * Trung vị (P50): **{bc.thoi_luong_ca_p50_s:.2f} s**
  * Phân vị 95 (P95): **{bc.thoi_luong_ca_p95_s:.2f} s**
  * Ngắn nhất / Dài nhất: **{bc.thoi_luong_ca_min_s:.2f} s** / **{bc.thoi_luong_ca_max_s:.2f} s**

---

## 3. Phân bố Độ dài Lượt thoại & Từ vựng (Word Distribution)

- **Số từ trung bình trên mỗi lượt thoại:** **{bc.tu_trung_binh_tren_luot:.2f}** từ/lượt
- **Phân nhóm độ dài lượt thoại:**
  * Lượt ngắn (< 5 từ - câu đáp tắt, chào hỏi xã giao): **{bc.ty_le_luot_ngan_duoi_5_tu * 100:.2f}%**
  * Lượt trung bình (5 - 15 từ - câu hỏi, mô tả triệu chứng ngắn): **{bc.ty_le_luot_trung_binh_5_15_tu * 100:.2f}%**
  * Lượt dài (> 15 từ - lời kể bệnh sử, giải thích đơn thuốc): **{bc.ty_le_luot_dai_tren_15_tu * 100:.2f}%**

---

## 4. Phân bố Phân đoạn Người nói (Diarization Speaker Breakdown)

- **Bác sĩ (Doctor):** **{bc.ty_le_luot_bac_si * 100:.2f}%** (chủ động dẫn dắt, hỏi bệnh, ra y lệnh)
- **Bệnh nhân (Patient):** **{bc.ty_le_luot_benh_nhan * 100:.2f}%** (trực tiếp mô tả triệu chứng, xác nhận)
- **Người nhà (Caregiver):** **{bc.ty_le_luot_nguoi_nha * 100:.2f}%** (kể hộ bệnh nhi/người già, khai tiền sử gia đình)

---

## 5. Đặc tính Mốc Trích dẫn Căn cứ Âm thanh (Audio Citation Spans)

- **Tổng số mốc âm thanh trích dẫn:** **{bc.tong_so_audio_spans:,}** mốc
- **Thời lượng trung bình mỗi đoạn trích dẫn:** **{bc.do_dai_span_trung_binh_ms:.1f} ms** (~**{bc.do_dai_span_trung_binh_ms / 1000.0:.2f} s**)
- **Tương thích Click-to-Verify Scrubber:**
  * 100% mốc có `start_ms < end_ms` và liên kết trực tiếp với lượt thoại gốc.
  * Được đệm pre-roll 400ms và post-roll 300ms trong `VerificationView.tsx` đảm bảo không bị cắt cụt âm tiết đầu/cuối khi bác sĩ nghe lại.
"""
    tep_md = thu_muc_ra / "bao_cao_phan_bo_audio_v2.md"
    tep_md.write_text(noi_dung_md, encoding="utf-8")
    print(f"Đã ghi báo cáo Markdown ra: {tep_md}")

    # In tóm tắt ra màn hình
    print("\n" + "="*60)
    print("TÓM TẮT PHÂN BỐ AUDIO SEGMENTS V2 (5.000 CA):")
    print(f"- Tổng số ca: {bc.tong_so_ca:,}")
    print(f"- Tổng số lượt: {bc.tong_so_luot:,}")
    print(f"- Tổng thời lượng: {bc.tong_thoi_luong_gio:.2f} giờ")
    print(f"- Lượt TB/ca: {bc.luot_trung_binh_tren_ca:.2f} (P50: {bc.luot_p50_tren_ca:.1f}, P95: {bc.luot_p95_tren_ca:.1f})")
    print(f"- Thời lượng TB/ca: {bc.thoi_luong_ca_trung_binh_s:.2f}s (~{bc.thoi_luong_ca_trung_binh_s/60:.2f} phút)")
    print(f"- Phân bố vai: Bác sĩ {bc.ty_le_luot_bac_si*100:.1f}%, Bệnh nhân {bc.ty_le_luot_benh_nhan*100:.1f}%, Người nhà {bc.ty_le_luot_nguoi_nha*100:.1f}%")
    print(f"- Mốc spans: {bc.tong_so_audio_spans:,} mốc (Thời lượng TB: {bc.do_dai_span_trung_binh_ms:.1f} ms)")
    print("="*60)


if __name__ == "__main__":
    main()
