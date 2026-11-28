import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-signoff-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "signoff.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu";

const { db } = await import("../csdl");
const { dangKyCaKhamRoutes } = await import("./ca-kham");
const { dangKySignOffRoutes } = await import("./sign-off");
const { khoaDuyetCuaNote } = await import("../../src/lib/kyDuyet");
const { buildSignOffCanonicalPayload } = await import("../../src/lib/compileEffectiveNote");

const NHAP = "LÝ DO KHÁM BỆNH\nđau ngực [T1]\n\nCẦN XÁC NHẬN\nsốt? [T2]";
const note = {
  caseId: "py_9",
  content: NHAP,
  propositions: [
    { id: 1, text: "đau ngực", status: "than", evidenceTurns: [1] },
    { id: 2, text: "sốt?", status: "can_xac_nhan", evidenceTurns: [2] },
  ],
};
function ca(id: string, quyet: Record<number, string>, banSua: Record<number, string> = {}) {
  return {
    id,
    patientIdentifier: "BN thử",
    activeTabId: "tab-transcript",
    tabs: [
      { id: "tab-transcript", title: "Lời thoại", type: "transcript", content: "BS: chào" },
      { id: "tab-soap", title: "Bệnh án SOAP", type: "soap", content: "S: đau ngực" },
      { id: "tab-doc", title: "Bản nháp hồ sơ", type: "custom", content: NHAP },
    ],
    note,
    duyet: { khoa: khoaDuyetCuaNote(note), quyet, banSua },
  };
}

let base = "";
let server: http.Server;
test.before(async () => {
  for (const [id, email] of [
    [1, "a@t.vn"],
    [2, "b@t.vn"],
  ] as const) {
    db.prepare(
      "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (?, ?, 'BS', 'h', 'bac_si', ?)",
    ).run(id, email, Date.now());
  }
  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    const uid = Number(req.get("x-test-uid") || 1);
    req.nguoiDung = { id: uid, email: `${uid}@t.vn`, hoTen: "BS", vai: "bac_si" } as any;
    next();
  });
  dangKyCaKhamRoutes(app);
  dangKySignOffRoutes(app);
  server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
});
test.after(() => {
  server?.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

async function luu(c: unknown, uid = 1) {
  const r = await fetch(`${base}/api/ca-kham/${(c as any).id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", "x-test-uid": String(uid) },
    body: JSON.stringify({ session: c }),
  });
  assert.equal(r.status, 200);
}
async function ky(id: string, body: Record<string, unknown>, uid = 1) {
  const r = await fetch(`${base}/api/sessions/${id}/sign-off`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-test-uid": String(uid) },
    body: JSON.stringify(body),
  });
  return { status: r.status, body: (await r.json()) as any };
}
const soDongWorm = () => (db.prepare("SELECT COUNT(*) AS n FROM worm_signoff").get() as { n: number }).n;

test("ký duyệt ca không tồn tại bị từ chối, không ghi WORM", async () => {
  const r = await ky("ca_bia_ra", { tongMenhDe: 3, soGiu: 3, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "x", soChuaXacNhan: 0 });
  assert.equal(r.status, 404);
  assert.equal(soDongWorm(), 0);
});

test("ca của bác sĩ khác: 403", async () => {
  await luu(ca("ca_cua_bs2", { 1: "giu", 2: "giu" }), 2);
  const r = await ky("ca_cua_bs2", {});
  assert.equal(r.status, 403);
  assert.equal(soDongWorm(), 0);
});

test("bỏ trống soChuaXacNhan vẫn bị chặn khi máy chủ thấy còn mục cần xác nhận", async () => {
  await luu(ca("ca_chua_duyet", { 1: "giu" }));
  const r = await ky("ca_chua_duyet", { tongMenhDe: 2, soGiu: 2, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "h" });
  assert.equal(r.status, 400);
  assert.equal(r.body.code, "con_muc_can_xac_nhan");
  const r2 = await ky("ca_chua_duyet", { soChuaXacNhan: 0 });
  assert.equal(r2.status, 400, "client khai soChuaXacNhan=0 cũng không qua được");
  assert.equal(soDongWorm(), 0);
});

test("số liệu và băm do máy chủ tính; số client gửi bị bỏ qua; băm lệch thì 409", async () => {
  await luu(ca("ca_du", { 1: "giu", 2: "sua" }, { 2: "không sốt" }));
  const mongDoi = crypto
    .createHash("sha256")
    .update(buildSignOffCanonicalPayload(NHAP, { 1: "giu", 2: "sua" }, { 2: "không sốt" }))
    .digest("hex");

  const lech = await ky("ca_du", { contentHash: "bam-gia-mao" });
  assert.equal(lech.status, 409);
  assert.equal(lech.body.code, "lech_noi_dung");

  const r = await ky("ca_du", { tongMenhDe: 99, soGiu: 99, soSua: 0, soBo: 0, tyLeCoNguon: 100, soChuaXacNhan: 0, tabId: "tab-transcript" });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  assert.deepEqual(
    [r.body.tongMenhDe, r.body.soGiu, r.body.soSua, r.body.soBo, r.body.tyLeCoNguon],
    [2, 1, 1, 0, 100],
  );
  assert.equal(r.body.contentHash, mongDoi);
  assert.equal(r.body.tabId, "tab-doc", "tab không phải bệnh án (lời thoại) không được chọn để băm");
  const dong = db.prepare("SELECT content_hash, tong_menh_de, nguoi_dung_id FROM worm_signoff ORDER BY seq DESC LIMIT 1").get() as any;
  assert.equal(dong.content_hash, mongDoi);
  assert.equal(dong.tong_menh_de, 2);
  assert.equal(dong.nguoi_dung_id, 1);

  const soap = await ky("ca_du", { tabId: "tab-soap", contentHash: undefined });
  assert.equal(soap.status, 200);
  assert.equal(soap.body.tabId, "tab-soap");
});

test("ký duyệt ghi bản chụp máy chủ đúng tab đã ký; chốt xuất đối chiếu đúng tab đó", async () => {
  const { kiemDaKyChoXuat } = await import("../kiem-ky-may-chu");
  await luu(ca("ca_ban_chup", { 1: "giu", 2: "giu" }));
  const r = await ky("ca_ban_chup", { tabId: "tab-soap" });
  assert.equal(r.status, 200);
  const kq = kiemDaKyChoXuat(1, "ca_ban_chup") as any;
  assert.equal(kq.duoc, true, JSON.stringify(kq));
  assert.equal(kq.banKy?.tabId, "tab-soap");
  assert.equal(kq.banKy?.wormSeq, r.body.wormSeq);

  // Sửa đúng tab đã ký (SOAP) dù tab bản nháp còn nguyên: không được xuất.
  const sua = ca("ca_ban_chup", { 1: "giu", 2: "giu" });
  sua.tabs[1].content = "S: sửa sau khi ký";
  await luu(sua);
  assert.equal(kiemDaKyChoXuat(1, "ca_ban_chup").duoc, false);
});
