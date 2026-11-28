import assert from "node:assert/strict";
import test from "node:test";
import { kiemVaBatMoHinhNgoai } from "./moHinhNgoai";

function giaFetch(trangThai: object, batTraVe?: { status: number; body: object }) {
  const goiDen: string[] = [];
  const goi = (async (url: string) => {
    goiDen.push(String(url));
    if (String(url).endsWith("/api/external/status")) return new Response(JSON.stringify(trangThai));
    const b = batTraVe || { status: 200, body: { ngoaiBat: true } };
    return new Response(JSON.stringify(b.body), { status: b.status });
  }) as typeof fetch;
  return { goi, goiDen };
}

test("chua_co_khoa_thi_khong_bat_va_khong_goi_ghi", async () => {
  const { goi, goiDen } = giaFetch({ configured: false, enabled: false });
  const kq = await kiemVaBatMoHinhNgoai(() => true, goi);
  assert.equal(kq.duoc, false);
  assert.deepEqual(goiDen, ["/api/external/status"]);
});

test("may_chu_da_bat_thi_bat_ngay_khong_hoi", async () => {
  let hoi = 0;
  const { goi } = giaFetch({ configured: true, enabled: true, reachable: true });
  const kq = await kiemVaBatMoHinhNgoai(() => (hoi++, true), goi);
  assert.equal(kq.duoc, true);
  assert.equal(hoi, 0);
});

test("quan_tri_xac_nhan_thi_bat_may_chu", async () => {
  const { goi, goiDen } = giaFetch({ configured: true, enabled: false, reachable: true });
  const kq = await kiemVaBatMoHinhNgoai(() => true, goi);
  assert.equal(kq.duoc, true);
  assert.ok(goiDen.includes("/api/tro-ly/cai-dat/ngoai"));
});

test("tu_choi_xac_nhan_thi_giu_tat", async () => {
  const { goi, goiDen } = giaFetch({ configured: true, enabled: false });
  const kq = await kiemVaBatMoHinhNgoai(() => false, goi);
  assert.equal(kq.duoc, false);
  assert.ok(!goiDen.includes("/api/tro-ly/cai-dat/ngoai"));
});

test("bac_si_thuong_bi_403_thi_bao_nho_quan_tri", async () => {
  const { goi } = giaFetch({ configured: true, enabled: false }, { status: 403, body: { error: "x" } });
  const kq = await kiemVaBatMoHinhNgoai(() => true, goi);
  assert.equal(kq.duoc, false);
  assert.match((kq as { lyDo: string }).lyDo, /quản trị/);
});

test("bien_moi_truong_khoa_tat_thi_bao_ro", async () => {
  const { goi } = giaFetch({ configured: true, enabled: false }, { status: 200, body: { ngoaiBat: false } });
  const kq = await kiemVaBatMoHinhNgoai(() => true, goi);
  assert.equal(kq.duoc, false);
  assert.match((kq as { lyDo: string }).lyDo, /MEDITRACE_TRO_LY_NGOAI/);
});
