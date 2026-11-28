import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-ngoai-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "ngoai.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu";
process.env.MEDITRACE_TRO_LY_NGOAI = "bat";

// Cổng mô hình ngoài giả: ghi lại thân yêu cầu và trả lại đúng nội dung người dùng gửi.
const daNhan: Array<{ body: any; ua: string }> = [];
/** Khi đặt, cổng giả trả mã 400 với thông điệp lỗi này (mô phỏng cổng bên thứ ba dội lại nội dung). */
let loiCongGia: string | null = null;
const mockLlm = http.createServer((req, res) => {
  let raw = "";
  req.on("data", (c) => (raw += c));
  req.on("end", () => {
    const body = JSON.parse(raw || "{}");
    daNhan.push({ body, ua: String(req.headers["user-agent"] || "") });
    if (loiCongGia) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: { message: loiCongGia } }));
      return;
    }
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ model: "gia", choices: [{ message: { content: body.messages?.[1]?.content || "" } }] }));
  });
});
await new Promise<void>((r) => mockLlm.listen(0, "127.0.0.1", r));

const { db } = await import("../csdl");
const { dangKyLlmNgoaiRoutes, NGOAI, datLaiHanMucNgoai } = await import("./llm-ngoai");
const { ghiNgoaiBat } = await import("../tro-ly/cai-dat-tro-ly");
NGOAI.base = `http://127.0.0.1:${(mockLlm.address() as { port: number }).port}`;
NGOAI.key = "khoa-gia";

let base = "";
let server: http.Server;
test.before(async () => {
  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    const uid = Number(req.get("x-test-uid") || 1);
    req.nguoiDung = { id: uid, email: `${uid}@t.vn`, hoTen: "BS", vai: uid === 3 ? "quan_tri" : "bac_si" } as any;
    next();
  });
  dangKyLlmNgoaiRoutes(app);
  server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
});
test.after(() => {
  server?.close();
  mockLlm.closeAllConnections?.();
  mockLlm.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

const post = async (duong: string, body: unknown, uid = 1) => {
  const r = await fetch(`${base}${duong}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-test-uid": String(uid) },
    body: JSON.stringify(body),
  });
  return { status: r.status, body: (await r.json()) as any };
};

const LOI_THOAI =
  "BS: Bác tên gì?\nBN: Tôi là Bà Hoa, 67 tuổi, sinh ngày 12/03/1959, nhà số 12 ngõ 45 Láng Hạ, Đống Đa.\n" +
  "BN: Số con tôi 0912 345 678, mã bệnh nhân 20261125. Cháu tên là Minh học trường Kim Liên.";

test("công tắc quản trị tắt thì mọi route mô hình ngoài bị chặn, không gọi ra ngoài", async () => {
  ghiNgoaiBat(db, false);
  try {
    const n = daNhan.length;
    for (const [duong, than] of [
      ["/api/edit-note", { currentContent: "x", instruction: "y" }],
      ["/api/clinical-qa", { question: "q" }],
      ["/api/questions-external", { transcript: "t" }],
      ["/api/generate-document", { title: "t", transcript: "t" }],
      ["/api/generate-note-external", { transcript: "t" }],
    ] as const) {
      const r = await post(duong, { ...than, allowExternal: true });
      assert.equal(r.status, 403, duong);
      assert.equal(r.body.code, "ngoai_bi_tat", duong);
    }
    assert.equal(daNhan.length, n);
  } finally {
    ghiNgoaiBat(db, true);
  }
});

test("lời thoại được che định danh trước khi gửi, câu trả lời khôi phục lại; không giả User-Agent trình duyệt", async () => {
  datLaiHanMucNgoai();
  const r = await post("/api/generate-note-external", { transcript: LOI_THOAI, allowExternal: true });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  const guiDi = JSON.stringify(daNhan.at(-1)!.body);
  for (const lo of ["Hoa", "12/03/1959", "Láng Hạ", "Đống Đa", "0912", "345 678", "20261125", "Minh", "Kim Liên"]) {
    assert.ok(!guiDi.includes(lo), `lộ "${lo}" ra mô hình ngoài`);
  }
  assert.match(r.body.content, /Bà Hoa/, "câu trả lời được khôi phục định danh cho bác sĩ");
  assert.doesNotMatch(daNhan.at(-1)!.ua, /Mozilla|Chrome/);
});

test("giới hạn số lần gọi ngoài theo người dùng (429)", async () => {
  datLaiHanMucNgoai();
  process.env.MEDITRACE_NGOAI_TOI_DA_PHUT = "2";
  try {
    const goi = (uid: number) => post("/api/clinical-qa", { question: "đau ngực bao lâu?", transcript: "BN: đau 2 ngày", allowExternal: true }, uid);
    assert.equal((await goi(1)).status, 200);
    assert.equal((await goi(1)).status, 200);
    const qua = await goi(1);
    assert.equal(qua.status, 429);
    assert.equal(qua.body.code, "qua_gioi_han_ngoai");
    assert.equal((await goi(2)).status, 200, "người dùng khác không bị ảnh hưởng");
  } finally {
    delete process.env.MEDITRACE_NGOAI_TOI_DA_PHUT;
    datLaiHanMucNgoai();
  }
  process.env.MEDITRACE_NGOAI_TOI_DA_NGAY = "1";
  try {
    assert.equal((await post("/api/clinical-qa", { question: "q", allowExternal: true }, 4)).status, 200);
    assert.equal((await post("/api/clinical-qa", { question: "q", allowExternal: true }, 4)).status, 429);
  } finally {
    delete process.env.MEDITRACE_NGOAI_TOI_DA_NGAY;
    datLaiHanMucNgoai();
  }
});

test("thiếu allowExternal vẫn 403; /api/external/status không lộ địa chỉ cổng cho bác sĩ", async () => {
  const r = await post("/api/edit-note", { currentContent: "x", instruction: "y" });
  assert.equal(r.status, 403);
  assert.equal(r.body.code, "chua_cho_phep_ngoai");
  const st = (await (await fetch(`${base}/api/external/status`, { headers: { "x-test-uid": "1" } })).json()) as any;
  assert.equal(st.base, undefined);
  const qt = (await (await fetch(`${base}/api/external/status`, { headers: { "x-test-uid": "3" } })).json()) as any;
  assert.equal(typeof qt.base, "string");
});

test("log_loi_cong_ngoai_da_che", async (t) => {
  const daLog: string[] = [];
  t.mock.method(console, "error", (...a: unknown[]) => void daLog.push(a.map(String).join(" ")));
  loiCongGia = "bad input: Bệnh nhân Nguyễn Văn An 0912345678";
  try {
    const r = await post("/api/clinical-qa", { question: "đau ngực bao lâu?", transcript: "BN: đau 2 ngày", allowExternal: true }, 7);
    assert.equal(r.status, 502);
  } finally {
    loiCongGia = null;
    datLaiHanMucNgoai();
  }
  assert.ok(daLog.length > 0, "phải có dòng log lỗi");
  for (const dong of daLog) {
    assert.ok(!dong.includes("Nguyễn Văn An") && !dong.includes("0912345678"), dong);
  }
});
