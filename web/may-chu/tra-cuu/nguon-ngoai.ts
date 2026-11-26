/**
 * Bộ khách truy xuất các nguồn y khoa chính thống (PubMed, StatPearls, PMC, AAFP, MedlinePlus,
 * DailyMed/openFDA, Cục KCB Bộ Y tế, MSD Manual, NICE, WHO IRIS / Fact sheets, CDC).
 */
import fs from "fs/promises";
import path from "path";
import {
  boThe,
  chuTrang,
  cuaSo,
  DUONG_DUNG_FDA,
  HOI_CAP,
  HOI_DIEU_TRI,
  MUC_NHAN,
  type TaiLieu,
  TEN_MY,
  THUOC_HIT,
  TU_CHUNG_EN,
  tuChinhBenh,
  UA_WEB,
} from "./tu-dien";

const NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";
const LOAI_UU_TIEN = "(guideline[pt] OR practice guideline[pt] OR systematic review[pt] OR meta-analysis[pt])";
const BO_BAI_RUT = "NOT (retracted publication[pt] OR retraction of publication[pt])";
const IRIS = "https://iris.who.int/server/api";
const RE_UUID_IRIS = /^[0-9a-f-]{20,64}$/i;

/** Hàng đợi điều tiết tốc độ gọi NCBI eutils (tối đa ~3 req/s khi không có API key). */
let luotNCBI = Promise.resolve();
function choLuotNCBI() {
  const cho = luotNCBI.then(() => new Promise<void>((r) => setTimeout(r, 350)));
  luotNCBI = cho;
  return cho;
}

export async function layChu(url: string, giay = 12): Promise<string> {
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

export async function layWeb(url: string, giay = 20): Promise<string> {
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

export async function timPubMed(tuKhoa: string, soBai = 4, chiBangChungCao = false, tuNam?: number): Promise<Omit<TaiLieu, "so">[]> {
  const locNam = tuNam ? ` AND ("${tuNam}"[dp] : "3000"[dp])` : "";
  const tim = async (term: string) => {
    const j = JSON.parse(
      await layChu(
        `${NCBI}/esearch.fcgi?db=pubmed&retmode=json&sort=relevance&tool=meditrace&retmax=${soBai}` +
          `&term=${encodeURIComponent(term + locNam)}`,
      ),
    );
    return (j?.esearchresult?.idlist || []) as string[];
  };
  const tu = tuKhoa.split(/\s+/).filter(Boolean);
  const cacMuc = Array.from({ length: Math.max(1, tu.length - 1) }, (_, i) => tu.slice(0, tu.length - i).join(" "));
  let ids: string[] = [];
  const gan = tuNam ? "" : ` AND ("${new Date().getFullYear() - 10}"[dp] : "3000"[dp])`;
  for (const q of cacMuc) {
    if ((ids = await tim(`(${q}) AND ${LOAI_UU_TIEN}${gan} ${BO_BAI_RUT}`)).length) break;
  }
  if (!ids.length) {
    for (const q of cacMuc) {
      if ((ids = await tim(`(${q}) AND ${LOAI_UU_TIEN} ${BO_BAI_RUT}`)).length) break;
    }
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
  return ids.map((id) => ra.find((b) => b.url.endsWith(`/${id}/`))).filter(Boolean) as Omit<TaiLieu, "so">[];
}

export async function timMedlinePlus(tuKhoa: string, soBai = 1): Promise<Omit<TaiLieu, "so">[]> {
  const xml = await layChu(`https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&retmax=${soBai}&term=${encodeURIComponent(tuKhoa)}`);
  return [...xml.matchAll(/<document[^>]*url="([^"]+)"[^>]*>([\s\S]*?)<\/document>/g)].map((m) => {
    const truong = (ten: string) => boThe(boThe(m[2].match(new RegExp(`<content name="${ten}">([\\s\\S]*?)</content>`))?.[1] || ""));
    return {
      nguon: "MedlinePlus" as const,
      ten: truong("title") || m[1],
      url: m[1],
      noiDung: truong("FullSummary").slice(0, 1500),
    };
  });
}

export async function timStatPearls(tenBenh: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const ten = tenBenh.toLowerCase().replace(/[^a-z0-9 -]/g, " ").replace(/\s+/g, " ").trim();
  if (!ten) return [];
  const timId = async (t: string) =>
    JSON.parse(
      await layChu(
        `${NCBI}/esearch.fcgi?db=pubmed&retmode=json&tool=meditrace&retmax=40&sort=relevance&term=${encodeURIComponent(`${t}[ti] AND statpearls[book]`)}`,
      ),
    )?.esearchresult?.idlist || [];
  let ids: string[] = await timId(ten);
  if (!ids.length && ten.includes(" ")) ids = await timId(tuChinhBenh(ten));
  if (!ids.length) return [];
  const tom = JSON.parse(await layChu(`${NCBI}/esummary.fcgi?db=pubmed&retmode=json&tool=meditrace&id=${ids.join(",")}`));
  const tuHoi = new Set(cauHoi.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 4));
  const hoiCap = HOI_CAP.test(cauHoi);
  const hoiDB = /trẻ|nhi|thai|child|pediatric|pregnan|neonat/i.test(cauHoi);
  const ung = ids
    .map((id) => {
      const t = boThe(String(tom?.result?.[id]?.title || "")).toLowerCase().replace(/\.$/, "");
      const diem =
        (t === ten ? 6 : 0) +
        (t.startsWith(ten) ? 2 : 0) +
        [...tuHoi].filter((w) => t.includes(w)).length * 2 +
        (hoiCap && /acute|exacerbation|status|emergenc|crisis/.test(t) ? 4 : 0) -
        t.length / 25 -
        Math.max(0, t.split(/\s+/).length - 3) * 1.5 -
        (!hoiDB && /pediatric|children|neonat|pregnan|infant/.test(t) ? 4 : 0) -
        (/secondary|nursing|anesthesia|imaging|evaluation of|history of|embryology|anatomy/.test(t) && !t.startsWith(ten) ? 2 : 0) -
        (/clinical trials?|trial|research|guidelines? history/.test(t) ? 4 : 0) +
        (/essential|primary|management|treatment|overview/.test(t) ? 1 : 0);
      return { id, t, diem };
    })
    .filter((x) => x.t)
    .sort((a, b) => b.diem - a.diem);
  if (!ung.length) return [];
  const xml = await layChu(`${NCBI}/efetch.fcgi?db=pubmed&retmode=xml&tool=meditrace&id=${ung[0].id}`, 20);
  const bai = xml.split("<PubmedBookArticle>")[1] || "";
  const tieuDe = boThe(bai.match(/<ArticleTitle[^>]*>([\s\S]*?)<\/ArticleTitle>/)?.[1] || "");
  const nbk = bai.match(/IdType="bookaccession">(NBK\d+)</)?.[1];
  const tomTat = [...bai.matchAll(/<AbstractText([^>]*)>([\s\S]*?)<\/AbstractText>/g)].map((m) => boThe(m[2])).join(" ");
  const nam = bai.match(/<ContributionDate>[\s\S]*?<Year>(\d{4})/)?.[1] || bai.match(/<PubDate>[\s\S]*?<Year>(\d{4})/)?.[1];
  if (!nbk || !tomTat) return [];
  return [
    {
      nguon: "StatPearls" as const,
      ten: tieuDe,
      url: `https://www.ncbi.nlm.nih.gov/books/${nbk}/`,
      nam,
      loai: "StatPearls (NCBI Bookshelf)",
      noiDung: tomTat.slice(0, 2200),
    },
  ];
}

async function vanPMC(pmc: string): Promise<string> {
  if (!/^PMC\d+$/i.test(pmc)) return "";
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

export async function lamDayPMC(ds: Omit<TaiLieu, "so">[], cauHoi: string, toiDa = 2): Promise<void> {
  const coPMC = ds.filter((t) => t.pmc).slice(0, toiDa);
  await Promise.all(
    coPMC.map(async (t) => {
      try {
        const van = await vanPMC(t.pmc!);
        if (van.length < 3000) return;
        t.noiDung = `(Toàn văn PMC) ${cuaSo(van, [cauHoi], HOI_DIEU_TRI.test(cauHoi), 2000)}`;
        t.url = `https://pmc.ncbi.nlm.nih.gov/articles/${t.pmc}/`;
        t.loai = `${t.loai ? `${t.loai} · ` : ""}toàn văn PMC`;
      } catch {}
    }),
  );
}

export async function timAAFP(tenBenh: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const ten = tenBenh.toLowerCase().replace(/[^a-z0-9 -]/g, " ").replace(/\s+/g, " ").trim();
  if (!ten) return [];
  const gan = `("${new Date().getFullYear() - 10}"[dp] : "3000"[dp])`;
  const timId = async (t: string) =>
    JSON.parse(
      await layChu(
        `${NCBI}/esearch.fcgi?db=pubmed&retmode=json&tool=meditrace&retmax=15&sort=relevance&term=${encodeURIComponent(`${t}[ti] AND "Am Fam Physician"[ta] AND ${gan}`)}`,
      ),
    )?.esearchresult?.idlist || [];
  let ids: string[] = await timId(ten);
  if (!ids.length && ten.includes(" ")) ids = await timId(tuChinhBenh(ten));
  if (!ids.length) return [];
  const tom = JSON.parse(await layChu(`${NCBI}/esummary.fcgi?db=pubmed&retmode=json&tool=meditrace&id=${ids.join(",")}`));
  const tuHoi = new Set(cauHoi.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 4));
  const ung = ids
    .map((id) => {
      const r = tom?.result?.[id] || {};
      const t = boThe(String(r.title || "")).toLowerCase();
      const loaiBai = (r.pubtype || []).join(" ").toLowerCase();
      const diem =
        [...tuHoi].filter((w) => t.includes(w)).length * 2 +
        (t.includes(ten) ? 3 : 0) -
        t.length / 40 -
        (/patient education|handout/.test(loaiBai) ? 20 : 0) -
        (/comment|editorial|letter|news/.test(loaiBai) ? 6 : 0) -
        (/photo quiz|poem|close-ups|curbside|cochrane for clinicians/.test(t) ? 5 : 0);
      return { id, t, nam: String(r.pubdate || "").slice(0, 4), diem };
    })
    .filter((x) => x.t && x.diem > -5)
    .sort((a, b) => b.diem - a.diem);
  for (const x of ung.slice(0, 3)) {
    try {
      const r = await fetch(`https://www.aafp.org/link_out?pmid=${x.id}`, { headers: { "User-Agent": UA_WEB }, redirect: "follow" });
      if (!r.ok) continue;
      const trang = await r.text();
      const van = chuTrang(trang);
      if (/-s\d+(\.html)?$/.test(r.url) || /this handout provides/i.test(van) || van.length < 3000) continue;
      const tieuDe = boThe(trang.match(/<title>([^<]+)<\/title>/i)?.[1] || x.t).replace(/\s*\|\s*AAFP.*$|\s*\|\s*AFP.*$/i, "");
      return [
        {
          nguon: "AAFP" as const,
          ten: tieuDe,
          url: r.url,
          nam: x.nam,
          loai: "American Family Physician",
          noiDung: cuaSo(van, [tenBenh, cauHoi], HOI_DIEU_TRI.test(cauHoi), 2000),
        },
      ];
    } catch {}
  }
  return [];
}

export async function timFDA(tenThuoc: string[], cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
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
    const T = encodeURIComponent(t.toUpperCase());
    const duong = duongCau || (THUOC_HIT.has(t) ? "RESPIRATORY (INHALATION)" : undefined);
    const theoDuong = duong ? `+AND+openfda.route:"${encodeURIComponent(duong)}"` : "";
    const cacTruyVan = [
      ...(theoDuong ? [`openfda.generic_name.exact:"${T}"${theoDuong}`] : []),
      `openfda.generic_name.exact:"${T}"+AND+openfda.product_type:"HUMAN+PRESCRIPTION+DRUG"`,
      `openfda.generic_name.exact:"${T}"`,
      `openfda.generic_name:"${encodeURIComponent(t)}"`,
    ];
    for (const q of cacTruyVan) {
      try {
        r = JSON.parse(await layChu(`https://api.fda.gov/drug/label.json?search=${q}&limit=1`))?.results?.[0];
      } catch {
        r = null;
      }
      if (r && !q.includes(".exact") && /,| AND /.test(String(r.openfda?.generic_name?.[0] || ""))) r = null;
      if (r) break;
    }
    if (!r) continue;
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
      loai:
        `${r.openfda?.product_type?.[0] === "HUMAN PRESCRIPTION DRUG" ? "nhãn thuốc kê đơn" : "nhãn thuốc"}` +
        `${r.openfda?.route?.[0] ? ` · ${String(r.openfda.route[0]).toLowerCase()}` : ""}`,
      noiDung: phan.join("\n").slice(0, 2400),
    });
  }
  return ra;
}

export async function timKCB(tuKhoa: string, soBai = 3): Promise<Omit<TaiLieu, "so">[]> {
  const trang = await layChu(`https://kcb.vn/?keyword=${encodeURIComponent(tuKhoa)}&site=2005611&page=search`);
  const da = new Set<string>();
  const ung: Array<{ url: string; ten: string; diem: number }> = [];
  for (const m of trang.matchAll(/href="(\/(?:cong-van|van-ban|tin-tuc|thong-bao)\/[^"]+\.html)"[^>]*title="([^"]+)"/g)) {
    if (da.has(m[1])) continue;
    da.add(m[1]);
    const ten = boThe(m[2]);
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
      ra.push({
        nguon: "Bộ Y tế",
        ten: u.ten,
        url: u.url,
        loai: u.url.includes("/cong-van/") ? "công văn" : "tin chuyên môn",
        noiDung: doan.join(" ").slice(0, 1500),
      });
    } catch {}
  }
  return ra;
}

export async function timKCBRutDan(ds: string[]): Promise<Omit<TaiLieu, "so">[]> {
  for (const cum of ds.slice(0, 2)) {
    const tu = cum.replace(/^(phác đồ|hướng dẫn|điều trị|chẩn đoán)(\s+(điều trị|chẩn đoán))?\s+/i, "").split(/\s+/);
    for (let n = Math.min(tu.length, 5); n >= Math.min(2, tu.length); n--) {
      const kq = await timKCB(tu.slice(0, n).join(" "));
      if (kq.length) return kq;
    }
  }
  return [];
}

export async function timMSD(tuKhoa: string, ngonNgu: "vi" | "en", cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const tu = tuKhoa.split(/\s+/).filter(Boolean);
  const q = `"${tuKhoa}" (${tu.join(" AND ")}) (${tu.map((w) => `${w}*`).join(" AND ")})`;
  const fq =
    `languagelistcomputed_sm:${ngonNgu} AND (mmeditioncomputed_s:Professional OR authoreditioncomputed_sm:professional) ` +
    `AND _language:${ngonNgu} AND -excludefrombrand_t:"MSD" AND -contenttype_s:"QuickFacts"`;
  const u =
    `https://www.msdmanuals.com/professional/api/search/search?q=${encodeURIComponent(q)}&metadata=true` +
    `&language=${ngonNgu}&fq=${encodeURIComponent(fq)}&model=${ngonNgu === "vi" ? "SearchResultVI" : "SearchResult"}&rows=15&start=0`;
  const d = JSON.parse(await layWeb(u));
  const docs: any[] = d?.data?.response?.docs || [];
  const tuTen = tu.map((w) => w.toLowerCase());
  const tuCuaTen = (x: any) => String(x.title_t || "").toLowerCase().split(/[^\p{L}\p{N}]+/u);
  const hop = docs.filter((x) => tuTen.length > 0 && tuCuaTen(x).includes(tuTen[0]));
  const k = tuKhoa.toLowerCase();
  const hang = (x: any) => {
    const t = String(x.title_t || "").toLowerCase();
    const trung = tuTen.filter((w) => tuCuaTen(x).includes(w)).length;
    return -trung * 100000 + (t === k ? 0 : t.startsWith(k) ? 1 : 2) * 1000 + t.length;
  };
  hop.sort((a, b) => hang(a) - hang(b));
  const ra: Omit<TaiLieu, "so">[] = [];
  for (const x of hop.slice(0, 1)) {
    const duong = String(x.relativeurlcomputed_s || "");
    const url = `https://www.msdmanuals.com${ngonNgu === "vi" ? "/vi" : ""}${duong}`;
    let van = "";
    let trang = "";
    try {
      trang = await layWeb(url);
      van = chuTrang(trang);
    } catch {}
    const hoiDT = HOI_DIEU_TRI.test(cauHoi);
    let noiDung = van ? cuaSo(van, [tuKhoa, cauHoi], hoiDT) : boThe(String(x.summary_t || ""));
    let ten = `${x.title_t}`;
    let urlRa = encodeURI(url);
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
      nguon: "MSD",
      ten,
      url: urlRa,
      loai: ngonNgu === "vi" ? "Cẩm nang MSD chuyên gia (tiếng Việt)" : "MSD Manual Professional",
      noiDung,
    });
  }
  return ra;
}

export async function timNICE(tuKhoa: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const t = await layWeb(`https://www.nice.org.uk/search?q=${encodeURIComponent(tuKhoa)}`);
  const tu = tuKhoa.toLowerCase().split(/\s+/).filter((w) => w.length >= 3);
  const khuc = t.split(/<a href="([^"]+)" class="SearchSections_keyLink[^"]*"/);
  const moTa = new Map<string, string>();
  const chuong: string[] = [];
  for (let i = 1; i < khuc.length; i += 2) {
    const tenKQ = boThe(khuc[i - 1].slice(-1500)).toLowerCase().slice(-400);
    const cua = [khuc[i], ...[...(khuc[i + 1] || "").matchAll(/href="([^"]+)"/g)].map((m) => m[1])];
    for (const c of cua) {
      if (/^\/guidance\/[A-Za-z]{2,3}\d+\/chapter\/[a-z0-9-]+$/.test(c) && !moTa.has(c)) {
        moTa.set(c, tenKQ);
        chuong.push(c);
      }
    }
  }
  const hoiThai = /mang thai|thai phụ|thai kỳ|sản phụ|pregnan/i.test(cauHoi);
  const hoiTre = /(^|[^\p{L}])(trẻ|nhi|sơ sinh)(?!\p{L})|child|infant|pediatric|paediatric/iu.test(cauHoi);
  const diem = (c: string) => {
    const mt = moTa.get(c) || "";
    return (
      tu.filter((w) => c.includes(w)).length * 2 +
      tu.filter((w) => mt.includes(w)).length +
      (HOI_DIEU_TRI.test(cauHoi) && /manag|treat|pharmacolog|recommend/.test(c) ? 2 : 0) +
      (HOI_CAP.test(cauHoi) ? (/acute|exacerbation|emergenc|attack/.test(c) ? 4 : /chronic|long-term/.test(c) ? -2 : 0) : 0) +
      (/\/guidance\/NG/.test(c) ? 3 : 0) -
      (/\/guidance\/QS/.test(c) ? 2 : 0) -
      (!hoiThai && /pregnan/.test(c + mt) ? 6 : 0) -
      (!hoiTre && /children|babies|neonat/.test(c + mt) ? 3 : 0) -
      (/context|rationale|terms-used|putting-this|finding-more|update-information|recommendations-for-research/.test(c) ? 5 : 0)
    );
  };
  chuong.sort((a, b) => diem(b) - diem(a));
  const ra: Omit<TaiLieu, "so">[] = [];
  const chon = chuong.slice(0, 2).filter((c, i) => i === 0 || diem(c) >= 2);
  for (const c of chon) {
    const url = `https://www.nice.org.uk${c}`;
    const trang = await layWeb(url);
    const ten = boThe(trang.match(/<title>([^<]+)<\/title>/i)?.[1] || c)
      .replace(/\s*\|\s*(Guidance|Quality standards)?\s*\|?\s*NICE.*$/, "")
      .replace(/\s*\|\s*(Guidance|Quality standards)\s*$/, "");
    const nam = (
      trang.match(/Last updated:\s*(?:<[^>]+>|&nbsp;|\s)*\d{1,2} \w+ (\d{4})/) ||
      trang.match(/Published:\s*(?:<[^>]+>|&nbsp;|\s)*\d{1,2} \w+ (\d{4})/)
    )?.[1];
    ra.push({
      nguon: "NICE",
      ten,
      url,
      nam,
      loai: "hướng dẫn NICE (Anh)",
      noiDung: cuaSo(chuTrang(trang), [tuKhoa, cauHoi], HOI_DIEU_TRI.test(cauHoi)),
    });
  }
  return ra;
}

/**
 * Tải toàn văn hướng dẫn lâm sàng WHO từ IRIS.
 * Kiểm tra chặt định dạng UUID `/^[0-9a-f-]{20,64}$/i` để chặn tuyệt đối Path Traversal
 * và dùng `fs/promises` bất đồng bộ thay cho sync I/O.
 */
export async function vanIRIS(uuid: string, thuMucGoc?: string): Promise<string> {
  const ma = String(uuid ?? "").trim();
  if (!RE_UUID_IRIS.test(ma)) {
    throw new Error("UUID IRIS không hợp lệ");
  }
  const thuMucIris = path.resolve(thuMucGoc || path.join(process.cwd(), "data", "who-iris"));
  const tep = path.resolve(thuMucIris, `${ma}.txt`);
  if (!tep.startsWith(thuMucIris + path.sep)) {
    throw new Error("Đường dẫn lưu IRIS không hợp lệ");
  }
  try {
    return await fs.readFile(tep, "utf-8");
  } catch {
    // Chưa có bộ đệm trên đĩa -> tải từ IRIS
  }
  const b = JSON.parse(await layWeb(`${IRIS}/core/items/${encodeURIComponent(ma)}/bundles`));
  const goi = (b?._embedded?.bundles || []).find((x: any) => x.name === "TEXT");
  if (!goi) return "";
  const bs = JSON.parse(await layWeb(goi._links.bitstreams.href));
  const noi = bs?._embedded?.bitstreams?.[0]?._links?.content?.href;
  if (!noi) return "";
  const van = (await layWeb(noi, 60)).replace(/[ \t]+/g, " ");
  if (van) {
    await fs.mkdir(thuMucIris, { recursive: true });
    await fs.writeFile(tep, van, "utf-8");
  }
  return van;
}

function cuaSoKhuyenCao(van: string, tuKhoa: string[], dai = 2000): string {
  const tu = [
    ...new Set(
      tuKhoa.flatMap((k) => k.toLowerCase().split(/[^\p{L}\p{N}]+/u)).filter((w) => w.length >= 4 && !TU_CHUNG_EN.has(w)),
    ),
  ];
  const thuong = van.toLowerCase();
  let tot = -1e9;
  let vt = 0;
  for (let i = 0; i < Math.max(1, van.length - 400); i += 300) {
    const c = thuong.slice(i, i + dai);
    const kc = (
      c.match(/we recommend|we suggest|who recommends|who suggests|is recommended|are recommended|should (be|receive)|recommendation \d+/g) ||
      []
    ).length;
    const bang = (c.match(/ci 95%|95% ci|risk of bias|imprecision|per 1000|certainty of evidence|\.{6,}/g) || []).length;
    const k = tu.filter((w) => c.includes(w)).length + 3 * Math.min(6, kc) - 3 * bang;
    if (k > tot) {
      tot = k;
      vt = i;
    }
  }
  return van.slice(vt, vt + dai).trim();
}

export async function timWHOHuongDan(
  tuKhoa: string,
  cauHoi: string,
  taiTrang: (url: string, giay?: number) => Promise<string> = layWeb,
): Promise<Omit<TaiLieu, "so">[]> {
  const benh = tuChinhBenh(tuKhoa);
  if (!benh) return [];
  const tim = (q: string, sapXep: boolean) =>
    taiTrang(`${IRIS}/discover/search/objects?query=${encodeURIComponent(q)}&size=15&dsoType=ITEM${sapXep ? "&sort=dc.date.issued,DESC" : ""}`)
      .then((t) => JSON.parse(t))
      .catch(() => null);
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
    .map((o: any) => o?._embedded?.indexableObject)
    .filter((it: any) => it && RE_UUID_IRIS.test(String(it.uuid || "")) && !daCo.has(it.uuid) && daCo.add(it.uuid))
    .map((it: any) => ({
      uuid: String(it.uuid),
      handle: it.handle,
      ten: g(it.metadata, "dc.title"),
      nam: Number(g(it.metadata, "dc.date.issued").slice(0, 4)),
      loai: g(it.metadata, "dc.type"),
    }))
    .filter(
      (x: any) =>
        x.ten.toLowerCase().includes(goc) &&
        /guideline|handbook|clinical management|recommendation/i.test(x.ten) &&
        !/training|facilitator|report of|annex|meeting|consultation|protocol|surveillance|outbreak|vaccine|national guidelines|mhealth|be mobile/i.test(
          x.ten,
        ) &&
        x.nam >= 2012 &&
        !/journal/i.test(x.loai) &&
        (hoiTre || !/child|infant|paediatric|pediatric|neonat|adolescent/i.test(x.ten)),
    )
    .sort((a: any, b: any) => b.nam - a.nam);
  const hoiDT = HOI_DIEU_TRI.test(cauHoi);
  const hoiCD = /chẩn đoán|xét nghiệm|diagnos|test/i.test(cauHoi);
  const chuDe = (t: string) =>
    (hoiDT && /treatment|management|care|pharmacolog|therapy/i.test(t) ? 2 : 0) -
    (hoiDT && !hoiCD && /diagnos|prevention|screening/i.test(t) ? 2 : 0) +
    (hoiCD && /diagnos/i.test(t) ? 2 : 0);
  ung.sort(
    (a: any, b: any) =>
      chuDe(b.ten) - chuDe(a.ten) || Number(/summary/i.test(a.ten)) - Number(/summary/i.test(b.ten)) || b.nam - a.nam,
  );
  for (const x of ung.slice(0, 3)) {
    const van = await vanIRIS(x.uuid).catch(() => "");
    if (van.length < 15000) continue;
    return [
      {
        nguon: "WHO",
        ten: x.ten,
        url: `https://iris.who.int/handle/${x.handle}`,
        nam: String(x.nam),
        loai: "hướng dẫn lâm sàng WHO (toàn văn)",
        noiDung: cuaSoKhuyenCao(van, [tuKhoa, cauHoi], 2600),
      },
    ];
  }
  return [];
}

let WHO_DS: { luc: number; ds: Array<{ url: string; ten: string }> } | null = null;

export function docBoDemWHO() {
  return WHO_DS;
}

export function datLaiBoDemWHO() {
  WHO_DS = null;
}

export async function timWHO(
  tuKhoa: string,
  cauHoi: string,
  taiTrang: (url: string, giay?: number) => Promise<string> = layWeb,
): Promise<Omit<TaiLieu, "so">[]> {
  if (!WHO_DS || Date.now() - WHO_DS.luc > 86_400_000) {
    try {
      const t = await taiTrang("https://www.who.int/news-room/fact-sheets");
      const ds = new Map<string, string>();
      for (const m of t.matchAll(/href="((?:https:\/\/www\.who\.int)?\/news-room\/fact-sheets\/detail\/([a-z0-9-]+))"/g)) {
        ds.set(m[2], m[1].startsWith("http") ? m[1] : `https://www.who.int${m[1]}`);
      }
      // Không cache mảng rỗng suốt 24 giờ khi tải lỗi hoặc cấu trúc HTML trang WHO đổi
      if (ds.size > 0) {
        WHO_DS = { luc: Date.now(), ds: [...ds].map(([slug, url]) => ({ url, ten: slug.replace(/-/g, " ") })) };
      }
    } catch {
      // Giữ bộ đệm cũ nếu có; nếu chưa có thì để null để lần sau thử lại ngay
    }
  }
  const danhSach = WHO_DS?.ds || [];
  const ra: Omit<TaiLieu, "so">[] = [];
  if (danhSach.length > 0) {
    const tu = tuKhoa.toLowerCase().replace(/'s\b/g, "").split(/[^a-z0-9]+/).filter((w) => w.length >= 3);
    const khop = (ten: string, w: string) => ten.split(" ").some((s) => s.startsWith(w.slice(0, 5)));
    const df = (w: string) => danhSach.filter((x) => khop(x.ten, w)).length;
    const coMat = tu.filter((w) => df(w) > 0);
    const tuHiem = [...coMat].sort((a, b) => df(a) - df(b))[0];
    const hop = danhSach
      .map((x) => ({ ...x, k: tu.filter((w) => khop(x.ten, w)).length }))
      .filter((x) => tuHiem && khop(x.ten, tuHiem) && x.k >= Math.max(1, Math.ceil(coMat.length / 2)))
      .sort((a, b) => b.k - a.k);
    for (const x of hop.slice(0, 1)) {
      const trang = await taiTrang(x.url);
      const ten = boThe(trang.match(/<title>([^<]+)<\/title>/i)?.[1] || x.ten).replace(/\s*-\s*World Health Organization.*$/i, "");
      ra.push({
        nguon: "WHO",
        ten,
        url: x.url,
        loai: "WHO fact sheet",
        noiDung: cuaSo(chuTrang(trang), [tuKhoa, cauHoi], HOI_DIEU_TRI.test(cauHoi)),
      });
    }
  }
  const hd = await timWHOHuongDan(tuKhoa, cauHoi, taiTrang).catch(() => []);
  if (hd.length) return [...hd, ...ra.map((t) => ({ ...t, noiDung: t.noiDung.slice(0, 700) }))];
  return ra;
}

export async function timCDC(tuKhoa: string, cauHoi: string): Promise<Omit<TaiLieu, "so">[]> {
  const chinh = tuChinhBenh(tuKhoa) || tuKhoa;
  const q = `${chinh}${HOI_DIEU_TRI.test(cauHoi) ? " clinical treatment" : ""}`;
  const d = JSON.parse(
    await layWeb(
      `https://search.cdc.gov/srch/internet/browse2?q=${encodeURIComponent(q)}&wt=json&start=0&rows=10` +
        `&fl=title,url,strippedContent,lang&df=strippedContent,title&affiliate=cdc-main`,
    ),
  );
  const tu = tuKhoa.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length >= 3);
  const docs: any[] = (d?.response?.docs || []).filter(
    (x: any) => (x.lang || "en") === "en" && tu.length > 0 && String(x.title || "").toLowerCase().includes(tuChinhBenh(tuKhoa)),
  );
  const hang = (x: any) =>
    (/\/hcp\//.test(x.url) ? 0 : 1) +
    (/\/mmwr\/|\/eid\/article|\/pcd\/issues/.test(x.url) ? 3 : 0) +
    (/\/nchs\/data|\/data-research\/|ndc\.services\.cdc\.gov/.test(x.url) ? 5 : 0) +
    (/QuickStats|Prevalence|Surveillance|Data and Statistics/i.test(x.title) ? 5 : 0);
  const CHUNG_CDC = new Set([
    "about", "treating", "treatment", "clinical", "overview", "for", "healthcare", "providers",
    "provider", "professionals", "guidance", "management", "managing", "of", "and", "the", "to", "in", "on", "symptoms",
    "diagnosis", "testing", "care", "hcp", "signs", "what", "is", "information", "facts", "cdc", "course",
  ]);
  const tuHoi = new Set([...tu, ...cauHoi.toLowerCase().split(/[^a-z0-9]+/)]);
  const chuLa = (x: any) =>
    String(x.title || "")
      .split("|")[0]
      .toLowerCase()
      .split(/[^a-z0-9]+/)
      .filter((w) => w && !CHUNG_CDC.has(w) && !tuHoi.has(w) && !tuHoi.has(w.replace(/s$/, ""))).length;
  const hang2 = (x: any) => hang(x) + 2 * chuLa(x);
  docs.sort((a, b) => hang2(a) - hang2(b));
  return docs
    .filter((x) => hang2(x) < 3)
    .slice(0, 2)
    .map((x) => {
      const van = Array.isArray(x.strippedContent) ? x.strippedContent[0] : String(x.strippedContent || "");
      return {
        nguon: "CDC" as const,
        ten: String(x.title || "").replace(/\s*\|\s*CDC\s*$/, ""),
        url: x.url,
        loai: "CDC (Hoa Kỳ)",
        noiDung: cuaSo(van, [tuKhoa, cauHoi], HOI_DIEU_TRI.test(cauHoi)),
      };
    });
}
