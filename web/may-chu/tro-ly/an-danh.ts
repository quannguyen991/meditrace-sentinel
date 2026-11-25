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
const R_TEN_LA = /(?<![\p{L}])(?:tên\s+(?:là|:)|họ\s+(?:và\s+)?tên)|(?<![\p{L}])[Tt]ên\s+\p{Lu}/u;
// Chữ hoa đầu từ nhận bằng \p{Lu}\p{Ll}: không dùng cờ `i` ở đây vì nó làm \p{Lu} khớp cả chữ thường.
const XUNG_HO = "(?:[Bb]ác sĩ|[Bb]ác|[Aa]nh|[Cc]hị|[Cc]ô|[Cc]hú|[Ôô]ng|ÔNG|[Bb]à|BÀ|[Ee]m|[Cc]háu|[Bb]é|[Mm]ẹ|[Bb]ố|[Cc]ha|[Mm]á|[Vv]ợ|[Cc]hồng|BS|bs)";
// Tên một chữ hoa đầu, hoặc viết hoa toàn bộ ("ÔNG NGUYỄN VĂN A").
const R_XUNG_HO_TEN = new RegExp(`(?<![\\p{L}])${XUNG_HO}\\s+\\p{Lu}[\\p{Ll}\\p{Lu}]+`, "u");
// "bệnh nhân Nữ/Covid/Parkinson..." là giới hay bệnh, không phải tên.
const R_BN_TEN = new RegExp(
  "(?<![\\p{L}])(?:[Bb]ệnh nhân|BN)\\s+(?!(?:Nam|NAM|Nữ|NỮ|Covid|COVID|Parkinson|Alzheimer|Down|Crohn|Cushing|Addison|Basedow|Đái|Tăng|Hen|Suy|Viêm|Ung|Sốt|Tiểu)(?![\\p{L}]))\\p{Lu}[\\p{Ll}\\p{Lu}]+",
  "u",
);
const R_HO = /(?<![\p{L}])(?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý|Đinh|Trương|Đoàn|Lương|Trịnh|Phùng|Quách|Vương|Nghiêm|Kiều|Nguyen|Tran|Pham|Hoang|Huynh)\s+\p{Lu}[\p{Ll}\p{Lu}]+/u;
const R_NOI = /(?<![\p{L}])(?:[Đđ]ường|[Pp]hố|[Pp]hường|[Xx]ã|[Qq]uận|[Hh]uyện|[Tt]ỉnh|[Tt]hành phố)\s+(?:\d+|\p{Lu}\p{Ll}{2,})/u;
const R_GIAY_TO = /(?<![\p{L}])(?:CCCD|CMND)(?![\p{L}])|(?<![\p{L}])BHYT\s*(?:số|:)?\s*[A-Z]{0,2}\s*\d/u;

/** Trả lý do nếu `s` còn dấu hiệu danh tính; `null` nếu không thấy. */
function lyDoDanhTinh(raw: string): string | null {
  const s = raw.normalize("NFC");
  const so = s.replace(/[()]/g, " ").replace(SAT_GIUA_SO, "");
  if (R_EMAIL.test(s)) return "email";
  if (R_SO_DAI.test(so)) return "chuoi_so_dai";
  if (R_NGAY.some((r) => r.test(s))) return "ngay";
  if (R_TEN_LA.test(s)) return "ten";
  if (R_XUNG_HO_TEN.test(s) || R_BN_TEN.test(s) || R_HO.test(s)) return "ten_rieng";
  if (R_NOI.test(s)) return "dia_chi";
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
    if (!MUC_CHO_PHEP.includes(String(m?.section ?? ""))) {
      soBo.muc_khong_cho_phep++;
      continue;
    }
    const goc = m.drug ? `thuốc: ${m.drug}` : String(m.text ?? "");
    if (!goc.trim()) {
      soBo.rong++;
      continue;
    }
    const sach = lamSachDong(goc, m.subject);
    if (sach === null) {
      // Dòng không rỗng mà bị loại: còn danh tính. (Dòng chỉ gồm ngày cũng vào đây; chấp nhận, an toàn hơn.)
      soBo.con_danh_tinh++;
      continue;
    }
    let ra = sach;
    // Người nhà không được gộp thành người bệnh (mục 5.1: chỉ "người bệnh" hoặc "người nhà").
    if (/^(người nhà|mẹ|bố|ba|má|cha|vợ|chồng|con)(?![\p{L}])/iu.test(String(m.subject ?? "").trim())) ra = `người nhà: ${ra}`;
    if (m.negated) ra = `KHÔNG CÓ: ${ra}`;
    else if (m.certainty === "nghi ngờ") ra = `nghi ngờ: ${ra}`;
    dong.push(ra);
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
