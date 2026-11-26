import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-cakham-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "cakham.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu";

const { db } = await import("../csdl");
const { dangKyCaKhamRoutes } = await import("./ca-kham");

let base = "";
let server: http.Server;
test.before(async () => {
  db.prepare(
    "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (1, 'a@t.vn', 'BS', 'h', 'bac_si', ?)",
  ).run(Date.now());
  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    req.nguoiDung = { id: 1, email: "a@t.vn", hoTen: "BS", vai: "bac_si" } as any;
    next();
  });
  dangKyCaKhamRoutes(app);
  server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
});
test.after(() => {
  server?.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

const doc = async () => (await (await fetch(`${base}/api/ca-kham`)).json()) as any;
async function putToanBo(body: Record<string, unknown>) {
  const r = await fetch(`${base}/api/ca-kham`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return { status: r.status, body: (await r.json()) as any };
}
async function putMot(ca: any, expectedUpdatedAt?: number) {
  const r = await fetch(`${base}/api/ca-kham/${ca.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session: ca, expectedUpdatedAt }),
  });
  return { status: r.status, body: (await r.json()) as any };
}

test("hai thiết bị: ghi cả danh sách không xoá ca của máy khác, có khoá lạc quan, chỉ xoá theo danh sách xoá", async () => {
  // Máy A tạo 2 ca
  const a1 = await putToanBo({ sessions: [{ id: "c1", patientIdentifier: "A" }, { id: "c2", patientIdentifier: "B" }] });
  assert.equal(a1.status, 200);
  assert.equal(typeof a1.body.updatedAt.c1, "number");

  // Máy B đọc về (có updatedAt từng ca)
  const bDoc = await doc();
  assert.deepEqual(bDoc.sessions.map((s: any) => s.id), ["c1", "c2"]);
  const banGocB = bDoc.updatedAt;
  assert.equal(banGocB.c1, a1.body.updatedAt.c1);

  // Máy A tạo thêm c3 và sửa c1 (hạt mịn, khoá lạc quan)
  await new Promise((r) => setTimeout(r, 5));
  const a2 = await putMot({ id: "c1", patientIdentifier: "A sửa" }, banGocB.c1);
  assert.equal(a2.status, 200);
  assert.equal((await putMot({ id: "c3", patientIdentifier: "C" })).status, 200);

  // Máy B (danh sách cũ: c1 bản cũ, không có c3) ghi cả danh sách, sửa c2 -> 409 vì c1 đã đổi; không ghi gì
  const b1 = await putToanBo({
    sessions: [{ id: "c1", patientIdentifier: "A" }, { id: "c2", patientIdentifier: "B sửa ở máy B" }],
    baseUpdatedAt: { c1: banGocB.c1, c2: banGocB.c2 },
  });
  assert.equal(b1.status, 409);
  assert.equal(b1.body.code, "conflict_stale_version");
  assert.deepEqual(b1.body.conflicts, ["c1"]);
  assert.equal(typeof b1.body.updatedAt.c1, "number");
  let hienTai = await doc();
  assert.deepEqual(hienTai.sessions.map((s: any) => s.id).sort(), ["c1", "c2", "c3"]);
  assert.equal(hienTai.sessions.find((s: any) => s.id === "c1").patientIdentifier, "A sửa");
  assert.equal(hienTai.sessions.find((s: any) => s.id === "c2").patientIdentifier, "B");

  // Sau khi đọc lại và gộp: B gửi c1 bản mới + c2 đã sửa, danh sách vẫn thiếu c3 -> c3 KHÔNG bị xoá
  const b1b = await putToanBo({
    sessions: [{ id: "c1", patientIdentifier: "A sửa" }, { id: "c2", patientIdentifier: "B sửa ở máy B" }],
    baseUpdatedAt: { c1: hienTai.updatedAt.c1, c2: hienTai.updatedAt.c2 },
  });
  assert.equal(b1b.status, 200, JSON.stringify(b1b.body));
  hienTai = await doc();
  assert.deepEqual(hienTai.sessions.map((s: any) => s.id).sort(), ["c1", "c2", "c3"]);
  assert.equal(hienTai.sessions.find((s: any) => s.id === "c2").patientIdentifier, "B sửa ở máy B");

  // Giao diện cũ (không gửi baseUpdatedAt) ghi danh sách chỉ có c2: vẫn ghi c2 nhưng KHÔNG xoá c1, c3
  const b2 = await putToanBo({ sessions: [{ id: "c2", patientIdentifier: "B bản cũ" }] });
  assert.equal(b2.status, 200);
  hienTai = await doc();
  assert.deepEqual(hienTai.sessions.map((s: any) => s.id).sort(), ["c1", "c2", "c3"]);

  // Máy B xoá c1 theo base cũ -> 409 (máy A vừa sửa c1), c1 vẫn còn
  const b3 = await putToanBo({ sessions: [], deletedIds: ["c1"], baseUpdatedAt: { c1: banGocB.c1 } });
  assert.equal(b3.status, 409);
  assert.ok((await doc()).sessions.some((s: any) => s.id === "c1"));

  // Xoá đúng: c3 có trong danh sách xoá với base mới nhất -> chỉ c3 bị xoá
  const moi = (await doc()).updatedAt;
  const b4 = await putToanBo({ sessions: [], deletedIds: ["c3"], baseUpdatedAt: { c3: moi.c3 } });
  assert.equal(b4.status, 200);
  assert.deepEqual((await doc()).sessions.map((s: any) => s.id).sort(), ["c1", "c2"]);
});
