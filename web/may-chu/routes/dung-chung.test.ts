import assert from "node:assert/strict";
import http from "node:http";
import test from "node:test";

let headerNhan: string | undefined;
const mock = http.createServer((req, res) => {
  headerNhan = req.headers["x-meditrace-internal-token"] as string | undefined;
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ ok: true }));
});
await new Promise<void>((r) => mock.listen(0, "127.0.0.1", r));
process.env.MEDITRACE_API = `http://127.0.0.1:${(mock.address() as { port: number }).port}`;
const { goiDichVu, traLoi } = await import("./dung-chung");

test.after(() => {
  mock.closeAllConnections?.();
  mock.close();
});

test("goiDichVu: luôn gửi X-MediTrace-Internal-Token, thiếu token thì báo lỗi rõ và không gọi dịch vụ", async () => {
  const cu = process.env.MEDITRACE_INTERNAL_TOKEN;
  try {
    delete process.env.MEDITRACE_INTERNAL_TOKEN;
    headerNhan = "chua-goi";
    await assert.rejects(goiDichVu("/api/suc-khoe"), (e: any) => {
      assert.equal(e.status, 503);
      assert.equal(e.code, "thieu_token_noi_bo");
      assert.match(e.message, /MEDITRACE_INTERNAL_TOKEN/);
      return true;
    });
    assert.equal(headerNhan, "chua-goi", "không được gọi dịch vụ khi thiếu token");

    process.env.MEDITRACE_INTERNAL_TOKEN = "  bi-mat-123  ";
    const d = await goiDichVu("/api/suc-khoe", { headers: { "X-MediTrace-Internal-Token": "gia-mao" } });
    assert.equal(d.ok, true);
    assert.equal(headerNhan, "bi-mat-123", "token từ env thắng header do nơi gọi truyền vào");
  } finally {
    if (cu === undefined) delete process.env.MEDITRACE_INTERNAL_TOKEN;
    else process.env.MEDITRACE_INTERNAL_TOKEN = cu;
  }
});

test("traLoi: lỗi 5xx không lộ chi tiết nội bộ, lỗi 4xx giữ thông điệp", () => {
  const ghi: any = {};
  const res: any = {
    headersSent: false,
    status(s: number) {
      ghi.status = s;
      return this;
    },
    json(b: unknown) {
      ghi.body = b;
      return this;
    },
  };
  traLoi(res, Object.assign(new Error("Traceback ... D:\\khkt-venv-lap\\Scripts\\python.exe lỗi"), { status: 500 }));
  assert.equal(ghi.status, 500);
  assert.doesNotMatch(JSON.stringify(ghi.body), /khkt-venv|Traceback/);
  traLoi(res, Object.assign(new Error("Thiếu câu hỏi"), { status: 400, code: "thieu" }));
  assert.equal(ghi.status, 400);
  assert.deepEqual(ghi.body, { error: "Thiếu câu hỏi", code: "thieu" });
});
