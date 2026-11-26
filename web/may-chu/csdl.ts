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

/**
 * Migration lũy đẳng nâng cấp CHECK constraint của bảng `muc_kho` trên các tệp `meditrace.db` cũ
 * (vốn chỉ cho phép `'tra-cuu'`, `'mau-van-ban'`) sang hỗ trợ thêm `'benh-nhan'` và `'nhiem-vu'`,
 * bảo toàn toàn bộ dữ liệu cũ và trạng thái `PRAGMA foreign_keys`.
 */
export function damBaoKhoMoRong(targetDb: DatabaseSync): boolean {
  const meta = targetDb
    .prepare("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'muc_kho'")
    .get() as { sql?: string } | undefined;

  if (!meta?.sql) {
    targetDb.exec(`
      CREATE TABLE IF NOT EXISTS muc_kho (
        nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
        kho            TEXT    NOT NULL CHECK (kho IN ('tra-cuu', 'mau-van-ban', 'benh-nhan', 'nhiem-vu')),
        thu_tu         INTEGER NOT NULL,
        du_lieu        TEXT    NOT NULL CHECK (json_valid(du_lieu)),
        PRIMARY KEY (nguoi_dung_id, kho, thu_tu)
      );
    `);
    return true;
  }

  if (meta.sql.includes("'benh-nhan'") && meta.sql.includes("'nhiem-vu'")) {
    return false;
  }

  const fkRow = targetDb.prepare("PRAGMA foreign_keys").get() as { foreign_keys?: number } | undefined;
  const fkWasOn = Boolean(fkRow?.foreign_keys);
  if (fkWasOn) targetDb.exec("PRAGMA foreign_keys = OFF;");
  try {
    targetDb.exec("BEGIN IMMEDIATE");
    try {
      targetDb.exec(`
        DROP TABLE IF EXISTS muc_kho_new;
        CREATE TABLE muc_kho_new (
          nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
          kho            TEXT    NOT NULL CHECK (kho IN ('tra-cuu', 'mau-van-ban', 'benh-nhan', 'nhiem-vu')),
          thu_tu         INTEGER NOT NULL,
          du_lieu        TEXT    NOT NULL CHECK (json_valid(du_lieu)),
          PRIMARY KEY (nguoi_dung_id, kho, thu_tu)
        );
        INSERT INTO muc_kho_new (nguoi_dung_id, kho, thu_tu, du_lieu)
          SELECT nguoi_dung_id, kho, thu_tu, du_lieu FROM muc_kho;
        DROP TABLE muc_kho;
        ALTER TABLE muc_kho_new RENAME TO muc_kho;
      `);
      targetDb.exec("COMMIT");
    } catch (err) {
      targetDb.exec("ROLLBACK");
      throw err;
    }
  } finally {
    if (fkWasOn) targetDb.exec("PRAGMA foreign_keys = ON;");
  }
  return true;
}

export const db = new DatabaseSync(TEP_DB);
db.exec("PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 3000; PRAGMA foreign_keys = ON;");
const TEP_SCHEMA = fs.existsSync(path.join(process.cwd(), "db", "schema.sql"))
  ? path.join(process.cwd(), "db", "schema.sql")
  : path.join(process.cwd(), "web", "db", "schema.sql");
db.exec(fs.readFileSync(TEP_SCHEMA, "utf-8"));
damBaoKhoMoRong(db);
// Đảm bảo migration bảng + trigger `worm_signoff` cho cả các tệp DB cũ đã tồn tại từ trước
damBaoBangWorm(db);
// Phiên chép âm (ASR) của dịch vụ Python gắn với người tạo: chặn dùng mã phiên của bác sĩ khác.
db.exec(`
  CREATE TABLE IF NOT EXISTS phien_asr (
    phien          TEXT    PRIMARY KEY,
    nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
    tao_luc        INTEGER NOT NULL
  );
`);

export function ganPhienAsr(uid: number, phien: string): void {
  db.prepare(
    `INSERT INTO phien_asr (phien, nguoi_dung_id, tao_luc) VALUES (?, ?, ?)
     ON CONFLICT (phien) DO NOTHING`,
  ).run(phien, uid, Date.now());
}

/** `true` chỉ khi phiên tồn tại và do chính `uid` tạo (phiên lạ hoặc của người khác đều `false`). */
export function phienAsrCuaNguoiDung(uid: number, phien: string): boolean {
  return Boolean(db.prepare("SELECT 1 FROM phien_asr WHERE phien = ? AND nguoi_dung_id = ?").get(phien, uid));
}

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
export const TEN_KHO = ["ca-kham", "tra-cuu", "mau-van-ban", "benh-nhan", "nhiem-vu"] as const;
export type TenKho = (typeof TEN_KHO)[number];
export const laTenKho = (t: string): t is TenKho => (TEN_KHO as readonly string[]).includes(t);

function mocLuu(uid: number, kho: TenKho): number {
  const r = db.prepare("SELECT luu_luc FROM moc_luu WHERE nguoi_dung_id = ? AND kho = ?").get(uid, kho) as
    | { luu_luc: number }
    | undefined;
  return r?.luu_luc || 0;
}

/**
 * Đọc một kho của một người, cùng dạng { sessions, savedAt } mà giao diện đang dùng.
 * Kho ca khám kèm `updatedAt` (id -> cap_nhat_luc) để giao diện gửi lại làm khoá lạc quan.
 */
export function docKho(
  uid: number,
  kho: TenKho,
): { sessions: unknown[]; savedAt: number; updatedAt?: Record<string, number> } {
  if (kho === "ca-kham") {
    const dong = db
      .prepare("SELECT id, du_lieu, cap_nhat_luc FROM ca_kham WHERE nguoi_dung_id = ? ORDER BY thu_tu")
      .all(uid) as Array<{ id: string; du_lieu: string; cap_nhat_luc: number }>;
    return {
      sessions: dong.map((d) => JSON.parse(d.du_lieu)),
      savedAt: mocLuu(uid, kho),
      updatedAt: Object.fromEntries(dong.map((d) => [d.id, d.cap_nhat_luc])),
    };
  }
  const dong = db.prepare("SELECT du_lieu FROM muc_kho WHERE nguoi_dung_id = ? AND kho = ? ORDER BY thu_tu").all(uid, kho);
  return { sessions: (dong as { du_lieu: string }[]).map((d) => JSON.parse(d.du_lieu)), savedAt: mocLuu(uid, kho) };
}

export interface TuyChonGhiKho {
  /** id -> cap_nhat_luc mà giao diện đã thấy lần cuối (khoá lạc quan). Có trường này là giao thức mới. */
  baseUpdatedAt?: Record<string, number> | null;
  /** Ca bị xoá CÓ CHỦ ĐÍCH ở giao diện. Ca vắng mặt khỏi danh sách nhưng không có ở đây thì giữ nguyên. */
  deletedIds?: string[] | null;
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
 * Ghi cả kho của một người bằng danh sách mới.
 * Với kho ca khám: KHÔNG xoá ca vắng mặt trong danh sách (máy khác có thể vừa tạo), chỉ xoá ca trong
 * `deletedIds`; nếu có `baseUpdatedAt` thì ca nào trên máy chủ đã mới hơn bản giao diện thấy -> 409, không ghi gì.
 */
export function ghiKho(
  uid: number,
  kho: TenKho,
  ds: unknown[],
  savedAt?: number,
  tuyChon?: TuyChonGhiKho,
): { updatedAt?: Record<string, number> } {
  const bay = Date.now();
  return giaoDich(() => {
    luuBanSaoNeuToiHan(uid, kho, bay);
    let updatedAt: Record<string, number> | undefined;

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
      const base =
        tuyChon?.baseUpdatedAt && typeof tuyChon.baseUpdatedAt === "object" && !Array.isArray(tuyChon.baseUpdatedAt)
          ? tuyChon.baseUpdatedAt
          : null;
      const moiHonBase = (id: string, capNhatLuc: number) => {
        if (!base) return false; // giao diện cũ: không khoá (nhưng cũng không còn xoá ngầm)
        const b = Number(base[id]);
        return !Number.isFinite(b) || b < capNhatLuc;
      };

      // Bước 1: kiểm tra toàn bộ trước khi ghi để 409 không để lại nửa chừng.
      const xungDot: string[] = [];
      const daThay = new Set<string>();
      for (const ca of ds as any[]) {
        const id = chuoi(ca?.id, 100);
        if (!id || daThay.has(id)) throw Object.assign(new Error("Ca khám thiếu id hoặc trùng id"), { ma: 400 });
        daThay.add(id);
        const cu = coSan.get(id);
        if (cu && cu.du_lieu !== JSON.stringify(ca) && moiHonBase(id, cu.cap_nhat_luc)) xungDot.push(id);
      }
      const canXoa = (Array.isArray(tuyChon?.deletedIds) ? tuyChon!.deletedIds! : [])
        .map((x) => chuoi(x, 100))
        .filter((x): x is string => Boolean(x) && !daThay.has(x as string) && coSan.has(x as string));
      for (const id of canXoa) {
        // Xoá ca mà máy khác vừa sửa sau lần giao diện này thấy -> xung đột, không xoá.
        const b = Number(base?.[id]);
        if (!Number.isFinite(b) || b < coSan.get(id)!.cap_nhat_luc) xungDot.push(id);
      }
      if (xungDot.length) {
        throw Object.assign(new Error("Ca khám trên máy chủ đã được cập nhật mới hơn (xung đột phiên bản)."), {
          ma: 409,
          status: 409,
          code: "conflict_stale_version",
          conflicts: xungDot,
          updatedAt: Object.fromEntries([...coSan.values()].map((d) => [d.id, d.cap_nhat_luc])),
        });
      }

      // Bước 2: ghi.
      updatedAt = {};
      ds.forEach((ca: any, i) => {
        const id = chuoi(ca?.id, 100)!;
        conLai.add(id);
        const json = JSON.stringify(ca);
        const ten = chuoi(ca.patientIdentifier);
        const ngay = chuoi(ca.date, 40);
        const cu = coSan.get(id);
        let luc = cu?.cap_nhat_luc ?? bay;
        if (!cu) them.run(uid, id, i, ten, ngay, json, bay, bay);
        else if (cu.du_lieu !== json) {
          luc = Math.max(bay, cu.cap_nhat_luc + 1);
          sua.run(i, ten, ngay, json, luc, uid, id);
        } else doiThuTu.run(i, uid, id);
        updatedAt![id] = luc;
      });
      const xoa = db.prepare("DELETE FROM ca_kham WHERE nguoi_dung_id = ? AND id = ?");
      for (const id of canXoa) xoa.run(uid, id);
      for (const d of coSan.values()) if (!conLai.has(d.id) && !canXoa.includes(d.id)) updatedAt[d.id] = d.cap_nhat_luc;
    } else {
      const chuoiMuc = ds.map((m) => {
        const j = JSON.stringify(m);
        if (typeof j !== "string") {
          throw Object.assign(new Error("Mục dữ liệu trong kho không hợp lệ"), { ma: 400, status: 400 });
        }
        return j;
      });
      db.prepare("DELETE FROM muc_kho WHERE nguoi_dung_id = ? AND kho = ?").run(uid, kho);
      const them = db.prepare("INSERT INTO muc_kho (nguoi_dung_id, kho, thu_tu, du_lieu) VALUES (?, ?, ?, ?)");
      chuoiMuc.forEach((json, i) => them.run(uid, kho, i, json));
    }

    db.prepare(
      `INSERT INTO moc_luu (nguoi_dung_id, kho, luu_luc) VALUES (?, ?, ?)
       ON CONFLICT (nguoi_dung_id, kho) DO UPDATE SET luu_luc = excluded.luu_luc`,
    ).run(uid, kho, Number(savedAt) || bay);
    return updatedAt ? { updatedAt } : {};
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

/** Đọc MỘT ca khám đã lưu của đúng người dùng `uid` (khoá chính (nguoi_dung_id, id)); không có thì `null`. */
export function docMotCaKham(uid: number, id: string): { duLieu: unknown; capNhatLuc: number } | null {
  const r = db.prepare("SELECT du_lieu, cap_nhat_luc FROM ca_kham WHERE nguoi_dung_id = ? AND id = ?").get(uid, id) as
    | { du_lieu: string; cap_nhat_luc: number }
    | undefined;
  if (!r) return null;
  try {
    return { duLieu: JSON.parse(r.du_lieu), capNhatLuc: r.cap_nhat_luc };
  } catch {
    return { duLieu: null, capNhatLuc: r.cap_nhat_luc };
  }
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
