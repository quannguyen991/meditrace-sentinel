/**
 * Cam đoan thủ thuật & đi buồng nội trú: dữ liệu hồ sơ phải lấy từ bản bác sĩ đã ký (không lấy từ thân yêu cầu),
 * mọi ca liên quan (hôm nay VÀ hôm qua) phải đã ký, mã ca lệch -> 422, nội dung gửi kèm khác bản đã ký -> 422.
 */
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-boost-ky-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "boost-ky.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu-boost-ky-0123456789abcdef";
process.env.MEDITRACE_INTERNAL_TOKEN = "boost-ky-test-internal-token";

const daGoi: Array<{ url: string; body: any }> = [];
const mockPy = http.createServer((req, res) => {
  let raw = "";
  req.on("data", (c) => (raw += c));
  req.on("end", () => {
    const body = JSON.parse(raw || "{}");
    daGoi.push({ url: req.url || "", body });
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, ngay_dieu_tri_thu: body.ngay_dieu_tri_thu ?? null }));
  });
});
await new Promise<void>((r) => mockPy.listen(0, "127.0.0.1", r));
process.env.MEDITRACE_API = `http://127.0.0.1:${(mockPy.address() as { port: number }).port}`;

const { db } = await import("../csdl");
const { dangKyBoostLamSangRoutes } = await import("./boost-lam-sang");
const { caMauDuDieuKienKy, luuCaMau, taoCaDaKy } = await import("../ho-tro-kiem-thu-ky-duyet");
const { xayNguCanhChoTaoHoSo } = await import("../../src/lib/nguCanhTroLy");

const MD_CAM_DOAN = [
  { id: 1, text: "chỉ định nội soi dạ dày gây mê", status: "than", evidenceTurns: [1] },
  { id: 2, text: "bệnh nhân đồng ý làm", status: "than", evidenceTurns: [2] },
];
const LT_CAM_DOAN = "BS: Bác cần nội soi dạ dày gây mê, nguy cơ sặc.\nBN: Tôi đã hiểu và đồng ý làm.";
const MD_HOM_NAY = [{ id: 2, text: "tăng liều Furosemid 40mg tiêm tĩnh mạch", status: "than", evidenceTurns: [1] }];
const MD_HOM_QUA = [{ id: 1, text: "Furosemid 20mg uống", status: "than", evidenceTurns: [1] }];
const LT_HOM_NAY = "BS: Hôm nay ngày thứ 3, còn phù nhẹ, tăng liều Furosemid 40mg.";

const caCamDoan = () =>
  caMauDuDieuKienKy("ca_cam_doan", { menhDe: MD_CAM_DOAN, transcript: LT_CAM_DOAN, segments: [{ luot: 2, start_s: 4.2, end_s: 7.1 }] });
const caHomNay = () => caMauDuDieuKienKy("ca_hom_nay", { menhDe: MD_HOM_NAY, transcriptCa: LT_HOM_NAY });
const caHomQua = () => caMauDuDieuKienKy("ca_hom_qua", { menhDe: MD_HOM_QUA });

let base = "";
let server: http.Server;
test.before(async () => {
  db.prepare(
    "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (1, 'a@t.vn', 'BS', 'h', 'bac_si', ?)",
  ).run(Date.now());
  luuCaMau(1, caCamDoan());
  taoCaDaKy(1, "ca_cam_doan", { menhDe: MD_CAM_DOAN, transcript: LT_CAM_DOAN, segments: [{ luot: 2, start_s: 4.2, end_s: 7.1 }] });
  taoCaDaKy(1, "ca_b", { ten: "BN B", transcript: "BS: ca B viêm phổi" });
  taoCaDaKy(1, "ca_hom_nay", { menhDe: MD_HOM_NAY, transcriptCa: LT_HOM_NAY });
  taoCaDaKy(1, "ca_hom_qua", { menhDe: MD_HOM_QUA });
  luuCaMau(1, caMauDuDieuKienKy("ca_hom_qua_chua_ky", { menhDe: MD_HOM_QUA }));

  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    req.nguoiDung = { id: 1, email: "a@t.vn", hoTen: "BS", vai: "bac_si" } as any;
    next();
  });
  dangKyBoostLamSangRoutes(app);
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
const ttbn = (ca: any) => xayNguCanhChoTaoHoSo({ ...ca, sessionId: ca.id }).thong_tin_benh_nhan || null;

/* ------------------------------------------------------------------ cam đoan thủ thuật */

test("cam đoan: chỉ gửi mã ca + tên thủ thuật -> máy chủ lấy mệnh đề, lời thoại, mốc âm thanh từ bản đã ký", async () => {
  daGoi.length = 0;
  const r = await post("/api/clinical/informed-consent", { sessionId: "ca_cam_doan", procedureName: "Nội soi dạ dày" });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  const goi = daGoi[0].body;
  assert.equal(daGoi[0].url, "/api/cam-doan-thu-thuat");
  assert.deepEqual(goi.propositions.map((p: any) => p.text), MD_CAM_DOAN.map((p) => p.text));
  assert.equal(goi.transcript, LT_CAM_DOAN);
  assert.deepEqual(goi.metadata_am_thanh, [{ luot: 2, start_ms: 4200, end_ms: 7100 }]);
  assert.equal(goi.ten_thu_thuat, "Nội soi dạ dày");
  assert.ok(!JSON.stringify(goi.propositions).includes("Nội soi dạ dày\""), "tên thủ thuật không trộn vào mệnh đề hồ sơ");
});

test("cam đoan: thân yêu cầu y hệt modal gửi (khớp bản đã ký) -> 200", async () => {
  const ca = caCamDoan();
  const r = await post("/api/clinical/informed-consent", {
    sessionId: "ca_cam_doan",
    propositions: ca.note.propositions,
    transcript: LT_CAM_DOAN,
    thong_tin_benh_nhan: ttbn(ca),
    doctorNotes: { rui_ro: "bác sĩ ghi thêm" },
    stampWorm: false,
  });
  assert.equal(r.status, 200, JSON.stringify(r.body));
});

test("cam đoan: mã ca A đã ký + nội dung ca B -> 422, không gọi Python, không ghi WORM", async () => {
  daGoi.length = 0;
  const soWorm = () => (db.prepare("SELECT COUNT(*) AS n FROM worm_signoff").get() as { n: number }).n;
  const truoc = soWorm();
  for (const them of [
    { propositions: [{ id: 9, text: "Ca B: mổ ruột thừa", evidenceTurns: [1] }] },
    { transcript: "BS: ca B viêm phổi" },
    { thong_tin_benh_nhan: { tuoi: 70 } },
    { audioMetadata: [{ luot: 2, start_ms: 1, end_ms: 2, speaker_id: "BN" }] },
  ]) {
    const r = await post("/api/clinical/informed-consent", { sessionId: "ca_cam_doan", stampWorm: true, ...them });
    assert.equal(r.status, 422, JSON.stringify(them));
    assert.equal(r.body.code, "noi_dung_khac_ban_ky");
  }
  const lech = await post("/api/clinical/informed-consent", { sessionId: "ca_cam_doan", caseId: "ca_b", stampWorm: true });
  assert.equal(lech.status, 422);
  assert.equal(lech.body.code, "lech_ma_ca");
  assert.deepEqual(daGoi, []);
  assert.equal(soWorm(), truoc);
});

test("cam đoan: đóng dấu WORM băm theo bản đã ký", async () => {
  const r = await post("/api/clinical/informed-consent", { sessionId: "ca_cam_doan", stampWorm: true, procedureName: "Nội soi" });
  assert.equal(r.status, 200);
  const mong = crypto
    .createHash("sha256")
    .update(JSON.stringify({ sessionId: "ca_cam_doan", transcript: LT_CAM_DOAN, propositions: MD_CAM_DOAN, checkedAt: r.body.checkedAt }))
    .digest("hex");
  assert.equal(r.body.consentHash, mong);
});

/* ------------------------------------------------------------------ đi buồng nội trú */

test("đi buồng: hai ca đã ký -> máy chủ lấy mệnh đề hôm nay/hôm qua + lời thoại từ bản đã ký", async () => {
  daGoi.length = 0;
  const r = await post("/api/inpatient/ward-round-diff", {
    sessionId: "ca_hom_nay",
    currentSessionId: "ca_hom_nay",
    previousSessionId: "ca_hom_qua",
    dayNumber: 3,
  });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  const goi = daGoi[0].body;
  assert.deepEqual(goi.todayPropositions.map((p: any) => p.text), MD_HOM_NAY.map((p) => p.text));
  assert.deepEqual(goi.yesterdayPropositions.map((p: any) => p.text), MD_HOM_QUA.map((p) => p.text));
  assert.equal(goi.todayTranscript, LT_HOM_NAY);
  assert.equal(goi.ngay_dieu_tri_thu, 3);
});

test("đi buồng: thân yêu cầu y hệt modal gửi (khớp hai bản đã ký) -> 200", async () => {
  const r = await post("/api/inpatient/ward-round-diff", {
    sessionId: "ca_hom_nay",
    todayPropositions: caHomNay().note.propositions,
    yesterdayPropositions: caHomQua().note.propositions,
    todayTranscript: LT_HOM_NAY,
    previousSessionId: "ca_hom_qua",
    currentSessionId: "ca_hom_nay",
  });
  assert.equal(r.status, 200, JSON.stringify(r.body));
});

test("đi buồng: ca hôm qua chưa ký / không có -> 409, không gọi Python", async () => {
  daGoi.length = 0;
  for (const truoc of ["ca_hom_qua_chua_ky", "ca_khong_co"]) {
    const r = await post("/api/inpatient/ward-round-diff", { sessionId: "ca_hom_nay", previousSessionId: truoc });
    assert.equal(r.status, 409, truoc);
    assert.equal(r.body.code, "chua_ky_duyet");
  }
  assert.deepEqual(daGoi, []);
});

test("đi buồng: mã ca lệch hoặc nội dung khác bản đã ký -> 422, không gọi Python", async () => {
  daGoi.length = 0;
  for (const body of [
    { sessionId: "ca_hom_nay", currentSessionId: "ca_b", previousSessionId: "ca_hom_qua" },
    { sessionId: "ca_hom_nay", caseId: "ca_b", previousSessionId: "ca_hom_qua" },
    { currentSessionId: "ca_hom_nay", caseId: "ca_b", previousSessionId: "ca_hom_qua" },
  ]) {
    const r = await post("/api/inpatient/ward-round-diff", body);
    assert.equal(r.status, 422, JSON.stringify(body));
    assert.equal(r.body.code, "lech_ma_ca");
  }
  for (const them of [
    { todayPropositions: [{ id: 9, text: "Ca B: Ceftriaxon 2g", evidenceTurns: [1] }] },
    { yesterdayPropositions: [{ id: 9, text: "Ca B: hôm qua", evidenceTurns: [1] }] },
    { todayTranscript: "BS: ca B" },
    { transcriptToday: "BS: ca B" },
  ]) {
    const r = await post("/api/inpatient/ward-round-diff", { sessionId: "ca_hom_nay", previousSessionId: "ca_hom_qua", ...them });
    assert.equal(r.status, 422, JSON.stringify(them));
    assert.equal(r.body.code, "noi_dung_khac_ban_ky");
  }
  // Không có ca hôm qua đã ký thì không được tự gửi mệnh đề hôm qua.
  const khongCaTruoc = await post("/api/inpatient/ward-round-diff", {
    sessionId: "ca_hom_nay",
    yesterdayPropositions: MD_HOM_QUA,
  });
  assert.equal(khongCaTruoc.status, 422);
  assert.deepEqual(daGoi, []);
});

test("đi buồng: chỉ ca hôm nay (không có ca trước) -> 200 với mệnh đề hôm qua rỗng", async () => {
  daGoi.length = 0;
  const r = await post("/api/inpatient/ward-round-diff", { currentSessionId: "ca_hom_nay" });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.deepEqual(daGoi[0].body.yesterdayPropositions, []);
});
