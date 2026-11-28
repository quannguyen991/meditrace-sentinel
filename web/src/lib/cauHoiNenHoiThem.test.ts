import { test } from "node:test";
import assert from "node:assert/strict";
import { laCauHoiNenHoiThem, locGoiYBamLoiThoai, soanCauNenHoiThem } from "./cauHoiNenHoiThem";

test("nhận ra câu hỏi 'nên hỏi thêm'", () => {
  assert.equal(laCauHoiNenHoiThem("Nên hỏi thêm bệnh nhân những gì?"), true);
  assert.equal(laCauHoiNenHoiThem("cần hỏi gì nữa"), true);
  assert.equal(laCauHoiNenHoiThem("Liều amoxicillin cho trẻ 20 kg?"), false);
});

test("dùng câu làm rõ, gợi ý có lượt dẫn và mục còn thiếu của đúng ca", () => {
  const kq = soanCauNenHoiThem({
    cauHoiLamRo: ["Nôn hai lần là của bệnh nhân hay người nhà ạ?"],
    goiYSocrates: [{ cau_hoi_goi_y: "Sốt có kèm rét run không?", luot_dan: [2], trich_dan: "sốt cao 4 ngày" }],
    menhDe: [{ section: "LÝ DO KHÁM BỆNH" }, { section: "BỆNH SỬ HIỆN TẠI" }, { section: "DỊ ỨNG" }],
  });
  assert.equal(kq.soCau, 2);
  assert.match(kq.noiDung, /Nôn hai lần/);
  assert.match(kq.noiDung, /T2 · “sốt cao 4 ngày”/);
  assert.match(kq.noiDung, /Thuốc đang dùng/);
  assert.doesNotMatch(kq.noiDung, /Lý do khám,/);
});

test("bỏ gợi ý cũ không có căn cứ và gợi ý có căn cứ không thuộc lời thoại ca đang mở", () => {
  const loiThoai = "Bác sĩ: Anh bị sao?\nBệnh nhân: Tôi sốt cao 4 ngày, người mệt.";
  const ds = [
    { cau_hoi_goi_y: "Ho khan hay có đờm?" }, // bộ cũ, không có căn cứ
    { cau_hoi_goi_y: "Đờm màu gì?", trich_dan: "ho ba hôm nay" }, // căn cứ của ca khác
    { cau_hoi_goi_y: "Rét run không?", trich_dan: "Tôi sốt cao 4 ngày" },
    { cau_hoi_goi_y: "Có thai không?", trich_dan: "Hồ sơ: nữ, 30 tuổi", nguon: "hồ sơ" },
  ];
  const giu = locGoiYBamLoiThoai(ds, loiThoai).map((g) => g.cau_hoi_goi_y);
  assert.deepEqual(giu, ["Rét run không?", "Có thai không?"]);
});

test("ca chưa có bản nháp thì nói rõ", () => {
  assert.match(soanCauNenHoiThem({}).noiDung, /chưa có bản nháp/);
});
