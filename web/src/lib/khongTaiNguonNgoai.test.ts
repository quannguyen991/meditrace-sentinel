/**
 * Đảm bảo giao diện web không tự động tải tài nguyên ngoài (như Google Fonts)
 * làm rò rỉ địa chỉ IP của máy trạm bệnh viện ra máy chủ bên thứ ba.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const GOC_WEB = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const TEP_INDEX_HTML = path.join(GOC_WEB, "index.html");

function docIndexHtml(): string {
  return fs.readFileSync(TEP_INDEX_HTML, "utf-8");
}

test("khong_tai_google_fonts_trong_index_html", () => {
  const html = docIndexHtml();
  assert.ok(!html.includes("fonts.googleapis.com"), "index.html vẫn chứa fonts.googleapis.com");
  assert.ok(!html.includes("fonts.gstatic.com"), "index.html vẫn chứa fonts.gstatic.com");
});

test("khong_co_the_link_hoac_script_tro_ra_http_ngoai", () => {
  const htmlKhongChuThich = docIndexHtml().replace(/<!--[\s\S]*?-->/g, "");
  const cacThe = htmlKhongChuThich.match(/<(?:link|script)\b[^>]*>/gi) ?? [];
  const theViPham = cacThe.filter((the) => /https?:\/\//i.test(the));
  assert.deepEqual(
    theViPham,
    [],
    `Phát hiện thẻ <link>/<script> tải tài nguyên ngoài qua HTTP(S): ${theViPham.join("; ")}`,
  );
});
