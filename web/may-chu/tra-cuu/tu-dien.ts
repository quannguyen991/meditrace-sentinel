/**
 * Từ điển, hằng số phân loại y khoa và hàm bóc tách cửa sổ văn bản dùng chung cho dịch vụ tra cứu.
 */

export type TaiLieu = {
  so: number;
  nguon:
    | "PubMed"
    | "MedlinePlus"
    | "FDA"
    | "Bộ Y tế"
    | "Phác đồ BYT"
    | "MSD"
    | "NICE"
    | "WHO"
    | "CDC"
    | "StatPearls"
    | "AAFP";
  ten: string;
  url: string;
  nam?: string;
  loai?: string;
  tapChi?: string;
  noiDung: string;
  pmc?: string;
};

export const UA_WEB = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36";

/** Câu hỏi về đợt cấp / cấp cứu (tiếng Việt hoặc từ khoá PubMed tiếng Anh). */
export const HOI_CAP = /(^|[^\p{L}])(cấp|cơn|đợt cấp|cấp cứu|sốc)(?!\p{L})|acute|exacerbation|attack|emergenc/iu;
export const MUC_DIEU_TRI = /điều trị|xử trí|treatment|management|pharmacolog|therapy/i;
export const MUC_CAP = /đợt cấp|cơn .*cấp|cấp tính|cấp cứu|acute|exacerbation|emergenc|attack|sốc|shock/i;
export const HOI_DIEU_TRI = /điều trị|xử trí|liều|thuốc|phác đồ|truyền|bù dịch|kháng sinh|treat|manage|dose|fluid/i;

export const TU_CHUNG_BENH = new Set([
  "high", "low", "acute", "chronic", "severe", "mild", "blood", "attack", "disease",
  "disorder", "disorders", "syndrome", "infection", "infections", "pain", "adult", "adults", "fever", "type", "primary",
]);

export function tuChinhBenh(ten: string): string {
  const tu = ten.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 3);
  return tu.find((w) => w.length >= 4 && !TU_CHUNG_BENH.has(w)) || tu[0] || "";
}

/** Tên phổ thông -> tên y khoa (khi mô hình không trả benh_en). */
export const TEN_Y_KHOA: Record<string, string> = {
  "high blood pressure": "hypertension",
  "heart attack": "myocardial infarction",
  "asthma attack": "asthma",
  flu: "influenza",
  "sinus infection": "sinusitis",
  "kidney stones": "nephrolithiasis",
  "stomach flu": "gastroenteritis",
  "pink eye": "conjunctivitis",
  "heart failure": "heart failure",
  "high cholesterol": "hyperlipidemia",
};

export const MUC_NHAN: Array<[RegExp, string[]]> = [
  [/liều|dose|dosing|mg\/kg|bao nhiêu mg|tối đa|dùng mấy lần/i, ["dosage_and_administration"]],
  [/tương tác|dùng chung|phối hợp|interaction/i, ["drug_interactions", "contraindications"]],
  [/chống chỉ định|contraindicat|không được dùng/i, ["contraindications", "boxed_warning"]],
  [/tác dụng phụ|tác dụng không mong muốn|adverse|side effect/i, ["adverse_reactions", "warnings_and_cautions"]],
  [/thai|cho con bú|pregnan/i, ["pregnancy", "use_in_specific_populations"]],
];

export const TEN_MY: Record<string, string> = {
  paracetamol: "acetaminophen",
  salbutamol: "albuterol",
  adrenaline: "epinephrine",
  adrenalin: "epinephrine",
  noradrenaline: "norepinephrine",
  glibenclamide: "glyburide",
  pethidine: "meperidine",
  frusemide: "furosemide",
  amoxycillin: "amoxicillin",
  lignocaine: "lidocaine",
  levothyroxine: "levothyroxine",
  aciclovir: "acyclovir",
  valaciclovir: "valacyclovir",
  ciclosporin: "cyclosporine",
  rifampicin: "rifampin",
  cefalexin: "cephalexin",
  colecalciferol: "cholecalciferol",
  ipratropium: "ipratropium",
  orciprenaline: "metaproterenol",
  metamizole: "dipyrone",
  hyoscine: "scopolamine",
  prednisolon: "prednisolone",
  amlodipin: "amlodipine",
};

export const DUONG_DUNG_FDA: Array<[RegExp, string]> = [
  [/khí dung|xịt|hít|phun sương|inhal|nebul/i, "RESPIRATORY (INHALATION)"],
  [/tiêm tĩnh mạch|truyền|tĩnh mạch|intraven/i, "INTRAVENOUS"],
  [/tiêm bắp|intramusc/i, "INTRAMUSCULAR"],
  [/nhỏ mắt|mắt/i, "OPHTHALMIC"],
  [/bôi|ngoài da|topical/i, "TOPICAL"],
  [/uống|viên|oral/i, "ORAL"],
];

export const THUOC_HIT = new Set([
  "albuterol", "levalbuterol", "ipratropium", "tiotropium", "budesonide", "fluticasone",
  "salmeterol", "formoterol", "beclomethasone", "ciclesonide", "mometasone", "umeclidinium", "vilanterol",
]);

export const TU_CHUNG_EN = new Set([
  "therapy", "treatment", "management", "adult", "adults", "children", "child", "dose",
  "dosage", "dosing", "clinical", "patients", "patient", "guideline", "guidelines", "disease", "acute", "chronic",
  "initiation", "threshold", "maximum", "daily", "timing", "drug", "drugs", "interaction", "interactions", "effect",
]);

export const TEN_NGUON: Record<string, string> = {
  MSD: "MSD Manual Professional",
  NICE: "NICE (Anh)",
  WHO: "WHO",
  CDC: "CDC (Hoa Kỳ)",
  StatPearls: "StatPearls (NCBI)",
  AAFP: "AAFP (Am Fam Physician)",
  "Phác đồ BYT": "Bộ Y tế · phác đồ lưu tại máy",
  PubMed: "PubMed",
  MedlinePlus: "MedlinePlus",
  FDA: "FDA · DailyMed",
  "Bộ Y tế": "Bộ Y tế · kcb.vn",
};

export function boThe(s: string): string {
  return s
    .replace(/<[^>]+>/g, "")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
    .replace(/&amp;/g, "&")
    .replace(/[\s\u200A\u2009]+/g, " ")
    .trim();
}

/** Chữ của một trang HTML: đoạn văn, mục liệt kê, tiêu đề mục — bỏ script, menu, chân trang. */
export function chuTrang(htmlVan: string): string {
  const t = htmlVan.replace(/<(script|style|nav|header|footer|noscript|svg)[^>]*>[\s\S]*?<\/\1>/gi, " ");
  const phan: string[] = [];
  for (const m of t.matchAll(/<(p|li|h2|h3|h4|td)[^>]*>([\s\S]*?)<\/\1>/gi)) {
    const v = boThe(
      m[2]
        .replace(/&(nbsp|ensp|emsp|thinsp);/g, " ")
        .replace(/&(ndash|mdash);/g, "–")
        .replace(/&(rsquo|lsquo);/g, "'")
        .replace(/&(rdquo|ldquo);/g, '"')
        .replace(/&(copy|reg|trade|shy|zwnj);/g, ""),
    );
    if (/^h/i.test(m[1])) {
      if (v.length > 3) phan.push(`\n## ${v}\n`);
    } else if (v.length > 25) {
      phan.push(v);
    }
  }
  return phan.join(" ");
}

/** Vị trí mục nên lấy: (đợt cấp + điều trị) > (đợt cấp, nếu hỏi cấp) > (điều trị, mà không phải mạn khi hỏi cấp). */
export function chonMuc(van: string, hoiCap: boolean, tuHoi: string[] = []): number {
  const muc = [...van.matchAll(/\n## ([^\n]*)\n/g)].map((m) => ({ vt: m.index!, ten: m[1] }));
  const trung = (m: { ten: string }) => tuHoi.filter((w) => m.ten.toLowerCase().includes(w)).length;
  const tot = <T extends { ten: string }>(ds: T[]) =>
    ds.reduce<T | undefined>((a, m) => (!a || trung(m) > trung(a) ? m : a), undefined);
  const dt = muc.filter((m) => MUC_DIEU_TRI.test(m.ten));
  if (hoiCap) {
    const c =
      tot(dt.filter((m) => MUC_CAP.test(m.ten))) ||
      tot(muc.filter((m) => MUC_CAP.test(m.ten) && !/triệu chứng|symptom|sign|chẩn đoán|diagnos/i.test(m.ten))) ||
      tot(dt.filter((m) => !/mạn|chronic|long-term|dài hạn/i.test(m.ten)));
    if (c) return c.vt;
  }
  return tot(dt)?.vt ?? -1;
}

/** Cửa sổ quanh chỗ khớp nhiều từ khoá nhất; câu hỏi về điều trị thì cộng điểm cho mục điều trị. */
export function cuaSo(van: string, tuKhoa: string[], hoiDieuTri: boolean, dai = 1600): string {
  const tu = [...new Set(tuKhoa.flatMap((k) => k.toLowerCase().split(/[^\p{L}\p{N}]+/u)).filter((w) => w.length >= 3))];
  const mucDT = hoiDieuTri ? chonMuc(van, HOI_CAP.test(tuKhoa.join(" ")), tu) : -1;
  if (mucDT >= 0) return van.slice(mucDT, mucDT + dai).trim();
  const thuong = van.toLowerCase();
  let tot = -1;
  let vt = 0;
  for (let i = 0; i < Math.max(1, van.length - 400); i += 250) {
    const c = thuong.slice(i, i + dai);
    if ((c.match(/\.{6,}|…{3,}/g) || []).length > 2) continue;
    let k = tu.filter((w) => c.includes(w)).length;
    if (hoiDieuTri) {
      k +=
        1.5 *
        Math.min(
          10,
          (c.match(/điều trị|xử trí|liều|truyền|bù dịch| mg |ml\/kg|treat|management|dose|recommend|therapy|fluid|khuyến cáo/g) || [])
            .length,
        );
    }
    if (k > tot) {
      tot = k;
      vt = i;
    }
  }
  return van.slice(vt, vt + dai).trim();
}

export function lienQuanChat(t: Omit<TaiLieu, "so">, tenBenhAnh: string, thuoc: string[], cauHoi: string): boolean {
  const ten = t.ten.toLowerCase();
  const tuBenh = tenBenhAnh
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((w) => w.length >= 4 && !TU_CHUNG_EN.has(w) && !/^(attack|acute|chronic|severe|disease|disorder|syndrome|infection)$/.test(w));
  const goc = (w: string) => w.slice(0, Math.max(5, w.length - 2));
  const chinh = tuChinhBenh(tenBenhAnh);
  const coBenh = tuBenh.length > 0 && !!chinh && ten.includes(goc(chinh));
  const coThuoc = thuoc.some((x) => x && ten.includes(goc(x.toLowerCase())));
  if (!coBenh && !coThuoc && (tuBenh.length || thuoc.length)) return false;
  const hoiTre = /(^|[^\p{L}])(trẻ|nhi|sơ sinh)(?!\p{L})|child|infant|pediatric|paediatric/iu.test(cauHoi);
  if (!hoiTre && /paediatric|pediatric|children|child|infant|neonat/.test(ten) && !/adult/.test(ten)) return false;
  return true;
}

export function lienQuan(t: Omit<TaiLieu, "so">, tuKhoa: string): boolean {
  const tu = tuKhoa
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((w) => w.length >= 4 && !TU_CHUNG_EN.has(w));
  if (!tu.length) return true;
  const van = `${t.ten} ${t.noiDung}`.toLowerCase();
  return tu.some((w) => van.includes(w.slice(0, Math.max(5, w.length - 2))));
}
