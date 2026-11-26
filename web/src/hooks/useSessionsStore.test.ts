import assert from "node:assert/strict";
import test from "node:test";
import { caBiXoaCoChuDich, gopKhiXungDot } from "./useSessionsStore";

const ca = (id: string, ten: string, them: Record<string, unknown> = {}) =>
  ({ id, patientIdentifier: ten, durationSeconds: 0, isRecording: false, transcript: "", tabs: [], ...them }) as any;

test("gopKhiXungDot: hai thiết bị — giữ sửa của cả hai, không mất ca, sửa trùng thì tách bản", () => {
  const goc = [ca("c1", "A"), ca("c2", "B"), ca("c4", "D")];
  // Máy này: sửa c2, xoá c4, tạo c5
  const mayNay = [ca("c5", "Mới máy này"), ca("c1", "A"), ca("c2", "B sửa máy này")];
  // Máy chủ (máy kia): sửa c1, tạo c3, giữ c4
  const mayChu = [ca("c3", "Mới máy kia"), ca("c1", "A sửa máy kia"), ca("c2", "B"), ca("c4", "D")];

  const gop = gopKhiXungDot(mayNay, mayChu, goc);
  const theoId = new Map(gop.map((s) => [s.id, s]));
  assert.equal(theoId.get("c1")!.patientIdentifier, "A sửa máy kia", "lấy bản máy kia khi máy này không sửa");
  assert.equal(theoId.get("c2")!.patientIdentifier, "B sửa máy này", "giữ bản máy này khi máy kia không sửa");
  assert.ok(theoId.has("c3"), "ca mới của máy kia không bị mất");
  assert.ok(theoId.has("c5"), "ca mới của máy này không bị mất");
  assert.ok(!theoId.has("c4"), "ca máy này đã xoá (máy kia không sửa) vẫn bị xoá");

  // Cả hai cùng sửa c1 khác nhau -> bản máy chủ giữ id, bản máy này tách thành ca riêng (không ký duyệt)
  const xung = gopKhiXungDot(
    [ca("c1", "A máy này", { signOff: { hash: "x" } })],
    [ca("c1", "A máy kia")],
    [ca("c1", "A")],
  );
  assert.equal(xung.length, 2);
  assert.equal(xung.find((s) => s.id === "c1")!.patientIdentifier, "A máy kia");
  const tach = xung.find((s) => s.id !== "c1")!;
  assert.match(tach.patientIdentifier, /A máy này/);
  assert.equal(tach.signOff, undefined);

  // Máy kia sửa c4 trong khi máy này xoá -> giữ c4 (không mất dữ liệu)
  const giu = gopKhiXungDot([], [ca("c4", "D sửa máy kia")], [ca("c4", "D")]);
  assert.deepEqual(giu.map((s) => s.id), ["c4"]);
  // Máy kia xoá c2 trong khi máy này sửa -> giữ bản máy này
  const hoiSinh = gopKhiXungDot([ca("c2", "B sửa")], [], [ca("c2", "B")]);
  assert.deepEqual(hoiSinh.map((s) => s.patientIdentifier), ["B sửa"]);
});

test("caBiXoaCoChuDich: chỉ những ca có ở lần đồng bộ trước mà nay không còn", () => {
  assert.deepEqual(caBiXoaCoChuDich([ca("a", ""), ca("b", "")], [ca("b", ""), ca("c", "")]), ["a"]);
  assert.deepEqual(caBiXoaCoChuDich(null, [ca("a", "")]), []);
});
