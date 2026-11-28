import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { THONG_BAO_BAN_DEMO } from "./thongBaoBanDemo";

test("thong_bao_ban_demo_dung_nguyen_van", () => {
  assert.equal(
    THONG_BAO_BAN_DEMO,
    "Bản chạy thử công khai: chỉ nhập dữ liệu mô phỏng. Không nhập tên, mã hồ sơ hay thông tin của người bệnh thật.",
  );
});

test("thong_bao_ban_demo_co_tren_man_dang_nhap", () => {
  const tep = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../components/ManDangNhap.tsx");
  const ma = fs.readFileSync(tep, "utf-8");
  assert.ok(ma.includes("THONG_BAO_BAN_DEMO"), "ManDangNhap phải hiện thông báo bản demo");
});
