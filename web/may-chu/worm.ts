/**
 * Sổ ký duyệt WORM (ghi một lần) cho bản nháp bệnh án.
 *
 * Chuỗi băm có KHOÁ: mỗi bản ghi mới dùng HMAC-SHA256 với khoá bí mật (env MEDITRACE_WORM_KEY, hoặc tệp khoá
 * NGOÀI thư mục dữ liệu, mặc định ~/.meditrace/worm.key, tự sinh lần đầu). Người chỉ có quyền ghi tệp SQLite
 * không tính lại được chuỗi. Tệp neo `<db>.anchor.json` cũng được ký HMAC.
 *
 * Tương thích (migration): bản ghi cũ (cột `thuat_toan` NULL) vẫn xác minh bằng SHA-256 không khoá như trước;
 * bản ghi cũ chỉ được phép đứng TRƯỚC bản ghi HMAC đầu tiên (`hmacTuSeq` trong neo đã ký). Tệp neo kiểu cũ
 * (chưa có `mac`) được ký lại một lần khi chuỗi khớp hoàn toàn với nó (có cảnh báo trong log).
 *
 * Mất tệp neo trong khi đã có bản ghi: KHÔNG tự neo lại từ CSDL (có thể đã bị sửa) — báo trạng thái bị can thiệp.
 * Người vận hành đã kiểm tra có thể cho phép neo lại một lần bằng MEDITRACE_WORM_NEO_LAI=1.
 * Neo chậm đúng MỘT bản ghi (sập giữa COMMIT và ghi neo) thì tự lành khi bản ghi đó hợp lệ với khoá.
 */
import crypto from "crypto";
import fs from "fs";
import os from "os";
import path from "path";
import type { DatabaseSync } from "node:sqlite";
import type { ApiSignOffResponse } from "../src/types/api-contract";

export const GENESIS_HASH_WORM = crypto
  .createHash("sha256")
  .update("MEDITRACE_SENTINEL_GENESIS_CIRCULAR_46_2018_TT_BYT")
  .digest("hex");

const THUAT_TOAN_HMAC = "hmac-sha256";

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
  thuat_toan?: string | null;
}

export interface WormAnchor {
  v?: number;
  firstSeq: number;
  firstPrevHash: string;
  firstHash: string;
  lastSeq: number;
  lastHash: string;
  totalRecords: number;
  /** seq của bản ghi HMAC đầu tiên; từ đây trở đi mọi bản ghi phải là HMAC. `null` nếu chưa có. */
  hmacTuSeq?: number | null;
  updatedAt: string;
  khoaId?: string;
  mac?: string;
}

/* ------------------------------------------------------------------ khoá */

/**
 * Khoá HMAC của sổ WORM: env MEDITRACE_WORM_KEY; nếu không có thì đọc tệp MEDITRACE_WORM_KEY_FILE
 * (mặc định ~/.meditrace/worm.key, ngoài thư mục data/), chưa có thì sinh 32 byte ngẫu nhiên và cảnh báo.
 */
export function layKhoaWorm(env: NodeJS.ProcessEnv = process.env): Buffer {
  const tuEnv = String(env.MEDITRACE_WORM_KEY || "").trim();
  if (tuEnv) {
    if (tuEnv.length < 32) console.warn("[worm] MEDITRACE_WORM_KEY ngắn hơn 32 ký tự — nên dùng khoá ngẫu nhiên dài hơn.");
    return Buffer.from(tuEnv, "utf8");
  }
  const tep = String(env.MEDITRACE_WORM_KEY_FILE || "").trim() || path.join(os.homedir(), ".meditrace", "worm.key");
  if (fs.existsSync(tep)) {
    const noiDung = fs.readFileSync(tep, "utf8").trim();
    if (noiDung) return Buffer.from(noiDung, "utf8");
  }
  const moi = crypto.randomBytes(32).toString("hex");
  fs.mkdirSync(path.dirname(tep), { recursive: true });
  fs.writeFileSync(tep, moi + "\n", { encoding: "utf8", mode: 0o600 });
  console.warn(
    `[worm] Chưa có MEDITRACE_WORM_KEY: đã sinh khoá WORM mới tại ${tep}. SAO LƯU tệp này cùng CSDL — mất khoá thì không xác minh được chuỗi ký duyệt.`,
  );
  return Buffer.from(moi, "utf8");
}

/* ------------------------------------------------------------------ lược đồ */

/**
 * Migration tự động đảm bảo bảng, cột `nguoi_dung_id`, `thuat_toan`, chỉ mục và 2 trigger WORM bất biến
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
  // NULL = bản ghi cũ băm SHA-256 không khoá; 'hmac-sha256' = bản ghi mới có khoá.
  if (!cols.some((c) => c.name === "thuat_toan")) {
    db.exec("ALTER TABLE worm_signoff ADD COLUMN thuat_toan TEXT;");
  }
  db.exec(`
    CREATE INDEX IF NOT EXISTS worm_signoff_theo_phien ON worm_signoff(session_id, seq);
    CREATE INDEX IF NOT EXISTS worm_signoff_theo_nguoi_phien ON worm_signoff(nguoi_dung_id, session_id, seq);

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

function loiWorm(thongDiep: string): Error {
  const e: any = new Error(`WORM Violation: ${thongDiep}`);
  e.status = 409;
  e.congKhai = true;
  e.code = "worm_bi_can_thiep";
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

const COT_DONG = `seq, timestamp, nguoi_dung_id AS user_id, event, session_id,
  tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
  content_hash, prev_hash, curr_hash, thuat_toan`;

function payloadDong(r: WormSignOffRow) {
  return {
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
}

export function taoKhoWorm(
  db: DatabaseSync,
  wormJsonlPath?: string,
  anchorPathOverride?: string,
  tuyChon: { khoa?: Buffer | string; env?: NodeJS.ProcessEnv } = {},
) {
  damBaoBangWorm(db);
  const env = tuyChon.env || process.env;
  const khoa = tuyChon.khoa !== undefined ? Buffer.from(tuyChon.khoa) : layKhoaWorm(env);
  const khoaId = crypto.createHash("sha256").update(khoa).digest("hex").slice(0, 16);

  const dbFilePath = timDuongDanDb(db);
  const anchorPath =
    anchorPathOverride ||
    (dbFilePath ? `${dbFilePath}.anchor.json` : wormJsonlPath ? `${wormJsonlPath}.anchor.json` : undefined);

  let neoTrongRam: WormAnchor | null = null;

  const bamDong = (r: WormSignOffRow, thuatToan: string | null | undefined): string => {
    const json = JSON.stringify(payloadDong(r));
    return thuatToan === THUAT_TOAN_HMAC
      ? crypto.createHmac("sha256", khoa).update(json).digest("hex")
      : crypto.createHash("sha256").update(json).digest("hex");
  };
  const macNeo = (n: WormAnchor): string =>
    crypto
      .createHmac("sha256", khoa)
      .update(
        JSON.stringify([2, n.firstSeq, n.firstPrevHash, n.firstHash, n.lastSeq, n.lastHash, n.totalRecords, n.hmacTuSeq ?? null]),
      )
      .digest("hex");
  const macBang = (a: string, b: string) =>
    a.length === b.length && crypto.timingSafeEqual(Buffer.from(a, "utf8"), Buffer.from(b, "utf8"));

  const docTatCa = (): WormSignOffRow[] =>
    db.prepare(`SELECT ${COT_DONG} FROM worm_signoff ORDER BY seq ASC`).all() as unknown as WormSignOffRow[];
  const docDau = () =>
    db.prepare("SELECT seq, prev_hash, curr_hash FROM worm_signoff ORDER BY seq ASC LIMIT 1").get() as
      | { seq: number; prev_hash: string; curr_hash: string }
      | undefined;
  const docCuoi = () =>
    db.prepare(`SELECT ${COT_DONG} FROM worm_signoff ORDER BY seq DESC LIMIT 1`).get() as unknown as WormSignOffRow | undefined;
  const demDong = () => Number((db.prepare("SELECT COUNT(*) AS n FROM worm_signoff").get() as { n: number }).n);
  const hmacDauTien = (): number | null => {
    const r = db.prepare("SELECT MIN(seq) AS s FROM worm_signoff WHERE thuat_toan = ?").get(THUAT_TOAN_HMAC) as
      | { s: number | null }
      | undefined;
    return r?.s ?? null;
  };

  function ghiAnchor(n: Omit<WormAnchor, "mac" | "khoaId" | "v">): WormAnchor {
    const neo: WormAnchor = { v: 2, ...n, hmacTuSeq: n.hmacTuSeq ?? null, khoaId };
    neo.mac = macNeo(neo);
    neoTrongRam = neo;
    if (anchorPath) {
      fs.mkdirSync(path.dirname(anchorPath), { recursive: true });
      const tam = `${anchorPath}.tmp.${process.pid}`;
      fs.writeFileSync(tam, JSON.stringify(neo, null, 2) + "\n", "utf8");
      fs.renameSync(tam, anchorPath);
    }
    return neo;
  }

  function neoTuCsdl(): WormAnchor | null {
    const dau = docDau();
    const cuoi = docCuoi();
    const n = demDong();
    if (!dau || !cuoi || n === 0) return null;
    return ghiAnchor({
      firstSeq: Number(dau.seq),
      firstPrevHash: dau.prev_hash,
      firstHash: dau.curr_hash,
      lastSeq: Number(cuoi.seq),
      lastHash: cuoi.curr_hash,
      totalRecords: n,
      hmacTuSeq: hmacDauTien(),
      updatedAt: new Date().toISOString(),
    });
  }

  /** Xác minh toàn bộ chuỗi trên các dòng (không dùng neo). Trả lỗi đầu tiên hoặc null. */
  function kiemChuoi(rows: WormSignOffRow[], neo: WormAnchor | null): string | null {
    let expectedPrev = rows[0].seq === 1 ? GENESIS_HASH_WORM : neo ? neo.firstPrevHash : rows[0].prev_hash;
    let expectedSeq = rows[0].seq;
    let daGapHmac = false;
    for (const r of rows) {
      if (r.seq !== expectedSeq) return `Gian doan seq tai seq=${r.seq} (ky vong ${expectedSeq})`;
      if (r.prev_hash !== expectedPrev) return `Dut chuoi tai seq=${r.seq}`;
      const laHmac = r.thuat_toan === THUAT_TOAN_HMAC;
      if (daGapHmac && !laHmac) return `Ban ghi khong khoa xuat hien sau ban ghi HMAC tai seq=${r.seq}`;
      if (!laHmac && typeof neo?.hmacTuSeq === "number" && r.seq >= neo.hmacTuSeq) {
        return `Ban ghi seq=${r.seq} phai la HMAC theo tep neo`;
      }
      if (r.thuat_toan && !laHmac) return `Thuat toan la tai seq=${r.seq}`;
      daGapHmac = daGapHmac || laHmac;
      if (!macBang(bamDong(r, r.thuat_toan), r.curr_hash)) return `Sai hash tai seq=${r.seq}`;
      expectedPrev = r.curr_hash;
      expectedSeq = r.seq + 1;
    }
    return null;
  }

  function docTrangThaiAnchor(): TrangThaiAnchor {
    if (!anchorPath) return neoTrongRam ? { trangThai: "hop_le", neo: neoTrongRam } : { trangThai: "chua_co" };
    if (!fs.existsSync(anchorPath)) {
      const n = demDong();
      if (n === 0) return { trangThai: "chua_co" };
      return {
        trangThai: "bi_sua_doi",
        lyDo: `Thieu tep neo .anchor.json trong khi da co ${n} ban ghi ky duyet (co the bi xoa de neo lai tu CSDL da sua). Khong tu neo lai.`,
      };
    }
    let j: any;
    try {
      j = JSON.parse(fs.readFileSync(anchorPath, "utf8"));
    } catch {
      return { trangThai: "bi_sua_doi", lyDo: "Phat hien tep neo .anchor.json bi hong JSON hoac bi sua doi" };
    }
    const dungDinhDang =
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
      j.totalRecords >= 1;
    if (!dungDinhDang) return { trangThai: "bi_sua_doi", lyDo: "Phat hien tep neo .anchor.json sai dinh dang hoac bi sua doi" };
    if (typeof j.mac !== "string") return { trangThai: "hop_le", neo: j as WormAnchor }; // neo kiểu cũ: nâng cấp ở khởi tạo
    if (j.khoaId && j.khoaId !== khoaId) {
      return { trangThai: "bi_sua_doi", lyDo: "Tep neo .anchor.json duoc ky bang khoa WORM khac (kiem tra MEDITRACE_WORM_KEY)" };
    }
    if (!macBang(macNeo(j as WormAnchor), j.mac)) {
      return { trangThai: "bi_sua_doi", lyDo: "Chu ky HMAC cua tep neo .anchor.json khong hop le (tep neo bi sua doi)" };
    }
    return { trangThai: "hop_le", neo: j as WormAnchor };
  }

  /** Neo chậm đúng 1 bản ghi (sập giữa COMMIT và ghi neo): bản ghi cuối hợp lệ với khoá thì cập nhật neo. */
  function thuTuLanhNeo(): void {
    const tt = docTrangThaiAnchor();
    if (tt.trangThai !== "hop_le" || typeof tt.neo.mac !== "string") return;
    const neo = tt.neo;
    const cuoi = docCuoi();
    const n = demDong();
    if (!cuoi || Number(cuoi.seq) !== neo.lastSeq + 1 || n !== neo.totalRecords + 1) return;
    const truoc = db.prepare("SELECT curr_hash FROM worm_signoff WHERE seq = ?").get(neo.lastSeq) as
      | { curr_hash: string }
      | undefined;
    if (!truoc || truoc.curr_hash !== neo.lastHash || cuoi.prev_hash !== neo.lastHash) return;
    if (cuoi.thuat_toan !== THUAT_TOAN_HMAC || !macBang(bamDong(cuoi, THUAT_TOAN_HMAC), cuoi.curr_hash)) return;
    ghiAnchor({
      firstSeq: neo.firstSeq,
      firstPrevHash: neo.firstPrevHash,
      firstHash: neo.firstHash,
      lastSeq: Number(cuoi.seq),
      lastHash: cuoi.curr_hash,
      totalRecords: n,
      hmacTuSeq: neo.hmacTuSeq ?? Number(cuoi.seq),
      updatedAt: new Date().toISOString(),
    });
    console.warn(`[worm] Tệp neo chậm 1 bản ghi (seq=${cuoi.seq}) — đã tự cập nhật sau khi xác minh HMAC.`);
  }

  // Khởi tạo: (1) neo kiểu cũ chưa ký -> xác minh chuỗi khớp rồi ký; (2) thiếu neo nhưng có bản ghi -> chỉ neo lại
  // khi người vận hành cho phép rõ ràng; (3) tự lành neo chậm 1 bản ghi.
  {
    const tt = docTrangThaiAnchor();
    if (tt.trangThai === "hop_le" && typeof tt.neo.mac !== "string") {
      const rows = docTatCa();
      const cu = tt.neo;
      const last = rows[rows.length - 1];
      const khop =
        rows.length > 0 &&
        rows[0].seq === cu.firstSeq &&
        rows[0].curr_hash === cu.firstHash &&
        last.seq === cu.lastSeq &&
        last.curr_hash === cu.lastHash &&
        rows.length === cu.totalRecords &&
        kiemChuoi(rows, cu) === null;
      if (khop) {
        ghiAnchor({ ...cu, hmacTuSeq: hmacDauTien(), updatedAt: new Date().toISOString() });
        console.warn("[worm] Đã ký HMAC tệp neo kiểu cũ (chuỗi hiện tại khớp hoàn toàn với neo cũ).");
      }
    } else if (tt.trangThai === "bi_sua_doi" && anchorPath && !fs.existsSync(anchorPath) && env.MEDITRACE_WORM_NEO_LAI === "1") {
      const rows = docTatCa();
      const loi = rows.length ? kiemChuoi(rows, null) : null;
      if (loi) {
        console.error(`[worm] MEDITRACE_WORM_NEO_LAI=1 nhưng chuỗi không hợp lệ (${loi}) — không neo lại.`);
      } else {
        neoTuCsdl();
        console.warn("[worm] MEDITRACE_WORM_NEO_LAI=1: đã neo lại từ CSDL theo yêu cầu người vận hành. Gỡ biến này sau khi dùng.");
      }
    } else if (tt.trangThai === "chua_co" && !anchorPath) {
      neoTuCsdl();
    }
    thuTuLanhNeo();
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
      let neoMoi!: Omit<WormAnchor, "mac" | "khoaId" | "v">;

      db.exec("BEGIN IMMEDIATE");
      try {
        thuTuLanhNeo();
        const ttAnchor = docTrangThaiAnchor();
        if (ttAnchor.trangThai === "bi_sua_doi") throw loiWorm(ttAnchor.lyDo);
        if (ttAnchor.trangThai === "hop_le" && typeof ttAnchor.neo.mac !== "string") {
          throw loiWorm("Tep neo .anchor.json kieu cu khong khop voi chuoi hien tai — khong ky them duoc");
        }
        const neoCu = ttAnchor.trangThai === "hop_le" ? ttAnchor.neo : null;
        const firstDb = docDau();
        const lastDb = docCuoi();
        const soHienCo = demDong();

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
            throw loiWorm("Chuoi ky duyet da bi cat hoac sua doi so voi tep neo (.anchor.json)");
          }
        }
        if (lastDb) {
          const cuoiJsonl = docCuoiTuJsonl(wormJsonlPath);
          if (cuoiJsonl.nextSeq - 1 > Number(lastDb.seq)) {
            throw loiWorm("Chuoi SQLite bi cat duoi so voi worm_signoff_log.jsonl");
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

        const tho: WormSignOffRow = {
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
          curr_hash: "",
          thuat_toan: THUAT_TOAN_HMAC,
        };
        entry = { ...tho, curr_hash: bamDong(tho, THUAT_TOAN_HMAC) };

        db.prepare(
          `INSERT INTO worm_signoff (
            seq, timestamp, nguoi_dung_id, event, session_id,
            tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
            content_hash, prev_hash, curr_hash, thuat_toan
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
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
          THUAT_TOAN_HMAC,
        );

        neoMoi = {
          firstSeq: firstDb ? Number(firstDb.seq) : entry.seq,
          firstPrevHash: firstDb ? firstDb.prev_hash : entry.prev_hash,
          firstHash: firstDb ? firstDb.curr_hash : entry.curr_hash,
          lastSeq: entry.seq,
          lastHash: entry.curr_hash,
          totalRecords: soHienCo + 1,
          hmacTuSeq: neoCu?.hmacTuSeq ?? hmacDauTien() ?? entry.seq,
          updatedAt: signedAt,
        };
        db.exec("COMMIT");
      } catch (err) {
        db.exec("ROLLBACK");
        throw err;
      }

      // Sập giữa COMMIT và dòng dưới: lần sau neo chậm đúng 1 bản ghi và tự lành (thuTuLanhNeo).
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
        return db
          .prepare(`SELECT ${COT_DONG} FROM worm_signoff WHERE session_id = ? AND nguoi_dung_id = ? ORDER BY seq ASC`)
          .all(sessionId, tuyChon!.userId!) as unknown as WormSignOffRow[];
      }
      if (sessionId) {
        return db
          .prepare(`SELECT ${COT_DONG} FROM worm_signoff WHERE session_id = ? ORDER BY seq ASC`)
          .all(sessionId) as unknown as WormSignOffRow[];
      }
      if (hasUserFilter) {
        return db
          .prepare(`SELECT ${COT_DONG} FROM worm_signoff WHERE nguoi_dung_id = ? ORDER BY seq ASC`)
          .all(tuyChon!.userId!) as unknown as WormSignOffRow[];
      }
      return docTatCa();
    },

    xacMinhChuoi(): { hopLe: boolean; soBanGhi: number; loi?: string } {
      thuTuLanhNeo();
      const rows = docTatCa();
      const ttAnchor = docTrangThaiAnchor();
      if (ttAnchor.trangThai === "bi_sua_doi") {
        return { hopLe: false, soBanGhi: rows.length, loi: ttAnchor.lyDo };
      }
      const neo = ttAnchor.trangThai === "hop_le" ? ttAnchor.neo : null;
      if (neo && typeof neo.mac !== "string") {
        return { hopLe: false, soBanGhi: rows.length, loi: "Tep neo .anchor.json kieu cu khong khop voi chuoi hien tai" };
      }

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

      // 2. Tính liên tục của seq và băm (HMAC có khoá cho bản ghi mới, SHA-256 cho bản ghi cũ đứng trước)
      const loiChuoi = kiemChuoi(rows, neo);
      if (loiChuoi) return { hopLe: false, soBanGhi: rows.length, loi: loiChuoi };

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
