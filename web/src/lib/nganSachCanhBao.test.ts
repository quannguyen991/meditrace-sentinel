import { test } from "node:test";
import assert from "node:assert/strict";
import { chiaCanhBaoCa, chiaCanhBaoMenhDe, nhanXemThem, tachTheVaGhiChu, type CanhBaoToiThieu } from "./nganSachCanhBao";

const cb = (code: string, severity: CanhBaoToiThieu["severity"] = "trung", kind: CanhBaoToiThieu["kind"] = "nghi_rui_ro") =>
  ({ code, severity, kind });

test("có canh_bao_hien: chỉ dựng phần hiện, phần gập nằm sau nút", () => {
  const p = {
    warning: cb("SPEAKER_SUBJECT_MISMATCH"),
    otherWarnings: [cb("WRONG_SUBJECT")],
    warningsShown: [cb("NEGATION_FLIP", "cao", "loi_phat_hien"), cb("SUBJECT_AMBIGUOUS")],
    warningsFolded: [cb("SPEAKER_SUBJECT_MISMATCH", "thap"), cb("DUPLICATE_INFORMATION", "thap", "can_xem"), cb("PAST_CURRENT_CONFUSION")],
  };
  const r = chiaCanhBaoMenhDe(p);
  assert.equal(r.coNganSach, true);
  assert.equal(r.chinh?.code, "NEGATION_FLIP");
  assert.deepEqual(r.hienThem.map((c) => c.code), ["SUBJECT_AMBIGUOUS"]);
  assert.equal(r.gap.length, 3);
  assert.equal(nhanXemThem(r.gap.length, false), "Xem thêm 3 gợi ý");
  assert.equal(nhanXemThem(r.gap.length, true), "Ẩn 3 gợi ý");
});

test("phần hiện rỗng nhưng có gợi ý: không có thẻ chính, vẫn có nút", () => {
  const r = chiaCanhBaoMenhDe({ warning: cb("SPEAKER_SUBJECT_MISMATCH"), warningsShown: [], warningsFolded: [cb("SPEAKER_SUBJECT_MISMATCH", "thap")] });
  assert.equal(r.chinh, null);
  assert.equal(r.gap.length, 1);
});

test("thiếu trường ngân sách: giữ cách cũ (chính + dấu hiệu khác)", () => {
  const p = { warning: cb("WRONG_SUBJECT", "cao"), otherWarnings: [cb("NEGATION_FLIP", "cao")] };
  const r = chiaCanhBaoMenhDe(p);
  assert.equal(r.coNganSach, false);
  assert.equal(r.chinh?.code, "WRONG_SUBJECT");
  assert.deepEqual(r.hienThem, []);
  assert.deepEqual(r.gap.map((c) => c.code), ["NEGATION_FLIP"]);
  assert.equal(chiaCanhBaoMenhDe({}).chinh, null);
});

test("cảnh báo đầu là can_xem (thành ghi chú): mọi cảnh báo hiện khác vẫn được dựng", () => {
  const chia = chiaCanhBaoMenhDe({
    warningsShown: [cb("APPROXIMATION_LOST", "thap", "can_xem"), cb("SUBJECT_AMBIGUOUS"), cb("NEGATION_FLIP", "cao", "loi_phat_hien")],
    warningsFolded: [cb("SPEAKER_SUBJECT_MISMATCH", "thap")],
  });
  const t = tachTheVaGhiChu(chia, false);
  assert.equal(t.the, null);
  assert.equal(t.ghiChu?.code, "APPROXIMATION_LOST");
  assert.deepEqual(t.dongHien.map((c) => c.code), ["SUBJECT_AMBIGUOUS", "NEGATION_FLIP"]);
  // tổng số hiện trên giao diện = đúng phần hien của ngân sách
  assert.equal((t.the ? 1 : 0) + (t.ghiChu ? 1 : 0) + t.dongHien.length, 3);
  // dòng đang bị chặn (canh): cảnh báo can_xem vẫn là thẻ, không thành ghi chú
  const t2 = tachTheVaGhiChu(chia, true);
  assert.equal(t2.the?.code, "APPROXIMATION_LOST");
  assert.equal(t2.ghiChu, null);
  // bỏ qua cảnh báo: không dựng gì
  assert.deepEqual(tachTheVaGhiChu(chia, false, true), { the: null, ghiChu: null, dongHien: [] });
});

test("cảnh báo đầu là thẻ: các cảnh báo hiện khác nằm trong dongHien", () => {
  const t = tachTheVaGhiChu(chiaCanhBaoMenhDe({ warningsShown: [cb("WRONG_SUBJECT", "cao"), cb("SUBJECT_AMBIGUOUS")] }), false);
  assert.equal(t.the?.code, "WRONG_SUBJECT");
  assert.deepEqual(t.dongHien.map((c) => c.code), ["SUBJECT_AMBIGUOUS"]);
});

test("cảnh báo toàn ca: có ngân sách thì chia, không có thì hiện hết", () => {
  const ds = [cb("OMITTED_MEDICATION", "cao"), cb("OMITTED_ANSWER"), cb("POSSIBLE_IMPORTANT_OMISSION", "thap")];
  const moi = chiaCanhBaoCa({ caseWarnings: ds, caseWarningsShown: ds.slice(0, 2), caseWarningsFolded: ds.slice(2) });
  assert.equal(moi.coNganSach, true);
  assert.equal(moi.hien.length, 2);
  assert.equal(moi.gap.length, 1);
  const cu = chiaCanhBaoCa({ caseWarnings: ds });
  assert.equal(cu.coNganSach, false);
  assert.equal(cu.hien.length, 3);
  assert.deepEqual(cu.gap, []);
});
