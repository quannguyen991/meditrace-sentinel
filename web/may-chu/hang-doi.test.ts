/**
 * Kiểm hàng đợi việc nền. Chạy: npx tsx may-chu/hang-doi.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import { taoHangDoi } from "./hang-doi";

const moi = () => taoHangDoi(new DatabaseSync(":memory:"));

// 1. thêm hai lần cùng khoá -> cùng id; khoá khác hoặc người khác -> id khác
{
  const h = moi();
  const a = h.them(1, "phien-A", "{}");
  assert.equal(h.them(1, "phien-A", "{}"), a);
  assert.notEqual(h.them(1, "phien-B", "{}"), a);
  assert.notEqual(h.them(2, "phien-A", "{}"), a);
}

// 2. lấy việc theo thứ tự thêm, mỗi việc chỉ một lần; hết việc -> null
{
  const h = moi();
  const a = h.them(1, "a", "tai-a");
  const b = h.them(1, "b", "tai-b");
  const x = h.layViecTiepTheo();
  assert.deepEqual(x, { id: a, nguoiDungId: 1, taiTrong: "tai-a" });
  const y = h.layViecTiepTheo();
  assert.equal(y?.id, b);
  assert.equal(h.layViecTiepTheo(), null);
  assert.equal(h.trangThai(a, 1)?.trangThai, "dang_chay");
}

// 3. xong và lỗi đổi trạng thái; việc đã xong thì cùng khoá được thêm lại thành việc mới
{
  const h = moi();
  const a = h.them(1, "a", "{}");
  h.layViecTiepTheo();
  h.xong(a, "ket-qua");
  assert.equal(h.trangThai(a, 1)?.trangThai, "xong");
  assert.equal(h.trangThai(a, 1)?.ketQua, "ket-qua");
  const b = h.them(1, "a", "{}");
  assert.notEqual(b, a);
  h.layViecTiepTheo();
  h.loi(b, "model_loi");
  assert.equal(h.trangThai(b, 1)?.trangThai, "that_bai");
  assert.equal(h.trangThai(b, 1)?.ma, "model_loi");
}

// 4. khôi phục: dang_chay lần 1 -> chạy lại; dang_chay lần 2 -> that_bai crash_recovery_exhausted
{
  const h = moi();
  const a = h.them(1, "a", "{}");
  h.layViecTiepTheo(); // so_lan_thu = 1, dang_chay
  assert.deepEqual(h.khoiPhucSauKhoiDong(), { chayLai: 1, thatBai: 0 });
  assert.equal(h.trangThai(a, 1)?.trangThai, "cho_chay");
  assert.equal(h.layViecTiepTheo()?.id, a); // so_lan_thu = 2
  assert.deepEqual(h.khoiPhucSauKhoiDong(), { chayLai: 0, thatBai: 1 });
  assert.equal(h.trangThai(a, 1)?.trangThai, "that_bai");
  assert.equal(h.trangThai(a, 1)?.ma, "crash_recovery_exhausted");
  // việc chờ và việc xong không bị đụng vào
  const b = h.them(1, "b", "{}");
  assert.deepEqual(h.khoiPhucSauKhoiDong(), { chayLai: 0, thatBai: 0 });
  assert.equal(h.trangThai(b, 1)?.trangThai, "cho_chay");
}

// 5. không đọc được việc của người khác
{
  const h = moi();
  const a = h.them(1, "a", "{}");
  assert.equal(h.trangThai(a, 2), null);
  assert.equal(h.trangThai(9999, 1), null);
}

// 6. còn sau khi đóng và mở lại tệp CSDL (mô phỏng khởi động lại máy chủ)
{
  const tep = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "hd-")), "t.db");
  const d1 = new DatabaseSync(tep);
  const h1 = taoHangDoi(d1);
  const a = h1.them(7, "phien", "tai");
  h1.layViecTiepTheo(); // đang chạy khi "máy chủ tắt"
  d1.close();
  const d2 = new DatabaseSync(tep);
  const h2 = taoHangDoi(d2);
  assert.deepEqual(h2.khoiPhucSauKhoiDong(), { chayLai: 1, thatBai: 0 });
  assert.deepEqual(h2.layViecTiepTheo(), { id: a, nguoiDungId: 7, taiTrong: "tai" });
  d2.close();
}

// 7. số việc trước, xoá theo chủ, dọn việc cũ
{
  const h = moi();
  const a = h.them(1, "a", "{}");
  const b = h.them(1, "b", "{}");
  const c = h.them(2, "c", "{}");
  assert.equal(h.soViecTruoc(a), 0);
  assert.equal(h.soViecTruoc(b), 1);
  assert.equal(h.soViecTruoc(c), 2);
  h.layViecTiepTheo();
  h.xong(a, "x");
  assert.equal(h.soViecTruoc(b), 0, "việc đã xong không tính là còn đứng trước");
  h.xoa(a, 2); // sai chủ: không xoá
  assert.ok(h.trangThai(a, 1));
  h.xoa(a, 1);
  assert.equal(h.trangThai(a, 1), null);
  h.layViecTiepTheo();
  h.loi(b, "e");
  assert.equal(h.donViecCu(60 * 60_000), 0, "việc mới chưa bị dọn");
  assert.equal(h.donViecCu(-1), 1, "tuổi tối đa âm: dọn mọi việc đã kết thúc");
  assert.equal(h.trangThai(c, 2)?.trangThai, "cho_chay", "việc đang chờ không bị dọn");
}

console.log("hang-doi.test.ts: tất cả đều qua");
