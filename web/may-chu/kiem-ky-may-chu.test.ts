import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-kiem-ky-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "kiem-ky.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu-kiem-ky-may-chu-0123456789";

const { db, khoWorm } = await import("./csdl");
const { kiemDaKyChoXuat } = await import("./kiem-ky-may-chu");
const { caMauDuDieuKienKy, luuCaMau, taoCaDaKy } = await import("./ho-tro-kiem-thu-ky-duyet");

test.before(() => {
  for (const id of [1, 2]) {
    db.prepare(
      "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (?, ?, 'BS', 'h', 'bac_si', ?)",
    ).run(id, `${id}@t.vn`, Date.now());
  }
});
test.after(() => {
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("thiếu mã ca hoặc ca không tồn tại: không được xuất", () => {
  assert.equal(kiemDaKyChoXuat(1, "").duoc, false);
  assert.equal(kiemDaKyChoXuat(1, "   ").duoc, false);
  const r = kiemDaKyChoXuat(1, "ca_khong_co");
  assert.equal(r.duoc, false);
  assert.ok(r.lyDo);
});

test("ca đã lưu nhưng chưa ký: không được xuất", () => {
  luuCaMau(1, caMauDuDieuKienKy("ca_chua_ky"));
  const r = kiemDaKyChoXuat(1, "ca_chua_ky");
  assert.equal(r.duoc, false);
  assert.match(r.lyDo || "", /chưa ký/i);
});

test("ca đã ký, chưa sửa: được xuất", () => {
  taoCaDaKy(1, "ca_da_ky");
  assert.deepEqual(kiemDaKyChoXuat(1, "ca_da_ky"), { duoc: true });
});

test("ca đã ký rồi sửa: không được xuất", () => {
  taoCaDaKy(1, "ca_sua_sau_ky", { suaSauKy: true });
  const r = kiemDaKyChoXuat(1, "ca_sua_sau_ky");
  assert.equal(r.duoc, false);
  assert.match(r.lyDo || "", /sửa sau/i);
});

test("ca đã ký, sửa rồi khôi phục đúng bản đã ký: được xuất lại", () => {
  taoCaDaKy(1, "ca_khoi_phuc", { suaSauKy: true });
  luuCaMau(1, caMauDuDieuKienKy("ca_khoi_phuc"));
  assert.equal(kiemDaKyChoXuat(1, "ca_khoi_phuc").duoc, true);
});

test("ca của bác sĩ khác (kể cả đã ký) không được xuất dưới tên mình", () => {
  taoCaDaKy(2, "ca_cua_bs2");
  assert.equal(kiemDaKyChoXuat(1, "ca_cua_bs2").duoc, false);
  assert.equal(kiemDaKyChoXuat(2, "ca_cua_bs2").duoc, true);
});

test("dòng WORM khác (dấu cam đoan thủ thuật, băm khác) không thay được chữ ký hồ sơ", () => {
  luuCaMau(1, caMauDuDieuKienKy("ca_chi_cam_doan"));
  khoWorm.ghiSignOff({
    sessionId: "ca_chi_cam_doan",
    userId: 1,
    tongMenhDe: 1,
    soGiu: 1,
    soSua: 0,
    soBo: 0,
    tyLeCoNguon: 100,
    contentHash: "a".repeat(64),
    soChuaXacNhan: 0,
  });
  assert.equal(kiemDaKyChoXuat(1, "ca_chi_cam_doan").duoc, false);
});
