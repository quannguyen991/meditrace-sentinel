import assert from "node:assert/strict";
import test from "node:test";
import { gopTabBanNhap, laMauSoapTrong } from "./gopTabBanNhap";
import type { DocumentTabItem } from "../types";

const loiThoai: DocumentTabItem = { id: "tab-transcript", title: "Lời thoại", type: "transcript", content: "", isClosable: false };
const soapTrong: DocumentTabItem = {
  id: "tab-soap",
  title: "Bệnh án SOAP",
  type: "soap",
  content: "Lý do vào viện (Chủ quan):\n\nTiền sử bệnh lý & Dị ứng:\n\nKế hoạch điều trị & Đơn thuốc:",
  isClosable: false,
};
const banNhap = (id: string, content: string): DocumentTabItem => ({ id, title: "Bản nháp hồ sơ", type: "custom", content, isClosable: true });

test("mau_soap_trong_bi_thay_bang_ban_nhap", () => {
  const kq = gopTabBanNhap([loiThoai, soapTrong], banNhap("d1", "LÝ DO KHÁM\nchóng mặt"));
  assert.deepEqual(kq.map((t) => t.id), ["tab-transcript", "d1"]);
});

test("soap_bac_si_da_go_thi_giu", () => {
  const daGo = { ...soapTrong, content: soapTrong.content + "\nbác sĩ ghi thêm: theo dõi huyết áp" };
  assert.equal(laMauSoapTrong(daGo), false);
  const kq = gopTabBanNhap([loiThoai, daGo], banNhap("d1", "x"));
  assert.deepEqual(kq.map((t) => t.id), ["tab-transcript", "tab-soap", "d1"]);
});

test("tao_lai_thi_thay_ban_nhap_cu", () => {
  const kq = gopTabBanNhap([loiThoai, banNhap("d1", "cũ")], banNhap("d2", "mới"));
  assert.deepEqual(kq.map((t) => t.id), ["tab-transcript", "d2"]);
});

test("mau_co_ly_do_vao_vien_da_dien_khong_phai_mau_trong", () => {
  assert.equal(laMauSoapTrong({ ...soapTrong, content: "Chủ quan (S):\n- Lý do vào viện: ho 3 ngày\n\nKế hoạch (P):" }), false);
  assert.equal(laMauSoapTrong({ ...soapTrong, content: "Chủ quan (S):\n- Lý do vào viện:\n\nKế hoạch (P):" }), true);
});
