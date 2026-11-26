/**
 * Hai tác tử luật tại chỗ: không gọi mô hình, không ra mạng, chỉ đọc mệnh đề đã trích.
 *  - "Chủ đề cần bàn": mục hồ sơ nào chưa có mệnh đề nào.
 *  - "Đối chiếu thuốc và dị ứng": thuốc trùng chất dị ứng, cùng thuốc khác liều, mục còn thiếu.
 */
import type { MenhDeVao } from "./an-danh";

export const CHU_DE: ReadonlyArray<{ ma: string; ten: string; mucLienQuan: string[] }> = [
  { ma: "ly_do", ten: "Lý do khám", mucLienQuan: ["LÝ DO KHÁM BỆNH"] },
  { ma: "benh_su", ten: "Bệnh sử hiện tại", mucLienQuan: ["BỆNH SỬ HIỆN TẠI"] },
  { ma: "tien_su", ten: "Tiền sử bệnh", mucLienQuan: ["TIỀN SỬ BỆNH"] },
  { ma: "thuoc", ten: "Thuốc đang dùng", mucLienQuan: ["THUỐC ĐANG DÙNG"] },
  { ma: "di_ung", ten: "Dị ứng", mucLienQuan: ["DỊ ỨNG"] },
  { ma: "gia_dinh", ten: "Tiền sử gia đình và xã hội", mucLienQuan: ["TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"] },
  { ma: "kham", ten: "Khám lâm sàng", mucLienQuan: ["KHÁM LÂM SÀNG"] },
];

/** Các mục hồ sơ biểu diễn thuốc đang dùng hoặc thuốc trong kế hoạch điều trị (loại trừ tuyệt đối DỊ ỨNG). */
const MUC_THUOC_DIEU_TRI: ReadonlySet<string> = new Set([
  "THUỐC ĐANG DÙNG",
  "KẾ HOẠCH ĐIỀU TRỊ",
  "THUỐC",
  "ĐIỀU TRỊ",
]);

export function chuDeCanBan(menhDe: MenhDeVao[]): {
  daBan: Array<{ ma: string; ten: string; soMenhDe: number }>;
  chuaBan: Array<{ ma: string; ten: string }>;
} {
  const daBan: Array<{ ma: string; ten: string; soMenhDe: number }> = [];
  const chuaBan: Array<{ ma: string; ten: string }> = [];
  for (const c of CHU_DE) {
    const so = (menhDe || []).filter((m) => c.mucLienQuan.includes(String(m?.section ?? ""))).length;
    if (so > 0) daBan.push({ ma: c.ma, ten: c.ten, soMenhDe: so });
    else chuaBan.push({ ma: c.ma, ten: c.ten });
  }
  return { daBan, chuaBan };
}

/**
 * Tách thông tin thuốc thành tên và liều:
 * Hỗ trợ cả định dạng chuỗi tự do ("amoxicillin 500 mg") LẪN định dạng có khoá của `menhDeChoGiaoDien`
 * ("ten Penicillin V, lieu 500 mg, so_lan 2 lần/ngày, trang_thai_dung đang dùng").
 */
function tachThuoc(s: string): { ten: string; lieu: string } {
  const g = s.trim().replace(/\s+/g, " ");
  const mTenKhoa = g.match(/(?:^|,\s*)ten\s+([^,]+)/iu);
  if (mTenKhoa) {
    const mLieuKhoa = g.match(/(?:^|,\s*)lieu\s+([^,]+)/iu);
    const tachTen = mTenKhoa[1].trim().match(/^(.*?)\s*(\d[\s\S]*)?$/u);
    const ten = (tachTen?.[1] ?? mTenKhoa[1]).trim().toLowerCase();
    const lieu = (mLieuKhoa?.[1] ?? tachTen?.[2] ?? "").trim().toLowerCase();
    return { ten, lieu };
  }
  const m = g.match(/^(.*?)\s*(\d[\s\S]*)?$/u);
  return { ten: (m?.[1] ?? g).trim().toLowerCase(), lieu: (m?.[2] ?? "").trim().toLowerCase() };
}

function laThuocDaNgung(rawDrug: string): boolean {
  return /(?:^|,\s*)trang_thai_dung\s+đã\s+ngừng(?=$|,)/iu.test(rawDrug);
}

function rutTenChatDiUng(rawDrug: string): string {
  const g = rawDrug.trim().replace(/\s+/g, " ");
  const mTenKhoa = g.match(/(?:^|,\s*)ten\s+([^,]+)/iu);
  return (mTenKhoa ? mTenKhoa[1] : g).trim();
}

export function doiChieuThuocDiUng(menhDe: MenhDeVao[]): { thuoc: string[]; diUng: string[]; mauThuan: string[]; thieu: string[] } {
  const ds = menhDe || [];
  // Chỉ gom thuốc đang dùng/điều trị từ các mục thuốc/điều trị; loại trừ hoàn toàn mục DỊ ỨNG, mệnh đề phủ định và thuốc đã ngừng.
  const thuoc = ds
    .map((m) => {
      const muc = String(m?.section ?? "").trim().toUpperCase();
      if (!m?.drug || m.negated === true || muc === "DỊ ỨNG" || !MUC_THUOC_DIEU_TRI.has(muc)) return "";
      const rawDrug = String(m.drug).trim();
      if (!rawDrug || laThuocDaNgung(rawDrug)) return "";
      return rawDrug;
    })
    .filter(Boolean);

  const mucDiUng = ds.filter((m) => String(m?.section ?? "").trim().toUpperCase() === "DỊ ỨNG");
  const diUng = mucDiUng
    .filter((m) => m.negated !== true)
    .map((m) => {
      const van = String(m.text ?? "").trim();
      const chat = rutTenChatDiUng(String(m.drug ?? ""));
      if (van && chat && !van.toLowerCase().includes(chat.toLowerCase())) return `${van} (${chat})`;
      return van || chat;
    })
    .filter(Boolean);

  const mauThuan: string[] = [];
  const lieuTheoTen = new Map<string, Set<string>>();
  for (const t of thuoc) {
    const { ten, lieu } = tachThuoc(t);
    if (!ten) continue;
    if (!lieuTheoTen.has(ten)) lieuTheoTen.set(ten, new Set());
    lieuTheoTen.get(ten)!.add(lieu);
  }
  for (const [ten, lieu] of lieuTheoTen) {
    if (lieu.size > 1) mauThuan.push(`${ten}: có ${lieu.size} liều khác nhau (${[...lieu].join("; ")})`);
  }
  const diUngThap = diUng.map((d) => d.toLowerCase());
  const daBao = new Set<string>();
  for (const t of thuoc) {
    const { ten } = tachThuoc(t);
    if (ten.length < 3 || daBao.has(ten)) continue;
    const dau = ten.split(" ")[0]; // "penicillin v" -> "penicillin"
    const trung = diUngThap.find((d) => d.includes(ten) || (dau.length >= 4 && d.includes(dau)));
    if (trung !== undefined) {
      daBao.add(ten);
      mauThuan.push(`${ten}: trùng mục dị ứng ("${diUng[diUngThap.indexOf(trung)]}")`);
    }
  }

  const thieu: string[] = [];
  if (mucDiUng.length === 0) thieu.push("chưa có mục dị ứng");
  if (!ds.some((m) => MUC_THUOC_DIEU_TRI.has(String(m?.section ?? "").trim().toUpperCase()))) {
    thieu.push("chưa có thuốc đang dùng");
  }
  return { thuoc, diUng, mauThuan, thieu };
}
