/**
 * Hỗ trợ kiểm thử chốt "đã ký duyệt mới được xuất": dựng ca khám đủ điều kiện ký, lưu vào `ca_kham`
 * và ghi dòng ký WORM với băm do máy chủ tính (giống hệt POST /api/sessions/:id/sign-off).
 * Chỉ dùng trong tệp *.test.ts — import SAU khi đã đặt MEDITRACE_DB / MEDITRACE_WORM_KEY.
 */
import { khoaDuyetCuaNote, tinhKyDuyetTuCa } from "../src/lib/kyDuyet";
import { docMotCaKham, ghiMotCaKham, khoWorm } from "./csdl";

export const NHAP_MAU = "LÝ DO KHÁM BỆNH\nđau ngực [T1]\n\nCẦN XÁC NHẬN\nsốt? [T2]";

/** Ca khám mẫu đã duyệt hết mệnh đề (đủ điều kiện ký). `noiDung` khác NHAP_MAU = bản đã sửa sau ký. */
export function caMauDuDieuKienKy(id: string, noiDung = NHAP_MAU) {
  const note = {
    caseId: "py_mau",
    content: noiDung,
    propositions: [
      { id: 1, text: "đau ngực", status: "than", evidenceTurns: [1] },
      { id: 2, text: "sốt?", status: "can_xac_nhan", evidenceTurns: [2] },
    ],
  };
  return {
    id,
    patientIdentifier: "BN thử",
    activeTabId: "tab-doc",
    tabs: [
      { id: "tab-transcript", title: "Lời thoại", type: "transcript", content: "BS: chào" },
      { id: "tab-doc", title: "Bản nháp hồ sơ", type: "custom", content: noiDung },
    ],
    note,
    duyet: { khoa: khoaDuyetCuaNote(note), quyet: { 1: "giu", 2: "giu" }, banSua: {} },
  };
}

export function luuCaMau(uid: number, ca: { id: string }) {
  ghiMotCaKham(uid, ca.id, ca as unknown as Record<string, unknown>, {});
}

/** Ký WORM cho ca đã lưu, băm tính từ `ca_kham.du_lieu` như route ký duyệt. */
export function kyCaMau(uid: number, id: string) {
  const ca = docMotCaKham(uid, id);
  if (!ca) throw new Error(`Chưa lưu ca ${id}`);
  const kq = tinhKyDuyetTuCa(ca.duLieu);
  if (!kq.kiemTra.duDieuKien) throw new Error(`Ca ${id} chưa đủ điều kiện ký`);
  return khoWorm.ghiSignOff({
    sessionId: id,
    userId: uid,
    tongMenhDe: kq.tongMenhDe,
    soGiu: kq.soGiu,
    soSua: kq.soSua,
    soBo: kq.soBo,
    tyLeCoNguon: kq.tyLeCoNguon,
    contentHash: kq.contentHash,
    soChuaXacNhan: kq.soChuaXacNhan,
  });
}

/** Lưu + ký; sau đó (tuỳ chọn) lưu bản sửa để mô phỏng "sửa sau khi ký". */
export function taoCaDaKy(uid: number, id: string, opts: { suaSauKy?: boolean } = {}) {
  luuCaMau(uid, caMauDuDieuKienKy(id));
  kyCaMau(uid, id);
  if (opts.suaSauKy) luuCaMau(uid, caMauDuDieuKienKy(id, `${NHAP_MAU}\nthêm dòng sau khi ký`));
}
