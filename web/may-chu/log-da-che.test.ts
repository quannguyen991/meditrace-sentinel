/**
 * Log lỗi của máy chủ web không được in đối tượng lỗi thô (thông điệp lỗi có thể chứa lời thoại,
 * ví dụ lỗi JSON.parse trích một đoạn dữ liệu ca khám). Mọi console.error/warn có biến lỗi phải qua cheLog.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const THU_MUC = path.dirname(fileURLToPath(import.meta.url));

function cacTep(thuMuc: string): string[] {
  const ra: string[] = [];
  for (const muc of fs.readdirSync(thuMuc, { withFileTypes: true })) {
    const p = path.join(thuMuc, muc.name);
    if (muc.isDirectory()) ra.push(...cacTep(p));
    else if (muc.name.endsWith(".ts") && !muc.name.endsWith(".test.ts")) ra.push(p);
  }
  return ra;
}

test("console_error_co_bien_loi_deu_qua_cheLog", () => {
  const vi_pham: string[] = [];
  for (const tep of cacTep(THU_MUC)) {
    fs.readFileSync(tep, "utf-8").split("\n").forEach((d, i) => {
      if (!/console\.(error|warn)\(/.test(d)) return;
      const coBienLoi = /[(,]\s*(err|e|exc|error|loi)\b(?!["'`])/.test(d) || /\$\{\s*(err|e)\b/.test(d);
      if (coBienLoi && !d.includes("cheLog(")) vi_pham.push(`${path.relative(THU_MUC, tep)}:${i + 1}: ${d.trim()}`);
    });
  }
  assert.deepEqual(vi_pham, []);
});
