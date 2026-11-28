/**
 * Quy trình "bác sĩ phê duyệt trước khi dùng hồ sơ" chạy từ đầu đến cuối (Đề cải tiến 1, minh chứng 3).
 * Dùng đúng các hàm mà màn bản nháp (NoteEditorView) dùng: kiemTraDieuKienKyDuyet → ký (băm nội dung)
 * → isSignOffStale → choPhepDungHoSo.
 */
import assert from "node:assert/strict";
import test from "node:test";
import { choPhepDungHoSo } from "./choPhepDungHoSo";
import { computeNoteSignOffHashSync, isSignOffStale, kiemTraDieuKienKyDuyet } from "./compileEffectiveNote";

const NOI_DUNG = "LÝ DO KHÁM BỆNH\nho đờm 3 ngày\n\nCẦN XÁC NHẬN\nsốt 39 độ (bệnh nhân hay người nhà?)";
const MENH_DE = [
  { id: 1, status: "than", evidenceTurns: [2] },
  { id: 2, status: "can_xac_nhan", evidenceTurns: [4] },
  { id: 3, status: "than", evidenceTurns: [5] },
];

test("quy_trinh_phe_duyet_tu_dau_den_cuoi", () => {
  // 1. Bản nháp mới: còn mục cần xác nhận → không ký được, không dùng được hồ sơ.
  const b1 = kiemTraDieuKienKyDuyet(MENH_DE, {}, {});
  assert.equal(b1.duDieuKien, false);
  assert.equal(b1.maLoi, "con_muc_can_xac_nhan");
  assert.equal(choPhepDungHoSo({ daKy: false, daSuaSauKy: false }).duoc, false);

  // 2. Chọn "Sửa" nhưng để trống bản sửa → vẫn chưa đủ điều kiện.
  assert.equal(kiemTraDieuKienKyDuyet(MENH_DE, { 2: "sua" }, { 2: "  " }).duDieuKien, false);

  // 3. Bác sĩ xác nhận giữ mục 2 → đủ điều kiện ký.
  const quyet = { 2: "giu" as const };
  assert.equal(kiemTraDieuKienKyDuyet(MENH_DE, quyet, {}).duDieuKien, true);

  // 4. Ký: sổ WORM lưu băm nội dung + quyết định → được chép/in/xuất.
  const h = computeNoteSignOffHashSync(NOI_DUNG, quyet, {});
  const signOff = { hash: h, contentHash: h };
  assert.equal(isSignOffStale(signOff, h), false);
  assert.equal(choPhepDungHoSo({ daKy: true, daSuaSauKy: isSignOffStale(signOff, h) }).duoc, true);

  // 5. Sửa nội dung sau khi ký → băm đổi → khóa lại, phải ký lại.
  const h2 = computeNoteSignOffHashSync(NOI_DUNG + " (sửa sau ký)", quyet, {});
  assert.notEqual(h2, h);
  assert.equal(isSignOffStale(signOff, h2), true);
  assert.equal(choPhepDungHoSo({ daKy: true, daSuaSauKy: isSignOffStale(signOff, h2) }).duoc, false);

  // 6. Đổi quyết định duyệt sau khi ký (giữ → bỏ) cũng làm hồ sơ khóa lại.
  const h3 = computeNoteSignOffHashSync(NOI_DUNG, { 2: "bo" }, {});
  assert.equal(isSignOffStale(signOff, h3), true);
});
