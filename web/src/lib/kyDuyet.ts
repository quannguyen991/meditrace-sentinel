/**
 * Tính dữ liệu ký duyệt WORM từ MỘT ca khám đã lưu — dùng chung cho giao diện và máy chủ.
 * Máy chủ gọi hàm này trên `ca_kham.du_lieu` nên số liệu và băm nội dung không lấy từ trình duyệt.
 */
import type { DocumentTabItem } from "../types";
import {
  buildSignOffCanonicalPayload,
  kiemTraDieuKienKyDuyet,
  sha256HexSync,
  type KetQuaKiemTraKyDuyet,
  type MenhDeKiemTraKyDuyet,
  type QuyetDuyet,
} from "./compileEffectiveNote";

/** Băm ngắn (djb2) để làm khoá kết quả duyệt theo nội dung bản nháp. Không dùng cho bảo mật. */
export function bamChuoi(s: string) {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
  return (h >>> 0).toString(36);
}

/** Khoá gắn kết quả duyệt (giữ/sửa/bỏ) với đúng phiên bản bản nháp. */
export function khoaDuyetCuaNote(note: { caseId?: string | null; content: string }): string {
  return `${note.caseId || ""}#${note.content.length}#${bamChuoi(note.content)}`;
}

type TabToiThieu = Pick<DocumentTabItem, "id" | "type" | "title" | "content">;

function laTabBenhAn(t: TabToiThieu, noiDungNhap?: string | null): boolean {
  if (!t || typeof t !== "object") return false;
  if (t.type === "soap") return true;
  return t.type === "custom" && (t.title === "Bản nháp hồ sơ" || (Boolean(noiDungNhap) && t.content === noiDungNhap));
}

/**
 * Chọn tab bệnh án để băm ký duyệt, KHÔNG phụ thuộc tab đang mở:
 * - `tabIdUuTien` (tab đã ký, hoặc tab bác sĩ chọn ký) được dùng nếu nó là tab bệnh án;
 * - nếu không: bản nháp hồ sơ mới nhất, rồi tab SOAP đầu tiên, rồi nội dung bản nháp.
 */
export function chonTabBenhAnDeBam(
  tabs: TabToiThieu[] | null | undefined,
  noiDungNhap?: string | null,
  tabIdUuTien?: string | null,
): { tabId: string | null; noiDung: string } {
  const ds = Array.isArray(tabs) ? tabs.filter((t) => t && typeof t === "object") : [];
  if (tabIdUuTien) {
    const t = ds.find((x) => x.id === tabIdUuTien);
    if (t && laTabBenhAn(t, noiDungNhap)) return { tabId: t.id, noiDung: String(t.content || "") };
  }
  const banNhap = [...ds]
    .reverse()
    .find((t) => t.type === "custom" && laTabBenhAn(t, noiDungNhap));
  if (banNhap) return { tabId: banNhap.id, noiDung: String(banNhap.content || "") };
  const soap = ds.find((t) => t.type === "soap");
  if (soap) return { tabId: soap.id, noiDung: String(soap.content || "") };
  return { tabId: null, noiDung: String(noiDungNhap || "") };
}

export interface KetQuaTinhKyDuyet {
  tabId: string | null;
  soapRaw: string;
  quyet: Record<number, QuyetDuyet>;
  banSua: Record<number, string>;
  kiemTra: KetQuaKiemTraKyDuyet;
  tongMenhDe: number;
  soGiu: number;
  soSua: number;
  soBo: number;
  tyLeCoNguon: number;
  soChuaXacNhan: number;
  canonical: string;
  contentHash: string;
}

const laDoiTuong = (x: unknown): x is Record<string, any> => Boolean(x) && typeof x === "object" && !Array.isArray(x);

/** Tính toàn bộ số liệu ký duyệt từ dữ liệu ca (dạng `Session` đã lưu); dữ liệu hỏng thì không đủ điều kiện. */
export function tinhKyDuyetTuCa(caTho: unknown, tabIdUuTien?: string | null): KetQuaTinhKyDuyet {
  const ca = laDoiTuong(caTho) ? caTho : {};
  const note = laDoiTuong(ca.note) ? ca.note : null;
  const noiDungNhap = note && typeof note.content === "string" ? note.content : "";
  const ds: MenhDeKiemTraKyDuyet[] = (note && Array.isArray(note.propositions) ? note.propositions : [])
    .filter((p: any) => laDoiTuong(p) && Number.isFinite(Number(p.id)))
    .map((p: any) => ({
      id: Number(p.id),
      status: typeof p.status === "string" ? p.status : undefined,
      stateD: typeof p.stateD === "string" ? p.stateD : null,
      evidenceTurns: Array.isArray(p.evidenceTurns) ? p.evidenceTurns : [],
    }));

  // Quyết định duyệt chỉ có hiệu lực khi khoá khớp đúng bản nháp hiện tại (như giao diện đang làm).
  const duyet = laDoiTuong(ca.duyet) ? ca.duyet : null;
  const khoaHienTai = note ? khoaDuyetCuaNote({ caseId: note.caseId, content: noiDungNhap }) : "";
  const duyetHopLe = duyet && note && duyet.khoa === khoaHienTai ? duyet : null;
  const quyet: Record<number, QuyetDuyet> = {};
  const banSua: Record<number, string> = {};
  if (duyetHopLe && laDoiTuong(duyetHopLe.quyet)) {
    for (const [k, v] of Object.entries(duyetHopLe.quyet)) {
      if (v === "cho" || v === "giu" || v === "sua" || v === "bo") quyet[Number(k)] = v;
    }
  }
  if (duyetHopLe && laDoiTuong(duyetHopLe.banSua)) {
    for (const [k, v] of Object.entries(duyetHopLe.banSua)) if (typeof v === "string") banSua[Number(k)] = v;
  }

  const { tabId, noiDung } = chonTabBenhAnDeBam(ca.tabs, noiDungNhap, tabIdUuTien);
  const kiemTra = kiemTraDieuKienKyDuyet(ds, quyet, banSua);
  const soGiu = ds.filter((p) => quyet[p.id] === "giu").length;
  const soSua = ds.filter((p) => quyet[p.id] === "sua").length;
  const soBo = ds.filter((p) => quyet[p.id] === "bo").length;
  const conHieuLuc = ds.filter((p) => quyet[p.id] !== "bo");
  const coNguon = conHieuLuc.filter(
    (p) => (p.evidenceTurns?.length || 0) > 0 || (quyet[p.id] === "sua" && Boolean(banSua[p.id]?.trim())),
  ).length;
  const tyLeCoNguon = conHieuLuc.length ? Math.round((coNguon / conHieuLuc.length) * 100) : 0;
  const canonical = buildSignOffCanonicalPayload(noiDung, quyet, banSua);
  return {
    tabId,
    soapRaw: noiDung,
    quyet,
    banSua,
    kiemTra,
    tongMenhDe: ds.length,
    soGiu,
    soSua,
    soBo,
    tyLeCoNguon,
    soChuaXacNhan: kiemTra.soCanXacNhanChuaDuyet,
    canonical,
    contentHash: sha256HexSync(canonical),
  };
}
