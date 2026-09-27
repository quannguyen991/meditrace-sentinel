/**
 * Kiểm ghép mệnh đề với câu bản nháp. Chạy: npx tsx src/lib/ghepMenhDe.test.ts
 */
import assert from "node:assert/strict";
import { ghepMenhDe, tachCau, doGiong } from "./ghepMenhDe";

const laTieuDe = (d: string) => d.trim().length > 0 && d.trim() === d.trim().toLocaleUpperCase("vi") && /\p{Lu}/u.test(d);
const ds = [
  { id: 0, text: "bà: nghẹt mũi (gần một tuần)" },
  { id: 1, text: "bà: nghẹt mũi (từ hôm kia)" },
  { id: 2, text: "bà: đau tăng khi cúi" },
  { id: 3, text: "bà: đau tăng khi cúi chỉ bị lúc sáng sớm" },
  { id: 8, text: "bà: amoxicillin 250 mg, uống" },
];
const ghepVao = (nd: string) => {
  const k = ghepMenhDe(nd, ds, laTieuDe);
  const dong = nd.split("\n");
  const ra: Record<number, { chu: string; gan: boolean }> = {};
  for (const [i, d] of k) for (const x of d) ra[x.id] = { chu: dong[i].slice(x.bd, x.kt), gan: x.ganDung };
  return ra;
};

// 1. nguyên văn: không để câu ngắn ăn vào câu dài
{
  const r = ghepVao("TIỀN SỬ\n\nbà: đau tăng khi cúi. bà: đau tăng khi cúi chỉ bị lúc sáng sớm.");
  assert.equal(r[2].chu, "bà: đau tăng khi cúi");
  assert.equal(r[3].chu, "bà: đau tăng khi cúi chỉ bị lúc sáng sớm");
  assert.equal(r[2].gan, false);
}

// 2. bác sĩ sửa chữ -> vẫn ghép (gần đúng), bỏ phần giải thích sau " — "
{
  const r = ghepVao("CẦN XÁC NHẬN\n\nbà: nghẹt mũi khoảng gần một tuần nay — đã hỏi lại. bà: amoxicillin 500 mg, uống — đoạn dẫn nói về bệnh nhân.");
  assert.equal(r[0].chu, "bà: nghẹt mũi khoảng gần một tuần nay");
  assert.equal(r[0].gan, true);
  assert.equal(r[8].chu, "bà: amoxicillin 500 mg, uống");
  assert.equal(r[8].gan, true);
  // "nghẹt mũi (từ hôm kia)" không được ghép nhầm vào câu "gần một tuần" (câu đó đã thuộc mệnh đề 0)
  assert.equal(r[1], undefined);
}

// 3. câu hỏi làm rõ không bị ghép dù giống
{
  const r = ghepVao("CÂU HỎI LÀM RÕ\n\n1. Nghẹt mũi: đúng là gần một tuần hay từ hôm kia ạ?");
  assert.equal(r[0], undefined);
  assert.equal(r[1], undefined);
}

// 4. sửa quá nhiều (khác hẳn) -> không ghép
{
  const r = ghepVao("bà: ho khan về đêm.");
  assert.equal(Object.keys(r).length, 0);
}

// 5. chữ bác sĩ sửa ở ngăn duyệt cũng khớp nguyên văn
{
  const k = ghepMenhDe("bà: amoxicillin 500 mg ngày 2 lần.", [{ id: 8, text: "bà: amoxicillin 250 mg, uống", textKhac: ["bà: amoxicillin 500 mg ngày 2 lần"] }]);
  const d = [...k.values()][0][0];
  assert.equal(d.ganDung, false);
}

// phụ trợ
assert.deepEqual(tachCau("a. b — c. d?").map((c) => c.laHoi), [false, false, true]);
assert.ok(doGiong("bà: nghẹt mũi (gần một tuần)", "bà nghẹt mũi gần một tuần") === 1);

console.log("ghepMenhDe: tất cả phép thử qua");
