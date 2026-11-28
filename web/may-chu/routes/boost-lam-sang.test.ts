import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import test from "node:test";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-boost-bff-"));
const mainDbPath = path.join(tmpDir, "boost-legacy-upgrade.db");

// Dựng sẵn tệp CSDL kiểu CŨ với CHECK (kho IN ('tra-cuu', 'mau-van-ban')) TRƯỚC KHI import csdl.ts
// để chứng minh khởi động máy chủ tự động migrate `muc_kho` an toàn mà không mất dữ liệu cũ.
{
  const seedDb = new DatabaseSync(mainDbPath);
  seedDb.exec(`
    PRAGMA foreign_keys = ON;
    CREATE TABLE nguoi_dung (
      id              INTEGER PRIMARY KEY,
      email           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
      ho_ten          TEXT    NOT NULL,
      mat_khau_bam    TEXT    NOT NULL,
      vai             TEXT    NOT NULL DEFAULT 'bac_si' CHECK (vai IN ('quan_tri', 'bac_si')),
      tao_luc         INTEGER NOT NULL,
      dang_nhap_cuoi  INTEGER
    );
    CREATE TABLE muc_kho (
      nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
      kho            TEXT    NOT NULL CHECK (kho IN ('tra-cuu', 'mau-van-ban')),
      thu_tu         INTEGER NOT NULL,
      du_lieu        TEXT    NOT NULL CHECK (json_valid(du_lieu)),
      PRIMARY KEY (nguoi_dung_id, kho, thu_tu)
    );
    INSERT INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc)
      VALUES (1, 'bs1@test.local', 'BS Một', 'hash', 'bac_si', 1700000000000);
    INSERT INTO muc_kho (nguoi_dung_id, kho, thu_tu, du_lieu)
      VALUES (1, 'tra-cuu', 0, '{"id":"tc_cu_1","query":"tăng huyết áp"}');
  `);
  // Xác nhận bảng cũ thực sự chặn 'benh-nhan' trước khi nâng cấp
  assert.throws(() => {
    seedDb
      .prepare("INSERT INTO muc_kho (nguoi_dung_id, kho, thu_tu, du_lieu) VALUES (1, 'benh-nhan', 0, '{}')")
      .run();
  }, /CHECK constraint failed/);
  seedDb.close();
}

const capturedPyRequests: Array<{ url: string; body: any }> = [];
const mockPyServer = http.createServer((req, res) => {
  let raw = "";
  req.on("data", (c) => (raw += c));
  req.on("end", () => {
    let parsed: any = {};
    try {
      parsed = raw ? JSON.parse(raw) : {};
    } catch {}
    capturedPyRequests.push({ url: req.url || "", body: parsed });

    res.writeHead(200, { "Content-Type": "application/json" });
    if (req.url === "/api/bhyt/precheck") {
      res.end(
        JSON.stringify({
          ma_icd10_chinh: { ma_icd10: "J02.9", ten_benh_byt: "Viêm họng cấp" },
          icd10_chi_tiet: [{ ma: "J02.9", ten: "Viêm họng cấp", khoa: "Hô hấp" }],
          canh_bao_xuat_toan: [],
          nhan_thong_tin_bn: parsed.thong_tin_benh_nhan ?? null,
        }),
      );
      return;
    }
    if (req.url === "/api/bhyt/recompile") {
      res.end(
        JSON.stringify({
          ok: true,
          caseId: parsed.caseId,
          goi_xml_1_5: { chuan: "QD_130_4750_QD_BYT", XML1: "<TONG_HOP/>" },
          nhan_thong_tin_bn: parsed.thong_tin_benh_nhan ?? null,
        }),
      );
      return;
    }
    if (req.url === "/api/ocr/phieu-cu") {
      res.end(
        JSON.stringify({
          chi_so: { creatinine_umol_l: 120 },
          thuoc_nhan_dien: ["Metformin"],
          nhan_tuoi: parsed.tuoi,
        }),
      );
      return;
    }
    if (req.url === "/api/cam-doan-thu-thuat") {
      res.end(
        JSON.stringify({
          ten_thu_thuat: parsed.procedureName || "Nội soi dạ dày",
          du_6_muc_phap_ly: true,
          so_muc_dat: 6,
          tong_so_muc: 6,
        }),
      );
      return;
    }
    if (req.url === "/api/noi-tru/to-dieu-tri") {
      res.end(
        JSON.stringify({
          chuan_bieu_mau: "Mẫu BV-01/BV2 — Thông tư 32/2023/TT-BYT",
          ngay_dieu_tri_thu: parsed.dayNumber,
          y_lenh_thay_doi: [{ loai_thay_doi: "dieu_chinh_lieu", ten_thuoc: "Furosemid" }],
        }),
      );
      return;
    }
    if (req.url === "/api/duoc-thu/nap-csv") {
      res.end(
        JSON.stringify({
          ok: true,
          so_thuoc_nap: 2,
          bytes: Buffer.byteLength(String(parsed.csvContent || ""), "utf8"),
        }),
      );
      return;
    }
    res.statusCode = 404;
    res.end(JSON.stringify({ loi: "khong_co_duong", thong_diep: "not found" }));
  });
});

await new Promise<void>((resolve) => mockPyServer.listen(0, "127.0.0.1", resolve));
const mockPyPort = (mockPyServer.address() as { port: number }).port;

process.env.MEDITRACE_DB = mainDbPath;
process.env.MEDITRACE_KHONG_LISTEN = "1";
process.env.MEDITRACE_INTERNAL_TOKEN = "boost-test-internal-token";
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu-boost-lam-sang-0123456789abcdef";
process.env.MEDITRACE_API = `http://127.0.0.1:${mockPyPort}`;

const { db, damBaoKhoMoRong, khoWorm, TEN_KHO } = await import("../csdl");
const { taoUngDung } = await import("../../server");
const { caMauDuDieuKienKy, luuCaMau, taoCaDaKy } = await import("../ho-tro-kiem-thu-ky-duyet");

test.after(() => {
  mockPyServer.closeAllConnections?.();
  mockPyServer.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("Boost 11: damBaoKhoMoRong migrate an toan muc_kho cu, bao toan du lieu + PRAGMA foreign_keys + ON DELETE CASCADE", () => {
  assert.deepEqual(TEN_KHO, ["ca-kham", "tra-cuu", "mau-van-ban", "benh-nhan", "nhiem-vu"]);

  // 1. Kiểm tra CSDL chính (đã được seed ở dạng cũ trước khi import csdl.ts) nay đã tự nâng cấp
  const cuConNguyen = db
    .prepare("SELECT du_lieu FROM muc_kho WHERE nguoi_dung_id = 1 AND kho = 'tra-cuu'")
    .all() as Array<{ du_lieu: string }>;
  assert.equal(cuConNguyen.length, 1);
  assert.equal(JSON.parse(cuConNguyen[0].du_lieu).id, "tc_cu_1");

  // Lần gọi lặp lại phải lũy đẳng (idempotent -> trả false)
  assert.equal(damBaoKhoMoRong(db), false);

  // 2. Kiểm tra trực tiếp trên một DatabaseSync độc lập để xác minh PRAGMA foreign_keys & ON DELETE CASCADE
  const standalonePath = path.join(tmpDir, "standalone-legacy.db");
  const sdb = new DatabaseSync(standalonePath);
  try {
    sdb.exec(`
      PRAGMA foreign_keys = ON;
      CREATE TABLE nguoi_dung (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        ho_ten TEXT NOT NULL,
        mat_khau_bam TEXT NOT NULL,
        vai TEXT NOT NULL DEFAULT 'bac_si',
        tao_luc INTEGER NOT NULL
      );
      CREATE TABLE muc_kho (
        nguoi_dung_id  INTEGER NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
        kho            TEXT    NOT NULL CHECK (kho IN ('tra-cuu', 'mau-van-ban')),
        thu_tu         INTEGER NOT NULL,
        du_lieu        TEXT    NOT NULL CHECK (json_valid(du_lieu)),
        PRIMARY KEY (nguoi_dung_id, kho, thu_tu)
      );
      INSERT INTO nguoi_dung VALUES (10, 'u10@test.vn', 'BS 10', 'h', 'bac_si', 1);
      INSERT INTO muc_kho VALUES (10, 'mau-van-ban', 0, '{"title":"Mẫu cũ"}');
    `);

    const migratedFirst = damBaoKhoMoRong(sdb);
    assert.equal(migratedFirst, true);
    assert.equal(damBaoKhoMoRong(sdb), false, "chạy lần 2 phải là no-op");

    const fkAfter = sdb.prepare("PRAGMA foreign_keys").get() as { foreign_keys: number };
    assert.equal(fkAfter.foreign_keys, 1, "PRAGMA foreign_keys phải được giữ nguyên = ON sau migration");

    // Cho phép ghi kho mới 'benh-nhan' và 'nhiem-vu'
    sdb.prepare("INSERT INTO muc_kho VALUES (10, 'benh-nhan', 0, '{\"id\":\"bn_1\",\"ten\":\"Nguyễn Văn A\"}')").run();
    sdb.prepare("INSERT INTO muc_kho VALUES (10, 'nhiem-vu', 0, '{\"id\":\"nv_1\",\"title\":\"Gọi tái khám\"}')").run();

    // Vẫn chặn tên kho lạ & JSON hỏng
    assert.throws(() => {
      sdb.prepare("INSERT INTO muc_kho VALUES (10, 'kho-trai-phep', 0, '{}')").run();
    }, /CHECK constraint failed/);
    assert.throws(() => {
      sdb.prepare("INSERT INTO muc_kho VALUES (10, 'benh-nhan', 1, '{hong_json')").run();
    }, /CHECK constraint failed/);

    // Xóa người dùng phải tự động xóa dây chuyền (ON DELETE CASCADE) toàn bộ mục kho
    sdb.prepare("DELETE FROM nguoi_dung WHERE id = 10").run();
    const conSot = (sdb.prepare("SELECT COUNT(*) AS n FROM muc_kho WHERE nguoi_dung_id = 10").get() as { n: number }).n;
    assert.equal(conSot, 0, "ON DELETE CASCADE phải xóa sạch các mục kho của người dùng bị xóa");
  } finally {
    sdb.close();
  }
});

test("Boost 5, 8, 10, 11, 12 tren HTTP server.ts: Xac thuc 401, CRUD kho benh-nhan/nhiem-vu, BHYT/OCR, Informed Consent WORM, Ward-Round Diff & Formulary CSV", async (t) => {
  // Cấp mã mời để tạo 2 tài khoản bác sĩ thật qua taoUngDung()
  const taoMaMoi = (ma: string) => {
    const bam = crypto.createHash("sha256").update(ma).digest("hex");
    db.prepare("INSERT OR REPLACE INTO ma_moi (bam_ma, goi_y, tao_boi, tao_luc, het_han) VALUES (?, 'BM', 1, ?, ?)").run(
      bam,
      Date.now(),
      Date.now() + 3600_000,
    );
  };
  taoMaMoi("INVITEBSA1");
  taoMaMoi("INVITEBSB2");

  const { app } = taoUngDung();
  const server = http.createServer(app);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as { port: number }).port;
  const baseUrl = `http://127.0.0.1:${port}`;

  t.after(() => {
    server.closeAllConnections?.();
    server.close();
  });

  // 1. Bảo vệ xác thực 401 khi chưa có cookie phiên trên toàn bộ route mới
  for (const [method, url, body] of [
    ["GET", "/api/kho/benh-nhan", null],
    ["PUT", "/api/kho/nhiem-vu", { sessions: [] }],
    ["POST", "/api/clinical/informed-consent", { transcript: "BS: Nội soi" }],
    ["POST", "/api/inpatient/ward-round-diff", { todayPropositions: [] }],
    ["POST", "/api/formulary/upload-csv", { csvContent: "ten_thuoc,hoat_chat\nPanadol,Paracetamol" }],
  ] as const) {
    const unauthRes = await fetch(`${baseUrl}${url}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
    assert.equal(unauthRes.status, 401, `${method} ${url} khi chưa đăng nhập phải trả 401`);
  }

  // Đăng ký + đăng nhập 2 bác sĩ độc lập để kiểm thử cô lập dữ liệu & IDOR
  async function dangKyVaDangNhap(email: string, hoTen: string, maMoi: string): Promise<string> {
    const rReg = await fetch(`${baseUrl}/api/dang-ky`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: baseUrl },
      body: JSON.stringify({ hoTen, email, matKhau: "MatKhauAnToan123!", maMoi }),
    });
    assert.equal(rReg.status, 200);
    const rLog = await fetch(`${baseUrl}/api/dang-nhap`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: baseUrl },
      body: JSON.stringify({ email, matKhau: "MatKhauAnToan123!" }),
    });
    assert.equal(rLog.status, 200);
    const cookie = rLog.headers.get("set-cookie")?.split(";")[0] || "";
    assert.ok(cookie.startsWith("mt_phien="));
    return cookie;
  }

  const cookieBsA = await dangKyVaDangNhap("bsa@meditrace.vn", "BS Nguyễn A", "INVITEBSA1");
  const cookieBsB = await dangKyVaDangNhap("bsb@meditrace.vn", "BS Trần B", "INVITEBSB2");

  // 2. Boost 11 — CRUD `/api/kho/benh-nhan` và `/api/kho/nhiem-vu` có cô lập theo từng bác sĩ
  const dsBenhNhan = [
    { id: "bn_001", name: "Bé Lê Minh Khôi", age: 4, weightKg: 15, allergies: ["Penicillin"] },
    { id: "bn_002", name: "Bà Phạm Thị Hoa", age: 72, chronicConditions: ["Tăng huyết áp", "ĐTĐ típ 2"] },
  ];
  const putBnRes = await fetch(`${baseUrl}/api/kho/benh-nhan`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({ sessions: dsBenhNhan, savedAt: 1730000111000 }),
  });
  assert.equal(putBnRes.status, 200);
  assert.deepEqual(await putBnRes.json(), { ok: true, count: 2 });

  const getBnA = await (await fetch(`${baseUrl}/api/kho/benh-nhan`, { headers: { Cookie: cookieBsA } })).json();
  assert.equal(getBnA.savedAt, 1730000111000);
  assert.deepEqual(getBnA.sessions, dsBenhNhan);

  // Bác sĩ B đọc kho benh-nhan của mình phải rỗng (không lộ bệnh nhân của Bác sĩ A)
  const getBnB = await (await fetch(`${baseUrl}/api/kho/benh-nhan`, { headers: { Cookie: cookieBsB } })).json();
  assert.deepEqual(getBnB.sessions, []);

  const dsNhiemVu = [
    { id: "task_01", title: "Kiểm tra lại Kali máu sau 48h ngưng Spironolacton", status: "pending", caseId: "ca_bn_002" },
  ];
  const putNvRes = await fetch(`${baseUrl}/api/kho/nhiem-vu`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({ sessions: dsNhiemVu, savedAt: 1730000222000 }),
  });
  assert.equal(putNvRes.status, 200);
  const getNvA = await (await fetch(`${baseUrl}/api/kho/nhiem-vu`, { headers: { Cookie: cookieBsA } })).json();
  assert.deepEqual(getNvA.sessions, dsNhiemVu);
  assert.equal(getNvA.savedAt, 1730000222000);

  // 3. Boost 5 — `/api/bhyt/precheck` truyền `thong_tin_benh_nhan` (cân nặng & tuổi nhi khoa) + `/api/ocr/phieu-cu` không bịa tuổi 50
  // Xuất gói BHYT chỉ được khi ca đã ký duyệt: bác sĩ A lưu ca rồi ký qua đúng API thật.
  // Máy chủ dựng gói từ bản chụp lúc ký (mệnh đề hiệu lực, lời thoại, thông tin BN từ phụ đề/ngữ cảnh ca).
  const kyCaQuaApi = async (ca: { id: string }) => {
    const luu = await fetch(`${baseUrl}/api/ca-kham/${ca.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
      body: JSON.stringify({ session: ca }),
    });
    assert.equal(luu.status, 200);
    const ky = await fetch(`${baseUrl}/api/sessions/${ca.id}/sign-off`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
      body: JSON.stringify({}),
    });
    assert.equal(ky.status, 200);
  };
  await kyCaQuaApi(caMauDuDieuKienKy("ca_bhyt_a", { phuDe: "Nam, 4 tuổi, 15 kg" }));
  // Ca nhi dùng cho đường fallback Python thật (mục 7a): Paracetamol quá liều theo cân nặng.
  const caNhi: any = caMauDuDieuKienKy("ca_bhyt_nhi", {
    phuDe: "Nam, 3 tuổi, 12 kg",
    transcript: "BS: Cháu viêm họng cấp, uống Paracetamol 1000 mg 4 lần một ngày.",
  });
  caNhi.note.propositions = [
    { id: 1, text: "viêm họng cấp", status: "than", evidenceTurns: [1] },
    { id: 2, text: "Paracetamol 1000 mg uống 4 lần/ngày", status: "than", drug: "Paracetamol", evidenceTurns: [1] },
  ];
  caNhi.duyet.quyet = { 1: "giu", 2: "giu" };
  caNhi.duyet.banSua = {};
  await kyCaQuaApi(caNhi);

  const postBhyt = (duong: string, body: unknown) =>
    fetch(`${baseUrl}${duong}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
      body: JSON.stringify(body),
    });
  const bhytChuaKy = await postBhyt("/api/bhyt/precheck", { propositions: [], transcript: "BS: chưa ký." });
  assert.equal(bhytChuaKy.status, 409, "không gửi mã ca đã ký thì không được xuất gói BHYT");
  const bhytTronCa = await postBhyt("/api/bhyt/precheck", {
    sessionId: "ca_bhyt_a",
    thong_tin_benh_nhan: { tuoi: 70, can_nang_kg: 50 },
  });
  assert.equal(bhytTronCa.status, 422, "thông tin BN khác bản đã ký thì không xuất");

  capturedPyRequests.length = 0;
  const bhytRes = await postBhyt("/api/bhyt/precheck", { sessionId: "ca_bhyt_a" });
  assert.equal(bhytRes.status, 200);
  const bhytData: any = await bhytRes.json();
  assert.equal(capturedPyRequests[0].url, "/api/bhyt/precheck");
  for (const ttbn of [bhytData.nhan_thong_tin_bn, capturedPyRequests[0].body.thong_tin_benh_nhan]) {
    assert.equal(ttbn.tuoi, 4);
    assert.equal(ttbn.can_nang_kg, 15);
    assert.equal(ttbn.gioi_tinh, "nam");
  }
  assert.deepEqual(
    capturedPyRequests[0].body.propositions.map((p: any) => p.text),
    ["đau ngực", "không sốt"],
    "mệnh đề hiệu lực từ bản đã ký: bỏ mệnh đề bị bác, dùng bản sửa",
  );

  // `/api/bhyt/recompile` dựng gói từ bản đã ký; caseId là mã ca đã ký; caseId lệch sessionId -> 422
  const recompileLech = await postBhyt("/api/bhyt/recompile", { sessionId: "ca_bhyt_a", caseId: "ca_nhi_01" });
  assert.equal(recompileLech.status, 422);
  const recompileRes = await postBhyt("/api/bhyt/recompile", { sessionId: "ca_bhyt_a" });
  assert.equal(recompileRes.status, 200);
  const recompileBody: any = await recompileRes.json();
  assert.equal(recompileBody.caseId, "ca_bhyt_a");
  assert.equal(recompileBody.nhan_thong_tin_bn.can_nang_kg, 15);

  // `/api/ocr/phieu-cu` khi không gửi `tuoi` phải gửi `tuoi: null` (tuyệt đối không bịa 50)
  const ocrNoAgeRes = await fetch(`${baseUrl}/api/ocr/phieu-cu`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({ text: "Creatinine: 120 umol/L; Đơn cũ: Metformin 850mg" }),
  });
  assert.equal(ocrNoAgeRes.status, 200);
  const ocrNoAgeData: any = await ocrNoAgeRes.json();
  assert.equal(ocrNoAgeData.nhan_tuoi, null, "thiếu tuổi phải truyền null thay vì tự bịa tuổi 50");

  // 4. Boost 8 — `/api/clinical/informed-consent` + đóng dấu WORM `consentHash` + chặn IDOR + khóa ký duyệt 409 + che PII log
  const uidBsA = (db.prepare("SELECT id FROM nguoi_dung WHERE email = ?").get("bsa@meditrace.vn") as { id: number }).id;
  taoCaDaKy(uidBsA, "ca_thu_thuat_a");
  luuCaMau(uidBsA, caMauDuDieuKienKy("ca_thu_thuat_chua_ky"));
  taoCaDaKy(uidBsA, "ca_thu_thuat_sua_sau_ky", { suaSauKy: true });

  const consentTranscript = "BS: Bác cần nội soi dạ dày gây mê, nguy cơ sặc hoặc phản vệ hiếm gặp.\nBN: Tôi đã hiểu và đồng ý làm.";
  const consentProps = [{ id: 1, text: "chỉ định nội soi dạ dày gây mê", evidenceTurns: [1] }];

  // 4a. Thiếu mã ca / ca chưa ký / ca sửa sau ký -> 409 chua_ky_duyet, không gọi Python và không ghi WORM
  for (const [nhan, sid] of [
    ["thiếu mã ca", undefined],
    ["ca chưa ký", "ca_thu_thuat_chua_ky"],
    ["ca sửa sau ký", "ca_thu_thuat_sua_sau_ky"],
  ] as const) {
    capturedPyRequests.length = 0;
    const truocWorm = sid ? khoWorm.docLichSuSignOff(sid, { userId: uidBsA }).length : 0;
    const r409 = await fetch(`${baseUrl}/api/clinical/informed-consent`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
      body: JSON.stringify({
        transcript: consentTranscript,
        propositions: consentProps,
        stampWorm: true,
        ...(sid ? { sessionId: sid } : {}),
      }),
    });
    assert.equal(r409.status, 409, `informed-consent (${nhan}) phải trả 409`);
    assert.equal((await r409.json()).code, "chua_ky_duyet");
    assert.equal(capturedPyRequests.length, 0, `informed-consent (${nhan}) không được gọi Python`);
    if (sid) {
      assert.equal(
        khoWorm.docLichSuSignOff(sid, { userId: uidBsA }).length,
        truocWorm,
        `informed-consent (${nhan}) không được ghi thêm WORM`,
      );
    }
  }

  const consentRes = await fetch(`${baseUrl}/api/clinical/informed-consent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({
      transcript: consentTranscript,
      propositions: consentProps,
      audioMetadata: [{ luot: 2, start_ms: 4200, end_ms: 7100, speaker_id: "BN" }],
      procedureName: "Nội soi thực quản - dạ dày gây mê",
      stampWorm: true,
      sessionId: "ca_thu_thuat_a",
    }),
  });
  assert.equal(consentRes.status, 200);
  const consentData: any = await consentRes.json();
  assert.equal(consentData.du_6_muc_phap_ly, true);
  assert.equal(consentData.sessionId, "ca_thu_thuat_a");
  assert.equal(typeof consentData.checkedAt, "string");
  const expectedConsentHash = crypto
    .createHash("sha256")
    .update(
      JSON.stringify({
        sessionId: "ca_thu_thuat_a",
        transcript: consentTranscript,
        propositions: consentProps,
        checkedAt: consentData.checkedAt,
      }),
    )
    .digest("hex");
  assert.equal(consentData.consentHash, expectedConsentHash);

  // Nhật ký kiểm toán đã ghi `cam_doan_thu_thuat_worm`
  const logWorm = db
    .prepare("SELECT chi_tiet FROM nhat_ky WHERE hanh_dong = 'cam_doan_thu_thuat_worm' ORDER BY id DESC LIMIT 1")
    .get() as { chi_tiet: string } | undefined;
  assert.ok(logWorm?.chi_tiet.includes(expectedConsentHash));

  // Che PII trong procedureName khi ghi bảng nhat_ky
  const consentPiiRes = await fetch(`${baseUrl}/api/clinical/informed-consent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({
      transcript: consentTranscript,
      propositions: consentProps,
      procedureName: "Nội soi cho Nguyễn Văn Minh 0912345678",
      stampWorm: true,
      sessionId: "ca_thu_thuat_a",
    }),
  });
  assert.equal(consentPiiRes.status, 200);
  const logWormPii = db
    .prepare("SELECT chi_tiet FROM nhat_ky WHERE hanh_dong = 'cam_doan_thu_thuat_worm' ORDER BY id DESC LIMIT 1")
    .get() as { chi_tiet: string } | undefined;
  assert.ok(logWormPii?.chi_tiet, "phải ghi dòng nhật ký WORM");
  assert.equal(logWormPii.chi_tiet.includes("Nguyễn Văn Minh"), false, "nhat_ky không được chứa tên bệnh nhân thô");
  assert.equal(logWormPii.chi_tiet.includes("0912345678"), false, "nhat_ky không được chứa SĐT bệnh nhân thô");

  // Bác sĩ B cố đóng dấu cam đoan thủ thuật vào ca của Bác sĩ A -> 403 IDOR!
  const consentIdor = await fetch(`${baseUrl}/api/clinical/informed-consent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsB, Origin: baseUrl },
    body: JSON.stringify({
      transcript: consentTranscript,
      propositions: consentProps,
      stampWorm: true,
      sessionId: "ca_thu_thuat_a",
    }),
  });
  assert.equal(consentIdor.status, 403);
  assert.equal((await consentIdor.json()).code, "idor_forbidden");

  // 5. Boost 10 — `/api/inpatient/ward-round-diff` (khóa ký duyệt 409 + nhánh 200)
  taoCaDaKy(uidBsA, "ca_noi_tru_a");
  luuCaMau(uidBsA, caMauDuDieuKienKy("ca_noi_tru_chua_ky"));
  taoCaDaKy(uidBsA, "ca_noi_tru_sua_sau_ky", { suaSauKy: true });

  for (const [nhan, sid] of [
    ["thiếu mã ca", undefined],
    ["ca chưa ký", "ca_noi_tru_chua_ky"],
    ["ca sửa sau ký", "ca_noi_tru_sua_sau_ky"],
  ] as const) {
    capturedPyRequests.length = 0;
    const truocWorm = sid ? khoWorm.docLichSuSignOff(sid, { userId: uidBsA }).length : 0;
    const w409 = await fetch(`${baseUrl}/api/inpatient/ward-round-diff`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
      body: JSON.stringify({
        todayPropositions: [{ id: 2, text: "tăng liều Furosemid 40mg tiêm tĩnh mạch", evidenceTurns: [1] }],
        yesterdayPropositions: [{ id: 1, text: "Furosemid 20mg uống", evidenceTurns: [1] }],
        todayTranscript: "BS: Hôm nay ngày thứ 3, tăng liều Furosemid 40mg.",
        dayNumber: 3,
        ...(sid ? { currentSessionId: sid } : {}),
      }),
    });
    assert.equal(w409.status, 409, `ward-round-diff (${nhan}) phải trả 409`);
    assert.equal((await w409.json()).code, "chua_ky_duyet");
    assert.equal(capturedPyRequests.length, 0, `ward-round-diff (${nhan}) không được gọi Python`);
    if (sid) {
      assert.equal(
        khoWorm.docLichSuSignOff(sid, { userId: uidBsA }).length,
        truocWorm,
        `ward-round-diff (${nhan}) không được ghi thêm WORM`,
      );
    }
  }

  const wardRes = await fetch(`${baseUrl}/api/inpatient/ward-round-diff`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({
      todayPropositions: [{ id: 2, text: "tăng liều Furosemid 40mg tiêm tĩnh mạch", evidenceTurns: [1] }],
      yesterdayPropositions: [{ id: 1, text: "Furosemid 20mg uống", evidenceTurns: [1] }],
      todayTranscript: "BS: Hôm nay ngày thứ 3, còn phù nhẹ hai chân, tăng liều Furosemid 40mg tiêm tĩnh mạch.",
      dayNumber: 3,
      currentSessionId: "ca_noi_tru_a",
    }),
  });
  assert.equal(wardRes.status, 200);
  const wardData: any = await wardRes.json();
  assert.equal(wardData.ngay_dieu_tri_thu, 3);
  assert.equal(wardData.y_lenh_thay_doi.length, 1);

  // 6. Boost 12 — `/api/formulary/upload-csv`: chặn rỗng (400), chặn >500KB (413), nạp hợp lệ (200 + ghiNhatKy)
  const csvEmptyRes = await fetch(`${baseUrl}/api/formulary/upload-csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({ csvContent: "   " }),
  });
  assert.equal(csvEmptyRes.status, 400);

  const over500KbCsv = "ma_thuoc,ten_biet_duoc,hoat_chat\n" + "BV001,ThuocTest,Paracetamol\n".repeat(20_000);
  assert.ok(Buffer.byteLength(over500KbCsv, "utf8") > 500 * 1024);
  const csvTooBigRes = await fetch(`${baseUrl}/api/formulary/upload-csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({ csvContent: over500KbCsv }),
  });
  assert.equal(csvTooBigRes.status, 413);
  assert.equal((await csvTooBigRes.json()).code, "csv_too_large");

  const validCsv = "ma_thuoc,ten_biet_duoc,hoat_chat,ham_luong\nBV101,Klamentin,amoxicillin,875mg/125mg\nBV102,Nexium Mups,esomeprazole,40mg\n";
  const csvOkRes = await fetch(`${baseUrl}/api/formulary/upload-csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({ csvContent: validCsv }),
  });
  assert.equal(csvOkRes.status, 200);
  const csvOkBody: any = await csvOkRes.json();
  assert.equal(csvOkBody.ok, true);
  assert.equal(csvOkBody.so_thuoc_nap, 2);

  const logCsv = db
    .prepare("SELECT chi_tiet FROM nhat_ky WHERE hanh_dong = 'nap_duoc_thu_csv' ORDER BY id DESC LIMIT 1")
    .get() as { chi_tiet: string } | undefined;
  assert.ok(logCsv?.chi_tiet.includes("bytes="));

  // 7. Tắt mockPyServer để kiểm thử thật 100% đường fallback `dich_vu_tat` -> `chayPythonJson` cho cả 4 module Python!
  mockPyServer.closeAllConnections?.();
  await new Promise<void>((resolve) => mockPyServer.close(() => resolve()));

  // 7a. Fallback thực tế `src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot --precheck` phát hiện quá liều Nhi khoa nhờ `thong_tin_benh_nhan`
  const fbBhytRes = await fetch(`${baseUrl}/api/bhyt/precheck`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    // Máy chủ dựng gói từ bản đã ký của ca nhi (Paracetamol 1000 mg × 4, 3 tuổi, 12 kg).
    body: JSON.stringify({ sessionId: "ca_bhyt_nhi" }),
  });
  assert.equal(fbBhytRes.status, 200);
  const fbBhytBody: any = await fbBhytRes.json();
  assert.ok(Array.isArray(fbBhytBody.canh_bao_lieu_nhi_khoa) && fbBhytBody.canh_bao_lieu_nhi_khoa.length >= 1);

  // 7b. Fallback thực tế `src.cong_cu_lam_sang.doc_phieu_xet_nghiem --parse` khi thiếu `tuoi`: không bịa eGFR tuổi 50
  const fbOcrRes = await fetch(`${baseUrl}/api/ocr/phieu-cu`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({ text: "Creatinine: 150 umol/L; Metformin 850mg" }),
  });
  assert.equal(fbOcrRes.status, 200);
  const fbOcrBody: any = await fbOcrRes.json();
  assert.equal(fbOcrBody.chi_so?.egfr, undefined, "không có tuổi thật thì tuyệt đối không tự tính eGFR giả định tuổi 50");

  // 7c. Fallback thực tế `src.cong_cu_lam_sang.cam_doan_thu_thuat --check`
  const fbConsentRes = await fetch(`${baseUrl}/api/clinical/informed-consent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({
      transcript:
        "BS: Bác đang bị loét dạ dày chảy máu, chỉ định nội soi dạ dày cầm máu. Nguy cơ tai biến có thể chảy máu hoặc phản vệ. Phương án thay thế là điều trị nội khoa bảo tồn; nếu từ chối hoặc chậm trễ bệnh sẽ tiến triển nặng nguy hiểm tính mạng.\nBN: Tôi đã hiểu và đồng ý tiến hành nội soi.",
      propositions: [],
      audioMetadata: [{ luot: 2, start_ms: 8000, end_ms: 11500, speaker_id: "BN" }],
      procedureName: "Nội soi dạ dày cầm máu",
      sessionId: "ca_thu_thuat_a",
    }),
  });
  assert.equal(fbConsentRes.status, 200);
  const fbConsentBody: any = await fbConsentRes.json();
  assert.equal(fbConsentBody.du_6_muc_phap_ly, true);
  assert.equal(fbConsentBody.so_muc_dat, 6);

  // 7d. Fallback thực tế `src.cong_cu_lam_sang.di_buong_noi_tru --diff`
  const fbWardRes = await fetch(`${baseUrl}/api/inpatient/ward-round-diff`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookieBsA, Origin: baseUrl },
    body: JSON.stringify({
      yesterdayPropositions: [
        { id: 1, text: "sốt cao 39 độ C", evidenceTurns: [1] },
        { id: 2, text: "Ceftriaxon 2g tiêm tĩnh mạch 1 lần/ngày", drug: "Ceftriaxon", evidenceTurns: [2] },
      ],
      todayPropositions: [
        { id: 3, text: "hết sốt, nhiệt độ 36.8 độ C", evidenceTurns: [1] },
        { id: 4, text: "duy trì thuốc như ngày trước", evidenceTurns: [2] },
      ],
      todayTranscript: "BN: Hôm nay tôi hết sốt rồi bác sĩ ạ.\nBS: Nhiệt độ 36.8 độ C, duy trì thuốc như ngày trước.",
      dayNumber: 4,
      currentSessionId: "ca_noi_tru_a",
    }),
  });
  assert.equal(fbWardRes.status, 200);
  const fbWardBody: any = await fbWardRes.json();
  assert.equal(fbWardBody.ngay_dieu_tri_thu, 4);
  assert.match(fbWardBody.van_ban_to_dieu_tri_tt32 || "", /THÔNG TƯ 32\/2023\/TT-BYT/);
});
