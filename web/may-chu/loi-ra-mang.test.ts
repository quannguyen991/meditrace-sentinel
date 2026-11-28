/**
 * Mọi lối ra mạng của máy chủ web phải nằm trong `LOI_RA_DUOC_PHEP`.
 * Thêm một `fetch(` mới mà quên khai báo thì test này đỏ — danh sách này cũng là nguồn của sơ đồ dữ liệu.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { LOI_RA_DUOC_PHEP } from "./loi-ra-mang";

const THU_MUC = path.dirname(fileURLToPath(import.meta.url));
const GOC_WEB = path.resolve(THU_MUC, "..");

function cacTep(thuMuc: string): string[] {
  const ra: string[] = [];
  for (const muc of fs.readdirSync(thuMuc, { withFileTypes: true })) {
    const p = path.join(thuMuc, muc.name);
    if (muc.isDirectory()) ra.push(...cacTep(p));
    else if (muc.name.endsWith(".ts") && !muc.name.endsWith(".test.ts")) ra.push(p);
  }
  return ra;
}

function demFetch(): Map<string, number> {
  const dem = new Map<string, number>();
  for (const tep of [...cacTep(THU_MUC), path.join(GOC_WEB, "server.ts")]) {
    const n = (fs.readFileSync(tep, "utf-8").match(/(?<![\w.])fetch\(/g) || []).length;
    if (n) dem.set(path.relative(GOC_WEB, tep).split(path.sep).join("/"), n);
  }
  return dem;
}

test("moi_fetch_deu_co_trong_danh_sach_loi_ra", () => {
  const thucTe = demFetch();
  const khaiBao = new Map<string, number>();
  for (const m of LOI_RA_DUOC_PHEP) khaiBao.set(m.tep, (khaiBao.get(m.tep) || 0) + 1);
  assert.deepEqual(Object.fromEntries([...thucTe].sort()), Object.fromEntries([...khaiBao].sort()));
});

test("muc_nao_cung_co_mo_ta", () => {
  for (const m of LOI_RA_DUOC_PHEP) {
    assert.ok(m.dich.trim() && m.mucDich.trim() && m.duLieu.trim(), JSON.stringify(m));
    assert.ok(m.macDinh === "bat" || m.macDinh === "tat");
  }
});
