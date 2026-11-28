import assert from "node:assert/strict";
import test from "node:test";
import { layLoiThoaiTuTep, loaiTepDauVao, NHAN_TEP_DAU_VAO } from "./loaiTepDauVao";

test("phu_de_srt_vtt_la_loi_thoai_va_bo_moc_gio", () => {
  assert.equal(loaiTepDauVao({ name: "ca.srt" }), "loi_thoai");
  assert.equal(loaiTepDauVao({ name: "ca.vtt", type: "text/vtt" }), "loi_thoai");
  const srt = "1\r\n00:00:01,000 --> 00:00:03,500\r\nBác sĩ: Chào anh.\r\n\r\n2\r\n00:00:04,000 --> 00:00:06,000\r\nBệnh nhân: Tôi ho ba ngày.\r\n";
  assert.equal(layLoiThoaiTuTep("ca.srt", srt), "Bác sĩ: Chào anh.\nBệnh nhân: Tôi ho ba ngày.");
  const vtt = "WEBVTT\n\n00:01.000 --> 00:03.000\nBác sĩ: Chào chị.\n";
  assert.equal(layLoiThoaiTuTep("ca.vtt", vtt), "Bác sĩ: Chào chị.");
  assert.equal(layLoiThoaiTuTep("ca.txt", "  Bác sĩ: 1\n"), "Bác sĩ: 1");
  assert.match(NHAN_TEP_DAU_VAO, /audio\/\*/);
  assert.match(NHAN_TEP_DAU_VAO, /\.srt/);
});

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
