/**
 * GHÉP MỆNH ĐỀ VỚI CÂU TRONG BẢN NHÁP — để tô màu câu theo trạng thái duyệt, kể cả khi bác sĩ đã
 * sửa chữ trong bản nháp.
 *
 *  1. Khớp NGUYÊN VĂN trước (chỉ khi sau chữ là hết câu: ".", "—", ",", ";", ":", ")" hoặc hết dòng —
 *     để "đau tăng khi cúi" không ăn vào "đau tăng khi cúi chỉ bị lúc sáng sớm"). Mệnh đề dài xét trước.
 *  2. Mệnh đề còn lại: so GẦN ĐÚNG với từng câu chưa được ghép (phần trước " — " giải thích). Độ giống =
 *     hệ số Dice trên các chữ (không phân biệt hoa thường, dấu câu). Từ 0,6 trở lên mới ghép; cặp giống
 *     nhất ghép trước, mỗi mệnh đề và mỗi câu chỉ ghép một lần.
 *  Câu hỏi (kết thúc bằng "?") không bao giờ được ghép — mục "Câu hỏi làm rõ" không phải mệnh đề.
 */

export type MenhDeCanGhep = { id: number; text: string; textKhac?: string[] };
export type DoanGhep = { bd: number; kt: number; id: number; ganDung: boolean; doGiong: number };

export const NGUONG_GIONG = 0.6;

function chu(s: string): string[] {
  return s.normalize("NFC").toLowerCase().match(/[\p{L}\p{N}]+/gu) || [];
}

/** Hệ số Dice trên túi chữ (đếm cả chữ lặp). */
export function doGiong(a: string, b: string): number {
  const x = chu(a), y = chu(b);
  if (!x.length || !y.length) return 0;
  const dem = new Map<string, number>();
  for (const w of x) dem.set(w, (dem.get(w) || 0) + 1);
  let chung = 0;
  for (const w of y) {
    const n = dem.get(w) || 0;
    if (n > 0) { chung++; dem.set(w, n - 1); }
  }
  return (2 * chung) / (x.length + y.length);
}

/** Các câu của một dòng: [bd, kt) là phần LÕI của câu (bỏ khoảng trắng đầu, dấu chấm cuối, và phần
 *  giải thích sau " — "). */
export function tachCau(dong: string): Array<{ bd: number; kt: number; laHoi: boolean }> {
  const ra: Array<{ bd: number; kt: number; laHoi: boolean }> = [];
  const re = /[^.?!]+[.?!]*/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(dong))) {
    let bd = m.index, kt = m.index + m[0].length;
    const laHoi = /\?\s*$/.test(m[0]);
    while (bd < kt && /\s/.test(dong[bd])) bd++;
    const gach = dong.slice(bd, kt).search(/\s[—–-]\s/);
    if (gach >= 0) kt = bd + gach;
    while (kt > bd && /[\s.?!]/.test(dong[kt - 1])) kt--;
    if (kt > bd) ra.push({ bd, kt, laHoi });
  }
  return ra;
}

/** -> Map chỉ số dòng -> các đoạn được ghép (đã xếp theo vị trí). */
export function ghepMenhDe(noiDung: string, ds: MenhDeCanGhep[], laTieuDe: (dong: string) => boolean = () => false) {
  const dong = noiDung.split("\n");
  const ket = new Map<number, DoanGhep[]>();
  const daGhep = new Set<number>();
  const trung = (i: number, bd: number, kt: number) => (ket.get(i) || []).some((d) => bd < d.kt && kt > d.bd);
  const them = (i: number, d: DoanGhep) => ket.set(i, [...(ket.get(i) || []), d]);

  // 1. nguyên văn (chữ máy trích hoặc chữ bác sĩ đã sửa ở ngăn duyệt)
  const theoDoDai = ds
    .flatMap((md) => [md.text, ...(md.textKhac || [])].filter((t) => t && t.trim()).map((t) => ({ md, t })))
    .sort((a, b) => b.t.length - a.t.length);
  for (const { md, t } of theoDoDai) {
    if (daGhep.has(md.id)) continue;
    for (let i = 0; i < dong.length && !daGhep.has(md.id); i++) {
      if (laTieuDe(dong[i])) continue;
      let vt = dong[i].indexOf(t);
      while (vt >= 0) {
        const kt = vt + t.length;
        const sau = dong[i].slice(kt).trimStart();
        if ((sau === "" || /^[.—–,;:)]/.test(sau)) && !trung(i, vt, kt)) {
          them(i, { bd: vt, kt, id: md.id, ganDung: false, doGiong: 1 });
          daGhep.add(md.id);
          break;
        }
        vt = dong[i].indexOf(t, vt + 1);
      }
    }
  }

  // 2. gần đúng: mọi cặp (mệnh đề chưa ghép, câu chưa ghép), giống nhất trước
  const cau: Array<{ i: number; bd: number; kt: number }> = [];
  dong.forEach((d, i) => {
    if (laTieuDe(d)) return;
    for (const c of tachCau(d)) if (!c.laHoi && !trung(i, c.bd, c.kt)) cau.push({ i, bd: c.bd, kt: c.kt });
  });
  const cap: Array<{ md: MenhDeCanGhep; c: (typeof cau)[number]; g: number }> = [];
  for (const md of ds) {
    if (daGhep.has(md.id)) continue;
    for (const c of cau) {
      const doan = dong[c.i].slice(c.bd, c.kt);
      const g = Math.max(...[md.text, ...(md.textKhac || [])].filter(Boolean).map((t) => doGiong(t, doan)));
      if (g >= NGUONG_GIONG) cap.push({ md, c, g });
    }
  }
  cap.sort((a, b) => b.g - a.g);
  const cauDaDung = new Set<string>();
  for (const { md, c, g } of cap) {
    const khoa = `${c.i}:${c.bd}`;
    if (daGhep.has(md.id) || cauDaDung.has(khoa)) continue;
    them(c.i, { bd: c.bd, kt: c.kt, id: md.id, ganDung: true, doGiong: g });
    daGhep.add(md.id);
    cauDaDung.add(khoa);
  }

  for (const [i, ds2] of ket) ket.set(i, ds2.sort((a, b) => a.bd - b.bd));
  return ket;
}
