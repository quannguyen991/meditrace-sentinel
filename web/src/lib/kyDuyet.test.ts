import assert from "node:assert/strict";
import crypto from "node:crypto";
import test from "node:test";
import { bamChuoi as bamChuoiCu } from "../hooks/useSessionsStore";
import { buildSignOffCanonicalPayload } from "./compileEffectiveNote";
import { bamChuoi, chonTabBenhAnDeBam, khoaDuyetCuaNote, tinhKyDuyetTuCa } from "./kyDuyet";

const NOI_DUNG_NHAP = "LÝ DO KHÁM BỆNH\nđau ngực [T1]\n\nCẦN XÁC NHẬN\nsốt? [T2]";
const tabs = [
  { id: "tab-transcript", title: "Lời thoại", type: "transcript", content: "BS: chào\nBN: đau ngực" },
  { id: "tab-soap", title: "Bệnh án SOAP", type: "soap", content: "Chủ quan (S): đau ngực" },
  { id: "tab-leaflet", title: "Tờ dặn dò", type: "leaflet", content: "Uống nhiều nước" },
  { id: "tab-doc-1", title: "Bản nháp hồ sơ", type: "custom", content: NOI_DUNG_NHAP },
] as any[];

function taoCa(quyet: Record<number, string>, banSua: Record<number, string> = {}, them: Record<string, unknown> = {}) {
  const note = {
    caseId: "py_1",
    content: NOI_DUNG_NHAP,
    propositions: [
      { id: 1, text: "đau ngực", status: "than", evidenceTurns: [1] },
      { id: 2, text: "sốt?", status: "can_xac_nhan", evidenceTurns: [2] },
    ],
  };
  return {
    id: "ca_1",
    tabs,
    activeTabId: "tab-transcript",
    note,
    duyet: { khoa: khoaDuyetCuaNote(note), quyet, banSua },
    ...them,
  };
}

test("bamChuoi dùng chung giữa giao diện và máy chủ", () => {
  assert.equal(bamChuoi("abc"), bamChuoiCu("abc"));
});

test("chonTabBenhAnDeBam: không phụ thuộc tab đang mở; giữ đúng tab đã ký", () => {
  // Đang mở lời thoại hay tờ dặn dò đều băm cùng một tab (bản nháp hồ sơ mới nhất)
  assert.equal(chonTabBenhAnDeBam(tabs, NOI_DUNG_NHAP).tabId, "tab-doc-1");
  assert.equal(chonTabBenhAnDeBam(tabs, NOI_DUNG_NHAP, "tab-leaflet").tabId, "tab-doc-1", "tab không phải bệnh án bị bỏ qua");
  assert.equal(chonTabBenhAnDeBam(tabs, NOI_DUNG_NHAP, "tab-transcript").tabId, "tab-doc-1");
  // Tab đã ký (SOAP) luôn được băm lại đúng tab đó, kể cả khi người dùng đang mở tab khác
  const r = chonTabBenhAnDeBam(tabs, NOI_DUNG_NHAP, "tab-soap");
  assert.equal(r.tabId, "tab-soap");
  assert.equal(r.noiDung, "Chủ quan (S): đau ngực");
  // Không có tab bệnh án nào: dùng nội dung bản nháp
  assert.deepEqual(chonTabBenhAnDeBam([tabs[0]], "nháp"), { tabId: null, noiDung: "nháp" });
});

test("tinhKyDuyetTuCa: đếm và băm từ dữ liệu ca đã lưu, chặn khi còn mục cần xác nhận", () => {
  const chua = tinhKyDuyetTuCa(taoCa({ 1: "giu" }));
  assert.equal(chua.kiemTra.duDieuKien, false);
  assert.equal(chua.kiemTra.maLoi, "con_muc_can_xac_nhan");
  assert.equal(chua.soChuaXacNhan, 1);

  const du = tinhKyDuyetTuCa(taoCa({ 1: "giu", 2: "sua" }, { 2: "không sốt" }));
  assert.equal(du.kiemTra.duDieuKien, true);
  assert.equal(du.soChuaXacNhan, 0);
  assert.deepEqual(
    { t: du.tongMenhDe, g: du.soGiu, s: du.soSua, b: du.soBo, n: du.tyLeCoNguon, tab: du.tabId },
    { t: 2, g: 1, s: 1, b: 0, n: 100, tab: "tab-doc-1" },
  );
  const ky = buildSignOffCanonicalPayload(NOI_DUNG_NHAP, { 1: "giu", 2: "sua" }, { 2: "không sốt" });
  assert.equal(du.canonical, ky);
  assert.equal(du.contentHash, crypto.createHash("sha256").update(ky).digest("hex"));

  // Quyết định duyệt của bản nháp CŨ (khoá không khớp) không được tính
  const lech = taoCa({ 1: "giu", 2: "giu" });
  (lech.duyet as any).khoa = "khac#1#x";
  assert.equal(tinhKyDuyetTuCa(lech).kiemTra.maLoi, "con_muc_can_xac_nhan");

  // Dữ liệu hỏng / không có bản nháp
  assert.equal(tinhKyDuyetTuCa({ id: "x" }).kiemTra.maLoi, "khong_co_menh_de");
  assert.equal(tinhKyDuyetTuCa(null).kiemTra.duDieuKien, false);
});
