import type express from "express";
import fs from "fs";
import path from "path";
import { GOC, traLoi } from "./dung-chung";
import { chanNeuChuaChoPhep, goiNgoai } from "./llm-ngoai";

const NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";
const LOAI_UU_TIEN =
  '(guideline[pt] OR practice guideline[pt] OR systematic review[pt] OR meta-analysis[pt])';
// Bài đã rút hoặc bị thay bằng bản mới thì không được làm căn cứ.
const BO_BAI_RUT = "NOT (retracted publication[pt] OR retraction of publication[pt])";

function boThe(s: string) {
  return s
    .replace(/<[^>]+>/g, "")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
    .replace(/&amp;/g, "&")
    .replace(/[\s  ]+/g, " ")
    .trim();
}

/**
 * NCBI (PubMed, StatPearls) cho tối đa 3 yêu cầu/giây khi không có khoá API. Thử 24/09: PubMed và
 * StatPearls gọi cùng lúc -> mã 429, cả hai ra 0 bài. Mọi yêu cầu tới eutils đi qua một hàng đợi,
 * cách nhau ≥ 350 ms; gặp 429 thì chờ rồi thử lại (tối đa 3 lần).
 */
let luotNCBI = Promise.resolve();
function choLuotNCBI() {
  const cho = luotNCBI.then(() => new Promise<void>((r) => setTimeout(r, 350)));
  luotNCBI = cho;
  return cho;
}

async function layChu(url: string, giay = 12): Promise<string> {
  const laNCBI = url.includes("eutils.ncbi.nlm.nih.gov");
  for (let lan = 0; ; lan++) {
    if (laNCBI) await choLuotNCBI();
    const ctl = new AbortController();
    const hen = setTimeout(() => ctl.abort(), giay * 1000);
    try {
      const r = await fetch(url, { signal: ctl.signal, headers: { "User-Agent": "MediTrace/1.0 (tool=meditrace)" } });
      if (r.status === 429 && laNCBI && lan < 3) {
        await new Promise((res) => setTimeout(res, 1000 * (lan + 1)));
        continue;
      }
      if (!r.ok) throw new Error(`mã ${r.status}`);
      return await r.text();
    } finally {
      clearTimeout(hen);
    }
  }
}

export type TaiLieu = { so: number; nguon: "PubMed" | "MedlinePlus" | "FDA" | "Bộ Y tế" | "Phác đồ BYT" | "MSD" | "NICE" | "WHO" | "CDC" | "StatPearls" | "AAFP"; ten: string; url: string; nam?: string;
                 loai?: string; tapChi?: string; noiDung: string; pmc?: string };

async function timPubMed(tuKhoa: string, soBai = 4, chiBangChungCao = false, tuNam?: number): Promise<Omit<TaiLieu, "so">[]> {
  // `tuNam` (màn Thư viện): lọc CHẶT theo năm xuất bản, không lùi về bài cũ hơn.
  const locNam = tuNam ? ` AND ("${tuNam}"[dp] : "3000"[dp])` : "";
  const tim = async (term: string) => {
    const j = JSON.parse(await layChu(
      `${NCBI}/esearch.fcgi?db=pubmed&retmode=json&sort=relevance&tool=meditrace&retmax=${soBai}` +
        `&term=${encodeURIComponent(term + locNam)}`));
    return (j?.esearchresult?.idlist || []) as string[];
  };
  // Từ khoá mô hình đặt đôi khi quá hẹp (gọi thử 23/09: "... timing prednisolone dose" ra 0 bài).
  // Không ra thì bỏ dần từ cuối (giữ tối thiểu 2 từ). Thử hết các mức CÓ lọc bằng chứng cao trước,
  // rồi mới bỏ lọc — bỏ lọc sớm thì ra bài lạc đề (thử: ra một bài về phục hồi chức năng).
  const tu = tuKhoa.split(/\s+/).filter(Boolean);
  const cacMuc = Array.from({ length: Math.max(1, tu.length - 1) }, (_, i) => tu.slice(0, tu.length - i).join(" "));
  let ids: string[] = [];
  // Bài 10 năm gần đây trước (thử 24/09: câu viêm xoang ra toàn bài 1995–2011); không có mới lấy bài cũ.
  const gan = tuNam ? "" : ` AND ("${new Date().getFullYear() - 10}"[dp] : "3000"[dp])`;
  for (const q of cacMuc) {
    if ((ids = await tim(`(${q}) AND ${LOAI_UU_TIEN}${gan} ${BO_BAI_RUT}`)).length) break;
  }
  if (!ids.length) for (const q of cacMuc) {
    if ((ids = await tim(`(${q}) AND ${LOAI_UU_TIEN} ${BO_BAI_RUT}`)).length) break;
  }
  if (!ids.length && !chiBangChungCao) {
    for (const q of cacMuc) {
      if ((ids = await tim(`(${q}) ${BO_BAI_RUT}`)).length) break;
    }
  }
  if (!ids.length) return [];
  const xml = await layChu(`${NCBI}/efetch.fcgi?db=pubmed&retmode=xml&tool=meditrace&id=${ids.join(",")}`, 20);
  const ra: Omit<TaiLieu, "so">[] = [];
  for (const bai of xml.split("<PubmedArticle>").slice(1)) {
    const pmid = bai.match(/<PMID[^>]*>(\d+)<\/PMID>/)?.[1];
    if (!pmid) continue;
    const tenBai = boThe(bai.match(/<ArticleTitle>([\s\S]*?)<\/ArticleTitle>/)?.[1] || "");
    if (/^WITHDRAWN\b|^RETRACTED\b/i.test(tenBai)) continue;
    const tomTat = [...bai.matchAll(/<AbstractText([^>]*)>([\s\S]*?)<\/AbstractText>/g)]
      .map((m) => {
        const nhan = m[1].match(/Label="([^"]+)"/)?.[1];
        return (nhan ? `${nhan}: ` : "") + boThe(m[2]);
      })
      .join(" ");
    const loai = [...bai.matchAll(/<PublicationType[^>]*>([^<]+)<\/PublicationType>/g)]
      .map((m) => m[1])
      .filter((x) => /guideline|systematic review|meta-analysis|review/i.test(x));
    ra.push({
      nguon: "PubMed",
      ten: tenBai || `PMID ${pmid}`,
      url: `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`,
      nam: bai.match(/<PubDate>[\s\S]*?<Year>(\d{4})<\/Year>/)?.[1] || bai.match(/<PubDate>[\s\S]*?(\d{4})/)?.[1],
      loai: loai[0],
      tapChi: boThe(bai.match(/<Title>([\s\S]*?)<\/Title>/)?.[1] || ""),
      pmc: bai.match(/<ArticleId IdType="pmc">(PMC\d+)<\/ArticleId>/)?.[1],
      noiDung: tomTat ? tomTat.slice(0, 1500) : "(bài không có tóm tắt)",
    });
  }
  // efetch không giữ thứ tự liên quan của esearch — xếp lại theo danh sách id.
  return ids.map((id) => ra.find((b) => b.url.endsWith(`/${id}/`))).filter(Boolean) as Omit<TaiLieu, "so">[];
}

async function timMedlinePlus(tuKhoa: string, soBai = 1): Promise<Omit<TaiLieu, "so">[]> {
  const xml = await layChu(
    `https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&retmax=${soBai}&term=${encodeURIComponent(tuKhoa)}`);
  return [...xml.matchAll(/<document[^>]*url="([^"]+)"[^>]*>([\s\S]*?)<\/document>/g)].map((m) => {
    const truong = (ten: string) =>
      boThe(boThe(m[2].match(new RegExp(`<content name="${ten}">([\\s\\S]*?)</content>`))?.[1] || ""));
    return { nguon: "MedlinePlus" as const, ten: truong("title") || m[1], url: m[1],
             noiDung: truong("FullSummary").slice(0, 1500) };
  });
}

/** Chữ chung chung không được làm "chữ chính" của tên bệnh (thử 24/09: "high blood pressure" -> bám
 *  chữ "high" -> StatPearls "High Risk Behaviors", WHO "high-threat pathogens"). */
const TU_CHUNG_BENH = new Set(["high", "low", "acute", "chronic", "severe", "mild", "blood", "attack", "disease",
  "disorder", "disorders", "syndrome", "infection", "infections", "pain", "adult", "adults", "fever", "type", "primary"]);
function tuChinhBenh(ten: string) {
  const tu = ten.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 3);
  return tu.find((w) => w.length >= 4 && !TU_CHUNG_BENH.has(w)) || tu[0] || "";
}
/** Tên phổ thông -> tên y khoa (khi mô hình không trả benh_en). */
const TEN_Y_KHOA: Record<string, string> = {
  "high blood pressure": "hypertension", "heart attack": "myocardial infarction", "asthma attack": "asthma",
  "flu": "influenza", "sinus infection": "sinusitis", "kidney stones": "nephrolithiasis", "stomach flu": "gastroenteritis",
  "pink eye": "conjunctivitis", "heart failure": "heart failure", "high cholesterol": "hyperlipidemia",
};

/**
 * STATPEARLS (sách cập nhật liên tục của NCBI Bookshelf, Heidi hay trích). Trang NCBI chặn máy bằng
 * CAPTCHA — không vượt; nhưng mỗi chương có trên PubMed dạng PubmedBookArticle với tóm tắt dài
 * (~4 nghìn ký tự). Tìm theo tên bệnh trong tiêu đề, chương khớp câu hỏi nhất.
 */
async function timStatPearls(tenBenh: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const ten = tenBenh.toLowerCase().replace(/[^a-z0-9 -]/g, " ").replace(/\s+/g, " ").trim();
  if (!ten) return [];
  const timId = async (t: string) => JSON.parse(await layChu(`${NCBI}/esearch.fcgi?db=pubmed&retmode=json&tool=meditrace` +
    `&retmax=40&sort=relevance&term=${encodeURIComponent(`${t}[ti] AND statpearls[book]`)}`))?.esearchresult?.idlist || [];
  let ids: string[] = await timId(ten);
  if (!ids.length && ten.includes(" ")) ids = await timId(tuChinhBenh(ten));
  if (!ids.length) return [];
  // Tên bệnh chung ("hypertension") khớp hàng trăm chương — lấy TIÊU ĐỀ 40 chương (esummary, nhẹ),
  // xếp hạng, rồi mới tải tóm tắt chương tốt nhất (thử 24/09: 8 chương đầu ra "Secondary Hypertension").
  const tom = JSON.parse(await layChu(`${NCBI}/esummary.fcgi?db=pubmed&retmode=json&tool=meditrace&id=${ids.join(",")}`));
  const tuHoi = new Set(cauHoi.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 4));
  const hoiCap = HOI_CAP.test(cauHoi);
  const hoiDB = /trẻ|nhi|thai|child|pediatric|pregnan|neonat/i.test(cauHoi);
  const ung = ids.map((id) => {
    const t = boThe(String(tom?.result?.[id]?.title || "")).toLowerCase().replace(/\.$/, "");
    const diem = (t === ten ? 6 : 0) + (t.startsWith(ten) ? 2 : 0) + [...tuHoi].filter((w) => t.includes(w)).length * 2
      + (hoiCap && /acute|exacerbation|status|emergenc|crisis/.test(t) ? 4 : 0) - t.length / 25
      // Chương tổng quan (tên ngắn) hơn chương chuyên đề: thử 24/09 "Renal Denervation Therapy for
      // Drug-Resistant Hypertension" thắng "Essential Hypertension" chỉ vì trùng "drug", "therapy".
      - Math.max(0, t.split(/\s+/).length - 3) * 1.5
      - (!hoiDB && /pediatric|children|neonat|pregnan|infant/.test(t) ? 4 : 0)
      - (/secondary|nursing|anesthesia|imaging|evaluation of|history of|embryology|anatomy/.test(t) && !t.startsWith(ten) ? 2 : 0)
      - (/clinical trials?|trial|research|guidelines? history/.test(t) ? 4 : 0)
      + (/essential|primary|management|treatment|overview/.test(t) ? 1 : 0);
    return { id, t, diem };
  }).filter((x) => x.t).sort((a, b) => b.diem - a.diem);
  if (!ung.length) return [];
  const xml = await layChu(`${NCBI}/efetch.fcgi?db=pubmed&retmode=xml&tool=meditrace&id=${ung[0].id}`, 20);
  const bai = xml.split("<PubmedBookArticle>")[1] || "";
  const tieuDe = boThe(bai.match(/<ArticleTitle[^>]*>([\s\S]*?)<\/ArticleTitle>/)?.[1] || "");
  const nbk = bai.match(/IdType="bookaccession">(NBK\d+)</)?.[1];
  const tomTat = [...bai.matchAll(/<AbstractText([^>]*)>([\s\S]*?)<\/AbstractText>/g)].map((m) => boThe(m[2])).join(" ");
  const nam = bai.match(/<ContributionDate>[\s\S]*?<Year>(\d{4})/)?.[1] || bai.match(/<PubDate>[\s\S]*?<Year>(\d{4})/)?.[1];
  if (!nbk || !tomTat) return [];
  return [{ nguon: "StatPearls" as const, ten: tieuDe, url: `https://www.ncbi.nlm.nih.gov/books/${nbk}/`, nam,
            loai: "StatPearls (NCBI Bookshelf)", noiDung: tomTat.slice(0, 2200) }];
}

/**
 * PMC TOÀN VĂN. Bài PubMed có bản mở trên PMC: lấy toàn văn qua Europe PMC (không qua NCBI nên không
 * vướng giới hạn 3 yêu cầu/giây), dựng lại thành các mục "## tên mục" rồi lấy mục khớp câu hỏi
 * (hỏi điều trị -> mục Treatment/Management). Không lấy được thì giữ tóm tắt như cũ.
 */
async function vanPMC(pmc: string): Promise<string> {
  const xml = await layWeb(`https://www.ebi.ac.uk/europepmc/webservices/rest/${pmc}/fullTextXML`, 20);
  const than = xml.split(/<body[^>]*>/)[1]?.split("</body>")[0] || "";
  if (!than) return "";
  return than
    .replace(/<(table-wrap|fig|disp-formula|supplementary-material)[\s\S]*?<\/\1>/g, " ")
    .replace(/<title>([\s\S]*?)<\/title>/g, (_, t) => `\n## ${boThe(t)}\n`)
    .replace(/<xref[^>]*>[\s\S]*?<\/xref>/g, "")
    .replace(/<\/p>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/[ \t]+/g, " ")
    .replace(/\n\s*\n+/g, "\n");
}

async function lamDayPMC(ds: Omit<TaiLieu, "so">[], cauHoi: string, toiDa = 2) {
  const coPMC = ds.filter((t) => t.pmc).slice(0, toiDa);
  await Promise.all(coPMC.map(async (t) => {
    try {
      const van = await vanPMC(t.pmc!);
      if (van.length < 3000) return;
      t.noiDung = `(Toàn văn PMC) ${cuaSo(van, [cauHoi], HOI_DIEU_TRI.test(cauHoi), 2000)}`;
      t.url = `https://pmc.ncbi.nlm.nih.gov/articles/${t.pmc}/`;
      t.loai = `${t.loai ? `${t.loai} · ` : ""}toàn văn PMC`;
    } catch {}
  }));
}

/**
 * AAFP — tạp chí American Family Physician (Heidi hay trích). Trang tìm kiếm của aafp.org trả 404
 * với máy, nên tìm trên PubMed theo tên tạp chí, rồi đi theo liên kết LinkOut sang aafp.org để đọc bài.
 * Bỏ tờ hướng dẫn cho bệnh nhân ("handout"), chỉ giữ bài cho thầy thuốc; bài 10 năm gần đây trước.
 */
async function timAAFP(tenBenh: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const ten = tenBenh.toLowerCase().replace(/[^a-z0-9 -]/g, " ").replace(/\s+/g, " ").trim();
  if (!ten) return [];
  const gan = `("${new Date().getFullYear() - 10}"[dp] : "3000"[dp])`;
  const timId = async (t: string) => JSON.parse(await layChu(`${NCBI}/esearch.fcgi?db=pubmed&retmode=json&tool=meditrace` +
    `&retmax=15&sort=relevance&term=${encodeURIComponent(`${t}[ti] AND "Am Fam Physician"[ta] AND ${gan}`)}`))
    ?.esearchresult?.idlist || [];
  let ids: string[] = await timId(ten);
  if (!ids.length && ten.includes(" ")) ids = await timId(tuChinhBenh(ten));
  if (!ids.length) return [];
  const tom = JSON.parse(await layChu(`${NCBI}/esummary.fcgi?db=pubmed&retmode=json&tool=meditrace&id=${ids.join(",")}`));
  const tuHoi = new Set(cauHoi.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 4));
  const ung = ids.map((id) => {
    const r = tom?.result?.[id] || {};
    const t = boThe(String(r.title || "")).toLowerCase();
    const loaiBai = (r.pubtype || []).join(" ").toLowerCase();
    const diem = [...tuHoi].filter((w) => t.includes(w)).length * 2 + (t.includes(ten) ? 3 : 0) - t.length / 40
      - (/patient education|handout/.test(loaiBai) ? 20 : 0) - (/comment|editorial|letter|news/.test(loaiBai) ? 6 : 0)
      - (/photo quiz|poem|close-ups|curbside|cochrane for clinicians/.test(t) ? 5 : 0);
    return { id, t, nam: String(r.pubdate || "").slice(0, 4), diem };
  }).filter((x) => x.t && x.diem > -5).sort((a, b) => b.diem - a.diem);
  for (const x of ung.slice(0, 3)) {
    try {
      const r = await fetch(`https://www.aafp.org/link_out?pmid=${x.id}`, { headers: { "User-Agent": UA_WEB }, redirect: "follow" });
      if (!r.ok) continue;
      const trang = await r.text();
      const van = chuTrang(trang);
      // Tờ cho bệnh nhân: địa chỉ "-s1" hoặc tự ghi "This handout" — bỏ.
      if (/-s\d+(\.html)?$/.test(r.url) || /this handout provides/i.test(van) || van.length < 3000) continue;
      const tieuDe = boThe(trang.match(/<title>([^<]+)<\/title>/i)?.[1] || x.t).replace(/\s*\|\s*AAFP.*$|\s*\|\s*AFP.*$/i, "");
      return [{ nguon: "AAFP" as const, ten: tieuDe, url: r.url, nam: x.nam, loai: "American Family Physician",
                noiDung: cuaSo(van, [tenBenh, cauHoi], HOI_DIEU_TRI.test(cauHoi), 2000) }];
    } catch {}
  }
  return [];
}

/**
 * Tìm thẳng trên PubMed, KHÔNG qua mô hình (không tốn tiền, không gửi gì ra ai-box). Dùng cho
 * ô tìm trong "Thư viện y khoa". PubMed hiểu từ khoá tiếng Anh; tiếng Việt thường không ra kết quả.
 */

/**
 * NHÃN THUỐC FDA (openFDA, api.fda.gov) — nguồn chính thức cho LIỀU, TƯƠNG TÁC, CHỐNG CHỈ ĐỊNH.
 * Thêm 24/09/2026: thử 6 câu bác sĩ hay hỏi, câu về liều (paracetamol tối đa, amoxicillin theo
 * cân nặng) đều hụt vì con số nằm trong tờ hướng dẫn thuốc, không nằm trong tóm tắt bài báo.
 * Ưu tiên nhãn THUỐC KÊ ĐƠN; lấy mục theo loại câu hỏi để không đưa cả tờ nhãn cho mô hình.
 */
const MUC_NHAN: Array<[RegExp, string[]]> = [
  [/liều|dose|dosing|mg\/kg|bao nhiêu mg|tối đa|dùng mấy lần/i, ["dosage_and_administration"]],
  [/tương tác|dùng chung|phối hợp|interaction/i, ["drug_interactions", "contraindications"]],
  [/chống chỉ định|contraindicat|không được dùng/i, ["contraindications", "boxed_warning"]],
  [/tác dụng phụ|tác dụng không mong muốn|adverse|side effect/i, ["adverse_reactions", "warnings_and_cautions"]],
  [/thai|cho con bú|pregnan/i, ["pregnancy", "use_in_specific_populations"]],
];

// Ten quoc te (INN) -> ten FDA dung (USAN). openFDA chi biet ten My: thu 24/09/2026 hoi
// "paracetamol" khong ra nhan nao vi FDA goi la "acetaminophen".
const TEN_MY: Record<string, string> = {
  paracetamol: "acetaminophen", salbutamol: "albuterol", adrenaline: "epinephrine", adrenalin: "epinephrine",
  noradrenaline: "norepinephrine", glibenclamide: "glyburide", pethidine: "meperidine", frusemide: "furosemide",
  amoxycillin: "amoxicillin", lignocaine: "lidocaine", levothyroxine: "levothyroxine", aciclovir: "acyclovir",
  valaciclovir: "valacyclovir", ciclosporin: "cyclosporine", rifampicin: "rifampin", cefalexin: "cephalexin",
  colecalciferol: "cholecalciferol", ipratropium: "ipratropium", orciprenaline: "metaproterenol",
  metamizole: "dipyrone", hyoscine: "scopolamine", prednisolon: "prednisolone", amlodipin: "amlodipine",
};

// Duong dung trong cau hoi -> openfda.route. Thu 24/09: hoi "salbutamol khi dung" ra nhan VIEN UONG.
const DUONG_DUNG_FDA: Array<[RegExp, string]> = [
  [/khí dung|xịt|hít|phun sương|inhal|nebul/i, "RESPIRATORY (INHALATION)"],
  [/tiêm tĩnh mạch|truyền|tĩnh mạch|intraven/i, "INTRAVENOUS"],
  [/tiêm bắp|intramusc/i, "INTRAMUSCULAR"],
  [/nhỏ mắt|mắt/i, "OPHTHALMIC"],
  [/bôi|ngoài da|topical/i, "TOPICAL"],
  [/uống|viên|oral/i, "ORAL"],
];

// Thuoc ma duong dung chinh la hit: cau hoi khong noi duong dung thi lay nhan dang hit
// (thu 24/09: hoi thuoc cat con hen ra nhan albuterol VIEN UONG).
const THUOC_HIT = new Set(["albuterol", "levalbuterol", "ipratropium", "tiotropium", "budesonide", "fluticasone",
  "salmeterol", "formoterol", "beclomethasone", "ciclesonide", "mometasone", "umeclidinium", "vilanterol"]);

async function timFDA(tenThuoc: string[], cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const duongCau = DUONG_DUNG_FDA.find(([bt]) => bt.test(cauHoi))?.[1];
  tenThuoc = tenThuoc.map((x) => TEN_MY[x.trim().toLowerCase()] || x);
  const muc = new Set<string>();
  for (const [bt, ds] of MUC_NHAN) if (bt.test(cauHoi)) ds.forEach((m) => muc.add(m));
  if (!muc.size) ["dosage_and_administration", "boxed_warning"].forEach((m) => muc.add(m));
  const ra: Omit<TaiLieu, "so">[] = [];
  for (const ten of tenThuoc.slice(0, 2)) {
    const t = ten.trim().toLowerCase().replace(/"/g, "");
    if (!t) continue;
    let r: any = null;
    // Ten hoat chat CHINH XAC truoc: tim "acetaminophen" thuong ra thuoc PHOI HOP
    // (oxycodone + acetaminophen) — thu 24/09/2026.
    const T = encodeURIComponent(t.toUpperCase());
    const duong = duongCau || (THUOC_HIT.has(t) ? "RESPIRATORY (INHALATION)" : undefined);
    const theoDuong = duong ? `+AND+openfda.route:"${encodeURIComponent(duong)}"` : "";
    const cacTruyVan = [
      ...(theoDuong ? [`openfda.generic_name.exact:"${T}"${theoDuong}`] : []),
      `openfda.generic_name.exact:"${T}"+AND+openfda.product_type:"HUMAN+PRESCRIPTION+DRUG"`,
      `openfda.generic_name.exact:"${T}"`, `openfda.generic_name:"${encodeURIComponent(t)}"`,
    ];
    for (const q of cacTruyVan) {
      try {
        r = JSON.parse(await layChu(`https://api.fda.gov/drug/label.json?search=${q}&limit=1`))?.results?.[0];
      } catch {
        r = null;                 // openFDA trả 404 khi không có kết quả
      }
      // Tim gan dung (khong .exact) hay ra thuoc PHOI HOP ("bictegravir, ..., tenofovir"): bo.
      if (r && !q.includes(".exact") && /,| AND /.test(String(r.openfda?.generic_name?.[0] || ""))) r = null;
      if (r) break;
    }
    if (!r) continue;
    // Muc dai (tuong tac thuoc hang chuc nghin ky tu): lay CAU nhac toi thuoc kia truoc, roi moi lay dau muc.
    const khac = tenThuoc.filter((x) => x.toLowerCase() !== t).map((x) => x.toLowerCase().slice(0, 7));
    const catMuc = (van: string) => {
      const cau = van.split(/(?<=[.;])\s+/);
      const trung = khac.length ? cau.filter((c) => khac.some((k) => c.toLowerCase().includes(k))) : [];
      return (trung.length ? trung.join(" ") : van).slice(0, 1400);
    };
    const phan = [...muc].filter((m) => r[m]?.[0]).map((m) => `${m.replace(/_/g, " ")}: ${catMuc(boThe(r[m][0]))}`);
    if (!phan.length) continue;
    const tenNhan = r.openfda?.generic_name?.[0] || t;
    ra.push({
      nguon: "FDA",
      ten: `Nhãn thuốc FDA — ${tenNhan}${r.openfda?.brand_name?.[0] ? ` (${r.openfda.brand_name[0]})` : ""}`,
      url: r.set_id ? `https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=${r.set_id}` : "https://open.fda.gov/",
      nam: String(r.effective_time || "").slice(0, 4) || undefined,
      loai: `${r.openfda?.product_type?.[0] === "HUMAN PRESCRIPTION DRUG" ? "nhãn thuốc kê đơn" : "nhãn thuốc"}` +
        `${r.openfda?.route?.[0] ? ` · ${String(r.openfda.route[0]).toLowerCase()}` : ""}`,
      noiDung: phan.join("\n").slice(0, 2400),
    });
  }
  return ra;
}

/**
 * CỤC QUẢN LÝ KHÁM, CHỮA BỆNH — BỘ Y TẾ (kcb.vn). Không có giao diện tìm kiếm cho máy; dùng ô tìm
 * của trang (GET /?keyword=…&page=search) rồi đọc chữ trong các thẻ <p> của từng bài. Nội dung là
 * công văn và tin chuyên môn, KHÔNG phải toàn văn quyết định ban hành hướng dẫn (bản đó là tệp đính
 * kèm) — nên câu trả lời có thể chỉ trỏ được tới văn bản, chưa đọc được phác đồ chi tiết.
 */
async function timKCB(tuKhoa: string, soBai = 3): Promise<Omit<TaiLieu, "so">[]> {
  const trang = await layChu(`https://kcb.vn/?keyword=${encodeURIComponent(tuKhoa)}&site=2005611&page=search`);
  const da = new Set<string>();
  const ung: Array<{ url: string; ten: string; diem: number }> = [];
  for (const m of trang.matchAll(/href="(\/(?:cong-van|van-ban|tin-tuc|thong-bao)\/[^"]+\.html)"[^>]*title="([^"]+)"/g)) {
    if (da.has(m[1])) continue;
    da.add(m[1]);
    const ten = boThe(m[2]);
    // Uu tien cong van / van ban va bai co chu "huong dan", "phac do", "quyet dinh".
    const diem = (/^\/(cong-van|van-ban)/.test(m[1]) ? 2 : 0) + (/hướng dẫn|phác đồ|quyết định/i.test(ten) ? 2 : 0);
    ung.push({ url: `https://kcb.vn${m[1]}`, ten, diem });
  }
  ung.sort((a, b) => b.diem - a.diem);
  const ra: Omit<TaiLieu, "so">[] = [];
  for (const u of ung.slice(0, soBai)) {
    try {
      const html = await layChu(u.url);
      const doan = [...html.matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g)].map((m) => boThe(m[1])).filter((x) => x.length > 40);
      if (!doan.length) continue;
      ra.push({ nguon: "Bộ Y tế", ten: u.ten, url: u.url, loai: u.url.includes("/cong-van/") ? "công văn" : "tin chuyên môn",
                noiDung: doan.join(" ").slice(0, 1500) });
    } catch {}
  }
  return ra;
}

/** kcb.vn chi khop cum ngan: thu tung chuoi, moi chuoi rut dan tu cuoi (giu toi thieu 2 tu).
 *  Thu 24/09: "phac do dieu tri sot xuat huyet dengue dau hieu canh bao truyen dich" ra 0 bai,
 *  "sot xuat huyet Dengue" ra 10. */
async function timKCBRutDan(ds: string[]): Promise<Omit<TaiLieu, "so">[]> {
  for (const cum of ds.slice(0, 2)) {
    const tu = cum.replace(/^(phác đồ|hướng dẫn|điều trị|chẩn đoán)(\s+(điều trị|chẩn đoán))?\s+/i, "").split(/\s+/);
    for (let n = Math.min(tu.length, 5); n >= Math.min(2, tu.length); n--) {
      const kq = await timKCB(tu.slice(0, n).join(" "));
      if (kq.length) return kq;
    }
  }
  return [];
}

// Tu chung, khong du de noi bai co lien quan hay khong.
const TU_CHUNG_EN = new Set(["therapy", "treatment", "management", "adult", "adults", "children", "child", "dose",
  "dosage", "dosing", "clinical", "patients", "patient", "guideline", "guidelines", "disease", "acute", "chronic",
  "initiation", "threshold", "maximum", "daily", "timing", "drug", "drugs", "interaction", "interactions", "effect"]);

/** Bai PubMed phai chua it nhat mot tu khoa KHONG chung chung — loc bai lac de (thu 24/09: hoi tang
 *  huyet ap ra mot bai xuat huyet gian tinh mach thuc quan). */
/** Bài PubMed phải nói VỀ bệnh/thuốc được hỏi: tên bài có tên bệnh (MedlinePlus) hoặc tên thuốc.
 *  Thử 24/09: hỏi hen cấp người lớn, giữ lại bài nấm phổi, ho, viêm xoang (tóm tắt có nhắc "asthma")
 *  và bài dự đoán cơn hen ở TRẺ EM. */
function lienQuanChat(t: Omit<TaiLieu, "so">, tenBenhAnh: string, thuoc: string[], cauHoi: string) {
  const ten = t.ten.toLowerCase();
  const tuBenh = tenBenhAnh.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 4 && !TU_CHUNG_EN.has(w)
    && !/^(attack|acute|chronic|severe|disease|disorder|syndrome|infection)$/.test(w));
  const goc = (w: string) => w.slice(0, Math.max(5, w.length - 2));
  const chinh = tuChinhBenh(tenBenhAnh);
  const coBenh = tuBenh.length > 0 && !!chinh && ten.includes(goc(chinh));
  const coThuoc = thuoc.some((x) => x && ten.includes(goc(x.toLowerCase())));
  if (!coBenh && !coThuoc && (tuBenh.length || thuoc.length)) return false;
  const hoiTre = /(^|[^\p{L}])(trẻ|nhi|sơ sinh)(?!\p{L})|child|infant|pediatric|paediatric/iu.test(cauHoi);
  if (!hoiTre && /paediatric|pediatric|children|child|infant|neonat/.test(ten) && !/adult/.test(ten)) return false;
  return true;
}

function lienQuan(t: Omit<TaiLieu, "so">, tuKhoa: string) {
  const tu = tuKhoa.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 4 && !TU_CHUNG_EN.has(w));
  if (!tu.length) return true;
  const van = `${t.ten} ${t.noiDung}`.toLowerCase();
  return tu.some((w) => van.includes(w.slice(0, Math.max(5, w.length - 2))));
}

/**
 * THƯ VIỆN PHÁC ĐỒ BỘ Y TẾ LƯU TẠI MÁY (tools/tai_phac_do.py → data/phac-do/doan.jsonl).
 * Mỗi dòng một TRANG của một văn bản hướng dẫn chẩn đoán, điều trị tải từ kcb.vn. Tìm bằng chỉ
 * mục từ và cặp từ liền nhau (tiếng Việt mỗi âm tiết một chữ: "xuất huyết" phải đi cùng nhau).
 * Không có mô hình nào ở bước tìm; trang tìm được đưa nguyên văn cho bước tóm tắt.
 */
type TrangPhacDo = { ma: string; tieu_de: string; nam: number | null; trang: number; van: string; noi_dang?: string;
                     url_trang: string; url_pdf: string; tu: Map<string, number>; cap: Set<string>; tuTen: Set<string> };
const TU_DUNG_VI = new Set(["và", "của", "cho", "là", "có", "không", "thế", "nào", "bao", "nhiêu", "gì", "những",
  "các", "một", "được", "trong", "với", "theo", "khi", "thì", "này", "đó", "như", "để", "từ", "hay", "hoặc", "nên",
  "cần", "ở", "ra", "vào", "trên", "dưới", "bị", "người", "bệnh", "nhân"]);

/** Phong PDF cu doc "u+moc" thanh "ƣ" (U+01A3) — "CHƢƠNG". Doi lai, khong thi tim truot. */
function suaPhong(s: string) {
  return s.normalize("NFC").replace(/ƣ/g, "ư").replace(/Ƣ/g, "Ư");
}

function tuViet(s: string): string[] {
  return (suaPhong(s).toLowerCase().match(/[\p{L}\p{N}]+/gu) || []);
}

/** Trang dau van ban (quyet dinh ban hanh, muc luc, loi noi dau, ban bien soan) chua nhieu tu cua
 *  ten benh nhung khong co noi dung chuyen mon — thu 24/09 chung dung dau ket qua. */
function laTrangPhu(van: string) {
  const v = van.slice(0, 600).toUpperCase();
  return /MỤC LỤC|LỜI NÓI ĐẦU|LỜI GIỚI THIỆU|BAN BIÊN SOẠN|CỘNG HOÀ XÃ HỘI|CỘNG HÒA XÃ HỘI|DANH MỤC CHỮ VIẾT TẮT/.test(v)
    || (van.match(/\.{8,}/g) || []).length >= 5;
}

let PHAC_DO: TrangPhacDo[] = [];
const IDF = new Map<string, number>();

function napPhacDo() {
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

/** "Quyết định 1740/QĐ-BYT ban hành tài liệu chuyên môn Hướng dẫn …" -> "Hướng dẫn … (QĐ 1740/QĐ-BYT)". */
function tenGon(t: string) {
  const qd = t.match(/(\d+\/QĐ-BYT)/)?.[1];
  const m = t.match(/[“"]([^”"]+)[”"]/) || t.match(/(Hướng dẫn.*)$/i);
  const ten = (m ? m[1] : t).trim();
  return qd && !ten.includes(qd) ? `${ten} (QĐ ${qd})` : ten;
}

/** -> các trang phác đồ khớp nhất (tối đa 3, từ tối đa 2 văn bản). */
/** Ten benh gon: bo chu chung o DAU ("phac do dieu tri", "con", "dot") va chu chi muc do / doi tuong
 *  o CUOI ("cap", "man", "o nguoi lon"). Thu 24/09: mo hinh luc ra "hen phe quan cap", luc ra
 *  "con hen phe quan cap" — van ban viet "hen phe quan", nen ca hai deu truot. */
function gonTenBenh(k: string) {
  return tuViet(k).join(" ")
    .replace(/^((phác đồ|hướng dẫn|điều trị|chẩn đoán|xử trí|bệnh|cơn|đợt cấp|đợt|hội chứng)\s+)+/, "")
    .replace(/^(và\s+)+/, "")
    .replace(/(\s+(cấp tính|mạn tính|cấp|mạn|nặng|nhẹ|ở|người lớn|trẻ em|nguy kịch|có dấu hiệu cảnh báo))+$/, "");
}

function timPhacDo(cauHoi: string, tuKhoaViet: string[]): Omit<TaiLieu, "so">[] {
  if (!PHAC_DO.length) return [];
  const tuHoi = tuViet(`${cauHoi} ${tuKhoaViet.join(" ")}`).filter((w) => !TU_DUNG_VI.has(w));
  const capHoi = new Set<string>();
  const tHoi = tuViet(`${cauHoi} ${tuKhoaViet.join(" ")}`);
  for (let i = 0; i + 1 < tHoi.length; i++) capHoi.add(`${tHoi[i]} ${tHoi[i + 1]}`);
  // Tên bệnh (từ khoá tiếng Việt) phải có trong TIÊU ĐỀ hoặc trang; không thì trang đó không liên quan.
  const tenBenh = tuKhoaViet.flatMap((k) => tuViet(k)).filter((w) => !TU_DUNG_VI.has(w));
  // Cum ten benh, bo tu chung dau cum ("phac do dieu tri sot xuat huyet" -> "sot xuat huyet").
  const cumBenh = tuKhoaViet
    .map(gonTenBenh)
    .filter((c) => c.length >= 2);
  const diem = PHAC_DO.map((p) => {
    let s = 0;
    for (const w of new Set(tuHoi)) if (p.tu.has(w)) s += (IDF.get(w) || 0) * Math.log(1 + p.tu.get(w)!);
    for (const c of capHoi) if (p.cap.has(c)) s += 2 * (IDF.get(c) || 0);
    const trungTen = tenBenh.filter((w) => p.tuTen.has(w)).length;
    if (tenBenh.length) s *= 1 + trungTen / tenBenh.length;          // uu tien van ban DUNG benh
    if (p.nam) s *= 1 + Math.max(0, Math.min(16, p.nam - 2010)) * 0.015; // cung benh: ban moi hon dung truoc (suy tim 2022 > 2020)
    // Trang phai NOI VE benh do: ten van ban chua du cac tu cua ten benh, hoac trang nhac NGUYEN CUM
    // ten benh it nhat 2 lan. Thu 24/09: hoi sot xuat huyet (thu vien KHONG co phac do nay) ra trang
    // xoan khuan vang da chi vi trang do nhac "sot xuat huyet" mot lan khi chan doan phan biet.
    const vanThuong = p.van.toLowerCase();
    const coTenBenh = !cumBenh.length || cumBenh.some((c) => {
      const tu = c.split(" ");
      if (tu.every((w) => p.tuTen.has(w))) return true;
      let n = 0, i = vanThuong.indexOf(c);
      while (i >= 0 && n < 2) { n++; i = vanThuong.indexOf(c, i + c.length); }
      return n >= 2;
    });
    return { p, s: coTenBenh ? (laTrangPhu(p.van) ? s * 0.15 : s) : 0 };
  }).filter((x) => x.s > 0).sort((a, b) => b.s - a.s);
  if (!diem.length || diem[0].s < 8) return [];                       // qua yeu: coi nhu khong co
  const ra: Omit<TaiLieu, "so">[] = [];
  const vb = new Set<string>();
  const daCo = new Set<string>();                    // cung mot trang dinh kem hai lan -> bo trung
  for (const { p, s } of diem) {
    if (s < diem[0].s * 0.45) break;
    const khoaTrung = p.van.slice(0, 300);
    if (daCo.has(khoaTrung)) continue;
    daCo.add(khoaTrung);
    if (!vb.has(p.ma) && vb.size >= 2) continue;
    vb.add(p.ma);
    // Cửa sổ 1.800 ký tự quanh chỗ dày từ khoá nhất trong trang.
    const van = p.van;
    let tot = 0, viTri = 0;
    for (let i = 0; i < van.length; i += 200) {
      const cua = van.slice(i, i + 1800).toLowerCase();
      const k = [...capHoi].filter((c) => cua.includes(c)).length * 2 + tuHoi.filter((w) => cua.includes(w)).length;
      if (k > tot) { tot = k; viTri = i; }
    }
    // Trang KHOP NHAT: noi them trang ke tiep cua cung van ban — phac do thuong dat "Dai cuong,
    // Chan doan" o trang nay va "Dieu tri" o trang sau (thu 24/09: ngo doc paracetamol bi cat ngang).
    let noiDung = van.slice(viTri, viTri + 1800);
    let trangCuoi = p.trang;
    if (!ra.length) {
      const sau = PHAC_DO.find((x) => x.ma === p.ma && x.trang === p.trang + 1);
      if (sau) {
        noiDung = `${noiDung}
[trang ${p.trang + 1}] ${sau.van.slice(0, 2200)}`;
        trangCuoi = p.trang + 1;
      }
    }
    ra.push({
      nguon: "Phác đồ BYT",
      ten: `${tenGon(p.tieu_de)} — trang ${p.trang}${trangCuoi !== p.trang ? `–${trangCuoi}` : ""}`,
      // Tep PDF truc tiep thi mo dung trang; ban Gia Lai tai qua phien nen tro ve trang van ban.
      url: /\.pdf($|\?)/i.test(p.url_pdf) ? `${p.url_pdf}#page=${p.trang}` : p.url_trang,
      nam: p.nam ? String(p.nam) : undefined,
      loai: `phác đồ Bộ Y tế (toàn văn) · nơi đăng: ${p.noi_dang || "Cục Quản lý Khám, chữa bệnh (kcb.vn)"}`,
      noiDung,
    });
    if (ra.length >= 3) break;
  }
  return ra;
}


/* ------------------------------------------------------------------ NGUỒN QUỐC TẾ BỔ SUNG (24/09/2026)
 * MSD Manual Professional (tiếng Việt + tiếng Anh), NICE (Anh), WHO (fact sheets), CDC (Hoa Kỳ).
 * Server tự tìm và tự đọc trang; mô hình chỉ nhận đoạn văn đã lấy. Mỗi nguồn 1-2 bài, mỗi bài một
 * cửa sổ ~1.600 ký tự quanh chỗ khớp câu hỏi (ưu tiên mục điều trị) — giữ chi phí mỗi câu hỏi vừa phải.
 */
const UA_WEB = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36";

async function layWeb(url: string, giay = 20) {
  const ctl = new AbortController();
  const hen = setTimeout(() => ctl.abort(), giay * 1000);
  try {
    const r = await fetch(url, { signal: ctl.signal, headers: { "User-Agent": UA_WEB, "Accept-Language": "vi,en" } });
    if (!r.ok) throw new Error(`mã ${r.status}`);
    return await r.text();
  } finally {
    clearTimeout(hen);
  }
}

/** Chữ của một trang HTML: đoạn văn, mục liệt kê, tiêu đề mục — bỏ script, menu, chân trang. */
function chuTrang(htmlVan: string) {
  const t = htmlVan.replace(/<(script|style|nav|header|footer|noscript|svg)[^>]*>[\s\S]*?<\/\1>/gi, " ");
  const phan: string[] = [];
  for (const m of t.matchAll(/<(p|li|h2|h3|h4|td)[^>]*>([\s\S]*?)<\/\1>/gi)) {
    const v = boThe(m[2].replace(/&(nbsp|ensp|emsp|thinsp);/g, " ").replace(/&(ndash|mdash);/g, "–")
      .replace(/&(rsquo|lsquo);/g, "'").replace(/&(rdquo|ldquo);/g, '"').replace(/&(copy|reg|trade|shy|zwnj);/g, ""));
    if (/^h/i.test(m[1])) { if (v.length > 3) phan.push(`\n## ${v}\n`); }
    else if (v.length > 25) phan.push(v);
  }
  return phan.join(" ");
}

/** Cửa sổ quanh chỗ khớp nhiều từ khoá nhất; câu hỏi về điều trị thì cộng điểm cho mục điều trị. */
function cuaSo(van: string, tuKhoa: string[], hoiDieuTri: boolean, dai = 1600) {
  const tu = [...new Set(tuKhoa.flatMap((k) => k.toLowerCase().split(/[^\p{L}\p{N}]+/u)).filter((w) => w.length >= 3))];
  // Hỏi điều trị mà trang có mục điều trị riêng thì lấy thẳng mục đó (MSD, WHO, NICE đều có tiêu đề mục).
  // Hỏi ĐỢT CẤP thì ưu tiên mục đợt cấp — thử 24/09: hỏi cơn hen cấp, MSD và NICE trả mục hen MẠN.
  const mucDT = hoiDieuTri ? chonMuc(van, HOI_CAP.test(tuKhoa.join(" ")), tu) : -1;
  if (mucDT >= 0) return van.slice(mucDT, mucDT + dai).trim();
  const thuong = van.toLowerCase();
  let tot = -1, vt = 0;
  for (let i = 0; i < Math.max(1, van.length - 400); i += 250) {
    const c = thuong.slice(i, i + dai);
    if ((c.match(/\.{6,}|…{3,}/g) || []).length > 2) continue;       // trang muc luc
    let k = tu.filter((w) => c.includes(w)).length;
    // Hỏi điều trị: cộng theo mật độ từ điều trị (liều, mg, truyền...), không chỉ theo tên bệnh.
    if (hoiDieuTri) k += 1.5 * Math.min(10, (c.match(/điều trị|xử trí|liều|truyền|bù dịch| mg |ml\/kg|treat|management|dose|recommend|therapy|fluid|khuyến cáo/g) || []).length);
    if (k > tot) { tot = k; vt = i; }
  }
  return van.slice(vt, vt + dai).trim();
}

/** Câu hỏi về đợt cấp / cấp cứu (tiếng Việt hoặc từ khoá PubMed tiếng Anh). */
const HOI_CAP = /(^|[^\p{L}])(cấp|cơn|đợt cấp|cấp cứu|sốc)(?!\p{L})|acute|exacerbation|attack|emergenc/iu;
const MUC_DIEU_TRI = /điều trị|xử trí|treatment|management|pharmacolog|therapy/i;
const MUC_CAP = /đợt cấp|cơn .*cấp|cấp tính|cấp cứu|acute|exacerbation|emergenc|attack|sốc|shock/i;

/** Vị trí mục nên lấy: (đợt cấp + điều trị) > (đợt cấp, nếu hỏi cấp) > (điều trị, mà không phải mạn khi hỏi cấp). */
function chonMuc(van: string, hoiCap: boolean, tuHoi: string[] = []) {
  const muc = [...van.matchAll(/\n## ([^\n]*)\n/g)].map((m) => ({ vt: m.index!, ten: m[1] }));
  // Trong các mục hợp lệ, ưu tiên mục có nhiều chữ trùng câu hỏi (thử 24/09 trên bài PMC: hỏi truyền dịch,
  // "Fluid Management in Severe Dengue" phải thắng "The Course of Dengue Illness—Implications in Management").
  const trung = (m: { ten: string }) => tuHoi.filter((w) => m.ten.toLowerCase().includes(w)).length;
  const tot = <T extends { ten: string }>(ds: T[]) => ds.reduce<T | undefined>((a, m) => (!a || trung(m) > trung(a) ? m : a), undefined);
  const dt = muc.filter((m) => MUC_DIEU_TRI.test(m.ten));
  if (hoiCap) {
    const c = tot(dt.filter((m) => MUC_CAP.test(m.ten)))
      || tot(muc.filter((m) => MUC_CAP.test(m.ten) && !/triệu chứng|symptom|sign|chẩn đoán|diagnos/i.test(m.ten)))
      || tot(dt.filter((m) => !/mạn|chronic|long-term|dài hạn/i.test(m.ten)));
    if (c) return c.vt;
  }
  return tot(dt)?.vt ?? -1;
}

const HOI_DIEU_TRI = /điều trị|xử trí|liều|thuốc|phác đồ|truyền|bù dịch|kháng sinh|treat|manage|dose|fluid/i;

/** MSD Manual Professional qua API tìm kiếm của chính trang (Solr). `ngonNgu` "vi" hoặc "en". */
async function timMSD(tuKhoa: string, ngonNgu: "vi" | "en", cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const tu = tuKhoa.split(/\s+/).filter(Boolean);
  const q = `"${tuKhoa}" (${tu.join(" AND ")}) (${tu.map((w) => `${w}*`).join(" AND ")})`;
  const fq = `languagelistcomputed_sm:${ngonNgu} AND (mmeditioncomputed_s:Professional OR authoreditioncomputed_sm:professional) ` +
    `AND _language:${ngonNgu} AND -excludefrombrand_t:"MSD" AND -contenttype_s:"QuickFacts"`;
  const u = `https://www.msdmanuals.com/professional/api/search/search?q=${encodeURIComponent(q)}&metadata=true` +
    `&language=${ngonNgu}&fq=${encodeURIComponent(fq)}&model=${ngonNgu === "vi" ? "SearchResultVI" : "SearchResult"}&rows=15&start=0`;
  const d = JSON.parse(await layWeb(u));
  const docs: any[] = d?.data?.response?.docs || [];
  // Bai phai co tu khoa trong TIEU DE (tim kiem cua trang tra ca bai nhac thoang qua).
  const tuTen = tu.map((w) => w.toLowerCase());
  // Tieu de phai co TU DAU cua ten benh (thu 24/09: "hen phe quan" ra bai "Gian phe quan" vi trung
  // "phe quan"). Xep: trung nhieu tu hon, roi tieu de dung bang / bat dau bang tu khoa, roi ngan hon.
  const tuCuaTen = (x: any) => String(x.title_t || "").toLowerCase().split(/[^\p{L}\p{N}]+/u);
  const hop = docs.filter((x) => tuTen.length > 0 && tuCuaTen(x).includes(tuTen[0]));
  const k = tuKhoa.toLowerCase();
  const hang = (x: any) => { const t = String(x.title_t || "").toLowerCase();
    const trung = tuTen.filter((w) => tuCuaTen(x).includes(w)).length;
    return -trung * 100000 + (t === k ? 0 : t.startsWith(k) ? 1 : 2) * 1000 + t.length; };
  hop.sort((a, b) => hang(a) - hang(b));
  const ra: Omit<TaiLieu, "so">[] = [];
  for (const x of hop.slice(0, 1)) {
    const duong = String(x.relativeurlcomputed_s || "");
    const url = `https://www.msdmanuals.com${ngonNgu === "vi" ? "/vi" : ""}${duong}`;
    let van = "", trang = "";
    try {
      trang = await layWeb(url);
      van = chuTrang(trang);
    } catch {}
    const hoiDT = HOI_DIEU_TRI.test(cauHoi);
    let noiDung = van ? cuaSo(van, [tuKhoa, cauHoi], hoiDT) : boThe(String(x.summary_t || ""));
    let ten = `${x.title_t}`, urlRa = encodeURI(url);
    // Mục tìm được chỉ vài câu và "được thảo luận ở mục khác" (thử 24/09: "Điều trị cơn hen cấp" 3 câu)
    // -> đi theo liên kết trong mục sang bài riêng, lấy mục phù hợp ở bài đó.
    const tenMuc = noiDung.match(/^## ([^\n]*)/)?.[1];
    const than = noiDung.replace(/^## [^\n]*\n/, "").split("\n## ")[0];
    if (trang && tenMuc && than.length < 700) {
      const vt = trang.indexOf(tenMuc.slice(0, 25));
      if (vt >= 0) {
        const doan = trang.slice(vt, vt + 10000);
        const het = doan.search(/<h[23][\s>]/);
        const lk = (het > 0 ? doan.slice(0, het) : doan).match(/href="(\/(?:vi\/)?professional\/[^"#]+)/)?.[1];
        if (lk && !decodeURI(url).endsWith(decodeURI(lk).replace(/^\/vi/, ""))) {
          try {
            const url2 = new URL(lk, "https://www.msdmanuals.com").href;
            const t2 = await layWeb(url2);
            noiDung = cuaSo(chuTrang(t2), [tuKhoa, cauHoi], hoiDT, 2000);
            ten = boThe(t2.match(/<title>([^<]+)<\/title>/i)?.[1] || ten).replace(/\s+-\s+[^-]*-\s+(MSD|Cẩm nang).*$/i, "");
            urlRa = url2;
          } catch {}
        }
      }
    }
    ra.push({
      nguon: "MSD", ten, url: urlRa, loai: ngonNgu === "vi" ? "Cẩm nang MSD chuyên gia (tiếng Việt)" : "MSD Manual Professional",
      noiDung,
    });
  }
  return ra;
}

/** NICE: trang tìm kiếm trả liên kết tới CHƯƠNG hướng dẫn; đọc chương khớp nhất. */
async function timNICE(tuKhoa: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const t = await layWeb(`https://www.nice.org.uk/search?q=${encodeURIComponent(tuKhoa)}`);
  const tu = tuKhoa.toLowerCase().split(/\s+/).filter((w) => w.length >= 3);
  // Trang kết quả: [tên + tóm tắt kết quả i] <a keyLink> [danh sách chương của kết quả i] [tên kết quả i+1]...
  // Cắt theo keyLink để biết mỗi chương thuộc hướng dẫn nào (tên hướng dẫn nằm ngay TRƯỚC keyLink).
  // split có nhóm bắt: [trước, href keyLink 1, sau 1, href keyLink 2, sau 2, ...]
  const khuc = t.split(/<a href="([^"]+)" class="SearchSections_keyLink[^"]*"/);
  const moTa = new Map<string, string>();
  const chuong: string[] = [];
  for (let i = 1; i < khuc.length; i += 2) {
    const tenKQ = boThe(khuc[i - 1].slice(-1500)).toLowerCase().slice(-400);
    const cua = [khuc[i], ...[...(khuc[i + 1] || "").matchAll(/href="([^"]+)"/g)].map((m) => m[1])];
    for (const c of cua) {
      if (/^\/guidance\/[A-Za-z]{2,3}\d+\/chapter\/[a-z0-9-]+$/.test(c) && !moTa.has(c)) { moTa.set(c, tenKQ); chuong.push(c); }
    }
  }
  // Hướng dẫn cho nhóm đặc biệt (thai kỳ, trẻ em) bị hạ nếu câu hỏi không nhắc tới nhóm đó.
  const hoiThai = /mang thai|thai phụ|thai kỳ|sản phụ|pregnan/i.test(cauHoi);
  const hoiTre = /(^|[^\p{L}])(trẻ|nhi|sơ sinh)(?!\p{L})|child|infant|pediatric|paediatric/iu.test(cauHoi);
  const diem = (c: string) => {
    const mt = moTa.get(c) || "";
    return tu.filter((w) => c.includes(w)).length * 2 + tu.filter((w) => mt.includes(w)).length
      + (HOI_DIEU_TRI.test(cauHoi) && /manag|treat|pharmacolog|recommend/.test(c) ? 2 : 0)
      + (HOI_CAP.test(cauHoi) ? (/acute|exacerbation|emergenc|attack/.test(c) ? 4 : /chronic|long-term/.test(c) ? -2 : 0) : 0)
      + (/\/guidance\/NG/.test(c) ? 3 : 0) - (/\/guidance\/QS/.test(c) ? 2 : 0)
      - (!hoiThai && /pregnan/.test(c + mt) ? 6 : 0) - (!hoiTre && /children|babies|neonat/.test(c + mt) ? 3 : 0)
      - (/context|rationale|terms-used|putting-this|finding-more|update-information|recommendations-for-research/.test(c) ? 5 : 0);
  };
  chuong.sort((a, b) => diem(b) - diem(a));
  const ra: Omit<TaiLieu, "so">[] = [];
  // 2 chương, nhưng không lấy 2 chương cùng một hướng dẫn nếu chương thứ hai là phụ (điểm thấp).
  const chon = chuong.slice(0, 2).filter((c, i) => i === 0 || diem(c) >= 2);
  for (const c of chon) {
    const url = `https://www.nice.org.uk${c}`;
    const trang = await layWeb(url);
    const ten = boThe(trang.match(/<title>([^<]+)<\/title>/i)?.[1] || c).replace(/\s*\|\s*(Guidance|Quality standards)?\s*\|?\s*NICE.*$/, "").replace(/\s*\|\s*(Guidance|Quality standards)\s*$/, "");
    const nam = (trang.match(/Last updated:\s*(?:<[^>]+>|&nbsp;|\s)*\d{1,2} \w+ (\d{4})/)
      || trang.match(/Published:\s*(?:<[^>]+>|&nbsp;|\s)*\d{1,2} \w+ (\d{4})/))?.[1];
    ra.push({ nguon: "NICE", ten, url, nam, loai: "hướng dẫn NICE (Anh)",
              noiDung: cuaSo(chuTrang(trang), [tuKhoa, cauHoi], HOI_DIEU_TRI.test(cauHoi)) });
  }
  return ra;
}

/**
 * WHO — HƯỚNG DẪN LÂM SÀNG (IRIS, kho tài liệu của WHO). Tờ thông tin (fact sheet) viết cho công chúng,
 * không có liều hay ngưỡng. IRIS có toàn văn hướng dẫn và gói TEXT (chữ đã trích sẵn từ PDF), nên
 * không phải tự đọc PDF. Chữ lưu tạm ở data/who-iris/<uuid>.txt, lần hỏi sau không tải lại.
 */
const IRIS = "https://iris.who.int/server/api";

async function vanIRIS(uuid: string) {
  const tep = path.join(process.cwd(), "data", "who-iris", `${uuid}.txt`);
  if (fs.existsSync(tep)) return fs.readFileSync(tep, "utf-8");
  const b = JSON.parse(await layWeb(`${IRIS}/core/items/${uuid}/bundles`));
  const goi = (b?._embedded?.bundles || []).find((x: any) => x.name === "TEXT");
  if (!goi) return "";
  const bs = JSON.parse(await layWeb(goi._links.bitstreams.href));
  const noi = bs?._embedded?.bitstreams?.[0]?._links?.content?.href;
  if (!noi) return "";
  const van = (await layWeb(noi, 60)).replace(/[ \t]+/g, " ");
  fs.mkdirSync(path.dirname(tep), { recursive: true });
  fs.writeFileSync(tep, van);
  return van;
}

/** Hướng dẫn WHO dài hàng trăm trang: lấy đoạn dày CÂU KHUYẾN CÁO ("we recommend", "WHO suggests",
 *  "Recommendation 3") và khớp câu hỏi; trừ điểm bảng chứng cứ GRADE (CI 95%, risk of bias) và mục lục. */
function cuaSoKhuyenCao(van: string, tuKhoa: string[], dai = 2000) {
  const tu = [...new Set(tuKhoa.flatMap((k) => k.toLowerCase().split(/[^\p{L}\p{N}]+/u)).filter((w) => w.length >= 4 && !TU_CHUNG_EN.has(w)))];
  const thuong = van.toLowerCase();
  let tot = -1e9, vt = 0;
  for (let i = 0; i < Math.max(1, van.length - 400); i += 300) {
    const c = thuong.slice(i, i + dai);
    const kc = (c.match(/we recommend|we suggest|who recommends|who suggests|is recommended|are recommended|should (be|receive)|recommendation \d+/g) || []).length;
    const bang = (c.match(/ci 95%|95% ci|risk of bias|imprecision|per 1000|certainty of evidence|\.{6,}/g) || []).length;
    const k = tu.filter((w) => c.includes(w)).length + 3 * Math.min(6, kc) - 3 * bang;
    if (k > tot) { tot = k; vt = i; }
  }
  return van.slice(vt, vt + dai).trim();
}

async function timWHOHuongDan(tuKhoa: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const benh = tuChinhBenh(tuKhoa);
  if (!benh) return [];
  // Hai cách tìm, gộp lại (thử 24/09):
  //  - trong TÊN tài liệu, mới nhất trước: ra hướng dẫn sốt xuất huyết 2025 (tìm toàn văn chỉ ra bản 1976–1999);
  //  - toàn văn theo độ liên quan: ra hướng dẫn tăng huyết áp 2021 (tìm theo tên lại bỏ sót).
  const tim = (q: string, sapXep: boolean) => layWeb(`${IRIS}/discover/search/objects?query=${encodeURIComponent(q)}` +
    `&size=15&dsoType=ITEM${sapXep ? "&sort=dc.date.issued,DESC" : ""}`).then((t) => JSON.parse(t)).catch(() => null);
  const ketQua = await Promise.all([
    tim(`dc.title:${benh} AND dc.title:(guideline* OR handbook OR "clinical management")`, true),
    tim(`${tuKhoa} guideline`, false),
  ]);
  const doiTuong = ketQua.flatMap((d: any) => d?._embedded?.searchResult?._embedded?.objects || []);
  const g = (md: any, k: string) => String(md?.[k]?.[0]?.value || "");
  const goc = benh.slice(0, Math.max(5, benh.length - 2));
  const hoiTre = /(^|[^\p{L}])(trẻ|nhi|sơ sinh)(?!\p{L})|child|infant|pediatric|paediatric/iu.test(cauHoi);
  const daCo = new Set<string>();
  const ung = doiTuong
    .map((o: any) => o?._embedded?.indexableObject).filter((it: any) => it && !daCo.has(it.uuid) && daCo.add(it.uuid))
    .map((it: any) => ({ uuid: it.uuid, handle: it.handle, ten: g(it.metadata, "dc.title"),
                          nam: Number(g(it.metadata, "dc.date.issued").slice(0, 4)), loai: g(it.metadata, "dc.type") }))
    // Hướng dẫn lâm sàng THẬT về đúng bệnh, từ 2012; bỏ tài liệu tập huấn, báo cáo họp, phụ lục, bài báo.
    .filter((x: any) => x.ten.toLowerCase().includes(goc) && /guideline|handbook|clinical management|recommendation/i.test(x.ten)
      && !/training|facilitator|report of|annex|meeting|consultation|protocol|surveillance|outbreak|vaccine|national guidelines|mhealth|be mobile/i.test(x.ten)
      && x.nam >= 2012 && !/journal/i.test(x.loai)
      && (hoiTre || !/child|infant|paediatric|pediatric|neonat|adolescent/i.test(x.ten)))
    .sort((a: any, b: any) => b.nam - a.nam);
  // Bản đầy đủ trước bản tóm tắt; bỏ bản mà chữ trích ra quá ngắn (thử 24/09: bản "summary" của
  // hướng dẫn tăng huyết áp chỉ có 2,5 nghìn ký tự — gần như chỉ có bìa).
  // Đúng chủ đề câu hỏi trước: hỏi điều trị thì tài liệu điều trị hơn tài liệu chẩn đoán/dự phòng
  // (thử 24/09: hỏi điều trị lao ra "module 3: diagnosis").
  const hoiDT = HOI_DIEU_TRI.test(cauHoi), hoiCD = /chẩn đoán|xét nghiệm|diagnos|test/i.test(cauHoi);
  const chuDe = (t: string) => (hoiDT && /treatment|management|care|pharmacolog|therapy/i.test(t) ? 2 : 0)
    - (hoiDT && !hoiCD && /diagnos|prevention|screening/i.test(t) ? 2 : 0) + (hoiCD && /diagnos/i.test(t) ? 2 : 0);
  ung.sort((a: any, b: any) => chuDe(b.ten) - chuDe(a.ten)
    || Number(/summary/i.test(a.ten)) - Number(/summary/i.test(b.ten)) || b.nam - a.nam);
  for (const x of ung.slice(0, 3)) {
    const van = await vanIRIS(x.uuid).catch(() => "");
    if (van.length < 15000) continue;
    return [{ nguon: "WHO", ten: x.ten, url: `https://iris.who.int/handle/${x.handle}`, nam: String(x.nam),
              loai: "hướng dẫn lâm sàng WHO (toàn văn)", noiDung: cuaSoKhuyenCao(van, [tuKhoa, cauHoi], 2600) }];
  }
  return [];
}

/** WHO: danh mục fact sheets (khoảng 240 bài, lưu tạm 1 ngày), khớp theo tên bệnh tiếng Anh. */
let WHO_DS: { luc: number; ds: Array<{ url: string; ten: string }> } | null = null;
async function timWHO(tuKhoa: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  if (!WHO_DS || Date.now() - WHO_DS.luc > 86_400_000) {
    const t = await layWeb("https://www.who.int/news-room/fact-sheets");
    const ds = new Map<string, string>();
    for (const m of t.matchAll(/href="((?:https:\/\/www\.who\.int)?\/news-room\/fact-sheets\/detail\/([a-z0-9-]+))"/g)) {
      ds.set(m[2], m[1].startsWith("http") ? m[1] : `https://www.who.int${m[1]}`);
    }
    WHO_DS = { luc: Date.now(), ds: [...ds].map(([slug, url]) => ({ url, ten: slug.replace(/-/g, " ") })) };
  }
  const tu = tuKhoa.toLowerCase().replace(/'s\b/g, "").split(/[^a-z0-9]+/).filter((w) => w.length >= 3);
  const khop = (ten: string, w: string) => ten.split(" ").some((s) => s.startsWith(w.slice(0, 5)));
  // Tu hiem nhat (it bai WHO co) phai khop: "dengue haemorrhagic fever" khong duoc ra
  // "crimean congo haemorrhagic fever" chi vi trung "haemorrhagic fever".
  const df = (w: string) => WHO_DS!.ds.filter((x) => khop(x.ten, w)).length;
  const coMat = tu.filter((w) => df(w) > 0);
  const tuHiem = coMat.sort((a, b) => df(a) - df(b))[0];
  const hop = WHO_DS.ds
    .map((x) => ({ ...x, k: tu.filter((w) => khop(x.ten, w)).length }))
    .filter((x) => tuHiem && khop(x.ten, tuHiem) && x.k >= Math.max(1, Math.ceil(coMat.length / 2)))
    .sort((a, b) => b.k - a.k);
  const ra: Omit<TaiLieu, "so">[] = [];
  for (const x of hop.slice(0, 1)) {
    const trang = await layWeb(x.url);
    const ten = boThe(trang.match(/<title>([^<]+)<\/title>/i)?.[1] || x.ten).replace(/\s*-\s*World Health Organization.*$/i, "");
    ra.push({ nguon: "WHO", ten, url: x.url, loai: "WHO fact sheet",
              noiDung: cuaSo(chuTrang(trang), [tuKhoa, cauHoi], HOI_DIEU_TRI.test(cauHoi)) });
  }
  // Có hướng dẫn lâm sàng toàn văn thì đặt trước; tờ thông tin rút còn 700 ký tự.
  const hd = await timWHOHuongDan(tuKhoa, cauHoi).catch(() => []);
  if (hd.length) return [...hd, ...ra.map((t) => ({ ...t, noiDung: t.noiDung.slice(0, 700) }))];
  return ra;
}

/** CDC: trang cdc.gov chặn máy tự động (403), nhưng API tìm kiếm của CDC trả sẵn toàn văn đã bóc thẻ. */
async function timCDC(tuKhoa: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const chinh = tuChinhBenh(tuKhoa) || tuKhoa;
  const q = `${chinh}${HOI_DIEU_TRI.test(cauHoi) ? " clinical treatment" : ""}`;
  const d = JSON.parse(await layWeb(
    `https://search.cdc.gov/srch/internet/browse2?q=${encodeURIComponent(q)}&wt=json&start=0&rows=10` +
      `&fl=title,url,strippedContent,lang&df=strippedContent,title&affiliate=cdc-main`));
  const tu = tuKhoa.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 3);
  // Tiêu đề phải có từ đầu của tên bệnh ("dengue" trong "dengue hemorrhagic fever") —
  // chỉ trùng "hemorrhagic fever" thì là bệnh khác.
  const docs: any[] = (d?.response?.docs || []).filter((x: any) => (x.lang || "en") === "en"
    && tu.length > 0 && String(x.title || "").toLowerCase().includes(tuChinhBenh(tuKhoa)));
  // Uu tien trang cho nhan vien y te (/hcp/), bo bang so lieu thong ke.
  const hang = (x: any) => (/\/hcp\//.test(x.url) ? 0 : 1) + (/\/mmwr\/|\/eid\/article|\/pcd\/issues/.test(x.url) ? 3 : 0)
    + (/\/nchs\/data|\/data-research\/|ndc\.services\.cdc\.gov/.test(x.url) ? 5 : 0)
    + (/QuickStats|Prevalence|Surveillance|Data and Statistics/i.test(x.title) ? 5 : 0);
  // Ten bai co chu KHONG lien quan cau hoi (thu 24/09: hoi hen cap ra "Treating Work-related Asthma",
  // "Flu and People with Asthma") -> moi chu la tru 2 diem.
  const CHUNG_CDC = new Set(["about", "treating", "treatment", "clinical", "overview", "for", "healthcare", "providers",
    "provider", "professionals", "guidance", "management", "managing", "of", "and", "the", "to", "in", "on", "symptoms",
    "diagnosis", "testing", "care", "hcp", "signs", "what", "is", "information", "facts", "cdc", "course"]);
  const tuHoi = new Set([...tu, ...cauHoi.toLowerCase().split(/[^a-z0-9]+/)]);
  const chuLa = (x: any) => String(x.title || "").split("|")[0].toLowerCase().split(/[^a-z0-9]+/)
    .filter((w) => w && !CHUNG_CDC.has(w) && !tuHoi.has(w) && !tuHoi.has(w.replace(/s$/, ""))).length;
  const hangGoc = hang;
  const hang2 = (x: any) => hangGoc(x) + 2 * chuLa(x);
  docs.sort((a, b) => hang2(a) - hang2(b));
  // Bai nghien cuu / bao cao dich (MMWR, EID, PCD) khong lay — PubMed da lo phan bai bao.
  return docs.filter((x) => hang2(x) < 3).slice(0, 2).map((x) => {
    const van = Array.isArray(x.strippedContent) ? x.strippedContent[0] : String(x.strippedContent || "");
    return { nguon: "CDC" as const, ten: String(x.title || "").replace(/\s*\|\s*CDC\s*$/, ""), url: x.url, loai: "CDC (Hoa Kỳ)",
             noiDung: cuaSo(van, [tuKhoa, cauHoi], HOI_DIEU_TRI.test(cauHoi)) };
  });
}

/**
 * KIỂM SỐ LIỆU (24/09): mỗi con số (kèm dấu so sánh nếu có) trong một ý của câu trả lời phải có mặt
 * trong chính các tài liệu ý đó trích. Không thấy -> gắn nhãn "chưa thấy trong văn bản gốc" cho bác sĩ
 * kiểm tay. Không sửa câu trả lời, không kết luận là sai (có thể do đổi đơn vị hoặc viết khác).
 */
function chuanSo(van: string) {
  return van
    .toLowerCase()
    .replace(/(greater than or equal to|at least|không dưới|từ)\s+(?=\d)/g, "≥")
    .replace(/(less than or equal to|at most|up to|không quá|tối đa)\s+(?=\d)/g, "≤")
    .replace(/(greater than|more than|higher than|above|over|exceeding|trên|lớn hơn|cao hơn|hơn)\s+(?=\d)/g, ">")
    .replace(/(less than|lower than|below|under|dưới|nhỏ hơn|thấp hơn|chưa tới)\s+(?=\d)/g, "<")
    .replace(/>=/g, "≥").replace(/<=/g, "≤")
    .replace(/(\d)\.(\d{3})(?!\d)/g, "$1$2")          // 1.000 -> 1000 (kiểu Việt)
    .replace(/(\d),(\d{3})(?!\d)/g, "$1$2")           // 1,000 -> 1000 (kiểu Anh)
    .replace(/(\d),(\d)/g, "$1.$2")                   // 0,5 -> 0.5
    .replace(/([<>≤≥])\s+(?=\d)/g, "$1");
}

function soLech(yNoi: string, vanNguon: string): string[] {
  const y = chuanSo(yNoi.replace(/\((lượt|luot)[^)]*\)/gi, "").replace(/\[\d+(,\s*\d+)*\]/g, ""));
  const nguon = chuanSo(vanNguon);
  const lech = new Set<string>();
  for (const m of y.matchAll(/([<>≤≥])?(\d+(?:\.\d+)?)/g)) {
    const [toanBo, dau, so] = m;
    if (!dau && so.length === 1 && Number(so) <= 1) continue;   // bỏ số 0/1 lẻ (đếm "1 lần")
    // số phải có trong nguồn như một số trọn vẹn (không phải phần của số khác)
    const coSo = new RegExp(`(^|[^\\d.])${so.replace(".", "\\.")}(?![\\d])`).test(nguon);
    if (!coSo) { lech.add(toanBo); continue; }
    if (dau) {
      const tuongDuong = dau === "<" || dau === "≤" ? "[<≤]" : "[>≥]";
      if (!new RegExp(`${tuongDuong}${so.replace(".", "\\.")}(?![\\d])`).test(nguon)) lech.add(toanBo);
    }
  }
  return [...lech];
}

const TEN_NGUON: Record<string, string> = {
  MSD: "MSD Manual Professional", NICE: "NICE (Anh)", WHO: "WHO", CDC: "CDC (Hoa Kỳ)", StatPearls: "StatPearls (NCBI)", AAFP: "AAFP (Am Fam Physician)",
  "Phác đồ BYT": "Bộ Y tế · phác đồ lưu tại máy", PubMed: "PubMed", MedlinePlus: "MedlinePlus", FDA: "FDA · DailyMed", "Bộ Y tế": "Bộ Y tế · kcb.vn" };

/** Bước "từ khoá" của tra cứu: một lời gọi mô hình ngoài. Dùng cho route cũ và trợ lý nhiều tác tử. */
export async function datTuKhoaTraCuu(cauHoi: string, ngucanh: string, caKham: string, coCa: boolean): Promise<{ tuKhoa: any; b1: { text: string; model: string; usage: any; seconds: number } }> {
  const b1 = await goiNgoai(
    (coCa
      ? "Bác sĩ hỏi trong lúc khám. Nếu câu hỏi CHỈ hỏi thông tin có sẵn trong ca (ai nói gì, bệnh nhân dùng " +
        "thuốc gì, dị ứng gì, khi nào) thì can_tra_cuu=false. Nếu cần kiến thức y khoa (liều, xử trí, " +
        "tương tác, ngưỡng, chẩn đoán phân biệt, nên hỏi/khám thêm gì, dấu hiệu nguy hiểm cần dặn) thì " +
        "can_tra_cuu=true và đặt từ khoá theo bệnh/thuốc của ca. "
      : "") +
    "Chuyển câu hỏi y khoa thành từ khoá tìm kiếm. Trả về DUY NHẤT JSON: " +
      (coCa ? '{"can_tra_cuu":true,' : "{") +
      '"pubmed":"3-6 từ khoá tiếng Anh, thuật ngữ MeSH nếu có","medlineplus":"1-3 từ tiếng Anh, tên bệnh",' +
      '"benh_en":"tên bệnh CHUẨN Y KHOA tiếng Anh 1-3 từ (vd hypertension, asthma, acute sinusitis, dengue), không dùng tên phổ thông",' +
      '"thuoc":["tên hoạt chất theo FDA Hoa Kỳ (vd acetaminophen, albuterol) của thuốc được hỏi, nếu có"],' +
      '"tieng_viet":"MỘT chuỗi 2-4 từ tiếng Việt có dấu: CHỈ tên bệnh hoặc tên thuốc, không kèm cơn/đợt/cấp/mạn (vd: sốt xuất huyết Dengue, hen phế quản)"}',
    `Câu hỏi: ${cauHoi}${ngucanh ? `\nNgữ cảnh: ${String(ngucanh).slice(0, 500)}` : ""}` +
      (coCa ? `\n\nTrích ca khám:\n${caKham.slice(0, 1500)}` : ""),
    200
  );
  let tuKhoa: any = { pubmed: "", medlineplus: "", thuoc: [], tieng_viet: "" };
  try {
    tuKhoa = { ...tuKhoa, ...JSON.parse(b1.text.match(/\{[\s\S]*\}/)?.[0] || b1.text) };
  } catch {}
  return { tuKhoa, b1 };
}

/** Bước "server tự tìm": chạy song song các nguồn, một nguồn lỗi thì dùng nguồn khác và báo lỗi. */
export async function timTaiLieuTheoTuKhoa(opts: { cauHoi: string; tuKhoa: any; nguon: any }): Promise<{ taiLieu: TaiLieu[]; daTra: Array<{ nguon: string; so: number; ghiChu?: string }>; loiTim: string[]; boLacDe: number; tuKhoaRa: any; kcb: any[]; phacDo: any[]; thuoc: string[]; tenAnh: string }> {
  const { cauHoi, tuKhoa, nguon } = opts;
  const dungPubMed = nguon?.pubmed !== false;
  const dungMedline = nguon?.medlineplus !== false;
  const dungFDA = nguon?.fda !== false;
  const dungKCB = nguon?.kcb !== false;          // gom ca phac do luu tai may va tim tren kcb.vn
  const dungMSD = nguon?.msd !== false;
  const dungNICE = nguon?.nice !== false;
  const dungWHO = nguon?.who !== false;
  const dungCDC = nguon?.cdc !== false;
  const dungSP = nguon?.statpearls !== false;
  const dungAAFP = nguon?.aafp !== false;
  const chiBangChungCao = nguon?.chiBangChungCao === true;
  const thuoc: string[] = Array.isArray(tuKhoa.thuoc) ? tuKhoa.thuoc.filter((x: any) => typeof x === "string") : [];
  // Mo hinh doi khi tra danh sach thay vi chuoi (thu 24/09) — nhan ca hai.
  const tuVietList: string[] = (Array.isArray(tuKhoa.tieng_viet) ? tuKhoa.tieng_viet : [tuKhoa.tieng_viet])
    .filter((x: any) => typeof x === "string" && x.trim());

  // 2. Server tự tìm. Một nguồn lỗi thì vẫn dùng nguồn khác, và báo lỗi ra.
  const loiTim: string[] = [];
  const bat = (ten: string) => (e: any) => (loiTim.push(`${ten}: ${e?.message || e}`), [] as Omit<TaiLieu, "so">[]);
  // Nguon quoc te doc theo ten benh tieng Anh; cua so van ban chon theo cau hoi + tu khoa PubMed.
  const tenPhoThong = String(tuKhoa.medlineplus || tuKhoa.pubmed).split(",")[0].trim();
  const tenAnh = String(tuKhoa.benh_en || "").trim() || TEN_Y_KHOA[tenPhoThong.toLowerCase()] || tenPhoThong;
  const hoiMo = `${cauHoi} ${tuKhoa.pubmed}`;
  // MSD: ban tieng Viet la ban dich cua ban tieng Anh — lay 1 ban, uu tien tieng Viet.
  const timMSDCaHai = async () => {
    const tenViet = gonTenBenh(tuVietList[0] || "");
    const vi = tenViet ? await timMSD(tenViet, "vi", hoiMo).catch(() => []) : [];
    const coMucCap = (r: any[]) => r.length > 0 && MUC_CAP.test(r[0].noiDung.split("\n").find((d: string) => d.startsWith("## ")) || "");
    if (vi.length && !(HOI_CAP.test(hoiMo) && !coMucCap(vi))) return vi;
    // Bản tiếng Việt thiếu mục đợt cấp (bản dịch ngắn hơn bản gốc) — thử bản tiếng Anh.
    const en = await timMSD(tenAnh, "en", hoiMo).catch(() => []);
    return coMucCap(en) || !vi.length ? en : vi;
  };
  const huaSP = dungSP ? timStatPearls(tenAnh, hoiMo).catch(bat("StatPearls")) : Promise.resolve([]);
  const huaAAFP = dungAAFP ? timAAFP(tenAnh, hoiMo).catch(bat("AAFP")) : Promise.resolve([]);
  const huaQuocTe = Promise.all([   // chay song song voi nhom nguon ben duoi
    dungMSD ? timMSDCaHai().catch(bat("MSD")) : Promise.resolve([]),
    dungNICE ? timNICE(tenAnh, hoiMo).catch(bat("NICE")) : Promise.resolve([]),
    dungWHO ? timWHO(tenAnh, hoiMo).catch(bat("WHO")) : Promise.resolve([]),
    dungCDC ? timCDC(tenAnh, hoiMo).catch(bat("CDC")) : Promise.resolve([]),
  ]);
  const [kcb, fda, mp, pmTho] = await Promise.all([
    dungKCB && tuVietList.length ? timKCBRutDan(tuVietList).catch(bat("kcb.vn")) : Promise.resolve([]),
    dungFDA && thuoc.length ? timFDA(thuoc, cauHoi).catch(bat("FDA")) : Promise.resolve([]),
    dungMedline ? timMedlinePlus(tuKhoa.medlineplus || tuKhoa.pubmed).catch(bat("MedlinePlus")) : Promise.resolve([]),
    dungPubMed ? timPubMed(tuKhoa.pubmed, 10, chiBangChungCao) /* 8: bo loc lien quan chat hon (24/09) */.catch(bat("PubMed")) : Promise.resolve([]),
  ]);
  const [msd, nice, who, cdc] = await huaQuocTe;
  const sp = await huaSP;
  const aafp = await huaAAFP;
  const pm = pmTho.filter((t) => lienQuan(t, tuKhoa.pubmed) && lienQuanChat(t, tenAnh, thuoc, cauHoi)).slice(0, 5);
  await lamDayPMC(pm, hoiMo);          // bài có bản mở trên PMC: đọc toàn văn, lấy mục khớp câu hỏi
  const phacDo = dungKCB ? timPhacDo(cauHoi, tuVietList) : [];
  const boLacDe = pmTho.length - pm.length;
  // Thu tu: Bo Y te, nhan thuoc, MedlinePlus, PubMed — nguon trong nuoc va nhan chinh thuc truoc.
  // Thu tu: phac do Bo Y te (toan van), trang kcb.vn, nhan thuoc FDA, MedlinePlus, PubMed.
  // Da co phac do toan van thi chi giu 1 trang kcb.vn (tin, cong van) cho do loang.
  const kcbGiu = phacDo.length ? kcb.slice(0, 1) : kcb;
  // Tran do dai gui mo hinh: ~28.000 ky tu (khoang 8-9 nghin token vao; nang tu 20.000 ngay 24/09 khi
  // them StatPearls va lay 2 bai o NICE/CDC). Qua tran thi tai lieu xep sau chi con 500 ky tu dau.
  let tong = 0;
  const taiLieu: TaiLieu[] = [...phacDo, ...kcbGiu, ...fda, ...msd, ...sp, ...aafp, ...nice, ...who, ...cdc, ...mp, ...pm]
    .map((t, i) => {
      const noiDung = tong > 28000 ? t.noiDung.slice(0, 500) : t.noiDung;
      tong += noiDung.length;
      return { ...t, noiDung, so: i + 1 };
    });
  // Nhat ky "da tra nhung nguon nao" — hien CA nguon khong ra ket qua, de bac si biet.
  const soVbPhacDo = new Set(PHAC_DO.map((x) => x.ma)).size;
  const daTra = [
    dungKCB && { nguon: `Bộ Y tế — ${soVbPhacDo} phác đồ lưu tại máy`, so: phacDo.length },
    dungKCB && { nguon: "Bộ Y tế — tìm trên kcb.vn", so: kcbGiu.length },
    dungFDA && { nguon: "Nhãn thuốc FDA (DailyMed)", so: fda.length, ghiChu: thuoc.length ? "" : "câu hỏi không nhắc thuốc" },
    dungMSD && { nguon: "MSD Manual Professional (bản tiếng Việt, không có thì bản tiếng Anh)", so: msd.length },
    dungSP && { nguon: "StatPearls (NCBI Bookshelf)", so: sp.length },
    dungAAFP && { nguon: "AAFP — American Family Physician", so: aafp.length },
    dungNICE && { nguon: "NICE — Viện Y tế và Chăm sóc Quốc gia Anh", so: nice.length },
    dungWHO && { nguon: "WHO — Tổ chức Y tế Thế giới", so: who.length },
    dungCDC && { nguon: "CDC — Trung tâm Kiểm soát Bệnh tật Hoa Kỳ", so: cdc.length },
    dungMedline && { nguon: "MedlinePlus (Thư viện Y khoa Quốc gia Hoa Kỳ)", so: mp.length },
    dungPubMed && { nguon: "PubMed", so: pm.length,
      ghiChu: [boLacDe ? `bỏ ${boLacDe} bài lạc đề` : "", pm.some((t) => /toàn văn PMC/.test(t.loai || "")) ?
        `${pm.filter((t) => /toàn văn PMC/.test(t.loai || "")).length} bài đọc toàn văn PMC` : ""].filter(Boolean).join(", ") },
  ].filter(Boolean) as Array<{ nguon: string; so: number; ghiChu?: string }>;
  const tuKhoaRa = { pubmed: tuKhoa.pubmed, medlineplus: tuKhoa.medlineplus, thuoc, tieng_viet: tuVietList };
  return { taiLieu, daTra, loiTim, boLacDe, tuKhoaRa, kcb, phacDo, thuoc, tenAnh };
}

/** Bước "mô hình chỉ tóm tắt": một lời gọi mô hình ngoài, rồi server tự ghép nguồn và cảnh báo. Với trợ lý, `caKham` là chuỗi ca đã ẩn danh. */
export async function soanTraLoiCoNguon(opts: { cauHoi: string; caKham: string; coCa: boolean; taiLieu: TaiLieu[]; daTra: Array<{ nguon: string; so: number; ghiChu?: string }>; boLacDe: number; loiTim: string[]; tuKhoaRa: any; kcb: any[]; phacDo: any[]; caAnDanh?: boolean }): Promise<{ answer: string; sources: any[]; searched: any[]; cauTruc: any; removedSources: number; warning: string | null; model: string; usage: any; seconds: number }> {
  const { cauHoi, caKham, coCa, taiLieu, daTra, boLacDe, loiTim, tuKhoaRa, kcb, phacDo, caAnDanh = false } = opts;
  void tuKhoaRa;
  if (!taiLieu.length) {
    return { answer: "Không tìm thấy tài liệu nào ở các nguồn đã chọn cho câu hỏi này.", sources: [], searched: daTra, cauTruc: null, removedSources: boLacDe,
      warning: "KHÔNG có nguồn nào — không có câu trả lời." + (loiTim.length ? ` Lỗi tìm: ${loiTim.join("; ")}` : ""), model: "", usage: {}, seconds: 0 };
  }
  // 3. Mô hình chỉ tóm tắt từ tài liệu đã tìm — dạng PHƯƠNG ÁN, mỗi phương án ghi nguồn.
  const b2 = await goiNgoai(
    "Bạn tổng hợp tài liệu y khoa cho bác sĩ, bằng tiếng Việt. CHỈ dùng các tài liệu được cung cấp; không " +
      "thêm kiến thức ngoài, không tự đặt ra phương án. Liệt kê các PHƯƠNG ÁN / lựa chọn mà tài liệu nêu " +
      "(ví dụ các cách xử trí, các mức liều, các ngưỡng), mỗi phương án ghi số tài liệu dạng [1]. Mỗi phương " +
      "án ghi TẤT CẢ tài liệu nói cùng ý, cả trong nước lẫn nước ngoài, không chỉ tài liệu chi tiết nhất. Nếu tài " +
      "liệu Bộ Y tế Việt Nam và tài liệu nước ngoài nói khác nhau hoặc nước ngoài có thêm điểm (thuốc, liều, " +
      "ngưỡng) thì nêu rõ trong khac_nhau, có số tài liệu. Phần câu hỏi mà tài " +
      "liệu không trả lời được thì nói thẳng. Tài liệu không liên quan thì bỏ qua. Không đưa link. Không " +
      "khẳng định, không kết luận thay bác sĩ. Viết gọn: tối đa 6 phương án, mỗi phương án dưới 70 từ; " +
      "khac_nhau dưới 80 từ. " +
      (coCa
        ? "Có kèm THÔNG TIN CA KHÁM. Ghi thêm: ca_kham = thông tin trong ca liên quan câu hỏi (" + (caAnDanh ? "ca đã ẩn danh, không có số lượt nên không ghi số lượt" : "mỗi ý ghi (lượt n)") + "); " +
          "luu_y_ca = các điểm trong ca có thể làm một phương án không phù hợp hoặc cần chỉnh (dị ứng, thai, tuổi, " +
          "cân nặng, chức năng thận/gan, thuốc đang dùng, bệnh nền), mỗi điểm ghi " + (caAnDanh ? "" : "(lượt n) ") + "và số tài liệu. " +
          "Không chọn phương án thay bác sĩ, không kê đơn. Ca không nói thì để rỗng, không suy đoán. "
        : "") +
      "Nếu bác sĩ hỏi NÊN HỎI/KHÁM THÊM GÌ thì mỗi phương án là MỘT câu hỏi hoặc việc khám nên làm (ten = câu " +
      "hỏi, noi_dung = vì sao, theo tài liệu). an_toan = tối đa 3 điểm an toàn tài liệu nêu (dấu hiệu nguy hiểm, " +
      "chống chỉ định, khi nào chuyển viện), mỗi điểm có số tài liệu; tài liệu không nêu thì để rỗng. hoi_tiep = 3 " +
      "câu hỏi tiếp ngắn bác sĩ có thể hỏi hệ thống. " +
      'Trả về DUY NHẤT JSON: {' + (coCa ? '"ca_kham":"… hoặc rỗng","luu_y_ca":["…"],' : "") +
      '"tom_tat":"1-2 câu","phuong_an":[{"ten":"…","noi_dung":"…","nguon":[số]}],' +
      '"an_toan":[{"noi_dung":"…","nguon":[số]}],"khac_nhau":"… hoặc rỗng","khong_du":"… hoặc rỗng",' +
      '"hoi_tiep":["…","…","…"],"dung":[số các tài liệu thực sự dùng]}',
    `Câu hỏi của bác sĩ: ${cauHoi}\n\n` + (coCa ? `THÔNG TIN CA KHÁM:\n${caKham}\n\n` : "") + `Tài liệu:\n` +
      taiLieu
        .map((t) => `[${t.so}] ${t.nguon}${t.loai ? ` · ${t.loai}` : ""}${t.nam ? ` · ${t.nam}` : ""} — ${t.ten}\n${t.noiDung}`)
        .join("\n\n"),
    2500
  );
  let traLoiMH = b2.text;
  let cauTruc: any = null;
  let dung: number[] = [];
  // JSON bi cat ngang (het tran token — thu 24/09 voi cau hen 6 phuong an): nhat lai tung phuong an
  // day du bang bieu thuc, thay vi hien JSON tho cho bac si.
  const cuuJSON = (t: string) => {
    const chuoi = (ten: string) => t.match(new RegExp(`"${ten}"\\s*:\\s*"((?:[^"\\\\]|\\\\.)*)"`))?.[1];
    const pa = [...t.matchAll(/\{\s*"ten"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"noi_dung"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"nguon"\s*:\s*\[([\d,\s]*)\]/g)]
      .map((m) => ({ ten: m[1], noi_dung: m[2], nguon: m[3].split(",").map(Number).filter(Boolean) }));
    return { ca_kham: chuoi("ca_kham"), tom_tat: chuoi("tom_tat"), phuong_an: pa, an_toan: [], hoi_tiep: [], khac_nhau: chuoi("khac_nhau"),
             khong_du: chuoi("khong_du") || "Câu trả lời của mô hình bị cắt ngang; có thể thiếu phương án cuối.",
             dung: [...new Set(pa.flatMap((x) => x.nguon))] };
  };
  try {
    let j: any;
    try {
      j = JSON.parse(b2.text.match(/\{[\s\S]*\}/)?.[0] || b2.text);
    } catch {
      j = cuuJSON(b2.text);
      if (!j.phuong_an.length && !j.tom_tat) throw new Error("không cứu được JSON");
    }
    dung = (Array.isArray(j.dung) ? j.dung : []).map(Number);
    const so = (ds: any) => (Array.isArray(ds) && ds.length ? " " + ds.map((n: any) => `[${n}]`).join("") : "");
    const pa = (Array.isArray(j.phuong_an) ? j.phuong_an : [])
      .map((x: any, i: number) => `${i + 1}. **${x.ten || "Phương án"}** — ${x.noi_dung || ""}${so(x.nguon)}`);
    const luuY = (Array.isArray(j.luu_y_ca) ? j.luu_y_ca : []).filter((x: any) => typeof x === "string" && x.trim());
    const soHop = (ds: any) => (Array.isArray(ds) ? ds.map(Number).filter((n: number) => taiLieu.some((t) => t.so === n)) : []);
    const anToan = (Array.isArray(j.an_toan) ? j.an_toan : [])
      .map((x: any) => (typeof x === "string" ? { noi_dung: x, nguon: [] } : x))
      .filter((x: any) => x?.noi_dung).map((x: any) => ({ noi_dung: String(x.noi_dung), nguon: soHop(x.nguon) }));
    // Số trong mỗi ý phải có trong chính tài liệu ý đó trích; không thấy thì gắn nhãn cho bác sĩ kiểm.
    const vanCua = (so: number[]) => taiLieu.filter((t) => so.includes(t.so)).map((t) => `${t.ten} ${t.noiDung}`).join("\n");
    const kiem = (y: string, so: number[]) => (so.length ? soLech(y, vanCua(so)) : []);
    cauTruc = {
      ca_kham: j.ca_kham || "", tom_tat: j.tom_tat || "",
      phuong_an: (Array.isArray(j.phuong_an) ? j.phuong_an : [])
        .map((x: any) => ({ ten: String(x.ten || ""), noi_dung: String(x.noi_dung || ""), nguon: soHop(x.nguon) }))
        .map((x: any) => ({ ...x, lech: kiem(`${x.ten} ${x.noi_dung}`, x.nguon) })),
      luu_y_ca: luuY, an_toan: anToan.map((x: any) => ({ ...x, lech: kiem(x.noi_dung, x.nguon) })), khac_nhau: j.khac_nhau || "", khong_du: j.khong_du || "",
      hoi_tiep: (Array.isArray(j.hoi_tiep) ? j.hoi_tiep : []).filter((x: any) => typeof x === "string" && x.trim()).slice(0, 3),
    };
    traLoiMH = [
      j.ca_kham ? `**Trong ca khám:** ${j.ca_kham}` : "",
      j.tom_tat ? `**Tóm tắt:** ${j.tom_tat}` : "",
      pa.length ? `**Các phương án tài liệu nêu:**\n${pa.join("\n")}` : "",
      luuY.length ? `**Lưu ý từ ca khám:**\n${luuY.map((x: string) => `- ${x}`).join("\n")}` : "",
      anToan.length ? `**Lưu ý an toàn:**\n${anToan.map((x: any) => `- ${x.noi_dung}${so(x.nguon)}`).join("\n")}` : "",
      j.khac_nhau ? `**Nguồn trong nước và nước ngoài khác nhau ở:** ${j.khac_nhau}` : "",
      j.khong_du ? `**Tài liệu chưa trả lời được:** ${j.khong_du}` : "",
    ].filter(Boolean).join("\n\n") || traLoiMH;
  } catch {}
  // "Da trich" = danh sach `dung` mo hinh khai; khong co thi moi lay cac so [n] trong cau tra loi.
  // (Truoc 24/09 lay ca hai — tai lieu mo hinh noi "khong lien quan" cung bi tinh la da trich.)
  const soTrongVan = [...traLoiMH.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1]));
  const soTrich = new Set(dung.length ? dung : soTrongVan);
  const soLa = [...new Set([...dung, ...soTrongVan])].filter((n) => !taiLieu.some((t) => t.so === n));
  const NHOM_NGUON: Record<string, string> = { "Phác đồ BYT": "kcb", "Bộ Y tế": "kcb", MSD: "msd", FDA: "fda",
    NICE: "nice", WHO: "who", CDC: "cdc", MedlinePlus: "medlineplus", PubMed: "pubmed", StatPearls: "statpearls", AAFP: "aafp" };
  const nhanNgan = (t: TaiLieu) => {
    if (t.nguon === "Phác đồ BYT") return `Bộ Y tế${t.ten.match(/QĐ\s*\d+/)?.[0] ? ` · ${t.ten.match(/QĐ\s*\d+/)![0]}` : ""}`;
    if (t.nguon === "Bộ Y tế") return "Bộ Y tế · kcb.vn";
    if (t.nguon === "FDA") return "DailyMed (FDA)";
    if (t.nguon === "MSD") return "MSD Manual";
    if (t.nguon === "WHO") return /hướng dẫn/.test(t.loai || "") ? `WHO${t.nam ? ` ${t.nam}` : ""}` : "WHO";
    if (t.nguon === "PubMed") return `${/toàn văn PMC/.test(t.loai || "") ? "PMC" : "PubMed"}${t.nam ? ` · ${t.nam}` : ""}`;
    if (t.nguon === "AAFP") return `AAFP${t.nam ? ` · ${t.nam}` : ""}`;
    return t.nguon;
  };
  const sources = taiLieu.map((t) => ({
    nhan: nhanNgan(t),
    nhom: NHOM_NGUON[t.nguon] || "",
    so: t.so,
    name: `${t.ten}${t.nam ? ` (${t.nam})` : ""}`,
    domain: `${TEN_NGUON[t.nguon] || t.nguon}${t.loai ? ` · ${t.loai}` : ""}`,
    url: t.url,
    cited: soTrich.has(t.so),
  }));
  const hoiBoYTe = /bộ y tế|phác đồ|việt nam|byt/i.test(cauHoi);
  const cu = phacDo.filter((t) => t.nam && Number(t.nam) < 2018).map((t) => t.nam);
  const canhBao = [
    soTrich.size === 0 ? "Câu trả lời không trích tài liệu nào — kiểm lại trước khi dùng." : "",
    soLa.length ? `Câu trả lời trích số không có trong danh sách: ${soLa.join(", ")}.` : "",
    hoiBoYTe && !kcb.length && !phacDo.length ? "Không tìm thấy phác đồ Bộ Y tế cho câu hỏi này (thư viện tại máy và kcb.vn)." : "",
    cu.length ? `Phác đồ Bộ Y tế tìm được ban hành năm ${[...new Set(cu)].join(", ")} — có thể đã có bản mới hơn.` : "",
    hoiBoYTe && kcb.length && !phacDo.length ? "Nguồn Bộ Y tế tìm được chỉ là trang quyết định, công văn hoặc tin chuyên môn — thư viện tại máy chưa có toàn văn phác đồ này. Mở văn bản gốc để đối chiếu." : "",
    loiTim.length ? `Một nguồn tìm bị lỗi: ${loiTim.join("; ")}.` : "",
  ].filter(Boolean).join(" ");
  // Server tu them — KHONG phu thuoc mo hinh: danh sach nguon da tra va loi nhac tham khao.
  const muc = daTra.map((d) => `- ${d.nguon}: ${d.so ? `${d.so} tài liệu` : "không tìm thấy"}${d.ghiChu ? ` (${d.ghiChu})` : ""}`);
  traLoiMH += `\n\n**Nguồn đã tra:**\n${muc.join("\n")}` +
    `\n\n> Chỉ để tham khảo — không phải khẳng định, chẩn đoán hay chỉ định điều trị. ` +
    `Bác sĩ đối chiếu văn bản gốc và tự quyết định.`;
  return {
    answer: traLoiMH,
    sources,
    searched: daTra,
    cauTruc,
    removedSources: boLacDe,
    warning: canhBao || null,
    model: b2.model,
    seconds: b2.seconds,
    usage: { prompt_tokens: b2.usage?.prompt_tokens || 0, completion_tokens: b2.usage?.completion_tokens || 0 },
  };
}

export function dangKyTraCuuRoutes(app: express.Express) {
app.get("/api/pubmed-search", async (req, res) => {
  const q = String(req.query.q || "").trim();
  if (!q) return res.status(400).json({ error: "Thiếu từ khoá" });
  try {
    const nam = Number(req.query.tuNam);
    const bai = await timPubMed(q, 8, req.query.cao === "1", Number.isInteger(nam) && nam > 1900 ? nam : undefined);
    res.json({ results: bai.map((b) => ({ title: b.ten, url: b.url, year: b.nam, type: b.loai, journal: b.tapChi,
                                          abstract: b.noiDung.slice(0, 600) })) });
  } catch (err: any) {
    res.status(502).json({ error: `Không tìm được trên PubMed: ${err?.message || err}` });
  }
});

app.get("/api/phac-do/muc-luc", (_req, res) => {
  const theoMa = new Map<string, { tieu_de: string; nam: number | null; so_trang: number; url: string }>();
  for (const p of PHAC_DO) {
    const cu = theoMa.get(p.ma);
    theoMa.set(p.ma, { tieu_de: p.tieu_de, nam: p.nam, so_trang: Math.max(cu?.so_trang || 0, p.trang), url: p.url_trang });
  }
  res.json({ van_ban: [...theoMa.values()].sort((a, b) => (b.nam || 0) - (a.nam || 0)) });
});

app.post("/api/lookup-official", async (req, res) => {
  try {
    chanNeuChuaChoPhep(req);
    const { question, context, nguon, transcript, draft } = req.body || {};
    // CA KHÁM (ngăn phải, 24/09): hỏi một ô — máy đọc ca khám rồi tự quyết định có cần tra tài liệu không.
    // Hội thoại đánh số lượt để câu trả lời ghi được căn cứ; cắt độ dài để giữ chi phí.
    const soLuotCa = String(transcript || "").split("\n").filter((x) => x.trim())
      .map((x, i) => `[lượt ${i + 1}] ${x.trim()}`).join("\n");
    const coCa = !!(soLuotCa || String(draft || "").trim());
    const caKham = coCa
      ? `Hội thoại:\n${soLuotCa.slice(0, 4000) || "(không có)"}\n\nBản nháp bệnh án:\n${String(draft || "").slice(0, 2000) || "(chưa có)"}`
      : "";
    // Nguồn bác sĩ chọn ở giao diện (nút "Nguồn y khoa"). Không gửi gì thì dùng tất cả.
    const dungPubMed = nguon?.pubmed !== false;
    const dungMedline = nguon?.medlineplus !== false;
    const dungFDA = nguon?.fda !== false;
    const dungKCB = nguon?.kcb !== false;          // gom ca phac do luu tai may va tim tren kcb.vn
    const dungMSD = nguon?.msd !== false;
    const dungNICE = nguon?.nice !== false;
    const dungWHO = nguon?.who !== false;
    const dungCDC = nguon?.cdc !== false;
    const dungSP = nguon?.statpearls !== false;
    const dungAAFP = nguon?.aafp !== false;
    const chiBangChungCao = nguon?.chiBangChungCao === true;
    if (!dungPubMed && !dungMedline && !dungFDA && !dungKCB && !dungMSD && !dungNICE && !dungWHO && !dungCDC && !dungSP && !dungAAFP) {
      return res.status(400).json({ error: "Chưa chọn nguồn tra cứu nào" });
    }
    if (!question) return res.status(400).json({ error: "Thiếu câu hỏi" });

    // 1. Từ khoá. Có ca khám thì gửi kèm đoạn đầu ca (để biết "bệnh nhân này" bị gì) và hỏi thêm
    //    câu hỏi có cần tra tài liệu không — hỏi thông tin sẵn trong ca thì không tra, đỡ tiền.
    const { tuKhoa, b1 } = await datTuKhoaTraCuu(question, context, caKham, coCa);
    if (coCa && (tuKhoa.can_tra_cuu === false || tuKhoa.can_tra_cuu === "false")) {
      const r = await goiNgoai(
        "Bạn trả lời câu hỏi của bác sĩ về MỘT ca khám, CHỈ dựa trên hội thoại và bản nháp được cung cấp. " +
          "Mỗi ý phải ghi số lượt hội thoại làm căn cứ, dạng (lượt 3). Nếu hội thoại không nói thì trả lời " +
          "đúng câu: “Hội thoại không nói điều này.” KHÔNG chẩn đoán, KHÔNG đề xuất thuốc hay điều trị. " +
          "Trả lời ngắn, tiếng Việt.",
        `${caKham}\n\nCâu hỏi: ${question}`,
        700
      );
      const u = (x: any) => x?.usage || {};
      return res.json({
        answer: `${r.text}\n\n**Nguồn:** chỉ hội thoại và bản nháp của ca này — câu hỏi về thông tin trong ca nên không tra tài liệu.` +
          `\n\n> Chỉ để tham khảo — bác sĩ đối chiếu lời thoại gốc và tự quyết định.`,
        sources: [], searched: [], caseOnly: true, model: r.model,
        seconds: Math.round((b1.seconds + r.seconds) * 10) / 10,
        usage: { prompt_tokens: (u(b1).prompt_tokens || 0) + (u(r).prompt_tokens || 0),
                 completion_tokens: (u(b1).completion_tokens || 0) + (u(r).completion_tokens || 0), calls: 2 },
      });
    }
    if (!tuKhoa.pubmed) {
      return res.status(502).json({ error: `Mô hình không trả được từ khoá tìm kiếm: ${b1.text.slice(0, 200)}` });
    }
    const { taiLieu, daTra, loiTim, boLacDe, tuKhoaRa, kcb, phacDo } = await timTaiLieuTheoTuKhoa({ cauHoi: question, tuKhoa, nguon });
    const usage = (x: any) => x?.usage || {};
    if (!taiLieu.length) {
      return res.json({
        answer: "Không tìm thấy tài liệu nào ở các nguồn đã chọn cho câu hỏi này.",
        sources: [], removedSources: boLacDe, searchTerms: tuKhoaRa,
        warning: "KHÔNG có nguồn nào — không có câu trả lời." + (loiTim.length ? ` Lỗi tìm: ${loiTim.join("; ")}` : ""),
        model: b1.model, seconds: b1.seconds,
        usage: { prompt_tokens: usage(b1).prompt_tokens, completion_tokens: usage(b1).completion_tokens },
      });
    }

    const b2 = await soanTraLoiCoNguon({ cauHoi: question, caKham, coCa, taiLieu, daTra, boLacDe, loiTim, tuKhoaRa, kcb, phacDo });
    res.json({
      answer: b2.answer,
      sources: b2.sources,
      searched: b2.searched,
      cauTruc: b2.cauTruc,
      removedSources: b2.removedSources,
      warning: b2.warning,
      searchTerms: tuKhoaRa,
      source: "mo_hinh_ngoai",
      model: b2.model,
      seconds: Math.round((b1.seconds + b2.seconds) * 10) / 10,
      usage: {
        prompt_tokens: (b1.usage?.prompt_tokens || 0) + (b2.usage?.prompt_tokens || 0),
        completion_tokens: (b1.usage?.completion_tokens || 0) + (b2.usage?.completion_tokens || 0),
        calls: 2,
      },
    });
  } catch (err) {
    traLoi(res, err);
  }
});
}
