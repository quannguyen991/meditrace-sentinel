import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-routes-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "routes-test.db");
process.env.MEDITRACE_KHONG_LISTEN = "1";
process.env.MEDITRACE_CHO_NHAP_MS = "80";
process.env.MEDITRACE_TRO_LY_CHO_MS = "50";
process.env.MEDITRACE_TRO_LY_NGOAI = "tat";
process.env.MEDITRACE_INTERNAL_TOKEN = "test-token-noi-bo";

// Mock dịch vụ Python cục bộ để kiểm thử tích hợp thực tế cho /api/generate-note và /api/transcribe
let mockPyPort = 0;
let delayHoSoMs = 0;
const mockPyServer = http.createServer((req, res) => {
  let raw = "";
  req.on("data", (c) => (raw += c));
  req.on("end", () => {
    if (req.url === "/api/ho-so") {
      setTimeout(() => {
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(
          JSON.stringify({
            id: "ca_py_1",
            nhanh: "C_khoa_hoi",
            nguon: "tai_cho",
            du_doan: "BỆNH ÁN NHÁP",
            phat_bieu: [
              { id: 10, noi_dung: "đau ngực", chu_the_id: 0, ten_chu_the: "bệnh nhân", bang_chung: [1], trich_dan: ["đau ngực"] },
              { id: 11, noi_dung: "tiền sử tăng huyết áp", chu_the_id: 2, ten_chu_the: "bố", bang_chung: [2], trich_dan: ["bố bị THA"] },
            ],
            ghi_chu: [
              { id: 10, muc: "LÝ DO KHÁM BỆNH", van: "đau ngực" },
              { id: 11, muc: "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", van: "bố: tiền sử tăng huyết áp" },
            ],
            worm_seq: 77,
            worm_hash: "worm_sha256_py_77",
          }),
        );
      }, delayHoSoMs);
      return;
    }
    if (req.url === "/api/chep-am") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({
          phien: "phien_am_1",
          doan: [{ speaker_id: "BS", text_original: "Chào bác", start_s: 0, end_s: 1.2 }],
          nguon: "phowhisper",
        }),
      );
      return;
    }
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ thong_diep: "not found" }));
  });
});

await new Promise<void>((resolve) => mockPyServer.listen(0, "127.0.0.1", resolve));
mockPyPort = (mockPyServer.address() as { port: number }).port;
process.env.MEDITRACE_API = `http://127.0.0.1:${mockPyPort}`;

const { db } = await import("../csdl");
const { dangKyCaKhamRoutes } = await import("./ca-kham");
const { dangKyAsrRoutes, menhDeChoGiaoDien } = await import("./asr");
const { dangKyLlmNgoaiRoutes, NGOAI } = await import("./llm-ngoai");
const { dangKyBhytOcrRoutes } = await import("./bhyt-ocr");
const { dangKySignOffRoutes } = await import("./sign-off");
const { dangKyTraCuuRoutes } = await import("./tra-cuu");
const { dangKyTroLyRoutes } = await import("./tro-ly");
const { chayPythonJson, datLaiDinhPythonCon, thongKePythonCon } = await import("./dung-chung");
const { ghiLanThu, kichThuocLanThu, TOI_DA_MUC_LAN_THU } = await import("../tai-khoan");
const { taoUngDung } = await import("../../server");

function taoAppTest() {
  const app = express();
  app.use(express.json({ limit: "5mb" }));
  db.prepare(
    `INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc)
     VALUES (1, 'bs@test.local', 'BS Test', 'hash', 'bac_si', ?)`,
  ).run(Date.now());
  db.prepare(
    `INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc)
     VALUES (2, 'bs2@test.local', 'BS Hai', 'hash', 'bac_si', ?)`,
  ).run(Date.now());
  db.prepare(
    `INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc)
     VALUES (3, 'qt@test.local', 'Quan Tri', 'hash', 'quan_tri', ?)`,
  ).run(Date.now());

  // Cho phép chuyển vai linh hoạt qua header X-Test-Uid để kiểm thử IDOR đa bác sĩ / quản trị
  app.use((req, _res, next) => {
    const uid = Number(req.get("x-test-uid") || 1);
    if (uid === 2) req.nguoiDung = { id: 2, email: "bs2@test.local", hoTen: "BS Hai", vai: "bac_si" };
    else if (uid === 3) req.nguoiDung = { id: 3, email: "qt@test.local", hoTen: "Quan Tri", vai: "quan_tri" };
    else req.nguoiDung = { id: 1, email: "bs@test.local", hoTen: "BS Test", vai: "bac_si" };
    next();
  });

  dangKyCaKhamRoutes(app);
  dangKyAsrRoutes(app);
  dangKyLlmNgoaiRoutes(app);
  dangKyTraCuuRoutes(app);
  dangKyTroLyRoutes(app);
  dangKyBhytOcrRoutes(app);
  dangKySignOffRoutes(app);
  return app;
}

test.after(() => {
  mockPyServer.closeAllConnections?.();
  mockPyServer.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("Express HTTP routes: ca-kham (batch + granular + 409 lock), sign-off/WORM + IDOR, validation va error paths", async (t) => {
  const app = taoAppTest();
  const server = http.createServer(app);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const addr = server.address() as { port: number };
  const baseUrl = `http://127.0.0.1:${addr.port}`;

  t.after(() => {
    server.close();
  });

  // 1. /api/ca-kham PUT + GET tương thích ngược 100% + kiểm tra không spam ban_sao trong vòng 5 phút
  const putRes = await fetch(`${baseUrl}/api/ca-kham`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sessions: [{ id: "ca_http_1", patientIdentifier: "BN Test", date: "2026-11-25" }],
      savedAt: 1700000000000,
    }),
  });
  assert.equal(putRes.status, 200);
  const putData: any = await putRes.json();
  assert.equal(putData.ok, true);
  assert.equal(putData.count, 1);

  // Ghi lần 2 ngay lập tức -> đã tạo 1 bản sao cho dữ liệu cũ ở mốc >5p đầu tiên, lần 3 ngay sau đó không tạo thêm bản sao
  await fetch(`${baseUrl}/api/ca-kham`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessions: [{ id: "ca_http_1", patientIdentifier: "BN Test v2", date: "2026-11-25" }] }),
  });
  const soBanSao1 = (db.prepare("SELECT COUNT(*) AS n FROM ban_sao WHERE nguoi_dung_id = 1").get() as { n: number }).n;
  await fetch(`${baseUrl}/api/ca-kham`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessions: [{ id: "ca_http_1", patientIdentifier: "BN Test v3", date: "2026-11-25" }] }),
  });
  const soBanSao2 = (db.prepare("SELECT COUNT(*) AS n FROM ban_sao WHERE nguoi_dung_id = 1").get() as { n: number }).n;
  assert.equal(soBanSao2, soBanSao1, "chưa quá 5 phút không tạo thêm bản sao thừa");

  const getRes = await fetch(`${baseUrl}/api/ca-kham`);
  assert.equal(getRes.status, 200);
  const getData: any = await getRes.json();
  assert.equal(getData.sessions.length, 1);
  assert.equal(getData.sessions[0].id, "ca_http_1");

  // 1b. API hạt mịn PUT /api/ca-kham/:id + khóa lạc quan expectedUpdatedAt (409) + DELETE /api/ca-kham/:id
  const granCreate = await fetch(`${baseUrl}/api/ca-kham/ca_hat_min_1`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session: { id: "ca_hat_min_1", patientIdentifier: "BN Hạt Mịn", date: "2026-11-26" } }),
  });
  assert.equal(granCreate.status, 200);
  const granData1: any = await granCreate.json();
  assert.equal(granData1.ok, true);
  assert.equal(granData1.created, true);
  assert.equal(typeof granData1.updatedAt, "number");

  // Cập nhật hợp lệ với expectedUpdatedAt khớp
  const granUpdateOk = await fetch(`${baseUrl}/api/ca-kham/ca_hat_min_1`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session: { id: "ca_hat_min_1", patientIdentifier: "BN Hạt Mịn Mới", date: "2026-11-26" },
      expectedUpdatedAt: granData1.updatedAt,
    }),
  });
  assert.equal(granUpdateOk.status, 200);
  const granData2: any = await granUpdateOk.json();
  assert.ok(granData2.updatedAt > granData1.updatedAt);

  // Tab cũ gửi expectedUpdatedAt cũ hơn -> 409 Conflict!
  const granConflict = await fetch(`${baseUrl}/api/ca-kham/ca_hat_min_1`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session: { id: "ca_hat_min_1", patientIdentifier: "Tab Cũ Ghi Đè", date: "2026-11-26" },
      expectedUpdatedAt: granData1.updatedAt,
    }),
  });
  assert.equal(granConflict.status, 409);
  const conflictBody: any = await granConflict.json();
  assert.equal(conflictBody.currentUpdatedAt, granData2.updatedAt);

  // Cạnh tranh đồng thời (Promise.all hai request PUT cùng expectedUpdatedAt): BEGIN IMMEDIATE đảm bảo đúng 1 thắng (200) và 1 thua (409)
  const [raceA, raceB] = await Promise.all([
    fetch(`${baseUrl}/api/ca-kham/ca_hat_min_1`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session: { id: "ca_hat_min_1", patientIdentifier: "Nhánh Đua A", date: "2026-11-26" },
        expectedUpdatedAt: granData2.updatedAt,
      }),
    }),
    fetch(`${baseUrl}/api/ca-kham/ca_hat_min_1`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session: { id: "ca_hat_min_1", patientIdentifier: "Nhánh Đua B", date: "2026-11-26" },
        expectedUpdatedAt: granData2.updatedAt,
      }),
    }),
  ]);
  assert.deepEqual([raceA.status, raceB.status].sort((x, y) => x - y), [200, 409]);

  // DELETE /api/ca-kham/:id chỉ xóa đúng 1 ca, giữ nguyên ca_http_1
  const granDel = await fetch(`${baseUrl}/api/ca-kham/ca_hat_min_1`, { method: "DELETE" });
  assert.equal(granDel.status, 200);
  const granDelBody: any = await granDel.json();
  assert.equal(granDelBody.deleted, true);

  const afterDelRes = await fetch(`${baseUrl}/api/ca-kham`);
  const afterDelData: any = await afterDelRes.json();
  assert.deepEqual(
    afterDelData.sessions.map((s: any) => s.id),
    ["ca_http_1"],
  );

  const badKhoRes = await fetch(`${baseUrl}/api/kho/khong-ton-tai`);
  assert.equal(badKhoRes.status, 404);

  // 2. /api/sessions/:id/sign-off + IDOR + kiểm định chặt + /api/worm/verify
  const signRes = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tongMenhDe: 5,
      soGiu: 4,
      soSua: 1,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "sha_demo",
    }),
  });
  assert.equal(signRes.status, 200);
  const signData: any = await signRes.json();
  assert.equal(signData.ok, true);
  assert.equal(typeof signData.wormSeq, "number");
  assert.equal(typeof signData.hash, "string");

  // Bác sĩ 2 (IDOR) cố ký duyệt ca_http_1 của Bác sĩ 1 -> 403!
  const idorPost = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-test-uid": "2" },
    body: JSON.stringify({
      tongMenhDe: 5,
      soGiu: 5,
      soSua: 0,
      soBo: 0,
      tyLeCoNguon: 100,
      contentHash: "sha_hack",
    }),
  });
  assert.equal(idorPost.status, 403);

  // Bác sĩ 2 cố đọc lịch sử ký duyệt ca_http_1 của Bác sĩ 1 -> 403!
  const idorGet = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`, {
    headers: { "x-test-uid": "2" },
  });
  assert.equal(idorGet.status, 403);

  // Quản trị (uid=3) được phép đọc kiểm toán
  const adminGet = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`, {
    headers: { "x-test-uid": "3" },
  });
  assert.equal(adminGet.status, 200);
  const adminHist: any = await adminGet.json();
  assert.equal(adminHist.entries.length, 1);

  // Các dữ liệu sai ràng buộc số nguyên, tổng mệnh đề, tỷ lệ nguồn, contentHash rỗng -> đều bị chặn 400
  const invalidPayloads = [
    { tongMenhDe: "khong-phai-so", contentHash: "h" },
    { tongMenhDe: 0, soGiu: 0, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "h" },
    { tongMenhDe: 2.5, soGiu: 2, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "h" },
    { tongMenhDe: 3, soGiu: 0, soSua: 0, soBo: 3, tyLeCoNguon: 100, contentHash: "h" },
    { tongMenhDe: 3, soGiu: 2, soSua: 1, soBo: 1, tyLeCoNguon: 100, contentHash: "h" },
    { tongMenhDe: 3, soGiu: 3, soSua: 0, soBo: 0, tyLeCoNguon: 0, contentHash: "h" },
    { tongMenhDe: 3, soGiu: 3, soSua: 0, soBo: 0, tyLeCoNguon: 150, contentHash: "h" },
    { tongMenhDe: 3, soGiu: 2, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "h", soChuaXacNhan: 1 },
    { tongMenhDe: 3, soGiu: 3, soSua: 0, soBo: 0, tyLeCoNguon: 100, contentHash: "   " },
  ];
  for (const p of invalidPayloads) {
    const badRes = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    });
    assert.equal(badRes.status, 400, `phải trả 400 cho payload: ${JSON.stringify(p)}`);
  }

  const histRes = await fetch(`${baseUrl}/api/sessions/ca_http_1/sign-off`);
  assert.equal(histRes.status, 200);
  const histData: any = await histRes.json();
  assert.equal(histData.entries.length, 1);
  assert.equal(histData.entries[0].curr_hash, signData.hash);

  const verifyRes = await fetch(`${baseUrl}/api/worm/verify`);
  assert.equal(verifyRes.status, 200);
  const verifyData: any = await verifyRes.json();
  assert.equal(verifyData.hopLe, true);
  assert.ok(verifyData.soBanGhi >= 1);

  // 3. Input validation guards
  const asrBad = await fetch(`${baseUrl}/api/transcribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  assert.equal(asrBad.status, 400);

  const noteBad = await fetch(`${baseUrl}/api/generate-note`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  assert.equal(noteBad.status, 400);

  const ocrBad = await fetch(`${baseUrl}/api/ocr/phieu-cu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "   " }),
  });
  assert.equal(ocrBad.status, 400);

  const extBlocked = await fetch(`${baseUrl}/api/edit-note`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ currentNote: "abc", instruction: "sua", allowExternal: false }),
  });
  assert.equal(extBlocked.status, 403);
});

test("Hàng đợi ASR & Trợ lý: sửa Read-Once Delete Race, truyền chu_the_id + wormSeq/wormHash, SSE stream & DELETE hủy việc", async (t) => {
  const app = taoAppTest();
  const server = http.createServer(app);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const baseUrl = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
  t.after(() => server.close());

  // 1. Unit check menhDeChoGiaoDien truyền chu_the_id và wormSeq/wormHash
  const props = menhDeChoGiaoDien({
    phat_bieu: [{ id: 1, chu_the_id: 2, ten_chu_the: "mẹ", bang_chung: [1], trich_dan: ["mẹ bị ĐTĐ"] }],
    ghi_chu: [{ id: 1, muc: "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", van: "mẹ: đái tháo đường" }],
    worm_seq: 9,
    worm_hash: "abc_worm_9",
  });
  assert.equal(props[0].chu_the_id, 2);
  assert.equal(props[0].wormSeq, 9);
  assert.equal(props[0].wormHash, "abc_worm_9");

  // 2. /api/generate-note chuyển sang 202 jobId rồi đọc lặp lại 3 lần không bao giờ bị 404 (Read-Once Delete Race đã vá)
  delayHoSoMs = 160;
  const startNote = await fetch(`${baseUrl}/api/generate-note`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript: "BS: Đau ngực mấy ngày?\nBN: Đau ngực 2 ngày." }),
  });
  assert.equal(startNote.status, 202);
  const { jobId: noteJobId }: any = await startNote.json();
  assert.ok(noteJobId);

  await new Promise((r) => setTimeout(r, 220));
  delayHoSoMs = 0;

  for (let lan = 1; lan <= 3; lan++) {
    const pollRes = await fetch(`${baseUrl}/api/generate-note/${noteJobId}`);
    assert.equal(pollRes.status, 200, `lần đọc thứ ${lan} phải trả 200 thay vì 404`);
    const noteBody: any = await pollRes.json();
    assert.equal(noteBody.wormSeq, 77);
    assert.equal(noteBody.wormHash, "worm_sha256_py_77");
    assert.equal(noteBody.propositions[0].chu_the_id, 0);
    assert.equal(noteBody.propositions[1].chu_the_id, 2);
  }

  // 3. /api/tro-ly: đọc nhiều lần + SSE stream GET /api/tro-ly/:id/stream + DELETE /api/tro-ly/:id
  const askRes = await fetch(`${baseUrl}/api/tro-ly`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cauHoi: "bệnh nhân Kawasaki sốt 5 ngày cần lưu ý gì",
      menhDe: [{ text: "sốc phản vệ penicillin", section: "DỊ ỨNG", drug: "penicillin" }],
      nguCanh: { tuoi: 4, gioi: "nam" },
    }),
  });
  assert.equal(askRes.status, 200);
  // Lấy id việc vừa tạo trong viec_tro_ly để kiểm chứng đọc lại nhiều lần + SSE stream không bị xoá
  const rowTroLy = db.prepare("SELECT id FROM viec_tro_ly ORDER BY id DESC LIMIT 1").get() as { id: number };
  assert.ok(rowTroLy?.id);

  const readAgain1 = await fetch(`${baseUrl}/api/tro-ly/${rowTroLy.id}`);
  assert.equal(readAgain1.status, 200);
  const readAgain2 = await fetch(`${baseUrl}/api/tro-ly/${rowTroLy.id}`);
  assert.equal(readAgain2.status, 200);

  // Kiểm thử SSE stream trả về event: done kèm kết quả
  const sseRes = await fetch(`${baseUrl}/api/tro-ly/${rowTroLy.id}/stream`);
  assert.equal(sseRes.status, 200);
  assert.match(sseRes.headers.get("content-type") || "", /text\/event-stream/);
  const sseText = await sseRes.text();
  assert.match(sseText, /event: done/);
  assert.match(sseText, /"trangThai":"xong"/);

  // Bác sĩ khác (uid=2) không hủy được việc của uid=1 (404), chính chủ hủy được (200 -> 410 da_huy)
  const delWrongUser = await fetch(`${baseUrl}/api/tro-ly/${rowTroLy.id}`, {
    method: "DELETE",
    headers: { "x-test-uid": "2" },
  });
  assert.equal(delWrongUser.status, 404);

  const delOk = await fetch(`${baseUrl}/api/tro-ly/${rowTroLy.id}`, { method: "DELETE" });
  assert.equal(delOk.status, 200);
  const delBody: any = await delOk.json();
  assert.equal(delBody.cancelled, true);

  const afterCancel = await fetch(`${baseUrl}/api/tro-ly/${rowTroLy.id}`);
  assert.equal(afterCancel.status, 410);
  const afterCancelBody: any = await afterCancel.json();
  assert.equal(afterCancelBody.code, "da_huy");

  // 4. Hủy việc giữa chừng khi đang gọi cổng mô hình ngoài treo chậm + SSE đang mở:
  // xác nhận SSE nhận ngay event: error (code: "da_huy") VÀ AbortSignal ngắt ngay kết nối HTTP ra cổng ngoài!
  let llmDaNhanKetNoi: (() => void) | null = null;
  const choLlmNhan = new Promise<void>((r) => (llmDaNhanKetNoi = r));
  let llmBiNgat = false;
  let choLlmBiNgat: (() => void) | null = null;
  const huaLlmBiNgat = new Promise<void>((r) => (choLlmBiNgat = r));

  const mockSlowLlm = http.createServer((req, res) => {
    req.on("data", () => {});
    req.on("end", () => {
      llmDaNhanKetNoi?.();
      res.on("close", () => {
        if (!res.writableEnded) {
          llmBiNgat = true;
          choLlmBiNgat?.();
        }
      });
    });
  });
  await new Promise<void>((r) => mockSlowLlm.listen(0, "127.0.0.1", r));
  const slowLlmPort = (mockSlowLlm.address() as { port: number }).port;
  const oldBase = NGOAI.base;
  const oldKey = NGOAI.key;
  const oldTroLyNgoai = process.env.MEDITRACE_TRO_LY_NGOAI;
  NGOAI.base = `http://127.0.0.1:${slowLlmPort}`;
  NGOAI.key = "test-key";
  process.env.MEDITRACE_TRO_LY_NGOAI = "bat";

  try {
    const slowAsk = await fetch(`${baseUrl}/api/tro-ly`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cauHoi: "bệnh nhân COPD đợt cấp nên chọn kháng sinh kinh nghiệm nào",
        menhDe: [{ text: "khó thở tăng, đờm mủ", section: "BỆNH SỬ HIỆN TẠI" }],
        nguCanh: { tuoi: 68, gioi: "nam" },
      }),
    });
    assert.equal(slowAsk.status, 202);
    const { jobId: liveJobId }: any = await slowAsk.json();
    await choLlmNhan;

    // Mở luồng SSE trong khi việc đang treo ở bước gọi mô hình ngoài, sau đó bắn DELETE hủy việc
    const sseLivePromise = fetch(`${baseUrl}/api/tro-ly/${liveJobId}/stream`).then((r) => r.text());
    await new Promise((r) => setTimeout(r, 40));
    const cancelLive = await fetch(`${baseUrl}/api/tro-ly/${liveJobId}`, { method: "DELETE" });
    assert.equal(cancelLive.status, 200);

    const sseLiveOut = await sseLivePromise;
    assert.match(sseLiveOut, /event: error/);
    assert.match(sseLiveOut, /"code":"da_huy"/);

    await Promise.race([huaLlmBiNgat, new Promise((_, rej) => setTimeout(() => rej(new Error("timeout chờ abort LLM")), 1500))]);
    assert.equal(llmBiNgat, true, "AbortSignal phải ngắt ngay kết nối HTTP tới cổng mô hình ngoài khi hủy việc");
  } finally {
    NGOAI.base = oldBase;
    NGOAI.key = oldKey;
    process.env.MEDITRACE_TRO_LY_NGOAI = oldTroLyNgoai;
    mockSlowLlm.closeAllConnections?.();
    mockSlowLlm.close();
  }
});

test("Biên HTTP server.ts + tai-khoan.ts + dung-chung.ts: CSRF Origin, giới hạn 2MB/60MB, JSON 413/404, LAN_THU <= 5000 & Python semaphore <= 2", async (t) => {
  // Tạo sẵn một mã mời hợp lệ để kiểm thử luồng đăng ký + đăng nhập thật trên taoUngDung() mà không đụng bảng bất biến worm_signoff
  const maMoiTho = "MAMOITST";
  const bamMaMoi = crypto.createHash("sha256").update(maMoiTho).digest("hex");
  db.prepare(
    "INSERT OR REPLACE INTO ma_moi (bam_ma, goi_y, tao_boi, tao_luc, het_han) VALUES (?, 'ST', 3, ?, ?)",
  ).run(bamMaMoi, Date.now(), Date.now() + 3600_000);
  process.env.MEDITRACE_NGUON_DUOC_PHEP = "https://portal.meditrace.vn";

  const { app } = taoUngDung();
  const server = http.createServer(app);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as { port: number }).port;
  const baseUrl = `http://127.0.0.1:${port}`;
  t.after(() => {
    delete process.env.MEDITRACE_NGUON_DUOC_PHEP;
    server.closeAllConnections?.();
    server.close();
  });

  // 1. Chặn ngay wildcard nguy hiểm .vercel.app, .trycloudflare.com và tấn công hạ cấp giao thức http:// (khi cấu hình https://)
  for (const evilOrigin of [
    "https://attacker-preview.vercel.app",
    "https://random-tunnel.trycloudflare.com",
    "https://evil.example.com",
    "http://portal.meditrace.vn",
  ]) {
    const csrfRes = await fetch(`${baseUrl}/api/dang-nhap`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: evilOrigin },
      body: JSON.stringify({ email: "a@b.vn", matKhau: "12345678" }),
    });
    assert.equal(csrfRes.status, 403, `phải chặn Origin lạ hoặc hạ cấp giao thức: ${evilOrigin}`);
  }

  // Nguồn khớp chính xác trong MEDITRACE_NGUON_DUOC_PHEP được phép đi qua lớp CSRF (trả 401 sai mật khẩu thay vì 403 CSRF)
  const allowedOriginRes = await fetch(`${baseUrl}/api/dang-nhap`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: "https://portal.meditrace.vn" },
    body: JSON.stringify({ email: "khong-ton-tai@meditrace.vn", matKhau: "sai-mat-khau" }),
  });
  assert.equal(allowedOriginRes.status, 401);

  // 2. Đăng ký tài khoản bác sĩ bằng mã mời + kiểm thử đăng nhập lấy cookie phiên
  const regRes = await fetch(`${baseUrl}/api/dang-ky`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: baseUrl },
    body: JSON.stringify({ hoTen: "BS Thực Tế", email: "bsthucte@meditrace.vn", matKhau: "MatKhauManh123!", maMoi: maMoiTho }),
  });
  assert.equal(regRes.status, 200);

  const loginRes = await fetch(`${baseUrl}/api/dang-nhap`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: baseUrl },
    body: JSON.stringify({ email: "bsthucte@meditrace.vn", matKhau: "MatKhauManh123!" }),
  });
  assert.equal(loginRes.status, 200);
  const cookie = loginRes.headers.get("set-cookie")?.split(";")[0] || "";
  assert.ok(cookie.startsWith("mt_phien="));

  // 3. Payload > 2MB trên route thường trả 413 JSON chuẩn (KHÔNG trả HTML!)
  const big25Mb = "x".repeat(2.4 * 1024 * 1024);
  const tooLargeNormal = await fetch(`${baseUrl}/api/ca-kham/ca_qua_lon`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Cookie: cookie },
    body: JSON.stringify({ session: { id: "ca_qua_lon", transcript: big25Mb } }),
  });
  assert.equal(tooLargeNormal.status, 413);
  assert.match(tooLargeNormal.headers.get("content-type") || "", /application\/json/);
  const err413: any = await tooLargeNormal.json();
  assert.equal(err413.code, "payload_too_large");

  // 4. /api/transcribe khi CHƯA đăng nhập bị chặn 401 TRƯỚC KHI đọc 60MB; khi ĐÃ đăng nhập gửi 2.4MB đi qua ngọt (200)!
  const unauthTranscribe = await fetch(`${baseUrl}/api/transcribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ audioBase64: big25Mb }),
  });
  assert.equal(unauthTranscribe.status, 401);

  const authTranscribe = await fetch(`${baseUrl}/api/transcribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookie },
    body: JSON.stringify({ audioBase64: big25Mb, fileName: "test.webm" }),
  });
  assert.equal(authTranscribe.status, 200);
  const trData: any = await authTranscribe.json();
  assert.equal(trData.sessionId, "phien_am_1");

  // Kể cả có dấu gạch chéo cuối /api/transcribe/ cũng không bị lọt nhầm vào bộ đọc 2MB trước xác thực
  const unauthTranscribeSlash = await fetch(`${baseUrl}/api/transcribe/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ audioBase64: big25Mb }),
  });
  assert.equal(unauthTranscribeSlash.status, 401);

  const authTranscribeSlash = await fetch(`${baseUrl}/api/transcribe/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: cookie },
    body: JSON.stringify({ audioBase64: big25Mb, fileName: "test-slash.webm" }),
  });
  assert.equal(authTranscribeSlash.status, 200);

  // 5. JSON hỏng trả 400 JSON + đường dẫn /api lạ trả 404 JSON
  const badJson = await fetch(`${baseUrl}/api/ca-kham`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Cookie: cookie },
    body: "{khong-phai-json",
  });
  assert.equal(badJson.status, 400);
  const badJsonBody: any = await badJson.json();
  assert.equal(badJsonBody.code, "invalid_json");

  const notFoundApi = await fetch(`${baseUrl}/api/duong-dan-khong-ton-tai`, {
    headers: { Cookie: cookie },
  });
  assert.equal(notFoundApi.status, 404);
  assert.deepEqual(await notFoundApi.json(), { error: "Không tìm thấy API" });

  // 6. Giới hạn kích thước LAN_THU <= 5.000 mục chống tràn RAM
  for (let i = 0; i < TOI_DA_MUC_LAN_THU + 350; i++) {
    ghiLanThu(`flood|10.0.0.${i % 255}|u${i}`);
  }
  assert.ok(kichThuocLanThu() <= TOI_DA_MUC_LAN_THU, `LAN_THU vượt ngưỡng: ${kichThuocLanThu()}`);

  // 7. Semaphore chayPythonJson: chạy 5 tác vụ đồng thời, tối đa chỉ 2 tiến trình con chạy song song
  const oldPyBin = process.env.PYTHON_BIN;
  // Dùng chính node.exe giả lập tiến trình con đọc stdin, ngủ 80ms rồi in JSON (tương đương "-m" bị bỏ bằng eval script nếu dùng python thật)
  // Kiểm tra python thật có sẵn trong máy
  process.env.PYTHON_BIN = "python";
  datLaiDinhPythonCon();
  try {
    const jobs = Array.from({ length: 5 }, (_, idx) =>
      chayPythonJson("json.tool", [], { stt: idx, ok: true }),
    );
    const results = await Promise.all(jobs);
    assert.equal(results.length, 5);
    assert.ok(thongKePythonCon().dinhDongThoi <= 2, `vượt quá 2 tiến trình Python song song: ${thongKePythonCon().dinhDongThoi}`);
    assert.equal(thongKePythonCon().dangChay, 0);
  } finally {
    if (oldPyBin === undefined) delete process.env.PYTHON_BIN;
    else process.env.PYTHON_BIN = oldPyBin;
  }
});
