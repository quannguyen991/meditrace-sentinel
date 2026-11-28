import assert from "node:assert/strict";
import test from "node:test";
import { loaiTepDauVao } from "./loaiTepDauVao";

test("tep_am_thanh_theo_duoi_va_kieu", () => {
  assert.equal(loaiTepDauVao({ name: "ca_01.MP3" }), "am_thanh");
  assert.equal(loaiTepDauVao({ name: "ghi-am.m4a", type: "" }), "am_thanh");
  assert.equal(loaiTepDauVao({ name: "khong-duoi", type: "audio/webm" }), "am_thanh");
});

test("tep_loi_thoai_txt_md", () => {
  assert.equal(loaiTepDauVao({ name: "ca_01.txt" }), "loi_thoai");
  assert.equal(loaiTepDauVao({ name: "kich_ban.md", type: "text/markdown" }), "loi_thoai");
});

test("tep_khac_bi_tu_choi", () => {
  assert.equal(loaiTepDauVao({ name: "anh.png", type: "image/png" }), "khong_ho_tro");
  assert.equal(loaiTepDauVao({ name: "ho-so.pdf", type: "application/pdf" }), "khong_ho_tro");
});
