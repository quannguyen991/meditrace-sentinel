/**
 * Kiểm cài đặt trợ lý. Chạy: npx tsx may-chu/tro-ly/cai-dat-tro-ly.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import { DatabaseSync } from "node:sqlite";
import { docCaiDat, ghiCaiDat, ghiNgoaiBat, ngoaiBat } from "./cai-dat-tro-ly";

const moi = () => {
  const db = new DatabaseSync(":memory:");
  db.exec("CREATE TABLE cai_dat (khoa TEXT PRIMARY KEY, gia_tri TEXT)");
  return db;
};

// 1. mặc định bật đủ sáu tác tử
{
  const db = moi();
  assert.deepEqual(docCaiDat(db, 1).batTacTu.sort(), ["chu_de_can_ban", "dieu_phoi", "doi_chieu", "doi_chieu_thuoc", "tim_kiem", "tra_loi"]);
}

// 2. ghi rồi đọc đúng, theo từng người dùng; giá trị rác bị bỏ
{
  const db = moi();
  ghiCaiDat(db, 1, ["tim_kiem", "hack" as any, "chu_de_can_ban", 5 as any, "tim_kiem"]);
  assert.deepEqual(docCaiDat(db, 1).batTacTu, ["tim_kiem", "chu_de_can_ban"]);
  assert.equal(docCaiDat(db, 2).batTacTu.length, 6, "người khác vẫn mặc định");
  ghiCaiDat(db, 1, []);
  assert.deepEqual(docCaiDat(db, 1).batTacTu, [], "tắt hết là hợp lệ");
}

// 3. dữ liệu hỏng trong bảng: về mặc định, không lỗi
{
  const db = moi();
  db.prepare("INSERT INTO cai_dat (khoa, gia_tri) VALUES ('tro_ly:1', 'không phải JSON')").run();
  assert.equal(docCaiDat(db, 1).batTacTu.length, 6);
}

// 4. công tắc ngoài: mặc định bật; env "tat" hoặc ghi false thì tắt
{
  const db = moi();
  assert.equal(ngoaiBat(db, {}), true);
  assert.equal(ngoaiBat(db, { MEDITRACE_TRO_LY_NGOAI: "tat" }), false);
  ghiNgoaiBat(db, false);
  assert.equal(ngoaiBat(db, {}), false);
  ghiNgoaiBat(db, true);
  assert.equal(ngoaiBat(db, {}), true);
  assert.equal(ngoaiBat(db, { MEDITRACE_TRO_LY_NGOAI: "tat" }), false, "env thắng công tắc bật");
}

console.log("cai-dat-tro-ly.test.ts: tất cả đều qua");
