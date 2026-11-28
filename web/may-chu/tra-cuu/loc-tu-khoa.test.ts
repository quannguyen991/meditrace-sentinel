import assert from "node:assert/strict";
import test from "node:test";
import { locTuKhoaCoDanhTinh } from "./dich-vu-tra-cuu";

test("bo_tu_khoa_mang_ten_hoac_so_truoc_khi_gui_ra_nguon_tai_lieu", () => {
  const { tuKhoa, boDi } = locTuKhoaCoDanhTinh({
    pubmed: "chest pain Nguyễn Văn An",
    medlineplus: "asthma",
    benh_en: "asthma",
    tieng_viet: "hen phế quản",
    thuoc: ["warfarin", "0912345678"],
  });
  assert.equal(tuKhoa.pubmed, "");
  assert.equal(tuKhoa.medlineplus, "asthma");
  assert.equal(tuKhoa.tieng_viet, "hen phế quản");
  assert.deepEqual(tuKhoa.thuoc, ["warfarin"]);
  assert.equal(boDi, 2);
});
