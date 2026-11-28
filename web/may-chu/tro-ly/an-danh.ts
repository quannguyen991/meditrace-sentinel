/**
 * BỘ LUẬT ẨN DANH cho tra cứu (thiết kế mục 5.1).
 *
 * NGUYÊN TẮC: xây chuỗi gửi ra ngoài từ DANH SÁCH CHO PHÉP, không "lau sạch" văn bản. Cái gì không
 * được liệt kê (trích dẫn, chữ trong hội thoại, chủ thể cụ thể, ngày, nơi chốn, số liên lạc, mục
 * hồ sơ không thuộc danh sách) thì không đi ra. Câu hỏi bác sĩ gõ là chuỗi tự do duy nhất, nên đi
 * qua máy phát hiện; nghi ngờ mà không chắc che được thì CHẶN, không đoán.
 *
 * Gửi được: triệu chứng, dấu hiệu, kết quả khám, bệnh/tình trạng đã biết, thuốc kèm liều, nhóm tuổi,
 * giới, có thai hay không (người dùng xác nhận 23/11/2026 là không ảnh hưởng). Không gửi: tuổi
 * chính xác, ngày sinh, tên, địa chỉ, số liên lạc, mã hồ sơ, tên cơ sở hay bác sĩ.
 *
 * Hàm thuần, không gọi ra ngoài. Chạy thử: npx tsx may-chu/tro-ly/an-danh.test.ts
 */

export type NhomTuoi = "sơ sinh" | "trẻ em" | "người lớn" | "cao tuổi";

/** Hình dạng của một mệnh đề từ `menhDeChoGiaoDien` (server.ts); các trường khác bị bỏ qua. */
export type MenhDeVao = {
  text?: string;
  section?: string;
  subject?: string | null;
  negated?: boolean;
  certainty?: string | null;
  drug?: string | null;
  time?: string | null;
  [khac: string]: unknown;
};

export type NguCanhVao = { tuoi?: number | null; gioi?: string | null; coThai?: boolean | null };

export type CaAnDanh = {
  nhomTuoi: NhomTuoi | null;
  gioi: "nam" | "nữ" | null;
  coThai: boolean | null;
  dong: string[];
  soBo: Record<string, number>;
};

/** Bảy mục hồ sơ được phép đi ra. Mục "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" và "KẾ HOẠCH ĐIỀU TRỊ" không. */
export const MUC_CHO_PHEP: readonly string[] = [
  "LÝ DO KHÁM BỆNH",
  "BỆNH SỬ HIỆN TẠI",
  "TIỀN SỬ BỆNH",
  "THUỐC ĐANG DÙNG",
  "DỊ ỨNG",
  "KHÁM LÂM SÀNG",
  "CHẨN ĐOÁN",
];

export function nhomTuoi(tuoi: number): NhomTuoi {
  if (tuoi < 1) return "sơ sinh";
  if (tuoi < 16) return "trẻ em";
  if (tuoi < 65) return "người lớn";
  return "cao tuổi";
}

/* ------------------------------------------------------------------ máy phát hiện danh tính */

/**
 * Whitelist các hội chứng / bệnh danh viết hoa phổ biến để câu hỏi lâm sàng của bác sĩ
 * (ví dụ "bệnh nhân Kawasaki", "hội chứng Cushing", "bệnh nhân Parkinson", "sốt Dengue")
 * không bị nhận nhầm là tên riêng bệnh nhân.
 */
export const DANH_SACH_BENH_DANH_Y_KHOA: readonly string[] = [
  "Parkinson",
  "Basedow",
  "Crohn",
  "Alzheimer",
  "Kawasaki",
  "Cushing",
  "Addison",
  "Marfan",
  "Wilson",
  "Wernicke",
  "Korsakoff",
  "Tourette",
  "Bell",
  "Raynaud",
  "Sjögren",
  "Sjogren",
  "Behcet",
  "Behçet",
  "Graves",
  "Hashimoto",
  "Hodgkin",
  "Dengue",
  "Zika",
  "Whitmore",
  "Down",
  "Covid",
  "COVID",
  "Guillain",
  "Babinski",
  "Glasgow",
  "Lupus",
  "Gout",
  "Zona",
  "Rubella",
  "Ebola",
  "Stevens",
  "Epstein",
  "Henoch",
  "Meniere",
  "Ménière",
  "Lyme",
  "Reye",
  "Paget",
  "Chagas",
  "Weil",
  "Mallory",
  "Zollinger",
  "Boerhaave",
  "Brugada",
  "Fallot",
  "Hirschsprung",
  "Klinefelter",
  "Turner",
  "Takayasu",
];

/** Từ viết tắt bệnh lý / chỉ số lâm sàng phổ biến đứng ngay sau "bệnh nhân" / "BN" không phải tên người. */
const TU_VIET_TAT_VA_TU_Y_KHOA_SAU_BN = [
  "COPD",
  "ARDS",
  "STEMI",
  "NSTEMI",
  "NYHA",
  "CKD",
  "AKI",
  "CHF",
  "AF",
  "DVT",
  "PE",
  "GERD",
  "IBD",
  "IBS",
  "SLE",
  "RA",
  "OA",
  "HIV",
  "AIDS",
  "HBV",
  "HCV",
  "HSV",
  "HPV",
  "RSV",
  "CMV",
  "EBV",
  "MDR",
  "XDR",
  "ICU",
  "NICU",
  "PICU",
  "CCU",
  "BMI",
  "BSA",
  "GFR",
  "CrCl",
  "INR",
  "APTT",
  "AST",
  "ALT",
  "WBC",
  "RBC",
  "PLT",
  "CRP",
  "PCT",
  "PSA",
  "TSH",
  "ECG",
  "EEG",
  "EMG",
  "MRI",
  "CT",
  "THA",
  "ĐTĐ",
  "SXH",
  "XHTH",
  "BPTNMT",
  "NMCT",
  "TKMP",
  "TBMN",
  "RLCH",
  "RLLP",
  "Nam",
  "NAM",
  "Nữ",
  "NỮ",
  "Đái",
  "Tăng",
  "Hen",
  "Suy",
  "Viêm",
  "Ung",
  "Sốt",
  "Tiểu",
  "Hội",
  "Bệnh",
  "Liệt",
  "Nhiễm",
  "Đau",
  "Khó",
  "Ho",
  "Nôn",
  "Phù",
  "Vàng",
  "Thiếu",
  "Xuất",
  "Nhồi",
  "Đột",
  "Tràn",
  "Xơ",
  "Loét",
  "Lao",
  "Gút",
  "Sỏi",
];

const MAU_WHITELIST_SAU_BN = [...DANH_SACH_BENH_DANH_Y_KHOA, ...TU_VIET_TAT_VA_TU_Y_KHOA_SAU_BN].join("|");

const MAU_EPONYM_HOA = [...DANH_SACH_BENH_DANH_Y_KHOA, ...TU_VIET_TAT_VA_TU_Y_KHOA_SAU_BN].join("|");

const SAT_GIUA_SO = /(?<=\d)[\s.-]+(?=\d)/g;
const R_EMAIL = /[\p{L}\d._%+-]+@[\p{L}\d-]+\.[\p{L}\d.-]+/u;
const R_SO_DAI = /\d{9,}/;
// Ngày 1–31 / tháng 1–12. "7/10", "1/2 viên", "90/60" là thang điểm, phân số, huyết áp: chỉ coi là ngày khi có
// năm, hoặc đứng sau chữ báo ngày (ngày, sinh, hẹn, khám, từ).
const NGAY = "(?:0?[1-9]|[12]\\d|3[01])";
const THANG = "(?:0?[1-9]|1[0-2])";
const R_NGAY = [
  new RegExp(`(?<![\\d/])${NGAY}[/.-]${THANG}[/.-]\\d{2,4}(?![\\d/])`, "u"),
  new RegExp(`(?<![\\p{L}])(?:ngày|sinh|hẹn|khám|từ)\\s+${NGAY}\\/${THANG}(?![\\d/])`, "iu"),
  /(?<!\d)\d{4}-\d{1,2}-\d{1,2}(?!\d)/u,
  /(?:ngày\s+)?\d{1,2}\s+tháng\s+\d{1,2}(?:\s+năm\s+\d{2,4})?/iu,
  /sinh\s+năm\s+\d{2,4}/iu,
];

const R_TEN_LA =
  /(?<![\p{L}])(?:tên\s*(?:là|:)\s*(?!(?:gì|thuốc|bệnh|hội\s+chứng|vi\s+khuẩn|vi\s+rút|virus)(?![\p{L}]))[\p{L}]{1,}|họ\s*(?:và\s+)?tên\s*(?:là|:)?\s*[\p{L}]{1,}|(?:bệnh\s+nhân|người\s+bệnh|bn|ông|bà|anh|chị|cháu|bé|em|cô|chú)\s+tên\s+(?:là\s*|:\s*)?(?!(?:gì|thuốc|bệnh)(?![\p{L}]))[\p{L}]{1,})/iu;
const R_TEN_HOA = new RegExp(`(?<![\\p{L}])[Tt]ên\\s+(?!(?:${MAU_EPONYM_HOA})(?![\\p{L}\\d]))\\p{Lu}[\\p{L}]+(?![\\p{L}\\d])`, "u");

// Chữ hoa đầu từ nhận bằng \p{Lu}\p{Ll}: không dùng cờ `i` ở đây vì nó làm \p{Lu} khớp cả chữ thường.
// Hậu tố (?![\p{L}\d]) đảm bảo các mã chỉ số có số đi liền như HbA1c, SpO2, G6PD, H5N1 không bị cắt chữ đầu làm tên riêng.
const XUNG_HO = "(?:[Bb]ác sĩ|[Bb]ác|[Aa]nh|[Cc]hị|[Cc]ô|[Cc]hú|[Ôô]ng|ÔNG|[Bb]à|BÀ|[Ee]m|[Cc]háu|[Bb]é|[Mm]ẹ|[Bb]ố|[Cc]ha|[Mm]á|[Vv]ợ|[Cc]hồng|BS|bs)";
// Tên một chữ hoa đầu, hoặc viết hoa toàn bộ ("ÔNG NGUYỄN VĂN A"), trừ hội chứng/từ viết tắt y khoa.
const R_XUNG_HO_TEN = new RegExp(
  `(?<![\\p{L}])${XUNG_HO}\\s+(?!(?:${MAU_WHITELIST_SAU_BN})(?![\\p{L}\\d]))\\p{Lu}[\\p{Ll}\\p{Lu}]+(?![\\p{L}\\d])`,
  "u",
);
// "bệnh nhân Nữ/Covid/Parkinson/Kawasaki/COPD/STEMI/HbA1c..." là giới, bệnh danh hoặc chỉ số, không phải tên riêng.
const R_BN_TEN = new RegExp(
  `(?<![\\p{L}])(?:[Bb]ệnh nhân|BỆNH NHÂN|BN)\\s+(?!(?:${MAU_WHITELIST_SAU_BN})(?![\\p{L}\\d]))\\p{Lu}[\\p{Ll}\\p{Lu}]+(?![\\p{L}\\d])`,
  "u",
);
// Bỏ qua cụm trùng họ mà không phải tên người ("Lý Do", "Thái Lan", "Cao Bằng", "Kim Ngân", "Hà Nội"…).
const R_HO =
  /(?<![\p{L}])(?!(?:Lý\s+Do|Thái\s+Lan|Cao\s+Bằng|Kim\s+Ngân|Hà\s+(?:Nội|Giang|Nam|Tĩnh))(?![\p{L}\d]))(?:(?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý|Đinh|Trương|Đoàn|Lương|Trịnh|Phùng|Quách|Vương|Nghiêm|Kiều|Nguyen|Tran|Pham|Hoang|Huynh)\s+\p{Lu}[\p{Ll}\p{Lu}]*|(?:NGUYỄN|TRẦN|LÊ|PHẠM|HUỲNH|PHAN|VŨ|VÕ|ĐẶNG|BÙI|ĐỖ|NGÔ|ĐINH|TRƯƠNG|ĐOÀN|LƯƠNG|TRỊNH|PHÙNG|QUÁCH|VƯƠNG|NGHIÊM|KIỀU|NGUYEN|TRAN|PHAM|HOANG|HUYNH)\s+\p{Lu}+|(?:HOÀNG|HỒ|DƯƠNG|LÝ)\s+(?!(?:TÍNH|VẬT|ĐẢM|ĐIỂM|THỂ|SƠ|MÁU|DO|LỊCH|THUYẾT|TƯỞNG)(?![\p{L}]))\p{Lu}+)(?![\p{L}\d])/u;

// Họ tên tiếng Việt viết chữ thường đi sau từ khóa nhận diện (bệnh nhân, ông/bà/anh/chị/cháu...) hoặc họ + tên đệm + tên
const XUNG_HO_CA_NHAN_THUONG = "(?:ông|bà|anh|chị|cháu|cô|chú|bé)";
const TU_KHOA_NHAN_DIEN_CHUNG = "(?:bệnh\\s+nhân|người\\s+bệnh|bn|em|bác(?:\\s+sĩ)?|bs)";
const HO_VIET_RO = "nguyễn|trần|lê|phạm|huỳnh|phan|vũ|võ|đặng|bùi|đỗ|ngô|đinh|trương|đoàn|trịnh|phùng|quách|nghiêm|nguyen|tran|pham|hoang|huynh";
const R_HO_THUONG_SAU_TU_KHOA = new RegExp(
  `(?<![\\p{L}])(?:` +
    `${XUNG_HO_CA_NHAN_THUONG}\\s+(?:${HO_VIET_RO}|hoàng|hồ|dương|lý)(?![\\p{L}])|` +
    `${TU_KHOA_NHAN_DIEN_CHUNG}\\s+(?:` +
      `(?:${HO_VIET_RO})(?![\\p{L}])|` +
      `(?:hoàng|hồ|dương|lý)\\s+(?!(?:tính|vật|đảm|điểm|thể|sơ|máu|đồ|tưởng|do|lịch|thuyết|trí|luận|học|sinh|nhiệt|cầu|đạo|quản)(?![\\p{L}]))[\\p{L}]{2,}` +
    `)` +
  `)`,
  "iu",
);
const R_HO_TEN_BA_TIENG_THUONG =
  /(?<![\p{L}])(?:nguyễn|trần|lê|phạm|hoàng|huỳnh|phan|vũ|võ|đặng|bùi|đỗ|hồ|ngô|dương|lý|nguyen|tran|pham|hoang|huynh)\s+(?:văn|thị|hữu|đức|đình|xuân|ngọc|quốc|bá|trọng|công|duy|minh|hoài|thu|thanh|anh|quang|tuấn|hải|phương|thành|tiến|mạnh|khánh|thảo|hồng|kim|mỹ|gia|bảo|nhật|thế|việt|tấn|vĩnh)\s+[\p{L}]{1,}/iu;

// Địa chỉ viết hoa (chữ hoa đầu từ theo sau bởi chữ thường \p{Ll}+ để không bắt nhầm đường dùng thuốc IV/IM/PO/SC),
// có số, hoặc viết chữ thường (số nhà, ngõ, ngách, phường, quận, huyện, tỉnh, thành phố kèm tên riêng)
const R_NOI_HOA = /(?<![\p{L}])(?:[Đđ]ường|[Pp]hố|[Pp]hường|[Xx]ã|[Qq]uận|[Hh]uyện|[Tt]ỉnh|[Tt]hành phố|[Tt][Pp]\.?)\s+(?:\d+[a-zA-Z]?|\p{Lu}\p{Ll}+)/u;
const TINH_THANH_VN =
  "hà\\s+nội|hồ\\s+chí\\s+minh|hcm|tphcm|sài\\s+gòn|đà\\s+nẵng|hải\\s+phòng|cần\\s+thơ|huế|thừa\\s+thiên|" +
  "nghệ\\s+an|thanh\\s+h[oó]a|đồng\\s+nai|bình\\s+dương|quảng\\s+ninh|hải\\s+dương|nam\\s+định|thái\\s+bình|" +
  "vĩnh\\s+phúc|phú\\s+thọ|bắc\\s+ninh|bắc\\s+giang|hưng\\s+yên|hà\\s+nam|ninh\\s+bình|lào\\s+cai|yên\\s+bái|" +
  "sơn\\s+la|lạng\\s+sơn|cao\\s+bằng|tuyên\\s+quang|thái\\s+nguyên|hà\\s+tĩnh|quảng\\s+bình|quảng\\s+trị|" +
  "quảng\\s+nam|quảng\\s+ngãi|bình\\s+định|phú\\s+yên|khánh\\s+h[oò]a|ninh\\s+thuận|bình\\s+thuận|kon\\s+tum|" +
  "gia\\s+lai|đắk\\s+lắk|đắc\\s+lắc|đắk\\s+nông|lâm\\s+đồng|bình\\s+phước|tây\\s+ninh|bà\\s+rịa|vũng\\s+tàu|" +
  "long\\s+an|tiền\\s+giang|bến\\s+tre|trà\\s+vinh|vĩnh\\s+long|đồng\\s+tháp|an\\s+giang|kiên\\s+giang|" +
  "cà\\s+mau|bạc\\s+liêu|sóc\\s+trăng|hậu\\s+giang|điện\\s+biên(?:\\s+phủ)?|lai\\s+châu|hà\\s+giang|bắc\\s+kạn|h[oò]a\\s+bình|" +
  "nha\\s+trang|đà\\s+lạt|biên\\s+h[oò]a|quy\\s+nhơn|hạ\\s+long|việt\\s+trì|thủ\\s+đức|buôn\\s+ma\\s+thuột|" +
  "vinh|pleiku|mỹ\\s+tho|phan\\s+thiết|tuy\\s+h[oò]a|đồng\\s+hới|tam\\s+kỳ|phủ\\s+lý|vĩnh\\s+yên|phúc\\s+yên|" +
  "thủ\\s+dầu\\s+một|dĩ\\s+an|thuận\\s+an|long\\s+xuyên|châu\\s+đốc|rạch\\s+giá|phú\\s+quốc|móng\\s+cái|cẩm\\s+phả|" +
  "uông\\s+bí|bảo\\s+lộc|cam\\s+ranh|phan\\s+rang|đồng\\s+xoài|gia\\s+nghĩa|tân\\s+an|cao\\s+lãnh|sa\\s+đéc|vị\\s+thanh";

const TU_KHONG_PHAI_TEN_DIA_DANH =
  "có|không|chưa|đã|đang|sẽ|nên|cần|phải|được|bị|là|ở|tại|với|và|hoặc|hay|khi|nếu|thì|mà|để|cho|về|từ|" +
  "lên|xuống|sang|ra|vào|chuyển|khám|điều|xử|cấp|trạm|tuyến|bệnh|viện|lớn|nhỏ|nào|gì|đó|này|khác|trên|dưới|" +
  "ngoài|trong|quận|huyện|tỉnh|xã|phường|thành|trung|ương|y|tế|theo|dõi|tiếp|nhận|thiếu|dùng|gửi|chỉ|định|kê|" +
  "tiêm|truyền|hẹn|tái|làm|chụp|xét|nghiệm|mổ|phẫu|thuật|cứu|chữa|quản|lý|phát|thuốc|máu|huyết|dịch|oxy";

const R_DIA_CHI_THUONG = [
  /(?<![\p{L}])số\s+nhà\s*[\d\p{L}]/iu,
  /(?<![\p{L}])(?:ở|tại|địa\s+chỉ|trú\s+tại|ngụ\s+tại)\s+số\s+\d+/iu,
  /(?<![\p{L}])ngõ\s+(?:\d+[\p{L}\d/.-]*|(?!(?:nhỏ|hẹp|cụt|tối|rộng)(?![\p{L}]))[\p{L}]{2,})/iu,
  /(?<![\p{L}])ngách\s+(?:\d+[\p{L}\d/.-]*|(?!(?:sườn|màng|mũi|bướm|lợi|thượng|hạnh|thanh|tử|âm|tiền|phế|nhĩ|xoang)(?![\p{L}]))[\p{L}]{2,}\s+[\p{L}]{2,})/iu,
  new RegExp(`(?<![\\p{L}])(?:tỉnh|thành\\s+phố|tp\\.?)(?:\\s+tỉnh)?\\s+(?:${TINH_THANH_VN})(?![\\p{L}])`, "iu"),
  new RegExp(
    `(?<![\\p{L}])(?:phường|quận|huyện|thành\\s+phố)\\s+(?:\\d+[a-z]?|` +
      `(?!(?:${TU_KHONG_PHAI_TEN_DIA_DANH})(?![\\p{L}]))[\\p{L}]{2,}\\s+(?!(?:${TU_KHONG_PHAI_TEN_DIA_DANH})(?![\\p{L}]))[\\p{L}]{2,})`,
    "iu",
  ),
];

const R_GIAY_TO = /(?<![\p{L}])(?:CCCD|CMND)(?![\p{L}])|(?<![\p{L}])BHYT\s*(?:số|:)?\s*[A-Z]{0,2}\s*\d/iu;

/**
 * Các mẫu danh tính dùng trong `lyDoDanhTinh`, dạng dùng được để CHE trên văn bản gốc
 * (chuỗi số dài viết liền hoặc cách bằng khoảng trắng/chấm/gạch/ngoặc tương đương R_SO_DAI sau khi ghép số).
 * Dùng cho đường gửi văn bản tự do ra mô hình ngoài (an-danh-ngoai.ts).
 */
export const MAU_DANH_TINH_DE_CHE: ReadonlyArray<RegExp> = [
  R_EMAIL,
  /\d(?:[\s().-]*\d){8,}/u,
  ...R_NGAY,
  R_TEN_LA,
  R_TEN_HOA,
  R_XUNG_HO_TEN,
  R_BN_TEN,
  R_HO,
  R_HO_THUONG_SAU_TU_KHOA,
  R_HO_TEN_BA_TIENG_THUONG,
  R_NOI_HOA,
  ...R_DIA_CHI_THUONG,
  R_GIAY_TO,
];

/** Trả lý do nếu `s` còn dấu hiệu danh tính; `null` nếu không thấy. */
export function lyDoDanhTinh(raw: string): string | null {
  const s = raw.normalize("NFC");
  const so = s.replace(/[()]/g, " ").replace(SAT_GIUA_SO, "");
  if (R_EMAIL.test(s)) return "email";
  if (R_SO_DAI.test(so)) return "chuoi_so_dai";
  if (R_NGAY.some((r) => r.test(s))) return "ngay";
  if (R_TEN_LA.test(s) || R_TEN_HOA.test(s)) return "ten";
  if (
    R_XUNG_HO_TEN.test(s) ||
    R_BN_TEN.test(s) ||
    R_HO.test(s) ||
    R_HO_THUONG_SAU_TU_KHOA.test(s) ||
    R_HO_TEN_BA_TIENG_THUONG.test(s)
  ) {
    return "ten_rieng";
  }
  if (R_NOI_HOA.test(s) || R_DIA_CHI_THUONG.some((r) => r.test(s))) return "dia_chi";
  if (R_GIAY_TO.test(s)) return "giay_to";
  return null;
}

const QUAN_HE = new Set([
  "bệnh nhân", "bn", "người bệnh", "người nhà", "mẹ", "bố", "ba", "má", "cha", "con", "vợ", "chồng",
  "anh", "chị", "em", "ông", "bà", "cô", "chú", "cháu", "bé", "trẻ", "bác",
]);

/** Bỏ tiền tố chủ thể ("bà Hoa: ..."); không cắt nội dung chỉ tình cờ có dấu hai chấm ("huyết áp: 120/80"). */
function boTienTo(s: string, subject?: string | null): string {
  const m = s.match(/^([^:]{1,30}):\s*([\s\S]*)$/u);
  if (!m) return s;
  const tienTo = m[1].trim().toLowerCase();
  const sub = (subject || "").trim().toLowerCase();
  if ((sub && tienTo === sub) || QUAN_HE.has(tienTo) || QUAN_HE.has(tienTo.split(/\s+/)[0])) return m[2];
  return s;
}

function boNgay(s: string): string {
  let ra = s;
  for (const r of R_NGAY) ra = ra.replace(new RegExp(r.source, r.flags + "g"), "");
  return ra.replace(/\s{2,}/g, " ").trim();
}

/** Làm sạch một dòng mệnh đề; `null` nếu rỗng hoặc sau khi bỏ ngày vẫn còn dấu hiệu danh tính. */
export function lamSachDong(s: string, subject?: string | null): string | null {
  const bo = boNgay(nhomHoaTuoi(boTienTo(String(s ?? "").normalize("NFC").trim(), subject)));
  if (!bo) return null;
  return lyDoDanhTinh(bo) ? null : bo;
}

/** Tuổi chính xác không đi ra: "3 tuổi" thành "(trẻ em)", "6 tháng tuổi" thành "(sơ sinh)". */
function nhomHoaTuoi(s: string): string {
  return s
    .replace(/(\d+)\s*(?:tháng|ngày|tuần)\s*tuổi/giu, () => `(${nhomTuoi(0)})`)
    .replace(/(\d{1,3})\s*tuổi/giu, (_m, n: string) => `(${nhomTuoi(Number(n))})`);
}

export function kiemCauHoi(cau: string): { ok: true; cau: string } | { ok: false; lyDo: string } {
  const c = nhomHoaTuoi(String(cau ?? "").normalize("NFC").trim());
  if (!c) return { ok: false, lyDo: "rong" };
  const ly = lyDoDanhTinh(c);
  return ly ? { ok: false, lyDo: ly } : { ok: true, cau: c };
}

/* ------------------------------------------------------------------ dựng chuỗi gửi ra */

function chuanGioi(g?: string | null): "nam" | "nữ" | null {
  const x = String(g ?? "").trim().toLowerCase();
  if (x === "nam" || x === "male" || x === "m") return "nam";
  if (x === "nữ" || x === "nu" || x === "female" || x === "f") return "nữ";
  return null;
}

export function xayCaAnDanh(menhDe: MenhDeVao[], nguCanh: NguCanhVao): CaAnDanh {
  const soBo: Record<string, number> = { muc_khong_cho_phep: 0, con_danh_tinh: 0, rong: 0 };
  const dong: string[] = [];
  for (const m of menhDe || []) {
    const muc = String(m?.section ?? "");
    if (!MUC_CHO_PHEP.includes(muc)) {
      soBo.muc_khong_cho_phep++;
      continue;
    }
    const vanTho = String(m.text ?? "").trim();
    const thuocTho = String(m.drug ?? "").trim();

    // TUYỆT ĐỐI KHÔNG để m.drug ghi đè xóa mất m.text (đặc biệt ở mục DỊ ỨNG / TIỀN SỬ BỆNH).
    // Với THUỐC ĐANG DÙNG: ưu tiên giữ m.text (hoặc m.drug), kèm thông tin liều từ m.drug nếu m.text chưa có.
    let sach: string | null = null;
    if (!vanTho && !thuocTho) {
      soBo.rong++;
      continue;
    }
    if (vanTho) {
      const sachVan = lamSachDong(vanTho, m.subject);
      if (sachVan === null) {
        soBo.con_danh_tinh++;
        continue;
      }
      if (thuocTho) {
        const sachThuoc = lamSachDong(thuocTho, m.subject);
        if (sachThuoc === null) {
          soBo.con_danh_tinh++;
          continue;
        }
        sach = sachVan.toLowerCase().includes(sachThuoc.toLowerCase()) ? sachVan : `${sachVan} (${sachThuoc})`;
      } else {
        sach = sachVan;
      }
    } else {
      sach = lamSachDong(thuocTho, m.subject);
      if (sach === null) {
        soBo.con_danh_tinh++;
        continue;
      }
    }

    let ra = sach;
    // Người nhà không được gộp thành người bệnh (mục 5.1: chỉ "người bệnh" hoặc "người nhà").
    if (/^(người nhà|mẹ|bố|ba|má|cha|vợ|chồng|con)(?![\p{L}])/iu.test(String(m.subject ?? "").trim())) ra = `người nhà: ${ra}`;
    if (m.negated) ra = `KHÔNG CÓ: ${ra}`;
    else if (m.certainty === "nghi ngờ") ra = `nghi ngờ: ${ra}`;
    // Gắn tiền tố mục rõ ràng để DỊ ỨNG sốc phản vệ không bao giờ bị hiểu nhầm thành THUỐC ĐANG DÙNG.
    dong.push(`[${muc}] ${ra}`);
  }
  const tuoi = nguCanh?.tuoi;
  return {
    nhomTuoi: typeof tuoi === "number" && Number.isFinite(tuoi) && tuoi >= 0 ? nhomTuoi(tuoi) : null,
    gioi: chuanGioi(nguCanh?.gioi),
    coThai: typeof nguCanh?.coThai === "boolean" ? nguCanh.coThai : null,
    dong,
    soBo,
  };
}

/** Đúng chuỗi sẽ đưa vào lời gọi mô hình ngoài; cũng là bản xem trước cho bác sĩ. */
export function chuoiGuiRa(ca: CaAnDanh, cauHoi: string): string {
  const boiCanh = [
    ca.nhomTuoi,
    ca.gioi,
    ca.coThai === true ? "có thai" : ca.coThai === false ? "không có thai" : null,
  ].filter(Boolean);
  return [
    `Bối cảnh: ${boiCanh.length ? boiCanh.join(", ") : "(không rõ)"}.`,
    "Dấu hiệu và tình trạng:",
    ...(ca.dong.length ? ca.dong.map((d) => `- ${d}`) : ["- (chưa có)"]),
    `Câu hỏi: ${String(cauHoi ?? "").trim()}`,
  ].join("\n");
}
