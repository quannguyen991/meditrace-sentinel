/**
 * CƠ SỞ DỮ LIỆU của MediTrace: SQLite trong một tệp (data/meditrace.db), mở bằng node:sqlite
 * có sẵn trong Node — không cần cài thêm gì. Lược đồ ở db/schema.sql.
 *
 * Thay cho các tệp JSON cũ (data/ca-kham.json, tra-cuu.json, mau-van-ban.json): dữ liệu giờ
 * tách theo người dùng, mỗi ca khám một dòng. Lần đầu có tài khoản quản trị, dữ liệu trong
 * các tệp JSON cũ được chuyển vào tài khoản đó (xem chuyenJsonCu).
 */
import { DatabaseSync } from "node:sqlite";
import fs from "fs";
import path from "path";

// Đổi chỗ đặt tệp bằng biến MEDITRACE_DB (dùng khi thử nghiệm, để không đụng dữ liệu thật).
// Các tệp JSON cũ được tìm trong cùng thư mục với tệp dữ liệu.
const TEP_DB = process.env.MEDITRACE_DB || path.join(process.cwd(), "data", "meditrace.db");
const THU_MUC = path.dirname(TEP_DB);
fs.mkdirSync(THU_MUC, { recursive: true });

export const db = new DatabaseSync(TEP_DB);
db.exec("PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 3000;");
db.exec(fs.readFileSync(path.join(process.cwd(), "db", "schema.sql"), "utf-8"));

/** Chạy một khối lệnh trong giao dịch: lỗi giữa chừng thì không ghi gì. */
export function giaoDich<T>(viec: () => T): T {
  db.exec("BEGIN IMMEDIATE");
  try {
    const kq = viec();
    db.exec("COMMIT");
    return kq;
  } catch (e) {
    db.exec("ROLLBACK");
    throw e;
  }
}

export function ghiNhatKy(nguoiDungId: number | null, hanhDong: string, chiTiet?: string | null, diaChi?: string) {
  db.prepare("INSERT INTO nhat_ky (nguoi_dung_id, luc, hanh_dong, chi_tiet, dia_chi) VALUES (?, ?, ?, ?, ?)").run(
    nguoiDungId,
    Date.now(),
    hanhDong,
    chiTiet ?? null,
    diaChi ?? null,
  );
}

// ------------------------------------------------------------------ các kho của từng người
/** Tên kho mà giao diện dùng. Chỉ nhận đúng các tên này. */
export const TEN_KHO = ["ca-kham", "tra-cuu", "mau-van-ban"] as const;
export type TenKho = (typeof TEN_KHO)[number];
export const laTenKho = (t: string): t is TenKho => (TEN_KHO as readonly string[]).includes(t);

function mocLuu(uid: number, kho: TenKho): number {
  const r = db.prepare("SELECT luu_luc FROM moc_luu WHERE nguoi_dung_id = ? AND kho = ?").get(uid, kho) as
    | { luu_luc: number }
    | undefined;
  return r?.luu_luc || 0;
}

/** Đọc một kho của một người, cùng dạng { sessions, savedAt } mà giao diện đang dùng. */
export function docKho(uid: number, kho: TenKho): { sessions: unknown[]; savedAt: number } {
  const dong =
    kho === "ca-kham"
      ? db.prepare("SELECT du_lieu FROM ca_kham WHERE nguoi_dung_id = ? ORDER BY thu_tu").all(uid)
      : db.prepare("SELECT du_lieu FROM muc_kho WHERE nguoi_dung_id = ? AND kho = ? ORDER BY thu_tu").all(uid, kho);
  return { sessions: (dong as { du_lieu: string }[]).map((d) => JSON.parse(d.du_lieu)), savedAt: mocLuu(uid, kho) };
}

const chuoi = (v: unknown, dai = 200) => (typeof v === "string" ? v.slice(0, dai) : null);

/**
 * Ghi đè cả kho của một người bằng danh sách mới (giao diện gửi cả danh sách mỗi lần lưu).
 * Ca khám: ca nào có trong danh sách thì thêm/cập nhật, ca nào không còn thì xoá; cột
 * cap_nhat_luc chỉ đổi khi nội dung ca thật sự đổi. Trước khi ghi, giữ một bản sao (5 phút một bản).
 */
export function ghiKho(uid: number, kho: TenKho, ds: unknown[], savedAt?: number) {
  const bay = Date.now();
  giaoDich(() => {
    const cu = docKho(uid, kho);
    const ganNhat = db
      .prepare("SELECT MAX(luc) AS luc FROM ban_sao WHERE nguoi_dung_id = ? AND kho = ?")
      .get(uid, kho) as { luc: number | null };
    if (cu.sessions.length && bay - (ganNhat.luc || 0) > 5 * 60_000) {
      db.prepare("INSERT INTO ban_sao (nguoi_dung_id, kho, du_lieu, luc) VALUES (?, ?, ?, ?)").run(
        uid,
        kho,
        JSON.stringify(cu),
        bay,
      );
      db.prepare(
        `DELETE FROM ban_sao WHERE nguoi_dung_id = ? AND kho = ? AND id NOT IN
           (SELECT id FROM ban_sao WHERE nguoi_dung_id = ? AND kho = ? ORDER BY luc DESC LIMIT 30)`,
      ).run(uid, kho, uid, kho);
    }

    if (kho === "ca-kham") {
      const coSan = new Map(
        (db.prepare("SELECT id, du_lieu FROM ca_kham WHERE nguoi_dung_id = ?").all(uid) as { id: string; du_lieu: string }[]).map(
          (d) => [d.id, d.du_lieu],
        ),
      );
      const conLai = new Set<string>();
      const them = db.prepare(
        `INSERT INTO ca_kham (nguoi_dung_id, id, thu_tu, ten_benh_nhan, ngay_kham, du_lieu, tao_luc, cap_nhat_luc)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      );
      const sua = db.prepare(
        `UPDATE ca_kham SET thu_tu = ?, ten_benh_nhan = ?, ngay_kham = ?, du_lieu = ?, cap_nhat_luc = ?
         WHERE nguoi_dung_id = ? AND id = ?`,
      );
      const doiThuTu = db.prepare("UPDATE ca_kham SET thu_tu = ? WHERE nguoi_dung_id = ? AND id = ?");
      ds.forEach((ca: any, i) => {
        const id = chuoi(ca?.id, 100);
        if (!id || conLai.has(id)) throw Object.assign(new Error("Ca khám thiếu id hoặc trùng id"), { ma: 400 });
        conLai.add(id);
        const json = JSON.stringify(ca);
        const ten = chuoi(ca.patientIdentifier);
        const ngay = chuoi(ca.date, 40);
        if (!coSan.has(id)) them.run(uid, id, i, ten, ngay, json, bay, bay);
        else if (coSan.get(id) !== json) sua.run(i, ten, ngay, json, bay, uid, id);
        else doiThuTu.run(i, uid, id);
      });
      const xoa = db.prepare("DELETE FROM ca_kham WHERE nguoi_dung_id = ? AND id = ?");
      for (const id of coSan.keys()) if (!conLai.has(id)) xoa.run(uid, id);
    } else {
      db.prepare("DELETE FROM muc_kho WHERE nguoi_dung_id = ? AND kho = ?").run(uid, kho);
      const them = db.prepare("INSERT INTO muc_kho (nguoi_dung_id, kho, thu_tu, du_lieu) VALUES (?, ?, ?, ?)");
      ds.forEach((m, i) => them.run(uid, kho, i, JSON.stringify(m)));
    }

    db.prepare(
      `INSERT INTO moc_luu (nguoi_dung_id, kho, luu_luc) VALUES (?, ?, ?)
       ON CONFLICT (nguoi_dung_id, kho) DO UPDATE SET luu_luc = excluded.luu_luc`,
    ).run(uid, kho, Number(savedAt) || bay);
  });
}

/**
 * Chuyển dữ liệu từ các tệp JSON cũ (trước khi có đăng nhập) vào tài khoản quản trị đầu tiên.
 * Chạy một lần; tệp cũ được đổi tên thành *.json.da-chuyen-sql (không xoá) để còn đối chiếu.
 */
export function chuyenJsonCu(uid: number): string[] {
  const daChuyen = db.prepare("SELECT gia_tri FROM cai_dat WHERE khoa = 'da_chuyen_json'").get();
  if (daChuyen) return [];
  const ketQua: string[] = [];
  for (const kho of TEN_KHO) {
    const tep = path.join(THU_MUC, `${kho}.json`);
    if (!fs.existsSync(tep)) continue;
    try {
      const d = JSON.parse(fs.readFileSync(tep, "utf-8"));
      if (Array.isArray(d.sessions) && d.sessions.length) {
        ghiKho(uid, kho, d.sessions, d.savedAt);
        ketQua.push(`${kho}: ${d.sessions.length}`);
      }
      fs.renameSync(tep, `${tep}.da-chuyen-sql`);
    } catch (e: any) {
      ketQua.push(`${kho}: lỗi ${e?.message || e}`);
    }
  }
  db.prepare("INSERT INTO cai_dat (khoa, gia_tri) VALUES ('da_chuyen_json', ?)").run(String(Date.now()));
  return ketQua;
}
