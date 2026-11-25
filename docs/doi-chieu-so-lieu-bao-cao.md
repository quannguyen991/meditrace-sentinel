# Đối chiếu số liệu trong tài liệu báo cáo (25/11/2026)

Mục đích: tìm con số về lọt lỗi, chặn nhầm, bỏ sót trong `docs/tai-lieu/*.md` và `docs/final/*.md` mà không có
nguồn đo, hoặc trái với lần đo `docs/ket-qua/canh-bao-moc-0.md`. **Chưa sửa tài liệu nào** — bảng này để bạn duyệt.

Cách lấy: lọc các dòng có `%` và một trong các từ lọt, sai lệch, bỏ sót, bịa, chặn, ảo giác, precision, recall,
chính xác, F1 (71 dòng). Bỏ qua các dòng nhật ký lệnh và trích dẫn tài liệu ngoài (Palm 2025, Asgari 2025).

## Mức 1 — Trái với số đã đo hoặc không có nguồn: nên sửa trước khi nộp

| Tệp:dòng | Con số trong tài liệu | Nguồn đo | Số đúng thay thế |
|---|---|---|---|
| `docs/tai-lieu/BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md:55` | "Tỷ lệ sinh thông tin sai lệch 0,0% (K1–K7 ngăn chặn hoàn toàn)" | Không tìm thấy | Lỗi nguy hiểm lọt vào thân **45,2%** (C) / 43,3% (D), so với bộ chấm tự động, 4 bộ thử thách phát triển (`canh-bao-moc-0.md`). Không có số nào là 0%. |
| `…BANG_SO_LIEU…:55-59` | Cột GPT-4o 5,2%, Gemini 1.5 Pro 4,8%, Claude 3.5 Sonnet 3,9%, Llama-3-8B 8,4%; chi phí API | Không có tệp kết quả, lệnh gọi hay mã nào gọi các mô hình này trong `src/`, `tools/`, `docs/ket-qua/` | Xoá cả bảng 2.2, hoặc ghi rõ "chưa đo". Bảng so sánh với mô hình thương mại mà không có lần chạy là rủi ro liêm chính lớn nhất trong bộ tài liệu. |
| `…BANG_SO_LIEU…:57` | "Xử lý đính chính: 0,8% lọt lỗi" | Không tìm thấy | Không có phép đo riêng. Lớp cảnh báo có độ phủ `ban_cu` 81,9% cùng loại (`canh-bao-moc-0.md`), tức khoảng 18% lỗi đính chính không có cảnh báo cùng loại. |
| `…BANG_SO_LIEU…:58` | "Kiểm soát liều tối đa Paracetamol 0,0% bỏ sót" | Không tìm thấy | Không có tập đo. Ghi "có luật kiểm tra, chưa đo trên tập độc lập". |
| `…BANG_SO_LIEU…:27-35` | Bảng nhánh A → D: sai chủ thể 12,4% → 2,1%, đính chính 11,5% → 0,8%, giả định 14,8% → 0,4%, SER, F1 51,4 → 76,5, "đo trên 5.000 ca độc lập" | Chỉ có trong `tools/tao_word_bang_thuc_nghiem.py` (số gõ tay vào mã sinh Word) | Số có nguồn: ghi nhầm người 22,0% → 17,9%, F1 66,1 → 70,8 ở bộ đổi chủ thể 80 ca (`docs/final/Báo cáo dự án.md:278`). "5.000 ca độc lập" sai: 5.000 là toàn bộ dữ liệu, gồm cả tập huấn luyện. Nhánh D (bác sĩ xác nhận) chưa từng chạy với bác sĩ thật. |
| `…BANG_SO_LIEU…:42`, `GIAI_THICH_TOAN_DIEN…:206`, `SO_DO_FLOW…:60,114`, `Q_AND_A…:56` | "Chặn nhầm 0,0% (0 / 30.136 dòng)" | Có (`danh_gia_khoa.thong_ke_khoa`) | Số này **có thật nhưng bị hiểu sai**: `src/dan_gian.py:4` ghi nó "chỉ đúng vì đáp án chép gần nguyên văn hội thoại (Coverage 0,95)". Trên đầu ra mô hình thật, chặn thừa là **8,0%** (C) / 6,1% (D). Phải ghi kèm điều kiện, hoặc thay bằng 8,0%. |
| `SO_DO_FLOW…:113`, `Q_AND_A…:56` | "Tỷ lệ bỏ sót dị ứng 0,0%" | Không tìm thấy | Chưa đo riêng. Lớp cảnh báo bỏ sót chung chỉ phủ **12,5%** mệnh đề bị sót, precision 2,8%. Mã nguồn còn lỗi che bỏ sót dị ứng (`kiem_duyet_bhyt_va_bo_sot.py:225`). |
| `…BANG_SO_LIEU…:126` | "Trích dẫn chuỗi con nguyên văn 100% (52.634 / 52.634), triệt tiêu 100% ảo giác trích dẫn" | Có (`docs/ket-qua/bao_cao_kiem_dinh_trich_dan_v2.json`) | Số đúng nhưng là kiểm **dữ liệu huấn luyện do mình sinh**, không phải đầu ra mô hình. Câu "triệt tiêu 100% ảo giác" phải bỏ: lớp cảnh báo vẫn bắt `FABRICATED_QUOTE` 17 lần trên đầu ra mô hình. |

## Mức 2 — Có nguồn nhưng cần ghi kèm điều kiện

| Tệp:dòng | Con số | Ghi chú |
|---|---|---|
| `…BANG_SO_LIEU…:134-138` | Bỏ sót 43,1% → 11,5% (30 ca phát triển, Wilson 95%) | Có nguồn (`tools/do_bo_sot_tren_tap.py`). Thêm: "so với bộ chấm tự động, 30 ca, đáp án v1". |
| `…BANG_SO_LIEU…:162`, `Báo cáo dự án.md:360-365`, `Bao_Cao_Nghien_Cuu…:316-317` | "Độ chính xác 96,7–100%", DDI Clopidogrel + Omeprazole 100%, eGFR sai số 0 | Là phép thử đơn vị với ca tự viết, không phải tỷ lệ trên dữ liệu thật. Nên viết "vượt qua N phép thử đơn vị" thay vì "%". |
| `Q_AND_A…:131` | 45.835 câu duy nhất, lặp giảm từ 76,92% | Số của bản v2 cũ. Bản v2 đã chấp nhận (phương án A) có tỷ lệ lặp **47,37%**; cần cập nhật theo `docs/tien-do-21-11-2026.md`. |

## Mức 3 — Khớp nguồn, giữ nguyên

`docs/final/Báo cáo dự án.md:278, 280, 299, 301, 316, 350, 352, 392` và các dòng tương ứng ở `docs/tai-lieu/Báo cáo dự án.md`:
có số đo cụ thể (22,0% → 17,9%; 15,06% → 12,52%; bỏ sót nghiêm trọng 0,58% → 3,48%), đã nêu cả mặt bất lợi
và câu "các tỷ lệ 100% đo khả năng bắt lỗi có chủ đích". Đây là văn phong nên dùng cho các tệp ở Mức 1.

## Nhận xét

- `docs/final/Báo cáo dự án.md` (bản nộp) khá trung thực. Các con số nói quá tập trung ở `docs/tai-lieu/`
  (bảng số liệu, Q&A ban giám khảo, sơ đồ flow) và các tệp `.docx` sinh từ đó. Nếu các tệp này sẽ đưa cho
  ban giám khảo, cần sửa Mức 1 trước.
- Các tệp `.docx` ở gốc repo và trong `docs/tai-lieu/` được sinh bằng `tools/tao_*.py`, trong đó số được gõ
  thẳng vào mã. Sửa `.md` mà không sửa mã sinh Word thì `.docx` vẫn giữ số cũ.
