import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { LOI_RA_DUOC_PHEP } from "./loi-ra-mang";
import { NOI_LUU_DU_LIEU } from "./noi-luu-du-lieu";
import { sinhSoDoDuLieu, TEP_SO_DO } from "./sinh-so-do-du-lieu";

const bo = (s: string) => s.replace(/\r\n/g, "\n");

test("so_do_khop_tep", () => {
  assert.equal(
    bo(fs.readFileSync(TEP_SO_DO, "utf-8")),
    bo(sinhSoDoDuLieu()),
    "Sơ đồ lệch với mã: chạy `cd web; npx tsx may-chu/sinh-so-do-du-lieu.ts` để sinh lại, không sửa tay.",
  );
});

test("so_do_du_loi_ra", () => {
  const md = sinhSoDoDuLieu();
  for (const m of LOI_RA_DUOC_PHEP) assert.ok(md.includes(m.dich), m.dich);
});

test("so_do_du_noi_luu", () => {
  const md = sinhSoDoDuLieu();
  for (const n of NOI_LUU_DU_LIEU) assert.ok(md.includes(n.noi), n.noi);
});

test("so_do_ghi_ben_thu_ba_va_xac_nhan_tac_gia", () => {
  const md = sinhSoDoDuLieu();
  assert.ok(md.includes("AIBOX") && md.includes("bên thứ ba"));
  assert.ok(md.includes("Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào"));
});
