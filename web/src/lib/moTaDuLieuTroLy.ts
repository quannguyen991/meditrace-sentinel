/**
 * Dòng mô tả ngay trên ô hỏi: trợ lý đang dùng dữ liệu gì của ca đang mở. Khớp đúng thứ được gửi đi
 * trong handleSendEvidenceMessage (mệnh đề đã tách + tuổi/giới/thai kỳ; không gửi tên, ngày, địa chỉ).
 */
export function moTaDuLieuTroLy(t: {
  coBanNhap: boolean;
  soMenhDe: number;
  tuoi?: number;
  gioi?: string;
  coThai?: boolean;
}): { coDuLieu: boolean; chu: string } {
  if (!t.coBanNhap || t.soMenhDe === 0) {
    return { coDuLieu: false, chu: "Chưa có bản nháp — tạo bản nháp trước." };
  }
  const phan = [`${t.soMenhDe} mệnh đề`];
  if (typeof t.tuoi === "number") phan.push(`${t.tuoi} tuổi`);
  if (t.gioi) phan.push(t.gioi);
  if (t.coThai) phan.push("có thai");
  return { coDuLieu: true, chu: `Đang dùng: ${phan.join(" · ")}` };
}
