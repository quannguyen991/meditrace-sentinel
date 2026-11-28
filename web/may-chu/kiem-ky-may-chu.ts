/**
 * Chốt "bác sĩ đã ký duyệt và chưa sửa sau khi ký" phía MÁY CHỦ, cho mọi đường đưa hồ sơ ra khỏi phần mềm
 * (cổng người bệnh/QR, gói XML 1–5 BHYT, FHIR...). Giao diện có khoá riêng (choPhepDungHoSo) nhưng không đủ:
 * gọi thẳng API thì phải bị chặn ở đây.
 *
 * "Đã ký" = có dòng ký WORM của đúng bác sĩ cho đúng ca VÀ băm nội dung hiện tại — tính lại từ `ca_kham.du_lieu`
 * bằng cùng hàm với route ký (tinhKyDuyetTuCa) — trùng băm đã ký. Không tin bất cứ số liệu nào trình duyệt gửi.
 */
import type express from "express";
import { tinhKyDuyetTuCa } from "../src/lib/kyDuyet";
import { docMotCaKham, khoWorm } from "./csdl";

export const LOI_CHUA_KY_DUYET = "Bác sĩ chưa ký duyệt hồ sơ này (hoặc đã sửa sau khi ký) — chưa được xuất.";
export const MA_LOI_CHUA_KY_DUYET = "chua_ky_duyet";

export function kiemDaKyChoXuat(uid: number, caseId: string): { duoc: boolean; lyDo?: string } {
  const id = typeof caseId === "string" ? caseId.trim() : "";
  if (!id) return { duoc: false, lyDo: "Thiếu mã ca khám để đối chiếu chữ ký." };
  if (typeof uid !== "number" || !Number.isFinite(uid)) return { duoc: false, lyDo: "Chưa đăng nhập." };

  const ca = docMotCaKham(uid, id);
  if (!ca) return { duoc: false, lyDo: "Không tìm thấy ca khám này trên máy chủ." };

  const dongKy = khoWorm.docLichSuSignOff(id, { userId: uid });
  if (!dongKy.length) return { duoc: false, lyDo: "Bác sĩ chưa ký duyệt ca này." };
  const bamDaKy = new Set(dongKy.map((d) => d.content_hash).filter(Boolean));

  // Băm lại đúng tab đã ký (ghi trong signOff.tabId của ca), và cả lựa chọn mặc định của route ký.
  const duLieu = ca.duLieu as { signOff?: { tabId?: unknown } } | null;
  const tabDaKy = typeof duLieu?.signOff?.tabId === "string" ? duLieu.signOff.tabId : null;
  const ungVien = new Set<string>([tinhKyDuyetTuCa(ca.duLieu).contentHash]);
  if (tabDaKy) ungVien.add(tinhKyDuyetTuCa(ca.duLieu, tabDaKy).contentHash);

  for (const bam of ungVien) if (bamDaKy.has(bam)) return { duoc: true };
  return { duoc: false, lyDo: "Hồ sơ đã sửa sau lần ký — cần ký lại." };
}

/** Lấy mã ca từ thân yêu cầu (ưu tiên `sessionId`, rồi `caseId`) hoặc query. */
export function layMaCaTuYeuCau(req: express.Request, ...truong: string[]): string {
  const body = req.body && typeof req.body === "object" ? (req.body as Record<string, unknown>) : {};
  for (const k of truong.length ? truong : ["sessionId", "caseId"]) {
    const v = body[k] ?? (req.query as Record<string, unknown>)[k];
    if (typeof v === "string" && v.trim()) return v.trim().slice(0, 200);
  }
  return "";
}

/**
 * Chặn yêu cầu xuất khi ca chưa ký / đã sửa sau ký: trả 409 và `true` (đã trả lời). Gọi ở đầu route xuất.
 */
export function chanNeuChuaKy(req: express.Request, res: express.Response, caseId: string): boolean {
  const uid = (req as express.Request & { nguoiDung?: { id?: number } }).nguoiDung?.id;
  const kq = kiemDaKyChoXuat(typeof uid === "number" ? uid : NaN, caseId);
  if (kq.duoc) return false;
  res.status(409).json({ error: LOI_CHUA_KY_DUYET, code: MA_LOI_CHUA_KY_DUYET, lyDo: kq.lyDo });
  return true;
}
