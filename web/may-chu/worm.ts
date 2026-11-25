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

export function taoKhoWorm(db: DatabaseSync, wormJsonlPath?: string) {
  return {
    ghiSignOff(input: WormSignOffInput): ApiSignOffResponse {
      const nums = [
        ["tongMenhDe", input.tongMenhDe],
        ["soGiu", input.soGiu],
        ["soSua", input.soSua],
        ["soBo", input.soBo],
        ["tyLeCoNguon", input.tyLeCoNguon],
      ] as const;
      for (const [k, v] of nums) {
        if (!Number.isFinite(v) || v < 0) {
          const e: any = new Error(`Gia tri khong hop le cho ${k}: ${v}`);
          e.status = 400;
          throw e;
        }
      }
      const signedAt = new Date().toISOString();
      let entry!: WormSignOffRow;

      db.exec("BEGIN IMMEDIATE");
      try {
        const lastDb = db
          .prepare("SELECT seq, curr_hash FROM worm_signoff ORDER BY seq DESC LIMIT 1")
          .get() as { seq: number; curr_hash: string } | undefined;

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
          session_id: input.sessionId,
          tong_menh_de: Number(input.tongMenhDe),
          so_giu: Number(input.soGiu),
          so_sua: Number(input.soSua),
          so_bo: Number(input.soBo),
          ty_le_co_nguon: Number(input.tyLeCoNguon),
          content_hash: String(input.contentHash),
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
        db.exec("COMMIT");
      } catch (err) {
        db.exec("ROLLBACK");
        throw err;
      }

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

    docLichSuSignOff(sessionId?: string): WormSignOffRow[] {
      const sql = sessionId
        ? `SELECT seq, timestamp, nguoi_dung_id AS user_id, event, session_id,
                  tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
                  content_hash, prev_hash, curr_hash
           FROM worm_signoff WHERE session_id = ? ORDER BY seq ASC`
        : `SELECT seq, timestamp, nguoi_dung_id AS user_id, event, session_id,
                  tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
                  content_hash, prev_hash, curr_hash
           FROM worm_signoff ORDER BY seq ASC`;
      return (sessionId ? db.prepare(sql).all(sessionId) : db.prepare(sql).all()) as unknown as WormSignOffRow[];
    },

    xacMinhChuoi(): { hopLe: boolean; soBanGhi: number; loi?: string } {
      const rows = this.docLichSuSignOff();
      if (!rows.length) return { hopLe: true, soBanGhi: 0 };
      let expectedPrev = rows[0].seq === 1 ? GENESIS_HASH_WORM : rows[0].prev_hash;
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
      return { hopLe: true, soBanGhi: rows.length };
    },
  };
}
