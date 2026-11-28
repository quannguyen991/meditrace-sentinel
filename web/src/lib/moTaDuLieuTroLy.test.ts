import assert from "node:assert/strict";
import test from "node:test";
import { moTaDuLieuTroLy } from "./moTaDuLieuTroLy";

test("chua_co_ban_nhap_thi_bao_ro", () => {
  const kq = moTaDuLieuTroLy({ coBanNhap: false, soMenhDe: 0 });
  assert.equal(kq.coDuLieu, false);
  assert.match(kq.chu, /Chưa có bản nháp/);
});

test("co_ban_nhap_thi_neu_so_menh_de_tuoi_gioi", () => {
  const kq = moTaDuLieuTroLy({ coBanNhap: true, soMenhDe: 16, tuoi: 58, gioi: "nam" });
  assert.equal(kq.coDuLieu, true);
  assert.equal(kq.chu, "Đang dùng: 16 mệnh đề của ca · 58 tuổi · nam (không gửi tên, ngày, địa chỉ)");
});

test("thieu_tuoi_gioi_van_hien_so_menh_de", () => {
  assert.match(moTaDuLieuTroLy({ coBanNhap: true, soMenhDe: 3 }).chu, /^Đang dùng: 3 mệnh đề của ca \(/);
});
