/**
 * Hàng đợi bền cho việc của trợ lý nhiều tác tử. Cùng kiểu với hang-doi.ts: nhận một DatabaseSync,
 * tự tạo bảng, giao dịch BEGIN IMMEDIATE khi nhận việc. Tiến trình (kế hoạch + các bước đã xong) được
 * ghi xuống sau mỗi bước, nên khởi động lại giữa chừng thì chạy tiếp, không lặp bước đã trả tiền.
 */
import type { DatabaseSync } from "node:sqlite";
import type { KetQuaTroLy, TacTuMa, TienTrinh, YeuCauTroLy } from "./kieu";

export type ViecNhan = { id: number; nguoiDungId: number; yeuCau: YeuCauTroLy; tienTrinh: TienTrinh | null };

export type TrangThaiViec = {
  trangThai: string;
  tienTrinh: TienTrinh | null;
  ketQua?: KetQuaTroLy;
  ma?: string;
  taoLuc: number;
};

export type KhoViec = {
  them(nguoiDungId: number, khoaTrung: string, yeuCau: YeuCauTroLy): number;
  layViecTiepTheo(toiDaDongThoi: number): ViecNhan | null;
  ghiTienTrinh(id: number, tt: TienTrinh): void;
  xong(id: number, kq: KetQuaTroLy): void;
  loi(id: number, ma: string): void;
  huy(id: number, nguoiDungId: number): boolean;
  daHuy(id: number): boolean;
  khoiPhuc(toiDaLanThuNgoai?: number, toiDaLanThuTaiCho?: number): { chayLai: number; thatBai: number };
  trangThai(id: number, nguoiDungId: number): TrangThaiViec | null;
  xoa(id: number, nguoiDungId: number): void;
  donViecCu(tuoiToiDaMs: number): number;
};

/** Tác tử gọi mô hình ngoài (tốn tiền). Hai tác tử luật tại chỗ không nằm trong đây. */
const TAC_TU_TON_TIEN: ReadonlySet<TacTuMa> = new Set(["tim_kiem", "tra_loi", "doi_chieu", "dieu_phoi"]);

const doc = <T>(s: unknown): T | null => {
  if (typeof s !== "string" || !s) return null;
  try {
    return JSON.parse(s) as T;
  } catch {
    return null;
  }
};

export function taoKhoViec(db: DatabaseSync): KhoViec {
  db.exec(`
    CREATE TABLE IF NOT EXISTS viec_tro_ly (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nguoi_dung_id INTEGER NOT NULL,
      khoa_trung TEXT NOT NULL,
      yeu_cau TEXT NOT NULL,
      tien_trinh TEXT,
      ket_qua TEXT,
      trang_thai TEXT NOT NULL DEFAULT 'cho_chay',
      so_lan_thu INTEGER NOT NULL DEFAULT 0,
      ma_loi TEXT,
      tao_luc INTEGER NOT NULL,
      bat_dau_luc INTEGER,
      hoan_tat_luc INTEGER
    );
    CREATE INDEX IF NOT EXISTS idx_viec_tro_ly_tt ON viec_tro_ly(trang_thai, id);
  `);
  const cols = db.prepare("PRAGMA table_info(viec_tro_ly)").all() as Array<{ name: string }>;
  if (!cols.some((c) => c.name === "hoan_tat_luc")) {
    db.exec("ALTER TABLE viec_tro_ly ADD COLUMN hoan_tat_luc INTEGER;");
  }

  const giaoDich = <T>(f: () => T): T => {
    db.exec("BEGIN IMMEDIATE");
    try {
      const r = f();
      db.exec("COMMIT");
      return r;
    } catch (e) {
      db.exec("ROLLBACK");
      throw e;
    }
  };

  return {
    them(nguoiDungId, khoaTrung, yeuCau) {
      return giaoDich(() => {
        const cu = db
          .prepare(
            "SELECT id FROM viec_tro_ly WHERE nguoi_dung_id = ? AND khoa_trung = ? AND trang_thai IN ('cho_chay','dang_chay') ORDER BY id LIMIT 1",
          )
          .get(nguoiDungId, khoaTrung) as { id: number } | undefined;
        if (cu) return Number(cu.id);
        const r = db
          .prepare("INSERT INTO viec_tro_ly (nguoi_dung_id, khoa_trung, yeu_cau, tao_luc) VALUES (?, ?, ?, ?)")
          .run(nguoiDungId, khoaTrung, JSON.stringify(yeuCau), Date.now());
        return Number(r.lastInsertRowid);
      });
    },

    layViecTiepTheo(toiDaDongThoi) {
      return giaoDich(() => {
        const dang = db.prepare("SELECT COUNT(*) AS n FROM viec_tro_ly WHERE trang_thai = 'dang_chay'").get() as { n: number };
        if (Number(dang.n) >= toiDaDongThoi) return null;
        const h = db
          .prepare("SELECT id, nguoi_dung_id, yeu_cau, tien_trinh FROM viec_tro_ly WHERE trang_thai = 'cho_chay' ORDER BY id LIMIT 1")
          .get() as { id: number; nguoi_dung_id: number; yeu_cau: string; tien_trinh: string | null } | undefined;
        if (!h) return null;
        db.prepare("UPDATE viec_tro_ly SET trang_thai = 'dang_chay', bat_dau_luc = ? WHERE id = ?").run(Date.now(), h.id);
        const yeuCau = doc<YeuCauTroLy>(h.yeu_cau);
        if (!yeuCau) {
          db.prepare("UPDATE viec_tro_ly SET trang_thai = 'that_bai', ma_loi = 'yeu_cau_hong', hoan_tat_luc = ? WHERE id = ?").run(
            Date.now(),
            h.id,
          );
          return null;
        }
        return { id: Number(h.id), nguoiDungId: Number(h.nguoi_dung_id), yeuCau, tienTrinh: doc<TienTrinh>(h.tien_trinh) };
      });
    },

    ghiTienTrinh(id, tt) {
      db.prepare("UPDATE viec_tro_ly SET tien_trinh = ? WHERE id = ? AND trang_thai != 'da_huy'").run(JSON.stringify(tt), id);
    },

    xong(id, kq) {
      db.prepare("UPDATE viec_tro_ly SET trang_thai = 'xong', ket_qua = ?, hoan_tat_luc = ? WHERE id = ? AND trang_thai != 'da_huy'").run(
        JSON.stringify(kq),
        Date.now(),
        id,
      );
    },

    loi(id, ma) {
      db.prepare("UPDATE viec_tro_ly SET trang_thai = 'that_bai', ma_loi = ?, hoan_tat_luc = ? WHERE id = ? AND trang_thai != 'da_huy'").run(
        ma,
        Date.now(),
        id,
      );
    },

    huy(id, nguoiDungId) {
      return giaoDich(() => {
        const co = db
          .prepare("SELECT trang_thai FROM viec_tro_ly WHERE id = ? AND nguoi_dung_id = ?")
          .get(id, nguoiDungId) as { trang_thai: string } | undefined;
        if (!co) return false;
        db.prepare("UPDATE viec_tro_ly SET trang_thai = 'da_huy', ma_loi = 'da_huy', hoan_tat_luc = ? WHERE id = ? AND nguoi_dung_id = ?").run(
          Date.now(),
          id,
          nguoiDungId,
        );
        return true;
      });
    },

    daHuy(id) {
      const r = db.prepare("SELECT trang_thai FROM viec_tro_ly WHERE id = ?").get(id) as { trang_thai: string } | undefined;
      return r?.trang_thai === "da_huy";
    },

    khoiPhuc(toiDaLanThuNgoai = 1, toiDaLanThuTaiCho = 2) {
      return giaoDich(() => {
        const rows = db
          .prepare("SELECT id, tien_trinh, so_lan_thu FROM viec_tro_ly WHERE trang_thai = 'dang_chay'")
          .all() as Array<{ id: number; tien_trinh: string | null; so_lan_thu: number }>;
        let chayLai = 0;
        let thatBai = 0;
        for (const r of rows) {
          const tt = doc<TienTrinh>(r.tien_trinh);
          // Tính cả Boolean(tt?.dieuPhoi) vào cờ tonTien để việc đã gọi điều phối ngoài không vượt ngưỡng retry trả phí
          const tonTien =
            Boolean(tt?.dieuPhoi) ||
            !!tt?.buoc?.some((b) => TAC_TU_TON_TIEN.has(b.tacTu) && (b.trangThai === "xong" || b.trangThai === "dang"));
          const nguong = tonTien ? toiDaLanThuNgoai : toiDaLanThuTaiCho;
          if (Number(r.so_lan_thu) >= nguong) {
            db.prepare(
              "UPDATE viec_tro_ly SET trang_thai = 'that_bai', ma_loi = 'crash_recovery_exhausted', hoan_tat_luc = ? WHERE id = ?",
            ).run(Date.now(), r.id);
            thatBai++;
          } else {
            db.prepare("UPDATE viec_tro_ly SET trang_thai = 'cho_chay', so_lan_thu = so_lan_thu + 1 WHERE id = ?").run(r.id);
            chayLai++;
          }
        }
        return { chayLai, thatBai };
      });
    },

    trangThai(id, nguoiDungId) {
      const r = db
        .prepare("SELECT trang_thai, tien_trinh, ket_qua, ma_loi, tao_luc FROM viec_tro_ly WHERE id = ? AND nguoi_dung_id = ?")
        .get(id, nguoiDungId) as
        | { trang_thai: string; tien_trinh: string | null; ket_qua: string | null; ma_loi: string | null; tao_luc: number }
        | undefined;
      if (!r) return null;
      const ketQua = doc<KetQuaTroLy>(r.ket_qua);
      return {
        trangThai: r.trang_thai,
        tienTrinh: doc<TienTrinh>(r.tien_trinh),
        ...(ketQua ? { ketQua } : {}),
        ...(r.ma_loi ? { ma: r.ma_loi } : {}),
        taoLuc: Number(r.tao_luc),
      };
    },

    xoa(id, nguoiDungId) {
      db.prepare("DELETE FROM viec_tro_ly WHERE id = ? AND nguoi_dung_id = ?").run(id, nguoiDungId);
    },

    donViecCu(tuoiToiDaMs) {
      const r = db
        .prepare("DELETE FROM viec_tro_ly WHERE trang_thai IN ('xong','that_bai','da_huy') AND COALESCE(hoan_tat_luc, tao_luc) < ?")
        .run(Date.now() - tuoiToiDaMs);
      return Number(r.changes);
    },
  };
}
