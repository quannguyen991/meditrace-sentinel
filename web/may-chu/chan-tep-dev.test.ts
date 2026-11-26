import assert from "node:assert/strict";
import http from "node:http";
import path from "node:path";
import test from "node:test";
import express from "express";
import { cauHinhViteDev, chanTepNhayCam, diaChiLangNghe, laDuongDanCam } from "./chan-tep-dev";

const GOC = path.resolve("D:/du-an/web");
const fsGoc = `/@fs/${GOC.replace(/\\/g, "/")}`;

test("laDuongDanCam: chặn CSDL, lược đồ, mã máy chủ, .env, khoá; cho qua mã giao diện", () => {
  const cam = [
    "/data/meditrace.db",
    "/data/meditrace.db-wal",
    "/data/meditrace.db.anchor.json",
    "/data/worm_signoff_log.jsonl",
    "/DATA/Meditrace.DB",
    "/db/schema.sql",
    "/may-chu/tai-khoan.ts",
    "/may-chu/routes/llm-ngoai.ts?import",
    "/server.ts",
    "/server.ts?raw",
    "/dist/server.cjs",
    "/.env",
    "/.env.local",
    "/src/../data/meditrace.db",
    "/%64ata/meditrace.db",
    "/data%2Fmeditrace.db",
    "/may-chu%5Ccsdl.ts",
    `${fsGoc}/data/meditrace.db`,
    `${fsGoc}/may-chu/csdl.ts`,
    "/@fs/C:/Users/x/.meditrace/worm.key",
    "/khac/thu-muc/backup.sqlite",
    "/.git/config",
  ];
  for (const u of cam) assert.equal(laDuongDanCam(u, GOC), true, `phải chặn ${u}`);

  const choQua = [
    "/",
    "/index.html",
    "/src/main.tsx",
    "/src/data/mockData.ts",
    "/src/lib/compileEffectiveNote.ts?t=123",
    "/@vite/client",
    "/@react-refresh",
    "/node_modules/.vite/deps/react.js?v=1",
    `${fsGoc}/src/App.tsx`,
    "/@fs/D:/khac/node_modules/vite/dist/client/env.mjs",
    "/favicon.svg",
  ];
  for (const u of choQua) assert.equal(laDuongDanCam(u, GOC), false, `không được chặn ${u}`);
});

test("chanTepNhayCam: Express trả 404 cho tệp nhạy cảm trước khi tới Vite", async (t) => {
  const app = express();
  app.use(chanTepNhayCam(GOC));
  app.use((_req, res) => res.status(200).send("vite"));
  const server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  t.after(() => server.close());
  const base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
  for (const u of ["/data/meditrace.db", "/db/schema.sql", "/may-chu/tai-khoan.ts", "/server.ts", "/.env.local"]) {
    const r = await fetch(base + u);
    assert.equal(r.status, 404, u);
    assert.doesNotMatch(await r.text(), /vite/);
  }
  const ok = await fetch(`${base}/src/main.tsx`);
  assert.equal(ok.status, 200);
});

test("cauHinhViteDev: không allowedHosts=true, có fs.deny; dev mặc định chỉ nghe 127.0.0.1", () => {
  const ch = cauHinhViteDev(GOC, {});
  assert.notEqual(ch.allowedHosts, true);
  assert.equal(ch.middlewareMode, true);
  assert.ok(ch.fs.deny.some((g) => g.includes("may-chu")));
  assert.ok(ch.fs.deny.some((g) => g.includes("*.db")));
  assert.deepEqual(cauHinhViteDev(GOC, { MEDITRACE_ALLOWED_HOSTS: "a.example.vn, b.example.vn" }).allowedHosts, [
    "a.example.vn",
    "b.example.vn",
  ]);

  assert.equal(diaChiLangNghe({}, false), "127.0.0.1");
  assert.equal(diaChiLangNghe({ HOST: "0.0.0.0" }, false), "0.0.0.0");
  assert.equal(diaChiLangNghe({}, true), undefined, "production giữ hành vi cũ trừ khi đặt HOST");
  assert.equal(diaChiLangNghe({ HOST: "127.0.0.1" }, true), "127.0.0.1");
});
