/**
 * KIỂM ĐỊNH SỐ LIỆU & ĐƠN VỊ Y KHOA (`chuanSo`, `soLech`).
 *
 * Nguyên tắc an toàn lâm sàng:
 *  1. Tuyệt đối KHÔNG biến số thập phân tiếng Anh (`0.125 mg`, `1.250 g`) thành `0125` / `1250`.
 *     Chỉ gộp dấu chấm phân cách nghìn khi chắc chắn là định dạng nghìn kiểu Việt (`100.000`, `1.000.000`,
 *     hoặc `[1-9].000` không đi trước đơn vị bậc lớn `g`/`kg`/`l`).
 *  2. Chuẩn hóa giá trị + đơn vị về cùng đại lượng cơ sở (`1 g = 1000 mg = 1_000_000 mcg`, `1 l = 1000 ml`,
 *     `1 g/kg = 1000 mg/kg = 1_000_000 mcg/kg`) để:
 *     - Không báo sai khi câu trả lời quy đổi đúng bậc (`1 g` ↔ `1000 mg`, `0.125 mg` ↔ `125 mcg`, `1.250 g` ↔ `1250 mg`).
 *     - Bắt buộc phát hiện lệch khi sai khác đơn vị hoặc sai bậc liều (`125 g` vs `125 mcg`, `50 mg` vs `50 ml`,
 *       `10 mg/kg` vs `10 mg`, `125 mg` vs `0.125 mg`).
 */

export type NhomDaiLuong =
  | "khoi_luong"
  | "khoi_luong_toc_do"
  | "lieu_cn"
  | "lieu_cn_toc_do"
  | "the_tich"
  | "the_tich_toc_do"
  | "the_tich_cn"
  | "mmol_l"
  | "mmol_mol"
  | "meq"
  | "meq_l"
  | "nong_do_kl"
  | "don_vi_qt"
  | "don_vi_qt_cn"
  | "don_vi_qt_the_tich"
  | "don_vi_qt_toc_do"
  | "don_vi_qt_cn_toc_do"
  | "ap_suat"
  | "phan_tram"
  | "nhiet_do_c";

interface ThongTinDonVi {
  nhom: NhomDaiLuong;
  heSo: number;
}

const PHUT = "(?:phút|phut|min|minutes?)";
const GIO = "(?:giờ|gio|h|hr|hours?)";

const BANG_DON_VI: ReadonlyArray<[RegExp, ThongTinDonVi]> = [
  // Tốc độ truyền theo cân nặng (quy về mcg/kg/giờ: 1 mcg/kg/phút = 60 mcg/kg/giờ)
  [new RegExp(`^(?:g|gam|gram)s?\\s*\\/\\s*kg\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "lieu_cn_toc_do", heSo: 60_000_000 }],
  [new RegExp(`^(?:g|gam|gram)s?\\s*\\/\\s*kg\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "lieu_cn_toc_do", heSo: 1_000_000 }],
  [new RegExp(`^(?:mg|miligam|milligram)s?\\s*\\/\\s*kg\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "lieu_cn_toc_do", heSo: 60_000 }],
  [new RegExp(`^(?:mg|miligam|milligram)s?\\s*\\/\\s*kg\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "lieu_cn_toc_do", heSo: 1_000 }],
  [new RegExp(`^(?:mcg|µg|μg|ug|microgam|microgram)s?\\s*\\/\\s*kg\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "lieu_cn_toc_do", heSo: 60 }],
  [new RegExp(`^(?:mcg|µg|μg|ug|microgam|microgram)s?\\s*\\/\\s*kg\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "lieu_cn_toc_do", heSo: 1 }],
  // Tốc độ truyền đơn vị quốc tế theo cân nặng & độc lập
  [new RegExp(`^(?:iu|ui|đvqt|units?)\\s*\\/\\s*kg\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "don_vi_qt_cn_toc_do", heSo: 60 }],
  [new RegExp(`^(?:iu|ui|đvqt|units?)\\s*\\/\\s*kg\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "don_vi_qt_cn_toc_do", heSo: 1 }],
  [new RegExp(`^(?:iu|ui|đvqt|units?)\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "don_vi_qt_toc_do", heSo: 60 }],
  [new RegExp(`^(?:iu|ui|đvqt|units?)\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "don_vi_qt_toc_do", heSo: 1 }],
  // Tốc độ truyền khối lượng (quy về mcg/giờ)
  [new RegExp(`^(?:g|gam|gram)s?\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "khoi_luong_toc_do", heSo: 60_000_000 }],
  [new RegExp(`^(?:g|gam|gram)s?\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "khoi_luong_toc_do", heSo: 1_000_000 }],
  [new RegExp(`^(?:mg|miligam|milligram)s?\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "khoi_luong_toc_do", heSo: 60_000 }],
  [new RegExp(`^(?:mg|miligam|milligram)s?\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "khoi_luong_toc_do", heSo: 1_000 }],
  [new RegExp(`^(?:mcg|µg|μg|ug|microgam|microgram)s?\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "khoi_luong_toc_do", heSo: 60 }],
  [new RegExp(`^(?:mcg|µg|μg|ug|microgam|microgram)s?\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "khoi_luong_toc_do", heSo: 1 }],
  // Tốc độ truyền thể tích / độ thanh thải (quy về ml/giờ)
  [new RegExp(`^(?:l|lít|lit|liter|litre)s?\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "the_tich_toc_do", heSo: 60_000 }],
  [new RegExp(`^(?:l|lít|lit|liter|litre)s?\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "the_tich_toc_do", heSo: 1_000 }],
  [new RegExp(`^(?:ml|mililit|milliliter|millilitre)s?\\s*\\/\\s*${PHUT}$`, "iu"), { nhom: "the_tich_toc_do", heSo: 60 }],
  [new RegExp(`^(?:ml|mililit|milliliter|millilitre)s?\\s*\\/\\s*${GIO}$`, "iu"), { nhom: "the_tich_toc_do", heSo: 1 }],
  // Liều theo cân nặng (g/kg, mg/kg, mcg/kg, IU/kg)
  [/^(?:g|gam|gram)s?\s*\/\s*kg$/iu, { nhom: "lieu_cn", heSo: 1_000_000 }],
  [/^(?:mg|miligam|milligram)s?\s*\/\s*kg$/iu, { nhom: "lieu_cn", heSo: 1_000 }],
  [/^(?:mcg|µg|μg|ug|microgam|microgram)s?\s*\/\s*kg$/iu, { nhom: "lieu_cn", heSo: 1 }],
  [/^(?:iu|ui|đvqt|units?)\s*\/\s*kg$/iu, { nhom: "don_vi_qt_cn", heSo: 1 }],
  // Thể tích theo cân nặng
  [/^(?:l|lít|lit|liter|litre)s?\s*\/\s*kg$/iu, { nhom: "the_tich_cn", heSo: 1_000 }],
  [/^(?:ml|mililit|milliliter|millilitre)s?\s*\/\s*kg$/iu, { nhom: "the_tich_cn", heSo: 1 }],
  // Nồng độ mol, đương lượng điện giải & HbA1c IFCC
  [/^mmol\s*\/\s*(?:l|lít|lit)$/iu, { nhom: "mmol_l", heSo: 1 }],
  [/^(?:µmol|μmol|umol|mcmol)\s*\/\s*(?:l|lít|lit)$/iu, { nhom: "mmol_l", heSo: 0.001 }],
  [/^mmol\s*\/\s*mol$/iu, { nhom: "mmol_mol", heSo: 1 }],
  [/^meq\s*\/\s*(?:l|lít|lit)$/iu, { nhom: "meq_l", heSo: 1 }],
  [/^meq$/iu, { nhom: "meq", heSo: 1 }],
  // Nồng độ khối lượng & nồng độ IU/mL
  [/^(?:iu|ui|đvqt|u|units?)\s*\/\s*ml$/iu, { nhom: "don_vi_qt_the_tich", heSo: 1 }],
  [/^(?:g|gam|gram)\s*\/\s*dl$/iu, { nhom: "nong_do_kl", heSo: 10_000 }],
  [/^(?:g|gam|gram)\s*\/\s*(?:l|lít|lit)$/iu, { nhom: "nong_do_kl", heSo: 1_000 }],
  [/^mg\s*\/\s*dl$/iu, { nhom: "nong_do_kl", heSo: 10 }],
  [/^(?:mg\s*\/\s*(?:l|lít|lit)|(?:mcg|µg|μg|ug)\s*\/\s*ml)$/iu, { nhom: "nong_do_kl", heSo: 1 }],
  // Khối lượng (quy về mcg: 1 g = 1_000 mg = 1_000_000 mcg)
  [/^(?:kg|kilogam|kilogram)s?$/iu, { nhom: "khoi_luong", heSo: 1_000_000_000 }],
  [/^(?:g|gam|gram)s?$/iu, { nhom: "khoi_luong", heSo: 1_000_000 }],
  [/^(?:mg|miligam|milligram)s?$/iu, { nhom: "khoi_luong", heSo: 1_000 }],
  [/^(?:mcg|µg|μg|ug|microgam|microgram)s?$/iu, { nhom: "khoi_luong", heSo: 1 }],
  [/^(?:ng|nanogam|nanogram)s?$/iu, { nhom: "khoi_luong", heSo: 0.001 }],
  // Thể tích (quy về ml: 1 l = 1_000 ml)
  [/^(?:l|lít|lit|liter|litre)s?$/iu, { nhom: "the_tich", heSo: 1_000 }],
  [/^(?:ml|mililit|milliliter|millilitre)s?$/iu, { nhom: "the_tich", heSo: 1 }],
  // Đơn vị quốc tế, áp suất, phần trăm, nhiệt độ
  [/^(?:iu|ui|đvqt|units?|đơn\s*vị)$/iu, { nhom: "don_vi_qt", heSo: 1 }],
  [/^mmhg$/iu, { nhom: "ap_suat", heSo: 1 }],
  [/^%$/u, { nhom: "phan_tram", heSo: 1 }],
  [/^(?:°c|độ\s*c)$/iu, { nhom: "nhiet_do_c", heSo: 1 }],
];

function traDonVi(raw?: string): ThongTinDonVi | null {
  if (!raw) return null;
  const sach = raw.trim().replace(/\s+/g, " ");
  for (const [re, info] of BANG_DON_VI) {
    if (re.test(sach)) return info;
  }
  return null;
}

/**
 * Chuẩn hóa dấu so sánh và dấu phân cách số học an toàn (không làm hỏng số thập phân `0.125` hay `1.250 g`).
 */
export function chuanSo(van: string): string {
  return (
    String(van ?? "")
      .normalize("NFC")
      .toLowerCase()
      // "từ 50 đến 100" là khoảng giá trị, không phải bất đẳng thức ≥50
      .replace(
        /(?:greater than or equal to|at least|không dưới|ít nhất|(?:minimum|tối thiểu)(?:\s+[\p{L}/]+){0,3}\s*(?:is|là|:|=)?)\s+(?=\d)/gu,
        "≥",
      )
      .replace(
        /(?<![\p{L}])từ\s+(?=\d+(?:[.,]\d+)?(?![\d.,]|\s*(?:[\p{L}%µμ°/]+\s+)?(?:đến|tới|[-–—~])))/gu,
        "≥",
      )
      .replace(
        /(?:less than or equal to|at most|up to|không quá|(?:maximum|max\.?|tối đa)(?:\s+[\p{L}/]+){0,3}\s*(?:is|là|:|=)?)\s+(?=\d)/gu,
        "≤",
      )
      .replace(/(greater than|more than|higher than|above|over|exceeding|trên|lớn hơn|cao hơn|hơn)\s+(?=\d)/g, ">")
      .replace(/(less than|lower than|below|under|dưới|nhỏ hơn|thấp hơn|chưa tới)\s+(?=\d)/g, "<")
      .replace(/>=/g, "≥")
      .replace(/<=/g, "≤")
      // 1.250,5 -> 1250.5; 1,250.5 -> 1250.5
      .replace(/(?<![\d.,])(\d{1,3}(?:\.\d{3})+),(\d+)(?![\d.,])/g, (_m, nguyen: string, le: string) => `${nguyen.replace(/\./g, "")}.${le}`)
      .replace(/(?<![\d.,])(\d{1,3}(?:,\d{3})+)\.(\d+)(?![\d.,])/g, (_m, nguyen: string, le: string) => `${nguyen.replace(/,/g, "")}.${le}`)
      // Nhiều nhóm nghìn liên tiếp: 1.000.000 -> 1000000; 1,000,000 -> 1000000
      .replace(/(?<![\d.])\d{1,3}(?:\.\d{3}){2,}(?![\d.])/g, (m) => m.replace(/\./g, ""))
      .replace(/(?<![\d,])\d{1,3}(?:,\d{3}){2,}(?![\d,])/g, (m) => m.replace(/,/g, ""))
      // Dấu chấm phân cách nghìn kiểu Việt:
      //  - 2–3 chữ số trước dấu chấm (10.000 .. 999.999), không đứng trước đơn vị bậc lớn g/kg/l/mmol/meq
      //  - Hoặc [1-9].xx0 (vd 1.000 mg, 1.500 mg/ngày, 2.400 mg, 5.000 IU), KHÔNG áp dụng cho 0.xxx, 1.125 mg hay 1.250 g!
      .replace(/(?<![\d.])([1-9]\d{1,2})\.(\d{3})(?![\d.])(?!\s*(?:g|gam|gram|kg|l|lít|lit|mmol|mol|meq)(?![\p{L}]))/gu, "$1$2")
      .replace(/(?<![\d.])([1-9])\.(\d{2}0)(?![\d.])(?!\s*(?:g|gam|gram|kg|l|lít|lit|mmol|mol|meq)(?![\p{L}]))/gu, "$1$2")
      // Dấu phẩy phân cách nghìn kiểu Anh:
      //  - 10,000 .. 999,999 hoặc [1-9],000 (không đi trước g/kg/l), hoặc [1-9],ddd trước mg/mcg/ml/iu
      .replace(/(?<![\d,])([1-9]\d{1,2}),(\d{3})(?![\d,])(?!\s*(?:g|gam|gram|kg|l|lít|lit|mmol|mol|meq)(?![\p{L}]))/gu, "$1$2")
      .replace(/(?<![\d,])([1-9]),000(?![\d,])(?!\s*(?:g|gam|gram|kg|l|lít|lit|mmol|mol|meq)(?![\p{L}]))/gu, "$1000")
      .replace(/(?<![\d,])([1-9]),(\d{3})(?=\s*(?:mg|mcg|µg|μg|ug|ml|iu|ui|đvqt|units?)(?![\p{L}]))/gu, "$1$2")
      // Dấu phẩy thập phân kiểu Việt/Pháp còn lại: 0,125 -> 0.125; 1,25 -> 1.25; 0,5 -> 0.5
      .replace(/(\d),(\d)/g, "$1.$2")
      // Tách khoảng trắng giữa toán tử so sánh và chữ số
      .replace(/([<>≤≥])\s+(?=\d)/g, "$1")
  );
}

const MAU_DON_VI =
  "(?:" +
  `(?:mg|miligam|milligrams?|mcg|µg|μg|ug|microgam|micrograms?|g|gam|grams?)\\s*\\/\\s*kg\\s*\\/\\s*(?:${PHUT}|${GIO})` +
  `|(?:iu|ui|đvqt|units?)\\s*\\/\\s*kg\\s*\\/\\s*(?:${PHUT}|${GIO})` +
  `|(?:iu|ui|đvqt|units?)\\s*\\/\\s*(?:${PHUT}|${GIO})` +
  `|(?:mg|miligam|milligrams?|mcg|µg|μg|ug|microgam|micrograms?|g|gam|grams?)\\s*\\/\\s*(?:${PHUT}|${GIO})` +
  `|(?:ml|mililit|milliliters?|millilitres?|lít|lit|liters?|litres?|l)\\s*\\/\\s*(?:${PHUT}|${GIO})` +
  "|(?:mg|miligam|milligrams?|mcg|µg|μg|ug|microgam|micrograms?|g|gam|grams?|lít|lit|liters?|litres?|l|ml|mililit|milliliters?|millilitres?)\\s*\\/\\s*kg" +
  "|(?:iu|ui|đvqt|units?)\\s*\\/\\s*kg" +
  "|(?:iu|ui|đvqt|u|units?)\\s*\\/\\s*ml" +
  "|mmol\\s*\\/\\s*(?:l|lít|lit)" +
  "|(?:µmol|μmol|umol|mcmol)\\s*\\/\\s*(?:l|lít|lit)" +
  "|mmol\\s*\\/\\s*mol" +
  "|meq\\s*\\/\\s*(?:l|lít|lit)" +
  "|(?:g|gam|gram|mg)\\s*\\/\\s*dl" +
  "|(?:g|gam|gram|mg)\\s*\\/\\s*(?:l|lít|lit)" +
  "|(?:mcg|µg|μg|ug)\\s*\\/\\s*ml" +
  "|(?:kg|kilogam|kilograms?|mg|miligam|milligrams?|mcg|µg|μg|ug|microgam|micrograms?|ng|nanogam|nanograms?|g|gam|grams?)" +
  "|(?:ml|mililit|milliliters?|millilitres?|lít|lit|liters?|litres?|l)" +
  "|meq" +
  "|(?:iu|ui|đvqt|units?|đơn\\s*vị|mmhg)" +
  "|°c|độ\\s*c|%" +
  ")";

const RE_TOKEN_SO = new RegExp(
  `([<>≤≥])?(\\d+(?:\\.\\d+)?)(?:\\s*(${MAU_DON_VI})(?![\\p{L}]))?`,
  "gu",
);

interface TokenSo {
  hienThi: string;
  dau: string;
  soChuoi: string;
  giaTri: number;
  donViChuoi: string;
  donVi: ThongTinDonVi | null;
  viTriDau: number;
  viTriCuoi: number;
}

function xapXiBang(a: number, b: number): boolean {
  const saiSo = Math.max(1e-9, Math.max(Math.abs(a), Math.abs(b)) * 1e-6);
  return Math.abs(a - b) <= saiSo;
}

function trichTokenSo(vanDaChuan: string): TokenSo[] {
  const ds: TokenSo[] = [];
  for (const m of vanDaChuan.matchAll(RE_TOKEN_SO)) {
    const dau = m[1] || "";
    const soChuoi = m[2];
    const donViChuoi = (m[3] || "").trim();
    const giaTri = Number(soChuoi);
    if (!Number.isFinite(giaTri)) continue;
    const donVi = traDonVi(donViChuoi);
    const viTriDau = m.index ?? 0;
    const viTriCuoi = viTriDau + m[0].length;
    ds.push({
      hienThi: donViChuoi ? `${dau}${soChuoi} ${donViChuoi}` : `${dau}${soChuoi}`,
      dau,
      soChuoi,
      giaTri,
      donViChuoi,
      donVi,
      viTriDau,
      viTriCuoi,
    });
  }

  // Lan truyền đơn vị ngược qua dải khoảng ("50–100 mg", "10 - 15 mg/kg", "50 đến 100 ml", "50 to 100 mg")
  for (let i = ds.length - 2; i >= 0; i--) {
    if (!ds[i].donVi && ds[i + 1].donVi) {
      const giua = vanDaChuan.slice(ds[i].viTriCuoi, ds[i + 1].viTriDau);
      if (/^\s*(?:[-–—~]|to|đến|tới|hoặc|hay|or)\s*$/iu.test(giua)) {
        ds[i].donVi = ds[i + 1].donVi;
        ds[i].donViChuoi = ds[i + 1].donViChuoi;
      }
    }
  }
  return ds;
}

function khopDau(dauY: string, dauNguon: string): boolean {
  if (!dauY) return true;
  if (dauY === "<" || dauY === "≤") return dauNguon === "<" || dauNguon === "≤";
  if (dauY === ">" || dauY === "≥") return dauNguon === ">" || dauNguon === "≥";
  return dauY === dauNguon;
}

/**
 * Tìm các con số / liều lượng trong `yNoi` không khớp hoặc sai đơn vị so với `vanNguon`.
 */
export function soLech(yNoi: string, vanNguon: string): string[] {
  const sachTrichDan = String(yNoi ?? "")
    .replace(/\((lượt|luot)[^)]*\)/gi, "")
    .replace(/\[\d+(,\s*\d+)*\]/g, "");
  const y = chuanSo(sachTrichDan);
  const nguon = chuanSo(vanNguon);

  const dsY = trichTokenSo(y);
  const dsNguon = trichTokenSo(nguon);
  const lech = new Set<string>();

  for (const t of dsY) {
    // Số 0 hoặc 1 đứng lẻ KHÔNG kèm dấu bất đẳng thức và KHÔNG kèm đơn vị đo lường ("1 lần", "bước 1") thì bỏ qua.
    // Nếu có đơn vị ("1 g", "1 mg", "1 ml") thì BẮT BUỘC kiểm tra!
    if (!t.dau && !t.donVi && !t.soChuoi.includes(".") && (t.giaTri === 0 || t.giaTri === 1)) {
      continue;
    }

    if (t.donVi) {
      const mucChuanY = t.giaTri * t.donVi.heSo;
      const khop = dsNguon.some((n) => {
        if (!n.donVi || n.donVi.nhom !== t.donVi!.nhom) return false;
        if (!xapXiBang(mucChuanY, n.giaTri * n.donVi.heSo)) return false;
        return khopDau(t.dau, n.dau);
      });
      if (!khop) lech.add(t.hienThi);
    } else {
      // Con số không có đơn vị vật lý trong bảng: đối chiếu giá trị số với các token tương ứng trong nguồn
      const khop = dsNguon.some((n) => {
        if (!xapXiBang(t.giaTri, n.giaTri)) return false;
        return khopDau(t.dau, n.dau);
      });
      if (!khop) lech.add(t.hienThi);
    }
  }

  return [...lech];
}
