/**
 * Danh sách DUY NHẤT các lối ra mạng của máy chủ web (Đề cải tiến 1).
 *
 * `loi-ra-mang.test.ts` đếm mọi lời gọi fetch trong `web/may-chu` và `web/server.ts`, so với danh sách này:
 * thêm lối ra mới mà không khai báo thì test đỏ. `sinh-so-do-du-lieu.ts` dựng sơ đồ dữ liệu từ đây.
 */
export interface LoiRa {
  /** Tệp chứa lời gọi, tính từ thư mục `web/`. */
  tep: string;
  /** Đích đến. */
  dich: string;
  mucDich: string;
  /** Dữ liệu gì đi ra, và đã được bảo vệ thế nào. */
  duLieu: string;
  /** Lối ra có hoạt động khi chưa ai bật gì không. */
  macDinh: "bat" | "tat";
}

export const LOI_RA_DUOC_PHEP: ReadonlyArray<LoiRa> = [
  {
    tep: "may-chu/routes/dung-chung.ts",
    dich: "Dịch vụ MediTrace (Python) trên cùng máy, MEDITRACE_API, mặc định 127.0.0.1:8765",
    mucDich: "Chép lời, trích mệnh đề, kiểm căn cứ, dựng bản nháp — chạy tại chỗ",
    duLieu: "Âm thanh và lời thoại ca khám; không rời máy (địa chỉ nội bộ, kèm khóa nội bộ)",
    macDinh: "bat",
  },
  {
    tep: "may-chu/routes/llm-ngoai.ts",
    dich: "Cổng mô hình ngoài AIBOX — dịch vụ bên thứ ba (chat/completions)",
    mucDich: "Tính năng phụ: sửa bản nháp theo lời nhắc, hỏi đáp về ca, soạn văn bản",
    duLieu: "Lời thoại/bản nháp ĐÃ CHE định danh; còn định danh thì từ chối gửi (422). Phải qua công tắc quản trị và bác sĩ bật cho từng lần",
    macDinh: "tat",
  },
  {
    tep: "may-chu/routes/llm-ngoai.ts",
    dich: "Cổng mô hình ngoài AIBOX — dịch vụ bên thứ ba (/models)",
    mucDich: "Kiểm tình trạng cổng",
    duLieu: "Không có nội dung ca khám (chỉ khóa truy cập của máy chủ)",
    macDinh: "bat",
  },
  {
    tep: "may-chu/tra-cuu/nguon-ngoai.ts",
    dich: "API tài liệu: NCBI E-utilities (PubMed), WHO IRIS, openFDA… (hàm layChu)",
    mucDich: "Tra tài liệu y khoa",
    duLieu: "Từ khóa y khoa; ô tìm từ chối từ khóa có tên/mã/số liên lạc (422)",
    macDinh: "bat",
  },
  {
    tep: "may-chu/tra-cuu/nguon-ngoai.ts",
    dich: "Trang tài liệu y khoa chính thống (StatPearls/PMC, MedlinePlus, DailyMed, Bộ Y tế, MSD, NICE, WHO, CDC) (hàm layWeb)",
    mucDich: "Đọc nội dung tài liệu để trả lời có nguồn",
    duLieu: "Địa chỉ trang tài liệu; từ khóa do bước tra cứu đặt từ văn bản đã che",
    macDinh: "bat",
  },
  {
    tep: "may-chu/tra-cuu/nguon-ngoai.ts",
    dich: "AAFP (www.aafp.org)",
    mucDich: "Mở bài AAFP theo mã PubMed",
    duLieu: "Mã PubMed của bài báo; không có dữ liệu ca khám",
    macDinh: "bat",
  },
];
