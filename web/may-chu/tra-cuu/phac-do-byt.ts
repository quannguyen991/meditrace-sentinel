/**
 * THƯ VIỆN PHÁC ĐỒ BỘ Y TẾ LƯU TẠI MÁY (data/phac-do/doan.jsonl).
 */
import fs from "fs";
import path from "path";
import type { TaiLieu } from "./tu-dien";

type TrangPhacDo = {
  ma: string;
  tieu_de: string;
  nam: number | null;
  trang: number;
  van: string;
  noi_dang?: string;
  url_trang: string;
  url_pdf: string;
  tu: Map<string, number>;
  cap: Set<string>;
  tuTen: Set<string>;
};

const TU_DUNG_VI = new Set([
  "và", "của", "cho", "là", "có", "không", "thế", "nào", "bao", "nhiêu", "gì", "những",
  "các", "một", "được", "trong", "với", "theo", "khi", "thì", "này", "đó", "như", "để", "từ", "hay", "hoặc", "nên",
  "cần", "ở", "ra", "vào", "trên", "dưới", "bị", "người", "bệnh", "nhân",
]);

export function suaPhong(s: string): string {
  return s.normalize("NFC").replace(/ƣ/g, "ư").replace(/Ƣ/g, "Ư");
}

export function tuViet(s: string): string[] {
  return suaPhong(s).toLowerCase().match(/[\p{L}\p{N}]+/gu) || [];
}

function laTrangPhu(van: string): boolean {
  const v = van.slice(0, 600).toUpperCase();
  return (
    /MỤC LỤC|LỜI NÓI ĐẦU|LỜI GIỚI THIỆU|BAN BIÊN SOẠN|CỘNG HOÀ XÃ HỘI|CỘNG HÒA XÃ HỘI|DANH MỤC CHỮ VIẾT TẮT/.test(v) ||
    (van.match(/\.{8,}/g) || []).length >= 5
  );
}

let PHAC_DO: TrangPhacDo[] = [];
const IDF = new Map<string, number>();

export function napPhacDo(): void {
  const tep = path.join(process.cwd(), "data", "phac-do", "doan.jsonl");
  PHAC_DO = [];
  IDF.clear();
  if (!fs.existsSync(tep)) return;
  const df = new Map<string, number>();
  for (const dong of fs.readFileSync(tep, "utf-8").split("\n")) {
    if (!dong.trim()) continue;
    const d = JSON.parse(dong);
    d.van = suaPhong(d.van);
    d.tieu_de = suaPhong(d.tieu_de);
    const t = tuViet(d.van);
    const tu = new Map<string, number>();
    for (const w of t) tu.set(w, (tu.get(w) || 0) + 1);
    const cap = new Set<string>();
    for (let i = 0; i + 1 < t.length; i++) cap.add(`${t[i]} ${t[i + 1]}`);
    const tuTen = new Set(tuViet(d.tieu_de));
    for (const k of new Set([...tu.keys(), ...cap])) df.set(k, (df.get(k) || 0) + 1);
    PHAC_DO.push({ ...d, tu, cap, tuTen });
  }
  for (const [k, n] of df) IDF.set(k, Math.log(1 + PHAC_DO.length / n));
  const soVb = new Set(PHAC_DO.map((p) => p.ma)).size;
  console.log(`Thư viện phác đồ Bộ Y tế: ${soVb} văn bản, ${PHAC_DO.length} trang`);
}

napPhacDo();

export function tenGon(t: string): string {
  const qd = t.match(/(\d+\/QĐ-BYT)/)?.[1];
  const m = t.match(/[“"]([^”"]+)[”"]/) || t.match(/(Hướng dẫn.*)$/i);
  const ten = (m ? m[1] : t).trim();
  return qd && !ten.includes(qd) ? `${ten} (QĐ ${qd})` : ten;
}

export function gonTenBenh(k: string): string {
  return tuViet(k)
    .join(" ")
    .replace(/^((phác đồ|hướng dẫn|điều trị|chẩn đoán|xử trí|bệnh|cơn|đợt cấp|đợt|hội chứng)\s+)+/, "")
    .replace(/^(và\s+)+/, "")
    .replace(/(\s+(cấp tính|mạn tính|cấp|mạn|nặng|nhẹ|ở|người lớn|trẻ em|nguy kịch|có dấu hiệu cảnh báo))+$/, "");
}

export function soVanBanPhacDo(): number {
  return new Set(PHAC_DO.map((x) => x.ma)).size;
}

export function mucLucPhacDo(): Array<{ tieu_de: string; nam: number | null; so_trang: number; url: string }> {
  const theoMa = new Map<string, { tieu_de: string; nam: number | null; so_trang: number; url: string }>();
  for (const p of PHAC_DO) {
    const cu = theoMa.get(p.ma);
    theoMa.set(p.ma, { tieu_de: p.tieu_de, nam: p.nam, so_trang: Math.max(cu?.so_trang || 0, p.trang), url: p.url_trang });
  }
  return [...theoMa.values()].sort((a, b) => (b.nam || 0) - (a.nam || 0));
}

export function timPhacDo(cauHoi: string, tuKhoaViet: string[]): Omit<TaiLieu, "so">[] {
  if (!PHAC_DO.length) return [];
  const tuHoi = tuViet(`${cauHoi} ${tuKhoaViet.join(" ")}`).filter((w) => !TU_DUNG_VI.has(w));
  const capHoi = new Set<string>();
  const tHoi = tuViet(`${cauHoi} ${tuKhoaViet.join(" ")}`);
  for (let i = 0; i + 1 < tHoi.length; i++) capHoi.add(`${tHoi[i]} ${tHoi[i + 1]}`);
  const tenBenh = tuKhoaViet.flatMap((k) => tuViet(k)).filter((w) => !TU_DUNG_VI.has(w));
  const cumBenh = tuKhoaViet.map(gonTenBenh).filter((c) => c.length >= 2);
  const diem = PHAC_DO.map((p) => {
    let s = 0;
    for (const w of new Set(tuHoi)) if (p.tu.has(w)) s += (IDF.get(w) || 0) * Math.log(1 + p.tu.get(w)!);
    for (const c of capHoi) if (p.cap.has(c)) s += 2 * (IDF.get(c) || 0);
    const trungTen = tenBenh.filter((w) => p.tuTen.has(w)).length;
    if (tenBenh.length) s *= 1 + trungTen / tenBenh.length;
    if (p.nam) s *= 1 + Math.max(0, Math.min(16, p.nam - 2010)) * 0.015;
    const vanThuong = p.van.toLowerCase();
    const coTenBenh =
      !cumBenh.length ||
      cumBenh.some((c) => {
        const tu = c.split(" ");
        if (tu.every((w) => p.tuTen.has(w))) return true;
        let n = 0;
        let i = vanThuong.indexOf(c);
        while (i >= 0 && n < 2) {
          n++;
          i = vanThuong.indexOf(c, i + c.length);
        }
        return n >= 2;
      });
    return { p, s: coTenBenh ? (laTrangPhu(p.van) ? s * 0.15 : s) : 0 };
  })
    .filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s);
  if (!diem.length || diem[0].s < 8) return [];
  const ra: Omit<TaiLieu, "so">[] = [];
  const vb = new Set<string>();
  const daCo = new Set<string>();
  for (const { p, s } of diem) {
    if (s < diem[0].s * 0.45) break;
    const khoaTrung = p.van.slice(0, 300);
    if (daCo.has(khoaTrung)) continue;
    daCo.add(khoaTrung);
    if (!vb.has(p.ma) && vb.size >= 2) continue;
    vb.add(p.ma);
    const van = p.van;
    let tot = 0;
    let viTri = 0;
    for (let i = 0; i < van.length; i += 200) {
      const cua = van.slice(i, i + 1800).toLowerCase();
      const k = [...capHoi].filter((c) => cua.includes(c)).length * 2 + tuHoi.filter((w) => cua.includes(w)).length;
      if (k > tot) {
        tot = k;
        viTri = i;
      }
    }
    let noiDung = van.slice(viTri, viTri + 1800);
    let trangCuoi = p.trang;
    if (!ra.length) {
      const sau = PHAC_DO.find((x) => x.ma === p.ma && x.trang === p.trang + 1);
      if (sau) {
        noiDung = `${noiDung}\n[trang ${p.trang + 1}] ${sau.van.slice(0, 2200)}`;
        trangCuoi = p.trang + 1;
      }
    }
    ra.push({
      nguon: "Phác đồ BYT",
      ten: `${tenGon(p.tieu_de)} — trang ${p.trang}${trangCuoi !== p.trang ? `–${trangCuoi}` : ""}`,
      url: /\.pdf($|\?)/i.test(p.url_pdf) ? `${p.url_pdf}#page=${p.trang}` : p.url_trang,
      nam: p.nam ? String(p.nam) : undefined,
      loai: `phác đồ Bộ Y tế (toàn văn) · nơi đăng: ${p.noi_dang || "Cục Quản lý Khám, chữa bệnh (kcb.vn)"}`,
      noiDung,
    });
    if (ra.length >= 3) break;
  }
  return ra;
}
