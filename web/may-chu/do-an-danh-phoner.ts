/**
 * Đo bộ che định danh TypeScript (`anDanhChoNgoai`, cổng ra mô hình ngoài) trên PhoNER_COVID19.
 *
 * Cùng định nghĩa với tools/do_an_danh_phoner.py (bộ che Python):
 *  - Nhãn vàng: NAME và PATIENT_ID (gộp B-/I-), văn bản nhãn = các âm tiết nối bằng dấu cách.
 *  - Câu = các âm tiết nối bằng dấu cách.
 *  - bao_ve(nhãn) = văn bản nhãn không còn trong văn bản đã che (so khớp có ranh giới: nhãn bắt đầu/kết
 *    thúc bằng chữ số thì không dính chữ số khác; bằng chữ cái thì không dính chữ cái/chữ số khác)
 *    HOẶC câu bị từ chối gửi (kq.ok === false).
 *  - Che nhầm: 300 câu hỏi đầu của ViMedAQA test_sample_500; một câu là "che nhầm" khi văn bản sau
 *    che khác văn bản gốc HOẶC câu bị từ chối.
 *
 * Chạy: cd web; npx tsx may-chu/do-an-danh-phoner.ts --tap dev|test [--toi-da N, 0 = cả tập] [--ra tep.json] [--chi-tiet]
 */
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { anDanhChoNgoai } from "./an-danh-ngoai";

const GOC = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const NHAN = ["NAME", "PATIENT_ID"] as const;
const SO_CAU_HOI_CHE_NHAM = 300;

function thamSo(ten: string): string | undefined {
  const i = process.argv.indexOf(ten);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

function docPhoner(tap: string, toiDa: number): Array<{ van: string; nhan: Array<[string, string]> }> {
  const tep = resolve(GOC, "data/ngoai/PhoNER_COVID19/data/syllable", `${tap}_syllable.json`);
  const ra: Array<{ van: string; nhan: Array<[string, string]> }> = [];
  for (const dong of readFileSync(tep, "utf8").split(/\r?\n/)) {
    if (!dong.trim()) continue;
    const r = JSON.parse(dong) as { words: string[]; tags: string[] };
    const nhan: Array<[string, string]> = [];
    let i = 0;
    while (i < r.tags.length) {
      const t = r.tags[i];
      const loai = t.slice(2);
      if (t.startsWith("B-") && (NHAN as readonly string[]).includes(loai)) {
        let j = i + 1;
        while (j < r.tags.length && r.tags[j] === `I-${loai}`) j++;
        nhan.push([loai, r.words.slice(i, j).join(" ")]);
        i = j;
      } else i++;
    }
    ra.push({ van: r.words.join(" "), nhan });
    if (toiDa > 0 && ra.length >= toiDa) break;
  }
  return ra;
}

const thoat = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

function conTrong(nhan: string, van: string): boolean {
  const dau = nhan[0] ?? "";
  const cuoi = nhan[nhan.length - 1] ?? "";
  const trai = /\d/.test(dau) ? "(?<![\\d_])" : /\p{L}/u.test(dau) ? "(?<![\\p{L}\\p{N}_])" : "";
  const phai = /\d/.test(cuoi) ? "(?![\\d_])" : /\p{L}/u.test(cuoi) ? "(?![\\p{L}\\p{N}_])" : "";
  return new RegExp(trai + thoat(nhan) + phai, "u").test(van);
}

function che(van: string): { daChe: string; tuChoi: boolean } {
  const kq = anDanhChoNgoai(van);
  return kq.ok ? { daChe: kq.van, tuChoi: false } : { daChe: "", tuChoi: true };
}

function doAnDanh(tap: string, toiDa: number, chiTiet = false) {
  const cau = docPhoner(tap, toiDa);
  let soNhan = 0;
  let baoVe = 0;
  let soCauTuChoi = 0;
  const theoLoai: Record<string, { so_nhan: number; bao_ve: number }> = {};
  for (const k of NHAN) theoLoai[k] = { so_nhan: 0, bao_ve: 0 };
  const lot: Array<{ loai: string; nhan: string; da_che: string }> = [];
  for (const { van, nhan } of cau) {
    const { daChe, tuChoi } = che(van);
    if (tuChoi) soCauTuChoi++;
    for (const [loai, chu] of nhan) {
      soNhan++;
      theoLoai[loai].so_nhan++;
      const ok = tuChoi || !conTrong(chu, daChe);
      if (ok) {
        baoVe++;
        theoLoai[loai].bao_ve++;
      } else if (chiTiet) lot.push({ loai, nhan: chu, da_che: daChe });
    }
  }
  const cauHoi = (JSON.parse(readFileSync(resolve(GOC, "data/ngoai/ViMedAQA/test_sample_500.json"), "utf8")) as Array<{
    question: string;
  }>)
    .slice(0, SO_CAU_HOI_CHE_NHAM)
    .map((c) => c.question);
  let cheNham = 0;
  const viDuCheNham: Array<{ goc: string; da_che: string; tu_choi: boolean }> = [];
  for (const q of cauHoi) {
    const { daChe, tuChoi } = che(q);
    if (tuChoi || daChe !== q.normalize("NFC")) {
      cheNham++;
      if (chiTiet) viDuCheNham.push({ goc: q, da_che: daChe, tu_choi: tuChoi });
    }
  }
  const kq: Record<string, unknown> = {
    bo_che: "typescript_anDanhChoNgoai",
    tap,
    so_cau: cau.length,
    so_nhan: soNhan,
    bao_ve: baoVe,
    ty_le_bao_ve: soNhan ? Math.round((baoVe / soNhan) * 1e4) / 1e4 : null,
    theo_loai: theoLoai,
    so_cau_tu_choi: soCauTuChoi,
    so_cau_hoi_vimedaqa: cauHoi.length,
    che_nham: cheNham,
    ty_le_che_nham: cauHoi.length ? Math.round((cheNham / cauHoi.length) * 1e4) / 1e4 : null,
  };
  if (chiTiet) {
    kq.lot = lot;
    kq.vi_du_che_nham = viDuCheNham;
  }
  return kq;
}

const tap = thamSo("--tap");
if (tap !== "dev" && tap !== "test") {
  console.error("Cần --tap dev|test");
  process.exit(2);
}
const kq = doAnDanh(tap, Number(thamSo("--toi-da") ?? 0), process.argv.includes("--chi-tiet"));
const { lot: _lot, vi_du_che_nham: _vd, ...tom } = kq;
console.log(JSON.stringify(tom));
const ra = thamSo("--ra");
if (ra) writeFileSync(ra, JSON.stringify(kq, null, 2), "utf8");
