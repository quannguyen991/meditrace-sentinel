/**
 * Che định danh trước khi gửi văn bản TỰ DO (lời thoại, bản nháp, lời nhắc) ra cổng mô hình ngoài.
 *
 * Cách làm: (1) che theo các luật riêng cho tiếng Việt (ranh giới từ bằng lookaround \p{L} vì `\b` của JS
 * không hiểu chữ có dấu), (2) che tiếp mọi chỗ mà bộ kiểm danh tính của trợ lý (`lyDoDanhTinh`) còn bắt được,
 * (3) kiểm lại lần cuối: còn dấu hiệu danh tính thì TỪ CHỐI gửi (fail closed).
 * Mỗi đoạn bị che thành token `[PII_n]`, được khôi phục trong câu trả lời bằng `khoiPhucPII`.
 */
import { lyDoDanhTinh, MAU_DANH_TINH_DE_CHE } from "./tro-ly/an-danh";

const KHONG_CHU_TRUOC = "(?<![\\p{L}\\d])";
const KHONG_CHU_SAU = "(?![\\p{L}\\d])";
const TEN_HOA = "\\p{Lu}\\p{Ll}*(?:\\s+\\p{Lu}\\p{Ll}*){0,3}";
const HO = "Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý|Đinh|Trương|Đoàn|Lương|Trịnh|Phùng|Quách|Vương|Nghiêm|Kiều|Mai|Đào|Tạ|Tô|Lâm|Châu|Thái|Hà|Cao|Đàm|Lại|Khúc|Kim|Triệu";
const HO_THUONG = HO.toLowerCase();
const TEN_DEM_THUONG =
  "văn|thị|hữu|đức|đình|xuân|ngọc|quốc|bá|trọng|công|duy|minh|hoài|thu|thanh|anh|quang|tuấn|hải|phương|thành|tiến|mạnh|khánh|thảo|hồng|kim|mỹ|gia|bảo|nhật|thế|việt|tấn|vĩnh|diệu|như|ánh|tường|trung";
const XUNG_HO =
  "[Ôô]ng|[Bb]à|[Aa]nh|[Cc]hị|[Ee]m|[Cc]ô|[Cc]hú|[Bb]ác(?:\\s+sĩ)?|[Cc]háu|[Bb]é|[Cc]ụ|[Dd]ì|[Cc]ậu|[Mm]ợ|[Tt]hím|[Mm]ẹ|[Bb]ố|[Vv]ợ|[Cc]hồng|BS\\.?|[Bb]s\\.?|[Cc]on(?:\\s+(?:trai|gái|dâu|rể))?(?:\\s+(?:là|tên))?";
const TU_DIA_CHI = "ngõ|ngách|hẻm|kiệt|phố|đường|phường|quận|huyện|xã|thôn|xóm|ấp|thị\\s+trấn|thị\\s+xã|tỉnh|thành\\s+phố|tp\\.?|TP\\.?";
const NOI_TIEP_DIA_CHI = `(?:[\\s,]+(?:\\d+[\\p{L}\\d/-]*|\\p{Lu}\\p{Ll}*|(?:${TU_DIA_CHI})(?=\\s)))*`;
const NGAY_SO = "\\d{1,2}[/.-]\\d{1,2}[/.-]\\d{2,4}";

/** Luật che theo thứ tự: số liên lạc / mã trước, rồi ngày, địa chỉ, nơi học/làm, tên. */
const LUAT: RegExp[] = [
  // Email
  /[\p{L}\d._%+-]+@[\p{L}\d-]+(?:\.[\p{L}\d-]+)+/gu,
  // Mã bệnh nhân / hồ sơ có từ báo trước
  new RegExp(
    `${KHONG_CHU_TRUOC}(?:[Mm]ã\\s+(?:số\\s+)?(?:bệnh\\s+nhân|người\\s+bệnh|BN|hồ\\s+sơ|bệnh\\s+án|y\\s+tế|lưu\\s+trữ)|[Ss]ố\\s+(?:hồ\\s+sơ|bệnh\\s+án|lưu\\s+trữ|vào\\s+viện)|PID|MRN|MSBN|[Mm]ã\\s+BN)\\s*(?:là|:|số)?\\s*[A-Za-z0-9][A-Za-z0-9/-]{3,}`,
    "gu",
  ),
  // Thẻ BHYT, CCCD/CMND
  /(?<![\p{L}])(?:[Tt]hẻ\s*)?(?:BHYT|[Bb]ảo\s+hiểm\s+y\s+tế)\s*(?:số|là|:)?\s*[A-Z]{2}\s*\d(?:[\s.]*\d){11,13}/gu,
  /(?<![\p{L}])(?:CCCD|CMND|[Cc]ăn\s+cước(?:\s+công\s+dân)?|[Ss]ố\s+định\s+danh)\s*(?:số|là|:)?\s*\d(?:[\s.]*\d){7,13}/gu,
  // Điện thoại: 0xxx xxx xxx, 0xxx.xxx.xxx, +84 xxx xxx xxx, 84xxxxxxxxx, máy bàn 0xx xxxx xxxx
  /(?<![\d\p{L}+])(?:\+?84[\s.-]?|0)\d{1,3}(?:[\s.-]?\d){6,8}(?!\d)/gu,
  // Chuỗi 8 chữ số trở lên (mã bệnh nhân, mã hồ sơ, số giấy tờ), kể cả viết cách
  /(?<!\d)\d(?:[\s.-]?\d){7,}(?!\d)/gu,
  // Ngày sinh và ngày đầy đủ
  new RegExp(
    `${KHONG_CHU_TRUOC}(?:[Ss]inh\\s+(?:ngày|năm|tháng)|[Nn]gày(?:\\s+tháng\\s+năm)?\\s+sinh|NS)\\s*:?\\s*(?:${NGAY_SO}|\\d{1,2}\\s+tháng\\s+\\d{1,2}(?:\\s+năm\\s+\\d{2,4})?|\\d{1,2}[/.-]\\d{4}|\\d{4})`,
    "gu",
  ),
  new RegExp(`(?<![\\d/])${NGAY_SO}(?![\\d/])`, "gu"),
  /(?<![\p{L}])(?:ngày\s+)?\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{2,4}/giu,
  // Tuổi rất cao (>= 90) là định danh gián tiếp
  /(?<!\d)(?:9\d|1[01]\d)\s*tuổi/gu,
  // Địa chỉ có từ báo trước (cho phép dấu phẩy: "123 Nguyễn Trãi, phường 5, quận 5, TP HCM")
  /(?:địa chỉ(?:\s+cư\s+trú)?|thường trú tại|ngụ tại|trú tại|nhà ở|hộ khẩu tại)\s*(?:là|:)?\s*[^\n;.]*?(?:phường|xã|thị trấn|quận|huyện|thị xã|tỉnh|thành phố|tp\.?)[^\n;.]*/giu,
  // Số nhà + ngõ/ngách/hẻm/phố/đường + tên (không bắt "đường huyết", "đường uống", "đái tháo đường")
  new RegExp(
    `${KHONG_CHU_TRUOC}(?:(?:[Ss]ố\\s+(?:nhà\\s+)?)?\\d+[\\p{L}\\d/-]*[\\s,]+)?(?:[Ss]ố\\s+nhà|[Nn]gõ|[Nn]gách|[Hh]ẻm|[Kk]iệt|[Tt]hôn|[Xx]óm|[Pp]hố|(?<!tháo\\s)[Đđ]ường)\\s+(?:số\\s+)?(?:\\d+[\\p{L}\\d/-]*|\\p{Lu}\\p{Ll}*)${NOI_TIEP_DIA_CHI}`,
    "gu",
  ),
  // Đơn vị hành chính + tên riêng / số
  new RegExp(
    `${KHONG_CHU_TRUOC}(?:[Pp]hường|[Qq]uận|[Hh]uyện|[Xx]ã|[Tt]hị\\s+trấn|[Tt]hị\\s+xã|[Tt]ỉnh|[Tt]hành\\s+phố|TP\\.?|[Tt]p\\.?)\\s+(?:\\d+${KHONG_CHU_SAU}|\\p{Lu}\\p{Ll}*)${NOI_TIEP_DIA_CHI}`,
    "gu",
  ),
  // Nơi ở không có từ địa chỉ: "sống ở Hoàn Kiếm", "quê ở Nam Định"
  new RegExp(`${KHONG_CHU_TRUOC}(?:[Ss]ống\\s+ở|[Qq]uê(?:\\s+ở)?|[Nn]hà\\s+ở|ở\\s+tại)\\s+\\p{Lu}\\p{Ll}*${NOI_TIEP_DIA_CHI}`, "gu"),
  // Trường học, nơi làm việc
  new RegExp(
    `${KHONG_CHU_TRUOC}(?:[Tt]rường|[Cc]ông\\s+ty|[Cc]ơ\\s+quan|[Xx]í\\s+nghiệp|[Nn]hà\\s+máy)\\s+(?:(?:THCS|THPT|PTTH|TNHH|CP|[Tt]iểu\\s+học|[Mm]ầm\\s+non|[Tt]rung\\s+học(?:\\s+cơ\\s+sở|\\s+phổ\\s+thông)?|[Đđ]ại\\s+học|[Cc]ao\\s+đẳng|[Cc]ổ\\s+phần|[Mm]ột\\s+thành\\s+viên)\\s+)*\\p{Lu}[\\p{L}\\d]*(?:\\s+\\p{Lu}[\\p{L}\\d]*){0,4}`,
    "gu",
  ),
  // Tên có từ báo: "tên là Minh", "tên tôi là ...", "họ và tên: ...", "cháu tên là minh" (cả chữ thường)
  new RegExp(
    `${KHONG_CHU_TRUOC}(?:[Hh]ọ\\s+(?:và\\s+)?tên|[Tt]ên(?:\\s+(?:tôi|cháu|bé|em|con|bệnh\\s+nhân))?|[Tt]ôi\\s+tên|[Cc]háu\\s+tên|[Bb]é\\s+tên|[Ee]m\\s+tên|[Cc]on\\s+tên)\\s*(?:là|:)\\s*(?!(?:gì|thuốc|bệnh|hội\\s+chứng)(?![\\p{L}]))\\p{L}+(?:\\s+\\p{Lu}\\p{Ll}*){0,3}`,
    "gu",
  ),
  // Xưng hô + tên viết hoa: "Bà Hoa", "ông Nam", "Bác sĩ Minh", "con gái là Ngọc"
  new RegExp(`${KHONG_CHU_TRUOC}(?:${XUNG_HO})\\s+${TEN_HOA}${KHONG_CHU_SAU}`, "gu"),
  // Họ + tên viết hoa: "Nguyễn Văn Nam", "Trần Thị Hoa"
  new RegExp(`${KHONG_CHU_TRUOC}(?:${HO})(?:\\s+\\p{Lu}\\p{Ll}*){1,3}${KHONG_CHU_SAU}`, "gu"),
  // Họ tên chữ thường ba tiếng: "nguyễn văn an"
  new RegExp(`${KHONG_CHU_TRUOC}(?:${HO_THUONG})\\s+(?:${TEN_DEM_THUONG})\\s+\\p{Ll}+(?:\\s+\\p{Ll}+)?${KHONG_CHU_SAU}`, "giu"),
];

const SO_VONG_CHE_TOI_DA = 8;

function cheBangMau(text: string, re: RegExp, mask: (raw: string) => string): string {
  const toanCuc = re.flags.includes("g") ? re : new RegExp(re.source, `${re.flags}g`);
  toanCuc.lastIndex = 0;
  return text.replace(toanCuc, (raw) => (raw.trim() ? mask(raw) : raw));
}

export type KetQuaAnDanh =
  | { ok: true; van: string; bang: Map<string, string> }
  | { ok: false; lyDo: string; bang: Map<string, string> };

/** Che một chuỗi; dùng chung `bang` cho nhiều chuỗi của cùng một lời gọi để token không trùng. */
export function anDanhChoNgoai(
  van: string,
  bang: Map<string, string> = new Map(),
  kiemDanhTinh: (s: string) => string | null = lyDoDanhTinh,
): KetQuaAnDanh {
  let text = String(van ?? "").normalize("NFC");
  const mask = (raw: string) => {
    const token = `[PII_${bang.size + 1}]`;
    bang.set(token, raw);
    return token;
  };
  for (const re of LUAT) text = cheBangMau(text, re, mask);
  // Che tiếp mọi dấu hiệu bộ kiểm danh tính của trợ lý còn thấy, rồi kiểm lại.
  for (let vong = 0; vong < SO_VONG_CHE_TOI_DA && kiemDanhTinh(text); vong++) {
    for (const re of MAU_DANH_TINH_DE_CHE) text = cheBangMau(text, re, mask);
  }
  const conLai = kiemDanhTinh(text);
  if (conLai) return { ok: false, lyDo: conLai, bang };
  return { ok: true, van: text, bang };
}

/** Thay token về nguyên văn (lặp vì một đoạn che có thể chứa token đã che trước đó). */
export function khoiPhucPII(text: string, bang: Map<string, string>): string {
  let ra = text;
  const ds = [...bang.entries()].reverse();
  for (let lan = 0; lan < 5; lan++) {
    let doi = false;
    for (const [token, goc] of ds) {
      if (ra.includes(token)) {
        ra = ra.split(token).join(goc);
        doi = true;
      }
    }
    if (!doi) break;
  }
  return ra;
}

/** Lỗi khi văn bản còn định danh sau khi che: KHÔNG gửi ra ngoài. */
export class LoiConDanhTinh extends Error {
  status = 422;
  code = "con_danh_tinh";
  congKhai = true;
  constructor(public lyDo: string) {
    super(
      `Không gửi ra mô hình ngoài: nội dung còn thông tin định danh không che được (${lyDo}). ` +
        "Hãy bỏ tên, ngày sinh, địa chỉ, số điện thoại, mã hồ sơ khỏi nội dung rồi thử lại.",
    );
  }
}

/**
 * Duyệt chuỗi/mảng/đối tượng và che từng chuỗi (tương thích hàm cũ). Ném `LoiConDanhTinh` nếu
 * một chuỗi nào còn định danh sau khi che.
 */
export function anDanhVanBanNgoai(value: unknown, bang: Map<string, string>): unknown {
  if (typeof value === "string") {
    const kq = anDanhChoNgoai(value, bang);
    if (!kq.ok) throw new LoiConDanhTinh(kq.lyDo);
    return kq.van;
  }
  if (Array.isArray(value)) return value.map((item) => anDanhVanBanNgoai(item, bang));
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => [key, anDanhVanBanNgoai(item, bang)]),
    );
  }
  return value;
}
