import crypto from "crypto";
import fs from "fs";
import path from "path";
import type { DatabaseSync } from "node:sqlite";
import type { ApiSignOffResponse } from "../src/types/api-contract";

export const GENESIS_HASH_WORM = crypto
  .createHash("sha256")
  .update("MEDITRACE_SENTINEL_GENESIS_CIRCULAR_46_2018_TT_BYT")
  .digest("hex");

export interface WormSignOffInput {
  sessionId: string;
  userId: number | null;
  tongMenhDe: number;
  soGiu: number;
  soSua: number;
  soBo: number;
  tyLeCoNguon: number;
  contentHash: string;
  soChuaXacNhan?: number;
}

export interface WormSignOffRow {
  seq: number;
  timestamp: string;
  user_id: number | null;
  event: string;
  session_id: string;
  tong_menh_de: number;
  so_giu: number;
  so_sua: number;
  so_bo: number;
  ty_le_co_nguon: number;
  content_hash: string;
  prev_hash: string;
  curr_hash: string;
}

export interface WormAnchor {
  firstSeq: number;
  firstPrevHash: string;
  firstHash: string;
  lastSeq: number;
  lastHash: string;
  totalRecords: number;
  updatedAt: string;
}

/**
 * Migration tự động đảm bảo bảng, cột `nguoi_dung_id`, chỉ mục và 2 trigger WORM bất biến
 * luôn có mặt kể cả trên các tệp SQLite cũ tạo trước khi có bảng `worm_signoff`.
 */
export function damBaoBangWorm(db: DatabaseSync): void {
  db.exec(`
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
  `);
  const cols = db.prepare("PRAGMA table_info(worm_signoff)").all() as Array<{ name: string }>;
  if (!cols.some((c) => c.name === "nguoi_dung_id")) {
    db.exec("ALTER TABLE worm_signoff ADD COLUMN nguoi_dung_id INTEGER REFERENCES nguoi_dung(id) ON DELETE RESTRICT;");
  }
  db.exec(`
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
  `);
}

function timDuongDanDb(db: DatabaseSync): string | undefined {
  try {
    const ds = db.prepare("PRAGMA database_list").all() as Array<{ name: string; file: string }>;
    const main = ds.find((d) => d.name === "main");
    return main?.file ? String(main.file) : undefined;
  } catch {
    return undefined;
  }
}

function docCuoiTuJsonl(jsonlPath?: string): { prevHash: string; nextSeq: number } {
  if (!jsonlPath || !fs.existsSync(jsonlPath)) {
    return { prevHash: GENESIS_HASH_WORM, nextSeq: 1 };
  }
  const lines = fs.readFileSync(jsonlPath, "utf8").split("\n").filter((l) => l.trim());
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const last = JSON.parse(lines[i]);
      if (last && typeof last.curr_hash === "string") {
        return {
          prevHash: last.curr_hash,
          nextSeq: Number(last.seq || i + 1) + 1,
        };
      }
    } catch {
      // Bỏ qua dòng hỏng, quét ngược tìm dòng hợp lệ gần nhất
    }
  }
  return { prevHash: GENESIS_HASH_WORM, nextSeq: 1 };
}

function coMocJsonlTruocDo(jsonlPath: string | undefined, targetSeq: number, targetPrevHash: string): boolean {
  if (!jsonlPath || !fs.existsSync(jsonlPath)) return false;
  const lines = fs.readFileSync(jsonlPath, "utf8").split("\n").filter((l) => l.trim());
  for (let i = 0; i < lines.length; i++) {
    try {
      const row = JSON.parse(lines[i]);
      const seq = Number(row?.seq || i + 1);
      if (seq === targetSeq - 1 && row?.curr_hash === targetPrevHash) return true;
    } catch {}
  }
  return false;
}

function loiDauVao(thongDiep: string): Error {
  const e: any = new Error(thongDiep);
  e.status = 400;
  return e;
}

function kiemTraInputSignOff(input: WormSignOffInput): string {
  const sessionId = typeof input.sessionId === "string" ? input.sessionId.trim() : "";
  if (!sessionId || sessionId.length > 200) {
    throw loiDauVao("Gia tri khong hop le cho sessionId: rong hoac vuot 200 ky tu");
  }

  const cacTruongNguyen = [
    ["tongMenhDe", input.tongMenhDe],
    ["soGiu", input.soGiu],
    ["soSua", input.soSua],
    ["soBo", input.soBo],
  ] as const;
  for (const [k, v] of cacTruongNguyen) {
    if (typeof v !== "number" || !Number.isInteger(v) || v < 0) {
      throw loiDauVao(`Gia tri khong hop le cho ${k}: ${v} (phai la so nguyen >= 0)`);
    }
  }
  if (input.tongMenhDe < 1) {
    throw loiDauVao("Gia tri khong hop le cho tongMenhDe: 0 (khong duoc hoan tat/ky duyet ho so khi chua co menh de co can cu)");
  }
  if (input.soBo >= input.tongMenhDe) {
    throw loiDauVao(
      `Gia tri khong hop le: tat ca menh de deu bi bo (${input.soBo}/${input.tongMenhDe}), ho so khong con can cu hop le`,
    );
  }
  if (input.soChuaXacNhan !== undefined) {
    if (typeof input.soChuaXacNhan !== "number" || !Number.isInteger(input.soChuaXacNhan) || input.soChuaXacNhan !== 0) {
      throw loiDauVao(
        `Gia tri khong hop le cho soChuaXacNhan: ${input.soChuaXacNhan} (con muc can bac si xac nhan chua xu ly, khong duoc ky duyet)`,
      );
    }
  }
  if (input.soGiu + input.soSua + input.soBo > input.tongMenhDe) {
    throw loiDauVao(
      `Gia tri khong hop le: soGiu + soSua + soBo (${input.soGiu + input.soSua + input.soBo}) vuot tongMenhDe (${input.tongMenhDe})`,
    );
  }
  if (
    typeof input.tyLeCoNguon !== "number" ||
    !Number.isFinite(input.tyLeCoNguon) ||
    input.tyLeCoNguon <= 0 ||
    input.tyLeCoNguon > 100
  ) {
    throw loiDauVao(`Gia tri khong hop le cho tyLeCoNguon: ${input.tyLeCoNguon} (phai trong khoang (0..100], khong duoc thieu can cu)`);
  }
  const contentHash = typeof input.contentHash === "string" ? input.contentHash.trim() : "";
  if (!contentHash || contentHash.length > 256) {
    throw loiDauVao("Gia tri khong hop le cho contentHash: khong duoc rong hoac vuot 256 ky tu");
  }
  return contentHash;
}

type TrangThaiAnchor =
  | { trangThai: "chua_co" }
  | { trangThai: "hop_le"; neo: WormAnchor }
  | { trangThai: "bi_sua_doi"; lyDo: string };

export function taoKhoWorm(db: DatabaseSync, wormJsonlPath?: string, anchorPathOverride?: string) {
  damBaoBangWorm(db);

  const dbFilePath = timDuongDanDb(db);
  const anchorPath =
    anchorPathOverride ||
    (dbFilePath ? `${dbFilePath}.anchor.json` : wormJsonlPath ? `${wormJsonlPath}.anchor.json` : undefined);

  let neoTrongRam: WormAnchor | null = null;

  function docTrangThaiAnchor(): TrangThaiAnchor {
    if (anchorPath && fs.existsSync(anchorPath)) {
      try {
        const j = JSON.parse(fs.readFileSync(anchorPath, "utf8"));
        if (
          j &&
          Number.isInteger(j.firstSeq) &&
          j.firstSeq >= 1 &&
          typeof j.firstPrevHash === "string" &&
          j.firstPrevHash.length > 0 &&
          typeof j.firstHash === "string" &&
          j.firstHash.length > 0 &&
          Number.isInteger(j.lastSeq) &&
          j.lastSeq >= j.firstSeq &&
          typeof j.lastHash === "string" &&
          j.lastHash.length > 0 &&
          Number.isInteger(j.totalRecords) &&
          j.totalRecords >= 1
        ) {
          return { trangThai: "hop_le", neo: j as WormAnchor };
        }
        return { trangThai: "bi_sua_doi", lyDo: "Phat hien tep neo .anchor.json sai dinh dang hoac bi sua doi" };
      } catch {
        return { trangThai: "bi_sua_doi", lyDo: "Phat hien tep neo .anchor.json bi hong JSON hoac bi sua doi" };
      }
    }
    if (neoTrongRam) return { trangThai: "hop_le", neo: neoTrongRam };
    return { trangThai: "chua_co" };
  }

  function ghiAnchor(neo: WormAnchor): void {
    neoTrongRam = neo;
    if (!anchorPath) return;
    fs.mkdirSync(path.dirname(anchorPath), { recursive: true });
    const tam = `${anchorPath}.tmp.${process.pid}`;
    fs.writeFileSync(tam, JSON.stringify(neo, null, 2) + "\n", "utf8");
    fs.renameSync(tam, anchorPath);
  }

  // Chỉ khởi tạo .anchor.json khi tệp neo CHƯA TỒN TẠI (tuyệt đối không ghi đè tệp neo đã bị kẻ tấn công làm hỏng).
  if (docTrangThaiAnchor().trangThai === "chua_co") {
    const dau = db.prepare("SELECT seq, prev_hash, curr_hash FROM worm_signoff ORDER BY seq ASC LIMIT 1").get() as
      | { seq: number; prev_hash: string; curr_hash: string }
      | undefined;
    const cuoi = db.prepare("SELECT seq, curr_hash FROM worm_signoff ORDER BY seq DESC LIMIT 1").get() as
      | { seq: number; curr_hash: string }
      | undefined;
    const dem = db.prepare("SELECT COUNT(*) AS n FROM worm_signoff").get() as { n: number };
    if (dau && cuoi && Number(dem.n) > 0) {
      ghiAnchor({
        firstSeq: Number(dau.seq),
        firstPrevHash: dau.prev_hash,
        firstHash: dau.curr_hash,
        lastSeq: Number(cuoi.seq),
        lastHash: cuoi.curr_hash,
        totalRecords: Number(dem.n),
        updatedAt: new Date().toISOString(),
      });
    }
  }

  return {
    duongDanAnchor(): string | undefined {
      return anchorPath;
    },

    ghiSignOff(input: WormSignOffInput): ApiSignOffResponse {
      const contentHash = kiemTraInputSignOff(input);
      const sessionId = input.sessionId.trim();
      const signedAt = new Date().toISOString();
      let entry!: WormSignOffRow;
      let neoMoi!: WormAnchor;

      db.exec("BEGIN IMMEDIATE");
      try {
        const ttAnchor = docTrangThaiAnchor();
        if (ttAnchor.trangThai === "bi_sua_doi") {
          const tamperErr: any = new Error(`WORM Violation: ${ttAnchor.lyDo}`);
          tamperErr.status = 409;
          throw tamperErr;
        }
        const neoCu = ttAnchor.trangThai === "hop_le" ? ttAnchor.neo : null;
        const firstDb = db.prepare("SELECT seq, prev_hash, curr_hash FROM worm_signoff ORDER BY seq ASC LIMIT 1").get() as
          | { seq: number; prev_hash: string; curr_hash: string }
          | undefined;
        const lastDb = db.prepare("SELECT seq, curr_hash FROM worm_signoff ORDER BY seq DESC LIMIT 1").get() as
          | { seq: number; curr_hash: string }
          | undefined;
        const countRow = db.prepare("SELECT COUNT(*) AS n FROM worm_signoff").get() as { n: number };
        const soHienCo = Number(countRow.n);

        if (neoCu && neoCu.totalRecords > 0) {
          if (
            !firstDb ||
            !lastDb ||
            Number(firstDb.seq) !== neoCu.firstSeq ||
            firstDb.curr_hash !== neoCu.firstHash ||
            Number(lastDb.seq) !== neoCu.lastSeq ||
            lastDb.curr_hash !== neoCu.lastHash ||
            soHienCo !== neoCu.totalRecords
          ) {
            const tamperErr: any = new Error("WORM Violation: Chuoi ky duyet da bi cat hoac sua doi so voi tep neo (.anchor.json)");
            tamperErr.status = 409;
            throw tamperErr;
          }
        }
        if (lastDb) {
          const cuoiJsonl = docCuoiTuJsonl(wormJsonlPath);
          if (cuoiJsonl.nextSeq - 1 > Number(lastDb.seq)) {
            const tamperErr: any = new Error("WORM Violation: Chuoi SQLite bi cat duoi so voi worm_signoff_log.jsonl");
            tamperErr.status = 409;
            throw tamperErr;
          }
        }

        let prevHash = GENESIS_HASH_WORM;
        let seq = 1;
        if (lastDb) {
          prevHash = lastDb.curr_hash;
          seq = Number(lastDb.seq) + 1;
        } else {
          const legacy = docCuoiTuJsonl(wormJsonlPath);
          prevHash = legacy.prevHash;
          seq = legacy.nextSeq;
        }

        const payload = {
          seq,
          timestamp: signedAt,
          user_id: input.userId ?? null,
          event: "doctor_forensic_signoff",
          session_id: sessionId,
          tong_menh_de: input.tongMenhDe,
          so_giu: input.soGiu,
          so_sua: input.soSua,
          so_bo: input.soBo,
          ty_le_co_nguon: input.tyLeCoNguon,
          content_hash: contentHash,
          prev_hash: prevHash,
        };
        const currHash = crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
        entry = { ...payload, curr_hash: currHash };

        db.prepare(
          `INSERT INTO worm_signoff (
            seq, timestamp, nguoi_dung_id, event, session_id,
            tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
            content_hash, prev_hash, curr_hash
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        ).run(
          entry.seq,
          entry.timestamp,
          entry.user_id,
          entry.event,
          entry.session_id,
          entry.tong_menh_de,
          entry.so_giu,
          entry.so_sua,
          entry.so_bo,
          entry.ty_le_co_nguon,
          entry.content_hash,
          entry.prev_hash,
          entry.curr_hash,
        );

        neoMoi = {
          firstSeq: firstDb ? Number(firstDb.seq) : entry.seq,
          firstPrevHash: firstDb ? firstDb.prev_hash : entry.prev_hash,
          firstHash: firstDb ? firstDb.curr_hash : entry.curr_hash,
          lastSeq: entry.seq,
          lastHash: entry.curr_hash,
          totalRecords: soHienCo + 1,
          updatedAt: signedAt,
        };
        db.exec("COMMIT");
      } catch (err) {
        db.exec("ROLLBACK");
        throw err;
      }

      ghiAnchor(neoMoi);

      // Ghi song song ra JSONL để tương thích ngược với công cụ kiểm toán ngoài
      if (wormJsonlPath) {
        fs.mkdirSync(path.dirname(wormJsonlPath), { recursive: true });
        fs.appendFileSync(wormJsonlPath, JSON.stringify(entry) + "\n", "utf8");
      }

      return {
        ok: true,
        signedAt,
        tongMenhDe: entry.tong_menh_de,
        soGiu: entry.so_giu,
        soSua: entry.so_sua,
        soBo: entry.so_bo,
        tyLeCoNguon: entry.ty_le_co_nguon,
        hash: entry.curr_hash,
        wormSeq: entry.seq,
      };
    },

    docLichSuSignOff(sessionId?: string, tuyChon?: { userId?: number }): WormSignOffRow[] {
      const hasUserFilter = typeof tuyChon?.userId === "number";
      if (sessionId && hasUserFilter) {
        const sql = `SELECT seq, timestamp, nguoi_dung_id AS user_id, event, session_id,
                            tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
                            content_hash, prev_hash, curr_hash
                     FROM worm_signoff WHERE session_id = ? AND nguoi_dung_id = ? ORDER BY seq ASC`;
        return db.prepare(sql).all(sessionId, tuyChon!.userId!) as unknown as WormSignOffRow[];
      }
      if (sessionId) {
        const sql = `SELECT seq, timestamp, nguoi_dung_id AS user_id, event, session_id,
                            tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
                            content_hash, prev_hash, curr_hash
                     FROM worm_signoff WHERE session_id = ? ORDER BY seq ASC`;
        return db.prepare(sql).all(sessionId) as unknown as WormSignOffRow[];
      }
      if (hasUserFilter) {
        const sql = `SELECT seq, timestamp, nguoi_dung_id AS user_id, event, session_id,
                            tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
                            content_hash, prev_hash, curr_hash
                     FROM worm_signoff WHERE nguoi_dung_id = ? ORDER BY seq ASC`;
        return db.prepare(sql).all(tuyChon!.userId!) as unknown as WormSignOffRow[];
      }
      const sql = `SELECT seq, timestamp, nguoi_dung_id AS user_id, event, session_id,
                          tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
                          content_hash, prev_hash, curr_hash
                   FROM worm_signoff ORDER BY seq ASC`;
      return db.prepare(sql).all() as unknown as WormSignOffRow[];
    },

    xacMinhChuoi(): { hopLe: boolean; soBanGhi: number; loi?: string } {
      const rows = this.docLichSuSignOff();
      const ttAnchor = docTrangThaiAnchor();
      if (ttAnchor.trangThai === "bi_sua_doi") {
        return { hopLe: false, soBanGhi: rows.length, loi: ttAnchor.lyDo };
      }
      const neo = ttAnchor.trangThai === "hop_le" ? ttAnchor.neo : null;

      if (!rows.length) {
        if (neo && neo.totalRecords > 0) {
          return {
            hopLe: false,
            soBanGhi: 0,
            loi: `Phat hien cat duoi / xoa trang chuoi WORM: tep neo ghi nhan ${neo.totalRecords} ban ghi (seq cuoi=${neo.lastSeq})`,
          };
        }
        return { hopLe: true, soBanGhi: 0 };
      }

      // 1. Kiểm tra cắt đầu chuỗi (head-truncation) qua tệp neo .anchor.json và GENESIS_HASH_WORM
      if (neo) {
        if (rows[0].seq !== neo.firstSeq || rows[0].prev_hash !== neo.firstPrevHash || rows[0].curr_hash !== neo.firstHash) {
          return {
            hopLe: false,
            soBanGhi: rows.length,
            loi: `Phat hien cat dau chuoi: ky vong seq dau=${neo.firstSeq}, thuc te seq=${rows[0].seq}`,
          };
        }
      } else if (rows[0].seq !== 1 && !coMocJsonlTruocDo(wormJsonlPath, rows[0].seq, rows[0].prev_hash)) {
        return {
          hopLe: false,
          soBanGhi: rows.length,
          loi: `Phat hien cat dau chuoi: thieu ban ghi khoi nguyen (seq dau=${rows[0].seq})`,
        };
      }

      // 2. Kiểm tra tính liên tục của seq và băm mật mã từng mắt xích
      let expectedPrev = rows[0].seq === 1 ? GENESIS_HASH_WORM : neo ? neo.firstPrevHash : rows[0].prev_hash;
      let expectedSeq = rows[0].seq;
      for (const r of rows) {
        if (r.seq !== expectedSeq) {
          return { hopLe: false, soBanGhi: rows.length, loi: `Gian doan seq tai seq=${r.seq} (ky vong ${expectedSeq})` };
        }
        if (r.prev_hash !== expectedPrev) {
          return { hopLe: false, soBanGhi: rows.length, loi: `Dut chuoi tai seq=${r.seq}` };
        }
        const payload = {
          seq: r.seq,
          timestamp: r.timestamp,
          user_id: r.user_id,
          event: r.event,
          session_id: r.session_id,
          tong_menh_de: r.tong_menh_de,
          so_giu: r.so_giu,
          so_sua: r.so_sua,
          so_bo: r.so_bo,
          ty_le_co_nguon: r.ty_le_co_nguon,
          content_hash: r.content_hash,
          prev_hash: r.prev_hash,
        };
        const check = crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
        if (check !== r.curr_hash) {
          return { hopLe: false, soBanGhi: rows.length, loi: `Sai hash tai seq=${r.seq}` };
        }
        expectedPrev = r.curr_hash;
        expectedSeq = r.seq + 1;
      }

      // 3. Kiểm tra cắt đuôi chuỗi (tail-truncation) qua tệp neo .anchor.json và nhật ký đối chứng .jsonl
      const last = rows[rows.length - 1];
      if (neo) {
        if (last.seq !== neo.lastSeq || last.curr_hash !== neo.lastHash || rows.length !== neo.totalRecords) {
          return {
            hopLe: false,
            soBanGhi: rows.length,
            loi: `Phat hien cat duoi chuoi: ky vong seq cuoi=${neo.lastSeq}, thuc te seq=${last.seq}`,
          };
        }
      }
      const cuoiJsonl = docCuoiTuJsonl(wormJsonlPath);
      if (cuoiJsonl.nextSeq - 1 > last.seq) {
        return {
          hopLe: false,
          soBanGhi: rows.length,
          loi: `Phat hien cat duoi chuoi so voi JSONL: ky vong seq cuoi=${cuoiJsonl.nextSeq - 1}, thuc te seq=${last.seq}`,
        };
      }

      return { hopLe: true, soBanGhi: rows.length };
    },
  };
}
