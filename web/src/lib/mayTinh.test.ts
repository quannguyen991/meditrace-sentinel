/**
 * Kiểm máy tính lâm sàng bằng các giá trị tính tay. Chạy: npx tsx src/lib/mayTinh.test.ts
 */
import assert from "node:assert/strict";
import {
  bmi, bsaMosteller, creatininMgDl, crclCockcroftGault, egfrCkdEpi2021, giaiDoanEgfr,
  huyetApTrungBinh, lieuTheoCanNang, phanLoaiBmiChauA,
} from "./mayTinh";

const gan = (a: number, b: number, sai = 0.5) => assert.ok(Math.abs(a - b) <= sai, `${a} khác ${b}`);

// CKD-EPI 2021: nam 60 tuổi, Scr 1,0 mg/dL → 142 × (1/0,9)^−1,2 × 0,9938^60 ≈ 86,2
gan(egfrCkdEpi2021(1.0, 60, false), 86.2);
// nữ 50 tuổi, Scr 0,8 → 142 × (0,8/0,7)^−1,2 × 0,9938^50 × 1,012 ≈ 89,7
gan(egfrCkdEpi2021(0.8, 50, true), 89.7);
// nhánh Scr/κ < 1: nữ 30 tuổi, Scr 0,5 → 142 × 1,0845 × 0,8298 × 1,012 ≈ 129,3
gan(egfrCkdEpi2021(0.5, 30, true), 129.3);
assert.equal(giaiDoanEgfr(86.2), "G2 — giảm nhẹ");
assert.equal(giaiDoanEgfr(10), "G5 — suy thận");

gan(creatininMgDl(88.4), 1.0, 1e-9);
// Cockcroft–Gault: nam 60 tuổi, 70 kg, Scr 1,0 → 80 × 70 / 72 ≈ 77,8; nữ × 0,85 ≈ 66,1
gan(crclCockcroftGault(1.0, 60, 70, false), 77.8, 0.1);
gan(crclCockcroftGault(1.0, 60, 70, true), 66.1, 0.1);

gan(bmi(70, 170), 24.22, 0.01);
assert.equal(phanLoaiBmiChauA(24.22), "Thừa cân");
assert.equal(phanLoaiBmiChauA(22.9), "Bình thường");
assert.equal(phanLoaiBmiChauA(18.4), "Thiếu cân");
gan(bsaMosteller(70, 170), 1.818, 0.001);
gan(huyetApTrungBinh(120, 80), 93.33, 0.01);

const l = lieuTheoCanNang(15, 20, 3);
assert.deepEqual([l.mgNgay, l.mgLan, l.chamTran], [300, 100, false]);
const t = lieuTheoCanNang(60, 80, 4, 4000);
assert.deepEqual([t.mgNgay, t.mgLan, t.chamTran, t.mgNgayTheoCongThuc], [4000, 1000, true, 4800]);

console.log("mayTinh: tất cả phép kiểm đều qua");
