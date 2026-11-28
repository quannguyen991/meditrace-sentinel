/**
 * Xoá bản sao dữ liệu ca khám MediTrace trong Web Storage của trình duyệt.
 * Gọi khi đăng xuất, hết phiên (401) và khi người khác đăng nhập trên cùng máy (taiKhoan.ts).
 * Hàm thuần: nhận Storage làm tham số để kiểm thử bằng Storage giả.
 *
 * Xoá MỌI khoá bắt đầu bằng `meditrace_` (ca khám, lời thoại, tên bệnh nhân, các kho useKho,
 * mẫu giọng bác sĩ, công tắc gửi ra mô hình ngoài, chủ máy, khoá mới chưa biết),
 * TRỪ các tuỳ chọn giao diện thuần không chứa dữ liệu bệnh nhân trong KHOA_GIU_LAI.
 */

export const TIEN_TO = "meditrace_";

/** Tuỳ chọn giao diện thuần, không có dữ liệu bệnh nhân — giữ lại qua đăng xuất. */
export const KHOA_GIU_LAI: readonly string[] = ["meditrace_taskbar_position"];

/** Khoá đã biết chứa ca khám/lời thoại; luôn gọi removeItem kể cả khi Storage không liệt kê được. */
export const KHOA_DU_LIEU_CA: readonly string[] = [
  "meditrace_sessions",
  "meditrace_sessions_luc",
  "meditrace_ca_dang_mo",
  "meditrace_kho_ca-kham",
  "meditrace_kho_ca-kham_luc",
  "meditrace_kho_benh-nhan",
  "meditrace_kho_benh-nhan_luc",
  "meditrace_kho_nhiem-vu",
  "meditrace_kho_nhiem-vu_luc",
  "meditrace_kho_tra-cuu",
  "meditrace_kho_tra-cuu_luc",
  "meditrace_kho_mau-van-ban",
  "meditrace_kho_mau-van-ban_luc",
  "meditrace_kho_mau-benh-an-tuy-chinh",
  "meditrace_kho_mau-benh-an-tuy-chinh_luc",
  "meditrace_doctor_voiceprint_v1",
];

export type KhoTrinhDuyet = {
  removeItem(k: string): void;
  length?: number;
  key?(i: number): string | null;
};

export function laKhoaCanXoa(k: string): boolean {
  return k.startsWith(TIEN_TO) && !KHOA_GIU_LAI.includes(k);
}

function lietKe(kho: KhoTrinhDuyet): string[] {
  const ra = new Set<string>();
  try {
    if (typeof kho.length === "number" && typeof kho.key === "function") {
      for (let i = 0; i < kho.length; i++) {
        const k = kho.key(i);
        if (k !== null) ra.add(k);
      }
    }
  } catch {}
  try {
    for (const k of Object.keys(kho)) ra.add(k);
  } catch {}
  return [...ra];
}

/** Xoá khoá dữ liệu ca khám; trả về danh sách khoá đã gọi xoá. Không bao giờ ném lỗi. */
export function xoaDuLieuTrinhDuyet(kho: KhoTrinhDuyet | null | undefined): string[] {
  if (!kho) return [];
  const can = new Set<string>(KHOA_DU_LIEU_CA);
  for (const k of lietKe(kho)) if (laKhoaCanXoa(k)) can.add(k);
  const daXoa: string[] = [];
  for (const k of can) {
    try {
      kho.removeItem(k);
      daXoa.push(k);
    } catch {}
  }
  return daXoa;
}
