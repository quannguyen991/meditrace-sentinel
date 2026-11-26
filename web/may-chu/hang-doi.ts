/**
 * HÀNG ĐỢI VIỆC NỀN BỀN VỮNG trên SQLite (bảng viec_nen).
 */
import type { DatabaseSync } from "node:sqlite";

export type TrangThaiViec = "cho_chay" | "dang_chay" | "xong" | "that_bai";

export interface ViecDangChay {
  id: number;
  nguoiDungId: number;
  taiTrong: string;
}

export interface TrangThaiViecTra {
  trangThai: TrangThaiViec;
  /** Mốc thêm việc (ms từ 1970). */
  taoLuc: number;
  ketQua?: string;
  ma?: string;
}

export interface HangDoi {
  /** Thêm việc. Nếu `khoaTrung` đã có việc chưa kết thúc (cho_chay hoặc dang_chay) thì trả id đó. */
  them(nguoiDungId: number, khoaTrung: string, taiTrong: string): number;
  /** Lấy việc chờ lâu nhất, đánh dấu dang_chay trong MỘT giao dịch nguyên tử. Hết việc: null. */
  layViecTiepTheo(): ViecDangChay | null;
  xong(id: number, ketQua: string): void;
  loi(id: number, ma: string): void;
  /** Gọi một lần khi máy chủ khởi động. */
  khoiPhucSauKhoiDong(toiDaLanThu?: number): { chayLai: number; thatBai: number };
  /** Chỉ trả khi `nguoiDungId` đúng là chủ của việc, ngược lại null. */
  trangThai(id: number, nguoiDungId: number): TrangThaiViecTra | null;
  /** Số việc chưa kết thúc (cho_chay hoặc dang_chay) được thêm TRƯỚC việc `id`. */
  soViecTruoc(id: number): number;
  /** Xoá việc của `nguoiDungId`. */
  xoa(id: number, nguoiDungId: number): void;
  /** Xoá việc đã kết thúc (xong hoặc that_bai) cũ hơn `tuoiToiDaMs`. Trả số dòng đã xoá. */
  donViecCu(tuoiToiDaMs: number): number;
}

const DDL = `
CREATE TABLE IF NOT EXISTS viec_nen (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  nguoi_dung_id INTEGER NOT NULL,
  khoa_trung    TEXT    NOT NULL,
  tai_trong     TEXT    NOT NULL,
  trang_thai    TEXT    NOT NULL DEFAULT 'cho_chay'
                CHECK (trang_thai IN ('cho_chay','dang_chay','xong','that_bai')),
  so_lan_thu    INTEGER NOT NULL DEFAULT 0,
  ket_qua       TEXT,
  ma_loi        TEXT,
  tao_luc       INTEGER NOT NULL,
  bat_dau_luc   INTEGER,
  hoan_tat_luc  INTEGER
);
CREATE INDEX IF NOT EXISTS viec_nen_cho ON viec_nen(trang_thai, tao_luc);
CREATE INDEX IF NOT EXISTS viec_nen_khoa ON viec_nen(nguoi_dung_id, khoa_trung);
`;

function giaoDich<T>(db: DatabaseSync, viec: () => T): T {
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

export function taoHangDoi(db: DatabaseSync): HangDoi {
  db.exec(DDL);
  const cols = db.prepare("PRAGMA table_info(viec_nen)").all() as Array<{ name: string }>;
  if (!cols.some((c) => c.name === "hoan_tat_luc")) {
    db.exec("ALTER TABLE viec_nen ADD COLUMN hoan_tat_luc INTEGER;");
  }

  return {
    them(nguoiDungId, khoaTrung, taiTrong) {
      return giaoDich(db, () => {
        const co = db
          .prepare(
            `SELECT id FROM viec_nen
             WHERE nguoi_dung_id = ? AND khoa_trung = ? AND trang_thai IN ('cho_chay','dang_chay')
             ORDER BY id LIMIT 1`,
          )
          .get(nguoiDungId, khoaTrung) as { id: number } | undefined;
        if (co) return Number(co.id);
        const r = db
          .prepare(`INSERT INTO viec_nen (nguoi_dung_id, khoa_trung, tai_trong, tao_luc) VALUES (?, ?, ?, ?)`)
          .run(nguoiDungId, khoaTrung, taiTrong, Date.now());
        return Number(r.lastInsertRowid);
      });
    },

    layViecTiepTheo() {
      return giaoDich(db, () => {
        const h = db
          .prepare(
            `UPDATE viec_nen
             SET trang_thai = 'dang_chay', bat_dau_luc = ?, so_lan_thu = so_lan_thu + 1
             WHERE id = (SELECT id FROM viec_nen WHERE trang_thai = 'cho_chay' ORDER BY tao_luc, id LIMIT 1)
             RETURNING id, nguoi_dung_id, tai_trong`,
          )
          .get(Date.now()) as { id: number; nguoi_dung_id: number; tai_trong: string } | undefined;
        return h ? { id: Number(h.id), nguoiDungId: Number(h.nguoi_dung_id), taiTrong: h.tai_trong } : null;
      });
    },

    xong(id, ketQua) {
      db.prepare(`UPDATE viec_nen SET trang_thai = 'xong', ket_qua = ?, ma_loi = NULL, hoan_tat_luc = ? WHERE id = ?`).run(
        ketQua,
        Date.now(),
        id,
      );
    },

    loi(id, ma) {
      db.prepare(`UPDATE viec_nen SET trang_thai = 'that_bai', ma_loi = ?, hoan_tat_luc = ? WHERE id = ?`).run(ma, Date.now(), id);
    },

    khoiPhucSauKhoiDong(toiDaLanThu = 2) {
      return giaoDich(db, () => {
        const chay = db
          .prepare(`UPDATE viec_nen SET trang_thai = 'cho_chay' WHERE trang_thai = 'dang_chay' AND so_lan_thu < ?`)
          .run(toiDaLanThu);
        const het = db
          .prepare(
            `UPDATE viec_nen SET trang_thai = 'that_bai', ma_loi = 'crash_recovery_exhausted', hoan_tat_luc = ?
             WHERE trang_thai = 'dang_chay' AND so_lan_thu >= ?`,
          )
          .run(Date.now(), toiDaLanThu);
        return { chayLai: Number(chay.changes), thatBai: Number(het.changes) };
      });
    },

    trangThai(id, nguoiDungId) {
      const h = db
        .prepare(`SELECT trang_thai, ket_qua, ma_loi, tao_luc FROM viec_nen WHERE id = ? AND nguoi_dung_id = ?`)
        .get(id, nguoiDungId) as
        | { trang_thai: TrangThaiViec; ket_qua: string | null; ma_loi: string | null; tao_luc: number }
        | undefined;
      if (!h) return null;
      const ra: TrangThaiViecTra = { trangThai: h.trang_thai, taoLuc: Number(h.tao_luc) };
      if (h.ket_qua != null) ra.ketQua = h.ket_qua;
      if (h.ma_loi != null) ra.ma = h.ma_loi;
      return ra;
    },

    soViecTruoc(id) {
      const r = db
        .prepare(`SELECT COUNT(*) AS n FROM viec_nen WHERE id < ? AND trang_thai IN ('cho_chay','dang_chay')`)
        .get(id) as { n: number };
      return Number(r.n);
    },

    xoa(id, nguoiDungId) {
      db.prepare(`DELETE FROM viec_nen WHERE id = ? AND nguoi_dung_id = ?`).run(id, nguoiDungId);
    },

    donViecCu(tuoiToiDaMs) {
      const r = db
        .prepare(`DELETE FROM viec_nen WHERE trang_thai IN ('xong','that_bai') AND COALESCE(hoan_tat_luc, tao_luc) < ?`)
        .run(Date.now() - tuoiToiDaMs);
      return Number(r.changes);
    },
  };
}
