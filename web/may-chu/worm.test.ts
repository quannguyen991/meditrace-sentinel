import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import test from "node:test";
import { damBaoBangWorm, GENESIS_HASH_WORM, taoKhoWorm } from "./worm";

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
      { tongMenhDe: -1, soGiu: 0, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 3.5, soGiu: 3, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 3, soSua: 2, soBo: 1, tyLeCoNguon: 100, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 5, soSua: 0, soBo: 0, tyLeCoNguon: 100.5, contentHash: "x" },
      { tongMenhDe: 5, soGiu: 5, soSua: 0, soBo: 0, tyLeCoNguon: -5, contentHash: "x" },
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

    // 2. Kẻ tấn công xóa cả .anchor.json lẫn dòng cuối trong SQLite, nhưng .jsonl vẫn còn seq=2 -> vẫn phát hiện cắt đuôi!
    fs.unlinkSync(anchorPath);
    db.exec("DROP TRIGGER trg_worm_signoff_no_delete;");
    db.prepare("DELETE FROM worm_signoff WHERE seq = 2").run();
    const khoRestart2 = taoKhoWorm(db, jsonl);
    const jsonlCrossCheck = khoRestart2.xacMinhChuoi();
    assert.equal(jsonlCrossCheck.hopLe, false);
    assert.match(jsonlCrossCheck.loi || "", /JSONL/);
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
