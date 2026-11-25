/**
 * Che giấu các định danh trực tiếp trước khi gửi văn bản ra cổng mô hình ngoài.
 * Cho phép dấu phẩy trong địa chỉ (vd: "123 Nguyễn Trãi, phường 5, quận 5, TP HCM").
 */
export function anDanhVanBanNgoai(value: unknown, bang: Map<string, string>): unknown {
  if (typeof value === "string") {
    let text = value;
    const mask = (raw: string) => {
      const token = `[PII_${bang.size + 1}]`;
      bang.set(token, raw);
      return token;
    };
    const rules = [
      /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi,
      /(?<!\d)(?:\+?84|0)(?:3[2-9]|5[2689]|7[06-9]|8[1-9]|9\d)[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)/g,
      /(?:CCCD|CMND|căn cước(?: công dân)?|số định danh)(?:\s+(?:của\s+(?:tôi|bác|em))?\s*(?:số|là|:))?\s*\d{9,12}/gi,
      /(?:thẻ\s*)?(?:BHYT|bảo hiểm y tế)(?:\s*(?:số|là|:))?\s*[A-Z]{2}\s*\d\s*\d{2}\s*\d{10}/gi,
      /(?:địa chỉ(?:\s+cư\s+trú)?|thường trú tại|ngụ tại|trú tại|nhà ở|hộ khẩu tại)\s*(?:là|:)?\s*[^\n;.]*?(?:phường|xã|thị trấn|quận|huyện|thị xã|tỉnh|thành phố|tp\.?)[^\n;.]*/gi,
      /(?:tôi tên là|tên tôi là|bệnh nhân tên là|bệnh nhân\s*:|người bệnh\s*:|bác tên là|cháu tên là|họ và tên:)\s*[A-ZÀ-Ỹ][\p{L}'’-]*(?:\s+[A-ZÀ-Ỹ][\p{L}'’-]*){1,3}/giu,
      /\b(?:[Bb]ác|[Aa]nh|[Cc]hị|[Cc]ô|[Cc]hú|[Ôô]ng|[Bb]à|[Ee]m|[Cc]háu|[Bb]é)\s+(?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý|Đinh|Đoàn|Lương|Trịnh|Đào|Mai|Tạ|Hà|Tăng|Quách|Chu|La|Tô|Châu|Tống|Thái|Nghiêm|Kiều|Lâm|Vương)(?:\s+[A-ZÀ-Ỹ][\p{L}'’-]*){1,3}\b/gu,
    ];
    for (const re of rules) text = text.replace(re, (raw) => mask(raw));
    return text;
  }
  if (Array.isArray(value)) return value.map((item) => anDanhVanBanNgoai(item, bang));
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => [key, anDanhVanBanNgoai(item, bang)]),
    );
  }
  return value;
}
