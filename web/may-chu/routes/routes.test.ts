import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-routes-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "routes-test.db");

const { db } = await import("../csdl");
const { dangKyCaKhamRoutes } = await import("./ca-kham");
const { dangKyAsrRoutes } = await import("./asr");
const { dangKyLlmNgoaiRoutes } = await import("./llm-ngoai");
const { dangKyBhytOcrRoutes } = await import("./bhyt-ocr");
const { dangKySignOffRoutes } = await import("./sign-off");
const { dangKyTraCuuRoutes } = await import("./tra-cuu");
const { dangKyTroLyRoutes } = await import("./tro-ly");

function taoAppTest() {
  const app = express();
  app.use(express.json({ limit: "5mb" }));
  // Gan nguoi dung gia lap da dang nhap de test truc tiep cac route nghiep vu
  db.prepare(
    `INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc)
     VALUES (1, 'bs@test.local', 'BS Test', 'hash', 'bac_si', ?)`,
  ).run(Date.now());
  app.use((req, _res, next) => {
    req.nguoiDung = { id: 1, email: "bs@test.local", hoTen: "BS Test", vai: "bac_si" };
    next();
  });

  dangKyCaKhamRoutes(app);
  dangKyAsrRoutes(app);
  dangKyLlmNgoaiRoutes(app);
  dangKyTraCuuRoutes(app);
  dangKyTroLyRoutes(app);
  dangKyBhytOcrRoutes(app);
  dangKySignOffRoutes(app);
  return app;
}

test("Express HTTP routes: ca-kham, sign-off/WORM, validation va error paths", async (t) => {
  const app = taoAppTest();
  const server = http.createServer(app);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const addr = server.address() as { port: number };
  const baseUrl = `http://127.0.0.1:${addr.port}`;

  t.after(() => {
    server.close();
    db.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  // 1. /api/ca-kham PUT + GET
  const putRes = await fetch(`${baseUrl}/api/ca-kham`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sessions: [{ id: "ca_http_1", patientIdentifier: "BN Test", date: "2026-11-25" }],
      savedAt: 1700000000000,
    }),
  });
  assert.equal(putRes.status, 200);
  const putData: any = await putRes.json();
  assert.equal(putData.ok, true);
  assert.equal(putData.count, 1);

  const getRes = await fetch(`${baseUrl}/api/ca-kham`);
  assert.equal(getRes.status, 200);
  const getData: any = await getRes.json();
  assert.equal(getData.sessions.length, 1);
  assert.equal(getData.sessions[0].id, "ca_http_1");

  const badKhoRes = await fetch(`${baseUrl}/api/kho/khong-ton-tai`);
  assert.equal(badKhoRes.status, 404);

  // 2. /api/sessions/:id/sign-off + /api/worm/verify
  const signRes = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tongMenhDe: 5,
      soGiu: 4,
      soSua: 1,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "sha_demo",
    }),
  });
  assert.equal(signRes.status, 200);
  const signData: any = await signRes.json();
  assert.equal(signData.ok, true);
  assert.equal(typeof signData.wormSeq, "number");
  assert.equal(typeof signData.hash, "string");

  const badSignRes = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tongMenhDe: "khong-phai-so" }),
  });
  assert.equal(badSignRes.status, 400);

  const histRes = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`);
  assert.equal(histRes.status, 200);
  const histData: any = await histRes.json();
  assert.equal(histData.entries.length, 1);
  assert.equal(histData.entries[0].curr_hash, signData.hash);

  const verifyRes = await fetch(`${baseUrl}/api/worm/verify`);
  assert.equal(verifyRes.status, 200);
  const verifyData: any = await verifyRes.json();
  assert.equal(verifyData.hopLe, true);
  assert.ok(verifyData.soBanGhi >= 1);

  // 3. Input validation guards tren cac route da tach
  const asrBad = await fetch(`${baseUrl}/api/transcribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  assert.equal(asrBad.status, 400);

  const noteBad = await fetch(`${baseUrl}/api/generate-note`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  assert.equal(noteBad.status, 400);

  const ocrBad = await fetch(`${baseUrl}/api/ocr/phieu-cu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "   " }),
  });
  assert.equal(ocrBad.status, 400);

  const extBlocked = await fetch(`${baseUrl}/api/edit-note`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ currentNote: "abc", instruction: "sua", allowExternal: false }),
  });
  assert.equal(extBlocked.status, 403);
});
