import assert from "node:assert/strict";
import test from "node:test";
import { cheLog } from "./che-log";

test("che_ten_va_so_dien_thoai_giu_noi_dung_lam_sang", () => {
  const ra = cheLog("Bệnh nhân Nguyễn Văn An, sđt 0912345678, đau ngực");
  assert.ok(!ra.includes("Nguyễn Văn An"), ra);
  assert.ok(!ra.includes("0912345678"), ra);
  assert.ok(ra.includes("đau ngực") || ra.startsWith("[đã ẩn"), ra);
});

test("cat_ngan_toi_da_300_ky_tu", () => {
  assert.ok(cheLog("x".repeat(5000)).length <= 300);
});

test("doi_tuong_duoc_chuoi_hoa", () => {
  assert.ok(cheLog({ a: 1 }).includes("a"));
});

test("loi_co_stack_khong_lo_ten", () => {
  const e = new Error("hỏng khi xử lý: Bà Trần Thị Hoa 0987654321");
  const ra = cheLog(e.stack || e.message);
  assert.ok(!ra.includes("Trần Thị Hoa") && !ra.includes("0987654321"), ra);
});
