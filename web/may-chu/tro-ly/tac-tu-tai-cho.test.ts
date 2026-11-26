/**
 * Kiểm hai tác tử luật tại chỗ. Chạy: npx tsx may-chu/tro-ly/tac-tu-tai-cho.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import { CHU_DE, chuDeCanBan, doiChieuThuocDiUng } from "./tac-tu-tai-cho";

// 1. bảy chủ đề, mã đúng như thiết kế
assert.deepEqual(
  CHU_DE.map((c) => c.ma),
  ["ly_do", "benh_su", "tien_su", "thuoc", "di_ung", "gia_dinh", "kham"],
);

// 2. ca chỉ có lý do + khám: năm chủ đề chưa bàn
{
  const r = chuDeCanBan([
    { text: "đau đầu", section: "LÝ DO KHÁM BỆNH" },
    { text: "huyết áp 120/80", section: "KHÁM LÂM SÀNG" },
  ]);
  assert.deepEqual(r.daBan.map((c) => c.ma).sort(), ["kham", "ly_do"]);
  assert.deepEqual(r.chuaBan.map((c) => c.ma).sort(), ["benh_su", "di_ung", "gia_dinh", "thuoc", "tien_su"]);
  assert.equal(r.daBan.find((c) => c.ma === "kham")?.soMenhDe, 1);
}

// 3. ca đủ mục: chưa bàn rỗng
{
  const r = chuDeCanBan(CHU_DE.map((c) => ({ text: "x", section: c.mucLienQuan[0] })));
  assert.equal(r.chuaBan.length, 0);
  assert.equal(r.daBan.length, 7);
}

// 4. thuốc cùng tên hai liều khác nhau -> một dòng mâu thuẫn
{
  const r = doiChieuThuocDiUng([
    { text: "a", section: "THUỐC ĐANG DÙNG", drug: "amoxicillin 500 mg" },
    { text: "b", section: "THUỐC ĐANG DÙNG", drug: "amoxicillin 250 mg" },
  ]);
  assert.equal(r.mauThuan.length, 1);
  assert.ok(r.mauThuan[0].toLowerCase().includes("amoxicillin"));
  assert.deepEqual(r.thuoc.length, 2);
}

// 5. thuốc trùng chất dị ứng (không phân biệt hoa thường) -> một dòng mâu thuẫn
{
  const r = doiChieuThuocDiUng([
    { text: "dị ứng penicillin", section: "DỊ ỨNG" },
    { text: "x", section: "THUỐC ĐANG DÙNG", drug: "Penicillin V 500 mg" },
  ]);
  assert.equal(r.mauThuan.length, 1);
  assert.deepEqual(r.thieu, []);
}

// 6. "không dị ứng" không vào danh sách dị ứng
{
  const r = doiChieuThuocDiUng([
    { text: "không dị ứng thuốc", section: "DỊ ỨNG", negated: true },
    { text: "x", section: "THUỐC ĐANG DÙNG", drug: "paracetamol 500 mg" },
  ]);
  assert.deepEqual(r.diUng, []);
  assert.deepEqual(r.mauThuan, []);
}

// 7. danh sách rỗng: không lỗi, thiếu cả hai
{
  const r = doiChieuThuocDiUng([]);
  assert.deepEqual(r.thieu, ["chưa có mục dị ứng", "chưa có thuốc đang dùng"]);
  assert.deepEqual(chuDeCanBan([]).daBan, []);
}

// 8. cùng thuốc cùng liều viết hoa khác nhau không bị coi là mâu thuẫn
{
  const r = doiChieuThuocDiUng([
    { text: "a", section: "THUỐC ĐANG DÙNG", drug: "Amoxicillin 500 mg" },
    { text: "b", section: "THUỐC ĐANG DÙNG", drug: "amoxicillin 500 mg" },
  ]);
  assert.deepEqual(r.mauThuan, []);
}

// 9. thuốc đã ngừng/phủ định không tính là đang dùng
{
  const r = doiChieuThuocDiUng([
    { text: "không dùng amoxicillin", section: "THUỐC ĐANG DÙNG", drug: "amoxicillin 500 mg", negated: true },
    { text: "dị ứng amoxicillin", section: "DỊ ỨNG" },
  ]);
  assert.deepEqual(r.thuoc, []);
  assert.deepEqual(r.mauThuan, []);
}

// 10. Vá P0: mệnh đề DỊ ỨNG có gắn trường drug KHÔNG tự mâu thuẫn với chính nó
{
  const r = doiChieuThuocDiUng([
    { text: "sốc phản vệ độ 3 với penicillin", section: "DỊ ỨNG", drug: "penicillin" },
    { text: "đang uống amlodipin 5 mg", section: "THUỐC ĐANG DÙNG", drug: "amlodipin 5 mg" },
  ]);
  assert.deepEqual(r.thuoc, ["amlodipin 5 mg"]);
  assert.deepEqual(r.diUng, ["sốc phản vệ độ 3 với penicillin"]);
  assert.deepEqual(r.mauThuan, [], "mục DỊ ỨNG có trường drug không được tính vào danh sách thuốc đang dùng");
  assert.deepEqual(r.thieu, []);
}

// 11. Vá P0: thuốc trong KẾ HOẠCH ĐIỀU TRỊ trùng chất ở mục DỊ ỨNG (kể cả khi text chỉ ghi phản ứng) vẫn phát hiện đúng
{
  const r = doiChieuThuocDiUng([
    { text: "sốc phản vệ nặng", section: "DỊ ỨNG", drug: "ceftriaxone" },
    { text: "kê ceftriaxone 1 g tiêm tĩnh mạch", section: "KẾ HOẠCH ĐIỀU TRỊ", drug: "ceftriaxone 1 g" },
    { text: "năm ngoái từng dùng ibuprofen", section: "TIỀN SỬ BỆNH", drug: "ibuprofen 400 mg" },
  ]);
  assert.deepEqual(r.thuoc, ["ceftriaxone 1 g"], "chỉ gom thuốc từ mục thuốc/điều trị, không gom TIỀN SỬ BỆNH");
  assert.deepEqual(r.diUng, ["sốc phản vệ nặng (ceftriaxone)"]);
  assert.equal(r.mauThuan.length, 1);
  assert.ok(r.mauThuan[0].includes("ceftriaxone"));
}

// 12. Tương thích định dạng thực tế của menhDeChoGiaoDien ("ten ..., lieu ..., trang_thai_dung ..."):
// bắt đúng dị ứng + khác liều và loại trừ thuốc đã ngừng (trang_thai_dung đã ngừng)
{
  const r = doiChieuThuocDiUng([
    { text: "dị ứng penicillin", section: "DỊ ỨNG", drug: "ten penicillin" },
    {
      text: "đang uống Penicillin V",
      section: "THUỐC ĐANG DÙNG",
      drug: "ten Penicillin V, lieu 500 mg, so_lan 2 lần/ngày, trang_thai_dung đang dùng",
    },
    {
      text: "từng uống amoxicillin nhưng đã ngừng",
      section: "THUỐC ĐANG DÙNG",
      drug: "ten amoxicillin, lieu 500 mg, trang_thai_dung đã ngừng",
    },
    {
      text: "amlodipin sáng",
      section: "THUỐC ĐANG DÙNG",
      drug: "ten amlodipin, lieu 5 mg, trang_thai_dung đang dùng",
    },
    {
      text: "amlodipin tối",
      section: "KẾ HOẠCH ĐIỀU TRỊ",
      drug: "ten amlodipin, lieu 10 mg, trang_thai_dung được kê, chưa dùng",
    },
  ]);
  assert.equal(r.thuoc.length, 3, "thuốc đã ngừng không đưa vào danh sách thuốc đang dùng");
  assert.ok(r.mauThuan.some((m) => m.includes("penicillin v") && m.includes("dị ứng")));
  assert.ok(r.mauThuan.some((m) => m.includes("amlodipin") && m.includes("2 liều khác nhau")));
}

console.log("tac-tu-tai-cho.test.ts: tất cả đều qua");
