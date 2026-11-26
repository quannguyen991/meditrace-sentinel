-- Lược đồ cơ sở dữ liệu MediTrace Sentinel (SQLite, chạy bằng node:sqlite có sẵn trong Node ≥ 22.5).
-- Tệp dữ liệu: data/meditrace.db (git bỏ qua cả thư mục data/ vì có thể chứa hội thoại khám thật).
-- server.ts chạy tệp này mỗi lần khởi động; mọi lệnh đều IF NOT EXISTS nên chạy lại không mất gì.
--
-- Quy ước thời gian: số mili giây từ 1970 (Date.now()), múi UTC.
-- Mỗi người dùng chỉ đọc/ghi được dòng có nguoi_dung_id của chính mình — server lọc ở mọi truy vấn.

PRAGMA foreign_keys = ON;

-- Tài khoản. Mật khẩu không lưu; chỉ lưu kết quả băm scrypt kèm muối riêng từng người.
CREATE TABLE IF NOT EXISTS nguoi_dung (
  id              INTEGER PRIMARY KEY,
  email           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
  ho_ten          TEXT    NOT NULL,
  mat_khau_bam    TEXT    NOT NULL,              -- scrypt$N$r$p$muoi$bam (base64)
  vai             TEXT    NOT NULL DEFAULT 'bac_si' CHECK (vai IN ('quan_tri', 'bac_si')),
  tao_luc         INTEGER NOT NULL,
  dang_nhap_cuoi  INTEGER
);

-- Phiên đăng nhập. Trình duyệt giữ token trong cookie HttpOnly; bảng chỉ giữ mã băm SHA-256 của
-- token, nên lộ tệp dữ liệu cũng không dùng lại được phiên.
CREATE TABLE IF NOT EXISTS phien (
  bam_token      TEXT    PRIMARY KEY,
  nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
  tao_luc        INTEGER NOT NULL,
  het_han        INTEGER NOT NULL,
  dia_chi        TEXT,
  trinh_duyet    TEXT
);
CREATE INDEX IF NOT EXISTS phien_theo_nguoi ON phien(nguoi_dung_id);

-- Mã mời. Đăng ký (trừ tài khoản đầu tiên) phải có mã do quản trị tạo; mỗi mã dùng một lần.
-- Cũng chỉ lưu mã băm.
CREATE TABLE IF NOT EXISTS ma_moi (
  bam_ma    TEXT    PRIMARY KEY,
  goi_y     TEXT    NOT NULL,                     -- 2 ký tự cuối, để quản trị nhận ra mã nào
  tao_boi   INTEGER REFERENCES nguoi_dung(id) ON DELETE SET NULL,
  tao_luc   INTEGER NOT NULL,
  het_han   INTEGER NOT NULL,
  dung_boi  INTEGER REFERENCES nguoi_dung(id) ON DELETE SET NULL,
  dung_luc  INTEGER
);

-- Ca khám: mỗi ca một dòng. Cột ten_benh_nhan/ngay_kham tách ra để tìm và sắp xếp;
-- phần còn lại (lời thoại, các tab, bản nháp, kết quả duyệt, hỏi đáp) nằm nguyên trong du_lieu (JSON).
CREATE TABLE IF NOT EXISTS ca_kham (
  nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
  id             TEXT    NOT NULL,
  thu_tu         INTEGER NOT NULL,
  ten_benh_nhan  TEXT,
  ngay_kham      TEXT,
  du_lieu        TEXT    NOT NULL CHECK (json_valid(du_lieu)),
  tao_luc        INTEGER NOT NULL,
  cap_nhat_luc   INTEGER NOT NULL,
  PRIMARY KEY (nguoi_dung_id, id)
);

-- Các danh sách nhỏ khác của từng người: lịch sử tra cứu, mẫu văn bản tự tạo, hồ sơ bệnh nhân, nhiệm vụ lâm sàng.
CREATE TABLE IF NOT EXISTS muc_kho (
  nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
  kho            TEXT    NOT NULL CHECK (kho IN ('tra-cuu', 'mau-van-ban', 'benh-nhan', 'nhiem-vu')),
  thu_tu         INTEGER NOT NULL,
  du_lieu        TEXT    NOT NULL CHECK (json_valid(du_lieu)),
  PRIMARY KEY (nguoi_dung_id, kho, thu_tu)
);

-- Mốc lưu gần nhất của từng kho, để trình duyệt biết bản trên máy chủ mới hơn hay cũ hơn bản của nó.
CREATE TABLE IF NOT EXISTS moc_luu (
  nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
  kho            TEXT    NOT NULL,
  luu_luc        INTEGER NOT NULL,
  PRIMARY KEY (nguoi_dung_id, kho)
);

-- Bản sao lưu: tối đa 5 phút một bản cho mỗi người mỗi kho, giữ 30 bản gần nhất.
-- Lỡ ghi đè (hai trình duyệt, lỗi đồng bộ) thì khôi phục từ đây.
CREATE TABLE IF NOT EXISTS ban_sao (
  id             INTEGER PRIMARY KEY,
  nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
  kho            TEXT    NOT NULL,
  du_lieu        TEXT    NOT NULL,
  luc            INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ban_sao_theo_kho ON ban_sao(nguoi_dung_id, kho, luc);

-- Nhật ký thao tác: đăng ký, đăng nhập (cả lần sai), đăng xuất, tạo mã mời, và mỗi lần
-- nội dung ca khám được gửi ra mô hình ngoài — để kê khai đúng ai gửi gì, lúc nào.
CREATE TABLE IF NOT EXISTS nhat_ky (
  id             INTEGER PRIMARY KEY,
  nguoi_dung_id  INTEGER REFERENCES nguoi_dung(id) ON DELETE SET NULL,
  luc            INTEGER NOT NULL,
  hanh_dong      TEXT    NOT NULL,
  chi_tiet       TEXT,
  dia_chi        TEXT
);
CREATE INDEX IF NOT EXISTS nhat_ky_theo_luc ON nhat_ky(luc);

-- Cờ một lần (ví dụ: đã chuyển dữ liệu từ các tệp JSON cũ vào đây chưa).
CREATE TABLE IF NOT EXISTS cai_dat (
  khoa     TEXT PRIMARY KEY,
  gia_tri  TEXT
);

-- Sổ kiểm toán ký duyệt bất biến WORM (Thông tư 46/2018/TT-BYT): lưu chuỗi băm SHA-256
-- song song với worm_signoff_log.jsonl; trigger cấm UPDATE/DELETE tuyệt đối.
CREATE TABLE IF NOT EXISTS worm_signoff (
  seq             INTEGER PRIMARY KEY,
  timestamp       TEXT    NOT NULL,
  nguoi_dung_id   INTEGER REFERENCES nguoi_dung(id) ON DELETE RESTRICT,
  event           TEXT    NOT NULL DEFAULT 'doctor_forensic_signoff',
  session_id      TEXT    NOT NULL,
  tong_menh_de    INTEGER NOT NULL,
  so_giu          INTEGER NOT NULL,
  so_sua          INTEGER NOT NULL,
  so_bo           INTEGER NOT NULL,
  ty_le_co_nguon  REAL    NOT NULL,
  content_hash    TEXT    NOT NULL,
  prev_hash       TEXT    NOT NULL,
  curr_hash       TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS worm_signoff_theo_phien ON worm_signoff(session_id, seq);

CREATE TRIGGER IF NOT EXISTS trg_worm_signoff_no_update
BEFORE UPDATE ON worm_signoff
BEGIN
  SELECT RAISE(FAIL, 'WORM Violation: Khong duoc sua ban ghi ky duyet da khoa');
END;

CREATE TRIGGER IF NOT EXISTS trg_worm_signoff_no_delete
BEFORE DELETE ON worm_signoff
BEGIN
  SELECT RAISE(FAIL, 'WORM Violation: Khong duoc xoa ban ghi ky duyet da khoa');
END;
