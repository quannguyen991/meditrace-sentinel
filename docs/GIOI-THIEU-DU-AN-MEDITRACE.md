# MediTrace Sentinel: giới thiệu dự án

> Tài liệu này mô tả đúng những gì có trong mã nguồn tại ngày 17/11/2026. Mỗi khẳng định đều có tệp kèm theo để kiểm chứng. Chỗ nào chưa chứng minh được bằng mã hoặc bằng số đo, tài liệu ghi rõ là chưa.

## 1. Một câu

MediTrace Sentinel nghe cuộc khám bệnh bằng tiếng Việt và dựng **bản nháp hồ sơ khám bệnh**. Mỗi dòng trong bản nháp đều chỉ về đúng câu nói làm căn cứ, để bác sĩ kiểm tra trước khi dùng. Phần mềm không chẩn đoán, không kê đơn, và bản nháp không phải bệnh án chính thức.

## 2. Bài toán

Bác sĩ khám 50–80 ca mỗi ngày, mỗi ca vài phút, và phải gõ hồ sơ trên máy. Mô hình ngôn ngữ lớn có thể viết ra một đoạn ghi chép trôi chảy, nhưng câu trôi chảy chưa chắc đúng. Các lỗi nguy hiểm nhất khó nhìn thấy:

| Lời nói trong khám | Bản ghi sai có thể viết |
|---|---|
| "**Bố em** bị hen từ nhỏ." | "Bệnh nhân có tiền sử hen." (sai người) |
| "Ho một tuần… à không, **mười ngày** rồi." | "Ho một tuần" (giữ lại thông tin đã bị đính chính) |
| "**Nếu** mai còn sốt thì chụp phim." | "Đã chụp phim." (biến lời dặn thành việc đã làm) |
| Bác sĩ hỏi dị ứng thuốc, chưa ai trả lời | "Không dị ứng thuốc." (ghi điều chưa ai nói) |

Tiếng Việt làm các lỗi này dễ xảy ra hơn: câu thường bỏ chủ ngữ ("Sốt hai hôm rồi"), và từ "con", "cháu", "em" vừa là cách tự xưng vừa là cách gọi người khác.

## 3. Ý tưởng cốt lõi

Hệ thống không để mô hình viết bệnh án từ đầu đến cuối. Phân công như sau:

- **Mô hình học máy chỉ làm hai việc:** chuyển âm thanh thành lời (PhoWhisper), và bóc tách lời thoại thành các mẩu tin nguyên tử, mỗi mẩu có câu trích nguyên văn (Qwen3-4B với QLoRA).
- **Mọi bước sau đó là luật xác định:** gom người nói, xử lý đính chính, khóa bằng chứng, phân loại rủi ro, và ghép mục bệnh án. Không bước nào dùng LLM để viết văn.
- **Mọi mệnh đề đều truy được về câu gốc.** Bác sĩ bấm một dòng, hệ thống hiện đường nối đến lượt thoại gốc.

Bất biến chính: không có bằng chứng thì không có mệnh đề; AI không tự chuyển sang trạng thái đã duyệt; thông tin nghi ngờ đi vào mục "Cần bác sĩ xác nhận", không bị xóa âm thầm.

## 4. Các tầng xử lý

Kiến trúc năm tầng được mô tả trong `HANDOVER.md`. Bảng dưới đối chiếu từng tầng với tệp thực tế.

| Tầng | Việc làm | Tệp chính | Trạng thái |
|---|---|---|---|
| 0 | Chuyển âm thanh thành lượt thoại có mốc thời gian và người nói | `src/audio/pipeline.py`, `alignment.py`, `pyannote_provider.py` | Chạy được; tách người nói bằng pyannote cần khoá Hugging Face |
| 1 | Bóc mẩu tin nguyên tử, có trích dẫn | `src/nhanh.py`, `phat_bieu.py`, `bakeoff.py` | Chạy được với mô hình; trọng số adapter không có trong repo |
| 2 | Gom chủ thể: bác sĩ, bệnh nhân, người nhà | `src/thuc_the.py`, `phan_quan_he.py` | Có |
| 3 | Máy trạng thái đính chính: lời sửa thay thế lời cũ | `src/cap_nhat.py` | Có |
| 4 | Khóa bằng chứng K1–K7, cổng rủi ro, cách ly | `src/khoa_bang_chung.py`, `cong_rui_ro.py`, `canh_bao/` | Có |
| 5 | Ghép bệnh án theo mục, không dùng LLM | `src/sinh_benh_an.py` | Có |

## 5. Các tệp và thư mục

- **`src/`** (82 tệp Python ở cấp gốc, cộng thư mục `audio/` và `canh_bao/`): pipeline, dịch vụ HTTP `dich_vu.py`, bộ sinh dữ liệu mô phỏng, bộ chấm, và các tệp kiểm dữ liệu.
- **`tests/`** (102 tệp): 1.357 test được thu thập. Xem mục 9 về trạng thái chạy.
- **`web/`**: ứng dụng React 19 + Vite + Tailwind, máy chủ Express (`server.ts`), có 29 thành phần giao diện trong `web/src/components/`. Dữ liệu trong `web/db/schema.sql`.
- **`docs/`**: báo cáo, slide, tài liệu cho ban giám khảo.
- **`data/`**: chỉ có `audio/` và `meditrace.db`. Bộ hội thoại mô phỏng và kết quả chạy không nằm trong repo.
- **`models/`**: trống. Trọng số QLoRA không có trong repo.

Các tệp gốc quan trọng: `README.md` (giới thiệu ngắn cho người đánh giá), `HANDOVER.md` (bàn giao kỹ thuật), `Q_AND_A_BAN_GIAM_KHAO.md` (câu hỏi và trả lời), `BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md` (các bảng thực nghiệm, xem mục 8).

## 6. Cách các phần nối nhau khi chạy

```
Trình duyệt ──> web/server.ts (Express, cổng 3000)
                    │  gọi qua MEDITRACE_API
                    ▼
              src/dich_vu.py (HTTP, cổng 8765)
                    │  bộ đệm ca đã chạy sẵn, hoặc mô hình cục bộ
                    ▼
              src/nhanh.py -> khóa bằng chứng -> sinh bệnh án
```

- Các endpoint của `dich_vu.py`: `/api/suc-khoe`, `/api/ca-mau`, `/api/chep-am`, `/api/gan-vai`, `/api/ho-so`, `/api/phien/`.
- `web/server.ts` có các endpoint cho ca khám, sinh bản nháp, chỉnh sửa, hỏi đáp, tra cứu PubMed và phác đồ, cùng tuỳ chọn gọi mô hình ngoài qua giao diện tương thích OpenAI.
- Ca mẫu trên trang chủ đọc từ bộ đệm kết quả đã chạy sẵn (`nguon: "bo_dem"` trong `dich_vu.py`). **Ca mẫu không gọi mô hình thật mỗi lần bấm.**
- Triển khai công khai: giao diện trên Vercel, chuyển tiếp qua đường hầm Cloudflare về máy chủ HoaiĐức, nơi có mô hình. Khi máy đó tắt thì trang công khai không dùng được.

## 7. Dữ liệu và cách tạo

- Hội thoại được sinh từ **200 khuôn ca bệnh** trong `src/ngu_lieu_viet.py` (`BENH`). Đếm trực tiếp ngày 18/11/2026: 200 tên khuôn duy nhất. Bản trước của tài liệu này ghi 100 khuôn là sai; đã sửa.
- Phần khuôn do AI viết (thêm ngày 10/09 và 11/09) **chưa có bác sĩ duyệt**. Toàn bộ 200 khuôn hiện chưa duyệt (`DA_DUYET_BAC_SI` rỗng).
- Chia tập theo khuôn bằng băm tên: 13 khuôn phát triển, 12 khuôn kiểm tra cuối, phần còn lại để huấn luyện (`src/tach_tap_viet.py`). Chia theo khuôn để tránh rò rỉ giữa các tập.
- `src/kiem_khuon.py` kiểm từng khuôn: trường dữ liệu, nhãn giới, từ khóa tuổi, chẩn đoán có nhắc tên bệnh, và trùng triệu chứng giữa các khuôn. Trên 200 khuôn hiện tại (đo 18/11/2026): 0 lỗi, 25 cảnh báo, 18 cặp trùng triệu chứng từ 50% trở lên.
- **Phát hiện khi đọc lại:** quy tắc giới theo `CHI_NU`/`CHI_NAM` không khớp khuôn nào. Quy tắc đang chạy là `GIOI_THEO_KHUON`, chỉ gắn nhãn cho 4 khuôn.

## 8. Số liệu: cái nào đo được, cái nào chưa

**Có trong mã và có thể kiểm lại:**
- Số khuôn, số test, số cặp trùng triệu chứng (mục 7).
- Các số trong nhật ký và bảng 6 bảng thực nghiệm chỉ là bản ghi của các lần chạy trước 03/10 trên dữ liệu mô phỏng. Chưa đo lại sau các nâng cấp 04–06/10.

**Chưa đủ căn cứ trong repo:**
- **Bảng 2 của `BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md`** so MediTrace với GPT-4o, Gemini 1.5 Pro, Claude 3.5 Sonnet và Llama-3-8B, kèm tỉ lệ ảo giác và chi phí API. Không có tệp nào trong `src/` hay `tests/` chạy các mô hình này. Các con số này chỉ xuất hiện trong tài liệu và `tools/tao_word_bang_thuc_nghiem.py`. **Không nên đưa ra trình bày khi chưa có lần chạy ghi lại.**
- **Bảng 6** mô tả thử nghiệm lâm sàng với 10 bác sĩ. Trong dự án không có dữ liệu hay tệp nào tương ứng. **Cần sửa thành đề xuất, không phải kết quả.**
- Tỉ lệ "0,0% ảo giác" của MediTrace đúng theo thiết kế của cổng K1 (trích dẫn phải khớp lượt thoại), nhưng chưa đo trên bộ dữ liệu độc lập có nhãn người.

## 9. Trạng thái chạy thử

- Một lượt chạy đầy đủ `pytest` bị dừng ở khoảng 47% (ngày 17/11). Lượt không có test âm thanh chạy đến khoảng 51% trong 280 giây rồi bị hết thời gian. Chưa có kết quả xanh toàn bộ.
- `HANDOVER.md` đã được sửa ngày 17/11: bỏ dòng "tất cả đều đạt 100%", thay `SoapNote.tsx` bằng tệp thật. Lưu ý: lần sửa đó đã đổi 200 thành 100 khuôn là sai; mã hiện có 200 khuôn (đã đếm lại ngày 18/11/2026).

## 10. Đã làm và chưa làm

**Đã có trong mã:**
- Pipeline từ lượt thoại đến bệnh án có trích dẫn (tầng 1 đến 5).
- Dịch vụ HTTP, ứng dụng web với duyệt từng mệnh đề, đối chiếu lời thoại, chỉnh sửa, in và xuất PDF.
- Bộ sinh hội thoại mô phỏng, chia tập theo khuôn, bộ kiểm khuôn.
- Tám module lâm sàng (tương tác thuốc, hiệu chỉnh liều theo thận, 9 thang điểm, cận lâm sàng nguy kịch, khử định danh, xuất FHIR R4, dặn dò bệnh nhân, phương ngữ) có tệp kiểm riêng.

**Chưa nối vào luồng chạy:**
- Tám module lâm sàng trên chỉ được `src/dieu_phoi_ha_tang.py` import, và module đó không có ai gọi. Do đó bản nháp trên web không chạy qua tương tác thuốc, hiệu chỉnh liều hay thang điểm.
- `src/da_benh_ly.py` và `src/dieu_phoi_ha_tang.py` không có nơi gọi.

**Chưa có, cần thứ bên ngoài:**
- Trọng số QLoRA (`models/` trống).
- Mô hình tách người nói pyannote: `pyannote/speaker-diarization-3.1` bị khoá, cần chấp nhận điều kiện và khoá đọc của chủ đề tài.
- Bác sĩ duyệt nội dung khuôn và luật lâm sàng. Đây là điều kiện để dùng ngoài nghiên cứu.
- Thử nghiệm với hội thoại thật đã ẩn danh.
- Khi `approved` vẫn là `false`, luật lâm sàng phải dừng và không xuất kết quả, theo bất biến của dự án.

## 11. Trước khi nộp hoặc trình bày

1. Gỡ hoặc đánh dấu rõ Bảng 2 và Bảng 6 trong `BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md`, `Q_AND_A_BAN_GIAM_KHAO.md` và các bản Word tương ứng.
2. Chạy lại số liệu sau các nâng cấp 04–06/10, và ghi ngày của từng bảng.
3. Chạy `pytest` theo nhóm, ghi số đậu và rớt thật. Không ghi "100%" khi chưa có kết quả.
4. Nếu giới thiệu các module lâm sàng, nói rõ chúng là lớp kiểm có test nhưng chưa nối vào luồng chạy.
5. Chờ bác sĩ duyệt khuôn trước khi dùng bất kỳ con số nào về độ đúng lâm sàng.

## 12. Lệnh chạy

```bash
# Dịch vụ Python (cổng 8765)
python -m src.dich_vu --cong 8765

# Bộ kiểm khuôn
python -m src.kiem_khuon

# Test không cần mô hình âm thanh
python -m pytest -q -k "not audio"

# Ứng dụng web
cd web && npm install && npm run dev
```
