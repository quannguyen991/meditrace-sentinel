import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import test from "node:test";
import { GENESIS_HASH_WORM, taoKhoWorm } from "./worm";

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
    fs.writeFileSync(
      jsonl,
      JSON.stringify({ seq: 5, curr_hash: "legacy_hash_5" }) + "\n",
      "utf-8",
    );
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

test("worm: chan gia tri NaN/am va phat hien gian doan seq", () => {
  const { dir, db, jsonl } = taoDbTam();
  try {
    const kho = taoKhoWorm(db, jsonl);
    assert.throws(
      () =>
        kho.ghiSignOff({
          sessionId: "ca_bad",
          userId: null,
          tongMenhDe: Number.NaN,
          soGiu: 0,
          soSua: 0,
          soBo: 0,
          tyLeCoNguon: 100,
          contentHash: "x",
        }),
      /Gia tri khong hop le/,
    );
    assert.throws(
      () =>
        kho.ghiSignOff({
          sessionId: "ca_neg",
          userId: null,
          tongMenhDe: -1,
          soGiu: 0,
          soSua: 0,
          soBo: 0,
          tyLeCoNguon: 100,
          contentHash: "x",
        }),
      /Gia tri khong hop le/,
    );

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
    // Gia lap chen ban ghi nhay coc seq = 3 voi prev_hash khop
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
