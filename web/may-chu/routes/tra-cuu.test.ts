import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-tracuu-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "tracuu.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu";

const { dangKyTraCuuRoutes } = await import("./tra-cuu");

let port = 0;
let server: http.Server;
test.before(async () => {
  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    req.nguoiDung = { id: 1, email: "1@t.vn", hoTen: "BS", vai: "bac_si" } as any;
    next();
  });
  dangKyTraCuuRoutes(app);
  server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  port = (server.address() as { port: number }).port;
});
test.after(() => {
  server?.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

/** Gọi bằng http (không qua fetch) để fetch toàn cục có thể bị giả lập. */
function goi(q: string): Promise<{ status: number; body: any }> {
  return new Promise((resolve, reject) => {
    http
      .get({ host: "127.0.0.1", port, path: `/api/pubmed-search?q=${encodeURIComponent(q)}` }, (res) => {
        let raw = "";
        res.on("data", (c) => (raw += c));
        res.on("end", () => resolve({ status: res.statusCode || 0, body: JSON.parse(raw || "{}") }));
      })
      .on("error", reject);
  });
}

test("pubmed_tu_choi_ten", async (t) => {
  const gia = t.mock.method(globalThis, "fetch", async () => new Response("{}"));
  const r = await goi("Nguyễn Văn An đau ngực");
  assert.equal(r.status, 422);
  assert.equal(r.body.code, "tu_khoa_co_danh_tinh");
  assert.equal(gia.mock.callCount(), 0, "không được gọi ra NCBI");
});

test("pubmed_tu_choi_ten_chu_thuong", async (t) => {
  const gia = t.mock.method(globalThis, "fetch", async () => new Response("{}"));
  const r = await goi("nguyễn văn an đau ngực");
  assert.equal(r.status, 422);
  assert.equal(gia.mock.callCount(), 0);
});

test("pubmed_tu_choi_so_dien_thoai", async (t) => {
  t.mock.method(globalThis, "fetch", async () => new Response("{}"));
  const r = await goi("đau ngực 0912345678");
  assert.equal(r.status, 422);
});

test("pubmed_cho_qua_tu_khoa_y_khoa", async (t) => {
  t.mock.method(
    globalThis,
    "fetch",
    async () => new Response(JSON.stringify({ esearchresult: { idlist: [] } }), { headers: { "Content-Type": "application/json" } }),
  );
  const r = await goi("chest pain troponin");
  assert.equal(r.status, 200);
});
