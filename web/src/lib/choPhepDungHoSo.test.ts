import assert from "node:assert/strict";
import test from "node:test";
import { choPhepDungHoSo, nhanInHoSo, LY_DO_CHUA_KY, LY_DO_SUA_SAU_KY, NHAN_BAN_NHAP } from "./choPhepDungHoSo";

test("chua_ky_thi_khoa", () => {
  assert.deepEqual(choPhepDungHoSo({ daKy: false, daSuaSauKy: false }), { duoc: false, lyDo: LY_DO_CHUA_KY });
});

test("da_ky_thi_mo", () => {
  assert.deepEqual(choPhepDungHoSo({ daKy: true, daSuaSauKy: false }), { duoc: true, lyDo: null });
});

test("sua_sau_ky_thi_khoa_lai", () => {
  assert.deepEqual(choPhepDungHoSo({ daKy: true, daSuaSauKy: true }), { duoc: false, lyDo: LY_DO_SUA_SAU_KY });
});

test("nhan_in_khi_chua_ky", () => {
  assert.equal(nhanInHoSo(false), NHAN_BAN_NHAP);
  assert.equal(nhanInHoSo(true), null);
});

test("chuoi_hien_thi_dung_nguyen_van", () => {
  assert.equal(LY_DO_CHUA_KY, "Bác sĩ chưa ký duyệt — hồ sơ chỉ được xem, chưa được chép, in hay xuất.");
  assert.equal(LY_DO_SUA_SAU_KY, "Hồ sơ đã sửa sau lần ký — cần ký lại trước khi chép, in hay xuất.");
  assert.equal(NHAN_BAN_NHAP, "BẢN NHÁP — CHƯA KÝ DUYỆT");
});
