import { test } from "node:test";
import assert from "node:assert/strict";
import { chiaCanhBaoCa, chiaCanhBaoMenhDe, nhanXemThem, type CanhBaoToiThieu } from "./nganSachCanhBao";

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
