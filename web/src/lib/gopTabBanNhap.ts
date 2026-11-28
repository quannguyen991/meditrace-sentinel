import type { DocumentTabItem } from "../types";

export const TEN_TAB_BAN_NHAP = "Bản nháp hồ sơ";

/** Tab SOAP còn nguyên mẫu: mọi dòng có chữ đều chỉ là tiêu đề kết thúc bằng dấu ":" (chưa ai điền gì). */
export function laMauSoapTrong(tab: DocumentTabItem): boolean {
  if (tab.type !== "soap") return false;
  return (tab.content || "")
    .split("\n")
    .map((d) => d.trim())
    .filter(Boolean)
    .every((d) => /^[^:]*:$/.test(d) || /^-\s*[^:]*:$/.test(d));
}

/**
 * Đặt bản nháp vừa tạo vào danh sách tab của ca: bỏ tab SOAP mẫu còn trống (tránh hai tab, một tab rỗng)
 * và bỏ bản nháp cũ cùng tên (tạo lại thì thay, không chồng thêm). Tab bác sĩ đã gõ nội dung thì giữ.
 */
export function gopTabBanNhap(tabs: DocumentTabItem[], tabMoi: DocumentTabItem): DocumentTabItem[] {
  return [
    ...tabs.filter((t) => !laMauSoapTrong(t) && !(t.title === TEN_TAB_BAN_NHAP && tabMoi.title === TEN_TAB_BAN_NHAP)),
    tabMoi,
  ];
}
