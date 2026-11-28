/**
 * Hỗ trợ kiểm thử chốt "đã ký duyệt mới được xuất": dựng ca khám đủ điều kiện ký, lưu vào `ca_kham`
 * và ký giống hệt POST /api/sessions/:id/sign-off (dòng WORM + bản chụp ký do máy chủ ghi).
 * Chỉ dùng trong tệp *.test.ts — import SAU khi đã đặt MEDITRACE_DB / MEDITRACE_WORM_KEY.
 */
import { khoaDuyetCuaNote, tinhKyDuyetTuCa } from "../src/lib/kyDuyet";
import { docMotCaKham, ghiMotCaKham, khoWorm } from "./csdl";
import { ghiBanKyDuyet } from "./kiem-ky-may-chu";

export const NHAP_MAU = [
  "LÝ DO KHÁM BỆNH",
  "đau ngực [T1]",
  "",
  "CHẨN ĐOÁN: Rối loạn mỡ máu / Tăng huyết áp",
  "",
  "ĐƠN THUỐC",
  "- Atorvastatin 20mg uống 1 viên buổi tối",
  "- Furosemide 40mg",
  "",
  "CẦN XÁC NHẬN",
  "sốt? [T2]",
].join("\n");
export const SOAP_MAU = "S: đau ngực\nA: Tăng huyết áp";

export interface TuyChonCaMau {
  noiDung?: string;
  soap?: string;
  ten?: string;
  phuDe?: string;
  nguCanh?: string;
  transcript?: string;
  /** Lời thoại cấp ca (`Session.transcript`), mặc định "BS: chào". */
  transcriptCa?: string;
  /** Mệnh đề tuỳ chọn; khi đặt thì mặc định mọi mệnh đề "giu". */
  menhDe?: Array<Record<string, unknown>>;
  quyet?: Record<number, string>;
  banSua?: Record<number, string>;
  segments?: Array<{ luot: number; start_s: number; end_s: number }>;
  signOffTabId?: string;
}

/** Ca khám mẫu đã duyệt hết mệnh đề (đủ điều kiện ký): mệnh đề 1 giữ, mệnh đề 2 sửa, mệnh đề 3 bỏ. */
export function caMauDuDieuKienKy(id: string, noiDungHoacTuyChon: string | TuyChonCaMau = {}) {
  const tc: TuyChonCaMau = typeof noiDungHoacTuyChon === "string" ? { noiDung: noiDungHoacTuyChon } : noiDungHoacTuyChon;
  const noiDung = tc.noiDung ?? NHAP_MAU;
  const note = {
    caseId: "py_mau",
    content: noiDung,
    transcript: tc.transcript ?? "BS: Anh đau ngực từ hôm qua?\nBN: Có, hơi sốt.\nBS: Kê Atorvastatin.",
    propositions: tc.menhDe ?? [
      { id: 1, text: "đau ngực", status: "than", section: "LÝ DO KHÁM BỆNH", evidenceTurns: [1] },
      { id: 2, text: "sốt?", status: "can_xac_nhan", section: "CẦN XÁC NHẬN", evidenceTurns: [2] },
      { id: 3, text: "Atorvastatin 20mg tối", status: "than", section: "ĐƠN THUỐC", drug: "Atorvastatin", evidenceTurns: [3] },
    ],
  };
  return {
    id,
    patientIdentifier: tc.ten ?? "BN thử",
    patientSubtitle: tc.phuDe ?? "Nam, 4 tuổi, 15 kg",
    transcript: tc.transcriptCa ?? "BS: chào",
    ...(tc.segments ? { transcriptSegments: tc.segments } : {}),
    activeTabId: "tab-doc",
    tabs: [
      { id: "tab-transcript", title: "Lời thoại", type: "transcript", content: "BS: chào" },
      { id: "tab-context", title: "Ngữ cảnh", type: "context", content: tc.nguCanh ?? "Creatinine 80 umol/L" },
      { id: "tab-soap", title: "Bệnh án SOAP", type: "soap", content: tc.soap ?? SOAP_MAU },
      { id: "tab-doc", title: "Bản nháp hồ sơ", type: "custom", content: noiDung },
    ],
    note,
    duyet: {
      khoa: khoaDuyetCuaNote(note),
      quyet:
        tc.quyet ??
        (tc.menhDe ? Object.fromEntries(tc.menhDe.map((p) => [Number(p.id), "giu"])) : { 1: "giu", 2: "sua", 3: "bo" }),
      banSua: tc.banSua ?? (tc.menhDe ? {} : { 2: "không sốt" }),
    },
    ...(tc.signOffTabId ? { signOff: { tabId: tc.signOffTabId } } : {}),
  };
}

export function luuCaMau(uid: number, ca: { id: string }) {
  ghiMotCaKham(uid, ca.id, ca as unknown as Record<string, unknown>, {});
}

/** Ký WORM cho ca đã lưu (tab `tabId` hoặc tab mặc định), băm tính từ `ca_kham.du_lieu` như route ký duyệt. */
export function kyCaMau(uid: number, id: string, tabId: string | null = null) {
  const ca = docMotCaKham(uid, id);
  if (!ca) throw new Error(`Chưa lưu ca ${id}`);
  const kq = tinhKyDuyetTuCa(ca.duLieu, tabId);
  if (!kq.kiemTra.duDieuKien) throw new Error(`Ca ${id} chưa đủ điều kiện ký`);
  const ketQua = khoWorm.ghiSignOff({
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
  ghiBanKyDuyet({ uid, sessionId: id, wormSeq: ketQua.wormSeq, tabId: kq.tabId, contentHash: kq.contentHash, duLieu: ca.duLieu });
  return ketQua;
}

/** Lưu + ký; sau đó (tuỳ chọn) lưu bản sửa nội dung tab đã ký để mô phỏng "sửa sau khi ký". */
export function taoCaDaKy(uid: number, id: string, opts: { suaSauKy?: boolean } & TuyChonCaMau = {}) {
  const { suaSauKy, ...tc } = opts;
  luuCaMau(uid, caMauDuDieuKienKy(id, tc));
  kyCaMau(uid, id);
  if (suaSauKy) luuCaMau(uid, caMauDuDieuKienKy(id, { ...tc, noiDung: `${tc.noiDung ?? NHAP_MAU}\nthêm dòng sau khi ký` }));
}
