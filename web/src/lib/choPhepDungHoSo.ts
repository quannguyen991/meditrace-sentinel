/**
 * Chốt "bác sĩ phê duyệt trước khi dùng hồ sơ" (Đề cải tiến 1, 28/11/2026).
 *
 * Xem bản nháp thì luôn được. Đưa hồ sơ RA KHỎI phần mềm (chép, in, tải tệp, chép sang HIS,
 * phiếu SBAR, tờ dặn dò) chỉ được khi bác sĩ đã ký và chưa sửa gì sau lần ký.
 */
export const LY_DO_CHUA_KY = "Bác sĩ chưa ký duyệt — hồ sơ chỉ được xem, chưa được chép, in hay xuất.";
export const LY_DO_SUA_SAU_KY = "Hồ sơ đã sửa sau lần ký — cần ký lại trước khi chép, in hay xuất.";
/** Dòng tự hiện ở đầu bản in khi chưa được phép (không chặn được phím in của trình duyệt). */
export const NHAN_BAN_NHAP = "BẢN NHÁP — CHƯA KÝ DUYỆT";

export function choPhepDungHoSo(t: { daKy: boolean; daSuaSauKy: boolean }): { duoc: boolean; lyDo: string | null } {
  if (!t.daKy) return { duoc: false, lyDo: LY_DO_CHUA_KY };
  if (t.daSuaSauKy) return { duoc: false, lyDo: LY_DO_SUA_SAU_KY };
  return { duoc: true, lyDo: null };
}

export function nhanInHoSo(duoc: boolean): string | null {
  return duoc ? null : NHAN_BAN_NHAP;
}
