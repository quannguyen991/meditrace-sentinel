/**
 * Phông web (Google Fonts) đã bị gỡ để trang không gọi ra ngoài. Khi đó trình duyệt dùng phông dự phòng,
 * nên phông dự phòng ĐẦU TIÊN phải hiển thị đúng dấu tiếng Việt chồng tầng ("hồ", "đều").
 * Georgia ghép dấu huyền lệch khỏi chữ ("hô`"), đã thấy trên bản demo 28/11/2026.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const CSS = fs.readFileSync(path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../index.css"), "utf-8");
const PHONG_VIET_TOT = ["Times New Roman", "Noto Serif", "Cambria", "Segoe UI", "Arial", "Noto Sans", "Roboto"];

function phongDau(bien: string): string {
  const m = CSS.match(new RegExp(`--${bien}:\\s*([^;]+);`));
  assert.ok(m, `không thấy --${bien}`);
  return m![1].split(",")[0].trim().replace(/^["']|["']$/g, "");
}

test("phong_serif_dau_tien_hien_thi_duoc_tieng_viet", () => {
  assert.ok(PHONG_VIET_TOT.includes(phongDau("font-serif")), phongDau("font-serif"));
});

test("phong_sans_dau_tien_hien_thi_duoc_tieng_viet", () => {
  assert.ok(PHONG_VIET_TOT.includes(phongDau("font-sans")), phongDau("font-sans"));
});
