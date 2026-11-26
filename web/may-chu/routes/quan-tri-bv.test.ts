import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import express from "express";

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-quantribv-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "quantribv.db");
process.env.MEDITRACE_WORM_KEY = "khoa-worm-kiem-thu-quan-tri-bv-32b";
process.env.MEDITRACE_INTERNAL_TOKEN = "test-internal-token";
process.env.MEDITRACE_API = "http://127.0.0.1:19999";

const { db, khoWorm } = await import("../csdl");
const { taoRouterQuanTriBv } = await import("./quan-tri-bv");

let base = "";
let server: http.Server;
let currentRole: "quan_tri" | "bac_si" | null = "quan_tri";
let currentUid = 1;

test.before(async () => {
  const now = Date.now();
  db.prepare(
    "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (1, 'admin@bv.vn', 'BS. Quản Trị KHTH', 'h', 'quan_tri', ?)",
  ).run(now);
  db.prepare(
    "INSERT OR IGNORE INTO nguoi_dung (id, email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (2, 'bs2@bv.vn', 'BS. Trần Nội Khoa', 'h', 'bac_si', ?)",
  ).run(now);

  const ca1 = {
    id: "ca_bv_1",
    patientName: "Nguyễn Văn Bệnh Nhân Bí Mật",
    propositions: [
      { chu_the_id: 0, phu_dinh: false, thuoc: { ten: "Amoxicillin 500mg" } },
      { chu_the_id: 0, phu_dinh: false, thuoc: { ten: "Meropenem 1g" } },
    ],
    bhyt_icd10: {
      canh_bao_xuat_toan_bhyt: [{ thuoc: "Meropenem", ly_do: "Thiếu ICD nhiễm khuẩn", nguy_co_xuat_toan: 450000 }],
      bien_luan_chi_dinh_cls: [{ dich_vu: "MRI sọ não", hop_le: false }],
    },
    warnings: [{ code: "DDI_01", group: "ddi", title: "Tương tác thuốc" }],
  };

  const ca2 = {
    id: "ca_bv_2",
    patientName: "Lê Thị PHI Cần Che",
    propositions: [{ chu_the_id: 0, phu_dinh: false, thuoc: { ten: "Colistin 1M IU" } }],
    allergyWarnings: [{ thuoc: "Penicillin" }],
  };

  db.prepare(
    "INSERT INTO ca_kham (nguoi_dung_id, id, thu_tu, ten_benh_nhan, ngay_kham, du_lieu, tao_luc, cap_nhat_luc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
  ).run(1, "ca_bv_1", 0, "Nguyễn Văn Bệnh Nhân Bí Mật", "2026-11-26", JSON.stringify(ca1), now, now);

  db.prepare(
    "INSERT INTO ca_kham (nguoi_dung_id, id, thu_tu, ten_benh_nhan, ngay_kham, du_lieu, tao_luc, cap_nhat_luc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
  ).run(2, "ca_bv_2", 0, "Lê Thị PHI Cần Che", "2026-11-26", JSON.stringify(ca2), now, now);

  khoWorm.ghiSignOff({
    sessionId: "ca_bv_1",
    userId: 1,
    tongMenhDe: 2,
    soGiu: 2,
    soSua: 0,
    soBo: 0,
    tyLeCoNguon: 1,
    contentHash: "hash_ca_bv_1",
    soChuaXacNhan: 0,
  });

  const app = express();
  app.use(express.json());
  app.use((req, _res, next) => {
    if (currentRole) {
      req.nguoiDung = { id: currentUid, email: "u@bv.vn", hoTen: "User", vai: currentRole } as any;
    }
    next();
  });
  app.use(taoRouterQuanTriBv({ db }));
  server = http.createServer(app);
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${(server.address() as { port: number }).port}`;
});

test.after(() => {
  server?.close();
  if (db.isOpen) db.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("chặn 401 khi chưa đăng nhập", async () => {
  currentRole = null;
  const r1 = await fetch(`${base}/api/quan-tri-bv/tong-quan`);
  assert.equal(r1.status, 401);

  const r2 = await fetch(`${base}/api/quan-tri-bv/kiem-toan-xml`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ xml_files: {} }),
  });
  assert.equal(r2.status, 401);
});

test("tong-quan cho quan_tri: tổng hợp KPI, AWaRe, WORM, không lộ PHI bệnh nhân", async () => {
  currentRole = "quan_tri";
  currentUid = 1;
  const r = await fetch(`${base}/api/quan-tri-bv/tong-quan`);
  assert.equal(r.status, 200);
  const rawText = await r.text();
  assert.equal(rawText.includes("Nguyễn Văn Bệnh Nhân Bí Mật"), false);
  assert.equal(rawText.includes("Lê Thị PHI Cần Che"), false);

  const data = JSON.parse(rawText);
  assert.equal(data.phamVi, "toan_vien");
  assert.equal(data.tongCaKham, 2);
  assert.equal(data.tongCaDaKyWorm, 1);
  assert.equal(data.tyLeHoanThienHoSo, 50);
  assert.equal(data.tongNguyCoXuatToanVnd, 950_000);
  assert.equal(data.soCanhBaoDdiVaDiUng, 2);
  assert.equal(data.tyLeKhangSinhAWaRe.access, 1);
  assert.equal(data.tyLeKhangSinhAWaRe.watch, 1);
  assert.equal(data.tyLeKhangSinhAWaRe.reserve, 1);
  assert.equal(data.ketQuaKiemDinhWorm.hopLe, true);
  assert.equal(data.theoBacSi.length, 2);
});

test("tong-quan cho bac_si: chỉ thấy thống kê của chính mình trong theoBacSi", async () => {
  currentRole = "bac_si";
  currentUid = 2;
  const r = await fetch(`${base}/api/quan-tri-bv/tong-quan`);
  assert.equal(r.status, 200);
  const data = await r.json();
  assert.equal(data.phamVi, "ca_nhan");
  assert.equal(data.theoBacSi.length, 1);
  assert.equal(data.theoBacSi[0].bacSiId, 2);
});

test("POST /api/quan-tri-bv/kiem-toan-xml fallback sang Python CLI --audit", async () => {
  currentRole = "bac_si";
  currentUid = 2;
  const xml1 = `<TONG_HOP>
    <MA_LK>LK_TEST</MA_LK><MA_BN>BN1</MA_BN><MA_THE>DN4790123456789</MA_THE>
    <MA_DKBD>79001</MA_DKBD><MA_LOAI_KCB>1</MA_LOAI_KCB><MA_BENH>I10</MA_BENH>
    <NGAY_VAO>202611260800</NGAY_VAO><NGAY_RA>202611260900</NGAY_RA><MA_BAC_SI>BS01</MA_BAC_SI>
    <T_TONGCHI>500000</T_TONGCHI><T_BHTT>400000</T_BHTT><T_BNTT>100000</T_BNTT>
    <T_BNCCT>0</T_BNCCT><T_NGUONKHAC>0</T_NGUONKHAC>
  </TONG_HOP>`;
  const xml2 = `<CHITIEU_CHITIET_THUOC><DSACH_CHI_TIET_THUOC>
    <CHI_TIET_THUOC><STT>1</STT><TEN_THUOC>Meropenem 1g</TEN_THUOC><THANH_TIEN>450000</THANH_TIEN></CHI_TIET_THUOC>
  </DSACH_CHI_TIET_THUOC></CHITIEU_CHITIET_THUOC>`;

  const r = await fetch(`${base}/api/quan-tri-bv/kiem-toan-xml`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ xml_files: { XML1: xml1, XML2: xml2 } }),
  });
  assert.equal(r.status, 200);
  const data = await r.json();
  assert.equal(data.hop_le, false);
  assert.equal(data.tong_nguy_co_xuat_toan, 450000);
  assert.equal(data.vi_pham_tt20.length, 1);
  assert.equal(data.vi_pham_tt20[0].nhom, "khang_sinh_han_che");
});
