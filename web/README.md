# MediTrace Sentinel — giao diện

Giao diện cho hệ thống dựng **bản nháp hồ sơ lâm sàng có cấu trúc** từ hội thoại khám bệnh
tiếng Việt. Mỗi dòng trong bản nháp kèm **lượt hội thoại làm căn cứ**, và bác sĩ duyệt từng
dòng trước khi dùng. Hệ thống **không** chẩn đoán và **không** tư vấn điều trị.

## Phần nào chạy ở đâu

Bản do AI Studio dựng ban đầu gọi thẳng Gemini cho mọi việc. Phần đó đã gỡ.

- **Chép âm** (PhoWhisper của VinAI), **tách mệnh đề** (Qwen3-4B + adapter của dự án), cổng rủi
  ro và câu hỏi làm rõ sinh bằng luật: chạy tại chỗ. Đây là phần được đo trong dự án.
- **Việc phụ dùng mô hình thương mại** (cổng ai-box), chỉ chạy khi bác sĩ bật công tắc
  "Mô hình ngoài" (mặc định tắt, server từ chối nếu thiếu cờ cho phép):
  - đề xuất thêm câu hỏi từ tab Ngữ cảnh + lời thoại + mệnh đề đã tách (`/api/questions-external`);
  - hỏi về ca khám, trả lời chỉ từ hội thoại (`/api/clinical-qa`);
  - tra nguồn chính thống (`/api/lookup-official`): mô hình chỉ đặt từ khoá; SERVER tự tìm ở
    thư viện phác đồ Bộ Y tế lưu tại máy (`python tools/tai_phac_do.py` tải PDF từ kcb.vn vào
    `data/phac-do/`, đọc toàn văn theo trang), Bộ Y tế (kcb.vn), nhãn thuốc FDA (openFDA/DailyMed — liều, tương tác, chống chỉ định, lọc theo
    đường dùng), PubMed (ưu tiên hướng dẫn, tổng quan hệ thống; bỏ bài đã rút, bài lạc đề) và
    MedlinePlus; mô hình chỉ tổng hợp các PHƯƠNG ÁN tài liệu nêu, mỗi phương án ghi nguồn, nêu chỗ
    trong nước và nước ngoài khác nhau; server tự thêm danh sách "Nguồn đã tra" và lời nhắc "chỉ để
    tham khảo, không khẳng định". Giới hạn: nhiều tệp phác đồ cũ trên kcb.vn đã hỏng liên kết
    (xem `data/phac-do/muc-luc.json`); phác đồ nào không có trong thư viện thì hệ thống nói rõ;
  - sửa bản nháp theo lời nhắc, bản so sánh (`/api/edit-note`, `/api/generate-note-external`).

  Khâu tách mệnh đề **không bao giờ** đi qua mô hình ngoài. Khoá cổng đọc từ
  `D:\Claude\.secrets\`, không nằm trong mã.

```
Giao diện (React)  →  server.ts (chuyển tiếp)  →  python -m src.dich_vu  →  MediTrace
   npm run dev            cổng 3000/3100              cổng 8765            (D:\Claude\meditrace-sentinel)
```

## Cách chạy

1. Bật dịch vụ MediTrace (thư mục `D:\Claude\meditrace-sentinel`):

   ```
   D:\meditrace-venv-lap\Scripts\python -m src.dich_vu --cong 8765
   ```

   Thêm `--khong-mo-hinh` nếu GPU đang bận: khi đó chỉ dùng được ca đã chạy trước và các ca
   có sẵn bộ đệm khâu trích.

2. Bật giao diện (thư mục này):

   ```
   npm install
   npm run dev
   ```

   Biến môi trường: `MEDITRACE_API` (mặc định `http://127.0.0.1:8765`), `PORT` (mặc định 3000).

## Ba nhãn nguồn — luôn hiện trên giao diện

| Nhãn | Nghĩa |
|---|---|
| Mô hình vừa chạy | Khâu trích chạy ngay bằng Qwen3-4B + adapter của dự án |
| Khâu trích lấy từ bộ đệm | Khâu trích lấy từ tệp đã chạy trước, khâu sinh chạy ngay (vài giây, không cần GPU) |
| Bản ghi đã chạy từ trước | Lấy nguyên kết quả cũ, không tính lại |

Nhãn này bắt buộc phải thấy được. Người xem demo không được hiểu nhầm một bản ghi cũ là máy
vừa chạy.

## Màn hình

- **Lời thoại ca khám** — gõ hoặc tải tệp âm thanh (chép bằng PhoWhisper chạy tại chỗ), hoặc
  nạp một ca đã chạy trước từ bộ dữ liệu tổng hợp của dự án.
- **Duyệt từng mệnh đề** — mỗi mệnh đề kèm: nói về ai, mức chắc chắn, phủ định, mốc thời gian,
  thuốc, lượt hội thoại làm căn cứ. Bác sĩ giữ, sửa hoặc bỏ. Mệnh đề bị cổng rủi ro đưa sang
  mục "Cần bác sĩ xác nhận" được đánh dấu kèm lý do.
- **Bệnh nhân / Nhiệm vụ / Mẫu** — vẫn là dữ liệu minh hoạ, có dải nhắc rõ trên đầu màn.
- **Ngăn phải (màn soạn)** — câu hỏi làm rõ sinh từ hội thoại; nút "Đề xuất thêm câu hỏi";
  nút "+" chép câu hỏi vào tab Ngữ cảnh; ô hỏi có hai chế độ "Hỏi về ca khám" và
  "Tra nguồn chính thống".

## Những gì bản này KHÔNG làm

- Không chẩn đoán, không kê đơn; câu trả lời tra cứu là tài liệu tham khảo, bác sĩ quyết định.
- Không tự quyết vai người nói. Nếu dịch vụ bật tách người nói (pyannote), lời thoại được chia theo
  giọng thành "Người nói 1", "Người nói 2"…; bác sĩ gán vai (Bác sĩ, Bệnh nhân, Người nhà…) cho từng
  người nói ở ô "Gán vai theo người nói" trước khi tạo bản nháp. Không bật thì mọi đoạn là một người
  nói và bác sĩ gán vai từng lượt.
- Không kết nối HIS/EMR.

## Tài khoản và dữ liệu

- Đăng nhập bắt buộc. Dữ liệu ca khám lưu trong SQLite `data/meditrace.db`, tách theo người dùng
  (`may-chu/csdl.ts`, `may-chu/tai-khoan.ts`, lược đồ `db/schema.sql`).
- Tài khoản quản trị đầu tiên do người dùng tự tạo, ngồi ở chính máy chạy server (không cần mã mời).
  Người sau vào bằng **mã mời**: 8 ký tự, dùng một lần, hết hạn sau 7 ngày, chỉ hiện một lần lúc tạo.
- Thư mục `data/` không vào git vì có thể chứa hội thoại thật.

## Kiểm tra

```
npm run lint        # kiểm kiểu TypeScript
npx tsx src/lib/nguoiNoi.test.ts    # mỗi tệp *.test.ts trong src/lib chạy riêng bằng tsx
```

## Tình trạng (27/09/2026)

- Chạy trên máy HoaiĐức cùng dịch vụ Python. Bản web trên HoaiĐức chưa có ô gán vai theo người nói.
- Kho chưa có remote, chưa đẩy lên GitHub.
