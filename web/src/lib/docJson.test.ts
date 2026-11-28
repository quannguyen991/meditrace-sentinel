import assert from "node:assert/strict";
import test from "node:test";
import { docJsonHoacNull } from "./docJson";

test("json_hop_le_thi_tra_doi_tuong", async () => {
  assert.deepEqual(await docJsonHoacNull(new Response('{"jobId":"7"}', { status: 202 })), { jobId: "7" });
});

test("trang_loi_html_cua_cong_mang_thi_tra_null", async () => {
  assert.equal(await docJsonHoacNull(new Response("<!DOCTYPE html><html>502</html>", { status: 502 })), null);
});

test("than_rong_thi_tra_null", async () => {
  assert.equal(await docJsonHoacNull(new Response("", { status: 504 })), null);
});
