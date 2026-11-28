import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-portal-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "portal.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu-portal-0123456789abcdef";

const { db } = await import("../csdl");
const { taoRouterBenhNhanPortal } = await import("./benh-nhan-portal");
const { taoCaDaKy, luuCaMau, caMauDuDieuKienKy } = await import("../ho-tro-kiem-thu-ky-duyet");

let base = "";
let server: http.Server;

test.before(async () => {
  db.prepare(
    "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (1, 'bs@t.vn', 'BS Test', 'h', 'bac_si', ?)"
  ).run(Date.now());
  // Cổng người bệnh là đường XUẤT hồ sơ: các ca dùng trong kiểm thử phải đã được bác sĩ ký duyệt.
  taoCaDaKy(1, "sess_123", { ten: "Nguyễn Văn An" });
  taoCaDaKy(1, "sess_rf_1", { ten: "Trần Thị Bình" });

  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    const uidHeader = req.get("x-test-uid");
    if (uidHeader) {
      (req as any).nguoiDung = { id: Number(uidHeader), email: "bs@t.vn", hoTen: "BS Test", vai: "bac_si" };
    }
    next();
  });
  app.use(taoRouterBenhNhanPortal({ db, secret: "test-portal-secret" }));

  server = http.createServer(app);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
});

test.after(() => {
  server?.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("POST /api/benh-nhan-portal/tao-ma yêu cầu đăng nhập", async () => {
  const res = await fetch(`${base}/api/benh-nhan-portal/tao-ma`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tenBenhNhan: "BN A", chanDoan: "Tăng huyết áp" }),
  });
  assert.equal(res.status, 401);
});

const taoMa = (body: Record<string, unknown>) =>
  fetch(`${base}/api/benh-nhan-portal/tao-ma`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-test-uid": "1" },
    body: JSON.stringify(body),
  });
const soMaCong = () => (db.prepare("SELECT COUNT(*) AS n FROM cong_benh_nhan").get() as { n: number }).n;

test("tao-ma: thiếu mã ca hoặc ca chưa ký -> 409 chua_ky_duyet, không tạo mã", async () => {
  luuCaMau(1, caMauDuDieuKienKy("ca_portal_chua_ky"));
  const truoc = soMaCong();
  for (const body of [{}, { sessionId: "ca_portal_chua_ky" }, { sessionId: "ca_khong_ton_tai" }]) {
    const r = await taoMa(body);
    assert.equal(r.status, 409, JSON.stringify(body));
    const j = (await r.json()) as any;
    assert.equal(j.code, "chua_ky_duyet");
    assert.equal(j.error, "Bác sĩ chưa ký duyệt hồ sơ này (hoặc đã sửa sau khi ký) — chưa được xuất.");
  }
  assert.equal(soMaCong(), truoc);
});

test("tao-ma: ca đã ký rồi sửa -> 409; ca đã ký -> 201", async () => {
  taoCaDaKy(1, "ca_portal_sua", { suaSauKy: true });
  const sua = await taoMa({ sessionId: "ca_portal_sua" });
  assert.equal(sua.status, 409);
  assert.equal(((await sua.json()) as any).code, "chua_ky_duyet");

  taoCaDaKy(1, "ca_portal_ky");
  const ok = await taoMa({ sessionId: "ca_portal_ky" });
  assert.equal(ok.status, 201);
  assert.ok(((await ok.json()) as any).token);
});

test("tao-ma: trộn hai ca (mã ca A đã ký + tên/chẩn đoán/thuốc của ca B) -> 422, không tạo mã", async () => {
  taoCaDaKy(1, "ca_portal_a", { ten: "BN A đã ký" });
  const truoc = soMaCong();
  for (const them of [
    { tenBenhNhan: "BN B" },
    { chanDoan: "Ca B: viêm phổi" },
    { thuoc: ["Ca B: Ceftriaxon 2g sáng"] },
    { dauHieu: ["ca B"] },
    { ngayTaiKham: "mai" },
    { ghiChuNoiBo: "x" },
    { caseId: "ca_portal_b" },
  ]) {
    const r = await taoMa({ sessionId: "ca_portal_a", ...them });
    assert.equal(r.status, 422, JSON.stringify(them));
    assert.match(((await r.json()) as any).code, /^(noi_dung_tu_trinh_duyet|lech_ma_ca)$/);
  }
  assert.equal(soMaCong(), truoc);
});

test("tao-ma: xuất tab khác tab đã ký -> 422", async () => {
  taoCaDaKy(1, "ca_portal_tab");
  const r = await taoMa({ sessionId: "ca_portal_tab", tabId: "tab-soap" });
  assert.equal(r.status, 422);
  assert.equal(((await r.json()) as any).code, "lech_tab_da_ky");
  assert.equal((await taoMa({ sessionId: "ca_portal_tab", tabId: "tab-doc", ttlDays: 7 })).status, 201);
});

test("tao-ma: gói dựng từ bản đã ký; đổi tên bệnh nhân sau khi ký (ngoài băm) -> 409", async () => {
  taoCaDaKy(1, "ca_portal_doi_ten", { ten: "Tên lúc ký" });
  const ok = await taoMa({ sessionId: "ca_portal_doi_ten" });
  assert.equal(ok.status, 201);
  const { goi } = (await ok.json()) as any;
  assert.equal(goi.tenBenhNhan, "Tên lúc ký");
  assert.match(goi.chanDoan, /Rối loạn mỡ máu/);

  const truoc = soMaCong();
  luuCaMau(1, caMauDuDieuKienKy("ca_portal_doi_ten", { ten: "Tên đổi sau ký" }));
  const r = await taoMa({ sessionId: "ca_portal_doi_ten" });
  assert.equal(r.status, 409);
  assert.match(((await r.json()) as any).lyDo, /dữ liệu dùng để xuất đã đổi sau lần ký/);
  assert.equal(soMaCong(), truoc);
});

test("Bác sĩ tạo mã cổng, lọc dữ liệu nội bộ, gắn cờ thuốc mơ hồ và đọc công khai qua GET", async () => {
  const createRes = await fetch(`${base}/api/benh-nhan-portal/tao-ma`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-test-uid": "1" },
    // Chỉ gửi mã ca: máy chủ tự dựng gói từ bản đã ký (tên, chẩn đoán, thuốc).
    body: JSON.stringify({ sessionId: "sess_123" }),
  });
  assert.equal(createRes.status, 201);
  const created = (await createRes.json()) as any;
  assert.ok(created.token);
  assert.equal(created.url, `?portal=${created.token}`);
  assert.ok(created.chuKyHmac);

  // Public GET without auth
  const getRes = await fetch(`${base}/api/benh-nhan-portal/${created.token}`);
  assert.equal(getRes.status, 200);
  const portal = (await getRes.json()) as any;
  assert.equal(portal.tenBenhNhan, "Nguyễn Văn An");
  assert.ok(portal.lichUongThuoc.toi.some((t: any) => t.ten_thuoc.includes("Atorvastatin")));
  assert.ok(portal.thuocMoHoLich.some((t: any) => t.ten_thuoc.includes("Furosemide")));
  assert.ok(portal.tuongTacThucAn.some((tt: any) => tt.noi_dung.includes("bưởi chùm")));

  const serialized = JSON.stringify(portal);
  assert.ok(!serialized.includes("đau ngực từ hôm qua"), "lời thoại không lọt ra cổng công khai");
  assert.ok(!serialized.includes("Creatinine"), "ngữ cảnh nội bộ không lọt ra cổng công khai");
});

test("GET trả 404 khi thiếu token và 410 khi hết hạn", async () => {
  const r404 = await fetch(`${base}/api/benh-nhan-portal/khong_ton_tai_xyz`);
  assert.equal(r404.status, 404);

  db.prepare(
    `INSERT INTO cong_benh_nhan (token, nguoi_dung_id, session_id, goi_json, tao_luc, het_han)
     VALUES ('expired_tok', 1, NULL, '{"tenBenhNhan":"BN"}', 1000, 2000)`
  ).run();
  const r410 = await fetch(`${base}/api/benh-nhan-portal/expired_tok`);
  assert.equal(r410.status, 410);
});

test("POST /bao-cao tạo nhiệm vụ ưu tiên cao trong muc_kho khi có dấu hiệu đỏ", async () => {
  const createRes = await fetch(`${base}/api/benh-nhan-portal/tao-ma`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-test-uid": "1" },
    body: JSON.stringify({ sessionId: "sess_rf_1" }),
  });
  const { token } = (await createRes.json()) as any;

  // Check-in bình thường không tạo task
  const okRes = await fetch(`${base}/api/benh-nhan-portal/${token}/bao-cao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      moc_theo_doi: "48h",
      da_uong_du_thuoc: true,
      trieu_chung_moi: "Ngủ ngon, đỡ mệt",
      muc_do_met: 2,
      co_dau_hieu_do: false,
      dau_hieu_do_chon: [],
    }),
  });
  assert.equal(okRes.status, 200);
  const okBody = (await okRes.json()) as any;
  assert.equal(okBody.redFlagDetected, false);
  assert.equal(okBody.taskCreated, false);

  // Check-in có từ khóa nguy hiểm ("khó thở") -> tự động tạo high-priority task trong muc_kho
  const rfRes = await fetch(`${base}/api/benh-nhan-portal/${token}/bao-cao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      moc_theo_doi: "7d",
      da_uong_du_thuoc: true,
      trieu_chung_moi: "Hôm nay thấy khó thở khi nằm và phù chân",
      muc_do_met: 8,
      co_dau_hieu_do: false,
      dau_hieu_do_chon: [],
    }),
  });
  assert.equal(rfRes.status, 200);
  const rfBody = (await rfRes.json()) as any;
  assert.equal(rfBody.redFlagDetected, true);
  assert.ok(rfBody.matchedKeywords.includes("khó thở"));
  assert.equal(rfBody.taskCreated, true);
  assert.ok(rfBody.taskId);

  const row = db
    .prepare("SELECT du_lieu FROM muc_kho WHERE nguoi_dung_id = 1 AND kho = 'nhiem-vu' ORDER BY thu_tu DESC LIMIT 1")
    .get() as { du_lieu: string } | undefined;
  assert.ok(row);
  const task = JSON.parse(row.du_lieu);
  assert.equal(task.id, rfBody.taskId);
  assert.equal(task.priority, "high");
  assert.equal(task.patientName, "Trần Thị Bình");
  assert.equal(task.sessionId, "sess_rf_1");
  assert.ok(task.title.includes("CẢNH BÁO ĐỎ 7d"));
});
