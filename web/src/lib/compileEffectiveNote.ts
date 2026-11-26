import type { DocumentTabItem, SignOffRecord } from "../types";
import { ghepMenhDe } from "./ghepMenhDe";

export type QuyetDuyet = "cho" | "giu" | "sua" | "bo";

export interface MenhDeBienDich {
  id: number;
  text: string;
  gateReason?: string | null;
  status?: "than" | "can_xac_nhan" | string;
  stateD?: string | null;
}

export type LuotThoai = { so: number; vai: string; chu: string };

/** Lời thoại → từng lượt (đánh số từ 1, như máy dẫn), tách vai ở đầu dòng. */
export function tachLuot(transcript?: string): LuotThoai[] {
  return (transcript || "")
    .split("\n")
    .filter((x) => x.trim())
    .map((d, i) => {
      const m = d.trim().match(/^([^:]{2,20}):\s*(.*)$/);
      return { so: i + 1, vai: m ? m[1].trim() : "", chu: m ? m[2] : d.trim() };
    });
}

/** Trạng thái cần bác sĩ xác nhận theo chính sách D (nếu có) hoặc mục bản nháp C. */
export function canXacNhan(p: { stateD?: string | null; status?: string }): boolean {
  return p.stateD ? p.stateD === "cần xác nhận" : p.status === "can_xac_nhan";
}

/** Dòng tiêu đề mục: viết hoa toàn bộ và ngắn ("LÝ DO KHÁM BỆNH", "CẦN XÁC NHẬN"), hoặc "## …". */
export function laTieuDeMuc(dong: string): boolean {
  const t = dong.trim();
  if (!t) return false;
  if (/^#{1,4}\s+\S/.test(t)) return true;
  return t.length <= 60 && /\p{Lu}/u.test(t) && t === t.toLocaleUpperCase("vi") && !/[.;]$/.test(t);
}

function laTieuDeCanXacNhan(dong: string): boolean {
  const sach = dong.trim().replace(/^#{1,4}\s*/, "").trim();
  return /^CẦN\s+(?:BÁC\s+SĨ\s+)?XÁC\s+NHẬN$/iu.test(sach);
}

function laTieuDeGocBenhAn(dong: string): boolean {
  return /^#\s+(?:BỆNH\s+ÁN|HỒ\s+SƠ\s+BỆNH\s+ÁN|SOAP\b)/iu.test(dong.trim());
}

function laDuongKeNgang(dong: string): boolean {
  return /^---+|^___+|^\*\*\*+$/.test(dong.trim());
}

function conChuLamSang(dong: string): boolean {
  const boDauDong = dong
    .replace(/^\s*(?:[-*•]+|\d+[.)])\s*/, "")
    .replace(/\[T\d+(?:,\s*T\d+)*\]/g, "")
    .trim();
  return /[\p{L}\p{N}]/u.test(boDauDong);
}

function coNoiDungDuoiTieuDe(cacDong: string[], chiSoTieuDe: number): boolean {
  for (let j = chiSoTieuDe + 1; j < cacDong.length; j++) {
    const d = cacDong[j];
    if (!d.trim()) continue;
    if (laTieuDeMuc(d) || laDuongKeNgang(d)) return false;
    if (conChuLamSang(d)) return true;
  }
  return false;
}

/**
 * Biên dịch văn bản bệnh án hiệu lực từ `rawContent` và các quyết định duyệt mệnh đề:
 * - `"sua"`: thay câu gốc bằng `banSuaDuyet[id]` (nếu bác sĩ đổi về `"giu"` thì giữ nguyên câu gốc).
 * - `"bo"`: loại câu/dòng mệnh đề bị bác sĩ bác bỏ khỏi văn bản xuất (Sao chép, .txt, .md, In A4).
 */
export function compileEffectiveNote(
  rawContent: string,
  propositions: MenhDeBienDich[] | null | undefined,
  quyetDuyet: Record<number, QuyetDuyet> | null | undefined,
  banSuaDuyet: Record<number, string> | null | undefined,
): string {
  if (!rawContent) return "";
  const ds = Array.isArray(propositions) ? propositions : [];
  const quyet = quyetDuyet || {};
  const banSua = banSuaDuyet || {};

  const coThayDoi = ds.some((p) => {
    const q = quyet[p.id];
    return q === "bo" || (q === "sua" && Boolean(banSua[p.id]?.trim()));
  });
  if (!coThayDoi) return rawContent;

  const propById = new Map<number, MenhDeBienDich>(ds.map((p) => [p.id, p]));
  const ghep = ghepMenhDe(
    rawContent,
    ds.map((p) => ({
      id: p.id,
      text: p.text,
    })),
    laTieuDeMuc,
  );

  const cacDong = rawContent.split("\n");

  // Bổ sung khớp nguyên văn cho các vị trí nhân bản chưa có chủ (VD: sinh_benh_an.py chép câu đầu của
  // BỆNH SỬ HIỆN TẠI lên LÝ DO KHÁM BỆNH dưới cùng một mã mệnh đề duy nhất).
  const cacMenhDeTacDong = [...ds]
    .filter((p) => {
      const q = quyet[p.id];
      return (q === "bo" || (q === "sua" && Boolean(banSua[p.id]?.trim()))) && Boolean(p.text?.trim());
    })
    .sort((a, b) => b.text.trim().length - a.text.trim().length);

  for (const md of cacMenhDeTacDong) {
    const t = md.text.trim();
    for (let i = 0; i < cacDong.length; i++) {
      if (laTieuDeMuc(cacDong[i])) continue;
      let vt = cacDong[i].indexOf(t);
      while (vt >= 0) {
        const kt = vt + t.length;
        const sau = cacDong[i].slice(kt).trimStart();
        const daBiChiem = (ghep.get(i) || []).some((d) => vt < d.kt && kt > d.bd);
        if ((sau === "" || /^(?:[.—–,;:)]|\[T\d)/.test(sau)) && !daBiChiem) {
          const hienCo = ghep.get(i) || [];
          ghep.set(
            i,
            [...hienCo, { bd: vt, kt, id: md.id, ganDung: false, doGiong: 1 }].sort((a, b) => a.bd - b.bd),
          );
        }
        vt = cacDong[i].indexOf(t, vt + 1);
      }
    }
  }

  type DongTam = { text: string; laTieuDeCoNoiDungGoc: boolean };
  const dongKetQua: DongTam[] = [];

  for (let i = 0; i < cacDong.length; i++) {
    const dongGoc = cacDong[i];
    const laTieuDe = laTieuDeMuc(dongGoc) && !laTieuDeGocBenhAn(dongGoc);
    const laTieuDeCoNoiDungGoc =
      laTieuDe && (laTieuDeCanXacNhan(dongGoc) || coNoiDungDuoiTieuDe(cacDong, i));

    const doan = ghep.get(i);
    if (!doan || doan.length === 0) {
      dongKetQua.push({ text: dongGoc, laTieuDeCoNoiDungGoc });
      continue;
    }

    const coTacDongDongNay = doan.some((d) => {
      const q = quyet[d.id];
      return q === "bo" || (q === "sua" && Boolean(banSua[d.id]?.trim()));
    });
    if (!coTacDongDongNay) {
      dongKetQua.push({ text: dongGoc, laTieuDeCoNoiDungGoc });
      continue;
    }

    // Áp dụng từ phải sang trái để không lệch chỉ số bd/kt trên cùng một dòng
    let dongMoi = dongGoc;
    const xepNguoc = [...doan].sort((a, b) => b.bd - a.bd);
    for (const d of xepNguoc) {
      const q = quyet[d.id];
      const prop = propById.get(d.id);
      if (q === "sua" && banSua[d.id]?.trim()) {
        const chuMoi = banSua[d.id].trim();
        let bdThay = d.bd;
        let ktThay = d.kt;
        if (d.ganDung) {
          const doanCu = dongMoi.slice(bdThay, ktThay);
          const mDauBullet = doanCu.match(/^(?:[-*•]+|\d+[.)])\s+/);
          if (mDauBullet && !/^(?:[-*•]+|\d+[.)])\s+/.test(chuMoi)) {
            bdThay += mDauBullet[0].length;
          }
          const mDuoiTrichDan = dongMoi.slice(bdThay, ktThay).match(/\s*(?:\[T\d+(?:,\s*T\d+)*\])+$/);
          if (mDuoiTrichDan && !/\[T\d+/.test(chuMoi)) {
            ktThay -= mDuoiTrichDan[0].length;
          }
        }
        if (prop?.gateReason) {
          const hauToLyDo = ` — ${prop.gateReason}`;
          if (dongMoi.slice(ktThay).startsWith(hauToLyDo)) {
            ktThay += hauToLyDo.length;
          }
        }
        const phanSau = dongMoi.slice(ktThay);
        const chuChuan = /[.;?!]$/.test(chuMoi) && /^[.;?!]/.test(phanSau) ? chuMoi.slice(0, -1) : chuMoi;
        dongMoi = dongMoi.slice(0, bdThay) + chuChuan + phanSau;
      } else if (q === "bo") {
        let bdXoa = d.bd;
        let ktXoa = d.kt;
        const phanConLai = dongMoi.slice(ktXoa);
        // Nuốt luôn nhãn trích dẫn [T...], giải thích cổng " — ...", và dấu kết câu liền sau
        const mMoRong = phanConLai.match(
          /^(?:\s*\[T\d+(?:,\s*T\d+)*\])*(?:\s+[—–-]\s+[^.;?!\n]+)?(?:\s*\[T\d+(?:,\s*T\d+)*\])*(?:[.;]\s*|\s*$)/,
        );
        if (mMoRong) {
          ktXoa += mMoRong[0].length;
        }
        const duoiBiXoaKetCham = /\.\s*$/.test(dongMoi.slice(bdXoa, ktXoa));
        let dauChamBu = "";
        // Nếu xoá chạm cuối dòng thì dọn khoảng trắng hoặc dấu phẩy / chấm phẩy thừa phía trước
        if (ktXoa >= dongMoi.length) {
          const truoc = dongMoi.slice(0, bdXoa);
          const mTruocPhay = truoc.match(/[,;]\s*$/);
          if (mTruocPhay) {
            bdXoa -= mTruocPhay[0].length;
            const conLaiTruoc = dongMoi.slice(0, bdXoa);
            if (duoiBiXoaKetCham && conChuLamSang(conLaiTruoc) && !/[.?!]$/.test(conLaiTruoc.trimEnd())) {
              dauChamBu = ".";
            }
          } else {
            const mTruocTrang = truoc.match(/(?<=[.?!])\s+$/);
            if (mTruocTrang) bdXoa -= mTruocTrang[0].length;
          }
        }
        dongMoi = dongMoi.slice(0, bdXoa) + dauChamBu + dongMoi.slice(ktXoa);
      }
    }

    if (conChuLamSang(dongMoi)) {
      dongKetQua.push({ text: dongMoi.replace(/[ \t]{2,}/g, " ").trimEnd(), laTieuDeCoNoiDungGoc: false });
    }
  }

  // Nếu một mục vốn có nội dung (VD: CẦN XÁC NHẬN, LÝ DO KHÁM BỆNH, TIỀN SỬ GIA ĐÌNH...) bị bác sĩ "Bỏ"
  // sạch hết các dòng bên dưới thì ẩn luôn tiêu đề rỗng đó (nhưng bảo toàn các mục mẫu vốn trống từ đầu).
  const dongDaDon: string[] = [];
  const danhSachText = dongKetQua.map((x) => x.text);
  for (let i = 0; i < dongKetQua.length; i++) {
    if (dongKetQua[i].laTieuDeCoNoiDungGoc && !coNoiDungDuoiTieuDe(danhSachText, i)) {
      let j = i + 1;
      while (j < dongKetQua.length && !dongKetQua[j].text.trim()) j++;
      i = j - 1;
      continue;
    }
    dongDaDon.push(dongKetQua[i].text);
  }

  return dongDaDon
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trimEnd();
}

/**
 * Chọn đúng nội dung bệnh án lâm sàng gốc (SOAP / Bản nháp hồ sơ) để băm ký duyệt pháp lý WORM.
 * Tuyệt đối KHÔNG băm nhầm tab tờ dặn dò ("leaflet"), lời thoại ("transcript") hay ngữ cảnh ("context").
 */
export function layNoiDungBenhAnDeBam(
  tabs: DocumentTabItem[] | null | undefined,
  activeTabId?: string,
  noteMetaContent?: string | null,
): string {
  const dsTab = Array.isArray(tabs) ? tabs : [];
  const active = dsTab.find((t) => t.id === activeTabId);

  // Nếu đang đứng ở tab SOAP hoặc tab Bản nháp hồ sơ (không phải leaflet/transcript/context)
  if (active && active.type === "soap") {
    return active.content || "";
  }
  if (
    active &&
    active.type === "custom" &&
    (active.title === "Bản nháp hồ sơ" || (noteMetaContent && active.content === noteMetaContent))
  ) {
    return active.content || "";
  }

  // Ưu tiên bản nháp hồ sơ mới nhất nếu có, sau đó tới tab SOAP chuẩn của ca khám
  const tabBanNhap = [...dsTab]
    .reverse()
    .find(
      (t) =>
        t.type === "custom" &&
        (t.title === "Bản nháp hồ sơ" || (Boolean(noteMetaContent) && t.content === noteMetaContent)),
    );
  if (tabBanNhap) return tabBanNhap.content || "";

  const tabSoap = dsTab.find((t) => t.type === "soap");
  if (tabSoap) return tabSoap.content || "";

  return noteMetaContent || "";
}

/** Chuỗi chuẩn hoá tất định (canonical JSON) trên nội dung bệnh án gốc + trạng thái duyệt mệnh đề. */
export function buildSignOffCanonicalPayload(
  soapRawContent: string,
  quyetDuyet: Record<number, QuyetDuyet> | null | undefined,
  banSuaDuyet: Record<number, string> | null | undefined,
): string {
  const q = quyetDuyet || {};
  const b = banSuaDuyet || {};

  const quyetChuan: Array<[number, QuyetDuyet]> = Object.keys(q)
    .map((k) => Number(k))
    .filter((id) => Number.isFinite(id) && q[id] && q[id] !== "cho")
    .sort((x, y) => x - y)
    .map((id) => [id, q[id]]);

  const suaChuan: Array<[number, string]> = quyetChuan
    .filter(([, trangThai]) => trangThai === "sua")
    .map(([id]) => [id, (b[id] || "").trim()] as [number, string])
    .filter(([, van]) => van.length > 0);

  return JSON.stringify({
    v: 1,
    soap: (soapRawContent || "").replace(/\r\n/g, "\n"),
    quyet: quyetChuan,
    banSua: suaChuan,
  });
}

// ============================================================================
// SHA-256 Mật mã học chuẩn FIPS 180-4 (crypto.subtle + fallback thuần TypeScript)
// ============================================================================

const SHA256_K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);

function rotr(x: number, n: number): number {
  return (x >>> n) | (x << (32 - n));
}

/** Băm SHA-256 đồng bộ thuần TypeScript (chuẩn FIPS 180-4) — chạy được cả trên HTTP LAN nội bộ không có WebCrypto. */
export function sha256HexSync(input: string): string {
  const bytes = new TextEncoder().encode(input);
  const bitLen = bytes.length * 8;
  const totalLen = (((bytes.length + 9 + 63) >> 6) << 6);
  const buf = new Uint8Array(totalLen);
  buf.set(bytes);
  buf[bytes.length] = 0x80;

  const view = new DataView(buf.buffer);
  view.setUint32(totalLen - 8, Math.floor(bitLen / 0x100000000), false);
  view.setUint32(totalLen - 4, bitLen >>> 0, false);

  let h0 = 0x6a09e667;
  let h1 = 0xbb67ae85;
  let h2 = 0x3c6ef372;
  let h3 = 0xa54ff53a;
  let h4 = 0x510e527f;
  let h5 = 0x9b05688c;
  let h6 = 0x1f83d9ab;
  let h7 = 0x5be0cd19;

  const W = new Uint32Array(64);

  for (let offset = 0; offset < totalLen; offset += 64) {
    for (let i = 0; i < 16; i++) {
      W[i] = view.getUint32(offset + i * 4, false);
    }
    for (let i = 16; i < 64; i++) {
      const s0 = rotr(W[i - 15], 7) ^ rotr(W[i - 15], 18) ^ (W[i - 15] >>> 3);
      const s1 = rotr(W[i - 2], 17) ^ rotr(W[i - 2], 19) ^ (W[i - 2] >>> 10);
      W[i] = (W[i - 16] + s0 + W[i - 7] + s1) >>> 0;
    }

    let a = h0;
    let b = h1;
    let c = h2;
    let d = h3;
    let e = h4;
    let f = h5;
    let g = h6;
    let h = h7;

    for (let i = 0; i < 64; i++) {
      const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = (h + S1 + ch + SHA256_K[i] + W[i]) | 0;
      const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (S0 + maj) | 0;

      h = g;
      g = f;
      f = e;
      e = (d + temp1) | 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) | 0;
    }

    h0 = (h0 + a) >>> 0;
    h1 = (h1 + b) >>> 0;
    h2 = (h2 + c) >>> 0;
    h3 = (h3 + d) >>> 0;
    h4 = (h4 + e) >>> 0;
    h5 = (h5 + f) >>> 0;
    h6 = (h6 + g) >>> 0;
    h7 = (h7 + h) >>> 0;
  }

  return [h0, h1, h2, h3, h4, h5, h6, h7].map((w) => w.toString(16).padStart(8, "0")).join("");
}

/** Băm SHA-256 ưu tiên `crypto.subtle.digest("SHA-256", ...)`, tự lùi về `sha256HexSync` nếu không có WebCrypto. */
export async function sha256Hex(
  input: string,
  subtleOverride?: Pick<SubtleCrypto, "digest"> | null,
): Promise<string> {
  const subtle = subtleOverride === undefined ? globalThis.crypto?.subtle : subtleOverride;
  if (subtle && typeof subtle.digest === "function") {
    try {
      const buf = await subtle.digest("SHA-256", new TextEncoder().encode(input));
      return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, "0")).join("");
    } catch {
      return sha256HexSync(input);
    }
  }
  return sha256HexSync(input);
}

export function computeNoteSignOffHashSync(
  soapRawContent: string,
  quyetDuyet?: Record<number, QuyetDuyet> | null,
  banSuaDuyet?: Record<number, string> | null,
): string {
  return sha256HexSync(buildSignOffCanonicalPayload(soapRawContent, quyetDuyet, banSuaDuyet));
}

export async function computeNoteSignOffHash(
  soapRawContent: string,
  quyetDuyet?: Record<number, QuyetDuyet> | null,
  banSuaDuyet?: Record<number, string> | null,
): Promise<string> {
  return sha256Hex(buildSignOffCanonicalPayload(soapRawContent, quyetDuyet, banSuaDuyet));
}

/** Kiểm tra bệnh án hoặc quyết định duyệt đã bị chỉnh sửa sau thời điểm ký WORM hay chưa. */
export function isSignOffStale(
  signOff: Pick<SignOffRecord, "hash" | "contentHash"> | null | undefined,
  currentContentHash: string,
): boolean {
  if (!signOff) return false;
  const baseline = signOff.contentHash || signOff.hash;
  if (!baseline) return false;
  return baseline !== currentContentHash;
}

/**
 * Trích chẩn đoán & thuốc từ văn bản SOAP thủ công (khi bác sĩ tự gõ mà chưa chạy tách mệnh đề AI)
 * để không chép nhầm `HO_SO_MAU` (Plavix / Stent / mạch vành) sang ca khám thật.
 */
export function trichChanDoanVaThuocTuSoap(content?: string | null): {
  chanDoan?: string;
  thuoc: string[];
} {
  if (!content || !content.trim()) return { thuoc: [] };
  let mucHienTai: "khac" | "chan_doan" | "thuoc" = "khac";
  const dsChanDoan: string[] = [];
  const dsThuoc: string[] = [];

  for (const dongTho of content.split("\n")) {
    const dong = dongTho.trim();
    if (!dong) continue;

    const mTieuDeCoNoiDung = dong.match(
      /^(?:#{1,4}\s*)?(?:ĐÁNH\s*GIÁ[^:]*|CHẨN\s*ĐOÁN[^:]*|A\s*[—–-]\s*ASSESSMENT)\s*(?::\s*(.*))?$/iu,
    );
    if (mTieuDeCoNoiDung) {
      mucHienTai = "chan_doan";
      const phanSau = (mTieuDeCoNoiDung[1] || "").trim();
      if (phanSau) dsChanDoan.push(phanSau);
      continue;
    }

    const mThuocCoNoiDung = dong.match(
      /^(?:#{1,4}\s*)?(?:KẾ\s*HOẠCH(?:\s*ĐIỀU\s*TRỊ[^:]*)?(?:\s*\(P\))?|ĐƠN\s*THUỐC[^:]*|THUỐC\s*ĐANG\s*DÙNG[^:]*|XỬ\s*TRÍ[^:]*|P\s*[—–-]\s*PLAN)\s*(?::\s*(.*))?$/iu,
    );
    if (mThuocCoNoiDung) {
      mucHienTai = "thuoc";
      const phanSau = (mThuocCoNoiDung[1] || "").trim();
      if (phanSau) dsThuoc.push(phanSau);
      continue;
    }

    if (
      laTieuDeMuc(dong) ||
      /^(?:Lý do vào viện|Chủ quan|Tiền sử|Khám lâm sàng|Khách quan)/iu.test(dong)
    ) {
      mucHienTai = "khac";
      continue;
    }

    const sach = dong.replace(/^\s*(?:[-*•]+|\d+[.)])\s*/, "").trim();
    if (!sach) continue;
    if (mucHienTai === "chan_doan") dsChanDoan.push(sach);
    else if (mucHienTai === "thuoc") dsThuoc.push(sach);
  }

  return {
    ...(dsChanDoan.length > 0 ? { chanDoan: dsChanDoan.join("; ") } : {}),
    thuoc: dsThuoc,
  };
}
