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
const { caMauDuDieuKienKy, kyCaMau, luuCaMau, taoCaDaKy } = await import("./ho-tro-kiem-thu-ky-duyet");
const { tinhKyDuyetTuCa } = await import("../src/lib/kyDuyet");

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
  assert.equal(kiemDaKyChoXuat(1, "ca_da_ky").duoc, true);
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

test("tab chưa sửa (đã ký trước đó) không che được tab đã ký sau rồi bị sửa", () => {
  luuCaMau(1, caMauDuDieuKienKy("ca_hai_tab"));
  kyCaMau(1, "ca_hai_tab", "tab-doc"); // lần ký 1: bản nháp
  kyCaMau(1, "ca_hai_tab", "tab-soap"); // lần ký 2 (mới nhất): SOAP
  // Sửa SOAP sau lần ký mới nhất; trình duyệt ghi signOff.tabId trỏ về tab bản nháp chưa sửa.
  luuCaMau(1, caMauDuDieuKienKy("ca_hai_tab", { soap: "S: đã sửa sau ký", signOffTabId: "tab-doc" }));
  const r = kiemDaKyChoXuat(1, "ca_hai_tab");
  assert.equal(r.duoc, false, "chỉ đúng tab của lần ký mới nhất (máy chủ ghi) mới là bằng chứng");
});

test("signOff.tabId do trình duyệt ghi không đổi được tab đối chiếu", () => {
  luuCaMau(1, caMauDuDieuKienKy("ca_tab_gia"));
  kyCaMau(1, "ca_tab_gia", "tab-soap");
  luuCaMau(1, caMauDuDieuKienKy("ca_tab_gia", { soap: "S: sửa", signOffTabId: "tab-doc" }));
  assert.equal(kiemDaKyChoXuat(1, "ca_tab_gia").duoc, false);
});

test("được xuất thì trả kèm bản chụp đã ký và đúng tab đã ký", () => {
  luuCaMau(1, caMauDuDieuKienKy("ca_ban_chup", { ten: "Lúc ký" }));
  kyCaMau(1, "ca_ban_chup", "tab-soap");
  // Đổi trường không nằm trong băm sau khi ký: vẫn được xuất, nhưng nội dung xuất là bản lúc ký.
  luuCaMau(1, caMauDuDieuKienKy("ca_ban_chup", { ten: "Sau khi ký" }));
  const r = kiemDaKyChoXuat(1, "ca_ban_chup") as any;
  assert.equal(r.duoc, true);
  assert.equal(r.banKy?.tabId, "tab-soap");
  assert.equal(r.banKy?.duLieu?.patientIdentifier, "Lúc ký");
});

test("chữ ký WORM cũ không có bản chụp máy chủ: phải ký lại", () => {
  luuCaMau(1, caMauDuDieuKienKy("ca_ky_kieu_cu"));
  const kq = tinhKyDuyetTuCa(caMauDuDieuKienKy("ca_ky_kieu_cu"));
  khoWorm.ghiSignOff({
    sessionId: "ca_ky_kieu_cu",
    userId: 1,
    tongMenhDe: kq.tongMenhDe,
    soGiu: kq.soGiu,
    soSua: kq.soSua,
    soBo: kq.soBo,
    tyLeCoNguon: kq.tyLeCoNguon,
    contentHash: kq.contentHash,
    soChuaXacNhan: kq.soChuaXacNhan,
  });
  const r = kiemDaKyChoXuat(1, "ca_ky_kieu_cu");
  assert.equal(r.duoc, false);
  assert.match(r.lyDo || "", /ký lại/i);
});
