/** Chạy: npx tsx src/lib/vietHoaCau.test.ts (trong thư mục web/) */
import assert from "node:assert/strict";
import { vietHoaCau, vietHoaDauDong } from "./vietHoaCau";

assert.equal(vietHoaCau("cảm giác vướng víu khó chịu."), "Cảm giác vướng víu khó chịu.");
assert.equal(vietHoaCau("đau ngực. khám bìu phẻ to. hết phát đồ."), "Đau ngực. Khám bìu phẻ to. Hết phát đồ.");
assert.equal(vietHoaCau("- amlodipin 10 mg ngày một lần"), "- Amlodipin 10 mg ngày một lần");
assert.equal(vietHoaCau("1. đau đầu"), "1. Đau đầu");
assert.equal(vietHoaCau("đúng rồi? ừ. không sao!"), "Đúng rồi? Ừ. Không sao!");
// số thập phân và đã viết hoa thì giữ nguyên
assert.equal(vietHoaCau("nhiệt độ 37.5 độ, huyết áp 120/80."), "Nhiệt độ 37.5 độ, huyết áp 120/80.");
assert.equal(vietHoaCau("LÝ DO KHÁM BỆNH"), "LÝ DO KHÁM BỆNH");
assert.equal(vietHoaCau(""), "");
// độ dài không đổi (để ghép mệnh đề theo vị trí vẫn đúng)
for (const s of ["đã uống thuốc. đỡ nhiều.", "- ăn kém. ngủ ít", "đau bụng"]) assert.equal(vietHoaCau(s).length, s.length);
assert.equal(vietHoaDauDong("a b\n\n- c d. e f"), "A b\n\n- C d. E f");
console.log("vietHoaCau.test.ts: tất cả đều qua");
