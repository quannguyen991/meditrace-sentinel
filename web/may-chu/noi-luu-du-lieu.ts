/**
 * Mọi nơi MediTrace lưu dữ liệu (Đề cải tiến 1). Ghi đúng điều đọc được từ mã; chỗ chưa làm thì ghi chưa làm.
 * `sinh-so-do-du-lieu.ts` dựng bảng "Nơi lưu dữ liệu" trong sơ đồ dữ liệu từ danh sách này.
 */
export interface NoiLuu {
  noi: string;
  tep: string;
  noiDung: string;
  coDinhDanh: "co" | "khong" | "da_che";
  aiDoc: string;
  giu: string;
}

export const NOI_LUU_DU_LIEU: ReadonlyArray<NoiLuu> = [
  {
    noi: "Bảng ca_kham (SQLite máy chủ web)",
    tep: "web/db/schema.sql",
    noiDung: "Lời thoại, bản nháp, quyết định duyệt, tên bệnh nhân, ngày khám",
    coDinhDanh: "co",
    aiDoc: "Chỉ bác sĩ sở hữu ca (mọi truy vấn lọc theo nguoi_dung_id)",
    giu: "Đến khi bác sĩ xóa ca; chưa có hạn tự xóa",
  },
  {
    noi: "Bảng ban_sao (bản sao trước khi ghi đè)",
    tep: "web/db/schema.sql",
    noiDung: "Bản sao dữ liệu kho của chính người dùng",
    coDinhDanh: "co",
    aiDoc: "Chỉ người dùng đó",
    giu: "30 bản gần nhất cho mỗi kho; chưa có hạn theo ngày",
  },
  {
    noi: "Bảng muc_kho (lịch sử tra cứu, mẫu văn bản, hồ sơ bệnh nhân, nhiệm vụ)",
    tep: "web/db/schema.sql",
    noiDung: "Danh sách nhỏ theo từng người dùng",
    coDinhDanh: "co",
    aiDoc: "Chỉ người dùng đó",
    giu: "Đến khi người dùng xóa",
  },
  {
    noi: "Bảng nhat_ky (nhật ký hoạt động)",
    tep: "web/may-chu/csdl.ts",
    noiDung: "Hành động, mã phiên, số đếm, địa chỉ IP; không có nội dung ca khám",
    coDinhDanh: "khong",
    aiDoc: "Quản trị",
    giu: "Không giới hạn",
  },
  {
    noi: "Bảng worm_signoff (sổ ký duyệt không sửa được)",
    tep: "web/may-chu/worm.ts",
    noiDung: "Băm SHA-256 nội dung đã ký, HMAC, số mệnh đề giữ/sửa/bỏ, người ký, thời điểm; không có nội dung",
    coDinhDanh: "khong",
    aiDoc: "Quản trị, người ký",
    giu: "Vĩnh viễn (sổ chỉ được thêm)",
  },
  {
    noi: "Bảng viec_nen, viec_tro_ly (hàng đợi việc)",
    tep: "web/may-chu/hang-doi.ts",
    noiDung: "Tải trọng và kết quả của việc dựng bản nháp / trợ lý (có lời thoại)",
    coDinhDanh: "co",
    aiDoc: "Người dùng tạo việc",
    giu: "Việc quá 30 phút bị đánh dấu thất bại; hạn dọn bảng chưa kiểm",
  },
  {
    noi: "Thư mục phiên âm thanh (dịch vụ Python)",
    tep: "src/audio/storage.py",
    noiDung: "Tệp ghi âm gốc và bản 16 kHz, lời thoại chép, nhật ký sự kiện",
    coDinhDanh: "co",
    aiDoc: "Dịch vụ Python tại chỗ",
    giu: "CHƯA có hạn giữ hay tự xóa âm thanh — việc tiếp theo (Task 11)",
  },
  {
    noi: "Sổ WORM của dịch vụ Python (data/audit_log_worm.db)",
    tep: "src/he_thong/nhat_ky_ky_duyet_worm.py",
    noiDung: "Sự kiện dựng bản nháp: nhánh, nguồn, số mệnh đề; không có lời thoại",
    coDinhDanh: "khong",
    aiDoc: "Quản trị",
    giu: "Vĩnh viễn",
  },
  {
    noi: "Log tiến trình (cửa sổ dòng lệnh máy chủ)",
    tep: "web/may-chu/che-log.ts",
    noiDung: "Thông báo lỗi, đã cắt ngắn và che định danh (cheLog / che_log)",
    coDinhDanh: "da_che",
    aiDoc: "Người vận hành máy chủ",
    giu: "Theo cách người vận hành lưu log",
  },
  {
    noi: "Trình duyệt của bác sĩ (localStorage)",
    tep: "web/src/lib/useKho.ts",
    noiDung: "Bản sao danh sách ca khám và các kho (có lời thoại, tên bệnh nhân) để mở nhanh khi tải lại trang; đặc trưng giọng bác sĩ",
    coDinhDanh: "co",
    aiDoc: "Chỉ máy của bác sĩ",
    giu: "Đến khi xóa dữ liệu trình duyệt",
  },
];
