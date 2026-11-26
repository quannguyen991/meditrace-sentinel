import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-asr-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "asr.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu";
process.env.MEDITRACE_INTERNAL_TOKEN = "tok";
process.env.MEDITRACE_CHO_NHAP_MS = "2000";

let soLanGoiGanVai = 0;
let dem = 0;
const mockPy = http.createServer((req, res) => {
  req.on("data", () => {});
  req.on("end", () => {
    res.writeHead(200, { "Content-Type": "application/json" });
    if (req.url === "/api/chep-am") {
      dem++;
      return res.end(JSON.stringify({ phien: `phien_${dem}`, doan: [{ speaker_id: "BS", text_original: "chào" }] }));
    }
    if (req.url === "/api/gan-vai") {
      soLanGoiGanVai++;
      return res.end(JSON.stringify({ phien: "x", doan: [] }));
    }
    if (req.url === "/api/ho-so") return res.end(JSON.stringify({ id: "ca", du_doan: "BỆNH ÁN", phat_bieu: [], ghi_chu: [] }));
    res.end("{}");
  });
});
await new Promise<void>((r) => mockPy.listen(0, "127.0.0.1", r));
process.env.MEDITRACE_API = `http://127.0.0.1:${(mockPy.address() as { port: number }).port}`;

const { db } = await import("../csdl");
const { dangKyAsrRoutes } = await import("./asr");

let base = "";
let server: http.Server;
test.before(async () => {
  for (const id of [1, 2]) {
    db.prepare(
      "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (?, ?, 'BS', 'h', 'bac_si', ?)",
    ).run(id, `${id}@t.vn`, Date.now());
  }
  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    const uid = Number(req.get("x-test-uid") || 1);
    req.nguoiDung = { id: uid, email: `${uid}@t.vn`, hoTen: "BS", vai: "bac_si" } as any;
    next();
  });
  dangKyAsrRoutes(app);
  server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
});
test.after(() => {
  server?.closeAllConnections?.();
  server?.close();
  mockPy.closeAllConnections?.();
  mockPy.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

const post = async (duong: string, body: unknown, uid = 1) => {
  const r = await fetch(`${base}${duong}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-test-uid": String(uid) },
    body: JSON.stringify(body),
  });
  return { status: r.status, body: (await r.json().catch(() => ({}))) as any };
};

test("phiên ASR gắn với người tạo: người khác không gán vai / tạo bản nháp từ phiên đó", async () => {
  const tr = await post("/api/transcribe", { audioBase64: "AAAA" }, 1);
  assert.equal(tr.status, 200);
  const phien = tr.body.sessionId;
  assert.ok(phien);

  const ganKhac = await post("/api/assign-roles", { sessionId: phien, roles: { BS: "bac_si" } }, 2);
  assert.equal(ganKhac.status, 403);
  const ganLa = await post("/api/assign-roles", { sessionId: "phien_bia", roles: { BS: "bac_si" } }, 1);
  assert.equal(ganLa.status, 403);
  assert.equal(soLanGoiGanVai, 0, "không chuyển yêu cầu sang dịch vụ khi sai chủ");

  const ganDung = await post("/api/assign-roles", { sessionId: phien, roles: { BS: "bac_si" } }, 1);
  assert.equal(ganDung.status, 200);
  assert.equal(soLanGoiGanVai, 1);

  const nhapKhac = await post("/api/generate-note", { sessionId: phien }, 2);
  assert.equal(nhapKhac.status, 403);
  const nhapDung = await post("/api/generate-note", { sessionId: phien }, 1);
  assert.ok([200, 202].includes(nhapDung.status), String(nhapDung.status));
});
