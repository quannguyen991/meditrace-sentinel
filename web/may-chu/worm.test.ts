import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import test from "node:test";
import crypto from "node:crypto";
import { damBaoBangWorm, GENESIS_HASH_WORM, layKhoaWorm, taoKhoWorm } from "./worm";

process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu-dai-hon-32-ky-tu-0123456789";

function taoDbTam() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-worm-"));
  const db = new DatabaseSync(path.join(dir, "test.db"));
  const schema = fs.readFileSync(path.join(process.cwd(), "db", "schema.sql"), "utf-8");
  db.exec(schema);
  const jsonl = path.join(dir, "worm_signoff_log.jsonl");
  return { dir, db, jsonl };
}

test("worm: ghi chuoi SHA-256 vao SQLite + JSONL va xac minh toan ven", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    const r1 = kho.ghiSignOff({
      sessionId: "ca_01",
      userId: null,
      tongMenhDe: 10,
      soGiu: 8,
      soSua: 2,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "abc123",
    });
    assert.equal(r1.wormSeq, 1);
    assert.equal(r1.ok, true);

    const r2 = kho.ghiSignOff({
      sessionId: "ca_02",
      userId: null,
      tongMenhDe: 5,
      soGiu: 5,
      soSua: 0,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "def456",
    });
    assert.equal(r2.wormSeq, 2);
    assert.notEqual(r2.hash, r1.hash);

    const check = kho.xacMinhChuoi();
    assert.deepEqual(check, { hopLe: true, soBanGhi: 2 });

    const rows = kho.docLichSuSignOff();
    assert.equal(rows[0].prev_hash, GENESIS_HASH_WORM);
    assert.equal(rows[1].prev_hash, rows[0].curr_hash);

    const lines = fs.readFileSync(jsonl, "utf-8").trim().split("\n");
    assert.equal(lines.length, 2);
    assert.equal(JSON.parse(lines[1]).curr_hash, r2.hash);

    // Tệp neo .anchor.json được lưu ngay cạnh tệp DB
    const anchorFile = kho.duongDanAnchor();
    assert.equal(anchorFile, path.join(dir, "test.db.anchor.json"));
    assert.ok(anchorFile && fs.existsSync(anchorFile));
    const anchor = JSON.parse(fs.readFileSync(anchorFile!, "utf-8"));
    assert.equal(anchor.firstSeq, 1);
    assert.equal(anchor.lastSeq, 2);
    assert.equal(anchor.totalRecords, 2);
    assert.equal(anchor.lastHash, r2.hash);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: trigger SQLite chan tuyet doi UPDATE va DELETE", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    kho.ghiSignOff({
      sessionId: "ca_01",
      userId: null,
      tongMenhDe: 4,
      soGiu: 4,
      soSua: 0,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "hash1",
    });

    assert.throws(() => {
      db.prepare("UPDATE worm_signoff SET so_giu = 0 WHERE seq = 1").run();
    }, /WORM Violation/);

    assert.throws(() => {
      db.prepare("DELETE FROM worm_signoff WHERE seq = 1").run();
    }, /WORM Violation/);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: noi tiep seq va prev_hash tu worm_signoff_log.jsonl cu", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    fs.writeFileSync(jsonl, JSON.stringify({ seq: 5, curr_hash: "legacy_hash_5" }) + "\n", "utf-8");
    const kho = taoKhoWorm(db, jsonl);
    const r6 = kho.ghiSignOff({
      sessionId: "ca_06",
      userId: null,
      tongMenhDe: 3,
      soGiu: 3,
      soSua: 0,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "h6",
    });
    assert.equal(r6.wormSeq, 6);
    const rows = kho.docLichSuSignOff("ca_06");
    assert.equal(rows.length, 1);
    assert.equal(rows[0].prev_hash, "legacy_hash_5");
    assert.deepEqual(kho.xacMinhChuoi(), { hopLe: true, soBanGhi: 1 });
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: chan gia tri NaN/am, so thap phan, tong vuot tongMenhDe, tyLeCoNguon ngoai 0..100, contentHash rong va phat hien gian doan seq", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    const invalidInputs = [
      { tongMenhDe: Number.NaN, soGiu: 0, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 0, soGiu: 0, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: -1, soGiu: 0, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 3.5, soGiu: 3, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 3, soGiu: 0, soSua: 0, soBo: 3, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 3, soSua: 2, soBo: 1, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 5, soSua: 0, soBo: 0, tyLeCoNguon: 0, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 5, soSua: 0, soBo: 0, tyLeCoNguon: 100.5, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 5, soSua: 0, soBo: 0, tyLeCoNguon: -5, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 5, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x", soChuaXacNhan: 1 },
      { tongMenhDe: 5, soGiu: 5, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "   " },
    ];
    for (const bad of invalidInputs) {
      assert.throws(
        () =>
          kho.ghiSignOff({
            sessionId: "ca_bad",
            userId: null,
            ...bad,
          }),
        /Gia tri khong hop le/,
      );
    }

    const r1 = kho.ghiSignOff({
      sessionId: "ca_01",
      userId: null,
      tongMenhDe: 2,
      soGiu: 2,
      soSua: 0,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "h1",
    });
    // Giả lập chèn bản ghi nhảy cóc seq = 3 với prev_hash khớp
    db.prepare(
      `INSERT INTO worm_signoff (
        seq, timestamp, nguoi_dung_id, event, session_id,
        tong_menh_de, so_giu, so_sua, so_bo, ty_le_co_nguon,
        content_hash, prev_hash, curr_hash
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    ).run(3, new Date().toISOString(), null, "doctor_forensic_signoff", "ca_03", 1, 1, 0, 0, 100, "h3", r1.hash, "fake");
    const check = kho.xacMinhChuoi();
    assert.equal(check.hopLe, false);
    assert.match(check.loi || "", /Gian doan seq/);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: phat hien tan cong cat dau chuoi, cat duoi chuoi va xoa trang nho tep neo .anchor.json", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    for (let i = 1; i <= 3; i++) {
      kho.ghiSignOff({
        sessionId: `ca_${i}`,
        userId: null,
        tongMenhDe: 4,
        soGiu: 4,
        soSua: 0,
        soBo: 0,
        tyLeCoNguon: 100,
        contentHash: `hash_${i}`,
      });
    }
    assert.deepEqual(kho.xacMinhChuoi(), { hopLe: true, soBanGhi: 3 });

    // Kẻ tấn công có quyền SQLite trực tiếp xóa trigger để cắt đuôi chuỗi (xóa seq = 3)
    db.exec("DROP TRIGGER trg_worm_signoff_no_delete;");
    db.prepare("DELETE FROM worm_signoff WHERE seq = 3").run();
    const tailCheck = kho.xacMinhChuoi();
    assert.equal(tailCheck.hopLe, false);
    assert.match(tailCheck.loi || "", /cat duoi chuoi/);

    // Kẻ tấn công không thể ghi đè làm sạch tệp neo bằng cách ký ca mới lên chuỗi đã bị cắt
    assert.throws(() => {
      kho.ghiSignOff({
        sessionId: "ca_4",
        userId: null,
        tongMenhDe: 1,
        soGiu: 1,
        soSua: 0,
        soBo: 0,
        tyLeCoNguon: 100,
        contentHash: "hash_4",
      });
    }, /WORM Violation/);

    // Kẻ tấn công tiếp tục cắt đầu chuỗi (xóa seq = 1, chỉ chừa seq = 2)
    db.prepare("DELETE FROM worm_signoff WHERE seq = 1").run();
    const headCheck = kho.xacMinhChuoi();
    assert.equal(headCheck.hopLe, false);
    assert.match(headCheck.loi || "", /cat dau chuoi/);

    // Kẻ tấn công xóa trắng toàn bộ bảng worm_signoff
    db.prepare("DELETE FROM worm_signoff").run();
    const wipeCheck = kho.xacMinhChuoi();
    assert.equal(wipeCheck.hopLe, false);
    assert.equal(wipeCheck.soBanGhi, 0);
    assert.match(wipeCheck.loi || "", /xoa trang/);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: phat hien tep .anchor.json bi pha hong hoac xoa .anchor.json kem cat duoi so voi .jsonl", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    kho.ghiSignOff({ sessionId: "s1", userId: null, tongMenhDe: 2, soGiu: 2, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "h1" });
    kho.ghiSignOff({ sessionId: "s2", userId: null, tongMenhDe: 2, soGiu: 2, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "h2" });

    const anchorPath = kho.duongDanAnchor()!;
    // 1. Kẻ tấn công ghi rác vào .anchor.json và khởi động lại khoWorm -> KHÔNG ĐƯỢC tự ghi đè làm sạch!
    fs.writeFileSync(anchorPath, "{khong-hop-le", "utf-8");
    const khoRestart1 = taoKhoWorm(db, jsonl);
    const corruptCheck = khoRestart1.xacMinhChuoi();
    assert.equal(corruptCheck.hopLe, false);
    assert.match(corruptCheck.loi || "", /anchor\.json/);
    assert.throws(
      () =>
        khoRestart1.ghiSignOff({
          sessionId: "s3",
          userId: null,
          tongMenhDe: 1,
          soGiu: 1,
          soSua: 0,
          soBo: 0,
          tyLeCoNguon: 100,
          contentHash: "h3",
        }),
      /WORM Violation/,
    );

    // 2. Kẻ tấn công xóa cả .anchor.json lẫn dòng cuối trong SQLite -> mất neo được báo là bị can thiệp,
    //    KHÔNG tự neo lại từ CSDL đã sửa; và đối chứng .jsonl vẫn phát hiện cắt đuôi.
    fs.unlinkSync(anchorPath);
    db.exec("DROP TRIGGER trg_worm_signoff_no_delete;");
    db.prepare("DELETE FROM worm_signoff WHERE seq = 2").run();
    const khoRestart2 = taoKhoWorm(db, jsonl);
    assert.equal(fs.existsSync(anchorPath), false, "không được tự tạo lại tệp neo");
    const jsonlCrossCheck = khoRestart2.xacMinhChuoi();
    assert.equal(jsonlCrossCheck.hopLe, false);
    assert.match(jsonlCrossCheck.loi || "", /Thieu tep neo/);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

const kyMau = (sessionId: string) => ({
  sessionId,
  userId: null,
  tongMenhDe: 2,
  soGiu: 2,
  soSua: 0,
  soBo: 0,
  tyLeCoNguon: 100,
  contentHash: `h_${sessionId}`,
  soChuaXacNhan: 0,
});

test("worm: chuoi dung HMAC co khoa — khong tinh lai duoc bang SHA-256 tran, sai khoa thi khong xac minh duoc", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    kho.ghiSignOff(kyMau("s1"));
    const [r] = kho.docLichSuSignOff();
    assert.equal(r.thuat_toan, "hmac-sha256");
    const { curr_hash, thuat_toan, ...payload } = r as any;
    const shaTran = crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
    assert.notEqual(curr_hash, shaTran, "băm phải có khoá");
    const dungKhoa = crypto.createHmac("sha256", layKhoaWorm()).update(JSON.stringify(payload)).digest("hex");
    assert.equal(curr_hash, dungKhoa);

    const anchor = JSON.parse(fs.readFileSync(kho.duongDanAnchor()!, "utf-8"));
    assert.equal(typeof anchor.mac, "string");
    assert.equal(anchor.hmacTuSeq, 1);

    // Mở lại bằng khoá khác -> báo bị can thiệp, không ký thêm được
    const khoSaiKhoa = taoKhoWorm(db, jsonl, undefined, { khoa: "mot-khoa-hoan-toan-khac-0123456789abcdef" });
    const kq = khoSaiKhoa.xacMinhChuoi();
    assert.equal(kq.hopLe, false);
    assert.match(kq.loi || "", /khoa WORM khac/);
    assert.throws(() => khoSaiKhoa.ghiSignOff(kyMau("s2")), /WORM Violation/);

    // Kẻ có quyền ghi tệp sửa tep neo (không có khoá) -> chữ ký neo hỏng
    anchor.lastSeq = 1;
    anchor.totalRecords = 1;
    anchor.lastHash = "gia";
    fs.writeFileSync(kho.duongDanAnchor()!, JSON.stringify(anchor), "utf-8");
    const kq2 = taoKhoWorm(db, jsonl).xacMinhChuoi();
    assert.equal(kq2.hopLe, false);
    assert.match(kq2.loi || "", /HMAC/);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: mat tep neo khi da co ban ghi -> khong tu neo lai; MEDITRACE_WORM_NEO_LAI=1 moi cho neo lai", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    kho.ghiSignOff(kyMau("s1"));
    const anchorPath = kho.duongDanAnchor()!;
    fs.unlinkSync(anchorPath);

    const khoMoi = taoKhoWorm(db, jsonl);
    assert.equal(fs.existsSync(anchorPath), false);
    const kq = khoMoi.xacMinhChuoi();
    assert.equal(kq.hopLe, false);
    assert.match(kq.loi || "", /Thieu tep neo/);
    assert.throws(() => khoMoi.ghiSignOff(kyMau("s2")), /WORM Violation/);

    const khoNeoLai = taoKhoWorm(db, jsonl, undefined, { env: { ...process.env, MEDITRACE_WORM_NEO_LAI: "1" } });
    assert.equal(fs.existsSync(anchorPath), true);
    assert.deepEqual(khoNeoLai.xacMinhChuoi(), { hopLe: true, soBanGhi: 1 });
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: neo cham dung 1 ban ghi (sap giua COMMIT va ghi neo) thi tu lanh; cham 2 ban ghi thi bao can thiep", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    kho.ghiSignOff(kyMau("s1"));
    const anchorPath = kho.duongDanAnchor()!;
    const neoSau1 = fs.readFileSync(anchorPath, "utf-8");
    kho.ghiSignOff(kyMau("s2"));
    const neoSau2 = fs.readFileSync(anchorPath, "utf-8");
    kho.ghiSignOff(kyMau("s3"));

    // Giả lập sập sau COMMIT bản ghi 3: tệp neo vẫn ở trạng thái sau bản ghi 2
    fs.writeFileSync(anchorPath, neoSau2, "utf-8");
    const khoSauSap = taoKhoWorm(db, jsonl);
    assert.deepEqual(khoSauSap.xacMinhChuoi(), { hopLe: true, soBanGhi: 3 });
    assert.equal(JSON.parse(fs.readFileSync(anchorPath, "utf-8")).lastSeq, 3);
    assert.equal(khoSauSap.ghiSignOff(kyMau("s4")).wormSeq, 4, "ký tiếp được, không 409 vĩnh viễn");

    // Neo chậm 3 bản ghi: không tự lành
    fs.writeFileSync(anchorPath, neoSau1, "utf-8");
    const khoLech = taoKhoWorm(db, jsonl);
    assert.equal(khoLech.xacMinhChuoi().hopLe, false);
    assert.throws(() => khoLech.ghiSignOff(kyMau("s5")), /WORM Violation/);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: chuoi cu (SHA-256 khong khoa, neo chua ky) van xac minh duoc va duoc noi tiep bang HMAC", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    damBaoBangWorm(db);
    // Dựng 2 bản ghi theo đúng cách mã cũ (trước bản vá) đã ghi
    let prev = GENESIS_HASH_WORM;
    const them = db.prepare(
      `INSERT INTO worm_signoff (seq, timestamp, nguoi_dung_id, event, session_id, tong_menh_de, so_giu, so_sua, so_bo,
        ty_le_co_nguon, content_hash, prev_hash, curr_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    );
    const hashes: string[] = [];
    for (const seq of [1, 2]) {
      const p = {
        seq,
        timestamp: `2026-11-2${seq}T00:00:00.000Z`,
        user_id: null,
        event: "doctor_forensic_signoff",
        session_id: `cu_${seq}`,
        tong_menh_de: 3,
        so_giu: 3,
        so_sua: 0,
        so_bo: 0,
        ty_le_co_nguon: 100,
        content_hash: `c${seq}`,
        prev_hash: prev,
      };
      const h = crypto.createHash("sha256").update(JSON.stringify(p)).digest("hex");
      them.run(seq, p.timestamp, null, p.event, p.session_id, 3, 3, 0, 0, 100, p.content_hash, prev, h);
      hashes.push(h);
      prev = h;
    }
    const anchorPath = path.join(dir, "test.db.anchor.json");
    fs.writeFileSync(
      anchorPath,
      JSON.stringify({ firstSeq: 1, firstPrevHash: GENESIS_HASH_WORM, firstHash: hashes[0], lastSeq: 2, lastHash: hashes[1], totalRecords: 2, updatedAt: "x" }),
      "utf-8",
    );

    const kho = taoKhoWorm(db, jsonl);
    assert.equal(typeof JSON.parse(fs.readFileSync(anchorPath, "utf-8")).mac, "string", "neo cũ được ký HMAC");
    assert.deepEqual(kho.xacMinhChuoi(), { hopLe: true, soBanGhi: 2 });
    assert.equal(kho.ghiSignOff(kyMau("moi")).wormSeq, 3);
    assert.deepEqual(kho.xacMinhChuoi(), { hopLe: true, soBanGhi: 3 });
    assert.equal(JSON.parse(fs.readFileSync(anchorPath, "utf-8")).hmacTuSeq, 3);

    // Kẻ không có khoá nối thêm bản ghi SHA-256 trần sau bản ghi HMAC -> bị phát hiện
    const p4 = {
      seq: 4, timestamp: "t", user_id: null, event: "doctor_forensic_signoff", session_id: "gia", tong_menh_de: 1,
      so_giu: 1, so_sua: 0, so_bo: 0, ty_le_co_nguon: 100, content_hash: "g",
      prev_hash: (kho.docLichSuSignOff().at(-1) as any).curr_hash,
    };
    them.run(4, "t", null, p4.event, "gia", 1, 1, 0, 0, 100, "g", p4.prev_hash, crypto.createHash("sha256").update(JSON.stringify(p4)).digest("hex"));
    const kq = kho.xacMinhChuoi();
    assert.equal(kq.hopLe, false);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("worm: damBaoBangWorm tu dong migrate bang + cot + trigger cho DB cu chua co worm_signoff", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-worm-legacy-"));
  const db = new DatabaseSync(path.join(dir, "legacy.db"));
  try {
    db.exec(`
      CREATE TABLE nguoi_dung (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        ho_ten TEXT NOT NULL,
        mat_khau_bam TEXT NOT NULL,
        vai TEXT NOT NULL DEFAULT 'bac_si',
        tao_luc INTEGER NOT NULL
      );
      INSERT INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (7, 'a@b.vn', 'BS A', 'x', 'bac_si', 1);
    `);
    damBaoBangWorm(db);
    const kho = taoKhoWorm(db);
    const kq = kho.ghiSignOff({
      sessionId: "legacy_s1",
      userId: 7,
      tongMenhDe: 3,
      soGiu: 2,
      soSua: 1,
      soBo: 0,
      tyLeCoNguon: 95.5,
      contentHash: "sha_legacy",
    });
    assert.equal(kq.wormSeq, 1);
    assert.equal(kho.docLichSuSignOff("legacy_s1", { userId: 7 }).length, 1);
    assert.equal(kho.docLichSuSignOff("legacy_s1", { userId: 99 }).length, 0);
    assert.throws(() => db.prepare("DELETE FROM worm_signoff WHERE seq = 1").run(), /WORM Violation/);
  } finally {
    db.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
