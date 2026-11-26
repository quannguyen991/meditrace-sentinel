/**
 * CƠ SỞ DỮ LIỆU của MediTrace: SQLite trong một tệp (data/meditrace.db), mở bằng node:sqlite
 * có sẵn trong Node — không cần cài thêm gì. Lược đồ ở db/schema.sql.
 */
import { DatabaseSync } from "node:sqlite";
import fs from "fs";
import path from "path";
import { damBaoBangWorm, taoKhoWorm } from "./worm";

const TEP_DB = process.env.MEDITRACE_DB || path.join(process.cwd(), "data", "meditrace.db");
const THU_MUC = path.dirname(TEP_DB);
fs.mkdirSync(THU_MUC, { recursive: true });

export const db = new DatabaseSync(TEP_DB);
db.exec("PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 3000; PRAGMA foreign_keys = ON;");
const TEP_SCHEMA = fs.existsSync(path.join(process.cwd(), "db", "schema.sql"))
  ? path.join(process.cwd(), "db", "schema.sql")
  : path.join(process.cwd(), "web", "db", "schema.sql");
db.exec(fs.readFileSync(TEP_SCHEMA, "utf-8"));
// Đảm bảo migration bảng + trigger `worm_signoff` cho cả các tệp DB cũ đã tồn tại từ trước
damBaoBangWorm(db);

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

function luuBanSaoNeuToiHan(uid: number, kho: TenKho, bay: number): void {
  const ganNhat = db
    .prepare("SELECT MAX(luc) AS luc FROM ban_sao WHERE nguoi_dung_id = ? AND kho = ?")
    .get(uid, kho) as { luc: number | null } | undefined;
  // Chỉ đọc dữ liệu cũ khi ĐÃ quá hạn 5 phút — không gọi docKho() / JSON.parse() vô ích mỗi lần autosave!
  if (bay - (ganNhat?.luc || 0) <= 5 * 60_000) return;

  const dong = (
    kho === "ca-kham"
      ? db.prepare("SELECT du_lieu FROM ca_kham WHERE nguoi_dung_id = ? ORDER BY thu_tu").all(uid)
      : db.prepare("SELECT du_lieu FROM muc_kho WHERE nguoi_dung_id = ? AND kho = ? ORDER BY thu_tu").all(uid, kho)
  ) as Array<{ du_lieu: string }>;
  if (!dong.length) return;

  const duLieuJson = `{"sessions":[${dong.map((d) => d.du_lieu).join(",")}],"savedAt":${mocLuu(uid, kho)}}`;
  db.prepare("INSERT INTO ban_sao (nguoi_dung_id, kho, du_lieu, luc) VALUES (?, ?, ?, ?)").run(uid, kho, duLieuJson, bay);
  db.prepare(
    `DELETE FROM ban_sao WHERE nguoi_dung_id = ? AND kho = ? AND id NOT IN
       (SELECT id FROM ban_sao WHERE nguoi_dung_id = ? AND kho = ? ORDER BY luc DESC LIMIT 30)`,
  ).run(uid, kho, uid, kho);
}

/**
 * Ghi đè cả kho của một người bằng danh sách mới (tương thích ngược 100% với giao diện hiện có).
 */
export function ghiKho(uid: number, kho: TenKho, ds: unknown[], savedAt?: number) {
  const bay = Date.now();
  giaoDich(() => {
    luuBanSaoNeuToiHan(uid, kho, bay);

    if (kho === "ca-kham") {
      const coSan = new Map(
        (
          db.prepare("SELECT id, du_lieu, cap_nhat_luc FROM ca_kham WHERE nguoi_dung_id = ?").all(uid) as Array<{
            id: string;
            du_lieu: string;
            cap_nhat_luc: number;
          }>
        ).map((d) => [d.id, d]),
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
        const cu = coSan.get(id);
        if (!cu) them.run(uid, id, i, ten, ngay, json, bay, bay);
        else if (cu.du_lieu !== json) sua.run(i, ten, ngay, json, Math.max(bay, cu.cap_nhat_luc + 1), uid, id);
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
 * Upsert hạt mịn MỘT ca khám theo `id`, hỗ trợ kiểm tra khóa lạc quan `expectedUpdatedAt` (trả mã 409 nếu cũ hơn).
 */
export function ghiMotCaKham(
  uid: number,
  rawId: string,
  caDauVao: Record<string, unknown>,
  tuyChon?: { expectedUpdatedAt?: number | null; savedAt?: number },
): { ok: true; id: string; updatedAt: number; created: boolean } {
  const id = chuoi(rawId.trim(), 100);
  if (!id) throw Object.assign(new Error("Thiếu mã ca khám hợp lệ"), { ma: 400, status: 400 });
  if (!caDauVao || typeof caDauVao !== "object" || Array.isArray(caDauVao)) {
    throw Object.assign(new Error("Dữ liệu ca khám không hợp lệ"), { ma: 400, status: 400 });
  }
  if (caDauVao.id !== undefined && String(caDauVao.id).trim() !== id) {
    throw Object.assign(new Error("Mã id trong thân yêu cầu không khớp với URL"), { ma: 400, status: 400 });
  }
  const expected = tuyChon?.expectedUpdatedAt;
  if (expected !== undefined && expected !== null && (typeof expected !== "number" || !Number.isFinite(expected))) {
    throw Object.assign(new Error("expectedUpdatedAt phải là số hợp lệ"), { ma: 400, status: 400 });
  }

  const ca = { ...caDauVao, id };
  const json = JSON.stringify(ca);
  const ten = chuoi((ca as any).patientIdentifier);
  const ngay = chuoi((ca as any).date, 40);
  const bay = Date.now();

  return giaoDich(() => {
    const cu = db
      .prepare("SELECT du_lieu, thu_tu, cap_nhat_luc FROM ca_kham WHERE nguoi_dung_id = ? AND id = ?")
      .get(uid, id) as { du_lieu: string; thu_tu: number; cap_nhat_luc: number } | undefined;

    if (cu && typeof expected === "number" && expected < cu.cap_nhat_luc) {
      throw Object.assign(new Error("Ca khám trên máy chủ đã được cập nhật mới hơn (xung đột phiên bản)."), {
        ma: 409,
        status: 409,
        code: "conflict_stale_version",
        currentUpdatedAt: cu.cap_nhat_luc,
      });
    }

    luuBanSaoNeuToiHan(uid, "ca-kham", bay);

    let capNhatLuc = bay;
    if (!cu) {
      const thuTuTiep = db
        .prepare("SELECT COALESCE(MAX(thu_tu) + 1, 0) AS n FROM ca_kham WHERE nguoi_dung_id = ?")
        .get(uid) as { n: number };
      db.prepare(
        `INSERT INTO ca_kham (nguoi_dung_id, id, thu_tu, ten_benh_nhan, ngay_kham, du_lieu, tao_luc, cap_nhat_luc)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      ).run(uid, id, Number(thuTuTiep.n), ten, ngay, json, bay, capNhatLuc);
    } else if (cu.du_lieu !== json) {
      capNhatLuc = Math.max(bay, cu.cap_nhat_luc + 1);
      db.prepare(
        `UPDATE ca_kham SET ten_benh_nhan = ?, ngay_kham = ?, du_lieu = ?, cap_nhat_luc = ?
         WHERE nguoi_dung_id = ? AND id = ?`,
      ).run(ten, ngay, json, capNhatLuc, uid, id);
    } else {
      capNhatLuc = cu.cap_nhat_luc;
    }

    const mocMoi = Math.max(Number(tuyChon?.savedAt) || capNhatLuc, mocLuu(uid, "ca-kham"));
    db.prepare(
      `INSERT INTO moc_luu (nguoi_dung_id, kho, luu_luc) VALUES (?, 'ca-kham', ?)
       ON CONFLICT (nguoi_dung_id, kho) DO UPDATE SET luu_luc = excluded.luu_luc`,
    ).run(uid, mocMoi);

    return { ok: true, id, updatedAt: capNhatLuc, created: !cu };
  });
}

/** Xoá hạt mịn MỘT ca khám của người dùng `uid`. */
export function xoaMotCaKham(uid: number, rawId: string): { ok: true; id: string; deleted: boolean } {
  const id = chuoi(rawId.trim(), 100);
  if (!id) throw Object.assign(new Error("Thiếu mã ca khám hợp lệ"), { ma: 400, status: 400 });
  const bay = Date.now();
  return giaoDich(() => {
    luuBanSaoNeuToiHan(uid, "ca-kham", bay);
    const kq = db.prepare("DELETE FROM ca_kham WHERE nguoi_dung_id = ? AND id = ?").run(uid, id);
    const daXoa = Number(kq.changes) > 0;
    if (daXoa) {
      db.prepare(
        `INSERT INTO moc_luu (nguoi_dung_id, kho, luu_luc) VALUES (?, 'ca-kham', ?)
         ON CONFLICT (nguoi_dung_id, kho) DO UPDATE SET luu_luc = excluded.luu_luc`,
      ).run(uid, bay);
    }
    return { ok: true, id, deleted: daXoa };
  });
}

/**
 * Kiểm tra IDOR: trả `true` nếu `sessionId` không thuộc `uid` nhưng đã tồn tại thuộc về bác sĩ khác
 * trong `ca_kham` hoặc trong sổ ký duyệt `worm_signoff`.
 */
export function caKhamThuocNguoiKhac(uid: number, sessionId: string): boolean {
  const cuaMinh = db.prepare("SELECT 1 FROM ca_kham WHERE id = ? AND nguoi_dung_id = ? LIMIT 1").get(sessionId, uid);
  if (cuaMinh) return false;
  const cuaKhac = db.prepare("SELECT 1 FROM ca_kham WHERE id = ? AND nguoi_dung_id != ? LIMIT 1").get(sessionId, uid);
  if (cuaKhac) return true;
  const kyBoiMinh = db
    .prepare("SELECT 1 FROM worm_signoff WHERE session_id = ? AND nguoi_dung_id = ? LIMIT 1")
    .get(sessionId, uid);
  if (kyBoiMinh) return false;
  const kyBoiKhac = db
    .prepare("SELECT 1 FROM worm_signoff WHERE session_id = ? AND nguoi_dung_id IS NOT NULL AND nguoi_dung_id != ? LIMIT 1")
    .get(sessionId, uid);
  return Boolean(kyBoiKhac);
}

/**
 * Chuyển dữ liệu từ các tệp JSON cũ (trước khi có đăng nhập) vào tài khoản quản trị đầu tiên.
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

const DUONG_DAN_WORM_JSONL = (() => {
  if (process.env.MEDITRACE_WORM_JSONL) return process.env.MEDITRACE_WORM_JSONL;
  if (process.env.MEDITRACE_DB) return path.join(THU_MUC, "worm_signoff_log.jsonl");
  const dataDir = path.resolve(process.cwd(), "..", "data");
  return fs.existsSync(dataDir)
    ? path.join(dataDir, "worm_signoff_log.jsonl")
    : path.join(THU_MUC, "worm_signoff_log.jsonl");
})();

export const khoWorm = taoKhoWorm(db, DUONG_DAN_WORM_JSONL);
export { damBaoBangWorm, taoKhoWorm } from "./worm";
