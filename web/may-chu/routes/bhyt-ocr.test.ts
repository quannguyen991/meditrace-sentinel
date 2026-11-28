import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-bhyt-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "bhyt.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu-bhyt-0123456789abcdef";
process.env.MEDITRACE_INTERNAL_TOKEN = "bhyt-test-internal-token";

// Dịch vụ Python giả: ghi lại các lần gọi; chặn xuất thì dịch vụ không được gọi.
const daGoi: string[] = [];
const mockPy = http.createServer((req, res) => {
  req.resume();
  req.on("end", () => {
    daGoi.push(req.url || "");
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ goi_xml_1_5: { XML1: "<XML1/>" }, duong: req.url }));
  });
});
await new Promise<void>((r) => mockPy.listen(0, "127.0.0.1", r));
process.env.MEDITRACE_API = `http://127.0.0.1:${(mockPy.address() as { port: number }).port}`;

const { db } = await import("../csdl");
const { dangKyBhytOcrRoutes } = await import("./bhyt-ocr");
const { taoCaDaKy, luuCaMau, caMauDuDieuKienKy } = await import("../ho-tro-kiem-thu-ky-duyet");

let base = "";
let server: http.Server;
test.before(async () => {
  db.prepare(
    "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (1, 'a@t.vn', 'BS', 'h', 'bac_si', ?)",
  ).run(Date.now());
  luuCaMau(1, caMauDuDieuKienKy("ca_chua_ky"));
  taoCaDaKy(1, "ca_sua_sau_ky", { suaSauKy: true });
  taoCaDaKy(1, "ca_da_ky");

  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    req.nguoiDung = { id: 1, email: "a@t.vn", hoTen: "BS", vai: "bac_si" } as any;
    next();
  });
  dangKyBhytOcrRoutes(app);
  server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
});
test.after(() => {
  server?.close();
  mockPy.closeAllConnections?.();
  mockPy.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

const post = async (duong: string, body: Record<string, unknown>) => {
  const r = await fetch(`${base}${duong}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ propositions: [{ id: 1, text: "đau ngực", evidenceTurns: [1] }], transcript: "BS: chào", ...body }),
  });
  return { status: r.status, body: (await r.json()) as any };
};
const LOI = "Bác sĩ chưa ký duyệt hồ sơ này (hoặc đã sửa sau khi ký) — chưa được xuất.";

for (const duong of ["/api/bhyt/precheck", "/api/bhyt/recompile", "/api/fhir/recompile"]) {
  test(`${duong}: thiếu mã ca / chưa ký / sửa sau ký -> 409, dịch vụ không được gọi`, async () => {
    daGoi.length = 0;
    for (const body of [{}, { sessionId: "ca_chua_ky" }, { sessionId: "ca_sua_sau_ky" }, { sessionId: "ca_khong_co" }]) {
      const r = await post(duong, body);
      assert.equal(r.status, 409, `${duong} ${JSON.stringify(body)}`);
      assert.equal(r.body.code, "chua_ky_duyet");
      assert.equal(r.body.error, LOI);
    }
    assert.deepEqual(daGoi, []);
  });

  test(`${duong}: ca đã ký, chưa sửa -> 200`, async () => {
    const r = await post(duong, { sessionId: "ca_da_ky" });
    assert.equal(r.status, 200, JSON.stringify(r.body));
    assert.ok(r.body.goi_xml_1_5);
  });
}

test("recompile chấp nhận mã ca qua caseId khi không gửi sessionId", async () => {
  const r = await post("/api/bhyt/recompile", { caseId: "ca_da_ky" });
  assert.equal(r.status, 200);
  const chan = await post("/api/bhyt/recompile", { caseId: "ca_chua_ky" });
  assert.equal(chan.status, 409);
});

test("/api/ocr/phieu-cu (chỉ đọc phiếu, không xuất hồ sơ) vẫn mở", async () => {
  const r = await fetch(`${base}/api/ocr/phieu-cu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "Creatinine: 120 umol/L" }),
  });
  assert.equal(r.status, 200);
});
