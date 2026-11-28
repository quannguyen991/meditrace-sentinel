import assert from "node:assert/strict";
import test from "node:test";
import { KHOA_GIU_LAI, laKhoaCanXoa, xoaDuLieuTrinhDuyet } from "./xoaDuLieuTrinhDuyet";

/** Storage giả đúng giao diện Web Storage (length/key/getItem/setItem/removeItem). */
function khoGia(ban: Record<string, string>) {
  const m = new Map(Object.entries(ban));
  return {
    m,
    get length() {
      return m.size;
    },
    key: (i: number) => [...m.keys()][i] ?? null,
    getItem: (k: string) => m.get(k) ?? null,
    setItem: (k: string, v: string) => void m.set(k, String(v)),
    removeItem: (k: string) => void m.delete(k),
    clear: () => m.clear(),
  };
}

const CA = '[{"id":"s1","patientIdentifier":"Nguyễn Văn A","transcript":"BS: chào bác"}]';

test("xoá mọi khoá meditrace_ chứa ca khám / lời thoại, giữ tuỳ chọn giao diện và khoá ngoài MediTrace", () => {
  const kho = khoGia({
    meditrace_sessions: CA,
    meditrace_sessions_luc: "123",
    meditrace_ca_dang_mo: "s1",
    "meditrace_kho_ca-kham": CA,
    "meditrace_kho_ca-kham_luc": "1",
    "meditrace_kho_benh-nhan": CA,
    "meditrace_kho_nhiem-vu": "[]",
    "meditrace_kho_tra-cuu": "[]",
    "meditrace_kho_mau-van-ban": "[]",
    "meditrace_kho_mau-benh-an-tuy-chinh": "[]",
    meditrace_doctor_voiceprint_v1: "{}",
    meditrace_cho_phep_ngoai: "1",
    meditrace_chu: "42",
    meditrace_khoa_moi_chua_biet: "x",
    meditrace_taskbar_position: "left",
    "mt-khac": "giu",
  });
  const daXoa = xoaDuLieuTrinhDuyet(kho);
  assert.deepEqual([...kho.m.keys()].sort(), ["meditrace_taskbar_position", "mt-khac"]);
  assert.ok(daXoa.includes("meditrace_sessions"));
  assert.ok(daXoa.includes("meditrace_kho_benh-nhan"));
  assert.ok(!daXoa.includes("meditrace_taskbar_position"));
});

test("chạy được với Storage giả không có length/key (dùng Object.keys)", () => {
  const m = new Map<string, string>([["meditrace_sessions", CA]]);
  const kho: any = {
    getItem: (k: string) => m.get(k) ?? null,
    removeItem: (k: string) => m.delete(k),
  };
  Object.defineProperty(kho, "meditrace_kho_tra-cuu", { value: "[]", enumerable: true, configurable: true });
  Object.defineProperty(kho, "meditrace_taskbar_position", { value: "left", enumerable: true, configurable: true });
  const daXoa = xoaDuLieuTrinhDuyet(kho);
  assert.equal(m.has("meditrace_sessions"), false); // khoá đã biết luôn bị xoá dù không liệt kê được
  assert.ok(daXoa.includes("meditrace_kho_tra-cuu"));
  assert.ok(!daXoa.includes("meditrace_taskbar_position"));
});

test("không có Storage hoặc Storage ném lỗi thì không vỡ", () => {
  assert.deepEqual(xoaDuLieuTrinhDuyet(undefined), []);
  const hong = {
    get length(): number {
      throw new Error("SecurityError");
    },
    key: () => null,
    getItem: () => null,
    removeItem: () => {
      throw new Error("SecurityError");
    },
  };
  assert.doesNotThrow(() => xoaDuLieuTrinhDuyet(hong));
});

test("laKhoaCanXoa: chỉ khoá meditrace_ ngoài danh sách giữ lại", () => {
  assert.equal(laKhoaCanXoa("meditrace_sessions"), true);
  assert.equal(laKhoaCanXoa("meditrace_taskbar_position"), false);
  assert.equal(laKhoaCanXoa("theme"), false);
  assert.deepEqual([...KHOA_GIU_LAI], ["meditrace_taskbar_position"]);
});
