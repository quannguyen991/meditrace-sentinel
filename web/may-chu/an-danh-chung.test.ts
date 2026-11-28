/**
 * Bộ ca rò rỉ định danh DÙNG CHUNG cho hai bộ che (TypeScript ở đây, Python ở
 * tests/test_ro_ri_dinh_danh_chung.py). Fixture: tests/fixtures/ro_ri_dinh_danh.json.
 *
 * Đạt khi: kq.ok === false (từ chối gửi) HOẶC mọi chuỗi `cam` vắng trong kq.van; khi kq.ok thì mọi
 * chuỗi `giu` còn nguyên.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { anDanhChoNgoai } from "./an-danh-ngoai";

type Ca = { van: string; cam: string[]; giu: string[] };
const THU_MUC = dirname(fileURLToPath(import.meta.url));
const CA: Ca[] = JSON.parse(readFileSync(resolve(THU_MUC, "../../tests/fixtures/ro_ri_dinh_danh.json"), "utf8"));

/** Chỉ số các ca đang lọt (Task 2 ghi lại, Task 3 gỡ): rỗng = mọi ca phải đạt. */
const DANG_LOT = new Set<number>([]);

test("bo_che_cong_ra_theo_bo_ca_chung: fixture đủ ca", () => {
  assert.ok(CA.length >= 24);
});

CA.forEach((ca, i) => {
  const ten = `bo_che_cong_ra_theo_bo_ca_chung ca${String(i).padStart(2, "0")}: ${ca.van}`;
  test(ten, { todo: DANG_LOT.has(i) ? "đang lọt, chờ vá" : undefined }, () => {
    const kq = anDanhChoNgoai(ca.van);
    if (!kq.ok) return;
    for (const c of ca.cam) assert.ok(!kq.van.includes(c), `còn lộ "${c}" trong: ${kq.van}`);
    for (const g of ca.giu) assert.ok(kq.van.includes(g), `mất chuỗi lâm sàng "${g}": ${kq.van}`);
  });
});
