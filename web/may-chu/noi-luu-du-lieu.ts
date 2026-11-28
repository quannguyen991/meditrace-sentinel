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
    giu: "Việc quá 30 phút bị đánh dấu thất bại; Việc đã kết thúc (xong/thất bại/đã hủy) cũ hơn 30 phút bị xóa định kỳ bởi donViecCu(TUOI_VIEC_TOI_DA_MS) (asr.ts, tro-ly.ts)",
  },
  {
    noi: "Thư mục phiên âm thanh (dịch vụ Python)",
    tep: "src/audio/storage.py",
    noiDung: "Tệp ghi âm gốc và bản 16 kHz, lời thoại chép, nhật ký sự kiện",
    coDinhDanh: "co",
    aiDoc: "Dịch vụ Python tại chỗ",
    giu: "Tệp ghi âm gốc và bản 16 kHz của phiên đã duyệt (gửi sang MediTrace) bị xóa sau 30 ngày kể từ lúc duyệt (MEDITRACE_GIU_AM_THANH_NGAY), phiên chưa duyệt đã có lời thoại (chờ bác sĩ nghe kiểm) giữ 30 ngày (MEDITRACE_GIU_AM_THANH_CHUA_DUYET_NGAY), phiên bỏ dở không có lời thoại bị xóa sau 7 ngày (MEDITRACE_GIU_AM_THANH_BO_DO_NGAY), đều ghi sự kiện am_thanh_da_xoa; lời thoại và nhật ký giữ lại. Dọn khi tạo phiên (tối đa 1 lần/ngày), khi api.py khởi động, và khi dich_vu_http.py khởi tạo AudioPipeline",
  },
  {
    noi: "Bảng ban_ky_duyet (bản chụp hồ sơ lúc ký)",
    tep: "web/may-chu/kiem-ky-may-chu.ts",
    noiDung: "Số thứ tự WORM, mã tab đã ký, băm nội dung, và bản chụp ca_kham.du_lieu đúng thời điểm bác sĩ ký",
    coDinhDanh: "co",
    aiDoc: "Chỉ bác sĩ sở hữu ca (đối chiếu lúc xuất)",
    giu: "Vĩnh viễn (trigger SQLite cấm sửa/xóa; gắn với chuỗi WORM)",
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
    giu: "Xóa mọi khóa meditrace_ (ca khám, các kho, mẫu giọng, công tắc gửi ra ngoài) khi đăng xuất, khi hết phiên (401) và khi người khác đăng nhập trên máy đó (web/src/lib/xoaDuLieuTrinhDuyet.ts); chỉ giữ vị trí thanh tác vụ. Đóng trình duyệt mà không đăng xuất thì bản sao còn đến lần đăng nhập sau",
  },
];
