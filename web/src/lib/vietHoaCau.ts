/**
 * Viết hoa chữ cái đầu dòng và đầu mỗi câu của bản nháp khi hiển thị, in, chép, tải.
 * Chỉ đổi MỘT chữ cái thường thành hoa nên độ dài chuỗi không đổi: vị trí ghép mệnh đề với câu vẫn đúng.
 * Không đụng tới nội dung lưu trữ hay chữ ký duyệt (chỉ áp lúc đưa ra).
 */
export function vietHoaCau(dong: string): string {
  return String(dong ?? "")
    // đầu dòng, sau gạch đầu dòng hoặc số thứ tự ("- ", "• ", "1. ", "2) ")
    .replace(/^(\s*(?:[-•*]\s+|\d+[.)]\s+)?)(\p{Ll})/u, (_m, dau: string, c: string) => dau + c.toLocaleUpperCase("vi"))
    // đầu mỗi câu: sau dấu chấm, chấm than, chấm hỏi rồi khoảng trắng ("37.5" không có khoảng trắng nên không đổi)
    .replace(/([.!?]\s+)(\p{Ll})/gu, (_m, dau: string, c: string) => dau + c.toLocaleUpperCase("vi"));
}

/** Áp `vietHoaCau` cho từng dòng của cả văn bản. */
export function vietHoaDauDong(van: string): string {
  return String(van ?? "").split("\n").map(vietHoaCau).join("\n");
}
