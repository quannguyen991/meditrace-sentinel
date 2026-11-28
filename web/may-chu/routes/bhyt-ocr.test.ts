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
const thanDaGoi: any[] = [];
const mockPy = http.createServer((req, res) => {
  let raw = "";
  req.on("data", (c) => (raw += c));
  req.on("end", () => {
    daGoi.push(req.url || "");
    thanDaGoi.push(JSON.parse(raw || "{}"));
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ goi_xml_1_5: { XML1: "<XML1/>" }, duong: req.url }));
  });
});
await new Promise<void>((r) => mockPy.listen(0, "127.0.0.1", r));
process.env.MEDITRACE_API = `http://127.0.0.1:${(mockPy.address() as { port: number }).port}`;

const { db } = await import("../csdl");
const { dangKyBhytOcrRoutes } = await import("./bhyt-ocr");
const { taoCaDaKy, luuCaMau, caMauDuDieuKienKy } = await import("../ho-tro-kiem-thu-ky-duyet");
const { xayNguCanhChoTaoHoSo } = await import("../../src/lib/nguCanhTroLy");

let base = "";
let server: http.Server;
test.before(async () => {
  db.prepare(
    "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (1, 'a@t.vn', 'BS', 'h', 'bac_si', ?)",
  ).run(Date.now());
  luuCaMau(1, caMauDuDieuKienKy("ca_chua_ky"));
  taoCaDaKy(1, "ca_sua_sau_ky", { suaSauKy: true });
  taoCaDaKy(1, "ca_da_ky");
  taoCaDaKy(1, "ca_b_chua_ky_khac", { ten: "BN B", transcript: "BS: ca B" });

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
    body: JSON.stringify(body),
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

/** Thân yêu cầu y hệt NoteEditorView gửi khi màn hình khớp ca đã lưu (mệnh đề hiệu lực, lời thoại, thông tin BN). */
function thanNhuGiaoDien(ca: any) {
  const quyet = ca.duyet.quyet as Record<number, string>;
  const banSua = ca.duyet.banSua as Record<number, string>;
  return {
    propositions: ca.note.propositions
      .filter((p: any) => quyet[p.id] !== "bo")
      .map((p: any) => (quyet[p.id] === "sua" && banSua[p.id]?.trim() ? { ...p, text: banSua[p.id].trim() } : p)),
    transcript: ca.note.transcript || ca.transcript,
    // App.tsx: xayNguCanhChoTaoHoSo({ sessionId: currentSession.id, patientIdentifier, patientSubtitle, tabs, contextNotes })
    thong_tin_benh_nhan: xayNguCanhChoTaoHoSo({ ...ca, sessionId: ca.id }).thong_tin_benh_nhan || null,
  };
}

test("precheck: chỉ gửi mã ca -> máy chủ tự dựng gói từ bản đã ký (mệnh đề hiệu lực, lời thoại, thông tin BN)", async () => {
  thanDaGoi.length = 0;
  const r = await post("/api/bhyt/precheck", { sessionId: "ca_da_ky" });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  const goi = thanDaGoi[0];
  assert.deepEqual(
    goi.propositions.map((p: any) => [p.id, p.text]),
    [
      [1, "đau ngực"],
      [2, "không sốt"],
    ],
    "mệnh đề bị bỏ không ra gói; mệnh đề sửa dùng bản sửa",
  );
  assert.match(goi.transcript, /Atorvastatin/);
  assert.equal(goi.thong_tin_benh_nhan?.can_nang_kg, 15);
});

test("precheck: thân yêu cầu khớp bản đã ký (đúng như giao diện gửi) -> 200", async () => {
  const r = await post("/api/bhyt/precheck", { sessionId: "ca_da_ky", ...thanNhuGiaoDien(caMauDuDieuKienKy("ca_da_ky")) });
  assert.equal(r.status, 200, JSON.stringify(r.body));
});

test("trộn hai ca: mã ca A đã ký + nội dung ca B -> 422, dịch vụ không được gọi", async () => {
  daGoi.length = 0;
  const caB = caMauDuDieuKienKy("ca_b_chua_ky_khac", { ten: "BN B", transcript: "BS: ca B" });
  const thanB = thanNhuGiaoDien({ ...caB, note: { ...caB.note, propositions: [{ id: 9, text: "Ca B: viêm phổi", evidenceTurns: [1] }] } });
  for (const duong of ["/api/bhyt/precheck", "/api/bhyt/recompile", "/api/fhir/recompile"]) {
    for (const body of [
      { sessionId: "ca_da_ky", propositions: thanB.propositions },
      { sessionId: "ca_da_ky", transcript: "BS: ca B" },
      { sessionId: "ca_da_ky", thong_tin_benh_nhan: { tuoi: 70, can_nang_kg: 50 } },
      { sessionId: "ca_da_ky", patientInfo: { tuoi: 70 } },
      { sessionId: "ca_da_ky", noteSections: { chan_doan: "Ca B" } },
      { sessionId: "ca_da_ky", du_lieu_xet_nghiem: { kali: 7 } },
    ]) {
      const r = await post(duong, body);
      assert.equal(r.status, 422, `${duong} ${JSON.stringify(body)}`);
      assert.equal(r.body.code, "noi_dung_khac_ban_ky");
    }
    const lech = await post(duong, { sessionId: "ca_da_ky", caseId: "ca_b_chua_ky_khac" });
    assert.equal(lech.status, 422, `${duong} sessionId/caseId lệch`);
    assert.equal(lech.body.code, "lech_ma_ca");
  }
  assert.deepEqual(daGoi, []);
});

test("dữ liệu xuất (ngoài băm) đổi sau khi ký: tên / mệnh đề / lời thoại / xét nghiệm -> 409; không đổi -> 200", async () => {
  const doi: Array<[string, (ca: any) => void]> = [
    ["cân nặng", (ca) => (ca.patientSubtitle = "Nam, 4 tuổi, 30 kg")],
    ["tên", (ca) => (ca.patientIdentifier = "Tên khác")],
    ["mệnh đề", (ca) => (ca.note.propositions[0].text = "đau bụng")],
    ["lời thoại", (ca) => (ca.note.transcript = "BS: lời thoại khác")],
    ["xét nghiệm", (ca) => (ca.tabs.find((t: any) => t.type === "context").content = "Creatinine 300 umol/L")],
  ];
  for (const [nhan, sua] of doi) {
    const id = `ca_doi_${doi.findIndex((d) => d[0] === nhan)}`;
    taoCaDaKy(1, id);
    assert.equal((await post("/api/bhyt/precheck", { sessionId: id })).status, 200, `${nhan}: trước khi đổi`);
    const sau: any = caMauDuDieuKienKy(id);
    sua(sau);
    luuCaMau(1, sau);
    daGoi.length = 0;
    for (const body of [{ sessionId: id }, { sessionId: id, ...thanNhuGiaoDien(sau) }]) {
      const r = await post("/api/bhyt/precheck", body);
      assert.equal(r.status, 409, `${nhan}: ${JSON.stringify(body).slice(0, 60)}`);
      assert.match(r.body.lyDo, /dữ liệu dùng để xuất đã đổi sau lần ký/);
    }
    assert.deepEqual(daGoi, []);
  }
});

test("xuất tab khác tab đã ký -> 422", async () => {
  const r = await post("/api/bhyt/recompile", { sessionId: "ca_da_ky", tabId: "tab-soap" });
  assert.equal(r.status, 422);
  assert.equal(r.body.code, "lech_tab_da_ky");
  const ok = await post("/api/bhyt/recompile", { sessionId: "ca_da_ky", tabId: "tab-doc" });
  assert.equal(ok.status, 200);
});

test("recompile: caseId trong gói gửi dịch vụ là mã ca đã ký", async () => {
  thanDaGoi.length = 0;
  const r = await post("/api/fhir/recompile", { caseId: "ca_da_ky" });
  assert.equal(r.status, 200);
  assert.equal(thanDaGoi[0].caseId, "ca_da_ky");
  assert.equal(thanDaGoi[0].ma_ca, "ca_da_ky");
});
